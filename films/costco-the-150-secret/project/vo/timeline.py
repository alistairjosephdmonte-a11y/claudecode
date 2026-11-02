"""Conform the edit to the voiceover. Lines are placed back to back at natural pace (never sped up); each scene lasts as long as
its narration needs. Each scene's visual design (authored on a 0–30 s grid) is time-warped piecewise-linearly so that its key
beats land on the words they illustrate (anchors below). Writes timeline.json (scene bases, durations, warps, line starts)."""
import json, os, numpy as np, soundfile as sf
H = os.path.dirname(os.path.abspath(__file__))
L = json.load(open(f'{H}/lines.json'))
GAP, TAIL = .45, 1.1
LEAD = {1: 3.6}                      # scene 01: register click, the red line draws, then "one dollar and fifty cents" lands on $1.50
TAILS = {16: 5.5}                    # hold the end slate after the final line
# design time (s, on the original 30 s grid) → line id whose start it should meet
ANCH = {1: [(3.6, 's01_01'), (8.6, 's01_02'), (12.0, 's01_03'), (18.0, 's01_04'), (25.0, 's01_06')],
        2: [(2.0, 's02_02'), (14.0, 's02_03'), (20.0, 's02_04'), (24.0, 's02_06')],
        3: [(9.0, 's03_03'), (15.0, 's03_04'), (24.0, 's03_06')],
        4: [(6.0, 's04_03'), (10.0, 's04_05'), (18.0, 's04_06'), (24.0, 's04_07')],
        5: [(1.6, 's05_01'), (10.0, 's05_02'), (20.0, 's05_05')],
        6: [(8.0, 's06_03'), (15.0, 's06_04'), (22.0, 's06_05')],
        7: [(6.0, 's07_02'), (10.0, 's07_03'), (20.0, 's07_04')],
        8: [(6.0, 's08_02'), (14.0, 's08_04'), (20.0, 's08_05'), (25.0, 's08_06')],
        9: [(6.0, 's09_03'), (12.0, 's09_04'), (18.0, 's09_05'), (24.0, 's09_07')],
        10: [(8.0, 's10_03'), (11.0, 's10_04'), (20.0, 's10_06')],
        11: [(4.0, 's11_02'), (12.0, 's11_03'), (22.0, 's11_06')],
        12: [(6.0, 's12_02'), (10.0, 's12_03'), (14.0, 's12_04'), (16.0, 's12_05')],
        13: [(10.0, 's13_04'), (18.0, 's13_06')],
        14: [(8.0, 's14_04'), (12.0, 's14_05'), (20.0, 's14_06'), (24.0, 's14_07')],
        15: [(14.0, 's15_04'), (24.0, 's15_07')],
        16: [(8.0, 's16_03'), (14.0, 's16_05'), (21.0, 's16_07'), (23.4, 's16_08')]}
def speech(path):                    # trimmed speech segment (drop leading/trailing silence)
    y, sr = sf.read(path); y = y if y.ndim == 1 else y.mean(1); e = np.abs(y) > .01; idx = np.where(e)[0]
    a, b = (idx[0], idx[-1]) if len(idx) else (0, len(y)); a = max(0, a - int(.03 * sr)); b = min(len(y), b + int(.08 * sr)); return a / sr, (b - a) / sr
out_l, scenes, base = [], [], 0.0
for i in range(1, 17):
    ls = [l for l in L if l['scene'] == i]; t = LEAD.get(i, .6); starts = {}
    for k, l in enumerate(ls, 1):
        off, d = speech(f"{H}/wav/{l['id']}.wav"); starts[l['id']] = t
        out_l.append({**l, 't': round(base + t, 3), 'local': round(t, 3), 'dur': round(d, 3), 'trim': round(off, 3)}); t += d + GAP
    dur = round(t - GAP + TAILS.get(i, TAIL), 3)
    pts = [(0.0, 0.0)]
    for (dt, ln) in ANCH.get(i, []):
        r = starts[ln] - (.1 if ln == 's01_01' else .25)
        if r > pts[-1][1] + .3 and dt > pts[-1][0]: pts.append((dt, round(r, 3)))
    if dur > pts[-1][1] + .3: pts.append((30.0, dur))
    else: pts[-1] = (30.0, dur)
    scenes.append({'i': i, 'base': round(base, 3), 'dur': dur, 'warp': pts}); base += dur
json.dump({'total': round(base, 3), 'scenes': scenes, 'lines': out_l}, open(f'{H}/timeline.json', 'w'), indent=1)
print('total', round(base, 2), 's =', f'{int(base // 60)}:{base % 60:05.2f}')
for s in scenes: print(s['i'], s['dur'], [(round(a, 1), round(b, 1)) for a, b in s['warp']])
