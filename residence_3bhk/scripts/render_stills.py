"""Renders still cameras from scenes/residence_master.blend.

    blender -b scenes/residence_master.blend --python scripts/render_stills.py -- <camera|all> <width> <samples> <out_dir> [exr]

The isometric camera (CAM_01_Isometric) hides ceilings and turns on the cutaway booleans; the interior cameras
keep ceilings on. Output names follow the deliverable list (living_room_4k.png etc.) when width is 3840."""

import os
import sys
import time

import bpy

NAMES = {
    "CAM_00_TopDown_Validation": "topdown_validation",
    "CAM_01_Isometric": "apartment_isometric",
    "CAM_02_Entry": "entry",
    "CAM_03_Living": "living_room",
    "CAM_04_Dining": "dining_room",
    "CAM_05_Kitchen": "kitchen",
    "CAM_06_Master": "master_bedroom",
    "CAM_07_Bedroom1": "bedroom_01",
    "CAM_08_Bedroom2": "bedroom_02",
}
EXPOSURE = {"CAM_00_TopDown_Validation": 0.0, "CAM_01_Isometric": 0.3}
INTERIOR_EXPOSURE = 0.3


def set_cutaway(on):
    bpy.context.scene.render.film_transparent = on
    for c in ("ARCH_Ceilings", "CONTEXT_City"):
        lc = bpy.context.view_layer.layer_collection.children[c]
        lc.exclude = on
    for ob in bpy.data.objects:
        md = ob.modifiers.get("CUTAWAY")
        if md:
            md.show_render = on


def render(cam, width, samples, out_dir, exr=False):
    sc = bpy.context.scene
    for mk in sc.timeline_markers:          # walkthrough markers bind cameras; stills must not follow them
        mk.camera = None
    sc.camera = bpy.data.objects[cam]
    iso = cam in ("CAM_01_Isometric", "CAM_00_TopDown_Validation")
    set_cutaway(iso)
    sc.render.resolution_x = width
    sc.render.resolution_y = round(width * 9 / 16)
    if cam == "CAM_00_TopDown_Validation":
        sc.render.resolution_y = round(width * 0.62)
    sc.cycles.samples = samples
    sc.view_settings.exposure = EXPOSURE.get(cam, INTERIOR_EXPOSURE)
    tag = "4k" if width == 3840 else "%dp" % sc.render.resolution_y
    if exr:
        sc.render.image_settings.file_format = "OPEN_EXR"
        sc.render.image_settings.color_depth = "16"
        ext = ".exr"
    else:
        sc.render.image_settings.file_format = "PNG"
        sc.render.image_settings.color_depth = "16" if width >= 3840 else "8"
        ext = ".png"
    path = os.path.join(out_dir, "%s_%s%s" % (NAMES[cam], tag, ext))
    sc.render.filepath = path
    t = time.time()
    bpy.ops.render.render(write_still=True)
    print("RENDERED %s %s %.1fs" % (cam, path, time.time() - t), flush=True)


if __name__ == "__main__":
    a = sys.argv[sys.argv.index("--") + 1:]
    cams = list(NAMES) if a[0] == "all" else a[0].split(",")
    os.makedirs(a[3], exist_ok=True)
    for c in cams:
        render(c, int(a[1]), int(a[2]), a[3], len(a) > 4 and a[4] == "exr")
