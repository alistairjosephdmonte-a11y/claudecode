"""PHASES 3-7: build the master project (sets, 48 shots, graphics, timeline) with a checkpoint save after each phase.
    blender -b --factory-startup --python scripts/shot_builder.py
Every shot lives in its own collection SHOT_Sxx (camera, lights, props, figures, graphics), keyed visible only inside
its 240 frames. Reconstruction shots carry an on-screen RECONSTRUCTION slate; every factual graphic carries a source
tag generated from config.EVIDENCE (VERIFIED / PENDING VERIFICATION)."""
import math
import os
import random
import sys
from types import SimpleNamespace

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy  # noqa: E402
from mathutils import Matrix, Vector  # noqa: E402

import assets as A  # noqa: E402
import camera_rigs as CR  # noqa: E402
import config as C  # noqa: E402
import environments as ENV  # noqa: E402
import motion_graphics as MG  # noqa: E402
import timeline as TL  # noqa: E402

MASTER = os.path.join(C.P["scenes"], C.SCENES["MASTER"])
SETS = {}            # set key -> world origin
K = dict(warm=(1.0, 0.82, 0.62), neutral=(1.0, 0.95, 0.88), cool=(0.85, 0.92, 1.0), fluoro=(0.92, 0.97, 1.0), dusk=(1.0, 0.6, 0.36))


def checkpoint(label):
    bpy.ops.wm.save_as_mainfile(filepath=MASTER, relative_remap=True)
    print(f"CHECKPOINT {label}: saved {MASTER}")


# ---------------------------------------------------------------- PHASE 3: scene + sets
def setup_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    sc.name = "BC001_MASTER"
    sc.render.fps, sc.render.fps_base = C.FPS, 1.0
    sc.frame_start, sc.frame_end = 1, C.TOTAL_FRAMES
    sc.render.resolution_x, sc.render.resolution_y = C.RES_FINAL
    sc.render.resolution_percentage = 100
    sc.render.engine = "BLENDER_EEVEE"
    sc.eevee.taa_render_samples = 64
    sc.render.use_motion_blur = True
    sc.render.motion_blur_shutter = C.SHUTTER                       # 180-degree shutter equivalent
    sc.view_settings.view_transform = "AgX"
    sc.view_settings.look = "None"
    sc.render.use_sequencer = False                                 # VSE holds placeholders only; renders come from the cameras
    sc.world = bpy.data.worlds.new("WORLD_BC001")
    sc.world.use_nodes = True
    try:
        sc.cycles.samples = 512
    except Exception:
        pass
    checkpoint("PHASE 3a scene settings")


def link_set(blend, coll_name, inst_name, origin, target):
    path = os.path.join(C.P["scenes"], blend)
    with bpy.data.libraries.load(path, link=True, relative=True) as (src, dst):
        dst.collections = [coll_name]
    lib_coll = bpy.data.collections[coll_name]
    e = bpy.data.objects.new(inst_name, None)
    e.instance_type, e.instance_collection = "COLLECTION", lib_coll
    e.location = origin
    target.objects.link(e)
    return e


def build_sets(M):
    root = A.coll("SETS")
    SETS["ENV_02_BOARDROOM"] = Vector((2000, 0, 0))
    SETS["ENV_03_BLOCKBUSTER_STORE"] = Vector((3000, 0, 0))
    SETS["ENV_07_DECLINING_STORE"] = Vector((3000, 300, 0))
    SETS["ENV_04_DVD_FULFILLMENT"] = Vector((4000, 0, 0))
    SETS["SET_DESK_VIGNETTE"] = Vector((5600, 0, 0))
    SETS["ENV_01_DALLAS"] = Vector((0, 0, 0))
    c = A.coll("SET_ENV_02_BOARDROOM", root)
    link_set(C.SCENES["BOARDROOM"], "ENV_02_BOARDROOM", "INST_ENV_02_BOARDROOM", SETS["ENV_02_BOARDROOM"], c)
    c = A.coll("SET_ENV_03_BLOCKBUSTER_STORE", root)
    link_set(C.SCENES["STORE"], "ENV_03_STORE_BASE", "INST_ENV_03_STORE_BASE", SETS["ENV_03_BLOCKBUSTER_STORE"], c)
    link_set(C.SCENES["STORE"], "ENV_03_STORE_INV_FULL", "INST_ENV_03_STORE_INV_FULL", SETS["ENV_03_BLOCKBUSTER_STORE"], c)
    c = A.coll("SET_ENV_07_DECLINING_STORE", root)
    e = bpy.data.objects.new("INST_ENV_07_STORE_BASE", None)
    e.instance_type, e.instance_collection = "COLLECTION", bpy.data.collections["ENV_03_STORE_BASE"]
    e.location = SETS["ENV_07_DECLINING_STORE"]
    c.objects.link(e)
    link_set(C.SCENES["STORE"], "ENV_03_STORE_INV_REDUCED", "INST_ENV_07_STORE_INV_REDUCED", SETS["ENV_07_DECLINING_STORE"], c)
    c = A.coll("SET_ENV_04_DVD_FULFILLMENT", root)
    link_set(C.SCENES["WAREHOUSE"], "ENV_04_DVD_FULFILLMENT", "INST_ENV_04_DVD_FULFILLMENT", SETS["ENV_04_DVD_FULFILLMENT"], c)
    c = A.coll("SET_ENV_05_ARCHIVE_LIGHT_TABLE", root)                 # one table instance per archive shot (no overlap)
    arc = [s for s in C.SHOTS if s["environment"] == "ENV_05_ARCHIVE_LIGHT_TABLE"]
    for k, s in enumerate(arc):
        o = Vector((5000 + 25 * k, 0, 0))
        SETS[f"ARCHIVE_{s['shot_id']}"] = o
        link_set(C.SCENES["ARCHIVE"], "ENV_05_ARCHIVE_LIGHT_TABLE", f"INST_ENV_05_ARCHIVE_{s['shot_id']}", o, c)
    c = A.coll("SET_ENV_01_DALLAS", root)
    ENV.build_dallas(c, M)
    c = A.coll("SET_DESK_VIGNETTE", root)
    before = set(bpy.data.objects)
    ENV.build_desk_vignette(c, M)
    for o in set(bpy.data.objects) - before:
        if o.parent is None:
            o.location += SETS["SET_DESK_VIGNETTE"]
    checkpoint("PHASE 3b sets linked and built")


# ---------------------------------------------------------------- helpers
def light(c, name, kind, loc, energy, color, size=0.5, target=None, rot=None, cutoff=None, shadow=True, angle=None, spot=None):
    ld = bpy.data.lights.new(name, kind)
    ld.energy, ld.color = energy, color
    if kind == "AREA":
        ld.size = size
    elif kind == "SUN":
        ld.angle = angle or math.radians(2)
    else:
        ld.shadow_soft_size = size
    ld.use_shadow = shadow
    if spot:
        ld.spot_size, ld.spot_blend = spot
    if cutoff and hasattr(ld, "use_custom_distance"):
        ld.use_custom_distance, ld.cutoff_distance = True, cutoff
    o = A.obj(name, ld, c, tuple(loc))
    if target is not None:
        o.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat("-Z", "Y").to_euler()
    elif rot is not None:
        o.rotation_euler = rot
    return o


def parent_keep(objs, root):
    bpy.context.view_layer.update()
    for o in objs:
        o.parent = root
        o.matrix_parent_inverse = root.matrix_world.inverted()


def slate(ctx, cam, extra=None):
    """On-screen classification (camera-parented, lower third): RECONSTRUCTION label and source status."""
    s = ctx.s
    cd = cam.data
    depth = 1.0
    hw, hh = CR.frame_half_extent(cam, depth)
    size = hh * 2 * 0.021
    lines = []
    if s["reconstruction"]:
        lines.append(("RECONSTRUCTION  ·  REPRESENTATIVE, NOT ARCHIVAL FOOTAGE", "EVIDENCE_IVORY"))
    if extra:
        lines.append((extra, "EVIDENCE_IVORY"))
    for i, (txt, col) in enumerate(lines):
        m = A.mat_basic(f"MAT_SLATE_{col}", A.pal(col), 0.7, emit=A.pal(col), strength=0.6)
        t = A.text(f"SLATE_{s['shot_id']}_{i}", txt, ctx.c, (-hw * 0.93, -hh * 0.86 + i * size * 1.6, -depth), size, m, "semibold",
                   rot=(0, 0, 0), parent=cam)
        if cd.type == "ORTHO":
            t.location.z = -5.0
    srcs = s["source_ids"]
    if srcs:
        pend = [x for x in srcs if not MG.is_verified(x)]
        label = "   ".join(f"{x}: {'VERIFIED' if MG.is_verified(x) else 'PENDING'}" for x in srcs)
        col = "VERDICT_RED" if pend else "ARCHIVE_GREY"
        m = A.mat_basic(f"MAT_SLATE_{col}", A.pal(col), 0.7, emit=A.pal(col), strength=0.6)
        t = A.text(f"SLATE_{s['shot_id']}_SRC", label, ctx.c, (hw * 0.93, -hh * 0.86, -depth), size * 0.85, m, "semibold", "RIGHT",
                   rot=(0, 0, 0), parent=cam)
        if cd.type == "ORTHO":
            t.location.z = -5.0


def world_keys():
    """Per-shot world colour (constant interpolation)."""
    bg = bpy.context.scene.world.node_tree.nodes["Background"]
    for s in C.SHOTS:
        col, strength = WORLD.get(s["shot_id"], ((0.012, 0.014, 0.017), 1.0))
        bg.inputs["Color"].default_value = (*col, 1)
        bg.inputs["Strength"].default_value = strength
        bg.inputs["Color"].keyframe_insert("default_value", frame=s["frame_start"])
        bg.inputs["Strength"].keyframe_insert("default_value", frame=s["frame_start"])
    from bpy_extras import anim_utils
    nt = bpy.context.scene.world.node_tree
    for fc in anim_utils.action_get_channelbag_for_slot(nt.animation_data.action, nt.animation_data.action_slot).fcurves:
        for k in fc.keyframe_points:
            k.interpolation = "CONSTANT"


