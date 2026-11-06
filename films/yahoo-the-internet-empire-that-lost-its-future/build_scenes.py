# ── Yahoo scene designs. Authored on a 0–30 s grid per scene; L(k) is the grid time of narration line k, and
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

# ═══════════════════════════ ACT 01 · THE EMPIRE ═══════════════════════════
@scene(1, 'the front door to the internet', 'act 01 · the empire')
def s01():
    for k, s_ in enumerate(['before google became a verb', 'before facebook connected billions', "before smartphones put the internet in everyone's pocket"]):
        text(s_, 960, 260 + k * 64, 40, L(1, k * .5), L(2), col=GREY, font='outfit500', al='CENTER')
    heading('there was yahoo.', 960, 520, 110, L(1, 1.8), L(2), al='CENTER'); EV.append((T(L(1, 1.8)), 'impact'))
    CX.beat()
    photo('hq', 60, 150, 820, 560, L(2), 30, PH_TAG.get('hq', ''), fx=.5, fy=.5, z0=1.0, z1=1.05)
    heading('for millions of people, yahoo was the internet.', 940, 150, 52, L(2), 30); wrap(900)
    chips(['search', 'email', 'news', 'discovering what was happening online'], 940, 320, L(3), dt=.5, size=32, gap=56)
    text('PEAK MARKET VALUE · DOT-COM BOOM · JAN 2000', 940, 580, 22, L(4), 30, col=GREY, font='mono600')
    heading('$100B+', 940, 615, 150, L(4, .3), 30, col=RED)
    text('reported peak ≈ $120–125 billion (new york times, ap)', 944, 800, 18, L(4, .3), 30, col=GREY, font='mono400')
    text('2017 · core operating business sold to verizon', 60, 750, 32, L(5), 30, font='outfit500')
    heading('how did an internet pioneer lose control of its future?', 60, 880, 52, L(6), 30, col=RED); EV.append((T(L(6)), 'low'))

@scene(2, 'the $4.48 billion ending')
def s02():
    text('JUNE 13, 2017', 60, 150, 30, L(1), 30, col=RED, font='mono600'); heading('the $4.48 billion ending', 60, 190, 72, L(1), 30)
    doc('doc_jun17', 1000, 150, 860, L(2), 30, hls=(L(2, .6), L(5), L(5, .6)))
    text('AMENDED PURCHASE AGREEMENT · FEB 2017', 60, 320, 22, L(3), 30, col=GREY, font='mono600')
    heading('≈ $4.48B', 60, 355, 120, L(3, .3), 30)
    text('approximately $4.48 billion in cash · subject to adjustments', 64, 500, 26, L(3, .8), 30, col=GREY, font='outfit500')
    text('FINAL ACCOUNTING · VERIZON FORM 10-K, 2017', 60, 580, 22, L(4), 30, col=GREY, font='mono600')
    heading('≈ $4.7B', 60, 615, 64, L(4, .3), 30, col=RED)
    text('aggregate purchase consideration, including $0.2 billion of cash acquired', 64, 700, 24, L(4, .6), 30, col=GREY, font='outfit500', wrap=860)
    text('NOT PART OF THE SALE', 1000, 560, 22, L(5), 30, col=RED, font='mono600')
    chips(['alibaba stake (≈ 15%)', 'yahoo japan stake (≈ 36%)'], 1000, 600, L(5, .3), dt=.6, size=34, gap=60)
    text("not the entire company's value disappearing", 1000, 740, 30, L(6), 30, col=GREY, font='outfit500', wrap=860)
    rect(60, 850, 1800, 2, RULE, L(7), 30)
    heading('the end of yahoo as an independent internet operating business', 60, 880, 48, L(7), 30)
    heading('to understand how it happened, return to the beginning →', 1860, 1000, 30, L(8), 30, col=RED, al='RIGHT'); EV.append((T(L(8)), 'low'))

