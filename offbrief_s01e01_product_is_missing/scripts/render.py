"""Render frames from the master scene (Eevee). Skips frames already on disk.
    blender -b scenes/OFFBRIEF_S01E01_MASTER.blend --python scripts/render.py -- --range 1 720 --res 854 480 --samples 12 --out deliverables/frames_480p
    blender -b scenes/OFFBRIEF_S01E01_MASTER.blend --python scripts/render.py -- --frames 36,108 --res 854 480 --out /tmp/x
"""
import argparse
import os
import sys
import time

import bpy

ap = argparse.ArgumentParser()
ap.add_argument("--range", nargs=2, type=int)
ap.add_argument("--frames", type=str)
ap.add_argument("--res", nargs=2, type=int, default=(1920, 1080))
ap.add_argument("--samples", type=int, default=16)
ap.add_argument("--out", required=True)
ap.add_argument("--prefix", default="OFFBRIEF_S01E01_")
ap.add_argument("--force", action="store_true")
ap.add_argument("--fast", action="store_true", help="preview: shadows only from the sun and windows")
a = ap.parse_args(sys.argv[sys.argv.index("--") + 1:])

sc = bpy.context.scene
sc.render.resolution_x, sc.render.resolution_y = a.res
sc.render.resolution_percentage = 100
sc.eevee.taa_render_samples = a.samples
if a.fast:
    for o in bpy.data.objects:
        if o.type == "LIGHT" and not (o.name.startswith("LGT_Sun") or o.name.startswith("LGT_Window")):
            o.data.use_shadow = False
frames = list(range(a.range[0], a.range[1] + 1)) if a.range else [int(f) for f in a.frames.split(",")]
os.makedirs(a.out, exist_ok=True)
t0 = time.time()
for i, f in enumerate(frames):
    p = os.path.join(os.path.abspath(a.out), f"{a.prefix}{f:04d}.png")
    if not a.force and os.path.exists(p) and os.path.getsize(p) > 5000:
        continue
    sc.frame_set(f)
    sc.render.filepath = p
    bpy.ops.render.render(write_still=True)
    print(f"FRAME {f} done ({time.time() - t0:.1f}s elapsed)", flush=True)
print("RENDER_COMPLETE", len(frames), f"{time.time() - t0:.1f}s")
