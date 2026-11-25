"""Renders the baked trap sim to deliverables/frames/frame_####.png, skipping frames already on disk.

    blender -b scenes/trap_chain.blend --python scripts/render_frames.py -- <first> <last> <width> <samples>
"""

import os
import sys
import time

import bpy

a = sys.argv[sys.argv.index("--") + 1:]
first, last, width, samples = (int(x) for x in a[:4])
sc = bpy.context.scene
sc.render.resolution_x = width
sc.render.resolution_y = round(width * 9 / 16)
sc.cycles.samples = samples
sc.render.image_settings.file_format = "PNG"
out = os.path.join(os.path.dirname(bpy.data.filepath), "..", "deliverables", "frames")
os.makedirs(out, exist_ok=True)
for f in range(max(first, sc.frame_start), min(last, sc.frame_end) + 1):
    path = os.path.abspath(os.path.join(out, "frame_%04d.png" % f))
    if os.path.exists(path):
        continue
    t = time.time()
    sc.frame_set(f)
    sc.render.filepath = path
    bpy.ops.render.render(write_still=True)
    print("FRAME %d %.1fs" % (f, time.time() - t), flush=True)
