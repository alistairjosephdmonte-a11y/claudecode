"""Prepare still assets for the Blender build (PIL): graded photos, the real Chapter 11 petition page, typeset filing
transcriptions (paper cards), the world map, dots/rings/arrowheads. Writes assets/*.png and assets/layout.json
(highlight boxes measured in the same fonts, so Blender can place red highlight strips exactly)."""
import json, os, subprocess
from PIL import Image, ImageDraw, ImageFont, ImageOps, ImageEnhance, ImageFilter
D = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
A = os.path.join(D, 'assets'); os.makedirs(A, exist_ok=True)
FONT = lambda n, s: ImageFont.truetype(os.path.join(D, 'fonts', n + '.ttf'), s)
INK, PAPER, RED, GREY = (17, 17, 17), (240, 237, 230), (255, 36, 0), (133, 133, 133)
LAY = {}

# ── photos: one grade (greyscale, contrast, slightly dark) ──
def grade(name, crop=None, maxw=2400):
    im = Image.open(os.path.join(D, 'raw', name + '.jpg')).convert('RGB')
    if crop: w, h = im.size; im = im.crop((int(crop[0] * w), int(crop[1] * h), int(crop[2] * w), int(crop[3] * h)))
    im.thumbnail((maxw, maxw)); g = ImageOps.grayscale(im); g = ImageEnhance.Contrast(g).enhance(1.22); g = ImageEnhance.Brightness(g).enhance(.92)
    g.convert('RGB').save(os.path.join(A, f'ph_{name}.png')); return g.size
for n, c in [('ww1', None), ('van2', None), ('van3', None), ('van4', None), ('van5', None), ('berlin', None), ('chicago', None),
             ('neumann', (0.0, 0.0, 0.57, 1.0)), ('empty1', None), ('empty2', None)]:
    LAY['ph_' + n] = grade(n, c)

# ── the real petition, page 1 (Official Form 201, Doc 1, filed 11/06/23) ──
subprocess.run(['pdftoppm', '-r', '150', '-f', '1', '-l', '1', '-png', os.path.join(D, 'raw/petition.pdf'), os.path.join(A, '_pet')], check=True)
pet = Image.open(os.path.join(A, '_pet-01.png')).convert('L'); pet = ImageEnhance.Brightness(pet).enhance(.94); pet.convert('RGB').save(os.path.join(A, 'doc_petition.png')); os.remove(os.path.join(A, '_pet-01.png'))
LAY['doc_petition'] = pet.size
# locate "Filed 11/06/23" with pdftotext -bbox (points → 150 dpi px)
bb = subprocess.run(['pdftotext', '-f', '1', '-l', '1', '-bbox', os.path.join(D, 'raw/petition.pdf'), '-'], capture_output=True, text=True).stdout
import re
words = re.findall(r'<word xMin="([\d.]+)" yMin="([\d.]+)" xMax="([\d.]+)" yMax="([\d.]+)">([^<]*)</word>', bb)
k = 150 / 72
def find(seq):
    toks = [w[4] for w in words]
    for i in range(len(toks) - len(seq) + 1):
        if toks[i:i + len(seq)] == seq: ws = words[i:i + len(seq)]; return [float(ws[0][0]) * k, min(float(w[1]) for w in ws) * k, float(ws[-1][2]) * k, max(float(w[3]) for w in ws) * k]
LAY['pet_filed'] = find(['Filed', '11/06/23']); LAY['pet_debtor'] = find(['WeWork', 'Inc.']); LAY['pet_chapter'] = find(['Chapter', '11'])
LAY['pet_form'] = find(['Voluntary', 'Petition', 'for', 'Non-Individuals', 'Filing', 'for'])

