"""Builds scenes/AMUL_OTM_EP01_MASTER.blend: environment, MOO_01 rig and artwork, performance, ten cameras with markers,
Cycles render settings, render layers / passes and the compositor.
    blender -b --factory-startup --python scripts/build.py"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy  # noqa: E402

import anim  # noqa: E402
import config as C  # noqa: E402
import env  # noqa: E402
import moo  # noqa: E402


def render_settings(sc):
    sc.render.engine = "CYCLES"
    sc.cycles.device = "GPU" if bpy.context.preferences.addons.get("cycles") and False else "CPU"
    sc.cycles.samples = 128                      # final; the animatic overrides this
    sc.cycles.adaptive_threshold = 0.02
    sc.cycles.use_adaptive_sampling = True
    sc.cycles.use_denoising = True
    sc.cycles.denoiser = "OPENIMAGEDENOISE"
    sc.cycles.max_bounces = 6
    sc.cycles.diffuse_bounces = 3
    sc.cycles.glossy_bounces = 3
    sc.cycles.transmission_bounces = 4
    sc.cycles.volume_bounces = 0
    sc.cycles.transparent_max_bounces = 16
    sc.cycles.volume_step_rate = 4.0
    sc.cycles.blur_glossy = 1.0
    sc.render.use_motion_blur = True
    sc.render.motion_blur_shutter = 0.5          # 180-degree shutter
    sc.render.fps = C.FPS
    sc.frame_start, sc.frame_end = 1, C.TOTAL_FRAMES
    sc.render.resolution_x, sc.render.resolution_y = C.RES_FINAL
    sc.render.resolution_percentage = 100
    sc.view_settings.view_transform = "AgX"
    sc.view_settings.look = "AgX - Base Contrast" if "AgX - Base Contrast" in [i.identifier for i in sc.view_settings.bl_rna.properties["look"].enum_items_static] else "None"
    sc.view_settings.exposure = 0.6
    sc.render.image_settings.file_format = "PNG"
    sc.render.image_settings.color_depth = "16"
    vl = sc.view_layers[0]
    vl.name = "01_BEAUTY"
    for k in ("use_pass_mist", "use_pass_ambient_occlusion", "use_pass_shadow_catcher", "use_pass_cryptomatte_object", "use_pass_z"):
        if hasattr(vl, k):
            setattr(vl, k, True)
        elif hasattr(vl.cycles, k):
            setattr(vl.cycles, k, True)
    vl.cycles.denoising_store_passes = True
    # separate layers for the final comp (disabled for the animatic); each excludes or holds out the other elements
    layers = {"02_MOO_ILLUSTRATED": ["MOO_SIDE_ART", "MOO_REAR_ART", "MOO_Q3_ART"], "03_MOO_SHADOW_CATCHER": ["MOO_PROXY"],
              "05_ATMOSPHERE": ["ENV_ATMOSPHERE"]}
    for name, keep in layers.items():
        nl = sc.view_layers.new(name)
        nl.use = False
        for lc in nl.layer_collection.children:
            if lc.name not in keep and not (name == "03_MOO_SHADOW_CATCHER" and lc.name.startswith("ENV_")):
                lc.holdout = True
    return vl


if __name__ == "__main__":
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    sc.name = "AMUL_OTM_EP01"
    rig = moo.build()
    E = env.build(sc, list(rig["hooves"].values()))
    cams_coll = moo.coll("CAMERAS")
    cams, poses = anim.build_shots(rig, cams_coll, E)
    render_settings(sc)
    out = os.path.join(C.P["scenes"], "AMUL_OTM_EP01_MASTER.blend")
    bpy.ops.wm.save_as_mainfile(filepath=out, relative_remap=True, compress=True)
    json.dump(anim.LOG, open(os.path.join(C.P["meta"], "build_log.json"), "w"), indent=1)
    print("SAVED", out, anim.LOG["notes"], "max leg overreach", anim.LOG["max_leg_overreach_m"])
