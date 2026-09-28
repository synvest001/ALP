import { spawnSync } from 'child_process';
import fs from 'fs';
import path from 'path';
import { fileURLToPath, pathToFileURL } from 'url';

const __filename = fileURLToPath(import.meta.url);
const baseDir = path.resolve(path.dirname(__filename), '..');
const tsxLoader = pathToFileURL(path.join(baseDir, 'frontend', 'node_modules', 'tsx', 'dist', 'loader.mjs')).href;

// Self-bootstrap with tsx loader if invoked via plain node
if (!process.env._TSX_BOOTSTRAPPED) {
  const result = spawnSync(process.execPath, [
    '--import', tsxLoader,
    __filename,
    ...process.argv.slice(2)
  ], {
    stdio: 'inherit',
    env: { ...process.env, _TSX_BOOTSTRAPPED: '1' }
  });
  process.exit(result.status ?? 0);
}

// ---------------------------------------------------------------------------
// Polyfill runtime dependencies (localStorage & fetch) for headless execution
// ---------------------------------------------------------------------------
const storage = new Map();
globalThis.localStorage = {
  getItem: (key) => storage.get(key) ?? null,
  setItem: (key, val) => storage.set(key, String(val)),
  removeItem: (key) => storage.delete(key),
  clear: () => storage.clear()
};

globalThis.fetch = async (url) => {
  let urlStr = String(url).replace(/^\/?(alp\/)?/, '');
  const filePath = path.join(baseDir, 'frontend', 'public', urlStr);
  if (fs.existsSync(filePath)) {
    const data = fs.readFileSync(filePath, 'utf8');
    return { ok: true, status: 200, json: async () => JSON.parse(data) };
  }
  return { ok: false, status: 404, json: async () => ({}) };
};

