import json
import glob
from pathlib import Path

BASE_DIR = Path(r"c:\Users\Asus\ALP")

GENUINE_PURE_REASONING_SUBSKILLS = {
    "L-CO-01", "L-CO-02", "L-CO-03", "L-CO-04",
    "L-CE-03", "L-CE-04",
    "L-AR-01", "L-AR-02",
    "L-RC-01", "L-RC-02", "L-RC-03", "L-RC-04", "L-RC-05"
}

files = sorted(glob.glob(str(BASE_DIR / "question_bank" / "items" / "LOGICAL_REASONING" / "*" / "*.json")))

selected = []
for f in files:
    with open(f, "r", encoding="utf-8") as fp:
        it = json.load(fp)
    sub = it.get("target_subskill_id")
    lang = it.get("language_load_class")
    fk = it.get("safeguard_metadata", {}).get("reading_grade_level", 0.0)
    if sub in GENUINE_PURE_REASONING_SUBSKILLS and lang == "PURE_REASONING" and fk > 1.0:
        selected.append(it)
        if len(selected) == 10:
            break

print(f"Found {len(selected)} genuine PURE_REASONING items over limit.")
for i, it in enumerate(selected, 1):
    print(f"\n==================== ITEM {i}: {it['item_id']} ====================")
    print(json.dumps(it, indent=2, ensure_ascii=False))
