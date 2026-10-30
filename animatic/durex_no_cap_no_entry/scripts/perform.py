"""Performances: distance-locked gait solver, per-shot character actions (NLA), props, cameras.

Every character gets one Action per shot (e.g. HERO_01_SH05) pushed as sequential NLA strips.
"""
import math
from math import sin, cos, pi, radians, degrees, asin, atan2, hypot, floor, exp
import bpy
from mathutils import Vector, Matrix, Quaternion

from common import (SHOTS, BEAT, clamp, smooth, seg, lerp, vlerp, pulse, wnoise, Rx, Ry, Rz, I3, aim_down_to,
                    heading_for, write_action, push_nla)
from cast import ROT_BONES
import environment as env

STOP = Vector((-0.25, -1.55))
MARK = env.BOUNCER_MARK
STEP_SPOT = Vector((0.30, -1.10))
HD_EAST = heading_for(1, 0)
HD_BOUNCER = heading_for(-1, 0)
L_HOOK = Vector((env.STANCHION_L.x, env.STANCHION_L.y - 0.03, env.HOOK_Z))
R_HOOK = Vector((env.STANCHION_R.x, env.STANCHION_R.y - 0.03, env.HOOK_Z))
ROPE_LEN = 0.88
CLUB_HERO = Vector((-0.6, 10.8))
SHOT_END = {s["n"]: s["end"] for s in SHOTS}
SHOT_START = {s["n"]: s["start"] for s in SHOTS}


def shot_of(f):
    for s in SHOTS:
        if s["start"] <= f <= s["end"]:
            return s["n"]
    return 10


# ---------------------------------------------------------------- pose container
class Pose:
    __slots__ = ("x", "y", "hd", "drop", "J", "chest_s", "eye", "brow", "ik")

    def __init__(self, x=0.0, y=0.0, hd=0.0):
        self.x, self.y, self.hd = x, y, hd
        self.drop = 0.0
        self.J = {}
        self.chest_s = 1.0
        self.eye = [0.0, 0.0]
        self.brow = [0.0, 0.0]
        self.ik = {}

    def pre(self, bone, M):
        self.J[bone] = M @ self.J.get(bone, I3())

    def blend_to(self, targets, w):
        if w <= 0:
            return
        for b, T in targets.items():
            q0 = self.J.get(b, I3()).to_quaternion()
            q1 = T.to_quaternion()
            if q0.dot(q1) < 0:
                q1.negate()
            self.J[b] = q0.slerp(q1, clamp(w)).to_matrix()


def rest_arms(p, style="relaxed"):
    if style == "clasp":
        p.J["upper_arm.L"] = Rx(-14) @ Rz(-48)
        p.J["upper_arm.R"] = Rx(-14) @ Rz(48)
        p.J["forearm.L"] = Rx(-62)
        p.J["forearm.R"] = Rx(-62)
    else:
        p.J["upper_arm.L"] = Ry(-6)
        p.J["upper_arm.R"] = Ry(6)
        p.J["forearm.L"] = Rx(-10)
        p.J["forearm.R"] = Rx(-10)


def breathe(p, f, seed, depth=0.012):
    p.chest_s = 1.0 + depth * sin(2 * pi * f / (84 + seed % 17) + seed)


def idle(ch, x, y, hd, f, seed, style="relaxed", amp=1.0):
    p = Pose(x, y, hd)
    rest_arms(p, style)
    breathe(p, f, seed)
    tilt = 1.3 * amp * wnoise(f, seed, (0.012, 0.027), (1.0, 0.35))
    p.pre("hips", Ry(tilt))
    p.pre("thigh.L", Ry(-tilt))
    p.pre("thigh.R", Ry(-tilt))
    p.pre("spine", Ry(-tilt * 0.6))
    p.pre("head", Rz(3.0 * amp * wnoise(f, seed + 3, (0.008, 0.019), (1.0, 0.4))) @ Rx(1.5 * amp * wnoise(f, seed + 5, (0.01,), (1.0,))))
    return p


def look(p, ch, target, w=1.0, eyes=True):
    if w <= 0:
        return
    hz = ch.head_c.z + p.drop
    d = Vector(target) - Vector((p.x, p.y, hz))
    c, s = cos(-p.hd), sin(-p.hd)
    lx = d.x * c - d.y * s
    ly = d.x * s + d.y * c
    yaw = clamp(degrees(atan2(lx, -ly)), -75, 75) * w
    pitch = clamp(degrees(atan2(d.z, hypot(lx, ly))), -35, 30) * w
    p.pre("neck", Rz(yaw * 0.35) @ Rx(-pitch * 0.3))
    p.pre("head", Rz(yaw * 0.65) @ Rx(-pitch * 0.7))
    if eyes:
        p.eye[1] += clamp(pitch / 30.0, -1, 1) * 0.0015 * w


def head_world_guess(ch, p):
    return Vector((p.x, p.y, ch.head_c.z + 0.012 * ch.s + p.drop))


# ---------------------------------------------------------------- path + gait
class Path:
    def __init__(self, pts, iters=3):
        P = [Vector((q[0], q[1])) for q in pts]
        for _ in range(iters if len(P) > 2 else 0):
            Q = [P[0]]
            for a, b in zip(P[:-1], P[1:]):
                Q += [a.lerp(b, 0.25), a.lerp(b, 0.75)]
            Q.append(P[-1])
            P = Q
        self.P = P
        self.cum = [0.0]
        for a, b in zip(P[:-1], P[1:]):
            self.cum.append(self.cum[-1] + (b - a).length)
        self.length = self.cum[-1]

    def at(self, d):
        d = clamp(d, 0.0, self.length)
        for i in range(len(self.P) - 1):
            if d <= self.cum[i + 1] or i == len(self.P) - 2:
                a, b = self.P[i], self.P[i + 1]
                segl = (self.cum[i + 1] - self.cum[i]) or 1e-6
                t = (d - self.cum[i]) / segl
                return a.lerp(b, t), (b - a).normalized()
        return self.P[-1], (self.P[-1] - self.P[-2]).normalized()


