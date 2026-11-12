"""Sound for the previs: synthesized SFX/ambience (numpy) timed from metadata/build_log.json, plus the dialogue guide.
    python3 scripts/audio.py
Writes audio/stems/LASTJOB_EP01_{dialogue,sfx,ambience}_stem.wav, audio/LASTJOB_EP01_mix.wav (48 kHz, 16-bit, stereo)
and metadata/audio_cues.json. The mix stops dead at frame 300 (hard cut)."""
import json
import os
import sys
import wave

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import config as C  # noqa: E402

SR = 48000
N = int((C.F1 + 1 - C.F0) / C.FPS * SR)
rng = np.random.default_rng(23)
CUES = []


def idx(f):
    return int((f - C.F0) / C.FPS * SR)


def cue(name, f0, f1=None, stem="sfx"):
    CUES.append(dict(cue=name, stem=stem, frame_in=f0, frame_out=f1 if f1 is not None else f0))


def band(x, lo, hi):
    X = np.fft.rfft(x)
    fr = np.fft.rfftfreq(len(x), 1 / SR)
    X[(fr < lo) | (fr > hi)] = 0
    return np.fft.irfft(X, len(x))


def noise(n):
    return rng.standard_normal(n)


def add(buf, sig, at):
    a, b = max(0, at), min(len(buf), at + len(sig))
    if b > a:
        buf[a:b] += sig[a - at:b - at]


def tone(freq, n, shape="sine"):
    ph = 2 * np.pi * np.cumsum(np.broadcast_to(freq, (n,)) if np.ndim(freq) else np.full(n, freq)) / SR
    return 2 * ((ph / (2 * np.pi)) % 1) - 1 if shape == "saw" else np.sin(ph)


def per_sample(values):
    """Frame-rate control curve -> sample-rate curve."""
    v = np.asarray(values, float)
    return np.interp(np.arange(N) / SR * C.FPS, np.arange(len(v)), v)


def sfx(log):
    s = np.zeros(N)
    fr = [log["frames"][str(f)] for f in range(C.F0, C.F1 + 1)]
    cy = np.array([x["car_y"] for x in fr])
    speed = np.abs(np.gradient(cy)) * C.FPS                       # m/s
    sp = per_sample(speed)
    interior = per_sample([0.0 if f < 30 else 1.0 for f in range(C.F0, C.F1 + 1)])
    # V8: firing rate follows road speed down to idle; muffled once we're inside the car
    rpm_hz = 22 + sp * 2.6
    eng = tone(rpm_hz, N, "saw") * 0.5 + tone(rpm_hz * 2, N, "saw") * 0.25 + band(noise(N), 40, 300) * 0.25
    lo = band(eng, 25, 220)
    hi = band(eng, 220, 2500)
    s += (lo * (0.30 - 0.10 * interior) + hi * (0.18 * (1 - interior) + 0.02 * interior))
    cue("V8 engine: braking to idle", 0, 299)
    # wet tyre hiss + brake scrub while decelerating, suspension clunk at the stop
    hiss = band(noise(N), 1500, 9000) * np.clip(sp / 15, 0, 1) * 0.10
    scrub = band(noise(N), 500, 3000) * np.clip((sp - 1) / 10, 0, 1) * per_sample([1 if 6 <= f <= 23 else 0 for f in range(300)]) * 0.12
    s += hiss + scrub
    cue("wet tyre hiss + brake scrub", 4, 23)
    n = int(0.25 * SR)
    clunk = (band(noise(n), 50, 400) * 0.6 + tone(55, n) * 0.4) * np.exp(-np.arange(n) / (0.05 * SR)) * 0.5
    add(s, clunk, idx(24))
    add(s, clunk * 0.4, idx(31))
    cue("suspension settles", 24, 34)
    # bag: lift rustle, weighted set-down thump
    for f0, dur, g in ((63, 0.45, 0.07), (84, 0.3, 0.05)):
        k = int(dur * SR)
        add(s, band(noise(k), 900, 6000) * np.sin(np.linspace(0, np.pi, k)) * g, idx(f0))
    k = int(0.18 * SR)
    add(s, (band(noise(k), 60, 500) * 0.7 + tone(80, k) * 0.3) * np.exp(-np.arange(k) / (0.035 * SR)) * 0.35, idx(88))
    cue("duffel lift rustle / set-down thump", 63, 90)
    # zipper: one tooth click per 3 mm of slider travel (Jason f94-116, Lucia f122-131)
    sx = np.array([x["slider_x"] for x in fr])
    pos = per_sample(sx)
    teeth = np.floor(pos / 0.003)
    clicks = np.flatnonzero(np.diff(teeth) != 0)
    k = int(0.006 * SR)
    tick = band(noise(k), 2500, 11000) * np.exp(-np.arange(k) / (0.0012 * SR))
    for c in clicks:
        add(s, tick * 0.22, c)
    cue("zipper teeth (synced to slider travel)", 94, 131)
    k = int(0.5 * SR)
    add(s, band(noise(k), 400, 4000) * np.sin(np.linspace(0, np.pi, k)) * 0.05, idx(132))
    cue("flaps fold open", 132, 144)
    # tag: card flick as it's flipped
    k = int(0.08 * SR)
    add(s, band(noise(k), 1800, 8000) * np.exp(-np.arange(k) / (0.015 * SR)) * 0.25, idx(C.TAG["flip"][0] + 3))
    cue("tag flick", C.TAG["flip"][0] + 3)
    # helicopter: blade-pass thump (~11 Hz) rising from far to overhead; searchlight switch-on clack
    t = np.arange(N) / SR
    env = np.clip((t - (226 / C.FPS)) / ((262 - 226) / C.FPS), 0, 1) ** 1.6
    blade = (0.5 + 0.5 * np.sign(np.sin(2 * np.pi * 11.2 * t))) * np.exp(-((t * 11.2) % 1) * 6)
    rotor = band(noise(N), 60, 900) * blade * 0.9 + band(tone(22.4, N, "saw"), 20, 200) * 0.4
    turb = band(noise(N), 800, 5000) * 0.15
    s += (rotor + turb) * env * 0.33
    cue("helicopter approach (rotor thump)", 226, 299)
    k = int(0.04 * SR)
    add(s, band(noise(k), 300, 3000) * np.exp(-np.arange(k) / (0.008 * SR)) * 0.4, idx(238))
    cue("searchlight on", 238)
    return s


