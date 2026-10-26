#!/bin/sh
# fonts → voices → events → video → score & mix → master → subtitles
set -e
HERE=$(cd "$(dirname "$0")" && pwd); LIB=$(cd "$HERE/../.." && pwd); PY="$LIB/.venv/bin/python"; cd "$HERE"
[ -f fonts.css ] || node fetch_fonts.mjs
[ -f voices/dur.json ] || { node tts/gen.mjs && "$PY" "$LIB/core/tts/tts.py" tts/lines.json voices; }
node render.mjs events
FPS=24 node render.mjs video ${WORKERS:-4}
ffmpeg -y -loglevel error -f concat -safe 0 -i out/list.txt -c copy out/video.mp4
"$PY" mix.py
sh "$LIB/core/render/mux.sh" out/video.mp4 out/mix.wav ramayana-hindi.mp4 24 2
"$PY" make_srt.py
