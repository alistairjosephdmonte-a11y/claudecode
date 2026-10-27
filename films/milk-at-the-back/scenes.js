// The 40 scenes. Each: cam keys [u, cx, cy, zoom, rot], draw(u), route (world polyline + [u0,u1] draw window), snaps (impacts, ~every 3 s), sepia.
import { clamp, lerp, seg, ss, eo, ei, eio, back, spring, hash, TAU } from '/core/lib.js';
import { g, push, pop, translate, rotate, scale, shape, fillOnly, stroke, ell, arc, rr, rect, spline, dot, S } from './toon.js';
import * as K from './props.js';
const P = () => K.P;
export const pk = (u, t0, d = .35) => back(seg(u, t0, t0 + d), 1.7);   // pop-up 0 → 1 with overshoot
const walkPh = (u, f = 9) => Math.floor(u * 12) / 12 * f;              // characters on twos
const along = (pts, k) => { // point at fraction k of a polyline
  const L = []; let tot = 0; for (let i = 1; i < pts.length; i++) { const d = Math.hypot(pts[i][0] - pts[i - 1][0], pts[i][1] - pts[i - 1][1]); L.push(d); tot += d; }
  let r = clamp(k) * tot; for (let i = 0; i < L.length; i++) { if (r <= L[i]) { const f = L[i] ? r / L[i] : 0; return [lerp(pts[i][0], pts[i + 1][0], f), lerp(pts[i][1], pts[i + 1][1], f)]; } r -= L[i]; } return pts[pts.length - 1];
};
export { along };
const items = sc => K.BASKET.filter(b => b[0] <= sc).map(b => b[1]);
const ground = (y = 0, col) => fillOnly(rect(-6000, y, 12000, 4000), col ?? P().floor, { boil: 0 });
const wall = (y = 0, col) => fillOnly(rect(-6000, y - 4000, 12000, 4000), col ?? P().milk, { boil: 0 });

// one-point aisle: shelves recede to a vanishing point; the dairy wall glows at the far end. travel = how far we've walked in.
function aisle(u, o = {}) {
  const VX = 0, VY = o.vy ?? -120, F = 600, A = 520, FL = 420, TOP = -520, travel = o.travel ?? 0, far = o.far ?? 5200;
  const pr = (x, y, z) => { const s = F / (F + z); return [VX + x * s, VY + (y - VY) * s]; };
  wall(VY + 2, P().milk); ground(VY, P().floor);
  // dairy wall at the far end
  const end = far - travel, se = F / (F + end);
  push(); translate(VX, VY); scale(se); translate(-VX, -VY); K.fridgeWall(-A, FL, 2 * A, FL - TOP, { glow: 1, doors: 4 }); pop();
  const step = 300, z0 = -(travel % step);
  for (let z = Math.min(end, z0 + step * 20); z >= z0; z -= step) {
    if (z + step < 0) continue; const za = Math.max(z, 1), zb = Math.min(z + step, end); if (zb <= za) continue;
    for (const side of [-1, 1]) {
      const q = [pr(side * A, TOP, za), pr(side * A, TOP, zb), pr(side * A, FL, zb), pr(side * A, FL, za)];
      K.card(q, Math.floor((z - z0) / step + travel / step) % 2 ? P().card : P().milk, { shadow: false, lw: 5, rimCol: P().milk });
      for (let r = 1; r < 4; r++) { const yy = lerp(TOP, FL, r / 4); stroke([pr(side * A, yy, za), pr(side * A, yy, zb)], 4); }
      const seed = Math.floor((z + travel) / step) * 7 + (side > 0 ? 3 : 0);
      for (let r = 0; r < 4; r++) for (let k = 0; k < 3; k++) {
        const zz0 = lerp(za, zb, (k + .15) / 3), zz1 = lerp(za, zb, (k + .8) / 3), yb = lerp(TOP, FL, (r + 1) / 4) - 6, yt = yb - (FL - TOP) / 4 * (.45 + hash(seed + r * 5 + k) * .3);
        fillOnly([pr(side * A, yt, zz0), pr(side * A, yt, zz1), pr(side * A, yb, zz1), pr(side * A, yb, zz0)], [P().blue, P().glow, P().milk, P().card2][Math.floor(hash(seed * 3 + r + k * 2) * 4)], { boil: .4 });
      }
    }
  }
  return pr;
}

const sceneList = [];
const def = o => sceneList.push(o);

// ═══ ACT I · Ch1 The Longest Walk ═══
def({ // S1 macro on the carton → doors open → the route races down an endless aisle
  cam: [[0, 0, -170, 3.2], [2.6, 0, -170, 2.6], [4.2, 0, -120, 1], [10, 0, -120, 1.05], [15, 0, -110, 1.8]],
  snaps: [2.6, 4.4, 7.4, 10.4, 13.2],
  draw(u) {
    if (u < 4.3) { wall(0); ground(0); K.door(0, 300, ss(seg(u, 2.8, 4.1)), 1.3); push(); translate(0, 150); K.carton(0, 0, 1.4, { glow: 1 }); pop(); return; }
    aisle(u, { travel: eio(seg(u, 4.2, 14.6)) * 4600, far: 5200 });
  },
  route(u) { if (u < 4.3) return { pts: [[0, 330], [0, 330]], k: 0 }; const pts = [[0, 540], [0, 420], [0, -60], [0, -118]]; return { pts, k: ss(seg(u, 4.3, 14.7)) }; },
});
def({ // S2 products pop at the shopper → shelves fold flat → the scale rises, wobbling
  cam: [[0, 0, -60, 1.6], [3, 0, -60, 1.1], [8, 0, -80, 1], [11, 0, -160, .9], [15, 0, -180, 1.3]],
  snaps: [1.2, 3.4, 5.6, 8.2, 11.0, 13.4],
  draw(u) {
    wall(240); ground(240);
    const fold = ss(seg(u, 7.6, 9));
    const kinds = ['loaf', 'chips', 'flowers', 'cereal', 'jar', 'biscuits'];
    for (let i = 0; i < 6; i++) {
      const side = i % 2 ? 1 : -1, x = side * (260 + Math.floor(i / 2) * 220);
      push(); translate(x, 240); scale(1, 1 - fold * .96); K.shelfUnit(-120, 0, 240, 420, { seed: i + 2 });
      const p = pk(u, 1 + i * .8); if (p > .01) { push(); translate(-side * 60 * p, -180 - 60 * p); scale(1.6 * p); K.ITEM[kinds[i]](0, 0); pop(); }
      pop();
    }
    K.shopper(0, 240, .9, { walk: u < 7.6 ? walkPh(u) : null, basket: true, items: items(2) });
    if (u > 8.4) { const r = pk(u, 8.4, .5); push(); translate(0, 240); scale(r); K.balance(0, 0, .85, Math.sin(u * 3.2) * .14 * (1.2 - r * .2)); pop(); }
  },
  route(u) { return { pts: [[-900, 250], [-200, 250], [0, 250], [0, 0], [0, -330]], k: ss(seg(u, 0, 13)) }; },
});
def({ // S3 dive through a crack, layers of paper fall into sepia; the film's title card
  cam: [[0, 0, 0, 1], [3, 0, 120, 1.6], [6, -160, 1000, 1.35], [8.5, 200, 1420, 1.3], [10.5, -120, 1900, 1.35], [12, 0, 2150, 1.2], [15, 0, 2250, 1.5]], sepia: u => ss(seg(u, 3, 7)),
  snaps: [2.2, 4.6, 7.0, 9.2, 11.8],
  draw(u) {
    ground(0); wall(0);
    const crack = ss(seg(u, 1.4, 2.6));
    fillOnly([[-10 * crack, 0], [-60 * crack, 60], [20, 130], [-30 * crack, 220], [40 * crack, 260], [70 * crack, 140], [10, 60]], P().ink);
    for (let k = 0; k < 6; k++) { const y = 400 + k * 320; fillOnly(rect(-3000, y, 6000, 300), [P().card, P().card2, P().milk][k % 3], { boil: .5 }); K.card(rect(-3000, y, 6000, 30), P().card2, { shadow: false, lw: 4 }); }
    K.iceBlock(-200, 1100, 1.9, seg(u, 5, 9));
    K.float_(300, 1500, 1.6);
    K.turnstile(-160, 1960, 1.7, u * 1.4);
  },
  route(u) { return { pts: [[0, -300], [0, 0], [10, 400], [-20, 900], [30, 1500], [0, 2150]], k: ss(seg(u, 0, 13.5)) }; },
  card: { t0: 11.2, t1: 14.7, text: ['WHY IS THE MILK', 'AT THE BACK?'] },
});

