import { chromium } from 'playwright-core';
import { serve } from './serve.mjs';
import { EXE, ARGS } from '../../core/render/browser.mjs';
const { server, port } = await serve(process.cwd());
const b = await chromium.launch({ executablePath: EXE, args: ARGS });
const p = await b.newPage({ viewport: { width: 1920, height: 1080 } });
await p.goto(`http://127.0.0.1:${port}/index.html${process.env.QS || ''}`);
await p.waitForFunction(() => window.READY === true, null, { timeout: 600000 });
const r = await p.evaluate(() => {
  const gl = document.querySelector('#stage canvas').getContext('webgl2'); const out = [];
  for (let i = 0; i < 5; i++) { const t = 300 + i / 24; const a = performance.now(); window.render(t); const b = performance.now(); gl.finish(); const c = performance.now(); window.grab(t + .001); const d = performance.now(); out.push([b - a, c - b, d - c].map(Math.round)); }
  return out;
});
console.log(JSON.stringify(r));
await b.close(); server.close();
