"""Procedural blocking characters: armature control rig + bone-parented body/wardrobe meshes.

Characters are modelled facing -Y with origin between the feet. Joint rotations are authored in this
character frame and converted to bone-local quaternions (see Character.local_quat).
"""
import math
from math import radians
import bpy
import bmesh
from mathutils import Vector, Matrix

from common import (bm_box, bm_ellipsoid, bm_limb, mesh_from_bm, new_object, skin, fabric, leather,
                    patterned_shirt, principled, I3)
from cap_asset import cap_object, RX as CAP_RX

CAST = {
    "HERO_01": dict(H=1.75, w=1.0, sex="M", age=26, skin="#8A5A3C", hair="#0B0A0A", hair_style="natural",
                    top="leather", top_hex="#151314", shirt="#36383B", legs="denim", legs_hex="#6F8198",
                    shoes="#0E0E10", cap="hero", bulk=1.08,
                    desc="Indian man 26, medium-brown skin, lean, natural black hair, oversized worn black leather "
                         "jacket, charcoal shirt, loose faded denim, black trainers, royal-blue six-panel cap"),
    "BOUNCER_01": dict(H=1.90, w=1.24, sex="M", age=42, skin="#5A3A26", hair="#0A0909", hair_style="crop",
                       top="suit", top_hex="#2A2C30", shirt="#E9E6DF", legs="suit", legs_hex="#2A2C30",
                       shoes="#0B0B0C", cap="navy", moustache=True, bulk=1.06,
                       desc="Indian man 42, tall broad, deep-brown skin, close-cropped hair, moustache, dark charcoal "
                            "suit, white shirt, navy cap, neutral expression"),
    "GUEST_01": dict(H=1.72, w=1.0, sex="M", age=25, skin="#7A4E33", hair="#0D0B0A", hair_style="natural",
                     top="shirt", top_hex="#59633A", legs="cloth", legs_hex="#2E3340", shoes="#4A3424",
                     desc="Indian man 25, olive shirt, no cap"),
    "GUEST_02": dict(H=1.62, w=0.92, sex="F", age=27, skin="#94613F", hair="#0C0A0A", hair_style="long",
                     top="bomber", top_hex="#4E5530", legs="cloth", legs_hex="#232428", shoes="#D9D6CF",
                     bulk=1.16, prop="cone",
                     desc="Indian woman 27, oversized olive bomber, dark trousers, cartoon traffic cone on head"),
    "GUEST_03": dict(H=1.76, w=1.02, sex="M", age=30, skin="#6C4429", hair="#0B0909", hair_style="natural",
                     top="pattern", top_hex="#D9CDAF", legs="cloth", legs_hex="#26272B", shoes="#1A1A1A",
                     prop="dish",
                     desc="Indian man 30, cream patterned shirt, dark trousers, giant flat cartoon satellite-dish hat"),
    "GUEST_04": dict(H=1.60, w=0.9, sex="F", age=26, skin="#9A6747", hair="#0A0909", hair_style="bun",
                     top="shirt", top_hex="#121214", legs="cloth", legs_hex="#2A3142", shoes="#101010",
                     desc="Indian woman 26, black top, no cap; receives blue cap from bouncer"),
}
_EXTRA_LOOKS = [
    ("M", 1.78, "#7B5034", "#3B4A5E", "#1F2228", "hero"),
    ("F", 1.63, "#8E5C3D", "#6B2E3A", "#202126", "navy"),
    ("M", 1.70, "#5F3C27", "#C9C2B4", "#2B2E36", "navy"),
    ("F", 1.58, "#A06B4A", "#2F4B45", "#1B1B1F", "hero"),
    ("M", 1.82, "#6A4630", "#141414", "#3A3F4A", "hero"),
    ("F", 1.66, "#7F5236", "#B58A3C", "#222226", "navy"),
]
for i, (sx, h, sk, top, legs, cap) in enumerate(_EXTRA_LOOKS, 1):
    CAST["CLUB_EXTRA_%02d" % i] = dict(
        H=h, w=0.92 if sx == "F" else 1.0, sex=sx, age=22 + i * 2, skin=sk, hair="#0B0A0A",
        hair_style="bun" if sx == "F" else "natural", top="shirt", top_hex=top, legs="cloth", legs_hex=legs,
        shoes="#111113", cap=cap, desc="Indian adult clubgoer (21+), %s cap" % ("blue" if cap == "hero" else "navy"))

