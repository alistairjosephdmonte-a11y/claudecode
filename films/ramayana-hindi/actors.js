// Cut-paper stick figures: ink-line limbs, a big round head, one costume shape, a white cut border.
// Each actor is a flat card whose canvas is redrawn only when its quantized pose changes.
import * as THREE from 'three';
import { cv, finishCut, sh, crescent, blob, INK, rr } from './paper.js';
import { TAU, mulberry, clamp } from './lib.js';
import { texOf } from './book.js';
import { mats, blobShadow } from './cutmesh.js';

export const SW = 760, SH = 1000;            // canvas px; feet at (380, 960)
const CX = 380, FOOT = 960, HIP = 610, NECK = 330, HEAD_Y = 225, HR = 96;
const PENCIL = 'rgba(70,72,82,.9)', CREAM = '#f6f0e1';

function limb(x, x0, y0, a1, l1, a2, l2, w, col) {
  // a = angle from straight down, positive = towards +x
  const x1 = x0 + Math.sin(a1) * l1, y1 = y0 + Math.cos(a1) * l1;
  const x2 = x1 + Math.sin(a1 + a2) * l2, y2 = y1 + Math.cos(a1 + a2) * l2;
  x.beginPath(); x.moveTo(x0, y0); x.lineTo(x1, y1); x.lineTo(x2, y2);
  x.lineWidth = w; x.strokeStyle = col; x.lineCap = 'round'; x.lineJoin = 'round'; x.stroke();
  return [x2, y2, a1 + a2];
}

// ---------- held props (drawn in hand space: origin = hand, +y along the forearm) ----------
function heldProp(x, kind, ink, pencil) {
  const f = (c) => pencil ? CREAM : c;
  if (kind === 'bow') {
    x.save(); x.rotate(Math.PI);
    x.beginPath(); x.moveTo(-10, -230); x.quadraticCurveTo(110, 0, -10, 230); x.lineWidth = 22; x.strokeStyle = ink; x.lineCap = 'round'; x.stroke();
    x.lineWidth = 12; x.strokeStyle = f('#c98a3a'); x.stroke();
    x.beginPath(); x.moveTo(-10, -230); x.lineTo(-10, 230); x.lineWidth = 4; x.strokeStyle = ink; x.stroke();
    x.restore();
  } else if (kind === 'mace') {
    x.save(); x.rotate(Math.PI);
    rr(x, -10, -40, 20, 200, 8); sh(x, f('#b07a3a'), 7, ink);
    x.beginPath(); x.arc(0, -70, 58, 0, TAU); sh(x, f('#f2b632'), 9, ink);
    x.beginPath(); x.arc(-18, -88, 16, 0, TAU); x.fillStyle = 'rgba(255,255,255,.45)'; x.fill();
    x.restore();
  } else if (kind === 'sandals') {
    for (const dx of [-34, 34]) { x.beginPath(); x.ellipse(dx, 40, 26, 60, 0, 0, TAU); sh(x, f('#a8683a'), 7, ink); x.beginPath(); x.arc(dx, 10, 9, 0, TAU); sh(x, f('#f2b632'), 4, ink); }
  } else if (kind === 'ring') {
    x.beginPath(); x.arc(0, 26, 20, 0, TAU); x.lineWidth = 9; x.strokeStyle = '#f2b632'; x.stroke(); x.beginPath(); x.arc(0, 4, 10, 0, TAU); sh(x, '#e8413a', 4, ink);
  } else if (kind === 'veena') {
    x.save(); x.rotate(Math.PI * .85);
    rr(x, -8, -260, 16, 300, 6); sh(x, f('#a8683a'), 6, ink);
    for (const y of [-250, 30]) { x.beginPath(); x.arc(0, y, 46, 0, TAU); sh(x, f('#e8a24a'), 7, ink); }
    x.restore();
  } else if (kind === 'axe') {
    x.save(); x.rotate(Math.PI);
    rr(x, -8, -60, 16, 280, 6); sh(x, f('#8a5a30'), 6, ink);
    x.beginPath(); x.moveTo(6, -40); x.quadraticCurveTo(120, -70, 110, 30); x.quadraticCurveTo(60, 0, 6, 10); x.closePath(); sh(x, f('#c9d0d8'), 7, ink);
    x.restore();
  } else if (kind === 'lamp') {
    x.beginPath(); x.ellipse(0, 30, 40, 18, 0, 0, Math.PI); sh(x, f('#c9933a'), 6, ink);
    x.beginPath(); x.ellipse(0, 4, 10, 22, 0, 0, TAU); x.fillStyle = '#ffb02e'; x.fill();
  } else if (kind === 'fruit') {
    x.beginPath(); x.ellipse(0, 40, 60, 30, 0, 0, Math.PI); x.lineTo(-60, 40); sh(x, f('#c9a06a'), 6, ink);
    for (const [dx, c] of [[-26, '#e8413a'], [0, '#ff9a2e'], [26, '#e8413a']]) { x.beginPath(); x.arc(dx, 28, 16, 0, TAU); sh(x, f(c), 4, ink); }
  } else if (kind === 'jewel') {
    x.beginPath(); x.arc(0, 30, 22, 0, TAU); sh(x, f('#f2b632'), 6, ink); x.beginPath(); x.arc(0, 30, 9, 0, TAU); sh(x, f('#3fa1de'), 3, ink);
  } else if (kind === 'hill') {
    x.save(); x.translate(0, -150); x.beginPath(); x.moveTo(-170, 60); x.lineTo(-90, -110); x.lineTo(-20, -40); x.lineTo(50, -150); x.lineTo(170, 60); x.closePath(); sh(x, f('#7fb05a'), 8, ink);
    for (const [dx, dy] of [[-60, -10], [20, -60], [80, 10], [-10, 20]]) { x.beginPath(); x.arc(dx, dy, 14, 0, TAU); sh(x, f('#fff35a'), 4, ink); }
    x.restore();
  } else if (kind === 'pot') {
    x.beginPath(); x.ellipse(0, 50, 50, 40, 0, 0, TAU); sh(x, f('#d9a04a'), 6, ink); x.beginPath(); x.ellipse(0, 14, 34, 10, 0, 0, TAU); sh(x, f('#fff6e0'), 5, ink);
  }
}

