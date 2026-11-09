# ── WHSmith scene designs. Authored on a 0–30 s grid per scene; L(k) is the grid time of narration line k, and
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
def letters(word, keep, x, y, size, t, t1=30, strike_t=None):
    """the name as plain letters in the film's own type (not a logo): kept part white, dropped part grey with a strike"""
    heading(word[:keep], x, y, size, t, t1)
    w0 = size * {3: 2.301}.get(keep, .62 * keep) + size * .02
    if keep < len(word):
        heading(word[keep:], x + w0, y, size, t, t1, col=GREY)
        if strike_t is not None: strike(x + w0 - 6, y + size * .52, size * 2.105 + 12, strike_t, t1)

# ═══════════════════════════ ACT 01 · THE TRIAL ═══════════════════════════
@scene(1, 'three letters', 'act 01 · the trial')
def s01():
    photo('york', 60, 150, 860, 645, 0, 30, PH_TAG.get('york', ''), z0=1.0, z1=1.05)
    text('DECEMBER 2023', 1000, 150, 30, L(1), 30, col=RED, font='mono600')
    heading('something strange outside several british stores', 1000, 190, 44, L(1, .2), 30); wrap(860)
    text('a familiar name, reduced to three letters', 1000, 330, 32, L(2), 30, col=GREY, font='outfit500')
    letters('WHSmith', 3, 1000, 400, 120, L(3), strike_t=L(3, .6)); EV.append((T(L(3, .6)), 'impact'))
    text('the name as letters, set in this film\'s type · not the sign or logo', 1004, 545, 18, L(3, .8), 30, col=GREY, font='mono400')
    text('meant to help modernize the shopping experience', 1000, 600, 30, L(4), 30, font='outfit500', wrap=860)
    text("instead: compared with the branding of britain's national health service", 1000, 670, 30, L(5), 30, col=RED, font='outfit500', wrap=860)
    text('york was among the reported trial sites · shown here in 2025 with whsmith signage', 60, 805, 16, 0, 30, col=GREY, font='mono400')
    text('more than two centuries of history · a public argument over three letters', 60, 850, 30, L(6), 30, col=GREY, font='outfit500', wrap=880)
    heading('not just about a logo', 1000, 800, 44, L(7), 30)
    heading('a business changing faster than its identity', 1000, 880, 44, L(8), 30, col=RED); wrap(860); EV.append((T(L(8)), 'low'))

