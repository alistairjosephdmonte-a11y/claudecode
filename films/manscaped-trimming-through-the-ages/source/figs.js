// Characters and props for "Trimming Through the Ages". One rig for every person (≈2.5 heads tall, dot eyes with a
// white-wax catchlight, pink cheeks, tube limbs, mitten hands), dressed per era; plus the three squirrels.
// Rig data is plain geometry; everything is drawn through the crayon line/fill + knock-out system (rig.part).
import { line, fill, dab, ellipse, handCircle, xf, smooth, text, sx, sy, CAM } from './crayon.js';
import { part, tube, curve } from './rig.js';
import { PAL } from './pal.js';
import { hash, clamp, lerp } from '/core/lib.js';
export const K = PAL.crayon;
const LW = 6;

// world-space handwriting (crayon.text works in screen pixels)
export function say(L, str, x, y, o = {}) { return text(L, str, sx(x), sy(y), { ...o, size: (o.size ?? 56) * CAM.s }); }
const F = (col, sd, o = {}) => ({ col, p: 0.85, gap: 7, w: 9, ang: 0.9, seed: sd, ...o });

// ——————————————————————— people ———————————————————————
// o: x, y (feet), s, flip, r, view 'front'|'q'|'side'|'back', expr, pose 'stand'|'walk'|'sit'|'float', ph,
//    armL/armR = hand position [x, y] in local coords (y up is negative), outfit, hair, beard, colours, prop(C, T, handR, handL)
export const CAST = {
  gerald:      { outfit: 'loin', hair: 'shaggy', hairCol: K.brown, skin: K.peach, nose: true, eyes: 'sleepy', cloth: K.brown },
  pharaoh:     { outfit: 'kilt', hair: 'nemes', cloth: K.white, collar: K.ochre },
  barber:      { outfit: 'kilt', hair: 'neat', hairCol: K.ink, cloth: K.white, collar: K.sky },
  philosopher: { outfit: 'robe', hair: 'bald', hairCol: K.white, beard: 'huge', cloth: K.white, sash: K.sky },
  senator:     { outfit: 'robe', hair: 'wreath', hairCol: K.brown, cloth: K.red, sash: K.white },
  clerk:       { outfit: 'robe', hair: 'neat', hairCol: K.brown, cloth: K.ochre, sash: K.white },
  knight:      { outfit: 'armour', hair: 'helmet', cloth: K.grey, scale: 0.86 },
  squire:      { outfit: 'tunic', hair: 'neat', hairCol: K.orange, cloth: K.green },
  smith:       { outfit: 'apron', hair: 'bald', hairCol: K.brown, beard: 'short', cloth: K.brown, shirt: K.red },
  inventor:    { outfit: 'tunic', hair: 'beret', hairCol: K.brown, beard: 'long', cloth: K.sky, capCol: K.violet },
  gentleman:   { outfit: 'waistcoat', hair: 'tophat', hairCol: K.brown, beard: 'moustache', cloth: K.ink, vest: K.red },
  butler:      { outfit: 'suit', hair: 'neat', hairCol: K.grey, cloth: K.ink, tie: K.white },
  salesman:    { outfit: 'suit', hair: 'neat', hairCol: K.yellow, cloth: K.sky, tie: K.red, slim: true },
  astronaut:   { outfit: 'space', hair: 'space', cloth: K.white },
  controller:  { outfit: 'suit', hair: 'neat', hairCol: K.brown, cloth: K.white, tie: K.ink, specs: true },
};
export function person(C, who, o) {
  const P = { ...CAST[who], ...o }, k = P.flip ? -1 : 1, s = (P.s || 1) * (P.scale || 1), sd = P.seed || (hash(who.length * 7.7) * 900 | 0) * 3 + 100;
  const T = pts => xf(pts, { x: P.x, y: P.y, s, sx: k, r: P.r || 0 });
  const dr = P.draw ?? 1, fd = P.fillDraw ?? dr;
  const L = (n, x = {}) => ({ w: LW, seed: sd + n, draw: dr, ...x });
  const view = P.view || 'front', side = view === 'side', back = view === 'back', q = view === 'q';
  const skin = F(K.peach, sd + 1, { p: 0.55, gap: 8, w: 10, ang: 0.5, draw: fd });
  const cloth = F(P.cloth || K.sky, sd + 2, { draw: fd });
  const ex = P.expr || (P.eyes === 'sleepy' ? 'sleepy' : 'neutral');
  // —— legs (stubby tubes) + shoes
  const ph = P.ph || 0, sw = Math.sin(ph * Math.PI * 2);
  let legs = [[[-16, -80], [-18, -6]], [[16, -80], [18, -6]]];
  if (P.pose === 'walk') legs = [[[-12, -80], [-12 + 22 * sw, -6]], [[12, -80], [12 - 22 * sw, -6]]];
  if (P.pose === 'sit') legs = [[[-16, -80], [40, -78], [42, -16]], [[16, -80], [62, -76], [64, -16]]];
  if (P.pose === 'float') legs = [[[-14, -80], [-26 + 8 * sw, -14]], [[14, -80], [24 - 8 * sw, -10]]];
  const legCol = P.outfit === 'armour' ? K.grey : P.outfit === 'space' ? K.white : ['loin', 'kilt', 'robe'].includes(P.outfit) ? K.peach : K.ink;
  if (P.outfit !== 'robe' || P.pose === 'sit') legs.forEach((lg, i) => {
    part(C, T(tube(lg, 30, 26)), legCol === K.peach ? skin : F(legCol, sd + 5 + i, { draw: fd, p: 0.8 }), L(5 + i));
    const f = lg[lg.length - 1];
    part(C, T(smooth([[f[0] - 18, f[1] + 6], [f[0] - 16, f[1] - 10], [f[0] + 8, f[1] - 12], [f[0] + 26, f[1] - 2], [f[0] + 24, f[1] + 8]], 3)), F(P.outfit === 'armour' ? K.grey : P.outfit === 'space' ? K.white : P.outfit === 'kilt' || P.outfit === 'robe' ? K.ochre : K.brown, sd + 7 + i, { draw: fd }), L(7 + i, { w: 5 }));
  });
  // —— back arm
  const shL = [-40, -166], shR = [40, -166];
  const hL = P.armL || (P.pose === 'float' ? [-80, -190] : [-76, -108]), hR = P.armR || (P.pose === 'float' ? [80, -196] : [76, -108]);
  const arm = (sh, h, n) => { const el = [(sh[0] + h[0]) / 2 + (h[0] < sh[0] ? -6 : 6), (sh[1] + h[1]) / 2 + 6];
    const sleeve = P.outfit === 'loin' || P.outfit === 'kilt' ? skin : P.outfit === 'apron' ? F(P.shirt, sd + 9, { draw: fd }) : P.outfit === 'waistcoat' ? F(K.white, sd + 9, { draw: fd }) : cloth;
    part(C, T(tube([sh, el, h], 24, 20)), sleeve, L(n));
    part(C, T(smooth([[h[0] - 15, h[1] - 4], [h[0] - 10, h[1] - 16], [h[0] + 8, h[1] - 16], [h[0] + 16, h[1] - 2], [h[0] + 8, h[1] + 13], [h[0] - 10, h[1] + 13]], 3)), P.outfit === 'armour' ? F(K.grey, sd + 11) : P.outfit === 'space' ? F(K.white, sd + 11) : skin, L(n + 1, { w: 4.5 }));
    part(C, T(handCircle(h[0] + (h[0] > 0 ? -16 : 16) * (side ? 0 : 1), h[1] - 6, 7, sd + n, 0, 10)), P.outfit === 'armour' ? F(K.grey, sd + 12) : P.outfit === 'space' ? F(K.white, sd + 12) : skin, L(n + 2, { w: 4 }));   // the thumb
  };
  if (!side) arm(shL, hL, 20);
  // —— body by outfit
  const torso = smooth([[-46, -178], [46, -178], [54, -120], [56, -78], [-56, -78], [-54, -120]], 4);
  const out = P.outfit;
  if (out === 'loin') { part(C, T(torso), skin, L(30)); part(C, T([[-58, -96], [58, -96], [62, -58], [30, -50], [0, -60], [-30, -50], [-62, -58]]), F(P.cloth, sd + 31, { draw: fd }), L(31)); line(C.l, T([[-10, -150], [-4, -140]]), L(32, { w: 4, p: 0.6 })); }
  else if (out === 'kilt') { part(C, T(torso), skin, L(30)); part(C, T([[-58, -96], [58, -96], [70, -34], [-70, -34]]), F(P.cloth, sd + 31, { draw: fd }), L(31)); line(C.l, T([[0, -96], [0, -36]]), L(33, { w: 4, p: 0.6 }));
    part(C, T(smooth([[-50, -178], [50, -178], [44, -140], [0, -128], [-44, -140]], 4)), F(P.collar, sd + 34, { draw: fd, p: 0.95 }), L(34)); [-30, -10, 10, 30].forEach((x, i) => line(C.l, T([[x, -174], [x * 0.9, -138]]), L(35 + i, { w: 3.5, col: K.ink, p: 0.7 }))); }
  else if (out === 'robe') { const robe = smooth([[-48, -178], [48, -178], [58, -100], [66, -10], [-66, -10], [-58, -100]], 4); part(C, T(robe), cloth, L(30));
    part(C, T([[30, -178], [50, -170], [-40, -40], [-60, -50]]), F(P.sash, sd + 31, { draw: fd, p: 0.9 }), L(31, { w: 4.5 })); [-30, 0, 30].forEach((x, i) => line(C.l, T(curve([[x, -60], [x + 4, -36], [x - 2, -12]], 4)), L(32 + i, { w: 3.5, p: 0.5 }))); }
  else if (out === 'tunic' || out === 'apron') { part(C, T(smooth([[-46, -178], [46, -178], [54, -120], [64, -50], [-64, -50], [-54, -120]], 4)), out === 'apron' ? F(P.shirt, sd + 2, { draw: fd }) : cloth, L(30));
    part(C, T([[-56, -96], [56, -96], [56, -88], [-56, -88]]), F(K.brown, sd + 31, { draw: fd }), L(31, { w: 4 }));
    if (out === 'apron') part(C, T([[-34, -160], [34, -160], [44, -50], [-44, -50]]), F(K.brown, sd + 32, { draw: fd, p: 0.9 }), L(32)); }
  else if (out === 'armour') { part(C, T(torso), F(K.grey, sd + 2, { draw: fd, p: 0.75 }), L(30)); part(C, T([[-60, -100], [60, -100], [66, -54], [-66, -54]]), F(K.grey, sd + 31, { draw: fd, p: 0.9 }), L(31));
    line(C.l, T([[-50, -140], [50, -140]]), L(32, { w: 4, p: 0.7 })); line(C.l, T([[-54, -116], [54, -116]]), L(33, { w: 4, p: 0.7 }));
    [-30, 0, 30].forEach((x, i) => dab(C.l, ...T([[x, -128]])[0], 4 * s, { col: K.ink, p: 0.9, seed: sd + 34 + i }));
    line(C.l, T([[-38, -164], [-24, -150]]), L(37, { w: 5, col: K.white, p: 1 })); }
  else if (out === 'suit' || out === 'waistcoat') { const jk = out === 'waistcoat' ? K.ink : P.cloth;
    part(C, T(smooth([[-50, -178], [50, -178], [56, -120], [60, -64], [-60, -64], [-56, -120]], 4)), F(jk, sd + 2, { draw: fd, p: out === 'waistcoat' ? 0.75 : 0.85 }), L(30));
    if (out === 'waistcoat') { part(C, T([[-22, -176], [22, -176], [26, -80], [-26, -80]]), F(P.vest, sd + 31, { draw: fd }), L(31)); [0, 1, 2].forEach(i => dab(C.l, ...T([[0, -150 + i * 22]])[0], 3.5 * s, { col: K.ochre, p: 1, seed: sd + 40 + i })); line(C.l, T(curve([[4, -140], [30, -130], [24, -118]], 4)), L(44, { w: 3, col: K.ochre })); }
    else { part(C, T([[-18, -178], [18, -178], [0, -140]]), F(K.white, sd + 31, { draw: fd }), L(31, { w: 4 })); part(C, T([[-6, -170], [6, -170], [P.slim ? 4 : 9, -96], [0, -88], [P.slim ? -4 : -9, -96]]), F(P.tie, sd + 32, { draw: fd, p: 0.95 }), L(32, { w: 4 }));
      line(C.l, T([[-18, -178], [-10, -130]]), L(33, { w: 4 })); line(C.l, T([[18, -178], [10, -130]]), L(34, { w: 4 })); } }
  else if (out === 'space') { part(C, T(smooth([[-58, -180], [58, -180], [66, -120], [64, -58], [-64, -58], [-66, -120]], 4)), F(K.white, sd + 2, { draw: fd, p: 0.95 }), L(30));
    part(C, T([[-28, -150], [28, -150], [28, -112], [-28, -112]]), F(K.grey, sd + 31, { draw: fd }), L(31, { w: 4 })); [K.red, K.sky, K.yellow].forEach((c, i) => dab(C.f, ...T([[-14 + i * 14, -132]])[0], 5 * s, { col: c, p: 1, seed: sd + 32 + i }));
    part(C, T([[-64, -74], [64, -74], [64, -60], [-64, -60]]), F(K.grey, sd + 35, { draw: fd }), L(35, { w: 4 })); }
  // —— head
  const hx = side ? 10 : q ? 6 : 0, hy = -236, R = 58;
  const head = ellipse(hx, hy, R, R * 0.96, 36);
  if (P.hair === 'nemes') part(C, T([[hx - 66, hy - 30], [hx + 66, hy - 30], [hx + 76, hy + 70], [hx + 40, hy + 76], [hx + 40, hy + 10], [hx - 40, hy + 10], [hx - 40, hy + 76], [hx - 76, hy + 70]]), F(K.yellow, sd + 50, { draw: fd }), L(50));
  if (P.hair === 'shaggy') part(C, T(smooth([[hx - 74, hy + 40], [hx - 82, hy - 20], [hx - 60, hy - 68], [hx, hy - 82], [hx + 60, hy - 68], [hx + 84, hy - 16], [hx + 76, hy + 44], [hx + 40, hy + 64], [hx - 40, hy + 64]], 5)), F(P.hairCol, sd + 50, { draw: fd, p: 0.9, ang: 1.4 }), L(50));
  if (P.hair === 'space') part(C, T(ellipse(hx, hy - 4, R + 22, R + 20, 36)), F(K.white, sd + 50, { draw: fd, p: 0.95 }), L(50));
  if (back) { part(C, T(head), P.hair === 'bald' || P.hair === 'space' ? (P.hair === 'space' ? F(K.white, sd + 51) : skin) : F(P.hairCol || K.brown, sd + 51, { draw: fd, ang: 1.3 }), L(51)); }
  else {
    part(C, T(head), skin, L(51));
    if (P.hair === 'space') { fill(C.f, T(ellipse(hx, hy, R - 4, R - 6, 30)), { col: K.sky, p: 0.25, gap: 12, w: 12, seed: sd + 52 }); line(C.l, T(ellipse(hx - 22, hy - 28, 14, 8, 10, 3.6, 5.6)), L(53, { w: 5, col: K.white, p: 1 })); }
    // face
    const fx = hx + (side ? 26 : q ? 16 : 0), ey = hy + 2, gap = side ? 0 : q ? 18 : 22;
    const eyeAt = side ? [[fx + 4, ey]] : [[fx - gap, ey], [fx + gap, ey]];
    eyeAt.forEach(([x, y], i) => {
      if (ex === 'sleepy' || ex === 'happy' || ex === 'faint') line(C.l, T(ex === 'happy' ? [[x - 7, y + 2], [x, y - 5], [x + 7, y + 2]] : ex === 'faint' ? [[x - 7, y - 6], [x + 7, y + 6]] : [[x - 8, y], [x, y + 4], [x + 8, y]]), L(60 + i, { w: 4.5 }));
      else { const r = ex === 'shock' ? 8 : 6; dab(C.l, ...T([[x, y]])[0], r * s, { col: K.ink, p: 1, seed: sd + 60 + i, gap: 2.5, w: 4 }); dab(C.l, ...T([[x - 2, y - 2]])[0], 1.8 * s, { col: K.white, p: 1, seed: sd + 62 + i, gap: 1.5, w: 2 }); }
      if (ex === 'faint') line(C.l, T([[x - 7, y + 6], [x + 7, y - 6]]), L(70 + i, { w: 4.5 }));
    });
    // brows
    if (ex === 'worried' || ex === 'eyebrow' || ex === 'shock' || ex === 'smug') eyeAt.forEach(([x, y], i) => {
      const up = ex === 'eyebrow' && i === eyeAt.length - 1 ? -12 : 0, tilt = ex === 'worried' ? (i ? 5 : -5) : ex === 'smug' ? (i ? -3 : 3) : 0;
      line(C.l, T([[x - 9, y - 16 - tilt + up], [x + 9, y - 16 + tilt + up]]), L(64 + i, { w: 4.5 }));
    });
    dab(C.f, ...T([[fx - (side ? -6 : gap + 10), ey + 20]])[0], 9 * s, { col: K.pink, p: 0.55, seed: sd + 66 }); if (!side) dab(C.f, ...T([[fx + gap + 10, ey + 20]])[0], 9 * s, { col: K.pink, p: 0.55, seed: sd + 67 });
    if (P.nose || side) part(C, T(side ? smooth([[fx + 24, ey + 4], [fx + 38, ey + 10], [fx + 26, ey + 18]], 3) : ellipse(fx, ey + 16, 11, 8, 16)), skin, L(68, { w: 4.5 }));
    const my = ey + (P.nose ? 32 : 26), mx = fx + (side ? 16 : 0);
    if (!['huge', 'long'].includes(P.beard) || (P.beardLen ?? 1) < 0.4) {
      const M = { neutral: [[mx - 8, my], [mx + 8, my]], happy: [[mx - 12, my - 2], [mx, my + 7], [mx + 12, my - 2]], smug: [[mx - 10, my + 2], [mx + 4, my + 2], [mx + 12, my - 5]], worried: [[mx - 10, my + 2], [mx - 4, my - 2], [mx + 2, my + 2], [mx + 8, my - 2], [mx + 12, my + 1]], sleepy: [[mx - 6, my], [mx + 6, my + 1]], eyebrow: [[mx - 8, my + 1], [mx + 8, my + 1]], faint: [[mx - 8, my + 3], [mx, my - 2], [mx + 8, my + 3]] }[ex];
      if (ex === 'shock') line(C.l, T(handCircle(mx, my + 2, 7, sd, 0, 10)), L(69, { w: 4.5 })); else line(C.l, T(M || [[mx - 8, my], [mx + 8, my]]), L(69, { w: 4.5 }));
    }
    if (P.specs) { [-1, 1].forEach((d, i) => line(C.l, T(handCircle(fx + d * gap, ey, 13, sd + 90 + i, 0.05, 16)), L(90 + i, { w: 4 }))); line(C.l, T([[fx - 9, ey], [fx + 9, ey]]), L(92, { w: 4 })); }
  }
  // beards
  const bl = P.beardLen ?? 1;
  if (P.beard === 'long' && !back && bl > 0.02) part(C, T(smooth([[hx - 40, hy + 18], [hx, hy + 34], [hx + 40, hy + 18], [hx + 32, hy + 30 + 60 * bl], [hx, hy + 40 + 70 * bl], [hx - 32, hy + 30 + 60 * bl]], 4)), F(P.hairCol, sd + 80, { p: 0.9, ang: 1.5, draw: fd }), L(80));
  if (P.beard === 'short' && !back) part(C, T(smooth([[hx - 44, hy + 10], [hx, hy + 30], [hx + 44, hy + 10], [hx + 34, hy + 46], [hx, hy + 58], [hx - 34, hy + 46]], 4)), F(P.hairCol, sd + 80, { p: 0.85, draw: fd }), L(80));
  if (P.beard === 'moustache' && !back) { [-1, 1].forEach((d, i) => part(C, T(smooth([[hx, hy + 22], [hx + d * 20, hy + 18], [hx + d * 34, hy + 22], [hx + d * 42, hy + 12], [hx + d * 40, hy + 26], [hx + d * 22, hy + 30], [hx, hy + 28]], 3)), F(P.hairCol, sd + 81 + i, { p: 0.95 }), L(81 + i, { w: 4 }))); }
  // hair / hats (outlined on outer edge only)
  if (!back) {
    if (P.hair === 'shaggy') part(C, T(smooth([[hx - 56, hy - 6], [hx - 50, hy - 44], [hx - 10, hy - 62], [hx + 36, hy - 56], [hx + 58, hy - 20], [hx + 40, hy - 26], [hx + 30, hy - 12], [hx + 14, hy - 28], [hx - 2, hy - 14], [hx - 18, hy - 28], [hx - 34, hy - 12], [hx - 44, hy - 24]], 3)), F(P.hairCol, sd + 84, { draw: fd, p: 0.9, ang: 1.4 }), L(84));
    if (P.hair === 'neat') part(C, T(smooth([[hx - 58, hy - 4], [hx - 54, hy - 40], [hx - 20, hy - 60], [hx + 30, hy - 58], [hx + 58, hy - 30], [hx + 56, hy - 6], [hx + 30, hy - 30], [hx - 20, hy - 34]], 4)), F(P.hairCol, sd + 85, { draw: fd, ang: 1.3 }), L(85));
    if (P.hair === 'wreath') { part(C, T(smooth([[hx - 58, hy - 4], [hx - 54, hy - 40], [hx - 20, hy - 60], [hx + 30, hy - 58], [hx + 58, hy - 30], [hx + 56, hy - 6], [hx + 30, hy - 30], [hx - 20, hy - 34]], 4)), F(P.hairCol, sd + 85, { draw: fd }), L(85));
      for (let i = 0; i < 9; i++) { const a = Math.PI * (1.1 + i * 0.1); part(C, T(xf(ellipse(0, 0, 13, 6, 12), { x: hx + 60 * Math.cos(a), y: hy - 20 + 46 * Math.sin(a), r: a + 1.6 })), F(K.green, sd + 86 + i, { p: 0.95 }), L(86 + i, { w: 3, col: K.green })); } }
    if (P.hair === 'nemes') { part(C, T([[hx - 62, hy - 22], [hx - 50, hy - 64], [hx + 50, hy - 64], [hx + 62, hy - 22], [hx + 40, hy - 26], [hx - 40, hy - 26]]), F(K.yellow, sd + 85, { draw: fd }), L(85)); for (let i = 0; i < 5; i++) line(C.l, T([[hx - 50 + i * 25, hy - 60], [hx - 56 + i * 28, hy - 26]]), L(86 + i, { w: 7, col: K.sky, p: 0.95 })); [-58, 58].forEach((x, i) => { for (let j = 0; j < 3; j++) line(C.l, T([[hx + x - 12, hy + 12 + j * 22], [hx + x + 12, hy + 12 + j * 22]]), L(92 + i * 3 + j, { w: 7, col: K.sky })); }); }
    if (P.hair === 'tophat') { part(C, T(smooth([[hx - 56, hy - 6], [hx - 50, hy - 40], [hx + 50, hy - 40], [hx + 56, hy - 6], [hx + 30, hy - 24], [hx - 30, hy - 24]], 4)), F(P.hairCol, sd + 85, { draw: fd }), L(85)); part(C, T([[hx - 78, hy - 50], [hx + 78, hy - 50], [hx + 78, hy - 38], [hx - 78, hy - 38]]), F(K.ink, sd + 86, { draw: fd }), L(86)); part(C, T([[hx - 46, hy - 150], [hx + 46, hy - 150], [hx + 44, hy - 48], [hx - 44, hy - 48]]), F(K.ink, sd + 87, { draw: fd }), L(87)); part(C, T([[hx - 44, hy - 72], [hx + 44, hy - 72], [hx + 44, hy - 58], [hx - 44, hy - 58]]), F(K.red, sd + 88), L(88, { w: 3.5 })); }
    if (P.hair === 'beret') { part(C, T(smooth([[hx - 66, hy - 26], [hx - 40, hy - 70], [hx + 20, hy - 78], [hx + 70, hy - 50], [hx + 60, hy - 30]], 4)), F(P.capCol, sd + 85, { draw: fd }), L(85)); part(C, T(smooth([[hx - 56, hy - 4], [hx - 52, hy - 30], [hx - 30, hy - 30], [hx - 38, hy + 6]], 3)), F(P.hairCol, sd + 86, { draw: fd }), L(86, { w: 4 })); }
    if (P.hair === 'helmet') { part(C, T([...smooth([[hx - 66, hy + 50], [hx - 68, hy - 30], [hx - 40, hy - 68], [hx, hy - 76], [hx + 40, hy - 68], [hx + 68, hy - 30], [hx + 66, hy + 50]], 5), [hx + 40, hy + 50], [hx + 40, hy - 26], [hx - 40, hy - 26], [hx - 40, hy + 50]]), F(K.grey, sd + 85, { draw: fd, p: 0.85 }), L(85)); part(C, T([[hx - 8, hy - 92], [hx + 8, hy - 92], [hx + 26, hy - 130], [hx - 6, hy - 118]]), F(K.red, sd + 86), L(86, { w: 4 })); line(C.l, T([[hx - 40, hy - 50], [hx - 20, hy - 60]]), L(87, { w: 5, col: K.white, p: 1 })); }
    if (P.hair === 'bald' && P.hairCol) { [-1, 1].forEach((d, i) => part(C, T(smooth([[hx + d * 56, hy - 10], [hx + d * 64, hy + 10], [hx + d * 52, hy + 24], [hx + d * 46, hy]], 3)), F(P.hairCol, sd + 85 + i), L(85 + i, { w: 4 }))); line(C.l, T([[hx - 20, hy - 40], [hx - 6, hy - 48]]), L(88, { w: 5, col: K.white, p: 1 })); }
  }
  // —— front arm
  arm(shR, hR, 100);
  if (P.beard === 'huge' && !back && bl > 0) part(C, T(smooth([[hx - 46, hy + 16], [hx - 30, hy + 30], [hx, hy + 34], [hx + 30, hy + 30], [hx + 46, hy + 16], [hx + 50, hy + 30 + 130 * bl], [hx + 10, hy + 50 + 150 * bl], [hx - 30, hy + 40 + 140 * bl], [hx - 52, hy + 30 + 110 * bl]], 5)), F(K.white, sd + 80, { p: 0.95, ang: 1.5 }), L(80, { col: K.grey }));
  if (P.prop) P.prop(C, T, hR, hL);
  return T;
}

