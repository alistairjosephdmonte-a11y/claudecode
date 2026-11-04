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

# ═══════════════════════════ ACT 01 · THE CONSEQUENCES ═══════════════════════════
@scene(1, 'two flights', 'act 01 · the consequences')
def s01():
    rect(560, 538, 800, 3, RED, .3, L(2), grow=(.3, 1.6, 'x'))
    heading('october 29, 2018', 960, 420, 96, L(1, -.3), L(2), al='CENTER')
    CX.beat()
    photo('lqp', 60, 150, 880, 560, L(2), 30, 'pk-lqp, the lion air 737 max 8 · aug 2018 · pk-ren · cc by-sa 2.0')
    text('LION AIR 610 · JAKARTA → JAVA SEA · OCT 29, 2018', 60, 740, 24, L(2), 30, col=RED, font='mono600')
    heading('189', 60, 780, 120, L(4), 30); text('lives lost', 300, 840, 34, L(4), 30, col=GREY, font='outfit500')
    photo('avj', 980, 150, 880, 560, L(5), 30, 'et-avj, the ethiopian 737 max 8 · cc by-sa 2.0')
    text('ETHIOPIAN 302 · ADDIS ABABA · MAR 10, 2019', 980, 740, 24, L(5), 30, col=RED, font='mono600')
    heading('157', 980, 780, 120, L(6), 30); text('lives lost', 1220, 840, 34, L(6), 30, col=GREY, font='outfit500')
    rect(0, 920, 1920, 160, BG, L(7), 30); heading('346 lives lost', 960, 940, 72, L(7, 1.2), 30, col=RED, al='CENTER'); EV.append((T(L(7, 1.2)), 'low'))
    text('two aircraft · two countries · both boeing 737 max', 960, 1030, 22, L(8), 30, col=GREY, font='mono600', al='CENTER')

@scene(2, 'the grounding')
def s02():
    photo('parked', 60, 150, 1100, 760, 0, 30, PH_TAG.get('parked', ''), fx=.5, fy=.5, z0=1.0, z1=1.06)
    text('MARCH 13, 2019', 1220, 160, 30, L(2), 30, col=RED, font='mono600'); heading('faa grounds the 737 max', 1220, 200, 52, L(2), 30)
    doc('doc_eo', 1220, 290, 640, L(2, .8), 30, hls=(L(2, 1.6),))
    chips(['airlines cancel flights', 'deliveries disrupted'], 1220, 560, L(3), dt=(L(4) - L(3)), size=36, gap=70)
    heading('a crisis beyond financial losses', 1220, 740, 40, L(5), 30, col=GREY)
    heading('how did a certified aircraft', 1220, 840, 40, L(6), 30); heading('reach two catastrophes?', 1220, 892, 40, L(6, 1), 30, col=RED)

# ═══════════════════════════ ACT 02 · THE COMPETITIVE DECISION ═══════════════════════════
@scene(3, 'the rival', 'act 02 · the competitive decision')
def s03():
    photo('neo', 60, 150, 1100, 700, 0, 30, PH_TAG.get('neo', ''), fx=.5, fy=.5, z0=1.0, z1=1.06)
    text('DECEMBER 2010', 1220, 160, 30, L(1), 30, col=RED, font='mono600'); heading('airbus launches', 1220, 200, 52, L(1), 30); heading('the a320neo', 1220, 260, 72, L(1, .4), 30, col=RED)
    heading('new engines → better fuel efficiency', 1220, 400, 34, L(3), 30)
    text('THE CHALLENGE FOR BOEING', 1220, 500, 22, L(4), 30, col=GREY, font='mono600')
    heading('the 737: one of the most successful', 1220, 540, 34, L(5), 30); heading('aircraft families in history', 1220, 584, 34, L(5), 30)
    heading('airlines wanted better fuel economics', 1220, 680, 34, L(6), 30, col=GREY)
    heading('boeing needed an answer.', 60, 900, 56, L(7), 30, col=RED); EV.append((T(L(7)), 'low'))

