# The Seat Is Taken

A 15-second, 1920×1080, 30 fps flat-vector motion explainer built in Remotion. It's a fan piece inspired by the character dynamics of *The Big Bang Theory*.

- **No show assets.** It uses no footage, episode audio, logos or likenesses. The characters are headless outfit silhouettes drawn as SVG.
- **Original voices.** All voices are generic text-to-speech voices (Kokoro), not imitations of the actors.

## Layout
- `src/config.js`: palette, stage geometry, shot windows, voice-line placement (from measured durations) and SFX cue sheet.
- `src/components/Characters.jsx`: reusable outfit-silhouette `<Person>` (stand/sit poses, arm angles, breathing).
- `src/components/Props.jsx`: couch, striped cushion, takeaway carton, fry, door, couch icon, arrows.
- `src/components/Type.jsx`: phrase reveals, keyword highlights, underline, name labels, speech bubbles, diagram labels, title.
- `src/scenes/Scenes.jsx`: the eight shots. `src/Main.jsx` sequences scenes and audio, and ducks the music under dialogue.
- `scripts/vo.py` → `scripts/normalize_vo.py`: voice generation and loudness matching. `scripts/sfx.py`: all SFX and music (synthesized).
- `scripts/finalize.sh`: final audio gain and limiter, and trims the container to exactly 15.000 s.

## Commands
```bash
npm install
npm run preview                        # half-resolution preview → preview/preview-960.mp4
npm run render && bash scripts/finalize.sh 3.5   # → out/the-seat-is-taken-final.mp4
```
Voice lines need the Kokoro ONNX model files: `python3 scripts/vo.py <model.onnx> <voices.bin> public/audio`.

## Shot timing (frames)
Shots are re-timed from the storyboard so every line fits its measured length. For example, the narrator line runs 3.0 s rather than the storyboard's 1.5 s.

| Shot | Frames |
|---|---|
| Arrival | 0–93 |
| Violation | 93–131 |
| Explanation | 131–180 |
| Logic | 180–270 |
| Penny | 270–306 |
| Fries | 306–340 |
| Reaction | 340–405 |
| Hold | 405–450 |
