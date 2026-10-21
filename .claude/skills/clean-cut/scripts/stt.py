#!/usr/bin/env python3
"""One transcription door for every script in this pack.

    from stt import transcribe, el_key
    J = transcribe("audio.flac", diarize=False, keyterms=None)     # -> {"words": [{"text", "start", "end", "type": "word", "speaker_id"}], "_engine": ...}

    python3 stt.py <audio or video file> [out.json] [--diarize]    # command-line use
    python3 stt.py --key                                           # is there an ElevenLabs key? (never prints it)

The result always has the ElevenLabs Scribe shape, whichever engine ran, so nothing downstream changes.

Engine = the "transcriber" answer in ~/.claude/creator-profile/profile.json (or $STT_ENGINE):
  elevenlabs  (recommended) ElevenLabs Scribe through the API. Most accurate words AND word edges, speaker labels,
              about $0.22 per hour of audio. Needs ELEVENLABS_API_KEY in the environment or the shell profile.
  local       Runs on this computer through HyperFrames (`npx hyperframes transcribe`: Parakeet if installed, else
              whisper.cpp). Free and private. The audio is split at its pauses and each part transcribed on its own
              (whisper, given a whole recording, drops a sentence after a long pause and folds a false start into the take
              after it). Word edges are a little looser, a repeat said without any pause can still come back once, so the
              tight cut needs a closer look, and there are NO speaker labels (long calls with several people are harder to
              read). Sounds (music, a cough) come back as "audio_event". The first run downloads the speech model once
              (about 500 MB); pass progress= to show it.
Language: transcribe() uses the creator's setting (Studio config "language", else the profile's, else "en"; "auto" = detect).
Failures raise STTError (a SystemExit: uncaught it exits with the plain message, like before) with .kind and .fix.
No third-party packages: the API call uses Python's own urllib.
The key is never printed and never asked for in chat: the creator adds the export line to their shell profile themselves.
"""
import json, os, re, subprocess, sys, tempfile, threading, time, uuid, wave
from urllib import request as _rq, error as _er

HOME = os.path.expanduser("~")
PROFILE = os.path.expanduser(os.environ.get("CREATOR_PROFILE_DIR", "~/.claude/creator-profile")) + "/profile.json"
RC = (".zshrc", ".zprofile", ".zshenv", ".bash_profile", ".bashrc", ".profile")     # in this order: the first one with a key wins
MODELS = os.path.join(HOME, ".cache", "hyperframes", "whisper", "models")           # where HyperFrames keeps the on-device speech model
MODEL_BYTES = {"small.en": 487614201, "small": 487601967}
DOWNLOADING = "Downloading the speech model (one time, about 500 MB)"
CONFIG = "config"                                                                    # transcribe(language=CONFIG): the creator's setting


class STTError(SystemExit):
    """A transcription failure in plain words. kind: no_key | bad_key | no_credit | network | api | local.
    fix: one sentence the creator can act on. Uncaught, it exits with the message (as sys.exit did)."""
    def __init__(self, msg, kind="api", fix=""):
        SystemExit.__init__(self, msg)
        self.kind, self.fix = kind, fix

    def __str__(self):
        return str(self.args[0]) if self.args else ""


def _read(p):
    """A JSON settings file as a dict: {} when it is missing, broken or not an object (e.g. [1] or "x")."""
    try:
        with open(p) as f:
            d = json.load(f)
    except (OSError, ValueError):
        return {}
    return d if isinstance(d, dict) else {}


def profile():
    return _read(PROFILE)


def studio_config():
    return _read(os.path.join(os.path.expanduser(os.environ.get("STUDIO_HOME", "~/edit-studio")), "config.json"))


def engine():
    return (os.environ.get("STT_ENGINE") or profile().get("transcriber") or "elevenlabs").lower()


def default_language():
    """The language to transcribe in: the Studio's setting (config.json "language"), else the creator profile's "language",
    else "en". "auto" = None (the transcriber detects it; accented English can be misread that way, so "en" is the default)."""
    for src in (studio_config(), profile()):
        v = src.get("language")
        if isinstance(v, str) and v.strip():
            v = v.strip().lower()
            if v == "auto":
                return None
            if re.fullmatch(r"[a-z]{2,3}", v):
                return v
    return "en"


def _key_value(raw):
    """The value of an ELEVENLABS_API_KEY= assignment: surrounding quotes stripped, or (unquoted) up to the first space,
    ';' or '#' (so `ELEVENLABS_API_KEY=sk_abc; export ELEVENLABS_API_KEY` and `...=sk_abc #mine` both give sk_abc)."""
    v = raw.strip()
    if v[:1] in ("'", '"'):
        end = v.find(v[0], 1)
        v = v[1:end] if end > 0 else v[1:]
    else:
        v = re.split(r"[\s;#]", v, maxsplit=1)[0]
    return v.strip()


