# ADAPTIVE LEARNING DESIGN — VERSION 1.3 (IMPLEMENTATION READY)

**Derived from:** Pedagogical Master Plan V4.1 (Sections 3.2, 3.3, 4, 5, 7, 8, 9, 14, 15, 18, 19, 20, 21, 25), Implementation Plan V1.0 (Section 4), Assessment & Mastery Framework V0.5 (Workstream 2), and Curriculum Map V1.0 (Workstream 1)
**Implementation Stage:** Workstream 3 (Implementation Plan V1.0, Section 4)
**Upstream Inputs:** `LearnerSkillProfile` contract & readiness telemetry from Assessment Framework (WS2), Skill/Subskill Graph & Prerequisite IDs from Curriculum Map (WS1)
**Downstream Consumers:** Question Specification Layer (Workstream 4) & Product / UX Engine (Workstream 7)
**Governing Rule:** Implements locked pedagogical principles (Master Plan Section 25). Operates as a deterministic pedagogical dispatch engine. WS3 consumes mastery stages, readiness verdicts, and archetype classifications as defined by WS2 without creating parallel scoring metrics, inventing duplicate readiness criteria, or redefining prerequisite dependencies.

> **Change note (1.1 → 1.2):**
> 
> 1. **Domain / Function-Type Conflation in Session Composition Resolved (Section 4):** V1.1's §4.2 Step 2 instructed the engine to check "each remaining function type's actual share... against its target range (Section 4.3 table)" — but §4.3's table was organized by **domain** (Mathematics / English / Science-WK / Logic), while §4.1's "function types" (Retrieval / Focused Core / Consolidation / Strategic Reasoning / Creative-Transfer) are a genuinely separate axis with no target ranges defined anywhere in V1.1. A task carries both a domain *and* a function type simultaneously, and the V1.1 algorithm never said which axis governed sampling, or how the two combine. Section 4 is restructured: §4.3 (domain ranges) is unchanged; a new **§4.4** adds function-type target ranges, grounded directly in Master Plan §18's own list ("focused learning; consolidation; retrieval; reasoning; transfer; selected challenge") rather than an invented breakdown; and §4.2 Steps 2–3 are rewritten to rank candidate (domain, function-type) pairs by combined deficit across both axes explicitly, rather than silently picking one.
> 2. **Floor-Priority Override Added for Ceiling Enforcement (Section 4.2, Step 3):** Building on the now-disambiguated dual-axis algorithm above, ceiling suppression (a domain or function type at or above its rolling target) is now explicitly deferred until the session has met its 4-task floor. Below the floor, a due-event-heavy session (e.g., several R1/R2/R3 retrieval checkpoints landing the same day) is allowed to temporarily exceed a rolling ceiling rather than being truncated below a usable session length. Once the floor is met, ceiling enforcement resumes for any remaining budget up to the 6-task cap.
> 3. **WS2 Open Item Closed (Section 5.1.2, Section 9):** Assessment Framework V0.5 §4.3 now formally derives `eligible_for_acceleration_phase_e` (previously an undocumented WS2 field, flagged as an open item in V1.1 §9). Section 5.1.2 is updated to cite WS2 §4.3; Section 9's open item is marked resolved rather than removed outright, preserving the historical record of why the flag was ever treated as opaque. WS3 continues to consume the flag as an opaque WS2-owned boolean and does not restate WS2 §4.3's criteria here, consistent with Implementation Plan §4's prohibition on inventing parallel readiness logic — closing the documentation gap does not change WS3's consumption posture.

> **Change note (1.2 → 1.3):**
> 
> 1. **Device-Capability Filtering Explicitly Placed Outside WS3 (Section 7):** Workstream 7 has surfaced a low-memory legacy-device deployment target. `permitted_modalities` / `restricted_modalities` in the `TaskRequestPayload` (Section 7) are, and remain, purely pedagogical fields — they are derived from struggle-branch classification (Section 3.1, Branch 4) and WS2's per-child modality capability profile, and WS3's architecture (Section 1) has no device/runtime-capability input to draw on. A one-line clarification is added after the Section 7 payload to state explicitly that filtering a retrieved item's modality set down to what a given device can actually render is a Workstream 7 responsibility performed after item retrieval, not a WS3 responsibility — closing a possible ambiguity before WS7 is authored, without adding any new field, input, or decision logic to WS3 itself. Question Specification V1.3 §3.5 / §8.2 cross-references this same boundary from the WS4 side.

