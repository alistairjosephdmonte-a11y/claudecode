// Spreads: page art (backdrop + ground) and the pop-up pieces, scheduled back to front.
import * as THREE from 'three';
import * as A from './art.js';
import * as P from './props.js';
import { cv, paperFill, GRAIN, smoothOpen } from './paper.js';
import { mulberry, seg, back, ss, TAU } from './lib.js';
import { BW, BD } from './book.js';
import { cutMesh, thread } from './cutmesh.js';
import { OPEN, TURNS, CLOSE } from './story.js';

const PW = 2048, PH = Math.round(2048 * BD / BW);
const gx = xm => (xm / BW + .5) * PW, gz = zm => zm / BD * PH;

// spreads: 0 prologue · 1 Bala/Ayodhya · 2 forest · 3 Kishkindha/Lanka · 4 war · 5 hermitage (same page as 4)
export const RISE = [OPEN[1] + .3, TURNS[0][1] - .9, TURNS[1][1] - .9, TURNS[2][1] - .9, TURNS[3][1] - .9, 99.6];
export const FOLD = [TURNS[0][0], TURNS[1][0], TURNS[2][0], TURNS[3][0], 98.9, CLOSE[0]];
export const PAGE_OF = [0, 1, 2, 3, 4, 4];

function page(fn) { const c = cv(PW, PH), x = c.getContext('2d'); fn(x); x.save(); x.globalAlpha = .7; x.fillStyle = x.createPattern(GRAIN, 'repeat'); x.fillRect(0, 0, PW, PH); x.restore(); return c; }
function grad(x, stops, x0 = 0, y0 = 0, x1 = 0, y1 = PH) { const g = x.createLinearGradient(x0, y0, x1, y1); stops.forEach(([o, c]) => g.addColorStop(o, c)); x.fillStyle = g; x.fillRect(0, 0, PW, PH); }
function dots(x, seed, n, cols, r0 = 5, r1 = 10, x0 = 0, x1 = PW) { const R = mulberry(seed); for (let i = 0; i < n; i++) { x.beginPath(); x.arc(x0 + R() * (x1 - x0), R() * PH, r0 + R() * (r1 - r0), 0, TAU); x.fillStyle = cols[(R() * cols.length) | 0]; x.fill(); } }
function clouds(x, seed, col, n = 6, y0 = .1, y1 = .5) { const R = mulberry(seed); for (let i = 0; i < n; i++) { const cx = R() * PW, cy = PH * (y0 + R() * (y1 - y0)), w = 180 + R() * 240; x.fillStyle = col; for (let k = 0; k < 5; k++) { x.beginPath(); x.ellipse(cx + (k - 2) * w * .22, cy - Math.sin(k / 4 * Math.PI) * w * .12, w * .2, w * .13, 0, 0, TAU); x.fill(); } } }
const pen = (x, fn, a = .5, w = 4) => { x.save(); x.beginPath(); fn(); x.lineWidth = w; x.strokeStyle = `rgba(70,72,82,${a})`; x.lineCap = 'round'; x.stroke(); x.restore(); };

