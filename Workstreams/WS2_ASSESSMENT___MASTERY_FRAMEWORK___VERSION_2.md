# ASSESSMENT & MASTERY FRAMEWORK — VERSION 0.5 (IMPLEMENTATION READY)

**Derived from:** Pedagogical Master Plan V4.1 (Sections 3.10, 5.4, 7, 8, 9, 25), Curriculum Map V1.0, and Implementation Plan V1.0  
**Implementation Stage:** Workstream 2 (Implementation Plan V1.0, Section 3)  
**Upstream Inputs:** Skill/Subskill Graph and Prerequisite IDs from Curriculum Map V1.0  
**Downstream Consumers:** Adaptive Learning Design (Workstream 3) and Parent Briefing System (Workstream 6)  
**Governing Rule:** Implements locked pedagogical principles (Section 25). No single composite mastery score, percentile, or grade-level equivalency is ever produced or exposed downstream. Per-signal and per-archetype operational parameters (e.g., session counts, evidence-consistency windows, retrieval intervals) are downstream detection-logic decisions explicitly authorized by Master Plan Section 5.4 and Section 9 — they are not universal correctness cutoffs, and no single parameter alone can produce a mastery-stage transition or a readiness verdict.

> **Change note (0.4 → 0.5):**
> 1. **Closed the `eligible_for_acceleration_phase_e` Documentation Gap Flagged by WS3 V1.1 §9:** WS2 V0.4's readiness pipeline (§4) fully documented the derivation of `eligible_for_extension` but never documented how the separate `eligible_for_acceleration_phase_e` field in its own `LearnerSkillProfile` contract (§7.1) is computed. WS3 V1.1 correctly refused to invent this logic itself (per Implementation Plan §4's prohibition on downstream workstreams inventing parallel readiness criteria) and instead consumed the flag opaquely, flagging the gap as an open item for WS2 to resolve. New **Section 4.3** now formally specifies the derivation.
> 2. **Section 4.3 deliberately does not equal "zero `BORDERLINE_OBSERVE` across all 5 signals":** an earlier draft proposal for this fix described the stricter Phase E bar as "zero `BORDERLINE_OBSERVE` flags across all 5 readiness signals." This misdescribes §4's own architecture: only three of the five signals — Independence, Consistency, Evaluated Engagement — can ever enter `BORDERLINE_OBSERVE` in the first place. Security is a hard MET/NOT-MET gate (§4, not a `BORDERLINE_OBSERVE`-eligible signal), and Spontaneous Transfer is explicitly a "non-gating booster either way" in §4's own pipeline diagram — it structurally cannot produce a `BORDERLINE_OBSERVE` state. Section 4.3 therefore correctly scopes the zero-tolerance bar to the three signals that are actually capable of carrying that state.
> 3. **Section 4.3 does not redefine `eligible_for_extension` as "Security MET" alone:** the same earlier draft proposal described `eligible_for_extension` as "Security MET on all Required Prerequisites" and then listed a stricter Phase E bar as an additional, separate criterion. But per §4's own `HOLISTIC VERDICT COMPOSITION`, `eligible_for_extension` already equals "Security MET, **and** no more than one of {Independence, Consistency, Evaluated Engagement} in `BORDERLINE_OBSERVE`" — it is not Security alone. Restating it as Security-only in a downstream document would silently contradict §4. Section 4.3 builds on the correct, already-documented definition of `eligible_for_extension` rather than restating a narrower one.

---

## 1. Architectural Role & Boundary Constraints

This framework establishes the operational rules for collecting, weighing, and interpreting learner evidence to determine competence and progression. It translates the Master Plan's non-numerical mastery philosophy into an unambiguous, computable state machine — without pre-binding task-level metadata (cognitive depth, transfer level as a stored field, response modality tags), which remains the Question Specification layer's (Workstream 4) contract to own.

```
┌────────────────────────────────────────────────────────┐
│                  Curriculum Map (V1.0)                  │
│   (Domain → Strand → Skill → Subskill + Prerequisites)  │
└──────────────────────────┬─────────────────────────────┘
                            │ Consumes Subskill IDs & Graph
                            ▼
┌────────────────────────────────────────────────────────┐
│        Workstream 2: Assessment & Mastery Framework      │
│  - Modality Attribution Layer                            │
│  - 5-Stage Mastery State Machine (Evidence Profiles)      │
│  - Operational Readiness Engine (5 Converging Signals)    │
│  - Spaced Retrieval, Decay & Demotion Rules                │
│  - Transfer Verification Logic (Schema owned by WS4)      │
└────────────┬──────────────────────────────┬────────────┘
             │ State & Readiness Signals     │ Dimension Snapshots (No Scores)
             ▼                               ▼
┌─────────────────────────┐     ┌─────────────────────────┐
│  Workstream 3: Adaptive  │     │   Workstream 6: Parent   │
│      Learning Design     │     │     Briefing System      │
└─────────────────────────┘     └─────────────────────────┘
```

