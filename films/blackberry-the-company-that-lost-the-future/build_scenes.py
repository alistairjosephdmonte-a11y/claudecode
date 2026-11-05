# ── BlackBerry scene designs. Authored on a 0–30 s grid per scene; L(k) is the grid time of narration line k, and
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

# ═══════════════════════════ ACT 01 · THE COLLAPSE ═══════════════════════════
@scene(1, 'the phone that ruled the world', 'act 01 · the collapse')
def s01():
    heading('2010', 960, 300, 220, L(1, -.3), L(2), al='CENTER')
    text("the most powerful name in smartphones wasn't apple", 960, 590, 40, L(1, .6), L(2), col=GREY, font='outfit500', al='CENTER')
    CX.beat()
    photo('bold', 60, 150, 560, 760, L(2), 30, PH_TAG.get('bold', ''), fx=.5, fy=.45, z0=1.0, z1=1.05)
    heading('it was blackberry.', 700, 150, 64, L(2), 30)
    heading('≈ 43%', 700, 270, 190, L(3), 30, col=RED)
    text('of the u.s. smartphone installed base · early 2010', 708, 480, 30, L(3, .4), 30, col=GREY, font='outfit500')
    doc('doc_jan10', 1300, 160, 560, L(3, .8), 30, hls=(L(3, 1.6),))
    text('TRUSTED BY', 708, 560, 22, L(4), 30, col=GREY, font='mono600')
    chips(['businesses', 'governments', 'millions of people'], 708, 600, L(4), dt=.6, size=32, gap=56)
    text('THREE YEARS LATER · SEPT 2013', 1280, 560, 22, L(5), 30, col=GREY, font='mono600')
    heading('3.8%', 1280, 600, 110, L(5, .3), 30); text('single digits', 1284, 730, 30, L(5, .8), 30, col=RED, font='outfit500')
    text('comscore mobilens · u.s. smartphone subscribers by platform · 3-month averages', 708, 800, 18, L(5), 30, col=GREY, font='mono400')
    heading('how did a company that helped define the smartphone become one of its most famous casualties?', 700, 860, 40, L(6), 30, col=RED)
    CX.m.sequences[-1].wrap_width = 1160 / W; EV.append((T(L(6)), 'low'))

@scene(2, 'the decision to stop')
def s02():
    text('SEPTEMBER 28, 2016', 60, 150, 30, L(1), 30, col=RED, font='mono600'); heading('the decision to stop', 60, 190, 72, L(1), 30)
    doc('doc_sep16', 60, 320, 820, L(2), 30, hls=(L(2, .8), L(2, 1.3)))
    photo('hq', 1000, 150, 860, 480, L(1), 30, PH_TAG.get('hq', ''))
    for k, (a_, b_, t) in enumerate([('IN-HOUSE', 'hardware development', L(2, .5)), ('FUTURE', 'outsourced to partners', L(3))]):
        y = 560 + k * 90; text(a_, 60, y + 10, 22, t, 30, col=GREY if k == 0 else RED, font='mono600'); heading(b_, 260, y, 44, t, 30)
    strike(256, 588, 470, L(3, .2))
    text('for a company once synonymous with the mobile phone: extraordinary', 60, 760, 30, L(4), 30, col=GREY, font='outfit500', wrap=880)
    heading('not a bankruptcy', 1000, 660, 56, L(5), 30, col=RED)
    text('REDIRECTED TOWARD', 1000, 750, 22, L(6), 30, col=GREY, font='mono600')
    for k, s_ in enumerate(['software', 'security', 'enterprise services']): heading(s_, 1000 + k * 220, 790, 34, L(6, k * .5), 30)
    rect(60, 860, 1800, 2, RULE, L(7), 30)
    heading('the market had already decided', 60, 885, 48, L(7), 30)
    text('the company that made mobile email essential could no longer compete as a major smartphone maker', 60, 955, 28, L(8), 30, col=GREY, font='outfit500', wrap=1200)
    heading('the real story began decades earlier →', 1860, 1010, 30, L(9), 30, col=RED, al='RIGHT'); EV.append((T(L(9)), 'low'))

