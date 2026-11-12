"""QC for the brief's checklist. Run on the built scene:
    blender -b scenes/LASTJOB_EP01_WRONG_BAG.blend --python scripts/qc.py
Writes metadata/qc_report.json and prints PASS/FAIL per check."""
import json
import math
import os
import sys

import bpy
from bpy_extras.object_utils import world_to_camera_view
from mathutils import Vector
from mathutils.bvhtree import BVHTree

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import config as C  # noqa: E402

sc = bpy.context.scene
O = bpy.data.objects
R = {}


def ok(name, passed, detail):
    R[name] = dict(passed=bool(passed), detail=detail)
    print(("PASS " if passed else "FAIL ") + name + ": " + json.dumps(detail)[:400])


def world_bvh(objs, dg):
    verts, polys = [], []
    for o in objs:
        ev = o.evaluated_get(dg)
        me = ev.to_mesh()
        mw = ev.matrix_world
        base = len(verts)
        verts += [mw @ v.co for v in me.vertices]
        polys += [[base + i for i in p.vertices] for p in me.polygons]
        ev.to_mesh_clear()
    return BVHTree.FromPolygons(verts, polys, epsilon=0.0) if polys else None


def bbox_world(objs):
    pts = [o.matrix_world @ Vector(c) for o in objs for c in o.bound_box]
    return Vector([min(p[i] for p in pts) for i in range(3)]), Vector([max(p[i] for p in pts) for i in range(3)])


def kids(prefix):
    return [o for o in O if o.type == "MESH" and o.name.startswith(prefix)]


# 1 duration ------------------------------------------------------------------------------------------
ok("duration_300_frames_30fps", (sc.frame_start, sc.frame_end, sc.render.fps) == (0, 299, 30),
   dict(frame_start=sc.frame_start, frame_end=sc.frame_end, fps=sc.render.fps, seconds=(sc.frame_end - sc.frame_start + 1) / sc.render.fps))

# 2 cuts / cameras -------------------------------------------------------------------------------------
mk = sorted([m for m in sc.timeline_markers if m.camera], key=lambda m: m.frame)
cuts = [(m.frame, m.camera.name, round(m.camera.data.lens)) for m in mk]
want = [(s["f0"], s["cam"], s["lens"]) for s in C.SHOTS]
zoom = [o.name for o in O if o.type == "CAMERA" and o.data.animation_data and any("lens" in fc.data_path for fc in
        (o.data.animation_data.action.fcurves if hasattr(o.data.animation_data.action, "fcurves") else []))]
ok("hard_cuts_and_dedicated_cameras", cuts == want and not zoom, dict(cuts=cuts, animated_lens=zoom))

# 3 identity / wardrobe -------------------------------------------------------------------------------
ident = {}
for cid in ("JASON_01", "LUCIA_01"):
    parts = [o for o in O if o.name.startswith(cid + "_") and o.type == "MESH"]
    ident[cid] = dict(parts=len(parts), materials=sorted({m.name for o in parts for m in o.data.materials}))
ok("identity_consistent", all(v["parts"] > 30 for v in ident.values()), ident)

# 4 product dimensions --------------------------------------------------------------------------------
dims = {}
for name, pre, want_ in (("PS5_01", "PS5_", (C.PS5["h"], C.PS5["d"], C.PS5["w"])), ("GTA_CASE_01", "CASE_", (C.CASE["w"], C.CASE["h"], C.CASE["t"])),
                         ("DUALSENSE_01", "DS_", (C.DUALSENSE["w"], C.DUALSENSE["d"], C.DUALSENSE["h"]))):
    sc.frame_set(0)
    lo, hi = bbox_world(kids(pre))
    got = tuple(round(hi[i] - lo[i], 3) for i in range(3))
    dims[name] = dict(measured_m=got, spec_m=want_, max_dev_mm=round(max(abs(a - b) for a, b in zip(got, want_)) * 1000, 1))
lo, hi = bbox_world(kids("TAG_face_front"))
dims["TAG_01"] = dict(card_mm=(round(C.TAG["w"] * 1000), round(C.TAG["h"] * 1000)))
ok("product_dimensions", all(v.get("max_dev_mm", 0) <= 12 for v in dims.values()), dims)

# 5 eyelines ------------------------------------------------------------------------------------------
def gaze(cid):
    a = O[cid + "_RIG"]
    pb = a.pose.bones["eyes"]
    return (a.matrix_world @ pb.head, (a.matrix_world.to_3x3() @ (pb.tail - pb.head)).normalized())