// ---------- heads & headwear ----------
function headwearBack(x, sp, hx, hy, ink, pencil) {
  const f = c => pencil ? CREAM : c;
  if (sp.hair === 'sita' || sp.hair === 'long') { blob(x, hx, hy + 30, HR * 1.12, HR * 1.25, .04, 3); sh(x, f('#2b1d18'), 8, ink); }
  if (sp.hair === 'sita') { x.beginPath(); x.arc(hx + 70, hy - 70, 48, 0, TAU); sh(x, f('#2b1d18'), 8, ink); }
  if (sp.hair === 'veil') { x.beginPath(); x.moveTo(hx - 130, hy + 200); x.quadraticCurveTo(hx - 140, hy - 140, hx, hy - 128); x.quadraticCurveTo(hx + 140, hy - 140, hx + 130, hy + 200); x.closePath(); sh(x, f(sp.veil || '#8a4fc0'), 9, ink); }
  if (sp.monkey) for (const s of [-1, 1]) { x.beginPath(); x.arc(hx + s * (sp.bear ? 70 : 98), hy - (sp.bear ? 74 : 6), 34, 0, TAU); sh(x, f(sp.skin), 8, ink); x.beginPath(); x.arc(hx + s * (sp.bear ? 70 : 98), hy - (sp.bear ? 74 : 6), 17, 0, TAU); x.fillStyle = f(sp.muzzle || '#f6d3a2'); x.fill(); }
  if (sp.heads) { // Ravana: nine more heads behind the main one
    const n = 4;
    for (const s of [-1, 1]) for (let k = n + (s > 0 ? 1 : 0); k >= 1; k--) {
      const r = HR * (.78 - k * .045), px = hx + s * (60 + k * 66), py = hy + 18 - k * 4;
      x.beginPath(); x.arc(px, py, r, 0, TAU); sh(x, f(sp.skin), 7, ink);
      for (const e of [-1, 1]) { x.beginPath(); x.ellipse(px + e * r * .32, py - 4, 6, 10, 0, 0, TAU); x.fillStyle = ink; x.fill(); }
      x.beginPath(); x.moveTo(px - r * .3, py + r * .42); x.lineTo(px + r * .3, py + r * .36); x.lineWidth = 5; x.strokeStyle = ink; x.stroke();
      crown(x, px, py - r * .82, r * .9, pencil, ink, .8);
    }
  }
}
function crown(x, cx, cy, w, pencil, ink, h = 1) {
  const f = c => pencil ? CREAM : c;
  x.beginPath(); x.moveTo(cx - w * .62, cy + 16);
  x.lineTo(cx - w * .7, cy - 50 * h); x.lineTo(cx - w * .35, cy - 22 * h); x.lineTo(cx, cy - 92 * h); x.lineTo(cx + w * .35, cy - 22 * h); x.lineTo(cx + w * .7, cy - 50 * h); x.lineTo(cx + w * .62, cy + 16); x.closePath();
  sh(x, f('#f2b632'), 8, ink);
  x.beginPath(); x.arc(cx, cy - 18 * h, 13 * h, 0, TAU); sh(x, f('#e8413a'), 5, ink);
}
function headwearFront(x, sp, hx, hy, ink, pencil) {
  const f = c => pencil ? CREAM : c;
  if (sp.hair === 'crown') crown(x, hx, hy - HR * .86, HR * 1.05, pencil, ink);
  if (sp.hair === 'sage') { // matted bun + white beard
    x.beginPath(); x.ellipse(hx, hy - HR - 24, 46, 40, 0, 0, TAU); sh(x, f('#efe9dc'), 8, ink);
    x.beginPath(); x.moveTo(hx - 70, hy + 30); x.quadraticCurveTo(hx - 70, hy + 190, hx, hy + 200); x.quadraticCurveTo(hx + 70, hy + 190, hx + 70, hy + 30); x.quadraticCurveTo(hx, hy + 80, hx - 70, hy + 30); sh(x, f('#f4f0e6'), 8, ink);
  }
  if (sp.hair === 'sita' || sp.hair === 'long') { x.beginPath(); x.moveTo(hx - HR, hy - 4); x.quadraticCurveTo(hx - HR * .9, hy - HR * 1.05, hx, hy - HR); x.quadraticCurveTo(hx + HR * .9, hy - HR * 1.05, hx + HR, hy - 4); x.quadraticCurveTo(hx + 20, hy - HR * .55, hx - HR, hy - 4); sh(x, f('#2b1d18'), 8, ink); }
  if (sp.hair === 'sita') { x.beginPath(); x.arc(hx, hy - 42, 8, 0, TAU); x.fillStyle = f('#e8413a'); x.fill(); x.beginPath(); x.arc(hx + 92, hy - 72, 16, 0, TAU); sh(x, f('#fff2f6'), 5, ink); }
  if (sp.hair === 'boy') { x.beginPath(); x.moveTo(hx - HR, hy - 10); x.quadraticCurveTo(hx - HR, hy - HR * 1.1, hx, hy - HR * 1.05); x.quadraticCurveTo(hx + HR, hy - HR * 1.1, hx + HR, hy - 10); x.quadraticCurveTo(hx, hy - HR * .5, hx - HR, hy - 10); sh(x, f('#2b1d18'), 8, ink); x.beginPath(); x.ellipse(hx, hy - HR - 14, 26, 22, 0, 0, TAU); sh(x, f('#2b1d18'), 7, ink); }
  if (sp.hair === 'king') {
    x.beginPath(); x.moveTo(hx - 70, hy + 30); x.quadraticCurveTo(hx - 70, hy + 170, hx, hy + 180); x.quadraticCurveTo(hx + 70, hy + 170, hx + 70, hy + 30); x.quadraticCurveTo(hx, hy + 80, hx - 70, hy + 30); sh(x, f(sp.beard || '#f4f0e6'), 8, ink);
    crown(x, hx, hy - HR * .86, HR * 1.05, pencil, ink);
  }
  if (sp.hair === 'wild') { const R = mulberry(7); x.lineCap = 'round'; for (let i = 0; i < 9; i++) { const a = -Math.PI * (.1 + .8 * i / 8); x.beginPath(); x.moveTo(hx + Math.cos(a) * HR * .8, hy + Math.sin(a) * HR * .8); x.lineTo(hx + Math.cos(a) * HR * (1.5 + R() * .3), hy + Math.sin(a) * HR * (1.5 + R() * .3)); x.lineWidth = 26; x.strokeStyle = ink; x.stroke(); x.lineWidth = 12; x.strokeStyle = f(sp.hairCol || '#4a2a5a'); x.stroke(); } for (const s2 of [-1, 1]) { x.beginPath(); x.moveTo(hx + s2 * 30, hy - HR * .9); x.lineTo(hx + s2 * 50, hy - HR * 1.35); x.lineTo(hx + s2 * 62, hy - HR * .8); x.closePath(); sh(x, f('#fff6e0'), 6, ink); } }
  if (sp.hair === 'bun') { x.beginPath(); x.arc(hx, hy - HR - 10, 34, 0, TAU); sh(x, f(sp.hairCol || '#d8d4cc'), 7, ink); x.beginPath(); x.moveTo(hx - HR, hy - 4); x.quadraticCurveTo(hx, hy - HR * 1.3, hx + HR, hy - 4); x.quadraticCurveTo(hx, hy - HR * .6, hx - HR, hy - 4); sh(x, f(sp.hairCol || '#d8d4cc'), 7, ink); }
  if (sp.hair === 'turban') { x.beginPath(); x.ellipse(hx, hy - HR * .62, HR * 1.04, HR * .5, 0, Math.PI, TAU); x.lineTo(hx + HR, hy - HR * .5); x.closePath(); sh(x, f(sp.turban || '#c0623a'), 8, ink); }
}
function face(x, sp, p, hx, hy, ink) {
  const d = p.dir ?? 0, lk = p.look ?? [0, 0], fx = hx + d * 30, eyes = p.eyes ?? 'open', blink = p.blink ?? 0;
  if (sp.monkey) { x.beginPath(); x.ellipse(fx, hy + 34, 62, 48, 0, 0, TAU); x.fillStyle = sp.pencil ? CREAM : (sp.muzzle || '#f6d3a2'); x.fill(); x.lineWidth = 5; x.strokeStyle = ink; x.stroke(); }
  for (const s of [-1, 1]) {
    const ex = fx + s * 34, ey = hy - 8;
    if (eyes === 'happy') { x.beginPath(); x.moveTo(ex - 15, ey + 4); x.quadraticCurveTo(ex, ey - 20, ex + 15, ey + 4); x.lineWidth = 8; x.strokeStyle = ink; x.lineCap = 'round'; x.stroke(); continue; }
    if (eyes === 'closed' || blink > .8) { x.beginPath(); x.moveTo(ex - 14, ey); x.quadraticCurveTo(ex, ey + 9, ex + 14, ey); x.lineWidth = 7; x.strokeStyle = ink; x.lineCap = 'round'; x.stroke(); continue; }
    const big = eyes === 'wide' ? 1.25 : 1, ry = 22 * big * (1 - blink * .9);
    x.beginPath(); x.ellipse(ex + lk[0] * 8, ey + lk[1] * 7, 12 * big, ry, 0, 0, TAU); x.fillStyle = ink; x.fill();
    if (ry > 9) { x.beginPath(); x.arc(ex + lk[0] * 8 - 4, ey + lk[1] * 7 - ry * .45, 4.5 * big, 0, TAU); x.fillStyle = '#fff'; x.fill(); }
  }
  if (sp.fangs && (p.mouth ?? 'smile') !== 'roar') for (const s2 of [-1, 1]) { x.beginPath(); x.moveTo(fx + s2 * 16, hy + 46); x.lineTo(fx + s2 * 10, hy + 64); x.lineTo(fx + s2 * 4, hy + 46); x.closePath(); sh(x, '#fff', 3, ink); }
  if (sp.brows === 'angry' || p.brows === 'angry') { x.lineWidth = 8; x.strokeStyle = ink; x.lineCap = 'round'; for (const s of [-1, 1]) { x.beginPath(); x.moveTo(fx + s * 54, hy - 44); x.lineTo(fx + s * 16, hy - 32); x.stroke(); } }
  if (!sp.monkey && !sp.pencil) { x.fillStyle = 'rgba(240,110,110,.35)'; for (const s of [-1, 1]) { x.beginPath(); x.ellipse(fx + s * 60, hy + 26, 18, 11, 0, 0, TAU); x.fill(); } }
  const m = p.mouth ?? 'smile', mx = fx, my = hy + 44;
  x.lineCap = 'round'; x.strokeStyle = ink; x.lineWidth = 7;
  if (m === 'smile') { x.beginPath(); x.moveTo(mx - 20, my - 4); x.quadraticCurveTo(mx, my + 16, mx + 20, my - 4); x.stroke(); }
  else if (m === 'sad') { x.beginPath(); x.moveTo(mx - 18, my + 8); x.quadraticCurveTo(mx, my - 8, mx + 18, my + 8); x.stroke(); }
  else if (m === 'line') { x.beginPath(); x.moveTo(mx - 16, my + 2); x.lineTo(mx + 16, my); x.stroke(); }
  else if (m === 'grin') { x.beginPath(); x.moveTo(mx - 30, my - 8); x.lineTo(mx + 30, my - 8); x.quadraticCurveTo(mx, my + 30, mx - 30, my - 8); sh(x, '#fff', 6, ink); }
  else if (m === 'roar') { x.beginPath(); x.ellipse(mx, my + 8, 30, 24, 0, 0, TAU); sh(x, '#8a2a2a', 6, ink); for (const s2 of [-1, 1]) { x.beginPath(); x.moveTo(mx + s2 * 18, my - 12); x.lineTo(mx + s2 * 10, my + 6); x.lineTo(mx + s2 * 4, my - 12); x.closePath(); sh(x, '#fff', 3, ink); } }
  else { const h = m === 'o' ? 14 : m === 'sing' ? 18 : 20; x.beginPath(); x.ellipse(mx, my + 4, m === 'o' ? 11 : 16, h, 0, 0, TAU); sh(x, '#8a2a2a', 6, ink); }
}

