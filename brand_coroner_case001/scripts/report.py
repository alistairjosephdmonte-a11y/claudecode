"""Writes delivery/BC001_camera_and_continuity_report.md and delivery/BC001_source_register.md from the metadata JSON.
    python3 scripts/report.py"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import config as C  # noqa: E402

rep = json.load(open(os.path.join(C.P["metadata"], "continuity_report.json")))
man = json.load(open(os.path.join(C.P["metadata"], "shot_manifest.json")))
ev = json.load(open(os.path.join(C.P["metadata"], "evidence_register.json")))
assets = json.load(open(os.path.join(C.P["metadata"], "asset_register.json")))

L = ["# BRAND CORONER · CASE 001 · Camera and continuity report", "",
     f"48 shots · 240 frames each · 11,520 frames · 480.0 s at 24 fps · master {C.RES_FINAL[0]}x{C.RES_FINAL[1]} · AgX · "
     "motion blur 180° shutter equivalent (0.5 frame).", "", "## Validation assertions", "", "| Assertion | Result |", "|---|---|"]
for k, v in rep["assertions"].items():
    L.append(f"| {k.replace('_', ' ')} | {'PASS' if v else 'FAIL'} |")
L += ["", f"**All assertions pass: {rep['all_pass']}**", "", "## Continuity measurements", ""]
for k, v in rep["continuity"].items():
    L.append(f"- {k.replace('_', ' ')}: {v}")
L += ["", f"Visual mode share: {rep['visual_mode_share']} (targets: investigation 40%, reconstruction 25%, data 20%, archive 15%).", "",
      "## Shots", "", "| Shot | Time | Title | Mode | Class | Camera | Lens | Move | Max acc (m/s²) | Sources | Continuity |",
      "|---|---|---|---|---|---|---|---|---|---|---|"]
for s in man["shots"]:
    c = s["camera_report"]
    lens = "ortho" if c["type"] == "ORTHO" else f"{c['lens_mm']:.0f} mm"
    src = ", ".join(f"{x} ({'V' if ev_s.startswith('verified') else 'P'})" for x, ev_s in
                    ((x, next(e['status'] for e in ev['sources'] if e['id'] == x)) for x in s["source_ids"])) or "—"
    L.append(f"| {s['shot_id']} | {s['timecode']} | {s['title']} | {s['visual_mode']} | {s['classification']} | {c['camera']} | {lens} | "
             f"{c['move']} | {c['max_acc_m_s2']} | {src} | {s['continuity']} |")
L += ["", "V = verified source, P = pending verification (shown on screen with a PENDING tag).", ""]
with open(os.path.join(C.P["delivery"], "BC001_camera_and_continuity_report.md"), "w") as fh:
    fh.write("\n".join(L) + "\n")

S = ["# BRAND CORONER · CASE 001 · Source and asset register", "", ev["rule"], "", "## Sources", "",
     "| ID | Status | Citation | Used for | Note |", "|---|---|---|---|---|"]
for e in ev["sources"]:
    cit = f"[{e['citation']}]({e['url']})" if e["url"] else e["citation"]
    S.append(f"| {e['id']} | {e['status']} | {cit} | {e['use']} | {e['note']} |")
S += ["", "## Assets", "", assets["rule"], "", "| ID | Type | Status | Location | Note |", "|---|---|---|---|---|"]
for a in assets["assets"]:
    S.append(f"| {a['id']} | {a['type']} | {a['status']} | {a['path']} | {a['note']} |")
with open(os.path.join(C.P["delivery"], "BC001_source_and_asset_register.md"), "w") as fh:
    fh.write("\n".join(S) + "\n")
print("REPORTS written")
