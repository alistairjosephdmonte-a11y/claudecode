"""BRAND CORONER · CASE 013 · NEW COKE — "the decision that backfired"
Blender (4.2 LTS) Python build: constructs the whole 8-minute animatic in the Video Sequence Editor.
  blender -b -P build.py                → writes newcoke.blend (editable project) and events.json (sound cues)
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
sc = bpy.context.scene; sc.name = 'brand_coroner_case013_newcoke'
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
    text('brand coroner · case 013', 60, 40, 16, 0, 30, col=GREY, font='mono600')
    text(f'{i:02d} · {title}', 1860, 40, 16, 0, 30, col=GREY, font='mono600', al='RIGHT')
    if act: text(act, 60, 70, 18, 0, 3.5, col=RED, font='mono600')

SCENES = []
def scene(i, title, act=None):
    def deco(fn): SCENES.append((i, title, act, fn)); return fn
    return deco

# ── New Coke scene designs. Authored on a 0–30 s grid per scene; L(k) is the grid time of narration line k, and
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

# ═══════════════════════════ ACT 01 · THE BRAND ═══════════════════════════
@scene(1, 'the 79-day disaster', 'act 01 · the brand')
def s01():
    photo('newcan', 90, 220, 300, 540, 0, 30, PH_TAG.get('newcan', ''), contain=True)
    text('APRIL 23, 1985', 480, 150, 30, L(1), 30, col=RED, font='mono600')
    heading('one of the most infamous decisions in business history', 480, 190, 52, L(1, .2), 30); wrap(1380)
    heading('coca-cola replaces the taste of its flagship drink', 480, 340, 40, L(2), 30, col=RED); wrap(1380)
    money('TASTE-TESTED ON', 'nearly 200,000', 480, 430, L(3), size=84, sub='consumers · coca-cola company history (time, may 6, 1985: "more than 190,000")')
    text('the research looked convincing', 1200, 470, 30, L(4), 30, font='outfit500')
    chips(['anger', 'protests', 'demands for the original coke'], 1200, 530, L(5), dt=.5, size=30, gap=52)
    for k, (d_, s_) in enumerate([('APR 23, 1985', 'reformulation announced'), ('JUL 11, 1985', 'the original returns')]):
        t = L(6, k * .5); x = 480 + k * 700; rect(x, 760, 680, 3, RED if k else GREY, t, 30, grow=(t, t + .4, 'x')); sprite('dot_red' if k else 'dot_grey', x + 8, 761, t, 30)
        text(d_, x, 785, 22, t, 30, col=RED if k else GREY, font='mono600'); text(s_, x, 820, 28, t, 30, font='outfit500')
    heading('79 days', 1520, 690, 56, L(6, 1.0), 30, col=RED); EV.append((T(L(6, 1.0)), 'impact'))
    heading('how did a brand with extraordinary research misunderstand its own customers?', 60, 920, 40, L(7), 30, col=RED); wrap(1800); EV.append((T(L(7)), 'low'))

@scene(2, 'the most famous drink in america')
def s02():
    photo('marker', 60, 150, 380, 676, 0, 30, PH_TAG.get('marker', ''))
    photo('ad1890', 480, 205, 440, 590, L(2), 30, PH_TAG.get('ad1890', ''))
    photo('contour', 1000, 260, 300, 360, L(3), 30, PH_TAG.get('contour', ''), contain=True)
    text('ATLANTA · 1886', 1380, 150, 30, L(1), 30, col=RED, font='mono600')
    heading('coca-cola begins', 1380, 190, 56, L(1, .2), 30)
    text('pharmacist john s. pemberton (time, may 6, 1985)', 1384, 270, 20, L(1, .5), 30, col=GREY, font='mono600', wrap=470)
    text('much more than a soft drink', 1380, 340, 30, L(2), 30, font='outfit500', wrap=470)
    chips(['the bottle', 'red-and-white identity', 'advertising', 'a place in american culture'], 1000, 640, L(3), dt=.4, size=28, gap=48)
    text('familiar experiences · family gatherings · sporting events · everyday routines', 60, 860, 26, L(4), 30, col=GREY, font='outfit500')
    heading('it sold refreshment — and recognition and continuity', 60, 920, 40, L(5), 30); wrap(1800)
    text('by the early 1980s: a commercial advantage', 1380, 430, 28, L(6), 30, font='outfit500', wrap=470)
    heading('and an obligation executives would soon underestimate', 1380, 520, 32, L(7), 30, col=RED); wrap(470); EV.append((T(L(7)), 'low'))

@scene(3, 'pepsi was closing in')
def s03():
    heading('the pressure came from pepsi', 60, 150, 52, L(1), 30)
    photo('challenge', 60, 270, 400, 500, L(1, .3), 30, PH_TAG.get('challenge', ''))
    doc('doc_share', 520, 270, 760, L(2, .5), 30, hls=(L(3, .2), L(3, .6), L(4, .4)))
    doc('doc_lead', 520, 600, 760, L(4, .2), 30, hls=(L(4, .8),))
    text('1970s – EARLY 1980s', 1340, 270, 22, L(2), 30, col=RED, font='mono600')
    for k, s_ in enumerate(['advertising for younger consumers', 'the pepsi challenge: blind taste tests']):
        t = L(3, k * .8); rect(1340, 320 + k * 90 + 7, 8, 26, RED, t, 30); heading(s_, 1366, 320 + k * 90, 28, t, 30); wrap(480)
    text('coca-cola remained enormously successful', 1340, 520, 26, L(4), 30, font='outfit500', wrap=500)
    text('but its lead over its rival was slipping', 1340, 600, 26, L(4, .4), 30, col=GREY, font='outfit500', wrap=500)
    heading('the threat was real', 1340, 700, 40, L(5), 30, col=RED); EV.append((T(L(5)), 'impact'))
    text('how to respond?', 1340, 770, 30, L(6), 30, font='outfit500')
    heading('defend its distinctive identity?', 60, 900, 40, L(7), 30)
    heading('or change its core product to compete on taste?', 760, 900, 40, L(7, .6), 30, col=RED); EV.append((T(L(7)), 'low'))

# ═══════════════════════════ ACT 02 · THE DECISION ═══════════════════════════
@scene(4, 'the data looked convincing', 'act 02 · the decision')
def s04():
    heading('a sweeter formula', 60, 150, 56, L(1), 30)
    text('performed strongly in taste tests', 60, 230, 28, L(1, .4), 30, col=GREY, font='outfit500')
    doc('doc_tests', 1000, 150, 860, L(2), 30, hls=(L(2, .2), L(2, .5), L(3, .2), L(3, .7)))
    money('1981–1984 · 25 CITIES · U.S. AND CANADA', '190,000+', 60, 290, L(2), size=96, sub='consumers tested (time) · "nearly 200,000" (company history)')
    text('BLIND COMPARISONS · NEW FORMULA VS ORIGINAL (TIME, MAY 6, 1985)', 60, 510, 20, L(3), 30, col=GREY, font='mono600')
    bars([('NEW FORMULA', 55, '55%', L(3, .2), RED), ('ORIGINAL', 45, '45%', L(3, .4), GREY)], 140, 850, 200, 300, 4.4)
    text('told which was which: 61% to 39%', 60, 905, 22, L(3, .8), 30, col=GREY, font='mono600')
    text('to executives: a major opportunity', 1000, 600, 28, L(4), 30, font='outfit500', wrap=420)
    text('change the flagship to restore momentum?', 1000, 700, 28, L(5), 30, col=GREY, font='outfit500', wrap=420)
    photo('grocery73', 1460, 600, 400, 270, L(5), 30, PH_TAG.get('grocery73', ''))
    heading('a laboratory preference ≠ a purchasing decision made in a store', 1000, 900, 34, L(6), 30, col=RED); wrap(860); EV.append((T(L(6)), 'low'))

@scene(5, "the question they didn't ask")
def s05():
    heading('the weakness was not a lack of data', 60, 150, 52, L(1), 30)
    text('enormous amounts of data about taste', 60, 235, 30, L(2), 30, col=GREY, font='outfit500')
    text('the problem: what that data could not fully explain', 60, 290, 30, L(3), 30, font='outfit500')
    text('EDITORIAL COMPARISON', 60, 360, 20, L(4), 30, col=GREY, font='mono600')
    card_box(60, 400, 880, 230, L(4), 30, edge=GREY); text('ANONYMOUS SAMPLES · BLIND TEST', 94, 425, 20, L(4), 30, col=GREY, font='mono600')
    card_box(980, 400, 880, 230, L(4, .5), 30); text('LOYAL CUSTOMERS · TOLD THEIR DRINK WOULD DISAPPEAR', 1014, 425, 20, L(4, .5), 30, col=RED, font='mono600')
    heading('"which liquid tastes better?"', 94, 490, 44, L(5), 30, col=GREY)
    heading('"replace something we love?"', 1014, 490, 44, L(6), 30, col=RED)
    heading('not interchangeable', 60, 690, 48, L(7), 30, col=RED); EV.append((T(L(7)), 'impact'))
    doc('doc_bond', 980, 690, 880, L(7, .3), 30, hls=(L(7, .6), L(8, .3)))
    text('the research emphasized the first', 60, 790, 30, L(8), 30, col=GREY, font='outfit500')
    heading('its most passionate customers cared about the second', 60, 850, 36, L(8, .4), 30); wrap(880); EV.append((T(L(8)), 'low'))

@scene(6, 'the executive bet')
def s06():
    photo('hq06', 60, 150, 480, 640, 0, 30, PH_TAG.get('hq06', ''))
    heading('the decision reached the top', 600, 150, 52, L(1), 30)
    text('ROBERTO GOIZUETA · CHAIRMAN AND CHIEF EXECUTIVE', 600, 240, 22, L(2), 30, col=RED, font='mono600')
    text('championed the change, supported by senior leadership', 600, 280, 28, L(2, .3), 30, font='outfit500')
    text('donald keough · president and chief operating officer', 600, 330, 20, L(2, .6), 30, col=GREY, font='mono600')
    doc('doc_ann', 600, 390, 820, L(3), 30, hls=(L(3, .4), L(3, .8)))
    text('strengthen its position against pepsi', 1460, 400, 26, L(3, .2), 30, col=GREY, font='outfit500', wrap=400)
    heading('another flavor extension', 600, 730, 40, L(4), 30, col=GREY); strike(596, 752, 500, L(4, .6))
    heading('replace the original taste of its flagship cola', 600, 800, 40, L(5), 30, col=RED); EV.append((T(L(5)), 'impact'))
    text('a product decision → a challenge to the brand\'s identity', 60, 870, 30, L(6), 30, font='outfit500')
    heading('something new alongside the familiar', 60, 935, 40, L(7), 30, col=GREY); strike(56, 957, 720, L(7, .6))
    heading('taking the familiar away', 1000, 935, 40, L(8), 30, col=RED); EV.append((T(L(8)), 'low'))

@scene(7, 'april 23, 1985')
def s07():
    photo('beaumont', 60, 150, 860, 573, 0, 30, PH_TAG.get('beaumont', ''))
    text('APRIL 23, 1985 · NEW YORK', 1000, 150, 30, L(1), 30, col=RED, font='mono600')
    heading('lincoln center: the reformulation unveiled', 1000, 190, 48, L(1, .2), 30); wrap(860)
    text('goizueta: "smoother, rounder, yet bolder — a more harmonious flavor" (as quoted by history.com)', 1000, 320, 22, L(2), 30, col=GREY, font='mono600', wrap=860)
    photo('newcan', 1000, 440, 190, 340, L(3), 30, PH_TAG.get('newcan', ''), contain=True)
    text('"white- and-red cans bearing the word NEW on a silver strip"', 1230, 460, 28, L(3, .2), 30, font='outfit500', wrap=630)
    text('time, may 6, 1985', 1230, 570, 20, L(3, .4), 30, col=GREY, font='mono600')
    text('promoted as a major improvement · years of research and testing', 60, 760, 28, L(2, .5), 30, font='outfit500')
    text('enormous attention — what a launch hopes for', 60, 815, 28, L(4), 30, col=GREY, font='outfit500')
    text('but it quickly became difficult to control', 60, 865, 28, L(5), 30, font='outfit500')
    text('"... will totally supplant the old Coke" — time, may 6, 1985', 1230, 640, 22, L(6), 30, col=GREY, font='mono600', wrap=630)
    heading('not: an exciting new drink', 60, 935, 40, L(6), 30, col=GREY); strike(56, 957, 520, L(6, .6))
    heading('their old coca-cola was no longer available', 700, 935, 40, L(7), 30, col=RED); EV.append((T(L(7)), 'low'))

# ═══════════════════════════ ACT 03 · THE BACKLASH ═══════════════════════════
@scene(8, 'the backlash begins', 'act 03 · the backlash')
def s08():
    heading('immediate and emotional', 60, 150, 56, L(1), 30)
    for k, (s_, t) in enumerate([('customers called to complain', L(2)), ('some stockpiled the original', L(3)), ('protest groups formed', L(4)), ("atlanta: the company's own hometown", L(5))]):
        rect(60, 270 + k * 70 + 9, 8, 30, RED, t, 30); heading(s_, 86, 270 + k * 70, 36, t, 30)
    doc('doc_stock', 1000, 150, 860, L(3), 30, hls=(L(3, .4), L(5), L(5, .4)))
    doc('doc_mullins', 1000, 490, 860, L(4), 30, hls=(L(4, .4), L(4, .8)))
    heading('the scale surprised management', 60, 600, 40, L(6), 30)
    text('treated as: a taste improvement', 60, 680, 28, L(7), 30, col=GREY, font='outfit500')
    text('interpreted as: the removal of something culturally important', 60, 730, 28, L(7, .5), 30, font='outfit500', wrap=880)
    heading('people can identify strongly with an everyday product', 60, 900, 40, L(8), 30, col=RED); wrap(1800); EV.append((T(L(8)), 'low'))

@scene(9, "the phones wouldn't stop")
def s09():
    heading('by june 1985', 60, 150, 52, L(1), 30)
    text('CONSUMER HOTLINE · CALLS A DAY (COMPANY HISTORY)', 60, 230, 20, L(1, .2), 30, col=GREY, font='mono600')
    bars([('BEFORE THE CHANGE', 400, '~400', L(1, .4), GREY), ('JUNE 1985', 1500, '~1,500', L(1, .9), RED)], 120, 800, 220, 340, .28)
    doc('doc_calls', 1000, 150, 860, L(1, .3), 30, hls=(L(1, .8), L(1, 1.0)))
    text('employees across the company confronted by people demanding an explanation', 1000, 480, 28, L(2), 30, font='outfit500', wrap=860)
    heading('a national news story', 1000, 570, 40, L(3), 30, col=RED)
    heading('a routine launch with mixed reviews', 1000, 640, 34, L(4), 30, col=GREY); strike(996, 660, 620, L(4, .6))
    heading("a public challenge to its understanding of its own brand", 1000, 710, 34, L(5), 30); wrap(860)
    text('what sales forecasts and taste tests struggled to quantify', 60, 870, 30, L(6), 30, col=GREY, font='outfit500')
    heading('customers felt a sense of ownership', 60, 930, 44, L(7), 30, col=RED); EV.append((T(L(7)), 'low'))

@scene(10, "pepsi's unexpected victory")
def s10():
    doc('doc_pepsi', 60, 150, 880, L(1, .3), 30, hls=(L(3, .2), L(3, .6)))
    heading('pepsi watched its rival', 1000, 150, 48, L(1), 30)
    text("it appeared to validate pepsi's argument: taste preferences were shifting", 1000, 240, 28, L(2), 30, font='outfit500', wrap=860)
    text('competitive theater: pepsi executives celebrating coca-cola\'s decision', 1000, 340, 26, L(3), 30, col=GREY, font='outfit500', wrap=860)
    heading('but pepsi had not forced consumers to reject new coke', 60, 520, 40, L(4), 30); wrap(1800)
    heading("the backlash came from coca-cola's own loyal audience", 60, 600, 40, L(5), 30, col=RED); wrap(1800); EV.append((T(L(5)), 'impact'))
    text('particularly damaging', 60, 680, 28, L(6), 30, col=GREY, font='outfit500')
    card_box(60, 760, 880, 170, L(7), 30, edge=GREY); text('THE FEAR', 94, 785, 20, L(7), 30, col=GREY, font='mono600'); heading('losing customers to a rival', 94, 830, 36, L(7, .2), 30, col=GREY)
    card_box(980, 760, 880, 170, L(8), 30); text('THE RESULT', 1014, 785, 20, L(8), 30, col=RED, font='mono600'); heading('angering customers already invested in the brand', 1014, 830, 36, L(8, .2), 30); wrap(820)
    EV.append((T(L(8)), 'low'))

@scene(11, 'the decision to reverse course')
def s11():
    photo('hq06', 1460, 150, 400, 533, 0, 30, PH_TAG.get('hq06', ''))
    heading('another difficult choice', 60, 150, 52, L(1), 30)
    card_box(60, 260, 640, 150, L(2), 30, edge=GREY); text('OPTION A', 94, 280, 20, L(2), 30, col=GREY, font='mono600'); heading('defend it and hope', 94, 320, 36, L(2, .2), 30, col=GREY)
    card_box(740, 260, 640, 150, L(3), 30); text('OPTION B', 774, 280, 20, L(3), 30, col=RED, font='mono600'); heading('admit it was a mistake', 774, 320, 36, L(3, .2), 30)
    text('publicly retreating from one of the most heavily researched product decisions in its history', 60, 450, 28, L(4), 30, font='outfit500', wrap=1340)
    text('evidence: the original formula retained powerful demand', 60, 540, 28, L(5), 30, col=GREY, font='outfit500')
    heading('leadership decided to bring it back', 60, 610, 48, L(6), 30, col=RED); EV.append((T(L(6)), 'impact'))
    text('the second decision · almost as famous as the first', 60, 690, 28, L(7), 30, col=GREY, font='outfit500')
    for k, (d_, s_) in enumerate([('APR 23', 'reformulation'), ('MAY', 'atlanta protest'), ('JUNE', '~1,500 calls a day'), ('JUL 11', 'original returns')]):
        t = L(7, k * .3); x = 60 + k * 450; rect(x, 780, 430, 3, RED if k == 3 else GREY, t, 30, grow=(t, t + .4, 'x')); sprite('dot_red' if k == 3 else 'dot_grey', x + 8, 781, t, 30)
        text(d_ + ' 1985', x, 800, 20, t, 30, col=RED if k == 3 else GREY, font='mono600'); text(s_, x, 832, 26, t, 30, font='outfit500')
    heading('restore the product it had removed', 60, 905, 44, L(8), 30); EV.append((T(L(8)), 'low'))
    text('dated public record only · no private boardroom dialogue reconstructed', 60, 975, 16, L(8, .3), 30, col=GREY, font='mono600')

@scene(12, 'july 11: the original returns')
def s12():
    text('JULY 11, 1985', 60, 150, 30, L(1), 30, col=RED, font='mono600')
    heading('the original returns as coca-cola classic', 60, 190, 52, L(1, .2), 30); wrap(880)
    money('APRIL 23 → JULY 11, 1985', '79 days', 60, 340, L(2), size=110)
    text('"led two network newscasts and made the front page of virtually every major newspaper" — company history', 60, 560, 24, L(3), 30, col=GREY, font='outfit500', wrap=880)
    heading('customers celebrated', 60, 660, 40, L(4), 30)
    doc('doc_back', 1000, 150, 860, L(5), 30, hls=(L(5, .3),))
    money('HOTLINE · TWO DAYS AFTER THE ANNOUNCEMENT', '31,600', 1000, 420, L(5, .3), size=84, sub='calls')
    doc('doc_keough', 1000, 600, 860, L(6), 30, hls=(L(6, .3), L(6, .6)))
    heading('the company had changed the formula', 60, 770, 40, L(7), 30); wrap(880)
    heading('its customers had forced it to reconsider', 60, 860, 40, L(8), 30, col=RED); wrap(880); EV.append((T(L(8)), 'low'))

# ═══════════════════════════ ACT 04 · THE AUTOPSY ═══════════════════════════
@scene(13, 'two cokes, one problem', 'act 04 · the autopsy')
def s13():
    photo('newcan', 60, 170, 220, 420, 0, 30, PH_TAG.get('newcan', ''), contain=True)
    photo('newbottle', 320, 262, 240, 330, L(2), 30, PH_TAG.get('newbottle', ''), contain=True)
    heading('new coke did not vanish overnight', 620, 150, 48, L(1), 30)
    doc('doc_two', 620, 240, 900, L(2), 30, hls=(L(2, .3), L(2, .7), L(4, .3)))
    text('"catch the wave" (new taste) · "red, white and you" (classic) — company history', 60, 640, 22, L(2, .5), 30, col=GREY, font='mono600')
    text('the original reclaimed its familiar position · the reformulation continued as an alternative', 60, 690, 26, L(3), 30, font='outfit500')
    for k, (d_, s_) in enumerate([('APR 1985', 'new taste launched'), ('JUL 1985', 'classic returns · both sold'), ('1990', 'renamed coke ii'), ('2002', 'abandoned (history.com)')]):
        t = L(4, k * .3); x = 60 + k * 450; rect(x, 770, 430, 3, RED if k == 1 else GREY, t, 30, grow=(t, t + .4, 'x')); sprite('dot_red' if k == 1 else 'dot_grey', x + 8, 771, t, 30)
        text(d_, x, 790, 20, t, 30, col=RED if k == 1 else GREY, font='mono600'); text(s_, x, 822, 26, t, 30, font='outfit500')
    heading('simply the cancellation of a failed launch', 60, 890, 34, L(5), 30, col=GREY); strike(56, 910, 720, L(5, .6))
    heading('it changed its product architecture to restore customer choice', 60, 950, 36, L(6), 30, col=RED); wrap(1800); EV.append((T(L(6)), 'impact'))
    text('a new taste, without forcing loyal consumers to surrender the old one', 1560, 260, 26, L(7), 30, font='outfit500', wrap=300); EV.append((T(L(7)), 'low'))

@scene(14, 'was it secretly a master plan?')
def s14():
    heading('later speculation: was new coke a publicity stunt?', 60, 150, 48, L(1), 30); wrap(1800)
    card_box(60, 260, 880, 170, L(1, .5), 30, edge=GREY); text('THEORY · RETROSPECTIVE SPECULATION', 94, 282, 20, L(1, .5), 30, col=GREY, font='mono600')
    heading('an elaborate publicity stunt', 94, 330, 40, L(1, .7), 30, col=GREY)
    heading('lacks convincing evidence', 60, 465, 36, L(2), 30, col=RED); EV.append((T(L(2)), 'impact'))
    text('EVIDENCE · COMPANY AND CONTEMPORARY RECORD', 1000, 262, 20, L(3), 30, col=RED, font='mono600')
    doc('doc_goiz95', 1000, 300, 860, L(3), 30, hls=(L(3, .6),))
    text('time, may 6, 1985: coke called it "the most significant soft-drink development in the company\'s history"', 1000, 600, 24, L(4), 30, font='outfit500', wrap=860)
    text('the return: enormous attention · renewed affection', 1000, 700, 28, L(5), 30, col=GREY, font='outfit500')
    doc('doc_smart', 60, 540, 880, L(6), 30, hls=(L(6, .2), L(6, .5), L(6, .8)))
    heading('an unintended recovery is not proof of a secret plan', 60, 900, 44, L(7), 30, col=RED); wrap(1800); EV.append((T(L(7)), 'low'))

@scene(15, 'what actually went wrong?')
def s15():
    heading('four failures in decision-making', 60, 150, 56, L(1), 30)
    for k, (h_, s_, ev, t) in enumerate([('01', 'focused on a measurable attribute: taste', 'time 1985: 190,000+ tested · 55% to 45%', L(2)),
                                        ('02', 'underestimated emotional attachment', 'keough, jul 11, 1985: research "could not measure or reveal"', L(3)),
                                        ('03', 'chose replacement over choice', 'time 1985: new coke would "totally supplant the old coke"', L(4)),
                                        ('04', 'assumed research = acceptance', 'company history: the tests didn\'t show "the bond"', L(5))]):
        x = 60 + k * 455; card_box(x, 260, 430, 330, t, 30)
        text(h_, x + 36, 290, 48, t, 30, col=RED, font='mono600'); heading(s_, x + 36, 370, 32, t, 30); wrap(360); text(ev, x + 36, 510, 18, t, 30, col=GREY, font='mono400'); wrap(370)
    text('yet: the value of correcting a decision quickly', 60, 660, 30, L(6), 30, font='outfit500')
    text('it listened to the backlash and restored what customers wanted', 60, 720, 30, L(7), 30, col=GREY, font='outfit500')
    heading('the original represented more than its ingredients', 60, 860, 48, L(8), 30, col=RED); wrap(1800); EV.append((T(L(8)), 'low'))

@scene(16, 'the verdict')
def s16():
    heading("coca-cola didn't fail because it ignored research", 960, 200, 52, L(1), L(5), al='CENTER')
    heading('it trusted one kind of research to answer a much larger question', 960, 300, 40, L(2), L(5), al='CENTER', col=RED); EV.append((T(L(2)), 'impact'))
    text('it knew which drink many preferred in a blind taste test', 960, 420, 32, L(3), L(5), col=GREY, font='outfit500', al='CENTER')
    text('it did not fully understand what replacing coca-cola would mean to the people who loved it', 960, 480, 32, L(4), L(5), font='outfit500', al='CENTER')
    CX.beat()
    text('THE VERDICT', 960, 180, 26, L(5), L(10), col=GREY, font='mono600', al='CENTER')
    heading('seventy-nine days later, the original returned', 960, 240, 48, L(5, .2), L(10), al='CENTER')
    text('the lesson extends far beyond soft drinks', 960, 340, 32, L(6), L(10), col=GREY, font='outfit500', al='CENTER')
    heading("customers don't always value a product only for what it does", 960, 420, 42, L(7), L(10), al='CENTER')
    heading('sometimes they value what it represents', 960, 520, 60, L(8), L(10), al='CENTER', col=RED); EV.append((T(L(8)), 'impact'))
    text('changing that without understanding the consequences can turn innovation into disaster', 960, 640, 32, L(9), L(10), font='outfit500', al='CENTER')
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
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(D, 'newcoke.blend')); bpy.ops.file.make_paths_relative(); bpy.ops.wm.save_mainfile()
print('BUILD OK', len(SCENES), 'scenes', len(EV), 'events', NAMES[0], 'strips')
