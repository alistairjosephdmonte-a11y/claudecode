// West Side Story, explained in a minute. Mid-century cut-paper poster style: cream stock, signal red, ink, mustard,
// one blue; bold condensed type; hard cuts behind a red paper wipe; everything lands on the beat of a finger-snap groove.
// Scene i plays under narrated line i; the timeline comes from the measured voice lengths (voice.json).
const cv = document.getElementById('c'), g = cv.getContext('2d');
const W = 1920, H = 1080;
const C = { paper: '#EFE6D2', paper2: '#E3D5B8', ink: '#18171B', red: '#D7352A', mustard: '#E9A930', blue: '#2C4C80', white: '#FBF7EE' };
const STORY = await (await fetch('./story.json')).json();
const VD = await (await fetch('./voice.json')).json();
await Promise.all(['40px Bebas', '600 40px Oswald', '300 40px Oswald', 'italic 40px DMSerif'].map(f => document.fonts.load(f)));

// —— timeline ——
const BPM = 112, BEAT = 60 / BPM;
const LINES = []; let t = 1.0;
STORY.lines.forEach(([id, text], i) => { LINES.push({ id, text, t, d: VD[id] }); t += VD[id] + (i === 1 || i === 3 || i === 7 ? 0.35 : 0.22); });
const OUTRO = 3.2;
const DUR = +(LINES[LINES.length - 1].t + LINES[LINES.length - 1].d + OUTRO).toFixed(3);
const SC = LINES.map((L, i) => ({ t0: i ? L.t - 0.3 : 0, t1: i < LINES.length - 1 ? LINES[i + 1].t - 0.3 : DUR }));
const SUBS = LINES.map((L, i) => ({ t0: L.t - 0.05, t1: Math.min(L.t + L.d + 0.4, i < LINES.length - 1 ? LINES[i + 1].t - 0.08 : DUR), text: L.text }));

// —— events for the mix ——
const EV = [];
const ev = (t, type, o = {}) => EV.push({ t: +t.toFixed(3), type, ...o });
LINES.forEach(L => ev(L.t, 'voice', { id: L.id, d: L.d }));
SC.forEach((s, i) => { if (i) ev(s.t0, 'wipe'); });
const at = (i, u) => SC[i].t0 + u;   // scene-local → absolute
const dur = i => SC[i].t1 - SC[i].t0;
ev(at(0, 0.9), 'slam'); ev(at(0, 0.9 + BEAT), 'slam'); ev(at(0, 0.9 + 2 * BEAT), 'slam');
ev(at(1, dur(1) - 2.2), 'stamp'); ev(at(2, dur(2) * 0.5 + 0.25), 'flip');
ev(at(3, 2.2), 'split'); ev(at(3, dur(3) - 3.4 + 1.1), 'heartpop');
[0.2, dur(4) * 0.33, dur(4) * 0.52, dur(4) * 0.68].forEach(u => ev(at(4, u), 'card'));
ev(at(5, dur(5) * 0.45), 'count', { dur: dur(5) * 0.55 - 0.6 });
ev(at(6, dur(6) * 0.55 + 0.6), 'win');
ev(at(7, 0.3), 'slam'); ev(at(7, 0.6), 'trophies'); ev(at(7, dur(7) * 0.42), 'swipe');
ev(at(8, 2.3), 'stamp2'); ev(at(9, dur(9) - 2.4), 'end');
EV.sort((a, b) => a.t - b.t);

