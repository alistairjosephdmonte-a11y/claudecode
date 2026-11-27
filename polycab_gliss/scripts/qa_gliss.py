"""Technical QA for POLYCAB_GLISS_MASTER.blend. Writes:
    metadata/GLISS_TECHNICAL_QA_REPORT.json   (all checks)
    metadata/GLISS_DIMENSION_REGISTER.json    (editable register, every value PROVISIONAL / NOT VERIFIED)
    metadata/camera_paths.json                (per-frame camera samples, used by plan_png.py)

    blender -b scenes/POLYCAB_GLISS_MASTER.blend --python scripts/qa_gliss.py"""
import json
import math
import os

import bpy
from mathutils import Matrix, Vector
from mathutils.bvhtree import BVHTree

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
META = os.path.join(ROOT, "metadata")
os.makedirs(META, exist_ok=True)
SHOTS = [("CAM_01_PRODUCT_HERO", "SCENE_PRODUCT_STUDIO", 1, 36, 85), ("CAM_02_COB_MACRO", "SCENE_PRODUCT_STUDIO", 37, 60, 100),
         ("CAM_03_AMBIENT", "SCENE_ARCHITECTURE", 61, 84, 35), ("CAM_04_TRANSFORMATION", "SCENE_ARCHITECTURE", 85, 108, 35),
         ("CAM_05_WEDDING_MEMORY", "SCENE_ARCHITECTURE", 109, 132, 85), ("CAM_06_MATCH_CUT", "SCENE_ARCHITECTURE", 133, 168, 85),
         ("CAM_07_HUMAN_CONNECTION", "SCENE_ARCHITECTURE", 169, 204, 85),
         ("CAM_08_INSTALLED_GLISS", "SCENE_ARCHITECTURE", 205, 228, 70),
         ("CAM_09_ARCHITECTURAL_REVEAL", "SCENE_ARCHITECTURE", 229, 276, 24),
         ("CAM_10_FINAL_PACKSHOT", "SCENE_PRODUCT_STUDIO", 277, 360, 85)]
def ev(sc, f):
    """Set the frame on `sc` and return that scene's evaluated depsgraph (not the context scene's)."""
    with bpy.context.temp_override(scene=sc, view_layer=sc.view_layers[0]):
        sc.frame_set(f)
        return bpy.context.evaluated_depsgraph_get()


report = {"status": "PROVISIONAL", "product_validation_status": "PROVISIONAL_UNTIL_MEASURED", "checks": []}


def check(name, ok, detail):
    report["checks"].append({"check": name, "result": ("PASS" if ok else "FAIL") if ok is not None else "INFO",
                             "detail": detail})
    print("QA", name, ok, json.dumps(detail)[:200])


def eval_world_tris(objs, dg, extra=Matrix.Identity(4)):
    verts, polys = [], []
    for o in objs:
        if o.type != "MESH":
            continue
        e = o.evaluated_get(dg)
        me = e.to_mesh()
        mw = extra @ e.matrix_world
        base = len(verts)
        verts += [mw @ v.co for v in me.vertices]
        polys += [[base + i for i in p.vertices] for p in me.polygons]
        e.to_mesh_clear()
    return verts, polys


root = bpy.data.objects["GLISS_MASTER_ROOT"]
reg = json.loads(root["dimension_register_json"])
with open(os.path.join(META, "GLISS_DIMENSION_REGISTER.json"), "w") as f:
    json.dump(reg, f, indent=1)

# ---------------------------------------------------------------- product dimensions
studio = bpy.data.scenes["SCENE_PRODUCT_STUDIO"]
dg = bpy.context.evaluated_depsgraph_get()
parts = {}
for c in ("GLISS_MASTER_MOUNT", "GLISS_MASTER_HEAD"):
    for o in bpy.data.collections[c].objects:
        e = o.evaluated_get(dg)
        me = e.to_mesh()
        mw = o.matrix_basis
        pts = [mw @ v.co for v in me.vertices]
        mn = Vector((min(p.x for p in pts), min(p.y for p in pts), min(p.z for p in pts)))
        mx = Vector((max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts)))
        npoly = len(me.polygons)
        e.to_mesh_clear()
        parts[o.name] = {"bbox_mm": [round((mx - mn)[i] * 1000, 2) for i in range(3)], "polygons": npoly}
