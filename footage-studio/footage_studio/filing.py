"""Opt-in filing of clips into Sorted/<bucket>/<original folders>/, and undo.

This is the only code that changes the project folder. Files are renamed in
place (never copied or re-encoded). Every action is written to the moves log
BEFORE it happens, so undo works even after a crash mid-filing. The log lives
inside Sorted/ so it travels with the files, and uses paths relative to the
project so it survives the drive being mounted somewhere else.
"""

import json
import os
import re
from pathlib import Path

from . import media


class FilingError(Exception):
    pass


def safe_folder_name(bucket):
    return re.sub(r'[\\/:*?"<>|]', "-", bucket).strip(" .") or "other"


def _log_path(root):
    return root / media.SORTED_DIR / media.MOVES_LOG


def _append(root, record):
    with open(_log_path(root), "a", encoding="utf-8") as f:
        f.write(json.dumps(record) + "\n")
        f.flush()
        os.fsync(f.fileno())


def _make_dirs(root, target):
    """Create target and any missing parents, logging each so undo removes them."""
    missing = []
    folder = target
    while not folder.exists():
        missing.append(folder)
        folder = folder.parent
    for folder in reversed(missing):
        _append(root, {"op": "mkdir", "path": folder.relative_to(root).as_posix()})
        folder.mkdir()


def _free_name(folder, name):
    dest, n = folder / name, 1
    while dest.exists():
        dest = folder / f"{Path(name).stem}_{n}{Path(name).suffix}"
        n += 1
    return dest


def has_filing(root):
    return _log_path(root).is_file()


def file_clips(library, log=print):
    """Move every tagged, not-yet-filed clip (with its sidecars) into Sorted/."""
    root = library.root
    sorted_dir = root / media.SORTED_DIR
    todo = [e for e in library.clips()
            if not e.get("sorted_path") and (root / e["rel_path"]).is_file()]
    if not todo:
        log("Nothing to file.")
        return 0
    if sorted_dir.exists() and not has_filing(root):
        raise FilingError(
            f"This project already has a folder named {media.SORTED_DIR} that Footage Studio "
            "did not create. Rename it first, then file again. Nothing was moved.")
    sorted_dir.mkdir(exist_ok=True)
    if not has_filing(root):
        _append(root, {"op": "start"})
    filed = 0
    for entry in sorted(todo, key=lambda e: e["rel_path"]):
        source = root / entry["rel_path"]
        dest_dir = sorted_dir / safe_folder_name(entry["bucket"]) / Path(entry["rel_path"]).parent
        _make_dirs(root, dest_dir)
        sidecars = sorted(
            s for s in source.parent.iterdir()
            if s.is_file() and s.stem == source.stem and s.suffix.lower() in media.SIDECAR_EXTS)
        video_dest = None
        for src in [source] + sidecars:
            dest = _free_name(dest_dir, src.name)
            _append(root, {"op": "move", "from": src.relative_to(root).as_posix(),
                           "to": dest.relative_to(root).as_posix()})
            os.rename(src, dest)
            video_dest = video_dest or dest
        library.put({**entry, "sorted_path": video_dest.relative_to(root).as_posix()})
        filed += 1
    library.compact()
    library.write_manifest()
    log(f"Filed {filed} clips into {media.SORTED_DIR}/. Undo puts every file back.")
    return filed


def undo(library, log=print):
    """Put every filed file back where it came from and repair the library."""
    root = library.root
    if not has_filing(root):
        log("Nothing has been filed, so there is nothing to undo.")
        return {"restored": 0, "problems": 0}
    records = []
    for line in _log_path(root).read_text(encoding="utf-8").splitlines():
        try:
            records.append(json.loads(line))
        except ValueError:
            continue
    restored, kept = 0, []
    for record in reversed(records):
        if record.get("op") == "move":
            src, dest = root / record["from"], root / record["to"]
            if not dest.exists():
                continue  # logged but never happened, or already undone
            if src.exists():
                kept.append(record)
                log(f"! Could not restore {record['from']}: something else is there now.")
                continue
            src.parent.mkdir(parents=True, exist_ok=True)
            os.rename(dest, src)
            restored += 1
        elif record.get("op") == "mkdir":
            try:
                (root / record["path"]).rmdir()
            except OSError:
                pass  # not empty: someone put other files there, so leave it
    if kept:
        body = "".join(json.dumps(r) + "\n" for r in [{"op": "start"}] + list(reversed(kept)))
        _log_path(root).write_text(body, encoding="utf-8")
    else:
        _log_path(root).unlink()
        try:
            (root / media.SORTED_DIR).rmdir()
        except OSError:
            pass  # not empty: someone put other files there, so leave it
    still_filed = {r["to"] for r in kept}
    for entry in library.clips():
        if entry.get("sorted_path") and entry["sorted_path"] not in still_filed:
            library.put({k: v for k, v in entry.items() if k != "sorted_path"})
    library.compact()
    library.write_manifest()
    log(f"Undone: {restored} files moved back to where they came from.")
    return {"restored": restored, "problems": len(kept)}
