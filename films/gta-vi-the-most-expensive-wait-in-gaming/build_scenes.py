# ── GTA VI scene designs. Authored on a 0–30 s grid per scene; L(k) is the grid time of narration line k, and
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

def boxes(items, x, y, w, h, gap, size=26):
    for k, (s_, t, edge) in enumerate(items):
        bx = x + k * (w + gap); card_box(bx, y, w, h, t, 30, edge=edge); text(s_, bx + 30, y + h / 2 - size * .7, size, t, 30, font='outfit500'); wrap(w - 60)

# ═══════════════════════════ ACT 01 · THE LONG WAIT ═══════════════════════════
@scene(1, 'thirteen years for one game', 'act 01 · the long wait')
def s01():
    heading('13 years', 60, 160, 150, L(1), 30, col=RED); EV.append((T(L(1)), 'impact'))
    text('since the last main grand theft auto release', 60, 340, 30, L(2), 30, font='outfit500'); wrap(1100)
    photo('rnorth23', 1240, 150, 620, 290, 0, 30, PH_TAG['rnorth23'])
    x0, x1 = 60, 1860; pos = lambda y: x0 + (y - 2013.71) / (2026.88 - 2013.71) * (x1 - x0)
    rect(x0, 600, x1 - x0, 3, GREY, L(3), 30, grow=(L(3), L(3, .8), 'x'))
    sprite('dot_grey', pos(2013.71), 601, L(3), 30); text('sep 2013 · gta v', x0, 620, 20, L(3), 30, col=GREY, font='mono600')
    sprite('dot_red', pos(2026.88), 601, L(3, .8), 30); text('nov 19, 2026 · gta vi (scheduled)', x1, 620, 20, L(3, .8), 30, col=RED, font='mono600', al='RIGHT')
    for k, (y_, lab, t) in enumerate([(2023.95, 'dec 2023 · trailer 1', L(7)), (2025.38, 'may 2025 · trailer 2', L(7, .3)), (2025.85, 'nov 2025 · new date', L(7, .6))]):
        ly = 546 - k * 38; sprite('dot_white', pos(y_), 601, t, 30); rect(pos(y_) - 1, ly + 22, 2, 594 - ly - 22, GREY, t, 30)
        text(lab, pos(y_) - 10, ly, 16, t, 30, col=TXT, font='mono600', al='RIGHT')
    text('following one of the most commercially successful entertainment products ever created', 60, 690, 28, L(4), 30, font='outfit500'); wrap(1800)
    text('enormous expectations · real financial stakes', 60, 745, 24, L(6), 30, col=GREY, font='mono600')
    heading('how did a company keep millions interested for thirteen years without releasing gta vi?', 60, 810, 40, L(9), 30, col=RED); wrap(1800); EV.append((T(L(9)), 'low'))
    text('and what happens when the waiting finally stops?', 60, 940, 28, L(11), 30, font='outfit500')

@scene(2, 'the money behind the hype')
def s02():
    card_box(60, 170, 860, 90, L(2), 30, edge=GREY); text('take-two interactive software, inc. · nasdaq: ttwo', 90, 198, 26, L(2), 30, font='outfit500')
    vline(490, 262, 318, L(2, .3), 30, L(2, .3), L(2, .6))
    card_box(60, 320, 860, 90, L(2, .6), 30); text('rockstar games · wholly-owned publishing label', 90, 348, 26, L(2, .6), 30, font='outfit500')
    photo('zelnick15', 60, 480, 300, 449, L(2, 1.0), 30, PH_TAG['zelnick15'])
    doc('doc_rev', 980, 170, 880, L(4), 30, hls=(L(4, .3), L(4, .7)))
    money('GTA PRODUCTS · SHARE OF NET REVENUE · FY2026', '12.4%', 980, 530, L(4, 1.0), size=110, sub='fiscal year ended mar 31, 2026')
    text('an established franchise — not gta vi sales', 980, 760, 20, L(5), 30, col=RED, font='mono600')
    text("the next release could change the company's financial performance dramatically", 420, 500, 28, L(6), 30, font='outfit500'); wrap(500)
    text('recognition is not the question', 420, 660, 26, L(7), 30, col=GREY, font='outfit500'); wrap(500)
    heading('can anticipation become another durable commercial success?', 420, 730, 32, L(8), 30, col=RED); wrap(500)

