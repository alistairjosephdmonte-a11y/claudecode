"""Word timestamps for every narration line (placed at tl.json starts) → audio/words.json."""
import json, os
from faster_whisper import WhisperModel
import soundfile as sf, soxr, numpy as np
def aud(p):
    a, sr = sf.read(p, dtype='float32')
    a = a.mean(1) if a.ndim > 1 else a
    return soxr.resample(a, sr, 16000).astype(np.float32)
B = '../brand-coroner-blockbuster'
tl = json.load(open(f'{B}/out/tl.json')); m = WhisperModel('base.en', device='cpu', compute_type='int8')
out = []
for L in tl:
    segs, _ = m.transcribe(aud(f"{B}/out/voice/{L['id']}.wav"), word_timestamps=True, language='en')
    ws = [(w.word.strip(), round(L['t'] + w.start, 3), round(L['t'] + w.end, 3)) for s in segs for w in s.words]
    out.append({**L, 'words': ws}); print(L['id'], len(ws), len(L['text'].split()))
json.dump(out, open('audio/words.json', 'w'), indent=0)
