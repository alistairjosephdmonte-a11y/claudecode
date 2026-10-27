// One function per world (palette, set), the Cold Door (a taped-up mini fridge that opens a violet portal), and the insert shots.
// Violet belongs to the portal only: no world uses it.
import { clamp, lerp, hash, seg, ss, eo, back, TAU } from '/core/lib.js';
import { INK, g, push, pop, translate, rotate, scale, shape, fillOnly, stroke, ell, arc, spline, rr, rect, quad, dot, text, bands, screenRect, S } from './toon.js';
import { C, curd, basket } from './chars.js';

export const FLOOR = 900;
export const PORTAL = { rim: '#8B4DFF', armA: '#C7A6FF', armB: '#6A36D9', core: '#F3ECFF', wash: 'rgba(139,77,255,.14)' };
const sh = (pts, fill, s2, o = {}) => shape(pts, { fill, lw: o.lw ?? 6, shade: s2 ? () => fillOnly(s2[0], s2[1], { boil: .3 }) : undefined });

// ---------- the Cold Door ----------
export function fridge(x, y, { door = 0, t = 0, s = 1 } = {}) {
  push(); translate(x, y); scale(s);
  for (const wx of [-60, 60]) shape(ell(wx, -8, 16, 16), { fill: '#2B2D35', lw: 6 });
  sh(rr(-110, -300, 220, 290, 22), '#DDE3E8', [rect(40, -300, 80, 300), '#B4BCC4']);
  stroke(spline([[60, -300], [70, -360], [40, -400], [80, -440]], false), 5); dot(80, -440, 7, '#E8392B');   // coat-hanger antenna
  sh(rect(-60, -270, 90, 26), '#F2D36B', null, { lw: 5 });   // duct tape
  if (door > 0) { push(); translate(-110, 0); scale(1 - door * .85, 1); sh(rr(0, -296, 220, 282, 18), '#EEF2F5', [rect(160, -296, 60, 282), '#C9D0D6']); pop(); }
  else stroke([[80, -230], [80, -180]], 10, { line: '#9AA3AC' });
  pop();
}
// the portal: lumpy rim, rotating spiral arms (on ones), pale core, orbiting sparks, drips
export function portal(cx, cy, k, t, { rx = 230, ry = 320 } = {}) {
  if (k <= .01) return;
  push(); translate(cx, cy); scale(k * .74, k);
  const n = 40, rim = []; for (let i = 0; i < n; i++) { const a = i / n * TAU, r = 1 + .06 * Math.sin(a * 5 + t * 3) + .04 * Math.sin(a * 9 - t * 2); rim.push([Math.cos(a) * rx * r, Math.sin(a) * ry * r]); }
  shape(rim, { fill: PORTAL.rim, lw: 8 });
  shape(ell(0, 0, rx * .84, ry * .84, 48), { fill: PORTAL.armB, lw: 0, shade: () => {
    for (let i = 0; i < 5; i++) { const pts = []; for (let j = 0; j <= 24; j++) { const u = j / 24, a = i / 5 * TAU + u * 4.2 - t * 3.2, r = u; pts.push([Math.cos(a) * rx * .84 * r, Math.sin(a) * ry * .84 * r]); } stroke(pts, 26, { line: i % 2 ? PORTAL.armA : '#9E6BFF', boil: .5 }); }
    fillOnly(ell(0, 0, rx * .22, ry * .22), PORTAL.core, { boil: .4 });
  } });
  for (let i = 0; i < 7; i++) { const a = i / 7 * TAU + t * 1.3; dot(Math.cos(a) * rx * 1.12, Math.sin(a) * ry * 1.08, 7, PORTAL.armA); }
  for (const [dx, L] of [[-60, 40], [10, 60], [70, 34]]) shape(spline([[dx - 12, ry * .96], [dx + 12, ry * .96], [dx + 8, ry * .96 + L * .7], [dx, ry * .96 + L], [dx - 8, ry * .96 + L * .7]]), { fill: PORTAL.rim, lw: 6 });
  pop();
}
// full-screen swirl wipe (screen space): k 0→1→0 around the cut
export function swirlWipe(k, t) {
  if (k <= 0) return;
  g.setTransform(1, 0, 0, 1, 0, 0); const R = Math.hypot(960, 540) * 1.1 * k;
  g.save(); g.translate(960, 540);
  g.beginPath(); g.arc(0, 0, R, 0, TAU); g.fillStyle = PORTAL.armB; g.fill();
  for (let i = 0; i < 6; i++) { g.beginPath(); for (let j = 0; j <= 30; j++) { const u = j / 30, a = i / 6 * TAU + u * 5 - t * 6; g.lineTo(Math.cos(a) * R * u, Math.sin(a) * R * u); } g.lineWidth = 60 * k; g.strokeStyle = i % 2 ? PORTAL.armA : PORTAL.rim; g.lineCap = 'round'; g.stroke(); }
  g.beginPath(); g.arc(0, 0, R * .18, 0, TAU); g.fillStyle = PORTAL.core; g.fill();
  g.beginPath(); g.arc(0, 0, R, 0, TAU); g.lineWidth = 10; g.strokeStyle = INK; g.stroke();
  g.restore();
}

