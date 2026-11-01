"""BRAND CORONER · CASE 002: WEWORK · "The $47 Billion Illusion" — pure-Python project data (no bpy).
16 scenes × 720 frames = 11,520 frames = 480.0 s at 24 fps, 1920×1080, Rec.709 SDR."""
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = {k: os.path.join(ROOT, v) for k, v in {
    "crops": "evidence/document_crops", "filings": "evidence/sec_filings", "map": "evidence/map", "meta": "metadata",
    "scenes": "scenes", "tests": "renders/tests", "stills": "renders/stills", "frames": "renders/frames", "delivery": "delivery",
    "audio": "audio"}.items()}

FPS = 24
SCENE_FRAMES = 720
N_SCENES = 16
TOTAL_FRAMES = SCENE_FRAMES * N_SCENES
RES = (1920, 1080)

PALETTE = {"bg": "#080808", "red": "#FF2400", "type": "#F5F3EF", "gray": "#858585",
           # derived neutrals for panels and rules (same hue family, used sparingly)
           "panel": "#141414", "rule": "#2E2E2E", "map": "#1E1E1E"}

FONTS = {"display": "/usr/share/fonts/opentype/inter/InterDisplay-Bold.otf",
         "bold": "/usr/share/fonts/opentype/inter/Inter-Bold.otf",
         "semi": "/usr/share/fonts/opentype/inter/Inter-SemiBold.otf",
         "regular": "/usr/share/fonts/opentype/inter/Inter-Regular.otf"}

EDGAR = "https://www.sec.gov/Archives/edgar/data/"
# Every on-screen fact cites one of these. status: verified = checked against the primary document in evidence/sec_filings;
# reported = widely reported, primary document not attached (shown on screen with a red REPORTED tag).
SOURCES = {
    "S1": dict(label="the we company · form s-1 · filed aug 14, 2019 · sec edgar", status="verified",
               url=EDGAR + "1533523/000119312519220499/d781982ds1.htm"),
    "S1A_0904": dict(label="the we company · form s-1/a · filed sep 4, 2019 · sec edgar", status="verified",
                     url=EDGAR + "1533523/000119312519236798/d781982ds1a.htm"),
    "S1A_0913": dict(label="the we company · form s-1/a · filed sep 13, 2019 · sec edgar", status="verified",
                     url=EDGAR + "1533523/000119312519244329/d804478ds1a.htm"),
    "RW": dict(label="the we company · form rw (withdrawal request) · sep 30, 2019 · sec edgar", status="verified",
               url=EDGAR + "1533523/000119312519258913/d808793drw.htm"),
    "SB": dict(label="softbank group corp. · press release · oct 23, 2019", status="verified",
               url="https://group.softbank/en/news/press/20191023"),
    "BOWX": dict(label="wework / bowx · press release, ex. 99.1 to form 8-k · filed mar 26, 2021 · sec edgar", status="verified",
                 url=EDGAR + "1813756/000119312521095508/d29340dex991.htm"),
    "CLOSE": dict(label="wework inc. · form 8-k · filed oct 26, 2021 · sec edgar", status="verified",
                  url=EDGAR + "1813756/000119312521308162/d188107d8k.htm"),
    "10K22": dict(label="wework inc. · form 10-k, fiscal 2022 · filed mar 29, 2023 · sec edgar", status="verified",
                  url=EDGAR + "1813756/000181375623000016/we-20221231.htm"),
    "10Q": dict(label="wework inc. · form 10-q, quarter ended jun 30, 2023 · filed aug 8, 2023 · sec edgar", status="verified",
                url=EDGAR + "1813756/000181375623000059/we-20230630.htm"),
    "CH11": dict(label="wework inc. · form 8-k · filed nov 7, 2023 · sec edgar", status="verified",
                 url=EDGAR + "1813756/000119312523271902/d522028d8k.htm"),
    "Q3": dict(label="wework inc. · form 8-k, ex. 99.1 (unaudited) · filed nov 21, 2023 · sec edgar", status="verified",
               url=EDGAR + "1813756/000181375623000067/wework2023q310q.htm"),
    "EMERGE": dict(label="wework inc. · form 8-k · filed jun 12, 2024 · sec edgar", status="verified",
                   url=EDGAR + "1813756/000119312524159419/d803133d8k.htm"),
    "VAL47": dict(label="$47 billion private valuation, january 2019 · widely reported · primary citation to attach", status="reported",
                  url=""),
    "NE": dict(label="map: natural earth 1:110m land · public domain", status="verified",
               url="https://www.naturalearthdata.com/"),
    "ILLUS": dict(label="illustrative diagram · not drawn from contract data", status="illustrative", url=""),
}

