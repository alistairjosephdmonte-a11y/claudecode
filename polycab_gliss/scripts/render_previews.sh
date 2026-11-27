#!/usr/bin/env bash
# Provisional inspection renders (no final rendering): 15 s editorial animatic (all 10 shots, cast proxies on)
# and the 10 s architectural walkthrough, both 960x540 / 16 samples, then H.264.
#   setsid nohup scripts/render_previews.sh > previews.log 2>&1 &
set -euo pipefail
cd "$(dirname "$0")/.."
BLENDER=${BLENDER:-/tmp/claude-0/blender/blender-5.2.4-linux-x64/blender}
W=${W:-960}; SPP=${SPP:-16}
SEQ=${SEQ:-/tmp/claude-0/gliss_animatic}
WSEQ=${WSEQ:-/tmp/claude-0/gliss_walkthrough}
BL=scenes/POLYCAB_GLISS_MASTER.blend
"$BLENDER" -b $BL --python scripts/render_frames.py -- SCENE_PRODUCT_STUDIO 1-60,277-360 $W $SPP "$SEQ"
"$BLENDER" -b $BL --python scripts/render_frames.py -- SCENE_ARCHITECTURE 61-276 $W $SPP "$SEQ" png previs
scripts/encode.sh "$SEQ" deliverables/GLISS_15S_MASTER_ANIMATIC.mp4 20
"$BLENDER" -b $BL --python scripts/render_frames.py -- SCENE_WALKTHROUGH_PREVIEW 1-240 $W $SPP "$WSEQ"
scripts/encode.sh "$WSEQ" deliverables/GLISS_ARCHITECTURAL_WALKTHROUGH_PREVIEW.mp4 20
echo PREVIEWS_DONE
