"""Performance, kinematics and cameras for the ten shots.
Every frame gets a full pose: root position, torso pitch/drop/compression/breath, head pitch, ears, tail, eyes, blink,
muzzle shape and four hoof targets. Legs are solved by two-bone IK so planted hooves stay exactly where they were put
(the walk planner keeps at least two hooves on the ground at all times). The same pose drives the side artwork, the rear
artwork (leg lifts, head height, ear and tail angles) and the invisible 3D shadow proxy."""
import json
import math
import os

import bpy
from mathutils import Vector

import config as C
import moo as M

S = C.MOO_SCALE
SP = M.META
TC = M.SIDE_PIV["torso"]
NK = M.SIDE_PIV["neck"]
L1 = 0.22
LEGS = [("rear", "near"), ("rear", "far"), ("front", "near"), ("front", "far")]
REST_U = {(w, s): SP[f"side_leg_{w}_{s}_upper"]["pivot_m"][0] for w, s in LEGS}
HIP_V = {(w, s): SP[f"side_leg_{w}_{s}_upper"]["pivot_m"][1] for w, s in LEGS}
BEND = {"rear": -1.0, "front": 1.0}
L2 = {leg: SP[f"side_leg_{leg[0]}_{leg[1]}_lower"]["pivot_m"][1] for leg in LEGS}      # knee height = lower length
LOG = {"contacts": [], "notes": []}


def ease(t):
    t = max(0.0, min(1.0, t))
    return t * t * (3 - 2 * t)


def lerp(a, b, t):
    return a + (b - a) * t


def seg(t, keys):
    """Piecewise eased interpolation through (time, value) keys."""
    if t <= keys[0][0]:
        return keys[0][1]
    for (t0, v0), (t1, v1) in zip(keys, keys[1:]):
        if t <= t1:
            return lerp(v0, v1, ease((t - t0) / (t1 - t0)))
    return keys[-1][1]


def rot(p, c, a):
    x, y = p[0] - c[0], p[1] - c[1]
    return (c[0] + x * math.cos(a) - y * math.sin(a), c[1] + x * math.sin(a) + y * math.cos(a))


def base_pose():
    return dict(x=0.0, y=0.0, tp=0.0, dy=0.0, comp=0.0, breath=0.0, hp=0.0, ear=0.0, ear_far=0.0, tail=0.0, eye=0.0,
                blink=0.0, mouth="mouth_neutral", hooves={}, exposure=1.0, head_dx=0.0)


def hip_design(p, leg):
    w, s = leg
    h = rot((REST_U[leg], HIP_V[leg]), TC, p["tp"])
    return (h[0], h[1] + p["dy"])


def rest_hooves(p, back=0.0, front=0.0):
    return {leg: (p["x"] + (REST_U[leg] + (back if leg[0] == "rear" else front)) * S, 0.0) for leg in LEGS}


# --------------------------------------------------------------------------- head geometry (for contact)
def _se(cx, cy, w, h, n, k=48):
    out = []
    for i in range(k):
        t = 2 * math.pi * i / k
        c, s = math.cos(t), math.sin(t)
        out.append((cx + w / 2 * math.copysign(abs(c) ** (2 / n), c), cy + h / 2 * math.copysign(abs(s) ** (2 / n), s)))
    return out


HEAD_PTS = _se(0.52, 0.78, 0.34, 0.30, 2.2) + _se(0.62, 0.69, 0.22, 0.16, 2.0) + _se(0.70, 0.705, 0.17, 0.155, 2.3)


def head_world(p):
    """Head outline in design coords after head pitch and torso transform."""
    pts = []
    for q in HEAD_PTS:
        a = rot(q, NK, p["hp"])
        a = rot(a, TC, p["tp"])
        pts.append((a[0] + p["head_dx"], a[1] + p["dy"]))
    return pts


def contact_root_x(p, face_x, block_h):
    """Root x that puts the front-most head point below the block top exactly on the block face (no clipping)."""
    pts = head_world(p)
    below = [u for u, v in pts if v * S < block_h - 0.01]
    above = [u for u, v in pts if v * S >= block_h - 0.01]
    lead = max(below)
    root = face_x - lead * S
    overhang = (max(above) - lead) * S if above else 0.0
    return root, overhang


