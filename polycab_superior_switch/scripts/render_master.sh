#!/usr/bin/env bash
# Detached master render: 1920x1080, 64 spp + OIDN, 16-bit PNG, skips finished frames (safe to re-run).
#   setsid nohup scripts/render_master.sh > /tmp/claude-0/master.log 2>&1 &
cd "$(dirname "$0")/.."
B=${BLENDER:-/tmp/claude-0/blender/blender-5.2.4-linux-x64/blender}
"$B" -b scenes/polycab_superior_switch.blend --python scripts/render_frames.py -- 1,46,72,120,1-120 1920 64 \
  deliverables/master_sequence_png16
echo MASTER_DONE
