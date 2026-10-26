// Static cut-paper props for the Ramayana spreads (drawn once at A.PPM px/m).
import { cut, PPM } from './art.js';
import { sh, crescent, blob, smoothOpen, INK, rr } from './paper.js';
import { mulberry, TAU } from './lib.js';
import { shade } from './actors.js';

const LW = 9, LW2 = 5, G = 'rgba(70,72,82,.9)', CREAM = '#f6f0e1';

// ---- prologue (graphite) ----
export function crane(hm, fallen = false) {   // a krauncha (sarus) crane, pencil on cream
  return cut(hm * .8, hm, (x, W, H) => {
    x.lineCap = 'round'; x.lineJoin = 'round';
    x.beginPath(); x.moveTo(W * .42, H * .62); x.lineTo(W * .4, H); x.moveTo(W * .52, H * .62); x.lineTo(W * .56, H); x.lineWidth = 8; x.strokeStyle = G; x.stroke();
    const body = () => { blob(x, W * .5, H * .52, W * .3, H * .13, .05, 4); };
    body(); sh(x, CREAM, LW, G);
    x.beginPath(); x.moveTo(W * .7, H * .48); x.quadraticCurveTo(W * .82, H * .3, W * .74, H * .12); x.lineWidth = 12; x.strokeStyle = G; x.stroke(); x.lineWidth = 5; x.strokeStyle = CREAM; x.stroke();
    x.beginPath(); x.arc(W * .74, H * .1, W * .07, 0, TAU); sh(x, '#e8a0a0', 6, G);   // the crane's red head, the one colour
    x.beginPath(); x.moveTo(W * .8, H * .1); x.lineTo(W * .98, H * .14); x.lineWidth = 6; x.strokeStyle = G; x.stroke();
    x.beginPath(); x.arc(W * .75, H * .09, 4, 0, TAU); x.fillStyle = G; x.fill();
    for (let i = 0; i < 4; i++) { x.beginPath(); x.moveTo(W * (.28 + i * .06), H * .5); x.quadraticCurveTo(W * (.33 + i * .06), H * .58, W * (.38 + i * .06), H * .52); x.lineWidth = 3; x.strokeStyle = G; x.stroke(); }
  }, { border: 12, paper: '#fbf8ef' });
}
export function arrow(lm) {
  return cut(lm, lm * .14, (x, W, H) => {
    x.beginPath(); x.moveTo(0, H / 2); x.lineTo(W * .88, H / 2); x.lineWidth = 7; x.strokeStyle = G; x.lineCap = 'round'; x.stroke();
    x.beginPath(); x.moveTo(W, H / 2); x.lineTo(W * .84, H * .1); x.lineTo(W * .84, H * .9); x.closePath(); sh(x, CREAM, 5, G);
    for (const d of [0, .07]) { x.beginPath(); x.moveTo(W * (.02 + d), H / 2); x.lineTo(W * (.08 + d), H * .05); x.moveTo(W * (.02 + d), H / 2); x.lineTo(W * (.08 + d), H * .95); x.stroke(); }
  }, { border: 8, ay: .5, ax: .5, paper: '#fbf8ef' });
}
export function sketchRiverBank(wm, hm, seed) {
  return cut(wm, hm, (x, W, H) => {
    x.beginPath(); x.moveTo(0, H); x.lineTo(0, H * .5); for (let i = 0; i <= 10; i++) x.lineTo(W * i / 10, H * (.35 + .15 * Math.sin(i * 1.7 + seed))); x.lineTo(W, H); x.closePath(); sh(x, CREAM, LW, G);
    const R = mulberry(seed); x.strokeStyle = G; x.lineWidth = 3;
    for (let i = 0; i < 22; i++) { const px = R() * W, py = H * (.55 + R() * .4), l = 20 + R() * 40; x.beginPath(); x.moveTo(px, py); x.quadraticCurveTo(px + 6, py - l * .6, px + (R() - .5) * 20, py - l); x.stroke(); }
  }, { paper: '#fbf8ef' });
}

