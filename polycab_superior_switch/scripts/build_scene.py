"""Builds the Polycab "Superior Switch" 5-second film scene and saves scenes/polycab_superior_switch.blend.

    blender -b --factory-startup --python scripts/build_scene.py

Everything is procedural: there are no external textures, so nothing needs packing. Real-world metres throughout.
Timing lives in TIMING; fan speed and light cue levels are driven from the CTRL_Fan and CTRL_Lights empties in
08_ANIMATION_CONTROLS, so the film can be re-timed by moving keys on one controller."""

import math
import os

import bmesh
import bpy
from mathutils import Euler, Matrix, Vector

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUT_BLEND = os.path.join(ROOT, "scenes", "polycab_superior_switch.blend")

FPS = 24
FRAMES = (1, 120)
LENS = 28.0

# room (interior faces). Camera looks along +Y towards the feature wall.
RX0, RX1, RY0, RY1 = -2.5, 2.5, -3.2, 2.6
WIN_Y = (-0.25, 2.30)            # full-height window in the left wall (towards the back corner)
CEIL = 2.75                      # false ceiling soffit
TRAY = 3.00                      # recessed tray ceiling
TRAY_X, TRAY_Y = (-1.80, 1.30), (-0.85, 2.15)
FAN_XY = (-0.25, 0.65)
SLAT_X = (-2.48, 1.30)            # walnut slat feature wall; shelving niche to its right
ART_X = -0.62
SHELF_Z = (1.05, 1.42, 1.79)

TIMING = dict(
    thumb_down=44, thumb_up=50,          # remote press
    fan_start=47, fan_ramp=44,           # fan: eased spin-up over fan_ramp frames
    fan_rpm=150.0,                       # terminal speed (a mid setting of the 25-step controller; 360 rpm max)
    wash=(56, 66), perim=(60, 70), cove=(63, 80), shelf=(68, 82), string=(76, 96),
)

COLLS = ["01_ARCHITECTURE", "02_INTERIOR_ASSETS", "03_POLYCAB_AERORUSH", "04_REMOTE_CONTROL",
         "05_LIGHTING_FIXTURES", "06_LIGHT_RIG", "07_CAMERA_RIG", "08_ANIMATION_CONTROLS", "09_BRANDING",
         "10_RENDER_SETTINGS"]


# ======================================================================== helpers
def coll(name):
    c = bpy.data.collections.get(name)
    if c is None:
        c = bpy.data.collections.new(name)
        bpy.context.scene.collection.children.link(c)
    return c


def link(ob, cname):
    coll(cname).objects.link(ob)
    return ob


def mesh_obj(name, bm, cname, mat=None, smooth=False):
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new(name, me)
    if mat is not None:
        ob.data.materials.append(mat)
    if smooth:
        for p in me.polygons:
            p.use_smooth = True
    return link(ob, cname)


def bm_box(bm, x0, x1, y0, y1, z0, z1):
    vs = [bm.verts.new(v) for v in ((x0, y0, z0), (x1, y0, z0), (x1, y1, z0), (x0, y1, z0),
                                    (x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1))]
    for f in ((0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)):
        bm.faces.new([vs[i] for i in f])


def bevel(ob, w, seg=2):
    md = ob.modifiers.new("Bevel", "BEVEL")
    md.width = w
    md.segments = seg
    md.limit_method = "ANGLE"
    return ob


def box(name, x0, x1, y0, y1, z0, z1, mat, cname, bev=0.0, seg=2):
    bm = bmesh.new()
    bm_box(bm, x0, x1, y0, y1, z0, z1)
    ob = mesh_obj(name, bm, cname, mat)
    if bev:
        bevel(ob, bev, seg)
    return ob


def lathe(name, prof, mat, cname, loc=(0, 0, 0), n=48, smooth=True):
    """Revolve a list of (r, z) points around local Z."""
    bm = bmesh.new()
    axis = {i: bm.verts.new((0, 0, z)) for i, (r, z) in enumerate(prof) if r < 1e-6}
    rings = []
    for k in range(n):
        a = 2 * math.pi * k / n
        rings.append([axis[i] if i in axis else bm.verts.new((r * math.cos(a), r * math.sin(a), z))
                      for i, (r, z) in enumerate(prof)])
    for k in range(n):
        r0, r1 = rings[k], rings[(k + 1) % n]
        for i in range(len(prof) - 1):
            vs = []
            for v in (r0[i], r1[i], r1[i + 1], r0[i + 1]):
                if v not in vs:
                    vs.append(v)
            if len(vs) >= 3:
                bm.faces.new(vs)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    ob = mesh_obj(name, bm, cname, mat, smooth)
    ob.location = loc
    return ob


def cyl(name, r, z0, z1, mat, cname, loc=(0, 0), n=32, bev=0.0):
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, segments=n, radius1=r, radius2=r, depth=z1 - z0,
                          matrix=Matrix.Translation((0, 0, (z1 - z0) / 2)))
    ob = mesh_obj(name, bm, cname, mat)
    ob.location = (loc[0], loc[1], z0)
    if bev:
        bevel(ob, bev, 2)
    return ob


def sphere(name, r, loc, mat, cname, scale=(1, 1, 1), seg=(24, 12)):
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=seg[0], v_segments=seg[1], radius=r)
    ob = mesh_obj(name, bm, cname, mat, True)
    ob.location = loc
    ob.scale = scale
    return ob


def empty(name, loc, cname, kind="PLAIN_AXES", size=0.2):
    e = bpy.data.objects.new(name, None)
    e.empty_display_type = kind
    e.empty_display_size = size
    e.location = loc
    return link(e, cname)


def kelvin_rgb(k):
    t = k / 100.0
    r = 255 if t <= 66 else 329.698727446 * (t - 60) ** -0.1332047592
    g = 99.4708025861 * math.log(t) - 161.1195681661 if t <= 66 else 288.1221695283 * (t - 60) ** -0.0755148492
    b = 255 if t >= 66 else (0 if t <= 19 else 138.5177312231 * math.log(t - 10) - 305.0447927307)

    def lin(c):
        c = min(max(c, 0), 255) / 255
        return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
    return (lin(r), lin(g), lin(b))


def light(name, kind, loc, power, cname, k=2850, size=0.05, spot=None, rot=(0, 0, 0), size_y=None):
    ld = bpy.data.lights.new(name, kind)
    ld.energy = power
    ld.color = kelvin_rgb(k)
    if kind in ("POINT", "SPOT"):
        ld.shadow_soft_size = size
    if kind == "SPOT" and spot:
        ld.spot_size = math.radians(spot)
        ld.spot_blend = 0.75
    if kind == "AREA":
        ld.shape = "RECTANGLE"
        ld.size = size
        ld.size_y = size_y if size_y else size
    ob = bpy.data.objects.new(name, ld)
    ob.location = loc
    ob.rotation_euler = rot
    return link(ob, cname)


def fcurves_of(idblock):
    ad = idblock.animation_data
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


def _coords(n, scale=1.0, kind="Object"):
    tc = n.new("ShaderNodeTexCoord")
    mp = n.new("ShaderNodeMapping")
    mp.inputs["Scale"].default_value = (scale, scale, scale)
    n.id_data.links.new(tc.outputs[kind], mp.inputs["Vector"])
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


def mat_wood(name, c0, c1, rough, axis="X", stretch=0.12, plank=None, coat=0.12):
    """Wood grain along local `axis`, fine pores, per-board colour variation when plank=(len, width)."""
    m, n, l, b = _mat(name)
    mp = _coords(n)
    gm = n.new("ShaderNodeMapping")
    sc = {"X": (stretch, 1.6, 1.6), "Z": (1.6, 1.6, stretch), "Y": (1.6, stretch, 1.6)}[axis]
    gm.inputs["Scale"].default_value = sc
    l.new(mp.outputs[0], gm.inputs["Vector"])
    wave = n.new("ShaderNodeTexWave")
    wave.wave_type = "RINGS"
    wave.rings_direction = axis
    wave.inputs["Scale"].default_value = 3.0
    wave.inputs["Distortion"].default_value = 7.0
    wave.inputs["Detail"].default_value = 4.0
    wave.inputs["Detail Scale"].default_value = 1.5
    l.new(gm.outputs[0], wave.inputs["Vector"])
    pores = n.new("ShaderNodeTexNoise")
    pm = n.new("ShaderNodeMapping")
    pm.inputs["Scale"].default_value = tuple(v * 60 for v in sc)
    l.new(mp.outputs[0], pm.inputs["Vector"])
    l.new(pm.outputs[0], pores.inputs["Vector"])
    pores.inputs["Scale"].default_value = 4.0
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
    col = ramp.outputs["Color"]
    if plank:
        # per-object random tint so neighbouring slats/boards differ slightly
        oi = n.new("ShaderNodeObjectInfo")
        tint = n.new("ShaderNodeMix")
        tint.data_type = "RGBA"
        tint.blend_type = "MULTIPLY"
        tint.inputs["Factor"].default_value = 1.0
        tr = _ramp(n, (0.86, 0.86, 0.86), (1.08, 1.05, 1.02))
        l.new(oi.outputs["Random"], tr.inputs["Fac"])
        l.new(col, tint.inputs["A"])
        l.new(tr.outputs["Color"], tint.inputs["B"])
        col = tint.outputs["Result"]
    l.new(col, b.inputs["Base Color"])
    rr = n.new("ShaderNodeMapRange")
    rr.inputs["To Min"].default_value = rough - 0.08
    rr.inputs["To Max"].default_value = rough + 0.10
    l.new(pores.outputs["Fac"], rr.inputs["Value"])
    l.new(rr.outputs["Result"], b.inputs["Roughness"])
    _set(b, coat=coat, coat_rough=0.4, spec=0.45)
    hh = n.new("ShaderNodeMath")
    hh.operation = "ADD"
    l.new(wave.outputs["Fac"], hh.inputs[0])
    l.new(pores.outputs["Fac"], hh.inputs[1])
    _bump(n, l, hh.outputs[0], b, 0.08, 0.001)
    m.diffuse_color = (*c1, 1)
    return m


