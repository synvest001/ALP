import json
import glob
import os
from pathlib import Path
from collections import Counter, defaultdict

BASE_DIR = Path(r"c:\Users\Asus\ALP")

# Load curriculum map subskills
curriculum_map_path = BASE_DIR / "frontend" / "public" / "data" / "curriculum_map.json"
with open(curriculum_map_path, "r", encoding="utf-8") as f:
    cmap = json.load(f)

cmap_subskills = set()
for d in cmap.get("domains", []):
    for s in d.get("strands", []):
        for sk in s.get("skills", []):
            cmap_subskills.add(sk.get("code"))

print(f"Total skills in curriculum_map.json: {len(cmap_subskills)}")

# 1. question_bank/items/
item_files = glob.glob(str(BASE_DIR / "question_bank" / "items" / "*" / "*" / "*.json"))
print(f"Total files in question_bank/items/: {len(item_files)}")

qb_domain_counts = Counter()
qb_subskill_counts = Counter()
qb_not_in_cmap = Counter()

for f in item_files:
    try:
        with open(f, "r", encoding="utf-8") as fp:
            it = json.load(fp)
            dom = it.get("domain_id")
            sub = it.get("target_subskill_id")
            qb_domain_counts[dom] += 1
            qb_subskill_counts[sub] += 1
            if sub not in cmap_subskills:
                qb_not_in_cmap[sub] += 1
    except Exception as e:
        print(f"Error reading {f}: {e}")

# 2. frontend/public/data/question_bank/
pub_files = glob.glob(str(BASE_DIR / "frontend" / "public" / "data" / "question_bank" / "items_*.json"))
pub_domain_counts = Counter()
pub_subskill_counts = Counter()
pub_not_in_cmap = Counter()

for pf in pub_files:
    with open(pf, "r", encoding="utf-8") as fp:
        items = json.load(fp)
        for it in items:
            dom = it.get("domain_id")
            sub = it.get("target_subskill_id")
            pub_domain_counts[dom] += 1
            pub_subskill_counts[sub] += 1
            if sub not in cmap_subskills:
                pub_not_in_cmap[sub] += 1

print("\n--- QUESTION_BANK/ITEMS DOMAIN COUNTS ---")
for dom, c in sorted(qb_domain_counts.items()):
    print(f"  {dom}: {c}")

print("\n--- FRONTEND/PUBLIC/DATA/QUESTION_BANK DOMAIN COUNTS ---")
for dom, c in sorted(pub_domain_counts.items()):
    print(f"  {dom}: {c}")

print(f"\nDistinct target_subskill_ids in question_bank/items NOT in curriculum_map.json: {len(qb_not_in_cmap)}")
for sub, c in sorted(qb_not_in_cmap.items()):
    print(f"  {sub}: {c} items")

print(f"\nDistinct target_subskill_ids in frontend/public NOT in curriculum_map.json: {len(pub_not_in_cmap)}")
for sub, c in sorted(pub_not_in_cmap.items()):
    print(f"  {sub}: {c} items")
