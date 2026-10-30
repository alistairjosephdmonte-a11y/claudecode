"""Location build: Mumbai street exterior, nightclub facade/doorway, corridor, club interior, props, lighting.

World layout (metres): +X = screen-right for the street cameras, +Y = north (into the building).
Facade plane y=0, doorway x in [-0.6, 0.6]. Camera-side pavement y in [-3, 0]. Road y < -3.
"""
import math
import random
from math import pi, sin, cos, radians
import bpy
import bmesh
from mathutils import Vector

from common import (bm_box, bm_ellipsoid, bm_limb, mesh_from_bm, new_object, box_object, principled, emission,
                    fabric, srgb, _mat, _coord, _noise, _bump, _mix_col, _ramp, _set)

DOOR_X0, DOOR_X1, DOOR_H = -0.6, 0.6, 2.4
FACADE_T = 0.35
STANCHION_L = Vector((-0.35, -0.70))
STANCHION_R = Vector((0.45, -0.70))
HOOK_Z = 0.93
BOUNCER_MARK = Vector((0.95, -0.95))
SHELF_POS = Vector((1.3, -0.11, 1.28))


# ---------------------------------------------------------------- materials
def mat_wet_asphalt():
    m, nt, out = _mat("MAT_ASPHALT_WET")
    b = nt.nodes.new("ShaderNodeBsdfPrincipled")
    vec = _coord(nt)
    puddle = _noise(nt, vec, 0.35, 3.0, 0.5)
    r = _ramp(nt, puddle.outputs["Fac"], [(0.0, (0.5,) * 4), (0.52, (0.42,) * 4), (0.6, (0.06,) * 4), (1.0, (0.04,) * 4)])
    nt.links.new(r.outputs[0], b.inputs["Roughness"])
    grit = _noise(nt, vec, 55.0, 8.0, 0.7)
    col = _mix_col(nt, srgb("#151517"), srgb("#2A2A2C"), grit.outputs["Fac"])
    nt.links.new(col, b.inputs["Base Color"])
    bp = _bump(nt, grit.outputs["Fac"], 0.35, 0.01)
    nt.links.new(bp.outputs["Normal"], b.inputs["Normal"])
    _set(b, "Specular IOR Level", 0.55)
    nt.links.new(b.outputs[0], out.inputs[0])
    return m


def mat_paving():
    m, nt, out = _mat("MAT_PAVEMENT_TILES_WET")
    b = nt.nodes.new("ShaderNodeBsdfPrincipled")
    vec = _coord(nt)
    br = nt.nodes.new("ShaderNodeTexBrick")
    br.inputs["Scale"].default_value = 1.6
    br.inputs["Mortar Size"].default_value = 0.012
    br.inputs["Color1"].default_value = srgb("#3A3836")
    br.inputs["Color2"].default_value = srgb("#2E2D2C")
    br.inputs["Mortar"].default_value = srgb("#151413")
    nt.links.new(vec, br.inputs["Vector"])
    stain = _noise(nt, vec, 1.2, 4.0)
    col = _mix_col(nt, br.outputs["Color"], srgb("#1C1B1A"), stain.outputs["Fac"])
    nt.links.new(col, b.inputs["Base Color"])
    wet = _noise(nt, vec, 0.6, 2.0)
    r = _ramp(nt, wet.outputs["Fac"], [(0.0, (0.55,) * 4), (0.5, (0.35,) * 4), (0.62, (0.08,) * 4), (1.0, (0.06,) * 4)])
    nt.links.new(r.outputs[0], b.inputs["Roughness"])
    bp = _bump(nt, br.outputs["Fac"], 0.25, 0.01)
    nt.links.new(bp.outputs["Normal"], b.inputs["Normal"])
    nt.links.new(b.outputs[0], out.inputs[0])
    return m


def mat_concrete(name, a="#5B5853", b_="#3E3B37", scale=2.0):
    m, nt, out = _mat(name)
    b = nt.nodes.new("ShaderNodeBsdfPrincipled")
    vec = _coord(nt)
    n = _noise(nt, vec, scale, 8.0, 0.65)
    grime = _noise(nt, vec, 0.4, 3.0)
    col = _mix_col(nt, srgb(b_), srgb(a), n.outputs["Fac"])
    col2 = _mix_col(nt, col, srgb("#22201D"), grime.outputs["Fac"])
    nt.links.new(col2, b.inputs["Base Color"])
    _set(b, "Roughness", 0.88)
    fine = _noise(nt, vec, 40.0, 6.0)
    bp = _bump(nt, fine.outputs["Fac"], 0.3, 0.01)
    nt.links.new(bp.outputs["Normal"], b.inputs["Normal"])
    nt.links.new(b.outputs[0], out.inputs[0])
    return m


