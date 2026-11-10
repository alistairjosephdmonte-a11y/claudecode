"""BRAND CORONER · CASE 012 · DOMINO'S — "the pizza company that admitted its food was bad"
Blender (4.2 LTS) Python build: constructs the whole 8-minute animatic in the Video Sequence Editor.
  blender -b -P build.py                → writes dominos.blend (editable project) and events.json (sound cues)
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
sc = bpy.context.scene; sc.name = 'brand_coroner_case012_dominos'
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
    text('brand coroner · case 012', 60, 40, 16, 0, 30, col=GREY, font='mono600')
    text(f'{i:02d} · {title}', 1860, 40, 16, 0, 30, col=GREY, font='mono600', al='RIGHT')
    if act: text(act, 60, 70, 18, 0, 3.5, col=RED, font='mono600')

SCENES = []
def scene(i, title, act=None):
    def deco(fn): SCENES.append((i, title, act, fn)); return fn
    return deco

# ── Domino's scene designs. Authored on a 0–30 s grid per scene; L(k) is the grid time of narration line k, and
#    vo/timeline.json warps every grid onto the voiceover so each beat lands on its line. ──
def L(k, d=0.0): return 1.0 + 27.0 * (k - 1) / CX.n + d
def have(k): return os.path.exists(os.path.join(A, k + '.png'))
PHJ = json.load(open(os.path.join(D, 'photos.json'))); SA = {k for k, v in PHJ.items() if v.get('sa')}; PH_TAG = {k: v.get('tag', '') for k, v in PHJ.items()}
def chips(items, x, y, t, dt=.8, t1=30, col=TXT, size=34, gap=70, bar=RED):
    for k, s_ in enumerate(items):
        rect(x, y + k * gap + size * .25, 8, size * .85, bar, t + k * dt, t1); heading(s_, x + 26, y + k * gap, size, t + k * dt, t1, col=col)
def photo(k, x, y, w, h, t0, t1, tagtxt, **kw):
    """graded photo (cover crop, optional push). CC BY-SA photos are shown unaltered: whole frame, contained, no crop or push."""
    if not have('ph_' + k): return None
    if k in SA: rect(x, y, w, h, '#101010', t0, t1); kw = {'contain': True}
    im = image('ph_' + k, x, y, w, h, t0, t1, **kw); tag(tagtxt, x, y - 26, t0, t1); EV.append((T(t0), 'shutter')); return im
def hline(x0, x1, y, t0, t1, ta, tb, col=RED, th=4, head=True):
    if x1 >= x0: rect(x0, y - th / 2, x1 - x0, th, col, t0, t1, grow=(ta, tb, 'x'))
    else: rect(x1, y - th / 2, x0 - x1, th, col, t0, t1, grow=(ta, tb, 'xr'))
    if head: sprite(f"arrow_{'red' if col == RED else 'grey'}_{'r' if x1 >= x0 else 'l'}", x1, y, tb, t1)
def up(s, y, h): s.transform.origin = (0, 0); s.transform.offset_y = H - y - h; return s
def vline(x, y0, y1, t0, t1, ta, tb, col=RED, th=4, head=True):
    top, h = min(y0, y1), abs(y1 - y0); s = rect(x - th / 2, top, th, h, col, t0, t1, grow=(ta, tb, 'y'))
    if y1 < y0: up(s, top, h)
    if head: sprite(f"arrow_{'red' if col == RED else 'grey'}_{'d' if y1 >= y0 else 'u'}", x, y1, tb, t1)
def card_box(x, y, w, h, t0, t1, edge=RED):
    rect(x, y, w, h, PANEL, t0, t1); rect(x, y, 6, h, edge, t0, t1)
def check(x, y, t, t1=30, ok=True, size=44, col=RED):
    text('✓' if ok else '✕', x, y, size, t, t1, col=col, font='outfit700'); EV.append((T(t), 'mark'))
def schematic(name, x, y, w, t0, t1, a=1.0):
    st = CX.m.sequences.new_image(nm('d'), os.path.join(A, f'{name}.png'), CX.ch(), F(T(t0)), fit_method='ORIGINAL'); st.frame_final_duration = max(1, F(T(t1)) - F(T(t0)))
    st.blend_type = 'ALPHA_OVER'; iw, ih = st.elements[0].orig_width, st.elements[0].orig_height; s = w / iw
    st.transform.scale_x = st.transform.scale_y = s; st.transform.offset_x = x + w / 2 - W / 2; st.transform.offset_y = H / 2 - (y + ih * s / 2)
    fade(st, t0, t1, a, .4, 0); return st

def bar(x, base, w, h, col, t, t1=30, d=.8):
    s = rect(x, base - h, w, h, col, t, t1, grow=(t, t + d, 'y')); up(s, base - h, h); return s
def strike(x, y, w, t, t1=30): rect(x, y, w, 5, RED, t, t1, grow=(t, t + .5, 'x')); EV.append((T(t), 'mark'))

def bars(items, x0, base, w, gap, k_, lab_size=44, yr_size=24):
    for k, (yr, v, lab, t, c) in enumerate(items):
        x = x0 + k * gap; bar(x, base, w, max(v * k_, 4), c, t)
        heading(lab, x + w / 2, base - max(v * k_, 4) - lab_size - 18, lab_size, t + .6, 30, al='CENTER'); text(yr, x + w / 2, base + 14, yr_size, t, 30, col=GREY, font='mono600', al='CENTER')

def wrap(px): CX.m.sequences[-1].wrap_width = px / W
def money(lbl, val, x, y, t, col=RED, size=120, sub=None, t1=30):
    text(lbl, x, y, 22, t, t1, col=GREY, font='mono600'); heading(val, x, y + 36, size, t + .2, t1, col=col); EV.append((T(t + .2), 'impact'))
    if sub: text(sub, x + 4, y + 50 + size * 1.05, 18, t + .4, t1, col=GREY, font='mono400')

# ═══════════════════════════ ACT 01 · THE CONFESSION ═══════════════════════════
@scene(1, 'the confession', 'act 01 · the confession')
def s01():
    photo('pizza09', 60, 150, 860, 573, 0, 30, PH_TAG.get('pizza09', ''))
    text('DECEMBER 2009', 1000, 150, 30, L(1), 30, col=RED, font='mono600')
    heading("one of america's biggest pizza chains did something almost unthinkable", 1000, 190, 44, L(1, .2), 30); wrap(860)
    text('an advertising campaign built around people criticizing its own food', 1000, 360, 30, L(2), 30, col=GREY, font='outfit500', wrap=860)
    chips(['the crust', 'the sauce', 'tasted fresh at all?'], 1000, 460, L(3), dt=1.6, size=34, gap=62)
    text('instead of hiding those opinions: the center of its marketing', 60, 790, 30, L(6), 30, font='outfit500')
    text('then: a changed pizza recipe', 60, 845, 30, L(7), 30, col=GREY, font='outfit500')
    money('Q1 2010 · DOMESTIC SAME-STORE SALES', '+ 14.3%', 1000, 690, L(8), size=96, sub='q1 2010 results release (may 4, 2010)')
    heading('how did admitting a product was not good enough become a turnaround?', 60, 920, 40, L(9), 30, col=RED); wrap(1800); EV.append((T(L(9)), 'low'))

@scene(2, 'built for delivery')
def s02():
    photo('ypsi', 60, 150, 640, 480, 0, 30, PH_TAG.get('ypsi', ''))
    text('YPSILANTI, MICHIGAN · 1960', 760, 150, 30, L(1), 30, col=RED, font='mono600')
    heading('domino\'s begins', 760, 190, 64, L(1, .2), 30)
    text('brothers thomas and james monaghan buy a store (form 10-k)', 764, 280, 22, L(1, .5), 30, col=GREY, font='mono600', wrap=500)
    chips(['convenience', 'delivery', 'a repeatable franchise model'], 760, 370, L(2), dt=.5, size=34, gap=60)
    photo('probe', 1320, 150, 540, 405, L(3), 30, PH_TAG.get('probe', ''))
    text('pizza brought to the door · speed · consistency', 60, 700, 30, L(4), 30, font='outfit500')
    text('dec 2009: 8,886 stores in the u.s. and 60 international markets (company release)', 60, 760, 22, L(5), 30, col=GREY, font='mono600')
    heading('good at delivery', 60, 850, 52, L(6), 30); heading('≠ loved for the food', 560, 850, 52, L(6, .6), 30, col=RED)
    heading('better known for how pizza arrived than for how it tasted?', 60, 940, 38, L(8), 30, col=GREY); wrap(1800); EV.append((T(L(8)), 'low'))

@scene(3, 'the taste problem')
def s03():
    text('THE LATE 2000s', 60, 150, 30, L(1), 30, col=RED, font='mono600')
    heading('a perception problem', 60, 190, 60, L(1, .2), 30)
    doc('doc_keys', 60, 300, 860, L(2), 30, hls=(L(2, .3), L(2, .6), L(2, .9)))
    photo('pizza09', 1000, 150, 860, 573, 0, 30, PH_TAG.get('pizza09', ''), fx=.5, fy=.5, z0=1.0, z1=1.08)
    text('a pizza category under pressure · more restaurant choices', 60, 700, 30, L(3), 30, col=GREY, font='outfit500')
    heading('another discount', 60, 780, 48, L(5), 30, col=GREY); strike(56, 806, 420, L(5, .6))
    heading('a reason to reconsider the product', 540, 780, 48, L(6), 30, col=RED)
    text('many already believed they knew what it tasted like', 1000, 738, 28, L(7), 30, font='outfit500', wrap=860)
    heading('changing that opinion required changing something real', 60, 920, 42, L(8), 30); wrap(1800); EV.append((T(L(8)), 'low'))

@scene(4, 'listening to the critics')
def s04():
    photo('hq', 1000, 150, 860, 573, 0, 30, PH_TAG.get('hq', ''))
    heading('comments that were unusually harsh', 60, 150, 52, L(1), 30); wrap(880)
    doc('doc_ad', 60, 300, 880, L(2), 30, hls=(L(2, .4), L(2, .8)))
    text('the campaign would feature complaints about the crust, the sauce, the eating experience', 60, 560, 26, L(2, .2), 30, col=GREY, font='outfit500', wrap=880)
    heading('flattering testimonials', 60, 660, 44, L(3), 30, col=GREY); strike(56, 684, 520, L(3, .6))
    text('the doubts management wanted to overcome', 60, 740, 30, L(4), 30, font='outfit500')
    text('"our product has improved" — why should skeptical customers believe it?', 1000, 770, 28, L(6), 30, font='outfit500', wrap=860)
    heading('show the criticism · make the response visible', 60, 920, 46, L(8), 30, col=RED); wrap(1800); EV.append((T(L(8)), 'low'))

# ═══════════════════════════ ACT 02 · THE DECISION ═══════════════════════════
@scene(5, 'the decision to change the product', 'act 02 · the decision')
def s05():
    heading('a fundamental choice', 60, 150, 60, L(1), 30)
    text('not marketing around the existing pizza:', 60, 240, 30, L(2), 30, col=GREY, font='outfit500')
    heading('reformulate the core hand-tossed pizza', 60, 290, 44, L(2, .4), 30, col=RED); wrap(880)
    doc('doc_dec09', 1000, 150, 860, L(3), 30, hls=(L(3, .2), L(3, .5), L(3, .8), L(4, .3)))
    for k, (h_, s_) in enumerate([('CRUST', 'garlic-seasoned'), ('SAUCE', 'more robust tomato'), ('CHEESE', 'revised shredded blend')]):
        t = L(3, k * .4); card_box(60 + k * 300, 430, 280, 130, t, 30); text(h_, 90 + k * 300, 450, 20, t, 30, col=RED, font='mono600'); heading(s_, 90 + k * 300, 490, 28, t, 30); wrap(240)
    text('not a limited-time novelty · the pizza at the center of the business', 60, 620, 28, L(4), 30, font='outfit500', wrap=880)
    text('a new recipe across a large store network · consistency · delivery performance', 60, 720, 26, L(6), 30, col=GREY, font='outfit500', wrap=880)
    heading('advertising could promise change', 60, 850, 44, L(8), 30)
    heading('the kitchens had to deliver it', 60, 920, 44, L(9), 30, col=RED); EV.append((T(L(9)), 'low'))

@scene(6, 'a dangerous advertising idea')
def s06():
    photo('hq', 60, 150, 860, 573, 0, 30, PH_TAG.get('hq', ''))
    heading('then came the more surprising decision', 1000, 150, 44, L(1), 30); wrap(860)
    text('tell customers why the change had been necessary', 1000, 270, 30, L(2), 30, font='outfit500', wrap=860)
    text('EDITORIAL COMPARISON', 1000, 380, 20, L(3), 30, col=GREY, font='mono600')
    card_box(1000, 420, 410, 170, L(3), 30, edge=GREY); text('CONVENTIONAL AD', 1030, 440, 20, L(3), 30, col=GREY, font='mono600'); heading('"great taste"', 1030, 485, 40, L(3, .2), 30, col=GREY)
    card_box(1450, 420, 410, 170, L(4), 30); text('PIZZA TURNAROUND', 1480, 440, 20, L(4), 30, col=RED, font='mono600'); heading('"you told us"', 1480, 485, 40, L(4, .2), 30, col=RED)
    heading('it was risky', 60, 790, 56, L(5), 30, col=RED); EV.append((T(L(5)), 'impact'))
    chips(['viewers might remember only the complaints', 'competitors could benefit from the admission'], 1000, 650, L(6), dt=1.4, size=28, gap=56, bar=GREY)
    heading('the bet: honesty, backed by a better product', 60, 920, 46, L(8), 30); wrap(1800); EV.append((T(L(8)), 'low'))

@scene(7, 'the pizza turnaround')
def s07():
    text('DECEMBER 27, 2009', 60, 150, 30, L(1), 30, col=RED, font='mono600')
    heading('the reformulated pizza in all u.s. stores', 60, 190, 52, L(1, .2), 30); wrap(880)
    text('per the company release of dec 16, 2009: "beginning december 27"', 60, 330, 20, L(1, .5), 30, col=GREY, font='mono600')
    doc('doc_k09', 1000, 150, 860, L(2), 30, hls=(L(2, .3), L(2, .6), L(4, .2)))
    text('documentary-style advertising (crispin porter + bogusky)', 60, 420, 30, L(3), 30, font='outfit500')
    text('company personnel confronting criticism · explaining the new recipe', 60, 480, 28, L(3, .5), 30, col=GREY, font='outfit500', wrap=880)
    chips(['we heard what you disliked', 'we changed the food', 'give us another chance'], 60, 600, L(6), dt=.6, size=34, gap=62)
    heading('not "forget the past"', 1000, 760, 44, L(7), 30, col=GREY); strike(996, 784, 480, L(7, .6))
    heading('judge the new product for yourself', 1000, 840, 44, L(8), 30, col=RED); wrap(860); EV.append((T(L(8)), 'low'))

@scene(8, 'the first test')
def s08():
    photo('driver07', 1000, 150, 860, 645, 0, 30, PH_TAG.get('driver07', ''))
    heading('publicity alone was not the objective', 60, 150, 48, L(1), 30); wrap(880)
    chips(['visit', 'order', 'try the pizza', 'come back'], 60, 290, L(2), dt=.5, size=36, gap=64)
    text('management reported encouraging traffic and sales momentum', 60, 580, 28, L(4), 30, font='outfit500', wrap=880)
    text('a heavily publicized change can produce temporary excitement', 60, 660, 28, L(6), 30, col=GREY, font='outfit500', wrap=880)
    text('TIMELINE', 60, 790, 20, L(7), 30, col=GREY, font='mono600')
    for k, (d_, s_) in enumerate([('DEC 16, 2009', 'new pizza announced'), ('DEC 27, 2009', 'in all u.s. stores'), ('MAR 28, 2010', 'q1 ends'), ('MAY 4, 2010', 'q1 results')]):
        t = L(7, k * .35); x = 60 + k * 460; rect(x, 840, 440, 3, RED if k == 3 else GREY, t, 30, grow=(t, t + .4, 'x')); sprite('dot_red' if k == 3 else 'dot_grey', x + 8, 841, t, 30)
        text(d_, x, 870, 20, t, 30, col=RED if k == 3 else GREY, font='mono600'); text(s_, x, 905, 26, t, 30, font='outfit500')
    EV.append((T(L(7, 1.2)), 'low'))

# ═══════════════════════════ ACT 03 · THE EVIDENCE ═══════════════════════════
@scene(9, 'the 14.3 percent surge', 'act 03 · the evidence')
def s09():
    text('MAY 4, 2010 · FIRST-QUARTER RESULTS', 60, 150, 30, L(1), 30, col=RED, font='mono600')
    money('DOMESTIC SAME-STORE SALES · VS PRIOR YEAR', '+ 14.3%', 60, 210, L(2), size=150)
    doc('doc_q1', 1000, 150, 860, L(2, .4), 30, hls=(L(3), L(4), L(2, .7), L(5)))
    text('company-owned u.s. stores  + 14.7%', 60, 450, 32, L(3), 30, font='mono600')
    text('domestic franchise stores  + 14.2%', 60, 505, 32, L(4), 30, font='mono600')
    text('attributed to increased traffic after the new pizza', 60, 600, 30, L(5), 30, col=GREY, font='outfit500')
    heading('extraordinary for an established chain', 60, 680, 44, L(6), 30)
    card_box(60, 790, 1800, 150, L(7), 30)
    text('HOW TO READ IT', 90, 810, 20, L(7), 30, col=RED, font='mono600')
    heading('sales growth at comparable stores ≠ a 14% increase in corporate profit', 90, 855, 40, L(8), 30); EV.append((T(L(8)), 'low'))

@scene(10, 'why the confession worked')
def s10():
    heading('it challenged a familiar advertising assumption', 60, 150, 52, L(1), 30)
    text('brands usually emphasize strengths and minimize weaknesses', 60, 235, 30, L(2), 30, col=GREY, font='outfit500')
    text('domino\'s did the opposite', 60, 290, 30, L(3), 30, col=RED, font='outfit500')
    text('EDITORIAL EVIDENCE SEQUENCE', 60, 380, 20, L(4), 30, col=GREY, font='mono600')
    for k, (h_, s_, src, t) in enumerate([('01', 'a recognized problem', 'customer criticism · brand keys, 2009', L(5)), ('02', 'a visible response', 'the pizza turnaround campaign', L(6)), ('03', 'a specific change', 'new crust · sauce · cheese', L(7))]):
        x = 60 + k * 610; card_box(x, 420, 580, 210, t, 30); text(h_, x + 34, 445, 40, t, 30, col=RED, font='mono600'); heading(s_, x + 34, 510, 36, t, 30); text(src, x + 34, 575, 20, t, 30, col=GREY, font='mono400')
        if k < 2: hline(x + 584, x + 606, 525, t + .3, 30, t + .3, t + .5, col=GREY)
    text('more credible than a vague promise of improvement', 60, 690, 30, L(8), 30, font='outfit500')
    text('the confession meant little without the reformulated pizza', 60, 750, 30, L(9), 30, col=GREY, font='outfit500')
    heading('a demonstration of change', 60, 860, 48, L(10), 30, col=RED); heading('not self-deprecating humor', 760, 860, 48, L(10, .5), 30, col=GREY); strike(756, 886, 620, L(10, .9)); EV.append((T(L(10)), 'low'))

@scene(11, 'the risk behind the recipe')
def s11():
    photo('valdosta', 1000, 150, 860, 645, 0, 30, PH_TAG.get('valdosta', ''))
    heading('changing a core product is dangerous', 60, 150, 48, L(1), 30); wrap(880)
    text('established customers may prefer the original', 60, 280, 28, L(1, .6), 30, col=GREY, font='outfit500')
    chips(['consistent ingredients', 'preparation procedures', 'product quality'], 60, 360, L(2), dt=.5, size=32, gap=58)
    money('END OF 2010 · U.S. STORES', '4,929', 60, 560, L(3), size=80, sub='4,475 franchise · 454 company-owned (form 10-k, fiscal 2010)')
    text('the promise depended on what customers actually received', 1000, 820, 28, L(4), 30, font='outfit500', wrap=860)
    text('weak execution could reinforce the criticism it had amplified', 1000, 880, 28, L(5), 30, col=GREY, font='outfit500', wrap=860)
    for k, s_ in enumerate(['product', 'operations', 'message']):
        t = L(7, k * .3); card_box(60 + k * 300, 840, 280, 70, t, 30); heading(s_, 90 + k * 300, 858, 30, t, 30)
    heading('→ convince customers the pizza itself had improved', 60, 950, 36, L(8), 30, col=RED); EV.append((T(L(8)), 'low'))

@scene(12, 'the second advantage')
def s12():
    photo('driver07', 60, 150, 860, 645, 0, 30, PH_TAG.get('driver07', ''))
    heading('strengthening other parts of the business', 1000, 150, 44, L(1), 30); wrap(860)
    chips(['online ordering', 'technology', 'a developed delivery network'], 1000, 280, L(2), dt=.5, size=32, gap=58)
    text('easier for interested customers to act', 1000, 470, 28, L(3), 30, col=GREY, font='outfit500')
    doc('doc_k10', 1000, 540, 860, L(4), 30, hls=(L(4, .4),))
    text('pulse ordering system · pizza tracker (2007) · pizza builder (2008) — form 10-k', 60, 830, 22, L(4, .3), 30, col=GREY, font='mono600')
    text('the recipe overhaul was not happening in isolation', 60, 890, 30, L(5), 30, font='outfit500')
    heading('attention → transactions', 60, 950, 44, L(6), 30, col=RED); EV.append((T(L(6)), 'low'))

@scene(13, 'momentum beyond the launch')
def s13():
    heading('the improvement continued', 60, 150, 56, L(1), 30)
    text('DOMESTIC SAME-STORE SALES GROWTH · 2010 · VS PRIOR YEAR', 60, 240, 22, L(1, .5), 30, col=GREY, font='mono600')
    bars([('Q1 2010', 14.3, '+14.3%', L(1, .6), GREY), ('Q2 2010', 8.8, '+8.8%', L(2), RED), ('Q3 2010', 11.7, '+11.7%', L(2, .5), RED)], 90, 760, 200, 280, 26)
    doc('doc_q23', 1000, 240, 860, L(2, .3), 30, hls=(L(2, .5), L(2, .9)))
    text('more than a launch-week spike', 1000, 548, 30, L(3), 30, font='outfit500')
    heading('not proof the advertising alone caused every sale', 1000, 605, 36, L(4), 30, col=RED); wrap(860)
    chips(['pricing', 'promotion', 'traffic', 'operations', 'business conditions'], 1000, 720, L(5), dt=.25, size=26, gap=40, bar=GREY)
    heading('a substantial shift in domestic sales momentum', 60, 960, 44, L(6), 30); wrap(1800); EV.append((T(L(6)), 'low'))

# ═══════════════════════════ ACT 04 · THE AUTOPSY ═══════════════════════════
@scene(14, 'the longer transformation', 'act 04 · the autopsy')
def s14():
    photo('pizza19', 60, 150, 860, 645, 0, 30, PH_TAG.get('pizza19', ''))
    heading('later: widely recognized for', 1000, 150, 44, L(1), 30)
    chips(['digital ordering', 'delivery systems', 'global expansion'], 1000, 230, L(1, .4), dt=.5, size=34, gap=60)
    text('developed over years · not credited to one campaign', 1000, 440, 28, L(2), 30, col=GREY, font='outfit500')
    text('the pizza turnaround: an important early chapter', 1000, 500, 28, L(3), 30, font='outfit500', wrap=860)
    text('sustained investment and execution', 1000, 580, 28, L(4), 30, col=RED, font='outfit500')
    heading('a campaign can change the conversation', 60, 820, 48, L(6), 30)
    heading('a business must keep delivering on the promise', 60, 900, 48, L(7), 30, col=RED); wrap(1800); EV.append((T(L(7)), 'impact'))

@scene(15, 'what actually changed?')
def s15():
    heading('four connected decisions', 60, 150, 56, L(1), 30)
    for k, (h_, s_, ev, t) in enumerate([('01', 'took customer criticism seriously', 'brand keys survey · customer comments', L(2)), ('02', 'changed the product, not just the message', 'release, dec 16, 2009', L(3)),
                                        ('03', 'made the criticism public', 'pizza turnaround campaign · pizzaturnaround.com', L(4)), ('04', 'a delivery and ordering system for renewed demand', '10-k: nearly 25% of sales online', L(5))]):
        x = 60 + k * 455; card_box(x, 260, 430, 330, t, 30)
        text(h_, x + 36, 290, 48, t, 30, col=RED, font='mono600'); heading(s_, x + 36, 370, 32, t, 30); wrap(360); text(ev, x + 36, 530, 18, t, 30, col=GREY, font='mono400'); wrap(370)
    text('none of these choices alone explains the company\'s entire future', 60, 660, 30, L(6), 30, font='outfit500')
    text('together: a credible reason to try domino\'s again', 60, 720, 30, L(7), 30, col=GREY, font='outfit500')
    heading('defending the old product', 60, 840, 44, L(8), 30, col=GREY); strike(56, 866, 560, L(8, .5))
    heading('committing to improving it', 700, 840, 44, L(8, .7), 30, col=RED); EV.append((T(L(8)), 'low'))

@scene(16, 'the verdict')
def s16():
    heading('domino\'s publicly admitted', 960, 200, 60, L(1), L(5), al='CENTER')
    text('customers had serious problems with its most important product', 960, 290, 32, L(2), L(5), col=GREY, font='outfit500', al='CENTER')
    heading('the admission was only the beginning', 960, 400, 44, L(3), L(5), al='CENTER')
    heading('changed the recipe · showed customers · gave a reason to reconsider', 960, 480, 40, L(4), L(5), al='CENTER', col=RED); EV.append((T(L(4)), 'impact'))
    CX.beat()
    text('THE VERDICT', 960, 220, 26, L(5), L(9), col=GREY, font='mono600', al='CENTER')
    heading('not "advertise your weaknesses"', 960, 290, 48, L(5, .2), L(9), al='CENTER', col=GREY)
    heading('honesty becomes powerful when it is supported by meaningful action', 960, 400, 44, L(6), L(9), al='CENTER')
    heading('it improved the pizza', 960, 540, 56, L(8), L(9), al='CENTER', col=RED)
    heading('and made that decision impossible to ignore', 960, 615, 48, L(8, .5), L(9), al='CENTER', col=RED); EV.append((T(L(8)), 'impact'))
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
    CX.n = sd['n'] if TL else sum(1 for l in json.load(open(os.path.join(D, 'vo', 'lines.json'))) if l['scene'] == i)
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
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(D, 'dominos.blend')); bpy.ops.file.make_paths_relative(); bpy.ops.wm.save_mainfile()
print('BUILD OK', len(SCENES), 'scenes', len(EV), 'events', NAMES[0], 'strips')
