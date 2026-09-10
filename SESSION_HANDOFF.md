# SESSION HANDOFF - MAGICAL KINGDOM PWA

**To the Next AI Agent / Developer:**
Do NOT rethink the architecture. Do NOT start from scratch. Do NOT suggest alternative cloud providers (like Firebase or AWS). The architecture is 100% locked, thoroughly tested, and strictly constrained to a "credit-card-free", legacy-compatible framework.

---

## 1. Executive Summary & Current State
The **Magical Kingdom Adaptive Learning Platform (ALP)** is fully functional and running locally. The platform features an offline-first, browser-based gamified learning experience with:
- **12,925 Schema-Compliant Question Items** across 5 academic domains.
- **Dual-Axis Adaptive Learning Engine** combining curriculum graph prerequisite progression with depth-first cognitive complexity escalation (`APPLY` $\to$ `REASON` $\to$ `GENERALIZE`).
- **RepetitionGuard System**: Guarantees zero intra-session question duplicates and strictly enforces a 3-session cooldown per kid profile.
- **Unpredictable Randomized Question Sampling**: Randomizes domain presentation order and subskill selection so no two kids (or sessions) experience predictable sequences.
- **Fast-Track Progression (Mastery Leap)**: Kids answering 100% correctly advance **+2 steps** on the realm path, receive **2 stars**, and accelerate their cognitive mastery transitions.
- **10 Rich Hand-Painted Map Themes**: Winding golden SVG road with interactive nodes, realm transitions, and ambient audio cues.
- **Procedural Fairy Castle Construction**: 10 progressive architectural wings rendered via vector SVG, unlocked upon completing each 5-node realm.
- **Grand Treasures Sandbox / Toybox**: 10 collectible mythical relics with rarity tiers and lore cards.
- **Full Multi-Kid Profile Isolation**: Independent progress, stars, mastery states, and session histories namespaced per player.

---

## 2. Immutable Architectural Rules
1. **Target Platforms:** Progressive Web App (PWA) supporting modern desktop and mobile browsers, plus graceful degradation for legacy devices (specifically iOS 9.3.5 iPads).
2. **Framework & Language:** Vanilla TypeScript, Vanilla CSS, and HTML. **Strictly No React, No Vue, and No TailwindCSS.**
3. **Build Tooling:** Vite with `@vitejs/plugin-legacy` (transpiles to ES5 with `core-js` polyfills).
4. **Backend Infrastructure (100% "Credit-Card Free"):**
   - Static hosting via GitHub Pages.
   - Remote database & telemetry logging via Google Sheets (Google Apps Script endpoint in `backend/apps_script.js`).
5. **Storage Architecture (Offline-First):**
   - Gameplay state and progress persist in `localStorage`.
   - All state keys are namespaced per player: `alp_${kidId}_nodes_completed`, `alp_${kidId}_stars`, `alp_${kidId}_assessment_states`, `alp_${kidId}_domain_counts`, `alp_${kidId}_cooldown_sessions`.
   - `SyncEngine.ts` handles pushing local progress and telemetry to Google Apps Script.
6. **Question Bank Architecture (Zero-Choke Public Bundles):**
   - **Never** use `import.meta.glob('../../../question_bank/items/**/*.json')` in frontend TypeScript. On Windows, 12,925 individual file handles cause OS `EMFILE` exhaustion.
   - Always load question bundles from `frontend/public/data/question_bank/` (`items_<domain>.json` and `manifest.json`), compiled by `scripts/compile_question_bank.py`.

---

## 3. Core Systems & File Map