# ═══════════════════════════ ACT 02 · THE INVENTION OF AN ADVANTAGE ═══════════════════════════
@scene(3, 'before the blackberry', 'act 02 · the invention of an advantage')
def s03():
    photo('hq', 60, 150, 900, 600, 0, 30, PH_TAG.get('hq', ''))
    heading('1984', 1020, 150, 150, L(1), 30, col=RED)
    heading('research in motion', 1020, 320, 56, L(1, .4), 30)
    text('founded by mike lazaridis and douglas fregin', 1024, 395, 30, L(1, .8), 30, font='outfit500')
    text('WATERLOO, ONTARIO, CANADA', 1024, 445, 22, L(1, 1.2), 30, col=GREY, font='mono600')
    text('wireless technology', 1024, 510, 32, L(2), 30, col=GREY, font='outfit500')
    text('LATE 1990s', 1024, 580, 22, L(3), 30, col=GREY, font='mono600'); text('digital communication beyond the office', 1024, 612, 32, L(3), 30, font='outfit500')
    text('1999', 1024, 680, 22, L(4), 30, col=RED, font='mono600'); heading('the original blackberry solution', 1024, 712, 40, L(4), 30)
    text('THE PROMISE', 60, 800, 22, L(5), 30, col=GREY, font='mono600')
    heading('you no longer needed to sit at a desk to receive important messages', 60, 840, 48, L(6), 30)
    CX.m.sequences[-1].wrap_width = 1100 / W
    text('for businesses: a new meaning of "available"', 1240, 840, 30, L(7), 30, col=GREY, font='outfit500', wrap=620)
    heading('the foundation of a global technology empire', 1240, 930, 36, L(8), 30, col=RED); CX.m.sequences[-1].wrap_width = 620 / W

@scene(4, 'the addiction')
def s04():
    photo('keys', 60, 150, 700, 800, 0, 30, PH_TAG.get('keys', ''), fx=.5, fy=.6, z0=1.0, z1=1.06)
    text('THREE STRENGTHS', 840, 150, 22, L(1), 30, col=GREY, font='mono600')
    for k, s_ in enumerate(['reliable mobile messaging', 'enterprise security', 'physical keyboards for writing email']):
        y = 190 + k * 70; check(840, y - 4, L(2 + k), size=44); heading(s_, 900, y, 40, L(2 + k), 30)
    text('+ BLACKBERRY MESSENGER (BBM)', 840, 410, 26, L(5), 30, col=RED, font='mono600'); text('another reason to stay inside the ecosystem', 840, 450, 28, L(5, .4), 30, col=GREY, font='outfit500')
    for k, (s_, t) in enumerate([('users built habits', L(6)), ('organizations built systems', L(7)), ('switching meant a new way of working', L(8))]):
        y = 530 + k * 56; rect(840, y + 10, 8, 26, RED if k == 2 else GREY, t, 30); text(s_, 866, y, 32, t, 30, font='outfit500')
    text('not merely communication tools —', 840, 730, 30, L(9), 30, col=GREY, font='outfit500')
    heading('the daily operating system of business', 840, 772, 48, L(10), 30)
    text('the loyalty helped it grow', 840, 880, 30, L(11), 30, font='outfit500')
    heading('— and complicated its response to change', 840, 925, 36, L(12), 30, col=RED); EV.append((T(L(12)), 'low'))

