"""Soundtrack for "West Side Story, explained": an original cool-jazz groove (finger snaps on 2 and 4, walking pizzicato
bass, brushes, vibraphone, a muted-trumpet riff), cut-paper hits synced to the edit, and the narration → out/mix.wav.
No melody from the show is quoted. Usage: .venv/bin/python films/wss-motion/mix.py
"""
import sys, os, json, numpy as np, soundfile as sf, soxr
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '../..'))
sys.path.insert(0, ROOT); sys.path.insert(0, os.path.join(ROOT, 'core/audio'))
from core.audio import sampler as S
from sfx import SR, add, bp, lp, hp, compress, limit, whoosh, thump, ding, click, pop
from scipy.ndimage import uniform_filter1d

S.seed(9)
E = json.load(open(os.path.join(HERE, 'events.json'))); DUR = E['dur']; EV = E['ev']; N = int(DUR * SR)
rng = np.random.default_rng(4)
T = lambda d: np.arange(int(round(d * SR))) / SR
nz = lambda d: rng.standard_normal(int(round(d * SR)))
mus = np.zeros((N, 2)); fx = np.zeros((N, 2)); vo = np.zeros((N, 2))
first = lambda ty: [e['t'] for e in EV if e['type'] == ty]
WIPES = first('wipe'); SCENE = [0.0] + WIPES
END = first('end')[0]
BPM = 112; B = 60 / BPM; BAR = 4 * B
def scene_of(t): return max(i for i, s in enumerate(SCENE) if s <= t + 1e-6)

def snap(v=1.0):
    t = T(0.12); x = bp(nz(0.12), 1800, 7000, 2) * np.exp(-t / 0.012) * 1.2 + np.sin(2 * np.pi * 2400 * t) * np.exp(-t / 0.004) * 0.3
    return x * 0.5 * v
def brush(d, v=1.0):
    t = T(d); x = bp(nz(d), 2500, 9000) * np.sin(np.pi * t / d) ** 2
    return x * 0.06 * v
def ride(v=1.0):
    t = T(0.6); x = sum(np.sin(2 * np.pi * f * t + rng.random() * 6) * a for f, a in [(3100, 1), (4730, .6), (6020, .4), (7400, .3)]) * np.exp(-t / 0.18)
    return (x + bp(nz(0.6), 6000, 12000) * np.exp(-t / 0.05) * 1.5) * 0.03 * v
def note(inst, p, d, v, att=0., rel=None): return S.note(inst, p, d, v, attack=att, release=rel)

# —— the groove: Dm7 | G7 | Cmaj7 | A7, swung eighths ——
CH = [('D2', ['F3', 'A3', 'C4', 'E4'], ['D2', 'F2', 'A2', 'C3']), ('G2', ['F3', 'B3', 'D4', 'E4'], ['G2', 'B2', 'D3', 'F3']),
      ('C2', ['E3', 'G3', 'B3', 'D4'], ['C2', 'E2', 'G2', 'B2']), ('A1', ['G3', 'C#4', 'E4', 'F4'], ['A1', 'C#2', 'E2', 'G2'])]
RIFF = [(0, 'A4', .5), (.66, 'C5', .3), (1, 'D5', .9), (2.5, 'F5', .3), (2.66, 'E5', .3), (3, 'D5', 1.2)]   # original 1-bar riff
t0 = 0.55; nb = int((END + 2.0 - t0) / BAR)
stalled = first('stamp')[0]; lost = first('win')[0]
for b in range(nb):
    tb = t0 + b * BAR; root, vib, walk = CH[b % 4]; sc = scene_of(tb)
    drop = stalled - 0.1 < tb + BAR and tb < stalled + 1.6   # stop-time under "It stalled."
    for k in range(4):
        tk = tb + k * B; sw = B * 0.62
        if k % 2: add(mus, snap(0.9 if not drop else 1.1), tk + rng.normal(0, .004), 1.0, -0.35); add(mus, snap(0.7), tk + .012, 1.0, 0.4)
        if drop: continue
        if sc >= 0: add(mus, note('contrabass_pizz', walk[k] if k else root, B * 0.95, .75 if k == 0 else .6), tk, 1.15, -0.05)
        if sc >= 1:
            add(mus, brush(B * 0.9), tk, 1.0, 0.2)
            add(mus, ride(0.9 if k % 2 == 0 else 0.6), tk, 1.0, 0.3); add(mus, ride(0.5), tk + sw, 1.0, 0.3)
    if drop: continue
    if sc >= 2 and b % 2 == 0:
        for j, p in enumerate(vib): add(mus, note('vibraphone', p, BAR * 1.8, .32), tb + j * 0.012, 0.7, 0.25 - j * 0.15)
    if sc in (0, 5, 9) and b % 2 == 0:   # the riff: title, marquee, outro
        for bt, p, d in RIFF: add(mus, note('trumpet_mute', p, d * B, .55, rel=.12), tb + bt * B, 0.75, -0.2)
