#!/usr/bin/env python3
"""
Footage Sorter for production houses and wedding studios.

Point it at one project folder (a wedding, a shoot, a client job). For every
video inside it:
  1. Reads date, length, resolution, orientation and HDR with ffprobe.
  2. Grabs 4 small preview frames and asks Claude what the clip is:
     a bucket (ceremony, speeches, b-roll...), indoor/outdoor, a "keeper"
     score 1-5 for edit selects, and a one-line description.
  3. Saves everything to a catalog (_Library/catalog.json) so it never
     re-scans a clip.
  4. Moves each clip into Sorted/<bucket>/. Nothing is ever deleted, and
     every move is logged so it can be undone.
  5. Builds dashboard.html you open in your browser: bucket counts, a
     thumbnail grid, filters (bucket, setting, date, keeper score), search,
     and click-to-play.

Needs: Python 3.8+, ffmpeg and ffprobe on your PATH, and an Anthropic API key
in the ANTHROPIC_API_KEY environment variable (https://console.anthropic.com).

Usage:
  python3 footage_sort.py sort --folder /path/to/Project --limit 50   # test run
  python3 footage_sort.py sort --folder /path/to/Project              # tag + dashboard,
                                                                      # originals untouched
  python3 footage_sort.py sort --folder /path/to/Project --organize   # also file clips
  python3 footage_sort.py sort --folder /path/to/Project --preset production
  python3 footage_sort.py dashboard --folder /path/to/Project         # rebuild page
  python3 footage_sort.py undo --folder /path/to/Project              # undo all moves
  python3 footage_sort.py sort --folder PATH --mock                   # test, no API key
"""

import argparse
import base64
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import urllib.request
import urllib.error
from datetime import datetime, timezone
from pathlib import Path

# ----------------------------------------------------------------------------
# BUCKETS = the folders under Sorted/. Two presets built in; edit freely or
# add your own preset and pass --preset <name>.
# ----------------------------------------------------------------------------
PRESETS = {
    "wedding": [
        "getting ready", "ceremony", "couple portraits", "family & groups",
        "speeches", "first dance", "dance floor", "details & decor",
        "drone & aerial", "guest moments", "behind the scenes", "other",
    ],
    "production": [
        "interview & a-roll", "b-roll", "product shots", "drone & aerial",
        "behind the scenes", "screen recording", "stills & plates", "other",
    ],
}
DEFAULT_PRESET = "wedding"
SETTINGS = ["indoor", "outdoor", "mixed", "unknown"]
# The model that looks at your frames. Cheap and fast is fine here.
# Current IDs: https://platform.claude.com/docs/en/about-claude/models/overview
MODEL = "claude-haiku-5-5"

# Verified to decode with ffmpeg 4.4 in testing: mp4, mov, mkv, webm, avi, mts.
# The rest are recognized and attempted, but unverified - r3d/braw/crm usually
# need the camera maker's own SDK and will be skipped with a note if unreadable.
VIDEO_EXTS = {".mp4", ".mov", ".m4v", ".avi", ".mkv", ".webm", ".3gp", ".mts", ".m2ts", ".mxf"}
SIDECAR_EXTS = {".xmp", ".json", ".xml", ".thm", ".lrf"}  # moved along with their video
API_URL = "https://api.anthropic.com/v1/messages"
API_VERSION = "2023-06-01"
SKIP_DIRS = {"_Library", "Sorted"}


# --------------------------------------------------------------- utilities

def run(cmd):
    return subprocess.run(cmd, capture_output=True, text=True)


def check_ffmpeg():
    for tool in ("ffmpeg", "ffprobe"):
        if shutil.which(tool) is None:
            sys.exit(
                f"ERROR: {tool} not found.\n"
                "  Mac:     brew install ffmpeg\n"
                "  Windows: download from https://www.gyan.dev/ffmpeg/builds/ "
                "and add the bin folder to PATH"
            )


