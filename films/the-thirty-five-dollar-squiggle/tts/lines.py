# story.json → tts/lines.json (Kokoro af_heart, the warm storyteller used only as Chatterbox's reference and fallback)
import json, os
H = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
S = json.load(open(f'{H}/story.json'))
L = [{'id': i, 'text': t, 'voice': 'af_heart', 'speed': .9} for p in S['pages'] for i, t, _ in p['lines']]
json.dump(L, open(f'{H}/tts/lines.json', 'w'), indent=1); print(len(L), 'lines')