// ═══ Ch2 The Theory Everyone Knows ═══
def({ // S4 top-down floor plan; tiny shoppers wear a groove door → back wall
  cam: [[0, 0, 300, 1.8], [3, 0, 100, 1], [12, 0, -40, .95], [15, 0, -380, 1.5]],
  snaps: [1.0, 4.0, 7.0, 10.0, 13.0],
  draw(u) {
    wall(-2000); K.floorPlan();
    const path = [[0, 420], [0, 300], [-430, 300], [-430, -300], [0, -330]];
    const groove = ss(seg(u, 3, 13));
    stroke(path, 26 * groove, { line: P().glow, boil: .3 });
    for (let i = 0; i < 9; i++) { const k = ((u * .08 + i / 9) % 1); const p = along(path, k); K.tinyShopper(p[0] + (hash(i) - .5) * 20, p[1], pk(u, 1 + i * .4) * 1.2, u * 8 + i); }
  },
  route(u) { return { pts: [[0, 540], [0, 300], [-430, 300], [-430, -300], [0, -330], [0, -380]], k: ss(seg(u, 0, 14.6)) }; },
});
def({ // S5 building the basket: biscuits, candle, chicken, flowers drop in; the gap stays empty
  cam: [[0, 0, -100, 1.3], [7, 0, -110, 1.1], [15, 0, -140, 1.5]],
  snaps: [2.8, 5.4, 8.0, 10.4, 12.6],
  draw(u) {
    wall(250); ground(250);
    const dropped = ['biscuits', 'candle', 'chicken', 'flowers'].filter((_, i) => u > 3 + i * 2.5);
    push(); translate(0, 250); K.basket(0, 0, 1.6, dropped); pop();
    ['biscuits', 'candle', 'chicken', 'flowers'].forEach((k, i) => { const t0 = 1.8 + i * 2.5, f = seg(u, t0, t0 + 1.2); if (f > 0 && f < 1) { push(); translate(-120 + i * 90, lerp(-700, 60, ei(f))); scale(1.6); rotate(f * 2); K.ITEM[k](0, 0); pop(); } });
    if (u > 12.4) { const p = pk(u, 12.4); dot(0, 140, 30 * p, P().glow); }
  },
  route(u) { return { pts: [[-900, 300], [-300, 300], [-200, 120], [200, 120], [300, 300], [900, 300]], k: ss(seg(u, 0, 14.6)) }; },
});
def({ // S6 the decompression zone: a pale bubble around the shopper, dimmed displays, pop at the dotted line
  cam: [[0, -300, -80, 1.2], [8, -100, -80, 1], [15, 300, -100, 1.3]],
  snaps: [2.0, 5.0, 8.4, 9.6, 12.4],
  draw(u) {
    wall(250); ground(250);
    const pop_ = ss(seg(u, 8.4, 8.8)), dim = 1 - pop_;
    for (let i = 0; i < 5; i++) { push(); translate(-760 + i * 330, 250); K.shelfUnit(-110, 0, 220, 360, { seed: i + 11 }); pop(); }
    if (dim > 0) fillOnly(rect(-1300, -400, 1100 + 400 * seg(u, 0, 8.4), 900), P().milk, { alpha: .55 * dim, boil: 0 });
    g.save(); g.setLineDash([18, 14]); stroke([[-200, -300], [-200, 300]], 5); g.restore();
    const x = lerp(-700, 500, ss(seg(u, 1, 13.5)));
    K.shopper(x, 250, .9, { walk: walkPh(u), basket: true, items: items(6) });
    if (u < 8.8) { const r = u > 8.4 ? 1 + pop_ * .6 : 1; fillOnly(ell(x, 100, 190 * r, 260 * r), P().glow, { alpha: .45 * (1 - pop_) }); stroke(ell(x, 100, 190 * r, 260 * r), 5, { line: P().blue, alpha: 1 - pop_ }); }
  },
  route(u) { return { pts: [[-1100, 280], [-700, 280], [500, 280], [1100, 280]], k: ss(seg(u, 0, 14.6)) }; },
});
def({ // S7 the carton as a lure → route lines bend into a funnel → a corner peels to a sepia plan
  cam: [[0, 0, -200, 1.3], [5, 0, -120, 1], [11, 0, 0, .9], [15, 520, 300, 1.8]],
  snaps: [1.6, 4.4, 7.4, 10.4, 12.8],
  draw(u) {
    wall(-2000); K.floorPlan();
    for (let i = 0; i < 7; i++) { const x0 = -600 + i * 200, f = ss(seg(u, 4, 8)); stroke(spline([[x0, 420], [lerp(x0, x0 * .4, f), 0], [lerp(x0, 0, f), -260]], false, 8), 4, { line: P().blue }); }
    const sw = Math.sin(u * 2.4) * .25; push(); translate(0, -560); rotate(sw); stroke([[0, 0], [0, 260]], 3); K.carton(0, 420, .8, { glow: .8 }); pop();
    const peel = ss(seg(u, 10.6, 13)); if (peel > 0) { K.setPal(1); fillOnly([[700, 420], [700 - 420 * peel, 420], [700, 420 - 420 * peel]], K.SEPIA.card2); K.setPal(0); K.card([[700 - 420 * peel, 420], [700, 420 - 420 * peel], [700 - 380 * peel, 420 - 380 * peel]], P().card, { lw: 5 }); }
  },
  route(u) { return { pts: [[-700, 600], [-500, 420], [-200, 100], [0, -150], [300, 60], [520, 300]], k: ss(seg(u, 0, 14.6)) }; },
});

