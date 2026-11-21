"""OFFBRIEF. / THE PITCH ROOM 2.0 / EP01 'THE PRODUCT IS MISSING' - master scene builder.

One continuous pitch room, six seated proxy actors on armatures, ten cameras bound to markers.
    blender -b --factory-startup --python scripts/build.py
Writes scenes/OFFBRIEF_EP01_MASTER.blend. All shot, cast and camera data lives in scripts/shotlist.py.
"""
import math
import os
import random
import sys

import bpy
from bpy_extras import anim_utils
from mathutils import Matrix, Vector

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import shotlist as S  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BLEND = os.path.join(ROOT, "scenes", "OFFBRIEF_EP01_MASTER.blend")
rnd = random.Random(1)

bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene
sc.name = "OFFBRIEF_EP01_MASTER"

# ------------------------------------------------------------------ collections
COLL = {}
for n in ("ENV_ARCHITECTURE", "ENV_FURNITURE", "ENV_PROPS", "CAST_RIGS", "CAMERAS", "LIGHTING",
          "ANIMATION", "SHOT_MARKERS", "REFERENCE_IMAGES"):
    c = bpy.data.collections.new(n)
    sc.collection.children.link(c)
    COLL[n] = c


def link(o, coll):
    for c in list(o.users_collection):
        c.objects.unlink(o)
    COLL[coll].objects.link(o) if isinstance(coll, str) else coll.objects.link(o)
    return o


# ------------------------------------------------------------------ materials
MATS = {}


def mat(name, col, rough=0.5, metal=0.0, emit=0.0, alpha=1.0, coat=0.0, sss=0.0):
    if name in MATS:
        return MATS[name]
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    p = m.node_tree.nodes["Principled BSDF"]
    p.inputs["Base Color"].default_value = (*col, 1)
    p.inputs["Roughness"].default_value = rough
    p.inputs["Metallic"].default_value = metal
    p.inputs["Coat Weight"].default_value = coat
    p.inputs["Subsurface Weight"].default_value = sss
    if emit:
        p.inputs["Emission Color"].default_value = (*col, 1)
        p.inputs["Emission Strength"].default_value = emit
    if alpha < 1:
        p.inputs["Alpha"].default_value = alpha
        m.surface_render_method = "BLENDED"
    m.diffuse_color = (*col, 1)
    MATS[name] = m
    return m


def tex_mat(name, kind, c1, c2, scale, rough=0.5, bump=0.1, extra=None):
    """Procedural two-colour material: kind in NOISE, BRICK, VORONOI, WAVE."""
    m = mat(name, c1, rough)
    nt = m.node_tree
    p = nt.nodes["Principled BSDF"]
    tc = nt.nodes.new("ShaderNodeTexCoord")
    if kind == "BRICK":
        t = nt.nodes.new("ShaderNodeTexBrick")
        t.inputs["Color1"].default_value = (*c1, 1)
        t.inputs["Color2"].default_value = (*[x * 0.8 for x in c1], 1)
        t.inputs["Mortar"].default_value = (*c2, 1)
        t.inputs["Scale"].default_value = scale
        t.inputs["Mortar Size"].default_value = 0.012
        t.inputs["Brick Width"].default_value = 0.5
        t.inputs["Row Height"].default_value = 0.25
        nt.links.new(tc.outputs["Object"], t.inputs["Vector"])
        nt.links.new(t.outputs["Color"], p.inputs["Base Color"])
        fac = t.outputs["Fac"]
    else:
        t = nt.nodes.new({"NOISE": "ShaderNodeTexNoise", "VORONOI": "ShaderNodeTexVoronoi",
                          "WAVE": "ShaderNodeTexWave"}[kind])
        t.inputs["Scale"].default_value = scale
        if kind == "NOISE":
            t.inputs["Detail"].default_value = 8
        nt.links.new(tc.outputs["Object"], t.inputs["Vector"])
        r = nt.nodes.new("ShaderNodeValToRGB")
        out = t.outputs["Distance"] if kind == "VORONOI" else t.outputs["Fac"]
        nt.links.new(out, r.inputs["Fac"])
        r.color_ramp.elements[0].color = (*c1, 1)
        r.color_ramp.elements[1].color = (*c2, 1)
        if extra:
            r.color_ramp.elements[0].position, r.color_ramp.elements[1].position = extra
        nt.links.new(r.outputs["Color"], p.inputs["Base Color"])
        fac = out
    if bump:
        b = nt.nodes.new("ShaderNodeBump")
        b.inputs["Strength"].default_value = bump
        nt.links.new(fac, b.inputs["Height"])
        nt.links.new(b.outputs["Normal"], p.inputs["Normal"])
    return m


def emission_image(name, path, strength):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    nt.nodes.remove(nt.nodes["Principled BSDF"])
    t = nt.nodes.new("ShaderNodeTexImage")
    t.image = bpy.data.images.load(path)
    e = nt.nodes.new("ShaderNodeEmission")
    e.inputs["Strength"].default_value = strength
    nt.links.new(t.outputs["Color"], e.inputs["Color"])
    nt.links.new(e.outputs[0], nt.nodes["Material Output"].inputs[0])
    return m


# ------------------------------------------------------------------ mesh helpers
def box(name, size, loc, m, coll, rot=(0, 0, 0), bevel=0.0):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc, rotation=rot)
    o = bpy.context.object
    o.name = name
    o.scale = size
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    if bevel:
        b = o.modifiers.new("Bevel", "BEVEL")
        b.width, b.segments = bevel, 2
    o.data.materials.append(m)
    return link(o, coll)


def cyl(name, r, depth, loc, m, coll, rot=(0, 0, 0), verts=24, smooth=True):
    bpy.ops.mesh.primitive_cylinder_add(vertices=verts, radius=r, depth=depth, location=loc, rotation=rot)
    o = bpy.context.object
    o.name = name
    if smooth:
        bpy.ops.object.shade_smooth()
    o.data.materials.append(m)
    return link(o, coll)


def cyl_between(name, a, b, r, m, coll, verts=16):
    a, b = Vector(a), Vector(b)
    d = b - a
    o = cyl(name, r, d.length, (a + b) / 2, m, coll, verts=verts)
    o.rotation_euler = d.to_track_quat("Z", "Y").to_euler()
    return o