WORLD = {"S01": ((0.16, 0.12, 0.13), 1.2), "S02": ((0.16, 0.12, 0.13), 1.2), "S03": ((0.3, 0.33, 0.38), 0.8),
         "S04": ((0.3, 0.33, 0.38), 0.8), "S43": ((0.22, 0.25, 0.3), 0.6), "S09": ((0.01, 0.015, 0.03), 1.0),
         "S10": ((0.05, 0.05, 0.06), 0.6), "S11": ((0.05, 0.05, 0.06), 0.6), "S31": ((0.05, 0.05, 0.06), 0.6),
         "S42": ((0.02, 0.022, 0.026), 0.6), "S17": ((0.04, 0.04, 0.045), 0.7), "S18": ((0.04, 0.04, 0.045), 0.7),
         "S22": ((0.03, 0.03, 0.035), 0.5), "S25": ((0.03, 0.03, 0.035), 0.5), "S36": ((0.008, 0.01, 0.018), 0.5)}


def gfx(ctx, drift=(0.0, 0.0), scale=(16.0, 15.0), key=1.0):
    """Graphics stage: backdrop, soft key + rim, orthographic front camera."""
    st = MG.Stage(f"GFX_{ctx.s['shot_id']}", ctx.c, ctx.origin, "front", ctx.M, ctx.f0, ctx.f1)
    st.backdrop()
    light(ctx.c, f"LGT_{ctx.s['shot_id']}_Key", "AREA", st.p(-4, 5, 12), 2600 * key, K["neutral"], 14, target=st.p(0, 0, 0), cutoff=40)
    light(ctx.c, f"LGT_{ctx.s['shot_id']}_Fill", "AREA", st.p(6, -3, 10), 900 * key, K["cool"], 14, target=st.p(0, 0, 0), cutoff=40, shadow=False)
    cam = CR.front_ortho(f"CAM_{ctx.s['shot_id']}", ctx.c, ctx.f0, ctx.f1, ctx.origin, scale, drift)
    return st, cam


def archive(ctx, scale=(2.9, 2.7), drift=((0, 0), (0.02, 0.01))):
    o = SETS[f"ARCHIVE_{ctx.s['shot_id']}"]
    st = MG.Stage(f"ARC_{ctx.s['shot_id']}", ctx.c, o, "flat", ctx.M, ctx.f0, ctx.f1, table_z=ENV.ARCHIVE["table"][2] + 0.003)
    light(ctx.c, f"LGT_{ctx.s['shot_id']}_Lamp", "SPOT", o + Vector((0, 0, 2.2)), 140, K["warm"], 0.35, target=o + Vector((0, 0, 0.9)),
          cutoff=8, spot=(math.radians(120), 1.0))                     # soft, wide pool: no blown-out hotspot
    light(ctx.c, f"LGT_{ctx.s['shot_id']}_Fill", "AREA", o + Vector((1.5, -1.5, 2.5)), 90, K["cool"], 3.0, target=o + Vector((0, 0, 0.9)),
          cutoff=8, shadow=False)
    d0, d1 = drift
    cam = CR.overhead(f"CAM_{ctx.s['shot_id']}", ctx.c, ctx.f0, ctx.f1, (o.x + d0[0], o.y + d0[1]), (o.x + d1[0], o.y + d1[1]), 1.95,
                      ortho=scale)                                     # below the lamp shade (z 2.3)
    return st, cam


def doc_card(st, base, u, v, w, h, title, lines, mat_key="ivory", deg=0.0, size=0.034, slide=None, tag=None, placeholder=0):
    """Paper card with a heading and short editorial lines (or grey placeholder bars for documents not yet imported)."""
    objs = [st.card(base, u, v, w, h, st.M[mat_key], deg=deg, thick=0.004)]
    top = v + h / 2 - size * 2.2
    objs.append(st.text(f"{base}_Title", title, u - w / 2 + size, top, size * 1.25, "CORONER_BLACK", "bold", d=0.006))
    y = top - size * 1.9
    for ln in lines:
        objs.append(st.text(f"{base}_Line", ln, u - w / 2 + size, y, size, "CORONER_BLACK", "regular", d=0.006))
        y -= size * 1.55
    for i in range(placeholder):                                         # placeholder bars: no AI-generated document text
        objs.append(st.card(f"{base}_Placeholder", u - w * 0.05, y - i * size * 1.5, w * 0.8, size * 0.45, st.M["grey"], d=0.005, thick=0.001))
    if tag:
        objs.append(st.source_tag(tag, u - w / 2 + size, v - h / 2 + size * 0.8, size * 0.75, d=0.006))
    if slide:
        root = A.empty(f"{st.name}_{base}_ROOT", st.c, tuple(st.p(u, v, 0)), 0.05)
        parent_keep(objs, root)
        st.slide_in(root, slide[0], slide[1], slide[2], slide[3])
        return root
    return objs[0]


# ---------------------------------------------------------------- PHASE 4/5: shot builders
B = {}


def shot(sid):
    def deco(fn):
        B[sid] = fn
        return fn
    return deco


@shot("S01")
def s01(x):
    light(x.c, "LGT_S01_Sun_Dusk", "SUN", (-900, -300, 260), 2.6, K["dusk"], target=(0, 0, 0), angle=math.radians(3))
    cam = CR.camera("CAM_S01", x.c, x.f0, x.f1, [(x.f0, (-560, -600, 150)), (x.f1, (-535, -575, 156))],
                    aim=[(x.f0, (0, 0, 70)), (x.f1, (0, 0, 74))], lens=28, move="slow_dolly_rise")
    cam.data.clip_end = 1600
    st = MG.Stage("TTL_S01", x.c, (0, 0, 0), "front", x.M, x.f0, x.f1)
    hw, hh = CR.frame_half_extent(cam, 1.0)
    for i, (txt, sz, kind) in enumerate((("DALLAS, TEXAS", 0.042, "bold"), ("SEPTEMBER 2000", 0.028, "regular"))):
        m = A.mat_fade(f"MAT_TXT_S01_{i}", A.pal("EVIDENCE_IVORY"), emit=0.8)
        t = A.text(f"TXT_S01_{i}", txt, x.c, (-hw * 0.9, hh * (0.62 - i * 0.12), -1.0), hh * 2 * sz, m, kind, rot=(0, 0, 0), parent=cam)
        A.key_fade(m, [(x.f0, 0), (x.f0 + 30 + 12 * i, 0), (x.f0 + 60 + 12 * i, 1), (x.f1 - 30, 1), (x.f1, 0)])
    return cam


@shot("S02")
def s02(x):
    light(x.c, "LGT_S02_Sun_Dusk", "SUN", (-900, -300, 260), 2.6, K["dusk"], target=(0, 0, 0), angle=math.radians(3))
    light(x.c, "LGT_S02_Lobby_Glow", "AREA", (0, -18.5, 5), 3500, K["warm"], 12, target=(0, -26, 1), cutoff=40)
    for i, (dx, y0, mat, delay) in enumerate(((-1.0, -39.0, "suit", 0), (0.2, -38.4, "suit_navy", 6), (1.35, -39.5, "suit", 3))):
        fg = A.Figure(f"FIG_S02_Visitor_{i}", x.c, x.M, x.M[mat])
        fg.animate(x.f0, x.f1, [(x.f0 + delay, (dx, y0), 90), (x.f1 - 20 + delay, (dx * 0.8, -25.5 - 0.4 * i), 90)])
        x.figs.append(fg)
    cam = CR.camera("CAM_S02", x.c, x.f0, x.f1, [(x.f0, (2.8, -45.5, 1.7)), (x.f1, (2.0, -34.0, 1.68))],
                    aim=[(x.f0, (0, -33, 1.35)), (x.f1, (0, -22, 1.5))], lens=35, fstop=5.6, focus=8.0, move="restrained_lateral_track")
    return cam


@shot("S03")
def s03(x):
    E = SETS["ENV_02_BOARDROOM"]
    boardroom_lights(x, E)
    return CR.camera("CAM_S03", x.c, x.f0, x.f1, [(x.f0, tuple(E + Vector((-4.45, -3.1, 1.62)))), (x.f1, tuple(E + Vector((-4.05, -2.95, 1.6))))],
                     aim=[(x.f0, tuple(E + Vector((1.2, 1.0, 0.95))))], lens=35, fstop=4.0, focus=5.5, move="slow_dolly")


def boardroom_lights(x, E, dim=1.0):
    for i, px in enumerate((-3.0, 0.0, 3.0)):
        light(x.c, f"LGT_{x.s['shot_id']}_Ceiling_{i}", "AREA", E + Vector((px, 0, 2.95)), 140 * dim, K["neutral"], 1.4, rot=(0, 0, 0), cutoff=12)
    light(x.c, f"LGT_{x.s['shot_id']}_Window_Daylight", "AREA", E + Vector((0, 4.6, 1.9)), 1500 * dim, K["cool"], 9.0,
          target=E + Vector((0, 0, 0.8)), cutoff=15)


FOLDER_REST = None


