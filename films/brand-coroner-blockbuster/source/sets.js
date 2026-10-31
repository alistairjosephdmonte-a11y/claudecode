// The permanent sets on the investigation table. Each builder returns a Group placed at its ZONE, plus handles the shots animate.
import * as THREE from 'three';
import { mulberry, clamp, lerp } from '/core/lib.js';
import { PAL, ZONE, M, box, cyl, sheet, label, canvas, ctex, paperBase, figure, car } from './world.js';

const at = (G, z) => { G.position.set(ZONE[z][0], 0, ZONE[z][1]); return G; };
const uvScale = (geo, sx, sy) => { const uv = geo.attributes.uv; for (let i = 0; i < uv.count; i++) uv.setXY(i, uv.getX(i) * sx, uv.getY(i) * sy); return geo; };

export function table(scene) {
  const T = new THREE.Mesh(new THREE.BoxGeometry(70, 1, 46), [M.walnut, M.walnut, M.walnut, M.walnut, M.walnut, M.walnut]); T.position.y = -.5; T.receiveShadow = true; scene.add(T);
  const floor = new THREE.Mesh(new THREE.PlaneGeometry(400, 400), new THREE.MeshLambertMaterial({ color: '#0b0c0e'})); floor.rotation.x = -Math.PI / 2; floor.position.y = -9; floor.receiveShadow = true; scene.add(floor);
  // the dark evidence felt (shots 7, 47)
  const felt = new THREE.Mesh(new THREE.BoxGeometry(12, .04, 7), M.felt); felt.position.set(ZONE.felt[0], .02, ZONE.felt[1]); felt.receiveShadow = true; scene.add(felt);
  return T;
}

// —— Dallas, as an architect's massing model on a printed street plan ——
export function dallas() {
  const G = at(new THREE.Group(), 'dallas'), R = mulberry(2000);
  G.add(sheet(14, 10, (g, w, h) => { g.strokeStyle = 'rgba(60,60,70,.35)'; g.lineWidth = 6; for (let x = 0; x < w; x += w / 14) { g.beginPath(); g.moveTo(x, 0); g.lineTo(x + 40, h); g.stroke(); } for (let y = 0; y < h; y += h / 10) { g.beginPath(); g.moveTo(0, y); g.lineTo(w, y - 30); g.stroke(); }
    g.lineWidth = 26; g.strokeStyle = 'rgba(70,70,80,.28)'; g.beginPath(); g.moveTo(0, h * .82); g.bezierCurveTo(w * .3, h * .7, w * .6, h * .95, w, h * .78); g.stroke(); }, { ppu: 100, curl: 0, seed: 21 }));
  const [wc, wg] = canvas(64, 256); wg.fillStyle = '#d6d2c8'; wg.fillRect(0, 0, 64, 256); for (let y = 0; y < 256; y += 8) for (let x = 0; x < 64; x += 8) { wg.fillStyle = (x * 7 + y * 3) % 5 ? '#7d8a96' : '#a9b6bf'; wg.fillRect(x + 1, y + 2, 6, 5); }
  const wt = ctex(wc); wt.wrapS = wt.wrapT = THREE.RepeatWrapping;
  const mats = ['#d9d4c9', '#c9c5bc', '#b8bec4', '#d1c7b3'].map(c => new THREE.MeshLambertMaterial({ color: c, map: wt}));
  const glassT = new THREE.MeshLambertMaterial({ color: '#7f99a8'});
  for (let i = 0; i < 95; i++) {
    const x = (R() - .5) * 12, z = (R() - .5) * 8, dc = Math.hypot(x / 6, z / 4), hgt = Math.max(.25, (1 - dc) * (R() * 3.4 + .4)), w = .4 + R() * .6, d = .4 + R() * .6;
    const geo = uvScale(new THREE.BoxGeometry(w, hgt, d), w * 2, hgt * 2), m = new THREE.Mesh(geo, R() < .12 ? glassT : mats[i % 4]);
    m.position.set(x, hgt / 2 + .012, z); m.castShadow = m.receiveShadow = true; G.add(m);
  }
  // a few taller towers and a ball-topped observation tower, as a generic skyline silhouette
  [[-1.2, -.6, 4.4, .7], [.4, -.2, 3.9, .6], [1.6, .6, 3.3, .8], [-.2, 1.1, 3.0, .55]].forEach(([x, z, h, w], i) => { const m = new THREE.Mesh(uvScale(new THREE.BoxGeometry(w, h, w), w * 2, h * 2), i === 1 ? glassT : mats[i]); m.position.set(x, h / 2, z); m.castShadow = m.receiveShadow = true; G.add(m); });
  { const [bc, bg] = canvas(16, 256), gr = bg.createLinearGradient(0, 0, 0, 256); gr.addColorStop(0, '#5f7894'); gr.addColorStop(.55, '#c9a98a'); gr.addColorStop(1, '#e9c9a0'); bg.fillStyle = gr; bg.fillRect(0, 0, 16, 256);
    const sw = new THREE.Mesh(new THREE.CylinderGeometry(9, 9, 7, 48, 1, true, Math.PI * .75, Math.PI * .5), new THREE.MeshBasicMaterial({ map: ctex(bc), side: THREE.BackSide, toneMapped: false })); sw.position.set(0, 3.5, 3.5); G.add(sw); }
  cyl(.09, 2.6, M.concrete, -3.4, 0, -.9, G); const ball = new THREE.Mesh(new THREE.SphereGeometry(.34, 24, 16), new THREE.MeshLambertMaterial({ color: '#d7d3cc'})); ball.position.set(-3.4, 2.75, -.9); ball.castShadow = true; G.add(ball);
  return G;
}

