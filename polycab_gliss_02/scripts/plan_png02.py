"""Annotated technical sheets (system python3 + PIL) from render_plans.py output and the QA metadata.

    python3 scripts/plan_png02.py <plans_dir> [official_photo.png]

Writes deliverables/GLISS_02_ARCHITECTURAL_FLOORPLAN.png, GLISS_02_FIXTURE_AIMING_VALIDATION.png,
GLISS_02_PRODUCT_ORTHOGRAPHIC.png and metadata/GLISS_02_AIMING_VALIDATION.json."""
import json
import math
import os
import sys

from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont, ImageOps

pd = sys.argv[1]
official = sys.argv[2] if len(sys.argv) > 2 else None
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "deliverables")
info = json.load(open(os.path.join(pd, "plan.json")))
paths = json.load(open(os.path.join(ROOT, "metadata", "camera_paths.json")))
reg = json.load(open(os.path.join(ROOT, "metadata", "GLISS_02_PRODUCT_DIMENSION_REGISTER.json")))
aim = reg["installed_aiming"]
try:
    F = ImageFont.truetype("DejaVuSans.ttf", 24)
    FS = ImageFont.truetype("DejaVuSans.ttf", 17)
    FB = ImageFont.truetype("DejaVuSans-Bold.ttf", 18)
except OSError:
    F = FS = FB = ImageFont.load_default()
NOTE = ("PREVIEW - proposed positions from the brief (X mirrored, see README). Dimensions in mm. "
        "Not for construction; product dimensions unverified.")
RED, INK, GREY = (190, 40, 20), (20, 20, 20), (90, 90, 90)


def header(d, title, w):
    d.rectangle((0, 0, w, 64), fill=(250, 250, 248))
    d.text((24, 8), title, fill=INK, font=F)
    d.text((24, 38), NOTE, fill=RED, font=FS)


def MX(x):
    return -x


# ------------------------------------------------------------------ floor plan
t = info["top"]
W, H = t["res"]
top = Image.open(os.path.join(pd, "top.png")).convert("RGB")
c = Image.new("RGB", (W + 560, H + 64), (250, 250, 248))
c.paste(top, (0, 64))
d = ImageDraw.Draw(c)
header(d, "GLISS 02 - ENV_GLISS_02 architectural floor plan (6500 x 5800 mm, ceiling 3000 mm)", W + 560)
S = W / t["ortho_scale"]


def Q(x, y):
    return (W / 2 + (x - t["centre"][0]) * S, 64 + H / 2 - (y - t["centre"][1]) * S)


labels = [(0.0, -0.12, "GALLERY WALL", "honed ivory travertine 4800 x 3000, slabs 1200 x 600"),
          (MX(-1.1), 0.12, "MEMORY_01 / GLISS_LEFT", "wedding; frame 700 x 900, centre h 1600"),
          (0.0, 0.12, "MEMORY_02 / GLISS_CENTRE", "travel memory; frames 1100 c/c"),
          (MX(1.1), 0.12, "MEMORY_03 / GLISS_RIGHT", "holiday; fixtures set back 900, ceiling mount"),
          (0.0, 3.6, "SOFA_MAIN", "2700 x 950 x 820, ivory linen, faces the wall"),
          (0.0, 2.15, "TABLE_COFFEE", "dark walnut, dia 900, h 350"),
          (MX(-0.30), 3.45, "FEM_01 (proxy)", "seat x +/-300 (brief +/-430, see README)"),
          (MX(0.30), 3.45, "MAL_01 (proxy)", "seated 1.78 m proxy"),
          (3.2, 2.9, "GLAZING", "floor-to-ceiling, viewer's LEFT, linen curtains"),
          (-3.05, 2.1, "JOINERY", "walnut shelving 2200 x 400, viewer's RIGHT"),
          (0.0, 4.25, "RUG", "woven wool 3200 x 2600")]
ly = 90
for i, (x, y, tid, txt) in enumerate(labels):
    p = Q(x, y)
    d.ellipse((p[0] - 6, p[1] - 6, p[0] + 6, p[1] + 6), fill=RED)
    d.text((p[0] + 6, p[1] - 24), str(i + 1), fill=RED, font=FB)
    d.text((W + 20, ly), "%d  %s" % (i + 1, tid), fill=INK, font=FB)
    d.text((W + 48, ly + 22), txt, fill=(60, 60, 60), font=FS)
    ly += 52