### A. Engine & Adaptive Learning (`frontend/src/engine/`)
- [`QuestionBank.ts`](file:///c:/Users/Asus/ALP/frontend/src/engine/QuestionBank.ts): Asynchronously loads the 5 domain bundles (12,925 items) into in-memory indices. Implements intelligent fallback queries matching `(domain, subskill, cognitive_depth, excludeIds)`.
- [`CurriculumGraph.ts`](file:///c:/Users/Asus/ALP/frontend/src/engine/CurriculumGraph.ts): Parses `curriculum_map.json` (187 subskills). Manages prerequisite resolution, unlocks downstream subskills when prerequisites reach `SECURE`, and provides randomized foundational entry points.
- [`AssessmentEngine.ts`](file:///c:/Users/Asus/ALP/frontend/src/engine/AssessmentEngine.ts): Tracks learner mastery (`INTRODUCED`, `DEVELOPING`, `SECURE`, `FLEXIBLE`, `GENERALIZED`). Tracks consecutive correct streaks for fast-track progression and maps mastery states directly to cognitive depth (`APPLY`, `REASON`, `GENERALIZE`). Namespaced per kid ID.
- [`RepetitionGuard.ts`](file:///c:/Users/Asus/ALP/frontend/src/engine/RepetitionGuard.ts): Enforces intra-session uniqueness and a rolling 3-session cooldown per kid profile. Pre-flight inspects every session and automatically replaces repeated items.
- [`AdaptiveEngine.ts`](file:///c:/Users/Asus/ALP/frontend/src/engine/AdaptiveEngine.ts): Session composer that balances domain rolling deficits with high-entropy randomized shuffling, coordinates subskill selection, and builds 5-task sessions.
- [`SyncEngine.ts`](file:///c:/Users/Asus/ALP/frontend/src/engine/SyncEngine.ts): Syncs local progress and telemetry to Google Apps Script.

### B. User Interface & Gameplay (`frontend/src/ui/`)
- [`MapScreen.ts`](file:///c:/Users/Asus/ALP/frontend/src/ui/MapScreen.ts): Renders the 5-node winding realm path, golden road SVG, glowing progress nodes, realm completion ceremony, and sticky header with player avatar, name, and stars.
- [`TaskRunner.ts`](file:///c:/Users/Asus/ALP/frontend/src/ui/TaskRunner.ts): Interactive modal runner for answering questions. Handles option randomization, audio sound effects, error scaffolding, fast-track leap (+2 nodes, 2 stars) on 0 errors, and session completion celebrations.
- [`FairyCastleSvg.ts`](file:///c:/Users/Asus/ALP/frontend/src/ui/FairyCastleSvg.ts): Procedural vector SVG generator rendering 10 distinct architectural wings of the Royal Fairy Castle.
- [`ToyboxScreen.ts`](file:///c:/Users/Asus/ALP/frontend/src/ui/ToyboxScreen.ts): Grand Treasures gallery displaying 10 mythical relics unlocked through realm progression.
- [`ParentsDashboard.ts`](file:///c:/Users/Asus/ALP/frontend/src/ui/ParentsDashboard.ts): Parent briefing dashboard tracking skills explored, qualitative mastery states, and real-world conversation connections per child.
- [`LandingScreen.ts`](file:///c:/Users/Asus/ALP/frontend/src/ui/LandingScreen.ts) & [`AccountScreen.ts`](file:///c:/Users/Asus/ALP/frontend/src/ui/AccountScreen.ts): Player hero selection (Princess, Knight, Magician, Explorer) and profile management.
- [`SoundEffects.ts`](file:///c:/Users/Asus/ALP/frontend/src/ui/SoundEffects.ts): Synthesized Web Audio API sound effects (no external audio files required).

---

## 4. How to Run & Verify

### Running the Application Locally
```powershell
cd c:\Users\Asus\ALP\frontend
npm run dev
```
- Dev server will be available at: `http://localhost:5173/`

### Compiling Production Bundle
```powershell
cd c:\Users\Asus\ALP\frontend
npm run build
```
- Output generated in `frontend/dist/` with legacy polyfills for older devices.

### Automated Verification Scripts
```powershell
cd c:\Users\Asus\ALP
# 1. Type-check TypeScript codebase
npx tsc --noEmit --project frontend/tsconfig.json

# 2. Test multi-session repetition cooldown and intra-session duplicate prevention
node scripts/test_repetition_guard.js

# 3. Test multi-kid isolation, randomized domain sequences, and fast-track mastery leaps
node scripts/test_kid_progression_and_randomization.js
```

### Re-compiling the Question Bank (if items change)
```powershell
cd c:\Users\Asus\ALP
python scripts/compile_question_bank.py
```

---

## 5. Active Profile & Storage Keys
- Profiles are managed via `alp_registered_profiles`, `alp_current_name`, `alp_current_avatar`.
- Kid-specific progress keys:
  - `alp_${kidName}_nodes_completed`
  - `alp_${kidName}_stars`
  - `alp_${kidName}_assessment_states`
  - `alp_${kidName}_domain_counts`
  - `alp_${kidName}_cooldown_sessions`
- Global fallback keys (`alp_nodes_completed`, `alp_stars`, etc.) are kept in sync for single-player compatibility.

---

## 6. Immediate Next Steps / Potential Enhancements
1. **Google Sheets Sync Integration Testing**: Configure live Google Apps Script endpoint in `SyncEngine.ts` to test live remote cloud backup.
2. **Audio Narration (TTS)**: Evaluate browser-native `window.speechSynthesis` for spoken prompts on younger learner profiles.
3. **PWA Offline Service Worker Deployment**: Validate service worker asset caching when deployed to GitHub Pages.
