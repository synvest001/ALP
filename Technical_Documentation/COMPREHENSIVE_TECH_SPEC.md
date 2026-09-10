# Comprehensive Technical Specification (Living Document)

**Status:** Active & Production-Ready
**Purpose:** A unified, comprehensive technical specification document for the Magical Kingdom PWA. This document serves as a single source of truth for architecture, constraints, data structures, adaptive logic, and UI behaviors to assist in future debugging, onboarding, and feature enhancements.

---

## 1. System Architecture & Constraints

1. **Target Platforms:** Progressive Web App (PWA) supporting modern devices and legacy devices (specifically iOS 9.3.5 iPads).
2. **Framework & Tooling:** 
   - Core: Vanilla TypeScript, Vanilla CSS, HTML. Strictly no React, Vue, or heavy external UI frameworks.
   - Build Tool: Vite with `@vitejs/plugin-legacy` (transpiling to ES5, injecting `core-js` polyfills).
3. **Infrastructure (100% "Credit Card Free"):**
   - Frontend Hosting: GitHub Pages (Free CDN, statically hosted).
   - Backend Database: Google Sheets via Google Apps Script (GAS) API.
4. **Offline-First Design:** 
   - All assets (HTML, CSS, JS, Images, Data Bundles) cached locally.
   - Local state persists in `localStorage` with kid-specific namespacing.
   - `SyncEngine` handles pushing local telemetry and progress to Google Sheets when an internet connection is available (or via manual "Sync Data" trigger).

---

## 2. Data Models & Storage Strategy

### A. Local Storage (Frontend)
All player-specific progress is strictly namespaced by sanitized player name (`cleanKidId`):
- `alp_registered_profiles`: JSON array of created player profiles (`[{ name, avatar }]`).
- `alp_current_name` / `alp_current_avatar`: Active player's session identity.
- `alp_${kidId}_nodes_completed`: Integer representing total completed map nodes for this player.
- `alp_${kidId}_stars`: Integer representing total earned stars for this player.
- `alp_${kidId}_assessment_states`: Subskill mastery records (`{ subskill_id, state, successes, attempts, consecutive_successes, last_active }`).
- `alp_${kidId}_domain_counts`: Historical answered question count by academic domain for rolling deficit balancing.
- `alp_${kidId}_cooldown_sessions`: Rolling array of recent sessions containing answered question IDs for repetition prevention.
- `alp_nodes_completed`, `alp_stars`: Mirrored global fallback keys for single-player compatibility.

### B. Remote Storage (Google Sheets)
- **Profiles Sheet:** Plain text debugging of user profiles.
- **MapProgress Sheet:** Logs `[ProfileID, NodesCompleted, Timestamp]`.
- **TelemetryLogs Sheet:** Logs anonymous telemetry using UUIDs `[UUID, EventJSON, Timestamp]`.

### C. Static Question Bank & Curriculum Assets
- **Curriculum Map (`frontend/public/data/curriculum_map.json`):**
  - Static JSON hierarchy of 5 Domains, Strands, 187 Subskills, and prerequisite dependencies.
  - Consumed by `CurriculumGraph.ts` for unlocking downstream skills.
- **Compiled Question Bank (`frontend/public/data/question_bank/`):**
  - Pre-compiled by `scripts/compile_question_bank.py` into 5 domain bundles:
    - `items_ENGLISH_LANGUAGE.json` (2,120 items)
    - `items_LOGICAL_REASONING.json` (960 items)
    - `items_MATHEMATICS.json` (7,645 items)
    - `items_SCIENCE_EVS.json` (1,400 items)
    - `items_WORLD_KNOWLEDGE.json` (800 items)
    - `manifest.json` (12,925 indexed items)
  - Loaded into memory asynchronously by `QuestionBank.ts` without Windows `EMFILE` file handle limits.

---

## 3. Adaptive Learning Architecture (Workstream 3 Compliant)

### Axis 1: Curriculum Graph Progression
- Managed by `CurriculumGraph.ts`.
- Evaluates prerequisite nodes across the 187 subskills.
- When prerequisite subskills achieve `SECURE` mastery, downstream subskills are automatically unlocked and added to the active subskill candidate set.
- Provides randomized foundational entry points for each domain.

