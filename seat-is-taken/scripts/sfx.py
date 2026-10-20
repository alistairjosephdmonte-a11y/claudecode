"""Synthesizes every sound effect and the music bed as separate WAV files in public/audio/.
All sounds are original (numpy/scipy); no samples or episode audio are used."""
import numpy as np, soundfile as sf
from scipy.signal import butter, sosfilt

SR = 48000
OUT = 'public/audio'
rng = np.random.default_rng(42)
def T(sec): return np.arange(int(sec * SR)) / SR
def lp(x, f): return sosfilt(butter(2, f, 'low', fs=SR, output='sos'), x)
def hp(x, f): return sosfilt(butter(2, f, 'high', fs=SR, output='sos'), x)
def bp(x, lo, hi): return sosfilt(butter(2, [lo, hi], 'band', fs=SR, output='sos'), x)
def norm(x, peak=0.8): return x / (np.abs(x).max() + 1e-9) * peak
def save(name, x, peak=0.8): sf.write(f'{OUT}/{name}.wav', norm(x, peak).astype(np.float32), SR)
def burst(sec, lo, hi, dec): t = T(sec); return bp(rng.standard_normal(len(t)), lo, hi) * np.exp(-t * dec)
def pluck(f, sec, damp=0.996):  # Karplus-Strong
    n = int(SR / f); buf = rng.uniform(-1, 1, n); out = np.zeros(int(sec * SR))
    for i in range(len(out)):
        out[i] = buf[i % n]; buf[i % n] = damp * 0.5 * (buf[i % n] + buf[(i + 1) % n])
    return out

# door: latch click + soft swing (low creak sweep)
t = T(0.9); latch = burst(0.9, 1500, 5000, 60)
swing = np.sin(2 * np.pi * np.cumsum(np.interp(t, [0, 0.9], [180, 120])) / SR) * (1 + 0.5 * np.sin(2 * np.pi * 23 * t)) * np.exp(-((t - 0.45) / 0.25) ** 2)
save('door', latch + 0.25 * lp(swing, 900) + 0.15 * burst(0.9, 80, 400, 3), 0.6)
# takeaway bag rustle: bursts of crinkly band noise
x = np.zeros(int(0.7 * SR))
for s in rng.uniform(0, 0.55, 14): i = int(s * SR); b = burst(0.08, 2500, 9000, 70); x[i:i + len(b)] += b * rng.uniform(.3, 1)
save('bag', x, 0.5)
# cushion slide: soft fabric swish (band noise with a hump envelope)
t = T(0.45); save('cushion', bp(rng.standard_normal(len(t)), 300, 2500) * np.sin(np.pi * t / 0.45) ** 2, 0.5)
# couch creak: a low resonant groan with rapid amplitude stutter
t = T(0.5); cr = np.sin(2 * np.pi * np.cumsum(np.interp(t, [0, .5], [140, 95])) / SR) * (0.5 + 0.5 * np.sign(np.sin(2 * np.pi * 38 * t)))
save('creak', lp(cr, 700) * np.sin(np.pi * t / 0.5) + 0.2 * burst(0.5, 100, 600, 6), 0.5)
# typography click: tiny high tick
save('click', burst(0.05, 3000, 9000, 220) + 0.3 * np.sin(2 * np.pi * 2400 * T(0.05)) * np.exp(-T(0.05) * 150), 0.4)
# marker stroke for diagram lines: felt-tip squeak-free scratch
t = T(0.35); save('marker', bp(rng.standard_normal(len(t)), 1200, 6000) * (0.6 + 0.4 * np.sin(2 * np.pi * 9 * t)) * np.sin(np.pi * t / 0.35), 0.35)
# food container: cardboard flap (low thud + crinkle) and a soft utensil tick
save('container', burst(0.3, 150, 900, 20) + 0.5 * burst(0.3, 2000, 7000, 35), 0.5)
save('utensil', np.sin(2 * np.pi * 3100 * T(0.25)) * np.exp(-T(0.25) * 25) + 0.6 * np.sin(2 * np.pi * 4700 * T(0.25)) * np.exp(-T(0.25) * 35), 0.25)
# fry pickup (little paper slip) and restrained bite (short crunchy burst)
save('pickup', burst(0.15, 1500, 6000, 40), 0.4)
x = np.zeros(int(0.25 * SR))
for s in (0.0, 0.03, 0.07): i = int(s * SR); b = burst(0.06, 800, 5000, 90); x[i:i + len(b)] += b
save('bite', x, 0.45)

# ---- music bed (15 s, 120 BPM, C major, pizzicato-style plucks + soft upright-ish bass)
DUR = 15.0; N = int(DUR * SR); BEAT = 0.5; bed = np.zeros(N)
def place(sig, at, gain):
    i = int(at * SR); m = min(len(sig), N - i)
    if m > 0: bed[i:i + m] += sig[:m] * gain
HZ = lambda m: 440 * 2 ** ((m - 69) / 12)
prog = [(48, [60, 64, 67, 72]), (43, [59, 62, 67, 71]), (45, [60, 64, 69, 72]), (41, [60, 65, 69, 72])]  # C G Am F
for bar in range(8):
    root, arp = prog[bar % 4]; t0 = bar * 2.0
    place(pluck(HZ(root), 1.0, 0.993) * 1.0, t0, 0.55); place(pluck(HZ(root + 7), 0.8, 0.993), t0 + 1.0, 0.4)
    for k, b in enumerate([0, 0.5, 0.75, 1.25, 1.5]):
        place(pluck(HZ(arp[k % 4]), 0.5, 0.990), t0 + b, 0.22)
bed = lp(bed, 5000)
save('music', bed, 0.5)
# stings: a short comedic sting (three-note pluck + muted 'bonk') and the final sting (major chord bloom)
s = np.zeros(int(1.2 * SR))
for i, (m, d) in enumerate([(72, 0), (67, 0.11), (60, 0.22)]): p = pluck(HZ(m), 0.9, 0.992); j = int(d * SR); s[j:j + len(p)] += p[:len(s) - j]
save('sting_small', s, 0.55)
f = np.zeros(int(1.6 * SR))
for m, d in [(48, 0), (60, 0.0), (64, 0.04), (67, 0.08), (72, 0.12)]: p = pluck(HZ(m), 1.4, 0.997); j = int(d * SR); f[j:j + len(p)] += p[:len(f) - j]
f *= np.clip((1.6 - T(1.6)) / 0.4, 0, 1)
save('sting_final', f, 0.6)
print('ok')
