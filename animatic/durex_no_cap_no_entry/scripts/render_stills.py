"""Render QC stills with each shot's own camera.

blender -b DUREX_NO_CAP_animatic.blend --python scripts/render_stills.py -- <outdir> <percent> <samples> <frame> [<frame> ...]
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy
from common import SHOTS, ENDCARD_START

argv = sys.argv[sys.argv.index("--") + 1:]
out, pct, samples = argv[0], int(argv[1]), int(argv[2])
frames = [int(a) for a in argv[3:]]
os.makedirs(out, exist_ok=True)

main = bpy.data.scenes["DUREX_MAIN"]
endc = bpy.data.scenes["END_CARD"]
for sc in (main, endc):
    sc.render.resolution_percentage = pct
    sc.eevee.taa_render_samples = samples
    sc.render.image_settings.file_format = "PNG"

for f in frames:
    if f >= ENDCARD_START:
        sc = endc
        sc.frame_set(f - ENDCARD_START + 1)
    else:
        sc = main
        shot = next(s for s in SHOTS if s["start"] <= f <= s["end"])
        sc.camera = bpy.data.objects["CAM_%02d" % shot["n"]]
        sc.frame_set(f)
    sc.render.filepath = os.path.join(out, "f%04d.png" % f)
    bpy.ops.render.render(write_still=True, scene=sc.name)
    print("RENDERED", f)
