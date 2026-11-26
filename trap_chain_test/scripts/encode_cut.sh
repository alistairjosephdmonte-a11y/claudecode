#!/usr/bin/env bash
# Muxes deliverables/cut_frames/ (24 fps) with deliverables/trap_cut_audio.wav into deliverables/trap_chain_15s.mp4.
set -euo pipefail
cd "$(dirname "$0")/.."
ffmpeg -y -v error -framerate 24 -i deliverables/cut_frames/frame_%04d.png -i deliverables/trap_cut_audio.wav \
  -c:v libx264 -crf 18 -pix_fmt yuv420p -c:a aac -b:a 192k -shortest -movflags +faststart \
  deliverables/trap_chain_15s.mp4
