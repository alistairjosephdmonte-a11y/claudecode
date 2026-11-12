"""Proxy human: armature with IK arms/legs, rigid clay parts parented to bones, IK target empties.
Built standing at the origin facing +Y; the armature object is then placed in the room."""
import math

import bpy
from mathutils import Matrix, Quaternion, Vector

import mats as M


def _bones(H):
    s = lambda *v: Vector(v) * H  # noqa: E731
    B = {"root": (s(0, 0, 0), s(0, -0.08, 0), None),
         "hips": (s(0, 0, 0.53), s(0, 0, 0.60), "root"),
         "spine": (s(0, 0, 0.60), s(0, 0, 0.72), "hips"),
         "chest": (s(0, 0, 0.72), s(0, 0, 0.82), "spine"),
         "neck": (s(0, 0, 0.82), s(0, 0.005, 0.87), "chest"),
         "head": (s(0, 0.005, 0.87), s(0, 0.005, 1.0), "neck"),
         "jaw": (s(0, 0.02, 0.90), s(0, 0.06, 0.885), "head"),
         "shirt_hem": (s(0, 0, 0.62), s(0, 0, 0.54), "spine")}
    for side, k in (("L", -1), ("R", 1)):     # character faces +Y, so its right side is +X
        B[f"upper_arm.{side}"] = (s(k * 0.125, 0, 0.805), s(k * 0.135, -0.015, 0.635), "chest")
        B[f"forearm.{side}"] = (s(k * 0.135, -0.015, 0.635), s(k * 0.14, 0.0, 0.485), f"upper_arm.{side}")
        B[f"hand.{side}"] = (s(k * 0.14, 0.0, 0.485), s(k * 0.14, 0.0, 0.43), f"forearm.{side}")
        B[f"fingers.{side}"] = (s(k * 0.14, 0.0, 0.43), s(k * 0.14, 0.0, 0.39), f"hand.{side}")
        B[f"thumb.{side}"] = (s(k * 0.14, 0.012, 0.47), s(k * 0.14, 0.03, 0.44), f"hand.{side}")
        B[f"thigh.{side}"] = (s(k * 0.055, 0, 0.525), s(k * 0.057, 0.012, 0.28), "hips")
        B[f"shin.{side}"] = (s(k * 0.057, 0.012, 0.28), s(k * 0.057, 0, 0.045), f"thigh.{side}")
        B[f"foot.{side}"] = (s(k * 0.057, 0, 0.045), s(k * 0.057, 0.13, 0.015), f"shin.{side}")
    return B


