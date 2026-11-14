# ── Target Canada scene designs. Authored on a 0–30 s grid per scene; L(k) is the grid time of narration line k, and
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

# ═══════════════════════════ ACT 01 · THE ARRIVAL ═══════════════════════════
@scene(1, '133 stores. gone.', 'act 01 · the arrival')
def s01():
    photo('oshawa13', 60, 190, 720, 480, 0, 30, PH_TAG['oshawa13'], z0=1.0, z1=1.06)
    text('MARCH 2013', 860, 150, 30, L(1), 30, col=RED, font='mono600')
    heading('target opens its first stores in canada', 860, 190, 52, L(1, .2), 30); wrap(1000)
    text('enormous ambitions · a recognizable brand · a plan to expand at extraordinary speed', 860, 330, 26, L(2), 30, col=GREY, font='outfit500'); wrap(1000)
    money('WITHIN NINE MONTHS', '124 stores', 860, 410, L(3), size=96, sub='opened in fiscal 2013 · target form 10-k')
    chips(['empty shelves', 'disappointing prices', 'missing products'], 1420, 430, L(4), dt=.5, size=30, gap=56)
    for k, (d_, s_, t) in enumerate([('MAR 2013', 'first stores open', L(5)), ('JAN 15, 2015', 'every canadian store to close · 133 stores', L(5, .6))]):
        x = 60 + k * 620; rect(x, 760, 600, 3, RED if k else GREY, t, 30, grow=(t, t + .4, 'x')); sprite('dot_red' if k else 'dot_grey', x + 8, 761, t, 30)
        text(d_, x, 785, 22, t, 30, col=RED if k else GREY, font='mono600'); text(s_, x, 820, 28, t, 30, font='outfit500'); wrap(580)
    heading('less than two years', 1320, 700, 44, L(5, 1.0), 30, col=RED); EV.append((T(L(5, 1.0)), 'impact'))
    text('the exit: US$5.1 billion in pretax charges (form 10-k, fiscal 2014)', 1320, 770, 22, L(6), 30, col=GREY, font='mono600'); wrap(560)
    heading("how did one of america's most successful retailers misjudge its expansion so badly?", 60, 920, 40, L(7), 30, col=RED); wrap(1800); EV.append((T(L(7)), 'low'))

@scene(2, 'the american success story')
def s02():
    photo('fred12', 60, 190, 820, 543, 0, 30, PH_TAG['fred12'], z0=1.0, z1=1.05)
    text('IN THE UNITED STATES', 960, 150, 26, L(1), 30, col=RED, font='mono600')
    rect(960, 270, 860, 3, GREY, L(1), 30, grow=(L(1), L(1, .6), 'x'))
    for x_, lab, c in ((960, 'traditional discount retail', GREY), (1820, 'fashionable department stores', GREY)):
        sprite('dot_grey', x_, 271, L(1, .3), 30); text(lab, x_, 290, 20, L(1, .3), 30, col=c, font='mono600', al='LEFT' if x_ < 1500 else 'RIGHT')
    sprite('dot_red', 1390, 271, L(1, .7), 30); heading('target', 1390, 205, 40, L(1, .7), 30, col=RED, al='CENTER')
    chips(['accessible prices', 'appealing design', 'recognizable private labels', 'a convenient shopping experience'], 960, 360, L(2), dt=.4, size=30, gap=54)
    text('the red bullseye: one of america\'s most familiar retail symbols', 960, 600, 28, L(3), 30, font='outfit500'); wrap(860)
    heading('canadian shoppers knew the brand too', 60, 790, 44, L(4), 30)
    note('many had shopped at u.s. target stores across the border · "90 per cent of canadians live within an hour\'s drive of the u.s. border" (retail council of canada, via the associated press, apr 2014)', 60, 850, L(5), w=1100)
    text('an opportunity?', 1300, 790, 40, L(6), 30, col=GREY, font='outfit500')
    heading("not an unknown retailer — an established experience", 60, 930, 38, L(7), 30); wrap(1800)
    heading('for customers who already had expectations', 1220, 930, 38, L(8), 30, col=RED); wrap(640); EV.append((T(L(8)), 'low'))