@scene(3, 'the game that refused to die')
def s03():
    text('SEPTEMBER 2013', 60, 150, 24, L(1), 30, col=RED, font='mono600')
    heading('grand theft auto v arrives', 60, 185, 44, L(1), 30)
    doc('doc_gta5', 60, 290, 900, L(2), 30, hls=(L(7), L(5, .5), L(3)))
    text("the game doesn't disappear from the market", 1000, 190, 30, L(5), 30, font='outfit500'); wrap(860)
    for k, s_ in enumerate(['generation 1 · ps3 / xbox 360', 'generation 2 · ps4 / xbox one', 'generation 3 · ps5 / xbox series x|s']):
        t = L(6, k * .4); sprite('dot_red', 1010, 290 + k * 60, t, 30); text(s_, 1040, 276 + k * 60, 24, t, 30, font='mono600')
    money('UNITS SOLD-IN TO DATE · MAY 2026', 'nearly 230M', 1000, 500, L(7), size=88, sub='sold-in = shipped into distribution, not bought by players')
    heading('a commercial lifespan that stretches across more than a decade', 60, 860, 40, L(9), 30, col=RED); wrap(1800); EV.append((T(L(9)), 'low'))

@scene(4, 'the second business inside gta')
def s04():
    doc('doc_online', 60, 170, 900, L(2), 30, hls=(L(2, .4), L(3)))
    flow(['new content', 'continued engagement', 'additional purchases'], 60, 560, 260, 100, 60, L(3, .5), dt=.4)
    note('illustrative', 60, 670, L(3, .5), w=300, size=15)
    doc('doc_strat', 1000, 170, 860, L(4), 30, hls=(L(4, .3), L(4, .7), L(4, 1.1)))
    heading('the economics of waiting change', 1000, 540, 36, L(5), 30)
    text('a successful game stays commercially relevant while its successor is developed', 1000, 600, 26, L(6), 30, col=GREY, font='outfit500'); wrap(860)
    heading('a franchise that generates business long after launch day', 60, 860, 40, L(8), 30, col=RED); wrap(1800); EV.append((T(L(8)), 'low'))

@scene(5, 'the decision not to rush')
def s05():
    text('most entertainment companies release new products regularly', 60, 170, 30, L(1), 30, font='outfit500'); wrap(1800)
    chips(['quality', 'longevity', 'internally developed titles'], 60, 260, L(3), dt=.4, size=30, gap=56)
    text('take-two: "a limited number of titles that are known for their quality and longevity"', 1000, 270, 24, L(3), 30, col=GREY, font='mono400'); wrap(860)
    check(60, 460, L(4)); text('enormous commercial value', 120, 470, 28, L(4), 30, font='outfit500')
    check(60, 520, L(4, .6), ok=False); text('expectations concentrated on fewer launches', 120, 530, 28, L(4, .6), 30, font='outfit500')
    rect(60, 700, 1800, 3, GREY, L(5), 30, grow=(L(5), L(5, .8), 'x'))
    sprite('dot_red', 68, 701, L(5), 30); text('2013 · gta v', 60, 720, 22, L(5), 30, col=TXT, font='mono600')
    sprite('dot_red', 1852, 701, L(5, .8), 30); text('2026 · gta vi', 1860, 720, 22, L(5, .8), 30, col=RED, font='mono600', al='RIGHT')
    text('no new numbered grand theft auto release', 960, 650, 22, L(6), 30, col=GREY, font='mono600', al='CENTER')
    rect(80, 760, 1760, 12, RULE, L(7), 30, grow=(L(7), L(7, .8), 'x')); text('gta v and gta online remain active', 960, 782, 20, L(7), 30, col=TXT, font='mono600', al='CENTER')
    heading('the cost of ambitious development — or a model where fewer releases sustain greater long-term value?', 60, 850, 38, L(9), 30, col=RED); wrap(1800); EV.append((T(L(9)), 'low'))

