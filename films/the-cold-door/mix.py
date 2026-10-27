"""Synthesized score (theremin main theme + one genre cue per world), synthesized foley, dialogue → out/mix.wav.
Every cue starts on its jump (the cut); 'silence' beats hard-cut the music, tails included."""
import json, os, sys, numpy as np, soundfile as sf
from scipy.signal import butter, sosfilt, fftconvolve
H = os.path.dirname(os.path.abspath(__file__)); SR = 48000
E = json.load(open(f'{H}/events.json')); DUR = E['dur']; EV = E['ev']; N = int((DUR + 3) * SR)
rng = np.random.default_rng(9)
mus = np.zeros(N); fx = np.zeros(N); vox = np.zeros(N); amb = np.zeros(N)
def tt(d): return np.arange(int(round(d * SR))) / SR
def lp(x, f, o=2): return sosfilt(butter(o, min(f, SR * .45), 'low', fs=SR, output='sos'), x)
def hp(x, f, o=2): return sosfilt(butter(o, f, 'high', fs=SR, output='sos'), x)
def bp(x, a, b, o=2): return sosfilt(butter(o, [a, b], 'band', fs=SR, output='sos'), x)
def put(buf, x, t, g=1.0):
    i = int(t * SR)
    if i < 0 or i >= len(buf): return
    n = min(len(x), len(buf) - i); buf[i:i + n] += x[:n] * g
NOTE = {'C': 0, 'C#': 1, 'Db': 1, 'D': 2, 'D#': 3, 'Eb': 3, 'E': 4, 'F': 5, 'F#': 6, 'Gb': 6, 'G': 7, 'G#': 8, 'Ab': 8, 'A': 9, 'A#': 10, 'Bb': 10, 'B': 11}
def M(s): n, o = (s[:2], s[2:]) if len(s) > 2 and s[1] in '#b' else (s[:1], s[1:]); return 12 * (int(o) + 1) + NOTE[n]
def hz(m): return 440 * 2 ** ((m - 69) / 12)
def env(n, a=.005, r=.1, hold=None):
    i = np.arange(n); A, R = max(1, int(a * SR)), max(1, int(r * SR)); h = n - R if hold is None else int(hold * SR)
    e = np.minimum(1, i / A); e = np.where(i > h, e * np.clip(1 - (i - h) / R, 0, 1), e); return e

# ---------- instruments (all synthesized) ----------
def theremin(notes, t0, step, g=.32):   # sine + a little 2nd/3rd harmonic, ~70 ms portamento, vibrato fading in after each onset
    d = len(notes) * step; x = tt(d); m = np.array([notes[min(len(notes) - 1, int(s / step))] for s in x], float)
    m = lp(np.nan_to_num(m, nan=0), 1 / .07 * .16)                     # glide
    on = (x % step); vib = .25 * np.clip((on - .15) / .2, 0, 1) * np.sin(2 * np.pi * 5.5 * x)
    f = hz(m + vib); ph = 2 * np.pi * np.cumsum(f) / SR
    y = np.sin(ph) + .18 * np.sin(2 * ph) + .08 * np.sin(3 * ph); y *= env(len(x), .08, .3)
    put(mus, spring(y) * g, t0)
