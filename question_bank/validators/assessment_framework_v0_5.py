# Authoritative subskill -> evidence_archetype mapping from WS2 §3.1

SUBSKILL_ARCHETYPE_MAP = {}

def _add_range(prefix: str, start: int, end: int, archetype: str):
    for i in range(start, end + 1):
        SUBSKILL_ARCHETYPE_MAP[f"{prefix}-{i:02d}"] = archetype

def _add_list(subskills: list, archetype: str):
    for s in subskills:
        SUBSKILL_ARCHETYPE_MAP[s] = archetype

# 1. CONCEPTUAL
_add_range("M-NQ", 1, 6, "CONCEPTUAL")
SUBSKILL_ARCHETYPE_MAP["M-OP-05"] = "CONCEPTUAL"
_add_range("M-FR", 1, 6, "CONCEPTUAL")
_add_range("M-PA", 1, 3, "CONCEPTUAL")
_add_range("M-GS", 1, 5, "CONCEPTUAL")
_add_range("S-KN", 1, 10, "CONCEPTUAL")
_add_range("S-OC", 1, 3, "CONCEPTUAL")
_add_range("S-PP", 1, 2, "CONCEPTUAL")
_add_range("S-EE", 1, 3, "CONCEPTUAL")
_add_range("W-KO", 5, 6, "CONCEPTUAL")

# 2. PROCEDURAL_FLUENCY
_add_range("M-OP", 1, 3, "PROCEDURAL_FLUENCY")
_add_range("M-ME", 1, 8, "PROCEDURAL_FLUENCY")
_add_range("M-DU", 1, 4, "PROCEDURAL_FLUENCY")
_add_range("E-PD", 1, 6, "PROCEDURAL_FLUENCY")
_add_range("E-SG", 1, 5, "PROCEDURAL_FLUENCY")
_add_range("E-RF", 1, 5, "PROCEDURAL_FLUENCY")
_add_list(["E-WE-01", "E-OL-06", "S-OC-04", "S-OC-05", "S-IN-02", "S-IN-05"], "PROCEDURAL_FLUENCY")

# 3. KNOWLEDGE_ACQUISITION
_add_range("E-VM", 1, 6, "KNOWLEDGE_ACQUISITION")
SUBSKILL_ARCHETYPE_MAP["E-OL-01"] = "KNOWLEDGE_ACQUISITION"
_add_range("W-KA", 1, 8, "KNOWLEDGE_ACQUISITION")
_add_range("W-KO", 1, 4, "KNOWLEDGE_ACQUISITION")
SUBSKILL_ARCHETYPE_MAP["S-KN-11"] = "KNOWLEDGE_ACQUISITION"

# 4. STRATEGIC_REASONING
_add_list(["M-OP-04", "M-OP-06", "M-PA-04", "M-PA-06", "M-GS-06", "M-GS-07"], "STRATEGIC_REASONING")
_add_range("M-DU", 5, 8, "STRATEGIC_REASONING")
_add_range("M-PS", 1, 7, "STRATEGIC_REASONING")
_add_list(["E-OL-02", "E-OL-03"], "STRATEGIC_REASONING")
_add_range("E-CR", 1, 9, "STRATEGIC_REASONING")
_add_range("E-WE", 6, 8, "STRATEGIC_REASONING")
_add_range("S-PP", 3, 4, "STRATEGIC_REASONING")
_add_list(["S-EE-04", "S-EE-05", "S-IN-04", "S-IN-06"], "STRATEGIC_REASONING")
_add_range("W-KP", 2, 5, "STRATEGIC_REASONING")

# All Logic domain subskills
for l_prefix in ["L-PC", "L-AR", "L-SR", "L-RC", "L-CO", "L-CE"]:
    _add_range(l_prefix, 1, 10, "STRATEGIC_REASONING")

# 5. CREATIVE_GENERATIVE
_add_list(["M-PA-05", "M-PS-08", "E-VM-07", "E-OL-04", "E-OL-05"], "CREATIVE_GENERATIVE")
_add_range("E-CC", 1, 6, "CREATIVE_GENERATIVE")
_add_list(["E-WE-02", "E-WE-03", "E-WE-04", "E-WE-05", "E-WE-09"], "CREATIVE_GENERATIVE")
_add_range("S-MO", 1, 4, "CREATIVE_GENERATIVE")
_add_list(["S-IN-01", "S-IN-03", "W-KP-01", "W-KP-06"], "CREATIVE_GENERATIVE")
