"""Re-voice every line with Chatterbox (expressive, open source). Each character's timbre comes from a short reference clip
built from their Kokoro lines; Chatterbox supplies natural pacing and emotion. Usage: python tts/cb.py [ids…]"""
import json, os, sys, time, numpy as np, soundfile as sf, torch
torch.set_num_threads(4)
from chatterbox.tts import ChatterboxTTS
H = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
L = json.load(open(f'{H}/tts/lines.json')); only = set(sys.argv[1:])
def ref(who, ids):
    p = f'{H}/out/cb/ref_{who}.wav'
    if not os.path.exists(p):
        ys = []
        for i in ids: y, sr = sf.read(f'{H}/out/raw/{i}.wav'); ys += [y, np.zeros(int(.3 * sr))]
        sf.write(p, np.concatenate(ys), sr)
    return p
REF = {'H': ref('H', ['c06', 'c11', 'c21']), 'D': ref('D', ['c01', 'c14', 'c20'])}
STYLE = {'H': dict(exaggeration=.35, cfg_weight=.5, temperature=.7), 'D': dict(exaggeration=.7, cfg_weight=.35, temperature=.8)}
HOT = {'c04', 'c07', 'c10', 'c14', 'c18', 'c31', 'c35'}   # Dot at full panic
m = ChatterboxTTS.from_pretrained(device='cpu')
for l in L:
    if only and l['id'] not in only: continue
    out = f"{H}/out/cb/{l['id']}.wav"
    if os.path.exists(out) and not only: continue
    st = dict(STYLE[l['who']]); 
    if l['id'] in HOT: st['exaggeration'] = .9
    t0 = time.time(); wav = m.generate(l['text'], audio_prompt_path=REF[l['who']], **st)
    sf.write(out, wav.squeeze(0).numpy(), m.sr); print(l['id'], round(wav.shape[-1] / m.sr, 2), 's in', round(time.time() - t0, 1), 's', flush=True)
