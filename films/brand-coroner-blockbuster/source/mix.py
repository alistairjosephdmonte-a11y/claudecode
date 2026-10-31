"""Mix for Brand Coroner, Case 001: narration on the timeline, tactile procedural Foley per shot, the score ducked under
the voice. → out/mix.wav and out/stems/{narration,foley,music}.wav, plus voice timing in out/tl.json and subs.srt."""
import sys, os, json
import numpy as np, soundfile as sf
H = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(H, '../..')); sys.path.insert(0, ROOT)
from core.audio.sfx import SR, add, bp, lp, hp, noise, brown, norm, step, thump, compress, limit
rng = np.random.default_rng(11)
DUR = 480.0; N = int(DUR * SR)
ST = json.load(open(f'{H}/story.json'))['shots']; VD = json.load(open(f'{H}/voice.json'))
FO, VO = np.zeros((N, 2), np.float32), np.zeros((N, 2), np.float32)
put = lambda x, t, g=1., pan=0.: add(FO, np.asarray(x, np.float32), t, g, pan)
tt = lambda d: np.arange(int(d * SR)) / SR
def fade(x, a=.3, b=.3): n = len(x); x = x.copy(); x[:int(a * SR)] *= np.linspace(0, 1, int(a * SR)); x[n - int(b * SR):] *= np.linspace(1, 0, int(b * SR)); return x

# —— Foley vocabulary ——
def room(d, g=.012): return fade(lp(brown(d), 300) * g + hp(noise(d), 4000) * g * .05, 1, 1)          # quiet table room tone
def vent(d, g=.02): return fade(bp(brown(d), 80, 900) * g, 1, 1)                                         # office ventilation
def city(d, g=.03): return fade(lp(brown(d), 500) * g + bp(noise(d), 300, 2000) * g * .15, 1.5, 1.5)    # distant morning traffic
def hum(d, f=120, g=.006): x = tt(d); return fade((np.sin(2 * np.pi * f * x) + .4 * np.sin(2 * np.pi * 2 * f * x)) * g + bp(noise(d), 2000, 6000) * g * .4, .4, .4)
def paper(d=.6, g=.25):   # a sheet sliding over wood: band-passed noise with a swell, fibre crackle
    x = bp(noise(d), 900, 6000) * np.sin(np.pi * np.minimum(1, tt(d) / d)) ** 1.5; cr = (rng.random(len(x)) < .002) * rng.standard_normal(len(x)) * 3
    return (x + bp(cr, 2000, 8000)) * g
def tap(g=.3): x = tt(.08); return (bp(noise(.08), 300, 2500) * np.exp(-x / .01) + np.sin(2 * np.pi * 160 * x) * np.exp(-x / .02) * .6) * g
def plastic(g=.3): x = tt(.12); return (hp(noise(.12), 1500) * np.exp(-x / .006) + sum(np.sin(2 * np.pi * f * x) * np.exp(-x / .02) for f in (1900, 3100, 4700)) * .3) * g
def slide(d=1., g=.2): return bp(noise(d), 1200, 7000) * np.sin(np.pi * tt(d) / d) * g
def beep(g=.08): x = tt(.12); return np.sin(2 * np.pi * 2100 * x) * np.minimum(1, (.12 - x) / .02) * g
def printer(d=1.2, g=.05): x = tt(d); return bp(noise(d), 800, 5000) * (np.sin(2 * np.pi * 38 * x) > .2) * g
def rise(d=2., g=.06): x = tt(d); f = 70 + 50 * x / d; return fade(lp(bp(noise(d), 80, 1200) * (1 + .5 * np.sin(2 * np.pi * np.cumsum(f) / SR)), 900) * g, .2, .4)
def conveyor(d, g=.05): x = tt(d); r = (rng.random(len(x)) < .0008) * rng.standard_normal(len(x)); return fade(lp(brown(d), 200) * g + bp(r, 1500, 6000) * g * 4 + np.sin(2 * np.pi * 50 * x) * g * .2, .8, .8)
def typing(d, g=.12):
    y = np.zeros(int(d * SR)); t = .2
    while t < d - .1: add1 = plastic(g * rng.uniform(.4, .9)); i = int(t * SR); y[i:i + len(add1)] += add1[:len(y) - i]; t += rng.uniform(.08, .28)
    return y
