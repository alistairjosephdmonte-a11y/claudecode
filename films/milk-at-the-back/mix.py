"""Original score (one sound per act), paper foley and the narration → out/mix.wav. All cue times come from events.json.
Act I   pizzicato + marimba (F major, 112 bpm)        Act II  ragtime-style piano + brushed snare (C, 100 bpm)
Act III pulsing minimal synth over a fridge-hum drone  Act IV  strings join the synth, then a lone music box for the reveal"""
import json, os, sys
import numpy as np, soundfile as sf
H = os.path.dirname(os.path.abspath(__file__)); LIB = os.path.abspath(f'{H}/../..'); sys.path.insert(0, LIB)
from core.audio import sfx as X
from core.audio import sampler as SM
SR = X.SR
E = json.load(open(f'{H}/events.json')); DUR = E['dur']; EV = E['ev']
CUE = {e['name']: e['t'] for e in EV if e['type'] == 'cue'}
N = int((DUR + 2) * SR); rng = np.random.default_rng(5)
mus = np.zeros((N, 2)); fx = np.zeros((N, 2)); amb = np.zeros((N, 2)); vox = np.zeros((N, 2)); USED = set()
def put(buf, x, t, g=1.0, pan=0.0):
    if 0 <= t < DUR + 1: X.add(buf, np.asarray(x, np.float64), t, g, pan)
def play(inst, p, t, d=.5, v=.7, g=1.0, pan=0.0, **kw): USED.add(inst); put(mus, SM.note(inst, p, d, v, **kw), t, g, pan)
def hit(inst, t, v=.6, g=.6, pan=0.0, p=None): USED.add(inst); put(mus, SM.hit(inst, p, v), t, g, pan)
NOTE = {'C': 0, 'C#': 1, 'Db': 1, 'D': 2, 'Eb': 3, 'E': 4, 'F': 5, 'F#': 6, 'G': 7, 'Ab': 8, 'A': 9, 'Bb': 10, 'B': 11}
NAMES = ['C', 'C#', 'D', 'Eb', 'E', 'F', 'F#', 'G', 'Ab', 'A', 'Bb', 'B']
def nm(m): return f'{NAMES[m % 12]}{m // 12 - 1}'
def M(s): n, o = (s[:2], s[2:]) if len(s) > 2 and s[1] in '#b' else (s[:1], s[1:]); return 12 * (int(o) + 1) + NOTE[n]
def tt(d): return np.arange(int(d * SR)) / SR
def fade(x, a=.4, b=1.0): n = len(x); e = np.minimum(1, np.minimum(np.arange(n) / (a * SR + 1), (n - np.arange(n)) / (b * SR + 1))); return x * e

