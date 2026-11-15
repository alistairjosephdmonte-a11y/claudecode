#!/usr/bin/env python3
"""
Footage Studio - the app window for the footage sorter.

Double-click the launcher (or run `python3 footage_studio.py`) and a clean
app window opens in your browser. No terminal work: pick the project folder,
choose a preset, paste the API key (hidden, never saved), confirm what gets
sent, and watch the tagging happen live. The searchable dashboard it builds
opens right from the app.

Same rules as the command-line sorter: originals are never moved unless you
tick "organize", every move is logged and undoable, and nothing is sent to
the AI until you explicitly allow it in the window.

Needs Python 3.8+ and ffmpeg/ffprobe on PATH. Runs fully offline except the
tagging calls to api.anthropic.com.
"""

import json
import mimetypes
import shutil
import threading
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import footage_sort as fs

PORT_PREFER = 8765
STATE = {"running": False, "lines": [], "done": False, "error": None,
         "root": None, "tagged": 0, "total": 0}


def log(msg):
    STATE["lines"].append(msg)


def run_job(cfg):
    """The sort pipeline, driving the UI log. Mirrors footage_sort.cmd_sort."""
    STATE.update(running=True, lines=[], done=False, error=None, tagged=0, total=0)
    try:
        root = Path(cfg["folder"]).expanduser().resolve()
        if not root.is_dir():
            raise ValueError(f"Not a folder: {root}")
        STATE["root"] = str(root)
        buckets = fs.PRESETS[cfg["preset"]]
        api_key = cfg.get("api_key", "")
        mock = bool(cfg.get("mock"))
        limit = cfg.get("limit")
        organize = bool(cfg.get("organize"))

        catalog = fs.load_catalog(root)
        (root / "_Library" / "thumbs").mkdir(parents=True, exist_ok=True)
        tmpdir = root / "_Library" / ".frames"
        tmpdir.mkdir(exist_ok=True)

        videos = []
        import os
        for dirpath, dirnames, filenames in os.walk(root):
            dirnames[:] = [d for d in dirnames if d not in fs.SKIP_DIRS and not d.startswith(".")]
            for name in filenames:
                if Path(name).suffix.lower() in fs.VIDEO_EXTS:
                    videos.append(Path(dirpath) / name)
        videos.sort()
        todo = []
        for v in videos:
            cid = fs.clip_id(v, root)
            if cid in catalog:
                continue
            todo.append((v, cid))
            if limit and len(todo) >= limit:
                break

        STATE["total"] = len(todo)
        log(f"Project: {root.name}")
        log(f"{len(videos)} videos found, {len(catalog)} already tagged, {len(todo)} to do now.")
        if not todo:
            log("Nothing new to tag.")

        done, skipped = 0, []
        for v, cid in todo:
            meta = fs.probe(v)
            frames = fs.grab_frames(v, meta["duration"], tmpdir)
            if not frames and not mock:
                skipped.append((v.name, "unreadable or unsupported format"))
                log(f"! {v.name}: skipped (can't read it)")
                continue
            try:
                tag = fs.tag_mock(v, buckets) if mock else \
                    fs.tag_with_claude(frames, api_key, buckets, cfg["preset"])
            except Exception as e:
                skipped.append((v.name, str(e)[:120]))
                log(f"! {v.name}: {e}")
                continue
            entry = {"id": cid, "file": v.name, "source_folder": v.parent.name,
                     **meta, **tag, "play_path": str(v.relative_to(root)),
                     "action": "catalogued (original left in place)"}
            thumb = root / "_Library" / "thumbs" / f"{cid}.jpg"
            if fs.save_thumb(v, meta["duration"], thumb):
                entry["thumb"] = f"_Library/thumbs/{cid}.jpg"
            if organize:
                fs.organize_clip(root, entry, v, False)
            catalog[cid] = entry
            done += 1
            STATE["tagged"] = done
            log(f"[{done}/{len(todo)}] {v.name} -> {tag['bucket']} "
                f"(keeper {tag['keeper']}) {tag['description'][:60]}")
            if done % 20 == 0:
                fs.save_catalog(root, catalog)

        if organize:
            filed = 0
            for entry in catalog.values():
                if entry.get("sorted_path"):
                    continue
                original = root / entry.get("play_path", "")
                if original.exists():
                    fs.organize_clip(root, entry, original, False)
                    filed += 1
            if filed:
                log(f"Filed {filed} previously tagged clips into Sorted/.")

        fs.save_catalog(root, catalog)
        fs.write_manifest(root, catalog, skipped)
        fs.write_dashboard(root, catalog)
        shutil.rmtree(tmpdir, ignore_errors=True)
        STATE["done"] = True
        log(f"Done. {len(catalog)} clips in the library"
            + (f", {len(skipped)} skipped (see manifest)." if skipped else "."))
        if not organize:
            log("Originals were not moved.")
    except Exception as e:
        STATE["error"] = str(e)
        log(f"ERROR: {e}")
    finally:
        STATE["running"] = False