// —— the arrival: a representative office tower entrance at figure scale ——
export function plaza() {
  const G = at(new THREE.Group(), 'plaza');
  box(9, .03, 7, M.concrete, 0, 0, 0, G);
  const [pc, pg] = canvas(512, 512); pg.fillStyle = '#b7b2a8'; pg.fillRect(0, 0, 512, 512); pg.strokeStyle = 'rgba(80,75,70,.35)'; pg.lineWidth = 2; for (let i = 0; i <= 512; i += 32) { pg.beginPath(); pg.moveTo(i, 0); pg.lineTo(i, 512); pg.moveTo(0, i); pg.lineTo(512, i); pg.stroke(); }
  const pt = ctex(pc); pt.wrapS = pt.wrapT = THREE.RepeatWrapping; pt.repeat.set(5, 4);
  const pav = new THREE.Mesh(new THREE.PlaneGeometry(9, 7), new THREE.MeshLambertMaterial({ map: pt})); pav.rotation.x = -Math.PI / 2; pav.position.y = .032; pav.receiveShadow = true; G.add(pav);
  // facade: stone base, mullioned glass, a revolving-door bay
  box(7, 6, 1.2, M.concrete, 0, 0, -3, G);
  const gl = new THREE.MeshLambertMaterial({ color: '#5d6f7a'});
  box(5.6, 2.2, .06, gl, 0, .05, -2.38, G);
  for (let x = -2.8; x <= 2.81; x += .7) box(.05, 2.25, .1, M.metal, x, .05, -2.34, G);
  box(5.8, .12, .14, M.metal, 0, 2.25, -2.33, G); box(1.4, .08, 1.2, M.metal, 0, 2.6, -1.9, G);   // canopy
  for (let x = -2.8; x <= 2.8; x += .9) box(.06, 3.4, .06, M.metal, x, 2.6, -2.36, G);
  [-2, 2].forEach(x => { cyl(.28, .5, M.concrete, x, 0, .2, G); const tr = new THREE.Mesh(new THREE.SphereGeometry(.42, 12, 10), new THREE.MeshLambertMaterial({ color: '#5f6b4c'})); tr.position.set(x, .85, .2); tr.castShadow = true; G.add(tr); });
  const people = [0, 1, 2].map(i => { const F = figure({ h: .62, mat: M.figureDark }); G.add(F); return F; });
  return { G, people };
}

