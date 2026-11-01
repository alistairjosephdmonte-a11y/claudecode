"""The 16 scene sequences. Each function builds one 30 s Blender scene (720 frames) with its own orthographic camera.
Beats live in separate regions of the canvas (x = 0, 40, 80); a jump between regions is a cut, a move within one is a
motivated camera move. Every number on screen is taken from config.FACTS or read from a document crop."""
import config as C
from toolkit import Scene

ACT = {n: f"{a[0].lower()} · {a[1]}" for a in C.ACTS for n in a[2]}
H1, H2, H3, BODY, LAB = 1.25, 0.62, 0.36, 0.26, 0.2


def new(n):
    S = Scene(n)
    S.header(ACT[n], C.SCENES[n][0])
    for b0, b1, _, src in C.SCENES[n][1]:
        if src:
            S.source(src, b0, b1)
    return S


def stack(S, x, y, rows, t, gap=0.06, align="CENTER", stagger=0.5):
    """rows: (text, size, color, font). Builds a vertical stack top-down from y; returns objects (faded in staggered)."""
    out = []
    for i, (body, size, color, fnt) in enumerate(rows):
        o = S.text(body, x, y, size, color, fnt, align)
        S.life(o, t + i * stagger, d=0.5)
        out.append(o)
        y -= (size + (rows[i + 1][1] if i + 1 < len(rows) else 0)) * 0.62 + gap
    return out


def node(S, x, y, label, t, r=0.95, color="type", sub=None):
    o = [S.ring(x, y, r, 0.04, color), S.text(label, x, y - r - 0.42, H3, color, "bold", "CENTER")]
    if sub:
        o.append(S.text(sub, x, y - r - 0.85, 0.2, "gray", "semi", "CENTER"))
    S.life(o, t, d=0.6)
    return o


def timeline_event(S, x, y, date, label, t, color="type", up=True, dsize=0.36):
    dy = 1 if up else -1
    o = [S.disc(x, y, 0.09, "red"), S.ring(x, y, 0.2, 0.025, "red"),
         S.text(date, x, y + dy * 0.62, dsize, color, "bold", "CENTER"),
         S.text(label, x, y + dy * 0.62 - 0.4 * (1 if up else -1) + (0 if up else 0), 0.2, "gray", "semi", "CENTER")]
    if not up:
        o[2].location.y, o[3].location.y = y - 0.55, y - 0.95
    else:
        o[2].location.y, o[3].location.y = y + 0.95, y + 0.55
    S.life(o, t, d=0.4)
    return o


# ===================================================================== ACT 01
def sc01():
    S = new(1)
    # beat 1 · black, a red line, the number
    S.line(-9, 1.45, 18, 0.5, 2.8)
    num = S.text("$47,000,000,000", 0, -0.05, 1.3, "type", "display", "CENTER")
    S.life(num, 2.4, d=1.0)
    S.move(num, [(2.4, (0, -0.35)), (3.6, (0, -0.05))])
    lab = S.text("2019 · private valuation", 0, -1.3, 0.32, "gray", "semi", "CENTER")
    S.life(lab, 4.6, d=0.6)
    # beat 2 · the company the number described (photograph slot)
    ph = S.placeholder("P01", 36.6, 0.0, 7.4, 4.9)
    g = S.group(36.6, 0)
    S.parent(ph, g)
    S.move(g, [(9.0, (36.45, 0)), (17.0, (36.75, 0))])
    S.life(ph, 9.0, d=0.6)
    stack(S, 41.2, 1.35, [("2019", 0.9, "red", "display"), ("$47 billion", 0.8, "type", "display"),
                          ("private valuation (reported)", 0.24, "gray", "semi")], 9.8, align="LEFT")
    # beat 3 · split screen: 2019 against 2023
    S.vline(80, -1.9, 5.0, 17.2, 18.0)
    y19 = S.text("2019", 76, 2.55, 0.62, "gray", "display", "CENTER")
    y23 = S.text("2023", 84, 2.55, 0.62, "red", "display", "CENTER")
    S.life([y19], 17.6, d=0.5)
    S.life([y23], 18.4, d=0.5)
    left = [S.text("$47 billion", 76, 0.55, 0.85, "type", "display", "CENTER"),
            S.text("private valuation · reported", 76, -0.45, 0.22, "gray", "semi", "CENTER")]
    S.life(left, 17.8, d=0.6)
    d = S.doc("D02_8K_CH11", 84, 0.5, 6.4)
    S.life(d.objs, 18.6, d=0.6)
    hl = d.highlight("On November 6, 2023", 19.6)
    right = [S.text("bankruptcy protection · chapter 11", 84, -1.45, 0.3, "type", "bold", "CENTER")]
    S.life(right, 20.2, d=0.6)
    link = [S.disc(76.75, 2.55, 0.07, "red"), S.disc(83.25, 2.55, 0.07, "red")]
    S.life(link, 20.6, d=0.3)
    ln = S.line(76.75, 2.55, 6.5, 20.8, 22.4)
    q = S.text("what went wrong?", 80, -2.85, 0.82, "type", "display", "CENTER")
    S.dim(left + right + d.objs + hl + [y19], 24.6, to=0.3)
    S.life(q, 25.0, d=0.8)
    S.shots([[(0, 0, 0, 16.0), (9, 0, 0.05, 14.9)],
             [(9, 40, 0, 15.6), (17, 40.35, 0, 15.1)],
             [(17, 80, 0.1, 16.0), (24.4, 80, 0.0, 15.6), (30, 80, -0.55, 14.6)]])
    S.fade_black(29.4, 30, 0, 0)
    return S, [ln]


