// 02 · The Egyptian Experiment (30–60 s). Pyramids and river; barbers line up; the diagram; the eyebrow; the invoice.
import { line, fill, handCircle, smooth, xf } from '../crayon.js';
import { part } from '../rig.js';
import { K, person, sign, say } from '../figs.js';
import { camOf, F, L, ground, clamp, lerp } from './util.js';
const PH = [1080, 870];
export const scissors = (C, T, h) => { const [x, y] = T([[h[0], h[1] - 4]])[0]; [-1, 1].forEach((d, i) => line(C.l, [[x - 10, y + d * 4], [x + 18, y - d * 6]], { w: 4, col: K.grey, p: 1, seed: 210 + i })); line(C.l, handCircle(x - 14, y - 4, 4, 212, 0, 8), { w: 3, seed: 213 }); line(C.l, handCircle(x - 14, y + 6, 4, 214, 0, 8), { w: 3, seed: 215 }); };
const palm = (x, y, i) => { const s = i ? -1 : 1; return [[x, y], [x + s * 10, y - 80], [x + s * 26, y - 160], [x + s * 30, y - 230]]; };
const crook = (x, y) => { const P = []; for (let k = 0; k <= 8; k++) { const a = Math.PI * k / 8; P.push([x + 14 * Math.cos(a + Math.PI), y - 14 * Math.sin(a)]); } return P; };
export default {
  cam: c => camOf(c, [[0, [720, 540, 1]], [c.at(3, -0.3), [720, 540, 1]], [c.at(3, 1.0), [1070, 480, 1.9]], [c.at(4, -0.4), [1070, 480, 1.9]], [c.at(4, 0.4), [740, 640, 1.7]], [30, [740, 640, 1.7]]]),
  draw(S, c) {
    const T = c.turn, d = c.p(T + 0.1, T + 1.4), f = c.p(T + 0.7, T + 2.2);
    part(S.G2, handCircle(1250, 200, 70, 200, 0.05, 30), F(K.yellow, 201, { draw: f, p: 0.95 }), L(202, { draw: d, col: K.orange }));
    [[300, 640, 260], [620, 650, 200], [860, 660, 140]].forEach(([x, y, h], i) => { part(S.G2, [[x - h, y], [x, y - h * 1.1], [x + h, y]], F(K.ochre, 220 + i, { draw: f, ang: 0.3 }), L(224 + i, { draw: d })); for (let r = 1; r < 5; r++) line(S.G2.l, [[x - h + r * h / 5, y - r * h * 1.1 / 5], [x + h - r * h / 5, y - r * h * 1.1 / 5]], L(230 + i * 5 + r, { w: 3, p: 0.5, draw: d })); });
    ground(S.BG, 650, K.ochre, d, 240);
    const rv = []; for (let x = -100; x <= 1540; x += 40) rv.push([x, 700 + 10 * Math.sin(x * 0.02)]);
    fill(S.BG.f, [...rv, [1540, 760], [-100, 760]], F(K.sky, 250, { draw: f, p: 0.9, ang: 0.1 }));
    line(S.BG.l, rv, L(251, { draw: d, col: K.sky })); line(S.BG.l, [[-100, 760], [1540, 760]], L(252, { draw: d, col: K.sky }));
    [[90, 650], [1370, 660]].forEach(([x, y], i) => { line(S.G2.l, palm(x, y, i), L(260 + i, { w: 10, col: K.brown, draw: d })); const top = palm(x, y, i)[3]; for (let k = 0; k < 5; k++) part(S.G2, xf(smooth([[0, 0], [50, -18], [100, 6], [50, -4]], 3), { x: top[0], y: top[1], r: -2.6 + k * 1.1 }), F(K.green, 262 + i * 5 + k, { draw: f, p: 0.95 }), L(272 + i * 5 + k, { draw: d, w: 4, col: K.green })); });
    // the pharaoh on a gold throne
    const pd = c.p(T + 0.8, T + 2.2), pf = c.p(T + 1.3, T + 2.8);
    part(S.G2, [[PH[0] - 120, PH[1] - 390], [PH[0] - 70, PH[1] - 390], [PH[0] - 70, PH[1] - 150], [PH[0] + 110, PH[1] - 150], [PH[0] + 110, PH[1]], [PH[0] - 120, PH[1]]], F(K.ochre, 280, { draw: pf, p: 0.9 }), L(281, { draw: pd }));
    const brow = c.tq > c.at(3, 1.6);
    person(S.G, 'pharaoh', { x: PH[0] - 40, y: PH[1] - 70, s: 1.2, pose: 'sit', draw: pd, fillDraw: pf, expr: brow ? 'eyebrow' : c.tq > c.at(3, -0.2) ? 'neutral' : 'smug', armR: [80, -150], armL: [-70, -140],
      prop: (C, T_, h) => { const [x, y] = T_([[h[0], h[1] - 10]])[0]; line(C.l, [[x, y - 40], [x, y + 50]], L(290, { w: 7, col: K.ochre })); line(C.l, crook(x - 14, y - 40), L(291, { w: 7, col: K.ochre })); } });
    // three barbers file in from the left
    [0, 0.5, 1.0].forEach((k, i) => { const ts = c.at(1, k); if (c.tq < ts - 0.2) return; const u = clamp((c.tq - ts) / 1.4), x = lerp(-120, 300 + i * 160, u), walking = u < 1;
      const step = i === 2 && c.tq > c.at(2) ? Math.min(1, (c.tq - c.at(2)) / 0.8) * 130 : 0;
      person(S.G, 'barber', { x: x + step, y: 880, s: 0.95, view: walking ? 'side' : 'front', pose: walking ? 'walk' : 'stand', ph: c.tq * 1.6 + i * 0.3, expr: i === 2 && c.tq > c.at(2) ? 'worried' : 'neutral', seed: 300 + i * 40,
        armR: i === 2 && c.tq > c.at(2, 0.3) && c.tq < c.at(4, 0.2) ? [96, -210] : i === 2 && c.tq > c.at(4, 0.2) ? [70, -200] : [76, -110], prop: i === 2 && c.tq > c.at(4, 0.2) ? null : scissors }); });
    // the diagram on papyrus: a plain stick figure, modestly draped, one dotted circle, one question mark
    if (c.tq > c.at(2, 0.2)) { const dd = c.p(c.at(2, 0.2), c.at(2, 1.2)), x = 740, y = 400;
      part(S.G2, [[x - 120, y - 170], [x + 120, y - 166], [x + 116, y + 170], [x - 118, y + 166]], F(K.ochre, 320, { draw: dd, p: 0.4 }), L(321, { draw: dd }));
      line(S.G2.l, handCircle(x, y - 100, 26, 322, 0, 20), L(323, { w: 4, draw: dd })); line(S.G2.l, [[x, y - 74], [x, y + 30]], L(324, { w: 4, draw: dd })); line(S.G2.l, [[x - 50, y - 40], [x + 50, y - 40]], L(325, { w: 4, draw: dd })); line(S.G2.l, [[x, y + 30], [x - 30, y + 120]], L(326, { w: 4, draw: dd })); line(S.G2.l, [[x, y + 30], [x + 30, y + 120]], L(327, { w: 4, draw: dd }));
      part(S.G2, [[x - 34, y + 10], [x + 34, y + 10], [x + 40, y + 56], [x - 40, y + 56]], F(K.white, 328, { draw: dd, p: 0.95 }), L(329, { draw: dd, w: 4 }));
      if (c.tq > c.at(2, 1.2)) { const q = c.p(c.at(2, 1.2), c.at(2, 1.9)); for (let i = 0; i < 9; i++) { const a = i / 9 * Math.PI * 2; line(S.FX, [[x + Math.cos(a) * 62, y + 34 + Math.sin(a) * 44], [x + Math.cos(a + 0.22) * 62, y + 34 + Math.sin(a + 0.22) * 44]], { w: 5, col: K.red, p: 1, seed: 330 + i, draw: clamp(q * 9 - i) }); }
        say(S.FX, '?', x + 92, y + 16, { size: 90, font: 'Gaegu', weight: 700, col: K.red, reveal: c.p(c.at(2, 1.9), c.at(2, 2.1)), seed: 340 }); } }
    // the invoice, held up very small
    if (c.tq > c.at(4, 0.2)) { const k = c.p(c.at(4, 0.2), c.at(4, 0.6)), bx = 620 + 130 + 70, by = 880 - 200 * 0.95 - 70;
      sign(S.G, bx, by - 30 * k, 128, 62, 'HAZARD PAY', { seed: 350, col: K.white, size: 24, reveal: c.p(c.at(4, 0.5), c.at(4, 1.1)), draw: k }); }
  },
  sfx: c => [[c.turn + 0.1, 'scratch', { dur: 1.3, pan: -0.3 }], [c.turn + 0.7, 'scribble', { dur: 1.5, pan: 0 }], [c.turn + 1.3, 'scribble', { dur: 1.4, pan: 0.5 }], [c.turn, 'river', { dur: 29 }],
    [c.at(1), 'steps', { dur: 2.6, pan: -0.5 }], [c.at(1, 1.6), 'snip', { pan: -0.4 }], [c.at(2), 'steps', { dur: 0.8, pan: -0.2 }], [c.at(2, 0.2), 'paper', { pan: 0 }], [c.at(2, 1.2), 'scratch', { dur: 0.8 }],
    [c.at(3, 1.6), 'brow', { pan: 0.4 }], [c.at(4, 0.2), 'paper', { pan: -0.3 }], [c.at(4, 0.5), 'write', { dur: 0.6, pan: -0.3 }]],
};
