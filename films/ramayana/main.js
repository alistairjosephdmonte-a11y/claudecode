// The Ramayana, a pop-up book: scene, choreography, camera, sound events, render(t)
import * as THREE from 'three';
import { RGBELoader } from 'three/addons/loaders/RGBELoader.js';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { clamp, lerp, seg, ss, eio, eo, back, TAU, mulberry, track, spring } from './lib.js';
import { cv, finishCut, sh, INK } from './paper.js';
import { makeBook, coverCanvases, texOf, BW, BD, PG } from './book.js';
import { pages, buildSets, buildSlats, updatePops, RISE, FOLD } from './sets.js';
import { makeStick, drawStick, CAST, SW, SH } from './actors.js';
import { cutMesh, particles, blobShadow } from './cutmesh.js';
import { makePost } from './post.js';
import { DUR, OPEN, TURNS, CLOSE, VO, ACTIONS } from './story.js';
import * as HUD from './hud.js';


const W = 1920, H = 1080;
const renderer = new THREE.WebGLRenderer({ antialias: false, preserveDrawingBuffer: true, powerPreference: 'high-performance' });
renderer.setSize(W, H); renderer.setPixelRatio(1);
const QS = new URLSearchParams(location.search), SHM = parseInt(QS.get('shm') || '2048');
renderer.shadowMap.enabled = true; renderer.shadowMap.type = QS.get('pcf') === '1' ? THREE.PCFShadowMap : THREE.PCFSoftShadowMap;
renderer.toneMapping = THREE.NeutralToneMapping; renderer.outputColorSpace = THREE.SRGBColorSpace;
document.getElementById('stage').appendChild(renderer.domElement);
const ov = document.getElementById('ov'), OX = ov.getContext('2d');
const scene = new THREE.Scene();
const cam = new THREE.PerspectiveCamera(30, W / H, .004, 30);
const RS = parseFloat(new URLSearchParams(location.search).get('rs') || '.75');
if (RS !== 1) renderer.setSize(W * RS, H * RS, false);
const post = makePost(renderer, scene, cam, W * RS, H * RS);

// ---------- assets ----------
await Promise.all(['500 40px Fredoka', '600 40px Fredoka', '40px "Lilita One"', '40px "IM Fell English"', 'italic 40px "IM Fell English"', '50px "Tiro Devanagari Sanskrit"'].map(f => document.fonts.load(f, 'Aaराम')));
const DURS = await (await fetch('voices/dur.json')).json();
const hdr = await new RGBELoader().loadAsync('assets/lythwood_lounge_2k.hdr'); hdr.mapping = THREE.EquirectangularReflectionMapping;
scene.environment = hdr; scene.background = hdr; scene.backgroundBlurriness = .22;
if (QS.get('bg') === '0') scene.background = new THREE.Color('#5a4a3a');
if (QS.get('sh') === '0') renderer.shadowMap.enabled = false;
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
// a marigold garland and a brass diya on the desk: small real-world nods to the topic, procedural
{
  const g = new THREE.Group(), R = mulberry(4);
  for (let i = 0; i < 46; i++) { const a = i / 46 * Math.PI * 1.25 - .3, r = .17; const m = new THREE.Mesh(new THREE.SphereGeometry(.0085, 10, 8), new THREE.MeshStandardMaterial({ color: R() < .5 ? '#f29a1a' : '#f6b81e', roughness: .9 })); m.position.set(Math.cos(a) * r * 1.4, .007, Math.sin(a) * r * .5); m.scale.y = .8; m.castShadow = m.receiveShadow = true; g.add(m); }
  g.position.set(.42, 0, .62); g.rotation.y = .4; scene.add(g);
  const brass = new THREE.MeshStandardMaterial({ color: '#c9933a', metalness: 1, roughness: .32 });
  const diya = new THREE.Mesh(new THREE.SphereGeometry(.03, 24, 12, 0, TAU, Math.PI / 2, Math.PI / 2), brass); diya.scale.y = .55; diya.rotation.x = Math.PI; diya.position.set(-.42, .016, .2); diya.castShadow = true; scene.add(diya);
  const flame = new THREE.Mesh(new THREE.SphereGeometry(.006, 12, 8), new THREE.MeshBasicMaterial({ color: new THREE.Color(4, 2.2, .6) })); flame.scale.set(1, 2, 1); flame.position.set(-.42, .03, .2); scene.add(flame);
}


// ---------- the book ----------
const cover = coverCanvases((x, px, py, w, h) => {   // medallion: Shiva's bow and an arrow, over a lotus
  x.save(); x.translate(px + w / 2, py + h / 2);
  x.fillStyle = '#f4e9cf'; x.beginPath(); x.arc(0, 0, w * .55, 0, TAU); x.fill();
  for (let i = 0; i < 8; i++) { x.save(); x.rotate(i / 8 * TAU); x.beginPath(); x.ellipse(0, -w * .22, w * .08, w * .2, 0, 0, TAU); x.fillStyle = i % 2 ? '#f29ab0' : '#e8708a'; x.fill(); x.lineWidth = 6; x.strokeStyle = INK; x.stroke(); x.restore(); }
  x.beginPath(); x.moveTo(-w * .4, -w * .3); x.quadraticCurveTo(0, w * .35, w * .4, -w * .3); x.lineWidth = 26; x.strokeStyle = INK; x.stroke(); x.lineWidth = 14; x.strokeStyle = '#5b8de0'; x.stroke();
  x.beginPath(); x.moveTo(-w * .4, -w * .3); x.lineTo(w * .4, -w * .3); x.lineWidth = 4; x.strokeStyle = INK; x.stroke();
  x.beginPath(); x.moveTo(0, w * .3); x.lineTo(0, -w * .48); x.lineWidth = 8; x.stroke(); x.beginPath(); x.moveTo(0, -w * .55); x.lineTo(-w * .05, -w * .44); x.lineTo(w * .05, -w * .44); x.closePath(); x.fillStyle = '#f2b632'; x.fill(); x.stroke();
  x.restore();
}, { title: ['The', 'Ramayana', ''], tag: '~ as Valmiki told it ~', cloth: '#7a2321' });
const book = makeBook(cover); scene.add(book.root);
const PP = pages(), PT = {}; for (const k in PP) PT[k] = texOf(PP[k]);
const PAGE = [{ sky: PT.sky0, ground: PT.ground0 }, { sky: PT.sky1, ground: PT.ground1 }, { sky: PT.sky2, ground: PT.ground2 }, { sky: PT.sky3, ground: PT.ground3 }, { sky: PT.sky4, ground: PT.ground4 }];
const { L: POPS, ex: EX } = buildSets(book);
const SL1 = buildSlats(book, PT.sky1, PT.sky1dusk), SL4 = buildSlats(book, PT.sky4, PT.sky5);


