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
                
                prompt_struct = item.get("prompt_structure", {})
                if prompt_struct.get("display_text") == "Which letter does Sun start with?":
                    prompt_struct["display_text"] = "Which letter does this picture start with?"
                    with open(filepath, "w", encoding="utf-8") as f:
                        json.dump(item, f, indent=2)
                    count += 1
            except Exception as e:
                print(f"Error processing {file}: {e}")

print(f"Updated prompt in {count} files.")
