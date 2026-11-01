"""Temporary, restrained sound design (synthesized: sines and filtered noise only; no samples, no music, no voice).
Low investigative underscore + soft paper movement on document reveals + minimal clicks on highlights + five bass
emphases at major revelations. Writes audio/BC002_temp_sound_design.wav (48 kHz stereo, exactly 480.0 s) and
metadata/audio_cues.json.    python3 scripts/sound_design.py"""
import json
import os
import wave

import numpy as np

import config as C

SR = 48000
N = int(C.TOTAL_FRAMES / C.FPS * SR)
rng = np.random.default_rng(2)
BASS = [(1, 25.0, "what went wrong?"), (7, 10.4, "$33.95 billion"), (11, 21.4, "the timeline breaks"),
        (14, 22.4, "chapter 11 filing"), (16, 18.8, "the verdict")]


def scene_t(n, t):
    return (C.scene_start(n) - 1) / C.FPS + t


def fft_band(x, lo, hi):
    X = np.fft.rfft(x)
    f = np.fft.rfftfreq(len(x), 1 / SR)
    X[(f < lo) | (f > hi)] = 0
    return np.fft.irfft(X, len(x))


def underscore():
    t = np.arange(N) / SR
    act_root = np.full(N, 55.0)
    for i, a in enumerate(C.ACTS):
        s0 = scene_t(a[2][0], 0)
        act_root[t >= s0] = [55.0, 55.0, 51.9, 51.9, 49.0, 46.2][i]
    phase = 2 * np.pi * np.cumsum(act_root) / SR
    lfo = 0.6 + 0.4 * np.sin(2 * np.pi * 0.045 * t)
    drone = (0.5 * np.sin(phase) + 0.22 * np.sin(1.5 * phase + 0.3) + 0.12 * np.sin(2 * phase)) * lfo
    noise = fft_band(rng.standard_normal(N), 60, 420) * 0.35
    bed = 0.06 * drone + 0.025 * noise / np.std(noise)
    env = np.ones(N)
    for a in C.ACTS:                                     # dip with the picture's fades to black between acts
        e = scene_t(a[2][-1], 30)
        m = (t > e - 0.8) & (t < e + 0.6)
        env[m] = np.minimum(env[m], np.abs(t[m] - e) / 0.8 * 0.85 + 0.15)
    env *= np.clip(t / 2.0, 0, 1) * np.clip((N / SR - t) / 1.5, 0, 1)
    return bed * env


def paper(n=0.35):
    L = int(n * SR)
    x = fft_band(rng.standard_normal(L), 1800, 7000)
    env = np.exp(-np.linspace(0, 6, L)) * (1 - np.exp(-np.linspace(0, 40, L)))
    return 0.05 * x / np.max(np.abs(x)) * env


def click():
    L = int(0.012 * SR)
    x = np.sin(2 * np.pi * 2400 * np.arange(L) / SR) * np.exp(-np.linspace(0, 9, L))
    return 0.035 * x


def bass():
    L = int(2.2 * SR)
    tt = np.arange(L) / SR
    f = 58 - 18 * (1 - np.exp(-tt * 2.5))
    x = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tt * 2.0) * (1 - np.exp(-tt * 60))
    return 0.32 * x


def place(buf, clip, t, pan=0.0):
    i = int(t * SR)
    j = min(N, i + len(clip))
    if i >= N:
        return
    buf[0, i:j] += clip[: j - i] * (1 - max(0, pan))
    buf[1, i:j] += clip[: j - i] * (1 + min(0, pan))


if __name__ == "__main__":
    log = json.load(open(os.path.join(C.P["meta"], "build_log.json")))
    out = np.zeros((2, N))
    bed = underscore()
    out += bed
    cues, seen = [], set()
    for name, lg in log.items():
        n = int(name[2:])
        for h in lg["highlights"]:
            t = scene_t(n, h["t"])
            if (n, h["doc"]) not in seen:
                seen.add((n, h["doc"]))
                place(out, paper(), max(0, t - 0.9), pan=rng.uniform(-0.3, 0.3))
                cues.append({"t": round(t - 0.9, 2), "type": "paper", "scene": name, "doc": h["doc"]})
            place(out, click(), t + 0.2)
            cues.append({"t": round(t + 0.2, 2), "type": "click", "scene": name, "phrase": h["phrase"]})
    for n, t, why in BASS:
        place(out, bass(), scene_t(n, t))
        cues.append({"t": round(scene_t(n, t), 2), "type": "bass", "scene": f"SC{n:02d}", "why": why})
    peak = np.max(np.abs(out))
    out *= 0.5 / peak                                     # about -6 dBFS peak: a temp bed, leaves room for narration
    pcm = (out.T * 32767).astype("<i2")
    path = os.path.join(C.P["audio"], "BC002_temp_sound_design.wav")
    with wave.open(path, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(pcm.tobytes())
    cues.sort(key=lambda c: c["t"])
    json.dump({"note": C.AUDIO["note"], "duration_s": N / SR, "cues": cues}, open(os.path.join(C.P["meta"], "audio_cues.json"), "w"), indent=1)
    print("WAV", path, N / SR, "s", len(cues), "cues")
