import { SubskillState } from './AssessmentEngine';

export interface ALPEventBase {
  i: string;        // deviceId-seq, e.g. "a1b2c3d4e5f6-1"
  d: string;        // deviceId
  q: number;        // device sequence counter
  t: number;        // client UTC ms timestamp
  y: 'att' | 'ckp' | 'ses' | 'base'; // event type
  ep: number;       // kid's epoch at write time
  r?: number;       // server receive UTC ms timestamp (for att/ses/base)
  recv_r?: number;  // server receive UTC ms timestamp (especially for ckp to avoid collision with tier r)
}

export interface ALPAttemptEvent extends ALPEventBase {
  y: 'att';
  s: string;        // skillId / subskill_id
  m: string;        // itemId
  ok: 0 | 1;        // outcome: 1=correct, 0=incorrect
  h: number;        // hintTier: 0-3
  md: string;       // modality (e.g. "TAP_SELECT")
  cf: 0 | 1;        // modality confound flag (always 0)
  ss: string;       // sessionId
}

export interface ALPCheckpointEvent extends ALPEventBase {
  y: 'ckp';
  s: string;        // skillId / subskill_id
  r: 1 | 2 | 3;     // retrieval checkpoint tier: R1=1, R2=2, R3=3
  ok: 0 | 1;        // outcome: 1=pass, 0=fail
  ss: string;       // sessionId
}

export interface ALPSessionEvent extends ALPEventBase {
  y: 'ses';
  ss: string;       // sessionId
  e: 'start' | 'end';
  why?: 'done' | 'fatigue' | 'quit';
}

export interface ALPBaseEvent extends ALPEventBase {
  y: 'base';
  states: { [subskill_id: string]: SubskillState };
}

export type ALPEvent = ALPAttemptEvent | ALPCheckpointEvent | ALPSessionEvent | ALPBaseEvent;
