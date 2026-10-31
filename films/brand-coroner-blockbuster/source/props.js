// Evidence objects: source cards, typeset archival excerpts, receipts, mailers, chart blocks, gears.
// Archival wording is only ever text verified against the cited filing; anything else is labelled an editorial summary.
import * as THREE from 'three';
import { mulberry, clamp } from '/core/lib.js';
import { PAL, M, sheet, box, cyl, label, wrap, canvas, ctex } from './world.js';

const SERIF = '"Newsreader"', MONO = '"Plex Mono"', COND = '"Plex Cond"';
function stamp(g, text, x, y, s, col = PAL.red, rot = -.06) {
  g.save(); g.translate(x, y); g.rotate(rot); g.font = `700 ${s}px ${COND}`; g.letterSpacing = s * .08 + 'px'; const w = g.measureText(text).width;
  g.strokeStyle = col; g.lineWidth = s * .09; g.globalAlpha = .85; g.strokeRect(-s * .4, -s * .95, w + s * .8, s * 1.3); g.fillStyle = col; g.fillText(text, 0, 0); g.restore();
}
const head = (g, w, h, tag, idx) => { g.fillStyle = PAL.ink; g.font = `500 ${h * .045}px ${MONO}`; g.letterSpacing = '3px'; g.fillText(tag, w * .06, h * .1); g.textAlign = 'right'; g.fillText(idx, w * .94, h * .1); g.textAlign = 'left'; g.fillRect(w * .06, h * .125, w * .88, 2); };

