# The Ramayana: a pop-up book

A 2-minute (123 s) explainer of Valmiki's Ramayana in the paper pop-up style: cut-paper stick figures on a pop-up book lying on a real desk.

- `ramayana.mp4`: the film (1920×1080, 24 fps, −14 LUFS, subtitles burned in)
- `ramayana.srt`: narration subtitles
- `TREATMENT.md`: structure, spreads, camera, sound
- `CREDITS`: assets, voices, sample libraries, fonts

Structure: a graphite prologue (Valmiki, the krauncha birds, the first verse in Devanagari), then four spreads pairing the seven books (1–2, 3, 4–5, 6–7). The book closes at the end, but one card stays standing: Valmiki and the twins singing.

Built on the Lemo-Opuscar paper-popup engine (MIT). To rebuild, copy this folder to `films/ramayana/` in a Lemo-Opuscar clone, run `sh plugin/skills/lemo-opuscar/scripts/setup.sh deps voice music` and `sh tools/fetch.sh hdri` plus `sh tools/fetch.sh instruments vsco2ce|vcsl|freepats`, copy `core/assets/polyhaven/{lythwood_lounge_2k.hdr,walnut_*,desk_lamp_arm_01,tea_set_01}` into `assets/`, then run `sh build.sh`. On a machine without a GPU the render takes about 2 hours.