// ---------- actors ----------
const A = {}, mk = (k, sp, h) => { A[k] = makeStick(sp, h); book.stage.add(A[k].root); book.stage.add(A[k].shadow); };
mk('valmikiG', CAST.valmikiG, .042); mk('hunterG', CAST.hunterG, .04);
mk('rama', CAST.rama, .045); mk('sita', CAST.sita, .042); mk('lakshmana', CAST.lakshmana, .043); mk('kaikeyi', CAST.kaikeyi, .042); mk('bharata', CAST.bharata, .043);
mk('ravana', CAST.ravana, .048); mk('hanuman', CAST.hanuman, .045); mk('sugriva', CAST.sugriva, .043);
mk('valmiki', CAST.valmiki, .042); mk('kid1', CAST.kid1, .03); mk('kid2', CAST.kid2, .03);

// the card that stays up: Valmiki with the twins, singing
const finale = (() => {
  const c = cv(1500, 1000), x = c.getContext('2d'), a = cv(SW, SH);
  const put = (sp, p, dx, s) => { drawStick(a, sp, p); x.drawImage(a, dx, 1000 - SH * s - 20, SW * s, SH * s); };
  put(CAST.valmiki, { sit: 1, eyes: 'closed', mouth: 'sing', armL: .9, armR: 1.1, elbowL: .6, elbowR: .7 }, 380, 1);
  put(CAST.kid1, { eyes: 'happy', mouth: 'sing', armR: 2.2, armL: .3 }, 40, .68);
  put(CAST.kid2, { eyes: 'happy', mouth: 'sing', armL: 2.2, armR: .3 }, 950, .68);
  const g = cutMesh({ c, w: .09, h: .06, ax: .5, ay: 1 }); g.visible = false; book.root.add(g); return g;
})();


// ---------- lights ----------
const lampHead = new THREE.Vector3(-.28, .375, .44);
const spot = new THREE.SpotLight('#fff0dc', 0, 3, .75, .55, 2); spot.position.copy(lampHead); spot.target.position.set(.02, 0, .2);
spot.castShadow = true; spot.shadow.mapSize.set(SHM, SHM); spot.shadow.bias = -.00006; spot.shadow.normalBias = .0004; spot.shadow.radius = 5; spot.shadow.camera.near = .05; spot.shadow.camera.far = 2;
scene.add(spot, spot.target);
const sun = new THREE.DirectionalLight('#fff3e0', 0); sun.castShadow = true; sun.shadow.mapSize.set(SHM, SHM); sun.shadow.bias = -.00008; sun.shadow.normalBias = .0003; sun.shadow.radius = 4;
Object.assign(sun.shadow.camera, { left: -.3, right: .3, top: .3, bottom: -.3, near: .1, far: 3 }); sun.target.position.set(0, .05, .12); scene.add(sun, sun.target);
const hemi = new THREE.HemisphereLight('#cfe6ff', '#caa27a', 0); scene.add(hemi);

