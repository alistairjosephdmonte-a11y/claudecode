"""Performance, props, cameras and timeline markers. Every control is a function of the frame and is keyed on
every frame, so positions are exact and checkable (metadata/build_log.json)."""
import math

import bpy
from mathutils import Matrix, Quaternion, Vector

import config as C
import rig

V = Vector
F = C.TOTAL_FRAMES


def smooth(t):
    t = min(1.0, max(0.0, t))
    return t * t * (3 - 2 * t)


def seg(f, keys):
    """Piecewise eased interpolation between (frame, value) keys; values are floats, Vectors or Quaternions."""
    if f <= keys[0][0]:
        return keys[0][1]
    for (f0, a), (f1, b) in zip(keys, keys[1:]):
        if f <= f1:
            t = smooth((f - f0) / (f1 - f0)) if f1 > f0 else 1.0
            if isinstance(a, Quaternion):
                return a.slerp(b, t)
            return a + (b - a) * t
    return keys[-1][1]


def frame_m(pos, fwd, up):
    """Matrix with local +Y = fwd and local +Z ~ up."""
    y = V(fwd).normalized()
    x = y.cross(V(up)).normalized()
    z = x.cross(y)
    m = Matrix((x, y, z)).transposed().to_4x4()
    m.translation = V(pos)
    return m


def heading_q(theta):
    return Quaternion((0, 0, 1), theta)


def heading_to(d):
    return math.atan2(-d.x, d.y)


# ------------------------------------------------------------------ geometry anchors
P2, K = C.PS2, C.CABINET
TRAY_OPEN = V((P2["x"] - 0.01, P2["front_y"] - P2["tray_out"] + 0.07, P2["z"] + 0.050))
TRAY_SHUT = TRAY_OPEN + V((0, P2["tray_out"], 0))
TRAY_CLOSE = (128, 140)
DISC_ON_TRAY = V((0, 0, 0.011))
GAMER_POS = V((C.SEAT["x"], C.SEAT["y"], 0))
SCREEN = V((0, C.CRT["y"] - C.CRT["d"] / 2 - 0.02, K["h"] + C.CRT["h"] / 2 + 0.02))
PS2_FRONT = V((P2["x"], P2["front_y"], P2["z"] + 0.04))
TOMMY_A, TOMMY_B = V(C.TOMMY_START + (0,)), V(C.TOMMY_MARK + (0,))


def tray_pos(f):
    return seg(f, [(TRAY_CLOSE[0], TRAY_OPEN), (TRAY_CLOSE[1], TRAY_SHUT)])


# ------------------------------------------------------------------ DISC_01 world matrix
def disc_m(f):
    """Disc frame: local +Z = label normal, local +Y = from the wrist across the disc."""
    if f >= 116:
        t = tray_pos(f)
        return Matrix.Translation(t + DISC_ON_TRAY)
    lap = (V((0.20, 1.00, 0.68)), V((-0.15, -0.35, 0.92)), V((0.15, 0.95, 0.2)))
    show = (V((0.16, 1.02, 0.92)), V((0.30, -0.95, 0.30)), V((-0.25, 0.3, 0.9)))
    over = (TRAY_OPEN + DISC_ON_TRAY + V((0, -0.01, 0.06)), V((0, 0, 1)), V((0, 1, 0)))
    down = (TRAY_OPEN + DISC_ON_TRAY, V((0, 0, 1)), V((0, 1, 0)))
    keys = [(1, lap), (38, lap), (60, show), (98, show), (110, over), (114, down)]
    for (f0, a), (f1, b) in zip(keys, keys[1:]):
        if f <= f1:
            t = smooth((f - f0) / (f1 - f0))
            pos = a[0].lerp(b[0], t)
            n = a[1].lerp(b[1], t).normalized()
            g = a[2].lerp(b[2], t)
            if 60 <= f <= 98:                                # S02: slow wrist turn while he reads the label
                q = Quaternion((0, 0, 1), math.radians(9) * math.sin((f - 60) / 38 * math.pi))
                n, g = q @ n, q @ g
            g = (g - n * g.dot(n)).normalized()
            m = frame_m(pos, g, n)
            return m
    return frame_m(down[0], down[2], down[1])


def disc_grip(f):
    """Right-hand target from the disc: thumb on the near rim, fingertips on the far rim, palm 2.5 cm above."""
    m = disc_m(f)
    R = m.to_3x3()
    pos, x, y, z = m.translation, R.col[0], R.col[1], R.col[2]
    # hand sits outside the near rim: fingers run along the rim (tangent), palm faces the disc centre, so the label stays clear
    wrist = pos - y * (C.DISC["r"] + 0.045) - x * 0.035 + z * 0.006
    return wrist, (x * 0.9 + y * 0.25).normalized(), y


