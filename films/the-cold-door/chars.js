// The cast (original): HAL — tall, deadpan, lives in an orange freezer parka with the hood up and teal oven mitts;
// DOT — short night-shift shop assistant, two hair buns, raspberry apron, a paper basket that keeps filling;
// CURD — a lumpy yoghurt blob with one eye. Feet at the origin, y down, face = 1 looks right (3/4), -1 mirrors.
import { clamp, lerp, hash, TAU } from '/core/lib.js';
import { INK, g, push, pop, translate, rotate, scale, shape, fillOnly, stroke, ell, arc, spline, rr, rect, noodle, quad, dot, S } from './toon.js';

export const C = {
  white: '#ffffff', mouthIn: '#4a1a2a', tongue: '#e8637a',
  parka: '#E07A2E', parkaS: '#B85A1C', fur: '#EFE3C8', furS: '#D3C3A0', skinH: '#EBC7A0', skinHs: '#CFA57C', stache: '#8E8A86', mitt: '#3AA6A0', mittS: '#2A7E79', pants: '#4A4E5A', boot: '#2B2D35',
  skinD: '#C58A5E', skinDs: '#A56E46', hair: '#3B2418', apron: '#C8326B', apronS: '#9E2252', shirt: '#F3E7C9', stripe: '#E3B341', legD: '#3A3F63', shoe: '#F7F3EA', shoeS: '#CFC7B5',
  curd: '#F4EEDC', curdS: '#E3D3A8',
  basket: '#D9B47A', basketS: '#B98F52',
};

export function eye(cx, cy, rx, ry, { lid = 0, look = [0, 0], pupil = 4.5, skin, closed = false, lw = 6, jitter = 0, lower = 0, wide = 1 } = {}) {
  if (closed) { stroke(arc(cx, cy + ry * .15, rx * .8, ry * .45, Math.PI * .1, Math.PI * .9, 14), lw); return; }
  rx *= wide; ry *= wide;
  shape(ell(cx, cy, rx, ry, 36), { fill: C.white, lw, shade: () => {
    dot(cx + look[0] * rx * .55 + jitter, cy + look[1] * ry * .5, pupil);
    if (lid > 0) { const yl = cy - ry + lid * 2 * ry; fillOnly([[cx - rx * 1.3, cy - ry * 1.4], [cx + rx * 1.3, cy - ry * 1.4], [cx + rx * 1.3, yl], [cx - rx * 1.3, yl + ry * .08]], skin, { boil: .5 }); stroke([[cx - rx * 1.2, yl + ry * .08], [cx + rx * 1.2, yl]], lw); }
    if (lower > 0) { const yb = cy + ry - lower * 2 * ry; fillOnly([[cx - rx * 1.3, yb], [cx + rx * 1.3, yb], [cx + rx * 1.3, cy + ry * 1.4], [cx - rx * 1.3, cy + ry * 1.4]], skin, { boil: .5 }); stroke([[cx - rx * 1.2, yb], [cx + rx * 1.2, yb]], lw * .8); }
  } });
}
export function mouth(cx, cy, mw, { o = 0, w = 1, sm = 0, skew = 0, lw = 6, teeth = true } = {}) {
  const hw = mw * w / 2, k = mw * .22, lc = [cx - hw, cy - sm * k + skew * k], rc = [cx + hw, cy - sm * k - skew * k];
  if (o < .07) { stroke(quad(lc, [cx, cy + sm * k * 1.2], rc, 12), lw); return; }
  const h = o * mw * .62, up = quad(lc, [cx, cy - h * .25 + sm * k * .4], rc, 12), dn = quad(rc, [cx, cy + h + sm * k * .6], lc, 14);
  shape([...up, ...dn], { fill: C.mouthIn, lw, shade: () => {
    if (teeth && o > .22) fillOnly(rect(cx - hw * 1.2, cy - h, hw * 2.4, h * .3 + 6), C.white, { boil: .3 });
    fillOnly(ell(cx + hw * .15, cy + h * .95, hw * .6, h * .45, 20), C.tongue, { boil: .3 });
  } });
}
function hand(x, y, ang, r, col, lw = 6) {
  push(); translate(x, y); rotate(ang);
  shape(spline([[-r * .5, -r * .85], [r * .5, -r * 1.05], [r * 1.35, -r * .75], [r * 1.05, -r * .3], [r * 1.5, -r * .1], [r * 1.1, r * .3], [r * 1.35, r * .7], [r * .6, r * .95], [-r * .6, r * .8], [-r * .95, 0]]), { fill: col, lw });
  pop();
}
function mitt(x, y, ang, r) {
  push(); translate(x, y); rotate(ang);
  shape(spline([[-r, -r * .7], [r * .2, -r * 1.2], [r * 1.3, -r * .7], [r * 1.4, r * .5], [r * .4, r * 1.1], [-r * .9, r * .8]]), { fill: C.mitt, lw: 7, shade: () => fillOnly(ell(r * .7, r * .3, r * .9, r * .9), C.mittS, { boil: .3 }) });
  shape(spline([[-r * .6, -r * .5], [-r * 1.5, -r * 1.0], [-r * 1.6, -r * .2], [-r * .9, r * .2]]), { fill: C.mitt, lw: 7 });   // thumb
  pop();
}
const sweat = (x, y, s = 1) => shape(spline([[x, y - 16 * s], [x + 9 * s, y + 4 * s], [x, y + 12 * s], [x - 9 * s, y + 4 * s]]), { fill: '#bfe9ff', lw: 5 });
const ARMS = {   // [hand offset from shoulder (x, y), elbow bend] for the arm on the near side (R) and far side (L), face-relative
  rest: [[30, 170, 16], [-30, 170, -16]], point: [[190, 10, 20], [-30, 170, -16]], up: [[90, -150, -20], [-90, -150, 20]], shrug: [[110, 40, 40], [-110, 40, -40]],
  hold: [[60, 120, 30], [-60, 100, -30]], write: [[90, 70, 40], [-40, 110, -30]], face: [[30, -20, 60], [-30, -20, -60]], beg: [[60, 40, 40], [-20, 40, -40]], strain: [[40, 200, 6], [-40, 200, -6]], wave: [[100, -140, -30], [-30, 170, -16]],
};