def trap(u, a1, a2):
    u = clamp(u)
    vmax = 1.0 / (1.0 - a1 / 2 - a2 / 2)
    if a1 > 0 and u < a1:
        return vmax * u * u / (2 * a1)
    if a2 > 0 and u > 1 - a2:
        return 1.0 - vmax * (1 - u) ** 2 / (2 * a2)
    return vmax * (a1 / 2 + (u - a1))


class Walk:
    """Footplant-locked walk: stance-foot angle is solved from root travel, so feet do not slide."""

    def __init__(self, ch, pts, f0, f1=None, speed=1.3, start_rest=True, end_rest=True, accel=10,
                 face=None, hd0=None, turn=8, stride=0.40, knee=50):
        self.ch = ch
        self.path = Path(pts)
        self.D = self.path.length
        self.f0 = f0
        if f1 is None:
            f1 = f0 + int(round(self.D / speed * 24 + (accel if start_rest else 0) / 2 + (accel if end_rest else 0) / 2))
        self.f1 = f1
        n = max(1, f1 - f0)
        self.a1 = min(0.45, accel / n) if start_rest else 0.0
        self.a2 = min(0.45, accel / n) if end_rest else 0.0
        s_nom = stride * ch.H
        if start_rest and end_rest:
            N = max(1, int(round(self.D / s_nom)))
            self.s = self.D / N
        else:
            self.s = s_nom
        self.start_rest, self.end_rest = start_rest, end_rest
        self.face, self.hd0, self.turn = face, hd0, turn
        self.knee = knee

    def dist(self, f):
        return self.D * trap((f - self.f0) / (self.f1 - self.f0), self.a1, self.a2)

    def active(self, f):
        return self.f0 <= f <= self.f1

    def apply(self, p, f):
        ch = self.ch
        dd = self.dist(f)
        pos, tan = self.path.at(dd)
        p.x, p.y = pos.x, pos.y
        hd_path = atan2(tan.y, tan.x) + pi / 2
        sign = 1.0
        if self.face is not None:
            p.hd = self.face
            fwd = Vector((sin(self.face), -cos(self.face)))
            sign = 1.0 if fwd.dot(tan) >= 0 else -1.0
        else:
            p.hd = hd_path
            if self.hd0 is not None:
                w = smooth((f - self.f0) / max(1, self.turn))
                dh = (hd_path - self.hd0 + pi) % (2 * pi) - pi
                p.hd = self.hd0 + dh * w
        s, L = self.s, ch.L
        ph = dd / s + (0.5 if self.start_rest else 0.0)
        n = int(floor(ph))
        u = ph - n
        stance = "L" if n % 2 == 0 else "R"
        swing = "R" if stance == "L" else "L"
        o_st = (s / 2 - u * s) * sign
        ph_end = self.D / s + 0.5
        if self.start_rest and ph < 1.0:
            v = (u - 0.5) * 2
            o_sw = s / 2 * smooth(v) * sign
            k = self.knee * 0.8 * sin(pi * clamp(v))
        elif self.end_rest and ph > ph_end - 1.0 + 1e-9 and u <= 0.5 + 1e-9:
            v = u * 2
            o_sw = (-s / 2 + s / 2 * smooth(v)) * sign
            k = self.knee * 0.8 * sin(pi * clamp(v))
        else:
            o_sw = (-s / 2 + (0.5 - 0.5 * cos(pi * u)) * s) * sign
            k = self.knee * sin(pi * u)
        a_st = asin(clamp(o_st / L, -0.95, 0.95))
        half = radians(k) / 2
        t_sw = half + asin(clamp(o_sw / (L * cos(half)), -0.95, 0.95))
        for side, a, kk in ((stance, a_st, 0.0), (swing, t_sw, k)):
            ad = degrees(a)
            p.J["thigh." + side] = Rx(-ad) @ p.J.get("thigh." + side, I3())
            p.J["shin." + side] = Rx(kk)
            p.J["foot." + side] = Rx(ad - kk)
        p.drop = L * (cos(a_st) - 1.0)
        o = {stance: o_st, swing: o_sw}
        nl = o["L"] / (s / 2) * sign
        amp = 1.0 if (f > self.f0 + 4) else smooth((f - self.f0) / 4)
        if self.end_rest:
            amp *= smooth((self.f1 - f) / 6)
        armL = 15 * (o["R"] / (s / 2) * sign) * amp
        armR = 15 * nl * amp
        p.pre("upper_arm.L", Rx(-armL))
        p.pre("upper_arm.R", Rx(-armR))
        p.pre("forearm.L", Rx(-6 * max(0.0, armL / 15)))
        p.pre("forearm.R", Rx(-6 * max(0.0, armR / 15)))
        p.pre("hips", Rz(-4 * nl * amp))
        p.pre("chest", Rz(5 * nl * amp))
        p.pre("spine", Rx(3 * amp))
        return p


