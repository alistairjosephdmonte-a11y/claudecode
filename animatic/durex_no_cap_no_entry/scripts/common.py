"""Shared helpers: math, mesh primitives, materials, keyframe writing."""
import math
from math import sin, cos, pi, radians
import bpy
import bmesh
from mathutils import Vector, Matrix

FPS = 24
FRAME_START, FRAME_END = 1, 720
BPM = 120
BEAT = FPS * 60 // BPM  # 12 frames per beat

# Placeholder only. Replace with the HEX sampled from approved Durex brand artwork before final render.
CAP_BLUE_PLACEHOLDER = "#1F4BA5"
CAP_NAVY = "#1A2238"

SHOTS = [
    dict(n=1, start=1, end=72, lens=24, name="SH01_EST_DOLLY"),
    dict(n=2, start=73, end=144, lens=50, name="SH02_GUEST01_BLOCK"),
    dict(n=3, start=145, end=216, lens=35, name="SH03_GUEST02_CONE"),
    dict(n=4, start=217, end=288, lens=28, name="SH04_GUEST03_DISH"),
    dict(n=5, start=289, end=360, lens=50, name="SH05_HERO_APPROACH"),
    dict(n=6, start=361, end=432, lens=85, name="SH06_CU_EXCHANGE"),
    dict(n=7, start=433, end=504, lens=35, name="SH07_ROPE_ENTRY"),
    dict(n=8, start=505, end=576, lens=24, name="SH08_CLUB_WIDE"),
    dict(n=9, start=577, end=648, lens=50, name="SH09_GUEST04_CAP"),
    dict(n=10, start=649, end=720, lens=85, name="SH10_CAP_CU_ENDCARD"),
]
ENDCARD_START = 673


# ---------------------------------------------------------------- math
def clamp(x, a=0.0, b=1.0):
    return a if x < a else b if x > b else x


def smooth(t):
    t = clamp(t)
    return t * t * (3 - 2 * t)


def seg(f, f0, f1):
    """Smoothstep 0->1 between frames f0 and f1."""
    if f1 <= f0:
        return 1.0 if f >= f1 else 0.0
    return smooth((f - f0) / (f1 - f0))


def lerp(a, b, t):
    return a + (b - a) * t


def vlerp(a, b, t):
    return Vector(a).lerp(Vector(b), t)


def pulse(f, f0, f1, f2, f3):
    """0 -> 1 (f0..f1), hold, 1 -> 0 (f2..f3)."""
    return seg(f, f0, f1) * (1.0 - seg(f, f2, f3))


def wnoise(f, seed, freqs=(0.031, 0.073, 0.137), amps=(1.0, 0.5, 0.25)):
    """Deterministic smooth pseudo-noise in roughly [-1, 1]."""
    v = 0.0
    tot = 0.0
    for i, (fr, a) in enumerate(zip(freqs, amps)):
        v += a * sin(f * fr * 2 * pi + seed * (1.7 + i * 2.3) + i)
        tot += a
    return v / tot


def Rx(d):
    return Matrix.Rotation(radians(d), 3, "X")


def Ry(d):
    return Matrix.Rotation(radians(d), 3, "Y")


def Rz(d):
    return Matrix.Rotation(radians(d), 3, "Z")


def I3():
    return Matrix.Identity(3)


def aim_down_to(direction):
    """Rotation taking a down-pointing limb (0,0,-1) to `direction` (character frame)."""
    return Vector((0, 0, -1)).rotation_difference(Vector(direction).normalized()).to_matrix()


def heading_for(dx, dy):
    """Object Z rotation so a character modelled facing -Y faces world direction (dx, dy)."""
    return math.atan2(dy, dx) + pi / 2


def srgb(h, a=1.0):
    h = h.lstrip("#")
    c = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    lin = [x / 12.92 if x <= 0.04045 else ((x + 0.055) / 1.055) ** 2.4 for x in c]
    return (lin[0], lin[1], lin[2], a)


# ---------------------------------------------------------------- scene / collections
def get_coll(name, parent=None, scene=None):
    c = bpy.data.collections.get(name)
    if c is None:
        c = bpy.data.collections.new(name)
        (parent or (scene or bpy.context.scene).collection).children.link(c)
    return c


def link(ob, coll):
    coll.objects.link(ob)
    return ob


