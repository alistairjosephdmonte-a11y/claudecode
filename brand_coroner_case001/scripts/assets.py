"""Reusable procedural assets: materials, primitives, editable typography, neutral stand-in figures, hand rigs.
Imported by environments.py and shot_builder.py (requires bpy)."""
import math
import os

import bpy
from mathutils import Matrix, Quaternion, Vector

import config as C

# ---------------------------------------------------------------- collections
def coll(name, parent=None):
    c = bpy.data.collections.get(name)
    if c is None:
        c = bpy.data.collections.new(name)
        (parent or bpy.context.scene.collection).children.link(c)
    return c


# ---------------------------------------------------------------- materials (procedural, physically plausible, no gloss abuse)
def _principled(m):
    m.use_nodes = True
    return m.node_tree.nodes["Principled BSDF"], m.node_tree


def mat_basic(name, rgb, rough=0.5, metal=0.0, alpha=1.0, emit=None, strength=0.0, coat=0.0):
    m = bpy.data.materials.get(name)
    if m:
        return m
    m = bpy.data.materials.new(name)
    b, nt = _principled(m)
    b.inputs["Base Color"].default_value = (*rgb, 1)
    b.inputs["Roughness"].default_value = rough
    b.inputs["Metallic"].default_value = metal
    if coat:
        b.inputs["Coat Weight"].default_value = coat
    if emit:
        b.inputs["Emission Color"].default_value = (*emit, 1)
        b.inputs["Emission Strength"].default_value = strength
    if alpha < 1:
        b.inputs["Alpha"].default_value = alpha
        m.surface_render_method = "BLENDED"
    m.diffuse_color = (*rgb, alpha)
    return m


def mat_noise(name, rgb_a, rgb_b, scale, rough=0.6, metal=0.0, bump=0.15, kind="noise", direction="X"):
    """Surface variation (paper fibre, wood grain, painted metal, cardboard flutes) from procedural textures."""
    m = bpy.data.materials.get(name)
    if m:
        return m
    m = bpy.data.materials.new(name)
    b, nt = _principled(m)
    b.inputs["Roughness"].default_value = rough
    b.inputs["Metallic"].default_value = metal
    tc = nt.nodes.new("ShaderNodeTexCoord")
    if kind == "wave":
        tex = nt.nodes.new("ShaderNodeTexWave")
        tex.bands_direction = direction
        tex.inputs["Distortion"].default_value = 4.0
    else:
        tex = nt.nodes.new("ShaderNodeTexNoise")
        tex.inputs["Detail"].default_value = 8.0
    tex.inputs["Scale"].default_value = scale
    ramp = nt.nodes.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].color = (*rgb_a, 1)
    ramp.color_ramp.elements[1].color = (*rgb_b, 1)
    bmp = nt.nodes.new("ShaderNodeBump")
    bmp.inputs["Strength"].default_value = bump
    bmp.inputs["Distance"].default_value = 0.002
    nt.links.new(tc.outputs["Object"], tex.inputs["Vector"])
    nt.links.new(tex.outputs["Fac"], ramp.inputs["Fac"])
    nt.links.new(ramp.outputs["Color"], b.inputs["Base Color"])
    nt.links.new(tex.outputs["Fac"], bmp.inputs["Height"])
    nt.links.new(bmp.outputs["Normal"], b.inputs["Normal"])
    m.diffuse_color = (*[(x + y) / 2 for x, y in zip(rgb_a, rgb_b)], 1)
    return m


def mat_fade(name, rgb, rough=0.6, emit=0.0):
    """Per-object material whose opacity is keyable (Eevee: shader alpha; Workbench: viewport alpha)."""
    m = bpy.data.materials.new(name)
    b, nt = _principled(m)
    b.inputs["Base Color"].default_value = (*rgb, 1)
    b.inputs["Roughness"].default_value = rough
    if emit:
        b.inputs["Emission Color"].default_value = (*rgb, 1)
        b.inputs["Emission Strength"].default_value = emit
    m.surface_render_method = "BLENDED"
    m.diffuse_color = (*rgb, 1)
    return m


