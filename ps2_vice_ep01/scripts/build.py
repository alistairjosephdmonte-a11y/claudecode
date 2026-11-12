"""Builds the PLAYSTATION x GTA VI EP01 block animatic scene.
    blender -b --factory-startup --python scripts/build.py
Writes scenes/PS_GTA_EP01_BLOCK.blend and metadata/build_log.json."""
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


def gamer_extras(add, s):
    hp = M.clay("headphones", "#0e0e10", 0.4)
    add("headphones_band", "torus", (0.15 * s * 0.6, 0.12 * s * 0.6, 0.012), hp, "chest", (0, 0.004 * s, 0.825 * s), rot=(0.25, 0, 0))
    for k in (-1, 1):
        add(f"headphones_cup{k}", "cyl", (0.05 * s * 0.6, 0.05 * s * 0.6, 0.028), hp, "chest", (k * 0.05 * s, 0.03 * s, 0.81 * s),
            rot=(0.9, 0, k * 0.5))
    add("tshirt_patch", "box", (0.04 * s, 0.004, 0.035 * s), M.clay("patch", "#d94b2f", 0.8), "chest", (0.04 * s, 0.067 * s, 0.775 * s))


def tommy_extras(add, s):
    gold = M.clay("gold", "#d4a63a", 0.25, 1.0)
    add("gold_chain", "torus", (0.075 * s, 0.06 * s, 0.003), gold, "chest", (0, 0.03 * s, 0.81 * s), rot=(0.55, 0, 0))
    add("collar_v", "box", (0.05 * s, 0.004, 0.06 * s), M.clay("tommy_skin", "#b98262", 0.6), "chest", (0, 0.067 * s, 0.79 * s))
    add("watch", "cyl", (0.05 * s, 0.05 * s, 0.018 * s), gold, "forearm.L", (-0.14 * s, -0.004 * s, 0.497 * s))


LOOKS = {
    "GAMER_01": dict(H=C.GAMER_H, shirt=M.clay, look=lambda: dict(
        shirt=M.clay("gamer_tshirt_offwhite", "#e9e4d8", 0.9), skin=M.clay("gamer_skin", "#c99c7c", 0.6),
        hair=M.clay("gamer_hair", "#3b2416", 0.9), pants=M.clay("gamer_jeans", "#3f5f86", 0.85),
        shoe=M.clay("sneaker_white", "#ececea", 0.6), curls=True, extras=[gamer_extras])),
    "TOMMY_01": dict(H=C.TOMMY_H, look=lambda: dict(
        shirt=M.image("tommy_shirt_tropical", "shirt_tropical.png", 0.8), skin=M.clay("tommy_skin", "#b98262", 0.6),
        hair=M.clay("tommy_hair", "#120e0e", 0.5), pants=M.clay("tommy_jeans", "#4a6ea0", 0.85),
        shoe=M.clay("sneaker_white", "#ececea", 0.6), curls=False, extras=[tommy_extras])),
}


def choose_pole_angles(arm, tg):
    """Pick the IK pole angle that bends each elbow/knee toward its pole target (rest-pose test)."""
    sc = bpy.context.scene
    for pb in arm.pose.bones:
        for c in pb.constraints:
            if c.type != "IK":
                continue
            best = None
            for ang in (0, 90, -90, 180):
                c.pole_angle = math.radians(ang)
                bpy.context.view_layer.update()
                mid = arm.matrix_world @ pb.head
                d = (mid - c.pole_target.matrix_world.translation).length
                if best is None or d < best[0]:
                    best = (d, ang)
            c.pole_angle = math.radians(best[1])


def head_track(arm, target):
    pb = arm.pose.bones["head"]
    Bm = pb.bone.matrix_local.to_3x3()
    fwd = Vector((0, 1, 0))
    axes = {"TRACK_X": Bm.col[0], "TRACK_NEGATIVE_X": -Bm.col[0], "TRACK_Z": Bm.col[2], "TRACK_NEGATIVE_Z": -Bm.col[2]}
    ax = max(axes, key=lambda k: axes[k].dot(fwd))
    c = pb.constraints.new("DAMPED_TRACK")
    c.target, c.track_axis, c.influence = target, ax, 0.9
    nk = arm.pose.bones["neck"].constraints.new("DAMPED_TRACK")
    nk.target, nk.track_axis, nk.influence = target, ax, 0.3
    return ax


def build_characters():
    chars = {}
    for cid, spec in LOOKS.items():
        coll = SP.coll(cid)
        arm, tg = rig.build(cid, spec["H"], spec["look"](), coll)
        for k, v in list(tg.items()):
            if k.startswith("pole_"):
                v.parent = arm
                v.location = arm.data.bones[f"{'forearm' if 'hand' in k else 'shin'}.{k[-1]}"].head_local + tg[f"_pole_off_{k[5:]}"]
        tg = {k: v for k, v in tg.items() if not k.startswith("_")}
        head_track(arm, tg["look"])
        chars[cid] = (arm, tg)
    return chars


def render_settings(sc):
    sc.render.engine = "BLENDER_EEVEE"
    sc.render.resolution_x, sc.render.resolution_y = C.RES
    sc.render.fps = C.FPS
    sc.frame_start, sc.frame_end = 1, C.TOTAL_FRAMES
    ee = sc.eevee
    for k, v in dict(taa_render_samples=24, taa_samples=8, use_shadows=True, shadow_ray_count=1, shadow_step_count=4,
                     use_raytracing=False, fast_gi_method="GLOBAL_ILLUMINATION", volumetric_start=0.1, volumetric_end=60.0,
                     volumetric_tile_size="8", volumetric_samples=32, use_volumetric_shadows=False, use_gtao=True,
                     gtao_distance=0.4).items():
        if hasattr(ee, k):
            try:
                setattr(ee, k, v)
            except Exception as e:  # noqa: BLE001
                print("eevee setting skipped", k, e)
    sc.render.use_motion_blur = False
    sc.view_settings.view_transform = "AgX"
    sc.view_settings.look = "AgX - Medium High Contrast"
    sc.view_settings.exposure = 0.0
    vl = sc.view_layers[0]
    vl.name = "BLOCK_BEAUTY"
    vl.use_pass_ambient_occlusion = True
    vl.use_pass_z = True
    sc.render.image_settings.file_format = "PNG"
    sc.render.image_settings.color_mode = "RGB"


