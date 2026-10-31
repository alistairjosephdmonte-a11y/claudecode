// Dump the shot manifest (camera, lens, frames, classification, narration cue) to qc/shot-list.md and qc/manifest.json
import fs from 'fs'; import path from 'path';
import { openDemo } from '../../../core/render/page.mjs';
const F = path.resolve(path.dirname(new URL(import.meta.url).pathname), '..');
const { browser, page } = await openDemo(F, {});
const M = await page.evaluate(() => window.MANIFEST); await browser.close();
fs.writeFileSync(path.join(F, 'qc/manifest.json'), JSON.stringify(M, null, 1));
const fmt = t => `${String(Math.floor(t / 60)).padStart(2, '0')}:${(t % 60).toFixed(2).padStart(5, '0')}`;
let md = '# Shot list: Brand Coroner, Case 001\n\n48 shots × 240 frames (10 s) at 24 fps = 11,520 frames. Camera positions are in table units (1 = 10 cm); the lens is the full-frame equivalent focal length.\n\n| Shot | Frames | Act | Title | Class | Sets | Light | Lens | Camera (start → end) | Narration cue | Transition |\n|---|---|---|---|---|---|---|---|---|---|---|\n';
for (const s of M) md += `| ${String(s.shot).padStart(3, '0')} | ${s.frames[0]}–${s.frames[1]} | ${s.act} | ${s.title} | ${s.cls}${s.dof ? ' · DOF' : ''}${s.split ? ' · split' : ''} | ${s.sets.join(', ') || 'evidence props'} | ${s.light} | ${s.lens} | ${s.cam0 ? `[${s.cam0.pos}] → [${s.cam1.pos}]` : 'black field'} | ${fmt(s.vo.t)} “${s.vo.text.slice(0, 48)}…” | ${s.transition} |\n`;
fs.writeFileSync(path.join(F, 'qc/shot-list.md'), md); console.log('manifest', M.length, 'shots');
process.exit(0);
