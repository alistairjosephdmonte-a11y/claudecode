# Trim each narrated line to its voiced span (+ small pads), resample to 48k, write out/voice/<id>.wav and voice.json {id: seconds}
import json, os, sys, numpy as np, soundfile as sf, soxr
H = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = sys.argv[1] if len(sys.argv) > 1 else f'{H}/out/cb'
os.makedirs(f'{H}/out/voice', exist_ok=True); D = {}
for l in json.load(open(f'{H}/tts/lines.json')):
    y, sr = sf.read(f"{RAW}/{l['id']}.wav")
    if y.ndim > 1: y = y.mean(1)
    y = soxr.resample(y, sr, 48000); sr = 48000
    e = np.convolve(np.abs(y), np.ones(480) / 480, 'same'); on = np.where(e > e.max() * .03)[0]
    a, b = max(0, on[0] - int(.04 * sr)), min(len(y), on[-1] + int(.12 * sr)); y = y[a:b]
    y[:240] *= np.linspace(0, 1, 240); y[-960:] *= np.linspace(1, 0, 960)
    sf.write(f"{H}/out/voice/{l['id']}.wav", y, sr); D[l['id']] = round(len(y) / sr, 3)
json.dump(D, open(f'{H}/voice.json', 'w'), indent=1); print(len(D), 'lines,', round(sum(D.values()), 1), 's of narration')
