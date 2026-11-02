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


# ── photos: one grade (greyscale-leaning documentary treatment keeps palette), light archival grain ──
PH = json.load(open(os.path.join(D, 'photos.json')))          # {key: crop or null}
def grade(name, crop=None, maxw=3840, keep_color=False):
    im = Image.open(os.path.join(D, 'raw', name + '.jpg')).convert('RGB')
    if crop: w, h = im.size; im = im.crop((int(crop[0] * w), int(crop[1] * h), int(crop[2] * w), int(crop[3] * h)))
    im.thumbnail((maxw, maxw))
    g = ImageOps.grayscale(im) if not keep_color else im
    g = ImageEnhance.Contrast(g).enhance(1.18); g = ImageEnhance.Brightness(g).enhance(.92)
    if keep_color: g = ImageEnhance.Color(g).enhance(.72)
    n_ = Image.effect_noise(g.size, 18).filter(ImageFilter.GaussianBlur(.6)).convert(g.mode); g = Image.blend(g, n_, .05)
    g.convert('RGB').save(os.path.join(A, f'ph_{name}.png')); return g.size
for n, spec in PH.items(): LAY['ph_' + n] = grade(n, spec.get('crop'), keep_color=spec.get('color', False))

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

card('is', 'COSTCO WHOLESALE CORP. · FORM 10-K · FISCAL 2025 (52 WEEKS ENDED AUG 31, 2025) · STATEMENT OF INCOME · TRANSCRIPTION',
     ['(in millions)', 'Net sales                         $269,912', 'Membership fees                      5,323', 'Total revenue                      275,235', 'Net income                           8,099'],
     w=1500, size=32, hl=[(1, '$269,912'), (2, '5,323')])
card('renew', 'COSTCO · FORM 10-K · FISCAL 2025 · TRANSCRIPTION', ['“Our member renewal rate was 92.3% in the U.S.', 'and Canada and 89.8% worldwide at the end of 2025.”'], w=1300, size=34, hl=[(0, '92.3% in the U.S.'), (1, 'and Canada')])
card('fees', 'COSTCO · FORM 10-K · FISCAL 2025 · TRANSCRIPTION', ['“... we increased our annual membership fees', 'in the U.S. and Canada, effective September 1, 2024.”'], w=1300, size=34, hl=[(1, 'effective September 1, 2024')])
card('wh', 'COSTCO · FORM 10-K · FISCAL 2025 · TRANSCRIPTION', ['“Costco operated 914, 890, and 861 warehouses worldwide', 'at August 31, 2025, September 1, 2024, and September 3, 2023.”'], w=1500, size=30, hl=[(0, '914')])

# ── small graphics ──
def dot(name, r, col, ring=False, w=4):
    s = r * 2 + 8; im = Image.new('RGBA', (s * 4, s * 4), (0, 0, 0, 0)); d = ImageDraw.Draw(im); c = s * 2
    if ring: d.ellipse((c - r * 4, c - r * 4, c + r * 4, c + r * 4), outline=col + (255,), width=w * 4)
    else: d.ellipse((c - r * 4, c - r * 4, c + r * 4, c + r * 4), fill=col + (255,))
    im = im.resize((s, s), Image.LANCZOS); im.save(os.path.join(A, f'{name}.png'))
dot('dot_red', 9, RED); dot('dot_white', 8, (245, 243, 239)); dot('ring_red', 60, RED, ring=True, w=3); dot('dot_grey', 7, GREY)
ar = Image.new('RGBA', (120, 120), (0, 0, 0, 0)); ImageDraw.Draw(ar).polygon([(10, 20), (110, 60), (10, 100)], fill=RED + (255,)); ar.resize((30, 30), Image.LANCZOS).save(os.path.join(A, 'arrow_red.png'))
ar = Image.new('RGBA', (120, 120), (0, 0, 0, 0)); ImageDraw.Draw(ar).polygon([(10, 20), (110, 60), (10, 100)], fill=(245, 243, 239, 255)); ar.resize((30, 30), Image.LANCZOS).save(os.path.join(A, 'arrow_white.png'))
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
cpi = json.load(open(os.path.join(A, 'cpi.json'))); idx = {int(k): v for k, v in cpi['index_1985_100'].items()}
X0, X1, Y0, Y1 = 220, 1700, 860, 260; vmax = 320
px = lambda yr: X0 + (yr - 1985) / (2025 - 1985) * (X1 - X0); py = lambda v: Y0 - v / vmax * (Y0 - Y1)
overlay('cpi', [([(px(y), py(idx[y])) for y in sorted(idx)], (245, 243, 239), 4)])
overlay('flat', [([(px(1985), py(100)), (px(2025), py(100))], (255, 36, 0), 6)])
overlay('streams', [([(780, 285 + k * 130), (1100, 470)], (255, 36, 0), 3) for k in range(4)])
overlay('links', [([(860, 320), (1060, 320)], (255, 36, 0), 3), ([(560, 380), (560, 620)], (255, 36, 0), 3), ([(1360, 380), (1360, 620)], (255, 36, 0), 3), ([(860, 680), (1060, 680)], (255, 36, 0), 3)])
print('overlays ok')