def safe_name(bucket):
    """A bucket name that is also a safe single folder name."""
    return re.sub(r'[\\/:*?"<>|]', '-', bucket).strip() or "other"


def clip_id(path, root):
    rel = str(path.relative_to(root))
    h = hashlib.sha1()
    h.update(rel.encode())
    h.update(str(path.stat().st_size).encode())
    return h.hexdigest()[:16]


def probe(path):
    """Return metadata dict using ffprobe. Missing values become None."""
    out = run([
        "ffprobe", "-v", "quiet", "-print_format", "json",
        "-show_format", "-show_streams", str(path)
    ])
    meta = {"date": None, "year": None, "duration": None, "width": None,
            "height": None, "orientation": None, "location": None, "hdr": False}
    if out.returncode != 0:
        return meta
    try:
        data = json.loads(out.stdout)
    except json.JSONDecodeError:
        return meta
    fmt = data.get("format", {})
    tags = fmt.get("tags", {})
    ct = tags.get("creation_time") or tags.get("com.apple.quicktime.creationdate")
    if ct:
        try:
            dt = datetime.fromisoformat(ct.replace("Z", "+00:00"))
            meta["date"] = dt.date().isoformat()
            meta["year"] = dt.year
        except ValueError:
            pass
    loc = tags.get("location") or tags.get("com.apple.quicktime.location.ISO6709")
    if loc:
        meta["location"] = loc.strip("/")
    if fmt.get("duration"):
        try:
            meta["duration"] = round(float(fmt["duration"]), 1)
        except ValueError:
            pass
    for s in data.get("streams", []):
        if s.get("codec_type") == "video":
            meta["width"] = s.get("width")
            meta["height"] = s.get("height")
            if s.get("color_transfer") in ("smpte2084", "arib-std-b67"):
                meta["hdr"] = True
            rot = (s.get("tags", {}) or {}).get("rotate")
            if not rot:
                for sd in s.get("side_data_list", []):
                    if "rotation" in sd:
                        rot = sd["rotation"]
            try:
                rot = abs(int(rot or 0))
            except (TypeError, ValueError):
                rot = 0
            w, h = meta["width"], meta["height"]
            if w and h:
                vertical = (h > w) if rot in (0, 180) else (w > h)
                meta["orientation"] = "vertical" if vertical else "horizontal"
            break
    if not meta["date"]:
        mtime = datetime.fromtimestamp(path.stat().st_mtime)
        meta["date"] = mtime.date().isoformat()
        meta["year"] = mtime.year
    # Google Photos / phone-export sidecar: <filename>.json holds date + geo.
    sidecar = path.with_name(path.name + ".json")
    if sidecar.exists():
        try:
            g = json.loads(sidecar.read_text(errors="replace"))
            ts = g.get("photoTakenTime", {}).get("timestamp")
            if ts:
                dt = datetime.fromtimestamp(int(ts), tz=timezone.utc)
                meta["date"] = dt.date().isoformat()
                meta["year"] = dt.year
            geo = g.get("geoData", {})
            if geo.get("latitude") and not meta["location"]:
                meta["location"] = f"{geo['latitude']:+.4f}{geo['longitude']:+.4f}"
        except (json.JSONDecodeError, ValueError, OSError):
            pass
    return meta


def grab_frames(path, duration, workdir, count=4, width=384):
    """Extract `count` small JPEG frames spread across the clip."""
    duration = duration or 10
    fractions = [0.15, 0.40, 0.65, 0.90][:count]
    frames = []
    for i, frac in enumerate(fractions):
        out = workdir / f"frame_{i}.jpg"
        r = run([
            "ffmpeg", "-y", "-v", "error", "-ss", f"{duration * frac:.1f}",
            "-i", str(path), "-frames:v", "1",
            "-vf", f"scale='min({width},iw)':-2", "-q:v", "5", str(out)
        ])
        if r.returncode == 0 and out.exists():
            frames.append(out)
    return frames


