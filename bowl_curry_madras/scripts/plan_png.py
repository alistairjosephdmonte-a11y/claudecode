"""Annotated blockout drawings (system python3 + PIL), from render_overview.py output and metadata/camera_paths.json.

    python3 scripts/plan_png.py <overview_dir>

Writes deliverables/BC_ISOMETRIC_OVERVIEW.png, BC_TOPDOWN_LAYOUT.png and BC_CAMERA_PATHS.png."""
import json
import os
import sys

from PIL import Image, ImageDraw, ImageFont

ovd = sys.argv[1]
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "deliverables")
os.makedirs(OUT, exist_ok=True)
pj = json.load(open(os.path.join(ovd, "top_projection.json")))
paths = json.load(open(os.path.join(ROOT, "metadata", "camera_paths.json")))
W, H = pj["res"]
try:
    F = ImageFont.truetype("DejaVuSans.ttf", 24)
    FS = ImageFont.truetype("DejaVuSans.ttf", 17)
    FB = ImageFont.truetype("DejaVuSans-Bold.ttf", 18)
except OSError:
    F = FS = FB = ImageFont.load_default()
NOTE = "BLOCKOUT - neutral clay; orange = provisional carton only. Dimensions in mm. Not for construction."


def P(x, y):
    s = W / pj["ortho_scale"]
    return (W / 2 + (x - pj["centre"][0]) * s, H / 2 - (y - pj["centre"][1]) * s)


def header(d, title, w):
    d.rectangle((0, 0, w, 64), fill=(250, 250, 248))
    d.text((24, 8), title, fill=(0, 0, 0), font=F)
    d.text((24, 38), NOTE, fill=(150, 40, 20), font=FS)


# --- isometric overview
iso = Image.open(os.path.join(ovd, "iso.png")).convert("RGB")
c = Image.new("RGB", (W, H + 64), (250, 250, 248))
c.paste(iso, (0, 64))
d = ImageDraw.Draw(c)
header(d, "BC Ten Minutes to Madras - ENV_BC_01 isometric overview (frame 150; ceiling, south and east walls cut away)",
       W)
c.save(os.path.join(OUT, "BC_ISOMETRIC_OVERVIEW.png"))

# --- top-down layout
top = Image.open(os.path.join(ovd, "top.png")).convert("RGB")
c = Image.new("RGB", (W + 520, H + 64), (250, 250, 248))
c.paste(top, (0, 64))
d = ImageDraw.Draw(c)
header(d, "BC Ten Minutes to Madras - top-down layout (ENV_BC_01, 8000 x 5500 mm, ceiling 2800 mm)", W + 520)


def Q(x, y):
    p = P(x, y)
    return (p[0], p[1] + 64)


labels = [  # x, y, id, text
    (-3.95, 2.8, "WINDOW", "full-height glazing 4000 x 2250 (west, camera-left)"),
    (-2.35, 2.6, "DINING", "oak table 1400 x 900, h 750"),
    (-2.30, 2.58, "PROP_BOWL_01", "serving bowl 180, rice bowl 130"),
    (-2.15, 2.73, "BC_MADRAS_01_HERO", "carton 120 x 45 x 190 (PROVISIONAL)"),
    (1.80, 3.36, "ISLAND", "2300 x 880, limestone top h 910"),
    (1.95, 3.32, "PROP_PAN_01", "cast-iron skillet 280, on flush induction hob"),
    (1.30, 3.28, "BC_MADRAS_01_ISLAND", "carton 120 x 45 x 190 (PROVISIONAL)"),
    (1.70, 5.20, "KITCHEN RUN", "oak base/upper units, limestone top h 900"),
    (3.54, 5.20, "TALL UNIT", "integrated fridge 680 x 600 x 2400"),
]
legend_y = 90
for i, (x, y, tid, txt) in enumerate(labels):
    p = Q(x, y)
    d.ellipse((p[0] - 7, p[1] - 7, p[0] + 7, p[1] + 7), fill=(200, 40, 20))
    d.text((p[0] + 6, p[1] - 26), str(i + 1), fill=(200, 40, 20), font=FB)
    d.text((W + 20, legend_y), "%d  %s" % (i + 1, tid), fill=(0, 0, 0), font=FB)
    d.text((W + 48, legend_y + 22), txt, fill=(60, 60, 60), font=FS)
    legend_y += 54


def dim(x0, y0, x1, y1, txt, off=(0, 0)):
    a, b = Q(x0, y0), Q(x1, y1)
    d.line((a, b), fill=(30, 30, 30), width=2)
    for p in (a, b):
        d.line((p[0] - 6, p[1] - 6, p[0] + 6, p[1] + 6), fill=(30, 30, 30), width=2)
    d.text(((a[0] + b[0]) / 2 - 30 + off[0], (a[1] + b[1]) / 2 + 6 + off[1]), txt, fill=(30, 30, 30), font=FS)


