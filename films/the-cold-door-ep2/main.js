// The Cold Door: timeline from story.js, shots, acting, portal jumps, subtitles with speaker pills, world tags, title and end card.
import { clamp, lerp, seg, ss, eo, ei, eio, back, spring, hash, TAU } from '/core/lib.js';
import { W, H, INK, init, frame, g, push, pop, translate, rotate, scale, shape, fillOnly, stroke, ell, arc, rr, rect, spline, dot, text, S, reset, screenRect } from './toon.js';
import { hal, dotChar, curd, basket, C } from './chars.js';
import { WORLDS, INSERTS, FLOOR, fridge, portal, swirlWipe, PORTAL } from './worlds.js';
import { SEQ, CAST, TARGET as TGT, TITLE, END } from './story.js';
import { casinoPieces } from './casino.js';

const CV = document.getElementById('c'); init(CV);
await Promise.all(['800 50px "Baloo 2"', '40px VT323', '100px Shrikhand', '60px "Caveat Brush"'].map(f => document.fonts.load(f)));
const J = async f => { try { const r = await fetch(f); if (r.ok) return await r.json(); } catch (e) { } return null; };
const DURS = (await J('voices/dur.json')) || {}, LIPS = (await J('voices/lips.json')) || {};
const q = t => Math.floor(t * 12 + 1e-6) / 12;   // characters on twos

// ---------- timeline: lines are timed by their audio; the gaps are scaled so the film lands on 10:00 ----------
const TARGET = TGT, WIPE = .9, FASTWIPE = .35;
function layout(gapK) {
  const T = []; let t = 0, world = 'home', tag = '', shot = 'two', last = null;
  for (const e of SEQ) {
    if (e[0] === 'W') { const fast = e[3]?.fast; if (T.length) t += fast ? FASTWIPE : WIPE; world = e[1]; tag = e[2]; T.push({ k: 'W', t, world, tag, fast }); shot = 'two'; continue; }
    if (e[0] === 'S') { shot = e[1]; continue; }
    if (e[0] === 'A') { const o = e[3] || {}; if (o.shot) shot = o.shot; T.push({ k: 'A', t, d: e[1], act: e[2], world, tag, shot }); t += e[1]; continue; }
    const [, who, id, txt, o = {}] = e; if (o.shot) shot = o.shot;
    const d = DURS[id] ?? txt.length * .065, cut = o.cut ? .22 : 0;
    const ev = { k: 'L', t, d, who, id, txt, act: o.act, world, tag, shot, cut: o.cut };
    T.push(ev); t += d - cut + (o.cut ? 0 : .32 * gapK + (o.pause || 0) * Math.min(1.6, gapK));
  }
  return { T, end: t };
}
let gk = 1, L0 = layout(gk); for (let i = 0; i < 20; i++) { gk *= (TARGET - (L0.end - (L0.T.filter(x => x.k !== 'A').length * 0))) > 0 ? 1 + (TARGET - L0.end) / 400 : 1 + (TARGET - L0.end) / 400; gk = clamp(gk, .3, 6); L0 = layout(gk); if (Math.abs(L0.end - TARGET) < .3) break; }
const TL = L0.T, DUR = TARGET;
// segments = consecutive spans that share a shot/world (each item lasts until the next one)
TL.forEach((e, i) => { e.end = i + 1 < TL.length ? TL[i + 1].t : DUR; });
const at = t => { let lo = 0; for (let i = 0; i < TL.length; i++) if (TL[i].t <= t) lo = i; return TL[lo]; };
const jumps = TL.filter(e => e.k === 'W');
const lineAt = (t, who) => TL.find(e => e.k === 'L' && (!who || e.who === who) && t >= e.t && t < e.t + e.d);
const actOn = (t, name) => TL.filter(e => e.act === name && e.t <= t);
const firstAct = name => TL.find(e => e.act === name);

