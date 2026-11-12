"""Performance, props, lights and cameras. Every control is a function of the frame, keyed on every frame (0-299).
Car-interior controls are in CAR_01_BODY-local coordinates."""
import json
import math
import os

import bpy
from mathutils import Matrix, Quaternion, Vector

import config as C
import rig

V = Vector
FR = range(C.F0, C.F1 + 1)
K, B, Z, T = C.CAR, C.BAG, C.ZIP, C.TAG
SYNC = json.load(open(os.path.join(C.P["meta"], "lipsync.json")))


def smooth(t):
    t = min(1.0, max(0.0, t))
    return t * t * (3 - 2 * t)


def seg(f, keys):
    if f <= keys[0][0]:
        return keys[0][1]
    for (f0, a), (f1, b) in zip(keys, keys[1:]):
        if f <= f1:
            t = smooth((f - f0) / (f1 - f0)) if f1 > f0 else 1.0
            return a.slerp(b, t) if isinstance(a, Quaternion) else a + (b - a) * t
    return keys[-1][1]


def frame_m(pos, xax, yax):
    x = V(xax).normalized()
    y = (V(yax) - x * V(yax).dot(x)).normalized()
    m = Matrix((x, y, x.cross(y))).transposed().to_4x4()
    m.translation = V(pos)
    return m


def key_m(o, m, f):
    o.matrix_basis = m
    o.rotation_mode = "QUATERNION"
    o.rotation_quaternion = m.to_quaternion()
    o.keyframe_insert("location", frame=f)
    o.keyframe_insert("rotation_quaternion", frame=f)


# ------------------------------------------------------------------ car motion (world)
def car_y(f):
    a, b = K["brake_f"]
    if f >= b:
        return K["stop_y"]
    T_ = (b - a) / C.FPS
    t = (f - a) / C.FPS
    d = K["stop_y"] - K["brake_start_y"]
    v0 = 2 * d / T_
    return K["brake_start_y"] + v0 * t - v0 / T_ * t * t / 2


def body_pitch_z(f):
    """Nose dive while braking, rebound and damped settle after the stop."""
    a, b = K["brake_f"]
    if f < b:
        k = smooth((f - a) / 4)
        return -0.032 * k, -0.018 * k
    t = (f - b) / C.FPS
    osc = math.cos(2 * math.pi * t / 0.62) * math.exp(-t / 0.22)
    return -0.032 * osc, -0.018 * osc


# ------------------------------------------------------------------ bag (body-local)
BAG_REST = V((B["x"], B["y"], B["z"]))


def bag_lift(f):
    return seg(f, [(63, 0.0), (75, 0.08), (80, 0.08), (88, -0.006), (91, 0.002), (94, 0.0)])


def bag_m(f):
    lift = bag_lift(f)
    tilt = seg(f, [(63, 0.0), (75, 0.05), (80, 0.05), (90, 0.0)])
    m = Matrix.Translation(BAG_REST + V((0, 0, lift))) @ Matrix.Rotation(tilt, 4, "Y")
    return m


def bag_shape(f):
    lift = bag_lift(f)
    sag = min(1.0, max(0.0, lift / 0.05))
    return sag, 1.0 - sag


def slider_x(f):
    a, b = Z["insert"]
    c, d = Z["full_f"]
    return seg(f, [(a, Z["start"]), (b, Z["after_insert"]), (c, Z["after_insert"]), (d, Z["full"])])


def flap_angle(f, which):
    return math.radians(Z["flap_deg"][which]) * smooth((f - Z["flaps_f"][0]) / (Z["flaps_f"][1] - Z["flaps_f"][0]))


def ring_local(f):
    return V((slider_x(f) + 0.018, 0.0, B["H"] + 0.008))


def ring_m(f):
    return bag_m(f) @ Matrix.Translation(ring_local(f))


# ------------------------------------------------------------------ tag (body-local)
CORD = 0.04


