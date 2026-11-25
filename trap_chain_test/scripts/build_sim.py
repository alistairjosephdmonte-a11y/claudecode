"""Mousetrap chain-reaction rigid-body test.

    blender -b --factory-startup --python scripts/build_sim.py -- [cols rows frames out.blend]

Each trap is a pine base plus a spring bar (U wire) on a hinge. A set trap holds its bar with a FIXED "latch"
constraint; firing it disables the latch and enables an angular MOTOR so the bar whips 180 degrees, and the
reaction kicks the base off the floor. A trap fires when a moving body enters the space just above its top face,
or when it is knocked (tilted or shoved). Bullet cannot fire constraints on contact, so the script steps the
simulation frame by frame, detects those events itself and keys the constraints on the next frame. The finished
motion is then baked to plain keyframes so the scene renders without the cache.
"""

import math
import os
import random
import sys

import bpy
from bpy_extras import anim_utils
import numpy as np
from mathutils import Euler, Matrix, Vector

ARGS = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
COLS = int(ARGS[0]) if len(ARGS) > 0 else 16
ROWS = int(ARGS[1]) if len(ARGS) > 1 else 20
FRAMES = int(ARGS[2]) if len(ARGS) > 2 else 360
OUT = ARGS[3] if len(ARGS) > 3 else os.path.join(os.path.dirname(__file__), "..", "scenes", "trap_chain.blend")

SEED = 7
TIME_SCALE = 0.5          # slow motion: 1 s of film = 0.5 s of physics
SUBSTEPS = 50
ITERATIONS = 30

BASE_L, BASE_W, BASE_T = 0.098, 0.045, 0.008
BAR_L, BAR_W, WIRE = 0.040, 0.040, 0.0016
PITCH_X, PITCH_Y = 0.122, 0.07
MASS_BASE, MASS_BAR = 0.016, 0.007
MOTOR_VEL, MOTOR_IMPULSE = -400.0, 0.04
PP_R, PP_MASS = 0.020, 0.0027
BALL_R, BALL_MASS = 0.032, 0.045
MARGIN = 0.0005
TOP = BASE_T / 2           # base top face in base-local space (origin at the board's centre)

MOVE_EPS = 0.25 * TIME_SCALE / 24.0     # per-frame displacement of a body moving at 0.25 m/s (physics time)
TILT_COS = math.cos(math.radians(8))
SHOVE = 0.004                            # base displacement since start that counts as a knock

random.seed(SEED)


def reset():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    sc.unit_settings.system = "METRIC"
    sc.render.fps = 24
    sc.frame_start, sc.frame_end = 1, FRAMES
    return sc


def mat(name, color, rough=0.5, metal=0.0, extra=None):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    p = nt.nodes["Principled BSDF"]
    p.inputs["Base Color"].default_value = (*color, 1)
    p.inputs["Roughness"].default_value = rough
    p.inputs["Metallic"].default_value = metal
    if extra:
        extra(nt, p)
    return m


def wood_grain(dark, light, scale, bump=0.15):
    def f(nt, p):
        tc = nt.nodes.new("ShaderNodeTexCoord")
        mp = nt.nodes.new("ShaderNodeMapping")
        mp.inputs["Scale"].default_value = (scale * 0.12, scale, scale)
        wv = nt.nodes.new("ShaderNodeTexWave")
        wv.wave_type = "BANDS"
        wv.bands_direction = "Y"
        wv.inputs["Scale"].default_value = 3.0
        wv.inputs["Distortion"].default_value = 6.0
        wv.inputs["Detail"].default_value = 3.0
        ramp = nt.nodes.new("ShaderNodeValToRGB")
        ramp.color_ramp.elements[0].color = (*dark, 1)
        ramp.color_ramp.elements[1].color = (*light, 1)
        bp = nt.nodes.new("ShaderNodeBump")
        bp.inputs["Strength"].default_value = bump
        nt.links.new(tc.outputs["Object"], mp.inputs["Vector"])
        nt.links.new(mp.outputs["Vector"], wv.inputs["Vector"])
        nt.links.new(wv.outputs["Fac"], ramp.inputs["Fac"])
        nt.links.new(ramp.outputs["Color"], p.inputs["Base Color"])
        nt.links.new(wv.outputs["Fac"], bp.inputs["Height"])
        nt.links.new(bp.outputs["Normal"], p.inputs["Normal"])
    return f


