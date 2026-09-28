import json
import glob
from collections import Counter
from pathlib import Path

BASE_DIR = Path(r"c:\Users\Asus\ALP")
files = glob.glob(str(BASE_DIR / "frontend" / "public" / "data" / "question_bank" / "items_*.json"))

print(f"Reading bundle files: {len(files)}")

level_1_counts = Counter()
level_2_counts = Counter()
level_3_counts = Counter()
total_items = 0

for f in files:
    with open(f, "r", encoding="utf-8") as fp:
        items = json.load(fp)
    total_items += len(items)
    for it in items:
        scaff = it.get("scaffolding_protocol", {})
        l1 = scaff.get("level_1_reflection_prompt", {}).get("prompt", "").strip()
        l2 = scaff.get("level_2_representation_shift", {}).get("hint", "").strip()
        l3 = scaff.get("level_3_prerequisite_bridge", {}).get("hint", "").strip()
        
        if l1: level_1_counts[l1] += 1
        if l2: level_2_counts[l2] += 1
        if l3: level_3_counts[l3] += 1

print(f"Total items inspected: {total_items}")

print(f"\n--- LEVEL 1 REFLECTION PROMPTS: {len(level_1_counts)} distinct strings ---")
for p, c in level_1_counts.most_common(20):
    print(f"  [{c} items] \"{p}\"")
if len(level_1_counts) > 20:
    print(f"  ... and {len(level_1_counts) - 20} more distinct level 1 prompts.")

print(f"\n--- LEVEL 2 REPRESENTATION SHIFT: {len(level_2_counts)} distinct strings ---")
for h, c in level_2_counts.most_common():
    print(f"  [{c} items] \"{h}\"")

print(f"\n--- LEVEL 3 PREREQUISITE BRIDGE: {len(level_3_counts)} distinct strings ---")
for h, c in level_3_counts.most_common():
    print(f"  [{c} items] \"{h}\"")