def sc02():
    S = new(2)
    d = S.doc("D02_8K_CH11", 0, 0.2, 13.0)
    S.life(d.objs, 0.0, d=0.7)
    cx, cy, w, h = d.center("On November 6, 2023")
    d.focus("On November 6, 2023", 2.6)
    d.highlight("On November 6, 2023", 2.2)
    d.highlight("Chapter 11", 4.4)
    lab = S.text("petition date · november 6, 2023", cx - w / 2, 0.2 + d.h / 2 + 0.4, 0.26, "red", "bold", "LEFT")
    S.life(lab, 5.4, d=0.5)
    # beat 2-3 · landlord -> wework -> member
    L, W, M, Y = 34.0, 40.0, 46.0, 0.55
    node(S, L, Y, "landlord", 10.4)
    node(S, W, Y, "wework", 11.0, color="red")
    node(S, M, Y, "member", 11.6)
    rails = [S.rect((L + W) / 2, Y + 0.32, W - L - 2.1, 0.012, "rule", 1.0), S.rect((W + M) / 2, Y - 0.32, M - W - 2.1, 0.012, "rule", 1.0)]
    S.life(rails, 12.4, d=0.5)
    S.flow(W - 1.1, Y + 0.32, L + 1.1, Y + 0.32, 13.0, 29.7, "red", n=7, period=2.6)
    S.flow(M - 1.1, Y - 0.32, W + 1.1, Y - 0.32, 14.4, 29.7, "type", n=7, period=2.6)
    rl = [S.text("rent", (L + W) / 2, Y + 0.72, 0.24, "red", "bold", "CENTER"),
          S.text("membership fees", (W + M) / 2, Y - 0.72, 0.24, "type", "bold", "CENTER")]
    S.life(rl[:1], 13.2, d=0.5)
    S.life(rl[1:], 14.6, d=0.5)
    a = S.text("long-term leases", L, Y - 2.25, 0.42, "red", "display", "CENTER")
    b = S.text("flexible customers", M, Y - 2.25, 0.42, "type", "display", "CENTER")
    ne = S.text("≠", W, Y - 2.25, 0.62, "red", "display", "CENTER")
    S.life(b, 21.6, d=0.6)
    S.life(a, 22.6, d=0.6)
    S.life(ne, 24.4, d=0.6)
    S.shots([[(0, 0, 0.2, 15.6), (2.2, 0, 0.2, 15.2), (10, cx - 0.6, cy - 0.35, 9.2)],
             [(10, 40, 0.2, 16.4), (21, 40, 0.1, 16.2), (30, 40, -0.45, 15.8)]])
    return S, []


# ===================================================================== ACT 02
def sc03():
    S = new(3)
    S.fade_black(0, 0.6, 1, 0)
    S.vline(0, -2.9, 5.6, 0.4, 1.2)
    hl = [S.text("traditional office", -4.0, 2.25, 0.46, "gray", "display", "CENTER"),
          S.text("flexible workspace", 4.0, 2.25, 0.46, "type", "display", "CENTER")]
    S.life(hl[:1], 0.8, d=0.5)
    S.life(hl[1:], 1.4, d=0.5)
    li = ["sign a long lease", "build out the space", "furnish and run it", "fixed footprint"]
    ri = ["furnished offices", "shared workspaces", "meeting rooms", "flexible membership"]
    for i, (a, b) in enumerate(zip(li, ri)):
        y = 1.1 - i * 0.8
        o1 = [S.rect(-6.3, y, 0.12, 0.12, "gray", 1.0), S.text(a, -5.95, y, BODY, "gray", "semi")]
        o2 = [S.rect(1.7, y, 0.12, 0.12, "red", 1.0), S.text(b, 2.05, y, BODY, "type", "semi")]
        S.life(o1, 2.4 + i * 0.6, d=0.4)
        S.life(o2, 2.7 + i * 0.6, d=0.4)
    # beat 2 · collage of photograph slots (restrained drift)
    for i, (pid, x, y, w, h) in enumerate([("P02", 37.1, -0.2, 6.2, 5.6), ("P03", 43.2, 1.75, 5.0, 1.75),
                                           ("P04", 43.2, -0.2, 5.0, 1.75), ("P05", 43.2, -2.15, 5.0, 1.75)]):
        o = S.placeholder(pid, x, y, w, h)
        g = S.group(x, y)
        S.parent(o, g)
        dx = 0.12 if i % 2 else -0.12
        S.move(g, [(10.0, (x - dx, y)), (20.0, (x + dx, y))])
        S.life(o, 10.3 + i * 0.55, d=0.5)
    # beat 3 · the first location, in the S-1's own words
    d = S.doc("D18_FIRST_LOCATION", 80, 0.9, 12.4)
    S.life(d.objs, 20.0, d=0.6)
    d.highlight("154 Grand Street in New York City", 21.4)
    t = stack(S, 80, -0.85, [("early 2010", 0.62, "red", "display"), ("154 grand street, new york", 0.32, "type", "semi")], 23.0)
    S.shots([[(0, 0, 0, 16.0), (10, 0, 0, 15.4)],
             [(10, 39.7, 0, 15.8), (20, 40.3, 0, 15.8)],
             [(20, 80, 0.3, 16.0), (30, 80, 0.2, 13.6)]])
    return S, t


def sc04():
    S = new(4)
    ph = S.placeholder("P06", -3.2, 0.0, 5.0, 6.2)
    g = S.group(-3.2, 0)
    S.parent(ph, g)
    S.move(g, [(0, (-3.3, 0)), (8, (-3.1, 0))])
    S.life(ph, 0.3, d=0.6)
    lt = [S.rect(0.55, 0.35, 0.05, 1.3, "red", 1.0),
          S.text("adam neumann", 0.85, 0.72, 0.62, "type", "display"),
          S.text("co-founder · chief executive officer until september 2019", 0.88, 0.08, 0.22, "gray", "semi")]
    S.life(lt, 1.6, d=0.6)
    S.source(["10K22"], 0, 8)
    # beat 2 · the map: one verified marker, the S-1's own totals
    import json
    import os
    gj = json.load(open(os.path.join(C.P["map"], "ne_110m_land.geojson")))
    mw, mh, mx, my = 14.4, 7.2, 40.0, 0.35
    verts, faces = [], []
    for ft in gj["features"]:
        geo = ft["geometry"]
        polys = geo["coordinates"] if geo["type"] == "MultiPolygon" else [geo["coordinates"]]
        for poly in polys:
            ring = poly[0][:-1]
            if len(ring) < 3:
                continue
            i0 = len(verts)
            verts += [(lon / 180 * mw / 2, lat / 90 * mh / 2, 0) for lon, lat in ring]
            faces.append(tuple(range(i0, len(verts))))
    me = S._mesh("land", verts, faces)
    land = S._link("land", me, mx, my, S._z(None))
    S._mat(land, "#262626", 1.0)
    S.life(land, 8.2, d=1.0)
    lon, lat = -73.9973, 40.7206                     # 154 grand street, new york (s-1: first location, early 2010)
    px, py = mx + lon / 180 * mw / 2, my + lat / 90 * mh / 2
    mk = [S.disc(px, py, 0.08, "red"), S.ring(px, py, 0.2, 0.025, "red")]
    S.life(mk, 9.6, d=0.4)
    pulse = S.ring(px, py, 0.2, 0.02, "red")
    S.scale(pulse, [(9.8, 1), (11.3, 3.2)], axes=(0, 1))
    S.alpha(pulse, [(9.8, 0.0), (10.0, 0.9), (11.3, 0.0)])
    ml = [S.rect(px + 0.18, py + 0.55, 0.012, 0.9, "red", 1.0, anchor="c"),
          S.text("154 grand street · early 2010", px + 0.28, py + 0.92, 0.2, "type", "bold")]
    S.life(ml, 10.2, d=0.4)
    stats = []
    for i, (v, l) in enumerate([("528", "locations"), ("111", "cities"), ("29", "countries")]):
        x = 35.6 + i * 4.4
        o = [S.text(v, x, -2.55, 0.75, "type", "display", "CENTER"), S.text(l, x, -3.25, 0.22, "gray", "semi", "CENTER")]
        S.life(o, 11.6 + i * 0.5, d=0.5)
        stats += o
    note = S.text("as of june 30, 2019 · single verified marker shown; per-city location data not yet sourced",
                  40, 3.55, 0.17, "gray", "semi", "CENTER")
    S.life(note, 12.5, d=0.5)
    S.dim([land] + stats + mk + ml + [note], 15.4, to=0.22)
    kw = [S.text(w, 40, 1.15 - i * 1.05, 0.72, "type", "display", "CENTER") for i, w in enumerate(["community", "growth", "global expansion"])]
    for i, o in enumerate(kw):
        S.life(o, 15.8 + i * 0.7, d=0.5)
    # beat 3 · growth is not profitability
    g1 = S.text("growth", 79.45, 0.75, 0.95, "type", "display", "RIGHT")
    ne = S.text("≠", 80.0, 0.75, 0.95, "red", "display", "CENTER")
    g2 = S.text("profitability", 80.55, 0.75, 0.95, "type", "display", "LEFT")
    S.life([g1], 20.4, d=0.5)
    S.life([ne], 21.0, d=0.5)
    S.life([g2], 21.6, d=0.5)
    q = S.text("could the economics support the ambition?", 80, -0.95, 0.4, "type", "semi", "CENTER")
    S.life(q, 24.0, d=0.8)
    S.shots([[(0, 0, 0, 16.0), (8, 0.2, 0, 15.4)],
             [(8, 40, 0.3, 15.8), (15, 40, 0.3, 15.4), (20, 40, 0.1, 15.6)],
             [(20, 80, 0.2, 16.0), (23.8, 80, 0.15, 15.8), (30, 80, -0.75, 11.8)]])
    S.fade_black(29.4, 30, 0, 1)
    return S, []


