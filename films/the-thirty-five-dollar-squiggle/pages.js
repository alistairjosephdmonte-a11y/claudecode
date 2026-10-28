// The pages of the book. Each page: cam(c) → [x, y, zoom], draw(S, c) → layers, sfx(c) → [[t, type, opts]].
// c.t is local page time; c.at(i) / c.end(i) are the start / end of the page's i-th narrated line; c.p(a, b) is progress.
// Every page draws itself on live (line first, then colour), stepping at 12 fps like the rest of the style.
import { line, fill, dab, ellipse, handCircle, xf, smooth, CAM, W, H } from './crayon.js';
import { part, tube, curve, erase } from './rig.js';
import { star } from './chars.js';
import { PAL } from './pal.js';
import { clamp, lerp, hash, track, mulberry } from '/core/lib.js';
import { K, say, person, shoe, shoeSide, tick, tickPts, box, card, sprout, clock, pine, bubble } from './figs.js';

const T0 = c => c.turn + 0.15;
const camOf = (c, keys) => { const k = keys.filter((q, i) => i === 0 || q[0] > keys[i - 1][0] + 0.05); return k.length > 1 ? track(k)(c.t) : k[0][1]; };
const title = (L, s, x, y, c, a, d = 1.2, o = {}) => say(L, s, x, y, { size: 110, font: 'Gaegu', weight: 700, reveal: c.p(a, a + d), seed: 40 + x % 97, p: 0.95, stroke: 2, ...o });
const hills = (L, y, dr, sd) => { const P = []; for (let x = -80; x <= 2000; x += 60) P.push([x, y + 26 * Math.sin(x * 0.004 + sd) + 10 * hash(x + sd)]); fill(L.f, [...P, [2000, y + 400], [-80, y + 400]], { col: K.green, p: 0.6, gap: 12, w: 13, ang: 1.25, seed: sd, draw: dr }); line(L.l, P, { w: 6, col: K.green, seed: sd + 1, draw: dr }); };
// cross-out: a few hard red strokes
const crossOut = (L, x0, y0, x1, y1, dr, sd) => { for (let k = 0; k < 3; k++) line(L, [[x0, y0 + k * 10 + 6 * hash(sd + k)], [x1, y1 + k * 10 - 6 * hash(sd + k + 3)]], { w: 9, col: K.red, p: 0.95, seed: sd + k, draw: clamp(dr * 3 - k) }); };
const sparkle = (L, x, y, r, sd, a = 1) => { line(L, [[x - r, y], [x + r, y]], { w: 4, col: K.orange, p: a, seed: sd }); line(L, [[x, y - r], [x, y + r]], { w: 4, col: K.orange, p: a, seed: sd + 1 }); };

// ————————————————————————————————— 1. title —————————————————————————————————
const titlePage = {
  cam: c => [960, 540 - 10 * c.p(0, c.dur), 1 + 0.035 * c.p(0, c.dur)],
  draw(S, c) {
    const t0 = 0.4;
    title(S.BG.l, 'The Thirty-Five', 960, 230, c, t0, 1.3, { size: 140 });
    title(S.BG.l, 'Dollar Squiggle', 960, 380, c, t0 + 1.35, 1.3, { size: 140 });
    say(S.BG.l, 'a true story, in crayon', 960, 470, { size: 54, reveal: c.p(t0 + 2.7, t0 + 3.4), seed: 9 });
    tick(S.FX, 960, 620, 1.5, { w: 22, draw: c.p(c.at(1, 0.4), c.at(1, 1.6)), seed: 71 });
    if (c.t > c.at(2)) {
      const d = c.p(c.at(2), c.at(2, 1.2));
      hills(S.BG, 800, d, 13);
      [[260, 820, 0.9], [420, 790, 0.7], [1580, 800, 0.8], [1720, 830, 1.0]].forEach(([x, y, s], i) => pine(S.G2, x, y, s, 120 + i * 9, d));
      const u = c.p(c.at(2, 0.8), c.dur), q = Math.floor(c.t * 12) / 12;
      [0, 1].forEach(i => person(S.G, { x: lerp(-120 - 120 * i, 2050 - 120 * i, u), y: 835, s: 0.36, pose: 'run', ph: q * 1.6 + i * 0.4, shirt: i ? K.orange : K.sky, pants: K.ink, hair: K.brown, hairStyle: i ? 'short' : 'cap', capCol: K.red, seed: 600 + i * 90 }));
    }
  },
  sfx: c => [[0.4, 'write', { dur: 2.6 }], [3.1, 'write', { dur: 0.7 }], [c.at(1, 0.4), 'scratch', { dur: 1.2, pan: 0 }], [c.at(2), 'scribble', { dur: 1.3, pan: -0.3 }], [c.at(2, 0.9), 'patter', { dur: c.dur - c.at(2, 0.9) }]],
};

