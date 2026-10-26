"""Score (sampled VSCO 2 CE / VCSL instruments + a synthesized tanpura drone), paper foley and narration → out/mix.wav.
Everything is placed from events.json, which the page writes: one 'scene' event per spread (with its mood), 'vo' events, and the sounds."""
import json, os, sys
import numpy as np, soundfile as sf
HERE = os.path.dirname(os.path.abspath(__file__)); LIB = os.path.abspath(f'{HERE}/../..'); sys.path.insert(0, LIB)
from core.audio import sfx as X
from core.audio import sampler as SM
SR = X.SR
ev = json.load(open(f'{HERE}/events.json')); DUR = ev['dur']; EV = ev['ev']
N = int((DUR + 2) * SR); rng = np.random.default_rng(7)
mus = np.zeros((N, 2)); fx = np.zeros((N, 2)); amb = np.zeros((N, 2)); vox = np.zeros((N, 2))
USED = set(); HAVE = set(SM.instruments())

def put(buf, x, t, g=1.0, pan=0.0):
    if t < 0 or t >= DUR + 1: return
    X.add(buf, np.asarray(x, np.float64), t, g, pan)
def play(inst, p, t, d=.6, v=.7, g=1.0, pan=0.0, **kw):
    if inst not in HAVE: return
    USED.add(inst); put(mus, SM.note(inst, p, d, v, **kw), t, g, pan)
def hit(inst, t, v=.6, g=.6, pan=0.0):
    if inst not in HAVE: return
    USED.add(inst); put(mus, SM.hit(inst, None, v), t, g, pan)

# scales on D: Bhupali (bright), a Bhimpalasi-like minor (D F G A C), a tense one with a flat second (D Eb F# G A Bb)
SCALES = {'bright': ['D', 'E', 'F#', 'A', 'B'], 'minor': ['D', 'F', 'G', 'A', 'C'], 'tense': ['D', 'D#', 'F#', 'G', 'A', 'A#']}
def deg(i, sc='bright', octv=4):
    S = SCALES[sc]; o, k = divmod(i, len(S)); return f'{S[k]}{octv + o}'

def drone(t0, t1, g=.05, low=False):
    n = int((t1 - t0) * SR)
    if n <= SR: return
    t = np.arange(n) / SR; x = np.zeros(n)
    for f, a in ([(73.42, 1), (110.0, .7), (146.83, .5), (220.0, .25)] if not low else [(36.71, .8), (73.42, 1), (110.0, .5)]):
        ph = 2 * np.pi * f * t + .3 * np.sin(2 * np.pi * .21 * t); w = np.sin(ph) + .3 * np.sin(2 * ph) + .18 * np.sin(3 * ph) + .1 * np.sin(5 * ph)
        x += a * w * (.75 + .25 * np.sin(2 * np.pi * (.4 + f / 997) * t))
    x = X.lp(x, 1800); e = np.minimum(1, np.minimum(t / 2.0, (t1 - t0 - t) / 2.0))
    put(mus, x * e, t0, g)

def melody(R, n, sc, lo=5, hi=11):
    d, out = R.integers(lo, hi), []
    for _ in range(n): d = int(np.clip(d + R.choice([-2, -1, -1, 0, 1, 1, 2]), lo, hi)); out.append(d)
    return out

