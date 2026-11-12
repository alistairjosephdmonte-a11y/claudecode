"""Encodes the previews and builds the contact sheet and shot list.
    python3 scripts/deliver.py
  delivery/LASTJOB_EP01_WRONG_BAG_previs_1920x1080_30fps.mp4   16:9 master preview with the WAV mix (H.264 / AAC)
  delivery/LASTJOB_EP01_WRONG_BAG_previs_1080x1920_9x16.mp4    centre-safe 9:16 crop with the mix
  delivery/LASTJOB_EP01_contact_sheet.png                       one frame per shot
  delivery/LASTJOB_EP01_shot_list.csv                           shot, camera, frames [in, out), lens, motion, description"""
import csv
import os
import subprocess
import sys

from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import config as C  # noqa: E402

FR = os.path.join(C.P["frames"], "f_%03d.png")
MIX = os.path.join(C.P["audio"], "LASTJOB_EP01_mix.wav")
V = ["-c:v", "libx264", "-preset", "slow", "-crf", "16", "-pix_fmt", "yuv420p", "-color_primaries", "bt709", "-color_trc", "bt709",
     "-colorspace", "bt709", "-movflags", "+faststart"]


def run(cmd):
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error"] + cmd, check=True)


if __name__ == "__main__":
    os.makedirs(C.P["delivery"], exist_ok=True)
    n = C.F1 - C.F0 + 1
    base = ["-framerate", str(C.FPS), "-start_number", str(C.F0), "-i", FR, "-i", MIX, "-map", "0:v", "-map", "1:a", "-frames:v", str(n)]
    a = ["-c:a", "aac", "-b:a", "256k", "-t", f"{n / C.FPS:.3f}"]
    out = os.path.join(C.P["delivery"], "LASTJOB_EP01_WRONG_BAG_previs_1920x1080_30fps.mp4")
    run(base + V + a + [out])
    cw = round(C.RES[1] * 9 / 16 / 2) * 2                     # 608 px centre-safe column of the 1080p frame
    run(base + ["-vf", f"crop={cw}:{C.RES[1]}:(in_w-{cw})/2:0,scale=1080:1920:flags=lanczos"] + V + a +
        [out.replace("1920x1080_30fps", "1080x1920_9x16")])
    fb = ImageFont.truetype("/usr/share/fonts/opentype/inter/Inter-Bold.otf", 22)
    fr_ = ImageFont.truetype("/usr/share/fonts/opentype/inter/Inter-Regular.otf", 18)
    W, H, P = 640, 360, 16
    sheet = Image.new("RGB", (P + 2 * (W + P), 80 + 5 * (H + 62)), (14, 12, 18))
    d = ImageDraw.Draw(sheet)
    d.text((P, 22), "THE LAST JOB · EP01 · THE WRONG BAG · block previs contact sheet (EEVEE, 1920x1080, 30 fps)", font=fb, fill=(240, 230, 240))
    for i, s in enumerate(C.SHOTS):
        f = (s["f0"] + s["f1"]) // 2
        im = Image.open(os.path.join(C.P["frames"], f"f_{f:03d}.png")).convert("RGB").resize((W, H), Image.LANCZOS)
        x, y = P + (i % 2) * (W + P), 64 + (i // 2) * (H + 62)
        sheet.paste(im, (x, y))
        d.text((x, y + H + 6), f"{s['id']} · {s['cam']} · [{s['f0']:03d},{s['f1']:03d}) · {s['lens']} mm", font=fb, fill=(243, 74, 165))
        d.text((x, y + H + 32), s["desc"], font=fr_, fill=(220, 214, 224))
    sheet.save(os.path.join(C.P["delivery"], "LASTJOB_EP01_contact_sheet.png"))
    with open(os.path.join(C.P["delivery"], "LASTJOB_EP01_shot_list.csv"), "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["shot", "camera", "frame_in", "frame_out_exclusive", "lens_mm", "motion", "description", "dialogue"])
        for s in C.SHOTS:
            dl = "; ".join(f"{d['who'].split('_')[0]} \"{d['text']}\" f{d['f0']:03d}-f{d['f1']:03d}" for d in C.DIALOGUE if s["f0"] <= d["f0"] < s["f1"])
            w.writerow([s["id"], s["cam"], s["f0"], s["f1"], s["lens"], s["motion"], s["desc"], dl])
    print("DELIVERED", out)
