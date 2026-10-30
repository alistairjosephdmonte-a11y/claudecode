"""Automated continuity / collision / contact QC over all 720 frames.

blender -b DUREX_NO_CAP_animatic.blend --python scripts/qc.py
Writes qc/qc_report.json and qc/qc_report.md. Automated checks are a first pass, not a substitute for review.
"""
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import bpy
from bpy_extras.object_utils import world_to_camera_view
from mathutils import Vector

from common import SHOTS, ENDCARD_START, CAP_BLUE_PLACEHOLDER
import environment as env

ROOT = os.path.dirname(HERE)
OUT = os.path.join(ROOT, "qc")
os.makedirs(OUT, exist_ok=True)

sc = bpy.data.scenes["DUREX_MAIN"]
O = bpy.data.objects
EXTERIOR = {1, 2, 3, 4, 5, 6, 7, 9}
SPEC_LENS = {1: 24, 2: 50, 3: 35, 4: 28, 5: 50, 6: 85, 7: 35, 8: 24, 9: 50, 10: 85}
APPROACH = {2: ("GUEST_01", 73, 96), 3: ("GUEST_02", 145, 166), 4: ("GUEST_03", 217, 249),
            5: ("HERO_01", 289, 337), 9: ("GUEST_04", 577, 596)}
CONTACTS = [("HERO_01", "R", "CTRL_HERO_01_BRIM_GRIP_R", 349, 354, "hero right hand on brim"),
            ("BOUNCER_01", "R", "CTRL_BOUNCER_CAP_GRIP", 607, 625, "bouncer hand on gift cap"),
            ("GUEST_04", "L", "CTRL_GUEST_04_CAP_GRIP_L", 625, 637, "guest04 left hand on cap"),
            ("GUEST_04", "R", "CTRL_GUEST_04_CAP_GRIP_R", 625, 637, "guest04 right hand on cap"),
            ("BOUNCER_01", "R", "CTRL_BOUNCER_ROPE_GRIP", 445, 504, "bouncer hand on rope end (SH07)"),
            ("BOUNCER_01", "R", "CTRL_BOUNCER_ROPE_GRIP", 641, 648, "bouncer hand on rope end (SH09)")]
EXT_CHARS = ["HERO_01", "BOUNCER_01", "GUEST_01", "GUEST_02", "GUEST_03", "GUEST_04"]
ALL_CHARS = [o.get("character") for o in O if o.type == "ARMATURE" and o.get("character")]


def shot_of(f):
    return next(s["n"] for s in SHOTS if s["start"] <= f <= s["end"])


def rig(n):
    return O[n + "_RIG"]


def wpos(arm, bone, tail=False):
    pb = arm.pose.bones[bone]
    return arm.matrix_world @ (pb.tail if tail else pb.head)


rep = {"checks": {}, "failures": [], "warnings": []}


def check(name, ok, detail, warn=False):
    rep["checks"][name] = {"pass": bool(ok), "detail": detail}
    if not ok:
        (rep["warnings"] if warn else rep["failures"]).append(name)


# ---- static checks
check("runtime_720_frames_24fps",
      sc.frame_start == 1 and sc.frame_end == 720 and sc.render.fps == 24 and sc.render.fps_base == 1.0,
      "frames %d-%d @ %s fps = %.2fs" % (sc.frame_start, sc.frame_end, sc.render.fps,
                                         (sc.frame_end - sc.frame_start + 1) / sc.render.fps))
check("resolution_1920x1080", sc.render.resolution_x == 1920 and sc.render.resolution_y == 1080,
      "%dx%d" % (sc.render.resolution_x, sc.render.resolution_y))
mk = {m.name: m for m in sc.timeline_markers}
shots_ok = True
rows = []
for s in SHOTS:
    m = mk.get("SH%02d" % s["n"])
    cam = O.get("CAM_%02d" % s["n"])
    ok = m is not None and m.frame == s["start"] and m.camera == cam and (s["end"] - s["start"] + 1) == 72 \
        and abs(cam.data.lens - SPEC_LENS[s["n"]]) < 1e-6
    shots_ok &= ok
    rows.append("SH%02d %d-%d (%d f) %s %dmm %s" % (s["n"], s["start"], s["end"], s["end"] - s["start"] + 1,
                                                    cam.name, cam.data.lens, "OK" if ok else "BAD"))
check("ten_shots_72f_bound_cameras", shots_ok, rows)
caps = [o for o in O if o.type == "MESH" and o.get("cap_asset")]
meshes = {o.data.name for o in caps}
check("single_shared_cap_mesh", len(meshes) == 1, "%d cap objects -> meshes %s (%d verts)" % (
    len(caps), sorted(meshes), len(caps[0].data.vertices)))
