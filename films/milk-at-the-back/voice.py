"""Join each scene's sentences with pauses so the line fills ~13.8 s of its 15 s scene (a calm ~140 wpm read).
Light low-mid warmth + gentle compression. → voices/sNN.wav (48 kHz), voices/dur.json"""
import json, os, glob, re, numpy as np, soundfile as sf, soxr
from scipy.signal import lfilter
H = os.path.dirname(os.path.abspath(__file__)); SR = 48000; TARGET = 13.8
S = json.load(open(f'{H}/tts/sentences.json'))
def peq(x, f, gdb, q=1.0):
    A = 10 ** (gdb / 40); w = 2 * np.pi * f / SR; al = np.sin(w) / (2 * q)
    b = [1 + al * A, -2 * np.cos(w), 1 - al * A]; a = [1 + al / A, -2 * np.cos(w), 1 - al / A]
    return lfilter(np.array(b) / a[0], np.array(a) / a[0], x)
scenes = sorted({s['id'][:3] for s in S}); dur = {}
for sc in scenes:
    parts = []
    for s in [x for x in S if x['id'][:3] == sc]:
        y, sr = sf.read(f"{H}/out/sent/{s['id']}.wav"); y = soxr.resample(y, sr, SR); parts.append((s['text'], y))
    speech = sum(len(y) for _, y in parts) / SR; n = len(parts) - 1
    gap = min(1.0, max(.3, (TARGET - speech) / n)) if n else 0
    out = []
    for j, (txt, y) in enumerate(parts):
        out.append(y)
        if j < n: out.append(np.zeros(int(SR * (gap * (1.25 if txt.endswith(('?', ':')) else 1)))))
    y = np.concatenate(out)
    y = peq(y, 150, 2.0, .8); y = peq(y, 3000, 1.0, 1.0)
    y = y / (np.abs(y).max() + 1e-9) * .9
    sf.write(f'{H}/voices/{sc}.wav', y.astype(np.float32), SR); dur[sc] = round(len(y) / SR, 3)
json.dump(dur, open(f'{H}/voices/dur.json', 'w'), indent=0)
w = sum(len(re.findall(r"[\w']+", s['text'])) for s in S)
print('total', round(sum(dur.values()), 1), 's', 'longest', max(dur.values()), 'wpm %.0f' % (w / sum(dur.values()) * 60))