def mat_stone_tile(name, a, b_, rough, tile):
    m, n, l, b = _mat(name)
    mp = _coords(n)
    noise = n.new("ShaderNodeTexNoise")
    noise.inputs["Scale"].default_value = 1.6
    noise.inputs["Detail"].default_value = 9.0
    noise.inputs["Roughness"].default_value = 0.62
    l.new(mp.outputs[0], noise.inputs["Vector"])
    ramp = _ramp(n, a, b_, (0.3, 0.75))
    l.new(noise.outputs["Fac"], ramp.inputs["Fac"])
    brick = n.new("ShaderNodeTexBrick")
    brick.offset = 0.5
    brick.inputs["Scale"].default_value = 1.0
    brick.inputs["Mortar Size"].default_value = 0.0018
    brick.inputs["Mortar Smooth"].default_value = 0.3
    brick.inputs["Brick Width"].default_value = tile[0]
    brick.inputs["Row Height"].default_value = tile[1]
    brick.inputs["Color1"].default_value = (1, 1, 1, 1)
    brick.inputs["Color2"].default_value = (0.95, 0.94, 0.93, 1)
    brick.inputs["Mortar"].default_value = (0.62, 0.58, 0.52, 1)
    l.new(mp.outputs[0], brick.inputs["Vector"])
    mul = n.new("ShaderNodeMix")
    mul.data_type = "RGBA"
    mul.blend_type = "MULTIPLY"
    mul.inputs["Factor"].default_value = 1.0
    l.new(ramp.outputs["Color"], mul.inputs["A"])
    l.new(brick.outputs["Color"], mul.inputs["B"])
    l.new(mul.outputs["Result"], b.inputs["Base Color"])
    rr = n.new("ShaderNodeMapRange")
    rr.inputs["To Min"].default_value = rough
    rr.inputs["To Max"].default_value = rough + 0.12
    l.new(noise.outputs["Fac"], rr.inputs["Value"])
    l.new(rr.outputs["Result"], b.inputs["Roughness"])
    inv = n.new("ShaderNodeMath")
    inv.operation = "SUBTRACT"
    inv.inputs[0].default_value = 1.0
    l.new(brick.outputs["Fac"], inv.inputs[1])
    _bump(n, l, inv.outputs[0], b, 0.25, 0.0015)
    m.diffuse_color = (*b_, 1)
    return m


def mat_fabric(name, col, rough=0.92, sheen=0.45, scale=520.0, weave=True):
    """Woven upholstery: two crossed band textures (warp/weft) plus slub noise."""
    m, n, l, b = _mat(name)
    mp = _coords(n)
    w1 = n.new("ShaderNodeTexWave")
    w1.bands_direction = "X"
    w1.inputs["Scale"].default_value = scale
    w1.inputs["Distortion"].default_value = 1.5
    w2 = n.new("ShaderNodeTexWave")
    w2.bands_direction = "Z"
    w2.inputs["Scale"].default_value = scale
    w2.inputs["Distortion"].default_value = 1.5
    l.new(mp.outputs[0], w1.inputs["Vector"])
    l.new(mp.outputs[0], w2.inputs["Vector"])
    wv = n.new("ShaderNodeMath")
    wv.operation = "MULTIPLY"
    l.new(w1.outputs["Fac"], wv.inputs[0])
    l.new(w2.outputs["Fac"], wv.inputs[1])
    slub = n.new("ShaderNodeTexNoise")
    slub.inputs["Scale"].default_value = 40.0
    slub.inputs["Detail"].default_value = 6.0
    l.new(mp.outputs[0], slub.inputs["Vector"])
    ramp = _ramp(n, tuple(c * 0.82 for c in col), col, (0.25, 0.8))
    l.new(slub.outputs["Fac"], ramp.inputs["Fac"])
    l.new(ramp.outputs["Color"], b.inputs["Base Color"])
    _set(b, rough=rough, sheen=sheen, sheen_rough=0.45, spec=0.25)
    _bump(n, l, wv.outputs[0] if weave else slub.outputs["Fac"], b, 0.3, 0.0008)
    m.diffuse_color = (*col, 1)
    return m


def mat_plain(name, col, rough=0.5, metal=0.0, aniso=0.0, coat=0.0, trans=0.0, ior=1.5, spec=0.5, sss=0.0):
    m, n, l, b = _mat(name)
    _set(b, base=col, rough=rough, metal=metal, aniso=aniso, coat=coat, trans=trans, ior=ior, spec=spec, sss=sss)
    m.diffuse_color = (*col, 1)
    return m


def mat_emit(name, k, strength, col=None):
    """Pure emission whose strength is driven by a light-cue channel (see drive_value)."""
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    nt.nodes.remove(nt.nodes["Principled BSDF"])
    em = nt.nodes.new("ShaderNodeEmission")
    em.inputs["Color"].default_value = (*(col or kelvin_rgb(k)), 1)
    em.inputs["Strength"].default_value = strength
    nt.links.new(em.outputs[0], nt.nodes["Material Output"].inputs["Surface"])
    m.diffuse_color = (*(col or kelvin_rgb(k)), 1)
    return m


def mat_flame(name):
    """Diya flame: emission with a vertical gradient (white-yellow core to orange tip), slightly see-through."""
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    n, l = nt.nodes, nt.links
    n.remove(n["Principled BSDF"])
    tc = n.new("ShaderNodeTexCoord")
    sep = n.new("ShaderNodeSeparateXYZ")
    l.new(tc.outputs["Generated"], sep.inputs[0])
    rp = n.new("ShaderNodeValToRGB")
    rp.color_ramp.elements[0].color = (1.0, 0.78, 0.42, 1)
    rp.color_ramp.elements[1].position = 0.9
    rp.color_ramp.elements[1].color = (1.0, 0.32, 0.05, 1)
    l.new(sep.outputs["Z"], rp.inputs["Fac"])
    em = n.new("ShaderNodeEmission")
    em.inputs["Strength"].default_value = 18.0
    l.new(rp.outputs["Color"], em.inputs["Color"])
    l.new(em.outputs[0], n["Material Output"].inputs["Surface"])
    m.diffuse_color = (1, 0.6, 0.2, 1)
    return m


def mat_glass(name):
    m, n, l, b = _mat(name)
    _set(b, base=(0.96, 0.99, 0.98), rough=0.0, trans=1.0, ior=1.52)
    tr = n.new("ShaderNodeBsdfTransparent")
    tr.inputs["Color"].default_value = (0.9, 0.93, 0.92, 1)
    lp = n.new("ShaderNodeLightPath")
    mx = n.new("ShaderNodeMath")
    mx.operation = "MAXIMUM"
    l.new(lp.outputs["Is Shadow Ray"], mx.inputs[0])
    l.new(lp.outputs["Is Diffuse Ray"], mx.inputs[1])
    mix = n.new("ShaderNodeMixShader")
    l.new(mx.outputs[0], mix.inputs["Fac"])
    l.new(b.outputs[0], mix.inputs[1])
    l.new(tr.outputs[0], mix.inputs[2])
    l.new(mix.outputs[0], n["Material Output"].inputs["Surface"])
    m.diffuse_color = (0.8, 0.9, 0.9, 0.3)
    return m


def mat_sheer(name, col):
    """Sheer voile: translucent + partly transparent so dusk light glows through."""
    m, n, l, b = _mat(name)
    _set(b, base=col, rough=0.8, sheen=0.4)
    tl = n.new("ShaderNodeBsdfTranslucent")
    tl.inputs["Color"].default_value = (*col, 1)
    tr = n.new("ShaderNodeBsdfTransparent")
    m1 = n.new("ShaderNodeMixShader")
    m1.inputs["Fac"].default_value = 0.45
    l.new(b.outputs[0], m1.inputs[1])
    l.new(tl.outputs[0], m1.inputs[2])
    m2 = n.new("ShaderNodeMixShader")
    m2.inputs["Fac"].default_value = 0.35
    l.new(m1.outputs[0], m2.inputs[1])
    l.new(tr.outputs[0], m2.inputs[2])
    l.new(m2.outputs[0], n["Material Output"].inputs["Surface"])
    m.diffuse_color = (*col, 1)
    return m


def mat_skin(name):
    m, n, l, b = _mat(name)
    mp = _coords(n)
    nz = n.new("ShaderNodeTexNoise")
    nz.inputs["Scale"].default_value = 300.0
    nz.inputs["Detail"].default_value = 8.0
    l.new(mp.outputs[0], nz.inputs["Vector"])
    rp = _ramp(n, (0.17, 0.085, 0.05), (0.23, 0.12, 0.072), (0.3, 0.7))
    l.new(nz.outputs["Fac"], rp.inputs["Fac"])
    l.new(rp.outputs["Color"], b.inputs["Base Color"])
    _set(b, rough=0.48, sss=0.25, spec=0.5)
    b.inputs["Subsurface Radius"].default_value = (0.9, 0.38, 0.22)
    b.inputs["Subsurface Scale"].default_value = 0.006
    _bump(n, l, nz.outputs["Fac"], b, 0.12, 0.0004)
    m.diffuse_color = (0.36, 0.2, 0.12, 1)
    return m


def mat_marigold(name):
    m, n, l, b = _mat(name)
    mp = _coords(n)
    vo = n.new("ShaderNodeTexVoronoi")
    vo.inputs["Scale"].default_value = 160.0
    l.new(mp.outputs[0], vo.inputs["Vector"])
    rp = _ramp(n, (0.55, 0.13, 0.0), (0.95, 0.42, 0.02), (0.0, 0.6))
    l.new(vo.outputs["Distance"], rp.inputs["Fac"])
    l.new(rp.outputs["Color"], b.inputs["Base Color"])
    _set(b, rough=0.7, sheen=0.5, sss=0.2)
    _bump(n, l, vo.outputs["Distance"], b, 0.6, 0.002)
    m.diffuse_color = (0.9, 0.4, 0.02, 1)
    return m


def mat_artwork(name):
    """Minimal abstract canvas: warm stone ground with two overlapping arches and a sun disc (procedural)."""
    m, n, l, b = _mat(name)
    tc = n.new("ShaderNodeTexCoord")
    sep = n.new("ShaderNodeSeparateXYZ")
    l.new(tc.outputs["UV"], sep.inputs[0])

    def shape(cx, cy, r, rect_bottom=True):
        # arch: union of a disc at (cx, cy) and a rectangle below it
        dx = n.new("ShaderNodeMath"); dx.operation = "SUBTRACT"; dx.inputs[1].default_value = cx
        l.new(sep.outputs["X"], dx.inputs[0])
        dy = n.new("ShaderNodeMath"); dy.operation = "SUBTRACT"; dy.inputs[1].default_value = cy
        l.new(sep.outputs["Y"], dy.inputs[0])
        cmb = n.new("ShaderNodeCombineXYZ")
        l.new(dx.outputs[0], cmb.inputs["X"])
        l.new(dy.outputs[0], cmb.inputs["Y"])
        ln = n.new("ShaderNodeVectorMath"); ln.operation = "LENGTH"
        l.new(cmb.outputs[0], ln.inputs[0])
        disc = n.new("ShaderNodeMath"); disc.operation = "LESS_THAN"; disc.inputs[1].default_value = r
        l.new(ln.outputs["Value"], disc.inputs[0])
        if not rect_bottom:
            return disc.outputs[0]
        ax = n.new("ShaderNodeMath"); ax.operation = "ABSOLUTE"
        l.new(dx.outputs[0], ax.inputs[0])
        inx = n.new("ShaderNodeMath"); inx.operation = "LESS_THAN"; inx.inputs[1].default_value = r
        l.new(ax.outputs[0], inx.inputs[0])
        below = n.new("ShaderNodeMath"); below.operation = "LESS_THAN"; below.inputs[1].default_value = cy
        l.new(sep.outputs["Y"], below.inputs[0])
        abv = n.new("ShaderNodeMath"); abv.operation = "GREATER_THAN"; abv.inputs[1].default_value = 0.14
        l.new(sep.outputs["Y"], abv.inputs[0])
        r1 = n.new("ShaderNodeMath"); r1.operation = "MULTIPLY"
        l.new(inx.outputs[0], r1.inputs[0]); l.new(below.outputs[0], r1.inputs[1])
        r2 = n.new("ShaderNodeMath"); r2.operation = "MULTIPLY"
        l.new(r1.outputs[0], r2.inputs[0]); l.new(abv.outputs[0], r2.inputs[1])
        u = n.new("ShaderNodeMath"); u.operation = "MAXIMUM"
        l.new(disc.outputs[0], u.inputs[0]); l.new(r2.outputs[0], u.inputs[1])
        return u.outputs[0]

    col = n.new("ShaderNodeRGB")
    col.outputs[0].default_value = (0.66, 0.58, 0.47, 1)
    out = col.outputs[0]
    for mask, c in ((shape(0.40, 0.52, 0.20), (0.38, 0.22, 0.13)), (shape(0.60, 0.44, 0.17), (0.80, 0.70, 0.56)),
                    (shape(0.66, 0.74, 0.07, False), (0.55, 0.20, 0.10))):
        mx = n.new("ShaderNodeMix")
        mx.data_type = "RGBA"
        l.new(mask, mx.inputs["Factor"])
        l.new(out, mx.inputs["A"])
        mx.inputs["B"].default_value = (*c, 1)
        out = mx.outputs["Result"]
    l.new(out, b.inputs["Base Color"])
    nz = n.new("ShaderNodeTexNoise")
    nz.inputs["Scale"].default_value = 400.0
    l.new(tc.outputs["UV"], nz.inputs["Vector"])
    _set(b, rough=0.9, spec=0.3)
    _bump(n, l, nz.outputs["Fac"], b, 0.15, 0.0005)
    m.diffuse_color = (0.66, 0.58, 0.47, 1)
    return m