// ═══ ACT II (sepia) · Ch3 Before the Aisle ═══
def({ // S8 a counter store; a faceless clerk on a rolling ladder fetches; the route is a still dot
  cam: [[0, 0, -100, 1.6], [6, -120, -120, 1], [15, 160, -100, 1.3]], sepia: () => 1,
  snaps: [1.4, 4.0, 7.0, 10.0, 13.0],
  draw(u) {
    wall(260); ground(260);
    for (let i = 0; i < 4; i++) { push(); translate(-540 + i * 360, 0); K.shelfUnit(-170, 0, 340, 420, { seed: i + 21, rows: 4 }); pop(); }
    const lx = lerp(-500, 420, (Math.sin(u * .55) + 1) / 2);
    K.card(rect(lx - 50, -420, 12, 430), P().card2); K.card(rect(lx + 40, -420, 12, 430), P().card2);
    for (let r = 0; r < 6; r++) stroke([[lx - 44, -380 + r * 70], [lx + 46, -380 + r * 70]], 5);
    K.shopper(lx, -60, .8, { face: -1, reach: Math.floor(u) % 3 === 0 });   // the clerk, from behind
    K.card(rect(-900, 260, 1800, 140), P().card2, { shade: K.hard(rect(-900, 260, 1800, 30), P().card) });
    for (let i = 0; i < 4; i++) { const f = seg(u, 2 + i * 3, 3 + i * 3); if (f > 0) { push(); translate(lerp(400, -200 + i * 70, eo(f)), 260); K.ITEM[['tin', 'loaf', 'jar', 'eggs'][i]](0, 0); pop(); } }
    K.shopper(-420, 620, .85, { face: 1 });
  },
  route(u) { return { pts: [[-300, 560], [-300, 560.1]], k: 1, dot: 1 }; },
});
def({ // S9 horse cart folds into an electric float; bottles hop onto doorsteps; the milk round on a map
  cam: [[0, -900, 20, 1.5], [7, 0, 0, 1.35], [14, 800, 0, 1.5], [15, 900, 0, 1.6]], sepia: () => 1,
  snaps: [2.4, 5.0, 7.6, 10.2, 12.6],
  draw(u) {
    wall(-2000); fillOnly(rect(-1400, -800, 2800, 1600), P().card, { boil: 0 });
    for (let i = 0; i < 6; i++) for (let j = 0; j < 3; j++) K.card(rect(-900 + i * 320, -460 + j * 300, 220, 180), P().milk, { lw: 4, sx: 4, sy: 5 });
    const k = ss(seg(u, 2, 4)), x = lerp(-900, 900, seg(u, 1, 14));
    K.float_(x, 110, .6, { horse: k < .5 });
    for (let i = 0; i < 5; i++) { const t0 = 4.5 + i * 1.8, f = seg(u, t0, t0 + .5); if (f > 0) K.bottle(-640 + i * 320, -110 - Math.sin(f * Math.PI) * 60 + 40, .7); }
  },
  route(u) { return { pts: [[-1100, 110], [-640, 110], [-640, -110], [-320, -110], [-320, 110], [0, 110], [0, -110], [320, -110], [320, 110], [640, 110], [1100, 110]], k: ss(seg(u, 0, 14.6)) }; },
});
def({ // S10 one float multiplies into a fleet; a tower of bottles collapses in three steps to one
  cam: [[0, -300, -40, 1], [6, -300, -40, .9], [9, 300, -60, 1.1], [15, 320, 0, 1.5]], sepia: () => 1,
  snaps: [1.4, 3.0, 4.6, 9.4, 11.4, 13.2],
  draw(u) {
    wall(160); ground(160);
    const n = Math.min(12, 1 + Math.floor(u * 1.6)); for (let i = 0; i < n; i++) { const p = pk(u, i / 1.6); push(); translate(-620 + (i % 4) * 160, 160 - Math.floor(i / 4) * 90); scale(p); K.float_(0, 0, .35); pop(); }
    const lvl = u < 9 ? 6 : u < 11 ? 3 : u < 13 ? 1.6 : .4;
    const rows = Math.max(1, Math.round(lvl));
    for (let r = 0; r < rows; r++) for (let c = 0; c < Math.max(1, rows - r); c++) K.bottle(340 + (c - (rows - r - 1) / 2) * 52, 160 - r * 106, .9);
  },
  route(u) { return { pts: [[-1100, 240], [-300, 240], [340, 240], [340, 40], [600, 40]], k: ss(seg(u, 0, 14.6)) }; },
});
def({ // S11 an icebox melting, a bottle sweating → a turnstile and a 1930s fridge slam in
  cam: [[0, -350, -40, 1.6], [8, -250, -40, 1.45], [11.5, 250, -60, 1.25], [15, 350, -80, 1.5]], sepia: () => 1,
  snaps: [2.2, 5.0, 7.6, 10.0, 11.0, 13.4],
  draw(u) {
    wall(240); ground(240);
    K.iceBlock(-420, 240, 1.4, seg(u, 0, 9)); K.bottle(-180, 240, 1.4);
    for (let i = 0; i < 4; i++) { const f = ((u * .7 + i * .25) % 1); fillOnly(ell(-180 + (i - 1.5) * 16, 120 + f * 110, 5, 8), P().glow); }
    const a = pk(u, 10, .3), b = pk(u, 11, .3);
    if (a > 0) { push(); translate(200, lerp(-900, 0, a)); K.turnstile(0, 240, 1.4, u); pop(); }
    if (b > 0) { push(); translate(500, lerp(-1200, 0, b)); K.fridge30s(0, 240, 1.3); pop(); }
  },
  route(u) { return { pts: [[-1100, 280], [-420, 280], [-180, 280], [200, 280], [500, 280], [1100, 280]], k: ss(seg(u, 0, 14.6)) }; },
});

// ═══ Ch4 The Maze, 1916 ═══
def({ // S12 the turnstile clicks; the clerk is yanked off; a basket drops into her hand
  cam: [[0, 0, -100, 1.6], [5, 0, -80, 1], [15, 100, -120, 1.4]], sepia: () => 1,
  snaps: [2.0, 4.4, 6.8, 9.2, 11.6],
  draw(u) {
    wall(260); ground(260);
    K.silhouette(-640, 260, 1.15, { face: 1 });   // Clarence Saunders, silhouette only
    K.turnstile(-180, 260, 1.3, -ss(seg(u, 2, 2.4)) * TAU / 3 - ss(seg(u, 9, 9.4)) * TAU / 3);
    const yank = ei(seg(u, 4.4, 5)); K.shopper(260 + yank * 1400, 0, .8, { face: -1 });
    const drop = ei(seg(u, 6.4, 7)), rb = u > 7 ? spring(u - 7, 7, .4) : 0;
    K.shopper(lerp(-420, 60, ss(seg(u, 8.4, 11))), 260, .95, { walk: u > 8.4 && u < 11 ? walkPh(u) : null });
    if (u > 6.4) { push(); translate(lerp(-420, 60, ss(seg(u, 8.4, 11))) + 70, lerp(-800, 60, drop) + (u > 7 ? (1 - rb) * -10 : 0)); scale(.5); K.basket(0, 0, 1, items(12)); pop(); }
  },
  route(u) { return { pts: [[-1100, 300], [-420, 300], [-180, 300], [300, 300], [1100, 300]], k: ss(seg(u, 0, 14.6)) }; },
});
def({ // S13 a sepia blueprint of one winding one-way path; the route traces it in one stroke
  cam: [[0, 0, 0, .95], [9, 0, 0, .9], [13, 300, 260, 1.4], [15, 300, 300, 2.4]], sepia: () => 1,
  snaps: [1.0, 4.0, 7.0, 10.0, 13.0],
  draw(u) {
    wall(-2000); K.card(rect(-760, -440, 1520, 880), P().card);
    for (let i = 0; i < 20; i++) stroke([[-760 + i * 80, -440], [-760 + i * 80, 440]], 1.5, { line: P().grey, boil: 0 });
    for (let i = 0; i < 11; i++) stroke([[-760, -440 + i * 80], [760, -440 + i * 80]], 1.5, { line: P().grey, boil: 0 });
    for (let i = 0; i < 6; i++) K.card(rect(-560 + i * 200, -320 + (i % 2) * 100, 40, 540), P().card2, { lw: 4, sx: 3, sy: 4 });
  },
  route(u) { const pts = [[-700, 380]]; for (let i = 0; i < 7; i++) { const x = -640 + i * 200; pts.push([x, i % 2 ? -380 : 380], [x + 100, i % 2 ? -380 : 380]); } pts.push([700, 380]); pts.push([300, 300]); return { pts, k: ss(seg(u, .4, 14.6)) }; },
});
def({ // S14 rise over dozens of shoppers snaking the maze; a marker circle around the cashier
  cam: [[0, 300, 300, 2.2], [4, 0, 0, .9], [11, 0, 0, .85], [15, 640, 380, 1.8]], sepia: () => 1,
  snaps: [2.0, 5.0, 8.0, 10.6, 12.6],
  draw(u) {
    wall(-2000); K.card(rect(-760, -440, 1520, 880), P().card);
    for (let i = 0; i < 6; i++) K.card(rect(-560 + i * 200, -320 + (i % 2) * 100, 40, 540), P().card2, { lw: 4, sx: 3, sy: 4 });
    const path = [[-700, 380]]; for (let i = 0; i < 7; i++) { const x = -640 + i * 200; path.push([x, i % 2 ? -380 : 380], [x + 100, i % 2 ? -380 : 380]); } path.push([700, 380]);
    for (let i = 0; i < 24; i++) { const p = along(path, (u * .03 + i / 24) % 1); K.tinyShopper(p[0], p[1], pk(u, .5 + i * .15) * 1.1, u * 6 + i); }
    K.card(rr(600, 330, 120, 80, 10), P().card2);   // the cashier's counter
    const c = ss(seg(u, 10.4, 12)); if (c > 0) stroke(arc(660, 370, 110, 90, -1, -1 + TAU * c, 40), 10, { line: K.BASE.coral });
  },
  route(u) { return { pts: [[300, 300], [500, 380], [640, 380], [660, 400]], k: ss(seg(u, 0, 14.6)) }; },
});
def({ // S15 searching the shelves — no milk; a blank back wall; frost turns it dairy blue
  cam: [[0, -400, -80, 1.2], [8, 0, -100, 1], [15, 0, -200, 1.5]], sepia: u => 1 - ss(seg(u, 11, 14.5)) * .5,
  snaps: [1.8, 4.6, 7.4, 10.0, 12.4],
  draw(u) {
    wall(260); ground(260);
    for (let i = 0; i < 3; i++) { push(); translate(-760 + i * 300, 260); K.shelfUnit(-120, 0, 240, 380, { seed: i + 31 }); pop(); }
    const frost = ss(seg(u, 10.6, 13.6));
    K.card(rect(150, -300, 700, 560), P().milk);
    if (frost > 0) { fillOnly(rect(150, -300, 700 * frost, 560), K.BASE.blue, { alpha: .95 }); for (let i = 0; i < 12; i++) { const x = 150 + hash(i) * 700 * frost; stroke([[x, -280 + hash(i + 3) * 500], [x + 20, -260 + hash(i + 3) * 500]], 3, { line: K.BASE.glow }); } }
    K.shopper(lerp(-700, 80, ss(seg(u, .5, 9))), 260, .9, { walk: u < 9 ? walkPh(u) : null, basket: true, items: items(15) });
    for (let i = 0; i < 3; i++) { const f = seg(u, 2 + i * 2.3, 3 + i * 2.3); if (f > 0 && f < 1) { fillOnly(ell(-760 + i * 300, -40, 110, 110), P().glow, { alpha: .3 * Math.sin(f * Math.PI) }); } }
  },
  route(u) { return { pts: [[-1100, 300], [-760, 300], [-460, 300], [-160, 300], [150, 300], [500, -20], [500, -200]], k: ss(seg(u, 0, 14.6)) }; },
});

