"""Original textures: evidence tag (front/back), placeholder case cover (no licensed art), station signage.
    python3 scripts/textures.py"""
import math
import os
import sys

from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import config as C  # noqa: E402

FB = "/usr/share/fonts/opentype/inter/Inter-Black.otf"
FBO = "/usr/share/fonts/opentype/inter/Inter-Bold.otf"


def hx(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def tag():
    W, H = 1520, 800                                      # 95 x 50 mm at 16 px/mm
    card = (214, 190, 150)
    for side in ("front", "back"):
        im = Image.new("RGB", (W, H), card)
        d = ImageDraw.Draw(im)
        for i in range(0, W, 7):                          # card fibre
            d.line([(i, 0), (i + 40, H)], fill=(206, 182, 142), width=1)
        d.ellipse([60, H / 2 - 50, 160, H / 2 + 50], outline=(150, 120, 80), width=14)      # reinforced eyelet
        d.ellipse([85, H / 2 - 25, 135, H / 2 + 25], fill=(60, 50, 40))
        if side == "front":
            cx, cy, r = 360, H / 2, 150                   # generic shield badge (original)
            pts = [(cx - r, cy - r * 0.9), (cx + r, cy - r * 0.9), (cx + r, cy + r * 0.1), (cx, cy + r * 1.05), (cx - r, cy + r * 0.1)]
            d.polygon(pts, outline=(40, 40, 50), width=10)
            star = [(cx + math.cos(math.pi / 2 + k * math.pi / 5) * (70 if k % 2 == 0 else 30),
                     cy - 10 - math.sin(math.pi / 2 + k * math.pi / 5) * (70 if k % 2 == 0 else 30)) for k in range(10)]
            d.polygon(star, fill=(40, 40, 50))
            f = ImageFont.truetype(FB, 118)
            for i, line in enumerate(("PROPERTY OF", "VICE CITY", "POLICE")):
                d.text((560, 150 + i * 165), line, font=f, fill=(28, 28, 34))
            d.text((560, 650), "EVIDENCE · DO NOT REMOVE", font=ImageFont.truetype(FBO, 44), fill=(120, 40, 40))
        im.save(os.path.join(C.P["tex"], f"tag_{side}.png"))


def case_cover():
    W, H = 675, 850                                      # 135 x 170 mm at 5 px/mm
    im = Image.new("RGB", (W, H))
    d = ImageDraw.Draw(im)
    top, mid, bot = hx(C.PAL["plum"]), hx(C.PAL["magenta"]), hx(C.PAL["peach"])
    for y in range(H):
        t = y / H
        c = tuple(int(top[i] + (mid[i] - top[i]) * min(1, t / 0.6)) if t < 0.6 else int(mid[i] + (bot[i] - mid[i]) * (t - 0.6) / 0.4) for i in range(3))
        d.line([(0, y), (W, y)], fill=c)
    d.rectangle([0, 0, W, 95], fill=(28, 70, 190))        # generic blue header band (no platform logo)
    d.text((24, 26), "GTA_CASE_01", font=ImageFont.truetype(FB, 42), fill=(255, 255, 255))
    for x, h in ((80, 320), (560, 360), (470, 250)):      # palm silhouettes
        d.line([(x, H), (x + 20, H - h)], fill=(25, 16, 35), width=16)
        for k in range(7):
            a = -math.pi / 2 + (k - 3) * 0.45
            d.line([(x + 20, H - h), (x + 20 + math.cos(a) * 110, H - h + math.sin(a) * 60 + 40)], fill=(25, 16, 35), width=12)
    d.text((W / 2 - 220, 380), "LICENSED ART", font=ImageFont.truetype(FB, 62), fill=(255, 240, 250))
    d.text((W / 2 - 220, 450), "PLACEHOLDER", font=ImageFont.truetype(FB, 62), fill=(255, 240, 250))
    im.save(os.path.join(C.P["tex"], "case_cover.png"))


def signs():
    im = Image.new("RGB", (1024, 256), (12, 8, 20))
    d = ImageDraw.Draw(im)
    d.text((40, 50), "FUEL · 24/7 · MART", font=ImageFont.truetype(FB, 120), fill=hx(C.PAL["pink"]))
    im.save(os.path.join(C.P["tex"], "station_sign.png"))


if __name__ == "__main__":
    os.makedirs(C.P["tex"], exist_ok=True)
    tag()
    case_cover()
    signs()
    print("TEXTURES", sorted(os.listdir(C.P["tex"])))
