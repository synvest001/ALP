# Implementation Plan: Mixed vs. Focused Session Toggle

Based on our discussion, we'll implement a feature allowing the player (or parent) to choose between the standard mixed-subject adventure and a focused single-subject session. 

To keep the UI clean and intuitive, we will introduce a **"Choose Your Adventure" modal** that appears when the player clicks the active node on the Map Screen, rather than cluttering the screen with permanent toggles.

## Proposed Changes

### 1. `MapScreen.ts` (The User Interface)
- **Modify the Active Node Click:** Instead of immediately launching the session, clicking the active node will now open a new modal.
- **Create the Modal:** We'll add a new HTML modal to `MapScreen`'s render method with the following options:
  - 🌟 **Mixed Adventure (Recommended)**
  - 🔢 **Math Focus**
  - 📖 **English Focus**
  - 🧩 **Logic Focus**
  - 🌍 **Science & World Focus**
- Clicking an option will call `TaskRunner.startSession()` and pass the selected focused domain (or `undefined` for mixed).

### 2. `TaskRunner.ts` (The Orchestrator)
- Update the signature of `startSession` to accept an optional `focusedDomain` parameter: `startSession(sessionData?: TaskRequestPayload[], focusedDomain?: string)`.
- Pass this new parameter down to the `AdaptiveEngine` when calling `this.composer.generateSession()`.

### 3. `AdaptiveEngine.ts` (The Logic)
- Update `generateSession(kidId: string, focusedDomain?: string)` to accept the new parameter.
- **Logic Branching:**
  - **If `focusedDomain` is provided:** The engine will bypass the 40% math rule and instead fill all 10 slots of the `domainSlots` array with the requested domain.
  - **If `focusedDomain` is absent:** The engine will continue to use the standard mixed distribution (4 Math, 2 English, 2 Logic, 2 Science).
- The existing `RepetitionGuard` and progressive subskill unlocking mechanisms will continue to work perfectly within the single-domain constraint, preventing the user from getting stuck on a single subskill for all 10 questions.

## Open Questions

> [!IMPORTANT]  
> Are you happy with this approach of popping up a modal when clicking the active node? Alternatively, we could add a permanent dropdown or toggle button to the top header of the Map Screen. I recommend the modal as it feels more like starting a video game quest, but the choice is yours!

## Verification Plan
1. Apply the changes to the UI and Engine.
2. Manually test clicking the active node to ensure the modal appears.
3. Start a focused Math session and verify that the console logs and UI indicate all 10 tasks are Mathematics.
4. Verify that completing the session still correctly awards stars and advances the path.
