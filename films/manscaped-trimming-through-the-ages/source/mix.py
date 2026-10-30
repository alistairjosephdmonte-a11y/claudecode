# 混音：原创配乐（music/score.wav）+ 材质拟音（蜡笔刮纸、湿刷子、毡子、纸页）+ 夜晚底噪 + 旁白 → mix.wav
# Trimming Through the Ages: score stems + crayon/paper/period foley + narration → out/{narration,foley,music,mix}.wav
# usage: .venv/bin/python films/manscaped-trimming-through-the-ages/mix.py
import sys, os, json, numpy as np, soundfile as sf, soxr
from scipy.ndimage import uniform_filter1d
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '../../core/audio'))
from sfx import *

E = json.load(open(os.path.join(HERE, 'events.json'))); DUR = E['dur']; EV = E['ev']; N = int(DUR * SR)
tt = np.arange(N) / SR
rng = np.random.default_rng(12)
def nz(d): return rng.standard_normal(int(round(d * SR)))
def T(d): return np.arange(int(round(d * SR))) / SR
def fade(x, a=.01, b=.03):
    n = len(x); ia, ib = min(n, int(a * SR)), min(n, int(b * SR))
    if ia: x[:ia] *= np.linspace(0, 1, ia)
    if ib: x[-ib:] *= np.linspace(1, 0, ib)
    return x
def envelope(d, pts):
    k = np.array(pts, float); return np.interp(T(d), k[:, 0] * d, k[:, 1])

