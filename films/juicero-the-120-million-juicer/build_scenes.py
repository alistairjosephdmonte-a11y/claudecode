# ── Juicero scene designs. Authored on a 0–30 s grid per scene; L(k) is the grid time of narration line k, and
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

def squeeze_chart(x, y, t_oz, t_s, t1=30):
    text("JUICE · OUNCES", x, y, 18, t_oz, t1, col=GREY, font='mono600')
    for k, (lab, v, c) in enumerate([('machine', 8.0, GREY), ('by hand', 7.5, RED)]):
        yy = y + 36 + k * 56; tt = t_oz + k * .4
        rect(x, yy, v * 80, 38, c, tt, t1, grow=(tt, tt + .6, 'x')); text(f'{v:g} oz · {lab}', x + v * 80 + 16, yy + 6, 22, tt + .4, t1, font='mono600', col=c if c == RED else TXT)
    text("TIME · SECONDS (APPROX.)", x, y + 170, 18, t_s, t1, col=GREY, font='mono600')
    for k, (lab, v, c) in enumerate([('machine', 120, GREY), ('by hand', 90, RED)]):
        yy = y + 206 + k * 56; tt = t_s + k * .4
        rect(x, yy, v * 5, 38, c, tt, t1, grow=(tt, tt + .6, 'x')); text(f'~{v} s · {lab}', x + v * 5 + 16, yy + 6, 22, tt + .4, t1, font='mono600', col=c if c == RED else TXT)
    note("bloomberg's squeeze test, april 2017 · one reported demonstration · bars to scale", x, y + 330, t_oz, t1=t1, w=900, size=15)

# ═══════════════════════════ ACT 01 · THE PITCH ═══════════════════════════
@scene(1, 'the experiment', 'act 01 · the pitch')
def s01():
    heading('a four-hundred-dollar machine', 60, 170, 60, L(1), 30)
    text('beside it: a sealed packet of fruit and vegetables', 60, 260, 30, L(2), 30, col=GREY, font='outfit500')
    text('APRIL 2017 · BLOOMBERG', 60, 360, 24, L(3), 30, col=RED, font='mono600')
    heading('they squeezed the packet by hand', 60, 400, 44, L(4), 30)
    heading('juice came out.', 60, 470, 60, L(5), 30, col=RED); EV.append((T(L(5)), 'impact'))
    for k, (s_, t) in enumerate([('pressed by the machine', L(4)), ('squeezed by hand', L(5))]):
        card_box(1100, 360 + k * 120, 760, 100, t, 30, edge=RED if k else GREY); text(s_, 1130, 390 + k * 120, 30, t, 30, font='outfit500'); check(1790, 380 + k * 120, t + .3)
    money('RAISED · APPROXIMATELY', '$120 million', 60, 600, L(6), size=110, sub='capital raised by the startup — not money lost')
    heading('what exactly were customers paying for?', 60, 880, 50, L(7), 30, col=RED); EV.append((T(L(7)), 'low'))

@scene(2, 'the money behind the machine')
def s02():
    photo('sandhill22', 60, 190, 700, 476, 0, 30, PH_TAG['sandhill22'])
    doc('doc_investors', 820, 170, 1040, L(2), 30, hls=(L(2, .4), L(2, .8)))
    chips(['gv (google ventures)', 'kleiner perkins', 'campbell soup company'], 820, 560, L(2, 1.2), dt=.4, size=26, gap=46)
    text('experience in technology · consumer products · new businesses', 60, 710, 22, L(3), 30, col=GREY, font='mono600'); wrap(700)
    flow(['healthy living', 'connected appliance', 'convenience', 'recurring purchases'], 60, 780, 410, 100, 40, L(4), dt=.4)
    heading('an entire ecosystem around the daily habit of fresh juice', 60, 930, 38, L(6), 30, col=RED); wrap(1800); EV.append((T(L(6)), 'low'))

