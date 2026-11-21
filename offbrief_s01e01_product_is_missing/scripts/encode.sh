#!/usr/bin/env bash
# Encode a rendered frame folder + room tone + BOX_01 foley into the previs MP4 (no overlays).
#   scripts/encode.sh deliverables/frames_144p deliverables/OFFBRIEF_S01E01_PREVIS_144P.mp4
set -euo pipefail
cd "$(dirname "$0")/.."
IN=${1:-deliverables/frames_144p}
OUT=${2:-deliverables/OFFBRIEF_S01E01_PREVIS_144P.mp4}
n=$(ls "$IN"/OFFBRIEF_S01E01_*.png | wc -l)
[ "$n" -eq 720 ] || { echo "expected 720 frames in $IN, found $n" >&2; exit 1; }
ffmpeg -y -loglevel error -framerate 24 -start_number 1 -i "$IN/OFFBRIEF_S01E01_%04d.png" \
  -i audio/OFFBRIEF_S01E01_room_tone.wav -i audio/OFFBRIEF_S01E01_box_foley.wav \
  -filter_complex "[1:a][2:a]amix=inputs=2:normalize=0[a]" -map 0:v -map "[a]" \
  -c:v libx264 -crf 16 -preset slow -pix_fmt yuv420p -c:a aac -b:a 160k -t 30 -movflags +faststart "$OUT"
ffprobe -v error -count_frames -select_streams v:0 -show_entries stream=nb_read_frames,width,height,r_frame_rate -of csv=p=0 "$OUT"