# ═══════════════════════════ ACT 03 · THE RULES CHANGE ═══════════════════════════
@scene(5, 'the iphone arrives', 'act 03 · the rules change')
def s05():
    photo('jobs', 60, 150, 1000, 640, 0, 30, PH_TAG.get('jobs', ''), fx=.5, fy=.4, z0=1.0, z1=1.06)
    text('JANUARY 9, 2007', 1120, 150, 30, L(1), 30, col=RED, font='mono600'); heading('apple introduces the iphone', 1120, 190, 48, L(1), 30)
    text('not the first smartphone', 1120, 270, 30, L(2), 30, col=GREY, font='outfit500')
    text("blackberry didn't disappear — rim kept growing", 1120, 320, 30, L(3), 30, font='outfit500')
    text('RIM REVENUE · FISCAL YEARS', 1120, 380, 20, L(4), 30, col=GREY, font='mono600')
    bars([('FY2008', 6.0, '$6.0B', L(4), GREY), ('FY2009', 11.1, '$11.1B', L(4, .5), GREY), ('FY2010', 15.0, '$15.0B', L(4, 1.0), GREY), ('FY2011', 19.9, '$19.9B', L(4, 1.5), RED)], 1140, 760, 140, 180, 13, lab_size=30, yr_size=20)
    text('fiscal years end feb/mar · rim annual results', 1120, 820, 16, L(4), 30, col=GREY, font='mono400')
    for k, s_ in enumerate(['a large touchscreen', 'a browser for the mobile internet', 'software built for direct interaction']):
        x = 60 + k * 340; rect(x, 836, 8, 28, RED, L(6 + k), 30); text(s_, x + 24, 830, 26, L(6 + k), 30, wrap=300); EV.append((T(L(6 + k)), 'type'))
    text('a different product experience', 60, 800, 22, L(5), 30, col=GREY, font='mono600')
    text('BLACKBERRY · OPTIMIZED FOR MESSAGING', 60, 940, 22, L(9), 30, col=GREY, font='mono600')
    text('APPLE · A GENERAL-PURPOSE POCKET COMPUTER', 60, 980, 22, L(10), 30, col=RED, font='mono600')
    heading('the difference would matter more and more', 1120, 950, 36, L(11), 30, col=RED)

@scene(6, 'the app economy')
def s06():
    cols = [('JULY 2008', 'app store', 'apple · iphone', L(1), RED), ('OCTOBER 2008', 'android', 'first android phone · many manufacturers', L(2), RED), ('BLACKBERRY', 'its own apps & services', 'blackberry app world · 2009', L(7), GREY)]
    for k, (a_, b_, c_, t, e) in enumerate(cols):
        x = 60 + k * 610; card_box(x, 150, 580, 210, t, 30, edge=e)
        text(a_, x + 36, 176, 24, t, 30, col=RED if e == RED else GREY, font='mono600'); heading(b_, x + 36, 214, 56 if k < 2 else 44, t, 30); text(c_, x + 36, 300, 24, t, 30, col=GREY, font='outfit500')
    heading('a platform war', 960, 420, 80, L(3), 30, al='CENTER'); EV.append((T(L(3)), 'impact'))
    for k, (s_, t) in enumerate([('applications mattered', L(4)), ('developers mattered', L(5)), ('the operating system set the value of the device', L(6))]):
        text(s_, 960, 540 + k * 50, 32, t, 30, al='CENTER', col=TXT if k < 2 else RED, font='outfit500')
    text('apple and android: broader consumer ecosystems', 960, 720, 30, L(8), 30, al='CENTER', col=GREY, font='outfit500')
    heading('a secure communications device', 960, 790, 40, L(9), 30, al='CENTER', col=GREY); strike(660, 816, 600, L(9, .8))
    for k, s_ in enumerate(['camera', 'entertainment', 'navigation', 'shopping', 'workplace']):
        text(s_, 300 + k * 330, 880, 34, L(10, k * .4), 30, al='CENTER', font='outfit700'); EV.append((T(L(10, k * .4)), 'type'))
    heading('all in one.', 960, 950, 48, L(11), 30, al='CENTER', col=RED)

SHORT = {'storm': 'storm · 2009 · aaltonen · cc by 2.0', 'torch': 'torch · 2010 · enrique dans · cc by 2.0', 'bold': 'bold 9700 · bertconcepts · cc by 2.0'}
@scene(7, 'the keyboard trap')
def s07():
    heading("the physical keyboard: one of its greatest advantages", 60, 150, 44, L(1), 30)
    text('a strength can become a constraint when expectations change', 60, 215, 30, L(2), 30, col=RED, font='outfit500')
    for k, (key, lab, t) in enumerate([('storm', 'STORM · 2008 · TOUCHSCREEN', L(5)), ('torch', 'TORCH · 2010 · SLIDER HYBRID', L(5, .7)), ('bold', 'BOLD · KEYBOARD', L(1))]):
        x = 60 + k * 450; photo(key, x, 300, 420, 520, t, 30, SHORT[key]); text(lab, x, 836, 22, t, 30, col=RED if k < 2 else GREY, font='mono600')
    text('larger touchscreens:', 1420, 300, 26, L(3), 30, col=GREY, font='mono600')
    text('more room for applications', 1420, 340, 30, L(3), 30, font='outfit500'); text('new interfaces and experiences', 1420, 384, 30, L(4), 30, font='outfit500')
    text('it did build touchscreen phones', 1420, 470, 30, L(6), 30, col=GREY, font='outfit500', wrap=440)
    heading('the problem was deeper', 1420, 560, 40, L(7), 30)
    text('KEYBOARD-CENTRED', 1420, 640, 22, L(8), 30, col=GREY, font='mono600'); vline(1440, 676, 736, L(8, .3), 30, L(8, .3), L(8, .8))
    text('SOFTWARE-FIRST PLATFORM', 1420, 750, 22, L(8, .8), 30, col=RED, font='mono600')
    heading("and the market wasn't waiting.", 60, 920, 52, L(9), 30, col=RED); EV.append((T(L(9)), 'low'))

