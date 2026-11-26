"""Builds the soundtrack for the 15-second cut from metadata/events.json, synthesised with numpy (no samples).

    python3 scripts/sound.py            -> deliverables/trap_cut_audio.wav (48 kHz stereo)

Every event in a shot's sim-frame range is placed at its film time, panned by where it sits relative to that shot's
camera and scaled by distance. Repeated sim frames (the held opening shot) trigger nothing. Sounds are pitched down
15% because the picture runs at half speed.
"""

import json
import math
import os
import random
import sys
import wave

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from cut_spec import FPS, TOTAL, film_frames  # noqa: E402

SR = 48000
PITCH = 0.85
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
rng = np.random.default_rng(11)
random.seed(11)


def env(n, decay):
    return np.exp(-np.arange(n) / (decay * SR))


def tone(freqs, decay, dur, amps=None):
    n = int(dur * SR)
    t = np.arange(n) / SR
    out = np.zeros(n)
    for k, f in enumerate(freqs):
        out += (amps[k] if amps else 1.0) * np.sin(2 * math.pi * f * PITCH * t + rng.uniform(0, 6.28))
    return out * env(n, decay)


def band_noise(lo, hi, dur, decay):
    n = int(dur * SR)
    spec = np.fft.rfft(rng.standard_normal(n))
    fr = np.fft.rfftfreq(n, 1 / SR)
    spec[(fr < lo * PITCH) | (fr > hi * PITCH)] = 0
    return np.fft.irfft(spec, n) * env(n, decay) * 3


def mixsum(*parts):
    out = np.zeros(max(len(x) for x in parts))
    for x in parts:
        out[:len(x)] += x
    return out


def snap(v):
    s = 1.0 + v * random.uniform(-0.15, 0.15)
    click = band_noise(2000, 12000, 0.012, 0.002) * 1.2
    ring = tone([2300 * s, 3750 * s, 5200 * s], 0.045, 0.18, [0.5, 0.35, 0.2])
    knock = mixsum(tone([420 * s, 610 * s], 0.03, 0.12, [0.8, 0.4]), band_noise(300, 1800, 0.1, 0.02) * 0.6)
    return mixsum(click, ring * 0.6, knock)


def clack(kind, speed):
    g = min(speed / 1.2, 1.0) ** 0.8
    if kind == "pingpong":
        f = random.uniform(1150, 1500)
        return mixsum(tone([f, f * 2.1], 0.012, 0.06, [1.0, 0.3]), band_noise(1500, 7000, 0.01, 0.002) * 0.4) * g * 0.7
    if kind == "ball":
        return mixsum(tone([110, 165], 0.07, 0.3, [1.0, 0.4]), band_noise(80, 600, 0.2, 0.03)) * g * 1.4
    if kind == "bar":
        return mixsum(tone([3100 * random.uniform(0.9, 1.1), 4700], 0.02, 0.08, [0.4, 0.2]),
                      band_noise(2500, 9000, 0.01, 0.002) * 0.3) * g * 0.35
    f = random.uniform(500, 800)
    return mixsum(band_noise(700, 3000, 0.08, 0.012) * 0.8, tone([f, f * 1.6], 0.025, 0.1, [0.7, 0.3])) * g * 0.55


def place(mix, sig, t, pan, gain):
    i = int(t * SR)
    if i >= mix.shape[1]:
        return
    sig = sig[: mix.shape[1] - i] * gain
    a = (pan + 1) * math.pi / 4
    mix[0, i:i + len(sig)] += sig * math.cos(a)
    mix[1, i:i + len(sig)] += sig * math.sin(a)


def cam_relative(p, loc, target):
    d = np.array(p) - np.array(loc)
    fwd = np.array(target) - np.array(loc)
    fwd /= np.linalg.norm(fwd)
    right = np.cross(fwd, [0, 0, 1])
    right /= np.linalg.norm(right) or 1
    dist = max(np.linalg.norm(d), 0.15)
    return float(np.clip(d @ right / dist, -0.9, 0.9)), dist


def ambience(n):
    w = np.fft.rfft(rng.standard_normal(n))
    fr = np.fft.rfftfreq(n, 1 / SR)
    w /= np.maximum(fr, 20) ** 0.5
    w[fr > 4000] *= 0.2
    room = np.fft.irfft(w, n)
    room *= 0.004 / room.std()
    t = np.arange(n) / SR
    calm_end = 48 / FPS + 0.9                     # drone rises through the opening, dies when the ball lands
    swell = np.clip(t / calm_end, 0, 1) ** 2 * (t < calm_end)
    swell *= np.clip((calm_end - t) / 0.15, 0, 1)
    drone = (np.sin(2 * math.pi * 55 * t) + 0.6 * np.sin(2 * math.pi * 82.4 * t)
             + 0.25 * np.sin(2 * math.pi * 164.8 * t * (1 + 0.002 * np.sin(t * 3)))) * swell * 0.06
    return np.vstack([room + drone, np.roll(room, 977) + drone])


def main():
    ev = json.load(open(os.path.join(ROOT, "metadata", "events.json")))
    by_frame = {}
    for e in ev["snap"]:
        by_frame.setdefault(e["frame"], []).append(("snap", e))
    for e in ev["clack"]:
        by_frame.setdefault(e["frame"], []).append(("clack", e))
    n = int(TOTAL / FPS * SR) + SR
    mix = ambience(n)
    prev = None
    count = 0
    for film, shot, i, sim, loc, target in film_frames():
        if i > 0 and sim == prev:
            continue
        prev = sim
        t0 = (film - 1) / FPS
        for kind, e in by_frame.get(sim, []):
            pan, dist = cam_relative(e["pos"], loc, target)
            gain = min(0.5 / dist, 2.0)
            t = t0 + random.uniform(0, 1 / FPS)
            if kind == "snap":
                place(mix, snap(1), t, pan, gain * 0.9)
            else:
                place(mix, clack(e["kind"], e["speed"]), t, pan, gain)
            count += 1
    mix = mix[:, : int(TOTAL / FPS * SR)]
    fade = int(0.6 * SR)
    mix[:, -fade:] *= np.linspace(1, 0, fade) ** 2
    mix = np.tanh(mix * 1.6) / np.tanh(1.6)
    mix *= 0.89 / np.abs(mix).max()
    out = os.path.join(ROOT, "deliverables", "trap_cut_audio.wav")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with wave.open(out, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((mix.T * 32767).astype("<i2").tobytes())
    print("AUDIO %s events %d %.2fs" % (out, count, mix.shape[1] / SR))


main()