// ---------- particles ----------
function spriteTex(fn, n = 64) { const c = cv(n, n), x = c.getContext('2d'); fn(x, n); const t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace; return t; }
const starTex = spriteTex((x, n) => { x.translate(n / 2, n / 2); x.fillStyle = '#fff'; x.beginPath(); for (let i = 0; i < 8; i++) { const a = i / 8 * TAU, r = i % 2 ? n * .1 : n * .48; x.lineTo(Math.cos(a) * r, Math.sin(a) * r); } x.closePath(); x.fill(); }, 128);
const puffTex = spriteTex((x, n) => { for (let i = 0; i < 6; i++) { const a = i / 6 * TAU, g = x.createRadialGradient(n / 2 + Math.cos(a) * n * .15, n / 2 + Math.sin(a) * n * .15, 0, n / 2 + Math.cos(a) * n * .15, n / 2 + Math.sin(a) * n * .15, n * .3); g.addColorStop(0, 'rgba(255,255,255,.9)'); g.addColorStop(1, 'rgba(255,255,255,0)'); x.fillStyle = g; x.fillRect(0, 0, n, n); } }, 128);
const quad = new THREE.PlaneGeometry(1, 1), camQ = new THREE.Quaternion();
const addMat = (map, col) => new THREE.MeshBasicMaterial({ map, color: col, transparent: true, depthWrite: false, blending: THREE.AdditiveBlending, side: THREE.DoubleSide });
function billboard(fn) { return (i, t) => { const p = fn(i, t); if (p) { const e = new THREE.Euler().setFromQuaternion(camQ); p.rx = e.x; p.ry = e.y; p.rz = e.z + (p.spin || 0); } return p; }; }
const PS = [];
const SPARK = [[OPEN[0] + .5, 0, .14, .2, 2.6, 110], [85.0, .152, .155, .03, .9, 30], [97.6, -.15, .17, .02, .8, 24], [113.8, 0, .15, .1, 1.4, 40]];
let sparkN = 0; const sparkOff = SPARK.map(s => { const o = sparkN; sparkN += s[5]; return o; });
const sparkle = particles(quad, addMat(starTex, new THREE.Color(2.4, 1.9, .9)), sparkN, billboard((i, t) => {
  let k0 = 0; while (k0 < SPARK.length - 1 && i >= sparkOff[k0 + 1]) k0++;
  const [T0, X, Z, spread, dur] = SPARK[k0], R = mulberry(i * 13 + 5), t0 = T0 + R() * dur, life = .9 + R() * .9, k = (t - t0) / life; if (k < 0 || k > 1) return null;
  const big = k0 === 0 || k0 === 3;
  return { x: X + (R() - .5) * spread * 2 + Math.sin(k * 6 + i) * .006, y: (big ? 0 : .025) + k * (big ? .12 : .03) * (.5 + R()) + (k0 === 3 ? 2 * PG - PG : 0), z: Z + (R() - .5) * spread, s: (big ? .006 : .004) * Math.sin(k * Math.PI) * (.6 + R()), spin: t * 2 + i };
}));
book.stage.add(sparkle); PS.push(sparkle);
const PUFFS = [[11.85, .085, .15, .5], [82.2, .125, .16, .7], [95.5, .135, .16, 1.0]];
const puffs = particles(quad, new THREE.MeshBasicMaterial({ map: puffTex, transparent: true, depthWrite: false, color: '#fffaf0' }), PUFFS.length * 7, billboard((i, t) => {
  const P0 = PUFFS[(i / 7) | 0], j = i % 7, k = (t - P0[0]) / .55; if (k < 0 || k > 1) return null;
  const a = j / 7 * TAU, r = .012 * P0[3] * eo(k);
  return { x: P0[1] + Math.cos(a) * r, y: .004 * P0[3] + Math.abs(Math.sin(a)) * r * .6, z: P0[2] + Math.sin(a) * r * .3, s: .012 * P0[3] * (.6 + k) * (1 - k * k) };
}));
book.stage.add(puffs); PS.push(puffs);

// ---------- choreography helpers ----------
const blinkAt = (t, o = 0) => { const p = (t + o) % 3.9; return p < .12 ? Math.sin(p / .12 * Math.PI) : 0; };
function walk(t, t0, t1, a, b) { const k = seg(t, t0, t1); const x = lerp(a[0], b[0], k), z = lerp(a[1], b[1], k), dist = Math.hypot(b[0] - a[0], b[1] - a[1]) * k; return { x, z, ph: dist / .014 * TAU, moving: t > t0 && t < t1, dir: Math.sign(b[0] - a[0]) * .7 }; }
function arc(t, t0, t1, a, b, h) { const k = seg(t, t0, t1); return { x: lerp(a[0], b[0], k), y: 4 * h * k * (1 - k), z: lerp(a[1], b[1], k) }; }
const popIn = (t, t0) => back(seg(t, t0, t0 + .4), 2);
const lieDown = (t, t0, d = .45) => ss(seg(t, t0, t0 + d));
// an actor state: {vis, x,y,z, s (scale), lie (0 up → 1 flat on its back), sx,sy (squash), pose}
const S0 = () => ({ vis: false, x: 0, y: 0, z: .16, s: 1, lie: 0, sx: 1, sy: 1, ry: 0, pose: {} });
function spreadLife(S, t, spread, t0, z = S.z) {   // pop with its spread, fold with it
  const tf = FOLD[spread] + (.3 - z) * .6; S.vis = t > t0 && t < tf + .45; S.s = popIn(t, t0); S.lie = Math.max(S.lie, lieDown(t, tf, .4)); return S;
}
const walkPose = (P, w) => { if (w.moving) { P.walk = w.ph; P.stride = 1; P.armL = .25 + Math.sin(w.ph) * .45; P.armR = .25 - Math.sin(w.ph) * .45; P.dir = w.dir; } };
const singing = t => Math.sin(t * 9) > 0 ? 'sing' : 'open';
const talk = (t, t0, t1) => t > t0 && t < t1 ? (Math.sin(t * 13) > -.2 ? 'open' : 'smile') : null;

const AT = {};   // per-actor state functions
AT.valmikiG = t => { const S = S0(); S.x = -.08; S.z = .19; spreadLife(S, t, 0, 7.0); const P = S.pose;
  P.dir = .35; P.look = [.6, 0]; P.blink = blinkAt(t);
  if (t > 11.8) { P.eyes = 'wide'; P.mouth = 'o'; }
  if (t > 13.4) { P.eyes = 'open'; P.mouth = 'sad'; P.look = [.6, .5]; }
  if (t > 15.2) { P.eyes = t > 16.5 ? 'closed' : 'open'; P.mouth = singing(t); const u = ss(seg(t, 15.4, 16.6)); P.armL = lerp(.2, 1.3, u); P.armR = lerp(.2, 1.3, u); P.elbowL = P.elbowR = lerp(.15, .7, u); P.dir = 0; P.look = [0, -.3]; }
  if (t > 23.2) P.mouth = 'smile';
  return S; };
AT.hunterG = t => { const S = S0(); S.x = .175; S.z = .155; spreadLife(S, t, 0, 7.3); const P = S.pose; P.dir = -.6; P.look = [-.7, .1]; P.brows = 'angry'; P.mouth = 'line';
  const aim = ss(seg(t, 9.6, 10.4)) * (1 - ss(seg(t, 12.0, 12.6))); P.armR = lerp(.2, 1.5, aim); P.elbowR = lerp(.15, 0, aim); P.armL = lerp(.2, 1.3, aim); P.elbowL = lerp(.15, 1.0, aim);
  const w = walk(t, 13.0, 15.2, [.175, .155], [.27, .16]); if (t > 13) { S.x = w.x; S.z = w.z; walkPose(P, w); }
  if (S.x > .225) S.vis = false; return S; };
