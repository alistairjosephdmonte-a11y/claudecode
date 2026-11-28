"""Renders frames of one scene to PNG (preview/inspection) or EXR (final), skipping frames that already exist.

    blender -b scenes/POLYCAB_GLISS_02_MASTER.blend --python scripts/render_frames.py -- \
        <SCENE> <frames "1,37" or "61-276"> <width> <spp> <outdir> [png|png16|exr] [previs] [cam=<CAMERA>]

Cameras follow the scene's timeline markers. `previs` renders SCENE_ARCHITECTURE with the PREVIS view layer
(character proxies visible) instead of BEAUTY.
`cam=<CAMERA>` overrides the marker camera (e.g. CAM_01 views of the lighting states). Prints "FRAME n secs"."""
import os
import sys
import time

import bpy

a = sys.argv[sys.argv.index("--") + 1:]
scn, spec, width, spp, out = a[0], a[1], int(a[2]), int(a[3]), a[4]
fmt = a[5] if len(a) > 5 else "png"
previs = "previs" in a[6:]
cam_over = [x[4:] for x in a[6:] if x.startswith("cam=")]
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
if "PREVIS" in sc.view_layers:
    sc.view_layers["PREVIS"].use = previs
    sc.view_layers["BEAUTY"].use = not previs
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
        vl.cycles.use_pass_shadow_catcher = False
marks = sorted(sc.timeline_markers, key=lambda m: m.frame)
if cam_over:                       # render-time marker switching would override the camera
    marks = []
    sc.timeline_markers.clear()
for f in frames:
    path = os.path.join(out, "frame_%04d%s" % (f, ext))
    if os.path.exists(path) and os.path.getsize(path) > 1000:
        continue
    if cam_over:
        cams = [bpy.data.objects[cam_over[0]]]
    else:
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
