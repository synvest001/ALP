// Mock LocalStorage for node environment
const storage = {};
global.localStorage = {
  getItem: (key) => (key in storage ? storage[key] : null),
  setItem: (key, val) => { storage[key] = String(val); },
  removeItem: (key) => { delete storage[key]; },
  clear: () => { Object.keys(storage).forEach(k => delete storage[k]); }
};

// Replicate DailyQuestManager logic for verification
class DailyQuestManagerTest {
  static TARGET_QUESTS = 3;

  static getTodayStr(dateOverride = null) {
    const now = dateOverride || new Date();
    const year = now.getFullYear();
    const month = String(now.getMonth() + 1).padStart(2, '0');
    const day = String(now.getDate()).padStart(2, '0');
    return `${year}-${month}-${day}`;
  }

  static getStatus(kidName, dateOverride = null) {
    const clean = (kidName || 'default_player').toLowerCase().trim();
    const today = this.getTodayStr(dateOverride);
    const storedDate = localStorage.getItem(`alp_${clean}_daily_quest_date`);
    let count = 0;

    if (storedDate === today) {
      count = parseInt(localStorage.getItem(`alp_${clean}_daily_quest_count`) || '0', 10);
      if (isNaN(count)) count = 0;
    } else {
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

  static recordSessionCompleted(kidName, dateOverride = null) {
    const clean = (kidName || 'default_player').toLowerCase().trim();
    const today = this.getTodayStr(dateOverride);
    const storedDate = localStorage.getItem(`alp_${clean}_daily_quest_date`);

    let currentCount = 0;
    if (storedDate === today) {
      currentCount = parseInt(localStorage.getItem(`alp_${clean}_daily_quest_count`) || '0', 10);
      if (isNaN(currentCount)) currentCount = 0;
    }

    const newCount = currentCount + 1;
    const justCompleted = (currentCount < this.TARGET_QUESTS && newCount >= this.TARGET_QUESTS);

    localStorage.setItem(`alp_${clean}_daily_quest_date`, today);
    localStorage.setItem(`alp_${clean}_daily_quest_count`, newCount.toString());

    return {
      count: Math.min(newCount, this.TARGET_QUESTS),
      target: this.TARGET_QUESTS,
      completed: newCount >= this.TARGET_QUESTS,
      justCompleted,
      dateStr: today
    };
  }
}

console.log('=== TEST 1: Initial State (0 / 3) ===');
const s0 = DailyQuestManagerTest.getStatus('Maya');
console.log('Maya initial quest status:', s0);
if (s0.count !== 0 || s0.completed !== false) {
  throw new Error('Initial state failed: expected 0/3, got ' + s0.count);
}
console.log('✓ PASS: Initial quest status is 0 / 3.');

console.log('\n=== TEST 2: Session Progression (1/3 -> 2/3 -> 3/3) ===');
const s1 = DailyQuestManagerTest.recordSessionCompleted('Maya');
console.log('Maya Session 1:', s1);
if (s1.count !== 1 || s1.completed !== false || s1.justCompleted !== false) {
  throw new Error('Session 1 failed: expected 1/3');
}

const s2 = DailyQuestManagerTest.recordSessionCompleted('Maya');
console.log('Maya Session 2:', s2);
if (s2.count !== 2 || s2.completed !== false || s2.justCompleted !== false) {
  throw new Error('Session 2 failed: expected 2/3');
}

const s3 = DailyQuestManagerTest.recordSessionCompleted('Maya');
console.log('Maya Session 3 (Target Reached):', s3);
if (s3.count !== 3 || s3.completed !== true || s3.justCompleted !== true) {
  throw new Error('Session 3 failed: expected 3/3 with justCompleted=true');
}
console.log('✓ PASS: Daily Quest completed after 3 sessions with justCompleted trigger.');

console.log('\n=== TEST 3: Capping Beyond Target (Session 4) ===');
const s4 = DailyQuestManagerTest.recordSessionCompleted('Maya');
console.log('Maya Session 4:', s4);
if (s4.count !== 3 || s4.completed !== true || s4.justCompleted !== false) {
  throw new Error('Session 4 failed: expected capped at 3/3 with justCompleted=false');
}
console.log('✓ PASS: Quest count cleanly capped at 3/3 without repeat completion triggers.');

console.log('\n=== TEST 4: Per-Kid Profile Isolation ===');
const bobStatus = DailyQuestManagerTest.getStatus('Bob');
console.log('Bob initial quest status (Maya has completed hers):', bobStatus);
if (bobStatus.count !== 0 || bobStatus.completed !== false) {
  throw new Error('Profile isolation failed: Bob should have 0/3');
}
console.log('✓ PASS: Maya and Bob have completely independent daily quest progress.');

console.log('\n=== TEST 5: Automatic Date Rollover (Tomorrow) ===');
const tomorrow = new Date(Date.now() + 24 * 60 * 60 * 1000);
const mayaTomorrow = DailyQuestManagerTest.getStatus('Maya', tomorrow);
console.log('Maya status tomorrow:', mayaTomorrow);
if (mayaTomorrow.count !== 0 || mayaTomorrow.completed !== false) {
  throw new Error('Date rollover failed: expected 0/3 tomorrow');
}
console.log('✓ PASS: Automatic rollover to 0/3 on next calendar day verified.');

console.log('\n=============================================');
console.log('ALL DAILY QUEST PROGRESSION TESTS PASSED! 🎉');
console.log('=============================================');
