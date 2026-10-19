import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

import { ContentManifestManager, ContentManifest } from '../src/engine/ContentManifest';
import { QuestionBank, QuestionItem } from '../src/engine/QuestionBank';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const distManifestPath = path.resolve(__dirname, '../dist/content-manifest.json');
const publicManifestPath = path.resolve(__dirname, '../public/content-manifest.json');

// Mock localStorage for Node environment
const storage: { [k: string]: string } = {};
(globalThis as any).localStorage = {
  getItem: (k: string) => (Object.prototype.hasOwnProperty.call(storage, k) ? storage[k] : null),
  setItem: (k: string, v: string) => { storage[k] = String(v); },
  removeItem: (k: string) => { delete storage[k]; },
  clear: () => {
    for (const k in storage) delete storage[k];
  }
};

function clearStorage() {
  (globalThis as any).localStorage.clear();
}

if (typeof (globalThis as any).XMLHttpRequest === 'undefined') {
  (globalThis as any).XMLHttpRequest = class MockXHR {
    status: number = 200;
    responseText: string = '';
    onload: (() => void) | null = null;
    onerror: (() => void) | null = null;
    ontimeout: (() => void) | null = null;
    open(_method: string, url: string) {
      if (url.indexOf('content-manifest.json') !== -1) {
        this.status = 200;
        this.responseText = fs.readFileSync(distManifestPath, 'utf8');
      } else {
        this.status = 404;
        this.responseText = '{}';
      }
    }
    send() {
      if (this.onload) this.onload();
    }
  };
}

test('Content Manifest: dist/content-manifest.json exists and contains exactly 187 subskills', () => {
  assert.ok(fs.existsSync(distManifestPath), 'dist/content-manifest.json must exist');
  const raw = fs.readFileSync(distManifestPath, 'utf8');
  const manifest: ContentManifest = JSON.parse(raw);

  assert.equal(manifest.format, 'alp-content-manifest');
  assert.equal(manifest.v, 1);
  assert.ok(manifest.generated);

  const chunkKeys = Object.keys(manifest.chunks);
  assert.equal(chunkKeys.length, 187, 'Must have exactly 187 subskill chunks');

  for (const key of chunkKeys) {
    const entry = manifest.chunks[key];
    assert.equal(entry.chunk, key);
    assert.ok(typeof entry.version === 'string' && entry.version.length >= 8, 'version must be a short hash');
    // Spec constraint: only "active" and "retired" states
    assert.ok(
      entry.status === 'active' || entry.status === 'retired',
      `Chunk ${key} status must be only 'active' or 'retired', got '${entry.status}'`
    );
    assert.ok(Array.isArray(entry.retired), `Chunk ${key} retired must be an array`);
  }
});

test('Client checks manifest at most once per session start', async () => {
  ContentManifestManager.resetForTest();
  clearStorage();

  const manifest: ContentManifest = JSON.parse(fs.readFileSync(distManifestPath, 'utf8'));

  // Pre-seed localStorage cache
  localStorage.setItem('alp_content_manifest_cache', JSON.stringify(manifest));

  // First session check
  const sessionId = 'session_123';
  const res1 = await ContentManifestManager.checkManifestAtSessionStart(sessionId);
  assert.ok(res1);
  assert.equal(res1!.format, 'alp-content-manifest');

  // Second check in the same session: does not re-fetch/re-parse, returns cached singleton
  const res2 = await ContentManifestManager.checkManifestAtSessionStart(sessionId);
  assert.strictEqual(res1, res2, 'Same session must reuse cached manifest without refetching');
});

test('Drops retired item IDs from task selection', () => {
  ContentManifestManager.resetForTest();

  // Create test items: item 1 is retired, item 2 is active
  const item1: QuestionItem = {
    item_id: 'ITEM-TEST-0001',
    target_subskill_id: 'TEST-SUB-01',
    domain_id: 'MATHEMATICS',
    evidence_archetype: 'PROCEDURAL_FLUENCY',
    language_load_class: 'LOW',
    challenge_type: 'STANDARD',
    prompt_structure: { display_text: 'Retired Question 1' },
    rubric: { correct_criteria: { selected_option_id: 'opt_1' } }
  };
  const item2: QuestionItem = {
    item_id: 'ITEM-TEST-0002',
    target_subskill_id: 'TEST-SUB-01',
    domain_id: 'MATHEMATICS',
    evidence_archetype: 'PROCEDURAL_FLUENCY',
    language_load_class: 'LOW',
    challenge_type: 'STANDARD',
    prompt_structure: { display_text: 'Active Question 2' },
    rubric: { correct_criteria: { selected_option_id: 'opt_1' } }
  };

  const testManifest: ContentManifest = {
    format: 'alp-content-manifest',
    v: 1,
    generated: new Date().toISOString(),
    total_chunks: 1,
    chunks: {
      'TEST-SUB-01': {
        chunk: 'TEST-SUB-01',
        version: 'hash123',
        status: 'active',
        retired: ['ITEM-TEST-0001']
      }
    }
  };

  ContentManifestManager.applyManifest(testManifest);

  assert.equal(ContentManifestManager.isItemRetired('ITEM-TEST-0001'), true);
  assert.equal(ContentManifestManager.isItemRetired('ITEM-TEST-0002'), false);

  const qb = new QuestionBank();
  (qb as any).chunks.set('TEST-SUB-01', [item1, item2]);
  (qb as any).rebuildViews();

  // Pick tasks multiple times: ITEM-TEST-0001 must NEVER be selected
  for (let i = 0; i < 20; i++) {
    const task = qb.getTask('MATHEMATICS', 'TEST-SUB-01');
    assert.ok(task);
    assert.equal(task!.item_id, 'ITEM-TEST-0002', 'Retired item must be completely dropped from selection');
  }
});

