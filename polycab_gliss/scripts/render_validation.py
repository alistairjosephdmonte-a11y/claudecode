"""Product validation renders (not saved into the .blend; the scene is modified in memory only).

    blender -b scenes/POLYCAB_GLISS_MASTER.blend --python scripts/render_validation.py -- <official_photo.png> <outdir>

1. Silhouette fit: the product is posed floor-standing like the official photograph (base down). Mount yaw, head
   tilt and camera elevation are grid-searched with 1-sample Cycles alpha silhouettes; each silhouette is normalised to
   its bounding box and compared with the photograph's alpha mask (IoU). The best pose is rendered in Cycles and
   written with its mask for overlay compositing (scripts/overlay.py).
2. Orthographic FRONT / SIDE / TOP views of the installed pose (35 deg tilt) on a light-grey studio background.
Writes <outdir>/fit.json with the search results."""
import json
import math
import os
import sys

import bpy
import numpy as np
from mathutils import Vector

a = sys.argv[sys.argv.index("--") + 1:]
photo, out = a[0], a[1]
os.makedirs(out, exist_ok=True)
sc = bpy.data.scenes["SCENE_PRODUCT_STUDIO"]
root = bpy.data.objects["GLISS_MASTER_ROOT"]
piv = root["pivot_depth_m"]


def mask_from_image(path, thr=0.5):
    img = bpy.data.images.load(path, check_existing=False)
    w, h = img.size
    px = np.array(img.pixels[:], dtype=np.float32).reshape(h, w, 4)
    bpy.data.images.remove(img)
    return px[::-1, :, 3] > thr


def norm(mask, n=96):
    ys, xs = np.nonzero(mask)
    y0, y1, x0, x1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
    crop = mask[y0:y1, x0:x1].astype(np.float32)
    yi = (np.arange(n) + 0.5) * crop.shape[0] / n
    xi = (np.arange(n) + 0.5) * crop.shape[1] / n
    return crop[yi.astype(int)][:, xi.astype(int)] > 0.5, (x1 - x0) / (y1 - y0)


ref, ref_aspect = norm(mask_from_image(photo))

# temporary pose: floor-standing instance pair at the origin, everything else hidden
master = set(bpy.data.collections["GLISS_MASTER_MOUNT"].objects) | set(bpy.data.collections["GLISS_MASTER_HEAD"].objects)
for o in sc.objects:
    if o not in master:                        # instanced parts must stay renderable
        o.hide_render = True
mi = bpy.data.objects.new("VALID_MOUNT", None)
mi.instance_type = "COLLECTION"
mi.instance_collection = bpy.data.collections["GLISS_MASTER_MOUNT"]
hi = bpy.data.objects.new("VALID_HEAD", None)
hi.instance_type = "COLLECTION"
hi.instance_collection = bpy.data.collections["GLISS_MASTER_HEAD"]
hi.parent = mi
hi.location = (0, 0, -piv)
for o in (mi, hi):
    sc.collection.objects.link(o)
cd = bpy.data.cameras.new("VALID_CAM")
cam = bpy.data.objects.new("VALID_CAM", cd)
sc.collection.objects.link(cam)
sc.camera = cam
sc.timeline_markers.clear()
cd.lens = 85
cd.dof.use_dof = False
sc.render.use_motion_blur = False
centre = Vector((0, 0, 0.085))


def place_camera(elev, dist=1.6, ortho=None, view=None):
    if view:
        d = {"FRONT": Vector((0, 1, 0)), "SIDE": Vector((1, 0, 0)), "TOP": Vector((0, 0.0001, 1))}[view]
    else:
        e = math.radians(elev)
        d = Vector((0, -math.cos(e), math.sin(e)))
    cam.location = centre + d.normalized() * dist
    cam.rotation_euler = (centre - cam.location).to_track_quat("-Z", "Y").to_euler()
    cd.type = "ORTHO" if ortho else "PERSP"
    if ortho:
        cd.ortho_scale = ortho


def faces_camera():
    """The photograph shows the reflector face toward the viewer: reject poses whose optical axis points away."""
    ax = (mi.matrix_basis @ hi.matrix_basis).to_3x3() @ Vector((0, 0, -1))
    return ax.normalized().dot((cam.location - centre).normalized()) > 0.25


def silhouette(path):
    with bpy.context.temp_override(scene=sc):
        sc.render.filepath = path
        bpy.ops.render.render(write_still=True)
    return mask_from_image(path)


# --- 1. silhouette grid search (1-sample Cycles alpha)
sc.render.engine = "CYCLES"                  # Workbench/EEVEE need OpenGL, unavailable headless here
sc.cycles.samples = 1
sc.cycles.use_adaptive_sampling = False
sc.cycles.use_denoising = False
sc.cycles.max_bounces = 0
sc.render.film_transparent = True
for vl in sc.view_layers:
    vl.use_pass_cryptomatte_object = vl.use_pass_cryptomatte_material = False
    vl.use_pass_vector = vl.use_pass_normal = vl.use_pass_z = False
s = sc.render.image_settings
if hasattr(s, "media_type"):
    s.media_type = "IMAGE"
