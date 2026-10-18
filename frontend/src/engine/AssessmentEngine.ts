import { ALPEvent, ALPAttemptEvent } from './EventTypes';
import { EventLog } from './EventLog';

export type MasteryState = 'INTRODUCED' | 'DEVELOPING' | 'SECURE' | 'FLEXIBLE' | 'GENERALIZED';

export interface SubskillState {
  subskill_id: string;
  state: MasteryState;
  successes: number;
  attempts: number;
  consecutive_successes?: number;
  last_active: number;
}

export function getEffectiveTime(ev: ALPEvent, localNow: number): number {
  var srv: number | undefined;
  if (ev.y === 'ckp') {
    srv = ev.recv_r;
  } else {
    srv = typeof ev.r === 'number' && ev.r > 1000000000 ? ev.r : undefined;
  }
  if (typeof srv === 'number' && !isNaN(srv)) {
    return Math.min(ev.t, srv);
  }
  return Math.min(ev.t, localNow);
}

export function compareEvents(a: ALPEvent, b: ALPEvent, localNow: number): number {
  var ta = getEffectiveTime(a, localNow);
  var tb = getEffectiveTime(b, localNow);
  if (ta !== tb) return ta - tb;
  if (a.d !== b.d) return a.d < b.d ? -1 : 1;
  return (a.q || 0) - (b.q || 0);
}

/**
 * Pure function: applies a single event to a dictionary of SubskillState.
 * Uses event.t for last_active, never Date.now().
 */
export function applyEvent(
  states: { [subskill_id: string]: SubskillState },
  ev: ALPEvent
): { [subskill_id: string]: SubskillState } {
  if (ev.y === 'base') {
    if (ev.states) {
      for (var k in ev.states) {
        if (Object.prototype.hasOwnProperty.call(ev.states, k)) {
          var src = ev.states[k];
          states[k] = {
            subskill_id: src.subskill_id,
            state: src.state,
            successes: src.successes || 0,
            attempts: src.attempts || 0,
            consecutive_successes: src.consecutive_successes || 0,
            last_active: src.last_active || ev.t
          };
        }
      }
    }
  } else if (ev.y === 'att') {
    var sid = ev.s;
    if (!states[sid]) {
      states[sid] = {
        subskill_id: sid,
        state: 'INTRODUCED',
        successes: 0,
        attempts: 0,
        consecutive_successes: 0,
        last_active: ev.t
      };
    }
    var st = states[sid];
    st.attempts += 1;
    st.last_active = ev.t;
    if (ev.ok === 1) {
      st.successes += 1;
      st.consecutive_successes = (st.consecutive_successes || 0) + 1;
    } else {
      st.consecutive_successes = 0;
    }

    var streak = st.consecutive_successes || 0;
    // Exactly existing fast-track progression thresholds:
    if (st.state === 'INTRODUCED' && (streak >= 1 || st.successes >= 2)) {
      st.state = 'DEVELOPING';
    } else if (st.state === 'DEVELOPING' && (streak >= 2 || st.successes >= 4)) {
      st.state = 'SECURE';
    } else if (st.state === 'SECURE' && (streak >= 3 || st.successes >= 6)) {
      st.state = 'FLEXIBLE';
    }
  } else if (ev.y === 'ckp') {
    if (ev.ok === 1 && ev.r === 3) {
      if (states[ev.s] && states[ev.s].state === 'FLEXIBLE') {
        states[ev.s].state = 'GENERALIZED';
      }
    }
  }
  return states;
}

/**
 * Pure function: deterministic replay of an event set.
 * Invariant under any permutation of the same event set.
 */
