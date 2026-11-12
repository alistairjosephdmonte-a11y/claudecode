"""Temp dialogue guide (espeak-ng), fitted to the brief's frame windows, plus per-frame lip-sync envelopes.
    python3 scripts/dialogue.py
Writes audio/dialogue/<ID>.wav (48 kHz mono, exactly the window length) and metadata/lipsync.json
({line: {f0, f1, jaw: [0..1 per frame], phonemes: [[frame, phoneme], ...]}})."""
import json
import os
import subprocess
import sys
import tempfile
import wave

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import config as C  # noqa: E402

SR = 48000
VOICE = {"JASON_01": ("en-us+m3", 30), "LUCIA_01": ("en-us+f4", 58)}


def tts(text, voice, pitch, speed):
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
        path = f.name
    subprocess.run(["espeak-ng", "-v", voice, "-p", str(pitch), "-s", str(speed), "-w", path, text], check=True)
    w = wave.open(path)
    sr = w.getframerate()
    x = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(float) / 32768
    os.unlink(path)
    x = np.interp(np.arange(int(len(x) * SR / sr)) * sr / SR, np.arange(len(x)), x)
    e = np.convolve(np.abs(x), np.ones(480) / 480, "same")
    on = np.where(e > 0.03 * e.max())[0]
    return x[on[0]:on[-1] + 1]


def phonemes(text, voice):
    out = subprocess.run(["espeak-ng", "-q", "-x", "--sep=_", "-v", voice, text], capture_output=True, text=True).stdout.split()
    return [p for w in out for p in w.replace("'", "").replace(",", "").split("_") if p] or out


if __name__ == "__main__":
    os.makedirs(os.path.join(C.P["audio"], "dialogue"), exist_ok=True)
    sync = {}
    for d in C.DIALOGUE:
        voice, pitch = VOICE[d["who"]]
        win = (d["f1"] - d["f0"]) / C.FPS
        best = None
        for speed in range(130, 330, 5):
            x = tts(d["text"], voice, pitch, speed)
            dur = len(x) / SR
            if dur <= win and (best is None or dur > best[1]):
                best = (x, dur, speed)
        x, dur, speed = best
        n = int(round(win * SR))
        y = np.zeros(n)
        y[:len(x)] = x * (0.9 / max(1e-9, np.abs(x).max()))
        f = np.linspace(1, 0, 240)
        y[len(x) - 240:len(x)] *= f
        with wave.open(os.path.join(C.P["audio"], "dialogue", f"{d['id']}.wav"), "w") as w:
            w.setnchannels(1)
            w.setsampwidth(2)
            w.setframerate(SR)
            w.writeframes((np.clip(y, -1, 1) * 32767).astype(np.int16).tobytes())
        spf = SR // C.FPS
        rms = np.array([np.sqrt(np.mean(y[i * spf:(i + 1) * spf] ** 2)) for i in range(d["f1"] - d["f0"])])
        jaw = (rms / max(1e-9, rms.max())).round(3).tolist()
        ph = phonemes(d["text"], voice)
        voiced = len(x) / SR * C.FPS
        sync[d["id"]] = dict(who=d["who"], f0=d["f0"], f1=d["f1"], speed_wpm=speed, voiced_frames=round(voiced, 1), jaw=jaw,
                             phonemes=[[d["f0"] + int(i * voiced / max(1, len(ph))), p] for i, p in enumerate(ph)])
        print(f"{d['id']}: '{d['text']}' window {d['f1'] - d['f0']} f, voiced {voiced:.1f} f at {speed} wpm, {len(ph)} phonemes")
    os.makedirs(C.P["meta"], exist_ok=True)
    json.dump(sync, open(os.path.join(C.P["meta"], "lipsync.json"), "w"), indent=1)