// —— helpers ——
const clamp = (x, a = 0, b = 1) => Math.max(a, Math.min(b, x));
const pr = (t, a, b) => clamp((t - a) / (b - a));
const eo = x => 1 - Math.pow(1 - clamp(x), 3);
const eio = x => { x = clamp(x); return x < .5 ? 4 * x * x * x : 1 - Math.pow(-2 * x + 2, 3) / 2; };
const back = (x, s = 1.7) => { x = clamp(x) - 1; return 1 + x * x * ((s + 1) * x + s); };
const lerp = (a, b, u) => a + (b - a) * u;
const hash = n => { n = Math.sin(n * 127.1 + 311.7) * 43758.5453; return n - Math.floor(n); };
function rect(x, y, w, h, col) { g.fillStyle = col; g.fillRect(x, y, w, h); }
function txt(s, x, y, { size = 80, font = 'Bebas', col = C.ink, align = 'left', track = 0, weight = '', italic = false, alpha = 1 } = {}) {
  g.save(); g.globalAlpha *= alpha; g.font = `${italic ? 'italic ' : ''}${weight} ${size}px ${font}`; g.fillStyle = col; g.textAlign = align; g.textBaseline = 'alphabetic';
  g.letterSpacing = track + 'px'; g.fillText(s, x, y); const w = g.measureText(s).width; g.restore(); return w;
}
// text revealed by a hard mask sliding up from its baseline (classic title-card pop)
function popTxt(s, x, y, u, o = {}) {
  const size = o.size || 80; if (u <= 0) return;
  g.save(); g.beginPath(); g.rect(-10, y - size * 1.05, W + 20, size * 1.25); g.clip();
  txt(s, x, y + (1 - eo(u)) * size * 1.1, o); g.restore();
}
function circle(x, y, r, col) { if (r <= 0) return; g.fillStyle = col; g.beginPath(); g.arc(x, y, r, 0, Math.PI * 2); g.fill(); }
// cut-paper shape: a polygon with a soft drop shadow and a hair of jitter (paper doesn't cut perfectly)
function paper(pts, col, sh = 8, seed = 1) {
  const j = (k, a) => (hash(seed + k * 3.1 + a) - .5) * 2.2;
  g.save(); g.fillStyle = 'rgba(40,25,10,0.18)'; g.beginPath(); pts.forEach(([x, y], k) => k ? g.lineTo(x + sh + j(k, 1), y + sh + j(k, 2)) : g.moveTo(x + sh, y + sh)); g.closePath(); g.fill();
  g.fillStyle = col; g.beginPath(); pts.forEach(([x, y], k) => k ? g.lineTo(x + j(k, 3), y + j(k, 4)) : g.moveTo(x, y)); g.closePath(); g.fill(); g.restore();
}
const box = (x, y, w, h) => [[x, y], [x + w, y], [x + w, y + h], [x, y + h]];
// a person as cut paper: head + tapered body (generic, no likeness)
function figure(x, y, s, col, lean = 0, step = 0) {
  paper([[x - 34 * s + lean, y - 150 * s], [x + 34 * s + lean, y - 150 * s], [x + 26 * s, y - 60 * s], [x + 30 * s + step, y], [x + 8 * s + step, y], [x, y - 50 * s], [x - 8 * s - step, y], [x - 30 * s - step, y], [x - 26 * s, y - 60 * s]], col, 6, x);
  g.save(); g.fillStyle = 'rgba(40,25,10,0.18)'; g.beginPath(); g.arc(x + lean * 1.3 + 6, y - 186 * s + 6, 28 * s, 0, 7); g.fill(); g.restore();
  circle(x + lean * 1.3, y - 186 * s, 28 * s, col);
}
function heart(x, y, s, col) {
  g.save(); g.translate(x, y); g.scale(s, s); g.fillStyle = col; g.beginPath(); g.moveTo(0, 30); g.bezierCurveTo(-60, -10, -40, -60, 0, -32); g.bezierCurveTo(40, -60, 60, -10, 0, 30); g.fill(); g.restore();
}
function trophy(x, y, s, col) {   // a generic award: a star on a column on a plinth
  paper([[x - 22 * s, y], [x + 22 * s, y], [x + 22 * s, y - 16 * s], [x + 9 * s, y - 16 * s], [x + 7 * s, y - 70 * s], [x - 7 * s, y - 70 * s], [x - 9 * s, y - 16 * s], [x - 22 * s, y - 16 * s]], col, 4, x);
  const P = []; for (let k = 0; k < 10; k++) { const a = -Math.PI / 2 + k * Math.PI / 5, r = k % 2 ? 9 * s : 22 * s; P.push([x + Math.cos(a) * r, y - 92 * s + Math.sin(a) * r]); } paper(P, col, 4, x + 1);
}
// skyline: ink slabs with lit windows; k = rise 0..1
const BLD = Array.from({ length: 18 }, (_, i) => ({ x: i * 112 - 20 + hash(i) * 20, w: 90 + hash(i + 7) * 50, h: 260 + hash(i + 3) * 420, d: hash(i + 11) * 0.5 }));
function skyline(k, col = C.ink, win = C.mustard, base = H, xmin = -999) {
  BLD.forEach((b, i) => {
    if (b.x < xmin) return;
    const u = back(pr(k, b.d * 0.5, b.d * 0.5 + 0.5), 1.2); if (u <= 0) return; const h = b.h * u;
    rect(b.x, base - h, b.w, h, col);
    for (let r = 0; r < Math.floor(h / 70); r++) for (let q = 0; q < 2; q++) if (hash(i * 31 + r * 7 + q) > 0.55) rect(b.x + 18 + q * (b.w - 52), base - h + 30 + r * 70, 16, 26, win);
    // fire-escape zigzag on every third building
    if (i % 3 === 0 && h > 300) { g.strokeStyle = C.paper; g.lineWidth = 4; g.beginPath(); for (let r = 0; r < 5; r++) { const yy = base - h + 80 + r * 50; g.moveTo(b.x + 10, yy); g.lineTo(b.x + b.w - 10, yy); g.moveTo(b.x + (r % 2 ? 14 : b.w - 14), yy); g.lineTo(b.x + (r % 2 ? b.w - 14 : 14), yy + 50); } g.stroke(); }
  });
}
// pre-rendered paper grain (two tiles, alternated at 12 fps)
const GR = [0, 1].map(s => { const c = document.createElement('canvas'); c.width = 960; c.height = 540; const x = c.getContext('2d'); const im = x.createImageData(960, 540);
  for (let i = 0; i < im.data.length; i += 4) { const v = 128 + (Math.random() - .5) * 90; im.data[i] = im.data[i + 1] = im.data[i + 2] = v; im.data[i + 3] = 22; } x.putImageData(im, 0, 0); return c; });