def click(g=.15): return plastic(g) * .6
def gears(d, g=.08):
    y = np.zeros(int(d * SR)); t = .1
    while t < d: c = plastic(g * .7); i = int(t * SR); y[i:i + len(c)] += c[:len(y) - i]; t += .18
    return y + lp(brown(d), 150) * g * .3
def relay(g=.08): x = tt(.05); return hp(noise(.05), 3000) * np.exp(-x / .003) * g
def buzz(d, g=.01): x = tt(d); return fade((np.sign(np.sin(2 * np.pi * 120 * x)) * .5 + np.sin(2 * np.pi * 240 * x)) * g, .3, .3)
def grind(d, g=.05): return fade(lp(brown(d), 400) * g + bp(noise(d), 200, 1500) * g * .5, .3, .5)
def whoosh(d=1.2, g=.05): x = tt(d); return bp(noise(d), 300, 3000) * np.sin(np.pi * x / d) ** 2 * g
def steps(t0, d, rate=1.8, g=.18, pan=0.):
    t = t0
    while t < t0 + d: put(step(g * rng.uniform(.7, 1)), t, 1., pan + rng.uniform(-.1, .1)); t += 1 / rate * rng.uniform(.9, 1.1)

# —— per-shot cues: (offset s, sound, gain, pan) ——
def cue(n, s0):
    T = lambda o: s0 + o
    beds = {0: city(10), 1: city(10, .02), 2: vent(10), 3: vent(10, .012), 8: city(10, .02), 9: hum(10) + vent(10, .01), 10: hum(10) + vent(10, .01), 17: conveyor(10), 19: conveyor(10, .03) + hum(10, g=.004),
            21: hum(10, 60, .01) + vent(10, .008), 25: conveyor(10, .02), 30: hum(10) + vent(10, .01), 33: gears(10), 35: hum(10, 60, .008), 41: buzz(10) + hum(10, g=.004)}
    put(beds.get(n, room(10)), T(0), 1.)
    if n == 1: steps(T(.2), 9.6, 2.0, .16)
    if n == 3: put(slide(2.2, .1), T(1.2)); put(tap(.15), T(3.3))
    if n in (4, 5, 7, 24, 26, 27, 29, 34, 40): put(paper(.7, .2), T(.15), 1., -.2)
    if n == 6: put(thump(.25, 55), T(.4)); put(paper(.5, .1), T(.3))
    if n == 8: steps(T(.5), 9, 1.6, .1, .3)
    if n == 9: steps(T(.5), 9, 1.2, .06, -.2)
    if n == 10: put(slide(2, .12), T(1.2)); put(tap(.2), T(3.6)); put(beep(), T(6.4)); put(printer(1.4), T(7.0), 1., .3)
    if n == 11: put(rise(2.8), T(.4)); [put(click(.04), T(4 + k * .12), 1., rng.uniform(-.5, .5)) for k in range(50)]
    if n == 12: [put(click(.025), T(k * .09), 1., rng.uniform(-.7, .7)) for k in range(90)]
    if n == 13: put(paper(1.2, .15), T(.3))
    if n == 14: put(rise(3.2), T(.8)); put(rise(1.8, .04), T(3.2)); put(paper(.6, .1), T(5))
    if n == 15: put(grind(10, .03), T(0)); put(whoosh(2, .03), T(4))
    if n == 16: put(slide(4.5, .12), T(1.5)); put(tap(.12), T(6))
    if n == 18: [put(tap(.18), T(.4 + k * 2.5)) for k in range(4)]; put(slide(9, .03), T(.5))
    if n == 20: [put(thump(.22, 70), T(1.6 + i * 1.1)) for i in range(4)]; [put(thump(.2, 80), T(1.9 + i * 1.1), 1., .3) for i in range(4)]
    if n == 21: put(typing(4, .08), T(1.5)); [put(click(.12), T(o)) for o in (6.2, 7.5, 8.8)]
    if n == 22: put(whoosh(3, .03), T(4))
    if n == 23: put(whoosh(6, .025), T(2))
    if n == 25: [put(paper(.3, .05), T(o), 1., .4) for o in np.arange(.5, 10, .7)]
    if n == 28: put(rise(2.5), T(.5)); put(rise(1.5, .04), T(3.5))
    if n == 30: put(slide(2.4, .1), T(1)); put(plastic(.2), T(3.4)); put(slide(2.4, .1), T(5.2)); put(plastic(.25), T(7.6))
    if n == 31: put(rise(2.1), T(.5)); put(rise(2, .05), T(2.6)); [put(thump(.15, 90), T(5.6 + i * .7)) for i in range(6)]
    if n == 32: put(rise(3, .05), T(.2)); put(grind(3, .04), T(2))
    if n == 37: [put(paper(.5, .15), T(1.8 + i * 1.4)) for i in range(5)]
    if n == 38: [put(thump(.5, 45), T(2.6 + i * 1.2)) for i in range(3)]; [put(grind(1.2, .03), T(1 + i * 1.2)) for i in range(3)]
    if n == 39: [put(relay(.08), T(.8 + h * 8.5), 1., rng.uniform(-.8, .8)) for h in rng.random(140)]
    if n == 41: [put(relay(.05), T(k / 9)) for k in range(90) if (np.sin(k * 127.1 + 311.7) * 43758.5453) % 1 > .78]
    if n == 43: [put(paper(.9, .07), T(1 + i * 1.2)) for i in range(6)]
    if n == 44: put(grind(5.5, .05), T(.5)); put(thump(.35, 50), T(6))
    if n == 45: put(whoosh(9, .03), T(.5))
