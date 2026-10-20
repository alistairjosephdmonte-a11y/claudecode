// Review stills: node scripts/stills.mjs 20 70 100 ...  → out/stills/fNNN.jpg
import { bundle } from '@remotion/bundler';
import { renderStill, selectComposition } from '@remotion/renderer';
import path from 'node:path';
const frames = process.argv.slice(2).map(Number);
const serveUrl = await bundle({ entryPoint: path.resolve('src/index.ts') });
const browserExecutable = process.env.REMOTION_CHROME || null;
const composition = await selectComposition({ serveUrl, id: 'SeatIsTaken', browserExecutable });
for (const frame of frames) {
  const output = `out/stills/f${String(frame).padStart(3, '0')}.jpg`;
  await renderStill({ composition, serveUrl, frame, output, imageFormat: 'jpeg', jpegQuality: 85, browserExecutable });
  console.log(output);
}
