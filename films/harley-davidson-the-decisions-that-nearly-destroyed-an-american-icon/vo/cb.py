"""Voice every line with Chatterbox, using the Brand Coroner narrator reference (same timbre as Case 001). Usage: python cb.py [ids…]"""
import json, os, sys, time, soundfile as sf, torch
torch.set_num_threads(4)
from chatterbox.tts import ChatterboxTTS
H = os.path.dirname(os.path.abspath(__file__)); L = json.load(open(f'{H}/lines.json')); only = set(sys.argv[1:])
REF = os.path.join(H, 'ref', 'ref.wav')   # 10.9 s of the series narrator, cut from the Case 011 narration stem
os.makedirs(f'{H}/wav', exist_ok=True); m = ChatterboxTTS.from_pretrained(device='cpu')
for l in L:
    if only and l['id'] not in only: continue
    out = f"{H}/wav/{l['id']}.wav"
    if os.path.exists(out) and not only: continue
    t0 = time.time(); wav = m.generate(l.get('say', l['text']), audio_prompt_path=REF, exaggeration=.3, cfg_weight=.45, temperature=.6)
    sf.write(out, wav.squeeze(0).numpy(), m.sr); print(l['id'], round(wav.shape[-1] / m.sr, 2), 's in', round(time.time() - t0, 1), 's', flush=True)
print('CB_DONE')
