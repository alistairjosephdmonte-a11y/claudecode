"""Writes the delivery documents from project data:
  delivery/BC002_fact_check.md          every on-screen figure, its exact filing source, and how it is labelled
  delivery/BC002_source_and_asset_register.md
  delivery/BC002_narration_markers.srt  narration markers (topics only; no narration was supplied)
  delivery/BC002_edit_and_render_report.md
    python3 scripts/report.py"""
import json
import os

import config as C

M = lambda n: os.path.join(C.P["meta"], n)  # noqa: E731
D = lambda n: os.path.join(C.P["delivery"], n)  # noqa: E731


def srt_t(s):
    h, r = divmod(s, 3600)
    m, x = divmod(r, 60)
    return f"{int(h):02d}:{int(m):02d}:{int(x):02d},{int(round((x % 1) * 1000)):03d}"


FACTS = [
    ("$47 billion (2019 private valuation)", "VAL47", "Reported figure (January 2019 SoftBank investment coverage). No primary document attached.",
     "Shown with a red REPORTED tag; never compared arithmetically with the 2021 enterprise value."),
    ("November 6, 2023 · Chapter 11", "CH11", "8-K Item 1.03: \"On November 6, 2023 (the 'Petition Date'), WeWork Inc. … filed voluntary petitions … under Chapter 11\".", "Highlighted in the filing."),
    ("First location: 154 Grand Street, New York, early 2010", "S1", "S-1 business overview: \"In early 2010, we opened our doors to our first member community at 154 Grand Street in New York City.\"", "Highlighted in the filing."),
    ("528 locations · 111 cities · 29 countries", "S1", "S-1: \"over 528 locations in 111 cities across 29 countries\" (as of June 30, 2019).", "Only the NYC marker is plotted; per-city data not sourced."),
    ("CEO until September 2019", "10K22", "10-K FY2022 note: Mr. Neumann's \"resignation as Chief Executive Officer in September 2019\".", ""),
    ("About 15 years: average initial term of U.S. leases", "S1", "S-1 risk factors: \"The average length of the initial term of our U.S. leases is approximately 15 years\".", "Scene 06 timelines are labelled illustrative."),
    ("$33.95 billion", "S1", "S-1 contractual obligations table, non-cancelable operating lease commitments, Total: $33,953,402 thousand (June 30, 2019), footnote (1): future undiscounted fixed minimum lease cost payments.",
     "Labelled 'future minimum payments on commenced operating leases, undiscounted'."),
    ("≈ $13.1 billion signed, not yet commenced", "S1", "S-1 footnote (1): \"Excludes an additional $13.1 billion relating to executed non-cancelable leases that have not yet commenced as of June 30, 2019.\"",
     "Kept as a separate category; never added to $33.95b on screen; labelled 'not one debt · not payable today'."),
    ("August 14, 2019 · S-1 filed", "S1", "S-1 cover: \"As filed with the Securities and Exchange Commission on August 14, 2019.\"", "Highlighted on the cover."),
    ("2018 revenue $1.82 billion", "S1", "S-1 selected financial data, Revenue 2018: $1,821,751 thousand.", "Bar drawn to scale (1 billion = 3.8 units)."),
    ("2018 net loss $1.61 billion", "S1", "S-1: Net loss attributable to WeWork Companies Inc. 2018: $(1,610,792) thousand; total net loss $(1,927,419) thousand.",
     "Labelled 'net loss attributable to wework companies inc. · a loss, not an expense line'; total $1.93b shown alongside."),
    ("2016 / 2017 revenue $0.44b / $0.89b", "S1", "S-1: Revenue 2016 $436,099k; 2017 $886,004k.", "Scene 09 growth bars."),
    ("Trademark transaction ≈ $5.9 million", "S1", "S-1 related-party note: partnership interests \"with a fair market value of approximately $5.9 million\", \"in lieu of paying cash\".",
     "Labelled 'paid in partnership interests, not cash'."),
    ("Trademark transaction later unwound", "S1A_0904", "S-1/A (Sep 4, 2019) heading: \"Unwinding of Receipt of Partnership Interests Relating to 'We' Family Trademarks\".", ""),
    ("High-vote shares: 20 votes, Class A: 1 vote", "S1", "S-1 (Aug 14, 2019): Class A \"one vote per share\"; Class B and C \"twenty votes per share\".",
     "Founder voting percentage is blank in the filing and is not shown."),
    ("Reduced to 10 votes", "S1A_0913", "S-1/A (Sep 13, 2019): \"Our high-vote stock will decrease from 20 votes per share to 10 votes per share.\"", ""),
    ("September 30, 2019 · IPO withdrawn", "RW", "Form RW dated September 30, 2019, requesting consent to withdraw the registration statement.", ""),
    ("SoftBank: $5b new financing · up to $3b tender offer · $1.5b accelerated", "SB", "SoftBank Group press release, Oct 23, 2019.",
     "Shown as three components, 'not a single sum'."),
    ("≈ $9 billion announced initial enterprise value", "BOWX", "Press release (Ex. 99.1, 8-K filed Mar 26, 2021): \"initial enterprise value of approximately $9 billion\".",
     "Labelled as a different measure from the 2019 private valuation; no percentage decline computed."),
    ("October 20, 2021 · merger closes / public listing", "CLOSE", "8-K filed Oct 26, 2021: \"the Closing, which occurred on October 20, 2021\".", ""),
    ("COVID-19 statement", "10K22", "10-K FY2022: \"We believe that the COVID-19 pandemic has accelerated the trends …\".", "Presented as the company's own position."),
    ("Member churn and weaker demand", "10Q", "10-Q Q2 2023: \"higher member churn and weaker demand than contemplated\".", ""),
    ("Going-concern warning, August 8, 2023", "10Q", "10-Q filed Aug 8, 2023: \"substantial doubt exists about the Company's ability to continue as a going concern\".", ""),
    ("$462 million cash, September 30, 2023", "Q3", "8-K filed Nov 21, 2023, Ex. 99.1 (unaudited): \"As of September 30, 2023, the Company had $462 million in cash and cash equivalents\".",
     "Labelled unaudited and disclosed Nov 21, 2023, after the Chapter 11 filing (see discrepancy note)."),
    ("June 11, 2024 · emergence", "EMERGE", "8-K filed Jun 12, 2024: \"The Plan became effective on June 11, 2024\".", ""),
    ("218 days", "CH11+EMERGE", "Computed: November 6, 2023 to June 11, 2024 (2024 is a leap year).", ""),
]

