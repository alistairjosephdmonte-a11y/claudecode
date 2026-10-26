// load the page once: print errors, the scene timeline and the total length
import { chromium } from 'playwright-core';
import { serve } from './serve.mjs';
import { EXE, ARGS } from '../../core/render/browser.mjs';
const { server, port } = await serve(process.cwd());
const b = await chromium.launch({ executablePath: EXE, args: ARGS });
const p = await b.newPage({ viewport: { width: 1920, height: 1080 } });
p.on('pageerror', e => { console.log('[pageerror]', e.message, (e.stack || '').split('\n').slice(0, 3).join(' | ')); process.exit(1); }); p.on('console', m => { if (m.type() === 'error') console.log('[err]', m.text().slice(0, 300)); });
const t0 = Date.now();
await p.goto(`http://127.0.0.1:${port}/index.html`);
await p.waitForFunction(() => window.READY === true || window.__err, null, { timeout: 600000 }).catch(e => console.log('timeout', e.message));
const r = await p.evaluate(() => ({ dur: window.DUR, lay: window.LAY && window.LAY.map(L => [L.id, L.S.toFixed(1), L.E.toFixed(1), (L.E - L.S).toFixed(1)]) }));
console.log('load', ((Date.now() - t0) / 1000).toFixed(0), 's  DUR', r.dur);
if (r.lay) for (const l of r.lay) console.log(l.join('\t'));
await b.close(); server.close();
