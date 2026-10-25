"""Write tts/lines.json from script.py and synthesize voices/ (Kokoro, hf_alpha, en-us)."""
import json, os, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE); LIB = os.path.abspath(f'{ROOT}/../..')
sys.path.insert(0, HERE); from script import LINES
VOICE = os.environ.get('VOICE', 'hf_alpha')
lines = [{'id': i, 'text': say or text, 'sub': text, 'voice': VOICE, 'speed': .92, 'lang': 'en-us', 'asr': text} for i, text, say in LINES]
json.dump(lines, open(f'{HERE}/lines.json', 'w'), indent=1, ensure_ascii=False)
subprocess.run([f'{LIB}/.venv/bin/python', f'{LIB}/core/tts/tts.py', f'{HERE}/lines.json', f'{ROOT}/voices'], check=True)
