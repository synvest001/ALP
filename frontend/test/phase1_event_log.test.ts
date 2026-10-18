import test from 'node:test';
import assert from 'node:assert/strict';

// Mock localStorage for headless Node environment
const mockStorage: { [key: string]: string } = {};
globalThis.localStorage = {
  getItem(key: string): string | null {
    return Object.prototype.hasOwnProperty.call(mockStorage, key) ? mockStorage[key] : null;
  },
  setItem(key: string, value: string): void {
    mockStorage[key] = String(value);
  },
  removeItem(key: string): void {
    delete mockStorage[key];
  },
  clear(): void {
    for (const k in mockStorage) {
      delete mockStorage[k];
    }
  },
  key(index: number): string | null {
    return Object.keys(mockStorage)[index] || null;
  },
  get length(): number {
    return Object.keys(mockStorage).length;
  }
} as any;

import { EventLog } from '../src/engine/EventLog';
import {
  AssessmentEngine,
  applyEvent,
  replay,
  SubskillState
} from '../src/engine/AssessmentEngine';
import {
  ALPEvent,
  ALPAttemptEvent,
  ALPCheckpointEvent,
  ALPSessionEvent,
  ALPBaseEvent
} from '../src/engine/EventTypes';

test('Device Identity: alp_device_id is 12 random hex chars and alp_device_seq never reuses a seq', () => {
  localStorage.clear();
  const id1 = EventLog.getDeviceId();
  assert.equal(id1.length, 12);
  assert.match(id1, /^[0-9a-f]{12}$/);

  // Calling again returns the exact same device ID
  const id2 = EventLog.getDeviceId();
  assert.equal(id1, id2);

  // Device sequence increments monotonically
  const seq1 = EventLog.nextDeviceSeq();
  const seq2 = EventLog.nextDeviceSeq();
  const seq3 = EventLog.nextDeviceSeq();
  assert.equal(seq1, 1);
  assert.equal(seq2, 2);
  assert.equal(seq3, 3);
});

test('EventLog Chunking: stores events in chunks ~40 KB and appends cleanly', () => {
  localStorage.clear();
  const kid = 'alice';
  const devId = 'dev111222333';

  // Append a few normal events
  for (let i = 1; i <= 5; i++) {
    const ev: ALPAttemptEvent = {
      i: `${devId}-${i}`,
      d: devId,
      q: i,
      t: 1000 + i * 100,
      y: 'att',
      ep: 0,
      s: 'M-NQ-01',
      m: `item_${i}`,
      ok: 1,
      h: 0,
      md: 'TAP_SELECT',
      cf: 0,
      ss: 'sess_1'
    };
    EventLog.appendEvent(kid, ev);
  }

  assert.equal(EventLog.getEventCount(kid), 5);
  const events = EventLog.getEvents(kid);
  assert.equal(events.length, 5);
  assert.equal(events[0].i, `${devId}-1`);
  assert.equal(events[4].i, `${devId}-5`);

  // Verify multiple chunks created when payload exceeds CHUNK_SIZE_LIMIT
  // Create an event with a large payload (~25 KB) to trigger chunk rollover
  const largeStr = 'x'.repeat(25000);
  const evLarge1: ALPAttemptEvent = {
    i: `${devId}-6`,
    d: devId,
    q: 6,
    t: 2000,
    y: 'att',
    ep: 0,
    s: 'M-NQ-01',
    m: largeStr,
    ok: 1,
    h: 0,
    md: 'TAP_SELECT',
    cf: 0,
    ss: 'sess_1'
  };
  EventLog.appendEvent(kid, evLarge1);

  const evLarge2: ALPAttemptEvent = {
    i: `${devId}-7`,
    d: devId,
    q: 7,
    t: 2100,
    y: 'att',
    ep: 0,
    s: 'M-NQ-01',
    m: largeStr,
    ok: 1,
    h: 0,
    md: 'TAP_SELECT',
    cf: 0,
    ss: 'sess_1'
  };
  EventLog.appendEvent(kid, evLarge2);

  // Should have rolled over into a second chunk (chunk_0 and chunk_1)
  const metaRaw = localStorage.getItem(`alp_${kid}_ev_meta`);
  assert.ok(metaRaw);
  const meta = JSON.parse(metaRaw);
  assert.equal(meta.count, 2);
  assert.ok(localStorage.getItem(`alp_${kid}_ev_0`));
  assert.ok(localStorage.getItem(`alp_${kid}_ev_1`));

  // getEvents reads all events across chunks seamlessly
  const allRead = EventLog.getEvents(kid);
  assert.equal(allRead.length, 7);
});

