// Brand Coroner · Case 001 · Blockbuster. 48 shots × 10 s on one investigation table.
import * as THREE from 'three';
import { makePost } from './post.js';
import { RGBELoader } from 'three/addons/loaders/RGBELoader.js';
import { clamp, lerp, seg, ss, hash } from '/core/lib.js';
import { PAL, ZONE, materials, M } from './world.js';
import { table, dallas, plaza, boardroom, store, network, mail, desk } from './sets.js';
import { SHOTS, bindC } from './shots.js';

const QS = new URLSearchParams(location.search), W = innerWidth, H = innerHeight, SC = H / 1080;
const STORY = await (await fetch('./story.json')).json();
for (const f of ['800 100px BigShoulders', '700 40px "Plex Cond"', '600 40px "Plex Cond"', '400 40px "Plex Mono"', '500 40px "Plex Mono"', '400 40px Newsreader', 'italic 400 40px Newsreader', '600 40px Newsreader', '700 40px Newsreader']) await document.fonts.load(f);

const renderer = new THREE.WebGLRenderer({ antialias: !QS.has('noaa'), preserveDrawingBuffer: true });
renderer.setPixelRatio(1); renderer.setSize(W, H); renderer.shadowMap.enabled = true; renderer.shadowMap.type = THREE.PCFSoftShadowMap;
renderer.toneMapping = THREE.AgXToneMapping; renderer.toneMappingExposure = 1.0;
document.getElementById('stage').appendChild(renderer.domElement);
const scene = new THREE.Scene(); scene.background = new THREE.Color('#0d0f12');
const camera = new THREE.PerspectiveCamera(35, W / H, .05, 200);
const post = makePost(renderer, scene, camera, W, H, { ssaa: 1, ao: false, bloom: false });
post.bloom.strength = .12; post.bloom.threshold = 1.2; post.bloom.radius = .4; post.vig.uniforms.amt.value = .42; post.dof.maxCoc = 12;

materials(); table(scene);
{ const hdr = await new RGBELoader().loadAsync('/core/assets/polyhaven/photo_studio_loft_hall_2k.hdr'); const pm = new THREE.PMREMGenerator(renderer); const env = pm.fromEquirectangular(hdr).texture; [M.metal, M.disc, M.glass].forEach(m => { m.envMap = env; m.envMapIntensity = .5; m.needsUpdate = true; }); scene.userData.env = env; scene.traverse(o => { const m = o.material; if (m && m.isMeshStandardMaterial && m.metalness > 0) { m.envMap = env; m.envMapIntensity = .5; } }); hdr.dispose(); pm.dispose(); }
const C = { dallas: dallas(), plaza: plaza(), board: boardroom(), store: store(), net: network(), mail: mail(), desk: desk() };
scene.add(C.dallas, C.plaza.G, C.board.G, C.store.G, C.net.P, C.net.N, C.mail.G, C.desk.G);
const SETS = { dallas: [C.dallas], plaza: [C.plaza.G], board: [C.board.G], store: [C.store.G], plan: [C.net.P], net: [C.net.N], mail: [C.mail.G], desk: [C.desk.G] };
const props = new THREE.Group(); scene.add(props); C.add = o => { props.add(o); return o; };
bindC(C);

