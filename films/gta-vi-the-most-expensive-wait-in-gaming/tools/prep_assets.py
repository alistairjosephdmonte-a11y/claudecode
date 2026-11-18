"""Brand Coroner · Case 010 · GTA VI. Prepare still assets for the Blender build (PIL): graded photos, typeset filing/release
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

K26 = 'TAKE-TWO FORM 10-K · FISCAL 2026 (YEAR TO MAR 31, 2026)'
Q26 = 'TAKE-TWO FORM 10-Q · QUARTER TO SEP 30, 2026'
PRES = 'TAKE-TWO INVESTOR PRESENTATION · MAY 2026'
card('rev', K26,
     ['"... our Grand Theft Auto products in particular', 'have historically accounted for a significant', 'portion of our revenue. Sales of Grand Theft', 'Auto products generated 12.4% of our net', 'revenue for the fiscal year ended March 31,', '2026."'], w=1300, size=30,
     hl=[(1, 'significant'), (3, '12.4% of our net')], foot=['existing gta products only: gta vi had not been released'])
card('gta5', PRES,
     ['GRAND THEFT AUTO V', '• Nearly 230 million units sold-in to date', '• Released across an unprecedented three', '  console generations', '• Reached $1 billion in retail sales faster', '  than any entertainment release in history'], w=1300, size=30, bold=(0,),
     hl=[(1, 'Nearly 230 million units sold-in'), (2, 'three'), (4, '$1 billion in retail sales faster')],
     foot=['"sold-in" = units shipped into distribution, not copies bought by players', 'retail sales = consumer spending at retail, not take-two revenue'])
card('strat', K26,
     ['"Rockstar Games\' strategy is to develop a', 'limited number of titles that are known for', 'their quality and longevity in the market for', 'which they can create sequels and incremental', 'revenue opportunities through virtual currency,', 'add-on content, and in-game purchases ..."'], w=1300, size=30,
     hl=[(1, 'limited number of titles'), (2, 'quality and longevity'), (3, 'incremental')],
     foot=['"software titles published by our rockstar games label are primarily internally developed."'])
card('online', PRES,
     ['GRAND THEFT AUTO ONLINE', '• Ever-changing world, driven by the regular', '  release of free updates', '• Free with every copy of Grand Theft Auto V', '• Standalone version launched March 15, 2022', '• Successfully launched GTA+ membership', '  program in March 2022'], w=1300, size=30, bold=(0,),
     hl=[(1, 'Ever-changing world'), (5, 'GTA+ membership')])
card('trailer', PRES,
     ['"As a YouTube exclusive, Trailer 1 broke the', 'record for biggest non-music video debut on', 'the platform at over 93 million views in 24', 'hours."'], w=1300, size=30,
     hl=[(1, 'biggest non-music video debut'), (2, '93 million views in 24')], foot=['trailer 1: december 2023 · views measure attention, not sales'])
card('delay', 'ROCKSTAR GAMES NEWSWIRE · NOV 6, 2025',
     ['"Grand Theft Auto VI will now release on', 'Thursday, November 19, 2026. We are sorry for', 'adding additional time to what we realize has', 'been a long wait, but these extra months will', 'allow us to finish the game with the level of', 'polish you ..."'], w=1300, size=30,
     hl=[(1, 'November 19, 2026'), (1, 'We are sorry'), (5, 'polish')], foot=['excerpt as published on rockstargames.com'])
card('timing', K26,
     ['"Our financial results are affected by the', 'timing of our product releases and the', 'commercial success of our titles."', '"The timing of our Grand Theft Auto product', 'releases may affect our financial performance', 'on a quarterly and annual basis."'], w=1300, size=30,
     hl=[(1, 'timing of our product releases'), (2, 'commercial success'), (4, 'may affect our financial performance')])
card('extended', Q26,
     ['"The label has released several trailers and', 'other marketing content for the title,', 'including an Extended Look that debuted on', 'Netflix, which featured nearly 30 minutes of', 'gameplay footage."'], w=1300, size=30, hl=[(2, 'Extended Look'), (3, 'nearly 30 minutes')])
card('price', 'ROCKSTAR GAMES / TAKE-TWO · PRESS RELEASE · JUN 24, 2026',
     ['"... pre-orders for Grand Theft Auto VI will', 'begin on June 25, 2026, at midnight local time."', '"Launching November 19, 2026, for the', 'PlayStation 5 ... and Xbox Series X|S ... for', '$79.99 ..."', '"... Ultimate Edition ... will be available', 'for $99.99."'], w=1300, size=30,
     hl=[(1, 'June 25, 2026'), (3, 'PlayStation 5'), (3, 'Xbox Series X|S'), (4, '$79.99'), (6, '$99.99')], foot=['u.s. prices · no pc version is named in the release'])
card('preord', Q26,
     ['"Pre-orders for the title commenced in June', '2026, generating initial demand that has', 'outpaced historical benchmarks for the series."'], w=1300, size=32,
     hl=[(1, 'initial demand'), (2, 'outpaced historical benchmarks')], foot=['no pre-order units or revenue are disclosed · pre-orders are not completed sales'])
card('risk', K26 + ' · RISK FACTORS',
     ['• We are dependent on the timing of our', '  product releases', '• We are dependent on the future success of', '  our Grand Theft Auto products and other hit', '  titles', '"Our business is driven by hit titles, which', 'require increasing budgets for development', 'and marketing."'], w=1300, size=30,
     hl=[(0, 'timing of our'), (2, 'future success of'), (6, 'increasing budgets')], foot=['no development budget for gta vi is disclosed'])
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