@scene(3, 'the big canadian bet')
def s03():
    photo('milton12', 60, 190, 620, 465, 0, 30, PH_TAG['milton12'])
    s_, hh = doc('doc_zellers', 740, 150, 1120, L(1), 30, hls=(L(1, .6), L(1, 1.2)))
    text('JAN 13, 2011', 740, 120, 22, L(1), 30, col=RED, font='mono600')
    photo('zint07', 60, 720, 300, 225, L(2), 30, PH_TAG['zint07'])
    rect(740, 640, 520, 140, PANEL, L(3), 30); text('A GRADUAL ENTRY', 770, 660, 20, L(3), 30, col=GREY, font='mono600'); text('a few stores → prove → expand', 770, 700, 30, L(3), 30, col=GREY, font='outfit500')
    card_box(1300, 640, 560, 140, L(3, .5), 30); text('TARGET\'S ENTRY', 1330, 660, 20, L(3, .5), 30, col=RED, font='mono600'); text('up to 220 sites at once · nationwide', 1330, 700, 30, L(3, .5), 30, font='outfit500')
    text('acquiring locations was only the beginning. each site needed:', 420, 820, 26, L(4), 30, col=GREY, font='outfit500')
    for k, w_ in enumerate(['conversion', 'merchandise', 'staff', 'distribution', 'technology']):
        t = L(5, k * .35); x = 420 + k * 290; rect(x, 870, 270, 56, PANEL, t, 30); rect(x, 870, 5, 56, RED, t, 30); text(w_, x + 22, 882, 28, t, 30, font='outfit500'); EV.append((T(t), 'mark'))
    heading('enormous opportunity · an equally enormous execution challenge', 420, 960, 34, L(6), 30, col=RED); wrap(1480); EV.append((T(L(6)), 'low'))

@scene(4, 'the speed trap')
def s04():
    for k, (d_, s_, t) in enumerate([('EARLY MAR 2013', '3 test stores', L(1)), ('MAR 2013', '+21 · official launch', L(1, .5)), ('END Q2 2013', '68 stores', L(2)), ('FEB 1, 2014', '124 stores', L(2, .5))]):
        x = 60 + k * 450; rect(x, 200, 430, 3, RED if k == 3 else GREY, t, 30, grow=(t, t + .4, 'x')); sprite('dot_red' if k == 3 else 'dot_grey', x + 8, 201, t, 30)
        text(d_, x, 222, 22, t, 30, col=RED if k == 3 else GREY, font='mono600'); heading(s_, x, 256, 36 if k < 3 else 44, t, 30, col=RED if k == 3 else TXT)
    note('sources: canadian business (2016) · cbc news, aug 2013 · target form 10-k, fiscal 2013 (year ended feb 1, 2014)', 60, 330, L(2), w=1700)
    text('CANADIAN STORES BY PROVINCE, FEB 1, 2014 (FORM 10-K)', 60, 395, 20, L(3), 30, col=GREY, font='mono600')
    prov = [('ON', 50), ('QC', 25), ('BC', 18), ('AB', 14), ('MB', 4), ('NS', 4), ('NB', 3), ('SK', 3), ('NL', 2), ('PE', 1)]
    for k, (p_, v) in enumerate(prov):
        t = L(3, k * .12); y = 440 + k * 30; text(p_, 60, y, 20, t, 30, col=GREY, font='mono600'); rect(110, y + 4, v * 10, 18, RED, t, 30, grow=(t, t + .4, 'x')); text(str(v), 120 + v * 10, y, 20, t, 30, font='mono600')
    photo('delta13', 760, 440, 360, 270, L(3), 30, PH_TAG['delta13'])
    chips(['working inventory systems', 'reliable suppliers', 'trained employees', 'daily replenishment'], 1200, 460, L(4), dt=.4, size=28, gap=52)
    text('the schedule left little room to fix problems before they spread', 1200, 680, 26, L(5), 30, col=GREY, font='outfit500'); wrap(660)
    schematic('grid1', 120, 820, 34, L(6), 30); text('one pilot store: contained', 60, 870, 26, L(6), 30, font='outfit500')
    schematic('grid124', 760, 770, 400, L(7), 30); heading('124 stores: a national crisis', 1200, 830, 40, L(7, .3), 30, col=RED); wrap(660); EV.append((T(L(7, .3)), 'impact'))
    note('editorial illustration', 760, 1000, L(7), w=400)