@scene(8, 'the market-share collapse')
def s08():
    heading('the numbers', 60, 150, 52, L(1), 30)
    text('BLACKBERRY · SHARE OF U.S. SMARTPHONE SUBSCRIBERS (INSTALLED BASE)', 60, 230, 22, L(1, .4), 30, col=GREY, font='mono600')
    base = 860; k_ = 11
    bars([('DEC 2009', 41.6, '41.6%', L(2), GREY), ('JAN 2010', 43.0, '43.0%', L(2, .6), GREY), ('SEP 2011', 18.9, '18.9%', L(3), GREY), ('SEP 2013', 3.8, '3.8%', L(4), RED)], 100, base, 190, 270, k_)
    text('comscore mobilens · 3-month averages ending in the month shown', 60, 930, 18, L(4), 30, col=GREY, font='mono400')
    heading('apple and android gained enormous ground', 1240, 320, 40, L(5), 30); CX.m.sequences[-1].wrap_width = 620 / W
    for k, (a_, b_, t, c) in enumerate([('NOT', 'global shipment figures', L(6), GREY), ('BUT', 'the american smartphone installed base', L(7), TXT)]):
        y = 470 + k * 110; text(a_, 1240, y, 22, t, 30, col=RED, font='mono600'); text(b_, 1240, y + 34, 32, t, 30, col=c, font='outfit500', wrap=620)
    if True: strike(1240, 524, 340, L(6, .6))
    heading('the trend was unmistakable', 1240, 720, 40, L(8), 30)
    text('losing the market where it had been exceptionally strong', 1240, 790, 30, L(9), 30, col=RED, font='outfit500', wrap=620); EV.append((T(L(9)), 'low'))

# ═══════════════════════════ ACT 04 · THE RESPONSE ═══════════════════════════
@scene(9, 'the playbook', 'act 04 · the response')
def s09():
    photo('playbook', 60, 150, 900, 600, 0, 30, PH_TAG.get('playbook', ''), fx=.5, fy=.5, z0=1.0, z1=1.05)
    text('APRIL 2011', 1020, 150, 30, L(1), 30, col=RED, font='mono600'); heading('blackberry playbook', 1020, 190, 64, L(1), 30)
    text('NEW OS FOUNDATION · QNX · ACQUIRED 2010', 1024, 290, 22, L(2), 30, col=GREY, font='mono600')
    text('a more modern software architecture', 1024, 330, 32, L(3), 30, font='outfit500')
    heading('a troubled launch', 1020, 410, 52, L(4), 30, col=RED)
    text('AT LAUNCH, NO NATIVE', 1024, 500, 22, L(5), 30, col=GREY, font='mono600')
    for k, s_ in enumerate(['email', 'calendar', 'contacts']):
        y = 540 + k * 60; heading(s_, 1024, y, 40, L(5, k * .4), 30, col=GREY); strike(1020, y + 26, 200, L(5, k * .4 + .3))
    text('— only through a paired blackberry smartphone (blackberry bridge)', 1024, 730, 26, L(5, 1.4), 30, col=GREY, font='outfit500', wrap=840)
    text('native apps arrived with playbook os 2.0 · feb 2012', 1024, 800, 20, L(5, 1.8), 30, col=GREY, font='mono400')
    heading('for a messaging company: especially damaging', 60, 800, 40, L(6), 30); CX.m.sequences[-1].wrap_width = 900 / W
    text('reinventing its software', 60, 930, 30, L(7), 30, col=GREY, font='outfit500')
    heading('the execution was proving difficult', 1020, 920, 44, L(8), 30, col=RED)

