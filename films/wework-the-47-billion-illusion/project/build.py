"""BRAND CORONER · CASE 002 · WEWORK — "the $47 billion illusion"
Blender (4.2 LTS) Python build: constructs the whole 8-minute animatic in the Video Sequence Editor.
  blender -b -P build.py                → writes wework.blend (editable project) and events.json (sound cues)
Every scene is a meta strip (S01…S16) holding its own editable strips: text strips (editable typography),
colour strips (panels, rules, bars, red evidence lines), image strips (graded authentic photographs, the real
Chapter 11 petition page, typeset filing transcriptions, the world map). Camera moves are keyframed 2D transforms
(orthographic, flat): push-ins, tracking, pull-outs. Narration markers sit on the master timeline (silent animatic).
Coordinates below are pixels, origin top-left, 1920×1080; times are seconds."""
import bpy, json, os, math
D = os.path.dirname(os.path.abspath(__file__)); A = os.path.join(D, 'assets'); FT = os.path.join(D, 'fonts')
LAY = json.load(open(os.path.join(A, 'layout.json')))
FPS, W, H, DUR = 24, 1920, 1080, 480
def hexc(h, a=None): h = h.lstrip('#'); c = tuple(int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)); return c + ((a,) if a is not None else ())
BG, RED, TXT, GREY, PANEL, RULE = '#080808', '#FF2400', '#F5F3EF', '#858585', '#121212', '#2B2B2B'
F = lambda t: int(round(t * FPS)) + 1

# ── scene setup ──
for s in list(bpy.data.scenes)[1:]: bpy.data.scenes.remove(s)
sc = bpy.context.scene; sc.name = 'brand_coroner_case002_wework'
sc.render.resolution_x, sc.render.resolution_y, sc.render.resolution_percentage = W, H, 100
sc.render.fps = FPS; sc.frame_start, sc.frame_end = 1, DUR * FPS
sc.view_settings.view_transform = 'Standard'; sc.view_settings.look = 'None'; sc.sequencer_colorspace_settings.name = 'sRGB'
if sc.sequence_editor: sc.sequence_editor_clear()
SE = sc.sequence_editor_create()
FONTS = {k: bpy.data.fonts.load(os.path.join(FT, f'{k}.ttf')) for k in ['outfit700', 'outfit500', 'outfit300', 'mono400', 'mono600', 'serifi']}
EV = []          # sound cues: (t, kind)
NAMES = [0]
def nm(p): NAMES[0] += 1; return f'{p}{NAMES[0]:04d}'

class Ctx:
    def __init__(self, meta, base): self.m, self.base, self.c, self.keep = meta, base, 2, 2
    def ch(self): self.c += 1; assert self.c < 127, 'too many channels'; return self.c
    def beat(self): self.c = self.keep
    def hold(self): self.keep = self.c
CX = None
def T(t): return CX.base + t

def fade(strip, t0, t1, a=1.0, fin=0.0, fout=0.0, flash=False):
    """opacity: cut in (fin=0) or fade; hold; cut/fade out"""
    s = strip
    if fin > 0: s.blend_alpha = 0; s.keyframe_insert('blend_alpha', frame=F(T(t0))); s.blend_alpha = a; s.keyframe_insert('blend_alpha', frame=F(T(t0 + fin)))
    else: s.blend_alpha = a
    if fout > 0: s.blend_alpha = a; s.keyframe_insert('blend_alpha', frame=F(T(t1 - fout))); s.blend_alpha = 0; s.keyframe_insert('blend_alpha', frame=F(T(t1)) - 1)

def span(s, t0, t1): s.frame_start = F(T(t0)); s.frame_final_duration = max(1, F(T(t1)) - F(T(t0)))

def rect(x, y, w, h, col, t0, t1, a=1.0, fin=0.0, fout=0.0, grow=None, blend='ALPHA_OVER'):
    """flat colour box; grow=(ta, tb, 'x'|'y'|'xr') draws it progressively (lines, bars)"""
    s = CX.m.sequences.new_effect(nm('r'), 'COLOR', CX.ch(), frame_start=F(T(t0)), frame_end=F(T(t1))); s.color = hexc(col)
    s.blend_type = blend; tr = s.transform; tr.origin = (0, 1)
    tr.scale_x, tr.scale_y = max(w, .01) / W, max(h, .01) / H; tr.offset_x, tr.offset_y = x, -y
    if grow:
        ta, tb, ax = grow
        if ax == 'xr': tr.origin = (1, 1); tr.offset_x = x + w - W
        prop = 'scale_x' if ax in ('x', 'xr') else 'scale_y'; full = getattr(tr, prop)
        setattr(tr, prop, 0.0001); tr.keyframe_insert(prop, frame=F(T(ta))); setattr(tr, prop, full); tr.keyframe_insert(prop, frame=F(T(tb)))
    fade(s, t0, t1, a, fin, fout); return s

def flash(x, y, w, h, t0, d=.13):
    s = rect(x, y, w, h, '#FFFFFF', t0, t0 + d + .05); s.blend_alpha = 1; s.keyframe_insert('blend_alpha', frame=F(T(t0))); s.blend_alpha = 0; s.keyframe_insert('blend_alpha', frame=F(T(t0 + d)))

def text(st, x, y, size, t0, t1, col=TXT, font='outfit700', al='LEFT', a=1.0, fin=0.0, fout=0.0, wrap=0, valign='TOP'):
    s = CX.m.sequences.new_effect(nm('t'), 'TEXT', CX.ch(), frame_start=F(T(t0)), frame_end=F(T(t1)))
    s.text = st; s.font = FONTS[font]; s.font_size = size; s.color = hexc(col, 1.0); s.align_x = al; s.align_y = valign
    s.location = (x / W, 1 - y / H); s.blend_type = 'ALPHA_OVER'
    if wrap: s.wrap_width = wrap / W
    fade(s, t0, t1, a, fin, fout); return s