# ---------- Act I: pizzicato bass + marimba figures ----------
def act1(t0, t1):
    B = 60 / 112; prog = [('F2', [0, 4, 7]), ('D2', [0, 3, 7]), ('Bb1', [0, 4, 7]), ('C2', [0, 4, 7])]
    k = 0; t = t0
    while t < t1 - 2 * B:
        root, ch = prog[(k // 8) % 4]; r = M(root)
        if k % 2 == 0: play('cellos_pizz', nm(r + (0 if k % 4 == 0 else 7)), t, .4, .7, .8, -.2)
        if k % 2 == 1: play('violins_pizz', nm(r + 24 + ch[(k // 2) % 3]), t, .3, .5, .45, .25)
        mel = [0, 2, 4, 7, 4, 2, 4, 9][k % 8]
        if (k // 16) % 2 == 1 and k % 2 == 0: play('marimba', nm(M('F4') + [0, 2, 4, 5, 7, 9, 11, 12][mel % 8] + (0 if mel < 8 else 0)), t, .4, .55, .55, .15)
        if (k // 16) % 2 == 0 and k % 4 == 3: play('marimba', nm(r + 36 + ch[k % 3]), t, .3, .45, .4, .3)
        t += B; k += 1
# ---------- Act II: ragtime-style piano (stride left hand, syncopated right) + brushed snare ----------
def act2(t0, t1):
    B = 60 / 100; prog = ['C', 'C', 'A', 'A', 'D', 'D', 'G', 'G']; Q = {'C': [0, 4, 7], 'A': [0, 4, 7, 10], 'D': [0, 4, 7, 10], 'G': [0, 4, 7, 10]}
    roots = {'C': 'C2', 'A': 'A1', 'D': 'D2', 'G': 'G1'}
    bar = 0; t = t0; R = np.random.default_rng(3)
    while t < t1 - 4 * B:
        c = prog[bar % 8]; r = M(roots[c]); ch = Q[c]
        for b in range(4):   # stride: bass on 1 & 3, chord on 2 & 4
            tb = t + b * B
            if b % 2 == 0: play('piano', nm(r + (0 if b == 0 else 7)), tb, .45, .6, .7, -.25)
            else: [play('piano', nm(r + 24 + iv), tb, .3, .42, .5, -.1) for iv in ch[:3]]
            hit('snare', tb + B * .5, .18, .18, .2); hit('shaker', tb, .25, .12, .3)
        # syncopated right hand: an invented figure on chord tones, accents off the beat
        rh = [0, 1.5, 2.5, 3.0, 3.5] if bar % 2 == 0 else [.5, 1.0, 2.0, 3.0]
        for j, s in enumerate(rh):
            p = r + 36 + ch[(j + bar) % len(ch)] + (12 if j == len(rh) - 1 and bar % 4 == 3 else 0)
            play('piano', nm(p), t + s * B, .28, .5 + .1 * (j % 2), .5, .15)
        t += 4 * B; bar += 1
# ---------- synth tools ----------
def synth_pulse(f, d, cut=1400, v=.5):
    x = tt(d); ph = np.cumsum(np.full(len(x), f)) / SR; s = (2 * (ph % 1) - 1) * .6 + np.sign(np.sin(2 * np.pi * ph)) * .4
    env = np.exp(-x / max(.05, d * .5)) * np.minimum(1, x / .004); return X.lp(s * env, cut) * v
def pad(fs, d, v=.2):
    x = tt(d); s = sum(np.sin(2 * np.pi * f * x + .3 * np.sin(2 * np.pi * .3 * x)) + .3 * np.sin(4 * np.pi * f * x) for f in fs)
    return fade(X.lp(s, 2200) * v, 1.5, 2.0)
def hum(d, g=1.0):
    x = tt(d); s = .6 * np.sin(2 * np.pi * 60 * x) + .35 * np.sin(2 * np.pi * 120 * x) + .2 * np.sin(2 * np.pi * 180 * x)
    s = s * (1 + .05 * np.sin(2 * np.pi * .23 * x)) + .15 * X.bp(X.noise(d), 200, 1200)
    return fade(s * g, 2, 2)
# ---------- Act III: minimal synth pulse in A minor over the fridge hum ----------
def act3(t0, t1):
    B = 60 / 120; prog = [('A2', [0, 3, 7]), ('F2', [0, 4, 7]), ('C3', [0, 4, 7]), ('G2', [0, 4, 7])]
    put(mus, hum(t1 - t0), t0, .09); k = 0; t = t0
    while t < t1 - B:
        root, ch = prog[(k // 16) % 4]; r = M(root); f = 440 * 2 ** ((r + 12 + ch[(k // 2) % 3] - 69) / 12)
        put(mus, synth_pulse(f, B * .45, 900 + 600 * (1 + np.sin(k * .1)), .45), t, .5, -.2 if k % 2 else .2)
        if k % 4 == 0: put(mus, synth_pulse(440 * 2 ** ((r - 69) / 12), B * 1.6, 500, .7), t, .5)
        if k % 16 == 0: put(mus, pad([440 * 2 ** ((r + 24 + iv - 69) / 12) for iv in ch], 8 * B), t, .25)
        t += B / 2; k += 1
# ---------- Act IV: the synth continues, strings join; then everything drops to a music box ----------
def act4(t0, t1):
    act3(t0, t1); B = 60 / 120; prog = [('A3', [0, 3, 7]), ('F3', [0, 4, 7]), ('C4', [0, 4, 7]), ('G3', [0, 4, 7])]
    for i, t in enumerate(np.arange(t0 + 4, t1 - 2, 8 * B)):
        root, ch = prog[i % 4]; r = M(root)
        for iv in ch: play('violins', nm(r + 12 + iv), t, 8 * B * .95, .45, .35, .15, attack=.6)
        play('cellos', nm(r - 12), t, 8 * B * .95, .5, .45, -.15, attack=.5)
MBOX = [72, 76, 79, 84, 83, 79, 76, 77, 81, 79, 76, 74, 72, 74, 76, 79, 77, 76, 74, 72]   # an original eight-bar lullaby line in C
def musicbox(t0, t1, start=0):
    B = .52; t = t0; i = start
    while t < t1 - .5:
        play('glockenspiel', nm(MBOX[i % len(MBOX)]), t, .9, .45, .5, .1);
        if i % 4 == 0: play('glockenspiel', nm(MBOX[i % len(MBOX)] - 12), t, .9, .3, .35, -.1)
        t += B * (1.5 if i % 8 == 7 else 1); i += 1
    return i

A1, A2, A3, A4, REV, END = CUE['I'], CUE['II'], CUE['III'], CUE['IV'], CUE['reveal'], CUE['end']
act1(A1 + .4, A2); act2(A2, A3); act3(A3, A4); act4(A4, REV)
i = musicbox(REV + .2, END); musicbox(END, DUR - 1.4, i)
for k, p in enumerate([72, 76, 79, 84]): play('glockenspiel', nm(p), DUR - 3.2 + k * .12, 2.5, .5, .5)

# ---------- foley ----------
def env(d, a=.003, tau=.1): x = tt(d); return np.minimum(1, x / a) * np.exp(-x / tau)
def crinkle(d=.15, v=1): return X.bp(X.noise(d), 2500, 9000) * env(d, .002, .03) * v
def pop(): d = .18; x = tt(d); f = 420 + 900 * np.exp(-x / .03); return X.norm(np.sin(2 * np.pi * np.cumsum(f) / SR) * env(d, .002, .04) + crinkle(d, .6))
def snap(): d = .3; return X.norm(X.hp(X.noise(d), 1500) * env(d, .001, .015) + .4 * crinkle(d))
def rustle(): d = .6; x = tt(d); return X.norm(X.bp(X.noise(d), 1200, 7000) * np.sin(np.pi * x / d) ** 2 * (.5 + .5 * np.abs(np.sin(2 * np.pi * 9 * x))))
def thunk(): d = .5; return X.norm(X.lp(X.noise(d), 220) * env(d, .002, .07) + .7 * np.sin(2 * np.pi * 62 * tt(d)) * env(d, .002, .1))
def drop(): d = .45; return X.norm(X.lp(X.noise(d), 700) * env(d, .001, .05) + .5 * np.sin(2 * np.pi * 140 * tt(d)) * env(d, .001, .06) + crinkle(d, .5))
def whoosh(): d = .5; x = tt(d); return X.norm(X.bp(X.noise(d), 400, 4000) * np.sin(np.pi * x / d) ** 2)
def card():
    r = rustle() * .6; q = pop(); o = int(.3 * SR); r[o:o + len(q)] += q[:len(r) - o]; return X.norm(r)
G = {'pop': .2, 'snap': .22, 'rustle': .16, 'thunk': .3, 'drop': .26, 'whoosh': .16, 'card': .22}
F = {'pop': pop, 'snap': snap, 'rustle': rustle, 'thunk': thunk, 'drop': drop, 'whoosh': whoosh, 'card': card}
for e in EV:
    if e['type'] in F: put(fx, F[e['type']](), e['t'], G[e['type']] * e.get('v', 1), float(rng.uniform(-.3, .3)))
# fridge hum as a room bed wherever the dairy wall is the subject (Acts III–IV), and a soft paper room tone throughout
put(amb, hum(REV - A3, 1.0), A3, .02)
room = X.norm(X.lp(X.brown(20), 400)); bedN = int(DUR * SR); put(amb, fade(np.resize(room, bedN), 2, 2), 0, .02)

# ---------- narration ----------
vg = np.zeros(N)
for e in EV:
    if e['type'] != 'vo': continue
    x, sr = sf.read(f"{H}/voices/{e['id']}.wav")
    if x.ndim > 1: x = x.mean(1)
    if sr != SR:
        import soxr; x = soxr.resample(x, sr, SR)
    x = X.compress(X.norm(X.hp(x, 70), .9), thr=.25, ratio=2.5)
    put(vox, x, e['t'], 1.0); vg[int((e['t'] - .2) * SR):int((e['t'] + len(x) / SR + .3) * SR)] = 1
k = int(.4 * SR); vg = np.convolve(vg, np.ones(k) / k, 'same')
def rms(x): m = np.abs(x).max(1) > 1e-4; return np.sqrt(np.mean(x[m] ** 2)) if m.any() else 1
vox *= .085 / rms(vox); mus *= (.085 / 2.4) / rms(mus)
mus *= (1 - .55 * vg)[:, None]          # ~ −7 dB under the voice
fx = np.stack([X.limit(fx[:, c], .5) for c in (0, 1)], 1) * .55
mix = (vox + mus + fx + amb)[:int(DUR * SR)]
mix[-int(1.5 * SR):] *= np.linspace(1, 0, int(1.5 * SR))[:, None]
mix = np.stack([X.limit(mix[:, c], .9) for c in (0, 1)], 1)
os.makedirs(f'{H}/out', exist_ok=True)
sf.write(f'{H}/out/mix.wav', mix.astype(np.float32), SR)
open(f'{H}/out/instruments_used.txt', 'w').write('\n'.join(sorted(USED)) + '\n' + '\n'.join(SM.credits(sorted(USED))) + '\n')
print('mix', mix.shape, 'peak', float(np.abs(mix).max()), sorted(USED))