// —— a representative boardroom, cut away so the camera can look in ——
export function boardroom() {
  const G = at(new THREE.Group(), 'board'), wood = M.wood;
  const fl = box(7, .06, 5, new THREE.MeshLambertMaterial({ color: '#7a6a5c'}), 0, 0, 0, G);
  box(7, 2.6, .12, M.white, 0, 0, -2.5, G); box(.12, 2.6, 5, M.white, -3.5, 0, 0, G);
  // window wall on the right (+x) with mullions; daylight comes through
  box(.12, .5, 5, M.white, 3.5, 0, 0, G); box(.12, .3, 5, M.white, 3.5, 2.3, 0, G);
  for (let z = -2.5; z <= 2.51; z += 1) box(.14, 1.8, .1, M.white, 3.5, .5, z, G);
  box(.04, 1.8, 5, M.glass, 3.48, .5, 0, G);
  box(4.2, .08, 1.5, wood, 0, .72, 0, G); [[-1.7, -.5], [1.7, -.5], [-1.7, .5], [1.7, .5]].forEach(([x, z]) => box(.08, .72, .08, M.dark, x, 0, z, G));
  const chairM = new THREE.MeshLambertMaterial({ color: '#2a211c'});
  for (let i = 0; i < 5; i++) for (const s of [-1, 1]) { const C = new THREE.Group(); box(.42, .08, .42, chairM, 0, .44, 0, C); box(.42, .55, .08, chairM, 0, .5, .2 * s, C); cyl(.03, .44, M.metal, 0, 0, 0, C, 8); C.position.set(-1.6 + i * .8, 0, s * 1.1); G.add(C); }
  box(.06, .9, 1.6, new THREE.MeshLambertMaterial({ color: '#3a4048'}), -3.42, 1.2, 0, G);   // a blank wall screen
  for (const x of [-1.5, 0, 1.5]) { const p = box(.9, .03, .5, new THREE.MeshLambertMaterial({ color: '#fff', emissive: '#fff6e6', emissiveIntensity: .9 }), x, 2.6, 0, G); p.castShadow = false; }
  const folder = sheet(.5, .36, (g, w, h) => { g.fillStyle = 'rgba(176,140,80,.35)'; g.fillRect(0, 0, w, h); g.fillStyle = 'rgba(120,90,50,.25)'; g.fillRect(0, h * .02, w, 3); g.fillRect(w * .62, 0, w * .3, h * .05); }, { ppu: 900, color: '#dcc596', thick: .004, curl: .02 }); folder.position.set(0, .81, .3); G.add(folder);
  const tab = box(.15, .004, .03, new THREE.MeshLambertMaterial({ color: '#d3bb8a'}), .12, 0, -.195, folder);
  return { G, folder };
}

