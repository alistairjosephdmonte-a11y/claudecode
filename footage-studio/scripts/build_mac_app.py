#!/usr/bin/env python3
"""Build the double-click Mac app: dist/Footage Studio.app (+ a zip of it).

The app is self-contained: the Python package is copied inside the bundle, so
it keeps working after being dragged to Applications. It still needs python3
and ffmpeg on the Mac, and tells the user how to get them if they are missing.

    python3 scripts/build_mac_app.py

Runs on any OS. NOTE: the resulting app has not yet been launched on a real Mac.
"""

import plistlib
import shutil
import sys
import zipfile
from pathlib import Path

PROJECT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT))
from footage_studio import __version__  # noqa: E402

APP_NAME = "Footage Studio"

LAUNCHER = r'''#!/bin/bash
# Footage Studio launcher. Finder starts apps without the shell's PATH, so the
# usual Homebrew locations are added here.
export PATH="/opt/homebrew/bin:/usr/local/bin:/opt/local/bin:$PATH"
export PYTHONDONTWRITEBYTECODE=1
RESOURCES="${0%/*}/../Resources"

alert() {
  /usr/bin/osascript -e "display dialog \"$1\" with title \"Footage Studio\" buttons {\"OK\"} default button 1 with icon caution" >/dev/null 2>&1 || echo "$1" >&2
}

if ! python3 -c 'import sys; sys.exit(0 if sys.version_info >= (3, 9) else 1)' >/dev/null 2>&1; then
  alert "Footage Studio needs Python 3.9 or newer. Install it from python.org/downloads, then open Footage Studio again."
  exit 1
fi
if ! command -v ffmpeg >/dev/null 2>&1 || ! command -v ffprobe >/dev/null 2>&1; then
  alert "Footage Studio needs ffmpeg to read your clips. Install Homebrew from brew.sh, run: brew install ffmpeg, then open Footage Studio again."
  exit 1
fi
cd "$RESOURCES" || exit 1
exec python3 -m footage_studio "$@"
'''


def build(dist=None):
    dist = Path(dist) if dist else PROJECT / "dist"
    app = dist / f"{APP_NAME}.app"
    if app.exists():
        shutil.rmtree(app)
    macos = app / "Contents" / "MacOS"
    resources = app / "Contents" / "Resources"
    macos.mkdir(parents=True)
    shutil.copytree(PROJECT / "footage_studio", resources / "footage_studio",
                    ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
    launcher = macos / "footage-studio"
    launcher.write_text(LAUNCHER, encoding="utf-8")
    launcher.chmod(0o755)
    with open(app / "Contents" / "Info.plist", "wb") as f:
        plistlib.dump({
            "CFBundleName": APP_NAME,
            "CFBundleDisplayName": APP_NAME,
            "CFBundleIdentifier": "studio.footage.app",
            "CFBundleExecutable": "footage-studio",
            "CFBundlePackageType": "APPL",
            "CFBundleShortVersionString": __version__,
            "CFBundleVersion": __version__,
            "CFBundleInfoDictionaryVersion": "6.0",
            "LSMinimumSystemVersion": "11.0",
            "NSHighResolutionCapable": True,
        }, f)
    archive = dist / "Footage-Studio-mac.zip"
    with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED) as z:
        for path in sorted(app.rglob("*")):
            if path.is_file():
                info = zipfile.ZipInfo.from_file(path, path.relative_to(dist).as_posix())
                info.compress_type = zipfile.ZIP_DEFLATED
                z.writestr(info, path.read_bytes())
    return app, archive


if __name__ == "__main__":
    built, zipped = build()
    print(f"Built {built}\nZipped {zipped}")
