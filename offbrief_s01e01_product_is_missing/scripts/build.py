"""OFFBRIEF S01E01 'THE PRODUCT IS MISSING' - master scene builder (Blender 5.2, headless).
    python3 scripts/art_box.py      # BOX_01 layers + slides (once)
    python3 scripts/audio.py        # room tone + box foley (once)
    blender -b --factory-startup --python scripts/build.py
Writes scenes/OFFBRIEF_S01E01_MASTER.blend. All data lives in scripts/shotlist.py.
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
ART = os.path.join(ROOT, "art")
BLEND = os.path.join(ROOT, "scenes", "OFFBRIEF_S01E01_MASTER.blend")
rnd = random.Random(11)

bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene
sc.name = "OFFBRIEF_S01E01"

# ------------------------------------------------------------------ collection hierarchy (brief)
TREE = {"ENV_BROOKLYN": ["PITCH_ROOM", "WINDOW_WALL", "GLASS_PARTITIONS", "PRACTICAL_LIGHTS"],
        "PROPS": ["CONFERENCE_TABLE", "PRESENTATION_SCREEN", "WATER_GLASS", "TABLET", "LAPTOPS", "COFFEE_CUPS"],
        "CAST": ["NICO_01", "SLOANE_01", "ELLIOT_01", "VANTA_CLIENT"],
        "ILLUSTRATION": ["BOX_01_SCREEN", "BOX_01_WORLD", "BOX_01_CONTACT_SHADOW"],
        "CAMERAS": [], "AUDIO": ["DIALOGUE", "ROOM_TONE", "BOX_FOLEY"], "ANIMATION_CONTROLS": [], "REFERENCE": []}
COLL = {}
top = bpy.data.collections.new("OFFBRIEF_S01E01")
sc.collection.children.link(top)
for parent, kids in TREE.items():
    c = bpy.data.collections.new(parent)
    top.children.link(c)
    COLL[parent] = c
    for k in kids:
        cc = bpy.data.collections.new(k)
        c.children.link(cc)
        COLL[k] = cc


def link(o, coll):
    for c in list(o.users_collection):
        c.objects.unlink(o)
    COLL[coll].objects.link(o)
    return o


# ------------------------------------------------------------------ materials
MATS = {}


def mat(name, col, rough=0.5, metal=0.0, emit=0.0, alpha=1.0, coat=0.0, sss=0.0, transmission=0.0):
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


def tex_mat(name, kind, c1, c2, scale, rough=0.5, bump=0.1, extra=None, wave_dir="X"):
    """Two-colour procedural material: kind in NOISE, BRICK, VORONOI, WAVE."""
    m = mat(name, c1, rough)
    nt = m.node_tree
    p = nt.nodes["Principled BSDF"]
    tc = nt.nodes.new("ShaderNodeTexCoord")
    if kind == "BRICK":
        t = nt.nodes.new("ShaderNodeTexBrick")
        t.inputs["Color1"].default_value = (*c1, 1)
        t.inputs["Color2"].default_value = (*[x * 0.78 for x in c1], 1)
        t.inputs["Mortar"].default_value = (*c2, 1)
        t.inputs["Scale"].default_value = scale
        t.inputs["Mortar Size"].default_value = 0.012
        t.inputs["Brick Width"].default_value = 0.5
        t.inputs["Row Height"].default_value = 0.25
        sep = nt.nodes.new("ShaderNodeSeparateXYZ")          # wall-aligned: (x + y, z) so bricks lie flat on every wall
        add_ = nt.nodes.new("ShaderNodeMath")
        com = nt.nodes.new("ShaderNodeCombineXYZ")
        nt.links.new(tc.outputs["Object"], sep.inputs[0])
        nt.links.new(sep.outputs["X"], add_.inputs[0])
        nt.links.new(sep.outputs["Y"], add_.inputs[1])
        nt.links.new(add_.outputs[0], com.inputs["X"])
        nt.links.new(sep.outputs["Z"], com.inputs["Y"])
        nt.links.new(com.outputs[0], t.inputs["Vector"])
        nt.links.new(t.outputs["Color"], p.inputs["Base Color"])
        fac = t.outputs["Fac"]
    else:
        t = nt.nodes.new({"NOISE": "ShaderNodeTexNoise", "VORONOI": "ShaderNodeTexVoronoi",
                          "WAVE": "ShaderNodeTexWave"}[kind])
        t.inputs["Scale"].default_value = scale
        if kind == "NOISE":
            t.inputs["Detail"].default_value = 8
        if kind == "WAVE":
            t.bands_direction = wave_dir
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


def img(path):
    return bpy.data.images.load(path, check_existing=True)


def flat_art_mat(name, path, strength=0.9, obj_alpha=False):
    """Flat 2D ink look: emission of the art, binary alpha cut-out (no dither noise)."""
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    nt.nodes.remove(nt.nodes["Principled BSDF"])
    t = nt.nodes.new("ShaderNodeTexImage")
    t.image = img(path)
    t.interpolation = "Cubic"
    e = nt.nodes.new("ShaderNodeEmission")
    e.inputs["Strength"].default_value = strength
    tr = nt.nodes.new("ShaderNodeBsdfTransparent")
    mx = nt.nodes.new("ShaderNodeMixShader")
    cut = nt.nodes.new("ShaderNodeMath")
    cut.operation = "GREATER_THAN"
    cut.inputs[1].default_value = 0.5
    nt.links.new(t.outputs["Color"], e.inputs["Color"])
    nt.links.new(t.outputs["Alpha"], cut.inputs[0])
    if obj_alpha:      # contact shadow: soft alpha scaled by the object's colour alpha (keyed)
        oi = nt.nodes.new("ShaderNodeObjectInfo")
        mul = nt.nodes.new("ShaderNodeMath")
        mul.operation = "MULTIPLY"
        nt.links.new(t.outputs["Alpha"], mul.inputs[0])
        nt.links.new(oi.outputs["Alpha"], mul.inputs[1])
        nt.links.new(mul.outputs[0], mx.inputs[0])
        e.inputs["Strength"].default_value = 0.0
        m.surface_render_method = "BLENDED"
    else:
        nt.links.new(cut.outputs[0], mx.inputs[0])
    nt.links.new(tr.outputs[0], mx.inputs[1])
    nt.links.new(e.outputs[0], mx.inputs[2])
    nt.links.new(mx.outputs[0], nt.nodes["Material Output"].inputs[0])
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


def cyl(name, r, depth, loc, m, coll, rot=(0, 0, 0), verts=24, smooth=True, r2=None):
    if r2 is None:
        bpy.ops.mesh.primitive_cylinder_add(vertices=verts, radius=r, depth=depth, location=loc, rotation=rot)
    else:
        bpy.ops.mesh.primitive_cone_add(vertices=verts, radius1=r, radius2=r2, depth=depth, location=loc, rotation=rot)
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


def card(name, w, h, m, coll, pivot=(0.5, 0.5)):
    """Vertical card in the XZ plane facing -Y; pivot given in UV space of the card (0,0 bottom-left)."""
    me = bpy.data.meshes.new(name)
    px, pz = pivot
    xs, zs = (-px * w, (1 - px) * w), (-pz * h, (1 - pz) * h)
    me.from_pydata([(xs[0], 0, zs[0]), (xs[1], 0, zs[0]), (xs[1], 0, zs[1]), (xs[0], 0, zs[1])], [], [(0, 1, 2, 3)])
    uv = me.uv_layers.new()
    for li, co in enumerate(((0, 0), (1, 0), (1, 1), (0, 1))):
        uv.data[li].uv = co
    me.materials.append(m)
    o = bpy.data.objects.new(name, me)
    COLL[coll].objects.link(o)
    o.visible_shadow = False
    return o


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


def set_interp(idb, kind, path_prefix=None):
    for fc in fcurves(idb):
        if path_prefix and not fc.data_path.startswith(path_prefix):
            continue
        for kp in fc.keyframe_points:
            kp.interpolation = kind


def stepped(idb, step=2):
    """12 fps-inspired stepped motion on the 24 fps timeline."""
    for fc in fcurves(idb):
        m = fc.modifiers.new("STEPPED")
        m.frame_step, m.frame_offset = step, 1


# ------------------------------------------------------------------ scene settings
sc.render.fps = S.FPS
sc.frame_start, sc.frame_end = S.FRAME_START, S.FRAME_END
sc.render.resolution_x, sc.render.resolution_y, sc.render.resolution_percentage = 1920, 1080, 100
sc.render.engine = "BLENDER_EEVEE"
sc.unit_settings.system, sc.unit_settings.scale_length = "METRIC", 1.0
sc.view_settings.view_transform = "AgX"
sc.view_settings.look = "AgX - Base Contrast"
sc.render.image_settings.file_format = "PNG"
sc.render.filepath = "//../deliverables/frames_1080p/OFFBRIEF_S01E01_"
ee = sc.eevee
ee.taa_render_samples = 16
ee.use_shadows = True
ee.use_raytracing = False

# ------------------------------------------------------------------ architecture
W, D, H = S.ROOM["width"], S.ROOM["depth"], S.ROOM["height"]
CONCRETE = tex_mat("MAT_floor_polished_concrete", "NOISE", (0.40, 0.36, 0.32), (0.55, 0.50, 0.44), 1.4, 0.3, 0.02)
BRICK = tex_mat("MAT_exposed_brick", "BRICK", (0.45, 0.19, 0.11), (0.58, 0.55, 0.50), 3.2, 0.85, 0.15)
PLASTER = tex_mat("MAT_wall_plaster_warm", "NOISE", (0.62, 0.58, 0.53), (0.70, 0.66, 0.60), 3.0, 0.9, 0.03)
CEIL = mat("MAT_ceiling_dark", (0.12, 0.12, 0.13), 0.9)
STEEL = mat("MAT_black_metal", (0.025, 0.025, 0.028), 0.45, 0.8)
GLASS = mat("MAT_glass_partition", (0.78, 0.86, 0.86), 0.05, alpha=0.12)
DUCT = mat("MAT_duct_galvanised", (0.5, 0.51, 0.52), 0.35, 0.9)
PR, WW, GP = "PITCH_ROOM", "WINDOW_WALL", "GLASS_PARTITIONS"

box("ARCH_Floor_Concrete", (W + 7.0, D, 0.1), (3.5, 0, -0.05), CONCRETE, PR)
box("ARCH_Ceiling", (W + 7.0, D, 0.1), (3.5, 0, H + 0.05), CEIL, PR)
box("ARCH_Wall_North_Brick", (W, 0.2, H), (0, D / 2 + 0.1, H / 2), BRICK, PR)
box("ARCH_Wall_South_Brick", (W, 0.2, H), (0, -D / 2 - 0.1, H / 2), BRICK, PR)
for i, y in enumerate((-2.7, -0.9, 0.9, 2.7)):     # exposed steel beams E-W
    box(f"ARCH_Ceiling_Beam_{i + 1}", (W + 7.0, 0.18, 0.32), (3.5, y, H - 0.16), STEEL, PR)
cyl("ARCH_Ceiling_Duct", 0.22, D, (2.2, 0, H - 0.6), DUCT, PR, rot=(math.radians(90), 0, 0), verts=32)

# west window wall (industrial black steel frames) - camera-left in the master
WX = -W / 2 - 0.1
SILL, HEAD = 0.55, 3.05
WINDOWS = [(-3.2, -1.3), (-1.0, 0.9), (1.2, 3.1)]
box("ARCH_Wall_West_Sill", (0.2, D, SILL), (WX, 0, SILL / 2), BRICK, WW)
box("ARCH_Wall_West_Header", (0.2, D, H - HEAD), (WX, 0, (H + HEAD) / 2), BRICK, WW)
edges = [-D / 2] + [v for w in WINDOWS for v in w] + [D / 2]
for i in range(0, len(edges), 2):
    y0, y1 = edges[i], edges[i + 1]
    box(f"ARCH_Wall_West_Pier_{i // 2 + 1}", (0.2, y1 - y0, HEAD - SILL), (WX, (y0 + y1) / 2, (SILL + HEAD) / 2), BRICK, WW)
for wi, (y0, y1) in enumerate(WINDOWS, 1):
    for k in range(5):
        box(f"ARCH_Window_{wi}_Mullion_{k}", (0.06, 0.045, HEAD - SILL), (-W / 2 - 0.02, y0 + (y1 - y0) * k / 4, (SILL + HEAD) / 2),
            STEEL, WW)
    for k, z in enumerate((SILL, 1.15, 1.75, 2.4, HEAD)):
        box(f"ARCH_Window_{wi}_Transom_{k}", (0.06, y1 - y0, 0.045), (-W / 2 - 0.02, (y0 + y1) / 2, z), STEEL, WW)
SKY = mat("MAT_exterior_sky_day", (0.70, 0.78, 0.88), 1.0, emit=0.9)
box("ARCH_Exterior_Sky", (0.05, 40, 14), (-18, 0, 4), SKY, WW)
for i in range(16):        # Brooklyn / Manhattan skyline massing (no specific landmark)
    y = -12 + i * 1.6 + rnd.uniform(-0.3, 0.3)
    h = rnd.uniform(2.0, 9.0)
    c = rnd.choice(((0.50, 0.46, 0.44), (0.58, 0.55, 0.52), (0.42, 0.40, 0.40), (0.55, 0.42, 0.34)))
    box(f"ARCH_Exterior_Tower_{i}", (rnd.uniform(1.5, 3), rnd.uniform(1.0, 1.5), h), (rnd.uniform(-16, -10), y, h / 2 - 3),
        mat(f"MAT_exterior_tower_{i % 4}", c, 0.9, emit=0.45), WW)

# east glass partitions (black steel) with the door to the creative floor, south-east
PX = W / 2
DOOR_Y = (-3.25, -2.3)
posts = [-D / 2, -3.3, DOOR_Y[1], -1.2, 0.0, 1.2, 2.4, D / 2]
for i, y in enumerate(posts):
    box(f"ARCH_Partition_Post_{i}", (0.06, 0.06, H), (PX, y, H / 2), STEEL, GP)
box("ARCH_Partition_Head", (0.08, D, 0.06), (PX, 0, 2.4), STEEL, GP)
box("ARCH_Partition_Base", (0.08, D, 0.05), (PX, 0, 0.025), STEEL, GP)
for i in range(2, len(posts) - 1):
    y0, y1 = posts[i], posts[i + 1]
    box(f"ARCH_Partition_Glass_{i - 1}", (0.012, y1 - y0 - 0.06, 2.33), (PX, (y0 + y1) / 2, 1.215), GLASS, GP)
    box(f"ARCH_Partition_GlassTransom_{i - 1}", (0.012, y1 - y0 - 0.06, H - 2.45), (PX, (y0 + y1) / 2, (H + 2.45) / 2), GLASS, GP)
DOOR = tex_mat("MAT_door_oak", "WAVE", (0.38, 0.24, 0.13), (0.52, 0.35, 0.2), 4, 0.5, 0.05, extra=(0.3, 0.7))
box("ARCH_Door_CreativeFloor", (0.045, DOOR_Y[1] - DOOR_Y[0] - 0.04, 2.36), (PX, sum(DOOR_Y) / 2, 1.2), DOOR, GP)
DESK = mat("MAT_creative_floor_desk", (0.42, 0.30, 0.18), 0.6)
for i, (x, y) in enumerate([(6.0, -1.8), (6.0, 0.6), (8.2, -1.8), (8.2, 0.6), (6.0, 2.6)]):
    box(f"ARCH_CreativeFloor_Desk_{i + 1}", (1.5, 0.8, 0.04), (x, y, 0.74), DESK, GP)
    box(f"ARCH_CreativeFloor_Desk_{i + 1}_Frame", (1.4, 0.05, 0.72), (x, y + 0.3, 0.36), STEEL, GP)
    box(f"ARCH_CreativeFloor_Monitor_{i + 1}", (0.6, 0.05, 0.36), (x, y - 0.1, 1.0), STEEL, GP)
box("ARCH_CreativeFloor_Wall_East", (0.2, D, H), (W / 2 + 7.1, 0, H / 2), BRICK, GP)

# ------------------------------------------------------------------ furniture and props
CT, PS = "CONFERENCE_TABLE", "PRESENTATION_SCREEN"
WOOD = tex_mat("MAT_reclaimed_wood_matte", "WAVE", (0.24, 0.13, 0.065), (0.38, 0.22, 0.11), 2.6, 0.55, 0.05,
               extra=(0.2, 0.8), wave_dir="Y")
TB = S.TABLE
tx, ty, TOP = TB["center"][0], TB["center"][1], TB["top_z"]
box("PROP_Conference_Table_Top", (TB["width_x"], TB["length_y"], 0.05), (tx, ty, TOP - 0.025), WOOD, CT, bevel=0.006)
for i, (lx, ly) in enumerate(TB["legs"]):
    box(f"PROP_Conference_Table_Leg_{i + 1}", (0.07, 0.07, TOP - 0.05), (lx, ly, (TOP - 0.05) / 2), STEEL, CT)
box("PROP_Conference_Table_Stretcher", (0.05, TB["legs"][1][1] - TB["legs"][0][1], 0.05),
    (tx, (TB["legs"][0][1] + TB["legs"][1][1]) / 2, 0.15), STEEL, CT)
LEATHER = mat("MAT_leather_cognac", (0.32, 0.14, 0.055), 0.45, coat=0.2)
ALUM = mat("MAT_chair_aluminium", (0.6, 0.6, 0.62), 0.3, 1.0)


def chair(name, x, y, face_deg, seat_top=S.SEAT_TOP):
    f = Vector((math.cos(math.radians(face_deg)), math.sin(math.radians(face_deg)), 0))
    c = Vector((x, y, 0)) - f * 0.03
    parts = [box(name + "_Seat", (0.50, 0.48, 0.07), (0, 0, seat_top - 0.035), LEATHER, CT, bevel=0.02),
             box(name + "_Back", (0.48, 0.07, 0.55), (0, -0.29, seat_top + 0.38), LEATHER, CT, rot=(math.radians(-10), 0, 0), bevel=0.025),
             cyl(name + "_Post", 0.028, seat_top - 0.17, (0, 0, (seat_top - 0.07 + 0.10) / 2), ALUM, CT)]
    for k in (-1, 1):
        parts.append(box(f"{name}_Arm_{k}", (0.04, 0.36, 0.03), (k * 0.27, -0.03, seat_top + 0.2), ALUM, CT))
        parts.append(box(f"{name}_ArmPost_{k}", (0.03, 0.03, 0.2), (k * 0.27, -0.12, seat_top + 0.1), ALUM, CT))
    for k in range(5):
        a = k * 2 * math.pi / 5
        e = Vector((math.cos(a), math.sin(a), 0)) * 0.3
        parts.append(cyl_between(f"{name}_Base_{k}", (0, 0, 0.09), (e.x, e.y, 0.06), 0.018, ALUM, CT, 8))
        parts.append(ell(f"{name}_Caster_{k}", (0.05, 0.05, 0.05), (e.x, e.y, 0.03), STEEL, CT, 8))
    root = empty(name, CT, size=0.3, shape="PLAIN_AXES")
    for p in parts:
        p.parent = root
    root.location, root.rotation_euler.z = c, math.radians(face_deg) - math.pi / 2
    return root


for cid, cd in S.CAST.items():
    if cd["pose"] == "seated":
        chair(f"PROP_Chair_{cid}", *cd["pos"], cd["face"])
for i, (x, y, f) in enumerate(S.EMPTY_CHAIRS):
    chair(f"PROP_Chair_Empty_{i + 1}", x, y, f)

SBM = tex_mat("MAT_sideboard_walnut", "WAVE", (0.22, 0.12, 0.06), (0.32, 0.19, 0.09), 3, 0.5, 0.03, extra=(0.3, 0.7))
sb = S.SIDEBOARD
box("PROP_Sideboard", sb["size"], (sb["center"][0], sb["center"][1], sb["size"][2] / 2), SBM, PS, bevel=0.01)
MON = S.MONITOR
box("PROP_Screen_Bezel", (MON["width"] + 0.04, 0.05, MON["height"] + 0.04), (MON["center"][0], MON["center"][1] + 0.03, MON["center"][2]),
    STEEL, PS, bevel=0.004)
box("PROP_Screen_WallMount", (0.4, 0.06, 0.3), (MON["center"][0], MON["center"][1] + 0.07, MON["center"][2]), STEEL, PS)
# display: logo slide until the reveal, then the illustration panel (key on the mix factor)
sm = bpy.data.materials.new("MAT_screen_slides")
sm.use_nodes = True
nt = sm.node_tree
nt.nodes.remove(nt.nodes["Principled BSDF"])
t1, t2 = nt.nodes.new("ShaderNodeTexImage"), nt.nodes.new("ShaderNodeTexImage")
t1.image, t2.image = img(os.path.join(ART, "slide_offbrief_logo.png")), img(os.path.join(ART, "slide_box_illustration.png"))
mix = nt.nodes.new("ShaderNodeMix")
mix.data_type = "RGBA"
mix.name = "SLIDE_SWITCH"
em = nt.nodes.new("ShaderNodeEmission")
em.inputs["Strength"].default_value = 1.1
nt.links.new(t1.outputs["Color"], mix.inputs[6])
nt.links.new(t2.outputs["Color"], mix.inputs[7])
nt.links.new(mix.outputs[2], em.inputs["Color"])
nt.links.new(em.outputs[0], nt.nodes["Material Output"].inputs[0])
for f, v in ((1, 0.0), (312, 0.0), (313, 1.0)):
    mix.inputs[0].default_value = v
    mix.inputs[0].keyframe_insert("default_value", frame=f)
for fc in fcurves(nt):
    for kp in fc.keyframe_points:
        kp.interpolation = "CONSTANT"
scr = card("PROP_Screen_Display", MON["width"], MON["height"], sm, "BOX_01_SCREEN")
scr.location = (MON["center"][0], MON["center"][1], MON["center"][2])
link(scr, PS)

LAP = mat("MAT_laptop_aluminium", (0.62, 0.62, 0.64), 0.35, 1.0)
LAPS = mat("MAT_laptop_screen", (0.55, 0.62, 0.75), 0.2, emit=0.5)


def laptop(name, x, y, yaw_deg):
    root = empty(name, "LAPTOPS", size=0.15, shape="PLAIN_AXES")
    parts = [box(name + "_Base", (0.31, 0.22, 0.014), (0, 0, 0.007), LAP, "LAPTOPS", bevel=0.003),
             box(name + "_Lid", (0.31, 0.008, 0.21), (0, 0.13, 0.105), LAP, "LAPTOPS", rot=(math.radians(-15), 0, 0)),
             box(name + "_Screen", (0.29, 0.002, 0.19), (0, 0.122, 0.105), LAPS, "LAPTOPS", rot=(math.radians(-15), 0, 0))]
    for o in parts:
        o.parent = root
    root.location, root.rotation_euler.z = (x, y, TOP), math.radians(yaw_deg)
    return root


laptop("PROP_Laptop_Nico", -0.30, -0.30, 80)
laptop("PROP_Laptop_Client", 0.10, -0.80, -100)
MUG = mat("MAT_mug_white_offbrief", (0.88, 0.87, 0.84), 0.3)
COFFEE = mat("MAT_coffee", (0.08, 0.04, 0.02), 0.1)
KRAFTC = mat("MAT_takeaway_cup_kraft", (0.55, 0.40, 0.24), 0.7)
for i, (x, y) in enumerate([(-0.48, 0.20), (0.36, -0.12), (-0.42, 1.35)]):
    root = empty(f"PROP_Coffee_Mug_{i + 1}", "COFFEE_CUPS", size=0.06, shape="PLAIN_AXES")
    for o in (cyl(f"PROP_Coffee_Mug_{i + 1}_Body", 0.04, 0.095, (0, 0, 0.0475), MUG, "COFFEE_CUPS"),
              cyl(f"PROP_Coffee_Mug_{i + 1}_Coffee", 0.036, 0.002, (0, 0, 0.085), COFFEE, "COFFEE_CUPS"),
              torus(f"PROP_Coffee_Mug_{i + 1}_Handle", 0.025, 0.007, (0.045, 0, 0.05), MUG, "COFFEE_CUPS", rot=(math.radians(90), 0, 0))):
        o.parent = root
    root.location, root.rotation_euler.z = (x, y, TOP), rnd.uniform(0, 6.28)
cyl("PROP_Takeaway_Cup", 0.04, 0.13, (0.40, 0.70, TOP + 0.065), KRAFTC, "COFFEE_CUPS", r2=0.03)
WATER = mat("MAT_water_glass", (0.80, 0.90, 0.95), 0.03, alpha=0.25)
cyl("PROP_Water_Glass", 0.036, 0.13, (0.32, 1.88, TOP + 0.065), WATER, "WATER_GLASS")
cyl("PROP_Water_Glass_Water", 0.033, 0.09, (0.32, 1.88, TOP + 0.046), mat("MAT_water", (0.65, 0.80, 0.88), 0.02, alpha=0.3),
    "WATER_GLASS")
cyl("PROP_Water_Carafe", 0.055, 0.24, (-0.05, 0.55, TOP + 0.12), WATER, "WATER_GLASS")
PAPER = mat("MAT_paper", (0.88, 0.87, 0.84), 0.8)
YELLOW = mat("MAT_notebook_yellow", (0.92, 0.70, 0.08), 0.6)
BLACKN = mat("MAT_notebook_black", (0.03, 0.03, 0.03), 0.6)
sl = S.CAST["SLOANE_01"]


def local_xy(cid, lx, ly):
    c = S.CAST[cid]
    a = math.radians(c["face"]) - math.pi / 2
    return (c["pos"][0] + lx * math.cos(a) - ly * math.sin(a), c["pos"][1] + lx * math.sin(a) + ly * math.cos(a))


x, y = local_xy("SLOANE_01", 0.0, 0.62)
box("PROP_Brief_Sloane", (0.21, 0.297, 0.004), (x, y, TOP + 0.002), PAPER, CT, rot=(0, 0, math.radians(sl["face"] - 90 + 4)))
x, y = local_xy("SLOANE_01", 0.22, 0.50)
box("PROP_Notebook_Yellow", (0.15, 0.21, 0.014), (x, y, TOP + 0.007), YELLOW, CT, rot=(0, 0, 0.2), bevel=0.002)
box("PROP_Notebook_Black", (0.15, 0.21, 0.014), (-0.35, -0.85, TOP + 0.007), BLACKN, CT, rot=(0, 0, -0.3), bevel=0.002)
POT = mat("MAT_planter_concrete", (0.6, 0.58, 0.55), 0.8)
LEAF = mat("MAT_plant_leaf", (0.10, 0.25, 0.08), 0.6, sss=0.2)
for pi_, (px, py) in enumerate([(-1.6, 3.1), (2.3, 3.1), (-3.9, -3.0), (3.9, -2.9)]):
    cyl(f"PROP_Planter_{pi_ + 1}", 0.2, 0.45, (px, py, 0.225), POT, PR)
    for i in range(12):
        a = rnd.uniform(0, 2 * math.pi)
        r = rnd.uniform(0.05, 0.28)
        ell(f"PROP_Plant_{pi_ + 1}_Leaf_{i}", (0.30, 0.13, 0.04), (px + r * math.cos(a), py + r * math.sin(a), rnd.uniform(0.6, 1.4)),
            LEAF, PR, 8).rotation_euler = (rnd.uniform(-0.6, 0.6), rnd.uniform(-0.6, 0.6), a)

# ------------------------------------------------------------------ cast rigs (faceless proxies, wardrobe from the storyboard)
RIGS, LOOK, EYES, IKT, EYE_OBJS, DIMS = {}, {}, {}, {}, {}, {}
GOLD = mat("MAT_gold_jewellery", (0.95, 0.70, 0.30), 0.25, 1.0)


def attach(o, arm, bone):
    b = arm.data.bones[bone]
    pw = arm.matrix_world @ b.matrix_local @ Matrix.Translation((0, b.length, 0))
    w = o.matrix_world.copy()
    o.parent, o.parent_type, o.parent_bone = arm, "BONE", bone
    o.matrix_parent_inverse = pw.inverted()
    o.matrix_basis = w


def wardrobe(cid, c, add, hc, Hs, G, zh, hair, sk, shirt):
    V = Vector
    st = c["style"]
    h = st["hair"]
    rr = random.Random(cid)
    dark = mat(f"MAT_{cid}_facial_hair", tuple(x * 0.9 for x in c["hair"]), 0.9)
    if h in ("short", "curly", "updo"):
        add("hair_cap", "ell", (0.172 * Hs, 0.214 * Hs, 0.14 * Hs), hc + V((0, -0.012 * Hs, 0.062 * Hs)), hair, "head")
        add("hair_back", "ell", (0.165 * Hs, 0.12 * Hs, 0.17 * Hs), hc + V((0, -0.05 * Hs, 0.0)), hair, "head")
    if h == "curly":
        for i in range(26):
            a = rr.uniform(0, 2 * math.pi)
            el = rr.uniform(0.2, 1.3)
            p = hc + V((math.cos(a) * math.cos(el) * 0.085 * Hs, math.sin(a) * math.cos(el) * 0.1 * Hs - 0.01 * Hs,
                        0.03 * Hs + math.sin(el) * 0.1 * Hs))
            if p.y - hc.y > 0.06 * Hs and p.z - hc.z < 0.08 * Hs:
                continue
            r = rr.uniform(0.055, 0.075) * Hs
            add(f"curl_{i:02d}", "ell", (r, r, r), p, hair, "head", seg=8)
    if h == "updo":
        add("updo_bun", "ell", (0.13 * Hs, 0.12 * Hs, 0.11 * Hs), hc + V((0, -0.05 * Hs, 0.13 * Hs)), hair, "head", seg=12)
        for i in range(8):
            k = -1 if i % 2 else 1
            add(f"loose_strand_{i}", "ell", (0.028 * Hs, 0.03 * Hs, 0.08 * Hs),
                hc + V((k * 0.08 * Hs, (0.03 - 0.015 * i) * Hs, (-0.01 - 0.008 * i) * Hs)), hair, "head", seg=8)
    if st.get("mustache"):
        add("mustache", "ell", (0.075 * Hs, 0.03 * Hs, 0.022 * Hs), hc + V((0, 0.096 * Hs, -0.045 * Hs)), dark, "head", seg=10)
    if st.get("hoops"):
        for k in (-1, 1):
            add(f"hoop_{k}", "torus", (0.02 * Hs, 0.0028, (1, 1, 1)), hc + V((k * 0.088 * Hs, 0.0, -0.065 * Hs)), GOLD,
                "head", rot=(0, math.radians(90), 0))
    if st.get("necklace"):
        add("necklace", "torus", (0.075 * G, 0.003, (1.0, 1.2, 1.0)), V((0, 0.03 * G, zh + 0.43 * Hs)), GOLD, "chest",
            rot=(math.radians(-30), 0, 0))
    if st.get("aviators"):
        lens = mat("MAT_aviator_lens_amber", (0.40, 0.25, 0.07), 0.05, 0.5)
        for k in (-1, 1):
            add(f"aviator_lens_{k}", "ell", (0.05 * Hs, 0.012, 0.042 * Hs), hc + V((k * 0.035 * Hs, 0.118 * Hs, 0.014 * Hs)), lens, "head", seg=12)
            add(f"aviator_arm_{k}", "box", (0.006, 0.11 * Hs, 0.006), hc + V((k * 0.08 * Hs, 0.07 * Hs, 0.03 * Hs)), GOLD, "head")
        add("aviator_bridge", "box", (0.07 * Hs, 0.006, 0.006), hc + V((0, 0.122 * Hs, 0.036 * Hs)), GOLD, "head")
    if st.get("glasses"):
        frame = mat("MAT_glasses_frame", (0.08, 0.05, 0.03), 0.4)
        for k in (-1, 1):
            add(f"glasses_rim_{k}", "torus", (0.022 * Hs, 0.0025, (1, 1, 0.85)), hc + V((k * 0.035 * Hs, 0.116 * Hs, 0.016 * Hs)),
                frame, "head", rot=(math.radians(90), 0, 0))
            add(f"glasses_arm_{k}", "box", (0.004, 0.11 * Hs, 0.004), hc + V((k * 0.075 * Hs, 0.07 * Hs, 0.02 * Hs)), frame, "head")
    if st.get("tee"):
        add("tee", "ell", (0.18 * G, 0.20 * G, 0.36 * Hs), V((0, 0.045 * G, zh + 0.32 * Hs)),
            mat(f"MAT_{cid}_tee", st["tee"], 0.85), "chest")
    if st.get("suspenders"):
        red = mat("MAT_suspenders_red", (0.45, 0.06, 0.05), 0.6)
        for k in (-1, 1):
            add(f"suspender_{k}", "box", (0.025, 0.012, 0.42 * Hs), V((k * 0.09 * G, 0.128 * G, zh + 0.24 * Hs)), red, "chest")
    if st.get("tie"):
        tie = tex_mat("MAT_tie_red_pattern", "VORONOI", (0.85, 0.65, 0.35), (0.42, 0.07, 0.06), 60, 0.6, 0.0, extra=(0.05, 0.12))
        add("tie", "box", (0.05, 0.012, 0.32 * Hs), V((0, 0.132 * G, zh + 0.27 * Hs)), tie, "chest")
        add("tie_knot", "ell", (0.04, 0.03, 0.035), V((0, 0.125 * G, zh + 0.445 * Hs)), tie, "chest", seg=8)


def build_actor(cid, c):
    Hs, G, B = c["H"], c["G"], c.get("belly", 1.0)
    standing = c["pose"] == "standing"
    zh = 0.93 * Hs if standing else S.SEAT_TOP + 0.075 * G + 0.012
    sw = 0.185 * G
    sh_z = zh + 0.44 * Hs
    hc = Vector((0, 0.012 * Hs, zh + 0.64 * Hs))
    DIMS[cid] = dict(zh=zh, sw=sw, shoulder_z=sh_z, head_c=hc)
    coll = cid
    ad = bpy.data.armatures.new(cid + "_RIG")
    arm = bpy.data.objects.new(cid + "_RIG", ad)
    COLL[coll].objects.link(arm)
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
             "eyes": (tuple(hc + Vector((0, 0.05 * Hs, 0.015 * Hs))), tuple(hc + Vector((0, 0.12, 0.015 * Hs))), "head")}
    for side, k in (("L", -1), ("R", 1)):
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
            o = box(nm, size, loc, m, coll, bevel=min(size) * 0.3)
        elif kind == "ell":
            o = ell(nm, size, loc, m, coll, seg)
        elif kind == "cyl":
            o = cyl_between(nm, size[0], size[1], size[2], m, coll)
        elif kind == "torus":
            o = torus(nm, size[0], size[1], loc, m, coll, rot=rot or (0, 0, 0), scale=size[2])
        if rot and kind != "torus":
            o.rotation_euler = rot
        o.matrix_world = Matrix.LocRotScale(o.location, o.rotation_euler.to_quaternion(), o.scale)   # fresh before binding
        attach(o, arm, bone)
        return o

    sk = mat(f"MAT_{cid}_skin", c["skin"], 0.55, sss=0.15)
    pat = c["style"].get("pattern")
    if pat == "denim":
        shirt = tex_mat(f"MAT_{cid}_denim_jacket", "NOISE", c["shirt"], tuple(x * 1.3 for x in c["shirt"]), 60, 0.85, 0.05)
    elif pat == "stripe":
        shirt = tex_mat(f"MAT_{cid}_striped_shirt", "WAVE", (0.93, 0.94, 0.96), (0.45, 0.55, 0.75), 40, 0.7, 0.0,
                        extra=(0.55, 0.6), wave_dir="X")
    else:
        shirt = mat(f"MAT_{cid}_top", c["shirt"], 0.8)
    sleeve = shirt if c["sleeves"] != "none" else sk
    pants = mat(f"MAT_{cid}_trousers", c["pants"], 0.8)
    shoe = mat(f"MAT_{cid}_shoes", (0.05, 0.04, 0.035), 0.5)
    hair = mat(f"MAT_{cid}_hair", c["hair"], 0.7)
    eye = mat("MAT_proxy_eye_marker", (0.02, 0.018, 0.016), 0.2)
    for side, k in (("L", -1), ("R", 1)):
        hip = Vector((k * 0.1 * G, -0.02, zh))
        if standing:
            knee = Vector((k * 0.1 * G, 0.02, 0.5 * Hs))
            ankle = Vector((k * 0.1 * G, 0.0, 0.09))
            shoe_c = (k * 0.1 * G, 0.07, 0.0475)
        else:
            knee = Vector((k * 0.1 * G, 0.45 * Hs, zh + 0.01))
            ankle = Vector((k * 0.1 * G, 0.48 * Hs, 0.09))
            shoe_c = (k * 0.1 * G, 0.53 * Hs, 0.0475)
        add(f"thigh.{side}", "cyl", (hip, knee, 0.075 * G), None, pants, "root")
        add(f"knee.{side}", "ell", (0.13 * G,) * 3, knee, pants, "root", seg=12)
        add(f"shin.{side}", "cyl", (knee, ankle, 0.055 * G), None, pants, "root")
        add(f"shoe.{side}", "box", (0.1, 0.27, 0.085), shoe_c, shoe, "root")
    add("hips", "ell", (0.38 * G, 0.30 * G, 0.2), (0, -0.03, zh + 0.03), pants, "pelvis")
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
        add(f"shoulder.{side}", "ell", (0.13 * G, 0.13 * G, 0.12 * G), b_u.head_local, sleeve if c["sleeves"] != "none" else shirt,
            f"upper_arm.{side}")
        add(f"upper_arm.{side}", "cyl", (b_u.head_local, b_u.tail_local, 0.05 * G), None, sleeve, f"upper_arm.{side}")
        add(f"elbow.{side}", "ell", (0.09 * G,) * 3, b_f.head_local, sleeve if c["sleeves"] == "long" else sk, f"forearm.{side}", seg=10)
        add(f"forearm.{side}", "cyl", (b_f.head_local, b_f.tail_local, 0.041 * G), None,
            sleeve if c["sleeves"] == "long" else sk, f"forearm.{side}")
        add(f"hand.{side}", "box", (0.07, 0.03, 0.095 * Hs), (b_h.head_local + b_h.tail_local) / 2, sk, f"hand.{side}")
    wardrobe(cid, c, add, hc, Hs, G, zh, hair, sk, shirt)

    IKT[cid] = {}
    for side, k in (("L", -1), ("R", 1)):
        t = empty(f"{cid}_IK_hand.{side}", "ANIMATION_CONTROLS", size=0.05, shape="CUBE")
        t.parent = arm
        t.location = c["rest"][side]
        p = empty(f"{cid}_POLE_elbow.{side}", "ANIMATION_CONTROLS", size=0.03)
        p.parent = arm
        p.location = (k * 0.6 * G, -0.35, sh_z - 0.25)
        ik = arm.pose.bones[f"forearm.{side}"].constraints.new("IK")
        ik.target, ik.pole_target, ik.chain_count, ik.use_tail = t, p, 2, True
        ik.pole_angle = math.radians(-90)
        IKT[cid][side] = t
    lk = empty(f"{cid}_LOOK", "ANIMATION_CONTROLS", size=0.06)
    ey = empty(f"{cid}_EYES", "ANIMATION_CONTROLS", size=0.03)
    ey.parent = lk
    dt = arm.pose.bones["head"].constraints.new("DAMPED_TRACK")
    dt.target, dt.track_axis, dt.influence = lk, "TRACK_Y", 0.85
    de = arm.pose.bones["eyes"].constraints.new("DAMPED_TRACK")
    de.target, de.track_axis = ey, "TRACK_Y"
    LOOK[cid], EYES[cid] = lk, ey
    arm.location = (*c["pos"], 0)
    arm.rotation_euler.z = math.radians(c["face"]) - math.pi / 2
    RIGS[cid] = arm
    cu = bpy.data.curves.new(f"{cid}_LABEL", "FONT")
    cu.body = f"{cid} (PROXY)\n{c['role']}"
    cu.size, cu.align_x = 0.09, "CENTER"
    lb = bpy.data.objects.new(f"{cid}_LABEL", cu)
    COLL[coll].objects.link(lb)
    lb.parent = arm
    lb.location = (0, 0, zh + 1.0)
    lb.rotation_euler.x = math.radians(90)
    lb.hide_render = True
    return arm


for cid, c in S.CAST.items():
    build_actor(cid, c)
arm = RIGS["ELLIOT_01"]
tab = box("PROP_Tablet_Elliot", (0.25, 0.175, 0.008), (0, 0, 0), STEEL, "TABLET", bevel=0.003)
tabs = box("PROP_Tablet_Elliot_Display", (0.235, 0.16, 0.001), (0, 0, 0.0045), mat("MAT_tablet_display", (0.6, 0.66, 0.8), 0.2, emit=0.8),
           "TABLET")
tabs.parent = tab
tab.parent = arm
tab.location = S.ELLIOT_TABLET["loc"]
tab.rotation_euler = [math.radians(a) for a in S.ELLIOT_TABLET["rot"]]
bpy.context.view_layer.update()

# ------------------------------------------------------------------ BOX_01: flat 2D layered rig (one continuous object)
BX = "BOX_01_WORLD"
PXM = S.BOX_SIZE_M / 1000.0              # metres per art pixel
box_root = empty("BOX_01", BX, size=0.15, shape="PLAIN_AXES")     # sole of the sneakers; keyed along BOX_PATH
box_yaw = empty("BOX_01_FACING", BX, size=0.12, shape="SINGLE_ARROW")  # yaw toward the shot camera (limited)
box_yaw.parent = box_root
box_sq = empty("BOX_01_SQUASH", BX, size=0.1, shape="CUBE")            # squash & stretch pivot at the soles
box_sq.parent = box_yaw
LEG_H, SHOE_S, GLOVE_S, ARM_L = 0.05, 0.6, 0.48, 0.07
SHOE_H = 220 * PXM * SHOE_S
BODY_BOTTOM = SHOE_H + LEG_H
body_c = BODY_BOTTOM - 0.10 * S.BOX_SIZE_M + 0.5 * S.BOX_SIZE_M     # body art bottom edge is 100 px above canvas bottom
LAYERS = {}


def art_card(name, file, w_px, h_px, scale, pivot, loc, depth):
    m = flat_art_mat(f"MAT_BOX_01_{name}", os.path.join(ART, file))
    o = card(f"BOX_01_{name}", w_px * PXM * scale, h_px * PXM * scale, m, BX, pivot)
    o.location = (loc[0], -depth, loc[1])
    return o


for nm in ("body_closed", "body_open"):
    LAYERS[nm] = art_card(nm, f"box_{nm}.png", 1000, 1000, 1.0, (0.5, 0.5), (0, body_c), 0.0)
for nm in ("eyes_open", "eyes_happy", "eyes_sad", "mouth_open", "mouth_smile", "mouth_sad"):
    LAYERS[nm] = art_card(nm, f"box_{nm}.png", 1000, 1000, 1.0, (0.5, 0.5), (0, body_c), 0.002)
for o in LAYERS.values():
    o.parent = box_sq
LIMB = {}
for side, k in (("L", -1), ("R", 1)):
    sh_x = (-0.2 if k < 0 else 0.29) * S.BOX_SIZE_M        # left edge of the front face / outer edge of the side face
    sh = empty(f"BOX_01_shoulder.{side}", BX, size=0.03, shape="CIRCLE")
    sh.parent = box_sq
    sh.location = (sh_x, -0.004, body_c - 0.06)
    sh.rotation_mode = "XYZ"
    a = art_card(f"arm.{side}", "box_limb.png", 200, 400, ARM_L / (400 * PXM), (0.5, 0.97), (0, 0), 0.0)
    a.parent = sh
    g = art_card(f"glove.{side}", "box_glove.png", 300, 300, GLOVE_S, (0.5, 0.93), (0, -ARM_L), 0.001)
    g.parent = sh
    if k > 0:
        g.scale.x = -1
    hip = empty(f"BOX_01_hip.{side}", BX, size=0.03, shape="CIRCLE")
    hip.parent = box_sq
    hip.location = (k * 0.045, -0.003, BODY_BOTTOM + 0.01)
    lg = art_card(f"leg.{side}", "box_limb.png", 200, 400, (LEG_H + 0.012) / (400 * PXM), (0.5, 0.97), (0, 0), 0.0)
    lg.parent = hip
    so = art_card(f"sneaker.{side}", "box_sneaker.png", 360, 220, SHOE_S, (0.5, 0.95), (k * 0.012, -LEG_H - 0.008), 0.001)
    so.parent = hip
    if k < 0:
        so.scale.x = -1
    LIMB[side] = (sh, hip)
focus_box = empty("BOX_01_FOCUS", BX, size=0.05)
focus_box.parent = box_sq
focus_box.location = (0, -0.01, body_c)

# path
for f, x, y, z in S.BOX_PATH:
    box_root.location = (x, y, z)
    box_root.keyframe_insert("location", frame=f)
for f, dx in S.BOX_DANCE:
    box_root.location = (S.BOX_PATH[-1][1] + dx, S.BOX_PATH[-1][2], S.BOX_PATH[-1][3])
    box_root.keyframe_insert("location", frame=f)
set_interp(box_root, "LINEAR")
# hidden (scale 0) until the slide reveal
box_root.scale = (0, 0, 0)
box_root.keyframe_insert("scale", frame=312)
box_root.scale = (1, 1, 1)
box_root.keyframe_insert("scale", frame=313)
set_interp(box_root, "CONSTANT", "scale")
for f, sx, sz in S.BOX_SQUASH:
    box_sq.scale = (sx, 1.0, sz)
    box_sq.keyframe_insert("scale", frame=f)
for f, la, ra in S.BOX_ARMS:
    LIMB["L"][0].rotation_euler = (0, math.radians(la), 0)
    LIMB["R"][0].rotation_euler = (0, -math.radians(ra), 0)
    LIMB["L"][0].keyframe_insert("rotation_euler", frame=f, index=1)
    LIMB["R"][0].keyframe_insert("rotation_euler", frame=f, index=1)
for a, b in S.BOX_STEPS:
    for i, f in enumerate(range(a, b + 1, 4)):
        s = 1 if i % 2 else -1
        for side, k in (("L", 1), ("R", -1)):
            LIMB[side][1].rotation_euler = (0, math.radians(22 * s * k), 0)
            LIMB[side][1].keyframe_insert("rotation_euler", frame=f, index=1)
    for side in ("L", "R"):
        LIMB[side][1].rotation_euler = (0, 0, 0)
        LIMB[side][1].keyframe_insert("rotation_euler", frame=b + 2, index=1)
# expressions: layer visibility by scale (constant keys)
state = {}
for f, body, eyes_, mouth in S.BOX_FACE:
    on = {f"body_{body}", f"eyes_{eyes_}", f"mouth_{mouth}"}
    for nm, o in LAYERS.items():
        v = 1.0 if nm in on else 0.0
        o.scale = (v, v, v)
        o.keyframe_insert("scale", frame=f)
for o in LAYERS.values():
    set_interp(o, "CONSTANT")


def cam_at(frame):
    for sh in S.SHOTS:
        if sh["start"] <= frame <= sh["end"]:
            return sh
    return S.SHOTS[-1]


# yaw toward each shot's camera, 85 % and clamped to +-40 deg (limited perspective rotation); on-screen it faces south
for sh in S.SHOTS:
    f = sh["start"]
    if f < 361:
        yaw = 0.0
    else:
        p = Vector(S.BOX_PATH[-1][1:]) if f >= 400 else Vector(S.BOX_PATH[6][1:])
        d = Vector(sh["pos"]) - p
        yaw = max(-40.0, min(40.0, 0.85 * math.degrees(math.atan2(d.x, -d.y))))
    box_yaw.rotation_euler.z = math.radians(yaw)
    box_yaw.keyframe_insert("rotation_euler", frame=f, index=2)
set_interp(box_yaw, "CONSTANT")
for o in [box_root, box_sq, LIMB["L"][0], LIMB["R"][0], LIMB["L"][1], LIMB["R"][1]]:
    if o.animation_data:
        stepped(o, 2)

# contact shadow (horizontal soft ellipse under the soles, faded by height above the support surface)
shm = flat_art_mat("MAT_BOX_01_contact_shadow", os.path.join(ART, "box_contact_shadow.png"), obj_alpha=True)
bpy.ops.mesh.primitive_plane_add(size=1)
shadow = bpy.context.object
shadow.name = "BOX_01_CONTACT_SHADOW"
shadow.scale = (0.30, 0.16, 1)
bpy.ops.object.transform_apply(scale=True)
shadow.data.materials.append(shm)
shadow.visible_shadow = False
link(shadow, "BOX_01_CONTACT_SHADOW")
SCREEN_PLANE_Y = MON["center"][1]


def support_z(x, y):
    if abs(x - tx) <= TB["width_x"] / 2 and abs(y - ty) <= TB["length_y"] / 2:
        return TOP, "TABLE"
    sbc, sbs = S.SIDEBOARD["center"], S.SIDEBOARD["size"]
    if abs(x - sbc[0]) <= sbs[0] / 2 and abs(y - sbc[1]) <= sbs[1] / 2:
        return sbs[2], "SIDEBOARD"
    return 0.0, "FLOOR"


TRAJ = []
for f in range(S.FRAME_START, S.FRAME_END + 1):
    sc.frame_set(f)
    p = box_root.matrix_world.translation.copy()
    vis = box_root.scale.x > 0.5
    on_screen = p.y >= SCREEN_PLANE_Y - 0.02
    sz, surf = support_z(p.x, p.y)
    hgt = p.z - sz
    a = 0.0 if (not vis or on_screen) else max(0.0, 1.0 - hgt / 0.35) * 0.85
    shadow.location = (p.x, p.y + 0.01, sz + 0.002)
    shadow.color = (1, 1, 1, a)
    shadow.keyframe_insert("location", frame=f)
    shadow.keyframe_insert("color", frame=f, index=3)
    TRAJ.append(dict(frame=f, x=round(p.x, 4), y=round(p.y, 4), z=round(p.z, 4), visible=vis,
                     phase="hidden" if not vis else ("screen" if on_screen else ("grounded" if hgt < 0.005 else "airborne")),
                     support=None if on_screen or not vis else surf, height_above_support=round(hgt, 4), shadow_alpha=round(a, 3)))

# ------------------------------------------------------------------ gaze, blinks, torso, hands
def head_world(cid):
    return RIGS[cid].matrix_world @ (DIMS[cid]["head_c"] + Vector((0, 0.05, 0)))


def box_face_world(f):
    t = TRAJ[f - 1]
    return Vector((t["x"], t["y"] - 0.02, t["z"] + 0.22))


def target_pos(cid, tgt, f):
    if tgt == "BOX":
        return box_face_world(max(f, 313))
    if tgt.startswith("LOCAL:"):
        return RIGS[cid].matrix_world @ Vector([float(v) for v in tgt[6:].split(",")])
    return head_world(tgt) + Vector((0, 0, -0.03))


for cid, sched in S.LOOKS.items():
    lk, ey = LOOK[cid], EYES[cid]
    me = head_world(cid)
    keys = {}
    for i, ev in enumerate(sched):
        f0, tgt = ev[0], ev[1]
        dur = ev[2] if len(ev) > 2 else 8
        frac = ev[3] if len(ev) > 3 else 1.0
        f_end = sched[i + 1][0] if i + 1 < len(sched) else S.FRAME_END + 1
        if i > 0:
            keys[f0] = keys.get(f0) or keys[max(k for k in keys if k <= f0)]
        step = 3 if tgt == "BOX" else max(1, f_end - f0 - dur - 1)
        for f in range(f0 + (dur if i > 0 else 0), f_end, step):
            full = target_pos(cid, tgt, f)
            look = me + (full - me) * frac
            keys[f] = (look, full - look)
    for sh in S.SHOTS:   # small nods during the actor's own lines
        for who, _line, a, b in sh["dialogue"]:
            if who != cid:
                continue
            sgn, f = 1, a + 4
            while f < b - 2:
                base = keys[max(k for k in keys if k <= f)]
                d = (base[0] - me).length
                keys[f] = (base[0] + Vector((0, 0, 0.03 * d * sgn)), base[1])
                sgn, f = -sgn, f + rnd.randint(9, 13)
    for f in sorted(keys):
        lk.location, ey.location = keys[f]
        lk.keyframe_insert("location", frame=f)
        ey.keyframe_insert("location", frame=f)
    for i in range(3):
        n = fcurve(ey, "location", i).modifiers.new("NOISE")
        n.scale, n.strength, n.phase = 16.0, 0.03, rnd.uniform(0, 100)

for cid, eyes in EYE_OBJS.items():
    frames, f = [], rnd.randint(10, 40)
    while f < S.FRAME_END - 6:
        frames.append(f)
        f += rnd.randint(55, 110)
    for e in eyes:
        base = e.scale.z
        for f in frames:
            for df, s in ((0, 1.0), (2, 0.08), (4, 1.0)):
                e.scale.z = base * s
                e.keyframe_insert("scale", frame=f + df, index=2)
        e.scale.z = base

for cid, keys in S.TORSO.items():
    arm = RIGS[cid]
    sp, ch = arm.pose.bones["spine"], arm.pose.bones["chest"]
    for f, lean, twist in keys:
        for pb, w in ((sp, 0.55), (ch, 0.45)):
            pb.rotation_euler = (-math.radians(lean) * w, math.radians(twist) * w, 0)
            pb.keyframe_insert("rotation_euler", frame=f)
    g = fcurve(arm, 'pose.bones["chest"].rotation_euler', 0).modifiers.new("FNGENERATOR")
    g.function_type, g.use_additive, g.amplitude = "SIN", True, 0.012
    g.phase_multiplier = 2 * math.pi / (S.FPS * rnd.uniform(3.6, 4.6))
    g.phase_offset = rnd.uniform(0, 6.28)
    for idx in (1, 2):
        n = fcurve(arm, 'pose.bones["spine"].rotation_euler', idx).modifiers.new("NOISE")
        n.scale, n.strength, n.phase = 110.0, 0.03, rnd.uniform(0, 100)

for cid, sides in S.HANDS.items():
    for side, keys in sides.items():
        t = IKT[cid][side]
        for f, loc in keys:
            t.location = loc
            t.keyframe_insert("location", frame=f)
    for (side, a, b, strength, scale) in S.HAND_NOISE.get(cid, []):
        t = IKT[cid][side]
        for i in range(3):
            n = fcurve(t, "location", i).modifiers.new("NOISE")
            n.scale, n.strength, n.phase = scale, strength, rnd.uniform(0, 100)
            n.use_restricted_range = True
            n.frame_start, n.frame_end, n.blend_in, n.blend_out = a, b, 2, 2

# ------------------------------------------------------------------ lighting (fixed for every shot)
PL = "PRACTICAL_LIGHTS"


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
    COLL[PL].objects.link(o)
    return o


sun_dir = Vector((math.cos(math.radians(30)), -0.25, -math.sin(math.radians(30))))
sun = light("LGT_Sun_Daylight_West", "SUN", (-8, 0, 6), 2.6, S.K5600, rot=sun_dir.to_track_quat("-Z", "Y").to_euler())
sun.data.angle = math.radians(2.5)
for i, (y0, y1) in enumerate(WINDOWS, 1):
    light(f"LGT_Window_Fill_{i}", "AREA", (-W / 2 + 0.08, (y0 + y1) / 2, (SILL + HEAD) / 2), 240, S.K5600,
          rot=(0, math.radians(90), 0), size=y1 - y0, size_y=HEAD - SILL)
SHADE = mat("MAT_pendant_shade_black", (0.02, 0.02, 0.02), 0.4, 0.6)
BULB = mat("MAT_pendant_bulb_3200K", (1.0, 0.72, 0.42), 0.3, emit=12)
for i, (x, y) in enumerate(S.PENDANTS, 1):
    z = 2.45
    cyl(f"LGT_Pendant_{i}_Cord", 0.004, H - z - 0.15, (x, y, (H + z + 0.15) / 2), STEEL, PL, verts=6)
    sh = cyl(f"LGT_Pendant_{i}_Shade", 0.22, 0.2, (x, y, z), SHADE, PL, r2=0.05, verts=32)
    sh.modifiers.new("Solidify", "SOLIDIFY").thickness = 0.006
    ell(f"LGT_Pendant_{i}_Bulb", (0.09, 0.09, 0.09), (x, y, z - 0.07), BULB, PL, 12)
    light(f"LGT_Practical_Pendant_{i}", "SPOT", (x, y, z - 0.1), 60, S.K3200, radius=0.08).data.spot_size = math.radians(120)
light("LGT_Bounce_Table_Up", "AREA", (tx, ty, TOP + 0.02), 20, (1.0, 0.86, 0.72), rot=(math.radians(180), 0, 0),
      size=1.2, size_y=3.4, shadow=False)
light("LGT_Bounce_South", "AREA", (0.3, -3.3, 1.7), 80, (1.0, 0.93, 0.85), rot=(math.radians(90), 0, 0), size=5.0, size_y=1.6,
      shadow=False)
light("LGT_Bounce_East_Glass", "AREA", (4.2, 0.3, 1.6), 40, (0.95, 0.95, 0.95), rot=(0, math.radians(-90), 0), size=1.6,
      size_y=6.0, shadow=False)
light("LGT_CreativeFloor_Ambient", "AREA", (7.5, 0, 3.3), 300, (1.0, 0.9, 0.78), size=6, size_y=6)
world = bpy.data.worlds.new("WORLD_Office_Ambient")
sc.world = world
world.use_nodes = True
world.node_tree.nodes["Background"].inputs["Color"].default_value = (0.55, 0.52, 0.48, 1)
world.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.35

# ------------------------------------------------------------------ cameras, set-ups, markers
CAMS, FOCUS = {}, {}
for name, cd in S.CAMERAS.items():
    cdat = bpy.data.cameras.new(name)
    cam = bpy.data.objects.new(name, cdat)
    COLL["CAMERAS"].objects.link(cam)
    cdat.lens, cdat.sensor_width, cdat.sensor_fit = cd["lens"], 36.0, "HORIZONTAL"
    cdat.clip_start, cdat.clip_end = 0.03, 60
    cdat.dof.use_dof, cdat.dof.aperture_fstop = True, cd["fstop"]
    fe = empty(f"FOCUS_{name}", "CAMERAS", size=0.05)
    cdat.dof.focus_object = fe
    CAMS[name], FOCUS[name] = cam, fe


def eval_world(obj_or_cid, frame):
    sc.frame_set(frame)
    if obj_or_cid == "BOX":
        return focus_box.matrix_world.translation.copy()
    arm = RIGS[obj_or_cid]
    return arm.matrix_world @ arm.pose.bones["eyes"].head


SETUPS = []
for sh in S.SHOTS:
    cam = CAMS[sh["cam"]]
    mid = (sh["start"] + sh["end"]) // 2
    aim = sh["aim"]
    aim_pt = eval_world(aim, mid) + Vector((0, 0, sh.get("aim_dz", -0.1))) if isinstance(aim, str) else Vector(aim)
    pos = Vector(sh["pos"])
    rot = (aim_pt - pos).to_track_quat("-Z", "Y").to_euler()
    cam.location, cam.rotation_euler = pos, rot
    cam.keyframe_insert("location", frame=sh["start"])
    cam.keyframe_insert("rotation_euler", frame=sh["start"])
    fp = eval_world(sh["focus"], mid)
    FOCUS[sh["cam"]].location = fp
    FOCUS[sh["cam"]].keyframe_insert("location", frame=sh["start"])
    m = sc.timeline_markers.new(f"SH{sh['n']:02d}_{sh['cam']}_{sh['setup']}", frame=sh["start"])
    m.camera = cam
    SETUPS.append(dict(shot=sh["n"], camera=sh["cam"], setup=sh["setup"], position=[round(v, 3) for v in pos],
                       rotation_deg=[round(math.degrees(a), 2) for a in rot], aim_point=[round(v, 3) for v in aim_pt],
                       focus_point=[round(v, 3) for v in fp], focus_distance=round((fp - pos).length, 3)))
for o in list(CAMS.values()) + list(FOCUS.values()):
    set_interp(o, "CONSTANT")
sc.camera = CAMS[S.SHOTS[0]["cam"]]

# ------------------------------------------------------------------ audio: positioned speakers + sequencer strips
AUD = os.path.join(ROOT, "audio")
for cid in S.CAST:
    spk = bpy.data.objects.new(f"SPK_DIALOGUE_{cid}", bpy.data.speakers.new(f"SPK_DIALOGUE_{cid}"))
    COLL["DIALOGUE"].objects.link(spk)
    spk.parent = RIGS[cid]
    spk.location = DIMS[cid]["head_c"] + Vector((0, 0.1, -0.05))
for nm, coll, parent in (("room_tone", "ROOM_TONE", None), ("box_foley", "BOX_FOLEY", box_root)):
    p = os.path.join(AUD, f"OFFBRIEF_S01E01_{nm}.wav")
    if os.path.exists(p):
        snd = bpy.data.sounds.load(p, check_existing=True)
        spk = bpy.data.objects.new(f"SPK_{coll}", bpy.data.speakers.new(f"SPK_{coll}"))
        spk.data.sound = snd
        COLL[coll].objects.link(spk)
        if parent:
            spk.parent = parent
        se = sc.sequence_editor_create()
        strips = se.strips if hasattr(se, "strips") else se.sequences
        strips.new_sound(coll, p, channel=1 if coll == "ROOM_TONE" else 2, frame_start=1)
for i, f in enumerate(["S01E01_storyboard.webp", "ENV_01_agency.webp", "ENV_02_geography.webp", "PROP_01_props.webp"]):
    ref = bpy.data.objects.new(f"REF_{f.split('.')[0]}", None)
    ref.empty_display_type = "IMAGE"
    ref.data = img(os.path.join(ROOT, "reference", f))
    ref.empty_display_size = 3.0
    ref.location, ref.rotation_euler = (-4.5 + i * 3.1, -3.45, 5.2), (math.radians(90), 0, 0)
    ref.hide_render = True
    COLL["REFERENCE"].objects.link(ref)

# data for the reports
import json  # noqa: E402
meta = dict(box_trajectory=TRAJ, camera_setups=SETUPS,
            actors={cid: dict(root=[round(v, 4) for v in RIGS[cid].location], yaw_deg=S.CAST[cid]["face"],
                              pose=S.CAST[cid]["pose"]) for cid in S.CAST},
            box_rig=dict(size_m=S.BOX_SIZE_M, body_bottom_m=round(BODY_BOTTOM, 4), stepped_frame_step=2))
os.makedirs(os.path.join(ROOT, "reports"), exist_ok=True)
with open(os.path.join(ROOT, "reports", "_build_meta.json"), "w") as fh:
    json.dump(meta, fh)

sc.frame_set(1)
bpy.ops.file.make_paths_relative()
os.makedirs(os.path.dirname(BLEND), exist_ok=True)
bpy.ops.wm.save_as_mainfile(filepath=BLEND)
print("SAVED", BLEND)