# ---------------------------------------------------------------- mesh primitives (bmesh)
def bm_box(bm, size, center=(0, 0, 0), bevel=0.0, segs=2):
    r = bmesh.ops.create_cube(bm, size=1.0)
    vs = r["verts"]
    for v in vs:
        v.co = Vector((v.co.x * size[0] + center[0], v.co.y * size[1] + center[1], v.co.z * size[2] + center[2]))
    if bevel > 0:
        edges = list({e for v in vs for e in v.link_edges})
        bmesh.ops.bevel(bm, geom=edges, offset=bevel, segments=segs, profile=0.5, affect="EDGES")
    return vs


def bm_ellipsoid(bm, radii, center=(0, 0, 0), seg=20, rings=12, rot=None):
    r = bmesh.ops.create_uvsphere(bm, u_segments=seg, v_segments=rings, radius=1.0)
    for v in r["verts"]:
        p = Vector((v.co.x * radii[0], v.co.y * radii[1], v.co.z * radii[2]))
        if rot is not None:
            p = rot @ p
        v.co = p + Vector(center)
    return r["verts"]


def bm_limb(bm, a, b, r1, r2, seg=14, squash=1.0):
    """Tapered cylinder from point a (radius r1) to b (radius r2)."""
    a, b = Vector(a), Vector(b)
    d = b - a
    L = d.length
    r = bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=seg, radius1=r1, radius2=r2, depth=L)
    q = Vector((0, 0, 1)).rotation_difference(d.normalized()).to_matrix()
    mid = (a + b) / 2
    for v in r["verts"]:
        p = Vector((v.co.x, v.co.y * squash, v.co.z))
        v.co = q @ p + mid
    return r["verts"]


def bm_flat_poly(bm, pts, thickness, y0=0.0):
    """Extrude a 2D (x, z) polygon along Y. Used for flat cel-animation geometry."""
    t = thickness / 2
    front = [bm.verts.new((x, y0 - t, z)) for x, z in pts]
    back = [bm.verts.new((x, y0 + t, z)) for x, z in pts]
    bm.faces.new(front)
    bm.faces.new(list(reversed(back)))
    n = len(pts)
    for i in range(n):
        j = (i + 1) % n
        bm.faces.new((front[j], front[i], back[i], back[j]))
    return front + back


def ellipse_pts(cx, cz, rx, rz, n=40, a0=0.0, a1=2 * pi):
    full = abs((a1 - a0) - 2 * pi) < 1e-6
    count = n if full else n + 1
    step = (a1 - a0) / n
    return [(cx + rx * cos(a0 + i * step), cz + rz * sin(a0 + i * step)) for i in range(count)]


def stroke_pts(path, w0, w1):
    """Polygon outline for a tapered stroke along a 2D polyline."""
    left, right = [], []
    n = len(path)
    for i, (x, z) in enumerate(path):
        if i < n - 1:
            dx, dz = path[i + 1][0] - x, path[i + 1][1] - z
        else:
            dx, dz = x - path[i - 1][0], z - path[i - 1][1]
        ln = math.hypot(dx, dz) or 1.0
        nx, nz = -dz / ln, dx / ln
        w = lerp(w0, w1, i / (n - 1)) / 2
        left.append((x + nx * w, z + nz * w))
        right.append((x - nx * w, z - nz * w))
    return left + list(reversed(right))


def mesh_from_bm(name, bm, smooth_shade=True):
    me = bpy.data.meshes.new(name)
    bm.normal_update()
    bm.to_mesh(me)
    bm.free()
    if smooth_shade:
        me.polygons.foreach_set("use_smooth", [True] * len(me.polygons))
    me.update()
    return me


def new_object(name, data, coll, mats=()):
    ob = bpy.data.objects.new(name, data)
    coll.objects.link(ob)
    if data is not None and hasattr(data, "materials"):
        for m in mats:
            data.materials.append(m)
    return ob


def box_object(name, size, center, coll, mat, bevel=0.0, rot_z=0.0):
    bm = bmesh.new()
    bm_box(bm, size, (0, 0, 0), bevel)
    ob = new_object(name, mesh_from_bm(name, bm, smooth_shade=bevel > 0), coll, [mat])
    ob.location = center
    ob.rotation_euler.z = rot_z
    return ob


def add_outline(ob, outline_mat, thickness=0.012):
    """Inverted-hull ink outline (Solidify + flipped normals + backface-culled black)."""
    me = ob.data
    if outline_mat.name not in [m.name for m in me.materials if m]:
        me.materials.append(outline_mat)
    idx = [m.name if m else None for m in me.materials].index(outline_mat.name)
    mod = ob.modifiers.new("INK_OUTLINE", "SOLIDIFY")
    mod.thickness = thickness
    mod.offset = 1.0
    mod.use_flip_normals = True
    mod.use_rim = False
    mod.material_offset = idx
    return mod