s.file_format, s.color_mode, s.color_depth = "PNG", "RGBA", "8"
sc.render.resolution_x = sc.render.resolution_y = 160
mi.rotation_euler = (math.pi, 0, 0)          # base on the floor, stem up
best = None
results = []
tmp = os.path.join(out, "_sil.png")
for yaw in range(-180, 180, 20):
    for tilt in range(20, 81, 10):
        for elev in (0, 12, 24, 36):
            mi.rotation_euler = (math.pi, 0, math.radians(yaw))
            hi.rotation_euler = (math.radians(tilt), 0, 0)
            place_camera(elev)
            m, asp = norm(silhouette(tmp))
            iou = float((m & ref).sum() / max(1, (m | ref).sum()))
            score = iou - 0.5 * abs(math.log(asp / ref_aspect)) - (0.0 if faces_camera() else 1.0)
            results.append((score, iou, yaw, tilt, elev))
            if best is None or score > best[0]:
                best = (score, iou, yaw, tilt, elev)
# refine around the best
_, _, y0, t0, e0 = best
for yaw in range(y0 - 10, y0 + 11, 5):
    for tilt in range(t0 - 6, t0 + 7, 3):
        for elev in range(max(0, e0 - 8), e0 + 9, 4):
            mi.rotation_euler = (math.pi, 0, math.radians(yaw))
            hi.rotation_euler = (math.radians(tilt), 0, 0)
            place_camera(elev)
            m, asp = norm(silhouette(tmp))
            iou = float((m & ref).sum() / max(1, (m | ref).sum()))
            score = iou - 0.5 * abs(math.log(asp / ref_aspect)) - (0.0 if faces_camera() else 1.0)
            if score > best[0]:
                best = (score, iou, yaw, tilt, elev)
os.remove(tmp)
score, iou, yaw, tilt, elev = best
with open(os.path.join(out, "fit.json"), "w") as f:
    json.dump({"best": {"score": score, "iou": iou, "yaw_deg": yaw, "head_tilt_deg": tilt, "camera_elev_deg": elev},
               "reference_aspect": ref_aspect,
               "note": "IoU of bounding-box-normalised silhouettes (96 x 96). Pose solved, not measured."}, f, indent=1)
print("FIT", best)

# --- 2. Cycles render of the best pose (+ mask) for the overlay
mi.rotation_euler = (math.pi, 0, math.radians(yaw))
hi.rotation_euler = (math.radians(tilt), 0, 0)
place_camera(elev)
sc.render.resolution_x = sc.render.resolution_y = 800
silhouette(os.path.join(out, "fit_mask.png"))
sc.cycles.samples = 64
sc.cycles.max_bounces = 8
sc.cycles.use_adaptive_sampling = True
sc.cycles.use_denoising = True
for n in ("LGT_STUDIO_KEY_SOFTBOX", "LGT_STUDIO_RIM_CHAMPAGNE", "LGT_STUDIO_FILL"):
    lt = bpy.data.objects[n]
    lt.hide_render = False
    lt.location = lt.location - Vector((0, 0, 1.30)) * 0 + Vector((0, 0, 0))
w = bpy.data.worlds.new("VALID_WORLD")
w.use_nodes = True
w.node_tree.nodes["Background"].inputs["Color"].default_value = (0.8, 0.8, 0.8, 1)
w.node_tree.nodes["Background"].inputs["Strength"].default_value = 1.0
sc.world = w
for n in ("LGT_STUDIO_KEY_SOFTBOX", "LGT_STUDIO_RIM_CHAMPAGNE", "LGT_STUDIO_FILL"):
    lt = bpy.data.objects[n]
    lt.location.z -= 1.30 - 0.085            # studio rig was built around the product at z = 1.3
for k in mi.keys():
    pass
hi["cob_on"] = 1.0                            # photograph shows the COB face lit/yellow
with bpy.context.temp_override(scene=sc):
    sc.render.filepath = os.path.join(out, "fit_render.png")
    bpy.ops.render.render(write_still=True)

# --- 3. orthographic validation views of the installed pose
mi.rotation_euler = (0, 0, 0)
hi.rotation_euler = (math.radians(35), 0, 0)
sc.render.film_transparent = False
s.color_mode = "RGB"
sc.render.resolution_x, sc.render.resolution_y = 1600, 1200
for lt in ("LGT_STUDIO_KEY_SOFTBOX", "LGT_STUDIO_RIM_CHAMPAGNE", "LGT_STUDIO_FILL"):
    bpy.data.objects[lt].location.z += 0.0
hi["cob_on"] = 0.0
reg = json.loads(root["dimension_register_json"])
dmm = {k: v["value"] / 1000 for k, v in reg["dimensions_mm"].items()}
R, L = dmm["housing_outer_diameter"] / 2, dmm["housing_length"]
pr = min(dmm["pivot_offset"], L * 0.6)
hc = (mi.matrix_basis @ hi.matrix_basis) @ Vector((0, -R, (pr - (L - pr)) / 2))
centre = (Vector((0, 0, -dmm["mounting_base_thickness"] / 2)) + hc) / 2
w.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.35
for view in ("FRONT", "SIDE", "TOP"):
    place_camera(0, dist=1.0, ortho=0.32, view=view)
    with bpy.context.temp_override(scene=sc):
        sc.render.filepath = os.path.join(out, "ortho_%s.png" % view)
        bpy.ops.render.render(write_still=True)
    print("ORTHO", view, cam.location[:])
print("VALIDATION_DONE")