def key_fade(m, frames_alpha):
    b = m.node_tree.nodes["Principled BSDF"]
    for f, a in frames_alpha:
        b.inputs["Alpha"].default_value = a
        b.inputs["Alpha"].keyframe_insert("default_value", frame=f)
        m.diffuse_color[3] = a
        m.keyframe_insert("diffuse_color", index=3, frame=f)


def pal(key):
    return C.hex_to_linear(C.PALETTE[key])


def library():
    """The shared material library (deterministic names)."""
    return {
        "black": mat_basic("MAT_CoronerBlack", pal("CORONER_BLACK"), 0.8),
        "ivory": mat_noise("MAT_Paper_EvidenceIvory", pal("EVIDENCE_IVORY"), tuple(c * 0.92 for c in pal("EVIDENCE_IVORY")), 140, 0.85, bump=0.05),
        "paper_white": mat_noise("MAT_Paper_Office", (0.84, 0.83, 0.8), (0.78, 0.77, 0.74), 160, 0.85, bump=0.04),
        "red": mat_basic("MAT_VerdictRed", pal("VERDICT_RED"), 0.55),
        "blue": mat_basic("MAT_BlockbusterBlue_Editorial", pal("BLOCKBUSTER_BLUE"), 0.5),
        "yellow": mat_basic("MAT_RetailYellow_Editorial", pal("RETAIL_YELLOW"), 0.5),
        "nred": mat_basic("MAT_NetflixRed_Editorial", pal("NETFLIX_RED"), 0.55),
        "grey": mat_basic("MAT_ArchiveGrey", pal("ARCHIVE_GREY"), 0.6),
        "ink": mat_basic("MAT_Ink", (0.03, 0.03, 0.035), 0.7),
        "wood": mat_noise("MAT_Wood_Walnut", (0.13, 0.07, 0.035), (0.2, 0.11, 0.055), 6, 0.45, bump=0.08, kind="wave"),
        "wood_light": mat_noise("MAT_Wood_Oak", (0.36, 0.24, 0.13), (0.45, 0.31, 0.18), 6, 0.5, bump=0.08, kind="wave"),
        "metal_paint": mat_noise("MAT_PaintedMetal_Grey", (0.32, 0.33, 0.34), (0.36, 0.37, 0.38), 40, 0.45, metal=0.3, bump=0.03),
        "metal_dark": mat_noise("MAT_PaintedMetal_Dark", (0.06, 0.065, 0.07), (0.08, 0.085, 0.09), 40, 0.5, metal=0.4, bump=0.03),
        "steel": mat_basic("MAT_Steel_Brushed", (0.55, 0.56, 0.57), 0.35, 1.0),
        "plastic_black": mat_basic("MAT_Plastic_Black", (0.02, 0.02, 0.022), 0.4),
        "plastic_beige": mat_basic("MAT_Plastic_Beige_PC", (0.62, 0.58, 0.5), 0.45),
        "glass": mat_basic("MAT_Glass_Clear", (0.75, 0.82, 0.85), 0.05, 0.0, alpha=0.18),
        "glass_tint": mat_basic("MAT_Glass_Tinted", (0.12, 0.16, 0.2), 0.08, 0.2, alpha=0.55),
        "cardboard": mat_noise("MAT_Cardboard", (0.45, 0.33, 0.2), (0.52, 0.39, 0.24), 30, 0.85, bump=0.1, kind="wave", direction="Y"),
        "carpet": mat_noise("MAT_Carpet_Blue_Grey", (0.08, 0.1, 0.14), (0.1, 0.12, 0.16), 300, 0.95, bump=0.2),
        "floor_tile": mat_noise("MAT_Floor_Vinyl", (0.45, 0.45, 0.43), (0.5, 0.5, 0.48), 3, 0.6, bump=0.02),
        "wall_paint": mat_noise("MAT_Wall_Paint_Warm", (0.62, 0.6, 0.55), (0.6, 0.58, 0.53), 20, 0.85, bump=0.02),
        "concrete": mat_noise("MAT_Concrete", (0.32, 0.31, 0.3), (0.4, 0.39, 0.37), 12, 0.9, bump=0.2),
        "asphalt": mat_noise("MAT_Asphalt", (0.05, 0.05, 0.055), (0.08, 0.08, 0.085), 60, 0.9, bump=0.2),
        "fabric": mat_noise("MAT_Fabric_Chair", (0.08, 0.08, 0.09), (0.1, 0.1, 0.11), 200, 0.95, bump=0.1),
        "suit": mat_noise("MAT_Figure_Suit_Charcoal", (0.08, 0.085, 0.095), (0.1, 0.105, 0.115), 220, 0.8, bump=0.05),
        "suit_navy": mat_noise("MAT_Figure_Suit_Navy", (0.04, 0.06, 0.1), (0.05, 0.07, 0.12), 220, 0.8, bump=0.05),
        "casual_a": mat_noise("MAT_Figure_Casual_A", (0.25, 0.22, 0.18), (0.28, 0.25, 0.2), 200, 0.85, bump=0.05),
        "casual_b": mat_noise("MAT_Figure_Casual_B", (0.12, 0.18, 0.22), (0.14, 0.2, 0.25), 200, 0.85, bump=0.05),
        "casual_c": mat_noise("MAT_Figure_Casual_C", (0.3, 0.12, 0.1), (0.33, 0.14, 0.12), 200, 0.85, bump=0.05),
        "skin_neutral": mat_basic("MAT_Figure_Neutral_Skin", (0.55, 0.42, 0.34), 0.6),
        "hair_neutral": mat_basic("MAT_Figure_Neutral_Hair", (0.06, 0.05, 0.045), 0.6),
        "shoe": mat_basic("MAT_Figure_Shoe", (0.025, 0.022, 0.02), 0.35),
        "fluoro": mat_basic("MAT_Fluorescent_Panel", (0.9, 0.92, 0.9), 0.4, emit=(0.95, 0.98, 1.0), strength=6.0),
        "warm_glow": mat_basic("MAT_Window_WarmGlow", (0.4, 0.3, 0.2), 0.4, emit=(1.0, 0.75, 0.45), strength=2.5),
        "crt": mat_basic("MAT_CRT_Screen_Glow", (0.1, 0.12, 0.14), 0.15, emit=(0.55, 0.68, 0.85), strength=1.6),
        "case_colors": [mat_basic(f"MAT_MediaCase_{i}", c, 0.45) for i, c in enumerate(
            ((0.08, 0.08, 0.1), (0.35, 0.05, 0.05), (0.05, 0.12, 0.3), (0.3, 0.25, 0.05), (0.05, 0.2, 0.1), (0.4, 0.4, 0.42),
             (0.18, 0.05, 0.22), (0.5, 0.25, 0.05)))],
    }