@shot("S04")
def s04(x):
    global FOLDER_REST
    E = SETS["ENV_02_BOARDROOM"]
    boardroom_lights(x, E)
    tz = ENV.BOARDROOM["table"][2]
    folder = A.box("PROP_S04_Folder_Plain", x.c, (0, 0, 0), (0.31, 0.235, 0.012), x.M["ivory"], bevel=0.002)
    hand = A.Hand("HAND_S04", x.c, x.M, x.M["suit"])
    yaw = 75.0
    R = Matrix.Rotation(math.radians(yaw), 4, "Z")
    off = Vector((0.1, 0, -0.0125 - 0.006))
    rest_c = E + Vector((-0.35, -0.3, tz + 0.006))
    wrist_rel = rest_c - (R.to_3x3() @ off)
    start = wrist_rel + Vector((-0.25, -0.6, 0.28))
    keys = [(x.f0, tuple(start), (0, yaw)), (x.f0 + 130, tuple(wrist_rel + Vector((0, 0, 0.035))), (0, yaw)),
            (x.f0 + 152, tuple(wrist_rel), (0, yaw)), (x.f0 + 166, tuple(wrist_rel), (0, yaw)),
            (x.f1 - 10, tuple(wrist_rel + Vector((-0.12, -0.55, 0.2))), (8, yaw)), (x.f1, tuple(wrist_rel + Vector((-0.12, -0.55, 0.2))), (8, yaw))]
    folder.matrix_world = Matrix.Translation(start) @ R @ Matrix.Translation(off)
    hand.animate(keys, prop=folder, grab=x.f0, release=x.f0 + 166)
    FOLDER_REST = Matrix.Translation(wrist_rel) @ R @ Matrix.Translation(off)
    x.checks["folder_rest_z"] = (folder.name, tz, x.f0 + 170)
    x.checks["hand_contact"] = (hand.name, folder.name, (x.f0 + 152, x.f0 + 166))
    return CR.camera("CAM_S04", x.c, x.f0, x.f1, [(x.f0, tuple(E + Vector((-1.3, -1.6, 1.22)))), (x.f1, tuple(E + Vector((-1.18, -1.47, 1.18))))],
                     aim=[(x.f0, tuple(rest_c + Vector((0, 0, 0.02))))], lens=50, fstop=2.8, focus=folder, move="controlled_push_in")


@shot("S43")
def s43(x):
    E = SETS["ENV_02_BOARDROOM"]
    boardroom_lights(x, E, 0.75)
    f = A.box("PROP_S43_Folder_Plain", x.c, (0, 0, 0), (0.31, 0.235, 0.012), x.M["ivory"], bevel=0.002)
    f.matrix_world = FOLDER_REST                                     # exactly where it was set down in S04
    cam = CR.camera("CAM_S43", x.c, x.f0, x.f1, [(x.f0, tuple(E + Vector((3.6, -2.95, 1.55)))), (x.f1, tuple(E + Vector((3.05, -2.5, 1.45))))],
                    aim=[(x.f0, tuple(FOLDER_REST.translation + Vector((0, 0, 0.05))))], lens=35, fstop=4.0, focus=f, move="slow_push_in")
    slate(x, cam, "A FAMOUS BUT DISPUTED MOMENT  ·  ACCOUNTS DIFFER")
    return cam


def store_lights(x, E, n_on=4, scale=1.0, temp="fluoro"):
    for i in range(n_on):
        light(x.c, f"LGT_{x.s['shot_id']}_Fluoro_{i}", "AREA", E + Vector((-6 + 4 * i, 2.5, 3.5)), 700 * scale, K[temp], 3.5,
              rot=(0, 0, 0), cutoff=14)


@shot("S09")
def s09(x):
    E = SETS["ENV_03_BLOCKBUSTER_STORE"]
    store_lights(x, E, 4, 1.4)
    light(x.c, "LGT_S09_Lot_Pole", "SPOT", E + Vector((-9, -14, 7)), 2500, (1.0, 0.86, 0.6), 0.3, target=E + Vector((-3, -8, 0)), cutoff=40)
    light(x.c, "LGT_S09_Fascia_Wash", "SPOT", E + Vector((0, -11, 1.0)), 900, K["neutral"], 0.2, target=E + Vector((0, -6.2, 4.3)), cutoff=20)
    for i, (px, py) in enumerate(((-15, -14), (9, -15), (13, -14.5))):
        A.box(f"PROP_S09_Car_{i}", x.c, tuple(E + Vector((px, py, 0.7))), (1.8, 4.4, 1.3), x.M["metal_paint"], bevel=0.25)
    specs = [("A", "casual_a", [(x.f0, (-11.0, -7.7), 0), (x.f1 - 10, (-2.6, -7.6), 10)]),
             ("B", "casual_b", [(x.f0 + 20, (9.0, -7.9), 180), (x.f1, (2.8, -7.4), 160)]),
             ("C", "casual_c", [(x.f0, (-1.0, -7.1), 90), (x.f1, (-1.0, -7.1), 90)])]
    for nm, mat, path in specs:
        fg = A.Figure(f"FIG_S09_Customer_{nm}", x.c, x.M, x.M[mat])
        fg.animate(x.f0, x.f1, [(f, tuple(E.to_2d() + Vector(p)), yaw) for f, p, yaw in path])
        x.figs.append(fg)
    cam = CR.camera("CAM_S09", x.c, x.f0, x.f1, [(x.f0, tuple(E + Vector((-7.6, -21.5, 1.55)))), (x.f1, tuple(E + Vector((-6.6, -20.4, 1.55))))],
                    aim=[(x.f0, tuple(E + Vector((0, -6, 2.4))))], lens=28, move="slow_dolly")
    slate(x, cam, "SIGNAGE OMITTED PENDING APPROVED BRAND REFERENCE")
    return cam


@shot("S10")
def s10(x):
    E = SETS["ENV_03_BLOCKBUSTER_STORE"]
    store_lights(x, E, 4, 1.2)
    shelf = lambda f: E + Vector((-2.4, 4.3, 1.12))  # noqa: E731
    for nm, mat, path, arm in (("A", "casual_a", [(x.f0, (-4.15, 2.6), 180)], None),
                               ("B", "casual_c", [(x.f0, (-2.9, 4.4), 0)], {"R": shelf}),
                               ("C", "casual_b", [(x.f0 + 30, (-3.6, 7.2), -90), (x.f1 - 30, (-3.5, 5.7), -90)], None)):
        fg = A.Figure(f"FIG_S10_Customer_{nm}", x.c, x.M, x.M[mat])
        fg.animate(x.f0, x.f1, [(f, tuple(E.to_2d() + Vector(p)), yaw) for f, p, yaw in path],
                   head_keys=(lambda f, n=nm: (25 * math.sin((f - x.f0) / 60.0 + (1 if n == "A" else 0)), 12)), arm_targets=arm)
        x.figs.append(fg)
    return CR.camera("CAM_S10", x.c, x.f0, x.f1, [(x.f0, tuple(E + Vector((-3.5, -1.9, 1.62)))), (x.f1, tuple(E + Vector((-3.5, 0.35, 1.6))))],
                     aim=[(x.f0, tuple(E + Vector((-3.5, 8, 1.3)))), (x.f1, tuple(E + Vector((-3.4, 8, 1.25))))], lens=35, fstop=4.0, focus=5.0,
                     move="slow_dolly")


def counter_props(x, E, tag):
    top = 1.08
    objs = []
    for i, (px, py, mat) in enumerate(((4.82, -3.12, 2), (5.02, -3.18, 5))):
        objs.append(A.box(f"PROP_{tag}_MediaCase_{i}", x.c, tuple(E + Vector((px, py, top + 0.01))), (0.135, 0.19, 0.02), x.M["case_colors"][mat],
                          rot=(0, 0, 0.1 * i)))
    objs.append(A.box(f"PROP_{tag}_MembershipCard", x.c, tuple(E + Vector((4.6, -3.08, top + 0.0005))), (0.085, 0.054, 0.001), x.M["blue"]))
    objs.append(A.box(f"PROP_{tag}_Receipt", x.c, tuple(E + Vector((5.3, -3.05, top + 0.0005))), (0.08, 0.2, 0.001), x.M["paper_white"]))
    return objs


@shot("S11")
def s11(x):
    E = SETS["ENV_03_BLOCKBUSTER_STORE"]
    store_lights(x, E, 4, 1.2)
    counter_props(x, E, "S11")
    clerk = A.Figure("FIG_S11_Clerk", x.c, x.M, x.M["casual_b"])
    clerk.animate(x.f0, x.f1, [(x.f0, tuple(E.to_2d() + Vector((5.0, -2.15))), -90)],
                  arm_targets={"L": lambda f: E + Vector((4.75, -2.78, 1.2)), "R": lambda f: E + Vector((5.28 + 0.05 * math.sin((f - x.f0) / 20), -2.78, 1.2))})
    cust = A.Figure("FIG_S11_Customer", x.c, x.M, x.M["casual_a"])
    cust.animate(x.f0, x.f1, [(x.f0, tuple(E.to_2d() + Vector((4.85, -4.05))), 90)],
                 arm_targets={"R": lambda f: E + Vector((4.95, -3.3, 1.19))})
    x.figs += [clerk, cust]
    return CR.camera("CAM_S11", x.c, x.f0, x.f1, [(x.f0, tuple(E + Vector((3.3, -5.4, 1.62)))), (x.f1, tuple(E + Vector((3.5, -5.15, 1.58))))],
                     aim=[(x.f0, tuple(E + Vector((5.0, -3.0, 1.25))))], lens=50, fstop=2.8, focus=2.8, move="locked_observation_drift")


