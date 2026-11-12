"""Temp sound for the block animatic: all synthesized here (numpy) except the dialogue guide (espeak-ng).
    python3 scripts/audio.py        (needs metadata/build_log.json and audio/dialogue/*.wav)
Writes audio/stems/{dialogue,music,sfx,ambience}.wav, audio/PS_GTA_EP01_temp_mix.wav (48 kHz, 16-bit) and
metadata/audio_cues.json."""
import json
import os
import sys
import wave

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import config as C  # noqa: E402

SR = 48000
N = int(C.TOTAL_FRAMES / C.FPS * SR)
rng = np.random.default_rng(11)
CUES = []


def t_of(frame):
    return (frame - 1) / C.FPS


def idx(frame):
    return int(t_of(frame) * SR)


def cue(name, f0, f1=None, stem="sfx"):
    CUES.append(dict(cue=name, stem=stem, frame_in=f0, frame_out=f1 or f0, time_in=round(t_of(f0), 3)))


def env(n, a=0.005, r=0.05):
    e = np.ones(n)
    na, nr = min(n, int(a * SR)), min(n, int(r * SR))
    if na:
        e[:na] = np.linspace(0, 1, na)
    if nr:
        e[-nr:] *= np.linspace(1, 0, nr)
    return e


def band(x, lo, hi):
    X = np.fft.rfft(x)
    f = np.fft.rfftfreq(len(x), 1 / SR)
    X[(f < lo) | (f > hi)] = 0
    return np.fft.irfft(X, len(x))


def noise(n):
    return rng.standard_normal(n)


def add(buf, sig, at):
    a = max(0, at)
    b = min(len(buf), at + len(sig))
    if b > a:
        buf[a:b] += sig[a - at:b - at]


def tone(freq, dur, shape="sine"):
    t = np.arange(int(dur * SR)) / SR
    ph = 2 * np.pi * np.cumsum(np.broadcast_to(freq, t.shape) if np.ndim(freq) else np.full(t.shape, freq)) / SR
    if shape == "saw":
        return 2 * ((ph / (2 * np.pi)) % 1) - 1
    if shape == "square":
        return np.sign(np.sin(ph))
    return np.sin(ph)


