// 05 · Medieval Armour (120–150 s). Castle and knight; the squire polishes; the knight fidgets; the blacksmith lifts
// one armour flap (a moth flies out), closes it, and hangs OUT OF OFFICE on his forge.
import { line, fill, handCircle, ellipse, smooth, xf } from '../crayon.js';
import { part } from '../rig.js';
import { K, person, say, sign } from '../figs.js';
import { camOf, F, L, ground, box, clamp, lerp, sparkle, wob } from './util.js';
const KX = 700, KY = 880;
export default {
  cam: c => camOf(c, [[0, [720, 540, 1]], [c.at(2, -0.3), [720, 540, 1]], [c.at(2, 0.8), [740, 660, 1.5]], [c.at(3, -0.3), [740, 660, 1.5]], [c.at(3, 0.6), [800, 620, 1.3]], [c.at(4, -0.3), [800, 620, 1.3]], [c.at(4, 0.5), [880, 560, 1.15]], [30, [880, 560, 1.15]]]),
  draw(S, c) {
    const T = c.turn, d = c.p(T + 0.1, T + 1.5), f = c.p(T + 0.6, T + 2.2);
    ground(S.BG, 860, K.green, d, 900);
    // castle: two towers and a curtain wall with crenellations, flags flapping on twos
    [[160, 220], [1260, 240]].forEach(([x, y], i) => { box(S.G2, x - 90, y, 180, 860 - y, K.grey, 910 + i * 3, d, { p: 0.75 }); for (let k = 0; k < 3; k++) box(S.G2, x - 90 + k * 70, y - 40, 40, 40, K.grey, 920 + i * 5 + k, d);
      line(S.G2.l, [[x, y - 40], [x, y - 150]], L(930 + i, { draw: d, w: 5 })); const fl = Math.floor(c.tq * 6) % 2 ? 10 : -6;
      part(S.G2, [[x, y - 150], [x + 90, y - 130 + fl], [x, y - 104]], F(K.red, 932 + i, { draw: f, p: 0.95 }), L(934 + i, { draw: d, w: 4 })); });
    box(S.G2, 250, 380, 920, 480, K.grey, 940, d, { p: 0.55 }); for (let k = 0; k < 9; k++) box(S.G2, 260 + k * 104, 340, 56, 40, K.grey, 950 + k, d);
    // the forge (blacksmith's corner) at the right
    const fx = 1120; box(S.G2, fx - 90, 640, 180, 220, K.brown, 970, d, { p: 0.85 }); part(S.G2, smooth([[fx - 60, 650], [fx - 30, 590 - 10 * (Math.floor(c.tq * 12) % 2)], [fx, 620], [fx + 30, 580], [fx + 60, 650]], 3), F(K.orange, 972, { draw: f, p: 0.95 }), L(973, { draw: d, col: K.red, w: 4 }));
    // the knight (short, oversized armour): fidgets during beat 3
    const fid = c.tq > c.at(2, 0.4) && c.tq < c.at(3) ? 1 : 0, jx = fid * 6 * wob(c, 7), jr = fid * 0.04 * wob(c, 5);
    person(S.G, 'knight', { x: KX + jx, y: KY, s: 1.55, r: jr, draw: c.p(T + 0.6, T + 2.0), fillDraw: c.p(T + 1.0, T + 2.6), expr: fid ? 'worried' : c.tq > c.at(3, 1.2) ? 'shock' : 'smug', armL: [-80, -110], armR: [80, -110] });
    // the hinged tasset (the flap): lifted by the blacksmith in beat 4
    const lift = c.tq < c.at(3, 0.6) ? 0 : c.tq < c.at(3, 1.8) ? c.p(c.at(3, 0.6), c.at(3, 1.0)) : 1 - c.p(c.at(3, 2.6), c.at(3, 3.0));
    const hx = KX + jx, hy = KY - 1.55 * 60;
    part(S.G, xf([[-40, 0], [40, 0], [44, 42], [-44, 42]], { x: hx, y: hy, s: 1.55 }).map(([x, y]) => [x, lerp(y, hy - (y - hy) * 0.9 - 6, lift)]), F(K.grey, 980, { p: 0.95 }), L(981));
    if (lift > 0.6 && c.tq < c.at(3, 2.8)) { const u = c.p(c.at(3, 1.0), c.at(3, 3.0)); const mx = hx + 30 + 260 * u, my = hy + 20 - 220 * u + 20 * Math.sin(u * 30), fl = Math.floor(c.tq * 12) % 2;   // a moth leaves
      part(S.FX ? S.G : S.G, [[mx, my], [mx - 18, my - 14 - fl * 6], [mx - 22, my + 4]], F(K.grey, 985, { p: 0.9 }), L(986, { w: 3 })); part(S.G, [[mx, my], [mx + 18, my - 14 - fl * 6], [mx + 22, my + 4]], F(K.grey, 987, { p: 0.9 }), L(988, { w: 3 })); }
    // the squire polishing (beat 2), sparkles where the cloth has been
    if (c.tq > c.at(1, -0.3) && c.tq < c.at(3, -0.2)) { const sd = c.p(c.at(1, -0.3), c.at(1, 0.4)), rub = 16 * Math.sin(Math.floor(c.tq * 12) * 1.6);
      person(S.G, 'squire', { x: 430, y: 880, s: 0.95, view: 'q', seed: 990, draw: sd, armR: [120 + rub, -190 + rub * 0.3], expr: 'happy',
        prop: (C, T_, h) => part(C, T_(smooth([[h[0] - 10, h[1] - 18], [h[0] + 22, h[1] - 14], [h[0] + 20, h[1] + 16], [h[0] - 12, h[1] + 12]], 3)), F(K.white, 995), L(996, { w: 3.5 })) });
      [[KX - 60, KY - 330], [KX + 40, KY - 230], [KX - 20, KY - 180], [KX + 70, KY - 360]].forEach(([x, y], i) => { const ts = c.at(1, 0.6 + i * 0.8); if (c.tq > ts) sparkle(S.FX, x, y, 14 + 10 * Math.abs(Math.sin((c.t - ts) * 6)), 1000 + i * 2); }); }
    // the blacksmith arrives (beat 4) and then retires (beat 5)
    if (c.tq > c.at(3, -0.6)) { const ar = c.p(c.at(3, -0.6), c.at(3, 0.4)), gone = c.p(c.at(4, 0.8), c.at(4, 2.6));
      const x = gone > 0 ? lerp(1000, 1600, gone) : lerp(1500, 940, ar);
      person(S.G, 'smith', { x, y: 880, s: 1.0, view: ar < 1 || gone > 0 ? 'side' : 'front', flip: !(gone > 0) && ar < 1, pose: ar < 1 || gone > 0 ? 'walk' : 'stand', ph: c.tq * 1.6, seed: 1010,
        expr: c.tq > c.at(3, 1.0) ? 'shock' : 'neutral', armL: lift > 0 && gone === 0 ? [-110, -110] : undefined }); }
    if (c.tq > c.at(4, 0.0)) sign(S.G2, 1120, 470, 230, 70, 'OUT OF OFFICE', { seed: 1020, string: 40, col: K.white, size: 34, reveal: c.p(c.at(4, 0.2), c.at(4, 0.9)), draw: c.p(c.at(4, 0.0), c.at(4, 0.3)), r: 0.05 * Math.sin(Math.max(0, c.tq - c.at(4, 0.3)) * 6) * Math.exp(-Math.max(0, c.tq - c.at(4, 0.3)) * 1.4) });
  },
  sfx: c => [[c.turn + 0.1, 'scratch', { dur: 1.4, pan: -0.5 }], [c.turn + 0.6, 'scribble', { dur: 1.6 }], [c.turn + 0.6, 'clank', { pan: 0 }], [c.turn + 1.0, 'forge', { dur: 28 }],
    [c.at(1, -0.3), 'steps', { dur: 0.6, pan: -0.3 }], [c.at(1, 0.2), 'polish', { dur: 3.2, pan: -0.2 }], [c.at(1, 0.6), 'ting', { pan: -0.1 }], [c.at(1, 2.2), 'ting', { pan: 0.1 }],
    [c.at(2, 0.4), 'squeak', { dur: 2.8, pan: 0 }], [c.at(3, -0.6), 'steps', { dur: 1.0, pan: 0.6 }], [c.at(3, 0.6), 'hinge', { pan: 0.1 }], [c.at(3, 1.0), 'flutter', { pan: 0.3 }], [c.at(3, 2.7), 'clank', { pan: 0.1 }],
    [c.at(4, 0.0), 'tap', { pan: 0.5 }], [c.at(4, 0.2), 'write', { dur: 0.7, pan: 0.5 }], [c.at(4, 0.8), 'steps', { dur: 1.8, pan: 0.8 }]],
};