DISCREPANCIES = [
    "Scene 14: the brief pairs the going-concern disclosure with a September 2023 cash balance of about $462 million. The filings separate them: "
    "the going-concern warning first appears in the 10-Q filed August 8, 2023 (cash $205 million at June 30, 2023); the $462 million figure is "
    "cash at September 30, 2023, disclosed unaudited in an 8-K filed November 21, 2023, after the November 6 Chapter 11 petition. The film shows "
    "all four dates on a day-scaled timeline and labels the $462 million accordingly.",
    "Scene 09: the brief's '$1.61 billion net loss' is the net loss attributable to WeWork Companies Inc.; total 2018 net loss was $1.93 billion. "
    "Both are shown, with exact labels.",
    "Scene 01 and 12: the $47 billion private valuation has no primary filing in this pack. It is tagged REPORTED on screen until a primary "
    "citation (e.g. the SoftBank or WeWork January 2019 announcement) is attached.",
    "Typography: the brief lists on-screen statements in capitals but locks the identity as bold lowercase; all statements are set lowercase.",
    "Narration: the WeWork master documentary script was not supplied with the brief. The animatic is silent (temp sound design only) with "
    "narration markers per beat; no lines were written or voiced. Picture timing will need a conform pass once narration is recorded.",
]


if __name__ == "__main__":
    man = json.load(open(M("scene_manifest.json")))
    src = C.SOURCES
    L = ["# BRAND CORONER · CASE 002 · WEWORK · Fact check", "",
         "Every figure that appears on screen, the exact wording in the primary document, and how the film labels it. "
         "Primary documents are stored in `evidence/sec_filings/` (fetched from SEC EDGAR and SoftBank Group) and shown on screen as unedited "
         "renders of the filed pages (`evidence/document_crops/`).", "",
         "| On screen | Source | Exact source wording / value | Labelling on screen |", "|---|---|---|---|"]
    for f, s, w, lab in FACTS:
        sl = " + ".join(src[k]["label"] for k in s.split("+"))
        L.append(f"| {f} | {sl} | {w} | {lab} |")
    L += ["", "## Discrepancies flagged against the brief", ""] + [f"- {d}" for d in DISCREPANCIES]
    open(D("BC002_fact_check.md"), "w").write("\n".join(L) + "\n")

    crops = json.load(open(M("document_crops.json")))
    R = ["# BRAND CORONER · CASE 002 · Source and asset register", "", "## Sources", "", "| ID | Status | On-screen label | URL |", "|---|---|---|---|"]
    for k, v in src.items():
        R.append(f"| {k} | {v['status']} | {v['label']} | {v['url'] or '—'} |")
    R += ["", "## Authentic document crops (rendered from the filed HTML, not retyped)", "", "| Crop | Filing file | Highlighted phrases |", "|---|---|---|"]
    for k, v in crops.items():
        R.append(f"| {k} | {v['file']} | {'; '.join(m['text'] for m in v['marks'] if m['rects'])} |")
    R += ["", "## Placeholders (licensed or authenticated media required)", "",
          "Placeholders are dark frames with red crop marks, labelled 'placeholder' and 'no generated or simulated imagery'.", "",
          "| ID | Slot | Asset required |", "|---|---|---|"]
    for k, (t, need) in C.PLACEHOLDERS.items():
        R.append(f"| {k} | {t} | {need} |")
    R += ["", "## Other assets", "", "- Typeface: Inter / Inter Display (SIL Open Font License 1.1).",
          "- Map: Natural Earth 1:110m land, public domain.",
          "- Sound: `audio/BC002_temp_sound_design.wav`, synthesized in `scripts/sound_design.py` (no samples, no music, no voice). Temporary.",
          "- Brand: no WeWork or SoftBank logos are used; company names appear only as text and inside the filed documents."]
    open(D("BC002_source_and_asset_register.md"), "w").write("\n".join(R) + "\n")

    S = []
    i = 1
    for sc in man["scenes"]:
        for b in sc["beats"]:
            S.append(f"{i}\n{srt_t(b['start_s'])} --> {srt_t(b['end_s'])}\n[narration marker {sc['id']}.{b['beat']}] {b['narration_marker']}\n")
            i += 1
    open(D("BC002_narration_markers.srt"), "w").write("\n".join(S))

    cam = json.load(open(M("camera_check.json")))
    chk = json.load(open(M("frame_check.json"))) if os.path.exists(M("frame_check.json")) else None
    E = ["# BRAND CORONER · CASE 002 · Edit and render report", "",
         f"- Film: 16 scene sequences × 720 frames = {C.TOTAL_FRAMES} frames = {C.TOTAL_FRAMES / C.FPS:.1f} s at {C.FPS} fps, {C.RES[0]}×{C.RES[1]}, 16:9.",
         "- Project: `scenes/BC002_WEWORK.blend`: scenes SC01–SC16 (one orthographic camera each), and BC002_EDIT, whose VSE holds the 16 scene strips "
         "back to back (channel 1), the temporary sound design (channel 3), and one narration marker per beat.",
         "- Engine: Workbench, flat lighting, texture colour, 8× AA; view transform Standard (sRGB/Rec.709 transfer), so brand hex values render exactly.",
         "- Delivery encode: H.264 High, yuv420p, CRF 16, BT.709 primaries, transfer and matrix, TV range; AAC 192 kb/s.", "",
         "## Scenes", "", "| Scene | In | Act | Title | Beats (narration markers) |", "|---|---|---|---|---|"]
    for sc in man["scenes"]:
        E.append(f"| {sc['id']} | {sc['timecode_in']} | {sc['act']} | {sc['title']} | " + " / ".join(b["narration_marker"] for b in sc["beats"]) + " |")
    E += ["", "## Camera smoothness (screen terms, cuts excluded)", "", f"Limits: {cam['limits']}", "",
          "| Scene | Cuts | Max pan (frame widths/s) | Max pan acc. | Max zoom (%/s) | Max zoom acc. |", "|---|---|---|---|---|---|"]
    for k, v in cam["scenes"].items():
        E.append(f"| {k} | {v['cuts']} | {v['max_pan_fw_s']} | {v['max_pan_acc_fw_s2']} | {v['max_zoom_pct_s']} | {v['max_zoom_acc_pct_s2']} |")
    E += ["", f"Flags: {cam['flags'] or 'none'}"]
    if chk:
        E += ["", "## Frame check (rendered output)", ""] + [f"- {k}: {v}" for k, v in chk.items() if k != "per_scene"]
    open(D("BC002_edit_and_render_report.md"), "w").write("\n".join(E) + "\n")
    print("REPORTS written")