// ---------- HAL ----------
export function hal(P) {
  const f = P.face ?? 1, m = P.mouth || {};
  push(); translate(P.x + (P.jit || 0), P.y); scale((P.s ?? 1) * f, (P.s ?? 1) * (P.sq ?? 1));
  const wk = P.walk ?? null, sw = wk == null ? 0 : Math.sin(wk) * 22;
  for (const [sx, d] of [[-1, sw], [1, -sw]]) {
    shape(noodle([sx * 24, -230], [sx * 26 + d, -30], sx * -4, 34, 30), { fill: C.pants, lw: 7 });
    shape(spline([[sx * 26 + d - 34, 0], [sx * 26 + d - 30, -36], [sx * 26 + d + 30, -36], [sx * 26 + d + 50, -6], [sx * 26 + d + 40, 4]]), { fill: C.boot, lw: 7 });
  }
  const A = ARMS[P.arms || 'rest'], sh = [[-70, -470], [70, -470]];
  // far arm behind the body
  { const [hx, hy, b] = A[1]; shape(noodle([-62, -470], [-62 + hx, -470 + hy], b, 52, 46), { fill: C.parkaS, lw: 7 }); mitt(-62 + hx, -470 + hy, -.3, 26); }
  // puffy parka body, quilted
  const body = spline([[-92, -500], [-60, -540], [60, -540], [92, -500], [104, -330], [96, -210], [-96, -210], [-104, -330]]);
  shape(body, { fill: C.parka, lw: 7, shade: () => { fillOnly(spline([[40, -540], [110, -500], [120, -220], [50, -210], [70, -360]]), C.parkaS, { boil: .3 }); for (let k = 0; k < 4; k++) stroke(quad([-104, -470 + k * 66], [0, -458 + k * 66], [104, -470 + k * 66], 10), 4, { line: C.parkaS }); } });
  stroke([[0, -540], [0, -214]], 5);
  // hood ring + fur
  const hb = P.tilt || 0; push(); translate(0, -600); rotate(hb);
  shape(ell(0, 0, 128, 142, 50), { fill: C.parka, lw: 7, shade: () => fillOnly(ell(60, 10, 90, 130), C.parkaS, { boil: .3 }) });
  shape(spline([[-104, 0], [-96, -76], [-60, -112], [0, -122], [60, -112], [96, -76], [104, 0], [96, 70], [60, 106], [0, 118], [-60, 106], [-96, 70]]), { fill: C.fur, lw: 6, shade: () => fillOnly(ell(40, 20, 70, 100), C.furS, { boil: .4 }) });
  shape(ell(8, 6, 76, 96, 40), { fill: C.skinH, lw: 6, shade: () => fillOnly(ell(58, 16, 40, 90), C.skinHs, { boil: .3 }) });
  // face: heavy lids, bags, a big grey moustache
  const lk = P.look || [.3, 0], lid = P.blink ? 1 : (P.lid ?? .5);
  eye(-16, -24, 26, 30, { lid, look: lk, skin: C.skinH, jitter: P.ejit || 0, wide: P.wide || 1 }); eye(40, -24, 24, 29, { lid, look: lk, skin: C.skinH, jitter: P.ejit || 0, wide: P.wide || 1 });
  stroke(arc(-16, 14, 20, 8, .2, Math.PI - .2, 10), 4); stroke(arc(40, 14, 18, 8, .2, Math.PI - .2, 10), 4);
  const br = P.brow || 0; stroke([[-40, -66 - br * 6], [6, -60 + br * 8]], 7); stroke([[22, -60 + br * 8], [64, -64 - br * 6]], 7);
  mouth(14, 58, 44, { o: m.o || 0, w: m.w ?? 1, sm: m.sm ?? -.3, lw: 6 });
  shape(spline([[-26, 40], [14, 30], [56, 40], [64, 56], [40, 50], [14, 46], [-12, 50], [-34, 56]]), { fill: C.stache, lw: 6 });
  shape(spline([[14, -10], [30, 14], [18, 26], [8, 20]]), { fill: C.skinH, lw: 5 });   // nose
  if (P.sweat) sweat(-60, -40, 1.1);
  pop();
  // near arm
  { const [hx, hy, b] = A[0]; shape(noodle([62, -470], [62 + hx, -470 + hy], b, 56, 48), { fill: C.parka, lw: 7, shade: () => fillOnly(rect(62, -480, 200, 30), C.parkaS, { boil: .3 }) }); mitt(62 + hx, -470 + hy, .3, 28); if (P.holdR) P.holdR(62 + hx, -470 + hy); }
  pop();
}

