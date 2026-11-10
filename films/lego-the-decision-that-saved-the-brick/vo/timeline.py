"""Conform the edit to the voiceover. Lines are placed back to back at natural pace (never sped up); each scene lasts as long as
its narration needs. Each scene's visual design (authored on a 0–30 s grid) is time-warped piecewise-linearly so that its key
beats land on the words they illustrate (anchors below). Writes timeline.json (scene bases, durations, warps, line starts)."""
import json, os, numpy as np, soundfile as sf
H = os.path.dirname(os.path.abspath(__file__))
L = json.load(open(f'{H}/lines.json'))
GAP, TAIL = .45, 1.1
LEAD = {1: 3.0}                      # scene 01: register click, the red line draws, then "one dollar and fifty cents" lands on $1.50
TAILS = {16: 5.5}                    # hold the end slate after the final line
# design time (s, on the original 30 s grid) → line id whose start it should meet
def grid(k, n): return 1.0 + 27.0 * (k - 1) / n     # design time of line k (1-based) of n, on the 0–30 grid
NL = {i: sum(1 for l in L if l['scene'] == i) for i in range(1, 17)}
ANCH = {i: [(grid(k, NL[i]), k) for k in range(1, NL[i] + 1)] for i in range(1, 17)}
def speech(path):                    # trimmed speech segment (drop leading/trailing silence)
    y, sr = sf.read(path); y = y if y.ndim == 1 else y.mean(1); e = np.abs(y) > .01; idx = np.where(e)[0]
    a, b = (idx[0], idx[-1]) if len(idx) else (0, len(y)); a = max(0, a - int(.03 * sr)); b = min(len(y), b + int(.08 * sr)); return a / sr, (b - a) / sr
out_l, scenes, base = [], [], 0.0
for i in range(1, 17):
    ls = [l for l in L if l['scene'] == i]; t = LEAD.get(i, .6); starts = {}
    for k, l in enumerate(ls, 1):
        off, d = speech(f"{H}/wav/{l['id']}.wav"); starts[k] = t
        out_l.append({**l, 't': round(base + t, 3), 'local': round(t, 3), 'dur': round(d, 3), 'trim': round(off, 3)}); t += d + GAP
    dur = round(t - GAP + TAILS.get(i, TAIL), 3)
    pts = [(0.0, 0.0)]
    for (dt, ln) in ANCH.get(i, []):
        r = starts[ln] - .25
        if r > pts[-1][1] + .3 and dt > pts[-1][0]: pts.append((dt, round(r, 3)))
    if dur > pts[-1][1] + .3: pts.append((30.0, dur))
    else: pts[-1] = (30.0, dur)
    scenes.append({'i': i, 'base': round(base, 3), 'dur': dur, 'n': len(ls), 'warp': pts}); base += dur
json.dump({'total': round(base, 3), 'scenes': scenes, 'lines': out_l}, open(f'{H}/timeline.json', 'w'), indent=1)
print('total', round(base, 2), 's =', f'{int(base // 60)}:{base % 60:05.2f}')
for s in scenes: print(s['i'], s['dur'], [(round(a, 1), round(b, 1)) for a, b in s['warp']])
