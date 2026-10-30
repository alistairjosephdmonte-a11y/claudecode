"""Narrate every line with Chatterbox. The narrator: a dry British storyteller whose timbre comes from Kokoro bm_george reference lines;
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
    for i in ['c01b', 'c05c', 'c07a']: y, sr = sf.read(f'{H}/out/raw/{i}.wav'); ys += [y, np.zeros(int(.3 * sr))]
    sf.write(REF, np.concatenate(ys), sr)
m = ChatterboxTTS.from_pretrained(device='cpu')
for l in L:
    if only and l['id'] not in only: continue
    out = f"{H}/out/cb/{l['id']}.wav"
    if os.path.exists(out) and not only: continue
    t0 = time.time(); wav = m.generate(l['text'], audio_prompt_path=REF, exaggeration=.38, cfg_weight=.42, temperature=.65)
    sf.write(out, wav.squeeze(0).numpy(), m.sr); print(l['id'], round(wav.shape[-1] / m.sr, 2), 's in', round(time.time() - t0, 1), 's', flush=True)