// ——————————————————————— squirrels ———————————————————————
export const SQ = [{ col: K.rust, belly: K.ochre, prop: 'acorn' }, { col: K.ochre, belly: K.white, prop: 'hammer' }, { col: K.brown, belly: K.ochre, prop: 'specs' }];
// o: x, y (feet), s, flip, i (which squirrel), pose 'sit'|'stand'|'peek', suit (bool), prop override, draw
export function squirrel(C, o) {
  const Q = SQ[o.i || 0], k = o.flip ? -1 : 1, s = o.s || 1, sd = 3000 + (o.i || 0) * 60;
  const T = pts => xf(pts, { x: o.x, y: o.y, s, sx: k, r: o.r || 0 });
  const dr = o.draw ?? 1, L = (n, x = {}) => ({ w: 5, seed: sd + n, draw: dr, ...x });
  // tail: a big S-curve plume behind
  part(C, T(smooth([[-20, -20], [-70, -40], [-96, -100], [-80, -160], [-40, -176], [-20, -150], [-50, -130], [-56, -90], [-30, -50]], 5)), F(Q.col, sd, { p: 0.9, ang: 1.2, gap: 6 }), L(0));
  line(C.l, T(curve([[-40, -60], [-70, -110], [-56, -150]], 6)), L(1, { w: 3, p: 0.5 }));
  // body
  part(C, T(smooth([[-34, -6], [-38, -60], [-20, -96], [20, -96], [34, -60], [30, -6]], 4)), F(o.suit ? K.ink : Q.col, sd + 2, { p: 0.85 }), L(2));
  if (o.suit) { part(C, T([[-10, -94], [10, -94], [0, -60]]), F(K.white, sd + 3), L(3, { w: 3 })); part(C, T([[-3, -88], [3, -88], [5, -52], [-5, -52]]), F(K.red, sd + 4), L(4, { w: 3 })); }
  else part(C, T(ellipse(4, -46, 20, 30, 20)), F(Q.belly, sd + 3, { p: 0.8 }), L(3, { w: 3.5 }));
  // head
  part(C, T([[18, -150], [26, -176], [34, -146]]), F(Q.col, sd + 5), L(5, { w: 4 }));
  part(C, T(ellipse(14, -122, 34, 30, 24)), F(Q.col, sd + 6, { p: 0.85 }), L(6));
  part(C, T(ellipse(40, -114, 14, 10, 14)), F(Q.belly, sd + 7, { p: 0.85 }), L(7, { w: 3.5 }));
  dab(C.l, ...T([[50, -118]])[0], 4 * s, { col: K.ink, p: 1, seed: sd + 8 });
  dab(C.l, ...T([[22, -130]])[0], 5 * s, { col: K.ink, p: 1, seed: sd + 9, gap: 2.5, w: 3.5 }); dab(C.l, ...T([[20, -132]])[0], 1.6 * s, { col: K.white, p: 1, seed: sd + 10, gap: 1.5, w: 2 });
  dab(C.f, ...T([[32, -110]])[0], 6 * s, { col: K.pink, p: 0.6, seed: sd + 11 });
  // mitten paws
  const pw = o.paw || [36, -70];
  part(C, T(ellipse(pw[0], pw[1], 10, 8, 12)), F(Q.col, sd + 12), L(12, { w: 3.5 }));
  if (o.i === 2 && !o.suit) { line(C.l, T(handCircle(18, -128, 9, sd + 13, 0, 12)), L(13, { w: 3 })); line(C.l, T(handCircle(40, -128, 8, sd + 14, 0, 12)), L(14, { w: 3 })); }
  if (o.hold) o.hold(C, T, pw);
  return T;
}