def save_thumb(path, duration, out, width=320):
    r = run([
        "ffmpeg", "-y", "-v", "error", "-ss", f"{(duration or 10) * 0.4:.1f}",
        "-i", str(path), "-frames:v", "1",
        "-vf", f"scale='min({width},iw)':-2", "-q:v", "6", str(out)
    ])
    return r.returncode == 0 and out.exists()


# ---------------------------------------------------------------- tagging

TAG_PROMPT = """You are tagging one video clip from {context}
using {n} preview frames taken across its length. Reply with ONLY a JSON object,
no other text:
{{
  "bucket": one of {buckets},
  "setting": one of {settings},
  "detail": "venue, location or subject clue if visible, else null",
  "keeper": integer 1-5, how likely an editor would select this clip
            (5 = in focus, stable, great moment or light; 1 = blurry, dark,
            accidental, lens cap, test shot),
  "description": "one line, under 15 words, what this clip shows"
}}
Pick the closest bucket even if none is perfect. Use "other" only as a last resort."""

CONTEXTS = {
    "wedding": "a wedding studio's project folder (one couple's event, possibly several cameras)",
    "production": "a production house's project folder (one client shoot, possibly several cameras)",
}


def tag_with_claude(frames, api_key, buckets, preset):
    parts = []
    for f in frames:
        parts.append({
            "type": "image",
            "source": {
                "type": "base64",
                "media_type": "image/jpeg",
                "data": base64.b64encode(f.read_bytes()).decode(),
            },
        })
    parts.append({
        "type": "text",
        "text": TAG_PROMPT.format(context=CONTEXTS.get(preset, "a video project folder"),
                                  n=len(frames), buckets=buckets, settings=SETTINGS),
    })
    body = json.dumps({
        "model": MODEL,
        "max_tokens": 300,
        "messages": [{"role": "user", "content": parts}],
    }).encode()
    req = urllib.request.Request(API_URL, data=body, headers={
        "content-type": "application/json",
        "x-api-key": api_key,
        "anthropic-version": API_VERSION,
    })
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            data = json.loads(resp.read())
    except urllib.error.HTTPError as e:
        detail = e.read().decode(errors="replace")[:300]
        raise RuntimeError(f"API error {e.code}: {detail}")
    text = "".join(b.get("text", "") for b in data.get("content", []))
    m = re.search(r"\{.*\}", text, re.S)
    if not m:
        raise RuntimeError(f"Could not parse reply: {text[:200]}")
    tag = json.loads(m.group(0))
    bk = str(tag.get("bucket", "")).lower().strip()
    tag["bucket"] = bk if bk in buckets else "other"
    st = str(tag.get("setting", "")).lower().strip()
    tag["setting"] = st if st in SETTINGS else "unknown"
    try:
        tag["keeper"] = max(1, min(5, int(tag.get("keeper", 3))))
    except (TypeError, ValueError):
        tag["keeper"] = 3
    tag["description"] = str(tag.get("description", ""))[:200]
    return tag


def tag_mock(path, buckets):
    """Deterministic fake tags for testing the pipeline without an API key."""
    h = int(hashlib.sha1(str(path).encode()).hexdigest(), 16)
    return {
        "bucket": buckets[h % len(buckets)],
        "setting": SETTINGS[h % len(SETTINGS)],
        "detail": None,
        "keeper": (h % 5) + 1,
        "description": f"Mock tag for {path.name}",
    }