// ---------- acting ----------
function talk(who, t) {
  const L = lineAt(q(t), who); if (!L) return { o: 0, w: 1, talking: false };
  const k = Math.floor((q(t) - L.t) * 24), lp = LIPS[L.id]; let o = lp ? (lp.o[k] ?? 0) : .5, b = lp ? (lp.b[k] ?? .5) : .5;
  if (L.act === 'scream') o = Math.min(1, o * 1.7);
  return { o, w: .8 + .45 * b - .2 * o, talking: true, L };
}
const blinkK = (t, seed) => { const k = Math.floor(t * 12), c = Math.floor(k / 40); return hash(c * 7.1 + seed) > .35 && (k % 40) < 2; };
// basket contents grow as the film goes on
const ITEM_AT = [['getBiscuits', 'biscuits'], ['fillBasket', 'candle'], ['chicken', 'chicken'], ['secondBasket', 'tin'], ['panic', 'pickles', 'd22'], ['baguette', 'baguette'], ['endcaps', 'chips'], ['endcaps', 'cereal']];
function itemsAt(t) { const out = []; for (const [a, it, id] of ITEM_AT) { const e = id ? TL.find(x => x.id === id) : firstAct(a); if (e && t >= e.t + .5) out.push(it); } return out; }

function actors(t, E) {
  const tq = q(t), hm = talk('H', t), dm = talk('D', t), act = E.act || '';
  const Dline = lineAt(t, 'D'), Hline = lineAt(t, 'H');
  const dAct = (Dline && Dline.act) || (E.who === 'D' ? act : '') || '', hAct = (Hline && Hline.act) || '';
  const panic = ['panic', 'scream'].includes(dAct) ? 1 : 0;
  const D = { x: 720, y: FLOOR, s: 1, face: 1, look: hm.talking ? [.7, -.1] : [.4, 0], lid: .1, brow: -.3, blink: blinkK(t, 3), mouth: { o: dm.o, w: dm.w, sm: .1 }, arms: 'rest', basket: false, items: [], sq: 1 + .01 * Math.sin(tq * 3.1), tilt: dm.talking ? (dm.o - .3) * .08 : 0 };
  const Hh = { x: 1180, y: FLOOR, s: 1, face: -1, look: dm.talking ? [.7, .05] : [.2, .1], lid: .55, brow: 0, blink: blinkK(t, 9), mouth: { o: hm.o, w: hm.w, sm: -.35 }, arms: 'rest', sq: 1 + .008 * Math.sin(tq * 2.3), tilt: hm.talking ? (hm.o - .3) * .05 : .04 };
  if (panic) { const a = 4 + 4 * panic; D.jit = (hash(Math.floor(t * 12)) - .5) * a * 2; D.ejit = (hash(Math.floor(t * 12) + 5) - .5) * 4; D.wide = 1.15; D.brow = -1; D.arms = 'up'; D.sweat = 1; D.mouth.sm = -.3; }
  const ds = { hope: () => { D.arms = 'up'; D.mouth.sm = .9; D.brow = .3; }, deflate: () => { D.lid = .5; D.mouth.sm = -.6; D.arms = 'rest'; D.look = [0, .5]; }, blank: () => { D.wide = 1.2; D.lid = 0; D.look = [0, 0]; D.mouth.sm = 0; },
    write: () => { D.arms = 'write'; D.look = [.3, .6]; D.holdR = (x, y) => { push(); translate(x + 30, y - 20); rotate(-.2); shape(rr(-50, -34, 100, 68, 6), { fill: '#FFFDF5', lw: 5 }); fillOnly(rect(-50, -34, 100, 12), C.apron); pop(); }; },
    beg: () => { D.arms = 'beg'; D.brow = -1; D.wide = 1.1; }, strain: () => { D.arms = 'strain'; D.sq = .9; D.brow = -1; D.sweat = 1; D.mouth.skew = .5; }, twitch: () => { D.twitch = Math.floor(t * 12) % 4 < 2; D.lid = .25; D.look = [.7, 0]; },
    pointFridge: () => { D.arms = 'point'; }, turnBack: () => { D.face = -1; }, cold: () => { D.look = [.6, 0]; } };
  if (ds[dAct]) ds[dAct]();
  if (E.act === 'lookBack') { D.face = -1; D.wide = 1.2; D.look = [-.6, 0]; }
  if (E.act === 'sigh') { Hh.lid = .8; Hh.sq = .97; }
  if (hAct === 'cold' || dAct === 'cold') { Hh.lid = .6; }
  if (/openPortal|rollFridge/.test(hAct)) Hh.arms = 'point';
  if (hm.talking && (Math.floor(hm.L.t * 3) % 4 === 0)) Hh.arms = 'shrug';
  if (E.k === 'L' && E.who === 'H' && /pointFridge|saunders|cullen|float|bottles|graph/.test(E.act || '')) Hh.arms = 'point';
  return { D, Hh };
}

