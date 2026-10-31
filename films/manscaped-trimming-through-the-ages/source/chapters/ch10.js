// 10 · The Modern Age (270–300 s). A blank page; the approved product draws into view; the procession of the ages;
// the squirrels arrive in suits with a tiny lawsuit; the film's one watercolour wash (sap green) reveals the slogan
// that has been on the page in white wax all along, and the approved wordmark sits beneath.
// Brand assets are never drawn or lettered here: assets/brand/packshot.png and assets/brand/wordmark.png (approved,
// supplied by the client) are composited as images. Until they exist, labelled crayon placeholders mark their slots.
import { line, fill, handCircle, ellipse, smooth, xf, CAM, W, H } from '../crayon.js';
import { part } from '../rig.js';
import { K, person, squirrel, say } from '../figs.js';
import { camOf, F, L, clamp, lerp, hash, wob } from './util.js';
const load = src => new Promise(r => { const im = new Image(); im.onload = () => r(im); im.onerror = () => r(null); im.src = src; });
const PACK = await load('./assets/brand/packshot.png'), MARK = await load('./assets/brand/wordmark.png');
export const ASSETS = { packshot: !!PACK, wordmark: !!MARK };
const PS = { x: 720, y: 450, w: 440, h: 440 }, WM = { x: 720, y: 780, w: 600, h: 120 };
const BANDS = [{ y0: -80, y1: 560, dir: 1, seed: 1 }, { y0: 470, y1: 1160, dir: -1, seed: 2 }];
const SLOGAN = 'EVOLUTION STARTS BELOW';

