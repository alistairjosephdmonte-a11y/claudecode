#!/usr/bin/env bash
# Master: all 360 frames rendered at 1920x1080 (16-bit PNG, resumable: existing frames are skipped), then
# encoded as a 1080p MP4 and a 4K MP4 upscaled with Lanczos. The 4K file is an UPSCALE, not a native 4K render
# (a native 4K frame measured 19.7 min on this 4-core CPU, ~4.5 days for 360 frames). Run detached:
#   setsid nohup scripts/render_master.sh > master.log 2>&1 &
set -euo pipefail
cd "$(dirname "$0")/.."
BLENDER=${BLENDER:-/tmp/claude-0/blender/blender-5.2.4-linux-x64/blender}
SPP=${SPP:-48}
SEQ=deliverables/master_sequence_1080p_png16
"$BLENDER" -b scenes/polycab_invisible_force.blend --python scripts/render_frames.py -- \
  1,72,120,216,288,360,1-360 1920 "$SPP" "$SEQ"
scripts/encode.sh "$SEQ" deliverables/invisible_force_master_1080p.mp4 14
ffmpeg -y -loglevel error -framerate 24 -start_number 1 -i "$SEQ/frame_%04d.png" \
  -vf "scale=3840:2160:flags=lanczos" -c:v libx264 -preset slow -crf 14 -pix_fmt yuv420p \
  -color_primaries bt709 -color_trc bt709 -colorspace bt709 -movflags +faststart \
  deliverables/invisible_force_master_4k_upscaled.mp4
echo MASTER_DONE
