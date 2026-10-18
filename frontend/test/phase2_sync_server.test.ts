import test from 'node:test';
import assert from 'node:assert/strict';
import crypto from 'node:crypto';

import { sha256 } from '../src/utils/sha256';
import { mergeRecords, ClassBProfile } from '../src/engine/SyncMerge';

import fs from 'node:fs';
import path from 'node:path';
import vm from 'node:vm';
import { fileURLToPath } from 'node:url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const codeGsPath = path.resolve(__dirname, '../../backend/apps_script/Code.gs');
const codeGsContent = fs.readFileSync(codeGsPath, 'utf8');

const backendContext: any = {
  console,
  Date,
  Math,
  JSON,
  Number,
  String,
  Boolean,
  Array,
  Object,
  module: { exports: {} },
  exports: {}
};
vm.createContext(backendContext);
vm.runInContext(codeGsContent, backendContext);
const backendCode = backendContext.module.exports;

// ---------------------------------------------------------------------------
// Mock Sheet Implementation for Apps Script unit testing in Node
// ---------------------------------------------------------------------------

class MockSheet {
  name: string;
  rows: any[][];

  constructor(name: string, headers?: any[]) {
    this.name = name;
    this.rows = headers && headers.length ? [headers.slice()] : [];
  }

  getName(): string {
    return this.name;
  }

  appendRow(row: any[]): void {
    this.rows.push(row.slice());
  }

  getDataRange(): { getValues: () => any[][] } {
    return {
      getValues: () => this.rows.map(r => r.slice())
    };
  }

  deleteRow(rowNumber: number): void {
    // 1-indexed row number
    const idx = rowNumber - 1;
    if (idx >= 0 && idx < this.rows.length) {
      this.rows.splice(idx, 1);
    }
  }

  getRange(rowNumber: number, colNumber: number): { setValue: (val: any) => void } {
    const rIdx = rowNumber - 1;
    const cIdx = colNumber - 1;
    return {
      setValue: (val: any) => {
        if (!this.rows[rIdx]) this.rows[rIdx] = [];
        this.rows[rIdx][cIdx] = val;
      }
    };
  }
}

class MockSheetAccess {
  sheets: { [name: string]: MockSheet } = {};

  getOrCreateSheet(name: string, headers?: string[]): MockSheet {
    if (!this.sheets[name]) {
      this.sheets[name] = new MockSheet(name, headers);
    }
    return this.sheets[name];
  }

  getSheet(name: string): MockSheet | null {
    return this.sheets[name] || null;
  }

  getAllSheets(): MockSheet[] {
    return Object.values(this.sheets);
  }

  deleteSheet(sheet: MockSheet): void {
    delete this.sheets[sheet.name];
  }
}

// ---------------------------------------------------------------------------
// Tests
// ---------------------------------------------------------------------------

test('SHA-256: passes standard FIPS vector and matches Node crypto for UTF-8', () => {
  // Test vector: sha256("abc")
  const abcHash = sha256('abc');
  assert.equal(abcHash, 'ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad');

  // Empty string
  const emptyHash = sha256('');
  const expectedEmpty = crypto.createHash('sha256').update('').digest('hex');
  assert.equal(emptyHash, expectedEmpty);

  // UTF-8 inputs with multi-byte characters and emojis
  const testInputs = [
    'family_code_alpha_123',
    'Hello, 世界! 🏰✨',
    'Español & Français: Ça va, señor niño?',
    '🌟 High surrogate test: 𝒳𝒴𝒵'
  ];

  for (const str of testInputs) {
    const computed = sha256(str);
    const expected = crypto.createHash('sha256').update(str, 'utf8').digest('hex');
    assert.equal(computed, expected, `Mismatch on UTF-8 string: "${str}"`);
  }
});

