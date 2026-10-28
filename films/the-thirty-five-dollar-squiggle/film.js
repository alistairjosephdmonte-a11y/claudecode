// "The Thirty-Five Dollar Squiggle": a crayon picture book. One page per chapter, each drawn on live while the
// storyteller reads it, joined by real page turns; at the end the camera pulls back to the book on a desk (end.js).
// Timing comes from the narration: story.json (lines + pauses) × voice.json (measured line lengths), scaled to TARGET.
import { layer, clear, text, CAM, BOIL, W, H } from './crayon.js';
import { group, clearGroup } from './rig.js';
import { PAL } from './pal.js';
import { clamp, hash, ss } from '/core/lib.js';
import { endFrame } from './end.js';
import { PAGES } from './pages.js';
const K = PAL.crayon;
const STORY = await (await fetch('./story.json')).json();
const VD = await (await fetch('./voice.json')).json();

// —— timeline ——
const TURN = 1.3, END_LEN = 9.5, END_VOICE = 4.9;
const body = STORY.pages.filter(p => p.id !== 'end');
const lead = i => i === 0 ? 3.6 : 2.6;
function layout(k) {
  let t = 0; const out = [];
  body.forEach((p, i) => {
    const P = { id: p.id, t0: t, lines: [] };
    let c = t + (i ? TURN : 0) + lead(i) * k;
    p.lines.forEach(([id, text, pause]) => { P.lines.push({ id, text, t: c - P.t0, d: VD[id] }); c += VD[id] + (0.3 + pause) * k; });
    P.dur = c - P.t0 + 1.0 * k; t += P.dur; out.push(P);
  });
  return { pages: out, end: t };
}
const a = layout(1), b = layout(2), KS = clamp(1 + (STORY.target - END_LEN - a.end) / (b.end - a.end), 0.6, 2.5);
const TL = layout(KS);
window.TL = TL; window.KS = KS;
export const E0 = TL.end, DUR = +(E0 + END_LEN).toFixed(3);
const endLine = STORY.pages.find(p => p.id === 'end').lines[0];

// —— subtitles: the book's printed words ——
export const SUBS = [];
TL.pages.forEach(P => P.lines.forEach((L, i) => {
  const t0 = P.t0 + L.t - 0.1, nx = P.lines[i + 1];
  let t1 = Math.max(t0 + 1.8, P.t0 + L.t + L.d + 0.6);
  t1 = Math.min(t1, nx ? P.t0 + nx.t - 0.2 : P.t0 + P.dur - 0.15);
  SUBS.push({ t0, t1, text: L.text });
}));
SUBS.push({ t0: E0 + END_VOICE - 0.1, t1: E0 + END_VOICE + 2.4, text: endLine[1] });

// —— events for the mix ——
export const EV = [];
const ev = (t, type, o = {}) => EV.push({ t: +t.toFixed(3), type, ...o });
TL.pages.forEach((P, i) => {
  ev(P.t0, 'cue', { id: P.id, i, dur: P.dur });
  if (i) ev(P.t0, 'page', { dur: TURN });
  P.lines.forEach(L => ev(P.t0 + L.t, 'voice', { id: L.id, d: L.d }));
  const M = PAGES[P.id];
  (M.sfx ? M.sfx(ctxOf(P, 0)) : []).forEach(([t, type, o]) => ev(P.t0 + t, type, o || {}));
});
ev(E0, 'cue', { id: 'end', i: TL.pages.length, dur: END_LEN });
ev(E0 + END_VOICE, 'voice', { id: endLine[0], d: VD[endLine[0]] });
ev(E0 + 0.2, 'room'); ev(E0 + 2.6, 'page', { dur: 1.2 });
EV.sort((x, y) => x.t - y.t);

// per-page context handed to page drawings: local time, line starts/ends, progress helpers
function ctxOf(P, t) {
  const L = P.lines;
  return {
    t, dur: P.dur, turn: P.t0 > 0 ? TURN : 0,
    at: (i, o = 0) => L[Math.max(0, Math.min(L.length - 1, i))].t + o,
    end: (i, o = 0) => L[i].t + L[i].d + o,
    p: (a, b) => clamp((t - a) / (b - a)),
  };
}

