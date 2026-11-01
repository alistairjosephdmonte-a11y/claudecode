"""Restrained documentary sound for the silent animatic: low investigative underscore (D minor), subtle document
movements, minimal interface clicks, occasional bass emphasis. Cues come from audio/events.json written by build.py."""
import json, os, sys
import numpy as np, soundfile as sf
D = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LIB = '/home/user/lemomo-ai/lemo-opuscar'; sys.path.insert(0, LIB)
from core.audio import sampler as S
from core.audio.sfx import SR, add, bp, hp, lp, noise, env_exp, t_, thump, norm, limit, brown
DUR = 480; N = int(DUR * SR); mus = np.zeros((N, 2), np.float32); fx = np.zeros((N, 2), np.float32)
EV = json.load(open(os.path.join(D, 'audio/events.json'))); S.seed(5); rng = np.random.default_rng(2)
ev = []; E = lambda *a: ev.append(a)
# bed: low D held, renewed every 15 s; harmony moves per act (i – VI – iv – V colour)
ACTS = [(0, 60, ['D2', 'A2', 'F3']), (60, 120, ['D2', 'A2', 'E3']), (120, 210, ['Bb1', 'F2', 'D3']), (210, 300, ['G1', 'D2', 'Bb2']), (300, 360, ['A1', 'E2', 'C#3']), (360, 450, ['D2', 'A2', 'F3']), (450, 480, ['D2', 'A2', 'E3'])]
for a, b, ch in ACTS:
    for t0 in np.arange(a, b, 15.0):
        t0 = float(t0); d = min(15.6, b - t0 + .6)
        E(t0, 'contrabass', ch[0], d, .5, -.15, .5); E(t0 + .4, 'cellos', ch[1], d, .42, .15, .36); E(t0 + 1.2, 'violas', ch[2], d - 1, .3, .3, .2)
# a slow, quiet pulse in the machine/documents acts (acts 3–4): pizzicato every 1.25 s
for t0 in np.arange(122, 298, 1.25): E(float(t0), 'cellos_pizz', 'D3' if int(t0 / 1.25) % 4 else 'A2', .4, .45, -.2, .28)
# tension under the break (act 5): soft tremolo minor second
E(300.0, 'violins_trem', 'E5', 30, .2, .3, .12); E(306.0, 'violins_trem', 'F5', 24, .22, -.3, .12)
# verdict & end slate
for i, p in enumerate(['D4', 'A4', 'E5', 'F5', 'A5']): E(474.0 + .5 * i, 'vibraphone', p, 3.0, .35, -.2 + .1 * i, .3)
for t, kind in EV:
    if kind == 'boom': E(t, 'contrabass', 'D1' if 'D1' in [] else 'D2', 4.0, .7, 0, .55); E(t, 'timpani', 'D2', 3.0, .5, 0, .45)
    elif kind == 'low': E(t, 'piano', 'D2', 5.0, .38, 0, .45)
    elif kind == 'break': E(t, 'timpani', 'A1', 2.5, .55, 0, .5)
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
out = mus * 2.6 + fx
fi = int(1.5 * SR); out[:fi] *= np.linspace(0, 1, fi)[:, None]; tail = int(4 * SR); out[-tail:] *= np.linspace(1, 0, tail)[:, None]
out = np.stack([limit(out[:, c], .7) for c in range(2)], 1)
sf.write(os.path.join(D, 'audio/mix.wav'), out.astype(np.float32), SR); print('mix ok', float(np.abs(out).max()))
