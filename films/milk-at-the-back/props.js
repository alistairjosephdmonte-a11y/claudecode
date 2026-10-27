// Paper-supermarket props in the toon line: boiling ink outlines, flat fills, a white cut-paper rim, a hard paper shadow.
import { clamp, lerp, hash, TAU } from '/core/lib.js';
import { g, push, pop, translate, rotate, scale, shape, fillOnly, stroke, ell, arc, rr, rect, spline, quad, dot, S, tx, zoom } from './toon.js';

// palette (brief) + paper tints; sepia swaps everything but the coral marker
export const BASE = { milk: '#F7F3EA', blue: '#2F6FD0', glow: '#BFE6FF', coral: '#FF5A4E', ink: '#1B1B1B', card: '#ECE5D6', card2: '#DED5C3', shadow: 'rgba(27,27,27,.16)', navy: '#22355E', blueDk: '#24579F', floor: '#E9E2D2', grey: '#B9B3A6' };
export const SEPIA = { milk: '#E8D3B4', blue: '#8A6440', glow: '#D9BE96', coral: '#FF5A4E', ink: '#3E2A1B', card: '#D8BC94', card2: '#C9A27A', shadow: 'rgba(62,42,27,.2)', navy: '#5A3F28', blueDk: '#6E4E30', floor: '#D2B48C', grey: '#A88A66' };
export let P = { ...BASE };
export function setPal(k) { P = k >= 1 ? { ...SEPIA } : k <= 0 ? { ...BASE } : mix(BASE, SEPIA, k); S.ink = P.ink; }
function hex(c) { const n = parseInt(c.slice(1), 16); return [n >> 16, n >> 8 & 255, n & 255]; }
function mix(A, B, k) { const o = {}; for (const key in A) { if (A[key][0] !== '#') { o[key] = k < .5 ? A[key] : B[key]; continue; } const a = hex(A[key]), b = hex(B[key]); o[key] = `rgb(${a.map((v, i) => Math.round(lerp(v, b[i], k))).join(',')})`; } return o; }

// a cut-paper card: shadow, white rim, fill, ink line
export function card(pts, fill, o = {}) {
  if (o.shadow !== false) { push(); translate(o.sx ?? 7, o.sy ?? 9); fillOnly(pts, P.shadow, { boil: 0 }); pop(); }
  if (o.rim !== false) shape(pts, { fill: null, line: o.rimCol ?? '#FFFDF8', lw: (o.lw ?? 6) + 10, boil: 1.4 });
  return shape(pts, { fill, lw: o.lw ?? 6, line: o.line ?? P.ink, shade: o.shade, boil: o.boil });
}
const hard = (pts, col) => () => fillOnly(pts, col, { boil: .6 });

// ---- the hero carton: white, dairy-blue gable top, small cow patch, no logo ----
export function carton(x, y, s = 1, o = {}) {
  push(); translate(x, y); scale(s); if (o.rot) rotate(o.rot);
  const w = 60, h = 110, top = 46;
  if (o.glow) { for (const [r, a] of [[1.9, .18], [1.45, .28]]) fillOnly(ell(0, -h - top * .6, w * r, top * r * .9), P.glow, { alpha: a * o.glow, boil: .4 }); }
  card(rect(-w, -h, w * 2, h), P.milk, { shade: hard(rect(w * .35, -h, w * .65, h), P.card) });
  card([[-w, -h], [0, -h - top], [w, -h], [w, -h + 12], [-w, -h + 12]], P.blue, { shade: hard([[0, -h - top], [w, -h], [w, -h + 12], [0, -h + 12]], P.blueDk) });
  card(rect(-10, -h - top - 16, 20, 18), P.blue, { shadow: false });   // folded peak (fin)
  card(spline([[-w * .62, -h * .52], [-w * .1, -h * .6], [-w * .02, -h * .38], [-w * .38, -h * .28], [-w * .66, -h * .34]]), P.ink, { shadow: false, rim: false, lw: 3 });   // cow patch
  fillOnly(ell(-w * .32, -h * .44, 7, 5), P.milk);
  pop();
}
// the gap in the basket: a dashed carton outline
export function cartonGap(x, y, s, filled) {
  push(); translate(x, y); scale(s);
  if (!filled) { g.save(); g.setLineDash([10, 9]); stroke([[-60, 0], [-60, -110], [0, -156], [60, -110], [60, 0]], 4, { line: P.ink, boil: .5 }); g.restore(); }
  pop();
}