// ————————————————————————————————— 2. Blue Ribbon Sports, 1964 —————————————————————————————————
const brs = {
  cam: c => camOf(c, [[0, [960, 540, 1]], [c.at(4, -0.4), [960, 540, 1]], [c.at(4, 0.4), [1460, 640, 1.55]], [c.at(5, -0.5), [1460, 640, 1.55]], [c.at(5, 0.5), [960, 1270, 1]], [c.dur, [960, 1290, 1.03]]]),
  draw(S, c) {
    const a = T0(c);
    title(S.BG.l, '1964', 190, 150, c, a, 0.8);
    const d1 = c.p(a + 0.3, a + 1.5), f1 = c.p(a + 1.0, a + 2.4);
    person(S.G, { x: 560, y: 820, s: 1.12, shirt: K.sky, pants: K.ink, hair: K.brown, hairStyle: 'cap', capCol: K.red, seed: 700, draw: d1, fillDraw: f1,
      armR: [[70, -196], [86, -250]], prop: (C, T, h) => { if (d1 >= 1) { part(C, T(handCircle(h[0], h[1] - 20, 22, 710, 0, 20)), { col: K.white, p: 0.9, gap: 5, w: 7, seed: 711 }, { w: 5, seed: 712 }); line(C.l, T([[h[0], h[1] - 20], [h[0] + 10, h[1] - 32]]), { w: 4, seed: 713 }); } } });
    if (c.t > c.at(1)) { const d2 = c.p(c.at(1), c.at(1, 1.2)), f2 = c.p(c.at(1, 0.6), c.at(1, 1.8)); person(S.G, { x: 860, y: 820, s: 1.0, shirt: K.orange, pants: K.sky, hair: K.brown, hairStyle: 'short', seed: 760, draw: d2, fillDraw: f2, armL: [[-40, -180], [-60, -230]] }); }
    if (c.t > c.at(2)) {   // the blue ribbon rosette and the name
      const d = c.p(c.at(2, 0.2), c.at(2, 1.2));
      for (let i = 0; i < 12; i++) { const b = i / 12 * Math.PI * 2; part(S.G2, handCircle(1340 + Math.cos(b) * 62, 250 + Math.sin(b) * 62, 30, 800 + i, 0, 14), { col: K.sky, p: 0.85, gap: 6, w: 8, seed: 820 + i, draw: d }, { w: 4, seed: 840 + i, draw: d }); }
      part(S.G2, handCircle(1340, 250, 58, 860, 0.05, 30), { col: K.yellow, p: 0.9, gap: 6, w: 8, seed: 861, draw: d }, { w: 5, seed: 862, draw: d });
      part(S.G2, [[1300, 300], [1330, 300], [1310, 420], [1290, 400], [1270, 420]], { col: K.sky, p: 0.9, gap: 6, w: 8, seed: 863, draw: d }, { w: 4.5, seed: 864, draw: d });
      part(S.G2, [[1352, 300], [1382, 300], [1412, 420], [1390, 400], [1372, 420]], { col: K.sky, p: 0.9, gap: 6, w: 8, seed: 865, draw: d }, { w: 4.5, seed: 866, draw: d });
      say(S.BG.l, 'Blue Ribbon Sports', 1450, 500, { size: 76, font: 'Gaegu', weight: 700, reveal: c.p(c.at(2, 0.9), c.at(2, 2.2)), seed: 41, p: 0.95, stroke: 1.5 });
    }
    if (c.t > c.at(3)) {   // a little boat of shoeboxes, sailing in from Japan
      const d = c.p(c.at(3), c.at(3, 1.0)), bx = lerp(1720, 1420, c.p(c.at(3), c.at(4, 1.5)));
      const wv = []; for (let x = 1080; x <= 1900; x += 40) wv.push([x, 790 + 10 * Math.sin(x * 0.03 + Math.floor(c.t * 12) * 0.5)]);
      line(S.BG.l, wv, { w: 6, col: K.sky, seed: 870, draw: d });
      fill(S.BG.f, [...wv, [1900, 860], [1080, 860]], { col: K.sky, p: 0.5, gap: 10, w: 11, seed: 871, draw: d });
      const bob = 5 * Math.sin(Math.floor(c.t * 12) * 0.45);
      part(S.G, [[bx - 170, 740 + bob], [bx + 170, 740 + bob], [bx + 120, 800 + bob], [bx - 130, 800 + bob]], { col: K.brown, p: 0.8, gap: 7, w: 9, seed: 872, draw: d }, { w: 5, seed: 873, draw: d });
      [[-120, 0], [-30, 0], [60, 0], [-80, -66], [10, -66]].forEach(([dx, dy], i) => { box(S.G, bx + dx, 740 + bob + dy, 84, 52, [K.ochre, K.orange, K.ochre, K.orange, K.ochre][i], 880 + i * 7, d); if (c.t > c.at(4)) line(S.G.l, [[bx + dx + 20, 712 + bob + dy], [bx + dx + 40, 700 + bob + dy], [bx + dx + 62, 716 + bob + dy]], { w: 4, col: K.violet, p: 0.9, seed: 920 + i, draw: c.p(c.at(4, 0.2 + i * 0.15), c.at(4, 0.5 + i * 0.15)) }); });
      say(S.BG.l, 'from Japan', 1520, 640, { size: 56, reveal: c.p(c.at(3, 0.8), c.at(3, 1.6)), seed: 42 });
    }
    if (c.t > c.at(5, -0.6)) {   // below the fold: an empty shoe, waiting for a mark
      const d = c.p(c.at(5, -0.2), c.at(5, 1.2));
      shoe(S.G, 960, 1430, 1.5, { draw: d, fillDraw: c.p(c.at(5, 0.8), c.at(5, 2)), col: K.white, seed: 940 });
      say(S.BG.l, 'our own shoes', 960, 1110, { size: 66, font: 'Gaegu', weight: 700, reveal: c.p(c.at(5, 0.3), c.at(5, 1.3)), seed: 43 });
      if (c.t > c.at(6)) { line(S.FX, handCircle(950, 1350, 120, 950, 0.1, 40).map(([x, y]) => [x, y * 0.6 + 1350 * 0.4]), { w: 6, col: K.orange, p: 0.9, seed: 951, draw: c.p(c.at(6, 0.4), c.at(6, 1.4)) }); say(S.FX, '?', 950, 1380, { size: 110, font: 'Gaegu', weight: 700, col: K.orange, reveal: c.p(c.at(6, 1.4), c.at(6, 1.7)), seed: 44 }); }
    }
  },
  sfx: c => [[c.turn + 0.15, 'write', { dur: 0.8, pan: -0.7 }], [c.turn + 0.5, 'scratch', { dur: 1.2, pan: -0.3 }], [c.turn + 1.1, 'scribble', { dur: 1.3, pan: -0.3 }], [c.at(1), 'scribble', { dur: 1.6, pan: 0 }], [c.at(2, 0.2), 'scribble', { dur: 1.0, pan: 0.4 }], [c.at(2, 0.9), 'write', { dur: 1.3, pan: 0.5 }], [c.at(3), 'waves', { dur: c.at(5) - c.at(3) }], [c.at(5, -0.2), 'scratch', { dur: 1.4 }], [c.at(6, 0.4), 'scratch', { dur: 1.0, pan: 0 }]],
};

// ————————————————————————————————— 3. Portland State —————————————————————————————————
const campus = {
  cam: c => camOf(c, [[0, [960, 540, 1]], [c.at(3, -0.4), [960, 540, 1]], [c.at(3, 0.5), [1180, 360, 1.3]], [c.dur, [1190, 360, 1.33]]]),
  draw(S, c) {
    const a = T0(c), d = c.p(a, a + 1.4), f = c.p(a + 0.8, a + 2.4);
    // the university building, a little Greek-temple doorway
    part(S.G2, [[110, 330], [610, 330], [610, 850], [110, 850]], { col: K.ochre, p: 0.6, gap: 9, w: 10, seed: 1000, draw: f }, { w: 6, seed: 1001, draw: d });
    part(S.G2, [[80, 330], [360, 190], [640, 330]], { col: K.red, p: 0.75, gap: 8, w: 10, seed: 1002, draw: f }, { w: 6, seed: 1003, draw: d });
    [170, 290, 430, 550].forEach((x, i) => part(S.G2, [[x - 22, 390], [x + 22, 390], [x + 22, 850], [x - 22, 850]], { col: K.white, p: 0.9, gap: 6, w: 8, seed: 1010 + i, draw: f }, { w: 5, seed: 1020 + i, draw: d }));
    say(S.BG.l, 'Portland State', 360, 300, { size: 46, font: 'Gaegu', weight: 700, reveal: c.p(a + 1.2, a + 2.2), seed: 45 });
    // the chalkboard
    part(S.G2, [[800, 150], [1700, 150], [1700, 560], [800, 560]], { col: K.ink, p: 0.92, gap: 6, w: 9, ang: 0.15, seed: 1030, draw: f }, { w: 9, col: K.brown, seed: 1031, draw: d });
    say(S.FX, 'Accounting 101', 1250, 250, { size: 70, col: K.white, reveal: c.p(c.at(0, 0.3), c.at(0, 1.6)), seed: 46, p: 0.9 });
    say(S.FX, 'debits = credits', 1180, 340, { size: 52, col: K.white, reveal: c.p(c.at(0, 1.2), c.at(0, 2.4)), seed: 47, p: 0.8 });
    // the teacher, pointing at the board
    person(S.G, { x: 760, y: 840, s: 1.0, shirt: K.white, pants: K.brown, hair: K.brown, hairStyle: 'short', seed: 1100, draw: c.p(a + 0.4, a + 1.6), fillDraw: c.p(a + 1.0, a + 2.4),
      armR: [[66, -230], [118, -296]], prop: (C, T, h) => line(C.l, T([[h[0], h[1]], [h[0] + 70, h[1] - 80]]), { w: 5, col: K.brown, seed: 1110 }) });
    // the student, with her sketchbook
    if (c.t > c.at(1)) {
      person(S.G, { x: 1420, y: 840, s: 0.98, shirt: K.pink, pants: K.sky, hair: K.brown, hairStyle: 'long', seed: 1200, flip: true, draw: c.p(c.at(1), c.at(1, 1.2)), fillDraw: c.p(c.at(1, 0.6), c.at(1, 1.8)),
        armR: [[40, -170], [62, -196]], prop: (C, T, h) => part(C, T([[h[0] - 10, h[1] - 50], [h[0] + 70, h[1] - 60], [h[0] + 76, h[1] + 30], [h[0] - 4, h[1] + 36]]), { col: K.yellow, p: 0.8, gap: 6, w: 8, seed: 1210 }, { w: 5, seed: 1211 }) });
    }
    if (c.t > c.at(2)) {   // charts and pictures, pinned up
      const dd = c.p(c.at(2), c.at(2, 1.0));
      card(S.G2, 1780, 760, 200, 160, 0.06, 1300, { draw: dd, col: K.white, p: 0.8 });
      [[1710, 30], [1750, 70], [1790, 50], [1830, 100]].forEach(([x, h], i) => part(S.G2, [[x - 14, 820 - h], [x + 14, 820 - h], [x + 14, 820], [x - 14, 820]], { col: [K.sky, K.orange, K.green, K.red][i], p: 0.9, gap: 4, w: 6, seed: 1310 + i, draw: dd }, { w: 3.5, seed: 1320 + i, draw: dd }));
    }
    if (c.t > c.at(3)) { say(S.FX, '$2 an hour', 1260, 470, { size: 92, font: 'Gaegu', weight: 700, col: K.yellow, reveal: c.p(c.at(3, 0.1), c.at(3, 1.0)), seed: 49, p: 0.95, stroke: 2 }); line(S.FX, [[1060, 495], [1470, 490]], { w: 7, col: K.yellow, seed: 1330, draw: c.p(c.at(3, 1.0), c.at(3, 1.5)) }); }
  },
  sfx: c => [[c.turn + 0.15, 'scratch', { dur: 1.4, pan: -0.5 }], [c.turn + 0.9, 'scribble', { dur: 1.6, pan: -0.2 }], [c.at(0, 0.3), 'chalk', { dur: 2.1, pan: 0.3 }], [c.at(1), 'scribble', { dur: 1.7, pan: 0.5 }], [c.at(2), 'scribble', { dur: 1.0, pan: 0.8 }], [c.at(3, 0.1), 'chalk', { dur: 1.3, pan: 0.3 }], [c.at(3, 0.2), 'coin', {}]],
};

