# ── LEGO scene designs. Authored on a 0–30 s grid per scene; L(k) is the grid time of narration line k, and
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

# ═══════════════════════════ ACT 01 · THE COLLAPSE ═══════════════════════════
@scene(1, 'the impossible collapse', 'act 01 · the collapse')
def s01():
    photo('bricks', 60, 150, 860, 576, 0, 30, PH_TAG.get('bricks', ''))
    text('2004', 1000, 150, 30, L(1), 30, col=RED, font='mono600')
    heading("one of the world's most recognizable toy companies, fighting for survival", 1000, 190, 44, L(1, .2), 30); wrap(860)
    text('decades teaching children to build almost anything', 1000, 330, 30, L(2), 30, col=GREY, font='outfit500', wrap=860)
    money('GROUP NET LOSS · 2004 · AS REPORTED AT THE TIME', '− DKK 1,931m', 1000, 420, L(4), size=96, sub='lego group 2005 results release (feb 2006)')
    text('the extraordinary part?', 60, 790, 34, L(5), 30, col=GREY, font='outfit500')
    text('it had not forgotten how to invent', 60, 850, 32, L(6), 30, font='outfit500')
    text('it had expanded in too many directions without making enough money', 60, 905, 32, L(7), 30, col=RED, font='outfit500', wrap=1000)
    heading('lego needed to become less complicated', 1000, 900, 48, L(9), 30); wrap(860); EV.append((T(L(9)), 'low'))

@scene(2, 'the system that built an empire')
def s02():
    photo('olekirk', 60, 150, 520, 600, 0, 30, PH_TAG.get('olekirk', ''))
    text('BILLUND, DENMARK · 1932', 640, 150, 30, L(1), 30, col=RED, font='mono600')
    heading('ole kirk kristiansen founds his toy business', 640, 190, 48, L(2), 30); wrap(620)
    text('wooden toys → plastic construction bricks', 640, 340, 30, L(3), 30, font='outfit500')
    photo('lego1957', 1340, 150, 520, 400, L(3), 30, PH_TAG.get('lego1957', ''))
    text('not any single model', 640, 420, 30, L(4), 30, col=GREY, font='outfit500')
    heading('a system', 640, 470, 110, L(5), 30, col=RED); EV.append((T(L(5)), 'impact'))
    chips(['connect', 'separate', 'combine', 'dismantle · rebuild'], 640, 620, L(6), dt=.5, size=32, gap=56)
    text('jan 28, 1958: patent application for the stud-and-tube brick (lego history)', 1340, 600, 22, L(6), 30, col=GREY, font='mono600', wrap=520)
    text('a distinctive identity · compatible across generations', 60, 880, 30, L(8), 30, font='outfit500')
    heading('the principle behind its success would become the foundation of its recovery', 60, 940, 36, L(10), 30, col=RED); wrap(1800); EV.append((T(L(10)), 'low'))

@scene(3, 'when growth became the strategy')
def s03():
    text('THE LATE 1990s', 60, 150, 30, L(1), 30, col=RED, font='mono600')
    heading('the toy industry was changing', 60, 190, 56, L(1, .2), 30)
    chips(['electronic entertainment competing for attention', 'retailers gaining negotiating power'], 60, 290, L(2), dt=1.2, size=32, gap=60, bar=GREY)
    text('LEGO SEARCHED FOR NEW OPPORTUNITIES', 60, 450, 22, L(4), 30, col=GREY, font='mono600')
    for k, s_ in enumerate(['products', 'entertainment', 'retail', 'theme parks']):
        t = L(5, k * .3); card_box(60 + k * 225, 490, 210, 80, t, 30, edge=RED if k == 3 else GREY); heading(s_, 80 + k * 225, 514, 25, t, 30)
    photo('legoland68', 1000, 150, 860, 598, L(5), 30, PH_TAG.get('legoland68', ''))
    text('four legoland parks by 2005: billund · windsor · california · deutschland (rté, july 2005)', 1004, 770, 18, L(5, .5), 30, col=GREY, font='mono400')
    text('some succeeded · others added cost and complexity', 60, 640, 30, L(6), 30, font='outfit500')
    text('growing beyond the construction-toy business', 60, 700, 30, L(8), 30, col=GREY, font='outfit500')
    heading('new categories ≠ profitable growth', 60, 830, 52, L(9), 30, col=RED)
    text('the more it expanded, the harder it became to manage', 60, 930, 30, L(10), 30, font='outfit500'); EV.append((T(L(10)), 'low'))