def do_undo(folder):
    root = Path(folder).expanduser().resolve()
    logf = root / "_Library" / "moves.jsonl"
    if not logf.exists():
        return "No moves logged - nothing to undo."
    lines = logf.read_text().strip().split("\n")
    undone = 0
    for line in reversed(lines):
        rec = json.loads(line)
        dst, src = Path(rec["to"]), Path(rec["from"])
        if dst.exists() and not src.exists():
            src.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(dst), str(src))
            undone += 1
    logf.unlink()
    catalog = fs.load_catalog(root)
    for entry in catalog.values():
        entry.pop("sorted_path", None)
        if str(entry.get("action", "")).startswith("organized"):
            entry["action"] = "catalogued (original left in place)"
    if catalog:
        fs.save_catalog(root, catalog)
        fs.write_manifest(root, catalog, [])
        fs.write_dashboard(root, catalog)
    return f"Undone: {undone} files moved back."


UI = """<!DOCTYPE html>
<html lang="en"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Footage Studio</title>
<style>
  :root { --ink:#1a1a1a; --muted:#777; --line:#e6e2da; --bg:#faf8f4; --accent:#c2571b; }
  * { box-sizing:border-box; margin:0; }
  body { font-family:-apple-system,"Segoe UI",Roboto,sans-serif; background:var(--bg); color:var(--ink); }
  .wrap { max-width:680px; margin:0 auto; padding:28px 18px 60px; }
  h1 { font-size:26px; letter-spacing:-.5px; }
  .sub { color:var(--muted); font-size:14px; margin:4px 0 18px; }
  .card { background:#fff; border:1px solid var(--line); border-radius:14px; padding:16px 18px; margin-bottom:14px; }
  .card h2 { font-size:15px; margin-bottom:10px; }
  label { display:block; font-size:13px; color:var(--muted); margin:10px 0 4px; }
  input[type=text], input[type=password], select { width:100%; font:inherit; font-size:14px; padding:9px 11px; border:1px solid var(--line); border-radius:8px; }
  .check { display:flex; gap:9px; align-items:flex-start; font-size:13px; margin-top:10px; line-height:1.4; }
  .check input { margin-top:2px; }
  button { font:inherit; font-size:14px; padding:10px 16px; border:none; border-radius:9px; background:var(--ink); color:#fff; cursor:pointer; margin-top:12px; }
  button.ghost { background:#f0ece3; color:var(--ink); }
  button.danger { background:#fff; color:#a33; border:1px solid #e3c6c6; }
  button:disabled { opacity:.4; cursor:default; }
  .row { display:flex; gap:10px; flex-wrap:wrap; }
  pre { background:#171412; color:#d8d2c8; font:12px/1.6 ui-monospace,Menlo,monospace; border-radius:10px; padding:12px 14px; height:220px; overflow:auto; white-space:pre-wrap; }
  .note { font-size:12px; color:var(--muted); margin-top:8px; line-height:1.5; }
  .links a { color:var(--accent); font-size:14px; margin-right:16px; }
  #scanResult { font-size:13px; margin-top:8px; }
</style></head><body><div class="wrap">
<h1>Footage Studio</h1>
<div class="sub">Point it at one project folder - a wedding, a shoot - and it builds a sorted, searchable clip library.</div>

<div class="card">
  <h2>1 · Project folder</h2>
  <label for="folder">Path to the project folder (paste or drag it in)</label>
  <input type="text" id="folder" placeholder="/Volumes/SSD/Sharma x Patel Wedding">
  <label for="preset">Footage type</label>
  <select id="preset"></select>
  <button class="ghost" onclick="scan()">Scan folder</button>
  <div id="scanResult"></div>
</div>

<div class="card">
  <h2>2 · AI tagging</h2>
  <label for="key">Anthropic API key (typed hidden, used for this session only, never saved)</label>
  <input type="password" id="key" autocomplete="off" placeholder="sk-ant-...">
  <label class="check"><input type="checkbox" id="consent">
    <span>I understand tagging sends 4 small preview frames per clip to Anthropic's API
    (never the videos), and that per-use API pricing applies.</span></label>
  <label class="check"><input type="checkbox" id="mock" onchange="mockFlip()">
    <span>Demo mode - no API key, fake tags, to try the app.</span></label>
</div>

<div class="card">
  <h2>3 · Run it</h2>
  <div class="row">
    <button id="btnTest" onclick="run(50)" disabled>Test run · 50 clips</button>
    <button id="btnAll" onclick="run(0)" disabled>Tag the whole project</button>
  </div>
  <label class="check"><input type="checkbox" id="organize">
    <span>Also file clips into Sorted folders afterward. Off = originals stay exactly where they are.
    Every move is logged and can be undone below.</span></label>
</div>

<div class="card" id="progressCard" hidden>
  <h2>Progress</h2>
  <pre id="log"></pre>
</div>

<div class="card links" id="libraryCard" hidden>
  <h2>Your library</h2>
  <a href="/p/dashboard.html" target="_blank">Open the dashboard</a>
  <a href="/p/_Library/manifest.csv" target="_blank">Download the manifest</a>
  <div><button class="danger" onclick="undo()">Undo all filing (restore originals)</button></div>
  <div class="note">Undo only reverses filing done with "organize" ticked.</div>
</div>

<script>
let scanning = null;
fetch('/api/presets').then(r=>r.json()).then(p => {
  const sel = document.getElementById('preset');
  for (const [name, buckets] of Object.entries(p)) {
    const o = document.createElement('option');
    o.value = name; o.textContent = name + ' (' + buckets.length + ' buckets)';
    sel.appendChild(o);
  }
});
function mockFlip() {
  const m = document.getElementById('mock').checked;
  document.getElementById('key').disabled = m;
  document.getElementById('consent').disabled = m;
  document.getElementById('consent').checked = m;
}
async function scan() {
  const folder = document.getElementById('folder').value.trim();
  const r = await fetch('/api/scan', {method:'POST', headers:{'Content-Type':'application/json'},
    body: JSON.stringify({folder})});
  const d = await r.json();
  document.getElementById('scanResult').textContent = d.ok
    ? `Found ${d.videos} videos (${d.catalogued} already tagged).`
    : 'Error: ' + d.error;
  const ready = d.ok;
  document.getElementById('btnTest').disabled = !ready;
  document.getElementById('btnAll').disabled = !ready;
}
async function run(limit) {
  const body = { folder: document.getElementById('folder').value.trim(),
    preset: document.getElementById('preset').value,
    api_key: document.getElementById('key').value,
    consent: document.getElementById('consent').checked,
    mock: document.getElementById('mock').checked,
    organize: document.getElementById('organize').checked,
    limit: limit || null };
  const r = await fetch('/api/run', {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify(body)});
  const d = await r.json();
  if (!d.started) { alert(d.error || 'Could not start'); return; }
  document.getElementById('progressCard').hidden = false;
  poll();
}
async function poll() {
  const r = await fetch('/api/status'); const d = await r.json();
  const el = document.getElementById('log');
  el.textContent = d.lines.join('\\n');
  el.scrollTop = el.scrollHeight;
  if (d.done) document.getElementById('libraryCard').hidden = false;
  if (d.running || (!d.done && !d.error)) setTimeout(poll, 1000);
}
async function undo() {
  if (!confirm('Move every filed clip back to its original folder?')) return;
  const r = await fetch('/api/undo', {method:'POST', headers:{'Content-Type':'application/json'},
    body: JSON.stringify({folder: document.getElementById('folder').value.trim()})});
  const d = await r.json();
  alert(d.result);
}
</script>
</div></body></html>
"""