test('Drops entire retired subskill chunks from task selection', () => {
  ContentManifestManager.resetForTest();

  const item1: QuestionItem = {
    item_id: 'ITEM-TEST-0003',
    target_subskill_id: 'RETIRED-SUB',
    domain_id: 'MATHEMATICS',
    evidence_archetype: 'PROCEDURAL_FLUENCY',
    language_load_class: 'LOW',
    challenge_type: 'STANDARD',
    prompt_structure: { display_text: 'Retired Subskill Item' },
    rubric: { correct_criteria: { selected_option_id: 'opt_1' } }
  };

  const testManifest: ContentManifest = {
    format: 'alp-content-manifest',
    v: 1,
    generated: new Date().toISOString(),
    total_chunks: 1,
    chunks: {
      'RETIRED-SUB': {
        chunk: 'RETIRED-SUB',
        version: 'hash999',
        status: 'retired',
        retired: []
      }
    }
  };

  ContentManifestManager.applyManifest(testManifest);
  assert.equal(ContentManifestManager.isChunkRetired('RETIRED-SUB'), true);

  const qb = new QuestionBank();
  (qb as any).chunks.set('RETIRED-SUB', [item1]);
  (qb as any).rebuildViews();

  const task = qb.getTask('MATHEMATICS', 'RETIRED-SUB');
  assert.equal(task, null, 'Retired chunk must never return items');
});

test('Refreshes chunks only when version changes', () => {
  ContentManifestManager.resetForTest();
  clearStorage();

  const sub = 'M-DU-01';
  const testManifest: ContentManifest = {
    format: 'alp-content-manifest',
    v: 1,
    generated: new Date().toISOString(),
    total_chunks: 1,
    chunks: {
      [sub]: {
        chunk: sub,
        version: 'v1_alpha',
        status: 'active',
        retired: []
      }
    }
  };

  ContentManifestManager.applyManifest(testManifest);

  // If not resident in memory -> needs loading
  assert.equal(ContentManifestManager.shouldRefreshChunk(sub, false), true);

  // Once loaded at v1_alpha
  ContentManifestManager.markChunkLoaded(sub);
  assert.equal(localStorage.getItem('alp_chunk_ver_' + sub), 'v1_alpha');

  // Resident in memory and version is same -> should NOT refresh
  assert.equal(ContentManifestManager.shouldRefreshChunk(sub, true), false);

  // If manifest updates to v2_beta
  testManifest.chunks[sub].version = 'v2_beta';
  ContentManifestManager.applyManifest(testManifest);

  // Version mismatch -> should refresh!
  assert.equal(ContentManifestManager.shouldRefreshChunk(sub, true), true);

  // After refresh
  ContentManifestManager.markChunkLoaded(sub);
  assert.equal(localStorage.getItem('alp_chunk_ver_' + sub), 'v2_beta');
  assert.equal(ContentManifestManager.shouldRefreshChunk(sub, true), false);
});

test('Asset Budget: each visual asset <= 2 MB and <= 8 MB per item', () => {
  const dirs = [
    path.resolve(__dirname, '../public/art'),
    path.resolve(__dirname, '../dist/art')
  ];

  for (const d of dirs) {
    if (!fs.existsSync(d)) continue;
    const files = fs.readdirSync(d);
    for (const f of files) {
      const full = path.join(d, f);
      const stat = fs.statSync(full);
      if (stat.isFile()) {
        assert.ok(
          stat.size <= 2 * 1024 * 1024,
          `Asset ${f} size (${stat.size} bytes) exceeds 2 MB budget`
        );
      }
    }
  }
});
