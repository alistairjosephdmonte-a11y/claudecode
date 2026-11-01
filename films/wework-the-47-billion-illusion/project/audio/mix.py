"""Restrained documentary sound for the silent animatic: low investigative underscore (D minor), subtle document
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
# bed: low D held, renewed every 15 s; harmony moves per act (i – VI – iv – V colour)
ACTS = [(0, 60, ['D2', 'A2', 'F3']), (60, 120, ['D2', 'A2', 'E3']), (120, 210, ['Bb1', 'F2', 'D3']), (210, 300, ['G1', 'D2', 'Bb2']), (300, 360, ['A1', 'E2', 'C#3']), (360, 450, ['D2', 'A2', 'F3']), (450, 480, ['D2', 'A2', 'E3'])]
for a, b, ch in ACTS:
    ra, rb = M(a), (M(b) if b < 480 else DUR)
    for t0 in np.arange(ra, rb, 15.0):
        t0 = float(t0); d = min(15.6, rb - t0 + .6)
        ev.append((t0, 'contrabass', ch[0], d, .5, -.15, .5)); ev.append((t0 + .4, 'cellos', ch[1], d, .42, .15, .36)); ev.append((t0 + 1.2, 'violas', ch[2], d - 1, .3, .3, .2))
# a slow, quiet pulse in the machine/documents acts (acts 3–4): pizzicato every 1.25 s
for k, t0 in enumerate(np.arange(M(122), M(298), 1.25)): ev.append((float(t0), 'cellos_pizz', 'D3' if k % 4 else 'A2', .4, .45, -.2, .28))
# tension under the break (act 5): soft tremolo minor second
E(300.0, 'violins_trem', 'E5', M(330) - M(300), .2, .3, .12); E(306.0, 'violins_trem', 'F5', M(330) - M(306), .22, -.3, .12)
# verdict & end slate
for i, p in enumerate(['D4', 'A4', 'E5', 'F5', 'A5']): ev.append((M(473.4) + .5 * i, 'vibraphone', p, 3.0, .35, -.2 + .1 * i, .3))
for t, kind in EV:
    if kind == 'boom': ev.append((t, 'contrabass', 'D1' if 'D1' in [] else 'D2', 4.0, .7, 0, .55)); ev.append((t, 'timpani', 'D2', 3.0, .5, 0, .45))
    elif kind == 'low': ev.append((t, 'piano', 'D2', 5.0, .38, 0, .45))
    elif kind == 'break': ev.append((t, 'timpani', 'A1', 2.5, .55, 0, .5))
mus += S.render(ev, dur=DUR, master=False)[:N]; mus = S.room(mus, size=.5, mix=.22)
def click(v=1.0): d = .025; tt = t_(d); return (hp(noise(d), 2500) * env_exp(d, .002) + np.sin(2 * np.pi * 2200 * tt) * env_exp(d, .003) * .3) * v
def paper(v=1.0): d = .3; return bp(noise(d), 1500, 6500) * env_exp(d, .07) * (1 - np.exp(-t_(d) / .015)) * v
def shutter(v=1.0): d = .08; return hp(noise(d), 2500) * env_exp(d, .006) * v
def swish(d=.6): tt = t_(d); return bp(noise(d), 2500, 7000) * np.sin(np.pi * tt / d) ** 2 * .3
for t, kind in EV:
    if kind == 'paper': add(fx, paper(1), t, .28, .2 * np.sin(t))
    elif kind == 'mark': add(fx, click(1), t, .22, .15 * np.cos(t))
    elif kind == 'shutter': add(fx, shutter(1), t, .2, .25)
    elif kind == 'draw': add(fx, swish(.8), t, .18, 0)
    elif kind in ('boom', 'break'): add(fx, thump(.8, 45), t, .45)
fx += np.repeat(lp(brown(DUR), 300)[:N, None] * .01, 2, axis=1).astype(np.float32)
# music steps back at 'growth ≠ profitability' (110.6–114 s) and before the chapter 11 reveal in scene 14
gm = np.ones(N)
for a_, b_ in [(M(110.6), M(114.0)), (M(409.8), M(410.5))]:
    gm[int(a_ * SR):int(b_ * SR)] = .25
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
