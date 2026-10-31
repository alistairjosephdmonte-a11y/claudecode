// The investigation table and everything that lives on it. One world, fixed geography: every set has a permanent place
// on the table, so the closing crane (shot 46) shows the whole case at once. Units: 1 = 10 cm of table.
import * as THREE from 'three';
import { mulberry, clamp, lerp } from '/core/lib.js';

export const PAL = { black: '#111418', ivory: '#E8E3D8', red: '#C5534E', blue: '#254F91', yellow: '#E8BC43', nred: '#C52232', grey: '#77828B', ink: '#23262b' };
export const ZONE = {   // set centres on the table (x, z)
  dallas: [-21, -10], plaza: [-9, -14], board: [-9, -5], docs: [5, -6], felt: [5, -15], store: [19, -10], plan: [20, 3],
  mail: [-20, 7], desk: [-8, 9], charts: [6, 9], net: [20, 13],
};
const TL = new THREE.TextureLoader();
const tex = (src, rep = 1, srgb = false) => { const t = TL.load(src); t.wrapS = t.wrapT = THREE.RepeatWrapping; t.repeat.set(rep, rep); t.anisotropy = 8; if (srgb) t.colorSpace = THREE.SRGBColorSpace; return t; };

// —— canvas textures ——
export function canvas(w, h) { const c = document.createElement('canvas'); c.width = w; c.height = h; return [c, c.getContext('2d')]; }
export function ctex(c) { const t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace; t.anisotropy = 8; return t; }
// paper: ivory base, long fibres, faint mottling, a slightly darker edge
export function paperBase(g, w, h, seed = 1, base = PAL.ivory) {
  const R = mulberry(seed); g.fillStyle = base; g.fillRect(0, 0, w, h);
  for (let i = 0; i < w * h / 900; i++) { const x = R() * w, y = R() * h, a = R() * 6.28, l = 3 + R() * 14; g.strokeStyle = `rgba(${R() < .5 ? '90,80,60' : '255,255,250'},${.04 + R() * .06})`; g.lineWidth = .6 + R() * .6; g.beginPath(); g.moveTo(x, y); g.lineTo(x + Math.cos(a) * l, y + Math.sin(a) * l); g.stroke(); }
  for (let i = 0; i < 40; i++) { const x = R() * w, y = R() * h, r = 40 + R() * 160, gr = g.createRadialGradient(x, y, 0, x, y, r); gr.addColorStop(0, `rgba(120,100,70,${R() * .035})`); gr.addColorStop(1, 'rgba(120,100,70,0)'); g.fillStyle = gr; g.fillRect(x - r, y - r, 2 * r, 2 * r); }
  const e = Math.min(w, h) * .03, gr = (x0, y0, x1, y1) => { const q = g.createLinearGradient(x0, y0, x1, y1); q.addColorStop(0, 'rgba(110,90,60,.16)'); q.addColorStop(1, 'rgba(110,90,60,0)'); return q; };
  g.fillStyle = gr(0, 0, e, 0); g.fillRect(0, 0, e, h); g.fillStyle = gr(w, 0, w - e, 0); g.fillRect(w - e, 0, e, h); g.fillStyle = gr(0, 0, 0, e); g.fillRect(0, 0, w, e); g.fillStyle = gr(0, h, 0, h - e); g.fillRect(0, h - e, w, e);
}
// word-wrapped text; returns the y after the block
export function wrap(g, text, x, y, maxW, lh) {
  const words = text.split(' '); let line = '';
  for (const w of words) { const tst = line ? line + ' ' + w : w; if (g.measureText(tst).width > maxW && line) { g.fillText(line, x, y); y += lh; line = w; } else line = tst; }
  if (line) { g.fillText(line, x, y); y += lh; } return y;
}

