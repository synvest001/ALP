export type MasteryState = 'INTRODUCED' | 'DEVELOPING' | 'SECURE' | 'FLEXIBLE' | 'GENERALIZED';

export interface SubskillState {
  subskill_id: string;
  state: MasteryState;
  successes: number;
  attempts: number;
  consecutive_successes?: number;
  last_active: number;
}

export class AssessmentEngine {
  private states: Map<string, SubskillState> = new Map();
  private kidId: string = 'default_player';

  constructor(kidId?: string) {
    if (kidId) {
      this.kidId = kidId.toLowerCase().trim();
    } else {
      const current = localStorage.getItem('alp_current_name');
      if (current) this.kidId = current.toLowerCase().trim();
    }
    this.loadState();
  }

  public setKidId(kidId: string) {
    const clean = (kidId || 'default_player').toLowerCase().trim();
    if (this.kidId !== clean) {
      this.kidId = clean;
      this.loadState();
    }
  }

  private getStorageKey(): string {
    return `alp_${this.kidId}_assessment_states`;
  }

  private loadState() {
    this.states.clear();
    const key = this.getStorageKey();
    let raw = localStorage.getItem(key);
    // Fallback to legacy global state if kid state not yet initialized
    if (!raw && this.kidId === 'default_player') {
      raw = localStorage.getItem('alp_assessment_states');
    }
    if (raw) {
      try {
        const parsed = JSON.parse(raw);
        for (const k of Object.keys(parsed)) {
          this.states.set(k, parsed[k]);
        }
      } catch (e) {
        console.error("Failed to parse assessment state", e);
      }
    }
  }

  private saveState() {
    const obj: any = {};
    this.states.forEach((val, key) => {
      obj[key] = val;
    });
    localStorage.setItem(this.getStorageKey(), JSON.stringify(obj));
    // Also update global legacy key if default
    if (this.kidId === 'default_player') {
      localStorage.setItem('alp_assessment_states', JSON.stringify(obj));
    }
  }

  public getSubskillState(subskill_id: string): MasteryState {
    const state = this.states.get(subskill_id);
    return state ? state.state : 'INTRODUCED';
  }

  public getAllStates(): SubskillState[] {
    return Array.from(this.states.values());
  }

  public getSecureSubskills(): Set<string> {
    const secure = new Set<string>();
    this.states.forEach((state, id) => {
      if (state.state === 'SECURE' || state.state === 'FLEXIBLE' || state.state === 'GENERALIZED') {
        secure.add(id);
      }
    });
    return secure;
  }

  public getActiveSubskills(): string[] {
    const active: string[] = [];
    this.states.forEach((state, id) => {
      if (state.state === 'INTRODUCED' || state.state === 'DEVELOPING') {
        active.push(id);
      }
    });
    return active;
  }

  /**
   * Implements Workstream 3 §5.1 Depth-First Cognitive Depth Escalation:
   * INTRODUCED  -> APPLY (Level 1 Surface)
   * DEVELOPING  -> REASON (Level 2/3 Contextual & Representational)
   * SECURE      -> GENERALIZE (Level 4 Structural)
   */
  public getTargetCognitiveDepth(subskill_id?: string): string {
    if (!subskill_id) return 'APPLY';
    const state = this.getSubskillState(subskill_id);
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

  public recordAttempt(subskill_id: string, isCorrect: boolean, archetype: string) {
    let state = this.states.get(subskill_id);
    if (!state) {
      state = { subskill_id, state: 'INTRODUCED', successes: 0, attempts: 0, consecutive_successes: 0, last_active: Date.now() };
      this.states.set(subskill_id, state);
    }

    state.attempts++;
    state.last_active = Date.now();
    if (isCorrect) {
      state.successes++;
      state.consecutive_successes = (state.consecutive_successes || 0) + 1;
    } else {
      state.consecutive_successes = 0;
    }

    this.evaluateTransitions(state, archetype);
    this.saveState();
  }

  private evaluateTransitions(state: SubskillState, _archetype: string) {
    const prevState = state.state;
    const streak = state.consecutive_successes || 0;

    // Fast-Track progression logic:
    // If the kid is answering correctly (streak >= 1 or streak >= 2), advance immediately!
    if (state.state === 'INTRODUCED' && (streak >= 1 || state.successes >= 2)) {
      state.state = 'DEVELOPING';
      console.log(`[AssessmentEngine] ${state.subskill_id} FAST-TRACK advanced to DEVELOPING (Cognitive Depth escalates to REASON)`);
    } else if (state.state === 'DEVELOPING' && (streak >= 2 || state.successes >= 4)) {
      state.state = 'SECURE';
      console.log(`[AssessmentEngine] ${state.subskill_id} FAST-TRACK advanced to SECURE (Unlocked downstream prerequisites; Cognitive Depth escalates to GENERALIZE)`);
    } else if (state.state === 'SECURE' && (streak >= 3 || state.successes >= 6)) {
      state.state = 'FLEXIBLE';
      console.log(`[AssessmentEngine] ${state.subskill_id} advanced to FLEXIBLE`);
    }

    if (prevState !== state.state) {
      try {
        window.dispatchEvent(new CustomEvent('alp:mastery_transition', {
          detail: { subskill_id: state.subskill_id, oldState: prevState, newState: state.state }
        }));
      } catch (e) {}
    }
  }
}
