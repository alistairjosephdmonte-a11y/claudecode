"""Top-view camera path plan (system python3 + PIL) from metadata/camera_paths.json.

    python3 scripts/plan_png.py   ->   deliverables/GLISS_CAMERA_PATH_PLAN.png"""
import json
import os

from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
paths = json.load(open(os.path.join(ROOT, "metadata", "camera_paths.json")))
S = 220                      # px per metre
PAD = 140
W, H = int(7.0 * S + 2 * PAD + 520), int(6.0 * S + 2 * PAD)
try:
    F = ImageFont.truetype("DejaVuSans.ttf", 20)
    FS = ImageFont.truetype("DejaVuSans.ttf", 15)
except OSError:
    F = FS = ImageFont.load_default()
im = Image.new("RGB", (W, H), (250, 249, 246))
d = ImageDraw.Draw(im)


def P(x, y):                 # world (x, y) -> image; feature wall (y = 0) at the top
    return (PAD + (x + 3.5) * S, PAD + y * S)


def rect(x0, y0, x1, y1, fill, outline=(90, 90, 90), label=None):
    a, b = P(x0, y0), P(x1, y1)
    d.rectangle((a[0], a[1], b[0], b[1]), fill=fill, outline=outline, width=2)
    if label:
        d.text(((a[0] + b[0]) / 2 - 4 * len(label), (a[1] + b[1]) / 2 - 8), label, fill=(60, 60, 60), font=FS)


rect(-3.5, 0, 3.5, 6, (238, 236, 230), (40, 40, 40))
rect(-3.5, -0.06, 1.9, 0.0, (214, 196, 160), label=None)
rect(1.9, 0, 3.5, 0.42, (120, 80, 50), label="walnut joinery")
rect(-0.9, 0.0, 0.9, 0.04, (60, 45, 30))
d.text((P(-0.6, 0.06)[0], P(0, 0.06)[1]), "ART_WEDDING_01 1800 mm", fill=(40, 40, 40), font=FS)
d.text((P(-3.2, -0.30)[0], P(0, -0.30)[1]), "travertine feature wall (y = 0)", fill=(90, 70, 40), font=FS)
rect(-3.56, 0.35, -3.5, 5.75, (150, 190, 230))
d.text((P(-3.48, 5.8)[0], P(0, 5.8)[1]), "glazing x = -3.5", fill=(40, 80, 140), font=FS)
rect(-3.125, 2.3, -2.175, 5.0, (230, 224, 210), label="sofa")
cx, cy = P(-1.45, 3.55)
d.ellipse((cx - 0.45 * S, cy - 0.45 * S, cx + 0.45 * S, cy + 0.45 * S), fill=(120, 80, 50), outline=(60, 40, 20), width=2)
d.text((cx - 20, cy - 8), "table", fill=(240, 240, 240), font=FS)
for x, y in ((-0.725, 0.95), (0.725, 0.95)):
    a = P(x, y)
    d.ellipse((a[0] - 7, a[1] - 7, a[0] + 7, a[1] + 7), fill=(20, 20, 20))
    t = P(x * 0.62, 0.04)
    d.line((a, t), fill=(230, 170, 60), width=2)
d.text((P(0.85, 0.95)[0], P(0, 0.95)[1] - 8), "Gliss x2 (z 3.1 m)", fill=(20, 20, 20), font=FS)
for x, n in ((0.30, "Isha"), (-0.30, "Veer")):
    a = P(x, 2.0)
    d.ellipse((a[0] - 12, a[1] - 12, a[0] + 12, a[1] + 12), outline=(120, 120, 120), width=2)
    d.text((a[0] - 14, a[1] + 14), n, fill=(100, 100, 100), font=FS)
COL = {"CAM_03_AMBIENT": (30, 30, 30), "CAM_05_WEDDING_MEMORY": (200, 40, 40), "CAM_06_MATCH_CUT": (40, 120, 200),
       "CAM_07_HUMAN_CONNECTION": (150, 60, 170), "CAM_08_INSTALLED_GLISS": (20, 150, 90),
       "CAM_09_ARCHITECTURAL_REVEAL": (230, 120, 20), "CAM_WALKTHROUGH": (110, 110, 110)}
legend_y = PAD
for cid, col in COL.items():
    pts = paths[cid]
    xy = [P(p[1][0], p[1][1]) for p in pts]
    if len(xy) > 1:
        d.line(xy, fill=col, width=4 if cid != "CAM_WALKTHROUGH" else 2)
    s, e = xy[0], xy[-1]
    d.ellipse((s[0] - 6, s[1] - 6, s[0] + 6, s[1] + 6), outline=col, width=3)
    d.ellipse((e[0] - 6, e[1] - 6, e[0] + 6, e[1] + 6), fill=col)
    if pts[-1][2]:
        fx, fy = pts[-1][2][0], pts[-1][2][1]
        d.line((e, (e[0] + fx * 0.6 * S, e[1] + fy * 0.6 * S)), fill=col, width=2)
    f0, f1 = pts[0][0], pts[-1][0]
    z = pts[0][1][2]
    d.rectangle((W - 500, legend_y, W - 470, legend_y + 18), fill=col)
    d.text((W - 460, legend_y), "%s  f%d-%d  z %.2f m" % (cid.replace("CAM_", ""), f0, f1, z), fill=(30, 30, 30),
           font=FS)
    legend_y += 30
d.text((W - 500, legend_y + 10), "open circle = first frame, dot = last frame", fill=(80, 80, 80), font=FS)
d.text((W - 500, legend_y + 32), "short line = view direction at last frame", fill=(80, 80, 80), font=FS)
d.text((W - 500, legend_y + 54), "studio shots 1, 2, 10 are in SCENE_PRODUCT_STUDIO", fill=(80, 80, 80), font=FS)
d.text((PAD, 14), "GLISS camera path plan (top view, room 7000 x 6000 mm, origin = feature-wall centre at floor)",
       fill=(0, 0, 0), font=F)
for m in range(0, 8):
    a = P(-3.5 + m, 6.0)
    d.line((a[0], a[1], a[0], a[1] + 10), fill=(0, 0, 0), width=2)
    d.text((a[0] - 12, a[1] + 14), "%+.1f" % (-3.5 + m), fill=(0, 0, 0), font=FS)
d.text((P(0, 6)[0] - 30, P(0, 6)[1] + 40), "metres (x)", fill=(0, 0, 0), font=FS)
im.save(os.path.join(ROOT, "deliverables", "GLISS_CAMERA_PATH_PLAN.png"))
print("PLAN_DONE")