AT.rama = t => { const S = S0(); const P = S.pose; P.blink = blinkAt(t, 1.1); P.holdL = 'bow';
  if (t < 34.0) { // Mithila: the bow
    S.x = .05; S.z = .16; spreadLife(S, t, 1, 27.0);
    const w = walk(t, 28.0, 29.4, [.05, .16], [.088, .165]); if (t > 28) { S.x = w.x; S.z = w.z; walkPose(P, w); }
    P.holdL = null; P.dir = .4; P.look = [.5, -.2];
    const up = ss(seg(t, 29.6, 30.4)) * (1 - ss(seg(t, 31.6, 32.2))); P.armL = P.armR = lerp(.2, 2.6, up); P.elbowL = P.elbowR = lerp(.15, .5, up); P.mouth = up > .5 ? 'grin' : 'smile';
    if (t > 31.3) { P.eyes = 'happy'; P.dir = .6; }
    return S;
  }
  if (t < 54.6) { // the palace, then the walk into exile
    S.vis = true; S.x = -.05; S.z = .165; P.dir = -.4; P.look = [-.6, 0]; P.mouth = 'line';
    if (t > 41.8) P.mouth = 'smile';
    const w = walk(t, 45.2, 50.2, [-.05, .165], [.27, .18]); if (t > 45.2) { S.x = w.x; S.z = w.z; walkPose(P, w); P.look = [.6, 0]; }
    if (S.x > .23) S.vis = false; return S;
  }
  if (t < 68.6) { // forest
    S.x = -.02; S.z = .165; spreadLife(S, t, 2, 57.2); P.dir = .2;
    if (t > 60.3) { P.look = [.8, 0]; P.dir = .6; P.eyes = 'wide'; }
    const w = walk(t, 61.6, 63.4, [-.02, .165], [.27, .17]); if (t > 61.6) { S.x = w.x; S.z = w.z; walkPose(P, w); P.eyes = 'open'; }
    if (S.x > .23) S.vis = false; return S;
  }
  if (t < 87.6) { S.x = -.19; S.z = .172; spreadLife(S, t, 3, 71.6); P.dir = .5; P.look = [.6, 0]; if (t > 85.2) P.eyes = 'happy'; return S; }
  if (t < 99.6) { // war
    S.x = -.15; S.z = .175; spreadLife(S, t, 4, 90.0); P.dir = .6; P.look = [.8, -.1];
    const aim = ss(seg(t, 94.0, 94.6)) * (1 - ss(seg(t, 95.6, 96.2))); P.armL = lerp(.2, 1.55, aim); P.elbowL = 0; P.armR = lerp(.2, 1.3, aim); P.elbowR = lerp(.15, 1.1, aim); P.brows = aim > .2 ? 'angry' : null;
    if (t > 97.6) { P.eyes = 'happy'; P.mouth = 'grin'; P.armL = P.armR = 2.3; }
    return S;
  }
  S.x = .16; S.z = .165; spreadLife(S, t, 5, 106.4); P.holdL = null; P.dir = -.6; P.look = [-.7, .2]; P.mouth = 'smile'; if (t > 108.0) P.eyes = 'happy'; return S;
};
AT.sita = t => { const S = S0(); const P = S.pose; P.blink = blinkAt(t, 2.2);
  if (t < 34.0) { S.x = .17; S.z = .16; spreadLife(S, t, 1, 27.3); P.dir = -.5; P.look = [-.6, -.1];
    const w = walk(t, 32.0, 33.2, [.17, .16], [.128, .162]); if (t > 32) { S.x = w.x; S.z = w.z; walkPose(P, w); } if (t > 31.3) { P.eyes = 'happy'; P.mouth = 'grin'; } return S; }
  if (t < 54.6) { S.vis = true; S.x = .0; S.z = .172; P.dir = -.4; P.look = [-.6, 0]; P.mouth = t > 40 ? 'sad' : 'smile';
    const w = walk(t, 45.4, 50.6, [0, .172], [.27, .19]); if (t > 45.4) { S.x = w.x; S.z = w.z; walkPose(P, w); } if (S.x > .23) S.vis = false; return S; }
  if (t < 68.8) { S.x = -.08; S.z = .172; spreadLife(S, t, 2, 57.3); P.dir = .4; P.look = [.6, 0];
    if (t > 60.2) { P.eyes = 'wide'; P.mouth = 'o'; P.armR = 1.2; }
    if (t > 61.5) { P.eyes = 'open'; P.mouth = 'smile'; P.armR = .2; }
    if (t > 64.6) { P.eyes = 'wide'; P.mouth = 'open'; P.armL = P.armR = 2.4; P.look = [0, -.6]; }
    if (t > 65.2) { const c = chariotAt(t), k = ss(seg(t, 65.2, 65.7)); S.x = lerp(-.08, c.x - .012, k); S.y = lerp(0, c.y + .004, k); S.z = lerp(.172, c.z - .003, k); }
    return S; }
  if (t < 87.6) { S.x = .165; S.z = .152; spreadLife(S, t, 3, 71.8); P.sit = 1; P.dir = -.3; P.mouth = 'sad'; P.look = [0, .4]; P.eyes = 'open';
    if (t > 84.8) { P.look = [-.6, -.2]; P.eyes = 'wide'; P.mouth = 'o'; } if (t > 85.5) { P.eyes = 'happy'; P.mouth = 'grin'; } return S; }
  if (t < 99.6) return S;
  S.x = -.145; S.z = .172; spreadLife(S, t, 5, 100.6); P.dir = .4; P.look = [.6, 0]; P.mouth = 'smile'; if (t > 104.5) P.eyes = 'happy'; return S;
};
AT.lakshmana = t => { const S = S0(); const P = S.pose; P.blink = blinkAt(t, .7);
  if (t < 34 || t > 54.6) return S;
  S.x = .048; S.z = .176; S.vis = t > 36.0; S.s = popIn(t, 36.0); P.dir = -.5; P.look = [-.6, 0]; P.brows = t > 38 && t < 44 ? 'angry' : null; P.mouth = 'line';
  const w = walk(t, 45.0, 50.0, [.048, .176], [.27, .19]); if (t > 45) { S.x = w.x; S.z = w.z; walkPose(P, w); } if (S.x > .23) S.vis = false; return S; };
