"""Brand Coroner · Case 013 · New Coke. Prepare still assets for the Blender build (PIL): graded photos, typeset filing/release
transcriptions (cards, not facsimiles), dots and arrowheads. Writes assets/*.png and assets/layout.json
(highlight boxes measured in the same fonts, so Blender can place red highlight strips exactly)."""
import json, os, subprocess
from PIL import Image, ImageDraw, ImageFont, ImageOps, ImageEnhance, ImageFilter
D = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
A = os.path.join(D, 'assets'); os.makedirs(A, exist_ok=True)
FONT = lambda n, s: ImageFont.truetype(os.path.join(D, 'fonts', n + '.ttf'), s)
INK, PAPER, RED, GREY = (245, 243, 239), (21, 21, 21), (255, 36, 0), (133, 133, 133)
import random
LAY = {}


# ── photos: documentary grade (greyscale or muted colour, light grain). CC BY-SA photos ("sa") are left unaltered: only resized.
PH = json.load(open(os.path.join(D, 'photos.json')))
def grade(name, crop=None, maxw=3840, keep_color=False, sa=False):
    src = os.path.join(D, 'raw', name + '.img')
    if not os.path.exists(src) or 'image' not in subprocess.run(['file', '-b', src], capture_output=True, text=True).stdout: print('missing', name); return None
    im = Image.open(src).convert('RGB'); im.thumbnail((maxw, maxw))
    if sa: im.save(os.path.join(A, f'ph_{name}.png')); return im.size
    if crop: w, h = im.size; im = im.crop((int(crop[0] * w), int(crop[1] * h), int(crop[2] * w), int(crop[3] * h)))
    g = ImageOps.grayscale(im) if not keep_color else im
    g = ImageEnhance.Contrast(g).enhance(1.12); g = ImageEnhance.Brightness(g).enhance(.94)
    if keep_color: g = ImageEnhance.Color(g).enhance(.8)
    n_ = Image.effect_noise(g.size, 18).filter(ImageFilter.GaussianBlur(.6)).convert(g.mode); g = Image.blend(g, n_, .04)
    g.convert('RGB').save(os.path.join(A, f'ph_{name}.png')); return g.size
for n, spec in PH.items():
    r = grade(n, spec.get('crop'), keep_color=spec.get('color', False), sa=spec.get('sa', False))
    if r: LAY['ph_' + n] = r

def card(name, head, lines, w=1500, size=34, font='mono400', hl=(), pad=56, lh=1.55, foot=None, bold=(), X=2):
    """flat editorial transcription card (charcoal, not a facsimile), drawn at X× for the 4K master"""
    w, size, pad = w * X, size * X, pad * X
    f = FONT(font, size); fb = FONT('mono600', size); hf = FONT('mono600', 22 * X); ff = FONT('mono400', 20 * X)
    h = int(pad * 2 + 70 * X + len(lines) * size * lh + (len(foot) * 30 * X + 30 * X if foot else 0))
    im = Image.new('RGB', (w, h), PAPER); d = ImageDraw.Draw(im); d.rectangle((0, 0, w - 1, h - 1), outline=(43, 43, 43), width=2 * X)
    d.text((pad, pad - 6 * X), head + ' · NOT A FACSIMILE', font=hf, fill=GREY); d.line((pad, pad + 32 * X, w - pad, pad + 32 * X), fill=(60, 60, 60), width=2 * X)
    top = pad + 70 * X; boxes = []
    for i, l in enumerate(lines):
        y = top + i * size * lh; d.text((pad, y), l, font=fb if i in bold else f, fill=INK)
    for (li, sub) in hl:
        l = lines[li]; a = l.index(sub); x0 = pad + d.textlength(l[:a], font=f); x1 = pad + d.textlength(l[:a + len(sub)], font=f); y = top + li * size * lh
        boxes.append([x0 - 6 * X, y - 4 * X, x1 + 6 * X, y + size * 1.18])
    if foot:
        y = top + len(lines) * size * lh + 10 * X; d.line((pad, y, w - pad, y), fill=(60, 60, 60), width=X)
        for j, l in enumerate(foot): d.text((pad, y + 16 * X + j * 30 * X), l, font=ff, fill=GREY)
    im.save(os.path.join(A, f'doc_{name}.png')); LAY['doc_' + name] = [w, h]; LAY['hl_' + name] = boxes