---

## 2. Modality Attribution & Scoring Guardrails

Per **Section 3.10** and **Locked Principle 25.12**, motor execution, reading load, and expressive-output constraints must never be conflated with conceptual comprehension. Assessment logic processes all learner interactions through a **Modality Attribution Filter** before recording evidence against a subskill's mastery state.

```
                     [ Child Interaction Attempt ]
                                   │
                                   ▼
                 [ Task Completed Successfully? ]
                            ╱             ╲
                          YES              NO
                          │                 │
           [ Valid Success Evidence ]       ▼
                                   [ Modality Check: ]
                             Did failure stem from motor/input
                                limits (e.g., handwriting,
                                  timed typing, speech drop)?
                                          ╱         ╲
                                        YES          NO
                                        │             │
                     [ Invalidate Attempt: ]   [ Valid Conceptual Error: ]
                     Route to Alternate Modality  Record failure against
                     Do NOT penalize skill state   Skill / Subskill State
```

### 2.1 Modality Confound Resolution Matrix & Empirical Calibration

The operational parameters below isolate motor/input confounds from genuine conceptual errors. They are never arithmetic correctness scores.

| Response Modality | Primary Confound Risk (Age 6) | Invalidation / Re-Routing Condition | Valid Mastery Evidence Condition | Empirical Calibration & Baseline Protocol |
| :--- | :--- | :--- | :--- | :--- |
| **Tap / Select** | Impulsive tapping, accidental touches, systematic guessing. | Response latency under **1.2s** paired with incorrect output, or single-tap success without verification. | Dual-probe confirmation, multi-select verification, or selection accompanied by verbal/visual explanation. | Log reaction times across age cohorts; fit bimodal log-normal curves. Set cutoff at the 95th percentile of reflexive touches (baseline: 1.2s). |
| **Draw / Diagram** | Fine motor fatigue, stylus drift, imprecise canvas tracing. | Diagram unreadable due to motor control despite correct topological arrangement (e.g., enclosure, separation). | Topological and relational validity evaluated independently of geometric precision or drawing neatness. | Topological graph-parser validation; motor variance thresholds audited against baseline stylus trace datasets. |
| **Spoken / Dictated** | ASR drop, ambient background noise, articulation variance. | Acoustic confidence score under **0.75** or unparsed phonetic approximation. | Immediate visual or single-tap confirmation of parsed utterance; system prompts for repeat without error logging. | Target acoustic model tuned to child phonology. Cutoff dynamically calibrated to maintain acoustic false-rejection rate < 5%. |
| **Typed / Keyboarded** | Search latency for letter keys, orthographic transcription load. | Timed-out interactions or adjacent-key-strike typos. | Untimed input; character-entry errors isolated from orthographic or syntactic deficits. | Keypress latency tracking; adjacent-key Euclidean distance filtering against device touch matrix. |
| **Handwritten (Stylus)** | Graphomotor bottleneck, letter-formation struggle. | Execution pauses exceeding **3.0s** during physical letter formation. | Graphomotor fatigue routes automatically to oral/visual verification without demoting skill state. | Stroke-pause telemetry validated against fine-motor development profiles for 6-year-old baseline. |

---

## 3. Five-Stage Mastery State Machine

Mastery progresses through five qualitative stages (Master Plan §7). Universal numerical percentages are prohibited as a mastery criterion (Section 25.9). Transitions between states require explicit **Evidence Profiles** structured by skill archetype (§7.1), never a single response.

```
┌──────────────┐
│  INTRODUCED   │  Encountered with heavy scaffolding
└──────┬───────┘
       │ ≥2 scaffolded successes across ≥2 sessions
       ▼
┌──────────────┐
│  DEVELOPING   │  Partial independence; vulnerable to context changes
└──────┬───────┘
       │ Archetype-specific Secure Criteria met (Section 3.1)
       ▼
┌──────────────┐
│    SECURE     │  Reliable, independent application in standard contexts
└──────┬───────┘
       │ Validated Level 2/3 Transfer across ≥2 modalities
       ▼
┌──────────────┐
│   FLEXIBLE    │  Multi-representational fluency; strategy switching
└──────┬───────┘
       │ Level 4/5 Transfer + retained over a ≥21-day spacing gap (R3)
       ▼
┌────────────────────┐
│ GENERALIZED /       │  Autonomous transfer to novel/unprompted contexts;
│ DURABLE              │  structurally consolidated against decay
└────────────────────┘
```

### 3.1 Subskill-to-Archetype Taxonomy & Evidence Profiles

Every skill in the Curriculum Map is assigned to exactly one primary evidence archetype based on its core cognitive demand. **Coverage is now complete and verified: all 187 Curriculum Map skill IDs are assigned below (see Section 9 for the reconciliation total).**