# ═══════════════════════════ ACT 02 · THE BREAKDOWN ═══════════════════════════
@scene(5, 'the empty shelf mystery', 'act 02 · the breakdown')
def s05():
    heading('a strange contradiction', 60, 150, 52, L(1), 30)
    photo('bramp16', 60, 260, 450, 600, L(2), 30, PH_TAG['bramp16'])
    note('first evening of trading · sign on an empty fixture: "we\'re in the process of stocking up so you can too."', 60, 880, L(2, .4), w=450)
    text('IN STORES', 580, 260, 22, L(2), 30, col=GREY, font='mono600'); bar(600, 640, 160, 40, GREY, L(2, .3)); text('missing products', 580, 660, 24, L(2), 30, font='outfit500')
    text('IN DIST. CENTRES', 820, 260, 22, L(3), 30, col=RED, font='mono600'); bar(840, 640, 160, 330, RED, L(3, .3)); text('excess inventory', 820, 660, 24, L(3), 30, font='outfit500')
    note('editorial illustration · not to scale', 580, 700, L(3), w=500)
    doc('doc_dc', 1100, 260, 760, L(3, .6), 30, hls=(L(3, 1.2), L(4)))
    text('the merchandise existed — it was not reaching the right shelves in the right quantities', 1100, 600, 26, L(4), 30, font='outfit500'); wrap(760)
    text('more serious than a temporary shortage', 1100, 690, 28, L(5), 30, col=GREY, font='outfit500'); wrap(760)
    flow(['purchasing', 'inventory', 'warehouses', 'stores'], 580, 790, 300, 70, 30, L(6), dt=.4)
    for k in range(3): text('✕', 580 + (k + 1) * 330 - 26, 800, 30, L(6, 1.6 + k * .2), 30, col=RED); EV.append((T(L(6, 1.6 + k * .2)), 'mark'))
    heading('they arrived expecting target — and left without what they wanted', 580, 920, 38, L(8), 30, col=RED); wrap(1300); EV.append((T(L(8)), 'low'))
    text('for customers, the result was simple', 580, 880, 22, L(7), 30, col=GREY, font='mono600')

@scene(6, 'the data problem')
def s06():
    heading('the problems began behind the scenes', 60, 150, 52, L(1), 30)
    text('new systems were being implemented while a massive launch was prepared', 60, 225, 28, L(2), 30, col=GREY, font='outfit500'); wrap(1000)
    card_box(60, 300, 640, 470, L(3), 30, edge=GREY); text('A PRODUCT RECORD · FIELDS NAMED BY CANADIAN BUSINESS', 90, 320, 16, L(3), 30, col=GREY, font='mono600')
    for k, f_ in enumerate(['manufacturer', 'model', 'upc', 'dimensions', 'weight', 'case pack']):
        t = L(3, .2 + k * .2); y = 370 + k * 58; text(f_, 90, y, 26, t, 30, font='mono400'); rect(400, y + 6, 270, 26, '#1d1d1d', t, 30)
        if f_ in ('dimensions', 'case pack'): rect(400, y + 6, 270, 26, RED, L(4, .3), 30, a=.35, grow=(L(4, .3), L(4, .9), 'x'))
    note('illustrative record · no real values shown', 90, 730, L(3), w=600)
    doc('doc_data', 900, 290, 960, L(4), 30, hls=(L(4, .4), L(4, 1.0), L(5)))
    money('DATA ACCURACY, AS REPORTED', '~30%', 760, 725, L(5, .6), size=72, sub='canada, per an internal team\'s estimate · u.s.: 98–99%')
    text('a warehouse may hold what a store needs — and the system fails to send it', 1300, 760, 26, L(6), 30, font='outfit500'); wrap(560)
    heading('the stores were built faster than the information that had to run them', 60, 930, 38, L(7), 30, col=RED); wrap(1800); EV.append((T(L(7)), 'low'))

