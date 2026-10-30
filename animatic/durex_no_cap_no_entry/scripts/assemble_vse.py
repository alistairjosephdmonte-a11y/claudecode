"""Assemble rendered shot sequences in the Video Sequence Editor and export the 30 s MP4.

blender -b DUREX_NO_CAP_animatic.blend --python scripts/assemble_vse.py -- --pass eevee_50 \
    --out output/DUREX_NO_CAP_animatic_30s.mp4
Creates/replaces scene EDIT_VSE (saved into the .blend) with one image strip per shot, hard cuts only,
beat/bar markers for a separately licensed 120 BPM track and SFX cue markers. No audio is generated.
"""
import argparse
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import bpy
from common import SHOTS, ENDCARD_START, BEAT, FPS

ap = argparse.ArgumentParser()
ap.add_argument("--pass", dest="pass_name", default="eevee_50")
ap.add_argument("--out", default="output/DUREX_NO_CAP_animatic_30s.mp4")
ap.add_argument("--no-save", action="store_true")
args = ap.parse_args(sys.argv[sys.argv.index("--") + 1:])
ROOT = os.path.dirname(HERE)
SRC = os.path.join(ROOT, "renders", args.pass_name)

SFX_CUES = [
    (1, "SFX_STREET_TRAFFIC_AMB_IN"), (1, "SFX_CLUB_BASS_MUFFLED_THROUGH_DOOR"), (1, "MUSIC_LICENSED_120BPM_IN"),
    (75, "SFX_SHOES_WET_PAVEMENT_G01"), (97, "SFX_ARM_BLOCK_SWISH_ON_BEAT"), (147, "SFX_SHOES_WET_PAVEMENT_G02"),
    (150, "SFX_CONE_WOBBLE"), (169, "SFX_HEAD_SHAKE_ON_BEAT"), (225, "SFX_DISH_CREAK_01"), (241, "SFX_DISH_CREAK_02"),
    (253, "SFX_EYEBROW_ACCENT_ON_BEAT"), (265, "SFX_POINT_AWAY_ON_BEAT"), (291, "SFX_SHOES_WET_PAVEMENT_HERO"),
    (349, "SFX_CAP_FABRIC_TUG_ON_BEAT"), (421, "SFX_NOD_ON_BEAT"), (445, "SFX_ROPE_HOOK_CLINK_ON_BEAT"),
    (470, "SFX_CLUB_BASS_OPENS_UP_DOORWAY"), (505, "SFX_CLUB_INTERIOR_CROWD_AMB"), (607, "SFX_CAP_LIFT_FROM_SHELF"),
    (625, "SFX_CAP_HANDOFF_ON_BEAT"), (637, "SFX_CAP_ON_ON_BEAT"), (645, "SFX_ROPE_HOOK_CLINK_02"),
    (673, "SFX_FINAL_BASS_STOP_HARD_CUT"),
]


def main():
    old = bpy.data.scenes.get("EDIT_VSE")
    if old:
        bpy.data.scenes.remove(old)
    sc = bpy.data.scenes.new("EDIT_VSE")
    r = sc.render
    r.resolution_x, r.resolution_y, r.resolution_percentage = 1920, 1080, 100
    r.fps, r.fps_base = FPS, 1.0
    sc.frame_start, sc.frame_end = 1, 720
    sc.view_settings.view_transform = "Standard"
    se = sc.sequence_editor_create()
    plan = [("SH%02d" % s["n"], s["start"]) for s in SHOTS] + [("SH10_ENDCARD", ENDCARD_START)]
    total = 0
    for name, start in plan:
        d = os.path.join(SRC, name)
        files = sorted(f for f in os.listdir(d) if f.endswith(".png"))
        st = se.sequences.new_image(name, os.path.join(d, files[0]), 1, start, fit_method="FIT")
        for f in files[1:]:
            st.elements.append(f)
        st.directory = bpy.path.relpath(d) + "/"
        st["source_pass"] = args.pass_name
        total += len(files)
        print("STRIP", name, start, len(files))
    assert total == 720, "expected 720 frames of source, got %d" % total
    for s in SHOTS:
        m = sc.timeline_markers.new("SH%02d_%s" % (s["n"], s["name"].split("_", 1)[1]), frame=s["start"])
    sc.timeline_markers.new("SH10b_ENDCARD_BRAND_REVEAL", frame=ENDCARD_START)
    for i, f in enumerate(range(1, 721, BEAT * 4)):
        sc.timeline_markers.new("BAR_%02d" % (i + 1), frame=f)
    for f, name in SFX_CUES:
        sc.timeline_markers.new(name, frame=f)
    sc["sound_note"] = ("No music or SFX generated. Markers: BAR_xx = downbeats of a separately licensed 120 BPM track "
                        "(12 frames/beat at 24 fps); SFX_* = diegetic cue points for the sound designer.")
    r.image_settings.file_format = "FFMPEG"
    r.ffmpeg.format = "MPEG4"
    r.ffmpeg.codec = "H264"
    r.ffmpeg.constant_rate_factor = "HIGH"
    r.ffmpeg.ffmpeg_preset = "GOOD"
    r.ffmpeg.gopsize = 12
    r.ffmpeg.audio_codec = "NONE"
    r.use_sequencer = True
    out = os.path.join(ROOT, args.out)
    os.makedirs(os.path.dirname(out), exist_ok=True)
    r.filepath = out
    bpy.ops.render.render(animation=True, scene=sc.name)
    print("EXPORTED", out)
    if not args.no_save:
        bpy.ops.wm.save_mainfile(compress=True)
        print("SAVED blend with EDIT_VSE")


main()
