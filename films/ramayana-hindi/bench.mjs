import { chromium } from 'playwright-core';
import { serve } from './serve.mjs';
import { EXE, ARGS } from '../../core/render/browser.mjs';
const { server, port } = await serve(process.cwd());
const b = await chromium.launch({ executablePath: EXE, args: ARGS });
const p = await b.newPage({ viewport: { width: 1920, height: 1080 } });
await p.goto(`http://127.0.0.1:${port}/index.html${process.env.QS || ''}`);
await p.waitForFunction(() => window.READY === true, null, { timeout: 600000 });
for (const T of [300, 900, 1500]) {
  let tot = 0, tr = 0;
  for (let i = 0; i < 6; i++) { const t = T + i / 24; const a = Date.now(); const r = (await p.evaluate(t => window.grab(t), t)).length; tot += Date.now() - a; tr += r; }
  const info = await p.evaluate(() => { const r = window.DBG; let n = 0; r.book.root.parent.traverse(() => n++); return n; });
  console.log(T, 'frame ms', Math.round(tot / 6), 'render ms', Math.round(tr / 6), 'objects', info);
}
await b.close(); server.close();