def _part(name, kind, size, mat, coll, loc=(0, 0, 0), rot=(0, 0, 0), bevel=0.0, seg=12):
    if kind == "box":
        bpy.ops.mesh.primitive_cube_add(size=1)
    elif kind == "sphere":
        bpy.ops.mesh.primitive_uv_sphere_add(segments=seg, ring_count=max(6, seg // 2), radius=0.5)
    elif kind == "cyl":
        bpy.ops.mesh.primitive_cylinder_add(vertices=seg, radius=0.5, depth=1)
    elif kind == "torus":
        bpy.ops.mesh.primitive_torus_add(major_radius=0.5, minor_radius=size[2], major_segments=20, minor_segments=6)
        size = (size[0], size[1], 1.0)
    o = bpy.context.active_object
    o.name = name
    o.dimensions = size if kind != "torus" else o.dimensions
    if kind == "torus":
        o.scale = (size[0], size[1], 1.0)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    o.location, o.rotation_euler = Vector(loc), rot
    if bevel:
        m = o.modifiers.new("bevel", "BEVEL")
        m.width, m.segments = bevel, 2
    if kind in ("sphere", "cyl", "torus") or bevel:
        bpy.ops.object.shade_smooth()
    o.data.materials.append(mat)
    for c in o.users_collection:
        c.objects.unlink(o)
    coll.objects.link(o)
    return o


def _attach(o, arm, bone):
    b = arm.data.bones[bone]
    pw = arm.matrix_world @ b.matrix_local @ Matrix.Translation((0, b.length, 0))
    w = o.matrix_world.copy()
    o.parent, o.parent_type, o.parent_bone = arm, "BONE", bone
    o.matrix_parent_inverse = pw.inverted()
    o.matrix_basis = w


def _empty(name, coll, size=0.05, shape="SPHERE"):
    e = bpy.data.objects.new(name, None)
    e.empty_display_type, e.empty_display_size = shape, size
    coll.objects.link(e)
    return e


def build(cid, H, look, coll):
    """look: dict(shirt, skin, hair, pants, shoe, curls(bool), extras(list of callables(add, H)))"""
    ad = bpy.data.armatures.new(cid + "_RIG")
    arm = bpy.data.objects.new(cid + "_RIG", ad)
    coll.objects.link(arm)
    bpy.context.view_layer.objects.active = arm
    for o in bpy.context.selected_objects:
        o.select_set(False)
    arm.select_set(True)
    bpy.ops.object.mode_set(mode="EDIT")
    for n, (h, t, p) in _bones(H).items():
        eb = ad.edit_bones.new(n)
        eb.head, eb.tail, eb.roll = h, t, 0.0
        if p:
            eb.parent = ad.edit_bones[p]
            eb.use_connect = False
    bpy.ops.object.mode_set(mode="OBJECT")
    ad.display_type = "STICK"
    for pb in arm.pose.bones:
        pb.rotation_mode = "QUATERNION"

    s = H
    add = lambda n, kind, size, mat, bone, loc, rot=(0, 0, 0), bevel=0.0, seg=12: _attach(  # noqa: E731
        _part(f"{cid}_{n}", kind, size, mat, coll, loc, rot, bevel, seg), arm, bone)
    sk, sh, pa, hr, sho = look["skin"], look["shirt"], look["pants"], look["hair"], look["shoe"]
    add("pelvis", "box", (0.20 * s, 0.12 * s, 0.10 * s), pa, "hips", (0, 0, 0.555 * s), bevel=0.03 * s)
    add("torso_low", "box", (0.19 * s, 0.115 * s, 0.13 * s), sh, "spine", (0, 0, 0.665 * s), bevel=0.035 * s)
    add("torso_up", "box", (0.235 * s, 0.13 * s, 0.13 * s), sh, "chest", (0, 0, 0.765 * s), bevel=0.04 * s)
    add("shirt_hem", "box", (0.20 * s, 0.125 * s, 0.035 * s), sh, "shirt_hem", (0, 0, 0.585 * s), bevel=0.012 * s)
    add("neck", "cyl", (0.055 * s, 0.055 * s, 0.07 * s), sk, "neck", (0, 0.004 * s, 0.84 * s))
    add("head", "sphere", (0.095 * s, 0.115 * s, 0.13 * s), sk, "head", (0, 0.008 * s, 0.93 * s), seg=16)
    add("nose", "box", (0.016 * s, 0.03 * s, 0.03 * s), sk, "head", (0, 0.068 * s, 0.925 * s), bevel=0.005 * s)
    for k in (-1, 1):
        add(f"eye{'L' if k < 0 else 'R'}", "sphere", (0.016 * s, 0.01 * s, 0.016 * s), M.get("eye"), "head",
            (k * 0.022 * s, 0.062 * s, 0.945 * s), seg=8)
        add(f"brow{'L' if k < 0 else 'R'}", "box", (0.028 * s, 0.008 * s, 0.006 * s), hr, "head",
            (k * 0.023 * s, 0.064 * s, 0.959 * s))
    add("mouth", "box", (0.034 * s, 0.01 * s, 0.006 * s), M.get("mouth"), "jaw", (0, 0.06 * s, 0.897 * s))
    add("chin", "sphere", (0.06 * s, 0.05 * s, 0.035 * s), sk, "jaw", (0, 0.04 * s, 0.888 * s), seg=10)
    for side, k in (("L", -1), ("R", 1)):
        add(f"sleeve.{side}", "cyl", (0.072 * s, 0.072 * s, 0.09 * s), sh, f"upper_arm.{side}", (k * 0.128 * s, -0.004 * s, 0.765 * s))
        add(f"upper_arm.{side}", "cyl", (0.052 * s, 0.052 * s, 0.17 * s), sk, f"upper_arm.{side}", (k * 0.13 * s, -0.008 * s, 0.72 * s))
        add(f"forearm.{side}", "cyl", (0.045 * s, 0.045 * s, 0.155 * s), sk, f"forearm.{side}", (k * 0.137 * s, -0.008 * s, 0.56 * s))
        add(f"palm.{side}", "box", (0.022 * s, 0.05 * s, 0.06 * s), sk, f"hand.{side}", (k * 0.14 * s, 0.0, 0.457 * s), bevel=0.006 * s)
        add(f"fingers.{side}", "box", (0.018 * s, 0.046 * s, 0.045 * s), sk, f"fingers.{side}", (k * 0.14 * s, 0.0, 0.41 * s), bevel=0.006 * s)
        add(f"thumb.{side}", "box", (0.016 * s, 0.016 * s, 0.035 * s), sk, f"thumb.{side}", (k * 0.142 * s, 0.022 * s, 0.455 * s),
            rot=(-0.6, 0, 0), bevel=0.005 * s)
        add(f"thigh.{side}", "cyl", (0.085 * s, 0.085 * s, 0.25 * s), pa, f"thigh.{side}", (k * 0.056 * s, 0.006 * s, 0.40 * s))
        add(f"shin.{side}", "cyl", (0.068 * s, 0.068 * s, 0.24 * s), pa, f"shin.{side}", (k * 0.057 * s, 0.006 * s, 0.165 * s))
        add(f"shoe.{side}", "box", (0.06 * s, 0.155 * s, 0.045 * s), sho, f"foot.{side}", (k * 0.057 * s, 0.05 * s, 0.024 * s), bevel=0.012 * s)
    if look.get("curls"):
        import random
        rnd = random.Random(cid)
        for i in range(46):
            th, ph = rnd.uniform(0, 2 * math.pi), rnd.uniform(0.0, 1.45)
            if math.sin(th) > 0.55 and ph > 0.9:          # keep the face clear
                continue
            d = Vector((math.sin(ph) * math.cos(th) * 0.052, math.sin(ph) * math.sin(th) * 0.064 - 0.006, math.cos(ph) * 0.07)) * s
            r = rnd.uniform(0.026, 0.036) * s
            add(f"curl{i:02d}", "sphere", (r, r, r), hr, "head", Vector((0, 0.004 * s, 0.94 * s)) + d, seg=8)
    else:
        add("hair_cap", "sphere", (0.102 * s, 0.122 * s, 0.085 * s), hr, "head", (0, -0.004 * s, 0.968 * s), seg=16)
        add("hair_back", "sphere", (0.098 * s, 0.07 * s, 0.09 * s), hr, "head", (0, -0.03 * s, 0.94 * s), seg=12)
    for fn in look.get("extras", []):
        fn(add, s)

    # IK + control empties (world space; keyed directly by the animation)
    tg = {}
    for side, k in (("L", -1), ("R", 1)):
        for limb, tip, chain, pole_off in (("hand", f"forearm.{side}", 2, (k * 0.25, -0.45, 0.0)),
                                           ("foot", f"shin.{side}", 2, (k * 0.05, 0.6, 0.0))):
            t = _empty(f"{cid}_IK_{limb}.{side}", coll, 0.06, "CUBE")
            p = _empty(f"{cid}_POLE_{limb}.{side}", coll, 0.04, "SPHERE")
            pb = arm.pose.bones[tip]
            c = pb.constraints.new("IK")
            c.target, c.pole_target, c.chain_count = t, p, chain
            c.use_tail = True
            end = arm.pose.bones[f"{limb}.{side}"]
            cr = end.constraints.new("COPY_ROTATION")
            cr.target = t
            tg[f"{limb}.{side}"], tg[f"pole_{limb}.{side}"] = t, p
            tg[f"_pole_off_{limb}.{side}"] = Vector(pole_off) * s
    look_t = _empty(f"{cid}_LOOK", coll, 0.08, "SPHERE")
    tg["look"] = look_t
    return arm, tg


def bone_world(arm, name, head=True):
    pb = arm.pose.bones[name]
    return arm.matrix_world @ (pb.head if head else pb.tail)


def set_rot(pb, axis, angle):
    """Rotate a pose bone by `angle` about `axis` given in armature rest space."""
    Bm = pb.bone.matrix_local.to_3x3()
    q = Quaternion(Vector(axis).normalized(), angle).to_matrix()
    pb.rotation_quaternion = (Bm.inverted() @ q @ Bm).to_quaternion()
