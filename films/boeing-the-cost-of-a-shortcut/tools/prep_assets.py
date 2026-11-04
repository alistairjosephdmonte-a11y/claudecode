"""Prepare still assets for the Blender build (PIL): graded photos, the real Chapter 11 petition page, typeset filing
transcriptions (paper cards), the world map, dots/rings/arrowheads. Writes assets/*.png and assets/layout.json
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

card('eo', 'FAA · EMERGENCY ORDER OF PROHIBITION · MARCH 13, 2019 · TRANSCRIPTION (TITLE)',
     ['Emergency Order of Prohibition:', 'Operators of Boeing Company Model 737-8 and', 'Boeing Company Model 737-9 Airplanes'], w=1100, size=30, bold=(0,), hl=[(0, 'Emergency Order of Prohibition')])
card('charge', 'THE BOEING COMPANY · PRESS RELEASE (FORM 8-K EX. 99.1) · JULY 18, 2019 · TRANSCRIPTION',
     ['Boeing to Recognize Charge and Increased Costs in', 'Second Quarter Due to 737 MAX Grounding', '“… after-tax charge of $4.9 billion …”'], w=1300, size=30, bold=(0, 1), hl=[(2, 'after-tax charge of $4.9 billion')])
card('bca', 'THE BOEING COMPANY · FORM 10-K · FISCAL 2019 · SEGMENT RESULTS · TRANSCRIPTION',
     ['(in millions)                        2019      2018', 'Commercial Airplanes', '  (loss)/earnings from operations  $(6,657)   $7,830'], w=1300, size=30, hl=[(2, '$(6,657)')])

# ── real public-domain pages of the House T&I final committee report (PD-USGov), with highlight boxes from word bboxes ──
import re as _re
def page(name, png, words_page, phrases, maxw=1400):
    im = Image.open(os.path.join(D, 'raw', 'docs', png)).convert('RGB'); sc = 1.0
    if im.width > maxw * 2: sc = maxw * 2 / im.width; im = im.resize((int(im.width * sc), int(im.height * sc)), Image.LANCZOS)
    im = ImageOps.grayscale(im).convert('RGB'); im = ImageEnhance.Contrast(im).enhance(1.05)
    im.save(os.path.join(A, f'doc_{name}.png')); LAY['doc_' + name] = list(im.size); boxes = []
    if words_page:
        h = open(os.path.join(D, 'raw', 'docs', 'bbox.html')).read(); pages = h.split('<page ')[1:]; pg = pages[words_page - 19]
        pw = float(_re.search(r'width="([\d.]+)"', pg).group(1)); k = im.width / pw
        ws = [(float(a), float(b), float(c), float(d_), html_un(t)) for a, b, c, d_, t in _re.findall(r'<word xMin="([\d.]+)" yMin="([\d.]+)" xMax="([\d.]+)" yMax="([\d.]+)">([^<]*)</word>', pg)]
        for ph in phrases:
            toks = ph.split()
            for i in range(len(ws) - len(toks) + 1):
                if all(ws[i + j][4].strip('.,“”"') == toks[j].strip('.,“”"') for j in range(len(toks))):
                    seg = ws[i:i + len(toks)]; boxes.append([min(w[0] for w in seg) * k - 6, min(w[1] for w in seg) * k - 4, max(w[2] for w in seg) * k + 6, max(w[3] for w in seg) * k + 4]); break
            else: print('phrase not found', ph)
    LAY['hl_' + name] = boxes
import html as _h; html_un = _h.unescape
page('hrcover', 'hr_cover-001.png', None, [])
page('hrp19', 'hr_p-019.png', 19, ['Production Pressures.'])
page('hrp20', 'hr_p-020.png', 20, ['Faulty Design and Performance Assumptions.', 'Culture of Concealment.'])

# ── schematic aircraft side view (illustrative) ──
X = 2; sw, sh = 1600 * X, 460 * X; im = Image.new('RGBA', (sw, sh), (0, 0, 0, 0)); d = ImageDraw.Draw(im); C = (245, 243, 239, 255); G = (133, 133, 133, 255)
d.rounded_rectangle((80 * X, 200 * X, 1440 * X, 300 * X), radius=50 * X, outline=C, width=4 * X)                  # fuselage
d.polygon([(80 * X, 250 * X), (10 * X, 262 * X), (80 * X, 290 * X)], outline=C, width=4 * X)                         # nose
d.polygon([(1380 * X, 205 * X), (1500 * X, 40 * X), (1560 * X, 40 * X), (1490 * X, 220 * X)], outline=C, width=4 * X)  # fin
d.line([(1420 * X, 250 * X), (1590 * X, 238 * X)], fill=(255, 36, 0, 255), width=8 * X)                             # horizontal stabilizer (red)
d.polygon([(560 * X, 285 * X), (900 * X, 285 * X), (1000 * X, 330 * X), (640 * X, 330 * X)], outline=G, width=3 * X)   # wing
d.rounded_rectangle((560 * X, 320 * X, 760 * X, 390 * X), radius=30 * X, outline=C, width=4 * X)                   # engine (forward, larger)
for i in range(10): d.ellipse(((160 + i * 40) * X, 228 * X, (172 + i * 40) * X, 240 * X), outline=G, width=2 * X)
d.ellipse((150 * X, 268 * X, 166 * X, 284 * X), fill=(255, 36, 0, 255))                                          # AoA vane position
im.save(os.path.join(A, 'sch_plane.png'))
# angle-of-attack diagram (illustrative): nose section, reference line, oncoming airflow, the angle
import math as _m
im = Image.new('RGBA', (760 * X, 700 * X), (0, 0, 0, 0)); d = ImageDraw.Draw(im); R_ = (255, 36, 0, 255)
d.arc((40 * X, 200 * X, 900 * X, 520 * X), 100, 260, fill=C, width=5 * X); d.line([(470 * X, 200 * X), (760 * X, 200 * X)], fill=C, width=5 * X); d.line([(470 * X, 520 * X), (760 * X, 520 * X)], fill=C, width=5 * X)
cx, cy = 300 * X, 360 * X
d.line([(cx - 280 * X, cy), (cx + 420 * X, cy)], fill=G, width=3 * X)                                  # aircraft reference line
ang = _m.radians(14); L_ = 330 * X
d.line([(cx - L_ * _m.cos(ang), cy + L_ * _m.sin(ang)), (cx, cy)], fill=R_, width=5 * X)                # oncoming airflow
for k_ in range(3):
    y0 = cy + (k_ - 1) * 90 * X + 60 * X; d.line([(20 * X, y0 + 110 * X), (220 * X, y0 + 60 * X)], fill=(255, 36, 0, 140), width=3 * X)
d.arc((cx - 160 * X, cy - 160 * X, cx + 160 * X, cy + 160 * X), 180, 194, fill=R_, width=4 * X)
d.rectangle((250 * X, 470 * X, 262 * X, 515 * X), fill=C); d.polygon([(256 * X, 470 * X), (210 * X, 455 * X), (215 * X, 470 * X)], fill=C)   # AoA vane
im.save(os.path.join(A, 'sch_aoa.png'))

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
