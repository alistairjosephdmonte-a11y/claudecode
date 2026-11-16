"""Builds the apartment from the traced plan (plan_trace.py) and saves scenes/residence_master.blend.

    blender -b --factory-startup --python scripts/build_residence.py

All geometry is generated from the pixel trace in plan_trace.py. Wall thickness, heights and door/window
heights come from plan_trace.PARAMS, so changing a value there and re-running this script rebuilds the model.
Furniture is procedural, at real-world sizes, placed from the furniture drawn on the plan."""

import math
import os
import sys

import bmesh
import bpy
from mathutils import Matrix, Vector

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import plan_trace as T  # noqa: E402

P = T.PARAMS
S = T.PX_PER_M
FZ = P["floor_finish"]                       # finished floor level
H = P["wall_h"]
OUT_BLEND = os.path.join(ROOT, "scenes", "residence_master.blend")
OUT_PATHS = os.path.join(ROOT, "scenes", "walkthrough_camera_paths.blend")

# location and time used for the sun (provisional; see UNCERTAINTIES)
SITE = dict(lat=19.02, lon=72.84, utc_offset=5.5, month=1, day=20, hour=15.5)
CCT_PRACTICAL = 3000


def X(px):
    return T.mx(px)


def Y(py):
    return T.my(py)


def XY(px, py):
    return Vector((X(px), Y(py)))


# ======================================================================== scene helpers
COLLS = ["ARCH_Exterior_Walls", "ARCH_Interior_Walls", "ARCH_Floors", "ARCH_Ceilings", "ARCH_Doors",
         "ARCH_Windows", "ARCH_Columns", "ARCH_Skirting", "ROOM_Living", "ROOM_Dining", "ROOM_Master",
         "ROOM_Bedroom_01", "ROOM_Bedroom_02", "ROOM_Kitchen", "ROOM_Utility", "ROOM_Bathrooms",
         "LIGHTS_Daylight", "LIGHTS_Interior", "CAMERAS_Still", "CAMERAS_Animation", "REFERENCE_FloorPlan",
         "CONTEXT_Core", "CONTEXT_City"]


def coll(name):
    c = bpy.data.collections.get(name)
    if c is None:
        c = bpy.data.collections.new(name)
        bpy.context.scene.collection.children.link(c)
    return c


def link(ob, cname):
    coll(cname).objects.link(ob)
    return ob


def mesh_obj(name, bm, cname, mat=None):
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new(name, me)
    if mat is not None:
        ob.data.materials.append(mat)
    return link(ob, cname)


def bm_box(bm, x0, x1, y0, y1, z0, z1):
    vs = [bm.verts.new(v) for v in ((x0, y0, z0), (x1, y0, z0), (x1, y1, z0), (x0, y1, z0),
                                    (x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1))]
    for f in ((0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)):
        bm.faces.new([vs[i] for i in f])


def bm_prism(bm, poly, z0, z1):
    """Extrude a CCW or CW 2D polygon into a closed prism."""
    if sum((poly[i][0] * poly[(i + 1) % len(poly)][1] - poly[(i + 1) % len(poly)][0] * poly[i][1])
           for i in range(len(poly))) < 0:
        poly = poly[::-1]
    lo = [bm.verts.new((x, y, z0)) for x, y in poly]
    hi = [bm.verts.new((x, y, z1)) for x, y in poly]
    bm.faces.new(lo[::-1])
    bm.faces.new(hi)
    n = len(poly)
    for i in range(n):
        j = (i + 1) % n
        bm.faces.new((lo[i], lo[j], hi[j], hi[i]))


def box(name, size, loc, mat, cname, rot=0.0, bevel=0.0, seg=2, base=True):
    """Box of size (sx, sy, sz); loc is the base centre (base=True) or the centre."""
    sx, sy, sz = size
    bm = bmesh.new()
    bm_box(bm, -sx / 2, sx / 2, -sy / 2, sy / 2, 0 if base else -sz / 2, sz if base else sz / 2)
    ob = mesh_obj(name, bm, cname, mat)
    ob.location = loc
    ob.rotation_euler.z = rot
    if bevel:
        md = ob.modifiers.new("Bevel", "BEVEL")
        md.width = bevel
        md.segments = seg
        md.limit_method = "ANGLE"
    return ob


def cyl(name, r, h, loc, mat, cname, n=32, sx=1.0, sy=1.0, bevel=0.0, rot=0.0):
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, segments=n, radius1=r, radius2=r, depth=h,
                          matrix=Matrix.Translation((0, 0, h / 2)))
    for v in bm.verts:
        v.co.x *= sx
        v.co.y *= sy
    ob = mesh_obj(name, bm, cname, mat)
    ob.location = loc
    ob.rotation_euler.z = rot
    if bevel:
        md = ob.modifiers.new("Bevel", "BEVEL")
        md.width = bevel
        md.segments = 3
        md.limit_method = "ANGLE"
    return ob


def sphere(name, r, loc, mat, cname, scale=(1, 1, 1)):
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=24, v_segments=12, radius=r)
    ob = mesh_obj(name, bm, cname, mat)
    ob.location = loc
    ob.scale = scale
    for p in ob.data.polygons:
        p.use_smooth = True
    return ob


def empty(name, loc, cname, kind="PLAIN_AXES", size=0.3):
    e = bpy.data.objects.new(name, None)
    e.empty_display_type = kind
    e.empty_display_size = size
    e.location = loc
    return link(e, cname)


def kelvin_rgb(k):
    """Approximate linear RGB of a blackbody (Tanner Helland fit, then sRGB -> linear)."""
    t = k / 100.0
    r = 255 if t <= 66 else 329.698727446 * (t - 60) ** -0.1332047592
    g = 99.4708025861 * math.log(t) - 161.1195681661 if t <= 66 else 288.1221695283 * (t - 60) ** -0.0755148492
    b = 255 if t >= 66 else (0 if t <= 19 else 138.5177312231 * math.log(t - 10) - 305.0447927307)

    def lin(c):
        c = min(max(c, 0), 255) / 255
        return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
    return (lin(r), lin(g), lin(b))


def light(name, kind, loc, power, cname, color_k=CCT_PRACTICAL, size=0.1, spot=None, rot=(0, 0, 0)):
    ld = bpy.data.lights.new(name, kind)
    ld.energy = power
    ld.color = kelvin_rgb(color_k)
    if kind in ("POINT", "SPOT"):
        ld.shadow_soft_size = size
    if kind == "SPOT" and spot:
        ld.spot_size = math.radians(spot)
        ld.spot_blend = 0.6
    if kind == "AREA":
        ld.shape = "RECTANGLE"
        ld.size, ld.size_y = size if isinstance(size, tuple) else (size, size)
    ob = bpy.data.objects.new(name, ld)
    ob.location = loc
    ob.rotation_euler = rot
    return link(ob, cname)


# ======================================================================== materials
MAT = {}


def _mat(name):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    return m, nt.nodes, nt.links, nt.nodes["Principled BSDF"]


def _set(b, **kw):
    names = dict(base="Base Color", rough="Roughness", metal="Metallic", ior="IOR", trans="Transmission Weight",
                 coat="Coat Weight", coat_rough="Coat Roughness", sheen="Sheen Weight", sheen_rough="Sheen Roughness",
                 aniso="Anisotropic", spec="Specular IOR Level", sss="Subsurface Weight", alpha="Alpha")
    for k, v in kw.items():
        sock = b.inputs[names[k]]
        sock.default_value = (*v, 1.0) if k == "base" else v


def _coords(n, scale=1.0):
    tc = n.new("ShaderNodeTexCoord")
    mp = n.new("ShaderNodeMapping")
    mp.inputs["Scale"].default_value = (scale, scale, scale)
    n.id_data.links.new(tc.outputs["Object"], mp.inputs["Vector"])
    return mp


def _ramp(n, a, b_, pos=(0.0, 1.0)):
    r = n.new("ShaderNodeValToRGB")
    r.color_ramp.elements[0].position, r.color_ramp.elements[1].position = pos
    r.color_ramp.elements[0].color = (*a, 1)
    r.color_ramp.elements[1].color = (*b_, 1)
    return r


def _bump(n, l, height_out, b, strength, dist=0.002):
    bp = n.new("ShaderNodeBump")
    bp.inputs["Strength"].default_value = strength
    bp.inputs["Distance"].default_value = dist
    l.new(height_out, bp.inputs["Height"])
    l.new(bp.outputs["Normal"], b.inputs["Normal"])


def mat_wood(name, c0, c1, rough, plank=None):
    """Wood grain along local X. With plank=(length, width) it is laid as staggered planks with seams."""
    m, n, l, b = _mat(name)
    mp = _coords(n)
    grain_map = n.new("ShaderNodeMapping")
    grain_map.inputs["Scale"].default_value = (0.12, 1.6, 1.6)
    l.new(mp.outputs[0], grain_map.inputs["Vector"])
    wave = n.new("ShaderNodeTexWave")             # rings around local X: grain runs along the long X axis
    wave.wave_type = "RINGS"
    wave.rings_direction = "X"
    wave.inputs["Scale"].default_value = 3.0
    wave.inputs["Distortion"].default_value = 7.0
    wave.inputs["Detail"].default_value = 4.0
    wave.inputs["Detail Scale"].default_value = 1.5
    l.new(grain_map.outputs[0], wave.inputs["Vector"])
    noise = n.new("ShaderNodeTexNoise")
    noise.inputs["Scale"].default_value = 3.0
    l.new(mp.outputs[0], noise.inputs["Vector"])
    mix = n.new("ShaderNodeMix")
    mix.data_type = "FLOAT"
    mix.inputs["Factor"].default_value = 0.35
    l.new(wave.outputs["Fac"], mix.inputs["A"])
    l.new(noise.outputs["Fac"], mix.inputs["B"])
    ramp = _ramp(n, c0, c1, (0.25, 0.85))
    l.new(mix.outputs["Result"], ramp.inputs["Fac"])
    col_out = ramp.outputs["Color"]
    height = wave.outputs["Fac"]
    if plank:
        brick = n.new("ShaderNodeTexBrick")
        brick.offset = 0.37
        brick.inputs["Scale"].default_value = 1.0
        brick.inputs["Mortar Size"].default_value = 0.0015
        brick.inputs["Mortar Smooth"].default_value = 0.2
        brick.inputs["Brick Width"].default_value = plank[0]
        brick.inputs["Row Height"].default_value = plank[1]
        brick.inputs["Bias"].default_value = 0.0
        brick.inputs["Color1"].default_value = (1, 1, 1, 1)
        brick.inputs["Color2"].default_value = (0.82, 0.82, 0.82, 1)
        brick.inputs["Mortar"].default_value = (0.25, 0.25, 0.25, 1)
        l.new(mp.outputs[0], brick.inputs["Vector"])
        tint = n.new("ShaderNodeMix")
        tint.data_type = "RGBA"
        tint.blend_type = "MULTIPLY"
        tint.inputs["Factor"].default_value = 1.0
        l.new(col_out, tint.inputs["A"])
        l.new(brick.outputs["Color"], tint.inputs["B"])
        col_out = tint.outputs["Result"]
        seam = n.new("ShaderNodeMath")
        seam.operation = "ADD"
        l.new(wave.outputs["Fac"], seam.inputs[0])
        sc = n.new("ShaderNodeMath")
        sc.operation = "MULTIPLY"
        sc.inputs[1].default_value = 4.0
        l.new(brick.outputs["Fac"], sc.inputs[0])
        l.new(sc.outputs[0], seam.inputs[1])
        height = seam.outputs[0]
    l.new(col_out, b.inputs["Base Color"])
    rr = n.new("ShaderNodeMapRange")
    rr.inputs["To Min"].default_value = rough - 0.08
    rr.inputs["To Max"].default_value = rough + 0.08
    l.new(wave.outputs["Fac"], rr.inputs["Value"])
    l.new(rr.outputs["Result"], b.inputs["Roughness"])
    _set(b, coat=0.15, coat_rough=0.35)
    _bump(n, l, height, b, 0.12)
    m.diffuse_color = (*c1, 1)
    return m


