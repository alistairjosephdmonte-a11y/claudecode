"""Milestone stills + contact sheet (system python3 + PIL).   python3 scripts/milestones.py <dir> <frames...>"""
import os
import sys

from PIL import Image, ImageDraw, ImageFont

src, frames = sys.argv[1], [int(f) for f in sys.argv[2:]]
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "deliverables")
NAMES = {24: "Kitchen establishment (CAM_A 24 mm)", 66: "Packaging reveal (CAM_A 50 mm)",
         102: "Cooked chicken (CAM_A 50 mm)", 145: "Sauce pour (CAM_A 65 mm)", 186: "Spice addition (CAM_A 65 mm)",
         230: "Simmering macro, steam building (CAM_A ~95 mm)", 330: "Hero hold (CAM_B 45 mm)"}
try:
    F = ImageFont.truetype("DejaVuSans.ttf", 30)
    FS = ImageFont.truetype("DejaVuSans.ttf", 22)
except OSError:
    F = FS = ImageFont.load_default()
tiles = []
for i, f in enumerate(frames):
    im = Image.open(os.path.join(src, "frame_%04d.png" % f)).convert("RGB")
    im.save(os.path.join(OUT, "BC_MILESTONE_%02d_F%03d.png" % (i + 1, f)))
    t = im.resize((960, 540), Image.LANCZOS)
    d = ImageDraw.Draw(t)
    lab = "%d  F%03d  %s" % (i + 1, f, NAMES.get(f, ""))
    d.rectangle((0, 0, d.textlength(lab, font=FS) + 20, 34), fill=(0, 0, 0))
    d.text((10, 4), lab, fill=(255, 255, 255), font=FS)
    tiles.append(t)
cols = 2
rows = (len(tiles) + cols - 1) // cols
sheet = Image.new("RGB", (cols * 960 + 30, rows * 550 + 90), (245, 245, 242))
d = ImageDraw.Draw(sheet)
d.text((15, 12), "BC Ten Minutes to Madras - blockout milestone frames (clay; orange = provisional carton)",
       fill=(0, 0, 0), font=F)
d.text((15, 52), "1920 x 1080 @ 48 samples, Cycles CPU. For composition, scale, clearance and continuity approval only.",
       fill=(150, 40, 20), font=FS)
for i, t in enumerate(tiles):
    sheet.paste(t, (10 + (i % cols) * 970, 90 + (i // cols) * 550))
sheet.save(os.path.join(OUT, "BC_MILESTONES_CONTACT_SHEET.png"))
print("SHEET_DONE")
