# BRAND CORONER · CASE 001: BLOCKBUSTER · *The $50 Million Decision*

An editable, eight-minute documentary animatic built entirely from Blender Python: 48 shots × 240 frames = 11,520 frames = 480.0 s at 24 fps (master format 3840×2160, 16:9, AgX).

## What is verified and what is not

- **Executed:** every script in `scripts/` ran headless in Blender 5.2.3 LTS on Linux (CPU only) and produced the files listed below.
- **Animatic quality:** the low-resolution animatic is a Workbench playblast.
- **Validation stills:** rendered in Eevee at 960×540.
- **Not rendered:** the 4K final.
- **Previs only:** the human figures are neutral, faceless stand-ins.
- **Not invented:**
  - No logos, signage, likenesses or document scans are invented. Those slots are labelled and listed as `pending` in `metadata/asset_register.json`.
  - Narration is a script with an SRT timing track; no voice was recorded.
- **Sources:** each factual figure carries the verification status recorded in `metadata/evidence_register.json`. Figures not yet confirmed against a primary source show a **PENDING VERIFICATION** tag on screen, and the matching narration lines are flagged in the script.

## Build order (each phase saves a checkpoint)

```bash
python3 scripts/config.py
```
Phase 1: folders, `shot_manifest.json`, `evidence_register.json`, `audio_cue_manifest.json`.

```bash
blender -b --factory-startup --python scripts/environments.py -- --render-check
```
Phase 2: `scenes/BC001_LOC_{BOARDROOM,STORE,WAREHOUSE,ARCHIVE}.blend`, plus a validation render.

```bash
blender -b --factory-startup --python scripts/shot_builder.py
```
Phases 3–7: `scenes/BC001_MASTER.blend`. This links the location files (relative paths), builds the Dallas, desk and graphics sets and all 48 shots, then the timeline, narration markers and VSE audio placeholders.

```bash
blender -b scenes/BC001_MASTER.blend --python scripts/render.py -- --stills --samples 12
```
Phase 8: one still per shot in `renders/shots/`.

```bash
blender -b scenes/BC001_MASTER.blend --python scripts/render.py -- --animatic
```
Phase 9: Workbench animatic frames, 640×360.

```bash
python3 scripts/render.py --assemble
```
Writes `delivery/BC001_ANIMATIC_640x360_24fps.mp4`, plus a copy with the narration as a subtitle track.

```bash
blender -b scenes/BC001_MASTER.blend --python scripts/validate.py
```
Phase 10: `metadata/continuity_report.json` and `asset_register.json`, plus manifest status.

```bash
python3 scripts/report.py
```
Writes the delivery reports.

```bash
python3 scripts/contact_sheets.py
```
Writes the per-act contact sheets.

To rebuild only some shots, use `shot_builder.py -- --shots 4,43` (a partial master for debugging).

## Final render (documented, not run here)

```bash
blender -b scenes/BC001_MASTER.blend --python scripts/render.py -- --final --frames 1-240
```

- **Format:** Eevee, 3840×2160, 64 samples, motion blur 0.5 (180°), AgX, 16-bit PNG to `renders/final/`.
- **Distribution:** split by shot ranges across machines. Every shot starts at frame 240·(n−1)+1.
- **Cycles hero frames:** add `--cycles` (512 samples).
- **Media handling:** the VSE contains placeholders only (`render.use_sequencer = False`). Conform picture and audio in your editor using `audio/narration/BC001_narration_timing.srt` and `metadata/audio_cue_manifest.json`.

## Layout

```
scripts/     config, assets, environments, camera_rigs, motion_graphics, shot_builder, timeline, render, validate, report, contact_sheets
scenes/      BC001_MASTER.blend + four reusable location files (linked, relative paths)
metadata/    shot_manifest.json, evidence_register.json, asset_register.json, continuity_report.json, audio_cue_manifest.json
audio/       narration script (Markdown) + SRT timing; music/sfx placeholders (cue manifest)
renders/     shots/ (48 validation stills), previews/ (contact sheets)
delivery/    animatic MP4s, camera & continuity report, source & asset register
assets/      fonts_reference_only/ (Inter, SIL OFL 1.1)
```
