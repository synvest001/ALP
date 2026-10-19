import test from 'node:test';
import assert from 'node:assert/strict';
import crypto from 'node:crypto';
import fs from 'node:fs';
import path from 'node:path';
import vm from 'node:vm';
import { fileURLToPath } from 'node:url';

import { sha256 } from '../src/utils/sha256';
import { ALPEvent, ALPAttEvent } from '../src/engine/EventTypes';
import { EventLog } from '../src/engine/EventLog';
import { SyncEngine } from '../src/engine/SyncEngine';
import { replay } from '../src/engine/AssessmentEngine';
import {
  computeBackupChecksum,
  buildBackupPayload,
  validateBackupPayload,
  restoreBackup,
  exportBackup,
  encryptPayload,
  decryptPayload,
  BackupPayload
} from '../src/engine/BackupRestore';

// ---------------------------------------------------------------------------
// Load Code.gs for backend daily snapshot test
// ---------------------------------------------------------------------------
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
}

class MockSpreadsheet {
  sheets: { [name: string]: MockSheet } = {};

  getOrCreateSheet(name: string, headers?: any[]): MockSheet {
    if (!this.sheets[name]) {
      this.sheets[name] = new MockSheet(name, headers);
    }
    return this.sheets[name];
  }

  getSheet(name: string): MockSheet | null {
    return this.sheets[name] || null;
  }

  getAllSheets(): MockSheet[] {
    const list: MockSheet[] = [];
    for (const k in this.sheets) {
      list.push(this.sheets[k]);
    }
    return list;
  }

  deleteSheet(sheet: MockSheet): void {
    delete this.sheets[sheet.name];
  }
}

// ---------------------------------------------------------------------------
// Mock localStorage for Node tests
// ---------------------------------------------------------------------------
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

// Ensure Web Crypto exists in Node test environment
if (!(globalThis as any).crypto || !(globalThis as any).crypto.subtle) {
  (globalThis as any).crypto = (crypto as any).webcrypto;
}

// ---------------------------------------------------------------------------
// Tests
// ---------------------------------------------------------------------------

test('Amendment 1: runDailySnapshot in Code.gs runs successfully and creates dated snapshot tab', () => {
  const ss = new MockSpreadsheet();
  const eventsSheet = ss.getOrCreateSheet('events', ['fam', 'kid', 'dev', 'seq', 'recv_ms', 'json']);
  eventsSheet.appendRow(['fam1', 'kid1', 'devA', 1, 1000, '{"i":"1"}']);
  eventsSheet.appendRow(['fam1', 'kid1', 'devA', 2, 2000, '{"i":"2"}']);

  const fixedDate = 1776528000000; // 2026-04-18T16:00:00Z
  const res = backendCode.handleSnapshot(ss, fixedDate);
  assert.equal(res.status, 'success');
  assert.equal(res.snapshot, 'events_snap_20260418');

  const snap = ss.getSheet('events_snap_20260418');
  assert.ok(snap, 'Snapshot sheet was created');
  assert.equal(snap!.rows.length, 3, 'Contains header + 2 event rows');
});

test('Amendment 1: runDailySnapshot in Code.gs rotates snapshots and keeps newest SNAPSHOT_KEEP (7)', () => {
  const ss = new MockSpreadsheet();
  ss.getOrCreateSheet('events', ['fam', 'kid', 'dev', 'seq', 'recv_ms', 'json']);

  // Pre-create 8 old snapshots
  for (let d = 1; d <= 8; d++) {
    const dayStr = d < 10 ? '0' + d : String(d);
    ss.getOrCreateSheet('events_snap_202604' + dayStr, []);
  }
  assert.equal(ss.getAllSheets().length, 9); // events + 8 snapshots

  // Create 9th snapshot
  const nowMs = Date.UTC(2026, 3, 20); // 2026-04-20
  backendCode.handleSnapshot(ss, nowMs);

  const allSnapshots = ss.getAllSheets().filter(s => s.name.startsWith('events_snap_'));
  assert.equal(allSnapshots.length, 7, 'Rotated to retain exactly 7 newest snapshots');
  // Oldest snapshots (01, 02) should have been pruned
  assert.equal(ss.getSheet('events_snap_20260401'), null);
  assert.equal(ss.getSheet('events_snap_20260402'), null);
  assert.ok(ss.getSheet('events_snap_20260420'));
});

