"""BRAND CORONER · CASE 003 · COSTCO — "the $1.50 secret"
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
sc = bpy.context.scene; sc.name = 'brand_coroner_case003_costco'
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
    text('brand coroner · case 003', 60, 40, 16, 0, 30, col=GREY, font='mono600')
    text(f'{i:02d} · {title}', 1860, 40, 16, 0, 30, col=GREY, font='mono600', al='RIGHT')
    if act: text(act, 60, 70, 18, 0, 3.5, col=RED, font='mono600')

SCENES = []
def scene(i, title, act=None):
    def deco(fn): SCENES.append((i, title, act, fn)); return fn
    return deco

# ── Costco scene designs (authored on a 0–30 s grid per scene; vo/timeline.json warps them onto the narration) ──
CPI = json.load(open(os.path.join(A, 'cpi.json')))
def have(k): return os.path.exists(os.path.join(A, k + '.png'))
def seg_line(x0, y0, x1, y1, col, t0, t1, ta, tb, th=4):
    """a straight line segment that draws from (x0,y0) to (x1,y1) between ta and tb"""
    L = math.hypot(x1 - x0, y1 - y0); s = rect(x0, y0 - th / 2, L, th, col, t0, t1, grow=(ta, tb, 'x'))
    s.transform.origin = (0, 1); s.transform.rotation = -math.degrees(math.atan2(y1 - y0, x1 - x0)); return s
def reveal(name, t0, t1, ta, tb):
    st = CX.m.sequences.new_image(nm('o'), os.path.join(A, f'ov_{name}.png'), CX.ch(), F(T(t0)), fit_method='ORIGINAL'); st.frame_final_duration = max(1, F(T(t1)) - F(T(t0)))
    st.blend_type = 'ALPHA_OVER'; iw = st.elements[0].orig_width; st.transform.scale_x = st.transform.scale_y = W / iw
    n = 6
    for i in range(n + 1):
        k = i / n; st.crop.max_x = int(iw * (1 - k)); st.crop.keyframe_insert('max_x', frame=F(T(ta + (tb - ta) * k)))
    return st
def chips(items, x, y, t, dt=.8, t1=30, col=TXT, size=34, gap=70):
    for k, s_ in enumerate(items):
        rect(x, y + k * gap + 10, 8, 30, RED, t + k * dt, t1); heading(s_, x + 26, y + k * gap, size, t + k * dt, t1, col=col)
def photo(k, x, y, w, h, t0, t1, tagtxt, **kw):
    if not have('ph_' + k): return None
    im = image('ph_' + k, x, y, w, h, t0, t1, **kw); tag(tagtxt, x, y - 26, t0, t1); EV.append((T(t0), 'shutter')); return im

# ═══════════════════════════ ACT 01 · THE PRICE ═══════════════════════════
@scene(1, 'the price that never moved', 'act 01 · the price')
def s01():
    rect(0, 538, 1920, 4, RED, 1.0, 8.6, grow=(1.0, 3.2, 'x')); EV.append((T(.4), 'register'))
    heading('$1.50', 960, 300, 320, 3.6, 8.6, al='CENTER'); EV.append((T(3.6), 'boom'))
    CX.beat()
    photo('combo', 60, 110, 1100, 780, 8.6, 30, 'photo · costco food court, vancouver · oct 2016 · gotovan · cc by 2.0', fx=.5, fy=.5, z0=1.0, z1=1.07)
    heading('$1.50', 1240, 150, 200, 8.8, 30, col=RED)
    text('hot dog + soda combo', 1244, 380, 34, 9.2, 30, font='outfit500')
    # 1985 → 2026, the nominal price unchanged
    rect(1240, 560, 600, 3, GREY, 12.0, 30, grow=(12.0, 13.4, 'x')); sprite('dot_red', 1240, 561, 12.0, 30); sprite('dot_red', 1840, 561, 13.4, 30)
    text('1985', 1240, 590, 30, 12.0, 30, col=RED, font='mono600'); text('$1.50', 1240, 630, 40, 12.2, 30, font='outfit700')
    text('2026', 1840, 590, 30, 13.4, 30, col=RED, font='mono600', al='RIGHT'); text('$1.50', 1840, 630, 40, 13.6, 30, font='outfit700', al='RIGHT')
    text('nominal price · reported unchanged since 1985', 1244, 710, 20, 14.0, 30, col=GREY, font='mono400')
    for k, w_ in enumerate(['rent', 'wages', 'food costs']): heading(w_, 1240 + k * 200, 780, 36, 18.0 + k * .6, 25.0, col=GREY)
    heading('why?', 1240, 800, 80, 25.0, 30, col=RED); EV.append((T(25.0), 'low'))

@scene(2, 'forty years of inflation')
def s02():
    X0, X1, Y0, Y1 = 220, 1700, 860, 260         # chart box (Y0 = baseline)
    idx = {int(k): v for k, v in CPI['index_1985_100'].items()}; ys = sorted(idx)
    vmax = 320; px = lambda yr: X0 + (yr - 1985) / (2025 - 1985) * (X1 - X0); py = lambda v: Y0 - v / vmax * (Y0 - Y1)
    tag('u.s. cpi-u · annual average · index 1985 = 100 · bls', 60, 84, 0, 30, col=GREY, chip=GREY)
    for v in (0, 100, 200, 300):
        rect(X0, py(v), X1 - X0, 1, '#262626' if v else GREY, .2, 30); text(str(v), X0 - 20, py(v) - 12, 20, .2, 30, col=GREY, font='mono400', al='RIGHT')
    for yr in (1985, 1995, 2005, 2015, 2025): text(str(yr), px(yr), Y0 + 16, 20, .2, 30, col=GREY, font='mono400', al='CENTER')
    ta, tb = 2.0, 14.0
    reveal('cpi', ta, 30, ta, tb)
    EV.append((T(ta), 'draw'))
    text('cpi', px(2025) + 16, py(idx[2025]) - 14, 26, tb, 30, font='mono600'); text(f'{idx[2025]:.0f}', px(2025) + 16, py(idx[2025]) + 16, 30, tb, 30, font='outfit700')
    reveal('flat', 14.0, 30, 14.0, 17.0); EV.append((T(14.0), 'draw'))
    text('combo price $1.50 · unchanged (indexed: 100)', px(1985) + 12, py(100) + 14, 22, 17.0, 30, col=RED, font='mono600')
    rect(1260, 140, 600, 150, PANEL, 20.0, 30); rect(1260, 140, 6, 150, RED, 20.0, 30)
    text('cpi-u, 1985 → 2025', 1290, 156, 22, 20.0, 30, col=GREY, font='mono600'); heading(f'+{idx[2025] - 100:.0f}%', 1290, 190, 64, 20.0, 30)
    text(f'$1.50 in 1985 ≈ ${1.5 * idx[2025] / 100:.2f} in 2025 dollars', 64, 950, 26, 23.0, 30, col=TXT, font='outfit500'); EV.append((T(20.0), 'mark'))

@scene(3, 'a warehouse, not a supermarket')
def s03():
    photo('exterior', 60, 110, 1800, 760, 0, 9.0, 'photo · costco, east lyme, ct · may 2021 · jjbers · cc by 2.0', fx=.5, fy=.4, z0=1.0, z1=1.06)
    CX.beat()
    photo('interior', 60, 110, 1100, 780, 9.0, 30, 'photo · costco warehouse, taipei · mar 2016 · cc0', fx=.5, fy=.5, z0=1.0, z1=1.05)
    chips(['high volume', 'limited selection', 'operational discipline'], 1220, 200, 15.0, dt=1.2)
    doc('doc_wh', 1220, 470, 640, 18.0, 30, hls=(19.0,))
    heading('more for their money', 1220, 760, 48, 24.0, 30, col=RED)

@scene(4, 'the membership agreement')
def s04():
    if have('ph_card'): photo('card', 60, 160, 820, 520, 0, 30, 'photo · costco membership card · cc', fx=.5, fy=.5, z0=1.0, z1=1.05)
    else:
        rect(140, 260, 660, 400, PANEL, .2, 30); rect(140, 260, 660, 400, GREY, .2, 30).blend_type = 'ALPHA_OVER'; rect(142, 262, 656, 396, PANEL, .2, 30)
        heading('membership card', 470, 420, 48, .4, 30, al='CENTER'); tag('editorial illustration · not a real card', 140, 234, .2, 30, col=RED, chip=RED)
    text('paid before the first purchase', 960, 200, 30, 2.0, 30, col=GREY, font='outfit500'); heading('annual membership', 960, 240, 64, 6.0, 30)
    for k, s_ in enumerate(['join', 'shop member prices', 'renew']):
        y = 400 + k * 110; text(f'{k + 1:02d}', 960, y, 26, 10.0 + k * 1.2, 30, col=RED, font='mono600'); heading(s_, 1020, y - 10, 52, 10.0 + k * 1.2, 30); EV.append((T(10.0 + k * 1.2), 'mark'))
    # circular relationship: membership → shopping value → renewal → membership
    cx, cy, R = 1460, 840, 0
    for k, s_ in enumerate(['membership', 'shopping value', 'renewal']):
        x = 960 + k * 330; text(s_, x, 800, 28, 18.0 + k * .8, 30, font='outfit700');
        if k < 2: rect(x + (len(s_) * 15) + 20, 818, 330 - len(s_) * 15 - 40, 3, RED, 18.4 + k * .8, 30, grow=(18.4 + k * .8, 19.0 + k * .8, 'x'))
    rect(960, 870, 900, 3, RED, 20.6, 30, grow=(20.6, 21.6, 'xr')); text('↺', 940, 852, 34, 21.6, 30, col=RED, font='outfit700', al='RIGHT')
    text('the customer relationship · not a causal model', 960, 900, 20, 21.6, 30, col=GREY, font='mono400')
    heading('the promise of value', 960, 960, 44, 24.0, 30, col=RED)

# ═══════════════════════════ ACT 02 · THE MEMBERSHIP MACHINE ═══════════════════════════
@scene(5, 'the money behind the membership', 'act 02 · the membership machine')
def s05():
    doc('doc_is', 60, 150, 1100, 0.2, 30, hls=(3.0, 1.6))
    heading('$5.32 billion', 1240, 170, 84, 1.6, 30, col=TXT); text('membership fees · fiscal 2025', 1244, 280, 26, 1.8, 30, col=GREY, font='mono600')
    doc('doc_renew', 60, 520, 1100, 10.0, 30, hls=(11.0, 11.6))
    heading('92.3%', 1240, 520, 120, 10.6, 30, col=RED); text('renewal rate · u.s. and canada', 1244, 670, 26, 11.0, 30, col=GREY, font='mono600')
    text('(89.8% worldwide)', 1244, 710, 22, 11.4, 30, col=GREY, font='mono400')
    text('revenue, not profit: membership fees are not pure profit', 1244, 800, 24, 20.0, 30, font='outfit500', wrap=620)
    EV.append((T(1.6), 'boom'))

@scene(6, 'the power of fewer choices')
def s06():
    tag('illustrative diagram · not actual costco inventory', 60, 84, 0, 30, col=RED, chip=RED)
    heading('many variations', 60, 140, 40, .4, 30, col=GREY); heading('fewer, larger lines', 1100, 140, 40, 2.0, 30)
    for k in range(16):   # conventional: 16 small SKUs
        x = 80 + (k % 4) * 170; y = 240 + (k // 4) * 130; rect(x, y, 120, 90, '#2a2a2a', .6 + k * .08, 30); rect(x, y, 120, 6, GREY, .6 + k * .08, 30)
    for k in range(3):    # concentrated: 3 large SKUs
        x = 1120 + k * 250; rect(x, 260, 200, 420, '#2a2a2a', 2.2 + k * .3, 30); rect(x, 260, 200, 10, RED, 2.2 + k * .3, 30)
    reveal('streams', 8.0, 30, 8.0, 10.6)    # purchasing streams consolidate
    EV.append((T(8.0), 'draw'))
    chips(['higher volume', 'simpler operations', 'potential cost advantages'], 60, 780, 15.0, dt=1.0, size=30, gap=56)
    heading('low prices are made before the shelf', 1100, 760, 40, 22.0, 30, col=RED)

@scene(7, 'the hot dog problem')
def s07():
    im = photo('hotdog', 60, 110, 1160, 800, 0, 30, 'photo · costco hot dog, vancouver · oct 2016 · gotovan · cc by 2.0', fx=.5, fy=.5, z0=1.0, z1=1.08)
    heading('prepared and served', 1290, 160, 48, 6.0, 30)
    for k, s_ in enumerate(['sausage', 'bun', 'drink', 'labor', 'operations']):
        y = 300 + k * 92; rect(1290, y, 560, 70, PANEL, 10.0 + k * .7, 30); rect(1290, y, 6, 70, RED, 10.0 + k * .7, 30)
        heading(s_.upper(), 1320, y + 14, 34, 10.0 + k * .7, 30); EV.append((T(10.0 + k * .7), 'mark'))
        rect(1150, y + 34, 140, 2, RED, 10.0 + k * .7, 30, grow=(10.0 + k * .7, 10.5 + k * .7, 'xr'))
    text('cost categories, not measured shares', 1290, 780, 22, 14.0, 30, col=GREY, font='mono400')
    heading('costs change over time', 1290, 840, 36, 20.0, 30, col=RED)

@scene(8, 'change the system, not the price')
def s08():
    if have('ph_kirkland'): photo('kirkland', 60, 110, 900, 780, 0, 30, 'photo · kirkland signature product · cc', fx=.5, fy=.5, z0=1.0, z1=1.05)
    else: photo('pallets', 60, 110, 900, 780, 0, 30, 'photo · costco carts · dec 2016 · edna winti · cc by 2.0', fx=.5, fy=.5, z0=1.0, z1=1.05)
    heading('kirkland signature', 1040, 150, 56, 6.0, 30); text('costco’s own hot dogs, from its own plants', 1044, 230, 26, 6.6, 30, col=GREY, font='outfit500')
    text('reported: tracy, california · morris, illinois (2018)', 1044, 276, 20, 7.2, 30, col=GREY, font='mono400')
    chips(['greater supply control', 'purchasing scale', 'operational efficiency'], 1040, 380, 14.0, dt=1.1, size=34)
    text('not immune to inflation', 1044, 640, 30, 20.0, 30, col=GREY, font='outfit700')
    heading('= $1.50', 1040, 720, 140, 25.0, 30, col=RED); EV.append((T(25.0), 'boom'))

# ═══════════════════════════ ACT 03 · THE SIGNAL ═══════════════════════════
@scene(9, 'the psychology of $1.50', 'act 03 · the signal')
def s09():
    k = 'menu' if have('ph_menu') else 'combo'
    photo(k, 60, 110, 1800, 800, 0, 30, 'photo · costco food court menu · jan 2008 · public domain', fx=.5, fy=.5, z0=1.0, z1=1.18)
    dk = rect(60, 110, 1800, 800, '#000000', 12.0, 30, a=.55, fin=2.0)
    heading('$1.50', 960, 330, 260, 6.0, 30, al='CENTER'); EV.append((T(6.0), 'low'))
    text('one price people can remember', 960, 640, 36, 12.6, 30, font='outfit500', al='CENTER')
    heading('a visible signal of value', 960, 720, 56, 18.0, 30, col=RED, al='CENTER')
    text('not proof that every item is the cheapest', 960, 820, 24, 24.0, 30, col=GREY, font='mono600', al='CENTER')

@scene(10, 'the trust equation')
def s10():
    photo('shoppers', 60, 110, 1800, 520, 0, 30, 'photo · costco at dusk · feb 2021 · ambrosia lafluer · cc by 2.0', fx=.5, fy=.5, z0=1.0, z1=1.04)
    for k, (s_, x) in enumerate([('consistent value', 360), ('customer trust', 1260)]):
        rect(x - 80, 700, 540, 110, PANEL, 8.0 + k * 3, 30); rect(x - 80, 700, 540, 110, RED, 8.0 + k * 3, 30).blend_type = 'ALPHA_OVER'; rect(x - 78, 702, 536, 106, PANEL, 8.0 + k * 3, 30)
        heading(s_.upper(), x + 190, 726, 44, 8.0 + k * 3, 30, al='CENTER')
    for j in range(8): rect(920 + j * 40, 752, 22, 4, RED, 10.0 + j * .1, 30)
    text('STRATEGIC INTERPRETATION · NOT MEASURED CAUSALITY', 960, 850, 24, 20.0, 30, col=RED, font='mono600', al='CENTER'); EV.append((T(20.0), 'mark'))

@scene(11, 'scale changes the equation')
def s11():
    doc('doc_is', 60, 150, 1100, 0.2, 12.0, hls=(4.0,))
    heading('$269.9 billion', 1240, 200, 90, 4.0, 12.0, col=TXT); text('net sales · fiscal 2025', 1244, 320, 28, 4.4, 12.0, col=GREY, font='mono600')
    text('sales, not profit · not market value', 1244, 380, 22, 5.0, 12.0, col=RED, font='mono600'); EV.append((T(4.0), 'boom'))
    CX.beat()
    photo('dusk', 60, 110, 1800, 780, 12.0, 30, 'photo · costco warehouse · feb 2021 · ambrosia lafluer · cc by 2.0', fx=.5, fy=.5, z0=1.12, z1=1.0)
    rect(60, 760, 1800, 130, '#000000', 12.4, 30, a=.6); heading('$269.9 billion moves through 914 warehouses', 100, 790, 48, 13.0, 30)
    heading('a system, not a collection of price tags', 960, 940, 36, 22.0, 30, col=RED, al='CENTER')

@scene(12, 'why rivals cannot simply copy it')
def s12():
    heading('why not copy the price?', 60, 120, 56, 0.2, 30)
    rect(60, 240, 860, 560, PANEL, 6.0, 30); heading('LOW PRICE ALONE', 100, 270, 44, 6.0, 30, col=GREY)
    for k, s_ in enumerate(['easy to copy', 'limited impact', 'can reduce earnings']):
        text('✕  ' + s_, 100, 370 + k * 90, 36, 7.0 + k * .8, 30, col=GREY, font='outfit700')
    rect(1000, 240, 860, 560, PANEL, 10.0, 30); rect(1000, 240, 860, 560, RED, 10.0, 30).blend_type = 'ALPHA_OVER'; rect(1002, 242, 856, 556, PANEL, 10.0, 30)
    heading('COSTCO’S SYSTEM', 1040, 270, 44, 10.0, 30, col=RED)
    for k, s_ in enumerate(['purchasing scale', 'operational discipline', 'membership model', 'customer value']):
        text('✓  ' + s_, 1040, 370 + k * 90, 36, 14.0 + k * .8, 30, font='outfit700'); EV.append((T(14.0 + k * .8), 'mark'))
    text('illustrative comparison · not a controlled study', 960, 840, 20, 16.0, 30, col=GREY, font='mono400', al='CENTER')

# ═══════════════════════════ ACT 04 · THE EVIDENCE ═══════════════════════════
@scene(13, 'the price costco will change', 'act 04 · the evidence')
def s13():
    rect(958, 120, 4, 760, RULE, 0, 30)
    text('SEPTEMBER 1, 2024', 60, 140, 30, 0.4, 30, col=RED, font='mono600'); heading('membership fees increased', 60, 180, 52, 0.6, 30)
    doc('doc_fees', 60, 300, 860, 2.0, 30, hls=(3.0,))
    text('u.s. & canada: gold star $60 → $65 · executive $120 → $130 (reported)', 64, 560, 22, 5.0, 30, col=GREY, font='mono400', wrap=860)
    photo('combo', 1000, 350, 860, 460, 10.0, 30, 'photo · hot dog combo · vancouver · 2016 · cc by 2.0', fx=.5, fy=.5)
    text('HOT DOG COMBO', 1000, 140, 30, 10.0, 30, col=RED, font='mono600'); heading('$1.50', 1000, 170, 110, 10.2, 30); EV.append((T(10.0), 'register'))
    heading('not every price is frozen', 960, 880, 44, 18.0, 30, col=RED, al='CENTER')

@scene(14, 'what the numbers actually prove')
def s14():
    heading('loss leader?', 60, 140, 72, 0.2, 30, col=GREY)
    rows = [('VERIFIED', 'historical $1.50 price (reported since 1985)', TXT, 12.0), ('VERIFIED', 'costco financial performance (form 10-k, fy2025)', TXT, 13.4), ('NOT PUBLICLY DISCLOSED', 'exact profit or loss per hot dog combo', RED, 8.0)]
    for k, (lab, s_, col, t) in enumerate(rows):
        y = 300 + k * 150; rect(60, y, 1800, 120, PANEL, t, 30)
        if col == RED: rect(60, y, 1800, 120, RED, t, 30, a=.9).blend_type = 'ALPHA_OVER'; rect(62, y + 2, 1796, 116, PANEL, t, 30)
        text('✓' if col == TXT else '✕', 100, y + 30, 54, t, 30, col=col, font='outfit700'); text(lab, 180, y + 22, 22, t, 30, col=col if col == RED else GREY, font='mono600'); heading(s_, 180, y + 54, 40, t, 30, col=col)
        EV.append((T(t), 'mark'))
    text('documented facts · strategic interpretation · unknown economics', 960, 820, 24, 20.0, 30, col=GREY, font='mono600', al='CENTER')
    heading('no invented per-hot-dog loss', 960, 900, 48, 24.0, 30, col=RED, al='CENTER')

@scene(15, 'the hidden strategic asset')
def s15():
    photo('interior', 60, 110, 1800, 800, 0, 30, 'photo · costco warehouse, taipei · 2016 · cc0', fx=.5, fy=.5, z0=1.1, z1=1.0, a=.35)
    P = [('PRICE CONSISTENCY', 260, 260), ('PURCHASING SCALE', 1060, 260), ('OPERATIONAL DISCIPLINE', 260, 620), ('MEMBERSHIP VALUE', 1060, 620)]
    for k2, (s_, x, y) in enumerate(P):
        t = 1.0 + k2 * 2.6; rect(x, y, 600, 120, '#000000', t, 30, a=.8); rect(x, y, 600, 120, RED, t, 30).blend_type = 'ALPHA_OVER'; rect(x + 3, y + 3, 594, 114, '#0c0c0c', t, 30)
        heading(s_, x + 300, y + 36, 40, t, 30, al='CENTER'); EV.append((T(t), 'mark'))
    reveal('links', 14.0, 30, 14.0, 15.6)
    heading('$1.50', 960, 430, 110, 24.0, 30, col=RED, al='CENTER'); EV.append((T(24.0), 'low'))

@scene(16, 'the final verdict')
def s16():
    photo('exterior', 60, 110, 1800, 780, 0, 21.0, 'photo · costco, east lyme, ct · may 2021 · cc by 2.0', fx=.5, fy=.4, z0=1.06, z1=1.0)
    rect(560, 360, 800, 170, '#F0EDE6', 8.0, 21.0); heading('it’s more than a hot dog.', 960, 400, 64, 8.2, 21.0, col=BG, al='CENTER'); rect(660, 500, 600, 6, RED, 9.0, 21.0, grow=(9.0, 10.0, 'x'))
    heading('$1.50', 960, 600, 120, 14.0, 21.0, col=RED, al='CENTER'); EV.append((T(14.0), 'low'))
    CX.beat()
    e = heading('brand coroner', 943, 420, 110, 23.4, 30, al='CENTER'); e2 = text('.', 1305, 420, 110, 23.4, 30, col=RED)
    f = text('EVERY BRAND LEAVES EVIDENCE.', 960, 570, 36, 24.6, 30, col=GREY, font='outfit500', al='CENTER')
    rect(810, 555, 300, 2, RED, 24.2, 30, grow=(24.2, 25.0, 'x'))
    for st in (e, e2, f): fade(st, 23.4, 30, 1, 0, 2.0)

# ── assemble: one meta strip per scene on the master timeline ──
NF = int(round(DUR * FPS))
bg = SE.sequences.new_effect('background', 'COLOR', 1, frame_start=1, frame_end=NF + 1); bg.color = hexc(BG)
for (i, title, act, fn) in SCENES:
    if TL: sd = TL['scenes'][i - 1]; base, dur, warp = sd['base'], sd['dur'], [tuple(p) for p in sd['warp']]
    else: base, dur, warp = (i - 1) * 30, 30, None
    meta = SE.sequences.new_meta(f'S{i:02d} · {title}', 2, F(base))
    CX = Ctx(meta, base, warp)
    b = meta.sequences.new_effect(nm('bg'), 'COLOR', 1, frame_start=F(base), frame_end=F(base + dur)); b.color = hexc(BG)
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
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(D, 'costco.blend')); bpy.ops.file.make_paths_relative(); bpy.ops.wm.save_mainfile()
print('BUILD OK', len(SCENES), 'scenes', len(EV), 'events', NAMES[0], 'strips')