def mat_shutter():
    m, nt, out = _mat("MAT_METAL_SHUTTER")
    b = nt.nodes.new("ShaderNodeBsdfPrincipled")
    vec = _coord(nt)
    w = nt.nodes.new("ShaderNodeTexWave")
    w.wave_type = "BANDS"
    w.bands_direction = "Z"
    w.inputs["Scale"].default_value = 9.0
    nt.links.new(vec, w.inputs["Vector"])
    bp = _bump(nt, w.outputs["Fac"], 0.6, 0.02)
    nt.links.new(bp.outputs["Normal"], b.inputs["Normal"])
    rust = _noise(nt, vec, 3.0, 8.0, 0.7)
    rr = _ramp(nt, rust.outputs["Fac"], [(0.0, srgb("#5E6266")), (0.55, srgb("#4D5155")), (0.7, srgb("#5A3A26")), (1.0, srgb("#3B2A1E"))])
    nt.links.new(rr.outputs[0], b.inputs["Base Color"])
    _set(b, "Metallic", 0.75)
    _set(b, "Roughness", 0.5)
    nt.links.new(b.outputs[0], out.inputs[0])
    return m


def mat_poster(name, seed):
    """Aged abstract poster: colour fields + paper wear. Deliberately no text, logos or brand marks."""
    rnd = random.Random(seed)
    pal = [("#B23A2E", "#E2C15A"), ("#2F5D8A", "#E8DCC0"), ("#6C2C6E", "#E39B3A"), ("#2C6B4F", "#D9D2BE"),
           ("#C8622A", "#1F2A44"), ("#8B1E3F", "#F0E2C4")][seed % 6]
    m, nt, out = _mat(name)
    b = nt.nodes.new("ShaderNodeBsdfPrincipled")
    vec = _coord(nt, "Generated")
    v = nt.nodes.new("ShaderNodeTexVoronoi")
    v.inputs["Scale"].default_value = rnd.uniform(1.5, 4.0)
    nt.links.new(vec, v.inputs["Vector"])
    base = _mix_col(nt, srgb(pal[0]), srgb(pal[1]), v.outputs["Distance"])
    wear = _noise(nt, _coord(nt), 9.0, 6.0, 0.7)
    wr = _ramp(nt, wear.outputs["Fac"], [(0.0, (0, 0, 0, 1)), (0.58, (0, 0, 0, 1)), (0.66, (1, 1, 1, 1)), (1.0, (1, 1, 1, 1))])
    col = _mix_col(nt, base, srgb("#CFC6B0"), wr.outputs[0])
    nt.links.new(col, b.inputs["Base Color"])
    _set(b, "Roughness", 0.92)
    nt.links.new(b.outputs[0], out.inputs[0])
    return m


def mat_velvet():
    m, nt, out = _mat("MAT_VELVET_ROPE_RED")
    b = nt.nodes.new("ShaderNodeBsdfPrincipled")
    _set(b, "Base Color", srgb("#5E0B14"))
    _set(b, "Roughness", 0.95)
    _set(b, "Sheen Weight", 1.0)
    _set(b, "Sheen Tint", srgb("#E05060"))
    _set(b, "Specular IOR Level", 0.2)
    nt.links.new(b.outputs[0], out.inputs[0])
    return m


# ---------------------------------------------------------------- builders
def plane_grid(name, x0, x1, y0, y1, z, nx, ny, coll, mat, disp=0.0, seed=0):
    bm = bmesh.new()
    rnd = random.Random(seed)
    verts = []
    for j in range(ny + 1):
        row = []
        for i in range(nx + 1):
            x = x0 + (x1 - x0) * i / nx
            y = y0 + (y1 - y0) * j / ny
            dz = 0.0
            if disp:
                dz = disp * (0.6 * sin(x * 1.3 + seed) * cos(y * 1.7) + 0.4 * sin(x * 4.1 + y * 3.3 + seed * 2))
                dz += disp * 0.3 * (rnd.random() - 0.5)
            row.append(bm.verts.new((x, y, z + dz)))
        verts.append(row)
    for j in range(ny):
        for i in range(nx):
            bm.faces.new((verts[j][i], verts[j][i + 1], verts[j + 1][i + 1], verts[j + 1][i]))
    return new_object(name, mesh_from_bm(name, bm), coll, [mat])