class Handler(BaseHTTPRequestHandler):
    def _json(self, obj, code=200):
        body = json.dumps(obj).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _body(self):
        n = int(self.headers.get("Content-Length", 0))
        try:
            return json.loads(self.rfile.read(n) or b"{}")
        except json.JSONDecodeError:
            return {}

    def log_message(self, *a):  # quiet
        pass

    def do_GET(self):
        path = self.path.split("?")[0]
        if path == "/":
            body = UI.encode()
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        elif path == "/api/presets":
            self._json(fs.PRESETS)
        elif path == "/api/status":
            self._json(STATE)
        elif path.startswith("/p/"):
            self._serve_project_file(path[3:])
        else:
            self._json({"error": "not found"}, 404)

    def _serve_project_file(self, rel):
        root = STATE.get("root")
        if not root:
            self._json({"error": "no project loaded"}, 400)
            return
        import urllib.parse
        target = (Path(root) / urllib.parse.unquote(rel)).resolve()
        if not str(target).startswith(str(Path(root).resolve())) or not target.is_file():
            self._json({"error": "not found"}, 404)
            return
        mime = mimetypes.guess_type(str(target))[0] or "application/octet-stream"
        size = target.stat().st_size
        start, end = 0, size - 1
        code = 200
        rng = self.headers.get("Range")
        if rng and rng.startswith("bytes="):
            try:
                a, _, b = rng[6:].partition("-")
                start = int(a) if a else 0
                end = int(b) if b else size - 1
                code = 206
            except ValueError:
                pass
        length = end - start + 1
        self.send_response(code)
        self.send_header("Content-Type", mime)
        self.send_header("Accept-Ranges", "bytes")
        self.send_header("Content-Length", str(length))
        if code == 206:
            self.send_header("Content-Range", f"bytes {start}-{end}/{size}")
        self.end_headers()
        with open(target, "rb") as f:
            f.seek(start)
            remaining = length
            while remaining > 0:
                chunk = f.read(min(1 << 20, remaining))
                if not chunk:
                    break
                try:
                    self.wfile.write(chunk)
                except (BrokenPipeError, ConnectionResetError):
                    break
                remaining -= len(chunk)

    def do_POST(self):
        path = self.path.split("?")[0]
        data = self._body()
        if path == "/api/scan":
            root = Path(data.get("folder", "")).expanduser().resolve()
            if not root.is_dir():
                self._json({"ok": False, "error": f"not a folder: {root}"})
                return
            import os
            count = 0
            for dirpath, dirnames, filenames in os.walk(root):
                dirnames[:] = [d for d in dirnames if d not in fs.SKIP_DIRS and not d.startswith(".")]
                count += sum(1 for n in filenames if Path(n).suffix.lower() in fs.VIDEO_EXTS)
            STATE["root"] = str(root)
            self._json({"ok": True, "videos": count,
                        "catalogued": len(fs.load_catalog(root))})
        elif path == "/api/run":
            if STATE["running"]:
                self._json({"started": False, "error": "a run is already going"})
                return
            if not data.get("mock"):
                if not data.get("api_key"):
                    self._json({"started": False, "error": "no API key (or tick Demo mode)"})
                    return
                if not data.get("consent"):
                    self._json({"started": False, "error": "please confirm what tagging sends"})
                    return
            if data.get("preset") not in fs.PRESETS:
                self._json({"started": False, "error": "unknown preset"})
                return
            fs.check_ffmpeg()
            t = threading.Thread(target=run_job, args=(data,), daemon=True)
            t.start()
            self._json({"started": True})
        elif path == "/api/undo":
            self._json({"result": do_undo(data.get("folder", ""))})
        else:
            self._json({"error": "not found"}, 404)


def main():
    fs.check_ffmpeg()
    for port in (PORT_PREFER, 0):
        try:
            server = ThreadingHTTPServer(("127.0.0.1", port), Handler)
            break
        except OSError:
            continue
    port = server.server_address[1]
    url = f"http://127.0.0.1:{port}"
    print(f"Footage Studio is running at {url}")
    print("Close this window to stop the app.")
    webbrowser.open(url)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
