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
