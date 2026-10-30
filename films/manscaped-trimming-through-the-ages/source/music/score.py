"""Original score for "Trimming Through the Ages". One central motif (below), rearranged per era — never quoting
real historical music. Small instruments only: ukulele (nylon pluck, high), bassoon, clarinet, toy piano, recorder,
woodblock, music box, glockenspiel. Each chapter ends with a comedy button just after its punchline line; chapter 10
returns to the opening arrangement in full.  Run: .venv/bin/python films/manscaped-trimming-through-the-ages/music/score.py
→ music/stems/*.wav (one per instrument) and music/score.wav
"""
import sys, os, json
import numpy as np, soundfile as sf
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '../../..'))
sys.path.insert(0, ROOT)
from core.audio import sampler as S, pluck as P
from core.audio.sfx import SR, add, bp, lp

S.seed(17)
E = json.load(open(os.path.join(HERE, '..', 'events.json')))
DUR = E['dur']; N = int((DUR + 4) * SR)
CUES = [e for e in E['ev'] if e['type'] == 'cue']
VOICE = [e for e in E['ev'] if e['type'] == 'voice']
rng = np.random.default_rng(23)
ST = {k: np.zeros((N, 2), np.float32) for k in ['uke', 'bassoon', 'clarinet', 'toypiano', 'recorder', 'woodblock', 'musicbox', 'glock']}
m = S.midi

def toy(p, vel=.6):
    f0 = 440 * 2 ** ((p - 69) / 12) * 2 ** (rng.uniform(-8, 8) / 1200); d = 1.3; t = np.arange(int(d * SR)) / SR; y = np.zeros_like(t)
    for r, a, t60 in [(1, 1.0, .9), (2.92, .4, .32), (5.84, .18, .15), (1.004, .3, .8)]:
        if f0 * r < 18000: y += a * np.sin(2 * np.pi * f0 * r * t + rng.random() * 6) * np.exp(-6.9 * t / t60)
    L = int(.01 * SR); y[:L] += bp(rng.standard_normal(L) * np.exp(-np.arange(L) / (.0012 * SR)), 1500, 6000) * .5 * vel
    y = lp(y, 7000); y[:48] *= np.linspace(0, 1, 48); y[-480:] *= np.linspace(1, 0, 480)
    return (y * .1 * (vel / .8) ** 1.3 / (np.sqrt(np.mean(y[:int(.1 * SR)] ** 2)) + 1e-9)).astype(np.float32)
def put(st, x, t, g=1.0, pan=0.0): add(ST[st], x, t, g, pan)
def note(st, inst, t, p, d, v=.5, pan=0., g=1., att=.03, rel=.2): put(st, S.note(inst, p, d, v, attack=att, release=rel), t, g, pan)
def uke(t, ps, v=.45, pan=-.3): put('uke', P.strum('nylon_guitar', [p + 12 for p in ps], .9, v, spread=.016), t, 0.9, pan)
def pl(t, p, v=.5, pan=-.3): put('uke', P.pluck('nylon_guitar', p + 12, .8, v), t, 0.9, pan)
def mbox(t, p, v=.5, pan=.15): put('musicbox', P.pluck('music_box', p, None, v), t, 1.0, pan)
def toyp(t, p, v=.55, pan=-.1): put('toypiano', toy(p, v), t, 1.0, pan)
def glock(t, p, v=.45, pan=.3): note('glock', 'glockenspiel', t, p, 1.4, v, pan, .8, 0, 1.2)
def wood(t, v=.6, pan=.2, k='a'):
    try: put('woodblock', S.note('woodblock', k, .3, v), t, 1.0, pan)
    except Exception:
        tt = np.arange(int(.12 * SR)) / SR; put('woodblock', (np.sin(2 * np.pi * 1100 * tt) * np.exp(-tt / .018) * .4 * v).astype(np.float32), t, 1.0, pan)

# —— the motif: (scale degree as midi in C, beat offset, length in beats) — 2 bars of 4/4 ——
MOTIF = [(76, 0, .5), (79, .5, .5), (76, 1, .5), (72, 1.5, .5), (74, 2, 1), (67, 3, 1), (69, 4, .5), (72, 4.5, .5), (71, 5, .5), (67, 5.5, .5), (72, 6, 2)]
def motif(t0, fn, beat, tr=0, mode=None):
    for p, b, d in MOTIF:
        q = p + tr
        if mode == 'phryg' and (q % 12) in (2,): q -= 1          # flat 2nd (Egypt)
        if mode == 'dorian' and (q % 12) in (4, 9): q -= 1        # minor 3rd and 6th (Greece)
        if mode == 'minor' and (q % 12) in (4, 9, 11): q -= 1
        fn(t0 + b * beat, q, d * beat)
