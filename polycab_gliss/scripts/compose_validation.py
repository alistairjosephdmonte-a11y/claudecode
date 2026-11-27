"""Composites the validation deliverables from render_validation.py output (system python3 + PIL).

    python3 scripts/compose_validation.py <validation_dir> <official_photo.png>

Writes deliverables/GLISS_PRODUCT_OFFICIAL_OVERLAY.png and GLISS_PRODUCT_VALIDATION_{FRONT,SIDE,TOP}.png."""
import json
import os
import sys

from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont

vdir, photo = sys.argv[1], sys.argv[2]
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "deliverables")
os.makedirs(OUT, exist_ok=True)
reg = json.load(open(os.path.join(ROOT, "metadata", "GLISS_DIMENSION_REGISTER.json")))
fit = json.load(open(os.path.join(vdir, "fit.json")))["best"]
try:
    FONT = ImageFont.truetype("DejaVuSans.ttf", 22)
    SMALL = ImageFont.truetype("DejaVuSans.ttf", 17)
except OSError:
    FONT = SMALL = ImageFont.load_default()


def on_white(im):
    bg = Image.new("RGBA", im.size, (255, 255, 255, 255))
    bg.alpha_composite(im.convert("RGBA"))
    return bg.convert("RGB")


def bbox_fit(img, mask, box_size, target_box):
    """Crop img to the mask bbox and scale it into target_box (x0, y0, x1, y1) on a canvas of box_size."""
    bb = mask.getbbox()
    crop_i, crop_m = img.crop(bb), mask.crop(bb)
    tw, th = target_box[2] - target_box[0], target_box[3] - target_box[1]
    crop_i, crop_m = crop_i.resize((tw, th), Image.LANCZOS), crop_m.resize((tw, th), Image.LANCZOS)
    ci = Image.new("RGBA", box_size, (0, 0, 0, 0))
    cm = Image.new("L", box_size, 0)
    ci.paste(crop_i, target_box[:2])
    cm.paste(crop_m, target_box[:2])
    return ci, cm


ph = Image.open(photo).convert("RGBA")
ph_mask = ph.getchannel("A").point(lambda v: 255 if v > 127 else 0)
pb = ph_mask.getbbox()
render = Image.open(os.path.join(vdir, "fit_render.png")).convert("RGBA")
rmask = render.getchannel("A").point(lambda v: 255 if v > 127 else 0)
r_img, r_mask = bbox_fit(render, rmask, ph.size, pb)
S = 3
W = ph.size[0] * S
panel = lambda im: im.resize((W, W), Image.LANCZOS)
p1 = panel(on_white(ph))
p2 = panel(on_white(r_img))
# overlay: photograph, model silhouette tinted, model outline in red, photo outline in blue
ov = on_white(ph).convert("RGBA")
tint = Image.new("RGBA", ph.size, (230, 60, 40, 0))
tint.putalpha(r_mask.point(lambda v: 70 if v else 0))
ov.alpha_composite(tint)
ov = panel(ov.convert("RGB")).convert("RGBA")
edge = lambda m: panel(m.convert("L")).filter(ImageFilter.FIND_EDGES).point(lambda v: 255 if v > 60 else 0)
for m, col in ((r_mask, (220, 30, 20, 255)), (ph_mask, (20, 80, 230, 255))):
    e = edge(m).filter(ImageFilter.MaxFilter(3))
    layer = Image.new("RGBA", (W, W), col)
    layer.putalpha(e)
    ov.alpha_composite(layer)
inter = ImageChops.multiply(r_mask, ph_mask)
iou_full = sum(1 for v in inter.getdata() if v) / max(1, sum(1 for v in ImageChops.lighter(r_mask, ph_mask).getdata() if v))
sheet = Image.new("RGB", (W * 3 + 80, W + 150), (255, 255, 255))
for i, p in enumerate((p1, p2, ov.convert("RGB"))):
    sheet.paste(p, (20 + i * (W + 20), 90))
d = ImageDraw.Draw(sheet)
d.text((20, 15), "GLISS product silhouette check: official photograph vs. provisional model (camera-matched)", fill=(0, 0, 0),
       font=FONT)
d.text((20, 48), "Official photograph (polycab.com p-64543)", fill=(60, 60, 60), font=SMALL)
d.text((40 + W, 48), "Model, solved pose: yaw %d deg, head tilt %d deg, camera elevation %d deg" %
       (fit["yaw_deg"], fit["head_tilt_deg"], fit["camera_elev_deg"]), fill=(60, 60, 60), font=SMALL)
d.text((60 + 2 * W, 48), "Overlay: blue = photo outline, red = model outline", fill=(60, 60, 60), font=SMALL)
d.text((20, W + 105), "Silhouette IoU %.3f (bbox-normalised) / %.3f (overlay). Proportions PROVISIONAL, no manufacturer "
       "dimensions; not dimensionally certified." % (fit["iou"], iou_full), fill=(150, 20, 20), font=SMALL)
sheet.save(os.path.join(OUT, "GLISS_PRODUCT_OFFICIAL_OVERLAY.png"))
print("overlay IoU", round(iou_full, 3))

# orthographic sheets with provisional dimensions
dm = {k: v["value"] for k, v in reg["dimensions_mm"].items()}
notes = {
    "FRONT": ["housing outer diameter %.1f mm" % dm["housing_outer_diameter"],
              "reflector opening %.1f mm, COB %.1f mm" % (dm["reflector_opening_diameter"], dm["emitter_diameter"]),
              "base diameter %.1f mm" % dm["mounting_base_diameter"]],
    "SIDE": ["housing length %.1f mm" % dm["housing_length"],
             "base thickness %.1f mm, boss %.1f mm" % (dm["mounting_base_thickness"], dm["boss_height"]),
             "stem %.1f x %.1f x %.1f mm (w x d x h)" % (dm["stem_width"], dm["stem_depth"], dm["stem_height"]),
             "pivot %.1f mm from housing rear; head tilt 35 deg" % dm["pivot_offset"]],
    "TOP": ["mounting face (ceiling side) up; base diameter %.1f mm" % dm["mounting_base_diameter"],
            "world scale: housing diameter %.0f mm (storyboard, PROVISIONAL)" %
            reg["world_scale_housing_diameter_mm"]["value"]],
}
for view, lines in notes.items():
    im = Image.open(os.path.join(vdir, "ortho_%s.png" % view)).convert("RGB")
    d = ImageDraw.Draw(im)
    d.rectangle((0, 0, im.size[0], 40 + 30 * (len(lines) + 1)), fill=(245, 245, 245))
    d.text((24, 14), "GLISS_PRODUCT_VALIDATION_%s  (orthographic, 320 mm frame width)" % view, fill=(0, 0, 0), font=FONT)
    for i, t in enumerate(lines + ["ALL VALUES PROVISIONAL / NOT VERIFIED against manufacturer data"]):
        d.text((24, 48 + 28 * i), t, fill=(150, 20, 20) if i == len(lines) else (40, 40, 40), font=SMALL)
    # 50 mm scale bar (frame 1600 px = 240 mm)
    px = 1600 / 320 * 50
    y = im.size[1] - 50
    d.line((40, y, 40 + px, y), fill=(0, 0, 0), width=4)
    d.text((40, y + 10), "50 mm", fill=(0, 0, 0), font=SMALL)
    im.save(os.path.join(OUT, "GLISS_PRODUCT_VALIDATION_%s.png" % view))
print("COMPOSE_DONE")
