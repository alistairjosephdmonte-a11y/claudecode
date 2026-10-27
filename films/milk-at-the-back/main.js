// Why Supermarkets Put Milk at the Back — 40 scenes × 15 s on one continuous coral route line.
import { clamp, lerp, seg, ss, eo, ei, eio, back, hash, track, TAU } from '/core/lib.js';
import { W, H, init, frame, g, push, pop, translate, rotate, scale, stroke, fillOnly, rect, ell, S, reset } from './toon.js';
import * as K from './props.js';
import { SCENES, CHAPTERS, along } from './scenes.js';

const C = document.getElementById('c'); init(C);
await Promise.all(['400 100px "Titan One"', '800 40px "Baloo 2"', '600 40px "Baloo 2"', '60px "Caveat Brush"'].map(f => document.fonts.load(f)));
const SC_D = 15, DUR = SCENES.length * SC_D;
const CAMS = SCENES.map(s => track(s.cam.map(k => [k[0], [k[1], k[2], k[3], k[4] ?? 0]])));
const sepiaOf = (s, u) => typeof s.sepia === 'function' ? s.sepia(u) : (s.sepia ?? 0);

// ---- route line: the coral marker, constant width, a marker pen at its head ----
function partial(pts, k) {
  if (k >= 1) return pts.slice();
  const out = [pts[0]]; let L = 0; const seglen = []; for (let i = 1; i < pts.length; i++) { const d = Math.hypot(pts[i][0] - pts[i - 1][0], pts[i][1] - pts[i - 1][1]); seglen.push(d); L += d; }
  let r = k * L; for (let i = 0; i < seglen.length; i++) { if (r >= seglen[i]) { out.push(pts[i + 1]); r -= seglen[i]; } else { const f = seglen[i] ? r / seglen[i] : 0; out.push([lerp(pts[i][0], pts[i + 1][0], f), lerp(pts[i][1], pts[i + 1][1], f)]); break; } }
  return out;
}
function drawRoute(R, u) {
  if (R.dot) { push(); translate(R.pts[0][0], R.pts[0][1]); fillOnly(ell(0, 0, 14, 14), K.BASE.coral); pop(); return R.pts[0]; }
  const pts = partial(R.pts, clamp(R.k)); if (pts.length < 2) return R.pts[0];
  stroke(pts, 14, { line: K.BASE.coral, boil: .6 });
  const h = pts[pts.length - 1], p = pts[pts.length - 2], a = Math.atan2(h[1] - p[1], h[0] - p[0]);
  if (R.k > 0 && R.k < 1) {   // the marker pen drawing it
    push(); translate(h[0], h[1]); rotate(a + Math.PI * .8);
    K.card([[0, -6], [26, -14], [130, -14], [130, 14], [26, 14], [0, 6]], K.P.milk, { lw: 5, sx: 5, sy: 6 });
    K.card([[0, -6], [26, -14], [26, 14], [0, 6]], K.BASE.coral, { shadow: false, rim: false, lw: 4 });
    K.card([[96, -16], [140, -16], [140, 16], [96, 16]], K.P.blue, { shadow: false, rim: false, lw: 4 });
    pop();
  }
  return h;
}

// ---- camera: one continuous move per scene; the seams push hard into the route head / out of the next route start ----
function camera(i, u) {
  const s = SCENES[i]; let [cx, cy, z, rot] = CAMS[i](u);
  const R = s.route(u), R0 = s.route(0), R1 = s.route(15);
  const head = along(partial(R1.pts, clamp(R1.k)), 1), start = R0.pts[0];
  const wOut = i < SCENES.length - 1 ? ei(seg(u, 14.45, 15)) : 0, wIn = i > 0 ? 1 - eo(seg(u, 0, .55)) : 0;
  if (wOut > 0) { cx = lerp(cx, head[0], wOut); cy = lerp(cy, head[1], wOut); z *= lerp(1, 3.2, wOut); }
  if (wIn > 0) { cx = lerp(cx, start[0], wIn); cy = lerp(cy, start[1], wIn); z *= lerp(1, 3.2, wIn); }
  reset(); translate(W / 2, H / 2); scale(z); if (rot) rotate(rot); translate(-cx, -cy);
}

// ---- cards: chapter titles, the film's title, the end line ----
const CH_AT = Object.fromEntries(CHAPTERS.map(([i, t], n) => [i, [n + 1, t]]));
function titleCard(u, t0, t1, lines, o = {}) {
  if (u < t0 || u > t1) return;
  const kin = back(seg(u, t0, t0 + .4), 1.6), kout = ei(seg(u, t1 - .35, t1));
  const sep = o.sepia, bg = sep ? K.SEPIA.milk : K.BASE.milk, ink = sep ? K.SEPIA.ink : K.BASE.ink, accent = sep ? K.SEPIA.blue : K.BASE.blue;
  g.setTransform(1, 0, 0, 1, 0, 0);
  g.save(); g.translate(W / 2, H / 2 + (1 - kin) * 300 - kout * 1200); g.rotate((1 - kin) * .06 - kout * .08);
  g.fillStyle = 'rgba(27,27,27,.18)'; g.fillRect(-W / 2 + 22, -H / 2 + 26, W, H);
  g.fillStyle = bg; g.fillRect(-W / 2 - 40, -H / 2 - 40, W + 80, H + 80);
  g.textAlign = 'center'; g.textBaseline = 'middle';
  if (o.num) { g.font = '800 44px "Baloo 2"'; g.fillStyle = ink; g.globalAlpha = .7; g.fillText(`CHAPTER ${o.num}`, 0, -150); g.globalAlpha = 1; }
  g.font = o.end ? '400 96px "Titan One"' : '400 112px "Titan One"'; g.lineJoin = 'round';
  lines.forEach((l, k) => { const y = (k - (lines.length - 1) / 2) * 128 - (o.num ? 10 : 0); g.lineWidth = 16; g.strokeStyle = ink; g.strokeText(l, 0, y); g.fillStyle = accent; g.fillText(l, 0, y); });
  // the route line runs under every title, drawn by the marker
  const w = Math.min(1, seg(u, t0 + .3, t0 + 1.4)) * 900, y = lines.length * 64 + 40;
  g.beginPath(); g.moveTo(-450, y); for (let x = 0; x <= w; x += 20) g.lineTo(-450 + x, y + Math.sin(x * .02) * 5); g.lineWidth = 14; g.lineCap = 'round'; g.strokeStyle = K.BASE.coral; g.stroke();
  g.restore();
}

