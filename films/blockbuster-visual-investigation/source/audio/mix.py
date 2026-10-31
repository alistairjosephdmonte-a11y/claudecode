#!/usr/bin/env python3
"""Score, Foley and narration for "Blockbuster: The $50 Million Decision" (Visual Investigation) → out/mix.wav + out/stems/.
Sound palette from styles/visual-investigation: low D bed, pendulum tick on the clock sections, pizzicato ostinato (Dm – B♭ – Gm – A) under the
slow sections, minor-second tremolo for tension, slow chords for the verdict columns, D minor add9 + vibraphone for the evidence map, harp to end.
Foley is procedural: paper (documents), shutter (photos), pencil (schematics), whoosh/rewind (cuts), one thump (the filing), glockenspiel for ✓ badges.
Narration: the Brand Coroner voice lines (out/voice/sNN.wav of the previous cut), placed at film.json times; s03 is trimmed (the film shows no room)."""
import json, os, sys
import numpy as np, soundfile as sf, soxr
from scipy.ndimage import uniform_filter1d
D = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LIB = os.path.abspath(os.path.join(D, '../..')); sys.path.insert(0, LIB)
from core.audio import sampler as S
from core.audio.sfx import SR, add, bp, hp, lp, noise, env_exp, t_, whoosh, thump, norm, limit, brown

F = json.load(open(os.path.join(D, 'film.json'))); DUR = F['dur']; SEC = F['sections']
VOICE = os.path.join(D, '../brand-coroner-blockbuster/out/voice')
N = int(DUR * SR); mus = np.zeros((N, 2), np.float32); fx = np.zeros((N, 2), np.float32); voc = np.zeros((N, 2), np.float32)
S.seed(11); rng = np.random.default_rng(3)
ev = []
def E(*a): ev.append(a)

# ── score ──
# bed: low D held by contrabass + cellos, renewed every 10 s (quieter inside the question 230–240)
for t0 in np.arange(4.0, 470, 10.0):
    t0 = float(t0); g = .32 if 230 <= t0 < 240 else .45
    if 450 <= t0 < 470: continue
    E(t0, 'contrabass', 'D2', 10.6, .5, -.2, g); E(t0 + .3, 'cellos', 'A2' if not (370 <= t0 < 420) else 'D3', 10.3, .42, .2, g * .8)