// draw an approved image into its slot, revealed behind a crayon-hatch mask (prog 0..1), at screen scale
function reveal(IMG, im, R, prog, seed) {
  const g = IMG.g, sxx = (R.x - CAM.x) * CAM.s + W / 2, syy = (R.y - CAM.y) * CAM.s + H / 2, s = CAM.s;
  const k = Math.min(R.w / im.width, R.h / im.height), w = im.width * k * s, h = im.height * k * s;
  const m = document.createElement('canvas'); m.width = W; m.height = H; const mg = m.getContext('2d');
  mg.strokeStyle = '#000'; mg.lineCap = 'round'; mg.lineWidth = 46 * s;
  const n = 18, done = prog * n;
  for (let i = 0; i < Math.ceil(done); i++) { const u = Math.min(1, done - i), y = syy - h / 2 + (i + 0.5) * h / n;
    mg.beginPath(); mg.moveTo(sxx - w / 2 - 20, y + 10 * Math.sin(i * 1.7 + seed)); mg.lineTo(sxx - w / 2 - 20 + (w + 40) * u, y - 10 * Math.sin(i * 2.3 + seed)); mg.stroke(); }
  mg.globalCompositeOperation = 'source-in'; mg.drawImage(im, sxx - w / 2, syy - h / 2, w, h);
  g.drawImage(m, 0, 0);
}
function placeholder(S, R, label, dr, sd) {
  const P = [[R.x - R.w / 2, R.y - R.h / 2], [R.x + R.w / 2, R.y - R.h / 2], [R.x + R.w / 2, R.y + R.h / 2], [R.x - R.w / 2, R.y + R.h / 2]];
  for (let i = 0; i < 4; i++) { const a = P[i], b = P[(i + 1) % 4]; for (let k = 0; k < 10; k += 2) line(S.G.l, [[lerp(a[0], b[0], k / 10), lerp(a[1], b[1], k / 10)], [lerp(a[0], b[0], (k + 1) / 10), lerp(a[1], b[1], (k + 1) / 10)]], L(sd + i * 10 + k, { w: 5, col: K.ink, draw: clamp(dr * 4 - i) })); }
  say(S.G.l, label, R.x, R.y + 12, { size: Math.min(34, R.h * 0.3), reveal: clamp(dr * 2 - 1), seed: sd + 50, col: K.ink });
}
function washBands(LW, c, times) {
  const g = LW.g; g.save(); g.setTransform(CAM.s, 0, 0, CAM.s, W / 2 - CAM.x * CAM.s, H / 2 - CAM.y * CAM.s);
  BANDS.forEach((b, j) => {
    const [t0, t1] = times[j]; if (c.t < t0) return;
    const u = clamp((c.t - t0) / (t1 - t0)), e = u < 0.5 ? 2 * u * u : 1 - Math.pow(-2 * u + 2, 2) / 2, X0 = -220, X1 = 1660;
    const f = b.dir > 0 ? lerp(X0, X1, 0.15 * u + 0.85 * e) : lerp(X1, X0, 0.15 * u + 0.85 * e);
    const top = [], bot = []; for (let x = X0; x <= X1; x += 40) { top.push([x, b.y0 + 12 * Math.sin(x * 0.006 + b.seed) + 12 * hash(x * 0.37 + b.seed)]); bot.push([x, b.y1 + 14 * Math.sin(x * 0.005 + b.seed * 2) + 14 * hash(x * 0.71 + b.seed)]); }
    const fx = y => f + b.dir * 70 * Math.sin(clamp((y - b.y0) / (b.y1 - b.y0)) * Math.PI) + 12 * Math.sin(y * 0.05);
    g.save(); g.beginPath(); const xe = b.dir > 0 ? X0 - 50 : X1 + 50; g.moveTo(xe, b.y0 - 200); for (let y = b.y0 - 200; y <= b.y1 + 200; y += 20) g.lineTo(fx(y), y); g.lineTo(xe, b.y1 + 200); g.closePath(); g.clip();
    const sh = new Path2D(); top.forEach(([x, y], i) => i ? sh.lineTo(x, y) : sh.moveTo(x, y)); for (let i = bot.length - 1; i >= 0; i--) sh.lineTo(...bot[i]); sh.closePath();
    g.fillStyle = '#000'; g.globalAlpha = 0.74; g.fill(sh);
    g.save(); g.clip(sh); let s = b.seed * 97; const R = () => { s = (s * 16807) % 2147483647; return s / 2147483647; };
    for (let i = 0; i < 22; i++) { const yy = lerp(b.y0, b.y1, R()), wd = 6 + R() * 30, dark = R() < 0.55; g.beginPath(); for (let x = X0; x <= X1; x += 60) { const y = yy + 14 * Math.sin(x * 0.002 + i); x === X0 ? g.moveTo(x, y) : g.lineTo(x, y); } g.lineWidth = dark ? wd : wd * 0.5; g.globalCompositeOperation = dark ? 'source-over' : 'destination-out'; g.globalAlpha = dark ? 0.14 + R() * 0.1 : 0.05 + R() * 0.06; g.strokeStyle = '#000'; g.stroke(); }
    g.globalCompositeOperation = 'source-over'; g.beginPath(); for (let y = b.y0 - 80; y <= b.y1 + 80; y += 16) { const x = fx(y) - b.dir * 14; y === b.y0 - 80 ? g.moveTo(x, y) : g.lineTo(x, y); }
    g.lineWidth = u < 1 ? 34 : 22; g.globalAlpha = u < 1 ? 0.3 : 0.14; g.stroke(); g.restore(); g.restore();
  });
  g.restore();
}
const PROC = [['pharaoh', { armR: [56, -270], armL: [-56, -270] }], ['philosopher', { expr: 'happy' }], ['senator', { armR: [56, -270] }], ['knight', {}], ['inventor', { beardLen: 0.05 }], ['gentleman', {}], ['salesman', {}], ['astronaut', {}], ['gerald', { expr: 'happy' }]];
export default {
  cam: c => camOf(c, [[0, [720, 540, 1]], [c.at(3, -0.3), [720, 540, 1]], [c.at(3, 0.6), [900, 600, 1.12]], [c.at(4, -0.8), [900, 600, 1.12]], [c.at(4, 0.2), [720, 540, 1]], [30, [720, 540, 1]]]),
  draw(S, c) {
    // the slogan, in white wax, on the page from the very first frame of the chapter
    say(S.BG.l, SLOGAN, 720, 190, { size: 92, font: 'Gaegu', weight: 700, col: K.white, p: 0.9, seed: 2400, stroke: 1.5 });
    // the product (approved packshot) draws into view in beat 2
    const pd = c.p(c.at(1, -0.4), c.at(1, 1.6));
    let image = false;
    if (pd > 0) { if (PACK) {   // the supplied photo, pasted into the book as a print with two strips of tape
        const b = PS.w / 2 + 16, d2 = clamp(pd * 2);
        part(S.G, [[PS.x - b, PS.y - b], [PS.x + b, PS.y - b], [PS.x + b, PS.y + b], [PS.x - b, PS.y + b]], F(K.white, 2420, { draw: d2, p: 0.95 }), L(2421, { w: 4, draw: d2 }));
        reveal(S.IMG, PACK, PS, pd, 3); image = true;
        if (pd >= 1) [[-1, 2430], [1, 2440]].forEach(([sx, sd]) => { const cx = PS.x + sx * (b - 10), cy = PS.y + b - 4, a = -sx * 0.6;
          const q = [[-56, -16], [56, -16], [56, 16], [-56, 16]].map(([u, v]) => [cx + u * Math.cos(a) - v * Math.sin(a), cy + u * Math.sin(a) + v * Math.cos(a)]);
          fill(S.FX, q, F(K.yellow, sd, { p: 0.55 })); line(S.FX, [...q, q[0]], L(sd + 1, { w: 2.5, col: K.ochre })); }); }
      else placeholder(S, PS, 'approved Lawn Mower packshot', pd, 2410); }
    // the procession of the ages, left to right, rejoicing
    if (c.tq > c.at(2, -0.6)) { const u = c.p(c.at(2, -0.6), c.at(3, 0.4));
      PROC.forEach(([who, o], i) => { const x = -150 - i * 150 + 3000 * u; if (x < -120 || x > 1560) return;
        person(S.G, who, { x, y: 900, s: 0.6, view: 'side', pose: 'walk', ph: c.tq * 1.8 + i * 0.37, expr: 'happy', seed: 2500 + i * 30, ...o, ...(o.armR ? { view: 'front', pose: 'walk' } : {}) }); }); }
    // the squirrels, in suits, with a suitcase on wheels and a very small lawsuit
    if (c.tq > c.at(3, -0.4)) { const u = c.p(c.at(3, -0.4), c.at(3, 1.4));
      [0, 1, 2].forEach(i => { const x = lerp(1600 + i * 90, 1060 + i * 110, u);
        squirrel(S.G, { x, y: 920, s: 0.62, i, suit: true, flip: true, paw: i === 1 ? [40, -110] : [36, -70],
          hold: i === 1 ? (C, T, p) => { const [px, py] = T([p])[0]; part(C, [[px - 60, py - 70], [px + 6, py - 72], [px + 8, py - 6], [px - 58, py - 4]], F(K.white, 2600, { p: 0.95 }), L(2601, { w: 3.5 })); say(C.l, 'LAWSUIT', px - 26, py - 30, { size: 15, font: 'Gaegu', weight: 700, seed: 2602 }); } : null }); });
      const bx = lerp(1880, 1400, u), bw = u < 1 ? Math.floor(c.tq * 12) % 2 : 0;
      part(S.G, [[bx - 40, 860], [bx + 40, 860], [bx + 40, 900], [bx - 40, 900]], F(K.brown, 2610), L(2611, { w: 4 })); line(S.G.l, [[bx - 14, 860], [bx - 14, 846], [bx + 14, 846], [bx + 14, 860]], L(2612, { w: 4 }));
      [-24, 24].forEach((dx, i) => line(S.G.l, handCircle(bx + dx, 908, 7, 2613 + i + bw, 0, 10), L(2615 + i, { w: 4 }))); }
    // the wash, then the wordmark (after the wash, so it stays clean and readable)
    const wt = [[c.at(4, -0.4), c.at(4, 1.5)], [c.at(4, 0.5), c.at(4, 2.4)]];
    washBands(S.WASH, c, wt);
    const md = c.p(c.at(4, 1.2), c.at(4, 2.2));
    if (md > 0) { if (MARK) { reveal(S.IMG, MARK, WM, md, 7); image = true; } else placeholder(S, WM, 'approved MANSCAPED wordmark', md, 2700); }
    return { wash: c.t > wt[0][0], image };
  },
  sfx: c => [[c.turn + 0.2, 'room', { dur: 28 }], [c.at(1, -0.4), 'scratch', { dur: 2.0 }], [c.at(2, -0.6), 'march', { dur: c.at(3, 0.4) - c.at(2, -0.6) }],
    [c.at(3, -0.4), 'wheels', { dur: 1.8, pan: 0.6 }], [c.at(3, 1.0), 'paper', { pan: 0.5 }], [c.at(4, -0.6), 'dip', {}], [c.at(4, -0.4), 'brush', { dur: 1.9, dir: 1 }], [c.at(4, 0.5), 'brush', { dur: 1.9, dir: -1 }], [c.at(4, 1.2), 'twinkle', {}]],
};
