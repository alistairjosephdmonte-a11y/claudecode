// रामायण, a pop-up book: a scene engine. Every scene in script.js is one spread; timing comes from the narration.
import * as THREE from 'three';
import { RGBELoader } from 'three/addons/loaders/RGBELoader.js';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { clamp, lerp, seg, ss, eio, eo, back, TAU, mulberry, track, spring } from './lib.js';
import { cv, INK } from './paper.js';
import { makeBook, coverCanvases, texOf, BW, BD, PG } from './book.js';
import { pages, PAGES } from './pages.js';
import { makeStick, drawStick, CAST, SW, SH } from './actors.js';
import { cutMesh, thread, particles } from './cutmesh.js';
import { makePost } from './post.js';
import * as ART from './art.js';
import * as P1 from './props.js';
import * as P2 from './props2.js';
import { SCENES, META } from './script.js';
import * as HUD from './hud.js';

const W = 1920, H = 1080, QS = new URLSearchParams(location.search);
const renderer = new THREE.WebGLRenderer({ antialias: false, preserveDrawingBuffer: true, powerPreference: 'high-performance' });
renderer.setSize(W, H); renderer.setPixelRatio(1);
const SHM = parseInt(QS.get('shm') || '2048');
renderer.shadowMap.enabled = QS.get('sh') !== '0'; renderer.shadowMap.type = THREE.PCFSoftShadowMap;
renderer.toneMapping = THREE.NeutralToneMapping; renderer.outputColorSpace = THREE.SRGBColorSpace;
document.getElementById('stage').appendChild(renderer.domElement);
const OX = document.getElementById('ov').getContext('2d');
const scene = new THREE.Scene();
const cam = new THREE.PerspectiveCamera(30, W / H, .004, 30);
const RS = parseFloat(QS.get('rs') || '.75');
if (RS !== 1) renderer.setSize(W * RS, H * RS, false);
const post = makePost(renderer, scene, cam, W * RS, H * RS);

// ---------- assets ----------
await Promise.all(['500 40px Fredoka', '40px "Lilita One"', 'italic 40px "IM Fell English"', '50px "Tiro Devanagari Sanskrit"', '600 40px "Baloo 2"', '800 40px "Baloo 2"', '40px "Tiro Devanagari Hindi"', 'italic 40px "Tiro Devanagari Hindi"'].map(f => document.fonts.load(f, 'Aaराम')));
const DURS = await (await fetch('voices/dur.json')).json();
const hdr = await new RGBELoader().loadAsync('assets/lythwood_lounge_2k.hdr'); hdr.mapping = THREE.EquirectangularReflectionMapping;
scene.environment = hdr; scene.background = hdr; scene.backgroundBlurriness = .22;
scene.backgroundRotation.set(0, 2.3, 0); scene.environmentRotation.set(0, 2.3, 0);
const tl = new THREE.TextureLoader();
const wt = n => { const t = tl.load(`assets/walnut_${n}.jpg`); t.wrapS = t.wrapT = THREE.RepeatWrapping; t.repeat.set(2.2, 1.4); t.anisotropy = 8; return t; };
const wdiff = wt('diff'); wdiff.colorSpace = THREE.SRGBColorSpace;
const desk = new THREE.Mesh(new THREE.BoxGeometry(2.6, .04, 1.7), new THREE.MeshStandardMaterial({ map: wdiff, normalMap: wt('nor'), roughnessMap: wt('rough'), color: '#c9a88a', envMapIntensity: .8 }));
desk.position.set(0, -.02, .25); desk.receiveShadow = true; scene.add(desk);
const gl = new GLTFLoader();
async function prop(name, x, z, s, ry) {
  const m = (await gl.loadAsync(`assets/${name}/${name}.gltf`)).scene;
  m.position.set(x, 0, z); m.scale.setScalar(s); m.rotation.y = ry;
  m.traverse(o => { if (o.isMesh) o.castShadow = o.receiveShadow = true; }); scene.add(m); return m;
}
const lamp = await prop('desk_lamp_arm_01', -.347, .51, .55, -.76);
lamp.traverse(o => { if (o.isMesh && o.material.name.includes('light')) { o.material = o.material.clone(); o.material.emissive = new THREE.Color('#ffd9a0'); o.material.emissiveIntensity = 6; } });
const tea = await prop('tea_set_01', 0, 0, 1, 0);
{ const keep = { tea_set_01_teapot_01: [.52, .2, .5], tea_set_01_teapot_01_lid: [.52, .2, .5], tea_set_01_cup_small_01: [.36, .5, 2.2], tea_set_01_saucer_circular_04: [.36, .5, 0] }, dead = [];
  tea.traverse(o => { if (!o.name.startsWith('tea_set_01_')) return; const k = keep[o.name]; if (!k) dead.push(o); else { o.position.x = k[0]; o.position.z = k[1]; o.rotation.y = k[2]; } });
  dead.forEach(o => o.parent && o.parent.remove(o)); tea.traverse(o => { if (o.name === 'tea_set_01_cup_small_01') o.position.y += .012; }); }
{ // marigold garland and a brass diya on the desk
  const g = new THREE.Group(), R = mulberry(4);
  for (let i = 0; i < 46; i++) { const a = i / 46 * Math.PI * 1.25 - .3, r = .17; const m = new THREE.Mesh(new THREE.SphereGeometry(.0085, 10, 8), new THREE.MeshStandardMaterial({ color: R() < .5 ? '#f29a1a' : '#f6b81e', roughness: .9 })); m.position.set(Math.cos(a) * r * 1.4, .007, Math.sin(a) * r * .5); m.scale.y = .8; m.castShadow = m.receiveShadow = true; g.add(m); }
  g.position.set(.42, 0, .62); g.rotation.y = .4; scene.add(g);
  const brass = new THREE.MeshStandardMaterial({ color: '#c9933a', metalness: 1, roughness: .32 });
  const diya = new THREE.Mesh(new THREE.SphereGeometry(.03, 24, 12, 0, TAU, Math.PI / 2, Math.PI / 2), brass); diya.scale.y = .55; diya.rotation.x = Math.PI; diya.position.set(-.42, .016, .2); diya.castShadow = true; scene.add(diya);
  const flame = new THREE.Mesh(new THREE.SphereGeometry(.006, 12, 8), new THREE.MeshBasicMaterial({ color: new THREE.Color(4, 2.2, .6) })); flame.scale.set(1, 2, 1); flame.position.set(-.42, .03, .2); scene.add(flame);
}