@shot("S31")
def s31(x):
    E = SETS["ENV_03_BLOCKBUSTER_STORE"]
    store_lights(x, E, 4, 1.2)
    counter_props(x, E, "S31")
    top = 1.08
    mailer = A.box("PROP_S31_Mailer_EditorialBlue", x.c, (0, 0, 0), (0.19, 0.135, 0.006), x.M["blue"])
    hand = A.Hand("HAND_S31", x.c, x.M, x.M["casual_a"])
    yaw = 80.0
    R = Matrix.Rotation(math.radians(yaw), 4, "Z")
    off = Vector((0.1, 0, -0.0125 - 0.003))
    rest_c = E + Vector((4.55, -3.2, top + 0.003))
    wr = rest_c - (R.to_3x3() @ off)
    start = wr + Vector((-0.3, -0.6, 0.25))
    keys = [(x.f0, tuple(start), (0, yaw)), (x.f0 + 120, tuple(wr + Vector((0, 0, 0.03))), (0, yaw)), (x.f0 + 140, tuple(wr), (0, yaw)),
            (x.f0 + 156, tuple(wr), (0, yaw)), (x.f1 - 15, tuple(wr + Vector((-0.15, -0.55, 0.2))), (8, yaw)), (x.f1, tuple(wr + Vector((-0.15, -0.55, 0.2))), (8, yaw))]
    mailer.matrix_world = Matrix.Translation(start) @ R @ Matrix.Translation(off)
    hand.animate(keys, prop=mailer, grab=x.f0, release=x.f0 + 156)
    x.checks["mailer_rest_z"] = (mailer.name, top, x.f0 + 160)
    cam = CR.camera("CAM_S31", x.c, x.f0, x.f1, [(x.f0, tuple(E + Vector((3.8, -4.35, 1.5)))), (x.f1, tuple(E + Vector((3.92, -4.2, 1.47))))],
                    aim=[(x.f0, tuple(rest_c + Vector((0.1, 0, 0.02))))], lens=50, fstop=2.8, focus=mailer, move="controlled_push_in")
    slate(x, cam, "TOTAL ACCESS (NOV 2006): MAILED DISCS RETURNED IN STORE  ·  MAILER STYLING EDITORIAL")
    return cam


@shot("S42")
def s42(x):
    E = SETS["ENV_07_DECLINING_STORE"]
    store_lights(x, E, 2, 0.55, "cool")
    cam = CR.camera("CAM_S42", x.c, x.f0, x.f1, [(x.f0, tuple(E + Vector((0.6, -5.1, 1.6)))), (x.f1, tuple(E + Vector((0.35, -3.9, 1.6))))],
                    aim=[(x.f0, tuple(E + Vector((-1.5, 6, 1.2))))], lens=35, fstop=4.0, focus=6.0, move="slow_dolly")
    slate(x, cam, "REPRESENTATIVE STORE  ·  NOT A SPECIFIC LOCATION")
    return cam


def warehouse_lights(x, E):
    for i in range(3):
        light(x.c, f"LGT_{x.s['shot_id']}_Pendant_{i}", "AREA", E + Vector((-10 + 5 * i, -1.5, 6.4)), 1800, K["fluoro"], 2.5, rot=(0, 0, 0), cutoff=20)


@shot("S17")
def s17(x):
    E = SETS["ENV_04_DVD_FULFILLMENT"]
    warehouse_lights(x, E)
    light(x.c, "LGT_S17_Task", "AREA", E + Vector((-9.0, -4.6, 1.9)), 90, K["warm"], 0.6, target=E + Vector((-9.0, -4.05, 0.93)), cutoff=6)
    top = 0.925
    env_c = E + Vector((-9.0, -4.05, top + 0.002))
    A.box("PROP_S17_Envelope_EditorialRed", x.c, tuple(env_c), (0.19, 0.135, 0.004), x.M["nred"])
    A.box("PROP_S17_Envelope_Flap", x.c, tuple(env_c + Vector((-0.11, 0, 0.0))), (0.03, 0.135, 0.002), x.M["nred"], rot=(0, math.radians(-25), 0))
    disc = A.obj("PROP_S17_DVD", A.mesh_cyl("PROP_S17_DVD", 0.06, 0.0012, x.M["steel"], 32), x.c)
    hand = A.Hand("HAND_S17", x.c, x.M, x.M["casual_b"])
    off = Vector((0.13, 0, -0.0125 - 0.0012))
    final = env_c + Vector((0.0, 0.0, 0.0004))
    wr_final = final - off
    wr_pre = wr_final - Vector((0.12, 0, 0))
    start = wr_pre + Vector((-0.45, -0.45, 0.22))
    keys = [(x.f0, tuple(start), (0, 0)), (x.f0 + 110, tuple(wr_pre + Vector((0, 0, 0.02))), (0, 0)), (x.f0 + 135, tuple(wr_pre), (0, 0)),
            (x.f0 + 178, tuple(wr_final), (0, 0)), (x.f0 + 186, tuple(wr_final), (0, 0)), (x.f1 - 10, tuple(wr_final + Vector((-0.35, -0.35, 0.18))), (6, 0)),
            (x.f1, tuple(wr_final + Vector((-0.35, -0.35, 0.18))), (6, 0))]
    disc.matrix_world = Matrix.Translation(start) @ Matrix.Translation(off)
    hand.animate(keys, prop=disc, grab=x.f0, release=x.f0 + 186)
    x.checks["disc_in_envelope"] = (disc.name, tuple(final), x.f0 + 190)
    return CR.camera("CAM_S17", x.c, x.f0, x.f1, [(x.f0, tuple(E + Vector((-9.05, -4.78, 1.38)))), (x.f1, tuple(E + Vector((-9.05, -4.7, 1.34))))],
                     aim=[(x.f0, tuple(env_c))], lens=85, fstop=4.0, focus=0.85, move="controlled_push_in")


@shot("S18")
def s18(x):
    E = SETS["ENV_04_DVD_FULFILLMENT"]
    warehouse_lights(x, E)
    belt_z = 0.87
    for i in range(14):
        o = A.box(f"PROP_S18_Envelope_{i:02d}", x.c, (0, 0, 0), (0.19, 0.135, 0.006), x.M["nred"], rot=(0, 0, 0.05 * ((i % 3) - 1)))
        for f in (x.f0, x.f1):
            o.location = E + Vector((-9.0 + 0.75 * i + 0.45 * (f - x.f0) / C.FPS, 0.02 * ((i % 4) - 1.5), belt_z + 0.003))
            o.keyframe_insert("location", frame=f)
        A.bake(o, "location", [(f, tuple(E + Vector((-9.0 + 0.75 * i + 0.45 * (f - x.f0) / C.FPS, 0.02 * ((i % 4) - 1.5), belt_z + 0.003))))
                               for f in range(x.f0, x.f1 + 1, 12)] + [(x.f1, tuple(E + Vector((-9.0 + 0.75 * i + 0.45 * (x.f1 - x.f0) / C.FPS,
                                                                                               0.02 * ((i % 4) - 1.5), belt_z + 0.003))))])
    return CR.camera("CAM_S18", x.c, x.f0, x.f1, [(x.f0, tuple(E + Vector((-4.4, -1.55, 1.3)))), (x.f1, tuple(E + Vector((-2.9, -1.55, 1.3))))],
                     aim=[(x.f0, tuple(E + Vector((-3.2, 0, 0.88)))), (x.f1, tuple(E + Vector((-1.7, 0, 0.88))))], lens=35, fstop=4.0, focus=1.9,
                     move="restrained_lateral_track")


def desk_lights(x, D, night=False):
    light(x.c, f"LGT_{x.s['shot_id']}_ScreenGlow", "AREA", D + Vector((0, 0.45, 1.0)), 6 if night else 4, (0.6, 0.72, 0.9), 0.35,
          target=D + Vector((0, -0.6, 1.0)), cutoff=4, shadow=False)
    light(x.c, f"LGT_{x.s['shot_id']}_Room", "AREA", D + Vector((-1.2, -1.0, 2.4)), 30 if night else 160, K["warm"], 1.5,
          target=D + Vector((0, 0.5, 0.8)), cutoff=8)


@shot("S22")
def s22(x):
    D = SETS["SET_DESK_VIGNETTE"]
    desk_lights(x, D)
    cam = CR.camera("CAM_S22", x.c, x.f0, x.f1, [(x.f0, tuple(D + Vector((0.05, -0.3, 1.1)))), (x.f1, tuple(D + Vector((0.02, -0.08, 1.04))))],   # clear of the chair back (y -0.39)
                    aim=[(x.f0, tuple(D + Vector((0, 0.52, 1.0))))], lens=50, fstop=2.8, focus=0.8, move="controlled_push_in")
    slate(x, cam, "ILLUSTRATIVE SCREEN LAYOUT  ·  NO HISTORICAL WEB PAGE REPRODUCED")
    return cam


@shot("S25")
def s25(x):
    D = SETS["SET_DESK_VIGNETTE"]
    desk_lights(x, D)
    cam = CR.camera("CAM_S25", x.c, x.f0, x.f1, [(x.f0, tuple(D + Vector((0.8, -0.6, 1.28)))), (x.f1, tuple(D + Vector((0.66, -0.46, 1.22))))],
                    aim=[(x.f0, tuple(D + Vector((0, 0.55, 1.0))))], lens=35, fstop=4.0, focus=1.0, move="slow_push_in")
    hw, hh = CR.frame_half_extent(cam, 1.0)
    for i, (txt, col, sz, kind) in enumerate((("AUGUST 2004", "RETAIL_YELLOW", 0.05, "bold"), ("BLOCKBUSTER ONLINE  ·  BY-MAIL RENTAL LAUNCH", "EVIDENCE_IVORY", 0.03, "semibold"),
                                              ("LAUNCH MONTH PENDING VERIFICATION (SRC_BB_ONLINE_2004)", "VERDICT_RED", 0.022, "semibold"))):
        m = A.mat_fade(f"MAT_TXT_S25_{i}", A.pal(col), emit=0.8)
        A.text(f"TXT_S25_{i}", txt, x.c, (-hw * 0.9, hh * (0.6 - 0.14 * i), -1.0), hh * 2 * sz, m, kind, rot=(0, 0, 0), parent=cam)
        A.key_fade(m, [(x.f0, 0), (x.f0 + 20 + 10 * i, 0), (x.f0 + 45 + 10 * i, 1)])
    return cam