def solve_brace(face_x):
    best = None
    for tp in [-0.04 * i for i in range(0, 7)]:
        for dy in [-0.01 * i for i in range(0, 16)]:
            for hp in [-0.02 * i for i in range(25, 80)]:
                p = base_pose()
                p.update(tp=tp, dy=dy, hp=hp)
                pts = head_world(p)
                if min(v for u, v in pts) * S < 0.03:          # muzzle never touches the floor
                    continue
                if not any(v * S < C.BLOCK["h"] - 0.04 for u, v in pts):
                    continue
                r, oh = contact_root_x(p, face_x, C.BLOCK["h"])
                if oh > 0.0:                                    # nothing of the head reaches over the block top
                    continue
                cost = abs(hp + 1.05) + abs(tp + 0.12) * 2 + abs(dy + 0.08) * 3
                if best is None or cost < best[0]:
                    best = (cost, tp, dy, hp, r, oh)
    LOG["notes"].append(f"brace pose: torso pitch {best[1]:.2f}, drop {best[2]:.2f}, head pitch {best[3]:.2f}, overhang {best[5]*100:.1f} cm")
    return dict(tp=best[1], dy=best[2], hp=best[3])


# --------------------------------------------------------------------------- walking planner
def walk_hooves(t, root_fn, ta, tb, T=0.9, duty=0.68, lift=0.06, phase0=0.0, start=None):
    """Lateral-sequence walk. Stance k of a leg spans [ta+(k+ph)T, ta+(k+ph+duty)T]; during it the hoof stays exactly at
    its plant. The first plant of each leg is where the hoof already is at ta (start, or rest under the body); later plants
    land under the hip at mid-stance. Swings ease between consecutive plants with a sine lift."""
    offs = {("rear", "far"): 0.0, ("front", "far"): 0.25, ("rear", "near"): 0.5, ("front", "near"): 0.75}
    out = {}
    for leg in LEGS:
        rest = REST_U[leg] * S
        ph = offs[leg] + phase0
        u_first = start[leg][0] if start else root_fn(ta) + rest

        def plant(k):
            if k + ph <= 1e-6:
                return u_first
            tm = ta + (k + ph + duty / 2) * T
            return root_fn(min(max(tm, ta), tb)) + rest

        if t <= ta:
            out[leg] = (u_first, 0.0)
            continue
        cyc = (t - ta) / T - ph
        k = math.floor(cyc)
        f = cyc - k
        if f < duty:
            out[leg] = (plant(k), 0.0)
        else:
            s = (f - duty) / (1 - duty)
            u0, u1 = plant(k), plant(k + 1)
            lf = lift * min(1.0, abs(u1 - u0) / 0.03)        # tiny corrections become tiny lifted shuffles, never slides
            out[leg] = (lerp(u0, u1, ease(s)), max(lf, 0.0025 if u1 != u0 else 0.0) * math.sin(math.pi * s))
    return out


# --------------------------------------------------------------------------- shots (t = seconds within shot)
def breathe(t, period=3.4, amp=0.012):
    return amp * math.sin(2 * math.pi * t / period)


def s01(t, p):
    p.update(x=C.MEADOW_MOO[0], y=C.MEADOW_MOO[1], hp=seg(t, [(0, 0.02), (2.5, 0.10), (4, 0.10)]))
    p["breath"] = breathe(t, 3.6, 0.016)
    p["ear"] = 0.10 * math.sin(t * 1.3) + (0.25 if 1.4 < t < 1.9 else 0.0) * math.sin((t - 1.4) / 0.5 * math.pi)
    p["ear_far"] = 0.08 * math.sin(t * 1.1 + 1.0)
    p["tail"] = 0.12 * math.sin(t * 1.7 - 0.5)
    p["hooves"] = rest_hooves(p)


PUD = dict(x=C.PUDDLE["x"] - 0.62, y=C.PUDDLE["y"] + 0.47)


def s02(t, p):
    p.update(x=PUD["x"], y=PUD["y"])
    p["tp"] = seg(t, [(0, -0.06), (1.0, -0.15), (2.2, -0.15), (2.9, -0.07)])
    p["dy"] = seg(t, [(0, -0.025), (1.0, -0.06), (2.2, -0.06), (2.9, -0.03)])
    p["hp"] = seg(t, [(0, -0.50), (1.05, -1.20), (2.2, -1.20), (2.95, -0.62)])
    p["ear"] = seg(t, [(0, 0.0), (1.4, -0.12), (2.3, -0.12), (2.9, 0.10)]) + 0.03 * math.sin(t * 5)
    p["ear_far"] = p["ear"] * 0.8
    p["blink"] = 1.0 if 1.65 < t < 1.78 else (0.5 if 1.6 < t <= 1.65 or 1.78 <= t < 1.83 else 0.0)
    p["eye"] = seg(t, [(0, 0.0), (1.2, -0.004), (2.6, 0.003)])
    p["breath"] = breathe(t, 3.0, 0.01)
    p["tail"] = 0.08 * math.sin(t * 1.5)
    p["hooves"] = rest_hooves(p, back=-0.02, front=0.03)


S03 = dict(xa=2.0, xb=4.45, ta=0.15, tb=3.15)