eyel = {}
for f, who, other in ((52, "JASON_01", "LUCIA_01"), (75, "LUCIA_01", "JASON_01"), (165, "JASON_01", "LUCIA_01"), (195, "LUCIA_01", "JASON_01")):
    sc.frame_set(f)
    p, d = gaze(who)
    q = O[other + "_RIG"].matrix_world @ O[other + "_RIG"].pose.bones["eyes"].head
    eyel[f"{f}:{who}->{other}"] = round(math.degrees(d.angle((q - p).normalized())), 1)
ok("eyelines_meet", all(v < 12 for v in eyel.values()), dict(angle_deg=eyel))

# 6 car axis: interior CUs all on the windshield side; Jason looks screen-left, Lucia screen-right -----------------
axis = {}
for s in C.SHOTS:
    if s["cam"] in ("CAM_01", "CAM_09", "CAM_05", "CAM_08"):
        continue
    sc.frame_set(s["f0"] + 15)
    cam = O[s["cam"]]
    hj = O["JASON_01_RIG"].matrix_world @ O["JASON_01_RIG"].pose.bones["head"].head
    hl = O["LUCIA_01_RIG"].matrix_world @ O["LUCIA_01_RIG"].pose.bones["head"].head
    pj, pl = world_to_camera_view(sc, cam, hj), world_to_camera_view(sc, cam, hl)
    axis[s["cam"]] = dict(front_side=cam.matrix_world.translation.y > max(hj.y, hl.y), jason_right_of_lucia=pj.x > pl.x)
ok("car_axis_180", all(v["front_side"] and v["jason_right_of_lucia"] for v in axis.values()), axis)

# 7 tag legibility ------------------------------------------------------------------------------------
cam = O["CAM_08"]
legi = []
for f in range(C.TAG["legible"][0], C.TAG["legible"][1] + 1):
    sc.frame_set(f)
    dg = bpy.context.evaluated_depsgraph_get()
    t = O["TAG_01"].matrix_world
    face_n = -(t.to_3x3() @ Vector((0, 1, 0))).normalized()
    centre = t @ Vector((C.TAG["w"] * 0.6, 0, 0))
    facing = face_n.dot((cam.matrix_world.translation - centre).normalized())
    hits = 0
    pts = [t @ Vector((C.TAG["w"] * u, -0.001, C.TAG["h"] * v)) for u in (0.4, 0.6, 0.9) for v in (-0.25, 0.0, 0.25)]
    for p in pts:
        d = p - cam.matrix_world.translation
        h, loc, n, i, ob, _ = sc.ray_cast(dg, cam.matrix_world.translation, d.normalized(), distance=d.length + 0.01)
        hits += h and ob.name == "TAG_face_front"
    a, b = world_to_camera_view(sc, cam, t @ Vector((C.TAG["w"] * 0.5, 0, 0.015))), world_to_camera_view(sc, cam, t @ Vector((C.TAG["w"] * 0.5, 0, -0.005)))
    text_px = abs(a.y - b.y) * C.RES[1] / 1.6          # one line of the three-line title
    legi.append((f, round(facing, 3), hits, round(text_px)))
ok("tag_legible_f220_f239", all(fa > 0.85 and h >= 8 and px >= 25 for _, fa, h, px in legi),
   dict(frames=len(legi), min_facing=min(x[1] for x in legi), min_unoccluded_of_9=min(x[2] for x in legi), min_line_height_px=min(x[3] for x in legi)))

# 8 prop positions ------------------------------------------------------------------------------------
inside, cord = [], []
for f in range(C.F0, C.F1 + 1, 3):
    sc.frame_set(f)
    bm = O["BAG_01"].matrix_world.inverted()
    for pre in ("PS5_", "DS_", "CASE_"):
        pts = [bm @ (o.matrix_world @ Vector(c)) for o in kids(pre) for c in o.bound_box]
        if not all(abs(p.x) <= C.BAG["L"] / 2 - 0.008 and abs(p.y) <= C.BAG["W"] / 2 - 0.008 and 0.09 <= p.z <= C.BAG["H"] for p in pts):
            inside.append((f, pre))
    ring = O["BAG_zip_pull_ring"].matrix_world.translation
    cord.append(round((O["TAG_01"].matrix_world.translation - ring).length, 4))
ok("props_in_place", not inside and max(cord) <= 0.045, dict(products_outside_bag=inside[:10], max_cord_length_m=max(cord)))