# ---------------------------------------------------------------- geometry
BOX_FACES = ((0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7))
BOX_SIGNS = ((-1, -1, -1), (1, -1, -1), (1, 1, -1), (-1, 1, -1), (-1, -1, 1), (1, -1, 1), (1, 1, 1), (-1, 1, 1))


def mesh_boxes(name, boxes):
    verts, faces, mats, idx = [], [], [], []
    for c, s, m in boxes:
        if m not in mats:
            mats.append(m)
        base = len(verts)
        verts += [(c[0] + sx * s[0] / 2, c[1] + sy * s[1] / 2, c[2] + sz * s[2] / 2) for sx, sy, sz in BOX_SIGNS]
        faces += [tuple(base + i for i in f) for f in BOX_FACES]
        idx += [mats.index(m)] * 6
    me = bpy.data.meshes.new(name)
    me.from_pydata(verts, [], faces)
    for m in mats:
        me.materials.append(m)
    me.polygons.foreach_set("material_index", idx)
    me.update()
    return me


def mesh_cyl(name, r, h, m, seg=24, r_top=None, axis="Z"):
    r_top = r if r_top is None else r_top
    v = [(r * math.cos(2 * math.pi * j / seg), r * math.sin(2 * math.pi * j / seg), 0) for j in range(seg)]
    v += [(r_top * math.cos(2 * math.pi * j / seg), r_top * math.sin(2 * math.pi * j / seg), h) for j in range(seg)]
    f = [(j, (j + 1) % seg, seg + (j + 1) % seg, seg + j) for j in range(seg)] + [tuple(reversed(range(seg))), tuple(range(seg, 2 * seg))]
    me = bpy.data.meshes.new(name)
    me.from_pydata(v, [], f)
    me.materials.append(m)
    for p in me.polygons:
        p.use_smooth = True
    me.update()
    return me