def s03_root(t):
    """Constant walking speed with 0.45 s soft start and stop (no speed peak the legs cannot follow)."""
    ta, tb, xa, xb, r = S03["ta"], S03["tb"], S03["xa"], S03["xb"], 0.45
    v = (xb - xa) / (tb - ta - r)
    if t <= ta:
        return xa
    if t >= tb:
        return xb
    if t < ta + r:
        return xa + v * (t - ta) ** 2 / (2 * r)
    if t > tb - r:
        return xb - v * (tb - t) ** 2 / (2 * r)
    return xa + v * r / 2 + v * (t - ta - r)


def s03(t, p):
    p.update(x=s03_root(t), y=0.0)
    p["hooves"] = walk_hooves(t, s03_root, S03["ta"], S03["tb"], T=0.52, duty=0.64)
    walking = S03["ta"] < t < S03["tb"] + 0.3
    carriage = -0.032 * seg(t, [(0, 0), (S03["ta"] + 0.3, 1), (S03["tb"] - 0.1, 1), (S03["tb"] + 0.5, 0)])
    p["dy"] = carriage + ((0.006 * math.sin(4 * math.pi * (t - S03["ta"]) / 0.52)) if walking else 0.0)
    p["hp"] = seg(t, [(0, 0.05), (3.0, 0.02), (3.4, -0.06), (4.0, -0.06)])
    p["ear"] = 0.06 * math.sin(t * 2.2) + seg(t, [(0, 0), (3.2, 0), (3.6, 0.15)])
    p["ear_far"] = p["ear"]
    p["tail"] = 0.15 * math.sin(t * 2 * math.pi / 0.52)
    p["breath"] = breathe(t, 2.8, 0.012)


def push_base(p, brace, face):
    p.update(tp=brace["tp"], dy=brace["dy"], hp=brace["hp"])


def s04(t, p, brace, face):
    push_base(p, brace, face)
    r0, _ = contact_root_x(p, face, C.BLOCK["h"])
    p["x"], p["y"] = r0, 0.0
    press = seg(t, [(0, 0.0), (0.6, 0.0), (2.6, 1.0), (2.8, 1.0)])
    p["comp"] = 0.035 * press
    p["dy"] = brace["dy"] - 0.012 * press
    slip = seg(t, [(0, 0.0), (2.55, 0.0), (2.95, 0.035), (4.0, 0.035)])
    release = seg(t, [(0, 0.0), (2.9, 0.0), (3.4, 0.022)])
    p["x"] = r0 - slip * 0.85 - release
    p["comp"] *= (1 - ease((t - 2.85) / 0.4)) if t > 2.85 else 1
    rest = rest_hooves(dict(x=r0), back=-0.07, front=-0.02)
    p["hooves"] = {leg: (u - (slip if leg[0] == "rear" else 0.0), 0.0) for leg, (u, v) in rest.items()}
    p["mouth"] = "mouth_strain" if 0.8 < t < 3.2 else "mouth_neutral"
    p["ear"] = seg(t, [(0, 0.05), (2.5, -0.15), (3.3, 0.05)])
    p["ear_far"] = p["ear"]
    p["tail"] = seg(t, [(0, 0.0), (2.6, 0.25), (3.0, -0.1), (4, 0.0)])
    p["breath"] = breathe(t, 1.6, 0.012)
    p["eye"] = 0.004
    p["blink"] = 0.35 * press
    LOG["contacts"].append(("S04", round(t, 2), "head-block gap cm", round((p["x"] - r0) * -100, 2)))


def s05(t, p, brace, face, end04, start_hooves=None):
    # steps backward and steadies, ears droop, stares, re-plants, ears rise, gaze focuses
    stand = dict(tp=0.0, dy=0.0, hp=-0.15)
    k = ease(t / 0.8)
    p["tp"] = lerp(brace["tp"], stand["tp"], k)
    p["dy"] = lerp(brace["dy"], stand["dy"], k)
    p["hp"] = seg(t, [(0, brace["hp"]), (0.8, -0.18), (2.4, -0.18), (3.4, 0.02), (4.0, 0.02)])
    x0 = end04
    q = base_pose()
    push_base(q, brace, face)
    r0, _ = contact_root_x(q, face, C.BLOCK["h"])
    x1 = r0 - 0.03                                     # S06 begins from here
    root = lambda tt: seg(tt, [(0.0, x0), (1.3, x0 - 0.12), (2.6, x0 - 0.12), (3.7, x1)])
    p["x"], p["y"] = root(t), 0.0
    if t < 2.6:                                        # steps back, steadies
        hv = walk_hooves(t, root, 0.0, 1.3, T=0.75, duty=0.7, lift=0.04, start=start_hooves)
    else:                                              # re-plants its hooves, deliberately, back to the block
        hv = walk_hooves(t, root, 2.6, 3.7, T=0.8, duty=0.7, lift=0.035)
    p["hooves"] = hv
    p["ear"] = seg(t, [(0, 0.0), (1.0, -0.35), (2.4, -0.35), (3.2, 0.18), (4.0, 0.15)])
    p["ear_far"] = p["ear"] * 0.9
    p["tail"] = seg(t, [(0, 0.0), (1.0, -0.15), (2.4, -0.15), (3.4, 0.05)])
    p["breath"] = breathe(t, 2.2, 0.016)
    p["blink"] = 1.0 if 1.9 < t < 2.02 else 0.0
    p["blink"] = max(p["blink"], seg(t, [(0, 0), (3.2, 0), (3.6, 0.28)]))       # focused, slightly lowered lids
    p["eye"] = seg(t, [(0, 0.0), (1.0, -0.002), (3.3, 0.005)])
    p["mouth"] = "mouth_breath" if t < 1.4 else "mouth_neutral"