def floor_planks(nt, p):
    tc = nt.nodes.new("ShaderNodeTexCoord")
    br = nt.nodes.new("ShaderNodeTexBrick")
    br.offset = 0.5
    br.inputs["Scale"].default_value = 1.0
    br.inputs["Brick Width"].default_value = 1.1
    br.inputs["Row Height"].default_value = 0.14
    br.inputs["Mortar Size"].default_value = 0.002
    br.inputs["Color1"].default_value = (0.20, 0.11, 0.06, 1)
    br.inputs["Color2"].default_value = (0.29, 0.17, 0.09, 1)
    br.inputs["Mortar"].default_value = (0.04, 0.025, 0.015, 1)
    ns = nt.nodes.new("ShaderNodeTexNoise")
    ns.inputs["Scale"].default_value = 40.0
    mix = nt.nodes.new("ShaderNodeMix")
    mix.data_type = "RGBA"
    mix.blend_type = "MULTIPLY"
    mix.inputs["Factor"].default_value = 0.35
    bp = nt.nodes.new("ShaderNodeBump")
    bp.inputs["Strength"].default_value = 0.2
    nt.links.new(tc.outputs["Object"], br.inputs["Vector"])
    nt.links.new(tc.outputs["Object"], ns.inputs["Vector"])
    nt.links.new(br.outputs["Color"], mix.inputs["A"])
    nt.links.new(ns.outputs["Color"], mix.inputs["B"])
    nt.links.new(mix.outputs["Result"], p.inputs["Base Color"])
    nt.links.new(br.outputs["Fac"], bp.inputs["Height"])
    nt.links.new(bp.outputs["Normal"], p.inputs["Normal"])


def build_materials():
    return {
        "pine": mat("MAT_Pine", (0.6, 0.42, 0.24), 0.6,
                    extra=wood_grain((0.45, 0.28, 0.14), (0.72, 0.52, 0.31), 60)),
        "steel": mat("MAT_Spring_Steel", (0.62, 0.62, 0.6), 0.3, 1.0),
        "zinc": mat("MAT_Zinc_Pedal", (0.7, 0.66, 0.55), 0.35, 1.0),
        "stamp": mat("MAT_Red_Stamp", (0.55, 0.05, 0.04), 0.7),
        "floor": mat("MAT_Floor_Planks", (0.25, 0.15, 0.08), 0.45, extra=floor_planks),
        "wall": mat("MAT_Wall_Plaster", (0.55, 0.52, 0.44), 0.9),
        "skirting": mat("MAT_Skirting", (0.18, 0.16, 0.13), 0.5),
        "pingpong": mat("MAT_PingPong", (0.92, 0.9, 0.85), 0.35),
        "pingpong_o": mat("MAT_PingPong_Orange", (0.95, 0.38, 0.05), 0.35),
        "ball": mat("MAT_Rubber_Ball", (0.75, 0.04, 0.05), 0.4),
    }


def mesh_obj(name, verts, faces, material, coll):
    me = bpy.data.meshes.new(name)
    me.from_pydata(verts, [], faces)
    me.materials.append(material)
    ob = bpy.data.objects.new(name, me)
    coll.objects.link(ob)
    return ob


def box_obj(name, size, center, material, coll):
    v, f = box_data(*size)
    ob = mesh_obj(name, v, f, material, coll)
    ob.location = center
    return ob


def box_data(sx, sy, sz, cx=0.0, cy=0.0, cz=0.0):
    v = [(cx + x * sx / 2, cy + y * sy / 2, cz + z * sz / 2)
         for x in (-1, 1) for y in (-1, 1) for z in (-1, 1)]
    f = [(0, 1, 3, 2), (4, 6, 7, 5), (0, 4, 5, 1), (2, 3, 7, 6), (0, 2, 6, 4), (1, 5, 7, 3)]
    return v, f