# ---------------------------------------------------------------- materials
def _mat(name):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    out.location = (600, 0)
    return m, nt, out


def _set(node, key, val):
    if key in node.inputs:
        node.inputs[key].default_value = val


def _coord(nt, kind="Object", scale=1.0):
    tc = nt.nodes.new("ShaderNodeTexCoord")
    if scale == 1.0:
        return tc.outputs[kind]
    mp = nt.nodes.new("ShaderNodeMapping")
    mp.inputs["Scale"].default_value = (scale, scale, scale)
    nt.links.new(tc.outputs[kind], mp.inputs["Vector"])
    return mp.outputs["Vector"]


def _noise(nt, vec, scale, detail=4.0, rough=0.55):
    n = nt.nodes.new("ShaderNodeTexNoise")
    n.inputs["Scale"].default_value = scale
    n.inputs["Detail"].default_value = detail
    n.inputs["Roughness"].default_value = rough
    nt.links.new(vec, n.inputs["Vector"])
    return n


def _bump(nt, height_socket, strength, distance=0.02, normal_in=None):
    b = nt.nodes.new("ShaderNodeBump")
    b.inputs["Strength"].default_value = strength
    b.inputs["Distance"].default_value = distance
    nt.links.new(height_socket, b.inputs["Height"])
    if normal_in is not None:
        nt.links.new(normal_in, b.inputs["Normal"])
    return b


def _mix_col(nt, a, b, fac):
    mx = nt.nodes.new("ShaderNodeMix")
    mx.data_type = "RGBA"
    for s, v in ((6, a), (7, b)):
        if isinstance(v, tuple):
            mx.inputs[s].default_value = v
        else:
            nt.links.new(v, mx.inputs[s])
    if isinstance(fac, float):
        mx.inputs[0].default_value = fac
    else:
        nt.links.new(fac, mx.inputs[0])
    return mx.outputs[2]


def _ramp(nt, fac, stops, interp="LINEAR"):
    r = nt.nodes.new("ShaderNodeValToRGB")
    r.color_ramp.interpolation = interp
    els = r.color_ramp.elements
    els[0].position, els[0].color = stops[0][0], stops[0][1]
    els[1].position, els[1].color = stops[-1][0], stops[-1][1]
    for pos, col in stops[1:-1]:
        e = els.new(pos)
        e.color = col
    nt.links.new(fac, r.inputs[0])
    return r


def principled(name, color, rough=0.5, metal=0.0, sheen=0.0, sss=0.0, spec=0.5, coat=0.0, bump=0.0,
               bump_scale=60.0, color_var=0.0):
    m, nt, out = _mat(name)
    b = nt.nodes.new("ShaderNodeBsdfPrincipled")
    col = srgb(color) if isinstance(color, str) else color
    _set(b, "Base Color", col)
    _set(b, "Roughness", rough)
    _set(b, "Metallic", metal)
    _set(b, "Specular IOR Level", spec)
    if sheen:
        _set(b, "Sheen Weight", sheen)
    if sss:
        _set(b, "Subsurface Weight", sss)
        _set(b, "Subsurface Radius", (1.0, 0.35, 0.2))
        _set(b, "Subsurface Scale", 0.012)
    if coat:
        _set(b, "Coat Weight", coat)
    vec = None
    if bump or color_var:
        vec = _coord(nt)
    if bump:
        n = _noise(nt, vec, bump_scale, 6.0, 0.6)
        bp = _bump(nt, n.outputs["Fac"], bump, 0.01)
        nt.links.new(bp.outputs["Normal"], b.inputs["Normal"])
    if color_var:
        n2 = _noise(nt, vec, bump_scale * 0.15, 3.0)
        dark = tuple(c * (1 - color_var) for c in col[:3]) + (1.0,)
        nt.links.new(_mix_col(nt, dark, col, n2.outputs["Fac"]), b.inputs["Base Color"])
    nt.links.new(b.outputs[0], out.inputs[0])
    return m


def skin(name, hexcol):
    return principled(name, hexcol, rough=0.52, sss=0.18, spec=0.42, bump=0.06, bump_scale=420.0, color_var=0.08)