// ---------- the stick figure ----------
export function drawStick(out, sp, p = {}) {
  const ink = sp.pencil ? PENCIL : INK, f = c => sp.pencil ? CREAM : c;
  const W = cv(SW, SH), x = W.getContext('2d');
  const walk = p.walk ?? 0, stride = p.stride ?? 0, sit = p.sit ?? 0;
  x.save(); x.translate(CX, FOOT); x.rotate(p.lean ?? 0); x.translate(-CX, -FOOT);
  // tail (monkeys), behind everything
  if (sp.monkey && !sp.bear) { x.beginPath(); x.moveTo(CX + 10, HIP - 10); x.bezierCurveTo(CX + 220, HIP + 60, CX + 300, HIP - 260, CX + 200, HIP - 330); x.lineWidth = 24; x.strokeStyle = ink; x.lineCap = 'round'; x.stroke(); x.lineWidth = 12; x.strokeStyle = f(sp.skin); x.stroke(); }
  const hy = HEAD_Y + (sit ? 120 : 0), hipY = HIP + (sit ? 120 : 0), neckY = NECK + (sit ? 120 : 0);
  headwearBack(x, sp, CX, hy, ink, sp.pencil);
  // legs
  const legW = 24, l1 = 175, l2 = 170;
  if (sit) { // cross-legged
    x.beginPath(); x.moveTo(CX - 20, hipY); x.quadraticCurveTo(CX - 150, hipY + 40, CX - 160, hipY + 120); x.lineTo(CX + 60, hipY + 150);
    x.moveTo(CX + 20, hipY); x.quadraticCurveTo(CX + 150, hipY + 40, CX + 160, hipY + 120); x.lineTo(CX - 60, hipY + 150);
    x.lineWidth = legW; x.strokeStyle = ink; x.lineCap = 'round'; x.lineJoin = 'round'; x.stroke();
  } else for (const s of [-1, 1]) {
    const sw = Math.sin(walk) * .5 * stride * s, knee = Math.max(0, -Math.sin(walk) * s) * .7 * stride;
    const [fx2, fy2] = limb(x, CX + s * 18, hipY, s * .1 + sw, l1, -knee * .9 * (sw > 0 ? 1 : 1) + 0, l2, legW, ink);
    x.beginPath(); x.ellipse(fx2 + (p.dir ?? 0) * 18 + s * 8, fy2 + 6, 30, 13, 0, 0, TAU); x.fillStyle = ink; x.fill();
  }
  // lower garment
  const dh = () => {
    if (sp.dress === 'sari') { x.beginPath(); x.moveTo(CX - 70, neckY + 30); x.lineTo(CX + 70, neckY + 30); x.quadraticCurveTo(CX + 150, hipY + 200, CX + 150, sit ? hipY + 150 : FOOT - 40); x.lineTo(CX - 150, sit ? hipY + 150 : FOOT - 40); x.quadraticCurveTo(CX - 150, hipY + 200, CX - 70, neckY + 30); x.closePath(); }
    else if (sp.dress === 'robe') { x.beginPath(); x.moveTo(CX - 60, neckY + 20); x.lineTo(CX + 60, neckY + 20); x.lineTo(CX + 130, sit ? hipY + 140 : FOOT - 70); x.lineTo(CX - 130, sit ? hipY + 140 : FOOT - 70); x.closePath(); }
    else { x.beginPath(); x.moveTo(CX - 64, hipY - 20); x.lineTo(CX + 64, hipY - 20); x.lineTo(CX + 92, hipY + 150); x.quadraticCurveTo(CX, hipY + 175, CX - 92, hipY + 150); x.closePath(); }
  };
  if (sp.dress) { const col = f(sp.dressCol); crescent(x, dh, sp.pencil ? CREAM : shade(sp.dressCol), 26, 0, col); dh(); sh(x, null, 8, ink); }
  // torso
  if (sp.dress !== 'sari' && sp.dress !== 'robe') { x.beginPath(); x.moveTo(CX, neckY); x.lineTo(CX, hipY - 10); x.lineWidth = 26; x.strokeStyle = ink; x.lineCap = 'round'; x.stroke(); }
  if (sp.sash) { x.beginPath(); x.moveTo(CX - 60, neckY + 10); x.lineTo(CX - 28, neckY - 6); x.lineTo(CX + 70, hipY - 40); x.lineTo(CX + 40, hipY - 18); x.closePath(); sh(x, f(sp.sash), 7, ink); }
  if (sp.dress === 'sari') { x.beginPath(); x.moveTo(CX + 64, neckY + 26); x.quadraticCurveTo(CX - 20, neckY + 120, CX - 130, hipY + 60); x.lineWidth = 18; x.strokeStyle = f(sp.pallu || '#f2b632'); x.stroke(); }
  // arms
  const shY = neckY + 22;
  for (const s of [-1, 1]) {
    const a = (s < 0 ? p.armL : p.armR) ?? .2, e = (s < 0 ? p.elbowL : p.elbowR) ?? .15;
    const [hx2, hy2, ang] = limb(x, CX + s * 22, shY, s * a, 150, s * e, 138, 22, ink);
    x.beginPath(); x.arc(hx2, hy2, 18, 0, TAU); sh(x, f(sp.skin), 6, ink);
    const hold = s > 0 ? p.holdR ?? sp.holdR : p.holdL ?? sp.holdL;
    if (hold) { x.save(); x.translate(hx2, hy2); x.rotate(-ang); heldProp(x, hold, ink, sp.pencil); x.restore(); }
  }
  // head
  const hd = () => { x.beginPath(); x.arc(CX, hy, HR, 0, TAU); };
  if (sp.pencil) { hd(); x.fillStyle = CREAM; x.fill(); } else { crescent(x, hd, shade(sp.skin), 18, 14, sp.skin); }
  hd(); sh(x, null, 9, ink);
  face(x, sp, p, CX, hy, ink);
  headwearFront(x, sp, CX, hy, ink, sp.pencil);
  x.restore();
  const o = out.getContext('2d'); o.clearRect(0, 0, SW, SH);
  o.drawImage(finishCut(W, 16, { grainA: .7, paper: sp.pencil ? '#fbf8ef' : '#fffdf7' }), 0, 0);
}
export function shade(hex) { const n = parseInt(hex.slice(1), 16), r = n >> 16, g = n >> 8 & 255, b = n & 255, f = .8; return `rgb(${r * f | 0},${g * f | 0},${b * f | 0})`; }

