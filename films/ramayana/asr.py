"""Speech check with Sanskrit names: whisper small.en, prompted with the names, compared word by word (names count)."""
import json, os, re, sys, difflib
import soundfile as sf, soxr
from faster_whisper import WhisperModel
HERE = os.path.dirname(os.path.abspath(__file__))
L = json.load(open(f'{HERE}/tts/lines.json'))
NAMES = 'Sugriva, Kaikeyi, Ayodhya, Valmiki, Tamasa, krauncha, Rama, Ramayana, Ayodhya, Dasharatha, Bharata, Lakshmana, Shatrughna, Vishvamitra, Mithila, Janaka, Sita, Shiva, Kaikeyi, Manthara, Shurpanakha, Ravana, Lanka, Jatayu, Hanuman, Sugriva, ashoka, Vibhishana, Lava, Kusha'
m = WhisperModel(os.environ.get('WM', 'small.en'), compute_type='float32')
norm = lambda s: re.sub(r"[^a-z' ]", ' ', s.lower().replace('—', ' ')).split()
bad = 0
only = sys.argv[1:]
for l in L:
    if only and l['id'] not in only: continue
    a, sr = sf.read(f"{HERE}/voices/{l['id']}.wav", dtype='float32'); a = soxr.resample(a, sr, 16000)
    txt = ' '.join(s.text for s in m.transcribe(a, initial_prompt=NAMES, language='en')[0]).strip()
    r = difflib.SequenceMatcher(None, norm(l['sub']), norm(txt)).ratio()
    ok = r >= .9; bad += not ok
    print(('OK  ' if ok else 'DIFF'), f"{r:.2f}", l['id'], '|', txt)
print('mismatches', bad)
