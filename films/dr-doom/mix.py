"""Sound built from typography: clicks, impacts, tears, metal locks, sub pulses, drones → out/mix.wav"""
import json, os, sys
import numpy as np, soundfile as sf
HERE = os.path.dirname(os.path.abspath(__file__))
LIB = os.environ.get('LIB') or os.path.abspath(f'{HERE}/../..')
sys.path.insert(0, LIB)
from core.audio import sfx as S
SR = S.SR
ev = json.load(open(f'{HERE}/events.json')); DUR = ev['dur']; EV = ev['ev']
N = int((DUR + 1) * SR); tt = np.arange(N) / SR
rng = np.random.default_rng(1962)
fx = np.zeros((N, 2)); bed = np.zeros((N, 2)); vox = np.zeros((N, 2))

def env_ad(d, a=.005, tau=.2): t = S.t_(d); return np.minimum(1, t / a) * np.exp(-t / tau)
def sub(v=1, f0=58, d=2.2):
    t = S.t_(d); f = f0 * (1 + 1.6 * np.exp(-t / .05)); w = 2 * np.pi * np.cumsum(f) / SR
    x = np.sin(w) + .25 * np.sin(2 * w) + .12 * np.tanh(3 * np.sin(w))
    return S.norm(x * env_ad(d, .002, .55)) * v
def typew(v=1):
    d = .14; t = S.t_(d)
    hit = S.hp(S.noise(d), 1800) * np.exp(-t / .004)
    body = sum(a * np.sin(2 * np.pi * f * t) * np.exp(-t / tau) for f, a, tau in [(2100, .5, .02), (3400, .3, .012), (180, .6, .03), (95, .5, .05)])
    bell = .15 * np.sin(2 * np.pi * 4200 * t) * np.exp(-t / .06)
    return S.norm(hit * 1.2 + body + bell) * v
def metal(f0=420, d=1.2, v=1):
    t = S.t_(d); x = sum(a * np.sin(2 * np.pi * f0 * r * t + i) * np.exp(-t / (tau * d)) for i, (r, a, tau) in enumerate([(1, 1, .5), (2.32, .7, .35), (3.17, .5, .25), (4.6, .35, .18), (6.1, .25, .1)]))
    return S.norm(x * np.minimum(1, t / .001) + S.hp(S.noise(d), 3000) * np.exp(-t / .006) * .8) * v
def lock(v=1):
    a = typew(.8); b = metal(310 + rng.random() * 60, .6, .7); x = np.zeros(int(.8 * SR))
    x[:len(a)] += a; s = int(.045 * SR); x[s:s + len(b)] += b[:len(x) - s]; x[:int(.3 * SR)] += S.lp(S.noise(.3), 300) * np.exp(-S.t_(.3) / .03) * .8
    return S.norm(x) * v
def biglock():
    x = np.zeros(int(3 * SR)); a = lock(1); x[:len(a)] += a; b = sub(1, 46, 2.6); x[:len(b)] += b * 1.2
    c = metal(140, 2.5, .6); x[int(.02 * SR):int(.02 * SR) + len(c)] += c[:len(x) - int(.02 * SR)]
    return S.norm(x)
def boom(v=1):
    d = 2.6; x = S.lp(S.brown(d), 200, 4) * np.exp(-S.t_(d) / .7) + sub(1, 50, d) * 1.2
    return S.norm(x) * v
def slam(v=1):
    d = 1.4; a = boom(1)[:int(d * SR)]; c = S.bp(S.noise(d), 500, 3500) * np.exp(-S.t_(d) / .05)
    return S.norm(a + c * .8) * v
def shatter(v=1):
    d = 1.6; t = S.t_(d); x = np.zeros(len(t))
    for _ in range(40):
        s = int(rng.random() ** 2 * .9 * SR); l = int(.08 * SR); f = 2500 + rng.random() * 5000
        seg_ = np.sin(2 * np.pi * f * np.arange(l) / SR) * np.exp(-np.arange(l) / (.012 * SR)) * rng.random()
        x[s:s + l] += seg_[:len(x) - s]
    x += S.hp(S.noise(d), 2000) * np.exp(-t / .08) * .7
    return S.norm(x) * v
def tear():
    d = .8; t = S.t_(d); n = S.bp(S.noise(d), 700, 6000)
    am = (np.abs(np.sin(2 * np.pi * (40 + 60 * t) * t)) ** 4) * np.minimum(1, t / .05) * np.exp(-np.maximum(0, t - .55) / .05)
    return S.norm(n * am + S.hp(S.noise(d), 4000) * am * .3)
