# Brand Coroner · Case 001 · "Blockbuster: The $50 Million Decision" (Visual Investigation)

The Brand Coroner Blockbuster film, rebuilt in the **Visual Investigation** style (`styles/visual-investigation/STYLE.md`).

- **Format:** 8:00, 1920×1080, 30 fps. English narration with one-line English subtitles.
- **Look:** a cold investigation desk, dark ground. Every source is greyscale, and one red (`#FF4A2E`) only ever points.
- **Sources:** SEC filings, re-typeset as labelled transcriptions; licensed Wikimedia Commons photographs; and data from the filings. These are pinned to one clock that changes scale: decade → years → months → a single day.

## Structure

| Time | Section | Layouts and native moves |
|---|---|---|
| 0–4 | Cold open | The 2010 filing and a closing store freeze first; evidence slams into a 2×2 grid; sync line; the date rewinds 2010 → 2000 |
| 4–10.5 | Title | Dallas photo, title, lower third (Dallas, Texas · SEP 2000) |
| 10.5–30 | Place / record | The 10-K address (1201 Elm St) meets a photo of the tower; then an on-record vs not-on-record board |
| 30–80 | Two accounts | Randolph (2019) and Antioco (2022) on one time axis, both pointing at SEP 2000; the $50,000,000 readout in a dashed "recalled" box; an "unresolved" board |
| 80–130 | The store | Photos with freeze, circle and label; the transaction steps; ≈9,100 stores as dots, with the 10-K line highlighted |
| 130–160 | Late fees | ≈14%, the fee table and 100 cells; revenue 2000–2004 with a playhead |
| 160–240 | Challenger | Mailer photo; mail route, subscription loop and order queue (schematics); revenue in 2000 as squares ($4,960.1M vs $35.9M); the question |
| 240–330 | Counterattack | Filings land on a clock (AUG 2004 → APR 2007) with a red playhead; the Addison "life after late fees" window ✓ the Jan 2005 filing; two quantities that are not addable; **hard sync point**: Blockbuster and Netflix subscriber counts at the same quarter-ends |
| 330–370 | Third model | Stores / mail / streaming; 16 Jan 2007 |
| 370–400 | Squeeze | Transition costs; debt (Ex. 99.1); two store counts on different bases, kept apart |
| 400–420 | Filing | 8-K Item 1.03 + a closing store; "all 3,000 … will remain open" + two later stores |
| 420–450 | Back to Dallas | Disputed accounts; hypotheticals (dashed, unproven); what the record shows (✓ with sources) |
| 450–462 | Evidence map | The decade, every source pinned to its date |
| 462–480 | Verdict and end card | Credits in full |

## Build

```
python3 tools/build_film.py            # audio/words.json → film.json (sections, voice times, subtitle cues)
.venv/bin/python audio/mix.py          # score + Foley + narration → out/mix.wav, out/stems/
node core/render/video.mjs films/blockbuster-visual-investigation --fps 30 --workers 4 --out films/blockbuster-visual-investigation/out/video.mp4
sh core/render/mux.sh out/video.mp4 out/mix.wav blockbuster-visual-investigation.mp4 30 0
```

- **Narration:** the voiced lines of the earlier Brand Coroner cut (`../brand-coroner-blockbuster/out/voice`). `tools/words.py` produced the word timings.
- **Photos:** in `raw/` with licences in `SOURCES.jsonl` / `CREDITS.md`, and `assets/` holds the resized copies.
- **Facts:** `FACTS.md`.