@scene(7, "when systems don't communicate")
def s07():
    heading('beyond the product records', 60, 150, 52, L(1), 30)
    for k, (nm_, role) in enumerate([('SAP', 'merchandising & inventory'), ('MANHATTAN', 'warehouse software'), ('RETALIX POS', 'checkout')]):
        t = L(2, k * .4); x = 60 + k * 330; card_box(x, 250, 300, 120, t, 30, edge=GREY); text(nm_, x + 26, 272, 26, t, 30, font='mono600'); text(role, x + 26, 318, 22, t, 30, col=GREY, font='outfit500')
        if k: rect(x - 40, 308, 40, 4, RED, L(2, 1.4), 30); text('✕', x - 31, 290, 26, L(2, 1.4), 30, col=RED)
    note('systems named in canadian business (2016)', 60, 385, L(2), w=1100)
    doc('doc_sync', 1040, 150, 820, L(2, .8), 30, hls=(L(2, 1.2), L(6), L(2, 1.6)))
    card_box(60, 450, 940, 150, L(3), 30, edge=GREY); text('ILLUSTRATIVE EXAMPLE · NOT A DOCUMENTED CASE', 90, 468, 18, L(3), 30, col=GREY, font='mono600')
    text('sold at the checkout: one variation of a product', 90, 505, 26, L(3, .2), 30, font='outfit500'); text('sent by replenishment: another', 90, 548, 26, L(3, .8), 30, col=RED, font='outfit500')
    text('distribution centres accumulated stock that could not be moved efficiently', 60, 650, 28, L(4), 30, font='outfit500'); wrap(1700)
    text('an expensive contradiction', 60, 720, 28, L(5), 30, col=GREY, font='outfit500')
    rect(60, 780, 520, 90, PANEL, L(6), 30); text('STORE SHELVES', 84, 794, 18, L(6), 30, col=GREY, font='mono600'); heading('empty', 84, 820, 34, L(6), 30)
    card_box(620, 780, 540, 90, L(6, .5), 30); text('SUPPLY CHAIN', 644, 794, 18, L(6, .5), 30, col=RED, font='mono600'); heading('overloaded', 644, 820, 34, L(6, .5), 30, col=RED)
    text('not simply a shortage of inventory', 1220, 790, 26, L(7), 30, col=GREY, font='outfit500')
    chips(['what existed', 'where it belonged', 'when it needed to move'], 1220, 850, L(8), dt=.4, size=30, gap=50); EV.append((T(L(8)), 'low'))

@scene(8, 'the price disappointment')
def s08():
    heading('a perception gap', 60, 150, 52, L(1), 30)
    text('expected: attractive prices and distinctive merchandise', 60, 222, 28, L(2), 30, font='outfit500'); wrap(1400)
    photo('bramp22', 60, 300, 560, 404, L(1), 30, PH_TAG['bramp22'])
    doc('doc_reuters', 720, 280, 820, L(3), 30, hls=(L(3, .4),))
    doc('doc_price', 720, 540, 820, L(4), 30, hls=(L(4, .4), L(5)))
    chips(['cross-border price differences', 'different suppliers', 'transportation costs', 'local market conditions'], 60, 760, L(4, .3), dt=.35, size=26, gap=44)
    note('no price tags shown: these sources publish no matched, dated item comparison we could verify', 60, 950, L(5), w=620)
    for k, w_ in enumerate(['low prices', 'products in stock']):
        t = L(6, k * .4); x = 1580; y = 680 + k * 100; rect(x, y, 280, 70, PANEL, t, 30); text(w_, x + 20, y + 16, 28, t, 30, font='outfit500'); strike(x + 12, y + 33, 256, t + .3)
    text('TWO REASONS TO CHOOSE TARGET OVER ESTABLISHED CANADIAN COMPETITORS', 1580, 560, 18, L(6), 30, col=RED, font='mono600'); wrap(280); EV.append((T(L(6)), 'low'))