// a sheet of paper (or card) with real thickness, a gentle curl and a drawn face. draw(g, W, H) paints the face.
export function sheet(w, h, draw, o = {}) {
  const ppu = o.ppu || 140, W = Math.min(4096, Math.round(w * ppu)), H = Math.min(4096, Math.round(h * ppu));
  const [c, g] = canvas(W, H); (o.base === false ? null : paperBase(g, W, H, o.seed || 1, o.color || PAL.ivory)); draw && draw(g, W, H);
  const geo = new THREE.BoxGeometry(w, o.thick || .012, h, 24, 1, 16), p = geo.attributes.position, curl = o.curl ?? .05;
  for (let i = 0; i < p.count; i++) { const x = p.getX(i) / (w / 2), z = p.getZ(i) / (h / 2); p.setY(i, p.getY(i) + curl * (x * x * .6 + Math.pow(Math.abs(z), 3) * .5) * Math.min(w, h) * .12); }
  geo.computeVertexNormals();
  const face = new THREE.MeshLambertMaterial({ map: ctex(c)});
  const edge = new THREE.MeshLambertMaterial({ color: o.edge || '#d9d2c2'});
  const m = new THREE.Mesh(geo, [edge, edge, face, edge, edge, edge]); m.castShadow = m.receiveShadow = true; m.userData.canvas = c; m.userData.g = g; m.userData.tex = face.map;
  return m;
}

// —— materials ——
export const M = {};
export function materials() {
  const base = '/core/assets/polyhaven/';
  M.walnut = new THREE.MeshLambertMaterial({ map: tex(base + 'walnut_diff.jpg', 6, true), normalMap: tex(base + 'walnut_nor.jpg', 6), color: '#6b5a4c' });
  M.felt = new THREE.MeshLambertMaterial({ color: '#15181c'});
  M.board = new THREE.MeshLambertMaterial({ color: '#d8d2c4'});          // model-making board (white card)
  M.card = new THREE.MeshLambertMaterial({ color: '#c9bfa9'});           // greyboard
  M.figure = new THREE.MeshLambertMaterial({ color: '#cfc9bd'});          // anonymous scale figures
  M.figureDark = new THREE.MeshLambertMaterial({ color: '#4c535b'});
  M.glass = new THREE.MeshPhysicalMaterial({ color: '#9fb4c2', roughness: .05, metalness: 0, transmission: 0, transparent: true, opacity: .32, reflectivity: .6 });
  M.asphalt = new THREE.MeshLambertMaterial({ color: '#2b2d31'});
  M.concrete = new THREE.MeshLambertMaterial({ color: '#a7a39b'});
  M.metal = new THREE.MeshStandardMaterial({ color: '#8d9399', roughness: .45, metalness: .7 });
  M.dark = new THREE.MeshLambertMaterial({ color: '#202327'});
  M.blue = new THREE.MeshLambertMaterial({ color: PAL.blue});
  M.yellow = new THREE.MeshLambertMaterial({ color: PAL.yellow});
  M.red = new THREE.MeshLambertMaterial({ color: PAL.red});
  M.nred = new THREE.MeshLambertMaterial({ color: PAL.nred});
  M.wood = new THREE.MeshLambertMaterial({ map: tex(base + 'walnut_diff.jpg', 1, true), color: '#a08060' });
  M.beige = new THREE.MeshLambertMaterial({ color: '#cfc6b0'});
  M.white = new THREE.MeshLambertMaterial({ color: '#efece6'});
  M.disc = new THREE.MeshPhysicalMaterial({ color: '#d8dde2', metalness: 1, roughness: .12, iridescence: 1, iridescenceIOR: 1.6, iridescenceThicknessRange: [200, 600] });
  return M;
}
export function box(w, h, d, mat, x = 0, y = 0, z = 0, parent) { const m = new THREE.Mesh(new THREE.BoxGeometry(w, h, d), mat); m.position.set(x, y + h / 2, z); m.castShadow = mat !== M.glass; m.receiveShadow = true; parent && parent.add(m); return m; }
export function cyl(r, h, mat, x = 0, y = 0, z = 0, parent, seg = 24) { const m = new THREE.Mesh(new THREE.CylinderGeometry(r, r, h, seg), mat); m.position.set(x, y + h / 2, z); m.castShadow = m.receiveShadow = true; parent && parent.add(m); return m; }
// a label printed on a thin card, lying flat or standing
export function label(text, o = {}) {
  const fs = o.size || 120, font = `${o.weight || 600} ${fs}px ${o.font || '"Plex Cond"'}`, [c0, g0] = canvas(8, 8); g0.font = font; g0.letterSpacing = (o.track || 0) + 'px';
  const lines = String(text).split('\n'), tw = Math.max(...lines.map(l => g0.measureText(l).width)), pad = fs * (o.pad ?? .45), W = Math.ceil(tw + pad * 2), H = Math.ceil(fs * 1.25 * lines.length + pad * 1.4);
  const s = sheet(W / (o.ppu || 400), H / (o.ppu || 400), (g, w, h) => { if (o.bg) { g.fillStyle = o.bg; g.fillRect(0, 0, w, h); } g.font = font; g.letterSpacing = (o.track || 0) + 'px'; g.fillStyle = o.col || PAL.ink; g.textBaseline = 'middle'; g.textAlign = 'center'; lines.forEach((l, i) => g.fillText(l, w / 2, h / 2 + (i - (lines.length - 1) / 2) * fs * 1.25)); }, { ppu: o.ppu || 400, curl: 0, base: o.bg ? false : true, seed: o.seed, thick: o.thick || .01 });
  return s;
}

