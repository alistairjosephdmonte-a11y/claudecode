// print the page timeline: node films/swoosh-crayon/tl.mjs
import path from 'path'; import { fileURLToPath } from 'url';
const HERE = path.dirname(fileURLToPath(import.meta.url));
const { openDemo, closeServer } = await import(path.join(HERE, '../../core/render/page.mjs'));
const { browser, page } = await openDemo(HERE);
const r = await page.evaluate(() => ({ k: window.KS, dur: window.DUR, pages: window.TL.pages.map(p => [p.id, +p.t0.toFixed(1), +p.dur.toFixed(1), p.lines.map(l => +(p.t0 + l.t).toFixed(1)).join(' ')]) }));
console.log('k', r.k.toFixed(2), 'dur', r.dur); r.pages.forEach(p => console.log(p.join('  ')));
await browser.close(); closeServer();