# ------------------------------------------------------------------ SFX
def sfx(log):
    s = np.zeros(N)
    # disc handling: pick-up rustle, case-plastic tick, slide over the tray, seat on the spindle
    for f0, dur, g in ((36, 0.5, 0.05), (100, 0.55, 0.05)):
        x = band(noise(int(dur * SR)), 2500, 9000) * env(int(dur * SR), 0.05, 0.2) * g
        add(s, x, idx(f0))
        cue("disc handling", f0, f0 + int(dur * C.FPS))
    for f0 in (44, 114):
        x = band(noise(int(0.03 * SR)), 3000, 12000) * np.exp(-np.arange(int(0.03 * SR)) / (0.004 * SR)) * 0.5
        add(s, x, idx(f0))
    cue("disc seats on spindle (tick)", 114)
    # PS2 tray motor (whir, rising) + latch click
    a, b = 128, 140
    n = idx(b) - idx(a)
    whir = tone(np.linspace(140, 210, n), n / SR, "saw") * 0.06 + band(noise(n), 300, 2500) * 0.03
    add(s, whir * env(n, 0.03, 0.04), idx(a))
    cue("PS2 tray motor", a, b)
    k = band(noise(int(0.025 * SR)), 1500, 8000) * np.exp(-np.arange(int(0.025 * SR)) / (0.003 * SR)) * 0.9
    add(s, k, idx(140))
    add(s, tone(1800, 0.02) * np.exp(-np.arange(int(0.02 * SR)) / (0.003 * SR)) * 0.25, idx(140))
    cue("tray click", 140)
    # CRT startup: degauss thunk + hum + rising 15.7 kHz whine
    th = int(0.6 * SR)
    add(s, (tone(60, 0.6) * 0.5 + band(noise(th), 40, 300) * 0.4) * np.exp(-np.arange(th) / (0.12 * SR)) * 0.8, idx(149))
    hum = (tone(60, 2.0) * 0.6 + tone(120, 2.0) * 0.3) * env(int(2.0 * SR), 0.05, 1.2) * 0.06
    add(s, hum, idx(149))
    wh = tone(15700, 1.6) * env(int(1.6 * SR), 0.4, 0.8) * 0.012
    add(s, wh, idx(150))
    cue("CRT startup degauss + hum", 149, 196)
    # portal: whoosh, hinge groans as the wall leaves swing out
    for f0, dur, g, lo, hi in ((193, 0.6, 0.25, 200, 6000), (448, 0.85, 0.3, 120, 5000)):
        n = int(dur * SR)
        sweep = band(noise(n), lo, hi) * np.sin(np.linspace(0, np.pi, n)) ** 2 * g
        add(s, sweep, idx(f0))
        cue("transition whoosh", f0, f0 + int(dur * C.FPS))
    for f0 in (199, 202):
        n = int(0.7 * SR)
        cr = band(tone(np.linspace(95, 70, n), 0.7, "saw"), 60, 1200)
        add(s, cr * env(n, 0.05, 0.3) * 0.08, idx(f0))
    cue("portal leaves swing open", 199, 215)
    # CAR_01 rolls in: engine rumble with tyre roll, settles to idle
    a, b = 206, 246
    n = idx(b) - idx(a)
    tt = np.linspace(0, 1, n)
    rpm = 38 + 28 * np.sin(np.pi * np.clip(tt * 1.3, 0, 1))
    eng = tone(rpm, n / SR, "saw") * 0.35 + tone(rpm * 2, n / SR, "saw") * 0.15
    eng = band(eng, 25, 900) + band(noise(n), 60, 400) * 0.25
    gain = np.clip(tt * 2.5, 0, 1) * np.where(tt > 0.85, np.linspace(1, 0.4, n), 1)
    add(s, eng * gain * 0.35, idx(a))
    idle = band(tone(32, 8.0, "saw"), 25, 300) * 0.05
    add(s, idle * env(len(idle), 0.3, 1.5), idx(b))
    cue("car engine roll-in + idle", a, b)
    # Tommy footsteps (from the planted-foot contacts in build_log)
    fr = log["frames"]
    for side in ("L", "R"):
        prev = None
        for f in range(2, C.TOTAL_FRAMES + 1):
            z = fr[str(f)]["tommy_feet"][side][2]
            if prev is not None and prev > 0.081 and z <= 0.0785:
                n = int(0.09 * SR)
                st = (band(noise(n), 80, 1800) * 0.6 + tone(70, 0.09) * 0.4) * np.exp(-np.arange(n) / (0.02 * SR)) * 0.35
                add(s, st, idx(f))
                cue(f"Tommy footstep {side}", f)
            prev = z
    # controller grab + handoff rustle, button taps during S09
    for f0 in (350, 352):
        n = int(0.05 * SR)
        add(s, band(noise(n), 1200, 6000) * np.exp(-np.arange(n) / (0.01 * SR)) * 0.25, idx(f0))
    cue("controller handoff", 350, 352)
    for f0 in range(388, 430, 5):
        n = int(0.015 * SR)
        add(s, band(noise(n), 2000, 7000) * np.exp(-np.arange(n) / (0.003 * SR)) * 0.12, idx(f0))
    # gameplay car on the CRT speaker: cruising away (band-limited like a TV speaker), fading with distance
    a, b = 385, 468
    n = idx(b) - idx(a)
    tt = np.linspace(0, 1, n)
    g = band(tone(55 + 6 * np.sin(tt * 6), n / SR, "saw") + band(noise(n), 200, 3000) * 0.3, 180, 4500)
    add(s, g * (0.12 * (1 - 0.7 * tt)), idx(a))
    cue("gameplay car on CRT (TV speaker)", a, b)
    # final low bass hit on the slate
    n = int(2.2 * SR)
    tt = np.arange(n) / SR
    hit = np.sin(2 * np.pi * np.cumsum(38 * np.exp(-tt * 0.6)) / SR) * np.exp(-tt * 1.6) + band(noise(n), 30, 200) * np.exp(-tt * 9) * 0.5
    add(s, hit * 0.9, idx(C.SLATE_F))
    cue("final low bass hit", C.SLATE_F)
    return s


