# story.json → tts/lines.json (Kokoro bm_george: the British reference timbre for Chatterbox)
import json, os
H = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
S = json.load(open(f'{H}/story.json'))
json.dump([{'id': b[2], 'text': b[3], 'voice': 'bm_george', 'speed': .92} for c in S['chapters'] for b in c['beats']], open(f'{H}/tts/lines.json', 'w'), indent=1)
