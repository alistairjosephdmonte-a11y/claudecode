"""BRAND CORONER - CASE 001: BLOCKBUSTER - "THE $50 MILLION DECISION"
Single source of truth: timing, the 48-shot manifest, sources, palette, paths and narration.

Pure Python (no bpy), so it runs both inside Blender and as a plain script:
    python3 scripts/config.py          -> PHASE 1: creates the folder tree and writes /metadata JSON files
"""
import json
import os

# ---------------------------------------------------------------- global format
FPS = 24
SHOT_FRAMES = 240                     # 10.0 s
N_SHOTS = 48
SHOTS_PER_ACT = 8
TOTAL_FRAMES = SHOT_FRAMES * N_SHOTS  # 11,520
TOTAL_SECONDS = TOTAL_FRAMES / FPS    # 480.0
RES_FINAL = (3840, 2160)
RES_PREVIEW = (960, 540)
RES_ANIMATIC = (640, 360)
SHUTTER = 0.5                         # 180-degree shutter equivalent

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
P = {k: os.path.join(ROOT, *v) for k, v in {
    "scripts": ("scripts",), "scenes": ("scenes",), "metadata": ("metadata",), "assets": ("assets",),
    "fonts": ("assets", "fonts_reference_only"), "documents": ("assets", "documents"),
    "previews": ("renders", "previews"), "shots": ("renders", "shots"), "final": ("renders", "final"),
    "narration": ("audio", "narration"), "music": ("audio", "music"), "sfx": ("audio", "sfx"), "delivery": ("delivery",),
}.items()}
SCENES = {"MASTER": "BC001_MASTER.blend", "BOARDROOM": "BC001_LOC_BOARDROOM.blend", "STORE": "BC001_LOC_STORE.blend",
          "WAREHOUSE": "BC001_LOC_WAREHOUSE.blend", "ARCHIVE": "BC001_LOC_ARCHIVE.blend"}
FOLDERS = ["assets/architecture", "assets/retail", "assets/boardroom", "assets/warehouse", "assets/props", "assets/materials",
           "assets/documents", "assets/fonts_reference_only", "scripts", "scenes", "renders/previews", "renders/shots",
           "renders/final", "audio/narration", "audio/music", "audio/sfx", "metadata", "delivery"]
FONTS = {"regular": "Inter-Regular.otf", "semibold": "Inter-SemiBold.otf", "bold": "Inter-Bold.otf"}

# ---------------------------------------------------------------- editorial palette (not brand specifications)
PALETTE = {
    "CORONER_BLACK": "#111418", "EVIDENCE_IVORY": "#E8E3D8", "VERDICT_RED": "#C5534E", "BLOCKBUSTER_BLUE": "#254F91",
    "RETAIL_YELLOW": "#E8BC43", "NETFLIX_RED": "#C52232", "ARCHIVE_GREY": "#77828B",
}


def hex_to_linear(h):
    h = h.lstrip("#")
    srgb = [int(h[i:i + 2], 16) / 255.0 for i in (0, 2, 4)]
    return tuple(c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4 for c in srgb)


