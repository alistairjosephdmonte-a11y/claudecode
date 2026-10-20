#!/bin/sh
# Preview (960×540) → final 1920×1080 H.264 → loudness-normalised master (−16 LUFS, −1.5 dBTP).
set -e
cd "$(dirname "$0")/.."
npx remotion render src/index.ts SeatIsTaken out/preview-540p.mp4 --scale=0.5 --codec=h264 --log=error
npx remotion render src/index.ts SeatIsTaken out/remotion-master.mp4 --codec=h264 --crf=18 --log=error
M=$(ffmpeg -hide_banner -i out/remotion-master.mp4 -af loudnorm=I=-16:TP=-1.5:LRA=11:print_format=json -f null - 2>&1 | sed -n '/{/,/}/p')
v() { echo "$M" | grep "\"$1\"" | sed 's/.*: "\(.*\)".*/\1/'; }
ffmpeg -hide_banner -loglevel error -y -i out/remotion-master.mp4 -c:v copy \
  -af "loudnorm=I=-16:TP=-1.5:LRA=11:measured_I=$(v input_i):measured_TP=$(v input_tp):measured_LRA=$(v input_lra):measured_thresh=$(v input_thresh):offset=$(v target_offset):linear=true" \
  -ar 48000 -c:a aac -b:a 192k -movflags +faststart out/the-seat-is-taken.mp4
echo "done: out/the-seat-is-taken.mp4"