// ---------- shots ----------
function cam(cx, cy, z, shake = 0, t = 0) { reset(); translate(W / 2, H / 2); if (shake) { const f = Math.floor(t * 24); translate((hash(f) - .5) * shake * 2, (hash(f + 77) - .5) * shake * 2); } scale(z); translate(-cx, -cy); }
function shotCam(E, t) {
  const u = t - E.t, sh = E.shot, push_ = 1 + .03 * clamp(u / 6);
  const scream = E.act === 'scream' && E.k === 'L' ? 9 : 0, cold = E.act === 'cold';
  if (sh === 'two') return cam(950, 640, (cold ? 1.0 + .06 * clamp(u / 4) : .98) * push_);
  if (sh === 'wide') return cam(1100, 560, .78 * push_);
  if (sh === 'cuH') return cam(1180 + 20, 290, 2.05 * push_, 0, t);
  if (sh === 'cuD') return cam(720 - 10, 470, 2.25 * push_, scream, t);
  if (sh === 'track') return cam(950 + u * 18, 620, 1.0);
  if (sh === 'mont') return cam(960, 600, 1.0);
  return cam(960, 560, 1);
}

// ---------- overlays ----------
function subs(t) {
  const cur = TL.filter(e => e.k === 'L' && t >= e.t - .05 && t < e.t + Math.max(1.4, e.d + .5) && t < (e.cutAt ?? 1e9));
  const live = cur.slice(-2);
  live.forEach((e, i) => {
    const old = i < live.length - 1, nxtW = jumps.find(j => j.t > e.t); if (nxtW && t >= nxtW.t - .05) return;
    g.setTransform(1, 0, 0, 1, 0, 0); g.font = '800 50px "Baloo 2"'; g.textAlign = 'left'; g.textBaseline = 'middle'; g.lineJoin = 'round';
    const words = e.txt.split(' '), lines = []; let s = ''; for (const w of words) { const tr = s ? s + ' ' + w : w; if (g.measureText(tr).width > 1300 && s) { lines.push(s); s = w; } else s = tr; } lines.push(s);
    const y0 = 1080 - 70 - (lines.length - 1) * 58 - (old ? 120 : 0), cw = Math.max(...lines.map(l => g.measureText(l).width)), x0 = 960 - cw / 2;
    g.globalAlpha = old ? .7 : 1;
    const col = CAST[e.who].col; g.font = '800 30px "Baloo 2"'; const pw = g.measureText(CAST[e.who].name).width + 30;
    g.fillStyle = col; g.beginPath(); g.roundRect(x0 - pw - 22, y0 - 24, pw, 46, 23); g.fill(); g.lineWidth = 5; g.strokeStyle = INK; g.stroke();
    g.fillStyle = '#fff'; g.fillText(CAST[e.who].name, x0 - pw - 7, y0 + 1);
    g.font = '800 50px "Baloo 2"';
    lines.forEach((l, k) => { g.lineWidth = 11; g.strokeStyle = INK; g.strokeText(l, x0, y0 + k * 58); g.fillStyle = '#fff'; g.fillText(l, x0, y0 + k * 58); });
    g.globalAlpha = 1;
  });
}
function worldTag(t, E) {
  const j = [...jumps].reverse().find(x => x.t <= t); if (!j || E.shot === 'title' || E.shot === 'end') return;
  const u = t - j.t - (j.fast ? .1 : .35); if (u < 0 || u > (j.fast ? 1.2 : 4.5)) return;
  const pal = WORLDS[j.world].pal, txt = j.tag.slice(0, Math.floor(clamp(u / 1.2) * j.tag.length)) + (Math.floor(t * 4) % 2 ? '_' : ' ');
  g.setTransform(1, 0, 0, 1, 0, 0); g.font = '44px VT323'; const w = g.measureText(j.tag + '_').width + 40;
  g.fillStyle = INK; g.fillRect(40, 40, w, 60); g.fillStyle = pal[1] === '#FFFFFF' ? pal[0] : pal[1]; g.fillRect(46, 46, w - 12, 48);
  g.fillStyle = INK; g.textBaseline = 'middle'; g.textAlign = 'left'; g.fillText('> ' + txt, 58, 71);
}
function titleCard(u, d, t) {
  WORLDS.home.draw(t); screenRect('rgba(30,39,64,.55)');
  g.setTransform(1, 0, 0, 1, 0, 0); g.save(); g.translate(960, 500);
  const step = Math.floor(u * 12) / 12, k = back(clamp(step / .4), 2), out = ei(seg(u, d - .3, d));
  g.scale(k * (1 - out), k * (1 - out)); g.rotate(-.04);
  g.strokeStyle = '#7FC8E8'; g.lineWidth = 10; g.beginPath(); g.ellipse(0, 0, 760, 200, -.12, 0, TAU); g.stroke();
  const a = u * 2.2, cx = Math.cos(a) * 760, cy = Math.sin(a) * 200; g.save(); g.translate(cx * Math.cos(-.12) - cy * Math.sin(-.12), cx * Math.sin(-.12) + cy * Math.cos(-.12)); g.fillStyle = '#fff'; g.fillRect(-26, -46, 52, 70); g.fillStyle = '#3B6FD6'; g.beginPath(); g.moveTo(-26, -46); g.lineTo(0, -70); g.lineTo(26, -46); g.fill(); g.lineWidth = 5; g.strokeStyle = INK; g.strokeRect(-26, -46, 52, 70); g.restore();
  g.font = '120px Shrikhand'; g.textAlign = 'center'; g.textBaseline = 'middle'; g.lineJoin = 'round';
  for (const [l, y] of [[TITLE[0], -70], [TITLE[1], 70]]) { g.fillStyle = C.apron; g.fillText(l, 10, y + 10); g.lineWidth = 14; g.strokeStyle = INK; g.strokeText(l, 0, y); g.fillStyle = '#F7EFD8'; g.fillText(l, 0, y); }
  g.restore();
}
function endCard(u, t) {
  screenRect('#1E2740');
  reset(); translate(960, 470); portal(0, 0, .5 + .02 * Math.sin(t * 2), t, { rx: 200, ry: 280 });
  g.setTransform(1, 0, 0, 1, 0, 0); g.textAlign = 'center'; g.textBaseline = 'middle'; g.lineJoin = 'round';
  g.font = '96px Shrikhand'; g.lineWidth = 12; g.strokeStyle = INK; g.strokeText('THE COLD DOOR', 960, 160); g.fillStyle = '#F7EFD8'; g.fillText('THE COLD DOOR', 960, 160);
  g.font = '44px VT323'; g.fillStyle = '#C7A6FF'; g.fillText(END.ep, 960, 245);
  g.font = '800 34px "Baloo 2"'; g.fillStyle = '#F7EFD8'; g.fillText(END.line, 960, 820);
  g.font = '600 24px "Baloo 2"'; g.fillStyle = 'rgba(247,239,216,.75)';
  ['Voices: Kokoro TTS (am_onyx, af_jessica) · Music & sound: synthesized', 'Inspired by adult-swim-era sci-fi sitcom cartoons · all characters original'].forEach((l, i) => g.fillText(l, 960, 900 + i * 36));
  reset(); translate(960, 470); curd(0, 120, .9 * back(seg(u, 2.5, 3.1), 2), { t, happy: 1, wave: 1 });
}

