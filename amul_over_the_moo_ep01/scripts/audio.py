"""Original score and sound effects, synthesized from scratch (no samples, no existing recordings).
Stems (48 kHz, 16-bit WAV, exactly 30.000 s):
  music_stem.wav        piano, analog pads, bass, electric guitar, drums: an original 80s-style power ballad (B minor -> D)
  vocal_guide_stem.wav  the lead-vocal MELODY on a synth lead, for a singer to record over (no synthesized voice/lyrics)
  sfx_stem.wav          hooves (timed to the animation's hoof contacts), floor creaks, breathing, hoof scrape,
                        block scrape, door hinges
  ambience_stem.wav     morning birds and light wind (exterior), barn room tone (interior)
  temp_mix.wav          the stems mixed for the animatic
    python3 scripts/audio.py"""
import json
import math
import os
import wave

import numpy as np

import config as C

SR = 48000
DUR = C.TOTAL_FRAMES / C.FPS
N = int(DUR * SR)
rng = np.random.default_rng(5)
BPM = 84.0
BEAT = 60 / BPM


def t_shot(sid, sec=0.0):
    s = next(x for x in C.SHOTS if x["id"] == sid)
    return s["f0"] / C.FPS + sec


def buf():
    return np.zeros(N)


def add(dst, sig, t0, gain=1.0):
    i = int(t0 * SR)
    if i >= N or i + len(sig) <= 0:
        return
    j0 = max(0, -i)
    i = max(0, i)
    j = min(N, i + len(sig) - j0)
    dst[i:j] += sig[j0:j0 + (j - i)] * gain


def fft_filter(x, lo=None, hi=None, slope=2.0):
    X = np.fft.rfft(x)
    f = np.fft.rfftfreq(len(x), 1 / SR)
    g = np.ones_like(f)
    if hi:
        g *= 1 / (1 + (f / hi) ** (2 * slope))
    if lo:
        g *= 1 / (1 + (lo / np.maximum(f, 1e-3)) ** (2 * slope))
    return np.fft.irfft(X * g, len(x))


def env_adsr(n, a=0.01, d=0.1, s=0.7, r=0.2, total=None):
    total = total or n / SR
    t = np.arange(n) / SR
    e = np.where(t < a, t / max(a, 1e-4), np.where(t < a + d, 1 - (1 - s) * (t - a) / max(d, 1e-4), s))
    rel = np.clip((total - t) / max(r, 1e-4), 0, 1)
    return e * rel


def midi(m):
    return 440.0 * 2 ** ((m - 69) / 12)


# ------------------------------------------------------------------ instruments
def piano(m, dur, vel=0.6):
    n = int((dur + 1.2) * SR)
    t = np.arange(n) / SR
    f = midi(m)
    x = np.zeros(n)
    for k, a in enumerate([1.0, 0.55, 0.32, 0.18, 0.10, 0.06], 1):
        inh = 1 + 0.0004 * k * k
        x += a * np.sin(2 * np.pi * f * k * inh * t) * np.exp(-t * (1.2 + 0.9 * k))
    x *= np.clip((dur + 0.25 - t) / 0.25, 0, 1) ** 2
    x[: int(0.004 * SR)] *= np.linspace(0, 1, int(0.004 * SR))
    return x * vel * 0.25


def saw(f, t, detune=0.0):
    ph = (f * (1 + detune)) * t
    return 2 * (ph - np.floor(ph + 0.5))


def pad(ms, dur, vel=0.5, bright=1800):
    n = int((dur + 0.8) * SR)
    t = np.arange(n) / SR
    x = np.zeros(n)
    for m in ms:
        f = midi(m)
        x += saw(f, t, -0.004) + saw(f, t, 0.004) + 0.5 * saw(f * 0.5, t)
    x = fft_filter(x, lo=80, hi=bright)
    return x * env_adsr(n, a=0.6, d=0.3, s=0.85, r=0.8, total=dur + 0.8) * vel * 0.05


