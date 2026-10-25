// Time a few frames in one worker: node bench.mjs   (QS='?q=...' to pass options)
import { chromium } from 'playwright-core';
import { serve } from './serve.mjs';
import { EXE, ARGS } from '../../core/render/browser.mjs';
const { server, port } = await serve(process.cwd());
const b = await chromium.launch({ executablePath: EXE, args: ARGS });
const p = await b.newPage({ viewport: { width: 1920, height: 1080 } });
await p.goto(`http://127.0.0.1:${port}/index.html${process.env.QS || ''}`);
await p.waitForFunction(() => window.READY === true, null, { timeout: 180000 });
const ts = [30, 30.1, 59, 59.1, 105, 105.1];
let tot = 0, tr = 0;
for (const t of ts) {
  const a = Date.now();
  const r = await p.evaluate(t => { const a = performance.now(); window.render(t); return performance.now() - a; }, t);
  await p.screenshot({ type: 'jpeg', quality: 95 });
  tot += Date.now() - a; tr += r;
}
console.log('per frame ms', Math.round(tot / ts.length), 'render() ms', Math.round(tr / ts.length));
await b.close(); server.close();
