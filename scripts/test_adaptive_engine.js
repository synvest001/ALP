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
  // Real Production Imports (SessionComposer from AdaptiveEngine.ts)
  // ---------------------------------------------------------------------------
  const { SessionComposer } = await import('../frontend/src/engine/AdaptiveEngine.ts');
  const { RepetitionGuard } = await import('../frontend/src/engine/RepetitionGuard.ts');

  console.log("=== STEP 1: Initializing Real SessionComposer & Production Guards ===");
  const composer = new SessionComposer();
  await composer.ensureReady();

  // Assertion: questionBank.getLoadedCount() and curriculumGraph.isGraphLoaded are real guards
  const loadedCount = composer.questionBank.getLoadedCount();
  const isGraphLoaded = composer.curriculumGraph.isGraphLoaded;

  console.log(`[QuestionBank] questionBank.getLoadedCount() = ${loadedCount}`);
  console.log(`[CurriculumGraph] curriculumGraph.isGraphLoaded = ${isGraphLoaded}`);

  if (typeof loadedCount !== 'number' || loadedCount <= 0) {
    console.error(`FAIL: questionBank.getLoadedCount() returned invalid count: ${loadedCount}`);
    process.exit(1);
  }
  if (isGraphLoaded !== true) {
    console.error(`FAIL: curriculumGraph.isGraphLoaded is not true!`);
    process.exit(1);
  }
  console.log(`PASS: Real guards verified against real local dataset (${loadedCount} questions loaded, graph active).`);

  // ---------------------------------------------------------------------------
  // STEP 2: Fixed 40/20/20/10/10 Domain Ratio Assertion on Real generateSession()
  // ---------------------------------------------------------------------------
  console.log("\n=== STEP 2: Testing Fixed 40/20/20/10/10 Domain Ratio on Real Output ===");
  const testKid = "kid_ratio_audit";
  const session = composer.generateSession(testKid);

  console.log(`Generated session task count: ${session.length}`);
  if (session.length !== 10) {
    console.error(`FAIL: Expected standard 10 tasks in session, got ${session.length}`);
    process.exit(1);
  }

  const domainCounts = {
    MATHEMATICS: session.filter(t => t.domain_id === 'MATHEMATICS').length,
    ENGLISH_LANGUAGE: session.filter(t => t.domain_id === 'ENGLISH_LANGUAGE').length,
    LOGICAL_REASONING: session.filter(t => t.domain_id === 'LOGICAL_REASONING').length,
    SCIENCE_EVS: session.filter(t => t.domain_id === 'SCIENCE_EVS').length,
    WORLD_KNOWLEDGE: session.filter(t => t.domain_id === 'WORLD_KNOWLEDGE').length
  };

  console.log("Measured Session Domain Distribution:");
  console.log(`  - MATHEMATICS:       ${domainCounts.MATHEMATICS} / 10 (${domainCounts.MATHEMATICS * 10}%)`);
  console.log(`  - ENGLISH_LANGUAGE:  ${domainCounts.ENGLISH_LANGUAGE} / 10 (${domainCounts.ENGLISH_LANGUAGE * 10}%)`);
  console.log(`  - LOGICAL_REASONING: ${domainCounts.LOGICAL_REASONING} / 10 (${domainCounts.LOGICAL_REASONING * 10}%)`);
  console.log(`  - SCIENCE_EVS:       ${domainCounts.SCIENCE_EVS} / 10 (${domainCounts.SCIENCE_EVS * 10}%)`);
  console.log(`  - WORLD_KNOWLEDGE:   ${domainCounts.WORLD_KNOWLEDGE} / 10 (${domainCounts.WORLD_KNOWLEDGE * 10}%)`);

  if (
    domainCounts.MATHEMATICS !== 4 ||
    domainCounts.ENGLISH_LANGUAGE !== 2 ||
    domainCounts.LOGICAL_REASONING !== 2 ||
    domainCounts.SCIENCE_EVS !== 1 ||
    domainCounts.WORLD_KNOWLEDGE !== 1
  ) {
    console.error("FAIL: Domain ratio did not match fixed 40% Math, 20% English, 20% Logic, 10% Science, 10% World Knowledge!");
    process.exit(1);
  }
  console.log("PASS: Fixed 40/20/20/10/10 ratio verified directly against SessionComposer.generateSession().");

  // ---------------------------------------------------------------------------
  // STEP 3: Prompt-TEXT Collision Assertion Across Generated Session
  // ---------------------------------------------------------------------------
  console.log("\n=== STEP 3: Asserting Prompt-TEXT Collision Across Session Tasks ===");
  const itemIds = session.map(t => t.question_item?.item_id).filter(Boolean);
  const promptTexts = session.map(t => RepetitionGuard.normalizePrompt(t.question_item?.prompt_structure?.display_text)).filter(Boolean);

  console.log(`Total valid tasks with items: ${itemIds.length}`);
  console.log(`Total normalized prompt texts: ${promptTexts.length}`);

  const uniqueItemIds = new Set(itemIds);
  const uniquePromptTexts = new Set(promptTexts);

  if (uniqueItemIds.size !== 10) {
    console.error(`FAIL: Item ID collision detected within session! Unique IDs: ${uniqueItemIds.size}/10`);
    process.exit(1);
  }
  if (uniquePromptTexts.size !== 10) {
    console.error(`FAIL: Prompt TEXT collision detected within session! Unique Prompts: ${uniquePromptTexts.size}/10`);
    process.exit(1);
  }
  console.log("PASS: 10/10 tasks have strictly unique item IDs AND strictly unique prompt texts.");

  // ---------------------------------------------------------------------------
  // STEP 4: Simulating 5 Real Multi-Session Progressions with Cooldown Enforcement
  // ---------------------------------------------------------------------------
  console.log("\n=== STEP 4: Simulating 5 Multi-Session Progressions with Real Cooldown ===");
  const progKid = "kid_progression_audit";
  const allEncounteredPrompts = new Set();
  const allEncounteredIds = new Set();

  for (let s = 1; s <= 5; s++) {
    const sess = composer.generateSession(progKid);
    const sIds = sess.map(t => t.question_item.item_id);
    const sPrompts = sess.map(t => t.question_item.prompt_structure?.display_text || '');
    
    // Check for collisions against all previous sessions
    for (let i = 0; i < sess.length; i++) {
      const id = sIds[i];
      const normPrompt = RepetitionGuard.normalizePrompt(sPrompts[i]);
      if (allEncounteredIds.has(id)) {
        console.error(`FAIL: Item ID '${id}' repeated in Session ${s}!`);
        process.exit(1);
      }
      if (allEncounteredPrompts.has(normPrompt)) {
        console.error(`FAIL: Prompt text '${sPrompts[i]}' repeated in Session ${s}!`);
        process.exit(1);
      }
      allEncounteredIds.add(id);
      allEncounteredPrompts.add(normPrompt);
    }

    // Record session into RepetitionGuard history
    RepetitionGuard.recordSession(progKid, `session_${s}`, sIds, sPrompts);
    console.log(`  Session ${s}: 10/10 tasks served with 0 ID or prompt repeats (total unique: ${allEncounteredIds.size}).`);
  }
  console.log("PASS: 50 total tasks across 5 consecutive sessions served with 0 repetitions.");

  // ---------------------------------------------------------------------------
  // STEP 5: Testing Real 3-Tier Fallback Chain in QuestionBank.getTask()
  // ---------------------------------------------------------------------------
  console.log("\n=== STEP 5: Testing Real 3-Tier Fallback Chain in QuestionBank.getTask() ===");
  
  // Collect all unique prompts in WORLD_KNOWLEDGE to exhaust the prompt filter
  const wkItems = composer.questionBank['itemsByDomain'].get('WORLD_KNOWLEDGE') || [];
  const allWkPrompts = new Set(wkItems.map(it => RepetitionGuard.normalizePrompt(it.prompt_structure?.display_text)));
  console.log(`Exhaustion Setup: Populating excludePrompts with all ${allWkPrompts.size} unique prompts for WORLD_KNOWLEDGE.`);

  let capturedWarning = null;
  const originalWarn = console.warn;
  console.warn = (...args) => {
    capturedWarning = args.join(' ');
    originalWarn(...args);
  };

  // Tier 1 & 2 fail because prompts are exhausted; triggers Tier 3 Step 7 Domain Affinity Guard
  const fallbackItem = composer.questionBank.getTask('WORLD_KNOWLEDGE', 'W-KP-01', 'APPLY', [], allWkPrompts);
  console.warn = originalWarn;

  if (!fallbackItem) {
    console.error("FAIL: QuestionBank.getTask() returned null when fallback was required!");
    process.exit(1);
  }

  if (fallbackItem.domain_id !== 'WORLD_KNOWLEDGE') {
    console.error(`FAIL: Fallback item leaked domain: expected WORLD_KNOWLEDGE, got ${fallbackItem.domain_id}`);
    process.exit(1);
  }

  if (!capturedWarning || !capturedWarning.includes("Domain Affinity Guard fallback: exhausted unique prompts for domain 'WORLD_KNOWLEDGE'")) {
    console.error(`FAIL: Expected real telemetry warning from Step 7 domain affinity fallback, got: ${capturedWarning}`);
    process.exit(1);
  }
  console.log(`PASS: Real QuestionBank fallback chain executed successfully.`);
  console.log(`  -> Fallback served item: ${fallbackItem.item_id}`);
  console.log(`  -> Telemetry verified: "${capturedWarning}"`);

  console.log("\n=======================================================");
  console.log("ALL REAL PRODUCTION ADAPTIVE ENGINE TESTS PASSED!");
  console.log("1. questionBank.getLoadedCount() and curriculumGraph.isGraphLoaded verified.");
  console.log("2. 40/20/20/10/10 domain ratio verified against real SessionComposer.");
  console.log("3. Prompt-TEXT collision verified (0 collisions).");
  console.log("4. 5-session multi-session cooldown verified on real session generation.");
  console.log("5. Real QuestionBank 3-tier fallback chain verified with real telemetry.");
  console.log("=======================================================");
})();
