# QUESTION SPECIFICATION LAYER — VERSION 1.3 (IMPLEMENTATION READY)

**Derived from:** Pedagogical Master Plan V4.1 (Sections 3.6, 3.10, 4, 8, 16, 17, 19, 21, 25), Implementation Plan V1.0 (Section 5), Curriculum Map V1.0 (187 Subskills), Assessment & Mastery Framework V0.5 (Workstream 2), and Adaptive Learning Design V1.3 (Workstream 3)
**Implementation Stage:** Workstream 4 (Implementation Plan V1.0, Section 5)
**Upstream Inputs:** Subskill IDs and Prerequisite Network from Curriculum Map V1.0; Evidence Archetypes and Modality Guardrails from Assessment Framework V0.5; `TaskRequestPayload` from Adaptive Learning Design V1.3
**Downstream Consumers:** Question Bank Repository & Validation Pipelines (Workstream 5); UI Rendering & Interaction Runtime (Workstream 7)
**Governing Rule:** Workstream 4 serves as the formal architectural contract and authoring schema interface between pedagogical requirements and content authoring. Items authored against this specification are completely decoupled from runtime execution engines and can be authored, reviewed, and mechanically validated independently of product releases. Per Implementation Plan Section 9, changes to this schema require joint sign-off from the Assessment Framework owner (WS2) and Question Bank owner (WS5), with WS4 acting as schema steward.

> **Change note (1.0 → 1.1):**
> 
> 1. **Regex Character-Class Bug Fixed (Section 2, Section 6):** `item_id` and `target_subskill_id` patterns used `[M|E|S|L|W]`, a character class that (harmlessly but incorrectly) also matches a literal `|` character. Corrected to `[MESLW]` in both the JSON Schema and the Python validator.
> 2. **`has_unvoiced_text` Universal Constraint Corrected (Section 2, Section 3.3):** V1.0 hard-coded `has_unvoiced_text` to `const: false` for *every* item, meaning 100% of displayed text was required to carry audio narration. This directly contradicted the document's own §3.3 prose, which mandates mandatory narration only for `PURE_REASONING` items, and it structurally made it impossible to ever author a schema-valid item for the entire Phonological Awareness/Decoding or Reading Fluency strands (`E-PD-01`–`06`, `E-RF-01`–`05`), whose entire pedagogical point (Master Plan §11.2, §16; Curriculum Map §7.2/§7.5) is that the child reads *unvoiced* text — narrating the word away would invalidate the exact construct being assessed. Fixed via a conditional (`allOf`/`if`-`then`) schema block: narration remains mandatory only when `language_load_class = PURE_REASONING`; for `INTEGRATED_LANGUAGE_AND_REASONING` items, `has_unvoiced_text` may be authored `true` or `false` per pedagogical intent, consistent with Master Plan §16's framing of such tasks as "integrated language-and-reasoning experiences." A new exemplar (§5.4) demonstrates this working for a decoding item.
> 3. **`reading_grade_level` Universal Ceiling Corrected (Section 2, Section 3.3):** V1.0 hard-capped `reading_grade_level` at 1.5 for every item regardless of `language_load_class`, contradicting the Master Plan's explicit content-acceleration principle (§3.1, §14) and the Curriculum Map's Enrichment/Advanced tier, which by design requires more complex language for `INTEGRATED_LANGUAGE_AND_REASONING` items (e.g., `E-CR-08`, `E-CR-09`, `E-SG-05`, `E-VM-06`). Fixed via the same conditional schema block: a strict ≤1.0 ceiling now applies only to `PURE_REASONING` items (where §16 explicitly requires linguistic load minimized so it cannot confound reasoning), while `INTEGRATED_LANGUAGE_AND_REASONING` items carry a looser structural ceiling (≤6.0) with actual age-appropriateness certified by the Question Bank's Stage 4 human review (Implementation Plan §6.2), rather than by an arbitrary schema number.
> 4. **WS2 Contract Naming Reconciled (Section 8):** Assessment Framework V0.4 §6 describes the metadata WS4 owns as `intended_transfer_level` and `intended_modality`. WS4's actual schema fields are named `transfer_level`, `primary_modality`, and `supported_alternative_modalities` — an unreconciled naming drift between two documents that both claim to be authoritative on this contract. Section 8 now states the mapping explicitly.
> 5. **Stage 1 Validator: Missing Archetype Cross-Check Added (Section 6):** V1.0's validator confirmed `evidence_archetype` was *a* valid enum value but never checked it was *the correct* one for the item's `target_subskill_id` per WS2 §3.1's canonical mapping — an author could tag an `M-OP-05` item `CREATIVE_GENERATIVE` and Stage 1 would pass it. Added a cross-check against WS2's canonical map, loaded from the shared upstream source rather than re-hardcoded in WS4, to avoid the exact kind of drifting-duplicate-table problem WS2 itself had to correct in its 0.3→0.4 revision.
> 6. **Stage 1 Validator: Vacuous Rule 3.3 Tightened (Section 6):** Because `supported_alternative_modalities` already requires `minItems: 1` for every item at the schema level, the old Rule 3.3 ("HANDWRITTEN_STYLUS must provide at least one alternative modality") could never actually fail — it was dead code. Rewritten to check what WS2 §2.1 actually requires: a HANDWRITTEN_STYLUS item's alternatives must include at least one genuinely low-motor-load modality (`TAP_SELECT` or `SPOKEN_DICTATED`), since WS2 defines graphomotor fatigue as routing specifically to oral/visual verification.
> 7. **Stage 1 Validator: `item_id` / `target_subskill_id` Consistency Check Added (Section 6):** Nothing previously verified that an item's `item_id` (e.g., `ITEM-M-OP-05-0042`) actually embeds its own `target_subskill_id` (e.g., `M-OP-05`) — the two fields could silently diverge. Added as a new Stage 1 rule.
> 8. **WS3 → WS4 Item Retrieval Field Mapping Added (new Section 8):** V1.0's architecture diagram labeled the WS3-facing arrow "Item Retrieval Contract" but never defined it. WS3 V1.1's `TaskRequestPayload` (its §7) uses field names (`task_function_type`, `required_cognitive_depth`, `target_transfer_level`, `permitted_modalities`, `restricted_modalities`, `support_branch`, etc.) that don't literally match WS4's schema field names, and nothing stated how a request is actually satisfied by a query against authored items. Section 8 now specifies this mapping explicitly.

> **Change note (1.1 → 1.2):**
> 9. **Audio URI Whitespace Guard (Section 2, Section 6):** The 1.1 validator check `if not prompt.get("spoken_audio_uri"):` catches an empty string but not a whitespace-only string (e.g., `" "`), which is truthy and would silently pass. Added `"minLength": 1` to `spoken_audio_uri` inside the `PURE_REASONING` conditional schema block (Section 2) as a first-line structural guard, and changed the Python check to `if not prompt.get("spoken_audio_uri", "").strip():` (Section 6, Rule 3.2) as the actual enforcement, since JSON Schema's `minLength` does not trim whitespace and cannot catch a whitespace-only string on its own.
> 10. **Modality Configuration Completeness Enforced (Section 6, new Rule 3.8):** Nothing previously verified that every modality named in `primary_modality` or `supported_alternative_modalities` actually had a corresponding entry under `interaction_model.modality_configurations` — an item could declare `SPOKEN_DICTATED` as a supported modality with no `spoken_dictated` configuration object beneath it, passing Stage 1 and failing only at runtime in Workstream 7. Added Rule 3.8, which checks every declared modality against its expected `modality_configurations` key.
> 11. **`rubric.correct_criteria` Shape Constrained by `evaluation_mode` (Section 2, Section 6):** `correct_criteria` was an unconstrained object regardless of `evaluation_mode`, so a `SEMANTIC_CONCEPT_KEYWORD_MATCH` item could omit `matched_concepts` entirely and still validate. Added two new `allOf` conditional blocks (Section 2) plus a matching Rule 3.9 (Section 6) requiring: `DETERMINISTIC_EXACT_MATCH` → one of `selected_option_id` / `target_word` / `target_value`; `SEMANTIC_CONCEPT_KEYWORD_MATCH` → one of `matched_concepts` / `target_semantic_clusters`; `TOPOLOGICAL_RELATIONAL_MATCH` → `topology_graph`; `CONSTRAINT_SATISFACTION_CHECK` → `constraint_set`. The latter two keys are newly defined in Section 3.4, since the exemplars in Section 5 had never exercised those two evaluation modes and no shape existed for them to validate against.
> 12. **Pre-Existing Exemplar Bug Found and Fixed (Section 5.3):** Running the completed validator against every exemplar for the first time (see verification note below) surfaced that the `L-RC-04` Logic exemplar had never actually been schema-valid: its `display_text` was 15 words under `PURE_REASONING` (limit 8, per §3.3 — this limit predates 1.2 and was simply never checked against this exemplar), and it declared `DRAW_DIAGRAM` as a supported alternative modality with no matching `modality_configurations.draw_diagram` entry (a gap Rule 3.8 now catches). `display_text` was shortened to 7 words and the alternative modality changed to `SPOKEN_DICTATED` (with a matching config block added), which is also the more natural alternative for a single-choice selection task.
> 
> **Verification:** All four Section 5 exemplars and the schema itself were mechanically checked for this revision — every JSON block parses, the Python validator compiles and runs, and `validate_item()` returns zero errors for all four exemplars post-fix.