_RESOLVED, KEY_NOTE = {}, []


def _from_command(line, rc):
    """A key the shell profile sets with a command, e.g. export ELEVENLABS_API_KEY=$(security find-generic-password -s el -w):
    run that one line in the profile's own shell (zsh for ~/.z*, else bash), then, if it gave nothing (it uses something set
    earlier in the file), the whole file, as a new Terminal window would. At most 10 s each, nothing shown, once per run.
    Returns the value, or "" (and KEY_NOTE says why)."""
    if (line, rc) in _RESOLVED:
        return _RESOLVED[(line, rc)]
    sh = "/bin/zsh" if rc.startswith(".z") else "/bin/bash"
    v = ""
    for code in (line.strip(), "source " + _q(os.path.join(HOME, rc)) + " >/dev/null 2>&1"):
        try:
            r = subprocess.run([sh, "-c", code + "\nprintf %s \"$ELEVENLABS_API_KEY\""], stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
                               stderr=subprocess.DEVNULL, text=True, timeout=10, env=dict(os.environ, ELEVENLABS_API_KEY=""))
            v = r.stdout.strip()
        except (OSError, subprocess.TimeoutExpired, UnicodeDecodeError):
            v = ""
        if v and not v.startswith(("$", "`")):
            break
        v = ""
    if not v:
        KEY_NOTE.append(f"~/{rc} sets ELEVENLABS_API_KEY with a command, and it gave no key here")
    _RESOLVED[(line, rc)] = v
    return v


def _q(p):
    return "'" + p.replace("'", "'\\''") + "'"


def key_source():
    """Where the ElevenLabs key comes from, as (where, key) or (None, ""). Never printed. The app's "key found" must agree:
    it follows this exact rule (same file order, last line per file, first file with a value wins) or runs `stt.py --key`
    (exit 0 = a key). The rule:
      1. a non-empty ELEVENLABS_API_KEY in the environment;
      2. else, in the order ~/.zshrc ~/.zprofile ~/.zshenv ~/.bash_profile ~/.bashrc ~/.profile, the first file whose LAST
         `ELEVENLABS_API_KEY=` line (`export ` optional, at the start of the line, quotes optional) has a non-empty value.
    The value is the quoted text, or (unquoted) everything up to the first space, ';' or '#'.
    An empty value (export ELEVENLABS_API_KEY="") counts as no key. A value set by a command ($(...) or `...`, not in single
    quotes) is worked out by running that line (_from_command); if it gives nothing, that file has no key."""
    k = _key_value(os.environ.get("ELEVENLABS_API_KEY") or "")
    if k:
        return "environment", k
    for rc in RC:
        p = os.path.join(HOME, rc)
        if not os.path.exists(p):
            continue
        v, last = None, None
        try:
            for line in open(p, errors="ignore"):
                m = re.match(r"\s*(?:export\s+)?ELEVENLABS_API_KEY=(.*)", line)
                if m:
                    v, last = _key_value(m.group(1)), line
        except OSError:
            continue
        if v and v.startswith(("$", "`")) and not last.split("=", 1)[1].lstrip().startswith("'"):
            v = _from_command(last, rc)
        if v:
            return "~/" + rc, v
    return None, ""


def el_key(required=True):
    """ElevenLabs key from the environment or an `ELEVENLABS_API_KEY=` line in the shell profile (see key_source). Never printed."""
    k = key_source()[1]
    if not k and required:
        raise STTError("ELEVENLABS_API_KEY not found (environment or shell profile" + "".join(f"; {n}" for n in KEY_NOTE) + "). Ask the creator to add\n"
                       "  export ELEVENLABS_API_KEY=\"...\"\nto ~/.zshrc themselves (never ask for the key in chat), "
                       "or switch to local transcription: python3 setup/apply_profile.py --set transcriber=local",
                       "no_key", "Add your ElevenLabs key to your shell profile (ask Claude how in the chat), or switch to on-device transcription.")
    return k


def _ssl():
    import ssl
    c = ssl.create_default_context()
    for f in ("/etc/ssl/cert.pem",):                                     # macOS's certificates: python.org's Python ships with none
        if os.path.exists(f):
            try:
                c.load_verify_locations(f)
            except Exception:
                pass
    try:
        import certifi
        c.load_verify_locations(certifi.where())
    except Exception:
        pass
    return c