# ------------------------------------------------------------------ CONTROLLER_01 world matrix
CTRL_LAP = (V((-0.11, 0.96, 0.605)), V((0, 1, 0)), V((0, 0, 1)))


def ctrl_play_gamer(f):
    p = V((0.0, 1.02, 0.72)) + V((0, 0, 0.006 * math.sin(f * 0.7)))
    return p, V((0, math.cos(0.6), math.sin(0.6))), V((0, -math.sin(0.6), math.cos(0.6)))


def tommy_frame(f):
    """Tommy root position and heading (world)."""
    return tommy_root(f)


def ctrl_play_tommy(f):
    pos, th = tommy_root(f)
    q = heading_q(th)
    p = pos + q @ V((0.02, 0.33, 1.06))
    fwd = q @ V((0, math.cos(0.7), math.sin(0.7)))
    up = q @ V((0, -math.sin(0.7), math.cos(0.7)))
    return p, fwd, up


HANDOFF = 352


def ctrl_m(f):
    if f <= 152:
        return frame_m(*CTRL_LAP)
    if f <= 172:
        a, b = CTRL_LAP, ctrl_play_gamer(172)
        t = smooth((f - 152) / 20)
        return frame_m(a[0].lerp(b[0], t) + V((0, 0, 0.05 * math.sin(t * math.pi))), a[1].lerp(b[1], t), a[2].lerp(b[2], t))
    if f <= 340:
        return frame_m(*ctrl_play_gamer(f))
    op = V((0.25, 0.98, 0.86))
    to_t = (TOMMY_B + V((0, 0, op.z)) - op)
    to_t = V((to_t.x, to_t.y, 0)).normalized()
    offer = (op, (to_t + V((0, 0, 0.35))).normalized(), (-to_t * 0.35 + V((0, 0, 1))).normalized())
    if f <= HANDOFF:
        a = ctrl_play_gamer(340)
        t = smooth((f - 340) / (HANDOFF - 340))
        return frame_m(a[0].lerp(offer[0], t), a[1].lerp(offer[1], t), a[2].lerp(offer[2], t))
    if f <= 368:
        b = ctrl_play_tommy(368)
        t = smooth((f - HANDOFF) / (368 - HANDOFF))
        return frame_m(offer[0].lerp(b[0], t), offer[1].lerp(b[1], t), offer[2].lerp(b[2], t))
    return frame_m(*ctrl_play_tommy(f))


def ctrl_grip(f, side):
    """Wrist target and hand frame for one hand on the controller grips."""
    m = ctrl_m(f)
    R = m.to_3x3()
    x, y, z = R.col[0], R.col[1], R.col[2]
    k = -1 if side == "L" else 1
    wrist = m.translation + x * (k * 0.085) - y * 0.085 - z * 0.012
    fdir = (y * 0.85 - x * k * 0.35).normalized()
    palm = (-x * k * 0.8 + z * 0.4).normalized()
    return wrist, fdir, palm


# ------------------------------------------------------------------ TOMMY_01 walk (S06)
WALK0, STEP_T, NSTEP = 244, 8, 5
WALK1 = WALK0 + STEP_T * NSTEP
TH_IN = heading_to(TOMMY_B - TOMMY_A)
TH_GAMER = heading_to(GAMER_POS - TOMMY_B)
TH_CRT = heading_to(V((SCREEN.x, SCREEN.y, 0)) - TOMMY_B)


def tommy_root(f):
    if f <= WALK0:
        return TOMMY_A.copy(), TH_IN
    if f <= WALK1:
        u = (f - WALK0) / (WALK1 - WALK0)
        s = u - math.sin(2 * math.pi * u) / (2 * math.pi) * 0.0       # constant speed between soft ends
        s = smooth(u) * 0.35 + u * 0.65
        th = TH_IN + (TH_GAMER - TH_IN) * smooth((u - 0.6) / 0.4)
        return TOMMY_A.lerp(TOMMY_B, s), th
    th = seg(f, [(WALK1, TH_GAMER), (WALK1 + 6, TH_GAMER), (356, TH_GAMER), (372, (TH_GAMER + TH_CRT) / 2)])
    return TOMMY_B.copy(), th


TURN_R, TURN_L = 364, 372          # Tommy steps round toward the CRT in S08