> **Change note (1.2 → 1.3):**
> 
> 1. **Device-Universal Fallback Modality Guaranteed (Section 2, Section 3.3, Section 6):** Product/UX (Workstream 7) has surfaced a low-memory legacy-device deployment target (dated WebKit, no reliable in-browser ASR, unsupported canvas/stylus APIs) that this schema's existing modality machinery does not, by itself, guarantee coverage for. WS2 §2.1's alternative-modality routing and this document's `supported_alternative_modalities` requirement (Rule 3.3) exist to solve *motor/expressive* confounds in a 6-year-old (e.g., stylus fatigue → route to speech or tap) — they were never designed to guarantee a modality that is renderable on every runtime. It was previously legal, for example, for an item to declare `primary_modality: HANDWRITTEN_STYLUS` with `supported_alternative_modalities: [SPOKEN_DICTATED]` only; on a device without usable ASR, that item has zero deliverable modality. **New Rule 3.10** (Section 6) and a new top-level schema constraint (Section 2) now require every item to carry `TAP_SELECT` as either its `primary_modality` or within `supported_alternative_modalities`, since `TAP_SELECT` has no microphone, canvas, or stylus dependency and is renderable on effectively any touch or pointer-capable runtime. This is a content-authoring guarantee, not a UI or pedagogical decision — it does not change `cognitive_depth`, `transfer_level`, `evidence_archetype`, or any pedagogical field, and does not require WS1, WS2, WS3, or Master Plan changes. All four Section 5 exemplars already satisfy this constraint without modification (verified below).

---

## 1. Architectural Position & Boundary Constraints

The Question Specification Layer establishes a strict, typed schema that all authorable content items must satisfy. Decoupling question authoring from the adaptive engine ensures that subject-matter correctness, child cognitive load, and pedagogical integrity can be audited independently.

```
┌─────────────────────────────────────────────────────────────────┐
│                    Curriculum Map (WS1, V1.0)                   │
│         - 187 Explicit Subskill IDs                             │
│         - Required / Supportive Prerequisite Dependency Graph   │
└───────────────────────────────┬─────────────────────────────────┘
                                │ Subskill IDs & Graph
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│           Workstream 4: Question Specification Layer            │
│  - Universal Item JSON Schema Specification (Draft 2020-12)     │
│  - Field Taxonomies & Controlled Vocabularies                   │
│  - Multimodal Delivery Payload & Asset Interaction Contracts     │
│  - 3-Tier Scaffolding & Metacognitive Protocol Contracts        │
│  - Child Construct-Load & Language Isolation Guardrails         │
│  - Stage 1 Automated Schema Compliance Validator               │
└───────────────┬─────────────────────────────────┬───────────────┘
                │ Authoring Contract              │ Item Retrieval Contract
                │                                  │ (field mapping: Section 8)
                ▼                                 ▼
┌───────────────────────────────┐ ┌───────────────────────────────┐
│ Workstream 5: Question Bank   │ │ Workstream 3: Adaptive Engine │
│ - Authoring & Review Pipeline │ │ - Task Selector & Dispatcher  │
│ - Independent Content Storage │ │ - Dynamic Payload Assembly    │
└───────────────────────────────┘ └───────────────────────────────┘
```

---

## 2. Universal Question Specification Schema (JSON Schema Draft 2020-12)