@scene(3, 'the man who wanted to change juice')
def s03():
    doc('doc_evans', 60, 170, 900, L(1), 30, hls=(L(1, .4), L(1, .8)))
    text('TRADITIONAL JUICING', 60, 430, 20, L(2), 30, col=RED, font='mono600')
    chips(['preparation', 'equipment', 'cleanup'], 60, 470, L(2, .2), dt=.4, size=30, gap=54)
    text('buying prepared juice: easier', 60, 660, 28, L(3), 30, col=GREY, font='outfit500')
    heading("juicero's offer: fresh juice at home — no loose ingredients, no juicer to clean", 1000, 190, 32, L(4), 30); wrap(860)
    check(1000, 340, L(5)); text('an understandable consumer problem', 1060, 350, 28, L(5), 30, font='outfit500')
    text('the controversial part: how they chose to solve it', 1000, 420, 28, L(6), 30, col=GREY, font='outfit500'); wrap(860)
    heading('a food preparation problem, approached as a technology platform', 60, 820, 40, L(7), 30, col=RED); wrap(1800); EV.append((T(L(7)), 'low'))

@scene(4, 'the seven-hundred-dollar solution')
def s04():
    text('SPRING 2016 · THE LAUNCH', 60, 150, 24, L(1), 30, col=RED, font='mono600')
    doc('doc_launch', 60, 190, 900, L(1, .3), 30, hls=(L(1, .7), L(2)))
    text('LAUNCH PRICE · THE PRESS', 1000, 180, 22, L(2), 30, col=GREY, font='mono600')
    heading('$699', 1000, 215, 200, L(2, .2), 30, col=RED); EV.append((T(L(2, .2)), 'impact'))
    flow(['proprietary produce packet', 'the press', 'juice in a glass'], 60, 520, 560, 100, 50, L(3), dt=.5)
    note('illustrative', 60, 630, L(3), w=300, size=15)
    text('designed for cleaner, more consistent juicing', 60, 690, 28, L(5), 30, font='outfit500')
    heading('first: convince customers to buy an unusually expensive appliance', 60, 830, 40, L(6), 30, col=RED); wrap(1800); EV.append((T(L(6)), 'low'))

@scene(5, 'the real business was inside the bag')
def s05():
    photo('produce26', 60, 190, 760, 429, 0, 30, PH_TAG['produce26'])
    doc('doc_packs', 900, 190, 960, L(2), 30, hls=(L(2, .4), L(3)))
    text('like coffee capsules or printer cartridges?', 900, 495, 28, L(4), 30, font='outfit500'); wrap(960)
    boxes([('shelf-stable consumables', L(5), GREY), ('fresh produce: it deteriorates', L(6), RED)], 900, 555, 460, 110, 40, size=26)
    chips(['careful handling', 'dependable distribution'], 60, 690, L(7), dt=.4, size=28, gap=50)
    boxes([('a reason to buy the machine', L(8), GREY), ('a reason to keep buying the packets', L(9), RED)], 60, 860, 880, 100, 40, size=30)

# ═══════════════════════════ ACT 02 · THE SQUEEZE ═══════════════════════════
@scene(6, 'why does a juicer need wi-fi?', 'act 02 · the squeeze')
def s06():
    chips(['internet connectivity', 'produce-pack identification (qr code)'], 60, 170, L(1), dt=.4, size=30, gap=56)
    doc('doc_qr', 60, 310, 900, L(1, .8), 30, hls=(L(1, 1.2), L(2), L(2, .4)))
    heading("the company's case: freshness and consistency", 1000, 190, 32, L(2), 30); wrap(860)
    heading('did customers value the technology enough to justify the price — and the dependence on a proprietary system?', 1000, 300, 30, L(4), 30, col=RED); wrap(860)
    flow(['pack delivered', 'code scanned', 'online check', 'press runs'], 60, 680, 410, 100, 40, L(3), dt=.4)
    note('illustrative', 60, 790, L(3), w=300, size=15)
    heading('an appliance dependent on the wider business', 60, 880, 40, L(7), 30, col=RED); EV.append((T(L(7)), 'low'))

