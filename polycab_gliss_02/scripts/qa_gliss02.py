"""QA for POLYCAB_GLISS_02_MASTER.blend. Writes metadata/GLISS_02_QA_REPORT.json, metadata/camera_paths.json and
metadata/GLISS_02_PRODUCT_DIMENSION_REGISTER.json (deliverables copy).

    blender -b scenes/POLYCAB_GLISS_02_MASTER.blend --python scripts/qa_gliss02.py"""
import json
import math
import os
import sys

import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
arch = bpy.data.scenes["SCENE_ARCHITECTURE"]
studio = bpy.data.scenes["STUDIO_PACKSHOT"]
walk = bpy.data.scenes["SCENE_WALKTHROUGH"]
edit = bpy.data.scenes["SCENE_MASTER_EDIT"]
results = []
CEIL, ART_Y, ART_Z = 3.0, 0.04, 1.6


def MX(x):
    return -x


def check(name, ok, detail):
    results.append({"check": name, "pass": bool(ok), "detail": detail})
    print("QA", "PASS" if ok else "FAIL", name, json.dumps(detail)[:220], flush=True)


VL = {"SCENE_ARCHITECTURE": "PREVIS", "SCENE_WALKTHROUGH": None, "STUDIO_PACKSHOT": None}


def vlayer(sc):
    nm = VL.get(sc.name)
    return sc.view_layers[nm] if nm else sc.view_layers[0]


def solids(sc, with_proxies=True):
    out = []
    for o in vlayer(sc).objects:
        if o.type != "MESH" or o.name.startswith("EXT_"):
            continue
        if not with_proxies and any(c.name == "09_CHARACTER_PROXIES" for c in o.users_collection):
            continue
        out.append(o)
    return out


LAST = {}


def bvh_at(sc, f, objs):
    with bpy.context.temp_override(scene=sc, view_layer=vlayer(sc)):
        sc.frame_set(f)
        dg = bpy.context.evaluated_depsgraph_get()
    dg.update()
    LAST["dg"] = dg
    verts, polys = [], []
    for o in objs:
        oe = o.evaluated_get(dg)
        me = oe.to_mesh()
        mw = oe.matrix_world
        base = len(verts)
        verts += [mw @ v.co for v in me.vertices]
        polys += [[base + i for i in p.vertices] for p in me.polygons]
        oe.to_mesh_clear()
    return BVHTree.FromPolygons(verts, polys)


def marker_cam(sc, f):
    ms = sorted((m.frame, m.camera) for m in sc.timeline_markers if m.camera)
    return [c for fr, c in ms if fr <= f][-1]


# ---------------------------------------------------------------- runtime / organisation
for sc in (arch, studio, edit):
    r = sc.render
    check("runtime %s: frames 1-360 @ 24 fps, 3840x2160" % sc.name,
          (sc.frame_start, sc.frame_end, r.fps, r.resolution_x, r.resolution_y) == (1, 360, 24, 3840, 2160),
          [sc.frame_start, sc.frame_end, r.fps, r.resolution_x, r.resolution_y])
strips = sorted((s.frame_final_start, s.frame_final_end - 1, s.name) for s in edit.sequence_editor.strips)
cont = strips[0][0] == 1 and strips[-1][1] == 360 and all(strips[i][1] + 1 == strips[i + 1][0]
                                                          for i in range(len(strips) - 1))
check("edit: 10 contiguous shot strips covering exactly 1-360", cont and len(strips) == 10,
      [s[:2] for s in strips])
walk_ok = (walk.frame_start, walk.frame_end, walk.render.fps) == (1, 240, 24)
check("walkthrough: 240 frames @ 24 fps (10 s)", walk_ok, [walk.frame_start, walk.frame_end])
need = ["00_REFERENCE_ASSETS", "01_ARCHITECTURE", "02_FURNITURE", "03_LIFESTYLE_PROPS", "04_GALLERY_ARTWORK",
        "05_GLISS_MASTER", "06_GLISS_INSTANCES", "07_AMBIENT_LIGHTING", "08_ACCENT_LIGHTING",
        "09_CHARACTER_PROXIES", "10_CINEMATIC_CAMERAS", "11_STUDIO_PACKSHOT", "12_RENDER_PASSES"]
missing = [c for c in need if c not in bpy.data.collections]
check("scene organisation: the 13 brief collections exist", not missing, missing)