Every task authored for the platform must strictly validate against the JSON Schema below:

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "QuestionSpecification",
  "type": "object",
  "required": [
    "item_id",
    "schema_version",
    "target_subskill_id",
    "domain_id",
    "evidence_archetype",
    "cognitive_depth",
    "transfer_level",
    "primary_modality",
    "supported_alternative_modalities",
    "language_load_class",
    "representation_type",
    "challenge_type",
    "creation_stage",
    "estimated_duration_seconds",
    "prompt_structure",
    "interaction_model",
    "scaffolding_protocol",
    "rubric",
    "safeguard_metadata"
  ],
  "properties": {
    "item_id": {
      "type": "string",
      "pattern": "^ITEM-[MESLW]-[A-Z]{2}-[0-9]{2}-[0-9]{4}$",
      "description": "Unique identifier conforming to Domain-Strand-Skill-Sequence format. (1.1: character class corrected from [M|E|S|L|W] to [MESLW].)"
    },
    "schema_version": {
      "type": "string",
      "enum": ["1.0.0", "1.1.0", "1.2.0"."1.3.0"]
    },
    "target_subskill_id": {
      "type": "string",
      "pattern": "^[MESLW]-[A-Z]{2}-[0-9]{2}$",
      "description": "Must match one of the 187 Curriculum Map V1.0 skill identifiers. (1.1: character class corrected from [M|E|S|L|W] to [MESLW].)"
    },
    "domain_id": {
      "type": "string",
      "enum": [
        "MATHEMATICS",
        "ENGLISH_LANGUAGE",
        "SCIENCE_EVS",
        "LOGICAL_REASONING",
        "WORLD_KNOWLEDGE"
      ]
    },
    "evidence_archetype": {
      "type": "string",
      "enum": [
        "CONCEPTUAL",
        "PROCEDURAL_FLUENCY",
        "KNOWLEDGE_ACQUISITION",
        "STRATEGIC_REASONING",
        "CREATIVE_GENERATIVE"
      ],
      "description": "Inherited from Assessment Framework V0.4 §3.1. Must equal the canonical archetype WS2 assigns to target_subskill_id (enforced by Stage 1 validator, Section 6, Rule 3.6 — not by this enum alone, since the enum only checks membership, not correctness for the specific subskill)."
    },
    "cognitive_depth": {
      "type": "string",
      "enum": ["UNDERSTAND", "APPLY", "REASON", "GENERALIZE", "CREATE"],
      "description": "Master Plan Axis 2 depth classification."
    },
    "transfer_level": {
      "type": "string",
      "enum": [
        "LEVEL_1_SURFACE",
        "LEVEL_2_CONTEXTUAL",
        "LEVEL_3_REPRESENTATIONAL",
        "LEVEL_4_STRUCTURAL",
        "LEVEL_5_NOVEL"
      ],
      "description": "Master Plan Section 8 Transfer taxonomy. Equivalent to what Assessment Framework V0.4 §6 calls intended_transfer_level — see Section 8 for the explicit cross-document field-name mapping."
    },
    "primary_modality": {
      "type": "string",
      "enum": [
        "TAP_SELECT",
        "DRAW_DIAGRAM",
        "SPOKEN_DICTATED",
        "TYPED_KEYBOARD",
        "HANDWRITTEN_STYLUS"
      ],
      "description": "Together with supported_alternative_modalities, equivalent to what Assessment Framework V0.4 §6 calls intended_modality — see Section 8 for the explicit cross-document field-name mapping."
    },
    "supported_alternative_modalities": {
      "type": "array",
      "minItems": 1,
      "items": {
        "type": "string",
        "enum": [
          "TAP_SELECT",
          "DRAW_DIAGRAM",
          "SPOKEN_DICTATED",
          "TYPED_KEYBOARD",
          "HANDWRITTEN_STYLUS"
        ]
      }
    },
    "language_load_class": {
      "type": "string",
      "enum": ["PURE_REASONING", "INTEGRATED_LANGUAGE_AND_REASONING"],
      "description": "Master Plan Section 16 construct-load isolation. Also gates safeguard_metadata.has_unvoiced_text and safeguard_metadata.reading_grade_level via the allOf conditional block below (1.1)."
    },
    "representation_type": {
      "type": "string",
      "enum": ["CONCRETE", "VISUAL", "VERBAL", "SYMBOLIC", "ABSTRACT"]
    },
    "challenge_type": {
      "type": "string",
      "enum": [
        "STANDARD",
        "UNFAMILIAR_CONTEXT",
        "INCOMPLETE_INFORMATION",
        "MULTIPLE_SOLUTIONS",
        "CONFLICTING_EVIDENCE",
        "NEW_REPRESENTATION",
        "STRATEGY_SELECTION"
      ]
    },
    "creation_stage": {
      "type": "string",
      "enum": [
        "NONE",
        "ANSWERING",
        "EXPLAINING",
        "MODIFYING",
        "GENERATING",
        "CREATING"
      ]
    },
    "estimated_duration_seconds": {
      "type": "integer",
      "minimum": 15,
      "maximum": 300
    },
    "prompt_structure": {
      "type": "object",
      "required": ["spoken_audio_uri", "display_text", "visual_assets"],
      "properties": {
        "spoken_audio_uri": { "type": "string" },
        "display_text": { "type": "string" },
        "visual_assets": {
          "type": "array",
          "items": {
            "type": "object",
            "required": ["asset_id", "asset_type", "uri"],
            "properties": {
              "asset_id": { "type": "string" },
              "asset_type": {
                "type": "string",
                "enum": ["STATIC_SVG", "DYNAMIC_SVG", "STATIC_IMAGE", "INTERACTIVE_CANVAS"]
              },
              "uri": { "type": "string" },
              "state_bindings": { "type": "object" }
            }
          }
        }
      }
    },
    "interaction_model": {
      "type": "object",
      "required": ["input_mechanic", "modality_configurations"],
      "properties": {
        "input_mechanic": {
          "type": "string",
          "enum": [
            "SINGLE_CHOICE",
            "MULTIPLE_CHOICE",
            "ORDERING_SEQUENCE",
            "CANVAS_DRAW_OR_CONNECT",
            "ASR_SPEECH_RESPONSE",
            "NUMBER_PAD_ENTRY",
            "OPEN_TEXT_KEYBOARD",
            "STYLUS_FREE_DRAW"
          ]
        },
        "modality_configurations": { "type": "object" }
      }
    },
    "scaffolding_protocol": {
      "type": "object",
      "required": [
        "level_1_reflection_prompt",
        "level_2_representation_shift",
        "level_3_prerequisite_bridge"
      ],
      "properties": {
        "level_1_reflection_prompt": {
          "type": "object",
          "required": ["spoken_text", "pedagogical_target", "preserves_productive_struggle"],
          "properties": {
            "spoken_text": { "type": "string" },
            "pedagogical_target": { "type": "string" },
            "preserves_productive_struggle": { "type": "boolean", "const": true }
          }
        },
        "level_2_representation_shift": {
          "type": "object",
          "required": ["spoken_text", "target_representation"],
          "properties": {
            "spoken_text": { "type": "string" },
            "target_representation": {
              "type": "string",
              "enum": ["CONCRETE", "VISUAL", "VERBAL", "SYMBOLIC", "ABSTRACT"]
            },
            "visual_asset_override": { "type": "string" }
          }
        },
        "level_3_prerequisite_bridge": {
          "type": "object",
          "required": ["spoken_text", "target_prerequisite_subskill_id"],
          "properties": {
            "spoken_text": { "type": "string" },
            "target_prerequisite_subskill_id": { "type": "string" },
            "interactive_overlay": { "type": "string" }
          }
        }
      }
    },
    "rubric": {
      "type": "object",
      "required": ["evaluation_mode", "correct_criteria", "diagnostic_distractors"],
      "properties": {
        "evaluation_mode": {
          "type": "string",
          "enum": [
            "DETERMINISTIC_EXACT_MATCH",
            "TOPOLOGICAL_RELATIONAL_MATCH",
            "SEMANTIC_CONCEPT_KEYWORD_MATCH",
            "CONSTRAINT_SATISFACTION_CHECK"
          ]
        },
        "correct_criteria": { "type": "object" },
        "diagnostic_distractors": {
          "type": "array",
          "items": {
            "type": "object",
            "required": ["response_pattern", "diagnostic_misconception", "recommended_ws3_branch"],
            "properties": {
              "response_pattern": { "type": "string" },
              "diagnostic_misconception": { "type": "string" },
              "recommended_ws3_branch": {
                "type": "string",
                "enum": [
                  "PREREQUISITE_STRENGTHENING",
                  "PRODUCTIVE_STRUGGLE_PROTECT",
                  "STRATEGY_REFLECTION_PIVOT",
                  "LOAD_REDUCTION"
                ]
              }
            }
          }
        }
      }
    },
    "safeguard_metadata": {
      "type": "object",
      "required": [
        "reading_grade_level",
        "has_unvoiced_text",
        "cultural_neutrality_verified",
        "contains_gamified_dark_patterns"
      ],
      "properties": {
        "reading_grade_level": {
          "type": "number",
          "minimum": 0,
          "description": "Base type only; the actual ceiling is language_load_class-dependent — see the allOf conditional block below (1.1)."
        },
        "has_unvoiced_text": {
          "type": "boolean",
          "description": "Base type only; whether this may be true is language_load_class-dependent — see the allOf conditional block below (1.1)."
        },
        "cultural_neutrality_verified": { "type": "boolean", "const": true },
        "contains_gamified_dark_patterns": { "type": "boolean", "const": false }
      }
    }
  },
  "allOf": [
    {
      "description": "1.1 FIX: PURE_REASONING items must minimize construct-irrelevant reading load (Master Plan §16) — narration stays mandatory and reading level stays near-zero. 1.2 FIX: spoken_audio_uri must be non-empty, not merely present (minLength alone cannot catch a whitespace-only string — see Rule 3.2 in Section 6 for the actual enforcement).",
      "if": {
        "properties": { "language_load_class": { "const": "PURE_REASONING" } }
      },
      "then": {
        "properties": {
          "prompt_structure": {
            "type": "object",
            "properties": {
              "spoken_audio_uri": { "minLength": 1 }
            }
          },
          "safeguard_metadata": {
            "type": "object",
            "properties": {
              "has_unvoiced_text": { "const": false },
              "reading_grade_level": { "maximum": 1.0 }
            }
          }
        }
      }
    },
    {
      "description": "1.1 FIX: INTEGRATED_LANGUAGE_AND_REASONING items measure language itself as the construct (Master Plan §16), so neither mandatory narration nor a near-zero reading ceiling is appropriate. A structural ceiling of 6.0 still bounds authoring; actual age-appropriateness is certified by Question Bank Stage 4 human review (Implementation Plan §6.2), not by this schema alone.",
      "if": {
        "properties": { "language_load_class": { "const": "INTEGRATED_LANGUAGE_AND_REASONING" } }
      },
      "then": {
        "properties": {
          "safeguard_metadata": {
            "type": "object",
            "properties": {
              "reading_grade_level": { "maximum": 6.0 }
            }
          }
        }
      }
    },
    {
      "description": "1.2 FIX (Rule 3.9): DETERMINISTIC_EXACT_MATCH items must carry a recognizable exact-match key in correct_criteria, not an arbitrary unconstrained object.",
      "if": {
        "properties": {
          "rubric": {
            "properties": { "evaluation_mode": { "const": "DETERMINISTIC_EXACT_MATCH" } }
          }
        }
      },
      "then": {
        "properties": {
          "rubric": {
            "properties": {
              "correct_criteria": {
                "anyOf": [
                  { "required": ["selected_option_id"] },
                  { "required": ["target_word"] },
                  { "required": ["target_value"] }
                ]
              }
            }
          }
        }
      }
    },
    {
      "description": "1.2 FIX (Rule 3.9): SEMANTIC_CONCEPT_KEYWORD_MATCH items must carry a matchable concept/keyword set in correct_criteria.",
      "if": {
        "properties": {
          "rubric": {
            "properties": { "evaluation_mode": { "const": "SEMANTIC_CONCEPT_KEYWORD_MATCH" } }
          }
        }
      },
      "then": {
        "properties": {
          "rubric": {
            "properties": {
              "correct_criteria": {
                "anyOf": [
                  { "required": ["matched_concepts"] },
                  { "required": ["target_semantic_clusters"] }
                ]
              }
            }
          }
        }
      }
    },
    {
      "description": "1.2 FIX (Rule 3.9): TOPOLOGICAL_RELATIONAL_MATCH items must carry an explicit topology_graph definition (Section 3.4) in correct_criteria.",
      "if": {
        "properties": {
          "rubric": {
            "properties": { "evaluation_mode": { "const": "TOPOLOGICAL_RELATIONAL_MATCH" } }
          }
        }
      },
      "then": {
        "properties": {
          "rubric": {
            "properties": {
              "correct_criteria": { "required": ["topology_graph"] }
            }
          }
        }
      }
    },
    {
      "description": "1.2 FIX (Rule 3.9): CONSTRAINT_SATISFACTION_CHECK items must carry an explicit constraint_set definition (Section 3.4) in correct_criteria.",
      "if": {
        "properties": {
          "rubric": {
            "properties": { "evaluation_mode": { "const": "CONSTRAINT_SATISFACTION_CHECK" } }
          }
        }
      },
      "then": {
        "properties": {
          "rubric": {
            "properties": {
              "correct_criteria": { "required": ["constraint_set"] }
            }
          }
        }
      }
    },
    {
      "description": "1.3 NEW: every item must carry a device-universal fallback modality. TAP_SELECT has no microphone, canvas, or stylus dependency and is renderable on effectively any touch/pointer-capable runtime, including low-memory legacy devices. This is independent of, and in addition to, the existing motor/expressive alternative-modality requirement (minItems:1 on supported_alternative_modalities) — that requirement guarantees *an* alternative exists; this requirement guarantees the device-universal one specifically is always among the options. Enforced structurally here via anyOf, and redundantly in Python as Rule 3.10 (Section 6) for validators that do not run a full JSON-Schema-draft-2020-12 implementation.",
      "anyOf": [
        { "properties": { "primary_modality": { "const": "TAP_SELECT" } } },
        { "properties": { "supported_alternative_modalities": { "contains": { "const": "TAP_SELECT" } } } }
      ]
    }
  ]
}
```

---

## 3. Controlled Taxonomies & Master Plan Grounding

Every enumeration field in the schema implements an explicit mandate from the upstream architectural source documents.

### 3.1 Cognitive Depth Taxonomy (Master Plan Axis 2)

Per Master Plan Section 4, Cognitive Depth operates independently of Content Progression:

| Depth Level  | Operational Meaning                                                      | Authoring Directive for Task Designers                                                                      |
|:------------ |:------------------------------------------------------------------------ |:----------------------------------------------------------------------------------------------------------- |
| `UNDERSTAND` | Direct concept identification, classification, or decoding.              | Prompt requires recognizing defining features, core meanings, or relationships without procedure execution. |
| `APPLY`      | Standard procedure execution in familiar, routine context.               | Computation, routine passage reading, direct non-standard measurement.                                      |
| `REASON`     | Multi-constraint analysis, contradiction detection, deductive logic.     | Requires eliminating invalid options, evaluating cause/effect, or strategy switching.                       |
| `GENERALIZE` | Inductive invariant extraction; stating abstract rules across instances. | Requires learner to identify or select the governing underlying pattern across multiple cases.              |
| `CREATE`     | Open-ended formulation, model construction, alternative hypotheses.      | Requires generating problems, modifying constraints, or synthesizing cross-domain models.                   |

### 3.2 Transfer Level Taxonomy (Master Plan Section 8)

| Transfer Level             | Taxonomy Definition                                              | Invariant vs Variant Dimensions                                                                   |
|:-------------------------- |:---------------------------------------------------------------- |:------------------------------------------------------------------------------------------------- |
| `LEVEL_1_SURFACE`          | Minor surface asset or numerical changes; identical format.      | Invariant: Logical structure & visual layout. Variant: Literal values (e.g., 4+2 to 5+3).         |
| `LEVEL_2_CONTEXTUAL`       | Invariant principle embedded in a novel narrative context.       | Invariant: Conceptual relationship. Variant: Narrative story setting / domain context.            |
| `LEVEL_3_REPRESENTATIONAL` | Invariant relational concept across disparate representations.   | Invariant: Relational structure. Variant: Mode of representation (e.g., discrete to number line). |
| `LEVEL_4_STRUCTURAL`       | Superficial structure altered; deep relational mapping required. | Invariant: Abstract systemic logic. Variant: Complete physical/visual problem topology.           |
| `LEVEL_5_NOVEL`            | Unprompted identification & application in a non-routine system. | Invariant: Generalized meta-strategy. Variant: Highly unfamiliar, unprimed context.               |

### 3.3 Language-Load & Construct-Isolation Classes (Master Plan Section 16, Principle 25.1)

To prevent reading barriers from acting as a construct confound for young children:

* `PURE_REASONING`: Reading demands are strictly non-construct-relevant. Spoken audio narration is mandatory for all text (`has_unvoiced_text` must be `false`). Displayed prompt text must not exceed 8 simple words. `reading_grade_level` is capped at 1.0. Visual/spatial/symbolic models carry the entire cognitive task.
* `INTEGRATED_LANGUAGE_AND_REASONING`: Linguistic comprehension is itself part of the measured construct (e.g., vocabulary nuance, reading inferences, syntactic ambiguity, or — at the more basic end of this same principle — phonics and decoding, where the child reading unvoiced text *is* the construct). Because narration or reading-level suppression would erase the very thing being measured, these items are **not** required to be fully narrated (`has_unvoiced_text` may be `true`) and carry a higher structural `reading_grade_level` ceiling (6.0) than `PURE_REASONING` items. *(1.1: this bullet was previously silent on `has_unvoiced_text` and `reading_grade_level`, while the JSON Schema in Section 2 contradicted it by forcing both to the strictest `PURE_REASONING` values universally. The two are now aligned via the `allOf` conditional block in Section 2.)*

### 3.4 `correct_criteria` Shape by `evaluation_mode` (NEW in 1.2)

V1.1 left `rubric.correct_criteria` an unconstrained object regardless of `rubric.evaluation_mode`, so nothing stopped, for example, a `SEMANTIC_CONCEPT_KEYWORD_MATCH` item from omitting `matched_concepts` entirely. The four `evaluation_mode` values now each require a recognizable, minimal key shape, enforced by the `allOf` conditional blocks in Section 2 and mirrored in the Python validator's Rule 3.9 (Section 6):

| `evaluation_mode`                | Required key (at least one, unless noted)               | Shape                                                                                                                                                                                                                                                                                                                              |
|:-------------------------------- |:------------------------------------------------------- |:---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `DETERMINISTIC_EXACT_MATCH`      | `selected_option_id` \| `target_word` \| `target_value` | Scalar string/number — whichever matches the item's `interaction_model.input_mechanic` (e.g., `selected_option_id` for `SINGLE_CHOICE`, `target_word` for `ASR_SPEECH_RESPONSE` decoding items).                                                                                                                                   |
| `SEMANTIC_CONCEPT_KEYWORD_MATCH` | `matched_concepts` \| `target_semantic_clusters`        | Array of strings representing acceptable semantic matches (as already used in the Section 5.2 exemplar).                                                                                                                                                                                                                           |
| `TOPOLOGICAL_RELATIONAL_MATCH`   | `topology_graph` (required)                             | `{ "nodes": [<node_id>...], "edges": [{"from": <node_id>, "to": <node_id>, "relation": <string>}...] }` — used for drawing/diagram items evaluated on relational arrangement rather than pixel-level geometry (WS2 §2.1's Draw/Diagram row: "topological and relational validity evaluated independently of geometric precision"). |
| `CONSTRAINT_SATISFACTION_CHECK`  | `constraint_set` (required)                             | `{ "constraints": [{"applies_to": <string>, "rule": <string>, "negated": <boolean>}...] }` — used for multi-constraint logical-reasoning items (Curriculum Map Domain 4, `L-RC`/`L-CO`/`L-CE` strands) where correctness is "did the response satisfy every listed constraint," not a single exact match.                          |

These two new shapes (`topology_graph`, `constraint_set`) were not previously exercised by any Section 5 exemplar — no authored item in this document used `TOPOLOGICAL_RELATIONAL_MATCH` or `CONSTRAINT_SATISFACTION_CHECK` even though both appear in the `evaluation_mode` enum — so there was no existing precedent to conform to; the shapes above are new and subject to WS2+WS5 joint sign-off like any other schema change (Section 7 governance rule).

### 3.5 Device-Universal Fallback Modality Requirement (NEW in 1.3)

Section 2's `supported_alternative_modalities` (minItems: 1) and WS2 §2.1's routing table guarantee that every item has *some* alternative delivery path for a given child's motor/expressive profile (e.g., a stylus-fatigued child gets routed to speech or tap). They do not guarantee that alternative is renderable on any given piece of hardware. `SPOKEN_DICTATED` depends on a working microphone and an ASR pipeline; `DRAW_DIAGRAM`/`STYLUS_FREE_DRAW` depend on canvas and pointer-event support; `TYPED_KEYBOARD` depends on a software or hardware keyboard surface. `TAP_SELECT` has none of these dependencies — it requires only a basic touch or pointer input, which is why it is the one modality this schema treats as device-universal.

As of 1.3, every item must carry `TAP_SELECT` as either its `primary_modality` or somewhere in `supported_alternative_modalities` (Section 2 `allOf`/`anyOf` block; Section 6 Rule 3.10). This is an **authoring-time content guarantee**, not a runtime UI decision: it ensures that whatever device-capability filtering Workstream 7 performs at render time, a deliverable modality will always exist for every authored item. It does not add, remove, or reinterpret any pedagogical field — an item's `cognitive_depth`, `transfer_level`, `evidence_archetype`, and `challenge_type` are unaffected. Which modality WS3 actually *permits* for a given task request remains a purely pedagogical decision (WS3 §3.1, Branch 4); which of the permitted modalities is *renderable* on the requesting device is a WS7 decision made after the item is retrieved (Section 8.2 note, and WS3 §7 cross-reference).

---

## 4. Scaffolding & Metacognitive Protocol Contracts

Per Master Plan Section 20 and Adaptive Design Section 3, scaffolding must preserve productive struggle and never reduce cognitive demand into passive consumption:

```
[ LEVEL 1: REFLECTION PROMPT ]
  - Injects a self-monitoring pivot ("What do you notice about...?", "What changed?")
  - Preserves 100% of problem complexity; provides zero direct hints or answers.