---

## 1. Architectural Role & Boundary Constraints

Workstream 3 is the **pedagogical decision, routing, and session-composition engine**. It translates evaluated mastery states and real-time interaction context into structured learning sessions tailored for a 6-year-old child who attends full-time school.

```
┌────────────────────────────────────────────────────────┐
│                  Curriculum Map (V1.0)                  │
│    - 187 Subskill IDs & Graph Dependencies              │
│    - Required / Supportive / Background Prerequisites   │
└──────────────────────────┬─────────────────────────────┘
                           │ Consumes Graph & Prereqs
                           ▼
┌────────────────────────────────────────────────────────┐
│        Workstream 2: Assessment & Mastery Framework      │
│  - 5-Stage Qualitative Mastery State Machine             │
│  - Operational Readiness Engine (5 Converging Signals)   │
│  - Spaced Retrieval Schedules (R1=3d, R2=7d, R3=21d)     │
│  - Ephemeral Telemetry vs. Longitudinal Persistence      │
└──────────────────────────┬─────────────────────────────┘
                           │ Consumes LearnerSkillProfile (JSON Contract)
                           ▼
┌────────────────────────────────────────────────────────┐
│        Workstream 3: Adaptive Learning Design           │
│  - Asynchronous / School-Day Schedule Accommodations    │
│  - 4-Way Support & Scaffolding Branching Engine          │
│  - Event-Driven, Rolling-Window Session Composition      │
│  - Dual-Axis Selective Acceleration Engine                │
│  - 5-Stage Creation Progression Orchestrator              │
└────────────┬──────────────────────────────┬────────────┘
             │ Task Selection Constraints   │ Ergonomic Rhythm & Pacing
             ▼                              ▼
┌─────────────────────────┐     ┌─────────────────────────┐
│  Workstream 4: Question  │     │   Workstream 7: Product  │
│      Specification      │     │         / UX Layer      │
└─────────────────────────┘     └─────────────────────────┘
```

---

## 2. Non-Daily, Asynchronous Rhythm (School-Day Accommodations)

Because the learner attends full-time school, learning sessions must fit flexibly around fluctuating cognitive fatigue, school schedules, and family life.

### 2.1 Calendar-Independent Progression Mechanics

1. **Zero Streak Mechanics:** Streaks, daily countdowns, and decay penalties for missed days are strictly prohibited (Master Plan §23). Progress is accumulated per active session, not per calendar day.
2. **Elapsed Wall-Clock Spacing:** Spaced retrieval intervals ($R_1 = 3\text{ days}$, $R_2 = 7\text{ days}$, $R_3 = 21\text{ days}$) define the *minimum elapsed wall-clock time* before a skill becomes eligible for retrieval verification.
   - *Example:* If a child does not use the application for 10 days after passing $R_1$, the $R_2$ probe (scheduled for $\ge 7$ days) is immediately eligible upon their next session without overdue flags or negative scoring.
3. **Session Budget:** Each session is constrained strictly to **15–20 minutes**, typically comprising **4 to 6 tasks** whose count and mix are determined dynamically per Section 4. The engine terminates or ramps down the session when the 20-minute limit is reached.

### 2.2 Transient School-Fatigue & Ergonomic Pacing Protection

Per Master Plan §18 and WS2 §4.1, transient session telemetry is isolated from longitudinal capability evaluations:

* **Fatigue Detection Triggers:** Rapid-click bursts ($<1.2\text{s}$ latency on multiple items), extended idle pauses ($>15\text{s}$ without input), or multiple immediate help requests.
* **Immediate Adaptive Pacing Action:**
  - Suppresses high-load symbolic/decoding items.
  - Automatically routes the remaining task budget to low-stakes creative exploration (Creation Steps 4–5) or initiates a graceful, encouraging session wind-down.
  - **Mastery State Isolation:** Fatigue-driven session terminations write zero negative evidence to the persistent `LearnerSkillProfile`.

