"""Kodak "they invented their downfall": narration + original investigative score + quiet Foley. low investigative underscore (D minor), subtle document
movements, minimal interface clicks, occasional bass emphasis. Cues come from audio/events.json written by build.py."""
import json, os, sys
import numpy as np, soundfile as sf
D = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LIB = '/home/user/lemomo-ai/lemo-opuscar'; sys.path.insert(0, LIB)
from core.audio import sampler as S
from core.audio.sfx import SR, add, bp, hp, lp, noise, env_exp, t_, thump, norm, limit, brown
TL = json.load(open(os.path.join(D, 'vo/timeline.json')))
DUR = TL['total']; N = int(DUR * SR); mus = np.zeros((N, 2), np.float32); fx = np.zeros((N, 2), np.float32)
EV = json.load(open(os.path.join(D, 'audio/events.json'))); S.seed(5); rng = np.random.default_rng(2)
def M(g):                         # design-grid time (16 × 30 s) → film time on the voiceover timeline
    i = min(15, int(g // 30)); t = g - 30 * i; sd = TL['scenes'][i]; w = sd['warp']
    for (a0, b0), (a1, b1) in zip(w, w[1:]):
        if t <= a1: return sd['base'] + b0 + (b1 - b0) * (t - a0) / (a1 - a0)
    return sd['base'] + w[-1][1]
ev = []; E0 = lambda t, *a: ev.append((M(t),) + a)
E = lambda t, *a: E0(t, *a)
# bed per act (A minor colour): 01 invention, 02 empire, 03 warning, 04 digital revolution, 05 collapse, 06 reckoning
ACTS = [(0, 60, ['A1', 'E2', 'C3']), (60, 120, ['F1', 'C2', 'A2']), (120, 180, ['D2', 'A2', 'F3']), (180, 300, ['A1', 'E2', 'C3']), (300, 360, ['E1', 'B1', 'G2']), (360, 480, ['F1', 'C2', 'A2'])]
for a, b, ch in ACTS:
    ra, rb = M(a), (M(b) if b < 480 else DUR)
    for t0 in np.arange(ra, rb, 15.0):
        t0 = float(t0); d = min(15.6, rb - t0 + .6)
        ev.append((t0, 'contrabass', ch[0], d, .42, -.15, .4)); ev.append((t0 + .4, 'cellos', ch[1], d, .34, .15, .28))
        if 60 <= a < 120: ev.append((t0 + 1.2, 'violas', ch[2], d - 1, .3, .3, .22))     # warm analogue textures
# act 01: sparse piano, low atmospheric pulse
for k, t0 in enumerate(np.arange(M(3), M(60), 2.5)): ev.append((float(t0), 'piano', ['A2', 'E3', 'C3', 'E3'][k % 4], 2.0, .26, -.1, .3))
for t0 in np.arange(M(2), M(60), 1.25): ev.append((float(t0), 'contrabass_pizz', 'A1', .4, .45, 0, .3))
# act 02: subtle mechanical rhythm (film advance)
for k, t0 in enumerate(np.arange(M(90), M(120), .625)): ev.append((float(t0), 'cellos_pizz', 'F2' if k % 4 else 'C2', .3, .36, -.2, .22))
# act 03: minimal tension
E(120.0, 'violins_trem', 'E5', M(180) - M(120), .14, .3, .08)
# act 04: controlled documentary percussion
for k, t0 in enumerate(np.arange(M(180), M(300), .5)): ev.append((float(t0), 'woodblock', 'a', .1, .18 + .14 * (k % 4 == 0), .3, .1))
for t0 in np.arange(M(180), M(300), 2.0): ev.append((float(t0), 'contrabass_pizz', 'A1', .5, .5, 0, .3))
# act 05: lower, restrained; act 06: sparse piano resolving to A major colour at the verdict
for t0 in np.arange(M(300), M(360), 3.0): ev.append((float(t0), 'piano', 'E2', 3.0, .3, 0, .3))
for k, t0 in enumerate(np.arange(M(366), M(450), 3.0)): ev.append((float(t0), 'piano', ['A2', 'C3', 'F2', 'E2'][k % 4], 3.0, .26, 0, .3))
for i, p_ in enumerate(['A3', 'E4', 'A4', 'C#5', 'E5']): ev.append((M(465) + .5 * i, 'piano', p_, 3.5, .3, -.2 + .1 * i, .32))
for t, kind in EV:
    if kind == 'impact': ev.append((t, 'contrabass', 'A1', 4.0, .6, 0, .5)); ev.append((t, 'timpani', 'A1', 3.0, .45, 0, .4))
    elif kind == 'low': ev.append((t, 'piano', 'A1', 5.0, .34, 0, .42))
    elif kind == 'break': ev.append((t, 'timpani', 'E2', 2.5, .5, 0, .45))
mus += S.render(ev, dur=DUR, master=False)[:N]; mus = S.room(mus, size=.5, mix=.22)
def click(v=1.0): d = .025; tt = t_(d); return (hp(noise(d), 2500) * env_exp(d, .002) + np.sin(2 * np.pi * 2200 * tt) * env_exp(d, .003) * .3) * v
def paper(v=1.0): d = .3; return bp(noise(d), 1500, 6500) * env_exp(d, .07) * (1 - np.exp(-t_(d) / .015)) * v
def register(v=1.0):
    d = .18; tt = t_(d); a = hp(noise(d), 3000) * env_exp(d, .004); b = np.sin(2 * np.pi * 2900 * tt) * env_exp(d, .05) * .35
    return (a + np.pad(b, (int(.06 * SR), 0))[:len(a)]) * v
def shutter(v=1.0):           # mechanical shutter: two clacks
    d = .12; a_ = hp(noise(d), 1800) * env_exp(d, .005); b_ = np.pad(hp(noise(d), 2200) * env_exp(d, .004), (int(.045 * SR), 0))[:len(a_)] * .7; return (a_ + b_) * v
def advance(v=1.0):           # film advance ratchet
    d = .32; out = np.zeros(int(d * SR))
    for k in range(5): c = hp(noise(.012), 3000) * env_exp(.012, .002); i = int(k * .05 * SR); out[i:i + len(c)] += c
    return out * v
def tape(d=2.5): tt = t_(d); return (lp(noise(d), 900) * .5 + np.sin(2 * np.pi * 60 * tt) * .05) * np.sin(np.pi * tt / d) ** 2 * .25
def swish(d=.6): tt = t_(d); return bp(noise(d), 2500, 7000) * np.sin(np.pi * tt / d) ** 2 * .3
for t, kind in EV:
    if kind == 'paper': add(fx, paper(1), t, .28, .2 * np.sin(t))
    elif kind in ('mark', 'click'): add(fx, click(1), t, .22, .15 * np.cos(t))
    elif kind == 'shutter': add(fx, shutter(1), t, .2, .25)
    elif kind == 'advance': add(fx, advance(1), t, .22, -.2)
    elif kind == 'tape': add(fx, tape(2.5), t, .3, 0)
    elif kind == 'draw': add(fx, swish(.8), t, .18, 0)
    elif kind in ('impact', 'break'): add(fx, thump(.8, 45), t, .45)
fx += np.repeat(lp(brown(DUR), 300)[:N, None] * .01, 2, axis=1).astype(np.float32)
# music steps back at 'growth ≠ profitability' (110.6–114 s) and before the chapter 11 reveal in scene 14
gm = np.ones(N)
for a_, b_, g_ in [(M(30.0), M(37.0), .15), (M(330.0), M(345.0), .4)]:   # scene 02 opening almost silent; scene 12 the score reduces
    gm[int(a_ * SR):int(b_ * SR)] = g_
from scipy.ndimage import uniform_filter1d
gm = uniform_filter1d(gm, int(.4 * SR)); mus *= gm[:, None]
# narration: the voiced lines at their timeline positions; music ducks about 9 dB, foley about 4 dB under the voice
voc = np.zeros((N, 2), np.float32); gv = np.ones(N)
import soxr
for l in TL['lines']:
    v, sr = sf.read(os.path.join(D, 'vo/wav', l['id'] + '.wav')); v = v if v.ndim == 1 else v.mean(1); v = soxr.resample(v, sr, SR)
    a = int(l['trim'] * SR); v = v[a:a + int((l['dur'] + .15) * SR)]
    v = v / (np.sqrt(np.mean(v[np.abs(v) > .01] ** 2)) + 1e-9) * .11
    add(voc, v.astype(np.float32), l['t'], 1.0, 0); i0, i1 = int(l['t'] * SR), int((l['t'] + len(v) / SR) * SR); gv[i0:i1] = .355
gv = uniform_filter1d(uniform_filter1d(gv, int(.25 * SR)), int(.1 * SR)); mus *= gv[:, None]; fx *= (.63 + .37 * gv)[:, None]
os.makedirs(os.path.join(D, 'audio/stems'), exist_ok=True)
for nm_, st in [('music', mus * 2.6), ('foley', fx), ('narration', voc)]: sf.write(os.path.join(D, f'audio/stems/{nm_}.wav'), st.astype(np.float32), SR)
out = mus * 2.6 + fx + voc
fi = int(1.5 * SR); out[:fi] *= np.linspace(0, 1, fi)[:, None]; tail = int(4 * SR); out[-tail:] *= np.linspace(1, 0, tail)[:, None]
out = np.stack([limit(out[:, c], .7) for c in range(2)], 1)
sf.write(os.path.join(D, 'audio/mix.wav'), out.astype(np.float32), SR); print('mix ok', float(np.abs(out).max()))