def wire_path(points, r, segs=6):
    """Tube through a polyline of points (open), as verts and faces."""
    verts, faces = [], []
    pts = [Vector(p) for p in points]
    for i, p in enumerate(pts):
        d = (pts[min(i + 1, len(pts) - 1)] - pts[max(i - 1, 0)]).normalized()
        a = d.orthogonal().normalized()
        b = d.cross(a)
        for k in range(segs):
            t = 2 * math.pi * k / segs
            verts.append(tuple(p + r * (math.cos(t) * a + math.sin(t) * b)))
    for i in range(len(pts) - 1):
        for k in range(segs):
            a0, a1 = i * segs + k, i * segs + (k + 1) % segs
            faces.append((a0, a1, a1 + segs, a0 + segs))
    return verts, faces


def build_trap_meshes(M):
    """Shared mesh data, built once: base board, pedal, coils, stamp, bar."""
    lib = bpy.data.collections.new("_trap_library")
    v, f = box_data(BASE_L, BASE_W, BASE_T, cz=BASE_T / 2)
    base = mesh_obj("lib_base", v, f, M["pine"], lib)
    v, f = box_data(0.026, 0.018, 0.0012, cx=0.024, cz=BASE_T + 0.0016)
    pedal = mesh_obj("lib_pedal", v, f, M["zinc"], lib)
    v, f = box_data(0.03, 0.022, 0.0002, cx=-0.026, cz=BASE_T + 0.0001)
    stamp = mesh_obj("lib_stamp", v, f, M["stamp"], lib)
    cv, cf = [], []
    for side in (-1, 1):
        pts = []
        for i in range(41):
            t = i / 40 * 5 * 2 * math.pi
            y = side * (0.008 + 0.009 * i / 40)
            pts.append((0.0035 * math.cos(t), y, BASE_T + 0.0042 + 0.0035 * math.sin(t)))
        vv, ff = wire_path(pts, 0.0006, 5)
        o = len(cv)
        cv += vv
        cf += [tuple(i + o for i in q) for q in ff]
    coils = mesh_obj("lib_coils", cv, cf, M["steel"], lib)
    # bar: U wire lying flat over -x half, pivot at local origin
    hw = BAR_W / 2
    pts = [(0, -hw, 0), (-BAR_L * 0.98, -hw, 0), (-BAR_L, -hw * 0.9, 0), (-BAR_L, hw * 0.9, 0),
           (-BAR_L * 0.98, hw, 0), (0, hw, 0)]
    bv, bf = wire_path(pts, WIRE / 2, 6)
    bar = mesh_obj("lib_bar", bv, bf, M["steel"], lib)
    for o in (base, pedal, stamp, coils):
        o.data.transform(Matrix.Translation((0, 0, -BASE_T / 2)))
    bar.data.transform(Matrix.Translation((BAR_L / 2, 0, 0)))
    return {"base": base.data, "pedal": pedal.data, "stamp": stamp.data, "coils": coils.data, "bar": bar.data}, lib


def rb(ob, kind="ACTIVE", mass=0.01, shape="BOX", fr=0.6, bounce=0.2):
    bpy.context.view_layer.objects.active = ob
    ob.select_set(True)
    bpy.ops.rigidbody.object_add(type=kind)
    ob.select_set(False)
    r = ob.rigid_body
    r.mass = mass
    r.collision_shape = shape
    r.friction = fr
    r.restitution = bounce
    r.use_margin = True
    r.collision_margin = MARGIN
    r.linear_damping = 0.02
    r.angular_damping = 0.05
    r.use_deactivation = False
    return r


def constraint(name, a, b, kind, loc, rot, coll):
    e = bpy.data.objects.new(name, None)
    e.empty_display_size = 0.01
    e.location = loc
    e.rotation_euler = rot
    coll.objects.link(e)
    bpy.context.view_layer.objects.active = e
    e.select_set(True)
    bpy.ops.rigidbody.constraint_add(type=kind)
    e.select_set(False)
    c = e.rigid_body_constraint
    c.object1, c.object2 = a, b
    c.disable_collisions = True
    c.solver_iterations = 40
    c.use_override_solver_iterations = True
    return e


