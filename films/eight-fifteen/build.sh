#!/bin/sh
# One command: voice → timeline → picture → mix → master.  Run from anywhere.
set -e
HERE=$(cd "$(dirname "$0")" && pwd)
LIB=${LIB:-$(cd "$HERE/../.." && pwd)}
export LIB
[ -f "$LIB/core/render/video.mjs" ] || { echo "set LIB to the library folder"; exit 1; }
cd "$LIB"
PY="$LIB/.venv/bin/python"
B=https://raw.githubusercontent.com/google/fonts/main/ofl/shipporimincho
mkdir -p "$HERE/fonts"
for f in ShipporiMincho-Regular.ttf ShipporiMincho-Medium.ttf OFL.txt; do [ -f "$HERE/fonts/$f" ] || curl -sSfL -o "$HERE/fonts/$f" "$B/$f"; done
[ -f "$HERE/voice/dur.json" ] || "$PY" core/tts/tts.py "$HERE/lines.json" "$HERE/voice"
"$PY" core/tts/asr_check.py "$HERE/lines.json" "$HERE/voice" --lang en
"$PY" "$HERE/gen_timeline.py"
node core/render/events.mjs "$HERE"
node core/render/readcheck.mjs "$HERE"
node core/render/video.mjs "$HERE" --fps 24 --workers 4 --out "$HERE/out/video.mp4"
"$PY" "$HERE/mix.py"
sh core/render/mux.sh "$HERE/out/video.mp4" "$HERE/out/mix.wav" "$HERE/eight-fifteen.mp4" 24 2
"$PY" core/render/srt.py "$HERE/cues.json" "$HERE/eight-fifteen.srt"
node core/render/still.mjs "$HERE" 100 --prefix poster_ --out "$HERE/out" && cp "$HERE/out/poster_100.jpg" "$HERE/poster.jpg"
