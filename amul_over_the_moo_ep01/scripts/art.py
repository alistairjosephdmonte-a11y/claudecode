"""MOO_01 illustrated artwork: layered cutout parts for the side, rear, three-quarter-front (head) and front views, plus
the character sheet. STAND-IN: drawn from the written character spec because the approved master sheet was not supplied.
Replace the PNGs in art/moo_01/ with the approved artwork (same part names and pivots) and rebuild.

Look: pixel-textured outlines (outline drawn on a coarse pixel grid), soft grain-textured fills, two-tone discrete shading.
Coordinates are metres in each view (x forward/right, y up, ground at y = 0) at design scale; the rig applies MOO_SCALE.
    python3 scripts/art.py"""
import json
import math
import os
import random

from PIL import Image, ImageChops, ImageDraw, ImageFilter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "art", "moo_01")
PPM = {"side": 1500, "rear": 1500, "q3": 2600, "front": 1500}   # pixels per metre
PIX = 4                                                          # outline pixel size (px)

PAL = {"white": (247, 243, 234), "white_s": (214, 208, 196), "cream": (243, 233, 210), "cream_s": (219, 203, 176),
       "black": (32, 28, 27), "black_s": (20, 17, 16), "black_h": (62, 55, 52), "coral": (240, 138, 126),
       "coral_s": (214, 108, 100), "pink": (242, 167, 160), "tan": (210, 168, 110), "tan_s": (176, 134, 82),
       "hoof": (58, 46, 40), "line": (23, 17, 14), "eye": (18, 15, 15), "glint": (255, 252, 244)}

rng = random.Random(7)
GRAIN = None


# ------------------------------------------------------------------ shapes (metres -> polygons)
def superellipse(cx, cy, w, h, n=2.6, k=96, squash_bottom=1.0):
    pts = []
    for i in range(k):
        t = 2 * math.pi * i / k
        c, s = math.cos(t), math.sin(t)
        x = cx + w / 2 * math.copysign(abs(c) ** (2 / n), c)
        y = cy + h / 2 * math.copysign(abs(s) ** (2 / n), s) * (squash_bottom if s < 0 else 1)
        pts.append((x, y))
    return pts


def ellipse(cx, cy, w, h, k=72, rot=0.0):
    out = []
    for i in range(k):
        t = 2 * math.pi * i / k
        x, y = w / 2 * math.cos(t), h / 2 * math.sin(t)
        out.append((cx + x * math.cos(rot) - y * math.sin(rot), cy + x * math.sin(rot) + y * math.cos(rot)))
    return out


def blob(cx, cy, r, seed, k=40, wob=0.28, sx=1.0, sy=1.0):
    g = random.Random(seed)
    a = [g.uniform(-1, 1) for _ in range(4)]
    ph = [g.uniform(0, 6.28) for _ in range(4)]
    pts = []
    for i in range(k):
        t = 2 * math.pi * i / k
        rr = r * (1 + wob * (a[0] * math.sin(2 * t + ph[0]) + a[1] * math.sin(3 * t + ph[1]) * 0.6 + a[2] * math.sin(5 * t + ph[2]) * 0.3))
        pts.append((cx + rr * math.cos(t) * sx, cy + rr * math.sin(t) * sy))
    return pts


def capsule(x0, y0, x1, y1, w0, w1, k=24):
    """Tapered limb from (x0,y0) width w0 to (x1,y1) width w1, rounded ends."""
    ang = math.atan2(y1 - y0, x1 - x0)
    nx, ny = -math.sin(ang), math.cos(ang)
    pts = []
    for i in range(k + 1):                                  # end cap at (x1,y1)
        t = ang - math.pi / 2 + math.pi * i / k
        pts.append((x1 + w1 / 2 * math.cos(t), y1 + w1 / 2 * math.sin(t)))
    for i in range(k + 1):                                  # start cap
        t = ang + math.pi / 2 + math.pi * i / k
        pts.append((x0 + w0 / 2 * math.cos(t), y0 + w0 / 2 * math.sin(t)))
    return pts