// ————————————————————————————————— 4. the brief, 1971 —————————————————————————————————
const brief = {
  cam: c => camOf(c, [[0, [960, 540, 1]], [c.at(4, -0.5), [960, 540, 1]], [c.at(4, 0.4), [960, 1280, 1]], [c.dur, [960, 1290, 1.04]]]),
  draw(S, c) {
    const a = T0(c);
    card(S.G2, 640, 470, 760, 640, -0.02, 1400, { draw: c.p(a, a + 0.8), col: K.white, p: 0.85, pin: K.red });
    title(S.BG.l, 'THE BRIEF', 640, 250, c, a + 0.6, 0.9, { size: 84 }); say(S.BG.l, '1971', 640, 320, { size: 52, reveal: c.p(a + 1.4, a + 1.8), seed: 50 });
    if (c.t > c.at(1)) say(S.G.l, '★ a mark for the side of the shoe', 640, 420, { size: 44, reveal: c.p(c.at(1), c.at(1, 1.6)), seed: 51 });
    if (c.t > c.at(2)) {
      say(S.G.l, '1. show MOTION', 590, 530, { size: 62, font: 'Gaegu', weight: 700, reveal: c.p(c.at(2), c.at(2, 0.9)), seed: 52 });
      const q = Math.floor(c.t * 12) / 12, d = c.p(c.at(2, 0.1), c.at(2, 1.0));
      person(S.G, { x: 1450, y: 820, s: 0.95, pose: 'run', ph: q * 1.4, shirt: K.green, pants: K.ink, hairStyle: 'short', seed: 1500, draw: d, fillDraw: d });
      [0, 1, 2, 3].forEach(i => line(S.FX, [[1340 - 30 * i, 600 + i * 50], [1180 - 50 * i, 600 + i * 50]], { w: 6, col: K.sky, p: 0.9, seed: 1510 + i, draw: c.p(c.at(2, 0.4 + 0.12 * i), c.at(2, 0.8 + 0.12 * i)) }));
    }
    if (c.t > c.at(3)) {
      say(S.G.l, '2. NOT three stripes', 610, 640, { size: 62, font: 'Gaegu', weight: 700, reveal: c.p(c.at(3), c.at(3, 1.0)), seed: 53 });
      [0, 1, 2].forEach(i => line(S.FX, [[1400 + i * 50, 340], [1460 + i * 50, 160]], { w: 16, col: K.violet, p: 0.9, seed: 1520 + i, draw: c.p(c.at(3, 1.0 + 0.2 * i), c.at(3, 1.3 + 0.2 * i)) }));
      crossOut(S.FX, 1360, 180, 1650, 330, c.p(c.at(3, 2.0), c.at(3, 2.6)), 1530);
      crossOut(S.FX, 1360, 330, 1650, 170, c.p(c.at(3, 2.4), c.at(3, 3.0)), 1540);
    }
    if (c.t > c.at(4, -0.6)) {   // a shoe, asleep in its box
      const d = c.p(c.at(4, -0.3), c.at(4, 0.9));
      box(S.G2, 640, 1500, 640, 200, K.orange, 1550, d);
      shoe(S.G, 960, 1360, 1.05, { draw: d, col: K.white, seed: 1560 });
      ['z', 'z', 'Z'].forEach((z, i) => say(S.FX, z, 1260 + i * 60, 1220 - i * 60, { size: 60 + i * 20, font: 'Gaegu', weight: 700, reveal: c.p(c.at(4, 1.2 + i * 0.4), c.at(4, 1.4 + i * 0.4)), seed: 54 + i }));
    }
  },
  sfx: c => [[c.turn + 0.15, 'paper', {}], [c.turn + 0.75, 'write', { dur: 1.2, pan: -0.3 }], [c.at(1), 'write', { dur: 1.6, pan: -0.3 }], [c.at(2), 'write', { dur: 0.9, pan: -0.3 }], [c.at(2, 0.3), 'whoosh', { pan: 0.4 }], [c.at(2, 0.4), 'patter', { dur: c.at(4) - c.at(2) - 0.4 }], [c.at(3), 'write', { dur: 1.0, pan: -0.3 }], [c.at(3, 1.0), 'scratch', { dur: 0.6, pan: 0.6 }], [c.at(3, 2.0), 'scratch', { dur: 1.0, pan: 0.6 }], [c.at(4, -0.3), 'scribble', { dur: 1.2 }], [c.at(4, 1.2), 'snore', {}]],
};

// ————————————————————————————————— 5. tissue paper —————————————————————————————————
const CURVES = [
  (x, y) => curve([[x - 120, y], [x - 40, y - 60], [x + 40, y + 40], [x + 120, y - 20]], 8),
  (x, y) => [[x - 140, y + 10], [x + 140, y - 40]],
  (x, y) => tickPts(x, y, 0.95),
  (x, y) => [[x - 130, y], [x - 70, y - 50], [x - 10, y + 10], [x + 50, y - 50], [x + 120, y]],
  (x, y) => curve([[x - 120, y + 20], [x - 60, y - 70], [x + 60, y - 70], [x + 120, y + 20]], 8),
  (x, y) => curve([[x - 120, y - 40], [x, y + 40], [x + 120, y - 40]], 8),
  (x, y) => tickPts(x + 10, y + 6, 0.85, 14),
  (x, y) => curve([[x - 130, y + 30], [x - 60, y - 20], [x + 30, y + 20], [x + 130, y - 50]], 8),
  (x, y) => tickPts(x, y, 1.0, -8),
];
const tissue = {
  cam: c => camOf(c, [[0, [960, 520, 1]], [c.at(2, -0.2), [960, 520, 1.12]], [c.dur, [960, 530, 1.2]]]),
  draw(S, c) {
    const a = T0(c);
    shoe(S.G2, 960, 640, 1.9, { draw: c.p(a, a + 1.6), seed: 1600 });
    // tissue sheets: pale and see-through (no knock-out), each with one try at a curve
    const times = [c.at(0, 1.8), c.at(1, 0.1), c.at(1, 1.2)]; for (let k = 0; k < 6; k++) times.push(c.at(2, 0.1 + k * 0.42));
    times.forEach((ts, k) => {
      if (c.t < ts) return;
      const R = mulberry(1700 + k * 13), x = 960 + (R() - 0.5) * 120, y = 500 + (R() - 0.5) * 80, r = (R() - 0.5) * 0.12;
      const slide = clamp((c.t - ts) / 0.25), dy = (1 - slide) * -260;
      const P = xf([[-430, -300], [430, -292], [424, 290], [-426, 296]], { x, y: y + dy, r });
      fill(S.G.f, P, { col: K.white, p: 0.2, gap: 11, w: 12, ang: 0.4 + R(), seed: 1710 + k });
      line(S.G.l, [...P, P[0]], { w: 3, col: K.sky, p: 0.45, seed: 1720 + k });
      line(S.G.l, CURVES[k](x - 30, 600 + dy * 0.9), { w: k === 8 ? 16 : 10, col: k === 8 ? K.orange : K.ink, p: k === 8 ? 0.95 : 0.6, seed: 1730 + k, draw: clamp((c.t - ts - 0.25) / 0.45), taper: 0.4 });
    });
    if (c.t > c.at(2, 0.6)) for (let k = 0; k < 5; k++) {   // crumpled tries piling up on the floor
      const tk = c.at(2, 0.6 + k * 0.45); if (c.t < tk) continue;
      const x = 300 + k * 330 + 60 * hash(k), y = 840 + 20 * hash(k + 9), drop = clamp((c.t - tk) / 0.2);
      const P = handCircle(x, lerp(700, y, drop), 42, 1800 + k, 0.25, 18);
      part(S.G2, P, { col: K.white, p: 0.9, gap: 5, w: 7, seed: 1810 + k }, { w: 4.5, seed: 1820 + k });
      [[[x - 24, y - 12], [x + 4, y + 10], [x + 22, y - 16]], [[x - 30, y + 14], [x - 8, y - 4], [x + 6, y + 24]], [[x + 8, y - 30], [x + 18, y - 6], [x + 34, y + 4]]].forEach((q, j) => line(S.G2.l, q, { w: 3.5, p: 0.6, seed: 1830 + k * 3 + j }));
    }
  },
  sfx: c => {
    const o = [[c.turn + 0.15, 'scratch', { dur: 1.6 }], [c.at(0, 1.8), 'tissue', {}], [c.at(0, 2.1), 'scratch', { dur: 0.5 }], [c.at(1, 0.1), 'tissue', {}], [c.at(1, 0.35), 'scratch', { dur: 0.4 }], [c.at(1, 1.2), 'tissue', {}], [c.at(1, 1.45), 'scratch', { dur: 0.45 }]];
    for (let k = 0; k < 6; k++) { o.push([c.at(2, 0.1 + k * 0.42), 'tissue', { v: 0.7 }]); o.push([c.at(2, 0.35 + k * 0.42), 'scratch', { dur: 0.35, pan: -0.2 + k * 0.08 }]); }
    for (let k = 0; k < 5; k++) o.push([c.at(2, 0.6 + k * 0.45), 'crumple', { pan: -0.7 + k * 0.35 }]);
    return o;
  },
};