def tag_cam_axes():
    cam, aim = CAMS["CAM_08"]["pos"], CAMS["CAM_08"]["aim"]
    fwd = (aim - cam).normalized()
    right = fwd.cross(V((0, 0, 1))).normalized()
    up = right.cross(fwd)
    return fwd, right, up


def tag_pose(f):
    """Returns (eyelet position, rotation matrix) in body-local. Tag-local +X runs along the card, text face is -Y."""
    ring = ring_m(f).translation
    bagR = bag_m(f).to_3x3()
    s = slider_x(f)
    tip = smooth((s - 0.25) / 0.02)                          # flops over the bag end as the slider reaches it
    lie = Matrix((V((1, 0, 0)), V((0, 0, 1)), V((0, -1, 0)))).transposed()     # columns x, y, z: lying flat, text face down
    hang = Matrix((V((0, 0, -1)), V((1, 0, 0)), V((0, -1, 0)))).transposed()   # draped over the +X end, text face to the wall
    R0 = bagR @ lie.to_quaternion().slerp(hang.to_quaternion(), tip).to_matrix()
    eyelet0 = ring + R0 @ V((CORD, 0, 0.002 if tip < 0.5 else 0.0))
    swing = 0.10 * math.sin((f - 130) * 0.55) * math.exp(-max(0, f - 130) / 12) if f >= 130 else 0.0
    R0 = R0 @ Quaternion((0, 0, 1), swing).to_matrix()
    p0, f1 = T["pinch"], T["flip"][1]
    if f < p0:
        return eyelet0, R0
    fwd, right, up = tag_cam_axes()
    Rf = Matrix((right, fwd, up)).transposed()                # right-handed; text face (-Y) toward CAM_08, reads left-to-right
    hold = ring + V((0, 0, 0.034)) - fwd * 0.012
    hold = hold + V((0, 0, 0.0015 * math.sin(f * 0.8)))      # fingers' micro-motion
    t = smooth((f - p0) / (f1 - p0))
    q = R0.to_quaternion().slerp(Rf.to_quaternion(), t)
    return eyelet0.lerp(hold, t), q.to_matrix()


# ------------------------------------------------------------------ steering wheel grip points
WC = V(K["wheel_c"])
WU = V((1, 0, 0))
WV = V((0, math.cos(math.radians(62)), math.sin(math.radians(62))))
WN = WU.cross(WV)                                            # points back toward the driver


def wheel_grip(deg, side):
    a = math.radians(deg)
    radial = WU * math.cos(a) + WV * math.sin(a)
    p = WC + radial * K["wheel_rad"]
    wrist = p + radial * 0.035 + WN * 0.055 - WV * 0.03
    fdir = (-WN * 0.75 + radial * -0.25 + WV * 0.3).normalized()
    palm = (-radial).normalized()
    return wrist, fdir, palm


def hand_target_m(arm, side, wrist, fdir, palm):
    k = -1 if side == "L" else 1
    A = arm.matrix_basis.to_3x3()
    R0 = A @ arm.data.bones[f"hand.{side}"].matrix_local.to_3x3()
    f0, n0 = (A @ V((0, 0, -1))).normalized(), (A @ V((-k, 0, 0))).normalized()
    fdir = V(fdir).normalized()
    palm = (V(palm) - fdir * V(palm).dot(fdir)).normalized()
    Ma = Matrix((fdir, palm, fdir.cross(palm))).transposed()
    Mb = Matrix((f0, n0, f0.cross(n0))).transposed()
    m = (Ma @ Mb.transposed() @ R0).to_4x4()
    m.translation = wrist
    return m


def foot_target_m(arm, side, pos):
    m = arm.data.bones[f"foot.{side}"].matrix_local.to_3x3().to_4x4()
    m.translation = pos
    return m


def lerp3(a, b, t):
    return tuple(x.lerp(y, t) for x, y in zip(a, b))


