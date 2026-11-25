"""Draws the flat 2D BOX_01 layer set and the two presentation-screen slides (system python3 + PIL).
    python3 scripts/art_box.py
Layers are transparent PNGs; every BOX_01 layer shares one 1000 px = 0.40 m scale so the rig keeps exact proportions.
"""
import math
import os
import random

from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "art")
os.makedirs(OUT, exist_ok=True)
INK = (22, 18, 16, 255)
KRAFT = (214, 165, 98, 255)
KRAFT_SIDE = (176, 128, 70, 255)
KRAFT_FLAP = (226, 184, 122, 255)
RED = (196, 38, 34, 255)
WHITE = (250, 248, 242, 255)
LW = 14
SS = 2   # supersample


def canvas(w=1000, h=1000):
    return Image.new("RGBA", (w * SS, h * SS), (0, 0, 0, 0))


def S(pts):
    return [(x * SS, y * SS) for x, y in pts]


def poly(d, pts, fill, lw=LW):
    d.polygon(S(pts), fill=fill)
    d.line(S(pts + [pts[0]]), fill=INK, width=lw * SS, joint="curve")


def save(im, name):
    im = im.resize((im.width // SS, im.height // SS), Image.LANCZOS)
    im.save(os.path.join(OUT, name))


def speckle(im, box, n=260, seed=3):
    """Hand-printed halftone speckle on the kraft faces."""
    d = ImageDraw.Draw(im)
    r = random.Random(seed)
    x0, y0, x1, y1 = box
    for _ in range(n):
        x, y = r.uniform(x0, x1), r.uniform(y0, y1)
        if im.getpixel((int(x * SS), int(y * SS)))[3] == 0:
            continue
        s = r.uniform(2, 5)
        d.ellipse(S([(x - s, y - s), (x + s, y + s)]), fill=(150, 98, 48, 120))


# body: front face 300..700 x 420..900, side face to the right, flaps on top
FRONT = [(300, 420), (700, 420), (700, 900), (300, 900)]
SIDE = [(700, 420), (790, 360), (790, 830), (700, 900)]


def body(open_flaps):
    im = canvas()
    d = ImageDraw.Draw(im)
    if open_flaps:
        poly(d, [(300, 420), (700, 420), (760, 250), (250, 280)], KRAFT_FLAP)        # back flap, wide open
        poly(d, [(300, 420), (180, 330), (170, 250), (300, 360)], KRAFT_FLAP)        # left flap
        poly(d, [(790, 360), (900, 230), (930, 300), (790, 420)], KRAFT_FLAP)        # right flap
    else:
        poly(d, [(300, 420), (700, 420), (690, 330), (320, 345)], KRAFT_FLAP)        # back flap, ajar
        poly(d, [(700, 420), (790, 360), (830, 280), (730, 330)], KRAFT_FLAP)
    poly(d, SIDE, KRAFT_SIDE)
    poly(d, FRONT, KRAFT)
    d.polygon(S([(300, 800), (700, 800), (700, 835), (300, 835)]), fill=RED)       # red identification stripe
    d.polygon(S([(700, 800), (790, 735), (790, 770), (700, 835)]), fill=(150, 30, 28, 255))
    d.line(S([(300, 800), (700, 800)]), fill=INK, width=5 * SS)
    d.line(S([(300, 835), (700, 835)]), fill=INK, width=5 * SS)
    if open_flaps:
        poly(d, [(300, 420), (700, 420), (650, 560), (340, 560)], (60, 40, 25, 255), lw=8)   # empty dark inside
        poly(d, [(300, 420), (220, 520), (230, 470), (300, 380)], KRAFT_FLAP)             # front flap folded down
    else:
        poly(d, [(300, 420), (700, 420), (660, 450), (340, 450)], KRAFT_FLAP, lw=8)       # front flap edge
    speckle(im, (300, 420, 790, 900))
    d.line(S([(498, 420), (498, 470)]), fill=INK, width=6 * SS)                         # tape seam
    poly(d, FRONT, None) if False else d.line(S(FRONT + [FRONT[0]]), fill=INK, width=LW * SS, joint="curve")
    return im


save(body(False), "box_body_closed.png")
save(body(True), "box_body_open.png")

# faces: drawn centred on the front face (500, 640)


def eyes(kind):
    im = canvas()
    d = ImageDraw.Draw(im)
    for cx in (430, 570):
        if kind == "open":
            d.ellipse(S([(cx - 40, 560), (cx + 40, 670)]), fill=WHITE, outline=INK, width=9 * SS)
            d.ellipse(S([(cx - 18, 600), (cx + 22, 660)]), fill=INK)
            d.ellipse(S([(cx - 6, 608), (cx + 6, 622)]), fill=WHITE)
        elif kind == "happy":
            d.arc(S([(cx - 38, 590), (cx + 38, 660)]), 190, 350, fill=INK, width=12 * SS)
        elif kind == "sad":
            d.ellipse(S([(cx - 34, 590), (cx + 34, 670)]), fill=WHITE, outline=INK, width=9 * SS)
            d.ellipse(S([(cx - 15, 625), (cx + 17, 668)]), fill=INK)
            k = -1 if cx < 500 else 1
            d.line(S([(cx - 40, 570 - 18 * k), (cx + 40, 570 + 18 * k)]), fill=INK, width=10 * SS)
    return im


def mouth(kind):
    im = canvas()
    d = ImageDraw.Draw(im)
    if kind == "open":
        d.chord(S([(420, 650), (580, 800)]), 0, 180, fill=(110, 20, 20, 255), outline=INK, width=9 * SS)
        d.chord(S([(455, 735), (545, 800)]), 0, 180, fill=(230, 80, 80, 255))
        d.line(S([(420, 725), (580, 725)]), fill=INK, width=9 * SS)
    elif kind == "smile":
        d.arc(S([(430, 650), (570, 760)]), 20, 160, fill=INK, width=12 * SS)
    elif kind == "sad":
        d.arc(S([(445, 730), (555, 810)]), 200, 340, fill=INK, width=12 * SS)
    return im


for k in ("open", "happy", "sad"):
    save(eyes(k), f"box_eyes_{k}.png")
for k in ("open", "smile", "sad"):
    save(mouth(k), f"box_mouth_{k}.png")

# limb: black rounded stroke, pivot at the top centre (canvas 200x400 -> 0.08 x 0.16 m)
im = canvas(200, 400)
d = ImageDraw.Draw(im)
d.line(S([(100, 20), (100, 380)]), fill=INK, width=22 * SS)
d.ellipse(S([(89, 9), (111, 31)]), fill=INK)
d.ellipse(S([(89, 369), (111, 391)]), fill=INK)
save(im, "box_limb.png")

# glove: white cartoon glove, wrist at top centre (canvas 300x300)
im = canvas(300, 300)
d = ImageDraw.Draw(im)
for (x0, y0, x1, y1) in ((70, 120, 120, 260), (115, 130, 165, 285), (160, 125, 210, 270), (200, 105, 255, 210)):
    d.rounded_rectangle(S([(x0, y0), (x1, y1)]), radius=24 * SS, fill=WHITE, outline=INK, width=9 * SS)
d.ellipse(S([(60, 60), (230, 200)]), fill=WHITE, outline=INK, width=9 * SS)
d.rounded_rectangle(S([(95, 20), (195, 80)]), radius=14 * SS, fill=WHITE, outline=INK, width=9 * SS)
for x in (125, 165):
    d.line(S([(x, 140), (x, 180)]), fill=INK, width=5 * SS)
save(im, "box_glove.png")

# sneaker: side view, ankle at top centre (canvas 360x220)
im = canvas(360, 220)
d = ImageDraw.Draw(im)
d.rounded_rectangle(S([(60, 150), (330, 200)]), radius=20 * SS, fill=WHITE, outline=INK, width=9 * SS)
d.pieslice(S([(70, 40), (320, 250)]), 180, 360, fill=(205, 40, 36, 255), outline=INK, width=9 * SS)
d.line(S([(140, 90), (190, 110)]), fill=WHITE, width=7 * SS)
d.line(S([(150, 70), (205, 92)]), fill=WHITE, width=7 * SS)
d.rounded_rectangle(S([(150, 10), (210, 70)]), radius=10 * SS, fill=INK)
save(im, "box_sneaker.png")

# contact shadow: soft radial ellipse
sh = Image.new("L", (512, 512), 0)
ImageDraw.Draw(sh).ellipse([(96, 96), (416, 416)], fill=255)
sh = sh.filter(ImageFilter.GaussianBlur(48))
im = Image.new("RGBA", (512, 512), (10, 8, 6, 0))
im.putalpha(sh)
im.save(os.path.join(OUT, "box_contact_shadow.png"))

# slides --------------------------------------------------------------------------------------
W, H = 1920, 1080
font = ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf", 300)
im = Image.new("RGB", (W, H), (14, 14, 15))
d = ImageDraw.Draw(im)
txt = "OFFBRIEF"
tw = d.textlength(txt, font=font)
x0, y0 = (W - tw - 90) / 2, H / 2 - 190
d.text((x0, y0), txt, font=font, fill=(246, 244, 238))
d.ellipse([(x0 + tw + 18, y0 + 255), (x0 + tw + 88, y0 + 325)], fill=(246, 196, 32))
im.save(os.path.join(OUT, "slide_offbrief_logo.png"))

# comic illustration panel: red burst, halftone dots, speed lines, ground line for BOX_01
im = Image.new("RGB", (W, H), (226, 74, 58))
d = ImageDraw.Draw(im)
cx, cy = W * 0.42, H * 0.55
for i in range(36):
    a0, a1 = i * 10, i * 10 + 4
    p = [(cx, cy)] + [(cx + 2400 * math.cos(math.radians(a)), cy + 2400 * math.sin(math.radians(a))) for a in (a0, a1)]
    d.polygon(p, fill=(244, 120, 92))
for y in range(0, H, 22):
    for x in range(0, W, 22):
        r = 2 + 5 * min(1.0, math.hypot(x - cx, y - cy) / 1100)
        d.ellipse([(x - r, y - r), (x + r, y + r)], fill=(180, 40, 34))
d.rectangle([(0, 0), (W - 1, H - 1)], outline=(30, 20, 18), width=26)
im.save(os.path.join(OUT, "slide_box_illustration.png"))
print("art written to", OUT)