# ===================================================================== ACT 03
def sc05():
    S = new(5)
    S.fade_black(0, 0.6, 1, 0)
    Y = 0.75
    pos = {"landlord": -5.0, "wework": 0.0, "member": 5.0}
    for i, (k, x) in enumerate(pos.items()):
        node(S, x, Y, k, 0.4 + i * 0.45, color="red" if k == "wework" else "type")
    steps = []
    for i, s in enumerate(["lease", "fit-out", "operate", "collect revenue"]):
        x = -5.4 + i * 3.6
        n = S.text(f"{i + 1:02d}", x - 0.15, -2.75, 0.22, "red", "bold", "RIGHT")
        t = S.text(s, x, -2.75, 0.32, "type", "display", "LEFT")
        n["a"] = t["a"] = 1.0
        S.alpha(n, [(1.6, 0), (2.1, 0.3)])
        S.alpha(t, [(1.6, 0), (2.1, 0.3)])
        steps.append((n, t))
    cap = [S.text(c, 0, 2.95, 0.3, "type", "semi", "CENTER") for c in
           ["wework leases property from a landlord", "wework pays to fit out the space", "wework operates the workspace",
            "members pay wework for access"]]
    T = [2.8, 9.8, 15.0, 20.0, 29.7]
    for i in range(4):
        S.life(cap[i], T[i], T[i + 1] - 0.1 if i < 3 else 29.6, d=0.5)
        n, t = steps[i]
        S.alpha(n, [(T[i], 0.3), (T[i] + 0.4, 1.0)])
        S.alpha(t, [(T[i], 0.3), (T[i] + 0.4, 1.0)])
    # 1 lease: an arrow from wework to the landlord, a red lease bar under the landlord
    S.line(-1.05, Y, -2.9, 3.2, 4.6, th=0.03)
    ah = S.tri(-3.98, Y, 0.14, 3.14159, "red")
    S.life(ah, 4.5, d=0.2)
    ll = S.text("lease", -2.5, Y + 0.35, 0.22, "red", "bold", "CENTER")
    S.life(ll, 4.6, d=0.4)
    # 2 fit-out: the space fills
    grid = [S.rect(-0.42 + c * 0.42, Y + 0.42 - r * 0.42, 0.3, 0.3, "type", 1.0) for r in range(3) for c in range(3)]
    for i, o in enumerate(grid):
        S.life(o, 10.4 + i * 0.12, d=0.25)
    fo = S.text("fit-out", 0, Y + 1.32, 0.22, "red", "bold", "CENTER")
    S.life(fo, 10.6, d=0.4)
    # 3 operate: the grid pulses as a running workspace (orbiting dots)
    orb = []
    for i in range(4):
        dd = S.disc(1.2, Y, 0.07, "red")
        e = S.group(0, Y, "orbit")
        dd.parent = e
        dd.location = (1.2, 0, dd.location.z)
        e.rotation_euler.z = i * 1.5708
        e.keyframe_insert("rotation_euler", index=2, frame=1 + int(15.0 * 24))
        e.rotation_euler.z = i * 1.5708 + 6.2832
        e.keyframe_insert("rotation_euler", index=2, frame=1 + int(21.0 * 24))
        from toolkit import fcurves
        for fc in fcurves(e):
            for k in fc.keyframe_points:
                k.interpolation = "LINEAR"
            fc.modifiers.new("CYCLES")
        S.life(dd, 15.2, 29.7, d=0.4)
        orb.append(dd)
    op = S.text("operate", 1.55, Y + 1.05, 0.22, "red", "bold", "LEFT")
    S.life(op, 15.4, d=0.4)
    # 4 collect revenue: membership fees in, rent out
    S.flow(3.9, Y, 1.15, Y, 20.2, 29.7, "type", n=6, period=2.2)
    S.flow(-1.15, Y - 0.3, -3.9, Y - 0.3, 22.4, 29.7, "red", n=6, period=2.2)
    fees = S.text("membership fees", 2.5, Y + 0.35, 0.22, "type", "bold", "CENTER")
    rent = S.text("rent", -2.5, Y - 0.68, 0.22, "red", "bold", "CENTER")
    S.life(fees, 20.4, d=0.4)
    S.life(rent, 22.6, d=0.4)
    S.shots([[(0, 0, 0.1, 16.4), (20, 0, 0.15, 15.2), (30, 0, 0.1, 15.6)]])
    return S, [op]