# ═══════════════════════════ ACT 02 · THE BUILD-UP ═══════════════════════════
@scene(6, 'the first trailer explodes', 'act 02 · the build-up')
def s06():
    text('DECEMBER 2023', 60, 150, 24, L(1), 30, col=RED, font='mono600')
    heading('the first gta vi trailer', 60, 185, 44, L(1), 30)
    doc('doc_trailer', 60, 290, 900, L(2), 30, hls=(L(3, .4), L(3)))
    money('FIRST 24 HOURS · YOUTUBE · PER TAKE-TWO', '93M+ views', 1000, 180, L(3), size=100, sub='record for a non-music video debut')
    text('powerful evidence of audience attention', 1000, 450, 30, L(6), 30, font='outfit500'); wrap(860)
    boxes([('trailer views = attention', L(4), GREY), ('paying customers = sales', L(5), RED)], 60, 640, 880, 110, 40, size=32)
    text('≠', 945, 668, 40, L(5), 30, col=RED, font='outfit700')
    heading('one announcement could still dominate the entertainment conversation', 60, 830, 40, L(7), 30, col=RED); wrap(1800); EV.append((T(L(7)), 'low'))

@scene(7, 'the date that moved')
def s07():
    heading('release timing', 60, 170, 44, L(1), 30)
    text('NOV 6, 2025 · NEW DATE ANNOUNCED', 1000, 180, 20, L(2), 30, col=RED, font='mono600')
    doc('doc_delay', 60, 260, 900, L(2), 30, hls=(L(2, .5), L(3), L(3, .6)))
    boxes([('more development time → supports quality', L(4), GREY), ('later commercial launch → revenue postponed', L(5), RED)], 60, 640, 880, 110, 40, size=28)
    doc('doc_timing', 1000, 230, 860, L(7), 30, hls=(L(7, .3), L(7, .6), L(8)))
    heading('for take-two, release timing matters financially', 60, 830, 40, L(6), 30, col=RED); wrap(1800); EV.append((T(L(6)), 'low'))

@scene(8, 'when expectations become the product')
def s08():
    photo('miami09', 60, 190, 860, 571, 0, 30, PH_TAG['miami09'])
    heading('it sells expectations', 980, 190, 44, L(2), 30)
    text('OFFICIAL REVEALS', 980, 270, 20, L(3), 30, col=RED, font='mono600')
    chips(['vice city', 'the state of leonida', 'jason and lucia'], 980, 305, L(3, .2), dt=.4, size=28, gap=50)
    doc('doc_extended', 980, 480, 880, L(4), 30, hls=(L(4, .4), L(4, .8)))
    check(980, 772, L(6), ok=False); text("a trailer can't prove how the complete game will perform", 1040, 782, 24, L(6), 30, font='outfit500'); wrap(820)
    text('the longer the wait, the more personal the expectations', 60, 820, 28, L(7), 30, col=GREY, font='outfit500'); wrap(860)
    heading('can the product withstand years of accumulated attention?', 60, 900, 40, L(9), 30, col=RED); wrap(1800); EV.append((T(L(9)), 'low'))

@scene(9, 'the price of the next generation')
def s09():
    text('JUNE 2026', 60, 150, 24, L(1), 30, col=RED, font='mono600')
    heading('the commercial model revealed', 60, 185, 44, L(1), 30)
    for k, (h_, v, t) in enumerate([('STANDARD EDITION · U.S.', '$79.99', L(2)), ('ULTIMATE EDITION · U.S.', '$99.99', L(3))]):
        x = 60 + k * 460; card_box(x, 290, 430, 250, t, 30, edge=RED if k else GREY)
        text(h_, x + 30, 315, 20, t, 30, col=GREY, font='mono600'); heading(v, x + 30, 380, 88, t + .1, 30, col=RED if k else TXT); EV.append((T(t + .1), 'impact'))
    text('PRE-ORDERS FROM JUNE 25, 2026', 60, 590, 24, L(4), 30, col=RED, font='mono600')
    heading('confirmed commercial decisions — not internet rumors', 60, 640, 32, L(5), 30); wrap(880)
    text('the game\'s price + the hardware to play it', 60, 740, 28, L(6), 30, col=GREY, font='outfit500'); wrap(880)
    doc('doc_price', 1000, 170, 860, L(1, .5), 30, hls=(L(4), L(6, .3), L(6, .6), L(2), L(3)))
    heading('a premium entertainment product with multiple purchase options', 60, 850, 40, L(7), 30, col=RED); wrap(1800); EV.append((T(L(7)), 'low'))