# ── typeset filing transcriptions on paper ──
def card(name, head, lines, w=1500, size=34, font='mono400', hl=(), pad=56, lh=1.55, foot=None, bold=()):
    f = FONT(font, size); fb = FONT('mono600', size); hf = FONT('mono600', 22); ff = FONT('mono400', 20)
    h = int(pad * 2 + 70 + len(lines) * size * lh + (len(foot) * 30 + 30 if foot else 0))
    im = Image.new('RGB', (w, h), PAPER); d = ImageDraw.Draw(im)
    d.text((pad, pad - 6), head, font=hf, fill=(110, 106, 98)); d.line((pad, pad + 32, w - pad, pad + 32), fill=(190, 186, 176), width=2)
    top = pad + 70; boxes = []
    for i, l in enumerate(lines):
        y = top + i * size * lh; d.text((pad, y), l, font=fb if i in bold else f, fill=INK)
    for (li, sub) in hl:
        l = lines[li]; a = l.index(sub); x0 = pad + d.textlength(l[:a], font=f); x1 = pad + d.textlength(l[:a + len(sub)], font=f); y = top + li * size * lh
        boxes.append([x0 - 6, y - 4, x1 + 6, y + size * 1.18])
    if foot:
        y = top + len(lines) * size * lh + 10; d.line((pad, y, w - pad, y), fill=(190, 186, 176), width=1)
        for j, l in enumerate(foot): d.text((pad, y + 16 + j * 30), l, font=ff, fill=(80, 78, 72))
    im.save(os.path.join(A, f'doc_{name}.png')); LAY['doc_' + name] = [w, h]; LAY['hl_' + name] = boxes
card('s1cover', 'FORM S-1 · REGISTRATION STATEMENT · TRANSCRIPTION', ['The We Company', 'Registration Statement under the Securities Act of 1933', 'As filed with the Securities and Exchange Commission', 'on August 14, 2019'], hl=[(3, 'August 14, 2019')], bold=(0,))
cols = ['$868,895', '$2,164,826', '$2,322,922', '$2,383,279', '$2,426,278', '$23,787,202', '$33,953,402']; W_ = [10, 12, 12, 12, 12, 13, 13]
fmt = lambda xs: ''.join(str(v).rjust(w) for v, w in zip(xs, W_))
card('s1table', 'FORM S-1 · CONTRACTUAL OBLIGATIONS · AS OF JUNE 30, 2019 · TRANSCRIPTION (EXCERPT)',
     ['(Amounts in thousands)', ' ' * 22 + fmt(['Remainder', '', '', '', '', '2024 and', '']), ' ' * 22 + fmt(['of 2019', '2020', '2021', '2022', '2023', 'beyond', 'Total']),
      'Non-cancelable operating', 'lease commitments (a)'.ljust(22) + fmt(cols)],
     w=1780, size=26, hl=[(4, '$33,953,402')],
     foot=['(a) Future undiscounted fixed minimum lease cost payments for the non-cancelable leases ... Excludes an additional',
           '$13.1 billion relating to executed non-cancelable leases that have not yet commenced as of June 30, 2019.'])
W2 = [14, 14, 14]; f2 = lambda xs: ''.join(str(v).rjust(w) for v, w in zip(xs, W2))
card('s1fin', 'FORM S-1 · SUMMARY CONSOLIDATED FINANCIAL DATA · TRANSCRIPTION',
     ['(Amounts in thousands)'.ljust(26) + f2(['2016', '2017', '2018']), 'Revenue'.ljust(26) + f2(['$436,099', '$886,004', '$1,821,751']), 'Net loss'.ljust(26) + f2(['(429,690)', '(933,494)', '(1,927,419)']),
      'Net loss attributable to', 'WeWork Companies Inc.'.ljust(26) + f2(['(429,690)', '(883,994)', '(1,610,792)'])], w=1500, size=30, hl=[(1, '$1,821,751'), (2, '(1,927,419)'), (4, '(1,610,792)')])
