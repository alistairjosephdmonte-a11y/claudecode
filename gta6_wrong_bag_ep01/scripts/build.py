"""Builds THE LAST JOB EP01 THE WRONG BAG block previs.
    python3 scripts/textures.py && python3 scripts/dialogue.py
    blender -b --factory-startup --python scripts/build.py
Writes scenes/LASTJOB_EP01_WRONG_BAG.blend and metadata/build_log.json."""
import json
import math
import os
import sys

import bpy
from mathutils import Vector

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import anim  # noqa: E402
import config as C  # noqa: E402
import mats as M  # noqa: E402
import rig  # noqa: E402
import setpieces as SP  # noqa: E402


def jason_extras(add, s):
    silver = M.clay("silver", "#c8ccd4", 0.2, 1.0)
    add("chain", "torus", (0.08 * s, 0.065 * s, 0.0025), silver, "chest", (0, 0.028 * s, 0.81 * s), rot=(0.5, 0, 0))
    add("watch", "cyl", (0.05 * s, 0.05 * s, 0.018 * s), M.clay("watch_black", "#18181c", 0.4), "forearm.L", (-0.14 * s, -0.004 * s, 0.497 * s))


def lucia_extras(add, s):
    gold = M.clay("gold", "#d4a63a", 0.25, 1.0)
    for k in (-1, 1):
        add(f"hoop{'L' if k < 0 else 'R'}", "torus", (0.028 * s, 0.028 * s, 0.0016), gold, "head", (k * 0.054 * s, 0.002 * s, 0.905 * s),
            rot=(0, math.pi / 2, 0))


LOOKS = {
    "JASON_01": dict(H=C.JASON_H, look=lambda: dict(
        shirt=M.clay("jason_tank_grey", "#9a9a9c", 0.9), skin=M.clay("jason_skin", "#b07a5a", 0.6),
        hair=M.clay("jason_hair", "#3a2a1e", 0.9), pants=M.clay("jason_cargo_olive", "#4f4a32", 0.9),
        shoe=M.clay("sneaker_white", "#e2e0da", 0.6), hair_style="short", sleeves=False, extras=[jason_extras])),
    "LUCIA_01": dict(H=C.LUCIA_H, look=lambda: dict(
        shirt=M.clay("lucia_tank_pink", "#d77a9e", 0.85), skin=M.clay("lucia_skin", "#b88466", 0.55),
        hair=M.clay("lucia_hair", "#2a1a14", 0.85), pants=M.clay("lucia_jeans", "#5a6e8e", 0.85),
        shoe=M.clay("sneaker_white", "#e2e0da", 0.6), hair_style="ponytail", sleeves=False, extras=[lucia_extras])),
}


def choose_pole_angles(arm):
    for pb in arm.pose.bones:
        for c in pb.constraints:
            if c.type != "IK":
                continue
            best = None
            for ang in (0, 90, -90, 180):
                c.pole_angle = math.radians(ang)
                bpy.context.view_layer.update()
                d = ((arm.matrix_world @ pb.head) - c.pole_target.matrix_world.translation).length
                if best is None or d < best[0]:
                    best = (d, ang)
            c.pole_angle = math.radians(best[1])


def trackers(arm, target):
    pb = arm.pose.bones["head"]
    Bm = pb.bone.matrix_local.to_3x3()
    axes = {"TRACK_X": Bm.col[0], "TRACK_NEGATIVE_X": -Bm.col[0], "TRACK_Z": Bm.col[2], "TRACK_NEGATIVE_Z": -Bm.col[2]}
    ax = max(axes, key=lambda k: axes[k].dot(Vector((0, 1, 0))))
    for b, inf in (("head", 0.75), ("neck", 0.3)):
        c = arm.pose.bones[b].constraints.new("DAMPED_TRACK")
        c.target, c.track_axis, c.influence = target, ax, inf
    e = arm.pose.bones["eyes"].constraints.new("DAMPED_TRACK")      # pupils finish the eyeline the head starts
    e.target, e.track_axis, e.influence = target, "TRACK_Y", 1.0


def build_characters(body):
    chars = {}
    for cid, spec in LOOKS.items():
        coll = SP.coll(cid)
        arm, tg = rig.build(cid, spec["H"], spec["look"](), coll)
        arm.parent = body
        for k, v in list(tg.items()):
            if k.startswith("pole_"):
                v.parent = arm
                v.location = arm.data.bones[f"{'forearm' if 'hand' in k else 'shin'}.{k[-1]}"].head_local + tg[f"_pole_off_{k[5:]}"]
            elif not k.startswith("_"):
                v.parent = body
        tg = {k: v for k, v in tg.items() if not k.startswith("_")}
        trackers(arm, tg["look"])
        chars[cid] = (arm, tg)
    return chars


