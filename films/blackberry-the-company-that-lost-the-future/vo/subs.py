"""English subtitles from the voiced lines: word timings (faster-whisper) mapped onto the script text, cues of ≤ 2 rows × 42 chars."""
import json, os, re, numpy as np, soundfile as sf, soxr
from faster_whisper import WhisperModel
H = os.path.dirname(os.path.abspath(__file__)); TL = json.load(open(f'{H}/timeline.json'))
m = WhisperModel('base.en', device='cpu', compute_type='int8'); MAX = 84
def rows(s):
    if len(s) <= 42: return s
    sp = [i for i, c in enumerate(s) if c == ' ']; c = min(sp, key=lambda i: abs(i - len(s) / 2)); return s[:c] + '\n' + s[c + 1:]
cues = []
for l in TL['lines']:
    y, sr = sf.read(f"{H}/wav/{l['id']}.wav"); y = y if y.ndim == 1 else y.mean(1); y = soxr.resample(y, sr, 16000).astype(np.float32)
    ws = [w for s in m.transcribe(y, word_timestamps=True, language='en')[0] for w in s.words]
    toks = l['text'].split(); t0 = l['t'] - l['trim']
    # chunk the script text at clause boundaries into ≤ MAX chars
    parts, cur = [], ''
    for tk in toks:
        if cur and len(cur) + 1 + len(tk) > MAX: parts.append(cur); cur = tk
        else: cur = (cur + ' ' + tk).strip()
        if re.search(r'[.?!]$', tk) and len(cur) > 40: parts.append(cur); cur = ''
    if cur: parts.append(cur)
    n = len(toks); i = 0
    for p in parts:
        k = len(p.split()); a = i * len(ws) // n; b = max(a, (i + k) * len(ws) // n - 1)
        ta = t0 + ws[min(a, len(ws) - 1)].start if ws else l['t']; tb = t0 + ws[min(b, len(ws) - 1)].end if ws else l['t'] + l['dur']
        cues.append([max(l['t'] - .05, ta - .05), tb + .2, rows(p)]); i += k
for j in range(len(cues) - 1):
    if cues[j][1] > cues[j + 1][0] - .04: cues[j][1] = cues[j + 1][0] - .04
    if cues[j][1] - cues[j][0] < 1.0: cues[j][1] = min(cues[j][0] + 1.0, cues[j + 1][0] - .04)
tc = lambda s: f'{int(s // 3600):02d}:{int(s % 3600 // 60):02d}:{int(s % 60):02d},{int(round((s % 1) * 1000)) % 1000:03d}'
with open(f'{H}/../BRAND_CORONER_CASE007_BLACKBERRY_EN.srt', 'w') as o:
    for j, (a, b, s) in enumerate(cues, 1): o.write(f'{j}\n{tc(a)} --> {tc(b)}\n{s}\n\n')
print(len(cues), 'cues')