@scene(10, 'the console decision')
def s10():
    photo('ps520', 60, 190, 420, 506, 0, 30, 'ps5 · 2020 · osh33m · cc by-sa 4.0')
    photo('xbox25', 540, 190, 640, 360, L(1, .4), 30, 'xbox series x|s · 2025 · kyu3a · cc by-sa 4.0')
    heading('announced launch platforms', 1240, 190, 34, L(1), 30); wrap(620)
    chips(['playstation 5', 'xbox series x|s'], 1240, 250, L(1, .3), dt=.4, size=30, gap=54)
    text('that defined the initial market', 1240, 370, 26, L(2), 30, font='outfit500'); wrap(620)
    check(1240, 430, L(4), ok=False); text('no simultaneous pc release named in the launch materials', 1300, 440, 24, L(4), 30, font='outfit500'); wrap(560)
    text('customers needed compatible hardware', 540, 600, 28, L(3), 30, font='outfit500'); wrap(640)
    flow(['distribution', 'who can buy on day one', 'technical requirements', 'later opportunities'], 60, 760, 410, 100, 40, L(5), dt=.4)
    heading('a major release within a particular hardware ecosystem', 60, 920, 38, L(8), 30, col=RED); wrap(1800); EV.append((T(L(8)), 'low'))

# ═══════════════════════════ ACT 03 · THE BET ═══════════════════════════
@scene(11, 'the pre-order signal', 'act 03 · the bet')
def s11():
    text('SEPTEMBER 2026 QUARTERLY FILING', 60, 150, 24, L(1), 30, col=RED, font='mono600')
    doc('doc_preord', 60, 200, 900, L(1, .2), 30, hls=(L(1, .6), L(1, 1.0)))
    heading('pre-orders ≠ completed sales', 1000, 220, 44, L(2), 30, col=RED); wrap(860)
    check(1000, 320, L(3)); text('customers committed before release', 1060, 330, 28, L(3), 30, font='outfit500')
    for k, (h_, rows, t, edge) in enumerate([('KNOWN · NOV 18, 2026', ['pre-orders opened jun 25, 2026', 'demand outpaced historical benchmarks', 'launch date: nov 19, 2026'], L(4), GREY),
                                            ('NOT YET KNOWN', ['launch sales', 'profitability', 'long-term reception'], L(5), RED)]):
        x = 60 + k * 920; card_box(x, 500, 880, 290, t, 30, edge=edge); text(h_, x + 30, 520, 20, t, 30, col=RED if k else GREY, font='mono600')
        for j, r in enumerate(rows): text(r, x + 30, 568 + j * 64, 30, t + j * .2, 30, font='outfit500')
    text("pre-orders show confidence and interest — they can't guarantee satisfaction", 60, 830, 28, L(6), 30, font='outfit500'); wrap(1800)
    heading('converting early demand into sustained success', 60, 900, 40, L(9), 30, col=RED); wrap(1800); EV.append((T(L(9)), 'low'))