// ---------- DOT ----------
export function dotChar(P) {
  const f = P.face ?? 1, m = P.mouth || {};
  push(); translate(P.x + (P.jit || 0), P.y); scale((P.s ?? 1) * f, (P.s ?? 1) * (P.sq ?? 1));
  const wk = P.walk ?? null, sw = wk == null ? 0 : Math.sin(wk) * 20, lift = wk == null ? 0 : Math.abs(Math.cos(wk)) * 6;
  for (const [sx, d] of [[-1, sw], [1, -sw]]) {
    shape(noodle([sx * 20, -150], [sx * 22 + d, -24], sx * -4, 26, 24), { fill: C.legD, lw: 7 });
    shape(spline([[sx * 22 + d - 26, 0], [sx * 22 + d - 24, -28], [sx * 22 + d + 26, -28], [sx * 22 + d + 40, -6], [sx * 22 + d + 30, 4]]), { fill: C.shoe, lw: 7, shade: () => fillOnly(rect(sx * 22 + d - 30, -10, 80, 16), C.shoeS, { boil: .3 }) });
  }
  const A = ARMS[P.arms || 'rest'];
  { const [hx, hy, b] = A[1]; const k = .75; shape(noodle([-52, -290], [-52 + hx * k, -290 + hy * k], b, 26, 22), { fill: C.shirt, lw: 7 }); hand(-52 + hx * k, -290 + hy * k, Math.PI, 17, C.skinD); }
  // striped shirt + apron
  const body = spline([[-66, -310], [66, -310], [80, -170], [70, -140], [-70, -140], [-80, -170]]);
  shape(body, { fill: C.shirt, lw: 7, shade: () => { for (let k = 0; k < 6; k++) fillOnly(rect(-90, -306 + k * 30, 180, 10), C.stripe, { boil: .3 }); fillOnly(spline([[30, -310], [90, -300], [90, -140], [40, -140]]), 'rgba(0,0,0,.12)', { boil: .3 }); } });
  shape(spline([[-48, -270], [48, -270], [62, -150], [56, -120], [-56, -120], [-62, -150]]), { fill: C.apron, lw: 7, shade: () => fillOnly(spline([[20, -270], [60, -260], [64, -120], [30, -120]]), C.apronS, { boil: .3 }) });
  shape(rr(-30, -246, 46, 26, 6), { fill: C.white, lw: 5 });   // blank name badge
  stroke([[-40, -270], [-26, -312]], 5, { line: C.apronS }); stroke([[40, -270], [26, -312]], 5, { line: C.apronS });
  // head: two buns, freckles
  push(); translate(0, -400); rotate(P.tilt || 0);
  for (const bx of [-70, 70]) shape(ell(bx, -88, 42, 40), { fill: C.hair, lw: 7 });
  shape(spline([[-96, 10], [-100, -60], [-60, -104], [0, -112], [60, -104], [100, -60], [96, 10], [70, 70], [0, 96], [-70, 70]]), { fill: C.skinD, lw: 7, shade: () => fillOnly(ell(64, 10, 50, 100), C.skinDs, { boil: .3 }) });
  shape(spline([[-98, -10], [-90, -80], [-40, -114], [40, -114], [90, -80], [98, -10], [70, -50], [20, -76], [-30, -66], [-74, -40]]), { fill: C.hair, lw: 7 });
  const lk = P.look || [.3, 0], wide = P.wide || 1;
  eye(-14, -6, 30, 36, { lid: P.blink ? 1 : (P.lid ?? .1), look: lk, skin: C.skinD, jitter: P.ejit || 0, wide, lower: P.lower || 0 }); eye(44, -6, 28, 35, { lid: P.blink ? 1 : (P.lid ?? .1), look: lk, skin: C.skinD, jitter: P.ejit || 0, wide, lower: P.lower || 0 });
  const br = P.brow || 0; stroke([[-38, -54 + br * 8], [4, -60 - br * 4]], 6); stroke([[24, -60 - br * 4], [66, -52 + br * 8]], 6);
  for (const [fx, fy] of [[-34, 34], [-24, 40], [62, 34], [72, 40]]) dot(fx, fy, 2.6, C.skinDs);
  mouth(18, 56, 40, { o: m.o || 0, w: m.w ?? 1, sm: m.sm ?? .2, skew: m.skew || 0, lw: 6 });
  if (P.twitch) stroke([[60, -40], [74, -34]], 4);
  if (P.sweat) { sweat(-90, -30, 1); sweat(96, -50, .8); }
  pop();
  // near arm (+ the basket on it)
  { const [hx, hy, b] = A[0]; const k = .75, hp = [52 + hx * k, -290 + hy * k]; shape(noodle([52, -290], hp, b, 26, 22), { fill: C.shirt, lw: 7 }); hand(hp[0], hp[1], 0, 17, C.skinD); if (P.basket) basket(hp[0] + 10, hp[1] + 110, .55, P.items || []); if (P.holdR) P.holdR(hp[0], hp[1]); }
  pop();
}

