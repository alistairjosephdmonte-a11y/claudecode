"""Animatic and final renders.
    blender -b scenes/AMUL_OTM_EP01_MASTER.blend --python scripts/render.py -- --animatic --frames 1-720   (1280x720, 10 spp + OIDN)
    blender -b scenes/AMUL_OTM_EP01_MASTER.blend --python scripts/render.py -- --still 330                  (3840x2160, 64 spp hero still)
    blender -b scenes/AMUL_OTM_EP01_MASTER.blend --python scripts/render.py -- --final --frames 1-720      (3840x2160 master, 128 spp, all layers)
Output: renders/frames/f_####.png (animatic), renders/stills/, renders/final/."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy  # noqa: E402

import config as C  # noqa: E402

a = sys.argv[sys.argv.index("--") + 1:]
sc = bpy.context.scene
mode = a[0]
lo, hi = 1, C.TOTAL_FRAMES
if "--frames" in a:
    lo, hi = [int(v) for v in a[a.index("--frames") + 1].split("-")]
if mode == "--animatic":
    sc.render.resolution_x, sc.render.resolution_y = 1280, 720
    sc.cycles.samples = 10
    sc.render.image_settings.color_depth = "8"
    sc.render.filepath = os.path.join(C.P["frames"], "f_")
elif mode == "--still":
    f = int(a[1])
    sc.render.resolution_x, sc.render.resolution_y = C.RES_FINAL
    sc.cycles.samples = 64
    sc.render.image_settings.color_depth = "8"
    sc.frame_set(f)
    sc.render.filepath = os.path.join(C.P["stills"], f"AMUL_OTM_EP01_4K_f{f - 1:03d}.png")
    bpy.ops.render.render(write_still=True)
    sys.exit(0)
else:
    sc.render.resolution_x, sc.render.resolution_y = C.RES_FINAL
    sc.cycles.samples = 128
    for vl in sc.view_layers:
        vl.use = True
    sc.render.filepath = os.path.join(C.ROOT, "renders", "final", "f_")
sc.frame_start, sc.frame_end = lo, hi
sc.render.use_overwrite = False
sc.render.use_placeholder = True
bpy.ops.render.render(animation=True)
