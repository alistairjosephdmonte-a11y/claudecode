"""Original score for "The Thirty-Five Dollar Squiggle": a 3/4 storybook waltz in C, 84 BPM, one section per page.
Small instruments only: music box, toy piano, kalimba, ukulele (nylon pluck, high), clarinet, flute, glockenspiel.
Sections start on each page turn (events.json 'cue'); the theme is played in the gap before narration and at the end.
Run: .venv/bin/python films/swoosh-crayon/music/score.py → music/stems/*.wav
"""
import sys, os, json
import numpy as np, soundfile as sf
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '../../..'))
sys.path.insert(0, ROOT)
from core.audio import sampler as S, pluck as P
from core.audio.sfx import SR, add, bp, lp

S.seed(5)
E = json.load(open(os.path.join(HERE, '..', 'events.json')))
DUR = E['dur']; N = int((DUR + 3) * SR)
CUES = [e for e in E['ev'] if e['type'] == 'cue']
VOICE = [(e['t'], e['t'] + e['d']) for e in E['ev'] if e['type'] == 'voice']
B = 60 / 84; BAR = 3 * B
rng = np.random.default_rng(3)
stems = {k: np.zeros((N, 2), np.float32) for k in ['musicbox', 'toypiano', 'kalimba', 'uke', 'clarinet', 'flute', 'glock']}
m = S.midi

def toy(p, vel=.6):
    f0 = 440 * 2 ** ((p - 69) / 12) * 2 ** (rng.uniform(-8, 8) / 1200)
    d = 1.4; t = np.arange(int(d * SR)) / SR; y = np.zeros_like(t)
    for r, a, t60 in [(1, 1.0, 1.0), (2.92, .4, .35), (5.84, .18, .16), (1.004, .3, .9)]:
        if f0 * r < 18000: y += a * np.sin(2 * np.pi * f0 * r * t + rng.random() * 6) * np.exp(-6.9 * t / t60)
    L = int(.01 * SR); y[:L] += bp(rng.standard_normal(L) * np.exp(-np.arange(L) / (.0012 * SR)), 1500, 6000) * .5 * vel
    y = lp(y, 7000); y[:48] *= np.linspace(0, 1, 48); y[-480:] *= np.linspace(1, 0, 480)
    return (y * .1 * (vel / .8) ** 1.3 / (np.sqrt(np.mean(y[:int(.1 * SR)] ** 2)) + 1e-9)).astype(np.float32)
def mbox(t, p, vel=.55, pan=.1, g=1.0): add(stems['musicbox'], P.pluck('music_box', p, None, vel), t, g, pan)
def toyp(t, p, vel=.55, pan=-.15, g=1.0): add(stems['toypiano'], toy(p, vel), t, g, pan)
def kal(t, p, vel=.5, pan=.25, g=1.0): add(stems['kalimba'], S.note('kalimba', p, 1.2, vel), t, g, pan)
def uke(t, ps, vel=.5, pan=-.3, g=1.0): add(stems['uke'], P.strum('nylon_guitar', ps, 1.0, vel, spread=.018), t, g, pan)
def sus(st, inst, t, p, d, vel=.4, pan=0., g=1.0, att=.08, rel=.4): add(stems[st], S.note(inst, p, d, vel, attack=att, release=rel), t, g, pan)
def glock(t, p, vel=.45, pan=.3, g=.8): add(stems['glock'], S.note('glockenspiel', p, 1.5, vel), t, g, pan)

# chords as (bass, triad) midi; progressions per mood
C = {'I': (48, [60, 64, 67]), 'IV': (53, [60, 65, 69]), 'V': (55, [59, 62, 67]), 'vi': (57, [60, 64, 69]), 'ii': (50, [60, 62, 65]), 'iii': (52, [59, 64, 67]), 'V7': (55, [59, 65, 67])}
PROG = {'bright': ['I', 'IV', 'V', 'I'], 'soft': ['I', 'vi', 'IV', 'V'], 'dream': ['IV', 'iii', 'ii', 'V'], 'warm': ['vi', 'IV', 'I', 'V']}
# the theme: 4 bars of 3/4 over I IV V I, in (degree-midi, beat, length)
THEME = [[(64, 0, .5), (67, .5, .5), (72, 1, 1.5), (71, 2.5, .5)], [(69, 0, 1), (72, 1, .5), (69, 1.5, .5), (65, 2, 1)],
         [(67, 0, .5), (71, .5, .5), (74, 1, 1.5), (72, 2.5, .5)], [(72, 0, 3)]]
def theme(t0, fn, bars=4, tr=0):
    for b in range(bars):
        for p, bt, d in THEME[b]: fn(t0 + b * BAR + bt * B, p + tr, d * B)