@scene(2, 'the brand everyone knew')
def s02():
    text('LONDON · 1792', 60, 150, 30, L(1), 30, col=RED, font='mono600')
    heading('henry walton smith and his wife anna', 60, 190, 52, L(1, .2), 30); wrap(900)
    text('a small news-vending business · accounts of the exact start date and street vary', 64, 320, 22, L(1, .5), 30, col=GREY, font='outfit500')
    text('over generations: familiar across british high streets', 60, 360, 32, L(2), 30, font='outfit500')
    for k, s_ in enumerate(['newspapers', 'books', 'stationery', 'magazines', 'everyday essentials']):
        t = L(3, k * .35); card_box(60 + (k % 3) * 300, 420 + (k // 3) * 100, 280, 80, t, 30, edge=GREY); heading(s_, 90 + (k % 3) * 300, 440 + (k // 3) * 100, 32, t, 30)
    photo('bookstall', 1000, 150, 860, 600, L(4), 30, PH_TAG.get('bookstall', ''))
    text('1 NOVEMBER 1848 · EUSTON', 60, 640, 26, L(4), 30, col=RED, font='mono600')
    text('the first w.h. smith railway bookstall (history today)', 60, 680, 26, L(4, .3), 30, col=GREY, font='outfit500')
    rect(60, 780, 1800, 2, RULE, L(5), 30)
    text('SOMETHING COMPETITORS COULD NOT SIMPLY PURCHASE', 60, 810, 22, L(5), 30, col=GREY, font='mono600')
    heading('recognition', 60, 845, 96, L(5, .3), 30, col=RED); EV.append((T(L(5, .3)), 'impact'))
    text('customers knew the name before they entered the store', 1000, 820, 30, L(6), 30, font='outfit500', wrap=860)
    text('that familiarity would become central to the controversy', 1000, 900, 30, L(7), 30, col=GREY, font='outfit500', wrap=860); EV.append((T(L(7)), 'low'))

@scene(3, 'the high street problem')
def s03():
    heading("britain's traditional high streets under pressure", 60, 150, 52, L(1), 30)
    chips(['online shopping', 'changing consumer habits', 'supermarkets and specialist retailers'], 60, 250, L(2), dt=.6, size=34, gap=62, bar=GREY)
    photo('sherborne', 60, 480, 860, 430, L(3), 30, PH_TAG.get('sherborne', ''), fy=.6)
    photo('laguardia', 1000, 480, 860, 430, L(5), 30, PH_TAG.get('laguardia', ''), fy=.45)
    text('recognizable locations · but recognition alone could not guarantee growth', 1000, 260, 28, L(3), 30, font='outfit500', wrap=860)
    text('more alternatives for books, stationery, snacks, everyday purchases', 1000, 350, 26, L(4), 30, col=GREY, font='outfit500', wrap=860)
    text('TWO DISTINCT RETAIL ENVIRONMENTS', 60, 940, 22, L(6), 30, col=RED, font='mono600')
    text('town-center shopping', 60, 980, 30, L(7), 30, font='outfit500')
    text('people already traveling somewhere', 1000, 980, 30, L(8), 30, font='outfit500'); EV.append((T(L(8)), 'low'))

@scene(4, 'the experiment')
def s04():
    text('NEAR THE END OF 2023', 60, 150, 30, L(1), 30, col=RED, font='mono600')
    heading('10', 60, 190, 220, L(1, .2), 30, col=RED); EV.append((T(L(1, .2)), 'impact'))
    heading('trial locations', 60, 430, 52, L(1, .5), 30)
    text('reported sites include york, preston and canterbury · of more than 1,100 uk stores', 64, 505, 18, L(1, .8), 30, col=GREY, font='mono400')
    letters('WHSmith', 3, 500, 240, 96, L(2), strike_t=L(2, .5))
    text('signs also highlighted product categories · localised', 520, 380, 26, L(3), 30, col=GREY, font='outfit500', wrap=420)
    doc('doc_stmt', 1000, 150, 860, L(3, .5), 30, hls=(L(4), L(4, .4), L(3, .8), L(6), L(6, .4)))
    text('make the offer clearer', 60, 620, 34, L(5), 30, font='outfit500')
    heading('not a nationwide replacement', 60, 700, 44, L(6), 30); strike(56, 726, 600, L(6, .8))
    heading('a limited experiment', 60, 780, 44, L(7), 30, col=RED)
    heading('a small experiment · a very large public reaction', 60, 920, 48, L(8), 30); EV.append((T(L(8)), 'low'))

@scene(5, 'the nhs comparison')
def s05():
    text('PHOTOGRAPHS OF THE SIGNS SPREAD ONLINE', 60, 150, 22, L(1), 30, col=GREY, font='mono600')
    text('no freely licensed photograph of the trial signs was found · described here from press reports', 60, 185, 18, L(1, .3), 30, col=GREY, font='mono400')
    for k, (w_, lab) in enumerate([('WHS', 'the trial name'), ('NHS', 'the comparison critics made')]):
        t = L(2, k * .6); x = 60 + k * 560; card_box(x, 250, 520, 260, t, 30, edge=RED if k else GREY)
        heading(w_, x + 60, 280, 140, t, 30); text(lab, x + 64, 460, 22, t, 30, col=GREY, font='mono600')
    text('reported: white lettering against blue · letters only, not the logos', 60, 540, 22, L(2, 1.2), 30, col=GREY, font='mono400')
    text('why remove the most distinctive part of a recognizable name?', 1240, 260, 30, L(3), 30, font='outfit500', wrap=620)
    text('often mocking · beneath the jokes, a serious branding question', 1240, 400, 26, L(4), 30, col=GREY, font='outfit500', wrap=620)
    rect(60, 620, 1800, 2, RULE, L(5), 30)
    heading('what does a company gain by shortening a name customers already understand?', 60, 660, 48, L(5), 30); wrap(1800)
    heading('and what might it lose?', 60, 790, 48, L(6), 30, col=RED); EV.append((T(L(6)), 'impact'))
    text('intended: communicate the offer more clearly', 60, 900, 30, L(7), 30, font='outfit500')
    text('some observers: less recognizable instead', 1000, 900, 30, L(8), 30, col=GREY, font='outfit500'); EV.append((T(L(8)), 'low'))

# ═══════════════════════════ ACT 02 · THE NAME ═══════════════════════════
@scene(6, 'what a name does', 'act 02 · the name')
def s06():
    heading('a brand name performs several jobs at once', 60, 150, 56, L(1), 30)
    for k, s_ in enumerate(['recognize a business', 'remember previous experiences', 'distinguish it from competitors']):
        t = L(2, k * .5); y = 250 + k * 90; card_box(60, y, 820, 74, t, 30); check(90, y + 10, t, size=40); heading(s_, 160, y + 16, 32, t, 30)
    text('familiarity reduces the effort of a shopping decision', 60, 540, 28, L(3), 30, col=GREY, font='outfit500')
    heading('but branding also evolves', 1000, 250, 44, L(4), 30)
    text('shorter names · simpler symbols · updated storefronts', 1000, 320, 28, L(5), 30, font='outfit500', wrap=860)
    text('none is automatically a mistake', 1000, 400, 28, L(6), 30, col=GREY, font='outfit500')
    heading('does the new design improve the customer\'s understanding?', 1000, 470, 40, L(7), 30, col=RED); wrap(860)
    rect(60, 640, 1800, 2, RULE, L(8), 30)
    text('THE TENSION', 60, 670, 22, L(8), 30, col=GREY, font='mono600')
    heading('simplicity', 60, 710, 72, L(8, .2), 30); text('vs', 470, 735, 36, L(8, .3), 30, col=GREY, font='mono600'); heading('recognition', 560, 710, 72, L(8, .4), 30, col=RED)
    letters('WHSmith', 3, 60, 860, 90, L(9), strike_t=L(9, .4)); text('shorter', 530, 885, 34, L(9, .6), 30, col=GREY, font='outfit500')
    heading('not necessarily clearer', 1000, 870, 52, L(10), 30, col=RED); EV.append((T(L(10)), 'low'))

@scene(7, 'the internet puts it on trial')
def s07():
    heading('beyond local shoppers', 60, 150, 56, L(1), 30)
    text('national newspapers and design publications covered the experiment', 60, 230, 30, L(2), 30, col=GREY, font='outfit500')
    for k, s_ in enumerate(['the telegraph · dec 26, 2023', 'retail gazette · dec 27, 2023', 'the drum · jan 3, 2024', 'marketing beat · jan 5, 2024', 'creative review']):
        t = L(2, .3 + k * .25); text(s_, 60 + (k % 3) * 600, 290 + (k // 3) * 44, 22, t, 30, col=TXT, font='mono600')
    text('PRESS COVERAGE · SELECTED · HEADLINES NOT REPRODUCED', 60, 390, 16, L(2, .8), 30, col=GREY, font='mono400')
    text('some: an obvious resemblance overlooked', 60, 450, 30, L(3), 30, font='outfit500')
    text('others: a legitimate reason to rethink the storefront', 1000, 450, 30, L(4), 30, font='outfit500', wrap=860)
    for k, (h_, sub, t) in enumerate([('INTENDED MESSAGE', 'what customers could buy · merchandise', L(5)), ('PUBLIC REACTION', 'how the sign looked · three letters and a comparison', L(6))]):
        x = 60 + k * 920; card_box(x, 560, 880, 200, t, 30, edge=GREY if k == 0 else RED)
        text(h_, x + 40, 590, 24, t, 30, col=GREY if k == 0 else RED, font='mono600'); heading(sub, x + 40, 640, 36, t, 30); wrap(800)
    heading('a communications problem', 60, 830, 52, L(7), 30, col=RED); EV.append((T(L(7)), 'impact'))
    text('intended: merchandise', 60, 920, 30, L(8), 30, font='outfit500')
    text('the conversation: three letters and a visual comparison', 1000, 920, 30, L(9), 30, col=GREY, font='outfit500', wrap=860); EV.append((T(L(9)), 'low'))

@scene(8, 'was it actually a failure?')
def s08():
    heading('here is where the evidence matters', 60, 150, 56, L(1), 30)
    cols = [('CONFIRMED', ['a trial at ten locations', 'press coverage and criticism', 'the company\'s stated reason'], GREY, L(3)),
            ('PUBLIC REACTION', ['nhs comparison', 'mockery online', 'questions about the name'], GREY, L(4)),
            ('NOT ESTABLISHED', ['a nationwide revenue loss', 'store-level results', 'a control comparison'], RED, L(5))]
    for k, (h_, items, c, t) in enumerate(cols):
        x = 60 + k * 610; card_box(x, 250, 580, 330, t, 30, edge=c); text(h_, x + 36, 275, 24, t, 30, col=c if c == RED else TXT, font='mono600')
        for j, s_ in enumerate(items): text(s_, x + 36, 330 + j * 70, 30, t + .3 * j, 30, col=TXT if k < 2 else GREY, font='outfit500')
    text('criticism ≠ proof of damaged sales', 60, 620, 30, L(2), 30, col=RED, font='mono600')
    text('assigning a financial cost to those signs would be misleading', 60, 680, 30, L(5, .8), 30, font='outfit500')
    heading('a public-relations warning', 60, 770, 48, L(6), 30)
    heading('a commercial failure?  a different question', 60, 850, 48, L(7), 30, col=GREY)
    text('the larger financial story was unfolding somewhere else entirely', 60, 950, 30, L(8), 30, col=RED, font='outfit500'); EV.append((T(L(8)), 'low'))

# ═══════════════════════════ ACT 03 · THE REAL BUSINESS ═══════════════════════════
@scene(9, 'two very different businesses', 'act 03 · the real business')
def s09():
    text('FISCAL 2024 · YEAR TO 31 AUGUST · REVENUE · £ MILLIONS', 60, 150, 22, L(1), 30, col=GREY, font='mono600')
    heading('£1,918m group', 60, 190, 56, L(1, .3), 30)
    bars([('TRAVEL', 1466, '£1,466m', L(2), RED), ('HIGH STREET', 452, '£452m', L(3), GREY)], 120, 820, 260, 380, .25, lab_size=52)
    doc('doc_fy24', 1000, 150, 860, L(1, .6), 30, hls=(L(1, .9), L(2), L(3), L(5)))
    heading('travel: over 75% of group revenue', 1000, 640, 40, L(4), 30, col=RED); EV.append((T(L(4)), 'impact'))
    text('airports · railway stations · hospitals · international travel locations', 1000, 710, 26, L(5), 30, font='outfit500', wrap=860)
    text('the high street still mattered · no longer the main growth story', 1000, 790, 26, L(6), 30, col=GREY, font='outfit500', wrap=860)
    heading('the controversy concerned one part of a business focused on another', 60, 900, 44, L(8), 30); wrap(1800); EV.append((T(L(8)), 'low'))

@scene(10, 'why travel mattered')
def s10():
    photo('plymouth', 60, 150, 860, 645, 0, 30, PH_TAG.get('plymouth', ''))
    heading('a different operating environment', 1000, 150, 48, L(1), 30); wrap(860)
    text('passengers and commuters shop because they need something during a journey', 1000, 280, 30, L(2), 30, font='outfit500', wrap=860)
    for k, s_ in enumerate(['books', 'snacks', 'drinks', 'travel accessories', 'convenience']):
        t = L(3, k * .25); heading(s_, 1000 + (k % 3) * 290, 400 + (k // 3) * 60, 32, t, 30, col=RED if k == 4 else TXT)
    text('the high street: more alternatives · online retailers · competing stores', 1000, 560, 26, L(4), 30, col=GREY, font='outfit500', wrap=860)
    text('years of expansion · including internationally', 1000, 650, 30, L(5), 30, font='outfit500')
    text('the strategy increasingly emphasized those locations', 1000, 710, 26, L(6), 30, col=GREY, font='outfit500')
    heading('not what the signs should say', 60, 850, 40, L(7), 30, col=GREY); strike(56, 874, 560, L(7, .8))
    heading('which markets deserved investment, attention and commitment', 700, 850, 40, L(8), 30, col=RED); wrap(1160); EV.append((T(L(8)), 'low'))

@scene(11, 'the bigger decision')
def s11():
    text('MARCH 28, 2025', 60, 150, 30, L(1), 30, col=RED, font='mono600')
    heading('a much more consequential change', 60, 190, 56, L(1, .2), 30)
    text('UK HIGH STREET BUSINESS  →  MODELLA CAPITAL', 60, 290, 30, L(2), 30, font='mono600')
    text('ENTERPRISE VALUE · CASH AND DEBT-FREE BASIS', 60, 370, 22, L(3), 30, col=GREY, font='mono600')
    heading('£76m', 60, 400, 180, L(3, .3), 30, col=RED); EV.append((T(L(3, .3)), 'impact'))
    doc('doc_sale', 1000, 150, 860, L(2, .5), 30, hls=(L(2, .8), L(2, 1.1), L(3, .6), L(4, .5), L(6)))
    text('not £76m handed over in cash', 60, 620, 32, L(4), 30, font='outfit500'); strike(56, 640, 420, L(4, .8))
    text('announced: £52m gross cash · c.£25m net', 60, 680, 26, L(5), 30, col=GREY, font='outfit500')
    text('on completion: gross cash proceeds revised to up to £40m', 60, 720, 26, L(5, .4), 30, col=GREY, font='outfit500')
    heading('c.480 stores · c.5,000 colleagues', 60, 800, 44, L(6), 30)
    heading('the planned separation of the high-street chain from the group that built its name', 60, 900, 40, L(7), 30, col=RED); wrap(1800); EV.append((T(L(7)), 'low'))

# ═══════════════════════════ ACT 04 · THE SEPARATION ═══════════════════════════
@scene(12, 'the name stays behind', 'act 04 · the separation')
def s12():
    heading('a remarkable detail', 60, 150, 56, L(1), 30)
    card_box(60, 260, 560, 300, L(2), 30, edge=GREY)
    text('SOLD', 96, 285, 22, L(2), 30, col=GREY, font='mono600'); heading('high street operations', 96, 325, 40, L(2, .2), 30); wrap(500)
    text('→ modella capital → a new identity', 96, 470, 24, L(4), 30, col=GREY, font='outfit500')
    card_box(700, 260, 560, 300, L(2, .6), 30)
    text('RETAINED', 736, 285, 22, L(2, .6), 30, col=RED, font='mono600'); heading('the whsmith brand', 736, 325, 40, L(2, .8), 30)
    text('travel division keeps the familiar name', 736, 400, 24, L(3), 30, font='outfit500', wrap=500)
    photo('plymouth', 1340, 260, 520, 300, L(3), 30, 'plymouth station · oct 2026 · mutney · cc by 4.0')
    doc('doc_brand', 60, 600, 860, L(4), 30, hls=(L(4, .3), L(4, .7), L(3, .5)))
    text('NOT THE SAME DECISION', 1000, 620, 22, L(5), 30, col=RED, font='mono600')
    text('2023: a signage trial at ten stores', 1000, 660, 28, L(5, .2), 30, font='outfit500')
    text('2025: a corporate transaction, different commercial considerations', 1000, 710, 28, L(6), 30, font='outfit500', wrap=860)
    text('yet the contrast was striking', 1000, 820, 30, L(7), 30, col=GREY, font='outfit500')
    heading('the identity and the original retail estate, separated', 1000, 880, 40, L(9), 30, col=RED); wrap(860); EV.append((T(L(9)), 'low'))

@scene(13, 'enter tgjones')
def s13():
    photo('reading', 60, 150, 1100, 508, 0, 30, PH_TAG.get('reading', ''))
    text('the reading store was a whsmith until a few days before this photo', 60, 668, 16, 0, 30, col=GREY, font='mono400')
    text('JUNE 30, 2025', 1240, 150, 30, L(1), 30, col=RED, font='mono600')
    heading('sale completed', 1240, 190, 56, L(1, .2), 30)
    text('the former high street stores begin transitioning to a new name', 1240, 280, 28, L(2), 30, font='outfit500', wrap=620)
    heading('tgjones', 1240, 380, 96, L(2, .5), 30, col=RED); EV.append((T(L(2, .5)), 'impact'))
    text('modella capital: “re-establish these stores as the hub of every high street they serve”', 60, 700, 28, L(3), 30, font='outfit500', wrap=1100)
    text('source: modella capital', 64, 780, 18, L(3, .3), 30, col=GREY, font='mono400')
    text('familiar products and services · a different storefront identity', 1240, 560, 26, L(4), 30, col=GREY, font='outfit500', wrap=620)
    text('a business associated with british shopping for generations · a new chapter', 60, 840, 28, L(5), 30, font='outfit500', wrap=1100)
    heading('the irony was unmistakable', 1240, 700, 40, L(6), 30)
    heading('after a trial over three letters, an entirely new name', 1240, 770, 36, L(7), 30, col=RED); wrap(620)
    card_box(60, 930, 1800, 90, L(7, .6), 30, edge=GREY)
    text('POSTSCRIPT · JUNE–AUG 2026', 96, 945, 18, L(7, .6), 30, col=GREY, font='mono600')
    text('the high court sanctioned restructuring plans for the tgjones business, leaving a reduced footprint of 302 stores · [2026] ewhc 2079 (ch)', 96, 975, 20, L(7, .8), 30, font='outfit500', wrap=1720)

# ═══════════════════════════ ACT 05 · THE AUTOPSY ═══════════════════════════
@scene(14, 'did the rebrand cause the sale?', 'act 05 · the autopsy')
def s14():
    heading('no evidence establishes that the 2023 signage controversy caused the 2025 sale', 60, 150, 44, L(1), 30); wrap(1800)
    text('that would confuse two different decisions', 60, 270, 30, L(2), 30, col=GREY, font='outfit500')
    for k, (h_, pts, t) in enumerate([('SIGNAGE', [('dec 2023', 'trial signs at ten locations'), ('jan 2024', 'no plan to roll out')], L(5)),
                                      ('CORPORATE STRATEGY', [('fy2024', 'travel: over 75% of revenue'), ('mar 2025', 'sale: focus on higher-growth travel'), ('jun 2025', 'sale completed')], L(3))]):
        y = 360 + k * 250; text(h_, 60, y, 22, t, 30, col=RED if k else GREY, font='mono600'); rect(60, y + 80, 1800, 3, RULE, t, 30, grow=(t, t + 1, 'x'))
        for j, (d_, s_) in enumerate(pts):
            x = 60 + j * 600 + (0 if k else 0); sprite('dot_red' if k else 'dot_grey', x + 10, y + 81, t + .3 * j, 30)
            text(d_, x, y + 110, 20, t + .3 * j, 30, col=GREY, font='mono600'); text(s_, x, y + 145, 26, t + .3 * j, 30, font='outfit500')
    text('its financial reporting showed the growing importance of travel', 1240, 360, 22, L(4), 30, col=GREY, font='outfit500', wrap=620)
    text('same broader period of change · not cause and effect · no arrow drawn between them', 60, 870, 26, L(6), 30, col=GREY, font='outfit500')
    heading('a compelling story does not require inventing a connection', 60, 930, 40, L(7), 30, col=RED); wrap(1800)
    text('the documented contrast is interesting enough', 1240, 1000, 24, L(8), 30, font='outfit500'); EV.append((T(L(8)), 'low'))

@scene(15, 'the real branding lesson')
def s15():
    heading('three lessons', 60, 150, 56, L(1), 30)
    for k, (s_, t) in enumerate([('a recognizable name is a valuable business asset', L(2)), ('visual simplicity is not the same as customer clarity', L(3)), ('a brand\'s identity can outlive the retail business that made it famous', L(4))]):
        y = 260 + k * 110; card_box(60, y, 1800, 92, t, 30); text(f'{k + 1:02d}', 90, y + 24, 40, t, 30, col=RED, font='mono600'); heading(s_, 180, y + 24, 38, t, 30)
    text('the trial drew criticism because people recognized something had changed', 60, 640, 30, L(5), 30, font='outfit500')
    text('the sale: a strategic transformation far beyond storefront design', 60, 700, 30, L(6), 30, col=GREY, font='outfit500')
    for k, (h_, s_, t) in enumerate([('ONE STORY', 'perception', L(7)), ('THE OTHER', 'where future growth would come from', L(8))]):
        x = 60 + k * 920; card_box(x, 790, 880, 170, t, 30, edge=GREY if k == 0 else RED)
        text(h_, x + 40, 815, 22, t, 30, col=GREY, font='mono600'); heading(s_, x + 40, 860, 44, t, 30, col=TXT if k == 0 else RED); wrap(800)
    EV.append((T(L(8)), 'low'))

@scene(16, 'the verdict')
def s16():
    heading('for more than two centuries', 960, 200, 52, L(1), L(5), al='CENTER')
    text('recognition built through everyday british life', 960, 275, 32, L(1, .3), L(5), col=GREY, font='outfit500', al='CENTER')
    heading('a three-letter experiment became a national talking point', 960, 380, 44, L(2), L(5), al='CENTER')
    heading('but the bigger transformation was not a logo', 960, 500, 52, L(3), L(5), al='CENTER', col=RED); EV.append((T(L(3)), 'impact'))
    text('it was the decision to separate the high-street operations', 960, 620, 32, L(4), L(5), font='outfit500', al='CENTER')
    text('from the growing travel business', 960, 665, 32, L(4), L(5), font='outfit500', al='CENTER')
    CX.beat()
    text('THE VERDICT', 960, 220, 26, L(5), L(8), col=GREY, font='mono600', al='CENTER')
    heading('not that brands should never change', 960, 290, 52, L(5, .2), L(8), al='CENTER')
    heading('every change needs a clear purpose', 960, 410, 44, L(6), L(8), al='CENTER')
    heading('every outcome needs to be judged against evidence', 960, 470, 44, L(6, .4), L(8), al='CENTER')
    heading('a familiar name can survive', 960, 590, 52, L(7), L(8), al='CENTER', col=RED); heading('even when the business behind it changes completely', 960, 660, 44, L(7), L(8), al='CENTER', col=RED); EV.append((T(L(7)), 'impact'))
    CX.beat()
    e = heading('brand coroner', 943, 420, 110, L(8), 30, al='CENTER'); e2 = text('.', 1305, 420, 110, L(8, .8), 30, col=RED)
    f = text('EVERY BRAND LEAVES EVIDENCE.', 960, 570, 36, L(8, .4), 30, col=GREY, font='outfit500', al='CENTER')
    rect(810, 555, 300, 2, RED, L(8, .2), 30, grow=(L(8, .2), L(8, 1.0), 'x'))
    for st in (e, e2, f): fade(st, L(8), 30, 1, .6, 2.0)