@scene(9, 'the customer trust problem')
def s09():
    heading('first impressions are hard to undo', 60, 150, 52, L(1), 30)
    text('target needed its stores to become part of canadians\' routines', 60, 225, 28, L(2), 30, col=GREY, font='outfit500'); wrap(900)
    flow(['a first visit', 'the item is missing', 'back to a familiar competitor'], 60, 310, 270, 90, 40, L(3), dt=.7)
    text('repeated disappointments make the habit stick', 60, 430, 26, L(5), 30, col=RED, font='outfit500')
    note('editorial diagram', 60, 470, L(3), w=400)
    text('"VERY SATISFIED" WITH THEIR SHOPPING EXPERIENCE · FORUM RESEARCH, AUG 2013', 60, 540, 18, L(6), 30, col=GREY, font='mono600')
    rows = [('costco', 62), ('wal-mart', 40), ("hudson's bay", 40), ("marshall's", 35), ('winners', 35), ('sears', 34), ('holt renfrew', 32), ('target', 27)]
    for k, (n_, v) in enumerate(rows):
        t = L(6, k * .1); y = 580 + k * 42; c = RED if n_ == 'target' else GREY
        text(n_, 60, y, 22, t, 30, col=c if n_ == 'target' else TXT, font='mono600'); rect(260, y + 4, v * 9, 24, c, t, 30, grow=(t, t + .4, 'x')); text(f'{v}%', 272 + v * 9, y, 22, t, 30, col=c, font='mono600')
    doc('doc_forum', 1080, 300, 780, L(6, .5), 30, hls=(L(6, 1.0), L(6, 1.6)))
    money('TARGET · AUG 2013', '27%', 1080, 640, L(6, 1.2), size=120, sub='last of eight retailers surveyed (cbc news, aug 19, 2013)')
    heading('national awareness — without the experience that awareness promised', 1080, 900, 34, L(7), 30, col=RED); wrap(780); EV.append((T(L(7)), 'low'))

# ═══════════════════════════ ACT 03 · THE RECKONING ═══════════════════════════
@scene(10, 'the losses accumulate', 'act 03 · the reckoning')
def s10():
    heading('the financial consequences appeared quickly', 60, 150, 52, L(1), 30)
    text('CANADIAN SEGMENT EBIT, US$ MILLIONS · FORM 10-K, FISCAL 2013', 60, 250, 20, L(2), 30, col=GREY, font='mono600')
    bars([('2011', 122, '−122', L(2, .2), GREY), ('2012', 369, '−369', L(2, .5), GREY), ('2013', 941, '−941', L(2, .8), RED)], 100, 800, 140, 210, .45, lab_size=40)
    text('pre-opening', 100, 860, 18, L(2, .5), 30, col=GREY, font='mono400'); text('first year of stores', 520, 860, 18, L(2, .8), 30, col=RED, font='mono400')
    money('FISCAL 2013 · FIRST YEAR OF STORES', '−US$941 million', 780, 300, L(3), size=84, sub='segment ebit on sales of us$1,317 million (form 10-k)')
    note('contemporary reports put the year\'s loss near us$1 billion · recast in the fiscal 2014 10-k as a pretax loss of us$1,018 million · the 2011–12 pre-opening years add us$491 million', 784, 490, L(3, .5), w=1060)
    chips(['opening stores', 'operating distribution centres', 'carrying inventory', 'fixing systems'], 780, 590, L(4), dt=.35, size=28, gap=50)
    text('…without the sales to support the investment', 780, 800, 26, L(5), 30, col=GREY, font='outfit500')
    for k, (h_, t) in enumerate([('repair the customer experience', L(6, .3)), ('reduce the financial burden of the network', L(7))]):
        x = 780 + k * 540; card_box(x, 880, 510, 110, t, 30); text(f'0{k + 1}', x + 24, 898, 26, t, 30, col=RED, font='mono600'); text(h_, x + 80, 898, 28, t, 30, font='outfit500'); wrap(410)
    text('TWO SIMULTANEOUS CHALLENGES', 780, 848, 18, L(6), 30, col=RED, font='mono600'); EV.append((T(L(7)), 'low'))