// ---------- world props & events per act ----------
function setPieces(E, t, A) {
  const w = E.world, P = A;
  // the Cold Door rides along on every jump (it's how they travel); open while a jump is near
  const nextJ = jumps.find(j => j.t > t), lastJ = [...jumps].reverse().find(j => j.t <= t);
  const opening = firstAct('openPortal'), fridgeX = 1560;
  let door = 0, pk = 0;
  if (w === 'home' && opening && t < jumps[1].t) { const rollK = firstAct('rollFridge'); const fx = rollK ? lerp(2300, fridgeX, eo(seg(t, rollK.t, rollK.t + 1.4))) : fridgeX; door = ss(seg(t, opening.t + .3, opening.t + .8)); pk = popOpen(t - opening.t - .5); fridge(fx, FLOOR, { door, t }); if (pk > 0) portal(fx, FLOOR - 330, pk, t); return; }
  if (nextJ && t > nextJ.t - (nextJ.fast ? .3 : 1.6)) { pk = popOpen(t - (nextJ.t - (nextJ.fast ? .3 : 1.6))); }
  if (lastJ && t < lastJ.t + (lastJ.fast ? .4 : 1.2)) pk = Math.max(pk, 1 - ss(seg(t, lastJ.t + .2, lastJ.t + (lastJ.fast ? .4 : 1.2))));
  if (!WORLDS[w].city) { fridge(fridgeX, FLOOR, { door: pk > 0 ? 1 : 0, t }); if (pk > 0) portal(fridgeX, FLOOR - 330, pk, t); }
  casinoPieces(E, t, firstAct);
}
const popOpen = x => x <= 0 ? 0 : back(clamp(x / .32), 1.4);

