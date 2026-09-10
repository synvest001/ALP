import { QuestionBank, QuestionItem } from './QuestionBank';
import { AssessmentEngine } from './AssessmentEngine';
import { CurriculumGraph } from './CurriculumGraph';
import { RepetitionGuard } from './RepetitionGuard';

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
  question_item?: QuestionItem | null;
}

export class SessionComposer {
  public questionBank: QuestionBank;
  public assessmentEngine: AssessmentEngine;
  public curriculumGraph: CurriculumGraph;

  constructor() {
    this.questionBank = new QuestionBank();
    this.assessmentEngine = new AssessmentEngine();
    this.curriculumGraph = new CurriculumGraph();
  }

  public async ensureReady(): Promise<void> {
    await Promise.all([
      this.questionBank.ensureLoaded(),
      this.curriculumGraph.ensureLoaded()
    ]);
  }

  /**
   * Composes a dynamic session according to Workstream 3 Dual-Axis Adaptive Design:
   * - Axis 1: Curriculum Graph progression & prerequisite unlocking
   * - Axis 2: Depth-First cognitive complexity escalation (APPLY -> REASON -> GENERALIZE)
   * - Fixed domain ratio in mixed mode: 40% Mathematics (4 tasks), 20% English (2 tasks), 20% Logic (2 tasks), 10% Science (1 task), 10% World Knowledge (1 task)
   * - Multi-strand rotation: distinct subskills per domain to prevent subskill lock-in
   * - Zero question repetitions via RepetitionGuard (cooldown across last 5 sessions + intra-session uniqueness)
   */
  public generateSession(kidId: string = 'default_player', focusedDomain?: string): TaskRequestPayload[] {
    const cleanKidId = (kidId || 'default_player').toLowerCase().trim();
    this.assessmentEngine.setKidId(cleanKidId);

    const session: TaskRequestPayload[] = [];
    const sessionId = `sess_${new Date().toISOString().replace(/[:.-]/g, '')}`;
    const targetTaskCount = 10; // Standard 10 tasks per node
    const maxTimeBudgetSeconds = 40 * 60; // Increased time budget
    let currentTimeBudget = 0;

    // Load kid-specific cooldown items & prompts (last 5 sessions)
    const cooldownIds = RepetitionGuard.getCooldownItemIds(cleanKidId, RepetitionGuard.COOLDOWN_SESSION_COUNT);
    const cooldownPrompts = RepetitionGuard.getCooldownPrompts(cleanKidId, RepetitionGuard.COOLDOWN_SESSION_COUNT);
    // Rely on the 5-session cooldown window alone to allow spaced-retrieval re-use of items.
    // lifetimeSeen is retained for reporting/analytics, not for session exclusion.
    const forbiddenBase = new Set([...cooldownIds]);
    const sessionSeenPrompts = new Set<string>();

    // 1. Get real learner states
    const secureSubskills = this.assessmentEngine.getSecureSubskills();
    const activeSubskills = this.assessmentEngine.getActiveSubskills();

    // 2. Build balanced domain sequence:
    let domainSlots: string[] = [];
    
    if (focusedDomain) {
      const domains = focusedDomain.split(',');
      domainSlots = Array.from({ length: targetTaskCount }, (_, i) => domains[i % domains.length]);
    } else {
      // Core rule: Fixed ratio for mixed adventure mode (10 slots)
      // 40% Mathematics (4 tasks), 20% English (2 tasks), 20% Logical Reasoning (2 tasks),
      // 10% Science (1 task), 10% World Knowledge (1 task)
      domainSlots = [
        'MATHEMATICS',
        'MATHEMATICS',
        'MATHEMATICS',
        'MATHEMATICS',
        'ENGLISH_LANGUAGE',
        'ENGLISH_LANGUAGE',
        'LOGICAL_REASONING',
        'LOGICAL_REASONING',
        'SCIENCE_EVS',
        'WORLD_KNOWLEDGE'
      ];
    }

    // High entropy shuffle ensures unpredictable sequence order across sessions and kids
    const domainPool = domainSlots.sort(() => Math.random() - 0.5);

    // 3. Ensure we have a healthy pool of active subskills across multiple strands (at least 3-4 per domain)
    const activeSet = new Set(activeSubskills);

    for (const dom of ['MATHEMATICS', 'ENGLISH_LANGUAGE', 'SCIENCE_EVS', 'WORLD_KNOWLEDGE', 'LOGICAL_REASONING']) {
      const currentDomainActive = Array.from(activeSet).filter(
        code => this.curriculumGraph.getDomainForSubskill(code) === dom
      );
      if (currentDomainActive.length < 3) {
        const needed = 3 - currentDomainActive.length;
        const nextSubskills = this.curriculumGraph.getNextProgressiveSubskills(dom, secureSubskills, activeSet, needed);
        for (const s of nextSubskills) {
          activeSet.add(s);
        }
      }
    }

    // 4. Fill Session Budget with Dual-Axis Progression
    let domainCycleIndex = 0;
    while (session.length < targetTaskCount && currentTimeBudget < maxTimeBudgetSeconds) {
      const targetDomain = domainPool[domainCycleIndex % domainPool.length];
      domainCycleIndex++;

      // Axis 1: Find an appropriate progressive subskill in this domain
      const domainActiveSubskills = Array.from(activeSet).filter(
        code => this.curriculumGraph.getDomainForSubskill(code) === targetDomain
      );

      // Intra-session variety: do not repeat the same subskill in the same session if alternatives exist
      const usedSubskillsInSession = new Set(session.map(t => t.target_subskill_id).filter(Boolean));
      const freshSubskills = domainActiveSubskills.filter(s => !usedSubskillsInSession.has(s));
      const subskillCandidates = freshSubskills.length > 0 ? freshSubskills : domainActiveSubskills;

      let targetSubskillId: string | undefined;
      if (subskillCandidates.length > 0) {
        targetSubskillId = subskillCandidates[Math.floor(Math.random() * subskillCandidates.length)];
      } else {
        // Fall back to foundational entry points
        const entries = this.curriculumGraph.getEntryPoints(targetDomain);
        const freshEntries = entries.filter(s => !usedSubskillsInSession.has(s));
        const entryCandidates = freshEntries.length > 0 ? freshEntries : entries;
        targetSubskillId = entryCandidates[Math.floor(Math.random() * entryCandidates.length)];
      }

      // Axis 2: Depth-First cognitive depth determination
      const targetDepth = this.assessmentEngine.getTargetCognitiveDepth(targetSubskillId);

      // Determine task function type
      const state = targetSubskillId ? this.assessmentEngine.getSubskillState(targetSubskillId) : 'INTRODUCED';
      let functionType = 'FOCUSED_CORE';
      if (state === 'DEVELOPING') functionType = 'CONSOLIDATION';
      else if (state === 'SECURE' || state === 'FLEXIBLE') functionType = 'RETRIEVAL';

      const payload: TaskRequestPayload = {
        session_id: sessionId,
        task_index: session.length + 1,
        session_task_count: targetTaskCount,
        task_function_type: functionType,
        target_subskill_id: targetSubskillId,
        domain_id: targetDomain,
        phase_context: 'PHASE_A',
        required_cognitive_depth: targetDepth,
        time_budget_seconds: 120
      };

      const currentSessionIds = session.map(p => p.question_item?.item_id).filter(Boolean) as string[];
      const excludeIds = Array.from(new Set([...forbiddenBase, ...currentSessionIds]));
      const allExcludePrompts = new Set([...cooldownPrompts, ...sessionSeenPrompts]);

      payload.question_item = this.questionBank.getTask(
        payload.domain_id,
        payload.target_subskill_id,
        targetDepth,
        excludeIds,
        allExcludePrompts
      );

      // If no question found for that specific subskill/depth, relax subskill to domain
      if (!payload.question_item) {
        payload.question_item = this.questionBank.getTask(
          payload.domain_id,
          undefined,
          undefined,
          excludeIds,
          allExcludePrompts
        );
      }

      // If still none, get literally any unseen item from question bank
      if (!payload.question_item) {
        payload.question_item = this.questionBank.getTask(
          undefined,
          undefined,
          undefined,
          excludeIds,
          allExcludePrompts
        );
      }

      if (payload.question_item) {
        payload.domain_id = payload.question_item.domain_id;
        payload.target_subskill_id = payload.question_item.target_subskill_id;
        payload.required_cognitive_depth = payload.question_item.cognitive_depth;
        const norm = RepetitionGuard.normalizePrompt(payload.question_item.prompt_structure?.display_text);
        if (norm) {
          sessionSeenPrompts.add(norm);
        }
      }

      session.push(payload);
      currentTimeBudget += payload.time_budget_seconds;
    }

    // THE HARD CHECK IN PLACE: Enforce 0 intra-session duplicates & 0 repeats in last 3 sessions
    return RepetitionGuard.validateAndEnforce(session, cleanKidId, this.questionBank);
  }
}