// ---- print finish: halftone, tilt-shift depth of field, vignette ----
const HT = document.createElement('canvas'); HT.width = W; HT.height = H;
{ const x = HT.getContext('2d'); for (let yy = 0; yy < H; yy += 7) for (let xx = (yy / 7) % 2 ? 3.5 : 0; xx < W; xx += 7) { x.beginPath(); x.arc(xx, yy, 1.5 + hash(xx * .13 + yy * .71) * .6, 0, TAU); x.fillStyle = 'rgba(40,30,20,.5)'; x.fill(); } }
const TS = document.createElement('canvas'); TS.width = W; TS.height = H; const TX = TS.getContext('2d');
function finish(sep) {
  g.setTransform(1, 0, 0, 1, 0, 0);
  g.globalAlpha = .07; g.globalCompositeOperation = 'multiply'; g.drawImage(HT, 0, 0); g.globalCompositeOperation = 'source-over'; g.globalAlpha = 1;
  TX.globalCompositeOperation = 'copy'; TX.filter = 'blur(7px)'; TX.drawImage(C, 0, 0); TX.filter = 'none';
  TX.globalCompositeOperation = 'destination-in'; const gr = TX.createLinearGradient(0, 0, 0, H);
  gr.addColorStop(0, 'rgba(0,0,0,1)'); gr.addColorStop(.26, 'rgba(0,0,0,0)'); gr.addColorStop(.7, 'rgba(0,0,0,0)'); gr.addColorStop(1, 'rgba(0,0,0,1)');
  TX.fillStyle = gr; TX.fillRect(0, 0, W, H); TX.globalCompositeOperation = 'source-over';
  g.drawImage(TS, 0, 0);
  const v = g.createRadialGradient(W / 2, H / 2, H * .45, W / 2, H / 2, H * 1.05); v.addColorStop(0, 'rgba(0,0,0,0)'); v.addColorStop(1, sep ? 'rgba(70,40,10,.32)' : 'rgba(20,30,50,.22)'); g.fillStyle = v; g.fillRect(0, 0, W, H);
}

// ---- render ----
window.render = function (t) {
  t = clamp(t, 0, DUR - 1e-4);
  const i = Math.min(SCENES.length - 1, Math.floor(t / SC_D)), u = t - i * SC_D, s = SCENES[i];
  frame(t); const sep = sepiaOf(s, u); K.setPal(sep);
  g.setTransform(1, 0, 0, 1, 0, 0); g.fillStyle = K.P.milk; g.fillRect(0, 0, W, H);
  camera(i, u);
  s.draw(u);
  drawRoute(s.route(u), u);
  finish(sep > .5);
  const ch = CH_AT[i]; if (ch) titleCard(u, i === 0 ? 1.0 : .2, (i === 0 ? 1.0 : .2) + 2.6, [ch[1]], { num: ch[0], sepia: sep > .5 });
  if (s.card) titleCard(u, s.card.t0, s.card.t1 + (s.card.end ? 1 : 0), s.card.text, { sepia: sep > .5, end: s.card.end });
  if (i === 0 && u < .6) { g.setTransform(1, 0, 0, 1, 0, 0); g.fillStyle = `rgba(0,0,0,${1 - u / .6})`; g.fillRect(0, 0, W, H); }
  if (s.end && u > 14.3) { g.setTransform(1, 0, 0, 1, 0, 0); g.fillStyle = `rgba(0,0,0,${ss(seg(u, 14.3, 14.9))})`; g.fillRect(0, 0, W, H); }
};

// ---- sound events: narration, act cues, impacts ----
const EV = [], TYPES = ['pop', 'snap', 'rustle', 'thunk', 'pop', 'drop'];
SCENES.forEach((s, i) => {
  EV.push({ t: i * SC_D + .15, type: 'vo', id: `s${String(i + 1).padStart(2, '0')}` });
  s.snaps.forEach((u, k) => EV.push({ t: i * SC_D + u, type: TYPES[Math.floor(hash(i * 13 + k) * TYPES.length)], v: .7 + hash(i + k * 3) * .3 }));
  if (i) EV.push({ t: i * SC_D - .3, type: 'whoosh' });
  if (CH_AT[i]) EV.push({ t: i * SC_D + (i === 0 ? 1.0 : .2), type: 'card' });
});
for (const [a, t] of [['I', 0], ['II', 105], ['III', 285], ['IV', 450], ['reveal', 570], ['end', 585]]) EV.push({ t, type: 'cue', name: a });
EV.sort((a, b) => a.t - b.t);
window.EV = EV; window.DUR = DUR;
window.render(0); window.READY = true;
