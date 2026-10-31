"""PHASES 8-9: validation stills and the low-resolution animatic. Final 4K settings are documented here, not run.
    blender -b scenes/BC001_MASTER.blend --python scripts/render.py -- --stills [--shots 1,2,3] [--samples 16]
    blender -b scenes/BC001_MASTER.blend --python scripts/render.py -- --animatic [--frames 1-11520]
    python3 scripts/render.py --assemble          (ffmpeg: animatic frames -> delivery/BC001_ANIMATIC_640x360.mp4)

FINAL RENDER (not executed in previs; run per shot range on a GPU workstation or farm):
    blender -b scenes/BC001_MASTER.blend --python scripts/render.py -- --final --frames 1-240
  -> Eevee, 3840x2160, 64 samples, motion blur 180 deg, AgX, PNG 16-bit to renders/final/BC001_####.png
     (Cycles hero frames: set engine to CYCLES, 512 samples, denoise; same command with --cycles)."""
import json
import os
import subprocess
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import config as C  # noqa: E402

try:
    import bpy  # noqa: E402
except ImportError:
    bpy = None

SET_FOR_ENV = {"ENV_01_DALLAS": "SET_ENV_01_DALLAS", "ENV_02_BOARDROOM": "SET_ENV_02_BOARDROOM",
               "ENV_03_BLOCKBUSTER_STORE": "SET_ENV_03_BLOCKBUSTER_STORE", "ENV_07_DECLINING_STORE": "SET_ENV_07_DECLINING_STORE",
               "ENV_04_DVD_FULFILLMENT": "SET_ENV_04_DVD_FULFILLMENT", "ENV_05_ARCHIVE_LIGHT_TABLE": "SET_ENV_05_ARCHIVE_LIGHT_TABLE",
               "SET_DESK_VIGNETTE": "SET_DESK_VIGNETTE"}
STILL_OFFSET = 180                         # 7.5 s into each shot: moves and graphic builds have resolved


def args():
    a = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else sys.argv[1:]
    o = {"mode": None, "shots": None, "samples": 16, "frames": (1, C.TOTAL_FRAMES), "cycles": False}
    for i, k in enumerate(a):
        if k in ("--stills", "--animatic", "--final", "--assemble"):
            o["mode"] = k[2:]
        elif k == "--shots":
            o["shots"] = {f"S{int(v):02d}" for v in a[i + 1].split(",")}
        elif k == "--samples":
            o["samples"] = int(a[i + 1])
        elif k == "--frames":
            lo, hi = a[i + 1].split("-")
            o["frames"] = (int(lo), int(hi))
        elif k == "--cycles":
            o["cycles"] = True
    return o


def isolate(shot):
    """Render only what a shot needs (speed): its SHOT collection and its set."""
    vl = bpy.context.view_layer
    keep = {f"SHOT_{shot['shot_id']}", SET_FOR_ENV.get(shot["environment"], "")}
    for top in vl.layer_collection.children:
        for lc in top.children:
            lc.exclude = lc.name not in keep


def restore():
    for top in bpy.context.view_layer.layer_collection.children:
        for lc in top.children:
            lc.exclude = False


def stills(o):
    sc = bpy.context.scene
    sc.render.engine = "BLENDER_EEVEE"
    sc.eevee.taa_render_samples = o["samples"]
    sc.render.resolution_x, sc.render.resolution_y = C.RES_PREVIEW
    sc.render.resolution_percentage = 100
    sc.render.image_settings.file_format = "PNG"
    log_path = os.path.join(C.P["metadata"], "render_log.json")
    log = json.load(open(log_path)) if os.path.exists(log_path) else {}
    for s in C.SHOTS:
        if o["shots"] and s["shot_id"] not in o["shots"]:
            continue
        isolate(s)
        f = s["frame_start"] + STILL_OFFSET
        sc.frame_set(f)
        sc.camera = bpy.data.objects[s["camera"]]
        out = os.path.join(C.P["shots"], f"BC001_{s['shot_id']}_still_f{f:05d}.png")
        t = time.time()
        sc.render.filepath = out
        bpy.ops.render.render(write_still=True)
        log[s["shot_id"]] = dict(still=os.path.relpath(out, C.ROOT), frame=f, seconds=round(time.time() - t, 1), ok=os.path.exists(out))
        print("STILL", s["shot_id"], log[s["shot_id"]])
        restore()
        json.dump(log, open(log_path, "w"), indent=2)


def animatic(o):
    """Workbench playblast of the whole cut through the camera markers (fast, deterministic)."""
    sc = bpy.context.scene
    sc.render.engine = "BLENDER_WORKBENCH"
    sh = sc.display.shading
    sh.light, sh.color_type = "STUDIO", "MATERIAL"
    sh.show_shadows, sh.show_cavity = False, True              # studio shadows would double the typography
    sh.shadow_intensity = 0.35
    sc.display.render_aa = "8"
    sc.render.resolution_x, sc.render.resolution_y = C.RES_ANIMATIC
    sc.render.resolution_percentage = 100
    sc.render.use_motion_blur = False
    sc.render.image_settings.file_format = "PNG"
    out_dir = os.path.join(C.P["previews"], "animatic_frames")
    os.makedirs(out_dir, exist_ok=True)
    sc.render.filepath = os.path.join(out_dir, "frame_")
    sc.frame_start, sc.frame_end = o["frames"]
    bpy.ops.render.render(animation=True)
    sc.frame_start, sc.frame_end = 1, C.TOTAL_FRAMES


def final(o):
    sc = bpy.context.scene
    sc.render.engine = "CYCLES" if o["cycles"] else "BLENDER_EEVEE"
    sc.render.resolution_x, sc.render.resolution_y = C.RES_FINAL
    sc.render.image_settings.file_format = "PNG"
    sc.render.image_settings.color_depth = "16"
    sc.render.filepath = os.path.join(C.P["final"], "BC001_")
    sc.frame_start, sc.frame_end = o["frames"]
    bpy.ops.render.render(animation=True)


def assemble():
    frames = os.path.join(C.P["previews"], "animatic_frames", "frame_%04d.png")
    out = os.path.join(C.P["delivery"], "BC001_ANIMATIC_640x360_24fps.mp4")
    srt = os.path.join(C.P["narration"], "BC001_narration_timing.srt")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-framerate", str(C.FPS), "-i", frames, "-c:v", "libx264", "-pix_fmt", "yuv420p",
                    "-crf", "20", out], check=True)
    sub = out.replace(".mp4", "_with_narration_subtitles.mp4")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", out, "-i", srt, "-c", "copy", "-c:s", "mov_text", sub], check=True)
    print("ANIMATIC", out, sub)


if __name__ == "__main__":
    o = args()
    if o["mode"] == "assemble":
        assemble()
    elif o["mode"] == "stills":
        stills(o)
    elif o["mode"] == "animatic":
        animatic(o)
    elif o["mode"] == "final":
        final(o)