// ---- Ayodhya & Mithila ----
export function palace(wm) {
  const hm = wm * .78;
  return cut(wm, hm, (x, W, H) => {
    const base = () => { x.beginPath(); x.moveTo(0, H); x.lineTo(0, H * .45); x.lineTo(W, H * .45); x.lineTo(W, H); x.closePath(); };
    crescent(x, base, '#e8b860', 30, 0, '#f6d48a'); base(); sh(x, null, LW);
    for (const [cx, r, top] of [[.2, .13, .2], [.5, .2, 0], [.8, .13, .2]]) {
      const d = () => { x.beginPath(); x.moveTo(W * (cx - r), H * .45); x.quadraticCurveTo(W * (cx - r), H * (top + .12), W * cx, H * (top + .02)); x.quadraticCurveTo(W * (cx + r), H * (top + .12), W * (cx + r), H * .45); x.closePath(); };
      crescent(x, d, '#d98a2a', 24, 0, '#f2a83a'); d(); sh(x, null, LW);
      x.beginPath(); x.moveTo(W * cx, H * (top + .02)); x.lineTo(W * cx, H * (top - .06)); x.lineWidth = 6; x.strokeStyle = INK; x.stroke();
      x.beginPath(); x.moveTo(W * cx, H * (top - .06)); x.lineTo(W * cx + 50, H * (top - .04)); x.lineTo(W * cx, H * (top - .01)); x.closePath(); sh(x, '#e8413a', 4);
    }
    x.beginPath(); x.moveTo(W * .42, H); x.lineTo(W * .42, H * .7); x.quadraticCurveTo(W * .5, H * .55, W * .58, H * .7); x.lineTo(W * .58, H); x.closePath(); sh(x, '#8a4a2a', LW2);
    for (const u of [.12, .25, .75, .88]) { x.beginPath(); x.moveTo(W * u - 22, H * .82); x.lineTo(W * u - 22, H * .64); x.quadraticCurveTo(W * u, H * .56, W * u + 22, H * .64); x.lineTo(W * u + 22, H * .82); x.closePath(); sh(x, '#b35a3a', LW2); }
    // bunting
    x.beginPath(); x.moveTo(W * .05, H * .47); x.quadraticCurveTo(W * .5, H * .58, W * .95, H * .47); x.lineWidth = 4; x.strokeStyle = INK; x.stroke();
    for (let i = 1; i < 12; i++) { const u = i / 12, px = W * (.05 + .9 * u), py = H * (.47 + .11 * Math.sin(Math.PI * u) * .9); x.beginPath(); x.moveTo(px - 14, py); x.lineTo(px + 14, py); x.lineTo(px, py + 36); x.closePath(); sh(x, ['#e8413a', '#ffd23f', '#5cbf4a'][i % 3], 3); }
  });
}
export function bowHalf(lm, side) {   // Shiva's bow, one half (side -1 left, +1 right); anchor = the break point
  return cut(lm / 2 + .004, lm * .26, (x, W, H) => {
    x.save(); if (side < 0) { x.translate(W, 0); x.scale(-1, 1); }
    x.beginPath(); x.moveTo(0, H * .78); x.quadraticCurveTo(W * .55, H * .9, W * .98, H * .1); x.lineWidth = 34; x.strokeStyle = INK; x.lineCap = 'round'; x.stroke(); x.lineWidth = 20; x.strokeStyle = '#6b8fd0'; x.stroke();
    for (let i = 1; i < 5; i++) { const u = i / 5; x.beginPath(); x.arc(W * (.1 + u * .78), H * (.78 - u * u * .62 - u * .05), 12, 0, TAU); sh(x, '#ffd23f', 4); }
    x.beginPath(); x.moveTo(W * .98, H * .1); x.lineTo(0, H * .1 + (H * .68) * .02); x.lineWidth = 4; x.strokeStyle = INK; x.stroke();
    x.restore();
  }, { ax: side < 0 ? 1 : 0, ay: .78, border: 12 });
}
export function bowStand(wm) {
  return cut(wm, wm * .3, (x, W, H) => {
    rr(x, W * .05, H * .55, W * .9, H * .45, 14); sh(x, '#a8683a', LW);
    for (const u of [.15, .85]) { rr(x, W * u - 14, 0, 28, H * .6, 8); sh(x, '#8a5530', LW2); }
    x.fillStyle = '#ffd23f'; for (let i = 0; i < 7; i++) { x.beginPath(); x.arc(W * (.15 + i * .12), H * .78, 8, 0, TAU); x.fill(); }
  });
}
export function throne(hm) {
  return cut(hm * .9, hm, (x, W, H) => {
    const back = () => { x.beginPath(); x.moveTo(W * .15, H * .6); x.lineTo(W * .15, H * .2); x.quadraticCurveTo(W * .5, -H * .05, W * .85, H * .2); x.lineTo(W * .85, H * .6); x.closePath(); };
    crescent(x, back, '#d98a2a', 24, 0, '#f2b632'); back(); sh(x, null, LW);
    blob(x, W * .5, H * .3, W * .18, H * .1, .03, 2); sh(x, '#e8413a', LW2);
    rr(x, W * .05, H * .55, W * .9, H * .14, 12); sh(x, '#e8413a', LW);
    for (const u of [.12, .88]) { rr(x, W * u - 16, H * .66, 32, H * .34, 8); sh(x, '#d98a2a', LW2); }
  });
}
export function sandals(wm) {
  return cut(wm, wm * .55, (x, W, H) => {
    for (const u of [.27, .73]) { x.beginPath(); x.ellipse(W * u, H * .55, W * .2, H * .42, 0, 0, TAU); sh(x, '#a8683a', LW2 + 1); x.beginPath(); x.arc(W * u, H * .3, 14, 0, TAU); sh(x, '#ffd23f', 4); }
  }, { border: 10 });
}