// ---------- render ----------
window.render = function (t) {
  t = clamp(t, 0, DUR - 1e-4); frame(t);
  const E = at(t), u = t - E.t;
  g.setTransform(1, 0, 0, 1, 0, 0); g.fillStyle = '#000'; g.fillRect(0, 0, W, H);
  if (E.shot === 'title') { titleCard(u, E.d, t); return; }
  if (E.shot === 'end') { endCard(u, t); return; }
  const A = actors(t, E);
  if (E.shot && E.shot.startsWith('ins:')) {
    const key = E.shot.slice(4); reset(); translate(W / 2, H / 2); scale(1 + .04 * clamp(u / 4));
    INSERTS[key](t, u);
  } else {
    shotCam(E, t);
    WORLDS[E.world].draw(t);
    setPieces(E, t, A);
    if (E.shot === 'mont') { const cx = ['london', 'paris', 'sydney'].includes(E.world) ? 700 : 1260; dotChar({ ...A.D, x: cx - 260, face: 1, look: [.8, 0], arms: E.who === 'D' ? 'point' : 'rest' }); hal({ ...A.Hh, x: cx + 300 }); }
    else {
      const walk = E.shot === 'track' ? q(t) * 9 : null; if (walk != null) { A.D.walk = walk; A.Hh.walk = walk + 1; A.D.x += u * 18; A.Hh.x += u * 18; }
      hal(A.Hh); dotChar(A.D);
      if (E.world !== 'zone') { const cy = FLOOR; curd(A.D.x - 120, cy, .55, { t, look: [.5, -.4], blink: blinkK(t, 21), happy: 0, sq: 1 - .06 * Math.abs(Math.sin(q(t) * 5)) }); }
    }
    // the portal's flat wash while it's open
    const nextJ = jumps.find(j => j.t > t); if (nextJ && t > nextJ.t - .9) screenRect(PORTAL.wash);
  }
  // jump: rush zoom then swirl wipe around each cut
  for (const j of jumps) { const hw = j.fast ? .18 : .45, d = Math.abs(t - j.t); if (j.t > 0 && d < hw) swirlWipe(1 - d / hw, t); }
  worldTag(t, E);
  subs(t);
  if (t < .8) screenRect(`rgba(0,0,0,${1 - t / .8})`);
  if (t > DUR - 1.2) screenRect(`rgba(0,0,0,${ss(seg(t, DUR - 1.2, DUR - .1))})`);
};

// ---------- events for sound and music ----------
const EV = [];
for (const e of TL) {
  if (e.k === 'L') EV.push({ t: e.t, type: 'vo', id: e.id, who: e.who, d: e.d });
  if (e.k === 'W') EV.push({ t: e.t, type: 'jump', world: e.world, fast: !!e.fast });
  if (e.act === 'cold') EV.push({ t: e.t + (e.d || 0), type: 'silence', d: 2.2 });
  if (e.act) EV.push({ t: e.t, type: 'act', name: e.act });
  if (e.shot === 'title') EV.push({ t: e.t, type: 'title' });
  if (e.shot === 'end') EV.push({ t: e.t, type: 'end' });
}
EV.sort((a, b) => a.t - b.t);
window.EV = EV; window.DUR = DUR; window.TL = TL.map(e => ({ k: e.k, t: +e.t.toFixed(3), d: e.d, id: e.id, world: e.world, shot: e.shot, act: e.act }));
window.render(0); window.READY = true;