# ------------------------------------------------------------------ cameras (world = body-local once parked; set in build)
HEAD_J = V((K["driver_x"], K["seat_y"] - 0.05, 1.07))
HEAD_L = V((K["pass_x"], K["seat_y"] - 0.05, 1.015))
CAMS = {
    # interior cameras sit inside the cabin, under the windshield plane; S05/S08 look in through the open passenger window
    # CUs: hood mount shooting back through the windshield (front side of the Jason-Lucia line throughout)
    "CAM_02": dict(pos=V((-0.12, 1.30, 1.16)), aim=HEAD_J + V((0.0, 0.0, -0.05)), fstop=5.6),
    "CAM_03": dict(pos=V((0.12, 1.30, 1.12)), aim=HEAD_L + V((0.0, 0.0, -0.05)), fstop=5.6),
    "CAM_04": dict(pos=V((0.16, 1.30, 1.12)), aim=BAG_REST + V((-0.16, 0.0, B["H"] - 0.01)), fstop=8.0),   # hood mount, through the glass
    "CAM_05": dict(pos=V((1.15, -0.04, 1.25)), aim=BAG_REST + V((0.0, 0.0, 0.18)), fstop=8.0),
    "CAM_06": dict(pos=V((-0.16, 1.45, 1.14)), aim=HEAD_J + V((0.0, 0.0, -0.01)), fstop=5.6),
    "CAM_07": dict(pos=V((0.16, 1.45, 1.10)), aim=HEAD_L + V((0.0, 0.0, -0.01)), fstop=5.6),
    "CAM_08": dict(pos=V((1.05, 0.15, 0.98)), aim=V((0.62, 0.0, 0.83)), fstop=11.0),
    "CAM_10": dict(pos=V((-0.05, 1.42, 1.18)), aim=HEAD_J + V((0.0, 0.0, -0.01)), fstop=5.6),
}


def look_q(pos, aim):
    return (V(aim) - V(pos)).normalized().to_track_quat("-Z", "Y")