def fabric(name, hexcol, rough=0.86, sheen=0.35, weave=900.0, strength=0.12, var=0.08):
    m, nt, out = _mat(name)
    b = nt.nodes.new("ShaderNodeBsdfPrincipled")
    col = srgb(hexcol)
    _set(b, "Roughness", rough)
    _set(b, "Sheen Weight", sheen)
    _set(b, "Specular IOR Level", 0.3)
    vec = _coord(nt)
    w = nt.nodes.new("ShaderNodeTexWave")
    w.wave_type = "BANDS"
    w.bands_direction = "DIAGONAL"
    w.inputs["Scale"].default_value = weave
    w.inputs["Distortion"].default_value = 1.5
    nt.links.new(vec, w.inputs["Vector"])
    bp = _bump(nt, w.outputs["Fac"], strength, 0.003)
    nt.links.new(bp.outputs["Normal"], b.inputs["Normal"])
    n2 = _noise(nt, vec, 6.0, 3.0)
    dark = tuple(c * (1 - var) for c in col[:3]) + (1.0,)
    nt.links.new(_mix_col(nt, dark, col, n2.outputs["Fac"]), b.inputs["Base Color"])
    nt.links.new(b.outputs[0], out.inputs[0])
    return m


def cap_twill(name, hexcol):
    """Cotton twill with diagonal weave normals; 'stitch' attribute lightens seam thread rows."""
    m, nt, out = _mat(name)
    b = nt.nodes.new("ShaderNodeBsdfPrincipled")
    col = srgb(hexcol)
    _set(b, "Roughness", 0.9)
    _set(b, "Sheen Weight", 0.3)
    _set(b, "Specular IOR Level", 0.28)
    vec = _coord(nt)
    w = nt.nodes.new("ShaderNodeTexWave")
    w.wave_type = "BANDS"
    w.bands_direction = "DIAGONAL"
    w.inputs["Scale"].default_value = 1400.0
    w.inputs["Distortion"].default_value = 0.6
    nt.links.new(vec, w.inputs["Vector"])
    attr = nt.nodes.new("ShaderNodeAttribute")
    attr.attribute_name = "stitch"
    dash = nt.nodes.new("ShaderNodeTexWave")
    dash.wave_type = "RINGS"
    dash.inputs["Scale"].default_value = 300.0
    nt.links.new(vec, dash.inputs["Vector"])
    gt = nt.nodes.new("ShaderNodeMath")
    gt.operation = "GREATER_THAN"
    gt.inputs[1].default_value = 0.5
    nt.links.new(dash.outputs["Fac"], gt.inputs[0])
    mul = nt.nodes.new("ShaderNodeMath")
    mul.operation = "MULTIPLY"
    nt.links.new(attr.outputs["Fac"], mul.inputs[0])
    nt.links.new(gt.outputs[0], mul.inputs[1])
    h = nt.nodes.new("ShaderNodeMath")
    h.operation = "ADD"
    nt.links.new(w.outputs["Fac"], h.inputs[0])
    nt.links.new(mul.outputs[0], h.inputs[1])
    bp = _bump(nt, h.outputs[0], 0.18, 0.002)
    nt.links.new(bp.outputs["Normal"], b.inputs["Normal"])
    thread = tuple(min(1.0, c * 1.35 + 0.01) for c in col[:3]) + (1.0,)
    nt.links.new(_mix_col(nt, col, thread, mul.outputs[0]), b.inputs["Base Color"])
    nt.links.new(b.outputs[0], out.inputs[0])
    m["cap_base_hex"] = hexcol
    return m


def leather(name, hexcol="#141213"):
    m, nt, out = _mat(name)
    b = nt.nodes.new("ShaderNodeBsdfPrincipled")
    vec = _coord(nt)
    n = _noise(nt, vec, 18.0, 8.0, 0.65)
    nt.links.new(_mix_col(nt, srgb(hexcol), srgb("#2E2622"), n.outputs["Fac"]), b.inputs["Base Color"])
    r = nt.nodes.new("ShaderNodeMapRange")
    r.inputs["To Min"].default_value = 0.38
    r.inputs["To Max"].default_value = 0.68
    nt.links.new(n.outputs["Fac"], r.inputs["Value"])
    nt.links.new(r.outputs[0], b.inputs["Roughness"])
    n2 = _noise(nt, vec, 260.0, 6.0, 0.6)
    bp = _bump(nt, n2.outputs["Fac"], 0.12, 0.004)
    nt.links.new(bp.outputs["Normal"], b.inputs["Normal"])
    nt.links.new(b.outputs[0], out.inputs[0])
    return m