# ═══════════════════════════ ACT 02 · THE COMPANY THAT ORGANIZED THE WEB ═══════════════════════════
@scene(3, 'two students and a directory', 'act 02 · the company that organized the web')
def s03():
    photo('founders', 60, 150, 860, 600, 0, 30, PH_TAG.get('founders', ''), fx=.5, fy=.4)
    heading('1994', 1000, 150, 150, L(1), 30, col=RED)
    text('two stanford graduate students', 1004, 320, 32, L(1, .4), 30, font='outfit500')
    heading('jerry yang & david filo', 1000, 365, 48, L(1, .8), 30)
    text('THEY CALLED IT', 1004, 450, 22, L(2), 30, col=GREY, font='mono600')
    text("“jerry and david's guide to the world wide web”", 1000, 485, 36, L(2, .2), 30, font='serifi', wrap=860); EV.append((T(L(2, .2)), 'type'))
    text('the idea was simple', 1004, 600, 30, L(3), 30, col=GREY, font='outfit500')
    text('the web was growing faster than people could navigate it', 1004, 650, 28, L(4), 30, font='outfit500', wrap=860)
    heading('organize the chaos', 1000, 700, 48, L(5), 30, col=RED)
    text('THEIR PROJECT BECAME', 60, 790, 22, L(6), 30, col=GREY, font='mono600')
    heading('yahoo', 60, 825, 80, L(6, .2), 30)
    text("one of the web's most recognizable destinations", 330, 855, 30, L(7), 30, col=GREY, font='outfit500')
    text('APRIL 1996', 1000, 790, 22, L(8), 30, col=RED, font='mono600'); heading('yahoo goes public', 1000, 825, 44, L(8, .2), 30)
    text('something extraordinarily valuable:', 1000, 905, 28, L(9), 30, col=GREY, font='outfit500')
    heading("a place at the beginning of the internet user's journey", 1000, 950, 34, L(10), 30, col=RED); wrap(860); EV.append((T(L(10)), 'low'))

