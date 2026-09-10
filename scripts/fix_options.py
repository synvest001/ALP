import json
import os
from pathlib import Path

QUESTION_BANK_DIR = Path(r"c:\Users\Asus\ALP\question_bank\items")

count = 0
for root, _, files in os.walk(QUESTION_BANK_DIR):
    for file in files:
        if file.endswith(".json"):
            filepath = Path(root) / file
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    item = json.load(f)
                
                changed = False
                
                # Check interaction model
                options = item.get("interaction_model", {}).get("modality_configurations", {}).get("tap_select", {}).get("options", [])
                for opt in options:
                    if opt.get("display_value") == "Left Group (6)":
                        opt["display_value"] = "Left Group"
                        changed = True
                    elif opt.get("display_value") == "Right Group (2)":
                        opt["display_value"] = "Right Group"
                        changed = True
                        
                if changed:
                    with open(filepath, "w", encoding="utf-8") as f:
                        json.dump(item, f, indent=2)
                    count += 1
            except Exception as e:
                print(f"Error processing {file}: {e}")

print(f"Updated options in {count} files.")