# 9 lip-sync ------------------------------------------------------------------------------------------
sync = json.load(open(os.path.join(C.P["meta"], "lipsync.json")))
spill, corr = {}, {}
for cid in ("JASON_01", "LUCIA_01"):
    jb = O[cid + "_RIG"].pose.bones["jaw"]
    wins = [(d["f0"], d["f1"]) for d in C.DIALOGUE if d["who"] == cid]
    talk = []
    for f in range(C.F0, C.F1 + 1):
        sc.frame_set(f)
        open_ = 2 * math.acos(min(1.0, abs(jb.rotation_quaternion.w)))
        inwin = any(a <= f <= b for a, b in wins)
        if open_ > 0.005 and not inwin:
            spill.setdefault(cid, []).append(f)
        talk.append(open_)
    for d in C.DIALOGUE:
        if d["who"] == cid:
            env = sync[d["id"]]["jaw"]
            j = talk[d["f0"]:d["f0"] + len(env)]
            ma, mb = sum(env) / len(env), sum(j) / len(j)
            num = sum((x - ma) * (y - mb) for x, y in zip(env, j))
            den = math.sqrt(sum((x - ma) ** 2 for x in env) * sum((y - mb) ** 2 for y in j)) or 1
            corr[d["id"]] = round(num / den, 3)
strips = {s.name: s.frame_final_start for s in sc.sequence_editor.strips} if sc.sequence_editor else {}
st_ok = all(strips.get(f"DLG_{d['id']}") == d["f0"] for d in C.DIALOGUE)
over = [(a["id"], b["id"]) for a in C.DIALOGUE for b in C.DIALOGUE if a["id"] < b["id"] and a["f0"] < b["f1"] and b["f0"] < a["f1"]]
ok("lip_sync", not spill and all(v > 0.95 for v in corr.values()) and st_ok and not over,
   dict(jaw_outside_lines=spill, envelope_correlation=corr, strips_at_line_starts=st_ok, overlaps=over))

# 10 clipping -----------------------------------------------------------------------------------------
groups = {
    "products": kids("PS5_") + kids("DS_") + kids("CASE_"),
    "bag": [O["BAG_01_shell"]] + kids("BAG_flap_"),
    "tag": kids("TAG_face_"),
    "car_hard": [o for o in O if o.type == "MESH" and o.name.startswith(("CAR_dash", "CAR_console", "CAR_roof", "CAR_door_", "CAR_steering", "CAR_pillar", "CAR_windshield"))],
    "jason": [o for o in O if o.type == "MESH" and o.name.startswith("JASON_01_")],
    "lucia": [o for o in O if o.type == "MESH" and o.name.startswith("LUCIA_01_")],
    "station": [o for o in O if o.type == "MESH" and o.name.startswith(("PUMP_", "CANOPY_pillar"))],
    "car_body": [o for o in O if o.type == "MESH" and o.name.startswith(("CAR_body", "CAR_door_", "CAR_bumper", "CAR_tire"))],
    "heli": [o for o in O if o.type == "MESH" and o.name.startswith("HELI_")],
    "canopy": [O["CANOPY_slab"]],
}
for cid in ("JASON_01", "LUCIA_01"):        # hands legitimately touch the wheel/bag/tag: checked as contact, not clipping
    groups[cid.split("_")[0].lower() + "_body"] = [o for o in groups[cid.split("_")[0].lower()] if not any(k in o.name for k in ("palm", "fingers", "thumb"))]
pairs = [("products", "products"), ("products", "bag"), ("tag", "bag"), ("tag", "products"), ("bag", "car_hard"), ("jason_body", "car_hard"),
         ("lucia_body", "car_hard"), ("jason_body", "lucia_body"), ("jason_body", "bag"), ("lucia_body", "bag"), ("car_body", "station"), ("heli", "canopy")]
clip = {}
for f in range(C.F0, C.F1 + 1, 2):
    sc.frame_set(f)
    dg = bpy.context.evaluated_depsgraph_get()
    for a, b in pairs:
        if a == b:
            objs = groups[a]
            for i in range(len(objs)):
                for j in range(i + 1, len(objs)):
                    if objs[i].name.split("_")[0] == objs[j].name.split("_")[0]:
                        continue                     # parts of the same product touch by design
                    ta, tb = world_bvh([objs[i]], dg), world_bvh([objs[j]], dg)
                    if ta and tb and ta.overlap(tb):
                        clip.setdefault(f"{objs[i].name}~{objs[j].name}", []).append(f)
            continue
        ta, tb = world_bvh(groups[a], dg), world_bvh(groups[b], dg)
        if ta and tb and ta.overlap(tb):
            for oa in groups[a]:                         # name the exact objects
                xa = world_bvh([oa], dg)
                for ob in groups[b]:
                    xb = world_bvh([ob], dg)
                    if xa and xb and xa.overlap(xb):
                        clip.setdefault(f"{oa.name}~{ob.name}", []).append(f)
ok("zero_clipping", not clip, {k: (v[0], v[-1], len(v)) for k, v in clip.items()})

json.dump(R, open(os.path.join(C.P["meta"], "qc_report.json"), "w"), indent=1)
print("QC", sum(v["passed"] for v in R.values()), "/", len(R), "checks pass")