def build_exterior(cols):
    C = cols["LOCATION_EXTERIOR"]
    P = cols["PROPS"]
    asphalt = mat_wet_asphalt()
    paving = mat_paving()
    conc = mat_concrete("MAT_CONCRETE_FACADE")
    conc2 = mat_concrete("MAT_CONCRETE_NEIGHBOUR_A", "#6B5E52", "#463D35", 1.5)
    conc3 = mat_concrete("MAT_CONCRETE_NEIGHBOUR_B", "#4E5552", "#343A38", 2.5)
    curb = mat_concrete("MAT_CURB_STONE", "#77746E", "#55524C", 6.0)
    shutter = mat_shutter()
    trim = principled("MAT_DOOR_TRIM_PAINTED_METAL", "#1C1D21", rough=0.45, metal=0.6)
    glass = principled("MAT_WINDOW_GLASS_DARK", "#0A0C10", rough=0.08, spec=0.7)
    warm_win = emission("MAT_WINDOW_WARM_LIT", "#E8A35A", 0.6)
    pipe = principled("MAT_PIPE_PVC_GREY", "#6F706B", rough=0.6)
    ac = principled("MAT_AC_UNIT_GREY", "#9B9A94", rough=0.55)
    cable = principled("MAT_CABLE_BLACK", "#050505", rough=0.5)

    plane_grid("STREET_ROAD_ASPHALT", -30, 30, -16, -3.12, -0.15, 120, 26, C, asphalt, disp=0.015, seed=3)
    plane_grid("STREET_PAVEMENT", -30, 30, -3.0, 0.0, 0.0, 120, 6, C, paving, disp=0.006, seed=7)
    box_object("STREET_CURB", (60, 0.16, 0.17), (0, -3.06, -0.07), C, curb, bevel=0.01)

    # Facade with doorway opening (north side of pavement)
    box_object("FACADE_LEFT", (11.4, FACADE_T, 9.0), (-6.3, FACADE_T / 2, 4.5), C, conc)
    box_object("FACADE_RIGHT", (11.4, FACADE_T, 9.0), (6.3, FACADE_T / 2, 4.5), C, conc)
    box_object("FACADE_LINTEL", (1.2, FACADE_T, 9.0 - DOOR_H), (0, FACADE_T / 2, DOOR_H + (9.0 - DOOR_H) / 2), C, conc)
    box_object("NEIGHBOUR_WEST", (18, 4, 12.5), (-21, 2.0, 6.25), C, conc2)
    box_object("NEIGHBOUR_EAST", (18, 4, 7.0), (21, 2.0, 3.5), C, conc3)
    box_object("FACADE_PLINTH", (24, 0.05, 0.25), (0, -0.02, 0.125), C, mat_concrete("MAT_PLINTH_STAINED", "#3A3632", "#26231F", 3))
    # door frame
    box_object("DOOR_JAMB_L", (0.08, 0.42, DOOR_H + 0.08), (DOOR_X0 - 0.04, 0.16, (DOOR_H + 0.08) / 2), C, trim)
    box_object("DOOR_JAMB_R", (0.08, 0.42, DOOR_H + 0.08), (DOOR_X1 + 0.04, 0.16, (DOOR_H + 0.08) / 2), C, trim)
    box_object("DOOR_HEADER", (1.36, 0.42, 0.08), (0, 0.16, DOOR_H + 0.04), C, trim)
    box_object("DOOR_THRESHOLD", (1.2, 0.4, 0.03), (0, 0.15, 0.015), C, trim)
    box_object("DOOR_SHUTTER_HOUSING", (1.5, 0.3, 0.32), (0, -0.12, DOOR_H + 0.32), C, shutter, bevel=0.03)
    # shutters + housings
    for i, (x0, x1, h) in enumerate([(-9.2, -6.0, 3.0), (-4.9, -1.75, 2.8), (2.05, 5.3, 2.9), (6.6, 10.2, 3.0)]):
        box_object("SHUTTER_%02d" % (i + 1), (x1 - x0, 0.04, h), ((x0 + x1) / 2, -0.02, h / 2), C, shutter)
        box_object("SHUTTER_HOUSING_%02d" % (i + 1), (x1 - x0 + 0.1, 0.28, 0.3), ((x0 + x1) / 2, -0.1, h + 0.15), C, shutter, bevel=0.03)
    # upper-floor windows
    rnd = random.Random(11)
    for fl, z in enumerate((4.6, 7.4)):
        for i, x in enumerate([-9.5, -6.5, -3.5, 3.5, 6.5, 9.5]):
            lit = rnd.random() < 0.35
            box_object("WINDOW_F%d_%02d" % (fl + 1, i + 1), (1.3, 0.06, 1.5), (x, -0.005, z), C, warm_win if lit else glass)
            box_object("WINDOW_SILL_F%d_%02d" % (fl + 1, i + 1), (1.45, 0.14, 0.08), (x, -0.06, z - 0.8), C, conc)
    for i, x in enumerate([-14, -18, -22, -26]):
        for j, z in enumerate((3.5, 6.5, 9.5)):
            box_object("NEIGHBOUR_WIN_%d_%d" % (i, j), (1.4, 0.05, 1.4), (x, -0.03, z), C, warm_win if (i + j) % 3 == 0 else glass)
    # services: drain pipes, AC units, overhead cables
    for i, x in enumerate((-1.05, 5.9)):
        bm = bmesh.new()
        bm_limb(bm, (x, -0.09, 0.05), (x, -0.09, 9.0), 0.05, 0.05, seg=12)
        new_object("DRAIN_PIPE_%02d" % (i + 1), mesh_from_bm("DRAIN_PIPE_%02d" % (i + 1), bm), C, [pipe])
    for i, (x, z) in enumerate([(-7.8, 5.6), (-2.6, 5.7), (4.6, 5.5), (8.4, 8.3)]):
        box_object("AC_UNIT_%02d" % (i + 1), (0.8, 0.32, 0.55), (x, -0.2, z), C, ac, bevel=0.02)
    for i, (z0, sag, y) in enumerate([(6.6, 0.8, -2.2), (6.9, 1.1, -2.6), (7.3, 0.6, -1.4), (6.2, 0.9, -3.4)]):
        cu = bpy.data.curves.new("OVERHEAD_CABLE_%02d" % (i + 1), "CURVE")
        cu.dimensions = "3D"
        cu.bevel_depth = 0.008
        sp = cu.splines.new("POLY")
        n = 24
        sp.points.add(n)
        for k in range(n + 1):
            t = k / n
            x = -30 + 60 * t
            sp.points[k].co = (x, y + 0.3 * sin(t * 3 + i), z0 - sag * 4 * t * (1 - t) * 3, 1)
        ob = new_object(cu.name, cu, C)
        cu.materials.append(cable)

    # posters (aged, abstract, no legible text or brands)
    poster_spots = [(-1.45, 1.55, 0.55, 0.8, 0), (-2.2, 1.35, 0.5, 0.7, 1), (1.6, 1.6, 0.5, 0.75, 2),
                    (-5.4, 1.4, 0.6, 0.85, 3), (-8.1, 1.5, 0.55, 0.8, 4), (2.9, 1.3, 0.5, 0.72, 5),
                    (-3.4, 1.45, 0.5, 0.72, 2), (7.4, 1.5, 0.55, 0.8, 1)]
    for i, (x, z, w, h, s) in enumerate(poster_spots):
        bm = bmesh.new()
        bm_box(bm, (w, 0.004, h), (0, 0, 0))
        ob = new_object("POSTER_AGED_%02d" % (i + 1), mesh_from_bm("POSTER_AGED_%02d" % (i + 1), bm, False), C,
                        [mat_poster("MAT_POSTER_%02d" % (i + 1), s + i)])
        ob.location = (x, -0.045 - 0.002 * i, z)
        ob.rotation_euler.y = radians((i * 37 % 7) - 3)

    # practical lamps + neon (no text)
    warm_bulb = emission("MAT_PRACTICAL_BULB_WARM", "#FFC27A", 18.0)
    hood = principled("MAT_LAMP_HOOD_METAL", "#2A2B2E", rough=0.4, metal=0.8)
    bm = bmesh.new()
    bm_ellipsoid(bm, (0.06, 0.06, 0.08), (0, -0.32, 2.66))
    new_object("PRACTICAL_DOOR_BULB", mesh_from_bm("PRACTICAL_DOOR_BULB", bm), C, [warm_bulb])
    box_object("PRACTICAL_DOOR_HOOD", (0.26, 0.26, 0.06), (0, -0.32, 2.77), C, hood, bevel=0.02)
    box_object("PRACTICAL_DOOR_ARM", (0.03, 0.3, 0.03), (0, -0.17, 2.8), C, hood)
    for i, x in enumerate((-3.2, 3.6)):
        bm = bmesh.new()
        bm_ellipsoid(bm, (0.045, 0.045, 0.06), (x, -0.12, 2.35))
        new_object("PRACTICAL_SCONCE_BULB_%02d" % (i + 1), mesh_from_bm("SCONCE_%d" % i, bm), C, [warm_bulb])
        box_object("PRACTICAL_SCONCE_PLATE_%02d" % (i + 1), (0.14, 0.04, 0.2), (x, -0.03, 2.35), C, hood)
    neon_b = emission("MAT_NEON_BLUE", "#3D6BFF", 9.0)
    neon_r = emission("MAT_NEON_RED", "#FF2A3C", 7.0)
    cu = bpy.data.curves.new("NEON_TUBE_BLUE_ABSTRACT", "CURVE")
    cu.dimensions = "3D"
    cu.bevel_depth = 0.014
    sp = cu.splines.new("POLY")
    pts = [(-3.9, -0.06, 3.15), (-3.5, -0.06, 3.45), (-3.1, -0.06, 3.15), (-2.7, -0.06, 3.45), (-2.3, -0.06, 3.15)]
    sp.points.add(len(pts) - 1)
    for k, p in enumerate(pts):
        sp.points[k].co = (*p, 1)
    new_object(cu.name, cu, C)
    cu.materials.append(neon_b)
    cu = bpy.data.curves.new("NEON_TUBE_RED_RING", "CURVE")
    cu.dimensions = "3D"
    cu.bevel_depth = 0.012
    sp = cu.splines.new("POLY")
    sp.use_cyclic_u = True
    n = 20
    sp.points.add(n - 1)
    for k in range(n):
        a = 2 * pi * k / n
        sp.points[k].co = (3.1 + 0.3 * cos(a), -0.06, 3.3 + 0.3 * sin(a), 1)
    new_object(cu.name, cu, C)
    cu.materials.append(neon_r)

    # bollards
    bol = principled("MAT_BOLLARD_PAINTED", "#3B3C38", rough=0.6, metal=0.3)
    for i, x in enumerate((-8.0, -4.6, 4.2, 7.8)):
        bm = bmesh.new()
        bm_limb(bm, (x, -2.82, 0), (x, -2.82, 0.75), 0.07, 0.065, seg=14)
        new_object("BOLLARD_%02d" % (i + 1), mesh_from_bm("BOLLARD_%02d" % (i + 1), bm), C, [bol])

    # entrance props: stanchions, rope (curve, animated elsewhere), shelf
    brass = principled("MAT_STANCHION_BRASS", "#B08A4A", rough=0.28, metal=1.0)
    for nm, p in (("STANCHION_ENTRANCE_LEFT", STANCHION_L), ("STANCHION_ENTRANCE_RIGHT", STANCHION_R)):
        bm = bmesh.new()
        bm_limb(bm, (p.x, p.y, 0.0), (p.x, p.y, 0.035), 0.16, 0.15, seg=24)
        bm_limb(bm, (p.x, p.y, 0.03), (p.x, p.y, HOOK_Z), 0.024, 0.022, seg=14)
        bm_ellipsoid(bm, (0.042,) * 3, (p.x, p.y, HOOK_Z + 0.04))
        ob = new_object(nm, mesh_from_bm(nm, bm), P, [brass])
        ob["geography"] = "entrance-left = screen-left" if "LEFT" in nm else "entrance-right = screen-right"
    wood = principled("MAT_SHELF_PAINTED_WOOD", "#2B2622", rough=0.7)
    box_object("ENTRANCE_SHELF", (0.36, 0.2, 0.03), (SHELF_POS.x, SHELF_POS.y, SHELF_POS.z - 0.015), P, wood, bevel=0.005)
    box_object("ENTRANCE_SHELF_BRACKET", (0.03, 0.18, 0.12), (SHELF_POS.x, SHELF_POS.y + 0.005, SHELF_POS.z - 0.09), P, hood)
    return dict(brass=brass, velvet=mat_velvet())


