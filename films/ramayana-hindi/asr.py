"""Whisper (multilingual medium) reads every Hindi narration clip back; prints a similarity score per line."""
import json, sys, difflib, re, os
import soundfile as sf, soxr, numpy as np
from faster_whisper import WhisperModel
HERE = os.path.dirname(os.path.abspath(__file__))
lines = json.load(open(f'{HERE}/tts/lines.json'))
only = set(sys.argv[1:])
m = WhisperModel('medium', device='cpu', compute_type='int8', cpu_threads=4)
norm = lambda s: re.sub(r'[^ऀ-ॿ ]', '', s).replace('ं', '').replace('ँ', '').replace('़', '').split()
out = {}
for L in lines:
    if only and L['id'] not in only: continue
    x, sr = sf.read(f"{HERE}/voices/{L['id']}.wav"); x = soxr.resample(x, sr, 16000).astype(np.float32)
    seg, _ = m.transcribe(x, language='hi', beam_size=5, initial_prompt='रामायण, राम, सीता, लक्ष्मण, हनुमान, रावण, वाल्मीकि, दशरथ, कैकेयी, भरत, सुग्रीव, विभीषण')
    hyp = ' '.join(s.text for s in seg).strip()
    r = difflib.SequenceMatcher(None, norm(L['text']), norm(hyp)).ratio()
    out[L['id']] = [round(r, 3), hyp]
    print(f"{L['id']:6s} {r:.2f}  {hyp}", flush=True)
json.dump(out, open(f'{HERE}/out/asr.json', 'w'), ensure_ascii=False, indent=1)
