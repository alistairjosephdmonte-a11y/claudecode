"""Continuity checks from the built animation (metadata/build_log.json) and the master .blend.
    python3 scripts/continuity.py                     (hoof checks; pure Python)
    blender -b scenes/AMUL_OTM_EP01_MASTER.blend --python scripts/continuity.py   (+ scene checks)
Writes metadata/continuity_report.json."""
import json
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import config as C  # noqa: E402

try:
    import bpy
except ImportError:
    bpy = None

GROUND = 0.002          # m: a hoof at or below this height is in contact
SLIDE = 0.0015          # m per frame: a planted hoof moving more than this is sliding
ALLOWED_SLIDE = {("S04", "rear_near"), ("S04", "rear_far")}     # scripted: rear hooves slip on the dusty floor


def hoof_checks(log):
    poses = {int(k): v for k, v in log["poses"].items()}
    frames = sorted(poses)
    out = {"frames": len(frames), "min_grounded_hooves": 4, "frames_with_fewer_than_2_grounded": [], "planted_hoof_slides": [],
           "scripted_slip_cm": 0.0, "hoof_jumps_at_cuts_cm": {}}
    for f in frames:
        n = sum(1 for v in poses[f]["hooves"].values() if v[1] <= GROUND)
        out["min_grounded_hooves"] = min(out["min_grounded_hooves"], n)
        if n < 2:
            out["frames_with_fewer_than_2_grounded"].append(f)
    for f in frames[1:]:
        a, b = poses[f - 1], poses[f]
        if a["shot"] != b["shot"]:
            out["hoof_jumps_at_cuts_cm"][f"{a['shot']}->{b['shot']}"] = round(max(abs(b["hooves"][k][0] - a["hooves"][k][0]) for k in a["hooves"]) * 100, 1)
            continue
        for k in a["hooves"]:
            ua, va = a["hooves"][k]
            ub, vb = b["hooves"][k]
            if va <= GROUND and vb <= GROUND and abs(ub - ua) > SLIDE:
                if (b["shot"], k) in ALLOWED_SLIDE:
                    out["scripted_slip_cm"] += abs(ub - ua) * 100
                else:
                    out["planted_hoof_slides"].append((f, k, round((ub - ua) * 1000, 2)))
    out["scripted_slip_cm"] = round(out["scripted_slip_cm"], 1)
    out["max_leg_overreach_m"] = log["max_leg_overreach_m"]
    return out


def scene_checks():
    from bpy_extras import anim_utils
    sc = bpy.context.scene
    r = {}

    def fc(obj, path, idx=0):
        ad = obj.animation_data
        cb = anim_utils.action_get_channelbag_for_slot(ad.action, ad.action_slot)
        return next(c for c in cb.fcurves if c.data_path == path and c.array_index == idx)

    r["frame_range"] = [sc.frame_start, sc.frame_end, sc.frame_end - sc.frame_start + 1 == C.TOTAL_FRAMES]
    mk = sorted(sc.timeline_markers, key=lambda m: m.frame)
    r["camera_cuts"] = [(m.name, m.frame, m.camera.name, round(m.camera.data.lens)) for m in mk]
    r["cuts_match_shot_table"] = [m.frame for m in mk] == [C.bf(s["f0"]) for s in C.SHOTS] and \
        all(round(m.camera.data.lens) == s["lens"] for m, s in zip(mk, C.SHOTS))
    blk = bpy.data.objects["TRAINING_BLOCK"]
    bx = fc(blk, "location", 0)
    moving = [f for f in range(2, C.TOTAL_FRAMES + 1) if abs(bx.evaluate(f) - bx.evaluate(f - 1)) > 1e-6]
    r["block_moves_frames"] = [min(moving), max(moving)] if moving else []
    r["block_moves_only_in"] = sorted({C.shot_of(f)["id"] for f in moving})
    r["block_total_slide_cm"] = round((bx.evaluate(C.TOTAL_FRAMES) - C.BLOCK["x"]) * 100, 2)
    r["block_dims_m"] = [round(v, 3) for v in blk.dimensions]
    hn = fc(bpy.data.objects["DOOR_HINGE_N"], "rotation_euler", 2)
    hs = fc(bpy.data.objects["DOOR_HINGE_S"], "rotation_euler", 2)
    ang = [(f, math.degrees(-hn.evaluate(f)), math.degrees(hs.evaluate(f))) for f in range(1, C.TOTAL_FRAMES + 1)]
    r["doors_closed_until_frame"] = next(f for f, a, b in ang if a > 0.01) - 1
    r["doors_final_angle_deg"] = round(ang[-1][1], 1)
    r["doors_monotonic_and_symmetric"] = all(ang[i][1] >= ang[i - 1][1] - 1e-6 for i in range(1, len(ang))) and \
        all(abs(a - b) < 1e-4 for f, a, b in ang)
    sun = bpy.data.objects["SUN"]
    r["sun_animated"] = bool(sun.animation_data)
    r["sun_rotation_deg"] = [round(math.degrees(v), 2) for v in sun.rotation_euler]
    sw = {}
    for cname in ("MOO_SIDE_ART", "MOO_REAR_ART", "MOO_Q3_ART"):
        o = next(o for o in bpy.data.collections[cname].objects if o.type == "MESH" and "torso" in o.name or o.name.endswith("_head"))
        h = fc(o, "hide_render")
        sw[cname] = sorted({int(k.co.x) for k in h.keyframe_points})
    cut_frames = {C.bf(s["f0"]) for s in C.SHOTS} | {1}
    r["artwork_view_switches_only_on_cuts"] = all(set(v) <= cut_frames for v in sw.values())
    names = [o.name for o in bpy.data.objects if o.type == "MESH" and o.visible_camera]
    r["characters_in_scene"] = sorted({n.split("_")[0] for n in names if n.startswith(("SIDE_", "REAR_", "Q3_"))})
    r["moo_proxy_visible_to_camera"] = any(o.visible_camera for o in bpy.data.collections["MOO_PROXY"].objects)
    return r


if __name__ == "__main__":
    log = json.load(open(os.path.join(C.P["meta"], "build_log.json")))
    rep = {"hooves": hoof_checks(log)}
    if bpy:
        rep["scene"] = scene_checks()
    path = os.path.join(C.P["meta"], "continuity_report.json")
    old = json.load(open(path)) if os.path.exists(path) else {}
    old.update(rep)
    json.dump(old, open(path, "w"), indent=1)
    print(json.dumps(rep, indent=1)[:3000])