BONES = ["root", "hips", "spine", "chest", "neck", "head", "eyes", "brow.L", "brow.R",
         "upper_arm.L", "forearm.L", "hand.L", "upper_arm.R", "forearm.R", "hand.R",
         "thigh.L", "shin.L", "foot.L", "thigh.R", "shin.R", "foot.R"]
ROT_BONES = [b for b in BONES if b not in ("root", "eyes", "brow.L", "brow.R")]

_MAT_CACHE = {}


def _m(key, factory):
    if key not in _MAT_CACHE:
        _MAT_CACHE[key] = factory()
    return _MAT_CACHE[key]


class Character:
    def __init__(self, name, coll, cap_mats, cap_coll=None):
        self.name = name
        self.cap_coll = cap_coll or coll
        sp = CAST[name]
        self.spec = sp
        H = sp["H"]
        self.H = H
        s = H / 1.75
        self.s = s
        fem = sp["sex"] == "F"
        w = sp.get("w", 1.0)
        bulk = sp.get("bulk", 1.0)
        self.ankle = 0.045 * H
        self.L = 0.485 * H
        self.hip_z = self.ankle + self.L
        self.sh_x = 0.19 * s * w * (0.9 if fem else 1.0)
        self.hip_x = 0.085 * s * (1.08 if fem else 1.0)
        self.head_c = Vector((0, -0.008 * s, 0.87 * H + 0.06 * s))
        self.head_r = Vector((0.075, 0.095, 0.118)) * s
        self.coll = coll
        self._build_rig()
        self._build_body(fem, w, bulk, cap_mats)

    # ------------------------------------------------------------ rig
    def _build_rig(self):
        H, s = self.H, self.s
        ad = bpy.data.armatures.new(self.name + "_RIG")
        ad.display_type = "STICK"
        arm = bpy.data.objects.new(self.name + "_RIG", ad)
        self.coll.objects.link(arm)
        self.arm = arm
        bpy.context.view_layer.objects.active = arm
        arm.select_set(True)
        bpy.ops.object.mode_set(mode="EDIT")
        eb = ad.edit_bones
        hz = self.hip_z
        hc = self.head_c

        def bone(n, h, t, parent=None, connect=False):
            b = eb.new(n)
            b.head, b.tail = Vector(h), Vector(t)
            b.roll = 0.0
            if parent:
                b.parent = eb[parent]
                b.use_connect = connect
            return b

        bone("root", (0, 0, 0), (0, 0.25 * s, 0))
        bone("hips", (0, 0, hz), (0, 0, hz + 0.08 * H), "root")
        bone("spine", (0, 0, hz + 0.08 * H), (0, 0, 0.70 * H), "hips", True)
        bone("chest", (0, 0, 0.70 * H), (0, 0, 0.82 * H), "spine", True)
        bone("neck", (0, 0, 0.82 * H), (0, 0, 0.87 * H), "chest", True)
        bone("head", (0, 0, 0.87 * H), (0, 0, 1.0 * H), "neck", True)
        bone("eyes", (0, -0.07 * s, hc.z + 0.012 * s), (0, -0.07 * s, hc.z + 0.04 * s), "head")
        for side, sx in (("L", 1), ("R", -1)):
            bone("brow." + side, (sx * 0.032 * s, -0.07 * s, hc.z + 0.035 * s),
                 (sx * 0.032 * s, -0.07 * s, hc.z + 0.055 * s), "head")
            shz = 0.815 * H
            x = sx * self.sh_x
            bone("upper_arm." + side, (x, 0, shz), (x, 0, shz - 0.186 * H), "chest")
            bone("forearm." + side, (x, 0, shz - 0.186 * H), (x, 0, shz - 0.332 * H), "upper_arm." + side, True)
            bone("hand." + side, (x, 0, shz - 0.332 * H), (x, 0, shz - 0.432 * H), "forearm." + side, True)
            hx = sx * self.hip_x
            bone("thigh." + side, (hx, 0, hz), (hx, 0, hz - self.L / 2), "hips")
            bone("shin." + side, (hx, 0, hz - self.L / 2), (hx, 0, self.ankle), "thigh." + side, True)
            bone("foot." + side, (hx, 0, self.ankle), (hx, -0.13 * s, 0.02 * s), "shin." + side, True)
        bpy.ops.object.mode_set(mode="OBJECT")
        arm.select_set(False)
        for n in ("neck", "upper_arm.L", "upper_arm.R"):
            ad.bones[n].inherit_scale = "NONE"
        self.rest3 = {b.name: b.matrix_local.to_3x3() for b in ad.bones}
        for pb in arm.pose.bones:
            pb.rotation_mode = "QUATERNION"
        arm["character"] = self.name
        arm["description"] = self.spec["desc"]

    def local_quat(self, bone, R3):
        Rr = self.rest3[bone]
        return (Rr.transposed() @ R3 @ Rr).to_quaternion()

    def local_vec(self, bone, v):
        return self.rest3[bone].transposed() @ Vector(v)

    def add_ik(self, side, cname, target):
        pb = self.arm.pose.bones["hand." + side]
        c = pb.constraints.new("IK")
        c.name = cname
        c.target = target
        c.chain_count = 3
        c.use_tail = True
        c.use_stretch = False
        c.influence = 0.0
        return c

    # ------------------------------------------------------------ body
    def _part(self, label, bone, mat, build):
        bm = bmesh.new()
        build(bm)
        ob = new_object("%s_%s" % (self.name, label), mesh_from_bm("%s_%s" % (self.name, label), bm), self.coll, [mat])
        self._parent(ob, bone)
        return ob

    def _parent(self, ob, bone):
        b = self.arm.data.bones[bone]
        ob.parent = self.arm
        ob.parent_type = "BONE"
        ob.parent_bone = bone
        ob.matrix_parent_inverse = (b.matrix_local @ Matrix.Translation((0, b.length, 0))).inverted()

    def bone_attach_matrix(self, bone):
        b = self.arm.data.bones[bone]
        return b.matrix_local @ Matrix.Translation((0, b.length, 0))

    def _build_body(self, fem, w, bulk, cap_mats):
        sp, s, H = self.spec, self.s, self.H
        nm = self.name
        mskin = _m("skin" + nm, lambda: skin("MAT_SKIN_" + nm, sp["skin"]))
        mhair = _m("hair" + sp["hair"], lambda: principled("MAT_HAIR_BLACK", sp["hair"], rough=0.55, bump=0.3, bump_scale=900))
        top = sp["top"]
        if top == "leather":
            mtop = _m("leather", lambda: leather("MAT_LEATHER_JACKET_WORN"))
        elif top == "pattern":
            mtop = _m("pattern", lambda: patterned_shirt("MAT_SHIRT_CREAM_PATTERNED"))
        elif top == "suit":
            mtop = _m("suit", lambda: fabric("MAT_SUIT_CHARCOAL_WOOL", sp["top_hex"], rough=0.78, sheen=0.25, weave=1600))
        else:
            mtop = _m("top" + sp["top_hex"], lambda: fabric("MAT_TOP_" + sp["top_hex"][1:], sp["top_hex"]))
        if sp["legs"] == "denim":
            mlegs = _m("denim", lambda: fabric("MAT_DENIM_FADED", sp["legs_hex"], rough=0.88, sheen=0.15, weave=700, strength=0.25, var=0.22))
        elif sp["legs"] == "suit":
            mlegs = mtop
        else:
            mlegs = _m("legs" + sp["legs_hex"], lambda: fabric("MAT_TROUSERS_" + sp["legs_hex"][1:], sp["legs_hex"]))
        mshoe = _m("shoe" + sp["shoes"], lambda: principled("MAT_SHOE_" + sp["shoes"][1:], sp["shoes"], rough=0.6, bump=0.05))
        mdark = _m("eyedark", lambda: principled("MAT_EYE_IRIS_DARK", "#120B08", rough=0.15, spec=0.6))
        mwhite = _m("eyewhite", lambda: principled("MAT_EYE_WHITE", "#C9C1B6", rough=0.25))
        mlip = _m("lip" + nm, lambda: principled("MAT_LIP_" + nm, _darken(sp["skin"], 0.72), rough=0.45, sss=0.1))
        self.mats = dict(skin=mskin, top=mtop, legs=mlegs)

        hz = self.hip_z
        b = bulk
        sw = w * (0.92 if fem else 1.0)
        hw = 1.12 if fem else 1.0
        # torso
        self._part("PELVIS", "hips", mlegs, lambda bm: bm_ellipsoid(bm, (0.155 * s * hw, 0.105 * s, 0.10 * s), (0, 0.004, hz + 0.035 * s)))
        self._part("ABDOMEN", "spine", mtop, lambda bm: bm_ellipsoid(bm, (0.145 * s * sw * b, 0.10 * s * b, 0.125 * s), (0, 0.0, 0.625 * H)))
        self._part("CHEST", "chest", mtop, lambda bm: (
            bm_ellipsoid(bm, (0.175 * s * sw * b, 0.112 * s * b, 0.13 * s), (0, 0.004, 0.745 * H)),
            bm_ellipsoid(bm, (0.065 * s * b,) * 3, (self.sh_x * 0.92, 0, 0.805 * H)),
            bm_ellipsoid(bm, (0.065 * s * b,) * 3, (-self.sh_x * 0.92, 0, 0.805 * H))))
        if top in ("leather", "suit", "bomber"):
            shirt_hex = sp.get("shirt", "#2B2B2B")
            mshirt = _m("shirt" + shirt_hex, lambda: fabric("MAT_SHIRT_" + shirt_hex[1:], shirt_hex))
            self._part("SHIRT_FRONT", "chest", mshirt, lambda bm: bm_box(
                bm, (0.07 * s, 0.012, 0.2 * s), (0, -0.108 * s * b, 0.73 * H), bevel=0.004))
        self._part("NECK", "neck", mskin, lambda bm: bm_limb(bm, (0, 0, 0.815 * H), (0, 0, 0.885 * H), 0.052 * s, 0.047 * s))
        # head + face
        hc, hr = self.head_c, self.head_r
        self._part("HEAD", "head", mskin, lambda bm: (
            bm_ellipsoid(bm, hr, hc, seg=28, rings=16),
            bm_ellipsoid(bm, (0.012 * s, 0.022 * s, 0.03 * s), (hr.x + hc.x - 0.002, hc.y + 0.005, hc.z)),
            bm_ellipsoid(bm, (0.012 * s, 0.022 * s, 0.03 * s), (-hr.x + hc.x + 0.002, hc.y + 0.005, hc.z)),
            bm_limb(bm, (0, hc.y - hr.y + 0.004, hc.z + 0.008 * s), (0, hc.y - hr.y - 0.016 * s, hc.z - 0.016 * s), 0.011 * s, 0.006 * s, seg=10),
            bm_ellipsoid(bm, (0.052 * s, 0.07 * s, 0.05 * s), (0, hc.y - 0.022 * s, hc.z - 0.07 * s))))
        self._part("MOUTH", "head", mlip, lambda bm: bm_box(bm, (0.034 * s, 0.006, 0.0045 * s), (0, hc.y - 0.0865 * s, hc.z - 0.046 * s), bevel=0.0015))
        for side, sx in (("L", 1), ("R", -1)):
            ex = sx * 0.032 * s
            self._part("EYE_WHITE_" + side, "head", mwhite, lambda bm, ex=ex: bm_ellipsoid(bm, (0.0125 * s, 0.009 * s, 0.009 * s), (ex, hc.y - 0.079 * s, hc.z + 0.012 * s), seg=12, rings=8))
            self._part("PUPIL_" + side, "eyes", mdark, lambda bm, ex=ex: bm_ellipsoid(bm, (0.0055 * s, 0.003 * s, 0.0055 * s), (ex, hc.y - 0.0885 * s, hc.z + 0.012 * s), seg=10, rings=6))
            self._part("BROW_" + side, "brow." + side, mhair, lambda bm, ex=ex: bm_box(bm, (0.03 * s, 0.006, 0.0055 * s), (ex, hc.y - 0.085 * s, hc.z + 0.036 * s), bevel=0.002))
        if sp.get("moustache"):
            self._part("MOUSTACHE", "head", mhair, lambda bm: bm_box(bm, (0.052 * s, 0.01, 0.009 * s), (0, hc.y - 0.091 * s, hc.z - 0.031 * s), bevel=0.003))
        style = sp["hair_style"]
        hs = 1.02 if style == "crop" else 1.07
        self._part("HAIR", "head", mhair, lambda bm: (
            bm_ellipsoid(bm, (hr.x * hs, hr.y * hs, hr.z * 0.8 * hs), (hc.x, hc.y + 0.012 * s, hc.z + 0.03 * s), seg=24, rings=12),
            *( [bm_ellipsoid(bm, (0.07 * s, 0.05 * s, 0.13 * s), (0, hc.y + 0.075 * s, hc.z - 0.07 * s))] if style == "long" else []),
            *( [bm_ellipsoid(bm, (0.04 * s,) * 3, (0, hc.y + 0.105 * s, hc.z + 0.02 * s))] if style == "bun" else [])))
        # arms
        shz = 0.815 * H
        for side, sx in (("L", 1), ("R", -1)):
            x = sx * self.sh_x
            self._part("UPPER_ARM_" + side, "upper_arm." + side, mtop, lambda bm, x=x: bm_limb(
                bm, (x, 0, shz + 0.01), (x, 0, shz - 0.186 * H - 0.01), 0.052 * s * b, 0.044 * s * b))
            self._part("FOREARM_" + side, "forearm." + side, mtop, lambda bm, x=x: bm_limb(
                bm, (x, 0, shz - 0.186 * H + 0.01), (x, 0, shz - 0.326 * H), 0.044 * s * b, 0.036 * s * b))
            self._part("HAND_" + side, "hand." + side, mskin, lambda bm, x=x, sx=sx: self._hand(bm, x, sx, shz - 0.332 * H))
        # legs
        for side, sx in (("L", 1), ("R", -1)):
            hx = sx * self.hip_x
            lb = 1.12 if sp["legs"] == "denim" else 1.0
            self._part("THIGH_" + side, "thigh." + side, mlegs, lambda bm, hx=hx: bm_limb(
                bm, (hx, 0, hz + 0.02), (hx, 0, hz - self.L / 2 - 0.01), 0.083 * s * hw * lb, 0.058 * s * lb))
            self._part("SHIN_" + side, "shin." + side, mlegs, lambda bm, hx=hx: bm_limb(
                bm, (hx, 0, hz - self.L / 2 + 0.01), (hx, 0, self.ankle + 0.005), 0.056 * s * lb, 0.045 * s * lb))
            self._part("SHOE_" + side, "foot." + side, mshoe, lambda bm, hx=hx: bm_box(
                bm, (0.1 * s, 0.27 * s, 0.085 * s), (hx, -0.075 * s, 0.0425 * s), bevel=0.025 * s, segs=3))
        # cap
        self.cap = None
        if sp.get("cap"):
            self.cap = self.attach_cap(cap_mats[sp["cap"]])

    def _hand(self, bm, x, sx, wrist_z):
        s = self.s
        bm_box(bm, (0.028 * s, 0.082 * s, 0.09 * s), (x, 0, wrist_z - 0.047 * s), bevel=0.008 * s)
        for i in range(4):
            fy = (-0.03 + i * 0.02) * s
            ln = (0.07, 0.08, 0.077, 0.062)[i] * s
            bm_limb(bm, (x, fy, wrist_z - 0.088 * s), (x, fy, wrist_z - 0.088 * s - ln), 0.0085 * s, 0.0072 * s, seg=8)
        bm_limb(bm, (x, -0.035 * s, wrist_z - 0.03 * s), (x - sx * 0.008 * s, -0.062 * s, wrist_z - 0.085 * s), 0.0095 * s, 0.0078 * s, seg=8)

    def cap_offset(self):
        """Cap pose relative to the head bone's attachment frame (used for bone-parented and world-keyed caps)."""
        hc, hr = self.head_c, self.head_r
        sc = (hr.x / 0.072)
        rest = Matrix.Translation((0, hc.y + 0.004 * self.s, hc.z + hr.z - 0.072 * self.s)) @ \
            Matrix.Rotation(radians(-6), 4, "X") @ Matrix.Diagonal((sc, sc, sc, 1.0))
        return rest

    def attach_cap(self, mats, name=None):
        ob = cap_object(name or (self.name + "_CAP"), self.cap_coll, override=mats)
        self._parent(ob, "head")
        ob.matrix_basis = self.cap_offset()
        return ob

    # world-space helpers (valid after depsgraph evaluation)
    def head_world(self):
        return self.arm.matrix_world @ self.arm.pose.bones["head"].matrix

    def hand_tip_world(self, side):
        pb = self.arm.pose.bones["hand." + side]
        return self.arm.matrix_world @ pb.tail

    def foot_world(self, side):
        pb = self.arm.pose.bones["foot." + side]
        return self.arm.matrix_world @ pb.head


def _darken(hexcol, k):
    h = hexcol.lstrip("#")
    return "#%02X%02X%02X" % tuple(int(int(h[i:i + 2], 16) * k) for i in (0, 2, 4))