def _plants():
    path = lambda u: TOMMY_A.lerp(TOMMY_B, u)    # noqa: E731
    off = lambda th, k: heading_q(th) @ V((k * 0.10, 0, 0))   # noqa: E731
    th_end = tommy_root(TURN_L)[1]
    pl = {"R": [(WALK0, path(0) + off(TH_IN, 1), TH_IN)], "L": [(WALK0, path(0) + off(TH_IN, -1), TH_IN)]}
    for i in range(NSTEP):
        side, k = ("R", 1) if i % 2 == 0 else ("L", -1)
        fl = WALK0 + (i + 1) * STEP_T
        u = min(1.0, (i + 1) / (NSTEP - 1))
        th = tommy_root(fl)[1]
        pl[side].append((fl, path(u) + off(th, k), th))
    pl["R"].append((TURN_R, TOMMY_B + off(th_end, 1), th_end))
    pl["L"].append((TURN_L, TOMMY_B + off(th_end, -1), th_end))
    return pl


PLANTS = None


def tommy_feet(f):
    """Planted feet (fixed world positions) with lifted swings between plants: {side: (ankle pos, heading)}."""
    global PLANTS
    if PLANTS is None:
        PLANTS = _plants()
    out = {}
    for side, pl in PLANTS.items():
        res = (pl[-1][1], pl[-1][2], 0.0)
        if f <= pl[0][0]:
            res = (pl[0][1], pl[0][2], 0.0)
        for (fa, pa, ta), (fb, pb, tb) in zip(pl, pl[1:]):
            if fa < f <= fb:
                u = (f - (fb - STEP_T)) / STEP_T
                if u <= 0:
                    res = (pa, ta, 0.0)
                else:
                    res = (pa.lerp(pb, smooth(u)), ta + (tb - ta) * smooth(u), 0.09 * math.sin(math.pi * u))
                break
        out[side] = (res[0] + V((0, 0, 0.078 + res[2])), res[1])
    return out


def ctrl_grab(f):
    """Tommy's right hand takes the controller by its far edge, palm down, fingers pointing back over it."""
    m = ctrl_m(f)
    R = m.to_3x3()
    return m.translation + R.col[1] * 0.115 + R.col[2] * 0.03, -R.col[1], -R.col[2]


# ------------------------------------------------------------------ apply
def key_m(o, m, f):
    o.matrix_world = m
    o.keyframe_insert("location", frame=f)
    o.rotation_mode = "QUATERNION"
    o.keyframe_insert("rotation_quaternion", frame=f)


def hand_target_m(arm, side, wrist, fdir, palm):
    """World matrix for the hand IK target so the hand bone points along fdir with its palm along `palm`."""
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


def foot_target_m(arm, side, pos, th):
    R0 = arm.data.bones[f"foot.{side}"].matrix_local.to_3x3()     # world = heading @ rest
    m = (heading_q(th).to_matrix() @ R0).to_4x4()
    m.translation = pos
    return m