# ---------------------------------------------------------------- the cast's direction
class Director:
    def __init__(self, chars, props):
        self.c = chars
        self.props = props
        C = chars
        H = C["HERO_01"]
        B = C["BOUNCER_01"]
        G1, G2, G3, G4 = (C["GUEST_0%d" % i] for i in range(1, 5))
        self.w = {
            "H1": Walk(H, [(-6.0, -0.72), (-3.85, -0.72)], 1, 73, start_rest=False, end_rest=False, stride=0.42),
            "H5": Walk(H, [(-2.75, -1.3), STOP], 289, 337),
            "H7": Walk(H, [STOP, (0.05, -1.0), (0.05, 0.25), (0.05, 4.2)], 451, None, speed=1.65, end_rest=False,
                       hd0=HD_EAST, turn=10),
            "G1a": Walk(G1, [(-1.1, -1.85), STOP], 73, 96),
            "G1b": Walk(G1, [STOP, (-0.5, -2.05), (-1.4, -2.5), (-3.0, -2.55)], 120, None, speed=1.35, end_rest=False,
                        hd0=HD_EAST, turn=10),
            "G2a": Walk(G2, [(-1.4, -1.6), STOP], 145, 166),
            "G2b": Walk(G2, [STOP, (-0.55, -2.15), (-1.5, -2.45), (-4.6, -2.5)], 182, None, speed=1.6, end_rest=False,
                        hd0=HD_EAST, turn=10),
            "G3a": Walk(G3, [(-1.5, -1.6), STOP], 217, 249, knee=40, stride=0.34),
            "G4a": Walk(G4, [(-1.4, -1.6), STOP], 577, 596),
            "B7f": Walk(B, [MARK, STEP_SPOT], 433, 443, face=HD_BOUNCER, accel=4, stride=0.36, knee=70),
            "B7b": Walk(B, [STEP_SPOT, MARK], 447, 461, face=HD_BOUNCER, accel=4, stride=0.36, knee=70),
            "B9f": Walk(B, [MARK, STEP_SPOT], 613, 623, face=HD_BOUNCER, accel=4, stride=0.36, knee=70),
        }
        self.queue = {
            "GUEST_01": {1: (-1.1, -1.85)},
            "GUEST_02": {1: (-2.05, -1.85), 2: (-2.05, -1.85)},
            "GUEST_03": {1: (-3.0, -1.85), 2: (-3.0, -1.85), 3: (-2.3, -1.85)},
            "GUEST_04": {1: (-3.95, -1.85), 2: (-3.95, -1.85), 3: (-3.25, -1.85), 4: (-2.65, -1.85),
                         5: (-3.4, -1.95), 6: (-3.4, -1.95), 7: (-3.4, -1.95), 8: (-3.4, -1.95)},
        }
        self.extras = {}
        spots = [(-2.3, 9.6, 40), (-1.9, 12.4, 160), (-0.2, 13.3, 200), (1.4, 10.2, -60), (-3.6, 12.1, 120), (0.2, 11.7, 220)]
        for i, (x, y, deg) in enumerate(spots, 1):
            self.extras["CLUB_EXTRA_%02d" % i] = (x, y, radians(deg), i * 7.3)

    # ---------------- positions of other actors used for eyelines
    def head_of(self, name, f):
        ch = self.c[name]
        p = self.pose(name, f, eyelines=False)
        return head_world_guess(ch, p)

    def pose(self, name, f, eyelines=True):
        fn = getattr(self, "p_" + name.lower(), None)
        if fn is None:
            return self.p_extra(name, f)
        return fn(f, eyelines)

    # ---------------- HERO_01
    def p_hero_01(self, f, eyes=True):
        ch = self.c["HERO_01"]
        n = shot_of(f)
        w = self.w
        if n == 1:
            p = idle(ch, 0, 0, 0, f, 11, amp=0.5)
            w["H1"].apply(p, f)
            if eyes:
                look(p, ch, (0.9, -0.95, 1.75), 0.35)
            return p
        if n in (2, 3, 4):
            return idle(ch, -16.0, -0.7, HD_EAST, f, 11, amp=0.0)
        if n == 5:
            p = idle(ch, 0, 0, 0, f, 11, amp=0.6 * seg(f, 337, 345))
            w["H5"].apply(p, f)
            shift = pulse(f, 337, 344, 356, 362)
            p.pre("hips", Ry(-2.2 * shift))
            p.pre("thigh.L", Ry(2.2 * shift))
            p.pre("thigh.R", Ry(2.2 * shift))
            p.pre("spine", Ry(1.6 * shift))
            p.ik["IK_R_BRIM"] = pulse(f, 341, 349, 354, 362)
            if eyes:
                look(p, ch, self.head_of("BOUNCER_01", f), 0.8)
            return p
        if n == 6:
            p = idle(ch, STOP.x, STOP.y, HD_EAST, f, 11, amp=0.25)
            if eyes:
                look(p, ch, self.head_of("BOUNCER_01", f) + Vector((0, 0, 0.02)), 1.0)
            return p
        if n == 7:
            p = idle(ch, STOP.x, STOP.y, HD_EAST, f, 11, amp=0.25)
            if f >= w["H7"].f0:
                w["H7"].apply(p, f)
                if eyes:
                    look(p, ch, Vector((0.05, 6.0, 1.6)), 0.6 * seg(f, 455, 470))
            elif eyes:
                look(p, ch, self.head_of("BOUNCER_01", f), 0.9)
            return p
        if n == 8:
            return idle(ch, 0.05, 3.6, heading_for(0, 1), f, 11, amp=0.0)
        hd = heading_for(0.85, -1.55) + radians(24)
        p = idle(ch, CLUB_HERO.x, CLUB_HERO.y, hd, f, 11, amp=0.3)
        if eyes and n == 10:
            look(p, ch, Vector((0.9, 8.6, 1.62)), 0.7)
        return p

    # ---------------- BOUNCER_01 (always on his mark at entrance-right, except one short step to the rope)
    def p_bouncer_01(self, f, eyes=True):
        ch = self.c["BOUNCER_01"]
        n = shot_of(f)
        w = self.w
        p = idle(ch, MARK.x, MARK.y, HD_BOUNCER, f, 23, style="clasp", amp=0.35)
        block = {"upper_arm.L": aim_down_to((0.42, -0.9, 0.03)), "forearm.L": Rx(-4), "hand.L": I3()}
        tgt = None
        if n == 1:
            tgt = Vector((-2.0, -1.7, 1.6))
        elif n == 2:
            p.blend_to(block, pulse(f, 89, 97, 116, 126))
            tgt = self.head_of("GUEST_01", f)
        elif n == 3:
            tgt = self.head_of("GUEST_02", f)
            shake = 9.0 * sin(2 * pi * (f - 169) / 12) if 169 <= f <= 181 else 0.0
            p.pre("head", Rz(shake))
        elif n == 4:
            tgt = self.head_of("GUEST_03", f) + Vector((0, 0, 0.25 * seg(f, 230, 250)))
            p.brow[0] = 0.0075 * pulse(f, 249, 254, 400, 410)
            point = {"upper_arm.L": aim_down_to((0.66, -0.74, -0.1)), "forearm.L": Rx(-3), "hand.L": I3()}
            p.blend_to(point, pulse(f, 261, 268, 400, 410))
        elif n == 5:
            tgt = self.head_of("HERO_01", f)
        elif n == 6:
            hero = self.head_of("HERO_01", f)
            cap_pt = hero + Vector((0.12, 0, 0.11))
            up = pulse(f, 361, 366, 405, 411)
            tgt = hero.lerp(cap_pt, up)
            p.eye[1] += 0.0028 * up
            sweep = pulse(f, 372, 374, 384, 386)
            p.eye[0] += 0.0028 * sin(pi * clamp((f - 372) / 12.0)) * sweep - 0.0012 * sweep
            p.pre("head", Rx(6.0 * pulse(f, 421, 424, 425, 431)))
        elif n == 7:
            if f <= 446:
                w["B7f"].apply(p, f)
            else:
                w["B7b"].apply(p, f)
            lean = pulse(f, 437, 444, 448, 458)
            p.pre("spine", Rx(16 * lean))
            p.pre("chest", Rx(8 * lean))
            p.ik["IK_R_ROPE"] = seg(f, 437, 445)
            tgt = L_HOOK if f < 452 else self.head_of("HERO_01", f)
            p.blend_to({"upper_arm.R": Ry(6), "forearm.R": Rx(-20)}, seg(f, 434, 440))
        elif n in (8, 10):
            tgt = None
        elif n == 9:
            p.blend_to(block, pulse(f, 583, 589, 596, 602))
            turn = pulse(f, 598, 604, 609, 616)
            p.pre("spine", Rz(-24 * turn))
            p.pre("chest", Rz(-22 * turn))
            p.ik["IK_R_CAP"] = pulse(f, 600, 607, 625, 631)
            if f >= 613:
                w["B9f"].apply(p, f)
            lean = pulse(f, 634, 641, 700, 710)
            p.pre("spine", Rx(16 * lean))
            p.pre("chest", Rx(8 * lean))
            p.blend_to({"upper_arm.R": Ry(6), "forearm.R": Rx(-20)}, seg(f, 626, 632))
            p.ik["IK_R_ROPE"] = seg(f, 633, 641)
            g4 = self.head_of("GUEST_04", f)
            shelf = env.SHELF_POS + Vector((0, 0, 0.05))
            tgt = g4.lerp(shelf, turn) if f < 634 else L_HOOK
        if eyes and tgt is not None:
            look(p, ch, tgt, 1.0)
        return p

    # ---------------- guests
    def _queue_or_off(self, name, ch, f, seed, n):
        spot = self.queue.get(name, {}).get(n)
        if spot:
            p = idle(ch, spot[0], spot[1], HD_EAST, f, seed, amp=0.8)
            if n in (1, 2, 3, 4, 5, 6, 7):
                look(p, ch, Vector((0.95, -0.95, 1.75)) + Vector((0, 0, 0.0)), 0.5 + 0.3 * wnoise(f, seed + 9, (0.007,), (1.0,)))
            return p
        return idle(ch, -14.0 - (seed % 7) * 1.5, -2.4, HD_EAST, f, seed, amp=0.0)

    def p_guest_01(self, f, eyes=True):
        ch = self.c["GUEST_01"]
        n = shot_of(f)
        if n != 2:
            return self._queue_or_off("GUEST_01", ch, f, 31, n)
        p = idle(ch, 0, 0, HD_EAST, f, 31, amp=0.4)
        if f < 120:
            self.w["G1a"].apply(p, f)
        else:
            self.w["G1b"].apply(p, f)
        down = pulse(f, 102, 110, 122, 134)
        if eyes:
            look(p, ch, self.head_of("BOUNCER_01", f), 1.0 - down)
        p.pre("head", Rx(20 * down))
        p.pre("neck", Rx(6 * down))
        p.eye[1] -= 0.002 * down
        return p

    def p_guest_02(self, f, eyes=True):
        ch = self.c["GUEST_02"]
        n = shot_of(f)
        if n != 3:
            return self._queue_or_off("GUEST_02", ch, f, 37, n)
        p = idle(ch, 0, 0, HD_EAST, f, 37, amp=0.4)
        if f < 182:
            self.w["G2a"].apply(p, f)
            if eyes:
                look(p, ch, self.head_of("BOUNCER_01", f), 1.0)
        else:
            self.w["G2b"].apply(p, f)
        return p

    def p_guest_03(self, f, eyes=True):
        ch = self.c["GUEST_03"]
        n = shot_of(f)
        if n != 4:
            return self._queue_or_off("GUEST_03", ch, f, 41, n)
        p = idle(ch, 0, 0, HD_EAST, f, 41, amp=0.6)
        self.w["G3a"].apply(p, f)
        bal = sin(2 * pi * f / 26.0)
        arms = 30 + 8 * sin(2 * pi * f / 19.0)
        p.pre("upper_arm.L", Ry(-arms))
        p.pre("upper_arm.R", Ry(arms))
        p.pre("forearm.L", Rx(-25))
        p.pre("forearm.R", Rx(-25))
        p.pre("spine", Ry(4.5 * bal))
        p.pre("chest", Ry(2.5 * bal))
        p.pre("neck", Ry(-5 * bal))
        p.pre("hips", Ry(-1.5 * bal))
        p.pre("thigh.L", Ry(1.5 * bal))
        p.pre("thigh.R", Ry(1.5 * bal))
        if eyes:
            look(p, ch, self.head_of("BOUNCER_01", f), 0.7)
        return p

    def p_guest_04(self, f, eyes=True):
        ch = self.c["GUEST_04"]
        n = shot_of(f)
        if n != 9:
            return self._queue_or_off("GUEST_04", ch, f, 43, n)
        p = idle(ch, 0, 0, HD_EAST, f, 43, amp=0.35 * (1 - seg(f, 615, 622)))
        self.w["G4a"].apply(p, f)
        p.ik["IK_L_CAP"] = pulse(f, 619, 625, 637, 643)
        p.ik["IK_R_CAP"] = pulse(f, 619, 625, 637, 643)
        if eyes and f < 615:
            look(p, ch, self.head_of("BOUNCER_01", f), 1.0)
        elif eyes:
            look(p, ch, Vector((0.6, -1.25, 1.62)), 1.0)
        return p

    def p_extra(self, name, f):
        ch = self.c[name]
        x, y, hd, seed = self.extras[name]
        p = Pose(x, y, hd)
        rest_arms(p)
        breathe(p, f, int(seed))
        off = (seed * 3.1) % BEAT
        half = int(seed) % 3 == 0
        ph = 2 * pi * (f + off) / (BEAT * (2 if half else 1))
        A = 7 + (seed % 5)
        a = A * (0.5 - 0.5 * cos(ph))
        for side in ("L", "R"):
            p.J["thigh." + side] = Rx(-a)
            p.J["shin." + side] = Rx(2 * a)
            p.J["foot." + side] = Rx(-a)
        p.drop = ch.L / 2 * 2 * (cos(radians(a)) - 1)
        sway = 4 * sin(ph / 2 + seed)
        p.pre("hips", Ry(sway))
        p.pre("thigh.L", Ry(-sway))
        p.pre("thigh.R", Ry(-sway))
        p.pre("spine", Rx(3) @ Ry(-sway * 0.7))
        p.pre("chest", Rz(7 * sin(ph / 2 + seed * 0.7)))
        sw = sin(ph / 2 + seed)
        p.J["upper_arm.L"] = Rx(-(22 + 14 * sw)) @ Ry(-12)
        p.J["upper_arm.R"] = Rx(-(22 - 14 * sw)) @ Ry(12)
        p.J["forearm.L"] = Rx(-(75 + 15 * sin(ph)))
        p.J["forearm.R"] = Rx(-(75 + 15 * sin(ph + 1)))
        p.pre("head", Rx(4 * (0.5 - 0.5 * cos(ph))) @ Rz(5 * wnoise(f, seed, (0.01,), (1.0,))))
        return p