card('risk', 'FORM S-1 · RISK FACTORS · TRANSCRIPTION', ['“... had net losses of $0.4 billion, $0.9 billion', 'and $1.9 billion for the years ended', 'December 31, 2016, 2017 and 2018.”'], w=1100, size=32, hl=[(0, '$0.4 billion, $0.9 billion'), (1, 'and $1.9 billion')])
card('related', 'FORM S-1/A · SEP 3, 2019 · RELATED-PARTY · TRANSCRIPTION', ['WE Holdings LLC “assigned to us any rights that it possessed', 'related to “we” family trademarks” — in exchange,', 'partnership interests “with a fair market value of', 'approximately $5.9 million.”', '', '“Subsequently, at Adam’s direction, the issuance to', 'WE Holdings LLC of the partnership interests was unwound.”'],
     w=1300, size=30, hl=[(3, 'approximately $5.9 million'), (6, 'was unwound')])
card('votes', 'FORM S-1 (AUG 14, 2019) · FORM S-1/A (SEP 13, 2019) · TRANSCRIPTION', ['“The Class A common stock has one vote per share”', 'Class B and Class C: “twenty votes per share”', '', 'S-1/A: “Our high-vote stock will decrease from', '20 votes per share to 10 votes per share.”'],
     w=1300, size=30, hl=[(1, 'twenty votes per share'), (4, '20 votes per share to 10 votes per share')])
card('rw', 'SEC EDGAR · FILING INDEX · TRANSCRIPTION', ['Form RW · Registration Withdrawal Request', 'Filed 2019-09-30 · File No. 333-233259 · We Co.'], w=1200, size=32, hl=[(1, 'Filed 2019-09-30')])
card('tenq', 'FORM 10-Q · QUARTER ENDED JUNE 30, 2023 · FILED AUG 2023 · TRANSCRIPTION', ['“... substantial doubt exists about the Company’s', 'ability to continue as a going concern.”'], w=1300, size=34, hl=[(0, 'substantial doubt exists')])
card('q3', 'FORM 8-K · EX. 99.1 · Q3 2023 FINANCIAL REPORT (NOV 2023) · TRANSCRIPTION', ['As of September 30, 2023, “the Company had', '$462 million in cash and cash equivalents”'], w=1300, size=34, hl=[(1, '$462 million')])
card('emerge', 'WEWORK NEWSROOM · JUNE 11, 2024 · TRANSCRIPTION', ['WeWork Announces Emergence from Chapter 11', 'and New Leadership Appointments'], w=1100, size=32, hl=[(0, 'Emergence from Chapter 11')])
card('first', 'FORM S-1 · BUSINESS · TRANSCRIPTION', ['“In early 2010, we opened our doors to our first', 'member community at 154 Grand Street in New York City.”'], w=1400, size=32, hl=[(0, 'In early 2010'), (1, '154 Grand Street')])
card('scale', 'FORM S-1 · TRANSCRIPTION', ['“... a platform spanning 528 locations', 'in 111 cities across 29 countries.”'], w=1100, size=32, hl=[(0, '528 locations'), (1, '111 cities across 29 countries')])
card('terms', 'FORM S-1 · TRANSCRIPTION', ['Members: average commitment term “to more than 15 months', 'as of June 1, 2019”', 'Landlords: “The average length of the initial term of our', 'U.S. leases is approximately 15 years.”'], w=1500, size=30, hl=[(0, 'more than 15 months'), (3, 'approximately 15 years')])
card('bowx', 'BUSINESS WIRE · MAR 26, 2021 · BOWX ACQUISITION CORP. & WEWORK · TRANSCRIPTION', ['“The transaction implies a pro forma initial enterprise', 'value of approximately $9 billion for WeWork.”'], w=1400, size=32, hl=[(1, 'approximately $9 billion')])

# ── world map (Robinson projection, public domain), greyscale, dark ──
m = Image.open(os.path.join(D, 'raw/worldmap.png')).convert('RGBA'); bgm = Image.new('RGBA', m.size, (255, 255, 255, 255)); bgm.alpha_composite(m)
g = ImageOps.grayscale(bgm.convert('RGB')); g = ImageOps.invert(g); g = ImageEnhance.Brightness(g).enhance(.42); g.convert('RGB').save(os.path.join(A, 'map.png')); LAY['map'] = g.size

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
