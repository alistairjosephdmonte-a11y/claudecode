#!/usr/bin/env bash
# Blockout render pass (spec section 07): 7 milestone frames (1920 px, 48 spp) and the 360-frame preview
# (960 x 540, 8 spp + denoise, labelled), all clay. Detached:
#   setsid nohup scripts/render_blockout.sh > /tmp/claude-0/bc_blockout.log 2>&1 < /dev/null &
set -euo pipefail
cd "$(dirname "$0")/.."
BLENDER=${BLENDER:-/tmp/claude-0/blender/blender-5.2.4-linux-x64/blender}
T=${T:-/tmp/claude-0/bc_blockout}
BL=scenes/BOWLCURRY_MADRAS_BLOCKOUT.blend
MS="24 66 102 145 186 230 330"
"$BLENDER" -b $BL --python scripts/render_frames.py -- BC_MADRAS_MASTER "$(echo $MS | tr ' ' ,)" 1920 48 $T/milestones
python3 scripts/milestones.py $T/milestones $MS
echo MILESTONES_DONE
"$BLENDER" -b $BL --python scripts/render_frames.py -- BC_MADRAS_MASTER 1-360 960 8 $T/preview
python3 scripts/burnin.py $T/preview $T/preview_labelled
scripts/encode.sh $T/preview_labelled deliverables/BC_BLOCKOUT_PREVIEW_360F.mp4 20
echo BLOCKOUT_DONE