def score_scene(i, t0, t1, mood):
    R = np.random.default_rng(100 + i); L = t1 - t0
    if L < 2: return
    if mood == 'calm':
        drone(t0, t1, .042); B = 60 / 72
        for k, t in enumerate(np.arange(t0 + .5, t1 - 1, 8 * B)):
            for j, p in enumerate(['D3', 'A3', 'D4', 'F#4']): play('harp', p, t + j * B * .5, 1.6, .38, .6, -.2 + j * .1)
        for t in np.arange(t0 + 3, t1 - 3, 9.0):
            for j, dg in enumerate(melody(R, 5, 'bright')): play('flute', deg(dg), t + j * .7, .9, .42, .5, .15)
    elif mood == 'festive':
        B = 60 / 104
        for k, t in enumerate(np.arange(t0 + .3, t1 - .5, B)): play('cellos_pizz', ['D3', 'A2', 'B2', 'A2'][k % 4], t, .4, .6, .75, -.15)
        for t in np.arange(t0 + 1, t1 - 2, 8 * B):
            for j, dg in enumerate(melody(R, 8, 'bright', 5, 10)): play('glockenspiel', deg(dg), t + j * B, .5, .5, .5, .2)
        for t in np.arange(t0 + .3, t1 - .5, 2 * B): hit('frame_drum', t, .45, .35, -.1)
    elif mood == 'sad':
        drone(t0, t1, .045, low=True); B = 60 / 60
        for t in np.arange(t0 + .5, t1 - 1, 6 * B):
            for j, p in enumerate(['D3', 'A3', 'F4']): play('harp', p, t + j * .35, 2.2, .32, .5, -.2 + j * .1)
        for t in np.arange(t0 + 2, t1 - 3, 7.0):
            for j, dg in enumerate(sorted(melody(R, 5, 'minor', 4, 9), reverse=True)): play('flute', deg(dg, 'minor'), t + j * 1.0, 1.3, .4, .5, .1)
    elif mood == 'tense':
        B = 60 / 88
        for t in np.arange(t0 + .3, t1 - 2, 4.0):
            put(mus, SM.note('violins_trem', 'A4', 4.2, .4, attack=.6), t, .22, .1); put(mus, SM.note('violins_trem', 'D#5', 4.2, .35, attack=.6), t, .14, -.1); USED.add('violins_trem')
        for k, t in enumerate(np.arange(t0 + .3, t1 - .5, B)): play('cellos_pizz', ['D2', 'D2', 'D#2', 'D2'][k % 4], t, .4, .55, .65)
        for t in np.arange(t0 + 2, t1 - 1, 8 * B): play('timpani', 'D2', t, .8, .5, .45)
    elif mood == 'battle':
        B = 60 / 120
        for k, t in enumerate(np.arange(t0 + .2, t1 - .5, B / 2)): hit('frame_drum', t, .7 if k % 4 == 0 else .45, .5, -.1)
        for t in np.arange(t0 + .2, t1 - .5, 2 * B): play('timpani', 'D2', t, .8, .6, .6)
        for k, t in enumerate(np.arange(t0 + .2, t1 - .5, B)): play('cellos_pizz', ['D2', 'D2', 'A2', 'A#2'][k % 4], t, .4, .7, .65)
        for t in np.arange(t0 + 2, t1 - 2, 8 * B):
            for j, dg in enumerate(melody(R, 4, 'tense', 6, 12)): play('glockenspiel', deg(dg, 'tense'), t + j * B / 2, .4, .5, .35, .2)
    elif mood == 'mystic':
        drone(t0, t1, .045)
        for t in np.arange(t0 + .5, t1 - 1, 1.6): play('kalimba', deg(int(R.integers(5, 12))), t + R.random() * .4, .8, .4, .45, R.uniform(-.4, .4))
        for t in np.arange(t0 + 1, t1 - 2, 6.0): play('nepal_bells', 'A5', t, 2.5, .35, .25)
    elif mood == 'joyful':
        B = 60 / 112
        for k, t in enumerate(np.arange(t0 + .3, t1 - .5, B)): play('cellos_pizz', ['D3', 'A2', 'B2', 'D3', 'E3', 'A2'][k % 6], t, .4, .6, .7, -.15)
        for t in np.arange(t0 + 1, t1 - 2, 8 * B):
            for j, dg in enumerate(melody(R, 12, 'bright', 5, 11)): play('marimba', deg(dg), t + j * B * .66, .4, .5, .5, .2)
    elif mood == 'tender':
        drone(t0, t1, .035); B = 60 / 66
        for t in np.arange(t0 + .5, t1 - 1, 4 * B):
            for j, p in enumerate(['D3', 'A3', 'D4', 'E4', 'F#4', 'A4']): play('harp', p, t + j * B * .5, 1.8, .34, .5, -.25 + j * .1)
        for t in np.arange(t0 + 2.5, t1 - 3, 8.0):
            for j, dg in enumerate(melody(R, 6, 'bright', 5, 10)): play('flute', deg(dg), t + j * .8, 1.0, .4, .5, .15)
    elif mood == 'regal':
        for t in np.arange(t0 + .5, t1 - 1, 3.0):
            for j, p in enumerate(['D3', 'A3', 'D4', 'F#4', 'A4']): play('harp', p, t + j * .07, 2.4, .5, .6)
            play('timpani', 'D2', t, 1, .6, .5)
        for t in np.arange(t0 + 1, t1 - 2, 4.0):
            for j, p in enumerate(['D5', 'F#5', 'A5', 'D6']): play('glockenspiel', p, t + j * .12, .6, .55, .4)
        drone(t0, t1, .03)

