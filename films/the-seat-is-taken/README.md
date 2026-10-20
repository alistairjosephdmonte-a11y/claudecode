# THE SEAT IS TAKEN

A 15-second, 1920×1080, 30 fps (450 frames) animated sitcom recap built in Remotion. Sheldon finds his couch cushion shoved aside for Leonard's food, explains the geometry of seating, and Penny takes the comfy spot and a fry.

**Unofficial parody.** The characters are from a TV series owned by others. All artwork, voices, music and sound here are original, and the voices don't imitate any actor. Don't use this commercially.

## Deliverables

| File | What |
|---|---|
| `out/the-seat-is-taken.mp4` | final H.264 MP4 (1920×1080, 30 fps, 450 frames, AAC 48 kHz, −16 LUFS, −1.5 dBTP) |
| `out/preview-540p.mp4` | low-resolution preview render |
| `out/the-seat-is-taken.srt` | narration + dialogue subtitles |
| `public/audio/voice/*.wav` | narration and the five dialogue lines, one file each |
| `public/audio/music.wav`, `sting.wav`, `sfx/*.wav` | music bed, sting, sound effects |
| `ASSET_MANIFEST.md` | every asset, what it is and where it came from |
| `src/` | the Remotion project |

## Project layout

```
src/config.ts            colours, font, shot boundaries, voice cue frames, caption cues, sfx cues, music ducking
src/SeatIsTaken.tsx      root composition: picks the shot for the frame, loads the font, adds the soundtrack
src/scenes/Shot0X*.tsx   eight independent shot components (camera, character state, captions)
src/components/          World (set + 2.5D parallax camera), Set, Characters, Diagram, Type (typography system)
src/audio/Soundtrack.tsx voice / sfx sequencing, music with automatic ducking under speech
audio-src/               voice lines + the script that builds music, sfx and lip-sync data
scripts/                 render.sh (preview → final → loudness), stills.mjs (review frames)
```

## Rebuild

```sh
npm install
npm run audio            # needs a Lemo-Opuscar library with voice + music tiers: LIB=/path/to/lemo-opuscar npm run audio
sh scripts/render.sh     # set REMOTION_CHROME=/path/to/chrome-headless-shell to use an existing browser
npm run studio           # live preview
```

## Timing (retimed from the brief to the real voice lengths)

The six generated lines run 11.3 s together, so the shot boundaries in the brief were moved to fit them (no voice was sped up):

| Shot | Frames | Seconds | Line |
|---|---|---|---|
| 01 Arrival | 0–84 | 0.0–2.8 | Narrator 0.07 s |
| 02 Violation | 84–128 | 2.8–4.27 | Sheldon 2.87 s, Leonard reacts from 3.87 s |
| 03 Explanation | 128–190 | 4.27–6.33 | Leonard 4.33 s, pause |
| 04 Logic | 190–272 | 6.33–9.07 | Sheldon 6.4 s; hand close-up 7.4–8.13 s |
| 05 Penny | 272–318 | 9.07–10.6 | Penny 9.53 s; Sheldon reacts 10.27 s |
| 06 Fries | 318–344 | 10.6–11.47 | hand close-up, then Leonard's look |
| 07 Punchline | 344–420 | 11.47–14.0 | Sheldon 11.53 s; silence after 13.9 s; Leonard's reaction 13.67 s |
| 08 Hold | 420–450 | 14.0–15.0 | wide on all three, title, sting at 14.13 s |