def build_materials():
    MAT["Walnut"] = mat_wood("MAT_Walnut_Slat", (0.10, 0.055, 0.03), (0.24, 0.14, 0.075), 0.42, axis="Z",
                             plank=True)
    MAT["WalnutFurn"] = mat_wood("MAT_Walnut_Furniture", (0.10, 0.055, 0.03), (0.22, 0.13, 0.07), 0.36)
    MAT["Floor"] = mat_stone_tile("MAT_Floor_Stone_1200x600", (0.62, 0.56, 0.48), (0.74, 0.69, 0.61), 0.28,
                                  (1.2, 0.6))
    MAT["Ceiling"] = mat_plain("MAT_Ceiling_Matte_Paint", (0.80, 0.78, 0.74), rough=0.92, spec=0.3)
    m, n, l, b = _mat("MAT_Wall_Paint_Warm")
    mp = _coords(n)
    nz = n.new("ShaderNodeTexNoise")
    nz.inputs["Scale"].default_value = 30.0
    nz.inputs["Detail"].default_value = 10.0
    l.new(mp.outputs[0], nz.inputs["Vector"])
    rp = _ramp(n, (0.62, 0.55, 0.46), (0.67, 0.60, 0.51), (0.3, 0.7))
    l.new(nz.outputs["Fac"], rp.inputs["Fac"])
    l.new(rp.outputs["Color"], b.inputs["Base Color"])
    _set(b, rough=0.9, spec=0.3)
    _bump(n, l, nz.outputs["Fac"], b, 0.03)
    MAT["Wall"] = m
    MAT["Sofa"] = mat_fabric("MAT_Sofa_Woven_Cream", (0.76, 0.70, 0.60))
    MAT["Rust"] = mat_fabric("MAT_Cushion_Rust_Red", (0.36, 0.06, 0.04), scale=420)
    MAT["Ivory"] = mat_fabric("MAT_Cushion_Ivory", (0.80, 0.76, 0.68), scale=420)
    MAT["Rug"] = mat_fabric("MAT_Rug_Wool_Sand", (0.55, 0.48, 0.40), 1.0, 0.5, 300.0)
    MAT["Curtain"] = mat_fabric("MAT_Curtain_Linen_Taupe", (0.48, 0.40, 0.32), scale=600)
    MAT["Sheer"] = mat_sheer("MAT_Curtain_Sheer", (0.82, 0.78, 0.70))
    MAT["Glass"] = mat_glass("MAT_Window_Glass")
    MAT["Frame"] = mat_plain("MAT_Window_Frame_Bronze", (0.06, 0.05, 0.045), rough=0.45, metal=0.7)
    MAT["Brass"] = mat_plain("MAT_Brass_Brushed", (0.62, 0.45, 0.22), rough=0.28, metal=1.0, aniso=0.5)
    MAT["Ceramic"] = mat_plain("MAT_Ceramic_Glazed_Ivory", (0.78, 0.74, 0.66), rough=0.18, coat=0.4)
    MAT["CeramicDark"] = mat_plain("MAT_Ceramic_Matte_Charcoal", (0.05, 0.045, 0.04), rough=0.6)
    MAT["Clay"] = mat_plain("MAT_Terracotta_Diya", (0.36, 0.14, 0.06), rough=0.75)
    MAT["Oil"] = mat_plain("MAT_Ghee_Oil", (0.45, 0.30, 0.08), rough=0.05, coat=1.0)
    MAT["Flame"] = mat_flame("MAT_Diya_Flame")
    MAT["Foliage"] = mat_plain("MAT_Foliage", (0.035, 0.09, 0.03), rough=0.5, sss=0.1)
    MAT["Pot"] = mat_plain("MAT_Planter_Stone", (0.32, 0.29, 0.25), rough=0.8)
    MAT["Marigold"] = mat_marigold("MAT_Marigold")
    MAT["Art"] = mat_artwork("MAT_Artwork_Canvas")
    MAT["ArtFrame"] = mat_wood("MAT_Artwork_Frame_Oak", (0.30, 0.20, 0.11), (0.45, 0.32, 0.19), 0.45, coat=0.0)
    MAT["Shade"] = mat_plain("MAT_Lamp_Shade_Linen", (0.86, 0.78, 0.64), rough=0.9)
    MAT["Shade"].node_tree.nodes["Principled BSDF"].inputs["Transmission Weight"].default_value = 0.45
    MAT["Book1"] = mat_plain("MAT_Book_Cover_Sage", (0.20, 0.23, 0.17), rough=0.7)
    MAT["Book2"] = mat_plain("MAT_Book_Cover_Clay", (0.45, 0.30, 0.20), rough=0.7)
    MAT["Paper"] = mat_plain("MAT_Book_Pages", (0.75, 0.71, 0.62), rough=0.9)
    MAT["Trim"] = mat_plain("MAT_Downlight_Trim_White", (0.75, 0.75, 0.73), rough=0.35)
    MAT["Reflector"] = mat_plain("MAT_Downlight_Reflector", (0.85, 0.85, 0.85), rough=0.15, metal=1.0)
    MAT["Wire"] = mat_plain("MAT_String_Wire", (0.12, 0.10, 0.06), rough=0.4, metal=0.5)
    # fan finishes (Aerorush "Classic Black" variant from the official product photos)
    MAT["FanBody"] = mat_plain("MAT_Aerorush_Classic_Black", (0.018, 0.018, 0.019), rough=0.38, coat=0.35)
    MAT["FanBlade"] = mat_plain("MAT_Aerorush_Blade_Black", (0.02, 0.02, 0.021), rough=0.42, coat=0.25)
    MAT["FanRing"] = mat_plain("MAT_Aerorush_Decor_Ring_Chrome", (0.86, 0.86, 0.86), rough=0.1, metal=1.0)
    MAT["Rivet"] = mat_plain("MAT_Aerorush_Rivet", (0.5, 0.5, 0.5), rough=0.3, metal=1.0)
    # remote / hand
    MAT["Remote"] = mat_plain("MAT_Remote_Satin_Black", (0.015, 0.015, 0.016), rough=0.32, coat=0.2)
    MAT["Button"] = mat_plain("MAT_Remote_Button_Rubber", (0.06, 0.06, 0.064), rough=0.6)
    MAT["Icon"] = mat_plain("MAT_Remote_Icon_Print", (0.7, 0.7, 0.7), rough=0.5)
    MAT["Skin"] = mat_skin("MAT_Skin_Hand")
    MAT["Sleeve"] = mat_fabric("MAT_Sleeve_Cotton_Navy", (0.04, 0.05, 0.08), scale=900)
    MAT["Nail"] = mat_plain("MAT_Nail", (0.45, 0.30, 0.25), rough=0.25, sss=0.2)


# ======================================================================== architecture
def build_architecture():
    c = "01_ARCHITECTURE"
    t = 0.2
    box("ARCH_Floor", RX0 - t, RX1 + t, RY0 - t, RY1 + t, -0.1, 0.0, MAT["Floor"], c)
    # walls (left wall has a full-height window opening)
    WY0, WY1 = WIN_Y
    WZ0, WZ1 = 0.06, 2.70
    box("ARCH_Wall_Back", RX0 - t, RX1 + t, RY1, RY1 + t, 0, TRAY + 0.3, MAT["Wall"], c)
    box("ARCH_Wall_Front", RX0 - t, RX1 + t, RY0 - t, RY0, 0, TRAY + 0.3, MAT["Wall"], c)
    box("ARCH_Wall_Right", RX1, RX1 + t, RY0, RY1, 0, TRAY + 0.3, MAT["Wall"], c)
    bm = bmesh.new()
    for y0, y1, z0, z1 in ((RY0, WY0, 0, TRAY + 0.3), (WY1, RY1, 0, TRAY + 0.3), (WY0, WY1, 0, WZ0),
                           (WY0, WY1, WZ1, TRAY + 0.3)):
        bm_box(bm, RX0 - t, RX0, y0, y1, z0, z1)
    mesh_obj("ARCH_Wall_Left_Window", bm, c, MAT["Wall"])
    # window: glazing, slim bronze frame, three vertical mullions
    box("ARCH_Window_Glass", RX0 - 0.12, RX0 - 0.11, WY0, WY1, WZ0, WZ1, MAT["Glass"], c)
    bm = bmesh.new()
    f = 0.05
    for y0, y1, z0, z1 in ((WY0, WY0 + f, WZ0, WZ1), (WY1 - f, WY1, WZ0, WZ1), (WY0, WY1, WZ0, WZ0 + f),
                           (WY0, WY1, WZ1 - f, WZ1)):
        bm_box(bm, RX0 - 0.15, RX0 - 0.08, y0, y1, z0, z1)
    for k in (1, 2):
        y = WY0 + (WY1 - WY0) * k / 3
        bm_box(bm, RX0 - 0.15, RX0 - 0.08, y - 0.025, y + 0.025, WZ0, WZ1)
    mesh_obj("ARCH_Window_Frame", bm, c, MAT["Frame"])
    # false ceiling with tray recess and cove upstand
    bm = bmesh.new()
    x0, x1 = TRAY_X
    y0, y1 = TRAY_Y
    for a in ((RX0, RX1, RY0, y0), (RX0, RX1, y1, RY1), (RX0, x0, y0, y1), (x1, RX1, y0, y1)):
        bm_box(bm, a[0], a[1], a[2], a[3], CEIL, CEIL + 0.12)
    mesh_obj("ARCH_False_Ceiling", bm, c, MAT["Ceiling"])
    box("ARCH_Tray_Ceiling", RX0, RX1, RY0, RY1, TRAY, TRAY + 0.05, MAT["Ceiling"], c)
    # cove: an upstand lip on the edge of the opening hides the LED strip lying on the soffit top behind it
    bm = bmesh.new()
    up = 0.06
    lip = 0.015
    for a in ((x0 - lip, x1 + lip, y0 - lip, y0), (x0 - lip, x1 + lip, y1, y1 + lip),
              (x0 - lip, x0, y0, y1), (x1, x1 + lip, y0, y1)):
        bm_box(bm, a[0], a[1], a[2], a[3], CEIL + 0.12, CEIL + 0.12 + up)
    mesh_obj("ARCH_Cove_Upstand", bm, c, MAT["Ceiling"])
    mesh_obj("ARCH_Skirting", _skirting(), c, MAT["Ceiling"])


