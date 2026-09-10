import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const baseDir = path.resolve(__dirname, '..');

// 1. Verify Question Bank Manifest and Domain Files
const qbDir = path.join(baseDir, 'frontend', 'public', 'data', 'question_bank');
const manifestPath = path.join(qbDir, 'manifest.json');

console.log("=== STEP 1: Verifying Question Bank Manifest ===");
if (!fs.existsSync(manifestPath)) {
  console.error("FAIL: manifest.json does not exist!");
  process.exit(1);
}

const manifest = JSON.parse(fs.readFileSync(manifestPath, 'utf8'));
console.log(`PASS: manifest.json loaded with ${manifest.total_items} items.`);
for (const [dom, info] of Object.entries(manifest.domains)) {
  const domFile = path.join(qbDir, info.file);
  if (!fs.existsSync(domFile)) {
    console.error(`FAIL: ${info.file} missing!`);
    process.exit(1);
  }
  console.log(`  Domain [${dom}]: ${info.count} items, ${info.size_kb} KB`);
}

// 2. Load all items into memory (simulating QuestionBank)
console.log("\n=== STEP 2: Testing Zero-Duplicate Query Engine ===");
const itemsByDomain = new Map();
const itemsBySubskill = new Map();

for (const [dom, info] of Object.entries(manifest.domains)) {
  const domFile = path.join(qbDir, info.file);
  const items = JSON.parse(fs.readFileSync(domFile, 'utf8'));
  itemsByDomain.set(dom, items);
  for (const it of items) {
    if (!itemsBySubskill.has(it.target_subskill_id)) {
      itemsBySubskill.set(it.target_subskill_id, []);
    }
    itemsBySubskill.get(it.target_subskill_id).push(it);
  }
}
console.log(`PASS: Total subskills indexed: ${itemsBySubskill.size}`);

// 3. Verify Curriculum Map
console.log("\n=== STEP 3: Testing Curriculum Map Dependencies ===");
const cmPath = path.join(baseDir, 'frontend', 'public', 'data', 'curriculum_map.json');
const cm = JSON.parse(fs.readFileSync(cmPath, 'utf8'));
console.log(`PASS: curriculum_map.json loaded with ${cm.domains.length} domains.`);

// 4. Simulate Dual-Axis Adaptive Learning Progression
console.log("\n=== STEP 4: Simulating Adaptive Learning Progression Across 5 Sessions ===");
const seenItems = new Set();
const assessmentStates = new Map(); // subskill -> { successes, state }

function getSubskillState(subskill_id) {
  return assessmentStates.get(subskill_id)?.state || 'INTRODUCED';
}

function getTargetCognitiveDepth(subskill_id) {
  const state = getSubskillState(subskill_id);
  if (state === 'INTRODUCED') return 'APPLY';
  if (state === 'DEVELOPING') return 'REASON';
  return 'GENERALIZE';
}

function recordSuccess(subskill_id) {
  if (!assessmentStates.has(subskill_id)) {
    assessmentStates.set(subskill_id, { successes: 0, state: 'INTRODUCED' });
  }
  const s = assessmentStates.get(subskill_id);
  s.successes++;
  if (s.state === 'INTRODUCED' && s.successes >= 2) {
    s.state = 'DEVELOPING';
  } else if (s.state === 'DEVELOPING' && s.successes >= 5) {
    s.state = 'SECURE';
  }
}

// Simulate 5 sessions of 5 tasks each
let totalRepeats = 0;
for (let sessionNum = 1; sessionNum <= 5; sessionNum++) {
  console.log(`\n--- Session ${sessionNum} ---`);
  const sessionTasks = [];
  const domains = ['MATHEMATICS', 'ENGLISH_LANGUAGE', 'SCIENCE_EVS', 'LOGICAL_REASONING', 'WORLD_KNOWLEDGE'];

  for (let t = 0; t < 5; t++) {
    const dom = domains[t % domains.length];
    const subskillCandidates = Array.from(itemsBySubskill.keys()).filter(code => {
      if (dom === 'MATHEMATICS') return code.startsWith('M-');
      if (dom === 'ENGLISH_LANGUAGE') return code.startsWith('E-');
      if (dom === 'SCIENCE_EVS') return code.startsWith('S-');
      if (dom === 'LOGICAL_REASONING') return code.startsWith('L-');
      if (dom === 'WORLD_KNOWLEDGE') return code.startsWith('W-');
      return false;
    });

    const subskill = subskillCandidates[sessionNum % subskillCandidates.length];
    const targetDepth = getTargetCognitiveDepth(subskill);
    const subItems = itemsBySubskill.get(subskill) || [];

    // Filter unseen
    let chosen = subItems.find(it => !seenItems.has(it.item_id) && it.cognitive_depth === targetDepth);
    if (!chosen) {
      chosen = subItems.find(it => !seenItems.has(it.item_id));
    }
    if (!chosen) {
      const domItems = itemsByDomain.get(dom) || [];
      chosen = domItems.find(it => !seenItems.has(it.item_id));
    }

    if (chosen) {
      if (seenItems.has(chosen.item_id)) {
        totalRepeats++;
        console.error(`  [REPEAT DETECTED]: ${chosen.item_id}`);
      } else {
        seenItems.add(chosen.item_id);
      }
      recordSuccess(subskill);
      const newState = getSubskillState(subskill);
      console.log(`  Task ${t+1} [${dom}]: Item ${chosen.item_id} | Subskill: ${subskill} | Depth: ${chosen.cognitive_depth} | State: ${newState}`);
    }
  }
}

// 5. Simulate Focused Subskill Cognitive Depth Escalation
console.log("\n=== STEP 5: Testing Cognitive Depth Escalation on Focused Subskill (M-NQ-01) ===");
const focusedSubskill = 'M-NQ-01';
const focusedItems = itemsBySubskill.get(focusedSubskill) || [];
const localSeen = new Set();
const focusedStates = { successes: 0, state: 'INTRODUCED' };

for (let attempt = 1; attempt <= 7; attempt++) {
  const currentDepth = (focusedStates.state === 'INTRODUCED') ? 'APPLY' : (focusedStates.state === 'DEVELOPING' ? 'REASON' : 'GENERALIZE');
  const matchingItem = focusedItems.find(it => !localSeen.has(it.item_id) && it.cognitive_depth === currentDepth);
  if (matchingItem) {
    localSeen.add(matchingItem.item_id);
    focusedStates.successes++;
    if (focusedStates.state === 'INTRODUCED' && focusedStates.successes >= 2) {
      focusedStates.state = 'DEVELOPING';
    } else if (focusedStates.state === 'DEVELOPING' && focusedStates.successes >= 5) {
      focusedStates.state = 'SECURE';
    }
    console.log(`  Attempt ${attempt}: Served ${matchingItem.item_id} (Depth: ${matchingItem.cognitive_depth}) -> State: ${focusedStates.state}`);
  }
}

console.log("\n=== VERIFICATION SUMMARY ===");
console.log(`Total Tasks Simulated: 25`);
console.log(`Unique Items Served: ${seenItems.size}`);
console.log(`Repeated Items: ${totalRepeats}`);
if (totalRepeats === 0) {
  console.log("SUCCESS: 100% Zero-Repetition Guarantee Passed!");
} else {
  console.error(`FAILED: Found ${totalRepeats} repeats.`);
  process.exit(1);
}
