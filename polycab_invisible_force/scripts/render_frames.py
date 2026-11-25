"""Renders chosen frames (or a range) of the hero camera, skipping frames that already exist.

    blender -b scenes/polycab_invisible_force.blend --python scripts/render_frames.py -- <frames> <width> <spp> <outdir> [png16|exr]

<frames> is "1,36,72" or "1-120". Output: <outdir>/frame_####.png (16-bit) or .exr (half float, multilayer off)."""
import os
import sys
import time

import bpy

a = sys.argv[sys.argv.index("--") + 1:]
spec, width, spp, out = a[0], int(a[1]), int(a[2]), a[3]
fmt = a[4] if len(a) > 4 else "png16"
frames = []
for part in spec.split(","):
    if "-" in part:
        f0, f1 = map(int, part.split("-"))
        frames += list(range(f0, f1 + 1))
    else:
        frames.append(int(part))
root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
out = out if os.path.isabs(out) else os.path.join(root, out)
os.makedirs(out, exist_ok=True)
sc = bpy.context.scene
sc.render.resolution_x, sc.render.resolution_y = width, round(width * 9 / 16)
sc.cycles.samples = spp
sc.render.use_persistent_data = True
s = sc.render.image_settings
if fmt == "exr":
    s.file_format, s.color_depth, s.exr_codec = "OPEN_EXR", "16", "DWAA"
    ext = ".exr"
else:
    s.file_format, s.color_depth = "PNG", "16"
    ext = ".png"
for f in frames:
    path = os.path.join(out, "frame_%04d%s" % (f, ext))
    if os.path.exists(path) and os.path.getsize(path) > 1000:
        continue
    sc.frame_set(f)
    sc.render.filepath = path
    t = time.time()
    bpy.ops.render.render(write_still=True)
    print("FRAME %d %.1fs" % (f, time.time() - t), flush=True)