// ---------- worlds ----------
const floorBand = (col, line) => { fillOnly(rect(-3000, FLOOR, 8000, 1200), col, { boil: 0 }); stroke([[-3000, FLOOR], [5000, FLOOR]], 6, { line: line ?? INK }); };
function shelves(x0, n, col, prod, y = FLOOR, h = 420, w = 230, seed = 1) {
  for (let i = 0; i < n; i++) {
    const x = x0 + i * (w + 20);
    sh(rect(x, y - h, w, h), col[0], [rect(x + w - 40, y - h, 40, h), col[1]], { lw: 5 });
    for (let r = 1; r <= 3; r++) { const yy = y - h + r * h / 4 + 14; stroke([[x, yy], [x + w, yy]], 4);
      for (let k = 0; k < 4; k++) { const ph = 40 + hash(seed + i * 9 + r * 3 + k) * 34; fillOnly(rect(x + 12 + k * 54, yy - ph, 40, ph), prod[Math.floor(hash(seed * 3 + i + r + k * 7) * prod.length)], { boil: .4 }); } }
  }
}
export const WORLDS = {
  home: { pal: ['#263049', '#E3B341', '#F1E6CF'], draw(t) {
    bands(['#1E2740', '#263049', '#2D385A'], -400, FLOOR); floorBand('#3B4466');
    shelves(-200, 3, ['#E3B341', '#B88A24'], ['#F1E6CF', '#7FC8E8', '#C8326B', '#8FBF5A'], FLOOR, 520, 230, 4);
    for (let i = 0; i < 3; i++) { fillOnly(rect(200 + i * 520, 70, 260, 22), '#F7F3EA', { boil: .2 }); fillOnly(rect(180 + i * 520, 92, 300, 30), 'rgba(247,243,234,.12)', { boil: .2 }); }
    for (let i = 0; i < 4; i++) sh(rr(1020 + (i % 2) * 120, FLOOR - 110 - Math.floor(i / 2) * 110, 110, 104, 6), '#C9A26A', [rect(1100 + (i % 2) * 120, FLOOR - 110 - Math.floor(i / 2) * 110, 30, 104), '#A47E48'], { lw: 5 });
  } },
  funnel: { pal: ['#FF4D8D', '#1FB5A8', '#FFF4F8'], draw(t) {
    bands(['#FF7FB0', '#FF4D8D'], -400, FLOOR); floorBand('#1FB5A8');
    for (let i = 0; i < 6; i++) { const x = -200 + i * 420; sh([[x, FLOOR], [x + 120, 300], [x + 220, 300], [x + 340, FLOOR]], '#FFF4F8', [[[x + 200, 300], [x + 220, 300], [x + 340, FLOOR], [x + 260, FLOOR]], '#F2C9D8'], { lw: 6 }); }
    sh(rr(2300, 420, 340, 480, 20), '#1FB5A8', [rect(2560, 420, 80, 480), '#168C82']);
    for (let i = 0; i < 9; i++) fillOnly(rect(-200 + i * 300, 160 + (i % 2) * 40, 120, 40), '#FFF4F8', { alpha: .7 });
  } },
  counter: { pal: ['#8B5E3C', '#F2DDB8', '#9C2F2F'], draw(t) {
    bands(['#F2DDB8', '#E8CC9C'], -400, FLOOR); floorBand('#8B5E3C');
    shelves(-150, 7, ['#8B5E3C', '#6B4428'], ['#F2DDB8', '#9C2F2F', '#D9B47A'], FLOOR - 260, 520, 230, 7);
    sh(rect(-400, FLOOR - 260, 2800, 260), '#9C2F2F', [rect(-400, FLOOR - 260, 2800, 40), '#7A2222']);
  } },
  round: { pal: ['#FFB38A', '#4B5D7A', '#FFFFFF'], draw(t) {
    bands(['#FFD3B0', '#FFB38A', '#F49A70'], -400, FLOOR - 200); floorBand('#4B5D7A');
    dot(1500, 300, 120, '#FFF1C8');
    for (let i = 0; i < 6; i++) { const x = -260 + i * 360; sh(rect(x, FLOOR - 520, 320, 520), i % 2 ? '#6B7C99' : '#5A6B88', [rect(x + 260, FLOOR - 520, 60, 520), '#46566F'], { lw: 5 }); sh(rect(x + 120, FLOOR - 170, 80, 170), '#2F3B52'); for (let w = 0; w < 2; w++) sh(rect(x + 40 + w * 160, FLOOR - 440, 80, 90), '#FFD3B0', null, { lw: 4 }); }
  } },
  maze: { pal: ['#E8A317', '#B23A2A', '#F7F3EA'], draw(t) {
    bands(['#E8A317', '#F0B83A'], -400, FLOOR); for (let i = -20; i < 40; i++) fillOnly(rect(i * 120, FLOOR, 60, 600), i % 2 ? '#F7F3EA' : INK, { boil: 0 }); stroke([[-3000, FLOOR], [5000, FLOOR]], 6);
    shelves(-150, 8, ['#B23A2A', '#8C2A1E'], ['#F7F3EA', '#E8A317', '#8FBF5A'], FLOOR, 460, 230, 11);
  } },
  kitchen: { pal: ['#9FE3C1', '#8C96A3', '#FFF6E0'], draw(t) {
    bands(['#B8EDD2', '#9FE3C1'], -400, FLOOR); floorBand('#8C96A3');
    for (let i = 0; i < 12; i++) fillOnly(rect(-300 + i * 240, -200, 120, 1100), 'rgba(255,255,255,.18)', { boil: 0 });
    sh(rr(1240, FLOOR - 560, 260, 560, 40), '#FFF6E0', [rect(1420, FLOOR - 560, 80, 560), '#E1D6B8']); sh(ell(1370, FLOOR - 600, 110, 50), '#8C96A3', null);
  } },
  garage: { pal: ['#7FD3B6', '#3E4A57', '#F4EAD5'], draw(t) {
    bands(['#7FD3B6', '#9FE3C1'], -400, FLOOR - 300); floorBand('#3E4A57');
    sh(rect(-300, FLOOR - 640, 2600, 640), '#F4EAD5', [rect(-300, FLOOR - 640, 2600, 60), '#D8CBAE']);
    shelves(-200, 7, ['#7FD3B6', '#5BB396'], ['#F4EAD5', '#E07A2E', '#3E4A57'], FLOOR, 380, 230, 13);
  } },
  dock: { pal: ['#A9D8F5', '#2E3238', '#F2C230'], draw(t) {
    bands(['#2E3238', '#3A3F47'], -400, FLOOR); floorBand('#5A6069');
    sh(rect(-300, FLOOR - 620, 1300, 620), '#A9D8F5', [rect(800, FLOOR - 620, 200, 620), '#7FB6D8']);
    for (let i = 0; i < 10; i++) fillOnly([[-300 + i * 140, FLOOR - 40], [-240 + i * 140, FLOOR - 40], [-300 + i * 140 + 120, FLOOR], [-300 + i * 140 + 60, FLOOR]], i % 2 ? '#F2C230' : '#2E3238', { boil: 0 });
    for (let i = 0; i < 3; i++) for (let k = 0; k < 4; k++) sh(rr(-200 + i * 100, FLOOR - 120 - k * 90, 90, 84, 8), '#F7F3EA', [rect(-130 + i * 100, FLOOR - 120 - k * 90, 20, 84), '#D6D9DE'], { lw: 4 });
  } },
  konbini: { pal: ['#FAFAFA', '#00A6A6', '#F2542D'], draw(t) {
    bands(['#FAFAFA', '#EEF7F7'], -400, FLOOR); floorBand('#DDE7E7');
    fillOnly(rect(-300, 0, 2600, 70), '#00A6A6', { boil: 0 }); fillOnly(rect(-300, 70, 2600, 20), '#F2542D', { boil: 0 });
    sh(rect(-100, FLOOR - 560, 2000, 520), '#00A6A6', [rect(-100, FLOOR - 560, 2000, 50), '#007F7F']);
    for (let i = 0; i < 8; i++) { sh(rect(-80 + i * 245, FLOOR - 500, 225, 440), '#D6F2F2', null, { lw: 5 }); for (let r = 0; r < 3; r++) for (let k = 0; k < 4; k++) fillOnly(rect(-60 + i * 245 + k * 52, FLOOR - 470 + r * 140, 38, 90), ['#FAFAFA', '#F2542D', '#FFC940'][(i + r + k) % 3], { boil: .3 }); }
  } },
  track: { pal: ['#FF8C1A', '#2E55D4', '#FFFFFF'], draw(t) {
    bands(['#2E55D4', '#3D66E6'], -400, FLOOR); for (let i = -20; i < 40; i++) for (let j = 0; j < 4; j++) fillOnly(rect(i * 80, FLOOR + j * 80, 80, 80), (i + j) % 2 ? '#FFFFFF' : INK, { boil: 0 });
    for (let i = 0; i < 7; i++) { sh(rect(-200 + i * 360, FLOOR - 330, 300, 330), '#FF8C1A', [rect(-200 + i * 360 + 240, FLOOR - 330, 60, 330), '#D96E06'], { lw: 5 }); for (let k = 0; k < 6; k++) fillOnly(rr(-180 + i * 360 + (k % 3) * 90, FLOOR - 300 + Math.floor(k / 3) * 140, 70, 110, 8), '#FFFFFF', { boil: .3 }); }
  } },
  globe: { pal: ['#0E3B43', '#F2C94C', '#E8F1F2'], draw(t) {
    bands(['#0E3B43', '#124A54'], -400, FLOOR); floorBand('#0A2C32');
    for (let i = 0; i < 40; i++) dot(-300 + hash(i) * 2600, -200 + hash(i + 7) * 900, 3 + hash(i + 3) * 3, '#F2C94C');
    shape(ell(1650, 360, 230, 230), { fill: '#E8F1F2', lw: 7, shade: () => { for (let i = 0; i < 4; i++) { const a = t * .6 + i * 1.6; fillOnly(ell(1650 + Math.sin(a) * 160, 260 + i * 70, 70 * Math.max(.2, Math.cos(a)), 40), '#F2C94C', { boil: .4 }); } } });
  } },
  beige: { pal: ['#EADCC2', '#8A6E4B', '#F6EEDD'], draw(t) {
    bands(['#EADCC2', '#E4D3B4'], -400, FLOOR); floorBand('#C9B08A');
    for (let i = 0; i < 3; i++) { sh(rect(-100 + i * 700, 160, 300, 220), '#F6EEDD', null, { lw: 5 }); for (let k = 0; k < 4; k++) stroke([[-80 + i * 700, 200 + k * 44], [180 + i * 700, 200 + k * 44]], 4, { line: '#8A6E4B' }); }
    sh(rect(1300, FLOOR - 300, 500, 300), '#8A6E4B', [rect(1300, FLOOR - 300, 500, 40), '#6E5638']);
    sh(rr(200, FLOOR - 240, 140, 240, 10), '#B89A70', null, { lw: 5 });
  } },
};
// six one-second cities for the montage: same framing, different two-tone palette
const CITY = { london: ['#6E7681', '#C0392B'], paris: ['#22324F', '#EADBC8'], sydney: ['#1C7FBF', '#F2D49B'], chicago: ['#7A3B2E', '#9AA5B1'], manchester: ['#5D6B5F', '#C7CFC2'], melbourne: ['#E2B93B', '#4D5156'] };
for (const [k, [a, b]] of Object.entries(CITY)) WORLDS[k] = { pal: [a, b], city: 1, draw(t) {
  bands([a, a], -400, FLOOR); floorBand(b);
  for (let i = 0; i < 7; i++) { const h = 300 + hash(i * 3 + k.length) * 300; sh(rect(-260 + i * 330, FLOOR - h, 300, h), b, [rect(-260 + i * 330 + 240, FLOOR - h, 60, h), a], { lw: 5 }); for (let w = 0; w < 3; w++) sh(rect(-220 + i * 330 + w * 80, FLOOR - h + 40, 50, 60), a, null, { lw: 4 }); }
  sh(rect(560, FLOOR - 420, 800, 420), '#FFFFFF', null);
  const front = ['london', 'paris', 'sydney'].includes(k), cx = front ? 620 : 1180;
  sh(rr(cx, FLOOR - 300, 150, 290, 10), '#7FC8E8', [rect(cx + 110, FLOOR - 300, 40, 290), '#5AA8C8']);
  for (let r = 0; r < 3; r++) fillOnly(rect(cx + 20, FLOOR - 270 + r * 90, 110, 50), '#FFFFFF', { boil: .3 });
} };