def bass(m, dur, vel=0.7):
    n = int((dur + 0.1) * SR)
    t = np.arange(n) / SR
    f = midi(m)
    x = 0.7 * np.sin(2 * np.pi * f * t) + 0.3 * saw(f, t)
    x = fft_filter(x, hi=700)
    return x * env_adsr(n, a=0.008, d=0.15, s=0.8, r=0.08, total=dur + 0.1) * vel * 0.35


def guitar(ms, dur, vel=0.6, drive=6.0, palm=False):
    n = int((dur + 0.4) * SR)
    t = np.arange(n) / SR
    x = np.zeros(n)
    for i, m in enumerate(ms):
        f = midi(m)
        vib = 1 + 0.003 * np.sin(2 * np.pi * 5.5 * t) * np.clip(t - 0.4, 0, 1)
        x += saw(f * vib, t, 0.002 * i) + 0.6 * saw(f * 2.0 * vib, t, -0.003)
    x = np.tanh(x * drive) * 0.8
    x = fft_filter(x, lo=110, hi=3800 if not palm else 1400, slope=2.5)
    e = env_adsr(n, a=0.006, d=0.25 if palm else 0.4, s=0.25 if palm else 0.85, r=0.3, total=dur + 0.4)
    return x * e * vel * 0.12


def lead(m, dur, vel=0.6, glide_from=None):
    """Vocal-guide lead: triangle-ish tone with vibrato and an 'ah' formant (a melody guide, not a voice)."""
    n = int((dur + 0.15) * SR)
    t = np.arange(n) / SR
    f0 = midi(m)
    f = np.full(n, f0)
    if glide_from is not None:
        g = int(0.08 * SR)
        f[:g] = np.linspace(midi(glide_from), f0, g)
    f = f * (1 + 0.006 * np.sin(2 * np.pi * 5.2 * t) * np.clip((t - 0.25) / 0.3, 0, 1))
    ph = np.cumsum(f) / SR
    x = 2 * np.abs(2 * (ph - np.floor(ph + 0.5))) - 1
    x = x + 0.25 * np.sin(2 * np.pi * ph * 2)
    y = fft_filter(x, lo=300, hi=2600) + 0.6 * fft_filter(x, lo=650, hi=1100)
    return y * env_adsr(n, a=0.05, d=0.1, s=0.9, r=0.12, total=dur + 0.15) * vel * 0.2


def kick(vel=1.0):
    n = int(0.45 * SR)
    t = np.arange(n) / SR
    f = 50 + 90 * np.exp(-t * 35)
    x = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 7)
    x[: 200] += rng.standard_normal(200) * 0.3 * np.linspace(1, 0, 200)
    return x * vel * 0.6


def snare(vel=1.0, room=True):
    n = int(0.6 * SR)
    t = np.arange(n) / SR
    nz = fft_filter(rng.standard_normal(n), lo=900, hi=9000) * np.exp(-t * (9 if room else 16))
    tone = np.sin(2 * np.pi * 190 * t) * np.exp(-t * 22)
    x = 0.5 * nz / np.max(np.abs(nz)) + 0.5 * tone
    if room:                                  # big 80s room tail
        tail = fft_filter(rng.standard_normal(n), lo=500, hi=5000) * np.exp(-t * 4.5) * 0.18
        x += tail / max(1e-6, np.max(np.abs(tail))) * 0.25
    return x * vel * 0.45


def hat(vel=0.5, open_=False):
    n = int((0.3 if open_ else 0.06) * SR)
    t = np.arange(n) / SR
    x = fft_filter(rng.standard_normal(n), lo=7000) * np.exp(-t * (10 if open_ else 60))
    return x / np.max(np.abs(x)) * vel * 0.12


def tom(m, vel=0.8):
    n = int(0.5 * SR)
    t = np.arange(n) / SR
    f = midi(m) * (1 + 0.5 * np.exp(-t * 20))
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 6) * vel * 0.4


