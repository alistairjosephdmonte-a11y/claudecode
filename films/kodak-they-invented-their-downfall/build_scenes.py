# ── Kodak scene designs. Authored on a 0–30 s grid per scene; L(k) is the grid time of narration line k, and
#    vo/timeline.json warps every grid onto the voiceover so each beat lands on its line. ──
def L(k, d=0.0): return 1.0 + 27.0 * (k - 1) / CX.n + d
def have(k): return os.path.exists(os.path.join(A, k + '.png'))
SA = {k for k, v in json.load(open(os.path.join(D, 'photos.json'))).items() if v.get('sa')}
def chips(items, x, y, t, dt=.8, t1=30, col=TXT, size=34, gap=70, bar=RED):
    for k, s_ in enumerate(items):
        rect(x, y + k * gap + size * .25, 8, size * .85, bar, t + k * dt, t1); heading(s_, x + 26, y + k * gap, size, t + k * dt, t1, col=col)
def photo(k, x, y, w, h, t0, t1, tagtxt, **kw):
    """graded photo (cover crop, optional push). CC BY-SA photos are shown unaltered: whole frame, contained, no crop or push."""
    if not have('ph_' + k): rect(x, y, w, h, PANEL, t0, t1); text('[photo unavailable]', x + 20, y + 20, 20, t0, t1, col=GREY, font='mono400'); return None
    if k in SA:
        rect(x, y, w, h, '#101010', t0, t1); kw = {'contain': True}
    im = image('ph_' + k, x, y, w, h, t0, t1, **kw); tag(tagtxt, x, y - 26, t0, t1); EV.append((T(t0), 'shutter')); return im
def hline(x0, x1, y, t0, t1, ta, tb, col=RED, th=4, head=True):
    if x1 >= x0: rect(x0, y - th / 2, x1 - x0, th, col, t0, t1, grow=(ta, tb, 'x'))
    else: rect(x1, y - th / 2, x0 - x1, th, col, t0, t1, grow=(ta, tb, 'xr'))
    if head: sprite(f"arrow_{'red' if col == RED else 'grey'}_{'r' if x1 >= x0 else 'l'}", x1, y, tb, t1)
def up(s, y, h):          # make a 'y'-grown rect grow upward from its bottom edge
    s.transform.origin = (0, 0); s.transform.offset_y = H - y - h; return s
def vline(x, y0, y1, t0, t1, ta, tb, col=RED, th=4, head=True):
    top, h = min(y0, y1), abs(y1 - y0); s = rect(x - th / 2, top, th, h, col, t0, t1, grow=(ta, tb, 'y'))
    if y1 < y0: up(s, top, h)
    if head: sprite(f"arrow_{'red' if col == RED else 'grey'}_{'d' if y1 >= y0 else 'u'}", x, y1, tb, t1)
def card_box(x, y, w, h, t0, t1, edge=RED):
    rect(x, y, w, h, PANEL, t0, t1); rect(x, y, 6, h, edge, t0, t1)
def check(x, y, t, t1=30, ok=True, size=44):
    text('✓' if ok else '✕', x, y, size, t, t1, col=RED, font='outfit700'); EV.append((T(t), 'mark'))