// ---------- CURD ----------
export function curd(x, y, s = 1, { t = 0, look = [0, 0], blink = false, happy = 0, o = 0, sq = 1, wave = 0 } = {}) {
  push(); translate(x, y); scale(s, s * sq);
  const w = Math.sin(t * 7) * 4;
  const body = spline([[-60, 0], [-66, -40], [-44, -86 + w], [-10, -100], [24, -96 - w], [56, -70], [64, -30], [60, 0], [30, 8], [-30, 8]]);
  shape(body, { fill: C.curd, lw: 7, shade: () => { fillOnly(ell(30, -30, 40, 60), C.curdS, { boil: .3 }); for (const [cx, cy] of [[-30, -30], [6, -60], [-14, -10]]) fillOnly(ell(cx, cy, 9, 6), C.curdS, { boil: .2 }); } });
  for (const dx of [-40, 36]) shape(spline([[dx - 8, -4], [dx + 8, -4], [dx + 4, 14], [dx, 20], [dx - 4, 14]]), { fill: C.curd, lw: 5 });
  if (blink) stroke([[-26, -58], [22, -58]], 6);
  else if (happy > .5) stroke(arc(-2, -52, 22, 18, Math.PI * 1.1, Math.PI * 1.9, 10), 6);
  else shape(ell(-2, -58, 24, 28), { fill: C.white, lw: 6, shade: () => dot(-2 + look[0] * 10, -58 + look[1] * 10, 6) });
  mouth(-2, -20, 18, { o, sm: .6 + happy * .4, lw: 5, teeth: false });
  if (wave) { const a = Math.sin(t * 14) * .5; shape(noodle([50, -50], [86, -90 + a * 20], -10, 12, 10), { fill: C.curd, lw: 5 }); }
  pop();
}