# ---------- the score, scene by scene ----------
SC = [e for e in EV if e['type'] == 'scene']
for i, s in enumerate(SC): score_scene(i, s['R'] - .2, s['t1'] + .4, s.get('mood', 'calm'))
for i, p in enumerate(['D3', 'A3', 'D4', 'F#4', 'A4', 'F#4', 'D4', 'A3']): play('harp', p, .3 + i * .45, 1.4, .45, .9, -.2 + i * .05)
for e in EV:
    if e['type'] == 'page':
        for i in range(8): play('glockenspiel', deg(i + 5), e['t'] - .2 + i * .07, .3, .4, .5, -.4 + i * .1)
CLOSE = max(e['t'] for e in EV if e['type'] == 'creak')
for i in range(8): play('glockenspiel', deg(12 - i), CLOSE + i * .22, .5, .45, .55)
for k, p in enumerate(['D3', 'A3', 'D4', 'F#4', 'A4']): play('harp', p, CLOSE + 2.6 + k * .09, 3.0, .5, .75)
play('nepal_bells', 'A5', CLOSE + 2.6, 2.5, .4, .3)
for i, p in enumerate(['A4', 'F#4', 'E4', 'D4', 'E4', 'D4']): play('flute', p, CLOSE + 4.4 + i * 1.0, 1.1, .4, .5)
drone(CLOSE + 3.0, DUR, .035)

# ---------- foley ----------
def env(d, a=.003, tau=.1): t = X.t_(d); return np.minimum(1, t / a) * np.exp(-t / tau)
def crinkle(d=.15, v=1): return X.bp(X.noise(d), 2500, 9000) * env(d, .002, .03) * v
def pop(): d = .18; t = X.t_(d); f = 420 + 900 * np.exp(-t / .03); return X.norm(np.sin(2 * np.pi * np.cumsum(f) / SR) * env(d, .002, .04) + crinkle(d, .6))
def page(d): t = X.t_(d); return X.norm(X.bp(X.noise(d), 600, 6000) * np.sin(np.pi * np.clip(t / d, 0, 1)) ** 2 * (1 + .4 * np.sin(2 * np.pi * 3 * t)))
def thump(v=1): d = .5; return X.norm(X.lp(X.noise(d), 180) * env(d, .002, .06) + .6 * np.sin(2 * np.pi * 70 * X.t_(d)) * env(d, .002, .08)) * v
def creak(): d = .9; t = X.t_(d); f = 140 + 60 * np.sin(2 * np.pi * .9 * t); s = sum(np.sin(2 * np.pi * k * np.cumsum(f) / SR) / k for k in range(1, 10)); return X.norm(X.bp(s * np.abs(np.sin(2 * np.pi * 28 * t)) ** 5, 200, 2500) * np.sin(np.pi * np.clip(t / d, 0, 1)))
def step(): d = .08; return X.norm(X.lp(X.noise(d), 1500) * env(d, .001, .012) + crinkle(d, .3))
def whoosh(d=.7): t = X.t_(d); return X.norm(X.bp(X.noise(d), 300, 3000) * np.sin(np.pi * t / d) ** 2)
def arrow(): d = .5; t = X.t_(d); return X.norm(X.bp(X.noise(d), 1500, 7000) * np.sin(np.pi * t / d) ** 3 * (1 + .5 * np.sin(2 * np.pi * 40 * t)))
def snap(): d = .5; x = X.norm(X.hp(X.noise(d), 1200) * env(d, .001, .02)) + .5 * X.norm(X.lp(X.noise(d), 400) * env(d, .002, .1)); return X.norm(x)
def ding(): d = 2.0; t = X.t_(d); return X.norm(sum(a * np.sin(2 * np.pi * f * t) * np.exp(-t / tau) for f, a, tau in [(1175, 1, .8), (2350, .4, .5), (3520, .2, .3)]))
def tink(): d = .8; t = X.t_(d); return X.norm(np.sin(2 * np.pi * 2900 * t) * np.exp(-t / .12) + .4 * np.sin(2 * np.pi * 4400 * t) * np.exp(-t / .06))
def boing(): d = .45; t = X.t_(d); f = 220 + 260 * t / d; return X.norm(np.sin(2 * np.pi * np.cumsum(f) / SR) * env(d, .004, .2) * (1 + .3 * np.sin(2 * np.pi * 14 * t)))
def clack(): return X.norm(X.clack(1.1)) * .8
def splash(): d = 1.0; t = X.t_(d); return X.norm(X.bp(X.noise(d), 400, 5000) * np.exp(-t / .25) * (1 + .5 * np.sin(2 * np.pi * 9 * t)))
def cry():
    out = np.zeros(int(1.3 * SR))
    for f0, at in [(1250, 0), (1150, .55)]:
        d = .45; t = X.t_(d); f = f0 * (1 - .25 * t / d) * (1 + .02 * np.sin(2 * np.pi * 7 * t)); x = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.sin(np.pi * t / d) ** 1.5
        s = int(at * SR); out[s:s + len(x)] += x
    return X.norm(out)