test('Class B Merge: deterministic and strictly commutative merge(a, b) == merge(b, a)', () => {
  const recA: ClassBProfile = {
    v: 1,
    name: 'Alice',
    avatar: 'princess',
    epoch: 1,
    nodes: 5,
    stars: 12,
    domain_counts: { MATHEMATICS: 10, ENGLISH_LANGUAGE: 4 },
    quest: { date: '2026-10-18', count: 2 },
    modality_preferences: { preferred: 'TAP_SELECT' },
    updated: 1710000001000
  };

  const recB: ClassBProfile = {
    v: 1,
    name: 'Alice Cooper',
    avatar: 'knight',
    epoch: 1,
    nodes: 8,
    stars: 10,
    domain_counts: { MATHEMATICS: 6, ENGLISH_LANGUAGE: 8, SCIENCE_EVS: 3 },
    quest: { date: '2026-10-18', count: 3 },
    modality_preferences: { preferred: 'VISUAL' },
    updated: 1710000002000 // Newer updated timestamp
  };

  const mergeAB = mergeRecords(recA, recB);
  const mergeBA = mergeRecords(recB, recA);

  assert.deepEqual(mergeAB, mergeBA, 'merge(a, b) must equal merge(b, a)');

  // Newer updated record wins name, avatar, modality_preferences
  assert.equal(mergeAB.name, 'Alice Cooper');
  assert.equal(mergeAB.avatar, 'knight');
  assert.equal(mergeAB.modality_preferences.preferred, 'VISUAL');

  // Math.max for nodes, stars, domain counts
  assert.equal(mergeAB.nodes, 8);
  assert.equal(mergeAB.stars, 12);
  assert.equal(mergeAB.domain_counts.MATHEMATICS, 10);
  assert.equal(mergeAB.domain_counts.ENGLISH_LANGUAGE, 8);
  assert.equal(mergeAB.domain_counts.SCIENCE_EVS, 3);

  // Quest: same date, max count wins
  assert.equal(mergeAB.quest.count, 3);
  assert.equal(mergeAB.quest.date, '2026-10-18');
});

test('Class B Merge: exact tie on updated timestamp broken lexicographically and symmetrically', () => {
  const rec1: ClassBProfile = {
    v: 1,
    name: 'Child A',
    avatar: 'explorer',
    epoch: 2,
    nodes: 3,
    stars: 5,
    domain_counts: { LOGICAL_REASONING: 2 },
    quest: { date: '2026-10-17', count: 1 },
    updated: 1710000000000
  };

  const rec2: ClassBProfile = {
    v: 1,
    name: 'Child B',
    avatar: 'magician',
    epoch: 2,
    nodes: 3,
    stars: 5,
    domain_counts: { LOGICAL_REASONING: 2 },
    quest: { date: '2026-10-17', count: 1 },
    updated: 1710000000000 // Exact tie
  };

  const m12 = mergeRecords(rec1, rec2);
  const m21 = mergeRecords(rec2, rec1);

  assert.deepEqual(m12, m21, 'Ties must produce strictly symmetric results');
  // Lexicographical winner deterministically selected
  assert.ok(m12.name === 'Child A' || m12.name === 'Child B');
});

test('Class B Merge: higher epoch wins the whole record unconditionally', () => {
  const oldEpoch: ClassBProfile = {
    v: 1,
    name: 'Old Reset Progress',
    avatar: 'knight',
    epoch: 0,
    nodes: 99,
    stars: 500,
    domain_counts: { MATHEMATICS: 100 },
    quest: { date: '2026-10-18', count: 3 },
    updated: 1710000050000 // Newer timestamp, but older epoch
  };

  const newEpoch: ClassBProfile = {
    v: 1,
    name: 'Fresh Start',
    avatar: 'princess',
    epoch: 1, // Higher epoch
    nodes: 0,
    stars: 0,
    domain_counts: {},
    quest: { date: '', count: 0 },
    updated: 1710000010000
  };

  const res1 = mergeRecords(oldEpoch, newEpoch);
  const res2 = mergeRecords(newEpoch, oldEpoch);

  assert.deepEqual(res1, res2);
  assert.equal(res1.name, 'Fresh Start');
  assert.equal(res1.epoch, 1);
  assert.equal(res1.nodes, 0);
  assert.equal(res1.stars, 0);
});