// —— layers ——
export const S = { BG: { f: layer(), l: layer() }, G: group(), G2: group(), FX: layer(), WASH: layer(), WFX: layer() };
const SUBK = layer(), SUBT = layer();
const mk = () => { const c = document.createElement('canvas'); c.width = W; c.height = H; return { c, g: c.getContext('2d') }; };
const snapA = mk(), snapB = mk(), turnC = mk();
const glc = () => document.getElementById('gl');
const snap = P => { P.g.setTransform(1, 0, 0, 1, 0, 0); P.g.clearRect(0, 0, W, H); P.g.drawImage(glc(), 0, 0); };

function renderPage(comp, P, t, { subs = true, absT = 0, vig = 0.28 } = {}) {
  const i = TL.pages.indexOf(P), M = PAGES[P.id], c = ctxOf(P, t);
  const cam = M.cam ? M.cam(c) : [960, 540, 1];
  [CAM.x, CAM.y, CAM.s] = cam;
  clear(S.BG.f); clear(S.BG.l); clearGroup(S.G); clearGroup(S.G2); clear(S.FX); clear(S.WASH); clear(S.WFX); clear(SUBK); clear(SUBT);
  const o = M.draw(S, c) || {};
  if (subs) subTo(SUBK, SUBT, absT);
  comp.paperCam(i * 2600 + CAM.x * 0.6, 900 * (i % 3) + CAM.y * 0.6, CAM.s / 0.6);
  comp.begin(PAL.paper);
  comp.crayon(S.BG.f.c); comp.crayon(S.BG.l.c);
  const go = [hash(BOIL.step) * 300, hash(BOIL.step + 7) * 300];
  comp.group(S.G2, { goff: go });
  if (o.wash) comp.wash(S.WASH.c, { color: o.wash });
  comp.crayon(S.WFX.c, { goff: go });
  comp.group(S.G, { goff: go });
  comp.crayon(S.FX.c, { goff: go });
  comp.knock(SUBK.c); comp.crayon(SUBT.c);
  comp.finish({ vig });
}

export function frame(comp, t) {
  if (t >= E0) return endFrame(comp, 46 + (t - E0) * 0.6, { drawPage: (cm) => renderPage(cm, TL.pages[TL.pages.length - 1], TL.pages[TL.pages.length - 1].dur, { subs: false, vig: 0 }), subTo: (k, s) => subTo(k, s, t) });
  let i = TL.pages.length - 1; while (TL.pages[i].t0 > t) i--;
  const P = TL.pages[i], lt = t - P.t0;
  if (i > 0 && lt < TURN) {
    const Q = TL.pages[i - 1];
    renderPage(comp, Q, Q.dur, { subs: false }); snap(snapA);
    renderPage(comp, P, lt, { subs: false }); snap(snapB);
    turnPage(turnC.g, snapA.c, snapB.c, Math.PI * ss(lt / TURN));
    comp.paperCam(0, 0, 1); comp.begin(PAL.paper); comp.image(turnC.c); comp.finish({ vig: 0, emb: 0, lift: 0 });
    return;
  }
  renderPage(comp, P, lt, { absT: t });
}