# ---------------------------------------------------------------- baking to actions / NLA
def bake_character(ch, director, active_shots):
    acts = []
    prev_q = {}
    prev_hd = None
    for s in SHOTS:
        n, f0, f1 = s["n"], s["start"], s["end"]
        step = 1 if n in active_shots else (f1 - f0)
        frames = list(range(f0, f1 + 1, step))
        if frames[-1] != f1:
            frames.append(f1)
        ch_ = {}

        def put(path, idx, f, v):
            ch_.setdefault((path, idx), []).append((f, v))

        for f in frames:
            p = director.pose(ch.name, f)
            hd = p.hd
            if prev_hd is not None:
                hd = prev_hd + ((hd - prev_hd + pi) % (2 * pi) - pi)
            prev_hd = hd
            put("location", 0, f, p.x)
            put("location", 1, f, p.y)
            put("location", 2, f, 0.0)
            put("rotation_euler", 2, f, hd)
            for b in ROT_BONES:
                q = ch.local_quat(b, p.J.get(b, I3()))
                if b in prev_q and prev_q[b].dot(q) < 0:
                    q.negate()
                prev_q[b] = q
                for i in range(4):
                    put('pose.bones["%s"].rotation_quaternion' % b, i, f, q[i])
            hv = ch.local_vec("hips", (0, 0, p.drop))
            for i in range(3):
                put('pose.bones["hips"].location', i, f, hv[i])
            put('pose.bones["chest"].scale', 0, f, p.chest_s)
            put('pose.bones["chest"].scale', 2, f, p.chest_s)
            ev = ch.local_vec("eyes", (p.eye[0], 0, p.eye[1]))
            for i in range(3):
                put('pose.bones["eyes"].location', i, f, ev[i])
            for k, side in enumerate(("L", "R")):
                bv = ch.local_vec("brow." + side, (0, 0, p.brow[k]))
                for i in range(3):
                    put('pose.bones["brow.%s"].location' % side, i, f, bv[i])
            for c in ch.arm.pose.bones["hand.R"].constraints:
                put('pose.bones["hand.R"].constraints["%s"].influence' % c.name, 0, f, p.ik.get(c.name, 0.0))
            for c in ch.arm.pose.bones["hand.L"].constraints:
                put('pose.bones["hand.L"].constraints["%s"].influence' % c.name, 0, f, p.ik.get(c.name, 0.0))
        act = write_action(None, "%s_SH%02d" % (ch.name, n), ch_)
        act["shot"] = n
        act["shot_frames"] = (f0, f1)
        acts.append((f0, act))
    push_nla(ch.arm, acts)


