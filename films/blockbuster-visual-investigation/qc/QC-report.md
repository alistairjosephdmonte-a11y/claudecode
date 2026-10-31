# QC report: Blockbuster · Visual Investigation cut

## Technical checks

| Check | Result |
|---|---|
| Duration | 480.000 s (8:00) ✅ |
| Frames | 14,400 at 30 fps, 1920×1080 ✅ |
| Loudness | −14.0 LUFS integrated, LRA 3.6 LU, peak −1.5 dBFS ✅ |
| Subtitles | 134 one-line English cues (`blockbuster-visual-investigation.srt`), ≤ 62 characters, burned in at y ≈ 1004 |
| Share copy | `blockbuster-visual-investigation.mp4` here is a two-pass ≈1.45 Mb/s encode (96 MB). The 246 MB master (CRF 18) stays in the build folder |

## Style compliance (`styles/visual-investigation/STYLE.md`)

- **Palette:** ground #0B0C0E, panels #141619, one red #FF4A2E used only to point (circles, highlights, playhead, sync line, unresolved items), paper cards #E4E0D4.
- **Sources:** greyscale with one grade and one grain. Grain is applied to sources only, never to type, and the master was muxed with grain 0.
- **Three kinds of source:** documents (SEC filings, re-typeset and labelled TRANSCRIPTION), photographs (Wikimedia Commons, licences in `CREDITS.md`) and data (revenues, store counts, subscribers).
  - **Departure:** no licensable moving image of Blockbuster exists (no public-domain or CC BY footage was found), so the film cross-checks documents, photos and data instead. The style allows this in its "one licensable source" pitfall.
- **One clock in the picture:** a date readout and playhead at every section. The scale changes from decade to years to months to a single day.
- **Hard sync point (310–320):** Blockbuster's and Netflix's subscriber counts at the same quarter-ends, joined by a red dashed line.
- **Native moves:**
  - rewind cold open;
  - freeze, circle and label on photos;
  - filings landing on the clock;
  - data chart with a playhead;
  - dots for stores;
  - then-vs-record (the two accounts);
  - known vs unresolved;
  - hypotheticals drawn dashed;
  - evidence map.
- **Uncertainty:**
  - disputed accounts are labelled;
  - "$50,000,000" sits in a dashed "recalled · no signed or documented offer" box;
  - schematics are labelled SCHEMATIC;
  - the 2004 and 2010 store counts are kept apart as "different bases".
- **Cuts:** hard cuts with white flashes; no dissolves or flying elements.
- **Credits:** every CC BY photographer is credited on the end card.

## Narration

The voice is the existing Brand Coroner narration (48 lines, Whisper-checked). For line s03, the clause "The room you are seeing is representative, and" is silenced in the mix, because this cut shows no room. Subtitles match the edited line.

## Stills

`qc/stills/` holds 49 frames sampled across the film, and `qc/contact-sheet.jpg` shows them all.