def _skirting():
    bm = bmesh.new()
    h, d = 0.08, 0.012
    bm_box(bm, RX0, RX1, RY1 - d, RY1, 0, h)
    bm_box(bm, RX1 - d, RX1, RY0, RY1, 0, h)
    bm_box(bm, RX0, RX0 + d, RY0, WIN_Y[0], 0, h)
    bm_box(bm, RX0, RX0 + d, WIN_Y[1], RY1, 0, h)
    bm_box(bm, RX0, RX1, RY0, RY0 + d, 0, h)
    return bm


def build_feature_wall():
    """Vertical walnut slats over a dark backing across the back wall, framed artwork centred above the sofa."""
    c = "01_ARCHITECTURE"
    box("ARCH_Slat_Backing", SLAT_X[0], SLAT_X[1], RY1 - 0.018, RY1, 0.0, CEIL, MAT["CeramicDark"], c)
    pitch, w, d = 0.065, 0.042, 0.028
    x = SLAT_X[0] + w / 2
    k = 0
    while x + w / 2 <= SLAT_X[1] + 1e-6:
        ob = box("ARCH_Slat_%03d" % k, x - w / 2, x + w / 2, RY1 - 0.018 - d, RY1 - 0.018, 0.0, CEIL,
                 MAT["Walnut"], c, bev=0.002, seg=1)
        k += 1
        x += pitch
    # slats stay separate objects so Object Info > Random varies the walnut tone board to board
    ay = RY1 - 0.05
    box("DEC_Artwork_Frame", ART_X - 0.52, ART_X + 0.52, ay - 0.035, ay, 1.05, 2.09, MAT["ArtFrame"], "02_INTERIOR_ASSETS",
        bev=0.003)
    bm = bmesh.new()
    v = [bm.verts.new(p) for p in ((ART_X - 0.48, ay - 0.0355, 1.09), (ART_X + 0.48, ay - 0.0355, 1.09),
                                   (ART_X + 0.48, ay - 0.0355, 2.05), (ART_X - 0.48, ay - 0.0355, 2.05))]
    f = bm.faces.new(v)
    uv = bm.loops.layers.uv.new()
    for lp, co in zip(f.loops, ((0, 0), (1, 0), (1, 1), (0, 1))):
        lp[uv].uv = co
    mesh_obj("DEC_Artwork_Canvas", bm, "02_INTERIOR_ASSETS", MAT["Art"])
    return k


# ======================================================================== furniture
def sofa():
    c = "02_INTERIOR_ASSETS"
    # main run along the back wall, chaise returning towards camera on the left
    bx0, bx1, by0, by1 = -2.20, 0.95, 1.62, 2.52
    cx0, cx1, cy0 = -2.20, -1.30, 0.45
    box("SOFA_Base_Main", bx0 + 0.02, bx1 - 0.02, by0 + 0.03, by1 - 0.02, 0.0, 0.08, MAT["WalnutFurn"], c)
    box("SOFA_Plinth_Main", bx0, bx1, by0, by1, 0.08, 0.30, MAT["Sofa"], c, bev=0.03, seg=3)
    box("SOFA_Base_Chaise", cx0 + 0.02, cx1 - 0.02, cy0 + 0.02, by0, 0.0, 0.08, MAT["WalnutFurn"], c)
    box("SOFA_Plinth_Chaise", cx0, cx1, cy0, by0 + 0.05, 0.08, 0.30, MAT["Sofa"], c, bev=0.03, seg=3)
    box("SOFA_Back_Main", bx0, bx1, by1 - 0.22, by1, 0.30, 0.80, MAT["Sofa"], c, bev=0.05, seg=4)
    box("SOFA_Back_Chaise", cx0, cx0 + 0.22, cy0, by1 - 0.2, 0.30, 0.66, MAT["Sofa"], c, bev=0.05, seg=4)
    box("SOFA_Arm_Right", bx1 - 0.2, bx1, by0, by1 - 0.2, 0.30, 0.60, MAT["Sofa"], c, bev=0.05, seg=4)
    # seat cushions
    n = 3
    sw = (bx1 - 0.2 - (cx1)) / n
    for i in range(n):
        x0 = cx1 + i * sw
        sub(box("SOFA_Seat_%d" % i, x0 + 0.005, x0 + sw - 0.005, by0 + 0.02, by1 - 0.22, 0.30, 0.43, MAT["Sofa"], c,
                bev=0.05, seg=4))
    sub(box("SOFA_Seat_Chaise", cx0 + 0.22, cx1, cy0 + 0.02, by1 - 0.22, 0.30, 0.43, MAT["Sofa"], c, bev=0.05,
            seg=4))
    # back cushions and scatter cushions (rust red / ivory)
    for i in range(n):
        x0 = cx1 + i * sw
        sub(box("SOFA_BackCushion_%d" % i, x0 + 0.01, x0 + sw - 0.01, by1 - 0.40, by1 - 0.20, 0.43, 0.86,
                MAT["Sofa"], c, bev=0.07, seg=4))
    sub(box("SOFA_BackCushion_Corner", cx0 + 0.20, cx1 - 0.02, by1 - 0.40, by1 - 0.20, 0.43, 0.86, MAT["Sofa"], c,
            bev=0.07, seg=4))
    for name, x, y, mat, rz in (("CUSH_Rust_01", -1.10, 1.98, "Rust", 0.12), ("CUSH_Ivory_01", -0.66, 2.0, "Ivory", -0.06),
                                ("CUSH_Rust_02", 0.22, 1.98, "Rust", -0.1), ("CUSH_Ivory_02", 0.56, 1.95, "Ivory", 0.15),
                                ("CUSH_Rust_03", -1.92, 1.05, "Rust", 1.45)):
        ob = pillow(name, MAT[mat], c)
        ob.location = (x, y, 0.67)
        ob.rotation_euler = (math.radians(-14) if "03" not in name else 0, math.radians(14) if "03" in name else 0, rz)
    # throw blanket over the chaise edge
    t = box("SOFA_Throw", cx0 + 0.3, cx1 + 0.03, cy0 + 0.25, cy0 + 0.75, 0.43, 0.445, MAT["Rug"], c, bev=0.006)
    return (bx0, bx1, by0, by1, cx0, cx1, cy0)


def sub(ob, lv=1):
    md = ob.modifiers.new("Subsurf", "SUBSURF")
    md.levels = lv
    md.render_levels = lv
    for p in ob.data.polygons:
        p.use_smooth = True
    return ob


def pillow(name, mat, c, w=0.46, h=0.46, d=0.15):
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    for v in bm.verts:
        v.co.x *= w
        v.co.z *= h
        v.co.y *= d
    ob = mesh_obj(name, bm, c, mat, True)
    md = ob.modifiers.new("Subsurf", "SUBSURF")
    md.levels = md.render_levels = 3
    # pinch the corners: a cast towards sphere gives the classic plump square cushion
    cs = ob.modifiers.new("Cast", "CAST")
    cs.factor = 0.35
    return ob


def coffee_table():
    c = "02_INTERIOR_ASSETS"
    cx, cy = -0.45, 0.80
    box("TABLE_Coffee_Top", cx - 0.65, cx + 0.65, cy - 0.36, cy + 0.36, 0.30, 0.36, MAT["WalnutFurn"], c, bev=0.008)
    box("TABLE_Coffee_Plinth", cx - 0.55, cx + 0.55, cy - 0.27, cy + 0.27, 0.0, 0.30, MAT["WalnutFurn"], c,
        bev=0.004)
    bm = bmesh.new()
    bm_box(bm, -1.25, 1.00, -0.45, 1.58, 0.0, 0.012)
    mesh_obj("RUG_Living", bm, c, MAT["Rug"])
    # books
    for i, (w, d, h, m, rz) in enumerate(((0.30, 0.22, 0.035, "Book1", 0.1), (0.27, 0.20, 0.03, "Book2", -0.05))):
        z = 0.36 + sum([0.035, 0.03][:i])
        bo = box("DEC_Book_%d" % i, -w / 2, w / 2, -d / 2, d / 2, 0, h, MAT[m], c, bev=0.002)
        bo.location = (cx - 0.38, cy + 0.04, z)
        bo.rotation_euler.z = rz
    # brass urli with marigolds
    urli = lathe("DEC_Urli_Brass", [(0.0, 0.0), (0.09, 0.0), (0.16, 0.035), (0.20, 0.07), (0.195, 0.075),
                                    (0.15, 0.04), (0.0, 0.035)], MAT["Brass"], c, loc=(cx + 0.18, cy + 0.02, 0.36))
    for k in range(17):
        a = k * 2.399
        r = 0.035 + 0.11 * math.sqrt((k + 0.5) / 17)
        sphere("DEC_Marigold_%02d" % k, 0.032, (cx + 0.18 + r * math.cos(a), cy + 0.02 + r * math.sin(a),
                                                0.36 + 0.07 + 0.012 * math.cos(k)), MAT["Marigold"], c,
               (1, 1, 0.75), (16, 8))
    diya("DIYA_Table_01", (cx + 0.48, cy - 0.16, 0.36), "table")
    diya("DIYA_Table_02", (cx + 0.40, cy - 0.24, 0.36), "table")
    return (cx, cy)


DIYAS = {}


def diya(name, loc, group):
    c = "02_INTERIOR_ASSETS"
    lathe(name + "_Bowl", [(0.0, 0.0), (0.028, 0.0), (0.042, 0.012), (0.048, 0.026), (0.044, 0.028),
                           (0.034, 0.016), (0.0, 0.014)], MAT["Clay"], c, loc=loc, n=32)
    cyl(name + "_Oil", 0.033, loc[2] + 0.019, loc[2] + 0.0195, MAT["Oil"], c, loc=loc[:2], n=24)
    fl = lathe(name + "_Flame", [(0.0, 0.0), (0.0045, 0.004), (0.006, 0.010), (0.0045, 0.018), (0.0, 0.03)],
               MAT["Flame"], "05_LIGHTING_FIXTURES", loc=(loc[0] + 0.03, loc[1], loc[2] + 0.024), n=16)
    fl.visible_shadow = False
    lt = light("LGT_" + name, "POINT", (loc[0] + 0.03, loc[1], loc[2] + 0.04), 0.35, "06_LIGHT_RIG", k=1850,
               size=0.006)
    DIYAS.setdefault(group, []).append(lt)