// ---- the shopper: faceless cut-out, navy coat ----
export function shopper(x, y, s = 1, o = {}) {
  const ph = o.walk ?? null, face = o.face ?? 1;
  push(); translate(x, y); scale(s * face, s);
  const sw = ph == null ? 0 : Math.sin(ph) * 16, lift = ph == null ? 0 : Math.abs(Math.cos(ph)) * 4;
  for (const [k, d] of [[-1, sw], [1, -sw]]) card(spline([[k * 14 - 6, -150], [k * 14 + 6, -150], [k * 12 + d + 7, -4], [k * 12 + d - 7, -4]], true, 4), P.ink, { shadow: false, lw: 5 });
  card(spline([[-34, -265], [34, -265], [46, -140], [-46, -140]], true, 5), P.navy, { shade: hard([[10, -265], [34, -265], [46, -140], [20, -140]], 'rgba(0,0,0,.22)') });
  card(ell(0, -300, 26, 32), P.milk, { shade: hard(ell(12, -296, 20, 30), P.card) });   // no features, ever
  const armA = o.reach ? -1.2 : (ph == null ? .15 : Math.sin(ph) * .3);
  push(); translate(26, -250); rotate(armA); card(rr(-9, 0, 18, 92, 9), P.navy, { shadow: false, lw: 5 }); fillOnly(ell(0, 96, 9, 9), P.milk); pop();
  if (o.basket) { push(); translate(34 + Math.sin(armA) * 80, -150 + (1 - Math.cos(armA)) * 30); scale(.55); basket(0, 0, 1, o.items || [], o.filled); pop(); }
  pop();
}