// —— the representative video rental store (exterior lot, interior aisles, counter) ——
export function store() {
  const G = at(new THREE.Group(), 'store'), R = mulberry(1990);
  box(10, .04, 7, M.asphalt, 0, 0, 0, G);
  for (let i = 0; i < 9; i++) box(.03, .006, .9, M.white, -4 + i * 1, .04, 2.4, G);
  box(10, .06, .9, M.concrete, 0, .04, -.25, G);   // sidewalk
  const W = 6, D = 3.6, H = 1.05, z0 = -2.3;
  const inner = new THREE.Group(); inner.position.set(0, .06, z0); G.add(inner);
  box(W, .02, D, new THREE.MeshLambertMaterial({ color: '#c8c3b6'}), 0, 0, 0, inner);   // floor
  box(W, H, .08, M.white, 0, 0, -D / 2, inner); box(.08, H, D, M.white, -W / 2, 0, 0, inner); box(.08, H, D, M.white, W / 2, 0, 0, inner);
  // storefront glass with mullions, door gap at centre
  const front = new THREE.Group(); inner.add(front);
  box(W, .12, .08, M.dark, 0, 0, D / 2, front); box(W, .1, .08, M.dark, 0, H - .1, D / 2, front);
  box(W, H - .2, .03, M.glass, 0, .1, D / 2, front); for (let x = -W / 2; x <= W / 2 + .01; x += .75) box(.04, H, .06, M.dark, x, 0, D / 2, front);
  // fascia and sign (editorial: a generic VIDEO sign, no company logo)
  const fascia = box(W + .2, .42, .5, M.blue, 0, H - .05, D / 2 - .15, inner);
  const sign = label('VIDEO', { size: 150, weight: 700, font: '"Plex Cond"', col: '#1b2b4a', bg: PAL.yellow, track: 18, ppu: 560 }); sign.rotation.x = Math.PI / 2; sign.position.set(0, H + .16, D / 2 + .11); inner.add(sign);
  const roof = box(W + .2, .08, D + .1, M.concrete, 0, H + .3, -.05, inner);
  // aisles of cases: one instanced mesh, spines in period colours
  const caseGeo = new THREE.BoxGeometry(.035, .1, .07), cases = new THREE.InstancedMesh(caseGeo, new THREE.MeshLambertMaterial({ }), 2600); let n = 0;
  const cols = ['#2b3f6b', '#b23b2e', '#e8c547', '#2f2f33', '#6c8b3c', '#d9d6cf', '#7d3f8c', '#c76b2e'].map(c => new THREE.Color(c)), q = new THREE.Object3D();
  const shelf = (x, z, len, rot) => { const S = new THREE.Group(); S.position.set(x, 0, z); S.rotation.y = rot; inner.add(S); box(len, .62, .22, M.white, 0, 0, 0, S);
    for (let r = 0; r < 4; r++) for (let i = 0; i < len / .045 - 1; i++) for (const s of [-1, 1]) { if (n >= 2600) return; q.position.set(-len / 2 + .04 + i * .045, .12 + r * .14, s * .12); q.rotation.set(0, 0, 0); q.updateMatrix(); S.updateMatrixWorld(); q.matrix.premultiply(new THREE.Matrix4().compose(S.position, S.quaternion, S.scale)); cases.setMatrixAt(n, q.matrix); cases.setColorAt(n, cols[Math.floor(R() * cols.length)]); n++; } };
  for (let i = 0; i < 4; i++) shelf(-1.6 + i * .9, -.3, 1.9, Math.PI / 2);
  shelf(0, -D / 2 + .15, W - .4, 0);
  cases.count = n; cases.castShadow = true; cases.receiveShadow = true; inner.add(cases);
  // counter + register
  const counter = new THREE.Group(); counter.position.set(2.2, 0, .8); inner.add(counter);
  box(1.4, .4, .4, M.blue, 0, 0, 0, counter); box(1.5, .04, .5, M.white, 0, .4, 0, counter);
  box(.2, .12, .16, M.dark, -.4, .44, 0, counter); box(.14, .06, .02, new THREE.MeshLambertMaterial({ color: '#1b3a2c', emissive: '#3c8c5c', emissiveIntensity: .8 }), -.4, .53, -.04, counter);
  // ceiling light panels
  const lights = []; for (let i = 0; i < 3; i++) for (let j = 0; j < 2; j++) { const p = box(.8, .02, .25, new THREE.MeshLambertMaterial({ color: '#fff', emissive: '#f4f7ff', emissiveIntensity: 1.2 }), -2 + i * 2, H - .05, -.8 + j * 1.4, inner); p.castShadow = false; lights.push(p); }
  // the lot: cars and customers
  const cars = [['#7b1e22', -3.2, 1.6], ['#d8d6d0', -1.2, 1.6], ['#2a3a5a', 2.6, 1.7], ['#5d5a52', 3.8, 1.6]].map(([c, x, z]) => { const C = car(c); C.position.set(x, .04, z); C.rotation.y = Math.PI / 2; G.add(C); return C; });
  const people = []; for (let i = 0; i < 7; i++) { const F = figure({ h: .5, mat: i % 2 ? M.figure : M.figureDark }); G.add(F); people.push(F); }
  const clerk = figure({ h: .5 }); clerk.position.set(2.2, .06, z0 + .45); G.add(clerk);
  // props for the counter macro: a rental case and a membership card
  const rcase = box(.07, .012, .1, new THREE.MeshLambertMaterial({ color: '#2b3f6b'}), 0, 0, 0); G.add(rcase);
  const mcard = sheet(.085, .054, (g, w, h) => { g.fillStyle = PAL.blue; g.fillRect(0, 0, w, h); g.fillStyle = PAL.yellow; g.fillRect(0, h * .62, w, h * .14); g.fillStyle = '#fff'; g.font = `600 ${h * .16}px "Plex Mono"`; g.fillText('MEMBER', w * .08, h * .3); }, { ppu: 3000, base: false, curl: 0, thick: .003 }); G.add(mcard);
  return { G, inner, roof, front, people, clerk, cars, lights, counter, rcase, mcard, H, D, z0 };
}