// ---- forest ----
export function hut(wm) {
  return cut(wm, wm * .8, (x, W, H) => {
    rr(x, W * .15, H * .5, W * .7, H * .5, 8); sh(x, '#c9a06a', LW);
    x.strokeStyle = '#8a6a3a'; x.lineWidth = 4; for (let i = 1; i < 8; i++) { x.beginPath(); x.moveTo(W * (.15 + i * .0875), H * .52); x.lineTo(W * (.15 + i * .0875), H); x.stroke(); }
    rr(x, W * .42, H * .66, W * .16, H * .34, 6); sh(x, '#4a3020', LW2);
    const roof = () => { x.beginPath(); x.moveTo(0, H * .56); x.lineTo(W * .5, 0); x.lineTo(W, H * .56); x.closePath(); };
    crescent(x, roof, '#b88a3a', 24, 0, '#e2b85a'); roof(); sh(x, null, LW);
    x.strokeStyle = '#a07a2a'; x.lineWidth = 4; for (let i = 0; i < 10; i++) { x.beginPath(); x.moveTo(W * (.12 + i * .08), H * .54); x.lineTo(W * .5, H * .06); x.stroke(); }
  });
}
export function deer(hm) {
  return cut(hm * 1.2, hm, (x, W, H) => {
    x.lineCap = 'round';
    for (const [a, b] of [[.3, .02], [.38, -.05], [.68, .05], [.76, -.04]]) { x.beginPath(); x.moveTo(W * a, H * .6); x.lineTo(W * (a + b), H); x.lineWidth = 16; x.strokeStyle = INK; x.stroke(); x.lineWidth = 7; x.strokeStyle = '#e8a83a'; x.stroke(); }
    const body = () => blob(x, W * .52, H * .52, W * .3, H * .14, .04, 7);
    crescent(x, body, '#d98a1a', 20, 18, '#ffc63a'); body(); sh(x, null, LW);
    for (let i = 0; i < 9; i++) { x.beginPath(); x.arc(W * (.32 + (i % 5) * .1), H * (.48 + (i > 4) * .07), 9, 0, TAU); x.fillStyle = '#fff2c0'; x.fill(); }
    x.beginPath(); x.moveTo(W * .78, H * .46); x.lineTo(W * .86, H * .22); x.lineWidth = 26; x.strokeStyle = INK; x.stroke(); x.lineWidth = 14; x.strokeStyle = '#ffc63a'; x.stroke();
    blob(x, W * .9, H * .2, W * .07, H * .07, .05, 2); sh(x, '#ffc63a', LW2 + 1);
    x.beginPath(); x.arc(W * .93, H * .18, 5, 0, TAU); x.fillStyle = INK; x.fill();
    x.lineWidth = 7; x.strokeStyle = INK; x.beginPath(); x.moveTo(W * .88, H * .14); x.lineTo(W * .84, H * .02); x.lineTo(W * .8, H * .0); x.moveTo(W * .86, H * .07); x.lineTo(W * .92, H * .02); x.stroke();
  });
}
export function chariot(wm) {   // Ravana's flying chariot, front card (riders stand behind it)
  return cut(wm, wm * .45, (x, W, H) => {
    const body = () => { x.beginPath(); x.moveTo(W * .05, H * .2); x.lineTo(W * .95, H * .2); x.quadraticCurveTo(W * .9, H * .85, W * .5, H * .9); x.quadraticCurveTo(W * .1, H * .85, W * .05, H * .2); x.closePath(); };
    crescent(x, body, '#2a3a6a', 26, 20, '#3f5aa8'); body(); sh(x, null, LW);
    for (let i = 0; i < 6; i++) { x.beginPath(); x.arc(W * (.15 + i * .14), H * .42, 12, 0, TAU); sh(x, '#ffd23f', 4); }
    for (const s of [-1, 1]) { x.beginPath(); x.moveTo(W * (.5 + s * .45), H * .3); x.quadraticCurveTo(W * (.5 + s * .7), H * .1, W * (.5 + s * .62), H * .0); x.quadraticCurveTo(W * (.5 + s * .58), H * .35, W * (.5 + s * .42), H * .55); x.closePath(); sh(x, '#e8e3f5', LW2); }
  }, { ay: .5 });
}
// ---- Kishkindha & Lanka ----
export function rockHill(wm, hm, seed) {
  return cut(wm, hm, (x, W, H) => {
    const R = mulberry(seed), pts = [[0, H]]; for (let i = 0; i <= 8; i++) pts.push([W * i / 8, H * (i % 2 ? .1 + R() * .25 : .35 + R() * .3)]); pts.push([W, H]);
    const p = () => { x.beginPath(); pts.forEach((q, i) => i ? x.lineTo(q[0], q[1]) : x.moveTo(q[0], q[1])); x.closePath(); };
    crescent(x, p, '#c27a32', 30, 20, '#e8a24a'); p(); sh(x, null, LW);
    x.strokeStyle = '#b06a2a'; x.lineWidth = 5; for (let i = 0; i < 8; i++) { const px = W * (.1 + R() * .8), py = H * (.5 + R() * .4); x.beginPath(); x.moveTo(px, py); x.lineTo(px + 30, py - 20); x.lineTo(px + 60, py - 6); x.stroke(); }
  });
}
export function lanka(wm) {
  const hm = wm * .9;
  return cut(wm, hm, (x, W, H) => {
    const R = mulberry(12);
    for (let i = 0; i < 7; i++) {
      const cx = W * (.08 + i * .14), tw = W * .1, top = H * (.12 + R() * .35);
      const tower = () => { x.beginPath(); x.moveTo(cx - tw / 2, H); x.lineTo(cx - tw / 2, top + tw * .6); x.quadraticCurveTo(cx - tw / 2, top, cx, top - tw * .4); x.quadraticCurveTo(cx + tw / 2, top, cx + tw / 2, top + tw * .6); x.lineTo(cx + tw / 2, H); x.closePath(); };
      crescent(x, tower, '#d9962a', 18, 0, '#ffcc3f'); tower(); sh(x, null, LW);
      for (let k = 0; k < 3; k++) { rr(x, cx - 9, top + tw * .8 + k * 60, 18, 30, 6); sh(x, '#8a4a1a', 4); }
    }
  });
}
export function ashoka(hm) {
  return cut(hm * .75, hm, (x, W, H) => {
    rr(x, W / 2 - 16, H * .45, 32, H * .55, 8); sh(x, '#7d5230', LW2 + 1);
    const can = () => blob(x, W / 2, H * .3, W * .46, H * .28, .08, 9);
    crescent(x, can, '#2f8a4a', 26, 20, '#3fa85a'); can(); sh(x, null, LW);
    const R = mulberry(4); for (let i = 0; i < 16; i++) { x.beginPath(); x.arc(W * (.2 + R() * .6), H * (.12 + R() * .32), 11, 0, TAU); sh(x, R() < .5 ? '#ff7a3a' : '#e8413a', 3); }
  });
}
export function monkey(hm, seed) {
  return cut(hm * .8, hm, (x, W, H) => {
    x.beginPath(); x.moveTo(W * .5, H * .7); x.bezierCurveTo(W * .95, H * .8, W * 1.0, H * .2, W * .85, H * .15); x.lineWidth = 14; x.strokeStyle = INK; x.lineCap = 'round'; x.stroke(); x.lineWidth = 6; x.strokeStyle = '#b5814a'; x.stroke();
    x.beginPath(); x.moveTo(W * .42, H); x.lineTo(W * .48, H * .62); x.lineTo(W * .58, H); x.lineWidth = 13; x.strokeStyle = INK; x.stroke();
    x.beginPath(); x.moveTo(W * .48, H * .64); x.lineTo(W * .48, H * .4); x.stroke();
    const up = seed % 2; x.beginPath(); x.moveTo(W * .2, H * (up ? .2 : .55)); x.lineTo(W * .48, H * .44); x.lineTo(W * .76, H * (up ? .25 : .55)); x.stroke();
    x.beginPath(); x.arc(W * .48, H * .28, W * .2, 0, TAU); sh(x, '#b5814a', LW2 + 1);
    x.beginPath(); x.ellipse(W * .48, H * .32, W * .12, W * .09, 0, 0, TAU); x.fillStyle = '#f2d2a0'; x.fill();
    for (const s of [-1, 1]) { x.beginPath(); x.arc(W * (.48 + s * .07), H * .25, 5, 0, TAU); x.fillStyle = INK; x.fill(); }
  }, { border: 10 });
}
export function stone(wm, seed) {
  return cut(wm, wm * .55, (x, W, H) => { blob(x, W / 2, H * .55, W * .46, H * .42, .1, seed); crescent(x, () => blob(x, W / 2, H * .55, W * .46, H * .42, .1, seed), '#8a8478', 14, 10, '#b8b2a4'); blob(x, W / 2, H * .55, W * .46, H * .42, .1, seed); sh(x, null, LW2 + 1); x.font = `${H * .5}px "Tiro Devanagari Sanskrit"`; x.fillStyle = 'rgba(58,42,36,.55)'; x.textAlign = 'center'; x.textBaseline = 'middle'; x.fillText('राम', W / 2, H * .58); }, { border: 9 });
}
export function flames(wm, seed) {
  return cut(wm, wm * 1.1, (x, W, H) => {
    const R = mulberry(seed);
    for (const [c, k] of [['#e8413a', 1], ['#ff9a2e', .72], ['#ffd23f', .45]]) {
      x.beginPath(); x.moveTo(W * (.5 - .45 * k), H);
      for (let i = 0; i <= 4; i++) { const u = i / 4; x.quadraticCurveTo(W * (.5 - .45 * k + .9 * k * (u - .12)), H * (1 - k * (.5 + R() * .5)), W * (.5 - .45 * k + .9 * k * u), H * (1 - k * .35)); }
      x.lineTo(W * (.5 + .45 * k), H); x.closePath(); sh(x, c, k === 1 ? LW : 0);
    }
  }, { border: 10 });
}
export function crownProp(wm) {
  return cut(wm, wm * .8, (x, W, H) => {
    x.beginPath(); x.moveTo(W * .1, H); x.lineTo(0, H * .25); x.lineTo(W * .3, H * .5); x.lineTo(W * .5, 0); x.lineTo(W * .7, H * .5); x.lineTo(W, H * .25); x.lineTo(W * .9, H); x.closePath();
    crescent(x, () => { x.beginPath(); x.moveTo(W * .1, H); x.lineTo(0, H * .25); x.lineTo(W * .3, H * .5); x.lineTo(W * .5, 0); x.lineTo(W * .7, H * .5); x.lineTo(W, H * .25); x.lineTo(W * .9, H); x.closePath(); }, '#d98a2a', 16, 0, '#f2b632');
    x.beginPath(); x.moveTo(W * .1, H); x.lineTo(0, H * .25); x.lineTo(W * .3, H * .5); x.lineTo(W * .5, 0); x.lineTo(W * .7, H * .5); x.lineTo(W, H * .25); x.lineTo(W * .9, H); x.closePath(); sh(x, null, LW);
    for (const u of [.3, .5, .7]) { x.beginPath(); x.arc(W * u, H * .72, 14, 0, TAU); sh(x, u === .5 ? '#e8413a' : '#3fa1de', 4); }
  }, { border: 10, ay: .5 });
}
export function note(hm, seed) {
  return cut(hm * .7, hm, (x, W, H) => {
    x.beginPath(); x.ellipse(W * .35, H * .8, W * .3, H * .17, -.4, 0, TAU); sh(x, seed % 2 ? '#e8413a' : '#3fa1de', LW2);
    x.beginPath(); x.moveTo(W * .62, H * .78); x.lineTo(W * .62, H * .05); x.quadraticCurveTo(W * .9, H * .2, W * .95, H * .4); x.lineWidth = 12; x.strokeStyle = INK; x.lineCap = 'round'; x.stroke();
  }, { border: 8, ay: .5 });
}
// the card that stays up at the end: Valmiki teaching the twins (drawn from the actor art)
export { PPM };