@shot("S36")
def s36(x):
    D = SETS["SET_DESK_VIGNETTE"]
    desk_lights(x, D, night=True)
    fg = A.Figure("FIG_S36_Viewer_Seated", x.c, x.M, x.M["casual_b"], seated=True)
    fg.animate(x.f0, x.f1, [(x.f0, tuple(D.to_2d() + Vector((0, -0.12))), 90)],
               arm_targets={"L": lambda f: D + Vector((-0.12, 0.33, 0.86)), "R": lambda f: D + Vector((0.3, 0.36, 0.86))},
               head_keys=lambda f: (0.0, 4.0))
    x.figs.append(fg)
    return CR.camera("CAM_S36", x.c, x.f0, x.f1, [(x.f0, tuple(D + Vector((0.8, -1.6, 1.45)))), (x.f1, tuple(D + Vector((0.62, -1.38, 1.4))))],
                     aim=[(x.f0, tuple(D + Vector((0, 0.5, 1.0))))], lens=35, fstop=2.8, focus=1.9, move="slow_push_in")


# ---------------- graphics stages (front, orthographic)
def big_number(x, value, sub, src, value_col="VERDICT_RED", pending_note=None):
    st, cam = gfx(x)
    st.text("Value", value, 0, 0.4, 2.0, value_col, "bold", "CENTER", fade=(x.f0 + 12, x.f0 + 40))
    st.text("Sub", sub, 0, -0.9, 0.42, "EVIDENCE_IVORY", "semibold", "CENTER", fade=(x.f0 + 40, x.f0 + 66))
    if pending_note:
        st.text("Pending", pending_note, 0, -1.7, 0.28, "VERDICT_RED", "semibold", "CENTER", fade=(x.f0 + 60, x.f0 + 84))
    st.source_tag(src, -7.4, -3.9, 0.2)
    return st, cam


@shot("S07")
def s07(x):
    st, cam = big_number(x, "$50,000,000", "ATTRIBUTED TO MARC RANDOLPH'S ACCOUNT", "SRC_RANDOLPH_2019")
    st.text("Note", "A RECOLLECTION, NOT A DOCUMENTED OFFER", 0, -1.7, 0.26, "ARCHIVE_GREY", "semibold", "CENTER", fade=(x.f0 + 70, x.f0 + 95))
    return cam


@shot("S12")
def s12(x):
    st, cam = gfx(x, scale=(16.0, 14.5))
    rnd = random.Random(12)
    pts = [(rnd.uniform(-6.5, 6.5), rnd.uniform(-3.2, 3.2)) for _ in range(900)]
    st.dots("Network", pts, 0.07, x.M["yellow"], build=(x.f0 + 10, 170), order_from=(-1.0, 0.0))
    st.text("Title", "ONE STORE BECOMES THOUSANDS", -7.4, 3.6, 0.42, "EVIDENCE_IVORY", "bold", fade=(x.f0 + 5, x.f0 + 30))
    st.text("Note", "ILLUSTRATIVE  ·  NOT A MAP  ·  NOT TO SCALE", -7.4, -3.9, 0.2, "ARCHIVE_GREY", "semibold")
    return cam


@shot("S13")
def s13(x):
    st, cam = big_number(x, "≈ 9,100", "STORES WORLDWIDE  ·  YEAR-END 2004", "SRC_STORES_2004", "EVIDENCE_IVORY",
                         "FIGURE PENDING PRIMARY CHECK  ·  FY2004 FORM 10-K")
    return cam


@shot("S15")
def s15(x):
    st, cam = gfx(x)
    st.text("Title", "EXTENDED VIEWING FEES", -7.4, 3.4, 0.5, "EVIDENCE_IVORY", "bold", fade=(x.f0 + 5, x.f0 + 30))
    st.bar("RentalRevenue", -6.5, 0.2, 13.0, 1.2, x.M["grey"], grow=(x.f0 + 20, x.f0 + 80), direction="right")
    st.bar("FeeShare", -6.5, 0.2, 13.0 * 0.14, 1.2, x.M["red"], grow=(x.f0 + 90, x.f0 + 130), direction="right", d=-0.05)
    st.text("Share", "≈ 14% OF 2004 RENTAL REVENUE", -6.5, -0.95, 0.42, "VERDICT_RED", "bold", fade=(x.f0 + 120, x.f0 + 145))
    st.text("Rest", "TOTAL RENTAL REVENUE, 2004 (100%)", 6.5, 1.55, 0.26, "ARCHIVE_GREY", "semibold", "RIGHT", fade=(x.f0 + 60, x.f0 + 85))
    st.source_tag("SRC_BBI_10K_FY2005", -7.4, -3.5, 0.2)
    st.text("Dollar", "$622.4 MILLION (2004)  ·  VALUE PENDING PRIMARY CHECK", -6.5, -1.8, 0.3, "VERDICT_RED", "semibold", fade=(x.f0 + 150, x.f0 + 175))
    st.source_tag("SRC_EVF_2004", -7.4, -3.95, 0.2)
    return cam


def store_field(st, x, n_x=26, n_y=14, lit=True, build=None, reverse=False):
    """Miniature network of identical store blocks (illustrative)."""
    pts = [(-6.5 + 13.0 * i / (n_x - 1), -3.0 + 6.0 * j / (n_y - 1)) for i in range(n_x) for j in range(n_y)]
    st.dots("Stores", pts, 0.16, x.M["blue"], d=0.1)
    if lit:
        st.dots("StoreLights", pts, 0.1, A.mat_basic("MAT_StoreLight_Warm", (1.0, 0.8, 0.45), 0.5, emit=(1.0, 0.8, 0.45), strength=3.0),
                build=build, d=0.2, reverse=reverse)


@shot("S16")
def s16(x):
    st, cam = gfx(x, scale=(16.0, 15.2))
    store_field(st, x)
    st.text("Title", "A LARGE NETWORK IS HARD TO MOVE", -7.0, 3.55, 0.42, "EVIDENCE_IVORY", "bold", fade=(x.f0 + 20, x.f0 + 45))
    st.text("Note", "ILLUSTRATIVE", -7.0, -3.65, 0.2, "ARCHIVE_GREY", "semibold")
    return cam


@shot("S40")
def s40(x):
    st, cam = gfx(x, scale=(15.2, 16.0))
    store_field(st, x, build=(x.f0 + 20, 380), reverse=True)        # lights go out over time; most remain lit at the cut
    st.text("Title", "A DOMINANT MODEL BEGINS TO FADE", -7.0, 3.55, 0.42, "EVIDENCE_IVORY", "bold", fade=(x.f0 + 20, x.f0 + 45))
    st.text("Note", "ILLUSTRATIVE  ·  DOES NOT REPRESENT ACTUAL CLOSURES", -7.0, -3.65, 0.2, "ARCHIVE_GREY", "semibold")
    return cam


@shot("S19")
def s19(x):
    st, cam = gfx(x)
    labels = ["SUBSCRIBE", "RECEIVE", "WATCH", "RETURN"]
    for i, lab in enumerate(labels):
        a = math.radians(90 - 90 * i)
        u, v = 3.0 * math.cos(a), 2.2 * math.sin(a)
        st.ring(f"Node_{lab}", u, v, 0.45, 0.55, x.M["nred"])
        st.text(f"Lab_{lab}", lab, u, v - 1.0, 0.32, "EVIDENCE_IVORY", "semibold", "CENTER", fade=(x.f0 + 20 + 30 * i, x.f0 + 40 + 30 * i))
        a2 = math.radians(90 - 90 * (i + 1))
        st.line(f"Arrow_{i}", u, v, 3.0 * math.cos(a2), 2.2 * math.sin(a2), x.M["ivory"], 0.04, grow=(x.f0 + 40 + 30 * i, x.f0 + 62 + 30 * i))
    token = st.card("Token_Disc", 0, 2.2, 0.35, 0.35, x.M["steel"], d=0.1)
    for k, f in enumerate(range(x.f0 + 160, x.f1 + 1, 8)):
        a = math.radians(90 - 360 * k / 10)
        token.location = st.p(3.0 * math.cos(a), 2.2 * math.sin(a), 0.1)
        token.keyframe_insert("location", frame=f)
    st.text("Title", "THE SUBSCRIPTION LOOP", -7.4, 3.6, 0.42, "EVIDENCE_IVORY", "bold", fade=(x.f0 + 5, x.f0 + 30))
    st.text("Sub", "NO LATE FEES IN THIS MODEL", 0, -0.1, 0.3, "ARCHIVE_GREY", "semibold", "CENTER", fade=(x.f0 + 150, x.f0 + 175))
    st.source_tag("SRC_NFLX_NO_LATE_FEES", -7.4, -3.95, 0.2)
    return cam


def icon_store(st, x, u, v, s=1.0, tag="Store"):
    st.card(f"{tag}_Body", u, v, 2.4 * s, 1.4 * s, x.M["wall_paint"], d=0.05, thick=0.4)
    st.card(f"{tag}_Fascia", u, v + 0.85 * s, 2.6 * s, 0.35 * s, x.M["blue"], d=0.1, thick=0.45)
    st.card(f"{tag}_Door", u, v - 0.3 * s, 0.6 * s, 0.8 * s, x.M["glass_tint"], d=0.3, thick=0.02)


def icon_warehouse(st, x, u, v, s=1.0, tag="Warehouse"):
    st.card(f"{tag}_Body", u, v, 2.8 * s, 1.5 * s, x.M["metal_paint"], d=0.05, thick=0.4)
    st.card(f"{tag}_Roof", u, v + 0.85 * s, 3.0 * s, 0.25 * s, x.M["metal_dark"], d=0.1, thick=0.45)
    for k in range(3):
        st.card(f"{tag}_Envelope_{k}", u - 0.7 * s + 0.7 * s * k, v - 0.25 * s, 0.5 * s, 0.35 * s, x.M["nred"], d=0.3, thick=0.02)