---

## 3. Four-Branch Support & Scaffolding Engine

Per Master Plan §20, adaptive intervention must match the specific cognitive cause of difficulty rather than treating all errors uniformly.

```
                     [ MODALITY ATTRIBUTION FILTER (WS2 §2) — evaluated FIRST ]
                                              │
                        Confound identified? ─┴─ No confound identified
                                │                          │
                                ▼                          ▼
                  [ ROUTE TO BRANCH 4 ]         [ LEARNER STRUGGLE DETECTED ]
                   (Cognitive Overload /                    │
                    Modality Confound)     ┌───────────────┬┴───────────────┐
                                            ▼               ▼                ▼
                                    [ MISSING PREREQ ] [ PRODUCTIVE     [ INEFFECTIVE
                                     Unmet required      STRUGGLE ]      STRATEGY ]
                                     subskill dependency  Secure          Repetitive
                                                          foundations;    failure;
                                                          exploring       rigid
                                                          solutions       approach
                                            │               │                │
                                            ▼               ▼                ▼
                                     Route to target   Withhold hints;  Inject self-monitor
                                     prerequisite       allow pause      prompts; pivot task
                                     subskill           time; preserve   representation
                                     consolidation       autonomy
```

**Precedence rule:** the Modality Attribution Filter (WS2 §2) always runs before struggle-cause classification. A pause or error is only eligible to be classified as Branch 1–3 once WS2 has ruled out a modality confound for that response. This resolves the previous overlap between Branch 2's general pause window and Branch 4's modality-specific pause threshold (see 3.1 below).

### 3.1 Cognitive Cause Detection & Routing Matrix

| Struggle Condition                                                               | Assessment Framework (WS2) Detection Trigger                                                                                                                                                                                    | Deterministic Adaptive Action (WS3)                                                                                             | Task Specification Dispatch (WS4)                                                       |
|:-------------------------------------------------------------------------------- |:------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |:------------------------------------------------------------------------------------------------------------------------------- |:--------------------------------------------------------------------------------------- |
| **Branch 4: Cognitive Overload** *(evaluated first — see precedence rule above)* | Modality Attribution Filter (WS2 §2) flags a confound: e.g., handwritten execution pause $>3.0\text{s}$ during letter formation, ASR confidence $<0.75$, tap latency $<1.2\text{s}$, or high construct-irrelevant reading load. | Swaps response modality (e.g., stylus writing $\to$ oral/tap selection); strips construct-irrelevant text.                      | `support_branch: "LOAD_REDUCTION"`, `language_load_class: "PURE_REASONING"`.            |
| **Branch 1: Missing Prerequisite**                                               | Target subskill blocked by an unmet Required Prerequisite ID (`mastery_stage` $\in$ {`INTRODUCED`, `DEVELOPING`}).                                                                                                              | Halts progression on target; re-routes current task to prerequisite strengthening.                                              | `support_branch: "PREREQUISITE_STRENGTHENING"`, target set to prerequisite subskill ID. |
| **Branch 2: Productive Struggle**                                                | Required prerequisites `SECURE`; no modality confound flagged; deliberate pause latencies ($3\text{s}$–$12\text{s}$); active exploratory attempts.                                                                              | Suppresses hints; provides processing time; preserves child autonomy and problem space.                                         | `support_branch: "PRODUCTIVE_STRUGGLE_PROTECT"`, hint injection suppressed.             |
| **Branch 3: Ineffective Strategy**                                               | Repeated errors with identical response pattern; lack of self-correction; strategy rigidity; no modality confound flagged.                                                                                                      | Injects metacognitive reflection prompt ("What changed?"); switches surface representation (e.g., ten-frame $\to$ number line). | `support_branch: "STRATEGY_REFLECTION_PIVOT"`, alternative representation requested.    |

---

## 4. Event-Driven, Rolling-Window Session Composition Engine