AT.kaikeyi = t => { const S = S0(); if (t < 34 || t > 54.6) return S; const P = S.pose; P.blink = blinkAt(t, 1.7);
  S.x = -.172; S.z = .162; S.vis = true; S.s = popIn(t, 34.3); S.lie = lieDown(t, 54.4 + .08); P.dir = .5; P.look = [.6, 0];
  const p1 = ss(seg(t, 36.4, 36.9)) * (1 - ss(seg(t, 38.2, 38.6))), p2 = ss(seg(t, 39.0, 39.5)) * (1 - ss(seg(t, 43.2, 43.7)));
  P.armR = lerp(.2, 1.6, Math.max(p1, p2)); P.elbowR = 0; P.mouth = talk(t, 36.4, 43.6) || 'line'; if (p2 > .5) { P.armL = 1.4; P.elbowL = .2; } return S; };
AT.bharata = t => { const S = S0(); if (t < 34 || t > 54.6) return S; const P = S.pose; P.blink = blinkAt(t, 2.9);
  S.x = -.142; S.z = .13; S.vis = t > 39.3; S.s = popIn(t, 39.3); S.lie = lieDown(t, 54.4 + .1); P.dir = .2; P.look = [.4, 0]; P.mouth = t > 40 ? 'sad' : 'o';
  if (t > 46.5 && t < 49.7) { P.holdR = 'sandals'; P.armR = 1.1; P.elbowR = .9; }
  if (t > 50.6) { S.ry = 0; P.lean = -.12 * ss(seg(t, 50.6, 51.2)); P.eyes = 'closed'; } return S; };
AT.ravana = t => { const S = S0(); const P = S.pose; P.blink = blinkAt(t, 3.3); P.brows = 'angry'; P.mouth = 'grin';
  if (t < 63.4 || t > 99.6) return S;
  if (t < 68.6) { const c = chariotAt(t); S.vis = t > 63.4; S.x = c.x + .006; S.y = c.y - .004; S.z = c.z - .004; P.armR = 1.6; P.dir = -.3; return S; }
  if (t < 90) return S;
  S.x = .135; S.z = .16; spreadLife(S, t, 4, 90.0); P.dir = -.6; P.look = [-.7, 0];
  if (t > 95.35) { P.eyes = 'closed'; P.mouth = 'o'; S.lie = Math.max(S.lie, lieDown(t, 95.4, .5)); } return S; };
AT.hanuman = t => { const S = S0(); if (t < 70 || t > 87.6) return S; const P = S.pose; P.blink = blinkAt(t, .4);
  S.x = -.05; S.z = .165; spreadLife(S, t, 3, 77.4); P.dir = .3; P.mouth = 'smile';
  // crouch, leap the sea, land, walk to Sita, offer the ring
  const cr = seg(t, 80.0, 80.4); if (cr > 0 && cr < 1) { S.sy = 1 - .25 * Math.sin(cr * Math.PI); S.sx = 1 + .15 * Math.sin(cr * Math.PI); }
  if (t > 80.4) { const a = arc(t, 80.4, 82.2, [-.05, .165], [.125, .16], .11); S.x = a.x; S.y = a.y; S.z = a.z; P.armL = P.armR = 2.5; P.walk = 1; P.stride = .6; P.eyes = 'happy'; P.mouth = 'grin'; P.dir = .6; }
  const ld = seg(t, 82.2, 82.45); if (ld > 0 && ld < 1) { S.sy = 1 - .3 * Math.sin(ld * Math.PI); S.sx = 1 + .2 * Math.sin(ld * Math.PI); }
  if (t > 82.4) { P.armL = P.armR = .25; P.walk = 0; P.stride = 0; P.eyes = 'open'; P.mouth = 'smile'; }
  const w = walk(t, 83.4, 84.4, [.125, .16], [.138, .158]); if (t > 83.4) { S.x = w.x; S.z = w.z; walkPose(P, w); }
  if (t > 84.5) { P.dir = .4; P.look = [.5, .3]; P.holdL = 'ring'; P.armR = .2; const u = ss(seg(t, 84.5, 85.0)); P.armL = lerp(.3, 1.25, u); P.elbowL = 0; P.holdR = null; }
  return S; };
AT.sugriva = t => { const S = S0(); if (t < 70 || t > 87.6) return S; const P = S.pose; P.blink = blinkAt(t, 1.9); S.x = -.12; S.z = .16; spreadLife(S, t, 3, 75.6); P.dir = -.3; P.look = [-.5, 0]; P.mouth = 'grin'; P.eyes = t < 77 ? 'happy' : 'open'; if (t > 75.8 && t < 77) { P.armL = P.armR = 2.4; } return S; };
AT.valmiki = t => { const S = S0(); if (t < 99.6) return S; const P = S.pose; P.blink = blinkAt(t, .9); S.x = -.03; S.z = .148; spreadLife(S, t, 5, 100.2); P.sit = 1; P.eyes = 'closed'; P.mouth = t > 104.4 ? singing(t + .2) : 'smile'; P.armL = .8; P.armR = .9 + .3 * Math.sin(t * 2); P.elbowL = .6; P.elbowR = .7; return S; };
const kid = (o, x) => t => { const S = S0(); if (t < 99.6) return S; const P = S.pose; P.blink = blinkAt(t, o); S.x = x; S.z = .17; spreadLife(S, t, 5, 103.0 + o * .3); P.eyes = 'happy'; P.mouth = t > 104.4 ? singing(t + o) : 'smile'; P.dir = -.2; if (t > 104.4) { P.armR = 1.6 + .6 * Math.sin(t * 4 + o * 3); P.armL = .3; }
  const hop = (t * 2 + o) % 1; if (t > 104.4) S.y = .002 * Math.max(0, Math.sin(hop * Math.PI)); return S; };
