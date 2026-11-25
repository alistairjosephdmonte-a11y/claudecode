"""Brand Coroner · Case 011 · Juicero. Prepare still assets for the Blender build (PIL): graded photos, typeset filing/release
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

B17 = 'BLOOMBERG · APR 2017 (VIA THE INDIAN EXPRESS)'
card('fund', B17,
     ['"Google\'s venture capital arm and other', 'backers poured about $120 million into the', 'startup. Juicero sells the machine for $400,', 'plus the cost of individual juice packs', 'delivered weekly."'], w=1300, size=30,
     hl=[(1, 'about $120 million'), (2, 'machine for $400')], foot=['capital raised, not money lost · crunchbase (via foodnavigator): $118.5m in four rounds'])
card('squeeze', B17,
     ['"In Bloomberg\'s squeeze tests, hands did the', 'job quicker, but the device was slightly more', 'thorough. Reporters were able to wring 7.5', 'ounces of juice in a minute and a half. The', 'machine yielded 8 ounces in about two', 'minutes."'], w=1300, size=30,
     hl=[(0, 'hands did the'), (1, 'slightly more'), (2, '7.5'), (3, 'a minute and a half'), (4, '8 ounces'), (5, 'minutes')], foot=['results from one reported demonstration, not a lab test'])
card('qr', B17,
     ['"The device also reads a QR code printed on', 'the back of each produce pack and checks the', 'source against an online database to ensure', 'the contents haven\'t expired or been', 'recalled ..."'], w=1300, size=30,
     hl=[(0, 'reads a QR code'), (2, 'online database'), (3, 'expired')], foot=['as described by a person close to the company'])
card('evans', B17,
     ['"Doug Evans, the company\'s founder ..."', '"In 2002, Evans helped start Organic Avenue,', 'a chain of juice bars selling cold-press', 'concoctions in glass jars."'], w=1300, size=30,
     hl=[(0, 'Doug Evans'), (1, 'Organic Avenue')])
card('investors', 'BLOOMBERG · SEP 1, 2017 (VIA MYSANANTONIO)',
     ['"Alphabet\'s venture arm GV, Kleiner Perkins', 'Caufield & Byers, Artis Ventures and Josh', 'Kushner\'s Thrive Capital are among the', 'startups [sic] investors."'], w=1300, size=30,
     hl=[(0, 'GV'), (0, 'Kleiner Perkins')], foot=['campbell soup company: listed by crunchbase, via foodnavigator-usa, sep 5, 2017', 'no single investor is reported to have put in $120 million'])
card('launch', 'FORTUNE · JAN 17, 2017',
     ['"San Francisco-based startup Juicero got a lot', 'of flak when it launched its cold-press', 'juicer in the spring of 2016."', '"... a $699 connected device ..."'], w=1300, size=30,
     hl=[(2, 'spring of 2016'), (3, '$699 connected device')], foot=['launch month reported as march (wikipedia) or april 2016 (company release, bevnet)'])
card('packs', 'FOODNAVIGATOR-USA · SEP 5, 2017',
     ['"... a refrigerated pack of finely chopped', 'fresh organic fruits and veggies ..."', '"The price tag per produce pack ($5-7', 'depending on the juice) ..."'], w=1300, size=30,
     hl=[(0, 'refrigerated pack'), (2, 'per produce pack ($5-7')])
card('teardown', 'ARS TECHNICA · SEP 1, 2017',
     ['"... a third-party teardown showed that the', 'Juicero press was a complex machine with many', 'specially made parts, which likely made the', 'machine as expensive to produce as it was for', 'a customer to buy."'], w=1300, size=30,
     hl=[(1, 'complex machine'), (2, 'specially made parts')], foot=['"likely" is ars technica\'s assessment · no manufacturing cost is verified'])
card('dunn', 'BLOOMBERG · APR 21, 2017 (VIA THE INDIAN EXPRESS)',
     ['"Dunn wrote in a blog post Thursday that the', 'Juicero device provides quality control,', 'consistency and data to the juice-squeezing', 'process that hands cannot."'], w=1300, size=30,
     hl=[(1, 'quality control,'), (2, 'consistency and data')], foot=['owners could send the machine back for a refund for 30 days'])
card('dunnq', 'JEFF DUNN, CEO · APR 2017 (QUOTED BY SELF)',
     ['"The value of Juicero is more than a glass of', 'cold-pressed juice—much more."'], w=1300, size=32, hl=[(0, 'more than a glass of')])
card('july', 'FORTUNE · JUL 14, 2017 · CEO LETTER TO STAFF',
     ['"... the current prices of $399 for the Press', 'and $5 – $7 for produce Packs are not a', 'realistic way for us to fulfill our mission at', 'the scale to which we aspire."'], w=1300, size=30,
     hl=[(0, '$399 for the Press'), (2, 'realistic way')],
     foot=['plan: lay off about 25% of staff, mainly sales and marketing', 'next press: "in the $200 range" (fortune source) · "under $200" (ars technica) · not launched'])
card('shut', 'JUICERO STATEMENT · SEP 1, 2017 (QUOTED BY ARS TECHNICA)',
     ['"[A]fter selling over a million Produce Packs,', 'we must let you know that we are suspending', 'the sale of the Juicero Press and Produce', 'Packs immediately."'], w=1300, size=30,
     hl=[(0, 'over a million Produce Packs'), (1, 'suspending')], foot=['bloomberg: refunds on presses "for the next 90 days" · company seeks a buyer'])
card('infra', 'JUICERO LETTER · SEP 1, 2017 (QUOTED BY FOODNAVIGATOR-USA)',
     ['"It became clear that creating an effective', 'manufacturing and distribution system for a', 'nationwide customer base requires', 'infrastructure that we cannot achieve on our', 'own as a standalone business."'], w=1300, size=30,
     hl=[(1, 'manufacturing and distribution system'), (3, 'infrastructure'), (4, 'standalone business')])
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