# ---------------------------------------------------------------- product + installation
root = bpy.data.objects["GLISS_MASTER_02"]
reg = json.loads(root["dimension_register_json"])
inst = [o for o in bpy.data.objects if o.instance_type == "COLLECTION" and o.instance_collection
        and o.instance_collection.name in ("GLISS_MASTER_MOUNT", "GLISS_MASTER_HEAD")]
check("every Gliss is a linked instance of the one master (mount + head collections)",
      len(inst) == 2 * 7, sorted(o.name for o in inst))
check("manufacturer dimensions remain unverified (all null, nothing certified)",
      all(v is None for v in reg["verified_manufacturer_dimensions_mm"].values()),
      {"world_scale_housing_diameter_mm": reg["world_scale_housing_diameter_mm"]})
head_c = bpy.data.collections["GLISS_MASTER_HEAD"]
mount_c = bpy.data.collections["GLISS_MASTER_MOUNT"]
arch.frame_set(200)
aim = []
for nm, tx in (("GLISS_LEFT", MX(-1.1)), ("GLISS_CENTRE", 0.0), ("GLISS_RIGHT", MX(1.1))):
    mi, hi, sp = (bpy.data.objects[nm + s] for s in ("_MOUNT", "_HEAD", "_SPOT"))
    mw = mi.matrix_world
    hw = hi.matrix_world
    zmax_head = max((hw @ o.matrix_world @ Vector(c)).z for o in head_c.objects if o.type == "MESH"
                    for c in o.bound_box)
    ztop_mount = max((mw @ o.matrix_world @ Vector(c)).z for o in mount_c.objects if o.type == "MESH"
                     for c in o.bound_box)
    emit = sp.matrix_world.translation
    axis = (sp.matrix_world.to_3x3() @ Vector((0, 0, -1))).normalized()
    t = (ART_Y - emit.y) / axis.y
    hit = emit + axis * t
    tgt = Vector((tx, ART_Y, ART_Z))
    aim.append({"fixture": nm, "mount_top_z": round(ztop_mount, 5), "head_max_z": round(zmax_head, 4),
                "emitter": [round(v, 4) for v in emit], "axis": [round(v, 4) for v in axis],
                "axis_hit_on_artwork_plane": [round(v, 4) for v in hit], "miss_mm": round((hit - tgt).length * 1000, 2),
                "tilt_from_vertical_deg": round(math.degrees(math.acos(-axis.z)), 2),
                "beam_angle_deg": round(math.degrees(sp.data.spot_size), 1),
                "setback_m": round(mi.location.y, 3)})
check("fixture bases flush to the ceiling (mounting face at z = 3.000)",
      all(abs(a["mount_top_z"] - CEIL) < 0.0005 for a in aim), [a["mount_top_z"] for a in aim])
check("optical housings clear the ceiling (head max z < ceiling - 1 mm)", all(a["head_max_z"] < CEIL - 0.001
                                                                           for a in aim), [a["head_max_z"] for a in aim])
check("optical axes through each emitter hit the artwork centres (miss < 1 mm)",
      all(a["miss_mm"] < 1.0 for a in aim), aim)
st_ok, st_det = True, {}
table = [((1, 84), (0, 0, 0)), ((85, 108), (1, 0, 0)), ((109, 126), (1, 1, 0)), ((127, 276), (1, 1, 1))]
spots = [bpy.data.objects[n + "_SPOT"] for n in ("GLISS_LEFT", "GLISS_CENTRE", "GLISS_RIGHT")]
heads = [bpy.data.objects[n + "_HEAD"] for n in ("GLISS_LEFT", "GLISS_CENTRE", "GLISS_RIGHT")]
for (f0, f1), want in table:
    for f in range(f0, f1 + 1):
        arch.frame_set(f)
        got = tuple(int(round(s["on"])) for s in spots)
        cob = tuple(int(round(h["cob_on"])) for h in heads)
        if got != want or cob != want:
            st_ok = False
            st_det.setdefault("bad", []).append(f)
    st_det["%d-%d" % (f0, f1)] = list(want)
check("Gliss switching follows the brief (L 85, C 109, R 127; spot and COB together; no flicker)", st_ok, st_det)


def light_state(f):
    arch.frame_set(f)
    return {o.name: (round(o.data.energy, 4), tuple(round(c, 4) for c in o.data.color))
            for o in arch.objects if o.type == "LIGHT" and not o.name.startswith("GLISS_")}