AT.kid1 = kid(0, .035); AT.kid2 = kid(1, .075);

// props on paths
function chariotAt(t) {
  const down = spring(t - 63.6, 4, .5), up = eio(seg(t, 65.6, 67.8));
  return { x: lerp(-.055, .21, up), y: lerp(.26, .012, Math.min(1, down)) + up * .2, z: lerp(.162, .12, up), vis: t > 63.6 && t < 68.6 };
}
function arrowAt(t) {
  if (t > 11.3 && t < 11.86) { const k = seg(t, 11.3, 11.85); return { vis: true, x: lerp(.16, .095, k), y: .028 - .006 * k, z: .152, s: 1 }; }
  if (t > 94.8 && t < 95.42) { const k = seg(t, 94.8, 95.4); return { vis: true, x: lerp(-.13, .118, k), y: .032 + .01 * Math.sin(k * Math.PI), z: .17, s: 1.3 }; }
  return { vis: false };
}

// ---------- camera ----------
// [t, px,py,pz, tx,ty,tz, fov, aperture]; each inner list is one shot (a new list = a hard cut)
const TURN = (a, b) => [[a, .0, .15, .62, .0, .08, .1, 30, 1.9], [b, .0, .15, .62, .0, .08, .1, 30, 1.9]];
const SHK = [
  [[0, .52, .34, 1.08, -.02, .1, .2, 34, 3.0], [3.0, .26, .3, .86, .0, .06, .16, 32, 3.0], [5.6, .02, .2, .68, .0, .09, .12, 30, 2.6], [7.2, -.02, .1, .52, -.02, .05, .12, 30, 2.2],
   [9.4, .07, .065, .42, .1, .035, .14, 30, 2.3], [12.6, .075, .062, .41, .09, .032, .14, 30, 2.3], [14.6, -.04, .07, .44, -.06, .045, .17, 30, 2.3], [18.8, -.065, .058, .38, -.08, .045, .19, 30, 2.5], [22.6, -.05, .07, .44, -.06, .05, .16, 30, 2.3],
   ...TURN(24.2, 26.4), [27.6, .09, .07, .43, .11, .04, .13, 30, 2.2], [30.4, .1, .062, .39, .11, .04, .13, 30, 2.3], [33.9, .12, .066, .41, .13, .04, .14, 30, 2.3]],
  [[34.0, -.08, .085, .5, -.08, .05, .12, 30, 2.1], [39.0, -.08, .095, .52, -.07, .065, .1, 30, 2.0], [41.4, -.11, .062, .41, -.13, .045, .14, 30, 2.3], [44.6, -.04, .07, .45, -.03, .04, .14, 30, 2.2],
   [47.6, .07, .07, .45, .1, .04, .16, 30, 2.2], [49.4, -.09, .06, .39, -.12, .035, .12, 30, 2.4], [53.8, -.085, .065, .41, -.11, .035, .12, 30, 2.4], ...TURN(54.6, 57.0),
   [58.4, -.04, .07, .45, -.05, .04, .14, 30, 2.2], [60.6, .06, .07, .45, .08, .04, .13, 30, 2.2], [62.6, .02, .085, .5, .02, .05, .12, 30, 2.1], [64.4, -.05, .085, .46, -.06, .06, .14, 30, 2.2], [67.6, .03, .13, .58, .03, .1, .1, 30, 2.0], ...TURN(68.8, 71.2),
   [72.4, -.13, .07, .43, -.14, .04, .14, 30, 2.2], [77.6, -.09, .07, .44, -.1, .04, .14, 30, 2.2], [79.8, -.01, .095, .54, .02, .06, .13, 30, 2.0], [82.4, .08, .08, .48, .1, .05, .13, 30, 2.1], [84.2, .14, .058, .38, .15, .035, .15, 30, 2.4], [86.8, .14, .062, .4, .15, .035, .15, 30, 2.4], ...TURN(87.4, 89.8),
   [91.0, .0, .12, .6, .0, .05, .11, 30, 2.0], [93.6, -.02, .09, .55, .0, .04, .14, 30, 2.0], [95.0, .0, .09, .58, .0, .04, .15, 30, 2.0], [96.1, .0, .09, .58, .0, .04, .15, 30, 2.0], [97.2, -.13, .066, .41, -.15, .045, .17, 30, 2.4], [98.6, .0, .13, .6, .0, .07, .1, 30, 1.9],
   [101.2, -.04, .08, .46, -.04, .04, .14, 30, 2.1], [104.2, .03, .064, .4, .05, .035, .16, 30, 2.3], [107.0, .1, .07, .44, .12, .04, .14, 30, 2.2], [110.0, .0, .13, .62, .0, .06, .12, 30, 2.0],
   [113.2, .0, .2, .62, .0, .05, .15, 32, 2.6], [116.0, .06, .26, .72, .0, .05, .15, 32, 2.8], [123.5, .17, .44, .98, .0, .06, .15, 34, 3.2]],
];
const SHOTS = SHK.map(keys => ({ t0: keys[0][0], f: track(keys.map(k => [k[0], k.slice(1, 9)])) }));
function camAt(t) { let s = SHOTS[0]; for (const S of SHOTS) if (t >= S.t0) s = S; const v = s.f(t); return { pos: new THREE.Vector3(v[0], v[1], v[2]), tgt: new THREE.Vector3(v[3], v[4], v[5]), fov: v[6], aper: v[7] }; }