check("cap_colour_placeholder_flagged", True, "hero cap twill base %s (PLACEHOLDER: sample approved artwork)" % CAP_BLUE_PLACEHOLDER)
fonts_main = [o.name for o in sc.objects if o.type == "FONT"]
brand_main = [o.name for o in sc.objects if "PLACEHOLDER__" in o.name or "DUREX" in o.name.upper()]
check("no_text_or_brand_in_story_scene", not fonts_main and not brand_main, {"fonts": fonts_main, "brand": brand_main})
ec = bpy.data.scenes.get("END_CARD")
check("brand_placeholders_only_in_endcard", ec is not None and all(
    "PLACEHOLDER__" in o.name for o in ec.objects if "LOGO" in o.name or "PACKSHOT" in o.name),
    [o.name for o in ec.objects] if ec else "missing")
cel = [o for o in O if o.type == "MESH" and (o.get("style") or o.name.startswith("CARTOON_"))]
check("cartoon_casts_shadows", all(o.visible_shadow for o in cel), "%d cel objects, all visible_shadow" % len(cel))

# ---- per-frame evaluation
slide = {c: 0.0 for c in ALL_CHARS}
slide_at = {c: None for c in ALL_CHARS}
prev_feet = {}
mind = {}
bouncer_dev = {}
geo_bad = []
axis_bad = []
contact = {c[5]: 0.0 for c in CONTACTS}
screen = {}
rope_x = {}
stanch = {}
dg = bpy.context.evaluated_depsgraph_get()
for f in range(1, 721):
    sc.frame_set(f)
    n = shot_of(f)
    cam = O["CAM_%02d" % n]
    # foot sliding: a planted foot (ankle at rest height) must not travel
    for c in ALL_CHARS:
        arm = rig(c)
        ank = arm.data.bones["shin.L"].tail_local.z
        for side in ("L", "R"):
            p = wpos(arm, "foot." + side)
            key = (c, side)
            if key in prev_feet and prev_feet[key][2] == n:
                q = prev_feet[key][0]
                planted = p.z < ank + 0.004 and q.z < ank + 0.004
                if planted and n in (EXTERIOR | {8, 10}):
                    d = (Vector((p.x, p.y)) - Vector((q.x, q.y))).length
                    if d > slide[c]:
                        slide[c], slide_at[c] = d, f
            prev_feet[key] = (p, f, n)
    # collisions between exterior characters (root/pelvis separation)
    if n in EXTERIOR:
        pos = {c: rig(c).matrix_world.translation.to_2d() for c in EXT_CHARS}
        for i, a in enumerate(EXT_CHARS):
            for b in EXT_CHARS[i + 1:]:
                d = (pos[a] - pos[b]).length
                k = (a, b)
                if d < mind.get(k, (9e9, 0))[0]:
                    mind[k] = (d, f)
            for sn, sp in (("L", env.STANCHION_L), ("R", env.STANCHION_R)):
                d = (pos[a] - sp).length
                if d < stanch.get((a, sn), (9e9, 0))[0]:
                    stanch[(a, sn)] = (d, f)
        bp = pos["BOUNCER_01"]
        dv = (bp - env.BOUNCER_MARK).length
        bouncer_dev[n] = max(bouncer_dev.get(n, 0.0), dv)
        # door geography: bouncer stays screen-right of the door centre
        dc = world_to_camera_view(sc, cam, Vector((0, 0, 1.2)))
        bh = world_to_camera_view(sc, cam, wpos(rig("BOUNCER_01"), "head", True))
        if 0 < bh.x < 1 and bh.z > 0 and dc.z > 0 and n != 7 and dv < 0.02:
            if not bh.x > dc.x:
                geo_bad.append(f)
        if n != 7 and cam.matrix_world.translation.y > -1.3:
            axis_bad.append(f)
    if n in APPROACH:
        c, f0, f1 = APPROACH[n]
        if f in (f0, f1):
            wp = rig(c).matrix_world.translation + Vector((0, 0, 1.0))
            v = world_to_camera_view(sc, cam, wp)
            screen.setdefault(n, []).append((round(v.x, 3), round(wp.x, 2)))
    for c, side, tgt, f0, f1, label in CONTACTS:
        if f0 <= f <= f1:
            d = (wpos(rig(c), "hand." + side, True) - O[tgt].matrix_world.translation).length
            contact[label] = max(contact[label], d)
    if n in (7, 9):
        rope_x[f] = O["ROPE_HOOK_END_LEFT"].matrix_world.translation.x

