# Comprehensive Technical Specification (Living Document)

**Status:** Active Draft (Updated as built)
**Purpose:** A unified, comprehensive technical specification document for the Magical Kingdom PWA. This document serves as a single source of truth for architecture, constraints, data structures, and UI behaviors to assist in future debugging, onboarding, and feature enhancements.

---

## 1. System Architecture & Constraints

1. **Target Platforms:** Progressive Web App (PWA) supporting modern devices and legacy devices (specifically iOS 9.3.5 iPads).
2. **Framework & Tooling:** 
   - Core: Vanilla TypeScript, Vanilla CSS, HTML. No React, Vue, or heavy frameworks.
   - Build Tool: Vite with `@vitejs/plugin-legacy` (transpiling to ES5, injecting `core-js` polyfills).
3. **Infrastructure (100% "Credit Card Free"):**
   - Frontend Hosting: GitHub Pages (Free CDN, statically hosted).
   - Backend Database: Google Sheets via Google Apps Script (GAS) API.
4. **Offline-First Design:** 
   - All assets (HTML, CSS, JS, Images) cached via Service Workers.
   - Local state persists in `localStorage` and `WebSQL`.
   - `SyncEngine` handles pushing local telemetry and progress to Google Sheets when an internet connection is available (or via manual "Sync Data" trigger).

---

## 2. Data Models & Storage Strategy

### A. Local Storage (Frontend)
- `alp_registered_profiles`: JSON array of created users.
- `alp_current_name` / `alp_current_avatar`: Active player's session identity.
- `alp_nodes_completed`: Integer representing the absolute total of completed nodes across all gameplay.
- `alp_stars`: Integer representing total earned stars.

### B. Remote Storage (Google Sheets)
- **Profiles Sheet:** Plain text debugging of user profiles.
- **MapProgress Sheet:** Logs `[ProfileID, NodesCompleted, Timestamp]`. The backend must eventually merge this data intelligently to resolve cross-device sync conflicts.
- **TelemetryLogs Sheet:** Logs anonymous telemetry using UUIDs `[UUID, EventJSON, Timestamp]`. 

### C. Static JSON Artifacts
- **Curriculum Map (`frontend/public/data/curriculum_map.json`):** 
  - Generated at build-time by the Python ingestion script (`scripts/ingest_curriculum_map.py`). 
  - Parses `WS1_CURRICULUM_MAP___VERSION_1_0.md` into a structured hierarchy of Domains, Strands, Skills, and Prerequisites.
- **Question Bank (`question_bank/`):**
  - Fully populated offline repository containing thousands of procedurally generated JSON items structured by subskill IDs (e.g. `items/W-KA-05/ITEM-W-KA-05-0001.json`).
  - Contains its own validation layer (`validators/stage1_compliance_validator.py`), frozen JSON schema (`schema/question_specification_v1_3_0.json`), and review ledger (`ledger/validation_ledger.jsonl`).
  - `TaskRunner` and `AdaptiveEngine` dynamically pull from this repository for session composition.

---

## 3. User Interface (UI) Orchestration

The app uses a Single Page Application (SPA) shell in `index.html`. UI screens are absolutely positioned containers toggled via CSS `.active` classes by the `app.ts` router.

### Theming & Visuals
- Heavy use of CSS variables (`--primary`, `--secondary`, `--bg-color`).
- Glassmorphism applied with `@supports (backdrop-filter)` for older browser degradation.

### Screens & Logic
1. **Landing Screen (`#screen-landing`):** CSS animated space void. Prompts user login via Profile cards.
2. **Account Management (`#screen-account`):** Avatar selection (Princess, Knight, Magician, Explorer) and a 4-digit PIN system for cross-device linking.
3. **Map Screen (`#screen-map`):** 
   - **Background Logic:** Cycles through 18 unique environment map sets (e.g., Magical Forest, Crystal Cave, Candy Canyon).
   - **Progression Rule:** A "World" consists of a full visual map of **10 nodes**. 
   - When 10 nodes are completed, the background dynamically advances to the next environment in the sequence, and the visual path resets to 0 for the new world.
   - **Dynamic Greeting:** The sticky header updates to greet the player using the name of the current world background (e.g., "Welcome, Royal Highness Princess to Candy Canyon!").
4. **Task Runner (`#modal-task-runner`):** A glassmorphic modal overlay displaying 4-option questions, hints, and visual scaffolding. Contains logic for incorrect shake animations and correct pulse animations.
5. **Parents Dashboard (`#screen-parents`):** A professional SaaS-style dashboard displaying curriculum mastery, daily quests, and insights (currently populated with static UI placeholders).
6. **Toybox (`#screen-sandbox`):** A drag-and-drop sticker reward zone using custom touch/mouse listeners to bypass native HTML5 drag/drop limitations on iOS 9.

---

## 4. Backend Endpoints (Google Apps Script)

Located in `backend/apps_script.js`, the GAS endpoint acts as the REST API using `doGet(e)` and `doPost(e)`.

**Supported POST Actions:**
- `SYNC_PROGRESS`: Receives `profileId`, `nodesCompleted`, and `timestamp` to update the MapProgress sheet.
- `LOG_TELEMETRY`: Receives anonymous `uuid` and `events` array to push to the TelemetryLogs sheet.
- `GET_PROFILE`: (Stub) Will handle cross-device profile retrieval using the PIN system.

---

## 5. Ongoing Implementation Phases

1. **Phase 1 (Foundational Infrastructure):** ✅ Completed. Ingestion pipeline script created; Google Apps Script draft written.
2. **Phase 2 (Core Logic & Content):** ✅ Completed. Assessment framework logic, 5-stage mastery engine, and dynamic AdaptiveEngine connected to the massively populated Question Bank repository.
3. **Phase 3 (Adaptive Engine & Parent UI):** ✅ Completed. Wired up offline telemetry and built dynamic parents dashboard UI.
4. **Phase 4 (Advanced UX):** ✅ Completed. Implemented graceful failure routing and strict 0-error map progression gating.

*(Note: This document should be continuously updated as new files are created, data schemas are solidified, or architectural decisions are made.)*