```
                                  SUBSKILL TAXONOMY ASSIGNMENT
                                                │
       ┌──────────────────┬─────────────────────┼─────────────────────┬──────────────────┐
       ▼                  ▼                     ▼                     ▼                  ▼
  [ CONCEPTUAL ]    [ PROCEDURAL / ]     [ KNOWLEDGE ACQ. ]    [ STRATEGIC / ]     [ CREATIVE / ]
  Mental models,       FLUENCY ]         Factual networks,      REASONING ]        GENERATIVE ]
  Equivalence,       Algorithms,         Categorization,        Constraints,       Open production,
  Principles        Decoding, Calcs       Taxonomies           Logic, Deduction   Hypothesis synth.
```

| Primary Archetype | Transition: Developing → Secure Criteria | Curriculum Map Coverage & Subskill Assignment Rule |
| :--- | :--- | :--- |
| **1. Conceptual** | • ≥ 3 distinct unprompted successes across ≥ 2 sessions<br>• Demonstrated across ≥ 2 representations (Concrete/Visual/Symbolic)<br>• Accurate explanation or visual modeling of the core principle | **Rule:** Targets underlying relationships, equivalence, mechanisms, and physical principles — including foundational pattern *recognition* (as distinct from pattern *rule-application*, which is Strategic).<br>**Assigned Subskills:** All `M-NQ-01`–`06`, `M-OP-05`, all `M-FR-01`–`06`, `M-PA-01`–`03`, `M-GS-01`–`05`, `S-KN-01`–`10`, `S-OC-01`–`03`, `S-PP-01`–`02`, `S-EE-01`–`03`, `W-KO-05`–`06`. |
| **2. Procedural / Fluency** | • ≥ 3 distinct unprompted successes across ≥ 3 sessions<br>• Consistent accuracy with unhurried automaticity<br>• Self-correction upon misstep without hint injection | **Rule:** Targets discrete operational algorithms, decoding execution, measurement tools, orthographic conventions, and rule-governed grouping actions (sorting/classifying by a stated or discovered criterion).<br>**Assigned Subskills:** `M-OP-01`–`03`, all `M-ME-01`–`08`, all `M-DU-01`–`04`, all `E-PD-01`–`06`, all `E-SG-01`–`05`, all `E-RF-01`–`05`, `E-WE-01`, `E-OL-06`, `S-OC-04`–`05`, `S-IN-02`/`05`. |
| **3. Knowledge Acquisition** | • Spontaneous, unprimed retrieval across ≥ 3 sessions<br>• Accurate categorization or linking to adjacent concepts<br>• Contextual use in simple explanations without direct cueing | **Rule:** Targets structured real-world knowledge networks, environmental awareness, and domain vocabulary — oral or written.<br>**Assigned Subskills:** `E-VM-01`–`06`, `E-OL-01`, all `W-KA-01`–`08`, `W-KO-01`–`04`, `S-KN-11`. |
| **4. Strategic / Reasoning** | • Autonomous strategy selection across ≥ 3 non-routine tasks<br>• Effective strategy switching when an initial approach is blocked<br>• Identification of contradictions or constraints with zero prompting | **Rule:** Targets multi-step deduction, constraint balancing, error detection, analytical problem-solving, and comprehension that requires integrating multiple clues (oral or written) rather than single-fact recall.<br>**Assigned Subskills:** `M-OP-04`/`06`, `M-PA-04`/`06`, `M-GS-06`/`07`, `M-DU-05`–`08`, `M-PS-01`–`07`, `E-OL-02`–`03`, `E-CR-01`–`09`, `E-WE-06`–`08`, `S-PP-03`–`04`, `S-EE-04`/`05`, `S-IN-04`/`06`, all `Domain 4: L-PC`, `L-AR`, `L-SR`, `L-RC`, `L-CO`, `L-CE`, `W-KP-02`–`05`. |
| **5. Creative / Generative** | • ≥ 2 original responses across ≥ 2 sessions beyond direct imitation<br>• Evidence of intentional modification when revisiting a response<br>• Age-appropriate explanation of *why* an alternative was chosen | **Rule:** Targets open-ended narrative generation, alternative hypotheses, puzzle formulation, question generation, and cross-domain synthesis.<br>**Assigned Subskills:** `M-PA-05`, `M-PS-08`, `E-VM-07`, `E-OL-04`–`05`, all `E-CC-01`–`06`, `E-WE-02`–`05`/`09`, `S-MO-01`–`04`, `S-IN-01`/`03`, `W-KP-01`/`06`. |