a84, a85, a127, a276 = light_state(84), light_state(85), light_state(127), light_state(276)
vs = arch.view_settings
def scene_fcurves(sc):
    ad = sc.animation_data
    if not ad or not ad.action:
        return []
    out = []
    for lay in ad.action.layers:
        for stp in lay.strips:
            for cb in stp.channelbags:
                out += list(cb.fcurves)
    return out


anim_vs = any("view_settings" in fc.data_path for fc in scene_fcurves(arch))
check("ambient light, exposure and white balance identical in every state", a84 == a85 == a127 == a276
      and not anim_vs, {"lights": len(a84), "view_transform": vs.view_transform, "look": vs.look,
                        "exposure": vs.exposure, "white_balance": vs.use_white_balance})
photo_anim = [o.name for o in bpy.data.objects if o.name.endswith("_Photograph") and o.animation_data]
photo_anim += [m.name for m in bpy.data.materials if m.name.startswith("MAT_MEMORY") and m.node_tree.animation_data]
check("photographs static (no object or material animation)", not photo_anim, photo_anim)

# ---------------------------------------------------------------- characters
with bpy.context.temp_override(scene=arch, view_layer=vlayer(arch)):
    arch.frame_set(204)
    dg = bpy.context.evaluated_depsgraph_get()


def world_bb(name):
    o = bpy.data.objects[name].evaluated_get(dg)
    pts = [o.matrix_world @ Vector(c) for c in o.bound_box]
    return Vector([min(p[i] for p in pts) for i in range(3)]), Vector([max(p[i] for p in pts) for i in range(3)])


seat_top = max((bpy.data.objects["SOFA_MAIN_Seat_Cushion_%d" % i].matrix_world @ Vector(c)).z
               for i in range(3) for c in bpy.data.objects["SOFA_MAIN_Seat_Cushion_%d" % i].bound_box)
seat = {}
for pid in ("FEM_01", "MAL_01"):
    pel = world_bb(pid + "_Pelvis")[0].z
    feet = min(world_bb(pid + "_Foot_" + s)[0].z for s in ("L", "R"))
    seat[pid] = {"pelvis_sink_mm": round((seat_top - pel) * 1000, 1), "foot_bottom_mm": round(feet * 1000, 1)}
check("seating: pelvis settles 0-40 mm into the cushion, feet on the floor (0-25 mm)",
      all(0 <= v["pelvis_sink_mm"] <= 40 and 0 <= v["foot_bottom_mm"] <= 25 for v in seat.values()), seat)
fh = bpy.data.objects["FEM_01_Head"].evaluated_get(dg)
fhc = fh.matrix_world @ Vector((0, 0, sum(v.co.z for v in fh.data.vertices) / len(fh.data.vertices)))
fem_head = bvh_at(arch, 204, [bpy.data.objects["FEM_01_Head"]])
mal_parts = bvh_at(arch, 204, [bpy.data.objects[n] for n in ("MAL_01_Torso", "MAL_01_UpperArm_L",
                                                            "MAL_01_UpperArm_R", "MAL_01_Head")])
ov = fem_head.overlap(mal_parts)
mal_sh = bvh_at(arch, 204, [bpy.data.objects[n] for n in ("MAL_01_UpperArm_L", "MAL_01_UpperArm_R",
                                                           "MAL_01_Torso")])
near = mal_sh.find_nearest(fhc)
fhv = [fh.matrix_world @ v.co for v in fh.data.vertices]
gap = min(mal_sh.find_nearest(p)[3] for p in fhv)
mh = bvh_at(arch, 204, [bpy.data.objects["MAL_01_Head"]])
head_clash = bool(fem_head.overlap(mh))
check("shot 07 contact: FEM_01 head rests on MAL_01 shoulder (gap <= 15 mm, heads do not intersect)",
      gap <= 0.015 and not head_clash, {"gap_mm": round(gap * 1000, 1), "head_overlap": head_clash,
                                        "lean_deg": round(bpy.data.objects["FEM_01_PROXY_ROOT"]["lean_solution_deg"], 1)})

# ---------------------------------------------------------------- cameras
BRIEF = {"CAM_01_ORDINARY_EVENING": 24, "CAM_02_UNNOTICED_MEMORIES": 50, "CAM_03_INTRODUCING_GLISS": 85,
         "CAM_04_FIRST_MEMORY": 50, "CAM_05_GALLERY_TRANSFORMS": 35, "CAM_06_THE_DISCOVERY": 85,
         "CAM_07_THE_FEELING": 50, "CAM_08_NOTHING_CHANGED": 24, "CAM_09_EVERYTHING_DID": 24,
         "CAM_10_GLAM_UP_YOUR_MEMORIES": 85}