export function pages() {
  const P0 = {};
  // 0 · prologue: graphite on cream
  P0.sky0 = page(x => {
    paperFill(x, PW, PH, '#f5eedc', 41, .05);
    pen(x, () => { x.moveTo(0, PH * .72); for (let i = 0; i <= 12; i++) x.lineTo(PW * i / 12, PH * (.62 + .08 * Math.sin(i * 1.3))); }, .4, 5);
    pen(x, () => { x.arc(PW * .72, PH * .3, 90, 0, TAU); }, .35, 4);
    for (const [cx, cy, s] of [[.25, .2, 1], [.48, .13, .7]]) pen(x, () => { x.arc(PW * cx - 70 * s, PH * cy + 10, 50 * s, Math.PI, 0); x.arc(PW * cx, PH * cy - 20 * s, 70 * s, Math.PI * 1.1, -.1); x.arc(PW * cx + 80 * s, PH * cy + 10, 45 * s, Math.PI * 1.3, .2); }, .3);
    x.font = 'italic 44px "IM Fell English"'; x.fillStyle = 'rgba(80,70,60,.5)'; x.textAlign = 'center'; x.fillText('the river Tamasā', PW * .5, PH * .9);
  });
  P0.ground0 = page(x => {
    paperFill(x, PW, PH, '#f5eedc', 43, .05);
    for (let k = 0; k < 7; k++) pen(x, () => { const y = gz(.075 + k * .01); x.moveTo(0, y); for (let i = 0; i <= 20; i++) x.lineTo(PW * i / 20, y + Math.sin(i * 1.1 + k) * 10); }, .3, 4);
  });
  // 1 · Ayodhya & Mithila: meadow green under sky blue, saffron festival
  P0.sky1 = page(x => {
    grad(x, [[0, '#7cc6ef'], [.75, '#c9ecf7'], [1, '#eaf7ec']]); clouds(x, 3, 'rgba(255,255,255,.6)');
    for (const y0 of [.12, .24]) { x.beginPath(); x.moveTo(0, PH * y0); x.quadraticCurveTo(PW / 2, PH * (y0 + .12), PW, PH * y0); x.lineWidth = 4; x.strokeStyle = '#6b4a36'; x.stroke();
      for (let i = 1; i < 20; i++) { const u = i / 20, px = PW * u, py = PH * (y0 + .24 * u * (1 - u)); x.beginPath(); x.moveTo(px - 22, py); x.lineTo(px + 22, py); x.lineTo(px, py + 56); x.closePath(); x.fillStyle = ['#ff9a2e', '#ffd23f', '#e8413a'][i % 3]; x.fill(); } }
  });
  P0.sky1dusk = page(x => {
    grad(x, [[0, '#2a2f6a'], [.6, '#7a4f8a'], [1, '#e8946a']]);
    const R = mulberry(5); for (let i = 0; i < 140; i++) { x.beginPath(); x.arc(R() * PW, R() * PH * .55, 1 + R() * 2.5, 0, TAU); x.fillStyle = `rgba(255,245,220,${.3 + R() * .6})`; x.fill(); }
    x.beginPath(); x.arc(PW * .8, PH * .25, 70, 0, TAU); x.fillStyle = '#fff3cf'; x.fill();
  });
  P0.ground1 = page(x => {
    grad(x, [[0, '#86c763'], [1, '#9fd57a']]);
    x.fillStyle = '#f4dca0'; x.beginPath(); x.roundRect(gx(-.21), gz(.08), gx(-.01) - gx(-.21), gz(.22) - gz(.08), 30); x.fill();
    x.strokeStyle = 'rgba(200,150,80,.5)'; x.lineWidth = 4; for (let i = 0; i < 9; i++) { x.beginPath(); x.moveTo(gx(-.21) + i * 60, gz(.08)); x.lineTo(gx(-.21) + i * 60, gz(.22)); x.stroke(); }
    x.lineCap = 'round'; x.beginPath(); smoothOpen(x, [[gx(-.01), gz(.17)], [gx(.08), gz(.16)], [gx(.15), gz(.18)], [gx(.23), gz(.17)]]); x.lineWidth = 110; x.strokeStyle = '#ecd49a'; x.stroke();
    dots(x, 5, 160, ['#ffffff', '#ffe066', '#ff9ec1']);
  });
  // 2 · forest: deep green and teal
  P0.sky2 = page(x => {
    grad(x, [[0, '#9fd8c8'], [.75, '#d8f0dc'], [1, '#eef6dc']]);
    x.save(); x.globalCompositeOperation = 'lighter'; for (let i = 0; i < 5; i++) { x.beginPath(); const x0 = PW * (.1 + i * .2); x.moveTo(x0, 0); x.lineTo(x0 + 140, 0); x.lineTo(x0 + 420, PH); x.lineTo(x0 + 220, PH); x.closePath(); x.fillStyle = 'rgba(255,255,230,.1)'; x.fill(); } x.restore();
    const R = mulberry(8); x.fillStyle = '#7fbf9e'; for (let i = 0; i < 28; i++) { const px = R() * PW, h = PH * (.35 + R() * .3), w = 60 + R() * 60; x.beginPath(); x.moveTo(px, PH - h); x.lineTo(px + w, PH); x.lineTo(px - w, PH); x.closePath(); x.fill(); }
  });
  P0.ground2 = page(x => { grad(x, [[0, '#3f7f46'], [1, '#56a253']]); dots(x, 9, 220, ['#e8a33a', '#c9612e', '#7a4a2a', '#9fd57a'], 6, 12); });
  // 3 · Kishkindha (ochre) and the sea to Lanka (turquoise)
  P0.sky3 = page(x => {
    grad(x, [[0, '#f2c27a'], [.45, '#f6dba6'], [.55, '#bfe6e6'], [1, '#7fd0d6']], 0, 0, PW, 0);
    x.fillStyle = 'rgba(255,255,255,.35)'; clouds(x, 14, 'rgba(255,255,255,.45)', 5, .08, .35);
    x.fillStyle = '#d99a4a'; x.beginPath(); x.moveTo(0, PH); for (let i = 0; i <= 8; i++) x.lineTo(PW * .5 * i / 8, PH * (.62 + .12 * Math.sin(i * 1.9))); x.lineTo(PW * .5, PH); x.fill();
    x.fillStyle = '#e8b83a'; for (let i = 0; i < 6; i++) { const cx = PW * (.72 + i * .045), h = PH * (.12 + (i % 3) * .05); x.fillRect(cx, PH * .75 - h, 34, h); x.beginPath(); x.arc(cx + 17, PH * .75 - h, 17, Math.PI, 0); x.fill(); }
    x.fillStyle = '#3fb0c0'; x.fillRect(PW * .5, PH * .75, PW * .5, PH * .25);
  });
  P0.ground3 = page(x => {
    grad(x, [[0, '#e0a24a'], [.4, '#e8b25a'], [.43, '#3fb5c8'], [.72, '#2f9ab8'], [.75, '#f2cf7a'], [1, '#e8be62']], 0, 0, PW, 0);
    const R = mulberry(31); x.strokeStyle = 'rgba(255,255,255,.35)'; x.lineWidth = 6; x.lineCap = 'round';
    for (let i = 0; i < 50; i++) { const px = PW * (.44 + R() * .26), py = R() * PH; x.beginPath(); x.moveTo(px, py); x.quadraticCurveTo(px + 30, py - 16, px + 60, py); x.stroke(); }
    dots(x, 33, 90, ['#c27a32', '#f2d29a'], 5, 11, 0, PW * .45);
  });
  // 4 · war (red-orange) → 5 · hermitage (lilac): the backdrop slats flip between them
  P0.sky4 = page(x => {
    grad(x, [[0, '#a8322a'], [.6, '#e8703a'], [1, '#f6b05a']]);
    const R = mulberry(2); x.fillStyle = 'rgba(90,40,40,.25)'; for (let i = 0; i < 10; i++) { const cx = R() * PW, cy = PH * (.2 + R() * .4), r = 120 + R() * 160; x.beginPath(); x.arc(cx, cy, r, 0, TAU); x.fill(); }
    x.fillStyle = '#7a2a22'; for (let i = 0; i < 6; i++) { const cx = PW * (.68 + i * .05), h = PH * (.15 + (i % 3) * .06); x.fillRect(cx, PH * .8 - h, 38, h); }
  });
  P0.sky5 = page(x => {
    grad(x, [[0, '#8f86c8'], [.65, '#d8c4e8'], [1, '#f6e2d8']]);
    x.beginPath(); x.arc(PW * .2, PH * .25, 80, 0, TAU); x.fillStyle = '#fff6e2'; x.fill();
    clouds(x, 21, 'rgba(255,255,255,.35)', 5, .3, .55);
  });
  P0.ground4 = page(x => {
    grad(x, [[0, '#2f9ab8'], [.32, '#3fb5c8'], [.38, '#c2703a'], [1, '#a8582a']]);
    const R = mulberry(41); x.strokeStyle = 'rgba(255,255,255,.3)'; x.lineWidth = 6; x.lineCap = 'round';
    for (let i = 0; i < 40; i++) { const px = R() * PW, py = R() * PH * .3; x.beginPath(); x.moveTo(px, py); x.quadraticCurveTo(px + 30, py - 14, px + 60, py); x.stroke(); }
    dots(x, 43, 120, ['#8a3a22', '#e8a05a'], 5, 10);
  });
  return P0;
}

