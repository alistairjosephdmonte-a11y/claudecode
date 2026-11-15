"""The clip library for one project.

The library lives in Footage Studio's own data folder, NOT inside the project
folder, so that tagging leaves the project byte-identical. The catalog is an
append-only journal: every finished clip is flushed to disk immediately, so a
forced quit never loses or repeats finished work.
"""

import csv
import hashlib
import json
import os
import re
import shutil
import sys
import threading
from pathlib import Path

from . import presets

TAGGED = "tagged"
SKIPPED = "skipped"
MANIFEST_COLUMNS = [
    "file", "original_path", "current_path", "source_folder", "date", "duration_s",
    "resolution", "bucket", "setting", "keeper", "description", "tagged_by",
    "corrected", "note",
]


def app_home():
    override = os.environ.get("FOOTAGE_STUDIO_HOME")
    if override:
        return Path(override)
    if sys.platform == "darwin":
        return Path.home() / "Library" / "Application Support" / "Footage Studio"
    if os.name == "nt":
        return Path(os.environ.get("APPDATA", Path.home())) / "Footage Studio"
    return Path(os.environ.get("XDG_DATA_HOME", Path.home() / ".local" / "share")) / "footage-studio"


def _library_dir(root):
    digest = hashlib.sha1(str(root).encode()).hexdigest()[:10]
    slug = re.sub(r"[^A-Za-z0-9]+", "-", root.name).strip("-")[:40] or "project"
    return app_home() / "projects" / f"{slug}-{digest}"


def _spreadsheet_safe(value):
    """Stop spreadsheet apps treating a description as a formula."""
    text = "" if value is None else str(value)
    return "'" + text if text[:1] in ("=", "+", "-", "@") else text


class Library:
    def __init__(self, root):
        self.root = Path(root).expanduser().resolve()
        if not self.root.is_dir():
            raise ValueError(f"Not a folder: {self.root}")
        self.dir = _library_dir(self.root)
        self.thumbs = self.dir / "thumbs"
        self.thumbs.mkdir(parents=True, exist_ok=True)
        self._journal = self.dir / "catalog.jsonl"
        self._lock = threading.RLock()
        self.entries = {}
        self._load()
        self.settings = self._load_settings()
        for stale in self.dir.glob(".frames-*"):
            shutil.rmtree(stale, ignore_errors=True)

    # ------------------------------------------------------------ settings

    def _load_settings(self):
        settings = {"root": str(self.root), "name": self.root.name,
                    "preset": presets.DEFAULT_PRESET,
                    "buckets": list(presets.PRESETS[presets.DEFAULT_PRESET])}
        try:
            saved = json.loads((self.dir / "project.json").read_text(encoding="utf-8"))
            if saved.get("preset") in presets.PRESETS:
                settings["preset"] = saved["preset"]
            if saved.get("buckets"):
                settings["buckets"] = presets.normalize_buckets(saved["buckets"])
        except (OSError, ValueError, AttributeError):
            pass
        return settings

    def save_settings(self, preset, buckets):
        self.settings["preset"] = preset
        self.settings["buckets"] = presets.normalize_buckets(buckets)
        self._atomic_write(self.dir / "project.json", json.dumps(self.settings, indent=1))

    # ------------------------------------------------------------- catalog

    def _load(self):
        if not self._journal.exists():
            return
        with open(self._journal, encoding="utf-8") as f:
            for line in f:
                try:
                    entry = json.loads(line)
                    self.entries[entry["id"]] = entry
                except (ValueError, KeyError, TypeError):
                    continue  # a line cut short by a forced quit

    def put(self, entry):
        """Record one clip durably. Safe against a kill at any moment."""
        with self._lock:
            self.entries[entry["id"]] = entry
            with open(self._journal, "a", encoding="utf-8") as f:
                f.write(json.dumps(entry) + "\n")
                f.flush()
                os.fsync(f.fileno())

    def compact(self):
        with self._lock:
            body = "".join(json.dumps(e) + "\n" for e in self.entries.values())
            self._atomic_write(self._journal, body)

    def _atomic_write(self, path, text):
        tmp = path.with_name(path.name + ".tmp")
        with open(tmp, "w", encoding="utf-8") as f:
            f.write(text)
            f.flush()
            os.fsync(f.fileno())
        tmp.replace(path)

    def clips(self):
        with self._lock:
            return [e for e in self.entries.values() if e.get("status") == TAGGED]

    def skipped(self):
        with self._lock:
            return [e for e in self.entries.values() if e.get("status") == SKIPPED]

    def current_path(self, entry):
        """Where the clip is right now: its filed spot if filed, else original."""
        return self.root / (entry.get("sorted_path") or entry["rel_path"])

    def thumb_path(self, clip_id):
        return self.thumbs / f"{clip_id}.jpg"

    # ------------------------------------------------------------ manifest

    @property
    def manifest_path(self):
        return self.dir / "manifest.csv"

    def write_manifest(self):
        with self._lock:
            rows = sorted(self.clips(), key=lambda c: (c.get("bucket", ""), c.get("rel_path", "")))
            rows += sorted(self.skipped(), key=lambda c: c.get("rel_path", ""))
        tmp = self.manifest_path.with_name("manifest.csv.tmp")
        with open(tmp, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.writer(f)
            writer.writerow(MANIFEST_COLUMNS)
            for c in rows:
                tagged = c.get("status") == TAGGED
                resolution = f"{c['width']}x{c['height']}" if c.get("width") and c.get("height") else ""
                if tagged:
                    note = "filed into Sorted" if c.get("sorted_path") else "original left in place"
                else:
                    note = f"SKIPPED: {c.get('note', 'could not be read')}"
                writer.writerow([_spreadsheet_safe(v) for v in [
                    c.get("file"), c.get("rel_path"), c.get("sorted_path") or c.get("rel_path"),
                    c.get("source_folder"), c.get("date"), c.get("duration"), resolution,
                    c.get("bucket") if tagged else "", c.get("setting") if tagged else "",
                    c.get("keeper") if tagged else "", c.get("description") if tagged else "",
                    {"ai": "AI", "demo": "demo (fake tags)"}.get(c.get("tagger"), "") if tagged else "",
                    "yes" if c.get("edited") else "", note]])
        tmp.replace(self.manifest_path)