lens_bad, roll_bad, paths = [], [], {}
objs = solids(arch, True)
min_c, worst, crossings = {}, {}, []
prev = None
fixt = [bpy.data.objects[n + "_HEAD"] for n in ("GLISS_LEFT", "GLISS_CENTRE", "GLISS_RIGHT")]
for f in range(1, 277):
    bvh = bvh_at(arch, f, objs)
    cam = marker_cam(arch, f)
    p = cam.matrix_world.translation.copy()
    d = bvh.find_nearest(p)[3]
    d = min([d] + [(h.matrix_world.translation - p).length - 0.09 for h in fixt])
    if d < min_c.get(cam.name, 9):
        min_c[cam.name], worst[cam.name] = d, f
    if prev and prev[0] == cam.name and (p - prev[1]).length > 1e-6:
        seg = p - prev[1]
        if bvh.ray_cast(prev[1], seg.normalized(), seg.length)[0] is not None:
            crossings.append(f)
    if abs(cam.data.lens - BRIEF[cam.name]) > 1e-4:
        lens_bad.append([f, cam.name, cam.data.lens])
    xr = cam.matrix_world.to_3x3() @ Vector((1, 0, 0))
    if abs(xr.z) > 1e-4:
        roll_bad.append([f, cam.name, round(xr.z, 5)])
    tgt = bpy.data.objects.get(cam.name + "_TARGET") or bpy.data.objects["CAM_01_ORDINARY_EVENING_TARGET"]
    paths.setdefault(cam.name, []).append([f, [round(c, 4) for c in p], [round(c, 4) for c in
                                                                          tgt.matrix_world.translation],
                                           cam.data.lens, round(d, 3)])
    prev = (cam.name, p)
studio.frame_set(277)
c10 = bpy.data.objects["CAM_10_GLAM_UP_YOUR_MEMORIES"]
m0 = c10.matrix_world.copy()
static10 = True
for f in range(277, 361):
    studio.frame_set(f)
    if any(abs(a - b) > 1e-7 for ra, rb in zip(c10.matrix_world, m0) for a, b in zip(ra, rb)):
        static10 = False
check("lenses match the brief and never change within a shot", not lens_bad and c10.data.lens == 85, lens_bad[:5])
check("no camera roll (horizon level) in any shot", not roll_bad, roll_bad[:5])
check("camera clearance >= 0.05 m from all geometry incl. proxies and fixtures, shots 1-9",
      all(v >= 0.05 for v in min_c.values()), {k: [round(v, 3), worst[k]] for k, v in min_c.items()})
check("no camera path segment passes through geometry", not crossings, crossings[:10])
c1, c8 = bpy.data.objects["CAM_01_ORDINARY_EVENING"], bpy.data.objects["CAM_08_NOTHING_CHANGED"]
arch.frame_set(20)
m1 = c1.matrix_world.copy()
arch.frame_set(215)
m8 = c8.matrix_world.copy()
same = all(abs(a - b) < 1e-7 for ra, rb in zip(m1, m8) for a, b in zip(ra, rb)) and c1.data == c8.data
check("shot 08 is an exact duplicate of CAM_01 (transform, lens, aperture; exposure is scene-wide)", same,
      {"shared_camera_data": c1.data == c8.data})
k9 = {229: (MX(1.65), 3.05), 240: (MX(1.85), 3.55), 252: (MX(2.05), 4.10), 264: (MX(2.30), 4.65),
      276: (MX(2.50), 5.30)}
dev = []
for f, (x, y) in k9.items():
    arch.frame_set(f)
    p = bpy.data.objects["CAM_09_EVERYTHING_DID"].matrix_world.translation
    dev.append(round((Vector((x, y, 1.65)) - p).length * 1000, 2))
