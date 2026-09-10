export interface DailyQuestStatus {
  count: number;
  target: number;
  completed: boolean;
  justCompleted: boolean;
  dateStr: string;
}

export class DailyQuestManager {
  public static readonly TARGET_QUESTS = 3;

  /**
   * Returns current date string formatted as YYYY-MM-DD in local time
   */
  public static getTodayStr(): string {
    const now = new Date();
    const year = now.getFullYear();
    const month = String(now.getMonth() + 1).padStart(2, '0');
    const day = String(now.getDate()).padStart(2, '0');
    return `${year}-${month}-${day}`;
  }

  /**
   * Retrieves today's daily quest status for the given child profile.
   * Resets counter to 0 if date has advanced.
   */
  public static getStatus(kidName: string): DailyQuestStatus {
    const clean = (kidName || 'default_player').toLowerCase().trim();
    const today = this.getTodayStr();
    const storedDate = localStorage.getItem(`alp_${clean}_daily_quest_date`);
    let count = 0;

    if (storedDate === today) {
      count = parseInt(localStorage.getItem(`alp_${clean}_daily_quest_count`) || '0', 10);
      if (isNaN(count)) count = 0;
    } else {
      // New day or first time initialized: reset to 0 for today
      localStorage.setItem(`alp_${clean}_daily_quest_date`, today);
      localStorage.setItem(`alp_${clean}_daily_quest_count`, '0');
      count = 0;
    }

    return {
      count: Math.min(count, this.TARGET_QUESTS),
      target: this.TARGET_QUESTS,
      completed: count >= this.TARGET_QUESTS,
      justCompleted: false,
      dateStr: today
    };
  }

  /**
   * Records a completed session / path node for the child.
   * Increments today's quest counter and identifies when 3/3 target is achieved.
   */
  public static recordSessionCompleted(kidName: string): DailyQuestStatus {
    const clean = (kidName || 'default_player').toLowerCase().trim();
    const today = this.getTodayStr();
    const storedDate = localStorage.getItem(`alp_${clean}_daily_quest_date`);

    let currentCount = 0;
    if (storedDate === today) {
      currentCount = parseInt(localStorage.getItem(`alp_${clean}_daily_quest_count`) || '0', 10);
      if (isNaN(currentCount)) currentCount = 0;
    }

    const newCount = currentCount + 1;
    const justCompleted = (currentCount < this.TARGET_QUESTS && newCount >= this.TARGET_QUESTS);

    // Save profile-specific keys
    localStorage.setItem(`alp_${clean}_daily_quest_date`, today);
    localStorage.setItem(`alp_${clean}_daily_quest_count`, newCount.toString());

    // Legacy fallback keys
    localStorage.setItem('alp_daily_quest_date', today);
    localStorage.setItem('alp_daily_quest_count', newCount.toString());

    return {
      count: Math.min(newCount, this.TARGET_QUESTS),
      target: this.TARGET_QUESTS,
      completed: newCount >= this.TARGET_QUESTS,
      justCompleted,
      dateStr: today
    };
  }

  /**
   * Resets quest progress for a specific player profile
   */
  public static resetQuest(kidName: string): void {
    const clean = (kidName || 'default_player').toLowerCase().trim();
    localStorage.removeItem(`alp_${clean}_daily_quest_date`);
    localStorage.removeItem(`alp_${clean}_daily_quest_count`);
    localStorage.removeItem('alp_daily_quest_date');
    localStorage.removeItem('alp_daily_quest_count');
  }
}