def s06(t, p, brace, face, x_start):
    push_base(p, brace, face)
    r0, _ = contact_root_x(p, face, C.BLOCK["h"])
    lean = seg(t, [(0, 0.0), (1.2, 1.0), (3.0, 1.0)])
    # approach from the S05 stance to contact, then drive: the block starts moving at 2.1 s
    p["x"] = lerp(x_start, r0, ease(t / 0.9))
    p["tp"] = lerp(-0.0, brace["tp"], ease(t / 0.9)) - 0.03 * lean
    p["hp"] = lerp(0.02, brace["hp"], ease(t / 0.9))
    p["dy"] = lerp(0.0, brace["dy"], ease(t / 0.9)) - 0.015 * lean
    p["comp"] = 0.03 * lean
    blk = block_offset_at(t + 0.0, "S06")
    p["x"] += blk
    p["hooves"] = rest_hooves(dict(x=x_start))       # hooves stay planted where S05 re-planted them; the body drives forward
    p["mouth"] = "mouth_strain"
    p["ear"] = seg(t, [(0, 0.15), (1.2, -0.12)])
    p["ear_far"] = p["ear"]
    p["tail"] = 0.06 * math.sin(t * 4)
    p["breath"] = breathe(t, 1.2, 0.012)
    p["blink"] = 0.35
    p["eye"] = 0.005


def block_offset_at(t, shot):
    """Block slide (m): starts at 2.1 s into S06, reaches slide_m during S07, eases to a stop."""
    total = C.BLOCK["slide_m"]
    if shot == "S06":
        return seg(t, [(0, 0.0), (2.1, 0.0), (3.0, 0.012)])
    if shot == "S07":
        return seg(t, [(0, 0.012), (1.5, total), (2.0, total)])
    return total


def s07(t, p, brace, face, x_start):
    push_base(p, brace, face)
    r0, _ = contact_root_x(p, face, C.BLOCK["h"])
    blk = block_offset_at(t, "S07")
    release = seg(t, [(0, 0.0), (1.55, 0.0), (2.0, 0.012)])
    p["x"] = r0 + blk - release
    p["tp"] = brace["tp"] - 0.03
    p["dy"] = brace["dy"] - 0.015
    p["comp"] = 0.03 * (1 - ease((t - 1.5) / 0.4)) if t > 1.5 else 0.03
    p["hooves"] = rest_hooves(dict(x=x_start))       # same planted hooves as S06
    p["mouth"] = "mouth_strain" if t < 1.6 else "mouth_breath"
    p["ear"] = seg(t, [(0, -0.12), (1.6, -0.12), (2.0, 0.1)])
    p["ear_far"] = p["ear"]
    p["breath"] = breathe(t, 1.0, 0.012)
    p["blink"] = 0.35


STAND = {}


def stand_after(p, face, t=0.0):
    """Relaxed from the push on the same planted hooves, just behind the moved block, head raised (S08-S10)."""
    r0 = STAND["x"] - 0.02
    p.update(x=r0, y=0.0, tp=-0.02, dy=-0.035, hp=0.08)
    p["hooves"] = dict(STAND["hooves"])
    return r0


def s08(t, p, face):
    stand_after(p, face)
    p["breath"] = breathe(t, 1.15, seg(t, [(0, 0.03), (3.0, 0.018)]))
    p["ear"] = seg(t, [(0, -0.05), (0.9, 0.25), (3, 0.22)])
    p["ear_far"] = p["ear"]
    p["mouth"] = "mouth_breath" if t < 1.0 else "mouth_smile" if t > 1.55 else "mouth_neutral"
    p["eye"] = seg(t, [(0, 0.0), (1.9, 0.0), (2.4, 1.0)])          # q3: gaze shift toward the doors (screen left)
    p["blink"] = 1.0 if 1.25 < t < 1.36 else 0.0
    p["hp"] = 0.08 + seg(t, [(0, 0), (2.0, 0), (2.6, 0.04)])


