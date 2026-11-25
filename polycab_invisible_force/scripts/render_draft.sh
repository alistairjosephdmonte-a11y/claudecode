#!/usr/bin/env bash
# Lightweight review draft: 960x540, 12 samples, then H.264 preview.
set -euo pipefail
cd "$(dirname "$0")/.."
BLENDER=${BLENDER:-/tmp/claude-0/blender/blender-5.2.4-linux-x64/blender}
SEQ=${1:-/tmp/claude-0/if_draft540}
"$BLENDER" -b scenes/polycab_invisible_force.blend --python scripts/render_frames.py -- 1-360 960 12 "$SEQ"
scripts/encode.sh "$SEQ" deliverables/invisible_force_draft_540p.mp4 22
echo DRAFT_DONE
