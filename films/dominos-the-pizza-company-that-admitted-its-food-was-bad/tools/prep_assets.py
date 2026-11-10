"""Brand Coroner · Case 012 · Domino's. Prepare still assets for the Blender build (PIL): graded photos, typeset filing/release
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

card('dec09', "DOMINO'S PIZZA · PRESS RELEASE · DEC 16, 2009 · TRANSCRIPTION",
     ['"A garlic seasoned crust with parsley baked', 'to a golden brown"', '"Sweeter, bolder tomato sauce with a medley', 'of herbs and a red pepper kick"',
      '"Shredded cheese made with 100% real mozzarella', 'and flavored with just a hint of provolone"', '"... will be in all U.S. stores beginning', 'December 27."'], w=1150, size=30,
     hl=[(0, 'garlic seasoned crust'), (2, 'bolder tomato sauce'), (4, 'Shredded cheese'), (7, 'December 27')],
     foot=['headline: "celebrating 50th year, domino\'s pizza gives itself a makeover"'])
card('keys', 'REUTERS · DEC 16, 2009 · TRANSCRIPTION (EXCERPT)',
     ['"Research firm Brand Keys said Domino\'s is', 'the No. 1 ranked pizza chain overall, but that', 'when it comes to taste it is tied for last', 'place with children\'s pizza party chain', 'Chuck E. Cheese."'], w=1150, size=30,
     hl=[(1, 'No. 1 ranked pizza chain overall'), (2, 'when it comes to taste'), (2, 'tied for last')], foot=['as published by nbc news'])
card('ad', "SLATE · AD REPORT CARD · JAN 11, 2010 · QUOTING THE TV SPOT",
     ['"Domino\'s pizza crust to me is like cardboard"', '"The sauce tastes like ketchup."'], w=1150, size=32,
     hl=[(0, 'like cardboard'), (1, 'like ketchup')], foot=['customer comments read aloud in the pizza turnaround ad (crispin porter + bogusky)'])
card('k09', "DOMINO'S PIZZA, INC. · FORM 10-K · FISCAL 2010 · TRANSCRIPTION",
     ['"In the fourth quarter of 2009, we introduced', 'our improved pizza recipe, which was a change', 'to our core pizza recipe."', '"We also created a new website,', 'www.pizzaturnaround.com ..."'], w=1150, size=30,
     hl=[(1, 'improved pizza recipe'), (2, 'core pizza recipe'), (4, 'www.pizzaturnaround.com')])
card('q1', "DOMINO'S PIZZA · Q1 2010 RESULTS · MAY 4, 2010 · TRANSCRIPTION",
     ['Same store sales growth          Q1 2010', 'Domestic Company-owned stores    +14.7%', 'Domestic franchise stores        +14.2%', 'Domestic stores                  +14.3%',
      '"... increased store traffic from the', 'successful introduction of its New and', 'Inspired Pizza."'], w=1150, size=30,
     hl=[(1, '+14.7%'), (2, '+14.2%'), (3, '+14.3%'), (4, 'increased store traffic')], foot=['versus the prior-year period · quarter ended march 28, 2010'])
card('q23', "DOMINO'S PIZZA · Q2 & Q3 2010 RESULTS · TRANSCRIPTION",
     ['Domestic stores · same store sales growth', '  Q2 2010 (release, July 27, 2010)    +8.8%', '  Q3 2010 (release, Oct 19, 2010)    +11.7%'], w=1150, size=30,
     hl=[(1, '+8.8%'), (2, '+11.7%')], foot=['a year earlier: q2 2009 −0.7% · q3 2009 0.0%'])
card('k10', "DOMINO'S PIZZA, INC. · FORM 10-K · FISCAL 2010 · TRANSCRIPTION",
     ['"Currently, on average, nearly 25% of our', 'domestic stores\' sales originate online."'], w=1150, size=30,
     hl=[(0, 'on average, nearly 25%')], foot=['an average across stores · the filing does not publish the store-by-store spread'])
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
