"""Score, foley and voice → out/mix.wav. Reads events.json (exported from the page) and timeline.json."""
import json, os, sys
import numpy as np, soundfile as sf
HERE = os.path.dirname(os.path.abspath(__file__))
LIB = os.environ.get('LIB') or os.path.abspath(f'{HERE}/../..')
sys.path.insert(0, LIB)
from core.audio import sfx as S
from core.audio import pluck as P
SR = S.SR

ev = json.load(open(f'{HERE}/events.json'))
DUR = ev['dur']; EV = ev['ev']
T = json.load(open(f'{HERE}/timeline.json'))['T']
N = int(DUR * SR) + SR
rng = np.random.default_rng(1945)

music = np.zeros((N, 2)); amb = np.zeros((N, 2)); fol = np.zeros((N, 2)); vox = np.zeros((N, 2))
tt = np.arange(N) / SR

def ramp(points):
    """piecewise-linear envelope over the whole film: [(t, gain), ...]"""
    xs, ys = zip(*points); return np.interp(tt, xs, ys)

def hz(m): return 440 * 2 ** ((m - 69) / 12)
def mid(p): return P.midi(p)

# ---------------- drones ----------------
def drone(notes, lp_hz=900):
    x = np.zeros(N)
    for i, n in enumerate(notes):
        f = hz(mid(n)); ph = rng.random() * 6
        vib = 1 + .002 * np.sin(2 * np.pi * (.13 + i * .05) * tt + ph)
        w = 2 * np.pi * f * np.cumsum(vib) / SR
        x += np.sin(w) + .35 * np.sin(2 * w) + .18 * np.sin(3 * w + ph)
    return S.lp(x / len(notes), lp_hz)

warm = drone(['D2', 'A2', 'D3'], 700)
dark = drone(['D2', 'Eb2', 'A2'], 380)
g_warm = ramp([(0, 0), (2.5, .09), (23.9, .09), (24.0, 0), (74, 0), (77, .07), (113, .07), (118, .04), (133.5, 0), (DUR, 0)])
g_dark = ramp([(0, 0), (28.0, 0), (31, .1), (44, .1), (47, .05), (56.2, .05), (56.3, 0), (58, 0), (60, .09), (62.5, .06), (64, 0), (DUR, 0)])
for c in (0, 1): music[:, c] += warm * g_warm + dark * g_dark

# ---------------- koto ----------------
KOTO = {}
def koto(t, p, d=2.5, v=.6, pan=0.0, gain=1.0):
    k = (p, round(v, 2))
    if k not in KOTO: KOTO[k] = P.pluck('koto', p, d, vel=v)
    S.add(music, KOTO[k], t, .32 * gain, pan)

IN = ['D4', 'Eb4', 'G4', 'A4', 'Bb4', 'D5']
phr = [[('D4', 0), ('Eb4', .55), ('G4', 1.1), ('A4', 1.9)],
       [('Bb4', 0), ('A4', .5), ('G4', 1.0), ('D4', 1.8)],
       [('D3', 0), ('A3', .6), ('D4', 1.4)],
       [('G4', 0), ('A4', .45), ('Bb4', .9), ('A4', 1.6)],
       [('Eb4', 0), ('D4', .7), ('A3', 1.5)],
       [('D4', 0), ('A4', .9)]]
for i, s0 in enumerate([0.6, 4.6, 8.6, 12.6, 16.6, 20.4]):
    for p, dt in phr[i]: koto(s0 + dt, p, v=.55, pan=-.2 + .08 * i)
# Kokura / Nagasaki: single low notes
for t in (47.0, 51.0, 54.2): koto(t, 'D3', 3.0, .5, 0, .8)
# cranes: one note per crane, climbing through the scale
cr = [e['t'] for e in EV if e['type'] == 'paper']
for i, t in enumerate(cr): koto(t, IN[(i * 2) % 5] if i < 18 else IN[i % 6], 2.2, .42, -.4 + (i % 5) * .2, .8)
# flight: rising arpeggio
for i in range(18):
    p = ['D5', 'Eb5', 'G5', 'A5', 'Bb5', 'D6'][i % 6]
    koto(92.2 + i * .26, p, 1.8, .4, -.6 + (i % 7) * .2, .7)
