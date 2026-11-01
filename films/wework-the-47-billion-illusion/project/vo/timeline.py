"""Conform the edit to the voiceover. Lines are placed back to back at natural pace (never sped up); each scene lasts as long as
its narration needs. Each scene's visual design (authored on a 0–30 s grid) is time-warped piecewise-linearly so that its key
beats land on the words they illustrate (anchors below). Writes timeline.json (scene bases, durations, warps, line starts)."""
import json, os, numpy as np, soundfile as sf
H = os.path.dirname(os.path.abspath(__file__))
L = json.load(open(f'{H}/lines.json'))
GAP, TAIL = .45, 1.1
LEAD = {1: 3.6}                      # scene 01: black, the red line draws, then "forty-seven billion dollars" lands on the number
TAILS = {16: 5.5}                    # hold the identity slate after the final line
# design time (s, on the original 30 s grid) → line number whose start it should meet
ANCH = {1: [(3.6, 1), (8.6, 3), (18.4, 6), (25.0, 7)], 2: [(11.0, 2), (21.4, 4), (25.0, 6)], 3: [(9.0, 2), (19.0, 4), (26.0, 6)],
        4: [(2.4, 2), (8.5, 3), (20.6, 6), (25.4, 7)], 5: [(3.0, 2), (17.0, 3), (24.0, 4)], 6: [(3.0, 2), (12.0, 3), (20.5, 4), (23.0, 5)],
        7: [(11.0, 2), (15.0, 3), (21.0, 4)], 8: [(9.5, 4), (25.5, 7)], 9: [(1.0, 1), (3.0, 2), (10.0, 3), (20.6, 6)],
        10: [(1.6, 4), (5.0, 5), (10.0, 6), (22.5, 7)], 11: [(1.0, 1), (6.0, 4), (11.0, 5), (18.0, 6)],
        12: [(10.0, 3), (12.4, 4), (20.2, 5), (24.0, 8)], 13: [(1.2, 2), (10.5, 4), (21.0, 6)], 14: [(1.4, 2), (10.5, 4), (20.5, 5)],
        15: [(3.0, 3), (10.5, 4), (20.6, 7)], 16: [(1.4, 3), (14.5, 5), (23.4, 8)]}
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
        r = starts[ln] - (.1 if (i, ln) == (1, 1) else .25)
        if r > pts[-1][1] + .3 and dt > pts[-1][0]: pts.append((dt, round(r, 3)))
    if dur > pts[-1][1] + .3: pts.append((30.0, dur))
    else: pts[-1] = (30.0, dur)
    scenes.append({'i': i, 'base': round(base, 3), 'dur': dur, 'warp': pts}); base += dur
json.dump({'total': round(base, 3), 'scenes': scenes, 'lines': out_l}, open(f'{H}/timeline.json', 'w'), indent=1)
print('total', round(base, 2), 's =', f'{int(base // 60)}:{base % 60:05.2f}')
for s in scenes: print(s['i'], s['dur'], [(round(a, 1), round(b, 1)) for a, b in s['warp']])
