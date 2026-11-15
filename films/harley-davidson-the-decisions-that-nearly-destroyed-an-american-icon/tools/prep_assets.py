"""Brand Coroner · Case 008 · Harley-Davidson. Prepare still assets for the Blender build (PIL): graded photos, typeset filing/release
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

M83 = 'WHITE HOUSE MEMO · MOTORCYCLE IMPORTS · APR 1, 1983'
YK = 'REAGAN · REMARKS AT HARLEY-DAVIDSON, YORK, PA. · MAY 6, 1987'
P87 = 'PROCLAMATION 5727 · TERMINATION OF IMPORT RELIEF · OCT 9, 1987'
K25 = 'HARLEY-DAVIDSON, INC. FORM 10-K · FY2025 (FILED FEB 26, 2026)'
card('k25gen', K25,
     ['"Harley-Davidson was founded in 1903.', 'Harley-Davidson, Inc. was incorporated in 1981,', 'at which time it purchased the Harley-Davidson', 'motorcycle business from AMF Incorporated in a', 'management buyout. In 1986, Harley-Davidson,', 'Inc. became publicly held."'], w=1300, size=30,
     hl=[(0, 'founded in 1903'), (3, 'from AMF Incorporated'), (4, 'management buyout'), (5, 'became publicly held')])
card('m83', M83,
     ['"I will impose tariff increases of 45 percent', 'ad valorem in the first year, declining to 35,', '20, 15 and 10 percent above scheduled rates in', 'subsequent years."', '"The additional duties will apply to all imports', 'above the tariff-rate quotas."'], w=1300, size=30,
     hl=[(0, '45 percent'), (2, 'above scheduled rates'), (5, 'above the tariff-rate quotas')],
     foot=['heavyweight = engines over 700 cc · petition by harley-davidson motor co. and harley-davidson york', 'added on top of the existing tariff: percentage points,', 'not a 45% total rate'])
card('m83b', M83,
     ['"Imposition of these tariff increases should', 'allow the heavyweight motorcycle industry to', 'adjust to the threat of injury caused by', 'increased imports, which have raised', 'inventories to twice their normal level."'], w=1300, size=30,
     hl=[(2, 'adjust to the threat of injury'), (4, 'twice their normal level')])
card('york', YK,
     ['"You cut the hours of work needed to make a', 'motorcycle by one-third. You cut inventory by', 'two-thirds. You tripled the number of defect', 'free machines you shipped."', '"You expanded your product line from 3 models', '10 years ago to 24 today ..."'], w=1300, size=30,
     hl=[(0, 'cut the hours of work'), (1, 'cut inventory by'), (2, 'tripled the number of defect')], foot=['figures as stated by the president in his remarks · not an audited disclosure'])
card('union', YK,
     ['"The tariffs helped to slow up the imports, and', 'that helped us. But the backbone of our comeback', 'as a company is our people here."', '— Harry Smith, president, IAM Local 175,', '  as quoted by the president'], w=1300, size=30,
     hl=[(0, 'The tariffs helped'), (1, 'the backbone of our comeback')])
card('york2', YK,
     ['"Just a few weeks ago, a year ahead of', 'schedule, you said to us you didn\'t need any', 'more breathing room."'], w=1300, size=32, hl=[(0, 'a year ahead of'), (1, 'you didn\'t need any')])
card('p87', P87,
     ['"... the early termination of the heavyweight', 'motorcycles import relief as requested by', 'petitioner Harley-Davidson, Inc."', '"... during the period April 16, 1983, through', 'April 15, 1988."'], w=1300, size=30,
     hl=[(1, 'as requested by'), (4, 'April 15, 1988')],
     foot=['usitc report (inv. ta-203-17, jun 19, 1987): early termination "would have no significant', 'economic effect on the domestic industry"'])
card('macro', K25,
     ['"... a challenging economic environment,', 'including high-interest rates and depressed', 'consumer sentiment resulting from economic', 'uncertainty, continued to adversely impact', 'consumer demand for premium discretionary', 'products, including the Company\'s motorcycles."'], w=1300, size=30,
     hl=[(1, 'high-interest rates'), (2, 'consumer sentiment'), (4, 'premium discretionary')])
card('delay', 'HARLEY-DAVIDSON FORM 10-K · FY2025 · RISK FACTORS',
     ['"... high interest rates contributing to delays', 'in customers\' decisions to upgrade to new', 'models ..."'], w=1300, size=30, hl=[(0, 'contributing to delays')])
card('ship', K25,
     ['"HDMC shipped 124,477 motorcycles worldwide', 'during 2025, which was 16.4% lower than during', '2024. Shipments to dealers in 2025 were lower', 'than 2024 based on a planned decrease in', 'motorcycle shipments and softer than expected', 'retail demand ..."'], w=1300, size=30,
     hl=[(0, '124,477 motorcycles'), (1, '16.4% lower'), (3, 'planned decrease'), (4, 'softer than expected')])
card('retail', K25,
     ['"Worldwide retail sales of new Harley-Davidson', 'motorcycles decreased 12.4% during 2025', 'compared to 2024 ..."'], w=1300, size=30, hl=[(1, 'decreased 12.4%')],
     foot=['retail data comes from dealer reports, which the company "does not regularly verify"'])
card('hdmc', K25,
     ['"HDMC segment operating loss was $28.7 million', 'in 2025 compared to operating income of', '$277.8 million in 2024."', '"... lower motorcycle shipments ... unfavorable', 'manufacturing leverage ... the impact from new', 'or increased tariffs implemented in 2025 ..."'], w=1300, size=30,
     hl=[(0, 'operating loss was $28.7 million'), (2, '$277.8 million'), (4, 'manufacturing leverage'), (5, 'increased tariffs')])
card('hdfs', K25,
     ['"HDFS segment operating income was $490.4', 'million in 2025 compared to operating income', 'of $248.4 million in 2024."', '"Net income attributable to Harley-Davidson,', 'Inc. for 2025 was $338.7 million ..."'], w=1300, size=30,
     hl=[(0, '$490.4'), (4, '$338.7 million')],
     foot=['2025 hdfs income was lifted by the "hdfs transaction" (receivables sold);', 'the company guided hdfs 2026 operating income to $45–60 million'])
card('lw', K25,
     ['"LiveWire segment operating loss was $75.0', 'million in 2025 compared to an operating loss', 'of $109.6 million in 2024."', 'LiveWire motorcycle unit shipments:  653   612'], w=1300, size=30,
     hl=[(0, 'operating loss was $75.0'), (3, '653')], foot=['the 10-k reports 653 (2025) and 612 (2024) as unit shipments'])
card('k25b', K25,
     ['"Harley-Davidson, Inc. was incorporated in 1981,', 'at which time it purchased the Harley-Davidson', 'motorcycle business from AMF Incorporated in a', 'management buyout."'], w=1300, size=30,
     hl=[(2, 'from AMF Incorporated'), (3, 'management buyout')])
card('k25ipo', K25, ['"In 1986, Harley-Davidson, Inc. became publicly', 'held."'], w=1300, size=30, hl=[(0, 'became publicly')])
card('hog', K25, ['"... HARLEY OWNERS GROUP, H.O.G., the H.O.G.', 'Logo, SCREAMIN\' EAGLE, SOFTAIL and SPORTSTER."'], w=1300, size=30, hl=[(0, 'HARLEY OWNERS GROUP')],
     foot=['from the list of the company\'s trademarks'])
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

