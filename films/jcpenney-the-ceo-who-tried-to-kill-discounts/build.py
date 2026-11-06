"""BRAND CORONER · CASE 009 · JCPENNEY — "the CEO who tried to kill discounts"
Blender (4.2 LTS) Python build: constructs the whole 8-minute animatic in the Video Sequence Editor.
  blender -b -P build.py                → writes jcpenney.blend (editable project) and events.json (sound cues)
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
sc = bpy.context.scene; sc.name = 'brand_coroner_case009_jcpenney'
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
    text('brand coroner · case 009', 60, 40, 16, 0, 30, col=GREY, font='mono600')
    text(f'{i:02d} · {title}', 1860, 40, 16, 0, 30, col=GREY, font='mono600', al='RIGHT')
    if act: text(act, 60, 70, 18, 0, 3.5, col=RED, font='mono600')

SCENES = []
def scene(i, title, act=None):
    def deco(fn): SCENES.append((i, title, act, fn)); return fn
    return deco

# ── JCPenney scene designs. Authored on a 0–30 s grid per scene; L(k) is the grid time of narration line k, and
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

# ═══════════════════════════ ACT 01 · THE EXPERIMENT ═══════════════════════════
@scene(1, 'the $4 billion question', 'act 01 · the experiment')
def s01():
    photo('store', 60, 150, 860, 600, 0, 30, PH_TAG.get('store', ''), fx=.5, fy=.5, z0=1.0, z1=1.06)
    text('2012', 1000, 150, 30, L(1), 30, col=RED, font='mono600')
    heading("one of america's oldest department store chains attempted something extraordinary", 1000, 190, 44, L(1), 30); wrap(860)
    heading("break its customers' addiction to discounts", 1000, 360, 48, L(2), 30, col=RED); wrap(860)
    for k, s_ in enumerate(['endless coupons', 'confusing markdowns', 'constant promotional theater']):
        t = L(3, k * .45); text('no ' + s_, 1000, 500 + k * 52, 34, t, 30, col=GREY, font='outfit500'); strike(1062, 524 + k * 52, 22 * len(s_) * .62 + 30, t + .25)
    text('instead: simpler, more predictable prices', 1000, 680, 34, L(4), 30, font='outfit500')
    text('the idea came from an executive who helped transform retail at apple', 60, 790, 30, L(5), 30, col=GREY, font='outfit500', wrap=860)
    text('WITHIN ONE FISCAL YEAR · ANNUAL NET SALES', 1000, 760, 22, L(6), 30, col=GREY, font='mono600')
    heading('− $4.28 billion', 1000, 795, 100, L(6, .3), 30, col=RED); EV.append((T(L(6, .3)), 'impact'))
    text('fiscal 2011 $17.26b → fiscal 2012 $12.99b · form 10-k', 1004, 920, 18, L(6, .6), 30, col=GREY, font='mono400')
    heading('how could a strategy designed to make shopping easier produce such a devastating result?', 60, 960, 36, L(7), 30); wrap(900); EV.append((T(L(7)), 'low'))

@scene(2, 'the man from apple')
def s02():
    photo('johnson', 60, 150, 760, 620, 0, 30, PH_TAG.get('johnson', ''), fx=.45, fy=.35)
    heading('ron johnson', 900, 150, 96, L(1), 30)
    text('arrived with an extraordinary reputation', 904, 270, 32, L(1, .4), 30, col=GREY, font='outfit500')
    text('APPLE · SENIOR VICE PRESIDENT, RETAIL', 900, 340, 22, L(2), 30, col=RED, font='mono600')
    text('a store experience that became one of the most admired in the industry', 900, 375, 30, L(2, .3), 30, font='outfit500', wrap=960)
    text('BEFORE APPLE', 900, 470, 22, L(3), 30, col=GREY, font='mono600'); heading('target', 900, 505, 44, L(3, .2), 30)
    doc('doc_fy11', 1180, 470, 680, L(4), 30, hls=(L(4, .4), L(4, .8), L(4, 1.2)))
    text('NOVEMBER 1, 2011', 900, 600, 22, L(4), 30, col=RED, font='mono600'); heading('chief executive', 900, 635, 40, L(4, .2), 30)
    text('a company struggling to remain relevant', 60, 820, 30, L(5), 30, col=GREY, font='outfit500')
    heading('preserve the status quo', 60, 880, 40, L(6), 30, col=GREY); strike(56, 906, 470, L(6, .8))
    heading('transform it', 620, 880, 40, L(7), 30, col=RED)
    text('FIRST MAJOR TARGET', 1180, 880, 22, L(8), 30, col=GREY, font='mono600')
    heading('the way merchandise was priced', 1180, 920, 44, L(9), 30); EV.append((T(L(9)), 'impact'))

# ═══════════════════════════ ACT 02 · THE CUSTOMER HABIT ═══════════════════════════
@scene(3, 'a century of retail', 'act 02 · the customer habit')
def s03():
    e = L(3)
    photo('penney', 60, 150, 520, 600, 0, e, PH_TAG.get('penney', ''), fx=.5, fy=.35)
    photo('golden', 640, 150, 900, 600, L(1, .6), e, PH_TAG.get('golden', ''), fx=.5, fy=.5, z0=1.0, z1=1.05)
    heading('est. 1902', 1600, 150, 64, L(1), e, col=RED)
    text('founded by james cash penney', 1604, 240, 24, L(1, .3), e, col=GREY, font='outfit500', wrap=280)
    text('generations of shoppers knew its department stores, clothing, household goods and familiar promotional events', 60, 800, 32, L(2), e, font='outfit500', wrap=1800)
    CX.beat()
    heading('by the early twenty-first century', 60, 150, 56, L(3), 30)
    text('traditional department stores faced growing pressure', 60, 230, 32, L(3, .4), 30, col=GREY, font='outfit500')
    chips(['competition was intensifying', 'customers had more places to shop', 'heavily dependent on promotional activity'], 60, 330, L(4), dt=1.4, size=38, gap=80)
    rect(60, 620, 1800, 2, RULE, L(7), 30)
    heading('the company needed a reason for shoppers to choose it', 60, 660, 48, L(7), 30)
    heading('another coupon', 60, 790, 48, L(8), 30, col=GREY); strike(56, 818, 360, L(8, .8))
    heading('a completely different shopping experience', 520, 790, 48, L(9), 30, col=RED); EV.append((T(L(9)), 'impact'))

@scene(4, 'the discount machine')
def s04():
    text('2011', 60, 150, 30, L(1), 30, col=RED, font='mono600')
    heading('590', 60, 190, 220, L(1, .2), 30, col=RED); EV.append((T(L(1, .2)), 'impact'))
    heading('promotional events', 60, 430, 52, L(1, .5), 30)
    text('as cited by the company in 2013 (fortune); an ap report gave 529 · counts vary', 64, 505, 18, L(1, .8), 30, col=GREY, font='mono400')
    for k, s_ in enumerate(['sale', 'offer', 'markdown', 'coupon', 'sale', 'clearance', 'offer', 'sale']):
        t = L(2, k * .2); x, y = 1000 + (k % 4) * 215, 170 + (k // 4) * 110
        card_box(x, y, 195, 86, t, L(3), edge=RED); heading(s_, x + 30, y + 22, 34, t, L(3))
    text('for customers: an almost constant stream', 1000, 400, 28, L(2, .4), L(3), col=GREY, font='outfit500')
    heading('for management, a different problem', 1000, 470, 40, L(3), 30); wrap(860)
    heading('if merchandise was always on sale, what did the original price actually mean?', 60, 600, 48, L(4), 30, col=RED); wrap(1800); EV.append((T(L(4)), 'low'))
    text("johnson's belief: customers would welcome a more straightforward approach", 60, 740, 30, L(5), 30, font='outfit500')
    text('no promotional calendar to navigate · shop with confidence', 60, 790, 30, L(6), 30, col=GREY, font='outfit500')
    text('THE CRUCIAL ASSUMPTION', 60, 870, 22, L(7), 30, col=RED, font='mono600')
    heading('a simpler price  >  the feeling of getting a bargain', 60, 910, 52, L(8), 30)

# ═══════════════════════════ ACT 03 · THE BIG DECISION ═══════════════════════════
@scene(5, 'fair and square', 'act 03 · the big decision')
def s05():
    text('JANUARY 25, 2012 · NEW YORK', 60, 150, 30, L(1), 30, col=RED, font='mono600')
    heading('the transformation plan', 60, 190, 64, L(1, .2), 30)
    text('THE NEW PRICING SYSTEM', 60, 300, 22, L(2), 30, col=GREY, font='mono600')
    heading('fair and square', 60, 335, 96, L(2, .2), 30, col=RED)
    text('three categories', 64, 460, 30, L(3), 30, col=GREY, font='outfit500')
    for k, (s_, sub) in enumerate([('everyday', 'prices'), ('month-long', 'values'), ('best prices', 'the lowest, at designated times')]):
        t = L(4 + k); x = 60 + k * 300; card_box(x, 520, 280, 170, t, 30, edge=RED if k == 2 else GREY)
        heading(s_, x + 30, 550, 36, t, 30); text(sub, x + 30, 605, 22, t, 30, col=GREY, font='outfit500', wrap=230)
    doc('doc_fair', 1000, 150, 860, L(4), 30, hls=(L(4, .3), L(5, .3), L(6, .3), L(8)))
    text('best prices: first and third fridays of each month (reported)', 1000, 560, 18, L(6, .5), 30, col=GREY, font='mono400')
    text('FEBRUARY 1, 2012', 1000, 610, 22, L(7), 30, col=RED, font='mono600'); heading('the new strategy begins', 1000, 645, 40, L(7, .2), 30)
    text('not eliminating every promotion', 60, 740, 30, L(8), 30, font='outfit500')
    text('abandoning the constant cycle of coupons and temporary markdowns', 60, 790, 30, L(9), 30, col=GREY, font='outfit500', wrap=880)
    rect(60, 880, 1800, 2, RULE, L(10), 30)
    text('changing more than prices', 60, 910, 34, L(10), 30, col=GREY, font='outfit500')
    heading('changing how shoppers understood value', 700, 900, 52, L(11), 30, col=RED); EV.append((T(L(11)), 'impact'))

@scene(6, 'the logic')
def s06():
    heading('on paper, the logic was compelling', 60, 150, 60, L(1), 30)
    for k, (s_, t) in enumerate([('simpler prices · less confusion', L(2)), ('no waiting for a coupon · no doubting a sale', L(3)), ('less energy on promotions · more on merchandise and stores', L(4)), ('individual branded shops inside the store', L(5))]):
        y = 260 + k * 100; card_box(60, y, 1100, 82, t, 30); check(90, y + 14, t, size=44); heading(s_, 160, y + 20, 34, t, 30)
    heading('the ambition was enormous', 1240, 280, 48, L(6), 30); wrap(620)
    rect(60, 700, 1800, 2, RULE, L(7), 30)
    text('a successful strategy requires more than internal logic', 60, 730, 34, L(7), 30, col=GREY, font='outfit500')
    heading('it must fit the behavior of the people who actually buy the product', 60, 800, 48, L(8), 30, col=RED); wrap(1800)
    text('jcpenney was about to discover that distinction', 60, 960, 30, L(9), 30, font='outfit500'); EV.append((T(L(9)), 'low'))

@scene(7, 'the psychology of a sale')
def s07():
    heading('imagine two shirts', 60, 150, 60, L(1), 30)
    text('ILLUSTRATION', 1860, 160, 20, L(1), 30, col=GREY, font='mono600', al='RIGHT')
    for k, x in enumerate((160, 1000)):
        t = L(2 + k); card_box(x, 270, 760, 380, t, 30, edge=GREY if k == 0 else RED); EV.append((T(t), 'paper'))
        text('SHIRT A · REGULAR PRICE' if k == 0 else 'SHIRT B · MARKED DOWN', x + 40, 300, 22, t, 30, col=GREY if k == 0 else RED, font='mono600')
        if k == 1: heading('$60', x + 40, 350, 80, t, 30, col=GREY); strike(x + 36, 395, 160, t + .5)
        heading('$40', x + 40 if k == 0 else x + 260, 350, 160, t + (.0 if k == 0 else .8), 30)
        text('everyday price' if k == 0 else 'sale price', x + 44, 580, 28, t, 30, col=GREY, font='outfit500')
    heading('the customer pays exactly the same', 960, 700, 44, L(4), 30, al='CENTER')
    text('but shirt b appears to offer the bigger bargain', 960, 770, 32, L(5), 30, col=RED, font='outfit500', al='CENTER')
    CX.beat()
    text('RETAIL PSYCHOLOGY', 60, 830, 22, L(6), 30, col=GREY, font='mono600')
    heading('a reference price shapes how attractive an offer feels', 60, 865, 40, L(7), 30); wrap(900)
    text("jcpenney's new approach challenged that habit", 1000, 840, 28, L(8), 30, col=GREY, font='outfit500')
    text('trust the everyday price — without a dramatic markdown', 1000, 885, 28, L(9), 30, font='outfit500', wrap=860)
    heading('a major change', 1000, 960, 40, L(10), 30, col=RED); EV.append((T(L(10)), 'low'))

@scene(8, 'the first warning')
def s08():
    e = L(5)
    heading('the early results were troubling', 60, 150, 60, L(1), e)
    text('customers did not embrace the transformation at the scale management anticipated', 60, 250, 32, L(2), e, col=GREY, font='outfit500', wrap=1800)
    heading('sales weakened sharply', 60, 340, 64, L(3), e, col=RED); EV.append((T(L(3)), 'impact'))
    text('AS THE YEAR PROGRESSED', 60, 480, 22, L(4), e, col=GREY, font='mono600')
    text('messaging and promotions adjusted', 60, 520, 34, L(4, .2), e, font='outfit500')
    text('aug 2012: “month-long values” dropped; “best prices” renamed clearance (ap, july 26, 2012)', 60, 580, 18, L(4, .6), e, col=GREY, font='mono400')
    CX.beat()
    text('CHANGING AT THE SAME TIME', 60, 150, 22, L(5), 30, col=RED, font='mono600')
    for k, s_ in enumerate(['prices', 'marketing', 'merchandise', 'store experience']):
        t = L(5, k * .35); x = 60 + k * 450; card_box(x, 200, 420, 100, t, 30); heading(s_, x + 36, 228, 40, t, 30)
    heading('an unusually difficult turnaround', 60, 350, 44, L(6), 30)
    heading('if customers stopped visiting, which part was responsible?', 60, 460, 48, L(7), 30)
    for k, s_ in enumerate(['the pricing?', 'the products?', 'the advertising?', 'the pace of change itself?']):
        t = L(8 + k); heading(s_, 60 + k * 440, 590, 40, t, 30, col=RED if k == 3 else TXT)
    rect(60, 760, 1800, 2, RULE, L(12), 30)
    heading('the financial results would soon make the problem impossible to ignore', 60, 800, 44, L(12), 30); wrap(1800); EV.append((T(L(12)), 'low'))

# ═══════════════════════════ ACT 04 · THE EVIDENCE ═══════════════════════════
@scene(9, 'the numbers', 'act 04 · the evidence')
def s09():
    text('ANNUAL NET SALES · $ BILLIONS', 60, 150, 22, L(1), 30, col=GREY, font='mono600')
    bars([('FISCAL 2011', 17.26, '$17.26B', L(1), GREY), ('FISCAL 2012', 12.99, '$12.99B', L(2), RED)], 120, 800, 260, 380, 26, lab_size=56)
    doc('doc_fy12', 1000, 150, 860, L(2, .5), 30, hls=(L(2, 1.0), L(3), L(4), L(5)))
    heading('− 24.8%', 1000, 620, 72, L(3), 30, col=RED); text('total net sales', 1004, 710, 22, L(3, .3), 30, col=GREY, font='mono600')
    heading('− 25.2%', 1420, 620, 72, L(4), 30, col=RED); text('comparable store sales', 1424, 710, 22, L(4, .3), 30, col=GREY, font='mono600')
    text('gross margin 36.0% → 31.3% of sales', 1000, 760, 28, L(5), 30, font='outfit500')
    text('these figures do not isolate pricing from every other change', 60, 870, 28, L(6), 30, col=GREY, font='outfit500')
    text('but they reveal the scale of the crisis', 1000, 830, 28, L(7), 30, font='outfit500')
    heading('one of the most damaging years in its modern history', 60, 940, 44, L(8), 30, col=RED); EV.append((T(L(8)), 'low'))

@scene(10, 'the stores go quiet')
def s10():
    photo('interior', 60, 150, 860, 645, 0, 30, PH_TAG.get('interior', ''))
    text('THE ANNUAL REPORT', 1000, 150, 22, L(1), 30, col=GREY, font='mono600')
    doc('doc_traffic', 1000, 190, 860, L(1, .2), 30, hls=(L(1, .6), L(3), L(4)))
    for k, s_ in enumerate(['fewer visits', 'fewer transactions', 'fewer items sold']):
        t = L(2 + k); sprite('arrow_red_d', 1020, 620 + k * 56 + 20, t, 30); heading(s_, 1050, 620 + k * 56, 38, t, 30)
    text('substantial fixed operating costs: employees · inventory · utilities · space', 60, 830, 28, L(5), 30, font='outfit500', wrap=880)
    text('they stay even when customers stop buying', 60, 910, 26, L(6), 30, col=GREY, font='outfit500')
    text('not simply a lack of excitement', 1000, 830, 28, L(7), 30, col=GREY, font='outfit500')
    heading('losing the sales volume it needed to support its operations', 1000, 880, 36, L(8), 30, col=RED); wrap(860)
    text('more than another advertising campaign', 1000, 990, 26, L(9), 30, font='outfit500'); EV.append((T(L(9)), 'low'))

@scene(11, 'the bigger reinvention')
def s11():
    photo('mall', 60, 150, 860, 645, 0, 30, PH_TAG.get('mall', ''))
    heading("pricing was only one part of johnson's plan", 1000, 150, 40, L(1), 30); wrap(860)
    doc('doc_shops', 1000, 270, 860, L(2), 30, hls=(L(2, .4), L(2, .8)))
    text('THE SHOPS · OPENED IN 2012', 1000, 640, 20, L(2, 1.0), 30, col=GREY, font='mono600')
    text("levi's · izod · liz claiborne · arizona · jcp · sephora", 1000, 670, 24, L(2, 1.2), 30, font='outfit500')
    text('merchandise · presentation · marketing · customer experience', 1000, 720, 24, L(3), 30, col=GREY, font='outfit500')
    text('modernize the entire retailer', 60, 820, 30, L(4), 30, font='outfit500')
    heading('the initiatives were interconnected', 60, 870, 40, L(5), 30, col=RED)
    for k, s_ in enumerate(['merchandise → unsettle shoppers', 'promotions → reasons to visit', 'layouts → time and investment']):
        text(s_, 1000, 780 + k * 46, 28, L(6 + k), 30, font='outfit500'); EV.append((T(L(6 + k)), 'type'))
    text("rebuilding its identity while depending on existing customers to fund it", 60, 960, 30, L(9), 30, col=GREY, font='outfit500'); EV.append((T(L(9)), 'low'))

@scene(12, 'the leadership crisis')
def s12():
    photo('johnson', 60, 150, 620, 560, 0, 30, PH_TAG.get('johnson', ''), fx=.45, fy=.35)
    text('BY 2013', 760, 150, 30, L(1), 30, col=RED, font='mono600')
    heading("the pressure on leadership was intense", 760, 190, 48, L(1, .2), 30); wrap(1100)
    text('promotions already being modified · confidence in the turnaround damaged', 760, 270, 28, L(2), 30, col=GREY, font='outfit500', wrap=1100)
    doc('doc_apr13', 760, 360, 760, L(4), 30, hls=(L(4, .4), L(4, .8), L(5)))
    text('APRIL 8, 2013', 1560, 360, 22, L(4), 30, col=RED, font='mono600')
    heading('johnson replaced', 1560, 395, 36, L(4, .2), 30); wrap(300)
    card_box(1560, 500, 300, 140, L(5), 30)
    text('RETURNS', 1590, 520, 20, L(5), 30, col=GREY, font='mono600'); heading('myron ullman', 1590, 555, 34, L(5, .2), 30)
    text('former ceo, 2004–2011', 1590, 600, 20, L(5, .4), 30, col=GREY, font='outfit500')
    heading('tenure: less than eighteen months', 60, 740, 44, L(6), 30)
    text('nov 1, 2011 → apr 8, 2013', 64, 800, 22, L(6, .3), 30, col=GREY, font='mono600')
    text('gone before the broader store transformation could be completed', 60, 850, 30, L(7), 30, font='outfit500')
    heading('could the company win back the customers it had lost?', 60, 940, 48, L(8), 30, col=RED); EV.append((T(L(8)), 'low'))

# ═══════════════════════════ ACT 05 · THE AFTERMATH ═══════════════════════════
@scene(13, 'bringing back the customer', 'act 05 · the aftermath')
def s13():
    heading('rebuilding the promotional relationship', 60, 150, 56, L(1), 30)
    chips(['restore familiar marketing', 'stabilize merchandise strategy'], 60, 270, L(2), dt=.8, size=40, gap=76)
    text('2013: coupons back in newspaper advertising (bloomberg, apr 2013)', 64, 430, 18, L(2, .6), 30, col=GREY, font='mono400')
    heading('trust and shopping habits do not return automatically', 1000, 270, 44, L(3), 30, col=RED); wrap(860)
    text('recovering sales while absorbing the financial consequences of the failed transformation', 60, 540, 32, L(4), 30, font='outfit500', wrap=1800)
    text('THE PRESSURES THAT PRE-DATED JOHNSON', 60, 660, 22, L(5), 30, col=GREY, font='mono600')
    chips(['changing consumer behavior', 'powerful alternatives'], 60, 700, L(6), dt=.6, size=36, gap=66, bar=GREY)
    heading('an internal strategic shock — inside a difficult industry', 60, 900, 48, L(7), 30); EV.append((T(L(7)), 'low'))

@scene(14, 'the 2020 bankruptcy')
def s14():
    photo('sephora', 60, 150, 860, 485, 0, 30, PH_TAG.get('sephora', ''))
    text('MAY 15, 2020', 1000, 150, 30, L(1), 30, col=RED, font='mono600')
    heading('chapter 11', 1000, 190, 110, L(1, .2), 30, col=RED); EV.append((T(L(1, .2)), 'impact'))
    doc('doc_may20', 1000, 340, 860, L(1, .6), 30, hls=(L(1, 1.0), L(3), L(2)))
    text('years of financial pressure and changing retail conditions', 60, 680, 30, L(2), 30, font='outfit500', wrap=860)
    text('covid-19: another severe disruption', 60, 760, 30, L(3), 30, col=GREY, font='outfit500')
    card_box(60, 830, 1800, 90, L(4), 30)
    heading('misleading: “the 2012 pricing strategy alone caused the bankruptcy”', 96, 856, 36, L(4), 30, col=GREY); strike(92, 880, 1150, L(4, .9))
    text('multiple structural challenges', 1300, 860, 28, L(5), 30, font='outfit500')
    text('the 2012 collapse: an important chapter · a costly transformation weakened the company when it needed a sustainable path', 60, 960, 24, L(6), 30, col=RED, font='outfit500', wrap=1800); EV.append((T(L(7)), 'low'))

# ═══════════════════════════ ACT 06 · THE AUTOPSY ═══════════════════════════
@scene(15, 'what actually went wrong?', 'act 06 · the autopsy')
def s15():
    heading('the evidence points to four strategic problems', 60, 150, 56, L(1), 30)
    for k, (s_, t) in enumerate([('underestimated how customers responded to discounts', L(2)), ('changed deeply established shopping habits too quickly', L(3)), ('transformed pricing, merchandise, marketing and stores at once', L(4)), ('created enormous financial pressure before the new model proved itself', L(5))]):
        y = 260 + k * 105; card_box(60, y, 1800, 88, t, 30); text(f'{k + 1:02d}', 90, y + 22, 40, t, 30, col=RED, font='mono600'); heading(s_, 180, y + 22, 36, t, 30)
    text('fair and square was not necessarily a bad idea in every retail environment', 60, 730, 32, L(6), 30, col=GREY, font='outfit500')
    heading('at jcpenney, it collided with the expectations of the customers the company needed most', 60, 800, 52, L(7), 30, col=RED); wrap(1800); EV.append((T(L(7)), 'low'))

@scene(16, 'the verdict')
def s16():
    heading('ron johnson helped build one of the most successful', 960, 200, 48, L(1), L(6), al='CENTER')
    heading('retail experiences in the world', 960, 265, 48, L(1), L(6), al='CENTER')
    heading('but jcpenney was not apple', 960, 400, 72, L(2), L(6), al='CENTER', col=RED); EV.append((T(L(2)), 'impact'))
    for k, s_ in enumerate(['different customer expectations', 'different business constraints']):
        text(s_, 960, 530 + k * 56, 34, L(3 + k), L(6), col=GREY, font='outfit500', al='CENTER')
    text('the habits that brought shoppers through its doors', 960, 690, 32, L(5), L(6), font='outfit500', al='CENTER')
    text('could not be erased by a new pricing philosophy', 960, 735, 32, L(5), L(6), font='outfit500', al='CENTER')
    CX.beat()
    text('THE VERDICT', 960, 220, 26, L(6), L(9), col=GREY, font='mono600', al='CENTER')
    heading('the lesson is bigger than coupons', 960, 290, 56, L(6, .2), L(9), al='CENTER')
    heading('a strategy can look elegant on paper', 960, 410, 44, L(7), L(9), al='CENTER')
    heading('and still misunderstand the people it serves', 960, 470, 44, L(7), L(9), al='CENTER')
    heading('changing a business is not the same', 960, 590, 52, L(8), L(9), al='CENTER', col=RED); heading('as changing its customers', 960, 660, 52, L(8), L(9), al='CENTER', col=RED); EV.append((T(L(8)), 'impact'))
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
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(D, 'jcpenney.blend')); bpy.ops.file.make_paths_relative(); bpy.ops.wm.save_mainfile()
print('BUILD OK', len(SCENES), 'scenes', len(EV), 'events', NAMES[0], 'strips')