@scene(4, 'the complexity trap')
def s04():
    heading('consider one more specialized part', 60, 150, 56, L(1), 30)
    text('EDITORIAL DIAGRAM · HOW COMPLEXITY ADDS COST', 60, 240, 22, L(2), 30, col=GREY, font='mono600')
    steps = ['design', 'tooling', 'manufacturing', 'inventory', 'distribution']
    for k, s_ in enumerate(steps):
        t = L(2, .2 + k * .35); x = 60 + k * 360; card_box(x, 290, 320, 90, t, 30, edge=GREY if k < 4 else RED); heading(s_, x + 30, 314, 34, t, 30)
        if k < 4: hline(x + 324, x + 356, 335, t + .2, 30, t + .2, t + .4, col=GREY)
    text('expensive when products fail to sell in sufficient quantities', 60, 430, 32, L(3), 30, font='outfit500')
    heading('an innovation system that was difficult to control', 60, 520, 48, L(4), 30)
    text('ideas funded without consistently understanding their commercial consequences', 60, 600, 30, L(5), 30, col=GREY, font='outfit500')
    heading('creativity', 60, 700, 64, L(6), 30, col=GREY); strike(56, 735, 330, L(6, .6))
    heading('discipline around creativity', 460, 700, 64, L(7), 30, col=RED)
    photo('brick', 1240, 760, 620, 260, L(8), 30, PH_TAG.get('brick', ''))
    heading('famous for connecting pieces · struggling to connect its own decisions', 60, 860, 40, L(8), 30); wrap(1120); EV.append((T(L(8)), 'low'))

@scene(5, 'the first financial warning')
def s05():
    text('2003', 60, 150, 30, L(1), 30, col=RED, font='mono600')
    heading('impossible to ignore', 60, 190, 56, L(1, .2), 30)
    money('GROUP NET LOSS · 2003', '− DKK 935m', 60, 290, L(2), size=110, sub="as given in lego's later five-year summary")
    doc('doc_ar03', 1000, 150, 860, L(2, .5), 30, hls=(L(3), L(3, .3), L(3, .6)))
    text('management: the growth strategy had not delivered', 60, 520, 30, L(3), 30, font='outfit500')
    text('more than an uncomfortable year for shareholders', 60, 600, 30, L(4), 30, col=GREY, font='outfit500')
    heading('a privately owned family business · its independence under pressure', 60, 680, 44, L(5), 30, col=RED); wrap(1800)
    chips(['preserve cash', 'rebuild profitability', 'reconsider where it belonged'], 60, 800, L(6), dt=.5, size=30, gap=50)
    text('the same strategy: increasingly dangerous', 1000, 900, 30, L(7), 30, col=GREY, font='outfit500'); EV.append((T(L(7)), 'low'))

# ═══════════════════════════ ACT 02 · THE DECISION ═══════════════════════════
@scene(6, 'the leadership decision', 'act 02 · the decision')
def s06():
    photo('knudstorp', 60, 150, 560, 690, 0, 30, PH_TAG.get('knudstorp', ''))
    text('2004', 700, 150, 30, L(1), 30, col=RED, font='mono600')
    heading('jørgen vig knudstorp', 700, 190, 72, L(1, .2), 30)
    text('becomes chief executive · succeeding kjeld kirk kristiansen, ceo 1979–2004', 704, 290, 22, L(1, .5), 30, col=GREY, font='mono600')
    heading('not a fashionable new identity', 700, 370, 40, L(2), 30, col=GREY); strike(696, 394, 600, L(2, .8))
    heading('a financially sustainable company', 700, 440, 48, L(3), 30, col=RED)
    for k, s_ in enumerate(['products', 'people', 'assets', 'investment']):
        t = L(4, k * .3); card_box(700 + k * 290, 540, 270, 80, t, 30, edge=GREY); heading(s_, 726 + k * 290, 562, 30, t, 30)
    text('clearer priorities · confronting the economics of the business', 700, 670, 28, L(5), 30, font='outfit500')
    text('which activities genuinely supported its strengths?', 700, 730, 28, L(6), 30, col=GREY, font='outfit500')
    heading('survival: what it stopped doing, as much as what it continued', 60, 900, 44, L(7), 30); wrap(1800); EV.append((T(L(7)), 'low'))