def dim(x0, y0, x1, y1, txt, off=(0, 0)):
    a, b = Q(x0, y0), Q(x1, y1)
    d.line((a, b), fill=INK, width=2)
    for p in (a, b):
        d.line((p[0] - 6, p[1] - 6, p[0] + 6, p[1] + 6), fill=INK, width=2)
    d.text(((a[0] + b[0]) / 2 - 30 + off[0], (a[1] + b[1]) / 2 + 6 + off[1]), txt, fill=INK, font=FS)


dim(-3.25, 5.65, 3.25, 5.65, "6500", (0, -32))
dim(-2.4, 0.35, 2.4, 0.35, "4800 travertine", (-40, 0))
dim(MX(-1.1), 0.0, MX(-1.1), 0.9, "900", (40, -10))
# cameras: each shot's position and view at its first frame, walkthrough path
COL = {"CAM_WALKTHROUGH": (40, 120, 40)}
for cid, pts in paths.items():
    col = COL.get(cid, (30, 90, 200))
    xy = [Q(p[1][0], p[1][1]) for p in pts]
    if len(set(map(tuple, xy))) > 1:
        d.line(xy, fill=col, width=3)
    q, tg = Q(*pts[0][1][:2]), Q(*pts[0][2][:2])
    v = (tg[0] - q[0], tg[1] - q[1])
    n = math.hypot(*v) or 1
    d.line((q, (q[0] + 70 * v[0] / n, q[1] + 70 * v[1] / n)), fill=col, width=2)
    d.ellipse((q[0] - 6, q[1] - 6, q[0] + 6, q[1] + 6), fill=col)
    lab = "WALK" if cid == "CAM_WALKTHROUGH" else cid[4:6]
    d.text((q[0] + 8, q[1] + 2), lab, fill=col, font=FB)
ly += 20
for tline in ("Blue: shot cameras 01-09 at their first frame (dot + view line; 08 = 01).",
              "Green: 10 s walkthrough (24 mm, h 1650, min clearance 0.5 m).",
              "Origin: centre of the gallery wall at finished floor level.",
              "Brief X values mirrored so the brief's LEFT is the viewer's left.",
              "Plan cut just below the ceiling; fixtures shown in plan."):
    d.text((W + 20, ly), tline, fill=(60, 60, 60), font=FS)
    ly += 24
c.save(os.path.join(OUT, "GLISS_02_ARCHITECTURAL_FLOORPLAN.png"))

# ------------------------------------------------------------------ aiming validation
e = info["elev"]
EW, EH = e["res"]
off = Image.open(os.path.join(pd, "elev_off.png")).convert("RGB")
on = Image.open(os.path.join(pd, "elev_on.png")).convert("RGB")
diff = ImageChops.subtract(ImageOps.grayscale(on), ImageOps.grayscale(off)).filter(ImageFilter.GaussianBlur(6))
es = EW / e["ortho_scale"]


def E(x, z):
    return (EW / 2 - (x - e["centre"][0]) * es, EH / 2 - (z - e["centre"][1]) * es)


def Einv(px, py):
    return (e["centre"][0] - (px - EW / 2) / es, e["centre"][1] - (py - EH / 2) / es)


dp = diff.load()
res = []
for a in aim:
    tx = a["axis_hit_on_artwork_plane"][0]
    x0, y0 = E(tx + 0.6, 2.75)
    x1, y1 = E(tx - 0.6, 0.6)
    sw = sx = sy = 0.0
    peak = (0, None)
    for py in range(int(y0), int(y1), 2):
        for px in range(int(x0), int(x1), 2):
            v = dp[px, py]
            sw += v
            sx += v * px
            sy += v * py
            if v > peak[0]:
                peak = (v, (px, py))
    cx, cz = Einv(sx / sw, sy / sw)
    pkx, pkz = Einv(*peak[1])
    res.append({"fixture": a["fixture"], "artwork_centre": [tx, 1.6],
                "brightening_centroid_m": [round(cx, 3), round(cz, 3)],
                "centroid_offset_mm": [round((cx - tx) * 1000), round((cz - 1.6) * 1000)],
                "peak_m": [round(pkx, 3), round(pkz, 3)],
                "centroid_on_photograph": abs(cx - tx) <= 0.23 and abs(cz - 1.6) <= 0.23,
                "centroid_within_frame": abs(cx - tx) <= 0.35 and abs(cz - 1.6) <= 0.45})