Per Implementation Plan §4, session composition must be implemented "not as five fixed slots, but as a rule for varying the mix over time" against Master Plan §15's instruction that balance is "reviewed over meaningful periods, not session by session." Section 4 replaces V1.0's fixed-slot template with a composition **algorithm**: no session is guaranteed to contain any particular fixed set of task types, and no task type carries a fixed per-session time allocation. What *is* fixed is the 15–20 minute session budget, the 4–6 task count, and two independent sets of rolling-window target **ranges** evaluated over a 14-day window — one for **domain** (§4.3) and one for **task function type** (§4.4, new in 1.2).

**Two distinct axes (1.2 clarification):** every task carries both a `domain_id` (Mathematics / English / Science-EVS / Logical Reasoning / World Knowledge) and a `task_function_type` (Retrieval / Focused Core / Consolidation / Strategic Reasoning / Creative-Transfer, §4.1). These are orthogonal — a single task is, for example, simultaneously "Mathematics" and "Strategic Reasoning." V1.1 defined rolling targets only for domain (§4.3) while describing the composition algorithm in terms of "function type," without ever reconciling the two. V1.2's §4.2 algorithm now explicitly tracks deficits on both axes and combines them; nothing about domain balance (§4.3, unchanged from V1.1) or the function-type definitions (§4.1, unchanged) was itself wrong — only the step that was supposed to connect them to the sampling algorithm was missing.

### 4.1 Task Function Types

Every task in a session is tagged with exactly one function type. These describe *what a task does*, not *where it sits in a template*:

- **Retrieval** — interleaved spaced-retrieval probe ($R_1$/$R_2$/$R_3$ checkpoints) for a subskill in `SECURE` or `FLEXIBLE` status.
- **Focused Core** — introduction or extension of an active subskill in Phase A, B, or C whose prerequisites are met.
- **Consolidation** — deepening understanding of a partially-mastered subskill across varied representations (Concrete ↔ Visual ↔ Symbolic).
- **Strategic Reasoning** — explicit reasoning challenges (Domain 4) or cross-domain relational problem-solving.
- **Creative / Transfer** — open-ended creation, model formulation, or novel problem generation (Creation Steps 3–5).

**Reflection is not a separate function type or task slot.** A short metacognitive closing element (a "what worked / what would you try next time" prompt, ~30–60 seconds) is appended to the final task of every session, consistent with Curriculum Map §11.2 treating metacognition as authentically embedded rather than an isolated block. On fatigue-triggered wind-down (§2.2), this closing element may be shortened or skipped entirely in favor of a graceful exit.

### 4.2 Per-Session Composition Algorithm

```
STEP 1 — DUE-EVENT INTAKE (event-driven, not scheduled)
  • Pull any Retrieval checkpoints WS2 currently marks due (R1/R2/R3) for this learner.
  • Pull any active Branch 1 (Missing Prerequisite) remediation targets flagged by WS2/WS3
    struggle history since the last session.
  → These are included first and are NOT capped by a fixed slot; if nothing is due,
    zero Retrieval or remediation tasks appear in the session — this is expected
    and correct behavior, not a gap to be filled.
  → Each due-event task carries both its domain and its function type (Retrieval, or
    Focused Core / Consolidation depending on the remediation target's phase); both
    axes' rolling actuals (Step 2) are updated by these tasks exactly as by any other,
    so an event-driven checkpoint never distorts either axis's balance accounting.

STEP 2 — ROLLING-WINDOW DEFICIT CHECK (dual-axis, 1.2 clarified)
  • Compute each domain's actual share of tasks delivered over the trailing 14 days
    against its target range (§4.3 table); compute each function type's actual share
    over the same window against its target range (§4.4 table). These are two
    independent computations against two independent tables.
  • For each candidate (domain, function_type) pair not yet ruled out by Step 3's
    floor/ceiling logic, compute a combined deficit score = domain_deficit_below_floor
    + function_type_deficit_below_floor (zero if a given axis is already within or
    above its own target range). A pair deficient on both axes ranks above a pair
    deficient on only one.
  • Rank candidate pairs by combined deficit score, largest first.

STEP 3 — FILL REMAINING TASK BUDGET (floor-priority override, 1.2 NEW)
  • Sample tasks from the ranked deficit list (largest combined deficit first) until
    either the 15–20 minute time budget or the 4–6 task count is reached.
  • Floor-Priority Override: while the session has fewer than 4 tasks, ceiling
    suppression (see below) does not apply — a domain or function type at or above
    its rolling ceiling may still be sampled if it is the best (or only) available
    fit, so that a due-event-heavy session (e.g., three retrieval checkpoints landing
    the same day, all in Mathematics) is never truncated below a usable session
    length purely because Mathematics or Retrieval is already at its rolling ceiling.
  • Once the session has reached 4 tasks, ceiling suppression resumes: a domain or
    function type at or above its rolling target ceiling (either table) is not
    sampled for any remaining budget up to the 6-task cap, even if Step 1 due events
    already consumed time budget in that domain or function type.

STEP 4 — CLOSE
  • Append the metacognitive closing element (Section 4.1) to the final task, unless
    fatigue wind-down (§2.2) is active.
```