// —— light rig: one shadow key (spot), one sun (directional), sky fill, a pool of practicals ——
const hemi = new THREE.HemisphereLight('#dfe6ee', '#1a1410', .3); scene.add(hemi);
const key = new THREE.SpotLight('#fff1dc', 0, 0, .5, .9, 0); key.castShadow = true; key.shadow.mapSize.set(2048, 2048); key.shadow.bias = -.0004; key.shadow.normalBias = .02; key.shadow.radius = 3; scene.add(key, key.target);
const sun = new THREE.DirectionalLight('#ffe2bd', 0); sun.castShadow = true; sun.shadow.mapSize.set(2048, 2048); sun.shadow.bias = -.0004; sun.shadow.normalBias = .02; sun.shadow.radius = 3; scene.add(sun, sun.target);
const pts = Array.from({ length: 6 }, () => { const p = new THREE.PointLight('#fff', 0, 6, 2); scene.add(p); return p; });
function zc(z) { return ZONE[z] || [0, 0]; }
function lightRig([name, z]) {
  const [cx, cz] = zc(z); key.intensity = 0; sun.intensity = 0; key.castShadow = sun.castShadow = false; pts.forEach(p => p.intensity = 0); hemi.intensity = .3; hemi.color.set('#dfe6ee'); hemi.groundColor.set('#1a1410');
  scene.background.set('#0d0f12'); renderer.toneMappingExposure = 1;
  const K = (dx, dy, dz, I, ang, col = '#fff1dc') => { key.position.set(cx + dx, dy, cz + dz); key.target.position.set(cx, 0, cz); key.intensity = I; key.angle = ang; key.penumbra = .85; key.color.set(col); key.castShadow = true; key.shadow.camera.near = 2; key.shadow.camera.far = 60; key.shadow.camera.updateProjectionMatrix(); };
  const S = (dx, dy, dz, I, col = '#ffe2bd', ext = 9) => { sun.position.set(cx + dx, dy, cz + dz); sun.target.position.set(cx, 0, cz); sun.intensity = I; sun.color.set(col); sun.castShadow = true; const c = sun.shadow.camera; c.left = c.bottom = -ext; c.right = c.top = ext; c.near = 1; c.far = 80; c.updateProjectionMatrix(); };
  const P = (i, x, y, zz, I, col = '#f4f6ff', d = 6) => { const p = pts[i]; p.position.set(x, y, zz); p.intensity = I; p.color.set(col); p.distance = d; };
  if (name === 'table') { K(-7, 17, 9, 9, .55); hemi.intensity = .22; }
  if (name === 'wide') { K(-10, 40, 22, 14, .75); hemi.intensity = .35; }
  if (name === 'spot') { K(-4, 15, 6, 10, .32, '#fff4e4'); hemi.intensity = .08; }
  if (name === 'low') { K(-16, 5, 10, 11, .6); hemi.intensity = .12; }
  if (name === 'dusk') { K(-7, 17, 9, 2.2, .7, '#c9d4ff'); hemi.intensity = .06; renderer.toneMappingExposure = 1.15; }
  if (name === 'morning') { S(9, 4.5, 6, 3.4, '#ffd7a8', 10); hemi.intensity = .55; hemi.color.set('#bcd2ea'); scene.background.set('#1b2026'); }
  if (name === 'day') { S(-6, 10, 7, 2.8, '#fff0dc', 7); hemi.intensity = .7; hemi.color.set('#cfdcea'); }
  if (name === 'window') { S(9, 7, 3, 3.2, '#fff3e2', 6); hemi.intensity = .45; }
  if (name === 'night') { hemi.intensity = .05; hemi.color.set('#6d7fa8'); const [x, y, zz] = [cx, .9, cz - 2.3]; P(0, x - 1.8, y, zz, 1.4, '#f2f4ff', 4); P(1, x, y, zz, 1.4, '#f2f4ff', 4); P(2, x + 1.8, y, zz, 1.4, '#f2f4ff', 4); P(3, x - 3, 1.6, cz + 2, 1.2, '#ffcf8a', 5); P(4, x + 3, 1.6, cz + 2, 1.2, '#ffcf8a', 5); K(0, 6, 7, .9, .9, '#ffe3b0'); renderer.toneMappingExposure = 1.2; }
  if (name === 'fluor' || name === 'empty') { const s = name === 'empty' ? .65 : 1; hemi.intensity = .25 * s; hemi.color.set('#e8eef7');
    if (z === 'store') { [[-2, -.1], [0, -.1], [2, -.1]].forEach(([dx, dz], i) => P(i, cx + dx, .95, cz - 2.3 + dz, 1.9 * s, name === 'empty' ? '#dfe8ff' : '#f4f6ff', 3.6)); K(0, 9, 3, 1.5 * s, .5, '#eef3ff'); }
    else { [[-3, 0], [-1, 0], [1, 0], [3, 0]].forEach(([dx, dz], i) => P(i, cx + dx, 1.8, cz + dz, 2.2, '#f2f6ff', 5)); K(0, 10, 4, 3, .6, '#eef3ff'); } }
  [key, sun, ...pts].forEach(l => l.visible = l.intensity > 0); if (QS.has('nopts')) pts.forEach(p => p.visible = false);   // unused lights cost shading time on every pixel
}