test('(a) Replay is invariant under any permutation of the same event set', () => {
  const baseTime = 1700000000000;
  const dev1 = '111111111111';
  const dev2 = '222222222222';

  const events: ALPEvent[] = [
    { i: `${dev1}-1`, d: dev1, q: 1, t: baseTime + 100, y: 'att', ep: 0, s: 'M-NQ-01', m: 'i1', ok: 1, h: 0, md: 'TAP_SELECT', cf: 0, ss: 's1' },
    { i: `${dev1}-2`, d: dev1, q: 2, t: baseTime + 200, y: 'att', ep: 0, s: 'M-NQ-01', m: 'i2', ok: 1, h: 0, md: 'TAP_SELECT', cf: 0, ss: 's1' },
    { i: `${dev2}-1`, d: dev2, q: 1, t: baseTime + 150, y: 'att', ep: 0, s: 'M-NQ-02', m: 'i3', ok: 1, h: 0, md: 'TAP_SELECT', cf: 0, ss: 's1' },
    { i: `${dev2}-2`, d: dev2, q: 2, t: baseTime + 300, y: 'att', ep: 0, s: 'M-NQ-02', m: 'i4', ok: 0, h: 1, md: 'TAP_SELECT', cf: 0, ss: 's1' },
    { i: `${dev1}-3`, d: dev1, q: 3, t: baseTime + 400, y: 'att', ep: 0, s: 'M-NQ-01', m: 'i5', ok: 1, h: 0, md: 'TAP_SELECT', cf: 0, ss: 's1' }
  ];

  const standardResult = replay(events);

  // Generate permutations and verify identical states
  const perm1 = [events[4], events[2], events[0], events[3], events[1]];
  const perm2 = [events[1], events[3], events[4], events[0], events[2]];
  const perm3 = [events[3], events[4], events[2], events[1], events[0]];

  assert.deepEqual(replay(perm1), standardResult);
  assert.deepEqual(replay(perm2), standardResult);
  assert.deepEqual(replay(perm3), standardResult);
});

test('(b) Duplicating events changes nothing', () => {
  const dev = 'abcdef123456';
  const events: ALPEvent[] = [
    { i: `${dev}-1`, d: dev, q: 1, t: 1000, y: 'att', ep: 0, s: 'M-NQ-01', m: 'i1', ok: 1, h: 0, md: 'TAP_SELECT', cf: 0, ss: 's1' },
    { i: `${dev}-2`, d: dev, q: 2, t: 2000, y: 'att', ep: 0, s: 'M-NQ-01', m: 'i2', ok: 1, h: 0, md: 'TAP_SELECT', cf: 0, ss: 's1' }
  ];

  const originalState = replay(events);

  // Triplicate the events in the list
  const duplicated = [...events, ...events, ...events];
  const dedupedState = replay(duplicated);

  assert.deepEqual(dedupedState, originalState);
});