# ---------------------------------------------------------------- sources (status is what we could actually confirm)
EVIDENCE = [
    dict(id="SRC_RANDOLPH_2019", type="book", citation="Marc Randolph, That Will Never Work (Little, Brown, 2019)",
         url="", status="verified_publication",
         use="Randolph's recollection of the September 2000 Dallas meeting, the $50 million figure and the reaction he describes.",
         note="One participant's memoir. Recollection, not a transcript."),
    dict(id="SRC_INC_2019_EXCERPT", type="press", citation="Inc., excerpt of That Will Never Work (2019), archived copy",
         url="https://gwern.net/docs/www/www.inc.com/9f8939c6b25070c4677db37b5c9ebda5787814aa.html",
         status="verified_secondary", use="Confirms the excerpt places the meeting at Blockbuster headquarters in Dallas.",
         note="Secondary reproduction of the memoir."),
    dict(id="SRC_ANTIOCO_DISPUTE", type="pending", citation="Accounts attributed to John Antioco disputing details of the meeting",
         url="", status="pending_primary_source",
         use="The film's second account. Only secondary, biography-style summaries were found during research.",
         note="BLOCKER for final graphics: obtain a primary interview or statement before rendering S06 as final."),
    dict(id="SRC_BBI_10K_FY2004", type="filing", citation="Blockbuster Inc., Form 10-K for fiscal 2004 (SEC EDGAR)",
         url="https://www.sec.gov/Archives/edgar/data/1085734/000119312505063510/d10k.htm", status="verified_primary",
         use="Late fees ('extended viewing fees') ended January 1, 2005 at more than 4,500 company-operated U.S. stores.",
         note="Also the expected location of the year-end 2004 store count (see SRC_STORES_2004)."),
    dict(id="SRC_BBI_10K_FY2005", type="filing", citation="Blockbuster Inc., Form 10-K for fiscal 2005 (SEC EDGAR)",
         url="https://www.sec.gov/Archives/edgar/data/0001085734/000119312506055023/d10k.htm", status="verified_primary",
         use="Eliminated fees were about 14% of 2004 rental revenues; about $60 million in initial marketing and implementation "
             "costs in Q1-Q2 2005; rental revenues fell 5.0% from 2004.", note="Primary source for S15, S28, S29."),
    dict(id="SRC_STORES_2004", type="pending", citation="Approximately 9,100 stores worldwide at year-end 2004 (brief figure)",
         url="", status="pending_primary_check", use="S13 store count.",
         note="Not found in research. Confirm in the FY2004 10-K (Item 1/Item 2) before rendering final."),
    dict(id="SRC_EVF_2004", type="pending", citation="Approximately $622.4 million extended viewing fee revenue in 2004 (brief figure)",
         url="", status="pending_primary_check", use="S15 dollar value.",
         note="Not found in research. The FY2004 10-K projected $400-450 million for 2005 instead. Confirm before final."),
    dict(id="SRC_RENTAL_REDUCTION_2005", type="pending", citation="More than $500 million reduction in 2005 rental revenue (brief figure)",
         url="", status="pending_primary_check", use="S29.",
         note="Not supported by research: the FY2005 10-K reports rental revenues down 5.0%. Reconcile before final; never present as profit loss."),
    dict(id="SRC_BB_ONLINE_2004", type="pending", citation="Blockbuster Online launch, August 2004 (brief figure)", url="",
         status="pending_primary_check", use="S25 launch date.", note="Launch year 2004 widely reported; the month was not confirmed."),
    dict(id="SRC_TOTAL_ACCESS_2006", type="press", citation="Blockbuster Total Access launched November 1, 2006 (press coverage)",
         url="https://archives-new.honoluluadvertiser.com/article/2006/Nov/02/bz/FP611020318.html", status="verified_secondary",
         use="S30-S31: launch date and in-store returns of mailed discs.", note="Import the original Blockbuster press release for final."),
    dict(id="SRC_TA_SUBSCRIBERS", type="pending", citation="Total Access subscriber counts (storyboard: 2.2M 2006, 3M+ Apr 2007)", url="",
         status="pending_primary_check", use="S32 bars.",
         note="Research found 'more than 2 million' reported in early 2007 (Hollywood Reporter). Exact values unconfirmed."),
    dict(id="SRC_NFLX_INSTANT_2007", type="press_release", citation="Netflix press release, January 16, 2007: instant viewing on PCs",
         url="https://about.netflix.com/en/news/netflix-offers-subscribers-the-option-of-instantly-watching-movies-on-their",
         status="verified_primary", use="S35: announced January 2007, initially about 1,000 titles, Windows PCs.", note=""),
    dict(id="SRC_BBI_CH11_2010", type="press", citation="Blockbuster Chapter 11 filing, September 23, 2010 (Bloomberg; TechCrunch)",
         url="https://www.bloomberg.com/news/2010-09-23/blockbuster-video-rental-chain-files-for-bankruptcy-protection.html",
         status="verified_secondary", use="S41 filing date; stores and online service continued operating during the case (S42).",
         note="Import the court petition or Form 8-K scan for the document graphic; none is rendered until imported."),
    dict(id="SRC_SCALE_2000", type="pending", citation="Relative size of Blockbuster and Netflix in 2000", url="",
         status="pending_primary_check", use="S23 qualitative comparison.",
         note="Use FY2000 filings (revenue, stores, subscribers) before showing any numbers. Shown only as not-to-scale blocks."),
    dict(id="SRC_NFLX_NO_LATE_FEES", type="pending", citation="Netflix subscription without late fees (circa 1999-2000)", url="",
         status="pending_primary_check", use="S19 narration line.", note="Widely reported; import a primary Netflix source."),
]
EVIDENCE_BY_ID = {e["id"]: e for e in EVIDENCE}

