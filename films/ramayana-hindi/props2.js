// More cut-paper props for the full-length film, same hand as props.js.
import { cut } from './art.js';
import { sh, crescent, blob, INK, rr, cv } from './paper.js';
import { mulberry, TAU } from './lib.js';
import { drawStick, SW, SH, CAST } from './actors.js';

const LW = 9, LW2 = 5;

// a static stick figure as a pop-up piece (crowds, armies, babies)
export function figure(name, pose = {}, hm = .04) {
  const a = cv(SW, SH); drawStick(a, CAST[name], pose);
  const h = hm * SH / 860;
  return { c: a, w: h * SW / SH, h, ax: .5, ay: 960 / SH };
}
export function fireAltar(wm) {   // yajna kund: a stepped brick altar with flames
  return cut(wm, wm * .8, (x, W, H) => {
    for (const [y, w, c] of [[.78, 1, '#c0623a'], [.62, .8, '#d97a4a'], [.48, .6, '#e8945a']]) { rr(x, W * (.5 - w / 2), H * y, W * w, H * .16, 6); sh(x, c, LW2 + 1); }
    for (const [c, k] of [['#e8413a', 1], ['#ff9a2e', .7], ['#ffd23f', .42]]) {
      x.beginPath(); x.moveTo(W * (.5 - .26 * k), H * .5);
      x.quadraticCurveTo(W * (.5 - .3 * k), H * (.5 - .3 * k), W * (.5 - .1 * k), H * (.5 - .36 * k)); x.quadraticCurveTo(W * (.5 - .04 * k), H * (.5 - .2 * k), W * .5, H * (.5 - .56 * k));
      x.quadraticCurveTo(W * (.5 + .08 * k), H * (.5 - .24 * k), W * (.5 + .14 * k), H * (.5 - .4 * k)); x.quadraticCurveTo(W * (.5 + .32 * k), H * (.5 - .2 * k), W * (.5 + .26 * k), H * .5); x.closePath(); sh(x, c, k === 1 ? LW2 + 1 : 0);
    }
  });
}
export function bowl(wm) {   // the bowl of sacred payasam
  return cut(wm, wm * .7, (x, W, H) => {
    x.beginPath(); x.ellipse(W * .5, H * .35, W * .46, H * .16, 0, 0, TAU); sh(x, '#fff6e0', LW2);
    x.beginPath(); x.moveTo(W * .04, H * .35); x.quadraticCurveTo(W * .1, H * .95, W * .5, H * .95); x.quadraticCurveTo(W * .9, H * .95, W * .96, H * .35); x.quadraticCurveTo(W * .5, H * .58, W * .04, H * .35); crescent(x, () => { x.beginPath(); x.moveTo(W * .04, H * .35); x.quadraticCurveTo(W * .1, H * .95, W * .5, H * .95); x.quadraticCurveTo(W * .9, H * .95, W * .96, H * .35); x.closePath(); }, '#c98a2a', 14, 0, '#f2b632');
    x.beginPath(); x.moveTo(W * .04, H * .35); x.quadraticCurveTo(W * .1, H * .95, W * .5, H * .95); x.quadraticCurveTo(W * .9, H * .95, W * .96, H * .35); sh(x, null, LW2 + 1);
  }, { border: 10 });
}
export function cradle(wm) {
  return cut(wm, wm * .6, (x, W, H) => {
    x.beginPath(); x.moveTo(W * .05, H * .3); x.quadraticCurveTo(W * .5, H * 1.1, W * .95, H * .3); x.closePath(); crescent(x, () => { x.beginPath(); x.moveTo(W * .05, H * .3); x.quadraticCurveTo(W * .5, H * 1.1, W * .95, H * .3); x.closePath(); }, '#c98a3a', 16, 0, '#e8b860');
    x.beginPath(); x.moveTo(W * .05, H * .3); x.quadraticCurveTo(W * .5, H * 1.1, W * .95, H * .3); x.closePath(); sh(x, null, LW2 + 1);
    x.fillStyle = '#e8413a'; for (let i = 0; i < 5; i++) { x.beginPath(); x.arc(W * (.25 + i * .125), H * .52, 7, 0, TAU); x.fill(); }
  }, { border: 10 });
}
export function boulder(wm, seed = 3) {   // the stone Ahalya was turned into
  return cut(wm, wm * .7, (x, W, H) => {
    const p = () => blob(x, W / 2, H * .55, W * .46, H * .42, .12, seed);
    crescent(x, p, '#8a8478', 16, 12, '#b8b2a4'); p(); sh(x, null, LW);
    x.strokeStyle = '#7a7468'; x.lineWidth = 4; x.beginPath(); x.moveTo(W * .3, H * .4); x.lineTo(W * .42, H * .55); x.lineTo(W * .38, H * .7); x.stroke();
  });
}
export function pillar(hm, col = '#f2b632') {
  return cut(hm * .22, hm, (x, W, H) => {
    rr(x, 0, 0, W, H * .08, 6); sh(x, col, LW2); rr(x, W * .15, H * .08, W * .7, H * .84, 6); sh(x, '#fff3dc', LW2);
    x.strokeStyle = 'rgba(180,140,80,.6)'; x.lineWidth = 4; for (const u of [.35, .5, .65]) { x.beginPath(); x.moveTo(W * u, H * .1); x.lineTo(W * u, H * .9); x.stroke(); }
    rr(x, 0, H * .92, W, H * .08, 6); sh(x, col, LW2);
  });
}
export function curtain(wm, hm, col = '#c0392b') {
  return cut(wm, hm, (x, W, H) => {
    const p = () => { x.beginPath(); x.moveTo(0, 0); x.lineTo(W, 0); x.quadraticCurveTo(W * .3, H * .3, W * .2, H); x.lineTo(0, H); x.closePath(); };
    crescent(x, p, '#8a2a20', 30, 0, col); p(); sh(x, null, LW);
    x.strokeStyle = 'rgba(90,20,15,.5)'; x.lineWidth = 5; for (let i = 1; i < 4; i++) { x.beginPath(); x.moveTo(W * i / 4, 0); x.quadraticCurveTo(W * i / 4 * .4, H * .4, W * i / 4 * .25, H); x.stroke(); }
    x.beginPath(); x.arc(W * .24, H * .55, 16, 0, TAU); sh(x, '#f2b632', 4);
  });
}
export function tree(hm, col = '#4fae4c', seed = 1, trunk = '#7d5230') {   // a broad banyan-ish tree
  return cut(hm * 1.1, hm, (x, W, H) => {
    rr(x, W / 2 - W * .06, H * .45, W * .12, H * .55, 10); sh(x, trunk, LW2 + 1);
    const R = mulberry(seed);
    const can = () => { x.beginPath(); for (let i = 0; i < 7; i++) { const a = Math.PI + i / 6 * Math.PI, r = W * (.32 + R() * .1); x.arc(W / 2 + Math.cos(a) * W * .22, H * .36 + Math.sin(a) * H * .16, r * .5, 0, TAU); } };
    x.fillStyle = col; can(); x.fill(); blob(x, W / 2, H * .34, W * .48, H * .3, .1, seed); crescent(x, () => blob(x, W / 2, H * .34, W * .48, H * .3, .1, seed), shade(col), 26, 20, col); blob(x, W / 2, H * .34, W * .48, H * .3, .1, seed); sh(x, null, LW);
  });
}
function shade(hex) { const n = parseInt(hex.slice(1), 16), r = n >> 16, g = n >> 8 & 255, b = n & 255, f = .8; return `rgb(${r * f | 0},${g * f | 0},${b * f | 0})`; }
export function vulture(wm, wing = 0, col = '#b07a4a', dark = '#8a5a3a', head = '#f6f0e1') {   // Jatayu (and Sampati): a great old bird, wings out
  return cut(wm, wm * .6, (x, W, H) => {
    for (const s of [-1, 1]) { x.save(); x.translate(W / 2, H * .5); x.scale(s, 1); x.rotate(-wing * .4);
      const w = () => { x.beginPath(); x.moveTo(0, 0); x.quadraticCurveTo(W * .2, -H * .45, W * .48, -H * .3); for (let i = 0; i < 5; i++) x.lineTo(W * (.46 - i * .07), -H * (.18 - i * .05) + 28); x.closePath(); };
      crescent(x, w, dark, 0, 20, col); w(); sh(x, null, LW); x.restore(); }
    const b = () => blob(x, W / 2, H * .55, W * .14, H * .22, .04, 3);
    crescent(x, b, dark, 14, 14, col); b(); sh(x, null, LW);
    x.beginPath(); x.arc(W / 2, H * .25, W * .07, 0, TAU); sh(x, head, LW2 + 1);
    x.beginPath(); x.moveTo(W * .53, H * .25); x.quadraticCurveTo(W * .6, H * .28, W * .56, H * .36); x.lineTo(W * .53, H * .3); x.closePath(); sh(x, '#f2b632', 4);
    x.beginPath(); x.arc(W * .515, H * .23, 6, 0, TAU); x.fillStyle = INK; x.fill();
    crown2(x, W / 2, H * .17, W * .08);
  }, { ay: .5 });
}
function crown2(x, cx, cy, w) { x.beginPath(); x.moveTo(cx - w * .5, cy); x.lineTo(cx - w * .55, cy - w * .5); x.lineTo(cx - w * .2, cy - w * .25); x.lineTo(cx, cy - w * .7); x.lineTo(cx + w * .2, cy - w * .25); x.lineTo(cx + w * .55, cy - w * .5); x.lineTo(cx + w * .5, cy); x.closePath(); sh(x, '#f2b632', 4); }
export function bundle(wm) {   // Sita's jewels tied in her scarf
  return cut(wm, wm, (x, W, H) => {
    blob(x, W / 2, H * .6, W * .4, H * .32, .06, 2); sh(x, '#f2b632', LW2);
    x.beginPath(); x.moveTo(W * .4, H * .32); x.lineTo(W * .5, H * .12); x.lineTo(W * .6, H * .32); sh(x, '#e8413a', LW2);
    for (const [u, v] of [[.35, .6], [.55, .7], [.65, .52]]) { x.beginPath(); x.arc(W * u, H * v, 9, 0, TAU); sh(x, '#3fa1de', 3); }
  }, { border: 8, ay: .5 });
}
export function serpent(wm) {   // Surasa, mother of serpents, rising from the sea
  return cut(wm, wm * 1.1, (x, W, H) => {
    x.beginPath(); x.moveTo(W * .3, H); x.bezierCurveTo(W * .1, H * .6, W * .8, H * .55, W * .55, H * .25); x.lineWidth = 70; x.strokeStyle = INK; x.lineCap = 'round'; x.stroke(); x.lineWidth = 54; x.strokeStyle = '#5cbf4a'; x.stroke();
    x.lineWidth = 10; x.strokeStyle = '#ffd23f'; x.setLineDash([16, 30]); x.stroke(); x.setLineDash([]);
    const hd = () => blob(x, W * .55, H * .18, W * .22, H * .12, .04, 5);
    crescent(x, hd, '#3f9a44', 20, 16, '#6fcc55'); hd(); sh(x, null, LW);
    for (const s of [-1, 1]) { x.beginPath(); x.arc(W * (.55 + s * .09), H * .14, 10, 0, TAU); x.fillStyle = '#fff35a'; x.fill(); x.lineWidth = 4; x.strokeStyle = INK; x.stroke(); }
    x.beginPath(); x.moveTo(W * .5, H * .26); x.lineTo(W * .55, H * .34); x.lineTo(W * .6, H * .26); x.lineWidth = 6; x.strokeStyle = '#e8413a'; x.stroke();
  });
}
export function vimana(wm) {   // Pushpaka, the flying palace
  return cut(wm, wm * .7, (x, W, H) => {
    for (const s of [-1, 1]) { x.beginPath(); x.moveTo(W * (.5 + s * .3), H * .62); x.quadraticCurveTo(W * (.5 + s * .62), H * .4, W * (.5 + s * .5), H * .25); x.quadraticCurveTo(W * (.5 + s * .45), H * .5, W * (.5 + s * .28), H * .72); x.closePath(); sh(x, '#fff6e0', LW2 + 1); }
    const base = () => { x.beginPath(); x.moveTo(W * .1, H * .62); x.lineTo(W * .9, H * .62); x.quadraticCurveTo(W * .82, H * .98, W * .5, H); x.quadraticCurveTo(W * .18, H * .98, W * .1, H * .62); x.closePath(); };
    crescent(x, base, '#d98a2a', 22, 0, '#f2b632'); base(); sh(x, null, LW);
    for (const [cx, r, top] of [[.3, .1, .35], [.5, .14, .12], [.7, .1, .35]]) {
      const d = () => { x.beginPath(); x.moveTo(W * (cx - r), H * .62); x.lineTo(W * (cx - r), H * (top + .14)); x.quadraticCurveTo(W * cx, H * (top - .08), W * (cx + r), H * (top + .14)); x.lineTo(W * (cx + r), H * .62); x.closePath(); };
      crescent(x, d, '#d9505a', 18, 0, '#ff8a9a'); d(); sh(x, null, LW2 + 1);
    }
    for (let i = 0; i < 7; i++) { x.beginPath(); x.arc(W * (.18 + i * .107), H * .78, 10, 0, TAU); sh(x, ['#fff35a', '#5cbf4a', '#3fa1de'][i % 3], 3); }
  }, { ay: .5 });
}
export function diya(wm) {
  return cut(wm, wm * .9, (x, W, H) => {
    x.beginPath(); x.moveTo(W * .05, H * .6); x.quadraticCurveTo(W * .5, H * 1.05, W * .95, H * .6); x.closePath(); sh(x, '#c9733a', LW2);
    x.beginPath(); x.moveTo(W * .5, H * .58); x.quadraticCurveTo(W * .3, H * .35, W * .5, H * .02); x.quadraticCurveTo(W * .7, H * .35, W * .5, H * .58); sh(x, '#ffb02e', 3);
    x.beginPath(); x.moveTo(W * .5, H * .54); x.quadraticCurveTo(W * .4, H * .4, W * .5, H * .22); x.quadraticCurveTo(W * .6, H * .4, W * .5, H * .54); x.fillStyle = '#fff3a0'; x.fill();
  }, { border: 8 });
}
export function herbHill(wm) {   // the mountain of healing herbs, glowing
  return cut(wm, wm * .8, (x, W, H) => {
    const p = () => { x.beginPath(); x.moveTo(0, H); x.lineTo(W * .2, H * .35); x.lineTo(W * .35, H * .5); x.lineTo(W * .55, H * .05); x.lineTo(W * .78, H * .45); x.lineTo(W, H); x.closePath(); };
    crescent(x, p, '#5a8a3a', 26, 20, '#7fb05a'); p(); sh(x, null, LW);
    const R = mulberry(6); for (let i = 0; i < 14; i++) { const px = W * (.18 + R() * .64), py = H * (.4 + R() * .5); x.beginPath(); x.arc(px, py, 12, 0, TAU); sh(x, '#fff35a', 3); x.beginPath(); x.arc(px, py, 22, 0, TAU); x.fillStyle = 'rgba(255,250,150,.35)'; x.fill(); }
  }, { ay: .5 });
}
export function horse(hm) {   // the white horse of the great sacrifice
  return cut(hm * 1.2, hm, (x, W, H) => {
    x.lineCap = 'round';
    for (const [a, b] of [[.28, .02], [.36, -.04], [.66, .04], [.74, -.03]]) { x.beginPath(); x.moveTo(W * a, H * .6); x.lineTo(W * (a + b), H); x.lineWidth = 18; x.strokeStyle = INK; x.stroke(); x.lineWidth = 8; x.strokeStyle = '#fffaf0'; x.stroke(); }
    const body = () => blob(x, W * .5, H * .52, W * .3, H * .15, .04, 9);
    crescent(x, body, '#dcd6ca', 20, 18, '#fffaf0'); body(); sh(x, null, LW);
    x.beginPath(); x.moveTo(W * .76, H * .48); x.lineTo(W * .86, H * .2); x.lineWidth = 30; x.strokeStyle = INK; x.stroke(); x.lineWidth = 18; x.strokeStyle = '#fffaf0'; x.stroke();
    blob(x, W * .9, H * .2, W * .08, H * .07, .05, 2); sh(x, '#fffaf0', LW2 + 1);
    x.beginPath(); x.arc(W * .92, H * .17, 5, 0, TAU); x.fillStyle = INK; x.fill();
    x.beginPath(); x.moveTo(W * .82, H * .16); x.quadraticCurveTo(W * .72, H * .3, W * .74, H * .44); x.lineWidth = 12; x.strokeStyle = '#f2b632'; x.stroke();
    x.beginPath(); x.moveTo(W * .2, H * .5); x.quadraticCurveTo(W * .08, H * .62, W * .1, H * .8); x.lineWidth = 12; x.strokeStyle = '#f2b632'; x.stroke();
    rr(x, W * .38, H * .36, W * .24, H * .1, 6); sh(x, '#e8413a', 4);
  });
}
export function drum(wm) {   // big war drums (to wake Kumbhakarna)
  return cut(wm, wm * .9, (x, W, H) => {
    rr(x, W * .1, H * .25, W * .8, H * .7, 20); sh(x, '#c0623a', LW);
    x.beginPath(); x.ellipse(W / 2, H * .25, W * .4, H * .12, 0, 0, TAU); sh(x, '#f6e6c8', LW);
    x.strokeStyle = INK; x.lineWidth = 4; for (let i = 0; i < 6; i++) { x.beginPath(); x.moveTo(W * (.12 + i * .15), H * .3); x.lineTo(W * (.2 + i * .13), H * .92); x.stroke(); }
  });
}
export function bridgeStone(wm, seed) {
  return cut(wm, wm * .5, (x, W, H) => { const p = () => blob(x, W / 2, H * .55, W * .46, H * .4, .1, seed); crescent(x, p, '#8a8478', 14, 10, '#c4beb0'); p(); sh(x, null, LW2 + 1); }, { border: 9 });
}
export function arrowGold(lm) {   // a bright divine arrow
  return cut(lm, lm * .14, (x, W, H) => {
    x.beginPath(); x.moveTo(0, H / 2); x.lineTo(W * .86, H / 2); x.lineWidth = 9; x.strokeStyle = INK; x.lineCap = 'round'; x.stroke(); x.lineWidth = 4; x.strokeStyle = '#ffd23f'; x.stroke();
    x.beginPath(); x.moveTo(W, H / 2); x.lineTo(W * .82, H * .08); x.lineTo(W * .82, H * .92); x.closePath(); sh(x, '#ffd23f', 5);
    for (const d of [0, .07]) { x.beginPath(); x.moveTo(W * (.02 + d), H / 2); x.lineTo(W * (.08 + d), H * .05); x.moveTo(W * (.02 + d), H / 2); x.lineTo(W * (.08 + d), H * .95); x.lineWidth = 6; x.strokeStyle = '#e8413a'; x.stroke(); }
  }, { border: 8, ay: .5, ax: .5 });
}
export function snakeArrow(lm) {   // Indrajit's serpent-noose arrow
  return cut(lm, lm * .2, (x, W, H) => {
    x.beginPath(); x.moveTo(0, H / 2); for (let i = 0; i <= 12; i++) x.lineTo(W * .85 * i / 12, H / 2 + Math.sin(i * 1.4) * H * .25); x.lineWidth = 12; x.strokeStyle = INK; x.lineCap = 'round'; x.stroke(); x.lineWidth = 6; x.strokeStyle = '#5cbf4a'; x.stroke();
    blob(x, W * .9, H / 2, W * .08, H * .3, .05, 3); sh(x, '#3f9a44', 5);
  }, { border: 8, ay: .5, ax: .5 });
}
export function lotus(wm) {
  return cut(wm, wm * .7, (x, W, H) => {
    for (let i = -3; i <= 3; i++) { x.save(); x.translate(W / 2, H * .9); x.rotate(i * .32); x.beginPath(); x.ellipse(0, -H * .42, W * .09, H * .42, 0, 0, TAU); sh(x, Math.abs(i) % 2 ? '#f29ab0' : '#ffd0dc', LW2); x.restore(); }
    x.beginPath(); x.ellipse(W / 2, H * .92, W * .4, H * .08, 0, 0, TAU); sh(x, '#5cbf4a', LW2);
  });
}
export function goldThrone(hm) {   // the throne that rose from the earth
  return cut(hm * 1.1, hm, (x, W, H) => {
    const b = () => { x.beginPath(); x.moveTo(W * .12, H * .62); x.lineTo(W * .12, H * .22); x.quadraticCurveTo(W * .5, -H * .05, W * .88, H * .22); x.lineTo(W * .88, H * .62); x.closePath(); };
    crescent(x, b, '#d98a2a', 24, 0, '#ffd23f'); b(); sh(x, null, LW);
    rr(x, W * .04, H * .58, W * .92, H * .16, 12); sh(x, '#5cbf4a', LW);
    x.beginPath(); x.moveTo(0, H); x.quadraticCurveTo(W * .5, H * .68, W, H); x.closePath(); sh(x, '#a8743a', LW);
    for (let i = 0; i < 5; i++) { x.beginPath(); x.arc(W * (.2 + i * .15), H * .66, 10, 0, TAU); sh(x, '#ff7aa8', 3); }
  });
}
export function crack(wm) {   // the earth opening
  return cut(wm, wm * .3, (x, W, H) => {
    x.beginPath(); x.moveTo(0, H * .5); for (let i = 1; i < 10; i++) x.lineTo(W * i / 10, H * (i % 2 ? .1 : .4)); x.lineTo(W, H * .5); for (let i = 9; i > 0; i--) x.lineTo(W * i / 10, H * (i % 2 ? .9 : .65)); x.closePath(); sh(x, '#3a2414', LW2);
  }, { ay: .5, border: 8 });
}
export function mountain(wm, hm, col = '#8a9ab8', seed = 2) {   // snowy peaks (Mahendra, and the Himalaya)
  return cut(wm, hm, (x, W, H) => {
    const R = mulberry(seed), pk = [[0, H], [W * .15, H * .5], [W * .3, H * .65], [W * .5, 0], [W * .7, H * .55], [W * .85, H * .35], [W, H]];
    const p = () => { x.beginPath(); pk.forEach((q, i) => i ? x.lineTo(q[0], q[1]) : x.moveTo(q[0], q[1])); x.closePath(); };
    crescent(x, p, shade(col), 30, 0, col); p(); sh(x, null, LW);
    x.beginPath(); x.moveTo(W * .5, 0); x.lineTo(W * .42, H * .2); x.lineTo(W * .47, H * .17); x.lineTo(W * .5, H * .24); x.lineTo(W * .55, H * .16); x.lineTo(W * .59, H * .22); x.closePath(); sh(x, '#ffffff', LW2);
    R();
  });
}
export function scroll(wm) {   // the poem, on a palm-leaf bundle
  return cut(wm, wm * .3, (x, W, H) => {
    rr(x, 0, H * .2, W, H * .6, 12); sh(x, '#f2d69a', LW2);
    x.strokeStyle = 'rgba(120,80,40,.6)'; x.lineWidth = 3; for (let i = 0; i < 4; i++) { x.beginPath(); x.moveTo(W * .08, H * (.32 + i * .12)); x.lineTo(W * .92, H * (.32 + i * .12)); x.stroke(); }
    for (const u of [.3, .7]) { x.beginPath(); x.arc(W * u, H * .5, 8, 0, TAU); sh(x, '#8a4a2a', 3); }
  }, { border: 8 });
}
export function rain(wm, hm) {   // a rain-cloud with falling streaks
  return cut(wm, hm, (x, W, H) => {
    x.strokeStyle = '#5a8ac8'; x.lineWidth = 7; x.lineCap = 'round';
    for (let i = 0; i < 12; i++) { const px = W * (.12 + i * .068); x.beginPath(); x.moveTo(px, H * .45); x.lineTo(px - 14, H * (.75 + (i % 3) * .08)); x.stroke(); }
    const p = () => { x.beginPath(); x.ellipse(W * .3, H * .3, W * .22, H * .18, 0, 0, TAU); x.ellipse(W * .55, H * .22, W * .26, H * .2, 0, 0, TAU); x.ellipse(W * .78, H * .32, W * .2, H * .16, 0, 0, TAU); };
    x.fillStyle = '#9aa8c0'; p(); x.fill(); x.lineWidth = LW; x.strokeStyle = INK; p(); x.stroke(); x.fillStyle = '#b8c4d8'; p(); x.fill();
  }, { ay: 0 });
}
export function kingdomCity(wm, col = '#f6d48a') {   // a low city skyline for distant Ayodhya
  return cut(wm, wm * .35, (x, W, H) => {
    const R = mulberry(4);
    for (let i = 0; i < 9; i++) { const cx = W * (.06 + i * .11), w = W * .09, h = H * (.4 + R() * .5); rr(x, cx - w / 2, H - h, w, h, 6); sh(x, i % 2 ? col : '#f2b26a', LW2);
      x.beginPath(); x.arc(cx, H - h, w * .4, Math.PI, 0); sh(x, '#e8945a', LW2); }
  });
}
