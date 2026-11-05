"""Brand Coroner · Case 006 · Nokia. Prepare still assets for the Blender build (PIL): graded photos, the real Chapter 11 petition page, typeset filing
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

card('ar07', 'NOKIA · FORM 20-F · FISCAL 2007 · TRANSCRIPTION (EXCERPTS)',
     ['“Our total mobile device volume for 2007 was', '437 million units …”', '“… our estimated full-year global market share', 'was 38% …”'], w=1150, size=30, hl=[(1, '437 million units'), (3, '38%')])
card('deal', 'NOKIA · STOCK EXCHANGE RELEASE · SEPTEMBER 3, 2013 · TRANSCRIPTION (TITLE)',
     ['Nokia to sell Devices & Services', 'business to Microsoft'], w=1100, size=34, bold=(0, 1), hl=[(0, 'Nokia to sell Devices & Services')])
card('elop', 'NOKIA · STOCK EXCHANGE RELEASE · SEPTEMBER 10, 2010 · TRANSCRIPTION (TITLE)',
     ['Nokia appoints Stephen Elop to President', 'and CEO as of September 21, 2010'], w=1100, size=32, bold=(0, 1), hl=[(0, 'Stephen Elop')])
card('ms', 'NOKIA AND MICROSOFT · FEBRUARY 11, 2011 · TRANSCRIPTION (TITLE)',
     ['Nokia and Microsoft Announce Plans for a Broad', 'Strategic Partnership to Build a New Global', 'Mobile Ecosystem'], w=1150, size=30, bold=(0, 1, 2), hl=[(1, 'Strategic Partnership')])
card('sym', 'NOKIA · FORM 20-F · FISCAL 2011 · TRANSCRIPTION (EXCERPTS)',
     ['“… the demand for our Symbian devices began', 'to deteriorate.”', '“… a faster decline in our Symbian volumes', 'than we anticipated.”'], w=1150, size=30, hl=[(2, 'a faster decline in our Symbian volumes'), (3, 'than we anticipated')])
card('share', 'NOKIA · FORM 20-F · FISCAL 2012 · TRANSCRIPTION (EXCERPTS)',
     ['“Nokia’s mobile device volume market share was', '21% in 2012 …”  “… compared to 27% in 2011 …”', '“We do not expect to sell any significant', 'volumes of Symbian devices in 2013.”'], w=1150, size=30, hl=[(1, '21% in 2012'), (2, 'We do not expect to sell any significant')])
card('close', 'NOKIA · STOCK EXCHANGE RELEASE · APRIL 25, 2014 · TRANSCRIPTION (TITLE)',
     ['Nokia completes sale of substantially all of', 'its Devices & Services business to Microsoft'], w=1150, size=32, bold=(0, 1), hl=[(0, 'Nokia completes sale')])

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