[ LEVEL 2: REPRESENTATION SHIFT ]
  - Switches cognitive representation (e.g., Symbolic equation -> Visual balance scale)
  - Clarifies relationships without solving the operational task.

[ LEVEL 3: PREREQUISITE BRIDGE ]
  - Overlays an interactive concrete scaffolding tool (e.g., Ten-Frame, Number Path)
  - Directly activates the underlying supportive subskill identified in WS1.
```

Note: `LOAD_REDUCTION` (WS3 Branch 4 — cognitive overload / modality confound, WS3 §3.1) is deliberately **not** a fourth scaffolding tier here. It is handled upstream of scaffolding entirely, via modality substitution (`primary_modality` / `supported_alternative_modalities`) and construct-irrelevant-text stripping (`language_load_class = PURE_REASONING`), before a struggle is ever classified into Branches 1–3. Every authored item still carries all three tiers above regardless of which branch eventually fires at runtime — WS3 decides at runtime whether and which tier to invoke; WS4 only guarantees the tooling exists.

---

## 5. Exemplar Question Specifications Across Domains

### 5.1 Domain 1: Mathematics & Mathematical Thinking

```json
{
  "item_id": "ITEM-M-OP-05-0042",
  "schema_version": "1.3.0",
  "target_subskill_id": "M-OP-05",
  "domain_id": "MATHEMATICS",
  "evidence_archetype": "CONCEPTUAL",
  "cognitive_depth": "REASON",
  "transfer_level": "LEVEL_3_REPRESENTATIONAL",
  "primary_modality": "TAP_SELECT",
  "supported_alternative_modalities": ["SPOKEN_DICTATED"],
  "language_load_class": "PURE_REASONING",
  "representation_type": "VISUAL",
  "challenge_type": "NEW_REPRESENTATION",
  "creation_stage": "ANSWERING",
  "estimated_duration_seconds": 90,
  "prompt_structure": {
    "spoken_audio_uri": "assets/audio/math/m_op_05_0042_prompt.mp3",
    "display_text": "Which block makes the bridge balance?",
    "visual_assets": [
      {
        "asset_id": "balance_beam_01",
        "asset_type": "DYNAMIC_SVG",
        "uri": "assets/svg/balance_beam_7_3.svg",
        "state_bindings": {
          "left_weight": 10,
          "right_weight_known": 7,
          "right_weight_unknown_target": 3
        }
      }
    ]
  },
  "interaction_model": {
    "input_mechanic": "SINGLE_CHOICE",
    "modality_configurations": {
      "tap_select": {
        "options": [
          { "option_id": "opt_1", "display_value": "3", "asset_uri": "assets/svg/block_3.svg" },
          { "option_id": "opt_2", "display_value": "7", "asset_uri": "assets/svg/block_7.svg" },
          { "option_id": "opt_3", "display_value": "10", "asset_uri": "assets/svg/block_10.svg" }
        ]
      },
      "spoken_dictated": {
        "target_tokens": ["three", "3"],
        "acoustic_confidence_threshold": 0.75
      }
    }
  },
  "scaffolding_protocol": {
    "level_1_reflection_prompt": {
      "spoken_text": "Look at the beam. What total number must be on both sides to stay level?",
      "pedagogical_target": "STRATEGY_REFLECTION_PIVOT",
      "preserves_productive_struggle": true
    },
    "level_2_representation_shift": {
      "spoken_text": "The left side has 10 dots. The right side has 7 dots. How many dots are missing?",
      "target_representation": "CONCRETE",
      "visual_asset_override": "assets/svg/ten_frame_comparison_7_10.svg"
    },
    "level_3_prerequisite_bridge": {
      "spoken_text": "Let's count up from 7 to reach 10: 8, 9, 10.",
      "target_prerequisite_subskill_id": "M-NQ-02",
      "interactive_overlay": "INTERACTIVE_COUNTING_BEADS"
    }
  },
  "rubric": {
    "evaluation_mode": "DETERMINISTIC_EXACT_MATCH",
    "correct_criteria": { "selected_option_id": "opt_1" },
    "diagnostic_distractors": [
      {
        "response_pattern": "opt_3",
        "diagnostic_misconception": "EQUALITY_AS_SUM_TOTAL",
        "recommended_ws3_branch": "STRATEGY_REFLECTION_PIVOT"
      },
      {
        "response_pattern": "opt_2",
        "diagnostic_misconception": "IDENTITY_COPYING",
        "recommended_ws3_branch": "STRATEGY_REFLECTION_PIVOT"
      }
    ]
  },
  "safeguard_metadata": {
    "reading_grade_level": 0.8,
    "has_unvoiced_text": false,
    "cultural_neutrality_verified": true,
    "contains_gamified_dark_patterns": false
  }
}
```

### 5.2 Domain 2: English Language & Literacy

```json
{
  "item_id": "ITEM-E-CR-02-0018",
  "schema_version": "1.3.0",
  "target_subskill_id": "E-CR-02",
  "domain_id": "ENGLISH_LANGUAGE",
  "evidence_archetype": "STRATEGIC_REASONING",
  "cognitive_depth": "REASON",
  "transfer_level": "LEVEL_2_CONTEXTUAL",
  "primary_modality": "SPOKEN_DICTATED",
  "supported_alternative_modalities": ["TAP_SELECT"],
  "language_load_class": "INTEGRATED_LANGUAGE_AND_REASONING",
  "representation_type": "VERBAL",
  "challenge_type": "STANDARD",
  "creation_stage": "EXPLAINING",
  "estimated_duration_seconds": 120,
  "prompt_structure": {
    "spoken_audio_uri": "assets/audio/literacy/e_cr_02_0018_prompt.mp3",
    "display_text": "Maya put on her yellow rain boots and grabbed her umbrella. Why did Maya choose an umbrella?",
    "visual_assets": [
      {
        "asset_id": "maya_hallway_scene",
        "asset_type": "STATIC_IMAGE",
        "uri": "assets/img/maya_boots.webp"
      }
    ]
  },
  "interaction_model": {
    "input_mechanic": "ASR_SPEECH_RESPONSE",
    "modality_configurations": {
      "spoken_dictated": {
        "target_semantic_clusters": ["rain", "storm", "wet outside", "raining"],
        "acoustic_confidence_threshold": 0.75
      },
      "tap_select": {
        "options": [
          { "option_id": "opt_1", "display_value": "It is raining outside." },
          { "option_id": "opt_2", "display_value": "She likes yellow boots." },
          { "option_id": "opt_3", "display_value": "It is very sunny." }
        ]
      }
    }
  },
  "scaffolding_protocol": {
    "level_1_reflection_prompt": {
      "spoken_text": "Think about what umbrellas and rain boots are used for.",
      "pedagogical_target": "STRATEGY_REFLECTION_PIVOT",
      "preserves_productive_struggle": true
    },
    "level_2_representation_shift": {
      "spoken_text": "Look at Maya's window in the picture. What is falling from the sky?",
      "target_representation": "VISUAL",
      "visual_asset_override": "assets/img/maya_window_rain_highlight.webp"
    },
    "level_3_prerequisite_bridge": {
      "spoken_text": "When water falls from the sky, we call it rain.",
      "target_prerequisite_subskill_id": "E-CR-01",
      "interactive_overlay": "LITERAL_TEXT_HIGHLIGHT"
    }
  },
  "rubric": {
    "evaluation_mode": "SEMANTIC_CONCEPT_KEYWORD_MATCH",
    "correct_criteria": {
      "matched_concepts": ["rain", "raining", "wet", "storm"]
    },
    "diagnostic_distractors": [
      {
        "response_pattern": "She likes yellow boots",
        "diagnostic_misconception": "LITERAL_SURFACE_FOCUS",
        "recommended_ws3_branch": "STRATEGY_REFLECTION_PIVOT"
      }
    ]
  },
  "safeguard_metadata": {
    "reading_grade_level": 1.1,
    "has_unvoiced_text": false,
    "cultural_neutrality_verified": true,
    "contains_gamified_dark_patterns": false
  }
}
```

### 5.3 Domain 4: Logical Reasoning

```json
{
  "item_id": "ITEM-L-RC-04-0011",
  "schema_version": "1.3.0",
  "target_subskill_id": "L-RC-04",
  "domain_id": "LOGICAL_REASONING",
  "evidence_archetype": "STRATEGIC_REASONING",
  "cognitive_depth": "REASON",
  "transfer_level": "LEVEL_4_STRUCTURAL",
  "primary_modality": "TAP_SELECT",
  "supported_alternative_modalities": ["SPOKEN_DICTATED"],
  "language_load_class": "PURE_REASONING",
  "representation_type": "ABSTRACT",
  "challenge_type": "INCOMPLETE_INFORMATION",
  "creation_stage": "ANSWERING",
  "estimated_duration_seconds": 100,
  "prompt_structure": {
    "spoken_audio_uri": "assets/audio/logic/l_rc_04_0011_prompt.mp3",
    "display_text": "Not red. No straight sides. Pick it.",
    "visual_assets": [
      {
        "asset_id": "shape_matrix_set",
        "asset_type": "DYNAMIC_SVG",
        "uri": "assets/svg/shape_grid_4.svg"
      }
    ]
  },
  "interaction_model": {
    "input_mechanic": "SINGLE_CHOICE",
    "modality_configurations": {
      "tap_select": {
        "options": [
          { "option_id": "opt_red_sq", "display_value": "RED_SQUARE" },
          { "option_id": "opt_blue_sq", "display_value": "BLUE_SQUARE" },
          { "option_id": "opt_red_circ", "display_value": "RED_CIRCLE" },
          { "option_id": "opt_blue_circ", "display_value": "BLUE_CIRCLE" }
        ]
      },
      "spoken_dictated": {
        "target_tokens": ["blue circle"],
        "acoustic_confidence_threshold": 0.75
      }
    }
  },
  "scaffolding_protocol": {
    "level_1_reflection_prompt": {
      "spoken_text": "Check rule 1: It cannot be red. Which shapes can you cross off?",
      "pedagogical_target": "STRATEGY_REFLECTION_PIVOT",
      "preserves_productive_struggle": true
    },
    "level_2_representation_shift": {
      "spoken_text": "Let's cross out every shape with straight corners and edges.",
      "target_representation": "VISUAL",
      "visual_asset_override": "assets/svg/shape_grid_straight_edges_dimmed.svg"
    },
    "level_3_prerequisite_bridge": {
      "spoken_text": "Circles are round and have no straight sides.",
      "target_prerequisite_subskill_id": "M-GS-01",
      "interactive_overlay": "SHAPE_PROPERTY_COMPARATOR"
    }
  },
  "rubric": {
    "evaluation_mode": "DETERMINISTIC_EXACT_MATCH",
    "correct_criteria": { "selected_option_id": "opt_blue_circ" },
    "diagnostic_distractors": [
      {
        "response_pattern": "opt_red_circ",
        "diagnostic_misconception": "IGNORED_NEGATIVE_COLOR_CONSTRAINT",
        "recommended_ws3_branch": "LOAD_REDUCTION"
      },
      {
        "response_pattern": "opt_blue_sq",
        "diagnostic_misconception": "IGNORED_SHAPE_SIDE_CONSTRAINT",
        "recommended_ws3_branch": "LOAD_REDUCTION"
      }
    ]
  },
  "safeguard_metadata": {
    "reading_grade_level": 0.9,
    "has_unvoiced_text": false,
    "cultural_neutrality_verified": true,
    "contains_gamified_dark_patterns": false
  }
}
```

### 5.4 Domain 2 (Reading Fluency Strand): Decoding — Demonstrates `has_unvoiced_text = true` (NEW in 1.1)

This exemplar is new in V1.1. It demonstrates the corrected schema authoring a valid item for `E-PD-03` (Decoding), a subskill that V1.0's universal `has_unvoiced_text: const false` made impossible to represent: narrating the target word aloud would hand the child the answer and invalidate the decoding construct WS2 §3.1 assigns this subskill to measure (`PROCEDURAL_FLUENCY`).

```json
{
  "item_id": "ITEM-E-PD-03-0027",
  "schema_version": "1.3.0",
  "target_subskill_id": "E-PD-03",
  "domain_id": "ENGLISH_LANGUAGE",
  "evidence_archetype": "PROCEDURAL_FLUENCY",
  "cognitive_depth": "APPLY",
  "transfer_level": "LEVEL_1_SURFACE",
  "primary_modality": "SPOKEN_DICTATED",
  "supported_alternative_modalities": ["TAP_SELECT"],
  "language_load_class": "INTEGRATED_LANGUAGE_AND_REASONING",
  "representation_type": "SYMBOLIC",
  "challenge_type": "STANDARD",
  "creation_stage": "ANSWERING",
  "estimated_duration_seconds": 45,
  "prompt_structure": {
    "spoken_audio_uri": "",
    "display_text": "Read this word out loud: shrimp",
    "visual_assets": []
  },
  "interaction_model": {
    "input_mechanic": "ASR_SPEECH_RESPONSE",
    "modality_configurations": {
      "spoken_dictated": {
        "target_tokens": ["shrimp"],
        "acoustic_confidence_threshold": 0.75
      },
      "tap_select": {
        "options": [
          { "option_id": "opt_1", "display_value": "shrimp" },
          { "option_id": "opt_2", "display_value": "shrimps" },
          { "option_id": "opt_3", "display_value": "ship" }
        ]
      }
    }
  },
  "scaffolding_protocol": {
    "level_1_reflection_prompt": {
      "spoken_text": "What sound does 'shr' make at the start of the word?",
      "pedagogical_target": "STRATEGY_REFLECTION_PIVOT",
      "preserves_productive_struggle": true
    },
    "level_2_representation_shift": {
      "spoken_text": "Let's break the word into chunks: shr - i - mp.",
      "target_representation": "VISUAL",
      "visual_asset_override": "assets/svg/word_chunk_shrimp.svg"
    },
    "level_3_prerequisite_bridge": {
      "spoken_text": "Let's sound out each letter one at a time: sh, r, i, m, p.",
      "target_prerequisite_subskill_id": "E-PD-02",
      "interactive_overlay": "GRAPHEME_PHONEME_TILES"
    }
  },
  "rubric": {
    "evaluation_mode": "DETERMINISTIC_EXACT_MATCH",
    "correct_criteria": { "target_word": "shrimp" },
    "diagnostic_distractors": [
      {
        "response_pattern": "ship",
        "diagnostic_misconception": "CONSONANT_BLEND_TRUNCATION",
        "recommended_ws3_branch": "STRATEGY_REFLECTION_PIVOT"
      }
    ]
  },
  "safeguard_metadata": {
    "reading_grade_level": 1.4,
    "has_unvoiced_text": true,
    "cultural_neutrality_verified": true,
    "contains_gamified_dark_patterns": false
  }
}
```

Note the deliberately empty `spoken_audio_uri`: the surrounding instruction could be narrated without harm, but this exemplar leaves the whole prompt unvoiced to make the fix maximally unambiguous. `reading_grade_level: 1.4` would have been schema-illegal under V1.0's universal 1.5 ceiling headroom concerns and *always* illegal under V1.0's `has_unvoiced_text: const false`; under V1.1's `INTEGRATED_LANGUAGE_AND_REASONING` branch (ceiling 6.0, `has_unvoiced_text` unconstrained) it validates correctly.

---

## 6. Stage 1 Automated Schema Compliance Validator

Below is the automated validation logic enforcing structural, cross-field, and pedagogical constraints prior to question ingestion into Workstream 5. **(1.1: regex fix, two new rules, one rule tightened — see inline `# 1.1` comments. 1.2: whitespace-guard fix, two new rules — see inline `# 1.2` comments.)**

