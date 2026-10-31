# QC report: Brand Coroner · Case 001 · Blockbuster (1080p cut)

## Technical checks

| Check | Target | Result |
|---|---|---|
| Duration | 8:00 | 480.000 s ✅ |
| Frames | 11,520 at 24 fps | 11,520 ✅ (6 acts × 1,920, each verified at render time) |
| Structure | 6 acts × 8 shots × 10 s | 48 shots, 240 frames each ✅ (`qc/manifest.json`, `qc/shot-list.md`) |
| Resolution | 1080p first, 4K on approval | 1920×1080, H.264 High, CRF 18 master ✅ |
| Loudness | −14 LUFS integrated | −14.1 LUFS, LRA 4.2 LU, true peak ≤ −1.2 dBTP (two-pass loudnorm) ✅ |
| Audio | Narration, original score, Foley | Three stems in `stems/` (narration, music, Foley); music ducks −9 dB and Foley −4 dB under the voice |
| Subtitles | Narration as subtitles | `subs.srt`, timed to the final placement |

## Validation stills

`qc/stills/shotNN.jpg` holds one frame from 6 s into every shot, and `qc/contact-sheet.jpg` puts all 48 on one sheet. Each still was checked for these points:

- Every evidence shot carries its classification chip (ARCHIVAL MATERIAL, RECONSTRUCTION, EDITORIAL GRAPHIC or HYPOTHETICAL SCENARIO) and a source line.
- Date titles appear where the script calls for them: Sept 2000, Aug 2004, Jan 2005, Nov 2006, Jan 2007 and 23 Sept 2010.
- No company logo, store sign, mailer design or interface is recreated. The store sign reads "VIDEO", and the mailer and web page are labelled representative.
- No portraits or likenesses: every figure is an anonymous model figure, and Antioco is never depicted.
- Randolph's account (shot 5) and Antioco's (shot 6) sit on separate, separately sourced cards. Randolph's "struggling not to laugh" line is not used.
- Each figure matches the evidence register: ≈9,100 stores, $622.4M extended viewing fees, >$500M revenue effect vs ~$60M expense ("not addable"), ≈2.2M / ≈3M subscribers, the $46.4M company-wide net loss, and the 8-K Item 1.03 wording.

## Narration

All 48 lines were re-voiced from the Kokoro `am_michael` timbre with Chatterbox and checked by Whisper ASR. Two lines needed attention:

- **s44:** "Possibly." was dropped in an earlier take and has been re-taken.
- **s42:** "continued to" comes out as a natural elision. Accepted.

Some lines run past their 10 s shot into the next one. This is deliberate, so the narrator keeps a calm pace instead of being cut:

| Line | Overrun |
|---|---|
| s01 | 1.2 s |
| s02 | 1.0 s |
| s06 | 2.7 s |
| s07 | 1.6 s |
| s21 | 1.0 s |
| s29 | 0.3 s |

## Corrections to the brief (sourced, see `qc/evidence-register.md`)

- **Total Access subscribers:** "approximately 3 million", not "more than 3 million" (Q1 2007 results release).
- **Extended viewing fees:** the $552.1M + $70.3M split comes from the FY2005 10-K, not the 2004 annual report.
- **Antioco's account:** sourced to his 2022 LinkedIn post as reported by *Next TV*. The original post was not retrieved.

## Departures from the brief

- **Renderer:** the film is rendered in three.js, not Blender/Cycles, because the container has no GPU and no Blender.
- **Reconstructions:** forensic miniatures with anonymous figures (client choice).
- **Resolution:** 1080p first; the 4K pass (3840×2160) follows on approval from the same source.