# ending
for p, dt in [('D4', 0), ('A4', .6), ('D5', 1.3)]: koto(97.3 + dt, p, 3, .5)
for p, dt in [('G4', 0), ('A4', .5), ('Bb4', 1.0), ('A4', 1.7)]: koto(105.6 + dt, p, 3, .48, .2)
for p in ('D3', 'A3', 'D4'): koto(111.0, p, 5, .5, 0)

# ---------------- ambience ----------------
def cicadas(d, v=1.0):
    t_ = S.t_(d); x = S.bp(S.noise(d), 4300, 6800, 3)
    am = (.5 + .5 * np.sin(2 * np.pi * 38 * t_)) ** 3 * (.55 + .45 * np.sin(2 * np.pi * t_ / 5.5) ** 2)
    return S.norm(x * am) * v
def bed(t0, t1, x, gain, fi=1.0, fo=1.0, pan=0):
    n = int((t1 - t0) * SR); x = np.resize(x, n)
    e = np.minimum(1, np.minimum(np.arange(n) / (fi * SR + 1), (n - np.arange(n)) / (fo * SR + 1)))
    S.add(amb, x * e, t0, gain, pan)

bed(0, 22.8, cicadas(23), .05, 1.5, .8, -.3)
bed(0, 22.8, cicadas(23) * .8, .04, 1.5, .8, .4)
bed(96.2, 113.5, cicadas(17.5), .035, 2, 2.5, .2)
wind = S.norm(S.bp(S.brown(20), 150, 900))
bed(28.0, 45.2, wind, .12, 2.5, 1.0)
bed(57.5, 63.2, wind, .1, 1.5, .8)
hwind = S.norm(S.bp(S.noise(10), 700, 2600)) * (.6 + .4 * np.sin(np.linspace(0, 6, int(10 * SR))))
bed(45.0, 53.6, hwind, .05, 1, .6)
rain = S.norm(S.bp(S.noise(13), 2000, 7000))
bed(33.0, 45.0, rain, .045, 2.0, 1.5)
crack = np.zeros(int(17 * SR))
for _ in range(90):
    p = int(rng.random() * (len(crack) - 2000)); crack[p:p + 600] += S.hp(S.noise(600 / SR), 2500) * np.exp(-np.arange(600) / 90) * rng.random()
bed(28.5, 45.0, crack, .18, 1, 1)
static = S.norm(S.bp(S.noise(10), 900, 4200)) * (.7 + .3 * np.sin(np.linspace(0, 40, int(10 * SR))))
for _ in range(60):
    p = int(rng.random() * (len(static) - 800)); static[p:p + 400] += S.noise(400 / SR) * .8
bed(63.2, 72.2, static, .03, 1.2, .8, .25)
room = S.norm(S.lp(S.brown(12), 400))
bed(72.0, 74.6, room, .03, .3, .3)

# ---------------- foley ----------------
def tick(v):
    d = .03; t_ = S.t_(d)
    return S.norm(S.hp(S.noise(d), 3000) * S.env_exp(d, .002) + .6 * np.sin(2 * np.pi * 3400 * t_) * S.env_exp(d, .004)) * v
def bell():
    d = 9.0; t_ = S.t_(d); f0 = 98.0
    x = sum(a * np.sin(2 * np.pi * f0 * r * t_ + i) * np.exp(-t_ / tau) * (1 + .15 * np.sin(2 * np.pi * (1.6 + i * .7) * t_))
            for i, (r, a, tau) in enumerate([(1, 1, 5.5), (2.0, .55, 3.5), (2.76, .5, 2.8), (3.6, .3, 2.0), (5.4, .2, 1.2), (.5, .4, 6.5)]))
    strike = S.lp(S.noise(d), 600) * S.env_exp(d, .02) * .4
    return S.norm(x + strike)
def ring(d=2.6):
    t_ = S.t_(d); return np.sin(2 * np.pi * 3150 * t_) * np.exp(-t_ / .9) * np.minimum(1, t_ / .05)
def rumble(d, v):
    x = S.lp(S.brown(d), 120, 4); t_ = S.t_(d)
    e = np.minimum(1, t_ / (d * .3)) * np.exp(-np.maximum(0, t_ - d * .3) / (d * .3))
    return S.norm(x * e) * v
