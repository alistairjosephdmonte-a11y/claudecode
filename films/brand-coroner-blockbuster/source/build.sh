#!/bin/sh
# Brand Coroner · Case 001 · Blockbuster — full build. Run from anywhere: sh films/brand-coroner-blockbuster/build.sh
#   SKIP_VOICE=1   reuse recorded narration (out/cb)      SKIP_RENDER=1  reuse out/video.mp4      ACTS="0 1"  render only these acts
set -e
cd "$(dirname "$0")"; F=films/brand-coroner-blockbuster
../../.venv/bin/python story.py                                                            # story.json + tts/lines.json
if [ -z "$SKIP_VOICE" ]; then
  ../../.venv/bin/python ../../core/tts/tts.py tts/lines.json out/raw > out/tts.log 2>&1      # Kokoro am_michael: reference timbre
  HF_HUB_OFFLINE=1 ../../../.venv-cb/bin/python tts/cb.py > out/cb.log 2>&1                 # Chatterbox: the narrator
fi
../../.venv/bin/python tts/prep.py out/cb                                                  # trim → out/voice + voice.json
../../.venv/bin/python music/score.py                                                      # music/score.wav + stems
../../.venv/bin/python mix.py                                                              # out/mix.wav, out/stems, out/tl.json, subs.srt
cd ../..
node $F/tools/manifest.mjs                                                                 # qc/shot-list.md + qc/manifest.json
[ -n "$SKIP_RENDER" ] || sh $F/tools/render.sh                                             # 6 acts × 1920 frames → out/video.mp4
c=$(ffprobe -v error -count_frames -select_streams v:0 -show_entries stream=nb_read_frames -of csv=p=0 $F/out/video.mp4); [ "$c" = "11520" ] || { echo "video has $c frames, expected 11520"; exit 1; }
CRF=18 sh $F/tools/mux.sh $F/out/video.mp4 $F/out/mix.wav $F/brand-coroner-blockbuster-1080p.mp4 24 0
echo BUILD_DONE
