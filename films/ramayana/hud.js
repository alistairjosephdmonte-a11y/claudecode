// 2D overlay: narration subtitles, hanging book signs, the first verse on a scroll, action words, end title
import { VO, CHAPTERS, SHLOKA, ACTIONS, TITLE, CREDITS, DUR } from './story.js';
import { clamp, seg, back, ss, eo, lerp, TAU, mulberry } from './lib.js';
const INK = '#3a2a24';
function wrap(x, text, maxW) { const words = text.split(' '), lines = []; let cur = ''; for (const w of words) { const t = cur ? cur + ' ' + w : w; if (x.measureText(t).width > maxW && cur) { lines.push(cur); cur = w; } else cur = t; } if (cur) lines.push(cur); return lines; }

export function drawSubs(x, t, dur) {
  for (const [id, t0, en] of VO) {
    const d = dur[id] || 3, hold = Math.max(1.8, d + .6), a = Math.min(seg(t, t0 - .15, t0 + .15), 1 - seg(t, t0 + hold, t0 + hold + .3));
    if (a <= 0) continue;
    x.save(); x.globalAlpha = a; x.textAlign = 'center'; x.textBaseline = 'alphabetic'; x.lineJoin = 'round';
    x.font = '500 40px Fredoka'; const lines = wrap(x, en, 1500);
    let y = 1080 - 56 - (lines.length - 1) * 50;
    x.shadowColor = 'rgba(0,0,0,.35)'; x.shadowBlur = 16;
    for (const l of lines) { x.lineWidth = 9; x.strokeStyle = 'rgba(40,26,18,.85)'; x.strokeText(l, 960, y); x.fillStyle = '#fffaf0'; x.fillText(l, 960, y); y += 50; }
    x.restore();
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
export function drawChapter(x, t) {
  for (const [t0, t1, a, b, gl] of CHAPTERS) {
    if (t < t0 || t > t1 + .6) continue;
    x.font = '84px "Lilita One"'; const w = Math.max(660, x.measureText(b).width + 160);
    sign(x, t, t0, t1, () => {
      x.fillStyle = '#d8423a'; x.beginPath(); x.moveTo(-190, -70); x.lineTo(190, -70); x.lineTo(170, -32); x.lineTo(190, 6); x.lineTo(-190, 6); x.lineTo(-170, -32); x.closePath(); x.fill(); x.lineWidth = 6; x.strokeStyle = INK; x.stroke();
      x.textAlign = 'center'; x.textBaseline = 'middle';
      x.font = '38px "Lilita One"'; x.fillStyle = '#fff4d6'; x.fillText(a, 0, -30);
      x.font = '84px "Lilita One"'; x.lineWidth = 12; x.strokeStyle = INK; x.lineJoin = 'round'; x.strokeText(b, 0, 56); x.fillStyle = '#ffcf3f'; x.fillText(b, 0, 56);
      x.font = 'italic 38px "IM Fell English"'; x.fillStyle = '#6b4a36'; x.fillText(gl, 0, 120);
    }, w, 196);
  }
}
export function drawShloka(x, t) {
  const S = SHLOKA; if (t < S.t0 || t > S.t1 + .6) return;
  sign(x, t, S.t0, S.t1, () => {
    x.textAlign = 'center'; x.textBaseline = 'middle';
    x.font = '50px "Tiro Devanagari Sanskrit"'; x.fillStyle = '#3a2a24';
    S.lines.forEach((l, i) => x.fillText(l, 0, 16 + i * 66));
    x.font = 'italic 32px "IM Fell English"'; x.fillStyle = '#6b4a36'; x.fillText(S.gloss, 0, 158);
  }, 1180, 236, 170);
}
export function drawAction(x, t, anchors) {
  ACTIONS.forEach(([t0, text, col], i) => {
    const p = anchors[i]; if (t < t0 || t > t0 + 1.2 || !p) return;
    const k = back(seg(t, t0, t0 + .18), 2.5), fo = 1 - seg(t, t0 + .85, t0 + 1.2);
    x.save(); x.translate(p[0], p[1] - 40 - seg(t, t0, t0 + 1.2) * 50); x.rotate(-.12); x.scale(k, k); x.globalAlpha = fo;
    const R = mulberry(Math.round(t0 * 10));
    for (let j = 0; j < 10; j++) { const a = j / 10 * TAU + R() * .3, r0 = 90, r1 = 150 + R() * 60 * eo(seg(t, t0, t0 + .4)); x.strokeStyle = j % 2 ? '#ffe35a' : '#ffffff'; x.lineWidth = 8; x.lineCap = 'round'; x.beginPath(); x.moveTo(Math.cos(a) * r0, Math.sin(a) * r0 * .6); x.lineTo(Math.cos(a) * r1, Math.sin(a) * r1 * .6); x.stroke(); }
    x.font = 'italic 120px "Lilita One"'; x.textAlign = 'center'; x.textBaseline = 'middle'; x.lineJoin = 'round';
    x.lineWidth = 30; x.strokeStyle = '#fffaf0'; x.strokeText(text, 0, 0); x.lineWidth = 12; x.strokeStyle = INK; x.strokeText(text, 0, 0);
    const g = x.createLinearGradient(0, -50, 0, 50); g.addColorStop(0, col[0]); g.addColorStop(1, col[1]); x.fillStyle = g; x.fillText(text, 0, 0);
    x.restore();
  });
}
export function drawBang(x, t, t0, p) {
  if (!p || t < t0 || t > t0 + 1.1) return;
  const k = back(seg(t, t0, t0 + .15), 3), fo = 1 - seg(t, t0 + .9, t0 + 1.1);
  x.save(); x.translate(p[0] + 10, p[1] - 30); x.scale(k, k); x.globalAlpha = fo;
  x.font = '130px "Lilita One"'; x.textAlign = 'center'; x.lineJoin = 'round';
  x.lineWidth = 26; x.strokeStyle = '#fffaf0'; x.strokeText('!', 0, 0); x.lineWidth = 10; x.strokeStyle = INK; x.strokeText('!', 0, 0); x.fillStyle = '#ff4b3a'; x.fillText('!', 0, 0);
  x.restore();
}
export function drawEnd(x, t) {
  const T0 = TITLE.t0; if (t < T0) return;
  const k = seg(t, T0, T0 + .8), k3 = seg(t, 119.5, 120.3), fo = 1 - seg(t, DUR - 1.2, DUR - .2);
  x.save(); x.globalAlpha = fo * k; x.textAlign = 'center'; x.textBaseline = 'middle'; x.lineJoin = 'round';
  x.translate(0, (1 - eo(k)) * 30); x.shadowColor = 'rgba(0,0,0,.45)'; x.shadowBlur = 24;
  x.font = '100px "Lilita One"'; x.lineWidth = 14; x.strokeStyle = INK; x.strokeText('The Ramayana', 960, 150); x.fillStyle = '#ffd24a'; x.fillText('The Ramayana', 960, 150);
  x.font = 'italic 48px "IM Fell English"'; x.lineWidth = 8; x.strokeStyle = 'rgba(30,20,14,.75)'; x.strokeText('as Valmiki told it, in seven books', 960, 232); x.fillStyle = '#fffaf0'; x.fillText('as Valmiki told it, in seven books', 960, 232);
  x.shadowBlur = 10; x.shadowColor = 'rgba(0,0,0,.6)'; x.globalAlpha = fo * k3; x.font = '24px Fredoka'; x.fillStyle = 'rgba(255,248,235,.95)';
  CREDITS.forEach((l, i) => x.fillText(l, 960, 1000 + i * 36));
  x.restore();
}