def s09(t, p, face):
    stand_after(p, face)
    p["hp"] = seg(t, [(0, 0.10), (1.4, 0.16)])
    p["ear"] = seg(t, [(0, 0.15), (0.8, 0.30)])
    p["ear_far"] = p["ear"]
    p["tail"] = 0.05 * math.sin(t * 2)
    p["breath"] = breathe(t, 1.6, 0.014)


def s10(t, p, face):
    r0 = stand_after(p, face)
    step = 0.10
    root = lambda tt: seg(tt, [(0.0, r0), (0.25, r0), (0.9, r0 + step * 0.55)])
    p["x"] = root(t)
    hv = dict(STAND["hooves"])
    # one deliberate step: right fore, then left hind follows partially (two hooves always down)
    for leg, t0, t1, d in ((("front", "near"), 0.2, 0.55, step), (("rear", "far"), 0.5, 0.85, step)):
        u, v = hv[leg]
        s = ease((t - t0) / (t1 - t0))
        hv[leg] = (u + d * s, 0.05 * math.sin(math.pi * s) if 0 < s < 1 else 0.0)
    p["hooves"] = hv
    p["hp"] = 0.16
    p["ear"] = 0.3
    p["ear_far"] = 0.3
    p["breath"] = breathe(t, 1.6, 0.012)


# --------------------------------------------------------------------------- applying a pose
def ik(hip, tgt, bend, l2):
    dx, dy = tgt[0] - hip[0], tgt[1] - hip[1]
    d = max(0.05, min(L1 + l2 - 1e-4, math.hypot(dx, dy)))
    a = math.atan2(dy, dx)
    A = math.acos(max(-1, min(1, (L1 * L1 + d * d - l2 * l2) / (2 * L1 * d))))
    al = a + bend * A
    k = (hip[0] + L1 * math.cos(al), hip[1] + L1 * math.sin(al))
    be = math.atan2(tgt[1] - k[1], tgt[0] - k[0])
    reach = math.hypot(dx, dy)
    return al, be, reach


def apply(rig, p, f, view):
    root, (svr, sp, sparts), (rvr, rp, rparts) = rig["root"], rig["side"], rig["rear"]
    root.location = (p["x"], p["y"], 0.0)
    root.keyframe_insert("location", frame=f)
    root["exposure"] = p["exposure"]
    root.keyframe_insert('["exposure"]', frame=f)
    # side pose
    sp["torso"].location = (TC[0], 0, TC[1] + p["dy"])
    sp["torso"].rotation_euler = (0, -p["tp"], 0)
    sparts["torso"].scale = (1 - p["comp"], 1, 1 + p["breath"])
    sp["neck"].rotation_euler = (0, -p["hp"], 0)
    sp["ear"].rotation_euler = (0, -p["ear"], 0)
    sp["tail"].rotation_euler = (0, -p["tail"], 0)
    sp["eye"].location.x = SP["side_eye"]["pivot_m"][0] - NK[0] + p["eye"] if view != "q3" else sp["eye"].location.x
    sp["lid"].scale = (1, 1, max(0.001, p["blink"]))
    for k in ("torso", "neck", "ear", "tail", "eye", "lid"):
        o = sp[k]
        for path in ("location", "rotation_euler", "scale"):
            o.keyframe_insert(path, frame=f)
    sparts["torso"].keyframe_insert("scale", frame=f)
    for nm in ("mouth_neutral", "mouth_strain", "mouth_smile", "mouth_breath"):
        o = sparts[nm]
        o.hide_render = nm != p["mouth"]
        o.keyframe_insert("hide_render", frame=f)
    worst = 0.0
    for leg in LEGS:
        hip = hip_design(p, leg)
        hu, hv = p["hooves"][leg]
        tgt = ((hu - p["x"]) / S, hv / S)
        al, be, reach = ik(hip, tgt, BEND[leg[0]], L2[leg])
        worst = max(worst, reach - (L1 + L2[leg]))
        up = sp[f"leg_{leg[0]}_{leg[1]}_upper"]
        lo = sp[f"leg_{leg[0]}_{leg[1]}_lower"]
        up.rotation_euler = (0, -(al + math.pi / 2 - p["tp"]), 0)
        lo.rotation_euler = (0, -(be - al), 0)
        up.keyframe_insert("rotation_euler", frame=f)
        lo.keyframe_insert("rotation_euler", frame=f)
        hz = rig["hooves"][f"{leg[0]}_{leg[1]}"]
        hz.location = (hu, p["y"] + (-0.11 if leg[1] == "near" else 0.11), hv)
        hz.keyframe_insert("location", frame=f)
        # rear artwork: near = MOO's right = screen right from behind ("_r")
        rk = f"leg_{leg[0]}_{'r' if leg[1] == 'near' else 'l'}"
        rpv = rp[rk]
        base = SP and M.META[f"rear_{rk}"]["pivot_m"]
        rpv.location.z = base[1] - M.REAR_PIV["torso"][1] - p["dy"] / S + hv / S
        rpv.scale = (1, 1, 1 - 0.5 * hv / 0.45)
        rpv.keyframe_insert("location", frame=f)
        rpv.keyframe_insert("scale", frame=f)
    rp["torso"].location.z = M.REAR_PIV["torso"][1] + p["dy"] / S
    rparts["torso"].scale = (1, 1 + p["breath"] * 0.6, 1 + p["breath"])
    rp["neck"].location.z = M.REAR_PIV["neck"][1] - M.REAR_PIV["torso"][1] + 0.22 * math.sin(p["hp"])
    rp["ear_l"].rotation_euler = (p["ear_far"] * 0.8, 0, 0)
    rp["ear_r"].rotation_euler = (-p["ear"] * 0.8, 0, 0)
    rp["tail"].rotation_euler = (p["tail"] * 0.8, 0, 0)
    for k in ("torso", "neck", "ear_l", "ear_r", "tail"):
        for path in ("location", "rotation_euler"):
            rp[k].keyframe_insert(path, frame=f)
    rparts["torso"].keyframe_insert("scale", frame=f)
    return worst


