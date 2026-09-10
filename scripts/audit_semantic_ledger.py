import json
import glob
import hashlib
from pathlib import Path

def get_correct_option_value(item):
    try:
        correct_opt_id = item.get("rubric", {}).get("correct_criteria", {}).get("selected_option_id")
        options = item.get("interaction_model", {}).get("modality_configurations", {}).get("tap_select", {}).get("options", [])
        for opt in options:
            if opt.get("option_id") == correct_opt_id:
                return opt.get("display_value", "")
    except Exception:
        pass
    return ""

def compute_semantic_hash(item):
    subskill = item.get("target_subskill_id", "")
    prompt = item.get("prompt_structure", {}).get("display_text", "")
    
    # Extract state bindings if any
    assets = item.get("prompt_structure", {}).get("visual_assets", [])
    bindings = ""
    if assets and isinstance(assets, list):
        b = assets[0].get("state_bindings")
        if b:
            # Sort keys for deterministic hashing
            bindings = json.dumps(b, sort_keys=True)
            
    correct_val = get_correct_option_value(item)
    
    semantic_string = f"{subskill}|{prompt}|{bindings}|{correct_val}"
    return hashlib.sha256(semantic_string.encode('utf-8')).hexdigest()

def main():
    items_dir = Path("c:/Users/Asus/ALP/question_bank/items")
    files = items_dir.rglob("*.json")
    
    ledger = set()
    ledger_details = {}
    duplicates = 0
    
    for f in files:
        with open(f, "r", encoding="utf-8") as file:
            try:
                item = json.load(file)
                h = compute_semantic_hash(item)
                if h in ledger:
                    duplicates += 1
                else:
                    ledger.add(h)
                    ledger_details[h] = str(f.relative_to(items_dir))
            except Exception as e:
                print(f"Error processing {f}: {e}")
                
    ledger_file = Path("c:/Users/Asus/ALP/question_bank/ledger/semantic_ledger.json")
    ledger_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(ledger_file, "w", encoding="utf-8") as f:
        json.dump(list(ledger), f, indent=2)
        
    print(f"Audited {len(ledger) + duplicates} items.")
    print(f"Found {len(ledger)} unique semantic cores.")
    print(f"Found {duplicates} duplicates already existing in the bank.")
    print(f"Semantic ledger saved to {ledger_file}")

if __name__ == "__main__":
    main()