This means a given session might be entirely Retrieval-plus-Consolidation in Mathematics (if three checkpoints are due and the child is fatigued), or entirely Focused-Core-plus-Strategic-Reasoning spread across English and Logic (if nothing is due and those combinations are furthest behind target on both axes), or any other mix — the algorithm, not a template, determines the shape of any single session. Balance is only meaningful, and only enforced past the 4-task floor, at the 14-day rolling level, matching Master Plan §15 exactly.

### 4.3 14-Day Rolling Target Ranges — Domain

Per Master Plan §15, time allocation reflects developmental prerequisite density rather than artificial daily symmetry. Targets below are expressed as **ranges** over the trailing 14-day window, not fixed per-session minutes:

| Category                                      | 14-Day Target Range | Rationale                                                                                                                                                                                                                                                                                              |
|:--------------------------------------------- |:------------------- |:------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| **Mathematics & Mathematical Thinking**       | 30–40%              | High longitudinal prerequisite density (Master Plan §15).                                                                                                                                                                                                                                              |
| **English Language, Reading & Communication** | 25–35%              | Foundational decoding, syntax, and comprehension fluency dependencies (Master Plan §15).                                                                                                                                                                                                               |
| **Science / EVS & World Knowledge**           | 15–25% (combined)   | Master Plan §15 discusses these two domains under a single heading — both "require regular exposure to build connected knowledge and inquiry" — so they are tracked as one combined range rather than split arbitrarily; downstream reporting may still break out per-domain actuals for transparency. |
| **Dedicated Logical Reasoning**               | 10–20%              | Explicit developmental strand (Master Plan §15) distinct from Logic's cross-domain embedding within the other categories' tasks.                                                                                                                                                                       |

### 4.4 14-Day Rolling Target Ranges — Task Function Type (NEW in 1.2)

V1.1 described the composition algorithm as sampling against "target ranges" for function types but never actually defined any — only the domain table above existed. Master Plan §18 independently lists almost exactly this axis directly: "The application should provide a purposeful combination of: focused learning; consolidation; retrieval; reasoning; transfer; selected challenge." The ranges below ground WS3's five function types (§4.1) in that list the same way §4.3's domain ranges are grounded in §15.

