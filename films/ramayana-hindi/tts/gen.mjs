// script.js → tts/lines.json (Kokoro, Hindi, Indian female voice)
import fs from 'fs';
const { SCENES } = await import('../script.js');
const lines = SCENES.flatMap(s => s.vo.map(([id, text]) => ({ id, text: text.replace(/[“”]/g, ''), voice: 'hf_beta', speed: .87, lang: 'hi' })));
const ids = lines.map(l => l.id); const dup = ids.filter((x, i) => ids.indexOf(x) !== i); if (dup.length) throw new Error('dup ids ' + dup);
fs.writeFileSync(new URL('./lines.json', import.meta.url), JSON.stringify(lines, null, 1));
console.log(lines.length, 'lines', lines.reduce((a, l) => a + l.text.split(' ').length, 0), 'words');