@scene(12, 'the billion-dollar question')
def s12():
    text('BUDGET FIGURES CIRCULATING ONLINE', 60, 150, 22, L(1), 30, col=GREY, font='mono600')
    heading('not verified', 60, 185, 52, L(2), 30, col=RED); EV.append((T(L(2)), 'impact'))
    text('no total production budget is established by the official materials examined', 500, 205, 26, L(3), 30, font='outfit500'); wrap(1360)
    for k, (h_, v, ev, t, edge) in enumerate([('DEVELOPMENT COST', 'not disclosed', 'no gta vi budget appears in the take-two filings examined; the 10-k says hit titles "require increasing budgets"', L(3, .5), GREY),
                                             ('FRANCHISE SALES', '$1 billion', 'gta v retail sales, faster than any entertainment release · nearly 230m units sold-in (take-two)', L(4), RED),
                                             ('PUBLISHER REVENUE', '12.4%', "gta products' share of take-two net revenue, fiscal 2026 (10-k)", L(5), RED)]):
        x = 60 + k * 610; card_box(x, 330, 580, 330, t, 30, edge=edge)
        text(h_, x + 36, 355, 20, t, 30, col=GREY, font='mono600'); heading(v, x + 36, 400, 64, t + .1, 30, col=TXT if k == 0 else RED)
        text(ev, x + 36, 520, 17, t + .3, 30, col=GREY, font='mono400'); wrap(510)
    text('revenue, a development cost and a forecast are not interchangeable numbers', 60, 720, 30, L(6), 30, font='outfit500'); wrap(1800)
    heading('the real story is extraordinary without inventing a budget', 60, 830, 40, L(8), 30, col=RED); wrap(1800); EV.append((T(L(8)), 'low'))

@scene(13, 'the risk no trailer can remove')
def s13():
    boxes([('opportunity: ambitious development · long product lifespans', L(1), GREY)], 1000, 170, 860, 110, 0, size=26)
    boxes([('risk: individual launches become disproportionately important', L(2), RED)], 1000, 300, 860, 110, 0, size=26)
    doc('doc_risk', 60, 170, 900, L(3), 30, hls=(L(3, .3), L(3, .6), L(3, 1.0)))
    text('WITH A STAKE IN THE OUTCOME', 1000, 450, 20, L(5), 30, col=RED, font='mono600')
    chips(['investors', 'distributors', 'the publisher itself'], 1000, 490, L(6), dt=.4, size=28, gap=50)
    text('before launch, no trailer or pre-order announcement can establish how customers will respond', 60, 680, 30, L(7), 30, font='outfit500'); wrap(1800)
    heading('that uncertainty is the central risk behind the entire strategy', 60, 800, 42, L(8), 30, col=RED); wrap(1800); EV.append((T(L(8)), 'low'))

@scene(14, 'the real test begins after launch')
def s14():
    heading('the larger opportunity may unfold over years', 60, 170, 40, L(2), 30); wrap(1800)
    text('ILLUSTRATIVE LIFECYCLE · NOT A FORECAST', 60, 260, 18, L(2), 30, col=GREY, font='mono600')
    bar(60, 420, 120, 120, RED, L(2, .3)); text('launch', 60, 435, 18, L(2, .3), 30, col=GREY, font='mono600')
    rect(190, 360, 1670, 60, RULE, L(2, .6), 30, grow=(L(2, .6), L(2, 1.4), 'x')); text('continued sales · updates · membership', 220, 375, 24, L(2, .8), 30, font='mono600')
    chips(['gta v: sold across three console generations', 'gta online: regular free updates', 'gta+ membership (since march 2022)'], 60, 490, L(3), dt=.4, size=26, gap=48)
    check(1000, 490, L(5), ok=False); text('a useful comparison — not a guarantee', 1060, 500, 26, L(5), 30, font='outfit500')
    heading('can rockstar build another durable entertainment ecosystem?', 1000, 560, 32, L(6), 30); wrap(860)
    flow(['first-week sales', 'engagement', 'continued demand', 'future content'], 60, 720, 410, 100, 40, L(7), dt=.4)
    heading('the long-term test: the commercial life of the franchise', 60, 880, 40, L(8), 30, col=RED); wrap(1800); EV.append((T(L(8)), 'low'))

