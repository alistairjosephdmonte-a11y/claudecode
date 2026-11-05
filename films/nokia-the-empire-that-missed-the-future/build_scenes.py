# ── Boeing scene designs. Authored on a 0–30 s grid per scene; L(k) is the grid time of narration line k, and
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

# ═══════════════════════════ ACT 01 · THE FALL ═══════════════════════════
@scene(1, 'the empire', 'act 01 · the fall')
def s01():
    heading('2007', 960, 330, 220, L(1, -.3), L(2), al='CENTER'); text('nokia was almost untouchable', 960, 620, 40, L(1, .6), L(2), col=GREY, font='outfit500', al='CENTER')
    CX.beat()
    photo('p3310', 60, 150, 480, 740, L(2), 30, PH_TAG['p3310'], fy=.35)
    heading('437M', 620, 150, 190, L(2), 30); text('mobile devices sold in 2007', 628, 360, 30, L(2, .4), 30, col=GREY, font='outfit500')
    heading('38%', 620, 420, 190, L(3), 30, col=RED); text('estimated share of the global market · 2007', 628, 630, 30, L(3, .4), 30, col=GREY, font='outfit500')
    doc('doc_ar07', 1260, 160, 600, L(2, .8), 30, hls=(L(2, 1.6), L(3, 1.0)))
    chips(['offices', 'schools', 'taxis', 'airports', 'millions of homes'], 1260, 470, L(4), dt=.5, size=32, gap=58)
    heading('it was leading it.', 620, 720, 56, L(6), 30)
    text('SIX YEARS LATER → THE SALE OF ITS HANDSET BUSINESS', 620, 810, 24, L(7), 30, col=GREY, font='mono600')
    heading('how does a market leader lose the market it helped create?', 620, 880, 42, L(8), 30, col=RED); EV.append((T(L(8)), 'low'))

@scene(2, 'the end of an era')
def s02():
    text('SEPTEMBER 3, 2013', 60, 150, 30, L(1), 30, col=RED, font='mono600'); heading('nokia → microsoft', 60, 190, 72, L(1), 30)
    doc('doc_deal', 60, 320, 820, L(2), 30, hls=(L(2, .8),))
    heading('€5.44B', 1000, 150, 180, L(3), 30); text('announced value · approximately · including a patent licence', 1004, 350, 24, L(3, .4), 30, col=GREY, font='mono600')
    text('€3.79B   devices & services business', 1004, 410, 28, L(3, 1.0), 30, font='mono600')
    text('€1.65B   patent licence and future option', 1004, 460, 28, L(3, 1.4), 30, font='mono600')
    heading('nokia had meant "the mobile phone"', 60, 620, 40, L(4), 30, col=GREY)
    heading('now it would leave handset manufacturing', 60, 680, 40, L(5), 30)
    heading('not a bankruptcy', 1000, 600, 64, L(6), 30, col=RED); text('the company continued operating', 1004, 690, 32, L(7), 30, col=GREY, font='outfit500')
    rect(60, 840, 1800, 2, RULE, L(8), 30)
    heading('what collapsed: its position as the dominant phone maker', 960, 880, 48, L(8), 30, al='CENTER', col=RED); EV.append((T(L(8)), 'low'))

# ═══════════════════════════ ACT 02 · THE ADVANTAGE ═══════════════════════════
@scene(3, 'the company that understood mobile', 'act 02 · the advantage')
def s03():
    photo('hq', 60, 150, 900, 675, 0, 30, PH_TAG['hq'])
    text('THE FINNISH COMPANY BUILT', 1020, 150, 22, L(2), 30, col=GREY, font='mono600')
    chips(['hardware engineering', 'manufacturing scale', 'distribution', 'brand recognition'], 1020, 190, L(2), dt=.7, size=36, gap=64)
    for k, s_ in enumerate(['dependable devices', 'familiar designs', 'a supply chain that reached markets others struggled to serve']):
        text(s_, 1020, 470 + k * 46, 28, L(3 + k), 30, col=TXT if k < 2 else GREY, font='outfit500', wrap=840)
    text('SINCE 1998', 1020, 640, 28, L(6), 30, col=RED, font='mono600'); heading("the world's leading mobile phone maker", 1020, 680, 40, L(6), 30)
    text('nokia form 20-f 2007: "a position nokia has held since 1998"', 1020, 740, 20, L(6, .6), 30, col=GREY, font='mono400')
    text('… and it kept expanding through the 2000s', 1020, 790, 28, L(7), 30, col=GREY, font='outfit500')
    heading('mobile technology for enormous numbers of people', 60, 900, 52, L(8), 30, col=RED)

