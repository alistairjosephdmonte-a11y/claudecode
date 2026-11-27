"""Labels preview frames (system python3 + PIL): frame, timecode, camera, lens, beat, BLOCKOUT tag.

    python3 scripts/burnin.py <in_dir> <out_dir>"""
import json
import os
import sys

from PIL import Image, ImageDraw, ImageFont

src, dst = sys.argv[1], sys.argv[2]
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.makedirs(dst, exist_ok=True)
paths = json.load(open(os.path.join(ROOT, "metadata", "camera_paths.json")))
lens = {p[0]: (cid, p[3]) for cid, pts in paths.items() for p in pts}
BEATS = [(1, "Kitchen establishment"), (49, "Packaging reveal"), (91, "Cooked chicken"), (121, "Sauce pour"),
         (169, "Spice addition"), (197, "Simmering macro"), (236, "Steam transition"), (241, "Serving bowl reveal"),
         (263, "Dining environment"), (288, "Hero hold")]
try:
    F = ImageFont.truetype("DejaVuSansMono.ttf", 16)
except OSError:
    F = ImageFont.load_default()
for f in range(1, 361):
    p = os.path.join(src, "frame_%04d.png" % f)
    if not os.path.exists(p):
        continue
    im = Image.open(p).convert("RGB")
    d = ImageDraw.Draw(im)
    beat = [n for b, n in BEATS if b <= f][-1]
    cid, mm = lens[f]
    s = (f - 1) // 24
    top = "BC TEN MINUTES TO MADRAS  |  BLOCKOUT PREVIEW  |  clay, orange = provisional carton"
    bot = "F %03d/360  TC 00:00:%02d:%02d  %s  %3.0f mm  %s" % (f, s, (f - 1) % 24, cid, mm, beat)
    for y, t in ((6, top), (im.size[1] - 26, bot)):
        w = d.textlength(t, font=F)
        d.rectangle((6, y - 2, 14 + w, y + 20), fill=(0, 0, 0))
        d.text((10, y), t, fill=(255, 255, 255), font=F)
    im.save(os.path.join(dst, "frame_%04d.png" % f))
print("BURNIN_DONE")
