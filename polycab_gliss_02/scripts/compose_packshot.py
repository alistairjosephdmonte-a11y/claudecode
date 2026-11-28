"""Shot 10 end slate: rendered Gliss packshot (left 45 %) + supplied END_02 artwork as a fixed plate (right 55 %).

    python3 scripts/compose_packshot.py <packshot.png> <out.png>

No typography is drawn or regenerated: the right 55 % of reference/END_02.webp (logo, product name, line, "Glam Up
Your Memories", 7W and the three white-light options) is pasted unchanged, scaled to the render width. The
generated product on the plate's left is not used. The join is a soft horizontal blend over 8 % of the width, and
the render is tone-matched to the plate's background in that zone."""
import os
import sys

from PIL import Image, ImageStat

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src, dst = sys.argv[1], sys.argv[2]
shot = Image.open(src).convert("RGB")
W, H = shot.size
plate = Image.open(os.path.join(ROOT, "reference", "END_02.webp")).convert("RGB").resize((W, H), Image.LANCZOS)
x0 = int(W * 0.45)
band = int(W * 0.08)
# match the render's background tone to the plate's just right of the join (per-channel gain on the left part)
ref = ImageStat.Stat(plate.crop((x0, 0, x0 + band, H // 3))).mean
cur = ImageStat.Stat(shot.crop((x0 - band, 0, x0, H // 3))).mean
gain = [max(0.6, min(1.8, r / max(c, 1))) for r, c in zip(ref, cur)]
shot = Image.merge("RGB", [ch.point(lambda v, g=g: min(255, int(v * g))) for ch, g in zip(shot.split(), gain)])
mask = Image.new("L", (W, H), 0)
mp = mask.load()
for x in range(W):
    a = 0 if x < x0 - band // 2 else 255 if x >= x0 + band // 2 else int(255 * (x - x0 + band // 2) / band)
    for y in range(H):
        mp[x, y] = a
Image.composite(plate, shot, mask).save(dst)
print("SLATE", dst, "gain", [round(g, 2) for g in gain])