# ---------------------------------------------------------------- acts (storyboard)
ACTS = [("ACT_01", "THE OFFER", "A famous proposal, two conflicting recollections, one unanswered question."),
        ("ACT_02", "THE EMPIRE", "Blockbuster's greatest strength was a vast physical distribution system."),
        ("ACT_03", "THE CHALLENGER", "Netflix approached the same customer problem through a different operating model."),
        ("ACT_04", "THE COUNTERATTACK", "Blockbuster responded, but competing in two systems came at a cost."),
        ("ACT_05", "THE TRAP", "The market changed again before the Blockbuster had completed its transition."),
        ("ACT_06", "THE VERDICT", "The failure cannot be explained by one meeting alone.")]

# ---------------------------------------------------------------- 48 shots: id, title, caption (storyboard text), mode, env, class, sources
# mode: INV = visual investigation, REC = photographic historical reconstruction, DATA = data storytelling, ARC = archive light table
_S = [
    ("01", "Dallas, September 2000", "City establishing shot.", "REC", "ENV_01_DALLAS", "reconstruction", ["SRC_RANDOLPH_2019", "SRC_INC_2019_EXCERPT"]),
    ("02", "Three visitors arrive", "Enter the corporate building.", "REC", "ENV_01_DALLAS", "reconstruction", ["SRC_RANDOLPH_2019"]),
    ("03", "The meeting room", "Representative reconstruction.", "REC", "ENV_02_BOARDROOM", "reconstruction", ["SRC_RANDOLPH_2019"]),
    ("04", "The proposal", "A plain folder is placed on the table.", "REC", "ENV_02_BOARDROOM", "reconstruction", ["SRC_RANDOLPH_2019"]),
    ("05", "Marc Randolph's account", "Source card with verified attribution.", "ARC", "ENV_05_ARCHIVE_LIGHT_TABLE", "source_card", ["SRC_RANDOLPH_2019"]),
    ("06", "John Antioco account", "Source card with verified attribution.", "ARC", "ENV_05_ARCHIVE_LIGHT_TABLE", "source_card", ["SRC_ANTIOCO_DISPUTE"]),
    ("07", "The number", "Attributed to Randolph's account.", "DATA", "ENV_06_FINANCIAL_GRAPHICS", "editorial_graphic", ["SRC_RANDOLPH_2019"]),
    ("08", "The number", "Two accounts, one question.", "ARC", "ENV_05_ARCHIVE_LIGHT_TABLE", "editorial_graphic", ["SRC_RANDOLPH_2019", "SRC_ANTIOCO_DISPUTE"]),
    ("09", "Friday night", "A busy store in the 1990s.", "REC", "ENV_03_BLOCKBUSTER_STORE", "reconstruction", []),
    ("10", "Inside the store", "Customers browse the aisles.", "REC", "ENV_03_BLOCKBUSTER_STORE", "reconstruction", []),
    ("11", "At the counter", "Rental, membership, register.", "REC", "ENV_03_BLOCKBUSTER_STORE", "reconstruction", []),
    ("12", "An expanding network", "One store becomes thousands.", "DATA", "ENV_06_FINANCIAL_GRAPHICS", "editorial_graphic", ["SRC_STORES_2004"]),
    ("13", "The scale", "Approximately 9,100 stores.", "DATA", "ENV_06_FINANCIAL_GRAPHICS", "data_graphic", ["SRC_STORES_2004"]),
    ("14", "The rental model", "Receipt and transaction details.", "ARC", "ENV_05_ARCHIVE_LIGHT_TABLE", "editorial_graphic", []),
    ("15", "A profitable policy", "14% of rental revenue.", "DATA", "ENV_06_FINANCIAL_GRAPHICS", "data_graphic", ["SRC_BBI_10K_FY2005", "SRC_EVF_2004"]),
    ("16", "A heavy business", "A large network is hard to move.", "INV", "ENV_06_FINANCIAL_GRAPHICS", "editorial_graphic", []),
    ("17", "A new approach", "A DVD enters a red envelope.", "REC", "ENV_04_DVD_FULFILLMENT", "reconstruction", []),
    ("18", "In the mail", "Envelopes move through sorting.", "REC", "ENV_04_DVD_FULFILLMENT", "reconstruction", []),
    ("19", "The subscription loop", "A simple customer experience.", "INV", "ENV_06_FINANCIAL_GRAPHICS", "editorial_graphic", ["SRC_NFLX_NO_LATE_FEES"]),
    ("20", "Two operating models", "Retail versus mail-based.", "INV", "ENV_06_FINANCIAL_GRAPHICS", "editorial_graphic", []),
    ("21", "Cost structures", "Different costs, different risks.", "DATA", "ENV_06_FINANCIAL_GRAPHICS", "editorial_graphic", []),
    ("22", "A growing online presence", "Early 2000s web environment.", "INV", "SET_DESK_VIGNETTE", "reconstruction", []),
    ("23", "Relative size in 2000", "Blockbuster was much larger.", "DATA", "ENV_06_FINANCIAL_GRAPHICS", "data_graphic", ["SRC_SCALE_2000"]),
    ("24", "A critical question", "A critical question.", "INV", "ENV_06_FINANCIAL_GRAPHICS", "editorial_graphic", []),
    ("25", "A real response", "Blockbuster launches online.", "INV", "SET_DESK_VIGNETTE", "editorial_graphic", ["SRC_BB_ONLINE_2004"]),
    ("26", "Two systems", "Stores and online operate together.", "INV", "ENV_06_FINANCIAL_GRAPHICS", "editorial_graphic", []),
    ("27", "A major change", "January 2005 initiative.", "INV", "ENV_06_FINANCIAL_GRAPHICS", "editorial_graphic", ["SRC_BBI_10K_FY2004"]),
    ("28", "The financial impact", "From the 2005 Form 10-K.", "ARC", "ENV_05_ARCHIVE_LIGHT_TABLE", "source_card", ["SRC_BBI_10K_FY2005"]),
    ("29", "Costs and consequences", "Revenue reduction and costs.", "DATA", "ENV_06_FINANCIAL_GRAPHICS", "data_graphic", ["SRC_BBI_10K_FY2005", "SRC_RENTAL_REDUCTION_2005"]),
    ("30", "November 2006", "Total Access launches.", "INV", "ENV_06_FINANCIAL_GRAPHICS", "editorial_graphic", ["SRC_TOTAL_ACCESS_2006"]),
    ("31", "Connecting the systems", "Return mailed DVDs in stores.", "REC", "ENV_03_BLOCKBUSTER_STORE", "reconstruction", ["SRC_TOTAL_ACCESS_2006"]),
    ("32", "Subscriber growth", "Success and high operating costs.", "DATA", "ENV_06_FINANCIAL_GRAPHICS", "data_graphic", ["SRC_TA_SUBSCRIBERS"]),
    ("33", "Growth and losses", "More customers but high costs.", "DATA", "ENV_06_FINANCIAL_GRAPHICS", "editorial_graphic", []),
    ("34", "Three business models", "Increasing complexity.", "INV", "ENV_06_FINANCIAL_GRAPHICS", "editorial_graphic", []),
    ("35", "Netflix instant viewing", "Initially PC-based, ~1,000 titles.", "INV", "ENV_06_FINANCIAL_GRAPHICS", "editorial_graphic", ["SRC_NFLX_INSTANT_2007"]),
    ("36", "Early streaming", "A new way to watch at home.", "REC", "SET_DESK_VIGNETTE", "reconstruction", ["SRC_NFLX_INSTANT_2007"]),
    ("37", "A changing market", "Three channels compete.", "INV", "ENV_06_FINANCIAL_GRAPHICS", "editorial_graphic", []),
    ("38", "Rising costs", "Transition puts pressure on margins.", "ARC", "ENV_05_ARCHIVE_LIGHT_TABLE", "editorial_graphic", []),
    ("39", "Financial constraints", "Less room to maneuver.", "DATA", "ENV_06_FINANCIAL_GRAPHICS", "editorial_graphic", []),
    ("40", "The network dims", "A dominant model begins to fade.", "INV", "ENV_06_FINANCIAL_GRAPHICS", "editorial_graphic", []),
    ("41", "The bankruptcy filing", "Chapter 11 protection.", "INV", "ENV_05_ARCHIVE_LIGHT_TABLE", "source_card", ["SRC_BBI_CH11_2010"]),
    ("42", "A quieter world", "A representative closed store.", "REC", "ENV_07_DECLINING_STORE", "reconstruction", ["SRC_BBI_CH11_2010"]),
    ("43", "The meeting returns", "A famous but disputed moment.", "INV", "ENV_02_BOARDROOM", "reconstruction", ["SRC_RANDOLPH_2019", "SRC_ANTIOCO_DISPUTE"]),
    ("44", "Hypothetical scenarios", "Possible, but unproven outcomes.", "INV", "ENV_06_FINANCIAL_GRAPHICS", "editorial_graphic", []),
    ("45", "Three converging forces", "A more complex explanation.", "INV", "ENV_06_FINANCIAL_GRAPHICS", "editorial_graphic", []),
    ("46", "The evidence", "A broader view of the record.", "ARC", "ENV_05_ARCHIVE_LIGHT_TABLE", "editorial_graphic", []),
    ("47", "The verdict", "A nuanced conclusion.", "INV", "ENV_06_FINANCIAL_GRAPHICS", "editorial_graphic", []),
    ("48", "End title", "Case 001 complete.", "INV", "ENV_06_FINANCIAL_GRAPHICS", "editorial_graphic", []),
]

