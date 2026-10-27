"""out/raw/<id>.wav → voices/<id>.wav (48 kHz, per-character colour) + voices/dur.json + voices/lips.json (mouth open o and brightness b at 24 Hz)
HAL: light saturation + a ~180 Hz bump (gravel). DOT: presence lift. Both: short early reflections so they sit in the room."""
import json, os, numpy as np, soundfile as sf, soxr
from scipy.signal import lfilter, stft
H = os.path.dirname(os.path.abspath(__file__)); SR = 48000
L = json.load(open(f'{H}/tts/lines.json')); os.makedirs(f'{H}/voices', exist_ok=True)
def peq(x, f, gdb, q=1.0):
    A = 10 ** (gdb / 40); w = 2 * np.pi * f / SR; al = np.sin(w) / (2 * q)
    b = [1 + al * A, -2 * np.cos(w), 1 - al * A]; a = [1 + al / A, -2 * np.cos(w), 1 - al / A]
    return lfilter(np.array(b) / a[0], np.array(a) / a[0], x)
def room(x):
    y = x.copy()
    for d, g in [(.011, .16), (.019, .11), (.031, .07)]: n = int(d * SR); y[n:] += x[:-n] * g
    return y
dur, lips = {}, {}
for l in L:
    y, sr = sf.read(f"{H}/{os.environ.get('RAW', 'out/raw')}/{l['id']}.wav"); y = y.mean(1) if y.ndim > 1 else y
    y = soxr.resample(y, sr, SR); y = y / (np.abs(y).max() + 1e-9) * .9
    if l['who'] == 'H': y = .7 * y + .3 * np.tanh(y * 2.6) / np.tanh(2.6); y = peq(y, 180, 2.5, .8); y = peq(y, 2800, -1.5)
    else: y = peq(y, 3200, 2.0, .9)
    y = room(y); y = y / (np.abs(y).max() + 1e-9) * .9
    sf.write(f"{H}/voices/{l['id']}.wav", y.astype(np.float32), SR); dur[l['id']] = round(len(y) / SR, 3)
    hop = SR // 24; f, t, Z = stft(y, SR, nperseg=2400, noverlap=2400 - hop, boundary=None); S = np.abs(Z)
    rms = np.sqrt((S ** 2).mean(0)); p = np.percentile(rms, 95) + 1e-9; cen = (S * f[:, None]).sum(0) / (S.sum(0) + 1e-9)
    lips[l['id']] = {'o': [round(float(np.clip((r / p - .1) / .8, 0, 1)), 2) for r in rms], 'b': [round(float(np.clip((c - 1200) / 2600, 0, 1)), 2) for c in cen]}
json.dump(dur, open(f'{H}/voices/dur.json', 'w'), indent=0); json.dump(lips, open(f'{H}/voices/lips.json', 'w'))
print(len(dur), 'lines', round(sum(dur.values()), 1), 's')
