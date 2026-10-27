// Episode 2 worlds, inserts and set pieces (casinos). Violet stays the portal's alone.
import { clamp, lerp, hash, seg, ss, eo, back, TAU } from '/core/lib.js';
import { INK, g, push, pop, translate, rotate, scale, shape, fillOnly, stroke, ell, arc, spline, rr, rect, quad, dot, text, bands, screenRect } from './toon.js';
import { WORLDS, INSERTS, FLOOR } from './worlds.js';
import { curd } from './chars.js';
const sh = (pts, fill, s2, o = {}) => shape(pts, { fill, lw: o.lw ?? 6, shade: s2 ? () => fillOnly(s2[0], s2[1], { boil: .3 }) : undefined });
const floorBand = (col) => { fillOnly(rect(-3000, FLOOR, 8000, 1200), col, { boil: 0 }); stroke([[-3000, FLOOR], [5000, FLOOR]], 6); };
const carpet = (a, b, c) => { fillOnly(rect(-3000, FLOOR, 8000, 1200), a, { boil: 0 }); for (let i = -20; i < 40; i++) for (let j = 0; j < 3; j++) { const x = i * 130 + (j % 2) * 65, y = FLOOR + 30 + j * 70; fillOnly(spline([[x, y - 18], [x + 18, y], [x, y + 18], [x - 18, y]]), (i + j) % 2 ? b : c, { boil: .2 }); } stroke([[-3000, FLOOR], [5000, FLOOR]], 6); };