// ——————————————————————— small props ———————————————————————
// a hand-lettered sign on a board; anchor = top-centre
export function sign(C, x, y, w, h, str, o = {}) {
  const sd = o.seed || 4000, dr = o.draw ?? 1;
  const P = xf([[-w / 2, 0], [w / 2, 4], [w / 2 - 4, h], [-w / 2 + 3, h - 3]], { x, y, r: o.r || 0 });
  part(C, P, F(o.col || K.ochre, sd, { p: 0.8, draw: dr }), { w: 5, seed: sd + 1, draw: dr });
  if (o.string) { const [a, b] = [P[0], P[1]]; line(C.l, [[a[0] + 10, a[1]], [x, y - o.string], [b[0] - 10, b[1]]], { w: 3.5, seed: sd + 2, draw: dr }); }
  const [cx, cy] = xf([[0, h * 0.62]], { x, y, r: o.r || 0 })[0];
  say(C.l, str, cx, cy, { size: o.size || Math.min(h * 0.5, w / str.length * 1.7), font: 'Gaegu', weight: 700, col: o.ink || K.ink, reveal: o.reveal ?? 1, seed: sd + 3, stroke: 1.5 });
}
export function acorn(C, x, y, s, sd = 4100) {
  part(C, xf(ellipse(0, 0, 14, 18, 16), { x, y, s }), F(K.ochre, sd), { w: 4, seed: sd + 1 });
  part(C, xf(smooth([[-17, -6], [-14, -18], [0, -24], [14, -18], [17, -6]], 3), { x, y, s }), F(K.brown, sd + 2), { w: 4, seed: sd + 3 });
  line(C.l, xf([[0, -24], [3, -32]], { x, y, s }), { w: 4, seed: sd + 4 });
}
// a scribbled hair "bush" mass: a lumpy cloud filled with spiral scribble (the film's central metaphor)
export function bush(C, cx, cy, rx, ry, o = {}) {
  const sd = o.seed || 4200, dr = o.draw ?? 1, n = 64, P = [];
  for (let i = 0; i < n; i++) { const a = i / n * Math.PI * 2, b = 1 + 0.05 * Math.sin(a * 11 + sd) + 0.04 * Math.sin(a * 19 + sd * 2) + 0.03 * Math.sin(a * 5); P.push([cx + Math.cos(a) * rx * b, cy + Math.sin(a) * ry * b]); }
  const S = smooth(P, 3);
  part(C, S, F(o.col || K.brown, sd, { p: 0.9, gap: 6, ang: 1.1, draw: o.fillDraw ?? dr }), { w: 6, seed: sd + 1, draw: dr, col: o.edge || K.ink });
  const sc = []; for (let i = 0; i < 90; i++) { const a = i * 0.6, r = 0.15 + 0.75 * (i / 90); sc.push([cx + Math.cos(a) * rx * r * (0.8 + 0.2 * Math.sin(i)), cy + Math.sin(a) * ry * r]); }
  line(C.l, sc, { w: 3.5, col: o.scribble || K.ink, p: 0.45, seed: sd + 2, draw: dr, wob: 2 });
}
export function scroll(C, x, y, w, open, o = {}) {   // a papyrus scroll unrolling to the right; open 0..1
  const sd = o.seed || 4300, h = o.h || 220, ww = 40 + (w - 40) * open;
  part(C, [[x, y - h / 2], [x + ww, y - h / 2], [x + ww, y + h / 2], [x, y + h / 2]], F(o.col || K.ochre, sd, { p: 0.45 }), { w: 4.5, seed: sd + 1 });
  [x, x + ww].forEach((rx, i) => part(C, [[rx - 16, y - h / 2 - 16], [rx + 16, y - h / 2 - 16], [rx + 16, y + h / 2 + 16], [rx - 16, y + h / 2 + 16]], F(K.brown, sd + 2 + i, { p: 0.85 }), { w: 4.5, seed: sd + 4 + i }));
  return [x + 24, x + ww - 24];
}
export function gear(C, cx, cy, r, teeth, rot, o = {}) {
  const sd = o.seed || 4400, P = [];
  for (let i = 0; i < teeth * 4; i++) { const a = rot + i / (teeth * 4) * Math.PI * 2, rr = (i % 4 < 2) ? r : r * 0.8; P.push([cx + Math.cos(a) * rr, cy + Math.sin(a) * rr]); }
  part(C, P, F(o.col || K.ochre, sd, { p: 0.85, draw: o.draw ?? 1 }), { w: 4.5, seed: sd + 1, draw: o.draw ?? 1 });
  part(C, handCircle(cx, cy, r * 0.25, sd + 2, 0, 14), F(K.brown, sd + 3), { w: 4, seed: sd + 4, draw: o.draw ?? 1 });
}
export function star5(C, x, y, r, col, sd) {
  const P = []; for (let k = 0; k <= 10; k++) { const a = -Math.PI / 2 + k * Math.PI / 5, rr = k % 2 ? r * 0.45 : r; P.push([x + Math.cos(a) * rr, y + Math.sin(a) * rr]); }
  part(C, P, F(col, sd, { p: 0.95, gap: 4, w: 6 }), { w: 4, seed: sd + 1, col: K.orange });
}
