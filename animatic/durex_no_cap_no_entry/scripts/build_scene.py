"""DUREX: NO CAP, NO ENTRY - reproducible Blender 4.2+ animatic build.

Usage:
    blender -b --factory-startup --python scripts/build_scene.py
Writes DUREX_NO_CAP_animatic.blend next to the scripts folder. No external assets are required.
"""
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import bpy
from math import radians
from mathutils import Vector, Matrix

import common
from common import (SHOTS, FRAME_START, FRAME_END, FPS, CAP_NAVY, ENDCARD_START, get_coll, safe_set, cap_twill,
                    principled, write_action)
import environment as env
import cap_asset
import cast
import cartoon
import perform
import endcard

ROOT = os.path.dirname(HERE)
BLEND = os.path.join(ROOT, "DUREX_NO_CAP_animatic.blend")


def setup_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    sc.name = "DUREX_MAIN"
    r = sc.render
    r.engine = "BLENDER_EEVEE_NEXT"
    r.resolution_x, r.resolution_y, r.resolution_percentage = 1920, 1080, 100
    r.fps, r.fps_base = FPS, 1.0
    sc.frame_start, sc.frame_end = FRAME_START, FRAME_END
    r.use_motion_blur = True
    r.motion_blur_shutter = 0.5  # 180-degree shutter
    safe_set(r, "motion_blur_position", "START")
    r.film_transparent = False
    r.filter_size = 1.5
    r.image_settings.file_format = "PNG"
    e = sc.eevee
    for k, v in (("taa_render_samples", 16), ("taa_samples", 8), ("use_shadows", True), ("shadow_ray_count", 1),
                 ("shadow_step_count", 6), ("use_raytracing", True), ("ray_tracing_method", "SCREEN"),
                 ("use_gtao", True), ("motion_blur_steps", 1), ("volumetric_tile_size", "8")):
        safe_set(e, k, v)
    try:
        e.ray_tracing_options.resolution_scale = "2"
        e.ray_tracing_options.trace_max_roughness = 0.45
    except AttributeError:
        pass
    vs = sc.view_settings
    safe_set(vs, "view_transform", "AgX")
    safe_set(vs, "look", "AgX - Medium High Contrast")
    vs.exposure = 0.6
    sc["project"] = "DUREX: NO CAP, NO ENTRY - 30s animatic"
    sc["cap_hex_status"] = "PLACEHOLDER %s - replace with HEX sampled from approved brand artwork" % common.CAP_BLUE_PLACEHOLDER
    return sc