// ————————————————————————————————— 6. the pitch —————————————————————————————————
const MARKS = [
  (L, x, y, o) => line(L, handCircle(x, y, 50, 1901, 0.1, 30), o),
  (L, x, y, o) => line(L, [[x - 80, y + 20], [x - 40, y - 30], [x, y + 20], [x + 40, y - 30], [x + 80, y + 20]], o),
  (L, x, y, o) => { line(L, [[x - 80, y + 10], [x + 60, y - 10]], o); line(L, [[x + 30, y - 40], [x + 70, y - 12], [x + 36, y + 22]], o); },
  (L, x, y, o) => { line(L, curve([[x - 80, y + 30], [x - 20, y - 40], [x + 80, y - 50]], 8), o); line(L, curve([[x - 60, y + 40], [x, y - 10], [x + 80, y - 20]], 8), o); },
  (L, x, y, o) => line(L, curve([[x - 90, y], [x - 45, y - 40], [x, y], [x + 45, y + 40], [x + 90, y]], 8), o),
  (L, x, y, o) => line(L, tickPts(x, y + 6, 0.62), { ...o, col: K.orange, w: 13, taper: 0.5 }),
];
const pitch = {
  cam: c => camOf(c, [[0, [960, 520, 1]], [c.at(1, 0.3), [960, 520, 1]], [c.at(1, 1.0), [1400, 560, 1.35]], [c.at(2, -0.5), [1400, 560, 1.35]], [c.at(2, 0.4), [960, 1280, 1]], [c.dur, [980, 1280, 1.05]]]),
  draw(S, c) {
    const a = T0(c);
    say(S.BG.l, 'six designs', 960, 120, { size: 70, font: 'Gaegu', weight: 700, reveal: c.p(c.at(0, 0.6), c.at(0, 1.4)), seed: 60 });
    [[520, 290], [960, 290], [1400, 290], [520, 600], [960, 600], [1400, 600]].forEach(([x, y], i) => {
      const ts = c.at(0, 0.2 + i * 0.45); if (c.t < ts) return;
      card(S.G2, x, y, 320, 240, (hash(i + 3) - 0.5) * 0.08, 1900 + i * 7, { col: K.white, p: 0.85, pin: [K.red, K.sky, K.green, K.yellow, K.violet, K.red][i], draw: clamp((c.t - ts) / 0.3) });
      MARKS[i](S.G.l, x, y + 10, { w: 9, col: K.ink, p: 0.9, seed: 1950 + i, draw: clamp((c.t - ts - 0.3) / 0.4) });
    });
    if (c.t > c.at(1, 0.6)) line(S.FX, handCircle(1400, 600, 200, 1990, 0.18, 50).map(([x, y]) => [x, 600 + (y - 600) * 0.75]), { w: 9, col: K.red, p: 0.95, seed: 1991, draw: c.p(c.at(1, 0.6), c.at(1, 1.5)) });
    if (c.t > c.at(2, -0.6)) {   // below: the boss, and what he said
      const d = c.p(c.at(2, -0.3), c.at(2, 0.9));
      person(S.G, { x: 520, y: 1560, s: 1.15, shirt: K.white, pants: K.brown, hair: K.brown, hairStyle: 'short', seed: 2000, draw: d, fillDraw: c.p(c.at(2, 0.2), c.at(2, 1.4)), mouth: c.t > c.at(3) && c.t < c.end(4) && Math.floor(c.t * 6) % 2 ? 'o' : undefined,
        armR: [[52, -200], [40, -250]], armL: [[-40, -190], [-20, -216]] });
      if (c.t > c.at(2, 0.5)) { const q = c.p(c.at(2, 0.5), c.at(2, 0.9)); say(S.FX, '?', 700, 1150, { size: 120, font: 'Gaegu', weight: 700, col: K.violet, reveal: q, seed: 61 }); }
      if (c.t > c.at(3, -0.2)) {
        bubble(S.G2, 1180, 1200, 860, 300, 2010, { tail: [700, 1360], draw: c.p(c.at(3, -0.2), c.at(3, 0.3)) });
        say(S.G.l, '"I don\'t love it..."', 1180, 1170, { size: 70, font: 'Gaegu', weight: 700, reveal: c.p(c.at(3, 0.1), c.at(3, 1.1)), seed: 62 });
        if (c.t > c.at(4)) say(S.G.l, '"...but maybe it will grow on me."', 1180, 1260, { size: 54, reveal: c.p(c.at(4), c.at(4, 1.4)), seed: 63 });
      }
      if (c.t > c.at(4)) { // the chosen curve, on a card in a pot, starting to sprout
        card(S.G2, 1480, 1500, 220, 150, 0.05, 2020, { col: K.white, p: 0.85 });
        line(S.G.l, tickPts(1480, 1505, 0.5), { w: 10, col: K.orange, p: 0.95, seed: 2021, taper: 0.5 });
        sprout(S.G, 1700, 1600, 1.0, c.p(c.at(4, 0.8), c.at(4, 2.4)), 2030);
      }
    }
  },
  sfx: c => {
    const o = [[c.at(0, 0.6), 'write', { dur: 0.8 }]];
    for (let i = 0; i < 6; i++) { o.push([c.at(0, 0.2 + i * 0.45), 'pin', { pan: [-0.5, 0, 0.5][i % 3] }]); o.push([c.at(0, 0.5 + i * 0.45), 'scratch', { dur: 0.4, pan: [-0.5, 0, 0.5][i % 3] }]); }
    o.push([c.at(1, 0.6), 'scratch', { dur: 0.9, pan: 0.5 }], [c.at(2, -0.3), 'scribble', { dur: 1.4, pan: -0.4 }], [c.at(3, -0.2), 'scratch', { dur: 0.5 }], [c.at(3, 0.1), 'write', { dur: 1.0 }], [c.at(4), 'write', { dur: 1.4 }], [c.at(4, 0.8), 'grow', {}]);
    return o;
  },
};