test('Checksum calculation: matches canonical sort by (d, q) and matches backend export_check', () => {
  const events: ALPEvent[] = [
    { i: 'devB-2', d: 'devB', q: 2, t: 300, y: 'att', ep: 0, s: 'skill1', ok: 1 },
    { i: 'devA-1', d: 'devA', q: 1, t: 100, y: 'att', ep: 0, s: 'skill1', ok: 1 },
    { i: 'devB-1', d: 'devB', q: 1, t: 200, y: 'att', ep: 0, s: 'skill1', ok: 1 },
    { i: 'devA-2', d: 'devA', q: 2, t: 400, y: 'att', ep: 0, s: 'skill1', ok: 1 }
  ];

  const clientChecksum = computeBackupChecksum(events);

  // Compare against backend handleExportCheck logic
  const ss = new MockSpreadsheet();
  const eventsSheet = ss.getOrCreateSheet('events', ['fam', 'kid', 'dev', 'seq', 'recv_ms', 'json']);
  for (let i = 0; i < events.length; i++) {
    eventsSheet.appendRow(['fam1', 'kid1', events[i].d, events[i].q, events[i].t, JSON.stringify(events[i])]);
  }

  const backendCheck = backendCode.handleExportCheck(ss, { kid: 'kid1' }, 'fam1');
  assert.equal(backendCheck.status, 'success');
  assert.equal(backendCheck.eventCount, 4);
  assert.equal(clientChecksum, backendCheck.checksum, 'Client and server checksums must match exactly');
});

test('Backup export: produces valid unencrypted payload and notice when no passphrase given', async () => {
  clearStorage();
  const kid = 'player_one';
  EventLog.appendEvent(kid, {
    i: 'devA-1', d: 'devA', q: 1, t: 1000, y: 'att', ep: 0, s: 'math_add_1', ok: 1
  });
  localStorage.setItem('alp_player_one_nodes_completed', '3');
  localStorage.setItem('alp_player_one_stars', '7');

  const result = await exportBackup(kid);
  assert.equal(result.encrypted, false);
  assert.equal(result.notice, 'This file is not password-protected.');

  const payload = result.payload as BackupPayload;
  assert.equal(payload.format, 'alp-backup');
  assert.equal(payload.v, 1);
  assert.equal(payload.kid, 'player_one');
  assert.equal(payload.eventCount, 1);
  assert.equal(payload.profile.nodes, 3);
  assert.equal(payload.profile.stars, 7);

  const val = validateBackupPayload(payload);
  assert.equal(val.valid, true);
});

test('Damaged backup rejection: tampered event contents or corrupted checksum rejected', () => {
  clearStorage();
  const events: ALPEvent[] = [
    { i: 'devA-1', d: 'devA', q: 1, t: 1000, y: 'att', ep: 0, s: 'math_add_1', ok: 1 }
  ];
  const payload: BackupPayload = {
    format: 'alp-backup',
    v: 1,
    kid: 'test_kid',
    exportedUtc: new Date().toISOString(),
    eventCount: 1,
    checksum: computeBackupChecksum(events),
    profile: {
      v: 1, name: 'test_kid', avatar: 'knight', epoch: 0, nodes: 1, stars: 1, domain_counts: {}, quest: { date: '', count: 0 }, updated: 1000
    },
    events: events
  };

  // Valid original
  assert.equal(validateBackupPayload(payload).valid, true);

  // Tamper with event ok flag (e.g. from 1 to 0)
  const tampered = JSON.parse(JSON.stringify(payload));
  tampered.events[0].ok = 0;
  const resTampered = validateBackupPayload(tampered);
  assert.equal(resTampered.valid, false);
  assert.equal(resTampered.message, 'This backup file looks damaged. Nothing was changed.');

  // Tamper with format
  const badFormat = JSON.parse(JSON.stringify(payload));
  badFormat.format = 'wrong-format';
  assert.equal(validateBackupPayload(badFormat).valid, false);

  // Tamper with version
  const badV = JSON.parse(JSON.stringify(payload));
  badV.v = 2;
  assert.equal(validateBackupPayload(badV).valid, false);
});

