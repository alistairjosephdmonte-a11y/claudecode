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
  } else if (kind === 'fry') { /* unused */ }
}

// ---------- heads & headwear ----------
function headwearBack(x, sp, hx, hy, ink, pencil) {
  const f = c => pencil ? CREAM : c;
  if (sp.hair === 'sita' || sp.hair === 'long') { blob(x, hx, hy + 30, HR * 1.12, HR * 1.25, .04, 3); sh(x, f('#2b1d18'), 8, ink); }
  if (sp.hair === 'sita') { x.beginPath(); x.arc(hx + 70, hy - 70, 48, 0, TAU); sh(x, f('#2b1d18'), 8, ink); }
  if (sp.hair === 'veil') { x.beginPath(); x.moveTo(hx - 130, hy + 200); x.quadraticCurveTo(hx - 140, hy - 140, hx, hy - 128); x.quadraticCurveTo(hx + 140, hy - 140, hx + 130, hy + 200); x.closePath(); sh(x, f(sp.veil || '#8a4fc0'), 9, ink); }
  if (sp.monkey) for (const s of [-1, 1]) { x.beginPath(); x.arc(hx + s * 98, hy - 6, 34, 0, TAU); sh(x, f(sp.skin), 8, ink); x.beginPath(); x.arc(hx + s * 98, hy - 6, 17, 0, TAU); x.fillStyle = f(sp.muzzle || '#f6d3a2'); x.fill(); }
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
  if (sp.brows === 'angry' || p.brows === 'angry') { x.lineWidth = 8; x.strokeStyle = ink; x.lineCap = 'round'; for (const s of [-1, 1]) { x.beginPath(); x.moveTo(fx + s * 54, hy - 44); x.lineTo(fx + s * 16, hy - 32); x.stroke(); } }
  if (!sp.monkey && !sp.pencil) { x.fillStyle = 'rgba(240,110,110,.35)'; for (const s of [-1, 1]) { x.beginPath(); x.ellipse(fx + s * 60, hy + 26, 18, 11, 0, 0, TAU); x.fill(); } }
  const m = p.mouth ?? 'smile', mx = fx, my = hy + 44;
  x.lineCap = 'round'; x.strokeStyle = ink; x.lineWidth = 7;
  if (m === 'smile') { x.beginPath(); x.moveTo(mx - 20, my - 4); x.quadraticCurveTo(mx, my + 16, mx + 20, my - 4); x.stroke(); }
  else if (m === 'sad') { x.beginPath(); x.moveTo(mx - 18, my + 8); x.quadraticCurveTo(mx, my - 8, mx + 18, my + 8); x.stroke(); }
  else if (m === 'line') { x.beginPath(); x.moveTo(mx - 16, my + 2); x.lineTo(mx + 16, my); x.stroke(); }
  else if (m === 'grin') { x.beginPath(); x.moveTo(mx - 30, my - 8); x.lineTo(mx + 30, my - 8); x.quadraticCurveTo(mx, my + 30, mx - 30, my - 8); sh(x, '#fff', 6, ink); }
  else { const h = m === 'o' ? 14 : m === 'sing' ? 18 : 20; x.beginPath(); x.ellipse(mx, my + 4, m === 'o' ? 11 : 16, h, 0, 0, TAU); sh(x, '#8a2a2a', 6, ink); }
}

// ---------- the stick figure ----------
export function drawStick(out, sp, p = {}) {
  const ink = sp.pencil ? PENCIL : INK, f = c => sp.pencil ? CREAM : c;
  const W = cv(SW, SH), x = W.getContext('2d');
  const walk = p.walk ?? 0, stride = p.stride ?? 0, sit = p.sit ?? 0;
  x.save(); x.translate(CX, FOOT); x.rotate(p.lean ?? 0); x.translate(-CX, -FOOT);
  // tail (monkeys), behind everything
  if (sp.monkey) { x.beginPath(); x.moveTo(CX + 10, HIP - 10); x.bezierCurveTo(CX + 220, HIP + 60, CX + 300, HIP - 260, CX + 200, HIP - 330); x.lineWidth = 24; x.strokeStyle = ink; x.lineCap = 'round'; x.stroke(); x.lineWidth = 12; x.strokeStyle = f(sp.skin); x.stroke(); }
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