// ═══ Ch5 The Cold Revolution (sepia → milk white) ═══
def({ // S16 windows light blue one by one; the route draws a rising graph over the roofs
  cam: [[0, -300, -80, 1.2], [8, 0, -100, .95], [15, 600, -340, 1.6]], sepia: u => .5 - ss(seg(u, 0, 4)) * .5,
  snaps: [1.6, 4.2, 6.8, 9.4, 12.0],
  draw(u) {
    wall(240); ground(240);
    for (let i = 0; i < 9; i++) { const lit = ss(seg(u, 1 + i * 1.3, 1.5 + i * 1.3)); K.house(-800 + i * 200, 240, .9 + (i % 2) * .15, lit); }
  },
  route(u) { const pts = []; for (let i = 0; i <= 9; i++) pts.push([-900 + i * 170, lerp(-80, -400, (i / 9) ** 1.8)]); pts.push([700, -420]); return { pts, k: ss(seg(u, .5, 14.6)) }; },
});
def({ // S17 the float peels like an old poster → a car boot opens → seven cartons slide into a fridge
  cam: [[0, -400, -60, 1.1], [6, 0, -60, 1], [15, 500, -80, 1.4]],
  snaps: [2.0, 4.6, 7.4, 9.0, 10.6, 12.8],
  draw(u) {
    wall(240); ground(240);
    const peel = ss(seg(u, 1.6, 4));
    if (peel < 1) { push(); translate(-500, 0); K.card(rect(-260, -280, 520, 400), P().card2); K.float_(60, 60, .8); pop(); fillOnly([[-240, 120], [-240 + 520 * peel, 120], [-240, 120 - 400 * peel]], P().milk); }
    K.car(-100 + (1 - pk(u, 4.4)) * -600, 240, 1.3, K.BASE.blue);
    K.fridge30s(560, 240, 1.4, ss(seg(u, 8, 9)));
    for (let i = 0; i < 7; i++) { const f = seg(u, 9 + i * .55, 9.6 + i * .55); if (f > 0) K.carton(lerp(80, 500 + (i % 4) * 34, eo(f)), lerp(110, i < 4 ? 80 : 0, eo(f)) + (i < 4 ? 0 : -10), .32); }
  },
  route(u) { return { pts: [[-1100, 280], [-500, 280], [-100, 280], [300, 160], [560, 100], [700, 280], [1100, 280]], k: ss(seg(u, 0, 14.6)) }; },
});
def({ // S18 a garage door rolls up on a huge store with parked cars; a tiny corner shop for scale
  cam: [[0, 0, -100, 1.5], [5, 0, -100, 1], [15, -500, -40, 1.3]],
  snaps: [1.2, 3.4, 6.0, 8.6, 11.2, 13.4],
  draw(u) {
    wall(240); ground(240);
    K.silhouette(-760, 240, 1, { face: 1 });   // Michael Cullen, silhouette only
    K.card(rect(-460, -380, 920, 620), P().card);
    fillOnly(rect(-400, -320, 800, 560), P().glow);
    for (let i = 0; i < 4; i++) { push(); translate(-300 + i * 200, 240); K.shelfUnit(-70, 0, 140, 300, { seed: i + 41 }); pop(); }
    const up = ss(seg(u, 1, 3.4)); K.card(rect(-400, -320, 800, 560 * (1 - up)), P().card2, { shade: () => { for (let i = 0; i < 12; i++) fillOnly(rect(-400, -320 + i * 48, 800, 6), P().grey); } });
    for (let i = 0; i < 6; i++) { const p = pk(u, 5 + i * .5); push(); translate(560 + (i % 3) * 210, 240 + Math.floor(i / 3) * 0); scale(p * .8); K.car(0, Math.floor(i / 3) * -10, 1, [K.BASE.blue, K.BASE.glow, K.BASE.milk][i % 3]); pop(); }
    push(); translate(-600, 240); scale(pk(u, 9.4) * .5); K.card(rect(-90, -200, 180, 200), P().card2); K.card(rect(-40, -110, 80, 110), P().glow, { shadow: false }); pop();
  },
  route(u) { return { pts: [[1100, 300], [500, 300], [0, 300], [-500, 300], [-1100, 300]], k: ss(seg(u, 0, 14.6)) }; },
});
def({ // S19 a fridge case opens to show its machinery → a marker arrow shoves it back → the dairy wall forms
  cam: [[0, 0, -100, 1.4], [5, 0, -100, 1], [10, 0, -260, .9], [15, 0, -360, 1.4]],
  snaps: [2.0, 4.6, 7.2, 9.8, 12.4],
  draw(u) {
    wall(260); ground(260);
    const shove = eio(seg(u, 7.4, 9.4)), sy = lerp(260, -160, shove), ss_ = lerp(1.3, .8, shove);
    if (u > 10.4) K.fridgeWall(-620, -160, 1240, 420, { glow: ss(seg(u, 10.4, 12.4)), doors: 6 });
    push(); translate(0, sy); scale(ss_);
    K.card(rect(-220, -380, 440, 380), P().blue);
    const open = ss(seg(u, 1.6, 3));
    K.card(rect(-200, -360, 400, 340), P().glow, { shadow: false });
    if (open > 0) { push(); translate(0, -190); scale(open);
      for (let i = 0; i < 4; i++) stroke(spline([[-170, -140 + i * 80], [-60, -120 + i * 80], [60, -160 + i * 80], [170, -130 + i * 80]], false), 10, { line: P().grey });
      K.card(ell(-80, 20, 70, 70), P().card2); K.card(rr(40, -20, 120, 90, 10), P().card2);
      for (let i = 0; i < 4; i++) { const f = (u * 1.5 + i * .25) % 1; stroke([[60 + i * 30, -60 - f * 60], [70 + i * 30, -90 - f * 60]], 4, { line: K.BASE.coral, alpha: 1 - f }); }
      pop(); }
    pop();
    const ar = ss(seg(u, 6.6, 7.6)); if (ar > 0) { stroke([[0, 380], [0, lerp(380, 120, ar)]], 12, { line: K.BASE.coral }); stroke([[-40, lerp(380, 120, ar) + 40], [0, lerp(380, 120, ar)], [40, lerp(380, 120, ar) + 40]], 12, { line: K.BASE.coral }); }
  },
  route(u) { return { pts: [[-1100, 330], [-300, 330], [0, 330], [0, 120], [0, -160], [0, -420]], k: ss(seg(u, 0, 14.6)) }; },
});