// —— a paper floor plan from which one store rises, then a network on a plinth ——
export function network() {
  const P = at(new THREE.Group(), 'plan');
  const plan = sheet(6, 4, (g, w, h) => { g.strokeStyle = '#2f4a78'; g.lineWidth = 6; g.strokeRect(w * .2, h * .2, w * .6, h * .55); g.lineWidth = 3; for (let i = 1; i < 5; i++) { g.beginPath(); g.moveTo(w * (.24 + i * .1), h * .3); g.lineTo(w * (.24 + i * .1), h * .62); g.stroke(); }
    g.strokeRect(w * .62, h * .62, w * .14, h * .08); g.font = `500 ${h * .035}px "Plex Mono"`; g.fillStyle = '#2f4a78'; g.fillText('TYPICAL STORE PLAN (REPRESENTATIVE)', w * .2, h * .14); g.fillText('AISLES', w * .36, h * .68); g.fillText('COUNTER', w * .62, h * .78); }, { ppu: 160, curl: 0, seed: 33 });
  P.add(plan);
  const hero = new THREE.Group(); P.add(hero); box(3.6, .5, 2.2, M.white, 0, 0, 0, hero); box(3.7, .16, .25, M.blue, 0, .42, 1.1, hero); box(1.0, .1, .02, M.yellow, 0, .45, 1.24, hero);
  const N0 = at(new THREE.Group(), 'net');
  const plinth = box(13, 1.2, 9, new THREE.MeshLambertMaterial({ color: '#1d2024'}), 0, 0, 0, N0);   // the heavy foundation the network stands on
  for (let i = 0; i < 9; i++) box(.06, 1.2, .04, M.metal, -6 + i * 1.5, 0, 4.51, N0);
  const N = new THREE.Group(); N.position.y = 1.2; N0.add(N);
  const field = sheet(12.6, 8.6, (g, w, h) => { g.strokeStyle = 'rgba(40,60,90,.25)'; g.lineWidth = 2; for (let x = 0; x < w; x += w / 24) { g.beginPath(); g.moveTo(x, 0); g.lineTo(x, h); g.stroke(); } for (let y = 0; y < h; y += h / 16) { g.beginPath(); g.moveTo(0, y); g.lineTo(w, y); g.stroke(); }
    g.font = `500 ${h * .022}px "Plex Mono"`; g.fillStyle = 'rgba(40,50,70,.7)'; g.fillText('SCHEMATIC — NOT A MAP OF ACTUAL STORE LOCATIONS', w * .03, h * .97); }, { ppu: 110, curl: 0, seed: 44 });
  field.position.y = .03; N.add(field);
  const R = mulberry(9100), MAX = 1820, pts = [];   // each model stands for about five stores
  for (let i = 0; i < MAX; i++) { let x, z, k = 0; do { x = (R() - .5) * 12; z = (R() - .5) * 8; k++; } while (k < 6 && R() > .35 + .65 * Math.exp(-((x + 2) ** 2 + (z + 1) ** 2) / 16)); pts.push([x, z, Math.hypot(x + .4, z + .2) + R() * 1.8]); }
  pts.sort((a, b) => a[2] - b[2]);
  const bGeo = new THREE.BoxGeometry(.2, .1, .15), body = new THREE.InstancedMesh(bGeo, new THREE.MeshLambertMaterial({ color: '#f1ede4'}), MAX), win = new THREE.InstancedMesh(new THREE.BoxGeometry(.12, .012, .08), new THREE.MeshBasicMaterial({ color: '#ffffff', toneMapped: false }), MAX), roofB = new THREE.InstancedMesh(new THREE.BoxGeometry(.21, .03, .035), M.blue, MAX);
  [body, win, roofB].forEach(m => { m.castShadow = m.receiveShadow = m !== win; N.add(m); });
  const q = new THREE.Object3D(), warm = new THREE.Color('#ffcf73'), off = new THREE.Color('#2a2c30'), e = new THREE.Euler(), v = new THREE.Vector3();
  function put(m, i, x, y, z, ry, s, dz = 0) { e.set(0, ry, 0); v.set(Math.sin(ry) * dz, 0, Math.cos(ry) * dz); q.position.set(x + v.x, y, z + v.z); q.rotation.copy(e); q.scale.setScalar(s || 1e-4); q.updateMatrix(); m.setMatrixAt(i, q.matrix); }
  function set(nOn, grow, lit) {   // nOn stores visible, grow (0..1) the newest rising, lit(i) → 0..1 rooftop light
    for (let i = 0; i < MAX; i++) { const [x, z] = pts[i], s = i < nOn ? 1 : i < nOn + 40 ? clamp(grow - (i - nOn) / 40) : 0, ry = (i % 4) * Math.PI / 2;
      put(body, i, x, .04 + .05 * s, z, ry, s); put(win, i, x, .04 + .1 * s + .006, z, ry, s, -.02); put(roofB, i, x, .04 + .1 * s, z, ry, s, .06);
      win.setColorAt(i, off.clone().lerp(warm, lit ? lit(i) : 1)); }
    body.instanceMatrix.needsUpdate = win.instanceMatrix.needsUpdate = roofB.instanceMatrix.needsUpdate = true; win.instanceColor.needsUpdate = true;
  }
  set(0, 0);
  // a much smaller mail operation beside the plinth (shot 23)
  const small = new THREE.Group(); small.position.set(8.6, 0, 2.6); N0.add(small); box(1.2, .2, .8, M.white, 0, 0, 0, small); box(1.22, .05, .1, M.nred, 0, .2, .4, small);
  return { P, N: N0, top: N, hero, plan, set, MAX, pts, small };
}

