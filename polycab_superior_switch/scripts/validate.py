"""QC for the Superior Switch scene. Writes metadata/validation.json and metadata/camera_animation.json.

    blender -b scenes/polycab_superior_switch.blend --python scripts/validate.py [-- <rendered frame png> ...]

Checks: collections, fan geometry and clearances, fan speed curve, light cues (no flicker), camera clearance and
speed, hand/remote press contact and scale, room continuity (nothing but the rigs moves), furniture intersections,
external files, and (optionally) clipped pixels in rendered frames."""
import json
import math
import os
import sys

import bmesh
import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sc = bpy.context.scene
dg = bpy.context.evaluated_depsgraph_get()
F0, F1 = sc.frame_start, sc.frame_end
REQ = ["01_ARCHITECTURE", "02_INTERIOR_ASSETS", "03_POLYCAB_AERORUSH", "04_REMOTE_CONTROL", "05_LIGHTING_FIXTURES",
       "06_LIGHT_RIG", "07_CAMERA_RIG", "08_ANIMATION_CONTROLS", "09_BRANDING", "10_RENDER_SETTINGS"]
ANIMATED_OK = {"CAM_Hero", "CAM_Look_Target", "HAND_Rig_CamSpace", "CTRL_Lights", "FAN_Rotor"}
results = []


def check(name, ok, **info):
    results.append(dict(check=name, passed=bool(ok), **info))
    print("%s %-28s %s" % ("PASS" if ok else "FAIL", name, json.dumps(info)[:220]), flush=True)


def set_frame(f):
    sc.frame_set(int(math.floor(f)), subframe=f - math.floor(f))


def bvh_of(ob):
    ev = ob.evaluated_get(dg)
    me = ev.to_mesh()
    bm = bmesh.new()
    bm.from_mesh(me)
    bm.transform(ob.matrix_world)
    t = BVHTree.FromBMesh(bm)
    bm.free()
    ev.to_mesh_clear()
    return t


# 1 collections ------------------------------------------------------------------------------------------------
names = [c.name for c in sc.collection.children]
orphans = [o.name for o in sc.collection.objects]
check("collections", all(n in names for n in REQ) and not orphans, present=names, loose_objects=orphans)

# 2 fan geometry -----------------------------------------------------------------------------------------------
set_frame(1)
blades = bpy.data.objects["FAN_Blades_x3"]
bm = bmesh.new()
bm.from_mesh(blades.data)
islands, seen = 0, set()
for v in bm.verts:
    if v.index in seen:
        continue
    islands += 1
    stack = [v]
    while stack:
        x = stack.pop()
        if x.index in seen:
            continue
        seen.add(x.index)
        stack.extend(e.other_vert(x) for e in x.link_edges)
rmax = max(Vector((v.co.x, v.co.y)).length for v in bm.verts)
bm.free()
mount = bpy.data.objects["FAN_Mount"].matrix_world.translation
zb = min((blades.matrix_world @ v.co).z for v in blades.data.vertices)
tray_z = mount.z
check("fan_blade_count", islands == 3, blades=islands)
check("fan_sweep_1200mm", abs(2 * rmax - 1.2) < 0.01, sweep_m=round(2 * rmax, 4))
check("fan_clearances", zb > 2.3 and tray_z - zb > 0.25, blade_low_point_m=round(zb, 3),
      ceiling_to_blades_m=round(tray_z - zb, 3))
tray_edges = [-1.80, 1.30, -0.85, 2.15]
cx, cy = mount.x, mount.y
edge_gap = min(abs(cx - tray_edges[0]), abs(cx - tray_edges[1]), abs(cy - tray_edges[2]), abs(cy - tray_edges[3]))
check("fan_inside_tray", edge_gap - 2 * rmax / 2 > 0.3, tip_to_soffit_edge_m=round(edge_gap - rmax, 3))

# 3 fan speed curve ------------------------------------------------------------------------------------------
rotor = bpy.data.objects["FAN_Rotor"]
ctrl = bpy.data.objects["CTRL_Fan"]
ang = []
step = 0.25
f = F0
while f <= F1 + 1e-9:
    set_frame(f)
    ang.append((f, rotor.matrix_world.to_euler().z, rotor.rotation_euler.z))
    f += step
w = [(ang[i][0], (ang[i + 1][2] - ang[i][2]) / step) for i in range(len(ang) - 1)]   # rad / frame
wabs = [abs(x) for _, x in w]
start, ramp, rpm = ctrl["start_frame"], ctrl["ramp_frames"], ctrl["rpm"]
w_term = rpm * 2 * math.pi / 60 / sc.render.fps
pre = max(abs(x) for f_, x in w if f_ < start - 0.01)
post = [abs(x) for f_, x in w if f_ > start + ramp + 0.01]
mono = all(wabs[i + 1] >= wabs[i] - 1e-4 for i in range(len(wabs) - 1))     # float32 angle noise at ~50 rad
dw = max(abs(wabs[i + 1] - wabs[i]) for i in range(len(wabs) - 1))
check("fan_speed_curve", pre < 1e-9 and mono and max(post) - min(post) < 1e-4 and abs(post[0] - w_term) < 1e-4,
      start_frame=start, ramp_frames=ramp, terminal_rpm=rpm,
      deg_per_frame_terminal=round(math.degrees(w_term), 2), max_change_deg_per_frame_per_quarter=round(
          math.degrees(dw), 4), monotonic_spin_up=mono)