@scene(7, 'the engineering paradox')
def s07():
    photo('bolt18', 60, 190, 860, 600, 0, 30, PH_TAG['bolt18'])
    doc('doc_teardown', 980, 190, 880, L(2), 30, hls=(L(2, .4), L(3)))
    check(980, 520, L(4)); text('an ambitious piece of hardware', 1040, 530, 28, L(4), 30, font='outfit500')
    boxes([('engineering achievement', L(5), GREY), ('commercial value', L(5, .5), RED)], 980, 600, 420, 100, 40, size=26)
    text('≠', 1404, 622, 36, L(5, .5), 30, col=RED, font='outfit700')
    note('no manufacturing cost or specification is verified', 980, 730, L(5), w=880, size=16)
    heading('the more complex the solution, the more it must prove that customers need it', 60, 860, 38, L(7), 30, col=RED); wrap(1800); EV.append((T(L(7)), 'low'))

@scene(8, 'the first warning')
def s08():
    text('BEFORE THE BLOOMBERG TEST · JAN 17, 2017 (FORTUNE)', 60, 150, 22, L(1), 30, col=RED, font='mono600')
    heading('$699', 60, 210, 150, L(2), 30, col=GREY); strike(60, 300, 390, L(2, .5))
    hline(480, 600, 290, L(2, .6), 30, L(2, .6), L(2, .9))
    heading('$399', 640, 210, 150, L(2, .9), 30, col=RED); EV.append((T(L(2, .9)), 'impact'))
    money('PRICE CUT', '−42.9%', 1220, 200, L(3), size=110, sub='calculated: ($699 − $399) ÷ $699')
    text('accessible to more potential customers', 60, 480, 30, L(4), 30, font='outfit500')
    note('the company later cited "a five-fold increase in consumer adoption" after the cut (foodnavigator-usa)', 60, 535, L(4, .4), w=1800, size=17)
    heading('the original price was hard to sustain', 60, 610, 40, L(5), 30)
    rect(60, 740, 1800, 3, GREY, L(6), 30, grow=(L(6), L(6, .6), 'x'))
    for x, lab, c in ((60, 'jan 17, 2017 · price cut', GREY), (1860, 'apr 2017 · bloomberg squeeze test', RED)):
        sprite('dot_red' if c == RED else 'dot_grey', x + (0 if x < 1000 else -8), 741, L(6), 30); text(lab, x, 760, 22, L(6), 30, col=c, font='mono600', al='LEFT' if x < 1000 else 'RIGHT')
    heading('the public revelation was still to come', 60, 860, 42, L(6), 30, col=RED); EV.append((T(L(6)), 'low'))

@scene(9, 'april nineteenth, 2017')
def s09():
    text('APRIL 2017 · BLOOMBERG', 60, 150, 24, L(1), 30, col=RED, font='mono600')
    heading('the squeeze test', 60, 185, 44, L(1), 30)
    squeeze_chart(60, 290, L(3), L(4))
    doc('doc_squeeze', 1000, 190, 860, L(2), 30, hls=(L(4, .2), L(3), L(3, .4), L(4, .5), L(3, .2), L(4, .8)))
    text('not every benefit of the appliance disappears', 1000, 560, 28, L(5), 30, font='outfit500'); wrap(860)
    heading("the machine's most visible function could be substantially reproduced without buying it", 60, 820, 40, L(7), 30, col=RED); wrap(1800); EV.append((T(L(7)), 'low'))

@scene(10, 'the moment the story changed')
def s10():
    text('before: technology improving nutrition and convenience', 60, 190, 30, L(1), 30, col=GREY, font='outfit500'); strike(60, 210, 780, L(2))
    heading('after: an expensive machine doing what people could do themselves', 60, 270, 44, L(2, .3), 30, col=RED); wrap(1800)
    text('easy to understand · difficult to overcome', 60, 420, 24, L(4), 30, col=GREY, font='mono600')
    boxes([('explain why the product is useful', L(5), GREY), ('defend why the whole system is worth buying', L(6), RED)], 60, 500, 880, 120, 40, size=30)
    heading('…under widespread public criticism', 60, 700, 38, L(7), 30)
    text('headline: "google funded this $400 juicer startup, but turns out hands are better" · the indian express (bloomberg), apr 20, 2017', 60, 780, 18, L(7), 30, col=GREY, font='mono400'); wrap(1800)
    note('no social-media reactions or engagement figures are shown: none are verified', 60, 840, L(7), w=1800, size=15)

