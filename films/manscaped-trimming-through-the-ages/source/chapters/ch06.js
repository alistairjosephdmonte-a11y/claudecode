// 06 · A Renaissance Invention (150–180 s). Workshop; the inventor sketches; the machine assembles stroke by stroke
// (gears, levers, a crank, a pair of shears on an arm); the lever; it trims only his beard.
import { line, fill, handCircle, ellipse, smooth, xf } from '../crayon.js';
import { part } from '../rig.js';
import { K, person, say, gear } from '../figs.js';
import { camOf, F, L, ground, box, clamp, lerp, hash, wob } from './util.js';
const MX = 1000;   // machine centre x
const GEARS = [[920, 520, 70, 10], [1040, 470, 50, 8], [1120, 560, 40, 7], [880, 660, 46, 8], [1010, 640, 60, 9], [1160, 680, 34, 6], [960, 760, 30, 6]];
export default {
  cam: c => camOf(c, [[0, [720, 540, 1]], [c.at(4, -0.3), [720, 540, 1]], [c.at(4, 0.6), [560, 560, 1.6]], [30, [560, 560, 1.6]]]),
  draw(S, c) {
    const T = c.turn, d = c.p(T + 0.1, T + 1.4), f = c.p(T + 0.6, T + 2.2);
    // the workshop: floorboards, a beam, an arched window, wall gears, a table with paper, ink and quill
    ground(S.BG, 860, K.brown, d, 1100); for (let k = 0; k < 8; k++) line(S.BG.l, [[k * 200 - 40, 870], [k * 200 + 40, 1080]], L(1101 + k, { w: 3, p: 0.4, draw: d }));
    box(S.G2, -20, 120, 1480, 40, K.brown, 1110, d);
    part(S.G2, smooth([[1180, 520], [1180, 300], [1250, 230], [1320, 300], [1320, 520]], 3), F(K.sky, 1112, { draw: f, p: 0.5 }), L(1113, { draw: d }));
    line(S.G2.l, [[1250, 240], [1250, 520]], L(1114, { w: 4, draw: d })); line(S.G2.l, [[1180, 380], [1320, 380]], L(1115, { w: 4, draw: d }));
    gear(S.G2, 140, 300, 60, 9, c.t * 0.3, { seed: 1120, draw: d }); gear(S.G2, 230, 380, 38, 7, -c.t * 0.5, { seed: 1125, draw: d, col: K.grey });
    box(S.G2, 60, 640, 360, 30, K.brown, 1130, d); line(S.G2.l, [[90, 670], [90, 860]], L(1131, { w: 8, col: K.brown, draw: d })); line(S.G2.l, [[390, 670], [390, 860]], L(1132, { w: 8, col: K.brown, draw: d }));
    part(S.G2, [[110, 600], [260, 596], [262, 640], [112, 642]], F(K.white, 1133, { draw: f, p: 0.8 }), L(1134, { draw: d, w: 4 }));
    part(S.G2, [[300, 600], [340, 600], [344, 640], [296, 640]], F(K.ink, 1135, { draw: f }), L(1136, { draw: d, w: 4 })); line(S.G2.l, [[320, 600], [360, 520]], L(1137, { w: 4, draw: d, col: K.white }));
    // the inventor: at his drawing board (beats 1–2), then at the lever (beats 4–5); his beard goes in beat 5
    const atLever = c.tq > c.at(3, -0.6), trim = c.p(c.at(4, 0.0), c.at(4, 0.5));
    const ix = atLever ? lerp(420, 640, c.p(c.at(3, -0.6), c.at(3, 0.2))) : 420, sk = c.tq > c.at(1) && c.tq < c.at(2, 1) ? 12 * Math.sin(Math.floor(c.tq * 12) * 2) : 0;
    person(S.G, 'inventor', { x: ix, y: 880, s: 1.2, view: atLever ? 'q' : 'q', draw: c.p(T + 0.5, T + 1.8), fillDraw: c.p(T + 0.9, T + 2.4), beardLen: 1 - trim * 0.96,
      expr: trim > 0 ? (c.tq > c.at(4, 1.2) ? 'neutral' : 'shock') : c.tq > c.at(3) ? 'happy' : 'neutral', armR: atLever ? (c.tq > c.at(3, 0.2) ? [100, -130] : [96, -220]) : [110 + sk, -200 + sk * 0.5] });
    // the falling beard trimmings
    if (trim > 0) for (let k = 0; k < 14; k++) { const u = clamp((c.tq - c.at(4, 0.1 + k * 0.03)) / 0.9); if (u <= 0) continue; const x = ix + 8 + (hash(k) - 0.5) * 80, y = 880 - 1.2 * 200 + u * 220 + hash(k + 3) * 30;
      line(S.FX, [[x, y], [x + 8 * Math.cos(k), y + 10]], { w: 4, col: K.brown, p: 0.95, seed: 1150 + k }); }
    // the big sheet with the sketch (beat 2)
    if (c.tq > c.at(1, -0.2) && c.tq < c.at(2, 1.0)) { const sd = c.p(c.at(1, -0.2), c.at(1, 0.4)); part(S.G2, [[620, 230], [1100, 226], [1104, 560], [624, 564]], F(K.ochre, 1160, { draw: sd, p: 0.3 }), L(1161, { draw: sd }));
      const q = c.p(c.at(1, 0.4), c.at(2, 0.4)); [[760, 400, 60], [860, 360, 40], [900, 450, 34]].forEach(([x, y, r], i) => line(S.G2.l, handCircle(x, y, r, 1162 + i, 0.1, 24), L(1165 + i, { w: 3.5, draw: clamp(q * 4 - i) })));
      line(S.G2.l, [[700, 520], [1040, 520], [1040, 300]], L(1168, { w: 3.5, draw: clamp(q * 4 - 2) })); line(S.G2.l, [[1040, 300], [980, 260], [1000, 250], [1050, 290]], L(1169, { w: 3.5, draw: clamp(q * 4 - 3) }));
      say(S.G2.l, '47 gears · 6 levers', 860, 270, { size: 34, reveal: clamp(q * 3 - 2), seed: 1170 }); }
    // the machine assembles (beat 3) and shakes (beat 4)
    if (c.tq > c.at(2, 0.6)) { const shake = c.tq > c.at(3, 0.3) && c.tq < c.at(4, 0.6) ? 1 : 0, jx = shake * 5 * wob(c, 9), jy = shake * 4 * wob(c, 7), spin = shake ? c.t * 4 : 0;
      const fr = c.p(c.at(2, 0.6), c.at(2, 1.4));
      part(S.G2, [[MX - 200 + jx, 860], [MX - 160 + jx, 420 + jy], [MX + 200 + jx, 420 + jy], [MX + 240 + jx, 860]], null, L(1180, { draw: fr, col: K.brown, w: 8 }));
      GEARS.forEach(([x, y, r, n], i) => { const ts = c.at(2, 1.0 + i * 0.45); if (c.tq < ts) return; gear(S.G, x + jx, y + jy, r, n, (i % 2 ? -1 : 1) * spin + i, { seed: 1190 + i * 6, col: [K.ochre, K.grey, K.ochre, K.yellow, K.grey, K.ochre, K.yellow][i], draw: clamp((c.tq - ts) / 0.35) }); });
      for (let k = 0; k < 6; k++) { const ts = c.at(2, 2.4 + k * 0.3); if (c.tq < ts) continue; const x = MX + 150 + jx, y = 470 + k * 60 + jy, a = c.tq > c.at(3, 0.2) && k === 0 ? 0.9 : -0.5; line(S.G.l, [[x, y], [x + 70 * Math.cos(a), y - 70 * Math.sin(a)]], L(1230 + k, { w: 7, col: K.brown, draw: clamp((c.tq - ts) / 0.25) })); fill(S.G.l, handCircle(x + 70 * Math.cos(a), y - 70 * Math.sin(a), 11, 1240 + k, 0, 12), F(K.red, 1246 + k, { p: 1 })); }
      // the shears on a long arm reaching toward where the inventor will stand
      if (c.tq > c.at(2, 4.0)) { const ad = c.p(c.at(2, 4.0), c.at(2, 4.8)), reach = c.tq > c.at(4, 0.0) && c.tq < c.at(4, 0.6) ? 40 : 0, ax = MX - 190 - reach + jx, ay = 600 + jy;
        line(S.G.l, [[MX - 150 + jx, 560 + jy], [ax + 40, ay]], L(1250, { w: 9, col: K.grey, draw: ad }));
        const op = Math.floor(c.tq * 12) % 2 && reach ? 0.5 : 0.2; [-op, op].forEach((a, i) => line(S.G.l, [[ax + 40, ay], [ax + 40 - 60 * Math.cos(a), ay - 60 * Math.sin(a)]], L(1251 + i, { w: 6, col: K.grey, draw: ad }))); }
      // the lever the inventor pulls
      const la = c.tq > c.at(3, 0.2) ? 0.5 : -0.6; line(S.G.l, [[MX - 180 + jx, 820], [MX - 180 + 120 * Math.sin(la) + jx, 820 - 120 * Math.cos(la)]], L(1260, { w: 10, col: K.red, draw: fr }));
      if (shake) for (let k = 0; k < 3; k++) { const ph = (c.tq * 1.5 + k * 0.33) % 1; part(S.FX ? S.G : S.G, handCircle(MX + 80 - k * 60, 400 - ph * 180, 20 + ph * 26, 1270 + k, 0.1, 18), F(K.grey, 1273 + k, { p: 0.6 * (1 - ph) }), null, { occ: false, kn: false }); }
    }
  },
  sfx: c => [[c.turn + 0.1, 'scratch', { dur: 1.3, pan: -0.4 }], [c.turn + 0.6, 'scribble', { dur: 1.6 }], [c.turn + 0.5, 'gears', { dur: 29, v: 0.25 }], [c.at(1, -0.2), 'paper', { pan: 0.3 }], [c.at(1, 0.4), 'quill', { dur: c.at(2, 0.4) - c.at(1, 0.4), pan: 0.2 }],
    [c.at(2, 0.6), 'scratch', { dur: 0.8, pan: 0.4 }], ...[0, 1, 2, 3, 4, 5, 6].map(i => [c.at(2, 1.0 + i * 0.45), 'clunk', { pan: 0.3 + i * 0.04 }]), ...[0, 1, 2, 3, 4, 5].map(k => [c.at(2, 2.4 + k * 0.3), 'click', { pan: 0.5 }]),
    [c.at(3, 0.2), 'lever', { pan: 0.3 }], [c.at(3, 0.3), 'rattle', { dur: c.at(4, 0.6) - c.at(3, 0.3), pan: 0.3 }], [c.at(4, 0.0), 'snip', { pan: -0.1 }], [c.at(4, 0.15), 'snip', { pan: -0.1 }], [c.at(4, 0.3), 'snip', { pan: -0.1 }], [c.at(4, 0.6), 'wind', { pan: 0.3 }]],
};