def ambience():
    a = np.zeros(N)
    a += band(noise(N), 40, 600) * 0.025                          # night city bed
    a += (tone(60, N) * 0.5 + tone(120, N) * 0.3) * 0.008          # canopy neon/ballast hum
    t = np.arange(N) / SR
    siren = tone(700 + 380 * np.sin(2 * np.pi * t / 2.6), N) * 0.012   # distant police siren
    a += band(siren, 400, 2500)
    for _ in range(6):                                               # drips off the wet canopy
        at = rng.integers(0, N - SR // 10)
        k = int(0.03 * SR)
        a[at:at + k] += tone(1800 + rng.uniform(-300, 300), k) * np.exp(-np.arange(k) / (0.006 * SR)) * 0.03
    cue("night city bed, neon hum, distant siren, canopy drips", 0, 299, "ambience")
    return a


def dialogue():
    d = np.zeros(N)
    for line in C.DIALOGUE:
        w = wave.open(os.path.join(C.P["audio"], "dialogue", f"{line['id']}.wav"))
        x = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(float) / 32768
        add(d, x, idx(line["f0"]))
        cue(f"{line['who'].split('_')[0]}: \"{line['text']}\"", line["f0"], line["f1"], "dialogue")
    return d


def write(path, x, stereo=False):
    y = np.clip(x, -1, 1)
    y[-int(0.004 * SR):] *= np.linspace(1, 0, int(0.004 * SR))   # hard cut, de-clicked
    data = (y * 32767).astype(np.int16)
    if stereo:
        data = np.repeat(data, 2)
    with wave.open(path, "w") as w:
        w.setnchannels(2 if stereo else 1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(data.tobytes())


if __name__ == "__main__":
    log = json.load(open(os.path.join(C.P["meta"], "build_log.json")))
    stems = dict(dialogue=dialogue(), sfx=sfx(log), ambience=ambience())
    os.makedirs(os.path.join(C.P["audio"], "stems"), exist_ok=True)
    for k, v in stems.items():
        write(os.path.join(C.P["audio"], "stems", f"LASTJOB_EP01_{k}_stem.wav"), v)
    dl = np.abs(stems["dialogue"]) > 0.02                             # duck SFX/ambience under dialogue
    duck = np.convolve(dl.astype(float), np.ones(4800) / 4800, "same")
    mix = stems["dialogue"] * 1.3 + (stems["sfx"] * 0.9 + stems["ambience"]) * (1 - 0.45 * np.clip(duck * 3, 0, 1))
    mix *= 0.89 / max(1e-9, np.abs(mix).max())
    write(os.path.join(C.P["audio"], "LASTJOB_EP01_mix.wav"), mix, stereo=True)
    json.dump(sorted(CUES, key=lambda c: c["frame_in"]), open(os.path.join(C.P["meta"], "audio_cues.json"), "w"), indent=1)
    print(f"AUDIO {len(CUES)} cues, {N / SR:.3f} s, mix RMS {20 * np.log10(np.sqrt(np.mean(mix ** 2))):.1f} dBFS")