def spring(x): ir = np.exp(-tt(.9) / .25) * (rng.standard_normal(int(.9 * SR)) * .12); ir[0] = 1; return fftconvolve(x, ir)[:len(x) + int(.9 * SR)]
def bass(m, t, d, g=.35): x = tt(d); ph = 2 * np.pi * hz(m) * x; y = lp(np.sin(ph) + .5 * np.sign(np.sin(ph)) * .4, 900) * env(len(x), .005, .08); put(mus, y * g, t)
def sqr(m, t, d, g=.08): x = tt(d); y = np.sign(np.sin(2 * np.pi * hz(m) * x)) * np.exp(-x / .12); put(mus, lp(y, 4000) * g, t)
def kick(t, g=.5): x = tt(.3); f = 50 + 90 * np.exp(-x / .04); put(mus, np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-x / .12) * g, t)
def snare(t, g=.25, brush=False): x = tt(.25); n = bp(rng.standard_normal(len(x)), 1200, 7000) * np.exp(-x / (.09 if brush else .05)); put(mus, (n * (.5 if brush else 1) + (0 if brush else .4 * np.sin(2 * np.pi * 190 * x) * np.exp(-x / .04))) * g, t)
def hat(t, g=.06): x = tt(.06); put(mus, bp(rng.standard_normal(len(x)), 6000, 11000) * np.exp(-x / .015) * g * (1 + .3 * np.sin(2 * np.pi * 900 * x)), t)
def fm(m, t, d, ratio=3.5, idx=2.2, decay=.6, g=.2):   # bells, vibes, toy piano, Rhodes
    x = tt(d); fc = hz(m); y = np.sin(2 * np.pi * fc * x + idx * np.exp(-x / (decay * .4)) * np.sin(2 * np.pi * fc * ratio * x)) * np.exp(-x / decay) * env(len(x), .002, .05); put(mus, y * g, t)
KS = {}
def ks(m, t, d=1.2, g=.25, bright=.5):   # Karplus–Strong pluck (cached per pitch)
    key = (m, round(d, 2), bright)
    if key not in KS:
        p = max(2, int(SR / hz(m))); n = int(d * SR); buf = list(rng.uniform(-1, 1, p)); out = np.zeros(n)
        for i in range(n): j = i % p; out[i] = buf[j]; buf[j] = .996 * (bright * buf[j] + (1 - bright) * buf[(j + 1) % p])
        KS[key] = lp(out, 5000)
    put(mus, KS[key] * g, t)
def reed(m, t, d, g=.1):   # accordion-ish: detuned pulses
    x = tt(d); y = sum(np.sign(np.sin(2 * np.pi * hz(m) * (1 + k) * x)) for k in (-.003, 0, .004)) / 3; put(mus, lp(y, 2400) * env(len(x), .03, .08) * g, t)
def tuba(m, t, d, g=.3): x = tt(d); ph = 2 * np.pi * hz(m) * x; y = lp(2 * (ph / (2 * np.pi) % 1) - 1, 500) * env(len(x), .03, .1); put(mus, y * g, t)
def strings(ms, t, d, g=.06, trem=0):
    x = tt(d); y = sum(lp(2 * ((hz(m) * (1 + k) * x) % 1) - 1, 2500) for m in ms for k in (-.004, .004))
    if trem: y *= .6 + .4 * np.sign(np.sin(2 * np.pi * 9 * x))
    put(mus, y * env(len(x), .3, .4) * g, t)
def slide(t, up=True, g=.1): x = tt(.6); f = (600 + 900 * x / .6) if up else (1500 - 900 * x / .6); put(mus, np.sin(2 * np.pi * np.cumsum(f) / SR) * env(len(x), .02, .1) * g, t)