// ————————————————————————————————— 7. the invoice —————————————————————————————————
const invoice = {
  cam: c => camOf(c, [[0, [960, 520, 1]], [c.at(2, -0.3), [960, 520, 1]], [c.at(2, 0.5), [960, 640, 1.4]], [c.at(3, -0.4), [960, 640, 1.4]], [c.at(3, 0.4), [960, 560, 1.05]]]),
  draw(S, c) {
    const a = T0(c);
    card(S.G2, 960, 470, 900, 760, 0.01, 2100, { draw: c.p(a, a + 0.7), col: K.white, p: 0.85 });
    title(S.G.l, 'INVOICE', 960, 200, c, c.at(0, 0.2), 0.9, { size: 92 });
    say(S.G.l, 'from: Carolyn Davidson, design', 960, 270, { size: 42, reveal: c.p(c.at(0, 0.9), c.at(0, 1.8)), seed: 64 });
    if (c.t > c.at(1)) {
      say(S.G.l, '17 1/2 hours', 720, 400, { size: 72, font: 'Gaegu', weight: 700, reveal: c.p(c.at(1), c.at(1, 1.0)), seed: 65, align: 'left' });
      say(S.G.l, '× $2 an hour', 720, 500, { size: 72, font: 'Gaegu', weight: 700, reveal: c.p(c.at(1, 1.3), c.at(1, 2.3)), seed: 66, align: 'left' });
      line(S.G.l, [[700, 540], [1300, 534]], { w: 6, seed: 2110, draw: c.p(c.at(1, 2.4), c.at(1, 2.8)) });
    }
    if (c.t > c.at(2)) { say(S.FX, '= $35', 960, 680, { size: 170, font: 'Gaegu', weight: 700, col: K.orange, reveal: c.p(c.at(2), c.at(2, 0.6)), seed: 67, p: 0.95, stroke: 3 }); line(S.FX, handCircle(960, 630, 190, 2120, 0.15, 44).map(([x, y]) => [x, 630 + (y - 630) * 0.55]), { w: 7, col: K.orange, p: 0.9, seed: 2121, draw: c.p(c.at(2, 0.7), c.at(2, 1.4)) }); }
    // a clock in the margin; its hands race through the hours
    const spin = 6.283 * (17.5 * c.p(c.at(1), c.at(1, 2.8)) + 4 * c.p(c.at(3, 0.3), c.at(3, 2.6)));
    clock(S.G, 300, 420, 120, Math.floor(spin * 2) / 2, 2130, c.p(a + 0.3, a + 1.2));
    if (c.t > c.at(3)) { say(S.G.l, '(she really worked longer)', 960, 800, { size: 46, reveal: c.p(c.at(3, 0.3), c.at(3, 1.6)), seed: 68 }); say(S.FX, '+', 460, 300, { size: 110, font: 'Gaegu', weight: 700, col: K.red, reveal: c.p(c.at(3, 0.5), c.at(3, 0.7)), seed: 69 }); }
  },
  sfx: c => [[c.turn + 0.15, 'paper', {}], [c.turn + 0.45, 'scratch', { dur: 0.9, pan: -0.7 }], [c.at(0, 0.2), 'write', { dur: 0.9 }], [c.at(0, 0.9), 'write', { dur: 0.9 }], [c.at(1), 'write', { dur: 1.0, pan: -0.2 }], [c.at(1), 'ticking', { dur: 2.8, pan: -0.7 }], [c.at(1, 1.3), 'write', { dur: 1.0, pan: -0.2 }], [c.at(2), 'write', { dur: 0.6 }], [c.at(2, 0.6), 'ding', {}], [c.at(3, 0.3), 'write', { dur: 1.3 }], [c.at(3, 0.3), 'ticking', { dur: 2.3, pan: -0.7 }]],
};

// ————————————————————————————————— 8. the name —————————————————————————————————
const name = {
  cam: c => camOf(c, [[0, [960, 540, 1]], [c.at(2, -0.3), [960, 540, 1]], [c.at(3, 0.2), [1300, 470, 1.25]], [c.dur, [1310, 470, 1.28]]]),
  draw(S, c) {
    const a = T0(c);
    card(S.G2, 440, 360, 600, 420, -0.04, 2200, { draw: c.p(a, a + 0.6), col: K.yellow, p: 0.4, pin: K.sky });
    say(S.G.l, 'names?', 440, 230, { size: 56, reveal: c.p(a + 0.4, a + 1.0), seed: 70 });
    say(S.G.l, 'Dimension Six', 440, 380, { size: 84, font: 'Gaegu', weight: 700, reveal: c.p(c.at(0, 1.6), c.at(0, 2.6)), seed: 71 });
    if (c.t > c.at(1)) crossOut(S.FX, 210, 340, 680, 380, c.p(c.at(1, 0.1), c.at(1, 0.9)), 2210);
    if (c.t > c.at(2)) {   // a sleeper, and a dream
      const d = c.p(c.at(2), c.at(2, 1.0));
      part(S.G2, [[980, 700], [1640, 700], [1640, 830], [980, 830]], { col: K.brown, p: 0.8, gap: 8, w: 10, seed: 2220, draw: d }, { w: 6, seed: 2221, draw: d });
      part(S.G2, [[980, 610], [1010, 610], [1010, 840], [980, 840]], { col: K.brown, p: 0.9, gap: 6, w: 8, seed: 2222, draw: d }, { w: 5, seed: 2223, draw: d });
      part(S.G, handCircle(1080, 660, 48, 2224, 0, 20).map(([x, y]) => [x, 660 + (y - 660) * 0.6]), { col: K.white, p: 0.9, gap: 6, w: 8, seed: 2225, draw: d }, { w: 5, seed: 2226, draw: d });
      part(S.G, ellipse(1100, 640, 32, 34, 24), { col: K.peach, p: 0.55, gap: 8, w: 10, seed: 2227, draw: d }, { w: 5, seed: 2228, draw: d });
      part(S.G, smooth([[1070, 628], [1090, 604], [1124, 606], [1132, 630], [1112, 620]], 4), { col: K.brown, p: 0.85, gap: 6, w: 8, seed: 2229, draw: d }, { w: 4, seed: 2230, draw: d });
      line(S.G.l, [[1088, 646], [1096, 650], [1104, 646]], { w: 4, seed: 2231, draw: d }); line(S.G.l, [[1112, 646], [1120, 650], [1128, 646]], { w: 4, seed: 2232, draw: d });
      part(S.G, smooth([[1130, 640], [1620, 640], [1636, 700], [1620, 720], [1130, 720], [1120, 680]], 4), { col: K.sky, p: 0.8, gap: 8, w: 10, ang: 0.3, seed: 2233, draw: d }, { w: 6, seed: 2234, draw: d });
      const zz = Math.floor(c.t * 2) % 3; ['z', 'z', 'z'].forEach((z, i) => { if (i <= zz) say(S.FX, z, 1180 + i * 44, 580 - i * 46, { size: 44 + i * 10, font: 'Gaegu', weight: 700, seed: 72 + i, col: K.violet }); });
      if (c.t > c.at(2, 0.8)) {
        bubble(S.G2, 1360, 330, 720, 400, 2240, { cloud: true, tail: [[1220, 560, 22], [1190, 600, 14]], draw: c.p(c.at(2, 0.8), c.at(2, 1.6)) });
        if (c.t > c.at(3)) {   // Nike, the winged goddess of victory, as a little crayon figure
          const dd = c.p(c.at(3), c.at(3, 1.4)), ff = c.p(c.at(3, 0.6), c.at(3, 1.8));
          [-1, 1].forEach((k, i) => part(S.G2, smooth([[1360 + k * 20, 300], [1360 + k * 140, 190], [1360 + k * 190, 220], [1360 + k * 150, 290], [1360 + k * 170, 320], [1360 + k * 40, 330]], 4), { col: K.yellow, p: 0.8, gap: 6, w: 8, seed: 2250 + i, draw: ff }, { w: 5, seed: 2252 + i, draw: dd }));
          person(S.G, { x: 1360, y: 470, s: 0.62, shirt: K.white, pants: K.white, hair: K.ochre, hairStyle: 'bun', seed: 2260, draw: dd, fillDraw: ff, armR: [[44, -230], [60, -290]],
            prop: (C, T, h) => line(C.l, T(handCircle(h[0], h[1] - 20, 26, 2270, 0.1, 20)), { w: 6, col: K.green, seed: 2271, draw: dd }) });
          say(S.FX, 'Nike', 1560, 470, { size: 96, font: 'Gaegu', weight: 700, reveal: c.p(c.at(3, 1.2), c.at(3, 2.0)), seed: 75, col: K.violet, stroke: 2 });
          say(S.FX, 'goddess of victory', 1560, 520, { size: 36, reveal: c.p(c.at(3, 1.9), c.at(3, 2.8)), seed: 76 });
          [[1110, 180], [1620, 200], [1660, 380]].forEach(([x, y], i) => { if (c.t > c.at(3, 2 + i * 0.3)) star(S.G2, [x, y], 22, 2280 + i * 5, i, K.yellow); });
        }
      }
    }
  },
  sfx: c => [[c.turn + 0.15, 'paper', {}], [c.turn + 0.55, 'write', { dur: 0.6, pan: -0.5 }], [c.at(0, 1.6), 'write', { dur: 1.0, pan: -0.5 }], [c.at(1, 0.1), 'scratch', { dur: 0.8, pan: -0.5 }], [c.at(2), 'scribble', { dur: 1.0, pan: 0.4 }], [c.at(2, 0.4), 'snore', { pan: 0.3 }], [c.at(2, 0.8), 'dream', {}], [c.at(3), 'scribble', { dur: 1.6, pan: 0.4 }], [c.at(3, 1.2), 'write', { dur: 0.8, pan: 0.6 }], [c.at(3, 2.0), 'twinkle', {}]],
};