@scene(4, 'nokia already had smartphones')
def s04():
    text('THE POPULAR EXPLANATION', 960, 260, 24, L(1), L(4), col=GREY, font='mono600', al='CENTER')
    heading('"nokia didn\'t understand smartphones"', 960, 320, 72, L(2), L(4), al='CENTER')
    strike(260, 368, 1400, L(3), L(4)); heading('not accurate', 960, 480, 64, L(3, .5), L(4), col=RED, al='CENTER')
    CX.beat()
    photo('n95', 60, 150, 360, 760, L(4), 30, PH_TAG['n95'], fx=.5, fy=.5)
    photo('e71', 470, 210, 560, 700, L(5), 30, PH_TAG['e71'])
    text('BEFORE THE FIRST IPHONE', 1100, 150, 24, L(4), 30, col=RED, font='mono600'); heading('nokia sold mobile computers', 1100, 190, 48, L(4), 30)
    text('NSERIES · ESERIES', 1100, 270, 22, L(5), 30, col=GREY, font='mono600')
    chips(['cameras', 'internet access', 'email', 'navigation', 'multimedia'], 1100, 310, L(5), dt=.5, size=34, gap=60)
    text('NOKIA N95 · ON SALE 2007 (ANNOUNCED SEPT 2006)', 1100, 640, 22, L(6), 30, col=RED, font='mono600')
    heading('phones were becoming computers', 1100, 690, 40, L(7), 30)
    heading('what it underestimated: how the experience of using them would change', 1100, 780, 38, L(8), 30, col=RED)
    CX.m.sequences[-1].wrap_width = 760 / W

# ═══════════════════════════ ACT 03 · THE MARKET CHANGES ═══════════════════════════
@scene(5, 'the iphone moment', 'act 03 · the market changes')
def s05():
    photo('jobs', 60, 150, 1080, 720, 0, 30, PH_TAG['jobs'], fx=.5, fy=.4, z0=1.0, z1=1.06)
    text('JANUARY 9, 2007', 1200, 150, 30, L(1), 30, col=RED, font='mono600'); heading('apple introduces', 1200, 190, 52, L(1), 30); heading('the iphone', 1200, 250, 72, L(1, .4), 30, col=RED)
    text('not the first smartphone', 1200, 370, 30, L(2), 30, col=GREY, font='outfit500'); text('not the first touchscreen phone', 1200, 416, 30, L(3), 30, col=GREY, font='outfit500')
    heading('a different philosophy', 1200, 490, 44, L(4), 30)
    for k, s_ in enumerate(['a large touchscreen', 'software built for direct interaction', 'hardware and operating system integrated']):
        rect(1200, 572 + k * 62, 8, 28, RED, L(5 + k), 30); text(s_, 1226, 566 + k * 62, 30, L(5 + k), 30, wrap=640); EV.append((T(L(5 + k)), 'type'))
    text('the threat: not simply another expensive handset', 60, 920, 30, L(8), 30, col=GREY, font='outfit500')
    heading('a new definition of what a smartphone should feel like', 60, 970, 44, L(9), 30, col=RED)

@scene(6, 'the platform war')
def s06():
    heading('the competition moved beyond devices', 960, 150, 44, L(1), 30, col=GREY, al='CENTER')
    cols = [('JULY 2008', 'app store', 'apple · iphone', L(2), RED), ('FROM 2008', 'android', 'google · many manufacturers', L(3), RED), ('NOKIA', 'symbian + services', 'an established operating system', L(7), GREY)]
    for k, (a_, b_, c_, t, e) in enumerate(cols):
        x = 60 + k * 610; card_box(x, 250, 580, 230, t, 30, edge=e)
        text(a_, x + 36, 280, 24, t, 30, col=RED if e == RED else GREY, font='mono600'); heading(b_, x + 36, 320, 60 if k < 2 else 48, t, 30); text(c_, x + 36, 410, 26, t, 30, col=GREY, font='outfit500')
    heading('applications · developers · operating systems · services', 960, 560, 40, L(4), 30, al='CENTER')
    heading('camera · battery · physical design', 960, 660, 40, L(5), 30, al='CENTER', col=GREY); strike(620, 688, 680, L(5, .8))
    heading('→ the software ecosystem decided what users could do', 960, 740, 44, L(6), 30, al='CENTER', col=RED)
    heading('the market moved toward integrated platforms — fast', 960, 900, 48, L(8), 30, al='CENTER'); EV.append((T(L(8)), 'low'))

