"""Brand Coroner · Case 014 · Target Canada. Prepare still assets for the Blender build (PIL): graded photos, typeset filing/release
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

PR11 = 'TARGET CORPORATION · PRESS RELEASE · JAN 13, 2011 · TRANSCRIPTION'
PR15 = 'TARGET CORPORATION · PRESS RELEASE · JAN 15, 2015 · TRANSCRIPTION'
CB = 'CANADIAN BUSINESS · "THE LAST DAYS OF TARGET" · JOE CASTALDO · JAN 2016'
K13 = 'TARGET FORM 10-K · FISCAL 2013 (FILED MAR 14, 2014) · TRANSCRIPTION'
K14 = 'TARGET FORM 10-K · FISCAL 2014 (FILED MAR 13, 2015) · TRANSCRIPTION'
card('zellers', PR11,
     ['"... it has agreed to pay C$1.825 billion to', 'purchase from Zellers Inc., a subsidiary of the', 'Hudson\'s Bay Company (HBC), the leasehold', 'interests in up to 220 sites currently', 'operated by Zellers Inc."'], w=1300, size=30,
     hl=[(0, 'C$1.825 billion'), (3, 'interests in up to 220 sites')], foot=['"target expects to open 100 to 150 target stores throughout canada in 2013 and 2014."'])
card('k13open', K13,
     ['"In fiscal 2013 we opened 124 Target stores in', 'Canada, which was our first retail store', 'expansion outside of the United States. Our', 'initial sales and operating results in Canada', 'have not met our initial expectations."'], w=1300, size=30,
     hl=[(0, 'opened 124 Target stores'), (4, 'have not met our initial expectations')], foot=['fiscal 2013 ended feb 1, 2014'])
card('dc', CB,
     ['"By fall of 2013, Target\'s three distribution', 'centres—approximately four million square feet', 'in all—were overflowing with goods."', '"Target Canada had ordered way more stock than', 'it could actually sell."'], w=1300, size=30,
     hl=[(2, 'were overflowing with goods'), (3, 'ordered way more stock')], foot=['based on interviews with former employees', '10-k: 3 canadian distribution centres, 3,963 thousand sq ft'])
card('paper', CB,
     ['"The merchandising department\'s software often', 'indicated items were in stock ..."', '"We\'d look on paper and think we\'re OK. Then', 'we\'d go to the store, and it\'s like, \'Oh my', 'god.\'" — a former employee'], w=1300, size=30,
     hl=[(1, 'indicated items were in stock'), (2, 'think we\'re OK')])
card('data', CB,
     ['"Product dimensions would be in inches, not', 'centimetres or entered in the wrong order ..."', '"... the system couldn\'t notify users about', 'data entry errors. The investigative team', 'estimated information in the system was', 'accurate about 30% of the time. In the U.S.,', 'it\'s between 98% and 99%."'], w=1300, size=30,
     hl=[(0, 'Product dimensions'), (2, 'couldn\'t notify users'), (5, 'accurate about 30% of the time')], foot=['an internal team\'s estimate, as reported · not a company disclosure'])
card('sync', CB,
     ['"Manhattan, the company\'s warehouse software,', 'and SAP weren\'t communicating properly."', '"Stores might end up with an abundance of some', 'products and a dearth of others."', '"Items wouldn\'t scan, or the POS returned the', 'incorrect price."'], w=1300, size=30,
     hl=[(1, 'weren\'t communicating properly'), (2, 'an abundance of some'), (4, 'Items wouldn\'t scan')], foot=['pos = point-of-sale (checkout) system'])
card('price', 'THE ASSOCIATED PRESS · APR 7, 2014 · TRANSCRIPTION (EXCERPT)',
     ['"The company said prices are in line with those', 'of rivals in Canada, including Wal-Mart, and in', 'some cases are lower. But it acknowledges', 'they\'re generally higher than at its U.S.', 'stores."'], w=1300, size=30,
     hl=[(0, 'in line with those'), (3, 'generally higher than at its U.S.')],
     foot=['ceo gregg steinhafel: "that would be like comparing prices in boston to', 'what we have in rural iowa."'])
card('reuters', 'REUTERS · FACTBOX · MAY 8, 2014 · TRANSCRIPTION (EXCERPT)',
     ['"Canadian shoppers have said they are', 'disappointed that prices at Target\'s Canadian', 'stores are higher than they are in stores in', 'the United States."'], w=1300, size=30, hl=[(1, 'disappointed')])
card('forum', 'CBC NEWS · AUG 19, 2013 · FORUM RESEARCH SURVEY · TRANSCRIPTION',
     ['"Only 27 per cent of Target customers said they', 'were \'very satisfied\' with their shopping', 'experience, down from 32 per cent in the', 'spring."'], w=1300, size=30,
     hl=[(0, 'Only 27 per cent'), (2, 'down from 32 per cent')], foot=['ivr telephone survey, aug 14, 2013 · 1,578 randomly selected canadians 18+'])
card('breach', CB,
     ['"A month prior, Target had disclosed a massive', 'security breach ... Combined with the bleeding', 'operations in Target Canada, Steinhafel\'s', 'position was untenable, and he stepped down', 'in May."'], w=1300, size=30,
     hl=[(1, 'security breach'), (3, 'he stepped down')], foot=['may 2014 · target canada president tony fisher left two weeks later (canadian business)'])
card('cornell', K14,
     ['Brian C. Cornell', 'Chairman of the Board and Chief Executive', 'Officer since August 2014.'], w=1300, size=30, bold=(0,),
     hl=[(2, 'since August 2014')], foot=['first ceo hired from outside the company (mpr news, jul 31, 2014)'])
card('quote', PR15,
     ['"... we were unable to find a realistic', 'scenario that would get Target Canada to', 'profitability until at least 2021."', '— Brian Cornell, Chairman and CEO'], w=1300, size=32,
     hl=[(0, 'unable to find a realistic'), (2, 'until at least 2021')])
card('holiday', PR15,
     ['"We hoped that these efforts in Canada would', 'lead to a successful holiday season, but we', 'did not see the required step-change in our', 'holiday performance," said Cornell.'], w=1300, size=30, hl=[(2, 'did not see the required step-change')])
card('ccaa', PR15,
     ['"... Target Canada filed an application for', 'protection under the Companies\' Creditors', 'Arrangement Act (the \'CCAA\') ..."', '"Target Canada currently has 133 stores across', 'the country and employs approximately 17,600', 'people."'], w=1300, size=30,
     hl=[(1, 'Companies\' Creditors'), (3, '133 stores'), (4, 'approximately 17,600')])
card('trust', PR15,
     ['"... cash contributions of C$70 million', '(approximately US$59 million) into an Employee', 'Trust ... nearly all Target Canada-based', 'employees receive a minimum of 16 weeks of', 'compensation, including wages and benefits ..."'], w=1300, size=30,
     hl=[(0, 'C$70 million'), (3, 'a minimum of 16 weeks')], foot=['subject to court approval'])
card('k14', K14,
     ['"... we deconsolidated the Canada Subsidiaries', 'effective January 15, 2015, resulting in a', 'pretax impairment loss on deconsolidation and', 'other charges, collectively totaling $5.1', 'billion."'], w=1300, size=30,
     hl=[(2, 'pretax impairment loss'), (3, 'collectively totaling $5.1')], foot=['the jan 15, 2015 release estimated "$5.4 billion of pre-tax losses on discontinued operations",', 'which also counts quarter-to-date operating losses'])
card('closed', CB,
     ['"All 133 stores closed by April."'], w=1300, size=32, hl=[(0, 'All 133 stores closed by April.')], foot=['april 2015'])
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

# ── store grids for scene 04: one pilot store vs the 124-store network (drawn at 2×) ──
def grid(name, n, cols, r=11, gap=34, col=RED, X=2):
    rows = (n + cols - 1) // cols; im = Image.new('RGBA', ((cols * gap) * X, (rows * gap) * X), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    for k in range(n):
        cx, cy = (k % cols * gap + gap / 2) * X, (k // cols * gap + gap / 2) * X; d.ellipse((cx - r * X, cy - r * X, cx + r * X, cy + r * X), fill=col + (255,))
    im.save(os.path.join(A, f'{name}.png'))
grid('grid124', 124, 20); grid('grid1', 1, 1)
print('grids ok')