@shot("S20")
def s20(x):
    st, cam = gfx(x)
    icon_store(st, x, -4.0, 0.3)
    icon_warehouse(st, x, 4.0, 0.3)
    st.line("Divider", 0, -3.0, 0, 3.0, x.M["grey"], 0.03, grow=(x.f0 + 10, x.f0 + 40))
    st.text("L", "RETAIL", -4.0, -1.7, 0.5, "EVIDENCE_IVORY", "bold", "CENTER", fade=(x.f0 + 30, x.f0 + 55))
    st.text("R", "MAIL-BASED", 4.0, -1.7, 0.5, "EVIDENCE_IVORY", "bold", "CENTER", fade=(x.f0 + 50, x.f0 + 75))
    st.text("Title", "TWO OPERATING MODELS", -7.4, 3.6, 0.42, "EVIDENCE_IVORY", "bold", fade=(x.f0 + 5, x.f0 + 30))
    return cam


@shot("S26")
def s26(x):
    st, cam = gfx(x)
    icon_store(st, x, -4.0, 0.3, tag="Stores")
    icon_warehouse(st, x, 4.0, 0.3, tag="Online")
    st.line("Link", -2.6, 0.3, 2.5, 0.3, x.M["yellow"], 0.05, grow=(x.f0 + 60, x.f0 + 110))
    st.text("L", "STORES", -4.0, -1.7, 0.5, "EVIDENCE_IVORY", "bold", "CENTER", fade=(x.f0 + 20, x.f0 + 45))
    st.text("R", "ONLINE (BY MAIL)", 4.0, -1.7, 0.5, "EVIDENCE_IVORY", "bold", "CENTER", fade=(x.f0 + 40, x.f0 + 65))
    st.text("Title", "TWO SYSTEMS, ONE COMPANY", -7.4, 3.6, 0.42, "EVIDENCE_IVORY", "bold", fade=(x.f0 + 5, x.f0 + 30))
    return cam


@shot("S21")
def s21(x):
    st, cam = gfx(x)
    for side, (u, labels, mat) in enumerate(((-3.6, ["STORE RENT", "INVENTORY", "STAFF", "LOGISTICS"], "blue"),
                                             (3.6, ["FULFILLMENT", "POSTAGE", "WAREHOUSE", "SUBSCRIBER ACQUISITION"], "nred"))):
        for i, lab in enumerate(labels):
            f = x.f0 + 20 + 22 * i + 10 * side
            blk = st.card(f"Block_{side}_{i}", u, -2.6 + 1.05 * i, 5.4, 0.9, x.M[mat], d=0.05, thick=0.3)
            st.slide_in(blk, 0, 4.0, f, f + 18)
            t = st.text(f"Lab_{side}_{i}", lab, u, -2.75 + 1.05 * i, 0.3, "EVIDENCE_IVORY", "semibold", "CENTER", d=0.4, fade=(f + 10, f + 24))
            st.slide_in(t, 0, 4.0, f, f + 18)
    st.text("Title", "DIFFERENT COSTS, DIFFERENT RISKS", -7.4, 3.6, 0.42, "EVIDENCE_IVORY", "bold", fade=(x.f0 + 5, x.f0 + 30))
    st.text("Note", "QUALITATIVE  ·  BLOCK SIZES ARE NOT TO SCALE", -7.4, -3.95, 0.2, "ARCHIVE_GREY", "semibold")
    return cam


@shot("S23")
def s23(x):
    st, cam = gfx(x)
    st.bar("Blockbuster", -3.2, -2.8, 4.2, 5.6, x.M["blue"], grow=(x.f0 + 20, x.f0 + 90))
    st.bar("Netflix", 3.2, -2.8, 0.6, 0.35, x.M["nred"], grow=(x.f0 + 90, x.f0 + 110))
    st.text("L", "BLOCKBUSTER", -3.2, -3.5, 0.4, "EVIDENCE_IVORY", "bold", "CENTER", fade=(x.f0 + 30, x.f0 + 55))
    st.text("R", "NETFLIX", 3.2, -3.5, 0.4, "EVIDENCE_IVORY", "bold", "CENTER", fade=(x.f0 + 95, x.f0 + 120))
    st.text("Title", "RELATIVE SIZE IN 2000", -7.4, 3.6, 0.42, "EVIDENCE_IVORY", "bold", fade=(x.f0 + 5, x.f0 + 30))
    st.text("Note", "NOT TO SCALE  ·  VALUES PENDING", 7.4, 3.65, 0.22, "VERDICT_RED", "semibold", "RIGHT")
    st.source_tag("SRC_SCALE_2000", -7.4, -4.25, 0.18)
    return cam


def title_card(x, lines, accent_idx=(), size=0.75, top=1.0):
    st, cam = gfx(x, scale=(16.0, 15.4))
    for i, ln in enumerate(lines):
        col = "VERDICT_RED" if i in accent_idx else "EVIDENCE_IVORY"
        st.text(f"Line_{i}", ln, 0, top - i * size * 1.45, size, col, "bold", "CENTER", fade=(x.f0 + 15 + 25 * i, x.f0 + 45 + 25 * i))
    return st, cam


@shot("S24")
def s24(x):
    st, cam = title_card(x, ["WAS THE THREAT", "OBVIOUS IN 2000?"], accent_idx=(1,), size=0.95, top=0.6)
    return cam


@shot("S47")
def s47(x):
    st, cam = title_card(x, ["RECOGNIZING CHANGE", "IS NOT THE SAME AS", "SURVIVING IT."], accent_idx=(2,), size=0.8, top=1.3)
    return cam


@shot("S48")
def s48(x):
    st, cam = gfx(x, scale=(16.0, 15.6))
    st.text("Brand", "BRAND CORONER", 0, 0.5, 1.3, "EVIDENCE_IVORY", "bold", "CENTER", fade=(x.f0 + 20, x.f0 + 60, x.f1 - 40, x.f1 - 8))
    st.text("Tag", "EVERY DECISION LEAVES EVIDENCE.", 0, -0.7, 0.45, "VERDICT_RED", "semibold", "CENTER", fade=(x.f0 + 60, x.f0 + 95, x.f1 - 40, x.f1 - 8))
    st.text("Case", "CASE 001  ·  COMPLETE", 0, -1.6, 0.28, "ARCHIVE_GREY", "semibold", "CENTER", fade=(x.f0 + 95, x.f0 + 125, x.f1 - 40, x.f1 - 8))
    return cam


def date_card(x, date, title, lines, src, accent="RETAIL_YELLOW"):
    st, cam = gfx(x)
    st.text("Date", date, -7.0, 1.8, 0.95, accent, "bold", fade=(x.f0 + 10, x.f0 + 40))
    st.text("Title", title, -7.0, 0.4, 0.7, "EVIDENCE_IVORY", "bold", fade=(x.f0 + 30, x.f0 + 60))
    for i, ln in enumerate(lines):
        st.text(f"Line_{i}", ln, -7.0, -0.6 - 0.55 * i, 0.34, "EVIDENCE_IVORY", "regular", fade=(x.f0 + 60 + 15 * i, x.f0 + 85 + 15 * i))
    st.line("Rule", -7.0, 1.45, 3.0, 1.45, x.M["grey"], 0.025, grow=(x.f0 + 20, x.f0 + 60))
    if src:
        st.source_tag(src, -7.0, -3.9, 0.2)
    return st, cam


@shot("S27")
def s27(x):
    st, cam = date_card(x, "JANUARY 1, 2005", "NO LATE FEES", ["Extended viewing fees ended at company-operated U.S. stores", "Editorial title card  ·  not a reproduction of campaign artwork"],
                        "SRC_BBI_10K_FY2004")
    return cam


@shot("S30")
def s30(x):
    st, cam = date_card(x, "NOVEMBER 2006", "TOTAL ACCESS", ["Online rentals by mail, with in-store returns and exchanges"], "SRC_TOTAL_ACCESS_2006",
                        accent="RETAIL_YELLOW")
    icon_store(st, x, 5.0, 1.6, 0.6, "TA_Store")
    icon_warehouse(st, x, 5.0, -1.0, 0.55, "TA_Mail")
    st.line("TA_Link", 5.0, 0.9, 5.0, -0.3, x.M["yellow"], 0.05, grow=(x.f0 + 100, x.f0 + 140))
    return cam


@shot("S35")
def s35(x):
    st, cam = date_card(x, "JANUARY 2007", "NETFLIX INSTANT VIEWING", ["Announced January 16, 2007", "Initially PC-based  ·  about 1,000 titles"],
                        "SRC_NFLX_INSTANT_2007", accent="NETFLIX_RED")
    return cam


@shot("S29")
def s29(x):
    st, cam = gfx(x)
    st.text("V1", "> $500 MILLION", -7.0, 1.6, 0.9, "VERDICT_RED", "bold", fade=(x.f0 + 10, x.f0 + 40))
    st.text("V1s", "REDUCTION IN RENTAL REVENUE (2005)", -7.0, 0.95, 0.32, "EVIDENCE_IVORY", "semibold", fade=(x.f0 + 30, x.f0 + 55))
    st.source_tag("SRC_RENTAL_REDUCTION_2005", -7.0, 0.45, 0.2)
    st.text("V2", "≈ $60 MILLION", -7.0, -0.8, 0.9, "VERDICT_RED", "bold", fade=(x.f0 + 70, x.f0 + 100))
    st.text("V2s", "INITIAL MARKETING AND IMPLEMENTATION COSTS (H1 2005)", -7.0, -1.45, 0.32, "EVIDENCE_IVORY", "semibold", fade=(x.f0 + 90, x.f0 + 115))
    st.source_tag("SRC_BBI_10K_FY2005", -7.0, -1.95, 0.2)
    st.text("Rule", "REVENUE REDUCTION IS NOT THE SAME AS PROFIT LOSS", -7.0, -3.4, 0.28, "ARCHIVE_GREY", "semibold", fade=(x.f0 + 140, x.f0 + 165))
    return cam