// —— scenes: (u = scene-local time, D = scene length, L = the scene's line start, local) ——
const S = [];
S[0] = (u, D) => {   // title
  rect(0, 0, W, H, C.paper);
  circle(1380, 520, 300 * back(pr(u, 0.1, 0.6)), C.red);
  skyline(pr(u, 0.2, 1.4), C.ink, C.mustard, H, 900);
  ['WEST', 'SIDE', 'STORY'].forEach((w, k) => popTxt(w, 120, 300 + k * 205, pr(u, 0.9 + k * BEAT, 1.2 + k * BEAT), { size: 240, col: k === 2 ? C.red : C.ink, track: 6 }));
  if (u > 2.4) { g.save(); g.globalAlpha = eo(pr(u, 2.4, 2.9)); rect(110, 830, 760, 92, C.ink); txt('Romeo & Juliet, with snaps.', 140, 895, { size: 58, font: 'DMSerif', italic: true, col: C.paper }); g.restore(); }
};
S[1] = (u, D) => {   // 1949: East Side Story
  rect(0, 0, W, H, C.paper2);
  const n = Math.round(lerp(1940, 1949, eo(pr(u, 0.1, 0.8))));
  popTxt(String(n), 110, 330, pr(u, 0, 0.3), { size: 300, col: C.mustard, track: 4 });
  popTxt('EAST SIDE STORY', 110, 470, pr(u, 0.8, 1.1), { size: 150, col: C.ink, track: 4 });
  txt('the first idea', 120, 530, { size: 40, font: 'Oswald', weight: 300, col: C.ink, alpha: pr(u, 1.2, 1.6), track: 6 });
  const k = eio(pr(u, 2.6, 3.6));
  figure(lerp(2100, 1250, k), 860, 1.5, C.blue); if (u > 3.6) figure(lerp(-200, 1560, eio(pr(u, 3.6, 4.6))), 860, 1.4, C.red);
  if (u > 3.0) txt('CATHOLIC BOY', 1250, 930, { size: 44, font: 'Oswald', weight: 600, col: C.blue, align: 'center', alpha: pr(u, 3.0, 3.4), track: 4 });
  if (u > 4.4) txt('JEWISH GIRL', 1560, 930, { size: 44, font: 'Oswald', weight: 600, col: C.red, align: 'center', alpha: pr(u, 4.4, 4.8), track: 4 });
  const sU = D - 2.2; if (u > sU) {   // the stamp
    const s = lerp(2.2, 1, back(pr(u, sU, sU + 0.25), 1.2)); g.save(); g.translate(1400, 470); g.rotate(-0.16); g.scale(s, s); g.globalAlpha = 0.92;
    g.strokeStyle = C.red; g.lineWidth = 12; g.strokeRect(-300, -95, 600, 170); txt('STALLED', 0, 52, { size: 150, col: C.red, align: 'center', track: 10 }); g.restore();
  }
};
S[2] = (u, D) => {   // 1955: headlines, east becomes west
  rect(0, 0, W, H, C.paper);
  g.save(); const k = eo(pr(u, 0, 0.6)); g.translate(lerp(-900, 520, k), 520); g.rotate(lerp(-0.6, -0.06, k));
  paper(box(-380, -300, 760, 600), C.white, 14, 5);
  txt('THE DAILY', 0, -205, { size: 70, col: C.ink, align: 'center', track: 6 }); rect(-340, -185, 680, 6, C.ink);
  popTxt('1955', -330, -70, pr(u, 0.5, 0.8), { size: 120, col: C.red });
  txt('YOUTH GANGS', -330, 40, { size: 100, col: C.ink, alpha: pr(u, 0.8, 1.0) });
  for (let r = 0; r < 6; r++) for (let q = 0; q < 2; q++) rect(-330 + q * 350, 80 + r * 30, 310 - 40 * hash(r + q), 12, '#bfb6a3');
  g.restore();
  // EAST → WEST: the word flips like a sign
  const f = pr(u, D * 0.5, D * 0.5 + 0.5), sc = Math.abs(Math.cos(f * Math.PI)), word = f < 0.5 ? 'EAST' : 'WEST';
  g.save(); g.translate(1420, 560); g.scale(1, Math.max(0.02, sc)); txt(word, 0, 110, { size: 320, col: f < 0.5 ? C.ink : C.red, align: 'center', track: 8 }); g.restore();
  txt('SIDE STORY', 1420, 760, { size: 90, col: C.ink, align: 'center', track: 10, alpha: pr(u, 0.3, 0.8) });
};
S[3] = (u, D) => {   // Upper West Side: Jets vs Sharks, Tony & Maria
  const split = pr(u, 2.2, 2.7);
  rect(0, 0, W, H, C.paper);
  if (split < 1) {   // the island, and a pin on the Upper West Side
    g.save(); g.globalAlpha = 1 - split; const isl = [[880, 60], [960, 40], [1010, 200], [1060, 420], [1050, 650], [990, 900], [930, 1040], [880, 960], [860, 700], [840, 420], [850, 200]];
    paper(isl, C.ink, 10, 9); rect(0, 0, 0, 0, C.ink);
    const pk = back(pr(u, 0.4, 0.8)); g.save(); g.translate(890, 330); g.scale(pk, pk); paper([[0, 0], [-34, -60], [-34, -96], [0, -120], [34, -96], [34, -60]], C.red, 6, 3); circle(0, -84, 14, C.paper); g.restore();
    popTxt('UPPER WEST SIDE', 1110, 300, pr(u, 0.7, 1.0), { size: 110, col: C.red, track: 4 }); txt('Manhattan, New York', 1114, 360, { size: 40, font: 'Oswald', weight: 300, alpha: pr(u, 1.0, 1.4), track: 4 });
    g.restore();
  }
  if (split > 0) {
    const w = W / 2 * eio(split);
    rect(W / 2 - w, 0, w, H, C.blue); rect(W / 2, 0, w, H, C.red);
    popTxt('JETS', 120, 230, pr(u, 2.6, 2.9), { size: 200, col: C.paper, track: 8 });
    popTxt('SHARKS', W - 120, 230, pr(u, 3.0 + BEAT, 3.3 + BEAT), { size: 200, col: C.paper, align: 'right', track: 8 });
    const tm = D - 3.4;   // Tony and Maria step to the line
    for (let k = 0; k < 4; k++) {
      const a = pr(u, 2.7 + k * BEAT * 0.5, 3.0 + k * BEAT * 0.5), b = pr(u, 3.0 + BEAT + k * BEAT * 0.5, 3.3 + BEAT + k * BEAT * 0.5);
      figure(lerp(-200, 140 + k * 150, eo(a)), 900, 1.3, C.ink, 4); figure(lerp(W + 200, W - 140 - k * 150, eo(b)), 900, 1.3, C.ink, -4);
    }
    const m = eio(pr(u, tm, tm + 1.2));
    figure(lerp(700, 820, m), 900, 1.45, C.paper, 6, 6 * Math.sin(m * 9)); figure(lerp(W - 700, W - 820, m), 900, 1.45, C.paper, -6, 6 * Math.sin(m * 9));
    if (u > tm) { txt('TONY', lerp(700, 820, m), 560, { size: 60, col: C.paper, align: 'center', track: 6 }); txt('MARIA', lerp(W - 700, W - 820, m), 560, { size: 60, col: C.paper, align: 'center', track: 6 }); }
    rect(W / 2 - 4, 0, 8, H, C.paper);
    if (u > tm + 1.1) heart(W / 2, 420, back(pr(u, tm + 1.1, tm + 1.4)) * 2.2, C.mustard);
  }
};
S[4] = (u, D) => {   // the four creators
  rect(0, 0, W, H, C.ink);
  const P = [['JEROME ROBBINS', 'direction + choreography', C.red], ['LEONARD BERNSTEIN', 'music', C.mustard], ['ARTHUR LAURENTS', 'book', C.blue], ['STEPHEN SONDHEIM', 'lyrics · his Broadway debut', C.paper]];
  const ts = [0.2, D * 0.33, D * 0.52, D * 0.68];
  P.forEach(([n, r, col], k) => {
    const v = back(pr(u, ts[k], ts[k] + 0.35), 1.3), x = 80 + k * 450;
    g.save(); g.translate(x + 200, 1100 - 560 * v); g.rotate((1 - eo(pr(u, ts[k], ts[k] + 0.35))) * 0.2 * (k % 2 ? 1 : -1));
    paper(box(-200, -500, 400, 560), col, 12, k + 20);
    const tc = col === C.paper || col === C.mustard ? C.ink : C.paper;
    txt(String(k + 1).padStart(2, '0'), -170, -400, { size: 90, col: tc });
    const [a, b] = n.split(' '); txt(a, -170, -150, { size: 64, col: tc, track: 3 }); txt(b, -170, -60, { size: 84, col: tc, track: 2 });
    rect(-170, -30, 120, 6, tc); txt(r, -170, 20, { size: 30, font: 'Oswald', weight: 300, col: tc, track: 2 });
    g.restore();
  });
};
S[5] = (u, D) => {   // 1957: the marquee
  rect(0, 0, W, H, C.red);
  const k = eo(pr(u, 0, 0.5));
  g.save(); g.translate(0, (1 - k) * -700);
  paper(box(260, 120, 1400, 520), C.ink, 16, 30);
  for (let i = 0; i < 44; i++) { const bx = i < 22 ? 300 + i * 63 : 300 + (i - 22) * 63, by = i < 22 ? 150 : 610; circle(bx, by, 11, (Math.floor(u * 8) + i) % 3 === 0 ? C.white : C.mustard); }
  txt('WINTER GARDEN THEATRE', 960, 250, { size: 52, font: 'Oswald', weight: 300, col: C.paper, align: 'center', track: 10 });
  txt('WEST SIDE STORY', 960, 440, { size: 190, col: C.paper, align: 'center', track: 6 });
  txt('BROADWAY · 1957', 960, 545, { size: 64, col: C.mustard, align: 'center', track: 12 });
  g.restore();
  const n = Math.round(732 * eio(pr(u, D * 0.45, D - 0.6)));
  popTxt(String(n), 960, 900, pr(u, D * 0.42, D * 0.42 + 0.3), { size: 230, col: C.paper, align: 'center', track: 6 });
  txt('PERFORMANCES', 960, 980, { size: 54, font: 'Oswald', weight: 600, col: C.ink, align: 'center', track: 14, alpha: pr(u, D * 0.5, D * 0.5 + 0.3) });
};
S[6] = (u, D) => {   // the Tonys
  rect(0, 0, W, H, C.paper);
  popTxt('1958 TONY AWARDS', 960, 170, pr(u, 0, 0.3), { size: 110, col: C.ink, align: 'center', track: 6 });
  txt('BEST MUSICAL', 960, 230, { size: 44, font: 'Oswald', weight: 600, col: C.red, align: 'center', track: 14, alpha: pr(u, 0.3, 0.6) });
  const r = eio(pr(u, D * 0.55, D * 0.55 + 0.6));
  g.save(); g.translate(560, 600 + r * 140); g.rotate(r * 0.12); paper(box(-300, -180, 600, 360), C.ink, 12, 40); txt('WEST SIDE STORY', 0, 20, { size: 92, col: C.paper, align: 'center', track: 3 }); g.restore();
  g.save(); g.translate(1360, 600 - r * 80); g.scale(1 + 0.08 * r, 1 + 0.08 * r); paper(box(-300, -180, 600, 360), r > 0.5 ? C.mustard : C.paper2, 12, 41); txt('THE MUSIC MAN', 0, 20, { size: 92, col: C.ink, align: 'center', track: 3 }); g.restore();
  if (r > 0.6) { trophy(1360, 360 - 80, 1.6 * back(pr(u, D * 0.55 + 0.6, D * 0.55 + 0.9)), C.mustard); txt('WINNER', 1360, 870, { size: 70, col: C.ink, align: 'center', track: 12 }); }
  if (r > 0.9) txt('West Side Story still won two: choreography and scenic design.', 560, 900, { size: 32, font: 'Oswald', weight: 300, col: C.ink, align: 'center', alpha: pr(u, D * 0.55 + 0.8, D * 0.55 + 1.2) });
};
S[7] = (u, D) => {   // the 1961 film; Rita Moreno
  const half = D * 0.42, k2 = eio(pr(u, half, half + 0.5));
  rect(0, 0, W, H, C.ink);
  for (let i = 0; i < 24; i++) { const x = ((i * 90 - u * 160) % 2160 + 2160) % 2160 - 120; rect(x, 40, 50, 34, C.paper2); rect(x, H - 74, 50, 34, C.paper2); }
  g.save(); g.translate(-k2 * W, 0);
  popTxt('THE 1961 FILM', 960, 240, pr(u, 0, 0.3), { size: 100, col: C.paper, align: 'center', track: 8 });
  popTxt('10', 520, 700, pr(u, 0.3, 0.6), { size: 420, col: C.mustard, align: 'center' });
  txt('OSCARS', 520, 800, { size: 80, col: C.paper, align: 'center', track: 14, alpha: pr(u, 0.5, 0.8) });
  for (let i = 0; i < 10; i++) { const s = back(pr(u, 0.6 + i * 0.12, 0.85 + i * 0.12)); if (s > 0) trophy(940 + (i % 5) * 170, 560 + Math.floor(i / 5) * 230, s * 1.3, C.mustard); }
  if (u > 1.9) { rect(940, 830, 600, 80, C.red); txt('BEST PICTURE', 1240, 892, { size: 64, col: C.paper, align: 'center', track: 10 }); }
  g.restore();
  if (k2 > 0) {
    g.save(); g.translate(W * (1 - k2), 0); rect(0, 0, W, H, C.red);
    figure(420, 940, 3.0, C.ink, 10, 0); trophy(640, 640, 2.2, C.mustard);
    popTxt('RITA MORENO', 800, 400, pr(u, half + 0.4, half + 0.7), { size: 170, col: C.paper, track: 6 });
    txt('as ANITA', 810, 470, { size: 60, font: 'DMSerif', italic: true, col: C.ink, alpha: pr(u, half + 0.6, half + 0.9) });
    popTxt('THE FIRST LATINA ACTRESS', 800, 640, pr(u, half + 1.6, half + 1.9), { size: 96, col: C.ink, track: 4 });
    popTxt('TO WIN AN OSCAR', 800, 740, pr(u, half + 1.8, half + 2.1), { size: 96, col: C.ink, track: 4 });
    g.restore();
  }
};
S[8] = (u, D) => {   // sixty years later: the same role
  rect(0, 0, W, H, C.paper);
  const k = eio(pr(u, 0.2, 1.6));
  rect(260, 540, 1400 * k, 8, C.ink);
  [[260, '1962', 'RITA MORENO', C.red], [1660, '2022', 'ARIANA DeBOSE', C.blue]].forEach(([x, y, n, col], i) => {
    const a = i ? pr(u, 1.4, 1.8) : pr(u, 0, 0.3); if (a <= 0) return;
    circle(x, 544, 34 * back(a), col);
    popTxt(y, x, 460, a, { size: 130, col, align: 'center', track: 6 });
    txt(n, x, 660, { size: 74, col: C.ink, align: 'center', track: 4, alpha: a });
    txt('as Anita · Best Supporting Actress', x, 715, { size: 30, font: 'Oswald', weight: 300, col: C.ink, align: 'center', alpha: a });
  });
  if (u > 0.4) txt(String(Math.round(60 * eio(pr(u, 0.4, 1.6)))) + ' YEARS', 960, 520, { size: 90, col: C.mustard, align: 'center', track: 10 });
  if (u > 2.3) { const s = back(pr(u, 2.3, 2.6)); g.save(); g.translate(960, 870); g.scale(s, s); rect(-260, -70, 520, 100, C.ink); txt('SAME ROLE', 0, 12, { size: 84, col: C.mustard, align: 'center', track: 14 }); g.restore(); }
};
S[9] = (u, D) => {   // outro
  rect(0, 0, W, H, C.paper);
  const k = eio(pr(u, 0, 0.6));
  rect(0, 0, W / 2 * k, H, C.blue); rect(W - W / 2 * k, 0, W / 2 * k, H, C.red);
  skyline(pr(u, 0.2, 1.2), C.ink, C.mustard, H);
  const tl = pr(u, 0.4, 0.7), tl2 = pr(u, 0.9, 1.2);
  g.save(); rect(0, 250, W, 300 * eo(pr(u, 0.3, 0.6)), C.paper);
  popTxt("SOME STORIES DON'T STAY", 960, 380, tl, { size: 120, col: C.ink, align: 'center', track: 4 });
  popTxt('ON ONE SIDE OF TOWN.', 960, 500, tl2, { size: 120, col: C.red, align: 'center', track: 4 });
  g.restore();
  if (u > D - 2.4) { const a = pr(u, D - 2.4, D - 1.9); g.save(); g.globalAlpha = a; rect(0, 0, W, H, C.ink); txt('WEST SIDE STORY', 960, 520, { size: 200, col: C.paper, align: 'center', track: 10 }); txt('BROADWAY 1957 · FILM 1961 · FILM 2021', 960, 610, { size: 44, font: 'Oswald', weight: 300, col: C.mustard, align: 'center', track: 10 }); txt('Sources: Wikipedia, History.com, Britannica, BroadwayWorld, Playbill, NPR', 960, 990, { size: 26, font: 'Oswald', weight: 300, col: C.paper2, align: 'center', track: 2 }); g.restore(); }
};