def _form(fields, path):
    """multipart/form-data body: the fields, then the audio file."""
    b = uuid.uuid4().hex
    out = []
    for k, v in fields:
        out.append(f"--{b}\r\nContent-Disposition: form-data; name=\"{k}\"\r\n\r\n{v}\r\n".encode())
    name = os.path.basename(path).replace('"', "")
    out.append(f"--{b}\r\nContent-Disposition: form-data; name=\"file\"; filename=\"{name}\"\r\nContent-Type: application/octet-stream\r\n\r\n".encode())
    out.append(open(path, "rb").read())
    out.append(f"\r\n--{b}--\r\n".encode())
    return b"".join(out), "multipart/form-data; boundary=" + b


def _elevenlabs(audio, diarize, keyterms, language, events, speakers=None, progress=None):
    key = el_key()
    data = {"timestamps_granularity": "word",
            "tag_audio_events": "true" if events else "false", "diarize": "true" if diarize else "false"}
    if language:
        data["language_code"] = language                                # None = let ElevenLabs detect the language
    if speakers:
        data["num_speakers"] = str(int(speakers))
    if progress:
        progress("Transcribing with ElevenLabs")
    last = ""
    for model in ("scribe_v2", "scribe_v1"):
        d = dict(data, model_id=model)
        fields = list(d.items()) + ([("keyterms", k) for k in keyterms] if keyterms and model == "scribe_v2" else [])
        body, ctype = _form(fields, audio)
        req = _rq.Request("https://api.elevenlabs.io/v1/speech-to-text", data=body, method="POST",
                          headers={"xi-api-key": key, "Content-Type": ctype, "Accept": "application/json"})
        try:
            with _rq.urlopen(req, timeout=3600, context=_ssl()) as r:
                J = json.loads(r.read().decode("utf-8"))
            if not isinstance(J, dict):
                raise ValueError("not a JSON object")
            J["_engine"] = "elevenlabs/" + model
            return J
        except _er.HTTPError as e:
            code = e.code
            text = e.read().decode("utf-8", "ignore")[:300]
            print(model, code, text)
            low = text.lower()
            if code == 402 or "quota" in low or "credit" in low:       # ElevenLabs answers 401 "quota_exceeded" when the credit runs out
                raise STTError("ElevenLabs is out of credit for this month.", "no_credit",
                               "Top up your ElevenLabs plan, or switch to on-device transcription.")
            if code in (401, 403):                                      # a bad or under-permissioned key fails the same way on every model
                raise STTError("ElevenLabs rejected the key. Ask the creator to check the key in their shell profile has Speech to Text access.",
                               "bad_key", "Check your ElevenLabs key has Speech to Text access, or switch to on-device transcription.")
            last = f"ElevenLabs answered {code}: {text[:200]}"
        except ValueError:                                              # it answered, but not with a transcript we can read
            raise STTError("ElevenLabs sent back an answer that couldn't be read.", "api",
                           "Ask Claude to try again in a few minutes.")
        except (_er.URLError, OSError) as e:                            # no internet, a timeout
            raise STTError(f"Couldn't reach ElevenLabs ({getattr(e, 'reason', e)}).", "network",
                           "Check the internet connection, then ask Claude to try again.")
    raise STTError(last or "ElevenLabs transcription failed.", "api", "Ask Claude to try again in a few minutes.")


PAUSE = 0.5          # on-device: a pause of this many seconds (or more) splits the audio into parts, each transcribed on its own
PART_MAX = 25.0      # a part longer than this (seconds) is split again at its longest pause
JOBS = 3             # parts transcribed at the same time


def _hf_exe():
    """HyperFrames' own command, found once through npx (which installs it the first time), so each part skips npx's start-up
    and its look at the npm registry. None = run it through npx each time."""
    try:
        r = subprocess.run(["npx", "-y", "-p", "hyperframes", "-c", "command -v hyperframes"], stdout=subprocess.PIPE,
                           stderr=subprocess.DEVNULL, stdin=subprocess.DEVNULL, text=True, timeout=300)
        p = (r.stdout.strip().splitlines() or [""])[-1].strip()
        return [p] if r.returncode == 0 and os.path.isabs(p) and os.access(p, os.X_OK) else None
    except (OSError, subprocess.TimeoutExpired, UnicodeDecodeError):
        return None


