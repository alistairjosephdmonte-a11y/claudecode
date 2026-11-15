# Footage Sorter - for production houses & wedding studios

Point it at a project folder (one wedding, one shoot, one client job) and it
turns the pile of clips into a searchable library with a dashboard you open
in any browser. Every clip gets tagged by Claude (bucket, indoor/outdoor,
keeper score 1-5 for edit selects, one-line description) and shown in a
filterable thumbnail grid with click-to-play.

Cull a wedding overnight. Find "all ceremony clips, keeper 4+" in seconds.
Pull selects for an edit without scrubbing through cards.

**Safe by default: a normal run never moves, deletes or re-encodes a single
file.** It only reads your clips and writes its own `_Library` folder.
Filing clips into `Sorted/` is a separate step you choose (`--organize`),
and even that is fully undoable.

## The easy way - the app (no command line)

- **Mac:** double-click `Footage Studio.command`. A small app opens in your
  browser: pick the project folder, choose the footage type, paste your API
  key (typed hidden, kept for that session only), confirm what tagging sends,
  and hit "Test run - 50 clips". Watch progress live, then open the
  dashboard from the app. Filing into Sorted folders and undo are buttons in
  the same window. No terminal needed.
- **Windows:** double-click `Footage Studio.bat` (same app). The Windows
  launcher is included but has not been run on a real Windows machine yet -
  Mac is the first test platform.

## What you need

1. **A computer or edit station** (Mac or Windows) with the footage on it -
   local drive, external SSD or NAS all work.
2. **Python 3** - python.org (Windows: tick "Add python.exe to PATH").
   Macs already have it.
3. **ffmpeg** - reads the clips and pulls preview frames.
   - Mac: `brew install ffmpeg`
   - Windows: download a build from https://www.gyan.dev/ffmpeg/builds/ ,
     unzip, add the `bin` folder to PATH.
4. **An Anthropic API key** - console.anthropic.com → API keys.
   Tagging is pay-per-use; current rates are on Anthropic's pricing page:
   https://platform.claude.com/docs/en/about-claude/pricing
   Before the first clip is tagged, the sorter tells you exactly what gets
   sent and asks you to confirm. Videos themselves are never uploaded -
   only 4 small preview frames per clip.

## Quick start (command line)

```bash
# 1. TEST RUN on 50 clips - always start here. Nothing is moved.
python3 footage_sort.py sort --folder "/drives/Projects/Sharma x Patel" --limit 50

# 2. Open the dashboard (the run prints its path) and check the buckets.
#    Wrong buckets? Edit PRESETS at the top of footage_sort.py,
#    then re-run with --rescan --limit 50.

# 3. Tag the whole project (still moves nothing)
python3 footage_sort.py sort --folder "/drives/Projects/Sharma x Patel"

# 4. OPTIONAL, only if you want the clips physically filed:
python3 footage_sort.py sort --folder "/drives/Projects/Sharma x Patel" --organize
```

Corporate / commercial shoot instead of a wedding? Use the production preset:

```bash
python3 footage_sort.py sort --folder "/drives/Projects/Acme Launch" --preset production
```

Changed your mind after organizing? Every move is undoable:

```bash
python3 footage_sort.py undo --folder "/drives/Projects/Sharma x Patel"
```

## Buckets

**Wedding:** getting ready · ceremony · couple portraits · family & groups ·
speeches · first dance · dance floor · details & decor · drone & aerial ·
guest moments · behind the scenes · other

**Production:** interview & a-roll · b-roll · product shots · drone & aerial ·
behind the scenes · screen recording · stills & plates · other

Edit `PRESETS` at the top of `footage_sort.py` to match how your studio
talks about footage - the buckets become the folders under `Sorted/`.

## Using the library

Open `dashboard.html` in the project folder. Filter by bucket, setting,
source card or keeper score; search descriptions in plain words; click any
clip to play it in place. To pull selects into an edit, find them in the
dashboard and **copy** them out - copy, don't move, so the library stays
intact. `_Library/manifest.csv` is a spreadsheet of every clip, its tags,
and exactly what happened to it.

## What organizing does (when you choose it)

`--organize` files each clip into `Sorted/<bucket>/<card-or-folder>/`,
**keeping the camera/card folder it came from** and carrying its sidecar
files (.xmp/.json/.xml/.thm) with it. Every move is appended to
`_Library/moves.jsonl`; `undo` walks that log backwards and restores every
file, sidecars included.

## Formats

- **Verified in testing** (ffmpeg 4.4): mp4, mov, mkv, webm, avi, mts.
- **Recognized but unverified:** m4v, 3gp, m2ts, mxf - these usually decode
  with ffmpeg but weren't tested here.
- **Not supported:** camera raw video like R3D, BRAW and Cinema RAW Light -
  those need the camera maker's own SDK. Any clip the sorter can't read is
  skipped with a note in the manifest, never fatal to the run.

## Honest notes

- **Start with the 50-clip test.** Fixing buckets at 50 clips takes five
  minutes; at 5,000 it takes all day.
- **One project folder per run.** Each project gets its own catalog and
  dashboard.
- **It's not perfect.** Some clips land in the wrong bucket. Search and
  filters still beat scrubbing cards.
- **It never deletes.** The only writes are its own `_Library/` files and,
  when you ask for it, logged moves into `Sorted/`.
- **Your key and your footage.** Tagging sends 4 preview frames per clip
  to Anthropic (never the video) and asks for confirmation before the
  first send. The key is typed hidden and never saved or printed.
- A few seconds per clip; big projects run a while. It checkpoints every
  20 clips, so stopping and re-running never redoes finished work.

## Files it creates

```
Project folder/
  dashboard.html        <- open this
  Sorted/<bucket>/<card>/   <- only if you run --organize
  _Library/catalog.json <- the brain; never re-scans a clip
  _Library/manifest.csv <- every clip, its tags, what happened
  _Library/thumbs/      <- thumbnails for the grid
  _Library/moves.jsonl  <- the undo log
```