def sc06():
    S = new(6)
    note = S.text("illustrative timeline · not actual contract terms", -7.0, 3.0, 0.2, "red", "bold")
    S.life(note, 0.4, d=0.5)
    ax = S.line(-7.0, -2.55, 40, 0.6, 2.0, th=0.012, color="gray")
    at = S.text("time", -7.0, -2.9, 0.2, "gray", "semi")
    S.life(at, 1.0, d=0.5)
    top_l = S.text("customer commitment", -7.0, 1.65, 0.34, "type", "display")
    top = S.rect(-7.0, 1.0, 3.1, 0.34, "type", 1.0, anchor="l")
    S.life(top_l, 1.2, d=0.5)
    S.grow(top, 1.6, 3.2)
    bot_l = S.text("landlord lease", -7.0, -0.55, 0.34, "red", "display")
    bot = S.rect(-7.0, -1.2, 1.0, 0.34, "red", 1.0, anchor="l")
    S.life(bot_l, 2.4, d=0.5)
    S.scale(bot, [(2.8, 0), (8.0, 13.0), (13.6, 13.0), (19.0, 26.0)])
    fr = S.text("flexible revenue", -3.65, 1.0, 0.24, "gray", "semi")
    lo = S.text("long-term obligations", -7.0, -1.75, 0.24, "gray", "semi")
    S.life(fr, 10.4, d=0.5)
    S.life(lo, 11.0, d=0.5)
    S.alpha(top, [(13.0, 1.0), (14.6, 0.0)])
    S.alpha(fr, [(13.2, 1.0), (14.6, 0.0)])
    S.alpha(top_l, [(13.4, 1.0), (15.0, 0.3)])
    rem = S.text("the longer commitment remains.", 5.4, 0.75, 0.5, "type", "display", "CENTER")
    S.life(rem, 16.8, d=0.7)
    d = S.doc("D10_RISK_FACTORS", 80, 0.55, 13.0)
    S.life(d.objs, 20.0, d=0.6)
    cx, cy, w, h = d.center("approximately 15 years")
    d.highlight("approximately 15 years", 21.6)
    d.focus("approximately 15 years", 22.0)
    cap = stack(S, 80, -1.85, [("average initial term of wework's u.s. leases: about 15 years", 0.3, "type", "bold"),
                               ("as disclosed in the s-1, august 2019", 0.2, "gray", "semi")], 23.0)
    S.shots([[(0, 0, 0, 16.0), (12.6, 0, 0, 16.0), (20, 6.2, 0, 16.0)],
             [(20, 80, 0, 16.0), (21.4, 80, 0, 16.0), (30, (80 + cx) / 2, (cy - 2.1) / 2, 12.6)]])
    return S, cap


def sc07():
    S = new(7)
    d = S.doc("D03_LEASE_TABLE", 0, 0.3, 14.0)
    S.life(d.objs, 0.0, d=0.6)
    cx, cy, w, h = d.center("33,953,402")
    band = S.rect(d.x, cy, d.w, h * 1.5, "red", 0.12, name="rowband")
    S.life(band, 3.6, d=0.6)
    d.highlight("33,953,402", 5.0)
    # beat 2 · the figure, with its exact label
    big = S.text("$33.95 billion", 40, 1.25, 1.15, "type", "display", "CENTER")
    S.life(big, 10.4, d=0.8)
    sub = stack(S, 40, 0.05, [("future minimum payments on commenced operating leases, undiscounted", 0.29, "type", "semi"),
                              ("as of june 30, 2019 · table value $33,953,402 thousand", 0.2, "gray", "semi")], 11.2)
    f = S.doc("D04_LEASE_FOOTNOTE", 40, -2.35, 14.0, crop_top=34)
    S.life(f.objs, 14.2, d=0.6)
    f.highlight("$13.1 billion", 15.4)
    f.highlight("not yet commenced", 16.4)
    # beat 3 · two separate categories, never summed
    a = stack(S, 76.0, 1.55, [("$33.95b", 1.0, "type", "display"), ("commenced operating leases", 0.26, "type", "bold"),
                              ("undiscounted future minimum payments", 0.2, "gray", "semi")], 20.4)
    b = stack(S, 84.0, 1.55, [("≈ $13.1b", 1.0, "gray", "display"), ("signed, not yet commenced", 0.26, "type", "bold"),
                              ("disclosed separately in a footnote", 0.2, "gray", "semi")], 21.6)
    S.vline(80, -0.6, 3.0, 20.6, 21.4)
    sep = S.text("separate categories · not one debt · not payable today", 80, -1.55, 0.22, "red", "bold", "CENTER")
    S.life(sep, 23.4, d=0.6)
    ext = S.line(72.6, -2.75, 40, 25.0, 29.8, th=0.035)
    S.shots([[(0, 0, 0.3, 16.0), (0.5, 0, 0.3, 16.0), (10, 7.4 - 5.0, cy - 0.1, 9.8)],
             [(10, 40, -0.1, 15.6), (20, 40, -0.45, 16.2)],
             [(20, 80, 0.15, 16.0), (24.8, 80, 0.05, 15.6), (30, 81.6, -0.15, 15.6)]])
    S.fade_black(29.4, 30, 0, 1)
    return S, [ext]


# ===================================================================== ACT 04
def sc08():
    S = new(8)
    S.fade_black(0, 0.6, 1, 0)
    d = S.doc("D01_S1_COVER", 0, 0.1, 11.0)
    S.life(d.objs, 0.0, d=0.7)
    cx, cy, w, h = d.center("August 14, 2019")
    d.highlight("August 14, 2019", 2.0)
    call = S.text("august 14, 2019", cx, 0.1 + d.h / 2 + 0.42, 0.36, "red", "display", "CENTER")
    S.life(call, 4.0, d=0.6)
    panels = []
    for i, (cid, title, mark) in enumerate([("D05_SELECTED_FINANCIALS", "financial statements", "1,821,751"),
                                            ("D10_RISK_FACTORS", "risk factors", "$47.2 billion"),
                                            ("D06_TRADEMARK", "related-party transactions", "approximately $5.9 million")]):
        x = 35.1 + i * 4.9
        p = S.doc(cid, x, 0.15, 4.5)
        t = S.text(title, x - 2.25, 0.15 + p.h / 2 + 0.4, 0.28, "type", "display")
        s = S.text("s-1 · excerpt", x - 2.25, 0.15 + p.h / 2 + 0.14, 0.15, "gray", "semi")
        objs = p.objs + [t, s]
        S.life(objs, 9.4 + i * 0.7, d=0.6)
        g = S.group(x, 0)
        S.parent(objs, g)
        S.move(g, [(9.4 + i * 0.7, (x, -0.45)), (10.4 + i * 0.7, (x, 0))])
        panels.append((x, p.h))
    pub = S.text("the evidence was public.", 80, 0.05, 0.85, "type", "display", "CENTER")
    S.life(pub, 21.8, d=0.8)
    ul = S.line(80 - 1.6, -0.75, 3.2, 23.2, 24.2, th=0.04)
    S.shots([[(0, 0, 0.1, 15.0), (1.0, 0, 0.1, 15.0), (9, cx, cy - 0.25, 10.0)],
             [(9, 40, 0.3, 16.0), (13, 40, 0.3, 15.4)],
             [(13, panels[0][0], 0.4, 6.0), (15.7, panels[0][0], 0.4, 5.6)],
             [(15.7, panels[1][0], 0.4, 5.6), (18.3, panels[1][0], 0.4, 5.2)],
             [(18.3, panels[2][0], 0.4, 5.6), (21, panels[2][0], 0.4, 5.2)],
             [(21, 80, 0, 16.0), (30, 80, -0.1, 14.6)]])
    return S, [ul]


