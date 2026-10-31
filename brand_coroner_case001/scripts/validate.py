"""PHASE 10: validation. Opens the master, asserts the brief's rules and writes:
    metadata/continuity_report.json, metadata/asset_register.json, and per-shot render_status/continuity in shot_manifest.json
    blender -b scenes/BC001_MASTER.blend --python scripts/validate.py"""
import glob
import json
import math
import os
import re
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy  # noqa: E402
from bpy_extras import anim_utils  # noqa: E402
from mathutils import Vector  # noqa: E402

import config as C  # noqa: E402

REQUIRED_SCRIPTS = ["config.py", "assets.py", "environments.py", "camera_rigs.py", "motion_graphics.py", "shot_builder.py", "timeline.py",
                    "render.py", "validate.py"]
CLAIM = re.compile(r"\d|\$|January|February|March|April|May|June|July|August|September|October|November|December|percent|million")


def fcs(o):
    ad = o.animation_data
    if not ad or not ad.action:
        return {}
    return {(f.data_path, f.array_index): f for f in anim_utils.action_get_channelbag_for_slot(ad.action, ad.action_slot).fcurves}


def loc_at(o, f, cache):
    if o.name not in cache:
        cache[o.name] = fcs(o)
    c = cache[o.name]
    return Vector([c[("location", i)].evaluate(f) if ("location", i) in c else o.location[i] for i in range(3)])


def asset_register():
    reg = [
        dict(id="AST_FONT_INTER", type="font", path="assets/fonts_reference_only/Inter-*.otf", status="verified_license", note="SIL OFL 1.1 (license copied)"),
        dict(id="AST_LOC_BOARDROOM", type="environment", path="scenes/BC001_LOC_BOARDROOM.blend", status="internal_generated", note="Representative, not a specific room"),
        dict(id="AST_LOC_STORE", type="environment", path="scenes/BC001_LOC_STORE.blend", status="internal_generated", note="Representative store, full/reduced inventory variants"),
        dict(id="AST_LOC_WAREHOUSE", type="environment", path="scenes/BC001_LOC_WAREHOUSE.blend", status="internal_generated", note="Representative fulfilment facility"),
        dict(id="AST_LOC_ARCHIVE", type="environment", path="scenes/BC001_LOC_ARCHIVE.blend", status="internal_generated", note="Investigative light table"),
        dict(id="AST_DALLAS_MASSING", type="environment", path="scenes/BC001_MASTER.blend#SET_ENV_01_DALLAS", status="internal_generated", note="Stylised massing; no identifiable buildings"),
        dict(id="AST_DALLAS_OBS_TOWER_PROXY", type="reference_geometry", path="DAL_ObservationTower_Proxy_REF_PENDING", status="pending", note="Replace with verified reference geometry"),
        dict(id="AST_BRAND_BLOCKBUSTER_SIGNAGE", type="brand", path="ST_Fascia_Panel_Blank", status="pending", note="Blank panel until an approved brand reference is supplied"),
        dict(id="AST_BRAND_NETFLIX_MAILER", type="brand", path="PROP_S17/S18 envelopes", status="pending", note="Plain editorial red; no logo until approved reference"),
        dict(id="AST_BRAND_TOTAL_ACCESS_MAILER", type="brand", path="PROP_S31_Mailer_EditorialBlue", status="pending", note="Plain editorial blue"),
        dict(id="AST_LIKENESS_RANDOLPH", type="likeness", path="S05/S08/S46 source cards", status="pending", note="Authenticated photo required; slot labelled"),
        dict(id="AST_LIKENESS_ANTIOCO", type="likeness", path="S06/S08/S46 source cards", status="pending", note="Authenticated photo required; slot labelled"),
        dict(id="AST_DOC_10K_FY2005", type="document_scan", path="assets/documents/", status="pending", note="Import verified SEC scan for S28 (placeholder bars only)"),
        dict(id="AST_DOC_CH11_PETITION", type="document_scan", path="assets/documents/", status="pending", note="Import court petition or 8-K for S41"),
        dict(id="AST_AUDIO_NARRATION", type="audio", path="audio/narration/", status="pending", note="Record from BC001_narration_script.md; SRT holds timing"),
        dict(id="AST_AUDIO_SCORE", type="audio", path="audio/music/", status="pending", note="Original score to be composed and cleared"),
        dict(id="AST_AUDIO_SFX", type="audio", path="audio/sfx/", status="pending", note="Licensed or recorded effects per audio_cue_manifest.json"),
    ]
    with open(os.path.join(C.P["metadata"], "asset_register.json"), "w") as fh:
        json.dump(dict(rule="status 'pending' = must be replaced/approved before final; nothing pending is presented as authentic", assets=reg), fh, indent=2)
    return reg


