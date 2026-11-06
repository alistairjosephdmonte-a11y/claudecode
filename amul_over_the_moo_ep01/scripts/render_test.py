"""Quick Cycles test renders of chosen frames.  blender -b scenes/AMUL_OTM_EP01_MASTER.blend --python scripts/render_test.py -- 50,130 [640 8]"""
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy  # noqa: E402

import config as C  # noqa: E402

a = sys.argv[sys.argv.index("--") + 1:]
frames = [int(v) for v in a[0].split(",")]
w = int(a[1]) if len(a) > 1 else 640
spp = int(a[2]) if len(a) > 2 else 8
sc = bpy.context.scene
sc.render.resolution_x, sc.render.resolution_y = w, w * 9 // 16
sc.cycles.samples = spp
sc.render.image_settings.color_depth = "8"
for f in frames:
    sc.frame_set(f)
    sc.render.filepath = os.path.join(C.P["tests"], f"t_{f:04d}.png")
    t = time.time()
    bpy.ops.render.render(write_still=True)
    print("TEST", f, round(time.time() - t, 1))
