import json
from datetime import datetime, timezone
from pathlib import Path
import sys

# Add validator parent dir to path
sys.path.append(str(Path("c:/Users/Asus/ALP/question_bank/validators").resolve()))
from stage1_compliance_validator import Stage1ComplianceValidator

items_dir = Path("c:/Users/Asus/ALP/question_bank/items/MATHEMATICS/M-OP-05")
ledger_file = Path("c:/Users/Asus/ALP/question_bank/ledger/validation_ledger.jsonl")

validator = Stage1ComplianceValidator()
item_files = sorted(list(items_dir.glob("ITEM-M-OP-05-*.json")))

print(f"Found {len(item_files)} items to validate.")

total_passed = 0
total_failed = 0
ledger_entries = []

for file_path in item_files:
    with open(file_path, "r", encoding="utf-8") as f:
        item_data = json.load(f)
    
    item_id = item_data.get("item_id", file_path.name)
    errors = validator.validate_item(item_data)
    
    timestamp = datetime.now(timezone.utc).isoformat()
    
    if not errors:
        total_passed += 1
        print(f"PASS: {item_id}")
        ledger_entry = {
            "item_id": item_id,
            "target_subskill_id": item_data.get("target_subskill_id"),
            "schema_version": item_data.get("schema_version"),
            "validation_stage": "STAGE_1_COMPLIANCE",
            "status": "PASSED",
            "timestamp": timestamp,
            "errors": []
        }
        ledger_entries.append(ledger_entry)
    else:
        total_failed += 1
        print(f"FAIL: {item_id}")
        for err in errors:
            print(f"  - {err}")

# Write to ledger if all passed or for passing items
with open(ledger_file, "w", encoding="utf-8") as f:
    for entry in ledger_entries:
        f.write(json.dumps(entry) + "\n")

print("\n--- BATCH VALIDATION SUMMARY ---")
print(f"Total Items Evaluated: {len(item_files)}")
print(f"Passed: {total_passed}")
print(f"Failed: {total_failed}")
print(f"Ledger written to: {ledger_file}")

if total_failed > 0:
    sys.exit(1)
else:
    sys.exit(0)