def key_enabled(empty, frame, value):
    c = empty.rigid_body_constraint
    c.enabled = value
    empty.keyframe_insert('rigid_body_constraint.enabled', frame=frame)


def build_traps(M, meshes):
    coll = bpy.data.collections.new("TRAPS")
    cons = bpy.data.collections.new("TRAP_Constraints")
    bpy.context.scene.collection.children.link(coll)
    bpy.context.scene.collection.children.link(cons)
    traps = []
    x0 = -(COLS - 1) * PITCH_X / 2
    y0 = -(ROWS - 1) * PITCH_Y / 2
    for j in range(ROWS):
        for i in range(COLS):
            if random.random() < 0.04:
                continue
            x = x0 + i * PITCH_X + random.uniform(-0.004, 0.004)
            y = y0 + j * PITCH_Y + random.uniform(-0.003, 0.003)
            yaw = random.uniform(-0.07, 0.07) + (math.pi if random.random() < 0.5 else 0.0)
            n = "TRAP_%02d_%02d" % (j, i)
            base = bpy.data.objects.new(n + "_Base", meshes["base"])
            base.location = (x, y, BASE_T / 2)
            base.rotation_euler = (0, 0, yaw)
            coll.objects.link(base)
            for part in ("pedal", "stamp", "coils"):
                c = bpy.data.objects.new(n + "_" + part.title(), meshes[part])
                c.parent = base
                coll.objects.link(c)
            bpy.context.view_layer.update()
            rot = Matrix.Rotation(yaw, 4, "Z")
            pivot = Vector((x, y, 0)) + rot @ Vector((0, 0, BASE_T + WIRE / 2 + 0.0002))
            bar = bpy.data.objects.new(n + "_Bar", meshes["bar"])
            bar.location = pivot + rot @ Vector((-BAR_L / 2, 0, 0))
            bar.rotation_euler = (0, 0, yaw)
            coll.objects.link(bar)
            rb(base, mass=MASS_BASE, fr=0.5, bounce=0.25)
            rb(bar, mass=MASS_BAR, fr=0.3, bounce=0.3)
            # hinge axis = local Z of the empty, pointed along the trap's +Y
            hinge_rot = (rot @ Matrix.Rotation(-math.pi / 2, 4, "X")).to_euler()
            h = constraint(n + "_Hinge", base, bar, "HINGE", pivot, hinge_rot, cons)
            # motor drives about local X of the empty, also pointed along the trap's +Y
            motor_rot = (rot @ Matrix.Rotation(math.pi / 2, 4, "Z")).to_euler()
            m = constraint(n + "_Motor", base, bar, "MOTOR", pivot, motor_rot, cons)
            mc = m.rigid_body_constraint
            mc.use_motor_ang = True
            mc.motor_ang_target_velocity = MOTOR_VEL * random.uniform(0.85, 1.15)
            mc.motor_ang_max_impulse = MOTOR_IMPULSE
            key_enabled(m, 1, False)
            l = constraint(n + "_Latch", base, bar, "FIXED", pivot, (0, 0, yaw), cons)
            key_enabled(l, 1, True)
            traps.append({"name": n, "base": base, "bar": bar, "motor": m, "latch": l, "fired": None,
                          "hinge": h, "start": Vector((x, y, BASE_T / 2))})
    return traps


def build_hinge_limits(traps):
    for t in traps:
        c = t["hinge"].rigid_body_constraint
        c.use_limit_ang_z = True
        c.limit_ang_z_lower = -3.1
        c.limit_ang_z_upper = 0.05