// ═══ ACT III · Ch6 Follow the Truck ═══
def({ // S20 chase a frosted refrigerated truck as it backs into the rear dock with a thud
  cam: [[0, -900, -80, 1.2], [6, -200, -80, 1], [12, 450, -80, 1], [15, 600, -60, 1.5]],
  snaps: [2.0, 5.0, 8.0, 10.4, 12.4],
  draw(u) {
    wall(240); ground(240);
    K.card(rect(500, -420, 900, 660), P().card); K.card(rect(560, -220, 300, 460), P().glow); K.fridgeWall(900, 240, 420, 460, { glow: .3, doors: 2 });
    for (let i = 0; i < 8; i++) K.card(rect(-1600 + i * 300, 220, 140, 10), P().milk, { shadow: false, lw: 3, rim: false });
    const x = u < 9 ? lerp(-1500, 0, eo(seg(u, 0, 8))) : lerp(0, 400, ei(seg(u, 9, 12.2)));
    const bump = u > 12.2 ? spring(u - 12.2, 8, .3) : 1;
    K.truck(x + (u > 12.2 ? (1 - bump) * 10 : 0), 240, 1.1, { face: u < 9 ? 1 : -1 });
  },
  route(u) { return { pts: [[-1600, 270], [0, 270], [400, 270], [700, 270], [700, 0]], k: ss(seg(u, 0, 14.6)) }; },
});
def({ // S21 a carton drops a scale pan → crates stack into a pallet → a coral ruler stretches from the dock and snaps back short
  cam: [[0, -300, -80, 1.3], [6, 0, -80, 1], [15, 300, -60, 1.3]],
  snaps: [1.6, 4.2, 6.6, 9.0, 11.4, 12.4],
  draw(u) {
    wall(240); ground(240);
    const d = pk(u, 1.4); push(); translate(-500, 240); K.card(rr(-40, -20, 80, 20, 6), P().card2); K.card(rect(-8, -200, 16, 180), P().card); K.card(rr(-110, -210 + d * 30, 220, 18, 8), P().card); if (u > 1) K.carton(0, -210 + d * 30, .7); pop();
    const n = Math.min(12, Math.floor(seg(u, 3.4, 8) * 12));
    for (let i = 0; i < n; i++) { push(); translate(-80 + (i % 4) * 90, 240 - 30 - Math.floor(i / 4) * 70); K.card(rr(-42, -60, 84, 60, 6), P().glow, { lw: 4 }); for (let k = 0; k < 3; k++) fillOnly([[-30 + k * 26, -60], [-20 + k * 26, -76], [-10 + k * 26, -60]], P().blue); pop(); }
    if (n) K.card(rect(-140, 210, 380, 30), P().card2);
    const st = u < 11.4 ? ss(seg(u, 9, 11.2)) : lerp(1, .3, spring(u - 11.4, 8, .35));
    if (u > 9) K.card(rect(300, 140, 700 * st, 50), K.BASE.coral, { lw: 5 });
    for (let i = 0; i < 14 * st; i++) stroke([[300 + i * 50, 140], [300 + i * 50, 160]], 3);
  },
  route(u) { return { pts: [[-1100, 290], [-500, 290], [-100, 290], [300, 290], [1100, 290]], k: ss(seg(u, 0, 14.6)) }; },
});
def({ // S22 dollhouse cutaway: dock → cold room → glass-door wall; a stocker pushes a carton forward as she takes one
  cam: [[0, -500, -60, 1.1], [7, 0, -60, .9], [15, 420, -100, 1.6]],
  snaps: [1.4, 4.0, 6.6, 9.2, 11.6, 12.8],
  draw(u) {
    wall(260); ground(260);
    K.card(rect(-900, -340, 1800, 600), P().card);
    K.card(rect(-880, -320, 520, 580), P().card2); K.card(rect(-340, -320, 560, 580), P().glow); K.card(rect(240, -320, 640, 580), P().milk);
    for (let i = 0; i < 3; i++) fillOnly(rect(-330, -300 + i * 170, 540, 10), P().milk);
    K.card(rect(200, -320, 40, 580), P().blue);
    const px = lerp(-800, -240, ss(seg(u, 1.2, 5))); push(); translate(px, 260); K.card(rect(-90, -30, 180, 30), P().card2); for (let i = 0; i < 6; i++) K.card(rr(-80 + (i % 3) * 56, -90 - Math.floor(i / 3) * 56, 50, 56, 4), P().glow, { lw: 3, shadow: false }); pop();
    K.shopper(-40, 260, .9, { face: -1, walk: u > 5 && u < 8 ? walkPh(u) : null });   // the stocker, from behind
    K.shopper(lerp(900, 480, ss(seg(u, 3, 8))), 260, .9, { face: -1, walk: u > 3 && u < 8 ? walkPh(u) : null, reach: u > 10, basket: true, items: items(22) });
    const push_ = ss(seg(u, 9.6, 10.6)), take = ss(seg(u, 10.8, 12));
    K.carton(lerp(120, 210, push_) + take * 120, 20 - take * 60, .5);
  },
  route(u) { return { pts: [[-1100, 290], [-800, 290], [-240, 290], [210, 290], [210, 40], [560, 40]], k: ss(seg(u, 0, 14.6)) }; },
});
def({ // S23 pull back from one fridge door: the whole wall is the face of a box joined to the dock
  cam: [[0, 0, -120, 3.4], [5, 0, -100, 1.6], [11, 300, -60, .7], [15, 700, -40, 1.2]],
  snaps: [1.4, 4.0, 6.6, 9.2, 11.8],
  draw(u) {
    wall(-2000); ground(320);
    const box = ss(seg(u, 6, 9.4));
    if (box > 0) { K.card([[620, -460], [1500, -620], [1500, 120], [620, 320]], P().card2, { alpha: box }); K.card([[-620, -460], [620, -460], [1500, -620], [260, -620]], P().card, { alpha: box }); }
    K.fridgeWall(-620, 320, 1240, 780, { glow: 1, doors: 5 });
    if (u > 9.4) { const d = pk(u, 9.4); push(); translate(1700, 320); scale(d); K.card(rect(-200, -500, 400, 500), P().card2); K.card(rect(-160, -440, 320, 440), P().glow, { shadow: false }); pop(); }
  },
  route(u) { return { pts: [[0, 360], [0, 380], [620, 380], [1500, 380], [1700, 380], [1700, 200]], k: ss(seg(u, 0, 14.6)) }; },
});
def({ // S24 slide from a corner shop into a Japanese-style convenience store; both back walls glow in sync
  cam: [[0, -700, -80, 1], [6, -400, -80, .95], [11, 400, -80, .95], [15, 700, -60, 1.4]],
  snaps: [1.0, 3.6, 6.4, 9.2, 12.0],
  draw(u) {
    wall(240); ground(240);
    const pulse = .6 + .4 * Math.sin(u * 2.4);
    for (const [cx, sh] of [[-700, 0], [700, 1]]) {
      K.card(rect(cx - 420, -380, 840, 620), P().card);
      K.fridgeWall(cx - 380, 80, 760, 420, { glow: pulse, doors: 4 });
      for (let i = 0; i < 2; i++) { push(); translate(cx - 200 + i * 400, 240); K.shelfUnit(-90, 0, 180, 150, { seed: i + 51 + sh * 9, rows: 2 }); pop(); }
      if (sh) for (let i = 0; i < 6; i++) fillOnly(rect(cx - 400 + i * 140, -360, 100, 14), P().blue);
    }
    K.shopper(lerp(-900, 900, ss(seg(u, .4, 14))), 240, .75, { walk: walkPh(u), basket: true, items: items(24) });
  },
  route(u) { return { pts: [[-1100, 270], [-700, 270], [-700, 80], [-300, 270], [700, 270], [700, 80], [1100, 80]], k: ss(seg(u, 0, 14.6)) }; },
});

