"""The tagging run: scan -> preview frames -> tag -> catalog -> manifest.

Reads the project folder, writes only to the library. Never moves originals.
"""

import shutil
import tempfile
from datetime import datetime
from pathlib import Path

from . import media, tagging
from .library import SKIPPED, TAGGED

MAX_FAILURES_IN_A_ROW = 5


def needs_tagging(entry, tagger_name, rescan):
    if entry is None or entry.get("status") != TAGGED:
        return True
    if entry.get("edited"):
        return False  # manual corrections are never overwritten
    if entry.get("tagger") == "demo":
        return tagger_name == "ai" or rescan
    return rescan and tagger_name == "ai"  # demo runs never replace real AI tags


def plan(library, tagger_name, rescan=False):
    """The clips a run would tag, as (path, clip_id) pairs, plus the total found."""
    candidates = {}
    for path in media.scan(library.root):
        candidates[media.clip_id(path, library.root)] = path
    for entry in library.clips():
        if entry.get("sorted_path") and library.current_path(entry).exists():
            candidates[entry["id"]] = library.current_path(entry)
    todo = [(path, cid) for cid, path in candidates.items()
            if needs_tagging(library.entries.get(cid), tagger_name, rescan)]
    todo.sort()
    return todo, len(candidates)


def run_tagging(library, tagger, preset, buckets, limit=None, rescan=False,
                log=print, should_stop=lambda: False, on_progress=lambda done, total: None):
    todo, found = plan(library, tagger.name, rescan)
    already = found - len(todo)
    if limit:
        todo = todo[:limit]
    log(f"Project: {library.root.name}")
    log(f"{found} clips found, {already} already tagged, {len(todo)} to tag now.")
    summary = {"found": found, "tagged": 0, "skipped": 0, "stopped": False, "error": None}
    workdir = Path(tempfile.mkdtemp(prefix=".frames-", dir=library.dir))
    failures_in_a_row = 0
    try:
        for index, (path, cid) in enumerate(todo, 1):
            if should_stop():
                summary["stopped"] = True
                log("Stopped. Finished clips are saved; run again to continue.")
                break
            previous = library.entries.get(cid) or {}
            base = {
                "id": cid, "file": path.name,
                "rel_path": previous.get("rel_path") or path.relative_to(library.root).as_posix(),
                "source_folder": previous.get("source_folder") or path.parent.name,
            }
            if previous.get("sorted_path"):
                base["sorted_path"] = previous["sorted_path"]
            note = None
            meta = media.probe(path)
            frames = media.grab_frames(path, meta["duration"], workdir)
            if not frames:
                note = "unreadable or unsupported format"
            else:
                try:
                    tag = tagger.tag(path.name, frames, buckets, preset)
                except tagging.FatalTaggingError as e:
                    summary["error"] = str(e)
                    log(f"Stopped: {e}")
                    break
                except tagging.TaggingError as e:
                    note = str(e)
            if note:
                library.put({**base, **meta, "status": SKIPPED, "note": note})
                summary["skipped"] += 1
                log(f"! {path.name}: skipped ({note})")
                failures_in_a_row += 1
                if tagger.name == "ai" and failures_in_a_row >= MAX_FAILURES_IN_A_ROW:
                    summary["error"] = (f"{MAX_FAILURES_IN_A_ROW} clips in a row could not be "
                                        "tagged, so the run was stopped.")
                    log(f"Stopped: {summary['error']}")
                    break
            else:
                failures_in_a_row = 0
                library.thumb_path(cid).write_bytes(frames[min(1, len(frames) - 1)])
                library.put({**base, **meta, **tag, "status": TAGGED, "tagger": tagger.name,
                             "tagged_at": datetime.now().isoformat(timespec="seconds")})
                summary["tagged"] += 1
                log(f"[{index}/{len(todo)}] {path.name} -> {tag['bucket']} "
                    f"(keeper {tag['keeper']}) {tag['description'][:60]}")
            on_progress(index, len(todo))
    finally:
        shutil.rmtree(workdir, ignore_errors=True)
        library.compact()
        library.write_manifest()
    log(f"Done. {len(library.clips())} clips in the library"
        + (f", {len(library.skipped())} skipped (see the manifest)." if library.skipped() else "."))
    log("Originals were not moved or changed.")
    return summary