export const CAST = {
  valmikiG: { pencil: true, skin: '#f2c79a', hair: 'sage', dress: 'robe', dressCol: '#e0a24a' },
  hunterG: { pencil: true, skin: '#c98a5a', hair: 'turban', dress: 'dhoti', dressCol: '#8a6a4a', holdR: 'bow' },
  valmiki: { skin: '#f2c79a', hair: 'sage', dress: 'robe', dressCol: '#e0a24a' },
  rama: { skin: '#5b8de0', hair: 'crown', dress: 'dhoti', dressCol: '#f2b632', sash: '#e8413a', holdL: 'bow' },
  ramaKing: { skin: '#5b8de0', hair: 'crown', dress: 'robe', dressCol: '#f2b632' },
  sita: { skin: '#f2c79a', hair: 'sita', dress: 'sari', dressCol: '#e8413a', pallu: '#f2b632' },
  lakshmana: { skin: '#f0c08a', hair: 'boy', dress: 'dhoti', dressCol: '#ffd766', sash: '#3fa1de', holdL: 'bow' },
  kaikeyi: { skin: '#f0c08a', hair: 'veil', veil: '#8a4fc0', dress: 'sari', dressCol: '#b36ad8', pallu: '#f2b632', brows: 'angry' },
  bharata: { skin: '#f0c08a', hair: 'boy', dress: 'dhoti', dressCol: '#5cbf4a', sash: '#f2b632' },
  ravana: { skin: '#5f8a6a', hair: 'crown', heads: true, dress: 'robe', dressCol: '#3a3f6a', brows: 'angry' },
  hanuman: { skin: '#f08a2e', muzzle: '#ffd9a0', monkey: true, dress: 'dhoti', dressCol: '#e8413a', holdR: 'mace' },
  sugriva: { skin: '#b5814a', muzzle: '#f2d2a0', monkey: true, hair: 'crown', dress: 'dhoti', dressCol: '#3fa1de' },
  kid1: { skin: '#f0c08a', hair: 'boy', dress: 'dhoti', dressCol: '#ffd766' },
  kid2: { skin: '#f0c08a', hair: 'boy', dress: 'dhoti', dressCol: '#7fc3e8' },
  naradaG: { pencil: true, skin: '#f2c79a', hair: 'sage', dress: 'robe', dressCol: '#f6f0e1', holdR: 'veena' },
  samudra: { skin: '#3fa1d0', hair: 'crown', dress: 'robe', dressCol: '#2f8ab8' },
  agni: { skin: '#ff8a3a', hair: 'wild', hairCol: '#ffd23f', dress: 'dhoti', dressCol: '#e8413a' },
  sushena: { skin: '#c48a4a', muzzle: '#f6d8a8', monkey: true, hair: 'sage', dress: 'dhoti', dressCol: '#f6f0e1' },
  tara: { skin: '#c9905a', muzzle: '#f6dcb0', monkey: true, hair: 'veil', veil: '#e8413a', dress: 'sari', dressCol: '#ff9a2e', pallu: '#ffd23f' },
  kabandha: { skin: '#5a4a6a', hair: 'wild', hairCol: '#2a1a2a', dress: 'dhoti', dressCol: '#3a2a2a', brows: 'angry', fangs: true },
  mandodari: { skin: '#7a9a7a', hair: 'veil', veil: '#3a3f6a', dress: 'sari', dressCol: '#5a4a9a', pallu: '#f2b632' },
  youth: { skin: '#e8b48a', hair: 'boy', dress: 'dhoti', dressCol: '#f6f0e1', sash: '#c9a06a' },
  narada: { skin: '#f2c79a', hair: 'sage', dress: 'robe', dressCol: '#f6f0e1', holdR: 'veena' },
  dasharatha: { skin: '#f0c08a', hair: 'king', dress: 'robe', dressCol: '#c0392b' },
  kausalya: { skin: '#f0c08a', hair: 'veil', veil: '#f2b632', dress: 'sari', dressCol: '#f29a1a', pallu: '#e8413a' },
  sumitra: { skin: '#f0c08a', hair: 'veil', veil: '#5cbf4a', dress: 'sari', dressCol: '#3fa1de', pallu: '#ffd23f' },
  kaikeyiQ: { skin: '#f0c08a', hair: 'veil', veil: '#8a4fc0', dress: 'sari', dressCol: '#b36ad8', pallu: '#f2b632' },
  shatrughna: { skin: '#f0c08a', hair: 'boy', dress: 'dhoti', dressCol: '#ff9ec1', sash: '#5cbf4a' },
  vishwamitra: { skin: '#e8b48a', hair: 'sage', dress: 'robe', dressCol: '#c0623a' },
  tataka: { skin: '#6a8a3a', hair: 'wild', hairCol: '#3a2a1a', dress: 'dhoti', dressCol: '#5a2a1a', brows: 'angry', fangs: true },
  ahalya: { skin: '#f2c79a', hair: 'long', dress: 'sari', dressCol: '#f6f0e1', pallu: '#d8b4ff' },
  janaka: { skin: '#f0c08a', hair: 'king', beard: '#e8e2d6', dress: 'robe', dressCol: '#3fa1de' },
  parashurama: { skin: '#e8b48a', hair: 'sage', dress: 'dhoti', dressCol: '#f29a1a', brows: 'angry', holdR: 'axe' },
  manthara: { skin: '#e8b48a', hair: 'bun', dress: 'sari', dressCol: '#7a6a5a', pallu: '#a89a8a' },
  guha: { skin: '#a8683a', hair: 'turban', turban: '#3fa1de', dress: 'dhoti', dressCol: '#f2b632' },
  bharataSage: { skin: '#f0c08a', hair: 'boy', dress: 'robe', dressCol: '#c9a06a' },
  ramaSage: { skin: '#5b8de0', hair: 'boy', dress: 'dhoti', dressCol: '#c9a06a', holdL: 'bow' },
  lakshmanaSage: { skin: '#f0c08a', hair: 'boy', dress: 'dhoti', dressCol: '#c9a06a', sash: '#8a6a3a', holdL: 'bow' },
  sitaSage: { skin: '#f2c79a', hair: 'sita', dress: 'sari', dressCol: '#e8b860', pallu: '#c98a3a' },
  shurpanakha: { skin: '#8a6ab8', hair: 'wild', hairCol: '#2a1a3a', dress: 'sari', dressCol: '#e8413a', pallu: '#3a2a6a', fangs: true },
  khara: { skin: '#8a3a3a', hair: 'wild', hairCol: '#1a1a1a', dress: 'dhoti', dressCol: '#2a2a3a', brows: 'angry', fangs: true },
  maricha: { skin: '#6a5a8a', hair: 'wild', hairCol: '#1a1a2a', dress: 'dhoti', dressCol: '#3a3a5a', fangs: true },
  ravanaSage: { skin: '#e8b48a', hair: 'sage', dress: 'robe', dressCol: '#c0623a', brows: 'angry' },
  shabari: { skin: '#c98a5a', hair: 'bun', dress: 'sari', dressCol: '#f6f0e1', pallu: '#c9a06a' },
  vali: { skin: '#8a5a2a', muzzle: '#e8c890', monkey: true, hair: 'crown', dress: 'dhoti', dressCol: '#e8413a', holdR: 'mace' },
  angada: { skin: '#c9905a', muzzle: '#f6dcb0', monkey: true, dress: 'dhoti', dressCol: '#5cbf4a' },
  jambavan: { skin: '#4a3428', muzzle: '#c9a07a', monkey: true, bear: true, hair: 'sage', dress: 'dhoti', dressCol: '#f2b632' },
  nala: { skin: '#d8a060', muzzle: '#fbe4c0', monkey: true, dress: 'dhoti', dressCol: '#3fa1de' },
  monkeyA: { skin: '#c48a4a', muzzle: '#f6d8a8', monkey: true, dress: 'dhoti', dressCol: '#ff9a2e' },
  monkeyB: { skin: '#a8743a', muzzle: '#f2d0a0', monkey: true, dress: 'dhoti', dressCol: '#b36ad8' },
  vibhishana: { skin: '#5f8a6a', hair: 'crown', dress: 'robe', dressCol: '#f6f0e1' },
  kumbhakarna: { skin: '#4a6a5a', hair: 'wild', hairCol: '#1a2a1a', dress: 'dhoti', dressCol: '#a8582a', fangs: true },
  indrajit: { skin: '#5f7a8a', hair: 'crown', dress: 'dhoti', dressCol: '#2a2a5a', sash: '#e8413a', holdL: 'bow', brows: 'angry' },
  ramaCrowned: { skin: '#5b8de0', hair: 'crown', dress: 'robe', dressCol: '#f2b632' },
  sitaQueen: { skin: '#f2c79a', hair: 'sita', dress: 'sari', dressCol: '#e8413a', pallu: '#f2b632' },
  bhumi: { skin: '#a8743a', hair: 'long', dress: 'sari', dressCol: '#5cbf4a', pallu: '#f2b632' },
  citizenA: { skin: '#f0c08a', hair: 'turban', turban: '#e8413a', dress: 'dhoti', dressCol: '#ffd23f' },
  citizenB: { skin: '#e8b48a', hair: 'veil', veil: '#ff7aa8', dress: 'sari', dressCol: '#3fa1de', pallu: '#ffd23f' },
  citizenC: { skin: '#d8a070', hair: 'turban', turban: '#5cbf4a', dress: 'dhoti', dressCol: '#f6f0e1' },
  sage2: { skin: '#e8b48a', hair: 'sage', dress: 'robe', dressCol: '#e8c860' },
  baby: { skin: '#f0c08a', hair: 'boy', dress: 'dhoti', dressCol: '#fff6e0' },
  babyBlue: { skin: '#5b8de0', hair: 'boy', dress: 'dhoti', dressCol: '#ffd766' },
};