def mesh_sphere(name, r, m, seg=24, rings=12):
    v, f = [(0, 0, -r)], []
    for i in range(1, rings):
        th = math.pi * i / rings - math.pi / 2
        for j in range(seg):
            ph = 2 * math.pi * j / seg
            v.append((r * math.cos(th) * math.cos(ph), r * math.cos(th) * math.sin(ph), r * math.sin(th)))
    v.append((0, 0, r))
    top = len(v) - 1
    f += [(0, 1 + (j + 1) % seg, 1 + j) for j in range(seg)]
    for i in range(rings - 2):
        for j in range(seg):
            a, b = 1 + i * seg + j, 1 + i * seg + (j + 1) % seg
            f.append((a, b, b + seg, a + seg))
    base = 1 + (rings - 2) * seg
    f += [(base + j, base + (j + 1) % seg, top) for j in range(seg)]
    me = bpy.data.meshes.new(name)
    me.from_pydata(v, [], f)
    me.materials.append(m)
    for p in me.polygons:
        p.use_smooth = True
    me.update()
    return me


def obj(name, data, coll_, loc=(0, 0, 0), rot=(0, 0, 0), parent=None, scale=None):
    o = bpy.data.objects.new(name, data)
    o.location, o.rotation_euler = loc, rot
    if scale:
        o.scale = scale
    coll_.objects.link(o)
    if parent is not None:
        o.parent = parent
    return o


def box(name, coll_, c, s, m, rot=(0, 0, 0), parent=None, bevel=0.0):
    o = obj(name, mesh_boxes(name, [((0, 0, 0), s, m)]), coll_, c, rot, parent)
    if bevel:
        b = o.modifiers.new("Bevel", "BEVEL")
        b.width, b.segments = bevel, 2
    return o


def empty(name, coll_, loc=(0, 0, 0), size=0.2, shape="PLAIN_AXES", parent=None):
    o = bpy.data.objects.new(name, None)
    o.empty_display_size, o.empty_display_type = size, shape
    o.location = loc
    coll_.objects.link(o)
    if parent is not None:
        o.parent = parent
    return o


# ---------------------------------------------------------------- editable typography
_FONT_CACHE = {}


def font(kind="regular"):
    if kind in _FONT_CACHE:
        return _FONT_CACHE[kind]
    path = os.path.join(C.P["fonts"], C.FONTS[kind])
    f = bpy.data.fonts.load(path, check_existing=True)
    _FONT_CACHE[kind] = f
    return f


def text(name, body, coll_, loc, size, m, kind="regular", align="LEFT", rot=(math.radians(90), 0, 0), parent=None,
         extrude=0.0, spacing=1.0, width=None):
    """Editable Blender text object. Default rotation stands it upright facing -Y (graphics stages)."""
    cu = bpy.data.curves.new(name, "FONT")
    cu.body = body
    cu.font = font(kind)
    cu.size = size
    cu.align_x = align
    cu.align_y = "BOTTOM_BASELINE"
    cu.extrude = extrude
    cu.space_character = spacing
    if width:
        cu.text_boxes[0].width = width
    cu.materials.append(m)
    return obj(name, cu, coll_, loc, rot, parent)


# ---------------------------------------------------------------- simple rigs
def solve_2bone(root, target, l1, l2, pole):
    dv = target - root
    d = min(max(dv.length, 0.05), l1 + l2 - 1e-4)
    dirn = dv.normalized()
    perp = pole - dirn * pole.dot(dirn)
    perp = perp.normalized() if perp.length > 1e-6 else Vector((0, 0, -1))
    a = (l1 * l1 - l2 * l2 + d * d) / (2 * d)
    h = math.sqrt(max(l1 * l1 - a * a, 0.0))
    return root + dirn * a + perp * h, root + dirn * d


def seg_matrix(origin, target, side):
    z = (origin - target).normalized()
    y = side - z * side.dot(z)
    y = y.normalized() if y.length > 1e-6 else Vector((0, 1, 0))
    x = y.cross(z)
    m = Matrix((x, y, z)).transposed().to_4x4()
    m.translation = origin
    return m


def smooth(t):
    t = min(1.0, max(0.0, t))
    return t * t * (3 - 2 * t)