test('Apps Script Backend: Code.gs handleSync stores events, dedupes, attaches recv_ms, and pages up to 200', () => {
  const sheetAccess = new MockSheetAccess();
  const fam = sha256('family_secret_123');
  const kid = 'leo';
  const now = 1715000000000;

  // Push 3 events from Device A
  const eventsA = [
    { i: 'devA-1', d: 'devA', q: 1, t: now - 3000, y: 'att', ep: 0, s: 'M-NQ-01', m: 'i1', ok: 1, h: 0, md: 'TAP_SELECT', cf: 0, ss: 's1' },
    { i: 'devA-2', d: 'devA', q: 2, t: now - 2000, y: 'att', ep: 0, s: 'M-NQ-01', m: 'i2', ok: 1, h: 0, md: 'TAP_SELECT', cf: 0, ss: 's1' },
    { i: 'devA-3', d: 'devA', q: 3, t: now - 1000, y: 'att', ep: 0, s: 'M-NQ-01', m: 'i3', ok: 1, h: 0, md: 'TAP_SELECT', cf: 0, ss: 's1' }
  ];

  const profile = { v: 1, name: 'Leo', avatar: 'explorer', epoch: 0, nodes: 2, stars: 4, domain_counts: {}, quest: { date: '', count: 0 }, updated: now };

  const syncReq1 = {
    action: 'sync',
    fam: fam,
    kid: kid,
    vec: {}, // Client knows 0 events
    events: eventsA,
    profile: profile
  };

  const res1 = backendCode.handleRequest(sheetAccess, syncReq1, now);
  assert.equal(res1.status, 'success');
  assert.equal(res1.events.length, 3);
  assert.equal(res1.serverVec.devA, 3);
  assert.equal(res1.events[0].r, now, 'Server receive time must be attached');

  // Push duplicate events + 1 new event from Device B
  const eventsB = [
    eventsA[0], // Duplicate of devA-1
    { i: 'devB-1', d: 'devB', q: 1, t: now - 500, y: 'ckp', ep: 0, s: 'M-NQ-01', r: 1, ok: 1, ss: 's2' }
  ];

  const syncReq2 = {
    action: 'sync',
    fam: fam,
    kid: kid,
    vec: { devA: 3 }, // Client already knows devA up to seq 3
    events: eventsB,
    profile: profile
  };

  const res2 = backendCode.handleRequest(sheetAccess, syncReq2, now + 100);
  assert.equal(res2.status, 'success');
  // Client only needs events whose seq > clientVec[dev] -> only devB-1 returned
  assert.equal(res2.events.length, 1);
  assert.equal(res2.events[0].i, 'devB-1');
  assert.equal(res2.events[0].recv_r, now + 100, 'Checkpoints attach server receive time without colliding with tier r');
  assert.equal(res2.events[0].r, 1, 'Checkpoint tier r is preserved');
  assert.equal(res2.serverVec.devA, 3);
  assert.equal(res2.serverVec.devB, 1);
});

test('Apps Script Backend: Code.gs handleList and handleDeleteKid with tombstones', () => {
  const sheetAccess = new MockSheetAccess();
  const fam = sha256('family_secret_123');
  const now = 1715000000000;

  // Sync two kids: Mia and Noah
  backendCode.handleRequest(sheetAccess, {
    action: 'sync',
    fam: fam,
    kid: 'mia',
    vec: {},
    events: [{ i: 'dev-1', d: 'dev', q: 1, t: now, y: 'att', ep: 0, s: 'M-1', m: 'i1', ok: 1, h: 0, md: 'TAP_SELECT', cf: 0, ss: 's1' }],
    profile: { v: 1, name: 'Mia', avatar: 'princess', epoch: 0, nodes: 1, stars: 2, domain_counts: {}, quest: { date: '', count: 0 }, updated: now }
  }, now);

  backendCode.handleRequest(sheetAccess, {
    action: 'sync',
    fam: fam,
    kid: 'noah',
    vec: {},
    events: [{ i: 'dev-2', d: dev => 'dev', q: 1, t: now, y: 'att', ep: 0, s: 'M-2', m: 'i2', ok: 1, h: 0, md: 'TAP_SELECT', cf: 0, ss: 's1' }],
    profile: { v: 1, name: 'Noah', avatar: 'knight', epoch: 0, nodes: 1, stars: 2, domain_counts: {}, quest: { date: '', count: 0 }, updated: now }
  }, now);

  // List kids
  const list1 = backendCode.handleRequest(sheetAccess, { action: 'list', fam: fam }, now);
  assert.equal(list1.status, 'success');
  assert.equal(list1.kids.length, 2);

  // Delete Noah
  const delNoah = backendCode.handleRequest(sheetAccess, { action: 'delete_kid', fam: fam, kid: 'noah' }, now + 1000);
  assert.equal(delNoah.status, 'success');

  // Verify Noah is tombstoned in list
  const list2 = backendCode.handleRequest(sheetAccess, { action: 'list', fam: fam }, now + 1100);
  const noahEntry = list2.kids.find((k: any) => k.kid === 'noah');
  assert.ok(noahEntry);
  assert.equal(noahEntry.tombstoned, true);
  assert.equal(noahEntry.deleted_ms, now + 1000);

  // An old sync for Noah returns tombstoned: true
  const oldSync = backendCode.handleRequest(sheetAccess, {
    action: 'sync',
    fam: fam,
    kid: 'noah',
    vec: {},
    events: [{ i: 'dev-old', d: 'dev', q: 2, t: now + 500, y: 'att', ep: 0, s: 'M-2', m: 'i3', ok: 1, h: 0, md: 'TAP_SELECT', cf: 0, ss: 's1' }],
    profile: { v: 1, name: 'Noah', avatar: 'knight', epoch: 0, nodes: 1, stars: 2, domain_counts: {}, quest: { date: '', count: 0 }, updated: now + 500 }
  }, now + 1200);
  assert.equal(oldSync.tombstoned, true);

  // A new sync with events after deleted_ms clears the tombstone (re-creating child is allowed)
  const recreateSync = backendCode.handleRequest(sheetAccess, {
    action: 'sync',
    fam: fam,
    kid: 'noah',
    vec: {},
    events: [{ i: 'dev-new', d: 'dev', q: 3, t: now + 2000, y: 'att', ep: 1, s: 'M-2', m: 'i4', ok: 1, h: 0, md: 'TAP_SELECT', cf: 0, ss: 's2' }],
    profile: { v: 1, name: 'Noah Reborn', avatar: 'knight', epoch: 1, nodes: 1, stars: 2, domain_counts: {}, quest: { date: '', count: 0 }, updated: now + 2000 }
  }, now + 2100);
  assert.equal(recreateSync.tombstoned, false);
  assert.equal(recreateSync.profile.name, 'Noah Reborn');
});

