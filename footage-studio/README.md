# Footage Studio

A local desktop app for production houses and wedding studios. Point it at one
project folder (one wedding, one shoot) and it turns the raw footage into a
searchable clip library: a bucket, indoor/outdoor, a keeper hint (1-5) and a
one-line description per clip, a filterable library with click-to-play, and a
`manifest.csv`.

It runs entirely on your own machine. No accounts, no backend, no telemetry.

This is the fresh build described in [HANDOVER.md](HANDOVER.md). The original
prototype is kept, unchanged, in `reference-prototype/` for reference.

## Status

| | |
|---|---|
| Demo mode, library, manifest, filing, undo, resume | Working, covered by automated tests (Linux, Python 3.9 and 3.13) |
| App window | Working, driven end to end in a headless browser |
| **AI tagging against the real Anthropic API** | **Never run. Unproven until a real run passes.** Only tested against a stand-in. |
| **Mac app bundle** | **Never launched on a real Mac.** Its launcher script is tested on Linux only. |
| Native "Choose folder…" button, "Show in folder" | Mac-only code paths, untested. Typing or pasting the path works everywhere. |
| Windows | Not started. |

## Try it (demo mode, no API key)

Needs only `python3` (3.9+) and `ffmpeg`.

```bash
python3 -m footage_studio
```

Click **Try it with sample clips**, leave **Demo mode** selected, and press
**Test run**. Demo tags are fake; nothing leaves the computer.

## Mac app (double-click, no terminal)

```bash
python3 scripts/build_mac_app.py
```

This writes `dist/Footage Studio.app` and a zip of it. The app is
self-contained and can be dragged to Applications. The Mac still needs Python
3 and ffmpeg; the app shows a dialog explaining how to get them if either is
missing. The app is unsigned, so a copy downloaded from the internet has to be
opened the first time with right-click → Open.

## The trust model

- **Non-destructive by default.** Tagging only reads the project folder. The
  library (catalog, thumbnails, manifest) is kept in Footage Studio's own data
  folder (`~/Library/Application Support/Footage Studio` on a Mac), so a run
  leaves the project folder byte-identical.
- **Filing is opt-in and undoable.** "File clips into Sorted folders" moves each
  tagged clip to `Sorted/<bucket>/<its original camera folders>/` with its
  sidecar files (`.xmp .json .xml .thm .lrf`). Files are renamed in place, never
  copied or re-encoded. Every move is logged before it happens in
  `Sorted/.footage-studio-moves.jsonl`; **Undo filing** puts every file back and
  repairs the library and manifest. Undo never overwrites a file.
- **Consent before anything is sent.** AI tagging shows exactly what will be
  sent and waits for an explicit confirmation, every run. Only small preview
  frames are sent, never videos or file names.
- **The API key is session-only.** It is typed into the app, used for that run,
  and never written to disk, config or logs. On the command line it is read
  from a hidden prompt, never from an argument.

## Good to know

- **Re-running does not fix wrong tags.** Clips that are already tagged are
  skipped (that is what makes a stopped or crashed run resume). To tag again,
  tick **Re-tag clips that are already tagged** (`--rescan` on the command
  line), or correct a single clip by clicking it in the library. Manual
  corrections are never overwritten.
- Demo tags are replaced automatically the first time AI tagging runs.
- Clips that can't be read are skipped and listed in the manifest and at the
  bottom of the library; they never stop a run.
- Formats: mp4, mov, mkv, webm, avi, mts are decode-verified. m4v, 3gp, m2ts,
  mxf are attempted but unverified. Camera RAW (R3D, BRAW, Cinema RAW) is not
  supported. Some formats tag fine but won't play in the browser; use
  "Show in folder".

## Command line

```bash
python3 -m footage_studio samples DIR      # write sample clips
python3 -m footage_studio tag DIR --demo   # fake tags, nothing sent
python3 -m footage_studio tag DIR          # AI tagging (asks to confirm, then for the key)
python3 -m footage_studio file DIR         # file into Sorted/
python3 -m footage_studio undo DIR         # put everything back
```

## Development

```bash
python3 -m unittest discover -s tests -t .
```

No dependencies beyond the standard library; the tests need `ffmpeg`.

| Module | Role |
|---|---|
| `media.py` | find clips, read metadata, pull preview frames (read-only) |
| `tagging.py` | demo tagger and Anthropic tagger; the consent gate |
| `library.py` | per-project catalog (append-only journal), manifest |
| `pipeline.py` | the tagging run; resume and re-tag rules |
| `filing.py` | opt-in filing into `Sorted/` and undo |
| `server.py`, `web/` | the app window (loopback only) |

Not built yet, in the brief's priority order: cross-project search, Windows
support. Also open: a first real AI tagging run, a first launch on a Mac, and
exporting a standalone copy of the library into the project folder.