// —— anonymous scale figures (architectural-model people: no faces, no likenesses) ——
export function figure(o = {}) {
  const G = new THREE.Group(), mat = o.mat || M.figure, h = o.h || .5, k = h / 1.75;
  const part = (geo, y) => { const m = new THREE.Mesh(geo, mat); m.position.y = y * k; m.castShadow = true; return m; };
  const legs = [-1, 1].map(s => { const L = new THREE.Group(); L.position.set(s * .1 * k, .92 * k, 0); const m = part(new THREE.CapsuleGeometry(.065 * k, .78 * k, 4, 8), -.43); L.add(m); G.add(L); return L; });
  const torso = part(new THREE.CapsuleGeometry(.17 * k, .42 * k, 4, 12), 1.22); torso.scale.z = .7; G.add(torso);
  const head = part(new THREE.SphereGeometry(.105 * k, 16, 12), 1.62); head.scale.y = 1.15; G.add(head);
  const arms = [-1, 1].map(s => { const A = new THREE.Group(); A.position.set(s * .22 * k, 1.42 * k, 0); const m = part(new THREE.CapsuleGeometry(.05 * k, .58 * k, 4, 8), -.32); A.add(m); G.add(A); return A; });
  G.userData = { legs, arms, k };
  return G;
}
// natural walk: leg swing, counter-swinging arms, a little bob (ph in cycles)
export function walk(F, ph, amt = 1) {
  const s = Math.sin(ph * Math.PI * 2) * .42 * amt, { legs, arms, k } = F.userData;
  legs[0].rotation.x = s; legs[1].rotation.x = -s; arms[0].rotation.x = -s * .7; arms[1].rotation.x = s * .7;
  F.children.forEach(c => { if (c.isMesh) c.position.y = c.userData.y0 ?? (c.userData.y0 = c.position.y); });
  const bob = Math.abs(Math.cos(ph * Math.PI * 2)) * .02 * k * amt; F.children.forEach(c => { if (c.isMesh) c.position.y = c.userData.y0 + bob; });
}
export function pose(F, { arm = [0, 0], leg = [0, 0], sit = 0 } = {}) {
  const { legs, arms } = F.userData; arms[0].rotation.x = arm[0]; arms[1].rotation.x = arm[1]; legs[0].rotation.x = leg[0] - sit * 1.5; legs[1].rotation.x = leg[1] - sit * 1.5;
}

// —— a boxy period sedan ——
export function car(col, R) {
  const G = new THREE.Group(), body = new THREE.MeshLambertMaterial({ color: col});
  box(1.0, .16, .44, body, 0, .07, 0, G); box(.56, .14, .4, body, -.04, .23, 0, G);
  box(.5, .11, .41, M.glass, -.04, .245, 0, G);
  for (const [x, z] of [[.32, .2], [.32, -.2], [-.32, .2], [-.32, -.2]]) { const w = cyl(.07, .06, M.dark, x, 0, z, G, 14); w.rotation.x = Math.PI / 2; w.position.y = .07; }
  return G;
}
