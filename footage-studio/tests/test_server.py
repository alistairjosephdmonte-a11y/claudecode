"""The app window's server: consent gate, session guard, clip serving, edits."""

import http.client
import json
import threading
import time
import unittest
from unittest import mock

from footage_studio import server, tagging
from tests.helpers import FakeResponse, ProjectCase, snapshot

KEY = "sk-ant-test-SECRET-0123456789"
HEADERS = {"Content-Type": "application/json", "X-Footage-Studio": "1"}


class ServerCase(ProjectCase):
    def setUp(self):
        super().setUp()
        self.app = server.create(0)
        self.port = self.app.server.server_address[1]
        threading.Thread(target=self.app.server.serve_forever, daemon=True).start()
        self.addCleanup(self.app.server.server_close)
        self.addCleanup(self.app.server.shutdown)
        self.cookie = f"{server.COOKIE}={self.app.token}"

    def request(self, method, path, body=None, headers=None, cookie=True, host=None):
        connection = http.client.HTTPConnection("127.0.0.1", self.port, timeout=30)
        send = dict(headers if headers is not None else (HEADERS if method == "POST" else {}))
        if cookie:
            send["Cookie"] = self.cookie
        if host:
            send["Host"] = host
        connection.request(method, path, json.dumps(body) if body is not None else None, send)
        response = connection.getresponse()
        data = response.read()
        connection.close()
        return response, data

    def post(self, path, body=None):
        response, data = self.request("POST", path, body or {})
        return json.loads(data)

    def get_json(self, path):
        return json.loads(self.request("GET", path)[1])

    def open_project(self):
        result = self.post("/api/project", {"folder": str(self.root)})
        self.assertTrue(result["ok"], result)
        return result["project"]

    def run_options(self, **extra):
        return dict({"preset": "wedding", "buckets": ["ceremony", "speeches"], "mode": "demo"}, **extra)

    def wait_for_job(self):
        deadline = time.time() + 120
        while time.time() < deadline:
            job = self.get_json("/api/state")["job"]
            if job["finished"]:
                return job
            time.sleep(0.05)
        self.fail("job did not finish")

    def demo_run(self):
        self.open_project()
        self.assertTrue(self.post("/api/run", self.run_options())["ok"])
        return self.wait_for_job()


class SessionGuard(ServerCase):
    def test_requests_without_the_session_cookie_are_refused(self):
        for path in ("/", "/api/state", "/api/clips", "/manifest.csv", "/media/x", "/library"):
            self.assertEqual(self.request("GET", path, cookie=False)[0].status, 403, path)
        self.assertEqual(self.request("POST", "/api/project", {"folder": "/"}, cookie=False)[0].status, 403)

    def test_posts_from_other_sites_are_refused(self):
        response, _ = self.request("POST", "/api/undo", {}, headers={"Content-Type": "text/plain"})
        self.assertEqual(response.status, 403)

    def test_foreign_host_header_is_refused(self):
        self.assertEqual(self.request("GET", "/api/state", host="evil.example:80")[0].status, 403)

    def test_launch_link_sets_the_cookie_only_with_the_right_token(self):
        response, _ = self.request("GET", f"/?t={self.app.token}", cookie=False)
        self.assertEqual(response.status, 303)
        self.assertIn(self.app.token, response.getheader("Set-Cookie"))
        self.assertIn("HttpOnly", response.getheader("Set-Cookie"))
        self.assertEqual(self.request("GET", "/?t=wrong", cookie=False)[0].status, 403)

    def test_pages_load(self):
        for path in ("/", "/library"):
            response, data = self.request("GET", path)
            self.assertEqual(response.status, 200)
            self.assertIn(b"Footage Studio", data)


class ConsentGate(ServerCase):
    def test_ai_tagging_cannot_start_without_confirmation(self):
        self.open_project()
        before = snapshot(self.home)
        with mock.patch("urllib.request.urlopen", side_effect=AssertionError("frames were sent")) as net:
            for consent in (None, "", True, "yes"):
                result = self.post("/api/run", self.run_options(mode="ai", api_key=KEY, consent=consent))
                self.assertFalse(result["ok"])
                self.assertIn("Nothing was sent", result["error"])
            time.sleep(0.2)
            self.assertFalse(self.get_json("/api/state")["job"]["running"])
            net.assert_not_called()
        self.assertEqual(snapshot(self.home), before)

    def test_preview_says_what_would_be_sent_without_sending(self):
        self.open_project()
        with mock.patch("urllib.request.urlopen", side_effect=AssertionError("frames were sent")):
            result = self.post("/api/preview-run", self.run_options(mode="ai", test_run=True))
        self.assertEqual(result["count"], 10)
        self.assertIn("10 clip(s)", result["egress"])
        self.assertIsNone(self.post("/api/preview-run", self.run_options())["egress"])

    def test_confirmed_run_tags_and_never_stores_the_key(self):
        self.open_project()
        reply = json.dumps({"stop_reason": "end_turn", "content": [{"type": "text", "text": json.dumps(
            {"bucket": "speeches", "setting": "indoor", "keeper": 5, "description": "Best man toast"})}]})
        with mock.patch("urllib.request.urlopen", return_value=FakeResponse(reply.encode())) as net:
            result = self.post("/api/run", self.run_options(
                mode="ai", api_key=KEY, consent=tagging.CONSENT_PHRASE))
            self.assertTrue(result["ok"], result)
            job = self.wait_for_job()
        self.assertIsNone(job["error"])
        self.assertEqual(net.call_count, 9)
        state = self.request("GET", "/api/state")[1]
        self.assertNotIn(KEY.encode(), state)
        for path in self.tmp.rglob("*"):
            if path.is_file():
                self.assertNotIn(KEY.encode(), path.read_bytes(), path)
        clips = self.get_json("/api/clips")["clips"]
        self.assertEqual({c["description"] for c in clips}, {"Best man toast"})


