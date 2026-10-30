// Model sheets: front / three-quarter / side / rear, then six expressive poses, all through the crayon renderer.
import { layer, clear, CAM, W, H } from './crayon.js';
import { group, clearGroup } from './rig.js';
import { PAL } from './pal.js';
import { person, squirrel, say, K } from './figs.js';
const G = group(), TX = layer();
const POSES = {
  default: [{ expr: 'happy', armR: [70, -230] }, { expr: 'worried' }, { expr: 'shock', armL: [-70, -220], armR: [70, -220] }, { expr: 'eyebrow' }, { expr: 'smug', armR: [30, -150] }, { pose: 'walk', ph: 0.25, view: 'side' }],
};
export function sheet(comp, Q, t) {
  const who = Q.get('who') || 'gerald';
  CAM.x = W / 2; CAM.y = H / 2; CAM.s = 1; clearGroup(G); clear(TX);
  say(TX, who.toUpperCase() + '  ·  model sheet', 40, 70, { size: 46, font: 'Gaegu', weight: 700, align: 'left', seed: 3 });
  if (who.startsWith('squirrel')) {
    for (let i = 0; i < 3; i++) { squirrel(G, { x: 200 + i * 220, y: 470, s: 1.3, i }); say(TX, ['rust · acorn', 'golden · hammer', 'chestnut · specs'][i], 200 + i * 220, 520, { size: 30, seed: 10 + i }); }
    for (let i = 0; i < 3; i++) { squirrel(G, { x: 200 + i * 220, y: 920, s: 1.3, i, suit: true }); }
    say(TX, 'chapter 10: in business suits', 420, 990, { size: 30, seed: 20 });
    squirrel(G, { x: 1000, y: 470, s: 1.3, i: 0, flip: true }); squirrel(G, { x: 1240, y: 470, s: 1.3, i: 1, r: -0.3 });
    say(TX, 'flip · lean', 1120, 520, { size: 30, seed: 21 });
  } else {
    const views = ['front', 'q', 'side', 'back'];
    views.forEach((v, i) => { person(G, who, { x: 190 + i * 350, y: 470, s: 1.15, view: v }); say(TX, ['front', 'three-quarter', 'side', 'rear'][i], 190 + i * 350, 515, { size: 30, seed: 10 + i }); });
    (POSES[who] || POSES.default).forEach((p, i) => { person(G, who, { x: 125 + i * 238, y: 960, s: 0.95, ...p }); say(TX, p.pose || p.expr, 125 + i * 238, 1000, { size: 26, seed: 20 + i }); });
  }
  comp.paperCam(0, 0, 1); comp.begin(PAL.paper); comp.group(G); comp.crayon(TX.c); comp.finish({ vig: 0.15 });
}