def mat_stone(name, base_a, base_b, rough, tile=None, vein=0.0, bump=0.05):
    """Stone: mottled noise, optional wavy veining (travertine banding) and tile grout."""
    m, n, l, b = _mat(name)
    mp = _coords(n)
    noise = n.new("ShaderNodeTexNoise")
    noise.inputs["Scale"].default_value = 2.2
    noise.inputs["Detail"].default_value = 8.0
    noise.inputs["Roughness"].default_value = 0.6
    l.new(mp.outputs[0], noise.inputs["Vector"])
    ramp = _ramp(n, base_a, base_b, (0.3, 0.75))
    fac = noise.outputs["Fac"]
    if vein:
        vm = n.new("ShaderNodeMapping")
        vm.inputs["Scale"].default_value = (1.0, 3.5, 1.0)
        l.new(mp.outputs[0], vm.inputs["Vector"])
        wave = n.new("ShaderNodeTexWave")
        wave.bands_direction = "Y"
        wave.inputs["Scale"].default_value = 1.6
        wave.inputs["Distortion"].default_value = 5.0
        wave.inputs["Detail"].default_value = 6.0
        l.new(vm.outputs[0], wave.inputs["Vector"])
        mx = n.new("ShaderNodeMix")
        mx.data_type = "FLOAT"
        mx.inputs["Factor"].default_value = vein
        l.new(noise.outputs["Fac"], mx.inputs["A"])
        l.new(wave.outputs["Fac"], mx.inputs["B"])
        fac = mx.outputs["Result"]
    l.new(fac, ramp.inputs["Fac"])
    col = ramp.outputs["Color"]
    height = fac
    if tile:
        brick = n.new("ShaderNodeTexBrick")
        brick.offset = 0.5 if tile[0] != tile[1] else 0.0
        brick.inputs["Scale"].default_value = 1.0
        brick.inputs["Mortar Size"].default_value = 0.002
        brick.inputs["Brick Width"].default_value = tile[0]
        brick.inputs["Row Height"].default_value = tile[1]
        brick.inputs["Color1"].default_value = (1, 1, 1, 1)
        brick.inputs["Color2"].default_value = (0.93, 0.93, 0.93, 1)
        brick.inputs["Mortar"].default_value = (0.55, 0.53, 0.5, 1)
        l.new(mp.outputs[0], brick.inputs["Vector"])
        mul = n.new("ShaderNodeMix")
        mul.data_type = "RGBA"
        mul.blend_type = "MULTIPLY"
        mul.inputs["Factor"].default_value = 1.0
        l.new(col, mul.inputs["A"])
        l.new(brick.outputs["Color"], mul.inputs["B"])
        col = mul.outputs["Result"]
        hh = n.new("ShaderNodeMath")
        hh.operation = "SUBTRACT"
        l.new(fac, hh.inputs[0])
        l.new(brick.outputs["Fac"], hh.inputs[1])
        height = hh.outputs[0]
    l.new(col, b.inputs["Base Color"])
    _set(b, rough=rough)
    _bump(n, l, height, b, bump)
    m.diffuse_color = (*base_b, 1)
    return m


def mat_fabric(name, col, rough=0.9, sheen=0.4, kind="linen", scale=900.0):
    m, n, l, b = _mat(name)
    mp = _coords(n)
    if kind == "boucle":
        tex = n.new("ShaderNodeTexVoronoi")
        tex.feature = "SMOOTH_F1"
        tex.inputs["Scale"].default_value = 260.0
        out = tex.outputs["Distance"]
        strength = 0.35
    else:
        tex = n.new("ShaderNodeTexWave")
        tex.wave_type = "RINGS" if kind == "wool" else "BANDS"
        tex.inputs["Scale"].default_value = scale
        tex.inputs["Distortion"].default_value = 2.0
        out = tex.outputs["Fac"]
        strength = 0.15
    l.new(mp.outputs[0], tex.inputs["Vector"])
    noise = n.new("ShaderNodeTexNoise")
    noise.inputs["Scale"].default_value = 12.0
    l.new(mp.outputs[0], noise.inputs["Vector"])
    ramp = _ramp(n, tuple(c * 0.86 for c in col), col, (0.2, 0.8))
    l.new(noise.outputs["Fac"], ramp.inputs["Fac"])
    l.new(ramp.outputs["Color"], b.inputs["Base Color"])
    _set(b, rough=rough, sheen=sheen, sheen_rough=0.5, spec=0.3)
    _bump(n, l, out, b, strength, 0.001)
    m.diffuse_color = (*col, 1)
    return m


def mat_plain(name, col, rough=0.5, metal=0.0, aniso=0.0, coat=0.0, trans=0.0, ior=1.5, emit=None):
    m, n, l, b = _mat(name)
    _set(b, base=col, rough=rough, metal=metal, aniso=aniso, coat=coat, trans=trans, ior=ior)
    if emit:
        b.inputs["Emission Color"].default_value = (*emit[0], 1)
        b.inputs["Emission Strength"].default_value = emit[1]
    m.diffuse_color = (*col, 1)
    return m


def mat_glass(name):
    """Clear glass, IOR 1.52. Shadow and diffuse rays see it as a thin transparent sheet so sun and sky light
    pass through windows without caustics (Cycles cannot sample light through refraction efficiently)."""
    m, n, l, b = _mat(name)
    _set(b, base=(0.96, 0.99, 0.98), rough=0.0, trans=1.0, ior=1.52)
    tr = n.new("ShaderNodeBsdfTransparent")
    tr.inputs["Color"].default_value = (0.90, 0.93, 0.92, 1)
    lp = n.new("ShaderNodeLightPath")
    mx = n.new("ShaderNodeMath")
    mx.operation = "MAXIMUM"
    l.new(lp.outputs["Is Shadow Ray"], mx.inputs[0])
    l.new(lp.outputs["Is Diffuse Ray"], mx.inputs[1])
    mix = n.new("ShaderNodeMixShader")
    l.new(mx.outputs[0], mix.inputs["Fac"])
    l.new(b.outputs[0], mix.inputs[1])
    l.new(tr.outputs[0], mix.inputs[2])
    out = n["Material Output"]
    l.new(mix.outputs[0], out.inputs["Surface"])
    m.diffuse_color = (0.8, 0.9, 0.9, 0.3)
    return m


def build_materials():
    MAT["MAT_Warm_Oak"] = mat_wood("MAT_Warm_Oak", (0.36, 0.22, 0.12), (0.58, 0.40, 0.24), 0.42, plank=(1.2, 0.19))
    MAT["MAT_Walnut"] = mat_wood("MAT_Walnut", (0.13, 0.075, 0.04), (0.22, 0.13, 0.075), 0.38)
    m, n, l, b = _mat("MAT_Ivory_Plaster")
    mp = _coords(n)
    nz = n.new("ShaderNodeTexNoise")
    nz.inputs["Scale"].default_value = 35.0
    nz.inputs["Detail"].default_value = 10.0
    l.new(mp.outputs[0], nz.inputs["Vector"])
    rp = _ramp(n, (0.74, 0.70, 0.63), (0.80, 0.76, 0.69), (0.35, 0.7))
    l.new(nz.outputs["Fac"], rp.inputs["Fac"])
    l.new(rp.outputs["Color"], b.inputs["Base Color"])
    _set(b, rough=0.88, spec=0.35)
    _bump(n, l, nz.outputs["Fac"], b, 0.04)
    m.diffuse_color = (0.8, 0.76, 0.69, 1)
    MAT["MAT_Ivory_Plaster"] = m
    MAT["MAT_Travertine"] = mat_stone("MAT_Travertine", (0.66, 0.60, 0.51), (0.80, 0.75, 0.66), 0.32,
                                      tile=(1.2, 0.6), vein=0.55, bump=0.04)
    MAT["MAT_Greige_Stone"] = mat_stone("MAT_Greige_Stone", (0.45, 0.42, 0.38), (0.58, 0.55, 0.50), 0.38,
                                        tile=(0.6, 0.6), bump=0.03)
    MAT["MAT_Brushed_Bronze"] = mat_plain("MAT_Brushed_Bronze", (0.42, 0.29, 0.17), rough=0.3, metal=1.0, aniso=0.6)
    MAT["MAT_Linen"] = mat_fabric("MAT_Linen", (0.80, 0.77, 0.71), 0.92, 0.3, "linen")
    MAT["MAT_Boucle"] = mat_fabric("MAT_Boucle", (0.84, 0.81, 0.75), 1.0, 0.6, "boucle")
    MAT["MAT_Clear_Glass"] = mat_glass("MAT_Clear_Glass")
    MAT["MAT_Ceramic_White"] = mat_plain("MAT_Ceramic_White", (0.86, 0.86, 0.84), rough=0.08, coat=0.6)
    MAT["MAT_Quartz"] = mat_stone("MAT_Quartz", (0.78, 0.77, 0.75), (0.90, 0.89, 0.87), 0.14, vein=0.25, bump=0.0)
    MAT["MAT_Warm_Metal"] = mat_plain("MAT_Warm_Metal", (0.70, 0.56, 0.38), rough=0.25, metal=1.0)
    # supporting finishes (not in the brief's list, kept separate so the listed set stays untouched)
    MAT["MAT_Frame_Charcoal"] = mat_plain("MAT_Frame_Charcoal", (0.035, 0.034, 0.033), rough=0.45, metal=0.6)
    MAT["MAT_Sage_Throw"] = mat_fabric("MAT_Sage_Throw", (0.20, 0.25, 0.16), 0.95, 0.5, "wool", 600)
    MAT["MAT_Rug_Wool"] = mat_fabric("MAT_Rug_Wool", (0.62, 0.58, 0.52), 1.0, 0.4, "wool", 400)
    MAT["MAT_Foliage"] = mat_plain("MAT_Foliage", (0.05, 0.14, 0.04), rough=0.55)
    MAT["MAT_Lamp_Shade"] = mat_plain("MAT_Lamp_Shade", (0.92, 0.86, 0.74), rough=0.9)
    MAT["MAT_Lamp_Shade"].node_tree.nodes["Principled BSDF"].inputs["Transmission Weight"].default_value = 0.35
    MAT["MAT_TV_Black"] = mat_plain("MAT_TV_Black", (0.008, 0.008, 0.009), rough=0.12, coat=1.0)
    MAT["MAT_Mirror"] = mat_plain("MAT_Mirror", (0.92, 0.92, 0.92), rough=0.01, metal=1.0)
    MAT["MAT_Concrete_Slab"] = mat_plain("MAT_Concrete_Slab", (0.42, 0.41, 0.40), rough=0.8)
    MAT["MAT_Lift_Steel"] = mat_plain("MAT_Lift_Steel", (0.55, 0.55, 0.55), rough=0.3, metal=1.0, aniso=0.5)
    MAT["MAT_Appliance_Steel"] = mat_plain("MAT_Appliance_Steel", (0.62, 0.62, 0.61), rough=0.25, metal=1.0, aniso=0.5)
    MAT["MAT_Terracotta"] = mat_plain("MAT_Terracotta", (0.42, 0.24, 0.15), rough=0.8)
    MAT["MAT_Pillow_Olive"] = mat_fabric("MAT_Pillow_Olive", (0.24, 0.27, 0.15), 0.9, 0.4, "linen")
    MAT["MAT_Reference"] = None