// ---------- lights over time ----------
function lightsAt(t) {
  const open = seg(t, OPEN[0] + .4, OPEN[1] + 1.2) * (1 - seg(t, CLOSE[0] + .4, CLOSE[1])), real = 1 - open;
  const dusk = seg(t, 39.6, 41.0) * (1 - seg(t, TURNS[0 + 1][0], TURNS[1][0] + .5));
  const pencil = 1 - seg(t, TURNS[0][0], TURNS[0][1]);
  return { sunI: open * (1.7 - dusk * .8 - pencil * .5), sunCol: new THREE.Color('#fff3e0').lerp(new THREE.Color('#ffb07a'), dusk), lampI: real * 1.0 + open * .25, hemiI: .12 + open * (.4 - dusk * .15), envI: .38 * real + open * .26 };
}

// ---------- sound events (for mix.py) ----------
const EV = [];
EV.push({ t: OPEN[0], type: 'creak' }, { t: OPEN[1] - .2, type: 'thump' }, { t: OPEN[0] + .6, type: 'sparkle', d: 2.4 });
for (const r of POPS) EV.push({ t: (r.t0 ?? RISE[r.spread] + r.d) + .1, type: 'pop', s: r.spread });
for (const [a, b] of TURNS) EV.push({ t: a + .45, type: 'page', d: b - a - .7 });
for (let i = 0; i < 4; i++) EV.push({ t: 39.6 + i * .25 + .3, type: 'clack' }, { t: 98.9 + i * .25 + .3, type: 'clack' });
EV.push({ t: 11.3, type: 'arrow' }, { t: 11.85, type: 'thud', v: .5 }, { t: 12.0, type: 'cry' }, { t: 31.2, type: 'snap' }, { t: 49.6, type: 'slide', d: .8 },
  { t: 63.6, type: 'whoosh' }, { t: 64.3, type: 'tink' }, { t: 64.6, type: 'bang' }, { t: 65.6, type: 'whoosh' }, { t: 80.4, type: 'boing' }, { t: 82.2, type: 'land' },
  { t: 85.0, type: 'sparkle', d: 1.0 }, { t: 94.8, type: 'arrow' }, { t: 95.45, type: 'thud', v: 1 }, { t: 96.8, type: 'tink' }, { t: 97.6, type: 'ding' }, { t: 97.6, type: 'sparkle', d: .8 },
  { t: CLOSE[0] + .4, type: 'creak' }, { t: CLOSE[1] - .15, type: 'thump', v: 1.3 }, { t: 113.8, type: 'pop' }, { t: 113.8, type: 'sparkle', d: 1.4 });
for (let i = 0; i < 6; i++) EV.push({ t: 61.0 + i * .23, type: 'hoof' });
for (let i = 0; i < 9; i++) EV.push({ t: 91.4 + i * .24 + .1, type: 'stone' });
{ const prev = {}; for (let f = 0; f < DUR * 30; f++) { const t = f / 30; for (const k in AT) { const s = AT[k](t), ph = s.pose.walk || 0; if (s.vis && s.pose.stride && Math.floor(ph / Math.PI) !== Math.floor((prev[k] || 0) / Math.PI)) EV.push({ t, type: 'step' }); prev[k] = ph; } } }
EV.sort((a, b) => a.t - b.t);
window.EV = EV; window.DUR = DUR