def side_table_lamp():
    c = "02_INTERIOR_ASSETS"
    x, y = 1.24, 2.12
    cyl("TABLE_Side_Top", 0.21, 0.52, 0.55, MAT["WalnutFurn"], c, loc=(x, y), n=48, bev=0.004)
    cyl("TABLE_Side_Stem", 0.035, 0.02, 0.52, MAT["Brass"], c, loc=(x, y), n=24)
    cyl("TABLE_Side_Foot", 0.18, 0.0, 0.02, MAT["Brass"], c, loc=(x, y), n=48)
    lathe("LAMP_Table_Base", [(0.0, 0.0), (0.07, 0.0), (0.11, 0.08), (0.10, 0.20), (0.04, 0.27), (0.015, 0.29),
                              (0.0, 0.29)], MAT["Ceramic"], c, loc=(x, y, 0.55))
    cyl("LAMP_Table_Stem", 0.008, 0.84, 0.95, MAT["Brass"], c, loc=(x, y), n=12)
    sh = lathe("LAMP_Table_Shade", [(0.13, 0.0), (0.12, 0.0), (0.10, 0.22), (0.11, 0.22), (0.13, 0.0)],
               MAT["Shade"], "05_LIGHTING_FIXTURES", loc=(x, y, 0.88))
    lt = light("LGT_Table_Lamp", "POINT", (x, y, 1.0), 11.0, "06_LIGHT_RIG", k=2700, size=0.03)
    plant("PLANT_Window_Front", (-1.70, -0.70, 0.0), 0.24, 1.75)
    plant("PLANT_Right", (1.95, 1.45, 0.0), 0.2, 1.15)
    return lt


def plant(name, loc, r, h):
    """Large-leaf plant (fiddle-leaf style): tapered pot, stems and ~40 curved leaves."""
    c = "02_INTERIOR_ASSETS"
    lathe(name + "_Pot", [(0.0, 0.0), (r * 0.75, 0.0), (r, r * 1.6), (r * 0.95, r * 1.6), (0.0, r * 1.5)],
          MAT["Pot"], c, loc=loc)
    base = Vector(loc) + Vector((0, 0, r * 1.5))
    bm = bmesh.new()
    rnd = 0.37
    for k in range(int(28 + h * 8)):
        rnd = (rnd * 9301 + 49297) % 233280 / 233280.0
        a = k * 2.399 + rnd
        t = 0.25 + 0.75 * ((k * 0.618) % 1.0)
        rr = r * (0.3 + 0.7 * t * (0.6 + 0.4 * rnd))
        p = base + Vector((math.cos(a) * rr, math.sin(a) * rr, h * t))
        L, W = 0.20 + 0.06 * rnd, 0.14 + 0.04 * rnd
        # curved leaf: 5x3 grid bent along its length, tilted outward and down
        rows = []
        for i in range(6):
            u = i / 5
            wid = W * math.sin(math.pi * min(0.98, 0.15 + 0.85 * u)) * (1.0 - 0.3 * u)
            row = []
            for j in (-1, 0, 1):
                lp = Vector((u * L, j * wid / 2, -0.25 * (u * L) ** 2 / L * 2 + 0.008 * (1 - abs(j))))
                rot = Euler((0, math.radians(-25 - 30 * rnd), a), "XYZ")
                lp.rotate(rot)
                row.append(bm.verts.new(p + lp))
            rows.append(row)
        for i in range(5):
            for j in range(2):
                bm.faces.new((rows[i][j], rows[i + 1][j], rows[i + 1][j + 1], rows[i][j + 1]))
        # petiole from the trunk to the leaf base
        s0 = base + Vector((0.0, 0.0, max(0.05, h * t - 0.12)))
        sv = [bm.verts.new(s0 + Vector((0, 0, dz))) for dz in (0.004, -0.004)]
        sv2 = [bm.verts.new(p + Vector((0, 0, dz))) for dz in (0.004, -0.004)]
        bm.faces.new((sv[0], sv[1], sv2[1], sv2[0]))
    ob = mesh_obj(name + "_Foliage", bm, c, MAT["Foliage"], True)
    cyl(name + "_Trunk", 0.014, base.z - 0.02, base.z + h * 0.95, MAT["Pot"], c, loc=loc[:2], n=10)
    sol = ob.modifiers.new("Solidify", "SOLIDIFY")
    sol.thickness = 0.002
    # soil
    cyl(name + "_Soil", r * 0.93, loc[2] + r * 1.45, loc[2] + r * 1.47, MAT["CeramicDark"], c, loc=loc[:2])


def curtains():
    c = "02_INTERIOR_ASSETS"
    x = RX0 + 0.16
    # heavy linen side panels and a sheer across the glass, gathered with sine pleats
    for name, y0, y1, mat, amp, xoff in (("CURTAIN_Panel_Front", -0.75, -0.12, "Curtain", 0.035, 0.0),
                                         ("CURTAIN_Panel_Back", 1.98, 2.55, "Curtain", 0.035, 0.0),
                                         ("CURTAIN_Sheer", -0.15, 2.0, "Sheer", 0.025, 0.0)):
        bm = bmesh.new()
        ny = int((y1 - y0) / 0.02)
        nz = 14
        grid = []
        for j in range(nz + 1):
            z = 0.015 + (CEIL - 0.03) * j / nz
            row = []
            for i in range(ny + 1):
                y = y0 + (y1 - y0) * i / ny
                xx = x + xoff + amp * math.sin(i / ny * (y1 - y0) / 0.09 * 2 * math.pi) * (0.85 + 0.15 * j / nz)
                row.append(bm.verts.new((xx, y, z)))
            grid.append(row)
        for j in range(nz):
            for i in range(ny):
                bm.faces.new((grid[j][i], grid[j][i + 1], grid[j + 1][i + 1], grid[j + 1][i]))
        ob = mesh_obj(name, bm, c, MAT[mat], True)
        if mat == "Curtain":
            s = ob.modifiers.new("Solidify", "SOLIDIFY")
            s.thickness = 0.004
    cyl("CURTAIN_Track", 0.012, 0, 1, MAT["Frame"], c, n=12)
    tr = bpy.data.objects["CURTAIN_Track"]
    tr.scale = (1, 1, 3.33)
    tr.rotation_euler = (math.radians(-90), 0, 0)
    tr.location = (x + 0.03, -0.8, CEIL - 0.02)


def console_shelves():
    """Back wall, right of the slats: low walnut console with a diya row, three floating shelves with LED."""
    c = "02_INTERIOR_ASSETS"
    x0, x1, yb = 1.50, 2.47, RY1
    box("CONSOLE_Body", x0, x1, yb - 0.44, yb - 0.01, 0.10, 0.55, MAT["WalnutFurn"], c, bev=0.006)
    box("CONSOLE_Plinth", x0 + 0.04, x1 - 0.04, yb - 0.40, yb - 0.05, 0.0, 0.10, MAT["CeramicDark"], c)
    xm = (x0 + x1) / 2
    box("CONSOLE_Door_Groove", xm - 0.005, xm + 0.005, yb - 0.445, yb - 0.435, 0.13, 0.52, MAT["CeramicDark"], c)
    for k in range(4):
        diya("DIYA_Console_%02d" % k, (x0 + 0.30 + 0.16 * k, yb - 0.24, 0.55), "console")
    lathe("DEC_Vase_Tall", [(0.0, 0.0), (0.06, 0.0), (0.09, 0.12), (0.07, 0.30), (0.035, 0.40), (0.04, 0.44),
                            (0.0, 0.43)], MAT["Ceramic"], c, loc=(x0 + 0.12, yb - 0.24, 0.55))
    lathe("DEC_Vase_Round", [(0.0, 0.0), (0.05, 0.0), (0.10, 0.08), (0.08, 0.17), (0.03, 0.2), (0.0, 0.19)],
          MAT["CeramicDark"], c, loc=(x1 - 0.13, yb - 0.24, 0.55))
    shelves = []
    for k, z in enumerate(SHELF_Z):
        box("SHELF_%d" % k, x0, x1 - 0.002, yb - 0.28, yb - 0.002, z, z + 0.04, MAT["WalnutFurn"], c, bev=0.003)
        shelves.append(z)
    yc = yb - 0.14
    lathe("DEC_Shelf_Vase_A", [(0.0, 0.0), (0.04, 0.0), (0.06, 0.08), (0.03, 0.2), (0.0, 0.2)], MAT["Ceramic"],
          c, loc=(x0 + 0.2, yc, SHELF_Z[0] + 0.04))
    lathe("DEC_Shelf_Bowl", [(0.0, 0.0), (0.05, 0.0), (0.11, 0.06), (0.10, 0.065), (0.0, 0.01)],
          MAT["CeramicDark"], c, loc=(x1 - 0.25, yc, SHELF_Z[0] + 0.04))
    for i in range(7):
        bo = box("DEC_Shelf_Book_%d" % i, -0.012, 0.012, -0.1, 0.1, 0, 0.21 + 0.02 * (i % 3),
                 MAT["Book1" if i % 2 else "Book2"], c, bev=0.001)
        bo.location = (xm + 0.05 + 0.027 * i, yc, SHELF_Z[1] + 0.04)
    lathe("DEC_Shelf_Lantern", [(0.0, 0.0), (0.05, 0.0), (0.05, 0.14), (0.02, 0.18), (0.0, 0.19)], MAT["Brass"],
          c, loc=(x0 + 0.2, yc, SHELF_Z[1] + 0.04))
    lathe("DEC_Shelf_Vase_B", [(0.0, 0.0), (0.05, 0.0), (0.08, 0.1), (0.04, 0.16), (0.0, 0.16)],
          MAT["Ceramic"], c, loc=(x1 - 0.2, yc, SHELF_Z[2] + 0.04))
    for k in range(3):
        diya("DIYA_Shelf_%02d" % k, (x0 + 0.15 + 0.2 * k, yc, SHELF_Z[2] + 0.04), "shelf")
    return shelves


# ======================================================================== lighting fixtures + rig
GROUPS = {}          # cue channel -> list of (id, data_path, full_value)


def add_cue(group, idblock, path, value):
    GROUPS.setdefault(group, []).append((idblock, path, value))


def downlight(name, x, y, group, power, k=3000, aim=None):
    c = "05_LIGHTING_FIXTURES"
    z = CEIL
    cyl(name + "_Trim", 0.05, z - 0.004, z, MAT["Trim"], c, loc=(x, y), n=32)
    cyl(name + "_Reflector", 0.036, z - 0.0045, z - 0.003, MAT["Reflector"], c, loc=(x, y), n=32)
    em = mat_emit("MAT_" + name + "_Lens", k, 0.0)
    cyl(name + "_Lens", 0.022, z - 0.005, z - 0.0042, em, c, loc=(x, y), n=24)
    rot = (0, 0, 0) if aim is None else aim
    lt = light("LGT_" + name, "SPOT", (x, y, z - 0.01), 0.0, "06_LIGHT_RIG", k=k, size=0.02, spot=70, rot=rot)
    lt.data.spot_blend = 0.85
    add_cue(group, lt.data, "energy", power)
    add_cue(group, em.node_tree.nodes["Emission"].inputs["Strength"], "default_value", 30.0)
    return lt


