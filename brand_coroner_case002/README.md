# BRAND CORONER · CASE 002: WEWORK · *The $47 Billion Illusion*

An eight-minute documentary visual animatic built entirely with Blender Python. It is exactly 16 scene sequences × 720 frames = 11,520 frames = 480.0 s at 24 fps, 1920×1080, 16:9, Rec.709 SDR.

## What is authentic and what is a placeholder

- **Documents:** every document on screen is the real filing.
  - The SEC filings come from EDGAR and the SoftBank release from group.softbank. They are stored in `evidence/sec_filings/` (run `scripts/fetch_sources.py`).
  - Each one was rendered from the filed HTML by Chromium (`scripts/capture_documents.js`) into `evidence/document_crops/`. Nothing is retyped or recreated.
  - The red highlights sit on the exact phrase rectangles recorded during capture.
- **Figures:** every number was checked against those filings. See `delivery/BC002_fact_check.md`, which also lists where the brief and the filings differ.
- **Reported figure:** the $47 billion private valuation has no primary document in this pack, so it carries a red **reported** tag on screen.
- **Photography:** no photograph, likeness, logo or interior is generated or simulated.
  - The nine slots that need licensed or authenticated photography (P01–P09) are clearly marked placeholders that state the exact asset required.
  - The full list is in `delivery/BC002_source_and_asset_register.md`.
- **Narration:** the WeWork master script was not supplied. The animatic is silent apart from a temporary sound bed, with one narration marker per beat (the topic only, no invented lines).
  - The markers are in the VSE and in `delivery/BC002_narration_markers.srt`.
- **Sound:** `audio/BC002_temp_sound_design.wav` is synthesized from sine waves and noise in `scripts/sound_design.py`. It contains no samples, music or voice.

## Build and render

```bash
python3 scripts/fetch_sources.py
```
Downloads the primary sources into `evidence/sec_filings/`.

```bash
node scripts/capture_documents.js
```
Renders the authentic document crops and their phrase rectangles.

```bash
python3 scripts/config.py
```
Writes the scene manifest and the source and placeholder registers.

```bash
blender -b --factory-startup --python scripts/build.py
```
Builds `scenes/BC002_WEWORK.blend`: SC01–SC16 plus the BC002_EDIT VSE.

```bash
python3 scripts/sound_design.py
```
Generates the temporary sound bed. Re-run `build.py` afterwards so the VSE picks up the audio.

```bash
blender -b scenes/BC002_WEWORK.blend --python scripts/camera_check.py
```
Checks camera smoothness for every scene.

```bash
blender -b scenes/BC002_WEWORK.blend --python scripts/render.py -- --test
```
Renders one test still per beat into `renders/tests`.

```bash
blender -b scenes/BC002_WEWORK.blend --python scripts/render.py -- --frames 1-11520
```
Renders the PNG frames through the VSE. Split the range across processes or machines to go faster.

```bash
python3 scripts/frame_check.py
```
Checks for missing frames, jumps and unexpected black frames.

```bash
python3 scripts/render.py --assemble
```
Writes `delivery/BC002_WEWORK_ANIMATIC_1920x1080_24fps.mp4` (H.264, BT.709, AAC).

```bash
python3 scripts/contact_sheet.py
```
Writes `delivery/BC002_contact_sheet.png`.

```bash
python3 scripts/report.py
```
Writes the fact check, the registers, the narration markers and the edit report.

## Layout

```
scripts/    config (scenes, sources, facts), toolkit (2D motion-design helpers), scenes (16 scene builders), build, render,
            camera_check, frame_check, sound_design, contact_sheet, report, fetch_sources, capture_documents.js
scenes/     BC002_WEWORK.blend: SC01–SC16 (one orthographic camera each) + BC002_EDIT (VSE timeline)
evidence/   sec_filings/ (downloaded, not committed), document_crops/ (rendered filing excerpts), map/ (Natural Earth)
metadata/   scene_manifest, source_register, placeholder_register, document_crops, build_log, camera_check, frame_check, audio_cues
delivery/   animatic MP4, contact sheet, fact check, source and asset register, narration markers, edit and render report
```

## Look

- **Palette:** background #080808, accent #FF2400, type #F5F3EF, secondary #858585.
- **Typography:** Inter Display / Inter, bold and lowercase.
- **Camera:** orthographic only. Moves are limited to slow push-ins, pull-outs, horizontal tracking and document moves, and each one lands on a highlighted fact.
- **Smoothness:** measured per frame in `metadata/camera_check.json`.