# ═══════════════════════════ ACT 04 · THE AUTOPSY ═══════════════════════════
@scene(15, 'three decisions. one enormous bet.', 'act 04 · the autopsy')
def s15():
    heading('three strategic decisions', 60, 150, 44, L(1), 30)
    for k, (h_, s_, ev, t) in enumerate([('01 · selective releases', 'a limited number of ambitious, long-lasting products', '10-k: "a limited number of titles that are known for their quality and longevity"', L(2)),
                                        ('02 · long-term monetization', 'gta online extended the life of the existing franchise', 'take-two: regular free updates · gta+ membership since march 2022', L(3)),
                                        ('03 · quality versus timing', 'more waiting to reach its stated level of polish', 'rockstar, nov 2025: new date nov 19, 2026 · "the level of polish"', L(4))]):
        x = 60 + k * 610; card_box(x, 240, 580, 380, t, 30)
        text(h_, x + 36, 265, 18, t, 30, col=RED, font='mono600'); heading(s_, x + 36, 310, 30, t, 30); wrap(500)
        text(ev, x + 36, 520, 17, t + .3, 30, col=GREY, font='mono400'); wrap(510)
    text('each decision involved trade-offs', 60, 670, 30, L(5), 30, font='outfit500')
    for k, (s_, t) in enumerate([('fewer releases concentrate risk', L(6)), ('long-lasting products create opportunity', L(7)), ('delay protects quality, postpones revenue', L(8))]):
        x = 60 + k * 610; card_box(x, 730, 580, 90, t, 30, edge=GREY); text(s_, x + 30, 758, 24, t, 30, font='outfit500'); wrap(520)
    heading('gta vi brings all three decisions together', 60, 880, 42, L(9), 30, col=RED); EV.append((T(L(9)), 'low'))

@scene(16, 'the verdict')
def s16():
    heading("the remarkable thing isn't that people waited thirteen years", 960, 160, 44, L(1), L(6), al='CENTER')
    heading('rockstar built a franchise that stayed commercially relevant throughout', 960, 240, 36, L(2), L(6), al='CENTER', col=RED); wrap(1700); EV.append((T(L(2)), 'impact'))
    text('gta v: a long-term success   ·   gta online: the business beyond launch   ·   gta vi: enormous expectations', 960, 340, 22, L(3), L(6), col=GREY, font='mono600', al='CENTER')
    photo('rnorth23', 160, 440, 760, 460, L(1), L(6), PH_TAG['rnorth23'])
    photo('neon18', 1000, 440, 760, 460, L(4), L(6), PH_TAG['neon18'])
    CX.beat()
    text('THE VERDICT', 960, 180, 26, L(6), L(10), col=GREY, font='mono600', al='CENTER')
    text("the verdict isn't written yet", 960, 260, 34, L(6, .2), L(10), font='outfit500', al='CENTER')
    heading('anticipation is evidence of demand, not proof of future success', 960, 370, 54, L(7), L(10), al='CENTER', col=RED); wrap(1600); EV.append((T(L(7)), 'impact'))
    text('rockstar has shown how powerful a long-lasting entertainment franchise can become', 960, 560, 32, L(8), L(10), font='outfit500', al='CENTER')
    text('now it must prove the next chapter can justify the expectations', 960, 620, 32, L(9), L(10), col=GREY, font='outfit500', al='CENTER')
    CX.beat()
    d = heading('november 19, 2026', 960, 450, 90, L(10), L(10, 1.4), al='CENTER', col=RED); EV.append((T(L(10)), 'impact'))
    CX.beat()
    e = heading('brand coroner', 943, 420, 110, L(10, 1.4), 30, al='CENTER'); e2 = text('.', 1305, 420, 110, L(10, 2.0), 30, col=RED)
    f = text('EVERY BRAND LEAVES EVIDENCE.', 960, 570, 36, L(10, 1.7), 30, col=GREY, font='outfit500', al='CENTER')
    rect(810, 555, 300, 2, RED, L(10, 1.5), 30, grow=(L(10, 1.5), L(10, 2.2), 'x'))
    for st in (e, e2, f): fade(st, L(10, 1.4), 30, 1, .6, 2.0)