# Verified figures (all amounts checked in the filings named; see delivery/BC002_fact_check.md)
FACTS = {
    "revenue_2016_k": 436_099, "revenue_2017_k": 886_004, "revenue_2018_k": 1_821_751,
    "net_loss_2018_k": 1_927_419, "net_loss_attrib_2018_k": 1_610_792,
    "op_lease_commenced_k": 33_953_402, "not_commenced_bn": 13.1, "total_signed_bn": 47.2,
    "trademark_m": 5.9, "votes_high_aug": 20, "votes_high_sep": 10, "votes_class_a": 1,
    "softbank_new_financing_bn": 5.0, "softbank_tender_bn": 3.0, "softbank_accelerated_bn": 1.5,
    "bowx_ev_bn": 9.0, "cash_jun30_2023_m": 205, "cash_sep30_2023_m": 462,
    "locations_jun2019": 528, "cities_jun2019": 111, "countries_jun2019": 29,
}

ACTS = [("ACT 01", "the valuation", [1, 2]), ("ACT 02", "the promise", [3, 4]), ("ACT 03", "the machine", [5, 6, 7]),
        ("ACT 04", "the documents speak", [8, 9, 10]), ("ACT 05", "the break", [11, 12]), ("ACT 06", "the reckoning", [13, 14, 15, 16])]

# scene: (title, [beats]); beat: (start_s, end_s, narration topic, [sources]). No narration text was supplied, so beats carry
# narration MARKERS (topic only), never invented lines.
SCENES = {
    1: ("the $47 billion contradiction", [
        (0, 9, "open on the reported 2019 private valuation", ["VAL47"]),
        (9, 17, "the company the number described (archival photography slot)", ["VAL47"]),
        (17, 30, "2019 valuation versus the november 2023 chapter 11 filing; what went wrong?", ["VAL47", "CH11"])]),
    2: ("the first clue", [
        (0, 10, "the bankruptcy filing and its date", ["CH11"]),
        (10, 21, "how money moved: landlord, wework, member", ["ILLUS"]),
        (21, 30, "flexible customers, long-term leases: the contradiction", ["ILLUS"])]),
    3: ("a different kind of office", [
        (0, 10, "traditional office versus flexible workspace", ["ILLUS"]),
        (10, 20, "what members got (archival photography slots)", []),
        (20, 30, "the first location, 154 grand street, 2010", ["S1"])]),
    4: ("selling the future", [
        (0, 8, "adam neumann and the expansion narrative (authenticated photo slot)", []),
        (8, 20, "from one building to 528 locations in 111 cities", ["S1", "NE"]),
        (20, 30, "growth is not profitability; could the economics support the ambition?", [])]),
    5: ("the business model", [
        (0, 10, "wework leases property from landlords", ["ILLUS"]),
        (10, 20, "fits it out and operates it", ["ILLUS"]),
        (20, 30, "members pay for access: lease, fit-out, operate, collect revenue", ["ILLUS"])]),
    6: ("the lease mismatch", [
        (0, 10, "two commitments of different lengths", ["ILLUS"]),
        (10, 20, "the shorter one can end; the longer one remains", ["ILLUS"]),
        (20, 30, "what the s-1 disclosed about lease length", ["S1"])]),
    7: ("the expansion machine", [
        (0, 10, "the contractual obligations table", ["S1"]),
        (10, 20, "$33.95 billion of commenced operating lease payments, undiscounted", ["S1"]),
        (20, 30, "plus about $13.1 billion signed but not yet commenced: a separate category", ["S1"])]),
    8: ("the ipo document", [
        (0, 9, "august 14, 2019: the s-1 is filed", ["S1"]),
        (9, 21, "financial statements, risk factors, related-party transactions", ["S1"]),
        (21, 30, "the evidence was public", ["S1"])]),
    9: ("the financial evidence", [
        (0, 12, "2018 revenue against 2018 net loss", ["S1"]),
        (12, 22, "the rows in the filing", ["S1"]),
        (22, 30, "revenue was growing; so were the questions", ["S1"])]),
    10: ("governance", [
        (0, 10, "the 'we' trademark transaction, about $5.9 million", ["S1"]),
        (10, 18, "later unwound", ["S1A_0904"]),
        (18, 30, "high-vote shares: 20 votes, later 10; who controlled the company?", ["S1", "S1A_0913"])]),
    11: ("the failed ipo", [
        (0, 10, "august 14, 2019: ipo registration", ["S1"]),
        (10, 20, "september 2019: adam neumann steps down as ceo", ["10K22"]),
        (20, 30, "september 30, 2019: ipo withdrawn; the ipo never happened", ["RW"])]),
    12: ("the rescue", [
        (0, 10, "softbank's october 2019 financing package", ["SB"]),
        (10, 20, "2021: merger with bowx, public listing", ["BOWX", "CLOSE"]),
        (20, 30, "two different measures; the dream was repriced", ["VAL47", "BOWX"])]),
    13: ("a world without offices", [
        (0, 10, "2020: remote work disruption (archival photography slot)", []),
        (10, 20, "what the company said, and what demand did", ["10K22", "10Q"]),
        (20, 30, "restructuring and lease renegotiation; a new shock, an old problem", ["10K22", "Q3"])]),
    14: ("the warning", [
        (0, 10, "august 2023: the going-concern warning", ["10Q"]),
        (10, 20, "cash at september 30, 2023: $462 million (unaudited, disclosed november 21)", ["Q3"]),
        (20, 30, "november 6, 2023: chapter 11; warning and filing are separate events", ["10Q", "CH11", "Q3"])]),
    15: ("what survived", [
        (0, 12, "chapter 11 to emergence: november 6, 2023 to june 11, 2024", ["CH11", "EMERGE"]),
        (12, 20, "the company continued in reorganized form (licensed photography slot)", ["EMERGE"]),
        (20, 30, "the business survived; the original valuation story did not", [])]),
    16: ("the final verdict", [
        (0, 8, "return to the number", ["VAL47"]),
        (8, 18, "four pieces of evidence", ["S1", "10Q"]),
        (18, 30, "verdict and brand coroner identity", [])]),
}