def render_settings(sc):
    sc.render.engine = "BLENDER_EEVEE"
    sc.render.resolution_x, sc.render.resolution_y = C.RES
    sc.render.fps = C.FPS
    sc.frame_start, sc.frame_end = C.F0, C.F1
    ee = sc.eevee
    for k, v in dict(taa_render_samples=12, use_shadows=True, use_raytracing=False, volumetric_start=0.05, volumetric_end=80.0,
                     volumetric_tile_size="16", volumetric_samples=24, use_volumetric_shadows=True, volumetric_light_clamp=0.0).items():
        if hasattr(ee, k):
            try:
                setattr(ee, k, v)
            except Exception as e:  # noqa: BLE001
                print("skip", k, e)
    sc.render.use_motion_blur = False
    sc.view_settings.view_transform = "AgX"
    sc.view_settings.look = "AgX - Medium High Contrast"
    sc.view_settings.exposure = 0.6
    sc.view_layers[0].name = "PREVIS_BEAUTY"
    sc.render.image_settings.file_format = "PNG"
    sc.render.use_sequencer = False


def audio_strips(sc):
    se = sc.sequence_editor_create()
    strips = se.strips if hasattr(se, "strips") else se.sequences
    for i, d in enumerate(C.DIALOGUE):
        st = strips.new_sound(d["id"], os.path.join(C.P["audio"], "dialogue", f"{d['id']}.wav"), channel=1 + (0 if d["who"] == "JASON_01" else 1),
                              frame_start=d["f0"])
        st.name = f"DLG_{d['id']}"
    mix = os.path.join(C.P["audio"], "LASTJOB_EP01_mix.wav")
    if os.path.exists(mix):
        strips.new_sound("MIX", mix, channel=4, frame_start=C.F0)


def annotations(sc):
    sync = json.load(open(os.path.join(C.P["meta"], "lipsync.json")))
    for d in C.DIALOGUE:
        sc.timeline_markers.new(f"{d['id']} ▶ \"{d['text']}\"", frame=d["f0"])
        sc.timeline_markers.new(f"{d['id']} ■", frame=d["f1"])
        for fr, ph in sync[d["id"]]["phonemes"]:
            if fr != d["f0"]:
                sc.timeline_markers.new(f"{d['id']}:{ph}", frame=fr)
    for n, fr in (("ZIP start", C.ZIP["insert"][0]), ("ZIP 15cm", C.ZIP["insert"][1]), ("TAG pinch", C.TAG["pinch"]),
                  ("TAG legible", C.TAG["legible"][0]), ("BEAM travel", C.BEAM["f"][0]), ("BEAM on windshield", C.BEAM["f"][1]),
                  ("BEAM crosses face", C.BEAM["face"][0])):
        sc.timeline_markers.new(n, frame=fr)


def main():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    sc.frame_start, sc.frame_end = C.F0, C.F1
    SP.station()
    root, body, wheels = SP.car()
    bagp = SP.bag(body)
    heli = SP.heli()
    SP.sky_and_haze()
    police = dict(bars={o.name: o for o in bpy.data.objects if o.name.startswith("POLICE_bar_")},
                  lights={o.name: o for o in bpy.data.objects if o.name.startswith("POLICE_flash_")},
                  spill=bpy.data.objects["POLICE_spill_blue"])
    chars = build_characters(body)
    for arm, _ in chars.values():
        choose_pole_angles(arm)
    cams = anim.cameras(sc, chars, body)
    log = anim.apply(sc, chars, (root, body, wheels), bagp, heli, police)
    anim.key_police_bars(police)
    sc.camera = cams["CAM_01"]
    render_settings(sc)
    audio_strips(sc)
    annotations(sc)
    reach = {}
    for f in range(C.F0, C.F1 + 1):
        sc.frame_set(f)
        sid = C.shot_of(f)["id"]
        for cid, (arm, tg) in chars.items():
            for sd in ("L", "R"):
                w = arm.matrix_world @ arm.pose.bones[f"forearm.{sd}"].tail
                e = (w - tg[f"hand.{sd}"].matrix_world.translation).length
                a = arm.matrix_world @ arm.pose.bones[f"shin.{sd}"].tail
                e2 = (a - tg[f"foot.{sd}"].matrix_world.translation).length
                key = f"{sid}/{cid}.{sd}"
                reach[key] = max(reach.get(key, 0), round(e, 4), round(e2, 4))
    log["ik_max_error_m"] = reach
    sc.frame_set(C.F0)
    os.makedirs(C.P["scenes"], exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(C.P["scenes"], "LASTJOB_EP01_WRONG_BAG.blend"))
    json.dump(log, open(os.path.join(C.P["meta"], "build_log.json"), "w"))
    bad = {k: v for k, v in reach.items() if v > 0.005}
    print("BUILT. IK errors > 5 mm:", json.dumps(bad))


if __name__ == "__main__":
    main()
