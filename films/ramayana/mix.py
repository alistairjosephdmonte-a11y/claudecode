"""Score (sampled VSCO 2 CE instruments + synthesized drone), paper foley from events.json, narration → mix.wav"""
import json, os, re, sys
import numpy as np, soundfile as sf
HERE = os.path.dirname(os.path.abspath(__file__)); LIB = os.path.abspath(f'{HERE}/../..'); sys.path.insert(0, LIB)
from core.audio import sfx as X
from core.audio import sampler as SM
SR = X.SR
ev = json.load(open(f'{HERE}/events.json')); DUR = ev['dur']; EV = ev['ev']
N = int((DUR + 2) * SR); rng = np.random.default_rng(7)
mus = np.zeros((N, 2)); fx = np.zeros((N, 2)); amb = np.zeros((N, 2)); vox = np.zeros((N, 2))
tt = np.arange(N) / SR
USED = set()

def put(buf, x, t, g=1.0, pan=0.0): X.add(buf, np.asarray(x, np.float64), t, g, pan)
def play(inst, p, t, d=.6, v=.7, g=1.0, pan=0.0, **kw):
    USED.add(inst); put(mus, SM.note(inst, p, d, v, **kw), t, g, pan)
SC = ['D', 'E', 'F#', 'A', 'B']          # Bhupali, on D
def deg(i, octv=4):                       # scale degree → pitch
    o, k = divmod(i, 5); return f'{SC[k]}{octv + o}'

# ---------- drone: a soft tanpura-like D / A with a gentle buzz ----------
def drone(t0, t1, g=.05, base=50):
    n = int((t1 - t0) * SR); t = np.arange(n) / SR; x = np.zeros(n)
    for f, a in [(73.42, 1), (110.0, .7), (146.83, .5), (220.0, .25)]:
        ph = 2 * np.pi * f * t + .3 * np.sin(2 * np.pi * .21 * t); w = np.sin(ph) + .3 * np.sin(2 * ph) + .18 * np.sin(3 * ph) + .1 * np.sin(5 * ph)
        x += a * w * (.75 + .25 * np.sin(2 * np.pi * (.4 + f / 997) * t))
    x = X.lp(x, 1800); e = np.minimum(1, np.minimum(t / 1.5, (t1 - t0 - t) / 1.5))
    put(mus, x * e, t0, g)

# ---------- the score, section by section ----------
# room: a warm harp
for i, p in enumerate(['D3', 'A3', 'D4', 'F#4', 'A4', 'F#4', 'D4', 'A3']): play('harp', p, .3 + i * .45, 1.4, .45, .9, -.2 + i * .05)
# prologue: drone + sparse flute; silence after the arrow; then the verse on kalimba + flute
drone(6.0, 11.3, .045); drone(13.6, 24.6, .05)
for t, p in [(7.2, 'A4'), (8.4, 'B4'), (9.2, 'A4'), (10.2, 'F#4')]: play('flute', p, t, .9, .5, .8, .1)
verse = [0, 1, 2, 3, 2, 1, 2, 0, 3, 4, 5, 4, 3, 2, 3, 1, 0]          # an eight-plus-eight syllable lilt
for i, d in enumerate(verse): t = 15.4 + i * .48; play('kalimba', deg(d + 5), t, .6, .55, .9, -.1 + (i % 3) * .1); (i % 4 == 0) and play('flute', deg(d + 5), t, 1.6, .45, .55)
play('harp', 'D4', 23.6, 1.5, .5); play('harp', 'A4', 23.75, 1.5, .5)
# page-turn glissandi
for t0 in (24.4, 54.8, 69.0, 87.6):
    for i in range(8): play('glockenspiel', deg(i + 5), t0 + i * .07, .3, .4, .55, -.4 + i * .1)
# spread 1 (festival → dusk): pizz cellos ostinato + glockenspiel tune
BPM = 104; B = 60 / BPM
def ostinato(t0, t1, notes, inst='cellos_pizz', v=.7, g=.9, step=B):
    t, i = t0, 0
    while t < t1: play(inst, notes[i % len(notes)], t, .4, v, g, -.15); t += step; i += 1
ostinato(26.8, 39.4, ['D3', 'A2', 'B2', 'A2'])
tune1 = [0, 2, 3, 4, 3, 2, 3, -1, 0, 2, 1, 0]
for i, d in enumerate(tune1): play('glockenspiel', deg(d + 5), 27.0 + i * 2 * B, .5, .55, .6, .2)
for t in (31.2,): [play('glockenspiel', p, t + k * .05, .5, .8, .8) for k, p in enumerate(['D5', 'F#5', 'A5', 'D6'])]
ostinato(39.6, 54.2, ['B2', 'F#2', 'A2', 'E2'], v=.5, g=.75, step=2 * B)
for i, p in enumerate(['B4', 'A4', 'F#4', 'E4', 'D4', None, 'E4', 'F#4', 'A4', 'F#4', 'E4', 'D4']):
    p and play('flute', p, 40.2 + i * 1.1, 1.2, .5, .7, .1)