// ————————————————————————————————— 9. first use, and the trials —————————————————————————————————
const trackPage = {
  cam: c => camOf(c, [[0, [960, 540, 1]], [c.at(1, -0.3), [960, 540, 1]], [c.at(2, 0.5), [960, 580, 1.08]], [c.dur, [975, 580, 1.1]]]),
  draw(S, c) {
    const a = T0(c);
    title(S.BG.l, 'June 18, 1971', 700, 175, c, c.at(0, 0.6), 1.2, { size: 92 });
    say(S.BG.l, 'first used', 700, 240, { size: 50, reveal: c.p(c.at(0, 1.9), c.at(0, 2.6)), seed: 77 });
    if (c.t > c.at(0, 2.4)) { const d = c.p(c.at(0, 2.4), c.at(0, 3.4)); shoe(S.G, 1400, 230, 0.55, { draw: d, col: K.white, seed: 2300 }); tick(S.FX, 1400, 188, 0.5, { w: 9, draw: c.p(c.at(0, 3.3), c.at(0, 3.8)), seed: 2301 }); }
    if (c.t > c.at(1)) {
      const d = c.p(c.at(1), c.at(1, 1.4)), f = c.p(c.at(1, 0.6), c.at(1, 2.0));
      [[160, 450, 0.8], [300, 430, 0.95], [1650, 440, 0.85], [1790, 460, 0.75]].forEach(([x, y], i) => pine(S.G2, x, y, [0.8, 0.95, 0.85, 0.75][i], 2310 + i * 7, d));
      fill(S.BG.f, ellipse(960, 650, 860, 250, 60), { col: K.orange, p: 0.55, gap: 10, w: 12, ang: 0.1, seed: 2330, draw: f });
      fill(S.BG.f, ellipse(960, 650, 620, 130, 50), { col: K.green, p: 0.7, gap: 10, w: 12, ang: 1.2, seed: 2331, draw: f });
      [860, 760, 620].forEach((rx, i) => line(S.BG.l, ellipse(960, 650, rx, rx * [0.29, 0.25, 0.21][i], 70), { w: 5, col: K.white, p: 0.95, seed: 2332 + i, draw: d, closed: true }));
      part(S.G2, [[940, 330], [940, 470], [952, 470], [952, 330]], { col: K.brown, p: 0.9, gap: 4, w: 6, seed: 2340, draw: d }, { w: 4, seed: 2341, draw: d });
      part(S.G2, [[952, 334], [1240, 360], [952, 410]], { col: K.sky, p: 0.85, gap: 6, w: 8, seed: 2342, draw: f }, { w: 5, seed: 2343, draw: d });
      say(S.G.l, 'Eugene, Oregon', 1060, 386, { size: 34, reveal: c.p(c.at(1, 1.0), c.at(1, 1.8)), seed: 78 });
      say(S.BG.l, 'Olympic trials 1972', 960, 300, { size: 56, font: 'Gaegu', weight: 700, reveal: c.p(c.at(1, 1.6), c.at(1, 2.6)), seed: 79 });
    }
    if (c.t > c.at(2)) {   // runners on the home straight, the little curve on every shoe
      const q = Math.floor(c.t * 12) / 12, u = c.p(c.at(2), c.dur);
      [[0, K.sky], [1, K.red], [2, K.yellow]].forEach(([i, col]) => person(S.G, { x: lerp(-100 - i * 170, 2100 - i * 190, u), y: 840 + i * 6, s: 0.62, pose: 'run', ph: q * 1.7 + i * 0.3, shirt: col, pants: K.ink, hairStyle: ['short', 'cap', 'curly'][i], capCol: K.green, shoe: K.white, curveOnShoe: true, seed: 2400 + i * 80 }));
    }
  },
  sfx: c => [[c.at(0, 0.6), 'write', { dur: 1.2, pan: -0.3 }], [c.at(0, 1.9), 'write', { dur: 0.7, pan: -0.3 }], [c.at(0, 2.4), 'scratch', { dur: 1.0, pan: 0.5 }], [c.at(1), 'scribble', { dur: 2.0 }], [c.at(1, 1.6), 'write', { dur: 1.0 }], [c.at(2), 'crowd', { dur: c.dur - c.at(2) }], [c.at(2), 'patter', { dur: c.dur - c.at(2) }]],
};