@scene(4, 'the decision')
def s04():
    for k, (a_, b_, t) in enumerate([('A', 'an all-new aircraft', L(1)), ('B', 'update the existing 737', L(2))]):
        x = 60 + k * 930; card_box(x, 150, 870, 200, t, 30, edge=GREY if k == 0 else RED)
        text(f'OPTION {a_}', x + 40, 180, 24, t, 30, col=GREY, font='mono600'); heading(b_, x + 40, 230, 52, t, 30, col=GREY if k == 0 else TXT)
    check(1800, 170, L(3), size=64)
    rect(60, 250, 870, 5, RED, L(3), 30, grow=(L(3), L(3, .6), 'x'))
    text('AUGUST 2011', 990, 400, 28, L(4), 30, col=RED, font='mono600'); heading('boeing launches the 737 max', 990, 440, 56, L(4), 30)
    text('THE COMMERCIAL ADVANTAGES', 60, 560, 22, L(5), 30, col=GREY, font='mono600')
    chips(['an established aircraft family', 'an existing customer base', 'fewer differences for pilots and airlines'], 60, 600, L(6), dt=1.0, size=36, gap=70)
    heading('the cost: larger engines on a decades-old design', 990, 620, 34, L(7), 30, col=GREY)
    heading('one solution became central to the investigations', 990, 700, 34, L(8), 30, col=RED)

# ═══════════════════════════ ACT 03 · THE HIDDEN SYSTEM ═══════════════════════════
@scene(5, 'the engineering challenge', 'act 03 · the hidden system')
def s05():
    photo('leap', 60, 150, 900, 640, 0, 30, PH_TAG.get('leap', ''), fx=.5, fy=.5, z0=1.0, z1=1.08)
    heading('larger engines', 1020, 160, 56, L(1), 30); heading('positioned differently', 1020, 224, 56, L(1, .6), 30, col=GREY)
    text('→ changed aerodynamic behaviour in certain flight conditions', 1020, 320, 26, L(2), 30, font='outfit500', wrap=840)
    card_box(1020, 420, 840, 170, L(3), 30); text('BOEING’S FLIGHT-CONTROL FUNCTION', 1050, 440, 22, L(3), 30, col=GREY, font='mono600')
    heading('MCAS', 1050, 474, 80, L(3, .3), 30, col=RED); text('maneuvering characteristics augmentation system', 1050, 560, 20, L(3, .6), 30, col=GREY, font='mono400')
    text('purpose: handling characteristics that meet certification requirements', 1020, 620, 22, L(4), 30, col=GREY, font='mono400', wrap=840)
    text('THE CRITICAL QUESTIONS', 60, 840, 22, L(6), 30, col=GREY, font='mono600')
    for k, s_ in enumerate(['what information?', 'how much authority?', 'what if it goes wrong?']):
        heading(s_, 60 + k * 620, 880, 44, L(6, k * 1.0), 30, col=RED if k == 2 else TXT)

@scene(6, 'the invisible system')
def s06():
    text('illustrative schematic · not to scale', 60, 84, 20, 0, 30, col=GREY, font='mono400')
    schematic('sch_plane', 160, 220, 1600, .2, 30)
    heading('MCAS', 1500, 150, 56, L(1), 30, col=RED)
    text('automatic nose-down stabilizer trim · manual flight, specific conditions', 60, 160, 24, L(1), 30, font='mono600', wrap=1300)
    vline(1660, 470, 640, L(1, 1), 30, L(1, 1), L(1, 2))        # stabilizer trim arrow (tail, nose-down)
    text('stabilizer', 1690, 560, 22, L(1, 1.5), 30, col=RED, font='mono600')
    heading('normally: no special pilot attention', 60, 760, 40, L(2), 30, col=GREY)
    rect(60, 840, 1800, 120, PANEL, L(4), 30); rect(60, 840, 6, 120, RED, L(4), 30)
    heading('incorrect angle-of-attack data  →  unneeded nose-down trim', 100, 876, 40, L(4), 30)
    EV.append((T(L(4)), 'low'))

