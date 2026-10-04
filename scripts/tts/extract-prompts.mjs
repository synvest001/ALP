import fs from 'fs';
import path from 'path';
function promptHash(text) {
  const s = text.trim();
  let h = 0x811c9dc5;
  for (let i = 0; i < s.length; i++) {
    h ^= s.charCodeAt(i);
    h = (h + ((h << 1) + (h << 4) + (h << 7) + (h << 8) + (h << 24))) >>> 0;
  }
  return ('00000000' + h.toString(16)).slice(-8);
}
const dir = path.resolve('frontend/public/data/question_bank');
const out = {};
for (const f of fs.readdirSync(dir)) {
  if (!/^items_.*\.json$/.test(f)) continue;
  const d = JSON.parse(fs.readFileSync(path.join(dir, f), 'utf8'));
  const items = Array.isArray(d) ? d : (d.items || Object.values(d));
  for (const it of items) {
    const t = it && it.prompt_structure && it.prompt_structure.display_text;
    if (!t || !t.trim()) continue;
    const text = t.trim();
    const h = promptHash(text);
    if (out[h] && out[h] !== text) { console.error('HASH COLLISION', h); process.exit(1); }
    out[h] = text;
  }
}
fs.mkdirSync('scripts/tts', { recursive: true });
fs.writeFileSync('scripts/tts/prompts.json', JSON.stringify(out, null, 1));
console.log('prompts:', Object.keys(out).length, 'chars:', Object.values(out).reduce((a, t) => a + t.length, 0));