test('(c) Two devices same day, interleaved attempts, both counted', () => {
  const devA = 'aaaa11112222';
  const devB = 'bbbb11112222';
  const baseT = 1710000000000;

  // Interleaved attempts on same subskill
  const events: ALPEvent[] = [
    { i: `${devA}-1`, d: devA, q: 1, t: baseT + 100, y: 'att', ep: 0, s: 'M-NQ-01', m: 'i1', ok: 1, h: 0, md: 'TAP_SELECT', cf: 0, ss: 'sA' },
    { i: `${devB}-1`, d: devB, q: 1, t: baseT + 200, y: 'att', ep: 0, s: 'M-NQ-01', m: 'i2', ok: 1, h: 0, md: 'TAP_SELECT', cf: 0, ss: 'sB' },
    { i: `${devA}-2`, d: devA, q: 2, t: baseT + 300, y: 'att', ep: 0, s: 'M-NQ-01', m: 'i3', ok: 1, h: 0, md: 'TAP_SELECT', cf: 0, ss: 'sA' },
    { i: `${devB}-2`, d: devB, q: 2, t: baseT + 400, y: 'att', ep: 0, s: 'M-NQ-01', m: 'i4', ok: 1, h: 0, md: 'TAP_SELECT', cf: 0, ss: 'sB' }
  ];

  const state = replay(events);
  assert.ok(state['M-NQ-01']);
  assert.equal(state['M-NQ-01'].attempts, 4);
  assert.equal(state['M-NQ-01'].successes, 4);
  assert.equal(state['M-NQ-01'].consecutive_successes, 4);
  assert.equal(state['M-NQ-01'].state, 'FLEXIBLE'); // streak >= 3 advances to FLEXIBLE
});

test('(d) The same R2 checkpoint on two devices counts once, deterministic winner', () => {
  const devA = 'aaaa11112222';
  const devB = 'bbbb11112222';
  const t1 = 1710000000000;
  const t2 = 1710000001000;

  // Device A passes R2 at t1; Device B fails R2 at t2
  const events: ALPEvent[] = [
    // Pre-requisite: Bring skill to FLEXIBLE
    { i: `${devA}-1`, d: devA, q: 1, t: t1 - 10000, y: 'att', ep: 0, s: 'M-OP-01', m: 'i1', ok: 1, h: 0, md: 'TAP_SELECT', cf: 0, ss: 's1' },
    { i: `${devA}-2`, d: devA, q: 2, t: t1 - 9000, y: 'att', ep: 0, s: 'M-OP-01', m: 'i2', ok: 1, h: 0, md: 'TAP_SELECT', cf: 0, ss: 's1' },
    { i: `${devA}-3`, d: devA, q: 3, t: t1 - 8000, y: 'att', ep: 0, s: 'M-OP-01', m: 'i3', ok: 1, h: 0, md: 'TAP_SELECT', cf: 0, ss: 's1' },
    // Device A's R2 event (first in total order)
    { i: `${devA}-4`, d: devA, q: 4, t: t1, y: 'ckp', ep: 0, s: 'M-OP-01', r: 2, ok: 1, ss: 'sA' },
    // Device B's duplicate R2 event (later in total order)
    { i: `${devB}-1`, d: devB, q: 1, t: t2, y: 'ckp', ep: 0, s: 'M-OP-01', r: 2, ok: 0, ss: 'sB' }
  ];

  const stateForward = replay(events);
  const stateReverse = replay([events[4], events[3], events[2], events[1], events[0]]);

  // Dev A at t1 is the deterministic winner; Dev B's R2 duplicate is ignored
  assert.deepEqual(stateForward, stateReverse);
  assert.equal(stateForward['M-OP-01'].state, 'FLEXIBLE');
});

test('(e) Skew +24h and -24h produces no demotion', () => {
  const dev = 'devclock1234';
  const now = 1710000000000;
  const dayMs = 24 * 60 * 60 * 1000;

  // Normal progression to SECURE
  const baseEvents: ALPEvent[] = [
    { i: `${dev}-1`, d: dev, q: 1, t: now, y: 'att', ep: 0, s: 'E-PH-01', m: 'i1', ok: 1, h: 0, md: 'TAP_SELECT', cf: 0, ss: 's1' },
    { i: `${dev}-2`, d: dev, q: 2, t: now + 100, y: 'att', ep: 0, s: 'E-PH-01', m: 'i2', ok: 1, h: 0, md: 'TAP_SELECT', cf: 0, ss: 's1' }
  ];

  const stateNormal = replay(baseEvents, 0, now);
  assert.equal(stateNormal['E-PH-01'].state, 'SECURE');

  // Skew clock forward +24 hours
  const stateSkewPlus24 = replay(baseEvents, 0, now + dayMs);
  assert.equal(stateSkewPlus24['E-PH-01'].state, 'SECURE');

  // Skew clock backward -24 hours
  const stateSkewMinus24 = replay(baseEvents, 0, now - dayMs);
  assert.equal(stateSkewMinus24['E-PH-01'].state, 'SECURE');
});

