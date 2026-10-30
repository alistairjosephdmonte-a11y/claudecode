// 09 · The Space Age (240–270 s). One tall page: the launch pad at the bottom, the moon at the top, Mission Control
// off to the right. The rocket draws itself and rides a dashed crayon arc; the astronaut floats; the checklist ends
// on PERSONAL MAINTENANCE (unchecked); a tiny message goes out: REQUESTING MAINTENANCE.
import { line, fill, handCircle, ellipse, smooth, xf } from '../crayon.js';
import { part } from '../rig.js';
import { K, person, say, star5 } from '../figs.js';
import { camOf, F, L, ground, box, clamp, lerp, hash, tick } from './util.js';
const MOON_Y = -900;     // the moon page sits above the launch page
const MC = 2300;         // Mission Control, to the right
const LIST = ['FUEL', 'OXYGEN', 'FLAG', 'CAMERA', 'SNACKS', 'SPARE SOCKS', 'PEN (UPSIDE-DOWN)', 'PERSONAL MAINTENANCE'];
export default {
  cam: c => camOf(c, [[0, [720, 540, 1]], [c.at(0, 1.4), [720, 540, 1]], [c.at(1, -0.2), [720, MOON_Y + 540, 1]], [c.at(2, -0.5), [720, MOON_Y + 540, 1]], [c.at(2, 0.4), [MC, 520, 1]], [c.at(3, 0.2), [MC, 520, 1]], [c.at(3, 1.4), [MC + 80, 700, 1.6]], [c.at(4, -0.5), [MC + 80, 700, 1.6]], [c.at(4, 0.3), [760, MOON_Y + 520, 1.3]], [30, [760, MOON_Y + 520, 1.3]]]),
  draw(S, c) {
    const T = c.turn, d = c.p(T + 0.1, T + 1.2), f = c.p(T + 0.5, T + 1.8);
    // night sky that runs the full height of the tall page; stars in yellow crayon
    fill(S.BG.f, [[-300, MOON_Y - 600], [3200, MOON_Y - 600], [3200, 860], [-300, 860]], F(K.violet, 1700, { draw: f, p: 0.75, gap: 9, w: 12, ang: 0.35 }));
    for (let k = 0; k < 40; k++) { const x = -200 + hash(k) * 1900, y = MOON_Y - 500 + hash(k + 50) * 1300; if (hash(k + 9) > 0.7) star5(S.G2, [x, y][0], y, 12, K.yellow, 1710 + k * 2); else fill(S.BG.l, handCircle(x, y, 4, 1790 + k, 0, 8), F(K.yellow, 1830 + k, { p: 1 })); }
    // the launch pad, the gantry and the rocket
    ground(S.BG, 860, K.grey, d, 1880, -300, 3200);
    line(S.G2.l, [[300, 860], [300, 440]], L(1881, { w: 8, col: K.red, draw: d })); for (let k = 0; k < 6; k++) line(S.G2.l, [[300, 840 - k * 70], [360, 800 - k * 70]], L(1882 + k, { w: 4, col: K.red, draw: d }));
    const launch = c.pc(c.at(0, 2.0), c.at(1, 0.4)), u = launch * launch;
    const path = s => [lerp(420, 1500, s) + 300 * Math.sin(s * 2), lerp(800, MOON_Y - 300, s)];   // the trajectory, dashed in crayon
    if (launch > 0) { for (let k = 0; k < 40; k++) { const s0 = k / 40, s1 = s0 + 0.012; if (s1 > u) break; line(S.FX, [path(s0), path(s1)], { w: 5, col: K.white, p: 0.9, seed: 1890 + k }); } }
    const [rx, ry] = path(u), [rx2, ry2] = path(Math.min(1, u + 0.01)), ang = launch > 0 ? Math.atan2(rx2 - rx, -(ry2 - ry)) : 0;
    const R = pts => xf(pts, { x: launch > 0 ? rx : 420, y: launch > 0 ? ry : 800, r: ang });
    const rd = c.p(T + 0.3, T + 1.6), rf = c.p(T + 0.8, T + 2.0);
    if (u < 0.98) {
      part(S.G, R([[-40, 0], [-50, -160], [-30, -230], [0, -270], [30, -230], [50, -160], [40, 0]]), F(K.white, 1940, { draw: rf, p: 0.95 }), L(1941, { draw: rd }));
      part(S.G, R([[-30, -230], [0, -270], [30, -230]]), F(K.red, 1942, { draw: rf }), L(1943, { draw: rd }));
      part(S.G, R(handCircle(0, -150, 20, 1944, 0, 16)), F(K.sky, 1945, { draw: rf }), L(1946, { draw: rd, w: 4 }));
      [[-40, 0, -80, 30, -46, -60], [40, 0, 80, 30, 46, -60]].forEach(([a, b, c2, d2, e, g], i) => part(S.G, R([[a, b], [c2, d2], [e, g]]), F(K.red, 1947 + i, { draw: rf }), L(1949 + i, { draw: rd })));
      if (launch > 0) { const fl = Math.floor(c.tq * 12) % 2; part(S.G, R([[-26, 6], [0, 70 + 30 * fl], [26, 6]]), F(K.orange, 1951, { p: 1 }), L(1952, { col: K.red, w: 4 })); part(S.G, R([[-14, 6], [0, 40 + 20 * fl], [14, 6]]), F(K.yellow, 1953, { p: 1 }), null, { occ: false });
        for (let k = 0; k < 4; k++) { const sm = clamp(launch * 5 - k * 0.3); if (sm > 0 && sm < 1) part(S.G2, handCircle(420 + (k - 1.5) * 70, 830, 50 * sm + 20, 1960 + k, 0.15, 18), F(K.white, 1965 + k, { p: 0.7 * (1 - sm) + 0.2 }), L(1970 + k, { w: 4, col: K.grey, p: 0.6 }), { occ: false }); } }
    }
    // the moon page: grey ground with craters, a small blue-and-green Earth, the floating astronaut
    if (c.tq > c.at(0, 2.5)) { const md = c.p(c.at(0, 2.5), c.at(1, 0.5));
      const top = []; for (let x = -300; x <= 1800; x += 60) top.push([x, MOON_Y + 860 + 18 * Math.sin(x * 0.006)]);
      fill(S.G2.f, [...top, [1800, MOON_Y + 1300], [-300, MOON_Y + 1300]], F(K.grey, 2000, { draw: md, p: 0.75 })); line(S.G2.l, top, L(2001, { draw: md }));
      [[300, 920, 70], [900, 960, 50], [1200, 900, 40]].forEach(([x, y, r], i) => line(S.G2.l, ellipse(x, MOON_Y + y, r, r * 0.3, 20), L(2002 + i, { draw: md, w: 4, closed: true })));
      part(S.G2, handCircle(1180, MOON_Y + 220, 70, 2010, 0.05, 30), F(K.sky, 2011, { draw: md }), L(2012, { draw: md })); part(S.G2, smooth([[1140, MOON_Y + 190], [1190, MOON_Y + 180], [1210, MOON_Y + 230], [1170, MOON_Y + 250], [1150, MOON_Y + 220]], 3), F(K.green, 2013, { draw: md, p: 0.95 }), null);
      const bob = 16 * Math.sin(c.tq * 1.6), drift = 40 * Math.sin(c.tq * 0.4);
      person(S.G, 'astronaut', { x: 720 + drift, y: MOON_Y + 640 + bob, s: 1.15, pose: 'float', ph: c.tq * 0.3, r: 0.12 * Math.sin(c.tq * 0.9), seed: 2020, draw: md, expr: c.tq > c.at(4) ? 'worried' : 'happy',
        armR: c.tq > c.at(4, 0.1) ? [70, -240] : undefined });
      if (c.tq > c.at(4, 0.3)) { const k = c.p(c.at(4, 0.3), c.at(4, 0.7)), mx = 900 + drift + 120 * c.p(c.at(4, 0.7), 30), my = MOON_Y + 330 + bob - 80 * c.p(c.at(4, 0.7), 30);
        part(S.G, [[mx - 90, my - 34], [mx + 90, my - 30], [mx + 86, my + 34], [mx - 88, my + 30]], F(K.white, 2030, { draw: k, p: 0.95 }), L(2031, { draw: k, w: 4 }));
        say(S.G.l, 'REQUESTING', mx, my - 2, { size: 24, font: 'Gaegu', weight: 700, reveal: c.p(c.at(4, 0.6), c.at(4, 1.2)), seed: 2032 }); say(S.G.l, 'MAINTENANCE', mx, my + 24, { size: 24, font: 'Gaegu', weight: 700, reveal: c.p(c.at(4, 1.1), c.at(4, 1.8)), seed: 2033 });
        for (let j = 0; j < 3; j++) line(S.FX, ellipse(mx - 120, my, 14 + j * 14, 14 + j * 14, 10, -0.7, 0.7), { w: 4, col: K.white, p: 0.9, seed: 2034 + j }); } }
    // Mission Control: desks, round screens, the controller with an ever-longer checklist
    if (c.tq > c.at(2, -0.8)) { const cd = c.p(c.at(2, -0.8), c.at(2, 0.2));
      part(S.G2, [[MC - 760, 100], [MC + 760, 100], [MC + 760, 860], [MC - 760, 860]], F(K.white, 2100, { draw: cd, p: 0.5 }), L(2101, { draw: cd }));
      for (let k = 0; k < 4; k++) { const x = MC - 600 + k * 300; box(S.G2, x - 100, 620, 200, 60, K.grey, 2110 + k * 5, cd); part(S.G2, handCircle(x, 540, 50, 2112 + k * 5, 0.05, 20), F(K.green, 2113 + k * 5, { draw: cd, p: 0.7 }), L(2114 + k * 5, { draw: cd })); line(S.G2.l, ellipse(x, 540, 30, 30, 12, Math.PI, Math.PI * 2), L(2115 + k * 5, { draw: cd, w: 3, col: K.white })); }
      person(S.G, 'controller', { x: MC - 260, y: 880, s: 1.05, view: 'q', seed: 2140, draw: cd, expr: c.tq > c.at(3, 1.2) ? 'worried' : 'neutral', armR: [96, -200] });
      // the checklist: a long paper ribbon that unrolls downward, ticking items as it goes
      const ux = MC - 60, n = Math.min(LIST.length, Math.floor(c.p(c.at(2, 0.2), c.at(3, 0.6)) * LIST.length + 1e-6) + (c.tq > c.at(3, 0.6) ? 1 : 0));
      const top = 180, rowH = 70, Hh = Math.max(60, n * rowH + 20);
      part(S.G, [[ux, top], [ux + 420, top], [ux + 420, top + Hh], [ux, top + Hh]], F(K.white, 2150, { p: 0.95 }), L(2151));
      say(S.G.l, 'CHECKLIST', ux + 210, top - 14, { size: 40, font: 'Gaegu', weight: 700, seed: 2152 });
      for (let i = 0; i < n; i++) { const y = top + 50 + i * rowH, last = i === LIST.length - 1;
        line(S.G.l, [[ux + 24, y - 24], [ux + 54, y - 24], [ux + 54, y + 6], [ux + 24, y + 6], [ux + 24, y - 24]], L(2160 + i, { w: 4 }));
        say(S.G.l, LIST[i], ux + 72, y, { size: last ? 34 : 34, font: 'Gaegu', weight: 700, align: 'left', seed: 2170 + i, col: last ? K.red : K.ink });
        if (!last) tick(S.G.l, ux + 40, y - 10, 1.0, 1, 2180 + i); }
    }
  },
  sfx: c => [[c.turn + 0.1, 'scratch', { dur: 1.2, pan: -0.5 }], [c.turn + 0.5, 'scribble', { dur: 1.4 }], [c.at(0, 2.0), 'rocket', { dur: 3.0 }], [c.at(1, -0.2), 'space', { dur: 6.5 }],
    [c.at(2, -0.8), 'scribble', { dur: 1.0, pan: 0.4 }], [c.at(2, 0.2), 'beeps', { dur: c.at(3, 0.6) - c.at(2, 0.2) }], ...[0, 1, 2, 3, 4, 5, 6].map(i => [c.at(2, 0.2) + (c.at(3, 0.6) - c.at(2, 0.2)) * (i + 0.5) / 8, 'ticker', { pan: 0.3 }]),
    [c.at(3, 0.6), 'beep_low', { pan: 0.3 }], [c.at(4, 0.3), 'radio', { dur: 1.6 }]],
};