def image(name, x, y, w, h, t0, t1, fx=.5, fy=.5, z0=1.0, z1=1.0, fin=0.0, fout=0.0, a=1.0, cut=True, contain=False):
    """image in a box (cover crop, or contain), optional push-in z0→z1 about focus (fx, fy); hard cut-in with flash"""
    path = os.path.join(A, name + '.png'); iw, ih = LAY.get(name.replace('.png', ''), (0, 0)) or (0, 0)
    s = CX.m.sequences.new_image(nm('i'), path, CX.ch(), F(T(t0)), fit_method='ORIGINAL'); s.frame_final_duration = max(1, F(T(t1)) - F(T(t0)))
    iw, ih = s.elements[0].orig_width, s.elements[0].orig_height; s.blend_type = 'ALPHA_OVER'
    def place(z, frame):
        sc0 = (min if contain else max)(w / iw, h / ih) * z; dw, dh = iw * sc0, ih * sc0
        cx = x + w / 2 + (0.5 - fx) * max(0, dw - w); cy = y + h / 2 + (0.5 - fy) * max(0, dh - h)
        tr = s.transform; tr.scale_x = tr.scale_y = sc0; tr.offset_x, tr.offset_y = cx - W / 2, H / 2 - cy
        l, r, t_, b = cx - dw / 2, cx + dw / 2, cy - dh / 2, cy + dh / 2
        cr = s.crop; cr.min_x = int(max(0, x - l) / sc0); cr.max_x = int(max(0, r - (x + w)) / sc0); cr.max_y = int(max(0, y - t_) / sc0); cr.min_y = int(max(0, b - (y + h)) / sc0)
        if frame is not None:
            for p in ('scale_x', 'scale_y', 'offset_x', 'offset_y'): tr.keyframe_insert(p, frame=frame)
            for p in ('min_x', 'max_x', 'min_y', 'max_y'): cr.keyframe_insert(p, frame=frame)
    if z0 == z1: place(z0, None)
    else:
        n = max(2, int((t1 - t0)) + 1)
        for i in range(n + 1): k = i / n; place(z0 + (z1 - z0) * (k * k * (3 - 2 * k)), F(T(t0 + (t1 - t0) * k)))
    fade(s, t0, t1, a, fin, fout)
    if cut and fin == 0: flash(x, y, w, h, t0)
    return s

def sprite(name, cx, cy, t0, t1, path_pts=None, scale=1.0, a=1.0, fin=0.0, fout=0.0):
    """small PNG (dot, ring, arrow) centred at (cx, cy); path_pts=[(t, x, y), …] moves it"""
    s = CX.m.sequences.new_image(nm('s'), os.path.join(A, name + '.png'), CX.ch(), F(T(t0)), fit_method='ORIGINAL'); s.frame_final_duration = max(1, F(T(t1)) - F(T(t0)))
    s.blend_type = 'ALPHA_OVER'; tr = s.transform; tr.scale_x = tr.scale_y = scale
    if path_pts:
        for (t, px, py) in path_pts: tr.offset_x, tr.offset_y = px - W / 2, H / 2 - py; tr.keyframe_insert('offset_x', frame=F(T(t))); tr.keyframe_insert('offset_y', frame=F(T(t)))
    else: tr.offset_x, tr.offset_y = cx - W / 2, H / 2 - cy
    fade(s, t0, t1, a, fin, fout); return s

def tag(st, x, y, t0, t1, col=TXT, chip=None):   # source tag: chip + lowercase mono label
    rect(x, y + 4, 6, 14, chip or col, t0, t1); return text(st, x + 16, y, 17, t0, t1, col=col, font='mono600')

def hl_boxes(doc, X, Y, scale, t0s, dur=.6):    # red multiply highlight wipes over a doc placed at (X, Y) with scale
    for (bx0, by0, bx1, by1), ta in zip(LAY['hl_' + doc], t0s):
        rect(X + bx0 * scale, Y + by0 * scale, (bx1 - bx0) * scale, (by1 - by0) * scale, RED, ta, CX_END[0], a=.30, grow=(ta, ta + dur, 'x'))
        rect(X + bx0 * scale, Y + by1 * scale - 1, (bx1 - bx0) * scale, max(3, 4 * scale), RED, ta, CX_END[0], grow=(ta, ta + dur, 'x'))
        EV.append((T(ta), 'mark'))
CX_END = [30]

def doc(name, x, y, w, t0, t1, hls=(), z0=1.0, z1=1.0, fy=.5, fx=.5, h=None):
    iw, ih = LAY[name]; s = w / iw; hh = h or ih * s
    im = image(name, x, y, w, hh, t0, t1, fx=fx, fy=fy, z0=z0, z1=z1)
    EV.append((T(t0), 'paper'))
    if hls: CX_END[0] = t1; hl_boxes(name[4:], x, y, s, hls)
    return s, hh

def heading(st, x, y, size, t0, t1, col=TXT, al='LEFT'):
    EV.append((T(t0), 'type')); return text(st, x, y, size, t0, t1, col=col, al=al)

def marker(code, t0, t1):     # on-screen narration marker for the silent animatic (low-key, bottom left)
    text(f'narration marker {code}', 60, 1032, 15, t0, t1, col='#5a5a5a', font='mono400')
    sc.timeline_markers.new(f'N{code}', frame=F(T(t0)))

def chrome(i, title, act=None):
    text('brand coroner · case 002', 60, 40, 16, 0, 30, col=GREY, font='mono600')
    text(f'{i:02d} · {title}', 1860, 40, 16, 0, 30, col=GREY, font='mono600', al='RIGHT')
    if act: text(act, 60, 70, 18, 0, 3.5, col=RED, font='mono600')

SCENES = []
def scene(i, title, act=None):
    def deco(fn): SCENES.append((i, title, act, fn)); return fn
    return deco

# ═══════════════════════════ ACT 01 · THE VALUATION ═══════════════════════════
@scene(1, 'the $47 billion contradiction', 'act 01 · the valuation')
def s01():
    # beat 1: pure black, a red line draws, the number
    rect(0, 538, 1920, 4, RED, 1.0, 8.6, grow=(1.0, 3.2, 'x'))
    heading('$47,000,000,000', 960, 360, 190, 3.6, 8.6, al='CENTER'); EV.append((T(3.6), 'boom'))
    text('2019 · private valuation · reported', 960, 600, 34, 5.2, 8.6, col=GREY, font='outfit500', al='CENTER')
    marker('01.1', 0, 8.6)
    # beat 2: authentic photograph + label
    CX.beat()
    image('ph_ww1', 60, 110, 1080, 760, 8.6, 18.4, fx=.5, fy=.55, z0=1.0, z1=1.06)
    tag('photo · wework, new york · jun 2019', 60, 84, 8.6, 18.4)
    text('2019', 1200, 230, 40, 9.2, 18.4, col=RED, font='mono600')
    heading('$47 billion', 1200, 290, 104, 9.6, 18.4)
    text('private valuation', 1204, 420, 40, 10.4, 18.4, font='outfit500')
    text('reported at softbank’s january 2019 investment', 1204, 480, 24, 11.4, 18.4, col=GREY, font='outfit300', wrap=640)
    text('a private-market price, not a public one', 1204, 560, 24, 13.0, 18.4, col=GREY, font='outfit300')
    marker('01.2', 8.6, 18.4)
    # beat 3: split screen, red evidence line between the dates
    CX.beat()
    rect(958, 110, 4, 770, RULE, 18.4, 30)
    image('ph_ww1', 60, 150, 860, 480, 18.4, 30, fx=.5, fy=.5)
    text('2019', 60, 670, 30, 18.6, 30, col=RED, font='mono600'); heading('$47 billion', 60, 710, 76, 18.6, 30)
    text('private valuation (reported)', 64, 800, 24, 18.6, 30, col=GREY, font='outfit500')
    ps, ph = doc('doc_petition', 1000, 150, 380, 19.4, 30)
    text('2023', 1420, 160, 30, 19.6, 30, col=RED, font='mono600'); heading('bankruptcy', 1420, 200, 64, 19.6, 30); heading('protection', 1420, 270, 64, 19.6, 30)
    text('chapter 11 · filed nov 6, 2023', 1424, 360, 24, 20.2, 30, col=GREY, font='outfit500')
    tag('court filing · d.n.j. · doc 1', 1000, 124, 19.4, 30)
    rect(490, 880, 0, 3, RED, 21.0, 30)
    rect(490, 905, 1210 - 490 + 0, 3, RED, 21.0, 30, grow=(21.0, 23.0, 'x')); sprite('dot_red', 490, 906, 21.0, 30); sprite('dot_red', 1190, 906, 23.0, 30)
    text('4 years', 840, 930, 22, 23.0, 30, col=RED, font='mono600', al='CENTER')
    heading('what went wrong?', 960, 960, 64, 25.0, 30, al='CENTER')
    marker('01.3', 18.4, 30)

