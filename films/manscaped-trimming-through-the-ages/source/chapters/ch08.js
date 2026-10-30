// 08 · The Electric Age (210–240 s). A chrome-and-tile bathroom; the salesman's electric face shaver; the flip chart
// (FACE ✓, NECK ✓, then NOT THERE); he folds it away with a nervous smile.
import { line, fill, handCircle, ellipse, smooth, xf } from '../crayon.js';
import { part } from '../rig.js';
import { K, person, say } from '../figs.js';
import { camOf, F, L, ground, box, clamp, lerp, tick, cross, sparkle, wob } from './util.js';
const EX = 980, EY = 420;   // chart centre
export default {
  cam: c => camOf(c, [[0, [720, 540, 1]], [c.at(1, -0.2), [720, 540, 1]], [c.at(1, 0.6), [520, 560, 1.4]], [c.at(2, -0.3), [520, 560, 1.4]], [c.at(2, 0.5), [880, 500, 1.3]], [c.at(4, -0.3), [880, 500, 1.3]], [c.at(4, 0.5), [640, 560, 1.2]], [30, [640, 560, 1.2]]]),
  draw(S, c) {
    const T = c.turn, d = c.p(T + 0.1, T + 1.4), f = c.p(T + 0.6, T + 2.4);
    // tiles (pale sky grid), chrome mirror, basin with taps, towel rail, plug socket with a little spark
    fill(S.BG.f, [[-200, 0], [1640, 0], [1640, 860], [-200, 860]], F(K.sky, 1500, { draw: f, p: 0.35, gap: 14, ang: 0.0 }));
    for (let k = 0; k < 15; k++) line(S.BG.l, [[k * 100, 120], [k * 100, 860]], L(1501 + k, { w: 3, col: K.white, p: 0.9, draw: d }));
    for (let k = 0; k < 8; k++) line(S.BG.l, [[-200, 160 + k * 100], [1640, 160 + k * 100]], L(1520 + k, { w: 3, col: K.white, p: 0.9, draw: d }));
    ground(S.BG, 860, K.white, d, 1530);
    part(S.G2, [[110, 220], [430, 220], [430, 520], [110, 520]], F(K.white, 1540, { draw: f, p: 0.6 }), L(1541, { draw: d, col: K.grey, w: 10 }));
    line(S.G2.l, [[150, 260], [220, 330]], L(1542, { w: 5, col: K.white, p: 1, draw: d }));
    part(S.G2, smooth([[110, 600], [430, 600], [400, 690], [140, 690]], 3), F(K.white, 1543, { draw: f, p: 0.95 }), L(1544, { draw: d }));
    line(S.G2.l, [[270, 690], [270, 860]], L(1545, { w: 12, col: K.white, draw: d })); line(S.G2.l, [[270, 860], [270, 690]], L(1546, { w: 4, col: K.grey, draw: d }));
    [[200, 590], [340, 590]].forEach(([x, y], i) => part(S.G2, [[x - 10, y], [x + 10, y], [x + 10, y - 30], [x + 26, y - 30], [x + 26, y - 40], [x - 10, y - 40]], F(K.grey, 1547 + i, { draw: f }), L(1549 + i, { draw: d, w: 4 })));
    line(S.G2.l, [[1240, 300], [1400, 300]], L(1551, { w: 8, col: K.grey, draw: d })); part(S.G2, [[1260, 300], [1380, 300], [1380, 470], [1260, 470]], F(K.pink, 1552, { draw: f }), L(1553, { draw: d }));
    box(S.G2, 1270, 640, 60, 70, K.white, 1554, d); [1290, 1310].forEach((x, i) => line(S.G2.l, [[x, 660], [x, 690]], L(1556 + i, { w: 4, draw: d })));
    // the salesman and the shaver (a generic chrome face shaver, cord and all)
    const fold = c.p(c.at(4, 0.0), c.at(4, 0.8));
    person(S.G, 'salesman', { x: 560, y: 880, s: 1.15, view: c.tq > c.at(2, -0.2) ? 'q' : 'front', draw: c.p(T + 0.6, T + 1.8), fillDraw: c.p(T + 0.9, T + 2.4), seed: 1560,
      expr: c.tq > c.at(4, 0.4) ? 'worried' : c.tq > c.at(3, 0.5) ? 'worried' : 'happy', armR: c.tq < c.at(2, -0.2) ? [90, -240] : [120, -200],
      prop: (C, T_, h) => { if (c.tq > c.at(2, -0.2)) return; const [x, y] = T_([[h[0], h[1] - 30]])[0], hum = c.tq > c.at(1, 0.2) ? 1.5 * wob(c, 13) : 0;
        part(C, smooth([[x - 22 + hum, y + 40], [x - 26 + hum, y - 20], [x - 14 + hum, y - 46], [x + 14 + hum, y - 46], [x + 26 + hum, y - 20], [x + 22 + hum, y + 40]], 3), F(K.grey, 1570, { p: 0.95 }), L(1571, { w: 5 }));
        part(C, [[x - 20 + hum, y - 46], [x + 20 + hum, y - 46], [x + 18 + hum, y - 58], [x - 18 + hum, y - 58]], F(K.white, 1572, { p: 0.95 }), L(1573, { w: 4 })); for (let k = 0; k < 4; k++) line(C.l, [[x - 14 + k * 9 + hum, y - 56], [x - 14 + k * 9 + hum, y - 48]], L(1574 + k, { w: 2.5 }));
        line(C.l, [[x, y + 40], [x - 10, y + 120], [x + 60, y + 160]], L(1578, { w: 4 })); } });
    if (c.tq > c.at(1, 0.4) && c.tq < c.at(2, -0.2)) [[680, 470], [760, 520], [700, 400]].forEach(([x, y], i) => sparkle(S.FX, x, y, 10 + 8 * Math.abs(Math.sin(c.t * 5 + i)), 1580 + i * 2));
    // the flip chart on an easel
    if (c.tq > c.at(2, -0.5)) { const ed = c.p(c.at(2, -0.5), c.at(2, 0.2)), sq = 1 - 0.75 * fold, W2 = 230 * sq, H2 = 270 * sq;
      line(S.G2.l, [[EX - 150, 860], [EX - 90, 160]], L(1590, { w: 8, col: K.brown, draw: ed })); line(S.G2.l, [[EX + 150, 860], [EX + 90, 160]], L(1591, { w: 8, col: K.brown, draw: ed }));
      part(S.G, [[EX - W2, EY - H2], [EX + W2, EY - H2], [EX + W2, EY + H2], [EX - W2, EY + H2]], F(K.white, 1592, { draw: ed, p: 0.95 }), L(1593, { draw: ed }));
      if (fold < 0.3) {
        const page2 = c.tq > c.at(3, -0.2), flip = c.p(c.at(3, -0.2), c.at(3, 0.2));
        if (!page2 || flip < 1) {   // page 1: a smiling face, FACE ✓ NECK ✓, and a question below
          line(S.G.l, handCircle(EX, EY - 120, 60, 1600, 0.05, 30), L(1601, { w: 5, draw: c.p(c.at(2, 0.1), c.at(2, 0.6)) }));
          [[EX - 22, EY - 130], [EX + 22, EY - 130]].forEach(([x, y], i) => fill(S.G.l, handCircle(x, y, 5, 1602 + i, 0, 10), F(K.ink, 1604 + i, { p: 1 })));
          say(S.G.l, 'FACE', EX - 60, EY + 0, { size: 46, font: 'Gaegu', weight: 700, reveal: c.p(c.at(2, 0.6), c.at(2, 1.0)), seed: 1606 }); tick(S.G.l, EX + 70, EY - 14, 1.3, c.p(c.at(2, 1.0), c.at(2, 1.2)), 1607);
          say(S.G.l, 'NECK', EX - 60, EY + 70, { size: 46, font: 'Gaegu', weight: 700, reveal: c.p(c.at(2, 1.3), c.at(2, 1.7)), seed: 1608 }); tick(S.G.l, EX + 70, EY + 56, 1.3, c.p(c.at(2, 1.7), c.at(2, 1.9)), 1609);
          say(S.G.l, '?', EX, EY + 190, { size: 110, font: 'Gaegu', weight: 700, col: K.red, reveal: c.p(c.at(2, 2.4), c.at(2, 2.6)), seed: 1610 });
          if (flip > 0) part(S.G, [[EX - W2, EY - H2], [EX + W2, EY - H2], [EX + W2, lerp(EY - H2, EY + H2, 1 - flip)], [EX - W2, lerp(EY - H2, EY + H2, 1 - flip)]], F(K.white, 1611, { p: 1 }), L(1612));
        } else {   // page 2
          say(S.G.l, 'NOT', EX, EY - 60, { size: 110, font: 'Gaegu', weight: 700, reveal: c.p(c.at(3, 0.3), c.at(3, 0.8)), seed: 1613 });
          say(S.G.l, 'THERE', EX, EY + 50, { size: 110, font: 'Gaegu', weight: 700, reveal: c.p(c.at(3, 0.8), c.at(3, 1.4)), seed: 1614 });
          line(S.G.l, [[EX, EY + 110], [EX, EY + 230]], L(1615, { w: 8, col: K.red, draw: c.p(c.at(3, 1.6), c.at(3, 2.0)) })); line(S.G.l, [[EX - 30, EY + 200], [EX, EY + 236], [EX + 30, EY + 200]], L(1616, { w: 8, col: K.red, draw: c.p(c.at(3, 1.9), c.at(3, 2.1)) }));
          if (c.tq > c.at(3, 2.4)) { cross(S.G.l, EX - 140, EY - 160, EX + 140, EY + 150, c.p(c.at(3, 2.4), c.at(3, 2.9)), 1617); cross(S.G.l, EX + 140, EY - 160, EX - 140, EY + 150, c.p(c.at(3, 2.7), c.at(3, 3.2)), 1621); }
        }
      }
      if (c.tq > c.at(4, 0.5)) line(S.FX, [[640, 620], [636, 636], [644, 640], [640, 620]], { w: 6, col: K.sky, p: 1, seed: 1630 });   // a bead of sweat
    }
  },
  sfx: c => [[c.turn + 0.1, 'scratch', { dur: 1.3, pan: -0.4 }], [c.turn + 0.6, 'scribble', { dur: 1.8 }], [c.turn + 0.5, 'drip', { pan: -0.6 }], [c.turn + 3.5, 'drip', { pan: -0.6 }],
    [c.at(1, 0.2), 'shaver', { dur: c.at(2, -0.4) - c.at(1, 0.2), pan: -0.2 }], [c.at(2, -0.5), 'easel', { pan: 0.4 }], [c.at(2, 0.1), 'marker', { dur: 2.2, pan: 0.4 }], [c.at(3, -0.2), 'flip', { pan: 0.4 }],
    [c.at(3, 0.3), 'marker', { dur: 1.9, pan: 0.4 }], [c.at(3, 2.4), 'scratch', { dur: 0.8, pan: 0.4 }], [c.at(4, 0.0), 'fold', { pan: 0.4 }], [c.at(4, 0.5), 'gulp', { pan: -0.1 }]],
};