# ——— 蜡笔刮纸：粘滑摩擦 = 带通噪声 × 不规则颗粒调制；speed 越快颗粒越密、越亮 ———
def crayon(d, speed=1.0, v=1.0):
    n = nz(d); g = np.abs(rng.standard_normal(len(n)))
    rate = int(SR / (70 + 90 * speed))
    grain = uniform_filter1d((rng.random(len(n) // rate + 2) ** 3).repeat(rate)[:len(n)], rate // 3 + 1)
    x = bp(n, 1400 + 600 * speed, 6500, 2) * (0.35 + grain * 1.6) + bp(n, 300, 900, 1) * 0.15
    return fade(x * envelope(d, [(0, 0), (.08, 1), (.85, .9), (1, 0)]) * v * 0.22, .01, .04)
# 涂色：来回排线 = 每一趟一个短刮擦
def scribble(d, rate=6.5, v=1.0):
    out = np.zeros(int(d * SR)); k = 0; t = 0.0
    while t < d - 0.08:
        L = 1 / rate * (0.8 + 0.4 * rng.random()); s = crayon(min(L, d - t), 1.3, v * (0.7 + 0.3 * rng.random()))
        i = int(t * SR); out[i:i + len(s)] += s[:len(out) - i]; t += L; k += 1
    return out
def write(d, v=1.0):   # 写字：一小簇一小簇
    out = np.zeros(int(d * SR)); t = 0.0
    while t < d - 0.1:
        L = 0.07 + 0.1 * rng.random(); s = crayon(L, 0.8, v); i = int(t * SR); out[i:i + len(s)] += s[:len(out) - i]; t += L + 0.03 * rng.random()
    return out
def paper_rustle(d=0.6, v=1.0):
    n = nz(d); cr = (rng.random(len(n)) < 0.004) * rng.standard_normal(len(n)) * 3
    return fade((hp(n, 900) * 0.25 + bp(cr, 1500, 8000)) * envelope(d, [(0, 0), (.2, 1), (1, 0)]) * v * 0.25)
def blink(v=1.0):
    t = T(0.09); return fade(np.sin(2 * np.pi * (1500 - 5000 * t) * t) * np.exp(-t / 0.02) * 0.25 * v, .001, .02)
def swish(d=0.4, v=1.0):   # 被子嗖声
    n = nz(d); e = np.sin(np.linspace(0, np.pi, len(n))) ** 2
    return lp(bp(n, 250, 2500), 2200) * e * 0.35 * v
def felt(v=1.0):   # 羊落地：毡子噗
    t = T(0.22); return fade((np.sin(2 * np.pi * 105 * t) * np.exp(-t / 0.05) * 0.7 + lp(nz(0.22), 600) * np.exp(-t / 0.03) * 0.5) * v * 0.45)
def baa(v=1.0, f0=430):
    d = 0.42; t = T(d); f = f0 * (1 + 0.02 * np.sin(2 * np.pi * 7 * t)) * (1 - 0.08 * t / d)
    ph = 2 * np.pi * np.cumsum(f) / SR; saw = 2 * ((ph / (2 * np.pi)) % 1) - 1
    x = bp(saw, 600, 1100) * 1.0 + bp(saw, 1900, 2600) * 0.5
    trem = 1 + 0.5 * np.sin(2 * np.pi * 18 * t)
    return fade(x * trem * envelope(d, [(0, 0), (.1, 1), (.7, .8), (1, 0)]) * 0.12 * v, .02, .08)
def cricket(d=1.2, v=1.0):
    out = np.zeros(int(d * SR)); t = 0
    while t < d - 0.1:
        for k in range(3):
            tc = T(0.018); c = np.sin(2 * np.pi * 4700 * tc) * np.sin(np.pi * tc / 0.018)
            i = int((t + k * 0.026) * SR); out[i:i + len(c)] += c[:len(out) - i]
        t += 0.32 + 0.1 * rng.random()
    return out * 0.05 * v
def tap(v=1.0, f=900):   # 屋瓦上的小脚步
    t = T(0.08); return fade((bp(nz(0.08), f, f * 3) * np.exp(-t / 0.012) + np.sin(2 * np.pi * f * 0.35 * t) * np.exp(-t / 0.02) * 0.4) * 0.35 * v, .001, .02)
def plip(v=1.0):   # 刷子蘸水
    t = T(0.25); x = np.sin(2 * np.pi * np.cumsum(900 + 1400 * np.exp(-t / 0.03)) / SR) * np.exp(-t / 0.05)
    return fade(x * 0.25 * v + bp(nz(0.25), 2000, 7000) * np.exp(-t / 0.02) * 0.08 * v)
def brush(d, v=1.0):   # 湿鬃毛擦纸：柔软宽带 + 细颗粒，起落软
    n = nz(d)
    wet = lp(n, 1800) * 0.5 + bp(n, 1800, 5000) * 0.18
    grain = uniform_filter1d(np.abs(rng.standard_normal(len(n))), 400) * 0.6 + 0.7
    body = wet * grain * envelope(d, [(0, 0), (.06, .9), (.3, 1), (.8, .85), (1, 0)])
    return fade(body * 0.22 * v, .03, .1)
def pat(v=1.0):
    t = T(0.12); return fade(lp(nz(0.12), 500) * np.exp(-t / 0.025) * 0.5 * v + np.sin(2 * np.pi * 140 * t) * np.exp(-t / 0.03) * 0.2 * v)
def page_turn(d=1.2, v=1.0):
    out = np.zeros(int((d + 0.4) * SR))
    lift = hp(nz(0.35), 700) * envelope(0.35, [(0, 0), (.5, .6), (1, .2)]) * 0.18
    wh = bp(nz(0.6), 300, 4000) * np.sin(np.linspace(0, np.pi, int(0.6 * SR))) ** 1.5 * 0.35
    cr = (rng.random(int(0.6 * SR)) < 0.003) * rng.standard_normal(int(0.6 * SR)) * 2.5
    flap_t = T(0.25); flap = (lp(nz(0.25), 1500) * np.exp(-flap_t / 0.03) * 0.6 + np.sin(2 * np.pi * 90 * flap_t) * np.exp(-flap_t / 0.05) * 0.3)
    for x, at in [(lift, 0.0), (wh + bp(cr, 2000, 9000), 0.25), (flap, d - 0.1)]:
        i = int(at * SR); out[i:i + len(x)] += x[:len(out) - i]
    return out * v
def tick(v=1.0, hi=True):
    t = T(0.04); return fade(bp(nz(0.04), 2500 if hi else 1800, 7000) * np.exp(-t / 0.006) * 0.12 * v, .0005, .01)

buf = np.zeros((N, 2)); amb = np.zeros((N, 2))
def put(x, at, g=1.0, pan=0.0, b=None): add(buf if b is None else b, np.asarray(x, np.float64), at, g, pan)

def patter(d, v=1.0):   # little running feet
    out = np.zeros(int(d * SR) + 4000); t = 0.0; k = 0
    while t < d: x = tap(0.5 * v, 700 + 200 * (k % 2)); i = int(t * SR); out[i:i + len(x)] += x[:len(out) - i]; t += 0.19 + 0.03 * rng.random(); k += 1
    return out
def bell(f, d=1.2, v=1.0):
    t = T(d); x = sum(a * np.sin(2 * np.pi * f * r * t) * np.exp(-t / (d * q)) for r, a, q in [(1, 1, .5), (2.76, .4, .2), (5.4, .2, .1)])
    return fade(x * 0.12 * v, .002, .05)
def chalk(d, v=1.0):
    out = np.zeros(int(d * SR)); t = 0.0
    while t < d - 0.1:
        L = 0.06 + 0.1 * rng.random(); n = nz(L); x = bp(n, 2500, 9000) * np.minimum(np.abs(rng.standard_normal(len(n))) ** 2, 3) * 0.12
        i = int(t * SR); out[i:i + len(x)] += fade(x, .005, .02)[:len(out) - i]; t += L + 0.04 * rng.random()
    return out * v
def crumple(v=1.0):
    d = 0.5; n = nz(d); cr = (rng.random(len(n)) < 0.02) * rng.standard_normal(len(n)) * 3
    return fade((bp(cr, 1200, 9000) * 0.5 + hp(n, 2000) * 0.05) * envelope(d, [(0, 0), (.1, 1), (.7, .6), (1, 0)]) * 0.4 * v)
def snore(v=1.0):
    d = 1.6; t = T(d); f = 90 + 10 * np.sin(2 * np.pi * 0.6 * t)
    x = lp(np.sign(np.sin(2 * np.pi * np.cumsum(f) / SR)) * 0.3 + nz(d) * 0.3, 700) * np.sin(np.pi * t / d) ** 2
    return fade(x * 0.12 * v)
def crowd(d, v=1.0):
    n = lp(bp(nz(d), 300, 2500), 2200); sw = 1 + 0.4 * np.sin(2 * np.pi * 0.25 * T(d)) * np.sin(2 * np.pi * 0.07 * T(d))
    return fade(n * sw * 0.05 * v, .8, 1.0)
def erase(d, v=1.0):
    out = np.zeros(int(d * SR)); t = 0.0
    while t < d - 0.1:
        L = 0.12 + 0.05 * rng.random(); x = lp(bp(nz(L), 200, 2500), 1800) * np.sin(np.linspace(0, np.pi, int(round(L * SR)))) * 0.3
        i = int(t * SR); out[i:i + len(x)] += x[:len(out) - i]; t += L
    return out * v
def waves(d, v=1.0):
    n = lp(nz(d), 900) * (0.6 + 0.4 * np.sin(2 * np.pi * 0.2 * T(d)) ** 2)
    return fade(n * 0.05 * v, .5, .8)


def bell(f, d=1.0, v=1.0):
    t = T(d); return fade(sum(a * np.sin(2 * np.pi * f * r * t) * np.exp(-t / (d * q)) for r, a, q in [(1, 1, .45), (2.76, .35, .18), (5.4, .15, .08)]) * .1 * v, .002, .05)
def metal(d=.4, f=900, v=1.0):   # armour plate: inharmonic ring + scrape
    t = T(d); x = sum(np.sin(2 * np.pi * f * r * t + rng.random() * 6) * a for r, a in [(1, 1), (2.32, .6), (3.9, .4), (5.1, .25)]) * np.exp(-t / (d * .3))
    return fade(x * .05 * v + bp(nz(d), 2000, 7000) * np.exp(-t / .03) * .1 * v)
def squeak(d, v=1.0):
    t = T(d); f = 1100 + 300 * np.sin(2 * np.pi * 3 * t) + 200 * np.sin(2 * np.pi * 7.3 * t); ph = 2 * np.pi * np.cumsum(f) / SR
    return fade(np.sin(ph) * (np.abs(np.sin(2 * np.pi * 2.5 * t)) ** 3) * .035 * v, .05, .1)
def hum(d, f=118, v=1.0):
    t = T(d); x = np.sign(np.sin(2 * np.pi * f * t)) * .5 + np.sin(2 * np.pi * 2 * f * t) * .3 + bp(nz(d), 2000, 6000) * .2
    return fade(lp(x, 2500) * .05 * v, .08, .15)
def clunk(v=1.0): t = T(.25); return fade((np.sin(2 * np.pi * 160 * t) * np.exp(-t / .04) + bp(nz(.25), 300, 2000) * np.exp(-t / .02)) * .25 * v, .001, .05)
def rattle(d, v=1.0):
    out = np.zeros(int(d * SR)); tc = 0.0
    while tc < d - .05: x = clunk(.35 + .3 * rng.random()); i = int(tc * SR); out[i:i + len(x)] += x[:len(out) - i]; tc += .05 + .04 * rng.random()
    return out * v
def snipf(v=1.0): t = T(.08); return fade(bp(nz(.08), 3000, 9000) * np.exp(-t / .01) * .25 * v + np.sin(2 * np.pi * 3200 * t) * np.exp(-t / .006) * .1 * v, .0005, .02)
def fire(d, v=1.0):
    n = lp(nz(d), 700) * .05; cr = (rng.random(int(d * SR)) < .0016) * rng.standard_normal(int(d * SR)) * 1.5
    return fade((n + bp(cr, 1500, 6000) * .4) * v, .6, 1.0)
def waterf(d, v=1.0): n = bp(nz(d), 400, 3000) * (0.6 + 0.4 * np.sin(2 * np.pi * .3 * T(d)) ** 2); return fade(n * .03 * v, .6, .8)
def beep(f, d=.12, v=1.0): t = T(d); return fade(np.sign(np.sin(2 * np.pi * f * t)) * .03 * v, .002, .01)
def rocket(d, v=1.0): t = T(d); n = lp(nz(d), 900) * np.interp(t, [0, .3, d * .6, d], [0, 1, .7, 0]); return fade(n * .22 * v)   # muted, never a big boom
def drip(v=1.0): t = T(.2); f = 1400 + 1800 * np.exp(-t / .02); return fade(np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / .04) * .12 * v)
def wheels(d, v=1.0):
    out = np.zeros(int(d * SR)); tc = 0
    while tc < d - .05: x = tap(.35, 1400); i = int(tc * SR); out[i:i + len(x)] += x[:len(out) - i]; tc += .09
    return out * v + lp(nz(d), 500) * .02 * v
def steps(d, v=1.0):
    out = np.zeros(int(d * SR)); tc = 0
    while tc < d - .05: x = pat(.6); i = int(tc * SR); out[i:i + len(x)] += x[:len(out) - i]; tc += .32
    return out * v
def tick_clock(d, v=1.0):
    out = np.zeros(int(d * SR)); tc = 0.0; k = 0
    while tc < d - .05: x = tick(.6, k % 2 == 0); i = int(tc * SR); out[i:i + len(x)] += x[:len(out) - i]; tc += 1.0; k += 1
    return out * v
def mm(d, f0, f1, v=1.0):   # a tiny voiced "hm" (cough, harrumph, gulp): filtered buzz with a pitch glide, no words
    t = T(d); f = np.linspace(f0, f1, len(t)); x = lp(np.sign(np.sin(2 * np.pi * np.cumsum(f) / SR)), 900) * np.sin(np.pi * t / d) ** 2
    return fade(x * .08 * v)

for e in EV:
    t, ty, pan = e['t'], e['type'], e.get('pan', 0.0); d = e.get('dur', .5)
    if ty == 'scratch': put(crayon(d, 1.1), t, 1.0, pan)
    elif ty == 'write': put(write(d), t, 0.9, pan)
    elif ty == 'scribble': put(scribble(d), t, 0.75, pan)
    elif ty in ('paper', 'unroll', 'easel', 'fold', 'flip'): put(paper_rustle(.6 if ty != 'unroll' else d, .9), t, 0.8, pan)
    elif ty == 'page': put(page_turn(d), t, 0.25, -0.1)
    elif ty == 'fire': put(fire(d), t, 1.0, -0.4, amb)
    elif ty == 'rustle': put(swish(.35, .6), t, 1.0, pan); put(paper_rustle(.3, .5), t, 1.0, pan)
    elif ty == 'acorn': put(tap(.7, 1500), t, 1.0, pan); put(tap(.4, 1200), t + .07, 1.0, pan)
    elif ty == 'tap': put(tap(.8), t, 1.0, pan)
    elif ty == 'river': put(waterf(d, .8), t, 1.0, .3, amb)
    elif ty == 'water': put(waterf(d, 1.0), t, 1.0, -.4, amb)
    elif ty == 'bubbles': [put(drip(.6), t + k * .4 + .2 * rng.random(), 1.0, .2) for k in range(int(d / .4))]
    elif ty in ('steps', 'march'): put(steps(d), t, 0.9, pan)
    elif ty == 'snip': put(snipf(), t, 1.0, pan)
    elif ty == 'brow': put(bell(2600, .4, .5), t, 1.0, pan)
    elif ty == 'cough': put(mm(.25, 180, 140), t, 1.0, pan); put(mm(.2, 170, 130), t + .3, 1.0, pan)
    elif ty == 'stylus': put(crayon(d, .7, .8), t, 1.0, pan)
    elif ty == 'clank': put(metal(.5, 700), t, 1.0, pan)
    elif ty == 'forge': put(fire(d, .6), t, 1.0, .5, amb)
    elif ty == 'polish': put(scribble(d, 9, .45), t, 1.0, pan)
    elif ty == 'ting': put(bell(3100, .6, .8), t, 1.0, pan)
    elif ty == 'squeak': put(squeak(d), t, 1.0, pan); [put(metal(.3, 900 + 80 * k, .5), t + k * .45, 1.0, pan) for k in range(int(d / .45))]
    elif ty == 'hinge': put(squeak(.5, 1.4), t, 1.0, pan)
    elif ty == 'flutter': [put(swish(.08, .5), t + k * .07, 1.0, pan + .05 * k) for k in range(14)]
    elif ty == 'gears': [put(tick(.35, k % 2 == 0), t + k * .5, 1.0, -.6, amb) for k in range(int(d / .5))]
    elif ty == 'quill': put(write(d, .8), t, 1.0, pan)
    elif ty == 'clunk': put(clunk(), t, 1.0, pan)
    elif ty == 'click': put(tick(1.4, True), t, 1.0, pan)
    elif ty == 'lever': put(clunk(1.2), t, 1.0, pan); put(squeak(.3, 1.0), t, 1.0, pan)
    elif ty == 'rattle': put(rattle(d), t, 1.0, pan)
    elif ty == 'wind': [put(clunk(.5), t + k * (.18 + .06 * k), 1.0, pan) for k in range(5)]
    elif ty == 'clock': put(tick_clock(d), t, 1.0, .5, amb)
    elif ty == 'harrumph': put(mm(.35, 150, 110), t, 1.0, pan)
    elif ty == 'tray': put(metal(.4, 1800, .6), t, 1.0, pan)
    elif ty == 'swoon': put(swish(.6, .7), t, 1.0, pan)
    elif ty == 'sofa': put(pat(1.0), t, 1.0, pan); put(felt(.8), t + .03, 1.0, pan)
    elif ty == 'teacup': [put(bell(2400 + 200 * (k % 2), .25, .5), t + k * .1, 1.0, pan) for k in range(8)]
    elif ty == 'drip': put(drip(), t, 1.0, pan, amb)
    elif ty == 'shaver': put(hum(d), t, 1.0, pan)
    elif ty == 'marker': put(write(d, .9), t, 1.0, pan)
    elif ty == 'gulp': put(mm(.18, 220, 300), t, 1.0, pan)
    elif ty == 'rocket': put(rocket(d), t, 1.0, -.2)
    elif ty == 'space': put(lp(nz(d), 300) * .015 * np.sin(np.pi * T(d) / d), t, 1.0, 0, amb)
    elif ty == 'beeps': [put(beep(880 + 220 * (k % 3), .08, .8), t + k * .55, 1.0, .4) for k in range(int(d / .55))]
    elif ty == 'ticker': put(tick(1.2, True), t, 1.0, pan)
    elif ty == 'beep_low': put(beep(330, .4, 1.0), t, 1.0, pan)
    elif ty == 'radio': [put(beep(1200, .05, .6), t + k * .12, 1.0, .2) for k in range(int(d / .12))]
    elif ty == 'room': x = lp(brown(d), 400) * 0.02; add(amb, x, t, 1.0, 0.0)
    elif ty == 'wheels': put(wheels(d), t, 1.0, pan)
    elif ty == 'dip': put(plip(), t, 0.9, -0.5)
    elif ty == 'twinkle': [put(bell(f, .9, .5), t + .11 * k, 1.0, pan + .1 * k) for k, f in enumerate([2093, 2637, 3136])]
    elif ty == 'brush':
        dd = d + 0.25; x = brush(dd); p0, p1 = (-0.85, 0.85) if e['dir'] > 0 else (0.85, -0.85)
        Lx = len(x); s0 = int(t * SR); pn = np.linspace(p0, p1, Lx); l, r = np.cos((pn + 1) * np.pi / 4) * 1.414, np.sin((pn + 1) * np.pi / 4) * 1.414
        e2 = min(N, s0 + Lx); buf[s0:e2, 0] += (x * l)[:e2 - s0]; buf[s0:e2, 1] += (x * r)[:e2 - s0]

air = hp(nz(DUR), 3000) * 0.0025   # the faint air of paper
E0 = DUR
amb[:, 0] += air * np.interp(tt, [0, 1, E0, E0 + 1], [1, 1, 1, 0]); amb[:, 1] += np.roll(air, 2000) * np.interp(tt, [0, 1, E0, E0 + 1], [1, 1, 1, 0])

# ——— 旁白 v3：Kokoro af_heart（睡前轻声），24k → 48k ———
# 链路：高通 → 先压缩（慢起慢放，削 TTS 峰均比）→ 配平 EQ（低搁架暖、3 kHz 轻挖、6 kHz 高搁架衰减）
#       → 分频去齿音 → 按 RMS 配平 → 温暖近场混响（预延迟 + 早反射 + 低通尾巴）
from scipy.signal import fftconvolve, sosfilt as _sosfilt
def biquad(x, kind, f0, gain_db, q=0.707):   # RBJ cookbook
    A = 10 ** (gain_db / 40); w = 2 * np.pi * f0 / SR; cw, sw = np.cos(w), np.sin(w); al = sw / (2 * q)
    if kind == 'peak':
        b = [1 + al * A, -2 * cw, 1 - al * A]; a = [1 + al / A, -2 * cw, 1 - al / A]
    else:
        s2 = 2 * np.sqrt(A) * al; sg = 1 if kind == 'high' else -1
        b = [A * ((A + 1) + sg * (A - 1) * cw + s2), -2 * sg * A * ((A - 1) + sg * (A + 1) * cw), A * ((A + 1) + sg * (A - 1) * cw - s2)]
        a = [(A + 1) - sg * (A - 1) * cw + s2, 2 * sg * ((A - 1) - sg * (A + 1) * cw), (A + 1) - sg * (A - 1) * cw - s2]
    return _sosfilt(np.array([b + a]) / a[0], x)
def deess(x, lo=4800, hi=10000, thr_rel=0.5, ratio=4.0):
    band = bp(x, lo, hi, 2)
    eb = uniform_filter1d(np.abs(band), int(0.004 * SR)); ef = uniform_filter1d(np.abs(x), int(0.004 * SR))
    over = eb / (ef * thr_rel + 1e-9)                      # 齿音段：高频包络占全频包络比例过高
    g = np.where(over > 1, over ** (1 / ratio - 1), 1.0)
    g = uniform_filter1d(g, int(0.003 * SR))
    return x - band + band * g, 20 * np.log10(g.min() + 1e-9)
VO_RMS = 10 ** (-21.0 / 20)                                # 每句激活段 RMS（相对同时段配乐+拟音约 +6~10 dB）
vo = np.zeros((N, 2)); vmask = np.zeros(N)
for e in [x for x in EV if x['type'] == 'voice']:
    a, sr = sf.read(os.path.join(HERE, 'out', 'voice', e['id'] + '.wav'))
    if a.ndim > 1: a = a.mean(1)
    a = soxr.resample(a, sr, SR)
    a = hp(a, 75)
    a = compress(a / (np.abs(a).max() + 1e-9) * 0.8, thr=.2, ratio=2.5, att=.008, rel=.14)   # 先压缩
    a = biquad(a, 'low', 220, 1.5)                          # 胸腔一点暖
    a = biquad(a, 'peak', 3200, -2.0, 1.0)                  # 3 kHz 轻挖，去"尖"
    a = biquad(a, 'high', 6000, -4.0)                       # 高频搁架 −4 dB，不刺
    a, gr = deess(a)
    act = np.abs(a) > np.abs(a).max() * 0.05
    a = a * VO_RMS / (np.sqrt(np.mean(a[act] ** 2)) + 1e-9)
    print(f'  vo {e["id"]}: de-ess max GR {gr:5.1f} dB  peak {20*np.log10(np.abs(a).max()):5.1f}')
    add(vo, a, e['t'], 1.0, 0.0)
    s = int(e['t'] * SR); vmask[s:s + len(a)] = 1
# 温暖近场混响：12 ms 预延迟，几条早反射，0.7 s 低通尾巴，两声道去相关；湿声约 −17 dB
def warm_ir(seed):
    r = np.random.default_rng(seed); L = int(0.9 * SR); ir = np.zeros(L); pd = int(0.012 * SR)
    for ms, g in [(7, .5), (11, .38), (17, .3), (23, .22), (31, .16)]: ir[pd + int((ms + r.uniform(-1, 1)) * SR / 1000)] += g * r.choice([-1, 1])
    tt_ = np.arange(L - pd) / SR; tail = r.standard_normal(L - pd) * np.exp(-tt_ / 0.11) * np.clip(tt_ / 0.02, 0, 1) * 0.35
    ir[pd:] += lp(tail, 3200); return lp(ir, 5000)
dry = vo.copy()
for c in range(2):
    wet = fftconvolve(dry[:, c], warm_ir(31 + c), 'full')[:N]
    vo[:, c] += wet * (10 ** (-17 / 20)) / (np.sqrt(np.mean(wet ** 2)) / (np.sqrt(np.mean(dry[:, c] ** 2)) + 1e-12) + 1e-12)

# ——— 配乐 ———
mp = os.path.join(HERE, 'music', 'score.wav')
SG = {'uke': 1.0, 'bassoon': 1.0, 'clarinet': 1.0, 'toypiano': 1.0, 'recorder': 1.0, 'woodblock': 0.9, 'musicbox': 1.4, 'glock': 1.2}
stems = [os.path.join(HERE, 'music', 'stems', k + '.wav') for k in SG]
if all(os.path.exists(p) for p in stems):
    mus = np.zeros((N, 2))
    for k, p in zip(SG, stems):
        m, msr = sf.read(p)
        if m.ndim == 1: m = np.stack([m, m], 1)
        L = min(N, len(m)); mus[:L] += m[:L] * SG[k]
    # 音乐盒和钟琴的金属光泽：3–6 kHz 轻提
    for c in range(2): mus[:, c] += bp(mus[:, c], 3000, 7000, 2) * 0.35
elif os.path.exists(mp):
    m, msr = sf.read(mp)
    if msr != SR: m = soxr.resample(m, msr, SR)
    if m.ndim == 1: m = np.stack([m, m], 1)
    mus = np.zeros((N, 2)); L = min(N, len(m)); mus[:L] = m[:L]
else:
    print('!! music/score.wav 不存在，先跑 music/score.py'); mus = np.zeros((N, 2))
# 旁白下闪避约 −7 dB（平滑）
duck = uniform_filter1d(vmask, int(0.25 * SR)); duck = np.clip(duck * 1.6, 0, 1)
g = 1 - duck * (1 - 10 ** (-11 / 20))
mus *= g[:, None]
# 拟音在旁白下也让 4 dB（数羊、爬梯、盖被子那几句拟音密）
buf *= (1 - duck * (1 - 10 ** (-8 / 20)))[:, None]
mix = mus * 0.75 + buf * 0.9 + amb * 1.0 + vo * 1.0
for c in range(2): mix[:, c] = limit(mix[:, c], .95)
sf.write(os.path.join(HERE, 'out', 'mix.wav'), mix.astype(np.float32), SR)
os.makedirs(os.path.join(HERE, 'out', 'stems'), exist_ok=True)
for nm, x in [('narration', vo), ('foley', buf + amb), ('music', mus * 0.75)]: sf.write(os.path.join(HERE, 'out', 'stems', nm + '.wav'), x.astype(np.float32), SR)
# 电平表
def db(x): return 20 * np.log10(np.sqrt(np.mean(x ** 2)) + 1e-9)
for name, x in [('music', mus), ('foley', buf), ('amb', amb), ('voice', vo), ('mix', mix)]: print(f'{name:6s} RMS {db(x):6.1f} dB  peak {20*np.log10(np.abs(x).max()+1e-9):6.1f}')
if os.environ.get('DBG'):
    fb = np.abs(buf).max(1); 
    for i in np.argsort(fb)[::-1][:1]: print('foley peak at', i / SR)
    w = int(0.5 * SR)
    for k in range(0, N - w, w):
        p = np.abs(buf[k:k + w]).max()
        if p > 0.3: print(f'  {k/SR:5.1f}s foley peak {p:.2f}')
# 每句：旁白 vs 同时段配乐+拟音（目标 +6~9 dB：听得清但不跳出来）
for e in [x for x in EV if x['type'] == 'voice']:
    s = int(e['t'] * SR); L = int(e['d'] * SR)
    bed = mus[s:s + L] * 0.75 + buf[s:s + L] * 0.9 + amb[s:s + L]
    print(f'  {e["id"]}  vo {db(vo[s:s+L]):6.1f}  bed {db(bed):6.1f}  diff {db(vo[s:s+L]) - db(bed):5.1f} dB')
