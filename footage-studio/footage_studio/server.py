"""The app window: a local web UI served on 127.0.0.1 only.

Security model: the server binds to loopback, checks the Host header (DNS
rebinding), and requires a random per-launch session cookie on everything
except the two instance-handshake endpoints. State-changing requests also
need a custom header, which other websites cannot send. Clips are served by
catalog id, never by path, so there is no path to traverse.

The API key arrives in the body of a run request, is handed to the tagger
for that run, and is never stored, logged or written anywhere.
"""

import json
import mimetypes
import os
import secrets
import subprocess
import sys
import threading
import urllib.request
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from . import __version__, filing, library as lib, media, pipeline, presets, samples, tagging

DEFAULT_PORT = 8765
COOKIE = "footage_studio_session"
APP_ID = "footage-studio"
WEB = Path(__file__).parent / "web"
TEST_RUN_CLIPS = 50


class App:
    def __init__(self):
        self.token = secrets.token_urlsafe(32)
        self.library = None
        self.lock = threading.Lock()
        self.job = {"running": False, "kind": None, "lines": [], "done": 0, "total": 0,
                    "finished": False, "error": None}
        self._stop = threading.Event()
        self.url = None
        self.server = None

    # ---------------------------------------------------------------- jobs

    def log(self, message):
        with self.lock:
            self.job["lines"].append(message)

    def start_job(self, kind, target):
        with self.lock:
            if self.job["running"]:
                return False
            self.job = {"running": True, "kind": kind, "lines": [], "done": 0, "total": 0,
                        "finished": False, "error": None}
            self._stop.clear()

        def work():
            error = None
            try:
                error = target()
            except Exception as e:  # shown to the user rather than lost in a thread
                error = str(e) or e.__class__.__name__
                self.log(f"ERROR: {error}")
            finally:
                with self.lock:
                    self.job.update(running=False, finished=True, error=error)

        threading.Thread(target=work, daemon=True).start()
        return True

    def progress(self, done, total):
        with self.lock:
            self.job.update(done=done, total=total)

    # ------------------------------------------------------------- project

    def project_info(self):
        library = self.library
        if library is None:
            return None
        found = len(media.scan(library.root)) + sum(1 for c in library.clips() if c.get("sorted_path"))
        clips = library.clips()
        return {
            "folder": str(library.root), "name": library.root.name, "found": found,
            "tagged": len(clips), "skipped": len(library.skipped()),
            "demo_tagged": sum(1 for c in clips if c.get("tagger") == "demo"),
            "filed": sum(1 for c in clips if c.get("sorted_path")),
            "preset": library.settings["preset"], "buckets": library.settings["buckets"],
        }

    def state(self):
        with self.lock:
            job = dict(self.job, lines=list(self.job["lines"]))
        return {
            "version": __version__, "presets": presets.PRESETS, "settings": presets.SETTINGS,
            "missing_tools": media.missing_tools(), "can_pick_folder": sys.platform == "darwin",
            "test_run_clips": TEST_RUN_CLIPS, "consent_phrase": tagging.CONSENT_PHRASE,
            "project": self.project_info(), "job": job,
        }


def pick_folder():
    """Native macOS folder chooser. Returns None if cancelled or unavailable."""
    if sys.platform != "darwin":
        return None
    script = 'POSIX path of (choose folder with prompt "Choose the project folder")'
    try:
        out = subprocess.run(["osascript", "-e", script], capture_output=True, text=True, timeout=600)
    except (OSError, subprocess.TimeoutExpired):
        return None
    return out.stdout.strip() or None if out.returncode == 0 else None


def reveal(path):
    if sys.platform == "darwin":
        subprocess.Popen(["open", "-R", str(path)])
    elif os.name == "nt":
        subprocess.Popen(["explorer", f"/select,{path}"])
    else:
        subprocess.Popen(["xdg-open", str(path.parent)])