# ---------------------------------------------------------------- props
def rope_points(A, B, n=16):
    A, B = Vector(A), Vector(B)
    d = (B - A).length
    extra = max(0.0, ROPE_LEN - d)
    sag = math.sqrt(3 * max(d, 1e-4) * extra / 8)
    u_shape = extra / 2
    k = smooth(1 - d / (0.6 * ROPE_LEN))
    sag = lerp(sag, max(sag, u_shape), k)
    return [A.lerp(B, t) - Vector((0, 0, sag * 4 * t * (1 - t))) for t in (i / (n - 1) for i in range(n))]


def rope_left_end(director, f):
    n = shot_of(f)
    B = director.c["BOUNCER_01"]
    if n < 7:
        return L_HOOK.copy()
    if n == 7 or n == 8 or n == 10:
        if n == 7 and f < 445:
            return L_HOOK.copy()
        if n in (8, 10):
            f = 504
        p = director.pose("BOUNCER_01", f, eyelines=False)
        root = Vector((p.x, p.y, 0))
        off_unhook = L_HOOK - Vector((STEP_SPOT.x, STEP_SPOT.y, 0))
        off_hold = Vector((-0.3, 0.15, 0.92))
        lift = Vector((0, 0, 0.05)) * seg(f, 445, 449)
        return root + off_unhook.lerp(off_hold, seg(f, 447, 463)) + lift
    if f < 643:
        return L_HOOK.copy()
    return L_HOOK + Vector((0.07, -0.02, 0.06)) * seg(f, 643, 648)