play('harp', 'D3', 50.0, 2, .5); play('harp', 'A3', 50.15, 2, .5); play('harp', 'F#4', 50.3, 2, .5)
# spread 2 (forest → abduction)
ostinato(57.2, 63.4, ['D4', 'A3', 'E4', 'A3'], inst='kalimba', v=.55, g=.8, step=B / 2)
ostinato(57.2, 63.4, ['D2', 'A2'], v=.5, g=.6, step=2 * B)
put(mus, SM.note('violins_trem', 'A4', 3.0, .45, attack=.4), 63.6, .35, .1); put(mus, SM.note('violins_trem', 'B4', 3.0, .45, attack=.4), 63.6, .3, -.1); USED.add('violins_trem')
for k, t in enumerate(np.arange(63.6, 66.6, B)): put(mus, SM.hit('frame_drum', None, .55 + .1 * (k % 2)), t, .5); USED.add('frame_drum')
# spread 3 (allies, the leap, the ring)
ostinato(71.4, 87.0, ['D3', 'A2', 'B2', 'D3', 'E3', 'A2'], v=.65, step=B)
for i, d in enumerate([0, 1, 2, 4, 3, 2, 1, 0, 2, 3, 4, 5]): play('marimba', deg(d + 5), 72.0 + i * B * 1.5, .4, .55, .55, .2)
for i in range(10): play('glockenspiel', deg(i + 5), 80.4 + i * .17, .4, .6, .7, -.3 + i * .06)     # the leap
for k, p in enumerate(['D5', 'A5', 'F#5', 'D6']): play('harp', p, 85.0 + k * .08, 1.6, .6, .8)            # the ring
# spread 4 (war): drums and low pizz; a silence after Ravana falls; a bright crowning chord
for k, t in enumerate(np.arange(90.0, 95.4, B)): put(mus, SM.hit('frame_drum', None, .7 if k % 2 == 0 else .5), t, .6, -.1)
for t in np.arange(90.0, 95.4, 2 * B): put(mus, SM.note('timpani', 'D2', .8, .65), t, .7); USED.add('timpani')
ostinato(90.0, 95.4, ['D2', 'D2', 'A2', 'B2'], v=.75, g=.7, step=B)
for k, p in enumerate(['D4', 'F#4', 'A4', 'D5']): play('harp', p, 97.6 + k * .06, 2.0, .6, .8); play('glockenspiel', 'D6', 97.6, 1, .7, .6)
# hermitage: drone, harp, the twins' tune on flute
drone(99.4, 113.0, .045)
for i, p in enumerate(['D3', 'A3', 'D4', 'A3'] * 6): play('harp', p, 99.8 + i * B, 1.0, .4, .55, -.2)
song = [0, 1, 2, 2, 3, 2, 1, 0, 1, 2, 3, 4, 3, 2, 3, 2, 1, 0]
for i, d in enumerate(song): play('flute', deg(d + 5), 104.4 + i * .34, .5, .5, .65, .15); (i % 3 == 0) and play('kalimba', deg(d + 5), 104.4 + i * .34, .5, .45, .4)
# close: falling glockenspiel; the last chord; a soft tail under the end title
for i in range(8): play('glockenspiel', deg(12 - i), 110.8 + i * .22, .5, .45, .55)
for k, p in enumerate(['D3', 'A3', 'D4', 'F#4', 'A4']): play('harp', p, 113.8 + k * .09, 3.0, .5, .75)
play('nepal_bells', 'A5', 113.8, 2.5, .4, .3) if 'nepal_bells' in SM.instruments() else None
for i, p in enumerate(['A4', 'F#4', 'E4', 'D4', 'E4', 'D4']): play('flute', p, 115.6 + i * 1.0, 1.1, .4, .5)
drone(114.5, DUR, .035)