export function slot(x, y, s = 1, o = {}) {   // a slot machine: cabinet, reel window, lights, lever
  push(); translate(x, y); scale(s);
  sh(rr(-80, -340, 160, 340, 16), o.col ?? '#C0392B', [rect(40, -340, 40, 340), o.dark ?? '#922B21']);
  sh(rr(-62, -310, 124, 70, 10), '#FFE08A', null, { lw: 5 });
  sh(rr(-58, -220, 116, 80, 8), '#FFFFFF', null, { lw: 5 });
  const sp = o.spin ?? 0; for (let k = 0; k < 3; k++) { const sym = Math.floor(sp * 8 + k * 3) % 3; const cx = -38 + k * 38, cy = -180; if (sym === 0) dot(cx, cy, 10, '#E8392B'); else if (sym === 1) shape(rect(cx - 9, cy - 9, 18, 18), { fill: '#2E8B57', lw: 4 }); else shape([[cx, cy - 12], [cx + 11, cy + 9], [cx - 11, cy + 9]], { fill: '#F2C230', lw: 4 }); }
  for (let k = 0; k < 5; k++) dot(-56 + k * 28, -330, 6, (Math.floor((o.t ?? 0) * 6) + k) % 2 ? '#FFF6C8' : '#F2C230');
  stroke([[80, -230], [104, -260], [104, -150]], 6); dot(104, -266, 12, '#E8392B');
  sh(rect(-70, -120, 140, 20), '#2E2E2E', null, { lw: 4 });
  pop();
}
export function clock(x, y, r, t, o = {}) {
  shape(ell(x, y, r, r), { fill: o.face ?? '#FFF8E6', lw: 7 });
  for (let i = 0; i < 12; i++) { const a = i / 12 * TAU; stroke([[x + Math.cos(a) * r * .78, y + Math.sin(a) * r * .78], [x + Math.cos(a) * r * .9, y + Math.sin(a) * r * .9]], 4); }
  const hA = (o.h ?? t * .02) * TAU - Math.PI / 2, mA = (o.m ?? t * .2) * TAU - Math.PI / 2;
  stroke([[x, y], [x + Math.cos(hA) * r * .45, y + Math.sin(hA) * r * .45]], 9); stroke([[x, y], [x + Math.cos(mA) * r * .7, y + Math.sin(mA) * r * .7]], 6); dot(x, y, 7);
}
Object.assign(WORLDS, {
  strip: { pal: ['#3A0D18', '#D4A017', '#7A1F2B'], draw(t) {
    bands(['#1A0609', '#2A0A11', '#3A0D18'], -400, FLOOR); carpet('#7A1F2B', '#D4A017', '#3A0D18');
    for (let i = 0; i < 8; i++) slot(-200 + i * 260, FLOOR, 1, { t: t + i, spin: t * (1 + i * .2) });
    for (let i = 0; i < 5; i++) { fillOnly(ell(100 + i * 450, 60, 120, 30), '#D4A017', { alpha: .5 }); }
  } },
  maze: { pal: ['#0F5132', '#F3E9D2', '#C9A227'], draw(t) {
    bands(['#0B3D26', '#0F5132'], -400, FLOOR); floorBand('#0B3D26');
    fillOnly(rect(-400, -400, 3000, 260), '#08301E', { boil: 0 });   // low ceiling
    for (let i = 0; i < 7; i++) { const x = -150 + i * 340; sh(rect(x, FLOOR - 380, 40, 380), '#C9A227', null, { lw: 5 }); slot(x + 140, FLOOR, .85, { col: '#F3E9D2', dark: '#D6C9A8', t: t + i, spin: t }); }
  } },
  book: { pal: ['#14213D', '#FCA311', '#E5E5E5'], draw(t) {
    bands(['#14213D', '#1C2D52'], -400, FLOOR); floorBand('#0E1830');
    for (let i = 0; i < 4; i++) { sh(rect(-100 + i * 600, 120, 500, 300), '#0E1830', null); fillOnly(rect(-80 + i * 600, 140, 460, 260), '#2E7D32', { alpha: .9 }); for (let k = 0; k < 4; k++) stroke([[-60 + i * 600, 180 + k * 50], [340 + i * 600, 180 + k * 50]], 4, { line: '#E5E5E5' }); }
    sh(rect(-300, FLOOR - 200, 2600, 200), '#FCA311', [rect(-300, FLOOR - 200, 2600, 30), '#D4870B']);
  } },
  tower: { pal: ['#1B4965', '#F4D35E', '#FAF0CA'], draw(t) {
    bands(['#1B4965', '#235A7C'], -400, FLOOR); carpet('#0F2F44', '#F4D35E', '#1B4965');
    sh(rect(880, -160, 280, FLOOR + 160), '#FAF0CA', [rect(1080, -160, 80, FLOOR + 160), '#D9CFA6']); clock(1020, 60, 120, t, { m: t * .02, h: .3 });
    for (let i = 0; i < 6; i++) if (Math.abs(i - 2.5) > 1) slot(-100 + i * 380, FLOOR, 1, { col: '#F4D35E', dark: '#C9A93E', t: t + i, spin: t });
  } },
  garden: { pal: ['#9ED8F0', '#FF7AA2', '#FFF8EE'], draw(t) {
    bands(['#CFEFFB', '#9ED8F0'], -400, FLOOR); floorBand('#FFF8EE');
    for (let i = 0; i < 4; i++) { sh(rect(-200 + i * 650, -300, 300, 700), '#E6F7FD', null, { lw: 5 }); }
    for (let i = 0; i < 9; i++) { const x = -150 + i * 260; stroke(spline([[x, FLOOR], [x - 10, FLOOR - 120], [x + 10, FLOOR - 200]], false), 6, { line: '#3E8E5B' }); for (let k = 0; k < 6; k++) { const a = k / 6 * TAU + t * .3; shape(ell(x + 10 + Math.cos(a) * 26, FLOOR - 210 + Math.sin(a) * 26, 18, 18), { fill: k % 2 ? '#FF7AA2' : '#FFD1DC', lw: 4 }); } dot(x + 10, FLOOR - 210, 12, '#F4D35E'); }
    sh(ell(1300, 300, 260, 60), '#BDE6F7', null);
  } },
  lab: { pal: ['#DDF3F0', '#14746F', '#F6AE2D'], draw(t) {
    bands(['#DDF3F0', '#C8EBE6'], -400, FLOOR); floorBand('#A8D8D0');
    for (let i = 0; i < 6; i++) slot(-100 + i * 320, FLOOR, .9, { col: '#14746F', dark: '#0E5551', t: t + i, spin: t * .5 });
    sh(rr(1500, 200, 300, 200, 12), '#FFFFFF', null); for (let k = 0; k < 4; k++) stroke([[1530, 240 + k * 40], [1760, 240 + k * 40]], 4, { line: '#14746F' });
  } },
  venue: { pal: ['#2F3E46', '#CAD2C5', '#84A98C'], draw(t) {
    bands(['#2F3E46', '#354F52'], -400, FLOOR); floorBand('#52796F');
    for (let i = 0; i < 6; i++) { slot(-100 + i * 330, FLOOR, .95, { col: '#84A98C', dark: '#5F7F67', t: t + i, spin: t }); clock(-100 + i * 330, FLOOR - 400, 28, t, { m: t * .05 + i, h: .1 }); }
    clock(1400, 200, 100, t, { m: t * .05, h: .35 });
  } },
  zone: { pal: ['#FF6B1A', '#111111', '#FFD6B0'], draw(t) {
    screenRectWorld('#111111'); for (let i = 0; i < 14; i++) { const r = 200 + i * 120 + (t * 160) % 120; stroke(ell(960, 500, r, r * .6, 60), 8, { line: i % 2 ? '#FF6B1A' : '#3A1A08' }); }
    slot(960, FLOOR, 1.5, { col: '#FF6B1A', dark: '#C24E0C', t, spin: t * 3 }); floorBand('#111111');
  } },
  air: { pal: ['#E8F6FF', '#3D5A80', '#EE6C4D'], draw(t) {
    bands(['#E8F6FF', '#D3EDFF'], -400, FLOOR); floorBand('#98C1D9');
    for (let i = 0; i < 6; i++) { const x = -100 + i * 380; stroke(spline([[x, 0], [x + 40, 200], [x - 40, 400], [x, 600]], false), 10, { line: '#3D5A80', alpha: .3 }); }
    for (let i = 0; i < 4; i++) slot(1100 + i * 260, FLOOR, .9, { col: '#3D5A80', dark: '#293D59', t: t + i, spin: t });
  } },
});
function screenRectWorld(col) { fillOnly(rect(-3000, -2000, 8000, 5000), col, { boil: 0 }); }
WORLDS.beige.draw = (orig => t => { orig(t); for (let i = 0; i < 3; i++) slot(1350 + i * 200, FLOOR, .8, { col: '#B89A70', dark: '#8A6E4B', t: t + i, spin: t * .3 }); })(WORLDS.beige.draw);

