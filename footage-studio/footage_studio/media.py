"""Reading footage: finding clips, probing metadata, pulling preview frames.

Everything here only ever reads from the project folder. Preview frames are
written to a work directory the caller supplies (outside the project).
"""

import hashlib
import json
import os
import shutil
import subprocess
from datetime import datetime
from pathlib import Path

# mp4, mov, mkv, webm, avi, mts are decode-verified. m4v, 3gp, m2ts, mxf are
# attempted but unverified. Camera RAW (R3D, BRAW, Cinema RAW) is unsupported.
VIDEO_EXTS = {".mp4", ".mov", ".m4v", ".avi", ".mkv", ".webm", ".3gp", ".mts", ".m2ts", ".mxf"}
SIDECAR_EXTS = {".xmp", ".json", ".xml", ".thm", ".lrf"}
SORTED_DIR = "Sorted"
MOVES_LOG = ".footage-studio-moves.jsonl"
FRAME_COUNT = 4
FRAME_WIDTH = 384
FRAME_FRACTIONS = [0.15, 0.40, 0.65, 0.90]
# Apps launched from Finder don't inherit the shell PATH, so Homebrew's
# locations are checked explicitly.
EXTRA_TOOL_DIRS = ["/opt/homebrew/bin", "/usr/local/bin", "/opt/local/bin"]


def find_tool(name):
    found = shutil.which(name)
    if found:
        return found
    for folder in EXTRA_TOOL_DIRS:
        candidate = Path(folder) / name
        if candidate.is_file() and os.access(candidate, os.X_OK):
            return str(candidate)
    return None


def missing_tools():
    return [t for t in ("ffmpeg", "ffprobe") if find_tool(t) is None]


def _run(cmd, timeout=120):
    try:
        return subprocess.run(cmd, capture_output=True, text=True, timeout=timeout,
                              stdin=subprocess.DEVNULL)
    except (subprocess.TimeoutExpired, OSError):
        return None


def is_filed_root(root):
    """True when Sorted/ in this project was created by Footage Studio."""
    return (root / SORTED_DIR / MOVES_LOG).is_file()


def scan(root):
    """Every video under root, sorted. Hidden files/folders are skipped
    (including macOS '._' resource forks), as is our own Sorted/ tree."""
    skip_sorted = is_filed_root(root)
    videos = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = sorted(
            d for d in dirnames
            if not d.startswith(".")
            and not (skip_sorted and Path(dirpath) == root and d == SORTED_DIR))
        for name in filenames:
            if not name.startswith(".") and Path(name).suffix.lower() in VIDEO_EXTS:
                videos.append(Path(dirpath) / name)
    videos.sort()
    return videos


def clip_id(path, root):
    """Stable id for a clip: its path inside the project plus its size."""
    h = hashlib.sha1()
    h.update(path.relative_to(root).as_posix().encode())
    h.update(str(path.stat().st_size).encode())
    return h.hexdigest()[:16]


def probe(path):
    """Metadata via ffprobe. Missing values stay None."""
    meta = {"date": None, "duration": None, "width": None, "height": None,
            "orientation": None, "hdr": False}
    out = _run([find_tool("ffprobe") or "ffprobe", "-v", "quiet", "-print_format", "json",
                "-show_format", "-show_streams", str(path)], timeout=60)
    data = {}
    if out is not None and out.returncode == 0:
        try:
            data = json.loads(out.stdout)
        except json.JSONDecodeError:
            data = {}
    fmt = data.get("format", {})
    tags = fmt.get("tags", {}) or {}
    created = tags.get("creation_time") or tags.get("com.apple.quicktime.creationdate")
    if created:
        try:
            meta["date"] = datetime.fromisoformat(created.replace("Z", "+00:00")).date().isoformat()
        except ValueError:
            pass
    try:
        meta["duration"] = round(float(fmt["duration"]), 1)
    except (KeyError, TypeError, ValueError):
        pass
    for stream in data.get("streams", []):
        if stream.get("codec_type") != "video":
            continue
        width, height = stream.get("width"), stream.get("height")
        meta["width"], meta["height"] = width, height
        meta["hdr"] = stream.get("color_transfer") in ("smpte2084", "arib-std-b67")
        rotation = (stream.get("tags") or {}).get("rotate")
        for side in stream.get("side_data_list", []):
            rotation = side.get("rotation", rotation)
        try:
            rotation = abs(int(float(rotation or 0)))
        except (TypeError, ValueError):
            rotation = 0
        if width and height:
            vertical = (height > width) if rotation in (0, 180) else (width > height)
            meta["orientation"] = "vertical" if vertical else "horizontal"
        break
    if not meta["date"]:
        meta["date"] = datetime.fromtimestamp(path.stat().st_mtime).date().isoformat()
    return meta


def grab_frames(path, duration, workdir):
    """Up to FRAME_COUNT small JPEG preview frames spread across the clip,
    returned as bytes. An empty list means the clip could not be decoded."""
    times = [duration * f for f in FRAME_FRACTIONS] if duration else [0.0]
    frames = []
    out = Path(workdir) / "frame.jpg"
    for t in times[:FRAME_COUNT]:
        if out.exists():
            out.unlink()
        result = _run([
            find_tool("ffmpeg") or "ffmpeg", "-y", "-v", "error", "-ss", f"{t:.2f}",
            "-i", str(path), "-frames:v", "1",
            "-vf", f"scale='min({FRAME_WIDTH},iw)':-2", "-q:v", "5", str(out)])
        if result is not None and result.returncode == 0 and out.exists() and out.stat().st_size:
            frames.append(out.read_bytes())
    if out.exists():
        out.unlink()
    return frames
