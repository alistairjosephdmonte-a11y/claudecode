"""Synthetic sample footage, so anyone can try the app without real clips."""

import subprocess
from pathlib import Path

from . import media

SOURCES = ["testsrc2", "smptebars", "mandelbrot", "rgbtestsrc", "testsrc", "yuvtestsrc"]
FOLDERS = ["A_CAM", "B_CAM/DCIM/100MEDIA", "DRONE"]
EXTENSIONS = [".mp4", ".mov", ".mkv"]


def make_samples(out, count=9):
    """Write `count` short clips into card-style folders under `out`, plus one
    sidecar file and one deliberately broken clip (to show how skips look)."""
    out = Path(out)
    ffmpeg = media.find_tool("ffmpeg")
    if not ffmpeg:
        raise RuntimeError("ffmpeg is not installed")
    made = []
    for i in range(count):
        folder = out / FOLDERS[i % len(FOLDERS)]
        folder.mkdir(parents=True, exist_ok=True)
        clip = folder / f"CLIP_{i + 1:04d}{EXTENSIONS[i % len(EXTENSIONS)]}"
        if not clip.exists():
            result = subprocess.run(
                [ffmpeg, "-y", "-v", "error", "-f", "lavfi",
                 "-i", f"{SOURCES[i % len(SOURCES)]}=size=320x180:rate=12",
                 "-t", "2", "-pix_fmt", "yuv420p", str(clip)],
                capture_output=True, text=True, stdin=subprocess.DEVNULL)
            if result.returncode != 0:
                raise RuntimeError(f"ffmpeg could not write {clip.name}: {result.stderr[:200]}")
        made.append(clip)
    sidecar = made[0].with_suffix(".xmp")
    if not sidecar.exists():
        sidecar.write_text("<x:xmpmeta xmlns:x='adobe:ns:meta/'/>\n", encoding="utf-8")
    broken = out / FOLDERS[0] / "BROKEN_CLIP.mp4"
    if not broken.exists():
        broken.write_bytes(b"this is not a video file\n" * 40)
    return made