def crash(vel=0.6):
    n = int(2.2 * SR)
    t = np.arange(n) / SR
    x = fft_filter(rng.standard_normal(n), lo=3500) * np.exp(-t * 1.6)
    return x / np.max(np.abs(x)) * vel * 0.12


# ------------------------------------------------------------------ the score
CH = {"Bm": [47, 54, 59, 62, 66], "G": [43, 50, 55, 59, 62], "D": [50, 57, 62, 66, 69], "A": [45, 52, 57, 61, 64],
      "Em": [40, 47, 52, 55, 59], "F#": [42, 49, 54, 58, 61]}
ROOT = {"Bm": 35, "G": 31, "D": 38, "A": 33, "Em": 28, "F#": 30}


def music():
    mu, gt, dr = buf(), buf(), buf()
    # 0-7 s: soft piano (Bm - G - D - A), gentle pad from 2 s
    prog = [("Bm", 0.0), ("G", 1.75), ("D", 3.5), ("A", 5.25), ("Bm", 7.0), ("G", 8.0), ("Em", 9.0), ("F#", 10.0),
            ("Bm", 11.0), ("G", 13.0), ("F#", 14.2), ("Bm", 15.0), ("G", 16.0), ("D", 17.0), ("A", 18.0),
            ("D", 19.0), ("A", 20.0), ("Bm", 21.0), ("G", 22.0), ("D", 23.0), ("A", 24.0), ("G", 25.5),
            ("Em", 27.0), ("A", 28.0), ("D", 29.0)]
    for i, (ch, t0) in enumerate(prog):
        t1 = prog[i + 1][1] if i + 1 < len(prog) else 30.0
        dur = t1 - t0
        notes = CH[ch]
        arp = [notes[0] + 12, notes[2] + 12, notes[3] + 12, notes[4] + 12, notes[3] + 12, notes[2] + 12]
        step = BEAT / 2
        k = 0
        tt = t0
        pv = 0.45 if t0 < 11 or 15 <= t0 < 19 else 0.32
        while tt < t1 - 0.01:
            add(mu, piano(arp[k % len(arp)], step * 1.6, pv), tt)
            tt += step
            k += 1
        if t0 >= 2.0:
            add(mu, pad(notes[1:4], dur, vel=0.35 if t0 < 19 else 0.6, bright=1400 if t0 < 19 else 2600), t0)
        if t0 >= 7.0:                                          # bass enters with the barn
            pattern = [0.0, BEAT * 1.5, BEAT * 2] if t0 < 19 else [0.0, BEAT, BEAT * 1.5, BEAT * 2, BEAT * 3]
            for off in pattern:
                if t0 + off < t1:
                    add(mu, bass(ROOT[ch] + 12, min(BEAT * 0.9, t1 - t0 - off), 0.75 if t0 >= 19 else 0.55), t0 + off)
        if t0 >= 19.0:                                        # electric guitar: power chords, then the anthem
            r = ROOT[ch] + 24
            for off in np.arange(0, dur - 0.01, BEAT / 2):
                add(gt, guitar([r, r + 7, r + 12], BEAT / 2 * 0.95, 0.55 if t0 < 22 else 0.75, palm=t0 < 22), t0 + off)
    # 14.0 s: the short guitar sting when the block does not move
    add(gt, guitar([47 + 12, 54 + 12, 59 + 12], 0.9, 0.7, drive=9), t_shot("S04", 3.0))
    # 22-24 s: full anthem lead line; 24-27 s: sustained guitar note
    add(gt, guitar([78], 2.9, 0.75, drive=10), t_shot("S08", 0.05))
    # drums: from 11 s a heartbeat kick, the rising fill at 18-19 s, full kit from 19 s, final hit, abrupt stop
    for k in np.arange(t_shot("S04"), t_shot("S05", 2.6), BEAT * 2):
        add(dr, kick(0.45), k)
    fill_t = t_shot("S05", 2.7)
    for i, m in enumerate([50, 50, 47, 47, 45, 45, 43, 43, 40, 40, 38, 38]):
        add(dr, tom(m + 12, 0.35 + i * 0.05), fill_t + i * (BEAT / 4) * 0.98)
    add(dr, snare(0.8), t_shot("S06") - 0.05)
    t = t_shot("S06")
    while t < 29.95:
        bi = round((t - t_shot("S06")) / BEAT)
        add(dr, kick(0.9 if t > t_shot("S07") else 0.7), t)
        if bi % 2 == 1:
            add(dr, snare(1.0 if t > t_shot("S07") else 0.8), t)
        add(dr, hat(0.5), t)
        add(dr, hat(0.35), t + BEAT / 2)
        t += BEAT
    for ct in (t_shot("S07"), t_shot("S08"), t_shot("S09"), t_shot("S10")):
        add(dr, crash(0.7), ct)
    gt *= 2.4
    mix = mu + gt + dr
    return mix, dict(piano_pads_bass=mu, guitars=gt, drums=dr)