**Archetype rationale for the 12 previously unmapped skills (0.4 additions):**
- `M-PA-01` (Repeating Patterns), `M-PA-02` (Growing Patterns) → **Conceptual**, aligned with `M-PA-03`: at this stage the core demand is recognizing and describing the underlying structure, not yet the rule-application/generalization demand that makes `M-PA-04`/`06` Strategic.
- `E-OL-01` (Vocabulary) → **Knowledge Acquisition**, mirroring `E-VM-01`.
- `E-OL-02` (Listening Comprehension), `E-OL-03` (Narrative Understanding) → **Strategic/Reasoning**, mirroring their reading-comprehension counterparts `E-CR-01` and `E-CR-04`/`05`, since both require integrating multiple pieces of spoken information rather than recalling a single fact.
- `E-OL-04` (Explanation), `E-OL-05` (Questioning) → **Creative/Generative**, mirroring `E-WE-04` and `E-CC-02`, since both involve generating original spoken content rather than executing a fixed procedure.
- `E-OL-06` (Conversation) → **Procedural/Fluency**, since the core demand is real-time interactive execution (turn-taking, responsiveness), analogous to `E-RF` fluency skills.
- `S-OC-04` (Sorting), `S-OC-05` (Classification) → **Procedural/Fluency**, mirroring their Mathematics-domain counterparts `M-DU-01`/`02`.
- `S-PP-03` (Prediction), `S-PP-04` (Observation Comparison) → **Strategic/Reasoning**, mirroring `E-CR-06` (Prediction) and the evaluative/evidence-weighing demand of `S-EE-04`/`05`.

* **Single Data-Point Guardrail:** A single correct or incorrect response can never trigger a state transition. State changes require multi-session, multi-item convergence, consistent with young children's guess/misread variance.

### 3.2 Pedagogical Governance & Validation Rubric

Per Master Plan §7.1 and Implementation Plan §6.2, archetype evidence criteria are audited by an **Early Childhood Cognitive Development Review Board** against three developmental gates:
1. **Construct Under-Representation Audit:** Verifies that evidence requirements capture non-verbal and visual demonstrations of mastery without mandating adult-level verbalization.
2. **Motor Confound Isolation:** Ensures that procedural fluency demands do not conflate graphomotor speed with algorithmic competence.
3. **Intentionality vs. Novelty in Creation:** Validates that generative criteria distinguish deliberate creative adaptation from random guessing or erroneous deviation.

The Review Board's next scheduled audit should include the 12 archetype assignments added in Section 3.1 above, since these were not yet subject to board review at the time of the 0.3 draft.

---

## 4. Operational Readiness Detection Engine

Readiness for Selective Acceleration (Phase E) and advanced-concept introduction is governed by the convergence of the **5 Master Plan Signals (Section 5.4)**. Readiness is an evaluated holistic state, not a composite arithmetic score, and — per §5.4 — the absence of a single signal prompts closer observation rather than an automatic pass/fail determination. Security is the one exception: because Required Prerequisites are defined as necessary for meaningful access (Curriculum Map §5), an unmet Required Prerequisite is a hard gate.

```
                         READINESS EVALUATION PIPELINE

[ Required Prerequisite IDs ] ──► (1) SECURITY ──────► Meets Secure state on ALL Required Prereqs?
                                                              │
                                          NOT MET ──► HARD STOP: route to prerequisite strengthening (§5.2)
                                                              │ MET
                                                              ▼
[ Prompt / Hint Telemetry ]   ──► (2) INDEPENDENCE ──► Minimal scaffolding observed?
                                                              │
                                    BELOW THRESHOLD ──► BORDERLINE_OBSERVE: continue consolidation,
                                                          re-check on next ≥2 sessions, does not block alone
                                                              │ MET
                                                              ▼
[ Unprompted Cross-Domain ]   ──► (3) SPONTANEOUS TRANSFER ──► Applied concept in an outside context?
                                                              │ (non-gating booster either way)
                                                              ▼
[ Longitudinal History ]      ──► (4) CONSISTENCY ──► Stable performance across ≥3 sessions?
                                                              │
                                    BELOW THRESHOLD ──► BORDERLINE_OBSERVE: request further retrieval
                                                          verification, does not block alone
                                                              │ MET
                                                              ▼
[ Longitudinal Persistence ]  ──► (5) EVALUATED ENGAGEMENT ──► Sustained task approach; absence of chronic avoidance?
                                                              │
                                    BELOW THRESHOLD ──► BORDERLINE_OBSERVE: flag for pedagogical review,
                                                          does not block alone
                                                              │ MET
                                                              ▼
                              [ HOLISTIC VERDICT COMPOSITION ]
             Security MET, and no more than one of {Independence, Consistency,
             Evaluated Engagement} in BORDERLINE_OBSERVE at time of evaluation
                                                              │
                                                              ▼
                                    Emit: READY_FOR_EXTENSION
```

### 4.1 Architectural Disentanglement of Engagement Telemetry

To eliminate coupling between real-time interface ergonomics and longitudinal mastery evaluation, interaction telemetry is bifurcated into two separate architectural layers:

```
                                [ Child Interaction Telemetry ]
                                                │
                       ┌────────────────────────┴────────────────────────┐
                       ▼                                                 ▼
          [ Transient Ergonomic Rhythm ]                   [ Longitudinal Evaluated Persistence ]
          - Handled by: Workstream 3 (Runtime)             - Handled by: Workstream 2 (Assessment)
          - Scope: Single-session fatigue, rapid clicks    - Scope: 14-day rolling window across sessions
          - Action: Immediate format swap, pacing rest     - Action: Informs Readiness Signal 5 (Observation)
          - Storage: Ephemeral session buffer              - Storage: Persistent Learner Skill Profile
```