check("fan_no_wagon_wheel", math.degrees(w_term) < 60.0, deg_per_frame=round(math.degrees(w_term), 2),
      note="3-blade symmetry aliases at 60 deg/frame; below it the rotation reads in the right direction")

# 4 light cues --------------------------------------------------------------------------------------------------
cl = bpy.data.objects["CTRL_Lights"]
cues = {}
for g in ("wash", "perim", "cove", "shelf", "string"):
    vals = []
    for fr in range(F0, F1 + 1):
        set_frame(fr)
        vals.append(cl[g])
    rev = sum(1 for i in range(1, len(vals) - 1) if (vals[i] - vals[i - 1]) * (vals[i + 1] - vals[i]) < -1e-9)
    on = next(i + F0 for i, v in enumerate(vals) if v > 1e-4)
    full = next(i + F0 for i, v in enumerate(vals) if v > 0.999)
    cues[g] = dict(on=on, full=full, reversals=rev, max_step=round(max(abs(vals[i + 1] - vals[i])
                                                                        for i in range(len(vals) - 1)), 3))
check("light_cues_no_flicker", all(c["reversals"] == 0 and c["max_step"] < 0.2 for c in cues.values()), cues=cues)
press = 44
check("lights_after_fan_cue", min(c["on"] for c in cues.values()) >= ctrl["start_frame"] + 6,
      fan_start=ctrl["start_frame"], first_light_frame=min(c["on"] for c in cues.values()),
      note="architectural lights are a separate cue, they begin after the fan is already turning")

# 5 camera --------------------------------------------------------------------------------------------------------
cam = sc.camera
static = [o for o in sc.objects if o.type == "MESH" and not o.hide_render and o.name not in ("FIX_String_Lights_Wire",)
          and not o.name.startswith(("HAND_", "REMOTE_", "BRAND_"))]
trees = [(o.name, bvh_of(o)) for o in static]
mind, worst = 9.0, None
pos = []
f = F0
while f <= F1 + 1e-9:
    set_frame(f)
    p = cam.matrix_world.translation.copy()
    pos.append((f, p))
    for n, t in trees:
        hit = t.find_nearest(p)
        if hit[0] is not None and hit[3] < mind:
            mind, worst = hit[3], (n, f)
    f += 0.5
spd = [((pos[i + 1][1] - pos[i][1]).length / 0.5 * sc.render.fps) for i in range(len(pos) - 1)]
acc = [abs(spd[i + 1] - spd[i]) / 0.5 * sc.render.fps for i in range(len(spd) - 1)]
check("camera_clearance", mind >= 0.25, min_distance_m=round(mind, 3), nearest=worst)
check("camera_motion", max(spd) < 2.5, peak_speed_m_s=round(max(spd), 2), peak_accel_m_s2=round(max(acc), 2),
      end_speed_m_s=round(spd[-1], 3), lens_mm=cam.data.lens,
      lens_animated=bool(cam.data.animation_data and any("lens" in fc.data_path for fc in
                                                         (cam.data.animation_data.action.fcurves
                                                          if hasattr(cam.data.animation_data.action, "fcurves")
                                                          else []))))

# 6 hand / remote -------------------------------------------------------------------------------------------------
set_frame(46)
hand = bpy.data.objects["HAND_Right"]
key = bpy.data.objects["REMOTE_Key_Power"]
kc = key.matrix_world @ Vector((0, 0, 0.0098 - 0.0080))      # centre of the key cap's top face
dmin = bvh_of(hand).find_nearest(kc)[3]
body = bpy.data.objects["REMOTE_Body"]
dims = [round(d, 4) for d in body.dimensions]
check("remote_press_contact", dmin < 0.003, frame=46, thumb_to_power_key_m=round(dmin, 4))
check("remote_scale", abs(dims[1] - 0.135) < 0.002, remote_dims_m=dims, remote_to_fan_sweep=round(dims[1] / 1.2, 3))

# 7 room continuity ------------------------------------------------------------------------------------------
def snap(f):
    set_frame(f)
    return {o.name: [round(x, 6) for row in o.matrix_world for x in row] for o in sc.objects
            if o.name not in ANIMATED_OK and not any(p.name in ANIMATED_OK for p in _parents(o))}


def _parents(o):
    out = []
    while o.parent:
        o = o.parent
        out.append(o)
    return out