# chords per bar (root midi, triad) in C
PROG = [(48, [60, 64, 67]), (53, [60, 65, 69]), (55, [59, 62, 67]), (48, [60, 64, 67])]

def section(ci, t0, t1, punch):
    B = 60 / [84, 88, 92, 104, 96, 100, 108, 112, 90, 96][ci]
    meter = 3 if ci in (5, 6) else 4; BAR = meter * B; nb = int((t1 - t0) / BAR)
    vs = [(e['t'], e['t'] + e['d']) for e in VOICE if t0 - 1 <= e['t'] < t1]
    under = lambda t: any(a - .2 < t < b + .2 for a, b in vs)
    for j in range(nb):
        tb = t0 + j * BAR; root, tri = PROG[j % 4]; q = .7 if under(tb + BAR / 2) else 1.0
        if ci == 0:     # prehistoric: woodblock heartbeat, bassoon grunts
            for k in range(meter): wood(tb + k * B, (.7 if k == 0 else .4) * q, -.2, 'a' if k % 2 == 0 else 'b')
            note('bassoon', 'bassoon_stac', tb, root - 12, B * .8, .55 * q, -.1)
            note('bassoon', 'bassoon_stac', tb + 2.5 * B, root - 5, B * .6, .45 * q, -.1)
        elif ci == 1:   # Egypt: recorder over a bassoon drone, gentle woodblock
            if j % 2 == 0: note('bassoon', 'bassoon', tb, 50 - 12, BAR * 2, .32 * q, -.2, .9, .3, .5)
            for k in (0, 1.5, 3): wood(tb + k * B, .35 * q, .3, 'c')
        elif ci == 2:   # Greece: ukulele arpeggios
            for k in range(8): pl(tb + k * B / 2, [tri[0], tri[1], tri[2], tri[1]][k % 4] - 12 + 12 * (k == 7), .4 * q)
        elif ci == 3:   # Rome: a little march, bassoon + clarinet staccato + woodblock snare
            note('bassoon', 'bassoon_stac', tb, root - 12, B * .7, .6 * q, -.2); note('bassoon', 'bassoon_stac', tb + 2 * B, root - 5, B * .7, .5 * q, -.2)
            for k in (1, 3): [note('clarinet', 'clarinet_stac', tb + k * B, p, B * .4, .35 * q, .2) for p in tri[1:]]
            for k in range(8): wood(tb + k * B / 2, (.5 if k % 2 == 0 else .25) * q, .3, 'b')
        elif ci == 4:   # medieval: drone fifths, recorder dances
            if j % 2 == 0: note('bassoon', 'bassoon', tb, 48 - 12, BAR * 2, .3 * q, -.2, .9, .3, .5); note('clarinet', 'clarinet', tb, 55, BAR * 2, .2 * q, .2, .8, .4, .5)
            wood(tb, .4 * q, .1, 'a'); wood(tb + 2.5 * B, .3 * q, .1, 'c')
        elif ci == 5:   # Renaissance: 3/4, ukulele strums + recorder
            uke(tb, tri, .42 * q); uke(tb + B, tri, .28 * q); uke(tb + 2 * B, tri, .3 * q)
            note('bassoon', 'bassoon_stac', tb, root - 12, B * .8, .45 * q, -.2)
        elif ci == 6:   # Victorian: music-box waltz
            mbox(tb, root + 12, .45 * q, -.2); [mbox(tb + k * B, p + 12, .3 * q, .2) for k in (1, 2) for p in tri[1:]]
        elif ci == 7:   # electric age: clarinet swing + toy piano comps
            note('bassoon', 'bassoon_stac', tb, root - 12, B * .7, .5 * q, -.2); note('bassoon', 'bassoon_stac', tb + 2 * B, root - 5, B * .7, .4 * q, -.2)
            for k in (1, 3): [toyp(tb + k * B + .18 * B, p, .32 * q, -.1) for p in tri[1:]]
            wood(tb + B, .3 * q, .4, 'b'); wood(tb + 3 * B, .3 * q, .4, 'b')
        elif ci == 8:   # space: glockenspiel and music-box sparkle, slow
            for k in range(8): mbox(tb + k * B / 2, tri[k % 3] + 24 - 12 * (k % 2), .22 * q, -.4 + .1 * k)
            if j % 2 == 0: note('clarinet', 'clarinet', tb, root, BAR * 2, .2 * q, -.2, .8, .5, .6)
        elif ci == 9:   # modern: the opening woodblock returns under everything
            for k in range(meter): wood(tb + k * B, (.5 if k == 0 else .3) * q, -.2, 'a' if k % 2 == 0 else 'b')
            uke(tb, tri, .38 * q); uke(tb + 2 * B, tri, .3 * q); note('bassoon', 'bassoon_stac', tb, root - 12, B * .8, .5 * q, -.2)
    # the motif: once before the first line (the "opening") and once after the chapter's last line if there is room
    first = min([a for a, b in vs] or [t1]); last = max([b for a, b in vs] or [t0])
    lead = {0: ('bassoon', -12, None), 1: ('recorder', 0, 'phryg'), 2: ('recorder', 0, 'dorian'), 3: ('clarinet', -12, None), 4: ('recorder', 0, 'minor'), 5: ('recorder', 0, None),
            6: ('musicbox', 12, None), 7: ('clarinet', 0, None), 8: ('glock', 12, None), 9: ('toypiano', 0, None)}[ci]
    def play(st, tr, mode, ts, v):
        if st == 'musicbox': motif(ts, lambda t, p, d: mbox(t, p, v), B, tr, mode)
        elif st == 'glock': motif(ts, lambda t, p, d: glock(t, p, v * .9), B, tr, mode)
        elif st == 'toypiano': motif(ts, lambda t, p, d: toyp(t, p, v), B, tr, mode)
        elif st == 'bassoon': motif(ts, lambda t, p, d: note('bassoon', 'bassoon', t, p, d + .05, v, -.1, 1, .03, .2), B, tr, mode)
        else: inst = 'recorder' if st == 'recorder' else 'clarinet'; motif(ts, lambda t, p, d: note(st, inst, t, p, d + .05, v, .15, 1, .03, .2), B, tr, mode)
    if first - t0 > 2.5: play(*lead, t0 + .2, .55)
    if ci == 9:   # finale: the motif in full, everyone, after the last line
        play('toypiano', 0, None, t1 - 8 * B - 1.4, .55); play('glock', 12, None, t1 - 8 * B - 1.4, .4); play('recorder', 0, None, t1 - 8 * B - 1.4, .4)
    # comedy button right after the punchline
    pt = punch + .25
    if ci == 9:
        for k, p in enumerate([60, 64, 67, 72]): toyp(t1 - .9 + k * .03, p, .6); glock(t1 - .8, 84, .5); wood(t1 - .9, .7)
    else:
        kind = ci % 3
        if kind == 0: note('bassoon', 'bassoon_stac', pt, 43, .25, .7, 0); note('bassoon', 'bassoon_stac', pt + .32, 36, .5, .75, 0)   # bwomp-bwomp
        elif kind == 1: wood(pt, .8, 0, 'a'); wood(pt + .18, .6, 0, 'b'); glock(pt + .4, 91, .45, 0)                               # tock-tock-ding
        else: note('clarinet', 'clarinet', pt, 67, .5, .5, 0, 1, .02, .3); note('clarinet', 'clarinet', pt + .45, 61, .9, .5, 0, 1, .02, .5)   # a wry little fall

for i, cu in enumerate(CUES):
    t0 = cu['t'] + (1.0 if i else 0.3); t1 = cu['t'] + 30 - .15
    punch = max([e['t'] + e['d'] for e in VOICE if cu['t'] <= e['t'] < cu['t'] + 30] or [t1 - 2])
    section(i, t0, t1, punch)

os.makedirs(os.path.join(HERE, 'stems'), exist_ok=True)
for k, x in ST.items(): sf.write(os.path.join(HERE, 'stems', k + '.wav'), x[:int(DUR * SR)], SR)
mix = sum(ST.values())[:int(DUR * SR)]
sf.write(os.path.join(HERE, 'score.wav'), (mix / (np.abs(mix).max() + 1e-9) * .8).astype(np.float32), SR)
print('score', round(DUR, 2), 's; peak', round(float(np.abs(mix).max()), 3))