| Function Type           | 14-Day Target Range | Rationale                                                                                                                                                                                                                                                                                                                   |
|:----------------------- |:------------------- |:--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Focused Core**        | 25–35%              | Master Plan §18's "focused learning" — the primary vehicle for new-content introduction and extension within a phase; must remain the largest single share so Phase A–C progression is not starved by maintenance activity.                                                                                                 |
| **Retrieval**           | 15–25%              | Master Plan §18's "retrieval," grounded further in §9's durable-learning emphasis (R1/R2/R3 spacing, WS2 §5). Kept as a range rather than purely event-driven-only so the engine still proactively samples retrieval-adjacent review even in weeks with few due checkpoints, without letting it crowd out focused learning. |
| **Consolidation**       | 15–25%              | Master Plan §18's "consolidation" — deepening partially-mastered content, distinct from both new-content introduction (Focused Core) and spaced-retrieval verification (Retrieval) per Master Plan §9's practice/retrieval/transfer distinction.                                                                            |
| **Strategic Reasoning** | 15–25%              | Master Plan §18's "reasoning," and the primary vehicle for the Logical Reasoning domain's cross-domain embedding (Master Plan §15, Curriculum Map §12).                                                                                                                                                                     |
| **Creative / Transfer** | 10–20%              | Master Plan §18's "transfer" and "selected challenge," and the primary vehicle for Master Plan §21's Answering→Creating progression (§6, this document). Kept as the smallest floor since Master Plan §19 frames challenge as something to be "selected," not maximized every session.                                      |

Retrieval and Branch-1 remediation tasks (Section 4.2, Step 1) are counted toward whichever domain *and* function type they target — never as a separate bucket on either table — so an event-driven checkpoint never distorts either axis's balance accounting.

---

## 5. Dual-Axis Selective Acceleration Engine

Acceleration operates along two decoupled dimensions (Master Plan §4, §14). Axis 1 and Phase A–F are related but distinct: Phase describes a subskill's *normal developmental orientation* (non-chronological, per Master Plan §12 and Curriculum Map §3), while Axis 1 describes *content complexity* itself. A subskill's phase provides context for where a child is working, but does not define, and must not be conflated with, its position on Axis 1.

```
                     AXIS 2: COGNITIVE DEPTH
   Understand ──► Apply ──► Reason ──► Generalize ──► Create
        ▲           ▲          ▲           ▲            ▲
        │           │          │           │            │
  ┌─────┴───────────┴──────────┴───────────┴────────────┴─────┐
  │         AXIS 1: CONTENT PROGRESSION                       │
  │     Foundational ──► Core ──► Extended ──► Advanced       │
  └───────────────────────────────────────────────────────────┘

  (Phase A–F, tracked per-subskill via the Curriculum Map, describes the subskill's
   normal developmental orientation and provides scheduling context — it is a
   separate, non-chronological classification and is not itself a position on Axis 1.)
```

### 5.1 Dual-Axis Dispatch Policies