def animate_rope(director, rope, hooks, grip):
    ch = {}
    endL = {}
    const = set(SHOT_END.values())
    for f in range(1, 721):
        A = rope_left_end(director, f)
        endL[f] = A
        pts = rope_points(A, R_HOOK)
        for i, p in enumerate(pts):
            for k in range(3):
                ch.setdefault(('splines[0].points[%d].co' % i, k), []).append((f, p[k]))
            ch.setdefault(('splines[0].points[%d].co' % i, 3), []).append((f, 1.0))
    write_action(rope.data, "VELVET_ROPE_SH07_SH09", ch, constant_frames=const)
    hl = {}
    for f, A in endL.items():
        for k in range(3):
            hl.setdefault(("location", k), []).append((f, A[k]))
    write_action(hooks[0], "ROPE_HOOK_END_LEFT_SH07_SH09", hl, constant_frames=const)
    hooks[1].location = R_HOOK
    gl = {}
    for f, A in endL.items():
        g = A + Vector((0.0, 0.0, 0.035))
        for k in range(3):
            gl.setdefault(("location", k), []).append((f, g[k]))
    write_action(grip, "BOUNCER_ROPE_GRIP_SH07_SH09", gl, constant_frames=const)
    return endL


def head_attach_world(ch):
    pb = ch.arm.pose.bones["head"]
    b = ch.arm.data.bones["head"]
    return ch.arm.matrix_world @ pb.matrix @ Matrix.Translation((0, b.length, 0)) @ ch.bone_attach_matrix("head").inverted()


def mat_from(loc, rot_z, tilt_x=0.0, scale=1.0):
    return Matrix.Translation(loc) @ Matrix.Rotation(rot_z, 4, "Z") @ Matrix.Rotation(radians(tilt_x), 4, "X") @ \
        Matrix.Diagonal((scale, scale, scale, 1.0))


def animate_gift_cap(scene, gift, g4):
    """Folded-cap substitute: the SAME cap asset rests on the shelf, is handed over and seated on GUEST_04."""
    sc = g4.cap_offset().to_scale()[0]
    shelf = mat_from(env.SHELF_POS + Vector((0, -0.005, 0.016)), 0.0, -5, sc)
    lifted = mat_from(env.SHELF_POS + Vector((-0.12, -0.25, 0.1)), radians(40), 0, sc)
    hand = mat_from(Vector((0.05, -1.33, 1.25)), HD_EAST, 0, sc)
    scene.frame_set(637)
    seated = head_attach_world(g4) @ g4.cap_offset()
    above = seated.copy()
    above.translation += Vector((0.02, 0, 0.12))
    keys = [(608, shelf), (614, lifted), (625, hand), (632, above), (637, seated)]
    chans = {}
    gift.rotation_mode = "QUATERNION"
    prev = None
    for f in range(1, 721):
        if f <= keys[0][0]:
            M = keys[0][1]
        elif f >= keys[-1][0]:
            M = keys[-1][1]
        else:
            for (fa, Ma), (fb, Mb) in zip(keys[:-1], keys[1:]):
                if fa <= f <= fb:
                    t = smooth((f - fa) / (fb - fa))
                    la, ra, sa = Ma.decompose()
                    lb, rb, sb = Mb.decompose()
                    if ra.dot(rb) < 0:
                        rb.negate()
                    M = Matrix.LocRotScale(la.lerp(lb, t), ra.slerp(rb, t), sa.lerp(sb, t))
                    break
        l, r, s = M.decompose()
        if prev is not None and prev.dot(r) < 0:
            r.negate()
        prev = r
        for k in range(3):
            chans.setdefault(("location", k), []).append((f, l[k]))
            chans.setdefault(("scale", k), []).append((f, s[k]))
        for k in range(4):
            chans.setdefault(("rotation_quaternion", k), []).append((f, r[k]))
    write_action(gift, "GIFT_CAP_SH09", chans)