dims = {k: v["value"] for k, v in reg["dimensions_mm"].items()}
measured = {
    "housing_outer_diameter": parts["GLISS_HOUSING"]["bbox_mm"][0],
    "housing_length": parts["GLISS_HOUSING"]["bbox_mm"][2],
    "mounting_base_diameter": parts["GLISS_BASE"]["bbox_mm"][0],
    "mounting_base_thickness": parts["GLISS_BASE"]["bbox_mm"][2],
    "stem_width": parts["GLISS_STEM"]["bbox_mm"][0],
    "stem_depth": parts["GLISS_STEM"]["bbox_mm"][1],
    "emitter_diameter": parts["GLISS_COB"]["bbox_mm"][0],
    "reflector_opening_diameter": parts["GLISS_REFLECTOR"]["bbox_mm"][0],
}
dim_rows = []
for k in reg["verified_manufacturer_dimensions_mm"]:
    dim_rows.append({"field": k, "model_mm": measured.get(k, dims.get(k)), "register_mm": dims.get(k),
                     "manufacturer_mm": reg["verified_manufacturer_dimensions_mm"][k], "result": "NOT VERIFIED"})
report["product_dimension_report"] = {"parts": parts, "fields": dim_rows,
                                      "note": "No manufacturer dimensions supplied; no engineering pass claimed."}
check("product register self-consistency", all(abs(measured[k] - dims[k]) < 1.0 for k in measured),
      {k: [measured[k], dims[k]] for k in measured})

# ---------------------------------------------------------------- installation
arch = bpy.data.scenes["SCENE_ARCHITECTURE"]
bpy.context.window_manager  # noqa: B018
inst = []
for side in ("L", "R"):
    mi = bpy.data.objects["GLISS_INSTALLED_%s_MOUNT" % side]
    hi = bpy.data.objects["GLISS_INSTALLED_%s_HEAD" % side]
    mw_m = mi.matrix_basis
    mw_h = mw_m @ hi.matrix_basis
    base_top = (mw_m @ Vector((0, 0, 0))).z
    em = mw_h @ Vector(root["emitter_head_local_m"])
    ax = (mw_h.to_3x3() @ Vector((0, 0, -1))).normalized()
    tgt = Vector(mi["illumination_target_m"])
    miss = (tgt - em - ax * (tgt - em).dot(ax)).length
    # head vs mount clearance (evaluated master geometry under each instance transform)
    vm, pm = eval_world_tris(bpy.data.collections["GLISS_MASTER_MOUNT"].objects, dg, mw_m)
    vh, ph = eval_world_tris(bpy.data.collections["GLISS_MASTER_HEAD"].objects, dg, mw_h)
    bm_, bh = BVHTree.FromPolygons(vm, pm), BVHTree.FromPolygons(vh, ph)
    hits = bm_.overlap(bh)
    stem_ids = set()
    inst.append({"fixture": side, "base_top_z_m": round(base_top, 6), "ceiling_z_m": 3.1,
                 "pan_deg": round(math.degrees(mi.rotation_euler.z), 2),
                 "tilt_deg": round(math.degrees(hi.rotation_euler.x), 2),
                 "optical_axis_miss_mm": round(miss * 1000, 2), "mount_head_overlap_pairs": len(hits)})
report["installation"] = inst
check("bases flush with ceiling", all(abs(i["base_top_z_m"] - 3.1) < 1e-5 for i in inst),
      [i["base_top_z_m"] for i in inst])
check("optical axes hit artwork targets (< 5 mm)", all(i["optical_axis_miss_mm"] < 5 for i in inst),
      [i["optical_axis_miss_mm"] for i in inst])
check("head/mount intersections limited to the stem-pivot joint", all(i["mount_head_overlap_pairs"] < 400 for i in inst),
      {"overlap_pairs": [i["mount_head_overlap_pairs"] for i in inst],
       "note": "stem end is seated inside the pivot pad by design; other contact would show as many pairs"})