json.dump({"method": "Gallery-wall orthographic elevation rendered with all Gliss off (f30) and all on (f210); "
                     "greyscale difference blurred; brightness-weighted centroid and peak per fixture within "
                     "+/-0.6 m of its artwork, z 0.6-2.75 m.", "results": res, "axes": aim},
          open(os.path.join(ROOT, "metadata", "GLISS_02_AIMING_VALIDATION.json"), "w"), indent=1)
SEC_W = 760
sheet = Image.new("RGB", (SEC_W + EW, EH + 64 + 150), (250, 250, 248))
d = ImageDraw.Draw(sheet)
header(d, "GLISS 02 - fixture aiming validation (optical axis section + measured brightening on the gallery wall)",
       SEC_W + EW)
# section (y horizontal from the wall, z vertical), drawn to scale
k = 200.0
ox, oz = 70, 64 + 40 + 3.0 * k


def SEC(y, z):
    return (ox + y * k, oz - z * k)


d.line((SEC(0, 0), SEC(0, 3.0)), fill=INK, width=5)
d.line((SEC(0, 3.0), SEC(3.2, 3.0)), fill=INK, width=5)
d.line((SEC(0, 0), SEC(3.2, 0)), fill=INK, width=3)
d.rectangle((SEC(0, 2.05) + SEC(0.045, 1.15)), outline=(120, 70, 30), width=3)
a0 = aim[0]
em = a0["emitter"]
tg = (0.04, 1.6)
half = math.radians(a0["beam_angle_deg"] / 2)
ang = math.atan2(tg[1] - em[2], tg[0] - em[1])
for sgn in (-1, 1):
    a2 = ang + sgn * half
    tt = (0.0 - em[1]) / math.cos(a2)
    d.line((SEC(em[1], em[2]), SEC(em[1] + tt * math.cos(a2), em[2] + tt * math.sin(a2))), fill=(230, 170, 60),
           width=2)
d.line((SEC(em[1], em[2]), SEC(*tg)), fill=RED, width=3)
d.ellipse((SEC(em[1], em[2])[0] - 7, SEC(em[1], em[2])[1] - 7, SEC(em[1], em[2])[0] + 7, SEC(em[1], em[2])[1] + 7),
          fill=INK)
d.text((SEC(0.25, 2.95)), "ceiling 3000", fill=GREY, font=FS)
d.text((SEC(0.1, 0.25)), "wall (y = 0)", fill=GREY, font=FS)
for i, tline in enumerate(("Section through any fixture (all three identical):",
                           "setback %d mm, emitter at h %d mm" % (a0["setback_m"] * 1000, em[2] * 1000),
                           "tilt from vertical %.1f deg (brief sheet: ~30-36)" % a0["tilt_from_vertical_deg"],
                           "beam %.0f deg (preview assumption, no IES)" % a0["beam_angle_deg"],
                           "axis miss at artwork centre: %s mm" % ", ".join(str(x["miss_mm"]) for x in aim),
                           "fixture base flush, head clear of ceiling")):
    d.text((24, oz + 30 + 22 * i), tline, fill=INK if i == 0 else GREY, font=FB if i == 0 else FS)
