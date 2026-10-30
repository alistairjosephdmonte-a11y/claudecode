#!/bin/sh
# Trimming Through the Ages — full build. Run from anywhere: sh films/manscaped-trimming-through-the-ages/build.sh
#   SKIP_VOICE=1   reuse the recorded narration (out/cb)
#   CHAPTERS="1 2" render only these chapters (others are reused from out/ch if present)
set -e
cd "$(dirname "$0")"; F=films/manscaped-trimming-through-the-ages
if [ -z "$SKIP_VOICE" ]; then
  ../../.venv/bin/python tts/lines.py
  ../../.venv/bin/python ../../core/tts/tts.py tts/lines.json out/raw > out/tts.log 2>&1            # Kokoro bm_george: the reference timbre
  HF_HUB_OFFLINE=1 ../../../.venv-cb/bin/python tts/cb.py > out/cb.log 2>&1                         # Chatterbox: the narrator
fi
../../.venv/bin/python tts/prep.py out/cb                                                          # trim → out/voice + voice.json
cd ../..
node $F/tools/timing.mjs                                                                          # qc/narration-script.md (+ beat check)
node core/render/events.mjs $F --size 1440x1080
.venv/bin/python $F/music/score.py
.venv/bin/python $F/mix.py > $F/out/mix.log                                                      # out/mix.wav + out/stems/{narration,foley,music}.wav
for n in ${CHAPTERS:-1 2 3 4 5 6 7 8 9 10}; do
  o=$F/out/ch/ch$(printf %02d $n).mp4
  node core/render/video.mjs $F --q "ch=$n" --fps 24 --workers 4 --size 1440x1080 --out $o
done
# stitch: every chapter must be exactly 720 frames; concat by stream copy (no re-encode, no duplicated boundary frames)
: > $F/out/ch/list.txt
for n in 1 2 3 4 5 6 7 8 9 10; do o=$F/out/ch/ch$(printf %02d $n).mp4
  c=$(ffprobe -v error -count_frames -select_streams v:0 -show_entries stream=nb_read_frames -of csv=p=0 $o)
  [ "$c" = "720" ] || { echo "chapter $n has $c frames, expected 720"; exit 1; }
  echo "file '$(basename $o)'" >> $F/out/ch/list.txt; done
ffmpeg -loglevel error -y -f concat -safe 0 -i $F/out/ch/list.txt -c copy $F/out/video24.mp4
CRF=20 sh $F/tools/mux.sh $F/out/video24.mp4 $F/out/mix.wav $F/trimming-through-the-ages-4x3.mp4 24 0
c=$(ffprobe -v error -count_frames -select_streams v:0 -show_entries stream=nb_read_frames -of csv=p=0 $F/trimming-through-the-ages-4x3.mp4); echo "master frames: $c"
echo BUILD_DONE
