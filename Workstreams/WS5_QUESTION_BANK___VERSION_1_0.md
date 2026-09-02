# QUESTION BANK — VERSION 1.0 (AUTHORING BASELINE)

**Derived from:** Pedagogical Master Plan V4.1 (Sections 16, 23, 25), Implementation Plan V1.0 (Sections 6, 9, 10.3), Curriculum Map V1.0 (187 Subskill IDs), Question Specification Layer V1.3 (Workstream 4 — item schema, Section 3.5/Rule 3.10 device-universal modality guarantee)
**Implementation Stage:** Workstream 5 (Implementation Plan V1.0, Section 6)
**Upstream Inputs:** Frozen QuestionSpecification JSON Schema v1.3.0 (WS4 §2), Stage 1 automated validator (WS4 §6), canonical Subskill→Archetype map (WS2 §3.1)
**Downstream Consumers:** Adaptive Learning Design (WS3, item retrieval per WS4 §8.2 mapping), Product/UX Runtime (WS7, asset rendering)
**Governing Rule:** The Question Bank is authored, stored, versioned, and validated as an independent artifact per Implementation Plan §6. It must be addable-to, retirable-from, and re-validatable **without a product release**, and its review board is distinct from the engine/product owner (Implementation Plan §6.3). This document does not redefine anything WS1–WS4 have already settled; it operationalizes the six-stage pipeline Implementation Plan §6.2 specifies in outline form.

> **Architectural note on this revision's trigger:** Workstream 7 has surfaced a low-memory legacy-device deployment target (older iPad hardware, capped iPadOS version, dated WebKit, unreliable in-browser ASR, constrained canvas/stylus support). WS3 V1.3 §7 and WS4 V1.3 §3.5/Rule 3.10 already closed the *interaction-modality* half of this problem (every item is guaranteed to carry `TAP_SELECT` as a device-universal fallback, and WS7 is responsible for runtime modality filtering). That guarantee says nothing about whether an item's actual **assets** — SVG files, audio files, canvas complexity — will load or render acceptably on that same hardware. Asset payload is authored and stored here, in the Question Bank, not in the WS4 schema or the WS3 engine. Section 4 of this document is the corresponding fix on the content side, closing the other half of the same device-support gap without reopening WS4's schema or asking WS1–WS3 to change anything.

---

## 1. Architectural Role & Boundary Constraints

```
┌────────────────────────────────────────────────────────┐
│      Workstream 4: Question Specification Layer          │
│   - Frozen JSON Schema v1.3.0                             │
│   - Stage 1 automated structural/pedagogical validator    │
└──────────────────────────┬─────────────────────────────┘
                            │ Authoring Contract (schema + validator)
                            ▼
┌────────────────────────────────────────────────────────┐
│              Workstream 5: Question Bank                 │
│  - Independent content repository, keyed to item_id       │
│  - 6-Stage Validation Pipeline (Section 3)                │
│  - Legacy-Device Asset Budget Guardrails (Section 4, NEW) │
│  - Versioning & Re-Certification Ledger (Section 5)       │
│  - Review Board, distinct from engine/product owner        │
└────────────┬──────────────────────────────┬────────────┘
             │ Validated Items (query-able)  │ Asset Manifests
             ▼                               ▼
┌─────────────────────────┐     ┌─────────────────────────┐
│  Workstream 3: Adaptive  │     │   Workstream 7: Product  │
│   Engine (item retrieval  │     │  / UX (asset rendering,  │
│   per WS4 §8.2 mapping)   │     │  device-capability filter)│
└─────────────────────────┘     └─────────────────────────┘
```

**Structural requirement (Implementation Plan §6, restated as binding for this artifact):** every item lives in this repository keyed to its `item_id`/`target_subskill_id`, independent of the WS3 engine and WS7 product codebases. Content may be added, retired, or re-validated at any time without a WS3 or WS7 release, and no WS3/WS7 release requires re-touching validated content. This document does not own the item schema (WS4 does) and does not own retrieval logic (WS3 does); it owns **content** — the actual authored instances, their assets, and their review history.

---

## 2. Repository & Versioning Structure

### 2.1 Storage Model

Each item is stored as:
- one schema-valid JSON document (WS4 v1.3.0 format), keyed by `item_id`;
- its referenced asset files (SVG, audio, images), stored under a path convention mirroring `item_id`;
- a **validation ledger entry** (Section 5) recording pipeline stage history, reviewer identity/role, dates, and outcome per stage.