test('(f) Fatigue-ended session adds no negative evidence', () => {
  const dev = 'devfatigue01';
  const baseT = 1710000000000;
  const sess = 'sess_fatigue_test';

  const events: ALPEvent[] = [
    // Session start
    { i: `${dev}-1`, d: dev, q: 1, t: baseT, y: 'ses', ep: 0, ss: sess, e: 'start' },
    // Question 1: answered correctly before fatigue
    { i: `${dev}-2`, d: dev, q: 2, t: baseT + 1000, y: 'att', ep: 0, s: 'M-NQ-01', m: 'i1', ok: 1, h: 0, md: 'TAP_SELECT', cf: 0, ss: sess },
    // Fatigue boundary triggered
    { i: `${dev}-3`, d: dev, q: 3, t: baseT + 2000, y: 'ses', ep: 0, ss: sess, e: 'end', why: 'fatigue' },
    // Question 2 attempted AFTER fatigue boundary: failed
    { i: `${dev}-4`, d: dev, q: 4, t: baseT + 3000, y: 'att', ep: 0, s: 'M-NQ-01', m: 'i2', ok: 0, h: 1, md: 'TAP_SELECT', cf: 0, ss: sess }
  ];

  const state = replay(events);
  // Only the pre-fatigue correct attempt should be counted
  assert.equal(state['M-NQ-01'].attempts, 1);
  assert.equal(state['M-NQ-01'].successes, 1);
  assert.equal(state['M-NQ-01'].consecutive_successes, 1);
  assert.equal(state['M-NQ-01'].state, 'DEVELOPING');
});

test('(g) A "base" event plus later events reproduces the pre-upgrade state exactly', () => {
  const dev = 'devlegacy001';
  const baseT = 1710000000000;

  const preUpgradeState: { [id: string]: SubskillState } = {
    'M-NQ-01': { subskill_id: 'M-NQ-01', state: 'DEVELOPING', successes: 3, attempts: 4, consecutive_successes: 1, last_active: baseT - 5000 },
    'E-OL-01': { subskill_id: 'E-OL-01', state: 'SECURE', successes: 5, attempts: 6, consecutive_successes: 3, last_active: baseT - 3000 }
  };

  const events: ALPEvent[] = [
    // One-time baseline event
    { i: `${dev}-1`, d: dev, q: 1, t: baseT, y: 'base', ep: 0, states: preUpgradeState },
    // Later event adding success to M-NQ-01
    { i: `${dev}-2`, d: dev, q: 2, t: baseT + 1000, y: 'att', ep: 0, s: 'M-NQ-01', m: 'i1', ok: 1, h: 0, md: 'TAP_SELECT', cf: 0, ss: 's1' }
  ];

  const state = replay(events);

  // E-OL-01 kept exactly as migrated
  assert.equal(state['E-OL-01'].state, 'SECURE');
  assert.equal(state['E-OL-01'].successes, 5);
  assert.equal(state['E-OL-01'].attempts, 6);

  // M-NQ-01 advanced from 3 successes -> 4 successes (DEVELOPING -> SECURE)
  assert.equal(state['M-NQ-01'].successes, 4);
  assert.equal(state['M-NQ-01'].attempts, 5);
  assert.equal(state['M-NQ-01'].consecutive_successes, 2);
  assert.equal(state['M-NQ-01'].state, 'SECURE');
});