def apply(sc, chars, hw, car, wheels, hinges, fog_portal, fog_trans):
    G, Gt = chars["GAMER_01"]
    T, Tt = chars["TOMMY_01"]
    log = {"frames": {}}
    hipsG, hipsT = G.pose.bones["hips"], T.pose.bones["hips"]
    G.location = GAMER_POS
    seat_drop = V((0, 0, C.SEAT["h"] + 0.07 - 0.53 * C.GAMER_H))
    rest_hand_R = (GAMER_POS + V((0.15, 0.30, 0.64)), V((0.05, 1, -0.3)), V((-0.6, 0, -0.8)))
    rest_hand_L = (GAMER_POS + V((-0.15, 0.30, 0.64)), V((-0.05, 1, -0.3)), V((0.6, 0, -0.8)))
    for f in range(1, F + 1):
        sc.frame_set(f)
        # ---------------- GAMER_01
        lean = seg(f, [(1, 0.05), (96, 0.08), (106, 0.66), (124, 0.68), (138, 0.12), (150, 0.10), (158, 0.30), (172, 0.10),
                       (212, 0.08), (226, -0.06), (240, -0.04), (290, -0.02), (300, -0.08), (336, -0.06), (344, 0.12), (356, 0.02),
                       (380, 0.04)])
        twist = seg(f, [(1, 0.0), (96, -0.05), (110, -0.30), (126, -0.30), (140, 0.0)])
        breathe = 0.008 * math.sin(f / 24 * 2 * math.pi / 3.2)
        slide = seg(f, [(96, 0.0), (106, 0.04), (124, 0.04), (138, 0.0)])
        hipsG.location = hipsG.bone.matrix_local.to_3x3().inverted() @ (seat_drop + V((0, slide, 0)))
        rig.set_rot(hipsG, (1, 0, 0), -max(0.0, lean) * 0.28)
        rig.set_rot(G.pose.bones["spine"], (1, 0, 0), -(lean * 0.45 + breathe))
        cq = Quaternion((1, 0, 0), -lean * 0.35) @ Quaternion((0, 0, 1), twist)
        Bm = G.pose.bones["chest"].bone.matrix_local.to_3x3()
        G.pose.bones["chest"].rotation_quaternion = (Bm.inverted() @ cq.to_matrix() @ Bm).to_quaternion()
        for b in ("hips", "spine", "chest"):
            G.pose.bones[b].keyframe_insert("location" if b == "hips" else "rotation_quaternion", frame=f)
            if b == "hips":
                G.pose.bones[b].keyframe_insert("rotation_quaternion", frame=f)
        # gamer hands
        if f <= 118:
            wR = disc_grip(f)
            curlR = 0.55
        elif f <= 124:
            w, fd, pa = disc_grip(118)
            u = (f - 118) / 6
            wR = (w + V((0, -0.01, 0.05)) * smooth(u), fd, pa)
            curlR = 0.55 - 0.45 * smooth(u)
        elif f < 152:
            a = disc_grip(118)
            a = (a[0] + V((0, -0.01, 0.05)), a[1], a[2])
            t = smooth((f - 124) / 16)
            wR = (a[0].lerp(rest_hand_R[0], t), a[1].lerp(rest_hand_R[1], t), a[2].lerp(rest_hand_R[2], t))
            curlR = 0.25
        else:
            wR, curlR = None, 0.9
        if 152 <= f <= HANDOFF:
            g = ctrl_grip(f, "R")
            t = smooth((f - 152) / 8)
            wR = (rest_hand_R[0].lerp(g[0], t), rest_hand_R[1].lerp(g[1], t), rest_hand_R[2].lerp(g[2], t)) if f < 160 else g
        elif f > HANDOFF:
            g = ctrl_grip(HANDOFF, "R")
            t = smooth((f - HANDOFF) / 12)
            wR = (g[0].lerp(rest_hand_R[0], t), g[1].lerp(rest_hand_R[1], t), g[2].lerp(rest_hand_R[2], t))
            curlR = 0.9 - 0.6 * t
        if f < 152:
            wL, curlL = rest_hand_L, 0.3
        elif f <= HANDOFF:
            g = ctrl_grip(f, "L")
            t = smooth((f - 152) / 8)
            wL = (rest_hand_L[0].lerp(g[0], t), rest_hand_L[1].lerp(g[1], t), rest_hand_L[2].lerp(g[2], t)) if f < 160 else g
            curlL = 0.3 + 0.6 * t
        else:
            g = ctrl_grip(HANDOFF, "L")
            t = smooth((f - HANDOFF) / 12)
            wL = (g[0].lerp(rest_hand_L[0], t), g[1].lerp(rest_hand_L[1], t), g[2].lerp(rest_hand_L[2], t))
            curlL = 0.9 - 0.6 * t
        key_m(Gt["hand.R"], hand_target_m(G, "R", *wR), f)
        key_m(Gt["hand.L"], hand_target_m(G, "L", *wL), f)
        for side, cu in (("R", curlR), ("L", curlL)):
            rig.set_rot(G.pose.bones[f"fingers.{side}"], (0, 1, 0), (1 if side == "R" else -1) * cu * 1.3)
            G.pose.bones[f"fingers.{side}"].keyframe_insert("rotation_quaternion", frame=f)
        for side, k in (("L", -1), ("R", 1)):
            key_m(Gt[f"foot.{side}"], foot_target_m(G, side, GAMER_POS + V((k * 0.20, 0.40, 0.077)), 0.0), f)
        # gamer look target
        tom_head = tommy_root(f)[0] + V((0, 0, 1.68))
        look = seg(f, [(1, PS2_FRONT), (40, PS2_FRONT), (54, disc_m(60).translation), (96, disc_m(96).translation),
                       (104, TRAY_OPEN), (130, TRAY_OPEN), (140, SCREEN), (150, SCREEN), (156, ctrl_m(160).translation),
                       (170, SCREEN), (206, SCREEN), (222, V((-1.8, 3.0, 0.7))), (238, V((-1.8, 1.8, 0.6))), (246, V((1.25, 3.2, 1.5)))])
        if 246 <= f:
            tw = tom_head if f < 360 else None
            if f >= 360:
                tw = tom_head.lerp(SCREEN, smooth((f - 360) / 14))
            look = tw
        if 400 <= f:
            look = SCREEN
        key_m(Gt["look"], Matrix.Translation(look), f)
        # ---------------- TOMMY_01
        pos, th = tommy_root(f)
        T.location = pos
        T.rotation_mode = "QUATERNION"
        T.rotation_quaternion = heading_q(th)
        T.keyframe_insert("location", frame=f)
        T.keyframe_insert("rotation_quaternion", frame=f)
        feet = tommy_feet(f)
        for side in ("L", "R"):
            key_m(Tt[f"foot.{side}"], foot_target_m(T, side, *feet[side]), f)
        # hips: bob, lateral weight shift over the stance foot, lean for S07/S08
        if WALK0 < f <= WALK1:
            u = (f - WALK0) / STEP_T
            bob = -0.075 - 0.02 * abs(math.cos(math.pi * u))
            sway = 0.025 * math.sin(math.pi * u)
        else:
            bob, sway = -0.02 - 0.03 * smooth(1 - (f - WALK1) / 8) * (f > WALK1), 0.0
        crouch = seg(f, [(292, 0.0), (304, -0.07), (330, -0.07), (338, -0.03), (344, -0.11), (354, -0.11), (366, -0.02)])
        tlean = seg(f, [(292, 0.0), (304, 0.30), (330, 0.30), (338, 0.18), (346, 0.46), (354, 0.46), (368, 0.06)])
        hipsT.location = hipsT.bone.matrix_local.to_3x3().inverted() @ V((sway, 0, bob + crouch))
        hipsT.keyframe_insert("location", frame=f)
        rig.set_rot(T.pose.bones["spine"], (1, 0, 0), -tlean * 0.5)
        rig.set_rot(T.pose.bones["chest"], (1, 0, 0), -tlean * 0.5)
        for b in ("spine", "chest"):
            T.pose.bones[b].keyframe_insert("rotation_quaternion", frame=f)
        # shirt secondary motion: hem lags the hips (velocity-driven swing)
        vel = (tommy_root(f)[0] - tommy_root(f - 2)[0]).length / 2 * C.FPS if f > 2 else 0.0
        acc = vel - ((tommy_root(f - 2)[0] - tommy_root(f - 4)[0]).length / 2 * C.FPS if f > 4 else 0.0)
        hem = 0.10 * vel + 0.25 * acc + 0.04 * math.sin(f * 0.9) * (vel > 0.1) + seg(f, [(292, 0), (304, 0.12), (346, 0.2), (368, 0)])
        rig.set_rot(T.pose.bones["shirt_hem"], (1, 0, 0), -hem)
        T.pose.bones["shirt_hem"].keyframe_insert("rotation_quaternion", frame=f)
        # Tommy hands
        qT = heading_q(th)
        swing = 0.0
        if WALK0 < f <= WALK1:
            swing = 0.12 * math.sin(math.pi * (f - WALK0) / STEP_T)
        restT = {s: (pos + qT @ V((k * 0.26, swing * -k, 0.88 + crouch)), qT @ V((k * 0.05, 0.05, -1)), qT @ V((-k, 0, 0)))
                 for s, k in (("L", -1), ("R", 1))}
        wave = seg(f, [(296, 0.0), (306, 1.0), (326, 1.0), (334, 0.0)])
        gest = (pos + qT @ V((0.22, 0.42, 1.12 + crouch)), qT @ V((0.15, 1, 0.1)), qT @ V((0, 0, 1)))
        handT = {}
        for side in ("L", "R"):
            r = restT[side]
            if side == "R":
                r = (r[0].lerp(gest[0], wave), r[1].lerp(gest[1], wave), r[2].lerp(gest[2], wave))
            if side == "R" and f >= 338:
                g = ctrl_grab(max(f, HANDOFF))
                t = smooth((f - 338) / (HANDOFF - 338))
                r = (r[0].lerp(g[0], t), r[1].lerp(g[1], t), r[2].lerp(g[2], t))
                if f >= 360:
                    p = ctrl_grip(f, "R")
                    g = ctrl_grab(f)
                    t = smooth((f - 360) / 10)
                    r = (g[0].lerp(p[0], t), g[1].lerp(p[1], t), g[2].lerp(p[2], t))
            if side == "L" and f >= 352:
                p = ctrl_grip(f, "L")
                t = smooth((f - 352) / 16)
                r = (r[0].lerp(p[0], t), r[1].lerp(p[1], t), r[2].lerp(p[2], t))
            handT[side] = r
            key_m(Tt[f"hand.{side}"], hand_target_m(T, side, *r), f)
            cu = 0.25 + (0.65 if f >= HANDOFF - 2 else 0.0) - wave * 0.2
            if f >= 385:
                cu += 0.08 * math.sin(f * 1.3 + (0 if side == "L" else 2))     # thumbs working the controller
            rig.set_rot(T.pose.bones[f"fingers.{side}"], (0, 1, 0), (1 if side == "R" else -1) * cu * 1.3)
            T.pose.bones[f"fingers.{side}"].keyframe_insert("rotation_quaternion", frame=f)
        gam_head = GAMER_POS + V((0, 0.05, 1.18))
        tl = seg(f, [(1, pos + qT @ V((0, 3, 1.6))), (WALK1, pos + qT @ V((0, 3, 1.6))), (WALK1 + 4, gam_head), (356, gam_head),
                     (358, ctrl_m(358).translation), (363, SCREEN)])
        key_m(Tt["look"], Matrix.Translation(tl), f)
        # jaw: restrained syllables
        jaw = 0.0
        for a, b, n in ((d["f0"], d["f0"] + d["frames"], d["syll"]) for d in C.DIALOGUE):
            if a <= f <= b:
                jaw = 0.10 * abs(math.sin(math.pi * n * (f - a) / (b - a)))
        rig.set_rot(T.pose.bones["jaw"], (1, 0, 0), -jaw)
        T.pose.bones["jaw"].keyframe_insert("rotation_quaternion", frame=f)
        # ---------------- props
        key_m(hw["tray"], Matrix.Translation(tray_pos(f)), f)
        key_m(hw["disc"], disc_m(f), f)
        key_m(hw["controller"], ctrl_m(f), f)
        # ---------------- portal leaves, car, fog
        ang = math.radians(100) * smooth((f - 199) / 16)
        hinges["W"].rotation_euler = (0, 0, ang)
        hinges["E"].rotation_euler = (0, 0, -ang)
        for h in hinges.values():
            h.keyframe_insert("rotation_euler", frame=f)
        yfront = seg(f, [(208, C.CAR["start_front_y"]), (238, C.CAR["stop_front_y"])])
        yc = yfront + C.CAR["len"] / 2
        car.location = (C.CAR["x"], yc, 0)
        car.keyframe_insert("location", frame=f)
        dist = C.CAR["start_front_y"] - yfront
        for w in wheels:
            w.rotation_euler = (dist / C.CAR["wheel_r"], 0, 0)
            w.keyframe_insert("rotation_euler", frame=f)
        log["frames"][f] = dict(car_front_y=round(yfront, 4), tray_y=round(tray_pos(f).y, 4), tommy=[round(v, 4) for v in pos],
                                tommy_feet={s: [round(v, 4) for v in feet[s][0]] for s in feet}, hinge_deg=round(math.degrees(ang), 2))
    return log


