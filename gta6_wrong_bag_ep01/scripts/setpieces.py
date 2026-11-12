"""LOCATION_01 (petrol station), CAR_01 (+ interior), BAG_01 (+ PS5_01, DUALSENSE_01, GTA_CASE_01, tag), HELI_01, lights."""
import math
import random

import bmesh
import bpy
from mathutils import Matrix, Vector

import config as C
import mats as M


def coll(name, parent=None):
    c = bpy.data.collections.get(name) or bpy.data.collections.new(name)
    par = parent or bpy.context.scene.collection
    if c.name not in [x.name for x in par.children]:
        par.children.link(c)
    return c


def put(o, c):
    for u in o.users_collection:
        u.objects.unlink(o)
    c.objects.link(o)
    return o


def empty(name, c, size=0.1, shape="PLAIN_AXES", parent=None, loc=(0, 0, 0)):
    e = bpy.data.objects.new(name, None)
    e.empty_display_type, e.empty_display_size = shape, size
    c.objects.link(e)
    e.parent = parent
    e.location = loc
    return e


def box(name, c, x0, x1, y0, y1, z0, z1, mat, bevel=0.0, parent=None):
    bpy.ops.mesh.primitive_cube_add(size=1, location=((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2))
    o = bpy.context.active_object
    o.name = name
    o.scale = (x1 - x0, y1 - y0, z1 - z0)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    if bevel:
        m = o.modifiers.new("bevel", "BEVEL")
        m.width, m.segments = bevel, 2
    o.data.materials.append(mat)
    put(o, c)
    if parent:
        o.parent = parent
    return o


def cyl(name, c, loc, r, depth, mat, rot=(0, 0, 0), verts=24, parent=None):
    bpy.ops.mesh.primitive_cylinder_add(vertices=verts, radius=r, depth=depth, location=loc, rotation=rot)
    o = bpy.context.active_object
    o.name = name
    bpy.ops.object.shade_smooth()
    o.data.materials.append(mat)
    put(o, c)
    if parent:
        o.parent = parent
    return o


def quad(name, c, pts, mat, parent=None, uv=True):
    me = bpy.data.meshes.new(name)
    me.from_pydata([Vector(p) for p in pts], [], [(0, 1, 2, 3)])
    if uv:
        me.uv_layers.new()
        for lp, co in zip(me.uv_layers[0].data, ((0, 0), (1, 0), (1, 1), (0, 1))):
            lp.uv = co
    o = bpy.data.objects.new(name, me)
    me.materials.append(mat)
    c.objects.link(o)
    o.parent = parent
    return o


def glass(name):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (0.05, 0.07, 0.09, 1)
    b.inputs["Roughness"].default_value = 0.03
    b.inputs["Alpha"].default_value = 0.06
    b.inputs["Specular IOR Level"].default_value = 0.8
    if hasattr(m, "surface_render_method"):
        m.surface_render_method = "BLENDED"            # sorted transparency: no dither grain through the windshield
    return m


# ------------------------------------------------------------------ LOCATION_01
def station():
    c = coll("LOCATION_01_PETROL_STATION")
    wet = M.clay("asphalt_wet", "#15141c", 0.10, 0.0, 0.7)
    box("GROUND_asphalt", c, -80, 60, -60, 200, -0.05, 0.0, wet)
    rnd = random.Random(3)
    pud = M.clay("puddle", "#0b0b10", 0.02, 0.0, 1.0)
    for i in range(14):
        x, y = rnd.uniform(-9, 7), rnd.uniform(-14, 12)
        if abs(x) < 1.2 and -3 < y < 3:
            continue
        cyl(f"GROUND_puddle_{i:02d}", c, (x, y, 0.001), rnd.uniform(0.4, 1.4), 0.002, pud, verts=20)
    K = C.CANOPY
    box("CANOPY_slab", c, K["x0"], K["x1"], K["y0"], K["y1"], K["z"], K["z"] + K["t"], M.clay("canopy_white", "#d8d4dc", 0.6))
    neon = M.emit("neon_canopy_pink", C.PAL["pink"], 14)
    for n, (a, b, d, e) in {"S": (K["x0"], K["x1"], K["y0"] - 0.03, K["y0"]), "N": (K["x0"], K["x1"], K["y1"], K["y1"] + 0.03),
                            "W": (K["x0"] - 0.03, K["x0"], K["y0"], K["y1"]), "E": (K["x1"], K["x1"] + 0.03, K["y0"], K["y1"])}.items():
        box(f"CANOPY_neon_{n}", c, a, b, d, e, K["z"] + 0.05, K["z"] + 0.14, neon)
    for x, y in ((K["x0"] + 0.5, K["y0"] + 0.6), (K["x0"] + 0.5, K["y1"] - 0.6), (-3.0, K["y0"] + 0.6), (-3.0, K["y1"] - 0.6)):
        box(f"CANOPY_pillar_{x:+.1f}_{y:+.1f}", c, x - 0.18, x + 0.18, y - 0.18, y + 0.18, 0, K["z"], M.clay("pillar", "#bfbac6", 0.5))
    for i, (x, y) in enumerate([(-2.0, -2.5), (-2.0, 2.5), (1.5, -2.5), (1.5, 2.5)]):        # canopy practicals (pink-white)
        ld = bpy.data.lights.new(f"CANOPY_light_{i}", "AREA")
        ld.shape, ld.size, ld.size_y, ld.energy, ld.color = "RECTANGLE", 1.2, 0.3, 1400, (1.0, 0.62, 0.86)
        lo = bpy.data.objects.new(f"CANOPY_light_{i}", ld)
        lo.location = (x, y, K["z"] - 0.02)
        c.objects.link(lo)
        box(f"CANOPY_panel_{i}", c, x - 0.6, x + 0.6, y - 0.15, y + 0.15, K["z"] - 0.015, K["z"], M.emit("canopy_panel", "#ffd8f0", 6))
    px = C.PUMPS["x"]
    box("PUMP_island", c, px - 0.45, px + 0.45, -4.0, 4.2, 0, 0.18, M.clay("island", "#8a8692", 0.8), 0.02)
    for i, y in enumerate(C.PUMPS["ys"]):
        box(f"PUMP_{i}", c, px - 0.3, px + 0.3, y - 0.35, y + 0.35, 0.18, 1.85, M.clay("pump", "#2b2a35", 0.5), 0.03)
        box(f"PUMP_{i}_screen_E", c, px + 0.30, px + 0.31, y - 0.2, y + 0.2, 1.2, 1.55, M.emit("pump_screen", C.PAL["blue"], 4))
        box(f"PUMP_{i}_cap", c, px - 0.32, px + 0.32, y - 0.37, y + 0.37, 1.85, 1.95, M.emit("pump_cap", C.PAL["pink"], 6))
    # kiosk / store
    box("STORE_body", c, 7.0, 15.0, 6.0, 14.0, 0, 3.8, M.clay("store", "#2a2236", 0.8))
    box("STORE_window", c, 6.98, 7.0, 7.0, 13.0, 0.5, 2.6, M.emit("store_window", "#ffe6c8", 3))
    sign = bpy.data.materials.new("station_sign")
    sign.use_nodes = True
    n, l = sign.node_tree.nodes, sign.node_tree.links
    t = n.new("ShaderNodeTexImage")
    t.image = bpy.data.images.load(f"{C.P['tex']}/station_sign.png")
    b = n["Principled BSDF"]
    l.new(t.outputs["Color"], b.inputs["Emission Color"])
    b.inputs["Emission Strength"].default_value = 5
    b.inputs["Base Color"].default_value = (0, 0, 0, 1)
    quad("STORE_sign", c, [(6.95, 13.5, 2.9), (6.95, 6.5, 2.9), (6.95, 6.5, 3.6), (6.95, 13.5, 3.6)], sign)
    for i, (x, y) in enumerate([(-9, -12), (-9, 0), (-9, 12), (6, -12), (5.5, 20), (-12, 26), (10, 24)]):
        palm(f"PALM_{i}", c, (x, y, 0), rnd)
    sky = M.clay("skyline", C.PAL["plum"], 0.9)
    for j in range(30):
        x = -120 + j * 8 + rnd.uniform(-2, 2)
        h = rnd.uniform(20, 70)
        box(f"SKYLINE_{j:02d}", c, x, x + rnd.uniform(4, 7), 160, 168, 0, h, sky)
        box(f"SKYLINE_{j:02d}_win", c, x + 0.6, x + 3.0, 159.9, 160.0, h * 0.25, h * 0.9, M.emit("sky_win", C.PAL["magenta"], 2.5))
    # distant police car with flashing bar (keyed in anim)
    pc = coll("POLICE_DISTANT")
    px, py = C.POLICE
    box("POLICE_body", pc, px - 2.3, px + 2.3, py - 0.9, py + 0.9, 0.3, 1.1, M.clay("police_body", "#e8e8ee", 0.4), 0.06)
    bars = {}
    for k, col in ((-1, "#2060ff"), (1, "#ff2040")):
        bars[col] = box(f"POLICE_bar_{'blue' if k < 0 else 'red'}", pc, px + k * 0.35 - 0.3, px + k * 0.35 + 0.3, py - 0.15, py + 0.15,
                        1.42, 1.55, M.emit(f"police_{col}", col, 30))
        pl = bpy.data.lights.new(f"POLICE_flash_{'blue' if k < 0 else 'red'}", "POINT")
        pl.color = C.rgb(col)[:3]
        pl.energy = 0
        plo = bpy.data.objects.new(pl.name, pl)
        plo.location = (px + k * 0.35, py, 1.8)
        pc.objects.link(plo)
    # a blue flash spill reaching the station (motivated by the police bar, off frame)
    sp = bpy.data.lights.new("POLICE_spill_blue", "AREA")
    sp.size, sp.energy, sp.color = 6.0, 0, (0.2, 0.35, 1.0)
    spo = bpy.data.objects.new("POLICE_spill_blue", sp)
    spo.location = (-14.0, 10.0, 3.0)
    spo.rotation_euler = (math.radians(70), 0, math.radians(-125))
    pc.objects.link(spo)
    return c


def palm(name, c, base, rnd):
    h = rnd.uniform(7, 10)
    cu = bpy.data.curves.new(name + "_trunk", "CURVE")
    cu.dimensions, cu.bevel_depth, cu.bevel_resolution = "3D", 0.16, 2
    sp = cu.splines.new("BEZIER")
    sp.bezier_points.add(1)
    p0, p1 = Vector(base), Vector(base) + Vector((rnd.uniform(-0.8, 0.8), 0, h))
    for bp, co in zip(sp.bezier_points, (p0, p1)):
        bp.co, bp.handle_left_type, bp.handle_right_type = co, "AUTO", "AUTO"
    o = bpy.data.objects.new(name + "_trunk", cu)
    o.data.materials.append(M.clay("palm_trunk", "#241a22", 0.9))
    c.objects.link(o)
    fm = M.clay("palm_frond", "#0e1a1c", 0.9)
    for k in range(9):
        a = k * 2 * math.pi / 9 + rnd.uniform(-0.2, 0.2)
        bpy.ops.mesh.primitive_cube_add(size=1)
        f = put(bpy.context.active_object, c)
        f.name = f"{name}_frond{k}"
        f.scale = (2.6, 0.38, 0.04)
        bpy.ops.object.transform_apply(scale=True)
        f.location = p1 + Vector((math.cos(a) * 1.15, math.sin(a) * 1.15, -0.35))
        f.rotation_euler = (0, 0.45, a)
        f.data.materials.append(fm)


# ------------------------------------------------------------------ CAR_01
def car():
    K = C.CAR
    c = coll("CAR_01")
    root = empty("CAR_01", c, 1.0, "ARROWS")
    body = empty("CAR_01_BODY", c, 0.6, "CUBE", parent=root)        # brake dive / settle lives here
    paint = M.clay("car_paint_dark", "#1b1c26", 0.28, 0.3, 0.8)
    L, W = K["len"], K["w"]
    hw = W / 2
    # hollow tub: engine bay, trunk, door sills and underbody around an open cabin (y -1.62..0.60)
    box("CAR_body_front", c, -hw, hw, 0.60, L / 2, 0.26, 0.80, paint, 0.06, body)
    box("CAR_body_rear", c, -hw, hw, -L / 2, -1.62, 0.26, 0.82, paint, 0.06, body)
    box("CAR_body_under", c, -hw, hw, -1.62, 0.60, 0.20, 0.26, paint, 0.0, body)
    for k in (-1, 1):
        box(f"CAR_door_{'L' if k < 0 else 'R'}", c, (hw - 0.07) if k > 0 else -hw, hw if k > 0 else (-hw + 0.07), -1.62, 0.60, 0.26, 0.80,
            paint, 0.03, body)
    box("CAR_rear_bench", c, -0.70, 0.70, -1.55, -1.05, 0.20, 0.42, M.clay("seat", "#3a2a24", 0.7), 0.04, body)
    box("CAR_rear_bench_back", c, -0.70, 0.70, -1.62, -1.50, 0.42, 0.86, M.clay("seat", "#3a2a24", 0.7), 0.04, body)
    box("CAR_hood_bulge", c, -0.35, 0.35, 0.75, L / 2 - 0.2, 0.80, 0.86, paint, 0.03, body)
    box("CAR_roof", c, -0.66, 0.66, -0.95, 0.02, K["roof_z"] - 0.04, K["roof_z"] + 0.02, paint, 0.03, body)
    chrome = M.clay("chrome", "#b8bcc8", 0.15, 1.0)
    box("CAR_bumper_F", c, -hw + 0.05, hw - 0.05, L / 2, L / 2 + 0.06, 0.30, 0.40, chrome, 0.02, body)
    box("CAR_bumper_R", c, -hw + 0.05, hw - 0.05, -L / 2 - 0.06, -L / 2, 0.30, 0.40, chrome, 0.02, body)
    for k in (-1, 1):
        s = "L" if k < 0 else "R"
        # A, B and C pillars (side windows are rolled down)
        for nm, p0, p1 in (("A", (k * 0.74, 0.58, 0.82), (k * 0.64, 0.02, K["roof_z"])), ("B", (k * 0.76, -0.95, 0.80), (k * 0.66, -0.95, K["roof_z"])),
                           ("C", (k * 0.66, -0.95, K["roof_z"]), (k * 0.78, -1.75, 0.84))):
            a, b = Vector(p0), Vector(p1)
            d = b - a
            o = cyl(f"CAR_pillar_{nm}{s}", c, (a + b) / 2, 0.035, d.length, paint, parent=body, verts=8)
            o.rotation_mode = "QUATERNION"
            o.rotation_quaternion = d.to_track_quat("Z", "Y")
        dx0, dx1 = (hw - 0.06, hw) if k > 0 else (-hw, -hw + 0.06)
        box(f"CAR_door_inner_{s}", c, dx0, dx1, -1.0, 0.55, 0.26, 0.80, M.clay("door_card", "#2a2026", 0.8), 0.0, body)
        box(f"CAR_seat_cushion_{s}", c, k * 0.37 - 0.25, k * 0.37 + 0.25, -0.52, -0.02, 0.20, K["seat_z"], M.clay("seat", "#3a2a24", 0.7), 0.04, body)
        bk = box(f"CAR_seat_back_{s}", c, k * 0.37 - 0.25, k * 0.37 + 0.25, -0.62, -0.52, 0.28, 0.98, M.clay("seat", "#3a2a24"), 0.04, body)
        bk.rotation_euler = (-0.22, 0, 0)
    box("CAR_floor", c, -hw + 0.06, hw - 0.06, -1.6, 0.6, K["floor_z"] - 0.02, K["floor_z"], M.clay("carpet", "#1a1418", 0.95), 0, body)
    box("CAR_console", c, -0.10, 0.10, -0.55, 0.35, K["floor_z"], 0.40, M.clay("console", "#221a1e", 0.6), 0.02, body)
    box("CAR_dash", c, -hw + 0.06, hw - 0.06, 0.38, 0.66, 0.55, K["dash_z"], M.clay("dash", "#1e1a20", 0.6), 0.03, body)
    box("CAR_dash_gauges", c, K["driver_x"] - 0.18, K["driver_x"] + 0.18, 0.375, 0.38, 0.66, 0.76, M.emit("gauges", "#ffb050", 2.5), 0, body)
    wc = Vector(K["wheel_c"])
    sw = bpy.ops.mesh.primitive_torus_add(major_radius=K["wheel_rad"], minor_radius=0.016, major_segments=32, minor_segments=8, location=wc,
                                          rotation=(math.radians(62), 0, 0))
    sw = put(bpy.context.active_object, c)
    sw.name = "CAR_steering_wheel"
    sw.data.materials.append(M.clay("wheel_black", "#0e0c0e", 0.5))
    sw.parent = body
    col = cyl("CAR_steering_column", c, (wc.x, wc.y + 0.14, wc.z - 0.05), 0.03, 0.3, M.clay("wheel_black", "#0e0c0e"), rot=(math.radians(62), 0, 0), parent=body)
    ws = quad("CAR_windshield", c, [(-0.74, 0.60, 0.82), (0.74, 0.60, 0.82), (0.64, 0.02, K["roof_z"] - 0.02), (-0.64, 0.02, K["roof_z"] - 0.02)],
              glass("car_glass"), parent=body)
    ws.visible_shadow = False
    rg = quad("CAR_rear_glass", c, [(0.64, -0.95, K["roof_z"] - 0.02), (-0.64, -0.95, K["roof_z"] - 0.02), (-0.76, -1.75, 0.84), (0.76, -1.75, 0.84)],
              glass("car_glass"), parent=body)
    rg.visible_shadow = False
    for k in (-1, 1):
        box(f"CAR_headlight_{k}", c, k * 0.62 - 0.14, k * 0.62 + 0.14, L / 2, L / 2 + 0.02, 0.56, 0.68, M.emit("headlight", "#fff1d6", 8), 0, body)
        box(f"CAR_taillight_{k}", c, k * 0.6 - 0.25, k * 0.6 + 0.25, -L / 2 - 0.02, -L / 2, 0.58, 0.68, M.emit("taillight", "#ff1830", 6), 0, body)
    # dashboard bounce (warm, from the gauges/instrument glow up onto the faces)
    db = bpy.data.lights.new("CAR_dash_bounce", "AREA")
    db.shape, db.size, db.size_y, db.energy, db.color = "RECTANGLE", 1.2, 0.2, 32, (1.0, 0.62, 0.32)
    # pink canopy spill reaching in through the open side windows
    for k in (-1, 1):
        sp = bpy.data.lights.new(f"CAR_canopy_spill_{'L' if k < 0 else 'R'}", "AREA")
        sp.shape, sp.size, sp.size_y, sp.energy, sp.color = "RECTANGLE", 1.6, 0.6, 26, (1.0, 0.45, 0.78)
        so = bpy.data.objects.new(sp.name, sp)
        so.location = (k * 1.5, -0.3, 1.5)
        so.rotation_euler = (0, k * math.radians(-55), 0)
        c.objects.link(so)
        so.parent = body
    dbo = bpy.data.objects.new("CAR_dash_bounce", db)
    dbo.location = (0, 0.36, 0.86)
    dbo.rotation_euler = (math.radians(-60), 0, 0)
    c.objects.link(dbo)
    dbo.parent = body
    wheels = []
    tire, rim = M.clay("tire", "#0b0b0d", 0.8), chrome
    for i, (x, y) in enumerate([(-K["track"] / 2, K["wheelbase"] / 2), (K["track"] / 2, K["wheelbase"] / 2),
                                (-K["track"] / 2, -K["wheelbase"] / 2), (K["track"] / 2, -K["wheelbase"] / 2)]):
        hub = empty(f"CAR_wheel_{i}", c, K["wheel_r"], "CIRCLE", parent=root, loc=(x, y, K["wheel_r"]))
        hub.rotation_mode = "XYZ"
        t = cyl(f"CAR_tire_{i}", c, (0, 0, 0), K["wheel_r"], 0.26, tire, rot=(0, math.pi / 2, 0), parent=hub)
        for j in range(3):
            sp = box(f"CAR_spoke_{i}_{j}", c, -0.135, 0.135, -0.02, 0.02, -0.24, 0.24, rim, 0, hub)
            sp.rotation_euler = (j * math.pi / 3, 0, 0)
        wheels.append(hub)
    return root, body, wheels


# ------------------------------------------------------------------ BAG_01 + contents + tag
def bag_mesh(name, c):
    B = C.BAG
    me = bpy.data.meshes.new(name)
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    bmesh.ops.subdivide_edges(bm, edges=bm.edges[:], cuts=5, use_grid_fill=True)
    for v in bm.verts:
        v.co = Vector((v.co.x * B["L"], v.co.y * B["W"], (v.co.z + 0.5) * (B["H"] - 0.02)))
    top = [f for f in bm.faces if f.calc_center_median().z > B["H"] - 0.025]
    bmesh.ops.delete(bm, geom=top, context="FACES")                # open top: the two flaps close it
    bm.to_mesh(me)
    bm.free()
    o = bpy.data.objects.new(name, me)
    c.objects.link(o)
    o.modifiers.new("solid", "SOLIDIFY").thickness = 0.008
    sub = o.modifiers.new("round", "SUBSURF")
    sub.levels = sub.render_levels = 1
    o.shape_key_add(name="Basis")
    sag, squash = o.shape_key_add(name="sag"), o.shape_key_add(name="squash")
    hx, hy = B["L"] / 2, B["W"] / 2
    for i, v in enumerate(me.vertices):
        x, y, z = v.co
        bel = (1 - (x / hx) ** 2) * (1 - (y / hy) ** 2)
        low = max(0.0, 1 - z / (B["H"] * 0.6))
        sag.data[i].co = Vector((x * (1 - 0.01 * low), y * (1 - 0.015 * low), z - 0.028 * bel * low))    # hanging weight
        squash.data[i].co = Vector((x * (1 + 0.02 * low), y * (1 + 0.07 * low), z * (1 - 0.06 * low) + 0.0))  # resting on thighs
    o.data.materials.append(M.clay("bag_black", "#0c0c10", 0.55))
    for p in me.polygons:
        p.use_smooth = True
    return o


def bag(parent):
    B, Z = C.BAG, C.ZIP
    c = coll("BAG_01")
    root = empty("BAG_01", c, 0.35, "CUBE", parent=parent)
    shell = bag_mesh("BAG_01_shell", c)
    shell.parent = root
    flap = M.clay("bag_black", "#0c0c10")
    flaps = {}
    for k in (-1, 1):
        hinge = empty(f"BAG_flap_hinge_{'back' if k < 0 else 'front'}", c, 0.05, parent=root, loc=(0, k * B["W"] / 2, B["H"] - 0.012))
        y0, y1 = (-B["W"] / 2 + 0.004, 0.0) if k > 0 else (0.0, B["W"] / 2 - 0.004)    # each flap reaches the zip line (hinge-local)
        box(f"BAG_flap_{'back' if k < 0 else 'front'}", c, -0.265, 0.265, y0, y1, -0.006, 0.006, flap, 0.004, hinge)    # flaps span the zip only
        flaps[k] = hinge
    for e, (xa, xb) in (("L", (-B["L"] / 2 + 0.004, -0.265)), ("R", (0.265, B["L"] / 2 - 0.004))):          # fixed end caps beyond the zip
        box(f"BAG_endcap_{e}", c, xa, xb, -B["W"] / 2 + 0.004, B["W"] / 2 - 0.004, B["H"] - 0.018, B["H"] - 0.006, flap, 0.004, root)
    zipm = M.clay("zip_teeth", "#2a2a30", 0.4, 0.7)
    box("BAG_zip_track", c, B["zip_x0"], B["zip_x1"], -0.006, 0.006, B["H"] - 0.006, B["H"] + 0.002, zipm, 0, root)
    gap = box("BAG_zip_open_gap", c, 0, 1, -0.012, 0.012, B["H"] - 0.012, B["H"] + 0.003, M.clay("bag_inside", "#020203", 0.9), 0, root)
    slider = empty("BAG_zip_slider", c, 0.02, "CUBE", parent=root, loc=(Z["start"], 0, B["H"] + 0.004))
    box("BAG_zip_slider_body", c, -0.012, 0.012, -0.011, 0.011, -0.004, 0.006, chrome_mat(), 0.002, slider)
    ring = empty("BAG_zip_pull_ring", c, 0.008, "CIRCLE", parent=slider, loc=(0.018, 0, 0.004))
    box("BAG_zip_pull_tab", c, 0.004, 0.026, -0.005, 0.005, 0.0, 0.003, chrome_mat(), 0.001, slider)
    # foam insert and products (bag-local)
    foam = M.clay("foam_grey", "#3c3c44", 0.95)
    box("BAG_foam_base", c, -B["L"] / 2 + 0.016, B["L"] / 2 - 0.016, -B["W"] / 2 + 0.016, B["W"] / 2 - 0.016, 0.012, 0.10, foam, 0.004, root)
    box("BAG_foam_divider", c, 0.108, 0.122, -B["W"] / 2 + 0.016, B["W"] / 2 - 0.016, 0.10, 0.16, foam, 0.002, root)
    P = C.PS5
    ps = empty("PS5_01", c, 0.1, "CUBE", parent=root, loc=(-0.095, 0.0, 0.101))     # lies flat: 390 long (x), 260 deep (y), 104 tall (z)
    white, black = M.clay("ps5_white", "#eceef2", 0.35), M.clay("ps5_black", "#101014", 0.4)
    box("PS5_core", c, -P["h"] / 2 + 0.01, P["h"] / 2 - 0.01, -P["d"] / 2 + 0.02, P["d"] / 2 - 0.02, 0.016, P["w"] - 0.016, black, 0.006, ps)
    box("PS5_plate_bottom", c, -P["h"] / 2, P["h"] / 2, -P["d"] / 2, P["d"] / 2, 0.0, 0.016, white, 0.008, ps)
    box("PS5_plate_top", c, -P["h"] / 2, P["h"] / 2, -P["d"] / 2, P["d"] / 2, P["w"] - 0.016, P["w"], white, 0.008, ps)
    box("PS5_light_strip", c, -P["h"] / 2 + 0.02, P["h"] / 2 - 0.02, P["d"] / 2 - 0.022, P["d"] / 2 - 0.018, P["w"] - 0.018, P["w"] - 0.015,
        M.emit("ps5_blue", "#4a7bff", 6), 0, ps)
    D = C.DUALSENSE
    ds = empty("DUALSENSE_01", c, 0.05, "CUBE", parent=root, loc=(0.205, 0.098, 0.101))
    box("DS_body", c, -0.055, 0.055, -0.03, 0.03, 0.0, 0.035, white, 0.012, ds)
    box("DS_touchpad", c, -0.03, 0.03, 0.0, 0.028, 0.035, 0.038, black, 0.003, ds)
    for k in (-1, 1):
        g = cyl(f"DS_grip_{k}", c, (k * 0.058, -0.022, 0.02), 0.022, 0.075, white, rot=(math.radians(70), 0, k * 0.3), verts=12, parent=ds)
        cyl(f"DS_stick_{k}", c, (k * 0.022, -0.012, 0.045), 0.010, 0.016, black, verts=12, parent=ds)
    fit_dims(ds, "DS_", (D["w"], D["d"], D["h"]))
    case = empty("GTA_CASE_01", c, 0.05, "CUBE", parent=root, loc=(0.205, -0.071, 0.101))
    cm = M.image("case_cover", "case_cover.png", 0.4)
    box("CASE_body", c, -C.CASE["w"] / 2, C.CASE["w"] / 2, -C.CASE["h"] / 2, C.CASE["h"] / 2, 0.0, C.CASE["t"] - 0.0005,
        M.clay("case_plastic", "#1c3a9a", 0.3), 0.002, case)
    quad("CASE_cover", c, [(-C.CASE["w"] / 2, -C.CASE["h"] / 2, C.CASE["t"]), (C.CASE["w"] / 2, -C.CASE["h"] / 2, C.CASE["t"]),
                           (C.CASE["w"] / 2, C.CASE["h"] / 2, C.CASE["t"]), (-C.CASE["w"] / 2, C.CASE["h"] / 2, C.CASE["t"])], cm, parent=case)
    # tag on a 4 cm cord from the pull ring. Tag-local: eyelet at the origin, card along +X (95 x 50 mm), text face = -Y.
    T = C.TAG
    tag_root = empty("TAG_01", c, 0.03, "ARROWS", parent=parent)
    front, back = M.image("tag_front", "tag_front.png", 0.8), M.image("tag_back", "tag_back.png", 0.8)
    w, h = T["w"], T["h"] / 2
    quad("TAG_face_front", c, [(0, -0.0006, -h), (w, -0.0006, -h), (w, -0.0006, h), (0, -0.0006, h)], front, parent=tag_root)
    quad("TAG_face_back", c, [(w, 0.0006, -h), (0, 0.0006, -h), (0, 0.0006, h), (w, 0.0006, h)], back, parent=tag_root)
    cord = cyl("TAG_cord", c, (-0.02, 0, 0), 0.0012, 0.04, M.clay("cord", "#d8d0c0", 0.9), rot=(0, math.pi / 2, 0), verts=6, parent=tag_root)
    return dict(root=root, shell=shell, flaps=flaps, gap=gap, slider=slider, ring=ring, tag=tag_root, cord=cord, ps5=ps, coll=c)


def fit_dims(group, prefix, spec):
    """Scale a product group (static) so its overall bounding box matches the approved real-world dimensions."""
    bpy.context.view_layer.update()
    inv = group.matrix_world.inverted()
    pts = [inv @ (o.matrix_world @ Vector(c)) for o in bpy.data.objects if o.name.startswith(prefix) and o.type == "MESH" for c in o.bound_box]
    size = [max(p[i] for p in pts) - min(p[i] for p in pts) for i in range(3)]
    group.scale = tuple(s / m for s, m in zip(spec, size))
    group.location.z -= min(p.z for p in pts) * group.scale.z        # lowest point rests on the foam, not in it


def chrome_mat():
    return M.clay("chrome", "#b8bcc8", 0.15, 1.0)


# ------------------------------------------------------------------ HELI_01 + searchlight, sky, haze
def heli():
    c = coll("HELI_01")
    root = empty("HELI_01", c, 2.0, "ARROWS")
    hm = M.clay("heli_body", "#24262e", 0.5, 0.3)
    bpy.ops.mesh.primitive_uv_sphere_add(segments=16, ring_count=10, radius=1.0)
    b = put(bpy.context.active_object, c)
    b.name = "HELI_body"
    b.scale = (1.1, 2.0, 1.0)
    b.data.materials.append(hm)
    b.parent = root
    box("HELI_tail", c, -0.15, 0.15, -6.0, -1.6, 0.2, 0.5, hm, 0.05, root)
    rotor = empty("HELI_rotor", c, 0.5, parent=root, loc=(0, 0, 1.15))
    box("HELI_blade_a", c, -5.0, 5.0, -0.15, 0.15, 0, 0.04, hm, 0, rotor)
    box("HELI_blade_b", c, -0.15, 0.15, -5.0, 5.0, 0, 0.04, hm, 0, rotor)
    nav = {k: box(f"HELI_nav_{k}", c, x - 0.08, x + 0.08, 0.3, 0.46, -0.2, -0.04, M.emit(f"nav_{k}", col, 40), 0, root)
           for k, x, col in (("red", -1.0, "#ff2020"), ("green", 1.0, "#20ff40"))}
    sd = bpy.data.lights.new("HELI_searchlight", "SPOT")
    sd.energy, sd.color = 2.6e6, (0.86, 0.92, 1.0)
    sd.spot_size, sd.spot_blend = math.radians(3.4), 0.18
    sd.shadow_soft_size = 0.05
    if hasattr(sd, "volume_factor"):
        sd.volume_factor = 1.0
    so = bpy.data.objects.new("HELI_searchlight", sd)
    c.objects.link(so)
    so.parent = root
    so.location = (0, 1.6, -0.9)
    tgt = empty("HELI_beam_target", c, 0.5, "SPHERE")
    tr = so.constraints.new("TRACK_TO")
    tr.target, tr.track_axis, tr.up_axis = tgt, "TRACK_NEGATIVE_Z", "UP_Y"
    lamp = box("HELI_lamp", c, -0.2, 0.2, 1.4, 1.75, -1.1, -0.75, M.emit("heli_lamp", "#e8f0ff", 60), 0.03, root)
    lamp.visible_shadow = False                               # the spot sits inside the lamp housing
    return root, rotor, so, tgt, nav


def sky_and_haze():
    sc = bpy.context.scene
    w = sc.world or bpy.data.worlds.new("World")
    sc.world = w
    w.use_nodes = True
    n, l = w.node_tree.nodes, w.node_tree.links
    bg = n["Background"]
    bg.inputs["Color"].default_value = C.rgb("#140c24")
    bg.inputs["Strength"].default_value = 0.35
    c = coll("FX_ATMOS")
    haze = box("FX_night_haze", c, -40, 30, -30, 60, 0.0, 40.0, bpy.data.materials.new("haze"))
    m = haze.data.materials[0]
    m.use_nodes = True
    n, l = m.node_tree.nodes, m.node_tree.links
    n.remove(n["Principled BSDF"])
    v = n.new("ShaderNodeVolumePrincipled")
    v.inputs["Color"].default_value = (0.7, 0.72, 0.8, 1)
    v.inputs["Density"].default_value = 0.0035
    l.new(v.outputs[0], n["Material Output"].inputs["Volume"])
    haze.visible_shadow = False
    return haze