// ═══ Ch7 The Racetrack ═══
def({ // S25 the carton unwrapped like a present → the whole store pops up around it
  cam: [[0, 0, -120, 2.2], [5, 0, -120, 1.4], [10, 0, -60, .8], [15, 0, -200, 1.3]],
  snaps: [1.4, 3.4, 5.2, 7.6, 10.0, 12.4],
  draw(u) {
    wall(240); ground(240);
    const st = ss(seg(u, 5.6, 9));
    for (let i = 0; i < 6; i++) { const side = i % 2 ? 1 : -1, p = pk(u, 5.6 + i * .5); push(); translate(side * (300 + Math.floor(i / 2) * 230), 240); scale(1, p); K.shelfUnit(-100, 0, 200, 360, { seed: i + 61 }); pop(); }
    if (st > 0) K.fridgeWall(-500, -60, 1000, 300 * st, { glow: st, doors: 5 });
    const un = ss(seg(u, 1.6, 4.4));
    K.carton(0, 240, 1.2, { glow: un });
    if (un < 1) { for (const k of [-1, 1]) { push(); translate(k * 170 * un, 240 - 100 * un); rotate(k * un * 1.4); K.card(rect(k < 0 ? -110 : 0, -220, 110, 230), P().glow); stroke([[k < 0 ? -55 : 55, -220], [k < 0 ? -55 : 55, 10]], 8, { line: P().blue }); pop(); } }
  },
  route(u) { return { pts: [[0, 600], [0, 280], [-200, 280], [-200, 0], [0, -60], [0, -360]], k: ss(seg(u, 0, 14.6)) }; },
});
def({ // S26 the route traces a racing circuit around the edge; fresh zones light; marker circles at the far corners
  cam: [[0, 0, -380, 1.5], [4, 0, 0, .95], [12, 0, 0, .9], [15, 0, 420, 1.5]],
  snaps: [1.6, 4.2, 6.8, 9.4, 11.6, 12.6],
  draw(u) {
    wall(-2000); const F = K.floorPlan();
    const zones = [[-700, -420, 140, 840], [560, -420, 140, 840], [-700, -420, 1400, 140]];
    zones.forEach((z, i) => { const l = ss(seg(u, 5 + i * 1.6, 6 + i * 1.6)); if (l > 0) fillOnly(rect(...z), P().glow, { alpha: .6 * l }); });
    for (const [cx, cy, t0] of [[-620, -340, 10.8], [620, -340, 11.8]]) { const c = ss(seg(u, t0, t0 + .8)); if (c > 0) stroke(arc(cx, cy, 90, 80, -1, -1 + TAU * c, 40), 10, { line: K.BASE.coral }); }
  },
  route(u) { return { pts: [[0, -330], [0, 380], [-600, 380], [-620, -320], [620, -320], [620, 380], [0, 380], [0, 420]], k: ss(seg(u, 0, 14.6)) }; },
});
def({ // S27 pyramids of paper fruit; coral scent lines curl from an oven around her; a baguette drops in
  cam: [[0, -500, -80, 1.2], [6, 0, -80, 1], [15, 400, -100, 1.4]],
  snaps: [1.0, 2.6, 4.2, 7.0, 10.0, 12.0],
  draw(u) {
    wall(240); ground(240);
    [[-760, K.BASE.blue], [-500, P().glow], [-240, P().card2]].forEach(([x, c], i) => { const p = pk(u, .8 + i * 1.6); push(); translate(x, 240); scale(p); K.card(rect(-110, -40, 220, 40), P().card2); K.fruitPile(0, -40, 1, c); pop(); });
    K.card(rr(420, -200, 300, 440, 20), P().card2); K.card(rr(460, -120, 220, 160, 14), P().ink); fillOnly(rr(480, -100, 180, 120, 10), K.BASE.coral, { alpha: .35 });
    const x = lerp(-300, 220, ss(seg(u, 2, 9)));
    K.shopper(x, 240, .95, { walk: u > 2 && u < 9 ? walkPh(u) : null, basket: true, items: items(u > 12 ? 27 : 26) });
    for (let i = 0; i < 3; i++) { const f = ss(seg(u, 5 + i * .6, 8 + i * .6)); if (f > 0) stroke(spline([[460, -140 - i * 30], [300, -260 - i * 40], [150, -120], [x + 40, -320 + i * 40]], false).slice(0, Math.max(2, Math.floor(f * 25))), 6, { line: K.BASE.coral }); }
    const b = seg(u, 10.6, 11.6); if (b > 0 && b < 1) { push(); translate(x + 40, lerp(-600, 40, ei(b))); K.ITEM.baguette(0, 0); pop(); }
  },
  route(u) { return { pts: [[-1100, 280], [-760, 280], [-240, 280], [220, 280], [420, 280], [1100, 280]], k: ss(seg(u, 0, 14.6)) }; },
});
def({ // S28 four end-of-aisle displays slam up as she passes, each faster; the basket fills
  cam: [[0, -600, -80, 1.1], [15, 600, -80, 1.1]],
  snaps: [2.4, 5.6, 8.2, 10.2, 11.6, 13.0],
  draw(u) {
    wall(240); ground(240);
    const ts = [2.4, 5.6, 8.2, 10.2], kinds = ['cereal', 'jar', 'chips', 'tin'];
    ts.forEach((t0, i) => { const p = pk(u, t0, .3 - i * .05); push(); translate(-760 + i * 470, 240); scale(1, p); K.card(rect(-120, -320, 240, 320), P().card); for (let r = 0; r < 3; r++) for (let c = 0; c < 3; c++) K.ITEM[kinds[i]](-70 + c * 70, -220 + r * 100 + 90); pop(); });
    const x = lerp(-1000, 900, seg(u, 0, 14.4));
    K.shopper(x, 240, .9, { walk: walkPh(u, 12), basket: true, items: items(u > 11 ? 28 : 27) });
  },
  route(u) { return { pts: [[-1200, 280], [-760, 280], [-290, 280], [180, 280], [650, 280], [1200, 280]], k: ss(seg(u, 0, 14.6)) }; },
});
def({ // S29 a coral highlight bar at adult eye level, then a second at a child's eye line
  cam: [[0, -300, -100, 1.3], [6, 0, -100, 1], [15, 300, -40, 1.3]],
  snaps: [1.4, 4.2, 6.8, 9.4, 12.0],
  draw(u) {
    wall(260); ground(260);
    for (let i = 0; i < 4; i++) { push(); translate(-600 + i * 400, 260); K.shelfUnit(-180, 0, 360, 560, { seed: i + 71, rows: 5 }); pop(); }
    const a = ss(seg(u, 2.6, 4.2)), b = ss(seg(u, 8.4, 10));
    if (a > 0) K.card(rect(-800, -180, 1600 * a, 30), K.BASE.coral, { lw: 4, alpha: .9 });
    if (b > 0) K.card(rect(-800, 60, 1600 * b, 30), K.BASE.coral, { lw: 4, alpha: .9 });
    K.shopper(-200, 260, 1, { face: -1 }); if (u > 7.4) K.shopper(80, 260, .55 * pk(u, 7.4), { face: -1 });
  },
  route(u) { return { pts: [[-1100, 300], [-600, 300], [-200, 300], [80, 300], [1100, 300]], k: ss(seg(u, 0, 14.6)) }; },
});
def({ // S30 carton, egg box and loaf glow in three corners; the route links them in a giant triangle; the scale wobbles again
  cam: [[0, 0, 0, .95], [9, 0, 0, .9], [11, 0, 100, .8], [15, 0, 160, 1.3]],
  snaps: [1.4, 3.4, 5.4, 8.6, 10.6, 12.8],
  draw(u) {
    wall(-2000); K.floorPlan();
    [[-560, -320, 'carton'], [560, -320, 'eggs'], [0, 320, 'loaf']].forEach(([x, y, k], i) => { const p = pk(u, 1.2 + i * 2); fillOnly(ell(x, y - 40, 110 * p, 100 * p), P().glow, { alpha: .7 }); push(); translate(x, y); scale(p * 1.3); if (k === 'carton') K.carton(0, 0, .55); else K.ITEM[k](0, 0); pop(); });
    if (u > 10) { const r = pk(u, 10, .5); push(); translate(0, 420); scale(r * .7); K.balance(0, 0, 1, Math.sin(u * 3.6) * .18); pop(); }
  },
  route(u) { return { pts: [[0, 420], [-560, -300], [560, -300], [0, 300], [0, 420]], k: ss(seg(u, 6.4, 14.6)) }; },
});

