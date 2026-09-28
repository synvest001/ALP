import json
import glob
import sys
from pathlib import Path
from collections import Counter

BASE_DIR = Path(r"c:\Users\Asus\ALP")
sys.path.append(str(BASE_DIR / "question_bank" / "validators"))

from stage1_compliance_validator import Stage1ComplianceValidator

validator = Stage1ComplianceValidator()
files = sorted(glob.glob(str(BASE_DIR / "question_bank" / "items" / "*" / "*" / "*.json")))

print(f"Running Stage1ComplianceValidator on {len(files)} items...")

error_categories = Counter()
sample_errors = []
total_items_with_errors = 0
total_errors = 0

for i, f in enumerate(files):
    with open(f, "r", encoding="utf-8") as fp:
        it = json.load(fp)
    
    errs = validator.validate_item(it)
    if errs:
        total_items_with_errors += 1
        total_errors += len(errs)
        for e in errs:
            # categorize
            if "8-word" in e:
                error_categories["PURE_REASONING prompt exceeds 8 words"] += 1
            elif "reading_grade_level <= 1.0" in e:
                error_categories["PURE_REASONING reading_grade_level > 1.0"] += 1
            elif "reading_grade_level <= 6.0" in e:
                error_categories["INTEGRATED reading_grade_level > 6.0"] += 1
            elif "spoken_audio_uri" in e:
                error_categories["Missing spoken_audio_uri"] += 1
            elif "has_unvoiced_text" in e:
                error_categories["has_unvoiced_text != false"] += 1
            elif "evidence_archetype" in e:
                error_categories["Archetype mismatch"] += 1
            elif "item_id" in e:
                error_categories["Item ID mismatch"] += 1
            else:
                error_categories[e] += 1
        
        if len(sample_errors) < 20:
            sample_errors.append((it.get("item_id"), errs))

print(f"\n--- STAGE 1 VALIDATOR SUMMARY ---")
print(f"Total items evaluated: {len(files)}")
print(f"Items with at least one violation: {total_items_with_errors}")
print(f"Total violations found: {total_errors}")

print(f"\nViolations by category:")
for cat, cnt in sorted(error_categories.items(), key=lambda x: -x[1]):
    print(f"  {cat}: {cnt}")

print(f"\nFirst 10 sample items with violations:")
for item_id, errs in sample_errors[:10]:
    print(f"  Item {item_id}:")
    for e in errs:
        print(f"    - {e}")