```python
import json
import re
from typing import Dict, Any, List

# 1.1 FIX (Rule 3.6 support): the canonical subskill -> evidence_archetype mapping is
# owned by Assessment Framework V0.4 §3.1. WS4 does NOT maintain its own hardcoded copy
# of the full 187-entry table -- duplicating it here would recreate exactly the kind of
# drifting-duplicate-table bug WS2 itself had to correct between its 0.3 and 0.4 drafts
# (12 skill IDs were silently missing from a hand-maintained copy). In production this is
# imported from the shared upstream data source WS2 publishes; the dict below is an
# illustrative excerpt covering only the subskills used in this document's exemplars.
from assessment_framework_v0_5 import SUBSKILL_ARCHETYPE_MAP  # shared source of truth (WS2 §3.1)

# Illustrative excerpt only (NOT the authoritative table -- see import above):
# SUBSKILL_ARCHETYPE_MAP = {
#     "M-OP-05": "CONCEPTUAL",
#     "E-CR-02": "STRATEGIC_REASONING",
#     "L-RC-04": "STRATEGIC_REASONING",
#     "E-PD-03": "PROCEDURAL_FLUENCY",
#     ...  # full 187-entry table lives with WS2, not duplicated here
# }


class Stage1ComplianceValidator:
    ALLOWED_DOMAINS = {
        "MATHEMATICS", "ENGLISH_LANGUAGE", "SCIENCE_EVS",
        "LOGICAL_REASONING", "WORLD_KNOWLEDGE"
    }

    ALLOWED_ARCHETYPES = {
        "CONCEPTUAL", "PROCEDURAL_FLUENCY", "KNOWLEDGE_ACQUISITION",
        "STRATEGIC_REASONING", "CREATIVE_GENERATIVE"
    }

    ALLOWED_DEPTHS = {"UNDERSTAND", "APPLY", "REASON", "GENERALIZE", "CREATE"}

    ALLOWED_TRANSFER_LEVELS = {
        "LEVEL_1_SURFACE", "LEVEL_2_CONTEXTUAL", "LEVEL_3_REPRESENTATIONAL",
        "LEVEL_4_STRUCTURAL", "LEVEL_5_NOVEL"
    }

    # 1.1 FIX: character class was [M|E|S|L|W], which (harmlessly, but incorrectly)
    # also matched a literal '|'. Corrected to [MESLW].
    ID_PATTERN = re.compile(r"^ITEM-[MESLW]-[A-Z]{2}-[0-9]{2}-[0-9]{4}$")
    SUBSKILL_PATTERN = re.compile(r"^[MESLW]-[A-Z]{2}-[0-9]{2}$")

    # 1.1 NEW: low-motor-load modalities WS2 §2.1 actually routes HANDWRITTEN_STYLUS
    # graphomotor-fatigue failures to ("routes automatically to oral/visual verification").
    LOW_MOTOR_LOAD_MODALITIES = {"TAP_SELECT", "SPOKEN_DICTATED"}

    # 1.2 NEW (Rule 3.8): expected interaction_model.modality_configurations key for
    # each enum value of primary_modality / supported_alternative_modalities.
    MODALITY_TO_CONFIG_KEY = {
        "TAP_SELECT": "tap_select",
        "DRAW_DIAGRAM": "draw_diagram",
        "SPOKEN_DICTATED": "spoken_dictated",
        "TYPED_KEYBOARD": "typed_keyboard",
        "HANDWRITTEN_STYLUS": "handwritten_stylus",
    }

    # 1.2 NEW (Rule 3.9): required correct_criteria key(s) per evaluation_mode. A tuple
    # value means "at least one of these"; a single string means "this exact key".
    EVALUATION_MODE_REQUIRED_KEYS = {
        "DETERMINISTIC_EXACT_MATCH": ("selected_option_id", "target_word", "target_value"),
        "SEMANTIC_CONCEPT_KEYWORD_MATCH": ("matched_concepts", "target_semantic_clusters"),
        "TOPOLOGICAL_RELATIONAL_MATCH": ("topology_graph",),
        "CONSTRAINT_SATISFACTION_CHECK": ("constraint_set",),
    }

    def validate_item(self, item: Dict[str, Any]) -> List[str]:
        errors = []

        # 1. Structural Identifiers
        item_id = item.get("item_id", "")
        if not self.ID_PATTERN.match(item_id):
            errors.append(f"Invalid item_id pattern: '{item_id}'")

        target_subskill = item.get("target_subskill_id", "")
        if not self.SUBSKILL_PATTERN.match(target_subskill):
            errors.append(f"Invalid target_subskill_id pattern: '{target_subskill}'")

        # 1.1 NEW -- Rule 3.7: item_id must embed target_subskill_id. Nothing previously
        # checked these two fields agreed with each other; they could silently diverge
        # (e.g., item_id says M-OP-05 but target_subskill_id says E-CR-02).
        if target_subskill and item_id and not item_id.startswith(f"ITEM-{target_subskill}-"):
            errors.append(
                f"item_id '{item_id}' does not embed target_subskill_id '{target_subskill}'."
            )

        # 2. Taxonomy Fields
        if item.get("domain_id") not in self.ALLOWED_DOMAINS:
            errors.append(f"Invalid domain_id: {item.get('domain_id')}")

        archetype = item.get("evidence_archetype")
        if archetype not in self.ALLOWED_ARCHETYPES:
            errors.append(f"Invalid evidence_archetype: {archetype}")

        depth = item.get("cognitive_depth")
        if depth not in self.ALLOWED_DEPTHS:
            errors.append(f"Invalid cognitive_depth: {depth}")

        transfer = item.get("transfer_level")
        if transfer not in self.ALLOWED_TRANSFER_LEVELS:
            errors.append(f"Invalid transfer_level: {transfer}")

        # 3. Cross-Field Pedagogical Integrity Rules
        # Rule 3.1: CREATE depth cannot be Transfer Level 1 Surface Recall
        if depth == "CREATE" and transfer == "LEVEL_1_SURFACE":
            errors.append("Depth 'CREATE' cannot carry Transfer Level 'LEVEL_1_SURFACE'.")

        # Rule 3.2: PURE_REASONING must enforce construct-irrelevant language limits
        language_load = item.get("language_load_class")
        prompt = item.get("prompt_structure", {})
        if language_load == "PURE_REASONING":
            prompt_text = prompt.get("display_text", "")
            if len(prompt_text.split()) > 8:
                errors.append(
                    f"PURE_REASONING item exceeds 8-word prompt text limit: ({len(prompt_text.split())} words)"
                )
            # 1.2 FIX: the old `if not prompt.get("spoken_audio_uri"):` check caught an
            # empty string but not a whitespace-only string (e.g. " "), which is truthy
            # in Python and would have silently passed. .strip() closes that gap. Note
            # the companion schema-level `minLength: 1` (Section 2) cannot catch a
            # whitespace-only string on its own -- JSON Schema does not trim -- so this
            # Python check is the actual enforcement point, not just a backstop.
            if not prompt.get("spoken_audio_uri", "").strip():
                errors.append("PURE_REASONING item must provide a non-empty spoken_audio_uri.")
            # 1.1 NEW: enforce the has_unvoiced_text / reading_grade_level ceilings that
            # moved into the schema's `allOf` block are also checked here for validators
            # that only run the Python layer without a full JSON-Schema-draft-2020-12
            # implementation available.
            safeguards = item.get("safeguard_metadata", {})
            if safeguards.get("has_unvoiced_text") is not False:
                errors.append("PURE_REASONING item must have has_unvoiced_text = false.")
            if safeguards.get("reading_grade_level", 0) > 1.0:
                errors.append("PURE_REASONING item must have reading_grade_level <= 1.0.")
        elif language_load == "INTEGRATED_LANGUAGE_AND_REASONING":
            safeguards = item.get("safeguard_metadata", {})
            if safeguards.get("reading_grade_level", 0) > 6.0:
                errors.append(
                    "INTEGRATED_LANGUAGE_AND_REASONING item must have reading_grade_level <= 6.0."
                )

        # Rule 3.3 (1.1 TIGHTENED): schema-level minItems:1 on
        # supported_alternative_modalities already guarantees every item has *some*
        # alternative, so the V1.0 check ("HANDWRITTEN_STYLUS must provide at least one
        # alternative modality") could never fail -- it was dead code. WS2 §2.1 actually
        # requires the alternative to be low-motor-load specifically (graphomotor fatigue
        # routes to oral/visual verification), so that is what is checked now.
        primary_mod = item.get("primary_modality")
        alt_mods = set(item.get("supported_alternative_modalities", []))
        if primary_mod == "HANDWRITTEN_STYLUS" and not (alt_mods & self.LOW_MOTOR_LOAD_MODALITIES):
            errors.append(
                "HANDWRITTEN_STYLUS items must include at least one low-motor-load "
                "alternative modality (TAP_SELECT or SPOKEN_DICTATED) per WS2 §2.1's "
                "graphomotor-fatigue routing behavior."
            )

        # Rule 3.4: Complete Scaffolding Protocol Presence
        scaffolding = item.get("scaffolding_protocol", {})
        for tier in ["level_1_reflection_prompt", "level_2_representation_shift", "level_3_prerequisite_bridge"]:
            if tier not in scaffolding:
                errors.append(f"Missing mandatory scaffolding tier: '{tier}'")

        # Rule 3.5: Safeguard dark pattern prohibition
        safeguards = item.get("safeguard_metadata", {})
        if safeguards.get("contains_gamified_dark_patterns") is not False:
            errors.append("contains_gamified_dark_patterns must strictly be False.")

        # Rule 3.6 (1.1 NEW): declared evidence_archetype must match WS2's canonical
        # mapping for this specific target_subskill_id -- V1.0 only checked archetype
        # was *a* valid enum value, never that it was the *correct* one for the subskill.
        canonical_archetype = SUBSKILL_ARCHETYPE_MAP.get(target_subskill)
        if canonical_archetype is not None and archetype != canonical_archetype:
            errors.append(
                f"evidence_archetype '{archetype}' does not match Assessment Framework "
                f"V0.4 §3.1's canonical archetype '{canonical_archetype}' for "
                f"target_subskill_id '{target_subskill}'."
            )
        elif canonical_archetype is None:
            errors.append(
                f"target_subskill_id '{target_subskill}' not found in the canonical "
                f"WS2 §3.1 archetype map -- cannot verify evidence_archetype correctness."
            )

        # Rule 3.8 (1.2 NEW): every modality declared in primary_modality or
        # supported_alternative_modalities must have a matching configuration object
        # under interaction_model.modality_configurations. V1.1 declared a modality
        # was "supported" without ever checking the runtime configuration for it
        # actually existed, deferring the failure to Workstream 7 at render time.
        interaction = item.get("interaction_model", {})
        modality_configs = interaction.get("modality_configurations", {})
        declared_modalities = set(alt_mods)
        if primary_mod:
            declared_modalities.add(primary_mod)
        for modality in declared_modalities:
            config_key = self.MODALITY_TO_CONFIG_KEY.get(modality)
            if config_key is None:
                errors.append(f"Unknown modality '{modality}' has no configuration key mapping.")
            elif config_key not in modality_configs:
                errors.append(
                    f"Modality '{modality}' is declared but interaction_model."
                    f"modality_configurations.{config_key} is missing."
                )

        # Rule 3.9 (1.2 NEW): correct_criteria must carry the key(s) appropriate to
        # this item's evaluation_mode (Section 3.4). V1.1 left correct_criteria an
        # unconstrained object, so e.g. a SEMANTIC_CONCEPT_KEYWORD_MATCH item could
        # omit matched_concepts entirely and still pass Stage 1.
        rubric = item.get("rubric", {})
        evaluation_mode = rubric.get("evaluation_mode")
        correct_criteria = rubric.get("correct_criteria", {})
        required_keys = self.EVALUATION_MODE_REQUIRED_KEYS.get(evaluation_mode)
        if required_keys is not None and not any(k in correct_criteria for k in required_keys):
            if len(required_keys) == 1:
                errors.append(
                    f"evaluation_mode '{evaluation_mode}' requires correct_criteria to "
                    f"contain '{required_keys[0]}'."
                )
            else:
                errors.append(
                    f"evaluation_mode '{evaluation_mode}' requires correct_criteria to "
                    f"contain at least one of {required_keys}."
                )

        # Rule 3.10 (1.3 NEW): every item must carry TAP_SELECT as either its
        # primary_modality or within supported_alternative_modalities. This is a
        # device-universal-fallback guarantee, distinct from Rule 3.3's motor-load
        # guarantee: Rule 3.3 ensures a HANDWRITTEN_STYLUS item has *some* low-motor-load
        # alternative; Rule 3.10 ensures every item (regardless of primary_modality) has
        # the one alternative -- TAP_SELECT -- that has no microphone/canvas/stylus
        # dependency and is therefore renderable on effectively any touch/pointer-capable
        # runtime, including low-memory legacy devices Workstream 7 must support.
        if primary_mod != "TAP_SELECT" and "TAP_SELECT" not in alt_mods:
            errors.append(
                "Item must include TAP_SELECT as primary_modality or within "
                "supported_alternative_modalities to guarantee a device-universal "
                "fallback delivery path (no ASR/canvas/stylus dependency)."
            )

        return errors
```