def sc09():
    S = new(9)
    k = 3.8 / 1_000_000                              # 1 billion = 3.8 units (amounts in thousands)
    x0 = -3.0
    yr = S.text("2018", -7.0, 2.9, 0.5, "gray", "display")
    S.life(yr, 0.4, d=0.5)
    rows = [(1.15, "revenue", C.FACTS["revenue_2018_k"], "type", "$1.82 billion"),
            (-0.55, "net loss", C.FACTS["net_loss_attrib_2018_k"], "red", "$1.61 billion loss")]
    for i, (y, lab, v, colr, txt) in enumerate(rows):
        t0 = 1.6 + i * 2.4
        L = S.text(lab, x0 - 0.3, y, 0.4, colr, "display", "RIGHT")
        S.life(L, t0 - 0.4, d=0.4)
        b = S.rect(x0, y, v * k, 0.62, colr, 1.0, anchor="l")
        S.grow(b, t0, t0 + 1.8)
        vt = S.text(txt, x0 + v * k + 0.25, y, 0.36, colr, "bold")
        S.life(vt, t0 + 1.6, d=0.4)
    nl = S.text("net loss attributable to wework companies inc. · a loss, not an expense line · "
                "total net loss incl. noncontrolling interests: $1.93 billion", x0, -1.2, 0.17, "gray", "semi", width=10.6)
    S.life(nl, 5.6, d=0.5)
    ax = [S.rect(x0, -2.1, 2.0 * 1_000_000 * k, 0.012, "rule", 1.0, anchor="l")]
    for i, v in enumerate([0, 0.5, 1.0, 1.5, 2.0]):
        x = x0 + v * 1_000_000 * k
        ax += [S.rect(x, -2.1, 0.012, 0.16, "rule", 1.0), S.text(["$0", "$0.5b", "$1b", "$1.5b", "$2b"][i], x, -2.4, 0.17, "gray", "semi", "CENTER")]
    S.life(ax, 1.2, d=0.5)
    sc = S.text("bars drawn to scale", 7.0, -2.4, 0.15, "gray", "semi", "RIGHT")
    S.life(sc, 1.4, d=0.5)
    # beat 2 · the rows in the filing
    d = S.doc("D05_SELECTED_FINANCIALS", 40, 0.0, 13.6)
    S.life(d.objs, 12.0, d=0.6)
    r1 = d.center("1,821,751")
    r2 = d.center("(1,610,792)")
    lab = d.center("Net loss attributable to WeWork Companies Inc.")
    d.highlight("1,821,751", 13.6)
    d.highlight("(1,610,792)", 15.2)
    d.highlight("Net loss attributable to WeWork Companies Inc.", 15.6, fill=0.12)
    d.highlight("(1,927,419)", 17.4, fill=0.1, underline=False, color="gray")
    # beat 3 · revenue was growing
    base = -2.3
    kk = 2.2 / 1_000_000
    for i, (yv, v) in enumerate([("2016", C.FACTS["revenue_2016_k"]), ("2017", C.FACTS["revenue_2017_k"]), ("2018", C.FACTS["revenue_2018_k"])]):
        x = 75.6 + i * 1.3
        b = S.rect(x, base, 0.85, v * kk, "type", 1.0, anchor="b")
        S.grow(b, 22.4 + i * 0.4, 23.6 + i * 0.4, axes=(1,))
        lbl = [S.text(yv, x, base - 0.3, 0.2, "gray", "semi", "CENTER"),
               S.text(f"${v / 1_000_000:.2f}b", x, base + v * kk + 0.25, 0.2, "type", "bold", "CENTER")]
        S.life(lbl, 23.2 + i * 0.4, d=0.4)
    rv = S.text("revenue (s-1)", 75.0, base - 0.75, 0.17, "gray", "semi")
    S.life(rv, 23.4, d=0.4)
    w1 = S.text("revenue was growing.", 79.6, 0.55, 0.62, "type", "display")
    w2 = S.text("so were the questions.", 79.6, -0.45, 0.62, "red", "display")
    S.life(w1, 24.6, d=0.6)
    S.life(w2, 26.0, d=0.6)
    S.shots([[(0, 0, 0.1, 16.0), (12, 0, 0.1, 15.2)],
             [(12, 40, 0, 16.0), (15.4, 40, 0, 16.0), (21.5, (lab[0] - lab[2] / 2 + r1[0] + r1[2] / 2) / 2, (r1[1] + r2[1]) / 2,
                                                 max(9.4, (r1[0] + r1[2] / 2) - (lab[0] - lab[2] / 2) + 1.2))],
             [(22, 82.2, 0, 15.6), (30, 82.0, 0, 15.0)]])
    return S, []