@scene(2, 'the first clue')
def s02():
    # beat 1: the genuine filing, push toward the filing date
    iw, ih = LAY['doc_petition']; fx0, fy0, fx1, fy1 = LAY['pet_filed']
    image('doc_petition', 60, 110, 760, 790, 0, 11, fx=(fx0 + fx1) / 2 / iw, fy=.0, z0=1.0, z1=1.55)
    tag('voluntary petition · official form 201 · doc 1', 60, 84, 0, 11)
    text('filed', 900, 210, 40, 1.0, 11, col=GREY, font='outfit500'); heading('nov 6, 2023', 900, 260, 110, 1.4, 11, col=RED)
    text('wework inc. · chapter 11', 904, 400, 36, 2.6, 11, font='outfit500')
    text('united states bankruptcy court · district of new jersey', 904, 456, 24, 3.4, 11, col=GREY, font='outfit300')
    rect(900, 520, 900, 2, RED, 4.0, 11, grow=(4.0, 5.0, 'x')); EV.append((T(4.0), 'mark'))
    marker('02.1', 0, 11)
    # beat 2: landlord → wework → member, money flows
    CX.beat()
    boxes = [('landlord', 210), ('wework', 960), ('member', 1710)]
    for k, (lab, cx) in enumerate(boxes):
        rect(cx - 210, 380, 420, 150, PANEL, 11 + k * .5, 30); rect(cx - 210, 380, 420, 150, RED if k == 1 else TXT, 11 + k * .5, 30, a=1).blend_type = 'ALPHA_OVER'
        rect(cx - 208, 382, 416, 146, PANEL, 11 + k * .5, 30)
        heading(lab, cx, 422, 52, 11 + k * .5, 30, al='CENTER'); flash(cx - 210, 380, 420, 150, 11 + k * .5)
    rect(420, 453, 330, 3, GREY, 13.0, 30, grow=(13.0, 13.8, 'xr')); sprite('arrow_white', 432, 455, 13.8, 30, scale=1)
    rect(1170, 453, 330, 3, GREY, 13.8, 30, grow=(13.8, 14.6, 'xr')); sprite('arrow_white', 1182, 455, 14.6, 30)
    text('rent', 585, 405, 28, 13.4, 30, col=TXT, font='mono600', al='CENTER'); text('membership fees', 1335, 405, 28, 14.2, 30, col=TXT, font='mono600', al='CENTER')
    for j in range(4):   # cash moving: members → wework → landlord
        t = 15 + j * 1.2
        sprite('dot_white', 0, 0, t, t + 2.2, path_pts=[(t, 1490, 455), (t + 1.0, 1180, 455)])
        sprite('dot_red', 0, 0, t + .9, t + 3.0, path_pts=[(t + .9, 740, 455), (t + 1.9, 430, 455)])
    tag('editorial diagram', 60, 300, 11, 30, col=GREY, chip=GREY)
    marker('02.2', 11, 21)
    # beat 3: the contradiction
    rect(0, 600, 1920, 2, RULE, 21, 30)
    heading('long-term leases', 210, 650, 48, 21.4, 30, col=RED, al='CENTER'); text('owed to landlords for years', 210, 715, 24, 21.8, 30, col=GREY, font='outfit300', al='CENTER')
    heading('flexible customers', 1710, 650, 48, 22.8, 30, al='CENTER'); text('members can leave sooner', 1710, 715, 24, 23.2, 30, col=GREY, font='outfit300', al='CENTER')
    heading('the contradiction at the centre', 960, 840, 40, 25.0, 30, al='CENTER'); rect(760, 900, 400, 3, RED, 25.4, 30, grow=(25.4, 26.4, 'x'))
    EV.append((T(25.0), 'low'))
    marker('02.3', 21, 30)

# ═══════════════════════════ ACT 02 · THE PROMISE ═══════════════════════════
@scene(3, 'a different kind of office', 'act 02 · the promise')
def s03():
    # beat 1: traditional vs flexible
    heading('traditional office', 60, 130, 56, 0.4, 10, col=GREY)
    for k, s in enumerate(['sign a long lease', 'build it out', 'furnish it', 'staff it']): text(f'—  {s}', 64, 230 + k * 64, 34, 1.2 + k * .5, 10, col=GREY, font='outfit500')
    rect(940, 110, 2, 640, RULE, 0.4, 10)
    heading('flexible workspace', 1000, 130, 56, 3.6, 10)
    image('ph_van5', 1000, 230, 860, 520, 4.0, 10, fx=.5, fy=.5, z0=1.0, z1=1.05)
    tag('photo · wework, vancouver · dec 2018', 1000, 204, 4.0, 10)
    text('walk in · it is already built', 1004, 780, 30, 6.0, 10, font='outfit500')
    marker('03.1', 0, 10)
    # beat 2: archival collage
    CX.beat()
    P = [('ph_van3', 60, 110, 900, 400, 'shared workspace', 'vancouver · dec 2018', 10.0), ('ph_van4', 990, 110, 870, 400, 'front desk & lounge', 'vancouver · dec 2018', 11.0),
         ('ph_berlin', 60, 540, 600, 340, 'shared desks', 'berlin · aug 2016', 12.0), ('ph_van2', 690, 540, 600, 340, 'member check-in', 'vancouver · dec 2018', 13.0),
         ('ph_chicago', 1320, 540, 540, 340, 'entrance', 'chicago · oct 2018', 14.0)]
    for (n, x, y, w, h, lab, src, t) in P:
        image(n, x, y, w, h, t, 21, z0=1.0, z1=1.04); EV.append((T(t), 'shutter'))
        rect(x, y + h - 54, w, 54, '#000000', t + .2, 21, a=.6); text(lab, x + 18, y + h - 44, 26, t + .2, 21, font='outfit700'); text(src, x + w - 18, y + h - 40, 17, t + .2, 21, col=GREY, font='mono600', al='RIGHT')
    marker('03.2', 10, 21)
    # beat 3: first location, from the S-1
    CX.beat()
    doc('doc_first', 60, 300, 1100, 21.0, 30, hls=(22.0, 23.0))
    heading('2010', 1300, 260, 150, 21.6, 30, col=RED); text('first location', 1304, 450, 40, 22.4, 30, font='outfit500'); text('154 grand street, new york', 1304, 510, 28, 23.0, 30, col=GREY, font='outfit300')
    text('memberships, not leases: desks, offices and rooms by agreement', 60, 640, 28, 25.0, 30, col=GREY, font='outfit500')
    marker('03.3', 21, 30)