# ======================================================================== walls
OPENINGS = []          # every door/window opening: dict(id, kind, wall, axis, line_m, a, b, z0, z1, centre, t)
WALL_OBS = []


def wall_rect(w):
    """Wall footprint in px (x0, y0, x1, y1), its axis and thickness in metres."""
    if w["kind"] == "core":
        x0, y0, x1, y1 = w["rect"]
        axis = "h" if (x1 - x0) >= (y1 - y0) else "v"
        return (x0, y0, x1, y1), axis
    t = (P["ext_t"] if w["kind"] == "ext" else P["int_t"]) * S
    if w["kind"] == "ext":
        a, b = sorted((w["line"], w["line"] + w["side"] * t))
        e0, e1 = (c * t for c in w.get("corners", (0, 0)))   # carry the wall through convex corners
    else:
        a, b = w["line"] - t / 2, w["line"] + t / 2
        e0 = e1 = 0.0
    s0, s1 = w["span"]
    if w["axis"] == "h":
        return (s0 - e0, a, s1 + e1, b), "h"
    return (a, s0 - e0, b, s1 + e1), "v"


def build_walls():
    for w in T.WALLS:
        (x0, y0, x1, y1), axis = wall_rect(w)
        X0, X1, Y0, Y1 = X(x0), X(x1), Y(y1), Y(y0)
        along = (X0, X1) if axis == "h" else (Y0, Y1)
        ops = []
        for (o0, o1, kind, oid) in w.get("openings", []):
            a, b = (X(o0), X(o1)) if axis == "h" else sorted((Y(o0), Y(o1)))
            z0, z1 = (P["sill_h"], P["head_h"]) if kind == "window" else \
                (0.0, P["entry_door_h"] if kind == "entry" else P["door_h"])
            ops.append((a, b, z0, z1, kind, oid))
            OPENINGS.append(dict(id=oid, kind=kind, wall=w["name"], axis=axis, a=a, b=b, z0=z0, z1=z1,
                                 c0=(Y0 if axis == "h" else X0), c1=(Y1 if axis == "h" else X1)))
        ops.sort()
        bm = bmesh.new()

        def piece(a, b, z0, z1):
            if b - a < 1e-4 or z1 - z0 < 1e-4:
                return
            if axis == "h":
                bm_box(bm, a, b, Y0, Y1, z0, z1)
            else:
                bm_box(bm, X0, X1, a, b, z0, z1)
        cur = along[0]
        for a, b, z0, z1, kind, oid in ops:
            piece(cur, a, 0, H)
            piece(a, b, 0, z0)
            piece(a, b, z1, H)
            cur = b
        piece(cur, along[1], 0, H)
        bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-5)
        cname = "ARCH_Interior_Walls" if w["kind"] == "int" else "ARCH_Exterior_Walls"
        ob = mesh_obj("WALL_" + w["name"], bm, cname, MAT["MAT_Ivory_Plaster"])
        ob["wall_kind"] = w["kind"]
        ob["thickness_m"] = round((Y1 - Y0) if axis == "h" else (X1 - X0), 4)
        WALL_OBS.append(ob)
    for c in T.COLUMNS:
        x0, y0, x1, y1 = c["rect"]
        bm = bmesh.new()
        bm_box(bm, X(x0), X(x1), Y(y1), Y(y0), 0, H)
        ob = mesh_obj(c["name"], bm, "ARCH_Columns", MAT["MAT_Ivory_Plaster"])
        WALL_OBS.append(ob)
    for c in T.CONTEXT:
        x0, y0, x1, y1 = c["rect"]
        bm = bmesh.new()
        bm_box(bm, X(x0), X(x1), Y(y1), Y(y0), 0, H)
        mesh_obj(c["name"], bm, "CONTEXT_Core", MAT["MAT_Ivory_Plaster"])


def wall_face_hit(pt, pad=0.0):
    """True if the 2D point lies inside any apartment wall/column footprint (px rect test in metres)."""
    for w in T.WALLS:
        (x0, y0, x1, y1), _ = wall_rect(w)
        if X(x0) - pad <= pt[0] <= X(x1) + pad and Y(y1) - pad <= pt[1] <= Y(y0) + pad:
            return w
    for c in T.COLUMNS:
        x0, y0, x1, y1 = c["rect"]
        if X(x0) <= pt[0] <= X(x1) and Y(y1) <= pt[1] <= Y(y0):
            return c
    return None


# ======================================================================== floors, ceilings, slab, skirting
def room_poly_m(name):
    return [(X(x), Y(y)) for x, y in T.ROOMS[name]["poly"]]


def build_floors_ceilings():
    for name, r in T.ROOMS.items():
        bm = bmesh.new()
        bm_prism(bm, room_poly_m(name), 0.001, FZ)
        ob = mesh_obj("FLOOR_" + name, bm, "ARCH_Floors", MAT[r["floor"]])
        ob["room"] = name
        bm = bmesh.new()
        bm_prism(bm, room_poly_m(name), H, H + 0.12)
        ob = mesh_obj("CEILING_" + name, bm, "ARCH_Ceilings", MAT["MAT_Ivory_Plaster"])
        ob["room"] = name
    bm = bmesh.new()
    bm_prism(bm, [(X(x), Y(y)) for x, y in T.FOYER], 0.001, FZ)
    mesh_obj("FLOOR_FOYER_context", bm, "CONTEXT_Core", MAT["MAT_Travertine"])
    # floor fill under the wall bases and openings so door thresholds have a surface
    for o in OPENINGS:
        if o["kind"] == "window":
            continue
        bm = bmesh.new()
        if o["axis"] == "h":
            bm_box(bm, o["a"], o["b"], o["c0"], o["c1"], 0.001, FZ)
        else:
            bm_box(bm, o["c0"], o["c1"], o["a"], o["b"], 0.001, FZ)
        mesh_obj("FLOOR_threshold_" + o["id"], bm, "ARCH_Floors", MAT["MAT_Quartz"])
    # structural slab under the whole floor plate (outer faces of the envelope, px)
    e, i = P["ext_t"] * S, P["int_t"] * S
    outline = [(707 - e, 175 - e), (787, 175 - e), (787, 16), (1130, 16), (1130, 175 - e), (1262 + e, 175 - e),
               (1262 + e, 305 - e), (1348 + e, 305 - e), (1348 + e, 486), (1381, 486), (1381, 551), (1316, 551),
               (1316, 497 + e), (1030, 497 + e), (1030, 624), (1007, 624), (1007, 617 + e), (707 - e, 617 + e)]
    bm = bmesh.new()
    bm_prism(bm, [(X(x), Y(y)) for x, y in outline], -0.30, 0.0)
    mesh_obj("SLAB_Structure", bm, "ARCH_Floors", MAT["MAT_Concrete_Slab"])
    return outline


def build_skirting():
    """Skirting runs wherever a room edge sits against a wall, minus door openings."""
    hgt, th, step = 0.08, 0.012, 0.02
    for name in ("DINING", "LIVING", "PASSAGE", "BEDROOM_1", "BEDROOM_2", "MASTER_BEDROOM"):   # dry rooms only
        poly = room_poly_m(name)
        n = len(poly)
        area = sum(poly[k][0] * poly[(k + 1) % n][1] - poly[(k + 1) % n][0] * poly[k][1] for k in range(n))
        bm = bmesh.new()
        for k in range(n):
            a, b = Vector(poly[k]), Vector(poly[(k + 1) % n])
            d = b - a
            L = d.length
            d.normalize()
            out = Vector((d.y, -d.x)) if area > 0 else Vector((-d.y, d.x))   # outward normal
            runs, cur = [], None
            steps = max(1, int(L / step))
            for s in range(steps + 1):
                t = s / steps * L
                p = a + d * t
                on_wall = wall_face_hit(p + out * 0.09) is not None and not in_door(p + out * 0.05)
                if on_wall and cur is None:
                    cur = t
                if (not on_wall or s == steps) and cur is not None:
                    if t - cur > 0.05:
                        runs.append((cur, t))
                    cur = None
            for t0, t1 in runs:
                p0, p1 = a + d * t0, a + d * t1
                q0, q1 = p0 - out * th, p1 - out * th
                vs = [bm.verts.new((*v, z)) for z in (FZ, FZ + hgt) for v in (p0, p1, q1, q0)]
                for f in ((0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)):
                    bm.faces.new([vs[i] for i in f])
        if bm.verts:
            mesh_obj("SKIRTING_" + name, bm, "ARCH_Skirting", MAT["MAT_Walnut"])
        else:
            bm.free()


def in_door(pt):
    for o in OPENINGS:
        if o["kind"] == "window":
            continue
        if o["axis"] == "h":
            if o["a"] - 0.01 <= pt[0] <= o["b"] + 0.01 and o["c0"] - 0.12 <= pt[1] <= o["c1"] + 0.12:
                return True
        elif o["a"] - 0.01 <= pt[1] <= o["b"] + 0.01 and o["c0"] - 0.12 <= pt[0] <= o["c1"] + 0.12:
            return True
    return False


# ======================================================================== doors and windows
DOOR_INFO = {}