def sc10():
    S = new(10)
    d = S.doc("D06_TRADEMARK", 0, 0.8, 12.0)
    S.life(d.objs, 0.0, d=0.6)
    cx, cy, w, h = d.center("approximately $5.9 million")
    d.highlight("approximately $5.9 million", 1.8)
    d.highlight("in lieu of paying cash", 3.4)
    cal = stack(S, 0, -1.75, [("trademark transaction · about $5.9 million", 0.42, "type", "display"),
                              ("paid in partnership interests, not cash", 0.24, "gray", "semi")], 6.4)
    u = S.doc("D07_TRADEMARK_UNWOUND", 40, 0.75, 12.0)
    S.life(u.objs, 10.0, d=0.6)
    u.highlight("Unwinding of Receipt of Partnership Interests", 11.0)
    un = stack(S, 40, -1.45, [("later unwound", 0.6, "red", "display"), ("disclosed in the s-1/a filed september 4, 2019", 0.24, "gray", "semi")], 12.4)
    # beat 3 · votes per share as proposed on august 14, then amended on september 13
    a = [S.text("class a share", 75.6, 2.35, 0.3, "type", "display", "CENTER"), S.rect(75.6, 0.85, 0.42, 0.42, "type", 1.0),
         S.text("1 vote", 75.6, -0.15, 0.36, "type", "bold", "CENTER")]
    S.life(a, 18.4, d=0.5)
    hv = [S.text("high-vote share (class b / class c)", 84.0, 2.35, 0.3, "type", "display", "CENTER")]
    S.life(hv, 19.0, d=0.5)
    sq = []
    for i in range(20):
        r, c = divmod(i, 5)
        o = S.rect(84.0 - 1.08 + c * 0.54, 1.55 - r * 0.54, 0.42, 0.42, "red", 1.0)
        S.life(o, 19.4 + i * 0.06, d=0.2)
        sq.append(o)
    v20 = S.text("20 votes", 84.0, -0.95, 0.36, "red", "bold", "CENTER")
    S.life(v20, 20.6, 24.4, d=0.4)
    v10 = S.text("10 votes after the s-1/a of september 13, 2019", 84.0, -0.95, 0.24, "type", "bold", "CENTER")
    S.life(v10, 24.6, d=0.4)
    for o in sq[10:]:
        S.alpha(o, [(23.6, 1.0), (24.4, 0.16)])
    cap = S.text("as proposed in the s-1 filed august 14, 2019", 80, -1.75, 0.2, "gray", "semi", "CENTER")
    S.life(cap, 20.8, d=0.5)
    q = S.text("who controlled the company?", 80, -2.85, 0.62, "type", "display", "CENTER")
    S.life(q, 26.6, d=0.7)
    S.shots([[(0, 0, 0.3, 15.6), (1.2, 0, 0.3, 15.6), (10, cx * 0.45, -0.1, 12.4)],
             [(10, 40, 0, 16.0), (18, 40, 0, 15.0)],
             [(18, 80, 0.15, 16.0), (26.2, 80, 0.1, 16.0), (30, 80, -0.4, 15.4)]])
    S.fade_black(29.4, 30, 0, 1)
    return S, []


# ===================================================================== ACT 05
def sc11():
    S = new(11)
    S.fade_black(0, 0.5, 1, 0)
    Y = 0.35
    line = S.rect(-9.0, Y, 1.0, 0.045, "red", 1.0, anchor="l")
    S.scale(line, [(0.4, 0.0), (2.2, 9.0), (6.2, 9.0), (10.6, 23.0), (15.6, 23.0), (20.0, 36.8), (21.4, 36.8), (21.45, 35.4)])
    e1 = timeline_event(S, 0, Y, "august 14, 2019", "ipo registration · form s-1 filed", 2.0)
    t1 = S.doc("D01_S1_COVER", 0, -1.6, 4.6)
    S.life(t1.objs, 2.6, d=0.5)
    t1.highlight("August 14, 2019", 3.4, underline=False)
    e2 = timeline_event(S, 14, Y, "september 2019", "adam neumann steps down as ceo", 10.4)
    p = S.placeholder("P07", 14, -1.75, 4.6, 2.5)
    S.life(p, 10.8, d=0.5)
    e3 = timeline_event(S, 28, Y, "september 30, 2019", "ipo withdrawn · form rw", 19.8)
    t3 = S.doc("D11_RW_WITHDRAWAL", 28, -1.75, 4.0, crop_top=20)
    S.life(t3.objs, 20.0, d=0.5)
    t3.highlight("consent to the withdrawal of the Registration Statement", 20.8, underline=False)
    # the line stops and breaks at the withdrawal
    frag = S.rect(26.45, Y, 1.35, 0.045, "red", 1.0, anchor="l")
    S.life(frag, 21.4, d=0.05)
    S.move(frag, [(22.2, (26.45, Y)), (24.6, (27.3, Y - 0.6))])
    frag.rotation_euler.z = 0
    frag.keyframe_insert("rotation_euler", index=2, frame=1 + int(22.2 * 24))
    frag.rotation_euler.z = -0.35
    frag.keyframe_insert("rotation_euler", index=2, frame=1 + int(24.6 * 24))
    S.alpha(frag, [(23.4, 1.0), (24.6, 0.0)])
    nv = S.text("the ipo never happened.", 60, 0.2, 0.85, "type", "display", "CENTER")
    S.life(nv, 25.4, d=0.6)
    br = [S.rect(60 - 3.3, -0.65, 3.0, 0.045, "red", 1.0, anchor="l"), S.rect(60 + 0.45, -0.65, 2.9, 0.045, "red", 1.0, anchor="l")]
    S.life(br, 25.9, d=0.4)
    S.shots([[(0, -1.5, -0.4, 12.0), (2.0, -0.6, -0.4, 12.0), (6.2, 0, -0.4, 12.0), (10.6, 14, -0.4, 12.0),
              (15.6, 14.2, -0.4, 12.0), (20.0, 28, -0.5, 12.0), (25.2, 28.3, -0.5, 12.0)],
             [(25.2, 60, 0, 15.2), (30, 60, 0, 14.4)]])
    return S, e1 + e2 + e3


