"""Renders the walkthrough image sequence (all camera paths, cut by timeline markers), skipping existing frames.

    blender -b scenes/residence_master.blend --python scripts/render_walkthrough.py -- <first> <last> <width> <samples>

Frames go to deliverables/walkthrough_render_sequence/frame_####.png; encode with scripts/encode_walkthrough.sh."""
import os
import sys
import time

import bpy

a = sys.argv[sys.argv.index("--") + 1:]
f0, f1, width, spp = int(a[0]), int(a[1]), int(a[2]), int(a[3])
root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
out = os.path.join(root, "deliverables", "walkthrough_render_sequence")
os.makedirs(out, exist_ok=True)
sc = bpy.context.scene
f0, f1 = max(f0, sc.frame_start), min(f1, sc.frame_end)
sc.render.resolution_x, sc.render.resolution_y = width, round(width * 9 / 16)
sc.cycles.samples = spp
sc.cycles.adaptive_threshold = 0.04
sc.render.film_transparent = False
sc.render.use_persistent_data = True
sc.view_settings.exposure = 0.3
sc.render.image_settings.file_format = "PNG"
sc.render.image_settings.color_depth = "8"
for f in range(f0, f1 + 1):
    path = os.path.join(out, "frame_%04d.png" % f)
    if os.path.exists(path) and os.path.getsize(path) > 1000:
        continue
    sc.frame_set(f)
    sc.render.filepath = path
    t = time.time()
    bpy.ops.render.render(write_still=True)
    print("FRAME %d %.1fs" % (f, time.time() - t), flush=True)
