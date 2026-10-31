#!/bin/sh
# Render the picture act by act (6 × 1920 frames), verify each, stitch by stream copy into out/video.mp4.
set -e
cd "$(dirname "$0")/../../.."; F=films/brand-coroner-blockbuster; mkdir -p $F/out/act
for a in ${ACTS:-0 1 2 3 4 5}; do o=$F/out/act/act$a.mp4
  node core/render/video.mjs $F --q "act=$a" --fps 24 --workers ${WK:-4} --out $o
  c=$(ffprobe -v error -count_frames -select_streams v:0 -show_entries stream=nb_read_frames -of csv=p=0 $o); [ "$c" = "1920" ] || { echo "act $a has $c frames, expected 1920"; exit 1; }
  echo "ACT_DONE $a"; done
: > $F/out/act/list.txt; for a in 0 1 2 3 4 5; do echo "file 'act$a.mp4'" >> $F/out/act/list.txt; done
ffmpeg -loglevel error -y -f concat -safe 0 -i $F/out/act/list.txt -c copy $F/out/video.mp4
echo RENDER_DONE