// ————————————————————————————————— 10. the gift, 1983 —————————————————————————————————
const gift = {
  cam: c => camOf(c, [[0, [960, 540, 1]], [c.at(2, -0.4), [960, 540, 1]], [c.at(2, 0.5), [960, 1280, 1]], [c.dur, [960, 1290, 1.04]]]),
  draw(S, c) {
    const a = T0(c);
    // the company grows: shop → bigger → bigger still
    [0, 1, 2].forEach(k => {
      const ts = c.at(0, 0.1 + k * 0.9); if (c.t < ts || (k < 2 && c.t > c.at(0, 1.0 + k * 0.9))) return;
      const d = clamp((c.t - ts) / 0.5), w = [220, 340, 460][k], h = [160, 330, 560][k], x = 1520;
      part(S.G2, [[x - w / 2, 860 - h], [x + w / 2, 860 - h], [x + w / 2, 860], [x - w / 2, 860]], { col: K.ochre, p: 0.7, gap: 8, w: 10, seed: 2500 + k * 9, draw: d }, { w: 6, seed: 2501 + k * 9, draw: d });
      for (let r = 0; r < [1, 3, 5][k]; r++) for (let q = 0; q < [2, 3, 4][k]; q++) { const wx = x - w / 2 + (q + 0.5) * w / [2, 3, 4][k], wy = 860 - h + 60 + r * 100; part(S.G2, [[wx - 26, wy - 30], [wx + 26, wy - 30], [wx + 26, wy + 26], [wx - 26, wy + 26]], { col: K.sky, p: 0.8, gap: 5, w: 7, seed: 2510 + r * 5 + q, draw: d }, { w: 4, seed: 2520 + r * 5 + q, draw: d }); }
    });
    if (c.t > c.at(1)) {
      title(S.BG.l, '1983', 200, 150, c, c.at(1), 0.7);
      const d = c.p(c.at(1, 0.6), c.at(1, 1.6)), f = c.p(c.at(1, 1.2), c.at(1, 2.6));
      // a gold ring seen from the front, the curve standing on top and a diamond set in it
      fill(S.G2.f, [...ellipse(700, 560, 230, 200, 48), ...ellipse(700, 560, 170, 145, 48).reverse()], { col: K.yellow, p: 0.85, gap: 6, w: 9, ang: 0.8, seed: 2550, draw: f });
      fill(S.G2.f, [...ellipse(700, 600, 230, 170, 30, 0.2, 2.9), ...ellipse(700, 600, 170, 120, 30, 0.2, 2.9).reverse()], { col: K.orange, p: 0.5, gap: 7, w: 9, ang: 0.8, seed: 2551, draw: f });
      line(S.G2.l, ellipse(700, 560, 230, 200, 60), { w: 6, seed: 2552, draw: d, closed: true }); line(S.G2.l, ellipse(700, 560, 170, 145, 60), { w: 6, seed: 2553, draw: d, closed: true });
      part(S.G, [...tickPts(700, 340, 0.85).map(([x, y]) => [x, y - 14]), ...tickPts(700, 340, 0.85).reverse().map(([x, y]) => [x, y + 14])], { col: K.yellow, p: 0.95, gap: 5, w: 7, seed: 2554, draw: f }, { w: 5, seed: 2555, draw: d });
      part(S.G, [[650, 330], [680, 300], [710, 330], [680, 362]], { col: K.white, p: 1, gap: 4, w: 6, seed: 2556, draw: f }, { w: 4.5, col: K.sky, seed: 2557, draw: d });
      if (c.t > c.at(1, 2.6)) [[620, 290], [760, 300], [590, 430]].forEach(([x, y], i) => sparkle(S.FX, x, y, 18 + 8 * Math.abs(Math.sin(c.t * 3 + i)), 2560 + i * 3));
    }
    if (c.t > c.at(2, -0.6)) {   // below: shares, and what they became
      const d = c.p(c.at(2, -0.2), c.at(2, 0.6));
      card(S.G2, 560, 1300, 600, 380, -0.03, 2600, { draw: d, col: K.yellow, p: 0.35 });
      line(S.G2.l, [...ellipse(560, 1300, 270, 160, 50)], { w: 4, col: K.orange, p: 0.7, seed: 2601, draw: d, closed: true });
      say(S.G.l, '500', 560, 1310, { size: 130, font: 'Gaegu', weight: 700, reveal: c.p(c.at(2, 0.2), c.at(2, 0.8)), seed: 80 });
      say(S.G.l, 'shares', 560, 1380, { size: 52, reveal: c.p(c.at(2, 0.6), c.at(2, 1.2)), seed: 81 });
      if (c.t > c.at(2, 2.4)) {
        line(S.FX, [[900, 1300], [1140, 1300]], { w: 10, col: K.ink, seed: 2610, draw: c.p(c.at(2, 2.4), c.at(2, 2.8)) });
        line(S.FX, [[1100, 1262], [1146, 1300], [1100, 1338]], { w: 10, col: K.ink, seed: 2611, draw: c.p(c.at(2, 2.7), c.at(2, 2.9)) });
        say(S.FX, '32,000', 1470, 1340, { size: 150, font: 'Gaegu', weight: 700, col: K.orange, reveal: c.p(c.at(2, 3.0), c.at(2, 3.8)), seed: 82, stroke: 3 });
        say(S.BG.l, 'after splits', 1470, 1430, { size: 50, reveal: c.p(c.at(2, 3.6), c.at(2, 4.3)), seed: 83 });
        if (c.t > c.at(2, 3.8)) [[1200, 1170], [1720, 1180], [1760, 1400]].forEach(([x, y], i) => star(S.G2, [x, y], 26, 2620 + i * 5, i * 0.4, K.yellow));
      }
    }
  },
  sfx: c => [[c.at(0, 0.1), 'scribble', { dur: 0.5, pan: 0.6 }], [c.at(0, 1.0), 'scribble', { dur: 0.5, pan: 0.6 }], [c.at(0, 1.9), 'scribble', { dur: 0.6, pan: 0.6 }], [c.at(1), 'write', { dur: 0.7, pan: -0.7 }], [c.at(1, 0.6), 'scratch', { dur: 1.0, pan: -0.3 }], [c.at(1, 1.2), 'scribble', { dur: 1.4, pan: -0.3 }], [c.at(1, 2.6), 'twinkle', { pan: -0.3 }], [c.at(2, -0.2), 'paper', {}], [c.at(2, 0.2), 'write', { dur: 1.0, pan: -0.4 }], [c.at(2, 2.4), 'scratch', { dur: 0.5 }], [c.at(2, 3.0), 'write', { dur: 0.8, pan: 0.5 }], [c.at(2, 3.8), 'twinkle', { pan: 0.5 }]],
};

// ————————————————————————————————— 11. the word goes away, 1995 —————————————————————————————————
const word = {
  cam: c => camOf(c, [[0, [960, 520, 1]], [c.at(2, -0.3), [960, 520, 1]], [c.at(2, 0.5), [780, 460, 1.45]], [c.at(3, -0.4), [780, 460, 1.45]], [c.at(3, 0.5), [960, 540, 1]]]),
  draw(S, c) {
    const a = T0(c);
    card(S.G2, 960, 440, 1180, 580, 0.0, 2700, { draw: c.p(a, a + 0.6), col: K.white, p: 0.85, pin: K.red });
    tick(S.G.l, 740, 450, 1.15, { w: 20, draw: c.p(c.at(0, 0.2), c.at(0, 1.0)), seed: 2701 });
    // the word: hand-lettered in crayon, then rubbed out
    const er = c.p(c.at(1, 0.8), c.at(1, 2.6));
    say(S.G.l, 'Nike', 1260, 500, { size: 160, font: 'Gaegu', weight: 700, reveal: c.p(c.at(0, 1.0), c.at(0, 2.0)), seed: 84, stroke: 2 });
    if (er > 0) {
      const x0 = 1080, x1 = 1450, xe = lerp(x0, x1, er);
      erase(S.G.l, [[x0 - 20, 360], [xe, 360], [xe + 20 * Math.sin(c.t * 30), 540], [x0 - 20, 540]]);
      if (er < 1) {   // the pink eraser scrubbing back and forth
        const wig = 30 * Math.sin(Math.floor(c.t * 12) * 2.1), ex = xe + wig;
        const EP = [[ex - 60, 400], [ex + 60, 380], [ex + 76, 470], [ex - 44, 490]];
        fill(S.FX, EP, { col: K.pink, p: 0.95, gap: 5, w: 8, seed: 2710 }); line(S.FX, [...EP, EP[0]], { w: 5, seed: 2711 });
      }
      for (let k = 0; k < Math.floor(er * 14); k++) dab(S.G2.f, x0 + 24 * k + 10 * hash(k), 560 + 22 * hash(k + 4), 6, { col: K.pink, p: 0.8, seed: 2720 + k });
    }
    if (c.t > c.at(3)) {   // everybody knew: the little curve turns up everywhere
      const items = [[230, 820, 'shoe'], [520, 860, 'cap'], [1420, 860, 'shirt'], [1720, 820, 'shoe'], [180, 200, 'cap'], [1760, 180, 'shirt']];
      items.forEach(([x, y, k], i) => {
        const ts = c.at(3, 0.1 + i * 0.25); if (c.t < ts) return; const d = clamp((c.t - ts) / 0.4);
        if (k === 'shoe') { part(S.G, shoeSide(x, y, 3.2), { col: K.white, p: 0.9, gap: 6, w: 8, seed: 2750 + i, draw: d }, { w: 5, seed: 2760 + i, draw: d }); line(S.G.l, tickPts(x + 14, y - 26, 0.42), { w: 7, col: K.orange, seed: 2770 + i, draw: d }); }
        if (k === 'cap') { part(S.G, smooth([[x - 80, y], [x - 70, y - 70], [x, y - 92], [x + 70, y - 70], [x + 80, y], [x + 160, y + 8], [x + 150, y + 20], [x - 80, y + 14]], 3), { col: K.sky, p: 0.85, gap: 6, w: 8, seed: 2750 + i, draw: d }, { w: 5, seed: 2760 + i, draw: d }); line(S.G.l, tickPts(x, y - 40, 0.32), { w: 6, col: K.white, seed: 2770 + i, draw: d }); }
        if (k === 'shirt') { part(S.G, [[x - 90, y - 160], [x - 40, y - 180], [x + 40, y - 180], [x + 90, y - 160], [x + 130, y - 100], [x + 90, y - 80], [x + 80, y + 20], [x - 80, y + 20], [x - 90, y - 80], [x - 130, y - 100]], { col: K.red, p: 0.8, gap: 7, w: 9, seed: 2750 + i, draw: d }, { w: 5, seed: 2760 + i, draw: d }); line(S.G.l, tickPts(x + 10, y - 90, 0.35), { w: 7, col: K.white, seed: 2770 + i, draw: d }); }
      });
    }
  },
  sfx: c => {
    const o = [[c.turn + 0.15, 'paper', {}], [c.at(0, 0.2), 'scratch', { dur: 0.8, pan: -0.3 }], [c.at(0, 1.0), 'write', { dur: 1.0, pan: 0.3 }], [c.at(1, 0.8), 'erase', { dur: 1.8, pan: 0.3 }]];
    for (let i = 0; i < 6; i++) o.push([c.at(3, 0.1 + i * 0.25), 'pop', { pan: [-0.8, -0.5, 0.5, 0.8, -0.8, 0.8][i] }]);
    return o;
  },
};