def bake(o, path, rows):
    """rows: list of (frame, tuple) - bulk F-curve write."""
    o.keyframe_insert(path, frame=rows[0][0])
    from bpy_extras import anim_utils
    ad = o.animation_data
    fcs = anim_utils.action_get_channelbag_for_slot(ad.action, ad.action_slot).fcurves
    for fc in [fc for fc in fcs if fc.data_path == path]:
        i = fc.array_index
        kp = fc.keyframe_points
        while len(kp):
            kp.remove(kp[0])
        kp.add(len(rows))
        co = [0.0] * (2 * len(rows))
        co[0::2] = [float(r[0]) for r in rows]
        co[1::2] = [float(r[1][i]) for r in rows]
        kp.foreach_set("co", co)
        try:
            kp.foreach_set("interpolation", [1] * len(rows))
        except Exception:
            pass
        fc.update()


class Figure:
    """Neutral, non-identifying stand-in (no face, generic clothing). World-space parts baked per frame.
    path: list of (frame, (x, y), yaw_deg) keys; feet are planted procedurally (no sliding)."""
    D = dict(thigh=0.45, shin=0.43, ankle=0.08, upper=0.3, fore=0.27, torso=0.56, neck=0.08, head=0.23, hip=0.1, sh=0.2)

    def __init__(self, name, coll_, M, cloth, seated=False, scale=1.0):
        self.name, self.coll, self.seated = name, coll_, seated
        D = self.D
        self.parts = {}
        mk = lambda k, boxes: self.parts.__setitem__(k, obj(f"{name}_{k}", mesh_boxes(f"{name}_{k}", boxes), coll_))  # noqa: E731
        mk("PELVIS", [((0, 0, 0), (0.24, 0.36, 0.2), cloth)])
        mk("TORSO", [((0, 0, D["torso"] / 2), (0.25, 0.42, D["torso"]), cloth)])
        mk("HEAD", [((0, 0, D["head"] / 2), (0.2, 0.17, D["head"]), M["skin_neutral"]),
                    ((-0.015, 0, D["head"] * 0.82), (0.21, 0.18, D["head"] * 0.42), M["hair_neutral"])])
        for s in "LR":
            mk(f"UPPER_{s}", [((0, 0, -D["upper"] / 2), (0.1, 0.1, D["upper"] + 0.02), cloth)])
            mk(f"FORE_{s}", [((0, 0, -D["fore"] / 2), (0.085, 0.085, D["fore"]), cloth),
                             ((0, 0, -D["fore"] - 0.08), (0.08, 0.03, 0.16), M["skin_neutral"])])
            mk(f"THIGH_{s}", [((0, 0, -D["thigh"] / 2), (0.15, 0.15, D["thigh"]), cloth)])
            mk(f"SHIN_{s}", [((0, 0, -D["shin"] / 2), (0.11, 0.11, D["shin"]), cloth)])
            mk(f"FOOT_{s}", [((0.08, 0, -D["ankle"] / 2), (0.27, 0.1, D["ankle"]), M["shoe"])])
        for o in self.parts.values():
            o.rotation_mode = "QUATERNION"
            b = o.modifiers.new("Bevel", "BEVEL")
            b.width, b.segments = 0.02, 2

    def animate(self, f0, f1, path, ground=0.0, head_keys=None, arm_targets=None, dur=11):
        """path: [(frame, (x,y), yaw_deg)], linear-eased between keys. arm_targets: {side: fn(frame)->world Vector or None}."""
        D = self.D
        keys = sorted(path)

        def root(f):
            if f <= keys[0][0]:
                k = keys[0]
                return Vector((k[1][0], k[1][1], ground)), math.radians(k[2])
            for a, b in zip(keys, keys[1:]):
                if a[0] <= f <= b[0]:
                    t = smooth((f - a[0]) / max(b[0] - a[0], 1))
                    p = Vector(a[1]).lerp(Vector(b[1]), t)
                    yaw = math.radians(a[2] + (b[2] - a[2]) * t)
                    return Vector((p.x, p.y, ground)), yaw
            k = keys[-1]
            return Vector((k[1][0], k[1][1], ground)), math.radians(k[2])

        def home(f, sg):
            p, yaw = root(min(max(f, f0), f1))
            left = Vector((-math.sin(yaw), math.cos(yaw), 0))
            h = p + left * sg * D["hip"]
            h.z = ground + D["ankle"]
            return h, yaw

        plant = {s: home(f0, s) for s in (1, -1)}
        swing, last = None, -1
        self.feet_log = {1: [], -1: []}
        rows = {k: [] for k in self.parts}
        prev_q = {}
        for f in range(f0, f1 + 1):
            if swing is None and not self.seated:
                best = None
                for s in (1, -1):
                    hp, hy = home(f + dur, s)
                    err = (hp - plant[s][0]).length + abs(hy - plant[s][1]) * 0.12
                    sc = err + (0.0 if s == last else 0.015)
                    if err > 0.035 and (best is None or sc > best[0]):
                        best = (sc, s)
                if best:
                    s = best[1]
                    tp, ty = home(f + int(dur * 1.6), s)
                    swing = (s, f, plant[s][0].copy(), tp, plant[s][1], ty)
            feet, t_sw = {}, 0.0
            for s in (1, -1):
                if swing and swing[0] == s:
                    t_sw = (f - swing[1]) / dur
                    k = smooth(t_sw)
                    pos = swing[2].lerp(swing[3], k)
                    pos.z += 0.07 * math.sin(math.pi * min(t_sw, 1.0))
                    feet[s] = (pos, swing[4] + (swing[5] - swing[4]) * k, True)
                else:
                    feet[s] = (plant[s][0].copy(), plant[s][1], False)
                self.feet_log[s].append((f, feet[s][0].copy(), feet[s][2]))
            if swing and f - swing[1] >= dur:
                plant[swing[0]] = (swing[3], swing[5])
                last = swing[0]
                swing = None
            p, yaw = root(f)
            R = Matrix.Translation(p) @ Matrix.Rotation(yaw, 4, "Z")
            if self.seated:
                pel = R @ Matrix.Translation((0, 0, 0.47 + 0.1))
            else:
                bob = 0.012 * math.sin(math.pi * min(t_sw, 1.0)) if swing else 0.0
                mid = (feet[1][0] + feet[-1][0]) / 2
                lm = R.inverted() @ Vector((mid.x, mid.y, ground))
                pel = R @ Matrix.Translation((lm.x * 0.5, lm.y * 0.5, ground + D["thigh"] + D["shin"] + D["ankle"] - 0.015 + bob))
            torso = pel @ Matrix.Translation((0, 0, 0.06))
            hk = head_keys(f) if head_keys else (0.0, 0.0)
            head = torso @ Matrix.Translation((0, 0, D["torso"] + D["neck"])) @ Matrix.Rotation(math.radians(hk[0]), 4, "Z") \
                @ Matrix.Rotation(math.radians(hk[1]), 4, "Y")
            out = {"PELVIS": pel, "TORSO": torso, "HEAD": head}
            tq = torso.to_quaternion()
            for side, sg in (("L", 1), ("R", -1)):
                sh = (torso @ Matrix.Translation((0, sg * D["sh"], D["torso"] - 0.05))).translation
                tgt = arm_targets[side](f) if arm_targets and arm_targets.get(side) else None
                if tgt is None:
                    swing_amt = 0.0 if self.seated else 0.12 * (feet[-sg][2] - feet[sg][2]) * math.sin(math.pi * min(t_sw, 1.0))
                    tgt = sh + tq @ Vector((0.05 + swing_amt, sg * 0.04, -(D["upper"] + D["fore"]) * 0.96))
                el, wr = solve_2bone(sh, tgt, D["upper"], D["fore"], tq @ Vector((-0.6, sg * 0.5, -0.3)))
                out[f"UPPER_{side}"] = seg_matrix(sh, el, tq @ Vector((0, sg, 0)))
                out[f"FORE_{side}"] = seg_matrix(el, wr, tq @ Vector((0, -sg, 0)))
                hip = (pel @ Matrix.Translation((0, sg * D["hip"], 0))).translation
                if self.seated:
                    knee = hip + (R.to_quaternion() @ Vector((D["thigh"], 0, -0.02)))
                    ank = Vector((knee.x, knee.y, ground + D["ankle"])) + (R.to_quaternion() @ Vector((0.05, 0, 0)))
                    fyaw = yaw
                else:
                    ank, fyaw = feet[sg][0], feet[sg][1]
                    knee, ank = solve_2bone(hip, ank, D["thigh"], D["shin"], Vector((math.cos(fyaw), math.sin(fyaw), 0.05)))
                lv = Vector((-math.sin(fyaw), math.cos(fyaw), 0))
                out[f"THIGH_{side}"] = seg_matrix(hip, knee, lv)
                out[f"SHIN_{side}"] = seg_matrix(knee, ank, lv)
                out[f"FOOT_{side}"] = Matrix.Translation(ank) @ Matrix.Rotation(fyaw, 4, "Z")
            for k, m in out.items():
                loc, q, _ = m.decompose()
                if k in prev_q and prev_q[k].dot(q) < 0:
                    q.negate()
                prev_q[k] = q
                rows[k].append((f, (loc.x, loc.y, loc.z, q.w, q.x, q.y, q.z)))
        for k, o in self.parts.items():
            bake(o, "location", [(f, v[:3]) for f, v in rows[k]])
            bake(o, "rotation_quaternion", [(f, v[3:]) for f, v in rows[k]])