def leaf(bx, by, tx, ty, width, k=30):
    """Ear shape: base (bx,by) to tip (tx,ty)."""
    ang = math.atan2(ty - by, tx - bx)
    L = math.hypot(tx - bx, ty - by)
    pts = []
    for i in range(k + 1):
        u = i / k
        w = width * math.sin(math.pi * u) ** 0.8 * (1 - 0.35 * u)
        pts.append((u, w / 2))
    for i in range(k, -1, -1):
        u = i / k
        w = width * math.sin(math.pi * u) ** 0.8 * (1 - 0.35 * u)
        pts.append((u, -w / 2 * 0.85))
    return [(bx + (u * L) * math.cos(ang) - v * math.sin(ang), by + (u * L) * math.sin(ang) + v * math.cos(ang)) for u, v in pts]


def horn(bx, by, tx, ty, w):
    return capsule(bx, by, tx, ty, w, w * 0.35, k=10)


# ------------------------------------------------------------------ raster helpers
class Canvas:
    def __init__(self, view, x0, y0, x1, y1):
        self.view, self.ppm = view, PPM[view]
        self.x0, self.y1 = x0, y1
        self.W, self.H = int((x1 - x0) * self.ppm), int((y1 - y0) * self.ppm)

    def px(self, pts):
        return [((x - self.x0) * self.ppm, (self.y1 - y) * self.ppm) for x, y in pts]

    def mask(self, *polys, holes=()):
        m = Image.new("L", (self.W * 2, self.H * 2), 0)
        d = ImageDraw.Draw(m)
        for p in polys:
            d.polygon([(x * 2, y * 2) for x, y in self.px(p)], fill=255)
        for p in holes:
            d.polygon([(x * 2, y * 2) for x, y in self.px(p)], fill=0)
        return m.resize((self.W, self.H), Image.LANCZOS)


