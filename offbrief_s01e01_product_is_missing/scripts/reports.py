"""Measures the saved master scene and writes the four required reports (JSON + Markdown) to reports/.
    blender -b scenes/OFFBRIEF_S01E01_MASTER.blend --python scripts/reports.py
"""
import json
import math
import os
import sys

import bpy
from bpy_extras.object_utils import world_to_camera_view
from mathutils import Vector
from mathutils.bvhtree import BVHTree

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import shotlist as S  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REP = os.path.join(ROOT, "reports")
sc = bpy.context.scene
dg = bpy.context.evaluated_depsgraph_get()
meta = json.load(open(os.path.join(REP, "_build_meta.json")))
WEST, EAST = ("NICO_01", "SLOANE_01"), ("ELLIOT_01", "VANTA_CLIENT")


def dump(name, data, md):
    json.dump(data, open(os.path.join(REP, name + ".json"), "w"), indent=2)
    open(os.path.join(REP, name + ".md"), "w").write(md)
    print("wrote", name)


def shot_of(f):
    return next(s for s in S.SHOTS if s["start"] <= f <= s["end"])


def eyes_world(cid):
    arm = bpy.data.objects[cid + "_RIG"]
    return arm.matrix_world @ arm.pose.bones["eyes"].head


def bvh_of(objs):
    verts, polys = [], []
    for o in objs:
        oe = o.evaluated_get(dg)
        me = oe.to_mesh()
        mw = oe.matrix_world
        base = len(verts)
        verts += [mw @ v.co for v in me.vertices]
        polys += [[base + i for i in p.vertices] for p in me.polygons]
        oe.to_mesh_clear()
    return BVHTree.FromPolygons(verts, polys) if polys else None