// ═══ ACT IV · Ch8 The Global Check ═══
def({ // S31 a short in-and-out route just inside the door; a small fridge pops up by the entrance
  cam: [[0, 0, 420, 1.6], [5, 0, 100, .95], [15, 0, 300, 1.4]],
  snaps: [2.0, 4.6, 7.2, 9.8, 12.4],
  draw(u) {
    wall(-2000); K.floorPlan();
    const p = pk(u, 4.4); push(); translate(-220, 330); scale(p); K.card(rect(-80, -60, 160, 60), K.BASE.blue); K.card(rect(-70, -54, 140, 46), P().glow, { shadow: false, lw: 4 }); pop();
    for (let i = 0; i < 3; i++) { const k = ((u - 6) * .25 + i / 3) % 1; if (u > 6) { const pt = along([[0, 420], [-220, 300], [0, 420]], k); K.tinyShopper(pt[0], pt[1], 1.2, u * 8); } }
  },
  route(u) { return { pts: [[0, 540], [0, 420], [-220, 300], [-80, 360], [0, 420], [300, 300]], k: ss(seg(u, 0, 14.6)) }; },
});
def({ // S32 a spinning paper globe; three generic shopfronts with fridges by the door; commuters dash
  cam: [[0, 0, -200, 1.4], [5, 0, -100, .9], [15, 500, -60, 1.3]],
  snaps: [1.2, 3.8, 6.4, 8.8, 11.2, 13.2],
  draw(u) {
    wall(260); ground(260);
    K.globe(0, -280, 160, u * .8);
    for (let i = 0; i < 3; i++) { const p = pk(u, 3.6 + i * 2.4); push(); translate(-600 + i * 600, 260); scale(p); K.card(rect(-220, -340, 440, 340), [P().card, P().card2, P().milk][i]); K.card(rect(-180, -280, 150, 280), P().glow); K.card(rect(-160, -240, 110, 200), K.BASE.blue, { lw: 4 }); for (let r = 0; r < 3; r++) fillOnly(rect(-150, -220 + r * 60, 90, 40), P().milk); K.card(rect(30, -260, 160, 120), P().glow); pop(); }
    for (let i = 0; i < 3; i++) { const k = ((u * .5 + i * .33) % 1); K.shopper(-600 + i * 600 + Math.sin(k * Math.PI) * 120 - 60, 260, .5, { walk: walkPh(u, 14), face: k < .5 ? -1 : 1 }); }
  },
  route(u) { return { pts: [[-1100, 300], [-600, 300], [-700, 100], [-600, 300], [0, 300], [-100, 100], [0, 300], [600, 300], [500, 100], [600, 300], [1100, 300]], k: ss(seg(u, 0, 14.6)) }; },
});
def({ // S33 three big stores on three continents; trucks back into each dock on the same beat; three blue back walls glow
  cam: [[0, 0, -120, 1.2], [5, 0, -80, .8], [15, 0, -40, 1.2]],
  snaps: [1.4, 4.0, 6.6, 9.2, 11.8],
  draw(u) {
    wall(240); ground(240);
    for (let i = 0; i < 3; i++) { const p = pk(u, 1.2 + i * .6); push(); translate(-700 + i * 700, 240); scale(p * .85); K.card(rect(-300, -480, 600, 480), P().card); K.fridgeWall(-260, -260, 520, 200, { glow: .5 + .5 * Math.sin(u * 3), doors: 3 }); K.card(rect(-100, -200, 200, 200), P().glow); pop();
      const tx_ = lerp(-260, 60, ss(seg(u, 7, 9))) ; const bump = u > 9 ? spring(u - 9, 8, .3) : 0; push(); translate(-700 + i * 700 + tx_ * .85 - (1 - bump) * 4, 240); K.truck(0, 0, .45, { face: -1 }); pop(); }
  },
  route(u) { return { pts: [[-1100, 270], [-700, 270], [-700, 0], [0, 270], [0, 0], [700, 270], [700, 0], [1100, 0]], k: ss(seg(u, 0, 14.6)) }; },
});
def({ // S34 two floor plans: the small store's cold box slides to the front; the big store's won't budge
  cam: [[0, 0, 0, .95], [15, 0, 0, 1.15]],
  snaps: [2.0, 4.6, 7.0, 8.6, 10.2, 12.6],
  draw(u) {
    wall(-2000);
    K.floorPlan({ x: -900, y: -300, w: 700, h: 600, aisles: 3, dairy: false });
    K.floorPlan({ x: 100, y: -380, w: 800, h: 760, aisles: 5, dairy: false });
    const s1 = ss(seg(u, 2.4, 4.4)); K.card(rect(-850, lerp(-280, 220, s1), 160, 50), K.BASE.blue, { lw: 5 });
    const tries = [7, 8.6, 10.2]; let jig = 0; tries.forEach(t0 => { const f = seg(u, t0, t0 + .5); jig += Math.sin(f * Math.PI) * 18; });
    K.card(rect(160, -360 + jig, 680, 50), K.BASE.blue, { lw: 5 });
  },
  route(u) { return { pts: [[-550, 540], [-550, 300], [-770, 260], [-550, 300], [500, 380], [500, -300], [500, -330]], k: ss(seg(u, 0, 14.6)) }; },
});