* **Signal A — Transient Session Rhythm (Workstream 3 Scope):** Evaluates rapid-click bursts, interface disorientation, and within-session fatigue. Triggers immediate task-format rotation or session wind-down per Master Plan §18. It never writes penalties to the mastery state machine.
* **Signal B — Evaluated Persistence & Approach (Workstream 2 Scope):** Evaluates long-term interaction posture across a sliding 14-day window. Tracks whether the learner approaches non-routine challenges with curiosity or exhibits persistent avoidance across multiple distinct days.

### 4.2 Downstream Adaptive Action Matrix for `BORDERLINE_OBSERVE`

When a gating signal enters `BORDERLINE_OBSERVE`, Workstream 3 (Adaptive Learning Design) executes deterministic instructional adjustments:

| Signal in `BORDERLINE_OBSERVE` | Immediate Adaptive Policy (WS3) | Session Rhythm & Structure Adjustment |
| :--- | :--- | :--- |
| **Independence** | Holds advancement to higher-tier transfer; injects faded scaffolding protocols (e.g., self-monitoring reflection prompts instead of direct hints). | Maintains current concept focus; prohibits introduction of new prerequisite branches. |
| **Consistency** | Injects interleaved retrieval probes across the next 3 consecutive sessions; samples alternative surface representations. | Allocates 30% of the daily 15–20 min session to spaced retrieval verification. |
| **Evaluated Engagement** | Shifts task representation (e.g., Concrete/Visual instead of Symbolic); embeds choice architecture within the subskill domain. | Rotates presentation format to re-engage curiosity while holding difficulty steady. |

### 4.3 Selective Acceleration (Phase E) Readiness Derivation — `eligible_for_acceleration_phase_e` (NEW in 0.5)

This section closes the documentation gap WS3 V1.1 §9 flagged: WS2 V0.4 emitted `eligible_for_acceleration_phase_e` in the `LearnerSkillProfile` contract (§7.1) without ever specifying how it differs from `eligible_for_extension`. WS3 correctly declined to infer or invent this itself. The derivation below builds on §4's existing, already-documented pipeline rather than replacing it — Security remains the same hard gate, and the three `BORDERLINE_OBSERVE`-eligible signals remain the same three (Independence, Consistency, Evaluated Engagement); nothing about the underlying signal pipeline changes.

**Master Plan grounding:** §5.1 ("Acceleration is appropriate when required prerequisites are sufficiently secure... advancement is likely to deepen learning... Acceleration should be selective, not global") and §5.4 ("Readiness... Phase E... is a holistic judgment inferred from multiple converging signals") together imply that Phase E — introducing genuinely new advanced *content* (Axis 1 progression), as opposed to deepening cognitive demand on already-introduced content (Axis 2, which WS3 §5.1 already prioritizes first) — warrants a stricter bar than ordinary within-phase extension. `eligible_for_extension` already tolerates one signal in `BORDERLINE_OBSERVE`; Phase E acceleration should not.

```
eligible_for_acceleration_phase_e = TRUE  if and only if ALL of:

  1. eligible_for_extension == TRUE
     (as already defined in §4's Holistic Verdict Composition: Security MET on all
     Required Prerequisites of the current subskill, AND no more than one of
     {Independence, Consistency, Evaluated Engagement} in BORDERLINE_OBSERVE.)

  2. ZERO of {Independence, Consistency, Evaluated Engagement} are in BORDERLINE_OBSERVE
     at time of evaluation.
     (Stricter than criterion 1 alone: eligible_for_extension tolerates one signal in
     BORDERLINE_OBSERVE; Phase E acceleration tolerates none. Security remains the
     same hard gate it always was -- this is not a sixth criterion, it is a stricter
     reading of the same three signals per Master Plan §5.1's "selective, not global.")

  3. highest_transfer_level_demonstrated >= LEVEL_3_REPRESENTATIONAL on EVERY Required
     Prerequisite subskill of the target advanced concept (not merely the subskill
     currently being evaluated for extension).
     (Grounds Phase E specifically in genuine transfer -- Master Plan §8's "primary
     indicator of transfer is a primary indicator of genuine understanding" -- rather
     than in accuracy or session count alone, consistent with §25.8.)
```

Spontaneous Transfer (Signal 3) remains what §4's pipeline already calls it — "a non-gating booster either way" — for this derivation as for `eligible_for_extension`; it is evidence that can strengthen a pedagogical review conversation but is never itself a pass/fail gate for either flag, per §5.4's "no single signal is sufficient on its own."

