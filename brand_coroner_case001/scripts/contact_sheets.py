"""One contact sheet per act (8 validation stills each) for review and delivery."""
import glob
import os
import sys

from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import config as C  # noqa: E402

fnt = ImageFont.truetype(os.path.join(C.P["fonts"], "Inter-SemiBold.otf"), 15)
for a in range(6):
    shots = C.SHOTS[a * 8:(a + 1) * 8]
    W, H = 480, 270
    sheet = Image.new("RGB", (4 * (W + 8) + 8, 2 * (H + 34) + 44), (17, 20, 24))
    d = ImageDraw.Draw(sheet)
    d.text((10, 10), f"{C.ACTS[a][0].replace('_', ' ')}  ·  {C.ACTS[a][1]}", fill=(232, 227, 216), font=fnt)
    for i, s in enumerate(shots):
        f = glob.glob(os.path.join(C.P["shots"], f"BC001_{s['shot_id']}_still_*.png"))
        x, y = 8 + (i % 4) * (W + 8), 40 + (i // 4) * (H + 34)
        if f:
            sheet.paste(Image.open(f[0]).convert("RGB").resize((W, H)), (x, y))
        d.text((x, y + H + 6), f"{s['shot_id']}  {s['timecode']}  {s['title']}  [{s['visual_mode']}]", fill=(200, 200, 200), font=fnt)
    out = os.path.join(C.P["previews"], f"BC001_contact_{C.ACTS[a][0]}.png")
    sheet.save(out)
    print(out)