# final hit: everything on D, then a last snap
for p in ['D2', 'A2', 'F3', 'C4', 'E4']: add(mus, note('vibraphone', p, 3.0, .5), END + 0.05, 0.8, 0)
add(mus, note('contrabass_pizz', 'D2', 2.0, .9), END + 0.05, 1.3, 0); add(mus, note('trumpet_mute', 'D5', 1.6, .6, rel=.5), END + 0.05, 0.8, -0.2)
add(mus, snap(1.2), END + 1.4, 1.0, 0)
mus[int((END + 3.2) * SR):] *= 0

# —— hits ——
for e in EV:
    t, ty = e['t'], e['type']
    if ty == 'wipe': add(fx, whoosh(0.32, 0.8), t - 0.24, 0.9, rng.uniform(-.4, .4))
    elif ty == 'slam': add(fx, thump(0.9, 75), t, 1.0, 0); add(fx, click(0.8, 0.8), t, 0.8, 0)
    elif ty in ('stamp', 'stamp2'): add(fx, thump(1.0, 60), t, 1.2, 0.2); add(fx, bp(nz(0.08), 300, 3000) * np.exp(-T(0.08) / .015), t, 0.6, 0.2)
    elif ty == 'flip': [add(fx, click(1.2, 0.6), t + k * 0.06, 1.0, 0.4) for k in range(4)]
    elif ty == 'split': add(fx, whoosh(0.5, 0.9), t - 0.1, 1.0, 0)
    elif ty == 'heartpop': add(fx, pop(0.9), t, 1.0, 0); add(fx, note('vibraphone', 'A5', 1.5, .5), t + .02, 0.8, 0)
    elif ty == 'card': add(fx, click(0.9, 0.7), t, 1.0, -0.3); add(fx, whoosh(0.2, 0.5), t - 0.05, 0.7, 0)
    elif ty == 'count':
        k = 0; tc = t
        while tc < t + e['dur']: add(fx, click(1.4 + 0.2 * (k % 2), 0.35), tc, 0.8, 0.2); tc += 0.05 + 0.08 * (tc - t) / e['dur']; k += 1
        add(fx, ding(0.6), t + e['dur'], 0.8, 0)
    elif ty == 'win': add(fx, ding(0.7), t + 0.3, 0.9, 0.3)
    elif ty == 'trophies': [add(fx, note('glockenspiel', p, 0.8, .4), t + 0.12 * k, 0.6, -0.4 + 0.08 * k) for k, p in enumerate(['D6', 'F6', 'A6', 'C7', 'D7', 'F6', 'A6', 'C7', 'E7', 'D7'])]
    elif ty == 'swipe': add(fx, whoosh(0.45, 0.8), t - 0.1, 1.0, -0.3)
    elif ty == 'end': add(fx, thump(0.8, 55), t + 0.05, 1.0, 0)

# —— narration ——
VO_RMS = 10 ** (-19.0 / 20); vmask = np.zeros(N)
for e in [x for x in EV if x['type'] == 'voice']:
    a, sr = sf.read(os.path.join(HERE, 'out', 'voice', e['id'] + '.wav'))
    if a.ndim > 1: a = a.mean(1)
    if sr != SR: a = soxr.resample(a, sr, SR)
    a = compress(hp(a, 80) / (np.abs(a).max() + 1e-9) * .8, thr=.22, ratio=2.5, att=.006, rel=.12)
    act = np.abs(a) > np.abs(a).max() * .05; a *= VO_RMS / (np.sqrt(np.mean(a[act] ** 2)) + 1e-9)
    add(vo, a, e['t'], 1.0, 0); s0 = int(e['t'] * SR); vmask[s0:s0 + len(a)] = 1
duck = np.clip(uniform_filter1d(vmask, int(.3 * SR)) * 1.6, 0, 1)
mus *= (1 - duck * (1 - 10 ** (-9 / 20)))[:, None]
mus /= (np.sqrt(np.mean(mus ** 2)) + 1e-9) / 10 ** (-29 / 20)
fx *= (1 - duck * (1 - 10 ** (-4 / 20)))[:, None]
mix = mus + fx * 0.6 + vo
for c in range(2): mix[:, c] = limit(mix[:, c], .95)
os.makedirs(os.path.join(HERE, 'out'), exist_ok=True)
sf.write(os.path.join(HERE, 'out', 'mix.wav'), mix.astype(np.float32), SR)
db = lambda x: 20 * np.log10(np.sqrt(np.mean(x ** 2)) + 1e-9)
print(f'dur {DUR}  music {db(mus):.1f}  fx {db(fx):.1f}  voice {db(vo):.1f}  mix {db(mix):.1f} dB')
