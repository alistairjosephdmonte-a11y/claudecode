# Asset manifest — THE SEAT IS TAKEN

No character, environment or prop assets were supplied, so every visual was drawn in code for this film (original designs, not likenesses of any actor). All audio is generated: voices with Kokoro TTS (offline; ElevenLabs was not available — no API key in this environment), music and sound effects synthesized in Python.

## Visual assets (code-drawn, `src/components/`)

| Asset | File | Notes |
|---|---|---|
| Apartment set: wall, window, floor lamp, atom print, whiteboard, open door 4A, floor | `Set.tsx` → `Background` | one fixed world, 1920×1080 units |
| Couch with 3 seat cushions (left = Sheldon's spot) | `Set.tsx` → `Couch` | `spotShift` displaces his cushion; `squash` dents a cushion when sat on |
| Coffee table, rug, drink | `Set.tsx` → `CoffeeTable` | foreground parallax layer |
| Takeout boxes, fries carton, single fry, paper takeaway bag | `Set.tsx` | generic, no brands |
| Sheldon, Leonard, Penny puppets | `Characters.tsx` | head turn, eyes, brows, lip-synced mouth, 2-segment arms, stand/walk/sit |
| Couch diagram | `Diagram.tsx` | blue line-draw, gold spot marker, 2 measurements, arrow |
| Typography components | `Type.tsx` | name labels, phrase captions, highlights, underline, lower third, stamp, title |

## Audio files (`public/audio/`)

| File | Bytes | What |
|---|---|---|
| `public/audio/music.wav` | 2880044 | Music bed: pizzicato bass pulse + kalimba accents, F major, 112 bpm, stops after the punchline |
| `public/audio/sting.wav` | 230444 | Final comedic sting |
| `public/audio/voice/leonard1.wav` | 83484 | Leonard (am_liam): "I needed space for the food." |
| `public/audio/voice/narrator.wav` | 130346 | Narrator (bm_lewis): "For Sheldon Cooper, even a couch has rules." |
| `public/audio/voice/penny1.wav` | 48306 | Penny (af_nicole): "Looks comfy." |
| `public/audio/voice/sheldon1.wav` | 54144 | Sheldon (am_eric): "Why have you moved it?" |
| `public/audio/voice/sheldon2.wav` | 126398 | Sheldon (am_eric): "The seating arrangement follows a specific geometry." |
| `public/audio/voice/sheldon3.wav` | 101276 | Sheldon (am_eric): "This is precisely why we need rules." |
| `public/audio/sfx/bag.wav` | 172844 | Takeaway bag rustle |
| `public/audio/sfx/bite.wav` | 67244 | Bite |
| `public/audio/sfx/click.wav` | 9644 | Typography click |
| `public/audio/sfx/container.wav` | 134444 | Food container rustle |
| `public/audio/sfx/creak.wav` | 105644 | Couch creak |
| `public/audio/sfx/door.wav` | 249644 | Door opening |
| `public/audio/sfx/fabric.wav` | 96044 | Fabric movement |
| `public/audio/sfx/fry_take.wav` | 57644 | Taking a fry |
| `public/audio/sfx/linedraw.wav` | 172844 | Diagram line drawing |
| `public/audio/sfx/roomtone.wav` | 2880044 | Apartment room tone |
| `public/audio/sfx/sit.wav` | 192044 | Sitting down on the couch |
| `public/audio/sfx/step.wav` | 38444 | Footstep |
| `public/audio/sfx/utensil.wav` | 67244 | Utensil taps |

## Fonts

| Font | File | Licence |
|---|---|---|
| Inter (variable) | `public/fonts/Inter.ttf` | SIL OFL 1.1 (`public/fonts/OFL-Inter.txt`) |

## Generated data (`src/generated/`)

- `voice-durations.json`: measured clip lengths, used for ducking and timing
- `lipsync.json`: per-frame mouth openness from each voice clip's loudness
- `words.json`: speech-to-text word timings, used to time the caption phrases

## Third-party software

- Remotion 4.0.537 (Remotion License: free for individuals and small companies; check remotion.dev/license for company use)
- Kokoro-82M via kokoro-onnx (Apache 2.0), faster-whisper (MIT) for the speech check
- Lemo-Opuscar core audio tools (MIT): Karplus–Strong plucked strings, procedural sfx helpers
