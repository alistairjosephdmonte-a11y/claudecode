#!/usr/bin/env bash
# Encodes a 16-bit PNG frame sequence (24 fps) to an H.264 review MP4.
#   scripts/encode_review.sh [sequence_dir] [out.mp4]
set -euo pipefail
cd "$(dirname "$0")/.."
SEQ=${1:-deliverables/master_sequence_png16}
OUT=${2:-deliverables/superior_switch_review_1080p.mp4}
ffmpeg -y -loglevel error -framerate 24 -start_number 1 -i "$SEQ/frame_%04d.png" \
  -c:v libx264 -preset slow -crf 16 -pix_fmt yuv420p -color_primaries bt709 -color_trc bt709 -colorspace bt709 \
  -movflags +faststart "$OUT"
echo "ENCODED $OUT"
