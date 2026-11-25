"""Room tone and BOX_01 foley for S01E01 (system python3 + numpy). 48 kHz, exactly 30.000 s.
    python3 scripts/audio.py
No dialogue is synthesised (no voice recordings or TTS available); dialogue timing lives in reports/camera_cut_timeline.json."""
import os
import sys
import wave

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import shotlist as S  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SR = 48000
N = int(SR * (S.FRAME_END - S.FRAME_START + 1) / S.FPS)
rng = np.random.default_rng(5)


def lowpass(x, a):
    y = np.empty_like(x)
    acc = 0.0
    for i, v in enumerate(x):
        acc += a * (v - acc)
        y[i] = acc
    return y


def write(name, data):
    data = np.clip(data, -1, 1)
    pcm = (data * 32767).astype(np.int16)
    p = os.path.join(ROOT, "audio", name)
    with wave.open(p, "wb") as w:
        w.setnchannels(2 if pcm.ndim == 2 else 1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(pcm.tobytes())
    print("wrote", p, f"{len(data) / SR:.3f}s")


def t_of(frame):
    return int((frame - 1) / S.FPS * SR)


# room tone: soft HVAC air (filtered noise), faint 60 Hz electrical hum, very slow swell; about -40 dBFS RMS
n = rng.standard_normal(N)
air = np.convolve(n, np.ones(40) / 40, mode="same")
air = air - np.convolve(air, np.ones(2400) / 2400, mode="same")
t = np.arange(N) / SR
tone = air * 0.05 * (1 + 0.15 * np.sin(2 * np.pi * 0.07 * t)) + 0.0025 * np.sin(2 * np.pi * 60 * t) + 0.001 * np.sin(2 * np.pi * 120 * t)
tone *= 0.01 / np.sqrt(np.mean(tone ** 2))
write("OFFBRIEF_S01E01_room_tone.wav", np.stack([tone, np.roll(tone, 911)], axis=1))


# foley: subtle illustrated footsteps and cardboard movement, no cartoon effects
def tap(level, dur=0.05, body=140.0, bright=0.4):
    k = int(dur * SR)
    tt = np.arange(k) / SR
    env = np.exp(-tt / (dur / 5))
    nz = rng.standard_normal(k)
    nz = nz - np.convolve(nz, np.ones(12) / 12, mode="same")
    return level * env * (bright * nz + (1 - bright) * np.sin(2 * np.pi * body * tt))


def rustle(level, dur):
    k = int(dur * SR)
    tt = np.linspace(0, 1, k)
    env = np.sin(np.pi * tt) ** 2
    nz = rng.standard_normal(k)
    nz = np.convolve(nz, np.ones(6) / 6, mode="same")
    return level * env * nz


fol = np.zeros(N)


def put(frame, sig):
    i = t_of(frame)
    j = min(N, i + len(sig))
    fol[i:j] += sig[:j - i]


put(313, rustle(0.05, 0.18))                       # pops onto the slide
for f in range(364, 369, 4):
    put(f, tap(0.04, 0.04, 220, 0.5))              # steps through the screen plane
put(372, tap(0.10, 0.08, 120, 0.35))               # drops onto the sideboard
for f in range(376, 389, 4):
    put(f, tap(0.035, 0.035, 240, 0.55))           # walks along the sideboard
put(390, rustle(0.04, 0.10))                        # crouch
put(400, tap(0.16, 0.10, 95, 0.3))                 # lands on the tabletop
put(401, rustle(0.05, 0.15))
put(420, rustle(0.07, 0.30))                        # flaps open
put(450, rustle(0.06, 0.25))                        # flaps close
for f in range(472, 521, 8):
    put(f, tap(0.03, 0.035, 230, 0.55))            # little dance steps
put(664, rustle(0.06, 0.45))                        # slumps
# pan with the box: on screen (left of centre) -> table (centre)
pan = np.full(N, 0.0)
pan[: t_of(400)] = -0.25
pl, pr = np.sqrt(0.5 * (1 - pan)), np.sqrt(0.5 * (1 + pan))
write("OFFBRIEF_S01E01_box_foley.wav", np.stack([fol * pl, fol * pr], axis=1))
