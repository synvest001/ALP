# Walkthrough: Adventure Selection Modal

We've successfully added the ability for players to choose between the standard mixed-subject sessions and fully focused single-subject sessions!

## What Changed?

### 1. The Map Screen UI (`MapScreen.ts`)
Instead of immediately jumping into a mixed session when clicking the active node, the Map Screen now pops open a sleek **"Choose Your Path"** modal. The player is presented with big, colorful buttons to select their adventure type:
- 🌟 **Mixed Adventure (Recommended)**
- 🔢 **Math Focus**
- 📖 **English Focus**
- 🧩 **Logic Focus**
- 🌍 **Science & World Focus**

### 2. Session Orchestration (`TaskRunner.ts`)
The `TaskRunner` was updated to accept a `focusedDomain` parameter. When a player clicks one of the buttons in the modal, their selection is passed down into the engine to begin generating a custom session for them.

### 3. Adaptive Engine Logic (`AdaptiveEngine.ts`)
The `AdaptiveEngine` now fully supports focused domain generation. 
- **If "Mixed Adventure" is selected:** It falls back to the default ruleset (4 Math, 2 English, 2 Logic, 2 Science).
- **If a "Focus" is selected:** It creates an array of 10 slots filled entirely with the selected domain (e.g., 10 Mathematics questions).
- **Repetition and Progression:** The engine still respects the internal Repetition Guard, meaning it will rotate through different active subskills within that domain to prevent boring repetition, and it will dynamically adjust cognitive depth based on performance!

You can test this out by refreshing the app, clicking the active avatar node on the map, and choosing a specific path. Let me know if you want to tweak any of the button designs or session logic!