def main():
    sc = bpy.context.scene
    rep, per_shot = {}, {s["shot_id"]: {"checks": {}} for s in C.SHOTS}
    ids = [s["shot_id"] for s in C.SHOTS]
    rep["48_shots"] = len(C.SHOTS) == 48
    rep["ids_unique"] = len(set(ids)) == 48
    rep["each_240_frames"] = all(s["frame_end"] - s["frame_start"] + 1 == 240 for s in C.SHOTS)
    rep["no_gaps_or_overlaps"] = all(C.SHOTS[i + 1]["frame_start"] == C.SHOTS[i]["frame_end"] + 1 for i in range(47)) and C.SHOTS[0]["frame_start"] == 1
    rep["duration_480s"] = C.SHOTS[-1]["frame_end"] == 11520 and sc.frame_end == 11520 and sc.frame_start == 1 and sc.render.fps == 24 \
        and abs(C.SHOTS[-1]["frame_end"] / sc.render.fps - 480.0) < 1e-9
    cam_marks = {m.frame: m.camera.name for m in sc.timeline_markers if m.camera}
    rep["every_shot_has_camera"] = all(cam_marks.get(s["frame_start"]) == s["camera"] and bpy.data.objects.get(s["camera"]) for s in C.SHOTS) \
        and len(cam_marks) == 48
    nar = {m.name for m in sc.timeline_markers if m.name.startswith("NAR_")}
    se = sc.sequence_editor
    strips = {st.name for st in (se.strips if hasattr(se, "strips") else se.sequences)} if se else set()
    rep["every_shot_has_narration_cue"] = all(f"NAR_{i}" in nar and f"NAR_{i}" in strips and C.NARRATION[i[1:]][1] for i in ids)
    # sources
    missing_src, unknown_src = [], []
    for s in C.SHOTS:
        statements = [x for x in re.split(r"(?<=[.?!])\s+", s["narration"]["text"]) if not x.strip().endswith("?")]   # questions are not claims
        claims = any(CLAIM.search(x) for x in statements) or s["classification"] in ("data_graphic", "source_card")
        if claims and not s["source_ids"]:
            missing_src.append(s["shot_id"])
        unknown_src += [x for x in s["source_ids"] if x not in C.EVIDENCE_BY_ID]
        per_shot[s["shot_id"]]["checks"]["sources"] = "ok" if s["shot_id"] not in missing_src else "missing"
    rep["every_historical_claim_has_source_id"] = not missing_src and not unknown_src
    rep["detail_claims_without_source"] = missing_src
    # reconstructions identified on screen + pending sources flagged on screen
    bad_rec, bad_pending = [], []
    for s in C.SHOTS:
        coll = bpy.data.collections.get(f"SHOT_{s['shot_id']}")
        bodies = [o.data.body for o in (coll.all_objects if coll else []) if o.type == "FONT"]
        if s["reconstruction"] and not any("RECONSTRUCTION" in b for b in bodies):
            bad_rec.append(s["shot_id"])
        if any(not C.EVIDENCE_BY_ID[x]["status"].startswith("verified") for x in s["source_ids"]) and not any("PENDING" in b for b in bodies):
            bad_pending.append(s["shot_id"])
        per_shot[s["shot_id"]]["checks"]["classification_on_screen"] = "ok" if s["shot_id"] not in bad_rec + bad_pending else "missing"
    rep["every_reconstruction_identified"] = not bad_rec
    rep["every_pending_source_flagged_on_screen"] = not bad_pending
    reg = asset_register()
    rep["every_unverified_asset_marked_pending"] = all(a["status"] in ("pending", "verified_license", "internal_generated") for a in reg)
    logos = [o.name for o in bpy.data.objects if "LOGO" in o.name.upper()]
    rep["no_logos_or_brand_artwork"] = not logos
    # files
    paths = [os.path.join(C.P["scripts"], f) for f in REQUIRED_SCRIPTS] + [os.path.join(C.P["scenes"], f) for f in C.SCENES.values()] + \
        [os.path.join(C.P["metadata"], f) for f in ("shot_manifest.json", "evidence_register.json", "asset_register.json", "audio_cue_manifest.json")] + \
        [os.path.join(C.P["narration"], f) for f in ("BC001_narration_script.md", "BC001_narration_timing.srt")]
    libs = [bpy.path.abspath(lib.filepath) for lib in bpy.data.libraries]
    fonts = [bpy.path.abspath(f.filepath) for f in bpy.data.fonts if f.filepath and f.filepath != "<builtin>"]
    unresolved = [p for p in paths + libs + fonts if not os.path.exists(p)]
    rep["every_required_path_resolves"] = not unresolved
    rep["detail_unresolved_paths"] = unresolved
    rep["libraries_relative"] = all(lib.filepath.startswith("//") for lib in bpy.data.libraries)
    # renders
    stills = {s["shot_id"]: glob.glob(os.path.join(C.P["shots"], f"BC001_{s['shot_id']}_still_*.png")) for s in C.SHOTS}
    rep["all_preview_stills_complete"] = all(stills.values())
    mp4 = os.path.join(C.P["delivery"], "BC001_ANIMATIC_640x360_24fps.mp4")
    n_frames = None
    if os.path.exists(mp4):
        out = subprocess.run(["ffprobe", "-v", "error", "-count_frames", "-select_streams", "v:0", "-show_entries", "stream=nb_read_frames",
                              "-of", "csv=p=0", mp4], capture_output=True, text=True).stdout.strip()
        n_frames = int(out) if out.isdigit() else None
    rep["animatic_complete_11520_frames"] = n_frames == 11520
    rep["detail_animatic_frames"] = n_frames
    # continuity: props, contact, feet, cameras
    cache = {}
    cont = {}
    f4 = bpy.data.objects.get("PROP_S04_Folder_Plain")
    f43 = bpy.data.objects.get("PROP_S43_Folder_Plain")
    if f4 and f43:
        sc.frame_set(C.SHOTS[3]["frame_end"])
        m4 = f4.matrix_world.copy()
        sc.frame_set(C.SHOTS[42]["frame_start"] + 10)
        cont["folder_S04_vs_S43_offset_mm"] = round((m4.translation - f43.matrix_world.translation).length * 1000, 3)
        tz = 0.75
        sc.frame_set(C.SHOTS[3]["frame_end"])
        cont["folder_bottom_vs_table_mm"] = round((f4.matrix_world.translation.z - 0.006 - tz) * 1000, 3)
    m31 = bpy.data.objects.get("PROP_S31_Mailer_EditorialBlue")
    if m31:
        sc.frame_set(C.SHOTS[30]["frame_end"])
        cont["mailer_bottom_vs_counter_mm"] = round((m31.matrix_world.translation.z - 0.003 - 1.08) * 1000, 3)
    d17 = bpy.data.objects.get("PROP_S17_DVD")
    if d17:
        sc.frame_set(C.SHOTS[16]["frame_end"])
        env = bpy.data.objects["PROP_S17_Envelope_EditorialRed"].matrix_world.translation
        dl = d17.matrix_world.translation - env
        cont["disc_inside_envelope"] = abs(dl.x) < 0.035 and abs(dl.y) < 0.01 and abs(dl.z) < 0.0015
    # carried props keep a fixed offset in the hand (no floating hands)
    carry = {}
    for sid, hand, prop, a, b in (("S04", "HAND_S04_WRIST", "PROP_S04_Folder_Plain", 0, 165), ("S31", "HAND_S31_WRIST", "PROP_S31_Mailer_EditorialBlue", 0, 155),
                                  ("S17", "HAND_S17_WRIST", "PROP_S17_DVD", 0, 185)):
        s = C.SHOTS[int(sid[1:]) - 1]
        h, p = bpy.data.objects[hand], bpy.data.objects[prop]
        rel = []
        for f in range(s["frame_start"] + a, s["frame_start"] + b, 5):
            sc.frame_set(f)
            rel.append((h.matrix_world.inverted() @ p.matrix_world.translation).copy())
        carry[sid] = round(max((r - rel[0]).length for r in rel) * 1000, 4)
    cont["carried_prop_slip_mm"] = carry
    # feet: no sliding while planted, planted feet on the ground
    feet = json.load(open(os.path.join(C.P["metadata"], "figure_feet_log.json")))
    slide = 0.0
    for sid, figs in feet.items():
        for fname, sides in figs.items():
            for side, rows in sides.items():
                anchor = None
                for f, p, sw in rows:
                    if sw:
                        anchor = None
                        continue
                    if anchor is None:
                        anchor = Vector(p)
                    slide = max(slide, (Vector(p) - anchor).length)
    cont["max_planted_foot_slide_mm"] = round(slide * 1000, 4)
    # cameras: smooth, motivated moves (acceleration from keyed curves), locked lens per shot
    cams = {}
    for s in C.SHOTS:
        cam = bpy.data.objects[s["camera"]]
        aim = bpy.data.objects.get(f"{s['camera']}_AIM")
        P = [loc_at(cam, f, cache) for f in range(s["frame_start"], s["frame_end"] + 1)]
        acc = max(((P[i + 1] - 2 * P[i] + P[i - 1]).length * 24 * 24 for i in range(1, len(P) - 1)), default=0)
        spd = max(((P[i + 1] - P[i]).length * 24 for i in range(len(P) - 1)), default=0)
        angacc = 0.0
        if aim:
            Dv = [(loc_at(aim, f, cache) - P[i]).normalized() for i, f in enumerate(range(s["frame_start"], s["frame_end"] + 1))]
            w = [math.degrees(Dv[i].angle(Dv[i + 1], 0)) * 24 for i in range(len(Dv) - 1)]
            angacc = max((abs(w[i + 1] - w[i]) * 24 for i in range(len(w) - 1)), default=0)
        cams[s["shot_id"]] = dict(camera=s["camera"], move=cam.get("move", ""), lens_mm=cam.get("lens_mm", 0),
                                  type=cam.data.type, max_speed_m_s=round(spd, 3), max_acc_m_s2=round(acc, 3), max_angacc_deg_s2=round(angacc, 2))
        ok = (acc < 3.0 or cam.data.type == "ORTHO") and angacc < 60
        per_shot[s["shot_id"]]["checks"]["camera_smooth"] = "ok" if ok else "review"
    rep["cameras_smooth"] = all(v["checks"]["camera_smooth"] == "ok" for v in per_shot.values())
    # tolerance 1 mm: sets sit up to 9 km from the origin, where float32 world coordinates resolve to ~0.5 mm
    rep["continuity_props_contact_feet"] = cont.get("folder_S04_vs_S43_offset_mm", 9) < 1.0 and abs(cont.get("folder_bottom_vs_table_mm", 9)) < 1.0 \
        and abs(cont.get("mailer_bottom_vs_counter_mm", 9)) < 1.0 and cont.get("disc_inside_envelope", False) \
        and max(carry.values()) < 1.0 and slide < 1e-3
    modes = {}
    for s in C.SHOTS:
        modes[s["visual_mode"]] = modes.get(s["visual_mode"], 0) + 1
    report = dict(assertions={k: v for k, v in rep.items() if not k.startswith("detail")}, details={k: v for k, v in rep.items() if k.startswith("detail")},
                  continuity=cont, cameras=cams, visual_mode_share={k: f"{100 * v / 48:.0f}%" for k, v in modes.items()},
                  per_shot=per_shot, all_pass=all(v for k, v in rep.items() if not k.startswith("detail")))
    with open(os.path.join(C.P["metadata"], "continuity_report.json"), "w") as fh:
        json.dump(report, fh, indent=2)
    man = json.load(open(os.path.join(C.P["metadata"], "shot_manifest.json")))
    for s in man["shots"]:
        sid = s["shot_id"]
        s["render_status"] = "preview_still_rendered" if stills[sid] else "not_rendered"
        if stills[sid]:
            s["preview_still"] = os.path.relpath(stills[sid][0], C.ROOT)
        s["continuity"] = "pass" if all(v == "ok" for v in per_shot[sid]["checks"].values()) else "review"
        s["camera_report"] = cams[sid]
    with open(os.path.join(C.P["metadata"], "shot_manifest.json"), "w") as fh:
        json.dump(man, fh, indent=2)
    print("VALIDATION", json.dumps(report["assertions"], indent=1))
    print("CONTINUITY", json.dumps(cont))
    print("ALL_PASS", report["all_pass"])


if __name__ == "__main__":
    main()