Object.assign(INSERTS, {
  card: (t, u) => { fillOnly(rect(-1200, -700, 2400, 1400), '#2D385A', { boil: 0 }); push(); rotate(-.04); sh(rr(-430, -260, 860, 520, 10), '#FFFDF5', [rect(-430, 140, 860, 120), '#EEE6D4']); fillOnly(rect(-430, -260, 860, 70), '#C8326B', { boil: .3 });
    text('CUSTOMER COMMENT CARD', 0, -224, { font: '800 34px "Baloo 2"', fill: '#FFFDF5' });
    const msg = "Why don't casinos have clocks?", n = Math.floor(clamp(u / 1.5) * msg.length); text(msg.slice(0, n), 0, -40, { font: '62px "Caveat Brush"', fill: '#2A2A6A' }); pop(); },
  lab: (t, u) => { fillOnly(rect(-1200, -700, 2400, 1400), '#DDF3F0', { boil: 0 });
    for (const [x, lab, real, est, col] of [[-420, 'noise', 1, .62, '#F6AE2D'], [420, 'music', 1, .9, '#14746F']]) {
      sh(rect(x - 200, -320, 400, 560), '#FFFFFF', null);
      const k = clamp((u - (x > 0 ? 3 : .6)) / 1.4);
      sh(rect(x - 130, 200 - 380 * real, 100, 380 * real), '#CAD2C5', null, { lw: 5 }); sh(rect(x + 30, 200 - 380 * est * k, 100, Math.max(2, 380 * est * k)), col, null, { lw: 5 });
      clock(x - 80, -250, 40, t, { m: 0, h: .25 }); clock(x + 80, -250, 40, t, { m: est * .99, h: .25 });
      if (x < 0) { for (let i = 0; i < 3; i++) dot(x - 150 + i * 40, 230, 8, '#F6AE2D'); } else { for (let i = 0; i < 3; i++) shape(ell(x - 140 + i * 50, 236, 12, 9), { fill: '#14746F', lw: 4 }); stroke([[x - 128, 236], [x - 128, 196]], 4); }
    } },
  zone: (t, u) => { WORLDS.zone.draw(t); },
  curdslot: (t, u) => { WORLDS.zone.draw(t); push(); translate(260, 900); curd(0, 0, 1.6, { t, look: [-.8, -.3], sq: 1 }); pop(); push(); translate(260, 900); fillOnly(ell(-30, -100, 70, 40), 'rgba(255,107,26,.35)'); pop(); },
  meter: (t, u) => { fillOnly(rect(-1200, -700, 2400, 1400), '#E8F6FF', { boil: 0 }); sh(rr(-300, -320, 600, 520, 40), '#3D5A80', null); sh(rr(-240, -260, 480, 220, 20), '#D9F0D2', null, { lw: 5 });
    const v = (20.9 * clamp(u / 1.6)).toFixed(1); text(v + '% O₂', 0, -150, { font: '800 110px "Baloo 2"', fill: '#1B4332' });
    sh(ell(-120, 100, 60, 60), '#EE6C4D', null); sh(ell(120, 100, 60, 60), '#98C1D9', null);
    if (u > 2.2) { push(); translate(380, -300); rotate(.2); sh(rr(-140, -70, 280, 140, 12), '#FFFDF5', null); text('= OUTSIDE AIR', 0, 0, { font: '800 34px "Baloo 2"', fill: '#3D5A80' }); pop(); } },
});

