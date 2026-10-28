# The Thirty-Five Dollar Squiggle

A five-minute crayon picture book about how the Nike swoosh came to be. It is told by one storyteller across 12 drawn pages joined by page turns, and it ends on the open book lying on a desk.

The film runs inside the lemo-opuscar library at `films/swoosh-crayon/`. It uses the Crayon Picture Book style engine (`gl.js`, `crayon.js`, `rig.js`, `pal.js` and `chars.js`, all copied from `styles/crayon-book/demo`). `rig.js` has one fix: outlines close properly on four-sided shapes.

- `story.json`: the narration, organised by page, with the pause after each line. The sources are listed at the top of the file.
- `pages.js`: the 12 pages. Each one is drawn on live and timed to its narrated lines.
- `film.js`: builds the timeline from the measured voice lengths, scaled to 300 s. It also handles page turns, the printed-word subtitles, and the events for the mix.
- `figs.js`: the generic picture-book figures and props. The curve is only ever drawn as a loose crayon stroke.
- `end.js`: the book on the desk and The End.
- `tts/`: the narrator, made with Kokoro af_heart as a reference voice and spoken by Chatterbox. Every take is checked with Whisper.
- `music/score.py` and `mix.py`: the original small-instrument waltz, the crayon and paper foley, and the narration mix.
- `build.sh`: runs the full pipeline, rendering at 12 fps and mastering to 24 fps at −14 LUFS.

The fonts are open-licensed Google Fonts; download the `.ttf` files listed in `fonts/fonts.css` from github.com/google/fonts.

Real people appear only as generic figures with no likenesses. The official logo and wordmark are never shown.
