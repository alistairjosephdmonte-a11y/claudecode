"""Original music, sound effects and lip-sync data for THE SEAT IS TAKEN.

Run with the Lemo-Opuscar Python env (numpy, scipy, soundfile, numba):
    LIB=/path/to/lemo-opuscar $LIB/.venv/bin/python audio-src/build_audio.py
Writes public/audio/sfx/*.wav, public/audio/music.wav, public/audio/sting.wav and src/generated/*.json.
"""
import json, os, sys
import numpy as np, soundfile as sf
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
LIB = os.environ['LIB']; sys.path.insert(0, LIB)
from core.audio import sfx as S
from core.audio import pluck as P
SR = S.SR; FPS = 30
rng = np.random.default_rng(42)
OUT = f'{ROOT}/public/audio'; os.makedirs(f'{OUT}/sfx', exist_ok=True); os.makedirs(f'{ROOT}/src/generated', exist_ok=True)

def save(name, x, peak=.8):
    x = np.asarray(x, float); m = np.abs(x).max()
    if m > 0: x = x / m * peak
    if x.ndim == 1: x = np.stack([x, x], 1)
    sf.write(f'{OUT}/{name}.wav', x.astype(np.float32), SR)

t_ = S.t_
def fade(x, a=.004, r=.02):
    n = len(x); e = np.ones(n); na, nr = int(a * SR), int(r * SR)
    e[:na] = np.linspace(0, 1, na); e[n - nr:] *= np.linspace(1, 0, nr); return x * e

# ---------- sound effects ----------
def door():
    d = 1.3; x = np.zeros(int(d * SR))
    latch = S.hp(S.noise(.05), 1500) * np.exp(-t_(.05) / .006) + .6 * np.sin(2 * np.pi * 900 * t_(.05)) * np.exp(-t_(.05) / .01)
    x[:len(latch)] += latch * .9
    cr = S.creak(.6); s = int(.08 * SR); x[s:s + len(cr)] += cr[:len(x) - s] * .35
    swish = S.bp(S.noise(.6), 200, 1200) * np.sin(np.pi * np.clip(t_(.6) / .6, 0, 1)); s = int(.15 * SR); x[s:s + len(swish)] += swish * .3
    room = S.lp(S.noise(d), 500) * .03; x += room
    return fade(x)
def bag():
    d = .9; t = t_(d); n = S.bp(S.noise(d), 1500, 7000)
    crinkle = np.zeros(len(t))
    for s in (rng.random(60) * (len(t) - 600)).astype(int): crinkle[s:s + 500] += S.hp(S.noise(500 / SR), 2500) * np.exp(-np.arange(500) / 80) * rng.random()
    return fade((n * .25 * (.5 + .5 * np.sin(2 * np.pi * 3 * t) ** 2) + crinkle) * np.sin(np.pi * np.clip(t / d, 0, 1)))
def fabric(d=.5):
    t = t_(d); return fade(S.bp(S.noise(d), 300, 2500) * np.sin(np.pi * np.clip(t / d, 0, 1)) ** 2)
def creak(v=1.0):
    d = .55; t = t_(d); f = 160 + 70 * np.sin(2 * np.pi * 1.4 * t)
    saw = np.zeros(len(t)); ph = np.cumsum(f) / SR
    for k in range(1, 12): saw += np.sin(2 * np.pi * k * ph) / k
    grit = (np.abs(np.sin(2 * np.pi * 35 * t)) ** 6)
    return fade(S.bp(saw * grit, 200, 2400) * np.sin(np.pi * np.clip(t / d, 0, 1)) * v)
def container():
    d = .7; x = np.zeros(int(d * SR))
    for s in (np.sort(rng.random(26)) * (len(x) - 900)).astype(int): x[s:s + 800] += S.bp(S.noise(800 / SR), 1200, 6000) * np.exp(-np.arange(800) / 140) * (.3 + rng.random())
    return fade(x)
def utensil():
    d = .35; x = np.zeros(int(d * SR))
    for s, f in ((0, 3100), (int(.13 * SR), 3500)):
        tt = t_(.2); hit = sum(a * np.sin(2 * np.pi * f * r * tt) * np.exp(-tt / tau) for r, a, tau in ((1, 1, .05), (2.7, .4, .02), (5.1, .2, .01)))
        x[s:s + len(hit)] += hit[:len(x) - s]
    return fade(x)
def tclick():
    d = .05; t = t_(d); return fade(S.hp(S.noise(d), 3000) * np.exp(-t / .002) * .6 + np.sin(2 * np.pi * 2400 * t) * np.exp(-t / .006) * .5, .001, .01)
def linedraw(d=.9):
    t = t_(d); x = S.bp(S.noise(d), 2500, 8000) * (.55 + .45 * np.sin(2 * np.pi * 7 * t)) * np.minimum(1, t / .05) * np.minimum(1, (d - t) / .1)
    return fade(x)
def step(v=1.0):
    d = .2; t = t_(d); return fade((S.lp(S.noise(d), 500) * np.exp(-t / .025) + .5 * np.sin(2 * np.pi * 85 * t) * np.exp(-t / .03)) * v)
