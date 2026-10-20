#!/bin/sh
# Voices (Kokoro TTS, offline) → speech check → music, sfx and lip-sync data.
# Needs a Lemo-Opuscar library with the voice and music tiers installed: set LIB to its folder.
set -e
HERE=$(cd "$(dirname "$0")/.." && pwd)
[ -f "$LIB/core/tts/tts.py" ] || { echo "set LIB to the lemo-opuscar folder"; exit 1; }
PY="$LIB/.venv/bin/python"
cd "$LIB"
"$PY" core/tts/tts.py "$HERE/audio-src/lines.json" "$HERE/public/audio/voice"
"$PY" core/tts/asr_check.py "$HERE/audio-src/lines.json" "$HERE/public/audio/voice" --lang en
LIB="$LIB" "$PY" "$HERE/audio-src/build_audio.py"
