// 2D overlay: Hindi subtitles, hanging book signs (kandas), verse scrolls, action words, end title
import { seg, back, ss, eo, TAU, mulberry } from './lib.js';
const INK = '#3a2a24', SUB = '600 44px "Baloo 2"', DEV = '"Tiro Devanagari Hindi"';
let G = null;
export function setup(g) { G = g; }

function wrap(x, text, maxW) { const words = text.split(' '), lines = []; let cur = ''; for (const w of words) { const t = cur ? cur + ' ' + w : w; if (x.measureText(t).width > maxW && cur) { lines.push(cur); cur = w; } else cur = t; } if (cur) lines.push(cur); return lines; }
// a long line is shown in parts, each part timed by its share of the characters
function parts(x, text) {
  x.font = SUB; const lines = wrap(x, text, 1560); if (lines.length <= 2) return [lines];
  const out = []; for (let i = 0; i < lines.length; i += 2) out.push(lines.slice(i, i + 2)); return out;
}
const cache = new Map();
function drawSubs(x, t) {
  for (const L of G.LAY) {
    if (t < L.S - 1 || t > L.E + 2) continue;
    L.vo.forEach((v, i) => {
      const nxt = L.vo[i + 1], hold = Math.min(v.d + .5, nxt ? nxt.t0 - v.t0 - .1 : v.d + 1.2);
      if (t < v.t0 - .15 || t > v.t0 + hold + .3) return;
      let P = cache.get(v.id); if (!P) { P = parts(x, v.text); const n = P.map(p => p.join(' ').length), tot = n.reduce((a, b) => a + b, 0); let acc = 0; P = P.map((p, k) => { const a = acc / tot; acc += n[k]; return { p, a, b: acc / tot }; }); cache.set(v.id, P); }
      for (const { p, a: fa, b: fb } of P) {
        const t0 = v.t0 + fa * v.d - (fa ? .05 : 0), t1 = fb === 1 ? v.t0 + hold : v.t0 + fb * v.d;
        const al = Math.min(seg(t, t0 - .15, t0 + .1), 1 - seg(t, t1, t1 + .2)); if (al <= 0) continue;
        x.save(); x.globalAlpha = al; x.textAlign = 'center'; x.textBaseline = 'alphabetic'; x.lineJoin = 'round'; x.font = SUB;
        let y = 1080 - 60 - (p.length - 1) * 58; x.shadowColor = 'rgba(0,0,0,.35)'; x.shadowBlur = 16;
        for (const l of p) { x.lineWidth = 10; x.strokeStyle = 'rgba(40,26,18,.88)'; x.strokeText(l, 960, y); x.fillStyle = '#fffaf0'; x.fillText(l, 960, y); y += 58; }
        x.restore();
      }
    });
  }
}
function sign(x, t, t0, t1, drawBody, w, h, yTop = 150) {
  const kin = seg(t, t0, t0 + .7), kout = seg(t, t1, t1 + .5);
  const drop = (1 - back(kin, 1.4)) * -360 - ss(kout) * 460, sw = Math.sin((t - t0) * 3.2) * .03 * (1 - kin * .6) * (1 - kout);
  x.save(); x.translate(960, yTop + drop); x.rotate(sw);
  x.strokeStyle = '#6b5a4a'; x.lineWidth = 3; x.beginPath(); x.moveTo(-w * .4, -40); x.lineTo(-w * .4, -420); x.moveTo(w * .4, -40); x.lineTo(w * .4, -420); x.stroke();
  x.fillStyle = 'rgba(40,25,15,.25)'; x.beginPath(); x.roundRect(-w / 2 + 10, -40 + 14, w, h, 20); x.fill();
  x.fillStyle = '#fffaf0'; x.beginPath(); x.roundRect(-w / 2 - 10, -52, w + 20, h + 24, 26); x.fill();
  x.fillStyle = '#f4e6c8'; x.beginPath(); x.roundRect(-w / 2, -40, w, h, 20); x.fill(); x.lineWidth = 6; x.strokeStyle = INK; x.stroke();
  drawBody(); x.restore();
}
function drawChapter(x, t) {
  for (const L of G.LAY) {
    const c = L.sc.chapter; if (!c) continue;
    const t0 = L.R + .1, t1 = L.R + (c[3] ?? 4.2); if (t < t0 || t > t1 + .6) continue;
    x.font = '800 92px "Baloo 2"'; const w = Math.max(680, x.measureText(c[1]).width + 170);
    sign(x, t, t0, t1, () => {
      x.fillStyle = '#d8423a'; x.beginPath(); x.moveTo(-200, -74); x.lineTo(200, -74); x.lineTo(180, -34); x.lineTo(200, 6); x.lineTo(-200, 6); x.lineTo(-180, -34); x.closePath(); x.fill(); x.lineWidth = 6; x.strokeStyle = INK; x.stroke();
      x.textAlign = 'center'; x.textBaseline = 'middle';
      x.font = '800 40px "Baloo 2"'; x.fillStyle = '#fff4d6'; x.fillText(c[0], 0, -30);
      x.font = '800 92px "Baloo 2"'; x.lineWidth = 12; x.strokeStyle = INK; x.lineJoin = 'round'; x.strokeText(c[1], 0, 62); x.fillStyle = '#ffcf3f'; x.fillText(c[1], 0, 62);
      x.font = `40px ${DEV}`; x.fillStyle = '#6b4a36'; x.fillText(c[2], 0, 132);
    }, w, 206);
  }
}
function drawShloka(x, t) {
  for (const L of G.LAY) {
    const S = L.sc.shloka; if (!S) continue;
    const t0 = L.T(S.t0), t1 = L.T(S.t1); if (t < t0 || t > t1 + .6) continue;
    sign(x, t, t0, t1, () => {
      x.textAlign = 'center'; x.textBaseline = 'middle';
      x.font = '50px "Tiro Devanagari Sanskrit"'; x.fillStyle = '#3a2a24';
      S.lines.forEach((l, i) => x.fillText(l, 0, 16 + i * 66));
      x.font = `32px ${DEV}`; x.fillStyle = '#6b4a36'; x.fillText(S.gloss, 0, 160);
    }, 1240, 240, 170);
  }
}
function drawWord(x, t, t0, text, col, p) {
  if (!p || t < t0 || t > t0 + 1.25) return;
  const k = back(seg(t, t0, t0 + .18), 2.5), fo = 1 - seg(t, t0 + .85, t0 + 1.25);
  x.save(); x.translate(p[0], p[1] - 40 - seg(t, t0, t0 + 1.2) * 50); x.rotate(-.1); x.scale(k, k); x.globalAlpha = fo;
  const R = mulberry(Math.round(t0 * 10));
  for (let j = 0; j < 10; j++) { const a = j / 10 * TAU + R() * .3, r0 = 90, r1 = 150 + R() * 60 * eo(seg(t, t0, t0 + .4)); x.strokeStyle = j % 2 ? '#ffe35a' : '#ffffff'; x.lineWidth = 8; x.lineCap = 'round'; x.beginPath(); x.moveTo(Math.cos(a) * r0, Math.sin(a) * r0 * .6); x.lineTo(Math.cos(a) * r1, Math.sin(a) * r1 * .6); x.stroke(); }
  x.font = '800 116px "Baloo 2"'; x.textAlign = 'center'; x.textBaseline = 'middle'; x.lineJoin = 'round';
  x.lineWidth = 30; x.strokeStyle = '#fffaf0'; x.strokeText(text, 0, 0); x.lineWidth = 12; x.strokeStyle = INK; x.strokeText(text, 0, 0);
  const g = x.createLinearGradient(0, -50, 0, 50); g.addColorStop(0, col[0]); g.addColorStop(1, col[1]); x.fillStyle = g; x.fillText(text, 0, 0);
  x.restore();
}
function drawBang(x, t, t0, p, ch = '!') {
  if (!p || t < t0 || t > t0 + 1.1) return;
  const k = back(seg(t, t0, t0 + .15), 3), fo = 1 - seg(t, t0 + .9, t0 + 1.1);
  x.save(); x.translate(p[0] + 10, p[1] - 30); x.scale(k, k); x.globalAlpha = fo;
  x.font = '130px "Lilita One"'; x.textAlign = 'center'; x.lineJoin = 'round';
  x.lineWidth = 26; x.strokeStyle = '#fffaf0'; x.strokeText(ch, 0, 0); x.lineWidth = 10; x.strokeStyle = INK; x.strokeText(ch, 0, 0); x.fillStyle = ch === '!' ? '#ff4b3a' : '#3fa1ff'; x.fillText(ch, 0, 0);
  x.restore();
}
function drawEnd(x, t) {
  const T0 = G.TITLE_T, M = G.META; if (t < T0) return;
  const k = seg(t, T0, T0 + .8), k3 = seg(t, T0 + 3.4, T0 + 4.2), fo = 1 - seg(t, G.DUR - 1.2, G.DUR - .2);
  x.save(); x.globalAlpha = fo * k; x.textAlign = 'center'; x.textBaseline = 'middle'; x.lineJoin = 'round';
  x.translate(0, (1 - eo(k)) * 30); x.shadowColor = 'rgba(0,0,0,.45)'; x.shadowBlur = 24;
  x.font = '800 124px "Baloo 2"'; x.lineWidth = 14; x.strokeStyle = INK; x.strokeText(M.title, 960, 150); x.fillStyle = '#ffd24a'; x.fillText(M.title, 960, 150);
  x.font = `50px ${DEV}`; x.lineWidth = 8; x.strokeStyle = 'rgba(30,20,14,.75)'; x.strokeText(M.sub, 960, 250); x.fillStyle = '#fffaf0'; x.fillText(M.sub, 960, 250);
  x.shadowBlur = 10; x.shadowColor = 'rgba(0,0,0,.6)'; x.globalAlpha = fo * k3; x.fillStyle = 'rgba(255,248,235,.95)';
  M.credits.forEach((l, i) => { x.font = i < M.credits.length - 2 ? '600 28px "Baloo 2"' : '24px Fredoka'; x.fillText(l, 960, 1080 - 40 - (M.credits.length - 1 - i) * 38); });
  x.restore();
}
export function draw(x, t, at) {
  drawChapter(x, t); drawShloka(x, t);
  for (const e of G.FX) {
    if (t < e.t - .1 || t > e.t + 1.4) continue;
    if (e.type === 'word') drawWord(x, t, e.t, e.f[2], e.f[3] || ['#fff35a', '#ff9a2e'], at(e.f[4]));
    else if (e.type === 'bang') drawBang(x, t, e.t, at(e.f[2]), e.f[3]);
  }
  drawSubs(x, t); drawEnd(x, t);
}
