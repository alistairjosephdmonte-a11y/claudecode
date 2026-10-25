#!/bin/sh
# One command: fonts → voices → speech check → events → video → score & mix → master → subtitles.
set -e
HERE=$(cd "$(dirname "$0")" && pwd); LIB=${LIB:-$(cd "$HERE/../.." && pwd)}; PY="$LIB/.venv/bin/python"
cd "$HERE"
[ -f fonts.css ] || node fetch_fonts.mjs
[ -f node_modules/three/package.json ] || npm install --no-audit --no-fund
[ -f voices/dur.json ] || "$PY" tts/gen.py
"$PY" asr.py
node render.mjs events
FPS=24 node render.mjs video ${WORKERS:-2}
ffmpeg -y -loglevel error -f concat -safe 0 -i out/list.txt -c copy out/video.mp4
"$PY" mix.py
sh "$LIB/core/render/mux.sh" out/video.mp4 out/mix.wav ramayana.mp4 24 2
"$PY" make_srt.py