def organize_clip(root, entry, video_path, by_year=False):
    """File one clip (and its sidecars) into Sorted/, preserving the camera/
    card folder it came from. Every move is logged; `undo` restores all."""
    dest_dir = root / "Sorted" / safe_name(entry["bucket"])
    rel_parent = video_path.parent.relative_to(root)
    if str(rel_parent) != ".":
        dest_dir = dest_dir / rel_parent
    if by_year:
        dest_dir = dest_dir / str(entry.get("year") or "unknown")
    dest_dir.mkdir(parents=True, exist_ok=True)
    companions = [video_path] + [
        s for s in video_path.parent.iterdir()
        if s.stem == video_path.stem and s.suffix.lower() in SIDECAR_EXTS
        and s != video_path]
    moved = []
    for src in companions:
        dest = dest_dir / src.name
        n = 1
        while dest.exists():
            dest = dest_dir / f"{src.stem}_{n}{src.suffix}"
            n += 1
        shutil.move(str(src), str(dest))
        log_move(root, src, dest)
        moved.append(dest)
    entry["sorted_path"] = str(moved[0].relative_to(root))
    entry["action"] = f"organized into {moved[0].parent.relative_to(root)}"


# ---------------------------------------------------------------- catalog

def load_catalog(root):
    p = root / "_Library" / "catalog.json"
    if p.exists():
        try:
            return json.loads(p.read_text())
        except json.JSONDecodeError:
            pass
    return {}


def save_catalog(root, catalog):
    lib = root / "_Library"
    lib.mkdir(exist_ok=True)
    tmp = lib / "catalog.json.tmp"
    tmp.write_text(json.dumps(catalog, indent=1))
    tmp.replace(lib / "catalog.json")


def log_move(root, src, dst):
    lib = root / "_Library"
    lib.mkdir(exist_ok=True)
    with open(lib / "moves.jsonl", "a") as f:
        f.write(json.dumps({
            "ts": datetime.now().isoformat(timespec="seconds"),
            "from": str(src), "to": str(dst),
        }) + "\n")


# ---------------------------------------------------------------- commands

