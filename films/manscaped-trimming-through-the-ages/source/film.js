// Trimming Through the Ages: ten 30-second pages of one crayon picture book, joined by page turns.
// Chapter i owns [30(i−1), 30i). Inside it, each narrated line is placed in its beat (story.json), nudged only as much as
// the measured voice length (voice.json) needs; drawings key off the line starts, so picture and words stay locked.
// Drawn things step at 12 fps (c.tq, c.p); the camera, page turns and the one watercolour wash run at 24 fps (c.t, c.pc).
import { layer, clear, text, CAM, BOIL, W, H } from './crayon.js';
import { group, clearGroup } from './rig.js';
import { PAL } from './pal.js';
import { clamp, hash, ss } from '/core/lib.js';
import { CHAPTERS } from './chapters/index.js';
const K = PAL.crayon;
const STORY = await (await fetch('./story.json')).json();
const VD = await (await fetch('./voice.json')).json();
export const LEN = STORY.chapter, DUR = LEN * STORY.chapters.length, TURN = 1.0;

// —— line placement: start at beat + lead, never before the previous line has finished and breathed ——
export const TL = STORY.chapters.map((ch, ci) => {
  const t0 = ci * LEN; let prevEnd = -1;
  const lines = ch.beats.map(([b0, b1, id, txt], i) => {
    const d = VD[id] ?? 3, lead = i === 0 ? (ci ? TURN + 0.9 : 1.2) : 0.45;
    let t = Math.max(b0 - t0 + lead, prevEnd + 0.55);
    const room = b1 - t0 - 0.35 - d; if (t > room && room > prevEnd + 0.4) t = room;   // pull earlier inside the beat if it would spill
    prevEnd = t + d; return { id, text: txt, t, d, b0: b0 - t0, b1: b1 - t0 };
  });
  return { id: ch.id, title: ch.title, t0, lines };
});
// book copy: each line is written on under the picture and stays until the next one
export const SUBS = [];
TL.forEach(C => C.lines.forEach((L, i) => { const nx = C.lines[i + 1]; SUBS.push({ t0: C.t0 + L.t - 0.05, t1: nx ? C.t0 + nx.t - 0.1 : C.t0 + LEN - (C.id === 'modern' ? 0 : 0.25), text: L.text }); }));

export const EV = [];
const ev = (t, type, o = {}) => EV.push({ t: +t.toFixed(3), type, ...o });
TL.forEach((C, ci) => {
  ev(C.t0, 'cue', { id: C.id, i: ci });
  if (ci) ev(C.t0, 'page', { dur: TURN });
  C.lines.forEach(L => ev(C.t0 + L.t, 'voice', { id: L.id, d: L.d }));
  ev(C.t0 + (ci ? TURN + 0.15 : 0.2), 'write', { dur: 1.3, pan: -0.6 });   // the chapter title being handwritten
  const M = CHAPTERS[C.id]; (M.sfx ? M.sfx(ctxOf(C, 0)) : []).forEach(([t, type, o]) => ev(C.t0 + t, type, o || {}));
});
EV.sort((a, b) => a.t - b.t);

export function ctxOf(C, t) {
  const L = C.lines, tq = Math.floor(t * 12 + 1e-6) / 12, Li = i => L[Math.max(0, Math.min(L.length - 1, i))];
  return {
    t, tq, dur: LEN, turn: C.t0 > 0 ? TURN : 0, id: C.id,
    at: (i, o = 0) => Li(i).t + o, end: (i, o = 0) => Li(i).t + Li(i).d + o, beat: (i, o = 0) => Li(i).b0 + o,
    p: (a, b) => clamp((tq - a) / (b - a)),      // drawn things: 12 fps steps
    pc: (a, b) => clamp((t - a) / (b - a)),      // camera / wash: 24 fps
  };
}

// —— layers ——
export const S = { BG: { f: layer(), l: layer() }, G: group(), G2: group(), FX: layer(), WASH: layer(), WFX: layer(), IMG: layer() };
const SUBK = layer(), SUBT = layer(), HEAD = layer();
const mk = () => { const c = document.createElement('canvas'); c.width = W; c.height = H; return { c, g: c.getContext('2d') }; };
const snapA = mk(), snapB = mk(), turnC = mk();
const snap = P => { P.g.setTransform(1, 0, 0, 1, 0, 0); P.g.clearRect(0, 0, W, H); P.g.drawImage(document.getElementById('gl'), 0, 0); };

export function renderChapter(comp, ci, t, { copy = true, absT = 0, vig = 0.24 } = {}) {
  const C = TL[ci], M = CHAPTERS[C.id], c = ctxOf(C, t);
  [CAM.x, CAM.y, CAM.s] = M.cam ? M.cam(c) : [W / 2, H / 2, 1];
  BOIL.step = Math.floor((C.t0 + t) * 12 + 1e-6);
  [S.BG.f, S.BG.l, S.FX, S.WASH, S.WFX, S.IMG, SUBK, SUBT, HEAD].forEach(clear); clearGroup(S.G); clearGroup(S.G2);
  const o = M.draw(S, c) || {};
  // the chapter title, handwritten into the top margin of the page as it is drawn
  const ta = c.turn + 0.15; text(HEAD, C.title, 36, 64, { size: 46, font: 'Gaegu', weight: 700, align: 'left', reveal: c.p(ta, ta + 1.3), seed: 500 + ci * 7, p: 0.9, stroke: 1.2 });
  if (copy) copyTo(SUBK, SUBT, absT);
  comp.paperCam(ci * 2400 + CAM.x * 0.6, 900 * (ci % 3) + CAM.y * 0.6, CAM.s / 0.6);
  comp.begin(PAL.paper);
  comp.crayon(S.BG.f.c); comp.crayon(S.BG.l.c);
  const go = [hash(BOIL.step) * 300, hash(BOIL.step + 7) * 300];
  comp.group(S.G2, { goff: go });
  if (o.wash) comp.wash(S.WASH.c, { color: PAL.wash });
  comp.crayon(S.WFX.c, { goff: go });
  comp.group(S.G, { goff: go });
  if (o.image) comp.image(S.IMG.c);
  comp.crayon(S.FX.c, { goff: go });
  comp.crayon(HEAD.c);
  comp.knock(SUBK.c); comp.crayon(SUBT.c);
  comp.finish({ vig });
}

