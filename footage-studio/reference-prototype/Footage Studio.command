#!/bin/bash
# Footage Studio - Mac launcher. Double-click to open the app.
cd "$(dirname "$0")" || exit 1

if ! command -v python3 >/dev/null; then
  echo "Python 3 isn't installed. Get it from https://www.python.org/downloads/"
  read -r -p "Press Enter to close..."
  exit 1
fi
if ! command -v ffmpeg >/dev/null; then
  echo "ffmpeg isn't installed."
  echo "Easiest fix: install Homebrew from https://brew.sh, then run: brew install ffmpeg"
  read -r -p "Press Enter to close..."
  exit 1
fi

python3 footage_studio.py
