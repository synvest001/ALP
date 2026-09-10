import { QuestionBank, QuestionItem } from './QuestionBank';
import { TaskRequestPayload } from './AdaptiveEngine';

export interface SessionRecord {
  sessionId: string;
  kidId: string;
  timestamp: number;
  itemIds: string[];
  prompts?: string[];
}

export class RepetitionGuard {
  // Strict rule: No question or prompt repeated within the same session,
  // and NO question or prompt repeated for the same kid for at least the last 5 sessions!
  public static readonly COOLDOWN_SESSION_COUNT = 5;

  public static normalizePrompt(text?: string): string {
    if (!text) return '';
    return text.toLowerCase().replace(/[^a-z0-9]/g, ' ').trim().replace(/\s+/g, ' ');
  }

  private static getStorageKey(kidId: string): string {
    const cleanId = (kidId || 'default_player').toLowerCase().trim();
    return `alp_${cleanId}_session_history`;
  }

  private static getSeenKey(kidId: string): string {
    const cleanId = (kidId || 'default_player').toLowerCase().trim();
    return `alp_${cleanId}_all_seen_items`;
  }

  /**
   * Retrieves the recent session history for a specific kid.
   */
  public static getSessionHistory(kidId: string): SessionRecord[] {
    try {
      const raw = localStorage.getItem(this.getStorageKey(kidId));
      if (!raw) return [];
      return JSON.parse(raw);
    } catch (e) {
      console.error("[RepetitionGuard] Failed to read session history:", e);
      return [];
    }
  }

  /**
   * Returns all item IDs served to this kid in their last N sessions.
   */
  public static getCooldownItemIds(kidId: string, sessionCount: number = RepetitionGuard.COOLDOWN_SESSION_COUNT): Set<string> {
    const history = this.getSessionHistory(kidId);
    const cooldownSet = new Set<string>();

    const recentSessions = history.slice(-sessionCount);
    for (const session of recentSessions) {
      for (const id of session.itemIds || []) {
        if (id) cooldownSet.add(id);
      }
    }

    return cooldownSet;
  }

  /**
   * Returns all normalized prompt texts served to this kid in their last N sessions.
   * These prompts are STRICTLY FORBIDDEN from being served again.
   */
  public static getCooldownPrompts(kidId: string, sessionCount: number = RepetitionGuard.COOLDOWN_SESSION_COUNT): Set<string> {
    const history = this.getSessionHistory(kidId);
    const cooldownPrompts = new Set<string>();

    const recentSessions = history.slice(-sessionCount);
    for (const session of recentSessions) {
      for (const prompt of session.prompts || []) {
        const norm = this.normalizePrompt(prompt);
        if (norm) cooldownPrompts.add(norm);
      }
    }

    return cooldownPrompts;
  }

  /**
   * Returns all historically seen item IDs for this kid.
   */
  public static getAllSeenItemIds(kidId: string): Set<string> {
    try {
      const raw = localStorage.getItem(this.getSeenKey(kidId));
      const list: string[] = raw ? JSON.parse(raw) : [];
      return new Set(list);
    } catch (e) {
      return new Set();
    }
  }

  /**
   * Records completed questions and their prompt texts for a kid's session.
   */
  public static recordSession(kidId: string, sessionId: string, itemIds: string[], prompts?: string[]) {
    if (!itemIds || itemIds.length === 0) return;
    const cleanId = (kidId || 'default_player').toLowerCase().trim();

    try {
      const history = this.getSessionHistory(cleanId);
      const existingIdx = history.findIndex(s => s.sessionId === sessionId);
      const cleanPrompts = prompts ? Array.from(new Set(prompts.filter(Boolean))) : [];

      if (existingIdx !== -1) {
        history[existingIdx].itemIds = Array.from(new Set([...(history[existingIdx].itemIds || []), ...itemIds]));
        if (cleanPrompts.length > 0) {
          history[existingIdx].prompts = Array.from(new Set([...(history[existingIdx].prompts || []), ...cleanPrompts]));
        }
      } else {
        history.push({
          sessionId,
          kidId: cleanId,
          timestamp: Date.now(),
          itemIds: Array.from(new Set(itemIds)),
          prompts: cleanPrompts
        });
      }

      // Limit history to 20 sessions
      const trimmedHistory = history.slice(-20);
      localStorage.setItem(this.getStorageKey(cleanId), JSON.stringify(trimmedHistory));

      // Update lifetime seen items
      const lifetime = this.getAllSeenItemIds(cleanId);
      itemIds.forEach(id => lifetime.add(id));
      localStorage.setItem(this.getSeenKey(cleanId), JSON.stringify(Array.from(lifetime)));

      console.log(`[RepetitionGuard] Recorded ${itemIds.length} items and ${cleanPrompts.length} prompts for kid '${cleanId}'.`);
    } catch (e) {
      console.error("[RepetitionGuard] Failed to record session:", e);
    }
  }

