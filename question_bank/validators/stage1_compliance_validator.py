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
