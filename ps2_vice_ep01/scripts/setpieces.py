"""ROOM_01, props (CONSOLE_01, DISC_01, CRT_01, controller), WORLD_01 (Ocean Drive), CAR_01, lights."""
import math
import random

import bmesh
import bpy
from mathutils import Vector

import config as C
import mats as M


def coll(name, parent=None):
    c = bpy.data.collections.get(name) or bpy.data.collections.new(name)
    if c.name not in [x.name for x in (parent or bpy.context.scene.collection).children]:
        (parent or bpy.context.scene.collection).children.link(c)
    return c


def put(o, c):
    for u in o.users_collection:
        u.objects.unlink(o)
    c.objects.link(o)
    return o


def box(name, c, x0, x1, y0, y1, z0, z1, mat, bevel=0.0):
    bpy.ops.mesh.primitive_cube_add(size=1, location=((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2))
    o = bpy.context.active_object
    o.name = name
    o.scale = (x1 - x0, y1 - y0, z1 - z0)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    if bevel:
        m = o.modifiers.new("bevel", "BEVEL")
        m.width, m.segments = bevel, 2
    o.data.materials.append(mat)
    return put(o, c)


def cyl(name, c, loc, r, depth, mat, rot=(0, 0, 0), verts=24, smooth=True):
    bpy.ops.mesh.primitive_cylinder_add(vertices=verts, radius=r, depth=depth, location=loc, rotation=rot)
    o = bpy.context.active_object
    o.name = name
    if smooth:
        bpy.ops.object.shade_smooth()
    o.data.materials.append(mat)
    return put(o, c)


def plane(name, c, loc, size, rot, mat):
    bpy.ops.mesh.primitive_plane_add(size=1, location=loc, rotation=rot)
    o = bpy.context.active_object
    o.name = name
    o.scale = (size[0], size[1], 1)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    o.data.materials.append(mat)
    return put(o, c)


def text(name, c, s, loc, rot, size, mat, align="CENTER", extrude=0.0):
    cu = bpy.data.curves.new(name, "FONT")
    cu.body, cu.size, cu.align_x, cu.align_y, cu.extrude = s, size, align, "CENTER", extrude
    cu.font = bpy.data.fonts.load("/usr/share/fonts/opentype/inter/Inter-Black.otf", check_existing=True)
    o = bpy.data.objects.new(name, cu)
    o.location, o.rotation_euler = loc, rot
    o.data.materials.append(mat)
    c.objects.link(o)
    return o


# ---------------------------------------------------------------- ROOM_01
def room():
    R, W = C.ROOM, C.ROOM["wall"]
    c = coll("ROOM_01")
    floor = M.clay("room_floor_wood", "#6b4a35", 0.75)
    wall = M.clay("room_wall", "#3c3358", 0.9)
    box("ROOM_floor", c, R["x0"] - W, R["x1"] + W, R["y0"] - W, R["y1"], -0.05, 0.0, floor)
    box("ROOM_ceiling", c, R["x0"] - W, R["x1"] + W, R["y0"] - W, R["y1"] + W, R["h"], R["h"] + 0.08, M.clay("room_ceiling", "#2b2540"))
    box("ROOM_wall_back", c, R["x0"] - W, R["x1"] + W, R["y0"] - W, R["y0"], 0, R["h"], wall)
    box("ROOM_wall_west", c, R["x0"] - W, R["x0"], R["y0"], R["y1"] + W, 0, R["h"], wall)
    box("ROOM_wall_east", c, R["x1"], R["x1"] + W, R["y0"], R["y1"] + W, 0, R["h"], wall)
    hw = C.CABINET["w"] / 2
    box("ROOM_wall_front_center", c, -hw, hw, R["y1"], R["y1"] + W, 0, R["h"], wall)
    box("ROOM_baseboard_back", c, R["x0"], R["x1"], R["y0"], R["y0"] + 0.015, 0, 0.08, M.clay("trim", "#211c30"))
    hinges = {}
    for side, hx, x0, x1 in (("W", R["x0"], R["x0"], -hw), ("E", R["x1"], hw, R["x1"])):
        h = bpy.data.objects.new(f"PORTAL_HINGE_{side}", None)
        h.empty_display_type, h.empty_display_size = "ARROWS", 0.3
        h.location = (hx, R["y1"], 0)
        c.objects.link(h)
        leaf = box(f"PORTAL_LEAF_{side}", c, x0, x1, R["y1"], R["y1"] + W, 0, R["h"], wall)
        leaf.parent = h
        leaf.matrix_parent_inverse = h.matrix_world.inverted()
        hinges[side] = h
    # rug, pouf, bed, desk
    cyl("ROOM_rug", c, (0, 0.55, 0.004), 1.0, 0.008, M.clay("rug", C.PAL["purple"], 0.95), verts=40)
    cyl("SEAT_pouf", c, (C.SEAT["x"], C.SEAT["y"], C.SEAT["h"] / 2), C.SEAT["r"], C.SEAT["h"], M.clay("pouf", "#2a2f55", 0.9), verts=28)
    B = C.BED
    bx0, bx1, by0, by1 = B["x"] - B["w"] / 2, B["x"] + B["w"] / 2, B["y"] - B["d"] / 2, B["y"] + B["d"] / 2
    box("BED_frame", c, bx0, bx1, by0, by1, 0, 0.28, M.clay("bed_frame", "#3a2a22"), 0.02)
    box("BED_mattress", c, bx0 + 0.03, bx1 - 0.03, by0 + 0.03, by1 - 0.03, 0.28, B["h"], M.clay("mattress", "#d8d2c8"), 0.04)
    box("BED_blanket", c, bx0 + 0.45, bx1 - 0.0, by0 + 0.0, by1 + 0.02, B["h"] - 0.02, B["h"] + 0.05,
        M.image("plaid", "plaid.png", 0.95), 0.03)
    box("BED_pillow", c, bx0 + 0.06, bx0 + 0.42, by0 + 0.12, by1 - 0.12, B["h"], B["h"] + 0.12, M.clay("pillow", "#e8e4ee"), 0.05)
    D = C.DESK
    dx0, dx1, dy0, dy1 = D["x"] - D["w"] / 2, D["x"] + D["w"] / 2, D["y"] - D["d"] / 2, D["y"] + D["d"] / 2
    dm = M.clay("desk", "#4a3528", 0.7)
    box("DESK_top", c, dx0, dx1, dy0, dy1, D["h"] - 0.03, D["h"], dm, 0.008)
    for i, (x, y) in enumerate([(dx0 + 0.03, dy0 + 0.03), (dx1 - 0.03, dy0 + 0.03), (dx0 + 0.03, dy1 - 0.03), (dx1 - 0.03, dy1 - 0.03)]):
        box(f"DESK_leg{i}", c, x - 0.02, x + 0.02, y - 0.02, y + 0.02, 0, D["h"] - 0.03, dm)
    # desk lamp (practical): base, arm, shade, bulb + warm point light
    z = D["h"]
    lx, ly = D["x"] - 0.05, D["y"] + 0.35
    cyl("LAMP_base", c, (lx, ly, z + 0.012), 0.07, 0.024, M.clay("lamp_metal", "#1e1e24", 0.4, 0.6))
    cyl("LAMP_arm", c, (lx, ly, z + 0.2), 0.008, 0.38, M.clay("lamp_metal", "#1e1e24"))
    bpy.ops.mesh.primitive_cone_add(vertices=24, radius1=0.12, radius2=0.05, depth=0.13, location=(lx, ly, z + 0.43))
    sh = put(bpy.context.active_object, c)
    sh.name = "LAMP_shade"
    sh.data.materials.append(M.emit("lamp_shade_glow", "#ffb35c", 2.2))
    lp = bpy.data.lights.new("LAMP_light", "POINT")
    lp.energy, lp.color, lp.shadow_soft_size = 70, (1.0, 0.68, 0.38), 0.06
    fl = bpy.data.lights.new("ROOM_fill", "AREA")
    fl.shape, fl.size, fl.size_y, fl.energy, fl.color = "RECTANGLE", 3.0, 2.5, 60, (0.62, 0.55, 1.0)
    fo = bpy.data.objects.new("ROOM_fill", fl)
    fo.location = (-0.5, -0.2, R["h"] - 0.05)
    c.objects.link(fo)
    lo = bpy.data.objects.new("LAMP_light", lp)
    lo.location = (lx, ly, z + 0.36)
    c.objects.link(lo)
    # set dressing (reference sheet): lava lamp, CD stack, soda can, pizza box, posters, neon strip
    cyl("PROP_lavalamp_base", c, (D["x"] + 0.12, D["y"] - 0.35, z + 0.05), 0.045, 0.10, M.clay("lava_metal", "#888890", 0.3, 0.8))
    cyl("PROP_lavalamp_glass", c, (D["x"] + 0.12, D["y"] - 0.35, z + 0.2), 0.04, 0.2, M.emit("lava", C.PAL["pink"], 3.0))
    for i in range(7):
        box(f"PROP_cd_{i}", c, D["x"] - 0.12, D["x"] + 0.02, D["y"] - 0.05 + i * 0.002, D["y"] + 0.07 + i * 0.002,
            z + i * 0.011, z + i * 0.011 + 0.01, M.clay(f"cdcase{i % 3}", ["#22c9ce", "#f54ba5", "#d8d8e0"][i % 3], 0.4))
    cyl("PROP_soda_can", c, (D["x"] + 0.16, D["y"] + 0.05, z + 0.06), 0.033, 0.12, M.clay("can", "#c8302e", 0.35, 0.6))
    box("PROP_pizza_box", c, -1.05, -0.65, -0.75, -0.35, 0.0, 0.045, M.clay("pizza_box", "#e6dcc8", 0.9))
    poster_specs = [("POSTER_west_a", (R["x0"] + 0.005, -0.6, 1.55), (math.pi / 2, 0, -math.pi / 2), "poster_a.png"),
                    ("POSTER_west_b", (R["x0"] + 0.005, 0.7, 1.55), (math.pi / 2, 0, -math.pi / 2), "poster_b.png"),
                    ("POSTER_back_a", (-1.7, R["y0"] + 0.005, 1.6), (math.pi / 2, 0, 0), "poster_b.png"),
                    ("POSTER_east_a", (R["x1"] - 0.005, 0.6, 1.6), (math.pi / 2, 0, math.pi / 2), "poster_a.png")]
    for n, loc, rot, f in poster_specs:
        plane(n, c, loc, (0.6, 0.84), rot, M.image(f, f, 0.8))
    box("NEON_strip_back", c, R["x0"] + 0.1, R["x1"] - 0.1, R["y0"] + 0.01, R["y0"] + 0.04, R["h"] - 0.06, R["h"] - 0.03,
        M.emit("neon_purple", C.PAL["purple"], 8.0))
    return c, hinges


# ---------------------------------------------------------------- CRT_01, CONSOLE_01, DISC_01, controller
def disc_mesh(name, c):
    D = C.DISC
    me = bpy.data.meshes.new(name)
    bm = bmesh.new()
    uv = bm.loops.layers.uv.new()
    n = 64
    rings = []
    for z in (D["t"], 0.0):
        rings.append(([bm.verts.new((math.cos(2 * math.pi * i / n) * D["r"], math.sin(2 * math.pi * i / n) * D["r"], z)) for i in range(n)],
                      [bm.verts.new((math.cos(2 * math.pi * i / n) * D["hole_r"], math.sin(2 * math.pi * i / n) * D["hole_r"], z)) for i in range(n)]))
    faces = []
    for k, (o, inn) in enumerate(rings):
        for i in range(n):
            j = (i + 1) % n
            q = [o[i], o[j], inn[j], inn[i]] if k == 0 else [o[j], o[i], inn[i], inn[j]]
            f = bm.faces.new(q)
            f.material_index = k
            faces.append(f)
    for i in range(n):
        j = (i + 1) % n
        bm.faces.new([rings[0][0][j], rings[0][0][i], rings[1][0][i], rings[1][0][j]]).material_index = 1
        bm.faces.new([rings[0][1][i], rings[0][1][j], rings[1][1][j], rings[1][1][i]]).material_index = 1
    for f in faces:
        for lp in f.loops:
            lp[uv].uv = (lp.vert.co.x / (2 * D["r"]) + 0.5, lp.vert.co.y / (2 * D["r"]) + 0.5)
    bm.to_mesh(me)
    bm.free()
    o = bpy.data.objects.new(name, me)
    me.materials.append(M.image("disc_label", "disc_label.png", 0.35))
    me.materials.append(M.clay("disc_data_side", "#c8ccd8", 0.08, 1.0))
    for p in me.polygons:
        p.use_smooth = False
    c.objects.link(o)
    return o


def crt_screen_material():
    m = bpy.data.materials.new("CRT_screen")
    m.use_nodes = True
    n, l = m.node_tree.nodes, m.node_tree.links
    b = n["Principled BSDF"]
    b.inputs["Base Color"].default_value = (0.01, 0.012, 0.015, 1)
    b.inputs["Roughness"].default_value = 0.12
    b.inputs["Specular IOR Level"].default_value = 0.6
    tex = {}
    for k, f in (("standby", "crt_standby.png"), ("title", "crt_title.png")):
        t = n.new("ShaderNodeTexImage")
        t.image = bpy.data.images.load(f"{C.P['tex']}/{f}", check_existing=True)
        tex[k] = t
    g = n.new("ShaderNodeTexImage")
    g.name = "gameplay"
    img = bpy.data.images.new("CRT_gameplay_seq", 640, 480)
    img.source = "SEQUENCE"
    img.filepath = "//../textures/gameplay/g_0385.png"          # rendered by scripts/render_gameplay.py
    g.image = img
    g.image_user.frame_duration, g.image_user.frame_start, g.image_user.frame_offset = 96, 385, 384
    g.image_user.use_auto_refresh = True
    vals = {}
    for k in ("title_mix", "game_mix", "power"):
        v = n.new("ShaderNodeValue")
        v.name = v.label = k
        vals[k] = v
    m1 = n.new("ShaderNodeMix")
    m1.data_type = "RGBA"
    l.new(vals["title_mix"].outputs[0], m1.inputs["Factor"])
    l.new(tex["standby"].outputs["Color"], m1.inputs[6])
    l.new(tex["title"].outputs["Color"], m1.inputs[7])
    m2 = n.new("ShaderNodeMix")
    m2.data_type = "RGBA"
    l.new(vals["game_mix"].outputs[0], m2.inputs["Factor"])
    l.new(m1.outputs[2], m2.inputs[6])
    l.new(g.outputs["Color"], m2.inputs[7])
    l.new(m2.outputs[2], b.inputs["Emission Color"])
    l.new(vals["power"].outputs[0], b.inputs["Emission Strength"])
    return m, vals


def screen_mesh(name, c, w, h, bulge):
    bpy.ops.mesh.primitive_grid_add(x_subdivisions=24, y_subdivisions=18, size=1)
    o = put(bpy.context.active_object, c)
    o.name = name
    for v in o.data.vertices:
        x, y = v.co.x * w, v.co.y * h
        v.co = (x, y, bulge * (1 - (x / (w * 0.5)) ** 2 * 0.5 - (y / (h * 0.5)) ** 2 * 0.5))
    bpy.ops.object.shade_smooth()
    return o


def hardware():
    c = coll("HARDWARE")
    K, T, P = C.CABINET, C.CRT, C.PS2
    cm = M.clay("cabinet", "#2a2228", 0.7)
    x0, x1, y0, y1 = K["x"] - K["w"] / 2, K["x"] + K["w"] / 2, K["y"] - K["d"] / 2, K["y"] + K["d"] / 2
    box("CABINET_top", c, x0, x1, y0, y1, K["h"] - 0.03, K["h"], cm, 0.005)
    box("CABINET_bottom", c, x0, x1, y0, y1, 0.04, 0.07, cm)
    box("CABINET_shelf", c, x0 + 0.03, x1 - 0.03, y0 + 0.02, y1, K["shelf_z"] - 0.025, K["shelf_z"], cm)
    box("CABINET_side_W", c, x0, x0 + 0.03, y0, y1, 0.0, K["h"] - 0.03, cm)
    box("CABINET_side_E", c, x1 - 0.03, x1, y0, y1, 0.0, K["h"] - 0.03, cm)
    box("CABINET_back", c, x0 + 0.03, x1 - 0.03, y1 - 0.02, y1, 0.07, K["h"] - 0.03, cm)
    # CRT_01
    tz = K["h"]
    fy = T["y"] - T["d"] / 2
    crt = M.clay("crt_shell", "#3b3a40", 0.55)
    box("CRT_bezel", c, -T["w"] / 2, T["w"] / 2, fy, fy + 0.2, tz, tz + T["h"], crt, 0.03)
    box("CRT_tube", c, -T["w"] * 0.36, T["w"] * 0.36, fy + 0.2, fy + T["d"], tz + 0.04, tz + T["h"] - 0.06, crt, 0.06)
    box("CRT_foot", c, -0.2, 0.2, fy + 0.05, fy + 0.4, tz, tz + 0.015, crt)
    sw, shh = T["screen"]
    sm, vals = crt_screen_material()
    scr = screen_mesh("CRT_screen", c, sw, shh, 0.022)
    scr.rotation_euler = (math.pi / 2, 0, 0)
    scr.location = (0, fy - 0.004, tz + T["h"] / 2 + 0.02)
    scr.data.materials.append(sm)
    for i, (x, col) in enumerate([(0.22, "#30ff60"), (0.26, "#ff4040")]):
        cyl(f"CRT_led{i}", c, (x, fy - 0.002, tz + 0.04), 0.005, 0.004, M.emit(f"led{i}", col, 3), rot=(math.pi / 2, 0, 0))
    screen_center = Vector((0, fy - 0.03, tz + T["h"] / 2 + 0.02))
    al = bpy.data.lights.new("CRT_glow", "AREA")
    al.shape, al.size, al.size_y, al.energy = "RECTANGLE", sw, shh, 6
    alo = bpy.data.objects.new("CRT_glow", al)
    alo.location = screen_center + Vector((0, -0.03, 0))
    alo.rotation_euler = (-math.pi / 2, 0, 0)
    c.objects.link(alo)
    # CONSOLE_01: horizontal PS2-style console (no logos), tray on the front
    pm = M.clay("console_black", "#121216", 0.45)
    sz = P["z"]
    px0, px1 = P["x"] - P["w"] / 2, P["x"] + P["w"] / 2
    ps = box("PS2_body", c, px0, px1, P["front_y"], P["front_y"] + P["d"], sz, sz + P["h"], pm, 0.004)
    for i in range(3):
        box(f"PS2_groove{i}", c, px0 + 0.01, px1 - 0.01, P["front_y"] - 0.001, P["front_y"] + 0.002,
            sz + 0.016 + i * 0.012, sz + 0.019 + i * 0.012, M.clay("console_groove", "#050507", 0.6))
    box("PS2_slot", c, P["x"] - 0.08, P["x"] + 0.06, P["front_y"] - 0.0015, P["front_y"] + 0.001, sz + 0.050, sz + 0.066,
        M.clay("console_slot", "#030304", 0.8))
    box("PS2_led_blue", c, px1 - 0.03, px1 - 0.012, P["front_y"] - 0.002, P["front_y"], sz + 0.012, sz + 0.016, M.emit("ps2_blue", "#2050ff", 6))
    tray = bpy.data.objects.new("PS2_TRAY", None)
    tray.empty_display_type, tray.empty_display_size = "PLAIN_AXES", 0.05
    tray.location = (P["x"] - 0.01, P["front_y"] - P["tray_out"] + 0.07, sz + 0.050)   # open position
    c.objects.link(tray)
    tm = M.clay("tray", "#16161b", 0.5)
    parts = [box("PS2_tray_plate", c, -0.068, 0.068, -0.07, 0.07, 0.0, 0.010, tm),
             box("PS2_tray_lip", c, -0.068, 0.068, -0.072, -0.066, -0.002, 0.016, tm),
             cyl("PS2_tray_recess", c, (0, 0, 0.0105), 0.061, 0.001, M.clay("tray_recess", "#0a0a0d", 0.6), verts=48),
             cyl("PS2_tray_spindle", c, (0, 0, 0.0115), 0.0072, 0.003, M.clay("spindle", "#2a2a30", 0.5), verts=16)]
    for p in parts:
        p.parent = tray
    disc = disc_mesh("DISC_01", c)
    # controller (one object hierarchy, matching black clay)
    ctl = bpy.data.objects.new("CONTROLLER_01", None)
    ctl.empty_display_type, ctl.empty_display_size = "PLAIN_AXES", 0.05
    c.objects.link(ctl)
    cp = [box("CTRL_body", c, -0.075, 0.075, -0.03, 0.03, -0.018, 0.018, pm, 0.012)]
    for k in (-1, 1):
        g = cyl(f"CTRL_grip_{'L' if k < 0 else 'R'}", c, (k * 0.056, -0.04, -0.008), 0.022, 0.06, pm, rot=(1.25, 0, k * 0.25), verts=12)
        cp.append(g)
        cp.append(cyl(f"CTRL_stick_{'L' if k < 0 else 'R'}", c, (k * 0.025, -0.012, 0.024), 0.011, 0.012,
                      M.clay("ctrl_stick", "#0a0a0c", 0.6), verts=12))
    for i, col in enumerate([C.PAL["cyan"], C.PAL["pink"], "#4b7bff", "#ff4b4b"]):
        a = i * math.pi / 2
        cp.append(cyl(f"CTRL_btn{i}", c, (0.05 + math.cos(a) * 0.011, 0.008 + math.sin(a) * 0.011, 0.019), 0.0045, 0.004,
                      M.clay(f"ctrl_btn{i}", col, 0.4), verts=8))
    for p in cp:
        p.parent = ctl
    return dict(screen_vals=vals, crt_glow=alo, screen_center=screen_center, tray=tray, disc=disc, controller=ctl, coll=c)


# ---------------------------------------------------------------- WORLD_01: Ocean Drive at sunset
def world():
    c = coll("WORLD_01_OCEAN_DRIVE")
    R = C.ROOM
    y0 = R["y1"] + R["wall"]
    box("STREET_asphalt", c, -9.0, 7.0, y0, 240, -0.05, 0.0, M.clay("asphalt", "#2a2a36", 0.7))
    for y in range(int(y0) + 3, 236, 6):
        box(f"STREET_dash_{y:03d}", c, -0.08, 0.08, y, y + 3, 0.0, 0.004, M.clay("dash", "#e8c060", 0.6))
    for side, (a, b) in (("W", (-13.0, -9.0)), ("E", (7.0, 11.0))):
        box(f"SIDEWALK_{side}", c, a, b, y0, 240, 0, 0.15, M.clay("sidewalk", "#b8a8b8", 0.85))
    rnd = random.Random(7)
    pastel = ["#f6a6c8", "#8fe0e0", "#ffd2a0", "#b9a2e0", "#f3ead8", "#ff8fb8"]
    neon_words = ["HOTEL", "OCEAN DRIVE", "CAFE", "MOTEL", "DINER", "CLUB", "BAR", "HOTEL"]
    signs = []
    for side, k, xf in (("W", -1, -13.0), ("E", 1, 11.0)):
        y, i = 4.0, 0
        while y < 230:
            L, Hh, Dd = rnd.uniform(10, 16), rnd.uniform(7, 15), 9
            col = pastel[(i + (0 if k < 0 else 3)) % len(pastel)]
            xa, xb = (xf - Dd, xf) if k < 0 else (xf, xf + Dd)
            box(f"FACADE_{side}_{i:02d}", c, xa, xb, y, y + L - 0.6, 0, Hh, M.clay(f"facade_{col}", col, 0.85), 0.05)
            face = xf + (0.02 if k < 0 else -0.02)
            for fl in range(1, int(Hh // 3.2)):
                box(f"FACADE_{side}_{i:02d}_win{fl}", c, face - 0.03, face + 0.03, y + 1.0, y + L - 1.6, fl * 3.2 + 0.4,
                    fl * 3.2 + 1.6, M.emit("window_warm", "#ffb35c", 1.2) if rnd.random() < 0.5 else M.clay("window_dark", "#24304a", 0.2))
            ncol = [C.PAL["pink"], C.PAL["cyan"], C.PAL["purple"]][i % 3]
            box(f"FACADE_{side}_{i:02d}_neonband", c, face - 0.05, face + 0.05, y, y + L - 0.6, 3.0, 3.12, M.emit(f"neon_{ncol}", ncol, 10))
            if i % 2 == 0:
                t = text(f"NEON_{side}_{i:02d}", c, neon_words[(i // 2 + (0 if k < 0 else 2)) % len(neon_words)],
                         (face - k * 0.08, y + L / 2, 4.6), (math.pi / 2, 0, -k * math.pi / 2), 1.1, M.emit(f"neonsign_{ncol}", ncol, 14),
                         extrude=0.03)
                signs.append(t)
            y += L
            i += 1
    for side, x in (("W", -11.0), ("E", 9.0)):
        for j, y in enumerate(range(8, 230, 9)):
            palm(f"PALM_{side}_{j:02d}", c, (x, y, 0.15), rnd)
    sky = M.clay("skyline", C.PAL["navy"], 0.9)
    for j in range(26):
        x = -60 + j * 4.8 + rnd.uniform(-1, 1)
        h = rnd.uniform(25, 85)
        box(f"SKYLINE_{j:02d}", c, x, x + rnd.uniform(3, 6), 255 + rnd.uniform(0, 20), 262 + rnd.uniform(0, 20), 0, h, sky)
        box(f"SKYLINE_{j:02d}_lights", c, x + 0.5, x + 2.5, 254.9, 255.0, h * 0.3, h * 0.85, M.emit("skyline_win", C.PAL["purple"], 3))
    return c


def palm(name, c, base, rnd):
    h = rnd.uniform(7, 10)
    lean = rnd.uniform(-0.8, 0.8)
    cu = bpy.data.curves.new(name + "_trunk", "CURVE")
    cu.dimensions, cu.bevel_depth, cu.bevel_resolution = "3D", 0.16, 2
    sp = cu.splines.new("BEZIER")
    sp.bezier_points.add(1)
    p0, p1 = Vector(base), Vector(base) + Vector((lean, 0, h))
    for bp, co in zip(sp.bezier_points, (p0, p1)):
        bp.co, bp.handle_left_type, bp.handle_right_type = co, "AUTO", "AUTO"
    o = bpy.data.objects.new(name + "_trunk", cu)
    o.data.materials.append(M.clay("palm_trunk", "#3a2c30", 0.9))
    c.objects.link(o)
    fm = M.clay("palm_frond", "#1c3a3a", 0.9)
    for k in range(9):
        a = k * 2 * math.pi / 9 + rnd.uniform(-0.2, 0.2)
        bpy.ops.mesh.primitive_cube_add(size=1)
        f = put(bpy.context.active_object, c)
        f.name = f"{name}_frond{k}"
        f.scale = (2.6, 0.38, 0.04)
        bpy.ops.object.transform_apply(scale=True)
        f.location = p1 + Vector((math.cos(a) * 1.15, math.sin(a) * 1.15, -0.35))
        f.rotation_euler = (0, 0.45, a)          # XYZ order: droop about Y, then yaw about Z
        f.data.materials.append(fm)


# ---------------------------------------------------------------- CAR_01 (proxy sports car)
def car(name, c):
    K = C.CAR
    root = bpy.data.objects.new(name, None)
    root.empty_display_type, root.empty_display_size = "ARROWS", 0.8
    c.objects.link(root)
    body = M.clay("car_paint", C.PAL["pink"], 0.35, 0.2, 0.6)
    L, W = K["len"], K["w"]
    # car faces -Y (toward the room); root at the centre of the wheelbase on the ground
    bw = W - 0.30
    parts = [box(f"{name}_body", c, -bw / 2, bw / 2, -L / 2 + 0.35, L / 2, 0.22, 0.66, body, 0.08),
             box(f"{name}_nose", c, -bw / 2 + 0.03, bw / 2 - 0.03, -L / 2, -L / 2 + 0.6, 0.22, 0.48, body, 0.1),
             box(f"{name}_cabin", c, -bw / 2 + 0.12, bw / 2 - 0.12, -0.45, 0.95, 0.66, K["h"] - 0.04, M.clay("car_glass", "#3a6e88", 0.08, 0.4, 0.9), 0.12),
             box(f"{name}_roof", c, -bw / 2 + 0.18, bw / 2 - 0.18, -0.25, 0.75, K["h"] - 0.06, K["h"], body, 0.04),
             box(f"{name}_spoiler", c, -bw / 2 + 0.05, bw / 2 - 0.05, L / 2 - 0.3, L / 2 - 0.05, 0.84, 0.88, body, 0.02)]
    for k in (-1, 1):
        for j, wy in enumerate((-L / 2 + 0.78, L / 2 - 0.8)):
            parts.append(box(f"{name}_arch{k}{j}", c, k * bw / 2 - 0.02 if k > 0 else -bw / 2 - 0.13, k * bw / 2 + 0.13 if k > 0 else -bw / 2 + 0.02,
                             wy - 0.42, wy + 0.42, 0.58, 0.68, body, 0.03))
    for k in (-1, 1):
        parts.append(box(f"{name}_headlight_{k}", c, k * 0.62 - 0.18, k * 0.62 + 0.18, -L / 2 - 0.06, -L / 2 - 0.02, 0.38, 0.45,
                         M.emit("headlight", "#fff2d8", 6)))
        parts.append(box(f"{name}_taillight_{k}", c, k * 0.6 - 0.25, k * 0.6 + 0.25, L / 2, L / 2 + 0.02, 0.42, 0.5, M.emit("taillight", "#ff2040", 8)))
    for p in parts:
        p.parent = root
    wheels = []
    r = K["wheel_r"]
    tire, rim = M.clay("tire", "#0c0c0e", 0.85), M.clay("rim", "#c0c0c8", 0.3, 0.9)
    for k, (wx, wy) in enumerate([(-W / 2 + 0.12, -L / 2 + 0.78), (W / 2 - 0.12, -L / 2 + 0.78), (-W / 2 + 0.12, L / 2 - 0.8), (W / 2 - 0.12, L / 2 - 0.8)]):
        hub = bpy.data.objects.new(f"{name}_wheel{k}", None)
        hub.empty_display_type, hub.empty_display_size = "CIRCLE", r
        hub.location = (wx, wy, r)
        hub.parent = root
        c.objects.link(hub)
        t = cyl(f"{name}_tire{k}", c, (0, 0, 0), r, 0.24, tire, rot=(0, math.pi / 2, 0), verts=20)
        s1 = box(f"{name}_spoke{k}a", c, -0.13, 0.13, -0.025, 0.025, -r * 0.75, r * 0.75, rim)
        s2 = box(f"{name}_spoke{k}b", c, -0.13, 0.13, -r * 0.75, r * 0.75, -0.025, 0.025, rim)
        for p in (t, s1, s2):
            p.parent = hub
        wheels.append(hub)
    return root, wheels


# ---------------------------------------------------------------- sky, sun, fog
def lights_and_sky():
    sc = bpy.context.scene
    w = sc.world or bpy.data.worlds.new("World")
    sc.world = w
    w.use_nodes = True
    n, l = w.node_tree.nodes, w.node_tree.links
    for x in list(n):
        if x.type != "OUTPUT_WORLD":
            n.remove(x)
    tc, sep, cr, bg = n.new("ShaderNodeTexCoord"), n.new("ShaderNodeSeparateXYZ"), n.new("ShaderNodeValToRGB"), n.new("ShaderNodeBackground")
    l.new(tc.outputs["Generated"], sep.inputs[0])
    l.new(sep.outputs["Z"], cr.inputs[0])
    els = cr.color_ramp.elements
    els[0].position, els[0].color = 0.48, C.rgb(C.PAL["orange"])
    els[1].position, els[1].color = 0.70, C.rgb(C.PAL["navy"])
    e = els.new(0.54)
    e.color = C.rgb(C.PAL["pink"])
    e = els.new(0.61)
    e.color = C.rgb(C.PAL["purple"])
    l.new(cr.outputs[0], bg.inputs["Color"])
    bg.inputs["Strength"].default_value = 1.0
    l.new(bg.outputs[0], n["World Output"].inputs["Surface"])
    sd = bpy.data.lights.new("SUN_sunset", "SUN")
    sd.energy, sd.color, sd.angle = 3.2, (1.0, 0.55, 0.42), math.radians(1.5)
    so = bpy.data.objects.new("SUN_sunset", sd)
    so.rotation_mode = "XYZ"
    # sun low at the far end of Ocean Drive (+Y), 7 degrees up: light travels toward -Y, into the room
    so.rotation_euler = (math.radians(90 - 7) * -1, 0, math.radians(8))
    sc.collection.objects.link(so)
    c = coll("FX")
    fog = box("FX_magenta_fog", c, C.ROOM["x0"], C.ROOM["x1"], 1.45, 10.0, 0.0, C.ROOM["h"], bpy.data.materials.new("fog_mat"))
    fm = fog.data.materials[0]
    fm.use_nodes = True
    n, l = fm.node_tree.nodes, fm.node_tree.links
    n.remove(n["Principled BSDF"])
    v = n.new("ShaderNodeVolumePrincipled")
    v.inputs["Color"].default_value = C.rgb(C.PAL["pink"])
    v.inputs["Density"].default_value = 0.0
    v.inputs["Emission Color"].default_value = C.rgb(C.PAL["purple"])
    v.inputs["Emission Strength"].default_value = 0.0
    l.new(v.outputs[0], n["Material Output"].inputs["Volume"])
    return so, v