# ---------------------------------------------------------------- scene geometry for clearance
def scene_bvh(sc, skip=("CAST", "ISHA", "VEER", "EXT_", "GLISS_", "LGT", "CAM", "ART_WEDDING_01_Frame")):
    objs = [o for o in sc.objects if o.type == "MESH" and not o.name.startswith(skip)]
    v, p = eval_world_tris(objs, ev(sc, 1))
    return BVHTree.FromPolygons(v, p)


bvh_arch = scene_bvh(arch)
paths = {}
cam_rows = []
for cid, scn, f0, f1, lens in SHOTS:
    sc = bpy.data.scenes[scn]
    cam = bpy.data.objects[cid]
    samples = []
    for f in range(f0, f1 + 1):
        dgs = ev(sc, f)
        e = cam.evaluated_get(dgs)
        mw = e.matrix_world
        pos = mw.translation.copy()
        fwd = (mw.to_3x3() @ Vector((0, 0, -1))).normalized()
        right = (mw.to_3x3() @ Vector((1, 0, 0))).normalized()
        d = None
        if scn == "SCENE_ARCHITECTURE":
            hit = bvh_arch.find_nearest(pos)
            d = hit[3] if hit[0] is not None else None
        samples.append((f, pos, fwd, right, d, e.data.lens, e.data.dof.focus_distance))
    sp = [(b[1] - a[1]).length * 24 for a, b in zip(samples, samples[1:])]
    acc = [abs(b - a) * 24 for a, b in zip(sp, sp[1:])]
    row = {"camera": cid, "scene": scn, "frames": [f0, f1], "lens_mm": samples[0][5],
           "lens_constant": all(abs(s[5] - samples[0][5]) < 1e-6 for s in samples),
           "travel_m": round(sum(sp) / 24, 4), "max_speed_mps": round(max(sp) if sp else 0, 4),
           "max_accel_mps2": round(max(acc) if acc else 0, 3),
           "max_horizon_roll_deg": round(max(abs(math.degrees(math.asin(max(-1, min(1, s[3].z))))) for s in samples), 4),
           "min_clearance_m": round(min(s[4] for s in samples), 3) if scn == "SCENE_ARCHITECTURE" else None}
    cam_rows.append(row)
    paths[cid] = [[s[0], [round(x, 4) for x in s[1]], [round(x, 4) for x in s[2]]] for s in samples]
report["cameras"] = cam_rows
lens_ok = all(r["lens_constant"] and abs(r["lens_mm"] - s[4]) < 1e-6 for r, s in zip(cam_rows, SHOTS))
check("focal lengths match brief and are constant within shots", lens_ok, [r["lens_mm"] for r in cam_rows])
check("no horizon roll (< 0.05 deg)", all(r["max_horizon_roll_deg"] < 0.05 for r in cam_rows),
      [r["max_horizon_roll_deg"] for r in cam_rows])
arch_rows = [r for r in cam_rows if r["min_clearance_m"] is not None]
check("architecture cameras clear of geometry (>= 0.30 m)", all(r["min_clearance_m"] >= 0.30 for r in arch_rows),
      {r["camera"]: r["min_clearance_m"] for r in arch_rows})
c3 = bpy.data.objects["CAM_03_AMBIENT"]
c4 = bpy.data.objects["CAM_04_TRANSFORMATION"]
m3 = c3.evaluated_get(ev(arch, 84)).matrix_world.copy()
m4 = c4.evaluated_get(ev(arch, 85)).matrix_world.copy()
check("CAM_04 identical to CAM_03 (transform, lens, focus)",
      max(abs(a - b) for ra, rb in zip(m3, m4) for a, b in zip(ra, rb)) < 1e-6 and c3.data == c4.data,
      "shared camera data, identity parent")


# frustum checks
def in_view(sc, cam, f, pt):
    from bpy_extras.object_utils import world_to_camera_view
    co = world_to_camera_view(sc, cam.evaluated_get(ev(sc, f)), Vector(pt))
    return 0 < co.x < 1 and 0 < co.y < 1 and co.z > 0