// ---------- the timeline, from the narration ----------
const OPEN = [3.5, 6.0], TURN_D = 2.6, GAP = .9;
const LAY = [];
{
  let prevE = 0;
  SCENES.forEach((sc, i) => {
    const L = { i, sc, page: sc.page };
    const newPage = i > 0 && sc.page !== SCENES[i - 1].page;
    if (i === 0) { L.S = OPEN[1]; L.R = OPEN[1] + .3; }
    else if (newPage) { L.S = prevE + .1; L.turn = [L.S, L.S + TURN_D]; L.R = L.S + TURN_D - .9; }
    else { L.S = prevE + .75; L.R = L.S; }
    let v = L.R + (sc.lead ?? 2.4); L.vo = [];
    for (const [id, text, pause] of sc.vo) { const d = DURS[id] ?? 3; L.vo.push({ id, t0: v, d, text }); v += d + GAP + (pause || 0); }
    L.E = Math.max(v - GAP + (sc.tail ?? 2.4), L.R + (sc.min ?? 0));
    L.T = spec => {
      if (typeof spec === 'number') return L.R + spec;
      const m = /^(v(\d+)(e?)|E|R)([+-][\d.]+)?$/.exec(spec); if (!m) throw new Error('bad time ' + spec + ' in ' + sc.id);
      const base = m[1] === 'E' ? L.E : m[1] === 'R' ? L.R : (m[3] ? L.vo[+m[2]].t0 + L.vo[+m[2]].d : L.vo[+m[2]].t0);
      return base + (m[4] ? parseFloat(m[4]) : 0);
    };
    LAY.push(L); prevE = L.E;
  });
}
const LAST = LAY[LAY.length - 1], CLOSE = [LAST.E + .2, LAST.E + 3.0], TITLE_T = CLOSE[1] + 1.4, DUR = Math.round((TITLE_T + 9.0) * 24) / 24;
const TURNS = LAY.filter(L => L.turn).map(L => [L.turn[0], L.turn[1], L.i]);
const sceneAt = t => { let k = 0; for (const L of LAY) if (t >= L.S) k = L.i; return LAY[k]; };

// ---------- the book ----------
const cover = coverCanvases((x, px, py, w, h) => {
  x.save(); x.translate(px + w / 2, py + h / 2);
  x.fillStyle = '#f4e9cf'; x.beginPath(); x.arc(0, 0, w * .55, 0, TAU); x.fill();
  for (let i = 0; i < 8; i++) { x.save(); x.rotate(i / 8 * TAU); x.beginPath(); x.ellipse(0, -w * .22, w * .08, w * .2, 0, 0, TAU); x.fillStyle = i % 2 ? '#f29ab0' : '#e8708a'; x.fill(); x.lineWidth = 6; x.strokeStyle = INK; x.stroke(); x.restore(); }
  x.beginPath(); x.moveTo(-w * .4, -w * .3); x.quadraticCurveTo(0, w * .35, w * .4, -w * .3); x.lineWidth = 26; x.strokeStyle = INK; x.stroke(); x.lineWidth = 14; x.strokeStyle = '#5b8de0'; x.stroke();
  x.beginPath(); x.moveTo(-w * .4, -w * .3); x.lineTo(w * .4, -w * .3); x.lineWidth = 4; x.strokeStyle = INK; x.stroke();
  x.beginPath(); x.moveTo(0, w * .3); x.lineTo(0, -w * .48); x.lineWidth = 8; x.stroke(); x.beginPath(); x.moveTo(0, -w * .55); x.lineTo(-w * .05, -w * .44); x.lineTo(w * .05, -w * .44); x.closePath(); x.fillStyle = '#f2b632'; x.fill(); x.stroke();
  x.restore();
}, { title: ['महर्षि वाल्मीकि की', 'रामायण', ''], tag: '~ एक चित्र-कथा ~', cloth: '#7a2321', fonts: ['800 120px "Baloo 2"', '800 250px "Baloo 2"', '64px "Tiro Devanagari Hindi"'] });
const book = makeBook(cover); scene.add(book.root);
const PP = pages(), PT = {}; for (const k in PP) PT[k] = texOf(PP[k]);
const pageTex = name => { const p = PAGES[name]; if (!p) throw new Error('page ' + name); return { sky: PT[p[0]], ground: PT[p[1]], sun: p[2], col: new THREE.Color(p[3]) }; };