// —— the DVD-by-mail fulfilment and sorting facility ——
export function mail() {
  const G = at(new THREE.Group(), 'mail');
  box(9, .05, 6, M.concrete, 0, 0, 0, G); box(9, 1.6, .1, M.white, 0, 0, -3, G); box(.1, 1.6, 6, M.white, -4.5, 0, 0, G);
  const belts = [], path = [];
  for (let i = 0; i < 3; i++) { const z = -1.6 + i * 1.3; box(7, .26, .32, M.dark, 0, .05, z, G); box(7, .02, .28, new THREE.MeshLambertMaterial({ color: '#3a3d42'}), 0, .31, z, G); for (let x = -3.4; x <= 3.4; x += .4) box(.04, .26, .04, M.metal, x, .05, z + .17, G); belts.push(z); }
  // sorting rack of cubbies
  const rack = new THREE.Group(); rack.position.set(0, .05, 2.1); G.add(rack); box(5, 1, .4, M.white, 0, 0, 0, rack);
  for (let i = 0; i < 10; i++) for (let j = 0; j < 4; j++) box(.42, .2, .02, M.card, -2.25 + i * .5, .1 + j * .23, .2, rack);
  const env = new THREE.InstancedMesh(new THREE.BoxGeometry(.2, .012, .14), M.nred, 120); env.castShadow = true; G.add(env);
  const bins = []; for (let i = 0; i < 4; i++) bins.push(box(.6, .4, .45, new THREE.MeshLambertMaterial({ color: '#5b6470'}), -3 + i * 2, .05, 1.0, G));
  const workers = []; for (let i = 0; i < 4; i++) { const F = figure({ h: .55, mat: i % 2 ? M.figure : M.figureDark }); F.position.set(-2.6 + i * 1.8, .05, -1.6 + (i % 3) * 1.3 + .45); F.rotation.y = Math.PI; G.add(F); workers.push(F); }
  const q = new THREE.Object3D();
  function step(t) { for (let i = 0; i < 120; i++) { const b = i % 3, ph = ((i / 120) * 7 + t * .55 * (b === 1 ? -1 : 1) + b * .3) % 7, x = ((ph + 7) % 7) - 3.5; q.position.set(x, .35, belts[b] + (Math.sin(i * 12.3) * .05)); q.rotation.set(0, Math.sin(i * 3.1) * .15, 0); q.updateMatrix(); env.setMatrixAt(i, q.matrix); } env.instanceMatrix.needsUpdate = true; }
  step(0);
  for (let i = 0; i < 4; i++) { const p = box(1.4, .02, .3, new THREE.MeshLambertMaterial({ color: '#fff', emissive: '#f2f6ff', emissiveIntensity: 1.1 }), -3 + i * 2, 1.9, 0, G); p.castShadow = false; }
  return { G, step, workers };
}