def build_doors():
    lining, gap = 0.04, 0.004
    for o in OPENINGS:
        if o["kind"] == "window":
            continue
        d = T.DOORS[o["id"]]
        t = o["c1"] - o["c0"]
        z1 = o["z1"]
        cname = "ARCH_Doors"
        bm = bmesh.new()
        if o["axis"] == "h":
            bm_box(bm, o["a"], o["a"] + lining, o["c0"] - 0.01, o["c1"] + 0.01, FZ, z1)
            bm_box(bm, o["b"] - lining, o["b"], o["c0"] - 0.01, o["c1"] + 0.01, FZ, z1)
            bm_box(bm, o["a"], o["b"], o["c0"] - 0.01, o["c1"] + 0.01, z1 - lining, z1)
        else:
            bm_box(bm, o["c0"] - 0.01, o["c1"] + 0.01, o["a"], o["a"] + lining, FZ, z1)
            bm_box(bm, o["c0"] - 0.01, o["c1"] + 0.01, o["b"] - lining, o["b"], FZ, z1)
            bm_box(bm, o["c0"] - 0.01, o["c1"] + 0.01, o["a"], o["b"], z1 - lining, z1)
        bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-5)
        mesh_obj("DOOR_FRAME_" + o["id"], bm, cname, MAT["MAT_Walnut"])
        width = (o["b"] - o["a"]) - 2 * lining - 2 * gap
        lt = d.get("leaf_t", 0.04)
        into = d["into"]
        # hinge point (plan metres); px +y is metres -y, so flip "into" for horizontal walls
        if o["axis"] == "h":
            n_into = Vector((0, -into))
            face = o["c1"] if n_into.y > 0 else o["c0"]
            hx = o["a"] + lining + gap if d["hinge"] == "a" else o["b"] - lining - gap
            hinge = Vector((hx, face + n_into.y * lt / 2))
            d0 = Vector((1, 0)) if d["hinge"] == "a" else Vector((-1, 0))
        else:
            n_into = Vector((into, 0))
            face = o["c1"] if n_into.x > 0 else o["c0"]
            hy_lo, hy_hi = o["a"], o["b"]          # metres, a < b, but px "a" end is the higher metre value
            hy = hy_hi - lining - gap if d["hinge"] == "a" else hy_lo + lining + gap
            hinge = Vector((face + n_into.x * lt / 2, hy))
            d0 = Vector((0, -1)) if d["hinge"] == "a" else Vector((0, 1))
        ang = math.radians(d.get("open_deg", 82))
        dirv = d0 * math.cos(ang) + n_into * math.sin(ang)
        bm = bmesh.new()
        bm_box(bm, 0, width, -lt / 2, lt / 2, 0.008, z1 - lining - gap)
        leaf = mesh_obj("DOOR_LEAF_" + o["id"], bm, cname, MAT["MAT_Walnut"])
        leaf.location = (hinge.x, hinge.y, FZ)
        leaf.rotation_euler.z = math.atan2(dirv.y, dirv.x)
        md = leaf.modifiers.new("Bevel", "BEVEL")
        md.width = 0.003
        md.segments = 2
        for side in (-1, 1):
            hb = box("DOOR_HANDLE_%s_%s" % (o["id"], "A" if side > 0 else "B"), (0.14, 0.018, 0.018),
                     (width - 0.07 - 0.06, side * (lt / 2 + 0.03), 1.05 - FZ), MAT["MAT_Brushed_Bronze"], cname,
                     base=False)
            hb.parent = leaf
        DOOR_INFO[o["id"]] = dict(hinge=(hinge.x, hinge.y), d0=(d0.x, d0.y), n=(n_into.x, n_into.y),
                                  width=width, room=d["room"], open_deg=d.get("open_deg", 82))


BAY_WINDOWS = {"W_Bedroom1_West", "W_Bedroom1_North", "W_Master_West", "W_Master_South"}


def build_windows():
    fw, fd = 0.06, 0.08                # frame face width and depth
    for o in OPENINGS:
        if o["kind"] != "window":
            continue
        a, b, z0, z1 = o["a"], o["b"], o["z0"], o["z1"]
        cmid = (o["c0"] + o["c1"]) / 2
        L = b - a
        n_bays = max(1, round(L / 1.25))
        bm = bmesh.new()

        def frame_box(u0, u1, w0, w1, z_0, z_1):
            if o["axis"] == "h":
                bm_box(bm, u0, u1, w0, w1, z_0, z_1)
            else:
                bm_box(bm, w0, w1, u0, u1, z_0, z_1)
        c0, c1 = cmid - fd / 2, cmid + fd / 2
        frame_box(a, a + fw, c0, c1, z0, z1)
        frame_box(b - fw, b, c0, c1, z0, z1)
        frame_box(a, b, c0, c1, z0, z0 + fw)
        frame_box(a, b, c0, c1, z1 - fw, z1)
        for k in range(1, n_bays):
            u = a + L * k / n_bays
            frame_box(u - 0.025, u + 0.025, c0, c1, z0, z1)
        mesh_obj("WINDOW_FRAME_" + o["id"], bm, "ARCH_Windows", MAT["MAT_Frame_Charcoal"])
        # double glazing: 6 mm + 12 mm cavity + 6 mm
        bm = bmesh.new()
        for off in (-0.009, 0.009):
            g0, g1 = cmid + off - 0.003, cmid + off + 0.003
            frame_box(a + fw * 0.5, b - fw * 0.5, g0, g1, z0 + fw * 0.5, z1 - fw * 0.5)
        g = mesh_obj("WINDOW_GLASS_" + o["id"], bm, "ARCH_Windows", MAT["MAT_Clear_Glass"])
        g.visible_shadow = True
        # internal quartz sill
        bm = bmesh.new()
        inner = (o["c0"], cmid) if True else None
        frame_box(a, b, min(o["c0"], o["c1"]) - 0.0, max(o["c0"], o["c1"]), z0 - 0.02, z0)
        mesh_obj("WINDOW_SILL_" + o["id"], bm, "ARCH_Windows", MAT["MAT_Quartz"])
        if o["id"] in BAY_WINDOWS:
            build_ledge(o)


def build_ledge(o):
    """0.40 m external planter ledge with a glass guard (the 'X 0.40M' annotation on the drawing)."""
    wall = next(w for w in T.WALLS if w["name"] == o["wall"])
    outward = -1 if wall["side"] < 0 else 1
    # px +y is metres -y
    if o["axis"] == "h":
        outward = -outward
    face = o["c0"] if outward < 0 else o["c1"]
    depth = 0.40
    w0, w1 = sorted((face, face + outward * depth))
    bm = bmesh.new()
    if o["axis"] == "h":
        bm_box(bm, o["a"] - 0.1, o["b"] + 0.1, w0, w1, -0.30, 0.30)
    else:
        bm_box(bm, w0, w1, o["a"] - 0.1, o["b"] + 0.1, -0.30, 0.30)
    mesh_obj("LEDGE_" + o["id"], bm, "ARCH_Windows", MAT["MAT_Ivory_Plaster"])
    edge = face + outward * (depth - 0.02)
    bm = bmesh.new()
    if o["axis"] == "h":
        bm_box(bm, o["a"] - 0.1, o["b"] + 0.1, edge - 0.006, edge + 0.006, 0.30, 1.30)
    else:
        bm_box(bm, edge - 0.006, edge + 0.006, o["a"] - 0.1, o["b"] + 0.1, 0.30, 1.30)
    mesh_obj("LEDGE_GUARD_" + o["id"], bm, "ARCH_Windows", MAT["MAT_Clear_Glass"])
    bm = bmesh.new()
    if o["axis"] == "h":
        bm_box(bm, o["a"] - 0.1, o["b"] + 0.1, edge - 0.02, edge + 0.02, 1.30, 1.34)
    else:
        bm_box(bm, edge - 0.02, edge + 0.02, o["a"] - 0.1, o["b"] + 0.1, 1.30, 1.34)
    mesh_obj("LEDGE_RAIL_" + o["id"], bm, "ARCH_Windows", MAT["MAT_Frame_Charcoal"])
    mid = face + outward * depth / 2
    u = (o["a"] + o["b"]) / 2
    loc = (u, mid, 0.30) if o["axis"] == "h" else (mid, u, 0.30)
    plant("PLANT_Ledge_" + o["id"], loc, "ARCH_Windows", 0.12, 0.45)


# ======================================================================== furniture
def plant(name, loc, cname, r=0.22, h=1.3):
    cyl(name + "_pot", r, r * 1.6, loc, MAT["MAT_Terracotta"], cname, bevel=0.01)
    base = Vector(loc) + Vector((0, 0, r * 1.6))
    for k in range(9):
        a = k * 2.399
        rr = r * (0.3 + 0.5 * ((k * 37) % 10) / 10)
        p = base + Vector((math.cos(a) * rr, math.sin(a) * rr, h * (0.25 + 0.65 * ((k * 53) % 10) / 10)))
        lf = sphere("%s_leaf_%02d" % (name, k), 0.5, p, MAT["MAT_Foliage"], cname, (r * 1.1, r * 0.45, 0.03))
        lf.rotation_euler = (0.5 + 0.25 * (k % 3), 0, a)
    cyl(name + "_stem", 0.012, h * 0.85, base, MAT["MAT_Foliage"], cname, n=8)


def bed(prefix, cname, head_x, cy, width, length=2.1, throw=True, pillows=4, sign=-1):
    """Bed with the headboard at head_x, extending towards sign * x."""
    cx = head_x + sign * length / 2
    box(prefix + "_Base", (length - 0.10, width, 0.30), (head_x + sign * (length + 0.10) / 2, cy, FZ),
        MAT["MAT_Walnut"], cname, bevel=0.01)
    box(prefix + "_Headboard", (0.09, width + 0.20, 1.15), (head_x + sign * 0.045, cy, FZ), MAT["MAT_Linen"],
        cname, bevel=0.03, seg=3)
    box(prefix + "_Mattress", (length - 0.14, width - 0.04, 0.24), (cx + sign * 0.03, cy, FZ + 0.30),
        MAT["MAT_Linen"], cname, bevel=0.05, seg=3)
    box(prefix + "_Duvet", (length - 0.55, width + 0.04, 0.07), (cx + sign * 0.24, cy, FZ + 0.52),
        MAT["MAT_Linen"], cname, bevel=0.03, seg=3)
    if throw:
        box(prefix + "_Throw", (0.55, width + 0.08, 0.03), (head_x + sign * (length - 0.42), cy, FZ + 0.585),
            MAT["MAT_Sage_Throw"], cname, bevel=0.012)
    pw = (width - 0.2) / 2
    for k in range(2):
        y = cy + (k - 0.5) * (pw + 0.05)
        box("%s_Pillow_%d" % (prefix, k + 1), (0.16, pw, 0.42), (head_x + sign * 0.22, y, FZ + 0.52),
            MAT["MAT_Linen"], cname, bevel=0.06, seg=3).rotation_euler.y = sign * -0.25
        if pillows > 2:
            box("%s_Cushion_%d" % (prefix, k + 1), (0.14, pw * 0.7, 0.32), (head_x + sign * 0.36, y, FZ + 0.52),
                MAT["MAT_Pillow_Olive"], cname, bevel=0.05, seg=3).rotation_euler.y = sign * -0.2


def nightstand(name, cname, loc, lamp=True, facing=0.0):
    box(name, (0.48, 0.42, 0.52), (loc[0], loc[1], FZ), MAT["MAT_Walnut"], cname, rot=facing, bevel=0.006)
    if lamp:
        cyl(name + "_LampBase", 0.07, 0.30, (loc[0], loc[1], FZ + 0.52), MAT["MAT_Warm_Metal"], cname, bevel=0.01)
        sh = cyl(name + "_LampShade", 0.15, 0.22, (loc[0], loc[1], FZ + 0.80), MAT["MAT_Lamp_Shade"], cname, n=40)
        sh.data.polygons[-1].use_smooth = True
        light("LGT_" + name + "_Lamp", "POINT", (loc[0], loc[1], FZ + 0.90), 5.0, "LIGHTS_Interior", size=0.05)


def armchair(name, cname, loc, facing):
    """facing = direction (radians) the sitter looks."""
    root = empty(name, (loc[0], loc[1], FZ), cname, size=0.2)
    root.rotation_euler.z = facing - math.pi / 2
    parts = [(name + "_Seat", (0.62, 0.58, 0.18), (0, 0.02, 0.24), MAT["MAT_Boucle"]),
             (name + "_Back", (0.70, 0.16, 0.48), (0, -0.30, 0.22), MAT["MAT_Boucle"]),
             (name + "_ArmL", (0.12, 0.62, 0.38), (-0.36, -0.02, 0.22), MAT["MAT_Boucle"]),
             (name + "_ArmR", (0.12, 0.62, 0.38), (0.36, -0.02, 0.22), MAT["MAT_Boucle"]),
             (name + "_Plinth", (0.80, 0.72, 0.22), (0, -0.04, 0.02), MAT["MAT_Boucle"])]
    for nm, size, off, mt in parts:
        p = box(nm, size, off, mt, cname, bevel=0.05, seg=3)
        p.parent = root
    return root