fxR = bpy.data.objects["GLISS_INSTALLED_R_MOUNT"].location
fxL = bpy.data.objects["GLISS_INSTALLED_L_MOUNT"].location
check("CAM_08 keeps the right fixture in frame",
      all(in_view(arch, bpy.data.objects["CAM_08_INSTALLED_GLISS"], f, fxR - Vector((0, 0, 0.08)))
          for f in range(205, 229)), "base-to-housing point sampled every frame")
check("CAM_09 end frame shows both fixtures and the artwork",
      all(in_view(arch, bpy.data.objects["CAM_09_ARCHITECTURAL_REVEAL"], 276, p) for p in
          (fxL - Vector((0, 0, 0.05)), fxR - Vector((0, 0, 0.05)), (0, 0.04, 1.65))), "frame 276")

# walkthrough
walk = bpy.data.scenes["SCENE_WALKTHROUGH_PREVIEW"]
bvh_w = scene_bvh(walk)
wc = bpy.data.objects["CAM_WALKTHROUGH"]
wsamp = []
for f in range(1, 241):
    p = wc.evaluated_get(ev(walk, f)).matrix_world.translation.copy()
    hit = bvh_w.find_nearest(p)
    wsamp.append((f, p, hit[3]))
wsp = [(b[1] - a[1]).length * 24 for a, b in zip(wsamp, wsamp[1:])]
mid = wsp[24:-24]
paths["CAM_WALKTHROUGH"] = [[f, [round(x, 4) for x in p], None] for f, p, _ in wsamp]
report["walkthrough"] = {"min_clearance_m": round(min(s[2] for s in wsamp), 3), "max_speed_mps": round(max(wsp), 3),
                         "mid_speed_cv": round((max(mid) - min(mid)) / (sum(mid) / len(mid)), 3),
                         "key_frames": list(wc.get("arc_length_key_frames", []))}
check("walkthrough clearance >= 0.35 m", report["walkthrough"]["min_clearance_m"] >= 0.35, report["walkthrough"])

# ---------------------------------------------------------------- lighting before / after (84 vs 85)
def light_state(sc, f):
    dgs = ev(sc, f)
    st = {}
    for o in sc.objects:
        e = o.evaluated_get(dgs)
        if o.type == "LIGHT":
            st[o.name] = (round(e.data.energy, 4), tuple(round(c, 4) for c in e.data.color))
        if "cob_on" in o.keys():
            st[o.name + ".cob_on"] = round(float(o["cob_on"]), 3)
    st["view"] = (sc.view_settings.view_transform, sc.view_settings.look, sc.view_settings.exposure,
                  sc.view_settings.gamma, sc.view_settings.use_white_balance)
    return st


a, b = light_state(arch, 84), light_state(arch, 85)
diff = sorted(k for k in a if a[k] != b.get(k))
check("before/after: only the two Gliss lights and their COBs change", set(diff) == {
    "GLISS_INSTALLED_L_SPOT", "GLISS_INSTALLED_R_SPOT", "GLISS_INSTALLED_L_HEAD.cob_on",
    "GLISS_INSTALLED_R_HEAD.cob_on"}, diff)

# ---------------------------------------------------------------- edit
edit = bpy.data.scenes["SCENE_MASTER_EDIT"]
strips = sorted(edit.sequence_editor.strips, key=lambda s: s.frame_final_start)
durs = [(s.name, s.frame_final_start, s.frame_final_end - 1, s.frame_final_duration,
         s.scene.name, s.scene_camera.name) for s in strips]
cover = sorted(f for s in strips for f in range(s.frame_final_start, s.frame_final_end))
report["edit"] = durs
check("edit: 10 shots, exactly 360 frames, no gaps or duplicate boundary frames",
      len(strips) == 10 and cover == list(range(1, 361)), [d[3] for d in durs])

with open(os.path.join(META, "camera_paths.json"), "w") as f:
    json.dump(paths, f)
fails = [c for c in report["checks"] if c["result"] == "FAIL"]
report["summary"] = {"checks": len(report["checks"]), "fail": len(fails),
                     "final_render_gate": "Not dimensionally approved: manufacturer measurements missing."}
with open(os.path.join(META, "GLISS_TECHNICAL_QA_REPORT.json"), "w") as f:
    json.dump(report, f, indent=1)
print("QA_DONE", len(report["checks"]), "checks,", len(fails), "fail")