def plane(d):
    t_ = S.t_(d); f = 92 + 6 * np.sin(np.pi * t_ / d)
    w = 2 * np.pi * np.cumsum(f) / SR
    x = sum(np.sin(k * w) / k for k in range(1, 8)) + .4 * S.bp(S.noise(d), 200, 900)
    e = np.sin(np.pi * np.clip(t_ / d, 0, 1)) ** 1.5
    return S.norm(S.lp(x, 700) * e)
def paper():
    d = .22; t_ = S.t_(d)
    return S.norm(S.bp(S.noise(d), 1800, 7000) * np.exp(-t_ / .05) * (1 + .5 * np.sin(2 * np.pi * 60 * t_)))
def wings(d):
    t_ = S.t_(d); x = S.bp(S.noise(d), 500, 3000)
    am = (.5 + .5 * np.sin(2 * np.pi * 7.5 * t_)) ** 2 * np.sin(np.pi * np.clip(t_ / d, 0, 1))
    return S.norm(x * am)
def tram_bell():
    d = 1.2; t_ = S.t_(d); x = sum(a * np.sin(2 * np.pi * f * t_) * np.exp(-t_ / tau) for f, a, tau in [(1560, 1, .35), (2480, .6, .25), (3900, .3, .15)])
    return S.norm(x)

for e in EV:
    t, k = e['t'], e['type']
    if k == 'tick': S.add(fol, tick(1), t, .05 * e.get('v', 1) + (.06 if e.get('v', 1) >= 1 else 0), .3)
    elif k == 'tram':
        S.add(fol, tram_bell(), t, .06, .5); S.add(fol, tram_bell(), t + .3, .05, .5)
        S.add(fol, S.norm(S.bp(S.noise(6), 80, 600)) * np.sin(np.linspace(0, np.pi, int(6 * SR))), t, .05, .6)
    elif k == 'plane': S.add(fol, plane(e['d']), t, .09 if t < 30 else .12, 0)
    elif k == 'flash':
        S.add(fol, ring(), t, .03 if e['big'] else .02, 0)
        S.add(fol, rumble(7 if e['big'] else 5, 1), t + (1.0 if e['big'] else .6), .55 if e['big'] else .4, 0)
    elif k == 'bell': S.add(fol, bell(), t, .4, 0)
    elif k == 'paper': S.add(fol, paper(), t, .07, rng.uniform(-.4, .4))
    elif k == 'wings': S.add(fol, wings(e['d']), t, .08, .3)

# ---------------- voice ----------------
vg = np.zeros(N)
for e in EV:
    if e['type'] != 'voice': continue
    x, sr = sf.read(f"{HERE}/voice/{e['id']}.wav")
    if x.ndim > 1: x = x.mean(1)
    if sr != SR:
        import soxr; x = soxr.resample(x, sr, SR)
    x = S.compress(S.norm(x, .9), thr=.25, ratio=3.0)
    S.add(vox, x, e['t'], 1.0, 0)
    s0 = int((e['t'] - .25) * SR); s1 = int((e['t'] + len(x) / SR + .35) * SR); vg[max(0, s0):s1] = 1
# smooth duck envelope
k = int(.25 * SR); vg = np.convolve(vg, np.ones(k) / k, 'same')
duck = 1 - .5 * vg

def rms(x): return np.sqrt(np.mean(x[np.abs(x).max(1) > 1e-4] ** 2)) if np.any(np.abs(x) > 1e-4) else 1
vox *= .07 / rms(vox)
bg = (music + amb) * duck[:, None] + fol * (1 - .25 * vg[:, None])
mus_rms = rms(bg)
bg *= (.07 / 3.16) / mus_rms          # voice about 10 dB above the bed
mix = vox + bg
# fades
mix[:int(.5 * SR)] *= np.linspace(0, 1, int(.5 * SR))[:, None]
mix = mix[:int(DUR * SR)]
mix[-int(1.0 * SR):] *= np.linspace(1, 0, int(1.0 * SR))[:, None]
mix = np.stack([S.limit(mix[:, c], .95) for c in (0, 1)], 1)
os.makedirs(f'{HERE}/out', exist_ok=True)
sf.write(f'{HERE}/out/mix.wav', mix.astype(np.float32), SR)
print('mix', mix.shape, 'peak', float(np.abs(mix).max()))