def side_table(name, cname, loc, r=0.22, h=0.52, mat=None):
    cyl(name + "_Top", r, 0.03, (loc[0], loc[1], FZ + h - 0.03), mat or MAT["MAT_Walnut"], cname, bevel=0.005)
    cyl(name + "_Stem", 0.025, h - 0.03, (loc[0], loc[1], FZ), MAT["MAT_Warm_Metal"], cname, n=16)
    cyl(name + "_Foot", r * 0.7, 0.015, (loc[0], loc[1], FZ), MAT["MAT_Warm_Metal"], cname)


def tv_wall(prefix, cname, wall_face, cy, axis="x", sign=1, console_len=1.8, tv_w=1.45):
    """Console against a wall whose room-side face is at wall_face, TV mounted above. sign = into the room."""
    d = 0.42
    if axis == "x":
        box(prefix + "_Console", (d, console_len, 0.42), (wall_face + sign * (d / 2 + 0.016), cy, FZ),
            MAT["MAT_Walnut"], cname, bevel=0.006)
        box(prefix + "_TV", (0.035, tv_w, tv_w * 0.5625), (wall_face + sign * 0.03, cy, FZ + 0.95),
            MAT["MAT_TV_Black"], cname, bevel=0.003)
    else:
        box(prefix + "_Console", (console_len, d, 0.42), (cy, wall_face + sign * (d / 2 + 0.016), FZ),
            MAT["MAT_Walnut"], cname, bevel=0.006)
        box(prefix + "_TV", (tv_w, 0.035, tv_w * 0.5625), (cy, wall_face + sign * 0.03, FZ + 0.95),
            MAT["MAT_TV_Black"], cname, bevel=0.003)


def wardrobe(name, cname, x0, x1, y_face, depth, sign):
    """Full-height wardrobe from x0..x1 against a horizontal wall face, projecting sign*depth in metres y."""
    cy = y_face + sign * (depth / 2 + 0.016)
    box(name, (x1 - x0, depth, 2.40), ((x0 + x1) / 2, cy, FZ), MAT["MAT_Walnut"], cname, bevel=0.004)
    n = max(2, round((x1 - x0) / 0.55))
    for k in range(1, n):
        x = x0 + (x1 - x0) * k / n
        box("%s_Seam_%d" % (name, k), (0.004, 0.004, 2.30), (x, y_face + sign * (depth + 0.018), FZ + 0.05),
            MAT["MAT_Frame_Charcoal"], cname)
    for k in range(n):
        x = x0 + (x1 - x0) * (k + 0.5) / n + (0.2 if k % 2 == 0 else -0.2) * (x1 - x0) / n
        box("%s_Pull_%d" % (name, k + 1), (0.016, 0.02, 0.5), (x, y_face + sign * (depth + 0.027), FZ + 0.85),
            MAT["MAT_Brushed_Bronze"], cname)


def rug(name, cname, c, sx, sy, rot=0.0):
    box(name, (sx, sy, 0.012), (c[0], c[1], FZ), MAT["MAT_Rug_Wool"], cname, rot=rot, bevel=0.004)


def annular_sector(name, c, r0, r1, a0, a1, z0, z1, mat, cname, seg=40):
    bm = bmesh.new()
    pts_o = [(c[0] + r1 * math.cos(a0 + (a1 - a0) * k / seg), c[1] + r1 * math.sin(a0 + (a1 - a0) * k / seg))
             for k in range(seg + 1)]
    pts_i = [(c[0] + r0 * math.cos(a0 + (a1 - a0) * k / seg), c[1] + r0 * math.sin(a0 + (a1 - a0) * k / seg))
             for k in range(seg + 1)]
    bm_prism(bm, pts_o + pts_i[::-1], z0, z1)
    ob = mesh_obj(name, bm, cname, mat)
    md = ob.modifiers.new("Bevel", "BEVEL")
    md.width = 0.04
    md.segments = 4
    md.limit_method = "ANGLE"
    for p in ob.data.polygons:
        p.use_smooth = True
    return ob


def wc(name, cname, loc, facing):
    root = empty(name, (loc[0], loc[1], FZ), cname, size=0.15)
    root.rotation_euler.z = facing
    b = cyl(name + "_Bowl", 0.19, 0.38, (0.30, 0, 0.0), MAT["MAT_Ceramic_White"], cname, sx=1.4, sy=1.0, bevel=0.03)
    b.parent = root
    p = box(name + "_FlushPanel", (0.03, 0.40, 1.0), (0.017, 0, 0), MAT["MAT_Walnut"], cname, bevel=0.004)
    p.parent = root
    f = box(name + "_FlushPlate", (0.01, 0.20, 0.14), (0.034, 0, 0.82), MAT["MAT_Brushed_Bronze"], cname)
    f.parent = root
    return root


def vanity(name, cname, loc, facing, length=0.9, mirror=True):
    """Wall-hung vanity: loc on the wall face, facing = direction into the room."""
    root = empty(name, (loc[0], loc[1], FZ), cname, size=0.15)
    root.rotation_euler.z = facing
    parts = [box(name + "_Cabinet", (0.48, length, 0.36), (0.245, 0, 0.40), MAT["MAT_Walnut"], cname, bevel=0.004),
             box(name + "_Top", (0.50, length + 0.02, 0.03), (0.255, 0, 0.76), MAT["MAT_Quartz"], cname, bevel=0.003),
             cyl(name + "_Basin", 0.19, 0.13, (0.25, 0, 0.79), MAT["MAT_Ceramic_White"], cname, sx=1.0,
                 sy=min(1.3, (length / 2 - 0.03) / 0.19),
                 bevel=0.02),
             cyl(name + "_Tap", 0.012, 0.26, (0.04, 0, 0.79), MAT["MAT_Brushed_Bronze"], cname, n=12),
             box(name + "_Spout", (0.16, 0.02, 0.02), (0.11, 0, 1.04), MAT["MAT_Brushed_Bronze"], cname)]
    if mirror:
        parts.append(box(name + "_Mirror", (0.012, length * 0.85, 0.85), (0.008, 0, 1.20), MAT["MAT_Mirror"], cname,
                         bevel=0.003))
    for p in parts:
        p.parent = root
    return root


def shower(name, cname, x0, x1, y0, y1, glass_side, glass_len=None):
    """Shower tray on (x0..x1, y0..y1) metres with an 8 mm glass screen along glass_side ('x0','x1','y0','y1')."""
    bm = bmesh.new()
    bm_box(bm, x0 + 0.005, x1 - 0.005, y0 + 0.005, y1 - 0.005, FZ, FZ + 0.03)
    mesh_obj(name + "_Tray", bm, cname, MAT["MAT_Greige_Stone"])
    bm = bmesh.new()
    if glass_side in ("y0", "y1"):
        y = y0 if glass_side == "y0" else y1
        L = glass_len or (x1 - x0 - 0.02)
        bm_box(bm, x0 + 0.01, x0 + 0.01 + L, y - 0.004, y + 0.004, FZ + 0.03, 2.0)
    else:
        x = x0 if glass_side == "x0" else x1
        L = glass_len or (y1 - y0 - 0.02)
        bm_box(bm, x - 0.004, x + 0.004, y0 + 0.01, y0 + 0.01 + L, FZ + 0.03, 2.0)
    mesh_obj(name + "_Glass", bm, cname, MAT["MAT_Clear_Glass"])
    cyl(name + "_Head", 0.11, 0.01, ((x0 + x1) / 2, (y0 + y1) / 2, 2.25), MAT["MAT_Brushed_Bronze"], cname)


