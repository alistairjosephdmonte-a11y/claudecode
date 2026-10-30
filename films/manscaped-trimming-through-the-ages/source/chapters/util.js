// shared helpers for the chapter pages
import { line, fill, handCircle, ellipse, smooth, xf } from '../crayon.js';
import { part } from '../rig.js';
import { track, clamp, hash, lerp } from '/core/lib.js';
import { K } from '../figs.js';
export { clamp, hash, lerp };
// camera keys [[t, [x, y, zoom]], ...] evaluated at 24 fps (monotone cubic, repeated keys collapse)
export const camOf = (c, keys) => { const k = keys.filter((q, i) => i === 0 || q[0] > keys[i - 1][0] + 0.05); return k.length > 1 ? track(k)(c.t) : k[0][1]; };
export const F = (col, sd, o = {}) => ({ col, p: 0.85, gap: 8, w: 10, ang: 0.6, seed: sd, ...o });
export const L = (sd, o = {}) => ({ w: 6, seed: sd, ...o });
export function ground(C, y, col, dr, sd, x0 = -200, x1 = 1640) {
  const P = []; for (let x = x0; x <= x1; x += 60) P.push([x, y + 10 * Math.sin(x * 0.01 + sd) + 6 * hash(x + sd)]);
  fill(C.f, [...P, [x1, y + 500], [x0, y + 500]], F(col, sd, { p: 0.6, gap: 12, w: 13, ang: 1.25, draw: dr }));
  line(C.l, P, L(sd + 1, { draw: dr }));
}
export function box(C, x, y, w, h, col, sd, dr = 1, o = {}) { part(C, [[x, y], [x + w, y], [x + w, y + h], [x, y + h]], col ? F(col, sd, { draw: dr, ...o }) : null, L(sd + 1, { draw: dr, w: o.lw || 6 })); }
export function cross(C, x0, y0, x1, y1, dr, sd, col = K.red) { for (let k = 0; k < 3; k++) line(C, [[x0, y0 + k * 9], [x1, y1 + k * 9]], { w: 9, col, p: 0.95, seed: sd + k, draw: clamp(dr * 3 - k) }); }
export function tick(C, x, y, s, dr, sd, col = K.green) { line(C, [[x - 14 * s, y], [x - 4 * s, y + 12 * s], [x + 18 * s, y - 16 * s]], { w: 7, col, p: 1, seed: sd, draw: dr }); }
export function sparkle(C, x, y, r, sd, p = 1) { line(C, [[x - r, y], [x + r, y]], { w: 4, col: K.yellow, p, seed: sd }); line(C, [[x, y - r], [x, y + r]], { w: 4, col: K.yellow, p, seed: sd + 1 }); }
export const wob = (c, hz = 6, a = 1) => a * Math.sin(Math.floor(c.tq * 12) * hz * 0.5236);