@scene(11, 'leadership under pressure')
def s11():
    heading('a turbulent period for the whole company', 60, 150, 52, L(1), 30)
    for k, (d_, s_, t) in enumerate([('Q4 2013', 'u.s. data breach (form 10-k)', L(2)), ('MAY 2014', 'ceo gregg steinhafel steps down', L(3)), ('MAY 2014', 'target canada\'s president leaves; mark schindele takes over', L(3, .6)), ('AUG 2014', 'brian cornell becomes chairman and ceo', L(4))]):
        x = 60 + k * 450; rect(x, 250, 430, 3, RED if k == 3 else GREY, t, 30, grow=(t, t + .4, 'x')); sprite('dot_red' if k == 3 else 'dot_grey', x + 8, 251, t, 30)
        text(d_, x, 272, 22, t, 30, col=RED if k == 3 else GREY, font='mono600'); text(s_, x, 306, 26, t, 30, font='outfit500'); wrap(410)
    doc('doc_breach', 60, 420, 820, L(3), 30, hls=(L(3, .4), L(3, 1.0)))
    note('no photograph of gregg steinhafel is shown: none with a licence we could verify', 60, 760, L(3), w=820)
    photo('cornell24', 960, 420, 300, 400, L(4), 30, PH_TAG['cornell24'])
    doc('doc_cornell', 1300, 420, 560, L(4, .4), 30, hls=(L(4, .8),))
    text('his task: could the canadian operation realistically be repaired?', 1300, 660, 28, L(5), 30, font='outfit500'); wrap(560)
    text('not "was entering canada a good idea?"', 60, 870, 30, L(6), 30, col=GREY, font='outfit500')
    heading('but "does continuing to fund it make economic sense?"', 60, 930, 40, L(7), 30, col=RED); wrap(1800); EV.append((T(L(7)), 'low'))

@scene(12, "the turnaround that wasn't enough")
def s12():
    heading('the fix-up year', 60, 150, 52, L(1), 30)
    chips(['inventory availability', 'operations', 'the shopping experience'], 60, 240, L(1, .4), dt=.4, size=28, gap=50)
    note('"by the latter half of 2014, target could finally have some confidence that the right products would arrive at the right times" · canadian business (2016)', 60, 410, L(1, 1.0), w=820)
    doc('doc_holiday', 960, 150, 900, L(2), 30, hls=(L(3),))
    text('JANUARY 15, 2015', 60, 520, 24, L(4), 30, col=RED, font='mono600')
    doc('doc_quote', 60, 560, 900, L(4, .2), 30, hls=(L(4, .6), L(4, 1.2)))
    rect(1000, 560, 860, 3, GREY, L(5), 30, grow=(L(5), L(5, .5), 'x')); rect(1000, 548, 4, 28, TXT, L(5), 30); rect(1856, 548, 4, 28, RED, L(5, .5), 30)
    text('2015', 1000, 590, 24, L(5), 30, font='mono600'); text('2021 at the earliest', 1860, 590, 24, L(5, .5), 30, col=RED, font='mono600', al='RIGHT')
    text('the company\'s own assessment: years of further losses before any profit', 1000, 640, 26, L(5, .6), 30, col=GREY, font='outfit500'); wrap(860)
    text('continuing meant committing more capital', 1000, 730, 28, L(6), 30, font='outfit500')
    for k, (h_, c) in enumerate([('finance a long recovery', GREY), ('accept an expensive exit', RED)]):
        x = 1000 + k * 440; t = L(7, k * .5); card_box(x, 800, 420, 110, t, 30, edge=c); text(h_, x + 26, 834, 30, t, 30, col=TXT if k == 0 else RED, font='outfit500'); wrap(370)
    EV.append((T(L(7)), 'low'))