export function frame(comp, T) {
  const ci = Math.min(TL.length - 1, Math.floor(T / LEN + 1e-9)), lt = T - TL[ci].t0;
  if (ci > 0 && lt < TURN) {
    renderChapter(comp, ci - 1, LEN - 1 / 24, { copy: false }); snap(snapA);
    renderChapter(comp, ci, lt, { copy: false }); snap(snapB);
    turnPage(turnC.g, snapA.c, snapB.c, Math.PI * ss(lt / TURN));
    comp.paperCam(0, 0, 1); comp.begin(PAL.paper); comp.image(turnC.c); comp.finish({ vig: 0, emb: 0, lift: 0 });
    return;
  }
  renderChapter(comp, ci, lt, { absT: T });
}

// full-frame page turn about the left edge (the spine): the old page lifts, curls and swings away over the new one
function turnPage(g, A, B, th) {
  g.setTransform(1, 0, 0, 1, 0, 0); g.clearRect(0, 0, W, H); g.drawImage(B, 0, 0);
  const D = 4200, N = 56, edgeX = W * Math.cos(th);
  if (th < Math.PI / 2) { const gr = g.createLinearGradient(edgeX, 0, edgeX + 260 * (1 - Math.cos(th)) + 40, 0); gr.addColorStop(0, `rgba(30,20,10,${0.36 * Math.sin(th) + 0.1})`); gr.addColorStop(1, 'rgba(30,20,10,0)'); g.fillStyle = gr; g.fillRect(Math.max(0, edgeX), 0, W, H); }
  else { g.fillStyle = `rgba(30,20,10,${0.18 * Math.sin(th)})`; g.fillRect(0, 0, 140 * Math.sin(th), H); }
  for (let i = 0; i < N; i++) {
    const u0 = W * i / N, u1 = W * (i + 1) / N, ang = u => th - 0.5 * Math.sin(th) * Math.pow(u / W, 1.6);
    const aA = ang(u0), aB = ang(u1); if (Math.cos((aA + aB) / 2) <= 0) continue;
    const fA = D / (D - u0 * Math.sin(aA)), fB = D / (D - u1 * Math.sin(aB));
    const XA = (u0 * Math.cos(aA) - W / 2) * fA + W / 2, YA0 = -H / 2 * fA + H / 2, YA1 = H / 2 * fA + H / 2;
    const XB = (u1 * Math.cos(aB) - W / 2) * fB + W / 2, YB0 = -H / 2 * fB + H / 2;
    if (XB - XA < 0.2) continue; const sw = W / N;
    g.save(); g.setTransform((XB - XA) / sw, (YB0 - YA0) / sw, 0, (YA1 - YA0) / H, XA, YA0);
    g.drawImage(A, u0, 0, sw, H, 0, 0, sw * 1.04, H);
    g.fillStyle = `rgba(40,28,15,${0.3 * Math.sin((aA + aB) / 2) * (0.5 + 0.5 * u0 / W)})`; g.fillRect(0, 0, sw * 1.04, H); g.restore();
  }
}

// the book's printed words: handwritten straight onto bare paper in the bottom margin (no box); long lines wrap
export function copyTo(SK, ST, t) {
  const S_ = SUBS.find(s => t >= s.t0 && t < s.t1); if (!S_) return;
  const tq = Math.floor(t * 12) / 12, rv = clamp((tq - S_.t0) / Math.max(0.5, S_.text.length * 0.022));
  const g = SK.g; g.save(); g.font = '400 46px "Patrick Hand"';
  let rows = [S_.text];
  if (g.measureText(S_.text).width > W - 200) { const w = S_.text.split(' '); let best = 1, bd = 1e9; for (let j = 1; j < w.length; j++) { const d = Math.abs(g.measureText(w.slice(0, j).join(' ')).width - g.measureText(w.slice(j).join(' ')).width); if (d < bd) { bd = d; best = j; } } rows = [w.slice(0, best).join(' '), w.slice(best).join(' ')]; }
  g.restore();
  const n = rows.length, tot = rows.reduce((s, r) => s + r.length, 0); let done = 0;
  rows.forEach((r, j) => { const rr = clamp((rv * tot - done) / r.length); done += r.length; const y = 1000 + (j - (n - 1)) * 50 + (n > 1 ? 10 : 0);
    // clear the paper just around the letters (a halo, not a box) so the words read over any drawing
    if (rr > 0) { g.save(); g.font = '400 46px "Patrick Hand"'; g.textAlign = 'center'; g.lineJoin = 'round'; g.lineWidth = 16; g.strokeStyle = '#000'; g.filter = 'blur(3px)';
      const cut = r.slice(0, Math.ceil(rr * r.length)), full = g.measureText(r).width; g.textAlign = 'left'; g.strokeText(cut, W / 2 - full / 2, y); g.fillText(cut, W / 2 - full / 2, y); g.restore(); }
    text(ST, r, W / 2, y, { size: 46, col: K.ink, reveal: rr, seed: 11 + S_.t0 * 3 + j * 5, p: 1, stroke: 1.1 }); });
}