def build_balls(M, traps):
    coll = bpy.data.collections.new("BALLS")
    bpy.context.scene.collection.children.link(coll)
    balls = []
    bait = random.sample(traps, k=max(1, len(traps) // 8))
    for k, t in enumerate(bait):
        bpy.context.view_layer.update()
        p = t["base"].matrix_world @ Vector((0.024, 0, TOP + 0.0023 + PP_R))
        bpy.ops.mesh.primitive_uv_sphere_add(radius=PP_R, segments=24, ring_count=12, location=p)
        ob = bpy.context.object
        ob.name = "PINGPONG_%02d" % k
        for c in ob.users_collection:
            c.objects.unlink(ob)
        coll.objects.link(ob)
        bpy.ops.object.shade_smooth()
        ob.data.materials.append(M["pingpong_o"] if k % 3 == 0 else M["pingpong"])
        rb(ob, mass=PP_MASS, shape="SPHERE", fr=0.4, bounce=0.75)
        ob.rigid_body.linear_damping = 0.1
        balls.append((ob, PP_R))
    # dropped rubber ball, falling in just right of centre, a little toward camera
    bpy.ops.mesh.primitive_uv_sphere_add(radius=BALL_R, segments=32, ring_count=16, location=(0.08, -0.12, 0.9))
    ob = bpy.context.object
    ob.name = "BALL_Rubber"
    for c in ob.users_collection:
        c.objects.unlink(ob)
    coll.objects.link(ob)
    bpy.ops.object.shade_smooth()
    ob.data.materials.append(M["ball"])
    rb(ob, mass=BALL_MASS, shape="SPHERE", fr=0.8, bounce=0.7)
    balls.append((ob, BALL_R))
    return balls


def build_room(M):
    coll = bpy.data.collections.new("ROOM")
    bpy.context.scene.collection.children.link(coll)
    hx = COLS * PITCH_X / 2 + 0.6
    hy = ROWS * PITCH_Y / 2 + 0.4
    floor = box_obj("ROOM_Floor", (2 * hx + 2, 2 * hy + 2, 0.02), (0, 0, -0.01), M["floor"], coll)
    rb(floor, kind="PASSIVE", shape="BOX", fr=0.6, bounce=0.3)
    wall = box_obj("ROOM_BackWall", (2 * hx + 2, 0.1, 2.6), (0, hy + 0.05, 1.3), M["wall"], coll)
    rb(wall, kind="PASSIVE", shape="BOX", fr=0.5, bounce=0.3)
    wl = box_obj("ROOM_LeftWall", (0.1, 2 * hy + 2, 2.6), (-hx - 0.05, 0, 1.3), M["wall"], coll)
    rb(wl, kind="PASSIVE", shape="BOX", fr=0.5, bounce=0.3)
    box_obj("ROOM_Skirting", (2 * hx + 2, 0.02, 0.12), (0, hy - 0.01, 0.06), M["skirting"], coll)
    return hx, hy


def build_lights_camera(hx, hy):
    sc = bpy.context.scene
    world = bpy.data.worlds.new("World")
    sc.world = world
    world.use_nodes = True
    world.node_tree.nodes["Background"].inputs["Color"].default_value = (0.03, 0.035, 0.045, 1)
    world.node_tree.nodes["Background"].inputs["Strength"].default_value = 1.0
    ld = bpy.data.lights.new("KEY_Window", "AREA")
    ld.shape = "RECTANGLE"
    ld.size, ld.size_y = 1.6, 0.9
    ld.energy = 450
    ld.color = (1.0, 0.9, 0.78)
    key = bpy.data.objects.new("KEY_Window", ld)
    key.location = (-hx + 0.2, 0.6, 1.9)
    key.rotation_euler = Euler((math.radians(50), 0, math.radians(-115)))
    sc.collection.objects.link(key)
    fd = bpy.data.lights.new("FILL", "AREA")
    fd.size = 3.0
    fd.energy = 120
    fd.color = (0.75, 0.82, 1.0)
    fill = bpy.data.objects.new("FILL", fd)
    fill.location = (0.8, -2.4, 2.2)
    fill.rotation_euler = Euler((math.radians(45), 0, math.radians(20)))
    sc.collection.objects.link(fill)
    cd = bpy.data.cameras.new("CAM_Main")
    cd.lens = 32
    cd.dof.use_dof = True
    cd.dof.aperture_fstop = 5.6
    cam = bpy.data.objects.new("CAM_Main", cd)
    cam.location = (0.15, -hy - 0.55, 0.42)
    sc.collection.objects.link(cam)
    tgt = bpy.data.objects.new("CAM_Target", None)
    tgt.location = (0.0, 0.05, 0.02)
    sc.collection.objects.link(tgt)
    tc = cam.constraints.new("TRACK_TO")
    tc.target = tgt
    tc.track_axis = "TRACK_NEGATIVE_Z"
    tc.up_axis = "UP_Y"
    cd.dof.focus_object = tgt
    sc.camera = cam
    # slow push-in and a small rise across the shot
    cam.keyframe_insert("location", frame=1)
    cam.location = (0.05, -hy - 0.15, 0.55)
    cam.keyframe_insert("location", frame=FRAMES)


def world_points(traps, balls):
    """Sample points per body (world space) plus owner index, for contact tests."""
    pts, owner = [], []
    hw = BASE_W / 2
    hl = BASE_L / 2
    base_local = [Vector((x, y, TOP)) for x in (-hl, 0, hl) for y in (-hw, hw)]
    bar_local = [Vector((-BAR_L / 2, y, 0)) for y in (-BAR_W / 2, 0, BAR_W / 2)] + [Vector((0, 0, 0))]
    for i, t in enumerate(traps):
        mb = t["base"].matrix_world
        for p in base_local:
            pts.append(mb @ p)
            owner.append(i)
        mr = t["bar"].matrix_world
        for p in bar_local:
            pts.append(mr @ p)
            owner.append(i)
    return np.array(pts), np.array(owner)


def simulate(traps, balls):
    sc = bpy.context.scene
    rbw = sc.rigidbody_world
    rbw.time_scale = TIME_SCALE
    rbw.substeps_per_frame = SUBSTEPS
    rbw.solver_iterations = ITERATIONS
    rbw.point_cache.frame_start = 1
    rbw.point_cache.frame_end = FRAMES
    bodies = [o for t in traps for o in (t["base"], t["bar"])] + [b for b, _ in balls]
    rec = {o.name: np.zeros((FRAMES, 16)) for o in bodies}
    trap_lookup = {}
    inv = [None] * len(traps)
    prev_pts = None
    prev_ball = None
    sc.frame_set(1)
    for f in range(1, FRAMES + 1):
        sc.frame_set(f)
        for o in bodies:
            rec[o.name][f - 1] = np.array(o.matrix_world).ravel()
        pts, owner = world_points(traps, balls)
        ball_pos = np.array([b.matrix_world.translation for b, _ in balls])
        ball_r = np.array([r for _, r in balls])
        if prev_pts is None:
            prev_pts, prev_ball = pts, ball_pos
            continue
        moving = np.linalg.norm(pts - prev_pts, axis=1) > MOVE_EPS
        ball_moving = np.linalg.norm(ball_pos - prev_ball, axis=1) > MOVE_EPS
        prev_pts, prev_ball = pts, ball_pos
        newly = []
        for i, t in enumerate(traps):
            if t["fired"]:
                continue
            mb = t["base"].matrix_world
            up = mb.to_3x3() @ Vector((0, 0, 1))
            shoved = (mb.translation - t["start"]).length > SHOVE
            hit = up.z < TILT_COS or shoved
            if not hit:
                im = np.array(mb.inverted())
                sel = moving & (owner != i)
                if sel.any():
                    q = pts[sel] @ im[:3, :3].T + im[:3, 3]
                    inside = ((np.abs(q[:, 0]) < BASE_L / 2) & (np.abs(q[:, 1]) < BASE_W / 2)
                              & (q[:, 2] > TOP - 0.002) & (q[:, 2] < TOP + 0.02))
                    hit = bool(inside.any())
                if not hit and ball_moving.any():
                    q = ball_pos[ball_moving] @ im[:3, :3].T + im[:3, 3]
                    r = ball_r[ball_moving]
                    dx = np.maximum(np.abs(q[:, 0]) - BASE_L / 2, 0)
                    dy = np.maximum(np.abs(q[:, 1]) - BASE_W / 2, 0)
                    dz = np.maximum(q[:, 2] - TOP, 0) + np.maximum(TOP - 0.004 - q[:, 2], 0)
                    hit = bool((((dx ** 2 + dy ** 2 + dz ** 2) < (r + 0.002) ** 2)
                                & (q[:, 2] > TOP - 0.004)).any())
            if hit:
                if os.environ.get("TRAP_DEBUG"):
                    print("DBG", t["name"], "upz %.4f shove %.4f" % (up.z, (mb.translation - t["start"]).length),
                          "moving pts", int(moving.sum()), "balls moving", ball_moving.tolist(), flush=True)
                newly.append(t)
        for t in newly:
            t["fired"] = f + 1
            key_enabled(t["latch"], f, True)
            key_enabled(t["latch"], f + 1, False)
            key_enabled(t["motor"], f, False)
            key_enabled(t["motor"], f + 1, True)
        fired = sum(1 for t in traps if t["fired"])
        if f % 10 == 0 or newly:
            print("SIM frame %d fired %d/%d (+%d)" % (f, fired, len(traps), len(newly)), flush=True)
    return rec, bodies


def bake_keys(rec, bodies):
    sc = bpy.context.scene
    for c in list(bpy.data.collections):
        if c.name == "TRAP_Constraints":
            for o in list(c.objects):
                bpy.data.objects.remove(o)
            bpy.data.collections.remove(c)
    bpy.ops.rigidbody.world_remove()
    frames = np.arange(1, FRAMES + 1, dtype=float)
    for o in bodies:
        o.rotation_mode = "QUATERNION"
        m = rec[o.name].reshape(FRAMES, 4, 4)
        loc = m[:, :3, 3]
        quats = []
        last = None
        for k in range(FRAMES):
            q = Matrix(m[k].tolist()).to_quaternion()
            if last is not None and last.dot(q) < 0:
                q.negate()
            quats.append(q)
            last = q
        quats = np.array([[q.w, q.x, q.y, q.z] for q in quats])
        o.animation_data_create()
        act = bpy.data.actions.new(o.name + "_Sim")
        slot = act.slots.new(id_type="OBJECT", name=o.name)
        o.animation_data.action = act
        o.animation_data.action_slot = slot
        cb = anim_utils.action_ensure_channelbag_for_slot(act, slot)
        for path, data in (("location", loc), ("rotation_quaternion", quats)):
            for idx in range(data.shape[1]):
                fc = cb.fcurves.new(path, index=idx)
                fc.keyframe_points.add(FRAMES)
                co = np.empty(FRAMES * 2)
                co[0::2] = frames
                co[1::2] = data[:, idx]
                fc.keyframe_points.foreach_set("co", co)
                fc.keyframe_points.foreach_set("interpolation", [1] * FRAMES)   # LINEAR
                fc.update()
    sc.frame_set(1)


def render_settings():
    sc = bpy.context.scene
    sc.render.engine = "CYCLES"
    sc.cycles.device = "CPU"
    sc.cycles.samples = 24
    sc.cycles.use_adaptive_sampling = True
    sc.cycles.adaptive_threshold = 0.05
    sc.cycles.use_denoising = True
    sc.cycles.denoiser = "OPENIMAGEDENOISE"
    sc.cycles.max_bounces = 6
    sc.render.resolution_x, sc.render.resolution_y = 960, 540
    sc.render.resolution_percentage = 100
    sc.view_settings.view_transform = "AgX"
    sc.view_settings.look = "AgX - Base Contrast"
    sc.render.use_persistent_data = True


def main():
    sc = reset()
    M = build_materials()
    meshes, lib = build_trap_meshes(M)
    for o in list(lib.objects):
        bpy.data.objects.remove(o)
    bpy.data.collections.remove(lib)
    bpy.ops.rigidbody.world_add()
    hx, hy = build_room(M)
    traps = build_traps(M, meshes)
    build_hinge_limits(traps)
    balls = build_balls(M, traps)
    build_lights_camera(hx, hy)
    render_settings()
    print("BUILT %d traps, %d balls" % (len(traps), len(balls)), flush=True)
    rec, bodies = simulate(traps, balls)
    fired = [t["fired"] for t in traps if t["fired"]]
    print("FIRED %d/%d, first %s last %s" % (len(fired), len(traps), min(fired, default=None),
                                              max(fired, default=None)), flush=True)
    bake_keys(rec, bodies)
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from grade import grade
    grade()
    os.makedirs(os.path.dirname(os.path.abspath(OUT)), exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=os.path.abspath(OUT), compress=True)
    print("SAVED", os.path.abspath(OUT), flush=True)


main()
