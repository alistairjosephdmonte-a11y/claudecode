// 04 · The Roman Empire (90–120 s). Left-to-right reading truck along one long page: aqueduct → bathhouse → Senate,
// where the Lower Provinces map is unveiled, hands go up, and the clerk writes NEXT CENTURY.
import { line, fill, handCircle, ellipse, smooth } from '../crayon.js';
import { part } from '../rig.js';
import { K, person, say, bush, sign } from '../figs.js';
import { camOf, F, L, ground, box, clamp, lerp, wob } from './util.js';
export default {
  cam: c => camOf(c, [[0, [720, 540, 1]], [c.at(1, -0.6), [720, 540, 1]], [c.at(1, 0.6), [1980, 540, 1]], [c.at(2, -0.6), [1980, 540, 1]], [c.at(2, 0.6), [3240, 540, 1]], [c.at(4, -0.3), [3240, 540, 1]], [c.at(4, 0.6), [2790, 600, 1.6]], [30, [2790, 600, 1.6]]]),
  draw(S, c) {
    const T = c.turn;
    ground(S.BG, 840, K.green, c.p(T, T + 1.0), 600, -200, 4400);
    // aqueduct: arches draw on left → right along the line
    const ad = c.p(T + 0.2, c.at(0, 4.0));
    for (let i = 0; i < 9; i++) { const x0 = 40 + i * 170, li = clamp(ad * 9 - i); if (li <= 0) continue;
      const P = [[x0, 840], [x0, 420], [x0 + 170, 420], [x0 + 170, 840], [x0 + 140, 840], ...ellipse(x0 + 85, 600, 55, 80, 16, 0, -Math.PI).map(([x, y]) => [x, y]), [x0 + 30, 840]];
      part(S.G2, smooth([[x0, 840], [x0, 420], [x0 + 170, 420], [x0 + 170, 840], [x0 + 140, 840], [x0 + 140, 600], [x0 + 120, 540], [x0 + 85, 520], [x0 + 50, 540], [x0 + 30, 600], [x0 + 30, 840]], 1), F(K.ochre, 610 + i, { draw: li, ang: 0.3 }), L(630 + i, { draw: li }));
      box(S.G2, x0 - 6, 390, 182, 34, K.ochre, 650 + i, li); }
    const wl = []; for (let x = 40; x <= 40 + 1530 * ad; x += 30) wl.push([x, 380 + 4 * Math.sin(x * 0.05 + c.tq * 6)]); if (wl.length > 1) line(S.FX, wl, { w: 9, col: K.sky, p: 0.95, seed: 670 });
    // bathhouse: pediment, columns, a steaming pool with a rubber-duck-free Roman in it
    const bd = c.p(c.at(1, -0.4), c.at(1, 1.2)), bf = c.p(c.at(1, 0.2), c.at(1, 1.8)), X = 1980;
    part(S.G2, [[X - 420, 330], [X, 200], [X + 420, 330]], F(K.red, 700, { draw: bf }), L(701, { draw: bd }));
    box(S.G2, X - 420, 330, 840, 36, K.white, 702, bd);
    for (let k = 0; k < 6; k++) box(S.G2, X - 390 + k * 150, 366, 60, 360, K.white, 710 + k, bd, { p: 0.9 });
    part(S.G2, [[X - 440, 726], [X + 440, 726], [X + 440, 840], [X - 440, 840]], F(K.white, 720, { draw: bf, p: 0.6 }), L(721, { draw: bd }));
    fill(S.G2.f, ellipse(X, 780, 360, 40, 30), F(K.sky, 722, { draw: bf, p: 0.95 })); line(S.G2.l, ellipse(X, 780, 360, 40, 40), L(723, { draw: bd, col: K.sky, closed: true }));
    if (c.tq > c.at(1, 0.6)) for (let k = 0; k < 5; k++) { const ph = (c.tq * 0.6 + k * 0.2) % 1, x = X - 260 + k * 130; line(S.FX, [[x, 750 - ph * 150], [x + 14, 720 - ph * 150], [x - 4, 690 - ph * 150], [x + 10, 660 - ph * 150]], { w: 5, col: K.grey, p: 0.8 * (1 - ph), seed: 730 + k }); }
    if (c.tq > c.at(1, 0.8)) person(S.G, 'senator', { x: X + 120, y: 830, s: 0.7, seed: 740, expr: 'happy', draw: c.p(c.at(1, 0.8), c.at(1, 1.6)), armR: [70, -200] });
    say(S.BG.l, 'BALNEUM', X, 315, { size: 40, font: 'Gaegu', weight: 700, reveal: c.p(c.at(1, 0.8), c.at(1, 1.6)), seed: 741, col: K.white });
    // the Senate: the senator and his map of the provinces
    const MX = 3330, MY = 470;
    if (c.tq > c.at(2, -0.8)) {
      const sd = c.p(c.at(2, -0.6), c.at(2, 0.6));
      [2700, 3900].forEach((x, i) => box(S.G2, x - 40, 200, 80, 640, K.white, 760 + i, sd, { p: 0.9 }));
      line(S.G2.l, [[2620, 200], [3980, 200]], L(762, { draw: sd, w: 8 }));
      // easel + map: neat provinces up top, the LOWER PROVINCES a wild scribble
      line(S.G2.l, [[MX - 200, 780], [MX - 140, 280]], L(770, { w: 8, col: K.brown, draw: sd })); line(S.G2.l, [[MX + 200, 780], [MX + 140, 280]], L(771, { w: 8, col: K.brown, draw: sd }));
      const md = c.p(c.at(2, 0.1), c.at(2, 1.0)), MW = 460, MH = 380;
      part(S.G2, [[MX - MW / 2, MY - MH / 2], [MX + MW / 2, MY - MH / 2 + 4], [MX + MW / 2 - 4, MY + MH / 2], [MX - MW / 2 + 4, MY + MH / 2 - 4]], F(K.ochre, 772, { draw: md, p: 0.35 }), L(773, { draw: md }));
      part(S.G2, smooth([[MX - 190, MY - 160], [MX + 170, MY - 166], [MX + 196, MY - 40], [MX + 120, MY + 10], [MX - 130, MY + 6], [MX - 196, MY - 60]], 3), F(K.green, 774, { draw: md, p: 0.6 }), L(775, { draw: md, w: 4 }));
      for (let k = 0; k < 6; k++) { const x = MX - 150 + k * 60; line(S.G2.l, [[x, MY - 70], [x, MY - 50]], L(780 + k, { w: 4, col: K.brown, draw: md })); fill(S.G2.l, handCircle(x, MY - 80, 10, 786 + k, 0, 12), F(K.green, 792 + k, { p: 1, draw: md })); }
      if (c.tq > c.at(2, 0.6)) bush(S.G2, MX, MY + 100, 170, 62, { seed: 800, col: K.brown, draw: c.p(c.at(2, 0.6), c.at(2, 1.6)) });
      say(S.G.l, 'LOWER PROVINCES', MX, MY + 180, { size: 40, font: 'Gaegu', weight: 700, reveal: c.p(c.at(2, 1.4), c.at(2, 2.4)), seed: 802 });
      person(S.G, 'senator', { x: 3000, y: 880, s: 1.05, seed: 820, draw: sd, armR: [110, -240], expr: c.tq > c.at(4) ? 'smug' : 'neutral' });
      // the vote: four senators, hands up one after another
      [3560, 3680, 3800, 3920].forEach((x, i) => { if (c.tq < c.at(3, -0.6)) return; const up = c.tq > c.at(3, 0.3 + i * 0.35);
        person(S.G, 'senator', { x, y: 900, s: 0.72, seed: 840 + i * 13, flip: i > 0, draw: c.p(c.at(3, -0.6), c.at(3, 0.3)), armR: up ? [56, -280] : [70, -110], expr: up ? 'happy' : 'neutral', cloth: [K.red, K.white, K.red, K.white][i], sash: [K.white, K.red, K.white, K.red][i] }); });
      // the clerk and his wax tablet
      if (c.tq > c.at(4, -0.4)) { const cd = c.p(c.at(4, -0.4), c.at(4, 0.2));
        person(S.G, 'clerk', { x: 2640, y: 880, s: 0.9, seed: 860, draw: cd, view: 'q', armR: [80, -190], armL: [-30, -170] });
        part(S.G, [[2690, 560], [2870, 556], [2874, 680], [2694, 684]], F(K.brown, 870, { draw: cd }), L(871, { draw: cd }));
        part(S.G, [[2704, 572], [2858, 568], [2860, 668], [2706, 672]], F(K.ochre, 872, { draw: cd, p: 0.9 }), L(873, { draw: cd, w: 3 }));
        say(S.G.l, 'NEXT', 2782, 612, { size: 40, font: 'Gaegu', weight: 700, reveal: c.p(c.at(4, 0.4), c.at(4, 0.9)), seed: 874 });
        say(S.G.l, 'CENTURY', 2782, 656, { size: 40, font: 'Gaegu', weight: 700, reveal: c.p(c.at(4, 0.9), c.at(4, 1.5)), seed: 875 }); }
    }
  },
  sfx: c => [[c.turn + 0.2, 'scratch', { dur: 3.6, pan: -0.6 }], [c.turn + 0.8, 'water', { dur: 5 }], [c.at(1, -0.4), 'scribble', { dur: 1.8 }], [c.at(1, 0.6), 'bubbles', { dur: 3 }],
    [c.at(2, -0.6), 'scratch', { dur: 1.2 }], [c.at(2, 0.1), 'unroll', { dur: 0.8 }], [c.at(2, 0.6), 'scribble', { dur: 1.0 }], [c.at(2, 1.4), 'write', { dur: 1.0 }],
    [c.at(3, 0.3), 'rustle', { pan: -0.4 }], [c.at(3, 0.65), 'rustle', { pan: 0.2 }], [c.at(3, 1.0), 'rustle', { pan: 0.4 }], [c.at(3, 1.35), 'rustle', { pan: 0.6 }], [c.at(4, 0.4), 'stylus', { dur: 1.1, pan: 0.3 }]],
};