export function replay(
  events: ALPEvent[],
  currentEpoch: number,
  localNow: number
): { [subskill_id: string]: SubskillState } {
  if (typeof localNow !== 'number' || isNaN(localNow)) {
    throw new Error('replay() requires an explicit localNow timestamp');
  }
  var now = localNow;
  var seenIds: { [id: string]: boolean } = {};
  var unique: ALPEvent[] = [];

  for (var i = 0; i < events.length; i++) {
    var ev = events[i];
    if (typeof currentEpoch === 'number' && ev.ep < currentEpoch) {
      continue; // Ignore old-epoch events
    }
    if (!seenIds[ev.i]) {
      seenIds[ev.i] = true;
      unique.push(ev);
    }
  }

  // Sort into deterministic total order: (tEff, d, q)
  unique.sort(function (a, b) {
    return compareEvents(a, b, now);
  });

  var states: { [subskill_id: string]: SubskillState } = {};
  var seenCheckpoints: { [key: string]: boolean } = {};
  var failedProbesPerSession: { [key: string]: number } = {};
  var fatigueSessions: { [sessionId: string]: number } = {};

  for (var j = 0; j < unique.length; j++) {
    var item = unique[j];

    if (item.y === 'ses') {
      if (item.e === 'end' && item.why === 'fatigue') {
        fatigueSessions[item.ss] = item.t;
      }
      continue;
    }

    if (item.y === 'att') {
      // If session ended by fatigue, attempts made after fatigue trigger add no negative evidence.
      // Successful attempts (ok === 1) are preserved; only failed attempts (ok === 0) are discarded.
      if (item.ss && typeof fatigueSessions[item.ss] === 'number') {
        if (item.t >= fatigueSessions[item.ss] && item.ok === 0) {
          continue;
        }
      }
      applyEvent(states, item);
    } else if (item.y === 'ckp') {
      var ckpKey = item.s + '_' + item.r;
      if (seenCheckpoints[ckpKey]) {
        // Later checkpoint events for the same (skill, r) are ignored
        continue;
      }
      seenCheckpoints[ckpKey] = true;

      if (item.ok === 1) {
        applyEvent(states, item);
      } else {
        // Checkpoint failure: Demotion requires two probe failures in the SAME session
        var probeKey = (item.ss || '') + '_' + item.s;
        failedProbesPerSession[probeKey] = (failedProbesPerSession[probeKey] || 0) + 1;
        if (failedProbesPerSession[probeKey] >= 2) {
          if (states[item.s]) {
            var st = states[item.s].state;
            if (st === 'SECURE' || st === 'FLEXIBLE' || st === 'GENERALIZED') {
              states[item.s].state = 'DEVELOPING';
            }
          }
        }
      }
    } else if (item.y === 'base') {
      applyEvent(states, item);
    }
  }

  return states;
}

export class AssessmentEngine {
  private states: { [subskill_id: string]: SubskillState } = {};
  private kidId: string = 'default_player';

  constructor(kidId?: string) {
    if (kidId) {
      this.kidId = kidId.toLowerCase().trim();
    } else {
      var current = localStorage.getItem('alp_current_name');
      if (current) this.kidId = current.toLowerCase().trim();
    }
    this.init();
  }

  public setKidId(kidId: string): void {
    var clean = (kidId || 'default_player').toLowerCase().trim();
    if (this.kidId !== clean) {
      this.kidId = clean;
      this.init();
    }
  }

  public reload(): void {
    this.loadState();
  }

  private getKidEpoch(): number {
    var raw = localStorage.getItem('alp_' + this.kidId + '_sync_epoch');
    var n = parseInt(raw || '0', 10);
    return isNaN(n) ? 0 : n;
  }

  private getStorageKey(): string {
    return 'alp_' + this.kidId + '_assessment_states';
  }

  private init(): void {
    this.loadState();
    // One-time baseline migration if needed
    EventLog.initKidLog(this.kidId, this.getKidEpoch(), this.states);
  }

  private loadState(): void {
    this.states = {};
    var key = this.getStorageKey();
    var raw = localStorage.getItem(key);
    if (!raw && this.kidId === 'default_player') {
      raw = localStorage.getItem('alp_assessment_states');
    }
    if (raw) {
      try {
        var parsed = JSON.parse(raw);
        for (var k in parsed) {
          if (Object.prototype.hasOwnProperty.call(parsed, k)) {
            this.states[k] = parsed[k];
          }
        }
      } catch (e) {
        console.error('Failed to parse assessment state', e);
      }
    } else {
      // If cache empty, rebuild from event log replay
      var events = EventLog.getEvents(this.kidId);
      if (events.length > 0) {
        this.states = replay(events, this.getKidEpoch(), Date.now());
        this.saveState();
      }
    }
  }