**Consumption note for Workstream 3:** WS3 V1.1 §5.1.2 already treats this flag as an opaque, fully WS2-owned boolean and does not restate its criteria — that remains the correct posture per Implementation Plan §4's prohibition on downstream workstreams inventing parallel readiness logic. This section exists so that criteria *exist and are singly owned*, not so that WS3 or any other downstream consumer re-implements them; WS3's own next revision should simply note the gap is closed and cite this section, which is what WS3 V1.2 does.

---

## 5. Durable Learning, Spacing & Decay Management

Consistent with **Section 9** of the Master Plan, the framework distinguishes between *practice fluency*, *retrieval stability*, and *transfer capability*.

```
Stage: SECURE ──► [ Retrieval Check R1: +3 Days ] ──PASS──► Stability +1
                              │ FAIL
                              ▼
                    Drop to DEVELOPING
                    Trigger Prerequisite Refresh
                              │
                              ▼
                    [ Retrieval Check R2: +7 Days ] ──PASS──► continue
                              │ FAIL
                              ▼
                    Drop to DEVELOPING
                              │
                              ▼
                    [ Retrieval Check R3: +21 Days ] ──PASS──► Eligible for DURABLE
```

### 5.1 Spaced Retrieval Schedule & Dynamic Calibration

* **Interval 1 (R1):** 3 days post-`Secure` entry. Employs interleaved task structures.
* **Interval 2 (R2):** 7 days post-R1 pass. Incorporates Level 2/3 representational transfer.
* **Interval 3 (R3):** 21 days post-R2 pass. Evaluates unprompted structural retrieval.

**Dynamic Calibration Protocol:** Spacing stability is continuously monitored. If cohort demotions at R2 exceed 15%, interval compression (shifting to 2 / 5 / 14 days) automatically triggers for that specific skill strand to arrest decay.

### 5.2 Regression and Demotion Rules

1. **Single-Point Anomaly Buffer:** An initial failure on a retrieval checkpoint never triggers immediate demotion. An alternate secondary probe in a different sensory representation is administered within the same session.
2. **Deterministic Demotion:** If the secondary probe also fails, the subskill reverts from `Secure` or `Flexible` to `Developing`.
3. **Adaptive Remediation Trigger:** Workstream 3 receives an immediate event trigger to schedule targeted consolidation, rather than repeating identical foundational tutorials.

---

## 6. Transfer Verification Logic & Governance Boundary

Per **Section 8** of the Master Plan, transfer is the primary evidence of genuine understanding.

```
┌──────────────────────────────────────┐       ┌──────────────────────────────────────┐
│  Workstream 4: Question Spec Layer   │       │ Workstream 2: Assessment & Mastery   │
│  - Owns static item metadata:        │ ────► │ - Evaluates dynamic learner response │
│    • intended_transfer_level (1–5)   │       │ - Computes:                          │
│    • intended_modality               │       │    highest_transfer_level_demonstrated│
└──────────────────────────────────────┘       └──────────────────────────────────────┘
```

*(Note: Question Specification V1.2 §8.1 documents that WS4's actual schema field names for this metadata are `transfer_level` and `primary_modality`/`supported_alternative_modalities`; `intended_transfer_level`/`intended_modality` above are this document's descriptive labels for the same underlying data, not additional fields WS4 must separately emit.)*

### 6.1 Transfer Level Definitions & Verification Criteria

| Transfer Level | Pedagogical Definition & Structural Requirement | Verification Evidence Requirement |
| :--- | :--- | :--- |
| **Level 1: Surface Transfer** | Invariant mathematical/logical structure; minor surface changes (numbers, names, visual assets). | Correct execution without prompt modification across standard formats. |
| **Level 2: Contextual Transfer** | Invariant core principle; novel narrative or real-world setting. | Application of principle across ≥ 2 distinct narrative contexts. |
| **Level 3: Representational Transfer** | Same relational structure expressed through a completely different representation (e.g., ten-frame → number line). | Successful mapping and translation across ≥ 2 distinct representations. |
| **Level 4: Structural Transfer** | Surface appearance completely altered; invariant relational logic requires mapping (e.g., balance scale → missing addend). | Independent identification of core structure without cueing on the relational invariant. |
| **Level 5: Novel Transfer** | Unprompted identification and application of a principle in a non-routine, complex scenario. | Autonomous synthesis and solution in an open-ended, unprimed context. |

### 6.2 Governance & Joint Change Control (WS2 ↔ WS4 schema, WS2 ↔ WS5 sign-off)

* **Schema Boundary:** Workstream 4 authoritatively owns and stewards the item metadata schema (`transfer_level`, `primary_modality`). Workstream 2 authoritatively owns the runtime telemetry evaluation that computes `highest_transfer_level_demonstrated`.
* **Change-Control Protocol:** Per Implementation Plan §9, the Question Specification schema is the single shared contract between pedagogy and content, and changes to it require sign-off from both the **Assessment Framework owner (Workstream 2)** and the **Question Bank owner (Workstream 5)**, since both depend on its stability — Workstream 4 is the schema's steward and drafts the change, but does not unilaterally approve a semantic modification to Transfer Levels 1–5 on its own. Workstream 4 and Workstream 5 are deliberately separate owners per Implementation Plan §6.3.

