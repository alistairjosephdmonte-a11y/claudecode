// stills of every scene: node shots.mjs [workers] [scene ids…] → out/shots/<scene>_<k>.jpg
import { chromium } from 'playwright-core';
import fs from 'fs';
import { serve } from './serve.mjs';
import { EXE, ARGS } from '../../core/render/browser.mjs';
const W = parseInt(process.argv[2] || '3'), only = process.argv.slice(3);
const { server, port } = await serve(process.cwd());
fs.mkdirSync('out/shots', { recursive: true });
async function open() {
  const b = await chromium.launch({ executablePath: EXE, args: ARGS }), p = await b.newPage({ viewport: { width: 1920, height: 1080 } });
  p.on('pageerror', e => console.log('[pageerror]', e.message));
  await p.goto(`http://127.0.0.1:${port}/index.html${process.env.QS || ''}`); await p.waitForFunction(() => window.READY === true, null, { timeout: 600000 }); return [b, p];
}
const [b0, p0] = await open();
const lay = await p0.evaluate(() => window.LAY); console.log('DUR', await p0.evaluate(() => window.DUR));
const jobs = [];
for (const L of lay) { if (only.length && !only.includes(L.id)) continue; const v = L.vo; const ts = [v[0][1] + 2.5]; if (v.length > 1) ts.push(v[Math.floor(v.length / 2)][1] + 3); if (v.length > 2) ts.push(v[v.length - 1][1] + 3); ts.forEach((t, k) => jobs.push([L.id, k, t])); }
const pages = [p0]; const browsers = [b0];
for (let i = 1; i < W; i++) { const [b, p] = await open(); pages.push(p); browsers.push(b); }
let n = 0;
await Promise.all(pages.map(async p => { while (jobs.length) { const [id, k, t] = jobs.shift(); await p.evaluate(t => window.render(t), t); await p.screenshot({ path: `out/shots/${id}_${k}.jpg`, type: 'jpeg', quality: 80 }); n++; } }));
console.log('shots', n);
for (const b of browsers) await b.close(); server.close();
