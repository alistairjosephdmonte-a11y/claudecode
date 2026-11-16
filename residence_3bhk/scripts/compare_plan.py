"""Builds deliverables/floorplan_comparison.png from the top-down render and the drawing (called by validate.py).

    python3 scripts/compare_plan.py metadata/topdown_mapping.json"""
import json
import os
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFont

m = json.load(open(sys.argv[1]))
r = Image.open(m["render"]).convert("RGBA")
W, H = r.size
scale = m["ortho_scale"] / W                      # metres per render pixel


def to_r(xm, ym):
    return ((xm - m["cam_x"]) / scale + W / 2, H / 2 - (ym - m["cam_y"]) / scale)


canvas = Image.new("RGBA", (W, H), (255, 255, 255, 255))
canvas.alpha_composite(r)
plan = Image.open(m["plan"]).convert("RGBA")
k = (1 / m["px_per_m"]) / scale                   # drawing px -> render px
plan_s = plan.resize((round(plan.width * k), round(plan.height * k)), Image.LANCZOS)
ox, oy = to_r(-m["origin_px"][0] / m["px_per_m"], m["origin_px"][1] / m["px_per_m"])
lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
lay.paste(plan_s, (round(ox), round(oy)))
mix = np.array(canvas).astype(float)
pl = np.array(lay).astype(float)
a = pl[:, :, 3:4] / 255 * 0.55
mix[:, :, :3] = mix[:, :, :3] * (1 - a) + pl[:, :, :3] * a
blend = Image.fromarray(mix.astype("uint8"))
d = ImageDraw.Draw(blend)
for name, poly in m["rooms"].items():
    d.polygon([to_r(*p) for p in poly], outline=(220, 30, 60, 255), width=2)
side = Image.new("RGBA", (W * 2 + 30, H + 70), (245, 244, 241, 255))
side.alpha_composite(canvas, (0, 60))
side.alpha_composite(blend, (W + 30, 60))
dd = ImageDraw.Draw(side)
f = ImageFont.truetype("/usr/share/fonts/opentype/inter/Inter-Bold.otf", max(16, W // 55))
dd.text((10, 18), "Top-down orthographic render of the model (ceilings off)", fill=(30, 30, 30, 255), font=f)
dd.text((W + 40, 18), "Same render with the supplied drawing overlaid at 55%; red = traced room outlines",
        fill=(30, 30, 30, 255), font=f)
os.makedirs(os.path.dirname(m["out"]), exist_ok=True)
side.convert("RGB").save(m["out"])
print("COMPARISON", m["out"], side.size)
