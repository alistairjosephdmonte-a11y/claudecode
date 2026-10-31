"""audio/words.json (narration + word times) → film.json: sections, voice lines and one-line English subtitle cues."""
import json, re, os
D = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
W = json.load(open(f'{D}/audio/words.json'))
MAX = 62
def chunks(text):
    parts = re.findall(r'[^,.;:?!]+[,.;:?!]*\s*', text)
    out = []
    for p in parts:
        p = p.strip()
        while len(p) > MAX:                       # split long clause at the space nearest the middle
            sp = [m.start() for m in re.finditer(' ', p)]; c = min(sp, key=lambda s: abs(s - len(p) / 2)); out.append(p[:c]); p = p[c + 1:]
        if out and len(out[-1]) + 1 + len(p) <= MAX and not re.search(r'[.?!]$', out[-1]): out[-1] += ' ' + p
        else: out.append(p)
    return out
subs = []
CUT = {'s03': ('The room you are seeing is representative, and the people', 'The people')}   # trimmed in the mix: the film no longer shows a room
for L in W:
    ws = L['words']; text = L['text']
    if L['id'] in CUT:
        a, b = CUT[L['id']]; k = len(text[:text.index(a)].split()); n = len(a.split()) - len(b.split())
        L['cut'] = [ws[k][1] - .04, ws[k + n][1] - .04]; ws = ws[:k] + ws[k + n:]; text = text.replace(a, b); L['words'] = ws
    cs = chunks(text); i = 0
    for c in cs:
        n = len(c.split()); a = ws[min(i, len(ws) - 1)][1]; b = ws[min(i + n, len(ws)) - 1][2]; i += n
        subs.append([round(a - .05, 2), round(b + .25, 2), c])
k = 0
while k < len(subs) - 1:                           # merge cues too short to read (< 1.2 s) into the next one when the line fits
    if subs[k][1] - subs[k][0] < 1.2 and len(subs[k][2]) + 1 + len(subs[k + 1][2]) <= MAX and subs[k + 1][0] - subs[k][1] < 1.5:
        subs[k] = [subs[k][0], subs[k + 1][1], subs[k][2] + ' ' + subs[k + 1][2]]; del subs[k + 1]
    elif subs[k + 1][1] - subs[k + 1][0] < 1.2 and len(subs[k][2]) + 1 + len(subs[k + 1][2]) <= MAX and subs[k + 1][0] - subs[k][1] < 1.5:
        subs[k] = [subs[k][0], subs[k + 1][1], subs[k][2] + ' ' + subs[k + 1][2]]; del subs[k + 1]
    else: k += 1
for k in range(len(subs) - 1):                     # no overlaps; close tiny gaps inside a line
    if subs[k][1] > subs[k + 1][0] - .02: subs[k][1] = round(subs[k + 1][0] - .02, 2)
    elif subs[k + 1][0] - subs[k][1] < .35: subs[k][1] = round(subs[k + 1][0] - .02, 2)
SEC = {'open': [0, 4], 'title': [4, 10.5], 'place': [10.5, 30], 'accounts': [30, 80], 'store': [80, 120], 'scale': [120, 130], 'fees': [130, 160],
       'challenger': [160, 240], 'counter': [240, 330], 'third': [330, 370], 'squeeze': [370, 400], 'filing': [400, 420], 'back': [420, 450],
       'map': [450, 462], 'verdict': [462, 470], 'end': [470, 480]}
json.dump({'dur': 480, 'fps': 30, 'sections': SEC, 'voice': [[L['id'], L['t'], L.get('cut')] for L in W], 'subs': subs}, open(f'{D}/film.json', 'w'), indent=1)
print(len(subs), 'cues; longest', max(len(s[2]) for s in subs))
