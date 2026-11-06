"""Encodes the animatic and builds the contact sheet.
    python3 scripts/deliver.py
  delivery/AMUL_OTM_EP01_ANIMATIC_1280x720_24fps_TEMPMIX.mp4   picture + temp mix (H.264 / AAC)
  delivery/AMUL_OTM_EP01_ANIMATIC_1280x720_24fps_CLEAN.mp4     picture only
  delivery/AMUL_OTM_EP01_contact_sheet.png                     one frame per shot"""
import os
import subprocess
import sys

from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import config as C  # noqa: E402

FR = os.path.join(C.P["frames"], "f_%04d.png")
MIX = os.path.join(C.P["audio"], "AMUL_OTM_EP01_temp_mix.wav")
V = ["-c:v", "libx264", "-preset", "slow", "-crf", "15", "-pix_fmt", "yuv420p", "-color_primaries", "bt709", "-color_trc", "bt709",
     "-colorspace", "bt709", "-movflags", "+faststart"]


def run(cmd):
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error"] + cmd, check=True)


if __name__ == "__main__":
    out = os.path.join(C.P["delivery"], "AMUL_OTM_EP01_ANIMATIC_1280x720_24fps_TEMPMIX.mp4")
    run(["-framerate", "24", "-i", FR, "-i", MIX, "-map", "0:v", "-map", "1:a"] + V + ["-c:a", "aac", "-b:a", "256k", "-t", "30", out])
    run(["-framerate", "24", "-i", FR] + V + ["-t", "30", out.replace("TEMPMIX", "CLEAN")])
    f_b = ImageFont.truetype("/usr/share/fonts/opentype/inter/Inter-Bold.otf", 22)
    f_r = ImageFont.truetype("/usr/share/fonts/opentype/inter/Inter-Regular.otf", 18)
    W, H, P = 640, 360, 16
    sheet = Image.new("RGB", (P + 2 * (W + P), 90 + 5 * (H + 62)), (18, 16, 14))
    d = ImageDraw.Draw(sheet)
    d.text((P, 24), "AMUL: OVER THE MOO · EP 01 · THE CALLING · contact sheet (Cycles animatic, 1280x720)", font=f_b, fill=(240, 232, 220))
    for i, s in enumerate(C.SHOTS):
        f = C.bf((s["f0"] + s["f1"]) // 2)
        im = Image.open(os.path.join(C.P["frames"], f"f_{f:04d}.png")).convert("RGB").resize((W, H), Image.LANCZOS)
        x, y = P + (i % 2) * (W + P), 70 + (i // 2) * (H + 62)
        sheet.paste(im, (x, y))
        d.text((x, y + H + 6), f"{s['id']} · frames {s['f0']:03d}-{s['f1']:03d} · {s['lens']} mm", font=f_b, fill=(240, 160, 120))
        d.text((x, y + H + 32), s["name"], font=f_r, fill=(220, 214, 204))
    sheet.save(os.path.join(C.P["delivery"], "AMUL_OTM_EP01_contact_sheet.png"))
    print("DELIVERED", out)