def sc12():
    S = new(12)
    hd = S.text("october 23, 2019 · softbank financing package", 0, 3.35, 0.28, "red", "bold", "CENTER")
    S.life(hd, 0.4, d=0.5)
    d = S.doc("D12_SOFTBANK_RELEASE", 0, 1.05, 12.6)
    S.life(d.objs, 0.0, d=0.6)
    d.highlight("$5 billion in new", 1.6)
    d.highlight("up to $3 billion", 2.6)
    d.highlight("$1.5 billion", 3.6)
    comps = [("$5 billion", "new financing"), ("up to $3 billion", "tender offer for existing shareholders"),
             ("$1.5 billion", "accelerated existing commitment")]
    for i, (v, l) in enumerate(comps):
        x = -4.7 + i * 4.7
        o = [S.text(v, x, -1.85, 0.5, "type", "display", "CENTER"), S.text(l, x, -2.45, 0.2, "gray", "semi", "CENTER")]
        S.life(o, 5.0 + i * 0.6, d=0.5)
    nt = S.text("three components, as announced · not a single sum", 0, -3.15, 0.18, "red", "bold", "CENTER")
    S.life(nt, 7.0, d=0.5)
    # beat 2 · to the public markets
    Y = 1.15
    tl = S.line(33.0, Y, 14.0, 10.2, 11.6, th=0.03)
    ev = [(34.4, "oct 2019", "softbank package"), (40.0, "mar 2021", "merger agreement with bowx announced"),
          (45.6, "oct 20, 2021", "merger closes · public listing via spac")]
    for i, (x, dt, lb) in enumerate(ev):
        timeline_event(S, x, Y, dt, lb, 10.8 + i * 0.8, up=True, dsize=0.32)
    b = S.doc("D13_BOWX_EV", 36.9, -1.55, 6.6, crop_top=56)
    S.life(b.objs, 12.8, d=0.5)
    b.highlight("initial enterprise value of approximately $9 billion", 14.0)
    c = S.doc("D14_SPAC_CLOSE", 43.6, -1.55, 6.4)
    S.life(c.objs, 15.0, d=0.5)
    c.highlight("October 20, 2021", 16.0)
    # beat 3 · two different measures, side by side, never divided into each other
    S.vline(80, -1.0, 3.6, 20.4, 21.0)
    a = stack(S, 76.0, 1.95, [("2019", 0.32, "gray", "display"), ("$47 billion", 0.85, "type", "display"),
                              ("private valuation · reported", 0.22, "gray", "semi")], 20.6)
    bb = stack(S, 84.0, 1.95, [("2021", 0.32, "gray", "display"), ("≈ $9 billion", 0.85, "type", "display"),
                               ("announced initial enterprise value", 0.22, "gray", "semi")], 21.4)
    dm = S.text("different measures · not directly comparable", 80, -1.45, 0.22, "red", "bold", "CENTER")
    S.life(dm, 23.0, d=0.5)
    rp = S.text("the dream was repriced.", 80, -2.7, 0.7, "type", "display", "CENTER")
    S.life(rp, 25.4, d=0.7)
    S.shots([[(0, 0, 0.2, 16.0), (10, 0, 0.1, 15.4)],
             [(10, 40, 0, 16.0), (20, 40, -0.2, 15.2)],
             [(20, 80, 0.1, 16.0), (30, 80, -0.35, 15.2)]])
    S.fade_black(29.4, 30, 0, 1)
    return S, [tl]


# ===================================================================== ACT 06
def sc13():
    S = new(13)
    S.fade_black(0, 0.6, 1, 0)
    ph = S.placeholder("P08", -2.6, 0.0, 8.4, 5.6)
    g = S.group(-2.6, 0)
    S.parent(ph, g)
    S.move(g, [(0, (-2.7, 0)), (10, (-2.45, 0))])
    S.life(ph, 0.3, d=0.7)
    t = stack(S, 2.35, 0.95, [("2020", 1.1, "red", "display"), ("remote work disruption", 0.4, "type", "display")], 1.6, align="LEFT")
    a = S.doc("D19_COVID_10K", 40, 1.75, 12.4)
    ca = S.text("what the company said · 10-k, fiscal 2022", 34.0, 2.75, 0.22, "gray", "bold")
    S.life(a.objs + [ca], 10.0, d=0.6)
    a.highlight("COVID-19", 11.2, underline=False)
    b = S.doc("D15_GOING_CONCERN", 40, -1.25, 12.4)
    cb = S.text("what demand did · 10-q, quarter ended june 30, 2023", 34.0, 0.33, 0.22, "gray", "bold")
    S.life(b.objs + [cb], 13.6, d=0.6)
    b.highlight("higher member churn and weaker demand", 15.4)
    Y = 0.6
    S.line(73.0, Y, 14.0, 20.2, 21.6, th=0.03)
    for i, (x, dt, lb) in enumerate([(74.6, "2020", "pandemic · offices empty"),
                                     (80.0, "2020–2022", "lease terminations · restructuring"),
                                     (85.4, "2023", "member churn · lease renegotiation")]):
        timeline_event(S, x, Y, dt, lb, 20.8 + i * 0.8, up=True, dsize=0.36)
    w1 = S.text("a new shock.", 80, -1.15, 0.62, "type", "display", "CENTER")
    w2 = S.text("an old problem.", 80, -2.05, 0.62, "red", "display", "CENTER")
    S.life(w1, 24.6, d=0.6)
    S.life(w2, 25.8, d=0.6)
    S.shots([[(0, 0, 0, 16.0), (10, 0.2, 0, 15.4)],
             [(10, 40, 0.9, 12.6), (13.4, 40, 0.85, 12.6), (17.6, 40, -0.2, 13.4), (20, 40, -0.2, 13.2)],
             [(20, 80, 0, 16.0), (30, 80, -0.3, 15.2)]])
    return S, t


def sc14():
    S = new(14)
    d = S.doc("D15_GOING_CONCERN", 0, 0.3, 13.0)
    lab = S.text("form 10-q · filed august 8, 2023", -6.5, 0.3 + d.h / 2 + 0.35, 0.26, "red", "bold")
    S.life(d.objs + [lab], 0.0, d=0.6)
    cx, cy, w, h = d.center("substantial doubt exists about the Company’s ability to continue as a going concern")
    d.highlight("substantial doubt exists about the Company’s ability to continue as a going concern", 2.0)
    d.focus("substantial doubt exists about the Company’s ability to continue as a going concern", 2.4)
    big = S.text("$462 million", 40, 1.35, 1.15, "type", "display", "CENTER")
    S.life(big, 10.3, d=0.8)
    sub = stack(S, 40, 0.15, [("cash and cash equivalents · september 30, 2023", 0.3, "type", "semi"),
                              ("unaudited · disclosed november 21, 2023, after the chapter 11 filing", 0.21, "red", "bold")], 11.0)
    q = S.doc("D16_Q3_CASH", 40, -2.25, 11.0, crop_bottom=40)
    S.life(q.objs, 13.2, d=0.5)
    q.highlight("$462 million", 14.2)
    # beat 3 · four dates, kept apart: warning, balance date, filing, disclosure (day-scaled)
    Y, x0, k = 0.45, 73.6, 12.6 / 105
    S.line(x0 - 0.6, Y, 14.2, 20.2, 21.4, th=0.03, color="gray")
    ev = [(0, "aug 8, 2023", "going-concern warning · 10-q", "type", True),
          (53, "sep 30, 2023", "balance date · $462m cash", "gray", False),
          (90, "nov 6, 2023", "chapter 11 petition", "red", True),
          (105, "nov 21, 2023", "q3 figures disclosed · 8-k", "gray", False)]
    for i, (days, dt, lb, colr, up) in enumerate(ev):
        timeline_event(S, x0 + days * k, Y, dt, lb, 20.8 + i * 0.7, color=colr, up=up, dsize=0.3)
    W = [S.text("warning", x0, 2.55, 0.62, "type", "display", "CENTER"), S.text("filing", x0 + 90 * k, 2.55, 0.62, "red", "display", "CENTER")]
    S.life(W[:1], 21.0, d=0.5)
    S.life(W[1:], 22.4, d=0.5)
    c = S.doc("D02_8K_CH11", 82.4, -2.45, 5.2)
    S.life(c.objs, 23.4, d=0.5)
    c.highlight("On November 6, 2023", 24.2, underline=False)
    S.shots([[(0, 0, 0.3, 15.6), (1.8, 0, 0.3, 15.6), (10, cx, cy, 10.6)],
             [(10, 40, -0.2, 15.8), (20, 40, -0.35, 15.4)],
             [(20, 80, 0.05, 16.0), (30, 80, -0.15, 15.4)]])
    return S, []