# ---------- paper foley from the picture's events ----------
def env(d, a=.003, tau=.1): t = X.t_(d); return np.minimum(1, t / a) * np.exp(-t / tau)
def crinkle(d=.15, v=1): return X.bp(X.noise(d), 2500, 9000) * env(d, .002, .03) * v
def pop(): d = .18; t = X.t_(d); f = 420 + 900 * np.exp(-t / .03); return X.norm(np.sin(2 * np.pi * np.cumsum(f) / SR) * env(d, .002, .04) + crinkle(d, .6))
def page(d): t = X.t_(d); return X.norm(X.bp(X.noise(d), 600, 6000) * np.sin(np.pi * np.clip(t / d, 0, 1)) ** 2 * (1 + .4 * np.sin(2 * np.pi * 3 * t)))
def thump(v=1): d = .5; return X.norm(X.lp(X.noise(d), 180) * env(d, .002, .06) + .6 * np.sin(2 * np.pi * 70 * X.t_(d)) * env(d, .002, .08)) * v
def creak(): d = .9; t = X.t_(d); f = 140 + 60 * np.sin(2 * np.pi * .9 * t); s = sum(np.sin(2 * np.pi * k * np.cumsum(f) / SR) / k for k in range(1, 10)); return X.norm(X.bp(s * np.abs(np.sin(2 * np.pi * 28 * t)) ** 5, 200, 2500) * np.sin(np.pi * np.clip(t / d, 0, 1)))
def clack(): return X.norm(X.clack(1.1)) * .8
def step(): d = .08; return X.norm(X.lp(X.noise(d), 1500) * env(d, .001, .012) + crinkle(d, .3))
def whoosh(d=.5): t = X.t_(d); return X.norm(X.bp(X.noise(d), 300, 3000) * np.sin(np.pi * t / d) ** 2)
def arrow(): d = .5; t = X.t_(d); return X.norm(X.bp(X.noise(d), 1500, 7000) * np.sin(np.pi * t / d) ** 3 * (1 + .5 * np.sin(2 * np.pi * 40 * t)))
def snap(): d = .5; x = X.norm(X.hp(X.noise(d), 1200) * env(d, .001, .02)) + .5 * X.norm(X.lp(X.noise(d), 400) * env(d, .002, .1)); return X.norm(x)
def ding(): d = 2.0; t = X.t_(d); return X.norm(sum(a * np.sin(2 * np.pi * f * t) * np.exp(-t / tau) for f, a, tau in [(1175, 1, .8), (2350, .4, .5), (3520, .2, .3)]))
def tink(): d = .8; t = X.t_(d); return X.norm(np.sin(2 * np.pi * 2900 * t) * np.exp(-t / .12) + .4 * np.sin(2 * np.pi * 4400 * t) * np.exp(-t / .06))
def boing(): d = .45; t = X.t_(d); f = 220 + 260 * t / d; return X.norm(np.sin(2 * np.pi * np.cumsum(f) / SR) * env(d, .004, .2) * (1 + .3 * np.sin(2 * np.pi * 14 * t)))
def hoof(): d = .1; return X.norm(X.bp(X.noise(d), 500, 2500) * env(d, .001, .015))
def stone(): d = .25; return X.norm(X.lp(X.noise(d), 900) * env(d, .001, .03) + .5 * np.sin(2 * np.pi * 180 * X.t_(d)) * env(d, .001, .05) + crinkle(d, .4))
def cry():   # the mate's cry: a two-note falling call, high and thin (a sine with vibrato, not a real bird sample)
    out = np.zeros(int(1.3 * SR))
    for k, (f0, at) in enumerate([(1250, 0), (1150, .55)]):
        d = .45; t = X.t_(d); f = f0 * (1 - .25 * t / d) * (1 + .02 * np.sin(2 * np.pi * 7 * t)); x = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.sin(np.pi * t / d) ** 1.5
        s = int(at * SR); out[s:s + len(x)] += x
    return X.norm(out)
def sparkle(d):
    out = np.zeros(int((d + .6) * SR))
    for i in range(int(d * 9)):
        s = int(rng.random() * d * SR); f = 2200 + rng.random() * 3200; t = X.t_(.5); x = np.sin(2 * np.pi * f * t) * np.exp(-t / .12); out[s:s + len(x)] += x[:len(out) - s] * (.4 + .6 * rng.random())
    return X.norm(out)