def main():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    sc.frame_start, sc.frame_end = 1, C.TOTAL_FRAMES
    room_c, hinges = SP.room()
    hw = SP.hardware()
    SP.world()
    car, wheels = SP.car("CAR_01", SP.coll("CAR_01"))
    sun, fog = SP.lights_and_sky()
    fc = SP.coll("FX")
    tf = SP.box("FX_transition_fog", fc, C.ROOM["x0"], C.ROOM["x1"], C.ROOM["y0"], 9.0, 0.0, C.ROOM["h"], bpy.data.materials.new("fog_trans_mat"))
    fm = tf.data.materials[0]
    fm.use_nodes = True
    nt = fm.node_tree
    nt.nodes.remove(nt.nodes["Principled BSDF"])
    vt = nt.nodes.new("ShaderNodeVolumePrincipled")
    vt.inputs["Color"].default_value = C.rgb(C.PAL["purple"])
    vt.inputs["Density"].default_value = 0.0
    vt.inputs["Emission Color"].default_value = C.rgb(C.PAL["pink"])
    nt.links.new(vt.outputs[0], nt.nodes["Material Output"].inputs["Volume"])
    pf = bpy.data.objects["FX_magenta_fog"]
    pf.scale = (1, 1, 1)
    gp = SP.coll("GAMEPLAY_ONLY")
    gcar, gwheels = SP.car("CAR_01_GAMEPLAY", gp)
    gp.hide_render = True                        # only the gameplay pass (render_gameplay.py) shows it
    gcd = bpy.data.cameras.new("CAM_GAMEPLAY")
    gcd.lens = 24
    gcam = bpy.data.objects.new("CAM_GAMEPLAY", gcd)
    gp.objects.link(gcam)
    gcar.rotation_euler = (0, 0, math.pi)       # driving away from the room, toward the sunset (+Y)
    for f in range(380, C.TOTAL_FRAMES + 1):
        t = (f - 380) / 24.0
        y = 70.0 + 13.0 * t
        x = C.CAR["x"] + 0.6 * math.sin(t * 0.9)
        gcar.location = (x, y, 0)
        gcar.keyframe_insert("location", frame=f)
        for w in gwheels:
            w.rotation_euler = ((13.0 * t) / C.CAR["wheel_r"], 0, 0)       # same rolling sense as CAR_01 (local -Y forward)
            w.keyframe_insert("rotation_euler", frame=f)
        cy = 70.0 - 6.5 + 10.5 * t
        gcam.location = (C.CAR["x"] + 0.3 * math.sin(t * 0.6), cy, 2.1)
        gcam.rotation_mode = "QUATERNION"
        gcam.rotation_quaternion = anim.look_q(gcam.location, Vector((x, y + 6, 0.9)))
        gcam.keyframe_insert("location", frame=f)
        gcam.keyframe_insert("rotation_quaternion", frame=f)
    chars = build_characters()
    for cid, (arm, tg) in chars.items():
        choose_pole_angles(arm, tg)
    log = anim.apply(sc, chars, hw, car, wheels, hinges, fog, vt)
    anim.key_fx(sc, hw, fog, vt, hw["crt_glow"])
    cams = anim.cameras(sc, chars)
    anim.slate(sc, cams["S10"])
    sc.camera = cams["S01"]
    render_settings(sc)
    # IK reach report: wrist (forearm tail) vs IK target, per shot
    reach = {}
    for f in range(1, C.TOTAL_FRAMES + 1, 1):
        sc.frame_set(f)
        sid = C.shot_of(f)["id"]
        for cid, (arm, tg) in chars.items():
            for side in ("L", "R"):
                w = arm.matrix_world @ arm.pose.bones[f"forearm.{side}"].tail
                e = (w - tg[f"hand.{side}"].matrix_world.translation).length
                a = arm.matrix_world @ arm.pose.bones[f"shin.{side}"].tail
                e2 = (a - tg[f"foot.{side}"].matrix_world.translation).length
                key = f"{sid}/{cid}"
                reach[key] = max(reach.get(key, 0), round(e, 4), round(e2, 4))
                log["frames"][f].setdefault("ankles", {})[f"{cid}.{side}"] = [round(v, 4) for v in a]
                log["frames"][f].setdefault("wrists", {})[f"{cid}.{side}"] = [round(v, 4) for v in w]
        log["frames"][f]["disc"] = [round(v, 4) for v in hw["disc"].matrix_world.translation]
        log["frames"][f]["controller"] = [round(v, 4) for v in hw["controller"].matrix_world.translation]
    log["ik_max_error_m"] = reach
    sc.frame_set(1)
    os.makedirs(C.P["scenes"], exist_ok=True)
    os.makedirs(C.P["meta"], exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(C.P["scenes"], "PS_GTA_EP01_BLOCK.blend"))
    json.dump(log, open(os.path.join(C.P["meta"], "build_log.json"), "w"))
    print("BUILT. IK max error by shot:", json.dumps(reach))


if __name__ == "__main__":
    main()
