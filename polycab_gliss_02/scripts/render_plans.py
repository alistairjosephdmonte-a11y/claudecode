"""Technical views for the plan / validation sheets (scene modified in memory only, never saved).

    blender -b scenes/POLYCAB_GLISS_02_MASTER.blend --python scripts/render_plans.py -- <outdir> [spp]

  top.png            orthographic plan, ceiling hidden from camera rays only (lighting unchanged), proxies shown
  elev_off/on.png    orthographic gallery-wall elevation from inside the room, Gliss off (f30) / all on (f210)
  prod_front/side/top.png  installed-pose product orthographics (left fixture pose) on a light-grey ground
  plan.json          ortho mappings for the PIL overlays"""
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
sc = bpy.data.scenes["SCENE_ARCHITECTURE"]
sc.cycles.device = "CPU"
sc.cycles.samples = spp
sc.render.use_motion_blur = False
sc.render.resolution_x, sc.render.resolution_y = 1920, 1080
s = sc.render.image_settings
if hasattr(s, "media_type"):
    s.media_type = "IMAGE"
s.file_format, s.color_mode, s.color_depth = "PNG", "RGB", "8"
for vl in sc.view_layers:
    vl.use_pass_cryptomatte_object = vl.use_pass_cryptomatte_material = vl.use_pass_vector = False
    vl.use_pass_z = vl.use_pass_normal = vl.use_pass_emit = False
    vl.use_pass_diffuse_direct = vl.use_pass_diffuse_indirect = False
    vl.use_pass_glossy_direct = vl.use_pass_glossy_indirect = False
    vl.cycles.use_pass_shadow_catcher = False
sc.timeline_markers.clear()
cd = bpy.data.cameras.new("PLAN_CAM")
cd.type = "ORTHO"
cd.clip_end = 100
cam = bpy.data.objects.new("PLAN_CAM", cd)
sc.collection.objects.link(cam)
sc.camera = cam
info = {}


def shoot(name, f, layer="BEAUTY"):
    sc.view_layers["PREVIS"].use = layer == "PREVIS"
    sc.view_layers["BEAUTY"].use = layer == "BEAUTY"
    sc.frame_set(f)
    sc.render.filepath = os.path.join(out, name)
    with bpy.context.temp_override(scene=sc):
        bpy.ops.render.render(write_still=True)


# plan: frame 205 (all on, lean complete), ceiling + curtain track + exterior hidden from the camera
for o in sc.objects:
    if o.name.startswith(("ARCH_Ceiling", "ARCH_Curtain_Track", "EXT_")) or "FloorLamp_Shade" in o.name:
        o.visible_camera = False
sc.view_settings.exposure = 1.2
cam.location = (0.0, 2.9, 20.0)
cam.rotation_euler = (0, 0, 0)
cd.ortho_scale = 7.6
cd.clip_start = 16.95                               # section cut just below the ceiling (z ~3.05)
shoot("top.png", 205, "PREVIS")
info["top"] = {"centre": [0.0, 2.9], "ortho_scale": 7.6, "res": [1920, 1080]}
for o in sc.objects:
    o.visible_camera = True
# gallery-wall elevation from inside the room (camera inside the room at y 0.6: furniture is behind it)
sc.view_settings.exposure = 0.0
cam.location = (0.0, 0.6, 1.5)
cam.rotation_euler = (math.radians(90), 0, math.radians(180))
cd.ortho_scale = 5.4
cd.clip_start = 0.01
shoot("elev_off.png", 30)
shoot("elev_on.png", 210)
info["elev"] = {"centre": [0.0, 1.5], "ortho_scale": 5.4, "res": [1920, 1080],
                "note": "viewed from +Y: image right = -X"}
# product orthographics: the studio product posed like GLISS_LEFT (pan/tilt copied), light-grey ground
st = bpy.data.scenes["STUDIO_PACKSHOT"]
st.cycles.device, st.cycles.samples = "CPU", spp
st.render.use_motion_blur = False
st.render.resolution_x, st.render.resolution_y = 1080, 1080
st.render.image_settings.file_format = "PNG"
st.timeline_markers.clear()
for o in st.objects:
    if o.name.startswith("STUDIO_Sweep"):
        o.hide_render = True
w = bpy.data.worlds.new("ORTHO_GREY")
w.use_nodes = True
w.node_tree.nodes["Background"].inputs["Color"].default_value = (0.55, 0.55, 0.56, 1)
w.node_tree.nodes["Background"].inputs["Strength"].default_value = 1.0
st.world = w
st.view_settings.exposure = 0.0
smi, shi = bpy.data.objects["GLISS_STUDIO_MOUNT"], bpy.data.objects["GLISS_STUDIO_HEAD"]
lmi, lhi = bpy.data.objects["GLISS_LEFT_MOUNT"], bpy.data.objects["GLISS_LEFT_HEAD"]
smi.rotation_euler = lmi.rotation_euler.copy()
shi.rotation_euler = lhi.rotation_euler.copy()
shi.location = lhi.location.copy()
for k in ("rotation_euler", "location"):
    pass
st.frame_set(30)
bpy.context.view_layer.update()
pc = smi.matrix_world.translation + Vector((0, -0.04, -0.07))
pcam = bpy.data.objects.new("ORTHO_PROD_CAM", cd)
st.collection.objects.link(pcam)
st.camera = pcam
cd.ortho_scale = 0.32
cd.clip_start = 0.01
for nm, off, rot in (("prod_front", (0, -2, 0), (math.radians(90), 0, 0)),
                     ("prod_side", (2, 0, 0), (math.radians(90), 0, math.radians(90))),
                     ("prod_top", (0, 0, -2), (math.radians(180), 0, 0))):
    pcam.location = pc + Vector(off)
    pcam.rotation_euler = rot
    st.render.filepath = os.path.join(out, nm + ".png")
    with bpy.context.temp_override(scene=st):
        bpy.ops.render.render(write_still=True)
info["prod"] = {"ortho_scale_m": 0.32, "res": [1080, 1080], "pose": "GLISS_LEFT installed pan/tilt",
                "pan_deg": math.degrees(lmi.rotation_euler.z), "tilt_deg": math.degrees(lhi.rotation_euler.x)}
json.dump(info, open(os.path.join(out, "plan.json"), "w"), indent=1)
print("PLANS_DONE")
