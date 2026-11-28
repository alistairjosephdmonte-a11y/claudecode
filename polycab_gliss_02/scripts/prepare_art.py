"""Animatic placeholder photographs for MEMORY_01..03 (system python3 + PIL).

    python3 scripts/prepare_art.py

Crops the three photographs from the supplied PROP_GLISS_02 reference sheet (generated imagery, about 132 px
square each), evens out the lighting baked into the sheet (row and column luminance normalised to a smooth
profile), and upscales to 768 px. PLACEHOLDERS ONLY: the final film needs the approved photographs."""
import os

from PIL import Image, ImageFilter, ImageOps, ImageStat

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "reference", "PROP_GLISS_02.webp")
BOXES = {"MEMORY_01": (652, 178, 781, 309), "MEMORY_02": (867, 178, 1003, 309),
         "MEMORY_03": (1088, 178, 1215, 309)}

sheet = Image.open(SRC).convert("RGB")
for mid, box in BOXES.items():
    im = sheet.crop(box)
    w, h = im.size
    lum = ImageOps.grayscale(im).filter(ImageFilter.GaussianBlur(max(w, h) / 3))
    mean = ImageStat.Stat(lum).mean[0]
    px, lp = im.load(), lum.load()
    out = Image.new("RGB", (w, h))
    op = out.load()
    for y in range(h):
        for x in range(w):
            g = mean / max(lp[x, y], 1)
            op[x, y] = tuple(min(255, int(c * g)) for c in px[x, y])
    out = out.resize((768, 768), Image.LANCZOS).filter(ImageFilter.UnsharpMask(2, 60, 2))
    out.save(os.path.join(ROOT, "reference", mid + "_PLACEHOLDER.png"))
    print(mid, box, (w, h))