@scene(7, 'the decision to go backward')
def s07():
    photo('brick', 60, 150, 860, 620, 0, 30, PH_TAG.get('brick', ''))
    heading('refocus on the construction system', 1000, 150, 52, L(1), 30); wrap(860)
    text('not a rejection of innovation', 1000, 300, 30, L(2), 30, col=GREY, font='outfit500')
    text('innovation built around a more coherent foundation', 1000, 350, 30, L(3), 30, font='outfit500', wrap=860)
    for k, s_ in enumerate(['bricks', 'compatible elements', 'recognizable play patterns', 'profitable product lines']):
        t = L(4, k * .35); rect(1000, 450 + k * 62 + 8, 8, 30, RED, t, 30); heading(s_, 1026, 450 + k * 62, 34, t, 30)
    text('new ideas must strengthen the core, not distract from it', 60, 820, 30, L(5), 30, font='outfit500')
    text('rediscovering the value of what customers already loved', 60, 880, 30, L(7), 30, col=GREY, font='outfit500')
    heading('what should never have changed?', 1000, 860, 52, L(8), 30, col=RED); wrap(860); EV.append((T(L(8)), 'low'))

@scene(8, 'cutting the cost of complexity')
def s08():
    photo('kladno', 1000, 150, 860, 645, 0, 30, PH_TAG.get('kladno', ''))
    text('changing how the business operated', 60, 150, 34, L(2), 30, font='outfit500')
    money('2004 ACTION PLAN · COSTS VS 2003', '− DKK 1.52bn', 60, 220, L(3), size=100)
    heading('− 20%', 60, 420, 110, L(4), 30, col=RED)
    doc('doc_ar04', 60, 580, 860, L(3, .5), 30, hls=(L(3, .8), L(4, .2)))
    text('≈ 1,000 jobs cut from a workforce of about 8,000 (reported: the telegraph, oct 2004)', 1000, 820, 22, L(5), 30, font='mono600', wrap=860)
    text('difficult decisions · real human consequences', 1000, 890, 30, L(6), 30, col=GREY, font='outfit500')
    text('costs in line with a smaller, more sustainable business', 1000, 940, 28, L(7), 30, font='outfit500')
    heading('not product nostalgia alone', 60, 940, 44, L(8), 30, col=RED); EV.append((T(L(8)), 'low'))

# ═══════════════════════════ ACT 03 · THE SEPARATION ═══════════════════════════
@scene(9, 'selling legoland', 'act 03 · the portfolio')
def s09():
    photo('legoland68', 60, 150, 860, 598, 0, 30, PH_TAG.get('legoland68', ''))
    heading('one of the most consequential decisions', 1000, 150, 44, L(1), 30); wrap(860)
    text('theme parks: substantial capital · management attention', 1000, 270, 28, L(2), 30, col=GREY, font='outfit500')
    text('no longer essential to the core business', 1000, 320, 30, L(3), 30, font='outfit500')
    money('JULY 2005 · FOUR LEGOLAND PARKS', '€375m', 1000, 390, L(4), size=110)
    doc('doc_lland', 1000, 600, 860, L(4, .5), 30, hls=(L(4, .7), L(4, 1.0), L(5), L(5, .3)))
    text('BLACKSTONE & MANAGEMENT 70%  ·  LEGO SIDE 30%', 60, 800, 26, L(5), 30, font='mono600')
    text('improved liquidity · concentrate on toys', 60, 860, 30, L(6), 30, font='outfit500')
    heading('the brand experience continued · lego no longer ran the parks', 60, 940, 36, L(7), 30, col=RED); wrap(900); EV.append((T(L(7)), 'low'))

@scene(10, 'the customer was still there')
def s10():
    photo('brickfair', 60, 150, 860, 571, 0, 30, PH_TAG.get('brickfair', ''))
    heading('reconnecting innovation with demand', 1000, 150, 48, L(1), 30); wrap(860)
    chips(['children', 'families', 'adult enthusiasts'], 1000, 290, L(2), dt=.4, size=34, gap=58)
    text('a relationship beyond individual sets', 1000, 490, 30, L(3), 30, col=GREY, font='outfit500')
    heading('create · combine · rebuild', 1000, 550, 52, L(4), 30, col=RED)
    text('which products deserved investment?', 1000, 650, 30, L(5), 30, font='outfit500')
    text('not abandoning every licensed theme or experiment', 60, 780, 30, L(6), 30, col=GREY, font='outfit500')
    text('does it reinforce the building experience? can it earn sustainable returns?', 60, 840, 30, L(7), 30, font='outfit500', wrap=1800)
    heading('enthusiasm, connected to commercial discipline', 60, 930, 44, L(9), 30, col=RED); EV.append((T(L(9)), 'low'))

