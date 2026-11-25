# QC report: Brand Coroner · Case 011 · Juicero, "the $120 million juicer disaster"

| Check | Result |
|---|---|
| Scenes | ✅ All 16 scenes, in order; `juicero.blend` has one meta strip per scene. No scene labels or timestamps on screen |
| Narration | ✅ Voiced verbatim: 113 lines, 1,291 words. Each line was checked with Whisper (small.en). Three lines re-voiced (S01·04, S02·06, S11·06); S02·06 now transcribes exactly. Remaining differences are number formatting ("$400", "43%"), the recognizer's spellings of "Juicero" ("Juicier O", "JU-SAR-O"), and "squeezed the" heard as "squeeze the" |
| Runtime | **10:28 (627.8 s), 15,067 frames.** The 1,291-word script is read at a natural pace and was not sped up or cut. An 8:00 cut would need about 990 words |
| Facts | ✅ See `FACTS.md`. Bloomberg (Apr 2017: about $120M raised, $400 machine, squeeze test 7.5 oz / ~90 s by hand vs 8 oz / ~2 min by machine, QR check, Doug Evans; Apr 21: Dunn's defense and 30-day refund; Sep 1: suspension, 90-day refunds, investors GV, Kleiner Perkins, Artis, Thrive); Fortune (Jan 17, 2017 price cut $699 → $399, "spring of 2016" launch; Jul 14 CEO letter and ~25% layoffs; Sep 1 shutdown); FoodNavigator-USA ($5–7 packs, shutdown letter, Crunchbase $118.5M incl. Campbell Soup); Ars Technica ("over a million Produce Packs", teardown, under-$200 plan); SELF (Dunn quote) |
| Figures | ✅ Funding shown as capital raised, not money lost; no single investor credited with $120M. The squeeze test is labelled one reported demonstration, with bars to scale. 42.9% is shown with its calculation. The sub-$200 press is labelled a plan that never launched. No manufacturing cost is shown. The hand-squeezing experiment and the company's stated reasons for closure are shown separately |
| Documents | ✅ Reporting and company statements appear on cards labelled "not a facsimile" |
| Storyboard items not used | No Bloomberg footage or thumbnails, no Juicero advertising, product photos or logos, no original teardown images (copyrighted). No photos of Doug Evans or Jeff Dunn with a usable licence. Flow diagrams (packet → press → glass; pack scanning; supply chain) labelled illustrative |
| Picture | 3840×2160 and 1920×1080, 24 fps, Rec.709, H.264; no burned-in subtitles. Frames from all 16 scenes reviewed on the voice-timed edit; fixed a photo credit running under a card (Scene 2) and spacing around cards (Scenes 5, 12). Contact sheet of the 1080p master: `qc/final_sheet.jpg` |
| Sound | 48 kHz stereo, −16.0 LUFS integrated; narration first, music ducked under voice |
| Subtitles | `BRAND_CORONER_CASE011_JUICERO_EN.srt`, 158 cues, ≤ 2 rows × 46 characters, the script's own wording |
| Licences | 3 photos from Wikimedia Commons, credited on screen and in `CREDITS.md`: 1 CC BY (disassembled Juicero Press, Steve Jurvetson), 2 CC BY-SA (Sand Hill Road, generic produce) shown unaltered on a dark mat. Music samples: Salamander Grand Piano (CC BY 3.0), VSCO 2 CE and VCSL (CC0) |
| Deliverables | 4K and 1080p masters, SRT, narration/music/foley stems, 16 per-scene segments. The 4K master is 38 MB, so the repo holds it as rendered; stems are stored as FLAC |
