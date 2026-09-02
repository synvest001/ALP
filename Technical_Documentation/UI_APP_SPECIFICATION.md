# Magical Kingdom PWA - App Specification

## Table of Contents
1. [Product & Design](#1-product--design)
2. [Technical Architecture](#2-technical-architecture)
3. [Docs vs. Implementation Discrepancies](#3-docs-vs-implementation-discrepancies)
4. [Gaps & Unknowns](#4-gaps--unknowns)

---

## 1. Product & Design

### What the App Is, Who It's For, and Platforms
The "Magical Kingdom" is an educational Progressive Web App (PWA) designed primarily for children, offering a gamified curriculum delivery system. It includes a dedicated tracking dashboard for parents. 
**Target Platform:** The app is explicitly configured to run on legacy devices, specifically iPads running iOS 9.3.5 (Safari), while functioning on modern browsers.

### User-Facing Screens and Flows
The application consists of a single HTML shell (`index.html`) with absolute-positioned `.screen` containers that are toggled via CSS classes.

#### 1. Landing Screen (`#screen-landing`)
*   **Visuals:** A deep, immersive animated space void created using pure CSS (radial gradients and an animated pseudo-element creating an aurora borealis effect).
*   **Layout:** Centralized text ("Magical Kingdom - Choose Your Hero..."). Below the text, a profile card displays the last active player's avatar and name. If no profiles exist, a prompt directs users to Account Management.
*   **Interactions:** Clicking the profile card logs the user in and navigates to the Map Screen. Two admin buttons in the top right corner (glassmorphic styling) navigate to "Parents Area" and "Account Mgmt".

#### 2. Account Management Screen (`#screen-account`)
*   **Visuals:** Dark theme (`#1a1a2e`) with glassmorphic cards and glowing borders.
*   **Layout:** Header with title and "Back" button. Main body contains a "Create New Profile" card and a list of existing profiles.
*   **Interactions:** 
    *   **Create Profile:** Clicking "Create New Profile" expands a form with a text input and a grid of four available avatars (Princess, Knight, Magician, Explorer). Selecting an avatar saves the profile and navigates back to the landing screen.
    *   **Manage Profiles:** Existing profiles list their avatar, name, and two actions: "Reset Progress" and "Delete". Both actions have native `confirm()` alerts before executing.

#### 3. Map Screen (`#screen-map`)
*   **Visuals:** A dark, space-like scrollable container (`#1a1a2e`). 
*   **Layout:** A sticky header displays the avatar, customized greeting, current level, star count, daily quest progress, and action buttons ("Treasures", "Sync Data", "Logout"). The body contains a massive 1000x4000 SVG map.
*   **Interactions:** The map generates 10 sequential nodes connected by a dashed SVG path. Completed nodes are green with a star (⭐). The current active node pulses yellow with an exclamation mark (!). Locked nodes are grey (🔒). Clicking the active node triggers an alert (placeholder for opening the Task Runner).

#### 4. Task Runner Modal (`#modal-task-runner`)
*   **Visuals:** A glassmorphic modal centered over the screen.
*   **Layout:** Header with progress indicator (e.g., "Task 1 of 5") and "Quit" button. Body contains a prompt, visual area (large emoji), and a 2x2 grid of chunky answer buttons. A scaffolding hint container is hidden below the visual.
*   **Interactions:** Clicking a correct answer turns the button green with a pulse animation, waits 1 second, and advances to the next task. Clicking an incorrect answer shakes the button, turns it red, disables all buttons for 2 seconds, and reveals the hint text.

#### 5. Parents Dashboard (`#screen-parents`)
*   **Visuals:** Sleek dark mode mimicking professional SaaS tools.
*   **Layout:** Header displays the active player's name. Main body contains an Executive Summary (KPIs), Curriculum Mastery (progress bars), Actionable Insights (text alerts), and Global Benchmarks (PISA equivalence).
*   **Interactions:** Completely static display of hardcoded placeholder data. "Back to Game" button returns to the previous state.

#### 6. Toybox Screen (`#screen-sandbox`)
*   **Visuals:** Split layout. Left sidebar (toolbar) is semi-transparent dark. Right area is the "interactive area" with a magical forest background.
*   **Layout:** Sidebar contains vertical buttons for each unlocked sticker. The interactive area is a drop zone.
*   **Interactions:** Clicking a sticker in the sidebar spawns it at a random position in the interactive area. The stickers can be dragged around using custom mouse/touch event listeners.

### Theming and Visual Design System
*   **Colors:** CSS Variables define `--primary: #9b59b6`, `--secondary: #f1c40f`, `--bg-color: #2c3e50`. The dark theme uses `#1a1a2e` backgrounds with `rgba(22, 33, 62, 0.95)` panels.
*   **Components:** Extensive use of CSS pseudo-elements for animation. Glassmorphism is used with `@supports` fallback for older browsers (`backdrop-filter: blur`). Buttons use chunky borders, hover transforms, and inset shadows for a tactile feel.

### Gamification & Reward Logic (Implemented)
*   **Progress:** Saved in `localStorage` under `alp_nodes_completed` (integer).
*   **Tasks:** A hardcoded array of 3 tasks runs in the Task Runner. Completing all 3 triggers a "Session complete! Earned a Star!" alert. The star is not actually saved or updated in the UI.
*   **Stickers:** Hardcoded array of 7 emojis in `ToyboxScreen.ts`. There is no logic implemented to "unlock" them based on gameplay.

---

## 2. Technical Architecture

### Directory & Module Structure
```
c:/Users/Asus/ALP/frontend/
├── index.html          # Clean HTML shell containing empty root containers for UI views
├── vite.config.ts      # Vite configuration, specifically targeting legacy iOS 9 support
├── package.json        # Dependencies (core-js) and scripts
├── src/
│   ├── main.ts         # App bootstrapper, DOMContentLoaded listener, and telemetry stub
│   ├── app.ts          # Central router, state manager, and UI component orchestrator
│   ├── style.css       # Massive monolithic stylesheet containing all UI and animation definitions
│   ├── profile/
│   │   └── profile_switcher.ts # LocalStorage-based user identity and avatar management
│   ├── storage/
│   │   └── websql_engine.ts    # Legacy WebSQL wrapper for offline data storage
│   └── ui/             # Object-oriented UI components that mutate the DOM shell
│       ├── AccountScreen.ts
│       ├── LandingScreen.ts
│       ├── MapScreen.ts
│       ├── ParentsDashboard.ts
│       ├── TaskRunner.ts
│       └── ToyboxScreen.ts
```

### Tech Stack & Build Tooling
*   **Core:** Vanilla TypeScript, HTML, CSS (No frontend frameworks).
*   **Build Tool:** Vite with `@vitejs/plugin-legacy`.
*   **Targets:** `targets: ['> 0.2%', 'not dead', 'iOS >= 9']`. Output format is `es2015` with `chrome61` CSS targets to ensure the PWA runs correctly on legacy iPads.
*   **Polyfills:** Injects `core-js` and `regenerator-runtime/runtime` to support async/await and ES6 features on older WebKit versions.

### State Management
*   **Approach:** Ephemeral UI state is held in class instance variables (e.g., `TaskRunner.currentTaskIndex`, `MapScreen.playerNodesCompleted`). The `App` class orchestrates which screen is active via `showScreen()`.
*   **Persistence:** `localStorage` is the primary persistence layer.
    *   `alp_registered_profiles`: JSON array of saved users.
    *   `alp_current_name` / `alp_current_avatar`: Active session state.
    *   `alp_nodes_completed`: Integer tracking map progression.
    *   `alp_unlocked_stickers`: Referenced in code but never actually written to or read from.

### Data Models / Schema (In Code)
```typescript
// Profile
export interface UserProfile {
  name: string;
  avatar: string; // 'princess' | 'knight' | 'magician' | 'explorer'
}

// Session Tasks (Duck-typed in TaskRunner.ts)
interface Task {
  id: string;
  prompt: string;
  visual: string; // HTML string
  options: string[]; // Array of 2-4 strings
  correctIndex: number;
  hint: string;
}

// WebSQL Schema (websql_engine.ts)
// TABLE: session_bundles
// FIELDS: id TEXT UNIQUE, profile_id TEXT, data TEXT (JSON stringified payload)
```

### Storage Engines
1.  **LocalStorage:** Used for profiles, current active user, and map progression.
2.  **WebSQL:** Implemented via `WebSQLEngine` to store `session_bundles`. It provides a promise-based wrapper over the legacy `window.openDatabase` API. (Note: Currently instantiated but entirely unused by the application).

### External Services & APIs
*   **None.** The application currently operates entirely offline using local hardcoded data arrays and `localStorage`. There is a `telemetry` object exported in `main.ts`, but it only logs to `console.log`.

---

## 3. Docs vs. Implementation Discrepancies

*   **Telemetry Queueing:**
    *   *Docs:* "A queueing system that logs granular interaction events for later sync."
    *   *Code:* `main.ts` contains a 3-line stub that logs to `console.log`. No queueing, local storage, or network sync exists.
*   **Curriculum Database:**
    *   *Docs:* "WebSQL Engine... storing 1,800+ categorized curriculum questions."
    *   *Code:* `websql_engine.ts` schema does not store individual questions; it stores a single `data TEXT` payload intended for "session bundles". Furthermore, `TaskRunner.ts` completely ignores WebSQL and uses a hardcoded array of 3 tasks (`startSession()` fallback).
*   **Rewards & Progression:**
    *   *Docs:* "Completing a 'World' (a set of 5 nodes) grants a 'Treasure Pack' (themed stickers)."
    *   *Code:* `TaskRunner.ts` completes sessions with a raw `alert()` and does not update `MapScreen`'s completed nodes. `ToyboxScreen.ts` hardcodes a list of 7 unlocked stickers and does not read from any reward unlock state.
*   **UI Flow / Task Runner Activation:**
    *   *Docs:* "Clicking a node on the map opens the Task Runner."
    *   *Code:* In `MapScreen.ts` line 181, clicking the active node triggers a native `alert("Task Runner opening...");`. It does not actually invoke `this.app.taskRunner.startSession()`.

---

## 4. Gaps & Unknowns

*   **Unused WebSQL Integration:** `WebSQLEngine` is fully implemented but never instantiated or queried anywhere in the UI or `App` lifecycle.
*   **Map State Sync:** `MapScreen` has a `saveState()` method, but the active node index (`playerNodesCompleted`) is never incremented after a task session finishes.
*   **Sticker State:** `profile_switcher.ts` clears `alp_unlocked_stickers` in the `resetProgress` method, but this key is never populated or read by `ToyboxScreen`.
*   **Parents Dashboard Data:** All data in `ParentsDashboard.ts` (0 quests, 0% accuracy, PISA benchmarks) is completely static HTML. There is no logic connecting the `TaskRunner` results to the dashboard.
*   **Missing Avatar Images:** The UI requests avatars from `/art/princess_avatar.jpg`, etc., and the landing page requests `/art/magical_forest.jpg`. If these assets are not present in the `public/art/` folder, the browser will render broken images.
*   **Sync Button:** The "Sync Data" button in `MapScreen.ts` has no event listener attached to it.
*   **Global Variables:** `app.ts` passes `this` (the App instance) into UI components so they can call `showScreen()`. This creates tight coupling and circular dependencies.