@scene(4, 'selling the future')
def s04():
    # beat 1: adam neumann (authentic photograph)
    image('ph_neumann', 60, 110, 600, 800, 0, 8.5, fx=.5, fy=.3, z0=1.0, z1=1.06)
    tag('photo · techcrunch disrupt ny · may 2015 · cc by 2.0', 60, 84, 0, 8.5)
    heading('adam neumann', 760, 300, 96, 0.8, 8.5); text('co-founder and chief executive', 764, 420, 36, 1.6, 8.5, col=GREY, font='outfit500')
    for k, s in enumerate(['community', 'growth', 'global expansion']):
        heading(s, 764, 540 + k * 90, 64, 3.0 + k * 1.3, 8.5, col=RED if k == 2 else TXT)
    marker('04.1', 0, 8.5)
    # beat 2: the map — verified markers only
    CX.beat()
    mw, mh = LAY['map']; X, Y, Wm = 60, 110, 1800; Hm = mh * Wm / mw
    image('map', X, Y, Wm, Hm, 8.5, 20.5, z0=1.0, z1=1.04)
    def robinson(lat, lon):
        tbl = [(0, 1.0, 0.0), (5, .9986, .062), (10, .9954, .124), (15, .99, .186), (20, .9822, .248), (25, .973, .31), (30, .96, .372), (35, .9427, .434), (40, .9216, .4958), (45, .8962, .5571),
               (50, .8679, .6176), (55, .835, .6769), (60, .7986, .7346), (65, .7597, .7903), (70, .7186, .8435), (75, .6732, .8936), (80, .6213, .9394), (85, .5722, .9761), (90, .5322, 1.0)]
        a = abs(lat); i = min(17, int(a // 5)); k = (a - i * 5) / 5; plen = tbl[i][1] + (tbl[i + 1][1] - tbl[i][1]) * k; pdfe = tbl[i][2] + (tbl[i + 1][2] - tbl[i][2]) * k
        u = .5 + plen * lon / 360 * (1 / 1.0) * .997; v = .5 - math.copysign(pdfe, lat) * .5 * .9865
        return X + u * Wm, Y + v * Hm
    pts = [('new york · 154 grand st · 2010 · first location', 40.72, -74.0, RED, 9.4), ('vancouver · photographed 2018', 49.28, -123.12, GREY, 11.6), ('chicago · photographed 2018', 41.88, -87.63, GREY, 12.2), ('berlin · photographed 2016', 52.51, 13.37, GREY, 12.8)]
    for (lab, la, lo, col, t) in pts:
        px, py = robinson(la, lo); sprite('dot_red' if col == RED else 'dot_grey', px, py, t, 20.5)
        if col == RED: sprite('ring_red', px, py, t, 20.5, scale=.5); EV.append((T(t), 'mark'))
    text('new york · 2010 · first location', 120, 800, 26, 9.6, 20.5, col=RED, font='mono600')
    text('grey: locations shown in this film’s photographs', 120, 838, 20, 12.0, 20.5, col=GREY, font='mono400')
    tag('map · robinson projection · public domain', 60, 84, 8.5, 20.5)
    s, h = doc('doc_scale', 1100, 640, 760, 14.0, 20.5, hls=(14.8, 15.6))
    text('as described in the s-1 · aug 2019', 1104, 640 + h + 14, 18, 14.4, 20.5, col=GREY, font='mono400')
    marker('04.2', 8.5, 20.5)
    # beat 3: growth ≠ profitability → the question (slow push = growing type)
    CX.beat()
    heading('growth', 560, 340, 120, 20.6, 25.4, al='CENTER'); heading('≠', 960, 340, 120, 21.2, 25.4, col=RED, al='CENTER'); heading('profitability', 1380, 340, 120, 21.2, 25.4, al='CENTER')
    q = text('could the economics support the ambition?', 960, 520, 60, 25.4, 30, al='CENTER'); EV.append((T(25.4), 'low'))
    q.transform.scale_x = q.transform.scale_y = 1.0; q.transform.keyframe_insert('scale_x', frame=F(T(25.4))); q.transform.keyframe_insert('scale_y', frame=F(T(25.4)))
    q.transform.scale_x = q.transform.scale_y = 1.08; q.transform.keyframe_insert('scale_x', frame=F(T(30)) - 1); q.transform.keyframe_insert('scale_y', frame=F(T(30)) - 1)
    marker('04.3', 20.6, 30)

# ═══════════════════════════ ACT 03 · THE MACHINE ═══════════════════════════
def node(lab, cx, cy, t, col=TXT, w=360):
    rect(cx - w / 2, cy - 60, w, 120, col, t, 30); rect(cx - w / 2 + 2, cy - 58, w - 4, 116, PANEL, t, 30); heading(lab, cx, cy - 28, 44, t, 30, al='CENTER', col=col); flash(cx - w / 2, cy - 60, w, 120, t)
@scene(5, 'the business model', 'act 03 · the machine')
def s05():
    tag('editorial diagram · how the model works', 60, 84, 0, 30, col=GREY, chip=GREY)
    node('landlord', 260, 300, 0.4); node('wework', 960, 300, 1.0, col=RED); node('member', 1660, 300, 1.6)
    steps = [('01', 'lease', 'signs a long lease with a landlord', 3.0), ('02', 'fit-out', 'spends to design and build the space', 7.0), ('03', 'operate', 'runs the space: staff, services, upkeep', 13.0), ('04', 'collect revenue', 'members pay for access', 17.0)]
    for k, (n, lab, sub, t) in enumerate(steps):
        x = 60 + k * 460
        text(n, x, 560, 24, t, 30, col=RED, font='mono600'); heading(lab, x, 596, 50, t, 30); text(sub, x, 666, 24, t + .4, 30, col=GREY, font='outfit300', wrap=420)
        rect(x, 740, 420, 3, RED if k < 3 else TXT, t, 30, grow=(t, t + .8, 'x'))
    # cash out first (red), revenue later (white)
    rect(440, 298, 340, 3, RED, 3.4, 30, grow=(3.4, 4.2, 'xr')); text('rent →', 610, 250, 22, 3.6, 30, col=RED, font='mono600', al='CENTER')
    for j in range(3): t = 4.4 + j * 1.5; sprite('dot_red', 0, 0, t, t + 1.4, path_pts=[(t, 780, 300), (t + 1.2, 450, 300)])
    text('fit-out spending', 960, 400, 24, 7.4, 30, col=RED, font='mono600', al='CENTER'); rect(940, 432, 40, 3, RED, 7.4, 30)
    rect(1140, 298, 340, 3, TXT, 17.4, 30, grow=(17.4, 18.2, 'xr')); text('← membership fees', 1310, 250, 22, 17.6, 30, font='mono600', al='CENTER')
    for j in range(4): t = 18.4 + j * 1.3; sprite('dot_white', 0, 0, t, t + 1.4, path_pts=[(t, 1480, 300), (t + 1.2, 1150, 300)])
    heading('cash goes out first. revenue arrives month by month.', 960, 840, 44, 24.0, 30, al='CENTER'); EV.append((T(24.0), 'low'))
    for t0, code in [(0, '05.1'), (10, '05.2'), (20, '05.3')]: marker(code, t0, t0 + 10)

@scene(6, 'the lease mismatch')
def s06():
    tag('timeline · scale: 1 px = 0.6 days · figures from the s-1', 60, 84, 0, 30, col=GREY, chip=GREY)
    X0, X1 = 260, 1800; L = X1 - X0; mo = L / 180          # 180 months (15 years) across the axis
    rect(X0, 900, L, 2, RULE, 0.2, 30)
    for yr in range(0, 16, 3):
        rect(X0 + yr * 12 * mo, 892, 2, 16, GREY, 0.2, 30); text(f'{yr} yr', X0 + yr * 12 * mo, 918, 18, 0.2, 30, col=GREY, font='mono400', al='CENTER')
    heading('customer commitment', 60, 250, 36, 0.8, 30); text('average membership term', 64, 300, 22, 1.2, 30, col=GREY, font='outfit300')
    heading('landlord lease', 60, 560, 36, 1.6, 30, col=RED); text('average initial term, u.s. leases', 64, 610, 22, 2.0, 30, col=GREY, font='outfit300')
    # bars draw at true scale
    top = rect(X0, 330, 15 * mo, 60, TXT, 3.0, 22.0, grow=(3.0, 4.2, 'x')); text('> 15 months', X0 + 15 * mo + 20, 342, 34, 4.2, 22.0, font='outfit700')
    rect(X0, 640, L, 60, RED, 5.0, 30, grow=(5.0, 11.0, 'x')); text('≈ 15 years', X1 - 10, 652, 34, 11.0, 30, col=BG, font='outfit700', al='RIGHT')
    EV.append((T(3.0), 'mark')); EV.append((T(5.0), 'draw'))
    s, h = doc('doc_terms', 760, 120, 1100, 12.0, 21.0, hls=(12.8, 13.6))
    heading('flexible revenue', X0, 420, 40, 14.0, 22.0, col=TXT); heading('long-term obligations', X0, 730, 40, 15.0, 30, col=RED)
    # the shorter timeline disappears; the longer one remains
    top.blend_alpha = 1; top.keyframe_insert('blend_alpha', frame=F(T(20.5))); top.blend_alpha = 0; top.keyframe_insert('blend_alpha', frame=F(T(22.0)) - 1); EV.append((T(21.0), 'low'))
    heading('the members can leave. the lease stays.', 960, 160, 52, 23.0, 30, al='CENTER')
    for t0, code in [(0, '06.1'), (10, '06.2'), (20, '06.3')]: marker(code, t0, t0 + 10)

@scene(7, 'the expansion machine')
def s07():
    # beat 1: the genuine S-1 table, camera moves toward the total
    iw, ih = LAY['doc_s1table']; s = 1800 / iw
    image('doc_s1table', 60, 160, 1800, ih * s, 0, 11, fx=.9, fy=.6, z0=1.0, z1=1.0); EV.append((T(0), 'paper'))
    tag('form s-1 · aug 14, 2019 · contractual obligations', 60, 134, 0, 11)
    CX_END[0] = 11; hl_boxes('s1table', 60, 160, s, (2.4,))
    bx = LAY['hl_s1table'][0]
    sprite('ring_red', 60 + (bx[0] + bx[2]) / 2 * s, 160 + (bx[1] + bx[3]) / 2 * s, 3.2, 11, scale=1.4)
    marker('07.1', 0, 11)
    # beat 2: the number, labelled precisely; the separate category
    CX.beat()
    heading('$33.95 billion', 60, 200, 150, 11.0, 30, col=TXT); EV.append((T(11.0), 'boom'))
    text('future minimum payments on commenced operating leases, undiscounted', 64, 380, 32, 11.6, 30, col=GREY, font='outfit500')
    text('as of june 30, 2019 · s-1 contractual obligations table', 64, 430, 22, 12.0, 30, col=GREY, font='mono400')
    rect(60, 520, 900, 200, PANEL, 15.0, 30); rect(60, 520, 900, 200, RED, 15.0, 30).blend_type = 'ALPHA_OVER'; rect(62, 522, 896, 196, PANEL, 15.0, 30)
    text('separate category', 90, 546, 20, 15.2, 30, col=RED, font='mono600'); heading('+ ≈ $13.1 billion', 90, 580, 64, 15.2, 30)
    text('signed, not yet commenced (s-1 footnote)', 94, 664, 24, 15.6, 30, col=GREY, font='outfit300'); flash(60, 520, 900, 200, 15.0); EV.append((T(15.0), 'mark'))
    text('not one debt payable today: payments fall due over many years', 64, 770, 28, 18.0, 30, col=TXT, font='outfit500')
    # beat 3: red line extends beyond the frame
    rect(60, 880, 1860, 6, RED, 21.0, 30, grow=(21.0, 27.0, 'x')); text('2019', 60, 900, 20, 21.0, 30, col=GREY, font='mono600'); text('2024 and beyond →', 1860, 900, 20, 25.0, 30, col=RED, font='mono600', al='RIGHT')
    EV.append((T(21.0), 'draw'))
    for t0, code in [(11, '07.2'), (21, '07.3')]: marker(code, t0, t0 + 10 if t0 < 21 else 30)

# ═══════════════════════════ ACT 04 · THE DOCUMENTS SPEAK ═══════════════════════════
@scene(8, 'the ipo document', 'act 04 · the documents speak')
def s08():
    s, h = doc('doc_s1cover', 60, 200, 1100, 0.2, 9.5, hls=(2.0,))
    heading('aug 14, 2019', 1240, 260, 84, 1.4, 9.5, col=RED); text('the we company files to go public', 1244, 370, 30, 2.4, 9.5, font='outfit500', wrap=600)
    marker('08.1', 0, 9.5)
    CX.beat()
    cards = [('financial statements', 'doc_s1fin', 9.5), ('risk factors', 'doc_risk', 13.0), ('related-party transactions', 'doc_related', 16.5)]
    for k, (lab, d, t) in enumerate(cards):
        x = 60 + k * 610; iw, ih = LAY[d]
        rect(x, 150, 580, 520, PANEL, t, 25.5); flash(x, 150, 580, 520, t); text(f'{k + 1:02d}', x + 24, 170, 22, t, 25.5, col=RED, font='mono600'); heading(lab, x + 24, 204, 36, t, 25.5)
        image(d, x + 24, 270, 532, 380, t + .4, 25.5, contain=True, fy=0, fx=0, z0=1.0, z1=1.05); EV.append((T(t), 'paper'))
    text('form s-1 (aug 14, 2019) · related-party excerpt from s-1/a (sep 3, 2019) · transcriptions', 60, 700, 20, 10.0, 25.5, col=GREY, font='mono400')
    marker('08.2', 9.5, 25.5)
    CX.beat()
    heading('the evidence was public.', 960, 470, 90, 25.5, 30, al='CENTER'); EV.append((T(25.5), 'low'))
    marker('08.3', 25.5, 30)

@scene(9, 'the financial evidence')
def s09():
    tag('form s-1 · year ended dec 31, 2018 · $ thousands', 60, 84, 0, 30)
    X0 = 520; k = 1200 / 1927419        # one scale for all three bars
    bars = [('2018 revenue', 1821751, '$1.82 billion', TXT, 1.0), ('2018 net loss', 1927419, '$1.93 billion loss', RED, 3.0), ('net loss attributable to\nwework companies inc.', 1610792, '$1.61 billion loss', RED, 5.0)]
    for i, (lab, v, s, col, t) in enumerate(bars):
        y = 180 + i * 150; text(lab, 60, y + 6, 28, t, 10, font='outfit700' if i < 2 else 'outfit500', col=TXT)
        rect(X0, y, v * k, 80, col, t, 10, grow=(t, t + 1.2, 'x')); text(s, X0 + 20, y + 18, 36, t + 1.2, 10, col=BG if col == TXT else TXT, font='outfit700')
        EV.append((T(t), 'draw'))
    text('net loss is the bottom line after all expenses, not operating expenses', 64, 640, 26, 6.0, 10, col=GREY, font='outfit500')
    text('the s-1 reports both figures; $1.61 billion is the share attributable to wework companies inc.', 64, 684, 22, 7.0, 10, col=GREY, font='outfit300')
    for t0, code in [(0, '09.1')]: marker(code, 0, 10)
    CX.beat()
    s, h = doc('doc_s1fin', 60, 160, 1200, 10.0, 30, hls=(11.0, 12.4, 13.8))
    text('revenue', 1320, 200, 24, 11.2, 30, col=GREY, font='mono600'); heading('2016 → 2018', 1320, 236, 44, 11.2, 30)
    heading('$436.1m → $1.82b', 1320, 300, 52, 11.8, 30)
    text('net loss', 1320, 400, 24, 12.6, 30, col=RED, font='mono600'); heading('$429.7m → $1.93b', 1320, 436, 52, 12.6, 30, col=RED)
    marker('09.2', 10, 20)
    heading('revenue was growing.', 60, 720, 64, 20.6, 30); heading('so were the questions.', 60, 800, 64, 22.4, 30, col=RED); EV.append((T(22.4), 'low'))
    marker('09.3', 20, 30)

@scene(10, 'governance')
def s10():
    s, h = doc('doc_related', 60, 150, 1080, 0.2, 10, hls=(1.4, 4.8))
    heading('trademark transaction', 1220, 200, 48, 0.8, 10); heading('≈ $5.9 million', 1220, 270, 72, 1.6, 10, col=RED)
    text('paid in partnership interests', 1224, 370, 26, 2.2, 10, col=GREY, font='outfit300')
    heading('later unwound', 1220, 460, 48, 5.0, 10); text('at adam’s direction (s-1/a, sep 3, 2019)', 1224, 524, 22, 5.4, 10, col=GREY, font='mono400')
    marker('10.1', 0, 10)
    CX.beat()
    s, h = doc('doc_votes', 60, 150, 1000, 10.0, 22, hls=(10.8, 12.0))
    # votes per share: 1 vs 20 vs 10 (squares)
    X, Y = 1140, 170
    text('votes per share', X, Y, 24, 10.4, 22, col=GREY, font='mono600')
    for row, (lab, n, col, t) in enumerate([('class a · ordinary', 1, TXT, 11.0), ('high-vote · s-1, aug 14', 20, RED, 12.4), ('high-vote · s-1/a, sep 13', 10, RED, 14.4)]):
        y = Y + 50 + row * 150; text(lab, X, y, 24, t, 22, font='outfit500')
        for j in range(n): rect(X + j * 34, y + 44, 28, 28, col, t + j * .04, 22)
        text(str(n), X + n * 34 + 16, y + 40, 40, t + .8, 22, col=col, font='outfit700'); EV.append((T(t), 'mark'))
    text('the proposal changed before the ipo was withdrawn', X, 700, 24, 16.0, 22, col=GREY, font='outfit300')
    marker('10.2', 10, 22)
    CX.beat()
    heading('who controlled the company?', 960, 470, 90, 22.5, 30, al='CENTER'); EV.append((T(22.5), 'low'))
    marker('10.3', 22, 30)

# ═══════════════════════════ ACT 05 · THE BREAK ═══════════════════════════
@scene(11, 'the failed ipo', 'act 05 · the break')
def s11():
    Y = 560; X0, X1 = 160, 1760
    pts = [('aug 14, 2019', 'ipo registration · form s-1', 160, 1.0), ('sep 24, 2019', 'adam neumann steps down as ceo', 760, 6.0), ('sep 30, 2019', 'ipo withdrawn · form rw', 1300, 11.0)]
    rect(X0, Y, 1300 - X0, 4, RED, 0.6, 30, grow=(0.6, 11.0, 'x')); EV.append((T(0.6), 'draw'))
    for (d, lab, x, t) in pts:
        sprite('dot_red', x, Y + 2, t, 30); text(d, x, Y - 120, 30, t, 30, col=RED, font='mono600', al='CENTER' if x > 200 else 'LEFT'); text(lab, x, Y - 80, 28, t, 30, font='outfit700', al='CENTER' if x > 200 else 'LEFT', wrap=360 if x > 200 else 0); EV.append((T(t), 'mark'))
    image('ph_neumann', 620, 640, 280, 260, 6.0, 11.0, fx=.5, fy=.25); tag('photo · 2015', 620, 614, 6.0, 11.0)
    s, h = doc('doc_rw', 1080, 650, 760, 11.2, 30, hls=(12.0,))
    # the line breaks: a dashed continuation that never arrives
    for j in range(6): rect(1320 + j * 70, Y, 36, 4, '#3a3a3a', 13.0 + j * .1, 30)
    text('ipo', 1720, Y - 40, 26, 13.6, 30, col=GREY, font='mono600', al='CENTER'); rect(1690, Y + 14, 60, 3, RED, 14.0, 30)
    heading('the ipo never happened.', 960, 190, 80, 18.0, 30, al='CENTER'); EV.append((T(13.0), 'break')); EV.append((T(18.0), 'low'))
    for t0, code in [(0, '11.1'), (10, '11.2'), (20, '11.3')]: marker(code, t0, t0 + 10)

@scene(12, 'the rescue')
def s12():
    text('oct 22, 2019', 60, 150, 30, 0.2, 10, col=RED, font='mono600'); heading('softbank rescue package', 60, 190, 64, 0.2, 10)
    items = [('$5 billion', 'new financing'), ('up to $3 billion', 'tender offer for existing shareholders'), ('$1.5 billion', 'existing commitment, accelerated')]
    for k, (v, s) in enumerate(items):
        y = 320 + k * 140; rect(60, y, 1180, 120, PANEL, 1.0 + k * .8, 10); flash(60, y, 1180, 120, 1.0 + k * .8)
        heading(v, 90, y + 22, 56, 1.0 + k * .8, 10, col=RED if k == 0 else TXT); text(s, 600, y + 42, 28, 1.0 + k * .8, 10, font='outfit500')
    text('as reported (axios, oct 22, 2019) · the tender offer was later abandoned by softbank', 64, 760, 22, 4.0, 10, col=GREY, font='mono400')
    marker('12.1', 0, 10)
    CX.beat()
    text('mar 26, 2021', 60, 150, 30, 10.0, 20, col=RED, font='mono600'); heading('public listing via spac', 60, 190, 64, 10.0, 20)
    s, h = doc('doc_bowx', 60, 320, 1200, 10.6, 20, hls=(11.6,))
    heading('≈ $9 billion', 1320, 330, 96, 12.4, 20, col=RED); text('announced enterprise value', 1324, 450, 30, 12.8, 20, font='outfit500')
    text('listed on the nyse: oct 21, 2021 (bowx merger)', 64, 600, 26, 14.0, 20, col=GREY, font='outfit300')
    marker('12.2', 10, 20)
    CX.beat()
    for k, (yr, v, lab) in enumerate([('2019', '$47 billion', 'private valuation · reported'), ('2021', '≈ $9 billion', 'enterprise value · announced')]):
        x = 60 + k * 940; text(yr, x, 200, 30, 20.2 + k * .6, 30, col=RED, font='mono600'); heading(v, x, 240, 96, 20.2 + k * .6, 30); text(lab, x + 4, 360, 28, 20.2 + k * .6, 30, col=GREY, font='outfit500')
    rect(958, 180, 4, 260, RED, 21.0, 30); text('different measures · not directly comparable', 960, 480, 26, 21.6, 30, col=RED, font='mono600', al='CENTER')
    heading('the dream was repriced.', 960, 640, 90, 24.0, 30, al='CENTER'); EV.append((T(24.0), 'low'))
    marker('12.3', 20, 30)

# ═══════════════════════════ ACT 06 · THE RECKONING ═══════════════════════════
@scene(13, 'a world without offices', 'act 06 · the reckoning')
def s13():
    image('ph_empty2', 60, 110, 1100, 780, 0, 10.5, fx=.5, fy=.5, z0=1.0, z1=1.06); tag('photo · empty office, vienna · may 2020 · iaea · cc by 2.0', 60, 84, 0, 10.5)
    text('2020', 1240, 240, 40, 0.8, 10.5, col=RED, font='mono600'); heading('remote work', 1240, 290, 84, 1.2, 10.5); heading('disruption', 1240, 380, 84, 1.2, 10.5)
    text('offices emptied as staff worked from home', 1244, 500, 26, 2.4, 10.5, col=GREY, font='outfit300', wrap=600)
    marker('13.1', 0, 10.5)
    CX.beat()
    image('ph_empty1', 60, 110, 860, 500, 10.5, 20, z0=1.0, z1=1.04); tag('photo · vienna · may 2020', 60, 84, 10.5, 20)
    Y = 760; rect(100, Y, 1720, 3, GREY, 10.5, 30)
    ev = [(100, '2019', 's-1: $33.95b in lease commitments', 11.0), (560, '2020', 'pandemic: demand for offices falls', 12.4), (1020, 'oct 2021', 'public via spac', 13.8), (1480, 'aug 2023', 'plan to cut rent and tenancy costs', 15.2)]
    for (x, d, lab, t) in ev:
        sprite('dot_red', x, Y + 1, t, 30); text(d, x, Y + 26, 24, t, 30, col=RED, font='mono600'); text(lab, x, Y + 62, 22, t, 30, font='outfit500', wrap=420); EV.append((T(t), 'mark'))
    text('aug 2023 entry: form 10-q, quarter ended june 30, 2023', 960, 680, 20, 15.6, 30, col=GREY, font='mono400')
    marker('13.2', 10.5, 21)
    CX.beat()
    heading('a new shock.', 60, 180, 96, 21.0, 30); heading('an old problem.', 60, 300, 96, 22.6, 30, col=RED); EV.append((T(22.6), 'low'))
    marker('13.3', 21, 30)

@scene(14, 'the warning')
def s14():
    s, h = doc('doc_tenq', 60, 200, 1200, 0.2, 10.5, hls=(1.4,))
    text('aug 8, 2023', 1320, 210, 30, 0.6, 10.5, col=RED, font='mono600'); heading('the warning', 1320, 250, 72, 0.6, 10.5); text('going-concern disclosure', 1324, 350, 28, 1.4, 10.5, col=GREY, font='outfit500')
    text('as of june 30, 2023: $205 million in cash and cash equivalents', 64, 200 + h + 40, 26, 4.0, 10.5, font='outfit500')
    marker('14.1', 0, 10.5)
    CX.beat()
    s, h = doc('doc_q3', 60, 200, 1200, 10.5, 20.5, hls=(11.4,))
    heading('≈ $462 million', 1320, 230, 80, 12.0, 20.5, col=TXT); text('cash and cash equivalents, sep 30, 2023', 1324, 340, 26, 12.4, 20.5, col=GREY, font='outfit500', wrap=540)
    text('reported in november 2023, after the filing', 1324, 430, 22, 13.4, 20.5, col=GREY, font='mono400', wrap=540)
    marker('14.2', 10.5, 20.5)
    CX.beat()
    image('doc_petition', 60, 110, 620, 790, 20.5, 30, fy=0, z0=1.0, z1=1.08); EV.append((T(20.5), 'boom'))
    tag('voluntary petition · doc 1 · filed 11/06/23', 60, 84, 20.5, 30)
    text('aug 2023', 760, 300, 30, 21.0, 30, col=GREY, font='mono600'); text('warning', 760, 340, 40, 21.0, 30, col=GREY, font='outfit700')
    rect(760, 420, 900, 3, RED, 21.6, 30, grow=(21.6, 23.0, 'x'))
    text('nov 6, 2023', 1660, 300, 30, 23.0, 30, col=RED, font='mono600', al='RIGHT'); heading('chapter 11', 1660, 340, 64, 23.0, 30, al='RIGHT')
    text('three months between the warning and the filing', 760, 480, 26, 24.4, 30, col=GREY, font='outfit300')
    marker('14.3', 20.5, 30)

@scene(15, 'what survived')
def s15():
    image('doc_petition', 60, 140, 560, 700, 0.2, 20.5, fy=0); tag('nov 6, 2023 · chapter 11', 60, 114, 0.2, 20.5)
    s, h = doc('doc_emerge', 1300, 300, 560, 2.0, 20.5, hls=(3.0,)); tag('jun 11, 2024 · emergence', 1300, 274, 2.0, 20.5)
    rect(640, 480, 640, 4, RED, 4.0, 20.5, grow=(4.0, 6.5, 'x')); sprite('dot_red', 640, 482, 4.0, 20.5); sprite('dot_red', 1280, 482, 6.5, 20.5); EV.append((T(4.0), 'draw'))
    text('7 months', 960, 500, 24, 6.5, 20.5, col=RED, font='mono600', al='CENTER')
    marker('15.1', 0, 10)
    CX.beat()
    image('ph_chicago', 660, 560, 600, 300, 10.5, 20.5, fy=.6); tag('photo · wework, chicago · 2018', 660, 534, 10.5, 20.5)
    text('the company continued, in reorganized form', 960, 890, 28, 12.0, 20.5, font='outfit500', al='CENTER')
    marker('15.2', 10, 20)
    heading('the business survived.', 960, 400, 80, 20.6, 30, al='CENTER'); heading('the original valuation story did not.', 960, 510, 64, 22.5, 30, col=RED, al='CENTER'); EV.append((T(22.5), 'low'))
    marker('15.3', 20, 30)

@scene(16, 'the final verdict')
def s16():
    v = heading('$47,000,000,000', 960, 420, 170, 0.2, 14.0, al='CENTER'); EV.append((T(0.2), 'boom'))
    v.blend_alpha = 1; v.keyframe_insert('blend_alpha', frame=F(T(9.5))); v.blend_alpha = .0; v.keyframe_insert('blend_alpha', frame=F(T(14.0)) - 1)
    cards = [('long-term lease commitments', '$33.95b + $13.1b signed (s-1)', 60, 120, 1.4), ('expensive expansion', '2018 net loss $1.93b (s-1)', 1260, 120, 2.8), ('governance concerns', '20 votes per share; trademark deal (s-1)', 60, 760, 4.2), ('changing office demand', '2020 pandemic; going concern, aug 2023', 1260, 760, 5.6)]
    for (h_, s, x, y, t) in cards:
        # cards converge toward the valuation
        c1 = rect(x, y, 600, 200, PANEL, t, 14.0); c2 = rect(x, y, 6, 200, RED, t, 14.0)
        t1 = text(h_, x + 30, y + 40, 34, t, 14.0); t2 = text(s, x + 30, y + 110, 22, t, 14.0, col=GREY, font='mono400')
        dx, dy = (330 if x < 900 else -330), (90 if y < 500 else -90)
        for st in (c1, c2, t1, t2):
            tr = st.transform; ox, oy = tr.offset_x, tr.offset_y
            tr.keyframe_insert('offset_x', frame=F(T(7.0))); tr.keyframe_insert('offset_y', frame=F(T(7.0)))
            tr.offset_x, tr.offset_y = ox + dx, oy - dy; tr.keyframe_insert('offset_x', frame=F(T(10.5))); tr.keyframe_insert('offset_y', frame=F(T(10.5)))
            fade(st, t, 14.0, 1, 0, 1.2)
        flash(x, y, 600, 200, t); EV.append((T(t), 'mark'))
    marker('16.1', 0, 14)
    CX.beat()
    heading('a useful product is not always', 960, 400, 80, 14.5, 23.0, al='CENTER'); heading('a sustainable investment.', 960, 500, 80, 15.5, 23.0, col=RED, al='CENTER'); EV.append((T(14.5), 'low'))
    marker('16.2', 14, 23)
    CX.beat()
    e = heading('brand coroner.', 960, 420, 110, 23.4, 30, al='CENTER'); f = text('every brand leaves evidence.', 960, 570, 40, 24.6, 30, col=GREY, font='outfit500', al='CENTER')
    rect(810, 555, 300, 2, RED, 24.2, 30, grow=(24.2, 25.0, 'x'))
    for st in (e, f): fade(st, 23.4, 30, 1, 0, 2.0)
    marker('16.3', 23, 30)

# ── assemble: one meta strip per scene on the master timeline ──
bg = SE.sequences.new_effect('background', 'COLOR', 1, frame_start=1, frame_end=DUR * FPS + 1); bg.color = hexc(BG)
for (i, title, act, fn) in SCENES:
    base = (i - 1) * 30
    meta = SE.sequences.new_meta(f'S{i:02d} · {title}', 2, F(base))
    CX = Ctx(meta, base)
    b = meta.sequences.new_effect(nm('bg'), 'COLOR', 1, frame_start=F(base), frame_end=F(base + 30)); b.color = hexc(BG)
    chrome(i, title, act); CX.hold()
    fn()
    meta.frame_final_start, meta.frame_final_end = F(base), F(base + 30)
    meta.blend_type = 'ALPHA_OVER'
vig = SE.sequences.new_image('vignette', os.path.join(A, 'vignette.png'), 3, 1, fit_method='ORIGINAL'); vig.frame_final_duration = DUR * FPS; vig.blend_type = 'ALPHA_OVER'
# fade from black at the very start, fade to black at the end
fb = SE.sequences.new_effect('fade_to_black', 'COLOR', 4, frame_start=F(476.0), frame_end=DUR * FPS + 1); fb.color = (0, 0, 0); fb.blend_type = 'ALPHA_OVER'
fb.blend_alpha = 0; fb.keyframe_insert('blend_alpha', frame=F(476.0)); fb.blend_alpha = 1; fb.keyframe_insert('blend_alpha', frame=F(479.5))
snd = os.path.join(D, 'audio', 'mix.flac')
if os.path.exists(snd): SE.sequences.new_sound('sound · underscore + foley', snd, 6, 1)
json.dump(sorted(EV), open(os.path.join(D, 'audio', 'events.json'), 'w'))
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(D, 'wework.blend')); bpy.ops.file.make_paths_relative(); bpy.ops.wm.save_mainfile()
print('BUILD OK', len(SCENES), 'scenes', len(EV), 'events', NAMES[0], 'strips')