---

## 7. WS4 Verification & Governance Audit

| Governance Guardrail                                          | Implementation Verification in WS4 Schema                                                                                                                                                                                                                                                                                 | Master Plan / Implementation Plan Source                                                           |
|:------------------------------------------------------------- |:------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |:-------------------------------------------------------------------------------------------------- |
| **Complete Decoupling from Engine**                           | Schema specifications are JSON files validatable in CI/CD without adaptive engine dependencies.                                                                                                                                                                                                                           | Implementation Plan §0, §5                                                                         |
| **Independence of Axes**                                      | `cognitive_depth` and `transfer_level` are distinct metadata fields; depth is not bundled into subskill IDs.                                                                                                                                                                                                              | Master Plan §4.1, §8, §25.5                                                                        |
| **Language Confound Isolation**                               | `language_load_class` isolates pure logical reasoning from reading comprehension bottlenecks.                                                                                                                                                                                                                             | Master Plan §16, §25.1                                                                             |
| **Reading/Decoding Strand Representable** *(1.1 NEW)*         | `has_unvoiced_text` and `reading_grade_level` ceilings are conditional on `language_load_class` (schema `allOf` block, Section 2), so `E-PD`/`E-RF` decoding and fluency items — where unvoiced text is the construct — are schema-valid. V1.0's universal narration mandate made this impossible.                        | Master Plan §11.2, §16; Curriculum Map §7.2, §7.5                                                  |
| **Content Acceleration Not Blocked by Schema** *(1.1 NEW)*    | `reading_grade_level` ceiling for `INTEGRATED_LANGUAGE_AND_REASONING` items raised from a universal 1.5 to a domain-appropriate 6.0, with real certification deferred to Question Bank Stage 4 human review rather than an arbitrary schema number.                                                                       | Master Plan §3.1, §14; Curriculum Map Enrichment/Advanced tier                                     |
| **Modality Attribution Support**                              | Multiple input modality configurations allow execution evaluation without penalizing motor barriers.                                                                                                                                                                                                                      | Master Plan §3.10, §25.12                                                                          |
| **Productive Struggle Protection**                            | `level_1_reflection_prompt` enforces `preserves_productive_struggle = true` with zero direct answer reveals.                                                                                                                                                                                                              | Master Plan §3.3, §20, §25.7                                                                       |
| **Archetype Correctness, Not Just Validity** *(1.1 NEW)*      | Stage 1 Rule 3.6 cross-checks `evidence_archetype` against WS2's canonical per-subskill mapping, loaded from the shared upstream source rather than re-hardcoded.                                                                                                                                                         | Implementation Plan §6.2 (Stage 1: "tags internally consistent"); WS2 §3.1                         |
| **Item Self-Consistency** *(1.1 NEW)*                         | Stage 1 Rule 3.7 verifies `item_id` embeds `target_subskill_id`.                                                                                                                                                                                                                                                          | Implementation Plan §6.2 (Stage 1)                                                                 |
| **Non-Empty Audio Narration** *(1.2 NEW)*                     | `PURE_REASONING` items require a non-empty, non-whitespace `spoken_audio_uri`, enforced in Python (Rule 3.2) since JSON Schema's `minLength` cannot detect whitespace-only strings on its own.                                                                                                                            | Master Plan §16; Section 3.3                                                                       |
| **Modality Configuration Completeness** *(1.2 NEW)*           | Stage 1 Rule 3.8 verifies every declared modality has a matching `interaction_model.modality_configurations` entry, preventing declared-but-unconfigured modalities from reaching Workstream 7 at runtime.                                                                                                                | Implementation Plan §6.2 (Stage 1)                                                                 |
| **Rubric Shape Matches Evaluation Mode** *(1.2 NEW)*          | Stage 1 Rule 3.9 and the Section 2 `allOf` conditionals require `correct_criteria` to carry the key(s) appropriate to its `evaluation_mode` (Section 3.4), including newly defined `topology_graph` / `constraint_set` shapes for modes that had no prior exemplar.                                                       | Implementation Plan §6.2 (Stage 1)                                                                 |
| **Device-Universal Fallback Modality Guaranteed** *(1.3 NEW)* | Section 2 `anyOf` block and Stage 1 Rule 3.10 require every item to carry `TAP_SELECT` as `primary_modality` or within `supported_alternative_modalities`, independent of and in addition to Rule 3.3's motor-load guarantee. Verified against all four Section 5 exemplars (Section 3.5) with zero modifications needed. | Implementation Plan §5 (content authored independently of runtime); WS7 device-target requirements |
| **Joint Schema Change Governance**                            | Schema modifications require joint sign-off from WS2 and WS5 leads, with WS4 acting as schema steward.                                                                                                                                                                                                                    | Implementation Plan §9                                                                             |