  /**
   * HARD DUAL-LAYER REPETITION ENFORCEMENT:
   * 1. Validates that NO item ID repeats within the current session.
   * 2. Validates that NO prompt text repeats within the current session.
   * 3. Validates that NO item ID or prompt text appeared in the kid's last N sessions.
   * 4. If any violation occurs, swaps with a strictly fresh, distinct question from QuestionBank.
   */
  public static validateAndEnforce(
    session: TaskRequestPayload[],
    kidId: string,
    questionBank: QuestionBank
  ): TaskRequestPayload[] {
    const cleanId = (kidId || 'default_player').toLowerCase().trim();
    const cooldownIds = this.getCooldownItemIds(cleanId, this.COOLDOWN_SESSION_COUNT);
    const cooldownPrompts = this.getCooldownPrompts(cleanId, this.COOLDOWN_SESSION_COUNT);
    const lifetimeSeen = this.getAllSeenItemIds(cleanId);

    const sessionSeenIds = new Set<string>();
    const sessionSeenPrompts = new Set<string>();
    const validatedSession: TaskRequestPayload[] = [];

    console.log(`[RepetitionGuard] Validating session for kid '${cleanId}'. Cooldown window active (${cooldownIds.size} IDs, ${cooldownPrompts.size} prompts).`);

    for (let i = 0; i < session.length; i++) {
      const task = session[i];
      let item = task.question_item;
      let promptNorm = this.normalizePrompt(item?.prompt_structure?.display_text);

      let isViolation = false;
      let violationReason = '';

      if (!item) {
        isViolation = true;
        violationReason = 'Item is null';
      } else if (sessionSeenIds.has(item.item_id)) {
        isViolation = true;
        violationReason = `Duplicate item ID '${item.item_id}' within same session`;
      } else if (promptNorm && sessionSeenPrompts.has(promptNorm)) {
        isViolation = true;
        violationReason = `Duplicate prompt text '${item.prompt_structure.display_text}' within same session (Task ${i + 1})`;
      } else if (cooldownIds.has(item.item_id)) {
        isViolation = true;
        violationReason = `Item ID '${item.item_id}' served in last ${this.COOLDOWN_SESSION_COUNT} sessions`;
      } else if (promptNorm && cooldownPrompts.has(promptNorm)) {
        isViolation = true;
        violationReason = `Prompt text '${item.prompt_structure.display_text}' served in last ${this.COOLDOWN_SESSION_COUNT} sessions`;
      }

      if (isViolation) {
        console.warn(`[RepetitionGuard] REPETITION DETECTED! ${violationReason}. Swapping with guaranteed fresh question...`);

        // Combined exclusion sets
        const allForbiddenIds = Array.from(new Set([...sessionSeenIds, ...cooldownIds, ...lifetimeSeen]));
        const allForbiddenPrompts = new Set([...sessionSeenPrompts, ...cooldownPrompts]);

        // Attempt 1: Target subskill & cognitive depth
        let freshItem: QuestionItem | null = questionBank.getTask(
          task.domain_id,
          task.target_subskill_id,
          task.required_cognitive_depth,
          allForbiddenIds,
          allForbiddenPrompts
        );

        // Attempt 2: Same domain, any subskill
        if (!freshItem || allForbiddenIds.includes(freshItem.item_id) || allForbiddenPrompts.has(this.normalizePrompt(freshItem.prompt_structure?.display_text))) {
          freshItem = questionBank.getTask(
            task.domain_id,
            undefined,
            task.required_cognitive_depth,
            allForbiddenIds,
            allForbiddenPrompts
          );
        }

        // Attempt 3: Any domain in question bank
        if (!freshItem || allForbiddenIds.includes(freshItem.item_id) || allForbiddenPrompts.has(this.normalizePrompt(freshItem.prompt_structure?.display_text))) {
          freshItem = questionBank.getTask(
            undefined,
            undefined,
            undefined,
            allForbiddenIds,
            allForbiddenPrompts
          );
        }

        if (freshItem) {
          const freshNorm = this.normalizePrompt(freshItem.prompt_structure?.display_text);
          if (!sessionSeenIds.has(freshItem.item_id) && !sessionSeenPrompts.has(freshNorm)) {
            item = freshItem;
            promptNorm = freshNorm;
            task.question_item = freshItem;
            task.domain_id = freshItem.domain_id;
            task.target_subskill_id = freshItem.target_subskill_id;
            task.required_cognitive_depth = freshItem.cognitive_depth;
            console.log(`[RepetitionGuard] Successfully swapped task ${i + 1} with fresh question: "${item.prompt_structure.display_text}" (${item.item_id}).`);
          }
        }
      }

      if (item) {
        sessionSeenIds.add(item.item_id);
        if (promptNorm) {
          sessionSeenPrompts.add(promptNorm);
        }
      }

      validatedSession.push(task);
    }

    return validatedSession;
  }
}