def build_rope(cols, mats):
    """Velvet rope as a NURBS curve; its control points are keyframed (see perform.rope_points)."""
    cu = bpy.data.curves.new("VELVET_ROPE", "CURVE")
    cu.dimensions = "3D"
    cu.bevel_depth = 0.017
    cu.bevel_resolution = 3
    cu.resolution_u = 6
    sp = cu.splines.new("NURBS")
    sp.points.add(15)
    sp.order_u = 4
    sp.use_endpoint_u = True
    ob = new_object("VELVET_ROPE", cu, cols["PROPS"])
    cu.materials.append(mats["velvet"])
    hooks = []
    for nm in ("ROPE_HOOK_END_LEFT", "ROPE_HOOK_END_RIGHT"):
        bm = bmesh.new()
        bm_limb(bm, (0, 0, -0.035), (0, 0, 0.035), 0.022, 0.016, seg=12)
        h = new_object(nm, mesh_from_bm(nm, bm), cols["PROPS"], [mats["brass"]])
        hooks.append(h)
    return ob, hooks


def build_interior(cols):
    C = cols["LOCATION_INTERIOR"]
    P = cols["PROPS"]
    wall = principled("MAT_CLUB_WALL_MATTE", "#1D1820", rough=0.9, bump=0.15, bump_scale=30)
    floor = principled("MAT_CLUB_FLOOR_POLISHED_CONCRETE", "#2A2729", rough=0.22, bump=0.03, bump_scale=8, color_var=0.3)
    corr_floor = principled("MAT_CORRIDOR_FLOOR", "#252224", rough=0.4, color_var=0.2, bump_scale=6)
    ceil = principled("MAT_CEILING_BLACK", "#0C0B0D", rough=0.9)
    bar_wood = principled("MAT_BAR_DARK_WOOD", "#2C1C14", rough=0.5, bump=0.08, bump_scale=12, color_var=0.25)
    bar_top = principled("MAT_BAR_TOP_STONE", "#3B3836", rough=0.15)
    metal = principled("MAT_STOOL_METAL", "#2F3033", rough=0.35, metal=0.9)
    seat = principled("MAT_STOOL_SEAT_LEATHERETTE", "#1A1A1C", rough=0.5)
    mag_strip = emission("MAT_LED_STRIP_MAGENTA", "#FF2FB0", 6.0)
    warm_strip = emission("MAT_LED_STRIP_WARM", "#FFB565", 4.0)
    speaker = principled("MAT_SPEAKER_BLACK", "#0E0E10", rough=0.7)

    # corridor y 0.35..5
    box_object("CORRIDOR_FLOOR", (1.3, 4.7, 0.04), (0, 2.675, -0.02), C, corr_floor)
    box_object("CORRIDOR_WALL_W", (0.1, 4.7, 2.7), (-0.7, 2.675, 1.35), C, wall)
    box_object("CORRIDOR_WALL_E", (0.1, 4.7, 2.7), (0.7, 2.675, 1.35), C, wall)
    box_object("CORRIDOR_CEILING", (1.5, 4.7, 0.1), (0, 2.675, 2.65), C, ceil)
    drape = fabric("MAT_ENTRY_CURTAIN_VELVET_BLACK", "#120910", rough=0.95, sheen=0.8, weave=40, strength=0.6)
    bm = bmesh.new()
    for i in range(16):
        x = -0.65 + 1.3 * (i + 0.5) / 16
        bm_box(bm, (1.3 / 16 + 0.01, 0.05, 2.58), (x, 4.7 + 0.03 * sin(i * 1.9), 1.29))
    new_object("CORRIDOR_ENTRY_CURTAIN", mesh_from_bm("CORRIDOR_ENTRY_CURTAIN", bm), C, [drape])
    for i, x in enumerate((-0.63, 0.63)):
        box_object("CORRIDOR_LED_%02d" % (i + 1), (0.02, 4.4, 0.02), (x, 2.7, 2.55), C, mag_strip)
    # club room x -8..8, y 5..18
    box_object("CLUB_FLOOR", (16, 13, 0.04), (0, 11.5, -0.02), C, floor)
    box_object("CLUB_CEILING", (16, 13, 0.1), (0, 11.5, 4.25), C, ceil)
    box_object("CLUB_WALL_N", (16, 0.2, 4.3), (0, 18.1, 2.15), C, wall)
    box_object("CLUB_WALL_W", (0.2, 13, 4.3), (-8.1, 11.5, 2.15), C, wall)
    box_object("CLUB_WALL_E", (0.2, 13, 4.3), (8.1, 11.5, 2.15), C, wall)
    box_object("CLUB_WALL_S_W", (7.35, 0.2, 4.3), (-4.325, 4.9, 2.15), C, wall)
    box_object("CLUB_WALL_S_E", (7.35, 0.2, 4.3), (4.325, 4.9, 2.15), C, wall)
    box_object("CLUB_WALL_S_TOP", (1.3, 0.2, 1.6), (0, 4.9, 3.45), C, wall)
    # bar
    box_object("BAR_COUNTER", (9.0, 0.8, 1.04), (1.5, 16.2, 0.52), C, bar_wood)
    box_object("BAR_TOP", (9.2, 0.95, 0.05), (1.5, 16.15, 1.065), C, bar_top, bevel=0.01)
    box_object("BAR_FOOTREST", (9.0, 0.06, 0.06), (1.5, 15.7, 0.22), C, metal)
    box_object("BAR_UNDERGLOW", (9.0, 0.02, 0.02), (1.5, 15.78, 1.0), C, warm_strip)
    box_object("BACKBAR_SHELF_1", (8.0, 0.35, 0.04), (1.5, 17.75, 1.5), C, bar_wood)
    box_object("BACKBAR_SHELF_2", (8.0, 0.35, 0.04), (1.5, 17.75, 2.1), C, bar_wood)
    box_object("BACKBAR_GLOW", (8.0, 0.02, 0.02), (1.5, 17.95, 2.6), C, mag_strip)
    rnd = random.Random(5)
    glass_cols = ["#2E5E3A", "#6B3A1C", "#3A2E5E", "#7A6A2A", "#1E3B4F"]
    bottle_mats = [principled("MAT_BOTTLE_GLASS_%d" % i, c, rough=0.08, spec=0.8) for i, c in enumerate(glass_cols)]
    for k, z in enumerate((1.52, 2.12)):
        x = -2.3
        i = 0
        while x < 5.4:
            bm = bmesh.new()
            h = rnd.uniform(0.22, 0.33)
            bm_limb(bm, (0, 0, 0), (0, 0, h * 0.7), 0.035, 0.035, seg=10)
            bm_limb(bm, (0, 0, h * 0.7), (0, 0, h), 0.03, 0.012, seg=10)
            ob = new_object("BOTTLE_UNLABELLED_%d_%02d" % (k, i), mesh_from_bm("BOTTLE_%d_%d" % (k, i), bm), C, [rnd.choice(bottle_mats)])
            ob.location = (x, 17.75, z + 0.02)
            x += rnd.uniform(0.11, 0.2)
            i += 1
    # stools: one foreground stool sits between CAM_08 and the elephant (occlusion)
    stools = [(-2.3, 15.3), (-1.0, 15.3), (0.3, 15.3), (4.7, 15.3), (5.8, 15.25), (1.18, 13.37)]
    for i, (x, y) in enumerate(stools):
        bm = bmesh.new()
        bm_limb(bm, (x, y, 0.0), (x, y, 0.03), 0.22, 0.2, seg=20)
        bm_limb(bm, (x, y, 0.03), (x, y, 0.72), 0.03, 0.03, seg=12)
        bm_limb(bm, (x, y, 0.72), (x, y, 0.78), 0.2, 0.2, seg=20)
        bm_limb(bm, (x, y, 0.3), (x, y, 0.33), 0.17, 0.17, seg=20)
        nm = "BAR_STOOL_FOREGROUND" if i == len(stools) - 1 else "BAR_STOOL_%02d" % (i + 1)
        ob = new_object(nm, mesh_from_bm(nm, bm), P, [metal])
        bm = bmesh.new()
        bm_limb(bm, (x, y, 0.77), (x, y, 0.84), 0.21, 0.2, seg=20)
        new_object(nm + "_SEAT", mesh_from_bm(nm + "_SEAT", bm), P, [seat])
    for i, (x, y) in enumerate([(-7.3, 17.2), (7.3, 17.2), (-7.3, 6.0), (7.3, 6.0)]):
        box_object("SPEAKER_STACK_%02d" % (i + 1), (0.7, 0.6, 1.8), (x, y, 0.9), C, speaker, bevel=0.02)
    for i, x in enumerate((-4.0, 0.0, 4.0)):
        box_object("CEILING_TRUSS_%02d" % (i + 1), (0.12, 12, 0.12), (x, 11.5, 3.9), C, metal)
    bm = bmesh.new()
    bm_ellipsoid(bm, (0.28,) * 3, (0, 0, 0), seg=24, rings=14)
    ob = new_object("MIRROR_BALL", mesh_from_bm("MIRROR_BALL", bm), C, [principled("MAT_MIRROR_BALL", "#C8C8C8", rough=0.12, metal=1.0)])
    ob.location = (-1.0, 11.0, 3.4)