Content is never mutated in place. A revision to an existing item creates a new versioned record; the prior version is retired (not deleted) so retrieval history and field-performance data remain attributable.

### 2.2 Repository Independence

The repository is queryable by WS3 (per the WS4 §8.2 field-mapping contract) without WS3 needing to know anything about authoring status, reviewer identity, or asset storage internals — WS3 only ever sees items that have cleared Stage 5 (Section 3) and carry an active version. Items mid-pipeline, retired, or flagged for re-review are excluded from the retrieval-eligible set automatically.

---

## 3. Six-Stage Validation Pipeline

Per Implementation Plan §6.2, each stage is independently re-runnable — an item can be pulled and returned to any stage without restarting the whole pipeline.

### Stage 1 — Spec-Compliance Check (automated)

Runs the WS4 Stage 1 validator (`Stage1ComplianceValidator`, WS4 §6) unmodified — this document does not fork or duplicate that logic. An item cannot proceed to Stage 2 until it returns zero errors, including all rules current at whatever WS4 schema version is authoritative at authoring time (currently v1.3.0, Rules 3.1–3.10).

**Extension for this revision:** Stage 1 also runs the new **Legacy Device Asset Budget** automated check (Section 4.2) as a sibling check to the WS4 validator, not a modification of it. A failure here blocks progression identically to a WS4 Stage 1 failure, but is tracked as a distinct failure category (`ASSET_BUDGET_VIOLATION` vs. `SCHEMA_VIOLATION`) in the ledger, since the two are owned and remediated differently — a schema violation is an authoring-contract fix; an asset-budget violation is usually an asset re-export, not a content rewrite.

### Stage 2 — Pedagogical Review (human, domain-expert reviewer)

Verifies the item actually exercises the `cognitive_depth` and `transfer_level` it claims (not just that those fields are present and internally consistent, which Stage 1 already checked). Reviewer confirms:
- the item's `challenge_type` (if not `STANDARD`) genuinely reflects one of Master Plan §19's challenge forms rather than merely being harder;
- the `creation_stage` tag matches the actual cognitive demand of the Answering→Creating progression (Master Plan §21);
- scaffolding tiers (WS4 §4) preserve productive struggle at Level 1 and don't leak the answer.

### Stage 3 — Content Accuracy Review (subject-matter expert)

Domain-specific correctness check: mathematical, scientific, linguistic, or factual accuracy of prompt, distractors, and rubric. This reviewer is not required to have pedagogical-design expertise — the two review functions (Stage 2 and Stage 3) are deliberately staffed separately per Implementation Plan §6.1.

### Stage 4 — Child-Appropriateness & Language-Load Review

Confirms: reading level is appropriate to the item's `language_load_class` band (WS4 §3.3's structural ceilings are a schema-level cap, not a certification — this stage is where real age-appropriateness is certified, per WS4's own §2 `allOf` block commentary); cultural neutrality; freedom from anything inconsistent with Master Plan §23 Safeguards (no gamification, no comparison framing, no speed pressure embedded in prompt language).

### Stage 5 — Field / Pilot Validation (empirical)

Item is deployed to a small pilot cohort. Reviewed for:
- actual difficulty and discrimination between mastery stages (does it behave the way its `evidence_archetype`/`transfer_level` predicts?);
- **legacy-device rendering check (Section 4.3, NEW):** at least one pilot session must occur on the reference legacy-device profile (Section 4.1) before an item exits Stage 5, confirming assets actually load and render acceptably, not just that they pass the automated budget check.

Items failing field validation route back to Stage 2 (pedagogical misfit) or Stage 4 (unexpected language-load confound), per Implementation Plan §6.2.

### Stage 6 — Versioning & Re-Certification