def build_furniture():
    it = P["int_t"] * S / 2          # half interior wall in px
    # ---------------------------------------------------------------- bedroom 1 (8)
    c = "ROOM_Bedroom_01"
    head = X(877 - it) - 0.016
    bed("FURN_Bed1_Bed", c, head, Y(272), 1.85, 2.10)
    nightstand("FURN_Bed1_Nightstand_N", c, (head - 0.25, Y(272) + 1.85 / 2 + 0.33))
    nightstand("FURN_Bed1_Nightstand_S", c, (head - 0.25, Y(272) - 1.85 / 2 - 0.33))
    box("FURN_Bed1_Bench", (0.45, 1.40, 0.45), (head - 2.10 - 0.40, Y(272), FZ), MAT["MAT_Linen"], c, bevel=0.03)
    rug("FURN_Bed1_Rug", c, (head - 1.85, Y(272)), 2.50, 2.40)
    tv_wall("FURN_Bed1", c, X(707), Y(270), "x", 1, 1.6, 1.30)
    armchair("FURN_Bed1_Armchair", c, (X(752), Y(205)), math.radians(-45))
    side_table("FURN_Bed1_SideTable", c, (X(792), Y(190)))
    wardrobe("FURN_Bed1_Wardrobe", c, X(709), X(832), Y(397 - it), 0.60, +1)
    # ---------------------------------------------------------------- master (10)
    c = "ROOM_Master"
    head = X(921 - it) - 0.016
    by = Y(537)
    bed("FURN_Master_Bed", c, head, by, 1.95, 2.15)
    nightstand("FURN_Master_Nightstand_N", c, (head - 0.25, by + 1.95 / 2 + 0.33))
    nightstand("FURN_Master_Nightstand_S", c, (head - 0.25, by - 1.95 / 2 - 0.33))
    box("FURN_Master_Bench", (0.45, 1.50, 0.45), (head - 2.15 - 0.40, by, FZ), MAT["MAT_Linen"], c, bevel=0.03)
    rug("FURN_Master_Rug", c, (head - 1.95, by), 2.70, 2.60)
    tv_wall("FURN_Master", c, X(707), Y(540), "x", 1, 1.6, 1.30)
    armchair("FURN_Master_Armchair", c, (X(758), Y(466)), math.radians(-40))
    side_table("FURN_Master_SideTable", c, (X(790), Y(458)))
    wardrobe("FURN_Master_Wardrobe", c, X(709), X(832), Y(397 + it), 0.60, -1)
    # ---------------------------------------------------------------- bedroom 2 (12)
    c = "ROOM_Bedroom_02"
    head = X(1348) - 0.016
    by = Y(415)
    bed("FURN_Bed2_Bed", c, head, by, 1.65, 2.10)
    nightstand("FURN_Bed2_Nightstand_N", c, (head - 0.25, by + 1.65 / 2 + 0.34))
    nightstand("FURN_Bed2_Nightstand_S", c, (head - 0.25, by - 1.65 / 2 - 0.34))
    rug("FURN_Bed2_Rug", c, (head - 1.75, by), 2.30, 2.30)
    tv_wall("FURN_Bed2", c, X(1192 + it), Y(414), "x", 1, 1.8, 1.30)
    wardrobe("FURN_Bed2_Wardrobe", c, X(1262), X(1346), Y(305 + it), 0.58, -1)
    # ---------------------------------------------------------------- living (2)
    c = "ROOM_Living"
    rug("FURN_Living_Rug", c, (X(1118), Y(412)), 3.0, 3.0)
    tv_wall("FURN_Living_Media", c, X(1011 + it), Y(415), "x", 1, 2.4, 1.65)
    sc = XY(1124, 420)
    R = 1.30
    a0, a1 = math.radians(-128), math.radians(62)          # opens towards the TV wall / dining (north-west)
    annular_sector("FURN_Living_Sofa_Base", sc, R - 0.86, R - 0.06, a0, a1, FZ, FZ + 0.12, MAT["MAT_Boucle"], c)
    annular_sector("FURN_Living_Sofa_Seat", sc, R - 0.90, R - 0.16, a0, a1, FZ + 0.12, FZ + 0.44, MAT["MAT_Boucle"], c)
    annular_sector("FURN_Living_Sofa_Back", sc, R - 0.22, R, a0 - 0.02, a1 + 0.02, FZ + 0.12, FZ + 0.80,
                   MAT["MAT_Boucle"], c)
    cyl("FURN_Living_CoffeeTableA", 0.48, 0.34, (X(1094), Y(409), FZ), MAT["MAT_Quartz"], c, sx=1.0, sy=0.72,
        bevel=0.02, rot=0.5)
    cyl("FURN_Living_CoffeeTableB", 0.34, 0.42, (X(1113), Y(377), FZ), MAT["MAT_Walnut"], c, sx=1.0, sy=0.72,
        bevel=0.02, rot=0.3)
    armchair("FURN_Living_Armchair", c, (X(1116), Y(338)), math.radians(-90))
    plant("FURN_Living_Plant", (X(1163), Y(354), FZ), c, 0.24, 1.4)
    cyl("FURN_Living_FloorLamp_Base", 0.14, 0.02, (X(1176), Y(484), FZ), MAT["MAT_Warm_Metal"], c)
    cyl("FURN_Living_FloorLamp_Stem", 0.012, 1.45, (X(1176), Y(484), FZ), MAT["MAT_Warm_Metal"], c, n=12)
    cyl("FURN_Living_FloorLamp_Shade", 0.20, 0.28, (X(1176), Y(484), FZ + 1.40), MAT["MAT_Lamp_Shade"], c, n=40)
    light("LGT_Living_FloorLamp", "POINT", (X(1176), Y(484), FZ + 1.52), 8.0, "LIGHTS_Interior", size=0.06)
    # ---------------------------------------------------------------- dining (1)
    c = "ROOM_Dining"
    tc = XY(1075, 256)
    box("FURN_Dining_Table_Top", (2.00, 1.00, 0.04), (tc.x, tc.y, FZ + 0.71), MAT["MAT_Quartz"], c, bevel=0.006)
    for k, dx in enumerate((-0.6, 0.6)):
        box("FURN_Dining_Table_Base_%d" % (k + 1), (0.12, 0.55, 0.71), (tc.x + dx, tc.y, FZ), MAT["MAT_Walnut"], c,
            bevel=0.01)
    for row, (yy, face) in enumerate(((tc.y + 0.72, -math.pi / 2), (tc.y - 0.72, math.pi / 2))):
        for k, dx in enumerate((-0.62, 0.0, 0.62)):
            dining_chair("FURN_Dining_Chair_%d%d" % (row + 1, k + 1), c, (tc.x + dx, yy), face)
    box("FURN_Dining_Pendant", (1.40, 0.10, 0.04), (tc.x, tc.y, 2.05), MAT["MAT_Brushed_Bronze"], c, bevel=0.01)
    for k, dx in enumerate((-0.55, 0.55)):
        cyl("FURN_Dining_Pendant_Rod_%d" % (k + 1), 0.004, H - 2.094, (tc.x + dx, tc.y, 2.09),
            MAT["MAT_Brushed_Bronze"], c, n=8)
    light("LGT_Dining_Pendant", "AREA", (tc.x, tc.y, 2.025), 60.0, "LIGHTS_Interior", size=(1.3, 0.06))
    sphere("FURN_Dining_Bowl", 0.16, (tc.x, tc.y, FZ + 0.75 + 0.057), MAT["MAT_Ceramic_White"], c, (1, 1, 0.35))
    # ---------------------------------------------------------------- kitchen (3)
    c = "ROOM_Kitchen"
    kx0, kx1, ky0, ky1 = X(952 + it) + 0.02, X(1117), Y(158), Y(32)   # room-side faces (m), clear of door linings
    tall_x0 = kx1 - 0.005
    box("FURN_Kitchen_NorthRun_Base", (tall_x0 - kx0 - 0.01, 0.60, 0.86), ((kx0 + tall_x0) / 2, ky1 - 0.305, FZ),
        MAT["MAT_Walnut"], c, bevel=0.003)
    box("FURN_Kitchen_NorthRun_Top", (tall_x0 - kx0 - 0.01, 0.61, 0.04), ((kx0 + tall_x0) / 2, ky1 - 0.31, FZ + 0.86),
        MAT["MAT_Quartz"], c, bevel=0.002)
    box("FURN_Kitchen_NorthRun_Cooktop", (0.75, 0.50, 0.006), (X(1018), ky1 - 0.32, FZ + 0.90), MAT["MAT_TV_Black"], c)
    box("FURN_Kitchen_NorthRun_Hood", (0.80, 0.50, 0.30), (X(1018), ky1 - 0.26, 1.95), MAT["MAT_Appliance_Steel"], c,
        bevel=0.003)
    box("FURN_Kitchen_NorthRun_WallUnits", (tall_x0 - kx0 - 0.01, 0.35, 0.74), ((kx0 + tall_x0) / 2, ky1 - 0.18, 2.25),
        MAT["MAT_Walnut"], c, bevel=0.003)
    box("FURN_Kitchen_NorthRun_Backsplash", (tall_x0 - kx0 - 0.01, 0.012, 0.60), ((kx0 + tall_x0) / 2, ky1 - 0.007, FZ + 0.90),
        MAT["MAT_Quartz"], c)
    box("FURN_Kitchen_TallOven_Body", (0.60, 0.70, 2.30), (kx1 - 0.31, Y(97), FZ), MAT["MAT_Walnut"], c, bevel=0.003)
    box("FURN_Kitchen_TallOven_Front", (0.01, 0.56, 0.60), (kx1 - 0.615, Y(97), FZ + 0.90), MAT["MAT_TV_Black"], c)
    box("FURN_Kitchen_Fridge", (0.60, 0.80, 2.10), (kx1 - 0.31, Y(134) + 0.0, FZ), MAT["MAT_Appliance_Steel"], c,
        bevel=0.004)
    sx0, sx1 = X(966), X(1036)
    box("FURN_Kitchen_SinkRun_Base", (sx1 - sx0, 0.60, 0.86), ((sx0 + sx1) / 2, ky0 + 0.305, FZ), MAT["MAT_Walnut"], c,
        bevel=0.003)
    box("FURN_Kitchen_SinkRun_Top", (sx1 - sx0, 0.62, 0.04), ((sx0 + sx1) / 2, ky0 + 0.315, FZ + 0.86), MAT["MAT_Quartz"],
        c, bevel=0.002)
    box("FURN_Kitchen_SinkRun_Sink", (0.70, 0.42, 0.006), ((sx0 + sx1) / 2, ky0 + 0.32, FZ + 0.901), MAT["MAT_Appliance_Steel"],
        c)
    cyl("FURN_Kitchen_SinkRun_Tap", 0.014, 0.32, ((sx0 + sx1) / 2, ky0 + 0.08, FZ + 0.90), MAT["MAT_Brushed_Bronze"], c, n=12)
    plant("FURN_Kitchen_Herb", (kx1 - 0.85, ky1 - 0.3, FZ + 0.901), c, 0.08, 0.3)
    light("LGT_Kitchen_UnderCabinet", "AREA", ((kx0 + kx1) / 2, ky1 - 0.25, 1.86), 25.0, "LIGHTS_Interior",
          size=(kx1 - kx0 - 0.2, 0.05))
    # ---------------------------------------------------------------- utility (4) and staff bathroom (5)
    c = "ROOM_Utility"
    ux0, ux1, uy1 = X(797), X(952 - it), Y(32)
    box("FURN_Utility_Counter_Base", (ux1 - ux0 - 0.66, 0.60, 0.86), (ux0 + (ux1 - ux0 - 0.66) / 2 + 0.005, uy1 - 0.305, FZ),
        MAT["MAT_Walnut"], c, bevel=0.003)
    box("FURN_Utility_Counter_Top", (ux1 - ux0 - 0.66, 0.62, 0.04), (ux0 + (ux1 - ux0 - 0.66) / 2 + 0.005, uy1 - 0.315,
                                                                FZ + 0.86), MAT["MAT_Quartz"], c)
    box("FURN_Utility_Washer", (0.60, 0.60, 0.85), (ux1 - 0.33, uy1 - 0.305, FZ), MAT["MAT_Ceramic_White"], c, bevel=0.01)
    box("FURN_Utility_Dryer", (0.60, 0.60, 0.85), (ux1 - 0.33, uy1 - 0.305, FZ + 0.86), MAT["MAT_Ceramic_White"], c,
        bevel=0.01)
    wc("FURN_StaffBath_WC", c, (X(890 + it), Y(144)), 0.0)
    vanity("FURN_StaffBath_Basin", c, (X(890 + it), Y(121)), 0.0, 0.45, mirror=True)
    # ---------------------------------------------------------------- bathrooms (6, 9, 11, 13)
    c = "ROOM_Bathrooms"
    wc("FURN_Powder_WC", c, (X(997), Y(175)), -math.pi / 2)
    vanity("FURN_Powder_Vanity", c, (X(1018 - it), Y(240)), math.pi, 0.75)
    shower("FURN_Bath1_Shower", c, X(877 + it), X(950 - it), Y(252), Y(210 + it), "y0")
    wc("FURN_Bath1_WC", c, (X(950 - it), Y(276)), math.pi)
    vanity("FURN_Bath1_Vanity", c, (X(950 - it), Y(316)), math.pi, 0.75)
    shower("FURN_MasterBath_Shower", c, X(921 + it), X(1007), Y(617), Y(560), "y1")
    wc("FURN_MasterBath_WC", c, (X(1007), Y(527)), math.pi)
    vanity("FURN_MasterBath_Vanity", c, (X(1007), Y(482)), math.pi, 0.80)
    shower("FURN_Bath2_Shower", c, X(1192 + it), X(1262), Y(216), Y(175), "y0")
    wc("FURN_Bath2_WC", c, (X(1262), Y(243)), math.pi)
    vanity("FURN_Bath2_Vanity", c, (X(1262), Y(281)), math.pi, 0.62)


def dining_chair(name, cname, loc, facing):
    root = empty(name, (loc[0], loc[1], FZ), cname, size=0.15)
    root.rotation_euler.z = facing - math.pi / 2
    parts = [box(name + "_Seat", (0.46, 0.46, 0.07), (0, 0, 0.42), MAT["MAT_Linen"], cname, bevel=0.025, seg=3),
             box(name + "_Back", (0.44, 0.06, 0.40), (0, -0.21, 0.48), MAT["MAT_Linen"], cname, bevel=0.025, seg=3)]
    for k, (dx, dy) in enumerate(((-0.19, -0.19), (0.19, -0.19), (-0.19, 0.19), (0.19, 0.19))):
        parts.append(cyl("%s_Leg_%d" % (name, k + 1), 0.013, 0.42, (dx, dy, 0), MAT["MAT_Brushed_Bronze"], cname, n=10))
    for p in parts:
        p.parent = root