def _hf(audio, language, say, model=None, stop=None, exe=None):
    """One run of HyperFrames' transcriber on one file -> ([{text, start, end}], meta). Writes transcript.json into a temp dir.
    say(step, pct, eta_s) hears about the one-time model download (HyperFrames' --json progress lines, or the model file
    growing in its cache for versions that don't report it). stop: a threading.Event that ends the run (another part failed).
    exe: HyperFrames' command (_hf_exe()), else npx."""
    model = model or ("small.en" if language == "en" else "small")
    fix = "Ask Claude to check on-device transcription (npx hyperframes doctor), or switch to ElevenLabs."
    with tempfile.TemporaryDirectory() as d:
        cmd = (exe or ["npx", "-y", "hyperframes"]) + ["transcribe", os.path.abspath(audio), "--json", "-d", d]
        if language is None:
            cmd += ["--model", model]                                    # detecting the language needs the multilingual model
        elif model != "small.en":
            cmd += ["--language", language, "--model", model]
        try:
            p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.DEVNULL,
                                 text=True, encoding="utf-8", errors="replace")
        except FileNotFoundError:
            raise STTError("On-device transcription needs Node.js (npx), which isn't installed.", "local", fix)
        out, err, st = [], [], {"events": False, "dl": None}

        def pump(stream, buf, events):
            for line in stream:
                buf.append(line)
                if not events:
                    continue
                try:                                                     # nothing here may end the loop: an undrained pipe
                    ev = json.loads(line)                                # would stall HyperFrames (and this script) for good
                    if isinstance(ev, dict) and ev.get("type") == "progress" and ev.get("phase") == "download":
                        st["events"] = True
                        got, tot = ev.get("receivedBytes") or 0, ev.get("totalBytes") or MODEL_BYTES.get(ev.get("model"), 0)
                        if st["dl"] is None:
                            st["dl"] = (time.time(), got)
                        t0, g0 = st["dl"]
                        rate = (got - g0) / max(0.1, time.time() - t0)
                        say(DOWNLOADING, 100 * got / tot if tot else None, (tot - got) / rate if tot and rate > 0 else None)
                except Exception:
                    continue
        th = [threading.Thread(target=pump, args=(p.stdout, out, False), daemon=True),
              threading.Thread(target=pump, args=(p.stderr, err, True), daemon=True)]
        for t in th:
            t.start()
        seen, look = None, 0.0
        try:
            while p.poll() is None:
                time.sleep(0.1)
                if stop is not None and stop.is_set():
                    raise STTError("On-device transcription was stopped.", "local", fix)
                if time.time() - look < 1 or st["events"] or os.path.exists(os.path.join(MODELS, f"ggml-{model}.bin")):
                    continue
                look = time.time()
                try:                                                     # older HyperFrames: watch ggml-<model>.bin[.<pid>.<id>].tmp grow
                    tmp = [os.path.join(MODELS, f) for f in os.listdir(MODELS) if f.startswith(f"ggml-{model}.bin") and f.endswith(".tmp")]
                    tmp = [f for f in tmp if time.time() - os.path.getmtime(f) < 15]
                    got = sum(os.path.getsize(f) for f in tmp)
                except OSError:
                    got = 0
                if got:
                    tot = MODEL_BYTES.get(model, 500e6)
                    if seen is None:
                        seen = (time.time(), got)
                    rate = (got - seen[1]) / max(0.1, time.time() - seen[0])
                    say(DOWNLOADING, min(99, 100 * got / tot), (tot - got) / rate if rate > 0 else None)
        finally:
            if p.poll() is None:                                         # left early (Ctrl-C, an error, another part failed):
                p.terminate()                                            # don't leave npx running (npm passes SIGTERM on to the
                try:                                                     # transcriber it started)
                    p.wait(5)
                except subprocess.TimeoutExpired:
                    p.kill()
        for t in th:
            t.join(5)
        tp = f"{d}/transcript.json"
        meta = {}
        for line in reversed("".join(out).strip().splitlines()):     # the last JSON object HyperFrames printed is its result
            try:
                m = json.loads(line)
            except ValueError:
                continue
            if isinstance(m, dict):
                meta = m
                break
        if p.returncode != 0 or not os.path.exists(tp):
            why = str(meta.get("error") or "") or "".join(err or out).strip()[-600:]
            print("local transcription failed:\n" + "".join(err or out)[-1200:] + "\nCheck `npx hyperframes doctor`, or use ElevenLabs.")
            raise STTError("On-device transcription failed: " + (why.splitlines()[-1] if why else f"exit {p.returncode}"), "local", fix)
        try:
            W = json.load(open(tp, encoding="utf-8"))
        except ValueError:
            raise STTError("On-device transcription failed: HyperFrames wrote a transcript that couldn't be read.", "local", fix)
    return (W if isinstance(W, list) else []), meta


