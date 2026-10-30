// print the timed narration script (and flag any line that leaves its beat or crowds the chapter's end)
import path from 'path'; import fs from 'fs'; import { fileURLToPath } from 'url';
const HERE = path.dirname(path.dirname(fileURLToPath(import.meta.url)));
const { openDemo, closeServer } = await import(path.join(HERE, '../../core/render/page.mjs'));
const { browser, page } = await openDemo(HERE, { w: 1440, h: 1080 });
const TL = await page.evaluate(() => window.TL);
const fmt = s => { const m = Math.floor(s / 60), r = s - m * 60; return `${String(m).padStart(2, '0')}:${r.toFixed(2).padStart(5, '0')}`; };
let out = '# Timed narration script\n\n| line | start | end | frames | beat | text | note |\n|---|---|---|---|---|---|---|\n';
TL.forEach(C => C.lines.forEach((L, i) => { const a = C.t0 + L.t, b = a + L.d, nx = C.lines[i + 1];
  const note = b > C.t0 + L.b1 + 0.01 ? `runs ${(b - C.t0 - L.b1).toFixed(2)} s past its beat` : '' + (!nx && C.t0 + 30 - b < 0.8 ? ' tight punchline pause' : '');
  out += `| ${L.id} | ${fmt(a)} | ${fmt(b)} | ${Math.round(a * 24)}–${Math.round(b * 24)} | ${fmt(C.t0 + L.b0)}–${fmt(C.t0 + L.b1)} | ${L.text} | ${note} |\n`; }));
fs.writeFileSync(path.join(HERE, 'qc', 'narration-script.md'), out); console.log(out.split('\n').filter(l => /past|tight/.test(l)).join('\n') || 'all lines inside their beats');
await browser.close(); closeServer();