  private saveState(): void {
    var serialized = JSON.stringify(this.states);
    localStorage.setItem(this.getStorageKey(), serialized);
    if (this.kidId === 'default_player') {
      localStorage.setItem('alp_assessment_states', serialized);
    }
  }

  public getSubskillState(subskill_id: string): MasteryState {
    var state = this.states[subskill_id];
    return state ? state.state : 'INTRODUCED';
  }

  public getAllStates(): SubskillState[] {
    var list: SubskillState[] = [];
    for (var k in this.states) {
      if (Object.prototype.hasOwnProperty.call(this.states, k)) {
        list.push(this.states[k]);
      }
    }
    return list;
  }

  /**
   * Returns a plain ES5 object implementing Set-like interface { has(code): boolean }
   * for seamless compatibility with CurriculumGraph without requiring ES6 Set.
   */
  public getSecureSubskills(): any {
    var secure: { [code: string]: boolean } = {};
    for (var id in this.states) {
      if (Object.prototype.hasOwnProperty.call(this.states, id)) {
        var st = this.states[id].state;
        if (st === 'SECURE' || st === 'FLEXIBLE' || st === 'GENERALIZED') {
          secure[id] = true;
        }
      }
    }
    return {
      has: function (code: string): boolean {
        return Boolean(secure[code]);
      },
      add: function (code: string): any {
        secure[code] = true;
        return this;
      }
    };
  }

  public getActiveSubskills(): string[] {
    var active: string[] = [];
    for (var id in this.states) {
      if (Object.prototype.hasOwnProperty.call(this.states, id)) {
        var st = this.states[id].state;
        if (st === 'INTRODUCED' || st === 'DEVELOPING') {
          active.push(id);
        }
      }
    }
    return active;
  }

  public getTargetCognitiveDepth(subskill_id?: string): string {
    if (!subskill_id) return 'APPLY';
    var state = this.getSubskillState(subskill_id);
    switch (state) {
      case 'INTRODUCED':
        return 'APPLY';
      case 'DEVELOPING':
        return 'REASON';
      case 'SECURE':
      case 'FLEXIBLE':
      case 'GENERALIZED':
        return 'GENERALIZE';
      default:
        return 'APPLY';
    }
  }

  public recordAttempt(
    subskill_id: string,
    isCorrect: boolean,
    _archetype: string,
    options?: {
      hintTier?: number;
      modality?: string;
      itemId?: string;
      sessionId?: string;
    }
  ): void {
    var devId = EventLog.getDeviceId();
    var seq = EventLog.nextDeviceSeq();
    var now = Date.now();
    var epoch = this.getKidEpoch();

    var ev: ALPAttemptEvent = {
      i: devId + '-' + seq,
      d: devId,
      q: seq,
      t: now,
      y: 'att',
      ep: epoch,
      s: subskill_id,
      m: options && options.itemId ? options.itemId : '',
      ok: isCorrect ? 1 : 0,
      h: options && typeof options.hintTier === 'number' ? options.hintTier : 0,
      md: options && options.modality ? options.modality : 'TAP_SELECT',
      cf: 0,
      ss: options && options.sessionId ? options.sessionId : ''
    };

    // 1. Append event to the chunked append-only log
    EventLog.appendEvent(this.kidId, ev);

    // 2. Update local cached state via pure applyEvent
    var prevState = this.getSubskillState(subskill_id);
    applyEvent(this.states, ev);
    var newState = this.getSubskillState(subskill_id);

    // 3. Save cached state
    this.saveState();

    // 4. Dispatch mastery transition event if changed
    if (prevState !== newState) {
      try {
        window.dispatchEvent(
          new CustomEvent('alp:mastery_transition', {
            detail: { subskill_id: subskill_id, oldState: prevState, newState: newState }
          })
        );
      } catch (e) {}
    }
  }
}