export function casinoPieces(E, t, firstAct) {
  const a = n => firstAct(n), w = E.world;
  if (w === 'maze') { const f = a('friedman'); if (f && t > f.t) { const x = 300; fillOnly(spline([[x - 46, FLOOR], [x - 50, FLOOR - 260], [x + 50, FLOOR - 260], [x + 46, FLOOR]]), INK); fillOnly(ell(x, FLOOR - 300, 34, 40), INK); fillOnly(rr(x - 70, FLOOR - 200, 60, 80, 6), '#F3E9D2'); } }
  if (w === 'book') { const c = a('clocks'); if (c && t > c.t) { const p = back(seg(t, c.t, c.t + .4), 2); push(); translate(900, 180); scale(p); clock(0, 0, 90, t, { m: t * .03, h: .4 }); pop(); push(); translate(1500, 560); scale(back(seg(t, c.t + 3, c.t + 3.4), 2)); clock(0, 0, 40, t, { m: .2, h: .4 }); pop(); } }
  if (w === 'venue') { /* the clocks are already everywhere */ }
  if (w === 'beige') { const p = a('phones'); if (p && t > p.t) for (let i = 0; i < 5; i++) { const k = back(seg(t, p.t + .5 + i * .4, p.t + .9 + i * .4), 2); push(); translate(-100 + i * 300, 560); scale(k); sh(rr(-36, -64, 72, 128, 12), '#2E2E2E', null); fillOnly(rr(-28, -54, 56, 100, 6), '#9ED8F0'); text('9:41', 0, -10, { font: '800 18px "Baloo 2"', fill: '#14213D' }); pop(); } }
}