def apply_q3(rig, p, f, cam_pos, head_world):
    vr, qp, qparts = rig["q3"]
    vr.location = head_world
    d = (Vector(cam_pos) - Vector(head_world))
    d.z = 0
    d.normalize()
    vr.rotation_euler = (0, 0, math.atan2(d.x, -d.y))
    vr.scale = (S, S, S)
    for path in ("location", "rotation_euler", "scale"):
        vr.keyframe_insert(path, frame=f)
    qp["neck"].scale = (1 + p["breath"] * 0.5, 1, 1 + p["breath"])
    qp["head"].location = (0.0, 0, 0.05 + p["breath"] * 0.25 + 0.06 * math.sin(p["hp"] - 0.08))
    qp["head"].rotation_euler = (0, 0.04 * p["eye"], 0)
    qp["ear_far"].rotation_euler = (0, p["ear"] * 0.6, 0)
    qp["ear_near"].rotation_euler = (0, -p["ear"] * 0.6, 0)
    for nm in ("eye_far", "eye_near"):
        base = M.META[f"q3_{nm}"]["pivot_m"]
        qp[nm].location.x = base[0] - 0.0 - 0.012 * p["eye"]
        qp[nm].location.z = base[1] - 0.0 + 0.003 * p["eye"]
    for nm in ("lid_far", "lid_near"):
        qp[nm].scale = (1, 1, max(0.001, p["blink"]))
    for k in ("neck", "head", "ear_far", "ear_near", "eye_far", "eye_near", "lid_far", "lid_near"):
        for path in ("location", "rotation_euler", "scale"):
            qp[k].keyframe_insert(path, frame=f)
    for nm in ("mouth_neutral", "mouth_strain", "mouth_smile", "mouth_breath"):
        o = qparts[nm]
        o.hide_render = nm != p["mouth"]
        o.keyframe_insert("hide_render", frame=f)


def side_head_world(rig, p):
    """World position of the side-view neck pivot area (used to place the q3 head rig)."""
    n = rot(NK, TC, p["tp"])
    return (p["x"] + (n[0] + 0.12) * S, p["y"] - 0.02, (n[1] + p["dy"] + 0.05) * S)


# --------------------------------------------------------------------------- cameras
def camera(name, coll, lens, keys, target_keys, fstop=4.0, focus=None):
    cd = bpy.data.cameras.new(name)
    cd.lens = lens
    cd.sensor_width = 36.0
    cd.clip_start = 0.02
    cd.clip_end = 1200
    cd.dof.use_dof = True
    cd.dof.aperture_fstop = fstop
    cam = bpy.data.objects.new(name, cd)
    coll.objects.link(cam)
    tgt = bpy.data.objects.new(name + "_AIM", None)
    coll.objects.link(tgt)
    for f, pos in keys:
        cam.location = pos
        cam.keyframe_insert("location", frame=f)
    for f, pos in target_keys:
        tgt.location = pos
        tgt.keyframe_insert("location", frame=f)
    c = cam.constraints.new("TRACK_TO")
    c.target = tgt
    c.track_axis, c.up_axis = "TRACK_NEGATIVE_Z", "UP_Y"
    cd.dof.focus_object = focus or tgt
    return cam


