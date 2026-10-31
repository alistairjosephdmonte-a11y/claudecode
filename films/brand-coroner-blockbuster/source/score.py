"""Original score for Brand Coroner, Case 001. Minimal and investigative: a low analog pad, warm analog bass, soft piano,
restrained strings, a ticking pulse, and real silence where the film asks a question (shot 24) and before the verdict.
Harmony: D minor, i – VI – III – VII (Dm, Bb, F, C), one chord per two bars at 72 bpm. A four-note "evidence" figure
(D A E F) on piano marks act openings. → music/stems/{pad,bass,piano,strings,tick}.wav and music/score.wav
"""
import sys, os
import numpy as np, soundfile as sf
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(HERE, '../../..')); sys.path.insert(0, ROOT)
from core.audio import sampler as S
from core.audio.sfx import SR, add, bp, lp, hp

S.seed(1); rng = np.random.default_rng(5)
DUR = 480.0; N = int((DUR + 3) * SR); BEAT = 60 / 72; BAR = 4 * BEAT
ST = {k: np.zeros((N, 2), np.float32) for k in ['pad', 'bass', 'piano', 'strings', 'tick']}
put = lambda st, x, t, g=1., pan=0.: add(ST[st], x.astype(np.float32), t, g, pan)
hz = lambda m: 440 * 2 ** ((m - 69) / 12)
PROG = [(38, [62, 65, 69]), (34, [62, 65, 70]), (41, [60, 65, 69]), (36, [60, 64, 67])]   # Dm, Bb, F, C (bass, voicing)
ACT = lambda t: int(t // 80)

def pad(t0, d, notes, bright=900., g=.06):
    tt = np.arange(int(d * SR)) / SR; y = np.zeros_like(tt)
    for m in notes:
        for det in (-7, 0, 6):   # three detuned saws per note
            f = hz(m) * 2 ** (det / 1200); ph = rng.random(); y += ((tt * f + ph) % 1 * 2 - 1) * .33
    env = np.minimum(1, tt / 2.5) * np.minimum(1, (d - tt) / 2.5); y = lp(lp(y, bright), bright) * env
    return y * g
def bass(t0, d, m, g=.075):
    tt = np.arange(int(d * SR)) / SR; f = hz(m); y = np.sin(2 * np.pi * f * tt) + .35 * np.sin(2 * np.pi * 2 * f * tt) + .18 * (2 * np.abs(2 * ((tt * f) % 1) - 1) - 1)
    env = np.minimum(1, tt / .08) * np.exp(-tt / (d * .9)) * np.minimum(1, (d - tt) / .3); return lp(y, 420) * env * g
def tick(v=1., hi=1.):
    tt = np.arange(int(.05 * SR)) / SR; y = hp(rng.standard_normal(len(tt)), 2500) * np.exp(-tt / .004) + np.sin(2 * np.pi * 1800 * hi * tt) * np.exp(-tt / .01) * .4
    return bp(y, 1200, 9000) * .08 * v

# —— silences: the film's question (shot 24, 230–240 s) and the verdict (shots 47–48 get their own ending) ——
QUIET = [(232.0, 240.0)]
quiet = lambda t: any(a <= t < b for a, b in QUIET)

t = 0.0; i = 0
while t < 460:
    a = ACT(t); bass_m, voi = PROG[i % 4]; d = 2 * BAR
    if not quiet(t) and not (t + d > 231 and t < 240):
        dark = {0: 1100, 1: 900, 2: 950, 3: 1000, 4: 700, 5: 800}[a]
        put('pad', pad(t, d + 1.5, [v - 12 for v in voi] if a in (4,) else voi, dark, .05 if a != 4 else .055), t, 1., 0)
        if a in (1, 2, 3, 4): put('bass', bass(t, d * .95, bass_m), t)
        if a in (3, 4, 5):   # restrained strings: long sustained low notes
            put('strings', S.note('cellos', bass_m + 12, d + .5, .32, attack=1.2, release=1.5), t, .5, -.25)
            if a == 5: put('strings', S.note('violas', voi[0], d + .5, .25, attack=1.5, release=1.5), t, .35, .25)
    t += d; i += 1

# ticking: quarter notes, eighths in the trap (act 5); stops dead before the question
for k in range(int(460 / (BEAT / 2))):
    tt = k * BEAT / 2; a = ACT(tt)
    if quiet(tt) or 228 < tt < 240 or tt < 6: continue
    if a == 4 or (k % 2 == 0 and a in (1, 2, 3)) or (k % 4 == 0 and a in (0, 5)): put('tick', tick(1. if k % 2 == 0 else .55, 1. if k % 8 else 1.2), tt, 1., .35 if k % 2 else -.35)

# the evidence figure on piano at each act opening and on key reveals
FIG = [62, 69, 64, 65]
def figure(t0, v=.42, tr=0):
    for j, m in enumerate(FIG): put('piano', S.note('piano', m + tr, 2.4, v * (1 - .1 * j), release=1.8), t0 + j * BEAT, .9, -.1)
for a in range(6): figure(a * 80 + 1.2 if a else 2.0)
for t0 in (61.0, 121.0, 300.5, 401.0): figure(t0, .3, 12)
# the question: one held low D after the pulse stops
put('piano', S.note('piano', 38, 7, .35, release=3), 230.5, .8)
# the verdict and the end card
put('pad', pad(450, 30, [50, 57, 62, 65], 600, .05), 450.5, 1.)
put('strings', S.note('cellos', 38, 14, .3, attack=2, release=4), 452, .5)
for j, m in enumerate([62, 69, 64, 65, 62]): put('piano', S.note('piano', m, 3.5, .34, release=2.5), 462.2 + j * 1.25, .85)
put('bass', bass(470, 9, 26, .25), 470.5)

for k, v in ST.items(): sf.write(f'{HERE}/stems/{k}.wav' if os.path.isdir(f'{HERE}/stems') or os.makedirs(f'{HERE}/stems') is None else '', v[:int(DUR * SR)], SR)
mix = sum(ST.values())[:int(DUR * SR)]; mix /= max(1e-9, np.abs(mix).max()) / .8
sf.write(f'{HERE}/score.wav', mix, SR); print('score', round(len(mix) / SR, 2), 's')