# ═══════════════════════════ ACT 01 · THE INVENTION ═══════════════════════════
@scene(1, 'the camera that shouldn’t have existed', 'act 01 · the invention')
def s01():
    rect(560, 538, 800, 4, RED, .3, L(1), grow=(.3, 1.6, 'x')); EV.append((T(.3), 'tape'))
    heading('1975', 960, 330, 300, L(1, -.6), L(2), al='CENTER'); EV.append((T(L(1, -.6)), 'shutter'))
    text('kodak laboratory · rochester, new york', 960, 690, 30, L(1), L(2), col=GREY, font='mono600', al='CENTER')
    CX.beat()
    photo('proto', 60, 140, 820, 820, L(2), 30, 'drawing of the 1975 prototype · b. labévue 2022 · cc by-sa 4.0 · not a photograph')
    photo('sasson', 1480, 140, 380, 480, L(1, 3.0), 30, 'steven sasson · photokina 2010 · aljawad · cc by 3.0', fx=.5, fy=.3)
    text('1975', 960, 130, 30, L(2), 30, col=RED, font='mono600'); heading('the prototype', 960, 166, 56, L(2), 30)
    specs = [('≈ 8 POUNDS', L(2, .4)), ('BLACK-AND-WHITE IMAGES', L(2, 2.0)), ('MAGNETIC TAPE RECORDING', L(2, 3.4)), ('100 × 100 PIXELS', L(3))]
    for k, (s_, t) in enumerate(specs):
        y = 280 + k * 84; card_box(960, y, 480, 68, t, 30); heading(s_, 990, y + 16, 30, t, 30); EV.append((T(t), 'mark'))
    text('= 10,000 pixels', 1450, 535, 24, L(3, .6), 30, col=GREY, font='mono400', al='RIGHT')
    heading('primitive.', 960, 660, 52, L(4), 30, col=GREY); heading('revolutionary.', 1240, 660, 52, L(5), 30, col=RED)
    heading('a camera without photographic film', 960, 760, 44, L(6), 30)
    rect(960, 820, 760, 4, RED, L(6, .4), 30, grow=(L(6, .4), L(6, 1.4), 'x'))
    heading('built by kodak.', 960, 860, 60, L(7), 30, col=RED); EV.append((T(L(7)), 'low'))

@scene(2, 'the contradiction')
def s02():
    photo('tower', 60, 140, 760, 820, 0, 30, 'photo · kodak tower, rochester, ny · 2009 · mark a. lackey · cc by 2.0', fx=.5, fy=.4, z0=1.0, z1=1.08)
    text('THIRTY-SEVEN YEARS LATER', 900, 140, 24, L(1), L(3), col=GREY, font='mono600')
    heading('january 19, 2012', 900, 176, 88, L(1, .8), L(3), col=TXT); rect(900, 290, 720, 6, RED, L(1, 1.6), L(3), grow=(L(1, 1.6), L(1, 2.6), 'x'))
    heading('chapter 11 bankruptcy protection', 900, 320, 40, L(1, 2.2), L(3), col=RED)
    doc('doc_ch11', 900, 420, 960, L(1, 3.0), L(3), hls=(L(1, 4.0), L(2)))
    text('1975: digital innovation  →  2012: bankruptcy protection', 900, 800, 28, L(2), L(3), font='mono600', col=GREY)
    CX.beat()
    text('THE POPULAR EXPLANATION', 900, 160, 24, L(3), 30, col=GREY, font='mono600')
    for k, s_ in enumerate(['invented the digital camera', 'ignored it', 'paid the price']):
        heading(s_, 900, 220 + k * 80, 52, L(4, k * .9), 30, col=GREY if k != 1 else TXT)
    rect(890, 335, 280, 5, RED, L(5), 30, grow=(L(5), L(5, .8), 'x')); text('not quite', 1190, 318, 30, L(5, .6), 30, col=RED, font='mono600'); EV.append((T(L(5)), 'mark'))
    heading('kodak invested in digital.', 900, 520, 64, L(7), 30, col=RED); EV.append((T(L(7)), 'low'))
    heading('how did kodak see the future —', 900, 700, 48, L(9), 30)
    heading('and still lose its position in it?', 900, 760, 48, L(9, 1.2), 30, col=RED)

# ═══════════════════════════ ACT 02 · THE EMPIRE ═══════════════════════════
@scene(3, 'the company that owned memories', 'act 02 · the empire')
def s03():
    ads = [('ad1921', 'eastman kodak advertisement · 1921 · public domain'), ('asyougo', 'photoplay · jan 1921 · public domain'), ('vacation', 'canadian kodak advertisement · aug 1922 · public domain')]
    for k, (a_, tg) in enumerate(ads):
        photo(a_, 60 + k * 610, 150, 580, 760, L(1, k * 1.2), L(4), tg, contain=True)
    CX.beat()
    for k, (p_, tg) in enumerate([('instamatic', 'kodak pocket instamatic 200 · delaville · cc by 2.0'), ('verichrome', 'kodak verichrome pan 120 · kevinfarrugia · cc0'), ('film', 'kodak ultramax 400 · veera.sj 2018 · cc0')]):
        photo(p_, 60 + k * 610, 150, 580, 440, L(3, k * .8), 30, tg, fx=.5, fy=.5, z0=1.0, z1=1.05)
    for k, s_ in enumerate(['CAMERAS', 'FILM', 'PAPER', 'PROCESSING']):
        x = 60 + k * 455; card_box(x, 640, 430, 80, L(3, .4 + k * .7), 30); heading(s_, x + 30, 660, 36, L(3, .4 + k * .7), 30); EV.append((T(L(3, .4 + k * .7)), 'mark'))
    rect(1280, 592, 520, 5, '#E8B400', L(4), 30, grow=(L(4), L(4, .8), 'x')); text('the yellow box', 1280, 604, 22, L(4, .4), 30, col='#E8B400', font='mono600')
    heading('the system around every photograph', 60, 800, 56, L(6), 30, col=RED)
    text('→ customers kept buying', 64, 880, 34, L(7), 30, font='outfit500'); EV.append((T(L(6)), 'low'))