def sc15():
    S = new(15)
    L, R = -3.9, 3.9
    a = S.doc("D02_8K_CH11", L, 0.25, 6.9)
    b = S.doc("D17_EMERGENCE", R, 0.25, 6.9)
    la = stack(S, L, 2.65, [("november 6, 2023", 0.42, "red", "display"), ("chapter 11 petition", 0.22, "gray", "semi")], 0.5)
    lb = stack(S, R, 2.65, [("june 11, 2024", 0.42, "type", "display"), ("plan effective · emergence from chapter 11", 0.22, "gray", "semi")], 3.0)
    S.life(a.objs, 0.3, d=0.6)
    S.life(b.objs, 2.8, d=0.6)
    a.highlight("On November 6, 2023", 1.6)
    b.highlight("The Plan became effective on June 11, 2024", 4.4)
    ends = [S.disc(L, -2.05, 0.08, "red"), S.disc(R, -2.05, 0.08, "red")]
    S.life(ends, 6.0, d=0.3)
    S.line(L, -2.05, R - L, 6.2, 8.4, th=0.035)
    dd = S.text("218 days", 0, -2.45, 0.24, "type", "bold", "CENTER")
    S.life(dd, 8.4, d=0.5)
    ph = S.placeholder("P09", 40, 0.25, 9.4, 5.5)
    g = S.group(40, 0.25)
    S.parent(ph, g)
    S.move(g, [(12, (39.85, 0.25)), (20, (40.15, 0.25))])
    S.life(ph, 12.2, d=0.6)
    cap = S.text("the company continued in reorganized form", 40, -3.15, 0.3, "type", "semi", "CENTER")
    S.life(cap, 13.6, d=0.5)
    w1 = S.text("the business survived.", 80, 0.65, 0.72, "type", "display", "CENTER")
    w2 = S.text("the original valuation story did not.", 80, -0.4, 0.58, "red", "display", "CENTER")
    S.life(w1, 20.6, d=0.6)
    S.life(w2, 23.2, d=0.7)
    S.shots([[(0, 0, 0.1, 16.0), (12, 0, 0, 15.4)],
             [(12, 40, 0, 15.6), (20, 40, 0, 15.0)],
             [(20, 80, 0.1, 16.0), (30, 80, 0.1, 14.8)]])
    return S, []


def sc16():
    S = new(16)
    num = S.text("$47,000,000,000", 0, 0.15, 1.3, "type", "display", "CENTER")
    S.alpha(num, [(0.4, 0.0), (1.6, 1.0), (14.2, 1.0), (17.4, 0.0)])
    cards = [("long-term lease commitments", "$33.95b in commenced operating lease payments, undiscounted (s-1, 2019)", (-5.0, 2.55), (-12, 2.55)),
             ("expensive expansion", "2018: $1.82b revenue; $1.61b net loss attributable to wework companies inc. (s-1)", (5.0, 2.55), (12, 2.55)),
             ("governance concerns", "20-vote high-vote shares as proposed; trademark deal later unwound (s-1, s-1/a)", (-5.0, -2.35), (-12, -2.35)),
             ("changing office demand", "member churn and weaker demand; going-concern warning (10-q, aug 2023)", (5.0, -2.35), (12, -2.35))]
    allc = []
    for i, (title, ev, pos, start) in enumerate(cards):
        w, h = 4.4, 1.75
        o = [S.rect(0, 0, w, h, "panel", 1.0), S.rect(0, h / 2 - 0.02, w, 0.04, "red", 1.0),
             S.text(title, -w / 2 + 0.22, h / 2 - 0.3, 0.26, "type", "display", width=w - 0.44, valign="TOP"),
             S.text(ev, -w / 2 + 0.22, -h / 2 + 0.2, 0.16, "gray", "semi", width=w - 0.44, valign="BOTTOM", line=1.08)]
        g = S.group(0, 0, "card")
        for ob in o[1:]:
            ob["overlay"] = True
        for ob in o:
            ob.parent = g
        t0 = 8.4 + i * 0.8
        S.move(g, [(t0, start), (t0 + 1.6, pos), (13.2, pos), (16.4, (pos[0] * 0.62, pos[1] * 0.64))])
        S.life(o, t0, 18.4, d=0.5, d_out=0.8)
        allc += o
    v1 = S.text("a useful product is not always", 0, 0.5, 0.62, "type", "display", "CENTER")
    v2 = S.text("a sustainable investment.", 0, -0.45, 0.62, "type", "display", "CENTER")
    S.life(v1, 18.8, 23.6, d=0.7, d_out=0.6)
    S.life(v2, 19.6, 23.6, d=0.7, d_out=0.6)
    brand = S.text("brand coroner", -0.22, 0.25, 1.0, "type", "display", "CENTER")
    dot = S.disc(0, 0, 0.095, "red")
    tag = S.text("every brand leaves evidence.", 0, -0.75, 0.3, "gray", "semi", "CENTER")
    S.life(brand, 24.4, 29.0, d=0.8, d_out=0.4)
    S.life(dot, 24.9, 29.0, d=0.3, d_out=0.4)
    S.life(tag, 25.6, 29.0, d=0.6, d_out=0.4)
    S.shots([[(0, 0, 0, 15.2), (8, 0, 0.05, 14.8), (18, 0, 0.05, 16.2)],
             [(18, 0, 0, 15.6), (30, 0, 0, 14.6)]])
    S.fade_black(28.9, 30, 0, 1)
    return S, [brand, dot]


BUILDERS = [sc01, sc02, sc03, sc04, sc05, sc06, sc07, sc08, sc09, sc10, sc11, sc12, sc13, sc14, sc15, sc16]