@scene(13, 'the shutdown decision')
def s13():
    text('JANUARY 15, 2015', 60, 150, 30, L(1), 30, col=RED, font='mono600')
    heading('target will discontinue its canadian operations', 60, 190, 52, L(1, .2), 30); wrap(1100)
    doc('doc_ccaa', 60, 330, 900, L(2), 30, hls=(L(2, .4), L(3), L(3, .5)))
    for k, (v, lab, t) in enumerate([('133', 'stores', L(3)), ('~17,600', 'employees', L(3, .5)), ('C$70M', 'proposed employee trust', L(4))]):
        x = 1020 + k * 290; heading(v, x, 330, 64, t, 30, col=RED); text(lab, x, 420, 22, t, 30, col=GREY, font='mono600'); wrap(270); EV.append((T(t), 'impact'))
    doc('doc_trust', 1020, 500, 840, L(4, .3), 30, hls=(L(4, .7), L(4, 1.2)))
    photo('pointe15', 60, 720, 420, 214, L(5), 30, PH_TAG['pointe15'])
    chips(['workers', 'suppliers', 'landlords', 'communities'], 560, 760, L(5), dt=.3, size=28, gap=46)
    rect(1100, 820, 760, 3, GREY, L(6), 30, grow=(L(6), L(6, .6), 'x')); text('MAR 2013', 1100, 840, 20, L(6), 30, col=GREY, font='mono600'); text('JAN 2015', 1860, 840, 20, L(6, .6), 30, col=RED, font='mono600', al='RIGHT')
    heading('less than two years', 1100, 880, 44, L(6, .6), 30, col=RED); EV.append((T(L(6, .6)), 'low'))

# ═══════════════════════════ ACT 04 · THE AUTOPSY ═══════════════════════════
@scene(14, 'the $5.1 billion exit', 'act 04 · the autopsy')
def s14():
    doc('doc_k14', 60, 150, 1000, L(1), 30, hls=(L(1, .5), L(1, 1.1)))
    text('FOURTH-QUARTER 2014 PRETAX EXIT COSTS, US$ MILLIONS · FORM 10-K', 1120, 150, 18, L(2), 30, col=GREY, font='mono600'); wrap(740)
    rows = [('impairment on deconsolidation', 4766, '', RED), ('contingent liabilities', 240, '', GREY), ('employee trust', 73, '', GREY), ('other exit costs', 26, '', GREY)]
    for k, (n_, v, s_, c) in enumerate(rows):
        t = L(2, k * .25); y = 210 + k * 76; text(n_, 1120, y, 22, t, 30, font='outfit500'); rect(1120, y + 34, max(v * .14, 4), 22, c, t, 30, grow=(t, t + .5, 'x')); text(f'{v:,}' + (f' · {s_}' if s_ else ''), 1860, y, 22, t, 30, col=c, font='mono600', al='RIGHT')
    text('total 5,105 · the largest item is a non-cash write-down of target\'s investment', 1120, 520, 22, L(2, 1.0), 30, col=RED, font='mono600'); wrap(740)
    heading('not a single cash expenditure', 60, 555, 40, L(3), 30); wrap(1000)
    note('expected cash cost of the exit: us$500–600 million (target release, jan 15, 2015) · liquidation and lease obligations followed', 60, 612, L(4), w=1000)
    photo('bayshore15', 60, 700, 420, 236, L(5), 30, PH_TAG['bayshore15'])
    doc('doc_closed', 540, 700, 760, L(5, .4), 30, hls=(L(5, .8),))
    text('the accounting tells only part of the story', 1360, 690, 28, L(6), 30, col=GREY, font='outfit500'); wrap(500)
    heading('also lost: the chance of a durable position in canada', 1360, 790, 36, L(7), 30, col=RED); wrap(500); EV.append((T(L(7)), 'low'))

