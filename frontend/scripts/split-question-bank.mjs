// Post-build step: split the big per-domain bundles in dist/ into one small file per
// subskill, plus a tiny index. Old iPads cannot hold ~20 MB of parsed JSON, so the app
// loads only the subskill chunks a session needs.
// Source of truth stays public/data/question_bank/items_<DOMAIN>.json (unchanged).
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';

const SRC = path.resolve('public/data/question_bank');
const OUT = path.resolve('dist/data/question_bank');
const CHUNKS = path.join(OUT, 'chunks');
const DOMAINS = ['MATHEMATICS', 'ENGLISH_LANGUAGE', 'SCIENCE_EVS', 'LOGICAL_REASONING', 'WORLD_KNOWLEDGE'];

fs.rmSync(CHUNKS, { recursive: true, force: true });
fs.mkdirSync(CHUNKS, { recursive: true });

const index = {};
const manifestChunks = {};
let total = 0;

for (const dom of DOMAINS) {
  const items = JSON.parse(fs.readFileSync(path.join(SRC, `items_${dom}.json`), 'utf8'));
  const bySub = new Map();
  for (const it of items) {
    if (!bySub.has(it.target_subskill_id)) bySub.set(it.target_subskill_id, []);
    bySub.get(it.target_subskill_id).push(it);
  }
  for (const [sub, list] of bySub) {
    const chunkJson = JSON.stringify(list);
    fs.writeFileSync(path.join(CHUNKS, `${sub}.json`), chunkJson);
    index[sub] = { domain: dom, count: list.length };
    total += list.length;

    // Short hash of chunk content
    const version = crypto.createHash('sha256').update(chunkJson).digest('hex').slice(0, 12);

    // Identify retired items in chunk (only "active" and "retired" states)
    const retired = [];
    for (const it of list) {
      if (it.status === 'retired' || it.retired === true) {
        retired.push(it.item_id);
      }
    }
    const chunkStatus = (retired.length === list.length && list.length > 0) ? 'retired' : 'active';

    manifestChunks[sub] = {
      chunk: sub,
      version: version,
      status: chunkStatus,
      retired: retired
    };
  }
}

fs.writeFileSync(path.join(CHUNKS, 'index.json'), JSON.stringify({ total_items: total, subskills: index }));

for (const dom of DOMAINS) fs.rmSync(path.join(OUT, `items_${dom}.json`), { force: true });
fs.rmSync(path.join(OUT, 'manifest.json'), { force: true });

// Minimal content-manifest.json with per-chunk version and retired item ids; only "active" and "retired" states
const contentManifest = {
  format: 'alp-content-manifest',
  v: 1,
  generated: new Date().toISOString(),
  total_chunks: Object.keys(manifestChunks).length,
  chunks: manifestChunks
};

const distManifestPath = path.resolve('dist/content-manifest.json');
fs.writeFileSync(distManifestPath, JSON.stringify(contentManifest, null, 2));

const publicManifestPath = path.resolve('public/content-manifest.json');
fs.writeFileSync(publicManifestPath, JSON.stringify(contentManifest, null, 2));

console.log(`[split-question-bank] ${Object.keys(index).length} subskill chunks, ${total} items`);
console.log(`[content-manifest] written to ${distManifestPath}`);
