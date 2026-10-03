// Post-build step: split the big per-domain bundles in dist/ into one small file per
// subskill, plus a tiny index. Old iPads cannot hold ~20 MB of parsed JSON, so the app
// loads only the subskill chunks a session needs.
// Source of truth stays public/data/question_bank/items_<DOMAIN>.json (unchanged).
import fs from 'node:fs';
import path from 'node:path';

const SRC = path.resolve('public/data/question_bank');
const OUT = path.resolve('dist/data/question_bank');
const CHUNKS = path.join(OUT, 'chunks');
const DOMAINS = ['MATHEMATICS', 'ENGLISH_LANGUAGE', 'SCIENCE_EVS', 'LOGICAL_REASONING', 'WORLD_KNOWLEDGE'];

fs.rmSync(CHUNKS, { recursive: true, force: true });
fs.mkdirSync(CHUNKS, { recursive: true });

const index = {};
let total = 0;
for (const dom of DOMAINS) {
  const items = JSON.parse(fs.readFileSync(path.join(SRC, `items_${dom}.json`), 'utf8'));
  const bySub = new Map();
  for (const it of items) {
    if (!bySub.has(it.target_subskill_id)) bySub.set(it.target_subskill_id, []);
    bySub.get(it.target_subskill_id).push(it);
  }
  for (const [sub, list] of bySub) {
    fs.writeFileSync(path.join(CHUNKS, `${sub}.json`), JSON.stringify(list));
    index[sub] = { domain: dom, count: list.length };
    total += list.length;
  }
}
fs.writeFileSync(path.join(CHUNKS, 'index.json'), JSON.stringify({ total_items: total, subskills: index }));

for (const dom of DOMAINS) fs.rmSync(path.join(OUT, `items_${dom}.json`), { force: true });
fs.rmSync(path.join(OUT, 'manifest.json'), { force: true });

console.log(`[split-question-bank] ${Object.keys(index).length} subskill chunks, ${total} items`);