# ---------------------------------------------------------------- narration (one continuous script; per-shot lines)
# lead = silence before the line (s); claims flagged PENDING are spoken only after their source clears.
NARRATION = {
    "01": (2.5, "Dallas, Texas. September 2000. A meeting took place in this city that is now retold, again and again, as a business parable."),
    "02": (1.0, "According to Marc Randolph, a Netflix co-founder, three Netflix executives came here to meet the leadership of Blockbuster, the largest name in video rental."),
    "03": (1.0, "We have no transcript of that meeting. The room you are seeing is representative, and the people who were there remember the day differently."),
    "04": (1.5, "In Randolph's version, Netflix proposed that Blockbuster buy the company, and that the Netflix team run Blockbuster's business online."),
    "05": (1.0, "Randolph described the meeting in his 2019 memoir. He recalls the price that was named, and a reaction he read as dismissive."),
    "06": (1.0, "Accounts attributed to John Antioco, then Blockbuster's chief executive, describe the encounter differently. We are still verifying that account against a primary source."),
    "07": (1.5, "The figure at the center of the story is fifty million dollars. It comes from Randolph's account, and it is where most retellings begin."),
    "08": (1.0, "Two recollections. One number. And a question that a single meeting, however famous, cannot answer on its own."),
    "09": (2.0, "To understand the decision, start with the business Blockbuster had built, and the Friday nights that built it."),
    "10": (1.0, "Its strength was physical: walls of tapes and discs, new releases in bulk, and stores close to where customers lived."),
    "11": (1.0, "A customer chose a film, showed a membership card, paid at the counter, and promised to bring it back by a due date."),
    "12": (1.0, "Repeated store by store, city by city, that simple transaction grew into a vast retail network."),
    "13": (1.0, "By the end of 2004, the company described a network of roughly nine thousand one hundred stores around the world."),
    "14": (1.0, "Every rental carried a due date, and every late return carried a fee. That small line on a receipt added up."),
    "15": (1.0, "The company later reported that those extended viewing fees made up about fourteen percent of its rental revenue in 2004."),
    "16": (1.0, "A system this large is powerful. It is also heavy, and heavy systems are slow to change direction when the ground moves."),
    "17": (1.0, "Netflix approached the same customer problem from the other side: a disc, a paper envelope, and a mailbox."),
    "18": (1.0, "There was no storefront. Orders moved through distribution centers, sorting lines and the postal system."),
    "19": (1.0, "Customers paid a monthly subscription, received discs, watched them, and sent them back. In this model there were no late fees."),
    "20": (1.0, "Two businesses now served the same evening at home, for the same customers, with very different machinery working behind each of them."),
    "21": (1.0, "One carried rent, inventory and staff across thousands of locations. The other carried postage, fulfillment, and the cost of winning subscribers."),
    "22": (1.0, "And it lived online, on early web pages and order forms, years before most viewers expected movies to arrive that way."),
    "23": (1.0, "In 2000, the difference in scale was enormous. Blockbuster was by far the larger company, and the more established brand."),
    "24": (3.0, "So was the threat obvious in 2000? Or does it only look obvious now?"),
    "25": (1.0, "Blockbuster did respond. It moved into online rental, with a service launched in 2004 to compete directly by mail."),
    "26": (1.0, "Now it ran two systems side by side: thousands of stores, and a growing operation built around the mailbox."),
    "27": (1.0, "In January 2005, it made a major change. It stopped charging late fees at its company-operated stores in the United States."),
    "28": (1.0, "The company's annual report for 2005 describes the financial impact of that decision, line by line."),
    "29": (1.0, "Rental revenue fell, and the company reported about sixty million dollars in initial marketing and implementation costs. Lost revenue, though, is not the same as lost profit."),
    "30": (1.0, "In November 2006, Blockbuster introduced Total Access, its most direct answer yet to the mail-order challenge."),
    "31": (1.0, "Online members could return a mailed disc at a store and leave with another film. For the first time, the two systems connected."),
    "32": (1.0, "Subscribers grew quickly. So did the cost of serving them, and of the promotions that brought them in."),
    "33": (1.0, "Growth came with losses. Attracting customers is not the same thing as making each of them profitable."),
    "34": (1.0, "Retail stores. Discs by mail. Each with its own costs, its own customers, and soon, a third model that needed neither."),
    "35": (1.0, "In January 2007, Netflix announced instant viewing on personal computers, starting with about a thousand titles."),
    "36": (1.0, "It was limited at first. But it pointed toward a way of watching that needed neither a store nor an envelope."),
    "37": (1.0, "Discs by mail, retail stores and streaming were now competing for the very same evenings at home."),
    "38": (1.0, "Running a transition is expensive, and the cost fell on a business whose core revenue was already under pressure."),
    "39": (1.0, "Debt, liquidity and other long-term obligations left the company with less and less room to maneuver, and less time to adjust."),
    "40": (1.0, "The network that had been the company's greatest strength became harder and harder to sustain."),
    "41": (1.0, "On September twenty-third, 2010, Blockbuster filed for Chapter Eleven bankruptcy protection, a decade after the meeting in Dallas."),
    "42": (1.0, "Some stores continued to operate. But the dominant model of the neighborhood video store had faded."),
    "43": (1.5, "Which brings us back to the meeting in Dallas. A famous moment, and still a disputed one."),
    "44": (1.0, "Could an earlier deal, different terms, or a partnership have changed the outcome? Possibly. None of these outcomes can be proven."),
    "45": (1.0, "The record points to something more complex: legacy economics, the cost of transition, and financial constraints, arriving together."),
    "46": (1.0, "One meeting is part of the evidence. It is not the whole record, and it was never the whole story."),
    "47": (2.0, "Recognizing change is not the same as surviving it."),
    "48": (4.0, "Every decision leaves evidence."),
}
NARRATION_PENDING = {"06": "SRC_ANTIOCO_DISPUTE", "13": "SRC_STORES_2004", "19": "SRC_NFLX_NO_LATE_FEES", "23": "SRC_SCALE_2000",
                     "25": "SRC_BB_ONLINE_2004"}
