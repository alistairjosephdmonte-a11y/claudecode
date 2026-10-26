// Page art for every location (backdrop = sky, floor = ground), drawn once.
import * as THREE from 'three';
import { cv, paperFill, GRAIN, smoothOpen } from './paper.js';
import { mulberry, TAU } from './lib.js';
import { BW, BD } from './book.js';
const PW = 2048, PH = Math.round(2048 * BD / BW);
const gx = xm => (xm / BW + .5) * PW, gz = zm => zm / BD * PH;


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
    x.font = 'italic 50px "Tiro Devanagari Hindi"'; x.fillStyle = 'rgba(80,70,60,.5)'; x.textAlign = 'center'; x.fillText('तमसा नदी', PW * .5, PH * .9);
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

  // --- pages added for the full film ---
  P0.skyAshram = page(x => { grad(x, [[0, '#ffd98a'], [.7, '#fff0c8'], [1, '#f4f6d8']]); x.beginPath(); x.arc(PW * .78, PH * .3, 110, 0, TAU); x.fillStyle = '#fff6d0'; x.fill(); clouds(x, 51, 'rgba(255,255,255,.5)', 5, .1, .4);
    const R = mulberry(52); x.fillStyle = '#b8d88a'; for (let i = 0; i < 18; i++) { const px = R() * PW, r = 80 + R() * 120; x.beginPath(); x.arc(px, PH * .92, r, Math.PI, 0); x.fill(); } });
  P0.groundAshram = page(x => { grad(x, [[0, '#b8d878'], [1, '#c8e08a']]); x.fillStyle = '#e8d6a0'; x.beginPath(); x.ellipse(PW * .5, gz(.17), PW * .28, gz(.07), 0, 0, TAU); x.fill(); dots(x, 53, 120, ['#ffffff', '#ffe066', '#f2a83a'], 4, 9); });
  P0.skyMithila = page(x => { grad(x, [[0, '#ffb0c0'], [.7, '#ffe0d0'], [1, '#fff4e0']]); clouds(x, 61, 'rgba(255,255,255,.55)', 6, .08, .45);
    for (const y0 of [.14]) { x.beginPath(); x.moveTo(0, PH * y0); x.quadraticCurveTo(PW / 2, PH * (y0 + .14), PW, PH * y0); x.lineWidth = 4; x.strokeStyle = '#6b4a36'; x.stroke();
      for (let i = 1; i < 26; i++) { const u = i / 26, px = PW * u, py = PH * (y0 + .28 * u * (1 - u)); x.beginPath(); x.arc(px, py + 22, 18, 0, TAU); x.fillStyle = ['#ff9a2e', '#ffd23f', '#ffffff'][i % 3]; x.fill(); } } });
  P0.groundMithila = page(x => { grad(x, [[0, '#f6c8a0'], [1, '#f8d8b0']]);
    for (const [cx, cz] of [[-.12, .17], [.12, .17]]) { const X0 = gx(cx), Y0 = gz(cz); for (let r = 5; r >= 1; r--) { x.beginPath(); for (let i = 0; i <= 16; i++) { const a = i / 16 * TAU, rr2 = r * 34 * (i % 2 ? .7 : 1); x.lineTo(X0 + Math.cos(a) * rr2, Y0 + Math.sin(a) * rr2 * .6); } x.closePath(); x.fillStyle = ['#e8413a', '#ffd23f', '#5cbf4a', '#ff9ec1', '#ffffff'][r - 1]; x.fill(); } }
    dots(x, 63, 120, ['#ffffff', '#ff9ec1', '#ffd23f'], 4, 8); });
  P0.skyRiver = page(x => { grad(x, [[0, '#8fd0f0'], [.75, '#d8f0f6'], [1, '#e8f6e8']]); clouds(x, 71, 'rgba(255,255,255,.6)', 5, .1, .4);
    x.fillStyle = '#a8d88a'; for (let i = 0; i < 9; i++) { const px = PW * i / 8, r = 140 + (i % 3) * 40; x.beginPath(); x.arc(px, PH * .95, r, Math.PI, 0); x.fill(); } });
  P0.groundRiver = page(x => { grad(x, [[0, '#86c763'], [.3, '#86c763'], [.33, '#5ab8e0'], [.66, '#3fa1d0'], [.69, '#e8d6a0'], [1, '#e8d6a0']], 0, 0, 0, PH);
    const R = mulberry(72); x.strokeStyle = 'rgba(255,255,255,.4)'; x.lineWidth = 6; x.lineCap = 'round'; for (let i = 0; i < 50; i++) { const px = R() * PW, py = PH * (.36 + R() * .28); x.beginPath(); x.moveTo(px, py); x.quadraticCurveTo(px + 30, py - 14, px + 60, py); x.stroke(); } });
  P0.skyPanch = page(x => { grad(x, [[0, '#f6b86a'], [.6, '#fde0a8'], [1, '#f0f0c8']]);
    const R = mulberry(81); x.fillStyle = '#d0a060'; for (let i = 0; i < 24; i++) { const px = R() * PW, h = PH * (.3 + R() * .3), w = 60 + R() * 60; x.beginPath(); x.moveTo(px, PH - h); x.lineTo(px + w, PH); x.lineTo(px - w, PH); x.closePath(); x.fill(); }
    x.beginPath(); x.arc(PW * .25, PH * .28, 100, 0, TAU); x.fillStyle = '#fff2c8'; x.fill(); });
  P0.groundPanch = page(x => { grad(x, [[0, '#7aa84a'], [1, '#8ab858']]); x.fillStyle = '#6ab0d0'; x.beginPath(); x.moveTo(0, gz(.03)); x.bezierCurveTo(PW * .3, gz(.06), PW * .7, gz(.0), PW, gz(.04)); x.lineTo(PW, 0); x.lineTo(0, 0); x.fill(); dots(x, 82, 160, ['#e8a33a', '#f2d29a', '#c9612e'], 5, 10); });
  P0.skyKish = page(x => { grad(x, [[0, '#f6c27a'], [.6, '#fbe0b0'], [1, '#f8eccc']]); clouds(x, 91, 'rgba(255,255,255,.45)', 5, .08, .35);
    x.fillStyle = '#d99a4a'; x.beginPath(); x.moveTo(0, PH); for (let i = 0; i <= 14; i++) x.lineTo(PW * i / 14, PH * (.55 + .14 * Math.sin(i * 1.9) + .05 * Math.sin(i * 4.3))); x.lineTo(PW, PH); x.fill();
    x.fillStyle = '#c4823a'; x.beginPath(); x.moveTo(0, PH); for (let i = 0; i <= 10; i++) x.lineTo(PW * i / 10, PH * (.72 + .08 * Math.sin(i * 2.7))); x.lineTo(PW, PH); x.fill(); });
  P0.groundKish = page(x => { grad(x, [[0, '#e0a24a'], [1, '#e8b25a']]); dots(x, 92, 130, ['#c27a32', '#f2d29a', '#9fd57a'], 5, 11); });
  P0.skyNight = page(x => { grad(x, [[0, '#141a3a'], [.65, '#2a2f6a'], [1, '#4a3f7a']]);
    const R = mulberry(101); for (let i = 0; i < 220; i++) { x.beginPath(); x.arc(R() * PW, R() * PH * .7, 1 + R() * 3, 0, TAU); x.fillStyle = `rgba(255,245,220,${.3 + R() * .6})`; x.fill(); }
    x.beginPath(); x.arc(PW * .82, PH * .2, 80, 0, TAU); x.fillStyle = '#fff3cf'; x.fill();
    x.fillStyle = '#c9902a'; for (let i = 0; i < 12; i++) { const cx = PW * (.04 + i * .085), h = PH * (.18 + (i % 4) * .06); x.fillRect(cx, PH - h, 60, h); x.beginPath(); x.arc(cx + 30, PH - h, 30, Math.PI, 0); x.fill(); }
    x.fillStyle = '#ffe680'; for (let i = 0; i < 40; i++) { x.fillRect(PW * (.05 + R() * .9), PH * (.82 + R() * .14), 10, 14); } });
  P0.groundNight = page(x => { grad(x, [[0, '#6a4a8a'], [1, '#7a5a9a']]); x.strokeStyle = 'rgba(255,220,140,.35)'; x.lineWidth = 4; for (let i = 0; i < 12; i++) { x.beginPath(); x.moveTo(PW * i / 12, 0); x.lineTo(PW * i / 12, PH); x.stroke(); x.beginPath(); x.moveTo(0, PH * i / 12); x.lineTo(PW, PH * i / 12); x.stroke(); } dots(x, 102, 60, ['#ffd23f', '#ff9a2e'], 3, 6); });
  P0.skyCourt = page(x => { grad(x, [[0, '#8a2a28'], [1, '#c0503a']]);
    for (let i = 0; i < 7; i++) { const px = PW * (.07 + i * .143); x.fillStyle = '#f6d48a'; x.fillRect(px - 26, PH * .1, 52, PH * .9); x.fillStyle = '#e8b85a'; x.fillRect(px - 40, PH * .08, 80, 30); }
    x.fillStyle = '#f2b632'; x.beginPath(); x.moveTo(0, 0); for (let i = 0; i <= 14; i++) x.lineTo(PW * i / 14, i % 2 ? PH * .1 : PH * .04); x.lineTo(PW, 0); x.fill(); });
  P0.groundCourt = page(x => { const n = 12; for (let i = 0; i < n; i++) for (let j = 0; j < 9; j++) { x.fillStyle = (i + j) % 2 ? '#f6ead0' : '#e8c890'; x.fillRect(PW * i / n, PH * j / 9, PW / n + 1, PH / 9 + 1); }
    x.fillStyle = '#c0392b'; x.fillRect(gx(-.05), 0, gx(.05) - gx(-.05), PH); x.fillStyle = '#f2b632'; x.fillRect(gx(-.05) - 8, 0, 8, PH); x.fillRect(gx(.05), 0, 8, PH); });
  P0.skyHerm = P0.sky5;
  P0.groundHerm = page(x => { grad(x, [[0, '#b8c890'], [1, '#c8d4a0']]); dots(x, 111, 140, ['#ffffff', '#d8b4ff', '#ffd23f'], 4, 9); });
  P0.skyRedSea = page(x => { grad(x, [[0, '#f6a86a'], [.6, '#fbd0a0'], [1, '#bfe6e6']]); clouds(x, 121, 'rgba(255,255,255,.45)', 5, .08, .35);
    x.fillStyle = '#3fb0c0'; x.fillRect(0, PH * .78, PW, PH * .22); x.fillStyle = '#7a2a22'; for (let i = 0; i < 5; i++) { const cx = PW * (.72 + i * .055), h = PH * (.1 + (i % 3) * .04); x.fillRect(cx, PH * .78 - h, 34, h); } });
  P0.groundShore = page(x => { grad(x, [[0, '#2f9ab8'], [.45, '#3fb5c8'], [.5, '#f2cf7a'], [1, '#e8be62']]);
    const R = mulberry(131); x.strokeStyle = 'rgba(255,255,255,.35)'; x.lineWidth = 6; x.lineCap = 'round'; for (let i = 0; i < 40; i++) { const px = R() * PW, py = R() * PH * .45; x.beginPath(); x.moveTo(px, py); x.quadraticCurveTo(px + 30, py - 14, px + 60, py); x.stroke(); } dots(x, 132, 80, ['#c27a32', '#fff2d0'], 4, 9); });
  P0.skyGold = page(x => { grad(x, [[0, '#ffcf5a'], [.6, '#ffe8a8'], [1, '#fff4d8']]); const R = mulberry(141);
    x.save(); x.translate(PW / 2, PH * .45); for (let i = 0; i < 24; i++) { x.rotate(TAU / 24); x.fillStyle = i % 2 ? 'rgba(255,255,255,.25)' : 'rgba(255,200,80,.18)'; x.beginPath(); x.moveTo(0, 0); x.lineTo(PW, -90); x.lineTo(PW, 90); x.closePath(); x.fill(); } x.restore();
    for (let i = 0; i < 30; i++) { x.beginPath(); x.arc(R() * PW, R() * PH * .6, 4 + R() * 6, 0, TAU); x.fillStyle = '#fffbe0'; x.fill(); } });
  return P0;
}


