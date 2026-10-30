// 01 · The Prehistoric Bush (0–30 s). Cave, fire and Gerald draw themselves; push to his waist-level undergrowth;
// three squirrels move in, furnish the place, and hang a sign.
import { line, fill, handCircle, ellipse, smooth, xf } from '../crayon.js';
import { part } from '../rig.js';
import { K, person, squirrel, sign, acorn, bush, say } from '../figs.js';
import { camOf, F, L, ground, box, clamp, lerp, hash, wob } from './util.js';
const GX = 930, GY = 880, GS = 1.5;
const BUSH = [GX, GY - 92, 1];   // waist bush centre (world)
export default {
  cam: c => camOf(c, [[0, [720, 540, 1]], [c.at(1, -0.2), [720, 540, 1]], [c.at(1, 1.6), [930, 700, 1.7]], [c.at(4, 0.2), [930, 700, 1.7]], [c.at(4, 1.6), [880, 640, 1.4]], [30, [880, 640, 1.4]]]),
  draw(S, c) {
    const d0 = c.p(0.2, 1.6), d1 = c.p(0.9, 2.4);
    ground(S.BG, 880, K.ochre, c.p(0.1, 1.2), 11);
    // cave: a lumpy rock arch with a dark mouth
    const rock = smooth([[60, 885], [80, 520], [180, 330], [360, 260], [540, 320], [640, 520], [660, 885]], 5);
    part(S.G2, rock, F(K.grey, 20, { draw: d1, p: 0.8, ang: 1.2 }), L(21, { draw: d0 }));
    part(S.G2, smooth([[200, 885], [210, 640], [300, 520], [420, 520], [500, 640], [510, 885]], 5), F(K.ink, 22, { draw: d1, p: 0.85 }), L(23, { draw: d0 }), { occ: true });
    [[120, 420], [560, 470], [250, 330]].forEach(([x, y], i) => line(S.G2.l, [[x, y], [x + 40, y + 16]], L(24 + i, { w: 4, draw: d0, p: 0.6 })));
    // fire: logs + flames that flicker on twos
    const fd = c.p(1.0, 2.0), fx = 600, fy = 870;
    part(S.G, [[fx - 70, fy - 10], [fx + 70, fy - 30], [fx + 74, fy - 14], [fx - 66, fy + 6]], F(K.brown, 30, { draw: fd }), L(31, { draw: fd, w: 5 }));
    part(S.G, [[fx - 70, fy - 30], [fx + 70, fy - 10], [fx + 66, fy + 6], [fx - 74, fy - 14]], F(K.brown, 32, { draw: fd }), L(33, { draw: fd, w: 5 }));
    if (fd > 0.5) { const k = Math.floor(c.tq * 12) % 3; [[K.red, 1], [K.orange, 0.75], [K.yellow, 0.45]].forEach(([col, s], i) => {
      const h = (130 + 12 * ((k + i) % 3)) * s, w = 70 * s; part(S.G, smooth([[fx - w, fy - 20], [fx - w * 0.6, fy - 20 - h * 0.5], [fx - w * 0.2 + 8 * k, fy - 20 - h], [fx + w * 0.3, fy - 20 - h * 0.55], [fx + w * 0.4, fy - 20 - h * 0.8], [fx + w, fy - 20]], 4), F(col, 34 + i, { p: 0.95, gap: 5, w: 7, ang: 1.5 }), i ? null : L(37, { w: 5, col: K.red }), { occ: false }); }); }
    // Gerald, with his undergrowth (it thickens as we push in)
    const gd = c.p(1.4, 3.0), gf = c.p(2.0, 3.6);
    person(S.G, 'gerald', { x: GX, y: GY, s: GS, view: 'front', draw: gd, fillDraw: gf, expr: c.tq > c.at(4, 1.4) ? 'sleepy' : 'sleepy', armL: [-80, -112], armR: [80, -112] });
    const grow = 0.62 + 0.38 * c.p(c.at(1, 0.2), c.at(1, 2.0));
    if (gd > 0.3) bush(S.G, BUSH[0], BUSH[1], 200 * grow, 86 * grow, { seed: 40, draw: clamp((gd - 0.3) / 0.7), fillDraw: gf });
    // the three squirrels pop up out of the undergrowth, one per beat of the line
    const pops = [[GX - 150, GY - 150, 0, 0.1], [GX - 10, GY - 166, 1, 0.9], [GX + 150, GY - 148, 2, 1.7]];
    pops.forEach(([x, y, i, dt]) => { const ts = c.at(2, dt); if (c.tq < ts) return; const u = clamp((c.tq - ts) / 0.35), up = (1 - Math.sin(u * Math.PI / 2)) * 60;
      squirrel(S.G, { x, y: y + up, s: 0.48, i, flip: i === 2, hold: i === 0 && c.tq > c.at(3, 0.6) ? (C, T, p) => acorn(C, ...T([[p[0] + 6, p[1] - 14]])[0], 0.45, 61) : null }); });
    // their household: a little door, a lit window, an acorn table, two leaf beds and a washing line
    if (c.tq > c.at(3)) {
      const h = c.p(c.at(3), c.at(3, 2.4)), bx = BUSH[0], by = BUSH[1];
      part(S.G, smooth([[bx - 112, by + 54], [bx - 114, by + 8], [bx - 94, by - 12], [bx - 74, by + 8], [bx - 72, by + 54]], 3), F(K.red, 70, { draw: h }), L(71, { draw: h, w: 4 }));
      fill(S.G.l, handCircle(bx - 80, by + 32, 3, 72, 0, 8), F(K.yellow, 73, { p: 1, draw: h }));
      if (c.tq > c.at(3, 0.5)) { const h2 = c.p(c.at(3, 0.5), c.at(3, 1.4)); part(S.G, [[bx - 40, by - 30], [bx - 8, by - 30], [bx - 8, by - 2], [bx - 40, by - 2]], F(K.yellow, 74, { draw: h2, p: 0.9 }), L(75, { draw: h2, w: 4 })); line(S.G.l, [[bx - 24, by - 30], [bx - 24, by - 2]], L(76, { w: 3, draw: h2 })); }
      if (c.tq > c.at(3, 1.0)) { const h3 = c.p(c.at(3, 1.0), c.at(3, 1.8)); part(S.G, ellipse(bx + 40, by + 30, 34, 9, 18), F(K.ochre, 77, { draw: h3 }), L(78, { draw: h3, w: 4 })); line(S.G.l, [[bx + 40, by + 38], [bx + 40, by + 70]], L(79, { w: 4, draw: h3 })); acorn(S.G, bx + 28, by + 14, 0.5, 80); acorn(S.G, bx + 54, by + 16, 0.45, 85); }
      if (c.tq > c.at(3, 1.6)) { const h4 = c.p(c.at(3, 1.6), c.at(3, 2.6)); [[bx + 96, by - 6], [bx + 120, by + 40]].forEach(([x, y], i) => { part(S.G, [[x - 26, y], [x + 26, y], [x + 26, y + 12], [x - 26, y + 12]], F(K.brown, 90 + i, { draw: h4 }), L(92 + i, { draw: h4, w: 3.5 })); part(S.G, smooth([[x - 18, y - 2], [x + 4, y - 14], [x + 28, y - 4], [x + 6, y + 4]], 3), F(K.green, 94 + i, { draw: h4, p: 0.95 }), L(96 + i, { draw: h4, w: 3.5, col: K.green })); }); }
      if (c.tq > c.at(3, 2.2)) { const h5 = c.p(c.at(3, 2.2), c.at(3, 3.0)); line(S.G.l, [[bx - 150, by - 70], [bx - 60, by - 60]], L(98, { w: 3, draw: h5 })); [[bx - 132, K.sky], [bx - 104, K.pink], [bx - 78, K.yellow]].forEach(([x, col], i) => part(S.G, [[x - 9, by - 68 + i * 1.2], [x + 9, by - 67 + i * 1.2], [x + 7, by - 50], [x - 7, by - 50]], F(col, 100 + i, { draw: h5, p: 0.95 }), L(103 + i, { draw: h5, w: 3 }))); }
    }
    // the sign
    if (c.tq > c.at(4, -0.2)) { const sd = c.p(c.at(4, -0.2), c.at(4, 0.6)), sw = Math.sin(Math.max(0, c.tq - c.at(4, 0.6)) * 5) * Math.exp(-Math.max(0, c.tq - c.at(4, 0.6)) * 1.5) * 0.12;
      sign(S.G, BUSH[0] + 10, BUSH[1] + 10, 330, 70, 'PRIVATE PROPERTY', { seed: 110, string: 34, reveal: c.p(c.at(4, 0.3), c.at(4, 1.2)), r: sw, draw: sd, size: 38, col: K.ochre });
      squirrel(S.G, { x: BUSH[0] + 140, y: BUSH[1] + 4, s: 0.45, i: 1, flip: true, paw: [40, -80] }); }
  },
  sfx: c => [[0.2, 'scratch', { dur: 1.4, pan: -0.5 }], [0.9, 'scribble', { dur: 1.5, pan: -0.5 }], [1.0, 'fire', { dur: 29 }], [1.4, 'scratch', { dur: 1.6, pan: 0.2 }], [2.0, 'scribble', { dur: 1.6, pan: 0.2 }],
    [c.at(1, 0.2), 'scribble', { dur: 1.8, pan: 0.2 }], [c.at(2, 0.1), 'rustle', { pan: -0.2 }], [c.at(2, 0.9), 'rustle', { pan: 0 }], [c.at(2, 1.7), 'rustle', { pan: 0.25 }],
    [c.at(3), 'scratch', { dur: 0.6 }], [c.at(3, 1.0), 'acorn', {}], [c.at(3, 1.15), 'acorn', { pan: 0.2 }], [c.at(3, 1.6), 'scribble', { dur: 1.0, pan: 0.3 }], [c.at(3, 2.2), 'scratch', { dur: 0.6, pan: -0.3 }],
    [c.at(4, -0.2), 'scratch', { dur: 0.7 }], [c.at(4, 0.3), 'write', { dur: 0.9 }], [c.at(4, 0.6), 'tap', {}]],
};