# vocal guide: phrases placed on the shots (lyrics from the brief; melody original)
VOCAL = [
    ("S02", 0.25, "They see a little shadow,", [(66, 0.32), (66, 0.32), (69, 0.32), (71, 0.6), (69, 0.32), (66, 0.7)]),
    ("S03", 0.10, "Standing in the light...", [(64, 0.32), (66, 0.32), (62, 0.32), (61, 0.5), (59, 1.3)]),
    ("S06", 0.10, "But every mountain starts", [(62, 0.28), (66, 0.28), (69, 0.28), (71, 0.42), (73, 0.28), (74, 0.7)]),
    ("S07", 0.15, "With one small climb...", [(73, 0.3), (71, 0.3), (69, 0.3), (71, 0.9)]),
    ("S08", 0.30, "I've got something to prove tonight!", [(74, 0.26), (74, 0.26), (76, 0.26), (78, 0.4), (76, 0.26), (74, 0.26),
                                                            (73, 0.26), (74, 1.1)]),
    ("S09", 0.30, "(ascending)", [(74, 0.3), (76, 0.3), (78, 0.3), (81, 0.9)]),
    ("S10", 0.05, "(final note)", [(81, 0.95)]),
]


def vocal_guide():
    v = buf()
    sheet = []
    for sid, off, words, notes in VOCAL:
        t = t_shot(sid, off)
        sheet.append({"t": round(t, 3), "shot": sid, "lyric": words, "notes_midi": [n for n, _ in notes]})
        prev = None
        for m, d in notes:
            add(v, lead(m, d, 0.65, glide_from=prev), t)
            prev = m
            t += d
    return v, sheet


# ------------------------------------------------------------------ effects and ambience
def noise_burst(dur, lo, hi, decay, vel):
    n = int(dur * SR)
    t = np.arange(n) / SR
    x = fft_filter(rng.standard_normal(n), lo=lo, hi=hi)
    x /= max(1e-6, np.max(np.abs(x)))
    return x * np.exp(-t * decay) * (1 - np.exp(-t * 400)) * vel


def hoof(surface):
    if surface == "grass":
        return noise_burst(0.12, 120, 1800, 38, 0.10) + noise_burst(0.12, 2500, 7000, 60, 0.03)
    n = int(0.18 * SR)
    t = np.arange(n) / SR
    knock = np.sin(2 * np.pi * 210 * t) * np.exp(-t * 45) * 0.12
    return knock + noise_burst(0.18, 300, 4000, 50, 0.08)