# ======================================================================== lighting
def sun_position(lat, lon, utc_offset, month, day, hour):
    """NOAA-style solar position: azimuth (deg from true north, clockwise) and elevation (deg)."""
    n = sum((31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31)[:month - 1]) + day
    g = 2 * math.pi / 365 * (n - 1 + (hour - 12) / 24)
    eqt = 229.18 * (0.000075 + 0.001868 * math.cos(g) - 0.032077 * math.sin(g) - 0.014615 * math.cos(2 * g)
                    - 0.040849 * math.sin(2 * g))
    decl = (0.006918 - 0.399912 * math.cos(g) + 0.070257 * math.sin(g) - 0.006758 * math.cos(2 * g)
            + 0.000907 * math.sin(2 * g) - 0.002697 * math.cos(3 * g) + 0.00148 * math.sin(3 * g))
    tst = hour * 60 + eqt + 4 * lon - 60 * utc_offset
    ha = math.radians(tst / 4 - 180)
    la = math.radians(lat)
    cz = math.sin(la) * math.sin(decl) + math.cos(la) * math.cos(decl) * math.cos(ha)
    zen = math.acos(max(-1, min(1, cz)))
    az = math.degrees(math.atan2(math.sin(ha), math.cos(ha) * math.sin(la) - math.tan(decl) * math.cos(la))) + 180
    return az % 360, 90 - math.degrees(zen)


def build_lighting():
    sc = bpy.context.scene
    az, el = sun_position(**SITE)
    # true north is 17.1 deg clockwise of plan-up, so a true azimuth is that much further clockwise on the plan
    north = T.NORTH_DEG_CW_FROM_UP
    plan_az = math.radians(az + north)
    to_sun = Vector((math.sin(plan_az) * math.cos(math.radians(el)), math.cos(plan_az) * math.cos(math.radians(el)),
                     math.sin(math.radians(el))))
    sd = bpy.data.lights.new("LGT_Sun", "SUN")
    sd.energy = 4.5
    sd.angle = math.radians(0.53)
    sd.color = kelvin_rgb(5600)
    sun = bpy.data.objects.new("LGT_Sun", sd)
    sun.rotation_euler = (-to_sun).to_track_quat("-Z", "Y").to_euler()
    link(sun, "LIGHTS_Daylight")
    sun["true_azimuth_deg"] = round(az, 2)
    sun["elevation_deg"] = round(el, 2)
    w = bpy.data.worlds.new("WORLD_Daylight")
    w.use_nodes = True
    nt = w.node_tree
    bg = nt.nodes["Background"]
    sky = nt.nodes.new("ShaderNodeTexSky")
    sky.sky_type = "MULTIPLE_SCATTERING" if "MULTIPLE_SCATTERING" in \
        sky.bl_rna.properties["sky_type"].enum_items.keys() else "NISHITA"
    sky.sun_disc = False
    sky.sun_elevation = math.radians(el)
    sky.sun_rotation = math.atan2(to_sun.x, to_sun.y) * -1 + math.pi / 2
    sky.altitude = 40.0
    sky.air_density = 1.0
    sky.aerosol_density = 2.0
    nt.links.new(sky.outputs[0], bg.inputs["Color"])
    bg.inputs["Strength"].default_value = 0.14
    sc.world = w
    north_e = empty("NORTH_Arrow", (X(1480), Y(560), 0.05), "REFERENCE_FloorPlan", "SINGLE_ARROW", 1.2)
    north_e.matrix_world = Matrix.Translation(north_e.location) @ Matrix.Rotation(-math.radians(north), 4, "Z") @ \
        Matrix.Rotation(-math.pi / 2, 4, "X")
    north_e["north_deg_cw_from_plan_up"] = round(north, 2)
    # window portals guide daylight sampling into the rooms
    for o in OPENINGS:
        if o["kind"] != "window":
            continue
        u = (o["a"] + o["b"]) / 2
        L = o["b"] - o["a"]
        cm = (o["c0"] + o["c1"]) / 2
        wall = next(w_ for w_ in T.WALLS if w_["name"] == o["wall"])
        outward = wall["side"] if o["axis"] == "v" else -wall["side"]
        face_in = cm - outward * 0.14
        z = (o["z0"] + o["z1"]) / 2
        if o["axis"] == "h":
            loc, rot = (u, face_in, z), (-math.pi / 2 if outward > 0 else math.pi / 2, 0, 0)
        else:
            loc, rot = (face_in, u, z), (0, math.pi / 2 if outward > 0 else -math.pi / 2, 0)
        ld = bpy.data.lights.new("LGT_Portal_" + o["id"], "AREA")
        ld.shape = "RECTANGLE"
        ld.size, ld.size_y = (L, o["z1"] - o["z0"]) if o["axis"] == "h" else (o["z1"] - o["z0"], L)
        ld.cycles.is_portal = True
        ob = bpy.data.objects.new("LGT_Portal_" + o["id"], ld)
        ob.location = loc
        ob.rotation_euler = rot
        link(ob, "LIGHTS_Daylight")
    # recessed 3000 K downlights on a grid per room (spots aimed down)
    for name, r in T.ROOMS.items():
        poly = room_poly_m(name)
        xs, ys = [p[0] for p in poly], [p[1] for p in poly]
        nx = max(1, round((max(xs) - min(xs)) / 1.6))
        ny = max(1, round((max(ys) - min(ys)) / 1.6))
        k = 0
        for i in range(nx):
            for j in range(ny):
                p = (min(xs) + (i + 0.5) * (max(xs) - min(xs)) / nx, min(ys) + (j + 0.5) * (max(ys) - min(ys)) / ny)
                if not point_in_poly(p, poly):
                    continue
                k += 1
                light("LGT_Down_%s_%02d" % (name, k), "SPOT", (p[0], p[1], H - 0.02), 7.0, "LIGHTS_Interior",
                      size=0.03, spot=75)
                cyl("FIX_Downlight_%s_%02d" % (name, k), 0.045, 0.004, (p[0], p[1], H - 0.004),
                    MAT["MAT_Warm_Metal"], "ARCH_Ceilings", n=20)


def point_in_poly(p, poly):
    x, y = p
    inside = False
    n = len(poly)
    for i in range(n):
        x0, y0 = poly[i]
        x1, y1 = poly[(i + 1) % n]
        if (y0 > y) != (y1 > y) and x < (x1 - x0) * (y - y0) / (y1 - y0) + x0:
            inside = not inside
    return inside


# ======================================================================== exterior context
def build_city():
    """Ground far below (the unit is on an upper floor) and a ring of generic block towers, for window views."""
    import random
    rnd = random.Random(7)
    g = mat_plain("MAT_Context_Ground", (0.16, 0.17, 0.15), rough=0.9)
    t_mats = [mat_plain("MAT_Context_Tower_%d" % k, c, rough=0.6) for k, c in
              enumerate(((0.55, 0.53, 0.50), (0.40, 0.42, 0.44), (0.62, 0.58, 0.52)))]
    box("CTX_Ground", (3000, 3000, 1.0), (8, 6, -61.0), g, "CONTEXT_City")
    for k in range(70):
        a = rnd.uniform(0, 2 * math.pi)
        d = rnd.uniform(140, 900)
        h = rnd.uniform(25, 140)
        w = rnd.uniform(18, 45)
        ob = box("CTX_Tower_%02d" % k, (w, rnd.uniform(18, 45), h), (8 + d * math.cos(a), 6 + d * math.sin(a), -60.0),
                 t_mats[k % 3], "CONTEXT_City", rot=rnd.uniform(0, 1.5))
        ob.visible_shadow = False


# ======================================================================== reference plane
def build_reference():
    img = bpy.data.images.load(os.path.join(ROOT, "reference", "floor_plan.jpg"))
    w, h = T.IMG
    x0, y0 = X(0), Y(0)
    x1, y1 = X(w), Y(h)
    me = bpy.data.meshes.new("REF_FloorPlan")
    me.from_pydata([(x0, y1, 0), (x1, y1, 0), (x1, y0, 0), (x0, y0, 0)], [], [(0, 1, 2, 3)])
    uv = me.uv_layers.new(name="UVMap")
    for loop, co in zip(uv.data, ((0, 0), (1, 0), (1, 1), (0, 1))):
        loop.uv = co
    ob = bpy.data.objects.new("REF_FloorPlan", me)
    m, n, l, b = _mat("MAT_Reference_Plan")
    t = n.new("ShaderNodeTexImage")
    t.image = img
    l.new(t.outputs["Color"], b.inputs["Base Color"])
    _set(b, rough=1.0)
    me.materials.append(m)
    link(ob, "REFERENCE_FloorPlan")
    ob.hide_render = True
    return ob


# ======================================================================== cameras
STILLS = {
    # name: (eye px, eye height, target px, target height, lens)
    "CAM_02_Entry": ((1166, 192), 1.55, (1090, 400), 1.0, 24),
    "CAM_03_Living": ((1036, 328), 1.50, (1092, 482), 0.55, 24),
    "CAM_04_Dining": ((1042, 474), 1.50, (1092, 225), 0.85, 28),
    "CAM_05_Kitchen": ((1078, 96), 1.55, (955, 86), 1.05, 24),
    "CAM_06_Master": ((736, 604), 1.50, (900, 520), 0.85, 28),
    "CAM_07_Bedroom1": ((732, 352), 1.50, (870, 250), 0.85, 28),
    "CAM_08_Bedroom2": ((1222, 332), 1.50, (1330, 470), 0.85, 24),
}


def build_cameras(outline):
    sc = bpy.context.scene
    for name, (eye, eh, tgt, th, lens) in STILLS.items():
        cd = bpy.data.cameras.new(name)
        cd.lens = lens
        cd.sensor_width = 36
        cd.clip_start = 0.05
        ob = bpy.data.objects.new(name, cd)
        e = Vector((X(eye[0]), Y(eye[1]), eh))
        t = Vector((X(tgt[0]), Y(tgt[1]), th))
        ob.location = e
        ob.rotation_euler = (t - e).to_track_quat("-Z", "Y").to_euler()
        link(ob, "CAMERAS_Still")
    # isometric master: orthographic, elevated, looking down from the south-east
    cd = bpy.data.cameras.new("CAM_01_Isometric")
    cd.type = "ORTHO"
    ob = bpy.data.objects.new("CAM_01_Isometric", cd)
    rot = Matrix.Rotation(math.radians(20), 4, "Z") @ Matrix.Rotation(math.radians(34), 4, "X")
    ob.matrix_world = rot
    link(ob, "CAMERAS_Still")
    pts = [Vector((X(x), Y(y), z)) for x, y in outline for z in (-0.3, H)]
    pts += [Vector((X(x), Y(y), z)) for x, y in ((1222, 16), (1475, 16), (1475, 175)) for z in (0, H)]
    inv = rot.inverted()
    loc = [inv @ p for p in pts]
    xs, ys, zs = [p.x for p in loc], [p.y for p in loc], [p.z for p in loc]
    cx, cy = (max(xs) + min(xs)) / 2, (max(ys) + min(ys)) / 2
    aspect = 16 / 9
    cd.ortho_scale = max(max(xs) - min(xs), (max(ys) - min(ys)) * aspect) * 1.06
    cd.clip_start = 0.1
    cd.clip_end = 200
    ob.matrix_world = rot @ Matrix.Translation((cx, cy, max(zs) + 40))
    # top-down orthographic validation camera
    cd = bpy.data.cameras.new("CAM_00_TopDown_Validation")
    cd.type = "ORTHO"
    ob = bpy.data.objects.new("CAM_00_TopDown_Validation", cd)
    xs, ys = [X(p[0]) for p in outline], [Y(p[1]) for p in outline]
    ob.location = ((max(xs) + min(xs)) / 2 + 1.0, (max(ys) + min(ys)) / 2, 40)
    cd.ortho_scale = (max(xs) - min(xs) + 2 + 3.0) * 1.04
    cd.clip_end = 100
    link(ob, "CAMERAS_Still")
    sc.camera = bpy.data.objects["CAM_01_Isometric"]