@scene(7, 'the symbian problem')
def s07():
    photo('s5800', 60, 150, 600, 800, 0, 30, PH_TAG['s5800'])
    text("NOKIA'S PRINCIPAL SMARTPHONE OS", 740, 150, 24, L(1), 30, col=GREY, font='mono600'); heading('symbian', 740, 190, 110, L(1), 30)
    text('it powered millions of capable devices', 740, 340, 32, L(2), 30, font='outfit500')
    chips(['legacy architecture', 'development complexity', 'hard to compete in a touchscreen-centred market'], 740, 420, L(3), dt=.8, size=34, gap=64)
    text('nokia kept investing in symbian — and pursued alternatives', 740, 640, 28, L(4), 30, col=GREY, font='outfit500')
    heading('not an absence of innovation', 740, 700, 44, L(5), 30)
    heading('the difficulty: one competitive platform', 740, 760, 44, L(6), 30, col=RED)
    text('EVERY DELAY', 740, 880, 22, L(7), 30, col=GREY, font='mono600'); hline(900, 1120, 892, L(7), 30, L(7), L(7, .6))
    text('apple + android: more customers, developers, manufacturers', 1140, 878, 26, L(7, .6), 30, font='outfit500', wrap=720)

@scene(8, 'too many directions')
def s08():
    card_box(60, 420, 300, 140, L(1), 30); heading('nokia', 210, 455, 56, L(1), 30, al='CENTER')
    hline(360, 470, 490, L(1), 30, L(1), L(1, .4), head=False); rect(468, 255, 4, 470, RED, L(1, .4), 30, grow=(L(1, .4), L(1, .9), 'y'))
    for k, (a_, b_, t) in enumerate([('symbian', 'remained important', L(2)), ('meego', 'another attempt at a modern smartphone platform', L(3)), ('services · maps', 'and new user experiences', L(4))]):
        y = 190 + k * 235; hline(470, 560, y + 65, t, 30, t, t + .4)
        card_box(560, y, 760, 130, t, 30); heading(a_, 600, y + 20, 48, t, 30); text(b_, 600, y + 82, 26, t, 30, col=GREY, font='outfit500')
    photo('n9', 1400, 190, 460, 560, L(3), 30, PH_TAG['n9'])
    text('RESOURCES · MANAGEMENT ATTENTION · HARD PRIORITIES', 1400, 780, 20, L(7), 30, col=GREY, font='mono600')
    text('nokia recognized the need for change', 60, 830, 32, L(5), 30, col=GREY, font='outfit500')
    heading('recognizing change  ≠  a unified response', 60, 880, 52, L(6), 30, col=RED)
    text('the market: less forgiving', 60, 970, 30, L(8), 30, col=GREY, font='outfit500')
    text('the longer the transition, the harder the catch-up', 700, 970, 30, L(9), 30, col=TXT, font='outfit500')

# ═══════════════════════════ ACT 04 · THE DECISION ═══════════════════════════
@scene(9, 'a new ceo', 'act 04 · the decision')
def s09():
    photo('elop', 60, 150, 810, 540, 0, 30, PH_TAG['elop'], fx=.38, fy=.5, z0=1.25, z1=1.32)
    text('SEPTEMBER 2010', 940, 150, 30, L(1), 30, col=RED, font='mono600'); heading('stephen elop becomes', 940, 190, 52, L(1), 30); heading('president & ceo', 940, 250, 52, L(1, .3), 30)
    doc('doc_elop', 940, 340, 760, L(1, 1.0), 30, hls=(L(1, 1.8),))
    text('enormous assets · a rapidly deteriorating position in high-end smartphones', 60, 720, 26, L(2), 30, col=GREY, font='outfit500', wrap=810)
    heading('not whether to change —', 940, 590, 44, L(3), 30, col=GREY); heading('but how', 1460, 590, 44, L(4), 30, col=RED)
    opts = [('OPTION A', 'its own platforms', L(5)), ('OPTION B', 'embrace android', L(6)), ('OPTION C', 'a different partnership', L(7))]
    for k, (a_, b_, t) in enumerate(opts):
        x = 60 + k * 610; card_box(x, 800, 580, 150, t, 30, edge=GREY); text(a_, x + 36, 826, 22, t, 30, col=GREY, font='mono600'); heading(b_, x + 36, 866, 44, t, 30)
    text('EACH OPTION CARRIED RISK', 60, 975, 20, L(8), 30, col=GREY, font='mono600')
    rect(1280, 944, 580, 6, RED, L(9), 30, grow=(L(9), L(9, .6), 'x')); check(1790, 816, L(9), size=56)

