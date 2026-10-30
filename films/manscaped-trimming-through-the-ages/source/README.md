# MANSCAPED: Trimming Through the Ages

A five-minute crayon picture book (300.000 s, 7200 frames at 24 fps, 4:3 master at 1440×1080). It is a fictional,
satirical history of male grooming, read by a dry British narrator, and it ends on the modern Lawn Mower. Every
incident in it is invented comedy. No quote is attributed to a real person, and the brand's origin is not placed in
any era.

The film is built on the library's Crayon Picture Book engine (`styles/crayon-book`): `gl.js` (WebGL2 wax and
watercolour compositor), `crayon.js` (stroke library), `rig.js` and `chars.js`, switched to a 1440×1080 canvas.

| path | what |
|---|---|
| `story.json` | the script: 10 chapters × 5 beats, with beat times and lines |
| `film.js` | chapter timeline, line placement, page turns, book-copy writing, compositing |
| `chapters/ch01–ch10.js` | one independently testable 30 s scene per chapter (`?ch=N`) |
| `figs.js` | character rig (about 2.5 heads tall, dot eyes, pink cheeks, mitten hands), squirrels, props |
| `pal.js` | the crayon box: 14 sticks, ≤ 12 per chapter; one sap-green wash |
| `sheets.js`, `sheets/` | model sheets (`?sheet=chars&who=…`) and the ten storyboard sheets |
| `tts/` | narration: Kokoro `bm_george` as the timbre reference, Chatterbox as the voice, Whisper-checked |
| `music/score.py` | original score: one motif rearranged per era for small instruments |
| `mix.py` | Foley + ambience + narration mix; stems written to `out/stems/` |
| `build.sh` | full pipeline: render by chapter, verify 720 frames each, stitch by stream copy, master at −14 LUFS |
| `assets/brand/` | **slots for the approved packshot and wordmark** (see its README) |
| `qc/` | QC report and timed narration script |