// ---------- pop-ups ----------
const K = { ...ART, ...P1, ...P2 };
const POPS = [];
function riseOf(r, t) {
  const tf = r.t1 ?? (r.L.E + (.3 - r.g.position.z) * .6);
  const up = r.pop ? back(seg(t, r.t0, r.t0 + .55), 1.7) : (t >= r.t0 ? 1 : 0);
  return Math.min(up, 1 - ss(seg(t, tf, tf + .4)));
}
for (const L of LAY) {
  if (!L.sc.set) continue;
  for (const [item, x, z, o = {}] of L.sc.set(K)) {
    const g = new THREE.Group(); g.position.set(x, o.y || 0, z);
    const m = cutMesh(item, o); if (o.ry) m.rotation.y = o.ry; if (o.flip) m.scale.x = -1;
    g.add(m); book.stage.add(g);
    const d = o.d ?? (.3 - z) * 1.2;
    POPS.push({ g, m, L, t0: o.t0 !== undefined ? L.T(o.t0) : L.R + d, t1: o.t1 !== undefined ? L.T(o.t1) : undefined, dir: o.dir ?? (z > .15 ? -1 : 1), sway: o.sway || 0, ph: x * 40, pop: o.pop !== false, bob: o.bob || 0 });
  }
}
function updatePops(t) {
  for (const r of POPS) {
    if (t < r.L.S - 1 || t > r.L.E + 1.2) { r.g.visible = false; continue; }
    const k = riseOf(r, t); r.g.visible = k > .002; if (!r.g.visible) continue;
    r.g.rotation.x = r.dir * (Math.PI / 2) * (1 - k);
    if (r.sway) r.m.rotation.z = Math.sin(t * 1.6 + r.ph) * r.sway * k;
    if (r.bob) r.m.position.y = Math.sin(t * 2.2 + r.ph) * r.bob;
  }
}

// ---------- movers: props on paths (arrows, chariots, birds, crowns…) ----------
const MOV = [];
for (const L of LAY) {
  if (!L.sc.mv) continue;
  L.sc.mv(K).forEach((o, j) => {
    const g = new THREE.Group(), m = cutMesh(o.item, o); g.add(m);
    if (o.thread) { const th = thread(o.thread); th.position.set(0, (o.item.h * (o.item.ay ?? 1)) * .9, -.0004); g.add(th); }
    g.visible = false; book.stage.add(g);
    const keys = o.keys.map(k => [L.T(k[0]), [k[1], k[2], k[3], k[4] ?? 0, k[5] ?? 0, k[6] ?? 1]]);
    const f = keys.length > 1 ? track(keys.map(k => [k[0], k[1]])) : () => keys[0][1];
    MOV.push({ g, m, L, f, o, name: o.name || `m${j}`, t0: o.t0 !== undefined ? L.T(o.t0) : keys[0][0], t1: o.t1 !== undefined ? L.T(o.t1) : keys[keys.length - 1][0], ease: o.ease });
  });
}
const movAt = (r, t) => { const v = r.f(r.ease === 'step' ? t : t); return v; };
function updateMovers(t, phase, actorPos) {
  for (const r of MOV) {
    if (!!r.o.follow !== (phase === 2)) continue;
    const vis = t >= r.t0 && t <= r.t1; r.g.visible = vis; if (!vis) continue;
    const v = movAt(r, t);
    let x = v[0], y = v[1], z = v[2];
    if (r.o.follow) { const a = actorPos[r.o.follow]; if (!a) { r.g.visible = false; continue; } x += a.x; y += a.y; z += a.z; }
    r.g.position.set(x, y, z); r.g.rotation.set(v[4], 0, v[3] + (r.o.flap ? Math.sin(t * 11) * r.o.flap : 0) + (r.o.spin ? t * r.o.spin : 0));
    const pk = r.o.pop ? back(seg(t, r.t0, r.t0 + .35), 1.8) : 1;
    const fo = r.o.fade ? 1 - seg(t, r.t1 - .25, r.t1) : 1;
    r.g.scale.setScalar(Math.max(1e-4, v[5] * pk * fo));
    if (r.o.bob) r.g.position.y += Math.sin(t * 3 + r.t0) * r.o.bob;
  }
}
const moverPos = (L, name, t) => { const r = MOV.find(m => m.L === L && m.name === name); const v = movAt(r, t); return { x: v[0], y: v[1], z: v[2] }; };