def make_handler(app):
    class Handler(BaseHTTPRequestHandler):
        protocol_version = "HTTP/1.1"

        def log_message(self, *args):
            pass  # nothing about requests is logged anywhere

        # ------------------------------------------------------- responses

        def _send(self, code, body, content_type, extra=()):
            self.send_response(code)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.send_header("X-Content-Type-Options", "nosniff")
            self.send_header("Referrer-Policy", "no-referrer")
            for name, value in extra:
                self.send_header(name, value)
            self.end_headers()
            if self.command != "HEAD":
                self.wfile.write(body)

        def _json(self, obj, code=200):
            self._send(code, json.dumps(obj).encode(), "application/json")

        def _page(self, name):
            self._send(200, (WEB / name).read_bytes(), "text/html; charset=utf-8", [(
                "Content-Security-Policy",
                "default-src 'self'; style-src 'self' 'unsafe-inline'; "
                "script-src 'self' 'unsafe-inline'; img-src 'self' data:; frame-ancestors 'none'")])

        def _file(self, path):
            size = path.stat().st_size
            mime = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
            start, end, code = 0, size - 1, 200
            header = self.headers.get("Range", "")
            if header.startswith("bytes=") and "," not in header:
                first, _, last = header[6:].partition("-")
                try:
                    if first:
                        start, end = int(first), min(int(last), size - 1) if last else size - 1
                    else:
                        start = max(0, size - int(last))
                    if start > end or start >= size:
                        raise ValueError
                    code = 206
                except ValueError:
                    self._send(416, b"", mime, [("Content-Range", f"bytes */{size}")])
                    return
            length = end - start + 1
            self.send_response(code)
            self.send_header("Content-Type", mime)
            self.send_header("Accept-Ranges", "bytes")
            self.send_header("Content-Length", str(length))
            self.send_header("X-Content-Type-Options", "nosniff")
            if code == 206:
                self.send_header("Content-Range", f"bytes {start}-{end}/{size}")
            self.end_headers()
            with open(path, "rb") as f:
                f.seek(start)
                while length > 0:
                    chunk = f.read(min(1 << 20, length))
                    if not chunk:
                        break
                    try:
                        self.wfile.write(chunk)
                    except (BrokenPipeError, ConnectionResetError):
                        break
                    length -= len(chunk)

        # ----------------------------------------------------------- guard

        def _host_ok(self):
            port = self.server.server_address[1]
            return self.headers.get("Host") in (f"127.0.0.1:{port}", f"localhost:{port}")

        def _authed(self):
            for part in self.headers.get("Cookie", "").split(";"):
                name, _, value = part.strip().partition("=")
                if name == COOKIE and secrets.compare_digest(value, app.token):
                    return True
            return False

        def _body(self):
            try:
                length = int(self.headers.get("Content-Length", 0))
                data = json.loads(self.rfile.read(length) or b"{}") if length < 1 << 20 else {}
            except ValueError:
                data = {}
            return data if isinstance(data, dict) else {}

        def _clip(self, clip_id):
            library = app.library
            entry = library.entries.get(clip_id) if library else None
            return (library, entry) if entry and entry.get("status") == lib.TAGGED else (library, None)

        # ------------------------------------------------------------- GET

        def do_GET(self):
            path, _, query = self.path.partition("?")
            if not self._host_ok():
                return self._json({"error": "forbidden"}, 403)
            if path == "/api/ping":
                return self._json({"app": APP_ID})
            if path == "/" and query.startswith("t="):
                if not secrets.compare_digest(query[2:], app.token):
                    return self._json({"error": "forbidden"}, 403)
                return self._send(303, b"", "text/plain", [
                    ("Set-Cookie", f"{COOKIE}={app.token}; HttpOnly; SameSite=Strict; Path=/"),
                    ("Location", "/")])
            if not self._authed():
                return self._send(403, (
                    b"<!doctype html><title>Footage Studio</title><p>This window is not connected "
                    b"to the running app. Open Footage Studio again from its icon.</p>"),
                    "text/html; charset=utf-8")
            if path == "/":
                return self._page("app.html")
            if path == "/library":
                return self._page("library.html")
            if path == "/api/state":
                return self._json(app.state())
            if path == "/api/clips":
                library = app.library
                if library is None:
                    return self._json({"error": "No project is open."}, 400)
                return self._json({
                    "project": library.root.name, "buckets": library.settings["buckets"],
                    "settings": presets.SETTINGS, "clips": library.clips(),
                    "skipped": library.skipped()})
            if path == "/manifest.csv":
                library = app.library
                if library is None:
                    return self._json({"error": "No project is open."}, 400)
                library.write_manifest()
                return self._send(200, library.manifest_path.read_bytes(), "text/csv; charset=utf-8", [
                    ("Content-Disposition", 'attachment; filename="manifest.csv"')])
            for prefix in ("/media/", "/thumb/"):
                if path.startswith(prefix):
                    library, entry = self._clip(path[len(prefix):])
                    if entry is None:
                        return self._json({"error": "not found"}, 404)
                    target = (library.current_path(entry) if prefix == "/media/"
                              else library.thumb_path(entry["id"]))
                    if not target.is_file():
                        return self._json({"error": "not found"}, 404)
                    return self._file(target)
            self._json({"error": "not found"}, 404)

        # ------------------------------------------------------------ POST

        def do_POST(self):
            path = self.path.partition("?")[0]
            if not self._host_ok():
                return self._json({"error": "forbidden"}, 403)
            data = self._body()
            if path == "/api/reopen":  # a second launch asks the running app to show itself
                webbrowser.open(app.url)
                return self._json({"ok": True})
            if not self._authed() or self.headers.get("X-Footage-Studio") != "1":
                return self._json({"error": "forbidden"}, 403)
            handler = {
                "/api/pick-folder": self._pick_folder, "/api/project": self._open_project,
                "/api/samples": self._samples, "/api/preview-run": self._preview_run,
                "/api/run": self._run, "/api/stop": self._stop_job, "/api/file": self._file_clips,
                "/api/undo": self._undo, "/api/clip": self._edit_clip, "/api/reveal": self._reveal,
                "/api/quit": self._quit,
            }.get(path)
            if handler is None:
                return self._json({"error": "not found"}, 404)
            try:
                handler(data)
            except (ValueError, filing.FilingError, RuntimeError) as e:
                self._json({"ok": False, "error": str(e)})

        def _need_project(self):
            if app.library is None:
                raise ValueError("Choose a project folder first.")
            if app.job["running"]:
                raise ValueError("Something is still running. Wait for it to finish or stop it.")
            return app.library

        def _pick_folder(self, data):
            self._json({"ok": True, "folder": pick_folder()})

        def _open_project(self, data):
            if app.job["running"]:
                raise ValueError("Something is still running. Wait for it to finish or stop it.")
            folder = str(data.get("folder", "")).strip()
            if not folder:
                raise ValueError("Enter the path to a project folder.")
            app.library = lib.Library(folder)
            self._json({"ok": True, "project": app.project_info()})

        def _samples(self, data):
            if app.job["running"]:
                raise ValueError("Something is still running. Wait for it to finish or stop it.")
            folder = lib.app_home() / "samples" / "Sample Wedding"
            samples.make_samples(folder)
            app.library = lib.Library(folder)
            self._json({"ok": True, "project": app.project_info()})

        def _run_options(self, data):
            library = self._need_project()
            preset = data.get("preset")
            if preset not in presets.PRESETS:
                raise ValueError("Choose a footage type.")
            buckets = presets.normalize_buckets(data.get("buckets"))
            if len(buckets) < 2:
                raise ValueError("Add at least one bucket.")
            mode = data.get("mode")
            if mode not in ("demo", "ai"):
                raise ValueError("Choose demo or AI tagging.")
            limit = TEST_RUN_CLIPS if data.get("test_run") else None
            return library, preset, buckets, mode, limit, bool(data.get("rescan"))

        def _preview_run(self, data):
            """How many clips a run would tag, and exactly what it would send."""
            library, _, _, mode, limit, rescan = self._run_options(data)
            todo, _ = pipeline.plan(library, mode, rescan)
            count = min(len(todo), limit) if limit else len(todo)
            self._json({"ok": True, "count": count,
                        "egress": tagging.egress_summary(count) if mode == "ai" else None})

        def _run(self, data):
            library, preset, buckets, mode, limit, rescan = self._run_options(data)
            if media.missing_tools():
                raise ValueError("ffmpeg is not installed.")
            if mode == "demo":
                tagger = tagging.DemoTagger()
            else:
                try:
                    tagger = tagging.AnthropicTagger(str(data.get("api_key", "")), data.get("consent"))
                except (tagging.ConsentRequired, tagging.FatalTaggingError) as e:
                    raise ValueError(str(e))
            library.save_settings(preset, buckets)

            def work():
                summary = pipeline.run_tagging(
                    library, tagger, preset, library.settings["buckets"], limit=limit,
                    rescan=rescan, log=app.log, should_stop=app._stop.is_set,
                    on_progress=app.progress)
                return summary["error"]

            if not app.start_job("tag", work):
                raise ValueError("Something is already running.")
            self._json({"ok": True})

        def _stop_job(self, data):
            app._stop.set()
            self._json({"ok": True})

        def _file_clips(self, data):
            library = self._need_project()
            if data.get("confirm") != "file clips":
                raise ValueError("Filing was not confirmed. Nothing was moved.")
            filed = filing.file_clips(library, log=lambda m: None)
            self._json({"ok": True, "filed": filed, "project": app.project_info()})

        def _undo(self, data):
            library = self._need_project()
            result = filing.undo(library, log=lambda m: None)
            self._json({"ok": True, **result, "project": app.project_info()})

        def _edit_clip(self, data):
            library, entry = self._clip(str(data.get("id", "")))
            if entry is None:
                raise ValueError("That clip is not in the library.")
            if app.job["running"]:
                raise ValueError("Wait for the current run to finish before correcting tags.")
            tag = tagging.normalize_tag(data, library.settings["buckets"])
            if str(data.get("bucket", "")).strip().lower() not in library.settings["buckets"]:
                raise ValueError("Choose one of this project's buckets.")
            updated = {**entry, **tag, "edited": True}
            library.put(updated)
            library.write_manifest()
            self._json({"ok": True, "clip": updated})

        def _reveal(self, data):
            library, entry = self._clip(str(data.get("id", "")))
            if entry is None or not library.current_path(entry).exists():
                raise ValueError("That clip could not be found on disk.")
            reveal(library.current_path(entry))
            self._json({"ok": True})

        def _quit(self, data):
            if app.job["running"]:
                app._stop.set()
            self._json({"ok": True})
            threading.Thread(target=app.server.shutdown, daemon=True).start()

    return Handler


def _already_running(port):
    """If another Footage Studio owns the port, ask it to show its window."""
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    try:
        with opener.open(f"http://127.0.0.1:{port}/api/ping", timeout=2) as r:
            if json.loads(r.read()).get("app") != APP_ID:
                return False
        request = urllib.request.Request(f"http://127.0.0.1:{port}/api/reopen", data=b"{}", method="POST")
        opener.open(request, timeout=5).close()
        return True
    except (OSError, ValueError):
        return False


def create(port=0):
    app = App()
    app.server = ThreadingHTTPServer(("127.0.0.1", port), make_handler(app))
    app.server.daemon_threads = True
    app.url = f"http://127.0.0.1:{app.server.server_address[1]}/?t={app.token}"
    return app


def main(open_browser=True, port=None):
    try:
        app = create(port or DEFAULT_PORT)
    except OSError:
        if port is None and _already_running(DEFAULT_PORT):
            print("Footage Studio is already running; its window has been brought up.")
            return
        app = create(0)
    print(f"Footage Studio is running at {app.url}", flush=True)
    if open_browser:
        webbrowser.open(app.url)
    try:
        app.server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        app.server.server_close()
