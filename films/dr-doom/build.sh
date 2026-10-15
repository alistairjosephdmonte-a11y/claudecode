#!/bin/sh
# One command: fonts → voice → timeline → picture → sound → master.
set -e
HERE=$(cd "$(dirname "$0")" && pwd)
LIB=${LIB:-$(cd "$HERE/../.." && pwd)}
export LIB
[ -f "$LIB/core/render/video.mjs" ] || { echo "set LIB to the library folder"; exit 1; }
cd "$LIB"
PY="$LIB/.venv/bin/python"
B=https://raw.githubusercontent.com/google/fonts/main/ofl
mkdir -p "$HERE/fonts"
[ -f "$HERE/fonts/Anton-Regular.ttf" ] || curl -sSfL -o "$HERE/fonts/Anton-Regular.ttf" "$B/anton/Anton-Regular.ttf"
[ -f "$HERE/fonts/BarlowCondensed-SemiBold.ttf" ] || curl -sSfL -o "$HERE/fonts/BarlowCondensed-SemiBold.ttf" "$B/barlowcondensed/BarlowCondensed-SemiBold.ttf"
[ -f "$HERE/fonts/JetBrainsMono[wght].ttf" ] || curl -sSfL -o "$HERE/fonts/JetBrainsMono[wght].ttf" "$B/jetbrainsmono/JetBrainsMono%5Bwght%5D.ttf"
[ -f "$HERE/voice/dur.json" ] || "$PY" core/tts/tts.py "$HERE/lines.json" "$HERE/voice"
"$PY" core/tts/asr_check.py "$HERE/lines.json" "$HERE/voice" --lang en
"$PY" "$HERE/gen_timeline.py"
node core/render/events.mjs "$HERE"
node core/render/video.mjs "$HERE" --fps 24 --workers 4 --out "$HERE/out/video.mp4"
"$PY" "$HERE/mix.py"
sh core/render/mux.sh "$HERE/out/video.mp4" "$HERE/out/mix.wav" "$HERE/dr-doom.mp4" 24 0
"$PY" core/render/srt.py "$HERE/cues.json" "$HERE/dr-doom.srt"