def build_lights():
    c = "06_LIGHT_RIG"
    # back-wall washers (aimed slightly at the slats), perimeter downlights
    for i, x in enumerate((-1.85, -0.62, 0.60, 1.98)):
        downlight("DL_Wash_%d" % i, x, RY1 - 0.24, "wash", 22.0, aim=(math.radians(14), 0, 0))
    for i, (x, y) in enumerate(((-2.15, -0.40), (-2.15, 1.30), (1.90, -0.40), (1.90, 1.30), (-1.0, -2.3),
                                (0.5, -2.3))):
        downlight("DL_Perim_%d" % i, x, y, "perim", 16.0)
    # cove: one area light per side, facing up at the tray, plus a low-power emissive strip for its look
    x0, x1 = TRAY_X
    y0, y1 = TRAY_Y
    o = 0.07
    em = mat_emit("MAT_Cove_LED_Strip", 3000, 0.0)
    bm = bmesh.new()
    zc = CEIL + 0.125
    for a in ((x0 - o - 0.01, x1 + o + 0.01, y0 - o - 0.01, y0 - o), (x0 - o - 0.01, x1 + o + 0.01, y1 + o,
                                                                       y1 + o + 0.01),
              (x0 - o - 0.01, x0 - o, y0 - o, y1 + o), (x1 + o, x1 + o + 0.01, y0 - o, y1 + o)):
        bm_box(bm, a[0], a[1], a[2], a[3], zc, zc + 0.004)
    strip = mesh_obj("FIX_Cove_LED_Strip", bm, "05_LIGHTING_FIXTURES", em)
    strip.visible_shadow = False
    add_cue("cove", em.node_tree.nodes["Emission"].inputs["Strength"], "default_value", 6.0)
    zl = zc + 0.01
    for name, loc, sx, sy, rot in (
            ("LGT_Cove_Front", ((x0 + x1) / 2, y0 - o - 0.02, zl), x1 - x0 + 0.2, 0.02, (math.radians(160), 0, 0)),
            ("LGT_Cove_Back", ((x0 + x1) / 2, y1 + o + 0.02, zl), x1 - x0 + 0.2, 0.02, (math.radians(-160), 0, 0)),
            ("LGT_Cove_Left", (x0 - o - 0.02, (y0 + y1) / 2, zl), 0.02, y1 - y0 + 0.2, (0, math.radians(-160), 0)),
            ("LGT_Cove_Right", (x1 + o + 0.02, (y0 + y1) / 2, zl), 0.02, y1 - y0 + 0.2, (0, math.radians(160), 0))):
        lt = light(name, "AREA", loc, 0.0, c, k=3000, size=sx, size_y=sy, rot=rot)
        add_cue("cove", lt.data, "energy", 40.0 * max(sx, sy))
    # under-shelf LED (right wall)
    em = mat_emit("MAT_Shelf_LED", 2850, 0.0)
    for k, z in enumerate(SHELF_Z):
        lt = light("LGT_Shelf_%d" % k, "AREA", (1.985, RY1 - 0.2, z - 0.004), 0.0, c, k=2850, size=0.9,
                   size_y=0.03)
        add_cue("shelf", lt.data, "energy", 14.0)
        s = box("FIX_Shelf_LED_%d" % k, 1.54, 2.43, RY1 - 0.215, RY1 - 0.195, z - 0.003, z, em,
                "05_LIGHTING_FIXTURES")
        s.visible_shadow = False
    add_cue("shelf", em.node_tree.nodes["Emission"].inputs["Strength"], "default_value", 5.0)
    string_lights()
    # constant layers: table lamp (always on), diyas (always lit), dusk window fill
    wy = (WIN_Y[0] + WIN_Y[1]) / 2
    lt = light("LGT_Window_Dusk_Fill", "AREA", (RX0 - 0.6, wy, 1.4), 9.0, c, k=9000, size=2.8, size_y=2.8,
               rot=(0, math.radians(-90), 0))
    lt.data.color = (0.45, 0.55, 0.85)
    lt = light("LGT_Window_Portal", "AREA", (RX0 - 0.13, wy, 1.38), 0.0, c, size=2.64, size_y=WIN_Y[1] - WIN_Y[0],
               rot=(0, math.radians(-90), 0))
    lt.data.cycles.is_portal = True
    # subtle neutral fill from behind camera (bounce from the unseen front wall)
    lt = light("LGT_Fill_Neutral", "AREA", (0.0, RY0 + 0.15, 1.6), 6.0, c, k=4000, size=3.0, size_y=1.4,
               rot=(math.radians(90), 0, 0))
    lt.visible_camera = False


def string_lights():
    """Warm micro-bulb curtain lights hung in front of the sheer: 14 strands of 18 bulbs."""
    c = "05_LIGHTING_FIXTURES"
    em = mat_emit("MAT_String_Bulb", 2500, 0.0)
    bm_b = bmesh.new()
    bm_w = bmesh.new()
    x = RX0 + 0.23
    ys = [0.0 + 1.9 * i / 13 for i in range(14)]
    for i, y in enumerate(ys):
        top = CEIL - 0.05
        bot = 0.55 + 0.35 * abs(math.sin(i * 1.7))
        n = 18
        prev = None
        for j in range(n + 1):
            z = top - (top - bot) * j / n
            v = bm_w.verts.new((x, y, z))
            if prev is not None:
                bm_w.edges.new((prev, v))
            prev = v
            if j > 0:
                bmesh.ops.create_icosphere(bm_b, subdivisions=1, radius=0.0045,
                                           matrix=Matrix.Translation((x, y + 0.004, z)))
    bulbs = mesh_obj("FIX_String_Lights_Bulbs", bm_b, c, em)
    bulbs.visible_shadow = False
    wire = mesh_obj("FIX_String_Lights_Wire", bm_w, c)
    sk = wire.modifiers.new("Skin", "SKIN")
    for v in wire.data.skin_vertices[0].data:
        v.radius = (0.0009, 0.0009)
    wire.data.materials.append(MAT["Wire"])
    add_cue("string", em.node_tree.nodes["Emission"].inputs["Strength"], "default_value", 7.0)
    # a few real lights so the strands actually light the curtain and floor
    for i, y in enumerate(ys[::3]):
        lt = light("LGT_String_%d" % i, "POINT", (x + 0.02, y, 1.6), 0.0, "06_LIGHT_RIG", k=2500, size=0.25)
        add_cue("string", lt.data, "energy", 4.0)


# ======================================================================== Polycab Aerorush (provisional geometry)
def build_fan():
    """Aerorush 1200 mm, 3 aluminium blades, Classic Black, decorative chrome motor ring.
    Proportions read from the official product photos (polycab.com, p-69875 and colour variants); exact CAD
    was not supplied. The canopy, downrod and top cover are stationary; the rotor (motor shell + ring + blade
    holders + blades) is parented to FAN_Rotor, whose Z rotation is driven by CTRL_Fan."""
    c = "03_POLYCAB_AERORUSH"
    fx, fy = FAN_XY
    root = empty("FAN_Mount", (fx, fy, TRAY), c, "ARROWS", 0.15)
    parts = []
    parts.append(lathe("FAN_Canopy", [(0.0, -0.075), (0.012, -0.075), (0.03, -0.068), (0.05, -0.048),
                                      (0.06, -0.02), (0.062, 0.0), (0.0, 0.0)], MAT["FanBody"], c))
    parts.append(cyl("FAN_Downrod", 0.011, -0.165, -0.07, MAT["FanBody"], c, n=24))
    parts.append(lathe("FAN_Top_Cover", [(0.0, -0.17), (0.022, -0.17), (0.03, -0.185), (0.075, -0.215),
                                         (0.098, -0.232), (0.1, -0.238), (0.0, -0.238)], MAT["FanBody"], c))
    for p in parts:
        p.parent = root
    rotor = empty("FAN_Rotor", (fx, fy, TRAY - 0.238), c, "CIRCLE", 0.12)
    rotor.parent = root
    rotor.location = (0, 0, -0.238)
    rp = []
    rp.append(lathe("FAN_Rotor_Shell", [(0.0, 0.0), (0.1, 0.0), (0.103, -0.02), (0.104, -0.05), (0.102, -0.062),
                                        (0.0, -0.062)], MAT["FanBody"], c))
    rp.append(lathe("FAN_Decor_Ring", [(0.098, -0.060), (0.106, -0.060), (0.107, -0.067), (0.104, -0.075),
                                       (0.096, -0.075)], MAT["FanRing"], c, n=64))
    rp.append(lathe("FAN_Bottom_Cap", [(0.0, -0.092), (0.04, -0.09), (0.075, -0.083), (0.097, -0.074),
                                       (0.097, -0.06), (0.0, -0.06)], MAT["FanBody"], c, n=64))
    # three blade holders + blades
    bm_b = bmesh.new()
    bm_h = bmesh.new()
    bm_r = bmesh.new()
    pitch = math.radians(11)
    for k in range(3):
        a = 2 * math.pi * k / 3
        R = Matrix.Rotation(a, 4, "Z")
        # holder: flat arm from the shell to the blade root
        hb = bmesh.new()
        bm_box(hb, 0.06, 0.20, -0.022, 0.022, -0.072, -0.064)
        bmesh.ops.transform(hb, matrix=R, verts=hb.verts)
        _merge(bm_h, hb)
        # blade: 0.155 .. 0.60 m radius, slight widening, rounded tip, pitched about its long axis
        bb = _blade_bmesh(0.155, 0.60, pitch)
        bmesh.ops.transform(bb, matrix=Matrix.Translation((0, 0, -0.064)), verts=bb.verts)
        bmesh.ops.transform(bb, matrix=R, verts=bb.verts)
        _merge(bm_b, bb)
        for rx, ry in ((0.175, -0.022), (0.175, 0.022), (0.195, 0.0)):
            rb = bmesh.new()
            bmesh.ops.create_uvsphere(rb, u_segments=10, v_segments=5, radius=0.0045)
            bmesh.ops.scale(rb, vec=(1, 1, 0.5), verts=rb.verts)
            bmesh.ops.transform(rb, matrix=Matrix.Translation((rx, ry, -0.0582)), verts=rb.verts)
            bmesh.ops.transform(rb, matrix=R, verts=rb.verts)
            _merge(bm_r, rb)
    blades = mesh_obj("FAN_Blades_x3", bm_b, c, MAT["FanBlade"], True)
    bevel(blades, 0.0015, 2)
    blades.modifiers["Bevel"].limit_method = "NONE"
    holders = mesh_obj("FAN_Blade_Holders_x3", bm_h, c, MAT["FanBody"])
    bevel(holders, 0.003, 2)
    rp += [blades, holders, mesh_obj("FAN_Rivets", bm_r, c, MAT["Rivet"], True)]
    for p in rp:
        p.parent = rotor
    return root, rotor, blades


def _merge(dst, src):
    me = bpy.data.meshes.new("_tmp")
    src.to_mesh(me)
    src.free()
    dst.from_mesh(me)
    bpy.data.meshes.remove(me)