# ---------- cues ----------
DM = ['D4', 'A4', 'Bb4', 'A4', 'E4', 'F4', 'E4', 'Eb4', 'D4']       # main theme: a chromatic descent in D minor
def main_theme(t0, t1, bpm=100, lead=True):
    B = 60 / bpm; k = 0; t = t0; prog = [M('D2'), M('Bb1'), M('G1'), M('A1')]
    while t < t1 - B:
        r = prog[(k // 8) % 4]
        if k % 2 == 0: bass(r, t, B * .9)
        sqr(r + 24 + [0, 3, 7, 12][k % 4], t, B * .4); sqr(r + 24 + [7, 12, 3, 0][k % 4], t + B / 2, B * .4)
        if k % 4 == 0: kick(t)
        if k % 4 == 2: snare(t)
        hat(t + B / 2); k += 1; t += B
    if lead and t1 - t0 > 6: theremin([M(n) for n in DM], t0 + 1, min(1.4, (t1 - t0 - 2) / len(DM)))
def polka(t0, t1):
    B = 60 / 140; k = 0; t = t0; ch = [M('F3'), M('C3')]
    while t < t1 - B:
        r = ch[(k // 8) % 2]; tuba(r - 12 if k % 2 == 0 else r - 5, t, B * .6) if k % 2 == 0 else [reed(r + iv, t, B * .5) for iv in (0, 4, 7)]
        if k % 4 == 0: reed(r + 12 + [4, 7, 9, 7][(k // 4) % 4], t, B * 1.6, .07)
        k += 1; t += B
def toy(t0, t1, bpm=96, root='C'):
    B = 60 / bpm; k = 0; t = t0; mel = [0, 4, 7, 12, 11, 7, 4, 2]
    while t < t1 - B:
        fm(M(root + '5') + mel[k % 8], t, .6, 3.5, 1.4, .35, .14)
        if k % 2 == 0: fm(M(root + '3') + [0, 7][(k // 2) % 2], t, .8, 1, .8, .5, .12)
        k += 1; t += B
def swing(t0, t1, bpm=128):
    B = 60 / bpm; k = 0; t = t0; prog = [M('F2'), M('D2'), M('G2'), M('C2')]
    while t < t1 - B:
        r = prog[(k // 4) % 4]; bass(r + [0, 4, 7, 9][k % 4], t, B * .8, .3); snare(t + B * .66, .12, brush=True); hat(t, .04)
        if k % 4 == 0: [fm(r + 24 + iv, t, 1.4, 4, 1.2, .8, .07) for iv in (4, 9, 14)]
        k += 1; t += B
def tremolo(t0, t1):
    for i, t in enumerate(np.arange(t0, t1 - 2, 4)): strings([M('D4'), M('F4'), M('A4') + (1 if i % 2 else 0)], t, 4.2, .05, trem=1); bass(M('D2'), t, 3.8, .25)
def surf(t0, t1):
    B = 60 / 150; k = 0; t = t0
    while t < t1 - B:
        ks(M('E3') + [0, 0, 3, 5, 7, 5, 3, 0][k % 8], t, .35, .18, .7)
        if k % 2 == 0: kick(t, .35)
        if k % 4 == 2: snare(t, .18)
        k += 1; t += B
def bossa(t0, t1):
    B = 60 / 112; k = 0; t = t0; prog = [M('A2'), M('D3'), M('G2'), M('C3')]
    while t < t1 - B:
        r = prog[(k // 8) % 4]
        if k % 8 in (0, 3, 6): bass(r, t, B * 1.2, .22)
        if k % 8 in (1, 2, 4, 6, 7): [ks(r + 12 + iv, t, .8, .07, .45) for iv in (3, 7, 10)]
        hat(t, .025); k += 1; t += B
def rhodes(t0, t1):
    for i, t in enumerate(np.arange(t0, t1 - 2, 3.2)): [fm(M(n) + 0, t, 3.4, 1, 1.6, 1.4, .07) for n in [['D3', 'F3', 'A3', 'C4'], ['G3', 'Bb3', 'D4', 'F4']][i % 2]]
def float_cue(t0, t1):
    for k, t in enumerate(np.arange(t0, t1 - 1, 60 / 90)): fm(M('G4') + [0, 4, 7, 11, 7, 4][k % 6], t, 1.2, 4, 1.0, .9, .08); (k % 2 == 0) and ks(M('G2') + [0, 7][(k // 2) % 2], t, 1.0, .12, .5)
def maze_cue(t0, t1):
    B = 60 / 120; k = 0; t = t0
    while t < t1 - B:
        tuba(M('C2') + [0, 7, 5, 7][k % 4], t, B * .5, .25)
        if k % 8 == 7: slide(t, k % 16 == 7)
        k += 1; t += B
def four_floor(t0, t1, stinger_every=None):
    B = .5; t = t0
    while t < t1 - .1: kick(t, .45); hat(t + .25); t += B
CUE = {'home': lambda a, b: main_theme(a, b), 'funnel': polka, 'counter': lambda a, b: toy(a, b, 96, 'C'), 'round': float_cue, 'maze': maze_cue,
       'kitchen': lambda a, b: swing(a, b, 120), 'garage': lambda a, b: swing(a, b, 140), 'dock': tremolo, 'konbini': lambda a, b: toy(a, b, 132, 'G'),
       'track': surf, 'globe': lambda a, b: main_theme(a, b, 112, lead=False), 'beige': bossa}
J = [e for e in EV if e['type'] == 'jump']
end_t = next(e['t'] for e in EV if e['type'] == 'end')
for i, j in enumerate(J):
    t1 = J[i + 1]['t'] if i + 1 < len(J) else end_t
    w = j['world']
    if w in ('london', 'paris', 'sydney', 'chicago', 'manchester', 'melbourne'):
        four_floor(j['t'], t1); fm(M('A5') if w in ('london', 'paris', 'sydney') else M('D4'), j['t'], .6, 2, 2, .3, .2)   # one stinger per city
    elif w == 'home' and i > 0: rhodes(j['t'], t1); theremin([M(n) for n in ['A4', 'F4', 'E4', 'D4']], j['t'] + 2, 2.4, .2)
    else: CUE[w](j['t'] + .02, t1)
title = next(e['t'] for e in EV if e['type'] == 'title'); main_theme(title, title + 3.2, 100, lead=False); [fm(M(n), title, 1.6, 3.5, 2, .9, .22) for n in ('D5', 'F5', 'A5')]
main_theme(end_t, DUR - 1, 100)
# silences: hard-cut the music (reverb tails included) for each cold pause
gate = np.ones(N)
for e in EV:
    if e['type'] == 'silence': a, b = int(e['t'] * SR), int((e['t'] + e['d']) * SR); gate[a:b] = 0
mus *= gate

# ---------- foley ----------
def noise(d): return rng.standard_normal(int(d * SR))
def portal_open(): x = tt(1.4); sub = np.sin(2 * np.pi * np.cumsum(60 - 20 * x) / SR) * np.exp(-x / .5); dn = bp(noise(1.4), 300, 3000) * np.exp(-x / .35); sw = np.sin(2 * np.pi * np.cumsum(300 + 900 * x) / SR) * np.clip(x / 1.2, 0, 1) * .3; return sub + .5 * dn + sw
def whoosh(d=.7): x = tt(d); return bp(noise(d), 300, 4000) * np.sin(np.pi * x / d) ** 2
def pop(): x = tt(.18); f = 420 + 900 * np.exp(-x / .03); return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-x / .04)
def boing(): x = tt(.45); f = 220 + 260 * x / .45; return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-x / .2) * (1 + .3 * np.sin(2 * np.pi * 14 * x))
def squish(): x = tt(.35); return lp(noise(.35), 900) * np.exp(-x / .08) + .6 * np.sin(2 * np.pi * np.cumsum(180 - 120 * x) / SR) * np.exp(-x / .1)
def squeak(): x = tt(.25); return np.sin(2 * np.pi * np.cumsum(1400 + 600 * np.sin(np.pi * x / .25)) / SR) * np.sin(np.pi * x / .25) * .6
def thud(): x = tt(.5); return lp(noise(.5), 200) * np.exp(-x / .06) + .7 * np.sin(2 * np.pi * 60 * x) * np.exp(-x / .1)
def beep(): x = tt(1.6); return np.sin(2 * np.pi * 1000 * x) * (np.sin(2 * np.pi * 1.6 * x) > 0) * .5
def scribble(): x = tt(1.0); return bp(noise(1.0), 2500, 7000) * (.5 + .5 * np.abs(np.sin(2 * np.pi * 7 * x))) * .5
def kazoo(): x = tt(.7); f = 300 + 40 * np.sin(2 * np.pi * 6 * x); return lp(np.sign(np.sin(2 * np.pi * np.cumsum(f) / SR)), 2500) * np.exp(-x / .5) * .5
def creak(): x = tt(.9); f = 140 + 60 * np.sin(2 * np.pi * .9 * x); return bp(np.sin(2 * np.pi * np.cumsum(f) / SR) * np.abs(np.sin(2 * np.pi * 28 * x)) ** 5, 200, 2500)
def norm(x): return x / (np.abs(x).max() + 1e-9)
SFX = {'openPortal': (portal_open, .5, .3), 'rollFridge': (creak, .3, 0), 'curdOut': (squish, .4, .2), 'getBiscuits': (pop, .3, 0), 'fillBasket': (pop, .3, 1.5), 'chicken': (boing, .3, .2),
       'moth': (squeak, .3, .3), 'clerk': (whoosh, .25, .5), 'ladder': (whoosh, .3, .1), 'float': (squeak, .1, .2), 'bottles': (thud, .3, 4), 'turnstile': (creak, .35, .5), 'secondBasket': (thud, .4, .8),
       'frost': (whoosh, .3, .5), 'machine': (thud, .3, .4), 'truckBack': (beep, .2, 0), 'dockThud': (thud, .6, .2), 'lift': (thud, .3, 1), 'pushOut': (pop, .4, .3), 'scream': (kazoo, .2, .1),
       'flag': (pop, .3, 0), 'baguette': (boing, .3, .3), 'endcaps': (thud, .3, 1), 'write': (scribble, .3, .2), 'curdWave': (squeak, .4, .2), 'newCard': (whoosh, .3, .2), 'vote': (pop, .25, 1)}
for e in EV:
    if e['type'] == 'act' and e['name'] in SFX:
        f, g, dt = SFX[e['name']]; put(fx, norm(f()) * g, e['t'] + dt)
        if e['name'] == 'endcaps': [put(fx, norm(thud()) * .3, e['t'] + 1 + i * (1.1 - i * .12)) for i in range(6)]
    if e['type'] == 'jump' and e['t'] > 0: put(fx, norm(whoosh(.8 if not e['fast'] else .35)) * .35, e['t'] - (.4 if not e['fast'] else .15)); put(fx, norm(portal_open())[:int(.5 * SR)] * .2, e['t'] - .9)
# room tone: fluorescent hum at home, a fridge everywhere quietly
x = tt(DUR); hum = (.5 * np.sin(2 * np.pi * 120 * x) + .2 * np.sin(2 * np.pi * 240 * x)) * .5 + .2 * lp(rng.standard_normal(len(x)), 300); put(amb, hum * .012, 0)

# ---------- dialogue ----------
import soxr
vg = np.zeros(N)
for e in EV:
    if e['type'] != 'vo': continue
    y, sr = sf.read(f"{H}/voices/{e['id']}.wav"); y = y.mean(1) if y.ndim > 1 else y
    if sr != SR: y = soxr.resample(y, sr, SR)
    put(vox, y, e['t']); vg[int((e['t'] - .15) * SR):int((e['t'] + len(y) / SR + .2) * SR)] = 1
k = int(.3 * SR); vg = np.convolve(vg, np.ones(k) / k, 'same')
def rms(x): m = np.abs(x) > 1e-4; return np.sqrt(np.mean(x[m] ** 2)) if m.any() else 1
vox *= .09 / rms(vox); mus *= .045 / rms(mus); mus *= 1 - .55 * vg
fx = np.tanh(fx * 1.2) * .6
mix = (vox + mus + fx * .9 + amb)[:int(DUR * SR)]
mix[-int(1.4 * SR):] *= np.linspace(1, 0, int(1.4 * SR))
mix = np.tanh(mix * 1.1) / 1.1
st = np.stack([mix, mix], 1); os.makedirs(f'{H}/out', exist_ok=True)
sf.write(f'{H}/out/mix.wav', st.astype(np.float32), SR); print('mix', st.shape, 'peak', float(np.abs(st).max()))