@scene(4, 'the perfect business model')
def s04():
    text('conceptual business model · not a revenue analysis', 60, 84, 20, 0, 30, col=GREY, font='mono400')
    N = [('BUY A CAMERA', L(2)), ('BUY FILM', L(3)), ('DEVELOP & PRINT', L(4)), ('BUY MORE FILM', L(5))]
    X = [100, 560, 1020, 1480]
    for k, ((s_, t), x) in enumerate(zip(N, X)):
        card_box(x, 300, 360, 150, t, 30, edge=GREY if k == 0 else RED); heading(s_, x + 180, 350, 34, t, 30, al='CENTER'); EV.append((T(t), 'advance'))
        if k: hline(X[k - 1] + 360, x - 6, 375, t - .5, 30, t - .5, t)
    text('one-time purchase', 280, 470, 24, L(2, 1), 30, col=GREY, font='mono600', al='CENTER')
    # recurring loop: from BUY MORE FILM back to DEVELOP & PRINT
    vline(1660, 450, 600, L(6), 30, L(6), L(6, .6), head=False); hline(1660, 1200, 600, L(6), 30, L(6, .6), L(6, 1.4), head=False)
    vline(1200, 600, 456, L(6), 30, L(6, 1.4), L(6, 2.0))
    text('recurring demand', 1430, 616, 26, L(6, 1.4), 30, col=RED, font='mono600', al='CENTER'); EV.append((T(L(6)), 'draw'))
    heading('an extraordinarily attractive structure', 100, 700, 48, L(7), 30)
    text('it depended on one thing:', 100, 800, 30, L(8), 30, col=GREY, font='outfit500')
    heading('people had to keep using physical film', 100, 850, 52, L(9), 30, col=RED)
    rect(1650, 492, 20, 60, BG, L(10), 30); text('✕', 1660, 490, 56, L(10), 30, col=RED, font='outfit700', al='CENTER'); EV.append((T(L(10)), 'break'))
    text('digital removes the requirement', 1430, 652, 22, L(10, .5), 30, col=RED, font='mono600', al='CENTER')

# ═══════════════════════════ ACT 03 · THE WARNING ═══════════════════════════
@scene(5, 'the future inside the building', 'act 03 · the warning')
def s05():
    for k, s_ in enumerate(['LIGHT', 'ELECTRONIC SENSOR', 'DIGITAL INFORMATION']):
        x = 100 + k * 600; t = L(1, k * 1.0); card_box(x, 160, 520, 110, t, 30, edge=RED if k == 2 else GREY); heading(s_, x + 260, 196, 36, t, 30, al='CENTER')
        if k: hline(x - 80, x - 6, 215, t - .4, 30, t - .4, t)
    for k, s_ in enumerate(['no chemical development', 'no conventional film negative', 'no print required to see the image']):
        y = 360 + k * 80; check(100, y - 6, L(2 + k), ok=False); heading(s_, 170, y, 42, L(2 + k), 30)
    text('THE LIMITS IN 1975', 1100, 340, 24, L(5), 30, col=GREY, font='mono600')
    chips(['bulky · ≈ 8 lb', 'limited quality · 100 × 100, b&w', 'slow storage · ≈ 23 s per image to tape'], 1100, 390, L(6), dt=1.0, size=30, gap=60, bar=GREY, col=GREY)
    text('23 s: reported time to record one image', 1100, 580, 18, L(6, 2), 30, col=GREY, font='mono400')
    # 1975 → decades of digital development
    rect(100, 760, 1720, 3, GREY, L(7), 30, grow=(L(7), L(8), 'x')); sprite('dot_red', 100, 761, L(7), 30); text('1975', 100, 780, 26, L(7), 30, col=RED, font='mono600')
    for yr in (1985, 1995, 2005): sprite('dot_grey', 100 + (yr - 1975) / 37 * 1720, 761, L(8), 30); text(str(yr), 100 + (yr - 1975) / 37 * 1720, 780, 22, L(8), 30, col=GREY, font='mono400', al='CENTER')
    text('kodak keeps developing digital imaging', 960, 700, 28, L(8), 30, font='outfit500', al='CENTER')
    heading('the question was the business, not the possibility', 960, 870, 48, L(9), 30, col=RED, al='CENTER'); EV.append((T(L(9)), 'low'))