// ---------- actors ----------
const ACT = {};
for (const L of LAY) for (const key in (L.sc.cast || {})) if (!ACT[key]) {
  const spec = CAST[key.split('#')[0]]; if (!spec) throw new Error('cast ' + key);
  const h = (L.sc.cast[key].h) ?? .044;
  const a = makeStick(spec, h); book.stage.add(a.root); book.stage.add(a.shadow); a.root.visible = a.shadow.visible = false; ACT[key] = a;
}
const blinkAt = (t, o = 0) => { const p = (t + o) % 3.9; return p < .12 ? Math.sin(p / .12 * Math.PI) : 0; };
const singing = t => Math.sin(t * 9) > 0 ? 'sing' : 'open';
const NUM = new Set(['armL', 'armR', 'elbowL', 'elbowR', 'lean', 'dir']);
function actorAt(L, key, t) {
  const a = L.sc.cast[key], T = L.T, P = { armL: .2, armR: .2, elbowL: .15, elbowR: .15, dir: a.dir ?? 0, ...a.pose };
  P.look = a.look ?? [(a.dir ?? 0) * 1.2, 0];
  const S = { vis: false, x: a.at[0], y: a.y ?? 0, z: a.at[1], s: 1, lie: 0, sx: 1, sy: 1 };
  const t0 = T(a.t0 ?? .4), tf = (a.t1 !== undefined ? T(a.t1) : L.E) + (.3 - S.z) * .6;
  S.vis = t > t0 && t < tf + .45; S.s = back(seg(t, t0, t0 + .4), 2); S.lie = ss(seg(t, tf, tf + .4));
  let mouth = null, grow = 1, hidden = 1;
  P.blink = blinkAt(t, key.length * .37);
  for (const b of a.b || []) {
    const tb = T(b[1]); if (t < tb) continue;
    const kind = b[0];
    if (kind === 'walk' || kind === 'run') {
      const te = T(b[2]), k = seg(t, tb, te), [x2, z2] = b[3], x1 = S.x, z1 = S.z;
      S.x = lerp(x1, x2, k); S.z = lerp(z1, z2, k);
      if (t < te) { const ph = Math.hypot(x2 - x1, z2 - z1) * k / (kind === 'run' ? .02 : .014) * TAU; P.walk = ph; P.stride = kind === 'run' ? 1.3 : 1; P.armL = .25 + Math.sin(ph) * .45; P.armR = .25 - Math.sin(ph) * .45; P.dir = Math.sign(x2 - x1) * .7; P.look = [P.dir, 0]; }
      else { P.walk = 0; P.stride = 0; }
    } else if (kind === 'hop' || kind === 'leap') {
      const te = T(b[2]), k = seg(t, tb, te), [x2, z2] = b[3], h = b[4] ?? .03;
      const x1 = S.x, z1 = S.z; S.x = lerp(x1, x2, k); S.z = lerp(z1, z2, k); S.y += 4 * h * k * (1 - k);
      if (t < te) { P.armL = P.armR = 2.4; P.dir = Math.sign(x2 - x1) * .6; }
      const ld = seg(t, te, te + .25); if (ld > 0 && ld < 1) { S.sy = 1 - .25 * Math.sin(ld * Math.PI); S.sx = 1 + .15 * Math.sin(ld * Math.PI); }
    } else if (kind === 'fly') {
      const te = T(b[2]), k = eio(seg(t, tb, te)), [x2, y2, z2] = b[3]; S.x = lerp(S.x, x2, k); S.y = lerp(S.y, y2, k); S.z = lerp(S.z, z2, k);
    } else if (kind === 'ride') {
      const te = T(b[2]); if (t <= te) { const m = moverPos(L, b[3], t), o = b[4] || [0, 0, 0], k = ss(seg(t, tb, tb + .4)); S.x = lerp(S.x, m.x + o[0], k); S.y = lerp(S.y, m.y + o[1], k); S.z = lerp(S.z, m.z + o[2], k); }
      else { const m = moverPos(L, b[3], te), o = b[4] || [0, 0, 0]; S.x = m.x + o[0]; S.y = m.y + o[1]; S.z = m.z + o[2]; }
    } else if (kind === 'pose') {
      const k = ss(seg(t, tb, tb + (b[3] ?? .35)));
      for (const [pk, v] of Object.entries(b[2])) { if (NUM.has(pk) && typeof P[pk] === 'number') P[pk] = lerp(P[pk], v, k); else if (k > .5 || typeof v !== 'number') P[pk] = v; }
    } else if (kind === 'talk') { if (t < T(b[2])) mouth = Math.sin(t * 13 + key.length) > -.2 ? 'open' : (P.mouth === 'sad' ? 'sad' : 'smile'); }
    else if (kind === 'sing') { if (t < T(b[2])) mouth = singing(t + key.length); }
    else if (kind === 'lie') S.lie = Math.max(S.lie, ss(seg(t, tb, tb + (b[2] ?? .45))));
    else if (kind === 'up') S.lie *= 1 - ss(seg(t, tb, tb + .5));
    else if (kind === 'hide') hidden = 1 - ss(seg(t, tb, tb + (b[2] ?? .35)));
    else if (kind === 'show') { hidden = back(seg(t, tb, tb + .4), 2); }
    else if (kind === 'grow') { const te = T(b[2]); grow = lerp(grow, b[3], eio(seg(t, tb, te))); }
    else if (kind === 'shake') { if (t < T(b[2])) S.x += Math.sin(t * 47) * (b[3] ?? .0015); }
    else if (kind === 'bounce') { if (t < T(b[2])) S.y += Math.abs(Math.sin((t - tb) * (b[3] ?? 7))) * (b[4] ?? .004); }
    else if (kind === 'crouch') { const k = seg(t, tb, tb + (b[2] ?? .4)); if (k < 1) { S.sy = 1 - .25 * Math.sin(k * Math.PI); S.sx = 1 + .15 * Math.sin(k * Math.PI); } }
  }
  // actors that start hidden until a 'show' beat
  if ((a.b || []).some(b => b[0] === 'show') && t < T(a.b.find(b => b[0] === 'show')[1])) hidden = 0;
  if (mouth) P.mouth = mouth;
  S.s *= grow * hidden; if (hidden <= .01) S.vis = false;
  if (Math.abs(S.x) > .228 && !a.edge) S.vis = false;
  S.pose = P; return S;
}