# elevation with difference overlay
heat = ImageOps.colorize(ImageOps.autocontrast(diff), (0, 0, 0), (255, 200, 60))
el = Image.blend(on, heat, 0.35)
sheet.paste(el, (SEC_W, 64))
d = ImageDraw.Draw(sheet)
for r in res:
    tx = r["artwork_centre"][0]
    p = E(tx, 1.6)
    p = (p[0] + SEC_W, p[1] + 64)
    d.line((p[0] - 18, p[1], p[0] + 18, p[1]), fill=(0, 200, 255), width=3)
    d.line((p[0], p[1] - 18, p[0], p[1] + 18), fill=(0, 200, 255), width=3)
    q = E(*r["brightening_centroid_m"])
    q = (q[0] + SEC_W, q[1] + 64)
    d.ellipse((q[0] - 9, q[1] - 9, q[0] + 9, q[1] + 9), outline=RED, width=4)
    a1, b1 = E(tx + 0.23, 1.83)
    a2, b2 = E(tx - 0.23, 1.37)
    d.rectangle((a1 + SEC_W, b1 + 64, a2 + SEC_W, b2 + 64), outline=(0, 200, 255), width=2)
    d.text((q[0] - 90, b2 + 64 + 60), "%s  offset %+d / %+d mm" % (r["fixture"], *r["centroid_offset_mm"]),
           fill=(255, 255, 255), font=FS)
yb = EH + 64 + 20
d.text((SEC_W + 20, yb), "Elevation from inside the room (viewer's left = MEMORY_01). Cyan cross / box: artwork centre "
       "and photograph. Red ring: brightness-weighted centroid of the Gliss contribution.", fill=INK, font=FS)
ok = all(r["centroid_on_photograph"] for r in res)
d.text((SEC_W + 20, yb + 26), "Result: brightest region falls on the photograph for all three fixtures: %s"
       % ("YES" if ok else "NO - see metadata/GLISS_02_AIMING_VALIDATION.json"), fill=(20, 120, 20) if ok else RED,
       font=FB)
sheet.save(os.path.join(OUT, "GLISS_02_FIXTURE_AIMING_VALIDATION.png"))
print("AIM", json.dumps(res))

# ------------------------------------------------------------------ product orthographic sheet
pr = info["prod"]
tiles = [("FRONT (from the room)", "prod_front.png"), ("SIDE", "prod_side.png"), ("TOP (from the ceiling)",
                                                                                  "prod_top.png")]
TS = 620
sheet = Image.new("RGB", (TS * 4 + 50, TS + 64 + 170), (250, 250, 248))
d = ImageDraw.Draw(sheet)
header(d, "GLISS 02 - GLISS_MASTER_02 orthographics, installed pose (pan %.0f, tilt %.1f deg) vs official photograph"
       % (pr["pan_deg"], pr["tilt_deg"]), TS * 4 + 50)
pxmm = TS / (pr["ortho_scale_m"] * 1000)
for i, (lab, fn) in enumerate(tiles):
    im = Image.open(os.path.join(pd, fn)).convert("RGB").resize((TS, TS), Image.LANCZOS)
    x = 10 + i * (TS + 10)
    sheet.paste(im, (x, 74))
    d.text((x + 10, 80), lab, fill=(255, 255, 255), font=FB)
    d.line((x + 20, 74 + TS - 30, x + 20 + 50 * pxmm, 74 + TS - 30), fill=(255, 255, 255), width=4)
    d.text((x + 20, 74 + TS - 58), "50 mm", fill=(255, 255, 255), font=FS)
x = 10 + 3 * (TS + 10)
if official and os.path.exists(official):
    im = Image.open(official).convert("RGB")
    im.thumbnail((TS, TS))
    sheet.paste(im, (x + (TS - im.width) // 2, 74 + (TS - im.height) // 2))
    d.text((x + 10, 80), "OFFICIAL PHOTOGRAPH (polycab.com)", fill=INK, font=FB)
for i, tline in enumerate((
        "Geometry: Concept 01 parametric master (one housing, base, stem, faceted reflector, single COB), linked to "
        "every fixture. Proportions fitted to the official photograph; silhouette IoU 0.76 (Concept 01 overlay).",
        "Scale: housing dia 60 mm is a PROVISIONAL world-scale control (no manufacturer drawing). PROP_GLISS_02's "
        "'~120 x 90 mm' reference contradicts the photograph's proportions and is recorded, not used.",
        "Not modelled / not claimed: tilt and rotation limits, finish variants, internal hinge, logos.")):
    d.text((14, TS + 64 + 24 + 30 * i), tline, fill=INK if i == 0 else GREY, font=FS)
sheet.save(os.path.join(OUT, "GLISS_02_PRODUCT_ORTHOGRAPHIC.png"))
print("SHEETS_DONE")