SECT = {   # page id → (progression, bed, melody voice)
    'title': ('bright', 'mbox', 'mbox'), 'brs': ('bright', 'uke', 'toy'), 'campus': ('soft', 'kal', 'flute'), 'brief': ('bright', 'toy', 'clar'),
    'tissue': ('soft', 'mboxfast', 'mbox'), 'pitch': ('warm', 'toy', 'flute'), 'invoice': ('bright', 'toy', 'toy'), 'name': ('dream', 'kal', 'flute'),
    'track': ('bright', 'uke', 'toy'), 'gift': ('warm', 'kal', 'flute'), 'word': ('soft', 'mbox', 'mbox'), 'meaning': ('soft', 'full', 'flute'), 'end': ('bright', 'mbox', 'mbox'),
}
def melody(kind, t0, bars=4, tr=12):
    if kind == 'mbox': theme(t0, lambda t, p, d: mbox(t, p + tr, .6, .15), bars)
    elif kind == 'toy': theme(t0, lambda t, p, d: toyp(t, p + tr - 12 + 12, .62, .1), bars)
    elif kind == 'flute': theme(t0, lambda t, p, d: sus('flute', 'flute', t, p + tr - 12 + 12, d + .05, .42, .15, .9, .05, .3), bars)
    elif kind == 'clar': theme(t0, lambda t, p, d: sus('clarinet', 'clarinet', t, p + tr - 24, d + .05, .45, -.1, .9, .04, .25), bars)

for i, cu in enumerate(CUES):
    pid = cu['id']; t0 = cu['t'] + (1.1 if i else 0.0); t1 = cu['t'] + cu['dur'] - 0.2
    prog, bed, mel = SECT[pid]; PR = PROG[prog]
    glock(cu['t'] + (0.9 if i else 0.2), 84, .5, .3)                                # a little bell as the page lands
    nb = int((t1 - t0) / BAR)
    vstart = min([a for a, b in VOICE if a >= cu['t']] or [t1])
    for j in range(nb):
        tb = t0 + j * BAR; bass, tri = C[PR[j % 4]]
        quiet = .75 if any(a - .3 < tb + BAR and b > tb for a, b in VOICE) else 1.0
        if pid == 'end' and j >= 3: break
        if bed in ('mbox', 'full'):
            for k, p in enumerate([bass + 12, tri[0] + 12, tri[1] + 12, tri[2] + 12, tri[1] + 12, tri[0] + 12]): mbox(tb + k * B / 2, p, .32 * quiet, -.25 + .1 * k, .7)
        if bed == 'mboxfast':
            for k in range(12): mbox(tb + k * B / 4, tri[k % 3] + 12 + (12 if k % 4 == 3 else 0), .26 * quiet, -.3 + .05 * k, .6)
        if bed in ('toy', 'full'):
            toyp(tb, bass + 12, .5 * quiet, -.2); [toyp(tb + k * B, p, .3 * quiet, -.05, .8) for k in (1, 2) for p in tri[1:]]
        if bed == 'kal':
            for k, p in enumerate([bass + 12, tri[0] + 12, tri[2] + 12, tri[1] + 12, tri[2] + 12, tri[0] + 24]): kal(tb + k * B / 2, p, .4 * quiet, .2)
        if bed == 'uke':
            uke(tb, [p + 12 for p in tri], .45 * quiet); uke(tb + B, [p + 12 for p in tri], .3 * quiet); uke(tb + 2 * B, [p + 12 for p in tri], .32 * quiet)
        if bed != 'mboxfast' and j % 2 == 0: sus('clarinet', 'clarinet', tb, bass, BAR * 2 - .1, .26 * quiet, -.2, .8, .3, .5)
        if bed == 'full': sus('flute', 'flute', tb, tri[2] + 12, BAR - .1, .2, .3, .6, .4, .4)
    # the theme: before the narration starts, and again in the page's last bars if there is room
    if vstart - t0 > 2 * BAR - .2: melody(mel, t0, 2 if vstart - t0 < 4 * BAR else 4)
    elif i == 0: melody(mel, t0, 2)
    last = max([b for a, b in VOICE if cu['t'] <= a < cu['t'] + cu['dur']] or [t0])
    if pid != 'end' and t1 - last > 1.5 * BAR: melody(mel, last + .3, 2, 12)
    if pid == 'pitch':   # "I don't love it": the clarinet sags
        vs = [a for a, b in VOICE if cu['t'] <= a < cu['t'] + cu['dur']]
        if len(vs) >= 4: sus('clarinet', 'clarinet_stac', vs[3] - .4, 55, .3, .5, 0, 1); sus('clarinet', 'clarinet_stac', vs[3] - .1, 54, .4, .45, 0, 1)
    if pid == 'end':   # the last chord, on the music box, and a bell
        te = t0 + 3 * BAR
        for k, p in enumerate([60, 64, 67, 72, 76]): mbox(te + k * .06, p + 12, .5, -.2 + .1 * k, .9)
        sus('clarinet', 'clarinet', te, 48, 3.0, .3, -.2, .8, .2, 1.0); glock(te + .4, 96, .4)

os.makedirs(os.path.join(HERE, 'stems'), exist_ok=True)
for k, x in stems.items(): sf.write(os.path.join(HERE, 'stems', k + '.wav'), x[:int(DUR * SR)], SR)
mix = sum(stems.values())[:int(DUR * SR)]
sf.write(os.path.join(HERE, 'score.wav'), (mix / (np.abs(mix).max() + 1e-9) * .8).astype(np.float32), SR)
print('score', round(DUR, 1), 's, peak', round(float(np.abs(mix).max()), 2))