# Placeholders for media that must be licensed or authenticated. Nothing here is generated or simulated.
PLACEHOLDERS = {
    "P01": ("wework location photograph, 2019", "exterior or interior of an operating wework location, dated 2019. licensed archive (getty images, ap, reuters) or wework press archive."),
    "P02": ("early wework workspace, c. 2010–2012", "interior of an early wework space (e.g. 154 grand street, new york). licensed archive or wework press archive; date and location must be captioned by the source."),
    "P03": ("furnished private offices", "wework private-office interior, dated, captioned by the licensor."),
    "P04": ("shared workspace / lounge", "wework common area or hot-desk floor, dated, captioned by the licensor."),
    "P05": ("meeting room", "wework conference room, dated, captioned by the licensor."),
    "P06": ("adam neumann, authenticated photograph", "editorial photograph of adam neumann, c. 2017–2019, licensed (getty images / ap / reuters). no generated or altered likeness."),
    "P07": ("adam neumann, september 2019", "dated editorial photograph or wire image tied to the september 2019 ceo change. licensed."),
    "P08": ("empty office, 2020", "dated editorial photograph of an empty office or closed workspace during 2020 pandemic restrictions. licensed."),
    "P09": ("wework location in operation, 2024 or later", "dated photograph of a wework location operating after the june 11, 2024 emergence. licensed or wework press kit."),
}

AUDIO = {"note": "Temporary sound design synthesized in scripts/sound_design.py (sine/noise only; no samples, no music, "
                 "no voice). Replace with the licensed score and the supplied narration."}


def scene_start(n):
    return 1 + (n - 1) * SCENE_FRAMES


def tc(frame):
    s = (frame - 1) / FPS
    return f"{int(s // 60):02d}:{int(s % 60):02d}:{int(round((s % 1) * FPS)):02d}"


def manifest():
    out = {"project": "BRAND CORONER · CASE 002: WEWORK", "title": "the $47 billion illusion", "fps": FPS,
           "resolution": list(RES), "total_frames": TOTAL_FRAMES, "duration_s": TOTAL_FRAMES / FPS,
           "narration": "not supplied — silent animatic with narration markers (topics only)", "scenes": []}
    for n, (title, beats) in SCENES.items():
        act = next(a for a in ACTS if n in a[2])
        f0 = scene_start(n)
        out["scenes"].append({
            "scene": n, "id": f"SC{n:02d}", "act": f"{act[0]} · {act[1]}", "title": title, "frame_start": f0,
            "frame_end": f0 + SCENE_FRAMES - 1, "timecode_in": tc(f0), "timecode_out": tc(f0 + SCENE_FRAMES),
            "beats": [{"beat": i + 1, "start_s": round((f0 - 1) / FPS + b[0], 2), "end_s": round((f0 - 1) / FPS + b[1], 2),
                       "narration_marker": b[2], "sources": b[3]} for i, b in enumerate(beats)]})
    return out


if __name__ == "__main__":
    for p in P.values():
        os.makedirs(p, exist_ok=True)
    json.dump(manifest(), open(os.path.join(P["meta"], "scene_manifest.json"), "w"), indent=2)
    json.dump({"rule": "verified = checked against the primary document stored in evidence/sec_filings; reported = no primary "
                       "document attached, flagged on screen", "sources": SOURCES, "facts": FACTS},
              open(os.path.join(P["meta"], "source_register.json"), "w"), indent=2)
    json.dump({"rule": "placeholders mark media that must be licensed or authenticated; nothing is generated",
               "placeholders": {k: {"title": v[0], "required": v[1]} for k, v in PLACEHOLDERS.items()}},
              open(os.path.join(P["meta"], "placeholder_register.json"), "w"), indent=2)
    print("metadata written", TOTAL_FRAMES, "frames")
