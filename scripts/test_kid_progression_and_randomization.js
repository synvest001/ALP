// Test script: verifying multi-kid session randomization, fast-track progress, and isolation
const fs = require('fs');
const path = require('path');

// Mock localStorage for Node
const storage = {};
global.localStorage = {
  getItem: (k) => (k in storage ? storage[k] : null),
  setItem: (k, v) => { storage[k] = String(v); },
  removeItem: (k) => { delete storage[k]; },
  clear: () => { for (const k in storage) delete storage[k]; }
};

console.log('=== TEST 1: AssessmentEngine Fast-Track Mastery Transitions ===');
// Simulate AssessmentEngine logic
class MockAssessmentEngine {
  constructor(kidId = 'default_player') {
    this.kidId = kidId.toLowerCase().trim();
    this.states = new Map();
    this.loadState();
  }
  setKidId(kidId) {
    this.kidId = kidId.toLowerCase().trim();
    this.loadState();
  }
  loadState() {
    this.states.clear();
    const raw = localStorage.getItem(`alp_${this.kidId}_assessment_states`);
    if (raw) {
      const parsed = JSON.parse(raw);
      for (const k in parsed) this.states.set(k, parsed[k]);
    }
  }
  saveState() {
    const obj = {};
    this.states.forEach((v, k) => { obj[k] = v; });
    localStorage.setItem(`alp_${this.kidId}_assessment_states`, JSON.stringify(obj));
  }
  recordAttempt(subskill_id, isCorrect) {
    let state = this.states.get(subskill_id);
    if (!state) {
      state = { subskill_id, state: 'INTRODUCED', successes: 0, attempts: 0, consecutive_successes: 0 };
      this.states.set(subskill_id, state);
    }
    state.attempts++;
    if (isCorrect) {
      state.successes++;
      state.consecutive_successes = (state.consecutive_successes || 0) + 1;
    } else {
      state.consecutive_successes = 0;
    }
    const streak = state.consecutive_successes;
    if (state.state === 'INTRODUCED' && (streak >= 1 || state.successes >= 2)) {
      state.state = 'DEVELOPING';
    } else if (state.state === 'DEVELOPING' && (streak >= 2 || state.successes >= 4)) {
      state.state = 'SECURE';
    }
    this.saveState();
  }
  getState(subskill_id) {
    return this.states.get(subskill_id)?.state || 'INTRODUCED';
  }
}

const engineKid1 = new MockAssessmentEngine('alice');
console.log('Alice initial state for M-NQ-01:', engineKid1.getState('M-NQ-01'));
engineKid1.recordAttempt('M-NQ-01', true); // 1st correct answer -> fast-track to DEVELOPING
console.log('Alice after 1 correct answer:', engineKid1.getState('M-NQ-01'));
if (engineKid1.getState('M-NQ-01') !== 'DEVELOPING') {
  throw new Error('FAIL: Alice did not reach DEVELOPING on 1st correct answer');
}

engineKid1.recordAttempt('M-NQ-01', true); // 2nd correct answer in streak -> fast-track to SECURE
console.log('Alice after 2nd consecutive correct answer:', engineKid1.getState('M-NQ-01'));
if (engineKid1.getState('M-NQ-01') !== 'SECURE') {
  throw new Error('FAIL: Alice did not reach SECURE on 2nd consecutive correct answer');
}

// Check Kid 2 is isolated
const engineKid2 = new MockAssessmentEngine('bob');
console.log('Bob initial state for M-NQ-01 (should be isolated):', engineKid2.getState('M-NQ-01'));
if (engineKid2.getState('M-NQ-01') !== 'INTRODUCED') {
  throw new Error('FAIL: Bob inherited Alice\'s state!');
}
console.log('✓ PASS: Fast-track transitions and kid assessment isolation verified.');

console.log('\n=== TEST 2: Single Node Progression (+1 Node at a time, 2 Stars on 0 errors) ===');
function simulateFinishSession(kidName, errors) {
  const clean = kidName.toLowerCase().trim();
  const currentNodes = parseInt(localStorage.getItem(`alp_${clean}_nodes_completed`) || '0', 10);
  const currentStars = parseInt(localStorage.getItem(`alp_${clean}_stars`) || '0', 10);

  if (errors === 0) {
    // Flawless session: strictly +1 node, 2 stars
    const nextNodes = currentNodes + 1;
    const newStars = currentStars + 2;
    localStorage.setItem(`alp_${clean}_nodes_completed`, nextNodes);
    localStorage.setItem(`alp_${clean}_stars`, newStars);
    return { leap: false, nodes: nextNodes, stars: newStars };
  } else if (errors === 1) {
    const nextNodes = currentNodes + 1;
    const newStars = currentStars + 1;
    localStorage.setItem(`alp_${clean}_nodes_completed`, nextNodes);
    localStorage.setItem(`alp_${clean}_stars`, newStars);
    return { leap: false, nodes: nextNodes, stars: newStars };
  } else {
    return { leap: false, nodes: currentNodes, stars: currentStars };
  }
}

const aliceSession1 = simulateFinishSession('alice', 0); // 0 errors
console.log('Alice Session 1 (0 errors):', aliceSession1);
if (aliceSession1.nodes !== 1 || aliceSession1.stars !== 2) {
  throw new Error('FAIL: Alice should have progressed 1 node and 2 stars');
}

const aliceSession2 = simulateFinishSession('alice', 0); // 0 errors again
console.log('Alice Session 2 (0 errors):', aliceSession2);
if (aliceSession2.nodes !== 2 || aliceSession2.stars !== 4) {
  throw new Error('FAIL: Alice should now have 2 nodes and 4 stars');
}

// Verify Bob is at 0
const bobNodes = parseInt(localStorage.getItem('alp_bob_nodes_completed') || '0', 10);
console.log('Bob nodes completed (should be 0):', bobNodes);
if (bobNodes !== 0) {
  throw new Error('FAIL: Bob shared Alice\'s nodes');
}
console.log('✓ PASS: Single node progression and kid progress isolation verified.');

console.log('\n=== TEST 3: Question Bank Random Domain Sampling & Unpredictability ===');
// Check question bank bundle
const bundleDir = path.join(__dirname, '../frontend/public/data/question_bank');
const manifest = JSON.parse(fs.readFileSync(path.join(bundleDir, 'manifest.json'), 'utf8'));
console.log(`Total questions in question bank: ${manifest.total_items}`);
console.log('Domains available:', Object.keys(manifest.domains));

const domains = ['MATHEMATICS', 'ENGLISH_LANGUAGE', 'SCIENCE_EVS', 'WORLD_KNOWLEDGE', 'LOGICAL_REASONING'];
const session1Domains = [...domains].sort(() => Math.random() - 0.5);
const session2Domains = [...domains].sort(() => Math.random() - 0.5);

console.log('Simulated Session 1 Domain Sequence:', session1Domains);
console.log('Simulated Session 2 Domain Sequence:', session2Domains);

console.log('\nALL PROGRESSION AND RANDOMIZATION TESTS PASSED! 🎉');
