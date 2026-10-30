# West Side Story, Explained (1:02)

A one-minute motion-graphics explainer in a mid-century cut-paper poster style: cream paper, signal red, ink, mustard and blue, set in bold condensed type, with hard cuts behind a paper wipe.

It covers the 1949 idea, *East Side Story*, and the 1955 rethink; Jets versus Sharks; the four creators; the 1957 opening (732 performances); losing the Best Musical Tony to *The Music Man*; the 1961 film's 10 Oscars; and Rita Moreno and Ariana DeBose, who each won an Oscar for playing Anita.

The film runs inside the lemo-opuscar library at `films/wss-motion/`.

- `main.js`: the Canvas 2D scenes, timed to the narration (`voice.json`).
- `mix.py`: an original finger-snap jazz groove and sound effects synced to the cuts. It quotes no melody from the show.
- `tts/`: the narration, voiced by Chatterbox with a Kokoro am_michael reference voice.

Build:

1. `node core/render/events.mjs films/wss-motion`
2. `.venv/bin/python films/wss-motion/mix.py`
3. `node core/render/video.mjs films/wss-motion --fps 30`
4. `sh core/render/mux.sh …`

Fonts: Bebas Neue, Oswald and DM Serif Display, all from github.com/google/fonts.

Real people appear only as names in type. Captions are always on screen.
