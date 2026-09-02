# IMPLEMENTATION PLAN — VERSION 1.0

**Derived from:** Pedagogical Master Plan V4.1
**Status:** Draft for review
**Governing rule:** Every workstream below must implement the Master Plan's locked principles (Section 25) and the dependency chain in Section 26. No workstream may redefine what the Master Plan has already settled — if a workstream needs something the Master Plan doesn't answer, that is a signal to revise the Master Plan, not to decide it locally.

---

## 0. Purpose

This document translates the Pedagogical Master Plan (source of truth) into a sequence of buildable, independently ownable workstreams, and makes explicit two structural requirements:

1. **The Question Bank is built and validated as a separate artifact** from the pedagogical/adaptive architecture, so it can be independently re-validated at any time without touching the engine that runs it.
2. **A Parent Briefing System is introduced as a first-class workstream.** The Master Plan (Section 22) establishes the *philosophy* of parent-facing outcomes but does not specify a delivery mechanism, cadence, or format — this plan adds that as new, downstream implementation, constrained by Sections 22 and 23.

---

## 1. Architecture Overview

The Master Plan's dependency chain (Section 26) is implemented as seven workstreams:

```
Pedagogical Master Plan (source of truth — DONE, V4.1)
        │
        ▼
1. Curriculum Map
        │
        ▼
2. Assessment / Mastery Framework
        │
        ▼
3. Adaptive Learning Design
        │
        ▼
4. Question Specification Layer  ──────┐
        │                              │ (contract)
        ▼                              ▼
5. Question Bank (separate,       6. Parent Briefing System
   independently validatable)        (reads Assessment Framework
        │                             outputs, not raw questions)
        ▼                              │
7. Product / UX Implementation  ◄──────┘
```

Workstreams 5 and 6 are deliberately drawn as branches off the main spine rather than links in a single chain — see Sections 5 and 6 below for why each is structured that way.

---

## 2. Workstream 1 — Curriculum Map

**Translates:** Section 11 (Core Curriculum Architecture) + Section 12 (Developmental Progression) + Section 5 (Prerequisite Dependency Network) into an actual, named skill graph.

**Deliverable:** A structured map following `Domain → Strand → Skill → Subskill`, where every Subskill carries:
- its Required, Strongly Supportive, and Useful Background prerequisites (Section 5), named explicitly, not left implicit;
- its placement across Essential Foundations / Core Development / Enrichment-Advanced (Section 13);
- which of Phases A–F (Section 12) it is normally associated with, while preserving the Master Plan's instruction that phases are not chronological gates (Section 12);
- its position on Axis 1 (Content Progression) independent of any claim about Axis 2 (Cognitive Depth) — the two must not be pre-bound at this layer (Section 4.1).

**Explicitly out of scope here:** cognitive-depth tagging (Understand/Apply/Reason/Generalize/Create) and transfer-level tagging — those are properties of *tasks*, not of the skill graph, and belong to Workstream 4.

**Validation criteria:** Every subskill's prerequisite chain must resolve without cycles; every Essential Foundation subskill must have a documented downstream dependent (orphan foundations indicate a mapping error).

---

## 3. Workstream 2 — Assessment / Mastery Framework

**Translates:** Section 7 (Mastery Philosophy), Section 5.4 (Readiness Signals), Section 8 (Transfer & Generalization), Section 9 (Durable Learning), Section 3.10 (Expression Is Modality-Dependent).

**Must specify (as the Master Plan explicitly leaves these downstream):**

- **Evidence rules per mastery stage** (Introduced → Developing → Secure → Flexible → Generalized/Durable): what counts as sufficient evidence to move a skill between stages, skill-type by skill-type (Section 7.1), while respecting that no universal numeric threshold applies (Section 25.9).
- **Readiness detection logic**, built directly on the five converging signals in Section 5.4 (security, independence, spontaneous transfer, consistency, engagement) — this workstream decides *how* those signals are weighed and combined; it may not introduce a sixth criterion the Master Plan doesn't name, and may not collapse the five into a single score in place of "holistic judgment."
- **Decay/regression handling**: whether and how a Secure/Flexible skill can revert to Developing after a gap, consistent with Section 9's retrieval emphasis.
- **Evidence reliability rules**: a single data point (one correct or incorrect answer) must not move a mastery judgment, given young children's guess/misread variance.
- **Modality-aware scoring**: per Section 3.10, assessment logic must record which modality (typed / dictated / tapped / drawn / handwritten) produced a response, and must not treat a modality-driven shortfall as an understanding shortfall. This requires the Question Specification layer (Workstream 4) to tag intended modality per item.
- **Transfer-level tagging logic**: how a task's Level 1–5 transfer classification (Section 8) is assigned and verified.