// ═══ Ch9 The Turn ═══
def({ // S35 a fridge lowered by the door; pipes snake across the store to reach it; blank coins pile up and topple
  cam: [[0, -200, -100, 1.5], [3, -200, 200, 1.4], [8, -450, 0, 1.25], [12, 350, 220, 1.45], [15, 400, 280, 1.6]],
  snaps: [1.6, 4.2, 6.8, 9.4, 11.6, 12.6],
  draw(u) {
    wall(-2000); K.floorPlan();
    const lw_ = ei(seg(u, .8, 1.8)); push(); translate(-200, lerp(-500, 360, lw_)); K.card(rect(-80, -50, 160, 60), K.BASE.blue); pop(); if (u < 1.8) stroke([[-200, -900], [-200, lerp(-500, 310, lw_)]], 3);
    const pipe = ss(seg(u, 2.6, 8));
    const P_ = [[-400, -360], [-650, -360], [-650, 100], [-400, 160], [-420, 330], [-260, 340]]; const n = Math.max(2, Math.floor(pipe * 30));
    const pts = spline(P_, false, 6); stroke(pts.slice(0, Math.max(2, Math.floor(pts.length * pipe))), 16, { line: P().grey }); stroke(pts.slice(0, Math.max(2, Math.floor(pts.length * pipe))), 6, { line: P().glow });
    const c = Math.min(12, Math.floor(seg(u, 8, 11.5) * 12)), top = u > 12 ? ei(seg(u, 12, 12.8)) : 0;
    for (let i = 0; i < c; i++) K.coin(400 + top * i * 14 * (i % 2 ? 1 : -1), 300 - i * 22 + top * i * 20, 1);
  },
  route(u) { return { pts: [[0, 540], [0, 420], [-200, 360], [0, 300], [400, 300], [400, 280]], k: ss(seg(u, 0, 14.6)) }; },
});
def({ // S36 two storefronts; shoppers drop blank slips into a box outside the one they choose; the milk-at-the-front store's shutter comes down
  cam: [[0, 0, -100, 1.2], [6, 0, -80, .95], [15, -380, -60, 1.3]],
  snaps: [1.8, 4.4, 7.0, 9.6, 11.6, 12.6],
  draw(u) {
    wall(240); ground(240);
    for (const [cx, front] of [[-420, 0], [420, 1]]) { K.card(rect(cx - 300, -360, 600, 600), P().card); K.card(rect(cx - 250, -300, 500, 420), P().glow); if (front) K.card(rect(cx - 220, -120, 140, 240), K.BASE.blue, { lw: 4 }); else K.card(rect(cx - 230, -280, 460, 80), K.BASE.blue, { lw: 4 }); K.card(rr(cx + 160, 140, 90, 100, 8), P().card2); }
    const sh = ss(seg(u, 11.4, 12.8)); if (sh > 0) K.card(rect(170, -300, 500, 420 * sh), P().card2, { shade: () => { for (let i = 0; i < 10; i++) fillOnly(rect(170, -300 + i * 44, 500, 6), P().grey); } });
    for (let i = 0; i < 6; i++) { const t0 = 2 + i * 1.4, f = seg(u, t0, t0 + .6), cx = i === 4 ? 420 : -420; K.shopper(cx + 160 + (i % 2 ? 60 : -60), 240, .5, { face: 1, reach: f > 0 && f < 1 }); if (f > 0 && f < 1) K.card(rect(cx + 190, lerp(60, 140, f), 30, 20), P().milk, { lw: 3, shadow: false }); }
  },
  route(u) { return { pts: [[-1100, 280], [-420, 280], [-260, 260], [420, 280], [-420, 280], [-420, 120]], k: ss(seg(u, 0, 14.6)) }; },
});
def({ // S37 the balance scale returns; truck pan lowers first, then the price-gun pan; it clicks perfectly level
  cam: [[0, 0, -260, 1.5], [6, 0, -220, 1.1], [15, 0, -240, 1.4]],
  snaps: [1.4, 4.4, 7.4, 10.4, 12.6],
  draw(u) {
    wall(260); ground(260);
    const tilt = u < 4.4 ? Math.sin(u * 3) * .12 : u < 7.4 ? lerp(0, -.22, ss(seg(u, 4.4, 5.4))) : u < 10.4 ? lerp(-.22, .08, ss(seg(u, 7.4, 8.6))) : .08 * (1 - spring(u - 10.4, 9, .45));
    K.balance(0, 260, 1.2, tilt);
    if (u > 10.4) { const f = seg(u, 10.4, 11); if (f < 1) stroke(arc(0, -150, 60 + f * 200, 60 + f * 200, 0, TAU, 40), 6, { line: P().glow, alpha: 1 - f }); }
  },
  route(u) { return { pts: [[-1100, 300], [-400, 300], [0, 300], [0, -140], [400, 300], [1100, 300]], k: ss(seg(u, 0, 14.6)) }; },
});

// ═══ Ch10 The Kicker ═══
def({ // S38 she walks the glowing route again while sepia ghosts flicker over the aisles
  cam: [[0, 0, -120, 1.2], [15, 0, -140, 1.1]],
  snaps: [2.0, 4.6, 7.2, 9.8, 12.4],
  draw(u) {
    const pr = aisle(u, { travel: ss(seg(u, 0, 15)) * 2600, far: 5200 });
    const ghosts = [(x, y) => K.turnstile(x, y, 1.1, u), (x, y) => K.float_(x, y, .7), (x, y) => K.card(rect(x - 180, y - 260, 360, 260), K.SEPIA.card2), (x, y) => K.truck(x, y, .6)];
    ghosts.forEach((G, i) => { const t0 = 2 + i * 2.6, f = seg(u, t0, t0 + 2.2); if (f > 0 && f < 1) { g.globalAlpha = Math.sin(f * Math.PI) * (Math.floor(u * 12) % 3 ? .55 : .35); K.setPal(1); G(i % 2 ? 300 : -300, 200); K.setPal(0); g.globalAlpha = 1; } });
    K.shopper(0, 420, 1.15, { walk: walkPh(u), basket: true, items: items(38), face: 1 });
  },
  route(u) { return { pts: [[0, 560], [0, 420], [0, -60], [0, -118]], k: ss(seg(u, 0, 14.6)) }; },
});
def({ // S39 THE REVEAL: up through the ceiling — every route forms one giant carton outline; the real carton glows at its peak
  cam: [[0, 0, -100, 1.3], [3, 0, 0, .8], [9, 0, 0, .52], [15, 0, -560, .6]], reveal: true,
  snaps: [1.2, 3.0, 6.2, 9.0, 12.0],
  draw(u) {
    if (u < 3) { const pr = aisle(u, { travel: 2600 + u * 100 }); const up = ss(seg(u, 1.4, 3)); fillOnly(rect(-4000, -4000, 8000, 3500 + up * 3200), P().milk, { alpha: up }); return; }
    wall(-4000); K.floorPlan({ x: -1300, y: -900, w: 2600, h: 1800, aisles: 9 });
    const k = seg(u, 3.4, 11.5);
    const OUT = [[-520, 760], [-520, -200], [0, -700], [520, -200], [520, 760], [-520, 760]];
    for (let i = 0; i < 18; i++) { const a = i / 18, b = (i + 1) / 18, f = ss(seg(k, a * .7, a * .7 + .3)); const A = along(OUT, a), B = along(OUT, b); const sx = (hash(i) - .5) * 2400, sy = (hash(i + 9) - .5) * 1600; stroke([[lerp(sx, A[0], f), lerp(sy, A[1], f)], [lerp(sx + 120, B[0], f), lerp(sy + 40, B[1], f)]], 14, { line: K.BASE.coral }); }
    const st = ss(seg(u, 10.6, 12)); K.carton(0, -700 + 60, 1.4 * st, { glow: st * (1 + .3 * Math.sin(u * 3)) });
    if (st > 0) for (let i = 0; i < 8; i++) { const a = i / 8 * TAU + u * .2; stroke([[Math.cos(a) * 170, -820 + Math.sin(a) * 170], [Math.cos(a) * (220 + 30 * Math.sin(u * 4 + i)), -820 + Math.sin(a) * (220 + 30 * Math.sin(u * 4 + i))]], 6, { line: K.BASE.glow, alpha: st }); }
  },
  route(u) { return { pts: [[0, 1000], [0, 760]], k: 1 }; },
});
def({ // S40 a straight line door → dairy wall; the carton clicks into the basket gap; push into its glowing top → black
  cam: [[0, 0, -60, 1], [6, 0, -100, 1], [9, 0, -200, 1.6], [12.6, 0, -230, 2.4], [14.4, 0, -268, 9], [15, 0, -268, 14]], end: true,
  snaps: [2.0, 5.0, 8.6, 10.8, 12.6],
  draw(u) {
    wall(260); ground(260);
    K.fridgeWall(-600, -40, 1200, 420, { glow: 1, doors: 5 });
    K.shopper(lerp(0, 0, 0), 260, 1, { face: 1, walk: u < 8 ? walkPh(u) : null });
    const click = u > 10.6; push(); translate(140, 240); scale(.8); K.basket(0, 0, 1, items(40), click); pop();
    if (!click) { const f = seg(u, 9, 10.6); if (f > 0) K.carton(lerp(300, 140, eo(f)), lerp(-120, 150, eo(f)) - Math.sin(f * Math.PI) * 120, .5); }
    if (u > 12.6) { push(); translate(0, -150); K.carton(0, 0, 1.4, { glow: 1 }); pop(); }
  },
  route(u) { return { pts: [[0, 560], [0, 300], [0, -20]], k: ss(seg(u, 0, 8)) }; },
  card: { t0: 13.2, t1: 15, end: true, text: ['Truck first.', 'Marketer second.'] },
});

export const SCENES = sceneList;
export const CHAPTERS = [[0, 'The Longest Walk'], [3, 'The Theory Everyone Knows'], [7, 'Before the Aisle'], [11, 'The Maze, 1916'], [15, 'The Cold Revolution'], [19, 'Follow the Truck'], [24, 'The Racetrack'], [30, 'The Global Check'], [34, 'The Turn'], [37, 'The Kicker']];
