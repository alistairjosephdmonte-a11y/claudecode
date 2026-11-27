"""Isometric overview and top-down layout renders (scene modified in memory only, never saved).

    blender -b scenes/BOWLCURRY_MADRAS_BLOCKOUT.blend --python scripts/render_overview.py -- <outdir> [spp]

Ceiling, front (south) and east walls are hidden from camera rays only, so lighting is unchanged. Writes
<outdir>/iso.png, <outdir>/top.png and <outdir>/top_projection.json (ortho mapping for the plan overlays)."""
import json
import math
import os
import sys

import bpy
from mathutils import Vector

a = sys.argv[sys.argv.index("--") + 1:]
out = a[0]
spp = int(a[1]) if len(a) > 1 else 32
os.makedirs(out, exist_ok=True)
sc = bpy.data.scenes["BC_MADRAS_MASTER"]
sc.cycles.device = "CPU"
sc.cycles.samples = spp
sc.render.use_motion_blur = False
sc.render.resolution_x, sc.render.resolution_y = 1920, 1080
sc.view_settings.exposure = 0.3
s = sc.render.image_settings
if hasattr(s, "media_type"):
    s.media_type = "IMAGE"
s.file_format, s.color_mode, s.color_depth = "PNG", "RGB", "8"
vl = sc.view_layers[0]
vl.use_pass_cryptomatte_object = vl.use_pass_vector = vl.use_pass_z = False
sc.timeline_markers.clear()
sc.frame_set(150)                                     # pour in progress: pouch, stream and sauce visible
for nm in ("ENV_Ceiling", "ENV_Wall_Front", "ENV_Wall_East", "ENV_Exterior_Backdrop"):
    bpy.data.objects[nm].visible_camera = False
for ob in bpy.data.collections["FX_STEAM"].objects:
    ob.hide_render = True
cd = bpy.data.cameras.new("OVERVIEW_CAM")
cd.type = "ORTHO"
cd.clip_end = 100
cam = bpy.data.objects.new("OVERVIEW_CAM", cd)
sc.collection.objects.link(cam)
sc.camera = cam


def shoot(path):
    sc.render.filepath = path
    with bpy.context.temp_override(scene=sc):
        bpy.ops.render.render(write_still=True)


centre = Vector((0.0, 2.75, 0.9))
d = Vector((1.0, -1.15, 1.05)).normalized()
cam.location = centre + d * 25
cam.rotation_euler = (centre - cam.location).to_track_quat("-Z", "Y").to_euler()
cd.ortho_scale = 11.0
shoot(os.path.join(out, "iso.png"))
for ob in sc.objects:
    if "Pendant" in ob.name or ob.name in ("DIN_Plant",):
        ob.visible_camera = False
TOP_C, TOP_S = Vector((0.0, 2.75)), 10.4
cam.location = (TOP_C.x, TOP_C.y, 20.0)
cam.rotation_euler = (0, 0, 0)
cd.ortho_scale = TOP_S
shoot(os.path.join(out, "top.png"))
with open(os.path.join(out, "top_projection.json"), "w") as fh:
    json.dump({"centre": [TOP_C.x, TOP_C.y], "ortho_scale": TOP_S, "res": [1920, 1080]}, fh)
print("OVERVIEW_DONE")
