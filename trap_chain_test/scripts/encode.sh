#!/usr/bin/env bash
# Encodes deliverables/frames/ to deliverables/trap_chain_test.mp4 (24 fps, H.264).
set -euo pipefail
cd "$(dirname "$0")/.."
ffmpeg -y -v error -framerate 24 -i deliverables/frames/frame_%04d.png \
  -c:v libx264 -crf 18 -pix_fmt yuv420p -movflags +faststart deliverables/trap_chain_test.mp4