// full-screen page turn: the old page (A) lifts from its right edge and swings over the spine at the left edge,
// curling as it goes, uncovering the new page (B) under a soft travelling shadow.
function turnPage(g, A, B, th) {
  g.setTransform(1, 0, 0, 1, 0, 0); g.clearRect(0, 0, W, H); g.drawImage(B, 0, 0);
  const D = 5200, N = 64;
  const edgeX = 1920 * Math.cos(th);
  if (th < Math.PI / 2) {
    const gr = g.createLinearGradient(edgeX, 0, edgeX + 320 * (1 - Math.cos(th)) + 40, 0);
    gr.addColorStop(0, `rgba(30,20,10,${0.38 * Math.sin(th) + 0.1})`); gr.addColorStop(1, 'rgba(30,20,10,0)');
    g.fillStyle = gr; g.fillRect(Math.max(0, edgeX), 0, 1920, 1080);
  } else { g.fillStyle = `rgba(30,20,10,${0.18 * Math.sin(th)})`; g.fillRect(0, 0, 160 * Math.sin(th), 1080); }
  for (let i = 0; i < N; i++) {
    const u0 = 1920 * i / N, u1 = 1920 * (i + 1) / N;
    const ang = u => th - 0.5 * Math.sin(th) * Math.pow(u / 1920, 1.6);
    const aA = ang(u0), aB = ang(u1); if (Math.cos((aA + aB) / 2) <= 0) continue;   // back of the page is off-screen
    const hA = u0 * Math.sin(aA), hB = u1 * Math.sin(aB), fA = D / (D - hA), fB = D / (D - hB);
    const XA = (u0 * Math.cos(aA) - 960) * fA + 960, YA0 = -540 * fA + 540, YA1 = 540 * fA + 540;
    const XB = (u1 * Math.cos(aB) - 960) * fB + 960, YB0 = -540 * fB + 540;
    if (XB - XA < 0.2) continue;
    const sw = 1920 / N;
    g.save(); g.setTransform((XB - XA) / sw, (YB0 - YA0) / sw, 0, (YA1 - YA0) / 1080, XA, YA0);
    g.drawImage(A, u0, 0, sw, 1080, 0, 0, sw * 1.04, 1080);
    g.fillStyle = `rgba(40,28,15,${0.3 * Math.sin((aA + aB) / 2) * (0.5 + 0.5 * u0 / 1920)})`; g.fillRect(0, 0, sw * 1.04, 1080);
    g.restore();
  }
}

// the printed words, on a torn-out patch of clean paper; long lines wrap to two rows
export function subTo(SK, ST, t) {
  const S_ = SUBS.find(s => t >= s.t0 && t < s.t1); if (!S_) return;
  const rv = clamp((t - S_.t0) / 0.35);
  const g = SK.g; g.save(); g.font = '400 52px "Patrick Hand"';
  let rows = [S_.text];
  if (g.measureText(S_.text).width > 1500) {
    const w = S_.text.split(' '); let best = 1, bd = 1e9;
    for (let j = 1; j < w.length; j++) { const d = Math.abs(g.measureText(w.slice(0, j).join(' ')).width - g.measureText(w.slice(j).join(' ')).width); if (d < bd) { bd = d; best = j; } }
    rows = [w.slice(0, best).join(' '), w.slice(best).join(' ')];
  }
  const tw = Math.max(...rows.map(r => g.measureText(r).width)); g.restore();
  const cx = 960, cy = rows.length > 1 ? 970 : 1002, hw = tw / 2 + 46, hh = rows.length > 1 ? 80 : 44;
  g.save(); g.fillStyle = '#000'; g.beginPath();
  for (let i = 0; i <= 60; i++) { const a = i / 60 * Math.PI * 2; const px = Math.cos(a), py = Math.sin(a); const sq = Math.pow(Math.abs(px), 0.3) * Math.sign(px); const n = 1 + 0.05 * Math.sin(a * 7 + 1.3) + 0.03 * Math.sin(a * 17); const X = cx + sq * hw * n, Y = cy + Math.pow(Math.abs(py), 0.6) * Math.sign(py) * hh * n; i ? g.lineTo(X, Y) : g.moveTo(X, Y); }
  g.closePath(); g.fill(); g.restore();
  const n = rows.length, tot = rows.reduce((s, r) => s + r.length, 0); let done = 0;
  rows.forEach((r, j) => {
    const rr = clamp((rv * tot - done) / r.length); done += r.length;
    text(ST, r, cx, cy + 18 + (j - (n - 1) / 2) * 64, { size: 52, col: K.ink, reveal: rr, seed: 11 + S_.t0 * 3 + j * 5, p: 1, stroke: 1.2 });
  });
}