@scene(4, 'the portal empire')
def s04():
    heading('far beyond the original directory', 60, 150, 56, L(1), 30)
    for k, s_ in enumerate(['email', 'news', 'finance', 'sports', 'shopping', 'entertainment']):
        x, y, t = 60 + (k % 3) * 400, 260 + (k // 3) * 130, L(2, k * .35); card_box(x, y, 370, 100, t, 30, edge=RED if k == 0 else GREY); heading(s_, x + 36, y + 26, 40, t, 30)
    text('THE STRATEGY', 1300, 260, 22, L(3), 30, col=GREY, font='mono600')
    heading('a central destination for everything people wanted online', 1300, 300, 38, L(3, .2), 30); wrap(560)
    heading('audience', 1300, 470, 40, L(4), 30); hline(1490, 1580, 495, L(4, .3), 30, L(4, .3), L(4, .7)); heading('advertisers', 1600, 470, 40, L(4, .7), 30, col=RED)
    text('the more users visited, the more valuable the audience', 1300, 540, 26, L(5), 30, col=GREY, font='outfit500', wrap=560)
    heading('for a time, the strategy worked', 60, 560, 44, L(6), 30)
    text('not simply a search engine —', 60, 640, 32, L(7), 30, col=GREY, font='outfit500')
    heading("a collection of internet services, held together by one of the world's most recognizable brands", 60, 690, 40, L(8), 30); wrap(1800)
    heading('but a different model of the internet was emerging', 60, 900, 48, L(9), 30, col=RED); EV.append((T(L(9)), 'low'))

# ═══════════════════════════ ACT 03 · THE SEARCH WAR ═══════════════════════════
@scene(5, 'google changes the question', 'act 03 · the search war')
def s05():
    heading('google approached the internet differently', 60, 150, 52, L(1), 30)
    text('THE PORTAL', 60, 260, 22, L(2), 30, col=GREY, font='mono600')
    text('browse a directory · spend time on the site', 60, 300, 32, L(2), 30, col=GREY, font='outfit500')
    text('THE ANSWER', 1000, 260, 22, L(2, 1.0), 30, col=RED, font='mono600')
    heading('find the most relevant answer', 1000, 295, 44, L(2, 1.0), 30)
    text('search technology improved as the web grew', 1000, 380, 30, L(3), 30, font='outfit500')
    text('advertising: commercial intent → search results', 1000, 430, 30, L(4), 30, font='outfit500')
    text('yahoo had search technology and search partnerships of its own', 60, 380, 30, L(5), 30, font='outfit500', wrap=860)
    text('inktomi results (1998–2000) · google results (2000–2004)', 60, 470, 20, L(5, .5), 30, col=GREY, font='mono400')
    heading("google's focus: a powerful competitive advantage", 1000, 520, 38, L(6), 30, col=RED); wrap(860)
    rect(60, 690, 1800, 2, RULE, L(7), 30)
    heading('attracting the largest audience', 60, 730, 44, L(7), 30, col=GREY); strike(56, 760, 690, L(7, .8))
    heading('owning the moment when someone wants an answer', 60, 830, 64, L(8), 30); EV.append((T(L(8)), 'impact'))

@scene(6, 'the google opportunity')
def s06():
    heading('the google opportunity', 60, 150, 64, L(1), 30)
    text("one of yahoo's most famous missed opportunities", 60, 240, 30, L(1, .5), 30, col=GREY, font='outfit500')
    text('CONTEMPORARY REPORTING · EARLY 2000s · ACQUISITION DISCUSSIONS', 60, 320, 22, L(2), 30, col=GREY, font='mono600')
    card_box(60, 380, 900, 240, L(3), 30)
    text('ONE WIDELY REPORTED ACCOUNT · 2002', 96, 400, 22, L(3), 30, col=RED, font='mono600')
    heading('yahoo explored buying google for roughly $3 billion', 96, 440, 40, L(3, .3), 30); wrap(840)
    text('no deal · reported (wired, feb 2007) · accounts vary', 96, 575, 20, L(3, 1.0), 30, col=GREY, font='mono400')
    text('THE FAMILIAR STORY', 1040, 380, 22, L(4), 30, col=GREY, font='mono600')
    heading('“yahoo rejected google for $1 million”', 1040, 420, 38, L(4, .2), 30, col=GREY); strike(1036, 446, 760, L(4, .9))
    text('the negotiations were more complicated', 1040, 500, 28, L(4, 1.2), 30, font='outfit500')
    heading('what matters: the strategic question', 60, 690, 48, L(5), 30)
    text("an opportunity to become more deeply involved in google's future", 60, 760, 32, L(6), 30, col=GREY, font='outfit500')
    heading('instead: its most formidable search competitor', 60, 880, 56, L(7), 30, col=RED); EV.append((T(L(7)), 'low'))

@scene(7, 'buying its way back')
def s07():
    heading('yahoo did not stand still', 60, 150, 60, L(1), 30)
    for k, (a_, b_, c_, t) in enumerate([('INKTOMI · COMPLETED MARCH 2003', 'search technology', 'web search engine', L(2)), ('OVERTURE · COMPLETED OCTOBER 2003', 'paid search', '≈ $1.6 billion', L(2, .8))]):
        x = 60 + k * 600; card_box(x, 260, 560, 190, t, 30)
        text(a_, x + 36, 282, 20, t, 30, col=RED, font='mono600'); heading(b_, x + 36, 320, 44, t, 30); text(c_, x + 36, 390, 26, t, 30, col=GREY, font='outfit500')
    text('capabilities in web search and advertising', 60, 490, 30, L(3), 30, col=GREY, font='outfit500')
    text('FEBRUARY 2004', 1300, 260, 22, L(4), 30, col=RED, font='mono600')
    heading('yahoo search technology', 1300, 296, 40, L(4, .2), 30)
    text("replaces google's results on yahoo", 1300, 360, 28, L(4, .6), 30, font='outfit500')
    text('investing where google was gaining strength', 1300, 430, 28, L(5), 30, col=GREY, font='outfit500', wrap=560)
    heading('owning the pieces of a search business ≠ executing a superior search strategy', 60, 600, 44, L(6), 30); wrap(1800)
    text('google kept building momentum', 60, 760, 34, L(7), 30, col=GREY, font='outfit500')
    heading('fighting to reclaim ground it had helped define', 60, 880, 56, L(8), 30, col=RED); EV.append((T(L(8)), 'low'))

@scene(8, 'too many businesses')
def s08():
    e = L(6)
    heading("yahoo's strength had become a strategic challenge", 60, 150, 48, L(1), e)
    card_box(760, 440, 400, 120, L(2), e); heading('yahoo', 960, 470, 52, L(2), e, al='CENTER')
    boxes = [(100, 300, 'a portal'), (1400, 300, 'a media company'), (100, 610, 'an email provider'), (1400, 610, 'an advertising platform'), (750, 760, 'a search competitor')]
    for k, (x, y, s_) in enumerate(boxes):
        t = L(2, .4 + k * .4); card_box(x, y, 420, 90, t, e, edge=GREY); heading(s_, x + 210, y + 26, 34, t, e, al='CENTER')
    t = L(2, .3)
    hline(760, 600, 500, t, e, t, t + .3, head=False); vline(600, 500, 345, t, e, t + .3, t + .6, head=False); hline(600, 524, 345, t, e, t + .6, t + .8)
    vline(600, 500, 655, t, e, t + .3, t + .6, head=False); hline(600, 524, 655, t, e, t + .6, t + 1.0)
    hline(1160, 1320, 500, t, e, t, t + .3, head=False); vline(1320, 500, 345, t, e, t + .3, t + .6, head=False); hline(1320, 1396, 345, t, e, t + .6, t + .8)
    vline(1320, 500, 655, t, e, t + .3, t + .6, head=False); hline(1320, 1396, 655, t, e, t + .6, t + 1.0)
    vline(960, 560, 756, t, e, t + .3, t + 1.2)
    for k, s_ in enumerate(['each required investment', 'each faced different rivals', 'each competed for management attention']):
        text(s_, 60 + k * 600, 900, 28, L(3 + k), e, col=TXT if k < 2 else RED, font='outfit500'); EV.append((T(L(3 + k)), 'type'))
    CX.beat()
    heading('diversification can protect a company', 60, 200, 56, L(6), 30)
    text('it can also make it hard to decide where the next great advantage will come from', 60, 290, 34, L(7), 30, col=GREY, font='outfit500', wrap=1800)
    for k, (a_, b_, t, c) in enumerate([('GOOGLE', 'a clear center of gravity: search and advertising', L(8), RED), ('YAHOO', 'an extraordinary collection of assets', L(9), GREY)]):
        x = 60 + k * 920; card_box(x, 420, 880, 220, t, 30, edge=c)
        text(a_, x + 36, 446, 22, t, 30, col=c, font='mono600'); heading(b_, x + 36, 490, 44, t, 30); wrap(800)
    heading('how should those assets fit together?', 960, 780, 64, L(10), 30, col=RED, al='CENTER'); EV.append((T(L(10)), 'impact'))

# ═══════════════════════════ ACT 04 · THE BILLION-DOLLAR DECISIONS ═══════════════════════════
@scene(9, 'the facebook question', 'act 04 · the billion-dollar decisions')
def s09():
    text('BY 2006', 60, 150, 30, L(1), 30, col=RED, font='mono600'); heading('another internet revolution', 60, 190, 64, L(1), 30)
    text('social networking: transforming how people discovered information and interacted online', 60, 290, 30, L(2), 30, col=GREY, font='outfit500', wrap=1800)
    card_box(60, 380, 900, 280, L(3), 30)
    text('REPORTED · 2006', 96, 400, 22, L(3), 30, col=RED, font='mono600')
    heading('acquisition discussions with facebook', 96, 440, 40, L(3, .2), 30)
    text('negotiations around a billion-dollar valuation', 96, 510, 30, L(4), 30, font='outfit500')
    text("disagreements over price and the company's future · accounts vary", 96, 570, 20, L(4, .6), 30, col=GREY, font='mono400', wrap=840)
    heading('no deal was completed', 1040, 390, 48, L(5), 30, col=RED)
    text("tempting: call facebook's later value “yahoo's loss”", 1040, 480, 30, L(6), 30, col=GREY, font='outfit500', wrap=820)
    text('that assumes the acquisition would have', 1040, 570, 26, L(7), 30, col=GREY, font='mono600')
    chips(['happened', 'succeeded', "preserved facebook's growth"], 1040, 615, L(7, .3), dt=.6, size=32, gap=56)
    heading('the more useful question: why yahoo struggled to build a comparable position in social networking', 60, 860, 44, L(8), 30); wrap(1800); EV.append((T(L(8)), 'low'))

@scene(10, "microsoft's $44.6 billion offer")
def s10():
    photo('ballmer', 60, 150, 620, 700, 0, 30, PH_TAG.get('ballmer', ''), fx=.5, fy=.35)
    heading('then came an extraordinary offer', 740, 150, 48, L(1), 30)
    text('FEBRUARY 1, 2008 · MICROSOFT', 740, 230, 22, L(2), 30, col=RED, font='mono600')
    heading('$44.6 billion', 740, 265, 100, L(2, .2), 30)
    text('equity value · $31 per share · cash and stock', 744, 390, 24, L(2, .6), 30, col=GREY, font='outfit500')
    doc('doc_msft08', 740, 450, 640, L(2, .8), L(5), hls=(L(2, 1.2), L(2, 1.6)))
    doc('doc_may08', 740, 450, 640, L(5), 30, hls=(L(5, .5), L(5, 1.0), L(7)))
    text('the aim: search and online advertising', 1420, 460, 28, L(3), 30, font='outfit500', wrap=440)
    text('negotiations continued for months', 1420, 560, 28, L(4), 30, col=GREY, font='outfit500', wrap=440)
    text('no agreement on terms', 1420, 640, 28, L(6), 30, col=GREY, font='outfit500')
    text('MAY 3, 2008', 1420, 710, 22, L(7), 30, col=RED, font='mono600'); heading('bid withdrawn', 1420, 745, 44, L(7, .2), 30)
    rect(60, 880, 1800, 2, RULE, L(8), 30)
    heading('yahoo remained independent', 60, 900, 52, L(8), 30)
    text('— and under pressure to prove that independence could create greater value', 60, 980, 30, L(9), 30, col=RED, font='outfit500'); EV.append((T(L(9)), 'low'))

@scene(11, 'the search partnership')
def s11():
    text('JULY 29, 2009', 60, 150, 30, L(1), 30, col=RED, font='mono600'); heading('the search partnership', 60, 190, 64, L(1), 30)
    doc('doc_jul09', 1000, 150, 860, L(2), 30, hls=(L(2, .6), L(2, 1.2), L(2, 1.8)))
    text('MICROSOFT · BING', 60, 310, 22, L(2, .6), 30, col=RED, font='mono600')
    text("powers yahoo's algorithmic and paid search", 60, 346, 32, L(2, .6), 30, font='outfit500')
    text('YAHOO', 60, 420, 22, L(2, 1.2), 30, col=GREY, font='mono600')
    text('owns the user experience on its properties', 60, 456, 32, L(2, 1.2), 30, font='outfit500')
    text('sales force for premium search advertisers', 60, 500, 32, L(2, 1.8), 30, font='outfit500')
    heading('designed to create scale against google', 60, 640, 44, L(3), 30)
    text('also a major strategic change', 1000, 680, 32, L(4), 30, col=GREY, font='outfit500')
    heading("a pioneer of online discovery, relying on another company's search technology", 60, 750, 40, L(5), 30); wrap(1800)
    text('it could still serve millions of users', 60, 850, 30, L(6), 30, col=GREY, font='outfit500')
    heading('but could it control the technology that shaped their experience?', 60, 920, 44, L(7), 30, col=RED); EV.append((T(L(7)), 'low'))

@scene(12, 'the mobile revolution')
def s12():
    heading('the internet was moving again', 60, 150, 60, L(1), 30)
    for k, s_ in enumerate(['smartphones changed how people accessed information', 'apps reduced the need to begin at a web portal', 'social networks changed how content was discovered and shared', 'digital advertising grew more sophisticated']):
        y, t = 270 + k * 70, L(2 + k); rect(60, y + 9, 8, 30, RED, t, 30); text(s_, 86, y, 34, t, 30, font='outfit500'); EV.append((T(t), 'type'))
    text('STILL POPULAR', 1300, 270, 22, L(6), 30, col=GREY, font='mono600')
    chips(['mail', 'finance', 'news', 'sports'], 1300, 310, L(6, .2), dt=.4, size=36, gap=60, bar=GREY)
    heading('audience scale alone was no longer enough', 60, 620, 52, L(7), 30); EV.append((T(L(7)), 'impact'))
    text('NEEDED: STRONGER POSITIONS IN', 60, 730, 22, L(8), 30, col=RED, font='mono600')
    for k, s_ in enumerate(['mobile products', 'advertising technology', 'next-generation platforms']):
        t = L(8, .3 + k * .5); card_box(60 + k * 610, 780, 580, 110, t, 30); heading(s_, 96 + k * 610, 810, 34, t, 30)

# ═══════════════════════════ ACT 05 · THE FINAL REINVENTION ═══════════════════════════
@scene(13, 'the marissa mayer era', 'act 05 · the final reinvention')
def s13():
    photo('mayer', 60, 150, 560, 700, 0, 30, PH_TAG.get('mayer', ''), fx=.5, fy=.3)
    text('JULY 2012', 680, 150, 30, L(1), 30, col=RED, font='mono600'); heading('marissa mayer becomes ceo', 680, 190, 44, L(1), 30)
    doc('doc_mayer', 680, 280, 620, L(1, .5), 30, hls=(L(1, 1.0), L(1, 1.4)))
    text('former google executive', 684, 510, 26, L(1, 1.2), 30, col=GREY, font='outfit500')
    heading('expectations of a turnaround', 1400, 150, 40, L(2), 30); wrap(460)
    text('YAHOO INVESTED IN', 1400, 290, 22, L(3), 30, col=GREY, font='mono600')
    chips(['mobile applications', 'product redesigns', 'talent', 'acquisitions'], 1400, 330, L(3, .2), dt=.5, size=32, gap=56)
    text('MAY 2013 · ANNOUNCED', 680, 600, 22, L(4), 30, col=RED, font='mono600'); heading('tumblr · ≈ $1.1 billion', 680, 635, 56, L(4, .2), 30)
    text('a large acquisition and new product investment could not automatically restore its position', 680, 730, 28, L(5), 30, font='outfit500', wrap=1180)
    text('entrenched competitors: search · social media · digital advertising', 680, 820, 28, L(6), 30, col=GREY, font='outfit500', wrap=1180)
    heading('time was becoming one of its scarcest resources', 680, 900, 44, L(7), 30, col=RED); EV.append((T(L(7)), 'low'))

@scene(14, 'the breaches and the sale')
def s14():
    text('JULY 2016', 60, 150, 30, L(1), 30, col=RED, font='mono600'); heading('verizon agrees: ≈ $4.83 billion', 60, 190, 56, L(1), 30)
    doc('doc_breach', 1000, 150, 860, L(2), 30, hls=(L(2, .5), L(2, 1.0), L(2, 1.3)))
    text('SEPT & DEC 2016 · HISTORICAL BREACHES DISCLOSED', 60, 300, 22, L(2), 30, col=RED, font='mono600')
    text('complicated the transaction · serious questions about security and accountability', 60, 340, 30, L(3), 30, font='outfit500', wrap=880)
    text('FEBRUARY 2017 · AMENDED AGREEMENT', 60, 450, 22, L(4), 30, col=GREY, font='mono600')
    heading('− $350 million', 60, 485, 80, L(4, .2), 30, col=RED)
    text('stated purchase price → ≈ $4.48 billion', 64, 590, 28, L(4, .8), 30, col=GREY, font='outfit500')
    text('JUNE 13, 2017', 60, 670, 22, L(5), 30, col=RED, font='mono600'); heading('the transaction closes', 60, 705, 44, L(5, .2), 30)
    text('operating business → verizon', 1000, 660, 34, L(6), 30, font='outfit500')
    text('investment holdings → altaba', 1000, 720, 34, L(7), 30, col=RED, font='outfit500')
    rect(60, 850, 1800, 2, RULE, L(8), 30)
    heading('the original internet empire, fundamentally transformed', 960, 890, 52, L(8), 30, al='CENTER'); EV.append((T(L(8)), 'low'))

# ═══════════════════════════ ACT 06 · THE AUTOPSY ═══════════════════════════
@scene(15, 'what actually went wrong?', 'act 06 · the autopsy')
def s15():
    heading("what killed yahoo's position as an internet leader?", 960, 200, 56, L(1), L(5), al='CENTER')
    for k, (s_, w_) in enumerate([('not one missed acquisition', 640), ('not one chief executive', 560)]):
        heading(s_, 960, 360 + k * 90, 48, L(2 + k), L(5), col=GREY, al='CENTER'); strike(960 - w_ / 2, 390 + k * 90, w_, L(2 + k, .7), L(5))
    heading('a broader pattern', 960, 620, 80, L(4), L(5), col=RED, al='CENTER'); EV.append((T(L(4)), 'impact'))
    CX.beat()
    text('THE FINDINGS', 60, 150, 24, L(5), 30, col=GREY, font='mono600')
    for k, (s_, t) in enumerate([('an uncertain strategic identity', L(5)), ('difficulty turning enormous audience reach into defensible technology leadership', L(6)), ('intensifying competition in search and advertising', L(7)), ('acquisitions and partnerships that built no lasting advantage in the next platforms', L(8))]):
        y = 200 + k * 105; card_box(60, y, 1800, 88, t, 30); check(90, y + 16, t, size=48); heading(s_, 170, y + 22, 36, t, 30)
    text('successful at attracting users', 60, 700, 34, L(9), 30, col=GREY, font='outfit500')
    heading('attracting users and controlling the future of the internet were becoming very different things', 60, 790, 52, L(10), 30, col=RED); wrap(1800)

@scene(16, 'the verdict')
def s16():
    heading('not simply a company that missed google or facebook', 960, 240, 52, L(1), L(3), al='CENTER')
    heading('the difference between being where the internet is today', 960, 400, 44, L(2), L(3), al='CENTER')
    heading('and building what the internet will need tomorrow', 960, 470, 44, L(2, .8), L(3), al='CENTER', col=RED)
    CX.beat()
    heading('it helped millions of people discover the web', 960, 240, 48, L(3), L(7), al='CENTER')
    text('it created services that became part of everyday digital life', 960, 330, 34, L(4), L(7), col=GREY, font='outfit500', al='CENTER')
    heading('the industry moved: new technologies · new platforms · new business models', 960, 470, 40, L(5), L(7), al='CENTER')
    heading('yahoo struggled to lead that transition', 960, 600, 56, L(6), L(7), al='CENTER', col=RED); EV.append((T(L(6)), 'impact'))
    CX.beat()
    text('THE VERDICT', 960, 240, 26, L(7), L(9), col=GREY, font='mono600', al='CENTER')
    heading('being the front door to an industry', 960, 340, 64, L(8), L(9), al='CENTER')
    heading('does not mean you will own what comes next', 960, 450, 56, L(8, 1.0), L(9), al='CENTER', col=RED)
    CX.beat()
    e = heading('brand coroner', 943, 420, 110, L(9), 30, al='CENTER'); e2 = text('.', 1305, 420, 110, L(9, .8), 30, col=RED)
    f = text('EVERY BRAND LEAVES EVIDENCE.', 960, 570, 36, L(9, .4), 30, col=GREY, font='outfit500', al='CENTER')
    rect(810, 555, 300, 2, RED, L(9, .2), 30, grow=(L(9, .2), L(9, 1.0), 'x'))
    for st in (e, e2, f): fade(st, L(9), 30, 1, .6, 2.0)