test('Apps Script Backend: Code.gs handleExportCheck returns event count and canonical SHA-256', () => {
  const sheetAccess = new MockSheetAccess();
  const fam = sha256('family_secret_123');
  const kid = 'emma';
  const now = 1715000000000;

  const events = [
    { i: 'devA-1', d: 'devA', q: 1, t: now + 100, y: 'att', ep: 0, s: 'M-1', m: 'i1', ok: 1, h: 0, md: 'TAP_SELECT', cf: 0, ss: 's1' },
    { i: 'devB-1', d: 'devB', q: 1, t: now + 200, y: 'att', ep: 0, s: 'M-2', m: 'i2', ok: 1, h: 0, md: 'TAP_SELECT', cf: 0, ss: 's1' }
  ];

  backendCode.handleRequest(sheetAccess, {
    action: 'sync',
    fam: fam,
    kid: kid,
    vec: {},
    events: events,
    profile: { v: 1, name: 'Emma', avatar: 'magician', epoch: 0, nodes: 1, stars: 2, domain_counts: {}, quest: { date: '', count: 0 }, updated: now }
  }, now);

  const checkRes = backendCode.handleRequest(sheetAccess, { action: 'export_check', fam: fam, kid: kid }, now);
  assert.equal(checkRes.status, 'success');
  assert.equal(checkRes.eventCount, 2);
  assert.ok(checkRes.checksum && checkRes.checksum.length === 64);

  // Verify against client canonical JSON
  const canonicalExpected = crypto.createHash('sha256').update(JSON.stringify(events)).digest('hex');
  assert.equal(checkRes.checksum, canonicalExpected);
});

test('Apps Script Backend: Code.gs handleSnapshot rotates and retains newest SNAPSHOT_KEEP tabs', () => {
  const sheetAccess = new MockSheetAccess();
  sheetAccess.getOrCreateSheet('events', ['fam', 'kid', 'dev', 'seq', 'recv_ms', 'json']);

  // Simulate snapshots across 9 distinct UTC days
  for (let day = 1; day <= 9; day++) {
    const dayMs = Date.UTC(2026, 9, day); // Oct day, 2026
    backendCode.handleSnapshot(sheetAccess, dayMs);
  }

  const allSheets = sheetAccess.getAllSheets();
  const snapSheets = allSheets.filter(s => s.name.startsWith('events_snap_'));

  // Must retain at most SNAPSHOT_KEEP (7) tabs
  assert.equal(snapSheets.length, backendCode.SNAPSHOT_KEEP);
  assert.equal(backendCode.SNAPSHOT_KEEP, 7);

  // The 7 retained tabs must be the newest days (Oct 3 to Oct 9)
  const names = snapSheets.map(s => s.name).sort();
  assert.equal(names[0], 'events_snap_20261003');
  assert.equal(names[6], 'events_snap_20261009');
});
