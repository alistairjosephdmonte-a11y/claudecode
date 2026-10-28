// Picture-book figures and props for the swoosh story. People are generic crayon figures (no likenesses);
// the curve is only ever a loose hand-drawn crayon stroke, never the official artwork.
import { line, fill, dab, ellipse, handCircle, xf, smooth, text, sx, sy, CAM } from './crayon.js';
import { part, tube, curve } from './rig.js';
import { PAL } from './pal.js';
import { hash, clamp, lerp } from '/core/lib.js';
export const K = PAL.crayon;
const LW = 6;
const lo = (seed, x = {}) => ({ w: LW, seed, ...x });

// text in world coordinates (crayon.text works in screen pixels)
export function say(L, str, x, y, o = {}) { return text(L, str, sx(x), sy(y), { ...o, size: (o.size ?? 56) * CAM.s }); }

// —— person: feet at (x, y), about 300 units tall at s = 1 ——
// o: shirt, pants, hair, hairStyle ('short' | 'cap' | 'long' | 'bun' | 'curly'), pose ('stand' | 'run' | 'sit' | 'sleep'),
//    ph (run phase 0..1), armL / armR ([[elbow], [hand]] in local coords), flip, prop(C, T) drawn last, draw (0..1 line progress)
export function person(C, o) {
  const k = o.flip ? -1 : 1, s = o.s || 1, sd = o.seed || 500;
  const T = pts => xf(pts, { x: o.x, y: o.y, s, sx: k, r: o.r || 0 });
  const dr = o.draw ?? 1, fd = o.fillDraw ?? dr;
  const skin = { col: K.peach, p: 0.55, gap: 8, w: 10, ang: 0.5, seed: sd + 1, draw: fd };
  const shirt = { col: o.shirt || K.sky, p: 0.8, gap: 7, w: 9, ang: 1.1, seed: sd + 2, draw: fd };
  const pants = { col: o.pants || K.ink, p: 0.6, gap: 7, w: 9, ang: 0.3, seed: sd + 3, draw: fd };
  const hair = { col: o.hair || K.brown, p: 0.85, gap: 6, w: 8, ang: 1.3, seed: sd + 4, draw: fd };
  const L = (n, x = {}) => lo(sd + n, { draw: dr, ...x });
  let legs;
  if (o.pose === 'run') {
    const a = Math.sin((o.ph || 0) * Math.PI * 2);
    legs = [[[-8, -128], [-8 + 40 * a, -68], [-20 + 70 * a, -8 + (a < 0 ? -26 * a : 0)]], [[8, -128], [8 - 40 * a, -68], [-6 - 70 * a, -8 + (a > 0 ? 26 * a : 0)]]];
  } else if (o.pose === 'sit') legs = [[[-10, -128], [50, -126], [52, -40]], [[10, -128], [66, -124], [70, -40]]];
  else legs = [[[-14, -128], [-16, -66], [-18, -6]], [[14, -128], [16, -66], [18, -6]]];
  // back leg + shoe
  legs.forEach(([h, kn, f], i) => {
    part(C, T(tube([h, kn, f], 30, 24)), pants, L(10 + i));
    part(C, T(shoeSide(f[0], f[1], 1)), { col: o.shoe || K.white, p: 0.9, gap: 6, w: 7, seed: sd + 20 + i, draw: fd }, L(12 + i));
    if (o.curveOnShoe) line(C.l, T(tickPts(f[0] + 4, f[1] - 8, 0.22)), { w: 4, col: K.orange, p: 1, seed: sd + 14 + i, draw: dr });
  });
  const run = o.pose === 'run', lean = run ? 14 : 0;
  const armB = o.armL || (run ? [[-34 - 20 * Math.sin((o.ph || 0) * 6.283), -188], [-14 - 40 * Math.sin((o.ph || 0) * 6.283), -160]] : [[-44, -176], [-46, -130]]);
  const armF = o.armR || (run ? [[34 + 20 * Math.sin((o.ph || 0) * 6.283), -188], [20 + 40 * Math.sin((o.ph || 0) * 6.283), -160]] : [[44, -176], [46, -130]]);
  part(C, T(tube([[-26 + lean, -218], ...armB], 22, 18)), shirt, L(30));
  part(C, T(handCircle(armB[1][0], armB[1][1], 11, sd + 31, 0, 16)), skin, L(31, { w: 4.5 }));
  // body: a soft trapezoid shirt
  const body = smooth([[-36 + lean, -224], [36 + lean, -224], [34, -170], [30, -122], [-30, -122], [-34, -170]], 4);
  part(C, T(body), shirt, L(32));
  // head
  const hx = lean + 2, hy = -262;
  if (o.hairStyle === 'long') part(C, T(smooth([[hx - 40, hy - 10], [hx - 36, hy - 44], [hx, hy - 52], [hx + 36, hy - 44], [hx + 42, hy - 6], [hx + 40, hy + 46], [hx - 42, hy + 48]], 5)), hair, L(40));
  part(C, T(ellipse(hx, hy, 32, 34, 30)), skin, L(41));
  if (o.hairStyle === 'cap') {
    part(C, T(smooth([[hx - 36, hy - 4], [hx - 32, hy - 34], [hx, hy - 44], [hx + 32, hy - 34], [hx + 36, hy - 6]], 4)), { ...hair, col: o.capCol || K.red }, L(42));
    part(C, T([[hx + 20, hy - 10], [hx + 66, hy - 4], [hx + 64, hy + 4], [hx + 20, hy + 2]]), { ...hair, col: o.capCol || K.red }, L(43));
  } else if (o.hairStyle === 'curly') {
    for (let i = 0; i < 7; i++) { const a = Math.PI * (1.05 + i * 0.15); part(C, T(handCircle(hx + 30 * Math.cos(a), hy + 30 * Math.sin(a), 15, sd + 50 + i, 0, 14)), hair, L(50 + i, { w: 4 })); }
  } else if (o.hairStyle !== 'bald') {
    part(C, T(smooth([[hx - 34, hy - 2], [hx - 30, hy - 30], [hx - 6, hy - 40], [hx + 24, hy - 36], [hx + 36, hy - 12], [hx + 20, hy - 22], [hx - 4, hy - 24], [hx - 22, hy - 16]], 4)), hair, L(44));
    if (o.hairStyle === 'bun') part(C, T(handCircle(hx - 4, hy - 50, 16, sd + 45, 0, 18)), hair, L(45));
  }
  // a simple face: two dots and a small smile (or closed eyes)
  if (dr > 0.6) {
  if (o.pose === 'sleep' || o.eyes === 'closed') { line(C.l, T([[hx - 16, hy - 2], [hx - 10, hy + 2], [hx - 4, hy - 2]]), L(46, { w: 4 })); line(C.l, T([[hx + 6, hy - 2], [hx + 12, hy + 2], [hx + 18, hy - 2]]), L(47, { w: 4 })); }
  else { dab(C.l, ...T([[hx - 11 + 4 * k * 0, hy - 4]])[0], 4.5 * s, { col: K.ink, p: 1, seed: sd + 46 }); dab(C.l, ...T([[hx + 11, hy - 4]])[0], 4.5 * s, { col: K.ink, p: 1, seed: sd + 47 }); }
  if (o.mouth !== false) line(C.l, T(o.mouth === 'o' ? handCircle(hx + 2, hy + 16, 5, sd, 0, 10) : [[hx - 8, hy + 13], [hx + 2, hy + 18], [hx + 12, hy + 13]]), L(48, { w: 4 }));
  dab(C.f, ...T([[hx - 20, hy + 8]])[0], 7 * s, { col: K.pink, p: 0.5, seed: sd + 49 }); dab(C.f, ...T([[hx + 22, hy + 8]])[0], 7 * s, { col: K.pink, p: 0.5, seed: sd + 59 });
  }
  // front arm
  part(C, T(tube([[26 + lean, -218], ...armF], 22, 18)), shirt, L(60));
  part(C, T(handCircle(armF[1][0], armF[1][1], 11, sd + 61, 0, 16)), skin, L(61, { w: 4.5 }));
  if (o.prop) o.prop(C, T, armF[1], armB[1]);
  return T;
}

