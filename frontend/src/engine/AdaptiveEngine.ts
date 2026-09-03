import { LearnerSkillProfile, MockProfile } from './LearnerProfileMock';
import { QuestionBank, QuestionItem } from './QuestionBank';
import { AssessmentEngine } from './AssessmentEngine';

export interface TaskRequestPayload {
  session_id: string;
  task_index: number;
  session_task_count: number;
  task_function_type: string;
  target_subskill_id?: string;
  domain_id: string;
  phase_context: string;
  required_cognitive_depth: string;
  time_budget_seconds: number;
  // Generated Question
  question_item?: QuestionItem | null;
}

const DOMAIN_TARGETS: Record<string, [number, number]> = {
  'MATHEMATICS': [30, 40],
  'ENGLISH_LANGUAGE': [25, 35],
  'SCIENCE_EVS_WORLD_KNOWLEDGE': [15, 25],
  'LOGICAL_REASONING': [10, 20]
};

const FUNCTION_TARGETS: Record<string, [number, number]> = {
  'FOCUSED_CORE': [25, 35],
  'RETRIEVAL': [15, 25],
  'CONSOLIDATION': [15, 25],
  'STRATEGIC_REASONING': [15, 25],
  'CREATIVE_TRANSFER': [10, 20]
};

// Map actual domain strings to combined target categories
const mapDomainToCategory = (domain: string) => {
  if (domain === 'SCIENCE_EVS' || domain === 'WORLD_KNOWLEDGE') {
    return 'SCIENCE_EVS_WORLD_KNOWLEDGE';
  }
  return domain;
};

export class SessionComposer {
  private questionBank: QuestionBank;
  private assessmentEngine: AssessmentEngine;

  constructor() {
    this.questionBank = new QuestionBank();
    this.assessmentEngine = new AssessmentEngine();
  }

  public generateSession(profile: LearnerSkillProfile = MockProfile): TaskRequestPayload[] {
    const session: TaskRequestPayload[] = [];
    const sessionId = `sess_${new Date().toISOString().replace(/[:.-]/g, '')}`;
    const targetTaskCount = Math.floor(Math.random() * 3) + 4; // 4 to 6 tasks
    const maxTimeBudgetSeconds = 20 * 60; // 20 minutes
    let currentTimeBudget = 0;

    // STEP 1 - DUE-EVENT INTAKE
    for (const event of profile.dueEvents) {
      if (session.length >= targetTaskCount || currentTimeBudget >= maxTimeBudgetSeconds) break;
      
      const payload: TaskRequestPayload = {
        session_id: sessionId,
        task_index: session.length + 1,
        session_task_count: targetTaskCount,
        task_function_type: event.task_function_type,
        target_subskill_id: event.target_subskill_id,
        domain_id: event.domain_id,
        phase_context: event.phase_context,
        required_cognitive_depth: 'APPLY', // Default for now
        time_budget_seconds: 120
      };
      
      payload.question_item = this.questionBank.getTask(payload.domain_id, payload.target_subskill_id);
      session.push(payload);
      currentTimeBudget += payload.time_budget_seconds;
    }

    // STEP 2 - ROLLING-WINDOW DEFICIT CHECK
    const candidatePairs: { domain: string, functionType: string, deficitScore: number }[] = [];
    
    for (const domain of ['MATHEMATICS', 'ENGLISH_LANGUAGE', 'SCIENCE_EVS', 'WORLD_KNOWLEDGE', 'LOGICAL_REASONING']) {
      const domainCategory = mapDomainToCategory(domain);
      const domainActual = profile.trailing14DayDomainActuals[domainCategory] || 0;
      const domainTarget = DOMAIN_TARGETS[domainCategory];
      
      let domainDeficit = 0;
      if (domainActual < domainTarget[0]) {
        domainDeficit = domainTarget[0] - domainActual;
      }

      for (const functionType of Object.keys(FUNCTION_TARGETS)) {
        const functionActual = profile.trailing14DayFunctionActuals[functionType] || 0;
        const functionTarget = FUNCTION_TARGETS[functionType];
        
        let functionDeficit = 0;
        if (functionActual < functionTarget[0]) {
          functionDeficit = functionTarget[0] - functionActual;
        }

        const combinedDeficit = domainDeficit + functionDeficit;
        candidatePairs.push({ domain, functionType, deficitScore: combinedDeficit });
      }
    }

    // Rank by deficit score descending
    candidatePairs.sort((a, b) => b.deficitScore - a.deficitScore);

    // Get active learning states from real telemetry
    const activeStates = this.assessmentEngine.getAllStates().filter(s => s.state === 'INTRODUCED' || s.state === 'DEVELOPING');

    // STEP 3 - FILL REMAINING TASK BUDGET
    // We will dynamically pick domains based on deficits, rather than forcing M-OP-05
    while (session.length < targetTaskCount && currentTimeBudget < maxTimeBudgetSeconds) {
      const payload: TaskRequestPayload = {
        session_id: sessionId,
        task_index: session.length + 1,
        session_task_count: targetTaskCount,
        task_function_type: 'FOCUSED_CORE',
        domain_id: '',
        phase_context: 'PHASE_B',
        required_cognitive_depth: 'UNDERSTAND',
        time_budget_seconds: 180
      };
      
      // Try to target an active subskill first
      if (activeStates.length > 0) {
        const targetState = activeStates[Math.floor(Math.random() * activeStates.length)];
        payload.question_item = this.questionBank.getTask('', targetState.subskill_id); // Domain empty, subskill specified
      }

      // If no item found from active states, fallback to deficit candidates
      if (!payload.question_item) {
        const topCandidate = candidatePairs.length > 0 ? candidatePairs[0].domain : 'MATHEMATICS';
        let domainIdToUse = topCandidate;
        if (domainIdToUse === 'SCIENCE_EVS' || domainIdToUse === 'WORLD_KNOWLEDGE') {
          domainIdToUse = 'SCIENCE_EVS_WORLD_KNOWLEDGE';
        }
        payload.domain_id = domainIdToUse;
        payload.question_item = this.questionBank.getTask(payload.domain_id);
      }
      
      // Ultimate fallback: completely random
      if (!payload.question_item) {
        const allDomains = ['MATHEMATICS', 'ENGLISH_LANGUAGE', 'SCIENCE_EVS_WORLD_KNOWLEDGE', 'LOGICAL_REASONING', 'SEL', 'ARTS'];
        const randDomain = allDomains[Math.floor(Math.random() * allDomains.length)];
        payload.question_item = this.questionBank.getTask(randDomain);
      }

      if (payload.question_item) {
        payload.domain_id = payload.question_item.domain_id;
        payload.target_subskill_id = payload.question_item.target_subskill_id;
      }
      
      session.push(payload);
      currentTimeBudget += payload.time_budget_seconds;
      
      // Shift to avoid picking the same domain constantly
      if (candidatePairs.length > 0) {
        const shifted = candidatePairs.shift();
        if (shifted) candidatePairs.push(shifted);
      }
    }

    // STEP 4 - CLOSE
    // Metacognitive closing element can be handled in the UI
    return session;
  }
}
