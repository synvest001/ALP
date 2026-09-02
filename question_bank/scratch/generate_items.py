import json
from pathlib import Path

base_dir = Path("c:/Users/Asus/ALP/question_bank/items/MATHEMATICS/M-OP-05")
base_dir.mkdir(parents=True, exist_ok=True)

items_data = [
    {
        "item_id": "ITEM-M-OP-05-0002",
        "schema_version": "1.3.0",
        "target_subskill_id": "M-OP-05",
        "domain_id": "MATHEMATICS",
        "evidence_archetype": "CONCEPTUAL",
        "cognitive_depth": "UNDERSTAND",
        "transfer_level": "LEVEL_1_SURFACE",
        "primary_modality": "TAP_SELECT",
        "supported_alternative_modalities": ["SPOKEN_DICTATED"],
        "language_load_class": "PURE_REASONING",
        "representation_type": "VISUAL",
        "challenge_type": "STANDARD",
        "creation_stage": "ANSWERING",
        "estimated_duration_seconds": 60,
        "prompt_structure": {
            "spoken_audio_uri": "assets/audio/math/m_op_05_0002_prompt.mp3",
            "display_text": "How many dots fill the ten frame?",
            "visual_assets": [
                {
                    "asset_id": "ten_frame_6_4",
                    "asset_type": "DYNAMIC_SVG",
                    "uri": "assets/svg/ten_frame_6_4.svg",
                    "state_bindings": {"filled_dots": 6, "target_total": 10, "empty_spots": 4}
                }
            ]
        },
        "interaction_model": {
            "input_mechanic": "SINGLE_CHOICE",
            "modality_configurations": {
                "tap_select": {
                    "options": [
                        {"option_id": "opt_1", "display_value": "4", "asset_uri": "assets/svg/dots_4.svg"},
                        {"option_id": "opt_2", "display_value": "6", "asset_uri": "assets/svg/dots_6.svg"},
                        {"option_id": "opt_3", "display_value": "10", "asset_uri": "assets/svg/dots_10.svg"}
                    ]
                },
                "spoken_dictated": {
                    "target_tokens": ["four", "4"],
                    "acoustic_confidence_threshold": 0.75
                }
            }
        },
        "scaffolding_protocol": {
            "level_1_reflection_prompt": {
                "spoken_text": "Count the empty squares in the ten frame.",
                "pedagogical_target": "STRATEGY_REFLECTION_PIVOT",
                "preserves_productive_struggle": True
            },
            "level_2_representation_shift": {
                "spoken_text": "You have 6 dots. A full frame holds 10.",
                "target_representation": "CONCRETE",
                "visual_asset_override": "assets/svg/ten_frame_counters_6_4.svg"
            },
            "level_3_prerequisite_bridge": {
                "spoken_text": "Count up from 6 to 10: 7, 8, 9, 10.",
                "target_prerequisite_subskill_id": "M-NQ-02",
                "interactive_overlay": "INTERACTIVE_TEN_FRAME_COUNTER"
            }
        },
        "rubric": {
            "evaluation_mode": "DETERMINISTIC_EXACT_MATCH",
            "correct_criteria": {"selected_option_id": "opt_1"},
            "diagnostic_distractors": [
                {
                    "response_pattern": "opt_2",
                    "diagnostic_misconception": "IDENTITY_COPYING",
                    "recommended_ws3_branch": "STRATEGY_REFLECTION_PIVOT"
                },
                {
                    "response_pattern": "opt_3",
                    "diagnostic_misconception": "EQUALITY_AS_SUM_TOTAL",
                    "recommended_ws3_branch": "STRATEGY_REFLECTION_PIVOT"
                }
            ]
        },
        "safeguard_metadata": {
            "reading_grade_level": 0.7,
            "has_unvoiced_text": False,
            "cultural_neutrality_verified": True,
            "contains_gamified_dark_patterns": False
        }
    },
    {
        "item_id": "ITEM-M-OP-05-0003",
        "schema_version": "1.3.0",
        "target_subskill_id": "M-OP-05",
        "domain_id": "MATHEMATICS",
        "evidence_archetype": "CONCEPTUAL",
        "cognitive_depth": "UNDERSTAND",
        "transfer_level": "LEVEL_1_SURFACE",
        "primary_modality": "TYPED_KEYBOARD",
        "supported_alternative_modalities": ["TAP_SELECT"],
        "language_load_class": "PURE_REASONING",
        "representation_type": "SYMBOLIC",
        "challenge_type": "STANDARD",
        "creation_stage": "ANSWERING",
        "estimated_duration_seconds": 45,
        "prompt_structure": {
            "spoken_audio_uri": "assets/audio/math/m_op_05_0003_prompt.mp3",
            "display_text": "Fill in the missing number.",
            "visual_assets": [
                {
                    "asset_id": "equation_5_plus_unknown_8",
                    "asset_type": "STATIC_SVG",
                    "uri": "assets/svg/eq_5_plus_box_8.svg"
                }
            ]
        },
        "interaction_model": {
            "input_mechanic": "NUMBER_PAD_ENTRY",
            "modality_configurations": {
                "typed_keyboard": {
                    "keypad_type": "NUMERIC_STANDARD",
                    "max_length": 2
                },
                "tap_select": {
                    "options": [
                        {"option_id": "opt_1", "display_value": "3"},
                        {"option_id": "opt_2", "display_value": "5"},
                        {"option_id": "opt_3", "display_value": "8"}
                    ]
                }
            }
        },
        "scaffolding_protocol": {
            "level_1_reflection_prompt": {
                "spoken_text": "What number added to 5 makes 8?",
                "pedagogical_target": "STRATEGY_REFLECTION_PIVOT",
                "preserves_productive_struggle": True
            },
            "level_2_representation_shift": {
                "spoken_text": "Start at 5 and add dots until you reach 8.",
                "target_representation": "VISUAL",
                "visual_asset_override": "assets/svg/dot_path_5_to_8.svg"
            },
            "level_3_prerequisite_bridge": {
                "spoken_text": "Count forward: 6, 7, 8. That is 3 steps.",
                "target_prerequisite_subskill_id": "M-NQ-02",
                "interactive_overlay": "NUMBER_PATH_HIGHLIGHT"
            }
        },
        "rubric": {
            "evaluation_mode": "DETERMINISTIC_EXACT_MATCH",
            "correct_criteria": {"target_value": 3},
            "diagnostic_distractors": [
                {
                    "response_pattern": "8",
                    "diagnostic_misconception": "EQUALITY_AS_SUM_TOTAL",
                    "recommended_ws3_branch": "STRATEGY_REFLECTION_PIVOT"
                },
                {
                    "response_pattern": "13",
                    "diagnostic_misconception": "ADDITIVE_OVERCOUNTING",
                    "recommended_ws3_branch": "PREREQUISITE_STRENGTHENING"
                }
            ]
        },
        "safeguard_metadata": {
            "reading_grade_level": 0.5,
            "has_unvoiced_text": False,
            "cultural_neutrality_verified": True,
            "contains_gamified_dark_patterns": False
        }
    },
    {
        "item_id": "ITEM-M-OP-05-0004",
        "schema_version": "1.3.0",
        "target_subskill_id": "M-OP-05",
        "domain_id": "MATHEMATICS",
        "evidence_archetype": "CONCEPTUAL",
        "cognitive_depth": "UNDERSTAND",
        "transfer_level": "LEVEL_2_CONTEXTUAL",
        "primary_modality": "TAP_SELECT",
        "supported_alternative_modalities": ["SPOKEN_DICTATED"],
        "language_load_class": "PURE_REASONING",
        "representation_type": "CONCRETE",
        "challenge_type": "UNFAMILIAR_CONTEXT",
        "creation_stage": "ANSWERING",
        "estimated_duration_seconds": 60,
        "prompt_structure": {
            "spoken_audio_uri": "assets/audio/math/m_op_05_0004_prompt.mp3",
            "display_text": "Which car set balances the see-saw?",
            "visual_assets": [
                {
                    "asset_id": "car_balance_3_4",
                    "asset_type": "DYNAMIC_SVG",
                    "uri": "assets/svg/toy_cars_3_4.svg",
                    "state_bindings": {"left_cars": 7, "right_cars_known": 3, "target_cars_missing": 4}
                }
            ]
        },
        "interaction_model": {
            "input_mechanic": "SINGLE_CHOICE",
            "modality_configurations": {
                "tap_select": {
                    "options": [
                        {"option_id": "opt_1", "display_value": "4", "asset_uri": "assets/svg/cars_4.svg"},
                        {"option_id": "opt_2", "display_value": "3", "asset_uri": "assets/svg/cars_3.svg"},
                        {"option_id": "opt_3", "display_value": "7", "asset_uri": "assets/svg/cars_7.svg"}
                    ]
                },
                "spoken_dictated": {
                    "target_tokens": ["four", "4"],
                    "acoustic_confidence_threshold": 0.75
                }
            }
        },
        "scaffolding_protocol": {
            "level_1_reflection_prompt": {
                "spoken_text": "How many cars are on the left pan?",
                "pedagogical_target": "STRATEGY_REFLECTION_PIVOT",
                "preserves_productive_struggle": True
            },
            "level_2_representation_shift": {
                "spoken_text": "The left side has 7 cars. The right side has 3 cars.",
                "target_representation": "VISUAL",
                "visual_asset_override": "assets/svg/car_counter_comparison_7_3.svg"
            },
            "level_3_prerequisite_bridge": {
                "spoken_text": "Count from 3 up to 7 to find the missing cars.",
                "target_prerequisite_subskill_id": "M-NQ-02",
                "interactive_overlay": "INTERACTIVE_CAR_COUNTERS"
            }
        },
        "rubric": {
            "evaluation_mode": "DETERMINISTIC_EXACT_MATCH",
            "correct_criteria": {"selected_option_id": "opt_1"},
            "diagnostic_distractors": [
                {
                    "response_pattern": "opt_2",
                    "diagnostic_misconception": "IDENTITY_COPYING",
                    "recommended_ws3_branch": "STRATEGY_REFLECTION_PIVOT"
                },
                {
                    "response_pattern": "opt_3",
                    "diagnostic_misconception": "EQUALITY_AS_SUM_TOTAL",
                    "recommended_ws3_branch": "STRATEGY_REFLECTION_PIVOT"
                }
            ]
        },
        "safeguard_metadata": {
            "reading_grade_level": 0.6,
            "has_unvoiced_text": False,
            "cultural_neutrality_verified": True,
            "contains_gamified_dark_patterns": False
        }
    },
    {
        "item_id": "ITEM-M-OP-05-0005",
        "schema_version": "1.3.0",
        "target_subskill_id": "M-OP-05",
        "domain_id": "MATHEMATICS",
        "evidence_archetype": "CONCEPTUAL",
        "cognitive_depth": "UNDERSTAND",
        "transfer_level": "LEVEL_2_CONTEXTUAL",
        "primary_modality": "TAP_SELECT",
        "supported_alternative_modalities": ["SPOKEN_DICTATED"],
        "language_load_class": "PURE_REASONING",
        "representation_type": "VISUAL",
        "challenge_type": "NEW_REPRESENTATION",
        "creation_stage": "ANSWERING",
        "estimated_duration_seconds": 60,
        "prompt_structure": {
            "spoken_audio_uri": "assets/audio/math/m_op_05_0005_prompt.mp3",
            "display_text": "Find the missing number bond part.",
            "visual_assets": [
                {
                    "asset_id": "number_bond_9_4",
                    "asset_type": "DYNAMIC_SVG",
                    "uri": "assets/svg/number_bond_9_4.svg",
                    "state_bindings": {"whole": 9, "part_known": 4, "part_missing": 5}
                }
            ]
        },
        "interaction_model": {
            "input_mechanic": "SINGLE_CHOICE",
            "modality_configurations": {
                "tap_select": {
                    "options": [
                        {"option_id": "opt_1", "display_value": "5"},
                        {"option_id": "opt_2", "display_value": "4"},
                        {"option_id": "opt_3", "display_value": "9"}
                    ]
                },
                "spoken_dictated": {
                    "target_tokens": ["five", "5"],
                    "acoustic_confidence_threshold": 0.75
                }
            }
        },
        "scaffolding_protocol": {
            "level_1_reflection_prompt": {
                "spoken_text": "What two parts make the whole number 9?",
                "pedagogical_target": "STRATEGY_REFLECTION_PIVOT",
                "preserves_productive_struggle": True
            },
            "level_2_representation_shift": {
                "spoken_text": "One part is 4. Count up to 9.",
                "target_representation": "CONCRETE",
                "visual_asset_override": "assets/svg/number_bond_cubes_9_4.svg"
            },
            "level_3_prerequisite_bridge": {
                "spoken_text": "4 plus 5 makes 9.",
                "target_prerequisite_subskill_id": "M-NQ-02",
                "interactive_overlay": "PART_WHOLE_BEAD_BAR"
            }
        },
        "rubric": {
            "evaluation_mode": "DETERMINISTIC_EXACT_MATCH",
            "correct_criteria": {"selected_option_id": "opt_1"},
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
            "reading_grade_level": 0.6,
            "has_unvoiced_text": False,
            "cultural_neutrality_verified": True,
            "contains_gamified_dark_patterns": False
        }
    },
    {
        "item_id": "ITEM-M-OP-05-0006",
        "schema_version": "1.3.0",
        "target_subskill_id": "M-OP-05",
        "domain_id": "MATHEMATICS",
        "evidence_archetype": "CONCEPTUAL",
        "cognitive_depth": "APPLY",
        "transfer_level": "LEVEL_1_SURFACE",
        "primary_modality": "TYPED_KEYBOARD",
        "supported_alternative_modalities": ["TAP_SELECT"],
        "language_load_class": "PURE_REASONING",
        "representation_type": "SYMBOLIC",
        "challenge_type": "STANDARD",
        "creation_stage": "ANSWERING",
        "estimated_duration_seconds": 45,
        "prompt_structure": {
            "spoken_audio_uri": "assets/audio/math/m_op_05_0006_prompt.mp3",
            "display_text": "Which number makes the sum nine?",
            "visual_assets": [
                {
                    "asset_id": "eq_box_plus_4_9",
                    "asset_type": "STATIC_SVG",
                    "uri": "assets/svg/eq_box_plus_4_9.svg"
                }
            ]
        },
        "interaction_model": {
            "input_mechanic": "NUMBER_PAD_ENTRY",
            "modality_configurations": {
                "typed_keyboard": {
                    "keypad_type": "NUMERIC_STANDARD",
                    "max_length": 2
                },
                "tap_select": {
                    "options": [
                        {"option_id": "opt_1", "display_value": "5"},
                        {"option_id": "opt_2", "display_value": "4"},
                        {"option_id": "opt_3", "display_value": "9"}
                    ]
                }
            }
        },
        "scaffolding_protocol": {
            "level_1_reflection_prompt": {
                "spoken_text": "The box comes first. What plus 4 equals 9?",
                "pedagogical_target": "STRATEGY_REFLECTION_PIVOT",
                "preserves_productive_struggle": True
            },
            "level_2_representation_shift": {
                "spoken_text": "Turn the equation around: 4 plus what equals 9?",
                "target_representation": "VISUAL",
                "visual_asset_override": "assets/svg/commutative_ten_frame_4_5.svg"
            },
            "level_3_prerequisite_bridge": {
                "spoken_text": "Start at 4 and count up to 9.",
                "target_prerequisite_subskill_id": "M-NQ-02",
                "interactive_overlay": "NUMBER_LINE_STEPPER"
            }
        },
        "rubric": {
            "evaluation_mode": "DETERMINISTIC_EXACT_MATCH",
            "correct_criteria": {"target_value": 5},
            "diagnostic_distractors": [
                {
                    "response_pattern": "9",
                    "diagnostic_misconception": "EQUALITY_AS_SUM_TOTAL",
                    "recommended_ws3_branch": "STRATEGY_REFLECTION_PIVOT"
                },
                {
                    "response_pattern": "13",
                    "diagnostic_misconception": "ADDITIVE_OVERCOUNTING",
                    "recommended_ws3_branch": "PREREQUISITE_STRENGTHENING"
                }
            ]
        },
        "safeguard_metadata": {
            "reading_grade_level": 0.5,
            "has_unvoiced_text": False,
            "cultural_neutrality_verified": True,
            "contains_gamified_dark_patterns": False
        }
    },
    {
        "item_id": "ITEM-M-OP-05-0007",
        "schema_version": "1.3.0",
        "target_subskill_id": "M-OP-05",
        "domain_id": "MATHEMATICS",
        "evidence_archetype": "CONCEPTUAL",
        "cognitive_depth": "APPLY",
        "transfer_level": "LEVEL_2_CONTEXTUAL",
        "primary_modality": "TAP_SELECT",
        "supported_alternative_modalities": ["SPOKEN_DICTATED"],
        "language_load_class": "PURE_REASONING",
        "representation_type": "CONCRETE",
        "challenge_type": "UNFAMILIAR_CONTEXT",
        "creation_stage": "ANSWERING",
        "estimated_duration_seconds": 60,
        "prompt_structure": {
            "spoken_audio_uri": "assets/audio/math/m_op_05_0007_prompt.mp3",
            "display_text": "How many monkeys keep the branch level?",
            "visual_assets": [
                {
                    "asset_id": "monkey_branch_5_2",
                    "asset_type": "DYNAMIC_SVG",
                    "uri": "assets/svg/monkeys_branch_5_2.svg",
                    "state_bindings": {"left_monkeys": 5, "right_monkeys_known": 2, "target_monkeys_missing": 3}
                }
            ]
        },
        "interaction_model": {
            "input_mechanic": "SINGLE_CHOICE",
            "modality_configurations": {
                "tap_select": {
                    "options": [
                        {"option_id": "opt_1", "display_value": "3", "asset_uri": "assets/svg/monkeys_3.svg"},
                        {"option_id": "opt_2", "display_value": "2", "asset_uri": "assets/svg/monkeys_2.svg"},
                        {"option_id": "opt_3", "display_value": "5", "asset_uri": "assets/svg/monkeys_5.svg"}
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
                "spoken_text": "How many monkeys are on the left side of the branch?",
                "pedagogical_target": "STRATEGY_REFLECTION_PIVOT",
                "preserves_productive_struggle": True
            },
            "level_2_representation_shift": {
                "spoken_text": "5 monkeys on the left equal 2 plus how many on the right?",
                "target_representation": "VISUAL",
                "visual_asset_override": "assets/svg/monkey_counter_grid_5_2.svg"
            },
            "level_3_prerequisite_bridge": {
                "spoken_text": "2 plus 3 equals 5.",
                "target_prerequisite_subskill_id": "M-NQ-02",
                "interactive_overlay": "MONKEY_BEAD_BAR"
            }
        },
        "rubric": {
            "evaluation_mode": "DETERMINISTIC_EXACT_MATCH",
            "correct_criteria": {"selected_option_id": "opt_1"},
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
            "reading_grade_level": 0.7,
            "has_unvoiced_text": False,
            "cultural_neutrality_verified": True,
            "contains_gamified_dark_patterns": False
        }
    },
    {
        "item_id": "ITEM-M-OP-05-0008",
        "schema_version": "1.3.0",
        "target_subskill_id": "M-OP-05",
        "domain_id": "MATHEMATICS",
        "evidence_archetype": "CONCEPTUAL",
        "cognitive_depth": "APPLY",
        "transfer_level": "LEVEL_2_CONTEXTUAL",
        "primary_modality": "TAP_SELECT",
        "supported_alternative_modalities": ["SPOKEN_DICTATED"],
        "language_load_class": "PURE_REASONING",
        "representation_type": "VISUAL",
        "challenge_type": "NEW_REPRESENTATION",
        "creation_stage": "ANSWERING",
        "estimated_duration_seconds": 60,
        "prompt_structure": {
            "spoken_audio_uri": "assets/audio/math/m_op_05_0008_prompt.mp3",
            "display_text": "Which rod completes the total length?",
            "visual_assets": [
                {
                    "asset_id": "bar_model_8_5",
                    "asset_type": "DYNAMIC_SVG",
                    "uri": "assets/svg/bar_model_8_5.svg",
                    "state_bindings": {"total_length": 8, "known_length": 5, "missing_length": 3}
                }
            ]
        },
        "interaction_model": {
            "input_mechanic": "SINGLE_CHOICE",
            "modality_configurations": {
                "tap_select": {
                    "options": [
                        {"option_id": "opt_1", "display_value": "3", "asset_uri": "assets/svg/rod_3.svg"},
                        {"option_id": "opt_2", "display_value": "5", "asset_uri": "assets/svg/rod_5.svg"},
                        {"option_id": "opt_3", "display_value": "8", "asset_uri": "assets/svg/rod_8.svg"}
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
                "spoken_text": "Compare the top rod and the bottom rod.",
                "pedagogical_target": "STRATEGY_REFLECTION_PIVOT",
                "preserves_productive_struggle": True
            },
            "level_2_representation_shift": {
                "spoken_text": "The top length is 8. The bottom rod is 5. How long is the gap?",
                "target_representation": "CONCRETE",
                "visual_asset_override": "assets/svg/cuisenaire_cubes_8_5.svg"
            },
            "level_3_prerequisite_bridge": {
                "spoken_text": "5 plus 3 equals 8.",
                "target_prerequisite_subskill_id": "M-NQ-02",
                "interactive_overlay": "ROD_LENGTH_RULER"
            }
        },
        "rubric": {
            "evaluation_mode": "DETERMINISTIC_EXACT_MATCH",
            "correct_criteria": {"selected_option_id": "opt_1"},
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
            "reading_grade_level": 0.6,
            "has_unvoiced_text": False,
            "cultural_neutrality_verified": True,
            "contains_gamified_dark_patterns": False
        }
    },
    {
        "item_id": "ITEM-M-OP-05-0009",
        "schema_version": "1.3.0",
        "target_subskill_id": "M-OP-05",
        "domain_id": "MATHEMATICS",
        "evidence_archetype": "CONCEPTUAL",
        "cognitive_depth": "APPLY",
        "transfer_level": "LEVEL_3_REPRESENTATIONAL",
        "primary_modality": "TAP_SELECT",
        "supported_alternative_modalities": ["SPOKEN_DICTATED"],
        "language_load_class": "PURE_REASONING",
        "representation_type": "SYMBOLIC",
        "challenge_type": "STRATEGY_SELECTION",
        "creation_stage": "ANSWERING",
        "estimated_duration_seconds": 60,
        "prompt_structure": {
            "spoken_audio_uri": "assets/audio/math/m_op_05_0009_prompt.mp3",
            "display_text": "Which number makes both sides equal?",
            "visual_assets": [
                {
                    "asset_id": "eq_3_plus_5_eq_2_plus_box",
                    "asset_type": "STATIC_SVG",
                    "uri": "assets/svg/eq_3_plus_5_eq_2_plus_box.svg"
                }
            ]
        },
        "interaction_model": {
            "input_mechanic": "SINGLE_CHOICE",
            "modality_configurations": {
                "tap_select": {
                    "options": [
                        {"option_id": "opt_1", "display_value": "6"},
                        {"option_id": "opt_2", "display_value": "8"},
                        {"option_id": "opt_3", "display_value": "2"}
                    ]
                },
                "spoken_dictated": {
                    "target_tokens": ["six", "6"],
                    "acoustic_confidence_threshold": 0.75
                }
            }
        },
        "scaffolding_protocol": {
            "level_1_reflection_prompt": {
                "spoken_text": "What is the total of 3 plus 5 on the left?",
                "pedagogical_target": "STRATEGY_REFLECTION_PIVOT",
                "preserves_productive_struggle": True
            },
            "level_2_representation_shift": {
                "spoken_text": "The left side equals 8. So 2 plus what equals 8?",
                "target_representation": "VISUAL",
                "visual_asset_override": "assets/svg/dual_ten_frame_8.svg"
            },
            "level_3_prerequisite_bridge": {
                "spoken_text": "2 plus 6 equals 8.",
                "target_prerequisite_subskill_id": "M-OP-01",
                "interactive_overlay": "EQUATION_BALANCE_SCALE"
            }
        },
        "rubric": {
            "evaluation_mode": "DETERMINISTIC_EXACT_MATCH",
            "correct_criteria": {"selected_option_id": "opt_1"},
            "diagnostic_distractors": [
                {
                    "response_pattern": "opt_2",
                    "diagnostic_misconception": "EQUALITY_AS_SUM_TOTAL",
                    "recommended_ws3_branch": "STRATEGY_REFLECTION_PIVOT"
                },
                {
                    "response_pattern": "opt_3",
                    "diagnostic_misconception": "IDENTITY_COPYING",
                    "recommended_ws3_branch": "STRATEGY_REFLECTION_PIVOT"
                }
            ]
        },
        "safeguard_metadata": {
            "reading_grade_level": 0.6,
            "has_unvoiced_text": False,
            "cultural_neutrality_verified": True,
            "contains_gamified_dark_patterns": False
        }
    },
    {
        "item_id": "ITEM-M-OP-05-0010",
        "schema_version": "1.3.0",
        "target_subskill_id": "M-OP-05",
        "domain_id": "MATHEMATICS",
        "evidence_archetype": "CONCEPTUAL",
        "cognitive_depth": "APPLY",
        "transfer_level": "LEVEL_3_REPRESENTATIONAL",
        "primary_modality": "TAP_SELECT",
        "supported_alternative_modalities": ["SPOKEN_DICTATED"],
        "language_load_class": "PURE_REASONING",
        "representation_type": "VISUAL",
        "challenge_type": "NEW_REPRESENTATION",
        "creation_stage": "ANSWERING",
        "estimated_duration_seconds": 60,
        "prompt_structure": {
            "spoken_audio_uri": "assets/audio/math/m_op_05_0010_prompt.mp3",
            "display_text": "How far is the missing jump?",
            "visual_assets": [
                {
                    "asset_id": "number_line_4_to_10",
                    "asset_type": "DYNAMIC_SVG",
                    "uri": "assets/svg/number_line_4_to_10.svg",
                    "state_bindings": {"start": 4, "target": 10, "missing_jump": 6}
                }
            ]
        },
        "interaction_model": {
            "input_mechanic": "SINGLE_CHOICE",
            "modality_configurations": {
                "tap_select": {
                    "options": [
                        {"option_id": "opt_1", "display_value": "6"},
                        {"option_id": "opt_2", "display_value": "4"},
                        {"option_id": "opt_3", "display_value": "10"}
                    ]
                },
                "spoken_dictated": {
                    "target_tokens": ["six", "6"],
                    "acoustic_confidence_threshold": 0.75
                }
            }
        },
        "scaffolding_protocol": {
            "level_1_reflection_prompt": {
                "spoken_text": "You start at 4 and land on 10. How many steps?",
                "pedagogical_target": "STRATEGY_REFLECTION_PIVOT",
                "preserves_productive_struggle": True
            },
            "level_2_representation_shift": {
                "spoken_text": "Count the spaces between 4 and 10 on the line.",
                "target_representation": "CONCRETE",
                "visual_asset_override": "assets/svg/bead_string_4_to_10.svg"
            },
            "level_3_prerequisite_bridge": {
                "spoken_text": "4 plus 6 equals 10.",
                "target_prerequisite_subskill_id": "M-NQ-02",
                "interactive_overlay": "NUMBER_LINE_HIGHLIGHTER"
            }
        },
        "rubric": {
            "evaluation_mode": "DETERMINISTIC_EXACT_MATCH",
            "correct_criteria": {"selected_option_id": "opt_1"},
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
            "reading_grade_level": 0.6,
            "has_unvoiced_text": False,
            "cultural_neutrality_verified": True,
            "contains_gamified_dark_patterns": False
        }
    },
    {
        "item_id": "ITEM-M-OP-05-0011",
        "schema_version": "1.3.0",
        "target_subskill_id": "M-OP-05",
        "domain_id": "MATHEMATICS",
        "evidence_archetype": "CONCEPTUAL",
        "cognitive_depth": "REASON",
        "transfer_level": "LEVEL_2_CONTEXTUAL",
        "primary_modality": "TAP_SELECT",
        "supported_alternative_modalities": ["SPOKEN_DICTATED"],
        "language_load_class": "PURE_REASONING",
        "representation_type": "CONCRETE",
        "challenge_type": "INCOMPLETE_INFORMATION",
        "creation_stage": "ANSWERING",
        "estimated_duration_seconds": 90,
        "prompt_structure": {
            "spoken_audio_uri": "assets/audio/math/m_op_05_0011_prompt.mp3",
            "display_text": "How many blocks are inside the box?",
            "visual_assets": [
                {
                    "asset_id": "mystery_box_3_7",
                    "asset_type": "DYNAMIC_SVG",
                    "uri": "assets/svg/mystery_box_3_7.svg",
                    "state_bindings": {"right_total": 7, "left_visible": 3, "box_hidden": 4}
                }
            ]
        },
        "interaction_model": {
            "input_mechanic": "SINGLE_CHOICE",
            "modality_configurations": {
                "tap_select": {
                    "options": [
                        {"option_id": "opt_1", "display_value": "4"},
                        {"option_id": "opt_2", "display_value": "3"},
                        {"option_id": "opt_3", "display_value": "7"}
                    ]
                },
                "spoken_dictated": {
                    "target_tokens": ["four", "4"],
                    "acoustic_confidence_threshold": 0.75
                }
            }
        },
        "scaffolding_protocol": {
            "level_1_reflection_prompt": {
                "spoken_text": "The scale is level. 7 blocks are on the right. How many must be on the left?",
                "pedagogical_target": "STRATEGY_REFLECTION_PIVOT",
                "preserves_productive_struggle": True
            },
            "level_2_representation_shift": {
                "spoken_text": "You see 3 blocks on the left. The box has the rest of the 7.",
                "target_representation": "VISUAL",
                "visual_asset_override": "assets/svg/transparent_box_3_4.svg"
            },
            "level_3_prerequisite_bridge": {
                "spoken_text": "3 plus 4 equals 7.",
                "target_prerequisite_subskill_id": "M-NQ-02",
                "interactive_overlay": "BLOCK_REMOVAL_TOOL"
            }
        },
        "rubric": {
            "evaluation_mode": "DETERMINISTIC_EXACT_MATCH",
            "correct_criteria": {"selected_option_id": "opt_1"},
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
            "reading_grade_level": 0.7,
            "has_unvoiced_text": False,
            "cultural_neutrality_verified": True,
            "contains_gamified_dark_patterns": False
        }
    },
    {
        "item_id": "ITEM-M-OP-05-0012",
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
            "spoken_audio_uri": "assets/audio/math/m_op_05_0012_prompt.mp3",
            "display_text": "Which block balances three numbers?",
            "visual_assets": [
                {
                    "asset_id": "three_addend_scale",
                    "asset_type": "DYNAMIC_SVG",
                    "uri": "assets/svg/three_addend_balance_2_3.svg",
                    "state_bindings": {"left_sum": 9, "right_known_1": 2, "right_known_2": 3, "right_missing": 4}
                }
            ]
        },
        "interaction_model": {
            "input_mechanic": "SINGLE_CHOICE",
            "modality_configurations": {
                "tap_select": {
                    "options": [
                        {"option_id": "opt_1", "display_value": "4"},
                        {"option_id": "opt_2", "display_value": "5"},
                        {"option_id": "opt_3", "display_value": "9"}
                    ]
                },
                "spoken_dictated": {
                    "target_tokens": ["four", "4"],
                    "acoustic_confidence_threshold": 0.75
                }
            }
        },
        "scaffolding_protocol": {
            "level_1_reflection_prompt": {
                "spoken_text": "Combine 2 and 3 first. What is their total?",
                "pedagogical_target": "STRATEGY_REFLECTION_PIVOT",
                "preserves_productive_struggle": True
            },
            "level_2_representation_shift": {
                "spoken_text": "2 plus 3 equals 5. Now, 5 plus what equals 9?",
                "target_representation": "SYMBOLIC",
                "visual_asset_override": "assets/svg/eq_5_plus_box_9.svg"
            },
            "level_3_prerequisite_bridge": {
                "spoken_text": "5 plus 4 equals 9.",
                "target_prerequisite_subskill_id": "M-OP-01",
                "interactive_overlay": "GROUPING_CIRCLES"
            }
        },
        "rubric": {
            "evaluation_mode": "DETERMINISTIC_EXACT_MATCH",
            "correct_criteria": {"selected_option_id": "opt_1"},
            "diagnostic_distractors": [
                {
                    "response_pattern": "opt_2",
                    "diagnostic_misconception": "PARTIAL_ADDEND_SUM",
                    "recommended_ws3_branch": "STRATEGY_REFLECTION_PIVOT"
                },
                {
                    "response_pattern": "opt_3",
                    "diagnostic_misconception": "EQUALITY_AS_SUM_TOTAL",
                    "recommended_ws3_branch": "STRATEGY_REFLECTION_PIVOT"
                }
            ]
        },
        "safeguard_metadata": {
            "reading_grade_level": 0.6,
            "has_unvoiced_text": False,
            "cultural_neutrality_verified": True,
            "contains_gamified_dark_patterns": False
        }
    },
    {
        "item_id": "ITEM-M-OP-05-0013",
        "schema_version": "1.3.0",
        "target_subskill_id": "M-OP-05",
        "domain_id": "MATHEMATICS",
        "evidence_archetype": "CONCEPTUAL",
        "cognitive_depth": "REASON",
        "transfer_level": "LEVEL_3_REPRESENTATIONAL",
        "primary_modality": "TAP_SELECT",
        "supported_alternative_modalities": ["SPOKEN_DICTATED"],
        "language_load_class": "PURE_REASONING",
        "representation_type": "SYMBOLIC",
        "challenge_type": "CONFLICTING_EVIDENCE",
        "creation_stage": "EXPLAINING",
        "estimated_duration_seconds": 90,
        "prompt_structure": {
            "spoken_audio_uri": "assets/audio/math/m_op_05_0013_prompt.mp3",
            "display_text": "Which number completes the equal balance?",
            "visual_assets": [
                {
                    "asset_id": "eq_4_plus_2_eq_6_plus_box",
                    "asset_type": "STATIC_SVG",
                    "uri": "assets/svg/eq_4_plus_2_eq_6_plus_box.svg"
                }
            ]
        },
        "interaction_model": {
            "input_mechanic": "SINGLE_CHOICE",
            "modality_configurations": {
                "tap_select": {
                    "options": [
                        {"option_id": "opt_1", "display_value": "0"},
                        {"option_id": "opt_2", "display_value": "6"},
                        {"option_id": "opt_3", "display_value": "2"}
                    ]
                },
                "spoken_dictated": {
                    "target_tokens": ["zero", "0"],
                    "acoustic_confidence_threshold": 0.75
                }
            }
        },
        "scaffolding_protocol": {
            "level_1_reflection_prompt": {
                "spoken_text": "What is 4 plus 2? Is 6 already on the right side?",
                "pedagogical_target": "STRATEGY_REFLECTION_PIVOT",
                "preserves_productive_struggle": True
            },
            "level_2_representation_shift": {
                "spoken_text": "4 plus 2 equals 6. The right side is 6 plus box. What keeps it 6?",
                "target_representation": "VISUAL",
                "visual_asset_override": "assets/svg/balance_6_equals_6.svg"
            },
            "level_3_prerequisite_bridge": {
                "spoken_text": "6 plus 0 equals 6.",
                "target_prerequisite_subskill_id": "M-OP-01",
                "interactive_overlay": "ZERO_PROPERTY_TOOL"
            }
        },
        "rubric": {
            "evaluation_mode": "DETERMINISTIC_EXACT_MATCH",
            "correct_criteria": {"selected_option_id": "opt_1"},
            "diagnostic_distractors": [
                {
                    "response_pattern": "opt_2",
                    "diagnostic_misconception": "EQUALITY_AS_SUM_TOTAL",
                    "recommended_ws3_branch": "STRATEGY_REFLECTION_PIVOT"
                },
                {
                    "response_pattern": "opt_3",
                    "diagnostic_misconception": "IDENTITY_COPYING",
                    "recommended_ws3_branch": "STRATEGY_REFLECTION_PIVOT"
                }
            ]
        },
        "safeguard_metadata": {
            "reading_grade_level": 0.6,
            "has_unvoiced_text": False,
            "cultural_neutrality_verified": True,
            "contains_gamified_dark_patterns": False
        }
    },
    {
        "item_id": "ITEM-M-OP-05-0014",
        "schema_version": "1.3.0",
        "target_subskill_id": "M-OP-05",
        "domain_id": "MATHEMATICS",
        "evidence_archetype": "CONCEPTUAL",
        "cognitive_depth": "REASON",
        "transfer_level": "LEVEL_4_STRUCTURAL",
        "primary_modality": "TAP_SELECT",
        "supported_alternative_modalities": ["SPOKEN_DICTATED"],
        "language_load_class": "PURE_REASONING",
        "representation_type": "CONCRETE",
        "challenge_type": "MULTIPLE_SOLUTIONS",
        "creation_stage": "ANSWERING",
        "estimated_duration_seconds": 90,
        "prompt_structure": {
            "spoken_audio_uri": "assets/audio/math/m_op_05_0014_prompt.mp3",
            "display_text": "Which pair balances five plus three?",
            "visual_assets": [
                {
                    "asset_id": "split_bag_balance",
                    "asset_type": "DYNAMIC_SVG",
                    "uri": "assets/svg/split_bag_balance_8.svg",
                    "state_bindings": {"left_sum": 8, "target_pairs": [[4, 4], [6, 2], [7, 1]]}
                }
            ]
        },
        "interaction_model": {
            "input_mechanic": "SINGLE_CHOICE",
            "modality_configurations": {
                "tap_select": {
                    "options": [
                        {"option_id": "opt_1", "display_value": "4 + 4"},
                        {"option_id": "opt_2", "display_value": "5 + 3"},
                        {"option_id": "opt_3", "display_value": "8 + 1"}
                    ]
                },
                "spoken_dictated": {
                    "target_tokens": ["four plus four", "4+4"],
                    "acoustic_confidence_threshold": 0.75
                }
            }
        },
        "scaffolding_protocol": {
            "level_1_reflection_prompt": {
                "spoken_text": "Find a pair that adds up to 8.",
                "pedagogical_target": "STRATEGY_REFLECTION_PIVOT",
                "preserves_productive_struggle": True
            },
            "level_2_representation_shift": {
                "spoken_text": "5 plus 3 is 8. 4 plus 4 is also 8.",
                "target_representation": "VISUAL",
                "visual_asset_override": "assets/svg/eight_dots_two_ways.svg"
            },
            "level_3_prerequisite_bridge": {
                "spoken_text": "Different pairs can add up to the same number 8.",
                "target_prerequisite_subskill_id": "M-NQ-04",
                "interactive_overlay": "PAIR_DECOMPOSITION_TOOL"
            }
        },
        "rubric": {
            "evaluation_mode": "DETERMINISTIC_EXACT_MATCH",
            "correct_criteria": {"selected_option_id": "opt_1"},
            "diagnostic_distractors": [
                {
                    "response_pattern": "opt_3",
                    "diagnostic_misconception": "ADDITIVE_OVERCOUNTING",
                    "recommended_ws3_branch": "PREREQUISITE_STRENGTHENING"
                },
                {
                    "response_pattern": "opt_2",
                    "diagnostic_misconception": "IDENTITY_COPYING",
                    "recommended_ws3_branch": "STRATEGY_REFLECTION_PIVOT"
                }
            ]
        },
        "safeguard_metadata": {
            "reading_grade_level": 0.6,
            "has_unvoiced_text": False,
            "cultural_neutrality_verified": True,
            "contains_gamified_dark_patterns": False
        }
    },
    {
        "item_id": "ITEM-M-OP-05-0015",
        "schema_version": "1.3.0",
        "target_subskill_id": "M-OP-05",
        "domain_id": "MATHEMATICS",
        "evidence_archetype": "CONCEPTUAL",
        "cognitive_depth": "REASON",
        "transfer_level": "LEVEL_4_STRUCTURAL",
        "primary_modality": "TAP_SELECT",
        "supported_alternative_modalities": ["SPOKEN_DICTATED"],
        "language_load_class": "PURE_REASONING",
        "representation_type": "SYMBOLIC",
        "challenge_type": "STRATEGY_SELECTION",
        "creation_stage": "ANSWERING",
        "estimated_duration_seconds": 90,
        "prompt_structure": {
            "spoken_audio_uri": "assets/audio/math/m_op_05_0015_prompt.mp3",
            "display_text": "Which value keeps the equation balanced?",
            "visual_assets": [
                {
                    "asset_id": "eq_6_plus_4_eq_box_plus_3",
                    "asset_type": "STATIC_SVG",
                    "uri": "assets/svg/eq_6_plus_4_eq_box_plus_3.svg"
                }
            ]
        },
        "interaction_model": {
            "input_mechanic": "SINGLE_CHOICE",
            "modality_configurations": {
                "tap_select": {
                    "options": [
                        {"option_id": "opt_1", "display_value": "7"},
                        {"option_id": "opt_2", "display_value": "10"},
                        {"option_id": "opt_3", "display_value": "3"}
                    ]
                },
                "spoken_dictated": {
                    "target_tokens": ["seven", "7"],
                    "acoustic_confidence_threshold": 0.75
                }
            }
        },
        "scaffolding_protocol": {
            "level_1_reflection_prompt": {
                "spoken_text": "First, add 6 plus 4. What is the total on the left?",
                "pedagogical_target": "STRATEGY_REFLECTION_PIVOT",
                "preserves_productive_struggle": True
            },
            "level_2_representation_shift": {
                "spoken_text": "The left total is 10. So what plus 3 equals 10?",
                "target_representation": "VISUAL",
                "visual_asset_override": "assets/svg/ten_frame_7_plus_3.svg"
            },
            "level_3_prerequisite_bridge": {
                "spoken_text": "7 plus 3 equals 10.",
                "target_prerequisite_subskill_id": "M-OP-01",
                "interactive_overlay": "DUAL_BEAD_STRING"
            }
        },
        "rubric": {
            "evaluation_mode": "DETERMINISTIC_EXACT_MATCH",
            "correct_criteria": {"selected_option_id": "opt_1"},
            "diagnostic_distractors": [
                {
                    "response_pattern": "opt_2",
                    "diagnostic_misconception": "EQUALITY_AS_SUM_TOTAL",
                    "recommended_ws3_branch": "STRATEGY_REFLECTION_PIVOT"
                },
                {
                    "response_pattern": "opt_3",
                    "diagnostic_misconception": "IDENTITY_COPYING",
                    "recommended_ws3_branch": "STRATEGY_REFLECTION_PIVOT"
                }
            ]
        },
        "safeguard_metadata": {
            "reading_grade_level": 0.6,
            "has_unvoiced_text": False,
            "cultural_neutrality_verified": True,
            "contains_gamified_dark_patterns": False
        }
    },
    {
        "item_id": "ITEM-M-OP-05-0016",
        "schema_version": "1.3.0",
        "target_subskill_id": "M-OP-05",
        "domain_id": "MATHEMATICS",
        "evidence_archetype": "CONCEPTUAL",
        "cognitive_depth": "GENERALIZE",
        "transfer_level": "LEVEL_3_REPRESENTATIONAL",
        "primary_modality": "TAP_SELECT",
        "supported_alternative_modalities": ["SPOKEN_DICTATED"],
        "language_load_class": "PURE_REASONING",
        "representation_type": "VISUAL",
        "challenge_type": "NEW_REPRESENTATION",
        "creation_stage": "ANSWERING",
        "estimated_duration_seconds": 90,
        "prompt_structure": {
            "spoken_audio_uri": "assets/audio/math/m_op_05_0016_prompt.mp3",
            "display_text": "What value does the square hide?",
            "visual_assets": [
                {
                    "asset_id": "square_plus_3_eq_7",
                    "asset_type": "DYNAMIC_SVG",
                    "uri": "assets/svg/shape_symbol_square_3_7.svg",
                    "state_bindings": {"symbol": "SQUARE", "known": 3, "total": 7, "hidden_val": 4}
                }
            ]
        },
        "interaction_model": {
            "input_mechanic": "SINGLE_CHOICE",
            "modality_configurations": {
                "tap_select": {
                    "options": [
                        {"option_id": "opt_1", "display_value": "4"},
                        {"option_id": "opt_2", "display_value": "3"},
                        {"option_id": "opt_3", "display_value": "7"}
                    ]
                },
                "spoken_dictated": {
                    "target_tokens": ["four", "4"],
                    "acoustic_confidence_threshold": 0.75
                }
            }
        },
        "scaffolding_protocol": {
            "level_1_reflection_prompt": {
                "spoken_text": "Treat the square like a missing number box. What plus 3 is 7?",
                "pedagogical_target": "STRATEGY_REFLECTION_PIVOT",
                "preserves_productive_struggle": True
            },
            "level_2_representation_shift": {
                "spoken_text": "Square plus 3 equals 7. So Square equals 4.",
                "target_representation": "SYMBOLIC",
                "visual_asset_override": "assets/svg/symbolic_substitution_4.svg"
            },
            "level_3_prerequisite_bridge": {
                "spoken_text": "4 plus 3 equals 7.",
                "target_prerequisite_subskill_id": "M-NQ-02",
                "interactive_overlay": "SHAPE_VALUE_MATCHER"
            }
        },
        "rubric": {
            "evaluation_mode": "DETERMINISTIC_EXACT_MATCH",
            "correct_criteria": {"selected_option_id": "opt_1"},
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
            "reading_grade_level": 0.6,
            "has_unvoiced_text": False,
            "cultural_neutrality_verified": True,
            "contains_gamified_dark_patterns": False
        }
    },
    {
        "item_id": "ITEM-M-OP-05-0017",
        "schema_version": "1.3.0",
        "target_subskill_id": "M-OP-05",
        "domain_id": "MATHEMATICS",
        "evidence_archetype": "CONCEPTUAL",
        "cognitive_depth": "GENERALIZE",
        "transfer_level": "LEVEL_3_REPRESENTATIONAL",
        "primary_modality": "TAP_SELECT",
        "supported_alternative_modalities": ["SPOKEN_DICTATED"],
        "language_load_class": "PURE_REASONING",
        "representation_type": "SYMBOLIC",
        "challenge_type": "STRATEGY_SELECTION",
        "creation_stage": "ANSWERING",
        "estimated_duration_seconds": 90,
        "prompt_structure": {
            "spoken_audio_uri": "assets/audio/math/m_op_05_0017_prompt.mp3",
            "display_text": "Which number keeps both equations true?",
            "visual_assets": [
                {
                    "asset_id": "relational_4_3_7",
                    "asset_type": "STATIC_SVG",
                    "uri": "assets/svg/relational_rule_4_3_7.svg"
                }
            ]
        },
        "interaction_model": {
            "input_mechanic": "SINGLE_CHOICE",
            "modality_configurations": {
                "tap_select": {
                    "options": [
                        {"option_id": "opt_1", "display_value": "1"},
                        {"option_id": "opt_2", "display_value": "7"},
                        {"option_id": "opt_3", "display_value": "8"}
                    ]
                },
                "spoken_dictated": {
                    "target_tokens": ["one", "1"],
                    "acoustic_confidence_threshold": 0.75
                }
            }
        },
        "scaffolding_protocol": {
            "level_1_reflection_prompt": {
                "spoken_text": "Look at both sides. 4 increased by 1 on the left. What happens on the right?",
                "pedagogical_target": "STRATEGY_REFLECTION_PIVOT",
                "preserves_productive_struggle": True
            },
            "level_2_representation_shift": {
                "spoken_text": "4+3=7. If you add 1 to the left (4+4), add 1 to the right (7+1).",
                "target_representation": "VISUAL",
                "visual_asset_override": "assets/svg/relational_balance_plus_1.svg"
            },
            "level_3_prerequisite_bridge": {
                "spoken_text": "Adding 1 to one side means adding 1 to the other.",
                "target_prerequisite_subskill_id": "M-OP-01",
                "interactive_overlay": "BALANCE_COMPENSATOR"
            }
        },
        "rubric": {
            "evaluation_mode": "DETERMINISTIC_EXACT_MATCH",
            "correct_criteria": {"selected_option_id": "opt_1"},
            "diagnostic_distractors": [
                {
                    "response_pattern": "opt_2",
                    "diagnostic_misconception": "IDENTITY_COPYING",
                    "recommended_ws3_branch": "STRATEGY_REFLECTION_PIVOT"
                },
                {
                    "response_pattern": "opt_3",
                    "diagnostic_misconception": "EQUALITY_AS_SUM_TOTAL",
                    "recommended_ws3_branch": "STRATEGY_REFLECTION_PIVOT"
                }
            ]
        },
        "safeguard_metadata": {
            "reading_grade_level": 0.6,
            "has_unvoiced_text": False,
            "cultural_neutrality_verified": True,
            "contains_gamified_dark_patterns": False
        }
    },
    {
        "item_id": "ITEM-M-OP-05-0018",
        "schema_version": "1.3.0",
        "target_subskill_id": "M-OP-05",
        "domain_id": "MATHEMATICS",
        "evidence_archetype": "CONCEPTUAL",
        "cognitive_depth": "GENERALIZE",
        "transfer_level": "LEVEL_4_STRUCTURAL",
        "primary_modality": "TAP_SELECT",
        "supported_alternative_modalities": ["SPOKEN_DICTATED"],
        "language_load_class": "PURE_REASONING",
        "representation_type": "CONCRETE",
        "challenge_type": "INCOMPLETE_INFORMATION",
        "creation_stage": "ANSWERING",
        "estimated_duration_seconds": 120,
        "prompt_structure": {
            "spoken_audio_uri": "assets/audio/math/m_op_05_0018_prompt.mp3",
            "display_text": "Which weight balances all three scales?",
            "visual_assets": [
                {
                    "asset_id": "multi_pan_scale",
                    "asset_type": "DYNAMIC_SVG",
                    "uri": "assets/svg/multi_pan_scale_invariant.svg",
                    "state_bindings": {"rule": "cube_equals_2_spheres", "target": 2}
                }
            ]
        },
        "interaction_model": {
            "input_mechanic": "SINGLE_CHOICE",
            "modality_configurations": {
                "tap_select": {
                    "options": [
                        {"option_id": "opt_1", "display_value": "2"},
                        {"option_id": "opt_2", "display_value": "4"},
                        {"option_id": "opt_3", "display_value": "6"}
                    ]
                },
                "spoken_dictated": {
                    "target_tokens": ["two", "2"],
                    "acoustic_confidence_threshold": 0.75
                }
            }
        },
        "scaffolding_protocol": {
            "level_1_reflection_prompt": {
                "spoken_text": "Look at how 1 cube balances 2 spheres on every scale.",
                "pedagogical_target": "STRATEGY_REFLECTION_PIVOT",
                "preserves_productive_struggle": True
            },
            "level_2_representation_shift": {
                "spoken_text": "1 cube always equals 2 spheres.",
                "target_representation": "VISUAL",
                "visual_asset_override": "assets/svg/cube_to_sphere_ratio.svg"
            },
            "level_3_prerequisite_bridge": {
                "spoken_text": "2 spheres match 1 cube.",
                "target_prerequisite_subskill_id": "M-NQ-04",
                "interactive_overlay": "WEIGHT_SUBSTITUTION_PALETTE"
            }
        },
        "rubric": {
            "evaluation_mode": "DETERMINISTIC_EXACT_MATCH",
            "correct_criteria": {"selected_option_id": "opt_1"},
            "diagnostic_distractors": [
                {
                    "response_pattern": "opt_2",
                    "diagnostic_misconception": "ADDITIVE_OVERCOUNTING",
                    "recommended_ws3_branch": "PREREQUISITE_STRENGTHENING"
                },
                {
                    "response_pattern": "opt_3",
                    "diagnostic_misconception": "EQUALITY_AS_SUM_TOTAL",
                    "recommended_ws3_branch": "STRATEGY_REFLECTION_PIVOT"
                }
            ]
        },
        "safeguard_metadata": {
            "reading_grade_level": 0.7,
            "has_unvoiced_text": False,
            "cultural_neutrality_verified": True,
            "contains_gamified_dark_patterns": False
        }
    },
    {
        "item_id": "ITEM-M-OP-05-0019",
        "schema_version": "1.3.0",
        "target_subskill_id": "M-OP-05",
        "domain_id": "MATHEMATICS",
        "evidence_archetype": "CONCEPTUAL",
        "cognitive_depth": "GENERALIZE",
        "transfer_level": "LEVEL_4_STRUCTURAL",
        "primary_modality": "TAP_SELECT",
        "supported_alternative_modalities": ["SPOKEN_DICTATED"],
        "language_load_class": "PURE_REASONING",
        "representation_type": "VISUAL",
        "challenge_type": "MULTIPLE_SOLUTIONS",
        "creation_stage": "ANSWERING",
        "estimated_duration_seconds": 90,
        "prompt_structure": {
            "spoken_audio_uri": "assets/audio/math/m_op_05_0019_prompt.mp3",
            "display_text": "Which number balances ten minus unknown?",
            "visual_assets": [
                {
                    "asset_id": "eq_10_minus_box_eq_4_plus_2",
                    "asset_type": "STATIC_SVG",
                    "uri": "assets/svg/eq_10_minus_box_eq_4_plus_2.svg"
                }
            ]
        },
        "interaction_model": {
            "input_mechanic": "SINGLE_CHOICE",
            "modality_configurations": {
                "tap_select": {
                    "options": [
                        {"option_id": "opt_1", "display_value": "4"},
                        {"option_id": "opt_2", "display_value": "6"},
                        {"option_id": "opt_3", "display_value": "10"}
                    ]
                },
                "spoken_dictated": {
                    "target_tokens": ["four", "4"],
                    "acoustic_confidence_threshold": 0.75
                }
            }
        },
        "scaffolding_protocol": {
            "level_1_reflection_prompt": {
                "spoken_text": "First calculate 4 plus 2. What is that sum?",
                "pedagogical_target": "STRATEGY_REFLECTION_PIVOT",
                "preserves_productive_struggle": True
            },
            "level_2_representation_shift": {
                "spoken_text": "4 plus 2 is 6. So 10 minus what equals 6?",
                "target_representation": "CONCRETE",
                "visual_asset_override": "assets/svg/ten_frame_subtraction_6.svg"
            },
            "level_3_prerequisite_bridge": {
                "spoken_text": "10 minus 4 equals 6.",
                "target_prerequisite_subskill_id": "M-OP-02",
                "interactive_overlay": "SUBTRACTION_SLIDER"
            }
        },
        "rubric": {
            "evaluation_mode": "DETERMINISTIC_EXACT_MATCH",
            "correct_criteria": {"selected_option_id": "opt_1"},
            "diagnostic_distractors": [
                {
                    "response_pattern": "opt_2",
                    "diagnostic_misconception": "PARTIAL_ADDEND_SUM",
                    "recommended_ws3_branch": "STRATEGY_REFLECTION_PIVOT"
                },
                {
                    "response_pattern": "opt_3",
                    "diagnostic_misconception": "EQUALITY_AS_SUM_TOTAL",
                    "recommended_ws3_branch": "STRATEGY_REFLECTION_PIVOT"
                }
            ]
        },
        "safeguard_metadata": {
            "reading_grade_level": 0.6,
            "has_unvoiced_text": False,
            "cultural_neutrality_verified": True,
            "contains_gamified_dark_patterns": False
        }
    },
    {
        "item_id": "ITEM-M-OP-05-0020",
        "schema_version": "1.3.0",
        "target_subskill_id": "M-OP-05",
        "domain_id": "MATHEMATICS",
        "evidence_archetype": "CONCEPTUAL",
        "cognitive_depth": "GENERALIZE",
        "transfer_level": "LEVEL_4_STRUCTURAL",
        "primary_modality": "TAP_SELECT",
        "supported_alternative_modalities": ["SPOKEN_DICTATED"],
        "language_load_class": "PURE_REASONING",
        "representation_type": "SYMBOLIC",
        "challenge_type": "STRATEGY_SELECTION",
        "creation_stage": "ANSWERING",
        "estimated_duration_seconds": 90,
        "prompt_structure": {
            "spoken_audio_uri": "assets/audio/math/m_op_05_0020_prompt.mp3",
            "display_text": "Which value keeps the structural balance?",
            "visual_assets": [
                {
                    "asset_id": "structural_law_a_b_c",
                    "asset_type": "STATIC_SVG",
                    "uri": "assets/svg/structural_law_a_b_c.svg"
                }
            ]
        },
        "interaction_model": {
            "input_mechanic": "SINGLE_CHOICE",
            "modality_configurations": {
                "tap_select": {
                    "options": [
                        {"option_id": "opt_1", "display_value": "1"},
                        {"option_id": "opt_2", "display_value": "0"},
                        {"option_id": "opt_3", "display_value": "2"}
                    ]
                },
                "spoken_dictated": {
                    "target_tokens": ["one", "1"],
                    "acoustic_confidence_threshold": 0.75
                }
            }
        },
        "scaffolding_protocol": {
            "level_1_reflection_prompt": {
                "spoken_text": "If a balance gets 1 added to the left side, what must be added to the right side?",
                "pedagogical_target": "STRATEGY_REFLECTION_PIVOT",
                "preserves_productive_struggle": True
            },
            "level_2_representation_shift": {
                "spoken_text": "To keep an equation level, whatever you add to one side, add to the other side.",
                "target_representation": "VISUAL",
                "visual_asset_override": "assets/svg/abstract_balance_plus_1.svg"
            },
            "level_3_prerequisite_bridge": {
                "spoken_text": "Add 1 to both sides to maintain equality.",
                "target_prerequisite_subskill_id": "M-OP-01",
                "interactive_overlay": "EQUATION_INVARIANT_BEAM"
            }
        },
        "rubric": {
            "evaluation_mode": "DETERMINISTIC_EXACT_MATCH",
            "correct_criteria": {"selected_option_id": "opt_1"},
            "diagnostic_distractors": [
                {
                    "response_pattern": "opt_2",
                    "diagnostic_misconception": "IDENTITY_COPYING",
                    "recommended_ws3_branch": "STRATEGY_REFLECTION_PIVOT"
                },
                {
                    "response_pattern": "opt_3",
                    "diagnostic_misconception": "ADDITIVE_OVERCOUNTING",
                    "recommended_ws3_branch": "PREREQUISITE_STRENGTHENING"
                }
            ]
        },
        "safeguard_metadata": {
            "reading_grade_level": 0.6,
            "has_unvoiced_text": False,
            "cultural_neutrality_verified": True,
            "contains_gamified_dark_patterns": False
        }
    }
]

for item in items_data:
    file_name = f"{item['item_id']}.json"
    file_path = base_dir / file_name
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(item, f, indent=2)
    print(f"Updated {file_name}")
