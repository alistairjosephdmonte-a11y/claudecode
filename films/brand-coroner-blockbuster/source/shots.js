// The 48 shots. Each: which sets are lit and visible, a light preset, a camera path (lens in mm), props, and per-frame motion.
// u is shot progress 0..1 (10 s); t is seconds into the shot.
import * as THREE from 'three';
import { clamp, lerp, seg, ss, eio, eo, mulberry, hash } from '/core/lib.js';
import { PAL, ZONE, M, box, sheet, figure, walk, pose, label } from './world.js';
import { sourceCard, excerpt, summary, plate, receipt, dvd, mailer, block, gear } from './props.js';

const Z = (z, dx = 0, dy = 0, dz = 0) => [ZONE[z][0] + dx, dy, ZONE[z][1] + dz];
// camera keys: [u, pos, look, mm]; eased between keys
export function keys(K) {
  return u => { let i = 0; while (i < K.length - 2 && u > K[i + 1][0]) i++; const [u0, p0, l0, f0] = K[i], [u1, p1, l1, f1] = K[Math.min(i + 1, K.length - 1)], k = u1 > u0 ? eio(seg(u, u0, u1)) : 0;
    return { p: p0.map((v, j) => lerp(v, p1[j], k)), l: l0.map((v, j) => lerp(v, l1[j], k)), f: lerp(f0, f1, k) }; };
}
const v3 = a => new THREE.Vector3(...a);
const place = (o, p, ry = 0) => { o.position.set(...p); o.rotation.y = ry; return o; };
const flat = (o, p, rz = 0) => { o.position.set(...p); o.rotation.set(0, rz, 0); return o; };

// —— shared evidence ——
const RANDOLPH = () => sourceCard({ idx: '01', name: 'Marc Randolph', role: 'Netflix co-founder', pub: 'That Will Never Work (Little, Brown, 2019)', seed: 51,
  lines: ['Places the meeting in Dallas, September 2000.', 'Recalls proposing that Blockbuster buy Netflix and run its online business.', 'Recalls a price of $50 million, and a reaction he read as dismissive.'], note: "Randolph's recollection. Not independently documented." });
const ANTIOCO = () => sourceCard({ idx: '02', name: 'John Antioco', role: 'Blockbuster chief executive, 1997–2007', pub: 'LinkedIn post, as reported by Next TV, 3 June 2022', seed: 52,
  quote: '“There were no serious conversations about our buying the nascent Netflix business twenty years ago.”', lines: ['Also wrote that he “was not present at any meeting with Netflix where the subject came up.”'], note: "Antioco's recollection, written two decades later." });
const FIFTY = () => plate([['$50,000,000', .42, .52, PAL.ivory], ['REPORTED BY MARC RANDOLPH', 0, .74, PAL.yellow, `600 ${2.6 * 420 * .07}px "Plex Mono"`, 6], ['A RECALLED FIGURE · NOT A SIGNED OR DOCUMENTED OFFER', 0, .87, '#9aa3ab', `500 ${2.6 * 420 * .05}px "Plex Mono"`, 3]], { seed: 50 });

// shared animation for the store lot: customers walking in on a Friday night
function lotPeople(S, t, mode) {
  S.people.forEach((F, i) => { const R = mulberry(70 + i), x0 = (R() - .5) * 7, z0 = 2.8 + R() * .8, ph = (t * .32 + R()) % 1, door = [0, -.3];
    if (mode === 'none') { F.visible = false; return; } F.visible = true;
    const x = lerp(x0, door[0] + (R() - .5) * .6, ph), z = lerp(z0, door[1], ph); F.position.set(x, .04, z); F.rotation.y = Math.atan2(door[0] - x0, door[1] - z0); walk(F, t * .95 + R(), 1); F.visible = ph < .97; });
}
function browsers(S, t) { S.people.forEach((F, i) => { if (i > 4) { F.visible = false; return; } const R = mulberry(90 + i); F.visible = true; const lx = -1.15 + (i % 3) * .9, lz = -.9 + R() * 1.2;
  F.position.set(lx, .06, S.z0 - .3 + lz + Math.sin(t * .2 + i) * .15); F.rotation.y = (i % 2 ? 1 : -1) * Math.PI / 2; pose(F, { arm: [i % 2 ? -.9 : 0, 0] }); walk(F, 0, 0); }); }

