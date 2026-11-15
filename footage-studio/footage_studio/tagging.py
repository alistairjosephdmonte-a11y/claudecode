"""Tagging clips from their preview frames.

Two taggers: DemoTagger (fake tags, never touches the network) and
AnthropicTagger (sends preview frames to Anthropic's API). AnthropicTagger
cannot be constructed without explicit consent, so no code path can send
frames by accident.

NOTE: AnthropicTagger has only been exercised against a stand-in for the API.
Treat it as unproven until a real run passes.

Raw HTTP is used instead of the Anthropic SDK on purpose: the app must run
with nothing installed beyond python3 and ffmpeg.
"""

import base64
import hashlib
import json
import time
import urllib.error
import urllib.request

from . import presets

API_URL = "https://api.anthropic.com/v1/messages"
API_HOST = "api.anthropic.com"
API_VERSION = "2026-10-21"
MODEL = "claude-haiku-5-5"
CONSENT_PHRASE = "send frames"
MAX_ATTEMPTS = 4
RETRYABLE = {408, 409, 429, 500, 502, 503, 504, 529}
FATAL = {401, 402, 403, 404}

PROMPT = """You are tagging one video clip from {context}, using {n} preview \
frame(s) taken across its length.

Choose the closest bucket even if none is perfect; use "other" only as a last \
resort. "keeper" is how likely an editor would select this clip: 5 = in focus, \
stable, a great moment or great light; 1 = blurry, dark, accidental, lens cap \
or test shot. "description" is one line, under 15 words, saying what is \
visible in the clip."""


class ConsentRequired(Exception):
    """Raised when tagging is attempted without the user's confirmation."""


class TaggingError(Exception):
    """This clip could not be tagged; the run can continue."""


class FatalTaggingError(Exception):
    """Tagging cannot continue at all (for example, the key was rejected)."""


def redact(text, secret):
    return text.replace(secret, "[key hidden]") if secret else text


def normalize_tag(raw, buckets):
    bucket = str(raw.get("bucket", "")).strip().lower()
    setting = str(raw.get("setting", "")).strip().lower()
    try:
        keeper = max(1, min(5, int(raw.get("keeper", 3))))
    except (TypeError, ValueError):
        keeper = 3
    return {
        "bucket": bucket if bucket in buckets else presets.FALLBACK_BUCKET,
        "setting": setting if setting in presets.SETTINGS else "unknown",
        "keeper": keeper,
        "description": " ".join(str(raw.get("description") or "").split())[:200],
    }


class DemoTagger:
    """Deterministic fake tags. Makes no network calls."""
    name = "demo"

    def tag(self, clip_name, frames, buckets, preset):
        h = int(hashlib.sha1(clip_name.encode()).hexdigest(), 16)
        return normalize_tag({
            "bucket": buckets[h % len(buckets)],
            "setting": presets.SETTINGS[h % len(presets.SETTINGS)],
            "keeper": (h % 5) + 1,
            "description": f"Demo tag for {clip_name} (not a real description)",
        }, buckets)


class AnthropicTagger:
    name = "ai"

    def __init__(self, api_key, consent, urlopen=None, sleep=time.sleep):
        if consent != CONSENT_PHRASE:
            raise ConsentRequired("Tagging was not confirmed. Nothing was sent.")
        if not api_key or not api_key.strip():
            raise FatalTaggingError("No API key was entered.")
        self._key = api_key.strip()
        self._urlopen = urlopen or urllib.request.urlopen
        self._sleep = sleep

    def build_request(self, frames, buckets, preset):
        content = [{"type": "image",
                    "source": {"type": "base64", "media_type": "image/jpeg",
                               "data": base64.b64encode(frame).decode()}}
                   for frame in frames]
        content.append({"type": "text", "text": PROMPT.format(
            context=presets.CONTEXTS.get(preset, "a video project folder"), n=len(frames))})
        schema = {
            "type": "object",
            "properties": {
                "bucket": {"type": "string", "enum": list(buckets)},
                "setting": {"type": "string", "enum": presets.SETTINGS},
                "keeper": {"type": "integer"},
                "description": {"type": "string"},
            },
            "required": ["bucket", "setting", "keeper", "description"],
            "additionalProperties": False,
        }
        return {
            "model": MODEL,
            # Thinking is on by default and shares this ceiling with the reply.
            "max_tokens": 2000,
            "output_config": {"effort": "low",
                              "format": {"type": "json_schema", "schema": schema}},
            "messages": [{"role": "user", "content": content}],
        }

    def tag(self, clip_name, frames, buckets, preset):
        if not frames:
            raise TaggingError("no preview frames")
        body = json.dumps(self.build_request(frames, buckets, preset)).encode()
        data = self._post(body)
        if data.get("stop_reason") == "refusal":
            raise TaggingError("the AI declined to describe this clip")
        if data.get("stop_reason") == "max_tokens":
            raise TaggingError("the AI's reply was cut short")
        text = "".join(b.get("text", "") for b in data.get("content", []) if b.get("type") == "text")
        try:
            raw = json.loads(text)
            if not isinstance(raw, dict):
                raise ValueError
        except ValueError:
            raise TaggingError("the AI's reply could not be read")
        return normalize_tag(raw, buckets)

    def _post(self, body):
        last = "no reply"
        for attempt in range(MAX_ATTEMPTS):
            request = urllib.request.Request(API_URL, data=body, method="POST", headers={
                "content-type": "application/json",
                "x-api-key": self._key,
                "anthropic-version": API_VERSION,
            })
            delay = 2 ** attempt
            try:
                with self._urlopen(request, timeout=120) as response:
                    return json.loads(response.read())
            except urllib.error.HTTPError as e:
                detail = self._error_message(e)
                if e.code in FATAL:
                    raise FatalTaggingError(self._explain(e.code, detail))
                if e.code not in RETRYABLE:
                    raise TaggingError(f"the AI service rejected this clip ({e.code}): {detail}")
                last = f"the AI service is busy ({e.code})"
                try:
                    delay = max(delay, min(60, int(e.headers.get("retry-after", 0))))
                except (TypeError, ValueError):
                    pass
            except (urllib.error.URLError, TimeoutError, OSError) as e:
                last = redact(f"could not reach {API_HOST} ({getattr(e, 'reason', e)})", self._key)
            except ValueError:
                last = "the AI service sent an unreadable reply"
            if attempt < MAX_ATTEMPTS - 1:
                self._sleep(delay)
        raise TaggingError(last)

    def _error_message(self, error):
        try:
            payload = json.loads(error.read().decode(errors="replace"))
            message = str(payload.get("error", {}).get("message", ""))
        except (ValueError, AttributeError, OSError):
            message = ""
        return redact(message[:200], self._key)

    @staticmethod
    def _explain(code, detail):
        reasons = {
            401: "Anthropic did not accept that API key. Check it and try again.",
            402: "Anthropic reports a billing problem on this account.",
            403: "This API key is not allowed to do that.",
            404: "The AI model was not found for this account.",
        }
        return f"{reasons[code]} {detail}".strip()


def egress_summary(clip_count):
    """Exactly what tagging sends, shown to the user before they confirm."""
    return (
        f"Tagging will send up to 4 small preview frames (JPEG, at most 384 pixels wide) "
        f"from each of {clip_count} clip(s) to Anthropic's API at {API_HOST}, using your "
        f"API key. The videos themselves are never uploaded. Usage is billed by Anthropic "
        f"to the account that owns the key.")