dim(-4.0, -0.12, 4.0, -0.12, "8000", (0, -30))
dim(4.12, 0.0, 4.12, 5.5, "5500", (-70, 0))
dim(0.65, 2.75, 2.95, 2.75, "2300", (0, -2))
dim(-3.05, 2.0, -1.65, 2.0, "1400")
dim(-1.65, 2.5, 0.65, 2.5, "2300 clear", (0, -30))
d.text((W + 20, legend_y + 20), "Grid origin: south-west room corner at (-4000, 0).", fill=(60, 60, 60), font=FS)
d.text((W + 20, legend_y + 44), "+Y away from the cameras; both cameras look ~+Y.", fill=(60, 60, 60), font=FS)
c.save(os.path.join(OUT, "BC_TOPDOWN_LAYOUT.png"))

# --- camera paths: plan + height/lens/clearance strip
CH = 330
c = Image.new("RGB", (W + 520, H + 64 + CH), (250, 250, 248))
faded = Image.blend(top, Image.new("RGB", top.size, (255, 255, 255)), 0.35)
c.paste(faded, (0, 64))
d = ImageDraw.Draw(c)
header(d, "BC Ten Minutes to Madras - camera paths (top view; CAM_A frames 1-240, CAM_B 241-360)", W + 520)
COL = {"CAM_A": (30, 90, 200), "CAM_B": (210, 70, 20)}
beats = [(1, "establish"), (66, "carton"), (102, "chicken"), (140, "pour"), (190, "spice"), (208, "macro"),
         (240, "into steam"), (241, "out of steam"), (288, "hero hold 288-360")]
for cid, pts in paths.items():
    xy = [Q(p[1][0], p[1][1]) for p in pts]
    d.line(xy, fill=COL[cid], width=4)
    for p in pts:
        if p[0] % 24 == 0 or p[0] in (1, 241, 360):
            q = Q(p[1][0], p[1][1])
            d.ellipse((q[0] - 5, q[1] - 5, q[0] + 5, q[1] + 5), fill=COL[cid])
    for f, nm in beats:
        for p in pts:
            if p[0] == f:
                q, t = Q(p[1][0], p[1][1]), Q(p[2][0], p[2][1])
                d.line((q, t), fill=COL[cid] + (0,), width=1)
                d.text((q[0] + 8, q[1] + 4), "%d %s" % (f, nm), fill=COL[cid], font=FS)
ly = 90
for cid, txt in (("CAM_A", "CAM_A  frames 1-240  24 -> 100 mm  kitchen: establish, carton, chicken, pour, spice, "
                  "macro"), ("CAM_B", "CAM_B  frames 241-360  50 -> 45 mm  bowl reveal, dining, hero hold")):
    d.rectangle((W + 20, ly, W + 44, ly + 18), fill=COL[cid])
    lines = txt.split("  ")
    d.text((W + 54, ly), "  ".join(lines[:3]), fill=(0, 0, 0), font=FB)
    d.text((W + 54, ly + 24), lines[3] if len(lines) > 3 else "", fill=(60, 60, 60), font=FS)
    ly += 70
for t in ("Dots every 24 frames (1 s). Thin lines: view", "direction at each beat. Bezier keys, eased.",
          "Cut 240/241 hidden by steam: CAM_A pushes", "into the skillet steam, CAM_B opens inside the",
          "steam column over the serving bowl.", "", "Window (west) is camera-left in every frame",
          "(QA verified). Minimum camera clearance from", "solid geometry: see strip below."):
    d.text((W + 20, ly), t, fill=(60, 60, 60), font=FS)
    ly += 24
# strip: camera height, lens and clearance per frame
y0 = H + 64 + 30
x0, x1 = 80, W + 440
d.text((20, y0 - 26), "Per-frame camera height (m, solid), focal length (mm/100, dashed) and clearance to nearest "
       "solid geometry (m, thin)", fill=(0, 0, 0), font=FS)
sh = CH - 70
d.rectangle((x0, y0, x1, y0 + sh), outline=(160, 160, 160))
for v in (0.5, 1.0, 1.5):
    yy = y0 + sh - v / 1.8 * sh
    d.line((x0, yy, x1, yy), fill=(220, 220, 220))
    d.text((x0 - 40, yy - 9), "%.1f" % v, fill=(90, 90, 90), font=FS)
for f in range(0, 361, 24):
    xx = x0 + (f - 1) / 359 * (x1 - x0)
    d.text((xx - 10, y0 + sh + 6), str(max(f, 1)), fill=(90, 90, 90), font=FS)
for cid, pts in paths.items():
    def S(p, v):
        return (x0 + (p[0] - 1) / 359 * (x1 - x0), y0 + sh - min(v, 1.8) / 1.8 * sh)
    d.line([S(p, p[1][2]) for p in pts], fill=COL[cid], width=3)
    lens = [S(p, p[3] / 100) for p in pts]
    for i in range(0, len(lens) - 1, 2):
        d.line((lens[i], lens[i + 1]), fill=COL[cid], width=2)
    d.line([S(p, p[4]) for p in pts], fill=COL[cid], width=1)
xc = x0 + (240.5 - 1) / 359 * (x1 - x0)
d.line((xc, y0, xc, y0 + sh), fill=(0, 0, 0), width=1)
d.text((xc + 4, y0 + 4), "cut", fill=(0, 0, 0), font=FS)
c.save(os.path.join(OUT, "BC_CAMERA_PATHS.png"))
print("PLAN_DONE")
