"""Composites the APPROVED brand artwork over the clean master sequence. Run with system python3 (needs PIL).

    python3 scripts/brand_master.py <logo.png> <end_slate.png> [--seq deliverables/master_sequence_png16]
                                    [--out deliverables/branded_sequence] [--slate-from 112]

Nothing here draws a logo or lettering. It only places files the brand team supplies:
  * logo.png       official category logo with alpha, placed in the top-right safe box (BRAND_Safe_Logo_TopRight)
  * end_slate.png  official end slate with alpha (title + "Feel the superior difference" as approved artwork),
                   faded in over the final frames in the right-hand message box (BRAND_Safe_Message_Right)
Boxes are normalised (u0, v0, u1, v1) from the bottom-left, the same values stored on the guide objects in the .blend.
Artwork is scaled uniformly (never stretched) to fit its box."""
import argparse
import glob
import os

from PIL import Image

LOGO_BOX = (0.70, 0.70, 0.92, 0.90)
MSG_BOX = (0.66, 0.30, 0.92, 0.62)


def fit(art, box, W, H):
    u0, v0, u1, v1 = box
    bw, bh = (u1 - u0) * W, (v1 - v0) * H
    s = min(bw / art.width, bh / art.height)
    a = art.resize((max(1, round(art.width * s)), max(1, round(art.height * s))), Image.LANCZOS)
    x = round(u1 * W - a.width)                       # right-aligned
    y = round((1 - v1) * H + (bh - a.height) / 2)     # vertically centred
    return a, (x, y)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("logo")
    ap.add_argument("slate")
    ap.add_argument("--seq", default="deliverables/master_sequence_png16")
    ap.add_argument("--out", default="deliverables/branded_sequence")
    ap.add_argument("--logo-from", type=int, default=96)
    ap.add_argument("--slate-from", type=int, default=104)
    ap.add_argument("--fade", type=int, default=10)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    logo = Image.open(a.logo).convert("RGBA")
    slate = Image.open(a.slate).convert("RGBA")
    for p in sorted(glob.glob(os.path.join(a.seq, "frame_*.png"))):
        f = int(os.path.basename(p)[6:10])
        im = Image.open(p).convert("RGB")      # 8-bit for the branded review master
        W, H = im.size
        base = im.convert("RGBA")
        for art, box, f0 in ((logo, LOGO_BOX, a.logo_from), (slate, MSG_BOX, a.slate_from)):
            k = min(1.0, max(0.0, (f - f0 + 1) / a.fade))
            if k <= 0:
                continue
            r, xy = fit(art, box, W, H)
            if k < 1:
                al = r.getchannel("A").point(lambda v: round(v * k))
                r.putalpha(al)
            layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            layer.paste(r, xy)
            base = Image.alpha_composite(base, layer)
        base.convert("RGB").save(os.path.join(a.out, os.path.basename(p)))
    print("BRANDED", a.out)


main()