# ======================================================================== walkthrough
FPS = 24
WALK_SPEED = 0.5            # m/s target cruise
# each path: list of control points (px x, px y), eye height; look keys: (fraction of travel or "pause", px, h)
WALKS = [
    dict(name="A_Entry_Living_Master", eye=1.55, pts=[(1156, 188), (1158, 238), (1160, 296), (1128, 316),
                                                        (1060, 318), (1000, 330), (978, 362), (978, 412),
                                                        (955, 428), (900, 442), (820, 449)],
         pauses={3: 2.0, 7: 1.0, 10: 2.5},
         look=[(0, (1100, 330), 1.1), (2, (1080, 330), 1.0), (3, (1070, 450), 0.8), (5, (1030, 420), 1.0),
               (6, (975, 470), 1.1), (8, (900, 520), 0.9), (10, (880, 545), 0.8)]),
    dict(name="B_Kitchen", eye=1.55, pts=[(1061, 232), (1061, 190), (1061, 152), (1048, 118)],
         pauses={0: 1.0, 3: 2.5}, look=[(0, (1061, 120), 1.2), (2, (1010, 60), 1.0), (3, (980, 50), 1.0)]),
    dict(name="C_Bedroom2", eye=1.50, pts=[(1150, 300), (1172, 331), (1210, 331), (1236, 342)],
         pauses={0: 1.0, 3: 2.5}, look=[(0, (1230, 331), 1.4), (2, (1300, 420), 0.9), (3, (1320, 470), 0.85)]),
    dict(name="D_Bedroom1", eye=1.50, pts=[(992, 345), (980, 370), (940, 370), (900, 362)],
         pauses={0: 1.0, 3: 2.5}, look=[(0, (930, 370), 1.4), (2, (840, 280), 0.9), (3, (820, 260), 0.85)]),
]


def build_walkthrough():
    sc = bpy.context.scene
    frame = 1
    markers = []
    for w in WALKS:
        pts = [Vector((X(x), Y(y), w["eye"])) for x, y in w["pts"]]
        cu = bpy.data.curves.new("PATH_" + w["name"], "CURVE")
        cu.dimensions = "3D"
        cu.use_path = True
        sp = cu.splines.new("BEZIER")
        sp.bezier_points.add(len(pts) - 1)
        for bp, p in zip(sp.bezier_points, pts):
            bp.co = p
            bp.handle_left_type = bp.handle_right_type = "AUTO"
        path = bpy.data.objects.new("PATH_" + w["name"], cu)
        link(path, "CAMERAS_Animation")
        cu.path_duration = 1000
        # cumulative distance at each control point (sampled along the evaluated spline)
        dg = bpy.context.evaluated_depsgraph_get()
        cum = [0.0]
        for i in range(len(pts) - 1):
            cum.append(cum[-1] + bezier_seg_len(sp, i))
        L = cum[-1]
        cd = bpy.data.cameras.new("CAM_WALK_" + w["name"])
        cd.lens = 24
        cd.sensor_width = 36
        cd.clip_start = 0.05
        cam = bpy.data.objects.new("CAM_WALK_" + w["name"], cd)
        link(cam, "CAMERAS_Animation")
        fp = cam.constraints.new("FOLLOW_PATH")
        fp.target = path
        fp.use_fixed_location = True
        tgt = empty("TGT_WALK_" + w["name"], pts[0], "CAMERAS_Animation", "SPHERE", 0.12)
        tt = cam.constraints.new("TRACK_TO")
        tt.target = tgt
        tt.track_axis = "TRACK_NEGATIVE_Z"
        tt.up_axis = "UP_Y"
        # schedule: cruise between control points at WALK_SPEED, holds at the pause points
        start = frame
        keys = [(frame, 0.0)]
        pt_frame = {0: frame}
        if 0 in w["pauses"]:
            frame += round(w["pauses"][0] * FPS)
            keys.append((frame, 0.0))
        seg_start = 0
        stops = sorted(k for k in w["pauses"] if k > 0)
        if len(pts) - 1 not in stops:
            stops.append(len(pts) - 1)
        for st in stops:
            d = cum[st] - cum[seg_start]
            # eased move: average speed WALK_SPEED * 0.82 so the eased peak stays within 0.65 m/s
            dur = max(1, round(d / (WALK_SPEED * 0.82) * FPS))
            for k in range(seg_start + 1, st + 1):
                pt_frame[k] = frame + dur * ease_inv((cum[k] - cum[seg_start]) / d)
            frame += dur
            keys.append((frame, cum[st] / L))
            hold = w["pauses"].get(st, 0.0)
            if hold:
                frame += round(hold * FPS)
                keys.append((frame, cum[st] / L))
            seg_start = st
        for f, v in keys:
            fp.offset_factor = v
            fp.keyframe_insert("offset_factor", frame=f)
        for fc in action_fcurves(cam):
            for kp in fc.keyframe_points:
                kp.interpolation = "BEZIER"
                kp.easing = "EASE_IN_OUT"
                kp.handle_left_type = kp.handle_right_type = "AUTO_CLAMPED"
        # look targets keyed at control point times
        for idx, (px, py), th in w["look"]:
            f = pt_frame.get(idx, frame)
            if idx in w["pauses"] and idx > 0:
                f = pt_frame[idx] + round(w["pauses"][idx] * FPS * 0.5)
            tgt.location = (X(px), Y(py), th)
            tgt.keyframe_insert("location", frame=round(f))
        for fc in action_fcurves(tgt):
            for kp in fc.keyframe_points:
                kp.interpolation = "BEZIER"
                kp.handle_left_type = kp.handle_right_type = "AUTO_CLAMPED"
        mk = sc.timeline_markers.new("WALK_" + w["name"], frame=start)
        mk.camera = cam
        markers.append(dict(path=w["name"], frame_start=start, frame_end=frame, length_m=round(L, 2)))
        frame += 1
    sc.frame_start = 1
    sc.frame_end = frame - 1
    sc.render.fps = FPS
    return markers


def ease_inv(u):
    """Frame fraction at which a smoothstep-eased move covers fraction u of its distance."""
    lo, hi = 0.0, 1.0
    for _ in range(40):
        mid = (lo + hi) / 2
        if mid * mid * (3 - 2 * mid) < u:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


def bezier_seg_len(sp, i, n=64):
    a, b = sp.bezier_points[i], sp.bezier_points[i + 1]
    p0, p1, p2, p3 = a.co, a.handle_right, b.handle_left, b.co
    prev, L = p0, 0.0
    for k in range(1, n + 1):
        t = k / n
        q = (1 - t) ** 3 * p0 + 3 * (1 - t) ** 2 * t * p1 + 3 * (1 - t) * t * t * p2 + t ** 3 * p3
        L += (q - prev).length
        prev = q
    return L


def action_fcurves(ob):
    ad = ob.animation_data
    if ad is None or ad.action is None:
        return []
    act = ad.action
    if hasattr(act, "fcurves") and len(getattr(act, "fcurves", [])):
        return list(act.fcurves)
    out = []
    for layer in getattr(act, "layers", []):
        for strip in layer.strips:
            for bag in strip.channelbags:
                out.extend(bag.fcurves)
    return out


# ======================================================================== cutaway + render settings
def build_cutaway():
    """Boolean box that removes everything above PARAMS['cutaway_h']; modifiers are off unless toggled."""
    bm = bmesh.new()
    bm_box(bm, -10, 40, -10, 30, P["cutaway_h"], 20)
    cut = mesh_obj("CUTAWAY_Volume", bm, "REFERENCE_FloorPlan")
    cut.display_type = "WIRE"
    cut.hide_render = True
    cut.hide_viewport = True
    targets = [o for o in bpy.data.objects if o.type == "MESH" and (
        o.name.startswith(("WALL_", "COL_", "CTX_", "WINDOW_", "LEDGE_GUARD", "DOOR_FRAME")))]
    for o in targets:
        md = o.modifiers.new("CUTAWAY", "BOOLEAN")
        md.operation = "DIFFERENCE"
        md.object = cut
        md.solver = "EXACT" if "EXACT" in md.bl_rna.properties["solver"].enum_items.keys() else md.solver
        md.show_viewport = False
        md.show_render = False


def render_settings():
    sc = bpy.context.scene
    sc.unit_settings.system = "METRIC"
    sc.unit_settings.length_unit = "METERS"
    sc.unit_settings.scale_length = 1.0
    sc.render.engine = "CYCLES"
    cy = sc.cycles
    cy.device = "CPU"
    cy.samples = 64
    cy.preview_samples = 32
    cy.use_adaptive_sampling = True
    cy.adaptive_threshold = 0.02
    cy.use_denoising = True
    if hasattr(cy, "denoiser"):
        cy.denoiser = "OPENIMAGEDENOISE"
    cy.max_bounces = 8
    cy.diffuse_bounces = 4
    cy.glossy_bounces = 4
    cy.transmission_bounces = 8
    cy.transparent_max_bounces = 8
    cy.caustics_reflective = False
    cy.caustics_refractive = False
    cy.sample_clamp_indirect = 8.0
    sc.render.resolution_x, sc.render.resolution_y = 3840, 2160
    sc.render.resolution_percentage = 100
    sc.render.fps = FPS
    sc.render.use_motion_blur = False
    sc.render.image_settings.file_format = "PNG"
    sc.render.image_settings.color_depth = "16"
    sc.view_settings.view_transform = "AgX"
    sc.view_settings.look = "AgX - Base Contrast" if "AgX - Base Contrast" in \
        [i.identifier for i in sc.view_settings.bl_rna.properties["look"].enum_items] else "None"
    sc.view_settings.exposure = 0.0


def main():
    for ob in list(bpy.data.objects):
        bpy.data.objects.remove(ob)
    for c in list(bpy.data.collections):
        bpy.data.collections.remove(c)
    for name in COLLS:
        coll(name)
    build_materials()
    build_walls()
    outline = build_floors_ceilings()
    build_skirting()
    build_doors()
    build_windows()
    build_furniture()
    build_lighting()
    build_reference()
    build_city()
    build_cameras(outline)
    walks = build_walkthrough()
    build_cutaway()
    render_settings()
    sc = bpy.context.scene
    sc["plan_px_per_m"] = round(S, 4)
    sc["north_deg_cw_from_plan_up"] = round(T.NORTH_DEG_CW_FROM_UP, 2)
    sc["walk_segments"] = str(walks)
    sc["openings"] = str([{k: (round(v, 4) if isinstance(v, float) else v) for k, v in o.items()} for o in OPENINGS])
    sc["door_info"] = str(DOOR_INFO)
    os.makedirs(os.path.dirname(OUT_BLEND), exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=OUT_BLEND, compress=True)
    bpy.ops.file.make_paths_relative()
    bpy.ops.wm.save_as_mainfile(filepath=OUT_BLEND, compress=True)
    ids = set()
    for ob in bpy.data.collections["CAMERAS_Animation"].objects:
        ids.add(ob)
    bpy.data.libraries.write(OUT_PATHS, ids, fake_user=True, compress=True)
    print("BUILT", len(bpy.data.objects), "objects;", walks)


if __name__ == "__main__":
    main()