// ---- the woven paper basket with a carton-shaped gap ----
export const ITEM = {
  biscuits: (x, y) => { card(rr(x - 32, y - 40, 64, 40, 8), P.glow, { shadow: false, lw: 4 }); for (let i = 0; i < 3; i++) fillOnly(ell(x - 16 + i * 16, y - 20, 7, 7), P.card2); },
  candle: (x, y) => { card(rect(x - 12, y - 62, 24, 62), P.milk, { shadow: false, lw: 4 }); card(spline([[x, y - 88], [x + 8, y - 72], [x, y - 64], [x - 8, y - 72]]), P.glow, { shadow: false, lw: 3 }); },
  chicken: (x, y) => { card(spline([[x - 40, y], [x - 44, y - 30], [x - 10, y - 50], [x + 34, y - 40], [x + 42, y - 10], [x + 30, y]]), P.card2, { shadow: false, lw: 4 }); card(rr(x + 30, y - 52, 26, 12, 6), P.milk, { shadow: false, lw: 3 }); },
  flowers: (x, y) => { stroke([[x, y], [x - 6, y - 70]], 4); stroke([[x, y], [x + 10, y - 60]], 4); for (const [a, b] of [[-6, -76], [10, -66]]) { for (let k = 0; k < 5; k++) fillOnly(ell(x + a + Math.cos(k / 5 * TAU) * 9, y + b + Math.sin(k / 5 * TAU) * 9, 7, 7), P.milk); dot(x + a, y + b, 5, P.blue); } },
  baguette: (x, y) => { push(); translate(x, y - 40); rotate(-.9); card(rr(-70, -12, 140, 24, 12), P.card2, { shadow: false, lw: 4 }); for (let i = -2; i <= 2; i++) stroke([[i * 24 - 6, -6], [i * 24 + 6, 6]], 3); pop(); },
  cereal: (x, y) => { card(rect(x - 26, y - 80, 52, 80), P.blue, { shadow: false, lw: 4 }); card(ell(x, y - 46, 14, 14), P.glow, { shadow: false, lw: 3 }); },
  jar: (x, y) => { card(rr(x - 22, y - 50, 44, 50, 10), P.glow, { shadow: false, lw: 4 }); card(rect(x - 24, y - 62, 48, 12), P.blue, { shadow: false, lw: 3 }); },
  chips: (x, y) => { card(spline([[x - 28, y], [x - 30, y - 64], [x, y - 70], [x + 30, y - 64], [x + 28, y]], true, 4), P.milk, { shadow: false, lw: 4 }); stroke([[x - 20, y - 30], [x + 20, y - 40]], 4, { line: P.blue }); },
  tin: (x, y) => { card(rect(x - 20, y - 46, 40, 46), P.grey, { shadow: false, lw: 4 }); stroke([[x - 20, y - 26], [x + 20, y - 26]], 3); },
  eggs: (x, y) => { card(rr(x - 40, y - 30, 80, 30, 6), P.card, { shadow: false, lw: 4 }); for (let i = 0; i < 3; i++) card(ell(x - 24 + i * 24, y - 34, 11, 13), P.milk, { shadow: false, lw: 3 }); },
  loaf: (x, y) => { card(spline([[x - 46, y], [x - 50, y - 36], [x - 20, y - 54], [x + 20, y - 54], [x + 50, y - 36], [x + 46, y]], true, 4), P.card2, { shadow: false, lw: 4 }); for (let i = -1; i <= 1; i++) stroke([[x + i * 22 - 6, y - 46], [x + i * 22 + 6, y - 30]], 3); },
};
// what's in the basket, by the scene it went in
export const BASKET = [[5, 'biscuits'], [5, 'candle'], [5, 'chicken'], [5, 'flowers'], [12, 'tin'], [27, 'baguette'], [28, 'cereal'], [28, 'chips'], [28, 'jar']];
export function basket(x, y, s = 1, items = [], filled = false) {
  push(); translate(x, y); scale(s);
  // handle
  stroke(arc(0, -120, 120, 110, Math.PI * 1.05, Math.PI * 1.95, 20), 10, { line: P.ink }); stroke(arc(0, -120, 120, 110, Math.PI * 1.05, Math.PI * 1.95, 20), 4, { line: P.card });
  // contents behind the front weave
  const slots = [-110, -55, 55, 110, -80, 80, -130, 130, 0];
  items.forEach((k, i) => { if (ITEM[k]) ITEM[k](slots[i % slots.length], -98 - (i > 3 ? 18 : 0)); });
  if (filled) carton(0, -60, .62); else cartonGap(0, -70, .62, false);
  card([[-160, -110], [160, -110], [130, 0], [-130, 0]], P.card, { shade: () => { for (let i = 0; i < 6; i++) fillOnly(rect(-170 + i * 60, -110, 26, 120), P.card2, { boil: .3 }); } });
  for (let r = 0; r < 3; r++) stroke([[-155 + r * 10, -80 + r * 30], [155 - r * 10, -80 + r * 30]], 3, { line: P.grey });
  pop();
}

// ---- the balance scale: a refrigerated truck vs a coral price-tag gun ----
export function balance(x, y, s, tilt) {
  push(); translate(x, y); scale(s);
  card(rr(-70, -10, 140, 30, 10), P.card2);
  card(rect(-10, -330, 20, 322), P.card);
  card(ell(0, -340, 22, 22), P.blue);
  push(); translate(0, -335); rotate(tilt);
  card(rr(-320, -8, 640, 16, 8), P.card);
  for (const [sx, what] of [[-1, 'truck'], [1, 'gun']]) {
    push(); translate(sx * 300, 0); rotate(-tilt);
    stroke([[-90, 120], [0, 0], [90, 120]], 4); card(spline([[-120, 120], [120, 120], [90, 150], [-90, 150]], true, 3), P.card);
    if (what === 'truck') truck(0, 120, .5); else priceGun(0, 118, .9);
    pop();
  }
  pop(); pop();
}
export function truck(x, y, s = 1, o = {}) {
  push(); translate(x, y); scale(s * (o.face ?? 1), s);
  card(rr(-200, -190, 290, 170, 10), P.milk, { shade: hard(rect(-200, -60, 290, 40), P.card) });
  for (let i = 0; i < 5; i++) stroke([[-180 + i * 56, -176], [-170 + i * 56, -150]], 3, { line: P.glow });   // frost
  card(spline([[-150, -170], [-120, -176], [-90, -166], [-60, -178]], false), null, { shadow: false, rim: false, lw: 0 });
  fillOnly(rr(-196, -188, 282, 14, 7), P.glow);
  card(rr(96, -150, 110, 130, 18), P.blue, { shade: hard(rect(150, -150, 56, 130), P.blueDk) });
  card(rr(120, -134, 64, 48, 8), P.glow, { shadow: false, lw: 4 });
  for (const wx of [-140, 20, 160]) { card(ell(wx, -14, 30, 30), P.ink, { shadow: false, lw: 4 }); fillOnly(ell(wx, -14, 11, 11), P.grey); }
  pop();
}
export function priceGun(x, y, s = 1) {
  push(); translate(x, y); scale(s);
  card(spline([[-70, -90], [60, -96], [74, -60], [-40, -54]], true, 4), P.coral);
  card(rr(-36, -64, 34, 70, 12), P.coral, { shadow: false });
  card(rect(52, -98, 44, 24), P.milk, { shadow: false, lw: 4 });   // a blank tag
  pop();
}