T85 = "TIME · \"FIDDLING WITH THE REAL THING\" · MAY 6, 1985 · TRANSCRIPTION"
KO = "THE COCA-COLA COMPANY · COMPANY HISTORY · TRANSCRIPTION (EXCERPT)"
card('ann', T85,
     ['"This is the first flavor change in 99 years', 'for the world\'s biggest-selling soda, and', 'Coke called it \'the most significant', 'soft-drink development in the company\'s', 'history.\'"'], w=1300, size=30,
     hl=[(0, 'first flavor change in 99 years'), (2, 'the most significant')], foot=['byline: john s. demott'])
card('share', T85,
     ['"In 1972 it started the Pepsi Challenge, which', 'pitted the two colas against each other in', 'blind testing."', '"Coke\'s share of the U.S. market last year', 'slipped from 22.5% to 21.7%, while Pepsi\'s', 'went to 18.8% ..."'], w=1300, size=30,
     hl=[(0, 'Pepsi Challenge'), (2, 'blind testing'), (4, 'slipped from 22.5% to 21.7%')], foot=['"last year" = 1984'])
card('lead', KO,
     ['"In 1985, The Coca-Cola Company\'s share lead', 'over its chief competitor, in its flagship', 'market, with its flagship product, had been', 'slowly slipping for 15 consecutive years."'], w=1300, size=30,
     hl=[(3, 'slowly slipping for 15 consecutive years')], foot=['"new coke: the most memorable marketing blunder ever?" · coca-colacompany.com'])
card('tests', T85,
     ['"From 1981 to 1984 in 25 cities in the U.S.', 'and Canada, Coke tested the taste on more', 'than 190,000 consumers. The new Coke flavor', 'beat the old one by 55% to 45%. When those', 'same people were told what they were tasting,', 'their preference for the new flavor was even', 'more pronounced, 61% to 39%."'], w=1300, size=30,
     hl=[(0, '25 cities in the U.S.'), (2, '190,000 consumers'), (3, '55% to 45%'), (6, '61% to 39%')],
     foot=['the company\'s own history says "nearly 200,000 consumers"'])
card('pepsi', T85,
     ['Roger Enrico, president of Pepsi-Cola U.S.A.:', '"The Real Thing is in real trouble."', '"... Pepsi gave all employees the day off', 'last Friday."'], w=1300, size=30,
     hl=[(1, 'The Real Thing is in real trouble.'), (2, 'gave all employees the day off')],
     foot=['pepsi newspaper ad, as quoted by history.com: "the other guy just blinked"'])
card('stock', KO,
     ['"A man in San Antonio, Texas, drove to a local', 'bottler and bought $1,000 worth of Coca-Cola."', '"Protesters at a Coca-Cola event in downtown', 'Atlanta in May carried signs with \'We want the', 'real thing\' and \'Our children will never know', 'refreshment.\'"'], w=1300, size=30,
     hl=[(1, '$1,000 worth of Coca-Cola'), (3, 'Atlanta in May'), (3, 'We want the')])
card('mullins', 'TIME · "ALL AFIZZ OVER THE NEW COKE" · JUNE 24, 1985 · TRANSCRIPTION',
     ['"Gay Mullins, 57, ... has formed an association', 'in Seattle called the Old Cola Drinkers of', 'America."', '"After receiving 60,000 calls, the line was', 'disconnected last week."'], w=1300, size=30,
     hl=[(1, 'Old Cola Drinkers of'), (3, '60,000 calls')], foot=['the protest group\'s own hotline, not coca-cola\'s'])
card('calls', KO,
     ['"By June 1985, The Coca-Cola Company was', 'getting 1,500 calls a day on its consumer', 'hotline, compared with 400 a day before the', 'taste change."'], w=1300, size=30,
     hl=[(1, '1,500 calls a day'), (2, '400 a day before')], foot=['other accounts give higher daily totals · these are the company\'s figures'])
card('keough', 'DONALD KEOUGH, PRESIDENT · PRESS CONFERENCE · JULY 11, 1985',
     ['"The simple fact is that all of the time and', 'money and skill poured into consumer research', 'on a new Coca-Cola could not measure or reveal', 'the depth and abiding emotional attachment to', 'original Coca-Cola felt by so many people."'], w=1300, size=30,
     hl=[(2, 'could not measure or reveal'), (3, 'emotional attachment')], foot=['as quoted by cbs news (2015) · history.com quotes "the deep and abiding"'])
card('back', KO,
     ['"In just two days after the announcement of', 'Coca-Cola classic, The Coca-Cola Company', 'received 31,600 telephone calls on the', 'hotline."'], w=1300, size=30, hl=[(2, '31,600 telephone calls')])