(async () => {
  // ---------------------------------------------------------------------------
  // Real Production Imports (evaluated dynamically with tsx loader)
  // ---------------------------------------------------------------------------
  const { RepetitionGuard } = await import('../frontend/src/engine/RepetitionGuard.ts');
  const { QuestionBank } = await import('../frontend/src/engine/QuestionBank.ts');

  console.log("=== STEP 1: Verifying Real Production Imports & Constants ===");
  console.log(`[RepetitionGuard] Loaded real class from RepetitionGuard.ts: ${typeof RepetitionGuard}`);
  console.log(`[RepetitionGuard] COOLDOWN_SESSION_COUNT = ${RepetitionGuard.COOLDOWN_SESSION_COUNT}`);

  if (RepetitionGuard.COOLDOWN_SESSION_COUNT !== 5) {
    console.error(`FAIL: RepetitionGuard.COOLDOWN_SESSION_COUNT is ${RepetitionGuard.COOLDOWN_SESSION_COUNT}, expected 5!`);
    process.exit(1);
  }
  console.log("PASS: Cooldown boundary constant strictly verified at 5 sessions.");

  // Initialize Real QuestionBank
  console.log("\n=== STEP 2: Initializing Real QuestionBank ===");
  const questionBank = new QuestionBank();
  await questionBank.ensureLoaded();
  const loadedCount = questionBank.getLoadedCount();
  console.log(`PASS: Real QuestionBank initialized with ${loadedCount} items.`);
  if (loadedCount === 0) {
    console.error("FAIL: QuestionBank loaded 0 items!");
    process.exit(1);
  }

  const testKid = "kid_leo";

  console.log("\n=== TEST 1: Intra-Session Duplicate Prevention (IDs & Prompts) ===");
  // Fetch distinct base items from question bank
  const item1 = questionBank.getTask('MATHEMATICS', 'M-NQ-01', 'APPLY', [], new Set());
  const item2 = questionBank.getTask('ENGLISH_LANGUAGE', 'E-CC-01', 'APPLY', [item1.item_id], new Set());
  const item3 = questionBank.getTask('LOGICAL_REASONING', 'L-PC-01', 'APPLY', [item1.item_id, item2.item_id], new Set());

  // Intentionally create tasks with duplicated IDs and prompt texts
  const tasksWithDuplicate = [
    { session_id: 's1', task_index: 0, session_task_count: 5, task_function_type: 'FOCUSED_CORE', domain_id: item1.domain_id, phase_context: 'P', required_cognitive_depth: 'APPLY', time_budget_seconds: 60, question_item: item1 },
    { session_id: 's1', task_index: 1, session_task_count: 5, task_function_type: 'FOCUSED_CORE', domain_id: item2.domain_id, phase_context: 'P', required_cognitive_depth: 'APPLY', time_budget_seconds: 60, question_item: item2 },
    { session_id: 's1', task_index: 2, session_task_count: 5, task_function_type: 'FOCUSED_CORE', domain_id: item1.domain_id, phase_context: 'P', required_cognitive_depth: 'APPLY', time_budget_seconds: 60, question_item: { ...item1 } }, // DUPLICATE of task 1!
    { session_id: 's1', task_index: 3, session_task_count: 5, task_function_type: 'FOCUSED_CORE', domain_id: item3.domain_id, phase_context: 'P', required_cognitive_depth: 'APPLY', time_budget_seconds: 60, question_item: item3 },
    { session_id: 's1', task_index: 4, session_task_count: 5, task_function_type: 'FOCUSED_CORE', domain_id: item2.domain_id, phase_context: 'P', required_cognitive_depth: 'APPLY', time_budget_seconds: 60, question_item: { ...item2 } }  // DUPLICATE of task 2!
  ];

  console.log("Original session task IDs:", tasksWithDuplicate.map(t => t.question_item.item_id));
  const cleanedSession = RepetitionGuard.validateAndEnforce(tasksWithDuplicate, testKid, questionBank);
  console.log("Validated session task IDs:", cleanedSession.map(t => t.question_item.item_id));

  const uniqueIds = new Set(cleanedSession.map(t => t.question_item.item_id));
  const uniquePrompts = new Set(cleanedSession.map(t => RepetitionGuard.normalizePrompt(t.question_item.prompt_structure?.display_text)));

  if (uniqueIds.size === 5 && uniquePrompts.size === 5) {
    console.log("PASS: Intra-session duplicate test passed (5/5 strictly unique item IDs and prompt texts).");
  } else {
    console.error(`FAIL: Intra-session duplicates detected! uniqueIds=${uniqueIds.size}, uniquePrompts=${uniquePrompts.size}`);
    process.exit(1);
  }

  // Record session 1
  const session1Ids = cleanedSession.map(t => t.question_item.item_id);
  const session1Prompts = cleanedSession.map(t => t.question_item.prompt_structure?.display_text || '');
  RepetitionGuard.recordSession(testKid, "session_1", session1Ids, session1Prompts);

  console.log("\n=== TEST 2: Multi-Session Cooldown Across 5 Full Sessions ===");
  // Assert cooldown IDs initially contains all session 1 IDs
  const initialCooldown = RepetitionGuard.getCooldownItemIds(testKid, RepetitionGuard.COOLDOWN_SESSION_COUNT);
  for (const id of session1Ids) {
    if (!initialCooldown.has(id)) {
      console.error(`FAIL: Item ${id} from Session 1 not found in 5-session cooldown window!`);
      process.exit(1);
    }
  }
  console.log(`PASS: Initial cooldown window contains all ${session1Ids.length} items from Session 1.`);

  // Attempt to generate sessions 2 through 6 (all within the 5-session cooldown window)
  for (let s = 2; s <= 6; s++) {
    console.log(`\nGenerating Session ${s} for ${testKid} (within 5-session cooldown)...`);
    
    // Intentionally try to inject an item from Session 1
    const forbiddenItem = cleanedSession[0].question_item;
    const candidateTasks = [
      { session_id: `s${s}`, task_index: 0, session_task_count: 5, task_function_type: 'FOCUSED_CORE', domain_id: forbiddenItem.domain_id, phase_context: 'P', required_cognitive_depth: 'APPLY', time_budget_seconds: 60, question_item: forbiddenItem },
      { session_id: `s${s}`, task_index: 1, session_task_count: 5, task_function_type: 'FOCUSED_CORE', domain_id: 'MATHEMATICS', phase_context: 'P', required_cognitive_depth: 'APPLY', time_budget_seconds: 60, question_item: questionBank.getTask('MATHEMATICS', 'M-OP-01', 'APPLY', session1Ids) },
      { session_id: `s${s}`, task_index: 2, session_task_count: 5, task_function_type: 'FOCUSED_CORE', domain_id: 'ENGLISH_LANGUAGE', phase_context: 'P', required_cognitive_depth: 'APPLY', time_budget_seconds: 60, question_item: questionBank.getTask('ENGLISH_LANGUAGE', 'E-RF-01', 'APPLY', session1Ids) },
      { session_id: `s${s}`, task_index: 3, session_task_count: 5, task_function_type: 'FOCUSED_CORE', domain_id: 'LOGICAL_REASONING', phase_context: 'P', required_cognitive_depth: 'APPLY', time_budget_seconds: 60, question_item: questionBank.getTask('LOGICAL_REASONING', 'L-AR-01', 'APPLY', session1Ids) },
      { session_id: `s${s}`, task_index: 4, session_task_count: 5, task_function_type: 'FOCUSED_CORE', domain_id: 'SCIENCE_EVS', phase_context: 'P', required_cognitive_depth: 'APPLY', time_budget_seconds: 60, question_item: questionBank.getTask('SCIENCE_EVS', 'S-KN-01', 'APPLY', session1Ids) }
    ];

    const validated = RepetitionGuard.validateAndEnforce(candidateTasks, testKid, questionBank);
    const validatedIds = validated.map(t => t.question_item.item_id);
    const validatedPrompts = validated.map(t => t.question_item.prompt_structure?.display_text || '');
    RepetitionGuard.recordSession(testKid, `session_${s}`, validatedIds, validatedPrompts);

    // Verify that NONE of session 1's items were allowed
    const hasForbidden = validated.some(t => session1Ids.includes(t.question_item.item_id));
    if (hasForbidden) {
      console.error(`FAIL: Session ${s} included an item from Session 1 within the 5-session cooldown window!`);
      process.exit(1);
    }
    console.log(`PASS: Session ${s} is 100% clear of Session 1 items (cooldown enforced).`);
  }

  // Verification of cooldown expiration at Session 7 (after 5 sessions have elapsed)
  console.log("\nVerifying 5-session cooldown expiry at Session 7...");
  const cooldownAtSession7 = RepetitionGuard.getCooldownItemIds(testKid, RepetitionGuard.COOLDOWN_SESSION_COUNT);
  const session1ItemReEligible = !cooldownAtSession7.has(session1Ids[0]);
  if (session1ItemReEligible) {
    console.log(`PASS: Session 1 item '${session1Ids[0]}' successfully rolled out of the 5-session cooldown window for spaced retrieval.`);
  } else {
    console.error(`FAIL: Session 1 item is still locked after 5 sessions!`);
    process.exit(1);
  }

  console.log("\n=== TEST 3: Multi-Kid Profile Isolation ===");
  const otherKid = "kid_maya";
  console.log(`Generating Session 1 for ${otherKid}...`);
  // Other kid should be allowed to receive items that kid_leo saw
  const mayaTasks = [
    { session_id: 'm1', task_index: 0, session_task_count: 3, task_function_type: 'FOCUSED_CORE', domain_id: item1.domain_id, phase_context: 'P', required_cognitive_depth: 'APPLY', time_budget_seconds: 60, question_item: item1 },
    { session_id: 'm1', task_index: 1, session_task_count: 3, task_function_type: 'FOCUSED_CORE', domain_id: item2.domain_id, phase_context: 'P', required_cognitive_depth: 'APPLY', time_budget_seconds: 60, question_item: item2 },
    { session_id: 'm1', task_index: 2, session_task_count: 3, task_function_type: 'FOCUSED_CORE', domain_id: item3.domain_id, phase_context: 'P', required_cognitive_depth: 'APPLY', time_budget_seconds: 60, question_item: item3 }
  ];
  const validatedMaya = RepetitionGuard.validateAndEnforce(mayaTasks, otherKid, questionBank);
  const mayaIds = validatedMaya.map(t => t.question_item.item_id);
  if (mayaIds.includes(item1.item_id) && mayaIds.includes(item2.item_id)) {
    console.log(`PASS: Maya received tasks seen by Leo without conflict (profile isolation verified).`);
  } else {
    console.error("FAIL: Profile isolation failed, Maya was blocked from Leo's seen items!");
    process.exit(1);
  }

  console.log("\n=======================================================");
  console.log("ALL REPETITION GUARD CHECKS PASSED SUCCESSFULLY!");
  console.log("1. Zero intra-session repeats guaranteed.");
  console.log("2. 5-session cooldown strictly enforced per kid.");
  console.log("3. Independent per-kid profile isolation verified.");
  console.log("=======================================================");
})();