test('Amendment 3: Restoring an older backup over newer progress loses nothing', () => {
  clearStorage();
  const kid = 'learner';
  const localNow = 5000;

  // 1. Initial play session (creates 1 attempt, 1 node)
  const ev1: ALPAttEvent = {
    i: 'devA-1', d: 'devA', q: 1, t: 1000, y: 'att', ep: 0, s: 'skill_a', ok: 1
  };
  EventLog.appendEvent(kid, ev1);
  localStorage.setItem('alp_learner_nodes_completed', '1');
  localStorage.setItem('alp_learner_stars', '2');
  localStorage.setItem('alp_learner_sync_updated', '1000');

  // Backup created at this initial point
  const olderBackup = buildBackupPayload(kid, 'Learner', 'magician');
  assert.equal(olderBackup.eventCount, 1);
  assert.equal(olderBackup.profile.nodes, 1);

  // 2. Child continues playing and achieves advanced progress
  const ev2: ALPAttEvent = {
    i: 'devA-2', d: 'devA', q: 2, t: 2000, y: 'att', ep: 0, s: 'skill_a', ok: 1 // consecutive=2 -> SECURE
  };
  const ev3: ALPAttEvent = {
    i: 'devA-3', d: 'devA', q: 3, t: 3000, y: 'att', ep: 0, s: 'skill_b', ok: 1
  };
  EventLog.appendEvent(kid, ev2);
  EventLog.appendEvent(kid, ev3);
  localStorage.setItem('alp_learner_nodes_completed', '3');
  localStorage.setItem('alp_learner_stars', '6');
  localStorage.setItem('alp_learner_sync_updated', '3000');

  // Replay live state to verify advanced progress
  const preRestoreStates = replay(EventLog.getEvents(kid), 0, localNow);
  assert.equal(preRestoreStates['skill_a'].state, 'SECURE');
  assert.equal(preRestoreStates['skill_b'].state, 'DEVELOPING');

  // 3. User restores the OLDER backup over the newer progress
  const restoreRes = restoreBackup(olderBackup, localNow, kid);
  assert.equal(restoreRes.success, true);
  assert.equal(restoreRes.message, 'Everything is saved.');

  // 4. Verify that NOTHING was lost:
  // Nodes completed must remain 3 (Math.max(3, 1))
  assert.equal(localStorage.getItem('alp_learner_nodes_completed'), '3');
  assert.equal(localStorage.getItem('alp_learner_stars'), '6');

  // All 3 events are still present in EventLog (ev1 from backup didn't duplicate or wipe ev2/ev3)
  const postEvents = EventLog.getEvents(kid);
  assert.equal(postEvents.length, 3);

  // Assessment states remain advanced
  const postStates = JSON.parse(localStorage.getItem('alp_learner_assessment_states') || '{}');
  assert.equal(postStates['skill_a'].state, 'SECURE');
  assert.equal(postStates['skill_b'].state, 'DEVELOPING');
});

