#!/usr/bin/env bash
# 4K master: all 360 frames, 16-bit PNG, resumable (existing frames are skipped). Run detached:
#   setsid nohup scripts/render_master.sh > master.log 2>&1 &
set -euo pipefail
cd "$(dirname "$0")/.."
BLENDER=${BLENDER:-/tmp/claude-0/blender/blender-5.2.4-linux-x64/blender}
SPP=${SPP:-48}
"$BLENDER" -b scenes/polycab_invisible_force.blend --python scripts/render_frames.py -- \
  1,72,120,216,288,360,1-360 3840 "$SPP" deliverables/master_sequence_4k_png16
echo MASTER_DONE