for n in range(46): cue(n, n * 10)
put(fade(lp(brown(9), 200) * .015, 1, 6), 470.5)   # closing low air under the end card

# —— narration: same placement solver as the picture (main.js) ——
TL = []; prev = -1
for i, s in enumerate(ST):
    d = VD[s['id']]; b0 = i * 10; lead = 1.6 if i == 0 else .9 if i % 8 == 0 else .45
    t0 = max(b0 + lead, prev + .45)
    if i == 46: t0 = max(t0, b0 + 2.2)
    if i == 47: t0 = max(t0, b0 + 3.6)
    prev = t0 + d; TL.append({'id': s['id'], 't': round(t0, 3), 'd': d, 'end': round(t0 + d, 3), 'shot_end': b0 + 10, 'text': s['line']})
    y, sr = sf.read(f"{H}/out/voice/{s['id']}.wav"); add(VO, y.astype(np.float32), t0, 1., 0.)
json.dump(TL, open(f'{H}/out/tl.json', 'w'), indent=1)
over = [(l['id'], round(l['end'] - l['shot_end'], 2)) for l in TL if l['end'] > l['shot_end'] + .01]
print('lines past their shot:', over)

def srt_t(x): h, r = divmod(x, 3600); m, s = divmod(r, 60); return f'{int(h):02d}:{int(m):02d}:{int(s):02d},{int(round((s % 1) * 1000)):03d}'.replace(',1000', ',999')
with open(f'{H}/subs.srt', 'w') as f:
    for k, l in enumerate(TL): f.write(f"{k + 1}\n{srt_t(l['t'])} --> {srt_t(l['end'] + .2)}\n{l['text']}\n\n")

# —— balance: duck music and Foley under the voice ——
MU, sr = sf.read(f'{H}/music/score.wav'); MU = MU[:N].astype(np.float32); MU = np.pad(MU, ((0, N - len(MU)), (0, 0)))
env = np.abs(VO.mean(1)); k = int(.25 * SR); env = np.convolve(env, np.ones(k) / k, 'same'); act = np.clip(env / (env.max() * .08), 0, 1)
k2 = int(.5 * SR); act = np.convolve(act, np.ones(k2) / k2, 'same')
duckM = 10 ** (-9 * act / 20); duckF = 10 ** (-4 * act / 20)
vo = VO * 1.0; mu = MU * .55 * duckM[:, None]; fo = FO * 1.0 * duckF[:, None]
def lvl(x): return 20 * np.log10(np.sqrt(np.mean(x ** 2)) + 1e-9)
print('levels dB: voice', round(lvl(vo[vo.any(1)]), 1), 'music', round(lvl(mu), 1), 'foley', round(lvl(fo), 1))
os.makedirs(f'{H}/out/stems', exist_ok=True)
for nm, x in [('narration', vo), ('foley', fo), ('music', mu)]: sf.write(f'{H}/out/stems/{nm}.wav', x, SR)
mix = vo + mu + fo; mix = limit(mix / max(1e-9, np.abs(mix).max()) * .9); sf.write(f'{H}/out/mix.wav', mix, SR); print('mix', round(len(mix) / SR, 2), 's')