**Output consumed by:** Adaptive Learning Design (Workstream 3) and Parent Briefing System (Workstream 6).

---

## 4. Workstream 3 — Adaptive Learning Design

**Translates:** Section 5.2/5.3 (ready / not ready responses), Section 3.3 & Section 20 (productive struggle vs. missing prerequisite vs. cognitive overload), Section 19 (challenge design), Section 15 (domain balance), Section 18 (time rhythm), Section 21 (creation progression).

**Must specify:**
- Decision logic for the four support branches named in Section 20 (missing prerequisite → strengthen it; productive struggle → allow time; ineffective strategy → prompt reflection; excessive cognitive load → reduce demand) — including how the system distinguishes between these four *cognitive* causes using only the evidence the Assessment Framework produces.
- Session composition logic implementing the 15–20 minute rhythm (Section 18) as a mix of focused learning, consolidation, retrieval, reasoning, transfer, and selected challenge — not as five fixed slots, but as a rule for varying the mix over time per Section 15's "reviewed over meaningful periods, not session by session."
- Escalation logic for selective acceleration (Phase E) that consumes Workstream 2's readiness signal output as its sole input for that decision — this workstream must not invent parallel readiness criteria.
- Creation-task cadence (Section 21's Answering → Explaining → Modifying → Generating → Creating progression) per domain.

**Explicitly not addressed here (per Section 22/23 boundary and the earlier scoping decision on this plan):** affective/emotional state modeling beyond what Section 5.4 already names (engagement, absence of avoidance) — this workstream uses those signals as given, it does not build a new emotional-state taxonomy.

---

## 5. Workstream 4 — Question Specification Layer

This is the **contract** between the pedagogical architecture and the content that will be authored. It exists specifically to make Workstream 5 possible as an independent, separately validatable process.

**Deliverable:** A specification schema, applied to every item type, carrying:

| Field | Source in Master Plan |
|---|---|
| Skill / Subskill ID | Curriculum Map (Workstream 1) |
| Required / Supportive prerequisite IDs | Section 5 |
| Cognitive depth level (Understand/Apply/Reason/Generalize/Create) | Axis 2, Section 4 |
| Transfer level (1–5) | Section 8 |
| Intended response modality | Section 3.10 |
| Language-load class (pure-reasoning vs. integrated language-and-reasoning) | Section 16 |
| Representation type (concrete/visual/verbal/symbolic/abstract) | Section 3.6, 17 |
| Challenge type, if applicable (unfamiliar context / incomplete info / multiple solutions / conflicting evidence / new representation, etc.) | Section 19 |
| Creation-stage tag, if applicable | Section 21 |

**Why this matters for independent validation:** once an item is tagged against this schema, a reviewer can validate it — pedagogical fit, content accuracy, age-appropriateness, safety — **without needing to know anything about the adaptive engine that will eventually select it.** The spec is the interface; Workstreams 4 and 5 do not need to ship together.

---

## 6. Workstream 5 — Question Bank (separate, independently validatable)

**Structural requirement (per this task's explicit instruction):** the Question Bank is authored, stored, versioned, and validated as its own artifact — a separate content repository keyed to Question Specification IDs — decoupled from the Adaptive Learning Design and Product/UX codebases. It must be possible to add, retire, or re-validate content **without a product release.**

### 6.1 Why separation matters here specifically
- **Different expertise validates different things.** Pedagogical-fit review, subject-matter accuracy review, and child-safety/language-load review are distinct skills; separating the bank lets each run independently rather than being bottlenecked on engineering release cycles.
- **Re-validation on demand.** Content can be flagged (parent report, periodic audit, curriculum revision) and re-reviewed or pulled without redeploying the adaptive engine.
- **Growth without redeployment.** New items can be added to expand coverage of a subskill without any change to Workstreams 3 or 7.

### 6.2 Validation pipeline (each stage independently re-runnable)

1. **Spec-compliance check** — automated: does the item carry all required tags from Workstream 4's schema, and are the tags internally consistent (e.g., a "Create" item cannot also be tagged pure-recall)?
2. **Pedagogical review** — does the item actually exercise the cognitive depth and transfer level it claims, per a domain-expert reviewer?
3. **Content accuracy review** — subject-matter correctness (this is where science/math/language errors are caught).
4. **Child-appropriateness & language-load review** — reading level, cultural neutrality, construct-irrelevant language (Section 16), and whether the item is free of anything inconsistent with the Safeguards in Section 23.
5. **Field/pilot validation** — empirical check that the item performs as intended (actual difficulty, discrimination between mastery levels) once used with real children; flagged items are routed back to stage 2 or 4.
6. **Versioning & re-certification** — every item carries a validation version and date; items can be scheduled for re-review or triggered for re-review by parent feedback or drift in field performance.

### 6.3 Ownership
The Question Bank should have its own review board/owner distinct from the engine/product owner, precisely so that a change of curriculum emphasis or a content correction does not require an app release, and an app release does not require re-touching validated content.

---

## 7. Workstream 6 — Parent Briefing System *(new; not specified in Master Plan)*

The Master Plan establishes the **philosophy** parents' understanding must follow (Section 22: progress is multidimensional; not reducible to "X grades ahead"; uneven development is expected; the key question is whether the child is learning to understand, adapt and recover) and the **safeguards** this must respect (Section 23: no single ability score, grade level, or speed metric). It does not specify a delivery mechanism. This workstream adds one, constrained entirely by those two sections.

### 7.1 What it must show
A multidimensional snapshot drawn directly from Section 22's list — knowledge, conceptual understanding, reasoning, transfer, problem solving, communication, creativity, strategic flexibility, persistence, metacognition, independence — **plus:**
- **Current areas of focus**: what the child is actively working on right now and why (e.g., "consolidating X because it supports upcoming Y," phrased in Master Plan terms, not raw skill IDs).
- **Recent movement**: skills that have progressed a mastery stage (Section 7), described narratively rather than numerically.
- **Suggested real-world complements**, tied to Section 18's list (reading, conversation, play, exploration) relevant to current focus areas — turning the briefing into something actionable for the parent, not just a report.

### 7.2 What it must never show (hard constraints from Section 23)
- No single composite score, percentile, or grade-level equivalency.
- No comparison to other children or cohort rankings.
- No framing that implies speed or volume is the measure of progress.
- No streaks, leaderboards, or gamified performance indicators in the parent-facing view — even if such mechanics exist in the child-facing product, they must not surface here.

### 7.3 Data source
The briefing is generated **only from Assessment/Mastery Framework outputs** (Workstream 2) — mastery stages, readiness signals, transfer evidence — never from raw item-level scores or the Question Bank directly. This preserves the same separation principle as Workstream 5: a parent-facing summary should not require exposing or interpreting individual question performance.

### 7.4 Cadence and format (proposed default, open to revision)
- A periodic narrative digest (default: every 1–2 weeks) plus an always-available on-demand view.
- Format: short narrative summary + a qualitative multidimensional profile (e.g., stage-per-dimension, not a single number) — never a leaderboard-style or single-axis visualization.

---

## 8. Workstream 7 — Product / UX Implementation

Implements the 15–20 minute session rhythm (Section 18), surfaces the Parent Briefing (Workstream 6), and enforces the Safeguards (Section 23) as product defaults — e.g., no optional leaderboard or streak feature should exist even as a togglable extra, since Section 23 rules these out categorically rather than conditionally.

---

## 9. Governance & Change Control

- Changes to the Master Plan's locked principles (Section 25) require an explicit Master Plan revision — no workstream may work around a gap by making a local decision that effectively redefines a locked principle.
- If any workstream discovers the Master Plan is silent on something it needs (as happened with readiness and expression modality, now resolved in V4.1), the correct action is to propose a Master Plan amendment, not to decide it locally and document the decision only in the workstream's own artifact.
- The Question Specification schema (Workstream 4) is the single shared contract between pedagogy and content; changes to it require sign-off from both the Assessment Framework owner and the Question Bank owner, since both depend on its stability.

---

## 10. Suggested Sequencing

Not a timeline — an ordering and parallelization guide:

1. **Curriculum Map** must complete first (everything depends on the skill graph existing).
2. **Assessment/Mastery Framework** and **Question Specification Layer** can be developed in parallel once the Curriculum Map is stable, since both consume it but don't depend on each other.
3. **Question Bank authoring** can begin as soon as the Question Specification schema is frozen — it does **not** need to wait for Adaptive Learning Design or Product/UX, which is the practical payoff of the separation in Section 6.
4. **Adaptive Learning Design** depends on the Assessment Framework being defined, not on the Question Bank being populated (it can be developed against a small pilot set of validated items).
5. **Parent Briefing System** depends only on the Assessment Framework's output format — it can be built in parallel with Adaptive Learning Design and Product/UX, not after them.
6. **Product/UX Implementation** integrates everything last, but its safeguard defaults (Section 23) should be specified from day one, not bolted on at the end.

---

## 11. What Remains Open

Per Section 27 of the Master Plan, the following are correctly left for the workstreams above to decide, not for this implementation plan to pre-empt: exact scoring algorithms, mastery percentages, response-time thresholds, hint weights, adaptive algorithms, retrieval intervals, database structures, UI, interaction mechanics, exact weekly schedules, and reward mechanics. This plan defines *who owns each decision and in what order*, not the decisions themselves.
