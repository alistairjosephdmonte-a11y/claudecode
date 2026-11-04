"""BRAND CORONER · CASE 004 · KODAK — "they invented their downfall"
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
TLP = os.path.join(D, 'vo', 'timeline.json'); TL = json.load(open(TLP)) if os.path.exists(TLP) else None
if TL: DUR = TL['total']
def hexc(h, a=None): h = h.lstrip('#'); c = tuple(int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)); return c + ((a,) if a is not None else ())
BG, RED, TXT, GREY, PANEL, RULE = '#080808', '#FF2400', '#F5F3EF', '#858585', '#121212', '#2B2B2B'
F = lambda t: int(round(t * FPS)) + 1

# ── scene setup ──
for s in list(bpy.data.scenes)[1:]: bpy.data.scenes.remove(s)
sc = bpy.context.scene; sc.name = 'brand_coroner_case004_kodak'
sc.render.resolution_x, sc.render.resolution_y, sc.render.resolution_percentage = W, H, 100
sc.render.fps = FPS; sc.frame_start, sc.frame_end = 1, int(round(DUR * FPS))
sc.view_settings.view_transform = 'Standard'; sc.view_settings.look = 'None'; sc.sequencer_colorspace_settings.name = 'sRGB'
if sc.sequence_editor: sc.sequence_editor_clear()
SE = sc.sequence_editor_create()
FONTS = {k: bpy.data.fonts.load(os.path.join(FT, f'{k}.ttf')) for k in ['outfit700', 'outfit500', 'outfit300', 'mono400', 'mono600', 'serifi']}
EV = []          # sound cues: (t, kind)
NAMES = [0]
def nm(p): NAMES[0] += 1; return f'{p}{NAMES[0]:04d}'

class Ctx:
    def __init__(self, meta, base, warp=None): self.m, self.base, self.c, self.keep, self.warp = meta, base, 2, 2, warp or [(0, 0), (30, 30)]
    def ch(self): self.c += 1; assert self.c < 127, 'too many channels'; return self.c
    def beat(self): self.c = self.keep
    def hold(self): self.keep = self.c
CX = None
def T(t):                       # design time (0–30 grid) → film time, piecewise-linear warp onto the voiceover
    w = CX.warp; t = max(0.0, min(30.0, t))
    for (a0, b0), (a1, b1) in zip(w, w[1:]):
        if t <= a1: return CX.base + b0 + (b1 - b0) * (t - a0) / (a1 - a0)
    return CX.base + w[-1][1]

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
    s = rect(x, y, w, h, '#FFFFFF', t0, t0 + d + .05); s.blend_alpha = .55; s.keyframe_insert('blend_alpha', frame=F(T(t0))); s.blend_alpha = 0; s.keyframe_insert('blend_alpha', frame=F(T(t0 + d)))

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
    pass

def chrome(i, title, act=None):
    text('brand coroner · case 004', 60, 40, 16, 0, 30, col=GREY, font='mono600')
    text(f'{i:02d} · {title}', 1860, 40, 16, 0, 30, col=GREY, font='mono600', al='RIGHT')
    if act: text(act, 60, 70, 18, 0, 3.5, col=RED, font='mono600')

SCENES = []
def scene(i, title, act=None):
    def deco(fn): SCENES.append((i, title, act, fn)); return fn
    return deco

# ── Kodak scene designs. Authored on a 0–30 s grid per scene; L(k) is the grid time of narration line k, and
#    vo/timeline.json warps every grid onto the voiceover so each beat lands on its line. ──
def L(k, d=0.0): return 1.0 + 27.0 * (k - 1) / CX.n + d
def have(k): return os.path.exists(os.path.join(A, k + '.png'))
SA = {k for k, v in json.load(open(os.path.join(D, 'photos.json'))).items() if v.get('sa')}
def chips(items, x, y, t, dt=.8, t1=30, col=TXT, size=34, gap=70, bar=RED):
    for k, s_ in enumerate(items):
        rect(x, y + k * gap + size * .25, 8, size * .85, bar, t + k * dt, t1); heading(s_, x + 26, y + k * gap, size, t + k * dt, t1, col=col)
def photo(k, x, y, w, h, t0, t1, tagtxt, **kw):
    """graded photo (cover crop, optional push). CC BY-SA photos are shown unaltered: whole frame, contained, no crop or push."""
    if not have('ph_' + k): rect(x, y, w, h, PANEL, t0, t1); text('[photo unavailable]', x + 20, y + 20, 20, t0, t1, col=GREY, font='mono400'); return None
    if k in SA:
        rect(x, y, w, h, '#101010', t0, t1); kw = {'contain': True}
    im = image('ph_' + k, x, y, w, h, t0, t1, **kw); tag(tagtxt, x, y - 26, t0, t1); EV.append((T(t0), 'shutter')); return im
def hline(x0, x1, y, t0, t1, ta, tb, col=RED, th=4, head=True):
    if x1 >= x0: rect(x0, y - th / 2, x1 - x0, th, col, t0, t1, grow=(ta, tb, 'x'))
    else: rect(x1, y - th / 2, x0 - x1, th, col, t0, t1, grow=(ta, tb, 'xr'))
    if head: sprite(f"arrow_{'red' if col == RED else 'grey'}_{'r' if x1 >= x0 else 'l'}", x1, y, tb, t1)
def up(s, y, h):          # make a 'y'-grown rect grow upward from its bottom edge
    s.transform.origin = (0, 0); s.transform.offset_y = H - y - h; return s
def vline(x, y0, y1, t0, t1, ta, tb, col=RED, th=4, head=True):
    top, h = min(y0, y1), abs(y1 - y0); s = rect(x - th / 2, top, th, h, col, t0, t1, grow=(ta, tb, 'y'))
    if y1 < y0: up(s, top, h)
    if head: sprite(f"arrow_{'red' if col == RED else 'grey'}_{'d' if y1 >= y0 else 'u'}", x, y1, tb, t1)
def card_box(x, y, w, h, t0, t1, edge=RED):
    rect(x, y, w, h, PANEL, t0, t1); rect(x, y, 6, h, edge, t0, t1)
def check(x, y, t, t1=30, ok=True, size=44):
    text('✓' if ok else '✕', x, y, size, t, t1, col=RED, font='outfit700'); EV.append((T(t), 'mark'))

# ═══════════════════════════ ACT 01 · THE INVENTION ═══════════════════════════
@scene(1, 'the camera that shouldn’t have existed', 'act 01 · the invention')
def s01():
    rect(560, 538, 800, 4, RED, .3, L(1), grow=(.3, 1.6, 'x')); EV.append((T(.3), 'tape'))
    heading('1975', 960, 330, 300, L(1, -.6), L(2), al='CENTER'); EV.append((T(L(1, -.6)), 'shutter'))
    text('kodak laboratory · rochester, new york', 960, 690, 30, L(1), L(2), col=GREY, font='mono600', al='CENTER')
    CX.beat()
    photo('proto', 60, 140, 820, 820, L(2), 30, 'drawing of the 1975 prototype · b. labévue 2022 · cc by-sa 4.0 · not a photograph')
    photo('sasson', 1480, 140, 380, 480, L(1, 3.0), 30, 'steven sasson · photokina 2010 · aljawad · cc by 3.0', fx=.5, fy=.3)
    text('1975', 960, 130, 30, L(2), 30, col=RED, font='mono600'); heading('the prototype', 960, 166, 56, L(2), 30)
    specs = [('≈ 8 POUNDS', L(2, .4)), ('BLACK-AND-WHITE IMAGES', L(2, 2.0)), ('MAGNETIC TAPE RECORDING', L(2, 3.4)), ('100 × 100 PIXELS', L(3))]
    for k, (s_, t) in enumerate(specs):
        y = 280 + k * 84; card_box(960, y, 480, 68, t, 30); heading(s_, 990, y + 16, 30, t, 30); EV.append((T(t), 'mark'))
    text('= 10,000 pixels', 1450, 535, 24, L(3, .6), 30, col=GREY, font='mono400', al='RIGHT')
    heading('primitive.', 960, 660, 52, L(4), 30, col=GREY); heading('revolutionary.', 1240, 660, 52, L(5), 30, col=RED)
    heading('a camera without photographic film', 960, 760, 44, L(6), 30)
    rect(960, 820, 760, 4, RED, L(6, .4), 30, grow=(L(6, .4), L(6, 1.4), 'x'))
    heading('built by kodak.', 960, 860, 60, L(7), 30, col=RED); EV.append((T(L(7)), 'low'))

@scene(2, 'the contradiction')
def s02():
    photo('tower', 60, 140, 760, 820, 0, 30, 'photo · kodak tower, rochester, ny · 2009 · mark a. lackey · cc by 2.0', fx=.5, fy=.4, z0=1.0, z1=1.08)
    text('THIRTY-SEVEN YEARS LATER', 900, 140, 24, L(1), L(3), col=GREY, font='mono600')
    heading('january 19, 2012', 900, 176, 88, L(1, .8), L(3), col=TXT); rect(900, 290, 720, 6, RED, L(1, 1.6), L(3), grow=(L(1, 1.6), L(1, 2.6), 'x'))
    heading('chapter 11 bankruptcy protection', 900, 320, 40, L(1, 2.2), L(3), col=RED)
    doc('doc_ch11', 900, 420, 960, L(1, 3.0), L(3), hls=(L(1, 4.0), L(2)))
    text('1975: digital innovation  →  2012: bankruptcy protection', 900, 800, 28, L(2), L(3), font='mono600', col=GREY)
    CX.beat()
    text('THE POPULAR EXPLANATION', 900, 160, 24, L(3), 30, col=GREY, font='mono600')
    for k, s_ in enumerate(['invented the digital camera', 'ignored it', 'paid the price']):
        heading(s_, 900, 220 + k * 80, 52, L(4, k * .9), 30, col=GREY if k != 1 else TXT)
    rect(890, 335, 280, 5, RED, L(5), 30, grow=(L(5), L(5, .8), 'x')); text('not quite', 1190, 318, 30, L(5, .6), 30, col=RED, font='mono600'); EV.append((T(L(5)), 'mark'))
    heading('kodak invested in digital.', 900, 520, 64, L(7), 30, col=RED); EV.append((T(L(7)), 'low'))
    heading('how did kodak see the future —', 900, 700, 48, L(9), 30)
    heading('and still lose its position in it?', 900, 760, 48, L(9, 1.2), 30, col=RED)

# ═══════════════════════════ ACT 02 · THE EMPIRE ═══════════════════════════
@scene(3, 'the company that owned memories', 'act 02 · the empire')
def s03():
    ads = [('ad1921', 'eastman kodak advertisement · 1921 · public domain'), ('asyougo', 'photoplay · jan 1921 · public domain'), ('vacation', 'canadian kodak advertisement · aug 1922 · public domain')]
    for k, (a_, tg) in enumerate(ads):
        photo(a_, 60 + k * 610, 150, 580, 760, L(1, k * 1.2), L(4), tg, contain=True)
    CX.beat()
    for k, (p_, tg) in enumerate([('instamatic', 'kodak pocket instamatic 200 · delaville · cc by 2.0'), ('verichrome', 'kodak verichrome pan 120 · kevinfarrugia · cc0'), ('film', 'kodak ultramax 400 · veera.sj 2018 · cc0')]):
        photo(p_, 60 + k * 610, 150, 580, 440, L(3, k * .8), 30, tg, fx=.5, fy=.5, z0=1.0, z1=1.05)
    for k, s_ in enumerate(['CAMERAS', 'FILM', 'PAPER', 'PROCESSING']):
        x = 60 + k * 455; card_box(x, 640, 430, 80, L(3, .4 + k * .7), 30); heading(s_, x + 30, 660, 36, L(3, .4 + k * .7), 30); EV.append((T(L(3, .4 + k * .7)), 'mark'))
    rect(1280, 592, 520, 5, '#E8B400', L(4), 30, grow=(L(4), L(4, .8), 'x')); text('the yellow box', 1280, 604, 22, L(4, .4), 30, col='#E8B400', font='mono600')
    heading('the system around every photograph', 60, 800, 56, L(6), 30, col=RED)
    text('→ customers kept buying', 64, 880, 34, L(7), 30, font='outfit500'); EV.append((T(L(6)), 'low'))

@scene(4, 'the perfect business model')
def s04():
    text('conceptual business model · not a revenue analysis', 60, 84, 20, 0, 30, col=GREY, font='mono400')
    N = [('BUY A CAMERA', L(2)), ('BUY FILM', L(3)), ('DEVELOP & PRINT', L(4)), ('BUY MORE FILM', L(5))]
    X = [100, 560, 1020, 1480]
    for k, ((s_, t), x) in enumerate(zip(N, X)):
        card_box(x, 300, 360, 150, t, 30, edge=GREY if k == 0 else RED); heading(s_, x + 180, 350, 34, t, 30, al='CENTER'); EV.append((T(t), 'advance'))
        if k: hline(X[k - 1] + 360, x - 6, 375, t - .5, 30, t - .5, t)
    text('one-time purchase', 280, 470, 24, L(2, 1), 30, col=GREY, font='mono600', al='CENTER')
    # recurring loop: from BUY MORE FILM back to DEVELOP & PRINT
    vline(1660, 450, 600, L(6), 30, L(6), L(6, .6), head=False); hline(1660, 1200, 600, L(6), 30, L(6, .6), L(6, 1.4), head=False)
    vline(1200, 600, 456, L(6), 30, L(6, 1.4), L(6, 2.0))
    text('recurring demand', 1430, 616, 26, L(6, 1.4), 30, col=RED, font='mono600', al='CENTER'); EV.append((T(L(6)), 'draw'))
    heading('an extraordinarily attractive structure', 100, 700, 48, L(7), 30)
    text('it depended on one thing:', 100, 800, 30, L(8), 30, col=GREY, font='outfit500')
    heading('people had to keep using physical film', 100, 850, 52, L(9), 30, col=RED)
    rect(1650, 492, 20, 60, BG, L(10), 30); text('✕', 1660, 490, 56, L(10), 30, col=RED, font='outfit700', al='CENTER'); EV.append((T(L(10)), 'break'))
    text('digital removes the requirement', 1430, 652, 22, L(10, .5), 30, col=RED, font='mono600', al='CENTER')

# ═══════════════════════════ ACT 03 · THE WARNING ═══════════════════════════
@scene(5, 'the future inside the building', 'act 03 · the warning')
def s05():
    for k, s_ in enumerate(['LIGHT', 'ELECTRONIC SENSOR', 'DIGITAL INFORMATION']):
        x = 100 + k * 600; t = L(1, k * 1.0); card_box(x, 160, 520, 110, t, 30, edge=RED if k == 2 else GREY); heading(s_, x + 260, 196, 36, t, 30, al='CENTER')
        if k: hline(x - 80, x - 6, 215, t - .4, 30, t - .4, t)
    for k, s_ in enumerate(['no chemical development', 'no conventional film negative', 'no print required to see the image']):
        y = 360 + k * 80; check(100, y - 6, L(2 + k), ok=False); heading(s_, 170, y, 42, L(2 + k), 30)
    text('THE LIMITS IN 1975', 1100, 340, 24, L(5), 30, col=GREY, font='mono600')
    chips(['bulky · ≈ 8 lb', 'limited quality · 100 × 100, b&w', 'slow storage · ≈ 23 s per image to tape'], 1100, 390, L(6), dt=1.0, size=30, gap=60, bar=GREY, col=GREY)
    text('23 s: reported time to record one image', 1100, 580, 18, L(6, 2), 30, col=GREY, font='mono400')
    # 1975 → decades of digital development
    rect(100, 760, 1720, 3, GREY, L(7), 30, grow=(L(7), L(8), 'x')); sprite('dot_red', 100, 761, L(7), 30); text('1975', 100, 780, 26, L(7), 30, col=RED, font='mono600')
    for yr in (1985, 1995, 2005): sprite('dot_grey', 100 + (yr - 1975) / 37 * 1720, 761, L(8), 30); text(str(yr), 100 + (yr - 1975) / 37 * 1720, 780, 22, L(8), 30, col=GREY, font='mono400', al='CENTER')
    text('kodak keeps developing digital imaging', 960, 700, 28, L(8), 30, font='outfit500', al='CENTER')
    heading('the question was the business, not the possibility', 960, 870, 48, L(9), 30, col=RED, al='CENTER'); EV.append((T(L(9)), 'low'))

@scene(6, 'the profit trap')
def s06():
    text('illustrative comparison · no margin figures implied', 60, 84, 20, 0, 30, col=GREY, font='mono400')
    rect(958, 130, 4, 760, RULE, 0, 30)
    heading('film economics', 100, 150, 56, L(1), 30); text('RECURRING REVENUE', 100, 222, 24, L(1), 30, col=RED, font='mono600')
    items = ['film sales', 'development', 'printing', 'repeat purchases']
    for k, s_ in enumerate(items):
        y = 300 + k * 90; check(100, y - 4, L(1, 1 + k * .7)); heading(s_, 170, y, 44, L(1, 1 + k * .7), 30)
    heading('digital economics', 1020, 150, 56, L(2), 30, col=GREY); text('ONE-TIME HARDWARE', 1020, 222, 24, L(2), 30, col=GREY, font='mono600')
    for k, s_ in enumerate(['electronic capture', 'digital storage', 'screen viewing', 'electronic sharing']):
        y = 300 + k * 90; heading(s_, 1020, y, 44, L(2, .6 + k * .6), 30, col=GREY)
    for k in range(3):     # recurring streams threatened
        y = 300 + k * 90; rect(160, y + 30, 420, 5, RED, L(5, k * .5), 30, grow=(L(5, k * .5), L(5, k * .5 + .6), 'x')); EV.append((T(L(5, k * .5)), 'mark'))
    text('threatened', 600, 390, 28, L(5, 1.6), 30, col=RED, font='mono600')
    heading('same profitability? not automatically.', 100, 720, 44, L(7), 30, col=GREY)
    heading('two economic worlds at once', 960, 850, 60, L(8), 30, col=RED, al='CENTER'); EV.append((T(L(8)), 'low'))

# ═══════════════════════════ ACT 04 · THE DIGITAL REVOLUTION ═══════════════════════════
@scene(7, 'the myth of ignoring digital', 'act 04 · the digital revolution')
def s07():
    heading('the myth of ignoring digital', 60, 130, 56, L(1), 30, col=GREY)
    rect(60, 210, 1800, 3, RULE, L(1), 30)
    M = [('1991', 'kodak professional digital camera system', 'dcs · nikon f3 body + storage unit', L(3)),
         ('1995', 'kodak dc40', 'consumer digital camera · launched march 1995', L(4)),
         ('2001', 'kodak easyshare', 'consumer digital camera system', L(5))]
    for k, (yr, a_, b_, t) in enumerate(M):
        y = 250 + k * 170; card_box(60, y, 1800, 140, t, 30); check(100, y + 38, t, size=56)
        heading(yr, 180, y + 30, 64, t, 30, col=RED); heading(a_, 420, y + 28, 44, t, 30); text(b_, 420, y + 88, 24, t, 30, col=GREY, font='mono400')
    heading('kodak did invest in digital.', 60, 800, 64, L(6), 30); EV.append((T(L(6)), 'low'))
    heading('entering a market  ≠  a profitable position in it', 60, 900, 44, L(8), 30, col=RED)

@scene(8, 'the digital products')
def s08():
    P = [('dcs', 'dcs 100 + storage unit · john · cc by 2.0', 'DCS 100 · 1991', L(1, -.5)),
         ('dc40', 'dc40 · nsmm · geni 2025 · cc by-sa 4.0', 'DC40 · 1995', L(1, 1.0)),
         ('easyshare', 'easyshare cx7330 · sgroey · cc by-sa 4.0', 'EASYSHARE CX7330 · LINE FROM 2001', L(2))]
    for k, (p_, tg, lab, t) in enumerate(P):
        x = 60 + k * 610; photo(p_, x, 150, 580, 520, t, 30, tg, fx=.5, fy=.5, z0=1.0, z1=1.04); text(lab, x, 690, 24, t, 30, col=RED, font='mono600')
    text('professional systems  →  consumer convenience', 60, 740, 26, L(2, 1), L(4), col=GREY, font='mono600')
    text('kodak also invested in digital printing and imaging technologies', 60, 740, 26, L(3), L(4), col=GREY, font='mono600')
    for k, s_ in enumerate(['price pressure', 'fast technology cycles', 'more choices for customers']):
        x = 60 + k * 610; t = L(5 + k); card_box(x, 790, 580, 76, t, 30); heading(s_, x + 30, 806, 36, t, 30); EV.append((T(t), 'mark'))
    heading('participation  ≠  control of the economics', 60, 920, 48, L(8), 30, col=RED)

@scene(9, 'the market changes')
def s09():
    photo('z740', 60, 150, 900, 760, 0, 30, 'photo · kodak easyshare z740, lcd image-info screen · cc by-sa 4.0')
    for k, s_ in enumerate(['TAKE', 'STORE', 'SHARE', 'VIEW']):
        y = 160 + k * 100; t = L(2, k * .9) if k < 1 else L(3, (k - 1) * .9); check(1040, y, t); heading(s_, 1110, y, 56, t, 30)
    rect(1040, 570, 780, 110, RED, L(3, 3.2), 30); heading('NO FILM REQUIRED', 1430, 596, 52, L(3, 3.2), 30, col=BG, al='CENTER'); EV.append((T(L(3, 3.2)), 'low'))
    for k, s_ in enumerate(['film', 'chemicals', 'paper']):
        x = 1040 + k * 270; heading(s_, x, 720, 40, L(4, k * .4), 30, col=GREY); rect(x - 6, 745, 200, 4, RED, L(4, k * .4 + .4), 30, grow=(L(4, k * .4 + .4), L(4, k * .4 + 1.0), 'x'))
    text('the photographic supply chain under pressure', 1040, 800, 24, L(5), 30, col=GREY, font='mono600')
    heading('replace an entire economic system', 1040, 860, 40, L(7), 30, col=RED)

@scene(10, 'the missing economics')
def s10():
    photo('lineup', 60, 150, 900, 640, 0, 30, 'photo · kodak easyshare z700 ×4 and c433 · jj harrison · cc by-sa 3.0')
    heading('invention  ≠  attractive returns', 1020, 140, 48, L(2), 30, col=RED)
    text('KODAK HAD', 1020, 240, 22, L(3), 30, col=GREY, font='mono600'); heading('expertise · patents · a global brand', 1020, 274, 36, L(3), 30)
    text('DIGITAL DEMANDED DIFFERENT', 1020, 360, 22, L(4), 30, col=GREY, font='mono600')
    chips(['capabilities', 'investments', 'sources of profit'], 1020, 400, L(4, .6), dt=.8, size=34, gap=62)
    heading('meanwhile: film declining', 1020, 620, 40, L(5), 30, col=GREY); vline(1600, 600, 680, L(5), 30, L(5, .3), L(5, 1.0), col=RED)
    text('fund the new  ·  manage the decline of the old', 60, 850, 30, L(6), 30, font='outfit500')
    heading('financial pressure', 60, 910, 60, L(7), 30, col=RED); EV.append((T(L(7)), 'low'))

# ═══════════════════════════ ACT 05 · THE COLLAPSE ═══════════════════════════
@scene(11, 'the financial evidence', 'act 05 · the collapse')
def s11():
    X0, Y0, Ytop, VMAX = 140, 860, 260, 8.0
    py = lambda v: Y0 - v / VMAX * (Y0 - Ytop)
    text('kodak net sales · continuing operations · $ billions · form 10-k fy2011', 140, 160, 20, 0, 30, col=GREY, font='mono400')
    for v in (0, 2, 4, 6, 8):
        rect(X0, py(v), 760, 1, '#262626' if v else GREY, .2, 30); text(str(v), X0 - 16, py(v) - 12, 20, .2, 30, col=GREY, font='mono400', al='RIGHT')
    for k, (yr, v, col) in enumerate([('2010', 7.167, GREY), ('2011', 6.022, RED)]):
        x = 240 + k * 340; t = L(2, k * 1.2)
        up(rect(x, py(v), 220, Y0 - py(v), col, t, 30, grow=(t, t + 1.0, 'y')), py(v), Y0 - py(v))
        heading(f'${v:.3f}B', x + 110, py(v) - 64, 44, t + 1.0, 30, al='CENTER'); text(yr, x + 110, Y0 + 14, 26, t, 30, col=GREY, font='mono600', al='CENTER'); EV.append((T(t), 'click'))
    doc('doc_k11', 1000, 150, 860, L(1, .5), 30, hls=(L(2), L(3)))
    rect(1000, 430, 860, 180, RED, L(3), 30); text('2011 NET LOSS ATTRIBUTABLE TO EASTMAN KODAK', 1030, 450, 22, L(3), 30, col=BG, font='mono600'); heading('$764M', 1030, 490, 96, L(3), 30, col=BG)
    text('a loss, not revenue: shown separately from the sales chart', 1000, 620, 20, L(3, .6), 30, col=GREY, font='mono400')
    doc('doc_mdna', 1000, 670, 860, L(4), 30, hls=(L(4, .6), L(4, 1.6), L(4, 2.6)))
    heading('not one product failing', 140, 940, 40, L(5), 30, col=RED)

@scene(12, 'the bankruptcy')
def s12():
    photo('building', 60, 140, 820, 820, 0, 30, 'photo · kodak building, rochester, ny · 2012 · viktor nagornyy · cc by 2.0', fx=.5, fy=.5, z0=1.0, z1=1.07)
    heading('january 19, 2012', 940, 150, 88, L(1), 30); rect(940, 262, 720, 6, RED, L(1, .8), 30, grow=(L(1, .8), L(1, 1.8), 'x'))
    heading('CHAPTER 11', 940, 300, 64, L(1, 1.2), 30, col=RED); EV.append((T(L(1)), 'impact'))
    text('eastman kodak company and its u.s. subsidiaries · s.d.n.y.', 940, 390, 24, L(1, 2), 30, col=GREY, font='mono600')
    for k, (s_, t, ok) in enumerate([('not the disappearance of the company', L(2), False), ('a legal reorganization process', L(3), True), ('kodak continued operating', L(4), True)]):
        y = 460 + k * 84; check(940, y - 4, t, ok=ok); heading(s_, 1010, y, 40, t, 30)
    heading('the symbol of photography’s future,', 940, 760, 40, L(6), 30, col=GREY)
    heading('restructuring in the digital age', 940, 812, 40, L(6, 1), 30, col=GREY)
    heading('it helped create the revolution.', 940, 890, 40, L(7), 30); heading('it did not transform around it.', 940, 942, 40, L(8), 30, col=RED)

# ═══════════════════════════ ACT 06 · THE RECKONING ═══════════════════════════
@scene(13, 'what kodak sold', 'act 06 · the reckoning')
def s13():
    heading('during restructuring', 60, 130, 48, L(1), 30, col=GREY)
    R = [('consumer digital-camera business', 'exit announced feb 9, 2012 · brand licensing instead', L(2)),
         ('online photo services', 'kodak gallery → shutterfly, 2012 (reported $23.8m)', L(3)),
         ('digital imaging patents', 'agreements dec 19, 2012 · ≈ $525m · not all kodak patents', L(4))]
    for k, (a_, b_, t) in enumerate(R):
        y = 220 + k * 150; card_box(60, y, 940, 124, t, 30); check(90, y + 30, t); heading(a_, 160, y + 22, 38, t, 30); text(b_, 160, y + 76, 20, t, 30, col=GREY, font='mono400')
    doc('doc_exit', 1060, 200, 800, L(2, .5), L(4), hls=(L(2, 1.5),))
    doc('doc_patent', 1060, 200, 800, L(4), 30, hls=(L(4, .8), L(4, 1.6)))
    text('CONCENTRATING ON', 60, 700, 22, L(5), 30, col=GREY, font='mono600')
    for k, s_ in enumerate(['commercial printing', 'packaging', 'imaging technologies']):
        heading(s_, 60 + k * 520, 740, 44, L(5, k * .6), 30)
    heading('the brand remained.', 60, 870, 56, L(7), 30); heading('the company changed.', 700, 870, 56, L(8), 30, col=RED)

@scene(14, 'what survived')
def s14():
    photo('magnus', 60, 140, 860, 560, 0, 30, 'photo · kodak magnus 800 platesetter · 2014 · frédéric bisson · cc by 2.0', fx=.5, fy=.5, z0=1.0, z1=1.06)
    rect(980, 140, 880, 190, RED, L(1), 30); text('SEPTEMBER 3, 2013', 1010, 162, 30, L(1), 30, col=BG, font='mono600'); heading('emerged from chapter 11', 1010, 212, 60, L(1, .4), 30, col=BG); EV.append((T(L(1)), 'low'))
    doc('doc_emerge', 980, 360, 880, L(1, 1.5), 30, hls=(L(1, 2.5), L(3)))
    heading('kodak had not vanished.', 60, 740, 48, L(2), 30)
    text('consumer imaging and document imaging businesses spun off to the kodak (uk) pension plan · kodak brand licensed to others', 60, 810, 22, L(4), 30, col=GREY, font='mono400', wrap=860)
    heading('photography didn’t disappear.', 980, 820, 44, L(5), 30)
    heading('the economics changed.', 980, 880, 56, L(7), 30, col=RED)

@scene(15, 'the real mistake')
def s15():
    heading('was inventing the threat the mistake?', 960, 140, 52, L(1), L(5), al='CENTER', col=GREY)
    heading('no.', 960, 300, 200, L(2), L(5), col=RED, al='CENTER'); EV.append((T(L(2)), 'impact'))
    heading('innovation wasn’t the mistake', 960, 600, 48, L(3), L(5), al='CENTER')
    CX.beat()
    rect(958, 140, 4, 640, RULE, L(5), 30)
    heading('they innovated', 100, 150, 56, L(5), 30)
    for k, (s_, t) in enumerate([('1975 prototype', L(5, .6)), ('professional digital cameras', L(6)), ('consumer digital cameras', L(6, .8)), ('imaging technology', L(7))]):
        y = 260 + k * 84; check(100, y - 4, t); heading(s_, 170, y, 40, t, 30)
    heading('the business did not', 1020, 150, 56, L(8), 30, col=RED); heading('reinvent itself', 1020, 210, 56, L(8), 30, col=RED)
    for k, s_ in enumerate(['film economics declining', 'digital price pressure', 'financial deterioration', 'restructuring']):
        y = 320 + k * 84; t = L(8, .6 + k * .5); check(1020, y - 4, t, ok=False); heading(s_, 1090, y, 40, t, 30)
    rect(100, 820, 1720, 120, PANEL, L(9), 30); heading('technological innovation  ≠  sustainable business transformation', 960, 856, 44, L(9), 30, al='CENTER', col=TXT)

@scene(16, 'the final verdict')
def s16():
    photo('film', 560, 120, 800, 800, 0, L(9), 'photo · kodak ultramax 400 · veera.sj 2018 · cc0', fx=.5, fy=.5, z0=1.0, z1=1.12, a=.85)
    heading('helped create the future · participated in it · struggled to survive it', 960, 940, 30, L(2), L(5), al='CENTER', col=GREY)
    rect(460, 340, 1000, 330, '#F0EDE6', L(6), L(9)); EV.append((T(L(6)), 'low'))
    for k, s_ in enumerate(['inventing the future', 'does not guarantee', 'owning it.']):
        heading(s_, 960, 370 + k * 96, 76, L(6, k * .5), L(9), col=BG if k < 2 else RED, al='CENTER')
    text('the documentary’s conclusion · not a quotation', 960, 690, 20, L(6, 1.5), L(9), col=GREY, font='mono400', al='CENTER')
    CX.beat()
    e = heading('brand coroner', 943, 420, 110, L(9), 30, al='CENTER'); e2 = text('.', 1305, 420, 110, L(9, .8), 30, col=RED)
    f = text('EVERY BRAND LEAVES EVIDENCE.', 960, 570, 36, L(9, .4), 30, col=GREY, font='outfit500', al='CENTER')
    rect(810, 555, 300, 2, RED, L(9, .2), 30, grow=(L(9, .2), L(9, 1.0), 'x'))
    for st in (e, e2, f): fade(st, L(9), 30, 1, .6, 2.0)
# ── assemble: one meta strip per scene on the master timeline ──
NF = int(round(DUR * FPS))
bg = SE.sequences.new_effect('background', 'COLOR', 1, frame_start=1, frame_end=NF + 1); bg.color = hexc(BG)
for (i, title, act, fn) in SCENES:
    if TL: sd = TL['scenes'][i - 1]; base, dur, warp = sd['base'], sd['dur'], [tuple(p) for p in sd['warp']]
    else: base, dur, warp = (i - 1) * 30, 30, None
    meta = SE.sequences.new_meta(f'S{i:02d} · {title}', 2, F(base))
    CX = Ctx(meta, base, warp)
    b = meta.sequences.new_effect(nm('bg'), 'COLOR', 1, frame_start=F(base), frame_end=F(base + dur)); b.color = hexc(BG)
    CX.n = sd['n'] if TL else 8
    chrome(i, title, act); CX.hold()
    fn()
    meta.frame_final_start, meta.frame_final_end = F(base), F(base + dur)
    meta.blend_type = 'ALPHA_OVER'
vig = SE.sequences.new_image('vignette', os.path.join(A, 'vignette.png'), 3, 1, fit_method='ORIGINAL'); vig.frame_final_duration = NF; vig.blend_type = 'ALPHA_OVER'
# fade from black at the very start, fade to black at the end
fb = SE.sequences.new_effect('fade_to_black', 'COLOR', 4, frame_start=F(DUR - 3.0), frame_end=NF + 1); fb.color = (0, 0, 0); fb.blend_type = 'ALPHA_OVER'
fb.blend_alpha = 0; fb.keyframe_insert('blend_alpha', frame=F(DUR - 3.0)); fb.blend_alpha = 1; fb.keyframe_insert('blend_alpha', frame=F(DUR - .4))
if TL:
    for l in TL['lines']: sc.timeline_markers.new(l['id'], frame=F(l['t']))
snd = os.path.join(D, 'audio', 'mix.flac')
if os.path.exists(snd): SE.sequences.new_sound('sound · underscore + foley', snd, 6, 1)
json.dump(sorted(EV), open(os.path.join(D, 'audio', 'events.json'), 'w'))
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(D, 'kodak.blend')); bpy.ops.file.make_paths_relative(); bpy.ops.wm.save_mainfile()
print('BUILD OK', len(SCENES), 'scenes', len(EV), 'events', NAMES[0], 'strips')