@scene(7, 'the single sensor')
def s07():
    schematic('sch_aoa', 60, 150, 760, .2, 30); tag('illustrative diagram · not to scale', 60, 124, 0, 30)
    text('aoa vane', 100, 680, 22, L(1), 30, col=TXT, font='mono600'); text('angle of attack', 60, 420, 22, L(2), 30, col=RED, font='mono600')
    text('reference line', 560, 520, 20, L(2), 30, col=GREY, font='mono400'); text('airflow', 60, 600, 20, L(2), 30, col=RED, font='mono400')
    text('ORIGINAL MCAS DESIGN', 900, 150, 24, L(1), 30, col=GREY, font='mono600')
    card_box(900, 200, 360, 110, L(1, .5), 30); heading('AOA SENSOR 1', 1080, 236, 32, L(1, .5), 30, al='CENTER')
    card_box(900, 340, 360, 110, L(1, .9), 30, edge=GREY); heading('AOA SENSOR 2', 1080, 376, 32, L(1, .9), 30, col=GREY, al='CENTER')
    text('not compared', 1080, 460, 20, L(1, 1.4), 30, col=GREY, font='mono400', al='CENTER')
    hline(1270, 1480, 255, L(1, 1.6), 30, L(1, 1.6), L(1, 2.4)); card_box(1500, 200, 360, 110, L(1, 2.4), 30); heading('MCAS', 1680, 228, 44, L(1, 2.4), 30, col=RED, al='CENTER')
    text('one sensor at a time', 1500, 320, 20, L(1, 2.6), 30, col=RED, font='mono600')
    text('angle of attack: aircraft reference line vs. oncoming airflow', 900, 520, 24, L(2), 30, font='mono400', wrap=960)
    chips(['erroneous reading → activation without a stall', 'repeated activation after pilot counter-trim'], 900, 600, L(3), dt=L(4) - L(3), size=32, gap=64)
    heading('one faulty input → a much larger problem', 60, 920, 48, L(6), 30, col=RED); EV.append((T(L(6)), 'low'))

@scene(8, 'the pilot assumption')
def s08():
    photo('cockpit', 60, 150, 900, 620, 0, 30, PH_TAG.get('cockpit', ''), fx=.5, fy=.5, z0=1.0, z1=1.06)
    heading('many pilots had not been told', 1020, 160, 44, L(2), 30); heading('about MCAS', 1020, 214, 44, L(2), 30, col=RED)
    text('before the first accident', 1020, 274, 24, L(2, .5), 30, col=GREY, font='mono600')
    text('BOEING’S SAFETY ASSESSMENTS ASSUMED', 1020, 360, 22, L(3), 30, col=GREY, font='mono600')
    heading('crews would quickly recognize and respond', 1020, 400, 34, L(3, .5), 30)
    text('REAL EMERGENCIES', 1020, 500, 22, L(4), 30, col=GREY, font='mono600')
    for k, (s_, t) in enumerate([('warnings arrive together', L(5)), ('workload escalates', L(6)), ('seconds to resolve conflicting information', L(7))]):
        check(1020, 540 + k * 70, t, ok=False, size=36); heading(s_, 1070, 544 + k * 70, 34, t, 30)
    heading('did certification account for human realities?', 60, 900, 44, L(8), 30, col=RED)

# ═══════════════════════════ ACT 04 · THE WARNING SIGNS ═══════════════════════════
@scene(9, 'lion air flight 610', 'act 04 · the warning signs')
def s09():
    photo('lqp', 60, 150, 900, 600, 0, 30, 'pk-lqp · aug 2018 · pk-ren · cc by-sa 2.0')
    text('OCTOBER 29, 2018 · JAKARTA', 1020, 150, 26, L(1), 30, col=RED, font='mono600'); heading('lion air 610', 1020, 190, 72, L(1), 30)
    for k, (s_, t) in enumerate([('erroneous angle-of-attack data', L(1, 1.5)), ('repeated nose-down trim (MCAS)', L(2)), ('multiple indications, control difficulty', L(3))]):
        y = 320 + k * 76; card_box(1020, y, 840, 60, t, 30); heading(s_, 1050, y + 12, 32, t, 30)
    heading('189 lives lost', 1020, 560, 48, L(4), 30, col=RED)
    text('KNKT (INDONESIA) · CONTRIBUTING FACTORS INCLUDED', 60, 800, 22, L(5), 30, col=GREY, font='mono600')
    for k, s_ in enumerate(['design assumptions', 'system behaviour', 'maintenance', 'crew circumstances']):
        heading(s_, 60 + k * 460, 840, 36, L(5, .5 + k * .5), 30)
    heading('the 737 max remained in service', 60, 930, 48, L(7), 30, col=RED); EV.append((T(L(7)), 'low'))

@scene(10, 'ethiopian airlines flight 302')
def s10():
    photo('avj', 60, 150, 900, 600, 0, 30, 'et-avj · llbg spotter · cc by-sa 2.0')
    text('MARCH 10, 2019 · ADDIS ABABA → NAIROBI', 1020, 150, 26, L(1), 30, col=RED, font='mono600'); heading('ethiopian 302', 1020, 190, 72, L(1), 30)
    for k, (s_, t) in enumerate([('erroneous angle-of-attack data', L(2)), ('unwanted MCAS activation', L(2, 1)), ('rapidly deteriorating situation', L(3))]):
        y = 320 + k * 76; card_box(1020, y, 840, 60, t, 30); heading(s_, 1050, y + 12, 32, t, 30)
    heading('157 lives lost', 1020, 560, 48, L(4), 30, col=RED)
    text('the accidents were not identical · ntsb and bea disputed parts of ethiopia’s final report (dec 2022)', 60, 800, 22, L(5), 30, col=GREY, font='mono400', wrap=1800)
    heading('MCAS: impossible to ignore', 60, 860, 48, L(7), 30)
    heading('the crisis was now global.', 1000, 860, 48, L(8), 30, col=RED); EV.append((T(L(8)), 'low'))

