"""Flat 2D cel-animation intrusions built as thin real geometry: traffic cone, satellite dish, elephant.

All use two-tone flat cel materials + inverted-hull ink outlines, cast real shadows and occlude/are occluded
by scene depth. They are authored in the X/Z plane and rotated into place.
"""
from math import pi, radians, sin, cos
import bpy
import bmesh
from mathutils import Vector, Matrix

from common import (bm_flat_poly, ellipse_pts, stroke_pts, mesh_from_bm, new_object, cel, ink_outline,
                    add_outline, CAP_BLUE_PLACEHOLDER, heading_for)
from cap_asset import cap_object


def _flat(name, coll, polys, mat, thickness=0.03, y0=0.0, outline=0.012, yaw90=False):
    bm = bmesh.new()
    for pts in polys:
        bm_flat_poly(bm, pts, thickness, y0)
    if yaw90:
        rot = Matrix.Rotation(pi / 2, 3, "Z")
        for v in bm.verts:
            v.co = rot @ v.co
    ob = new_object(name, mesh_from_bm(name, bm, smooth_shade=False), coll, [mat])
    if outline:
        add_outline(ob, ink_outline(), outline)
    ob["style"] = "flat cel 2D intrusion (thin real geometry)"
    return ob


def build_cone(coll):
    """Oversized flat traffic cone. Local origin = contact point on the wearer's head. Plane = char Y/Z."""
    orange = cel("MAT_CEL_CONE_ORANGE", "#FF7A1A", "#B8420E")
    white = cel("MAT_CEL_CONE_STRIPE", "#F2EEE4", "#B5AFA2")
    base = cel("MAT_CEL_CONE_BASE", "#E2621A", "#93360C")
    body = [(-0.2, 0.05), (0.2, 0.05), (0.04, 0.6), (0.02, 0.625), (-0.02, 0.625), (-0.04, 0.6)]
    cone = _flat("CARTOON_TRAFFIC_CONE", coll, [body], orange, 0.03, yaw90=True)
    _flat("CARTOON_TRAFFIC_CONE_BASE", coll, [[(-0.27, -0.01), (0.27, -0.01), (0.27, 0.055), (-0.27, 0.055)]], base, 0.036, yaw90=True).parent = cone

    def band(z0, z1):
        def wx(z):
            return 0.2 + (0.04 - 0.2) * (z - 0.05) / 0.55
        return [(-wx(z0), z0), (wx(z0), z0), (wx(z1), z1), (-wx(z1), z1)]

    s1 = _flat("CARTOON_TRAFFIC_CONE_STRIPE_1", coll, [band(0.22, 0.3)], white, 0.036, outline=0.0, yaw90=True)
    s2 = _flat("CARTOON_TRAFFIC_CONE_STRIPE_2", coll, [band(0.4, 0.46)], white, 0.036, outline=0.0, yaw90=True)
    s1.parent = cone
    s2.parent = cone
    return cone


def build_dish(coll):
    """Giant flat satellite dish hat, drawn in cartoon 3/4 view. Bows under its weight (animated Simple Deform)."""
    grey = cel("MAT_CEL_DISH_WHITE", "#E4E6E8", "#A3A9B1")
    rim = cel("MAT_CEL_DISH_INNER", "#C3C8CF", "#8C939C")
    dark = cel("MAT_CEL_DISH_ARM", "#5B6068", "#33363C")
    pole = [(-0.03, 0.0), (0.03, 0.0), (0.03, 0.16), (-0.03, 0.16)]
    bracket = [(-0.16, 0.12), (0.16, 0.12), (0.1, 0.2), (-0.1, 0.2)]
    face = ellipse_pts(0.0, 0.62, 0.78, 0.46, 56)
    inner = ellipse_pts(0.03, 0.64, 0.6, 0.33, 48)
    hub = ellipse_pts(0.04, 0.64, 0.07, 0.05, 16)
    arm = stroke_pts([(0.04, 0.64), (-0.12, 0.92), (-0.26, 1.12)], 0.045, 0.03)
    lnb = [(-0.36, 1.08), (-0.18, 1.08), (-0.18, 1.22), (-0.36, 1.22)]
    dish = _flat("CARTOON_SATELLITE_DISH", coll, [face], grey, 0.03, yaw90=True, outline=0.014)
    dish["sag_note"] = "SimpleDeform BEND animated: bows under its own absurd weight"
    ring = _flat("CARTOON_SATELLITE_DISH_INNER", coll, [inner], rim, 0.036, outline=0.008, yaw90=True)
    ring.parent = dish
    parts = _flat("CARTOON_SATELLITE_DISH_ARM", coll, [pole, bracket, hub, arm, lnb], dark, 0.044, yaw90=True)
    parts.parent = dish
    for ob in (dish, ring, parts):
        bend = ob.modifiers.new("WEIGHT_SAG", "SIMPLE_DEFORM")
        bend.deform_method = "BEND"
        bend.deform_axis = "X"
        bend.angle = radians(-12)
        if ob is not dish:
            bend.origin = dish
        ob.modifiers.move(len(ob.modifiers) - 1, 0)
    return dish


