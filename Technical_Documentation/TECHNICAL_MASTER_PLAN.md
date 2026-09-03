# TECHNICAL MASTER PLAN — VERSION 1.0

**Status:** Draft for Baseline Review  
**Purpose:** This document consolidates all previous architectural specifications (`APP_SPECIFICATION.md`, `architecture_and_requirements.md`) and the recent "credit card free" cross-device constraints into a single, unified source of truth. All future engineering and implementation must strictly adhere to this baseline.

---

## 1. Core Architectural Constraints

1. **Target Platforms:** A fully responsive Progressive Web App supporting all modern laptops, phones, and desktops, while ensuring it degrades gracefully enough to support legacy devices (specifically iPads running iOS 9.3.5).
2. **Cross-Device Sync:** A child must be able to play on an iPad, and later have their progress reflect on another device (e.g., a laptop or parent's phone).
3. **100% "Credit Card Free":** The entire platform must operate on a completely free, serverless architecture. No paid databases (Firebase, AWS, Heroku) and no paid hosting.
4. **Offline-First (PWA):** The app must function perfectly without an active internet connection (crucial for road trips).

---

## 2. Infrastructure & Hosting Strategy

To satisfy the "Cross-Device" and "Credit Card Free" constraints simultaneously, the architecture employs a serverless "no-code/low-code" stack:

### A. Frontend Hosting: GitHub Pages
- The Progressive Web App (PWA) will be hosted entirely on GitHub Pages.
- All static assets (HTML, CSS, JS, Audio, SVGs) are served from this free CDN.
- **Service Workers** will cache these assets locally on the device to fulfill the offline-first requirement.

### B. Backend Database: Google Sheets + Google Apps Script
- Instead of a traditional cloud database, we use a private **Google Sheet** to act as our relational database.
- A **Google Apps Script** (GAS) exposes a free `doGet`/`doPost` API endpoint (Web App URL).
- The PWA fetches and pushes JSON payloads to this endpoint.
- **Tables (Sheets):** `Profiles` (plain text for parent debugging), `MapProgress` (merged intelligently on conflict to prevent offline data loss), `TelemetryLogs` (uses anonymous UUIDs instead of names for privacy).
- **Conflict Resolution:** The GAS endpoint is responsible for intelligently merging arrays of completed nodes/stars when a device reconnects, ensuring no offline progress is overwritten by a stale online session.

### C. Curriculum & Content Delivery
- The massive Question Bank and Curriculum Map will **not** be stored in Google Sheets (to prevent API throttling and slow load times).
- A fully populated, procedurally generated Question Bank containing thousands of JSON items (along with schemas, validators, and a ledger) already exists locally in the `question_bank/` directory.
- Python scripts run at build-time to parse the markdown/JSON files and compile them into a static `curriculum_map.json`. 
- These JSON payloads are bundled with the GitHub Pages deployment and cached locally by the PWA.

---

## 3. Frontend Tech Stack

- **Core:** Vanilla TypeScript, HTML, Vanilla CSS (No large frameworks like React or Vue, which add unnecessary parsing overhead).
- **Build Tool:** Vite with `@vitejs/plugin-legacy` (targeting modern ES modules while injecting `core-js` polyfills for iOS 9 support).
- **Styling:** CSS variables, pseudo-elements, and `@supports` queries for glassmorphism. Fully responsive to adapt to laptops, desktops, and mobile screens.

---

## 4. Local Storage & Sync Architecture

To handle the "Offline-First" requirement alongside "Cross-Device Sync", the frontend employs a dual-storage pattern:

1. **Local Data Layer (WebSQL / LocalStorage):**
   - When a session starts, the app reads the user's state from the local cache.
   - During gameplay, stars earned and nodes completed are written immediately to the local cache.
   - Telemetry events (time-to-answer, hints used) are pushed to a local `TelemetryQueue`.

2. **Sync Engine (Auto-Sync with Manual Override):**
   - A background `SyncEngine` monitors the network connection (`navigator.onLine`).
   - **Online Mode (Automatic):** When online, the engine automatically flushes the local `TelemetryQueue` and `MapProgress` to the Google Apps Script API as changes occur. It also polls the API on startup to pull down any progress made on other devices.
   - **Offline Mode (Manual Override):** If the child plays offline, changes are queued locally. The user can explicitly trigger a push via the existing **"Sync Data"** button on the UI (e.g., Map Screen) when they regain connection, ensuring their offline session is safely backed up to the cloud.

---

## 5. UI Architecture & Flows

The application operates as a Single Page Application (SPA) with a single `index.html` shell. Screens are toggled via CSS classes orchestrated by a central `app.ts` router.

- **Landing Screen (`#screen-landing`):** Pure CSS space/aurora visuals. Fast-login for the last active profile.
- **Account Management (`#screen-account`):** Hidden area for parents to create/delete profiles. Profile creation now requires setting a **4-digit PIN**, which acts as the secure key for linking that profile on subsequent devices.
- **Map Screen (`#screen-map`):** A massive SVG panning engine generating dynamic paths based on the `MapProgress` state.
- **Task Runner (`#modal-task-runner`):** A glassmorphic modal overlay. The core gameplay loop. Parses the `interaction_model` from the static Question Bank and renders multi-level scaffolding.
- **Parents Dashboard (`#screen-parents`):** Consumes the telemetry/mastery data to display narrative progress. Strictly enforces the Pedagogical Master Plan Safeguards (no scores, no leaderboards, no grade-level equivalents).
- **Toybox (`#screen-sandbox`):** A custom touch/mouse drag-and-drop engine (bypassing native HTML5 drag-and-drop which fails on iOS 9).

---

## 6. Scalability & Extensibility

The architecture is designed to allow continuous evolution of both the curriculum content and the user interface without requiring fundamental rewrites.

### A. Zero-Code Curriculum Expansion
- **Decoupled Content:** The Question Bank is strictly decoupled from the codebase. Adding new subjects or advancing the curriculum (e.g., from preschool Math to 3rd-grade Math) requires zero code changes.
- **Build-Time Ingestion:** Content creators simply drop new JSON files into the `question_bank/items/` folder. The `import.meta.glob` build step automatically discovers and compiles them.
- **Silent Over-the-Air Updates:** When a new build is pushed to GitHub Pages, the Service Worker silently downloads the new JSON payload in the background. The next time the child opens the app, the new curriculum is instantly available offline.
- **Lightweight Scaling:** Because questions are stored as compressed JSON text, the app can hold tens of thousands of questions spanning years of curriculum while remaining smaller in file size than a single high-resolution image.

### B. UI Enrichment & Evolution
- **Extensible Standards:** Because the UI is built entirely in Vanilla HTML/CSS/TypeScript, it is not locked into the lifecycle of a specific framework version (like React 16 vs 18).
- **Future-Proofing:** We can continually enrich the UI (e.g., adding Speech-to-Text APIs, complex multi-level scaffolding, or richer Parent Dashboard visualizations) as long as we adhere to the core hardware constraints.
- **Performance Ceiling:** The only rigid rule for UI enhancement is respecting the legacy iPad CPU/Memory limits. Enhancements should rely on CSS hardware acceleration (transforms, opacity) rather than heavy JavaScript physics engines or WebGL.

---

## 7. Implementation Phasing

Once this Master Plan is baselined, execution will follow a strict 4-Phase sequence:

* **Phase 1 (Foundational Infrastructure):** ✅ Completed. Set up GitHub Pages, write the Google Apps Script API, and build the `SyncEngine`. Ingest the Curriculum Map into a static JSON artifact.
* **Phase 2 (Core Logic & Content):** ✅ Completed. Built the Assessment Framework logic to transition mastery stages. AdaptiveEngine now dynamically pulls from the massively populated, pre-existing Question Bank.
* **Phase 3 (Adaptive Engine & Parent UI):** ✅ Completed. Re-enabled the dynamic Adaptive Engine (targets active subskills). Built the dynamic Parents Dashboard UI hooked up to TelemetryQueue.
* **Phase 4 (Advanced UX):** ✅ Completed. Implemented graceful failure routing (skip to next question on failure) and strict session gating (0-error threshold to advance map node).
