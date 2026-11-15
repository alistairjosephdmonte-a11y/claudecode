"""The four acceptance checks from HANDOVER.md, plus filing and undo."""

import csv
import os
import signal
import subprocess
import sys
import time
import unittest
from pathlib import Path
from unittest import mock

from footage_studio import filing, pipeline, presets, tagging
from footage_studio.library import Library
from tests.helpers import ProjectCase, snapshot

BUCKETS = presets.PRESETS["wedding"]
PACKAGE_DIR = Path(__file__).resolve().parents[1]


def demo_run(root, **kwargs):
    library = Library(root)
    summary = pipeline.run_tagging(library, tagging.DemoTagger(), "wedding", BUCKETS,
                                   log=lambda m: None, **kwargs)
    return library, summary


class CountingTagger(tagging.DemoTagger):
    def __init__(self):
        self.calls = []

    def tag(self, clip_name, frames, buckets, preset):
        self.calls.append(clip_name)
        return super().tag(clip_name, frames, buckets, preset)


class DemoEndToEnd(ProjectCase):
    def test_demo_run_builds_library_and_manifest_without_network(self):
        with mock.patch("urllib.request.urlopen", side_effect=AssertionError("network used")), \
                mock.patch("socket.socket.connect", side_effect=AssertionError("network used")):
            library, summary = demo_run(self.root)
        self.assertEqual(summary["tagged"], 9)
        self.assertEqual(summary["skipped"], 1)
        for clip in library.clips():
            self.assertIn(clip["bucket"], BUCKETS)
            self.assertIn(clip["setting"], presets.SETTINGS)
            self.assertIn(clip["keeper"], range(1, 6))
            self.assertTrue(clip["description"])
            self.assertTrue(library.thumb_path(clip["id"]).read_bytes().startswith(b"\xff\xd8"))
        with open(library.manifest_path, encoding="utf-8-sig", newline="") as f:
            rows = list(csv.DictReader(f))
        self.assertEqual(len(rows), 10)
        broken = [r for r in rows if r["file"] == "BROKEN_CLIP.mp4"]
        self.assertTrue(broken[0]["note"].startswith("SKIPPED:"))

    def test_unreadable_clip_is_skipped_not_fatal(self):
        library, summary = demo_run(self.root)
        self.assertIsNone(summary["error"])
        self.assertEqual([s["file"] for s in library.skipped()], ["BROKEN_CLIP.mp4"])


class NonDestructive(ProjectCase):
    def test_run_without_filing_leaves_project_byte_identical(self):
        before = snapshot(self.root)
        demo_run(self.root)
        self.assertEqual(snapshot(self.root), before)

    def test_library_lives_outside_the_project_folder(self):
        library, _ = demo_run(self.root)
        self.assertNotIn(self.root, library.dir.parents)
        self.assertIn(self.home, library.dir.parents)


class Resume(ProjectCase):
    def test_stopped_run_resumes_without_retagging(self):
        first = CountingTagger()
        library = Library(self.root)
        pipeline.run_tagging(library, first, "wedding", BUCKETS, log=lambda m: None,
                             should_stop=lambda: len(first.calls) >= 3)
        self.assertEqual(len(first.calls), 3)
        second = CountingTagger()
        library = Library(self.root)
        pipeline.run_tagging(library, second, "wedding", BUCKETS, log=lambda m: None)
        self.assertEqual(len(second.calls), 6)
        self.assertFalse(set(first.calls) & set(second.calls))
        self.assertEqual(len(library.clips()), 9)

    def test_forced_quit_mid_run_resumes_without_retagging(self):
        env = dict(os.environ, PYTHONPATH=str(PACKAGE_DIR))
        command = [sys.executable, "-m", "footage_studio", "tag", str(self.root), "--demo"]
        process = subprocess.Popen(command, env=env, stdout=subprocess.DEVNULL)
        journal = Library(self.root)._journal
        deadline = time.time() + 60
        while time.time() < deadline and process.poll() is None:
            if journal.exists() and journal.read_text().count("\n") >= 3:
                break
            time.sleep(0.01)
        self.assertIsNone(process.poll(), "run finished before it could be killed")
        process.send_signal(signal.SIGKILL)
        process.wait()

        survivors = {c["id"]: c["tagged_at"] for c in Library(self.root).clips()}
        self.assertGreaterEqual(len(survivors), 2)
        self.assertLess(len(survivors), 9)
        time.sleep(1.1)  # so a re-tag would show up as a different timestamp
        output = subprocess.run(command, env=env, capture_output=True, text=True, check=True).stdout
        # 9 clips plus the broken one, which is always retried
        self.assertIn(f"{10 - len(survivors)} to tag now", output)
        library = Library(self.root)
        self.assertEqual(len(library.clips()), 9)
        for clip_id, tagged_at in survivors.items():
            self.assertEqual(library.entries[clip_id]["tagged_at"], tagged_at)

    def test_cut_off_journal_line_is_ignored(self):
        library, _ = demo_run(self.root)
        with open(library._journal, "a", encoding="utf-8") as f:
            f.write('{"id": "abc", "status": "tag')
        self.assertEqual(len(Library(self.root).clips()), 9)


