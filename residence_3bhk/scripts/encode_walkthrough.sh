#!/usr/bin/env bash
# Encodes deliverables/walkthrough_render_sequence/frame_####.png (24 fps) to H.264.
set -euo pipefail
cd "$(dirname "$0")/.."
ffmpeg -y -loglevel error -framerate 24 -start_number 1 -i deliverables/walkthrough_render_sequence/frame_%04d.png \
  -c:v libx264 -preset slow -crf 17 -pix_fmt yuv420p -movflags +faststart deliverables/walkthrough.mp4
echo "ENCODED deliverables/walkthrough.mp4"