def animate_hero_brim(scene, hero, target):
    """Key the hero's brim-contact IK target from the evaluated cap so fingers meet the fabric."""
    cap = hero.cap
    base_rx = cap.rotation_euler.x
    capch = {}
    for f in (1, 345, 349, 352, 355, 360, 720):
        tug = radians(3.5) * pulse(f, 349, 351, 353, 356)
        capch.setdefault(("rotation_euler", 0), []).append((f, base_rx + tug))
    write_action(cap, "HERO_01_CAP_TUG_SH05", capch, interp="BEZIER")
    grip_local = Vector((-0.05, -0.155, -0.012))
    ch = {}
    for f in list(range(330, 366)):
        scene.frame_set(f)
        w = cap.matrix_world @ grip_local
        for k in range(3):
            ch.setdefault(("location", k), []).append((f, w[k]))
    write_action(target, "HERO_01_BRIM_GRIP_SH05", ch)


def animate_cartoon_props(director, chars, cone, dish, elephant_obs):
    ch = {}
    g2 = director.w["G2a"], director.w["G2b"]
    for f in range(1, 721):
        n = shot_of(f)
        if n == 3:
            walking = 1.0 if (g2[0].active(f) or g2[1].active(f)) else 0.0
            stop = 166
            env_ = walking if walking else exp(-max(0, f - stop) / 7.0)
            ang = 7.0 * sin(2 * pi * f / 9.0) * env_
        else:
            ang = 1.2 * sin(2 * pi * f / 37.0)
        ch.setdefault(("rotation_euler", 0), []).append((f, radians(ang)))
    write_action(cone, "GUEST_02_CONE_WOBBLE_SH03", ch)
    ch = {}
    g3 = director.w["G3a"]
    for f in range(1, 721):
        n = shot_of(f)
        if n == 4:
            walking = 1.0 if g3.active(f) else exp(-max(0, f - g3.f1) / 10.0)
            ang = -(18 + 7 * seg(f, 217, 245) + 5 * sin(2 * pi * f / 13.0) * walking)
        else:
            ang = -(16 + 1.5 * sin(2 * pi * f / 41.0))
        ch.setdefault(('modifiers["WEIGHT_SAG"].angle', 0), []).append((f, radians(ang)))
    write_action(dish, "GUEST_03_DISH_SAG_SH04", ch)
    for child in dish.children:
        child.animation_data_create()
        child.animation_data.action = bpy.data.actions["GUEST_03_DISH_SAG_SH04"]
    ear = elephant_obs["EAR"]
    ch = {}
    for f in range(1, 721, 2):
        ch.setdefault(("rotation_euler", 1), []).append((f, radians(3.0 * sin(2 * pi * f / 30.0))))
    write_action(ear, "CARTOON_ELEPHANT_01_EAR_SH08", ch, interp="BEZIER")


# ---------------------------------------------------------------- cameras
CAM_FSTOP = {1: 4.0, 2: 2.8, 3: 2.8, 4: 4.0, 5: 2.8, 6: 2.0, 7: 2.8, 8: 4.0, 9: 2.8, 10: 2.0}


def camera_rig(n, f, d):
    """Return (location, look-at target, focus point) for camera n at frame f."""
    if n == 1:
        t = seg(f, 1, 72)
        return vlerp((-0.45, -9.6, 0.55), (-0.3, -7.7, 0.6), t), vlerp((0.15, 0, 1.45), (0.15, 0, 1.5), t), Vector((0.5, -0.9, 1.4))
    if n == 2:
        t = seg(f, 73, 144)
        foc = d.head_of("GUEST_01", f).lerp(d.head_of("BOUNCER_01", f), 0.4)
        return vlerp((-0.8, -4.65, 1.5), (-0.62, -4.25, 1.48), t), Vector((0.32, -1.2, 1.38)), foc
    if n == 3:
        x = lerp(-2.25, -0.95, seg(f, 145, 172)) + 0.22 * seg(f, 172, 216)
        g = d.head_of("GUEST_02", f)
        return Vector((x, -4.7, 1.35)), Vector((x + 0.95, -1.4, 1.45)), g
    if n == 4:
        t = seg(f, 217, 288)
        return vlerp((-1.95, -4.2, 0.3), (-1.75, -3.98, 0.32), t), Vector((0.2, -1.2, 1.85)), d.head_of("GUEST_03", f)
    if n == 5:
        hx = d.pose("HERO_01", f, eyelines=False).x
        x = hx - 0.2 - 0.25 * seg(hx, -1.0, -0.1)
        h = d.head_of("HERO_01", f)
        tgt = Vector((h.x + 0.38, -1.3, 1.42))
        return Vector((x, -3.55, 1.3)), tgt, h
    if n == 6:
        if f <= 384:
            t = seg(f, 361, 384)
            b = d.head_of("BOUNCER_01", f)
            return vlerp((-0.48, -2.6, 1.72), (-0.44, -2.52, 1.72), t), b + Vector((0, 0, 0.02)), b
        if f <= 408:
            t = seg(f, 385, 408)
            h = d.head_of("HERO_01", f)
            return vlerp((1.02, -2.78, 1.64), (0.98, -2.7, 1.64), t), h + Vector((0, 0, 0.04)), h
        t = seg(f, 409, 432)
        b = d.head_of("BOUNCER_01", f)
        return vlerp((-0.4, -2.5, 1.7), (-0.36, -2.42, 1.7), t), b + Vector((0, 0, 0.01)), b
    if n == 7:
        hold = Vector((-0.75, -3.65, 1.62))
        h = d.head_of("HERO_01", f)
        follow = Vector((lerp(h.x, 0.05, 0.6), h.y - 1.45, 1.6))
        w = seg(f, 452, 470)
        loc = hold.lerp(follow, w)
        if loc.y > -0.6:
            loc.x = lerp(loc.x, 0.05, seg(loc.y, -0.6, -0.2))
        tgt = Vector((0.15, -0.8, 1.35)).lerp(h + Vector((0, 1.2, -0.15)), w)
        return loc, tgt, h
    if n == 8:
        t = seg(f, 505, 576)
        return vlerp((-3.4, 7.2, 1.58), (-3.1, 7.55, 1.56), t), Vector((1.9, 13.9, 1.35)), Vector((2.7, 14.1, 1.4))
    if n == 9:
        return Vector((-0.35, -4.5, 1.42)), Vector((0.4, -1.15, 1.3)), Vector((0.35, -1.25, 1.4))
    t = seg(f, 649, 672)
    capc = d.head_of("HERO_01", f) + Vector((0, 0, 0.09))
    return vlerp((0.25, 9.22, 1.74), (0.16, 9.38, 1.73), t), capc + Vector((0, 0, -0.03)), capc