def build_shots(rig, coll_cam, E):
    sc = bpy.context.scene
    face = C.BLOCK["x"] - C.BLOCK["d"] / 2
    brace = solve_brace(face)
    poses = {}
    worst = {}
    ext_exposure, int_exposure = 1.0, 1.0
    end04_x = end05_x = end04_hooves = None
    for s in C.SHOTS:
        f0, f1 = C.bf(s["f0"]), C.bf(s["f1"])
        for f in range(f0, f1 + 1):
            t = (f - f0) / C.FPS
            p = base_pose()
            sid = s["id"]
            if sid == "S01":
                s01(t, p)
            elif sid == "S02":
                s02(t, p)
            elif sid == "S03":
                s03(t, p)
            elif sid == "S04":
                s04(t, p, brace, face)
            elif sid == "S05":
                s05(t, p, brace, face, end04_x, end04_hooves)
            elif sid == "S06":
                s06(t, p, brace, face, end05_x)
            elif sid == "S07":
                s07(t, p, brace, face, end05_x)
            elif sid == "S08":
                s08(t, p, face)
            elif sid == "S09":
                s09(t, p, face)
            else:
                s10(t, p, face)
            p["exposure"] = ext_exposure if sid in ("S01", "S02") else int_exposure
            poses[f] = p
        if s["id"] == "S04":
            end04_x = poses[f1]["x"]
            end04_hooves = poses[f1]["hooves"]
        if s["id"] == "S05":
            end05_x = poses[f1]["x"]
        if s["id"] == "S07":
            STAND.update(x=poses[f1]["x"], hooves=poses[f1]["hooves"])
    for f, p in poses.items():
        s = C.shot_of(f)
        worst[f] = apply(rig, p, f, s["view"])
    # block slide and debris
    blk = E["block"]
    for f in range(1, C.TOTAL_FRAMES + 1):
        s = C.shot_of(f)
        t = (f - C.bf(s["f0"])) / C.FPS
        off = 0.0 if s["id"] in ("S01", "S02", "S03", "S04", "S05") else block_offset_at(t, s["id"])
        blk.location.x = C.BLOCK["x"] + off
        blk.keyframe_insert("location", index=0, frame=f)
        for o in bpy.data.objects:
            if o.name.startswith("BLOCK_DEBRIS_"):
                r = o["rest"]
                o.location.x = r[0] + off * (0.7 + 0.3 * (hash(o.name) % 7) / 7)
                o.keyframe_insert("location", index=0, frame=f)
    # doors: closed until S09, swing on their hinges (same angle law both leaves)
    for f in range(1, C.TOTAL_FRAMES + 1):
        s = C.shot_of(f)
        t = (f - C.bf(s["f0"])) / C.FPS
        if s["id"] == "S09":
            a = seg(t, [(0, 0.0), (0.25, 0.0), (2.0, 30.0)])
        elif s["id"] == "S10":
            a = seg(t, [(0, 30.0), (1.0, 52.0)])
        else:
            a = 0.0
        for h in E["hinges"]:
            h.rotation_euler.z = math.radians(-a if h.name.endswith("N") else a)
            h.keyframe_insert("rotation_euler", index=2, frame=f)
    # view visibility per shot (artwork sets switch only on cuts)
    for f in range(1, C.TOTAL_FRAMES + 1):
        s = C.shot_of(f)
        if f != C.bf(s["f0"]) and f != 1:
            continue
        for cname, view in (("MOO_SIDE_ART", "side"), ("MOO_REAR_ART", "rear"), ("MOO_Q3_ART", "q3")):
            for o in bpy.data.collections[cname].objects:
                if o.type != "MESH":
                    continue
                if o.name.endswith(("mouth_neutral", "mouth_strain", "mouth_smile", "mouth_breath")):
                    continue
                o.hide_render = view != s["view"]
                o.keyframe_insert("hide_render", frame=f)
    # mouths of a hidden view must stay hidden: AND with view visibility via per-frame keys (side + q3 only)
    for f, p in poses.items():
        s = C.shot_of(f)
        for nm in ("mouth_neutral", "mouth_strain", "mouth_smile", "mouth_breath"):
            so = rig["side"][2][nm]
            so.hide_render = not (s["view"] == "side" and nm == p["mouth"])
            so.keyframe_insert("hide_render", frame=f)
            qo = rig["q3"][2][nm]
            qo.hide_render = not (s["view"] == "q3" and nm == p["mouth"])
            qo.keyframe_insert("hide_render", frame=f)
    for o in bpy.data.objects:
        ad = o.animation_data
        if ad and ad.action:
            from bpy_extras import anim_utils
            cb = anim_utils.action_get_channelbag_for_slot(ad.action, ad.action_slot)
            for fc in cb.fcurves:
                if fc.data_path == "hide_render":
                    for k in fc.keyframe_points:
                        k.interpolation = "CONSTANT"
    # ------------------------------------------------------------------ cameras
    cams = {}
    P = poses
    m1 = P[C.bf(0)]
    cams["S01"] = camera("CAM_S01", coll_cam, 24, [(C.bf(0), (m1["x"] - 5.6, m1["y"] - 1.45, 1.2)), (C.bf(95), (m1["x"] - 5.1, m1["y"] - 1.45, 1.2))],
                         [(C.bf(0), (m1["x"] + 6.0, m1["y"] - 0.2, 1.75))], fstop=8.0)
    m2 = P[C.bf(96)]
    cams["S02"] = camera("CAM_S02", coll_cam, 85, [(C.bf(96), (m2["x"] + 0.58, C.PUDDLE["y"] - 1.70, 0.34))],
                         [(C.bf(96), (m2["x"] + 0.58, C.PUDDLE["y"] + 0.10, 0.235))], fstop=5.6)
    cams["S03"] = camera("CAM_S03", coll_cam, 35, [(C.bf(168), (S03["xa"] - 2.6, -0.32, 0.55)), (C.bf(263), (S03["xa"] - 0.55, -0.32, 0.55))],
                         [(C.bf(168), (S03["xa"] + 3.5, 0.1, 0.42)), (C.bf(263), (S03["xa"] + 4.6, 0.1, 0.40))], fstop=5.6)
    m4 = P[C.bf(264)]
    cams["S04"] = camera("CAM_S04", coll_cam, 50, [(C.bf(264), (m4["x"] + 0.24, -3.05, 0.40))], [(C.bf(264), (m4["x"] + 0.24, 0.0, 0.36))], fstop=5.6)
    m5 = P[C.bf(360)]
    cams["S05"] = camera("CAM_S05", coll_cam, 50, [(C.bf(360), (m5["x"] + 0.10, -2.75, 0.52))], [(C.bf(360), (m5["x"] + 0.12, 0.0, 0.44))], fstop=4.0)
    m6 = P[C.bf(456)]
    cams["S06"] = camera("CAM_S06", coll_cam, 50, [(C.bf(456), (m6["x"] + 0.28, -2.85, 0.18)), (C.bf(527), (m6["x"] + 0.36, -2.45, 0.19))],
                         [(C.bf(456), (m6["x"] + 0.28, 0.0, 0.40)), (C.bf(527), (m6["x"] + 0.36, 0.0, 0.38))], fstop=4.0)
    m7 = P[C.bf(528)]
    hu = m7["hooves"][("front", "near")][0]
    bface = face + block_offset_at(0.0, "S07")
    cx7 = (hu + bface) / 2 + 0.09
    cams["S07"] = camera("CAM_S07", coll_cam, 100, [(C.bf(528), (cx7, -2.35, 0.06))], [(C.bf(528), (cx7, -0.11, 0.10))], fstop=5.6)
    m8 = P[C.bf(576)]
    hw = side_head_world(rig, m8)
    cam8 = (hw[0] + 1.78, hw[1] + 1.62, hw[2] + 0.10)
    cams["S08"] = camera("CAM_S08", coll_cam, 85, [(C.bf(576), cam8)], [(C.bf(576), (hw[0], hw[1], hw[2] + 0.12))], fstop=2.8)
    for f in range(C.bf(576), C.bf(647) + 1):
        apply_q3(rig, P[f], f, cam8, hw)
    m9 = P[C.bf(648)]
    cams["S09"] = camera("CAM_S09", coll_cam, 35, [(C.bf(648), (m9["x"] - 1.35, -0.38, 0.78)), (C.bf(695), (m9["x"] - 1.28, -0.38, 0.78))],
                         [(C.bf(648), (C.BARN["x1"], 0.15, 1.25))], fstop=5.6)
    m10 = P[C.bf(696)]
    cams["S10"] = camera("CAM_S10", coll_cam, 24, [(C.bf(696), (m10["x"] - 3.3, -0.15, 1.25))], [(C.bf(696), (C.BARN["x1"], 0.0, 1.45))], fstop=8.0)
    sc.timeline_markers.clear()
    for s in C.SHOTS:
        mk = sc.timeline_markers.new(s["id"], frame=C.bf(s["f0"]))
        mk.camera = cams[s["id"]]
    sc.camera = cams["S01"]
    LOG["max_leg_overreach_m"] = round(max(worst.values()) * S, 4)
    LOG["overreach_by_shot_m"] = {sh["id"]: round(max(worst[f] for f in range(C.bf(sh["f0"]), C.bf(sh["f1"]) + 1)) * S, 4) for sh in C.SHOTS}
    LOG["poses"] = {f: {"shot": C.shot_of(f)["id"], "x": round(p["x"], 4), "hooves": {f"{k[0]}_{k[1]}": [round(v[0], 4), round(v[1], 4)] for k, v in p["hooves"].items()}}
                    for f, p in poses.items()}
    LOG["block_face_x"] = face
    return cams, poses