# cold open hit and evidence slams
E(0.0, 'gran_cassa', 'hit', 1.6, .95, 0, 1.0); E(0.0, 'timpani', 'D2', 1.8, .9, 0, .9); E(0.0, 'contrabass', 'D2', .5, .9, -.2, .8)
for tt in (0.7, 1.0, 1.3): E(tt, 'woodblock', 'a', .2, .7, .3, .5); E(tt, 'timpani', 'A2', .6, .5, 0, .4)
E(4.0, 'timpani', 'D2', 2.0, .75, 0, .8); E(4.0, 'sus_cymbal', 'roll', 1.4, .35, .2, .22); E(4.2, 'violins_trem', 'A5', 3.2, .22, .4, .16)
# pizzicato ostinato in eighths, Dm → B♭ → Gm → A (2 s per chord) under the slow sections
PAT = [['D4', 'F4', 'A4', 'F4'], ['D4', 'F4', 'Bb4', 'F4'], ['D4', 'G4', 'Bb4', 'G4'], ['C#4', 'E4', 'A4', 'E4']]
ROOT = ['D2', 'Bb1', 'G2', 'A1']
def ostinato(a, b, g=.42):
    tt = a; k = 0
    while tt < b - .01:
        ci = int((tt - a) // 2) % 4; E(tt, 'violas_pizz', PAT[ci][k % 4], .3, .4 + .12 * (k % 4 == 0), .25, g)
        if k % 8 == 0: E(tt, 'contrabass_pizz', ROOT[ci] if ROOT[ci] != 'Bb1' else 'Bb2', .6, .6, -.2, g * .9)
        k += 1; tt += .25
for a, b in [(80, 130), (160, 228.5), (330, 368)]: ostinato(a, b)
# the record columns and the verdict columns: slow chords
def chords(t0, n, dur=2.5, g=1.0):
    for i in range(n):
        notes = [['D3', 'A3', 'F4'], ['Bb2', 'F3', 'D4'], ['G2', 'D3', 'Bb3'], ['A2', 'E3', 'C#4']][i % 4]; tt = t0 + i * dur
        E(tt, 'cellos', notes[0], dur + .2, .4, .15, .4 * g); E(tt, 'violas', notes[1], dur + .2, .35, -.1, .3 * g); E(tt, 'violins', notes[2], dur + .2, .3, .3, .2 * g); E(tt, 'harp', notes[0], 2.0, .5, -.2, .28 * g)
chords(20.0, 4); chords(30.0, 12, 2.5, .7); chords(440.0, 4)
# the number: one cello note; the question: a held low D only, no rhythm
E(63.0, 'cellos', 'D3', 8.5, .35, 0, .4); E(230.4, 'piano', 'D2', 7, .35, 0, .5)
# the scale & fees: slow strings under the facts
E(120.0, 'cellos', 'F3', 9.5, .35, .1, .35); E(130.0, 'cellos', 'D3', 29.5, .32, .1, .3); E(140.0, 'violas', 'A3', 19.5, .28, -.1, .22)
# counterattack: strings rising under the clock
for t0, n, inst, g in [(240, 'D3', 'cellos', .32), (260, 'F3', 'violas', .26), (280, 'A3', 'violas', .24), (300, 'D4', 'violins', .2), (310, 'F4', 'violins', .2)]: E(float(t0), inst, n, 20.5, .3, .2, g)
# tension: minor-second tremolo (E5/F5) through the squeeze and the filing, heartbeat pulse; cut before the filing hit
E(370.0, 'violins_trem', 'E5', 31.0, .28, .35, .2); E(374.0, 'violins_trem', 'F5', 27.0, .3, -.35, .2)
for tt in np.arange(380.4, 400.8, 1.0): E(float(tt), 'contrabass_pizz', 'D2', .5, .75, 0, .6)
E(401.0, 'gran_cassa', 'hit', 2.0, .9, 0, .9); E(401.0, 'timpani', 'D2', 2.2, .85, 0, .8)
E(410.0, 'cellos', 'D3', 10.5, .3, 0, .3)
# back to Dallas: low strings; hypotheticals: soft tremolo
E(420.0, 'cellos', 'D3', 10.2, .35, 0, .35); E(430.0, 'violins_trem', 'A4', 10, .2, .3, .14)
# ✓ badges: rising glockenspiel
for base in (17.5, 265.5):
    for i, p in enumerate(['D6', 'A6']): E(base + .12 * i, 'glockenspiel', p, 1.2, .55, -.2 + .4 * i, .5)
for i, (tt, p) in enumerate([(442.2, 'D6'), (443.6, 'F6'), (446.2, 'A6')]): E(tt, 'glockenspiel', p, 1.2, .55, -.2 + .2 * i, .5)
# evidence map: D minor add9 + vibraphone arpeggio; verdict: one held chord; end card on harp
E(450.0, 'gran_cassa', 'hit', 2.0, .5, 0, .45)
for p, pan in [('D2', 0), ('D3', -.2), ('A3', .2), ('E4', -.3), ('F4', .3)]: E(450.0, 'cellos' if p != 'D2' else 'contrabass', p, 12.2, .4, pan, .38)
E(450.4, 'violins', 'A4', 11.6, .3, .35, .2)
for i, p in enumerate(['D4', 'A4', 'E5', 'F5', 'A5', 'D6']): E(450.4 + .25 * i, 'vibraphone', p, 2.5, .45, -.3 + .12 * i, .35)
for p, pan in [('D2', 0), ('A2', -.2), ('F3', .2), ('E4', 0)]: E(462.0, 'cellos' if p != 'D2' else 'contrabass', p, 8.4, .35, pan, .34)
for i, p in enumerate(['D3', 'A3', 'E4', 'F4', 'A4', 'D5']): E(470.0 + .5 * i, 'harp', p, 4.0, .45, -.2 + .08 * i, .33)
E(474.0, 'cellos', 'D2', 6, .3, 0, .3)

mus += S.render(ev, dur=DUR, master=False)[:N]
mus = S.room(mus, size=.5, mix=.2)

# ── Foley ──
def tick(v=1.0, f=2400): d = .03; tt = t_(d); return (hp(noise(d), 1800) * env_exp(d, .003) + np.sin(2 * np.pi * f * tt) * env_exp(d, .004) * .6) * v
def paper(v=1.0): d = .25; return bp(noise(d), 1200, 6000) * env_exp(d, .05) * (1 - np.exp(-t_(d) / .01)) * v
def shutter(v=1.0):
    d = .09; a = hp(noise(d), 2000) * env_exp(d, .006); b = np.pad(hp(noise(.05), 1500) * env_exp(.05, .005), (int(.045 * SR), 0))[:len(a)]; return norm(a + b * .8) * v
def rewind(d=1.4, v=1.0):
    tt = t_(d); f = 3000 * np.exp(-tt * 1.6) + 300; ph = 2 * np.pi * np.cumsum(f) / SR
    return (bp(noise(d), 600, 4000) * .5 + np.sin(ph) * .3 + np.sin(ph * 2.01) * .15) * np.sin(np.pi * tt / d) * v
def pencil(d=.6): return bp(noise(d), 2500, 7000) * (.5 + .5 * np.abs(np.sin(t_(d) * 23))) * env_exp(d, d * .8) * .45
def key(): d = .035; return norm(bp(noise(d), 900, 5000) * env_exp(d, .004) + np.sin(2 * np.pi * 180 * t_(d)) * env_exp(d, .008) * .4)

PAPER = [.7, 11.4, 30.6, 50.6, 122.0, 142.2, 241.6, 261.4, 270.4, 280.4, 340.6, 380.6, 401.0, 410.5, 420.8, 421.8]
SHUT = [1.3, 4.0, 10.5, 80.0, 83.0, 90.0, 92.4, 100.0, 101.6, 130.0, 160.0, 190.6, 192.0, 250.6, 252.4, 263.4, 330.4, 331.4, 402.6, 412.0, 413.0, 420.0]
CUTS = [10.5, 20.0, 30.0, 63.0, 72.0, 80.0, 90.0, 100.0, 110.0, 120.0, 130.0, 140.0, 150.0, 160.0, 170.0, 180.0, 190.0, 211.0, 220.0, 230.0, 240.0, 250.0, 260.0, 270.0, 280.0,
        290.0, 300.0, 310.0, 320.0, 330.0, 340.0, 350.0, 360.0, 370.0, 380.0, 390.0, 400.0, 410.0, 420.0, 430.0, 440.0, 450.0, 462.0, 470.0]
for tt in PAPER: add(fx, paper(1), tt, .42, .25 * np.sin(tt))
for tt in SHUT: add(fx, shutter(1), tt, .45, .3 * np.cos(tt))
for tt in CUTS: add(fx, whoosh(.25, 1), tt - .08, .22)
add(fx, thump(1.0, 48), 0.0, .6); add(fx, whoosh(.3, 1), 1.7, .35); add(fx, rewind(1.4, 1), 2.6, .5)
for a, b in [(170.6, 176.0), (180.6, 186.0), (211.0, 214.5), (300.5, 304.0), (350.6, 354.0), (430.2, 433.4)]:
    for tt in np.arange(a, b, .7): add(fx, pencil(.5), float(tt), .3, -.2)
for a, b in [(110.5, 118.0), (390.0, 395.0)]:     # dots appearing: soft dense clicks
    for tt in np.arange(a, b, .06): add(fx, tick(.25, 3200 + 400 * rng.random()), float(tt), .08, rng.uniform(-.5, .5))
for tt in np.arange(240.5, 330, .5): add(fx, tick(.6, 2400 if int(tt * 2) % 2 else 2600), float(tt), .2, -.2)   # the clock sections: pendulum
for tt in np.arange(370.0, 400.0, .5): add(fx, tick(.8, 2400), float(tt), .26, .2)
for at in (241.6, 261.4, 401.0):                # filings land with a few keystrokes
    for k in range(8): add(fx, key(), at + .05 + k * .045, .26, .2 - .05 * k)
add(fx, thump(1.0, 42), 401.0, .9)
fx += np.repeat(lp(brown(DUR), 400)[:N, None] * .012, 2, axis=1).astype(np.float32)   # room tone

# ── narration ──
VO = {}
for k, at, cut in F['voice']:
    v, sr = sf.read(os.path.join(VOICE, f'{k}.wav')); v = v if v.ndim == 1 else v.mean(1); v = soxr.resample(v, sr, SR)
    if cut:   # silence the trimmed clause in place (keeps every later word on its subtitle time)
        a, b = int((cut[0] - at) * SR), int((cut[1] - at) * SR); fd = int(.03 * SR)
        v[a:a + fd] *= np.linspace(1, 0, fd); v[a + fd:b - fd] = 0; v[b - fd:b] *= np.linspace(0, 1, fd)
    v = v / (np.sqrt(np.mean(v[np.abs(v) > .01] ** 2)) + 1e-9) * .11
    add(voc, v, at, 1.0, 0); VO[k] = (at, at + len(v) / SR)

# ── ducking: music −9 dB under the voice (Foley −4 dB) ──
g = np.ones(N)
for a, b in VO.values(): g[int(a * SR):int(b * SR)] = .355
g = uniform_filter1d(uniform_filter1d(g, int(.25 * SR)), int(.1 * SR)); mus *= g[:, None]; fx *= (.63 + .37 * g)[:, None]
mus *= 3.0; fx *= .8
out = mus + fx + voc
tail = int(2.0 * SR); out[-tail:] *= np.linspace(1, 0, tail)[:, None]
def tp_limit(x, ceil):
    from scipy.signal import resample_poly
    from scipy.ndimage import maximum_filter1d, minimum_filter1d
    up = resample_poly(x, 4, 1); n = int(.004 * SR * 4)
    gg = np.minimum(1, ceil / np.maximum(maximum_filter1d(np.abs(up), 2 * n + 1), 1e-9)); gg = uniform_filter1d(minimum_filter1d(gg, 2 * n + 1), n)
    return resample_poly(up * gg, 1, 4)[:len(x)]
out = np.stack([tp_limit(limit(out[:, c], .5), .45) for c in range(2)], 1)
os.makedirs(os.path.join(D, 'out/stems'), exist_ok=True)
sf.write(os.path.join(D, 'out/mix.wav'), out.astype(np.float32), SR)
for nm, st in [('music', mus), ('foley', fx), ('narration', voc)]: sf.write(os.path.join(D, f'out/stems/{nm}.wav'), st.astype(np.float32), SR)
print('mix', out.shape, 'peak', float(np.abs(out).max()))