def sit():
    d = 1.0; x = np.zeros(int(d * SR))
    th = S.lp(S.noise(.4), 220) * np.exp(-t_(.4) / .06) + .8 * np.sin(2 * np.pi * 70 * t_(.4)) * np.exp(-t_(.4) / .08); x[:len(th)] += th
    poof = S.bp(S.noise(.5), 300, 1500) * np.exp(-t_(.5) / .15); x[int(.02 * SR):int(.02 * SR) + len(poof)] += poof * .5
    c = creak(.6); s = int(.12 * SR); x[s:s + len(c)] += c[:len(x) - s] * .5
    return fade(x)
def fry_take():
    d = .3; t = t_(d); return fade(S.bp(S.noise(d), 1500, 6000) * np.exp(-t / .06) * .7 + container()[:len(t)] * .4)
def bite():
    d = .35; x = np.zeros(int(d * SR))
    for s in (0, int(.06 * SR), int(.1 * SR)):
        b = S.bp(S.noise(.12), 800, 5000) * np.exp(-t_(.12) / .02); x[s:s + len(b)] += b[:len(x) - s] * (.6 + rng.random() * .4)
    return fade(x)
def roomtone(d=15.0):
    x = S.lp(S.brown(d), 380) * .6 + S.bp(S.noise(d), 90, 140) * .05   # fridge hum + air
    return fade(x, .3, .3)

FX = {'door': door(), 'bag': bag(), 'fabric': fabric(), 'creak': creak(), 'container': container(), 'utensil': utensil(),
      'click': tclick(), 'linedraw': linedraw(), 'step': step(), 'sit': sit(), 'fry_take': fry_take(), 'bite': bite(),
      'roomtone': roomtone()}
for k, v in FX.items(): save(f'sfx/{k}', v, .25 if k == 'roomtone' else .8)

# ---------- music: restrained comic bass pulse (pizzicato bass + kalimba), F major, 112 bpm ----------
BPM = 112; beat = 60 / BPM; END = 13.9      # music stops after the punchline's last word
mus = np.zeros(int(15 * SR))
def put(x, t, g):
    s = int(t * SR)
    if s >= len(mus): return
    x = x[:len(mus) - s]; mus[s:s + len(x)] += x * g
bass = ['F2', 'F2', 'C3', 'A2', 'Bb2', 'Bb2', 'F2', 'C3', 'D3', 'D3', 'A2', 'F2', 'G2', 'G2', 'C3', 'E2']
CACHE = {}
def note(inst, p, d, v):
    k = (inst, p, d, v)
    if k not in CACHE: CACHE[k] = P.pluck(inst, p, d, vel=v)
    return CACHE[k]
i = 0; t = .05
while t < END - .1:
    put(note('upright_bass_pizz', bass[i % len(bass)], 1.0, .7), t, .9)
    if i % 2 == 1: put(note('upright_bass_pizz', bass[i % len(bass)], .5, .4), t + beat * .5, .35)   # little "walk" ghost note
    # soft brushed tick on the off-beat
    tk = S.hp(S.noise(.04), 6000) * np.exp(-t_(.04) / .008); put(tk, t + beat * .5, .12)
    i += 1; t += beat
# kalimba accents at story turns (shot 1, the diagram, Penny's entrance)
for at, notes in [(0.05, ['F4', 'A4', 'C5']), (6.35, ['C5', 'D5', 'F5']), (9.1, ['A4', 'C5', 'E5', 'G5'])]:
    for k, p in enumerate(notes): put(note('kalimba', p, 1.5, .5), at + k * beat * .5, .35)
e = np.ones(len(mus)); n0 = int(END * SR); e[n0:] = 0; e[n0 - int(.08 * SR):n0] = np.linspace(1, 0, int(.08 * SR))
mus *= e
mus = S.lp(mus, 5000)
save('music', mus, .7)
# comedic sting: two plucks and a kalimba "plink" (a dry button)
st = np.zeros(int(1.2 * SR))
for at, inst, p, v in [(0, 'upright_bass_pizz', 'C3', .8), (.2, 'upright_bass_pizz', 'F2', .9), (.2, 'kalimba', 'F5', .55), (.2, 'kalimba', 'C5', .45)]:
    x = note(inst, p, 1.0, v); s = int(at * SR); st[s:s + len(x)] += x[:len(st) - s]
save('sting', fade(st, .002, .15), .8)

# ---------- lip-sync envelopes (mouth open 0..1 per frame) ----------
lips, durs = {}, {}
for f in sorted(os.listdir(f'{OUT}/voice')):
    if not f.endswith('.wav'): continue
    x, sr = sf.read(f'{OUT}/voice/{f}')
    if x.ndim > 1: x = x.mean(1)
    hop = sr // FPS; n = len(x) // hop + 1
    env = np.array([np.sqrt(np.mean(x[i * hop:(i + 1) * hop] ** 2)) if i * hop < len(x) else 0 for i in range(n)])
    env = np.clip(env / (np.percentile(env, 95) + 1e-9), 0, 1)
    lips[f[:-4]] = [round(float(v), 3) for v in env]
    durs[f[:-4]] = round(len(x) / sr, 3)
json.dump(lips, open(f'{ROOT}/src/generated/lipsync.json', 'w'))
json.dump(durs, open(f'{ROOT}/src/generated/voice-durations.json', 'w'), indent=1)
print('audio ok', durs)
