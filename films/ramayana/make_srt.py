"""Narration subtitles → ramayana.srt (same timing as the burned-in subtitles)."""
import json, os, re
HERE = os.path.dirname(os.path.abspath(__file__))
dur = json.load(open(f'{HERE}/voices/dur.json'))
VO = [(m.group(1), float(m.group(2)), m.group(3)) for m in re.finditer(r"\['(\w+)', ([\d.]+), \"(.*?)\"\]", open(f'{HERE}/story.js').read())]
ts = lambda t: f"{int(t // 3600):02d}:{int(t % 3600 // 60):02d}:{int(t % 60):02d},{int(round((t % 1) * 1000)):03d}"
with open(f'{HERE}/ramayana.srt', 'w') as f:
    for i, (k, t0, txt) in enumerate(VO, 1):
        f.write(f"{i}\n{ts(t0)} --> {ts(t0 + max(1.8, dur[k] + .6))}\n{txt}\n\n")
print(len(VO), 'cues')