def ink():
    d = .9; t = S.t_(d); x = S.lp(S.noise(d), 900) * (np.abs(np.sin(2 * np.pi * 9 * t)) ** 3) * np.exp(-t / .3)
    return S.norm(x + .5 * np.sin(2 * np.pi * (300 - 200 * t) * t) * np.exp(-t / .1))
def shimmer(d):
    t = S.t_(d); x = sum(np.sin(2 * np.pi * f * t + 2 * np.sin(2 * np.pi * .7 * t)) / (k + 1) for k, f in enumerate([660, 990, 1320, 1765]))
    return S.norm(x * np.sin(np.pi * np.clip(t / d, 0, 1)) ** 2)
def whoosh(d=.45):
    t = S.t_(d); return S.norm(S.bp(S.noise(d), 400, 5000) * np.sin(np.pi * t / d) ** 3)
def burst():
    x = np.zeros(int(1.5 * SR))
    for _ in range(70):
        s = int(rng.random() * .9 * SR); c = typew(.2 + rng.random() * .5); x[s:s + len(c)] += c[:len(x) - s]
    b = boom(.6); x[:len(b)] += b[:len(x)]
    return S.norm(x)
def tick(v=.6): return typew(1)[:int(.05 * SR)] * v
def clack(v=1):
    d = .2; t = S.t_(d); p = .8 + rng.random() * .5
    x = S.hp(S.noise(d), 900) * np.exp(-t / .006) + sum(a * np.sin(2 * np.pi * f * p * t) * np.exp(-t / tau) for f, a, tau in [(900, .7, .03), (1700, .5, .02), (260, .6, .05)])
    return S.norm(x) * v
def stamp(): x = slam(1); c = metal(220, 1.0, .5); x[:len(c)] += c; return S.norm(x)
def tink(): t = S.t_(1.2); return S.norm(np.sin(2 * np.pi * 3700 * t) * np.exp(-t / .3) + .4 * np.sin(2 * np.pi * 5300 * t) * np.exp(-t / .15))
def collapse():
    d = 1.6; x = np.zeros(int(d * SR))
    for i in range(26):
        s = int((i / 26) ** .6 * 1.1 * SR); c = clack(.4 + rng.random() * .6); x[s:s + len(c)] += c[:len(x) - s]
    t = S.t_(d); x += S.lp(S.brown(d), 300) * np.minimum(1, t / .3) * .6
    return S.norm(x)
def thud(v=1): d = 1.6; return S.norm(sub(1, 44, d) + S.lp(S.noise(d), 400) * np.exp(-S.t_(d) / .04) * .7) * v
def crush(): d = .9; t = S.t_(d); x = S.bp(S.noise(d), 150, 2500) * (np.abs(np.sin(2 * np.pi * 30 * t)) ** 2) * np.sin(np.pi * t / d); return S.norm(x + .5 * sub(1, 40, d))
def crackle(d): x = np.zeros(int(d * SR)); [x.__setitem__(slice(s, s + 200), x[s:s + 200] + S.hp(S.noise(200 / SR), 3000) * rng.random()) for s in (rng.random(160) * (len(x) - 300)).astype(int)]; return S.norm(x)
def step(): return S.norm(sub(1, 38, 2.0) + .35 * metal(90, 2.0, 1))
def sweep(): d = .7; t = S.t_(d); return S.norm(np.sin(2 * np.pi * np.cumsum(300 + 2500 * t / d) / SR) * np.sin(np.pi * t / d) * .4 + S.bp(S.noise(d), 2000, 8000) * np.sin(np.pi * t / d))

def place(x, t, g=1.0, pan=0.0): S.add(fx, x, t, g, pan)

# beds: hum, drones, pulse, machine, rise
def tone_bed(t0, d, f0s, lp_hz, g, fi=.4, fo=.6, saw=False, rise=0.0):
    n = int(d * SR); t = np.arange(n) / SR; x = np.zeros(n)
    for f0 in f0s:
        f = f0 * (1 + rise * t / d); w = 2 * np.pi * np.cumsum(f) / SR
        x += (sum(np.sin(k * w) / k for k in range(1, 9)) if saw else np.sin(w) + .3 * np.sin(2 * w) + .15 * np.sin(3 * w))
    x = S.lp(x / len(f0s), lp_hz)
    e = np.minimum(1, np.minimum(t / fi, (d - t) / fo)); S.add(bed, x * e, t0, g)

