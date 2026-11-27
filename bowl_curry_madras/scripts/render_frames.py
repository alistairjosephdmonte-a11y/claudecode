"""Renders frames of one scene to PNG (preview/inspection) or EXR (final), skipping frames that already exist.

    blender -b scenes/BOWLCURRY_MADRAS_BLOCKOUT.blend --python scripts/render_frames.py -- \
        <SCENE> <frames "1,37" or "61-276"> <width> <spp> <outdir> [png|png16|exr]

Cameras follow the scene's timeline markers (CAM_A at 1, CAM_B at 241). Renders on CPU (this machine has no GPU).
Prints "FRAME n secs"."""
import os
import sys
import time

import bpy

a = sys.argv[sys.argv.index("--") + 1:]
scn, spec, width, spp, out = a[0], a[1], int(a[2]), int(a[3]), a[4]
fmt = a[5] if len(a) > 5 else "png"
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
sc = bpy.data.scenes[scn]
sc.render.resolution_x, sc.render.resolution_y = width, round(width * 9 / 16)
sc.cycles.samples = spp
sc.render.use_persistent_data = True
sc.cycles.device = "CPU"
s = sc.render.image_settings
if fmt == "exr":
    ext = ".exr"
else:
    if hasattr(s, "media_type"):
        s.media_type = "IMAGE"
    s.file_format, s.color_depth = "PNG", ("16" if fmt == "png16" else "8")
    s.color_mode = "RGB"
    ext = ".png"
    for vl in sc.view_layers:
        vl.use_pass_cryptomatte_object = vl.use_pass_cryptomatte_material = False
        vl.use_pass_vector = vl.use_pass_normal = vl.use_pass_z = False
        vl.use_pass_diffuse_direct = vl.use_pass_diffuse_indirect = False
        vl.use_pass_glossy_direct = vl.use_pass_glossy_indirect = vl.use_pass_emit = False
marks = sorted(sc.timeline_markers, key=lambda m: m.frame)
for f in frames:
    path = os.path.join(out, "frame_%04d%s" % (f, ext))
    if os.path.exists(path) and os.path.getsize(path) > 1000:
        continue
    cams = [m.camera for m in marks if m.frame <= f and m.camera]
    if cams:
        sc.camera = cams[-1]
    sc.frame_set(f)
    if cams:
        sc.camera = cams[-1]
    sc.render.filepath = path
    t = time.time()
    with bpy.context.temp_override(scene=sc):
        bpy.ops.render.render(write_still=True)
    print("FRAME %d %.1fs %s" % (f, time.time() - t, sc.camera.name), flush=True)