def build_cameras(cols, director):
    cams = {}
    for s in SHOTS:
        n = s["n"]
        cd = bpy.data.cameras.new("CAM_%02d" % n)
        cd.lens = s["lens"]
        cd.sensor_width = 36.0
        cd.sensor_fit = "HORIZONTAL"
        cd.clip_start = 0.05
        cd.clip_end = 200.0
        cd.dof.use_dof = True
        cd.dof.aperture_fstop = CAM_FSTOP[n]
        cam = bpy.data.objects.new("CAM_%02d" % n, cd)
        cols["CAMERAS"].objects.link(cam)
        cam["shot"] = s["name"]
        cam["lens_mm"] = s["lens"]
        f_last = 672 if n == 10 else s["end"]
        ch, chd = {}, {}
        prev = None
        for f in range(s["start"], f_last + 1):
            loc, tgt, foc = camera_rig(n, f, director)
            rot = (Vector(tgt) - Vector(loc)).to_track_quat("-Z", "Y").to_euler()
            if prev is not None:
                rot.make_compatible(prev)
            prev = rot
            for k in range(3):
                ch.setdefault(("location", k), []).append((f, loc[k]))
                ch.setdefault(("rotation_euler", k), []).append((f, rot[k]))
            chd.setdefault(("dof.focus_distance", 0), []).append((f, (Vector(foc) - Vector(loc)).length))
        const = {384, 408} if n == 6 else set()
        write_action(cam, "CAM_%02d_SH%02d" % (n, n), ch, constant_frames=const)
        write_action(cd, "CAM_%02d_FOCUS_SH%02d" % (n, n), chd, constant_frames=const)
        cams[n] = cam
    return cams


# ---------------------------------------------------------------- foot locking (leg IK)
def foot_lock(scene, ch, active_shots, coll):
    """Pin planted feet: sample FK ankles, hold each stance at its slowest-frame position via 2-bone leg IK."""
    arm = ch.arm
    rest_z = arm.data.bones["shin.L"].tail_local.z
    frames = [f for s in SHOTS for f in range(s["start"], s["end"] + 1)]
    fk = {"L": {}, "R": {}}
    for f in frames:
        scene.frame_set(f)
        for side in ("L", "R"):
            fk[side][f] = (arm.matrix_world @ arm.pose.bones["foot." + side].head).copy()
    for side in ("L", "R"):
        tgt = bpy.data.objects.new("CTRL_%s_FOOT_%s" % (ch.name, side), None)
        tgt.empty_display_type = "CUBE"
        tgt.empty_display_size = 0.04
        coll.objects.link(tgt)
        pos = dict(fk[side])
        for s in SHOTS:
            if s["n"] not in active_shots:
                continue
            run = []
            for f in range(s["start"], s["end"] + 2):
                planted = f <= s["end"] and fk[side][f].z < rest_z + 0.006
                if planted:
                    run.append(f)
                    continue
                if run:
                    def speed(g):
                        a = fk[side][max(run[0], g - 1)]
                        b = fk[side][min(run[-1], g + 1)]
                        return (b.to_2d() - a.to_2d()).length
                    anchor = min(run, key=speed)
                    lock = fk[side][anchor].copy()
                    for g in run:
                        q = lock.copy()
                        q.z = fk[side][g].z
                        pos[g] = q
                    run = []
        chans = {}
        const = set(SHOT_END.values())
        for f in frames:
            for k in range(3):
                chans.setdefault(("location", k), []).append((f, pos[f][k]))
        write_action(tgt, "%s_FOOT_%s_LOCK" % (ch.name, side), chans, constant_frames=const)
        c = arm.pose.bones["shin." + side].constraints.new("IK")
        c.name = "IK_FOOTLOCK_" + side
        c.target = tgt
        c.chain_count = 2
        c.use_tail = True
        c.use_stretch = False