@scene(11, 'innovation with rules')
def s11():
    heading('ambitious products · within the construction system', 60, 150, 48, L(1), 30)
    text('licensed partnerships could remain valuable when they worked inside the system', 60, 230, 28, L(2), 30, col=GREY, font='outfit500')
    text('EDITORIAL ANALYSIS · AN ILLUSTRATIVE FRAMEWORK, NOT A LEGO DOCUMENT', 60, 320, 20, L(3), 30, col=RED, font='mono600')
    for k, s_ in enumerate(['fits the construction system?', 'evidence of customer demand?', 'cost under control?', 'commercially sustainable?']):
        t = L(3, .3 + k * .5); y = 370 + k * 90; card_box(60, y, 900, 74, t, 30); check(90, y + 10, t, size=40); heading(s_, 160, y + 16, 32, t, 30)
    chips(['better cost control', 'stronger coordination', 'clearer commercial priorities'], 1040, 380, L(4), dt=.4, size=32, gap=60, bar=GREY)
    heading('creativity and constraints were not opposites', 1040, 620, 40, L(5), 30, col=RED); wrap(820)
    text('constraints direct resources toward stronger ideas', 60, 780, 30, L(6), 30, font='outfit500')
    heading('experiment without making every experiment an expensive commitment', 60, 880, 40, L(7), 30); wrap(1800); EV.append((T(L(7)), 'low'))

# ═══════════════════════════ ACT 04 · THE EVIDENCE ═══════════════════════════
@scene(12, 'the first signs of recovery', 'act 04 · the evidence')
def s12():
    heading('the results began to change', 60, 150, 56, L(1), 30)
    text('GROUP NET RESULT · DKK MILLIONS · AS REPORTED AT THE TIME', 60, 240, 22, L(2), 30, col=GREY, font='mono600')
    for k, (yr, v, c, t) in enumerate([('2004', '− 1,931', GREY, L(2)), ('2005', '+ 505', RED, L(2, .5))]):
        heading(v, 60 + k * 440, 280, 96, t, 30, col=c); text(yr, 64 + k * 440, 400, 24, t, 30, col=GREY, font='mono600')
    doc('doc_ar05', 1000, 150, 860, L(2, .8), 30, hls=(L(3), L(3, .3), L(3, .6), L(4, .4)))
    heading('an important qualification', 60, 480, 44, L(3), 30, col=RED)
    text('the 2005 result included discontinued activities, including asset disposals', 60, 550, 28, L(4), 30, font='outfit500', wrap=880)
    card_box(60, 640, 420, 140, L(4, .5), 30, edge=GREY); text('DISCONTINUING', 90, 660, 20, L(4, .5), 30, col=GREY, font='mono600'); heading('+ 174', 90, 690, 56, L(4, .7), 30, col=GREY)
    card_box(500, 640, 420, 140, L(5), 30); text('CONTINUING', 530, 660, 20, L(5), 30, col=RED, font='mono600'); heading('+ 331', 530, 690, 56, L(5, .2), 30, col=RED)
    text('stronger evidence of operational recovery', 60, 820, 30, L(6), 30, font='outfit500')
    text('not every improvement came from selling more toys', 60, 880, 30, L(7), 30, col=RED, font='outfit500')
    text("lego's 2008 annual report later restated these years on a different basis: 2004 −1,800 · 2005 +214", 60, 970, 18, L(7, .4), 30, col=GREY, font='mono400')

@scene(13, 'from survival to stability')
def s13():
    money('2006 · GROUP NET PROFIT · AS REPORTED', 'DKK 1,430m', 60, 150, L(1), size=110)
    doc('doc_ar06', 1000, 150, 860, L(1, .5), 30, hls=(L(1, .8),))
    doc('doc_ar08', 1000, 330, 860, L(1, 1.2), 30, hls=(L(2, .2), L(2, .4), L(2, .6)))
    text('beyond emergency stabilization', 60, 380, 32, L(2), 30, font='outfit500')
    text('FIRST, IMPROVE', 60, 470, 22, L(3), 30, col=GREY, font='mono600')
    chips(['supply chains', 'product profitability', 'organizational processes'], 60, 510, L(3, .2), dt=.4, size=34, gap=60)
    text('— then accelerate growth', 60, 710, 30, L(3, 1.4), 30, col=RED, font='outfit500')
    heading('that sequence mattered', 60, 790, 48, L(4), 30)
    text('not recreating its earlier size · building a business able to support expansion', 60, 870, 28, L(5), 30, col=GREY, font='outfit500', wrap=1800)
    heading('rapid growth is dangerous when the economics underneath are weak', 60, 940, 40, L(7), 30, col=RED); wrap(1800); EV.append((T(L(7)), 'low'))