---

## 8. Downstream Interface Handoff

### 8.1 Contract Naming Reconciliation with Workstream 2 *(1.1 NEW)*

Assessment Framework V0.4 §6 describes the metadata Workstream 4 owns as:

```
Workstream 4: Question Spec Layer
  - Owns static item metadata:
    • intended_transfer_level (1–5)
    • intended_modality
```

WS4's schema (Section 2) implements this using different literal field names. The mapping is:

| WS2 §6 Descriptive Name   | WS4 Actual Schema Field(s)                                                                                                 |
|:------------------------- |:-------------------------------------------------------------------------------------------------------------------------- |
| `intended_transfer_level` | `transfer_level`                                                                                                           |
| `intended_modality`       | `primary_modality` (the authored/default modality) plus `supported_alternative_modalities` (the full set WS3 may route to) |

Both documents describe the same underlying data; `intended_transfer_level` / `intended_modality` were WS2's descriptive labels for the concept, not a separate field WS4 must additionally emit. No data is missing — but the two documents previously left a reader to infer this correspondence rather than stating it, which is the same class of unreconciled cross-document naming gap WS2 §6.2 and §7.2 each had to explicitly correct in its own 0.3→0.4 revision. Any future WS2 or WS4 revision that changes one side of this mapping must update this table.