// —— an early-2000s desk: CRT monitor, beige tower, keyboard, a window ——
export function desk() {
  const G = at(new THREE.Group(), 'desk');
  box(7, .04, 5, new THREE.MeshLambertMaterial({ color: '#8a8070'}), 0, 0, 0, G);
  box(7, 3.2, .1, new THREE.MeshLambertMaterial({ color: '#d8d0c0'}), 0, 0, -2.5, G);
  // a window on the back wall
  box(1.8, 1.3, .02, new THREE.MeshLambertMaterial({ color: '#cfe2f0', emissive: '#cfe2f0', emissiveIntensity: .7 }), 2.2, 1.5, -2.44, G);
  for (const [w, h, x, y] of [[1.9, .07, 2.2, 1.46], [1.9, .07, 2.2, 2.8], [.07, 1.4, 1.28, 1.46], [.07, 1.4, 3.12, 1.46], [.05, 1.3, 2.2, 1.5]]) box(w, h, .06, M.white, x, y, -2.42, G);
  const top = box(3.2, .08, 1.5, M.wood, 0, 1.0, -1.6, G); for (const x of [-1.5, 1.5]) box(.08, 1.0, 1.4, M.wood, x, 0, -1.6, G);
  const crt = new THREE.Group(); crt.position.set(-.2, 1.08, -1.75); G.add(crt);
  box(.9, .78, .85, M.beige, 0, .08, -.05, crt); box(.6, .5, .4, M.beige, 0, .1, -.55, crt); box(.4, .08, .4, M.beige, 0, 0, 0, crt);
  const [sc, sg] = canvas(640, 480), st = ctex(sc);
  const screen = new THREE.Mesh(new THREE.PlaneGeometry(.72, .54), new THREE.MeshBasicMaterial({ map: st, toneMapped: false })); screen.position.set(0, .48, .381); crt.add(screen);
  box(.8, .04, .26, M.beige, -.2, 1.08, -1.05, G); box(.1, .03, .14, M.beige, .45, 1.08, -1.05, G);
  box(.36, .9, .8, M.beige, 1.1, 1.08, -1.7, G);
  const chair = new THREE.Group(); chair.position.set(-.2, 0, -.2); G.add(chair); box(.6, .08, .6, M.dark, 0, .6, 0, chair); box(.6, .7, .08, M.dark, 0, .66, .3, chair); cyl(.04, .6, M.metal, 0, 0, 0, chair, 8);
  const viewer = figure({ h: 1.7 }); viewer.position.set(-.2, .0, -.25); viewer.rotation.y = Math.PI; viewer.visible = false; G.add(viewer);
  return { G, screen: { c: sc, g: sg, t: st }, viewer, chair };
}