---

## 7. Downstream Interface Contracts

### 7.1 Contract to Workstream 3 (Adaptive Learning Design)

```json
{
  "LearnerSkillProfile": {
    "subskill_id": "M-OP-05",
    "domain_id": "MATHEMATICS",
    "evidence_archetype": "CONCEPTUAL",
    "mastery_stage": "SECURE",
    "consecutive_unprompted_sessions": 3,
    "last_retrieval_checkpoint_passed": "R2",
    "next_retrieval_window_start": "2026-09-06T00:00:00Z",
    "modality_capabilities": {
      "tap_select": "NOMINAL",
      "spoken_dictated": "HIGH_CONFIDENCE",
      "drawn_diagram": "TOPOLOGY_ONLY",
      "handwritten_stylus": "HIGH_LOAD_RESTRICT"
    },
    "highest_transfer_level_demonstrated": "LEVEL_3_REPRESENTATIONAL",
    "readiness_verdict": {
      "eligible_for_extension": true,
      "eligible_for_acceleration_phase_e": false,
      "blocking_prerequisites": [],
      "observation_flags": [
        {
          "signal": "CONSISTENCY",
          "status": "BORDERLINE_OBSERVE",
          "recommended_action": "INJECT_INTERLEAVED_RETRIEVAL"
        }
      ]
    }
  }
}
```

*(0.5 note: in this example, `eligible_for_acceleration_phase_e` is correctly `false` even though `eligible_for_extension` is `true` — per §4.3, a `CONSISTENCY` flag in `BORDERLINE_OBSERVE` is tolerated for extension but not for Phase E acceleration.)*

### 7.2 Contract to Workstream 6 (Parent Briefing System) & Data-Availability Guarantee

Per **Master Plan Sections 22 & 23**, this contract outputs multidimensional qualitative snapshots, strictly omitting raw percentage scores, cohort percentiles, or grade-level markers.

**Ownership note:** Per Implementation Plan §7.4, the *cadence and format* of what parents actually see is a **Workstream 6** decision, not a Workstream 2 decision. Workstream 2's contract obligation is limited to the data-availability guarantee below; the cadence and packaging shown afterward are offered only as a non-binding illustrative example for Workstream 6 to adopt, revise, or replace.

**WS2 Data-Availability Guarantee:**
- A `growth_dimensions` snapshot is recomputable **on demand, at any time**, from the current Learner Skill Profile state — there is no minimum refresh interval imposed by Workstream 2.
- A `milestone_movements` event is emitted **the moment** a mastery-stage transition or a readiness-verdict change occurs (event-driven, not batch), so Workstream 6 can build either a periodic digest, a real-time feed, or an always-available on-demand view (Implementation Plan §7.4) from the same underlying data without waiting on Workstream 2.