// a source card: who, what they said, where it was published
export function sourceCard({ idx, name, role, pub, lines, quote, note, seed }) {
  return sheet(2.4, 1.6, (g, w, h) => {
    head(g, w, h, 'SOURCE CARD', idx);
    g.fillStyle = PAL.ink; g.font = `700 ${h * .11}px ${COND}`; g.letterSpacing = '1px'; g.fillText(name.toUpperCase(), w * .06, h * .26);
    g.font = `400 ${h * .05}px ${MONO}`; g.letterSpacing = '0px'; g.fillStyle = '#4a4f57'; g.fillText(role, w * .06, h * .33);
    g.fillStyle = PAL.blue; g.font = `italic 500 ${h * .052}px ${SERIF}`; g.fillText(pub, w * .06, h * .41);
    g.fillStyle = PAL.ink; let y = h * .52;
    if (quote) { g.font = `italic 400 ${h * .056}px ${SERIF}`; y = wrap(g, quote, w * .06, y, w * .86, h * .07); y += h * .02; }
    g.font = `400 ${h * .05}px ${SERIF}`; for (const l of lines || []) { g.fillText('—', w * .06, y); y = wrap(g, l, w * .1, y, w * .82, h * .065); }
    if (note) { g.font = `500 ${h * .038}px ${MONO}`; g.fillStyle = '#6b6f75'; wrap(g, note, w * .06, h * .93, w * .88, h * .045); }
  }, { ppu: 900, seed: seed || 5, curl: .03, thick: .02 });
}
// a typeset excerpt from a filing: masthead, the verified passage, citation, and the archival/typeset disclosure
export function excerpt({ mast, sub, passage, cite, hi, w = 2.6, h = 3.4, seed }) {
  return sheet(w, h, (g, W, H) => {
    g.fillStyle = PAL.ink; g.textAlign = 'center'; g.font = `600 ${H * .019}px ${SERIF}`; g.letterSpacing = '1px';
    mast.forEach((l, i) => g.fillText(l, W / 2, H * (.07 + i * .036)));
    g.font = `700 ${H * .05}px ${SERIF}`; g.letterSpacing = '4px'; g.fillText(sub, W / 2, H * (.11 + mast.length * .036)); g.textAlign = 'left'; g.letterSpacing = '0px';
    let y = H * (.2 + mast.length * .036); g.fillRect(W * .08, y - H * .04, W * .84, 2);
    // dummy body above and below, greyed, so the verified passage reads as an excerpt of a page
    g.fillStyle = 'rgba(40,40,45,.16)'; for (let i = 0; i < 4; i++) g.fillRect(W * .08, y + i * H * .028, W * (i === 3 ? .5 : .84), H * .012); y += H * .14;
    g.font = `400 ${H * .034}px ${SERIF}`; const lh = H * .047, x0 = W * .08;
    if (hi) { g.save(); g.font = `400 ${H * .034}px ${SERIF}`; const yy = y; const tmp = []; const words = passage.split(' '); let line = '', ly = yy; for (const w_ of words) { const t = line ? line + ' ' + w_ : w_; if (g.measureText(t).width > W * .84 && line) { tmp.push([line, ly]); ly += lh; line = w_; } else line = t; } tmp.push([line, ly]);
      g.fillStyle = 'rgba(232,188,67,.42)'; tmp.forEach(([l, ly2]) => g.fillRect(x0 - 6, ly2 - H * .03, g.measureText(l).width + 12, H * .04)); g.restore(); }
    g.fillStyle = PAL.ink; y = wrap(g, passage, x0, y, W * .84, lh) + H * .03;
    g.fillStyle = 'rgba(40,40,45,.16)'; for (let i = 0; i < 6; i++) g.fillRect(W * .08, y + i * H * .028, W * (i === 5 ? .3 : .84), H * .012);
    g.fillStyle = '#5a5f66'; g.font = `500 ${H * .022}px ${MONO}`; wrap(g, cite, W * .08, H * .9, W * .84, H * .028);
    g.fillStyle = PAL.red; g.fillText('TYPESET EXCERPT · WORDING AS FILED', W * .08, H * .965);
  }, { ppu: 700, seed: seed || 7, curl: .04 });
}
// an editorial summary card (not archival wording)
export function summary({ kicker, title, body, cite, w = 2.4, h = 1.7, seed, tagCol = PAL.blue }) {
  return sheet(w, h, (g, W, H) => {
    head(g, W, H, 'EDITORIAL SUMMARY', kicker);
    g.fillStyle = tagCol; let ts = H * .12; g.font = `700 ${ts}px ${COND}`; while (g.measureText(title).width > W * .88) { ts *= .94; g.font = `700 ${ts}px ${COND}`; } g.fillText(title, W * .06, H * .3);
    g.fillStyle = PAL.ink; g.font = `400 ${H * .058}px ${SERIF}`; let y = wrap(g, body, W * .06, H * .43, W * .88, H * .075);
    if (cite) { g.fillStyle = '#5a5f66'; g.font = `500 ${H * .04}px ${MONO}`; wrap(g, cite, W * .06, H * .9, W * .88, H * .048); }
  }, { ppu: 900, seed: seed || 9, curl: .03, thick: .02 });
}
// a big figure on a dark plate (the felt surface)
export function plate(lines, { w = 6, h = 2.6, seed } = {}) {
  return sheet(w, h, (g, W, H) => {
    g.fillStyle = '#16191d'; g.fillRect(0, 0, W, H); const R = mulberry(seed || 3); for (let i = 0; i < 9000; i++) { g.fillStyle = `rgba(255,255,255,${R() * .025})`; g.fillRect(R() * W, R() * H, 2, 2); }
    g.textAlign = 'center'; lines.forEach(([txt, sz, y, col, font, ls]) => { g.font = font || `800 ${H * sz}px "BigShoulders"`; g.letterSpacing = (ls || 0) + 'px'; g.fillStyle = col || PAL.ivory; g.fillText(txt, W / 2, H * y); });
  }, { ppu: 420, base: false, curl: 0, thick: .03, rough: .8 });
}
// a thermal-paper rental receipt; values are illustrative and stamped as such
export function receipt() {
  const L = [['VIDEO RENTAL · STORE 0000', 0], ['', 0], ['NEW RELEASE  1 NIGHT', '3.99'], ['  DUE: FRI 7:00 PM', 0], ['CATALOG  5 NIGHTS', '2.49'], ['  DUE: WED 7:00 PM', 0], ['', 0], ['EXTENDED VIEWING FEE', '3.99'], ['  (RETURNED 1 DAY LATE)', 0], ['', 0], ['TOTAL', '10.47'], ['', 0], ['PLEASE BE KIND', 0]];
  return sheet(.9, 2.6, (g, W, H) => {
    g.fillStyle = '#f2efe8'; g.fillRect(0, 0, W, H); g.fillStyle = '#2a2b2f'; g.font = `500 ${W * .05}px ${MONO}`;
    L.forEach(([a, b], i) => { const y = H * (.08 + i * .055); g.fillText(a, W * .07, y); if (b) { g.textAlign = 'right'; g.fillText(b, W * .93, y); g.textAlign = 'left'; } if (i === 7) { g.fillStyle = 'rgba(197,83,78,.25)'; g.fillRect(W * .05, y - H * .03, W * .9, H * .04); g.fillStyle = '#2a2b2f'; } });
    stamp(g, 'ILLUSTRATIVE VALUES', W * .14, H * .88, W * .085);
  }, { ppu: 900, base: false, curl: .12, thick: .006, rough: .5 });
}
// the DVD and a neutral mailer (no company packaging is recreated)
export function dvd() { const G = new THREE.Group(); const d = new THREE.Mesh(new THREE.CylinderGeometry(.6, .6, .012, 64), M.disc); d.castShadow = true; G.add(d); const hub = cyl(.08, .014, M.white, 0, -.001, 0, G, 32); return G; }
export function mailer() {
  return sheet(1.9, 1.35, (g, W, H) => { g.fillStyle = PAL.nred; g.fillRect(0, 0, W, H); const R = mulberry(4); for (let i = 0; i < 4000; i++) { g.fillStyle = `rgba(0,0,0,${R() * .06})`; g.fillRect(R() * W, R() * H, 3, 1); }
    g.fillStyle = '#f3efe6'; g.fillRect(W * .52, H * .55, W * .38, H * .26); g.fillStyle = '#555'; for (let i = 0; i < 3; i++) g.fillRect(W * .55, H * (.6 + i * .06), W * .3, H * .02);
    g.fillStyle = 'rgba(255,255,255,.88)'; g.font = `600 ${H * .065}px ${MONO}`; g.fillText('DVD BY MAIL', W * .07, H * .16); g.font = `500 ${H * .04}px ${MONO}`; g.fillText('EDITORIAL MAILER · NOT PERIOD PACKAGING', W * .07, H * .9);
  }, { ppu: 700, base: false, curl: .04, thick: .015, rough: .95 });
}
// a solid chart block with a printed label on its front face
export function block(w, h, d, col, text, o = {}) {
  const G = new THREE.Group(), mat = new THREE.MeshLambertMaterial({ color: col}); const b = box(w, h, d, mat, 0, 0, 0, G);
  if (text) { const l = label(text, { size: o.size || 90, col: o.tcol || PAL.ink, bg: o.lbg || PAL.ivory, weight: 700, track: 3, ppu: o.ppu || 300 }); const s = Math.min(1, (w * .92) / l.geometry.parameters.width); l.scale.set(s, 1, s);
    if (o.top) { l.position.set(0, h + .006, 0); G.userData.top = l; } else { l.rotation.x = Math.PI / 2; l.position.set(0, o.ly ?? h / 2, d / 2 + .012); } G.add(l); }
  G.userData.b = b; return G;
}
// an extruded gear
export function gear(r, teeth, col, thick = .3) {
  const s = new THREE.Shape(), n = teeth * 4; for (let i = 0; i <= n; i++) { const a = i / n * Math.PI * 2, k = i % 4, rr = k < 2 ? r : r * .82; const x = Math.cos(a) * rr, y = Math.sin(a) * rr; i ? s.lineTo(x, y) : s.moveTo(x, y); }
  const hole = new THREE.Path(); hole.absarc(0, 0, r * .25, 0, Math.PI * 2, true); s.holes.push(hole);
  const m = new THREE.Mesh(new THREE.ExtrudeGeometry(s, { depth: thick, bevelEnabled: true, bevelSize: .02, bevelThickness: .02, bevelSegments: 2 }), new THREE.MeshStandardMaterial({ color: col, roughness: .5, metalness: .15 }));
  m.rotation.x = -Math.PI / 2; m.castShadow = m.receiveShadow = true; const G = new THREE.Group(); G.add(m); return G;
}
export { label };