// —— the desk screen: a representative early web page, or a representative player ——
function screen(kind, t) {
  const { g, c, t: tx } = C.desk.screen, w = c.width, h = c.height; g.fillStyle = '#c9c9c9'; g.fillRect(0, 0, w, h);
  g.fillStyle = '#0b2a6b'; g.fillRect(0, 0, w, 26); g.fillStyle = '#fff'; g.font = '600 15px "Plex Sans"'; g.fillText(kind === 'web' ? 'Rent DVDs Online - Web Browser' : 'Video Player', 8, 18);
  g.fillStyle = '#fff'; g.fillRect(6, 34, w - 12, 22); g.fillStyle = '#333'; g.font = '13px "Plex Mono"'; g.fillText('http://www.example.com/rent', 12, 50);
  if (kind === 'web') { g.fillStyle = '#fff'; g.fillRect(6, 62, w - 12, h - 70); g.fillStyle = '#7a1c22'; g.fillRect(6, 62, w - 12, 44); g.fillStyle = '#fff'; g.font = '700 22px "Plex Sans"'; g.fillText('MOVIES BY MAIL', 20, 92);
    g.fillStyle = '#223'; g.font = '600 14px "Plex Sans"'; ['Browse', 'Your Queue', 'Account', 'Help'].forEach((s, i) => g.fillText(s, 20 + i * 110, 128));
    for (let i = 0; i < 5; i++) { const y = 150 + i * 58; g.fillStyle = ['#2b3f6b', '#6c8b3c', '#b23b2e', '#444', '#7d3f8c'][i]; g.fillRect(20, y, 34, 48); g.fillStyle = '#333'; g.fillRect(66, y + 8, 220 - i * 20, 9); g.fillStyle = '#999'; g.fillRect(66, y + 26, 160, 7); g.fillStyle = '#e7e2c6'; g.fillRect(470, y + 12, 120, 24); g.fillStyle = '#333'; g.font = '600 13px "Plex Sans"'; g.fillText('Add to Queue', 482, y + 29); }
    const cy = 150 + Math.floor(t * 1.2 % 5) * 58; g.strokeStyle = '#000'; g.lineWidth = 1; g.strokeRect(470, cy + 12, 120, 24);
    g.fillStyle = '#000'; const mx = 420 + Math.sin(t * .7) * 90, my = 200 + Math.cos(t * .5) * 90; g.beginPath(); g.moveTo(mx, my); g.lineTo(mx, my + 16); g.lineTo(mx + 5, my + 12); g.lineTo(mx + 11, my + 12); g.closePath(); g.fill(); }
  else { const gr = g.createLinearGradient(0, 62, 0, h - 40); gr.addColorStop(0, '#2c4b6e'); gr.addColorStop(.6, '#d9925a'); gr.addColorStop(1, '#3a2a22'); g.fillStyle = gr; g.fillRect(6, 62, w - 12, h - 110);
    g.fillStyle = '#1d1a18'; g.beginPath(); g.moveTo(6, h - 120); for (let x = 6; x < w - 6; x += 20) g.lineTo(x, h - 130 - 30 * Math.sin(x * .02 + t * .3) - 15 * Math.sin(x * .05)); g.lineTo(w - 6, h - 48); g.lineTo(6, h - 48); g.fill();
    g.fillStyle = '#222'; g.fillRect(6, h - 46, w - 12, 40); g.fillStyle = '#888'; g.fillRect(40, h - 30, w - 80, 6); g.fillStyle = '#d33'; g.fillRect(40, h - 30, (w - 80) * (.12 + t * .006), 6); }
  const sl = g.createLinearGradient(0, 0, 0, 6); for (let y = 0; y < h; y += 3) { g.fillStyle = 'rgba(0,0,0,.06)'; g.fillRect(0, y, w, 1); }
  tx.needsUpdate = true;
}