Every item is stamped with a validation version and date on exit from Stage 5. Re-review triggers: parent feedback flag, periodic audit cycle, curriculum revision (Curriculum Map version bump affecting the item's subskill), or field-performance drift. A re-triggered item does not lose its retrieval-eligible status until re-review actually fails a stage — this avoids pulling live content for routine audit scheduling alone.

---

## 4. Legacy Device Asset Budget Guardrails (NEW)

### 4.1 Reference Device Profile

To make "the old iPad" a concrete, testable target rather than an ambient worry, this document defines a single reference profile that Stage 1 (automated) and Stage 5 (field) both validate against. WS7 owns the authoritative, evolving device-support matrix; this profile is WS5's frozen snapshot of the *floor* of that matrix, versioned independently so content isn't silently invalidated every time WS7's supported-device list changes.

| Parameter | Reference Floor Value | Rationale |
|---|---|---|
| Browser engine | Legacy WebKit (iOS/iPadOS, ~4 major versions behind current) | Matches WS7's surfaced deployment target; WebKit lags Chromium on several relevant APIs (Web Audio, OffscreenCanvas). |
| Available RAM budget for a single task's assets | ≤ 40 MB decoded, ≤ 8 MB on-disk per item | Older iPad models (2–3 GB total RAM) share memory across the WebView, OS, and background apps; a single task should not risk a tab reload. |
| In-browser ASR (speech recognition) | Not assumed reliable | Matches WS4 §3.5's own rationale for the `TAP_SELECT` guarantee. |
| Canvas / stylus API support | Basic 2D canvas only; no advanced compositing, no `OffscreenCanvas`, no pressure-sensitivity APIs assumed | Legacy WebKit stylus/canvas support is inconsistent below recent OS versions. |
| Audio codec | AAC/MP3 only; no WebM/Opus assumed | WebKit codec support is narrower than Chromium's. |
| Network assumption | Assets are pre-cached/bundled, not assumed to stream reliably | Home wifi variability for the target household context; do not assume a persistent fast connection mid-session. |

This profile is a **floor**, not a target experience — it exists so no authored item silently requires more than the floor allows, not to cap what richer devices can render.

### 4.2 Automated Asset Budget Check (Stage 1 extension)

Runs alongside the WS4 validator, checking every asset referenced in `prompt_structure.visual_assets` and any `modality_configurations` asset URIs:

- **File size:** each individual asset ≤ 2 MB; total assets referenced by one item ≤ 8 MB on-disk (Section 4.1).
- **Format allowlist:** `STATIC_IMAGE` assets must be WebP or JPEG (no unsupported next-gen formats without a fallback); audio must be MP3 or AAC; SVG assets must not embed raster images inline above a size threshold (inline base64 bloats DOM parse cost on constrained WebKit).
- **`DYNAMIC_SVG` complexity budget:** items using `state_bindings` (WS4 §2 `prompt_structure.visual_assets`) are capped at a maximum node/element count and forbidden from nested SMIL animation chains, which have known legacy-WebKit performance cliffs. A simple numeric/positional `state_bindings` object (as in the WS4 §5.1 balance-beam exemplar) is within budget; a densely animated multi-layer scene is not.
- **No blocking synchronous asset loads:** every asset must be declarable as pre-fetchable ahead of task start, consistent with the Section 4.1 "assets pre-cached, not streamed mid-task" assumption.

A failure here is logged as `ASSET_BUDGET_VIOLATION` (Section 3, Stage 1) and is typically resolved by re-exporting the asset (compression, format change, simplifying the SVG), not by rewriting the pedagogical content — the two failure classes are tracked separately in the ledger precisely so this distinction is visible to whoever picks up the fix.

### 4.3 Field Validation on the Reference Device (Stage 5 extension)

Automated budget checks catch payload size and format; they cannot catch actual dropped frames, memory-pressure reloads, or touch-latency degradation under real conditions. Before any item exits Stage 5:

1. At least one pilot session for that item must run on hardware matching or falling below the Section 4.1 reference profile (a maintained physical device pool, not emulation alone — WebKit emulation on desktop is not a reliable proxy for iPad memory-pressure behavior).
2. The reviewer confirms: asset load completes before the item's `estimated_duration_seconds` budget is meaningfully consumed by waiting; no visible frame-rate degradation during any `DYNAMIC_SVG` state transition; touch response for `TAP_SELECT` (the guaranteed fallback modality, WS4 Rule 3.10) remains responsive.
3. A failure here routes the item back to Stage 1 asset remediation, not to Stages 2–4 — this is a delivery-fidelity failure, not a pedagogical or content-accuracy one, and should not consume domain-expert or child-safety reviewer time.

### 4.4 What This Section Deliberately Does Not Do

This guardrail governs **content authoring** only. It does not:
- change WS4's schema, modality enum, or Rule 3.10 (that guarantee — every item carries `TAP_SELECT` — already exists and is unmodified here);
- assign WS5 any runtime device-detection responsibility (that remains WS7's, per WS3 §7's explicit boundary statement and WS4 §8.2's device-capability filtering note — WS5 constrains what gets *authored*, WS7 decides what gets *served* to a given device at runtime);
- redefine any pedagogical field (`cognitive_depth`, `transfer_level`, `evidence_archetype`, `challenge_type` are all untouched by this section, consistent with how WS4 §3.5 scoped its own equivalent modality guarantee).

---

## 5. Versioning & Re-Certification Ledger

Every item's ledger entry records, per stage: reviewer identity/role, date, outcome (pass / fail / routed-back), and — for Stage 1 — whether a failure was `SCHEMA_VIOLATION` or `ASSET_BUDGET_VIOLATION` (Section 3, Section 4.2). Re-certification triggers (Section 3, Stage 6) are logged the same way a first-pass review is, so an item's full history — including any legacy-device remediation cycles — remains inspectable without needing to consult WS7 or WS3 systems.

---

## 6. Ownership

Per Implementation Plan §6.3, the Question Bank has its own review board, distinct from the WS3 engine owner and the WS7 product owner. This revision adds one narrow addendum: the **Legacy Device Asset Budget** (Section 4) is owned jointly by the Question Bank review board and a WS7-nominated device-support liaison, since Section 4.1's reference profile must track WS7's actual supported-device floor over time without WS5 needing to re-litigate device strategy on every authoring cycle. The liaison's role is limited to keeping Section 4.1 current; it does not grant WS7 authority over pedagogical, content-accuracy, or child-appropriateness sign-off (Stages 2–4), which remain solely Question Bank board functions.

---

## 7. WS5 Verification & Compliance Audit

| Guardrail | Verification | Source |
|---|---|---|
| **Independent, re-validatable content artifact** | Repository keyed to `item_id`, versioned independently of WS3/WS7 releases; items addable/retirable without a product deploy. | Implementation Plan §6 |
| **Six-stage pipeline, each independently re-runnable** | Sections 3.1–3.6; failed items route back to the specific stage responsible, not to the start of the pipeline. | Implementation Plan §6.2 |
| **Schema compliance unmodified/undupicated** | Stage 1 runs WS4's `Stage1ComplianceValidator` directly; WS5 does not fork or re-implement it. | WS4 §6 |
| **Separate expertise, separate stages** | Pedagogical (Stage 2), content-accuracy (Stage 3), and child-safety/language-load (Stage 4) reviewers are distinct roles. | Implementation Plan §6.1 |
| **Legacy-device asset budget enforced pre-authoring-exit** | New Stage 1 automated check (§4.2) plus mandatory Stage 5 on-device field validation (§4.3) before an item is retrieval-eligible. | WS3 V1.3 §7; WS4 V1.3 §3.5/Rule 3.10 (motivating context) |
| **Device concern scoped to authoring, not runtime** | §4.4 explicitly confirms no WS4 schema change, no WS5 runtime device-detection responsibility; WS7 retains all runtime filtering. | WS3 V1.3 §7; WS4 V1.3 §8.2 |
| **No pedagogical field redefinition** | `cognitive_depth`, `transfer_level`, `evidence_archetype`, `challenge_type` untouched by Section 4. | Master Plan §25.5, §25.8 |
| **Ownership distinct from engine/product** | Question Bank review board separate from WS3/WS7 owners; WS7 liaison role limited to Section 4.1 currency only. | Implementation Plan §6.3 |
| **Full audit trail including device remediation** | Ledger (Section 5) distinguishes `SCHEMA_VIOLATION` from `ASSET_BUDGET_VIOLATION` and logs all re-certification cycles. | Implementation Plan §6.2 |

---

## 8. Open Items for Next Revision

- **Section 4.1 profile currency:** the reference device profile is a snapshot; it should be reviewed against WS7's actual supported-device matrix once WS7 is drafted, and updated via the joint-ownership mechanism in Section 6 rather than unilaterally by either side.
- **Physical device pool logistics** for Stage 5 field validation (Section 4.3) — sourcing, maintaining, and rotating reference hardware is an operational detail intentionally left open here, consistent with Master Plan §27's exclusion of implementation mechanics from upstream documents.
- **Initial authoring priority order** — not specified here; recommend starting with Essential Foundation subskills (Curriculum Map §16.3) given their downstream dependency weight, but this is a scheduling decision for whoever staffs Stage 2–4 review capacity first, not an architectural one.