export const SHOTS = [
  // ———————————— ACT 01 · THE OFFER ————————————
  { show: ['dallas'], light: ['morning', 'dallas'], title: 'DALLAS, TEXAS\nSEPTEMBER 2000',
    cam: keys([[0, Z('dallas', .6, 2.1, 9.2), Z('dallas', -.4, 1.9, -2), 28], [1, Z('dallas', .2, 2.2, 6.2), Z('dallas', -.4, 2.1, -2), 28]]) },
  { show: ['plaza'], light: ['day', 'plaza'],
    cam: u => { const z = lerp(-8.6, -11.4, u); return { p: [ZONE.plaza[0] + .15, .62, z], l: [ZONE.plaza[0], .9, -17], f: 35 }; },
    update(u, t, C) { C.plaza.people.forEach((F, i) => { const z = 3.5 - i * .25 + (i === 1 ? -.45 : 0) - t * .42; F.position.set([-.45, 0, .45][i], .032, z); F.rotation.y = Math.PI; walk(F, t * .9 + i * .33); }); } },
  { show: ['board'], light: ['window', 'board'],
    cam: keys([[0, Z('board', -2.4, 2.3, 5.4), Z('board', -.9, .7, -.6), 35], [1, Z('board', 1.6, 2.3, 5.4), Z('board', .9, .7, -.6), 35]]),
    enter(C) { C.board.folder.visible = false; } },
  { show: ['board'], light: ['window', 'board'], dof: 1.4,
    cam: keys([[0, Z('board', .75, 1.12, 1.35), Z('board', .02, .82, .32), 85], [1, Z('board', .55, 1.02, 1.18), Z('board', 0, .82, .3), 85]]),
    update(u, t, C) { const F = C.board.folder, k = eo(seg(t, 1.2, 3.4)); F.visible = true; F.position.set(lerp(-.7, 0, k), .81 + .04 * Math.sin(Math.PI * k) * (1 - k), lerp(.55, .3, k)); F.rotation.y = lerp(.25, .04, k); } },
  { show: [], light: ['table', 'docs'], dof: 1.2,
    cam: keys([[0, Z('docs', -2.0, 4.9, 3.4), Z('docs', -1.3, 0, .05), 85], [1, Z('docs', -1.2, 3.9, 2.5), Z('docs', -1.3, 0, .1), 85]]),
    enter(C) { C.add(flat(RANDOLPH(), Z('docs', -1.3, .02, 0), .05)); } },
  { show: [], light: ['table', 'docs'], dof: 1.2,
    cam: keys([[0, Z('docs', 2.1, 4.9, 3.4), Z('docs', 1.4, 0, 0), 85], [1, Z('docs', 1.5, 3.9, 2.5), Z('docs', 1.4, 0, .05), 85]]),
    enter(C) { C.add(flat(RANDOLPH(), Z('docs', -1.3, .02, 0), .05)); C.add(flat(ANTIOCO(), Z('docs', 1.4, .02, -.05), -.04)); } },
  { show: [], light: ['spot', 'felt'], dof: .8,
    cam: keys([[0, Z('felt', -1.5, 4.2, 4.6), Z('felt', 0, 0, .3), 50], [1, Z('felt', 0, 6.1, 1.0), Z('felt', 0, 0, -.1), 50]]),
    enter(C) { C.add(flat(FIFTY(), Z('felt', 0, .05, 0))); } },
  { show: ['board', 'dallas'], light: ['table', 'docs'],
    cam: keys([[0, Z('docs', 0, 2.8, 2.1), Z('docs', 0, 0, -.1), 50], [1, Z('docs', -3, 9.5, 9.5), Z('docs', -4, 0, -2.5), 35]]),
    enter(C) { C.add(flat(RANDOLPH(), Z('docs', -1.3, .02, 0), .05)); C.add(flat(ANTIOCO(), Z('docs', 1.4, .02, -.05), -.04));
      C.add(flat(label('WHAT REALLY HAPPENED?', { size: 120, weight: 700, track: 6, ppu: 520, seed: 8 }), Z('docs', 0, .02, 1.25))); C.add(flat(FIFTY(), Z('felt', 0, .05, 0))); } },

  // ———————————— ACT 02 · THE EMPIRE ————————————
  { show: ['store'], light: ['night', 'store'],
    cam: keys([[0, Z('store', 3.8, .7, 4.8), Z('store', .4, .5, -2.2), 35], [1, Z('store', 1.4, .62, 3.6), Z('store', -.1, .55, -2.4), 35]]),
    enter(C) { C.store.roof.visible = true; }, update(u, t, C) { lotPeople(C.store, t); } },
  { show: ['store'], light: ['fluor', 'store'], dof: .5,
    cam: u => { const S = C_.store, z = lerp(.95, -.9, eio(u)); return { p: [ZONE.store[0] - 1.15, .58, ZONE.store[1] + S.z0 + z], l: [ZONE.store[0] - 1.3, .45, ZONE.store[1] + S.z0 + z - 1.5], f: 35 }; },
    update(u, t, C) { browsers(C.store, t); } },
  { show: ['store'], light: ['fluor', 'store'], dof: 1.6,
    cam: keys([[0, Z('store', 3.05, .84, -1.0), Z('store', 2.25, .5, -1.5), 50], [1, Z('store', 2.95, .78, -1.12), Z('store', 2.25, .5, -1.5), 50]]),
    update(u, t, C) { const S = C.store, cx = 2.2, cz = S.z0 + .8; S.people.forEach(F => F.visible = false); const cu = S.people[0]; cu.visible = true; cu.position.set(cx + .1, .06, cz + .42); cu.rotation.y = Math.PI; pose(cu, { arm: [-.6 * ss(seg(t, 1, 2.5)), 0] });
      const k = ss(seg(t, 1.2, 3.2)); S.rcase.position.set(cx + .15 - .12 * k, .52, cz + .2 - .1 * k); S.rcase.rotation.y = .3;
      const kc = ss(seg(t, 3.6, 5.2)); S.mcard.position.set(cx + .32 - .1 * kc, .521, cz + .22 - .12 * kc); S.mcard.rotation.y = -.2;
      pose(S.clerk, { arm: [-.5 * ss(seg(t, 5.5, 7)), -.4 * ss(seg(t, 6, 8))] }); } },
  { show: ['plan', 'net'], light: ['table', 'plan'],
    cam: keys([[0, Z('plan', 3.2, 1.2, 3.6), Z('plan', 0, .3, 0), 50], [.4, Z('plan', 3.4, 2.4, 4.2), Z('plan', 0, .3, 0), 50], [1, Z('net', 0, 13, 14), Z('net', 0, 1.2, 0), 35]]),
    update(u, t, C) { const H = C.net.hero; H.scale.y = Math.max(1e-3, eo(seg(t, .4, 3.2))); C.net.set(Math.floor(lerp(0, 380, ss(seg(t, 4, 10)))), (t * 3) % 1); } },
  { show: ['net'], light: ['table', 'net'], card: true,
    cam: keys([[0, Z('net', -1, 9.5, 13.5), Z('net', 0, 1.0, 2.2), 35], [1, Z('net', 1, 13.0, 11.5), Z('net', 0, 1.0, 1.6), 35]]),
    enter(C) { C.add(flat(label('≈ 9,100 STORES WORLDWIDE · YEAR-END 2004', { size: 110, weight: 700, ppu: 220, track: 4 }), Z('net', 0, .01, 5.6), 0)); C.add(flat(label('SOURCE: FORM 10-K, FISCAL 2004 · EACH MODEL ≈ 5 STORES', { size: 60, weight: 600, ppu: 220, track: 3 }), Z('net', 0, .01, 6.4), 0)); },
    update(u, t, C) { C.net.set(Math.floor(lerp(380, C.net.MAX - 40, eo(seg(t, 0, 8)))), (t * 3) % 1); } },
  { show: [], light: ['table', 'charts'], dof: 1.5,
    cam: keys([[0, Z('charts', -3.6, 2.9, -.2), Z('charts', -4.0, 0, -.95), 100], [1, Z('charts', -3.6, 2.9, 1.7), Z('charts', -4.0, 0, .85), 100]]),
    enter(C) { C.add(flat(receipt(), Z('charts', -4, .02, 0), .03)); } },
  { show: [], light: ['table', 'charts'],
    cam: keys([[0, Z('charts', -.6, 7.4, 13.4), Z('charts', .2, 1.0, 1.6), 50], [1, Z('charts', .4, 7.0, 12.4), Z('charts', .4, 1.0, 1.6), 50]]),
    enter(C) { C.add(flat(receipt(), Z('charts', -4, .02, 0), .03));
      const mv = block(1.2, 1, 1.2, PAL.blue, 'MOVIES  $552.1M', { size: 80, ly: .1 }), gm = block(1.2, 1, 1.2, PAL.yellow, 'GAMES  $70.3M', { size: 80, ly: .1 }); C.add(place(mv, Z('charts', -1.2))); C.add(place(gm, Z('charts', -1.2))); C.s15 = { mv, gm };
      C.add(flat(label('EXTENDED VIEWING FEES, 2004 · $622.4M', { size: 90, weight: 700, ppu: 300, track: 3 }), Z('charts', -1.2, .02, 1.45)));
      const strip = sheet(6, .5, (g, w, h) => { g.fillStyle = '#d6d0c2'; g.fillRect(0, 0, w, h); g.fillStyle = PAL.red; g.fillRect(0, 0, w * .14, h); g.fillStyle = PAL.ink; g.font = `600 ${h * .38}px "Plex Mono"`; g.fillText('≈14%', w * .015, h * .65); g.fillText('OF RENTAL REVENUE, 2004', w * .17, h * .65); }, { ppu: 300, base: false, curl: 0 });
      C.add(flat(strip, Z('charts', 1.0, .02, 2.5))); C.add(flat(label('SOURCE: BLOCKBUSTER FORM 10-K, FISCAL 2005', { size: 60, weight: 600, ppu: 300, track: 3 }), Z('charts', 1.0, .02, 3.2))); },
    update(u, t, C) { const { mv, gm } = C.s15, a = eo(seg(t, .8, 4)) * 2.76, b = eo(seg(t, 3.2, 5)) * .35; mv.scale.y = Math.max(.001, a); gm.scale.y = Math.max(.001, b); gm.position.y = a; } },
  { show: ['net'], light: ['low', 'net'],
    cam: keys([[0, Z('net', -8.2, 2.5, 7.8), Z('net', -3.2, 1.1, 3.0), 28], [1, Z('net', 2.8, 2.4, 7.6), Z('net', 7.0, 1.1, 2.8), 28]]),
    update(u, t, C) { C.net.set(C.net.MAX, 1); } },

  // ———————————— ACT 03 · THE CHALLENGER ————————————
  { show: [], light: ['table', 'docs'], dof: 1.6,
    cam: keys([[0, Z('docs', 1.2, 3.7, 8.0), Z('docs', .3, 0, 5.0), 85], [1, Z('docs', .9, 3.2, 7.4), Z('docs', .2, 0, 5.0), 85]]),
    enter(C) { C.m17 = flat(mailer(), Z('docs', 0, .02, 5), .1); C.add(C.m17); C.d17 = dvd(); C.add(C.d17); },
    update(u, t, C) { const k = ss(seg(t, 1.5, 6)); C.d17.position.set(ZONE.docs[0] + lerp(1.6, .05, k), .05 + .02 * (1 - k), ZONE.docs[1] + 5 + lerp(-.6, 0, k)); C.d17.rotation.y = t * .1; C.d17.visible = k < .985; } },
  { show: ['mail'], light: ['fluor', 'mail'],
    cam: keys([[0, Z('mail', -3.8, .95, 2.3), Z('mail', -1.2, .3, -.6), 35], [1, Z('mail', 2.6, .95, 2.3), Z('mail', 4.2, .3, -.6), 35]]),
    update(u, t, C) { C.mail.step(t); C.mail.workers.forEach((F, i) => pose(F, { arm: [-.7 + .25 * Math.sin(t * 2.2 + i), -.6 + .25 * Math.cos(t * 2 + i)] })); } },
  { show: [], light: ['table', 'charts'],
    cam: keys([[0, Z('charts', 0, 9, 3.5), Z('charts', 0, 0, 0), 35], [1, Z('charts', 0, 8.2, 2.0), Z('charts', 0, 0, 0), 35]]),
    enter(C) { const P = [['SUBSCRIBE', -2.2, -1.4], ['RECEIVE', 2.2, -1.4], ['WATCH', 2.2, 1.4], ['RETURN', -2.2, 1.4]];
      P.forEach(([s, x, z], i) => C.add(flat(label(s, { size: 120, weight: 700, track: 8, ppu: 360, seed: 60 + i }), Z('charts', x, .02, z))));
      [[0, -1.4, 0, 1.7], [2.2, 0, Math.PI / 2, 1.9], [0, 1.4, 0, 1.7], [-2.2, 0, Math.PI / 2, 1.9]].forEach(([x, z, r, len]) => { const ar = sheet(len, .1, (g, w, h) => { g.fillStyle = PAL.nred; g.fillRect(0, 0, w, h); }, { base: false, curl: 0, ppu: 200 }); C.add(flat(ar, Z('charts', x, .015, z), r)); });
      C.add(flat(label('NO LATE FEES IN THIS MODEL', { size: 70, weight: 600, ppu: 300, track: 4 }), Z('charts', 0, .02, 0))); C.tok = dvd(); C.tok.scale.setScalar(.45); C.add(C.tok); },
    update(u, t, C) { const ph = (t / 10 * 1.5) % 1, pts = [[-2.2, -1.4], [2.2, -1.4], [2.2, 1.4], [-2.2, 1.4]], i = Math.floor(ph * 4), f = ss(ph * 4 - i), a = pts[i], b = pts[(i + 1) % 4];
      C.tok.position.set(ZONE.charts[0] + lerp(a[0], b[0], f), .06, ZONE.charts[1] + lerp(a[1], b[1], f)); } },
  { show: ['store', 'mail'], light: ['fluor', 'store'], split: true,
    cam: keys([[0, Z('store', 2.6, 1.6, 4.2), Z('store', 0, .5, -2.2), 35], [1, Z('store', 1.6, 1.4, 3.8), Z('store', 0, .5, -2.2), 35]]),
    cam2: keys([[0, Z('mail', -2.6, 1.8, 3.6), Z('mail', 0, .3, -.4), 35], [1, Z('mail', -1.4, 1.6, 3.2), Z('mail', .4, .3, -.4), 35]]),
    update(u, t, C) { lotPeople(C.store, t); C.mail.step(t); } },
  { show: [], light: ['table', 'charts'],
    cam: keys([[0, Z('charts', 0, 3.6, 9.4), Z('charts', 0, 1.3, 0), 50], [1, Z('charts', 0, 4.4, 8.4), Z('charts', 0, 1.5, 0), 50]]),
    enter(C) { const L = ['STORE RENT', 'INVENTORY', 'STAFF', 'STORE OPERATIONS'], R = ['FULFILLMENT', 'POSTAGE', 'WAREHOUSING', 'SUBSCRIPTION OPERATIONS']; C.cb = [];
      L.forEach((s, i) => { const b = block(2.6, .62, 1.6, '#3f5f93', s, { size: 70 }); C.add(place(b, Z('charts', -2.0, i * .64, 0))); C.cb.push([b, i]); });
      R.forEach((s, i) => { const b = block(2.6, .62, 1.6, '#a8393f', s, { size: 64 }); C.add(place(b, Z('charts', 2.0, i * .64, 0))); C.cb.push([b, i + .3]); });
      C.add(flat(label('RETAIL', { size: 110, weight: 700, track: 8, ppu: 300 }), Z('charts', -2, .02, 1.4))); C.add(flat(label('BY MAIL', { size: 110, weight: 700, track: 8, ppu: 300 }), Z('charts', 2, .02, 1.4)));
      C.add(flat(label('CONCEPTUAL · NOT TO SCALE · NOT EXHAUSTIVE', { size: 56, weight: 600, ppu: 300, track: 3 }), Z('charts', 0, .02, 2.1))); },
    update(u, t, C) { C.cb.forEach(([b, i]) => { const k = eo(seg(t, .6 + i * 1.1, 1.6 + i * 1.1)); b.visible = k > 0; b.position.y = i % 1 === 0 ? (Math.floor(i) * .64 + (1 - k) * 2.5) : (Math.floor(i) * .64 + (1 - k) * 2.5); }); } },
  { show: ['desk'], light: ['window', 'desk'], screen: 'web', dof: 1,
    cam: keys([[0, Z('desk', .5, 1.75, .6), Z('desk', -.2, 1.5, -1.4), 50], [1, Z('desk', .1, 1.62, -.35), Z('desk', -.2, 1.55, -1.4), 50]]) },
  { show: ['net'], light: ['table', 'net'],
    cam: keys([[0, Z('net', 12.5, 1.0, 6.5), Z('net', 6.5, 1.0, 1.5), 35], [1, Z('net', 11.5, 2.4, 8.5), Z('net', 4.5, 1.2, 1.5), 35]]),
    enter(C) { C.add(flat(label('RELATIVE SCALE · AROUND 2000 · NOT TO A NUMERICAL RATIO', { size: 60, weight: 600, ppu: 300, track: 3 }), Z('net', 8.6, .02, 4.1))); C.add(flat(label('DVD BY MAIL', { size: 70, weight: 700, ppu: 300, track: 4 }), Z('net', 8.6, .02, 3.5))); },
    update(u, t, C) { C.net.set(C.net.MAX, 1); C.net.small.visible = true; } },
  { show: ['board', 'dallas', 'store', 'plan', 'net', 'mail', 'desk'], light: ['wide', 'docs'],
    cam: keys([[0, Z('docs', 0, 3, 3.6), Z('docs', 0, 0, .3), 35], [1, Z('docs', 0, 20, 8), Z('docs', 0, 0, -.5), 35]]),
    enter(C) { C.add(flat(label('WAS THE THREAT\nOBVIOUS IN 2000?', { size: 150, weight: 700, ppu: 300, track: 6 }), Z('docs', 0, .02, .3))); },
    update(u, t, C) { C.net.set(C.net.MAX, 1); } },

  // ———————————— ACT 04 · THE COUNTERATTACK ————————————
  { show: [], light: ['table', 'docs'], dof: 1.3, title: 'AUGUST 2004',
    cam: keys([[0, Z('docs', -.5, 5.6, 3.6), Z('docs', 0, 0, -.25), 50], [1, Z('docs', .3, 3.4, 2.0), Z('docs', 0, 0, -.3), 50]]),
    enter(C) { C.add(flat(excerpt({ mast: ['UNITED STATES SECURITIES AND EXCHANGE COMMISSION', 'BLOCKBUSTER INC.'], sub: 'FORM 10-K · FISCAL 2004', passage: 'In August 2004, we launched BLOCKBUSTER ONLINE, our U.S. online subscription program.', cite: 'Blockbuster Inc., annual report on Form 10-K for fiscal 2004, filed March 2005. SEC EDGAR accession 0001193125-05-063510.', hi: true, seed: 71 }), Z('docs', 0, .02, -.2), .03)); } },
  { show: ['plan'], light: ['table', 'plan'],
    cam: keys([[0, Z('plan', -2.4, 4.4, 7.6), Z('plan', .4, .3, .3), 35], [1, Z('plan', 4.0, 4.2, 7.0), Z('plan', 2.6, .3, .3), 35]]),
    enter(C) { const m = new THREE.Group(); box(1.8, .5, 1.3, M.white, 0, 0, 0, m); box(1.82, .08, .1, M.nred, 0, .5, .65, m); C.add(place(m, Z('plan', 4.2, 0, .2))); C.add(flat(label('STORES', { size: 90, weight: 700, ppu: 300, track: 6 }), Z('plan', 0, .02, 1.65))); C.add(flat(label('BY MAIL', { size: 90, weight: 700, ppu: 300, track: 6 }), Z('plan', 4.2, .02, 1.45)));
      C.env = new THREE.InstancedMesh(new THREE.BoxGeometry(.26, .02, .18), M.nred, 14); C.env.castShadow = true; C.add(C.env); },
    update(u, t, C) { C.net.hero.scale.y = 1; const q = new THREE.Object3D(); for (let i = 0; i < 14; i++) { const ph = (i / 14 + t * .06) % 1; q.position.set(ZONE.plan[0] + lerp(1.9, 3.3, ph), .55 + Math.sin(ph * Math.PI) * .5, ZONE.plan[1] + .2); q.rotation.set(0, 0, Math.sin(ph * 6.28) * .2); q.updateMatrix(); C.env.setMatrixAt(i, q.matrix); } C.env.instanceMatrix.needsUpdate = true; } },
  { show: [], light: ['table', 'docs'], dof: 1.2, title: 'JANUARY 2005',
    cam: keys([[0, Z('docs', -1.0, 7.6, 5.4), Z('docs', -.1, 0, -.1), 85], [1, Z('docs', .7, 6.9, 4.8), Z('docs', .2, 0, -.1), 85]]),
    enter(C) { C.add(flat(summary({ kicker: 'JAN 2005', title: 'NO LATE FEES', body: 'Extended viewing fees eliminated “beginning on January 1, 2005” in “more than 4,500 company-operated stores and approximately 550 participating franchise stores in the United States.” The program removed extended viewing fees; it is not a claim that every return-related charge ended.', cite: 'Quoted phrases: Blockbuster Inc., Form 10-K for fiscal 2004.', w: 3.0, h: 2.45, seed: 73, tagCol: PAL.red }), Z('docs', 0, .02, -.1), -.02)); } },
  { show: [], light: ['table', 'docs'], dof: 1.3,
    cam: keys([[0, Z('docs', -1.1, 4.6, 2.6), Z('docs', -.5, 0, -.25), 85], [1, Z('docs', 1.0, 4.4, 2.5), Z('docs', .5, 0, -.25), 85]]),
    enter(C) { C.add(flat(excerpt({ mast: ['UNITED STATES SECURITIES AND EXCHANGE COMMISSION', 'BLOCKBUSTER INC.'], sub: 'FORM 10-K · FISCAL 2005', passage: 'Despite the elimination of extended viewing fees, which accounted for approximately 14% of our rental revenues during 2004, and a declining in-store rental industry, we experienced only a 5.0% decline in our rental revenues from 2004.', cite: 'Blockbuster Inc., annual report on Form 10-K for fiscal 2005, filed March 2006. SEC EDGAR accession 0001193125-06-055023.', hi: true, seed: 74 }), Z('docs', 0, .02, -.2), .02)); } },
  { show: [], light: ['table', 'charts'],
    cam: keys([[0, Z('charts', 0, 7.2, 11.5), Z('charts', 0, .8, 1.4), 50], [1, Z('charts', 0, 6.8, 10.6), Z('charts', 0, .8, 1.4), 50]]),
    enter(C) { const a = block(2.4, 1, 2.4, '#3f5f93', null), b = block(2.4, 1, 2.4, PAL.red, null); C.add(place(a, Z('charts', -2.2))); C.add(place(b, Z('charts', 2.2))); C.s29 = { a, b };
      C.add(flat(label('MORE THAN $500 MILLION\nREDUCTION IN RENTAL REVENUES', { size: 70, weight: 700, ppu: 300, track: 2 }), Z('charts', -2.2, .02, 1.9))); C.add(flat(label('REVENUE EFFECT', { size: 70, weight: 700, ppu: 300, track: 6, bg: '#3f5f93', col: PAL.ivory }), Z('charts', -2.2, .02, 2.75)));
      C.add(flat(label('ABOUT $60 MILLION\nMARKETING & IMPLEMENTATION COSTS', { size: 70, weight: 700, ppu: 300, track: 2 }), Z('charts', 2.2, .02, 1.9))); C.add(flat(label('EXPENSE', { size: 70, weight: 700, ppu: 300, track: 6, bg: PAL.red, col: PAL.ivory }), Z('charts', 2.2, .02, 2.75)));
      C.add(flat(label('SOURCE: FORM 10-K, FISCAL 2005 · DIFFERENT QUANTITIES, NOT ADDABLE', { size: 54, weight: 600, ppu: 300, track: 3 }), Z('charts', 0, .02, 3.4))); },
    update(u, t, C) { C.s29.a.scale.y = Math.max(.001, eo(seg(t, .5, 3)) * 3.0); C.s29.b.scale.y = Math.max(.001, eo(seg(t, 3.5, 5)) * .36); } },
  { show: [], light: ['table', 'docs'], dof: 1.3, title: 'NOVEMBER 2006',
    cam: keys([[0, Z('docs', -.5, 5.6, 3.6), Z('docs', 0, 0, -.25), 50], [1, Z('docs', .3, 3.4, 2.0), Z('docs', 0, 0, -.3), 50]]),
    enter(C) { C.add(flat(excerpt({ mast: ['UNITED STATES SECURITIES AND EXCHANGE COMMISSION', 'BLOCKBUSTER INC.'], sub: 'FORM 10-K · FISCAL 2006', passage: 'As of December 31, 2006, we had approximately 2.2 million online subscribers, including approximately 2.0 million paying subscribers.', cite: 'Blockbuster Inc., annual report on Form 10-K for fiscal 2006, filed March 2007. SEC EDGAR accession 0001193125-07-044360. Total Access launched November 2006.', hi: true, seed: 76 }), Z('docs', 0, .02, -.2), -.02)); } },
  { show: ['store'], light: ['fluor', 'store'], dof: 1.6,
    cam: keys([[0, Z('store', 3.05, .84, -1.0), Z('store', 2.25, .5, -1.5), 50], [1, Z('store', 2.95, .78, -1.12), Z('store', 2.25, .5, -1.5), 50]]),
    enter(C) { C.e31 = sheet(.2, .14, (g, w, h) => { g.fillStyle = PAL.nred; g.fillRect(0, 0, w, h); }, { base: false, ppu: 600, curl: 0, thick: .004 }); C.add(C.e31); },
    update(u, t, C) { const S = C.store, cx = ZONE.store[0] + 2.2, cz = ZONE.store[1] + S.z0 + .8; S.people.forEach(F => F.visible = false); const cu = S.people[0]; cu.visible = true; cu.position.set(2.3, .06, S.z0 + .8 + .42); cu.rotation.y = Math.PI;
      pose(cu, { arm: [-.7 * ss(seg(t, .5, 2)) * (1 - ss(seg(t, 4, 5))), 0] }); const k = ss(seg(t, 1, 3.4)); C.e31.position.set(cx + .1 - .05 * k, .52, cz + .32 - .18 * k); C.e31.rotation.y = .2;
      const k2 = ss(seg(t, 5.2, 7.6)); S.rcase.position.set(2.15 + .1 * k2, .52, S.z0 + .85 + .2 * k2); pose(S.clerk, { arm: [-.6 * ss(seg(t, 4.6, 6)), -.6 * ss(seg(t, 2.5, 4))] }); S.mcard.position.y = -5; } },
  { show: [], light: ['table', 'charts'],
    cam: keys([[0, Z('charts', -.4, 6.6, 11.0), Z('charts', -.6, .9, .6), 50], [1, Z('charts', .2, 6.4, 10.2), Z('charts', -.4, .9, .6), 50]]),
    enter(C) { const a = block(1.6, 1, 1.6, '#3f5f93', null), b = block(1.6, 1, 1.6, '#3f5f93', null); C.add(place(a, Z('charts', -1.4))); C.add(place(b, Z('charts', 1.4))); C.s32 = { a, b, c: [] };
      C.add(flat(label('≈2.2M · DEC 31, 2006', { size: 90, weight: 700, ppu: 300, track: 3 }), Z('charts', -1.4, .02, 1.35))); C.add(flat(label('≈3M · APR 1, 2007', { size: 90, weight: 700, ppu: 300, track: 3 }), Z('charts', 1.4, .02, 1.35)));
      C.add(flat(label('ONLINE SUBSCRIBERS · FORM 10-K FY2006; Q1 2007 RESULTS RELEASE', { size: 52, weight: 600, ppu: 300, track: 3 }), Z('charts', 0, .02, 2.0)));
      for (let i = 0; i < 6; i++) { const c = block(.9, .26, .9, '#5b616a', i === 0 ? 'COSTS' : null, { size: 60 }); C.add(place(c, Z('charts', -3.6 + (i % 2) * .95, Math.floor(i / 2) * .27, -1.6))); C.s32.c.push(c); } },
    update(u, t, C) { C.s32.a.scale.y = Math.max(.001, eo(seg(t, .5, 2.6)) * 2.2); C.s32.b.scale.y = Math.max(.001, eo(seg(t, 2.6, 4.6)) * 3.0); C.s32.c.forEach((c, i) => { const k = eo(seg(t, 4.8 + i * .7, 5.6 + i * .7)); c.visible = k > 0; c.position.y = Math.floor(i / 2) * .27 + (1 - k) * 1.5; }); } },

  // ———————————— ACT 05 · THE TRAP ————————————
  { show: [], light: ['table', 'charts'],
    cam: keys([[0, Z('charts', 0, 6.6, 11.2), Z('charts', 0, .7, 1.0), 50], [1, Z('charts', 0, 6.2, 10.4), Z('charts', 0, .6, 1.0), 50]]),
    enter(C) { const a = block(1.6, 3.0, 1.6, '#3f5f93', null); C.add(place(a, Z('charts', -1.8))); C.add(flat(label('SUBSCRIBERS UP', { size: 90, weight: 700, ppu: 300, track: 4 }), Z('charts', -1.8, .02, 1.35)));
      const l = block(1.6, 1, 1.6, PAL.red, null); C.add(place(l, Z('charts', 1.8))); C.s33 = l; C.add(flat(label('NET LOSS, Q1 2007: $46.4M\n(COMPANY-WIDE)', { size: 80, weight: 700, ppu: 300, track: 3 }), Z('charts', 1.8, .02, 1.45)));
      C.add(flat(label('ALSO: AN INCREMENTAL $35M TOTAL ACCESS AD CAMPAIGN · SOURCE: Q1 2007 RESULTS RELEASE', { size: 50, weight: 600, ppu: 300, track: 2 }), Z('charts', 0, .02, 2.2))); },
    update(u, t, C) { const k = eo(seg(t, 2, 5)); C.s33.position.y = -1.2 * k; C.s33.scale.y = 1.2; } },
  { show: [], light: ['table', 'charts'],
    cam: keys([[0, Z('charts', 1.6, 8.0, 10.2), Z('charts', 1.4, .2, 1.0), 50], [1, Z('charts', 1.9, 7.4, 9.4), Z('charts', 1.6, .2, 1.0), 50]]),
    enter(C) { C.g34 = [gear(1.3, 14, '#3f5f93'), gear(1.0, 11, '#a8393f'), gear(1.1, 12, '#8a9097')]; [[-1.6, 0], [.75, .25], [3.6, .1]].forEach(([x, z], i) => C.add(place(C.g34[i], Z('charts', x, .05, z))));
      C.g34[2].children[0].material.transparent = true; C.g34[2].children[0].material.opacity = .45;
      [['RETAIL', -1.6], ['MAIL', .75], ['STREAMING', 3.6]].forEach(([s, x]) => C.add(flat(label(s, { size: 100, weight: 700, track: 8, ppu: 300 }), Z('charts', x, .02, 1.8))));
      C.add(flat(label('NEXT INDUSTRY SHIFT · NOT YET A BLOCKBUSTER SYSTEM', { size: 52, weight: 600, ppu: 300, track: 2 }), Z('charts', 3.6, .02, 2.35))); },
    update(u, t, C) { C.g34[0].rotation.y = t * .25; C.g34[1].rotation.y = -t * .25 * 14 / 11 + .1; C.g34[2].rotation.y = t * .05 * ss(seg(t, 4, 9)); C.g34[2].children[0].material.opacity = .25 + .5 * ss(seg(t, 3, 8)); } },
  { show: [], light: ['table', 'docs'], dof: 1.3, title: 'JANUARY 2007',
    cam: keys([[0, Z('docs', -.8, 5.6, 4.0), Z('docs', -.1, 0, 0), 85], [1, Z('docs', .5, 5.0, 3.4), Z('docs', .1, 0, 0), 85]]),
    enter(C) { C.add(flat(summary({ kicker: '16 JAN 2007', title: 'NETFLIX: INSTANT VIEWING', body: 'Netflix announces that subscribers can watch movies and TV episodes instantly on personal computers, starting with about 1,000 titles, at no extra charge to their plan.', cite: 'Netflix announcement, 16 January 2007, and contemporary press reports. Summary, not quoted wording.', w: 3.0, h: 1.9, seed: 78, tagCol: PAL.nred }), Z('docs', 0, .02, -.1), .02)); } },
  { show: ['desk'], light: ['window', 'desk'], screen: 'play', dof: 1.2,
    cam: keys([[0, Z('desk', 2.6, 1.9, .9), Z('desk', -.3, 1.25, -1.2), 50], [1, Z('desk', 2.2, 1.85, .5), Z('desk', -.3, 1.3, -1.25), 50]]),
    enter(C) { C.desk.viewer.visible = true; pose(C.desk.viewer, { sit: .7, arm: [-.9, -.2] }); C.desk.viewer.position.y = -.2; },
    leave(C) { C.desk.viewer.visible = false; } },
  { show: [], light: ['table', 'charts'],
    cam: keys([[0, Z('charts', -2.0, 8.6, 11.4), Z('charts', -1.0, .2, .4), 50], [1, Z('charts', 2.0, 8.6, 11.4), Z('charts', 1.0, .2, .4), 50]]),
    enter(C) { const lanes = [['DVD BY MAIL', -3.2, PAL.nred], ['RETAIL STORES', 0, PAL.blue], ['STREAMING', 3.2, '#77828B']];
      lanes.forEach(([s, x, col], i) => { C.add(flat(sheet(2.8, 3.2, (g, w, h) => { g.strokeStyle = col; g.lineWidth = 10; g.strokeRect(10, 10, w - 20, h - 20); }, { ppu: 120, curl: 0, seed: 80 + i }), Z('charts', x, .02, 0))); C.add(flat(label(s, { size: 100, weight: 700, track: 6, ppu: 300 }), Z('charts', x, .03, 1.2))); });
      const env = mailer(); env.scale.setScalar(.6); C.add(flat(env, Z('charts', -3.2, .04, -.3), .2));
      const st = new THREE.Group(); box(1.4, .55, .9, M.white, 0, 0, 0, st); box(1.45, .16, .12, M.blue, 0, .45, .45, st); C.add(place(st, Z('charts', 0, .02, -.4)));
      const mon = new THREE.Group(); box(.9, .7, .7, M.beige, 0, .05, 0, mon); box(.7, .5, .02, new THREE.MeshBasicMaterial({ color: '#4f7fbf' }), 0, .15, .36, mon); C.add(place(mon, Z('charts', 3.2, .02, -.4))); } },
  { show: ['net'], light: ['table', 'net'],
    cam: keys([[0, Z('net', -2, 7.5, 9.5), Z('net', 0, 1.2, 0), 35], [1, Z('net', 1, 6.5, 8.0), Z('net', 0, 1.2, 0), 35]]),
    enter(C) { C.f38 = []; ['FISCAL 2005', 'FISCAL 2006', 'FISCAL 2007', 'FISCAL 2008', 'FISCAL 2009'].forEach((y, i) => { const s = sheet(2.4, 3.1, (g, w, h) => { g.fillStyle = PAL.ink; g.textAlign = 'center'; g.font = `600 ${h * .03}px "Newsreader"`; g.fillText('UNITED STATES SECURITIES AND EXCHANGE COMMISSION', w / 2, h * .1); g.font = `700 ${h * .07}px "Newsreader"`; g.fillText('FORM 10-K', w / 2, h * .22); g.font = `600 ${h * .045}px "Newsreader"`; g.fillText('BLOCKBUSTER INC.', w / 2, h * .31); g.fillText(y.toUpperCase(), w / 2, h * .37); g.font = `500 ${h * .025}px "Plex Mono"`; g.fillText('COVER ONLY · CONTENTS NOT REPRODUCED', w / 2, h * .93); }, { ppu: 400, seed: 90 + i, curl: .05 }); C.add(s); C.f38.push(s); }); },
    update(u, t, C) { C.net.set(C.net.MAX, 1); C.f38.forEach((s, i) => { const k = eo(seg(t, .6 + i * 1.4, 1.8 + i * 1.4)); s.visible = k > 0; s.position.set(ZONE.net[0] - 3 + i * 1.5, 1.25 + .02 * i + (1 - k) * 3, ZONE.net[1] - 1.2 + i * .5); s.rotation.set(0, -.2 + i * .12, 0); }); } },
  { show: ['net'], light: ['table', 'net'],
    cam: keys([[0, Z('net', -6, 4.4, 10.5), Z('net', -2, 1.8, 0), 35], [1, Z('net', -4.6, 3.8, 9.2), Z('net', -2, 1.6, 0), 35]]),
    enter(C) { C.b39 = [['DEBT', -5.4], ['LIQUIDITY', -2.2], ['OBLIGATIONS', 1.0]].map(([s, x]) => { const b = block(2.6, 1.3, 2.6, '#2a2e33', s, { size: 110, tcol: PAL.ivory, lbg: '#2a2e33', metal: .3, rough: .5, ly: .45 }); C.add(place(b, Z('net', x, 6, -.5))); return b; });
      C.add(flat(label('INDEBTEDNESS “NEARLY $1 BILLION” · BLOCKBUSTER, 23 SEPT 2010', { size: 70, weight: 700, ppu: 300, track: 3 }), Z('net', -2.2, 1.23, 3.6))); },
    update(u, t, C) { C.net.set(C.net.MAX, 1); C.b39.forEach((b, i) => { const k = Math.min(1, Math.pow(seg(t, 1 + i * 1.2, 2.6 + i * 1.2), 2)); b.position.y = lerp(6, 1.2, k) + (k >= 1 ? 0 : 0); }); } },
  { show: ['net'], light: ['dusk', 'net'],
    cam: keys([[0, Z('net', 0, 8.5, 10.5), Z('net', 0, 1.2, 0), 35], [1, Z('net', 0, 10.5, 9.0), Z('net', 0, 1.2, 0), 35]]),
    enter(C) { C.add(flat(label('METAPHOR · NOT A LITERAL CLOSURE SEQUENCE', { size: 60, weight: 600, ppu: 300, track: 3 }), Z('net', 3.6, 1.23, 4.1))); },
    update(u, t, C) { C.net.set(C.net.MAX, 1, i => { const R = hash(i * 7.3 + 1); return clamp(1 - seg(t, .8 + R * 8.5, 1.1 + R * 8.5) * (R < .88 ? 1 : 0)); }); } },

  // ———————————— ACT 06 · THE VERDICT ————————————
  { show: [], light: ['table', 'docs'], dof: 1.3, title: 'SEPTEMBER 23, 2010',
    cam: keys([[0, Z('docs', -.4, 6.2, 3.8), Z('docs', 0, 0, -.3), 50], [1, Z('docs', .2, 3.6, 2.1), Z('docs', 0, 0, -.3), 50]]),
    enter(C) { C.add(flat(excerpt({ mast: ['UNITED STATES SECURITIES AND EXCHANGE COMMISSION', 'BLOCKBUSTER INC.'], sub: 'FORM 8-K · ITEM 1.03', passage: 'On September 23, 2010, the Blockbuster Inc. (the “Company”) and certain of its domestic subsidiaries [filed voluntary petitions for relief under chapter 11 of the United States Bankruptcy Code].', cite: 'Blockbuster Inc., current report on Form 8-K, date of report September 23, 2010. SEC EDGAR accession 0001193125-10-215765. Bracketed words are an editorial summary of the remainder of the sentence.', hi: true, seed: 81 }), Z('docs', 0, .02, -.2), .02)); } },
  { show: ['store'], light: ['empty', 'store'], fixed: true,
    cam: keys([[0, Z('store', -2.4, .56, -1.1), Z('store', .2, .45, -2.9), 35], [1, Z('store', -2.4, .56, -1.1), Z('store', .2, .45, -2.9), 35]]),
    enter(C) { C.store.people.forEach(F => F.visible = false); C.store.clerk.visible = false; C.store.roof.visible = true; }, leave(C) { C.store.clerk.visible = true; },
    update(u, t, C) { C.store.lights.forEach((p, i) => p.material.emissiveIntensity = i === 3 ? (hash(Math.floor(t * 9)) > .78 ? .15 : 1.1) : 1.1); } },
  { show: ['board'], light: ['table', 'docs'],
    cam: keys([[0, Z('board', 0, 3.4, 6.2), Z('board', 0, .7, 0), 35], [.45, Z('board', 0, 3.4, 6.2), Z('board', 0, .7, 0), 35], [1, Z('docs', 0, 3.2, 3.5), Z('docs', 0, 0, -.3), 50]]),
    enter(C) { C.board.folder.visible = true; C.board.folder.position.set(0, .81, .3); C.add(flat(RANDOLPH(), Z('docs', -1.3, .02, 0), .05)); C.add(flat(ANTIOCO(), Z('docs', 1.4, .02, -.05), -.04)); C.add(flat(plate([['$50,000,000', .5, .62, PAL.ivory], ['DISPUTED', 0, .85, PAL.red, `700 ${1.2 * 420 * .14}px "Plex Cond"`, 10]], { w: 2.6, h: 1.2, seed: 77 }), Z('docs', 0, .03, 1.4))); } },
  { show: [], light: ['spot', 'felt'], hypo: true,
    cam: keys([[0, Z('felt', -1.2, 9.6, 7.0), Z('felt', -.4, 0, .2), 35], [1, Z('felt', 0, 9.2, 6.0), Z('felt', 0, 0, .1), 35]]),
    enter(C) { C.add(flat(label('SEPT 2000\nTHE MEETING', { size: 90, weight: 700, ppu: 300, track: 4 }), Z('felt', -4.4, .06, 0)));
      const O = [['ACQUISITION, THEN FAILURE', -2.2], ['DIFFERENT TERMS, DIFFERENT OUTCOME', 0], ['A SUCCESSFUL PARTNERSHIP', 2.2]]; C.h44 = [];
      O.forEach(([s, z], i) => { const strip = sheet(5, .1, (g, w, h) => { g.fillStyle = PAL.ivory; for (let x = 0; x < w; x += 60) g.fillRect(x, 0, 36, h); }, { base: false, ppu: 200, curl: 0 }); const a = Math.atan2(z * .9, 4.2); strip.position.set(ZONE.felt[0] - 1.3, .06, ZONE.felt[1] + z * .45); strip.rotation.y = -a; C.add(strip); C.h44.push(strip);
        const c = label(s + '\nHYPOTHETICAL · UNPROVEN', { size: 70, weight: 700, ppu: 300, track: 3, seed: 85 + i }); C.add(flat(c, Z('felt', 2.6, .06, z * .95))); C.h44.push(c); }); },
    update(u, t, C) { C.h44.forEach((o, i) => { o.visible = t > 1 + Math.floor(i / 2) * 1.2; }); } },
  { show: [], light: ['table', 'charts'],
    cam: keys([[0, Z('charts', 0, 6.5, 7.5), Z('charts', 0, .4, 0), 35], [1, Z('charts', 0, 5.5, 6.2), Z('charts', 0, .4, 0), 35]]),
    enter(C) { C.b45 = [['LEGACY ECONOMICS', -Math.PI / 2], ['TRANSITION COSTS', Math.PI / 6], ['FINANCIAL CONSTRAINTS', Math.PI * 5 / 6]].map(([s, a], i) => { const b = block(3.2, 1.1, 1.6, ['#3f5f93', '#a8393f', '#3a3f45'][i], s, { size: 76, top: true }); b.userData.a = a; C.add(b); return b; });
      C.add(flat(label('INTERPRETIVE SYNTHESIS', { size: 60, weight: 600, ppu: 300, track: 6 }), Z('charts', 0, .02, 3.4))); },
    update(u, t, C) { C.b45.forEach(b => { const a = b.userData.a, r = lerp(4.2, 1.75, eo(seg(t, .5, 6))) + .03 * Math.sin(t * 9) * seg(t, 6, 7); b.position.set(ZONE.charts[0] + Math.cos(a) * r, 0, ZONE.charts[1] - Math.sin(a) * r); b.rotation.y = a + Math.PI / 2; }); } },
  { show: ['dallas', 'plaza', 'board', 'store', 'plan', 'net', 'mail', 'desk'], light: ['wide', 'center'],
    cam: keys([[0, [2, 14, 22], [0, 0, -1], 35], [1, [0, 46, 14], [0, 0, -1], 35]]),
    enter(C) { C.add(flat(RANDOLPH(), Z('docs', -1.3, .02, 0), .05)); C.add(flat(ANTIOCO(), Z('docs', 1.4, .02, -.05), -.04)); C.add(flat(FIFTY(), Z('felt', 0, .05, 0))); C.add(flat(receipt(), Z('charts', -4, .02, 0), .03)); C.add(flat(mailer(), Z('docs', 0, .02, 5), .1));
      [[-1.2, 2.76, '#3f5f93'], [1.2, 3.0, PAL.red]].forEach(([x, h, c]) => { const b = block(1.2, h, 1.2, c, null); C.add(place(b, Z('charts', x))); });
      C.net.set(C.net.MAX, 1, i => hash(i * 7.3 + 1) < .88 ? 0 : 1); C.store.people.forEach(F => F.visible = false); } },
  { black: true, fadeFrom: 45 },
  { black: true },
];
export let C_ = null; export const bindC = c => { C_ = c; };
