import glob
import json
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

subskills = [
    "L-PC-01", "L-PC-02", "L-PC-03", "L-PC-04",
    "L-SR-01", "L-SR-02", "L-SR-03", "L-SR-04", "L-SR-05",
    "L-CO-01", "L-CO-02", "L-CO-03", "L-CO-04",
    "L-CE-03", "L-CE-04",
    "L-AR-01", "L-AR-02",
    "L-RC-01", "L-RC-02", "L-RC-03", "L-RC-04", "L-RC-05"
]

for sub in subskills:
    files = sorted(glob.glob(f"question_bank/items/LOGICAL_REASONING/{sub}/*.json"))
    if files:
        with open(files[0], "r", encoding="utf-8") as fp:
            it = json.load(fp)
        arch = it.get("evidence_archetype")
        depth = it.get("cognitive_depth")
        fk = it.get("safeguard_metadata", {}).get("reading_grade_level")
        prompt = it.get("prompt_structure", {}).get("display_text")
        print(f"{sub:<10} | {arch:<20} | {depth:<10} | FK: {fk:<4} | Prompt: \"{prompt}\"")