// ---------- inserts (drawn around the origin, framed by the insert camera) ----------
export const INSERTS = {
  card: (t, u, o = {}) => { fillOnly(rect(-1200, -700, 2400, 1400), '#2D385A', { boil: 0 }); push(); rotate(-.04); sh(rr(-430, -260, 860, 520, 10), '#FFFDF5', [rect(-430, 140, 860, 120), '#EEE6D4']); fillOnly(rect(-430, -260, 860, 70), '#C8326B', { boil: .3 });
    text('CUSTOMER COMMENT CARD', 0, -224, { font: '800 34px "Baloo 2"', fill: '#FFFDF5' });
    const msg = o.alt ? 'Why are the eggs in the middle?' : 'Why is the milk at the back??'; const n = Math.floor(clamp(u / 1.6) * msg.length);
    text(msg.slice(0, n), 0, -40, { font: '64px "Caveat Brush"', fill: '#2A2A6A' });
    if (u > 1.8 && !o.alt) { stroke([[-330, 10], [330, 0]], 6, { line: '#2A2A6A' }); if (u > 2.1) stroke([[-320, 30], [320, 22]], 6, { line: '#2A2A6A' }); }
    pop(); },
  curd: (t, u, o = {}) => { WORLDS.home.draw(t); push(); translate(0, 140); fillOnly(rect(-300, 0, 600, 40), '#B4BCC4', { boil: .2 }); curd(0, 0, 2.2, { t, look: [.2, -.2], happy: o.wave ? 1 : 0, wave: o.wave ? 1 : 0, sq: 1 - .08 * Math.abs(Math.sin(t * 6)) }); pop(); },
  basket: (t, u, o = {}) => { fillOnly(rect(-1200, -700, 2400, 1400), o.bg || '#FF4D8D', { boil: 0 }); basket(0, 280, 2.2, o.items || []); },
  moth: (t, u) => { WORLDS.funnel.draw(t); push(); translate(Math.sin(t * 2) * 200, -60 + Math.cos(t * 3) * 40); for (const s2 of [-1, 1]) shape(spline([[0, 0], [s2 * 160, -120 + Math.sin(t * 20) * 40], [s2 * 200, 40], [s2 * 60, 60]]), { fill: '#FFF4F8', lw: 7 }); shape(ell(0, 20, 30, 70), { fill: '#1FB5A8', lw: 7 }); for (const ex of [-12, 12]) shape(ell(ex, -30, 12, 14), { fill: '#fff', lw: 5, shade: () => dot(ex, -28, 4) }); sh(rect(-50, 70, 100, 50), '#FFF4F8', null, { lw: 5 }); pop(); },
  ladder: (t, u) => { WORLDS.counter.draw(t); const x = lerp(-600, 600, clamp(u / 1.4)); push(); translate(x, 0); stroke([[-60, -500], [-60, 300]], 10); stroke([[60, -500], [60, 300]], 10); for (let r = 0; r < 8; r++) stroke([[-60, -460 + r * 100], [60, -460 + r * 100]], 8); fillOnly(spline([[-40, -300], [40, -300], [50, -40], [-50, -40]]), INK); fillOnly(ell(0, -350, 40, 46), INK); pop(); },
  machine: (t, u) => { fillOnly(rect(-1200, -700, 2400, 1400), '#9FE3C1', { boil: 0 }); sh(rect(-500, -320, 1000, 640), '#8C96A3', [rect(300, -320, 200, 640), '#6E7884']); for (let i = 0; i < 4; i++) stroke(spline([[-440, -240 + i * 120], [-150, -200 + i * 120], [150, -280 + i * 120], [440, -230 + i * 120]], false), 18, { line: '#F4EAD5' }); sh(ell(-200, 120, 120, 120), '#3E4A57', null); sh(rr(80, 40, 260, 180, 16), '#3E4A57', null); for (let i = 0; i < 5; i++) { const f = (t * 1.2 + i * .2) % 1; fillOnly(ell(140 + i * 40, 20 - f * 260, 30 + f * 30, 24 + f * 20), '#E8EEF2', { alpha: 1 - f }); } },
  coldroom: (t, u) => { fillOnly(rect(-1200, -700, 2400, 1400), '#2E3238', { boil: 0 }); sh(rect(-800, -300, 520, 560), '#5A6069', null); sh(rect(-280, -300, 600, 560), '#A9D8F5', null); sh(rect(320, -300, 480, 560), '#FAFAFA', null); sh(rect(300, -300, 30, 560), '#00A6A6', null);
    const px = lerp(-700, -200, clamp(u / 4)); for (let k = 0; k < 4; k++) sh(rr(px + (k % 2) * 90, 140 - Math.floor(k / 2) * 90, 84, 84, 6), '#F7F3EA', null, { lw: 4 }); for (let i = 0; i < 3; i++) stroke([[-280, -180 + i * 160], [320, -180 + i * 160]], 6); },
  shelf: (t, u) => { fillOnly(rect(-1200, -700, 2400, 1400), '#A9D8F5', { boil: 0 }); for (let r = 0; r < 2; r++) stroke([[-900, -100 + r * 300], [900, -100 + r * 300]], 8); for (let i = 0; i < 5; i++) { const pushK = i === 2 ? back(seg(u, .3, .7), 2) : 0; sh(rect(-500 + i * 220, -340 + pushK * 0, 140, 230 + pushK * 0), '#FFFFFF', null); push(); translate(-430 + i * 220, -100); scale(1 + pushK * .25); pop(); }
    if (u > .4) { shape(spline([[-60, 320], [-40, 180], [60, 170], [80, 320]]), { fill: '#F2C9A0', lw: 7 }); } },
  plan: (t, u) => { fillOnly(rect(-1200, -700, 2400, 1400), '#2E55D4', { boil: 0 }); sh(rect(-640, -380, 1280, 760), '#FFFFFF', null); for (let i = 0; i < 6; i++) sh(rect(-420 + i * 160, -200, 60, 420), '#FF8C1A', null, { lw: 5 });
    const pts = [[0, 380], [-560, 330], [-560, -320], [560, -320], [560, 330], [40, 330]], k = clamp(u / 6); const n = Math.max(2, Math.floor(k * 60)); const P_ = []; for (let i = 0; i <= n; i++) { const f = i / 60 * (pts.length - 1), a = Math.floor(f), b = Math.min(pts.length - 1, a + 1), r = f - a; P_.push([lerp(pts[a][0], pts[b][0], r), lerp(pts[a][1], pts[b][1], r)]); } stroke(P_, 16, { line: '#F2542D' }); fillOnly(rect(-600, -370, 1200, 40), '#7FC8E8'); },
  eyeline: (t, u) => { WORLDS.track.draw(t); const a = clamp(u / 1.2), b = clamp((u - 4) / 1.2); if (a) fillOnly(rect(-300, 360, 2600 * a, 40), '#FFFFFF', { alpha: .8 }); if (b) fillOnly(rect(-300, 640, 2600 * b, 40), '#FFFFFF', { alpha: .8 }); },
  triangle: (t, u) => { fillOnly(rect(-1200, -700, 2400, 1400), '#FF8C1A', { boil: 0 }); const P3 = [[-520, -260], [520, -260], [0, 330]]; P3.forEach(([x, y], i) => { const p = back(seg(u, .3 + i * .5, .7 + i * .5), 2); push(); translate(x, y); scale(p * 1.6); if (i === 0) { sh(rect(-40, -100, 80, 100), '#FFFFFF', null); sh([[-40, -100], [0, -140], [40, -100]], '#2E55D4', null); } else if (i === 1) { sh(rr(-60, -40, 120, 40, 6), '#F4EAD5', null); for (let k = 0; k < 3; k++) sh(ell(-36 + k * 36, -50, 16, 20), '#FFFFFF', null, { lw: 4 }); } else sh(spline([[-60, 0], [-64, -40], [-20, -64], [20, -64], [64, -40], [60, 0]]), '#E0A65A', null); pop(); });
    const k = clamp((u - 2) / 3); if (k > 0) { const L = [P3[0], P3[1], P3[2], P3[0]]; const out = [L[0]]; for (let i = 1; i < 4; i++) { const f = clamp(k * 3 - (i - 1)); if (f <= 0) break; out.push([lerp(L[i - 1][0], L[i][0], f), lerp(L[i - 1][1], L[i][1], f)]); } stroke(out, 16, { line: '#2E55D4' }); } },
  pipes: (t, u) => { WORLDS.beige.draw(t); const k = clamp(u / 5); const P_ = spline([[1700, 700], [1400, 400], [900, 450], [500, 300], [200, 500], [-100, 700]], false, 8); stroke(P_.slice(0, Math.max(2, Math.floor(P_.length * k))), 24, { line: '#8A6E4B' }); stroke(P_.slice(0, Math.max(2, Math.floor(P_.length * k))), 8, { line: '#F6EEDD' });
    const c = Math.floor(clamp((u - 4) / 4) * 10); for (let i = 0; i < c; i++) sh(ell(700, 820 - i * 24, 50, 16), '#D9B47A', null, { lw: 5 }); },
};