G = {'pop': .22, 'page': .35, 'thump': .5, 'creak': .3, 'clack': .25, 'step': .12, 'whoosh': .3, 'arrow': .3, 'snap': .55, 'ding': .25, 'tink': .2, 'boing': .25, 'land': .3, 'hoof': .07, 'stone': .3, 'cry': .12, 'sparkle': .12, 'slide': .25, 'bang': .3, 'thud': .45}
for e in EV:
    t, k = e['t'], e['type']; g = G.get(k, .2) * e.get('v', 1); pan = float(rng.uniform(-.25, .25))
    x = {'pop': pop, 'step': step, 'clack': clack, 'snap': snap, 'ding': ding, 'tink': tink, 'boing': boing, 'hoof': hoof, 'stone': stone, 'cry': cry, 'arrow': arrow, 'creak': creak}.get(k)
    if x: put(fx, x(), t, g, pan)
    elif k == 'page': put(fx, page(e['d']), t, g)
    elif k == 'sparkle': put(fx, sparkle(e['d']), t, g)
    elif k in ('thump', 'thud', 'land'): put(fx, thump(), t, g)
    elif k == 'whoosh': put(fx, whoosh(.7), t, g)
    elif k == 'slide': put(fx, X.norm(X.bp(X.noise(e['d']), 800, 4000) * np.sin(np.pi * X.t_(e['d']) / e['d'])), t, g)
    elif k == 'bang': put(fx, X.norm(X.hp(X.noise(.2), 800) * env(.2, .001, .03)), t, g)
# ---------- ambience: room tone + clock on the desk; one bed per spread ----------
def bed(t0, t1, x, g):
    n = int((t1 - t0) * SR); x = np.resize(x, n); e = np.minimum(1, np.minimum(np.arange(n) / SR / 1.0, (n - np.arange(n)) / SR / 1.0)); put(amb, x * e, t0, g)
room = X.norm(X.lp(X.brown(12), 300)); bed(0, 7.5, room, .05); bed(111.0, DUR, room, .05)
for t in np.arange(.5, 7, 1.0): put(amb, X.click(.6, .5), t, .05, .5)
for t in np.arange(111.5, DUR, 1.0): put(amb, X.click(.6, .5), t, .04, .5)
river = X.norm(X.bp(X.noise(10), 300, 2500) * (.7 + .3 * np.sin(np.linspace(0, 30, int(10 * SR))))); bed(6.5, 24.4, river, .04)
def birds(n, f0):
    out = np.zeros(int(10 * SR))
    for _ in range(n):
        s = int(rng.random() * 9 * SR); d = .12; t = X.t_(d); f = f0 * (1 + .3 * rng.random()) * (1 + .4 * np.sin(2 * np.pi * 9 * t)); x = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.sin(np.pi * t / d); out[s:s + len(x)] += x
    return X.norm(out)
bed(26.6, 54.4, birds(14, 2800), .025)
crick = X.norm(X.bp(X.noise(10), 4000, 6500) * (np.abs(np.sin(2 * np.pi * 15 * np.linspace(0, 10, int(10 * SR)))) ** 6)); bed(57.0, 68.6, crick, .03)
bed(71.2, 87.2, X.norm(X.bp(X.noise(10), 150, 900) * (.6 + .4 * np.sin(np.linspace(0, 12, int(10 * SR))))), .05)
bed(99.6, 110.6, birds(10, 3200), .02)

# ---------- narration ----------
story = open(f'{HERE}/story.js').read()
VO = [(m.group(1), float(m.group(2))) for m in re.finditer(r"\['(\w+)', ([\d.]+), ", story)]
vg = np.zeros(N)
for vid, t0 in VO:
    x, sr = sf.read(f'{HERE}/voices/{vid}.wav')
    if x.ndim > 1: x = x.mean(1)
    if sr != SR:
        import soxr; x = soxr.resample(x, sr, SR)
    x = X.compress(X.norm(X.hp(x, 90), .9), thr=.22, ratio=3.0)
    put(vox, x, t0, 1.0)
    vg[int((t0 - .2) * SR):int((t0 + len(x) / SR + .3) * SR)] = 1
k = int(.3 * SR); vg = np.convolve(vg, np.ones(k) / k, 'same')
def rms(x): m = np.abs(x).max(1) > 1e-4; return np.sqrt(np.mean(x[m] ** 2)) if m.any() else 1
vox *= .08 / rms(vox)
mus *= (.08 / 2.66) / rms(mus)          # music ~8.5 dB under the voice
mus *= (1 - .4 * vg)[:, None]
fx = np.stack([X.limit(fx[:, c], .5) for c in (0, 1)], 1) * .5
mix = (vox + mus + fx + amb * 2)[:int(DUR * SR)]
mix[-int(1.4 * SR):] *= np.linspace(1, 0, int(1.4 * SR))[:, None]
mix = np.stack([X.limit(mix[:, c], .95) for c in (0, 1)], 1)
sf.write(f'{HERE}/out/mix.wav', mix.astype(np.float32), SR)
open(f'{HERE}/out/instruments_used.txt', 'w').write('\n'.join(sorted(USED)) + '\n' + '\n'.join(SM.credits(sorted(USED))) + '\n')
print('mix', mix.shape, 'peak', float(np.abs(mix).max()), 'instruments', sorted(USED))