// ---------- camera ----------
const CAMV = {
  T: [.0, .15, .62, .0, .08, .1, 30, 1.9], W: [.0, .13, .6, .0, .055, .11, 30, 1.95], M: [.0, .095, .5, .0, .05, .13, 30, 2.05],
  L: [-.08, .078, .45, -.1, .045, .14, 30, 2.2], R: [.08, .078, .45, .1, .045, .14, 30, 2.2], HI: [.0, .2, .5, .0, .09, .1, 30, 2.0],
};
const actorPosAt = (L, key, t) => { const s = actorAt(L, key, t); return s; };
function frame(L, F, t) {
  if (Array.isArray(F)) { const [x, z, d, y = 0] = F; return [x * .7, .03 + y + d * .12, z + d, x, .036 + y, z - .005, 30, 2.1 + (.34 - d) * 2]; }
  if (CAMV[F]) return CAMV[F].slice();
  let [who, mode] = F.split(':'); const names = who.split('+');
  const ps = names.map(n => actorPosAt(L, n, t)); const x = ps.reduce((a, p) => a + p.x, 0) / ps.length, z = ps.reduce((a, p) => a + p.z, 0) / ps.length, y = ps.reduce((a, p) => a + p.y, 0) / ps.length;
  const sep = Math.max(...ps.map(p => p.x)) - Math.min(...ps.map(p => p.x));
  let d = mode === 'c' ? .21 : mode === 'm' ? .34 : mode === 'w' ? .44 : .27; d = Math.max(d, sep * 1.25 + .16);
  const hs = (L.sc.cast[names[0]].h ?? .044) / .044;
  return [x * .7, .03 + y + d * .12 * hs, z + d, x, .033 * hs + y, z - .005, 30, 2.1 + (.34 - d) * 2];
}
const SEGS = [];
{
  let keys = [[0, [.52, .34, 1.08, -.02, .1, .2, 34, 3.0]], [3.0, [.26, .3, .86, .0, .06, .16, 32, 3.0]], [5.6, [.02, .2, .68, .0, .09, .12, 30, 2.6]]];
  const pushSeg = () => { if (keys.length) SEGS.push({ t0: keys[0][0], f: track(keys) }); keys = []; };
  const add = (t, v) => { if (keys.length && t <= keys[keys.length - 1][0] + .05) keys[keys.length - 1] = [keys[keys.length - 1][0], v]; else keys.push([t, v]); };
  const push = (v, k) => { const o = v.slice(); for (let i = 0; i < 3; i++) o[i] = lerp(v[i], v[i + 3], k); return o; };
  for (const L of LAY) {
    if (L.turn) { add(L.turn[0] + .2, CAMV.T); add(L.turn[1] - .5, CAMV.T); }
    const shots = [[0, 'W'], ...(L.sc.cam || [])].map(([ts, F, o]) => [L.T(ts), F, o || {}]).sort((a, b) => a[0] - b[0]);
    shots.forEach(([ts, F, o], k) => {
      const next = k + 1 < shots.length ? shots[k + 1][0] : L.E + .3, mid = Math.min(ts + .8, next);
      const v = frame(L, F, o.at !== undefined ? L.T(o.at) : mid);
      if (o.cut) { pushSeg(); }
      if (o.follow) { for (let tt = ts; tt < next - .5; tt += .6) add(tt + (k ? 1.0 : .6), frame(L, F, tt + 1.0)); }
      else { add(ts + (o.cut ? 0 : (k ? 1.0 : .6)), v); if (next - ts > 3) add(next - .15, push(v, o.push ?? .045)); }
    });
  }
  add(CLOSE[0] - .2, CAMV.W); add(CLOSE[1] - .4, [.0, .2, .62, .0, .05, .15, 32, 2.6]); add(TITLE_T + .6, [.06, .26, .72, .0, .05, .15, 32, 2.8]); add(DUR, [.17, .44, .98, .0, .06, .15, 34, 3.2]);
  pushSeg();
}
function camAt(t) { let s = SEGS[0]; for (const S of SEGS) if (t >= S.t0) s = S; const v = s.f(t); return { pos: new THREE.Vector3(v[0], v[1], v[2]), tgt: new THREE.Vector3(v[3], v[4], v[5]), fov: v[6], aper: v[7] }; }

