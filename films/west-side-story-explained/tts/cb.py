"""Narrate every line with Chatterbox. The narrator timbre comes from a reference clip of Kokoro am_michael lines;
Chatterbox gives it natural, unhurried pacing. Usage: python tts/cb.py [ids…]"""
import json, os, sys, time, numpy as np, soundfile as sf, torch
torch.set_num_threads(4)
from chatterbox.tts import ChatterboxTTS
H = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
L = json.load(open(f'{H}/tts/lines.json')); only = set(sys.argv[1:])
os.makedirs(f'{H}/out/cb', exist_ok=True)
REF = f'{H}/out/cb/ref.wav'
if not os.path.exists(REF):
    ys = []
    for i in ['s02', 's04', 's08']: y, sr = sf.read(f'{H}/out/raw/{i}.wav'); ys += [y, np.zeros(int(.3 * sr))]
    sf.write(REF, np.concatenate(ys), sr)
m = ChatterboxTTS.from_pretrained(device='cpu')
for l in L:
    if only and l['id'] not in only: continue
    out = f"{H}/out/cb/{l['id']}.wav"
    if os.path.exists(out) and not only: continue
    t0 = time.time(); wav = m.generate(l['text'], audio_prompt_path=REF, exaggeration=.55, cfg_weight=.5, temperature=.7)
    sf.write(out, wav.squeeze(0).numpy(), m.sr); print(l['id'], round(wav.shape[-1] / m.sr, 2), 's in', round(time.time() - t0, 1), 's', flush=True)