@scene(10, 'the outage')
def s10():
    text('OCTOBER 2011', 60, 150, 30, L(2), 30, col=RED, font='mono600'); heading('then came another blow', 60, 190, 64, L(1), 30)
    text('A MAJOR SERVICE OUTAGE · MULTIPLE CONTINENTS', 60, 300, 22, L(2), 30, col=GREY, font='mono600')
    chips(['europe · middle east · africa', 'india · latin america', 'then north america'], 60, 340, L(2, .3), dt=.6, size=34, gap=60)
    for k, s_ in enumerate(['email', 'messaging', 'internet']):
        x = 60 + k * 280; heading(s_, x, 560, 44, L(3, k * .3), 30, col=GREY)
    strike(60, 590, 780, L(3, 1.2))
    doc('doc_outage', 1000, 150, 860, L(4), 30, hls=(L(4, .6), L(4, 1.4)))
    text('a brand built on dependable communication', 60, 680, 32, L(5), 30, font='outfit500')
    text("the outage didn't cause the decline by itself", 1000, 640, 30, L(6), 30, col=GREY, font='outfit500')
    heading('it exposed the risks of a tightly managed ecosystem', 1000, 690, 40, L(7), 30); CX.m.sequences[-1].wrap_width = 860 / W
    heading('— while competitors were gaining ground', 60, 900, 52, L(8), 30, col=RED); EV.append((T(L(8)), 'low'))

@scene(11, 'the blackberry 10 gamble')
def s11():
    photo('z10', 60, 150, 900, 620, L(3), 30, PH_TAG.get('z10', ''), fy=.45)
    text('Z10 · TOUCHSCREEN', 60, 790, 26, L(3), 30, col=RED, font='mono600')
    text('Q10 · PHYSICAL KEYBOARD', 60, 836, 26, L(3, .6), 30, col=RED, font='mono600')
    text('JANUARY 30, 2013 · NEW YORK', 1060, 150, 26, L(1), 30, col=RED, font='mono600'); heading('blackberry 10', 1060, 190, 80, L(1), 30)
    text('RESEARCH IN MOTION', 1064, 310, 26, L(2), 30, col=GREY, font='mono600'); hline(1380, 1460, 324, L(2, .3), 30, L(2, .3), L(2, .6))
    text('BLACKBERRY', 1490, 310, 26, L(2, .6), 30, font='mono600'); text('the new corporate name', 1064, 350, 26, L(2, .8), 30, col=GREY, font='outfit500')
    heading('not a company refusing to innovate', 1060, 430, 40, L(4), 30)
    text('A SUBSTANTIALLY REDESIGNED OS', 1064, 500, 22, L(5), 30, col=GREY, font='mono600')
    chips(['new gestures', 'multitasking', 'messaging tools (blackberry hub)'], 1060, 540, L(5, .3), dt=.6, size=32, gap=56)
    text('but it arrived after years of rapid growth by ios and android', 1064, 740, 28, L(6), 30, col=GREY, font='outfit500', wrap=800)
    text('not simply building a better blackberry —', 1064, 830, 28, L(7), 30, font='outfit500')
    heading('convincing users and developers to invest in another ecosystem', 1060, 880, 40, L(8), 30, col=RED); CX.m.sequences[-1].wrap_width = 800 / W