# ═══════════════════════════ ACT 05 · THE AUTOPSY ═══════════════════════════
@scene(14, 'the brick becomes the platform', 'act 05 · the autopsy')
def s14():
    photo('bricks', 60, 150, 860, 576, 0, 30, PH_TAG.get('bricks', ''))
    heading('a foundation for later product successes', 1000, 150, 48, L(1), 30); wrap(860)
    chips(['construction themes', 'licensed sets', 'new play experiences'], 1000, 300, L(2), dt=.4, size=34, gap=60)
    text('grown from the same recognizable system', 1000, 500, 28, L(2, 1.2), 30, col=GREY, font='outfit500')
    text('it kept evolving · no permanent return to the old catalog', 1000, 570, 28, L(3), 30, font='outfit500', wrap=860)
    heading('not "avoid diversification"', 60, 790, 44, L(5), 30, col=GREY); strike(56, 816, 620, L(5, .8))
    heading('know which capabilities make diversification work', 60, 880, 44, L(6), 30, col=RED)
    text('not simply the logo or the history:', 1000, 700, 28, L(7), 30, col=GREY, font='outfit500')
    heading('compatibility · creativity · repeatability', 1000, 760, 40, L(8), 30); wrap(860); EV.append((T(L(8)), 'impact'))

@scene(15, 'what actually saved lego?')
def s15():
    heading('four interconnected decisions', 60, 150, 56, L(1), 30)
    for k, (h_, s_, t) in enumerate([('01', 'refocus on the construction system', L(2)), ('02', 'reduce costs · operating discipline', L(3)), ('03', 'sell non-core assets', L(4)), ('04', 'customer-led, profitable product development', L(5))]):
        x = 60 + k * 455; card_box(x, 260, 430, 300, t, 30)
        text(h_, x + 36, 290, 48, t, 30, col=RED, font='mono600'); heading(s_, x + 36, 370, 34, t, 30); wrap(370)
    text('evidence: 2004 action plan (−20% costs) · legoland sale (2005, €375m) · results 2005–2006', 60, 590, 20, L(5, .5), 30, col=GREY, font='mono400')
    text('no single decision explains the recovery', 60, 680, 32, L(6), 30, font='outfit500')
    text('together: how resources were allocated and growth evaluated', 60, 740, 32, L(7), 30, col=GREY, font='outfit500')
    heading('not stopping innovation', 60, 840, 44, L(8), 30, col=GREY); strike(56, 866, 470, L(8, .8))
    heading('choosing where innovation belonged', 620, 840, 44, L(9), 30, col=RED); EV.append((T(L(9)), 'low'))

@scene(16, 'the verdict')
def s16():
    heading('lego nearly lost its future', 960, 200, 60, L(1), L(4), al='CENTER')
    text('expanding beyond the system that made it successful', 960, 290, 32, L(1, .4), L(4), col=GREY, font='outfit500', al='CENTER')
    heading('more products · more businesses · more ideas', 960, 400, 44, L(2), L(4), al='CENTER')
    heading('did not necessarily mean more value', 960, 470, 44, L(2, .6), L(4), al='CENTER', col=RED); EV.append((T(L(2, .6)), 'impact'))
    text('a clearer identity + stronger financial and operational discipline', 960, 600, 32, L(3), L(4), font='outfit500', al='CENTER')
    CX.beat()
    text('THE VERDICT', 960, 220, 26, L(4), L(7), col=GREY, font='mono600', al='CENTER')
    heading('the lesson extends far beyond toys', 960, 290, 52, L(4, .2), L(7), al='CENTER')
    heading("a brand's greatest opportunity is not always the next market", 960, 410, 44, L(5), L(7), al='CENTER')
    heading('sometimes it is the advantage it already has', 960, 540, 52, L(6), L(7), al='CENTER', col=RED)
    heading('but has stopped protecting', 960, 610, 52, L(6), L(7), al='CENTER', col=RED); EV.append((T(L(6)), 'impact'))
    CX.beat()
    e = heading('brand coroner', 943, 420, 110, L(7), 30, al='CENTER'); e2 = text('.', 1305, 420, 110, L(7, .8), 30, col=RED)
    f = text('EVERY BRAND LEAVES EVIDENCE.', 960, 570, 36, L(7, .4), 30, col=GREY, font='outfit500', al='CENTER')
    rect(810, 555, 300, 2, RED, L(7, .2), 30, grow=(L(7, .2), L(7, 1.0), 'x'))
    for st in (e, e2, f): fade(st, L(7), 30, 1, .6, 2.0)