@scene(6, 'the profit trap')
def s06():
    text('illustrative comparison · no margin figures implied', 60, 84, 20, 0, 30, col=GREY, font='mono400')
    rect(958, 130, 4, 760, RULE, 0, 30)
    heading('film economics', 100, 150, 56, L(1), 30); text('RECURRING REVENUE', 100, 222, 24, L(1), 30, col=RED, font='mono600')
    items = ['film sales', 'development', 'printing', 'repeat purchases']
    for k, s_ in enumerate(items):
        y = 300 + k * 90; check(100, y - 4, L(1, 1 + k * .7)); heading(s_, 170, y, 44, L(1, 1 + k * .7), 30)
    heading('digital economics', 1020, 150, 56, L(2), 30, col=GREY); text('ONE-TIME HARDWARE', 1020, 222, 24, L(2), 30, col=GREY, font='mono600')
    for k, s_ in enumerate(['electronic capture', 'digital storage', 'screen viewing', 'electronic sharing']):
        y = 300 + k * 90; heading(s_, 1020, y, 44, L(2, .6 + k * .6), 30, col=GREY)
    for k in range(3):     # recurring streams threatened
        y = 300 + k * 90; rect(160, y + 30, 420, 5, RED, L(5, k * .5), 30, grow=(L(5, k * .5), L(5, k * .5 + .6), 'x')); EV.append((T(L(5, k * .5)), 'mark'))
    text('threatened', 600, 390, 28, L(5, 1.6), 30, col=RED, font='mono600')
    heading('same profitability? not automatically.', 100, 720, 44, L(7), 30, col=GREY)
    heading('two economic worlds at once', 960, 850, 60, L(8), 30, col=RED, al='CENTER'); EV.append((T(L(8)), 'low'))

# ═══════════════════════════ ACT 04 · THE DIGITAL REVOLUTION ═══════════════════════════
@scene(7, 'the myth of ignoring digital', 'act 04 · the digital revolution')
def s07():
    heading('the myth of ignoring digital', 60, 130, 56, L(1), 30, col=GREY)
    rect(60, 210, 1800, 3, RULE, L(1), 30)
    M = [('1991', 'kodak professional digital camera system', 'dcs · nikon f3 body + storage unit', L(3)),
         ('1995', 'kodak dc40', 'consumer digital camera · launched march 1995', L(4)),
         ('2001', 'kodak easyshare', 'consumer digital camera system', L(5))]
    for k, (yr, a_, b_, t) in enumerate(M):
        y = 250 + k * 170; card_box(60, y, 1800, 140, t, 30); check(100, y + 38, t, size=56)
        heading(yr, 180, y + 30, 64, t, 30, col=RED); heading(a_, 420, y + 28, 44, t, 30); text(b_, 420, y + 88, 24, t, 30, col=GREY, font='mono400')
    heading('kodak did invest in digital.', 60, 800, 64, L(6), 30); EV.append((T(L(6)), 'low'))
    heading('entering a market  ≠  a profitable position in it', 60, 900, 44, L(8), 30, col=RED)