@scene(12, 'the ecosystem problem')
def s12():
    heading('by 2013: network effects', 60, 150, 52, L(1), 30)
    text('apple and android', 64, 220, 30, L(1, .4), 30, col=GREY, font='outfit500')
    text('developers → platforms with large audiences', 60, 300, 32, L(2), 30, font='outfit500')
    text('customers → platforms with the apps they wanted', 60, 350, 32, L(3), 30, font='outfit500')
    heading('each reinforced the other', 60, 420, 40, L(4), 30, col=RED)
    text('BLACKBERRY · A DIFFICULT CYCLE', 1000, 150, 22, L(5), 30, col=GREY, font='mono600')
    for (x, y, s_, t) in [(1000, 220, 'applications', L(6)), (1460, 520, 'users', L(6, .6)), (1000, 520, 'developers', L(7))]:
        card_box(x, y, 400, 120, t, 30); heading(s_, x + 200, y + 34, 44, t, 30, al='CENTER')
    hline(1400, 1560, 280, L(6, .3), 30, L(6, .3), L(6, .6), head=False); vline(1560, 280, 516, L(6, .3), 30, L(6, .3), L(6, .6))
    hline(1460, 1404, 580, L(7, .2), 30, L(7, .2), L(7, .5))
    vline(1200, 520, 344, L(7, .5), 30, L(7, .5), L(7, .8))
    text('it needed apps to attract users — and users to attract developers', 1000, 680, 26, L(7, .8), 30, col=GREY, font='outfit500', wrap=860)
    text('even strong hardware and a redesigned os could not solve that instantly', 60, 560, 30, L(8), 30, col=GREY, font='outfit500', wrap=860)
    heading('early to mobile communication', 60, 820, 44, L(9), 30)
    heading('struggling for momentum in the platform economy', 60, 890, 52, L(10), 30, col=RED); EV.append((T(L(10)), 'low'))

# ═══════════════════════════ ACT 05 · THE EXIT ═══════════════════════════
@scene(13, 'the financial damage', 'act 05 · the exit')
def s13():
    heading('the financial statements', 60, 150, 52, L(1), 30)
    text('REVENUE · FISCAL YEARS', 60, 240, 22, L(1, .4), 30, col=GREY, font='mono600')
    bars([('FY2011', 19.9, '$19.9B', L(1, .6), GREY), ('FY2012', 18.4, '$18.4B', L(1, 1.0), GREY), ('FY2013', 11.1, '$11.1B', L(1, 1.4), GREY), ('FY2014', 6.8, '$6.8B', L(2), RED)], 80, 860, 160, 220, 22, lab_size=38)
    text('rim / blackberry annual results · fiscal 2014 ended march 1, 2014', 60, 930, 18, L(2), 30, col=GREY, font='mono400')
    doc('doc_fy14', 1000, 150, 860, L(2, .4), 30, hls=(L(2, 1.0), L(2, 1.6), L(3, .4)))
    text('FY2014 NET LOSS (CONTINUING OPERATIONS)', 1000, 640, 22, L(2, 1.0), 30, col=GREY, font='mono600'); heading('$5.9B', 1000, 676, 90, L(2, 1.2), 30, col=RED)
    text('blackberry 10 had not delivered the recovery management hoped for', 1000, 800, 28, L(4), 30, font='outfit500', wrap=860)
    text('still: technology · patents · enterprise relationships · security', 1000, 860, 26, L(5), 30, col=GREY, font='outfit500', wrap=860)
    heading('handsets: no longer the engine of growth', 1000, 920, 36, L(6), 30)
    heading('it needed a different future.', 1000, 975, 36, L(7), 30, col=RED); EV.append((T(L(7)), 'low'))

@scene(14, 'the final pivot')
def s14():
    photo('chen', 60, 150, 560, 700, 0, 30, PH_TAG.get('chen', ''), fx=.5, fy=.35)
    text('NOVEMBER 2013', 680, 150, 30, L(1), 30, col=RED, font='mono600'); heading('john chen takes charge', 680, 190, 52, L(1), 30)
    doc('doc_chen', 680, 270, 620, L(1, .6), L(4), hls=(L(1, 1.2), L(1, 1.6)))
    text('executive chair & interim ceo · later ceo', 684, 500, 22, L(1, 1.0), L(4), col=GREY, font='mono600')
    text('A SHIFT TOWARD', 1380, 150, 22, L(2), 30, col=GREY, font='mono600')
    chips(['enterprise software', 'security', 'services'], 1380, 190, L(2), dt=.6, size=34, gap=60)
    text('android-powered blackberry · priv · 2015', 1380, 400, 20, L(3), 30, col=GREY, font='mono600')
    photo('priv', 1380, 470, 480, 380, L(3), 30, 'priv · jan 2016 · maurizio pesce · cc by 2.0')
    doc('doc_sep16', 680, 270, 620, L(4), 30, hls=(L(4, .6),)); text('SEPTEMBER 28, 2016', 684, 500, 22, L(4), 30, col=RED, font='mono600')
    text('branded devices could continue through licensing and manufacturing partners', 680, 560, 28, L(5), 30, font='outfit500', wrap=640)
    heading('the distinction matters', 680, 680, 40, L(6), 30)
    text('not every phone bearing its name', 680, 740, 28, L(7), 30, col=GREY, font='outfit500')
    rect(60, 880, 1800, 2, RULE, L(8), 30)
    heading('ended: the vertically integrated smartphone manufacturer', 960, 910, 48, L(8), 30, col=RED, al='CENTER')