// a posable card: front art + paper back, cut-out shadow, blob contact shadow
export function makeStick(sp, H = .045) {
  const c = cv(SW, SH); drawStick(c, sp, {});
  const tex = texOf(c), m = mats(tex);
  const h = H * SH / 860, w = h * SW / SH, ay = FOOT / SH;
  const geo = new THREE.PlaneGeometry(w, h); geo.translate(0, ay * h - h / 2, 0);
  const front = new THREE.Mesh(geo, m.front), back = new THREE.Mesh(geo, m.back);
  front.castShadow = true; front.customDepthMaterial = m.depth; front.receiveShadow = back.receiveShadow = true;
  const body = new THREE.Group(); body.add(front, back);
  const root = new THREE.Group(); root.add(body);
  const shadow = blobShadow(H * .3, .45);
  let key = '';
  return {
    root, body, shadow, H, sp,
    pose(p) {
      const k = JSON.stringify(p, (kk, v) => typeof v === 'number' ? Math.round(v * 24) / 24 : v);
      if (k === key) return; key = k; drawStick(c, sp, p); tex.needsUpdate = true;
    },
    head(v = new THREE.Vector3()) { return v.set(0, (FOOT - HEAD_Y + HR) / SH * h, 0).applyMatrix4(body.matrixWorld); },
  };
}
