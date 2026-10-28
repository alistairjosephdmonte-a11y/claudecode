#!/bin/sh
# The Thirty-Five Dollar Squiggle (crayon picture book): narration → timeline → score → mix → frames → master
# run from anywhere: sh films/swoosh-crayon/build.sh   (SKIP_VOICE=1 to reuse out/cb)
set -e
cd "$(dirname "$0")"
if [ -z "$SKIP_VOICE" ]; then
  ../../.venv/bin/python tts/lines.py
  ../../.venv/bin/python ../../core/tts/tts.py tts/lines.json out/raw > out/tts.log 2>&1      # Kokoro af_heart: reference timbre
  ../../../.venv-cb/bin/python tts/cb.py > out/cb.log 2>&1                                    # Chatterbox: the storyteller
fi
../../.venv/bin/python tts/prep.py out/cb                                                    # trim → out/voice, voice.json
cd ../..
node core/render/events.mjs films/swoosh-crayon
.venv/bin/python films/swoosh-crayon/music/score.py
.venv/bin/python films/swoosh-crayon/mix.py > films/swoosh-crayon/out/mix.log
node core/render/video.mjs films/swoosh-crayon --fps 12 --workers 3 --out films/swoosh-crayon/out/video12.mp4   # the style boils at 12 fps
CRF=22 sh films/swoosh-crayon/tools/mux.sh films/swoosh-crayon/out/video12.mp4 films/swoosh-crayon/out/mix.wav films/swoosh-crayon/the-thirty-five-dollar-squiggle.mp4 24 0
echo BUILD_DONE
