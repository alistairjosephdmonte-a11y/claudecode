#!/usr/bin/env bash
# Preview renders for Gliss 02 (this machine: 4 CPU cores, no GPU).
#   stills    1920x1080 @ 48 spp (brief preview settings), BEAUTY layer: lighting states, plates, product
#   animatic  960x540 @ 16 spp, PREVIS layer (proxies visible). Locked shots with constant lighting are rendered
#             once and held (Cycles seed is fixed, so every held frame would render identically).
#   walkthrough 960x540 @ 16 spp, 240 frames
set -euo pipefail
cd "$(dirname "$0")/.."
BL=${BLENDER:-/tmp/claude-0/blender/blender-5.2.4-linux-x64/blender}
T=${T:-/tmp/claude-0/g2}
F=scenes/POLYCAB_GLISS_02_MASTER.blend
R() { "$BL" -b $F --python scripts/render_frames.py -- "$@" 2>&1 | grep -E "FRAME|Error|Traceback" || true; }
D=deliverables
P=$D/GLISS_02_CLEAN_CHARACTER_PLATES
mkdir -p $P
# lighting comparison: identical CAM_01 transform, exposure and white balance; only the Gliss state differs
R SCENE_ARCHITECTURE 30,100,120,210 1920 48 $T/states png beauty cam=CAM_01_ORDINARY_EVENING
cp $T/states/frame_0030.png $D/GLISS_02_BEFORE.png
cp $T/states/frame_0100.png $D/GLISS_02_FIRST_MEMORY.png
cp $T/states/frame_0120.png $D/GLISS_02_SECOND_MEMORY.png
cp $T/states/frame_0210.png $D/GLISS_02_AFTER.png
echo STATES_DONE
R STUDIO_PACKSHOT 40,300 1920 48 $T/studio
cp $T/studio/frame_0040.png $D/GLISS_02_PRODUCT_MACRO.png
echo PRODUCT_DONE
R SCENE_ARCHITECTURE 18,156,190,216,252 1920 48 $T/plates
for f in 18:SHOT01 156:SHOT06 190:SHOT07 216:SHOT08 252:SHOT09; do
  cp $T/plates/frame_$(printf %04d ${f%%:*}).png $P/GLISS_02_PLATE_${f##*:}_F$(printf %03d ${f%%:*}).png
done
echo PLATES_DONE
# animatic: unique frames only, then hold-fill
R SCENE_ARCHITECTURE 1,37-84,85,109,127,145-204,205,229-276 960 16 $T/anim_raw png previs
R STUDIO_PACKSHOT 277 960 16 $T/anim_raw
python3 scripts/compose_packshot.py $T/anim_raw/frame_0277.png $T/anim_raw/frame_0277_slate.png
python3 scripts/hold_fill.py $T/anim_raw $T/anim
scripts/encode.sh $T/anim $D/GLISS_02_ANIMATIC_15S.mp4
echo ANIMATIC_DONE
R SCENE_WALKTHROUGH 1-240 960 16 $T/walk
scripts/encode.sh $T/walk $D/GLISS_02_WALKTHROUGH_10S.mp4
echo ALL_DONE