def cmd_sort(args):
    root = Path(args.folder).expanduser().resolve()
    if not root.is_dir():
        sys.exit(f"ERROR: {root} is not a folder")
    check_ffmpeg()
    if args.organize:
        print("NOTE: --organize moves originals into Sorted/. Every move is logged")
        print("      and `undo` restores everything. Without it, nothing is moved.")
    buckets = PRESETS.get(args.preset)
    if not buckets:
        sys.exit(f"ERROR: unknown preset '{args.preset}'. "
                 f"Have: {', '.join(PRESETS)} - or add your own in PRESETS.")
    api_key = os.environ.get("ANTHROPIC_API_KEY", "")
    if not api_key and not args.mock:
        sys.exit(
            "ERROR: no ANTHROPIC_API_KEY set.\n"
            "  Get one at https://console.anthropic.com, then:\n"
            "  Mac/Linux:  export ANTHROPIC_API_KEY=sk-ant-...\n"
            "  Windows:    setx ANTHROPIC_API_KEY sk-ant-...\n"
            "  (or run with --mock to test the pipeline without tagging)"
        )
    if not args.mock and not args.yes:
        # Explicit consent before any footage leaves the machine.
        print("BEFORE ANYTHING IS SENT:")
        print("  Tagging sends 4 small preview frames per clip to Anthropic's")
        print("  API (api.anthropic.com) using your key. Videos themselves are")
        print("  never uploaded. Per-use API pricing applies:")
        print("  https://platform.claude.com/docs/en/about-claude/pricing")
        try:
            answer = input("  Type 'send frames' to continue: ").strip().lower()
        except EOFError:
            answer = ""
        if answer != "send frames":
            sys.exit("Stopped. Nothing was sent. Re-run and confirm, or pass --yes.")

    catalog = load_catalog(root)
    (root / "_Library" / "thumbs").mkdir(parents=True, exist_ok=True)
    tmpdir = root / "_Library" / ".frames"
    tmpdir.mkdir(exist_ok=True)

    videos = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS and not d.startswith(".")]
        for name in filenames:
            if Path(name).suffix.lower() in VIDEO_EXTS:
                videos.append(Path(dirpath) / name)
    videos.sort()

    todo = []
    for v in videos:
        cid = clip_id(v, root)
        if cid in catalog and not args.rescan:
            continue
        todo.append((v, cid))
        if args.limit and len(todo) >= args.limit:
            break

    print(f"Project: {root.name}  (preset: {args.preset})")
    print(f"{len(videos)} videos found, {len(catalog)} already catalogued, "
          f"{len(todo)} to sort now.")
    done, skipped = 0, []
    for v, cid in todo:
        meta = probe(v)
        frames = grab_frames(v, meta["duration"], tmpdir)
        if not frames and not args.mock:
            skipped.append((v.name, "no preview frames - unreadable or unsupported format"))
            print(f"  ! {v.name}: skipped, could not read frames")
            continue
        try:
            tag = tag_mock(v, buckets) if args.mock else \
                  tag_with_claude(frames, api_key, buckets, args.preset)
        except Exception as e:  # one bad clip shouldn't stop a run
            skipped.append((v.name, str(e)[:120]))
            print(f"  ! {v.name}: {e}")
            continue
        entry = {"id": cid, "file": v.name,
                 "source_folder": v.parent.name, **meta, **tag,
                 "play_path": str(v.relative_to(root)),
                 "action": "catalogued (original left in place)"}
        thumb = root / "_Library" / "thumbs" / f"{cid}.jpg"
        if save_thumb(v, meta["duration"], thumb):
            entry["thumb"] = f"_Library/thumbs/{cid}.jpg"
        if args.organize:
            organize_clip(root, entry, v, args.by_year)
        catalog[cid] = entry
        done += 1
        print(f"  [{done}/{len(todo)}] {v.name} -> {tag['bucket']} "
              f"(keeper {tag['keeper']}) {tag['description'][:60]}")
        if done % 20 == 0:
            save_catalog(root, catalog)  # checkpoint
    # --organize also files clips that were catalogued in an earlier,
    # non-destructive run and are still sitting in their original spot.
    if args.organize:
        filed = 0
        for entry in catalog.values():
            if entry.get("sorted_path"):
                continue
            original = root / entry.get("play_path", "")
            if original.exists():
                organize_clip(root, entry, original, args.by_year)
                filed += 1
        if filed:
            print(f"  Filed {filed} previously catalogued clips into Sorted/.")
    save_catalog(root, catalog)
    write_manifest(root, catalog, skipped)
    shutil.rmtree(tmpdir, ignore_errors=True)
    write_dashboard(root, catalog)
    print(f"\nDone. {len(catalog)} clips catalogued"
          + (f", {len(skipped)} skipped (see _Library/manifest.csv)" if skipped else "") + ".")
    if not args.organize:
        print("Originals were NOT moved. Review the dashboard, then re-run with")
        print("--organize if you want them filed into Sorted/<bucket>/.")
    print(f"Open: {root / 'dashboard.html'}")


def write_manifest(root, catalog, skipped):
    """A plain spreadsheet of every clip and what happened to it."""
    import csv
    lib = root / "_Library"
    lib.mkdir(exist_ok=True)
    with open(lib / "manifest.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["file", "source_folder", "date", "duration_s", "bucket",
                    "setting", "keeper", "description", "action"])
        for c in sorted(catalog.values(), key=lambda c: (c.get("bucket", ""), c.get("file", ""))):
            w.writerow([c.get("file"), c.get("source_folder"), c.get("date"),
                        c.get("duration"), c.get("bucket"), c.get("setting"),
                        c.get("keeper"), c.get("description"), c.get("action")])
        for name, why in skipped:
            w.writerow([name, "", "", "", "", "", "", "", f"SKIPPED: {why}"])


