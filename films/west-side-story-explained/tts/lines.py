import json, os
H = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
S = json.load(open(f'{H}/story.json'))
json.dump([{'id': i, 'text': t, 'voice': 'am_michael', 'speed': 1.0} for i, t in S['lines']], open(f'{H}/tts/lines.json', 'w'), indent=1)