# ------------------------------------------------------------------ ambience
def ambience():
    a = np.zeros(N)
    room = band(noise(N), 40, 400) * 0.010 + tone(15700, N / SR) * 0.0015
    gate_room = np.ones(N)
    gate_room[idx(199):] = np.linspace(1, 0.35, N - idx(199))
    a += room * gate_room
    cue("room tone + CRT whine", 1, 199, "ambience")
    st0 = idx(197)
    n = N - st0
    tt = np.linspace(0, 1, n)
    street = band(noise(n), 80, 3000) * 0.02 + band(noise(n), 300, 1200) * 0.01 * (1 + np.sin(tt * 9))
    birds = np.zeros(n)
    for k in range(9):
        at = rng.integers(0, max(1, n - SR // 2))
        m = int(0.18 * SR)
        birds[at:at + m] += tone(np.linspace(3200, 4200, m) + 300 * np.sin(np.arange(m) / SR * 80), m / SR) * env(m, 0.01, 0.08) * 0.02
    fade = np.clip((np.arange(n) - 0) / (0.4 * SR), 0, 1) * np.where(np.arange(n) > idx(C.SLATE_F) - st0, 0.0, 1.0)
    a[st0:] += (street + birds) * fade
    cue("Ocean Drive street ambience", 197, C.SLATE_F - 1, "ambience")
    return a


# ------------------------------------------------------------------ music: retro synth pulse from the title screen
def music():
    m = np.zeros(N)
    bpm = 100.0
    beat = 60 / bpm
    start = t_of(149)
    end = t_of(C.SLATE_F)
    prog = [(47, 59, 62, 66), (43, 55, 59, 62), (38, 50, 54, 57), (45, 57, 61, 64)]   # Bm  G  D  A (MIDI)
    hz = lambda n: 440 * 2 ** ((n - 69) / 12)   # noqa: E731
    t = start
    i = 0
    while t < end - 1e-6:
        chord = prog[(i // 8) % 4]
        dur = beat / 2
        n = int(dur * SR)
        lvl = 0.35 if t < t_of(193) else 0.6
        b = tone(hz(chord[0]), dur, "saw") * np.exp(-np.arange(n) / (0.09 * SR))
        b = band(b, 30, 1600) * 0.22 * lvl
        ar = tone(hz(chord[1 + i % 3] + 12), dur, "square") * np.exp(-np.arange(n) / (0.05 * SR))
        ar = band(ar, 200, 5000) * 0.05 * lvl
        add(m, b + ar, int(t * SR))
        if i % 8 == 0:
            pd_d = beat * 4
            pn = int(pd_d * SR)
            pad = sum(tone(hz(x + 12) * (1 + d), pd_d, "saw") for x in chord[1:] for d in (-0.003, 0.003))
            add(m, band(pad, 150, 2500) * env(pn, 0.4, 0.6) * 0.012 * lvl, int(t * SR))
        if t >= t_of(193) and i % 2 == 0:
            kn = int(0.18 * SR)
            kick = np.sin(2 * np.pi * np.cumsum(np.linspace(110, 45, kn)) / SR) * np.exp(-np.arange(kn) / (0.05 * SR)) * 0.25
            add(m, kick, int(t * SR))
        t += dur
        i += 1
    m[idx(C.SLATE_F):] *= 0.0
    cue("retro synth pulse (Bm-G-D-A, 100 bpm)", 149, C.SLATE_F - 1, "music")
    return m


def dialogue():
    d = np.zeros(N)
    for line in C.DIALOGUE:
        w = wave.open(os.path.join(C.P["audio"], "dialogue", f"{line['id']}.wav"))
        sr = w.getframerate()
        x = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(float) / 32768
        xs = np.interp(np.arange(int(len(x) * SR / sr)) * sr / SR, np.arange(len(x)), x)
        xs = band(xs, 90, 7000) * 0.9
        add(d, xs, idx(line["f0"]))
        cue(f"TOMMY: \"{line['text']}\"", line["f0"], line["f0"] + line["frames"], "dialogue")
    return d


def write(path, x):
    y = np.clip(x, -1, 1)
    y[-int(0.004 * SR):] *= np.linspace(1, 0, int(0.004 * SR))
    with wave.open(path, "w") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((y * 32767).astype(np.int16).tobytes())


if __name__ == "__main__":
    log = json.load(open(os.path.join(C.P["meta"], "build_log.json")))
    stems = dict(dialogue=dialogue(), music=music(), sfx=sfx(log), ambience=ambience())
    os.makedirs(os.path.join(C.P["audio"], "stems"), exist_ok=True)
    for k, v in stems.items():
        write(os.path.join(C.P["audio"], "stems", f"PS_GTA_EP01_{k}_stem.wav"), v)
    mix = stems["dialogue"] * 1.6 + stems["music"] * 0.8 + stems["sfx"] * 1.0 + stems["ambience"] * 1.4
    mix *= 0.89 / max(1e-9, np.abs(mix).max())
    write(os.path.join(C.P["audio"], "PS_GTA_EP01_temp_mix.wav"), mix)
    json.dump(sorted(CUES, key=lambda c: c["frame_in"]), open(os.path.join(C.P["meta"], "audio_cues.json"), "w"), indent=1)
    rms = 20 * np.log10(np.sqrt(np.mean(mix ** 2)))
    print(f"AUDIO {len(CUES)} cues; mix RMS {rms:.1f} dBFS; length {N / SR:.3f} s")
