# QC report: Brand Coroner · Case 002 · WeWork, "the $47 billion illusion"

## Technical checks

| Check | Result |
|---|---|
| Duration | 480.000 s (8:00) ✅ |
| Frames | 11,520 at 24 fps (4 render chunks × 2,880, each verified) ✅ |
| Format | 1920×1080, 16:9, H.264 MP4, Rec.709 SDR (bt709 primaries, transfer and matrix; tv range) ✅ |
| Audio | AAC 192k, −16.0 LUFS integrated (restrained underscore and Foley; no narration) |
| Project | `wework.blend` (Blender 4.2 LTS). 16 meta strips S01–S16 hold 627 editable strips: text, colour, image and sound. Asset paths are relative |
| Narration markers | 48 timeline markers (N01.1–N16.3), shown on screen bottom-left and exported to `narration-markers.srt` |

## Visual tests

A 48-frame test pass found and fixed four problems:
1. The highlight blend mode darkened whole frames. It was replaced with a red tint plus a solid underline.
2. Scene 09's bars overlapped the S-1 table. Their timing was fixed.
3. Scene 11's timeline labels collided. They were respaced.
4. Scene 15's closing lines overlapped the documents. The layout was cleared.

Also, the Neumann photo is cropped so it shows only him. A final 48-frame contact sheet is in `qc/contact-sheet.jpg`.

## Departures and corrections (see FACTS.md)

- **No script or voice supplied:** this is a silent animatic with narration markers, as the brief specifies. No voice was invented.
- **2018 net loss:** the brief's "$1.61 billion" is the net loss *attributable to WeWork Companies Inc.* The total net loss was $1.93 billion. Both are shown and labelled.
- **Lease mismatch timelines:** these use real S-1 figures (member commitments "more than 15 months"; average initial U.S. lease term "approximately 15 years"), drawn to scale, not illustrative durations.
- **$462 million:** verified as cash and cash equivalents at 30 Sep 2023, reported in the Nov 2023 8-K (Ex. 99.1). The June 30, 2023 figure of $205 million from the going-concern 10-Q is shown alongside it.
- **SEC filings:** shown as labelled transcriptions, because EDGAR blocks automated page capture. The Chapter 11 petition is the real court document.
- **Photography:** no licensable early-era (2010–2014) WeWork interiors were found. Interiors are from 2016–2018 and tagged with their dates. The pandemic offices (Vienna, 2020) are generic context, labelled as such. The map plots only the verified first location plus the cities shown in the photos.
- **Renderer:** Blender VSE 2D compositing (flat orthographic-style editorial compositions with keyframed push-ins and wipes), not 3D scenes. No 3D objects or people.
- **Not shown:** the 2019 S-1/A vote change and the trademark unwind are shown as changes. No percentage decline is computed between the 2019 valuation and the 2021 enterprise value.