def build_elephant(coll, cap_mats_cel):
    """Large flat hand-drawn-style elephant standing at the bar. Origin at ground between its feet."""
    body_c = cel("MAT_CEL_ELEPHANT_GREY", "#9AA3AD", "#66707C")
    far_c = cel("MAT_CEL_ELEPHANT_GREY_FAR", "#7D8792", "#545D68")
    ear_c = cel("MAT_CEL_ELEPHANT_EAR", "#B4BCC5", "#7A8591")
    black = cel("MAT_CEL_INK_FILL", "#121214", "#121214", 1.0)
    tusk = cel("MAT_CEL_TUSK", "#F3EEDF", "#BDB6A2")
    root = bpy.data.objects.new("CARTOON_ELEPHANT_01", None)
    coll.objects.link(root)
    root.empty_display_type = "PLAIN_AXES"
    root["note"] = "Flat cel elephant. Feet at z=0 for contact shadow; partly occluded by BAR_STOOL_FOREGROUND."

    def leg(x, w=0.34):
        return [(x - w / 2, 0.0), (x + w / 2, 0.0), (x + w / 2 - 0.02, 1.05), (x - w / 2 + 0.02, 1.05)]

    parts = [
        ("FAR_LEGS", [leg(-0.55), leg(0.65)], far_c, 0.04),
        ("BODY", [ellipse_pts(0.1, 1.45, 1.2, 0.78, 48)], body_c, 0.0),
        ("TAIL", [stroke_pts([(1.25, 1.55), (1.42, 1.3), (1.45, 1.05)], 0.06, 0.03)], body_c, 0.01),
        ("HEAD", [ellipse_pts(-1.15, 1.9, 0.55, 0.52, 40)], body_c, -0.02),
        ("TRUNK", [stroke_pts([(-1.5, 1.75), (-1.75, 1.35), (-1.82, 0.85), (-1.72, 0.55), (-1.6, 0.5)], 0.3, 0.12)], body_c, -0.025),
        ("NEAR_LEGS", [leg(-0.85), leg(0.35)], body_c, -0.04),
        ("EAR", [ellipse_pts(-0.8, 1.85, 0.4, 0.52, 36)], ear_c, -0.06),
        ("TUSK", [stroke_pts([(-1.45, 1.5), (-1.62, 1.32), (-1.75, 1.3)], 0.07, 0.03)], tusk, -0.07),
        ("EYE", [ellipse_pts(-1.38, 2.0, 0.045, 0.06, 16)], black, -0.075),
    ]
    obs = {}
    for nm, polys, mat, y in parts:
        ob = _flat("CARTOON_ELEPHANT_01_" + nm, coll, polys, mat, 0.035, y0=y, outline=0.0 if nm == "EYE" else 0.016)
        ob.parent = root
        obs[nm] = ob
    # pivot the ear at its root so it can flap
    ear = obs["EAR"]
    ear.data.transform(Matrix.Translation((0.75, 0, -2.2)))
    ear.location = (-0.75, 0, 2.2)
    cap = cap_object("CARTOON_ELEPHANT_01_CAP", coll, override=cap_mats_cel, scale=6.2)
    mod = cap.modifiers.new("INK_OUTLINE", "SOLIDIFY")
    mod.thickness = 0.0035
    mod.offset = 1.0
    mod.use_flip_normals = True
    mod.use_rim = False
    mod.material_offset = 5
    cap.parent = root
    cap.location = (-1.12, -0.02, 2.33)
    cap.rotation_euler = (radians(-4), 0, radians(-90))
    obs["CAP"] = cap
    return root, obs


def cel_cap_materials():
    from cap_asset import SLOT_TWILL, SLOT_THREAD, SLOT_BUTTON, SLOT_BUCKLE, SLOT_INNER, SLOT_SPARE
    blue = cel("MAT_CEL_CAP_BLUE", CAP_BLUE_PLACEHOLDER, "#13306A")
    thread = cel("MAT_CEL_CAP_THREAD", "#163877", "#0D2149")
    buckle = cel("MAT_CEL_CAP_BUCKLE", "#A7ABB1", "#6A6F76")
    inner = cel("MAT_CEL_CAP_INNER", "#0A0F1E", "#0A0F1E")
    return {SLOT_TWILL: blue, SLOT_THREAD: thread, SLOT_BUTTON: blue, SLOT_BUCKLE: buckle, SLOT_INNER: inner,
            SLOT_SPARE: ink_outline()}
