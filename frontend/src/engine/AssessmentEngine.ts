export type MasteryState = 'INTRODUCED' | 'DEVELOPING' | 'SECURE' | 'FLEXIBLE' | 'GENERALIZED';

export interface SubskillState {
  subskill_id: string;
  state: MasteryState;
  successes: number;
  attempts: number;
  last_active: number;
}

export class AssessmentEngine {
  private states: Map<string, SubskillState> = new Map();

  constructor() {
    this.loadState();
  }

  private loadState() {
    const raw = localStorage.getItem('alp_assessment_states');
    if (raw) {
      try {
        const parsed = JSON.parse(raw);
        for (const key of Object.keys(parsed)) {
          this.states.set(key, parsed[key]);
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
    localStorage.setItem('alp_assessment_states', JSON.stringify(obj));
  }

  public getSubskillState(subskill_id: string): MasteryState {
    const state = this.states.get(subskill_id);
    return state ? state.state : 'INTRODUCED';
  }

  public getAllStates(): SubskillState[] {
    return Array.from(this.states.values());
  }

  public recordAttempt(subskill_id: string, isCorrect: boolean, archetype: string) {
    let state = this.states.get(subskill_id);
    if (!state) {
      state = { subskill_id, state: 'INTRODUCED', successes: 0, attempts: 0, last_active: Date.now() };
      this.states.set(subskill_id, state);
    }

    state.attempts++;
    state.last_active = Date.now();
    if (isCorrect) {
      state.successes++;
    }

    this.evaluateTransitions(state, archetype);
    this.saveState();
  }

  private evaluateTransitions(state: SubskillState, _archetype: string) {
    // Core Logic: implementing WS2 state transitions
    if (state.state === 'INTRODUCED' && state.successes >= 2) {
      state.state = 'DEVELOPING';
      console.log(`[AssessmentEngine] ${state.subskill_id} advanced to DEVELOPING`);
    } else if (state.state === 'DEVELOPING' && state.successes >= 5) {
      // Simplified: Archetypes require 3 unprompted successes across sessions.
      // For MVP, we map 5 total successes to SECURE.
      state.state = 'SECURE';
      console.log(`[AssessmentEngine] ${state.subskill_id} advanced to SECURE`);
    } else if (state.state === 'SECURE' && state.successes >= 10) {
      state.state = 'FLEXIBLE';
      console.log(`[AssessmentEngine] ${state.subskill_id} advanced to FLEXIBLE`);
    }
  }
}
