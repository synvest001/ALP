# SESSION HANDOFF - READ ME FIRST

**To the Next AI Agent:**
Do NOT rethink the architecture. Do NOT start from scratch. Do NOT suggest alternative cloud providers (like Firebase or AWS). The architecture is 100% locked and strictly constrained to a "credit-card-free", legacy-compatible framework.

## 1. Current State
- The `TECHNICAL_MASTER_PLAN.md` has been finalized and locked. It is located in `Technical_Documentation/`.
- The entire project codebase (including the massive `question_bank` and pedagogical `Workstreams`) has been pushed to a private GitHub repository (`synvest001/ALP`).
- The project is now fully baselined and ready for active coding.

## 2. Immutable Architectural Rules
1. **Target:** Progressive Web App supporting all modern devices AND degrading gracefully to run on legacy iOS 9.3.5 iPads.
2. **Framework:** Vanilla TypeScript, Vanilla CSS, Vite (with `@vitejs/plugin-legacy` for ES5 transpilations). No React, No Vue.
3. **Backend:** Google Sheets (via Google Apps Script API) for remote sync, and GitHub Pages for free static hosting.
4. **Storage:** "Offline-First". Gameplay saves locally via WebSQL/LocalStorage. Syncing to Google Sheets is handled by a background `SyncEngine` (with a manual override "Sync Data" button).
5. **Privacy/Security:** Profiles require a 4-digit PIN for cross-device linking. Telemetry logs use anonymous UUIDs instead of names.

## 3. The Immediate Next Step (Where to begin)
You must immediately begin executing **Phase 1 (Foundational Infrastructure)** as outlined in the Master Plan. 

Your first coding tasks are:
1. Write the Python script (`scripts/ingest_curriculum_map.py`) to parse the `WS1_CURRICULUM_MAP___VERSION_1_0.md` and convert the curriculum graph into a static `frontend/public/data/curriculum_map.json` artifact for the app to consume.
2. Draft the initial `apps_script.js` code that will run on Google Apps Script to serve as the `GET`/`POST` endpoint for our Google Sheets database.

**Instruction:** Acknowledge this handoff document and begin Phase 1.
