#!/usr/bin/env bash
# Provisional inspection stills, 1920x1080 @ 48 samples, BEAUTY layer (no cast proxies) for the room stills.
set -euo pipefail
cd "$(dirname "$0")/.."
BLENDER=${BLENDER:-/tmp/claude-0/blender/blender-5.2.4-linux-x64/blender}
T=${T:-/tmp/claude-0/gliss_stills}
BL=scenes/POLYCAB_GLISS_MASTER.blend
"$BLENDER" -b $BL --python scripts/render_frames.py -- SCENE_PRODUCT_STUDIO 48,300 1920 48 $T/studio
"$BLENDER" -b $BL --python scripts/render_frames.py -- SCENE_ARCHITECTURE 84,85,276 1920 48 $T/arch
cp $T/studio/frame_0048.png deliverables/GLISS_PRODUCT_MACRO.png
cp $T/studio/frame_0300.png deliverables/GLISS_FINAL_PACKSHOT.png
cp $T/arch/frame_0084.png deliverables/GLISS_LIGHTING_BEFORE.png
cp $T/arch/frame_0085.png deliverables/GLISS_LIGHTING_AFTER.png
cp $T/arch/frame_0276.png deliverables/GLISS_ENVIRONMENT_MASTER.png
echo STILLS_DONE
