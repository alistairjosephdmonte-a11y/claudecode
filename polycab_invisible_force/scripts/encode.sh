#!/usr/bin/env bash
# PNG sequence (24 fps) -> H.264 MP4.   scripts/encode.sh <sequence_dir> <out.mp4> [crf]
set -euo pipefail
cd "$(dirname "$0")/.."
SEQ=$1; OUT=$2; CRF=${3:-16}
ffmpeg -y -loglevel error -framerate 24 -start_number 1 -i "$SEQ/frame_%04d.png" \
  -c:v libx264 -preset slow -crf "$CRF" -pix_fmt yuv420p -color_primaries bt709 -color_trc bt709 -colorspace bt709 \
  -movflags +faststart "$OUT"
echo "ENCODED $OUT"