def cmd_undo(args):
    root = Path(args.folder).expanduser().resolve()
    log = root / "_Library" / "moves.jsonl"
    if not log.exists():
        sys.exit("No moves logged - nothing to undo.")
    lines = log.read_text().strip().split("\n")
    undone = 0
    for line in reversed(lines):
        rec = json.loads(line)
        dst, src = Path(rec["to"]), Path(rec["from"])
        if dst.exists() and not src.exists():
            src.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(dst), str(src))
            undone += 1
    log.unlink()
    catalog = load_catalog(root)
    for entry in catalog.values():
        entry.pop("sorted_path", None)
        if str(entry.get("action", "")).startswith("organized"):
            entry["action"] = "catalogued (original left in place)"
    if catalog:
        save_catalog(root, catalog)
        write_manifest(root, catalog, [])
        write_dashboard(root, catalog)
    print(f"Undone: {undone} clips moved back to their original spots.")


def cmd_dashboard(args):
    root = Path(args.folder).expanduser().resolve()
    catalog = load_catalog(root)
    if not catalog:
        sys.exit("No catalog yet. Run a sort first.")
    write_dashboard(root, catalog)
    print(f"Open: {root / 'dashboard.html'}")


# -------------------------------------------------------------- dashboard

DASHBOARD_HTML = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>__TITLE__</title>
<style>
  :root { --ink:#1a1a1a; --muted:#777; --line:#e6e2da; --bg:#faf8f4; --accent:#c2571b; }
  * { box-sizing: border-box; margin: 0; }
  body { font-family: -apple-system, "Segoe UI", Roboto, sans-serif; background: var(--bg); color: var(--ink); }
  header { padding: 28px 20px 12px; }
  h1 { font-size: 26px; letter-spacing: -.5px; }
  .sub { color: var(--muted); font-size: 14px; margin-top: 4px; }
  .stats { display: flex; flex-wrap: wrap; gap: 8px; padding: 12px 20px; }
  .chip { background: #fff; border: 1px solid var(--line); border-radius: 999px; padding: 6px 12px; font-size: 13px; cursor: pointer; }
  .chip b { color: var(--accent); }
  .chip.active { background: var(--ink); color: #fff; }
  .chip.active b { color: #ffb38a; }
  .bar { position: sticky; top: 0; background: var(--bg); padding: 10px 20px; border-bottom: 1px solid var(--line); display: flex; flex-wrap: wrap; gap: 8px; z-index: 5; }
  .bar input, .bar select { font: inherit; font-size: 14px; padding: 7px 10px; border: 1px solid var(--line); border-radius: 8px; background: #fff; }
  .bar input { flex: 1; min-width: 160px; }
  .grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(180px, 1fr)); gap: 14px; padding: 16px 20px 60px; }
  .card { background: #fff; border: 1px solid var(--line); border-radius: 12px; overflow: hidden; cursor: pointer; transition: transform .12s; }
  .card:hover { transform: translateY(-2px); }
  .card img { width: 100%; aspect-ratio: 16/10; object-fit: cover; display: block; background: #ddd; }
  .card .body { padding: 9px 11px 11px; }
  .card .desc { font-size: 13px; line-height: 1.35; min-height: 2.6em; }
  .card .meta { display: flex; justify-content: space-between; align-items: center; margin-top: 6px; font-size: 11px; color: var(--muted); }
  .badge { background: #f0ece3; border-radius: 6px; padding: 2px 7px; }
  .stars { color: var(--accent); letter-spacing: 1px; }
  .empty { padding: 60px 20px; text-align: center; color: var(--muted); }
  dialog { border: none; border-radius: 14px; padding: 0; max-width: min(860px, 94vw); width: 100%; }
  dialog::backdrop { background: rgba(0,0,0,.6); }
  dialog video { width: 100%; max-height: 70vh; background: #000; display: block; }
  dialog .info { padding: 12px 16px 16px; font-size: 14px; }
  dialog .info .row { color: var(--muted); font-size: 12px; margin-top: 4px; }
  dialog .x { position: absolute; top: 8px; right: 12px; font-size: 22px; color: #fff; background: none; border: none; cursor: pointer; }
</style>
</head>
<body>
<header>
  <h1>__TITLE__</h1>
  <div class="sub" id="totals"></div>
</header>
<div class="stats" id="chips"></div>
<div class="bar">
  <input id="q" type="search" placeholder="Search descriptions, files, cameras...">
  <select id="fBucket"><option value="">Bucket: all</option></select>
  <select id="fSetting"><option value="">Setting: all</option></select>
  <select id="fSource"><option value="">Source/card: all</option></select>
  <select id="fKeeper">
    <option value="">Keeper: all</option>
    <option value="5">5 stars</option>
    <option value="4">4+ stars</option>
    <option value="3">3+ stars</option>
  </select>
  <select id="sort">
    <option value="date_desc">Newest first</option>
    <option value="date_asc">Oldest first</option>
    <option value="keeper">Best keepers first</option>
  </select>
</div>
<div class="grid" id="grid"></div>
<div class="empty" id="empty" hidden>No clips match those filters.</div>
<dialog id="player">
  <button class="x" onclick="player.close()">&times;</button>
  <video id="vid" controls playsinline></video>
  <div class="info"><div id="vdesc"></div><div class="row" id="vmeta"></div></div>
</dialog>
<script id="catalog" type="application/json">__CATALOG__</script>
<script>
const clips = Object.values(JSON.parse(document.getElementById('catalog').textContent));
const $ = id => document.getElementById(id);
const enc = p => p.split('/').map(encodeURIComponent).join('/');
const clipSrc = c => enc(c.sorted_path || c.play_path || '');
const fmtDur = s => s ? Math.floor(s/60) + ':' + String(Math.round(s%60)).padStart(2,'0') : '';
const fmtDurLong = s => { const h = Math.floor(s/3600); return h ? `${h}h ${Math.round(s%3600/60)}m` : `${Math.floor(s/60)}m ${Math.round(s%60)}s`; };

const uniq = key => [...new Set(clips.map(c => c[key]).filter(v => v !== null && v !== ''))].sort();
for (const [el, key] of [['fBucket','bucket'], ['fSetting','setting'], ['fSource','source_folder']]) {
  for (const v of uniq(key)) {
    const o = document.createElement('option');
    o.value = v; o.textContent = v;
    $(el).appendChild(o);
  }
}

const counts = {};
for (const c of clips) counts[c.bucket] = (counts[c.bucket]||0) + 1;
let chipFilter = '';
function renderChips() {
  $('chips').innerHTML = '';
  const all = document.createElement('span');
  all.className = 'chip' + (chipFilter==='' ? ' active':'');
  all.innerHTML = `All <b>${clips.length}</b>`;
  all.onclick = () => { chipFilter=''; $('fBucket').value=''; renderChips(); render(); };
  $('chips').appendChild(all);
  for (const [t, n] of Object.entries(counts).sort((a,b)=>b[1]-a[1])) {
    const chip = document.createElement('span');
    chip.className = 'chip' + (chipFilter===t ? ' active':'');
    chip.innerHTML = `${t} <b>${n}</b>`;
    chip.onclick = () => { chipFilter=t; $('fBucket').value=t; renderChips(); render(); };
    $('chips').appendChild(chip);
  }
}

function matches(c) {
  const q = $('q').value.trim().toLowerCase();
  if (chipFilter && c.bucket !== chipFilter) return false;
  if ($('fBucket').value && c.bucket !== $('fBucket').value) return false;
  if ($('fSetting').value && c.setting !== $('fSetting').value) return false;
  if ($('fSource').value && c.source_folder !== $('fSource').value) return false;
  const k = $('fKeeper').value;
  if (k && (c.keeper||0) < +k) return false;
  if (q) {
    const hay = `${c.description||''} ${c.file||''} ${c.detail||''} ${c.bucket||''} ${c.source_folder||''}`.toLowerCase();
    if (!hay.includes(q)) return false;
  }
  return true;
}

function render() {
  const list = clips.filter(matches);
  const s = $('sort').value;
  list.sort((a,b) => s==='keeper' ? (b.keeper||0)-(a.keeper||0)
    : s==='date_asc' ? String(a.date).localeCompare(String(b.date))
    : String(b.date).localeCompare(String(a.date)));
  $('totals').textContent = `${list.length} of ${clips.length} clips · ` +
    `${fmtDurLong(list.reduce((t,c)=>t+(c.duration||0),0))} of footage`;
  $('empty').hidden = list.length > 0;
  $('grid').innerHTML = '';
  for (const c of list) {
    const card = document.createElement('div');
    card.className = 'card';
    const stars = '★'.repeat(c.keeper||0) + '☆'.repeat(5-(c.keeper||0));
    card.innerHTML =
      (c.thumb ? `<img loading="lazy" src="${enc(c.thumb)}">` : '') +
      `<div class="body"><div class="desc">${c.description||c.file||''}</div>
       <div class="meta"><span class="badge">${c.bucket}</span>
       <span class="stars">${stars}</span></div>
       <div class="meta"><span>${c.source_folder||''}</span><span>${fmtDur(c.duration)}</span></div></div>`;
    card.onclick = () => {
      $('vid').src = clipSrc(c);
      $('vdesc').textContent = c.description || c.file;
      $('vmeta').textContent = [c.date, c.bucket, c.detail||c.setting,
        c.width&&c.height?`${c.width}×${c.height}`:'', c.hdr?'HDR':'', c.file].filter(Boolean).join(' · ');
      player.showModal();
    };
    $('grid').appendChild(card);
  }
}
player.addEventListener('close', () => { $('vid').pause(); $('vid').src=''; });
for (const id of ['q','fBucket','fSetting','fSource','fKeeper','sort'])
  $(id).addEventListener('input', () => {
    if (id==='fBucket') { chipFilter = $('fBucket').value; renderChips(); }
    render();
  });
renderChips(); render();
</script>
</body>
</html>
"""


def write_dashboard(root, catalog):
    html = DASHBOARD_HTML.replace(
        "__CATALOG__", json.dumps(catalog).replace("</", "<\\/"),
    ).replace("__TITLE__", f"{root.name} - Footage Library")
    (root / "dashboard.html").write_text(html)


# -------------------------------------------------------------------- main

def main():
    ap = argparse.ArgumentParser(
        description="Sort a shoot's footage into a searchable, bucketed library.")
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name in ("sort", "dashboard", "undo"):
        p = sub.add_parser(name)
        p.add_argument("--folder", required=True, help="One project folder (a wedding, a shoot)")
    s = sub.choices["sort"]
    s.add_argument("--preset", default=DEFAULT_PRESET,
                   help=f"Bucket set: {', '.join(PRESETS)} (default: {DEFAULT_PRESET})")
    s.add_argument("--organize", action="store_true",
                   help="Actually file clips into Sorted/<bucket>/<card>/ after "
                        "tagging. Off by default: a plain run never moves an "
                        "original. Every move is logged and undoable.")
    s.add_argument("--by-year", action="store_true",
                   help="Nest Sorted/<bucket>/<year>/ (for multi-year libraries)")
    s.add_argument("--limit", type=int, help="Sort at most N clips (test run)")
    s.add_argument("--mock", action="store_true", help="Fake tags, no API key needed")
    s.add_argument("--yes", action="store_true",
                   help="Skip the interactive confirm before frames are sent to the API")
    s.add_argument("--rescan", action="store_true", help="Re-tag clips already catalogued")
    args = ap.parse_args()
    {"sort": cmd_sort, "dashboard": cmd_dashboard, "undo": cmd_undo}[args.cmd](args)


if __name__ == "__main__":
    main()