// ---------- lights ----------
const lampHead = new THREE.Vector3(-.28, .375, .44);
const spot = new THREE.SpotLight('#fff0dc', 0, 3, .75, .55, 2); spot.position.copy(lampHead); spot.target.position.set(.02, 0, .2);
spot.castShadow = true; spot.shadow.mapSize.set(SHM, SHM); spot.shadow.bias = -.00006; spot.shadow.normalBias = .0004; spot.shadow.radius = 5; spot.shadow.camera.near = .05; spot.shadow.camera.far = 2;
scene.add(spot, spot.target);
const sun = new THREE.DirectionalLight('#fff3e0', 0); sun.castShadow = true; sun.shadow.mapSize.set(SHM, SHM); sun.shadow.bias = -.00008; sun.shadow.normalBias = .0003; sun.shadow.radius = 4;
Object.assign(sun.shadow.camera, { left: -.3, right: .3, top: .3, bottom: -.3, near: .1, far: 3 }); sun.target.position.set(0, .05, .12); scene.add(sun, sun.target);
const hemi = new THREE.HemisphereLight('#cfe6ff', '#caa27a', 0); scene.add(hemi);

// ---------- particles: sparkles and puffs from every scene's fx ----------
function spriteTex(fn, n = 64) { const c = cv(n, n), x = c.getContext('2d'); fn(x, n); const t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace; return t; }
const starTex = spriteTex((x, n) => { x.translate(n / 2, n / 2); x.fillStyle = '#fff'; x.beginPath(); for (let i = 0; i < 8; i++) { const a = i / 8 * TAU, r = i % 2 ? n * .1 : n * .48; x.lineTo(Math.cos(a) * r, Math.sin(a) * r); } x.closePath(); x.fill(); }, 128);
const puffTex = spriteTex((x, n) => { for (let i = 0; i < 6; i++) { const a = i / 6 * TAU, g = x.createRadialGradient(n / 2 + Math.cos(a) * n * .15, n / 2 + Math.sin(a) * n * .15, 0, n / 2 + Math.cos(a) * n * .15, n / 2 + Math.sin(a) * n * .15, n * .3); g.addColorStop(0, 'rgba(255,255,255,.9)'); g.addColorStop(1, 'rgba(255,255,255,0)'); x.fillStyle = g; x.fillRect(0, 0, n, n); } }, 128);
const quad = new THREE.PlaneGeometry(1, 1), camQ = new THREE.Quaternion(), eul = new THREE.Euler();
const addMat = (map, col) => new THREE.MeshBasicMaterial({ map, color: col, transparent: true, depthWrite: false, blending: THREE.AdditiveBlending, side: THREE.DoubleSide });
const SPARK = [[OPEN[0] + .5, 0, .14, .2, 2.6, 110, 1, 0]], PUFFS = [];
const FX = [];   // resolved fx for the HUD & sound: {type, t, ...}
for (const L of LAY) for (const f of L.sc.fx || []) {
  const t = L.T(f[1]);
  if (f[0] === 'spark') SPARK.push([t, f[2], f[3], f[4] ?? .03, f[5] ?? .9, f[6] ?? 26, f[7] ?? 0, f[8] ?? 0]);
  else if (f[0] === 'puff') PUFFS.push([t, f[2], f[3], f[4] ?? .7, f[5] ?? 0]);
  FX.push({ type: f[0], t, f, L });
}
const SPK_N = 40;   // instances per burst slot; bursts beyond this many particles are thinned
const sparkle = particles(quad, addMat(starTex, new THREE.Color(2.4, 1.9, .9)), 160, (i, t) => {
  // find the live bursts and hand out instances among them
  let live = 0; for (const s of SPARK) if (t > s[0] - .1 && t < s[0] + s[4] + 2) live++;
  if (!live) return null;
  let j = i, s = null; for (const b of SPARK) { if (!(t > b[0] - .1 && t < b[0] + b[4] + 2)) continue; const n = Math.min(b[5], Math.floor(160 / live)); if (j < n) { s = b; break; } j -= n; }
  if (!s) return null;
  const [T0, X, Z, spread, dur, , big, Y] = s, R = mulberry(j * 13 + 5 + Math.round(T0 * 10)), t0 = T0 + R() * dur, life = .9 + R() * .9, k = (t - t0) / life; if (k < 0 || k > 1) return null;
  eul.setFromQuaternion(camQ);
  return { x: X + (R() - .5) * spread * 2 + Math.sin(k * 6 + j) * .006, y: Y + (big ? 0 : .025) + k * (big ? .12 : .03) * (.5 + R()), z: Z + (R() - .5) * spread, s: (big ? .006 : .004) * Math.sin(k * Math.PI) * (.6 + R()), rx: eul.x, ry: eul.y, rz: eul.z + t * 2 + j };
});
book.stage.add(sparkle);
const puffs = particles(quad, new THREE.MeshBasicMaterial({ map: puffTex, transparent: true, depthWrite: false, color: '#fffaf0' }), 7 * 6, (i, t) => {
  const live = PUFFS.filter(p => t >= p[0] && t <= p[0] + .55), P0 = live[(i / 7) | 0]; if (!P0) return null;
  const j = i % 7, k = (t - P0[0]) / .55, a = j / 7 * TAU, r = .012 * P0[3] * eo(k);
  eul.setFromQuaternion(camQ);
  return { x: P0[1] + Math.cos(a) * r, y: P0[4] + .004 * P0[3] + Math.abs(Math.sin(a)) * r * .6, z: P0[2] + Math.sin(a) * r * .3, s: .012 * P0[3] * (.6 + k) * (1 - k * k), rx: eul.x, ry: eul.y, rz: eul.z };
});
book.stage.add(puffs);