card('two', KO,
     ['"Coca-Cola classic was sold alongside', 'Coca-Cola (\'new Coke\'), and the two brands had', 'distinct advertising campaigns ..."', '"Later, the name of the new taste of Coca-Cola', 'was changed to Coke II; the product is no', 'longer available in the United States."'], w=1300, size=30,
     hl=[(0, 'sold alongside'), (2, 'distinct advertising campaigns'), (4, 'Coke II')], foot=['renamed in 1990 (history.com)'])
card('smart', 'DONALD KEOUGH · AS QUOTED BY HISTORY.COM (2015)',
     ['"Some cynics say that we planned the whole', 'thing ... The truth is we\'re not that dumb', 'and we\'re not that smart."'], w=1300, size=32,
     hl=[(0, 'we planned the whole'), (1, "we're not that dumb"), (2, "we're not that smart")])
card('goiz95', KO,
     ['"We set out to change the dynamics of sugar', 'colas in the United States, and we did exactly', 'that -- albeit not in the way we had planned,"', 'then chairman and chief executive officer', 'Roberto Goizueta said in 1995 ...'], w=1300, size=30,
     hl=[(2, 'not in the way we had planned')])
card('bond', KO,
     ['"... adopting a formula preferred in taste', 'tests of nearly 200,000 consumers. What these', 'tests didn\'t show, of course, was the bond', 'consumers felt with their Coca-Cola ..."'], w=1300, size=30,
     hl=[(1, 'nearly 200,000 consumers'), (2, 'the bond')])
# ── small graphics ──
def dot(name, r, col, ring=False, w=4):
    s = r * 2 + 8; im = Image.new('RGBA', (s * 4, s * 4), (0, 0, 0, 0)); d = ImageDraw.Draw(im); c = s * 2
    if ring: d.ellipse((c - r * 4, c - r * 4, c + r * 4, c + r * 4), outline=col + (255,), width=w * 4)
    else: d.ellipse((c - r * 4, c - r * 4, c + r * 4, c + r * 4), fill=col + (255,))
    im = im.resize((s, s), Image.LANCZOS); im.save(os.path.join(A, f'{name}.png'))
dot('dot_red', 9, RED); dot('dot_white', 8, (245, 243, 239)); dot('ring_red', 60, RED, ring=True, w=3); dot('dot_grey', 7, GREY)
ar = Image.new('RGBA', (120, 120), (0, 0, 0, 0)); ImageDraw.Draw(ar).polygon([(10, 20), (110, 60), (10, 100)], fill=RED + (255,)); ar.resize((30, 30), Image.LANCZOS).save(os.path.join(A, 'arrow_red.png'))
ar = Image.new('RGBA', (120, 120), (0, 0, 0, 0)); ImageDraw.Draw(ar).polygon([(10, 20), (110, 60), (10, 100)], fill=(245, 243, 239, 255)); ar.resize((30, 30), Image.LANCZOS).save(os.path.join(A, 'arrow_white.png'))
for d_, poly in {'r': [(10, 20), (110, 60), (10, 100)], 'l': [(110, 20), (10, 60), (110, 100)], 'u': [(20, 110), (60, 10), (100, 110)], 'd': [(20, 10), (60, 110), (100, 10)]}.items():
    for nm_, col in (('red', RED), ('grey', GREY)):
        ar = Image.new('RGBA', (120, 120), (0, 0, 0, 0)); ImageDraw.Draw(ar).polygon(poly, fill=col + (255,)); ar.resize((30, 30), Image.LANCZOS).save(os.path.join(A, f'arrow_{nm_}_{d_}.png'))
# vignette
v = Image.new('L', (1920, 1080), 0); dv = ImageDraw.Draw(v)
for i in range(60): dv.ellipse((-300 + i * 9, -260 + i * 6, 2220 - i * 9, 1340 - i * 6), fill=int(255 * (i / 60) ** .5))
v = v.filter(ImageFilter.GaussianBlur(60)); vig = Image.new('RGBA', (1920, 1080), (0, 0, 0, 0)); vig.putalpha(ImageOps.invert(v).point(lambda p: int(p * .55))); vig.save(os.path.join(A, 'vignette.png'))
json.dump(LAY, open(os.path.join(A, 'layout.json'), 'w'), indent=1)
print('assets ok', len(LAY))

# ── line overlays (drawn at 2× for the 4K master; revealed left→right in Blender by animating the crop) ──
def overlay(name, segs, X=2):
    im = Image.new('RGBA', (1920 * X, 1080 * X), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    for (pts, col, w) in segs: d.line([(x * X, y * X) for x, y in pts], fill=col + (255,), width=w * X, joint='curve')
    im.save(os.path.join(A, f'ov_{name}.png'))
print('overlays ok')