class Library(ServerCase):
    def test_demo_run_through_the_app_leaves_project_untouched(self):
        before = snapshot(self.root)
        job = self.demo_run()
        self.assertIsNone(job["error"])
        self.assertEqual((job["done"], job["total"]), (10, 10))
        self.assertEqual(snapshot(self.root), before)
        data = self.get_json("/api/clips")
        self.assertEqual(len(data["clips"]), 9)
        self.assertEqual(len(data["skipped"]), 1)
        self.assertEqual(data["buckets"], ["ceremony", "speeches", "other"])  # edited buckets are used
        self.assertTrue(all(c["bucket"] in data["buckets"] for c in data["clips"]))
        response, manifest = self.request("GET", "/manifest.csv")
        self.assertEqual(response.status, 200)
        self.assertIn(b"SKIPPED", manifest)

    def test_clips_are_served_by_id_with_range_support(self):
        self.demo_run()
        clip = self.get_json("/api/clips")["clips"][0]
        original = (self.root / clip["rel_path"]).read_bytes()
        response, data = self.request("GET", f"/media/{clip['id']}")
        self.assertEqual((response.status, data), (200, original))
        response, data = self.request("GET", f"/media/{clip['id']}", headers={"Range": "bytes=10-19"})
        self.assertEqual((response.status, data), (206, original[10:20]))
        self.assertEqual(response.getheader("Content-Range"), f"bytes 10-19/{len(original)}")
        response, data = self.request("GET", f"/media/{clip['id']}", headers={"Range": "bytes=-5"})
        self.assertEqual((response.status, data), (206, original[-5:]))
        response, _ = self.request("GET", f"/media/{clip['id']}", headers={"Range": "bytes=99999999-"})
        self.assertEqual(response.status, 416)
        response, data = self.request("GET", f"/thumb/{clip['id']}")
        self.assertTrue(data.startswith(b"\xff\xd8"))

    def test_nothing_outside_the_catalog_can_be_fetched(self):
        self.demo_run()
        (self.tmp / "secret.txt").write_text("private")
        for path in ("/media/../../secret.txt", "/media/..%2F..%2Fsecret.txt", "/media/%2e%2e/secret.txt",
                     "/thumb/../catalog.jsonl", "/media//etc/passwd", "/../secret.txt", "/media/"):
            response, data = self.request("GET", path)
            self.assertEqual(response.status, 404, path)
            self.assertNotIn(b"private", data)

    def test_correcting_a_clip(self):
        self.demo_run()
        clip = self.get_json("/api/clips")["clips"][0]
        result = self.post("/api/clip", {"id": clip["id"], "bucket": "speeches", "setting": "indoor",
                                         "keeper": 5, "description": "Father of the bride speech"})
        self.assertTrue(result["ok"], result)
        saved = [c for c in self.get_json("/api/clips")["clips"] if c["id"] == clip["id"]][0]
        self.assertEqual((saved["bucket"], saved["keeper"], saved["edited"]), ("speeches", 5, True))
        self.assertIn(b"Father of the bride speech", self.request("GET", "/manifest.csv")[1])
        bad = self.post("/api/clip", {"id": clip["id"], "bucket": "not a bucket"})
        self.assertFalse(bad["ok"])

    def test_filing_needs_confirmation_and_undo_restores(self):
        before = snapshot(self.root)
        self.demo_run()
        refused = self.post("/api/file", {})
        self.assertFalse(refused["ok"])
        self.assertEqual(snapshot(self.root), before)
        filed = self.post("/api/file", {"confirm": "file clips"})
        self.assertEqual((filed["filed"], filed["project"]["filed"]), (9, 9))
        clip = self.get_json("/api/clips")["clips"][0]
        self.assertEqual(self.request("GET", f"/media/{clip['id']}")[0].status, 200)
        undone = self.post("/api/undo")
        self.assertEqual((undone["restored"], undone["project"]["filed"]), (10, 0))
        self.assertEqual(snapshot(self.root), before)


if __name__ == "__main__":
    unittest.main()