for e in EV:
    t, k = e['t'], e['type']; v = e.get('v', 1)
    if k == 'sub': place(sub(v, 52, 2.4), t, .9)
    elif k == 'type': place(typew(v), t, .5, rng.uniform(-.3, .3))
    elif k == 'tick': place(tick(), t, .5)
    elif k == 'lock': place(lock(v), t, .55, rng.uniform(-.2, .2))
    elif k == 'biglock': place(biglock(), t, 1.0)
    elif k == 'boom': place(boom(v), t, .8)
    elif k == 'slam': place(slam(v), t, .85)
    elif k == 'shatter': place(shatter(v), t, .45)
    elif k == 'clack': place(clack(v), t, .3, rng.uniform(-.5, .5))
    elif k == 'ink': place(ink(), t, .4)
    elif k == 'tear': place(tear(), t, .5)
    elif k == 'shimmer': place(shimmer(e['d']), t, .12)
    elif k == 'burst': place(burst(), t, .6)
    elif k == 'whoosh': place(whoosh(), t, .4, .4)
    elif k == 'stamp': place(stamp(), t, .8)
    elif k == 'tink': place(tink(), t, .25, .4)
    elif k == 'collapse': place(collapse(), t, .55)
    elif k == 'thud': place(thud(v), t, .7)
    elif k == 'crush': place(crush(), t, .5)
    elif k == 'crackle': place(crackle(e['d']), t, .2)
    elif k == 'step': place(step(), t, .7)
    elif k == 'sweep': place(sweep(), t, .25)
    elif k == 'hum': tone_bed(t, e['d'], [50, 100.5], 400, .10, .8, .8)
    elif k == 'pulse':  # restless mechanical 16ths at 132 bpm, accents on the beat
        st = 60 / 132 / 4
        for i in range(int(e['d'] / st)):
            c = clack(.9 if i % 4 == 0 else .35); place(c, t + i * st, .22 if i % 4 == 0 else .12, (-1) ** i * .3)
        tone_bed(t, e['d'], [73.4, 110], 900, .07, .3, .4, saw=True)
    elif k == 'machine': tone_bed(t, e['d'], [55, 82.4], 1200, .09, 1.0, .02, saw=True, rise=.6)   # cut dead into the vacuum
    elif k == 'warble': tone_bed(t, e['d'], [233, 247], 2000, .03, .2, .02)
    elif k == 'swell': tone_bed(t, e['d'], [36.7, 55], 300, .14, 1.6, .3)
    elif k == 'rise': tone_bed(t, e['d'], [41.2, 61.7, 82.4], 700, .12, 2.5, .05, saw=True, rise=.25)
    elif k == 'drone': tone_bed(t, e['d'], [36.7, 55] if e.get('kind') == 'sub' else [32.7, 49, 65.4], 260, .16, 1.0, 1.2)

# voice
vg = np.zeros(N)
for e in EV:
    if e['type'] != 'voice': continue
    x, sr = sf.read(f"{HERE}/voice/{e['id']}.wav")
    if x.ndim > 1: x = x.mean(1)
    if sr != SR:
        import soxr; x = soxr.resample(x, sr, SR)
    x = S.compress(S.norm(x, .9), thr=.22, ratio=3.5)
    # a touch of low body + short room for authority
    x = x + .25 * S.lp(x, 220)
    S.add(vox, x, e['t'], 1.0, 0)
    vg[int((e['t'] - .2) * SR):int((e['t'] + len(x) / SR + .3) * SR)] = 1
k = int(.2 * SR); vg = np.convolve(vg, np.ones(k) / k, 'same')

def rms(x): m = np.abs(x).max(1) > 1e-4; return np.sqrt(np.mean(x[m] ** 2)) if m.any() else 1
vox *= .07 / rms(vox)
fxb = (fx + bed) * (1 - .45 * vg)[:, None]
fxb *= (.07 / 2.5) / rms(fxb)           # voice ~8 dB above the typographic sound
mix = (vox + fxb)[:int(DUR * SR)]
mix[-int(.3 * SR):] *= np.linspace(1, 0, int(.3 * SR))[:, None]
mix = np.stack([S.limit(mix[:, c], .95) for c in (0, 1)], 1)
os.makedirs(f'{HERE}/out', exist_ok=True)
sf.write(f'{HERE}/out/mix.wav', mix.astype(np.float32), SR)
print('mix', mix.shape, 'peak', float(np.abs(mix).max()))
