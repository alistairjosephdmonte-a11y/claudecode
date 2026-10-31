# Brand Coroner · Case 001 · Blockbuster: "The $50 Million Decision"

An eight-minute investigative documentary: 48 shots × 10 s, 11,520 frames at 24 fps, 16:9. This is the 1080p cut; 4K follows on approval.

**Idea:** *Every decision leaves evidence.* The whole film takes place on one investigation table. Documents, typeset filings, source cards and receipts lie on it, along with architectural-model reconstructions (Dallas, an office entrance, a boardroom, a video store, a mail-sorting facility, an early-2000s desk), a store network on a heavy plinth, and physical charts. Every set has a fixed place on the table, so the closing crane (shot 46) shows the whole case at once.

## How it is built

The picture is three.js, rendered headless frame by frame. Every frame is a pure function of time, so any frame can be rendered alone.

| File | Contents |
|---|---|
| `story.py` → `story.json` | The 48 shots: title, act, evidence classification, narration line and source note. This is the single source of truth, and it also writes `tts/lines.json` |
| `world.js` | Palette, paper and card materials (fibres, edge tone, curl, thickness), labels, anonymous scale figures with walk and pose, and a period sedan |
| `sets.js` | The permanent sets and their table positions |
| `props.js` | Evidence objects: source cards, typeset filing excerpts, editorial summaries, dark plates, the illustrative receipt, the DVD and a neutral mailer, chart blocks and gears |
| `shots.js` | Each shot's sets, light preset, camera path (lens in mm), props and motion |
| `main.js` | Light rig, HDRI reflections, light depth of field on the macro shots, the split screen (shot 20), and the overlay: act slugs, date titles, classification chip and source line, vignette, grain, verdict and end card |
| `music/score.py` | The original score (see "Music and sound" below) |
| `mix.py` | Per-shot procedural Foley, narration placement, ducking, stems and `subs.srt` |
| `tts/` | Narration. A Kokoro `am_michael` reference timbre is re-voiced by Chatterbox; every line is checked by Whisper |
| `tools/render.sh` | Renders act by act (6 × 1920 frames), verifies each act and stitches them by stream copy |
| `tools/manifest.mjs` | Writes `qc/shot-list.md` and `qc/manifest.json`: frames, lens, camera start → end, classification, narration cue and transition for every shot |
| `build.sh` | The full pipeline. `SKIP_VOICE=1` and `SKIP_RENDER=1` skip those stages; `ACTS="0 1"` renders only those acts |

**Classification:** every shot carries a chip reading ARCHIVAL MATERIAL, RECONSTRUCTION, EDITORIAL GRAPHIC or HYPOTHETICAL SCENARIO, plus a source line. `qc/evidence-register.md` lists every claim and its source.

**Music and sound:** the score is original — an analog pad, analog bass, Salamander piano, VSCO 2 CE strings and a synthesized tick. It holds a near-silence on the film's question (shot 24). Foley is synthesized per shot: paper, card taps, plastic cases, the register, a conveyor, the CRT, relays, gears and heavy blocks. The final mix is −14 LUFS.

## Departures from the brief, by agreement

- **Rendering:** the container has no GPU and no Blender, so the film is rendered in three.js, not Blender/Cycles.
- **Reconstruction shots:** these are forensic miniatures with anonymous figures rather than photoreal humans, as agreed with the client.
- **Resolution:** the cut is 1080p first, with 4K after approval.