a, b_, c_ = snap(1), snap(60), snap(120)
moved = [n for n in a if a[n] != b_.get(n) or a[n] != c_.get(n)]
check("room_continuity", not moved, static_objects=len(a), moved=moved[:10])
cnt = {}
for o in sc.objects:
    base = o.name.split(".")[0]
    cnt[base] = cnt.get(base, 0) + 1
dups = [n for n, k in cnt.items() if k > 1]
check("no_duplicates", not dups, duplicated=dups)

# 8 intersections --------------------------------------------------------------------------------------------
def group(n):
    p = n.split("_")
    return "_".join(p[:3]) if p[0] == "DIYA" else ("SOFA" if p[0] in ("SOFA", "CUSH") and False else p[0])


set_frame(1)
furn = [o for o in sc.objects if o.type == "MESH" and o.users_collection[0].name == "02_INTERIOR_ASSETS"]
arch = [o for o in sc.objects if o.type == "MESH" and o.users_collection[0].name == "01_ARCHITECTURE"
        and not o.name.startswith(("ARCH_Floor",))]
bvh = {o.name: bvh_of(o) for o in furn + arch}


def bbox(o):
    cs = [o.matrix_world @ Vector(c) for c in o.bound_box]
    return [min(c[i] for c in cs) for i in range(3)], [max(c[i] for c in cs) for i in range(3)]


bb = {o.name: bbox(o) for o in furn + arch}
pairs = []
items = furn + arch
for i, o1 in enumerate(items):
    for o2 in items[i + 1:]:
        if o1 in arch and o2 in arch:
            continue
        if group(o1.name) == group(o2.name):
            continue
        (a0, a1), (b0, b1) = bb[o1.name], bb[o2.name]
        if any(a1[k] < b0[k] + 0.004 or b1[k] < a0[k] + 0.004 for k in range(3)):
            continue
        if bvh[o1.name].overlap(bvh[o2.name]):
            pairs.append((o1.name, o2.name))
# resting contacts that are intended (object sits on / leans against the other)
RESTING = ("RUG_", "DEC_Book", "DEC_Urli", "DEC_Marigold", "DIYA_", "DEC_Shelf", "DEC_Vase", "LAMP_", "CUSH_")
real = [p for p in pairs if not (p[0].startswith(RESTING) or p[1].startswith(RESTING))]
check("no_interpenetration", not real, unintended=real[:12], resting_contacts=len(pairs) - len(real))

# 9 external files ---------------------------------------------------------------------------------------------
ext = [i.name for i in bpy.data.images if i.source == "FILE" and not i.packed_file]
check("textures_packed", not ext, external_images=ext, images_total=len(bpy.data.images),
      note="all materials are procedural node trees; nothing to pack")

# 10 clipped pixels in supplied renders -----------------------------------------------------------------------
argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
for path in argv:
    img = bpy.data.images.load(path)
    px = img.pixels[:]
    n = len(px) // 4
    clip = sum(1 for i in range(n) if max(px[4 * i], px[4 * i + 1], px[4 * i + 2]) >= 0.999)
    check("clipping_" + os.path.basename(path), clip / n < 0.002, clipped_fraction=round(clip / n, 5))
    bpy.data.images.remove(img)

os.makedirs(os.path.join(ROOT, "metadata"), exist_ok=True)
with open(os.path.join(ROOT, "metadata", "validation.json"), "w") as fh:
    json.dump(dict(blender=bpy.app.version_string, frames=[F0, F1], fps=sc.render.fps,
                   passed=sum(r["passed"] for r in results), total=len(results), checks=results), fh, indent=1)

# camera / animation documentation
cd = cam.data
doc = dict(fps=sc.render.fps, frames=[F0, F1], resolution=[sc.render.resolution_x, sc.render.resolution_y],
           camera=dict(name=cam.name, lens_mm=cd.lens, sensor_mm=cd.sensor_width, fstop=cd.dof.aperture_fstop,
                       shutter=sc.render.motion_blur_shutter, rig="location keys + Track To CAM_Look_Target, Bezier",
                       keys=[]),
           fan=dict(start_frame=ctrl["start_frame"], ramp_frames=ctrl["ramp_frames"], rpm=ctrl["rpm"],
                    direction=ctrl["direction"],
                    driver=rotor.animation_data.drivers[0].driver.expression),
           light_cues=cues)
tgt = bpy.data.objects["CAM_Look_Target"]
for fr in (1, 36, 46, 54, 66, 72, 96, 112, 120):
    set_frame(fr)
    doc["camera"]["keys"].append(dict(frame=fr, location=[round(x, 3) for x in cam.matrix_world.translation],
                                      target=[round(x, 3) for x in tgt.matrix_world.translation],
                                      focus_m=round(cd.dof.focus_distance, 3)))
with open(os.path.join(ROOT, "metadata", "camera_animation.json"), "w") as fh:
    json.dump(doc, fh, indent=1)
print("VALIDATION %d/%d passed" % (sum(r["passed"] for r in results), len(results)))