// ---------- the basket (fills up, world by world) ----------
const ITEMS = {
  biscuits: (x, y) => { shape(rr(x - 30, y - 38, 60, 38, 8), { fill: '#7FC8E8', lw: 5 }); for (let i = 0; i < 3; i++) dot(x - 16 + i * 16, y - 20, 6, '#E3B341'); },
  candle: (x, y) => { shape(rect(x - 11, y - 62, 22, 62), { fill: '#F7F3EA', lw: 5 }); shape(spline([[x, y - 90], [x + 8, y - 72], [x, y - 64], [x - 8, y - 72]]), { fill: '#FFC940', lw: 4 }); },
  chicken: (x, y) => { shape(spline([[x - 40, y], [x - 44, y - 30], [x - 10, y - 50], [x + 34, y - 40], [x + 42, y - 10], [x + 30, y]]), { fill: '#D98A3A', lw: 5 }); shape(rr(x + 30, y - 52, 26, 12, 6), { fill: '#F7F3EA', lw: 4 }); },
  tin: (x, y) => { shape(rect(x - 20, y - 46, 40, 46), { fill: '#B9B3A6', lw: 5 }); stroke([[x - 20, y - 26], [x + 20, y - 26]], 4); },
  baguette: (x, y) => { push(); translate(x, y - 40); rotate(-.9); shape(rr(-70, -12, 140, 24, 12), { fill: '#E0A65A', lw: 5 }); pop(); },
  cereal: (x, y) => { shape(rect(x - 24, y - 76, 48, 76), { fill: '#3B6FD6', lw: 5 }); },
  chips: (x, y) => { shape(spline([[x - 26, y], [x - 28, y - 60], [x, y - 66], [x + 28, y - 60], [x + 26, y]], true, 4), { fill: '#FFC940', lw: 5 }); },
  pickles: (x, y) => { shape(rr(x - 22, y - 56, 44, 56, 10), { fill: '#8FBF5A', lw: 5 }); shape(rect(x - 24, y - 66, 48, 12), { fill: '#B9B3A6', lw: 4 }); },
};
export function basket(x, y, s, items) {
  push(); translate(x, y); scale(s);
  stroke(arc(0, -110, 120, 110, Math.PI * 1.05, Math.PI * 1.95, 20), 10);
  const slots = [-100, -45, 45, 100, -75, 75, -10, 0];
  items.forEach((k, i) => ITEMS[k] && ITEMS[k](slots[i % slots.length], -96 - (i > 3 ? 16 : 0)));
  shape([[-150, -104], [150, -104], [124, 0], [-124, 0]], { fill: C.basket, lw: 7, shade: () => { for (let i = 0; i < 6; i++) fillOnly(rect(-160 + i * 58, -110, 24, 120), C.basketS, { boil: .3 }); } });
  pop();
}
