"""MOO_01 rig: one pose skeleton (empties) drives
  - the SIDE artwork (cutout planes in MOO's local X-Z plane, legs on two-bone pivots),
  - the REAR artwork (planes in the local Y-Z plane, placed at the real hip/shoulder depth),
  - the THREE-QUARTER head artwork (separate head rig, oriented per shot; never continuously rotated),
  - a low-poly 3D PROXY (invisible to camera) that casts the contact shadows and blocks light.
Artwork planes are emission-only (palette and linework unchanged by scene lighting), visible to camera and to
glossy rays (so the puddle reflects the actual drawing), and never cast shadows themselves."""
import json
import math
import os

import bmesh
import bpy

import config as C

S = C.MOO_SCALE
META = json.load(open(os.path.join(C.P["meta"], "moo_parts.json")))["parts"]
SIDE_PIV = {"torso": (0.0, 0.56), "neck": (0.33, 0.64)}
REAR_PIV = {"torso": (0.0, 0.56), "neck": (0.0, 0.74)}
LEG_DEPTH = {"near": -0.11, "far": 0.11}            # local Y of near (camera side, MOO's right) / far legs
LEG_U = {"rear": -0.27, "front": 0.24}


def coll(name):
    c = bpy.data.collections.get(name) or bpy.data.collections.new(name)
    if c.name not in bpy.context.scene.collection.children:
        bpy.context.scene.collection.children.link(c)
    return c


def empty(name, c, parent=None, loc=(0, 0, 0)):
    o = bpy.data.objects.new(name, None)
    o.empty_display_size = 0.05
    c.objects.link(o)
    o.parent = parent
    o.location = loc
    return o


def art_material(key, root):
    m = bpy.data.materials.get(f"MOO_{key}")
    if m:
        return m
    v = META[key]
    m = bpy.data.materials.new(f"MOO_{key}")
    m.use_nodes = True
    nt = m.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    mix = nt.nodes.new("ShaderNodeMixShader")
    tr = nt.nodes.new("ShaderNodeBsdfTransparent")
    em = nt.nodes.new("ShaderNodeEmission")
    tx = nt.nodes.new("ShaderNodeTexImage")
    tx.image = bpy.data.images.load(os.path.join(C.ROOT, v["file"]), check_existing=True)
    tx.interpolation = "Cubic"
    tx.extension = "CLIP"
    nt.links.new(tx.outputs["Color"], em.inputs["Color"])
    nt.links.new(tx.outputs["Alpha"], mix.inputs[0])
    nt.links.new(tr.outputs[0], mix.inputs[1])
    nt.links.new(em.outputs[0], mix.inputs[2])
    nt.links.new(mix.outputs[0], out.inputs["Surface"])
    # per-shot exposure match (MOO_ROOT["exposure"]), a simple driver: no scripts needed at render time
    d = em.inputs["Strength"].driver_add("default_value").driver
    d.type = "SCRIPTED"
    var = d.variables.new()
    var.name = "e"
    var.targets[0].id = root
    var.targets[0].data_path = '["exposure"]'
    d.expression = "e"
    return m


def plane(name, c, w, h, mat, axes="XZ"):
    """Quad centred on its origin, in the local X-Z plane (side) or Y-Z plane facing -X (rear) or X-Z (q3 rig)."""
    me = bpy.data.meshes.new(name)
    if axes == "XZ":
        vs = [(-w / 2, 0, -h / 2), (w / 2, 0, -h / 2), (w / 2, 0, h / 2), (-w / 2, 0, h / 2)]
    else:                                               # YZ facing -X: screen-right = -Y
        vs = [(0, w / 2, -h / 2), (0, -w / 2, -h / 2), (0, -w / 2, h / 2), (0, w / 2, h / 2)]
    me.from_pydata(vs, [], [(0, 1, 2, 3)])
    uv = me.uv_layers.new()
    for li, uvv in zip(range(4), [(0, 0), (1, 0), (1, 1), (0, 1)]):
        uv.data[li].uv = uvv
    o = bpy.data.objects.new(name, me)
    c.objects.link(o)
    o.data.materials.append(mat)
    o.visible_shadow = False
    o.visible_diffuse = False
    o.visible_transmission = False
    o.visible_volume_scatter = False
    o.visible_glossy = True
    return o