@scene(8, 'the digital products')
def s08():
    P = [('dcs', 'dcs 100 + storage unit · john · cc by 2.0', 'DCS 100 · 1991', L(1, -.5)),
         ('dc40', 'dc40 · nsmm · geni 2025 · cc by-sa 4.0', 'DC40 · 1995', L(1, 1.0)),
         ('easyshare', 'easyshare cx7330 · sgroey · cc by-sa 4.0', 'EASYSHARE CX7330 · LINE FROM 2001', L(2))]
    for k, (p_, tg, lab, t) in enumerate(P):
        x = 60 + k * 610; photo(p_, x, 150, 580, 520, t, 30, tg, fx=.5, fy=.5, z0=1.0, z1=1.04); text(lab, x, 690, 24, t, 30, col=RED, font='mono600')
    text('professional systems  →  consumer convenience', 60, 740, 26, L(2, 1), L(4), col=GREY, font='mono600')
    text('kodak also invested in digital printing and imaging technologies', 60, 740, 26, L(3), L(4), col=GREY, font='mono600')
    for k, s_ in enumerate(['price pressure', 'fast technology cycles', 'more choices for customers']):
        x = 60 + k * 610; t = L(5 + k); card_box(x, 790, 580, 76, t, 30); heading(s_, x + 30, 806, 36, t, 30); EV.append((T(t), 'mark'))
    heading('participation  ≠  control of the economics', 60, 920, 48, L(8), 30, col=RED)

@scene(9, 'the market changes')
def s09():
    photo('z740', 60, 150, 900, 760, 0, 30, 'photo · kodak easyshare z740, lcd image-info screen · cc by-sa 4.0')
    for k, s_ in enumerate(['TAKE', 'STORE', 'SHARE', 'VIEW']):
        y = 160 + k * 100; t = L(2, k * .9) if k < 1 else L(3, (k - 1) * .9); check(1040, y, t); heading(s_, 1110, y, 56, t, 30)
    rect(1040, 570, 780, 110, RED, L(3, 3.2), 30); heading('NO FILM REQUIRED', 1430, 596, 52, L(3, 3.2), 30, col=BG, al='CENTER'); EV.append((T(L(3, 3.2)), 'low'))
    for k, s_ in enumerate(['film', 'chemicals', 'paper']):
        x = 1040 + k * 270; heading(s_, x, 720, 40, L(4, k * .4), 30, col=GREY); rect(x - 6, 745, 200, 4, RED, L(4, k * .4 + .4), 30, grow=(L(4, k * .4 + .4), L(4, k * .4 + 1.0), 'x'))
    text('the photographic supply chain under pressure', 1040, 800, 24, L(5), 30, col=GREY, font='mono600')
    heading('replace an entire economic system', 1040, 860, 40, L(7), 30, col=RED)

@scene(10, 'the missing economics')
def s10():
    photo('lineup', 60, 150, 900, 640, 0, 30, 'photo · kodak easyshare z700 ×4 and c433 · jj harrison · cc by-sa 3.0')
    heading('invention  ≠  attractive returns', 1020, 140, 48, L(2), 30, col=RED)
    text('KODAK HAD', 1020, 240, 22, L(3), 30, col=GREY, font='mono600'); heading('expertise · patents · a global brand', 1020, 274, 36, L(3), 30)
    text('DIGITAL DEMANDED DIFFERENT', 1020, 360, 22, L(4), 30, col=GREY, font='mono600')
    chips(['capabilities', 'investments', 'sources of profit'], 1020, 400, L(4, .6), dt=.8, size=34, gap=62)
    heading('meanwhile: film declining', 1020, 620, 40, L(5), 30, col=GREY); vline(1600, 600, 680, L(5), 30, L(5, .3), L(5, 1.0), col=RED)
    text('fund the new  ·  manage the decline of the old', 60, 850, 30, L(6), 30, font='outfit500')
    heading('financial pressure', 60, 910, 60, L(7), 30, col=RED); EV.append((T(L(7)), 'low'))

