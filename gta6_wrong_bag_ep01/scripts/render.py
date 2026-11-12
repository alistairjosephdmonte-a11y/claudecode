"""Renders preview frames (1920x1080 EEVEE) to renders/frames/f_###.png, skipping frames already on disk.
    blender -b scenes/LASTJOB_EP01_WRONG_BAG.blend --python scripts/render.py -- 0 299"""
import os
import sys

import bpy

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import config as C  # noqa: E402

a, b = (int(x) for x in sys.argv[sys.argv.index("--") + 1:][:2])
sc = bpy.context.scene
os.makedirs(C.P["frames"], exist_ok=True)
for f in range(a, b + 1):
    p = os.path.join(C.P["frames"], f"f_{f:03d}.png")
    if os.path.exists(p) and os.path.getsize(p) > 10000:
        continue
    sc.frame_set(f)
    sc.render.filepath = p
    bpy.ops.render.render(write_still=True)
