# QC report: Brand Coroner · Case 006 · Nokia, "the empire that missed the future"

| Check | Result |
|---|---|
| Scenes | ✅ All 16 storyboard scenes, in order; `nokia.blend` has one meta strip per scene |
| Narration | ✅ Voiced verbatim: 134 lines, 1,256 words. Each line was checked with Whisper (small.en). Six lines were re-voiced after the voice slipped ("Bet" for "That", "make" for "made" and similar). All now match; the only remaining differences are number formatting and the names "MeeGo" and "Elop" |
| Runtime | **11:12 (671.9 s), 16,125 frames.** The script runs 1,256 words at a natural pace and was not sped up or cut. An 8:00 cut would need about 950–1,000 words |
| Facts | ✅ See `FACTS.md`. Every date and figure is sourced to Nokia's Forms 20-F (2007, 2011, 2012), Nokia and Microsoft releases (Feb 11, 2011; Sept 3, 2013; Apr 25, 2014) and Nokia's Sept 2010 CEO release |
| Figures | ✅ €5.44B is shown split as €3.79B (business) + €1.65B (patent licence and future option). Scene 13 shares (38/32/27/21%, 2007–2012) label their estimators. Scene 11 shows reported smartphone shipments (77.3M in 2011, about 35M in 2012) |
| Documents | ✅ Filing and release text appears on cards labelled "transcription · not a facsimile". No fabricated documents |
| Storyboard figures not used | Scene 13's "38% / 16% / 3%" smartphone-share chart (mixes all-phone and smartphone shares; unverified as labelled) and Scene 11's Symbian-only sales chart (not reported by Nokia). No logos or handshake image reproduced |
| Balance | ✅ The narration's "not one phone, not one competitor, not one executive decision" framing is kept; Scene 09 presents the Android and own-platform options alongside the Microsoft choice |
| Picture | 3840×2160 and 1920×1080, 24 fps, Rec.709, H.264; no burned-in subtitles |
| Sound | 48 kHz stereo, −16 LUFS integrated; narration first, music ducked under voice |
| Subtitles | `BRAND_CORONER_CASE006_NOKIA_EN.srt`, 163 cues, ≤ 2 rows × 45 characters, written forms ("2007", "€5.44 billion") |
| Licences | 10 dated Wikimedia Commons photos, credited on screen and in `CREDITS.md`. CC BY-SA photos (E71, Espoo HQ, N9, 5800) are shown unaltered: fitted on a dark mat with no crop or grade |
| Deliverables | 4K and 1080p masters, SRT, narration/music/foley stems, 16 per-scene segments. The repo copy of the 4K is re-encoded at CRF 27 to stay under GitHub's 100 MB limit; stems are stored as FLAC |
