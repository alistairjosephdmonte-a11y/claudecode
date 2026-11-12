"""Low-res EEVEE test frames.  blender -b scenes/LASTJOB_EP01_WRONG_BAG.blend --python scripts/render_test.py -- 15,45 [width]"""
import os
import sys

import bpy

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import config as C  # noqa: E402

argv = sys.argv[sys.argv.index("--") + 1:]
w = int(argv[1]) if len(argv) > 1 else 640
sc = bpy.context.scene
sc.render.resolution_x, sc.render.resolution_y = w, w * 9 // 16
sc.eevee.taa_render_samples = 8
os.makedirs(C.P["tests"], exist_ok=True)
for f in (int(x) for x in argv[0].split(",")):
    sc.frame_set(f)
    sc.render.filepath = os.path.join(C.P["tests"], f"t_{f:03d}.png")
    bpy.ops.render.render(write_still=True)