1. **Depth-First Prioritization:** When a child demonstrates rapid mastery, WS3 escalates **Axis 2 (Cognitive Depth)** to *Reason*, *Generalize*, or *Create* on current-phase content before advancing **Axis 1 (Content Progression)**. This is an operational dispatch preference chosen by WS3 within the discretion Implementation Plan §27 grants to downstream workstreams for exact algorithms — it does not alter the Master Plan's independence of the two axes (§4.1, §25.5); a subskill's depth and content-progression classifications remain independently tracked regardless of dispatch order.
2. **Selective Content Acceleration (Phase E):** Triggered **only** when WS2 emits `eligible_for_acceleration_phase_e = true`. **WS3 treats this flag as an opaque, fully WS2-owned verdict and does not itself define, restate, or assume the criteria behind it** (per Implementation Plan §4's prohibition on inventing parallel readiness criteria). *(1.2: WS2 Assessment & Mastery Framework V0.5 §4.3 now formally documents this flag's derivation, closing the gap flagged in V1.1 §9 — see Section 9 below. This does not change WS3's consumption posture: the flag remains opaque to WS3, which cites WS2 §4.3 rather than restating its criteria.)*

---

## 6. Creation Progression Orchestrator

Per Master Plan §21, creative synthesis is cultivated systematically through a 5-step developmental progression:

```
[ 1. ANSWERING ] ──► [ 2. EXPLAINING ] ──► [ 3. MODIFYING ] ──► [ 4. GENERATING ] ──► [ 5. CREATING ]
Standard response     Justify method/       Alter constraints     Formulate new         Open-ended multi-
selection             demonstrate why       in existing problem   problem instance      domain synthesis
```

### 6.1 Domain-Specific Creation Trajectories

* **Mathematics:**
  1. *Answer:* Solve $8 + \square = 12$.
  2. *Explain:* Demonstrate with a balance scale why adding 4 balances the sides.
  3. *Modify:* Change one number on the balance scale so the missing quantity becomes 6.
  4. *Generate:* Create a new balance scale problem that has a solution of 7.
  5. *Create:* Design a multi-step number puzzle for a family member to solve.
* **English & Literacy:**
  1. *Answer:* Identify character feelings in a story excerpt.
  2. *Explain:* Cite text clues explaining why the character felt nervous.
  3. *Modify:* Change a key character decision and predict the immediate consequence.
  4. *Generate:* Formulate three alternative questions the character could have asked.
  5. *Create:* Compose an original alternative ending to the narrative.
* **Science / EVS & World Knowledge:**
  1. *Answer:* Match an animal to its natural habitat.
  2. *Explain:* Describe how the animal's physical features help it survive there.
  3. *Modify:* Alter a climate condition (e.g., water shortage) and predict the organism's response.
  4. *Generate:* Propose a testable inquiry question about plant growth in different soils.
  5. *Create:* Construct an interactive diagram modeling energy and food flow in that ecosystem.
* **Logical Reasoning:**
  1. *Answer:* Identify the missing shape in a visual pattern matrix.
  2. *Explain:* Identify the two transformation rules (rotation + color shift) in the matrix.
  3. *Modify:* Add a third constraint (size variation) to make the puzzle more complex.
  4. *Generate:* Build a 3x3 pattern matrix with a deliberate error for the system to check.
  5. *Create:* Invent a multi-rule constraint riddle with a unique valid solution.

---

## 7. Downstream Contract to Question Specification (WS4)

WS3 emits a task request payload to WS4 for item retrieval and dynamic instantiation. Note that `task_index` reflects position within *this* session's dynamically-assembled task list, not a fixed slot number, and `session_task_count` communicates how many tasks this particular session contains (4–6, per Section 4):

```json
{
  "TaskRequestPayload": {
    "session_id": "sess_20260817_01",
    "task_index": 3,
    "session_task_count": 5,
    "task_function_type": "STRATEGIC_REASONING",
    "target_subskill_id": "M-OP-05",
    "domain_id": "MATHEMATICS",
    "phase_context": "PHASE_D",
    "required_cognitive_depth": "REASON",
    "target_transfer_level": "LEVEL_3_REPRESENTATIONAL",
    "intended_representation": "VISUAL_BALANCE_SCALE",
    "permitted_modalities": ["TAP_SELECT", "SPOKEN_DICTATED"],
    "restricted_modalities": ["HANDWRITTEN_STYLUS"],
    "language_load_class": "PURE_REASONING",
    "creation_stage": "MODIFYING",
    "support_branch": "PRODUCTIVE_STRUGGLE_PROTECT",
    "time_budget_seconds": 240
  }
}
```

*(1.3 note: see Question Specification V1.3 §8.2 for the explicit field-by-field mapping from this payload to WS4's authored item schema, including how `task_function_type` and `phase_context` — which are not stored on any individual item — are used to select `target_subskill_id` and `evidence_archetype` before a query is issued.)*

**Device-capability filtering note (1.3 NEW):** `permitted_modalities` and `restricted_modalities` above are populated entirely from pedagogical inputs — struggle-branch classification (Section 3.1) and WS2's per-child `modality_capabilities` profile — and carry no information about the requesting device or runtime. WS3 has no device-capability input anywhere in its architecture (Section 1) and this revision does not add one. Once WS4 returns an item matching this payload, filtering that item's `primary_modality` / `supported_alternative_modalities` down to whatever is actually renderable on the requesting device (e.g., a low-memory legacy client without reliable in-browser ASR or canvas support) is a Workstream 7 responsibility, performed after retrieval, not a WS3 decision. Question Specification V1.3 §3.5 guarantees every authored item carries at least one device-universal modality (`TAP_SELECT`) so this later WS7 filtering step always has a viable option to fall back to.

---

## 8. WS3 Validation & Compliance Audit

| Architectural Guardrail                                              | Implementation Verification                                                                                                                                                                                                                  | Master Plan / Implementation Plan Source     |
|:-------------------------------------------------------------------- |:-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |:-------------------------------------------- |
| **No Streak or Speed Metrics**                                       | Spacing and progression operate on session count and elapsed real time; zero gap penalties.                                                                                                                                                  | Master Plan §23                              |
| **Fatigue Isolation**                                                | Transient session pacing (Signal A) is decoupled from persistent learner evaluations (Signal B).                                                                                                                                             | Master Plan §18, WS2 §4.1                    |
| **No Fixed Session Template**                                        | Session composition is generated per-session by an event-driven + rolling-deficit algorithm (Section 4); no task-type carries a fixed per-session time allocation, and no session is required to contain a fixed set of task types.          | Implementation Plan §4                       |
| **Balance Reviewed Over Meaningful Periods, Not Session-by-Session** | Domain (§4.3) and task-function (§4.4) targets are each enforced only as independent 14-day rolling ranges; single-session composition is intentionally unconstrained below the 4-task floor (§4.2 Step 3).                                  | Master Plan §15                              |
| **Domain and Function-Type Axes Explicitly Reconciled** *(1.2 NEW)*  | §4.2's ranking step computes a combined deficit score across both the domain table (§4.3) and the newly-added function-type table (§4.4) rather than leaving the composition algorithm to silently favor one axis.                           | Implementation Plan §4; Master Plan §15, §18 |
| **No Deadlock Below Minimum Session Length** *(1.2 NEW)*             | Floor-Priority Override (§4.2 Step 3) suspends ceiling suppression on both axes until the 4-task floor is met, preventing a due-event-heavy session (e.g., a heavy retrieval/decay-recovery day) from being truncated below a usable length. | Implementation Plan §4                       |
| **Depth Before Content Acceleration**                                | Axis 2 (Cognitive Depth) is deepened to Reason/Create before Axis 1 (Phase E) is unlocked, as a WS3 dispatch preference that does not alter the axes' independent tracking.                                                                  | Master Plan §4.1, §14, §25.5                 |
| **No Invented Readiness Criteria**                                   | `eligible_for_acceleration_phase_e` is consumed as an opaque WS2-owned boolean; WS3 does not define or restate its derivation, even now that WS2 §4.3 documents it.                                                                          | Implementation Plan §4                       |
| **Deterministic Cause Handling with Modality Precedence**            | 4-branch engine responds specifically to missing prerequisites vs. overload vs. strategy deficits, with the Modality Attribution Filter evaluated first to resolve latency-window overlaps.                                                  | Master Plan §20, WS2 §2                      |
| **Modality Protection**                                              | Task requests enforce modality constraints derived directly from WS2 capability profiles.                                                                                                                                                    | Master Plan §3.10, WS2 §2                    |
| **Phase / Axis 1 Distinction Preserved**                             | Phase A–F is represented as scheduling context (`phase_context`) separate from Axis 1 content-progression classification.                                                                                                                    | Master Plan §12, Curriculum Map §3           |

---

## 9. Open Items for Upstream Resolution

**WS2 Documentation Gap — `eligible_for_acceleration_phase_e` derivation — RESOLVED in 1.2.** WS2 V0.4's readiness pipeline (WS2 §4) documented the derivation of `eligible_for_extension` but not the distinct `eligible_for_acceleration_phase_e` field in its own `LearnerSkillProfile` contract (WS2 §7.1). WS3 V1.1 §5.1.2 consumed this flag opaquely rather than asserting its own criteria and flagged the gap here for upstream resolution. **Assessment & Mastery Framework V0.5 §4.3 now formally derives this flag** (Security MET, zero of the three `BORDERLINE_OBSERVE`-eligible signals in that state, and Level 3+ transfer demonstrated on every Required Prerequisite of the target advanced concept), closing this item. WS3's consumption posture is unchanged: Section 5.1.2 above cites WS2 §4.3 rather than restating its criteria, since the documentation gap being closed does not itself license WS3 to start asserting parallel readiness logic (Implementation Plan §4).

No other open items remain at this revision.