### Axis 2: Depth-First Cognitive Escalation
- Managed by `AssessmentEngine.ts`.
- Subskills advance through mastery states: `INTRODUCED` $\to$ `DEVELOPING` $\to$ `SECURE` $\to$ `FLEXIBLE` $\to$ `GENERALIZED`.
- Maps mastery states directly to cognitive depth:
  - `INTRODUCED` $\to$ **`APPLY`** (`LEVEL_1_SURFACE`)
  - `DEVELOPING` $\to$ **`REASON`** (`LEVEL_2_CONTEXTUAL` / `LEVEL_3_REPRESENTATIONAL`)
  - `SECURE` / `FLEXIBLE` $\to$ **`GENERALIZE`** (`LEVEL_4_STRUCTURAL`)

### Zero Repetition & Randomized Sampling
- `RepetitionGuard.ts` enforces:
  1. **Intra-session uniqueness:** No two questions in the same session can have the same item ID.
  2. **Multi-session cooldown:** No question seen in the kid's **last 3 sessions** may be presented again.
- `AdaptiveEngine.ts` randomizes domain presentation order using high-entropy rolling deficit distribution. Session task sequences are unpredictable across kids and across sessions.

### Fast-Track Progression (Mastery Leap)
- **Map Advancement:**
  - **0 Errors (Perfect Session):** Triggers a **+2 Steps Mastery Leap** and awards **2 Stars**.
  - **1 Error:** Advances +1 step and awards 1 star.
  - **2+ Errors:** Encouraging practice mode without node advance.
- **Cognitive Fast-Tracking:**
  - In `AssessmentEngine.ts`, consecutive correct answers (`consecutive_successes`) accelerate transitions:
    - 1st correct answer $\to$ `DEVELOPING` (escalates to `REASON` depth).
    - 2nd consecutive correct answer $\to$ `SECURE` (escalates to `GENERALIZE` depth and unlocks downstream curriculum skills).

---

## 4. User Interface Orchestration

### Screens & Modules
1. **Landing Screen (`LandingScreen.ts`):** Hero selection grid displaying registered player cards.
2. **Account Management (`AccountScreen.ts`):** Hero avatar picker (Princess, Knight, Magician, Explorer) and 4-digit PIN system.
3. **Map Screen (`MapScreen.ts`):**
   - Cycles through **10 high-definition hand-painted map themes** (`art/` backgrounds).
   - Winding SVG golden road connecting 5 interactive nodes per realm.
   - Dynamic sticky header greeting displaying player avatar, realm name, and stars.
   - Realm completion celebration modal.
4. **Fairy Castle Modal (`FairyCastleSvg.ts`):**
   - Visual architectural viewer rendering 10 progressive wings of the Royal Fairy Castle in procedural SVG.
   - Completing each 5-node realm constructs a new castle wing.
5. **Grand Treasures Sandbox (`ToyboxScreen.ts`):**
   - Gallery displaying 10 mythical relics (e.g. Celestial Astrolabe, Mermaid Pearl Harp, Chrono-Compass).
   - Unlocked upon completing each corresponding realm.
6. **Task Runner Modal (`TaskRunner.ts`):**
   - Modal presentation of 4-option questions with randomized button order, image option rendering, sound effects, hints, and error scaffolding.
   - Mastery Leap celebrations for perfect sessions.
7. **Parents Dashboard (`ParentsDashboard.ts`):**
   - Qualitative briefing tracking milestones completed, skills explored, mastery states, and conversational real-world connection prompts.

---

## 5. Verification & Test Suite

The platform includes automated verification scripts in `scripts/`:
- `scripts/test_repetition_guard.js`: Verifies intra-session duplicate prevention and 3-session cooldown.
- `scripts/test_kid_progression_and_randomization.js`: Verifies fast-track mastery leaps (+2 nodes, 2 stars), accelerated cognitive transitions, multi-kid profile isolation, and random domain sequencing.
- `python scripts/compile_question_bank.py`: Compiles and validates all 12,925 questions into public bundles.
- `npx tsc --noEmit`: Strict TypeScript type checking.
- `npm run build`: Production build packaging with legacy ES5 polyfills.