def patterned_shirt(name, base="#D9CDAF", ink="#7A5A3A"):
    m, nt, out = _mat(name)
    b = nt.nodes.new("ShaderNodeBsdfPrincipled")
    _set(b, "Roughness", 0.82)
    _set(b, "Sheen Weight", 0.3)
    vec = _coord(nt)
    v = nt.nodes.new("ShaderNodeTexVoronoi")
    v.inputs["Scale"].default_value = 26.0
    nt.links.new(vec, v.inputs["Vector"])
    rp = _ramp(nt, v.outputs["Distance"], [(0.0, srgb(ink)), (0.18, srgb(ink)), (0.2, srgb(base)), (1.0, srgb(base))], "CONSTANT")
    nt.links.new(rp.outputs[0], b.inputs["Base Color"])
    nt.links.new(b.outputs[0], out.inputs[0])
    return m


def emission(name, hexcol, strength=5.0):
    m, nt, out = _mat(name)
    e = nt.nodes.new("ShaderNodeEmission")
    e.inputs["Color"].default_value = srgb(hexcol)
    e.inputs["Strength"].default_value = strength
    nt.links.new(e.outputs[0], out.inputs[0])
    return m


def cel(name, lit_hex, shade_hex, strength=0.55, threshold=0.004):
    """Flat two-tone cel shading: lit or shadow tone only, no gradients. Receives real shadows."""
    m, nt, out = _mat(name)
    d = nt.nodes.new("ShaderNodeBsdfDiffuse")
    d.inputs["Color"].default_value = (1, 1, 1, 1)
    s2r = nt.nodes.new("ShaderNodeShaderToRGB")
    nt.links.new(d.outputs[0], s2r.inputs[0])
    bw = nt.nodes.new("ShaderNodeRGBToBW")
    nt.links.new(s2r.outputs[0], bw.inputs[0])
    gt = nt.nodes.new("ShaderNodeMath")
    gt.operation = "GREATER_THAN"
    gt.inputs[1].default_value = threshold
    nt.links.new(bw.outputs[0], gt.inputs[0])
    col = _mix_col(nt, srgb(shade_hex), srgb(lit_hex), gt.outputs[0])
    e = nt.nodes.new("ShaderNodeEmission")
    e.inputs["Strength"].default_value = strength
    nt.links.new(col, e.inputs["Color"])
    nt.links.new(e.outputs[0], out.inputs[0])
    m["cel"] = True
    return m


def ink_outline(name="MAT_CEL_INK_OUTLINE"):
    m = bpy.data.materials.get(name)
    if m:
        return m
    m, nt, out = _mat(name)
    e = nt.nodes.new("ShaderNodeEmission")
    e.inputs["Color"].default_value = srgb("#0B0A0C")
    e.inputs["Strength"].default_value = 1.0
    nt.links.new(e.outputs[0], out.inputs[0])
    m.use_backface_culling = True
    try:
        m.use_backface_culling_shadow = True
    except AttributeError:
        pass
    return m


# ---------------------------------------------------------------- keyframe writing
def write_action(idblock, action_name, channels, interp="LINEAR", constant_frames=()):
    """channels: {(data_path, index): [(frame, value), ...]} -> new Action assigned to idblock."""
    act = bpy.data.actions.new(action_name)
    for (path, idx), keys in channels.items():
        keys = sorted(keys)
        fc = act.fcurves.new(path, index=idx)
        fc.keyframe_points.add(len(keys))
        flat = []
        for f, v in keys:
            flat += [f, v]
        fc.keyframe_points.foreach_set("co", flat)
        for kp in fc.keyframe_points:
            kp.interpolation = "CONSTANT" if int(round(kp.co.x)) in constant_frames else interp
        fc.update()
    if idblock is not None:
        if idblock.animation_data is None:
            idblock.animation_data_create()
        idblock.animation_data.action = act
    return act


def push_nla(idblock, actions_with_start):
    """Turn shot-specific actions into sequential NLA strips on one track (hold forward between shots)."""
    ad = idblock.animation_data or idblock.animation_data_create()
    ad.action = None
    tr = ad.nla_tracks.new()
    tr.name = idblock.name + "_SHOTS"
    for i, (start, act) in enumerate(sorted(actions_with_start, key=lambda x: x[0])):
        st = tr.strips.new(act.name, int(start), act)
        st.extrapolation = "HOLD" if i == 0 else "HOLD_FORWARD"
        st.blend_type = "REPLACE"
    return tr


def safe_set(obj, attr, val):
    try:
        setattr(obj, attr, val)
        return True
    except (AttributeError, TypeError, ValueError):
        return False