def creak(dur, f0, f1, vel):
    n = int(dur * SR)
    t = np.arange(n) / SR
    f = np.linspace(f0, f1, n) * (1 + 0.04 * np.sin(2 * np.pi * 23 * t))
    x = np.sign(np.sin(2 * np.pi * np.cumsum(f) / SR)) * (rng.random(n) > 0.35)
    x = fft_filter(x.astype(float), lo=400, hi=2400)
    x /= max(1e-6, np.max(np.abs(x)))
    return x * np.sin(np.pi * np.clip(t / dur, 0, 1)) * vel


def breath(dur, vel, strain=False):
    n = int(dur * SR)
    t = np.arange(n) / SR
    x = fft_filter(rng.standard_normal(n), lo=350 if not strain else 250, hi=2200 if not strain else 1600)
    x /= max(1e-6, np.max(np.abs(x)))
    return x * np.sin(np.pi * np.clip(t / dur, 0, 1)) ** 1.5 * vel


def scrape(dur, vel, lo=200, hi=2500, grit=40):
    n = int(dur * SR)
    t = np.arange(n) / SR
    x = fft_filter(rng.standard_normal(n), lo=lo, hi=hi)
    am = 0.6 + 0.4 * np.abs(np.sin(2 * np.pi * grit * t + rng.random() * 6))
    x /= max(1e-6, np.max(np.abs(x)))
    return x * am * np.sin(np.pi * np.clip(t / dur, 0, 1)) * vel


def bird(f0, vel):
    n = int(0.22 * SR)
    t = np.arange(n) / SR
    f = f0 * (1 + 0.35 * np.sin(2 * np.pi * 14 * t)) * (1 + 0.4 * t)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.sin(np.pi * t / 0.22) ** 2 * vel


def hoof_contacts():
    log = json.load(open(os.path.join(C.P["meta"], "build_log.json")))
    poses = {int(k): v for k, v in log["poses"].items()}
    events = []
    for leg in ("rear_near", "rear_far", "front_near", "front_far"):
        prev = None
        for f in sorted(poses):
            v = poses[f]["hooves"][leg][1]
            if prev is not None and prev > 0.004 and v <= 0.004:
                events.append((f, leg, poses[f]["shot"]))
            prev = v
    return events


def sfx_and_ambience():
    fx, amb = buf(), buf()
    ext_end = t_shot("S03")
    t = np.arange(N) / SR
    wind = fft_filter(rng.standard_normal(N), lo=80, hi=900)
    wind /= np.max(np.abs(wind))
    gust = 0.6 + 0.4 * np.sin(2 * np.pi * 0.11 * t + 1.0)
    room = fft_filter(rng.standard_normal(N), lo=40, hi=300)
    room /= np.max(np.abs(room))
    xf = np.clip((t - ext_end + 0.15) / 0.3, 0, 1)
    amb += wind * gust * 0.035 * (1 - xf) + room * 0.02 * xf
    tb = 0.3
    while tb < ext_end - 0.3:
        for k in range(rng.integers(2, 5)):
            add(amb, bird(rng.uniform(2600, 4200), rng.uniform(0.012, 0.03)), tb + k * rng.uniform(0.12, 0.2))
        tb += rng.uniform(0.6, 1.4)
    for f, leg, shot in hoof_contacts():
        sec = (f - 1) / C.FPS
        add(fx, hoof("grass" if shot in ("S01", "S02") else "wood"), sec, 1.0 if leg.startswith("front") else 0.85)
    # interior: floor creaks under the walk, the first attempt, the recovery and the final step
    for sec, d, f0, f1, v in ((t_shot("S03", 1.2), 0.5, 120, 90, 0.02), (t_shot("S04", 1.6), 0.7, 95, 70, 0.025),
                              (t_shot("S05", 0.4), 0.5, 110, 80, 0.02), (t_shot("S10", 0.4), 0.5, 100, 75, 0.02)):
        add(fx, creak(d, f0, f1, v), sec)
    # breathing: quiet exterior, strained on the pushes, heavy after the breakthrough
    for sec, d, v, st in ((t_shot("S01", 1.0), 1.4, 0.02, False), (t_shot("S02", 2.3), 0.9, 0.025, False),
                          (t_shot("S04", 1.0), 1.8, 0.05, True), (t_shot("S05", 0.3), 0.8, 0.04, False), (t_shot("S05", 1.6), 0.8, 0.03, False),
                          (t_shot("S06", 0.5), 1.4, 0.06, True), (t_shot("S07", 0.0), 1.6, 0.065, True),
                          (t_shot("S08", 0.0), 0.5, 0.06, False), (t_shot("S08", 0.6), 0.5, 0.055, False), (t_shot("S08", 1.2), 0.55, 0.045, False),
                          (t_shot("S08", 1.9), 0.6, 0.035, False)):
        add(fx, breath(d, v, st), sec)
    add(fx, scrape(0.4, 0.10, lo=600, hi=5000, grit=60), t_shot("S04", 2.55))          # rear hooves slip
    add(fx, scrape(1.0, 0.05, lo=500, hi=4000, grit=30), t_shot("S06", 0.6))           # hooves gripping timber
    add(fx, scrape(0.9, 0.12, lo=120, hi=1400, grit=18), t_shot("S06", 2.1))           # block begins to scrape
    add(fx, scrape(1.5, 0.16, lo=100, hi=1600, grit=14), t_shot("S07", 0.0))           # block slides 5-8 cm
    add(fx, creak(2.0, 260, 180, 0.05), t_shot("S09", 0.3))                             # hinges, two leaves
    add(fx, creak(1.6, 300, 210, 0.035), t_shot("S09", 0.45))
    add(fx, creak(1.0, 200, 170, 0.03), t_shot("S10", 0.0))
    return fx, amb