def grain(size):
    global GRAIN
    if GRAIN is None or GRAIN.size[0] < size[0] or GRAIN.size[1] < size[1]:
        w, h = max(size[0], 512), max(size[1], 512)
        small = Image.effect_noise((w // 6 + 1, h // 6 + 1), 38).resize((w, h), Image.BICUBIC)
        fine = Image.effect_noise((w, h), 18)
        GRAIN = ImageChops.add(small, fine, scale=2.0)
    return GRAIN.crop((0, 0, size[0], size[1]))


def fill(mask, color, tex=0.045):
    """Soft textured fill: colour modulated by paper grain."""
    g = grain(mask.size)
    base = Image.new("RGB", mask.size, color)
    dark = Image.new("RGB", mask.size, tuple(int(c * (1 - tex)) for c in color))
    lite = Image.new("RGB", mask.size, tuple(min(255, int(c * (1 + tex * 0.6))) for c in color))
    rgb = Image.composite(lite, dark, g)
    rgb = Image.blend(base, rgb, 0.8)
    out = rgb.convert("RGBA")
    out.putalpha(mask)
    return out


def shade_mask(mask, dx, dy, soft=False):
    """Discrete shading: the part of the shape not covered by itself shifted toward the light (up-left)."""
    shifted = ImageChops.offset(mask, -dx, -dy)
    m = ImageChops.subtract(mask, shifted)
    m = m.point(lambda v: 255 if v > 90 else 0)
    if soft:
        m = m.filter(ImageFilter.GaussianBlur(1.2))
    return ImageChops.multiply(m, mask)


def outline(mask, width):
    """Pixel-textured outline around a shape (coarse pixel grid, slightly irregular)."""
    w, h = mask.size
    coarse = mask.resize((max(1, w // PIX), max(1, h // PIX)), Image.BILINEAR).point(lambda v: 255 if v > 110 else 0)
    k = max(3, (width // PIX) * 2 + 1)
    grown = coarse.filter(ImageFilter.MaxFilter(k))
    ring = ImageChops.subtract(grown, coarse.filter(ImageFilter.MinFilter(3)))
    ring = ring.resize((w, h), Image.NEAREST)
    return ring


class Part:
    def __init__(self, cv):
        self.cv = cv
        self.img = Image.new("RGBA", (cv.W, cv.H), (0, 0, 0, 0))
        self.solid = Image.new("L", (cv.W, cv.H), 0)

    def layer(self, mask, color, shade=None, sdx=0.018, sdy=-0.022, clip=None, line=True, lw=10):
        if clip is not None:
            mask = ImageChops.multiply(mask, clip)
        self.img.alpha_composite(fill(mask, PAL[color]))
        if shade:
            sm = shade_mask(mask, int(sdx * self.cv.ppm), int(sdy * self.cv.ppm))
            self.img.alpha_composite(fill(sm, PAL[shade], tex=0.03))
        self.solid = ImageChops.lighter(self.solid, mask)
        return mask

    def ink(self, mask, lw=10):
        ring = outline(mask, lw)
        ln = Image.new("RGBA", mask.size, PAL["line"] + (255,))
        ln.putalpha(ring)
        self.img.alpha_composite(ln)
        self.solid = ImageChops.lighter(self.solid, ring)

    def stroke(self, pts, width_m, color="line"):
        d = ImageDraw.Draw(self.img)
        p = self.cv.px(pts)
        w = max(PIX, int(width_m * self.cv.ppm) // PIX * PIX)
        d.line(p, fill=PAL[color] + (255,), width=w, joint="curve")
        for x, y in (p[0], p[-1]):
            d.ellipse((x - w / 2, y - w / 2, x + w / 2, y + w / 2), fill=PAL[color] + (255,))

    def dot(self, cx, cy, r, color):
        d = ImageDraw.Draw(self.img)
        (x, y), = self.cv.px([(cx, cy)])
        rr = r * self.cv.ppm
        d.ellipse((x - rr, y - rr, x + rr, y + rr), fill=PAL[color] + (255,))

    def save(self, name, pivot, parent, z, meta):
        bb = self.img.getbbox()
        if not bb:
            raise ValueError(name)
        x0, y0, x1, y1 = bb
        pad = 4
        x0, y0, x1, y1 = max(0, x0 - pad), max(0, y0 - pad), min(self.cv.W, x1 + pad), min(self.cv.H, y1 + pad)
        im = self.img.crop((x0, y0, x1, y1))
        path = os.path.join(OUT, f"{self.cv.view}_{name}.png")
        im.save(path, optimize=True)
        cv = self.cv
        meta[f"{cv.view}_{name}"] = {
            "view": cv.view, "part": name, "file": os.path.relpath(path, ROOT), "px": [im.width, im.height], "ppm": cv.ppm,
            "center_m": [cv.x0 + (x0 + x1) / 2 / cv.ppm, cv.y1 - (y0 + y1) / 2 / cv.ppm],
            "size_m": [im.width / cv.ppm, im.height / cv.ppm], "pivot_m": list(pivot), "parent": parent, "z": z}
        return im


# ------------------------------------------------------------------ SIDE VIEW (facing +x)
SIDE = dict(hip=(-0.27, 0.45), shoulder=(0.24, 0.47), knee_drop=0.22, leg_len=0.45, neck=(0.33, 0.64),
            ear=(0.47, 0.90), tail=(-0.40, 0.70), torso_c=(0.0, 0.56))


def side_parts(meta):
    cv = Canvas("side", -0.70, -0.02, 0.92, 1.12)
    torso = superellipse(0.0, 0.56, 0.82, 0.40, n=2.4, squash_bottom=0.92)
    # torso (with neck root) ------------------------------------------------
    P = Part(cv)
    neck = capsule(0.18, 0.56, 0.36, 0.66, 0.30, 0.24)
    m_t = cv.mask(torso, neck)
    P.layer(m_t, "white", "white_s", sdx=0.03, sdy=-0.05)
    patches = [blob(-0.20, 0.64, 0.12, 1, sx=1.3), blob(0.07, 0.69, 0.09, 2, sx=1.2), blob(-0.02, 0.43, 0.07, 3, sx=1.5),
               blob(0.26, 0.55, 0.06, 4)]
    m_p = cv.mask(*patches)
    P.layer(m_p, "black", "black_s", sdx=0.02, sdy=-0.03, clip=m_t)
    P.ink(m_t, 12)
    P.save("torso", SIDE["torso_c"], "root", 0.0, meta)
    # head (skull + muzzle), separate expression and feature parts ----------
    H = Part(cv)
    skull = superellipse(0.52, 0.78, 0.34, 0.30, n=2.2)
    jaw = ellipse(0.62, 0.69, 0.22, 0.16)
    m_h = cv.mask(skull, jaw)
    H.layer(m_h, "cream", "cream_s", sdx=0.02, sdy=-0.03)
    muzzle = superellipse(0.70, 0.705, 0.17, 0.155, n=2.3)
    m_m = cv.mask(muzzle)
    H.layer(m_m, "coral", "coral_s", sdx=0.012, sdy=-0.016)
    H.ink(ImageChops.lighter(m_h, m_m), 11)
    H.dot(0.755, 0.735, 0.012, "coral_s")
    H.save("head", SIDE["neck"], "neck", 0.03, meta)
    for nm, pts in {"mouth_neutral": [(0.705, 0.655), (0.74, 0.652), (0.765, 0.66)],
                    "mouth_strain": [(0.70, 0.66), (0.735, 0.648), (0.77, 0.652)],
                    "mouth_smile": [(0.695, 0.668), (0.725, 0.650), (0.76, 0.656), (0.778, 0.672)],
                    "mouth_breath": [(0.70, 0.655), (0.735, 0.645), (0.77, 0.655)]}.items():
        Mo = Part(cv)
        if nm == "mouth_breath":
            m = cv.mask(ellipse(0.738, 0.652, 0.05, 0.022))
            Mo.layer(m, "coral_s")
        Mo.stroke(pts, 0.008)
        Mo.save(nm, SIDE["neck"], "neck", 0.036, meta)
    E = Part(cv)
    m_e = cv.mask(ellipse(0.565, 0.815, 0.062, 0.085, rot=0.15))
    E.layer(m_e, "eye")
    E.dot(0.575, 0.832, 0.010, "glint")
    E.dot(0.556, 0.800, 0.004, "glint")
    E.save("eye", (0.565, 0.815), "neck", 0.04, meta)
    L = Part(cv)
    m_l = cv.mask(ellipse(0.565, 0.818, 0.076, 0.098, rot=0.15))
    L.layer(m_l, "cream", "cream_s", sdx=0.0, sdy=-0.01)
    L.stroke([(0.532, 0.808), (0.565, 0.797), (0.598, 0.808)], 0.006)
    L.save("lid", (0.565, 0.864), "neck", 0.045, meta)
    Ho = Part(cv)
    m_ho = cv.mask(horn(0.50, 0.915, 0.525, 0.985, 0.032))
    Ho.layer(m_ho, "tan", "tan_s", sdx=0.006, sdy=-0.006)
    Ho.ink(m_ho, 8)
    Ho.save("horn", SIDE["neck"], "neck", 0.025, meta)
    Ea = Part(cv)
    e_out = leaf(0.47, 0.90, 0.31, 0.95, 0.10)
    m_eo = cv.mask(e_out)
    Ea.layer(m_eo, "black", "black_s", sdx=0.006, sdy=-0.01)
    m_ei = cv.mask(leaf(0.455, 0.903, 0.345, 0.94, 0.05))
    Ea.layer(m_ei, "pink", clip=m_eo)
    Ea.ink(m_eo, 9)
    Ea.save("ear", SIDE["ear"], "neck", 0.05, meta)
    Ea2 = Part(cv)
    m_e2 = cv.mask(leaf(0.47, 0.905, 0.33, 0.975, 0.09))
    Ea2.layer(m_e2, "black_s")
    Ea2.ink(m_e2, 8)
    Ea2.save("ear_far", SIDE["ear"], "neck", -0.01, meta)
    # tail --------------------------------------------------------------------
    T = Part(cv)
    tx, ty = SIDE["tail"]
    m_tl = cv.mask(capsule(tx, ty, tx - 0.08, ty - 0.27, 0.035, 0.024))
    T.layer(m_tl, "white", "white_s", sdx=0.006, sdy=-0.004)
    m_tf = cv.mask(blob(tx - 0.085, ty - 0.30, 0.04, 9, wob=0.35, sy=1.4))
    T.layer(m_tf, "black", "black_s", sdx=0.006, sdy=-0.008)
    T.ink(ImageChops.lighter(m_tl, m_tf), 8)
    T.save("tail", SIDE["tail"], "torso", -0.015, meta)
    # legs: upper (hip/shoulder -> knee) and lower (knee -> ground incl. hoof); near and far ---------
    for which, (hx, hy) in (("rear", SIDE["hip"]), ("front", SIDE["shoulder"])):
        for side, z, dx in (("near", 0.02, 0.0), ("far", -0.02, 0.05)):
            x = hx + dx
            ky = hy - SIDE["knee_drop"]
            U = Part(cv)
            w0 = 0.15 if which == "rear" else 0.12
            m_u = cv.mask(capsule(x, hy + 0.02, x, ky, w0, 0.085))
            col, sh = ("white", "white_s") if side == "near" else ("white_s", "white_s")
            U.layer(m_u, col, sh if side == "near" else None, sdx=0.012, sdy=0.0)
            if which == "front" and side == "near":
                U.layer(cv.mask(blob(x, hy - 0.08, 0.05, 11, sy=1.4)), "black", clip=m_u)
            U.ink(m_u, 9)
            U.save(f"leg_{which}_{side}_upper", (x, hy), "torso", z, meta)
            Lo = Part(cv)
            m_lo = cv.mask(capsule(x, ky + 0.02, x, 0.055, 0.085, 0.07))
            Lo.layer(m_lo, col, sh if side == "near" else None, sdx=0.01, sdy=0.0)
            m_hf = cv.mask(superellipse(x + 0.012, 0.03, 0.09, 0.06, n=3.0))
            Lo.layer(m_hf, "hoof", sdx=0.0, sdy=0.0)
            Lo.ink(ImageChops.lighter(m_lo, m_hf), 9)
            Lo.save(f"leg_{which}_{side}_lower", (x, ky), f"leg_{which}_{side}_upper", z + 0.001, meta)


# ------------------------------------------------------------------ REAR VIEW (seen from behind; +x = MOO's right)
REAR = dict(torso_c=(0.0, 0.56), tail=(0.0, 0.74), head=(0.0, 0.74))


def rear_parts(meta):
    cv = Canvas("rear", -0.42, -0.02, 0.42, 1.08)
    P = Part(cv)
    body = superellipse(0.0, 0.57, 0.50, 0.42, n=2.3, squash_bottom=0.9)
    m_b = cv.mask(body)
    P.layer(m_b, "white", "white_s", sdx=0.03, sdy=-0.04)
    P.layer(cv.mask(blob(0.12, 0.66, 0.11, 21, sx=1.1), blob(-0.15, 0.50, 0.06, 22)), "black", "black_s", sdx=0.02, sdy=-0.02, clip=m_b)
    P.ink(m_b, 12)
    P.save("torso", REAR["torso_c"], "root", 0.0, meta)
    H = Part(cv)
    m_h = cv.mask(superellipse(0.0, 0.83, 0.34, 0.24, n=2.2))
    H.layer(m_h, "cream", "cream_s", sdx=0.015, sdy=-0.02)
    H.layer(cv.mask(blob(0.06, 0.90, 0.06, 31, sx=1.4)), "black", clip=m_h)
    H.ink(m_h, 10)
    H.save("head", REAR["head"], "neck", -0.03, meta)
    for nm, s in (("ear_l", -1), ("ear_r", 1)):
        E = Part(cv)
        m_o = cv.mask(leaf(s * 0.14, 0.86, s * 0.30, 0.90, 0.095))
        E.layer(m_o, "black", "black_s", sdx=0.006, sdy=-0.01)
        E.ink(m_o, 9)
        E.save(nm, (s * 0.14, 0.86), "neck", -0.025, meta)
        Hn = Part(cv)
        m_hn = cv.mask(horn(s * 0.07, 0.92, s * 0.085, 0.985, 0.03))
        Hn.layer(m_hn, "tan", "tan_s", sdx=0.005, sdy=-0.005)
        Hn.ink(m_hn, 8)
        Hn.save(f"horn_{nm[-1]}", (s * 0.07, 0.92), "neck", -0.026, meta)
    T = Part(cv)
    m_t = cv.mask(capsule(0.0, 0.74, 0.015, 0.47, 0.035, 0.026))
    T.layer(m_t, "white", "white_s", sdx=0.006, sdy=0.0)
    m_f = cv.mask(blob(0.017, 0.44, 0.042, 41, wob=0.35, sy=1.4))
    T.layer(m_f, "black", "black_s", sdx=0.005, sdy=-0.006)
    T.ink(ImageChops.lighter(m_t, m_f), 8)
    T.save("tail", REAR["tail"], "torso", 0.02, meta)
    for nm, x, z, near in (("leg_rear_l", -0.125, 0.01, True), ("leg_rear_r", 0.125, 0.01, True),
                           ("leg_front_l", -0.085, -0.02, False), ("leg_front_r", 0.085, -0.02, False)):
        L = Part(cv)
        top = 0.44 if near else 0.40
        m_l = cv.mask(capsule(x, top, x * 1.02, 0.06, 0.13 if near else 0.085, 0.075 if near else 0.065))
        L.layer(m_l, "white" if near else "white_s", "white_s" if near else None, sdx=0.012, sdy=0.0)
        m_hf = cv.mask(superellipse(x * 1.02, 0.03, 0.085 if near else 0.07, 0.06, n=3.0))
        L.layer(m_hf, "hoof")
        L.ink(ImageChops.lighter(m_l, m_hf), 9)
        L.save(nm, (x, top), "torso", z, meta)


# ------------------------------------------------------------------ THREE-QUARTER FRONT HEAD + SHOULDERS (looking to screen left)
def rim_for(meta, key, dx_m=-0.009, dy_m=0.004):
    """Backlight rim: a soft warm crescent on the silhouette edge facing the light (screen left / up)."""
    v = meta[key]
    im = Image.open(os.path.join(ROOT, v["file"]))
    pad = 40
    a = Image.new("L", (im.width + 2 * pad, im.height + 2 * pad), 0)
    a.paste(im.getchannel("A"), (pad, pad))
    ppm = v["ppm"]
    sh = ImageChops.offset(a, int(dx_m * ppm), -int(dy_m * ppm)).filter(ImageFilter.GaussianBlur(4))
    rim = ImageChops.subtract(sh, a).filter(ImageFilter.GaussianBlur(2))
    out = Image.new("RGBA", a.size, (255, 200, 140, 0))
    out.putalpha(rim.point(lambda x: int(x * 0.7)))
    nm = "q3rim_" + v["part"]
    path = os.path.join(OUT, f"{nm}.png")
    out.save(path, optimize=True)
    meta[nm] = dict(v, part="rim_" + v["part"], file=os.path.relpath(path, ROOT), px=[out.width, out.height],
                    size_m=[out.width / ppm, out.height / ppm], z=v["z"] - 0.002)


def q3_parts(meta):
    cv = Canvas("q3", -0.40, -0.62, 0.40, 0.48)
    N = Part(cv)
    m_n = cv.mask(superellipse(0.03, -0.25, 0.52, 0.70, n=2.2))
    N.layer(m_n, "white", "white_s", sdx=0.03, sdy=-0.04)
    N.layer(cv.mask(blob(0.18, -0.12, 0.12, 51, sx=1.1), blob(-0.17, -0.30, 0.08, 52)), "black", "black_s", sdx=0.02, sdy=-0.02, clip=m_n)
    N.ink(m_n, 14)
    N.save("neck", (0.0, -0.05), "root", -0.05, meta)
    H = Part(cv)
    m_f = cv.mask(superellipse(0.0, 0.17, 0.40, 0.35, n=2.15))
    H.layer(m_f, "cream", "cream_s", sdx=0.025, sdy=-0.03)
    m_m = cv.mask(superellipse(-0.06, 0.045, 0.25, 0.155, n=2.3))
    H.layer(m_m, "coral", "coral_s", sdx=0.012, sdy=-0.018)
    H.ink(ImageChops.lighter(m_f, m_m), 13)
    H.dot(-0.13, 0.065, 0.016, "coral_s")
    H.dot(-0.005, 0.07, 0.019, "coral_s")
    H.save("head", (0.0, 0.0), "neck", 0.0, meta)
    for nm, pts in {"mouth_neutral": [(-0.13, 0.002), (-0.06, -0.006), (0.01, 0.0)],
                    "mouth_strain": [(-0.13, 0.004), (-0.06, -0.010), (0.01, -0.002)],
                    "mouth_smile": [(-0.135, 0.012), (-0.10, -0.006), (-0.04, -0.010), (0.01, 0.002), (0.025, 0.016)],
                    "mouth_breath": [(-0.12, 0.002), (-0.06, -0.006), (0.0, 0.0)]}.items():
        Mo = Part(cv)
        if nm == "mouth_breath":
            Mo.layer(cv.mask(ellipse(-0.06, -0.004, 0.07, 0.03)), "coral_s")
        Mo.stroke(pts, 0.009)
        Mo.save(nm, (0.0, 0.0), "head", 0.01, meta)
    for nm, (cx, cy, w, h) in {"eye_far": (-0.115, 0.205, 0.062, 0.088), "eye_near": (0.065, 0.215, 0.078, 0.104)}.items():
        E = Part(cv)
        E.layer(cv.mask(ellipse(cx, cy, w, h, rot=-0.1)), "eye")
        E.dot(cx - w * 0.12, cy + h * 0.2, w * 0.17, "glint")
        E.dot(cx + w * 0.18, cy - h * 0.22, w * 0.06, "glint")
        E.save(nm, (cx, cy), "head", 0.015, meta)
        Ld = Part(cv)
        Ld.layer(cv.mask(ellipse(cx, cy + 0.003, w * 1.22, h * 1.18, rot=-0.1)), "cream", "cream_s", sdx=0.0, sdy=-0.008)
        Ld.stroke([(cx - w * 0.55, cy - h * 0.1), (cx, cy - h * 0.25), (cx + w * 0.55, cy - h * 0.1)], 0.006)
        Ld.save(nm.replace("eye", "lid"), (cx, cy + h * 0.6), "head", 0.02, meta)
    for nm, b, t, wd, z in (("ear_far", (-0.17, 0.27), (-0.34, 0.31), 0.10, -0.01), ("ear_near", (0.16, 0.28), (0.36, 0.32), 0.12, 0.02)):
        E = Part(cv)
        m_o = cv.mask(leaf(b[0], b[1], t[0], t[1], wd))
        E.layer(m_o, "black", "black_s", sdx=0.006, sdy=-0.01)
        f = 0.6
        E.layer(cv.mask(leaf(b[0] + (t[0] - b[0]) * 0.12, b[1], b[0] + (t[0] - b[0]) * 0.85, b[1] + (t[1] - b[1]) * 0.85, wd * f)), "pink", clip=m_o)
        E.ink(m_o, 10)
        E.save(nm, b, "head", z, meta)
    for nm, b, t in (("horn_far", (-0.075, 0.33), (-0.09, 0.40)), ("horn_near", (0.07, 0.335), (0.085, 0.41))):
        Hn = Part(cv)
        m = cv.mask(horn(b[0], b[1], t[0], t[1], 0.034))
        Hn.layer(m, "tan", "tan_s", sdx=0.006, sdy=-0.006)
        Hn.ink(m, 9)
        Hn.save(nm, b, "head", -0.005, meta)


# ------------------------------------------------------------------ FRONT VIEW (sheet reference)
def front_sheet():
    cv = Canvas("front", -0.40, -0.02, 0.40, 1.08)
    P = Part(cv)
    for x in (-0.10, 0.10):
        m = cv.mask(capsule(x, 0.44, x, 0.06, 0.10, 0.075))
        P.layer(m, "white", "white_s", sdx=0.01, sdy=0.0)
        P.layer(cv.mask(superellipse(x, 0.03, 0.085, 0.06, n=3.0)), "hoof")
        P.ink(ImageChops.lighter(m, cv.mask(superellipse(x, 0.03, 0.085, 0.06, n=3.0))), 9)
    m_b = cv.mask(superellipse(0.0, 0.56, 0.42, 0.40, n=2.3))
    P.layer(m_b, "white", "white_s", sdx=0.03, sdy=-0.04)
    P.layer(cv.mask(blob(0.12, 0.62, 0.08, 61)), "black", clip=m_b)
    P.ink(m_b, 12)
    for s in (-1, 1):
        m = cv.mask(leaf(s * 0.15, 0.86, s * 0.33, 0.90, 0.11))
        P.layer(m, "black", "black_s", sdx=0.006, sdy=-0.01)
        P.layer(cv.mask(leaf(s * 0.17, 0.865, s * 0.30, 0.895, 0.06)), "pink", clip=m)
        P.ink(m, 9)
        mh = cv.mask(horn(s * 0.07, 0.93, s * 0.085, 1.0, 0.032))
        P.layer(mh, "tan", "tan_s", sdx=0.005, sdy=-0.005)
        P.ink(mh, 8)
    m_f = cv.mask(superellipse(0.0, 0.79, 0.36, 0.33, n=2.15))
    P.layer(m_f, "cream", "cream_s", sdx=0.02, sdy=-0.03)
    m_m = cv.mask(superellipse(0.0, 0.67, 0.22, 0.14, n=2.3))
    P.layer(m_m, "coral", "coral_s", sdx=0.01, sdy=-0.015)
    P.ink(ImageChops.lighter(m_f, m_m), 11)
    for s in (-1, 1):
        P.layer(cv.mask(ellipse(s * 0.085, 0.82, 0.068, 0.092)), "eye")
        P.dot(s * 0.085 - 0.008, 0.838, 0.011, "glint")
        P.dot(s * 0.05, 0.685, 0.014, "coral_s")
    P.stroke([(-0.05, 0.625), (0.0, 0.618), (0.05, 0.625)], 0.008)
    return P.img


def composite_view(meta, view, pose=None):
    """Assemble a view's parts at rest (for the sheet)."""
    items = sorted([v for v in meta.values() if v["view"] == view and not v["part"].startswith(("mouth_", "rim_")) or
                    (v["view"] == view and v["part"] == "mouth_neutral")], key=lambda v: v["z"])
    items = [v for v in items if not v["part"].startswith("lid")]
    xs = [v["center_m"][0] - v["size_m"][0] / 2 for v in items] + [v["center_m"][0] + v["size_m"][0] / 2 for v in items]
    ys = [v["center_m"][1] - v["size_m"][1] / 2 for v in items] + [v["center_m"][1] + v["size_m"][1] / 2 for v in items]
    ppm = PPM[view]
    x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
    im = Image.new("RGBA", (int((x1 - x0) * ppm) + 2, int((y1 - y0) * ppm) + 2), (0, 0, 0, 0))
    for v in items:
        p = Image.open(os.path.join(ROOT, v["file"]))
        im.alpha_composite(p, (int((v["center_m"][0] - v["size_m"][0] / 2 - x0) * ppm), int((y1 - v["center_m"][1] - v["size_m"][1] / 2) * ppm)))
    return im


def sheet(meta):
    from PIL import ImageFont
    W, Hh = 3600, 2200
    S = Image.new("RGB", (W, Hh), (236, 230, 218))
    d = ImageDraw.Draw(S)
    fb = ImageFont.truetype("/usr/share/fonts/opentype/inter/Inter-Bold.otf", 64)
    fr = ImageFont.truetype("/usr/share/fonts/opentype/inter/Inter-Regular.otf", 30)
    fs = ImageFont.truetype("/usr/share/fonts/opentype/inter/Inter-SemiBold.otf", 34)
    d.text((80, 60), "MOO_01 · character sheet (stand-in)", font=fb, fill=(30, 26, 24))
    d.text((80, 150), "Drawn from the written Episode 01 spec because the approved master sheet was not supplied. "
                      "Replace art/moo_01/*.png with the approved artwork (same part names and pivots).", font=fr, fill=(110, 60, 50))
    views = [("side", composite_view(meta, "side")), ("rear", composite_view(meta, "rear")),
             ("front", front_sheet()), ("three-quarter head", composite_view(meta, "q3"))]
    scale = 1050 / 1.12 / 1500
    x = 80
    for name, im in views:
        k = scale * (1500 / 2600 * 1.25 if name.startswith("three") else 1.0)
        im2 = im.resize((max(1, int(im.width * k)), max(1, int(im.height * k))), Image.LANCZOS)
        y = 1350 - im2.height
        S.paste(im2, (x, y), im2)
        d.text((x, 1380), name, font=fs, fill=(30, 26, 24))
        x += im2.width + 140
    d.line((80, 1352, W - 80, 1352), fill=(160, 150, 136), width=3)
    notes = ["height ≈ 0.90 m to top of head · body ≈ 1.10 m nose to rump (tail excluded) · rig scale 0.95 applied in Blender",
             "cream-white oversized face · large oval black eyes · coral-pink rounded muzzle · two small tan horns",
             "large black ears with pink interiors · irregular black patches (fixed: large patch high on the right flank and rump, shoulder, belly, front-right leg)",
             "four bovine legs · short tail with black tuft · pixel-textured outline · grain-textured fills · two-tone shading",
             "rig controls: head pitch/yaw, ear pivots, eye direction, blink lids, muzzle shapes (neutral / strain / breath / smile),",
             "tail, four-leg gait with planted-hoof IK, torso compression, breathing, weight transfer"]
    for i, t in enumerate(notes):
        d.text((80, 1480 + i * 52), t, font=fr, fill=(40, 36, 34))
    S.save(os.path.join(ROOT, "delivery", "MOO_01_character_sheet_STANDIN.png"))


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    meta = {}
    side_parts(meta)
    rear_parts(meta)
    q3_parts(meta)
    for k in ("q3_head", "q3_neck", "q3_ear_far", "q3_ear_near", "q3_horn_far", "q3_horn_near"):
        rim_for(meta, k)
    json.dump({"note": "STAND-IN artwork drawn from the written spec; approved master sheet not supplied", "parts": meta},
              open(os.path.join(ROOT, "metadata", "moo_parts.json"), "w"), indent=1)
    sheet(meta)
    print("PARTS", len(meta))
