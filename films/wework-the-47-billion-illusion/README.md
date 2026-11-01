# Brand Coroner · Case 002 · WeWork: "the $47 billion illusion"

An 8-minute silent documentary animatic in the Visual Investigation identity, built and rendered in Blender.

- **Format:** 1920×1080, 24 fps, 11,520 frames, H.264, Rec.709.
- **Palette:** #080808 ground, #FF2400 accent, #F5F3EF type, #858585 grey.
- **Type:** lowercase Outfit; IBM Plex Mono for sources.

## Files

| Path | Contents |
|---|---|
| `brand-coroner-case002-wework.mp4` | The animatic |
| `project/wework.blend` | Editable Blender 4.2 project. Master timeline with 16 scene meta strips (S01–S16), 48 narration markers, a vignette, the fade to black and the sound strip |
| `project/build.py` | Builds the .blend from scratch: `blender -b -P build.py` |
| `project/render_chunk.py` | Renders a frame range, e.g. `blender -b wework.blend -P render_chunk.py -- 1 2880 out/chunk0.mp4` |
| `project/tools/prep_assets.py` | Graded photos, the real petition page, typeset filing transcriptions with measured highlight boxes, the map and graphics |
| `project/audio/mix.py` | Restrained underscore and Foley, cued from `events.json` |
| `narration-markers.srt` | Beat markers for recording narration later |
| `FACTS.md` | Sources for every on-screen claim |
| `CREDITS.md` | Photo, document and font credits |
| `QC-report.md` | Technical checks and departures from the brief |
| `qc/` | 48 stills and the contact sheet |

## Structure

16 scenes × 30 s, six acts: the valuation · the promise · the machine · the documents speak · the break · the reckoning.