// ---- store pieces ----
export function shelfUnit(x, y, w, h, o = {}) {   // front-on shelving with blank products
  card(rect(x, y - h, w, h), o.col ?? P.card, { shade: hard(rect(x, y - h, w, 18), P.card2) });
  const rows = o.rows ?? 4, R = o.seed ?? 1;
  for (let r = 0; r < rows; r++) {
    const yy = y - h + (r + 1) * h / rows;
    fillOnly(rect(x, yy - 8, w, 8), P.card2);
    if (o.empty) continue;
    let px = x + 10; let i = 0;
    while (px < x + w - 30) { const pw = 26 + hash(R * 9 + r * 31 + i) * 30, ph = h / rows * (.5 + hash(R + r * 7 + i * 3) * .35), c = [P.blue, P.milk, P.glow, P.card2, P.milk][Math.floor(hash(R * 3 + i + r * 11) * 5)];
      if (px + pw > x + w - 8) break; fillOnly(rr(px, yy - 8 - ph, pw, ph, 4), c, { boil: .5 }); stroke(rr(px, yy - 8 - ph, pw, ph, 4).concat([[px, yy - 8 - ph + 4]]), 3, { line: P.ink, boil: .5 }); px += pw + 8; i++; }
  }
}
export function fridgeWall(x, y, w, h, o = {}) {   // the dairy wall: glass doors in a cold-room face
  const glow = o.glow ?? 1, n = o.doors ?? Math.max(2, Math.round(w / 170));
  if (glow) fillOnly(rect(x - 30, y - h - 30, w + 60, h + 60), P.glow, { alpha: .35 * glow, boil: .3 });
  card(rect(x, y - h, w, h), P.blue, { shade: hard(rect(x, y - h, w, 30), P.blueDk) });
  const dw = (w - 30) / n;
  for (let i = 0; i < n; i++) {
    const dx = x + 15 + i * dw;
    card(rect(dx + 6, y - h + 40, dw - 12, h - 56), P.glow, { shadow: false, lw: 5 });
    for (let r = 0; r < 3; r++) for (let k = 0; k < 3; k++) { const cx = dx + 6 + (k + .5) * (dw - 12) / 3, cy = y - h + 40 + (r + 1) * (h - 56) / 3 - 6; fillOnly(rect(cx - 12, cy - 34, 24, 34), P.milk, { boil: .4 }); fillOnly([[cx - 12, cy - 34], [cx, cy - 46], [cx + 12, cy - 34]], P.blue, { boil: .4 }); }
    stroke([[dx + dw - 22, y - h * .6], [dx + dw - 22, y - h * .4]], 6, { line: P.milk });
  }
}
export function door(x, y, open, s = 1) {   // paper double doors (open 0..1)
  push(); translate(x, y); scale(s);
  card(rect(-150, -330, 300, 330), P.card2);
  fillOnly(rect(-130, -310, 260, 310), P.glow, { alpha: .9 });
  for (const k of [-1, 1]) { push(); translate(k * 130, 0); scale(1 - open * .85, 1); card(rect(k < 0 ? 0 : -130, -310, 130, 310), P.milk, { shadow: false, shade: hard(rect(k < 0 ? 100 : -130, -310, 30, 310), P.card) }); pop(); }
  pop();
}
export function floorPlan(o = {}) {   // top-down: store box, aisles, dairy wall along the top (back), door at the bottom
  const X = o.x ?? -700, Y = o.y ?? -420, Wd = o.w ?? 1400, Hd = o.h ?? 840;
  card(rect(X, Y, Wd, Hd), P.floor);
  const aisles = o.aisles ?? 6;
  for (let i = 0; i < aisles; i++) { const ax = X + 220 + i * (Wd - 440) / (aisles - 1) - 30; card(rect(ax, Y + 200, 60, Hd - 380), P.card, { lw: 4, sx: 4, sy: 5 }); }
  if (o.dairy !== false) card(rect(X + 60, Y + 20, Wd - 120, 50), P.blue, { lw: 5 });
  if (o.door !== false) { fillOnly(rect(X + Wd / 2 - 70, Y + Hd - 10, 140, 20), P.glow); stroke([[X + Wd / 2 - 70, Y + Hd], [X + Wd / 2 - 70, Y + Hd - 40]], 5); stroke([[X + Wd / 2 + 70, Y + Hd], [X + Wd / 2 + 70, Y + Hd - 40]], 5); }
  return { X, Y, Wd, Hd };
}
export function tinyShopper(x, y, s = 1, ph = 0) {   // top-down dot-person: navy coat circle + milk head
  push(); translate(x, y); scale(s); fillOnly(ell(2, 4, 14, 14), P.shadow); card(ell(0, 0, 13, 13), P.navy, { shadow: false, lw: 4 }); fillOnly(ell(0, -2 + Math.sin(ph) * 1.5, 6, 6), P.milk); pop();
}
// produce, ice, clerks, cars: small pieces used by several scenes
export function fruitPile(x, y, s, col) {
  push(); translate(x, y); scale(s);
  const rows = [5, 4, 3, 2, 1]; let k = 0;
  rows.forEach((n, r) => { for (let i = 0; i < n; i++) card(ell((i - (n - 1) / 2) * 34, -18 - r * 28, 18, 18), [col, P.milk, P.glow][(k++) % 3 === 0 ? 0 : (k % 3)], { shadow: false, lw: 4, rim: false }); });
  pop();
}
export function iceBlock(x, y, s, melt = 0) {
  push(); translate(x, y); scale(s, s * (1 - melt * .5));
  card(rr(-70, -120, 140, 120, 14), P.glow, { shade: hard(rect(20, -120, 50, 120), 'rgba(255,255,255,.5)') });
  for (let i = 0; i < 3; i++) stroke([[-40 + i * 30, -100], [-30 + i * 30, -70]], 3, { line: P.milk });
  pop();
  if (melt > 0) fillOnly(ell(x, y + 4, 80 + melt * 60, 10), P.glow, { alpha: .8 });
}
export function silhouette(x, y, s, o = {}) {   // a historical figure: solid silhouette in a hat
  push(); translate(x, y); scale(s * (o.face ?? 1), s);
  const C = o.col ?? P.ink;
  fillOnly(spline([[-40, 0], [-44, -170], [-30, -250], [30, -250], [44, -170], [40, 0]], true, 4), C);
  fillOnly(ell(0, -290, 30, 36), C); fillOnly(rect(-44, -322, 88, 10), C); fillOnly(rr(-28, -366, 56, 50, 6), C);
  pop();
}
export function car(x, y, s, col) {
  push(); translate(x, y); scale(s);
  card(spline([[-90, -20], [-80, -60], [-40, -90], [40, -90], [70, -60], [100, -50], [100, -20]], true, 4), col ?? P.blue, { lw: 5 });
  fillOnly(spline([[-34, -80], [30, -80], [56, -58], [-60, -58]], true, 3), P.glow);
  for (const wx of [-55, 60]) { card(ell(wx, -18, 20, 20), P.ink, { shadow: false, lw: 4 }); fillOnly(ell(wx, -18, 7, 7), P.grey); }
  pop();
}
export function fridge30s(x, y, s, open = 0) {   // a 1930s monitor-top fridge
  push(); translate(x, y); scale(s);
  card(rr(-70, -260, 140, 260, 20), P.milk, { shade: hard(rect(30, -260, 40, 260), P.card) });
  card(ell(0, -280, 50, 26), P.card2); card(rect(-20, -300, 40, 20), P.card2, { shadow: false });
  if (open) { fillOnly(rect(-62, -246, 124, 220), P.glow); push(); translate(-70, 0); scale(1 - open * .8, 1); card(rr(0, -256, 140, 252, 18), P.milk, { shadow: false }); pop(); }
  stroke([[50, -180], [50, -140]], 8, { line: P.grey });
  pop();
}
export function bottle(x, y, s = 1) {
  push(); translate(x, y); scale(s);
  card(spline([[-22, 0], [-24, -60], [-12, -80], [-12, -100], [12, -100], [12, -80], [24, -60], [22, 0]], true, 4), P.milk, { lw: 4, sx: 4, sy: 4 });
  fillOnly(rect(-13, -104, 26, 10), P.blue);
  pop();
}
export function float_(x, y, s, o = {}) {   // electric milk float (o.horse: the older horse cart)
  push(); translate(x, y); scale(s * (o.face ?? 1), s);
  card(rect(-150, -150, 240, 110), P.milk, { shade: hard(rect(-150, -60, 240, 20), P.card) });
  card(rect(-160, -168, 260, 20), P.blue);
  for (let i = 0; i < 6; i++) bottle(-125 + i * 38, -50, .5);
  card(rr(90, -130, 70, 90, 10), P.blue);
  for (const wx of [-110, 50]) { card(ell(wx, -30, 28, 28), P.ink, { shadow: false, lw: 4 }); fillOnly(ell(wx, -30, 10, 10), P.grey); }
  if (o.horse) { push(); translate(250, 0); card(spline([[-60, -60], [-60, -130], [40, -140], [90, -200], [120, -180], [70, -110], [60, -60]], true, 4), P.card2); for (const lx of [-50, 40]) card(rect(lx, -64, 14, 64), P.card2, { shadow: false, lw: 4 }); pop(); }
  pop();
}
export function turnstile(x, y, s, ang = 0) {
  push(); translate(x, y); scale(s);
  card(rr(-24, -170, 48, 170, 10), P.card2);
  push(); translate(0, -130); for (let i = 0; i < 3; i++) { push(); rotate(ang + i * TAU / 3); card(rr(0, -8, 110, 16, 8), P.grey, { shadow: false, lw: 4 }); pop(); } card(ell(0, 0, 22, 22), P.blue, { shadow: false }); pop();
  pop();
}
export function coin(x, y, s) { push(); translate(x, y); scale(s); card(ell(0, 0, 30, 30), P.card2, { lw: 5, sx: 3, sy: 4 }); stroke(ell(0, 0, 18, 18), 3, { line: P.grey }); pop(); }
export function globe(x, y, r, spin) {
  card(ell(x, y, r, r), P.glow);
  for (let i = 0; i < 5; i++) { const a = spin + i * 1.3; const cx = x + Math.sin(a) * r * .7; if (Math.cos(a) < 0) continue; fillOnly(spline([[cx - 40, y - 60 + i * 20], [cx + 30, y - 70 + i * 24], [cx + 40, y - 10 + i * 10], [cx - 30, y + 20]]).map(p => [p[0], p[1]]), P.card, { alpha: .9 }); }
  stroke(ell(x, y, r, r), 6);
}
export function house(x, y, s, lit = 0) {
  push(); translate(x, y); scale(s);
  card(rect(-60, -100, 120, 100), P.card);
  card([[-74, -98], [0, -160], [74, -98]], P.card2, { shadow: false });
  card(rect(-34, -76, 30, 30), lit ? P.glow : P.card2, { shadow: false, lw: 4 }); card(rect(8, -76, 30, 30), lit ? P.glow : P.card2, { shadow: false, lw: 4 });
  if (lit) fillOnly(ell(0, -60, 70, 50), P.glow, { alpha: .25 * lit });
  pop();
}
export { hard };