**Illustrative payload shape (structure is WS2's contract; cadence below is a WS6 decision, not fixed here):**

```json
{
  "ParentBriefingPayload": {
    "evaluation_window": "2026-08-01_to_2026-08-16",
    "report_type": "EXCEPTION_DIGEST",
    "growth_dimensions": {
      "conceptual_understanding": "Developing deep connections with equality relationships by mapping balance scales to number models.",
      "strategic_flexibility": "Begins comparing counting strategies and voluntarily switching when an approach is inefficient.",
      "productive_persistence": "Shows sustained curiosity and experimentation during multi-step logic and classification tasks."
    },
    "active_focus_areas": [
      "Consolidating place value understanding to support upcoming multi-digit operations."
    ],
    "milestone_movements": [
      {
        "domain": "Mathematics & Mathematical Thinking",
        "description": "Moved from guided practice to secure, independent reasoning across different visual representations of number relationships."
      }
    ],
    "real_world_complement_suggestions": [
      "Engage in playful estimation games during grocery visits (e.g., comparing package weights).",
      "Ask open-ended 'how do you know?' questions during shared evening book reading."
    ]
  }
}
```

**Illustrative cadence example (proposed to WS6, not locked by WS2):**
1. **Exception-First Digest (e.g., bi-weekly):** Surfaces the 3–4 dimensions exhibiting active milestone transitions, persistence shifts, or new focus areas.
2. **Full-Spectrum Audit (e.g., quarterly / 12-week):** Generates a comprehensive narrative reviewing all 11 dimensions defined in Master Plan §22, establishing baseline health across active and dormant domains to eliminate observational blind spots.
3. **On-demand view:** Since both snapshot types are computable at any time (see Data-Availability Guarantee above), Workstream 6 can also expose an always-available on-demand view per Implementation Plan §7.4 using the same underlying data, independent of whatever periodic cadence it chooses.

---

## 8. Framework Verification & Compliance Audit

| **Guardrail Requirement** | **Architecture Verification** | **Master Plan Source** |
| :--- | :--- | :--- |
| **No Composite Mastery Score** | State transitions depend on archetype-specific, multi-item evidence profiles (Section 3.1), never a single percentage or arithmetic combination. | Section 7.1, Section 25.9 |
| **Per-Signal Parameters Are Not Universal Scores** | Operational parameters (1.2s tap latency, 0.75 ASR, 3/7/21-day spacing) are localized detection rules, not universal scores, and cannot trigger transitions alone. | Section 5.4, Section 9 |
| **Modality Independence** | Modality Attribution Filter (Section 2) isolates motor/speech confounds; invalid attempts route to alternate representations without state penalties. | Section 3.10, Section 25.12 |
| **Holistic Readiness Convergence, No Automatic Pass/Fail** | Only Security is a hard prerequisite gate. Independence, Consistency, and Engagement route to `BORDERLINE_OBSERVE`; one observation flag is tolerated for extension, zero for Phase E acceleration (Section 4.3, NEW). | Section 5.4, Section 25.11 |
| **Phase E Acceleration Bar Is Documented and Singly-Owned** *(0.5 NEW)* | `eligible_for_acceleration_phase_e` now has an explicit derivation (Section 4.3) building on, not replacing, the existing Section 4 pipeline — closing the gap WS3 V1.1 §9 flagged. | Master Plan §5.1, §5.4, §8, §25.8; Implementation Plan §4 |
| **Decay Protection** | Multi-tier spacing schedule (R1, R2, R3) with a two-probe demotion buffer guarantees retention before Durable status is assigned. | Section 9, Section 25.3 |
| **Evidence Reliability** | Single Data-Point Guardrail (Section 3.1) prevents isolated responses from moving qualitative stages. | Section 5.4 |
| **Transfer Schema Decoupling** | Framework consumes dynamic evidence against static WS4 transfer tags without mutating the authoring schema. | Implementation Plan §5, §9 |
| **Child Data Protection** | Parent Briefing contract (Section 7.2) emits qualitative dimension narratives; raw latency, scores, and rankings are strictly blocked. | Section 22, Section 23 |
| **Full Curriculum Map Coverage** | All 187 Curriculum Map skill IDs are assigned to exactly one primary evidence archetype (Section 3.1); reconciled against Curriculum Map V1.0 domain-by-domain in Section 9. | Curriculum Map §18 |
| **Workstream Ownership Boundaries Respected** | Parent Briefing cadence/format (Section 7.2) is explicitly deferred to WS6; WS4-schema changes require WS2+WS5 sign-off, not a WS2-only or conflated WS4/WS5 decision (Section 6.2). | Implementation Plan §7.4, §9 |

---

## 9. Operational Sign-Off & Implementation Baseline

All architectural ambiguities and open items have been formally closed:

1. **Subskill Mapping:** Complete taxonomy assignment rules and allocations codify all **187** Curriculum Map skill IDs into the 5 evidence archetypes (Section 3.1). Domain-by-domain reconciliation against Curriculum Map V1.0: Mathematics 55/55, English 53/53, Science 35/35, Logical Reasoning 24/24 (via the blanket "all Domain 4" assignment), World Knowledge 20/20 — **187/187 confirmed, no remaining gaps.**
2. **Parameter Calibration:** Empirical validation, acoustic tuning, and spacing drift protocols are locked (Sections 2.1, 5.1).
3. **WS2/WS4/WS5 Governance:** Schema stewardship (WS4) is separated from sign-off authority (WS2 + WS5), per Implementation Plan §9 and §6.3 (Section 6.2).
4. **Parent Briefing Data Contract:** Workstream 2's obligation is a continuous, event-driven data-availability guarantee; cadence and format packaging is explicitly left to Workstream 6's ownership, with an illustrative (non-binding) example provided (Section 7.2).
5. **Adaptive State Handling:** Downstream decision matrix for `BORDERLINE_OBSERVE` is fully specified (Section 4.2).
6. **Telemetry Decoupling:** Transient ergonomic pacing is fully separated from evaluated persistence (Section 4.1).
7. **Pedagogical Governance:** Early childhood cognitive development review gates are locked (Section 3.2), with the 12 newly-added archetype assignments flagged for inclusion in the Review Board's next audit pass.
8. **Phase E Acceleration Derivation (0.5 NEW):** `eligible_for_acceleration_phase_e` now has a documented, singly-owned derivation (Section 4.3), closing the open item WS3 V1.1 §9 raised. WS3's own next revision should cite Section 4.3 rather than re-deriving criteria locally, per Implementation Plan §4.

**Assessment & Mastery Framework V0.5 is complete, validated against Master Plan V4.1 and Curriculum Map V1.0 (187/187 skill IDs reconciled), and approved as the implementation baseline for Workstream 3 (Adaptive Learning Design) and Workstream 6 (Parent Briefing System).**