@scene(10, 'the microsoft bet')
def s10():
    text('FEBRUARY 11, 2011', 60, 150, 30, L(1), 30, col=RED, font='mono600'); heading('nokia + microsoft', 60, 190, 72, L(1), 30)
    doc('doc_ms', 60, 320, 860, L(1, 1.0), 30, hls=(L(1, 1.8),))
    heading('windows phone', 1000, 180, 72, L(2), 30, col=RED); text("becomes nokia's primary smartphone platform", 1004, 270, 30, L(2, .4), 30, font='outfit500')
    text('THE LOGIC', 1000, 360, 22, L(3), 30, col=GREY, font='mono600')
    for k, (a_, items, t) in enumerate([('NOKIA', ['hardware', 'distribution', 'design'], L(4)), ('MICROSOFT', ['software', 'services', 'ecosystem'], L(5))]):
        x = 1000 + k * 440; card_box(x, 400, 420, 300, t, 30, edge=RED if k == 0 else GREY)
        text(a_, x + 36, 426, 24, t, 30, col=RED if k == 0 else GREY, font='mono600')
        for j, s_ in enumerate(items): heading(s_, x + 36, 480 + j * 66, 40, t + j * .4, 30)
    heading('a third ecosystem — against apple and android', 1000, 750, 36, L(6), 30)
    text('nokia committed its smartphone future to a platform without comparable market scale', 60, 680, 30, L(7), 30, col=GREY, font='outfit500', wrap=860)
    heading('a strategic gamble.', 60, 870, 80, L(8), 30, col=RED); EV.append((T(L(8)), 'impact'))

@scene(11, 'the transition trap')
def s11():
    heading('an immediate problem', 60, 150, 52, L(1), 30)
    for k, (a_, b_, t) in enumerate([('TODAY', 'symbian phones', L(2)), ('LATER', 'windows phone', L(2, .8))]):
        x = 60 + k * 500; card_box(x, 250, 420, 130, t, 30, edge=GREY if k == 0 else RED); text(a_, x + 36, 272, 22, t, 30, col=GREY, font='mono600'); heading(b_, x + 36, 310, 44, t, 30)
    hline(486, 556, 315, L(2, .4), 30, L(2, .4), L(2, .8))
    text('the announcement made the future direction clear', 60, 410, 28, L(3), 30, col=GREY, font='outfit500')
    strike(90, 335, 360, L(4)); text('symbian: no longer the long-term centrepiece', 60, 456, 28, L(4), 30, col=RED, font='outfit500')
    doc('doc_sym', 1000, 150, 860, L(5), 30, hls=(L(5, .8), L(5, 1.4)))
    text('NOKIA SMARTPHONE SHIPMENTS', 60, 508, 22, L(6), 30, col=GREY, font='mono600')
    base = 920; k_ = 3.8
    for k, (yr, v, lab, t) in enumerate([('2011', 77.3, '77.3M', L(6)), ('2012', 35.0, '≈ 35M', L(7))]):
        x = 100 + k * 320; bar(x, base, 220, v * k_, GREY if k == 0 else RED, t)
        heading(lab, x + 110, base - v * k_ - 64, 44, t + .6, 30, al='CENTER'); text(yr, x + 110, base + 14, 26, t, 30, col=GREY, font='mono600', al='CENTER')
    text('nokia form 20-f 2011 & 2012 · all smartphones, symbian and windows phone', 60, 990, 18, L(6), 30, col=GREY, font='mono400')
    heading('the new products needed time', 1000, 520, 40, L(6), 30, col=GREY); heading('the old products were losing momentum', 1000, 580, 40, L(7), 30)
    heading('caught between two generations of its own strategy', 1000, 720, 48, L(8), 30, col=RED); CX.m.sequences[-1].wrap_width = 860 / W; EV.append((T(L(8)), 'low'))

