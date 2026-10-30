// 07 · The Victorian Cover-Up (180–210 s). A parlour (the street outside its window); the gentleman admires himself in
// the mirror; the butler's pamphlet; the tiny scissors on a silver tray; the gentleman faints onto the sofa.
import { line, fill, handCircle, ellipse, smooth, xf } from '../crayon.js';
import { part } from '../rig.js';
import { K, person, say } from '../figs.js';
import { camOf, F, L, ground, box, clamp, lerp, wob } from './util.js';
import { scissors } from './ch02.js';
export default {
  cam: c => camOf(c, [[0, [720, 540, 1]], [c.at(1, -0.3), [720, 540, 1]], [c.at(1, 0.6), [520, 560, 1.35]], [c.at(2, -0.3), [520, 560, 1.35]], [c.at(2, 0.5), [720, 560, 1.08]], [c.at(3, 0.2), [720, 560, 1.08]], [c.at(3, 1.0), [880, 600, 1.45]], [c.at(4, -0.2), [880, 600, 1.45]], [c.at(4, 0.6), [640, 600, 1.15]], [30, [640, 600, 1.15]]]),
  draw(S, c) {
    const T = c.turn, d = c.p(T + 0.1, T + 1.4), f = c.p(T + 0.6, T + 2.2);
    // wallpaper stripes, skirting, floor rug
    fill(S.BG.f, [[-200, 0], [1640, 0], [1640, 860], [-200, 860]], F(K.pink, 1300, { draw: f, p: 0.25, gap: 16, ang: 1.57 }));
    for (let k = 0; k < 14; k++) line(S.BG.l, [[k * 110, 120], [k * 110, 860]], L(1301 + k, { w: 4, col: K.pink, p: 0.6, draw: d }));
    ground(S.BG, 860, K.brown, d, 1320); part(S.G2, ellipse(700, 960, 420, 50, 30), F(K.red, 1321, { draw: f, p: 0.7 }), L(1322, { draw: d }));
    // window onto the street: a gas lamp and the house opposite
    part(S.G2, [[980, 160], [1340, 160], [1340, 520], [980, 520]], F(K.sky, 1330, { draw: f, p: 0.35 }), L(1331, { draw: d, col: K.brown, w: 9 }));
    box(S.G2, 1030, 300, 160, 220, K.red, 1332, d, { p: 0.7 }); for (let k = 0; k < 2; k++) box(S.G2, 1050 + k * 80, 330, 40, 50, K.yellow, 1334 + k, d);
    line(S.G2.l, [[1270, 520], [1270, 260]], L(1337, { w: 6, draw: d })); part(S.G2, [[1250, 260], [1290, 260], [1300, 230], [1240, 230]], F(K.yellow, 1338, { draw: f }), L(1339, { draw: d, w: 4 }));
    line(S.G2.l, [[1160, 160], [1160, 520]], L(1340, { w: 6, col: K.brown, draw: d })); line(S.G2.l, [[980, 340], [1340, 340]], L(1341, { w: 6, col: K.brown, draw: d }));
    // the oval mirror (with his reflection in it) and the sofa
    part(S.G2, ellipse(260, 420, 120, 170, 36), F(K.sky, 1350, { draw: f, p: 0.25 }), L(1351, { draw: d, col: K.ochre, w: 10 }));
    part(S.G2, [[90, 860], [90, 690], [140, 650], [560, 650], [610, 690], [610, 860]], F(K.green, 1360, { draw: f }), L(1361, { draw: d }));
    part(S.G2, [[110, 780], [590, 780], [590, 860], [110, 860]], F(K.green, 1362, { draw: f, p: 0.95 }), L(1363, { draw: d }));
    // a side table with a teacup that rattles when he faints
    const rat = c.tq > c.at(4, 0.3) && c.tq < c.at(4, 1.4) ? 3 * wob(c, 11) : 0;
    box(S.G2, 680, 740, 120, 20, K.brown, 1370, d); line(S.G2.l, [[740, 760], [740, 860]], L(1371, { w: 7, col: K.brown, draw: d }));
    part(S.G, [[712 + rat, 706], [768 + rat, 706], [760 + rat, 738], [720 + rat, 738]], F(K.white, 1372, { draw: f }), L(1373, { draw: d, w: 4 })); part(S.G, ellipse(740 - rat, 742, 44, 6, 14), F(K.white, 1374, { draw: f }), L(1375, { draw: d, w: 3.5 }));
    // the gentleman
    const faint = c.p(c.at(4, 0.0), c.at(4, 0.5)), gd = c.p(T + 0.6, T + 1.9);
    if (faint <= 0) {
      const atMirror = c.tq < c.at(2, -0.1), gx = atMirror ? 470 : 540;
      if (atMirror && gd > 0.5) person(S.G2, 'gentleman', { x: 262, y: 520, s: 0.55, flip: true, view: 'q', seed: 1380, expr: 'smug', draw: 1 });   // the reflection
      person(S.G, 'gentleman', { x: gx, y: 880, s: 1.15, view: atMirror ? 'q' : c.tq < c.at(3) ? 'front' : 'q', flip: atMirror, draw: gd, fillDraw: c.p(T + 1.0, T + 2.4), seed: 1390,
        expr: atMirror ? 'smug' : c.tq > c.at(3, 0.6) ? 'shock' : c.tq > c.at(2, 0.6) ? 'eyebrow' : 'smug', armR: atMirror ? [70, -200] : c.tq > c.at(2, 0.6) && c.tq < c.at(3) ? [-30, -180] : [76, -110] });
    } else {   // fainted flat onto the sofa, top hat still on
      person(S.G, 'gentleman', { x: lerp(540, 150, faint), y: lerp(880, 740, faint), s: 1.15, r: 1.45 * faint, seed: 1390, expr: 'faint', armR: [80, -60], armL: [-60, -150] });
    }
    // the butler: pamphlet (beat 3), then the silver tray with tiny scissors (beat 4)
    if (c.tq > c.at(2, -0.6)) { const bd = c.p(c.at(2, -0.6), c.at(2, 0.2)), tray = c.tq > c.at(3, -0.2);
      person(S.G, 'butler', { x: 960, y: 880, s: 1.1, view: 'q', flip: true, seed: 1400, draw: bd, expr: c.tq > c.at(4, 0.3) ? 'worried' : 'neutral', armR: [100, -170],
        prop: (C, T_, h) => { const [x, y] = T_([[h[0], h[1]]])[0];
          if (!tray) { part(C, [[x - 70, y - 90], [x + 10, y - 94], [x + 12, y + 6], [x - 68, y + 10]], F(K.white, 1410, { p: 0.95 }), L(1411, { w: 4 })); say(C.l, 'A Delicate', x - 30, y - 54, { size: 18, seed: 1412 }); say(C.l, 'Matter', x - 30, y - 34, { size: 18, seed: 1413 });
            part(C, xf(smooth([[0, 0], [-10, -16], [0, -26], [10, -16]], 3), { x: x - 30, y: y - 6 }), F(K.green, 1414, { p: 1 }), L(1415, { w: 3, col: K.green })); }
          else { part(C, ellipse(x - 40, y - 4, 70, 12, 24), F(K.grey, 1416, { p: 0.95 }), L(1417, { w: 4 })); line(C.l, ellipse(x - 50, y - 12, 30, 5, 12), L(1418, { w: 3, col: K.white, p: 1 }));
            scissors(C, pts => pts.map(([a, b]) => [a, b]), [x - 44, y - 14]); } } }); }
  },
  sfx: c => [[c.turn + 0.1, 'scratch', { dur: 1.3, pan: -0.3 }], [c.turn + 0.6, 'scribble', { dur: 1.6 }], [c.turn + 0.3, 'clock', { dur: 29 }], [c.at(1, 0.4), 'ting', { pan: -0.5 }],
    [c.at(2, -0.6), 'steps', { dur: 0.8, pan: 0.5 }], [c.at(2, 0.2), 'paper', { pan: 0.4 }], [c.at(2, 0.8), 'harrumph', { pan: -0.2 }], [c.at(3, -0.2), 'tray', { pan: 0.4 }],
    [c.at(4, 0.0), 'swoon', { pan: -0.3 }], [c.at(4, 0.45), 'sofa', { pan: -0.4 }], [c.at(4, 0.4), 'teacup', { pan: 0.1 }]],
};