# ------------------------------------------------------------------ apply
def apply(sc, chars, carp, bagp, heli, police):
    root, body, wheels = carp
    J, Jt = chars["JASON_01"]
    L, Lt = chars["LUCIA_01"]
    log = {"frames": {}}
    jaws = {}
    for d in C.DIALOGUE:
        for i, v in enumerate(SYNC[d["id"]]["jaw"]):
            jaws[(d["who"], d["f0"] + i)] = v
    seatJ, seatL = V((K["driver_x"], K["seat_y"], 0)), V((K["pass_x"], K["seat_y"], 0))
    J.location, L.location = seatJ, seatL
    dropJ = V((0, 0, K["seat_z"] + 0.07 - 0.53 * C.JASON_H))
    dropL = V((0, 0, K["seat_z"] + 0.07 - 0.53 * C.LUCIA_H))
    blinks = {"JASON_01": [12, 70, 128, 190, 236, 284], "LUCIA_01": [20, 58, 142, 172, 228, 262]}
    rest_bag_L = lambda f: (bag_m(f) @ V((-0.06, -0.20, 0.24)), bag_m(f).to_3x3() @ V((0.2, 1, -0.3)), bag_m(f).to_3x3() @ V((0, 0.4, -1)))  # noqa: E731
    rest_bag_R = lambda f: (bag_m(f) @ V((0.38, 0.0, 0.13)), bag_m(f).to_3x3() @ V((-1, 0.1, -0.2)), bag_m(f).to_3x3() @ V((-0.4, 0, -1)))  # noqa: E731
    for f in FR:
        sc.frame_set(f)
        # ---------------- car
        root.location = (0, car_y(f), 0)
        root.keyframe_insert("location", frame=f)
        pitch, dz = body_pitch_z(f)
        body.rotation_euler = (pitch, 0, 0)
        body.location = (0, 0, dz)
        body.keyframe_insert("rotation_euler", frame=f)
        body.keyframe_insert("location", frame=f)
        dist = car_y(f) - K["brake_start_y"]
        for w in wheels:
            w.rotation_euler = (-dist / K["wheel_r"], 0, 0)
            w.keyframe_insert("rotation_euler", frame=f)
        # ---------------- bag, zipper, flaps, gap, tag
        key_m(bagp["root"], bag_m(f), f)
        sag, squash = bag_shape(f)
        kb = bagp["shell"].data.shape_keys.key_blocks
        kb["sag"].value, kb["squash"].value = sag, squash
        kb["sag"].keyframe_insert("value", frame=f)
        kb["squash"].keyframe_insert("value", frame=f)
        s = slider_x(f)
        bagp["slider"].location = (s, 0, B["H"] + 0.004)
        bagp["slider"].keyframe_insert("location", frame=f)
        g = bagp["gap"]
        g.location = (B["zip_x0"], 0, 0)
        g.scale = (max(0.0005, s - B["zip_x0"] - 0.012), 1, 1)
        g.keyframe_insert("location", frame=f)
        g.keyframe_insert("scale", frame=f)
        bagp["flaps"][1].rotation_euler = (-flap_angle(f, "front"), 0, 0)
        bagp["flaps"][-1].rotation_euler = (flap_angle(f, "back"), 0, 0)
        for h in bagp["flaps"].values():
            h.keyframe_insert("rotation_euler", frame=f)
        ey, R = tag_pose(f)
        key_m(bagp["tag"], Matrix.Translation(ey) @ R.to_4x4(), f)
        ring = ring_m(f).translation
        cd = ey - ring
        cm = Matrix.Translation((ring + ey) / 2) @ cd.to_track_quat("Z", "Y").to_matrix().to_4x4()
        key_m(bagp["cord"], cm, f)
        bagp["cord"].scale = (1, 1, max(0.2, cd.length / CORD))
        bagp["cord"].keyframe_insert("scale", frame=f)
        # ---------------- characters: seat, breathing, blinks, jaw
        for cid, arm, tg, drop, rate in (("JASON_01", J, Jt, dropJ, 3.6), ("LUCIA_01", L, Lt, dropL, 3.2)):
            pb = arm.pose.bones
            pb["hips"].location = pb["hips"].bone.matrix_local.to_3x3().inverted() @ drop
            pb["hips"].keyframe_insert("location", frame=f)
            br = 0.014 * math.sin(2 * math.pi * f / (rate * C.FPS))
            effort = 0.06 * smooth((f - 62) / 8) * (1 - smooth((f - 82) / 8)) if cid == "LUCIA_01" else 0.0
            lean_j = seg(f, [(150, 0.0), (156, -0.02), (175, -0.015), (180, 0.0)]) if cid == "JASON_01" else 0.0
            lean_j += seg(f, [(88, 0.0), (94, 0.16), (116, 0.18), (124, 0.20), (132, 0.18), (142, 0.0)]) if cid == "JASON_01" else 0.0
            lean_l = seg(f, [(204, 0.0), (212, 0.16), (239, 0.14), (246, 0.0)]) if cid == "LUCIA_01" else 0.0
            rig.set_rot(pb["spine"], (1, 0, 0), 0.14 - (lean_j + lean_l) * 0.5 - effort)
            rig.set_rot(pb["chest"], (1, 0, 0), -br - (lean_j + lean_l) * 0.5)
            pb["spine"].keyframe_insert("rotation_quaternion", frame=f)
            pb["chest"].keyframe_insert("rotation_quaternion", frame=f)
            bl = any(0 <= f - b0 <= 3 for b0 in blinks[cid])
            rig.set_rot(pb["lids"], (1, 0, 0), -1.0 if bl else 0.0)
            pb["lids"].keyframe_insert("rotation_quaternion", frame=f)
            jv = jaws.get((cid, f), 0.0)
            shock = seg(f, [(176, 0.0), (180, 0.0)]) if cid == "JASON_01" else 0.0
            rig.set_rot(pb["jaw"], (1, 0, 0), -(0.16 * jv + 0.05 * shock))
            pb["jaw"].keyframe_insert("rotation_quaternion", frame=f)
            for sd in ("L", "R"):
                k = -1 if sd == "L" else 1
                reach = 0.84 if cid == "JASON_01" else 0.78           # long legs: thighs lie low enough for the bag and the wheel
                key_m(tg[f"foot.{sd}"], foot_target_m(arm, sd, arm.location + V((k * 0.11, reach, K["floor_z"] + 0.08))), f)
        # ---------------- JASON hands
        jl = wheel_grip(150, "L")
        jr = wheel_grip(30, "R")
        J_REL = Z["insert"][1] + 2                          # Jason lets go after his 15 cm; Lucia finishes the run toward her end
        if 88 <= f <= J_REL + 16:
            pull = lambda ff: (ring_m(ff).translation + V((-0.035, 0.095, 0.03)), V((0.3, -1, -0.35)), V((0.1, 0.1, -1)))  # noqa: E731  (pinch from the front side)
            if f < 94:
                jr = lerp3(jr, pull(f), smooth((f - 88) / 6))
            elif f <= J_REL:
                jr = pull(f)
            else:
                lift = pull(J_REL)
                lift = (lift[0] + V((-0.04, 0.0, 0.05)), lift[1], lift[2])
                jr = lerp3(lerp3(pull(J_REL), lift, smooth((f - J_REL) / 4)), wheel_grip(30, "R"), smooth((f - J_REL - 4) / 12))
        key_m(Jt["hand.L"], hand_target_m(J, "L", *jl), f)
        key_m(Jt["hand.R"], hand_target_m(J, "R", *jr), f)
        for sd, cu in (("L", 0.9), ("R", 0.55 if 94 <= f <= 130 else 0.9)):
            rig.set_rot(J.pose.bones[f"fingers.{sd}"], (0, 1, 0), (1 if sd == "R" else -1) * cu * 1.2)
            J.pose.bones[f"fingers.{sd}"].keyframe_insert("rotation_quaternion", frame=f)
        # ---------------- LUCIA hands
        ll, lr = rest_bag_L(f), rest_bag_R(f)
        a_, b_ = Z["full_f"]
        if a_ - 5 <= f <= b_ + 12:
            pullL = lambda ff: (ring_m(ff).translation + V((0.055, 0.02, 0.10)), V((-0.45, -0.1, -1)), V((-1, 0, 0.3)))  # noqa: E731  (pinch from above)
            if f < a_:
                t = smooth((f - (a_ - 5)) / 5)
                lr = lerp3(rest_bag_R(f), pullL(f), t)
                lr = (lr[0] + V((0.05, 0, 0.10)) * math.sin(math.pi * t), lr[1], lr[2])      # arc up and over the bag end
            elif f <= b_:
                lr = pullL(f)
            else:
                t = smooth((f - b_) / 12)
                lr = lerp3(pullL(b_), rest_bag_R(f), t)
                lr = (lr[0] + V((0.05, 0, 0.08)) * math.sin(math.pi * t), lr[1], lr[2])
        if f >= 200:
            ey, Rt = tag_pose(max(f, T["pinch"]))
            xa, ya, za = Rt.col[0], Rt.col[1], Rt.col[2]
            centre = ey + xa * (C.TAG["w"] / 2)
            grip = (centre + za * 0.085 + ya * 0.03, -za, -ya)  # behind the card: only fingertips over the top edge
            t = smooth((f - 200) / (T["pinch"] - 200))
            lr = lerp3(lr, grip, t) if f < T["pinch"] else grip
            if f < T["pinch"]:
                lr = (lr[0] + V((0.05, 0, 0.08)) * math.sin(math.pi * t), lr[1], lr[2])
            if f > 244:
                t = smooth((f - 244) / 14)
                lr = lerp3(grip, rest_bag_R(f), t)
                lr = (lr[0] + V((0.07, 0, 0.10)) * math.sin(math.pi * t), lr[1], lr[2])
        key_m(Lt["hand.L"], hand_target_m(L, "L", *ll), f)
        key_m(Lt["hand.R"], hand_target_m(L, "R", *lr), f)
        for sd, cu in (("L", 0.6), ("R", 0.75 if (T["pinch"] <= f <= 244 or Z["full_f"][0] <= f <= Z["full_f"][1]) else 0.55)):
            rig.set_rot(L.pose.bones[f"fingers.{sd}"], (0, 1, 0), (1 if sd == "R" else -1) * cu * 1.2)
            L.pose.bones[f"fingers.{sd}"].keyframe_insert("rotation_quaternion", frame=f)
        # ---------------- looks (eyelines), with head-turn anticipation
        out_j = V((K["driver_x"] + 0.1, 3.0, 1.15))
        out_l = V((K["pass_x"] - 0.2, 3.0, 1.05))
        at_l, at_j = HEAD_L + V((0, 0.05, 0)), HEAD_J + V((0, 0.05, 0))
        bagtop = BAG_REST + V((0, 0, B["H"]))
        up_j, up_l = V((-2.5, 6.0, 4.0)), V((-1.8, 6.0, 4.0))
        lj = seg(f, [(0, out_j), (38, out_j), (41, out_j + V((-0.5, 0, -0.15))), (47, at_l + V((0.06, 0, 0))), (50, at_l),
                     (64, at_l), (70, bagtop), (88, bagtop), (92, ring_m(100).translation), (118, ring_m(118).translation),
                     (124, bagtop), (150, bagtop), (153, at_l), (176, at_l), (190, at_l), (232, ring_m(232).translation),
                     (246, ring_m(240).translation), (252, up_j), (300, up_j)])
        ll_ = seg(f, [(0, out_l), (26, out_l), (33, at_j), (60, at_j), (64, at_j), (67, bagtop), (71, at_j), (90, at_j), (96, bagtop),
                      (150, bagtop), (155, at_j), (180, at_j), (200, at_j), (206, ring_m(206).translation), (240, tag_pose(240)[0]),
                      (248, up_l), (300, up_l)])
        if 274 <= f:
            lj = lj + V((0, 0, 0))
        key_m(Jt["look"], Matrix.Translation(lj), f)
        key_m(Lt["look"], Matrix.Translation(ll_), f)
        # Lucia half-smile in SHOT_07 (mouth corner lift on the jaw)
        mo = bpy.data.objects["LUCIA_01_mouth"]
        sm = seg(f, [(184, 0.0), (190, 0.0), (196, 0.22), (210, 0.22), (214, 0.1)])
        mo.rotation_euler = (0, sm, 0)
        mo.keyframe_insert("rotation_euler", frame=f)
        for nm, up in (("JASON_01_browL", seg(f, [(150, 0.0), (154, 0.004), (176, 0.003), (182, 0.0), (268, 0.0), (276, 0.005)])),
                       ("JASON_01_browR", seg(f, [(150, 0.0), (154, 0.004), (176, 0.003), (182, 0.0), (268, 0.0), (276, 0.005)]))):
            o = bpy.data.objects[nm]
            o.delta_location = (0, 0, up)
            o.keyframe_insert("delta_location", frame=f)
        # ---------------- heli, beam, police
        hroot, rotor, spot, tgt, nav = heli
        hp = seg(f, [(0, V((-60.0, 120.0, 60.0))), (236, V(C.HELI["start"])), (300, V(C.HELI["end"]))])
        hroot.location = hp
        hroot.rotation_euler = (0.12, 0, math.radians(200))
        hroot.keyframe_insert("location", frame=f)
        hroot.keyframe_insert("rotation_euler", frame=f)
        rotor.rotation_euler = (0, 0, f * 1.37)
        rotor.keyframe_insert("rotation_euler", frame=f)
        a, b = C.BEAM["f"]
        c0, c1 = C.BEAM["face"]
        ground = V((3.0, 1.0, 0.0))                          # beside the car, inside CAM_09's frame
        wind = V((-0.30, 0.42, 1.0))
        tp = seg(f, [(0, ground), (a, ground), (a + 6, V((1.2, 2.8, 0.0))), (a + 12, V((0.3, 1.6, 0.85))), (b, wind), (b + 6, wind), (c0, V((-2.4, -0.3, 1.1))), (c1, V((1.6, -0.4, 1.1))), (300, V((1.8, -0.4, 1.1)))])
        tgt.location = tp
        tgt.keyframe_insert("location", frame=f)
        on = 1.0 if f >= 238 else 0.0
        spot.data.energy = 4.0e5 * on
        spot.data.keyframe_insert("energy", frame=f)
        for k, o in nav.items():
            o.hide_render = not ((f // 12) % 2 == (0 if k == "red" else 1))
            o.keyframe_insert("hide_render", frame=f)
        ph = (f // 4) % 2
        for nm, o in police["bars"].items():
            lit = (ph == 0) == ("blue" in nm)
            o.data.materials[0].node_tree.nodes["Emission"].inputs["Strength"].default_value = 30 if lit else 1
        for nm, l_ in police["lights"].items():
            lit = (ph == 0) == ("blue" in nm)
            l_.data.energy = 9000 if lit else 0
            l_.data.keyframe_insert("energy", frame=f)
        police["spill"].data.energy = 160 if ph == 0 else 10
        police["spill"].data.keyframe_insert("energy", frame=f)
        log["frames"][f] = dict(car_y=round(car_y(f), 4), pitch=round(pitch, 5), slider_x=round(s, 4), bag_lift=round(bag_lift(f), 4),
                                tag_eyelet=[round(v, 4) for v in ey], beam_target=[round(v, 3) for v in tp])
    return log


def key_police_bars(police):
    """Material emission keys for the flashing bar (one material per colour)."""
    for f in FR:
        ph = (f // 4) % 2
        for nm, o in police["bars"].items():
            node = o.data.materials[0].node_tree.nodes["Emission"]
            node.inputs["Strength"].default_value = 30 if (ph == 0) == ("blue" in nm) else 1
            node.inputs["Strength"].keyframe_insert("default_value", frame=f)


def cameras(sc, chars, body):
    coll = bpy.data.collections.get("CAMERAS") or bpy.data.collections.new("CAMERAS")
    if coll.name not in [c.name for c in sc.collection.children]:
        sc.collection.children.link(coll)
    J = chars["JASON_01"][0]
    out = {}
    for s in C.SHOTS:
        cd = bpy.data.cameras.new(s["cam"])
        cd.lens, cd.sensor_width = s["lens"], 36
        cd.clip_start, cd.clip_end = 0.01, 500
        cd.dof.use_dof = True
        cam = bpy.data.objects.new(s["cam"], cd)
        coll.objects.link(cam)
        cam.rotation_mode = "QUATERNION"
        if s["cam"] not in ("CAM_01", "CAM_09"):
            cam.parent = body                     # interior cameras ride with the car body
        for f in range(s["f0"], s["f1"]):
            if s["cam"] == "CAM_01":
                cy = car_y(f)
                pos = V((2.35, cy + 4.6, 0.38))
                aim = V((0.0, cy + 0.6, 0.66))
                fst, foc = 5.6, (V((0.8, cy + 2.2, 0.6)) - pos).length
            elif s["cam"] == "CAM_09":
                pos, aim, fst = V((2.3, 6.4, 0.75)), V((-0.35, 0.2, 1.25)), 8.0
                foc = (V((0, 0.4, 1.0)) - pos).length
            else:
                cs = CAMS[s["cam"]]
                pos, fst = cs["pos"].copy(), cs["fstop"]
                aim = cs["aim"].copy() if cs["aim"] is not None else pos + V((0, 0, -1))
                if s["cam"] == "CAM_05":
                    pos = pos.lerp(aim, 0.08 * smooth((f - s["f0"]) / 29))
                foc = (aim - pos).length if cs["aim"] is not None else pos.z - (B["z"] + B["H"])
            cam.location = pos
            cam.rotation_quaternion = look_q(pos, aim)
            cam.keyframe_insert("location", frame=f)
            cam.keyframe_insert("rotation_quaternion", frame=f)
            cd.dof.focus_distance, cd.dof.aperture_fstop = foc, fst
            cd.dof.keyframe_insert("focus_distance", frame=f)
        mk = sc.timeline_markers.new(s["id"], frame=s["f0"])
        mk.camera = cam
        out[s["cam"]] = cam
    return out