def write(path, x, gain=1.0):
    y = np.clip(x * gain, -1, 1)
    pcm = (np.stack([y, y], axis=1) * 32767).astype("<i2")
    with wave.open(path, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(pcm.tobytes())


if __name__ == "__main__":
    os.makedirs(C.P["stems"], exist_ok=True)
    m, parts = music()
    v, sheet = vocal_guide()
    fx, amb = sfx_and_ambience()
    cut = np.ones(N)
    cut[-int(0.004 * SR):] = np.linspace(1, 0, int(0.004 * SR))     # abrupt cutoff at 30.000 s (4 ms de-click)
    stems = {"music_stem": m * cut, "vocal_guide_stem": v * cut, "sfx_stem": fx * cut, "ambience_stem": amb * cut}
    peak = max(np.max(np.abs(s)) for s in stems.values())
    mix = stems["music_stem"] * 0.9 + stems["vocal_guide_stem"] * 1.3 + stems["sfx_stem"] * 1.5 + stems["ambience_stem"] * 2.0
    g = 0.89 / max(np.max(np.abs(mix)), 1e-6)
    for k, s in stems.items():
        write(os.path.join(C.P["stems"], f"AMUL_OTM_EP01_{k}.wav"), s, g * {"music_stem": 0.9, "vocal_guide_stem": 1.3, "sfx_stem": 1.5, "ambience_stem": 2.0}[k])
    for k, s in parts.items():
        write(os.path.join(C.P["stems"], f"AMUL_OTM_EP01_music_sub_{k}.wav"), s * cut, g * 0.9)
    write(os.path.join(C.P["audio"], "AMUL_OTM_EP01_temp_mix.wav"), mix, g)
    json.dump({"bpm": BPM, "key": "B minor -> D major", "vocal_guide": sheet, "hoof_contacts": len(hoof_contacts()),
               "note": "All audio synthesized in scripts/audio.py. The vocal stem is a melody guide on a synth lead: the lyrics "
                       "must be sung by a vocalist. No existing recording or soundtrack is reproduced."},
              open(os.path.join(C.P["meta"], "audio_cues.json"), "w"), indent=1)
    print("AUDIO", N / SR, "s; vocal phrases", len(sheet))