@scene(12, 'the lumia gamble')
def s12():
    photo('lumia800', 60, 150, 620, 760, 0, 30, PH_TAG['lumia800'], fx=.5, fy=.5, z0=1.0, z1=1.04)
    text('OCTOBER 26, 2011 · NOKIA WORLD, LONDON', 760, 150, 26, L(1), 30, col=RED, font='mono600'); heading('lumia 800 & lumia 710', 760, 190, 64, L(1), 30)
    text("nokia's first windows phone smartphones", 764, 280, 30, L(1, .5), 30, col=GREY, font='outfit500')
    chips(['distinctive industrial design', 'imaging', "microsoft's mobile software"], 760, 360, L(2), dt=.7, size=34, gap=62)
    text('not poorly made phones · serious hardware expertise', 760, 580, 30, L(3), 30, font='outfit500')
    heading("strong hardware wasn't enough", 760, 640, 44, L(5), 30, col=RED)
    for k, (a_, b_, t) in enumerate([('apple', 'ios · an established ecosystem', L(6)), ('google', 'android · an established ecosystem', L(6, .6)), ('nokia + microsoft', 'windows phone · persuade people to join a third platform', L(7))]):
        y = 740 + k * 50; text(a_.upper(), 760, y + 4, 22, t, 30, col=RED if k == 2 else GREY, font='mono600'); text(b_, 1060, y, 28, t, 30, col=TXT, font='outfit500')
    heading('platform competition rewards momentum.', 760, 920, 48, L(8), 30, col=RED); EV.append((T(L(8)), 'low'))

# ═══════════════════════════ ACT 05 · THE COLLAPSE ═══════════════════════════
@scene(13, 'the numbers turn', 'act 05 · the collapse')
def s13():
    heading("nokia's own reporting", 60, 150, 52, L(1), 30)
    doc('doc_share', 1000, 150, 860, L(1, .6), 30, hls=(L(1, 1.4), L(2, 1.0)))
    text('ESTIMATED GLOBAL MOBILE DEVICE VOLUME SHARE', 60, 240, 22, L(1, .5), 30, col=GREY, font='mono600')
    base = 860; k_ = 11
    for k, (yr, v, t) in enumerate([('2007', 38, L(1, .8)), ('2010', 32, L(2)), ('2011', 27, L(2, .7)), ('2012', 21, L(3))]):
        x = 80 + k * 220; bar(x, base, 150, v * k_, RED if k == 3 else GREY, t)
        heading(f'{v}%', x + 75, base - v * k_ - 62, 44, t + .6, 30, al='CENTER'); text(yr, x + 75, base + 14, 26, t, 30, col=GREY, font='mono600', al='CENTER')
    text('2007, 2010: nokia estimates · 2011, 2012: strategy analytics, as reported in nokia\'s 2012 20-f', 60, 930, 18, L(3), 30, col=GREY, font='mono400')
    chips(['declining symbian demand', 'pressure on selling prices', 'a difficult platform transition'], 1000, 470, L(2), dt=.8, size=32, gap=56)
    text('still selling millions of phones', 1000, 680, 30, L(3), 30, col=GREY, font='outfit500')
    heading('scale  ≠  leadership', 1000, 730, 48, L(4), 30, col=RED)
    text('customers moved toward competing ecosystems', 1000, 810, 28, L(5), 30, font='outfit500')
    text('it had to rebuild in a market that had already moved', 1000, 856, 28, L(7), 30, col=GREY, font='outfit500')
    heading('time had become its scarcest resource.', 1000, 940, 40, L(8), 30, col=RED); EV.append((T(L(8)), 'low'))