// the card that stays up on the closed cover: Valmiki with the twins, singing
const finale = (() => {
  const c = cv(1500, 1000), x = c.getContext('2d'), a = cv(SW, SH);
  const put = (sp, p, dx, s) => { drawStick(a, sp, p); x.drawImage(a, dx, 1000 - SH * s - 20, SW * s, SH * s); };
  put(CAST.valmiki, { sit: 1, eyes: 'closed', mouth: 'sing', armL: .9, armR: 1.1, elbowL: .6, elbowR: .7 }, 380, 1);
  put(CAST.kid1, { eyes: 'happy', mouth: 'sing', armR: 2.2, armL: .3 }, 40, .68);
  put(CAST.kid2, { eyes: 'happy', mouth: 'sing', armL: 2.2, armR: .3 }, 950, .68);
  const g = cutMesh({ c, w: .09, h: .06, ax: .5, ay: 1 }); g.visible = false; book.root.add(g); return g;
})();

// ---------- sound events (for mix.py) ----------
const EV = [];
EV.push({ t: OPEN[0], type: 'creak' }, { t: OPEN[1] - .2, type: 'thump' }, { t: OPEN[0] + .6, type: 'sparkle', d: 2.4 });
for (const r of POPS) if (r.pop) EV.push({ t: r.t0 + .1, type: 'pop' });
for (const r of MOV) if (r.o.pop) EV.push({ t: r.t0 + .05, type: 'pop' });
for (const [a, b] of TURNS) EV.push({ t: a + .45, type: 'page', d: b - a - .7 });
for (const L of LAY) {
  EV.push({ t: L.S, type: 'scene', id: L.sc.id, mood: L.sc.mood || 'calm', page: L.page, t1: L.E + .6, R: L.R });
  for (const v of L.vo) EV.push({ t: v.t0, type: 'vo', id: v.id, d: v.d });
}
for (const e of FX) {
  const f = e.f;
  if (f[0] === 'sfx') EV.push({ t: e.t, type: f[2], ...(f[3] || {}) });
  if (f[0] === 'spark') EV.push({ t: e.t, type: 'sparkle', d: f[5] ?? .9 });
  if (f[0] === 'puff') EV.push({ t: e.t, type: 'thud', v: .5 });
}
EV.push({ t: CLOSE[0] + .4, type: 'creak' }, { t: CLOSE[1] - .15, type: 'thump', v: 1.3 }, { t: CLOSE[1] + .2, type: 'pop' }, { t: CLOSE[1] + .2, type: 'sparkle', d: 1.4 });
SPARK.push([CLOSE[1] + .2, 0, .15, .1, 1.4, 40, 1, 2 * PG - PG]);
{ const prev = {}; for (const L of LAY) for (let f = Math.floor(L.R * 24); f < (L.E + .5) * 24; f++) { const t = f / 24; for (const k in L.sc.cast || {}) { const s = actorAt(L, k, t), ph = s.pose.walk || 0; if (s.vis && s.pose.stride && Math.floor(ph / Math.PI) !== Math.floor((prev[k] || 0) / Math.PI)) EV.push({ t, type: 'step' }); prev[k] = ph; } } }
EV.sort((a, b) => a.t - b.t);
window.EV = EV; window.DUR = DUR; window.LAY = LAY.map(L => ({ id: L.sc.id, S: L.S, R: L.R, E: L.E, page: L.page, mood: L.sc.mood, vo: L.vo.map(v => [v.id, +v.t0.toFixed(3), v.text]) }));
HUD.setup({ LAY, DUR, TITLE_T, META, FX });