@scene(11, 'the company fights back')
def s11():
    doc('doc_dunnq', 60, 170, 900, L(1), 30, hls=(L(1, .4),))
    doc('doc_dunn', 60, 380, 900, L(2), 30, hls=(L(2, .4), L(2, .8)))
    money('REFUND OFFER · APR 2017', '30 days', 1000, 190, L(3), size=96, sub='owners could return the press for a full refund')
    heading('these arguments deserve consideration', 1000, 440, 34, L(4), 30); wrap(860)
    text('a machine can offer more than its most basic mechanical function', 1000, 510, 28, L(5), 30, font='outfit500'); wrap(860)
    boxes([('the complete experience', L(6), GREY), ('simply the juice', L(6, .5), RED)], 60, 720, 880, 110, 40, size=30)
    heading('the defense needed customers to value the whole system', 60, 880, 40, L(7), 30, col=RED); EV.append((T(L(7)), 'low'))

# ═══════════════════════════ ACT 03 · THE COLLAPSE ═══════════════════════════
@scene(12, "the problem the camera didn't show", 'act 03 · the collapse')
def s12():
    heading('behind the image: another challenge', 60, 170, 40, L(2), 30)
    flow(['sourced', 'prepared', 'packaged', 'transported', 'delivered fresh'], 60, 260, 330, 100, 40, L(3), dt=.35)
    note('illustrative', 60, 370, L(3), w=300, size=15)
    boxes([('consumer hardware', L(4), GREY), ('fresh-food distribution', L(5), RED)], 60, 440, 880, 110, 40, size=32)
    text('more sales = more infrastructure · lower prices = lower costs', 60, 600, 26, L(6), 30, font='outfit500'); wrap(900)
    text('the appliance attracted attention', 60, 680, 28, L(8), 30, col=GREY, font='outfit500')
    doc('doc_infra', 1000, 585, 860, L(7), 30, hls=(L(7, .4), L(8), L(8, .4)))
    heading('the distribution network: less visible, equally important', 60, 905, 40, L(9), 30, col=RED); wrap(1800); EV.append((T(L(9)), 'low'))

@scene(13, 'the last attempt to survive')
def s13():
    text('JULY 2017', 60, 150, 24, L(1), 30, col=RED, font='mono600')
    heading('a "strategic shift"', 60, 185, 44, L(1), 30)
    doc('doc_july', 60, 290, 900, L(1, .5), 30, hls=(L(1, .9), L(2, .5)))
    money('ANNOUNCED STAFF CUT', '25%', 1000, 190, L(2), size=120, sub='mainly sales and marketing')
    money('REPORTED TARGET · NEXT PRESS', 'about $200', 1000, 450, L(3), size=88, sub='a plan — never launched')
    text('a successful turnaround', 60, 640, 32, L(4), 30, col=GREY, font='outfit500'); strike(60, 660, 340, L(4, .5))
    chips(['cheaper hardware', 'cheaper distribution', 'enough customers to support both'], 60, 730, L(6), dt=.4, size=30, gap=56)

@scene(14, 'september first')
def s14():
    text('SEPTEMBER 1, 2017', 60, 150, 24, L(1), 30, col=RED, font='mono600')
    doc('doc_shut', 60, 200, 900, L(1, .2), 30, hls=(L(2), L(1, .6)))
    money('PRODUCE PACKS SOLD · PER JUICERO', '1 million+', 1000, 190, L(2), size=96, sub='company figure, since launch')
    doc('doc_infra', 60, 510, 900, L(3), 30, hls=(L(3, .3), L(3, .6), L(3, .9)))
    chips(['seeking a buyer with a fresh-food supply chain', 'refunds on presses for 90 days'], 1000, 410, L(4), dt=.4, size=24, gap=46)
    photo('bolt18', 1260, 560, 600, 418, L(5), 30, 'juicero press, disassembled · 2018 · s. jurvetson · cc by 2.0')
    heading('about seventeen months after launch, it could no longer continue independently', 60, 820, 36, L(5), 30, col=RED); wrap(1150); EV.append((T(L(5)), 'low'))

