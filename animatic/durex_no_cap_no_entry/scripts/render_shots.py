"""Render shots as separate PNG sequences, each with its own camera (for VSE assembly).

blender -b DUREX_NO_CAP_animatic.blend --python scripts/render_shots.py -- \
    --pass eevee_50 --engine EEVEE --pct 50 --samples 8 --shots 1 2 3
Shot 10 renders as SH10 (frames 649-672, CAM_10) plus SH10_ENDCARD (END_CARD scene, frames 673-720).
Output: renders/<pass>/SHxx/####.png numbered by MAIN timeline frame.
"""
import argparse
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import bpy
from common import SHOTS, ENDCARD_START

ap = argparse.ArgumentParser()
ap.add_argument("--pass", dest="pass_name", default="eevee_50")
ap.add_argument("--engine", default="EEVEE", choices=["EEVEE", "WORKBENCH"])
ap.add_argument("--pct", type=int, default=50)
ap.add_argument("--samples", type=int, default=8)
ap.add_argument("--shots", type=int, nargs="*", default=[s["n"] for s in SHOTS])
ap.add_argument("--endcard-only", action="store_true")
args = ap.parse_args(sys.argv[sys.argv.index("--") + 1:])

ROOT = os.path.dirname(HERE)
OUT = os.path.join(ROOT, "renders", args.pass_name)
main = bpy.data.scenes["DUREX_MAIN"]
endc = bpy.data.scenes["END_CARD"]


def configure(sc):
    r = sc.render
    r.resolution_percentage = args.pct
    r.image_settings.file_format = "PNG"
    r.image_settings.color_mode = "RGB"
    r.use_file_extension = True
    if args.engine == "WORKBENCH":
        r.engine = "BLENDER_WORKBENCH"
        sc.display.shading.light = "STUDIO"
        sc.display.shading.color_type = "MATERIAL"
        sc.display.shading.show_shadows = True
        sc.display.render_aa = "8"
    else:
        r.engine = "BLENDER_EEVEE_NEXT"
        sc.eevee.taa_render_samples = args.samples


for sc in (main, endc):
    configure(sc)

for n in ([10] if args.endcard_only else args.shots):
    s = next(x for x in SHOTS if x["n"] == n)
    end = ENDCARD_START - 1 if n == 10 else s["end"]
    if not args.endcard_only:
        main.camera = bpy.data.objects["CAM_%02d" % n]
        main.frame_start, main.frame_end = s["start"], end
        main.render.filepath = os.path.join(OUT, "SH%02d" % n, "")
        bpy.ops.render.render(animation=True, scene=main.name)
        print("SHOT_DONE", n)
    if n == 10:
        endc.frame_start, endc.frame_end = 1, 720 - ENDCARD_START + 1
        endc.render.filepath = os.path.join(OUT, "SH10_ENDCARD", "")
        bpy.ops.render.render(animation=True, scene=endc.name)
        print("SHOT_DONE endcard")