test('(h) Single-data-point guardrail: replay of a log yields exactly the state live play yields under the existing rules, and a merge never produces a stage the existing rules would not produce from the same events', () => {
  localStorage.clear();
  const kid = 'charlie';
  const engine = new AssessmentEngine(kid);

  // 1. Live play: simulate 1 attempt (correct)
  engine.recordAttempt('M-GS-01', true, 'EVIDENCE_1', { hintTier: 0, modality: 'TAP_SELECT', itemId: 'item_1', sessionId: 'sess_live' });
  const liveState1 = engine.getSubskillState('M-GS-01');
  assert.equal(liveState1, 'DEVELOPING'); // streak=1 -> DEVELOPING

  // Replay of this exact event log matches live play
  const eventsLive1 = EventLog.getEvents(kid);
  const replayed1 = replay(eventsLive1);
  assert.equal(replayed1['M-GS-01'].state, liveState1);

  // 2. Add second correct attempt
  engine.recordAttempt('M-GS-01', true, 'EVIDENCE_1', { hintTier: 0, modality: 'TAP_SELECT', itemId: 'item_2', sessionId: 'sess_live' });
  const liveState2 = engine.getSubskillState('M-GS-01');
  assert.equal(liveState2, 'SECURE'); // streak=2 -> SECURE

  const eventsLive2 = EventLog.getEvents(kid);
  const replayed2 = replay(eventsLive2);
  assert.equal(replayed2['M-GS-01'].state, liveState2);

  // 3. Verify that merging fewer events than required NEVER produces a stage jump
  // Single incorrect event can never jump to DEVELOPING or SECURE
  const singleFailEvent: ALPEvent[] = [
    { i: 'devX-1', d: 'devX', q: 1, t: 1000, y: 'att', ep: 0, s: 'M-GS-02', m: 'i1', ok: 0, h: 0, md: 'TAP_SELECT', cf: 0, ss: 'sX' }
  ];
  const replayedFail = replay(singleFailEvent);
  assert.equal(replayedFail['M-GS-02'].state, 'INTRODUCED');
});

test('(i) Epoch test: old-epoch events pulled from the server do not resurrect progress', () => {
  const dev = 'dev333444555';
  const baseT = 1710000000000;

  // Events written before reset (epoch 0)
  const oldEpochEvents: ALPEvent[] = [
    { i: `${dev}-1`, d: dev, q: 1, t: baseT, y: 'att', ep: 0, s: 'M-NQ-01', m: 'i1', ok: 1, h: 0, md: 'TAP_SELECT', cf: 0, ss: 's1' },
    { i: `${dev}-2`, d: dev, q: 2, t: baseT + 100, y: 'att', ep: 0, s: 'M-NQ-01', m: 'i2', ok: 1, h: 0, md: 'TAP_SELECT', cf: 0, ss: 's1' },
    { i: `${dev}-3`, d: dev, q: 3, t: baseT + 200, y: 'att', ep: 0, s: 'M-NQ-01', m: 'i3', ok: 1, h: 0, md: 'TAP_SELECT', cf: 0, ss: 's1' }
  ];

  // If replayed under epoch 0, M-NQ-01 would be FLEXIBLE
  const stateEpoch0 = replay(oldEpochEvents, 0);
  assert.equal(stateEpoch0['M-NQ-01'].state, 'FLEXIBLE');

  // Reset Progress happened: profile epoch is now 1
  // Replaying with currentEpoch = 1 ignores all epoch 0 events
  const stateEpoch1 = replay(oldEpochEvents, 1);
  assert.equal(stateEpoch1['M-NQ-01'], undefined); // No progress resurrected!

  // New events recorded in epoch 1
  const newEpochEvents: ALPEvent[] = [
    ...oldEpochEvents,
    { i: `${dev}-4`, d: dev, q: 4, t: baseT + 1000, y: 'att', ep: 1, s: 'M-NQ-01', m: 'i4', ok: 1, h: 0, md: 'TAP_SELECT', cf: 0, ss: 's2' }
  ];

  const stateNew = replay(newEpochEvents, 1);
  // Only the epoch 1 event applies: 1 attempt, 1 success -> DEVELOPING
  assert.equal(stateNew['M-NQ-01'].attempts, 1);
  assert.equal(stateNew['M-NQ-01'].successes, 1);
  assert.equal(stateNew['M-NQ-01'].state, 'DEVELOPING');
});