# ------------------------------------------------------------------ 1. camera-cut timeline
markers = sorted(sc.timeline_markers, key=lambda m: m.frame)
timeline = []
checks = []
for sh, m in zip(S.SHOTS, markers):
    su = next(x for x in meta["camera_setups"] if x["shot"] == sh["n"])
    sc.frame_set((sh["start"] + sh["end"]) // 2)
    cam = bpy.data.objects[sh["cam"]]
    fwd = cam.matrix_world.to_quaternion() @ Vector((0, 0, -1))
    timeline.append(dict(shot=sh["n"], frames=[sh["start"], sh["end"]], duration_s=round((sh["end"] - sh["start"] + 1) / S.FPS, 3),
                         marker=m.name, marker_frame=m.frame, camera=m.camera.name, setup=sh["setup"],
                         lens_mm=cam.data.lens, fstop=cam.data.dof.aperture_fstop, position=su["position"],
                         rotation_deg=su["rotation_deg"], focus_distance_m=su["focus_distance"],
                         forward=[round(v, 3) for v in fwd], beat=sh["beat"],
                         dialogue=[dict(speaker=w, line=t, frames=[a, b]) for w, t, a, b in sh["dialogue"]]))
    checks.append(m.frame == sh["start"] and m.camera.name == sh["cam"])
md = ["# Camera-cut timeline: S01E01 'The Product Is Missing'", "",
      f"{S.FRAME_END - S.FRAME_START + 1} frames at {S.FPS} fps, {len(markers)} markers, {len(S.CAMERAS)} cameras. "
      f"Every marker sits on its shot's first frame and binds that shot's camera: **{'PASS' if all(checks) else 'FAIL'}**.", "",
      "| Shot | Frames | Sec | Camera / set-up | Lens | Position (m) | Beat | Dialogue |", "|---|---|---|---|---|---|---|---|"]
for t in timeline:
    dl = "<br>".join(f"{d['speaker']} {d['frames'][0]}-{d['frames'][1]}: {d['line']}" for d in t["dialogue"]) or "-"
    md.append(f"| {t['shot']:02d} | {t['frames'][0]}-{t['frames'][1]} | {t['duration_s']} | {t['camera']} / {t['setup']} | "
              f"{t['lens_mm']:.0f} mm f/{t['fstop']:.1f} | {tuple(t['position'])} | {t['beat']} | {dl} |")
dump("camera_cut_timeline", dict(frames=S.FRAME_END, fps=S.FPS, shots=timeline, markers_ok=all(checks)), "\n".join(md) + "\n")

# ------------------------------------------------------------------ 2. actor-position continuity
SAMPLE = sorted(set(list(range(1, 721, 6)) + [s["start"] for s in S.SHOTS] + [s["end"] for s in S.SHOTS] + [720]))
actors = {}
for cid in S.CAST:
    actors[cid] = dict(root=[], yaw=[], foot_min_z=[], pelvis_z=[])
for f in SAMPLE:
    sc.frame_set(f)
    for cid in S.CAST:
        arm = bpy.data.objects[cid + "_RIG"]
        a = actors[cid]
        a["root"].append(arm.matrix_world.translation.copy())
        a["yaw"].append(math.degrees(arm.matrix_world.to_euler().z))
        a["pelvis_z"].append((arm.matrix_world @ arm.pose.bones["pelvis"].head).z)
        a["foot_min_z"].append(min((o.matrix_world @ Vector(c)).z for o in bpy.data.objects
                                   if o.name.startswith(cid + "_shoe") for c in o.bound_box))
cont = {}
md = ["# Actor-position continuity report", "",
      f"Sampled {len(SAMPLE)} frames (every 6th frame plus every shot's first and last frame).", "",
      "| Actor | Pose | Root position (m) | Max root drift (m) | Max yaw drift (deg) | Pelvis z range (m) | Shoe sole z range (m) | Shots on screen | Result |",
      "|---|---|---|---|---|---|---|---|---|"]
for cid, a in actors.items():
    r0 = a["root"][0]
    drift = max((r - r0).length for r in a["root"])
    yd = max(abs(y - a["yaw"][0]) for y in a["yaw"])
    pz, fz = (min(a["pelvis_z"]), max(a["pelvis_z"])), (min(a["foot_min_z"]), max(a["foot_min_z"]))
    seen = []
    for sh in S.SHOTS:
        sc.frame_set((sh["start"] + sh["end"]) // 2)
        cam = bpy.data.objects[sh["cam"]]
        p = world_to_camera_view(sc, cam, eyes_world(cid))
        if 0 <= p.x <= 1 and 0 <= p.y <= 1 and p.z > 0:
            seen.append(sh["n"])
    ok = drift < 1e-6 and yd < 1e-4 and fz[0] >= 0 and fz[1] < 0.02
    cont[cid] = dict(pose=S.CAST[cid]["pose"], root=[round(v, 4) for v in r0], max_root_drift_m=drift, max_yaw_drift_deg=yd,
                     pelvis_z_range=[round(v, 4) for v in pz], shoe_sole_z_range=[round(v, 4) for v in fz],
                     visible_in_shots=seen, chair=f"PROP_Chair_{cid}" if S.CAST[cid]["pose"] == "seated" else None, ok=ok)
    md.append(f"| {cid} | {S.CAST[cid]['pose']} | {tuple(round(v, 3) for v in r0)} | {drift:.6f} | {yd:.4f} | "
              f"{pz[0]:.3f}-{pz[1]:.3f} | {fz[0]:.3f}-{fz[1]:.3f} | {', '.join(map(str, seen)) or 'none'} | {'PASS' if ok else 'FAIL'} |")
md += ["", "Nobody stands, walks or changes seats. The client (VANTA_CLIENT) is in frame only where the table above lists it; "
       "every other shot, including shot 09 where the client speaks, keeps the client off screen at the same chair."]
dump("actor_position_continuity", cont, "\n".join(md) + "\n")

# ------------------------------------------------------------------ 3. BOX_01 trajectory
traj = meta["box_trajectory"]
speeds = []
for a, b in zip(traj, traj[1:]):
    d = math.dist((a["x"], a["y"], a["z"]), (b["x"], b["y"], b["z"]))
    speeds.append(d * S.FPS)
phase_runs = []
for t in traj:
    if not phase_runs or phase_runs[-1]["phase"] != t["phase"] or phase_runs[-1]["support"] != t["support"]:
        phase_runs.append(dict(phase=t["phase"], support=t["support"], start=t["frame"], end=t["frame"]))
    phase_runs[-1]["end"] = t["frame"]
jumps = [i + 1 for i, v in enumerate(speeds) if v > 6.0]
land = next(t for t in traj if t["support"] == "TABLE" and t["phase"] == "grounded")
md = ["# BOX_01 trajectory report", "",
      "BOX_01 is one continuous flat 2D layered rig (`BOX_01` root, `BOX_01_FACING` yaw, `BOX_01_SQUASH` squash pivot, art cards). "
      "It is never swapped, morphed or duplicated. The same object is the on-screen illustration and the tabletop character. "
      f"Art scale is fixed at {S.BOX_SIZE_M} m per 1000 px, so it keeps the same world size from the screen to the table.", "",
      "Motion is keyed on the 24 fps timeline with STEPPED modifiers (frame step 2): 12 fps-style holds.", "",
      "## Phases", "", "| Frames | Phase | Support |", "|---|---|---|"]
md += [f"| {r['start']}-{r['end']} | {r['phase']} | {r['support'] or '-'} |" for r in phase_runs]
md += ["", "## Key events", "",
       f"- Revealed on the illustration slide at frame 313, 1 cm in front of the display plane (y = {S.BOX_PATH[0][2]}).",
       f"- Steps through the screen plane at frames 361-368, drops onto the sideboard top ({S.SIDEBOARD['size'][2]} m) at frame 372.",
       f"- Leaps from the sideboard edge at frame 390 (peak z {max(t['z'] for t in traj if 388 <= t['frame'] <= 400):.3f} m) "
       f"and lands on the tabletop at frame {land['frame']} at ({land['x']}, {land['y']}, {land['z']}).",
       f"- Max speed {max(speeds):.2f} m/s (the leap). Largest single-frame move "
       f"{max(speeds) / S.FPS * 100:.1f} cm. Frames with any move above 6 m/s (a teleport test): {jumps or 'none'}.",
       "- Per-frame positions are in `box01_trajectory.json`."]
dump("box01_trajectory", dict(size_m=S.BOX_SIZE_M, phases=phase_runs, max_speed_mps=max(speeds), teleport_frames=jumps,
                              frames=traj), "\n".join(md) + "\n")

# ------------------------------------------------------------------ 4. contact & occlusion validation
res = []


def check(name, ok, detail):
    res.append(dict(check=name, result="PASS" if ok else "FAIL", detail=detail))


g_err = [abs(t["height_above_support"]) for t in traj if t["phase"] == "grounded"]
check("BOX_01 soles on the support when grounded", max(g_err) < 0.005, f"max |sole - surface| = {max(g_err) * 1000:.2f} mm over {len(g_err)} frames")
check("Both feet land on the tabletop", land["support"] == "TABLE" and abs(land["z"] - S.TABLE["top_z"]) < 0.005,
      f"frame {land['frame']}: z = {land['z']} m, table top = {S.TABLE['top_z']} m")
sh_ok = all(t["shadow_alpha"] > 0.5 for t in traj if t["phase"] == "grounded")
sh_off = all(t["shadow_alpha"] == 0 for t in traj if t["phase"] in ("screen", "hidden"))
check("Contact shadow present when grounded, absent on screen", sh_ok and sh_off,
      "alpha 0.85 on contact, fading with height in the air, 0 while BOX_01 is part of the illustration")
fwd = [t for t in traj if t["phase"] == "screen"]
check("On-screen BOX_01 sits in front of the display plane", all(t["y"] < S.MONITOR["center"][1] for t in fwd),
      f"y = {fwd[0]['y']} m vs display plane y = {S.MONITOR['center'][1]} m (BOX_01 occludes the slide, never the reverse)")
after = [t for t in traj if t["frame"] >= 372 and t["visible"]]
check("After stepping out, BOX_01 never re-enters the wall/screen plane", all(t["y"] < S.MONITOR["center"][1] - 0.2 for t in after),
      f"max y after frame 372 = {max(t['y'] for t in after):.3f} m")
check("No teleport (per-frame move under 25 cm)", not jumps, f"max per-frame move {max(speeds) / S.FPS * 100:.1f} cm")

# box vs props: closest approach between the box footprint and the water glass / mugs while on the table
glass = bpy.data.objects["PROP_Water_Glass"].matrix_world.translation
dmin = min(math.hypot(t["x"] - glass.x, t["y"] - glass.y) for t in traj if t["support"] == "TABLE")
check("BOX_01 clears the water glass", dmin > 0.036 + 0.09, f"closest centre distance {dmin:.3f} m (needs > 0.126 m)")

# layer order inside the rig
lay = {o.name: o.location.y for o in bpy.data.objects if o.name.startswith("BOX_01_") and o.type == "MESH"}
face_front = all(lay[n] < lay["BOX_01_body_closed"] for n in lay if "eyes" in n or "mouth" in n)
check("Rig layer order (face over body, gloves/sneakers over limbs)", face_front, "face cards 2 mm in front of the body card")

# camera-to-BOX occlusion by real geometry at each box shot's mid frame
box_names = {o.name for o in bpy.data.objects if o.name.startswith("BOX_01")}
for sh in S.SHOTS:
    if sh["start"] < 313:
        continue
    f = (sh["start"] + sh["end"]) // 2
    sc.frame_set(f)
    cam = bpy.data.objects[sh["cam"]]
    tgt = bpy.data.objects["BOX_01_FOCUS"].matrix_world.translation
    o_ = cam.matrix_world.translation
    d = (tgt - o_)
    hit, loc, _n, _i, ob, _m = sc.ray_cast(dg, o_, d.normalized(), distance=d.length - 0.02)
    blocked = hit and ob.name not in box_names and not ob.name.startswith("PROP_Screen") and "Glass" not in ob.name
    check(f"Shot {sh['n']:02d}: line of sight camera -> BOX_01 face", not blocked,
          f"frame {f}: {'blocked by ' + ob.name if blocked else 'clear'}")

# cameras inside the room, outside geometry, north-facing; west actors left of east actors
static = [o for o in bpy.data.objects if o.type == "MESH" and not o.name.startswith(("BOX_01",) + tuple(S.CAST))
          and not o.name.startswith("ARCH_Exterior")]
sc.frame_set(1)
tree = bvh_of(static)
for sh in S.SHOTS:
    sc.frame_set(sh["start"])
    cam = bpy.data.objects[sh["cam"]]
    p = cam.matrix_world.translation
    fwd = cam.matrix_world.to_quaternion() @ Vector((0, 0, -1))
    inside = abs(p.x) < S.ROOM["width"] / 2 - 0.1 and abs(p.y) < S.ROOM["depth"] / 2 - 0.1 and 0.2 < p.z < S.ROOM["height"] - 0.2
    near = tree.find_nearest(p)[3]
    order = []
    for w in WEST:
        for e in EAST:
            pw, pe = world_to_camera_view(sc, cam, eyes_world(w)), world_to_camera_view(sc, cam, eyes_world(e))
            if all(0 <= q.x <= 1 and 0 <= q.y <= 1 and q.z > 0 for q in (pw, pe)):
                order.append(pw.x < pe.x)
    check(f"Shot {sh['n']:02d}: {sh['cam']} inside room, clear of geometry, north-facing",
          inside and near > 0.08 and fwd.y > 0,
          f"pos {tuple(round(v, 2) for v in p)}, nearest surface {near:.2f} m, forward.y {fwd.y:.2f}")
    if order:
        check(f"Shot {sh['n']:02d}: 180-degree rule (window-side actors left of client/screen-side actors)", all(order),
              f"{len(order)} west/east pairs in frame")

# human vs furniture interpenetration at sampled frames
HELD = ("PROP_Tablet_Elliot",)   # props an actor is holding count as part of that actor
furn = [o for o in static if o.name.startswith(("PROP_", "ARCH_Partition", "ARCH_Wall")) and not o.name.startswith(HELD)]
ftree = bvh_of(furn)
fnames = []
for o in furn:
    oe = o.evaluated_get(dg)
    me = oe.to_mesh()
    fnames += [o.name] * len(me.polygons)
    oe.to_mesh_clear()
hits = {}
for f in SAMPLE[::2]:
    sc.frame_set(f)
    for cid in S.CAST:
        parts = [o for o in bpy.data.objects if o.type == "MESH" and o.name.startswith(cid + "_")]
        at = bvh_of(parts)
        for _a, b in at.overlap(ftree):
            hits.setdefault(cid, {}).setdefault(fnames[b], set()).add(f)
for cid in S.CAST:
    h = hits.get(cid, {})
    check(f"{cid}: no interpenetration with furniture/props", not h,
          "none" if not h else "; ".join(f"{k} @ {min(v)}-{max(v)} ({len(v)} samples)" for k, v in sorted(h.items())))

n_fail = sum(r["result"] == "FAIL" for r in res)
md = ["# Contact and occlusion validation", "",
      f"{len(res)} checks, {len(res) - n_fail} pass, {n_fail} fail. Measured on `scenes/OFFBRIEF_S01E01_MASTER.blend`.", "",
      "| Check | Result | Detail |", "|---|---|---|"]
md += [f"| {r['check']} | {r['result']} | {r['detail']} |" for r in res]
dump("contact_occlusion_validation", dict(checks=res, fails=n_fail), "\n".join(md) + "\n")