// side-view shoe outline (toe to +x), sole at y
export function shoeSide(x, y, s = 1) {
  return smooth([[x - 18 * s, y + 4 * s], [x - 20 * s, y - 14 * s], [x - 8 * s, y - 20 * s], [x + 8 * s, y - 14 * s], [x + 28 * s, y - 8 * s], [x + 34 * s, y + 2 * s], [x + 30 * s, y + 6 * s]], 3);
}
// the loose crayon curve: a tick that starts fat at the left and trails off to the upper right
export function tickPts(x, y, s = 1, wob = 0) {
  return curve([[x - 120 * s, y - 34 * s], [x - 96 * s, y + 8 * s + wob], [x - 50 * s, y + 18 * s], [x + 40 * s, y - 6 * s - wob], [x + 140 * s, y - 52 * s]], 8);
}
export function tick(L, x, y, s, o = {}) {
  line(L, tickPts(x, y, s, o.wob || 0), { w: o.w ?? 14, col: o.col ?? K.orange, p: o.p ?? 0.95, seed: o.seed ?? 70, draw: o.draw ?? 1, taper: 0.5 });
}
// a big side-view running shoe (lace-up, 1970s shape), toe pointing right; returns the side panel centre
export function shoe(C, x, y, s, o = {}) {
  const T = pts => xf(pts, { x, y, s });
  const dr = o.draw ?? 1, fd = o.fillDraw ?? dr, sd = o.seed || 900;
  const upper = smooth([[-210, 0], [-218, -70], [-200, -120], [-150, -126], [-120, -100], [-40, -96], [40, -80], [140, -52], [210, -24], [222, 0]], 5);
  const sole = [[-224, -6], [228, -6], [236, 12], [200, 30], [-210, 30], [-230, 14]];
  part(C, T(sole), { col: o.sole || K.white, p: 0.9, gap: 6, w: 8, seed: sd, draw: fd }, { w: 6, seed: sd + 1, draw: dr });
  part(C, T(upper), o.col ? { col: o.col, p: 0.7, gap: 8, w: 10, ang: 0.4, seed: sd + 2, draw: fd } : null, { w: 6, seed: sd + 3, draw: dr });
  line(C.l, T([[-120, -100], [-80, -60], [-10, -50], [60, -64]]), { w: 4.5, seed: sd + 4, draw: dr, p: 0.8 });
  for (let i = 0; i < 4; i++) line(C.l, T([[-96 + i * 26, -96 + i * 4], [-70 + i * 26, -66 + i * 3]]), { w: 4, seed: sd + 5 + i, draw: dr, p: 0.8 });
  return [x - 10 * s, y - 40 * s];
}
// shoebox (front view)
export function box(C, x, y, w, h, col, sd, dr = 1) {
  part(C, [[x, y - h], [x + w, y - h], [x + w, y], [x, y]], { col, p: 0.75, gap: 8, w: 10, ang: 0.2, seed: sd, draw: dr }, { w: 5, seed: sd + 1, draw: dr });
  part(C, [[x - 6, y - h - 18], [x + w + 6, y - h - 18], [x + w + 6, y - h + 4], [x - 6, y - h + 4]], { col, p: 0.95, gap: 6, w: 8, ang: 0.2, seed: sd + 2, draw: dr }, { w: 5, seed: sd + 3, draw: dr });
}
// paper sheet (cream card) with slight rotation
export function card(C, x, y, w, h, r, sd, o = {}) {
  const P = xf([[-w / 2, -h / 2], [w / 2, -h / 2 + 3], [w / 2 - 2, h / 2], [-w / 2 + 2, h / 2 - 2]], { x, y, r });
  part(C, P, o.col ? { col: o.col, p: o.p ?? 0.35, gap: 9, w: 11, seed: sd, draw: o.draw ?? 1 } : null, { w: 4.5, seed: sd + 1, draw: o.draw ?? 1, p: 0.85 });
  if (o.pin) { const [px, py] = xf([[0, -h / 2 + 12]], { x, y, r })[0]; fill(C.l, handCircle(px, py, 10, sd + 2, 0, 14), { col: o.pin, p: 1, gap: 3, w: 5, seed: sd + 3 }); }
  return P;
}
// small sprout in a pot: g = growth 0..1
export function sprout(C, x, y, s, g, sd = 990) {
  part(C, xf([[-40, -50], [40, -50], [30, 0], [-30, 0]], { x, y, s }), { col: K.orange, p: 0.8, gap: 7, w: 9, seed: sd }, { w: 5, seed: sd + 1 });
  if (g <= 0) return;
  const h = 120 * g;
  line(C.l, xf([[0, -50], [4, -50 - h * 0.5], [0, -50 - h]], { x, y, s }), { w: 6, col: K.green, p: 1, seed: sd + 2 });
  if (g > 0.4) {
    const q = clamp((g - 0.4) / 0.6);
    part(C, xf(smooth([[0, -50 - h], [-40 * q, -70 - h - 10 * q], [-70 * q, -50 - h], [-30 * q, -40 - h]], 4), { x, y, s }), { col: K.green, p: 0.85, gap: 6, w: 8, seed: sd + 3 }, { w: 5, seed: sd + 4 });
    part(C, xf(smooth([[0, -60 - h * 0.7], [40 * q, -80 - h * 0.7 - 10 * q], [70 * q, -60 - h * 0.7], [30 * q, -50 - h * 0.7]], 4), { x, y, s }), { col: K.green, p: 0.85, gap: 6, w: 8, seed: sd + 5 }, { w: 5, seed: sd + 6 });
  }
}
// clock face with hands at angle a (radians) for the minute hand
export function clock(C, x, y, r, a, sd = 960, dr = 1) {
  part(C, handCircle(x, y, r, sd, 0.05, 40), { col: K.white, p: 0.9, gap: 6, w: 8, seed: sd + 1, draw: dr }, { w: 6, seed: sd + 2, draw: dr });
  for (let i = 0; i < 12; i++) { const b = i / 12 * Math.PI * 2; line(C.l, [[x + Math.cos(b) * r * 0.82, y + Math.sin(b) * r * 0.82], [x + Math.cos(b) * r * 0.92, y + Math.sin(b) * r * 0.92]], { w: 4, seed: sd + 3 + i, draw: dr }); }
  line(C.l, [[x, y], [x + Math.cos(a - 1.57) * r * 0.75, y + Math.sin(a - 1.57) * r * 0.75]], { w: 6, seed: sd + 20, draw: dr });
  line(C.l, [[x, y], [x + Math.cos(a / 12 - 1.57) * r * 0.5, y + Math.sin(a / 12 - 1.57) * r * 0.5]], { w: 7, seed: sd + 21, draw: dr });
}
// pine tree
export function pine(C, x, y, s, sd, dr = 1) {
  part(C, xf([[0, -260], [70, -110], [40, -110], [90, -20], [-90, -20], [-40, -110], [-70, -110]], { x, y, s }), { col: K.green, p: 0.75, gap: 8, w: 10, ang: 1.2, seed: sd, draw: dr }, { w: 5, seed: sd + 1, draw: dr, col: K.green });
  part(C, xf([[-12, -20], [12, -20], [12, 20], [-12, 20]], { x, y, s }), { col: K.brown, p: 0.85, gap: 6, w: 8, seed: sd + 2, draw: dr }, { w: 4, seed: sd + 3, draw: dr });
}
// speech/thought bubble outline (cloud if thought)
export function bubble(C, x, y, w, h, sd, o = {}) {
  let P;
  if (o.cloud) { P = []; for (let i = 0; i <= 64; i++) { const a = i / 64 * Math.PI * 2; const bump = 1 + 0.08 * Math.abs(Math.sin(a * 5)); P.push([x + Math.cos(a) * w / 2 * bump, y + Math.sin(a) * h / 2 * bump]); } }
  else P = smooth([[x - w / 2, y - h / 2], [x + w / 2, y - h / 2], [x + w / 2, y + h / 2], [x - w / 2 + 60, y + h / 2], ...(o.tail ? [o.tail] : []), [x - w / 2 + 30, y + h / 2], [x - w / 2, y + h / 2]], 3);
  part(C, P, { col: K.white, p: 0.85, gap: 6, w: 8, seed: sd, draw: o.draw ?? 1 }, { w: 5, seed: sd + 1, draw: o.draw ?? 1 });
  if (o.cloud && o.tail) o.tail.forEach(([tx, ty, tr], i) => part(C, handCircle(tx, ty, tr, sd + 5 + i, 0, 16), { col: K.white, p: 0.85, gap: 5, w: 7, seed: sd + 8 + i }, { w: 4.5, seed: sd + 12 + i, draw: o.draw ?? 1 }));
}