def _levels(audio):
    """Loudness per 10 ms in dBFS (ffmpeg's astats, so no Python packages are needed); [] when it can't be measured."""
    af = ("aresample=16000,asetnsamples=n=160:p=0,astats=metadata=1:reset=1%s,"
          "ametadata=mode=print:key=lavfi.astats.Overall.RMS_level:file=-")
    for extra in (":measure_overall=RMS_level:measure_perchannel=none", ""):         # an older ffmpeg has no measure_ options
        try:
            r = subprocess.run(["ffmpeg", "-v", "error", "-nostdin", "-i", audio, "-vn", "-ac", "1", "-af", af % extra, "-f", "null", "-"],
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, errors="replace")
        except OSError:
            return []
        if r.returncode == 0:
            break
    else:
        return []
    lv = []
    for line in r.stdout.splitlines():
        if line.startswith("lavfi.astats.Overall.RMS_level="):
            try:
                v = float(line.split("=", 1)[1])
            except ValueError:
                v = -100.0
            lv.append(v if v > -100 else -100.0)                         # digital silence (-inf) and nan count as -100
    return lv


def _quiet_level(lv):
    """Quieter than this (dBFS) = a pause: the room's noise floor (its quietest 5%) + 9 dB, kept between -46 and -30, the
    rough cut's own word-edge level (studio_cut.py)."""
    srt = sorted(lv)
    floor = srt[len(srt) // 20] if len(srt) > 100 else -80.0
    return min(-30.0, max(-46.0, floor + 9))


def _parts(lv, pause=PAUSE, pad=0.2, longest=PART_MAX):
    """Where the speech is, as [(start, end)] seconds: the stretches of sound, split at every pause of `pause` seconds or more,
    each with up to `pad` s of the quiet around it (never past the middle of a pause). A stretch longer than `longest` is
    split at its longest pause; anything shorter than 0.1 s (a click) is left out. Sound = above the cut's word-edge level
    (_quiet_level); quieter speech it misses (a whisper, someone further from the mic: more than 15 dB above the room's noise
    floor for 0.3 s or more) gets parts of its own, so it is transcribed too."""
    if not lv:
        return []
    n, srt = len(lv), sorted(lv)
    th = _quiet_level(lv)
    low = min(th, (srt[n // 20] if n > 100 else -80.0) + 15)

    def groups(level):
        runs, i = [], 0
        while i < n:
            if lv[i] <= level:
                i += 1
                continue
            j = i
            while j < n and lv[j] > level:
                j += 1
            runs.append((i, j))
            i = j
        out = []
        for r in runs:
            if out and r[0] - out[-1][-1][1] < pause * 100:
                out[-1].append(r)
            else:
                out.append([r])
        return out

    def split(g):
        if g[-1][1] - g[0][0] <= longest * 100 or len(g) < 2:
            return [g]
        k = max(range(1, len(g)), key=lambda k: g[k][0] - g[k - 1][1])  # at its longest pause
        return split(g[:k]) + split(g[k:])
    G = [(x[0][0], x[-1][1]) for g in groups(th) for x in split(g) if x[-1][1] - x[0][0] >= 10]
    if low < th:                                                         # quiet speech the parts above leave out
        extra, margin = [], int(pad * 100)
        for g in groups(low):
            for x in split(g):
                pieces = [(x[0][0], x[-1][1])]
                for a, b in G:                                           # minus the parts already found (and their padding)
                    pieces = [p for q in pieces for p in ((q[0], min(q[1], a - margin)), (max(q[0], b + margin), q[1])) if p[1] - p[0] > 0]
                extra += [p for p in pieces if p[1] - p[0] >= 30 and sum(1 for v in lv[p[0]:p[1]] if v > low) >= 30]
        G = sorted(G + extra)
    out = []
    for k, (a, b) in enumerate(G):
        lo = (G[k - 1][1] + a) / 2 if k else 0
        hi = (b + G[k + 1][0]) / 2 if k + 1 < len(G) else n
        out.append((round(max(lo, a - pad * 100) / 100, 3), round(min(hi, b + pad * 100) / 100, 3)))
    return out


def stretched(w, lv, th=None):
    """A word whisper stretched over a pause: much longer than its letters need (1.8 x (0.08 s + 0.065 s a letter)) with
    0.15 s or more of quiet inside it. Usually a false start or a repeat folded into the word after it ("this one app / this
    one app gives you" came back as "this one app gives you", each word over both takes). Returns the middle of that quiet
    (seconds, the recording's clock), else None (also for a word over quiet speech, all of it below th). w = {"text"/"w", "start"/"s", "end"/"e"}; lv = _levels(); th = _quiet_level()."""
    th = _quiet_level(lv) if th is None else th
    t = str(w.get("text", w.get("w", "")))
    s, e = float(w.get("start", w.get("s", 0))), float(w.get("end", w.get("e", 0)))
    letters = sum(c.isalnum() for c in t)
    if not letters or e - s < 1.8 * (0.08 + 0.065 * letters):
        return None
    a, b = int(s * 100) + 3, int(e * 100) - 3                            # not the word's own edges
    if not any(v > th for v in lv[int(s * 100): int(e * 100)]):
        return None                                                      # quiet speech: every frame reads as a pause at th
    best, run, at = 0, 0, None
    for i in range(max(0, a), min(len(lv), b)):
        run = run + 1 if lv[i] <= th else 0
        if run > best:
            best, at = run, i - run / 2 + 0.5
    return round(at / 100, 3) if best >= 15 else None


NOT_SPEECH = {"ahem", "tsk", "pfft", "psst", "hmph"}                       # sounds whisper writes as words
MADE_UP = {"thank", "thanks", "you", "very", "much", "so", "for", "watching", "bye", "subscribe", "please"}


def _made_up(W, a, b, lv, th):
    """Whisper's stock phrases over (near) silence: "Thank you.", "Thank you very much.", "Thanks for watching!". Only in a
    weak part (under 0.4 s of it above the cut's level th): when it holds nothing else it is dropped, and a run of them at
    either end over the room's own noise is trimmed (quiet real speech in between stays)."""
    seg = lv[int(a * 100): int(b * 100)]
    if not W or sum(1 for v in seg if v > th) >= 40:
        return W
    srt = sorted(lv)
    low = min(th, (srt[len(srt) // 20] if len(srt) > 100 else -80.0) + 15) + 6
    key = lambda w: re.sub(r"[^a-z]", "", str(w.get("text", "")).lower())
    heard = lambda w: sum(1 for v in lv[int(w["start"] * 100): max(int(w["start"] * 100) + 1, int(w["end"] * 100))] if v > low)
    if all(key(w) in MADE_UP for w in W if key(w)):
        return []
    while W and key(W[0]) in MADE_UP and heard(W[0]) < 10:
        W = W[1:]
    while W and key(W[-1]) in MADE_UP and heard(W[-1]) < 10:
        W = W[:-1]
    return W


def _shape(W, engine):
    """HyperFrames' words in the ElevenLabs shape. Non-speech (♪, [MUSIC], (laughs), a lone "-", "Ahem", "Tsk") becomes
    "audio_event", as ElevenLabs marks such sounds, so the cut and the captions skip it."""
    words = []
    for w in W:
        if not isinstance(w, dict):
            continue
        t = str(w.get("text", "")).strip()
        try:
            s, e = float(w["start"]), float(w["end"])
        except (KeyError, TypeError, ValueError):
            continue
        if not t:
            continue
        ev = bool(re.fullmatch(r"[\[(*♪].*[\])*♪]", t)) or not any(c.isalnum() for c in t) \
            or re.sub(r"[^a-z]", "", t.lower()) in NOT_SPEECH
        words.append({"text": t, "start": s, "end": e, "type": "audio_event" if ev else "word", "speaker_id": "speaker_0"})
    words.sort(key=lambda x: x["start"])
    for a, b in zip(words, words[1:]):                                   # whisper can give a word a zero or negative length
        if a["end"] <= a["start"]:
            a["end"] = min(a["start"] + 0.12, b["start"]) if b["start"] > a["start"] else a["start"] + 0.08
    if words and words[-1]["end"] <= words[-1]["start"]:
        words[-1]["end"] = words[-1]["start"] + 0.12
    return {"words": words, "text": " ".join(w["text"] for w in words if w["type"] == "word"), "_engine": engine}


def _local(audio, language, progress=None):
    """On this computer, through HyperFrames' transcriber (Parakeet if installed, else whisper.cpp).
    Given a whole recording, whisper quietly drops a sentence that comes after a long pause (it jumps to the end of its 30 s
    window) and folds a false start into the take after it ("this one app / this one app gives you" comes back once). So:
      1. the audio is split at its pauses (PAUSE s or more) and each part is transcribed on its own, JOBS at a time (the
         longest first and alone: it installs or downloads anything missing, and with language None it tells the language
         for the rest), then the words go back on the recording's clock;
      2. a part with a word stretched over a pause inside it (stretched()) is cut at those pauses and transcribed again; the
         new words are kept when there are more of them (the false start, now on its own).
    Quiet speech (a whisper, someone further from the mic) gets parts of its own; whisper's stock "Thank you." over a
    near-silent part is left out (_made_up).
    A recording whose loudness can't be measured goes in whole, as before. progress(step, pct, eta_s): the one-time model
    download, then the parts done."""
    def say(*a):
        try:
            if progress:
                progress(*a)
        except Exception:                                                # a failing callback (say, a full disk) must never stop
            pass                                                         # the transcription or the draining of HyperFrames' output
    say("Transcribing on this computer")
    eng = lambda meta, model: "local/" + str(meta.get("engine", "whisper")) + "/" + str(meta.get("model", model))
    lv = _levels(audio)
    parts = _parts(lv)
    pcm = b""
    if parts:
        try:
            pcm = subprocess.run(["ffmpeg", "-v", "error", "-nostdin", "-i", audio, "-vn", "-ac", "1", "-ar", "16000", "-f", "s16le", "-"],
                                 stdout=subprocess.PIPE, stderr=subprocess.PIPE).stdout
        except OSError:
            pcm = b""
    model = "small.en" if language == "en" else "small"
    if lv and not parts and sorted(lv)[int(len(lv) * 0.99)] - sorted(lv)[len(lv) // 20] < 20:
        return _shape([], eng({}, model))                               # nothing louder than the room: no speech (whisper would
    if not parts or not pcm:                                             # make up a "you"); couldn't measure it: in one go
        W, meta = _hf(audio, language, say)
        return _shape(W, eng(meta, ""))
    th, quiet, exe = _quiet_level(lv), (lambda *a: None), _hf_exe()
    with tempfile.TemporaryDirectory() as d:
        names = iter(range(10 ** 9))
        lock = threading.Lock()

        def cut(a, b):
            with lock:
                f = os.path.join(d, "part%05d.wav" % next(names))
            with wave.open(f, "wb") as o:
                o.setnchannels(1)
                o.setsampwidth(2)
                o.setframerate(16000)
                o.writeframes(pcm[int(a * 16000) * 2: int(b * 16000) * 2])
            return f

        def run(spans, lang, first=None, report=None, got=None):
            """Transcribe each span -> {index: (words on the recording's clock, meta)}, JOBS at a time (first: alone, before).
            got: spans already done."""
            got, stop = dict(got or {}), threading.Event()
            todo = [k for k in range(len(spans)) if k != first and k not in got]
            t0 = time.time()

            def one(k, say_=quiet):
                if stop.is_set():
                    return
                a, b = spans[k]
                W, meta = _hf(cut(a, b), lang, say_, model, stop, exe)
                out = []
                for w in W:
                    try:
                        s, e = float(w["start"]) + a, float(w["end"]) + a
                    except (KeyError, TypeError, ValueError):
                        continue
                    if s < b and e > a:                                  # outside its own part: whisper made it up
                        out.append(dict(w, start=round(max(a, s), 3), end=round(min(b, e), 3)))
                out = _made_up(out, a, b, lv, th)
                with lock:
                    got[k] = (out, meta)
                    if report:
                        left = sum(spans[j][1] - spans[j][0] for j in range(len(spans)) if j not in got)
                        took = (time.time() - t0) / max(0.5, sum(spans[j][1] - spans[j][0] for j in got))
                        report(100 * len(got) / len(spans), left * took / (1 if len(got) < 2 else JOBS))
            if first is not None and first not in got:
                one(first, say)
            if todo:
                from concurrent.futures import ThreadPoolExecutor
                ex = ThreadPoolExecutor(max_workers=JOBS)
                try:
                    for fu in [ex.submit(one, k) for k in todo]:
                        fu.result()                                      # the first failure stops the rest
                except BaseException:
                    stop.set()
                    raise
                finally:
                    ex.shutdown(wait=True, cancel_futures=True)
            return got

        first = max(range(len(parts)), key=lambda k: parts[k][1] - parts[k][0])
        lang, have = language, {}
        if language is None:                                             # find the language on the longest part, then use it
            have = {first: run([parts[first]], None, 0)[0]}
            dl = str(have[first][1].get("detectedLanguage") or "").lower()
            lang = dl if re.fullmatch(r"[a-z]{2,3}", dl) else None
        got = run(parts, lang, first, lambda pct, eta: say("Transcribing on this computer", pct, eta), have)
        meta = got[first][1]
        # 2. a second look at the parts with a word stretched over a pause
        redo = {}
        for k, (a, b) in enumerate(parts):
            cuts = sorted({c for c in (stretched(w, lv, th) for w in got[k][0]) if c and a + 0.3 < c < b - 0.3})
            if cuts:
                edges = [a] + cuts + [b]
                redo[k] = [(edges[i], edges[i + 1]) for i in range(len(edges) - 1)]
        if redo:
            say("Checking the pauses again")
            flat = [(k, sp) for k in sorted(redo) for sp in redo[k]]
            again = run([sp for _, sp in flat], lang)
            for k in redo:
                new = [w for i, (kk, _) in enumerate(flat) if kk == k for w in again[i][0]]
                count = lambda W: len(_shape(W, "")["text"].split())
                if count(new) > count(got[k][0]):
                    got[k] = (new, got[k][1])
    J = _shape([w for k in range(len(parts)) for w in got[k][0]], eng(meta, model))
    J["_parts"] = len(parts)
    return J


def transcribe(audio, diarize=False, keyterms=None, language=CONFIG, events=True, speakers=None, use=None, progress=None):
    """language: the creator's setting by default (default_language()); None lets the transcriber detect it.
    speakers = a known number of people (ElevenLabs only). use = "elevenlabs" | "local" overrides the engine.
    progress(step, pct=None, eta_s=None) is told what is happening (the model download, with pct and eta)."""
    if language == CONFIG:
        language = default_language()
    e = (use or engine()).lower()
    if e.startswith("eleven"):
        return _elevenlabs(audio, diarize, keyterms, language, events, speakers, progress)
    if diarize:
        print("NOTE local transcription has no speaker labels: every word is marked speaker_0. Work out who is speaking from what is said.")
    print("NOTE local transcription: word edges are looser than ElevenLabs, and a repeat or false start said without a pause can come back "
          "once. Check the tight cut for clipped words and listen around each pause before rendering.")
    return _local(audio, language, progress)


# ---- the Studio's choice of engine: the app's switch first, and on-device when ElevenLabs can't be used for this video
FALLBACK = {"bad_key": "Used on-device transcription: ElevenLabs didn't accept the key",
            "no_credit": "Used on-device transcription: ElevenLabs is out of credit",
            "network": "Used on-device transcription: couldn't reach ElevenLabs",
            "api": "Used on-device transcription: ElevenLabs had a problem"}


def studio_engine():
    """(engine, note) for a Studio job. The app's Transcription switch (config "transcriber") wins over the setup answer;
    ElevenLabs with no key yet = on-device for this video, and the note says so."""
    e = (studio_config().get("transcriber") or engine()).lower()
    if e.startswith("eleven"):
        return ("elevenlabs", None) if el_key(False) else ("local", "Used on-device transcription: no ElevenLabs key yet")
    return "local", None


def transcribe_studio(audio, progress=None, **kw):
    """transcribe() with the Studio's engine choice, falling back to on-device when ElevenLabs fails (rejected key, no credit,
    no connection). Returns (result, note): note is None, or one line for the app saying what was used instead."""
    e, note = studio_engine()
    try:
        return transcribe(audio, use=e, progress=progress, **kw), note
    except STTError as x:
        if note:                                                         # no ElevenLabs key, and on-device didn't work either
            raise STTError(f"There's no ElevenLabs key yet, and on-device transcription didn't work: {x}", "local",
                           "Ask Claude in the chat to set up your ElevenLabs key or on-device transcription.")
        if e != "elevenlabs" or x.kind not in FALLBACK:
            raise
        print(f"NOTE {x} -> on-device transcription for this video")
        try:
            return transcribe(audio, use="local", progress=progress, **kw), FALLBACK[x.kind]
        except STTError as y:
            raise STTError(f"{x} On-device transcription didn't work either: {y}", "local", x.fix or y.fix)


if __name__ == "__main__":
    if "--key" in sys.argv:
        where = key_source()[0]
        print(f"ElevenLabs key found ({where})" if where else "No ElevenLabs key yet" + "".join(f" ({n})" for n in KEY_NOTE))
        sys.exit(0 if where else 1)
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if not args:
        sys.exit(__doc__)
    src = args[0]
    tmp = None
    if not src.lower().endswith((".wav", ".flac", ".mp3", ".m4a")):
        tmp = tempfile.mktemp(suffix=".flac")
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", src, "-vn", "-ac", "1", "-ar", "16000", tmp], check=True)
    J = transcribe(tmp or src, diarize="--diarize" in sys.argv)
    out = args[1] if len(args) > 1 else os.path.splitext(src)[0] + ".words.json"
    json.dump(J, open(out, "w"))
    print(J["_engine"], len(J["words"]), "words ->", out)
    if tmp:
        os.remove(tmp)