PRONUNCIATION = {"06": "Antioco: an-tee-OH-koh.", "28": "10-K: 'ten-K'.", "41": "Chapter 11: 'Chapter Eleven'.",
                 "05": "Randolph: RAN-dolf.", "01": "Dallas: DAL-us."}
WORDS_PER_SECOND = 2.5               # calm documentary delivery (150 wpm)
BREATH_S = 0.35                      # minimum pause between consecutive lines


def tc(frame):
    s = (frame - 1) / FPS
    return f"{int(s // 60):02d}:{int(s % 60):02d}"


def shots():
    """The authoritative manifest (computed, so timing can never drift from the 240-frame rule).
    Narration is one continuous track: a line starts after its shot's lead silence and at least BREATH_S after the previous
    line ends; a line may run across the next cut (recorded as carries_over_cut)."""
    out = []
    prev_end = 0.0
    for i, (sid, title, caption, mode, env, cls, srcs) in enumerate(_S):
        start = i * SHOT_FRAMES + 1
        end = start + SHOT_FRAMES - 1
        act = ACTS[i // SHOTS_PER_ACT]
        lead, text = NARRATION[sid]
        words = len(text.split())
        dur = words / WORDS_PER_SECOND
        n_start = max((start - 1) / FPS + lead, prev_end + BREATH_S)
        n_end = n_start + dur
        prev_end = n_end
        out.append(dict(
            shot_id=f"S{sid}", index=i + 1, act_id=act[0], act_title=act[1], title=title, caption=caption,
            frame_start=start, frame_end=end, frames=SHOT_FRAMES, timecode=f"{tc(start)}-{tc(end + 1)}",
            visual_mode=mode, environment=env, classification=cls,
            reconstruction=cls == "reconstruction", source_ids=srcs,
            camera=f"CAM_S{sid}",
            narration=dict(text=text, words=words, start_s=round(n_start, 2), end_s=round(n_end, 2),
                           lead_silence_s=round(n_start - (start - 1) / FPS, 2),
                           tail_silence_s=round(max(0.0, (end / FPS) - n_end), 2),
                           carries_over_cut=n_end > end / FPS, carry_s=round(max(0.0, n_end - end / FPS), 2),
                           pending_source=NARRATION_PENDING.get(sid), pronunciation=PRONUNCIATION.get(sid, "")),
            render_status="not_rendered", continuity="not_validated"))
    return out


SHOTS = shots()

AUDIO_CUES = [  # id, shot, offset_s, duration_s, category, description
    ("AMB_DALLAS_DUSK", "S01", 0.0, 20.0, "ambience", "Distant downtown traffic, light wind, no identifiable signage audio"),
    ("SFX_FOOTSTEPS_PLAZA", "S02", 1.0, 8.0, "sfx", "Three sets of leather-soled steps on stone, then glass door"),
    ("AMB_ROOM_TONE_BOARDROOM", "S03", 0.0, 20.0, "ambience", "HVAC room tone, muted"),
    ("SFX_FOLDER_CONTACT", "S04", 6.0, 1.0, "sfx", "Plain card folder set down on wood"),
    ("MUS_MOTIF_EVIDENCE", "S05", 0.0, 40.0, "music", "Original motif A: low piano + bowed bass (cleared original score)"),
    ("SFX_PAPER_SLIDE", "S08", 2.0, 2.0, "sfx", "Two cards sliding on the light table"),
    ("AMB_RETAIL_STORE", "S09", 0.0, 30.0, "ambience", "Busy store murmur, period-neutral (no copyrighted music bed)"),
    ("SFX_VHS_DVD_HANDLING", "S11", 2.0, 6.0, "sfx", "Cases on counter, card swipe, receipt printer"),
    ("MUS_MOTIF_SCALE", "S12", 0.0, 30.0, "music", "Motif B: pulsing strings, building"),
    ("SFX_ENVELOPE", "S17", 3.0, 2.0, "sfx", "Disc into paper mailer, seal"),
    ("AMB_SORTING_MACHINERY", "S18", 0.0, 10.0, "ambience", "Conveyor rollers, sorter clacks"),
    ("AMB_COMPUTER_QUIET", "S22", 0.0, 10.0, "ambience", "CRT whine, fan hum, keyboard"),
    ("MUS_SILENCE_QUESTION", "S24", 0.0, 10.0, "music", "Music drops to near silence"),
    ("SFX_PAPER_HANDLING", "S28", 1.0, 4.0, "sfx", "Filing pages turned"),
    ("MUS_MOTIF_PRESSURE", "S29", 0.0, 80.0, "music", "Motif C: tightening ostinato"),
    ("AMB_COMPUTER_HOME", "S36", 0.0, 10.0, "ambience", "Home room tone, PC fan"),
    ("AMB_STORE_EMPTY", "S42", 0.0, 10.0, "ambience", "Fluorescent hum, empty room"),
    ("MUS_MOTIF_EVIDENCE_REPRISE", "S43", 0.0, 40.0, "music", "Motif A reprise"),
    ("MUS_STING_FINAL", "S47", 7.5, 2.5, "music", "Final investigative sting (original)"),
    ("MUS_END_TITLE", "S48", 0.0, 10.0, "music", "End-title tail, fades to silence"),
]


def write_metadata():
    for f in FOLDERS:
        os.makedirs(os.path.join(ROOT, f), exist_ok=True)
    with open(os.path.join(P["metadata"], "shot_manifest.json"), "w") as fh:
        json.dump(dict(project="BRAND CORONER", case="CASE 001: BLOCKBUSTER", film="THE $50 MILLION DECISION", fps=FPS,
                       total_frames=TOTAL_FRAMES, total_seconds=TOTAL_SECONDS, resolution_final=RES_FINAL,
                       shot_frames=SHOT_FRAMES, acts=[dict(id=a, title=t, logline=l) for a, t, l in ACTS], shots=SHOTS), fh, indent=2)
    with open(os.path.join(P["metadata"], "evidence_register.json"), "w") as fh:
        json.dump(dict(rule="A figure renders as final only when its source status is verified_primary or verified_secondary; "
                            "otherwise graphics carry a PENDING tag.", sources=EVIDENCE), fh, indent=2)
    with open(os.path.join(P["metadata"], "audio_cue_manifest.json"), "w") as fh:
        json.dump([dict(id=c[0], shot=c[1], offset_s=c[2], duration_s=c[3], category=c[4], description=c[5],
                        timeline_s=round((int(c[1][1:]) - 1) * SHOT_FRAMES / FPS + c[2], 2), status="placeholder")
                   for c in AUDIO_CUES], fh, indent=2)


if __name__ == "__main__":
    write_metadata()
    w = sum(s["narration"]["words"] for s in SHOTS)
    carry = [(s["shot_id"], s["narration"]["carry_s"]) for s in SHOTS if s["narration"]["carries_over_cut"]]
    late = [s["shot_id"] for s in SHOTS if s["narration"]["start_s"] > s["frame_end"] / FPS - 2.0]
    last = SHOTS[-1]["narration"]["end_s"]
    assert not late, f"lines that start too late in their shot: {late}"
    assert last <= TOTAL_SECONDS - 2.0, f"narration overruns the film: {last}"
    print(f"PHASE 1 OK: {len(SHOTS)} shots, {TOTAL_FRAMES} frames, {TOTAL_SECONDS:.0f} s, narration {w} words "
          f"({w / TOTAL_SECONDS * 60:.0f} wpm overall), ends at {last:.1f} s; lines carried over a cut: {carry}")