def key_fx(sc, hw, fog_portal, fog_trans, crt_glow):
    vals = hw["screen_vals"]
    for f in range(1, F + 1):
        p = seg(f, [(1, 0.5), (146, 0.5), (147, 0.0), (149, 0.0), (151, 2.2), (152, 0.6), (154, 1.6), (160, 1.3)])
        vals["power"].outputs[0].default_value = p
        vals["power"].outputs[0].keyframe_insert("default_value", frame=f)
        vals["title_mix"].outputs[0].default_value = 1.0 if f >= 149 else 0.0
        vals["title_mix"].outputs[0].keyframe_insert("default_value", frame=f)
        vals["game_mix"].outputs[0].default_value = 1.0 if f >= 385 else 0.0
        vals["game_mix"].outputs[0].keyframe_insert("default_value", frame=f)
        L = crt_glow.data
        L.energy = 4.0 + 14.0 * min(p, 1.6) if f >= 147 else 6.0
        L.color = (0.13, 0.79, 0.81) if f < 147 else ((0.96, 0.29, 0.65) if f < 385 else (0.53, 0.34, 0.66))
        L.keyframe_insert("energy", frame=f)
        L.keyframe_insert("color", frame=f)
        d = seg(f, [(193, 0.0), (199, 0.0), (210, 0.06), (240, 0.03), (300, 0.02)])
        fog_portal.inputs["Density"].default_value = d
        fog_portal.inputs["Density"].keyframe_insert("default_value", frame=f)
        e = seg(f, [(193, 0.0), (197, 0.0), (206, 0.6), (240, 0.15), (300, 0.08)])
        fog_portal.inputs["Emission Strength"].default_value = e
        fog_portal.inputs["Emission Strength"].keyframe_insert("default_value", frame=f)
        dt = seg(f, [(450, 0.0), (466, 0.35)]) if f < C.SLATE_F else 0.0
        fog_trans.inputs["Density"].default_value = dt
        fog_trans.inputs["Density"].keyframe_insert("default_value", frame=f)
        fog_trans.inputs["Emission Strength"].default_value = dt * 2.5
        fog_trans.inputs["Emission Strength"].keyframe_insert("default_value", frame=f)


