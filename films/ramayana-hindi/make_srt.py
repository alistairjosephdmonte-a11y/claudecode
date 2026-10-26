"""events.json → ramayana-hindi.srt (Hindi subtitles timed to the narration)"""
import json, os
HERE = os.path.dirname(os.path.abspath(__file__))
ev = json.load(open(f'{HERE}/events.json'))['ev']; text = {l['id']: l['text'] for l in json.load(open(f'{HERE}/tts/lines.json'))}
f = lambda t: f'{int(t // 3600):02d}:{int(t % 3600 // 60):02d}:{int(t % 60):02d},{int(t * 1000 % 1000):03d}'
vo = [e for e in ev if e['type'] == 'vo']
open(f'{HERE}/ramayana-hindi.srt', 'w').write(''.join(f"{i + 1}\n{f(e['t'])} --> {f(e['t'] + e['d'] + .4)}\n{text[e['id']]}\n\n" for i, e in enumerate(vo)))
print(len(vo), 'cues')
