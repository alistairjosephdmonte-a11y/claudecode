# AMUL: OVER THE MOO · EPISODE 01: THE CALLING

A 30-second Blender Cycles cinematic. It is exactly 720 frames at 24 fps, 16:9.

MOO_01 is a 2D illustrated calf composited into a photographic sunrise dairy farm. The artwork is layered cutout planes on a rig, with an invisible 3D stand-in body that casts MOO's shadows.

## What was delivered, and what was not

**Rendered:**
- The complete 720-frame film in Cycles at 1280×720, 10 samples plus OpenImageDenoise, with 180° motion blur.
- 4K (3840×2160) Cycles hero stills.
- Delivery files: `delivery/AMUL_OTM_EP01_ANIMATIC_1280x720_24fps_{TEMPMIX,CLEAN}.mp4`, plus `renders/stills/`.

**Not rendered:**
- **The 4K master.** These 4 CPU cores, with no GPU, need about 9 minutes per 4K frame. The full master would take about 4–5 days, so it was not run.
- The command for it is below. The project already holds the 4K settings, render layers and passes.

**Stand-in artwork:**
- The approved MOO_01 master character sheet and the ten-frame storyboard were not supplied.
- MOO_01 was drawn from the written spec: `scripts/art.py` produces `art/moo_01/` and `delivery/MOO_01_character_sheet_STANDIN.png`.
- To swap in the approved artwork, replace the PNGs (same part names and pivots), then run `build.py`.

**Vocals:**
- No voice was synthesized.
- `audio/stems/AMUL_OTM_EP01_vocal_guide_stem.wav` plays the original vocal melody on a synth lead, timed to the shots, for a singer to record over.
- The lyric timing is in `metadata/audio_cues.json`.

**Audio:** all of it is original and synthesized in `scripts/audio.py`. No samples are used and no existing soundtrack is imitated.

## Build

```bash
python3 scripts/art.py
```
MOO_01 cutout parts, backlight rims and the stand-in character sheet.

```bash
blender -b --factory-startup --python scripts/build.py
```
Writes `scenes/AMUL_OTM_EP01_MASTER.blend`.

```bash
python3 scripts/audio.py
```
Writes the music, vocal-guide, SFX and ambience stems plus the temp mix. It needs `build.py` first, because the hoof sounds come from the hoof contacts in the animation.

```bash
python3 scripts/continuity.py
```
Runs the hoof grounding, sliding and cut checks.

```bash
blender -b scenes/AMUL_OTM_EP01_MASTER.blend --python scripts/continuity.py
```
Adds the scene checks: cuts and lenses, block slide, door hinges, sun, and artwork view switches.

```bash
blender -b scenes/AMUL_OTM_EP01_MASTER.blend --python scripts/render.py -- --animatic --frames 1-720
```
Renders the animatic frames.

```bash
blender -b scenes/AMUL_OTM_EP01_MASTER.blend --python scripts/render.py -- --still 313
```
Renders a 4K hero still at Blender frame 313 (brief frame 312).

```bash
python3 scripts/deliver.py
```
Encodes the MP4s and builds the contact sheet.

## Final 4K master (documented, not run here)

```bash
blender -b scenes/AMUL_OTM_EP01_MASTER.blend --python scripts/render.py -- --final --frames 1-720
```
- **Settings:** 3840×2160 at 128 samples with adaptive sampling and OIDN, 16-bit PNG to `renders/final/`.
- **Render layers:** all are enabled — `01_BEAUTY` (with mist, AO, Z, shadow-catcher, Cryptomatte and denoise data), `02_MOO_ILLUSTRATED`, `03_MOO_SHADOW_CATCHER` and `05_ATMOSPHERE`.
- **GPU:** set `cycles.device = 'GPU'` on a CUDA or OptiX machine.
- **Splitting:** the shots can be divided across machines by frame range (see `config.SHOTS`).

## Layout

```
scripts/   config (axes, sun, barn layout, shot table), art (MOO_01 artwork), env (Cycles environment), moo (rig, artwork planes,
           shadow proxy), anim (performance, IK, gait, cameras), build, audio, render, render_test, continuity, deliver
art/       moo_01/ layered cutout PNGs (side, rear, three-quarter head + backlight rims)
scenes/    AMUL_OTM_EP01_MASTER.blend
audio/     stems/ (music, vocal guide, sfx, ambience, music sub-stems) + temp mix
delivery/  animatic MP4s (temp mix / clean), contact sheet, stand-in character sheet, continuity notes
metadata/  moo_parts, build_log (per-frame pose + hoof positions), continuity_report, audio_cues
```