def sparkle(d):
    out = np.zeros(int((d + .6) * SR))
    for _ in range(int(d * 9) + 1):
        s = int(rng.random() * d * SR); f = 2200 + rng.random() * 3200; t = X.t_(.5); x = np.sin(2 * np.pi * f * t) * np.exp(-t / .12); out[s:s + len(x)] += x[:len(out) - s] * (.4 + .6 * rng.random())
    return X.norm(out)
def rain(d): t = X.t_(d); return X.norm(X.bp(X.noise(d), 2000, 8000) * np.minimum(1, np.minimum(t / .5, (d - t) / .8)))
def fire(d): t = X.t_(d); n = X.lp(X.noise(d), 900) * (.6 + .4 * np.sin(2 * np.pi * .7 * t)); c = np.zeros(len(t)); idx = rng.integers(0, len(t), int(d * 25)); c[idx] = rng.uniform(.3, 1, len(idx)); c = X.bp(c, 1500, 6000); return X.norm((n + 2 * c) * np.minimum(1, np.minimum(t / .6, (d - t) / 1.0)))
def drum(d):
    out = np.zeros(int((d + .6) * SR))
    for k, s in enumerate(np.arange(0, d, .25)): x = thump(1.0 if k % 2 == 0 else .6); i = int(s * SR); out[i:i + len(x)] += x[:len(out) - i]
    return X.norm(out)
def conch(): d = 2.4; t = X.t_(d); f = 220 * (1 + .03 * np.sin(2 * np.pi * 5 * t)); x = sum(np.sin(2 * np.pi * k * np.cumsum(f) / SR) / k ** 1.3 for k in range(1, 8)); return X.norm(X.lp(x, 2400) * np.minimum(1, np.minimum(t / .4, (d - t) / .6)))
def rumble(d): t = X.t_(d); return X.norm(X.lp(X.noise(d), 120) * np.sin(np.pi * t / d))
G = {'pop': .2, 'page': .35, 'thump': .5, 'creak': .3, 'clack': .25, 'step': .1, 'whoosh': .3, 'arrow': .3, 'snap': .55, 'ding': .22, 'tink': .2, 'boing': .25, 'thud': .42, 'cry': .12, 'sparkle': .12, 'bang': .3, 'splash': .3, 'rain': .12, 'fire': .16, 'drum': .45, 'conch': .2, 'rumble': .6}
SIMPLE = {'pop': pop, 'step': step, 'clack': clack, 'snap': snap, 'ding': ding, 'tink': tink, 'boing': boing, 'cry': cry, 'arrow': arrow, 'creak': creak, 'splash': splash, 'conch': conch, 'whoosh': whoosh}
for e in EV:
    t, k = e['t'], e['type']
    if k in ('scene', 'vo'): continue
    g = G.get(k, .2) * e.get('v', 1); pan = float(rng.uniform(-.25, .25))
    if k in SIMPLE: put(fx, SIMPLE[k](), t, g, pan)
    elif k == 'page': put(fx, page(e['d']), t, g)
    elif k == 'sparkle': put(fx, sparkle(e.get('d', 1)), t, g)
    elif k in ('thump', 'thud'): put(fx, thump(), t, g)
    elif k == 'bang': put(fx, X.norm(X.hp(X.noise(.2), 800) * env(.2, .001, .03)), t, g)
    elif k == 'rain': put(fx, rain(e.get('d', 3)), t, g)
    elif k == 'fire': put(fx, fire(e.get('d', 5)), t, g)
    elif k == 'drum': put(fx, drum(e.get('d', 2)), t, g)
    elif k == 'rumble': put(fx, rumble(e.get('d', 2)), t, g)