// —— overlay typography ——
const [GW, GH] = [512, 512], grain = document.createElement('canvas'); grain.width = GW; grain.height = GH; { const g = grain.getContext('2d'), im = g.createImageData(GW, GH); let s = 7; for (let i = 0; i < im.data.length; i += 4) { s = (s * 16807) % 2147483647; const v = (s / 2147483647) * 255; im.data[i] = im.data[i + 1] = im.data[i + 2] = v; im.data[i + 3] = 10; } g.putImageData(im, 0, 0); }
function vignette(T) {
  const r = o.createRadialGradient(W / 2, H / 2, H * .35, W / 2, H / 2, H * .95); r.addColorStop(0, 'rgba(0,0,0,0)'); r.addColorStop(1, 'rgba(0,0,0,.42)'); o.fillStyle = r; o.fillRect(0, 0, W, H);
  const f = Math.floor(T * 24), ox = (hash(f) * GW) | 0, oy = (hash(f + .5) * GH) | 0; o.globalCompositeOperation = 'overlay'; o.fillStyle = o.createPattern(grain, 'repeat'); o.save(); o.translate(-ox, -oy); o.fillRect(ox, oy, W, H); o.restore(); o.globalCompositeOperation = 'source-over';
}
const ov = document.getElementById('ov'); ov.width = W; ov.height = H; const o = ov.getContext('2d');
const CLS = { 'RECONSTRUCTION': '#9aa6b0', 'ARCHIVAL MATERIAL': PAL.yellow, 'EDITORIAL GRAPHIC': PAL.ivory, 'HYPOTHETICAL SCENARIO': PAL.red };
function overlay(n, t, T) {
  o.clearRect(0, 0, W, H); const S = STORY.shots[n], sh = SHOTS[n], px = v => v * SC;
  const txt = (s, x, y, font, col, a = 1, ls = 0, align = 'left') => { o.globalAlpha = a; o.font = font; o.letterSpacing = ls + 'px'; o.fillStyle = col; o.textAlign = align; o.fillText(s, x, y); o.globalAlpha = 1; o.letterSpacing = '0px'; o.textAlign = 'left'; };
  if (sh.black) {
    o.fillStyle = '#000'; o.globalAlpha = sh.fadeFrom != null ? ss(seg(t, 0, 1.6)) : 1; o.fillRect(0, 0, W, H); o.globalAlpha = 1;
    if (n === 46) { const a = ss(seg(t, 1.8, 3.4)) * (1 - ss(seg(t, 9.3, 9.95))); const L = [['RECOGNIZING CHANGE', PAL.ivory], ['IS NOT THE SAME AS', PAL.ivory], ['SURVIVING IT.', PAL.red]];
      L.forEach(([s, c], i) => txt(s, W / 2, H / 2 + px(-70 + i * 92), `700 ${px(78)}px "Plex Cond"`, c, a * ss(seg(t, 1.8 + i * .5, 3.2 + i * .5)), px(6), 'center')); }
    if (n === 47) { const a = ss(seg(t, .6, 2.2)) * (1 - ss(seg(t, 8.2, 9.6)));
      txt('BRAND CORONER', W / 2, H / 2 + px(10), `800 ${px(150)}px BigShoulders`, PAL.ivory, a, px(14), 'center');
      o.globalAlpha = a; o.fillStyle = PAL.red; o.fillRect(W / 2 - px(330) * ss(seg(t, 1.4, 3)), H / 2 + px(42), px(660) * ss(seg(t, 1.4, 3)), px(3)); o.globalAlpha = 1;
      txt('EVERY DECISION LEAVES EVIDENCE.', W / 2, H / 2 + px(100), `500 ${px(28)}px "Plex Mono"`, PAL.ivory, a * ss(seg(t, 2.2, 3.6)), px(6), 'center');
      txt('CASE 001 · BLOCKBUSTER', W / 2, H / 2 + px(150), `500 ${px(18)}px "Plex Mono"`, '#8a929a', a * ss(seg(t, 2.6, 4)), px(5), 'center'); }
    return;
  }
  vignette(T);
  // bottom gradient for legibility
  const gr = o.createLinearGradient(0, H - px(190), 0, H); gr.addColorStop(0, 'rgba(8,9,11,0)'); gr.addColorStop(1, 'rgba(8,9,11,.62)'); o.fillStyle = gr; o.fillRect(0, H - px(190), W, px(190));
  const tg = o.createLinearGradient(0, 0, 0, px(120)); tg.addColorStop(0, 'rgba(8,9,11,.45)'); tg.addColorStop(1, 'rgba(8,9,11,0)'); o.fillStyle = tg; o.fillRect(0, 0, W, px(120));
  txt('BRAND CORONER · CASE 001', W - px(48), px(52), `500 ${px(17)}px "Plex Mono"`, PAL.ivory, .5, px(4), 'right');
  txt(`SHOT ${String(n + 1).padStart(3, '0')}`, W - px(48), px(76), `400 ${px(15)}px "Plex Mono"`, PAL.ivory, .35, px(4), 'right');
  // act slug on each act's first shot
  if (n % 8 === 0) { const a = ss(seg(t, .3, 1.2)) * (1 - ss(seg(t, 4.2, 5.2))); txt(`ACT ${String(S.act + 1).padStart(2, '0')}`, px(48), px(58), `500 ${px(18)}px "Plex Mono"`, PAL.red, a, px(5)); txt(STORY.acts[S.act], px(48), px(108), `700 ${px(52)}px "Plex Cond"`, PAL.ivory, a, px(5)); }
  // date / place title
  if (sh.title) { const a = ss(seg(t, .8, 1.8)) * (1 - ss(seg(t, 6.2, 7.2))), lines = sh.title.split('\n');
    lines.forEach((l, i) => txt(l, px(48), H - px(250) + i * px(64) - (lines.length - 1) * px(64) + px(64), `700 ${px(58)}px "Plex Cond"`, PAL.ivory, a, px(6)));
    o.globalAlpha = a; o.fillStyle = PAL.red; o.fillRect(px(48), H - px(222) + px(14), px(90) * ss(seg(t, 1, 2.2)), px(3)); o.globalAlpha = 1; }
  // classification chip and source line
  const ca = ss(seg(t, .25, .9)) * (1 - ss(seg(t, 9.55, 9.98)) * (n % 8 === 7 ? 0 : 0));
  const col = CLS[S.cls] || PAL.ivory; o.globalAlpha = ca; o.fillStyle = col; o.fillRect(px(48), H - px(86), px(12), px(12)); o.globalAlpha = 1;
  txt(S.cls + (S.cls === 'RECONSTRUCTION' ? ' · REPRESENTATIVE, NOT A HISTORICAL RECORD' : ''), px(70), H - px(75), `500 ${px(17)}px "Plex Mono"`, PAL.ivory, ca * .92, px(3));
  if (S.src) txt(S.src.toUpperCase(), px(70), H - px(48), `400 ${px(15)}px "Plex Mono"`, '#b9bfc5', ca * .85, px(2));
  if (n === 0) { o.fillStyle = '#000'; o.globalAlpha = 1 - ss(seg(t, 0, 1.6)); o.fillRect(0, 0, W, H); o.globalAlpha = 1; }
  if (n % 8 === 7 || n === 23) { /* act ends cut directly; the next act's slug carries the change */ }
}