def build_side(root, c):
    """Pivot hierarchy in design coordinates (scaled by S on the view root)."""
    vr = empty("SIDE_ROOT", c, root)
    vr.scale = (S, S, S)
    piv = {"root": vr}

    def P(name, uv, parent, y=0.0):
        pu, pv = piv_uv[parent]
        e = empty(f"SIDE_{name}_PIV", c, piv[parent], (uv[0] - pu, y, uv[1] - pv))
        piv[name], piv_uv[name] = e, uv
        return e

    piv_uv = {"root": (0.0, 0.0)}
    P("torso", SIDE_PIV["torso"], "root")
    P("neck", SIDE_PIV["neck"], "torso", -0.0)
    P("ear", (0.47, 0.90), "neck")
    P("tail", (-0.40, 0.70), "torso")
    for which in ("rear", "front"):
        for side in ("near", "far"):
            k = META[f"side_leg_{which}_{side}_upper"]
            P(f"leg_{which}_{side}_upper", k["pivot_m"], "torso", LEG_DEPTH[side] / S)
            kl = META[f"side_leg_{which}_{side}_lower"]
            P(f"leg_{which}_{side}_lower", kl["pivot_m"], f"leg_{which}_{side}_upper")
    P("eye", META["side_eye"]["pivot_m"], "neck")
    P("lid", META["side_lid"]["pivot_m"], "neck")
    parts = {}
    owner = {"torso": "torso", "head": "neck", "horn": "neck", "ear": "ear", "ear_far": "ear", "tail": "tail", "eye": "eye", "lid": "lid"}
    for key, v in META.items():
        if v["view"] != "side":
            continue
        part = v["part"]
        pv = owner.get(part) or ("neck" if part.startswith("mouth_") else part)
        if part.startswith("leg_"):
            pv = part
        pu, pvv = piv_uv[pv]
        cx, cy = v["center_m"]
        mat = art_material(key, root)
        o = plane(f"SIDE_{part}", c, v["size_m"][0], v["size_m"][1], mat, "XZ")
        o.parent = piv[pv]
        depth = -v["z"] * 0.5 if not part.startswith("leg_") else -0.004 * (1 if "lower" in part else 0)
        if part == "ear_far":
            depth = 0.06 / S
        if part == "tail":
            depth = 0.02 / S
        o.location = (cx - pu, depth, cy - pvv)
        parts[part] = o
    return vr, piv, parts


def build_rear(root, c):
    """Rear artwork at its real depth: rump plane nearest the camera, rear legs at the hips, front legs and head beyond."""
    vr = empty("REAR_ROOT", c, root)
    vr.scale = (S, S, S)
    tv = REAR_PIV["torso"][1]
    piv = {"root": vr}
    piv["torso"] = empty("REAR_torso_PIV", c, vr, (0, 0, tv))
    piv["neck"] = empty("REAR_neck_PIV", c, piv["torso"], (0.06, 0, REAR_PIV["neck"][1] - tv))    # just behind the rump plane
    piv["tail"] = empty("REAR_tail_PIV", c, piv["torso"], (-0.43, 0, 0.74 - tv))
    legx = {"leg_rear_l": -0.27, "leg_rear_r": -0.27, "leg_front_l": 0.24, "leg_front_r": 0.24}
    parts = {}
    for key, v in META.items():
        if v["view"] != "rear":
            continue
        part, (cx, cy), (pu, pv) = v["part"], v["center_m"], v["pivot_m"]
        mat = art_material(key, root)
        o = plane(f"REAR_{part}", c, v["size_m"][0], v["size_m"][1], mat, "YZ")
        if part.startswith("leg_"):
            e = empty(f"REAR_{part}_PIV", c, piv["torso"], (legx[part], -pu, pv - tv))
            piv[part] = e
            o.parent, o.location = e, (0, -(cx - pu), cy - pv)
        elif part.startswith("ear_"):
            e = empty(f"REAR_{part}_PIV", c, piv["neck"], (0.006, -pu, pv - REAR_PIV["neck"][1]))
            piv[part] = e
            o.parent, o.location = e, (0, -(cx - pu), cy - pv)
        elif part in ("head", "horn_l", "horn_r"):
            o.parent, o.location = piv["neck"], (0.0 if part == "head" else 0.01, -cx, cy - REAR_PIV["neck"][1])
        elif part == "tail":
            o.parent, o.location = piv["tail"], (0, -cx, cy - 0.74)
        else:
            o.parent, o.location = piv["torso"], (-0.36, -cx, cy - tv)
        parts[part] = o
    return vr, piv, parts