class CachedTags(ProjectCase):
    def test_rerun_reuses_tags_and_rescan_replaces_them(self):
        demo_run(self.root)
        again = CountingTagger()
        library = Library(self.root)
        pipeline.run_tagging(library, again, "wedding", BUCKETS, log=lambda m: None)
        self.assertEqual(again.calls, [])
        pipeline.run_tagging(library, again, "wedding", BUCKETS, rescan=True, log=lambda m: None)
        self.assertEqual(len(again.calls), 9)

    def test_manual_corrections_survive_a_rescan(self):
        library, _ = demo_run(self.root)
        clip = library.clips()[0]
        library.put({**clip, "description": "bride laughing", "edited": True})
        pipeline.run_tagging(library, tagging.DemoTagger(), "wedding", BUCKETS, rescan=True,
                             log=lambda m: None)
        self.assertEqual(library.entries[clip["id"]]["description"], "bride laughing")

    def test_real_tagging_replaces_demo_tags_but_demo_never_replaces_real(self):
        library, _ = demo_run(self.root)
        self.assertEqual(len(pipeline.plan(library, "ai")[0]), 10)
        for clip in library.clips():
            library.put({**clip, "tagger": "ai"})
        todo, _ = pipeline.plan(library, "demo", rescan=True)
        self.assertEqual([p.name for p, _ in todo], ["BROKEN_CLIP.mp4"])


class FilingAndUndo(ProjectCase):
    def test_filing_keeps_card_folders_and_sidecars_then_undo_restores_everything(self):
        before = snapshot(self.root)
        library, _ = demo_run(self.root)
        self.assertEqual(filing.file_clips(library, log=lambda m: None), 9)

        by_file = {c["file"]: c for c in library.clips()}
        nested = by_file["CLIP_0002.mov"]
        self.assertEqual(nested["sorted_path"],
                         f"Sorted/{nested['bucket']}/B_CAM/DCIM/100MEDIA/CLIP_0002.mov")
        first = by_file["CLIP_0001.mp4"]
        self.assertTrue((self.root / first["sorted_path"]).with_suffix(".xmp").is_file())
        self.assertFalse((self.root / "A_CAM" / "CLIP_0001.xmp").exists())
        self.assertTrue((self.root / "A_CAM" / "BROKEN_CLIP.mp4").exists())
        self.assertNotEqual(snapshot(self.root), before)

        result = filing.undo(Library(self.root), log=lambda m: None)
        self.assertEqual(result, {"restored": 10, "problems": 0})
        self.assertEqual(snapshot(self.root), before)
        library = Library(self.root)
        self.assertFalse(any(c.get("sorted_path") for c in library.clips()))
        self.assertNotIn("filed into Sorted", library.manifest_path.read_text(encoding="utf-8-sig"))

    def test_filed_clips_are_not_seen_as_new_clips(self):
        library, _ = demo_run(self.root)
        filing.file_clips(library, log=lambda m: None)
        tagger = CountingTagger()
        pipeline.run_tagging(Library(self.root), tagger, "wedding", BUCKETS, log=lambda m: None)
        self.assertEqual(tagger.calls, [])

    def test_undo_after_a_crash_mid_filing(self):
        before = snapshot(self.root)
        library, _ = demo_run(self.root)
        real_rename, moved = os.rename, []

        def crashing_rename(src, dest):
            if len(moved) == 4:
                raise KeyboardInterrupt
            moved.append(src)
            real_rename(src, dest)

        with mock.patch("os.rename", crashing_rename):
            with self.assertRaises(KeyboardInterrupt):
                filing.file_clips(library, log=lambda m: None)
        filing.undo(Library(self.root), log=lambda m: None)
        self.assertEqual(snapshot(self.root), before)

    def test_filing_refuses_a_sorted_folder_it_did_not_create(self):
        library, _ = demo_run(self.root)
        (self.root / "Sorted").mkdir()
        before = snapshot(self.root)
        with self.assertRaises(filing.FilingError):
            filing.file_clips(library, log=lambda m: None)
        self.assertEqual(snapshot(self.root), before)

    def test_undo_never_overwrites_a_file_in_the_way(self):
        library, _ = demo_run(self.root)
        filing.file_clips(library, log=lambda m: None)
        blocker = self.root / "DRONE" / "CLIP_0003.mkv"
        blocker.write_bytes(b"someone put this here")
        result = filing.undo(Library(self.root), log=lambda m: None)
        self.assertEqual(result["problems"], 1)
        self.assertEqual(blocker.read_bytes(), b"someone put this here")
        library = Library(self.root)
        still = [c for c in library.clips() if c.get("sorted_path")]
        self.assertEqual([c["file"] for c in still], ["CLIP_0003.mkv"])
        self.assertTrue((self.root / still[0]["sorted_path"]).is_file())


if __name__ == "__main__":
    unittest.main()