def build_lights(cols):
    L = cols["LIGHTING"]

    def light(name, kind, loc, energy, color, size=0.1, rot=None, spot=None, shadow=True):
        ld = bpy.data.lights.new(name, kind)
        ld.energy = energy
        ld.color = color
        ld.use_shadow = shadow
        if kind == "AREA":
            ld.shape = "RECTANGLE"
            ld.size, ld.size_y = size if isinstance(size, tuple) else (size, size)
        elif kind in ("POINT", "SPOT"):
            ld.shadow_soft_size = size
        if kind == "SPOT" and spot:
            ld.spot_size = radians(spot)
            ld.spot_blend = 0.6
        ob = bpy.data.objects.new(name, ld)
        L.objects.link(ob)
        ob.location = loc
        if rot:
            ob.rotation_euler = rot
        return ob

    def aim(ob, target):
        d = Vector(target) - ob.location
        ob.rotation_euler = d.to_track_quat("-Z", "Y").to_euler()

    warm = (1.0, 0.66, 0.36)
    light("KEY_DOOR_PRACTICAL_WARM", "POINT", (0, -0.36, 2.6), 140, warm, 0.06)
    for i, x in enumerate((-3.2, 3.6)):
        light("PRACTICAL_SCONCE_%02d" % (i + 1), "POINT", (x, -0.22, 2.3), 28, warm, 0.04)
    a = light("FILL_NEON_BLUE_CAMLEFT", "AREA", (-6.5, -4.8, 3.0), 420, (0.24, 0.42, 1.0), (2.5, 0.35))
    aim(a, (0.2, -0.8, 1.2))
    light("NEON_BLUE_SPILL", "POINT", (-3.1, -0.35, 3.25), 45, (0.25, 0.42, 1.0), 0.3)
    light("NEON_RED_SPILL", "POINT", (3.1, -0.35, 3.3), 35, (1.0, 0.14, 0.18), 0.25)
    s = light("STREETLIGHT_SODIUM_EAST", "SPOT", (9.5, -4.2, 6.5), 1800, (1.0, 0.58, 0.28), 0.15, spot=75)
    aim(s, (6.0, -2.0, 0.0))
    s = light("STREETLIGHT_SODIUM_WEST", "SPOT", (-13.0, -4.2, 6.5), 1500, (1.0, 0.58, 0.28), 0.15, spot=75)
    aim(s, (-10.0, -2.0, 0.0))
    a = light("RIM_COOL_SKY_BOUNCE", "AREA", (2.0, -9.0, 7.0), 300, (0.45, 0.55, 0.8), (8.0, 3.0))
    aim(a, (0, -1, 1))
    # interior: muted magenta, warm bar, cool back rim
    for i, (x, y) in enumerate([(-3.5, 8.5), (1.5, 12.8), (-1.5, 15.0), (4.5, 9.0)]):
        a = light("CLUB_MAGENTA_AREA_%02d" % (i + 1), "AREA", (x, y, 4.0), 150, (1.0, 0.22, 0.68), (1.5, 1.5))
        aim(a, (x, y, 0))
    light("CORRIDOR_MAGENTA_01", "POINT", (0, 1.6, 2.4), 30, (1.0, 0.25, 0.7), 0.1)
    light("CORRIDOR_MAGENTA_02", "POINT", (0, 3.8, 2.4), 30, (1.0, 0.25, 0.7), 0.1)
    a = light("BAR_WARM_TOPLIGHT", "AREA", (1.5, 16.0, 3.0), 260, warm, (6.0, 0.8))
    aim(a, (1.5, 16.0, 0))
    s = light("CLUB_COOL_BACK_RIM", "SPOT", (-6.5, 17.0, 3.6), 380, (0.35, 0.5, 1.0), 0.2, spot=55)
    aim(s, (-0.6, 10.8, 1.5))
    a = light("CLUB_HERO_NEUTRAL_KEY", "AREA", (0.6, 9.0, 2.4), 30, (1.0, 0.97, 0.94), (0.6, 0.6))
    aim(a, (-0.6, 10.8, 1.7))
    a = light("ELEPHANT_CONTACT_TOP", "AREA", (3.0, 14.2, 3.9), 260, (1.0, 0.85, 0.9), (1.2, 1.2))
    aim(a, (3.0, 14.4, 0))

    w = bpy.data.worlds.new("WORLD_MUMBAI_NIGHT")
    w.use_nodes = True
    bg = w.node_tree.nodes["Background"]
    bg.inputs["Color"].default_value = (0.006, 0.008, 0.016, 1)
    bg.inputs["Strength"].default_value = 1.0
    bpy.context.scene.world = w