@scene(14, 'the sale')
def s14():
    text('SEPTEMBER 3, 2013 · ANNOUNCED', 60, 150, 26, L(1), 30, col=GREY, font='mono600')
    doc('doc_deal', 60, 190, 820, L(1, .3), 30, hls=(L(1, 1.0),))
    heading('€5.44B', 1000, 150, 160, L(2), 30); text('approximately · including patent-related arrangements', 1004, 330, 24, L(2, .4), 30, col=GREY, font='mono600')
    text('€3.79B   devices & services business', 1004, 380, 28, L(2, 1.0), 30, font='mono600'); text('€1.65B   patent licence and future option', 1004, 426, 28, L(2, 1.4), 30, font='mono600')
    text('APRIL 25, 2014 · COMPLETED', 60, 470, 26, L(3), 30, col=RED, font='mono600')
    doc('doc_close', 60, 510, 820, L(3, .3), 30, hls=(L(3, 1.0),)); EV.append((T(L(3, 1.0)), 'impact'))
    text('NOKIA RETAINED', 1000, 520, 22, L(4), 30, col=GREY, font='mono600')
    chips(['networks', 'here maps', 'advanced technologies & patents'], 1000, 560, L(4), dt=.7, size=34, gap=62)
    text('a major telecommunications technology company', 1000, 770, 30, L(5), 30, font='outfit500')
    rect(60, 860, 1800, 2, RULE, L(6), 30)
    heading('the era of the nokia handset empire: ended', 960, 900, 52, L(6), 30, col=RED, al='CENTER')

# ═══════════════════════════ ACT 06 · THE AUTOPSY ═══════════════════════════
@scene(15, 'what actually killed the empire?', 'act 06 · the autopsy')
def s15():
    heading("what destroyed nokia's handset dominance?", 960, 180, 56, L(1), L(6), al='CENTER')
    for k, s_ in enumerate(['not one phone', 'not one competitor', 'not one executive decision']):
        heading(s_, 960, 330 + k * 70, 44, L(2 + k), L(6), col=GREY, al='CENTER')
    heading('an accumulation of problems', 960, 620, 80, L(5), L(6), col=RED, al='CENTER'); EV.append((T(L(5)), 'impact'))
    CX.beat()
    text('THE FINDINGS', 60, 150, 24, L(6), 30, col=GREY, font='mono600')
    for k, (s_, t) in enumerate([('legacy software complexity', L(6)), ('slow execution during a fundamental market transition', L(7)), ('fragmented platform development', L(8)), ('a late commitment to an ecosystem that struggled to match its rivals', L(9))]):
        y = 200 + k * 105; card_box(60, y, 1800, 88, t, 30); check(90, y + 16, t, size=48); heading(s_, 170, y + 20, 42, t, 30)
    heading('hardware strengths: real', 60, 660, 40, L(10), 30)
    heading('the competitive advantage: moved', 960, 660, 40, L(11), 30, col=RED)
    text('it could still build impressive phones', 60, 780, 32, L(12), 30, col=GREY, font='outfit500')
    heading('it could no longer reliably win the platform battle', 60, 850, 56, L(13), 30, col=RED)

@scene(16, 'the verdict')
def s16():
    heading('a warning for every market leader', 960, 200, 44, L(1), L(4), al='CENTER', col=GREY)
    heading('dominance is evidence of past success', 960, 340, 64, L(2), L(4), al='CENTER')
    heading('not proof of future relevance', 960, 440, 64, L(3), L(4), al='CENTER', col=RED)
    CX.beat()
    heading("the greatest danger isn't always failing to see change", 960, 200, 44, L(4), L(9), al='CENTER', col=GREY)
    for k, (s_, t) in enumerate([('recognize change', L(5)), ('invest in it', L(5, .7)), ('move too slowly', L(5, 1.4))]):
        heading(s_, 340 + k * 620, 360, 52, t, L(9), al='CENTER', col=RED if k == 2 else TXT)
        if k: hline(340 + (k - 1) * 620 + 200, 340 + k * 620 - 210, 392, t - .3, L(9), t - .3, t)
    heading("nokia didn't disappear", 960, 560, 56, L(6), L(9), al='CENTER'); text('it reinvented itself beyond handsets', 960, 640, 34, L(7), L(9), col=GREY, font='outfit500', al='CENTER')
    heading("its strongest capabilities  ≠  the market's most important demands", 960, 800, 40, L(8), L(9), al='CENTER', col=RED)
    CX.beat()
    e = heading('brand coroner', 943, 420, 110, L(9), 30, al='CENTER'); e2 = text('.', 1305, 420, 110, L(9, .8), 30, col=RED)
    f = text('EVERY BRAND LEAVES EVIDENCE.', 960, 570, 36, L(9, .4), 30, col=GREY, font='outfit500', al='CENTER')
    rect(810, 555, 300, 2, RED, L(9, .2), 30, grow=(L(9, .2), L(9, 1.0), 'x'))
    for st in (e, e2, f): fade(st, L(9), 30, 1, .6, 2.0)