check("shot 09 dolly passes through the brief's five keyframes (mirrored X)", max(dev) < 0.5, {"dev_mm": dev})
check("shot 10 packshot camera completely static 277-360", static10, {})
# walkthrough clearance >= 0.35 (characters hidden)
wo = solids(walk, False)
wcam = bpy.data.objects["CAM_WALKTHROUGH"]
wmin, wf, wpath = 9, 0, []
for f in range(1, 241):
    bvh = bvh_at(walk, f, wo)
    p = wcam.evaluated_get(LAST["dg"]).matrix_world.translation.copy()
    d = bvh.find_nearest(p)[3]
    if d < wmin:
        wmin, wf = d, f
    wpath.append([f, [round(c, 4) for c in p], [round(c, 4) for c in bpy.data.objects["CAM_WALKTHROUGH_TARGET"]
                                                .evaluated_get(LAST["dg"]).matrix_world.translation], 24.0,
                  round(d, 3)])
paths["CAM_WALKTHROUGH"] = wpath
check("walkthrough clearance >= 0.35 m from all geometry", wmin >= 0.35, {"min_m": round(wmin, 3), "frame": wf})
# final render settings stored
r = arch.render
vl = arch.view_layers["BEAUTY"]
check("final settings stored: Cycles 256 spp adaptive, denoise, AgX, 180-deg blur, EXR multilayer half + passes",
      arch.cycles.samples == 256 and arch.cycles.use_adaptive_sampling and arch.cycles.use_denoising
      and arch.view_settings.view_transform == "AgX" and r.use_motion_blur and abs(r.motion_blur_shutter - 0.5) < 1e-6
      and r.image_settings.file_format == "OPEN_EXR_MULTILAYER" and r.image_settings.color_depth == "16"
      and vl.use_pass_z and vl.use_pass_normal and vl.use_pass_vector and vl.use_pass_emit
      and vl.use_pass_cryptomatte_object and vl.use_pass_cryptomatte_material and vl.cycles.use_pass_shadow_catcher,
      {"device": arch.cycles.device, "note": "no standalone shadow pass in Cycles; shadow catcher pass stored"})

os.makedirs(os.path.join(ROOT, "metadata"), exist_ok=True)
json.dump(paths, open(os.path.join(ROOT, "metadata", "camera_paths.json"), "w"))
reg_out = {"product": "Polycab Gliss Surface COB Track Light, 7 W, Warm White (hero variant)",
           "master_object": "GLISS_MASTER_02",
           "dimension_status": "Manufacturer dimensions remain unverified. No certified measurement is claimed.",
           "brief_dimension_register_mm": {k: None for k in (
               "housing_diameter", "housing_length", "mounting_base_diameter", "mounting_base_thickness",
               "stem_width", "stem_length", "reflector_depth", "emitter_diameter")},
           "model_register": reg,
           "conflicts": ["PROP_GLISS_02 'dimension reference' reads ~120 mm x ~90 mm for a stem-less cylinder; "
                         "it contradicts the official photograph's proportions (length/diameter 1.75) and is "
                         "generated imagery, so it is recorded, not used.",
                         "STORYBOARD_02 panel 08 and TRANSFORM_02 show 'Tilt 0-90 deg / Rotate 355 deg' and "
                         "three housing finishes; both are unverified and excluded per the brief."],
           "installed_aiming": aim,
           "photometry": {"cct_k": 3000, "beam_angle_deg": aim[0]["beam_angle_deg"],
                          "light_output": "70 W radiant per spot (preview value, NOT the 7 W electrical rating)",
                          "status": "Preview assumptions only; replace with manufacturer IES data."}}
json.dump(reg_out, open(os.path.join(ROOT, "metadata", "GLISS_02_PRODUCT_DIMENSION_REGISTER.json"), "w"), indent=1)
nf = sum(not c["pass"] for c in results)
json.dump({"stage": "PREVIEW / INSPECTION", "checks": results, "failures": nf,
           "unresolved": ["Manufacturer dimensions, articulation limits and IES photometry not supplied.",
                          "Approved photographs MEMORY_01-03 not supplied (placeholders cropped from PROP_GLISS_02).",
                          "FEM_01 / MAL_01 locked character sheets not supplied; proxies only.",
                          "END_02 used as supplied (1672 px); a full-resolution vector master is needed for 4K.",
                          "Brief X coordinates mirrored so GLISS_LEFT / MEMORY_01 / glazing are on the viewer's "
                          "left; seats moved from +/-0.43 to +/-0.30 m; CAM_04 moved from y 2.1 to 2.75 m."]},
          open(os.path.join(ROOT, "metadata", "GLISS_02_QA_REPORT.json"), "w"), indent=1)
print("QA_DONE %d checks, %d fail" % (len(results), nf))
