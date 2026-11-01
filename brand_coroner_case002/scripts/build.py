"""Builds scenes/BC002_WEWORK.blend: 16 modular scene sequences (SC01..SC16) plus BC002_EDIT, whose Video Sequence Editor
assembles them into the 11,520-frame film with narration markers and the temporary sound-design track.
    blender -b --factory-startup --python scripts/build.py [-- --scenes 1,2]"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy  # noqa: E402

import config as C  # noqa: E402
import scenes  # noqa: E402


def args():
    a = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    sel = None
    if "--scenes" in a:
        sel = [int(v) for v in a[a.index("--scenes") + 1].split(",")]
    return sel


def text_width(S, o):
    dg = S.sc.view_layers[0].depsgraph
    dg.update()
    ev = o.evaluated_get(dg)
    xs = [v[0] for v in ev.bound_box]
    return (max(xs) - min(xs)) * o.scale.x


def finish_brand(S, extra):
    """Places the red full stop directly after 'brand coroner' (measured from the evaluated text)."""
    brand, dot = extra
    w = text_width(S, brand)
    brand.location.x = -0.16
    dot.location = (-0.16 + w / 2 + 0.16, brand.location.y - 0.26, dot.location.z)


def build(sel=None):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    built, logs = [], {}
    for n, fn in enumerate(scenes.BUILDERS, 1):
        if sel and n not in sel:
            continue
        S, extra = fn()
        if n == 16:
            finish_brand(S, extra)
        built.append(S)
        logs[S.name] = S.log
        print("BUILT", S.name, S.log["objects"], "objects")
    ed = bpy.data.scenes.new("BC002_EDIT")
    ed.render.resolution_x, ed.render.resolution_y = C.RES
    ed.render.resolution_percentage = 100
    ed.render.fps = C.FPS
    ed.view_settings.view_transform = "Standard"
    ed.view_settings.look = "None"
    ed.render.use_sequencer = True
    ed.render.image_settings.file_format = "PNG"
    ed.render.image_settings.color_mode = "RGB"
    se = ed.sequence_editor_create()
    strips = se.strips if hasattr(se, "strips") else se.sequences
    for S in built:
        f0 = C.scene_start(S.n)
        st = strips.new_scene(name=S.name, scene=S.sc, channel=1, frame_start=f0)
        st.scene_input = "CAMERA"
    ed.frame_start = 1
    ed.frame_end = C.scene_start(built[-1].n) + C.SCENE_FRAMES - 1
    # narration markers: no narration was supplied, so each beat carries its topic only (no invented lines)
    for n, (title, beats) in C.SCENES.items():
        if sel and n not in sel:
            continue
        for i, b in enumerate(beats):
            ed.timeline_markers.new(f"SC{n:02d}.{i + 1} NAR: {b[2][:48]}", frame=C.scene_start(n) + int(b[0] * C.FPS))
    wav = os.path.join(C.P["audio"], "BC002_temp_sound_design.wav")
    if os.path.exists(wav) and not sel:
        snd = strips.new_sound("TEMP_SOUND_DESIGN", wav, channel=3, frame_start=1)
        snd.volume = 1.0
    if bpy.context.window is not None:
        bpy.context.window.scene = ed
    out = os.path.join(C.P["scenes"], "BC002_WEWORK.blend" if not sel else "BC002_PARTIAL.blend")
    bpy.ops.wm.save_as_mainfile(filepath=out, relative_remap=True, compress=True)
    json.dump(logs, open(os.path.join(C.P["meta"], "build_log.json" if not sel else "build_log_partial.json"), "w"), indent=1)
    print("SAVED", out, ed.frame_end)


if __name__ == "__main__":
    build(args())