# ═══════════════════════════ ACT 05 · THE COLLAPSE ═══════════════════════════
@scene(11, 'the financial evidence', 'act 05 · the collapse')
def s11():
    X0, Y0, Ytop, VMAX = 140, 860, 260, 8.0
    py = lambda v: Y0 - v / VMAX * (Y0 - Ytop)
    text('kodak net sales · continuing operations · $ billions · form 10-k fy2011', 140, 160, 20, 0, 30, col=GREY, font='mono400')
    for v in (0, 2, 4, 6, 8):
        rect(X0, py(v), 760, 1, '#262626' if v else GREY, .2, 30); text(str(v), X0 - 16, py(v) - 12, 20, .2, 30, col=GREY, font='mono400', al='RIGHT')
    for k, (yr, v, col) in enumerate([('2010', 7.167, GREY), ('2011', 6.022, RED)]):
        x = 240 + k * 340; t = L(2, k * 1.2)
        up(rect(x, py(v), 220, Y0 - py(v), col, t, 30, grow=(t, t + 1.0, 'y')), py(v), Y0 - py(v))
        heading(f'${v:.3f}B', x + 110, py(v) - 64, 44, t + 1.0, 30, al='CENTER'); text(yr, x + 110, Y0 + 14, 26, t, 30, col=GREY, font='mono600', al='CENTER'); EV.append((T(t), 'click'))
    doc('doc_k11', 1000, 150, 860, L(1, .5), 30, hls=(L(2), L(3)))
    rect(1000, 430, 860, 180, RED, L(3), 30); text('2011 NET LOSS ATTRIBUTABLE TO EASTMAN KODAK', 1030, 450, 22, L(3), 30, col=BG, font='mono600'); heading('$764M', 1030, 490, 96, L(3), 30, col=BG)
    text('a loss, not revenue: shown separately from the sales chart', 1000, 620, 20, L(3, .6), 30, col=GREY, font='mono400')
    doc('doc_mdna', 1000, 670, 860, L(4), 30, hls=(L(4, .6), L(4, 1.6), L(4, 2.6)))
    heading('not one product failing', 140, 940, 40, L(5), 30, col=RED)

@scene(12, 'the bankruptcy')
def s12():
    photo('building', 60, 140, 820, 820, 0, 30, 'photo · kodak building, rochester, ny · 2012 · viktor nagornyy · cc by 2.0', fx=.5, fy=.5, z0=1.0, z1=1.07)
    heading('january 19, 2012', 940, 150, 88, L(1), 30); rect(940, 262, 720, 6, RED, L(1, .8), 30, grow=(L(1, .8), L(1, 1.8), 'x'))
    heading('CHAPTER 11', 940, 300, 64, L(1, 1.2), 30, col=RED); EV.append((T(L(1)), 'impact'))
    text('eastman kodak company and its u.s. subsidiaries · s.d.n.y.', 940, 390, 24, L(1, 2), 30, col=GREY, font='mono600')
    for k, (s_, t, ok) in enumerate([('not the disappearance of the company', L(2), False), ('a legal reorganization process', L(3), True), ('kodak continued operating', L(4), True)]):
        y = 460 + k * 84; check(940, y - 4, t, ok=ok); heading(s_, 1010, y, 40, t, 30)
    heading('the symbol of photography’s future,', 940, 760, 40, L(6), 30, col=GREY)
    heading('restructuring in the digital age', 940, 812, 40, L(6, 1), 30, col=GREY)
    heading('it helped create the revolution.', 940, 890, 40, L(7), 30); heading('it did not transform around it.', 940, 942, 40, L(8), 30, col=RED)

# ═══════════════════════════ ACT 06 · THE RECKONING ═══════════════════════════
@scene(13, 'what kodak sold', 'act 06 · the reckoning')
def s13():
    heading('during restructuring', 60, 130, 48, L(1), 30, col=GREY)
    R = [('consumer digital-camera business', 'exit announced feb 9, 2012 · brand licensing instead', L(2)),
         ('online photo services', 'kodak gallery → shutterfly, 2012 (reported $23.8m)', L(3)),
         ('digital imaging patents', 'agreements dec 19, 2012 · ≈ $525m · not all kodak patents', L(4))]
    for k, (a_, b_, t) in enumerate(R):
        y = 220 + k * 150; card_box(60, y, 940, 124, t, 30); check(90, y + 30, t); heading(a_, 160, y + 22, 38, t, 30); text(b_, 160, y + 76, 20, t, 30, col=GREY, font='mono400')
    doc('doc_exit', 1060, 200, 800, L(2, .5), L(4), hls=(L(2, 1.5),))
    doc('doc_patent', 1060, 200, 800, L(4), 30, hls=(L(4, .8), L(4, 1.6)))
    text('CONCENTRATING ON', 60, 700, 22, L(5), 30, col=GREY, font='mono600')
    for k, s_ in enumerate(['commercial printing', 'packaging', 'imaging technologies']):
        heading(s_, 60 + k * 520, 740, 44, L(5, k * .6), 30)
    heading('the brand remained.', 60, 870, 56, L(7), 30); heading('the company changed.', 700, 870, 56, L(8), 30, col=RED)

