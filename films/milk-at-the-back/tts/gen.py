"""script.py → tts/sentences.json: every sentence voiced on its own (am_onyx, unhurried), so voice.py can join them with real pauses."""
import json, os, sys, re
sys.path.insert(0, os.path.dirname(__file__)); from script import VO
H = os.path.dirname(os.path.abspath(__file__))
say = lambda s: s.replace(' — ', ', ').replace('—', ', ')
L = []
for i, s in enumerate(VO):
    for k, part in enumerate(re.split(r'(?<=[.?!:])\s+(?=[A-Z])', s)):
        L.append({'id': f's{i + 1:02d}_{k}', 'text': say(part), 'voice': 'am_onyx', 'speed': .84})
json.dump(L, open(os.path.join(H, 'sentences.json'), 'w'), indent=1)
print(len(L), 'sentences')