def _blade_bmesh(r0, r1, pitch, nu=24, nv=6, th=0.004):
    """Outline: root width 0.090 widening to 0.110 at 85 % span, rounded tip. Gentle chordwise camber."""
    bm = bmesh.new()
    top, bot = [], []
    for i in range(nu + 1):
        u = i / nu
        x = r0 + (r1 - r0) * u
        w = 0.090 + 0.020 * min(1.0, u / 0.85)
        tip = max(0.0, (u - 0.93) / 0.07)
        w *= math.sqrt(max(0.0, 1 - tip * tip)) if tip > 0 else 1.0
        w = max(w, 0.012)
        rt, rb = [], []
        for j in range(nv + 1):
            v = -0.5 + j / nv
            y = v * w
            camber = 0.006 * (1 - (2 * v) ** 2)
            z = camber
            # pitch about the blade's long axis: leading edge (-Y, direction of travel) up
            yy = y * math.cos(pitch) + z * math.sin(pitch)
            zz = -y * math.sin(pitch) + z * math.cos(pitch)
            rt.append(bm.verts.new((x, yy, zz + th / 2)))
            rb.append(bm.verts.new((x, yy, zz - th / 2)))
        top.append(rt)
        bot.append(rb)
    for i in range(nu):
        for j in range(nv):
            bm.faces.new((top[i][j], top[i][j + 1], top[i + 1][j + 1], top[i + 1][j]))
            bm.faces.new((bot[i][j], bot[i + 1][j], bot[i + 1][j + 1], bot[i][j + 1]))
    for i in range(nu):
        for j in (0, nv):
            a, b_ = (top[i][j], top[i + 1][j]), (bot[i][j], bot[i + 1][j])
            f = (a[0], a[1], b_[1], b_[0]) if j == 0 else (a[1], a[0], b_[0], b_[1])
            bm.faces.new(f)
    for i in (0, nu):
        for j in range(nv):
            f = (top[i][j + 1], top[i][j], bot[i][j], bot[i][j + 1]) if i == 0 else \
                (top[i][j], top[i][j + 1], bot[i][j + 1], bot[i][j])
            bm.faces.new(f)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return bm


# ======================================================================== remote + hand
def build_remote():
    """Slim satin-black RF remote, 135 x 42 x 17 mm, power key near the top. PROVISIONAL: no Aerorush
    remote reference was supplied, so the key layout is a minimal neutral placeholder with no labels
    (power symbol only, as a moulded mark), to be replaced from the approved reference."""
    c = "04_REMOTE_CONTROL"
    root = empty("REMOTE_Root", (0, 0, 0), c, "ARROWS", 0.05)
    bm = bmesh.new()
    bm_box(bm, -0.021, 0.021, -0.0675, 0.0675, -0.0085, 0.0085)
    body = mesh_obj("REMOTE_Body", bm, c, MAT["Remote"])
    bevel(body, 0.006, 4)
    body.modifiers["Bevel"].limit_method = "NONE"
    for p in body.data.polygons:
        p.use_smooth = True
    parts = [body]
    pw = cyl("REMOTE_Key_Power", 0.0065, 0.0080, 0.0098, MAT["Button"], c, loc=(0, 0.042), n=32, bev=0.0008)
    parts.append(pw)
    # moulded power glyph: open ring + bar
    bm = bmesh.new()
    n = 20
    for k in range(n):
        a0 = math.radians(60 + 240 * k / n) + math.pi / 2 - math.radians(60) + math.radians(30)
        a1 = math.radians(60 + 240 * (k + 1) / n) + math.pi / 2 - math.radians(60) + math.radians(30)
        r0, r1 = 0.0026, 0.0033
        vs = [bm.verts.new((r * math.cos(a), 0.042 + r * math.sin(a), 0.00985)) for r, a in
              ((r0, a0), (r1, a0), (r1, a1), (r0, a1))]
        bm.faces.new(vs)
    bm_box(bm, -0.00035, 0.00035, 0.042 + 0.0006, 0.042 + 0.0038, 0.00985, 0.0099)
    parts.append(mesh_obj("REMOTE_Glyph_Power", bm, c, MAT["Icon"]))
    for k, (x, y) in enumerate(((0, 0.014), (0, -0.012), (-0.011, 0.001), (0.011, 0.001))):
        parts.append(cyl("REMOTE_Key_%d" % k, 0.0045, 0.0080, 0.0094, MAT["Button"], c, loc=(x, y), n=24,
                         bev=0.0006))
    parts.append(cyl("REMOTE_Status_LED", 0.0012, 0.0084, 0.0087, MAT["Icon"], c, loc=(0, 0.058), n=12))
    for p in parts:
        p.parent = root
    return root


def build_hand(remote_root):
    """Right hand gripping the remote from its right side: palm on the +X edge, fingers wrapping under to the -X
    edge, thumb over the face to the power key. Skin modifier over a joint skeleton + subdivision; the press is a
    shape key ("Thumb_Press") on the skeleton. Coordinates are in the remote's local frame (metres)."""
    c = "04_REMOTE_CONTROL"
    V = []
    E = []
    R = []

    def chain(pts, radii, start=None):
        idx = []
        for i, (p, r) in enumerate(zip(pts, radii)):
            V.append(p)
            R.append(r)
            idx.append(len(V) - 1)
        if start is not None:
            E.append((start, idx[0]))
        for a, b in zip(idx, idx[1:]):
            E.append((a, b))
        return idx

    oy = 0.022                                   # whole grip sits slightly forward of the remote's centre
    wrist = chain([(0.052, -0.135 + oy, -0.036), (0.046, -0.100 + oy, -0.028)], [(0.024, 0.019), (0.022, 0.017)])
    # metacarpals fan from the wrist into the palm along the remote's +X side, then each finger curls under the
    # body and up its -X edge (finger centres sit one radius off the shell)
    fingers = []
    for k, (y, L) in enumerate(((0.010, 1.0), (-0.011, 1.05), (-0.031, 1.0), (-0.049, 0.86))):
        y += oy
        mid = (0.044, -0.058 + oy + y * 0.4, -0.028)
        mcp = (0.033, y, -0.021)
        base = chain([mid, mcp], [(0.015, 0.012), (0.0098, 0.0092)], wrist[1])
        f = chain([(0.006, y + 0.001, -0.0178), (-0.017, y + 0.002, -0.0172), (-0.0295, y + 0.002, -0.004),
                   (-0.0275, y + 0.002, 0.004 + 0.003 * (L - 0.86))],
                  [(0.0088 * L, 0.0084 * L), (0.0080, 0.0076), (0.0072, 0.0068), (0.0060, 0.0057)], base[1])
        fingers.append(f)
    thumb = chain([(0.047, -0.068 + oy, -0.015), (0.042, -0.036 + oy, 0.011), (0.025, -0.004 + oy, 0.0185),
                   (0.010, 0.016 + oy, 0.0182), (0.003, 0.021 + oy, 0.0172)],
                  [(0.019, 0.015), (0.0112, 0.0100), (0.0094, 0.0088), (0.0085, 0.0080), (0.0068, 0.0064)],
                  wrist[1])
    me = bpy.data.meshes.new("HAND_Right")
    me.from_pydata(V, E, [])
    ob = bpy.data.objects.new("HAND_Right", me)
    link(ob, c)
    sk = ob.modifiers.new("Skin", "SKIN")
    sk.use_smooth_shade = True
    sk.branch_smoothing = 0.6
    for i, r in enumerate(R):
        sv = me.skin_vertices[0].data[i]
        sv.radius = r
        sv.use_root = (i == 0)
    sd = ob.modifiers.new("Subsurf", "SUBSURF")
    sd.levels = sd.render_levels = 2
    me.materials.append(MAT["Skin"])
    # shape keys: rest has the thumb hovering 9 mm above the key; Thumb_Press puts the pad on the key
    ob.shape_key_add(name="Basis")
    hover = ob.shape_key_add(name="Thumb_Hover")
    for i, idx in enumerate(thumb[2:]):
        hover.data[idx].co.z += (0.003, 0.007, 0.009)[i]
    hover.value = 1.0
    press = ob.shape_key_add(name="Thumb_Press")
    for idx in thumb:
        press.data[idx].co = me.vertices[idx].co
    for idx, dz in zip(thumb[2:], (0.002, 0.006, 0.0085)):
        press.data[idx].co.z -= dz                 # pad onto the key (subdivision pulls the skin inwards)
    press.value = 0.0
    ob.parent = remote_root
    # shirt cuff over the wrist
    cuff = cyl("HAND_Sleeve_Cuff", 0.036, 0.0, 0.16, MAT["Sleeve"], c, n=32, bev=0.004)
    cuff.parent = remote_root
    cuff.location = (0.058, -0.165, -0.046)
    cuff.rotation_euler = (math.radians(100), math.radians(-6), 0)
    for p in cuff.data.polygons:
        p.use_smooth = True
    return ob, hover, press


# ======================================================================== camera rig + animation
CAM_KEYS = [  # frame, camera location, look target   (shot 1 glide in, shot 2 push + tilt up, shot 3 pull back + rise)
    (1, (0.30, -2.55, 1.02), (-0.25, 1.40, 1.95)),
    (36, (0.12, -1.30, 1.18), (-0.22, 1.00, 2.20)),
    (54, (0.00, -0.45, 1.38), (-0.25, 0.65, 2.62)),
    (66, (0.02, -0.52, 1.40), (-0.25, 0.66, 2.58)),
    (112, (0.05, -2.74, 1.58), (-0.25, 1.05, 1.95)),
    (120, (0.05, -2.76, 1.585), (-0.25, 1.05, 1.95)),
]
FOCUS_KEYS = [(1, 3.67), (36, 2.52), (54, 1.72), (66, 1.78), (112, 3.64), (120, 3.66)]


def build_camera():
    c = "07_CAMERA_RIG"
    cd = bpy.data.cameras.new("CAM_Hero")
    cd.lens = LENS
    cd.sensor_width = 36.0
    cd.sensor_fit = "HORIZONTAL"
    cd.clip_start = 0.02
    cd.dof.use_dof = True
    cd.dof.aperture_fstop = 5.6
    cam = bpy.data.objects.new("CAM_Hero", cd)
    link(cam, c)
    tgt = empty("CAM_Look_Target", CAM_KEYS[0][2], c, "SPHERE", 0.08)
    tc = cam.constraints.new("TRACK_TO")
    tc.target = tgt
    tc.track_axis = "TRACK_NEGATIVE_Z"
    tc.up_axis = "UP_Y"
    for f, loc, t in CAM_KEYS:
        cam.location = loc
        cam.keyframe_insert("location", frame=f)
        tgt.location = t
        tgt.keyframe_insert("location", frame=f)
    for f, d in FOCUS_KEYS:
        cd.dof.focus_distance = d
        cd.dof.keyframe_insert("focus_distance", frame=f)
    for idb in (cam, tgt, cd):
        for fc in fcurves_of(idb):
            for kp in fc.keyframe_points:
                kp.interpolation = "BEZIER"
                kp.handle_left_type = kp.handle_right_type = "AUTO_CLAMPED"
            # frame 1 is already moving ("glides into the room"): extrapolate the first segment's slope
            k0 = fc.keyframe_points[0]
            k0.handle_left_type = k0.handle_right_type = "AUTO"
            fc.update()
    bpy.context.scene.camera = cam
    # visual path for editors (not rendered)
    cu = bpy.data.curves.new("CAM_Path_Preview", "CURVE")
    cu.dimensions = "3D"
    sp = cu.splines.new("POLY")
    sc = bpy.context.scene
    pts = []
    for f in range(FRAMES[0], FRAMES[1] + 1, 2):
        sc.frame_set(f)
        pts.append(cam.matrix_world.translation.copy())
    sp.points.add(len(pts) - 1)
    for p, v in zip(sp.points, pts):
        p.co = (*v, 1)
    po = bpy.data.objects.new("CAM_Path_Preview", cu)
    po.hide_render = True
    link(po, c)
    sc.frame_set(1)
    return cam, tgt