@shot("S32")
def s32(x):
    st, cam = gfx(x)
    st.bar("Y2006", -2.5, -2.6, 2.0, 2.9, x.M["blue"], grow=(x.f0 + 20, x.f0 + 80))
    st.bar("Y2007", 2.5, -2.6, 2.0, 4.0, x.M["red"], grow=(x.f0 + 70, x.f0 + 130))
    st.text("L", "2006", -2.5, -3.3, 0.36, "EVIDENCE_IVORY", "semibold", "CENTER")
    st.text("R", "APR 2007", 2.5, -3.3, 0.36, "EVIDENCE_IVORY", "semibold", "CENTER")
    st.text("Lv", "2.2M", -2.5, 0.5, 0.5, "EVIDENCE_IVORY", "bold", "CENTER", fade=(x.f0 + 80, x.f0 + 100))
    st.text("Rv", "3M+", 2.5, 1.6, 0.5, "EVIDENCE_IVORY", "bold", "CENTER", fade=(x.f0 + 130, x.f0 + 150))
    st.text("Title", "TOTAL ACCESS SUBSCRIBERS", -7.4, 3.6, 0.42, "EVIDENCE_IVORY", "bold", fade=(x.f0 + 5, x.f0 + 30))
    st.text("Pending", "STORYBOARD VALUES  ·  PENDING VERIFICATION", 7.4, 3.65, 0.22, "VERDICT_RED", "semibold", "RIGHT")
    st.source_tag("SRC_TA_SUBSCRIBERS", -7.4, -4.25, 0.18)
    return cam


@shot("S33")
def s33(x):
    st, cam = gfx(x)
    for i, h in enumerate((1.0, 1.6, 2.3, 3.1)):
        st.bar(f"Subs_{i}", -6.0 + 1.1 * i, -0.2, 0.8, h, x.M["blue"], grow=(x.f0 + 20 + 15 * i, x.f0 + 50 + 15 * i))
    for i, h in enumerate((0.6, 1.1, 1.6, 2.3)):
        st.bar(f"Loss_{i}", 2.0 + 1.1 * i, -0.2, 0.8, h, x.M["red"], grow=(x.f0 + 80 + 15 * i, x.f0 + 110 + 15 * i), direction="down")
    st.line("Axis", -6.8, -0.2, 6.8, -0.2, x.M["grey"], 0.03)
    st.text("L", "SUBSCRIBERS UP", -6.6, 3.2, 0.36, "EVIDENCE_IVORY", "semibold")
    st.text("R", "BUT LOSSES GROW", 2.0, 0.4, 0.36, "EVIDENCE_IVORY", "semibold")
    st.text("Note", "ILLUSTRATIVE TREND  ·  NO VALUES SHOWN", -7.4, -3.95, 0.2, "ARCHIVE_GREY", "semibold")
    return cam


@shot("S34")
def s34(x):
    st, cam = gfx(x)
    for i, (lab, mat, u) in enumerate((("RETAIL", "blue", -4.2), ("MAIL", "nred", 0.0), ("STREAMING", "yellow", 4.2))):
        r = st.ring(f"Gear_{lab}", u, 0.2, 1.3, 1.75, x.M[mat], seg=12)
        for f, a in ((x.f0, 0.0), (x.f1, (1 if i % 2 == 0 else -1) * 60.0)):
            r.rotation_euler = (0, math.radians(a), 0)
            r.keyframe_insert("rotation_euler", frame=f)
        st.text(f"Lab_{lab}", lab, u, -2.4, 0.42, "EVIDENCE_IVORY", "bold", "CENTER", fade=(x.f0 + 20 + 30 * i, x.f0 + 45 + 30 * i))
    st.text("Title", "THREE BUSINESS MODELS", -7.4, 3.6, 0.42, "EVIDENCE_IVORY", "bold", fade=(x.f0 + 5, x.f0 + 30))
    return cam


@shot("S37")
def s37(x):
    st, cam = gfx(x)
    for i, (lab, mat, v) in enumerate((("DVD BY MAIL", "nred", 2.0), ("RETAIL STORES", "blue", 0.0), ("STREAMING", "yellow", -2.0))):
        st.card(f"Icon_{i}", -5.8, v, 0.8, 0.8, x.M[mat], d=0.1, thick=0.2)
        st.text(f"Lab_{i}", lab, -5.1, v - 0.15, 0.36, "EVIDENCE_IVORY", "semibold", fade=(x.f0 + 15 + 20 * i, x.f0 + 40 + 20 * i))
        st.line(f"Track_{i}", -1.5, v, 4.6, 0.0, x.M[mat], 0.05, grow=(x.f0 + 60 + 20 * i, x.f0 + 120 + 20 * i))
    st.card("Home", 5.2, 0.0, 1.2, 1.2, x.M["ivory"], d=0.1, thick=0.2)
    st.text("HomeLab", "THE SAME EVENING AT HOME", 5.2, -1.1, 0.26, "EVIDENCE_IVORY", "semibold", "CENTER", fade=(x.f0 + 130, x.f0 + 155))
    st.text("Title", "THREE CHANNELS COMPETE", -7.4, 3.6, 0.42, "EVIDENCE_IVORY", "bold", fade=(x.f0 + 5, x.f0 + 30))
    return cam


@shot("S39")
def s39(x):
    st, cam = gfx(x)
    for i, lab in enumerate(("OBLIGATIONS", "LIQUIDITY", "DEBT")):
        f = x.f0 + 20 + 35 * i
        blk = st.card(f"Block_{i}", 0, -2.4 + 1.3 * i, 7.5, 1.15, x.M["grey"] if i < 2 else x.M["red"], d=0.05, thick=0.4)
        st.slide_in(blk, 0, 5.0, f, f + 24)
        t = st.text(f"Lab_{i}", lab, 0, -2.55 + 1.3 * i, 0.42, "CORONER_BLACK", "bold", "CENTER", d=0.5, fade=(f + 14, f + 30))
        st.slide_in(t, 0, 5.0, f, f + 24)
    st.text("Title", "LESS ROOM TO MANEUVER", -7.4, 3.6, 0.42, "EVIDENCE_IVORY", "bold", fade=(x.f0 + 5, x.f0 + 30))
    st.text("Note", "QUALITATIVE  ·  NOT TO SCALE", -7.4, -3.95, 0.2, "ARCHIVE_GREY", "semibold")
    return cam


@shot("S44")
def s44(x):
    st, cam = gfx(x)
    st.card("Root", -5.0, 0.0, 2.6, 1.0, x.M["ivory"], d=0.05, thick=0.1)
    st.text("RootLab", "SEPT 2000 MEETING", -5.0, -0.15, 0.3, "CORONER_BLACK", "bold", "CENTER", d=0.2)
    for i, (lab, v) in enumerate((("AN EARLIER DEAL", 2.4), ("DIFFERENT TERMS", 0.0), ("A PARTNERSHIP", -2.4))):
        f = x.f0 + 40 + 30 * i
        for k in range(6):                                           # dashed line: hypothetical
            u0 = -3.6 + k * 0.85
            st.line(f"Dash_{i}_{k}", u0, v * (k / 6), u0 + 0.5, v * ((k + 0.6) / 6), x.M["grey"], 0.04, grow=(f + 4 * k, f + 4 * k + 6))
        st.card(f"Node_{i}", 3.6, v, 3.6, 0.95, x.M["grey"], d=0.05, thick=0.1)
        st.text(f"NodeLab_{i}", lab + "  ?", 3.6, v - 0.15, 0.32, "CORONER_BLACK", "bold", "CENTER", d=0.2, fade=(f + 20, f + 40))
    st.text("Title", "HYPOTHETICAL SCENARIOS", -7.4, 3.6, 0.42, "EVIDENCE_IVORY", "bold", fade=(x.f0 + 5, x.f0 + 30))
    st.text("Note", "POSSIBLE, BUT UNPROVEN OUTCOMES", -7.4, -3.95, 0.24, "VERDICT_RED", "semibold", fade=(x.f0 + 150, x.f0 + 175))
    return cam


@shot("S45")
def s45(x):
    st, cam = gfx(x)
    for i, (lab, v) in enumerate((("LEGACY ECONOMICS", 2.6), ("TRANSITION COSTS", 0.0), ("FINANCIAL CONSTRAINTS", -2.6))):
        st.text(f"Lab_{i}", lab, -7.2, v + 0.25, 0.36, "EVIDENCE_IVORY", "bold", fade=(x.f0 + 15 + 25 * i, x.f0 + 40 + 25 * i))
        st.line(f"Force_{i}", -7.2, v, 3.8, 0.0, x.M["red"] if i == 1 else x.M["grey"], 0.06, grow=(x.f0 + 60 + 20 * i, x.f0 + 140 + 20 * i))
    st.ring("Point", 4.2, 0.0, 0.25, 0.45, x.M["red"])
    st.text("Out", "A MORE COMPLEX EXPLANATION", 4.2, -1.0, 0.3, "EVIDENCE_IVORY", "semibold", "CENTER", fade=(x.f0 + 170, x.f0 + 195))
    st.text("Title", "THREE CONVERGING FORCES", -7.4, 3.9, 0.42, "EVIDENCE_IVORY", "bold", fade=(x.f0 + 5, x.f0 + 30))
    return cam