# ---------- ambience: room tone with a clock at the open and close; a bed per location ----------
def bed(t0, t1, x, g):
    n = int((t1 - t0) * SR)
    if n <= 0: return
    x = np.resize(x, n); e = np.minimum(1, np.minimum(np.arange(n) / SR / 1.0, (n - np.arange(n)) / SR / 1.0)); put(amb, x * e, t0, g)
room = X.norm(X.lp(X.brown(12), 300)); bed(0, 7.5, room, .05); bed(CLOSE - .5, DUR, room, .05)
for t in np.arange(.5, 7, 1.0): put(amb, X.click(.6, .5), t, .05, .5)
for t in np.arange(CLOSE, DUR, 1.0): put(amb, X.click(.6, .5), t, .04, .5)
def birds(n, f0):
    out = np.zeros(int(10 * SR))
    for _ in range(n):
        s = int(rng.random() * 9 * SR); d = .12; t = X.t_(d); f = f0 * (1 + .3 * rng.random()) * (1 + .4 * np.sin(2 * np.pi * 9 * t)); x = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.sin(np.pi * t / d); out[s:s + len(x)] += x
    return X.norm(out)
river = X.norm(X.bp(X.noise(10), 300, 2500) * (.7 + .3 * np.sin(np.linspace(0, 30, int(10 * SR)))))
sea = X.norm(X.bp(X.noise(10), 150, 900) * (.6 + .4 * np.sin(np.linspace(0, 12, int(10 * SR)))))
crick = X.norm(X.bp(X.noise(10), 4000, 6500) * (np.abs(np.sin(2 * np.pi * 15 * np.linspace(0, 10, int(10 * SR)))) ** 6))
BEDS = {'graphite': (river, .035), 'ayodhya': (birds(14, 2800), .022), 'ashram': (birds(10, 3200), .02), 'mithila': (birds(14, 2800), .02), 'river': (river, .05), 'forest': (birds(8, 2400), .02),
        'panch': (crick, .025), 'kish': (birds(6, 2000), .02), 'sea': (sea, .05), 'shore': (sea, .05), 'night': (crick, .03), 'war': (sea, .025), 'herm': (birds(10, 3200), .02), 'dusk': (crick, .022)}
for s in SC:
    b = BEDS.get(s['page'])
    if b: bed(s['R'], s['t1'], b[0], b[1])

# ---------- narration ----------
vg = np.zeros(N)
for e in EV:
    if e['type'] != 'vo': continue
    x, sr = sf.read(f"{HERE}/voices/{e['id']}.wav")
    if x.ndim > 1: x = x.mean(1)
    if sr != SR:
        import soxr; x = soxr.resample(x, sr, SR)
    x = X.compress(X.norm(X.hp(x, 90), .9), thr=.22, ratio=3.0)
    put(vox, x, e['t'], 1.0)
    vg[int((e['t'] - .2) * SR):int((e['t'] + len(x) / SR + .3) * SR)] = 1
k = int(.3 * SR); vg = np.convolve(vg, np.ones(k) / k, 'same')
def rms(x): m = np.abs(x).max(1) > 1e-4; return np.sqrt(np.mean(x[m] ** 2)) if m.any() else 1
vox *= .08 / rms(vox)
mus *= (.08 / 2.66) / rms(mus)
mus *= (1 - .45 * vg)[:, None]
fx = np.stack([X.limit(fx[:, c], .5) for c in (0, 1)], 1) * .5
mix = (vox + mus + fx + amb * 2)[:int(DUR * SR)]
mix[-int(1.4 * SR):] *= np.linspace(1, 0, int(1.4 * SR))[:, None]
mix = np.stack([X.limit(mix[:, c], .95) for c in (0, 1)], 1)
os.makedirs(f'{HERE}/out', exist_ok=True)
sf.write(f'{HERE}/out/mix.wav', mix.astype(np.float32), SR)
sf.write(f'{HERE}/out/voice_only.wav', np.clip(vox[:int(DUR * SR)] / max(1e-6, np.abs(vox).max()) * .89, -1, 1).astype(np.float32), SR)
open(f'{HERE}/out/instruments_used.txt', 'w').write('\n'.join(sorted(USED)) + '\n' + '\n'.join(SM.credits(sorted(USED))) + '\n')
print('mix', mix.shape, 'peak', float(np.abs(mix).max()), 'instruments', sorted(USED))