// ---------- render ----------
const tmpV = new THREE.Vector3();
function toScreen(v) { const p = v.clone().project(cam); if (p.z > 1) return null; return [(p.x * .5 + .5) * W, (-p.y * .5 + .5) * H]; }
window.render = function (t) {
  // book
  const op = eio(seg(t, OPEN[0], OPEN[1])) * (1 - eio(seg(t, CLOSE[0] + .4, CLOSE[1])));
  book.setOpen(Math.PI / 2 * op + Math.sin(seg(t, OPEN[1] - .2, OPEN[1] + .5) * Math.PI) * -.03);
  let pg = 0; for (let i = 0; i < 4; i++) if (t >= TURNS[i][0] + .45) pg = i + 1;
  let turning = -1; for (let i = 0; i < 4; i++) if (t >= TURNS[i][0] + .45 && t < TURNS[i][1] - .3) turning = i;
  book.groundMat.map = PAGE[pg].ground; book.backMat.map = PAGE[turning >= 0 ? turning : pg].sky; book.groundMat.needsUpdate = book.backMat.needsUpdate = true;
  if (turning >= 0) {
    const a = TURNS[turning][0] + .45, b = TURNS[turning][1] - .3, lf = book.leafFront.material, lb = book.leafBack.material;
    lf.map = lf.emissiveMap = PAGE[turning].ground; lb.map = lb.emissiveMap = PAGE[turning + 1].sky; lf.needsUpdate = lb.needsUpdate = true;
    book.setLeaf(eio(seg(t, a, b)));
  } else book.setLeaf(0);
  updatePops(POPS, t);
  // slats: Ayodhya festive → dusk; war → lilac
  SL1.forEach((g, i) => { g.visible = t > TURNS[0][1] - .3 && t < TURNS[1][0] + .45; g.rotation.y = Math.PI * eio(seg(t, 39.6 + i * .25, 40.3 + i * .25)); });
  SL4.forEach((g, i) => { g.visible = t > TURNS[3][1] - .3 && t < CLOSE[0] + .5; g.rotation.y = Math.PI * eio(seg(t, 98.9 + i * .25, 99.6 + i * .25)); });
  // prologue: arrow, birds
  const ar = arrowAt(t); EX.arrow.visible = ar.vis; if (ar.vis) { EX.arrow.position.set(ar.x, ar.y, ar.z); EX.arrow.rotation.set(0, 0, Math.PI); EX.arrow.scale.setScalar(ar.s); }
  if (EX.bird2.g.visible) { const k = lieDown(t, 11.85, .35); if (k > 0) EX.bird2.g.rotation.x = -Math.PI / 2 * k; }
  if (EX.bird1.g.visible) { const fl = seg(t, 11.95, 13.6); if (fl > 0 && fl < 1) { EX.bird1.g.position.y = .006 * Math.abs(Math.sin(fl * 14)); EX.bird1.m.rotation.z = Math.sin(fl * 30) * .08; } else EX.bird1.g.position.y = 0; }
  // Mithila: the bow lifts, then snaps in two
  if (EX.bowL.g.visible) {
    const lift = ss(seg(t, 29.8, 30.8)), snap = eo(seg(t, 31.2, 31.6)), fall = ss(seg(t, 31.6, 32.1));
    for (const [r, s] of [[EX.bowL, -1], [EX.bowR, 1]]) { r.g.position.y = .02 + lift * .016 * (1 - fall) + Math.sin(t * 30) * .0006 * lift * (1 - snap); r.m.rotation.z = s * (-.05 * lift + snap * .7) ; if (fall > 0) r.g.rotation.x = -Math.PI / 2 * fall; r.g.position.x = .12 + s * snap * .012; }
  }
  // sandals: from Bharata's hands to the throne
  EX.sandals.visible = t > 49.6 && t < 54.6; if (EX.sandals.visible) { const k = eio(seg(t, 49.6, 50.4)); EX.sandals.position.set(lerp(-.132, -.1, k), lerp(.03, .0215, k) + Math.sin(k * Math.PI) * .008, lerp(.134, .1132, k)); }
  // deer runs off
  if (EX.deer.g.visible) { const k = seg(t, 61.0, 62.4); EX.deer.g.position.x = lerp(.13, .3, k); EX.deer.g.position.y = .004 * Math.abs(Math.sin(k * 18)); if (EX.deer.g.position.x > .23) EX.deer.g.visible = false; }
  // chariot on strings
  const ch = chariotAt(t); EX.chariot.visible = ch.vis; if (ch.vis) { EX.chariot.position.set(ch.x, ch.y, ch.z); EX.chariot.rotation.z = Math.sin(t * 2.4) * .04; }
  // sea
  for (const set of [EX.waves3, EX.waves4]) set.forEach((r, k) => { r.m.position.x = Math.sin(t * 1.7 + k * 1.3) * .006 * (k % 2 ? -1 : 1); });
  // crown on a string
  EX.crown.visible = t > 96.6 && t < 99.3; if (EX.crown.visible) { const d = Math.min(1, spring(t - 96.8, 4, .45)); EX.crown.position.set(-.15, lerp(.3, .051, d), .177); }
  // notes rising from the twins
  EX.notes.forEach((m, i) => { const per = 1.6, k = ((t - 104.6 + i * .4) % per) / per; m.visible = t > 104.6 && t < CLOSE[0] && t - 104.6 > i * .4 * 0; if (m.visible) { m.position.set(.055 + Math.sin(i * 2 + k * 4) * .02, .04 + k * .05, .168); m.scale.setScalar(Math.sin(k * Math.PI)); } });
  // the card that stays up on the closed cover
  finale.visible = t > 113.6; if (finale.visible) { const k = back(seg(t, 113.6, 114.2), 1.8); finale.position.set(0, 2 * PG + .0006, .16); finale.rotation.x = -Math.PI / 2 * (1 - k); }

  // actors
  const anchors = {};
  for (const k in AT) {
    const s = AT[k](t), a = A[k];
    a.root.visible = a.shadow.visible = s.vis && s.s > .01;
    if (!a.root.visible) continue;
    a.pose(s.pose);
    a.root.position.set(s.x, s.y, s.z); a.root.rotation.set(-Math.PI / 2 * s.lie, 0, 0);
    a.body.scale.set(s.sx * s.s, s.sy * s.s, s.s);
    a.shadow.position.set(s.x, .0004, s.z); a.shadow.scale.setScalar(s.s * clamp(1 - s.y * 12, .3, 1) * (1 - s.lie * .5)); a.shadow.visible = s.y < .03 && s.lie < .5;
    anchors[k] = a;
  }
  // lights
  const Lt = lightsAt(t);
  sun.intensity = Lt.sunI; sun.color.copy(Lt.sunCol); sun.position.set(-.35, .55, .75);
  spot.intensity = Lt.lampI * 2.2; hemi.intensity = Lt.hemiI; scene.environmentIntensity = Lt.envI; scene.backgroundIntensity = .42 + Lt.envI * .3;
  // camera
  const C = camAt(t);
  cam.position.copy(C.pos); cam.fov = C.fov; cam.lookAt(C.tgt); cam.updateProjectionMatrix(); cam.updateMatrixWorld(); camQ.copy(cam.quaternion);
  post.dof.focus = C.pos.distanceTo(C.tgt); post.dof.aper = C.aper; post.dof.maxCoc = QS.get('dof') === '0' ? 0 : 14;
  post.vig.uniforms.fade.value = 1; post.vig.uniforms.warm.value = .12; post.bloom.strength = .22;
  for (const p of PS) p.userData.update(t);
  scene.updateMatrixWorld(true);
  post.composer.render();
  // overlay
  OX.clearRect(0, 0, W, H);
  const hs = k => anchors[k] ? toScreen(anchors[k].head(tmpV)) : null;
  HUD.drawChapter(OX, t); HUD.drawShloka(OX, t);
  HUD.drawBang(OX, t, 64.6, hs('sita'));
  HUD.drawAction(OX, t, [toScreen(new THREE.Vector3(.12, .06 + PG, .12)), hs('hanuman')]);
  HUD.drawSubs(OX, t, DURS);
  HUD.drawEnd(OX, t);
  if (t < 1.2 || t > DUR - 1.4) { OX.fillStyle = `rgba(0,0,0,${1 - seg(t, 0, 1.2) * (1 - seg(t, DUR - 1.4, DUR))})`; OX.fillRect(0, 0, W, H); }
};
window.DBG = { book, cam, A, EX };
window.render(0);
window.READY = true;