// ---------- pop-up pieces ----------
function popper(list, spread, parent, item, x, y, z, o = {}) {
  const g = new THREE.Group(); g.position.set(x, y, z);
  const m = cutMesh(item, o); if (o.ry) m.rotation.y = o.ry;
  g.add(m); parent.add(g);
  const rec = { g, m, spread, d: o.d ?? (.3 - z) * 1.2, dir: o.dir ?? (z > .15 ? -1 : 1), sway: o.sway || 0, ph: o.ph ?? x * 40, pop: o.pop !== false, t0: o.t0 };
  list.push(rec); return rec;
}
export function riseOf(r, t) {
  const t0 = (r.t0 ?? RISE[r.spread] + r.d), tf = FOLD[r.spread] + (.3 - r.g.position.z) * .6;
  const up = r.pop ? back(seg(t, t0, t0 + .55), 1.7) : (t >= t0 ? 1 : 0);
  const dn = 1 - ss(seg(t, tf, tf + .4));
  return Math.min(up, dn);
}

export function buildSets(book) {
  const L = [], S = book.stage, ex = {};
  // ===== 0 · prologue =====
  popper(L, 0, S, A.sketchTree(.09), -.17, 0, .03);
  popper(L, 0, S, A.sketchTree(.07), -.05, 0, .025);
  popper(L, 0, S, A.sketchTree(.1), .19, 0, .04);
  popper(L, 0, S, P.sketchRiverBank(.44, .02, 3), 0, 0, .065, { dir: -1 });
  popper(L, 0, S, P.sketchRiverBank(.44, .016, 5), 0, 0, .1, { dir: -1 });
  ex.bird1 = popper(L, 0, S, P.crane(.028), .045, 0, .145);
  ex.bird2 = popper(L, 0, S, P.crane(.026), .085, 0, .15);
  ex.arrow = cutMesh(P.arrow(.03)); ex.arrow.visible = false; S.add(ex.arrow);
  // ===== 1 · Ayodhya (left) & Mithila (right) =====
  popper(L, 1, S, A.hill(.26, .07, '#b5e39a', '#93cc78', 11, { bumps: 2 }), -.1, 0, .012);
  popper(L, 1, S, A.hill(.24, .08, '#a9dd8c', '#88c46c', 12, { bumps: 3 }), .12, 0, .014);
  ex.palace = popper(L, 1, S, P.palace(.13), -.11, 0, .035);
  popper(L, 1, S, A.lolliTree(.06, '#5cbf4a', '#3f9934', 21), .03, 0, .05, { sway: .03 });
  popper(L, 1, S, A.lolliTree(.05, '#6fcc55', '#4ea93e', 22), .2, 0, .055, { sway: .03 });
  ex.throne = popper(L, 1, S, P.throne(.04), -.1, 0, .11);
  popper(L, 1, S, P.bowStand(.08), .12, 0, .108);
  ex.bowL = popper(L, 1, S, P.bowHalf(.09, -1), .12, .02, .112, { dir: 1 });
  ex.bowR = popper(L, 1, S, P.bowHalf(.09, 1), .12, .02, .113, { dir: 1 });
  ex.sandals = cutMesh(P.sandals(.014)); ex.sandals.visible = false; S.add(ex.sandals);
  const R1 = mulberry(90);
  for (let i = 0; i < 8; i++) popper(L, 1, S, A.flower(.014 + R1() * .006, ['#ff7aa8', '#ffd23f', '#ffffff', '#ff9a2e'][i % 4], i), -.2 + i * .057, 0, .25 + R1() * .03, { sway: .08 });
  // ===== 2 · forest =====
  const R2 = mulberry(7);
  for (let i = 0; i < 11; i++) popper(L, 2, S, A.pine(.12 + R2() * .04, '#7fbf9e', '#66a886', 100 + i), -.22 + i * .044, 0, .01 + (i % 2) * .004, { sway: .01 });
  for (let i = 0; i < 6; i++) popper(L, 2, S, A.pine(.09 + R2() * .03, '#2f8a55', '#236b40', 120 + i), -.2 + i * .08 + (R2() - .5) * .02, 0, .04 + (i % 2) * .008, { sway: .015 });
  popper(L, 2, S, P.hut(.06), -.13, 0, .08);
  ex.deer = popper(L, 2, S, P.deer(.03), .13, 0, .13, { t0: 60.1 });
  for (const [x, z, h] of [[-.2, .22, .022], [.09, .24, .02], [.2, .21, .024]]) popper(L, 2, S, A.fern(h, 140 + Math.round(x * 100)), x, 0, z, { sway: .05 });
  ex.chariot = new THREE.Group(); { const c = cutMesh(P.chariot(.06)); c.position.z = .006; ex.chariot.add(c); for (const dx of [-.022, .022]) { const th = thread(.3); th.position.set(dx, .012, 0); ex.chariot.add(th); } } ex.chariot.visible = false; S.add(ex.chariot);
  // ===== 3 · Kishkindha & Lanka =====
  popper(L, 3, S, P.rockHill(.2, .08, 3), -.12, 0, .015);
  popper(L, 3, S, P.rockHill(.14, .05, 4), -.17, 0, .05);
  popper(L, 3, S, P.lanka(.12), .15, 0, .03);
  ex.waves3 = [];
  const wc = [['#7fd6e6', '#5cc0d6'], ['#5cc0d6', '#3fa8c6'], ['#3fa8c6', '#2f8fb0']];
  for (let k = 0; k < 3; k++) ex.waves3.push(popper(L, 3, S, A.waveStrip(.13, .016 - k * .002, wc[k][0], wc[k][1], 60 + k, 6), .035, 0, .07 + k * .045, { dir: 1 }));
  popper(L, 3, S, P.ashoka(.07), .19, 0, .1, { sway: .02 });
  const R3 = mulberry(3);
  ex.monkeys = [];
  for (let i = 0; i < 6; i++) ex.monkeys.push(popper(L, 3, S, P.monkey(.022 + R3() * .004, i), -.205 + i * .03, 0, .1 + (i % 2) * .01, { t0: 76.2 + i * .12 }));
  // ===== 4 · war =====
  popper(L, 4, S, P.lanka(.12), .15, 0, .025);
  ex.waves4 = [];
  for (let k = 0; k < 2; k++) ex.waves4.push(popper(L, 4, S, A.waveStrip(.44, .014 - k * .003, wc[k][0], wc[k][1], 70 + k, 14), 0, 0, .05 + k * .04, { dir: 1 }));
  ex.stones = [];
  for (let i = 0; i < 9; i++) ex.stones.push(popper(L, 4, S, P.stone(.018, i + 3), -.16 + i * .036, 0, .115 - i * .006, { t0: 91.4 + i * .24 }));
  for (let i = 0; i < 5; i++) popper(L, 4, S, P.monkey(.02, i + 1), -.2 + i * .022, 0, .2 + (i % 2) * .012, { t0: 92.2 + i * .1 });
  popper(L, 4, S, P.flames(.016, 1), .2, 0, .07);
  popper(L, 4, S, P.flames(.012, 2), .1, 0, .055);
  ex.crown = new THREE.Group(); { const c = cutMesh(P.crownProp(.014)); ex.crown.add(c); const th = thread(.3); th.position.set(0, .004, -.0004); ex.crown.add(th); } ex.crown.visible = false; S.add(ex.crown);
  // ===== 5 · hermitage (rises on the war page after it folds) =====
  popper(L, 5, S, P.hut(.065), -.08, 0, .06);
  for (const [x, z, h] of [[-.19, .03, .1], [.04, .03, .08], [.18, .05, .1]]) popper(L, 5, S, A.lolliTree(h * .7, '#9a8ad8', '#7a6ab8', Math.round(x * 100) + 50), x, 0, z, { sway: .02 });
  for (let i = 0; i < 7; i++) popper(L, 5, S, A.flower(.014, ['#ffffff', '#ffd23f', '#d8b4ff'][i % 3], i + 20), -.2 + i * .065, 0, .26, { sway: .08 });
  ex.notes = [0, 1, 2, 3].map(i => { const m = cutMesh(P.note(.01, i)); m.visible = false; S.add(m); return m; });
  return { L, ex };
}