test('Amendment 3: A backup from before a "Reset Progress" (older epoch) does not resurrect progress', () => {
  clearStorage();
  const kid = 'learner';
  const localNow = 10000;

  // 1. Child plays in Epoch 0 (skills A and B mastered)
  EventLog.appendEvent(kid, {
    i: 'devA-1', d: 'devA', q: 1, t: 1000, y: 'att', ep: 0, s: 'skill_a', ok: 1
  });
  EventLog.appendEvent(kid, {
    i: 'devA-2', d: 'devA', q: 2, t: 1500, y: 'att', ep: 0, s: 'skill_a', ok: 1
  });
  EventLog.appendEvent(kid, {
    i: 'devA-3', d: 'devA', q: 3, t: 2000, y: 'att', ep: 0, s: 'skill_b', ok: 1
  });
  localStorage.setItem('alp_learner_nodes_completed', '5');
  localStorage.setItem('alp_learner_stars', '10');
  localStorage.setItem('alp_learner_sync_epoch', '0');
  localStorage.setItem('alp_learner_sync_updated', '2000');

  // Backup taken in Epoch 0
  const preResetBackup = buildBackupPayload(kid, 'Learner', 'knight');
  assert.equal(preResetBackup.profile.epoch, 0);
  assert.equal(preResetBackup.eventCount, 3);

  // 2. Parent clicks "Reset Progress"
  // Epoch bumped to 1, local log cleared, nodes reset to 0
  SyncEngine.bumpEpoch(kid);
  assert.equal(localStorage.getItem('alp_learner_sync_epoch'), '1');
  EventLog.clearKidLog(kid);
  localStorage.setItem('alp_learner_nodes_completed', '0');
  localStorage.setItem('alp_learner_stars', '0');
  localStorage.setItem('alp_learner_assessment_states', '{}');

  // 3. Child plays 1 new skill in Epoch 1
  EventLog.appendEvent(kid, {
    i: 'devA-4', d: 'devA', q: 4, t: 5000, y: 'att', ep: 1, s: 'skill_c', ok: 1
  });
  localStorage.setItem('alp_learner_nodes_completed', '1');

  // 4. Restore the pre-reset (Epoch 0) backup
  const restoreRes = restoreBackup(preResetBackup, localNow, kid);
  assert.equal(restoreRes.success, true);

  // Current epoch must remain 1 (Epoch 1 wins over Epoch 0 in mergeRecords)
  assert.equal(localStorage.getItem('alp_learner_sync_epoch'), '1');

  // Replay should fence out all Epoch 0 events!
  const restoredStates = JSON.parse(localStorage.getItem('alp_learner_assessment_states') || '{}');

  // Pre-reset skills A and B MUST NOT be resurrected!
  assert.equal(restoredStates['skill_a'], undefined, 'Skill A from epoch 0 must NOT be resurrected');
  assert.equal(restoredStates['skill_b'], undefined, 'Skill B from epoch 0 must NOT be resurrected');

  // Post-reset skill C from epoch 1 MUST be preserved
  assert.ok(restoredStates['skill_c'], 'Skill C from epoch 1 is present');
  assert.equal(restoredStates['skill_c'].state, 'DEVELOPING');
});

test('Web Crypto encryption & decryption: payload protected with passphrase and recovers accurately', async () => {
  clearStorage();
  const kid = 'secure_kid';
  const events: ALPEvent[] = [
    { i: 'dev1-1', d: 'dev1', q: 1, t: 1000, y: 'att', ep: 0, s: 'math_sub', ok: 1 }
  ];
  const payload: BackupPayload = {
    format: 'alp-backup',
    v: 1,
    kid: kid,
    exportedUtc: new Date().toISOString(),
    eventCount: 1,
    checksum: computeBackupChecksum(events),
    profile: {
      v: 1, name: 'SecureKid', avatar: 'explorer', epoch: 0, nodes: 2, stars: 4, domain_counts: {}, quest: { date: '', count: 0 }, updated: 1000
    },
    events: events
  };

  const passphrase = 'SecretParentPassword123!';
  const encrypted = await encryptPayload(payload, passphrase);
  assert.equal(encrypted.format, 'alp-backup');
  assert.equal(encrypted.v, 1);
  assert.equal(encrypted.encrypted, true);
  assert.ok(encrypted.salt && encrypted.salt.length === 32);
  assert.ok(encrypted.iv && encrypted.iv.length === 24);
  assert.ok(encrypted.ciphertext && encrypted.ciphertext.length > 0);

  // Decrypt with correct passphrase
  const decrypted = await decryptPayload(encrypted, passphrase);
  assert.equal(decrypted.kid, 'secure_kid');
  assert.equal(decrypted.checksum, payload.checksum);
  assert.equal(decrypted.profile.nodes, 2);

  // Decrypt with wrong passphrase must fail
  await assert.rejects(
    async () => {
      await decryptPayload(encrypted, 'WrongPassword');
    },
    'Wrong passphrase should reject'
  );
});
