"""BRAND CORONER · CASE 008 · HARLEY-DAVIDSON — "the decisions that nearly destroyed an american icon"
Blender (4.2 LTS) Python build: constructs the whole 8-minute animatic in the Video Sequence Editor.
  blender -b -P build.py                → writes harleydavidson.blend (editable project) and events.json (sound cues)
Every scene is a meta strip (S01…S16) holding its own editable strips: text strips (editable typography),
colour strips (panels, rules, bars, red evidence lines), image strips (graded authentic photographs,
typeset filing and press transcriptions, store grids). Camera moves are keyframed 2D transforms
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
sc = bpy.context.scene; sc.name = 'brand_coroner_case008_harleydavidson'
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
    text('brand coroner · case 008', 60, 40, 16, 0, 30, col=GREY, font='mono600')
    text(f'{i:02d} · {title}', 1860, 40, 16, 0, 30, col=GREY, font='mono600', al='RIGHT')
    if act: text(act, 60, 70, 18, 0, 3.5, col=RED, font='mono600')

SCENES = []
def scene(i, title, act=None):
    def deco(fn): SCENES.append((i, title, act, fn)); return fn
    return deco

# ── Harley-Davidson scene designs. Authored on a 0–30 s grid per scene; L(k) is the grid time of narration line k, and
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

def flow(labels, x, y, w, h, gap, t0, dt=.5, t1=30, edge=GREY, size=24):
    """row of boxed stages joined by arrows"""
    for k, lab in enumerate(labels):
        bx = x + k * (w + gap); t = t0 + k * dt; card_box(bx, y, w, h, t, t1, edge=edge); text(lab, bx + 24, y + h / 2 - size * .6, size, t, t1, font='outfit500'); wrap(w - 40)
        if k: hline(bx - gap + 8, bx - 10, y + h / 2, t, t1, t, t + .3, col=GREY)
def note(st, x, y, t, t1=30, w=900, size=18, col=GREY): text(st, x, y, size, t, t1, col=col, font='mono400'); wrap(w)

def nums(items, x, y, t, size=96, gap=300):
    for k, (lab, val, col, tt) in enumerate(items):
        text(lab, x + k * gap, y, 20, tt, 30, col=GREY, font='mono600'); heading(val, x + k * gap, y + 32, size, tt + .1, 30, col=col); EV.append((T(tt + .1), 'impact'))

# ═══════════════════════════ ACT 01 · THE FIRST CRISIS ═══════════════════════════
@scene(1, 'the american icon in trouble', 'act 01 · the first crisis')
def s01():
    photo('museum09', 60, 190, 780, 520, 0, 30, PH_TAG['museum09'])
    heading('one of the most recognizable identities in american business', 900, 190, 46, L(1), 30); wrap(960)
    chips(['freedom', 'rebellion', 'the open road'], 900, 340, L(2), dt=.4, size=30, gap=54)
    for k, (yr, a_, b_, src, t) in enumerate([('1983', 'import relief approved', 'tariff increase: +45 points in year one', 'white house memo · apr 1, 1983', L(3)),
                                             ('2025', 'shipments −16.4%', 'motorcycle division: $28.7m operating loss', 'form 10-k · fy2025', L(5))]):
        x = 900 + k * 490; card_box(x, 540, 460, 230, t, 30)
        heading(yr, x + 30, 560, 48, t, 30, col=RED); text(a_, x + 30, 630, 26, t + .2, 30, font='outfit500'); wrap(400)
        text(b_, x + 30, 672, 20, t + .3, 30, col=GREY, font='mono400'); wrap(410); text(src, x + 30, 735, 16, t + .3, 30, col=GREY, font='mono600')
    text('FOUR DECADES LATER', 1390, 510, 18, L(4), 30, col=RED, font='mono600')
    heading('how could a brand with more than a century of history face such serious challenges twice?', 60, 820, 40, L(6), 30, col=RED); wrap(1800); EV.append((T(L(6)), 'low'))
    text('and what separated its legendary comeback from its latest struggle?', 60, 940, 28, L(7), 30, font='outfit500'); wrap(1800)

@scene(2, 'the machine that became america')
def s02():
    photo('fact12', 60, 190, 820, 584, 0, L(2), PH_TAG['fact12'], z0=1.0, z1=1.05)
    photo('war18', 60, 190, 820, 584, L(2), 30, PH_TAG['war18'])
    text('MILWAUKEE · 1903', 960, 150, 26, L(1), 30, col=RED, font='mono600')
    doc('doc_k25gen', 960, 190, 860, L(1, .2), 30, hls=(L(1, .6),))
    text('distinctive machines →', 960, 500, 28, L(3), 30, col=GREY, font='outfit500')
    heading('an identity riders could make part of their lives', 960, 545, 34, L(4), 30); wrap(860)
    chips(['independence', 'community', 'a vision of the american road'], 960, 640, L(5), dt=.4, size=26, gap=46)
    check(960, 780, L(6)); text("an advantage competitors couldn't easily reproduce", 1020, 790, 26, L(6), 30, font='outfit500'); wrap(800)
    for k, (h_, s_, t) in enumerate([('THE VULNERABILITY', 'customers loyal to the image', L(7)), ('', 'competitors meeting changing practical needs', L(8))]):
        x = 60 + k * 920; card_box(x, 860, 880, 120, t, 30, edge=RED if k else GREY)
        if h_: text(h_, x + 30, 875, 18, t, 30, col=RED, font='mono600')
        text(s_, x + 30, 910, 30, t, 30, font='outfit500'); wrap(820)
    hline(950, 975, 920, L(8), 30, L(8), L(8, .3), col=GREY, head=False)

@scene(3, 'the competition arrives')
def s03():
    text('1969', 60, 150, 26, L(1), 30, col=RED, font='mono600')
    heading('harley-davidson becomes part of amf', 60, 190, 44, L(1), 30); wrap(860)
    photo('xlcr77', 60, 300, 640, 480, L(1, .3), 30, PH_TAG['xlcr77'], z0=1.0, z1=1.05)
    text('access to capital · a period of changing competition', 960, 200, 24, L(2), 30, col=GREY, font='outfit500'); wrap(900)
    photo('cb750', 760, 300, 520, 345, L(3), 30, PH_TAG['cb750'])
    photo('gw75', 1320, 300, 540, 360, L(3, .5), 30, PH_TAG['gw75'])
    for k, (s_, x) in enumerate([('engineering', 760), ('manufacturing quality', 1060), ('price', 1500)]):
        rect(x, 708, 8, 26, RED, L(3, 1 + k * .4), 30); heading(s_, x + 24, 700, 30, L(3, 1 + k * .4), 30)
    check(60, 800, L(4)); text('brand recognition', 120, 810, 28, L(4), 30, font='outfit500')
    check(420, 800, L(4, .6), ok=False); text('operational weaknesses', 480, 810, 28, L(4, .6), 30, font='outfit500')
    text('improve the motorcycles — and the processes used to build them', 960, 810, 28, L(5), 30, font='outfit500'); wrap(900)
    heading("could harley-davidson remain an american icon if it couldn't consistently compete as a motorcycle manufacturer?", 60, 900, 36, L(6), 30, col=RED); wrap(1800); EV.append((T(L(7)), 'low'))
    note('amf ownership 1969–1981: company histories; the 10-k confirms the 1981 purchase from amf', 60, 1010, L(1, .5), w=1800, size=15)

@scene(4, 'the management buyout')
def s04():
    for k, (yr, lab, t) in enumerate([('1903', 'founded, milwaukee', L(1)), ('1969', 'amf', L(1, .3)), ('1981', 'management buyout', L(1, .6)), ('1986', 'publicly held', L(1, .9))]):
        x = 60 + k * 460; c = RED if k == 2 else GREY; rect(x, 250, 440, 3, c, t, 30, grow=(t, t + .4, 'x')); sprite('dot_red' if k == 2 else 'dot_grey', x + 8, 251, t, 30)
        text(yr, x, 180, 34, t, 30, col=c, font='mono600'); text(lab, x, 270, 24, t, 30, font='outfit500')
    doc('doc_k25b', 60, 360, 860, L(1, 1.0), 30, hls=(L(1, 1.4), L(1, 1.8)))
    text('control returned to people directly involved in running the business', 1000, 360, 28, L(2), 30, font='outfit500'); wrap(860)
    text('INHERITED', 1000, 450, 20, L(4), 30, col=RED, font='mono600')
    chips(['intense competition', 'financial pressures', 'the need for operational change'], 1000, 485, L(4, .2), dt=.4, size=28, gap=50)
    check(60, 600, L(5)); text('a historic american brand', 120, 610, 28, L(5), 30, font='outfit500')
    check(560, 600, L(5, .6), ok=False); text('a completed turnaround', 620, 610, 28, L(5, .6), 30, font='outfit500')
    flow(['manufacturing', 'product development', 'financing', 'customers'], 60, 700, 400, 100, 50, L(6), dt=.4)
    heading('independence regained', 60, 860, 40, L(7), 30)
    heading('now it had to become a viable business', 60, 920, 40, L(8), 30, col=RED); EV.append((T(L(8)), 'low'))

# ═══════════════════════════ ACT 02 · THE COMEBACK ═══════════════════════════
@scene(5, "reagan's 45-point decision", 'act 02 · the comeback')
def s05():
    text('THE PETITION', 60, 150, 22, L(1), 30, col=GREY, font='mono600')
    heading('relief from heavyweight motorcycle imports (over 700 cc)', 60, 185, 34, L(1), 30); wrap(960)
    text('APRIL 1, 1983 · PRESIDENT REAGAN APPROVES IMPORT RELIEF', 60, 270, 20, L(2), 30, col=RED, font='mono600')
    doc('doc_m83', 60, 300, 860, L(2, .2), 30, hls=(L(3), L(3, .6), L(3, 1.2)))
    text('ADDITIONAL DUTY ABOVE THE SCHEDULED RATE · PERCENTAGE POINTS', 1080, 190, 18, L(3), 30, col=GREY, font='mono600')
    bars([('yr 1', 45, '+45', L(3, .4), RED), ('yr 2', 35, '+35', L(3, .7), GREY), ('yr 3', 20, '+20', L(3, 1.0), GREY), ('yr 4', 15, '+15', L(3, 1.3), GREY), ('yr 5', 10, '+10', L(3, 1.6), GREY)],
         1100, 700, 110, 150, 7.5, lab_size=40, yr_size=20)
    note('only on imports above quotas · year one: 5,000 units (west germany), 6,000 (japan), 4,000 (all others)', 1080, 760, L(3, 2.0), w=780, size=16)
    text('the objective: time for the domestic industry to adjust', 60, 700, 26, L(4), 30, font='outfit500'); wrap(900)
    heading("tariffs couldn't:", 60, 750, 30, L(5), 30)
    for k, s_ in enumerate(['redesign motorcycles', 'improve production quality', 'rebuild customer confidence']):
        check(60, 795 + k * 50, L(6, k * .4), ok=False, size=30); text(s_, 110, 800 + k * 50, 26, L(6, k * .4), 30, font='outfit500')
    heading('washington: temporary breathing room', 1080, 860, 32, L(7), 30); wrap(780)
    text('a lasting recovery depended on what harley-davidson did next', 1080, 920, 26, L(8), 30, col=RED, font='outfit500'); wrap(780)

@scene(6, 'the turnaround behind the logo')
def s06():
    photo('reagan87', 60, 190, 760, 507, 0, 30, PH_TAG['reagan87'], z0=1.0, z1=1.05)
    chips(['manufacturing processes improved', 'motorcycle components redesigned', 'new marketing programs'], 880, 190, L(1), dt=.4, size=28, gap=52)
    doc('doc_york', 880, 370, 980, L(1, 1.2), L(6), hls=(L(1, 1.6), L(1, 2.0), L(1, 2.4)))
    doc('doc_union', 880, 370, 980, L(6), 30, hls=(L(6, .3), L(7)))
    text('1986', 60, 730, 22, L(3), 30, col=RED, font='mono600'); text('finances restructured · public offering', 140, 728, 24, L(2), 30, font='outfit500')
    doc('doc_k25ipo', 60, 770, 760, L(3), 30, hls=(L(3, .4),))
    text('the tariff created time — management had to use it', 880, 790, 30, L(4), 30, font='outfit500'); wrap(980)
    heading('not just protection: operational improvement', 880, 845, 36, L(7), 30, col=RED); wrap(980)
    text('rebuilding what the famous name alone could not provide', 880, 905, 24, L(8), 30, col=GREY, font='outfit500'); wrap(980)
    heading('and soon, it made an extraordinary request', 60, 960, 34, L(9), 30, col=RED); EV.append((T(L(9)), 'low'))

@scene(7, 'the company that rejected protection')
def s07():
    text('MARCH 1987', 60, 150, 24, L(1), 30, col=RED, font='mono600')
    heading('harley-davidson asks to end its own protection early', 60, 185, 36, L(1), 30); wrap(860)
    doc('doc_york2', 60, 290, 860, L(1, .5), 30, hls=(L(1, .9), L(1, 1.3)))
    doc('doc_p87', 980, 150, 880, L(2), 30, hls=(L(2, .4), L(2, .9)))
    x0, px = 60, 1800 / 5.0; yr = lambda y: x0 + (y - 1983.29) * px
    rect(x0, 600, 1800, 3, GREY, L(2), 30, grow=(L(2), L(2, .8), 'x'))
    for y_, lab, c, t in [(1983.29, 'apr 16, 1983 · relief begins', GREY, L(2)), (1988.29, 'scheduled end · apr 15, 1988', GREY, L(2, .8))]:
        sprite('dot_grey', yr(y_), 601, t, 30); text(lab, yr(y_), 620, 20, t, 30, col=GREY, font='mono600', al='LEFT' if y_ < 1985 else 'RIGHT')
    sprite('dot_red', yr(1987.77), 601, L(3), 30); text('oct 9, 1987 · terminated', yr(1987.77), 548, 22, L(3), 30, col=RED, font='mono600', al='RIGHT')
    rect(yr(1987.77), 596, yr(1988.29) - yr(1987.77), 10, RED, L(3, .3), 30, grow=(L(3, .3), L(3, .8), 'x')); EV.append((T(L(3)), 'impact'))
    heading('a powerful symbol of progress', 60, 700, 40, L(4), 30)
    text('needed temporary protection → prepared to compete without it', 60, 770, 28, L(5), 30, font='outfit500'); wrap(1800)
    check(60, 840, L(6)); text('survived a major competitive crisis', 120, 850, 28, L(6), 30, font='outfit500')
    heading('the next challenge: preserve the identity, keep adapting', 60, 920, 36, L(7), 30, col=RED); wrap(1800)
    text('products · operations · strategy', 60, 985, 22, L(8), 30, col=GREY, font='mono600')

@scene(8, 'the business of belonging')
def s08():
    photo('sturgis06', 60, 190, 800, 600, 0, 30, PH_TAG['sturgis06'])
    chips(['riding communities', 'events', 'clothing', 'a recognizable american lifestyle'], 940, 190, L(2), dt=.35, size=28, gap=50)
    doc('doc_hog', 940, 395, 800, L(2, 1.5), 30, hls=(L(2, 1.9),))
    check(940, 610, L(3)); text("commercially valuable: hard to replicate", 1000, 620, 26, L(3), 30, font='outfit500')
    heading('the strategic dilemma', 940, 680, 36, L(4), 30, col=RED)
    for k, (h_, s_, t) in enumerate([('EXISTING CUSTOMERS', 'how a harley-davidson should look, sound and feel', L(5)), ('NEW CUSTOMERS', 'may want something different', L(6))]):
        x = 940 + k * 470; card_box(x, 735, 450, 130, t, 30, edge=GREY)
        text(h_, x + 26, 750, 18, t, 30, col=RED, font='mono600'); text(s_, x + 26, 785, 24, t, 30, font='outfit500'); wrap(390)
    text('every product decision balances both', 60, 820, 26, L(7), 30, col=GREY, font='outfit500')
    for k, (s_, t) in enumerate([('change too much → the identity weakens', L(8)), ('change too little → less relevant to the next generation', L(9))]):
        x = 60 + k * 920; card_box(x, 880, 880, 100, t, 30, edge=RED); text(s_, x + 30, 910, 28, t, 30, font='outfit500'); wrap(820)

# ═══════════════════════════ ACT 03 · THE SECOND CRISIS ═══════════════════════════
@scene(9, 'the premium motorcycle problem', 'act 03 · the second crisis')
def s09():
    photo('eglide24', 60, 190, 700, 624, 0, 30, PH_TAG['eglide24'])
    text('HDMC MOTORCYCLE SHIPMENTS BY FAMILY · 2025 · FORM 10-K', 840, 170, 18, L(1), 30, col=GREY, font='mono600')
    for k, (lab, n_, p, c) in enumerate([('grand american touring', '69,252', 55.6, RED), ('cruiser', '41,172', 33.1, RED), ('sport and lightweight', '9,638', 7.8, GREY), ('adventure touring', '4,415', 3.5, GREY)]):
        y = 215 + k * 80; t = L(1, .3 + k * .3)
        text(f'{lab} · {n_}', 840, y, 22, t, 30, font='outfit500'); rect(840, y + 34, p * 16, 24, c, t, 30, grow=(t, t + .6, 'x'))
        text(f'{p}%', 850 + p * 16, y + 32, 22, t + .5, 30, col=c, font='mono600')
    heading('touring + cruiser: 88.7% of shipments', 840, 545, 34, L(2), 30, col=RED)
    text('expensive motorcycles are discretionary purchases', 840, 610, 28, L(3), 30, font='outfit500'); wrap(1000)
    chips(['delayed when financing becomes costly', 'delayed when economic confidence weakens'], 840, 660, L(4), dt=.4, size=24, gap=44)
    text('competitors: different preferences, technologies, price points', 840, 760, 22, L(5), 30, col=GREY, font='mono600'); wrap(1000)
    heading('could it build enough demand beyond its established strengths?', 840, 810, 32, L(6), 30, col=RED); wrap(1000)
    check(60, 880, L(8)); text('heritage: an advantage', 120, 890, 28, L(8), 30, font='outfit500')
    check(60, 940, L(9), ok=False); text('not a guarantee of future choices', 120, 950, 28, L(9), 30, font='outfit500')

@scene(10, 'a different kind of crisis')
def s10():
    text('BY 2025', 60, 150, 24, L(1), 30, col=RED, font='mono600')
    heading('a market very different from 1983', 60, 185, 40, L(1), 30)
    doc('doc_macro', 60, 290, 900, L(2), 30, hls=(L(2, .4), L(2, .8), L(3)))
    heading('an expensive recreational purchase', 1040, 290, 32, L(3, .5), 30); wrap(820)
    text('desirable — without being financially urgent', 1040, 350, 26, L(4), 30, col=GREY, font='outfit500'); wrap(820)
    doc('doc_delay', 1040, 420, 820, L(5), 30, hls=(L(5, .4),))
    flow(['customers delay', 'dealer sales', 'production', 'inventory', 'costs'], 60, 680, 310, 100, 50, L(6), dt=.4)
    text('no longer simply: competing against imported motorcycles', 60, 850, 28, L(8), 30, col=GREY, font='outfit500'); strike(60, 868, 760, L(8, .8))
    heading('now: sustaining demand in a difficult market', 60, 910, 40, L(9), 30, col=RED); EV.append((T(L(9)), 'low'))

@scene(11, 'twenty-four thousand fewer motorcycles')
def s11():
    text('HDMC MOTORCYCLE SHIPMENTS TO DEALERS (WHOLESALE) · WORLDWIDE · FORM 10-K', 60, 160, 18, L(1), 30, col=GREY, font='mono600')
    k_ = 420 / 148862
    bars([('2024', 148862, '148,862', L(2), GREY), ('2025', 124477, '124,477', L(3), RED)], 120, 720, 220, 340, k_, lab_size=44, yr_size=24)
    note('bars drawn to scale from zero', 120, 770, L(3), w=600, size=16)
    money('DECLINE', '−24,385', 860, 200, L(4), size=88, sub='−16.4% · motorcycles shipped')
    doc('doc_ship', 860, 395, 1000, L(5), 30, hls=(L(5, .2), L(5, .5), L(6), L(6, .4)))
    text('WHOLESALE ≠ RETAIL: shipments go to dealers, not to consumers', 860, 762, 18, L(5, .6), 30, col=RED, font='mono600'); wrap(1000)
    heading('retail sales of new motorcycles: −12.4%', 60, 830, 40, L(8), 30, col=RED); EV.append((T(L(8)), 'impact'))
    doc('doc_retail', 860, 805, 880, L(7, .5), 30, hls=(L(8, .3),))
    text('lower volumes → consequences for financial performance', 60, 900, 26, L(9), 30, font='outfit500'); wrap(740)

@scene(12, 'when the core business loses money')
def s12():
    text('SEGMENT OPERATING INCOME (LOSS) · US$ MILLIONS · FORM 10-K', 60, 160, 18, L(1), 30, col=GREY, font='mono600')
    Z, k_ = 600, .62; rect(60, Z, 980, 2, GREY, L(1), 30)
    def sbar(x, v, lab, t, c):
        h = abs(v) * k_
        if v >= 0: bar(x, Z, 110, h, c, t); heading(lab, x + 55, Z - h - 52, 30, t + .6, 30, al='CENTER')
        else: rect(x, Z + 2, 110, h, c, t, 30, grow=(t, t + .8, 'y')); heading(lab, x + 55, Z + h + 12, 30, t + .6, 30, al='CENTER', col=c)
    for gx, name, (a_, b_), (ta, tb), cs in [(80, 'motorcycles (hdmc)', (277.8, -28.7), (L(2), L(3)), (GREY, RED)),
                                             (420, 'financial services (hdfs)', (248.4, 490.4), (L(6), L(6, .4)), (GREY, GREY)),
                                             (760, 'livewire', (-109.6, -75.0), (L(8), L(8, .4)), (GREY, GREY))]:
        sbar(gx, a_, f'{a_:+,.1f}'.replace('+', ''), ta, cs[0]); sbar(gx + 130, b_, f'{b_:+,.1f}'.replace('+', ''), tb, cs[1])
        text(name, gx, 770, 20, ta, 30, font='mono600'); text('2024 · 2025', gx, 798, 16, ta, 30, col=GREY, font='mono400')
    doc('doc_hdmc', 1100, 170, 760, L(2), 30, hls=(L(3), L(2, .5), L(4), L(4, .5)))
    heading('not a company-wide operating loss', 1100, 440, 32, L(5), 30); wrap(760)
    note('hdfs 2025 income was lifted by a one-off sale of receivables (the "hdfs transaction"); 2026 guidance: $45–60m', 1100, 530, L(6, .5), w=760, size=17)
    text('NET INCOME, HARLEY-DAVIDSON, INC.: $338.7M (2025) · $455.4M (2024)', 1100, 610, 17, L(6, 1.0), 30, col=TXT, font='mono600'); wrap(760)
    check(1100, 680, L(7)); text('valuable operations and financial resources', 1160, 690, 24, L(7), 30, font='outfit500'); wrap(700)
    check(1100, 750, L(8), ok=False); text('the core motorcycle business struggled', 1160, 760, 24, L(8), 30, font='outfit500'); wrap(700)
    text("the warning wasn't that harley-davidson had disappeared", 60, 840, 28, L(9), 30, font='outfit500'); wrap(1800)
    heading('the economics of its central product business had weakened', 60, 900, 40, L(10), 30, col=RED); wrap(1800); EV.append((T(L(10)), 'low'))

@scene(13, 'the electric bet')
def s13():
    photo('livewire21', 60, 190, 640, 640, 0, 30, PH_TAG['livewire21'], z0=1.0, z1=1.04)
    heading('livewire', 760, 190, 56, L(1), 30)
    text('an effort to participate in a different future for motorcycling', 760, 270, 26, L(2), 30, col=GREY, font='outfit500'); wrap(1100)
    chips(['a new category requires investment', 'commercial success is not guaranteed'], 760, 330, L(3), dt=.4, size=26, gap=48)
    nums([('2024', '612', GREY, L(4)), ('2025', '653', RED, L(4, .5))], 760, 460, L(4), size=88, gap=260)
    text('livewire motorcycle unit shipments · form 10-k', 760, 600, 16, L(4, .5), 30, col=GREY, font='mono600')
    money('OPERATING LOSS · 2025', '−$75.0m', 1340, 460, L(5), size=88, sub='2024: −$109.6m')
    text('harley-davidson motor company · 124,477 (2025)', 760, 670, 18, L(6), 30, col=GREY, font='mono600')
    rect(760, 698, 1000, 24, GREY, L(6), 30, grow=(L(6), L(6, .8), 'x'))
    text('livewire · 653', 760, 735, 18, L(6, .6), 30, col=RED, font='mono600'); rect(760, 763, max(4, 1000 * 653 / 124477), 24, RED, L(6, .6), 30)
    note('bars to scale · 2025 shipments', 1600, 735, L(6, .6), w=260, size=15)
    text("innovation — not yet a financial replacement for the company's traditional products", 760, 830, 26, L(7), 30, font='outfit500'); wrap(1100)
    heading('the challenge: building a sustainable business around it', 760, 920, 36, L(9), 30, col=RED); wrap(1100)

# ═══════════════════════════ ACT 04 · THE AUTOPSY ═══════════════════════════
@scene(14, 'two crises. two different problems.', 'act 04 · the autopsy')
def s14():
    heading('the two crises were not identical', 960, 150, 40, L(1), 30, al='CENTER')
    for k, (yr, rows, rec, src, test, ta, tb) in enumerate([
            ('1983', ['manufacturing competitiveness', 'intense import competition'], 'recovery: trade protection · product improvements · operational changes · financial restructuring', 'white house memo, apr 1, 1983 · proclamation 5727, 1987', 'tested: rebuilding its operations', L(2), L(6)),
            ('2025', ['weaker consumer demand', 'shipments −16.4%', 'manufacturing cost pressure', 'new sources of growth: livewire −$75.0m'], '', 'form 10-k, fy2025', 'tested: sustaining demand and profitability', L(4), L(7))]):
        x = 60 + k * 920; card_box(x, 220, 880, 600, ta, 30)
        heading(yr, x + 40, 245, 56, ta, 30, col=RED)
        chips(rows, x + 40, 340, ta + .3, dt=.35, size=26, gap=48)
        if rec: text(rec, x + 40, 470, 24, L(3), 30, col=GREY, font='outfit500'); wrap(800)
        text(src, x + 40, 690, 15, ta, 30, col=GREY, font='mono600'); wrap(800)
        heading(test, x + 40, 740, 30, tb, 30, col=RED); wrap(800)
    heading('both revealed the limits of relying on an iconic name', 960, 890, 42, L(8), 30, col=RED, al='CENTER'); EV.append((T(L(8)), 'low'))

@scene(15, 'what the evidence reveals')
def s15():
    heading('three lessons', 60, 150, 44, L(1), 30)
    for k, (h_, s_, ev, t) in enumerate([('01 · operational competitiveness', 'brand loyalty cannot substitute for competitive products and efficient operations', 'york, 1987: hours per motorcycle −⅓, inventory −⅔ (as stated by the president)', L(2)),
                                        ('02 · consumer demand', "premium positioning doesn't eliminate exposure to changing consumer demand", 'fy2025: retail −12.4%, shipments −16.4% (form 10-k)', L(3)),
                                        ('03 · sustainable reinvention', 'new products are not the same as a commercially sustainable new business', 'livewire 2025: 653 units, −$75.0m operating loss (form 10-k)', L(4))]):
        x = 60 + k * 610; card_box(x, 240, 580, 420, t, 30)
        text(h_, x + 36, 265, 18, t, 30, col=RED, font='mono600'); heading(s_, x + 36, 310, 30, t, 30); wrap(500)
        text(ev, x + 36, 560, 17, t + .3, 30, col=GREY, font='mono400'); wrap(510)
    text('adaptation: important — and difficult', 60, 710, 30, L(5), 30, font='outfit500')
    text('protect what made it successful, without assuming those strengths will always be enough', 60, 770, 28, L(6), 30, col=GREY, font='outfit500'); wrap(1800)
    heading("not just preserving a famous brand: building a business that can support the brand's future", 60, 860, 40, L(7), 30, col=RED); wrap(1800); EV.append((T(L(8)), 'low'))

@scene(16, 'the verdict')
def s16():
    heading('harley-davidson survived its first great modern crisis', 960, 170, 46, L(1), L(5), al='CENTER')
    heading('because it changed what happened behind the brand', 960, 250, 38, L(1, .6), L(5), al='CENTER', col=RED); EV.append((T(L(1, .6)), 'impact'))
    text('its motorcycles · its manufacturing · its financial position', 960, 330, 28, L(2), L(5), col=GREY, font='outfit500', al='CENTER')
    text('decades later: could it sustain demand while preserving its identity?', 960, 390, 30, L(3), L(5), font='outfit500', al='CENTER')
    photo('war18', 160, 480, 760, 460, L(1), L(5), PH_TAG['war18'])
    photo('eglide24', 1000, 480, 760, 460, L(3), L(5), PH_TAG['eglide24'])
    CX.beat()
    text('THE VERDICT', 960, 180, 26, L(5), L(10), col=GREY, font='mono600', al='CENTER')
    text("the evidence doesn't establish that harley-davidson is destined to fail", 960, 260, 34, L(5, .2), L(10), font='outfit500', al='CENTER')
    heading('even an iconic brand must continually earn its future', 960, 380, 58, L(7), L(10), al='CENTER', col=RED); EV.append((T(L(7)), 'impact'))
    text('heritage can explain why customers loved a company yesterday', 960, 520, 34, L(8), L(10), font='outfit500', al='CENTER')
    text("it cannot guarantee they'll buy from it tomorrow", 960, 580, 34, L(9), L(10), col=GREY, font='outfit500', al='CENTER')
    CX.beat()
    e = heading('brand coroner', 943, 420, 110, L(10), 30, al='CENTER'); e2 = text('.', 1305, 420, 110, L(10, .8), 30, col=RED)
    f = text('EVERY BRAND LEAVES EVIDENCE.', 960, 570, 36, L(10, .4), 30, col=GREY, font='outfit500', al='CENTER')
    rect(810, 555, 300, 2, RED, L(10, .2), 30, grow=(L(10, .2), L(10, 1.0), 'x'))
    for st in (e, e2, f): fade(st, L(10), 30, 1, .6, 2.0)
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
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(D, 'harleydavidson.blend')); bpy.ops.file.make_paths_relative(); bpy.ops.wm.save_mainfile()
print('BUILD OK', len(SCENES), 'scenes', len(EV), 'events', NAMES[0], 'strips')
