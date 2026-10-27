// Google Fonts (SIL OFL) → fonts/ + fonts/fonts.css (latin only)
import fs from 'fs';
const UA = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Safari/537.36';
let out = '', n = 0; fs.mkdirSync('fonts', { recursive: true });
for (const f of ['family=Titan+One', 'family=Baloo+2:wght@600;800', 'family=Caveat+Brush']) {
  let css = await (await fetch(`https://fonts.googleapis.com/css2?${f}&display=block`, { headers: { 'User-Agent': UA } })).text();
  css = css.split('/*').filter(b => /^\s*latin \*\//.test(b)).map(b => '/*' + b).join('');
  for (const u of [...new Set(css.match(/https:\/\/[^)]+/g) || [])]) { const name = `g${n++}.woff2`; fs.writeFileSync('fonts/' + name, Buffer.from(await (await fetch(u)).arrayBuffer())); css = css.split(u).join(name); }
  out += css;
}
fs.writeFileSync('fonts/fonts.css', out); console.log('fonts', n);