# ═══════════════════════════ ACT 06 · THE AUTOPSY ═══════════════════════════
@scene(15, "what actually killed blackberry's dominance?", 'act 06 · the autopsy')
def s15():
    heading("what caused blackberry's collapse in smartphones?", 960, 200, 56, L(1), L(5), al='CENTER')
    for k, (s_, w_) in enumerate([('not simply the iphone', 560), ('not simply the keyboard', 620)]):
        heading(s_, 960, 360 + k * 90, 48, L(2 + k), L(5), col=GREY, al='CENTER'); strike(960 - w_ / 2, 390 + k * 90, w_, L(2 + k, .7), L(5))
    heading('a combination of problems', 960, 620, 80, L(4), L(5), col=RED, al='CENTER'); EV.append((T(L(4)), 'impact'))
    CX.beat()
    text('THE FINDINGS', 60, 150, 24, L(5), 30, col=GREY, font='mono600')
    for k, (s_, t) in enumerate([('a product identity centred on messaging — as the market moved to applications', L(5)), ('difficulty executing a modern software transition', L(6)), ('a growing disadvantage in developer ecosystems', L(7)), ('a delayed response to rival platforms gaining scale', L(8))]):
        y = 200 + k * 105; card_box(60, y, 1800, 88, t, 30); check(90, y + 16, t, size=48); heading(s_, 170, y + 22, 38, t, 30)
    text('it understood mobile communication better than almost anyone', 60, 700, 34, L(9), 30, col=GREY, font='outfit500')
    heading('understanding the old market was not enough to win the new one', 60, 800, 52, L(10), 30, col=RED); CX.m.sequences[-1].wrap_width = 1800 / W

@scene(16, 'the verdict')
def s16():
    heading('a dangerous paradox', 960, 220, 64, L(1), L(3), al='CENTER', col=RED)
    heading('the capabilities that make a company successful', 960, 380, 52, L(2), L(3), al='CENTER')
    heading('can become the assumptions that limit its future', 960, 460, 52, L(2, .8), L(3), al='CENTER', col=GREY)
    CX.beat()
    for k, s_ in enumerate(['reliability', 'security', 'productivity']): heading(s_, 400 + k * 560, 220, 56, L(3, k * .5), L(8), al='CENTER')
    text('those strengths were real', 960, 320, 32, L(4), L(8), col=GREY, font='outfit500', al='CENTER')
    heading('the smartphone became something bigger than the product it had perfected', 960, 430, 44, L(5), L(8), al='CENTER')
    heading('the company survived by changing its business', 960, 580, 44, L(6), L(8), al='CENTER')
    heading('its handset dominance did not', 960, 660, 56, L(7), L(8), al='CENTER', col=RED); EV.append((T(L(7)), 'impact'))
    CX.beat()
    text('THE LESSON', 960, 220, 26, L(8), L(11), col=GREY, font='mono600', al='CENTER')
    heading("a market leader doesn't have to stop innovating to fall behind", 960, 320, 56, L(9), L(11), al='CENTER')
    heading('sometimes it innovates in a direction the market has already moved beyond', 960, 460, 44, L(10), L(11), al='CENTER', col=RED)
    CX.beat()
    e = heading('brand coroner', 943, 420, 110, L(11), 30, al='CENTER'); e2 = text('.', 1305, 420, 110, L(11, .8), 30, col=RED)
    f = text('EVERY BRAND LEAVES EVIDENCE.', 960, 570, 36, L(11, .4), 30, col=GREY, font='outfit500', al='CENTER')
    rect(810, 555, 300, 2, RED, L(11, .2), 30, grow=(L(11, .2), L(11, 1.0), 'x'))
    for st in (e, e2, f): fade(st, L(11), 30, 1, .6, 2.0)