// —— frame ——
let cur = -1;
function enterShot(n) {
  if (cur >= 0) SHOTS[cur].leave && SHOTS[cur].leave(C);
  props.clear(); cur = n; const sh = SHOTS[n];
  C.store.roof.visible = true; C.store.people.forEach(F => F.visible = true); C.store.clerk.visible = true; C.net.hero.scale.y = 1; C.net.small.visible = n >= 22; C.net.set(0, 0); C.board.folder.visible = n >= 3; C.store.rcase.position.y = -5; C.store.mcard.position.y = -5;
  C.store.lights.forEach(p => p.material.emissiveIntensity = 1.2);
  sh.enter && sh.enter(C);
}
function draw(n, t) {
  const sh = SHOTS[n]; if (n !== cur) enterShot(n);
  const show = new Set(sh.show || []); Object.entries(SETS).forEach(([k, arr]) => arr.forEach(g => g.visible = show.has(k)));
  lightRig(sh.light || ['table', 'docs']);
  const u = t / 10; sh.update && sh.update(u, t, C);
  if (sh.screen) screen(sh.screen, t);
  const aim = (cm) => { camera.position.set(...cm.p); camera.lookAt(...cm.l); camera.fov = 2 * Math.atan(12 / cm.f) * 180 / Math.PI; camera.aspect = W / H; camera.updateProjectionMatrix(); return cm; };
  if (sh.split) {
    const a = aim(sh.cam(u)); renderer.setScissorTest(true); camera.aspect = (W / 2) / H; camera.updateProjectionMatrix();
    renderer.setViewport(0, 0, W / 2 - 2, H); renderer.setScissor(0, 0, W / 2 - 2, H); renderer.render(scene, camera);
    lightRig(['fluor', 'mail']); const b = sh.cam2(u); camera.position.set(...b.p); camera.lookAt(...b.l); camera.aspect = (W / 2) / H; camera.updateProjectionMatrix();
    renderer.setViewport(W / 2 + 2, 0, W / 2 - 2, H); renderer.setScissor(W / 2 + 2, 0, W / 2 - 2, H); renderer.render(scene, camera);
    renderer.setScissorTest(false); renderer.setViewport(0, 0, W, H); return;
  }
  const cm = aim(sh.cam(u)); const d = Math.hypot(cm.p[0] - cm.l[0], cm.p[1] - cm.l[1], cm.p[2] - cm.l[2]);
  post.dof.focus = d; post.dof.aper = (sh.dof ?? .25) * 30 * (cm.f / 50) * (cm.f / 50) * Math.min(3, d / 2) * SC; post.vig.uniforms.fade.value = 1;
  if (sh.dof && !QS.has("nodof")) post.composer.render(); else renderer.render(scene, camera);
}
const ACT = QS.has('act') ? +QS.get('act') : -1;
window.DUR = ACT >= 0 ? 80 : 480; window.READY = false;
const render = T => {
  const n = Math.min(47, Math.floor(T / 10 + 1e-9)), t = T - n * 10, sh = SHOTS[n];
  if (sh.black) { if (sh.fadeFrom != null && t < 1.7) draw(sh.fadeFrom, 9.99); else { renderer.setClearColor('#000'); renderer.clear(); } }
  else draw(n, t);
  if (!QS.has('noov')) overlay(n, t, T);
};
window.render = T => render(ACT >= 0 ? T + ACT * 80 : T);
// timeline of narration lines (solver: start at shot + lead, never before the previous line has ended + breath)
const VD = await fetch('./voice.json').then(r => r.ok ? r.json() : {}).catch(() => ({}));
let prevEnd = -1; window.TL = STORY.shots.map((s, i) => { const d = VD[s.id] ?? 7, b0 = i * 10, lead = i === 0 ? 1.6 : i % 8 === 0 ? .9 : .45; let t0 = Math.max(b0 + lead, prevEnd + .45); if (i === 47) t0 = b0 + 3.6; if (i === 46) t0 = b0 + 2.2; prevEnd = t0 + d; return { id: s.id, t: +t0.toFixed(3), d, text: s.line }; });
window.EV = window.TL.map(l => ({ t: l.t, type: 'voice', id: l.id, d: l.d }));
if (QS.has('aniso')) scene.traverse(o => { const ms = o.material ? [].concat(o.material) : []; ms.forEach(m => ['map', 'normalMap', 'roughnessMap'].forEach(k => { if (m[k]) m[k].anisotropy = +QS.get('aniso'); })); });
if (QS.has('noenv')) scene.environment = null;
if (QS.has('noshadow')) { renderer.shadowMap.enabled = false; }
window.MANIFEST = SHOTS.map((sh, i) => { const S = STORY.shots[i], r = a => a.map(v => +v.toFixed(2)), c0 = sh.cam ? sh.cam(0) : null, c1 = sh.cam ? sh.cam(1) : null;
  return { shot: i + 1, id: S.id, title: S.title, act: S.act + 1, frames: [i * 240, i * 240 + 239], cls: S.cls, src: S.src, sets: sh.show || [], light: (sh.light || [])[0] || 'black',
    lens: c0 ? (c0.f === c1.f ? `${c0.f}mm` : `${c0.f}→${c1.f}mm`) : 'n/a', cam0: c0 && { pos: r(c0.p), look: r(c0.l) }, cam1: c1 && { pos: r(c1.p), look: r(c1.l) }, dof: !!sh.dof, split: !!sh.split,
    vo: { t: window.TL[i].t, text: S.line }, transition: i === 0 ? 'fade in from black' : i === 46 ? 'evidence fades to black' : i === 47 ? 'fade to black' : i % 8 === 0 ? 'cut; act slug' : 'cut' }; });
if (QS.has('t')) render(+QS.get('t'));
window.READY = true;