class Hand:
    """Hands-only rig: sleeve + forearm + hand with a finger block. carry(): baked contact with a prop."""

    def __init__(self, name, coll_, M, cloth):
        self.root = empty(f"{name}_WRIST", coll_, size=0.05)
        self.root.rotation_mode = "QUATERNION"
        obj(f"{name}_Sleeve", mesh_cyl(f"{name}_Sleeve", 0.045, 0.32, cloth, 20), coll_, (0, 0, 0.0), (0, math.radians(-90), 0), self.root)
        obj(f"{name}_Palm", mesh_boxes(f"{name}_Palm", [((0.05, 0, 0), (0.1, 0.085, 0.025), M["skin_neutral"]),
                                                        ((0.135, 0, -0.004), (0.075, 0.08, 0.018), M["skin_neutral"]),
                                                        ((0.04, 0.05, -0.006), (0.06, 0.022, 0.018), M["skin_neutral"])]),
            coll_, (0, 0, 0), (0, 0, 0), self.root)
        self.name = name

    def animate(self, keys, prop=None, grab=None, release=None, rest=None):
        """keys: [(frame, (x,y,z), (pitch_deg, yaw_deg))]. prop is carried from grab to release frame, then rests at `rest`."""
        keys = sorted(keys)
        f0, f1 = keys[0][0], keys[-1][0]

        def at(f):
            for a, b in zip(keys, keys[1:]):
                if a[0] <= f <= b[0]:
                    t = smooth((f - a[0]) / max(b[0] - a[0], 1))
                    return Vector(a[1]).lerp(Vector(b[1]), t), (a[2][0] + (b[2][0] - a[2][0]) * t, a[2][1] + (b[2][1] - a[2][1]) * t)
            k = keys[0] if f < keys[0][0] else keys[-1]
            return Vector(k[1]), k[2]

        rows, prow = [], []
        off, last_m = None, None
        for f in range(f0, f1 + 1):
            p, (pitch, yaw) = at(f)
            q = (Matrix.Rotation(math.radians(yaw), 4, "Z") @ Matrix.Rotation(math.radians(pitch), 4, "Y")).to_quaternion()
            rows.append((f, (p.x, p.y, p.z, q.w, q.x, q.y, q.z)))
            if prop is not None:
                hm = Matrix.Translation(p) @ q.to_matrix().to_4x4()
                if grab is not None and f >= grab and (release is None or f < release):
                    if off is None:
                        off = hm.inverted() @ prop.matrix_world
                    m = hm @ off
                    last_m = m
                elif release is not None and f >= release:
                    m = rest if rest is not None else last_m          # set down exactly where the hand left it
                else:
                    m = prop.matrix_world.copy()
                l2, q2, _ = m.decompose()
                prow.append((f, (l2.x, l2.y, l2.z, q2.w, q2.x, q2.y, q2.z)))
        bake(self.root, "location", [(f, v[:3]) for f, v in rows])
        bake(self.root, "rotation_quaternion", [(f, v[3:]) for f, v in rows])
        if prop is not None:
            prop.rotation_mode = "QUATERNION"
            bake(prop, "location", [(f, v[:3]) for f, v in prow])
            bake(prop, "rotation_quaternion", [(f, v[3:]) for f, v in prow])
        return off