### 8.2 WS3 → WS4 Item Retrieval Field Mapping *(1.1 NEW)*

WS3 V1.1 §7 emits a `TaskRequestPayload` to request an item; V1.0 of this document labeled the corresponding architecture-diagram arrow "Item Retrieval Contract" (Section 1) without ever defining it. The mapping from WS3's request fields to the WS4 item-schema fields a retrieval query filters on is:

| WS3 `TaskRequestPayload` Field | WS4 Item Schema Field(s) Queried                                                                                                                       | Notes                                                                                                                                                                                                                                                                                                       |
|:------------------------------ |:------------------------------------------------------------------------------------------------------------------------------------------------------ |:----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `target_subskill_id`           | `target_subskill_id`                                                                                                                                   | Direct match.                                                                                                                                                                                                                                                                                               |
| `domain_id`                    | `domain_id`                                                                                                                                            | Direct match.                                                                                                                                                                                                                                                                                               |
| `required_cognitive_depth`     | `cognitive_depth`                                                                                                                                      | Direct match.                                                                                                                                                                                                                                                                                               |
| `target_transfer_level`        | `transfer_level`                                                                                                                                       | Direct match (see §8.1 naming note).                                                                                                                                                                                                                                                                        |
| `intended_representation`      | `representation_type`                                                                                                                                  | Direct match.                                                                                                                                                                                                                                                                                               |
| `permitted_modalities`         | `primary_modality` ∈ list, OR `primary_modality` ∈ `restricted_modalities`-excluded set with a matching entry in `supported_alternative_modalities`    | An item qualifies if its primary modality is permitted, or if a permitted modality is available among its supported alternatives.                                                                                                                                                                           |
| `restricted_modalities`        | `primary_modality` ∉ list AND `supported_alternative_modalities` ∖ list ≠ ∅                                                                            | An item is excluded only if *no* permitted delivery path remains once restricted modalities are removed.                                                                                                                                                                                                    |
| `language_load_class`          | `language_load_class`                                                                                                                                  | Direct match.                                                                                                                                                                                                                                                                                               |
| `creation_stage`               | `creation_stage`                                                                                                                                       | Direct match.                                                                                                                                                                                                                                                                                               |
| `support_branch`               | `rubric.diagnostic_distractors[].recommended_ws3_branch` (for post-response diagnosis) and `scaffolding_protocol` tier selection (for in-task support) | `support_branch = "LOAD_REDUCTION"` is satisfied via modality/language_load_class substitution (Section 4), not a scaffolding tier lookup.                                                                                                                                                                  |
| `phase_context`                | *(not a WS4 item field)*                                                                                                                               | Phase is Curriculum Map metadata about the subskill (WS1), not the item; WS3 resolves phase from the Curriculum Map directly and uses it only to select `target_subskill_id`, which WS4 then queries on.                                                                                                    |
| `task_function_type`           | *(not a WS4 item field)*                                                                                                                               | This is a WS3-internal session-composition label (WS3 §4.1: Retrieval / Focused Core / Consolidation / Strategic Reasoning / Creative-Transfer), not an item property — it determines *which* `target_subskill_id` and `evidence_archetype` combination WS3 requests, but is not itself stored on the item. |

**Device-capability filtering note (1.3 NEW):** `permitted_modalities` / `restricted_modalities` in `TaskRequestPayload` reflect only pedagogical constraints (WS3 §3.1 Branch 4, WS2 §2 modality profile) and carry no device/runtime information — WS3 has no device-capability input in its architecture (WS3 §1). Filtering a retrieved item's modality set down to what is actually renderable on the requesting device is a Workstream 7 concern, performed after WS4 returns the item, using the `primary_modality` / `supported_alternative_modalities` set the item already carries. Section 3.5's `TAP_SELECT` guarantee exists precisely so this later WS7 filtering step always has at least one viable option regardless of device.

---

* **Workstream 5 (Question Bank):** Consumes this JSON schema and automated validator to begin authoring repository items, setting up human review rubrics, and executing field validation pipelines.
* **Workstream 7 (Product / UX):** Consumes `interaction_model` mechanics, dynamic SVG bindings, and audio playback contracts to build native rendering components for the child-facing application.