def build_q3(root, c):
    """Head-and-shoulders rig for the 85 mm close-up; its root is placed and aimed at the camera per shot."""
    vr = empty("Q3_ROOT", c, None)
    vr["view"] = "q3"
    piv, piv_uv = {"root": vr}, {"root": (0.0, 0.0)}

    def P(name, uv, parent):
        pu, pv = piv_uv[parent]
        e = empty(f"Q3_{name}_PIV", c, piv[parent], (uv[0] - pu, 0, uv[1] - pv))
        piv[name], piv_uv[name] = e, uv
        return e

    P("neck", (0.0, -0.05), "root")
    P("head", (0.0, 0.0), "neck")
    for nm in ("ear_far", "ear_near", "eye_far", "eye_near", "lid_far", "lid_near"):
        P(nm, META[f"q3_{nm}"]["pivot_m"], "head")
    parts = {}
    for key, v in META.items():
        if v["view"] != "q3" or key.startswith("q3rim_"):
            continue
        part = v["part"]
        parent = part if part in piv else ("neck" if part == "neck" else "head")
        pu, pv = piv_uv[parent]
        cx, cy = v["center_m"]
        o = plane(f"Q3_{part}", c, v["size_m"][0], v["size_m"][1], art_material(key, root), "XZ")
        o.parent = piv[parent]
        o.location = (cx - pu, -v["z"] * 0.4, cy - pv)
        parts[part] = o
        rim = f"q3rim_{part}"
        if rim in META:                                  # warm backlight catching the illustrated silhouette
            r = META[rim]
            ro = plane(f"Q3_RIM_{part}", c, r["size_m"][0], r["size_m"][1], art_material(rim, root), "XZ")
            ro.parent = piv[parent]
            ro.location = (r["center_m"][0] - pu, -v["z"] * 0.4 + 0.004, r["center_m"][1] - pv)
            parts[f"rim_{part}"] = ro
    return vr, piv, parts


def _prim(name, c, kind, size, mat):
    me = bpy.data.meshes.new(name)
    bm = bmesh.new()
    if kind == "sphere":
        bmesh.ops.create_uvsphere(bm, u_segments=16, v_segments=10, radius=0.5)
    else:
        bmesh.ops.create_cone(bm, segments=10, radius1=0.5, radius2=0.5, depth=1.0, cap_ends=True)
    for v in bm.verts:
        v.co.x *= size[0]
        v.co.y *= size[1]
        v.co.z *= size[2]
    bm.to_mesh(me)
    bm.free()
    o = bpy.data.objects.new(name, me)
    c.objects.link(o)
    o.data.materials.append(mat)
    o.visible_camera = False
    o.visible_glossy = False
    o.visible_diffuse = False
    o.visible_transmission = False
    o.visible_shadow = True
    return o


def build_proxy(piv, c):
    """3D stand-in (design units, inherits S): torso, neck, head, legs, tail -> correct shadows and occlusion of light."""
    m = bpy.data.materials.new("M_MooProxy")
    m.diffuse_color = (0.8, 0.8, 0.8, 1)
    out = {}
    t = _prim("PROXY_torso", c, "sphere", (0.80, 0.30, 0.38), m)
    t.parent = piv["torso"]
    n = _prim("PROXY_neck", c, "cyl", (0.20, 0.18, 0.28), m)
    n.parent = piv["neck"]
    n.location = (-0.06, 0, -0.04)
    n.rotation_euler.y = math.radians(55)
    h = _prim("PROXY_head", c, "sphere", (0.36, 0.24, 0.30), m)
    h.parent = piv["neck"]
    h.location = (0.22, 0, 0.12)
    mz = _prim("PROXY_muzzle", c, "sphere", (0.17, 0.17, 0.15), m)
    mz.parent = piv["neck"]
    mz.location = (0.37, 0, 0.065)
    for which in ("rear", "front"):
        for side in ("near", "far"):
            u = _prim(f"PROXY_leg_{which}_{side}_u", c, "cyl", (0.10, 0.10, 0.22), m)
            u.parent = piv[f"leg_{which}_{side}_upper"]
            u.location = (0, 0, -0.11)
            lo = _prim(f"PROXY_leg_{which}_{side}_l", c, "cyl", (0.075, 0.075, 0.225), m)
            lo.parent = piv[f"leg_{which}_{side}_lower"]
            lo.location = (0, 0, -0.112)
    tl = _prim("PROXY_tail", c, "cyl", (0.03, 0.03, 0.28), m)
    tl.parent = piv["tail"]
    tl.location = (-0.04, 0, -0.14)
    tl.rotation_euler.y = math.radians(-16)
    return out


def build():
    c_rig = coll("MOO_RIG")
    root = empty("MOO_ROOT", c_rig)
    root["exposure"] = 1.0
    root.keyframe_insert('["exposure"]', frame=1)
    side = build_side(root, coll("MOO_SIDE_ART"))
    rear = build_rear(root, coll("MOO_REAR_ART"))
    q3 = build_q3(root, coll("MOO_Q3_ART"))
    build_proxy(side[1], coll("MOO_PROXY"))
    hooves = {}
    for which in ("rear", "front"):
        for s in ("near", "far"):
            hooves[f"{which}_{s}"] = empty(f"HOOF_{which}_{s}", c_rig)
    return dict(root=root, side=side, rear=rear, q3=q3, hooves=hooves)