// location → page textures + light (sun intensity, colour, hemi)
export const PAGES = {
  graphite: ['sky0', 'ground0', 1.2, '#fff3e0'], ayodhya: ['sky1', 'ground1', 1.7, '#fff3e0'], dusk: ['sky1dusk', 'ground1', 1.0, '#ffb07a'],
  ashram: ['skyAshram', 'groundAshram', 1.6, '#fff0d0'], mithila: ['skyMithila', 'groundMithila', 1.7, '#fff0e8'], river: ['skyRiver', 'groundRiver', 1.7, '#fff6e8'],
  forest: ['sky2', 'ground2', 1.5, '#fff3e0'], panch: ['skyPanch', 'groundPanch', 1.5, '#ffe0b0'], kish: ['skyKish', 'groundKish', 1.6, '#fff0d8'],
  sea: ['sky3', 'ground3', 1.7, '#fff3e0'], night: ['skyNight', 'groundNight', .75, '#b8c0ff'], court: ['skyCourt', 'groundCourt', 1.4, '#ffe0c0'],
  war: ['sky4', 'ground4', 1.4, '#ffc090'], herm: ['skyHerm', 'groundHerm', 1.5, '#fff0f0'], shore: ['skyRedSea', 'groundShore', 1.6, '#fff0e0'],
  gold: ['skyGold', 'ground1', 1.8, '#fff6e0'],
};
