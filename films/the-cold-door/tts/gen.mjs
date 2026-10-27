// story.js → tts/lines.json
import fs from 'fs';
const { SEQ, CAST } = await import('../story.js');
const L = SEQ.filter(e => e[0] === 'L').map(([, who, id, text]) => ({ id, who, text, voice: CAST[who].voice, speed: CAST[who].speed }));
const ids = L.map(l => l.id); if (new Set(ids).size !== ids.length) throw new Error('dup id');
fs.writeFileSync(new URL('./lines.json', import.meta.url), JSON.stringify(L, null, 1));
console.log(L.length, 'lines', L.reduce((a, l) => a + l.text.split(/\s+/).length, 0), 'words');
