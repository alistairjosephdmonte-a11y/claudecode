"""Consent, the API key, and the shape of what is sent to the AI service."""

import io
import json
import unittest
import urllib.error

from footage_studio import pipeline, presets, tagging
from footage_studio.library import Library
from tests.helpers import FakeResponse, ProjectCase

BUCKETS = presets.PRESETS["wedding"]
KEY = "sk-ant-test-SECRET-0123456789"
FRAME = b"\xff\xd8fake-jpeg"


def reply(tag, stop_reason="end_turn"):
    return FakeResponse(json.dumps({
        "stop_reason": stop_reason,
        "content": [{"type": "thinking", "thinking": ""}, {"type": "text", "text": json.dumps(tag)}],
    }).encode())


def http_error(code, message="nope", headers=None):
    body = io.BytesIO(json.dumps({"error": {"message": message}}).encode())
    return urllib.error.HTTPError(tagging.API_URL, code, "error", headers or {}, body)


class Recorder:
    def __init__(self, *results):
        self.results = list(results)
        self.requests = []

    def __call__(self, request, timeout=None):
        self.requests.append(request)
        result = self.results.pop(0) if len(self.results) > 1 else self.results[0]
        if isinstance(result, Exception):
            raise result
        return result


GOOD = {"bucket": "ceremony", "setting": "outdoor", "keeper": 4, "description": "Couple at the altar"}


class Consent(unittest.TestCase):
    def test_tagger_cannot_exist_without_consent(self):
        for consent in (None, "", True, "yes", "send"):
            with self.assertRaises(tagging.ConsentRequired):
                tagging.AnthropicTagger(KEY, consent, urlopen=Recorder(reply(GOOD)))

    def test_tagger_needs_a_key(self):
        with self.assertRaises(tagging.FatalTaggingError):
            tagging.AnthropicTagger("  ", tagging.CONSENT_PHRASE)

    def test_consent_text_has_no_cost_numbers(self):
        text = tagging.egress_summary(120)
        self.assertNotRegex(text, r"[$€£]|\bcents?\b|\bUSD\b")
        self.assertIn("api.anthropic.com", text)
        self.assertIn("never uploaded", text)


class Request(unittest.TestCase):
    def setUp(self):
        self.net = Recorder(reply(GOOD))
        self.tagger = tagging.AnthropicTagger(KEY, tagging.CONSENT_PHRASE, urlopen=self.net,
                                              sleep=lambda s: None)

    def test_sends_only_frames_and_prompt_and_parses_reply(self):
        tag = self.tagger.tag("C0001.mp4", [FRAME] * 4, BUCKETS, "wedding")
        self.assertEqual(tag, GOOD)
        request = self.net.requests[0]
        self.assertEqual(request.full_url, "https://api.anthropic.com/v1/messages")
        self.assertEqual(request.get_header("X-api-key"), KEY)
        body = json.loads(request.data)
        self.assertNotIn(KEY, request.data.decode())
        self.assertNotIn("C0001", request.data.decode())  # file names stay on the machine
        self.assertEqual(body["model"], "claude-haiku-5-5")
        content = body["messages"][0]["content"]
        self.assertEqual([c["type"] for c in content], ["image"] * 4 + ["text"])
        self.assertEqual(body["output_config"]["format"]["schema"]["properties"]["bucket"]["enum"], BUCKETS)

    def test_out_of_range_values_are_clamped(self):
        self.net.results = [reply({"bucket": "Nonsense", "setting": "underwater", "keeper": 11,
                                   "description": "x" * 500})]
        tag = self.tagger.tag("a.mp4", [FRAME], BUCKETS, "wedding")
        self.assertEqual((tag["bucket"], tag["setting"], tag["keeper"]), ("other", "unknown", 5))
        self.assertEqual(len(tag["description"]), 200)

    def test_refusal_and_garbage_fail_only_that_clip(self):
        for result in (reply(GOOD, "refusal"), reply(GOOD, "max_tokens"),
                       FakeResponse(b'{"content": [{"type": "text", "text": "not json"}]}')):
            self.net.results = [result]
            with self.assertRaises(tagging.TaggingError):
                self.tagger.tag("a.mp4", [FRAME], BUCKETS, "wedding")

    def test_busy_service_is_retried(self):
        self.net.results = [http_error(529), http_error(429, headers={"retry-after": "1"}), reply(GOOD)]
        self.assertEqual(self.tagger.tag("a.mp4", [FRAME], BUCKETS, "wedding"), GOOD)
        self.assertEqual(len(self.net.requests), 3)

    def test_rejected_key_is_fatal_and_never_echoed(self):
        self.net.results = [http_error(401, f"invalid x-api-key {KEY}")]
        with self.assertRaises(tagging.FatalTaggingError) as caught:
            self.tagger.tag("a.mp4", [FRAME], BUCKETS, "wedding")
        self.assertNotIn(KEY, str(caught.exception))
        self.assertEqual(len(self.net.requests), 1)


class RunWithFakeService(ProjectCase):
    def run_ai(self, *results):
        net = Recorder(*results)
        tagger = tagging.AnthropicTagger(KEY, tagging.CONSENT_PHRASE, urlopen=net, sleep=lambda s: None)
        library = Library(self.root)
        lines = []
        summary = pipeline.run_tagging(library, tagger, "wedding", BUCKETS, log=lines.append)
        return library, summary, net, lines

    def test_full_run_and_key_is_never_written_anywhere(self):
        library, summary, net, lines = self.run_ai(reply(GOOD))
        self.assertEqual(summary["tagged"], 9)
        self.assertEqual(len(net.requests), 9)  # the broken clip is never sent
        self.assertTrue(all(c["tagger"] == "ai" for c in library.clips()))
        self.assertNotIn(KEY, "\n".join(lines))
        for path in list(self.tmp.rglob("*")):
            if path.is_file():
                self.assertNotIn(KEY.encode(), path.read_bytes(), path)

    def test_rejected_key_stops_the_run_at_once(self):
        _, summary, net, _ = self.run_ai(http_error(401))
        self.assertIn("API key", summary["error"])
        self.assertEqual(len(net.requests), 1)

    def test_repeated_failures_stop_the_run(self):
        _, summary, net, _ = self.run_ai(http_error(400))
        self.assertIn("in a row", summary["error"])
        self.assertLess(len(net.requests), 9)


if __name__ == "__main__":
    unittest.main()