// backdrop slats that flip (front = a, back = b)
export function buildSlats(book, aTex, bTex) {
  const n = 4, w = (BW - .006) / n, h = BD - .03, out = [];
  for (let i = 0; i < n; i++) {
    const g = new THREE.Group(); g.position.set(-BW / 2 + .003 + w * (i + .5), .03 + h / 2, .004);
    const mk = (tex, side, flipU) => {
      const geo = new THREE.PlaneGeometry(w, h), uv = geo.attributes.uv;
      for (let k = 0; k < uv.count; k++) { const u = uv.getX(k), v = uv.getY(k); uv.setXY(k, (i + (flipU ? 1 - u : u)) / n, (.03 + v * h) / BD); }
      const m = new THREE.Mesh(geo, new THREE.MeshStandardMaterial({ map: tex, roughness: .9, side })); m.receiveShadow = m.castShadow = true; return m;
    };
    g.add(mk(aTex, THREE.FrontSide, false)); g.add(mk(bTex, THREE.BackSide, true)); g.visible = false;
    book.sky.add(g); out.push(g);
  }
  return out;
}

export function updatePops(L, t) {
  for (const r of L) {
    const k = riseOf(r, t);
    r.g.visible = k > .002; if (!r.g.visible) continue;
    r.g.rotation.x = r.dir * (Math.PI / 2) * (1 - k);
    if (r.sway) r.m.rotation.z = Math.sin(t * 1.6 + r.ph) * r.sway * k;
  }
}
