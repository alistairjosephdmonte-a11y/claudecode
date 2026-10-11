# Eight Fifteen

A 2-minute-15 narrated film about the atomic bombings of Hiroshima and Nagasaki, drawn in code in the style of a flat, ink-outlined still life. Sources are listed on screen at the end and in `CREDITS`.

- `eight-fifteen.mp4`: the film (1080p, 24 fps, −14 LUFS, subtitles burned in)
- `eight-fifteen.srt`: subtitles
- `TREATMENT.md`: structure, shot list, cue map and sound design
- `CREDITS`: third-party material, licences and the historical sources

Built with the [Lemo-Opuscar](https://github.com/lemomo-ai/lemo-opuscar) tools (MIT). To rebuild, copy this folder to `films/eight-fifteen/` inside a Lemo-Opuscar clone, run `sh plugin/skills/lemo-opuscar/scripts/setup.sh deps voice music` from that clone, then run `sh films/eight-fifteen/build.sh`.