// ————————————————————————————————— 12. what it means (wax resist) —————————————————————————————————
// White crayon is on this page from the start (footprints, speed lines, three words), almost invisible on white
// paper. When the blue wash sweeps across, the wax refuses the paint and the runners appear.
const BANDS = [{ y0: -60, y1: 560, dir: 1, seed: 1 }, { y0: 480, y1: 1140, dir: -1, seed: 2 }];
function washBands(LW, c, times) {
  const g = LW.g; g.save(); g.setTransform(CAM.s, 0, 0, CAM.s, W / 2 - CAM.x * CAM.s, H / 2 - CAM.y * CAM.s);
  BANDS.forEach((b, j) => {
    const [t0, t1] = times[j]; if (c.t < t0) return;
    const u = clamp((c.t - t0) / (t1 - t0)), e = u < 0.5 ? 2 * u * u : 1 - Math.pow(-2 * u + 2, 2) / 2, X0 = -200, X1 = 2120;
    const f = b.dir > 0 ? lerp(X0, X1, 0.15 * u + 0.85 * e) : lerp(X1, X0, 0.15 * u + 0.85 * e);
    const top = [], bot = [];
    for (let x = X0; x <= X1; x += 40) { top.push([x, b.y0 + 12 * Math.sin(x * 0.006 + b.seed) + 12 * hash(x * 0.37 + b.seed)]); bot.push([x, b.y1 + 14 * Math.sin(x * 0.005 + b.seed * 2) + 14 * hash(x * 0.71 + b.seed)]); }
    const fx = y => f + b.dir * 70 * Math.sin(clamp((y - b.y0) / (b.y1 - b.y0)) * Math.PI) + 12 * Math.sin(y * 0.05);
    g.save(); g.beginPath();
    const xe = b.dir > 0 ? X0 - 50 : X1 + 50; g.moveTo(xe, b.y0 - 200); for (let y = b.y0 - 200; y <= b.y1 + 200; y += 20) g.lineTo(fx(y), y); g.lineTo(xe, b.y1 + 200); g.closePath(); g.clip();
    const sh = new Path2D(); top.forEach(([x, y], i) => i ? sh.lineTo(x, y) : sh.moveTo(x, y)); for (let i = bot.length - 1; i >= 0; i--) sh.lineTo(...bot[i]); sh.closePath();
    g.fillStyle = '#000'; g.globalAlpha = 0.72; g.fill(sh);
    g.save(); g.clip(sh); const R = mulberry(b.seed * 97);
    for (let i = 0; i < 22; i++) { const yy = lerp(b.y0, b.y1, R()), wd = 6 + R() * 30, dark = R() < 0.55; g.beginPath(); for (let x = X0; x <= X1; x += 60) { const y = yy + 14 * Math.sin(x * 0.002 + i); x === X0 ? g.moveTo(x, y) : g.lineTo(x, y); } g.lineWidth = dark ? wd : wd * 0.5; g.globalCompositeOperation = dark ? 'source-over' : 'destination-out'; g.globalAlpha = dark ? 0.14 + R() * 0.1 : 0.05 + R() * 0.06; g.strokeStyle = '#000'; g.stroke(); }
    g.globalCompositeOperation = 'source-over';
    g.beginPath(); for (let y = b.y0 - 80; y <= b.y1 + 80; y += 16) { const x = fx(y) - b.dir * 14; y === b.y0 - 80 ? g.moveTo(x, y) : g.lineTo(x, y); }
    g.lineWidth = u < 1 ? 34 : 22; g.globalAlpha = u < 1 ? 0.3 : 0.14; g.stroke(); g.restore(); g.restore();
  });
  g.restore();
}
const meaning = {
  cam: c => camOf(c, [[0, [960, 540, 1.04]], [c.at(1, -0.2), [960, 540, 1.04]], [c.at(3, -0.2), [960, 540, 1.0]], [c.dur, [960, 540, 1.0]]]),
  draw(S, c) {
    const a = T0(c);
    // hidden white wax: two trails of footprints, speed lines, and three words
    for (let k = 0; k < 16; k++) {
      [[0, 230, 0.004], [1, 760, 0.005]].forEach(([j, yb, fr]) => {
        const x = 70 + k * 122 + j * 50, y = yb + 70 * Math.sin(x * fr + j * 2) + (k % 2 ? 26 : -26), r = 0.25 - j * 0.5;
        fill(S.BG.f, xf(ellipse(0, 0, 26, 14, 18), { x, y, r }), { col: K.white, p: 1, gap: 4, w: 6, seed: 2800 + k + j * 40, over: 1 });
        fill(S.BG.f, xf(ellipse(-30, 0, 12, 10, 12), { x, y, r }), { col: K.white, p: 1, gap: 4, w: 6, seed: 2820 + k + j * 40, over: 1 });
      });
    }
    for (let k = 0; k < 9; k++) { const y = 120 + k * 104 + 20 * hash(k), x = 140 + 1500 * hash(k + 3); line(S.BG.l, [[x, y], [x + 260 + 120 * hash(k + 7), y - 6]], { w: 10, col: K.white, p: 1, seed: 2850 + k }); }
    [['running', 400, 400], ['racing', 1500, 360], ['winning', 980, 660]].forEach(([s, x, y], i) => say(S.BG.l, s, x, y, { size: 96, font: 'Gaegu', weight: 700, col: K.white, p: 1, seed: 85 + i, stroke: 4 }));
    // the shoe and its curve (drawn after the wash: crisp on top)
    shoe(S.G, 960, 520, 1.45, { draw: c.p(a, a + 1.4), col: K.white, seed: 2900 });
    tick(S.FX, 940, 440, 0.9, { w: 18, draw: c.p(c.at(0, 0.3), c.at(0, 1.1)), seed: 2901 });
    say(S.FX, 'only a shape', 960, 180, { size: 60, reveal: c.p(c.at(0, 0.8), c.at(0, 1.6)), seed: 88 });
    if (c.t > c.at(3)) say(S.FX, '17 1/2 hours · $35', 960, 860, { size: 74, font: 'Gaegu', weight: 700, col: K.yellow, reveal: c.p(c.at(3, 0.1), c.at(3, 1.6)), seed: 89, stroke: 3 });
    if (c.t > c.at(4)) sprout(S.G, 1640, 900, 0.9, c.p(c.at(4, 0.2), c.at(4, 2.4)), 2910);
    washBands(S.WASH, c, [[c.at(1, 0.1), c.at(1, 2.4)], [c.at(2, 0.0), c.at(2, 2.6)]]);
    return { wash: c.t > c.at(1, 0.1) ? PAL.wash : null };
  },
  sfx: c => [[c.turn + 0.15, 'scratch', { dur: 1.4 }], [c.at(0, 0.3), 'scratch', { dur: 0.8 }], [c.at(0, 0.8), 'write', { dur: 0.8 }], [c.at(1, 0.0), 'dip', {}], [c.at(1, 0.1), 'brush', { dur: 2.3, dir: 1 }], [c.at(2, -0.1), 'dip', {}], [c.at(2, 0.0), 'brush', { dur: 2.6, dir: -1 }], [c.at(2, 0.6), 'twinkle', { pan: 0 }], [c.at(3, 0.1), 'write', { dur: 1.5 }], [c.at(4, 0.2), 'grow', {}]],
};

export const PAGES = { title: titlePage, brs, campus, brief, tissue, pitch, invoice, name, track: trackPage, gift, word, meaning };
