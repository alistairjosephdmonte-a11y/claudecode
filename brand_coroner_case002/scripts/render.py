"""Renders through the VSE edit scene (BC002_EDIT), so what is tested is exactly what the film contains.
    blender -b scenes/BC002_WEWORK.blend --python scripts/render.py -- --test            (one still per beat, renders/tests)
    blender -b scenes/BC002_WEWORK.blend --python scripts/render.py -- --frames 1-720    (PNG frames, renders/frames)
    python3 scripts/render.py --assemble                                                (H.264 MP4, Rec.709, with audio)"""
import os
import subprocess
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import config as C  # noqa: E402


def opts():
    a = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else sys.argv[1:]
    o = {"mode": None, "frames": None, "list": None}
    for i, k in enumerate(a):
        if k in ("--test", "--frames", "--assemble", "--list"):
            o["mode"] = k[2:]
        if k == "--frames":
            lo, hi = a[i + 1].split("-")
            o["frames"] = (int(lo), int(hi))
        if k == "--list":
            o["list"] = [int(v) for v in a[i + 1].split(",")]
    return o


def test_frames():
    out = []
    for n, (_, beats) in C.SCENES.items():
        for b0, b1, *_ in beats:
            out.append(C.scene_start(n) + int((b0 + (b1 - b0) * 0.72) * C.FPS))
    return out


def render_list(frames, folder, prefix):
    import bpy
    sc = bpy.data.scenes["BC002_EDIT"]
    os.makedirs(folder, exist_ok=True)
    for f in frames:
        sc.frame_set(f)
        sc.render.filepath = os.path.join(folder, f"{prefix}{f:05d}.png")
        t = time.time()
        bpy.ops.render.render(write_still=True, scene=sc.name)
        print("FRAME", f, round(time.time() - t, 2))


def render_range(lo, hi):
    import bpy
    sc = bpy.data.scenes["BC002_EDIT"]
    os.makedirs(C.P["frames"], exist_ok=True)
    sc.frame_start, sc.frame_end = lo, hi
    sc.render.filepath = os.path.join(C.P["frames"], "f_")
    sc.render.use_overwrite = False
    sc.render.use_placeholder = True
    bpy.ops.render.render(animation=True, scene=sc.name)


def assemble():
    frames = os.path.join(C.P["frames"], "f_%04d.png")
    wav = os.path.join(C.P["audio"], "BC002_temp_sound_design.wav")
    out = os.path.join(C.P["delivery"], "BC002_WEWORK_ANIMATIC_1920x1080_24fps.mp4")
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-framerate", str(C.FPS), "-i", frames]
    if os.path.exists(wav):
        cmd += ["-i", wav]
    cmd += ["-map", "0:v"] + (["-map", "1:a", "-c:a", "aac", "-b:a", "192k"] if os.path.exists(wav) else [])
    cmd += ["-c:v", "libx264", "-preset", "slow", "-crf", "16", "-pix_fmt", "yuv420p", "-profile:v", "high",
            "-vf", "scale=out_color_matrix=bt709:out_range=tv",
            "-color_primaries", "bt709", "-color_trc", "bt709", "-colorspace", "bt709", "-color_range", "tv",
            "-movflags", "+faststart", "-t", f"{C.TOTAL_FRAMES / C.FPS:.3f}", out]
    subprocess.run(cmd, check=True)
    print("MP4", out)


if __name__ == "__main__":
    o = opts()
    if o["mode"] == "assemble":
        assemble()
    elif o["mode"] == "test":
        render_list(test_frames(), C.P["tests"], "t_")
    elif o["mode"] == "list":
        render_list(o["list"], C.P["tests"], "t_")
    elif o["mode"] == "frames":
        render_range(*o["frames"])