@scene(14, 'what survived')
def s14():
    photo('magnus', 60, 140, 860, 560, 0, 30, 'photo · kodak magnus 800 platesetter · 2014 · frédéric bisson · cc by 2.0', fx=.5, fy=.5, z0=1.0, z1=1.06)
    rect(980, 140, 880, 190, RED, L(1), 30); text('SEPTEMBER 3, 2013', 1010, 162, 30, L(1), 30, col=BG, font='mono600'); heading('emerged from chapter 11', 1010, 212, 60, L(1, .4), 30, col=BG); EV.append((T(L(1)), 'low'))
    doc('doc_emerge', 980, 360, 880, L(1, 1.5), 30, hls=(L(1, 2.5), L(3)))
    heading('kodak had not vanished.', 60, 740, 48, L(2), 30)
    text('consumer imaging and document imaging businesses spun off to the kodak (uk) pension plan · kodak brand licensed to others', 60, 810, 22, L(4), 30, col=GREY, font='mono400', wrap=860)
    heading('photography didn’t disappear.', 980, 820, 44, L(5), 30)
    heading('the economics changed.', 980, 880, 56, L(7), 30, col=RED)

@scene(15, 'the real mistake')
def s15():
    heading('was inventing the threat the mistake?', 960, 140, 52, L(1), L(5), al='CENTER', col=GREY)
    heading('no.', 960, 300, 200, L(2), L(5), col=RED, al='CENTER'); EV.append((T(L(2)), 'impact'))
    heading('innovation wasn’t the mistake', 960, 600, 48, L(3), L(5), al='CENTER')
    CX.beat()
    rect(958, 140, 4, 640, RULE, L(5), 30)
    heading('they innovated', 100, 150, 56, L(5), 30)
    for k, (s_, t) in enumerate([('1975 prototype', L(5, .6)), ('professional digital cameras', L(6)), ('consumer digital cameras', L(6, .8)), ('imaging technology', L(7))]):
        y = 260 + k * 84; check(100, y - 4, t); heading(s_, 170, y, 40, t, 30)
    heading('the business did not', 1020, 150, 56, L(8), 30, col=RED); heading('reinvent itself', 1020, 210, 56, L(8), 30, col=RED)
    for k, s_ in enumerate(['film economics declining', 'digital price pressure', 'financial deterioration', 'restructuring']):
        y = 320 + k * 84; t = L(8, .6 + k * .5); check(1020, y - 4, t, ok=False); heading(s_, 1090, y, 40, t, 30)
    rect(100, 820, 1720, 120, PANEL, L(9), 30); heading('technological innovation  ≠  sustainable business transformation', 960, 856, 44, L(9), 30, al='CENTER', col=TXT)

@scene(16, 'the final verdict')
def s16():
    photo('film', 560, 120, 800, 800, 0, L(9), 'photo · kodak ultramax 400 · veera.sj 2018 · cc0', fx=.5, fy=.5, z0=1.0, z1=1.12, a=.85)
    heading('helped create the future · participated in it · struggled to survive it', 960, 940, 30, L(2), L(5), al='CENTER', col=GREY)
    rect(460, 340, 1000, 330, '#F0EDE6', L(6), L(9)); EV.append((T(L(6)), 'low'))
    for k, s_ in enumerate(['inventing the future', 'does not guarantee', 'owning it.']):
        heading(s_, 960, 370 + k * 96, 76, L(6, k * .5), L(9), col=BG if k < 2 else RED, al='CENTER')
    text('the documentary’s conclusion · not a quotation', 960, 690, 20, L(6, 1.5), L(9), col=GREY, font='mono400', al='CENTER')
    CX.beat()
    e = heading('brand coroner', 943, 420, 110, L(9), 30, al='CENTER'); e2 = text('.', 1305, 420, 110, L(9, .8), 30, col=RED)
    f = text('EVERY BRAND LEAVES EVIDENCE.', 960, 570, 36, L(9, .4), 30, col=GREY, font='outfit500', al='CENTER')
    rect(810, 555, 300, 2, RED, L(9, .2), 30, grow=(L(9, .2), L(9, 1.0), 'x'))
    for st in (e, e2, f): fade(st, L(9), 30, 1, .6, 2.0)