// ---------- render ----------
const tmpV = new THREE.Vector3();
function toScreen(v) { const p = v.clone().project(cam); if (p.z > 1) return null; return [(p.x * .5 + .5) * W, (-p.y * .5 + .5) * H]; }
window.render = function (t) {
  const op = eio(seg(t, OPEN[0], OPEN[1])) * (1 - eio(seg(t, CLOSE[0] + .4, CLOSE[1])));
  book.setOpen(Math.PI / 2 * op + Math.sin(seg(t, OPEN[1] - .2, OPEN[1] + .5) * Math.PI) * -.03);
  // pages & turning leaf
  const Lc = sceneAt(t); let turning = null;
  for (const tr of TURNS) if (t >= tr[0] + .45 && t < tr[1] - .3) turning = tr;
  let pg = LAY[0].page; for (const L of LAY) if (t >= (L.turn ? L.turn[0] + .45 : L.S)) pg = L.page;
  const cur = pageTex(pg);
  book.groundMat.map = cur.ground; book.backMat.map = turning ? pageTex(LAY[turning[2] - 1].page).sky : cur.sky; book.groundMat.needsUpdate = book.backMat.needsUpdate = true;
  if (turning) {
    const a = turning[0] + .45, b = turning[1] - .3, lf = book.leafFront.material, lb = book.leafBack.material;
    lf.map = lf.emissiveMap = pageTex(LAY[turning[2] - 1].page).ground; lb.map = lb.emissiveMap = pageTex(LAY[turning[2]].page).sky; lf.needsUpdate = lb.needsUpdate = true;
    book.setLeaf(eio(seg(t, a, b)));
  } else book.setLeaf(0);
  updatePops(t);
  // actors of the live scenes
  const pos = {}, anchors = {};
  updateMovers(t, 1, pos);
  for (const k in ACT) ACT[k].root.visible = ACT[k].shadow.visible = false;
  for (const L of LAY) {
    if (t < L.S - .5 || t > L.E + 1.2) continue;
    for (const k in L.sc.cast || {}) {
      const s = actorAt(L, k, t), a = ACT[k];
      if (!(s.vis && s.s > .01)) continue;
      a.root.visible = true; a.pose(s.pose);
      a.root.position.set(s.x, s.y, s.z); a.root.rotation.set(-Math.PI / 2 * s.lie, 0, 0);
      a.body.scale.set(s.sx * s.s, s.sy * s.s, s.s);
      a.shadow.position.set(s.x, .0004, s.z); a.shadow.scale.setScalar(s.s * clamp(1 - s.y * 12, .3, 1) * (1 - s.lie * .5)); a.shadow.visible = s.y < .03 && s.lie < .5;
      pos[k] = s; anchors[k] = a;
    }
  }
  updateMovers(t, 2, pos);
  // light: blend page light through a turn
  const op2 = seg(t, OPEN[0] + .4, OPEN[1] + 1.2) * (1 - seg(t, CLOSE[0] + .4, CLOSE[1])), real = 1 - op2;
  let sunI = cur.sun, col = cur.col.clone();
  if (turning) { const A0 = pageTex(LAY[turning[2] - 1].page), B0 = pageTex(LAY[turning[2]].page), k = seg(t, turning[0] + .45, turning[1] - .3); sunI = lerp(A0.sun, B0.sun, k); col = A0.col.clone().lerp(B0.col, k); }
  sun.intensity = op2 * sunI; sun.color.copy(col); sun.position.set(-.35, .55, .75);
  spot.intensity = (real * 1.0 + op2 * .25) * 2.2; hemi.intensity = .12 + op2 * .4 * Math.min(1, sunI / 1.5);
  const envI = .38 * real + op2 * .26 * Math.min(1, sunI / 1.4); scene.environmentIntensity = envI; scene.backgroundIntensity = .42 + envI * .3;
  // camera
  const C = camAt(t);
  cam.position.copy(C.pos); cam.fov = C.fov; cam.lookAt(C.tgt); cam.updateProjectionMatrix(); cam.updateMatrixWorld(); camQ.copy(cam.quaternion);
  post.dof.focus = C.pos.distanceTo(C.tgt); post.dof.aper = C.aper; post.dof.maxCoc = QS.get('dof') === '0' ? 0 : 14;
  post.vig.uniforms.fade.value = 1; post.vig.uniforms.warm.value = .12; post.bloom.strength = .22;
  sparkle.userData.update(t); puffs.userData.update(t);
  finale.visible = t > CLOSE[1] + .1; if (finale.visible) { const k = back(seg(t, CLOSE[1] + .1, CLOSE[1] + .7), 1.8); finale.position.set(0, 2 * PG + .0006, .16); finale.rotation.x = -Math.PI / 2 * (1 - k); }
  scene.updateMatrixWorld(true);
  post.composer.render();
  // overlay
  OX.clearRect(0, 0, W, H);
  const hs = k => anchors[k] ? toScreen(anchors[k].head(tmpV)) : null;
  const at = p => Array.isArray(p) ? toScreen(new THREE.Vector3(p[0], p[1] + PG, p[2])) : hs(p);
  HUD.draw(OX, t, at);
  if (t < 1.2 || t > DUR - 1.4) { OX.fillStyle = `rgba(0,0,0,${1 - seg(t, 0, 1.2) * (1 - seg(t, DUR - 1.4, DUR))})`; OX.fillRect(0, 0, W, H); }
};
// grab the composited frame in-page (much faster than a browser screenshot under software GL)
const GRAB = document.createElement('canvas'); GRAB.width = W; GRAB.height = H; const GX = GRAB.getContext('2d');
window.grab = function (t, q = .93) { window.render(t); GX.imageSmoothingQuality = 'high'; GX.drawImage(renderer.domElement, 0, 0, W, H); GX.drawImage(document.getElementById('ov'), 0, 0); return GRAB.toDataURL('image/jpeg', q).slice(23); };
window.DBG = { book, cam, ACT, LAY, MOV, POPS };
window.render(0);
window.READY = true;
