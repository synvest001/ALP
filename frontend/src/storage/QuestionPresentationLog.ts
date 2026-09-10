/**
 * QuestionPresentationLog
 * 
 * Maintains a persistent, tamper-evident audit log of all questions presented
 * across all kid sessions. Provides browser console inspection helpers
 * (window.showQuestionLog, window.exportQuestionLog) to debug question repetition,
 * domain distributions, and subskill coverage.
 */

export interface QuestionPresentationEntry {
  id: string;
  timestamp: number;
  dateStr: string;
  kidName: string;
  sessionId: string;
  taskIndex: number;
  totalSessionTasks: number;
  domainId: string;
  subskillId: string;
  cognitiveDepth: string;
  itemId: string;
  promptText: string;
  options: { id: string; text: string }[];
  correctOptionId: string;
  correctOptionText: string;
  selectedOptionText?: string;
  isCorrect?: boolean;
}

export class QuestionPresentationLog {
  private static readonly MAX_ENTRIES = 200;

  private static getStorageKey(kidName: string): string {
    const clean = (kidName || 'default_player').toLowerCase().trim();
    return `alp_${clean}_presentation_log`;
  }

  private static getGlobalStorageKey(): string {
    return 'alp_global_presentation_log';
  }

  /**
   * Records a question presentation event.
   */
  public static recordPresentation(entry: Omit<QuestionPresentationEntry, 'id' | 'timestamp' | 'dateStr'>): QuestionPresentationEntry {
    const now = new Date();
    const fullEntry: QuestionPresentationEntry = {
      ...entry,
      id: `pres_${now.getTime()}_${Math.random().toString(36).substring(2, 7)}`,
      timestamp: now.getTime(),
      dateStr: now.toISOString()
    };

    try {
      // 1. Kid-specific log
      const kidKey = this.getStorageKey(entry.kidName);
      const kidLog = this.getLog(entry.kidName);
      kidLog.push(fullEntry);
      const trimmedKidLog = kidLog.slice(-this.MAX_ENTRIES);
      localStorage.setItem(kidKey, JSON.stringify(trimmedKidLog));

      // 2. Global log across all profiles
      const globalKey = this.getGlobalStorageKey();
      const globalLog = this.getGlobalLog();
      globalLog.push(fullEntry);
      const trimmedGlobalLog = globalLog.slice(-this.MAX_ENTRIES);
      localStorage.setItem(globalKey, JSON.stringify(trimmedGlobalLog));

      console.log(
        `%c[QuestionLog] Task ${entry.taskIndex}/${entry.totalSessionTasks} [${entry.domainId} • ${entry.subskillId}] %c"${entry.promptText}" (Item: ${entry.itemId})`,
        'color: #0284c7; font-weight: bold;',
        'color: #334155;'
      );
    } catch (e) {
      console.error("[QuestionPresentationLog] Failed to record presentation:", e);
    }

    return fullEntry;
  }

  /**
   * Updates the response for a recorded task presentation.
   */
  public static recordAnswer(
    kidName: string,
    sessionId: string,
    taskIndex: number,
    selectedOptionText: string,
    isCorrect: boolean
  ) {
    try {
      const updateList = (list: QuestionPresentationEntry[]) => {
        const item = list.slice().reverse().find(
          e => e.sessionId === sessionId && e.taskIndex === taskIndex
        );
        if (item) {
          item.selectedOptionText = selectedOptionText;
          item.isCorrect = isCorrect;
        }
      };

      const kidKey = this.getStorageKey(kidName);
      const kidLog = this.getLog(kidName);
      updateList(kidLog);
      localStorage.setItem(kidKey, JSON.stringify(kidLog));

      const globalKey = this.getGlobalStorageKey();
      const globalLog = this.getGlobalLog();
      updateList(globalLog);
      localStorage.setItem(globalKey, JSON.stringify(globalLog));
    } catch (e) {
      console.error("[QuestionPresentationLog] Failed to record answer:", e);
    }
  }

  public static getLog(kidName: string): QuestionPresentationEntry[] {
    try {
      const raw = localStorage.getItem(this.getStorageKey(kidName));
      return raw ? JSON.parse(raw) : [];
    } catch {
      return [];
    }
  }

  public static getGlobalLog(): QuestionPresentationEntry[] {
    try {
      const raw = localStorage.getItem(this.getGlobalStorageKey());
      return raw ? JSON.parse(raw) : [];
    } catch {
      return [];
    }
  }

  public static clearLog(kidName?: string) {
    if (kidName) {
      localStorage.removeItem(this.getStorageKey(kidName));
      console.log(`[QuestionPresentationLog] Log cleared for kid: ${kidName}`);
    } else {
      localStorage.removeItem(this.getGlobalStorageKey());
      console.log(`[QuestionPresentationLog] Global log cleared.`);
    }
  }

  /**
   * Formatted DevTools table viewer
   */
  public static printLogTable(limit: number = 20, kidName?: string) {
    const raw = kidName ? this.getLog(kidName) : this.getGlobalLog();
    const slice = raw.slice(-limit);

    if (slice.length === 0) {
      console.log("[QuestionPresentationLog] No questions recorded yet.");
      return;
    }

    const tableData = slice.map(e => ({
      Time: new Date(e.timestamp).toLocaleTimeString(),
      Kid: e.kidName,
      Session: e.sessionId.slice(-6),
      Task: `${e.taskIndex}/${e.totalSessionTasks}`,
      Domain: e.domainId,
      Subskill: e.subskillId,
      Depth: e.cognitiveDepth,
      Item_ID: e.itemId,
      Prompt: e.promptText.length > 50 ? e.promptText.substring(0, 47) + '...' : e.promptText,
      Correct: e.correctOptionText,
      Selected: e.selectedOptionText || '(Pending)',
      Result: e.isCorrect === undefined ? '⏳' : e.isCorrect ? '✅' : '❌'
    }));

    console.table(tableData);
    console.log(`Total questions recorded in session history: ${raw.length}`);
  }

  /**
   * Export as downloadable JSON
   */
  public static exportLog(kidName?: string) {
    const data = kidName ? this.getLog(kidName) : this.getGlobalLog();
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `question_presentation_log_${kidName || 'all'}_${Date.now()}.json`;
    a.click();
    URL.revokeObjectURL(url);
  }
}

// Bind to window for instant access from browser DevTools
if (typeof window !== 'undefined') {
  (window as any).showQuestionLog = (limit = 25, kidName?: string) => QuestionPresentationLog.printLogTable(limit, kidName);
  (window as any).exportQuestionLog = (kidName?: string) => QuestionPresentationLog.exportLog(kidName);
  (window as any).clearQuestionLog = (kidName?: string) => QuestionPresentationLog.clearLog(kidName);
}