# ═══════════════════════════ ACT 04 · THE AUTOPSY ═══════════════════════════
@scene(15, 'three decisions that broke the business', 'act 04 · the autopsy')
def s15():
    heading('three strategic weaknesses', 60, 150, 44, L(1), 30)
    for k, (h_, s_, ev, t) in enumerate([('01 · premium hardware pricing', 'an expensive appliance put a high barrier in front of adoption', '$699 at launch; cut to $399 in jan 2017 (fortune)', L(2)),
                                        ('02 · perishable proprietary consumables', 'a proprietary fresh-food ecosystem with heavy operational demands', 'shutdown letter: infrastructure "that we cannot achieve on our own"', L(3)),
                                        ('03 · the manual substitute', 'the central function could be reproduced far more cheaply', 'bloomberg: 7.5 oz by hand in ~90 s vs 8 oz by machine in ~2 min', L(4))]):
        x = 60 + k * 610; card_box(x, 240, 580, 380, t, 30)
        text(h_, x + 36, 265, 18, t, 30, col=RED, font='mono600'); heading(s_, x + 36, 310, 30, t, 30); wrap(500)
        text(ev, x + 36, 520, 17, t + .3, 30, col=GREY, font='mono400'); wrap(510)
    text("none of these alone explains every decision inside juicero", 60, 670, 28, L(5), 30, col=GREY, font='outfit500')
    heading('together: engineering, customer value and distribution economics out of alignment', 60, 730, 34, L(6), 30); wrap(1800)
    text('ANALYTICAL SYNTHESIS', 60, 840, 18, L(7), 30, col=GREY, font='mono600')
    heading("funding built the system — it couldn't make it sustainable", 60, 875, 42, L(8), 30, col=RED); EV.append((T(L(8)), 'low'))

@scene(16, 'the verdict')
def s16():
    heading("juicero didn't fail because innovation is unnecessary", 960, 160, 46, L(1), L(5), al='CENTER')
    heading('innovation must justify its own complexity', 960, 240, 40, L(2), L(5), al='CENTER', col=RED); EV.append((T(L(2)), 'impact'))
    text('about $120 million raised → an extraordinary machine', 960, 320, 28, L(3), L(5), col=GREY, font='outfit500', al='CENTER')
    text('customers needed a reason to buy it · the company needed an affordable way to support it', 960, 375, 26, L(4), L(5), font='outfit500', al='CENTER')
    photo('bolt18', 560, 470, 800, 480, L(1), L(5), PH_TAG['bolt18'])
    CX.beat()
    text('THE VERDICT', 960, 180, 26, L(5), L(7), col=GREY, font='mono600', al='CENTER')
    text("the most important lesson wasn't revealed inside a boardroom or a financial report", 960, 260, 32, L(5, .2), L(7), font='outfit500', al='CENTER')
    heading('it was revealed when someone picked up a packet and squeezed', 960, 370, 54, L(6), L(7), al='CENTER', col=RED); wrap(1600); EV.append((T(L(6)), 'impact'))
    text('bloomberg, april 2017 · 7.5 oz by hand · 8 oz by machine', 960, 560, 24, L(6, .6), L(7), col=GREY, font='mono600', al='CENTER')
    CX.beat()
    e = heading('brand coroner', 943, 420, 110, L(7), 30, al='CENTER'); e2 = text('.', 1305, 420, 110, L(7, .8), 30, col=RED)
    f = text('EVERY BRAND LEAVES EVIDENCE.', 960, 570, 36, L(7, .4), 30, col=GREY, font='outfit500', al='CENTER')
    rect(810, 555, 300, 2, RED, L(7, .2), 30, grow=(L(7, .2), L(7, 1.0), 'x'))
    for st in (e, e2, f): fade(st, L(7), 30, 1, .6, 2.0)
