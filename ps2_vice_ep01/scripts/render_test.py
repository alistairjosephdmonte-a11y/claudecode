"""Low-res EEVEE test frames.  blender -b scenes/PS_GTA_EP01_BLOCK.blend --python scripts/render_test.py -- 1,60,120 [width]"""
import os
import sys

import bpy

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import config as C  # noqa: E402

argv = sys.argv[sys.argv.index("--") + 1:]
frames = [int(x) for x in argv[0].split(",")]
w = int(argv[1]) if len(argv) > 1 else 640
sc = bpy.context.scene
sc.render.resolution_x, sc.render.resolution_y = w, w * 9 // 16
sc.eevee.taa_render_samples = 8
os.makedirs(C.P["tests"], exist_ok=True)
for f in frames:
    sc.frame_set(f)
    sc.render.filepath = os.path.join(C.P["tests"], f"t_{f:04d}.png")
    bpy.ops.render.render(write_still=True)
