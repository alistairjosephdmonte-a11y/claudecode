# Footage Studio - engineering handover

Self-contained handover for a coding LLM (Claude Code, Codex, etc.).
Everything needed to continue or rebuild this product is in this package;
no other context exists or is required. Written 15 Nov 2026 against the
exact source included here.

## How to read this package

Two halves:

1. REFERENCE PROTOTYPE - `footage_sort.py` and `footage_studio.py`, a working
   demo-tested prototype. Treat it as proven reference material: mine it for
   the pipeline logic, the prompt design, the dashboard, the trust rules.
   You may build on it or rebuild from scratch - that choice is yours to
   make and justify.
2. FRESH-BUILD BRIEF - the requirements below. This is the product to end
   up with, stated independently of the prototype. Where the prototype and
   the brief disagree, the brief wins.

## What this product is

A local desktop app for production houses and wedding studios. It points at
one project folder (one wedding, one shoot) and turns the raw footage into a
sorted, searchable clip library: AI tags per clip (bucket, indoor/outdoor,
tentative keeper hint 1-5, one-line description of what's visible), a
searchable dashboard with filters and click-to-play, and a manifest.csv.

Product direction: a tool studios run themselves on their own machines.
Not a hosted service. No backend, no accounts, no telemetry. Mac is the
first test platform; Windows follows.

## Fresh-build requirements

MUST:
1. Double-click launch on Mac - no terminal, no config editing for the
   studio user. A small app window (the prototype uses a localhost web UI;
   an equivalent or better approach is fine).
2. Pick a project folder and footage type (wedding / production presets,
   each with its own buckets; buckets user-editable).
3. AI-tag every clip from a few sampled preview frames (the prototype uses
   4 frames per clip via ffmpeg, tagged by Anthropic's claude-haiku-5-5,
   vision). Output per clip: bucket, indoor/outdoor, keeper hint 1-5,
   one-line description of what's visible.
4. Searchable dashboard: filter by bucket/keeper/setting, search
   descriptions, click a thumbnail to play the clip.
5. manifest.csv of every clip and its tags.
6. Non-destructive by default. A normal run never moves, deletes or
   re-encodes originals. Filing into Sorted/ folders is opt-in, logged, and
   fully undoable (undo restores originals and repairs catalog, manifest
   and dashboard). Camera-card folder structure and sidecar files
   (.xmp/.json/.xml/.thm) survive filing and undo intact.
7. Consent before egress: no frames leave the machine until the user
   explicitly confirms. Videos are never uploaded - only small preview
   frames. The API key is session-only: never written to disk, config, logs
   or shell history.
8. Demo/mock mode that exercises the full flow with fake tags and no API
   key, so anyone can try it safely.
9. Resume after interruption (checkpointed catalog).
10. Unreadable/unsupported clips are skipped with a manifest note, never
    fatal.

SHOULD (known gaps, in priority order):
- Per-clip tag correction in the dashboard (today: edit presets and
  re-scan).
- A rescan control in the app UI.
- Cross-project search (each project currently builds its own library).
- Windows support, tested on real hardware.

NOT NOW: hosted SaaS, accounts, cloud storage, multi-user.

## Acceptance checks for any build

- Demo mode runs end-to-end on a folder of sample clips with zero setup
  beyond python3 + ffmpeg.
- A run with filing switched off leaves the project folder byte-identical.
- Tagging cannot start without the consent confirmation.
- A forced quit mid-run resumes without re-tagging finished clips.

## Reference prototype: test status

VERIFIED (ran 15 Nov 2026, demo/mock mode, synthetic footage on Linux):
full pipeline end-to-end - scan, frame extraction, mock tagging, dashboard,
manifest, organize, undo (incl. dashboard repair), checkpoint resume,
consent refusal, path-traversal confinement, Range requests. UI exercised
at desktop and mobile widths. Verified decodable: mp4, mov, mkv, webm, avi,
mts.

NOT YET DONE:
- Real AI tagging has never run against the live Anthropic API. The code
  path exists but is unproven; expect prompt/response-parsing fixes on the
  first real run.
- The app has not been launched on an actual Mac. The .command launcher is
  syntax-checked but hardware-untested. The Windows .bat is untested.
- m4v/3gp/m2ts/mxf recognized but decode-unverified. RAW video (R3D, BRAW,
  Cinema RAW) declared unsupported.

## Prototype behavior notes (if you reuse it)

- Re-running a sort REUSES cached tags: clips already in catalog.json are
  skipped, and the UI has no rescan path. To force re-tagging (e.g. after
  editing PRESETS), run the CLI with `sort --rescan`, or delete
  `_Library/catalog.json`. Never tell users "just re-run" fixes wrong tags.
- Undo only reverses moves made with organize on; it also clears
  sorted_path and rebuilds dashboard/manifest.
- `clip_id` is a content-ish hash; thumbnails are keyed by it.
- The dashboard is one self-contained HTML file with the catalog embedded
  as JSON - no server needed to view it (click-to-play needs the app's
  `/p/` serving or any local server).

## Other files

- `README.md` - user-facing setup and usage for the prototype.
- `Footage Studio.command` / `Footage Studio.bat` - prototype launchers
  (check python3 + ffmpeg, run footage_studio.py).
- `PROMPT.md` - the starter prompt for the coding assistant.
