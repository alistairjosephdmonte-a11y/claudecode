"""Original placeholder textures (no licensed artwork or logos).
    python3 scripts/textures.py   ->  textures/*.png"""
import math
import os
import random
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import config as C  # noqa: E402

FB = "/usr/share/fonts/opentype/inter/Inter-Black.otf"
FR = "/usr/share/fonts/opentype/inter/Inter-Bold.otf"


def hx(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


PINK, CYAN, ORANGE, PURPLE, NAVY = (hx(C.PAL[k]) for k in ("pink", "cyan", "orange", "purple", "navy"))


def lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def sunset(w, h, horizon=0.62):
    im = Image.new("RGB", (w, h))
    px = im.load()
    stops = [(0.0, NAVY), (0.35, PURPLE), (0.55, PINK), (horizon, ORANGE)]
    for y in range(h):
        t = y / h
        if t >= horizon:
            c = lerp(NAVY, PURPLE, min(1, (t - horizon) / (1 - horizon)) * 0.6)
        else:
            for (t0, c0), (t1, c1) in zip(stops, stops[1:]):
                if t0 <= t <= t1:
                    c = lerp(c0, c1, (t - t0) / (t1 - t0))
                    break
        for x in range(w):
            px[x, y] = c
    return im


def sun(d, cx, cy, r, h):
    for i in range(int(r * 2)):
        y = cy - r + i
        if y > cy and (int((y - cy) / (r * 0.12))) % 2 == 1:
            continue
        hw = math.sqrt(max(0, r * r - (y - cy) ** 2))
        d.line([(cx - hw, y), (cx + hw, y)], fill=lerp(ORANGE, PINK, i / (2 * r)))


def palm(d, x, base, hgt, lean, col, s=1.0):
    pts = [(x + lean * (t ** 1.6) * hgt, base - t * hgt) for t in [i / 20 for i in range(21)]]
    d.line(pts, fill=col, width=int(9 * s))
    tx, ty = pts[-1]
    for k in range(9):
        a = -math.pi / 2 + (k - 4) * 0.42
        fr = [(tx + math.cos(a + 0.9 * t * (1 if a > -math.pi / 2 else -1)) * 95 * s * t,
               ty + math.sin(a) * 60 * s * t + 70 * s * t * t) for t in [i / 10 for i in range(11)]]
        d.line(fr, fill=col, width=int(7 * s))


def scanlines(im, strength=0.22, period=3):
    px = im.load()
    for y in range(0, im.height, period):
        for x in range(im.width):
            r, g, b = px[x, y]
            px[x, y] = (int(r * (1 - strength)), int(g * (1 - strength)), int(b * (1 - strength)))
    return im


def vignette(im, k=0.55):
    w, h = im.size
    m = Image.new("L", (w, h))
    pm = m.load()
    for y in range(h):
        for x in range(w):
            dx, dy = (x - w / 2) / (w / 2), (y - h / 2) / (h / 2)
            pm[x, y] = int(255 * max(0.0, 1 - k * (dx * dx + dy * dy) ** 1.2))
    return Image.composite(im, Image.new("RGB", (w, h)), m)


def centered(d, cx, y, text, font, fill):
    w = d.textlength(text, font=font)
    d.text((cx - w / 2, y), text, font=font, fill=fill)


def disc_label():
    S = 1024
    im = sunset(S, S, 0.6)
    d = ImageDraw.Draw(im)
    sun(d, S / 2, S * 0.56, S * 0.17, S)
    for x, l, h in [(190, -0.25, 330), (830, 0.25, 360), (700, 0.18, 250)]:
        palm(d, x, S * 0.74, h, l, NAVY, 1.3)
    d.rectangle([0, S * 0.74, S, S], fill=NAVY)
    centered(d, S / 2, S * 0.17, "VICE CITY", ImageFont.truetype(FB, 120), (255, 255, 255))
    centered(d, S / 2, S * 0.80, "DISC_01 · PLACEHOLDER LABEL", ImageFont.truetype(FR, 38), CYAN)
    centered(d, S / 2, S * 0.85, "no licensed artwork", ImageFont.truetype(FR, 30), (200, 200, 220))
    m = Image.new("L", (S, S), 0)
    md = ImageDraw.Draw(m)
    md.ellipse([0, 0, S - 1, S - 1], fill=255)
    hr = S / 2 * C.DISC["hole_r"] / C.DISC["r"] * 2.3              # clamp ring + hole stay unprinted
    md.ellipse([S / 2 - hr, S / 2 - hr, S / 2 + hr, S / 2 + hr], fill=0)
    out = Image.composite(im, Image.new("RGB", (S, S), (205, 208, 214)), m)
    out.save(os.path.join(C.P["tex"], "disc_label.png"))


def crt_standby():
    w, h = 1024, 768
    im = Image.new("RGB", (w, h))
    d = ImageDraw.Draw(im)
    for y in range(h):
        d.line([(0, y), (w, y)], fill=lerp((4, 18, 30), (10, 70, 86), 1 - abs(y / h - 0.5) * 1.6))
    for i in range(14):
        rr = 60 + i * 36
        d.ellipse([w / 2 - rr, h / 2 - rr * 0.6, w / 2 + rr, h / 2 + rr * 0.6], outline=lerp((20, 90, 110), (6, 30, 40), i / 14), width=3)
    vignette(scanlines(im, 0.25)).save(os.path.join(C.P["tex"], "crt_standby.png"))


def crt_title():
    w, h = 1024, 768
    im = sunset(w, h, 0.64)
    d = ImageDraw.Draw(im)
    sun(d, w / 2, h * 0.58, 170, h)
    for i in range(1, 16):                                    # perspective grid
        y = h * 0.66 + (i / 15) ** 1.8 * h * 0.34
        d.line([(0, y), (w, y)], fill=PINK, width=2)
    for i in range(-12, 13):
        d.line([(w / 2 + i * 22, h * 0.66), (w / 2 + i * 150, h)], fill=PINK, width=2)
    for x, l, hh in [(120, -0.2, 330), (230, -0.1, 240), (900, 0.22, 360), (800, 0.12, 250)]:
        palm(d, x, h * 0.70, hh, l, NAVY, 1.15)
    glow = Image.new("RGB", (w, h))
    gd = ImageDraw.Draw(glow)
    f = ImageFont.truetype(FB, 132)
    centered(gd, w / 2, h * 0.13, "VICE CITY", f, PINK)
    gl = np.asarray(glow.filter(ImageFilter.GaussianBlur(16)), dtype=float)
    im = Image.fromarray(np.clip(np.asarray(im, dtype=float) + gl * 1.4, 0, 255).astype("uint8"))
    d = ImageDraw.Draw(im)
    centered(d, w / 2, h * 0.13, "VICE CITY", f, (255, 236, 248))
    centered(d, w / 2, h * 0.34, "PRESS START", ImageFont.truetype(FR, 40), CYAN)
    centered(d, w / 2, h * 0.92, "title art placeholder · no licensed artwork", ImageFont.truetype(FR, 22), (230, 220, 240))
    vignette(scanlines(im, 0.22)).save(os.path.join(C.P["tex"], "crt_title.png"))


def posters():
    w, h = 600, 840
    a = sunset(w, h, 0.55)
    d = ImageDraw.Draw(a)
    sun(d, w / 2, h * 0.5, 150, h)
    d.rectangle([0, h * 0.55, w, h], fill=NAVY)
    centered(d, w / 2, h * 0.07, "NEON NIGHTS", ImageFont.truetype(FB, 64), (255, 240, 250))
    a.save(os.path.join(C.P["tex"], "poster_a.png"))
    b = Image.new("RGB", (w, h), NAVY)
    d = ImageDraw.Draw(b)
    for i in range(10):
        d.rectangle([40 + i * 8, 120 + i * 50, w - 40 - i * 8, 150 + i * 50], fill=[PINK, CYAN, ORANGE, PURPLE][i % 4])
    centered(d, w / 2, h * 0.8, "RETRO RACER", ImageFont.truetype(FB, 60), CYAN)
    b.save(os.path.join(C.P["tex"], "poster_b.png"))


def shirt():
    """Teal tropical shirt (TOMMY_01 sheet): navy and pale palm leaves on teal."""
    S = 512
    rnd = random.Random(4)
    im = Image.new("RGB", (S, S), (38, 168, 170))
    d = ImageDraw.Draw(im)
    for _ in range(60):
        x, y, L = rnd.uniform(0, S), rnd.uniform(0, S), rnd.uniform(40, 80)
        a = rnd.uniform(0, 2 * math.pi)
        col = rnd.choice([NAVY, NAVY, (20, 70, 90), (225, 236, 230), (240, 190, 200)])
        for k in range(-4, 5):
            b = a + k * 0.16
            tip = (x + math.cos(b) * L, y + math.sin(b) * L)
            n = (math.cos(b + math.pi / 2) * L * 0.07, math.sin(b + math.pi / 2) * L * 0.07)
            mid = (x + math.cos(b) * L * 0.5, y + math.sin(b) * L * 0.5)
            d.polygon([(x, y), (mid[0] + n[0], mid[1] + n[1]), tip, (mid[0] - n[0], mid[1] - n[1])], fill=col)
    im.save(os.path.join(C.P["tex"], "shirt_tropical.png"))


def plaid():
    S = 256
    im = Image.new("RGB", (S, S), (44, 52, 92))
    d = ImageDraw.Draw(im)
    for i in range(0, S, 64):
        d.rectangle([i, 0, i + 18, S], fill=(150, 50, 70))
        d.rectangle([0, i, S, i + 18], fill=(150, 50, 70))
        d.rectangle([i + 36, 0, i + 40, S], fill=(220, 200, 170))
        d.rectangle([0, i + 36, S, i + 40], fill=(220, 200, 170))
    im.save(os.path.join(C.P["tex"], "plaid.png"))


if __name__ == "__main__":
    os.makedirs(C.P["tex"], exist_ok=True)
    disc_label()
    crt_standby()
    crt_title()
    posters()
    shirt()
    plaid()
    print("TEXTURES", sorted(os.listdir(C.P["tex"])))