check("bouncer_holds_door_position", all(v < 0.02 for k, v in bouncer_dev.items() if k not in (7, 9))
      and bouncer_dev.get(7, 0) < 0.7 and bouncer_dev.get(9, 0) < 0.7,
      {"max deviation from mark per exterior shot (m)": {("SH%02d" % k): round(v, 3) for k, v in sorted(bouncer_dev.items())},
       "note": "SH07/SH09: one deliberate step toward the entrance-left stanchion to reach the rope hook, then back to mark"})
check("door_geography_bouncer_screen_right", not geo_bad, "frames where bouncer head is not screen-right of door: %s" % geo_bad[:20])
check("camera_side_of_180_line", not axis_bad, "exterior story cameras south of the queue/bouncer line (y<-1.3) except SH07 follow-through: bad frames %s" % axis_bad[:20])
check("screen_direction_left_to_right",
      all(len(v) == 2 and v[1][1] > v[0][1] and v[1][0] >= v[0][0] - 0.01 for v in screen.values()),
      {("SH%02d" % k): "world x %s -> %s, screen x %s -> %s (tracking cameras may hold screen x)" % (
          v[0][1], v[1][1], v[0][0], v[1][0]) for k, v in screen.items()})
pairs = {"%s/%s" % k: "%.2fm @f%d" % v for k, v in sorted(mind.items(), key=lambda kv: kv[1][0])}
check("no_character_interpenetration", all(v[0] > 0.45 for v in mind.values()), {"min root separation": pairs})
check("no_stanchion_collision", all(v[0] > 0.24 for v in stanch.values()),
      {"%s/%s" % k: "%.2fm @f%d" % v for k, v in sorted(stanch.items(), key=lambda kv: kv[1][0])[:6]})
check("hand_to_prop_contacts", all(v < 0.02 for v in contact.values()), {k: "max gap %.1f mm" % (v * 1000) for k, v in contact.items()})
check("foot_sliding_planted_feet", all(v < 0.01 for v in slide.values()),
      {c: "%.1f mm/frame @f%s" % (v * 1000, slide_at[c]) for c, v in slide.items()}, warn=True)
r7 = [rope_x[f] for f in range(445, 505)]
check("rope_opens_toward_screen_right", r7[-1] > r7[0] + 0.5,
      "left rope end x %.2f -> %.2f in SH07 (unhooked from entrance-LEFT stanchion, carried screen-right)" % (r7[0], r7[-1]))

# cartoon depth: feet contact + stool occlusion from CAM_08
sc.frame_set(540)
dg = bpy.context.evaluated_depsgraph_get()
minz = 9e9
for o in O:
    if o.name.startswith("CARTOON_ELEPHANT_01_") and o.type == "MESH" and "LEGS" in o.name:
        e = o.evaluated_get(dg)
        for v in e.data.vertices:
            minz = min(minz, (e.matrix_world @ v.co).z)
check("elephant_feet_on_floor", abs(minz) < 0.02, "lowest leg vertex z = %.3f m" % minz)
cam = O["CAM_08"]
origin = cam.matrix_world.translation
hits = {"stool": 0, "elephant": 0, "other": 0}
root = O["CARTOON_ELEPHANT_01"].matrix_world
vs = [root @ Vector((lx, -0.05, z / 10)) for lx in (-0.85, 0.35) for z in range(1, 11)]
for p in vs:
    d = (p - origin)
    ok, loc, nrm, idx, ob, _ = sc.ray_cast(dg, origin, d.normalized(), distance=d.length + 0.1)
    key = "stool" if ok and "STOOL" in ob.name else "elephant" if ok and "ELEPHANT" in ob.name else "other"
    hits[key] += 1
check("elephant_partially_occluded_by_foreground_stool", hits["stool"] > 0 and hits["elephant"] > 0,
      "rays CAM_08 -> 20 points on the elephant near legs: %s" % hits)

open(os.path.join(OUT, "qc_report.json"), "w").write(json.dumps(rep, indent=2, default=str))
lines = ["# QC report (automated)", "", "Failures: %s" % (rep["failures"] or "none"),
         "Warnings: %s" % (rep["warnings"] or "none"), ""]
for k, v in rep["checks"].items():
    lines.append("## %s - %s" % (k, "PASS" if v["pass"] else "CHECK"))
    det = v["detail"]
    if isinstance(det, list):
        lines += ["- %s" % x for x in det]
    elif isinstance(det, dict):
        for a, b in det.items():
            if isinstance(b, dict):
                lines.append("- %s:" % a)
                lines += ["  - %s: %s" % (x, y) for x, y in b.items()]
            else:
                lines.append("- %s: %s" % (a, b))
    else:
        lines.append("- %s" % det)
    lines.append("")
open(os.path.join(OUT, "qc_report.md"), "w").write("\n".join(lines))
print("QC FAILURES:", rep["failures"])
print("QC WARNINGS:", rep["warnings"])