# ---------------- archive light table (flat, overhead orthographic)
def randolph_card(st, x, u, v, slide=True, deg=-2.0, base="Card_Randolph"):
    return doc_card(st, base, u, v, 1.0, 0.62, "ACCOUNT A  ·  MARC RANDOLPH",
                    ["Netflix co-founder", "Memoir: That Will Never Work (2019)", "Recalls a $50 million proposal and a", "reaction he read as dismissive.",
                     "LIKENESS: PENDING AUTHENTICATED PHOTO"], deg=deg, size=0.03, tag="SRC_RANDOLPH_2019",
                    slide=(-1.6, 0.0, x.f0 + 10, x.f0 + 50) if slide else None)


def antioco_card(st, x, u, v, slide=True, deg=1.5, base="Card_Antioco"):
    return doc_card(st, base, u, v, 1.0, 0.62, "ACCOUNT B  ·  JOHN ANTIOCO",
                    ["Blockbuster chief executive at the time", "Accounts attributed to him dispute key", "details of the meeting.",
                     "Primary statement not yet located.", "LIKENESS: PENDING AUTHENTICATED PHOTO"], deg=deg, size=0.03, tag="SRC_ANTIOCO_DISPUTE",
                    slide=(1.6, 0.0, x.f0 + 10, x.f0 + 50) if slide else None)


@shot("S05")
def s05(x):
    st, cam = archive(x, scale=(1.55, 1.42))
    randolph_card(st, x, 0.0, 0.05)
    return cam


@shot("S06")
def s06(x):
    st, cam = archive(x, scale=(1.55, 1.42))
    antioco_card(st, x, 0.0, 0.05)
    return cam


@shot("S08")
def s08(x):
    st, cam = archive(x, scale=(3.0, 2.8))
    randolph_card(st, x, -0.62, 0.12, slide=False, deg=-3)
    antioco_card(st, x, 0.62, 0.12, slide=False, deg=2)
    st.line("Thread", -0.1, 0.12, 0.1, 0.12, x.M["red"], 0.008, grow=(x.f0 + 30, x.f0 + 70), d=0.008)
    st.text("Question", "WHAT REALLY HAPPENED?", 0, -0.55, 0.11, "VERDICT_RED", "bold", "CENTER", d=0.008, fade=(x.f0 + 70, x.f0 + 110))
    return cam


@shot("S14")
def s14(x):
    st, cam = archive(x, scale=(2.2, 2.0))
    doc_card(st, "Receipt", -0.1, 0.0, 0.42, 0.95, "RENTAL RECEIPT", ["Title  ·  Format  ·  Price", "Rental period", "DUE DATE", "Extended viewing fee"],
             mat_key="paper_white", deg=-4, size=0.028, placeholder=8)
    ring = st.ring("DueDate_Circle", -0.15, 0.2, 0.09, 0.1, x.M["red"], d=0.01)
    for f, k in ((x.f0, 0.001), (x.f0 + 90, 0.001), (x.f0 + 120, 1.0)):
        ring.scale = (k, k, 1)
        ring.keyframe_insert("scale", frame=f)
    st.text("Label", "ILLUSTRATIVE RECEIPT  ·  NOT AN ARCHIVAL DOCUMENT", 0.32, -0.62, 0.032, "VERDICT_RED", "semibold", d=0.006)
    return cam


@shot("S28")
def s28(x):
    st, cam = archive(x, scale=(2.6, 2.3))
    doc_card(st, "Filing", -0.35, 0.0, 0.85, 1.1, "FORM 10-K  ·  FISCAL 2005", ["Editorial label  ·  import the verified filing scan here"],
             mat_key="paper_white", deg=-1.5, size=0.03, placeholder=14, tag="SRC_BBI_10K_FY2005")
    for i, (txt, v) in enumerate((("Fees eliminated: about 14% of 2004 rental revenues", 0.3), ("About $60M initial marketing and implementation costs", 0.05),
                                  ("Rental revenues down 5.0% from 2004", -0.2))):
        n = doc_card(st, f"Callout_{i}", 0.68, v, 0.78, 0.17, "FROM THE FILING", [txt], mat_key="ivory", deg=1, size=0.026,
                     slide=(0.9, 0.0, x.f0 + 40 + 30 * i, x.f0 + 70 + 30 * i))
    return cam


@shot("S38")
def s38(x):
    st, cam = archive(x, scale=(2.6, 2.4))
    for i, (u, v, deg) in enumerate(((-0.55, 0.1, -3), (0.0, -0.05, 2), (0.55, 0.08, -1))):
        doc_card(st, f"Sheet_{i}", u, v, 0.6, 0.85, "OPERATING COSTS", ["Editorial worksheet  ·  qualitative"], mat_key="paper_white", deg=deg,
                 size=0.026, placeholder=10, slide=(0.0, 1.4, x.f0 + 10 + 25 * i, x.f0 + 45 + 25 * i))
    st.line("Underline", -0.35, -0.38, 0.75, -0.38, x.M["red"], 0.008, grow=(x.f0 + 120, x.f0 + 160), d=0.01)
    st.text("Note", "TRANSITION PUTS PRESSURE ON MARGINS", -0.35, -0.48, 0.045, "VERDICT_RED", "bold", d=0.01, fade=(x.f0 + 150, x.f0 + 180))
    return cam


@shot("S41")
def s41(x):
    st, cam = archive(x, scale=(2.4, 2.2))
    doc_card(st, "Petition", -0.42, 0.0, 0.8, 1.05, "CHAPTER 11 FILING", ["September 23, 2010", "Import court petition / Form 8-K scan here"],
             mat_key="paper_white", deg=-2, size=0.032, placeholder=12, tag="SRC_BBI_CH11_2010")
    st.text("Date", "SEPTEMBER 23, 2010", 0.15, 0.35, 0.075, "VERDICT_RED", "bold", d=0.01, fade=(x.f0 + 60, x.f0 + 95))
    st.text("Sub", "CHAPTER 11 PROTECTION", 0.15, 0.25, 0.045, "EVIDENCE_IVORY", "semibold", d=0.01, fade=(x.f0 + 80, x.f0 + 110))
    return cam


@shot("S46")
def s46(x):
    st, cam = archive(x, scale=(2.2, 3.1), drift=((0, 0), (0.0, 0.05)))
    randolph_card(st, x, -0.95, 0.42, slide=False, deg=-4, base="Card_R")
    antioco_card(st, x, 0.15, 0.48, slide=False, deg=3, base="Card_A")
    doc_card(st, "Receipt", 1.1, 0.25, 0.32, 0.7, "RENTAL RECEIPT", ["Illustrative"], mat_key="paper_white", deg=6, size=0.024, placeholder=6)
    doc_card(st, "Filing10K", -0.85, -0.4, 0.7, 0.5, "FORM 10-K  ·  FY2005", ["Scan pending import"], mat_key="paper_white", deg=2, size=0.026, placeholder=5)
    doc_card(st, "Ch11", 0.25, -0.45, 0.7, 0.5, "CHAPTER 11  ·  SEPT 23, 2010", ["Scan pending import"], mat_key="paper_white", deg=-3, size=0.026, placeholder=5)
    doc_card(st, "Instant", 1.15, -0.45, 0.5, 0.4, "JAN 2007", ["Instant viewing (Netflix)"], mat_key="ivory", deg=5, size=0.024)
    for i, (a, b) in enumerate((((-0.95, 0.42), (0.15, 0.48)), ((0.15, 0.48), (0.25, -0.45)), ((-0.85, -0.4), (0.25, -0.45)), ((0.25, -0.45), (1.15, -0.45)))):
        st.line(f"Thread_{i}", a[0], a[1], b[0], b[1], x.M["red"], 0.006, grow=(x.f0 + 40 + 25 * i, x.f0 + 80 + 25 * i), d=0.012)
    return cam


# ---------------------------------------------------------------- shot assembly
def build_shots(only=None):
    M = A.library()
    root = A.coll("SHOTS")
    results = {}
    order = [s for s in C.SHOTS if (only is None or s["shot_id"] in only)]
    # S04 must be built before S43 (folder continuity)
    order.sort(key=lambda s: (0 if s["shot_id"] == "S04" else 1, s["index"]))
    for s in order:
        sid = s["shot_id"]
        c = A.coll(f"SHOT_{sid}", root)
        idx = s["index"] - 1
        origin = Vector((8000 + (idx % 8) * 60, 1000 + (idx // 8) * 40, 10))
        x = SimpleNamespace(s=s, f0=s["frame_start"], f1=s["frame_end"], c=c, M=M, origin=origin, figs=[], checks={})
        cam = B[sid](x)
        if cam.name != s["camera"]:
            cam.name = s["camera"]
        if s["reconstruction"] or s["source_ids"]:
            if not any(o.name.startswith(f"SLATE_{sid}") for o in c.objects):
                slate(x, cam)
        cam["shot_id"] = sid
        results[sid] = dict(camera=cam.name, figures=[f.name for f in x.figs], checks=x.checks,
                            feet={f.name: {str(k): v for k, v in f.feet_log.items()} for f in x.figs if hasattr(f, "feet_log")})
    world_keys()
    return results


if __name__ == "__main__":
    import json
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    only = None
    if "--shots" in argv:
        only = set(f"S{int(v):02d}" for v in argv[argv.index("--shots") + 1].split(","))
    setup_scene()
    M = A.library()
    build_sets(M)
    res = build_shots(only)
    checkpoint("PHASE 4-5 shots + graphics built")
    TL.assemble(res)
    checkpoint("PHASE 6-7 timeline, narration markers, audio placeholders")
    feet = {k: v.pop("feet") for k, v in res.items()}
    with open(os.path.join(C.P["metadata"], "build_results.json"), "w") as fh:
        json.dump(res, fh, indent=2, default=str)
    with open(os.path.join(C.P["metadata"], "figure_feet_log.json"), "w") as fh:
        json.dump({k: {fn: {s: [(f, list(p), sw) for f, p, sw in rows] for s, rows in d.items()} for fn, d in v.items()} for k, v in feet.items()},
                  fh, default=str)
    print("BUILD_DONE", len(res), "shots")
