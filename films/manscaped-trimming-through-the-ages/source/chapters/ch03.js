// 03 · The Greek Question (60–90 s). Columns, amphitheatre, thinkers; WHO? WHY? HOW?; the bush beside the chair;
// a scroll unrolls a bold new theory, and is quietly rolled up again.
import { line, fill, handCircle, ellipse, smooth } from '../crayon.js';
import { part } from '../rig.js';
import { K, person, say, bush, scroll } from '../figs.js';
import { camOf, F, L, ground, box, clamp } from './util.js';
const PX = 640, PY = 870;
export default {
  cam: c => camOf(c, [[0, [720, 540, 1]], [c.at(2, -0.3), [720, 540, 1]], [c.at(2, 1.2), [800, 700, 1.55]], [c.at(3, -0.3), [800, 700, 1.55]], [c.at(3, 0.6), [800, 560, 1.25]], [30, [790, 570, 1.3]]]),
  draw(S, c) {
    const T = c.turn, d = c.p(T + 0.1, T + 1.4), f = c.p(T + 0.6, T + 2.2);
    // amphitheatre: stepped arcs
    for (let r = 0; r < 4; r++) { const P = ellipse(720, 560, 560 - r * 70, 150 - r * 22, 40, Math.PI, Math.PI * 2); line(S.BG.l, P, L(400 + r, { draw: d, col: K.grey, w: 5 })); }
    fill(S.BG.f, [...ellipse(720, 560, 560, 150, 40, Math.PI, Math.PI * 2), [1280, 560], [160, 560]], F(K.ochre, 405, { draw: f, p: 0.35, ang: 0.1 }));
    ground(S.BG, 640, K.white, d, 410); fill(S.BG.f, [[-200, 640], [1640, 640], [1640, 1100], [-200, 1100]], F(K.grey, 411, { draw: f, p: 0.25, ang: 0.05, gap: 16 }));
    // two marble columns
    [140, 1300].forEach((x, i) => { box(S.G2, x - 60, 150, 120, 30, K.white, 420 + i * 5, d); box(S.G2, x - 46, 180, 92, 450, K.white, 422 + i * 5, d, { p: 0.95 }); box(S.G2, x - 64, 630, 128, 26, K.white, 424 + i * 5, d);
      for (let k = 0; k < 4; k++) line(S.G2.l, [[x - 30 + k * 20, 190], [x - 30 + k * 20, 620]], L(440 + i * 5 + k, { w: 3, col: K.grey, draw: d })); });
    // a stone chair and the philosopher on it; two colleagues behind
    person(S.G2, 'philosopher', { x: 380, y: 760, s: 0.8, beard: 'short', hairCol: K.grey, sash: K.red, seed: 470, draw: c.p(T + 0.5, T + 1.6), expr: c.tq > c.at(4, 0.6) ? 'eyebrow' : 'neutral' });
    person(S.G2, 'philosopher', { x: 1080, y: 760, s: 0.8, beard: 'short', hairCol: K.brown, sash: K.green, seed: 480, flip: true, draw: c.p(T + 0.6, T + 1.7), expr: c.tq > c.at(4, 0.6) ? 'eyebrow' : 'neutral' });
    box(S.G2, PX - 110, PY - 180, 220, 40, K.white, 450, c.p(T + 0.6, T + 1.4)); box(S.G2, PX - 100, PY - 140, 30, 140, K.white, 452, c.p(T + 0.6, T + 1.4)); box(S.G2, PX + 70, PY - 140, 30, 140, K.white, 454, c.p(T + 0.6, T + 1.4));
    const look = c.tq > c.at(2, 0.4) && c.tq < c.at(3), hide = c.tq > c.at(4, 0.4);
    const sOpen = c.tq < c.at(3) ? 0 : c.tq < c.at(4) ? c.p(c.at(3, 0.2), c.at(3, 1.6)) : 1 - c.p(c.at(4, 0.0), c.at(4, 0.6));
    person(S.G, 'philosopher', { x: PX, y: PY - 80, s: 1.15, pose: 'sit', view: look ? 'q' : 'front', flip: false, draw: c.p(T + 0.7, T + 2.0), fillDraw: c.p(T + 1.0, T + 2.4),
      expr: look ? 'worried' : hide ? 'happy' : c.tq > c.at(3) ? 'smug' : 'neutral', armR: hide ? [60, -120] : sOpen > 0 ? [96, -170] : [80, -112], armL: hide ? [-60, -120] : [-80, -112] });
    // WHO? WHY? HOW? on three little sheets, one per word of the line
    ['WHO?', 'WHY?', 'HOW?'].forEach((w, i) => { const ts = c.at(1, 0.2 + i * 0.9); if (c.tq < ts) return; const dd = c.p(ts, ts + 0.4), x = 420 + i * 300, y = 300 + (i % 2) * 30;
      part(S.G2, [[x - 110, y - 70], [x + 110, y - 66], [x + 106, y + 66], [x - 108, y + 62]], F(K.white, 460 + i, { draw: dd, p: 0.9 }), L(463 + i, { draw: dd, w: 4.5 }));
      say(S.G2.l, w, x, y + 24, { size: 72, font: 'Gaegu', weight: 700, reveal: c.p(ts + 0.2, ts + 0.7), seed: 466 + i }); });
    // the giant scribbled bush beside the chair
    if (c.tq > c.at(2, -0.2)) bush(S.G2, 940, 800, 170, 105, { seed: 490, draw: c.p(c.at(2, -0.2), c.at(2, 1.0)), fillDraw: c.p(c.at(2, 0.4), c.at(2, 1.6)) });
    // the scroll
    if (sOpen > 0) { const [a, b] = scroll(S.G, 760, 520, 560, sOpen, { seed: 500, h: 170 }); const rv = clamp((sOpen - 0.3) / 0.7) * c.p(c.at(3, 0.6), c.at(3, 2.2));
      if (rv > 0) { say(S.G.l, 'ON THE NATURE', (a + b) / 2, 506, { size: 48, font: 'Gaegu', weight: 700, reveal: rv, seed: 501 }); say(S.G.l, 'OF THE BUSH', (a + b) / 2, 566, { size: 48, font: 'Gaegu', weight: 700, reveal: c.p(c.at(3, 1.6), c.at(3, 2.6)) * clamp((sOpen - 0.5) / 0.5), seed: 502 }); } }
  },
  sfx: c => [[c.turn + 0.1, 'scratch', { dur: 1.3, pan: -0.5 }], [c.turn + 0.6, 'scribble', { dur: 1.6 }], [c.turn + 0.9, 'scratch', { dur: 1.1, pan: 0.2 }],
    [c.at(1, 0.2), 'write', { dur: 0.5, pan: -0.4 }], [c.at(1, 1.1), 'write', { dur: 0.5, pan: 0 }], [c.at(1, 2.0), 'write', { dur: 0.5, pan: 0.4 }],
    [c.at(2, -0.2), 'scribble', { dur: 1.8, pan: 0.4 }], [c.at(3, 0.2), 'unroll', { dur: 1.4 }], [c.at(3, 0.6), 'write', { dur: 2.0 }], [c.at(4, 0.0), 'unroll', { dur: 0.6 }], [c.at(4, 0.6), 'cough', { pan: 0.1 }]],
};
