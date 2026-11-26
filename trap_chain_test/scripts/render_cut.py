"""Renders the 15-second cut to deliverables/cut_frames/frame_####.png, skipping frames already on disk.

    blender -b scenes/trap_chain.blend --python scripts/render_cut.py -- <first> <last> <width> <samples> [out_dir]
"""

import os
import sys
import time

import bpy

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from cut_spec import film_frames  # noqa: E402

a = sys.argv[sys.argv.index("--") + 1:]
first, last, width, samples = (int(x) for x in a[:4])
sc = bpy.context.scene
out = a[4] if len(a) > 4 else os.path.join(os.path.dirname(bpy.data.filepath), "..", "deliverables", "cut_frames")
os.makedirs(out, exist_ok=True)
sc.render.resolution_x = width
sc.render.resolution_y = round(width * 9 / 16)
sc.cycles.samples = samples
sc.render.image_settings.file_format = "PNG"

cd = bpy.data.cameras.new("CAM_Cut")
cam = bpy.data.objects.new("CAM_Cut", cd)
sc.collection.objects.link(cam)
tgt = bpy.data.objects.new("CAM_Cut_Target", None)
sc.collection.objects.link(tgt)
tc = cam.constraints.new("TRACK_TO")
tc.target = tgt
tc.track_axis = "TRACK_NEGATIVE_Z"
tc.up_axis = "UP_Y"
cd.dof.use_dof = True
cd.dof.focus_object = tgt
cd.clip_start = 0.01
sc.camera = cam

for n, shot, i, sim, loc, target in film_frames():
    if not first <= n <= last:
        continue
    path = os.path.abspath(os.path.join(out, "frame_%04d.png" % n))
    if os.path.exists(path):
        continue
    t = time.time()
    cd.lens = shot[2]
    cd.dof.aperture_fstop = shot[3]
    cam.location = loc
    tgt.location = target
    sc.frame_set(sim)
    sc.render.filepath = path
    bpy.ops.render.render(write_still=True)
    print("FRAME %d %s sim %d %.1fs" % (n, shot[0], sim, time.time() - t), flush=True)
