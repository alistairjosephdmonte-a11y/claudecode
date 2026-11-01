"""Representative scene contact sheet from the rendered frames: 16 scenes × 3 beats, labelled with scene, timecode and title.
Writes delivery/BC002_contact_sheet.png.    python3 scripts/contact_sheet.py"""
import os

from PIL import Image, ImageDraw, ImageFont

import config as C

TW, TH, PAD, LAB = 560, 315, 14, 34
if __name__ == "__main__":
    f_b = ImageFont.truetype(C.FONTS["bold"], 17)
    f_r = ImageFont.truetype(C.FONTS["semi"], 15)
    f_h = ImageFont.truetype(C.FONTS["display"], 40)
    cols, rows = 6, 8
    W = PAD + cols * (TW + PAD)
    H = 110 + rows * (TH + LAB + PAD) + PAD
    sheet = Image.new("RGB", (W, H), C.PALETTE["bg"])
    d = ImageDraw.Draw(sheet)
    d.text((PAD, 30), "brand coroner · case 002 · wework · the $47 billion illusion", font=f_h, fill=C.PALETTE["type"])
    d.text((PAD, 80), "contact sheet · 16 scenes × 3 beats · frames from the rendered 1920×1080 animatic", font=f_r, fill=C.PALETTE["gray"])
    i = 0
    for n, (title, beats) in C.SCENES.items():
        for bi, (b0, b1, *_) in enumerate(beats):
            f = C.scene_start(n) + int((b0 + (b1 - b0) * 0.72) * C.FPS)
            im = Image.open(os.path.join(C.P["frames"], f"f_{f:04d}.png")).convert("RGB").resize((TW, TH), Image.LANCZOS)
            x = PAD + (i % cols) * (TW + PAD)
            y = 110 + (i // cols) * (TH + LAB + PAD)
            sheet.paste(im, (x, y))
            d.rectangle((x - 1, y - 1, x + TW, y + TH), outline="#2E2E2E")
            d.text((x, y + TH + 7), f"SC{n:02d}.{bi + 1}", font=f_b, fill=C.PALETTE["red"])
            d.text((x + 72, y + TH + 8), f"{C.tc(f)} · {title}", font=f_r, fill=C.PALETTE["type"])
            i += 1
    out = os.path.join(C.P["delivery"], "BC002_contact_sheet.png")
    sheet.save(out, optimize=True)
    print("SHEET", out, sheet.size)