def ell(name, size, loc, m, coll, seg=16):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=seg, ring_count=max(6, seg // 2), radius=0.5, location=loc)
    o = bpy.context.object
    o.name = name
    o.scale = size
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    bpy.ops.object.shade_smooth()
    o.data.materials.append(m)
    return link(o, coll)


def torus(name, R, r, loc, m, coll, rot=(0, 0, 0), scale=(1, 1, 1)):
    bpy.ops.mesh.primitive_torus_add(major_radius=R, minor_radius=r, major_segments=24, minor_segments=6,
                                     location=loc, rotation=rot)
    o = bpy.context.object
    o.name = name
    o.scale = scale
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
    bpy.ops.object.shade_smooth()
    o.data.materials.append(m)
    return link(o, coll)


def empty(name, coll, loc=(0, 0, 0), size=0.05, shape="SPHERE"):
    e = bpy.data.objects.new(name, None)
    e.empty_display_type, e.empty_display_size = shape, size
    e.location = loc
    COLL[coll].objects.link(e)
    return e


def fcurves(idb):
    ad = idb.animation_data
    return anim_utils.action_get_channelbag_for_slot(ad.action, ad.action_slot).fcurves


def fcurve(idb, path, index):
    for fc in fcurves(idb):
        if fc.data_path == path and fc.array_index == index:
            return fc
    return None


# ------------------------------------------------------------------ scene settings
sc.render.fps = S.FPS
sc.frame_start, sc.frame_end = S.FRAME_START, S.FRAME_END
sc.render.resolution_x, sc.render.resolution_y, sc.render.resolution_percentage = 1920, 1080, 100
sc.render.engine = "BLENDER_EEVEE"
sc.unit_settings.system, sc.unit_settings.scale_length = "METRIC", 1.0
sc.view_settings.view_transform = "AgX"
sc.view_settings.look = "AgX - Base Contrast"
sc.view_settings.exposure = 0.0
sc.render.image_settings.file_format = "PNG"
sc.render.filepath = "//../deliverables/frames/OFFBRIEF_EP01_"
ee = sc.eevee
ee.taa_render_samples = 16
ee.use_shadows = True
ee.use_raytracing = False
ee.shadow_ray_count = 1
ee.shadow_step_count = 4
sc.render.film_transparent = False

# ------------------------------------------------------------------ architecture
A = "ENV_ARCHITECTURE"
W, D, H = S.ROOM["width"], S.ROOM["depth"], S.ROOM["height"]
CONCRETE = tex_mat("MAT_floor_polished_concrete", "NOISE", (0.42, 0.36, 0.30), (0.56, 0.49, 0.41), 1.6, rough=0.32, bump=0.02)
BRICK = tex_mat("MAT_wall_brick_north", "BRICK", (0.42, 0.18, 0.11), (0.55, 0.52, 0.48), 6.0, rough=0.85, bump=0.15)
PLASTER = tex_mat("MAT_wall_plaster", "NOISE", (0.74, 0.71, 0.66), (0.80, 0.77, 0.72), 3.0, rough=0.9, bump=0.03)
CEIL = mat("MAT_ceiling_painted_dark", (0.16, 0.16, 0.17), 0.9)
STEEL_BLACK = mat("MAT_steel_black", (0.025, 0.025, 0.028), 0.45, 0.8)
GLASS = mat("MAT_glass_partition", (0.78, 0.86, 0.86), 0.05, 0.0, alpha=0.12)
DOOR = tex_mat("MAT_door_oak", "WAVE", (0.38, 0.24, 0.13), (0.52, 0.35, 0.2), 4, rough=0.5, bump=0.05,
               extra=(0.3, 0.7))
DUCT = mat("MAT_duct_galvanized", (0.55, 0.56, 0.57), 0.35, 0.9)

# floor runs under the glass partition into the bullpen
box("ARCH_Floor_Concrete", (W + 7.0, D, 0.1), (-3.5, 0, -0.05), CONCRETE, A)
box("ARCH_Ceiling", (W + 7.0, D, 0.1), (-3.5, 0, H + 0.05), CEIL, A)
box("ARCH_Wall_North_Brick", (W, 0.2, H), (0, D / 2 + 0.1, H / 2), BRICK, A)
box("ARCH_Wall_South_Plaster", (W, 0.2, H), (0, -D / 2 - 0.1, H / 2), PLASTER, A)
box("ARCH_Bullpen_Wall_North", (7.0, 0.2, H), (-W / 2 - 3.5, D / 2 + 0.1, H / 2), BRICK, A)
box("ARCH_Bullpen_Wall_South", (7.0, 0.2, H), (-W / 2 - 3.5, -D / 2 - 0.1, H / 2), PLASTER, A)
box("ARCH_Bullpen_Wall_West", (0.2, D, H), (-W / 2 - 7.1, 0, H / 2), BRICK, A)

# east window wall: sill, header and piers around three black-framed industrial windows
EX = W / 2 + 0.1
SILL, HEAD = 0.85, 2.95
WINDOWS = [(-3.0, -1.2), (-0.9, 0.9), (1.2, 3.0)]
box("ARCH_Wall_East_Sill", (0.2, D, SILL), (EX, 0, SILL / 2), PLASTER, A)
box("ARCH_Wall_East_Header", (0.2, D, H - HEAD), (EX, 0, (H + HEAD) / 2), PLASTER, A)
edges = [-D / 2] + [v for w in WINDOWS for v in w] + [D / 2]
for i in range(0, len(edges), 2):
    y0, y1 = edges[i], edges[i + 1]
    box(f"ARCH_Wall_East_Pier_{i // 2 + 1}", (0.2, y1 - y0, HEAD - SILL), (EX, (y0 + y1) / 2, (SILL + HEAD) / 2), PLASTER, A)
for wi, (y0, y1) in enumerate(WINDOWS, 1):
    for k in range(4):
        y = y0 + (y1 - y0) * k / 3
        box(f"ARCH_Window_{wi}_Mullion_{k}", (0.06, 0.05, HEAD - SILL), (W / 2 + 0.02, y, (SILL + HEAD) / 2), STEEL_BLACK, A)
    for k, z in enumerate((SILL, 1.75, 2.35, HEAD)):
        box(f"ARCH_Window_{wi}_Transom_{k}", (0.06, y1 - y0, 0.05), (W / 2 + 0.02, (y0 + y1) / 2, z), STEEL_BLACK, A)
# exterior: hazy daylight backdrop and Brooklyn rooftops seen through the windows
SKY = mat("MAT_exterior_sky_daylight", (0.80, 0.86, 0.92), 1.0, emit=2.2)
box("ARCH_Exterior_Sky", (0.05, 30, 12), (16, 0, 4), SKY, A)
BLDG = [mat(f"MAT_exterior_building_{i}", c, 0.9, emit=e) for i, (c, e) in
        enumerate((((0.55, 0.38, 0.30), 0.9), ((0.62, 0.55, 0.48), 0.9), ((0.42, 0.30, 0.26), 0.8)))]
for i in range(9):
    y = -9 + i * 2.2 + rnd.uniform(-0.3, 0.3)
    h = rnd.uniform(1.0, 5.5)
    box(f"ARCH_Exterior_Building_{i}", (2.5, rnd.uniform(1.6, 2.4), h), (rnd.uniform(9, 13), y, h / 2 - 1.5), BLDG[i % 3], A)

# west glass partition with a single oak door in the southwest
PX = -W / 2
DOOR_Y = (-3.25, -2.3)
posts = [-D / 2, -3.3, DOOR_Y[1], -1.2, 0.0, 1.2, 2.4, D / 2]
for i, y in enumerate(posts):
    box(f"ARCH_Partition_Post_{i}", (0.06, 0.06, H), (PX, y, H / 2), STEEL_BLACK, A)
box("ARCH_Partition_Head", (0.08, D, 0.06), (PX, 0, 2.4), STEEL_BLACK, A)
box("ARCH_Partition_Base", (0.08, D, 0.05), (PX, 0, 0.025), STEEL_BLACK, A)
for i in range(2, len(posts) - 1):
    y0, y1 = posts[i], posts[i + 1]
    box(f"ARCH_Partition_Glass_{i - 1}", (0.012, y1 - y0 - 0.06, 2.33), (PX, (y0 + y1) / 2, 1.215), GLASS, A)
    box(f"ARCH_Partition_GlassTransom_{i - 1}", (0.012, y1 - y0 - 0.06, H - 2.45), (PX, (y0 + y1) / 2, (H + 2.45) / 2), GLASS, A)
box("ARCH_Partition_Glass_SW_Transom", (0.012, 0.18, H), (PX, -3.4, H / 2), GLASS, A)
box("ARCH_Door_Bullpen_SW", (0.045, DOOR_Y[1] - DOOR_Y[0] - 0.04, 2.36), (PX, sum(DOOR_Y) / 2, 1.2), DOOR, A)
box("ARCH_Door_Frame_Head", (0.08, DOOR_Y[1] - DOOR_Y[0], 0.06), (PX, sum(DOOR_Y) / 2, 2.4), STEEL_BLACK, A)
box("ARCH_Door_Frame_Glass_Over", (0.012, DOOR_Y[1] - DOOR_Y[0] - 0.06, H - 2.45), (PX, sum(DOOR_Y) / 2, (H + 2.45) / 2), GLASS, A)
cyl("ARCH_Door_Handle", 0.012, 0.16, (PX + 0.04, DOOR_Y[1] - 0.12, 1.05), STEEL_BLACK, A)

# exposed ceiling: steel I-beams E-W, a galvanised duct N-S
for i, y in enumerate((-2.6, -0.9, 0.8, 2.5)):
    box(f"ARCH_Ceiling_Beam_{i + 1}_Web", (W + 7.0, 0.02, 0.34), (-3.5, y, H - 0.17), STEEL_BLACK, A)
    box(f"ARCH_Ceiling_Beam_{i + 1}_Flange", (W + 7.0, 0.18, 0.025), (-3.5, y, H - 0.34), STEEL_BLACK, A)
cyl("ARCH_Ceiling_Duct", 0.22, D, (-2.4, 0, H - 0.62), DUCT, A, rot=(math.radians(90), 0, 0), verts=32)

# bullpen hints beyond the glass (low detail, out of focus)
DESK = mat("MAT_bullpen_desk_white", (0.78, 0.76, 0.72), 0.6)
for i, (x, y) in enumerate([(-6.0, -1.8), (-6.0, 0.6), (-8.4, -1.8), (-8.4, 0.6)]):
    box(f"ARCH_Bullpen_Desk_{i + 1}", (1.5, 0.8, 0.04), (x, y, 0.74), DESK, A)
    box(f"ARCH_Bullpen_Desk_{i + 1}_Leg", (1.4, 0.05, 0.72), (x, y - 0.3, 0.36), STEEL_BLACK, A)
    box(f"ARCH_Bullpen_Monitor_{i + 1}", (0.05, 0.6, 0.36), (x + 0.3, y, 1.0), STEEL_BLACK, A)

# ------------------------------------------------------------------ furniture
F = "ENV_FURNITURE"
WALNUT = tex_mat("MAT_table_walnut", "WAVE", (0.20, 0.11, 0.06), (0.32, 0.19, 0.10), 3.0, rough=0.35, bump=0.04,
                 extra=(0.25, 0.75))
T = S.TABLE
tx, ty = T["center"][0], T["center"][1]
box("FURN_Table_Top", (T["width_x"], T["length_y"], 0.04), (tx, ty, T["top_z"] - 0.02), WALNUT, F, bevel=0.006)
for i, (lx, ly) in enumerate(T["legs"]):
    box(f"FURN_Table_Leg_{i + 1}", (0.06, 0.06, T["top_z"] - 0.04), (lx, ly, (T["top_z"] - 0.04) / 2), STEEL_BLACK, F)
box("FURN_Table_Rail_N_S", (0.05, T["legs"][1][1] - T["legs"][0][1], 0.05), (tx, (T["legs"][0][1] + T["legs"][1][1]) / 2, 0.15),
    STEEL_BLACK, F)
CHAIR_FAB = mat("MAT_chair_fabric_charcoal", (0.07, 0.07, 0.075), 0.85)
CHAIR_MET = mat("MAT_chair_aluminium", (0.6, 0.6, 0.62), 0.3, 1.0)


def chair(cid, x, y, face_deg, seat_top=S.SEAT_TOP):
    f = Vector((math.cos(math.radians(face_deg)), math.sin(math.radians(face_deg)), 0))
    c = Vector((x, y, 0)) - f * 0.03
    rz = math.radians(face_deg) - math.pi / 2
    nm = f"FURN_Chair_{cid}"
    parts = [box(nm + "_Seat", (0.48, 0.47, 0.07), (0, 0, seat_top - 0.035), CHAIR_FAB, F, bevel=0.02),
             box(nm + "_Back", (0.46, 0.06, 0.5), (0, -0.29, seat_top + 0.36), CHAIR_FAB, F, rot=(math.radians(-10), 0, 0), bevel=0.02),
             box(nm + "_BackStrut", (0.05, 0.03, 0.3), (0, -0.27, seat_top + 0.05), CHAIR_MET, F, rot=(math.radians(-20), 0, 0)),
             cyl(nm + "_Post", 0.028, seat_top - 0.17, (0, 0, (seat_top - 0.07 + 0.10) / 2), CHAIR_MET, F)]
    for k in range(5):
        a = k * 2 * math.pi / 5
        e = Vector((math.cos(a), math.sin(a), 0)) * 0.3
        parts.append(cyl_between(f"{nm}_Base_{k}", (0, 0, 0.09), (e.x, e.y, 0.06), 0.018, CHAIR_MET, F, 8))
        parts.append(ell(f"{nm}_Caster_{k}", (0.05, 0.05, 0.05), (e.x, e.y, 0.03), STEEL_BLACK, F, 8))
    root = empty(nm, F, size=0.3, shape="PLAIN_AXES")
    for p in parts:
        p.parent = root
    root.location, root.rotation_euler.z = c, rz
    return root


for cid, cdat in S.CAST.items():
    chair(cid, *cdat["pos"], cdat["face"])

CRED = tex_mat("MAT_credenza_oak", "WAVE", (0.45, 0.30, 0.17), (0.56, 0.40, 0.24), 4.0, rough=0.45, bump=0.03, extra=(0.3, 0.7))
box("FURN_Credenza_North", (2.4, 0.45, 0.62), (0, D / 2 - 0.25, 0.31), CRED, F, bevel=0.01)

# presentation monitor on the north wall, display facing south
MON = S.MONITOR
box("FURN_Monitor_Bezel", (MON["width"] + 0.06, 0.05, MON["height"] + 0.06), (MON["center"][0], MON["center"][1] + 0.03, MON["center"][2]),
    STEEL_BLACK, F, bevel=0.004)
bpy.ops.mesh.primitive_plane_add(size=1, location=MON["center"], rotation=(math.radians(90), 0, 0))
scr = bpy.context.object
scr.name = "FURN_Monitor_Display"
scr.scale = (MON["width"], MON["height"], 1)
bpy.ops.object.transform_apply(scale=True)
scr.rotation_euler = (math.radians(90), 0, math.radians(180))   # normal -> -Y (south); image reads left-to-right from the room
scr.location.y -= 0.002
scr.data.materials.append(emission_image("MAT_monitor_burger_slide", os.path.join(ROOT, "textures", "burger_slide.png"), 1.6))
link(scr, F)
box("FURN_Monitor_WallMount", (0.4, 0.06, 0.3), (MON["center"][0], MON["center"][1] + 0.08, MON["center"][2]), STEEL_BLACK, F)

PLANT_POT = mat("MAT_planter_terracotta", (0.45, 0.22, 0.13), 0.8)
LEAF = mat("MAT_plant_leaf", (0.10, 0.25, 0.08), 0.6, sss=0.2)
cyl("FURN_Planter_NE", 0.22, 0.5, (3.9, 2.9, 0.25), PLANT_POT, F)
for i in range(14):
    a = rnd.uniform(0, 2 * math.pi)
    r = rnd.uniform(0.05, 0.3)
    ell(f"FURN_Plant_NE_Leaf_{i}", (0.28, 0.12, 0.05), (3.9 + r * math.cos(a), 2.9 + r * math.sin(a), rnd.uniform(0.7, 1.5)), LEAF, F, 8
        ).rotation_euler = (rnd.uniform(-0.6, 0.6), rnd.uniform(-0.6, 0.6), a)

# ------------------------------------------------------------------ table props
P = "ENV_PROPS"
ALU = mat("MAT_laptop_aluminium", (0.62, 0.62, 0.64), 0.35, 1.0)
LAP_SCREEN = mat("MAT_laptop_screen_glow", (0.55, 0.62, 0.75), 0.2, emit=0.6)
MUG = [mat("MAT_mug_white", (0.85, 0.84, 0.8), 0.3), mat("MAT_mug_black", (0.05, 0.05, 0.05), 0.3),
       mat("MAT_mug_mustard", (0.75, 0.55, 0.12), 0.35)]
COFFEE = mat("MAT_coffee", (0.08, 0.04, 0.02), 0.1)
PAPER = mat("MAT_paper", (0.88, 0.87, 0.84), 0.8)
NOTE = [mat("MAT_notebook_black", (0.04, 0.04, 0.04), 0.6), mat("MAT_notebook_kraft", (0.55, 0.42, 0.27), 0.8)]
PEN = mat("MAT_pen_blue", (0.05, 0.08, 0.3), 0.3)
BOTTLE = mat("MAT_water_bottle", (0.55, 0.70, 0.80), 0.05, alpha=0.35)
CAP = mat("MAT_bottle_cap", (0.1, 0.3, 0.7), 0.4)
CABLE = mat("MAT_cable_white", (0.82, 0.82, 0.8), 0.4)
TOP = T["top_z"]


def laptop(name, x, y, yaw_deg):
    root = empty(name, P, size=0.15, shape="PLAIN_AXES")
    b = box(name + "_Base", (0.31, 0.22, 0.014), (0, 0, 0.007), ALU, P, bevel=0.003)
    s = box(name + "_Lid", (0.31, 0.008, 0.21), (0, 0.11 + 0.02, 0.105), ALU, P, rot=(math.radians(-15), 0, 0))
    g = box(name + "_Screen", (0.29, 0.002, 0.19), (0, 0.11 + 0.012, 0.105), LAP_SCREEN, P, rot=(math.radians(-15), 0, 0))
    for o in (b, s, g):
        o.parent = root
    root.location, root.rotation_euler.z = (x, y, TOP), math.radians(yaw_deg)
    return root


def mug(name, x, y, m):
    root = empty(name, P, size=0.06, shape="PLAIN_AXES")
    a = cyl(name + "_Body", 0.04, 0.095, (0, 0, 0.0475), m, P)
    c = cyl(name + "_Coffee", 0.036, 0.002, (0, 0, 0.085), COFFEE, P)
    h = torus(name + "_Handle", 0.025, 0.007, (0.045, 0, 0.05), m, P, rot=(math.radians(90), 0, 0))
    for o in (a, c, h):
        o.parent = root
    root.location = (x, y, TOP)
    root.rotation_euler.z = rnd.uniform(0, 6.28)
    return root


laptop("PROP_Laptop_Jason", -0.30, 0.50, -90)
laptop("PROP_Laptop_Lucia", -0.30, -1.02, -90)
laptop("PROP_Laptop_BaeLuxe", 0.10, -1.70, 180 + 25)
for i, (x, y, m) in enumerate([(-0.48, 0.05, 0), (0.44, 0.05, 1), (0.42, -1.62, 2), (-0.46, -1.52, 1), (-0.25, -1.90, 0)]):
    mug(f"PROP_Mug_{i + 1}", x, y, MUG[m])
for i, (x, y, yaw, m) in enumerate([(0.36, -0.62, 12, 0), (-0.42, -0.55, -8, 1), (0.30, 1.05, 4, 1)]):
    box(f"PROP_Notebook_{i + 1}", (0.15, 0.21, 0.012), (x, y, TOP + 0.006), NOTE[m], P, rot=(0, 0, math.radians(yaw)), bevel=0.002)
    cyl(f"PROP_Pen_{i + 1}", 0.004, 0.14, (x + 0.05, y, TOP + 0.016), PEN, P, rot=(math.radians(90), 0, math.radians(yaw + 8)), verts=8)
for i, (x, y, yaw) in enumerate([(0.12, -0.25, 20), (0.18, -0.32, 34), (-0.10, 1.10, -10), (0.30, -1.30, 75)]):
    box(f"PROP_ProductionNotes_{i + 1}", (0.21, 0.297, 0.0008), (x, y, TOP + 0.0004 + i * 0.0006), PAPER, P,
        rot=(0, 0, math.radians(yaw)))
box("PROP_Presentation_Remote", (0.04, 0.12, 0.016), (-0.45, 0.92, TOP + 0.008), STEEL_BLACK, P, rot=(0, 0, 0.3), bevel=0.004)
box("PROP_Phone_BaeLuxe", (0.075, 0.155, 0.009), (0.30, -1.92, TOP + 0.0045), STEEL_BLACK, P, rot=(0, 0, 0.5), bevel=0.003)
cyl("PROP_Water_Bottle", 0.034, 0.21, (0.42, 1.18, TOP + 0.105), BOTTLE, P)
cyl("PROP_Water_Bottle_Cap", 0.02, 0.025, (0.42, 1.18, TOP + 0.222), CAP, P)
box("PROP_Table_PowerHub", (0.16, 0.08, 0.03), (0.0, -0.3, TOP + 0.015), STEEL_BLACK, P, bevel=0.005)
for i, (sx, sy) in enumerate([(-0.15, 0.50), (-0.15, -1.02), (0.05, -1.58)]):
    cu = bpy.data.curves.new(f"PROP_Cable_{i + 1}", "CURVE")
    cu.dimensions, cu.bevel_depth, cu.bevel_resolution = "3D", 0.003, 2
    sp = cu.splines.new("BEZIER")
    sp.bezier_points.add(2)
    pts = [(sx, sy, TOP + 0.003), ((sx + 0.0) / 2 + rnd.uniform(-0.08, 0.08), (sy - 0.3) / 2, TOP + 0.003), (0.0, -0.3, TOP + 0.01)]
    for bp, p in zip(sp.bezier_points, pts):
        bp.co = p
        bp.handle_left_type = bp.handle_right_type = "AUTO"
    o = bpy.data.objects.new(f"PROP_Cable_{i + 1}", cu)
    o.data.materials.append(CABLE)
    COLL[P].objects.link(o)

# ------------------------------------------------------------------ cast rigs
CR = "CAST_RIGS"


def attach(o, arm, bone):
    b = arm.data.bones[bone]
    pw = arm.matrix_world @ b.matrix_local @ Matrix.Translation((0, b.length, 0))
    w = o.matrix_world.copy()
    o.parent, o.parent_type, o.parent_bone = arm, "BONE", bone
    o.matrix_parent_inverse = pw.inverted()
    o.matrix_basis = w


RIGS, LOOK, EYES, IKT, EYE_OBJS, DIMS = {}, {}, {}, {}, {}, {}

GOLD = mat("MAT_gold_jewellery", (0.95, 0.70, 0.30), 0.25, 1.0)


def wardrobe(cid, c, add, hc, Hs, G, zh, hair, sk):
    V = Vector
    st = c["style"]
    h = st["hair"]
    rr = random.Random(cid)
    if h in ("short", "curly_pony", "long_curly", "bun"):
        add("hair_cap", "ell", (0.172 * Hs, 0.214 * Hs, 0.14 * Hs), hc + V((0, -0.012 * Hs, 0.062 * Hs)), hair, "head")
        add("hair_back", "ell", (0.165 * Hs, 0.12 * Hs, 0.17 * Hs), hc + V((0, -0.05 * Hs, 0.0)), hair, "head")
    if st.get("stubble"):
        add("stubble", "ell", (0.152 * Hs, 0.17 * Hs, 0.12 * Hs), hc + V((0, 0.02 * Hs, -0.062 * Hs)),
            mat(f"MAT_{cid}_stubble", tuple(x * 0.55 for x in c["skin"]), 0.9), "head")
    if st.get("beard"):
        add("beard", "ell", (0.16 * Hs, 0.16 * Hs, 0.15 * Hs), hc + V((0, 0.036 * Hs, -0.08 * Hs)),
            mat(f"MAT_{cid}_beard", st["beard"], 0.9), "head")
    if h == "cap":
        capm = mat(f"MAT_{cid}_cap", (0.20, 0.13, 0.08), 0.8)
        add("hair_sides", "ell", (0.172 * Hs, 0.19 * Hs, 0.13 * Hs), hc + V((0, -0.025 * Hs, 0.0)), hair, "head")
        add("cap_crown", "ell", (0.176 * Hs, 0.218 * Hs, 0.14 * Hs), hc + V((0, -0.006 * Hs, 0.072 * Hs)), capm, "head")
        add("cap_brim", "box", (0.16 * Hs, 0.11 * Hs, 0.012), hc + V((0, 0.13 * Hs, 0.085 * Hs)), capm, "head",
            rot=(math.radians(-8), 0, 0))
        add("cap_sunglasses", "box", (0.13 * Hs, 0.03, 0.035), hc + V((0, 0.07 * Hs, 0.135 * Hs)),
            mat("MAT_sunglasses_dark", (0.02, 0.02, 0.02), 0.1, 0.5), "head")
    if h == "curly_pony":
        for i in range(10):
            t = i / 9
            r = (0.05 - 0.018 * t) * Hs
            add(f"pony_{i}", "ell", (2 * r,) * 3, hc + V((rr.uniform(-0.01, 0.01), (-0.09 - 0.05 * t) * Hs, (0.12 - 0.2 * t) * Hs)),
                hair, "head", seg=8)
        for k in (-1, 1):
            add(f"temple_curl_{k}", "ell", (0.04 * Hs,) * 3, hc + V((k * 0.075 * Hs, 0.03 * Hs, -0.02 * Hs)), hair, "head", seg=8)
    if h == "long_curly":
        for i in range(44):
            a = rr.uniform(math.radians(-200), math.radians(20))        # around the back and sides, never the face
            zz = rr.uniform(-0.30, 0.10) * Hs
            rad = (0.095 + 0.03 * (0.1 - zz)) * Hs
            p = hc + V((math.cos(a) * rad, math.sin(a) * rad * 0.9 - 0.02 * Hs, zz))
            if p.y - hc.y > 0.02 * Hs and abs(p.x) < 0.09 * Hs:
                continue
            r = rr.uniform(0.07, 0.095) * Hs
            add(f"curl_{i:02d}", "ell", (r, r, r), p, hair, "head", seg=8)
    if h == "bun":
        add("bun", "ell", (0.12 * Hs, 0.12 * Hs, 0.11 * Hs), hc + V((0, -0.06 * Hs, 0.15 * Hs)), hair, "head", seg=12)
        for i in range(6):
            k = -1 if i % 2 else 1
            add(f"loose_strand_{i}", "ell", (0.03 * Hs, 0.03 * Hs, 0.07 * Hs),
                hc + V((k * 0.078 * Hs, (0.02 - 0.02 * i) * Hs, (0.0 - 0.01 * i) * Hs)), hair, "head", seg=8)
    if st.get("hoops"):
        for k in (-1, 1):
            add(f"hoop_{k}", "torus", (0.02 * Hs, 0.0028, (1, 1, 1)), hc + V((k * 0.088 * Hs, 0.0, -0.065 * Hs)), GOLD,
                "head", rot=(0, math.radians(90), 0))
    if st.get("aviators"):
        lens = mat("MAT_aviator_lens_amber", (0.35, 0.20, 0.05), 0.05, 0.6)
        for k in (-1, 1):
            add(f"aviator_lens_{k}", "ell", (0.052 * Hs, 0.012, 0.044 * Hs), hc + V((k * 0.035 * Hs, 0.118 * Hs, 0.014 * Hs)),
                lens, "glasses", seg=12)
            add(f"aviator_arm_{k}", "box", (0.006, 0.11 * Hs, 0.006), hc + V((k * 0.08 * Hs, 0.07 * Hs, 0.03 * Hs)), GOLD, "glasses")
        add("aviator_bridge", "box", (0.07 * Hs, 0.006, 0.006), hc + V((0, 0.122 * Hs, 0.036 * Hs)), GOLD, "glasses")
    if st.get("chains"):
        for i in range(2 if h == "bald" else 1):
            add(f"chain_{i}", "torus", (0.085 * G + 0.02 * i, 0.005, (1.0, 1.15, 1.0)),
                V((0, 0.03 * G + 0.012 * i, zh + (0.445 - 0.03 * i) * Hs)), GOLD, "chest", rot=(math.radians(-25), 0, 0))



def build_actor(cid, c):
    Hs, G, B = c["H"], c["G"], c.get("belly", 1.0)
    zh = S.SEAT_TOP + 0.075 * G + 0.004          # hip joint: thigh rests on the seat
    sw = 0.185 * G
    sh_z = zh + 0.44 * Hs
    hc = Vector((0, 0.012 * Hs, zh + 0.64 * Hs))  # head centre
    DIMS[cid] = dict(zh=zh, sw=sw, shoulder_z=sh_z, head_c=hc)
    ad = bpy.data.armatures.new(cid + "_RIG")
    arm = bpy.data.objects.new(cid + "_RIG", ad)
    COLL[CR].objects.link(arm)
    for o in bpy.context.selected_objects:
        o.select_set(False)
    bpy.context.view_layer.objects.active = arm
    arm.select_set(True)
    bones = {"root": ((0, 0, 0), (0, 0.15, 0), None),
             "pelvis": ((0, 0, zh), (0, 0, zh + 0.12 * Hs), "root"),
             "spine": ((0, 0, zh + 0.12 * Hs), (0, 0, zh + 0.28 * Hs), "pelvis"),
             "chest": ((0, 0, zh + 0.28 * Hs), (0, 0, zh + 0.46 * Hs), "spine"),
             "neck": ((0, 0, zh + 0.46 * Hs), (0, 0, zh + 0.56 * Hs), "chest"),
             "head": (tuple(hc), tuple(hc + Vector((0, 0.12, 0))), "neck"),
             "eyes": (tuple(hc + Vector((0, 0.05 * Hs, 0.015 * Hs))), tuple(hc + Vector((0, 0.12, 0.015 * Hs))), "head"),
             "glasses": (tuple(hc + Vector((0, 0.05 * Hs, 0.0))), tuple(hc + Vector((0, 0.12, 0.0))), "head")}
    for side, k in (("L", -1), ("R", 1)):        # actor faces +Y: their right is +X
        s0 = Vector((k * sw, 0, sh_z))
        e0 = s0 + Vector((k * 0.01, 0.01, -0.29 * Hs))
        w0 = e0 + Vector((0, 0.02, -0.26 * Hs))
        bones[f"upper_arm.{side}"] = (tuple(s0), tuple(e0), "chest")
        bones[f"forearm.{side}"] = (tuple(e0), tuple(w0), f"upper_arm.{side}")
        bones[f"hand.{side}"] = (tuple(w0), tuple(w0 + Vector((0, 0, -0.09 * Hs))), f"forearm.{side}")
    bpy.ops.object.mode_set(mode="EDIT")
    for n, (h, t, p) in bones.items():
        eb = ad.edit_bones.new(n)
        eb.head, eb.tail, eb.roll = h, t, 0.0
        if p:
            eb.parent = ad.edit_bones[p]
            eb.use_connect = n.startswith("forearm") or n.startswith("hand")
    bpy.ops.object.mode_set(mode="OBJECT")
    ad.display_type = "STICK"
    for pb in arm.pose.bones:
        pb.rotation_mode = "XYZ"

    def add(name, kind, size, loc, m, bone, rot=None, seg=16):
        nm = f"{cid}_{name}"
        if kind == "box":
            o = box(nm, size, loc, m, CR, bevel=min(size) * 0.3)
        elif kind == "ell":
            o = ell(nm, size, loc, m, CR, seg)
        elif kind == "cyl":
            o = cyl_between(nm, size[0], size[1], size[2], m, CR)
        elif kind == "torus":
            o = torus(nm, size[0], size[1], loc, m, CR, rot=rot or (0, 0, 0), scale=size[2])
        if rot and kind != "torus":
            o.rotation_euler = rot
        attach(o, arm, bone)
        return o

    sk = mat(f"MAT_{cid}_skin", c["skin"], 0.55, sss=0.15)
    pat = c["style"].get("pattern")
    if pat == "floral":
        shirt = tex_mat(f"MAT_{cid}_shirt_floral", "VORONOI", (0.86, 0.46, 0.22), c["shirt"], 38, 0.8, 0.0, extra=(0.08, 0.16))
    elif pat == "gold_paisley":
        shirt = tex_mat(f"MAT_{cid}_shirt_gold_print", "WAVE", c["shirt"], (0.80, 0.58, 0.18), 9, 0.6, 0.0, extra=(0.6, 0.68))
    else:
        shirt = mat(f"MAT_{cid}_top", c["shirt"], 0.8)
    sleeve = mat(f"MAT_{cid}_varsity_sleeve", (0.93, 0.86, 0.88), 0.8) if pat == "varsity" else shirt
    pants = mat(f"MAT_{cid}_trousers", c["pants"], 0.8)
    shoe = mat(f"MAT_{cid}_shoes", c.get("shoe", (0.05, 0.04, 0.035)), 0.5)
    hair = mat(f"MAT_{cid}_hair", c["hair"], 0.7)
    eye = mat("MAT_proxy_eye", (0.02, 0.018, 0.016), 0.2)
    # legs: static, seated, feet flat on the floor
    for side, k in (("L", -1), ("R", 1)):
        hip = Vector((k * 0.1 * G, -0.02, zh))
        knee = Vector((k * 0.1 * G, 0.45 * Hs, zh + 0.01))
        ankle = Vector((k * 0.1 * G, 0.48 * Hs, 0.09))
        add(f"thigh.{side}", "cyl", (hip, knee, 0.075 * G), None, pants, "root")
        add(f"knee.{side}", "ell", (0.13 * G, 0.13 * G, 0.13 * G), knee, pants, "root", seg=12)
        add(f"shin.{side}", "cyl", (knee, ankle, 0.055 * G), None, pants, "root")
        add(f"shoe.{side}", "box", (0.1, 0.27, 0.085), (k * 0.1 * G, 0.53 * Hs, 0.0475), shoe, "root")
    add("hips", "ell", (0.38 * G, 0.30 * G, 0.2), (0, -0.03, zh + 0.03), pants, "pelvis")
    add("belt", "cyl", ((0, -0.03, zh + 0.10 * Hs), (0, -0.03, zh + 0.13 * Hs), 0.17 * G), None,
        mat("MAT_belt_black", (0.03, 0.03, 0.03), 0.4), "pelvis")
    add("abdomen", "ell", (0.35 * G, 0.25 * G * B, 0.26 * Hs), (0, 0.01 * B, zh + 0.21 * Hs), shirt, "spine")
    add("chest", "ell", (0.42 * G, 0.25 * G, 0.27 * Hs), (0, 0.0, zh + 0.36 * Hs), shirt, "chest")
    add("neck", "cyl", ((0, 0, zh + 0.44 * Hs), (0, 0.005, zh + 0.57 * Hs), 0.052 * G ** 0.5), None, sk, "neck")
    add("head", "ell", (0.16 * Hs, 0.205 * Hs, 0.235 * Hs), hc, sk, "head", seg=24)
    for k in (-1, 1):
        sd = "L" if k < 0 else "R"
        e = add(f"eye.{sd}", "ell", (0.024 * Hs, 0.012 * Hs, 0.013 * Hs), hc + Vector((k * 0.034 * Hs, 0.093 * Hs, 0.016 * Hs)),
                eye, "eyes", seg=10)
        EYE_OBJS.setdefault(cid, []).append(e)
        add(f"ear.{sd}", "ell", (0.02 * Hs, 0.04 * Hs, 0.06 * Hs), hc + Vector((k * 0.08 * Hs, 0.0, 0.0)), sk, "head", seg=10)
    for side, k in (("L", -1), ("R", 1)):
        b_u, b_f, b_h = (arm.data.bones[f"{n}.{side}"] for n in ("upper_arm", "forearm", "hand"))
        add(f"shoulder.{side}", "ell", (0.13 * G, 0.13 * G, 0.12 * G), b_u.head_local, sleeve, f"upper_arm.{side}")
        add(f"upper_arm.{side}", "cyl", (b_u.head_local, b_u.tail_local, 0.052 * G), None,
            sleeve, f"upper_arm.{side}")
        add(f"elbow.{side}", "ell", (0.09 * G,) * 3, b_f.head_local,
            sleeve if c["sleeves"] == "long" else sk, f"forearm.{side}", seg=10)
        add(f"forearm.{side}", "cyl", (b_f.head_local, b_f.tail_local, 0.042 * G), None,
            sleeve if c["sleeves"] == "long" else sk, f"forearm.{side}")
        add(f"hand.{side}", "box", (0.07, 0.03, 0.095 * Hs), (b_h.head_local + b_h.tail_local) / 2, sk, f"hand.{side}")
    wardrobe(cid, c, add, hc, Hs, G, zh, hair, sk)

    # IK hands (targets/poles parented to the rig object, keyed in actor-local metres)
    IKT[cid] = {}
    for side, k in (("L", -1), ("R", 1)):
        t = empty(f"{cid}_IK_hand.{side}", "ANIMATION", size=0.05, shape="CUBE")
        t.parent = arm
        t.location = c["rest"][side]
        p = empty(f"{cid}_POLE_elbow.{side}", "ANIMATION", size=0.03)
        p.parent = arm
        p.location = (k * 0.6 * G, -0.35, sh_z - 0.25)
        pb = arm.pose.bones[f"forearm.{side}"]
        ik = pb.constraints.new("IK")
        ik.target, ik.pole_target, ik.chain_count, ik.use_tail = t, p, 2, True
        ik.pole_angle = math.radians(-90 if k > 0 else -90)
        IKT[cid][side] = t
    # gaze: head partially, eyes fully, tracked to LOOK / EYES empties
    lk = empty(f"{cid}_LOOK", "ANIMATION", size=0.06)
    ey = empty(f"{cid}_EYES", "ANIMATION", size=0.03)
    ey.parent = lk
    dt = arm.pose.bones["head"].constraints.new("DAMPED_TRACK")
    dt.target, dt.track_axis, dt.influence = lk, "TRACK_Y", c.get("head_follow", 0.85)
    de = arm.pose.bones["eyes"].constraints.new("DAMPED_TRACK")
    de.target, de.track_axis = ey, "TRACK_Y"
    LOOK[cid], EYES[cid] = lk, ey
    # place the actor
    x, y = c["pos"]
    arm.location = (x, y, 0)
    arm.rotation_euler.z = math.radians(c["face"]) - math.pi / 2
    RIGS[cid] = arm
    # viewport-only proxy label
    cu = bpy.data.curves.new(f"{cid}_LABEL", "FONT")
    cu.body = f"{cid}  (PROXY)\n{c['role']}"
    cu.size, cu.align_x = 0.09, "CENTER"
    lb = bpy.data.objects.new(f"{cid}_LABEL", cu)
    COLL[CR].objects.link(lb)
    lb.parent = arm
    lb.location = (0, 0, zh + 1.0)
    lb.rotation_euler.x = math.radians(90)
    lb.hide_render = True
    return arm


for cid, c in S.CAST.items():
    build_actor(cid, c)
bpy.context.view_layer.update()

# ------------------------------------------------------------------ gaze targets and animation
SCREEN = Vector(S.MONITOR["center"]) + Vector((0, -0.05, 0))


def head_world(cid):
    arm = RIGS[cid]
    return arm.matrix_world @ (DIMS[cid]["head_c"] + Vector((0, 0.05, 0)))


def local_to_world(cid, v):
    return RIGS[cid].matrix_world @ Vector(v)


def target_pos(cid, tgt):
    if tgt == "SCREEN":
        return SCREEN.copy()
    if tgt.startswith("LOCAL:"):
        return local_to_world(cid, [float(v) for v in tgt[6:].split(",")])
    return head_world(tgt) + Vector((0, 0, -0.03))


def set_key_loc(obj, frame, loc):
    obj.location = loc
    obj.keyframe_insert("location", frame=frame)


for cid, sched in S.LOOKS.items():
    lk, ey = LOOK[cid], EYES[cid]
    me = head_world(cid)
    events = []          # (frame, look_pos, eye_offset)
    prev = None
    for ev in sched:
        f, tgt = ev[0], ev[1]
        dur = ev[2] if len(ev) > 2 else 8
        frac = ev[3] if len(ev) > 3 else 1.0      # <1: head turns only part-way, eyes go all the way
        full = target_pos(cid, tgt)
        look = me + (full - me) * frac if frac < 1 else full
        eye_off = full - look
        if prev is None:
            events.append((f, look, eye_off))
        else:
            events.append((f, prev[0], prev[1]))
            events.append((f + dur, look, eye_off))
        prev = (look, eye_off)
    # talk beats: small nods on the speaker's look target during their lines
    beats = []
    for sh in S.SHOTS:
        for (who, line, a, b) in sh["dialogue"]:
            if who != cid:
                continue
            fr = a + 4
            sgn = 1
            while fr < b - 2:
                beats.append((fr, sgn))
                sgn = -sgn
                fr += rnd.randint(9, 13)
    keyed = sorted(events, key=lambda e: e[0])
    frames_busy = set()
    for i in range(1, len(keyed)):
        if (keyed[i][1] - keyed[i - 1][1]).length > 1e-4:
            frames_busy.update(range(keyed[i - 1][0], keyed[i][0] + 1))

    def hold_at(fr):
        cur = keyed[0]
        for e in keyed:
            if e[0] <= fr:
                cur = e
        return cur

    for fr, sgn in beats:
        if fr in frames_busy:
            continue
        e = hold_at(fr)
        d = (e[1] - me).length
        keyed.append((fr, e[1] + Vector((0, 0, 0.03 * d * sgn)), e[2]))
    keyed.sort(key=lambda e: e[0])
    for fr, lp, eo in keyed:
        set_key_loc(lk, fr, lp)
        set_key_loc(ey, fr, eo)
    # micro saccades on the eyes
    for i in range(3):
        fc = fcurve(ey, "location", i)
        m = fc.modifiers.new("NOISE")
        m.scale, m.strength, m.phase = 16.0, 0.035 * (me - SCREEN).length / 4, rnd.uniform(0, 100)

# blinks: every 2.3-4.6 s, plus one shortly after big head turns
for cid, eyes in EYE_OBJS.items():
    frames = []
    f = rnd.randint(10, 40)
    while f < S.FRAME_END - 6:
        frames.append(f)
        f += rnd.randint(55, 110)
    frames += [ev[0] + 3 for ev in S.LOOKS[cid] if ev[0] > 1 and (len(ev) < 4)][::3]
    frames = sorted(set(frames))
    for e in eyes:
        base = e.scale.z
        for f in frames:
            for df, s in ((0, 1.0), (2, 0.08), (4, 1.0)):
                e.scale.z = base * s
                e.keyframe_insert("scale", frame=f + df, index=2)
        e.scale.z = base

# torso: lean (+ forward) and twist (+ toward actor's left), split spine 55% / chest 45%; breathing and weight shift
for cid, keys in S.TORSO.items():
    arm = RIGS[cid]
    sp, ch = arm.pose.bones["spine"], arm.pose.bones["chest"]
    for f, lean, twist in keys:
        for pb, w in ((sp, 0.55), (ch, 0.45)):
            pb.rotation_euler = (-math.radians(lean) * w, math.radians(twist) * w, 0)
            pb.keyframe_insert("rotation_euler", frame=f)
    fc = fcurve(arm, 'pose.bones["chest"].rotation_euler', 0)
    g = fc.modifiers.new("FNGENERATOR")
    g.function_type, g.use_additive = "SIN", True
    g.amplitude = 0.012
    g.phase_multiplier = 2 * math.pi / (S.FPS * rnd.uniform(3.6, 4.6))
    g.phase_offset = rnd.uniform(0, 6.28)
    for idx in (1, 2):
        fc = fcurve(arm, 'pose.bones["spine"].rotation_euler', idx)
        n = fc.modifiers.new("NOISE")
        n.scale, n.strength, n.phase = 110.0, 0.035, rnd.uniform(0, 100)

# hands: IK target keys in actor-local metres
for cid, sides in S.HANDS.items():
    for side, keys in sides.items():
        t = IKT[cid][side]
        for f, loc in keys:
            set_key_loc(t, f, loc)
    for (side, a, b, strength, scale) in S.HAND_NOISE.get(cid, []):
        t = IKT[cid][side]
        if not t.animation_data:
            set_key_loc(t, 1, t.location.copy())
        for i in range(3):
            fc = fcurve(t, "location", i)
            n = fc.modifiers.new("NOISE")
            n.scale, n.strength, n.phase = scale, strength, rnd.uniform(0, 100)
            n.use_restricted_range = True
            n.frame_start, n.frame_end, n.blend_in, n.blend_out = a, b, 3, 3

# ------------------------------------------------------------------ hand-held props and wardrobe animation
brief_m = PAPER
arm = RIGS["BRIAN_01"]
hb = arm.data.bones["hand.R"]
o = box("BRIAN_01_PROP_Client_Brief", (0.003, 0.21, 0.27), hb.tail_local + Vector((-0.02, 0.06, 0.03)), brief_m, CR)
o.matrix_world = arm.matrix_world @ Matrix.Translation(hb.tail_local + Vector((-0.02, 0.07, 0.02)))
attach(o, arm, "hand.R")
o.name = "PROP_Client_Brief_BRIAN"

arm = RIGS["LORI_01"]
nb = box("PROP_Notebook_LORI", (0.17, 0.24, 0.014), (0, 0, 0), NOTE[0], CR, bevel=0.002)
nb.parent = arm
nb.location = S.LORI_NOTEBOOK["loc"]
nb.rotation_euler = [math.radians(a) for a in S.LORI_NOTEBOOK["rot"]]
pg = box("PROP_Notebook_LORI_Page", (0.155, 0.225, 0.002), (0, 0, 0.008), PAPER, CR)
pg.parent = nb
hb = arm.data.bones["hand.R"]
pen = cyl("PROP_Pen_LORI", 0.0045, 0.14, (0, 0, 0), PEN, CR, verts=8)
pen.matrix_world = arm.matrix_world @ Matrix.Translation(hb.tail_local + Vector((-0.01, 0.0, 0.03)))
attach(pen, arm, "hand.R")

arm = RIGS["BOOBIE_IKE_01"]
pb = arm.pose.bones["glasses"]
for f, loc in S.BOOBIE_GLASSES:
    pb.location = loc
    pb.keyframe_insert("location", frame=f)

# ------------------------------------------------------------------ lighting (consistent for every camera)
L = "LIGHTING"


def light(name, kind, loc, power, col, rot=(0, 0, 0), size=None, size_y=None, radius=None, shadow=True):
    ld = bpy.data.lights.new(name, kind)
    ld.energy, ld.color = power, col
    if kind == "AREA":
        ld.shape = "RECTANGLE"
        ld.size, ld.size_y = size, size_y or size
    if radius is not None:
        ld.shadow_soft_size = radius
    ld.use_shadow = shadow
    o = bpy.data.objects.new(name, ld)
    o.location, o.rotation_euler = loc, rot
    COLL[L].objects.link(o)
    return o


def aim_rot(frm, to, up="Y"):
    return (Vector(to) - Vector(frm)).to_track_quat("-Z", up).to_euler()


DAY = S.K5600
WARM = S.K3200
sun_dir = Vector((-math.cos(math.radians(32)), 0.18, -math.sin(math.radians(32))))
sun = light("LGT_Sun_Daylight_East", "SUN", (8, 0, 6), 3.2, DAY, rot=sun_dir.to_track_quat("-Z", "Y").to_euler())
sun.data.angle = math.radians(2.5)
for i, (y0, y1) in enumerate(WINDOWS, 1):
    light(f"LGT_Window_Fill_{i}", "AREA", (W / 2 - 0.08, (y0 + y1) / 2, (SILL + HEAD) / 2), 260, DAY,
          rot=(0, math.radians(-90), 0), size=y1 - y0, size_y=HEAD - SILL, shadow=True)
PEND_SHADE = mat("MAT_pendant_shade_black", (0.02, 0.02, 0.02), 0.4, 0.6)
PEND_GLOW = mat("MAT_pendant_bulb_glow", (1.0, 0.72, 0.42), 0.3, emit=12)
for i, (x, y) in enumerate(S.PENDANTS, 1):
    z = 2.35
    cyl(f"ARCH_Pendant_{i}_Cord", 0.004, H - z - 0.15, (x, y, (H + z + 0.15) / 2), STEEL_BLACK, A, verts=6)
    bpy.ops.mesh.primitive_cone_add(vertices=32, radius1=0.21, radius2=0.05, depth=0.2, location=(x, y, z))
    shade = bpy.context.object
    shade.name = f"ARCH_Pendant_{i}_Shade"
    shade.data.materials.append(PEND_SHADE)
    sol = shade.modifiers.new("Solidify", "SOLIDIFY")
    sol.thickness = 0.006
    link(shade, A)
    ell(f"ARCH_Pendant_{i}_Bulb", (0.09, 0.09, 0.09), (x, y, z - 0.07), PEND_GLOW, A, 12)
    light(f"LGT_Practical_Pendant_{i}", "SPOT", (x, y, z - 0.1), 55, WARM, rot=(0, 0, 0), radius=0.08).data.spot_size = math.radians(120)
light("LGT_Bounce_Table_Up", "AREA", (0, -0.3, T["top_z"] + 0.02), 22, (1.0, 0.86, 0.72),
      rot=(math.radians(180), 0, 0), size=1.2, size_y=3.4, shadow=False)
light("LGT_Bounce_South_Wall", "AREA", (0.6, -3.3, 1.6), 70, (1.0, 0.93, 0.85), rot=(math.radians(90), 0, 0),
      size=5.0, size_y=1.6, shadow=False)
light("LGT_Bounce_West_Glass", "AREA", (-4.2, -0.3, 1.6), 35, (0.95, 0.95, 0.95), rot=(0, math.radians(90), 0),
      size=1.6, size_y=6.0, shadow=False)
light("LGT_Bullpen_Ambient", "AREA", (-8, 0, 3.3), 300, (1.0, 0.9, 0.78), size=6, size_y=6)
world = bpy.data.worlds.new("WORLD_Office_Ambient")
sc.world = world
world.use_nodes = True
world.node_tree.nodes["Background"].inputs["Color"].default_value = (0.55, 0.52, 0.48, 1)
world.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.35

# ------------------------------------------------------------------ cameras, markers, shot data
rigm = empty("CAM_RIG_MASTER", "CAMERAS", size=0.4, shape="ARROWS")
FOCUS_SCREEN = empty("FOCUS_Monitor_Display", "CAMERAS", loc=SCREEN, size=0.2, shape="CUBE")


def eval_head(cid, frame):
    sc.frame_set(frame)
    arm = RIGS[cid]
    pb = arm.pose.bones["head"]
    return arm.matrix_world @ pb.head


for sh in S.SHOTS:
    cd = bpy.data.cameras.new(sh["cam"])
    cam = bpy.data.objects.new(sh["cam"], cd)
    COLL["CAMERAS"].objects.link(cam)
    cam.parent = rigm
    cd.lens, cd.sensor_width, cd.sensor_fit = sh["lens"], 36.0, "HORIZONTAL"
    cd.clip_start, cd.clip_end = 0.05, 60
    mid = (sh["start"] + sh["end"]) // 2
    aim = sh["aim"]
    if isinstance(aim, str):
        aim_pt = eval_head(aim, mid) + Vector((0, 0, sh.get("aim_dz", -0.1)))
    else:
        aim_pt = Vector(aim)
    pos = Vector(sh["pos"])
    cam.location = pos
    cam.rotation_euler = aim_rot(pos, aim_pt)
    cam.rotation_euler.y += math.radians(sh.get("dutch", 0.0))
    cd.dof.use_dof = True
    cd.dof.aperture_fstop = sh["fstop"]
    if sh["focus"] == "SCREEN":
        cd.dof.focus_object = FOCUS_SCREEN
    else:
        cd.dof.focus_object, cd.dof.focus_subtarget = RIGS[sh["focus"]], "eyes"
    if sh.get("push"):
        d = (aim_pt - pos).normalized()
        cam.keyframe_insert("location", frame=sh["start"])
        cam.location = pos + d * sh["push"]
        cam.keyframe_insert("location", frame=sh["end"])
        for fc in fcurves(cam):
            for kp in fc.keyframe_points:
                kp.interpolation = "SINE"
                kp.easing = "EASE_IN_OUT"
    if sh.get("handheld"):
        cam.keyframe_insert("rotation_euler", frame=sh["start"])
        for i, s_ in ((0, 0.0035), (2, 0.0045), (1, 0.0015)):
            fc = fcurve(cam, "rotation_euler", i)
            n = fc.modifiers.new("NOISE")
            n.scale, n.strength, n.phase = 26.0, s_, rnd.uniform(0, 100)
    m = sc.timeline_markers.new(f"SH{sh['n']:02d}_{sh['subject']}", frame=sh["start"])
    m.camera = cam
    e = empty(f"SHOT_{sh['n']:02d}_{sh['subject']}", "SHOT_MARKERS", loc=pos, size=0.12, shape="SINGLE_ARROW")
    e["frame_start"], e["frame_end"], e["camera"], e["lens_mm"] = sh["start"], sh["end"], sh["cam"], sh["lens"]
    e["framing"] = sh["framing"]
    e["dialogue"] = " | ".join(f"{w}: {t} [{a}-{b}]" for w, t, a, b in sh["dialogue"])
    e["notes"] = sh["notes"]
    e.hide_render = True
sc.camera = bpy.data.objects[S.SHOTS[0]["cam"]]

# reference storyboard (viewport only)
ref = bpy.data.objects.new("REF_Storyboard_S01E01", None)
ref.empty_display_type = "IMAGE"
ref.data = bpy.data.images.load(os.path.join(ROOT, "reference", "storyboard_s01e01.webp"))
ref.empty_display_size = 3.0
ref.location, ref.rotation_euler = (0, -3.4, 4.6), (math.radians(90), 0, 0)
ref.hide_render = True
COLL["REFERENCE_IMAGES"].objects.link(ref)

sc.frame_set(1)
bpy.ops.file.make_paths_relative()
os.makedirs(os.path.dirname(BLEND), exist_ok=True)
bpy.ops.wm.save_as_mainfile(filepath=BLEND)
print("SAVED", BLEND)
