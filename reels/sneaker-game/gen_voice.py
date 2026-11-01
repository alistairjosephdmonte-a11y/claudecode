import json
import sys

import numpy as np
import soundfile as sf
from kokoro import KPipeline

VOICE = sys.argv[1] if len(sys.argv) > 1 else "am_michael"
SPEED = float(sys.argv[2]) if len(sys.argv) > 2 else 1.2
SR = 24000
GAP = 0.25

lines = json.load(open("script.json"))
pipe = KPipeline(lang_code="a")

audio = [np.zeros(int(0.15 * SR), dtype=np.float32)]
t = 0.15
out_lines, out_words = [], []

for i, line in enumerate(lines):
    chunks, tokens, offset = [], [], 0.0
    for r in pipe(line["say"], voice=VOICE, speed=SPEED):
        a = r.audio.numpy()
        for tok in r.tokens:
            if tok.start_ts is None or not any(c.isalnum() for c in tok.text):
                continue
            tokens.append((tok.start_ts + offset, tok.end_ts + offset))
        chunks.append(a)
        offset += len(a) / SR
    seg = np.concatenate(chunks)
    dur = len(seg) / SR

    display = line["text"].split()
    n, m = len(display), len(tokens)
    for j, w in enumerate(display):
        a = tokens[j * m // n] if m else (0, dur)
        b = tokens[min(m - 1, ((j + 1) * m - 1) // n)] if m else (0, dur)
        out_words.append({"line": i, "text": w, "start": round(t + a[0], 3), "end": round(t + b[1], 3)})

    out_lines.append({"text": line["text"], "start": round(t, 3), "end": round(t + dur, 3)})
    audio += [seg, np.zeros(int(GAP * SR), dtype=np.float32)]
    t += dur + GAP

audio.append(np.zeros(int(0.6 * SR), dtype=np.float32))
sf.write("public/voice.wav", np.concatenate(audio), SR)
json.dump({"lines": out_lines, "words": out_words, "duration": round(t + 0.6, 3)}, open("src/voice.json", "w"), indent=1)
print(f"done: {t + 0.6:.2f}s, {len(out_words)} words")