def main():
    t0 = time.time()
    sc = setup_scene()
    cols = {n: get_coll(n) for n in ("LOCATION_EXTERIOR", "LOCATION_INTERIOR", "CHARACTERS", "CAPS",
                                       "CARTOON_ELEMENTS", "LIGHTING", "CAMERAS", "PROPS")}
    mats = env.build_exterior(cols)
    env.build_interior(cols)
    env.build_lights(cols)
    rope, hooks = env.build_rope(cols, mats)

    me = cap_asset.build_cap_mesh()
    navy_twill = cap_twill("MAT_CAP_TWILL_NAVY", CAP_NAVY)
    navy_thread = principled("MAT_CAP_THREAD_NAVY", "#10162A", rough=0.8, sheen=0.3)
    cap_mats = {
        "hero": None,
        "navy": {cap_asset.SLOT_TWILL: navy_twill, cap_asset.SLOT_THREAD: navy_thread, cap_asset.SLOT_BUTTON: navy_twill,
                 cap_asset.SLOT_SPARE: navy_twill},
    }

    chars = {}
    for name in cast.CAST:
        cc = get_coll("CHAR_" + name, cols["CHARACTERS"])
        chars[name] = cast.Character(name, cc, cap_mats, cols["CAPS"])
    print("characters built", round(time.time() - t0, 1))

    # rig controls: IK targets (keyed in world space or parented to the props they grab)
    ctrl = get_coll("RIG_CONTROLS", cols["CHARACTERS"])

    def empty(name, parent=None, loc=(0, 0, 0)):
        o = bpy.data.objects.new(name, None)
        o.empty_display_type = "SPHERE"
        o.empty_display_size = 0.03
        ctrl.objects.link(o)
        o.parent = parent
        o.location = loc
        return o

    hero, bouncer, g4 = chars["HERO_01"], chars["BOUNCER_01"], chars["GUEST_04"]
    brim_t = empty("CTRL_HERO_01_BRIM_GRIP_R")
    hero.add_ik("R", "IK_R_BRIM", brim_t)

    gift = cap_asset.cap_object("GUEST_04_GIFT_CAP", cols["CAPS"])
    gift["note"] = "Same hero-cap asset (shared mesh). Rests on ENTRANCE_SHELF; handed to GUEST_04 in SH09."
    rope_grip = empty("CTRL_BOUNCER_ROPE_GRIP")
    bouncer.add_ik("R", "IK_R_ROPE", rope_grip)
    b_grip = empty("CTRL_BOUNCER_CAP_GRIP", gift, (0.0, 0.07, 0.075))
    bouncer.add_ik("R", "IK_R_CAP", b_grip)
    g4.add_ik("L", "IK_L_CAP", empty("CTRL_GUEST_04_CAP_GRIP_L", gift, (0.098, -0.01, 0.04)))
    g4.add_ik("R", "IK_R_CAP", empty("CTRL_GUEST_04_CAP_GRIP_R", gift, (-0.098, -0.01, 0.04)))

    # cartoon intrusions
    cone = cartoon.build_cone(cols["CARTOON_ELEMENTS"])
    g2 = chars["GUEST_02"]
    g2._parent(cone, "head")
    cone.matrix_basis = Matrix.Translation((0, g2.head_c.y + 0.01, g2.head_c.z + g2.head_r.z - 0.018))
    dish = cartoon.build_dish(cols["CARTOON_ELEMENTS"])
    g3 = chars["GUEST_03"]
    g3._parent(dish, "head")
    dish.matrix_basis = Matrix.Translation((0, g3.head_c.y + 0.01, g3.head_c.z + g3.head_r.z - 0.012))
    eleph, eleph_obs = cartoon.build_elephant(cols["CARTOON_ELEMENTS"], cartoon.cel_cap_materials())
    eleph.location = (3.0, 14.4, 0.0)
    eleph.rotation_euler.z = common.heading_for(-6.2, -7.0)

    # animation
    d = perform.Director(chars, {})
    active = {"HERO_01": {1, 5, 6, 7, 10}, "BOUNCER_01": {1, 2, 3, 4, 5, 6, 7, 9},
              "GUEST_01": {1, 2}, "GUEST_02": {1, 2, 3}, "GUEST_03": {1, 2, 3, 4}, "GUEST_04": {1, 2, 3, 4, 5, 6, 7, 9}}
    for name, ch in chars.items():
        perform.bake_character(ch, d, active.get(name, {7, 8, 10}))
        print("baked", name, round(time.time() - t0, 1))
    for name in ("HERO_01", "BOUNCER_01", "GUEST_01", "GUEST_02", "GUEST_03", "GUEST_04"):
        perform.foot_lock(sc, chars[name], active[name], ctrl)
    print("feet locked", round(time.time() - t0, 1))
    perform.animate_rope(d, rope, hooks, rope_grip)
    perform.animate_cartoon_props(d, chars, cone, dish, eleph_obs)
    perform.animate_gift_cap(sc, gift, g4)
    perform.animate_hero_brim(sc, hero, brim_t)
    cams = perform.build_cameras(cols, d)
    print("props + cameras", round(time.time() - t0, 1))

    # camera binding markers (one camera per shot) + gag markers
    for s in SHOTS:
        m = sc.timeline_markers.new("SH%02d" % s["n"], frame=s["start"])
        m.camera = cams[s["n"]]
    for name, fr in (("GAG_ARM_BLOCK", 97), ("GAG_HEAD_SHAKE", 169), ("GAG_EYEBROW", 253), ("GAG_POINT_AWAY", 265),
                     ("HERO_STOP", 337), ("BRIM_CONTACT", 349), ("SH06b_HERO_CU", 385), ("SH06c_BOUNCER_CU", 409),
                     ("NOD", 421), ("ROPE_UNHOOK", 445), ("CAP_HANDOFF", 625), ("CAP_ON", 637),
                     ("SH10b_ENDCARD_CUT", ENDCARD_START)):
        sc.timeline_markers.new(name, frame=fr)
    sc.camera = cams[1]

    endcard.build_endcard(sc)
    sc.frame_set(1)
    bpy.ops.wm.save_as_mainfile(filepath=BLEND, compress=True)
    print("saved", BLEND, round(time.time() - t0, 1))


if __name__ == "__main__":
    main()
