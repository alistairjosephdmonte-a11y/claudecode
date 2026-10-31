"""PHASES 6-7: 11,520-frame timeline assembly.
- One camera-bound marker per shot (the cut list), contiguous with no gaps or overlaps.
- Shot content and sets keyed visible only inside the frames that use them (constant interpolation).
- Narration markers + VSE placeholder strips (narration text strips, audio-cue colour strips). Rendering uses the
  cameras (render.use_sequencer = False); the VSE is the editorial/audio placeholder layer.
- Writes the narration script (Markdown) and a timed narration SRT."""
import os

import bpy

import config as C

SET_USE = {"SET_ENV_01_DALLAS": ["S01", "S02"], "SET_ENV_02_BOARDROOM": ["S03", "S04", "S43"],
           "SET_ENV_03_BLOCKBUSTER_STORE": ["S09", "S10", "S11", "S31"], "SET_ENV_07_DECLINING_STORE": ["S42"],
           "SET_ENV_04_DVD_FULFILLMENT": ["S17", "S18"], "SET_DESK_VIGNETTE": ["S22", "S25", "S36"]}


def _all_objects(coll):
    out = list(coll.objects)
    for ch in coll.children:
        out += _all_objects(ch)
    return out


def _constant(o):
    from bpy_extras import anim_utils
    ad = o.animation_data
    if not ad or not ad.action:
        return
    for fc in anim_utils.action_get_channelbag_for_slot(ad.action, ad.action_slot).fcurves:
        if fc.data_path in ("hide_render", "hide_viewport"):
            for k in fc.keyframe_points:
                k.interpolation = "CONSTANT"


def key_visible(o, ranges):
    """Visible only inside the given [(f0, f1)] ranges."""
    if o.type == "CAMERA":
        return
    keys = {1: True}
    for f0, f1 in sorted(ranges):
        keys[f0] = False
        keys[f1 + 1] = True
    for f, hide in sorted(keys.items()):
        if f > C.TOTAL_FRAMES + 1:
            continue
        o.hide_render = o.hide_viewport = hide
        o.keyframe_insert("hide_render", frame=f)
        o.keyframe_insert("hide_viewport", frame=f)
    _constant(o)


def assemble(build_results):
    sc = bpy.context.scene
    sc.timeline_markers.clear()
    by_id = {s["shot_id"]: s for s in C.SHOTS}
    # cut list
    for s in C.SHOTS:
        if s["camera"] not in bpy.data.objects:
            continue
        mk = sc.timeline_markers.new(f"{s['shot_id']}_{s['title'].upper().replace(' ', '_')[:28]}", frame=s["frame_start"])
        mk.camera = bpy.data.objects[s["camera"]]
    sc.camera = next(m.camera for m in sorted(sc.timeline_markers, key=lambda m: m.frame) if m.camera)
    # shot content visibility
    for s in C.SHOTS:
        coll = bpy.data.collections.get(f"SHOT_{s['shot_id']}")
        if coll:
            for o in _all_objects(coll):
                key_visible(o, [(s["frame_start"], s["frame_end"])])
    # set visibility (union of the shots that use each set)
    for set_name, sids in SET_USE.items():
        coll = bpy.data.collections.get(set_name)
        if not coll:
            continue
        rng = [(by_id[x]["frame_start"], by_id[x]["frame_end"]) for x in sids]
        for o in _all_objects(coll):
            key_visible(o, rng)
    arc = bpy.data.collections.get("SET_ENV_05_ARCHIVE_LIGHT_TABLE")
    if arc:
        for o in arc.objects:
            sid = o.name.split("_")[-1]
            if sid in by_id:
                key_visible(o, [(by_id[sid]["frame_start"], by_id[sid]["frame_end"])])
    # narration markers + VSE placeholders
    for s in C.SHOTS:
        sc.timeline_markers.new(f"NAR_{s['shot_id']}", frame=int(round(s["narration"]["start_s"] * C.FPS)) + 1)
    se = sc.sequence_editor_create()
    strips = se.strips if hasattr(se, "strips") else se.sequences
    for s in C.SHOTS:
        n = s["narration"]
        f0 = int(round(n["start_s"] * C.FPS)) + 1
        f1 = int(round(n["end_s"] * C.FPS)) + 1
        st = strips.new_effect(name=f"NAR_{s['shot_id']}", type="TEXT", channel=2, frame_start=f0, length=max(1, f1 - f0))
        st.text = n["text"]
        st.font_size = 28
    import json
    cues = json.load(open(os.path.join(C.P["metadata"], "audio_cue_manifest.json")))
    ch = {"ambience": 3, "sfx": 4, "music": 5}
    for c in cues:
        f0 = int(round(c["timeline_s"] * C.FPS)) + 1
        st = strips.new_effect(name=c["id"], type="COLOR", channel=ch[c["category"]], frame_start=f0, length=max(1, int(c["duration_s"] * C.FPS)))
        st.color = {"ambience": (0.2, 0.4, 0.3), "sfx": (0.5, 0.4, 0.1), "music": (0.25, 0.25, 0.55)}[c["category"]]
    sc.render.use_sequencer = False
    write_narration_docs()


def _srt_t(s):
    h, rem = divmod(s, 3600)
    m, sec = divmod(rem, 60)
    return f"{int(h):02d}:{int(m):02d}:{int(sec):02d},{int(round((sec % 1) * 1000)):03d}"


def write_narration_docs():
    os.makedirs(C.P["narration"], exist_ok=True)
    with open(os.path.join(C.P["narration"], "BC001_narration_timing.srt"), "w") as fh:
        for i, s in enumerate(C.SHOTS, 1):
            n = s["narration"]
            fh.write(f"{i}\n{_srt_t(n['start_s'])} --> {_srt_t(n['end_s'])}\n{n['text']}\n\n")
    words = sum(s["narration"]["words"] for s in C.SHOTS)
    lines = ["# BRAND CORONER · CASE 001 · THE $50 MILLION DECISION", "## Narration script (8:00)", "",
             f"{words} words · delivery about 150 wpm with planned silences · one continuous voice: calm, deliberate, evidence-led.",
             "Lines marked **PENDING** contain a claim whose source is not yet verified (see metadata/evidence_register.json); "
             "record them, but do not lock picture until the source clears or the line is rewritten.", ""]
    for a in C.ACTS:
        lines += [f"### {a[0].replace('_', ' ')} · {a[1]}", f"*{a[2]}*", ""]
        for s in [x for x in C.SHOTS if x["act_id"] == a[0]]:
            n = s["narration"]
            flag = f" **PENDING ({n['pending_source']})**" if n["pending_source"] else ""
            carry = f" · carries {n['carry_s']} s over the cut" if n["carries_over_cut"] else ""
            pron = f" · pronunciation: {n['pronunciation']}" if n["pronunciation"] else ""
            lines.append(f"**{s['shot_id']} · {s['timecode']} · {s['title']}** — silence {n['lead_silence_s']} s, "
                         f"line {n['start_s']:.2f}–{n['end_s']:.2f} s{carry}{pron}{flag}")
            lines.append(f"> {n['text']}")
            lines.append("")
    with open(os.path.join(C.P["narration"], "BC001_narration_script.md"), "w") as fh:
        fh.write("\n".join(lines) + "\n")