def build_hand_rig(cam, remote_root, hover, press):
    """Hand + remote live in camera space (the operator stands at the camera). Enters from lower left, presses
    the power key, lowers out of frame. The remote points up toward the fan."""
    c = "04_REMOTE_CONTROL"
    rig = empty("HAND_Rig_CamSpace", (0, 0, 0), c, "CUBE", 0.03)
    rig.parent = cam
    remote_root.parent = rig
    # remote orientation in camera space: long axis forward-up-right into the scene, keys facing the camera
    remote_root.rotation_euler = Euler((math.radians(-68), math.radians(-14), math.radians(-28)), "XYZ")
    keys = [(36, (-0.15, -0.28, -0.40)), (43, (-0.10, -0.055, -0.36)), (52, (-0.095, -0.05, -0.36)),
            (62, (-0.14, -0.30, -0.40))]
    for f, loc in keys:
        rig.location = loc
        rig.keyframe_insert("location", frame=f)
    # hidden outside its window so it never appears in shot 1 or 3
    for f, vis in ((35, True), (36, False), (63, False), (64, True)):
        for o in [rig] + list(rig.children_recursive):
            o.hide_render = vis
            o.keyframe_insert("hide_render", frame=f)
    t = TIMING
    for f, hv, pr in ((t["thumb_down"] - 3, 1.0, 0.0), (t["thumb_down"], 0.0, 1.0), (t["thumb_up"] - 2, 0.0, 1.0),
                      (t["thumb_up"] + 2, 1.0, 0.0)):
        hover.value, press.value = hv, pr
        hover.keyframe_insert("value", frame=f)
        press.keyframe_insert("value", frame=f)
    for idb in (rig, hover.id_data):
        for fc in fcurves_of(idb):
            for kp in fc.keyframe_points:
                if fc.data_path != "hide_render":
                    kp.interpolation = "BEZIER"
                    kp.handle_left_type = kp.handle_right_type = "AUTO_CLAMPED"
            fc.update()
    return rig


def build_controls(rotor):
    """CTRL_Fan drives the rotor angle analytically (no baked keys):
         speed ramps with smoothstep from 0 to rpm over `ramp` frames starting at `start`; angle is its integral
         angle = W*T*(u^3 - u^4/2) + W*max(f - start - T, 0),  u = clamp((f - start)/T, 0, 1),  W = rpm*2pi/60/fps
       so acceleration is continuous, terminal angular velocity is constant and motion blur sub-frames are exact.
       CTRL_Lights holds one 0..1 channel per light cue; light energies and emission strengths are driven from it."""
    c = "08_ANIMATION_CONTROLS"
    t = TIMING
    cf = empty("CTRL_Fan", (FAN_XY[0] + 0.9, FAN_XY[1], TRAY - 0.3), c, "SINGLE_ARROW", 0.2)
    cf["start_frame"] = float(t["fan_start"])
    cf["ramp_frames"] = float(t["fan_ramp"])
    cf["rpm"] = t["fan_rpm"]
    cf["direction"] = -1.0           # counter-clockwise seen from below (Indian standard)
    for k, desc in (("start_frame", "frame the fan starts accelerating"), ("ramp_frames", "frames to full speed"),
                    ("rpm", "terminal speed, rev/min (Aerorush max 360)"), ("direction", "-1 CCW from below")):
        cf.id_properties_ui(k).update(description=desc)
    fc = rotor.driver_add("rotation_euler", 2)
    d = fc.driver
    d.type = "SCRIPTED"
    for name, prop in (("s", "start_frame"), ("T", "ramp_frames"), ("rpm", "rpm"), ("dr", "direction")):
        v = d.variables.new()
        v.name = name
        v.type = "SINGLE_PROP"
        v.targets[0].id = cf
        v.targets[0].data_path = '["%s"]' % prop
    W = "(rpm*0.10471975512/%d)" % FPS
    u = "min(max((frame-s)/T,0),1)"
    d.expression = "dr*%s*(T*(%s*%s*%s-0.5*%s*%s*%s*%s)+max(frame-s-T,0))" % (W, u, u, u, u, u, u, u)
    if len(d.expression) > 255:
        raise RuntimeError("driver expression too long")
    cl = empty("CTRL_Lights", (0, RY0 + 0.5, 2.2), c, "PLAIN_AXES", 0.2)
    for g, (f0, f1) in (("wash", t["wash"]), ("perim", t["perim"]), ("cove", t["cove"]), ("shelf", t["shelf"]),
                        ("string", t["string"])):
        cl[g] = 0.0
        cl.keyframe_insert('["%s"]' % g, frame=f0)
        cl[g] = 1.0
        cl.keyframe_insert('["%s"]' % g, frame=f1)
        cl.id_properties_ui(g).update(min=0.0, max=1.0, description="light cue level (0 off, 1 full)")
    for fcv in fcurves_of(cl):
        for kp in fcv.keyframe_points:
            kp.interpolation = "BEZIER"
            kp.handle_left_type = kp.handle_right_type = "AUTO_CLAMPED"
        fcv.update()
    for g, items in GROUPS.items():
        for idb, path, full in items:
            fcd = idb.driver_add(path)
            dd = fcd.driver
            dd.type = "SCRIPTED"
            v = dd.variables.new()
            v.name = "lv"
            v.type = "SINGLE_PROP"
            v.targets[0].id = cl
            v.targets[0].data_path = '["%s"]' % g
            dd.expression = "lv*%.4f" % full
    return cf, cl


# ======================================================================== branding + render settings
def build_branding(cam):
    """No official artwork was supplied, so no logo or lettering is rendered. A camera-parented, non-rendering
    guide marks the top-right logo safe area and the end-slate text block (title-safe 90 %)."""
    c = "09_BRANDING"
    g = empty("BRAND_Guides", (0, 0, 0), c, "PLAIN_AXES", 0.01)
    g.parent = cam
    d = 1.0
    hw = 18.0 / LENS * d
    hh = hw * 9 / 16
    for name, (u0, v0, u1, v1) in (("BRAND_Safe_Logo_TopRight", (0.70, 0.70, 0.92, 0.90)),
                                   ("BRAND_Safe_Message_Right", (0.66, 0.30, 0.92, 0.62))):
        bm = bmesh.new()
        vs = [bm.verts.new(((u * 2 - 1) * hw, (v * 2 - 1) * hh, -d)) for u, v in
              ((u0, v0), (u1, v0), (u1, v1), (u0, v1))]
        for a, b in zip(vs, vs[1:] + vs[:1]):
            bm.edges.new((a, b))
        ob = mesh_obj(name, bm, c)
        ob.parent = cam
        ob.hide_render = True
        ob["normalized_box_u0v0u1v1"] = [u0, v0, u1, v1]


def render_settings():
    sc = bpy.context.scene
    sc.unit_settings.system = "METRIC"
    sc.render.engine = "CYCLES"
    cy = sc.cycles
    cy.device = "CPU"
    cy.samples = 96
    cy.preview_samples = 24
    cy.use_adaptive_sampling = True
    cy.adaptive_threshold = 0.02
    cy.use_denoising = True
    cy.denoiser = "OPENIMAGEDENOISE"
    cy.max_bounces = 8
    cy.diffuse_bounces = 4
    cy.glossy_bounces = 4
    cy.transmission_bounces = 8
    cy.transparent_max_bounces = 16
    cy.caustics_reflective = False
    cy.caustics_refractive = False
    cy.sample_clamp_indirect = 6.0
    cy.blur_glossy = 1.0
    cy.seed = 7
    cy.use_animated_seed = False      # fixed noise pattern frame to frame (denoised): no shimmer
    sc.render.resolution_x, sc.render.resolution_y = 1920, 1080
    sc.render.resolution_percentage = 100
    sc.render.fps = FPS
    sc.frame_start, sc.frame_end = FRAMES
    sc.render.use_motion_blur = True
    sc.render.motion_blur_shutter = 0.5           # 180-degree shutter
    sc.render.image_settings.file_format = "PNG"
    sc.render.image_settings.color_depth = "16"
    sc.view_settings.view_transform = "AgX"
    looks = [i.identifier for i in sc.view_settings.bl_rna.properties["look"].enum_items]
    sc.view_settings.look = "AgX - Base Contrast" if "AgX - Base Contrast" in looks else "None"
    sc.view_settings.exposure = 0.9
    # world: deep dusk blue, only visible through the window
    w = bpy.data.worlds.new("WORLD_Dusk")
    w.use_nodes = True
    bg = w.node_tree.nodes["Background"]
    bg.inputs["Color"].default_value = (0.020, 0.032, 0.070, 1)
    bg.inputs["Strength"].default_value = 1.0
    sc.world = w
    doc = empty("RENDER_Settings_Doc", (0, 0, -0.5), "10_RENDER_SETTINGS", "PLAIN_AXES", 0.05)
    doc.hide_render = True
    for k, v in (("resolution", "1920x1080"), ("fps", FPS), ("frames", "1-120"), ("engine", "Cycles CPU"),
                 ("samples", 96), ("denoise", "OpenImageDenoise"), ("motion_blur_shutter", 0.5),
                 ("view", "AgX Base Contrast, exposure +0.9"), ("lens_mm", LENS), ("fstop", 5.6)):
        doc[k] = v


def main():
    for o in list(bpy.data.objects):
        bpy.data.objects.remove(o, do_unlink=True)
    for c in list(bpy.data.collections):
        bpy.data.collections.remove(c)
    for cname in COLLS:
        coll(cname)
    build_materials()
    build_architecture()
    nslats = build_feature_wall()
    sofa()
    coffee_table()
    lamp = side_table_lamp()
    curtains()
    console_shelves()
    build_lights()
    fan_root, rotor, blades = build_fan()
    remote = build_remote()
    hand, hover, press = build_hand(remote)
    cam, tgt = build_camera()
    build_hand_rig(cam, remote, hover, press)
    build_controls(rotor)
    build_branding(cam)
    render_settings()
    bpy.context.scene.frame_set(1)
    os.makedirs(os.path.dirname(OUT_BLEND), exist_ok=True)
    bpy.ops.file.pack_all()
    bpy.context.preferences.filepaths.save_version = 0
    bpy.ops.wm.save_as_mainfile(filepath=OUT_BLEND, compress=True)
    print("SAVED", OUT_BLEND, "objects", len(bpy.data.objects), "slats", nslats)


main()