// captions: one line in a slim ink bar along the bottom
function caption(t) {
  const s = SUBS.find(x => t >= x.t0 && t < x.t1); if (!s) return;
  g.save(); g.font = '400 40px Oswald'; g.letterSpacing = '1px'; let rows = [s.text];
  if (g.measureText(s.text).width > 1600) { const w = s.text.split(' '); let best = 1, bd = 1e9; for (let j = 1; j < w.length; j++) { const d = Math.abs(g.measureText(w.slice(0, j).join(' ')).width - g.measureText(w.slice(j).join(' ')).width); if (d < bd) { bd = d; best = j; } } rows = [w.slice(0, best).join(' '), w.slice(best).join(' ')]; }
  const tw = Math.max(...rows.map(r => g.measureText(r).width)), hh = rows.length * 50 + 24, y0 = H - 40 - hh;
  g.globalAlpha = 0.86; g.fillStyle = C.ink; g.fillRect(W / 2 - tw / 2 - 28, y0, tw + 56, hh); g.globalAlpha = 1;
  g.fillStyle = C.white; g.textAlign = 'center'; rows.forEach((r, j) => g.fillText(r, W / 2, y0 + 50 + j * 50)); g.restore();
}

function render(t) {
  g.setTransform(1, 0, 0, 1, 0, 0); g.globalAlpha = 1;
  let i = SC.length - 1; while (SC[i].t0 > t) i--;
  const u = t - SC[i].t0, D = SC[i].t1 - SC[i].t0;
  S[i](u, D);
  // red paper wipe across every cut: it covers the old scene, the cut happens under it, then it leaves
  const prev = i > 0 ? t - SC[i].t0 : 99, next = i < SC.length - 1 ? SC[i + 1].t0 - t : 99;
  const wipe = next < 0.22 ? -1 + next / 0.22 : prev < 0.22 ? prev / 0.22 : null;
  if (wipe !== null) { const x = wipe < 0 ? W * (1 + wipe) : -W * eo(wipe); paper([[x - 80, 0], [x + W + 80, 0], [x + W, H], [x - 160, H]], i % 2 ? C.red : C.mustard, 0, i); }
  caption(t);
  g.drawImage(GR[Math.floor(t * 12) % 2], 0, 0, W, H);
}
window.DUR = DUR; window.EV = EV; window.SUBS = SUBS; window.render = render; window.SC = SC; window.LINES = LINES;
window.READY = true;