# ------------------------------------------------------------------ cameras
def look_q(pos, aim, roll=0.0):
    d = (V(aim) - V(pos)).normalized()
    q = d.to_track_quat("-Z", "Y")
    return q @ Quaternion((0, 0, 1), roll)


def cameras(sc, chars):
    G, T = chars["GAMER_01"][0], chars["TOMMY_01"][0]
    coll = bpy.data.collections.get("CAMERAS") or bpy.data.collections.new("CAMERAS")
    if coll.name not in sc.collection.children:
        sc.collection.children.link(coll)
    head = lambda arm, f: (sc.frame_set(f), arm.matrix_world @ arm.pose.bones["head"].head)[1]  # noqa: E731
    tray = TRAY_OPEN
    ghead = GAMER_POS + V((0, 0.08, 1.15))
    plan = {
        "S01": [(1, V((1.75, 0.98, 1.05)), V((0.0, 1.08, 0.88)), 4.0),
                (48, V((1.75, 0.98, 1.05)) + (V((0.0, 1.08, 0.88)) - V((1.75, 0.98, 1.05))).normalized() * 0.25, V((0.0, 1.08, 0.88)), 4.0)],
        "S02": [],
        "S03": [(97, V((0.98, 1.06, 0.71)), tray + V((0.0, 0.03, 0.0)), 5.6), (144, V((0.98, 1.06, 0.71)), tray + V((0.0, 0.07, 0.0)), 5.6)],
        "S04": [(145, V((0.40, 0.88, 0.98)), SCREEN, 4.0), (192, V((0.37, 0.97, 0.97)), SCREEN, 4.0)],
        "S05": [(193, V((0.42, -0.82, 1.30)), V((-0.55, 2.6, 0.95)), 8.0), (240, V((0.42, -0.82, 1.34)), V((-0.55, 2.6, 0.98)), 8.0)],
        "S06": [(241, V((0.40, 0.05, 0.30)), V((1.0, 2.5, 1.25)), 5.6), (288, V((0.40, 0.05, 0.30)), None, 5.6)],
        "S07": [(289, V((1.62, -1.25, 1.30)), None, 4.0), (336, V((1.56, -1.15, 1.30)), None, 4.0)],
        "S08": [(337, V((1.75, -1.10, 1.18)), None, 4.0), (384, V((1.75, -1.10, 1.18)), None, 4.0)],
        "S09": [(385, V((0.30, 0.02, 1.22)), SCREEN + V((0, 0, 0.02)), 5.6), (432, V((0.28, 0.17, 1.20)), SCREEN + V((0, 0, 0.02)), 5.6)],
        "S10": [(433, V((0.10, 1.00, 0.93)), SCREEN, 4.0), (446, V((0.30, 0.62, 1.50)), SCREEN, 5.6),
                (468, V((0.55, -1.55, 2.30)), V((-0.2, 3.5, 1.0)), 8.0), (480, V((0.55, -1.55, 2.30)), V((-0.2, 3.5, 1.0)), 8.0)],
    }
    cams, csv = {}, []
    for s in C.SHOTS:
        cd = bpy.data.cameras.new(f"CAM_{s['id']}")
        cd.lens, cd.sensor_width = s["lens"], 36
        cd.clip_start, cd.clip_end = 0.02, 600
        cd.dof.use_dof = True
        cam = bpy.data.objects.new(f"CAM_{s['id']}", cd)
        coll.objects.link(cam)
        cam.rotation_mode = "QUATERNION"
        for f in range(s["f0"], s["f1"] + 1):
            if s["id"] == "S02":
                dm = disc_m(f)
                c0 = dm.translation
                n = dm.to_3x3().col[2]
                base = (n + V((0.55, 0.0, 0.0))).normalized()
                ang = math.radians(-7.5 + 15 * (f - s["f0"]) / (s["f1"] - s["f0"]))       # 15 degree arc
                pos = c0 + (Quaternion((0, 0, 1), ang) @ base) * 0.52
                aim, fst = c0, 4.0
            else:
                pos = seg(f, [(k[0], k[1]) for k in plan[s["id"]]])
                aim = None
                for (fa, pa, aa, _), (fb, pb, ab, _) in zip(plan[s["id"]], plan[s["id"]][1:]):
                    if fa <= f <= fb and aa is not None and ab is not None:
                        aim = aa.lerp(ab, smooth((f - fa) / (fb - fa)))
                if aim is None and plan[s["id"]][0][2] is not None and f <= plan[s["id"]][0][0]:
                    aim = plan[s["id"]][0][2]
                fst = plan[s["id"]][0][3]
                if s["id"] == "S06":
                    th = head(T, f)
                    base_aim = V((1.0, 2.5, 1.25))
                    tilt = smooth((f - 241) / 47) * math.radians(12)
                    d = (base_aim - pos)
                    horiz = V((d.x, d.y, 0)).normalized()
                    pitch0 = math.atan2(d.z, V((d.x, d.y)).length)
                    aim = pos + horiz * math.cos(pitch0 + tilt) * 2 + V((0, 0, math.sin(pitch0 + tilt) * 2))
                    # pan to keep Tommy framed as he walks in
                    tom = V((th.x, th.y, 0))
                    hd = (tom - V((pos.x, pos.y, 0))).normalized()
                    aim = pos + (hd * math.cos(pitch0 + tilt) + V((0, 0, math.sin(pitch0 + tilt)))) * 2
                if s["id"] in ("S07", "S08"):
                    gh, th = head(G, f), head(T, f)
                    aim = gh.lerp(th, 0.5) + V((0, 0, -0.08 if s["id"] == "S07" else -0.12))
                if s["id"] == "S06" and f == s["f0"]:
                    pass
            cam.location = pos
            cam.rotation_quaternion = look_q(pos, aim)
            cam.keyframe_insert("location", frame=f)
            cam.keyframe_insert("rotation_quaternion", frame=f)
            focus = {"S01": ghead, "S02": None, "S03": tray, "S04": SCREEN, "S05": V((-0.5, 2.0, 0.8)), "S06": None, "S07": None,
                     "S08": None, "S09": SCREEN, "S10": SCREEN}[s["id"]]
            if s["id"] == "S02":
                focus = disc_m(f).translation
            if s["id"] == "S06":
                focus = head(T, f) + V((0, 0, -0.5))
            if s["id"] in ("S07", "S08"):
                focus = head(T, f) if s["id"] == "S07" else ctrl_m(f).translation
            cd.dof.focus_distance = (focus - pos).length if f < C.SLATE_F else 0.30
            cd.dof.aperture_fstop = fst if f < C.SLATE_F else 64.0
            cd.dof.keyframe_insert("focus_distance", frame=f)
            cd.dof.keyframe_insert("aperture_fstop", frame=f)
        mk = sc.timeline_markers.new(s["id"], frame=s["f0"])
        mk.camera = cam
        cams[s["id"]] = cam
    return cams


def slate(sc, cam):
    import setpieces as SP
    import mats as M
    c = SP.coll("SLATE")
    bpy.ops.mesh.primitive_plane_add(size=1)
    bg = SP.put(bpy.context.active_object, c)
    bg.name = "SLATE_black"
    bg.scale = (2, 2, 1)
    bg.data.materials.append(M.emit("slate_black", (0, 0, 0, 1), 0.0))
    bg.parent = cam
    bg.location = (0, 0, -0.30)
    t = SP.text("SLATE_text", c, "THE JOURNEY CONTINUES", (0, 0, -0.29), (0, 0, 0), 0.016, M.emit("slate_white", (0.9, 0.9, 0.9, 1), 1.0))
    t.data.font = bpy.data.fonts.load("/usr/share/fonts/opentype/inter/Inter-Bold.otf", check_existing=True)
    t.data.space_character = 1.25
    t.parent = cam
    for o in (bg, t):
        for f, h in ((1, True), (C.SLATE_F - 1, True), (C.SLATE_F, False)):
            o.hide_render = h
            o.hide_viewport = h
            o.keyframe_insert("hide_render", frame=f)
            o.keyframe_insert("hide_viewport", frame=f)
