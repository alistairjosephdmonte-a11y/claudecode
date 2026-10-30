// Entry: ?sheet=chars&who=<name> | ?sheet=board&ch=<n> → model / storyboard sheets; ?ch=<n> → one 30 s chapter; else the film
import { makeComp } from './gl.js';
import { BOIL } from './crayon.js';
const Q = new URLSearchParams(location.search);
const comp = makeComp(document.getElementById('gl'));
window.DUR = 1;
await Promise.all(['400 40px "Patrick Hand"', '700 40px Gaegu', '400 40px Gaegu'].map(f => document.fonts.load(f)));
if (Q.get('sheet')) {
  const M = await import('./sheets.js');
  window.render = t => { BOIL.step = Math.floor(t * 12); M.sheet(comp, Q, t); };
} else {
  const M = await import('./film.js');
  const ch = Q.get('ch'), off = ch ? (+ch - 1) * 30 : 0;
  window.TL = M.TL; window.DUR = ch ? 30 : M.DUR; window.EV = ch ? M.EV.filter(e => e.t >= off && e.t < off + 30).map(e => ({ ...e, t: +(e.t - off).toFixed(3) })) : M.EV; window.SUBS = M.SUBS;
  window.render = t => { const T = t + off; BOIL.step = Math.floor(T * 12 + 1e-6); M.frame(comp, T); };
}
window.READY = true;