# ═══════════════════════════ ACT 05 · THE INVESTIGATION ═══════════════════════════
@scene(11, 'the documents', 'act 05 · the investigation')
def s11():
    doc('doc_hrcover', 60, 150, 440, 0, 30)
    tag('u.s. house t&i committee · final committee report · sept 2020 · majority staff · public domain', 60, 124, 0, 30)
    text('THE REPORT IDENTIFIED', 1620, 160, 22, L(2), 30, col=GREY, font='mono600')
    text('commercial goals shaped the program · information not adequately shared with regulators and pilots', 1620, 200, 24, L(3), 30, font='outfit500', wrap=250)
    doc('doc_hrp19', 560, 150, 470, L(2), 30, hls=(L(2, .4),))
    doc('doc_hrp20', 1090, 150, 470, L(2, 1.5), 30, hls=(L(2, 2.0), L(4)))
    for k, s_ in enumerate(['production pressures', 'faulty design and performance assumptions', 'culture of concealment', 'inadequate regulatory oversight']):
        x = 60 + (k % 2) * 930; y = 820 + (k // 2) * 64; check(x, y - 6, L(2, k * 1.0), size=36); heading(s_, x + 50, y, 34, L(2, k * 1.0), 30)
    heading('not one software function — how was it approved?', 60, 960, 40, L(5), 30, col=RED)

@scene(12, 'the oversight failure')
def s12():
    photo('faa', 60, 150, 760, 520, 0, 30, PH_TAG.get('faa', ''), fx=.5, fy=.5, z0=1.0, z1=1.05)
    text('LAYERS OF PROTECTION', 900, 150, 24, L(1), 30, col=GREY, font='mono600')
    Lyr = [('engineers identify hazards', L(2)), ('manufacturers assess risks', L(3)), ('regulators review compliance', L(4)), ('pilots get information and training', L(5))]
    for k, (s_, t) in enumerate(Lyr):
        y = 200 + k * 100; card_box(900, y, 960, 80, t, 30); heading(s_, 940, y + 20, 36, t, 30)
        rect(1700, y + 20, 140, 40, RED, L(6, k * .4), 30); text('weakness', 1770, y + 26, 22, L(6, k * .4), 30, col=BG, font='mono600', al='CENTER'); EV.append((T(L(6, k * .4)), 'mark'))
    text('JATR (FAA-COMMISSIONED), OCT 2019: HOW MCAS CHANGES WERE EVALUATED', 60, 720, 22, L(7), 30, col=GREY, font='mono600')
    text('HOUSE REPORT: DELEGATED CERTIFICATION OVERSIGHT QUESTIONED', 60, 760, 22, L(8), 30, col=GREY, font='mono600')
    heading('not one failed safeguard.', 60, 860, 56, L(9), 30); heading('the interaction of several.', 60, 930, 56, L(10), 30, col=RED); EV.append((T(L(10)), 'low'))

# ═══════════════════════════ ACT 06 · THE RECKONING ═══════════════════════════
@scene(13, 'the financial reckoning', 'act 06 · the reckoning')
def s13():
    text('JULY 18, 2019', 60, 150, 28, L(2), 30, col=RED, font='mono600')
    heading('$4.9B', 60, 190, 200, L(2), 30); text('after-tax charge · estimated customer considerations', 64, 410, 26, L(2, .5), 30, col=GREY, font='mono600')
    doc('doc_charge', 60, 470, 860, L(2, 1.0), 30, hls=(L(2, 1.8),))
    chips(['production', 'deliveries', 'airline schedules', 'earnings'], 60, 700, L(3), dt=.6, size=32, gap=56)
    text('2019 · COMMERCIAL AIRPLANES', 1000, 150, 28, L(4), 30, col=RED, font='mono600')
    heading('$6.7B', 1000, 190, 200, L(4), 30, col=RED); text('loss from operations ($6,657M)', 1004, 410, 26, L(4, .5), 30, col=GREY, font='mono600')
    doc('doc_bca', 1000, 470, 860, L(4, 1.0), 30, hls=(L(4, 1.8),))
    text('different measures · not a single total cost of the crisis', 1000, 700, 26, L(5), 30, font='mono600', col=TXT)
    heading('no figure can represent 346 lives.', 1000, 860, 44, L(6), 30, col=RED); EV.append((T(L(6)), 'low'))

@scene(14, 'the return')
def s14():
    photo('maxfly', 60, 150, 900, 600, 0, 30, PH_TAG.get('maxfly', ''), fx=.5, fy=.5, z0=1.0, z1=1.06)
    text('THE REVISED MCAS', 1020, 150, 24, L(2), 30, col=GREY, font='mono600')
    for k, s_ in enumerate(['compares both AoA sensors', 'limited authority', 'revised training and procedures']):
        y = 200 + k * 90; card_box(1020, y, 840, 70, L(2, k * 1.2) if k < 2 else L(3), 30); check(1040, y + 10, L(2, k * 1.2) if k < 2 else L(3), size=40); heading(s_, 1100, y + 16, 34, L(2, k * 1.2) if k < 2 else L(3), 30)
    text('NOVEMBER 18, 2020', 1020, 500, 28, L(4), 30, col=RED, font='mono600'); heading('faa: return to service (u.s.)', 1020, 540, 44, L(4), 30)
    text('with required modifications (AD 2020-24-02) and training', 1020, 600, 22, L(4, .5), 30, col=GREY, font='mono400')
    text('other jurisdictions followed in stages', 1020, 650, 22, L(5), 30, col=GREY, font='mono400')
    heading('certification restored ≠ trust restored', 60, 880, 52, L(6), 30, col=RED); EV.append((T(L(6)), 'low'))

@scene(15, 'the real failure')
def s15():
    heading('caused by competition with airbus?', 960, 160, 52, L(1), L(4), al='CENTER', col=GREY)
    heading('context — not the cause', 960, 380, 96, L(2), L(4), al='CENTER', col=RED); EV.append((T(L(2)), 'impact'))
    heading('competition alone did not cause the crashes', 960, 600, 44, L(3), L(4), al='CENTER')
    CX.beat()
    text('MULTIPLE DEFENSES THAT FAILED', 60, 150, 24, L(4), 30, col=GREY, font='mono600')
    for k, (s_, t) in enumerate([('design decisions', L(5)), ('incorrect safety assumptions', L(6)), ('insufficient communication', L(7)), ('weaknesses in certification oversight', L(8)), ('pilot response under real conditions', L(9))]):
        y = 210 + k * 110; card_box(60, y, 1800, 90, t, 30); check(90, y + 18, t, size=48); heading(s_, 170, y + 22, 44, t, 30)
    heading('a dangerous design entered — and stayed in — service', 960, 790 + 3 * 0, 40, L(10), 30, col=RED, al='CENTER')

@scene(16, 'the final verdict')
def s16():
    heading('commercial success  ≠  engineering responsibility', 960, 200, 52, L(1), L(4), al='CENTER')
    for k, s_ in enumerate(['deadlines met', 'customers won', 'competitive']):
        heading(s_, 300 + k * 660, 400, 44, L(2, k * .6), L(4), col=GREY, al='CENTER')
    heading('no substitute for rigorous safety design and independent oversight', 960, 560, 36, L(3), L(4), al='CENTER', col=RED)
    CX.beat()
    heading('do decisions remain safe', 960, 300, 72, L(5), L(8, 2), al='CENTER'); heading('when assumptions prove wrong?', 960, 390, 72, L(5, .6), L(8, 2), al='CENTER', col=RED)
    heading('346', 960, 560, 160, L(7), L(9), al='CENTER'); text('lives lost · lion air 610 and ethiopian 302', 960, 750, 26, L(7, .5), L(9), col=GREY, font='mono600', al='CENTER')
    EV.append((T(L(7)), 'low'))
    CX.beat()
    e = heading('brand coroner', 943, 420, 110, L(9), 30, al='CENTER'); e2 = text('.', 1305, 420, 110, L(9, .8), 30, col=RED)
    f = text('EVERY BRAND LEAVES EVIDENCE.', 960, 570, 36, L(9, .4), 30, col=GREY, font='outfit500', al='CENTER')
    rect(810, 555, 300, 2, RED, L(9, .2), 30, grow=(L(9, .2), L(9, 1.0), 'x'))
    for st in (e, e2, f): fade(st, L(9), 30, 1, .6, 2.0)