@scene(15, 'what actually broke target canada?')
def s15():
    heading('four interconnected decisions', 60, 150, 52, L(1), 30)
    for k, (h_, s_, ev, t) in enumerate([('01', 'expanded before proving the operating model', '124 stores in fiscal 2013 (10-k)', L(2)),
                                        ('02', 'relied on systems that were not dependable', 'data ~30% accurate, per an internal estimate (canadian business)', L(3)),
                                        ('03', 'underestimated the expectations gap', '27% "very satisfied", aug 2013 (forum research)', L(4)),
                                        ('04', 'a rollout so large that fixing it was costly', 'us$5.1 billion in exit charges (10-k, fiscal 2014)', L(5))]):
        x = 60 + k * 455; card_box(x, 250, 430, 330, t, 30)
        text(h_, x + 36, 280, 48, t, 30, col=RED, font='mono600'); heading(s_, x + 36, 360, 30, t, 30); wrap(360); text(ev, x + 36, 500, 18, t, 30, col=GREY, font='mono400'); wrap(370)
    text('the problems reinforced one another', 60, 640, 30, L(6), 30, font='outfit500')
    for k, (a_, t) in enumerate([('poor availability', L(7)), ('weak demand', L(7, .6)), ('mounting losses', L(8)), ('less time to fix operations', L(9))]):
        x = 60 + k * 460; card_box(x, 720, 400, 90, t, 30, edge=RED if k == 3 else GREY); text(a_, x + 24, 748, 28, t, 30, font='outfit500'); wrap(360)
        if k: hline(x - 52, x - 10, 765, t, 30, t, t + .3)
    vline(1720, 820, 880, L(9, .5), 30, L(9, .5), L(9, .8), head=False); hline(1720, 260, 880, L(9, .8), 30, L(9, .8), L(9, 1.3), head=False); vline(260, 880, 822, L(9, 1.3), 30, L(9, 1.3), L(9, 1.5))
    text('…and poorer availability again', 300, 900, 22, L(9, 1.3), 30, col=RED, font='mono600'); EV.append((T(L(9)), 'low'))

@scene(16, 'the verdict')
def s16():
    heading("target didn't fail because canadians had never heard of it", 960, 200, 50, L(1), L(5), al='CENTER')
    heading('it failed to deliver the experience that made the brand attractive', 960, 300, 40, L(2), L(5), al='CENTER', col=RED); EV.append((T(L(2)), 'impact'))
    text('national scale came before the operation was ready', 960, 420, 32, L(3), L(5), col=GREY, font='outfit500', al='CENTER')
    text('by the time the problems were visible, it was carrying the costs of more than a hundred stores', 960, 480, 32, L(4), L(5), font='outfit500', al='CENTER')
    CX.beat()
    text('THE VERDICT', 960, 180, 26, L(5), L(8), col=GREY, font='mono600', al='CENTER')
    text('the lesson is not that international expansion is inherently dangerous', 960, 260, 34, L(5, .2), L(8), font='outfit500', al='CENTER')
    heading('brand recognition cannot replace operational readiness', 960, 380, 58, L(6), L(8), al='CENTER', col=RED); EV.append((T(L(6)), 'impact'))
    text('a successful formula does not automatically survive a new market', 960, 520, 34, L(7), L(8), font='outfit500', al='CENTER')
    CX.beat()
    e = heading('brand coroner', 943, 420, 110, L(8), 30, al='CENTER'); e2 = text('.', 1305, 420, 110, L(8, .8), 30, col=RED)
    f = text('EVERY BRAND LEAVES EVIDENCE.', 960, 570, 36, L(8, .4), 30, col=GREY, font='outfit500', al='CENTER')
    rect(810, 555, 300, 2, RED, L(8, .2), 30, grow=(L(8, .2), L(8, 1.0), 'x'))
    for st in (e, e2, f): fade(st, L(8), 30, 1, .6, 2.0)
