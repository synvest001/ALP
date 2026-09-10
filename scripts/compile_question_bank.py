import os
import sys
import glob
import json
from pathlib import Path
from collections import defaultdict

BASE_DIR = Path(__file__).resolve().parent.parent
ITEMS_DIR = BASE_DIR / "question_bank" / "items"
OUT_DIR = BASE_DIR / "frontend" / "public" / "data" / "question_bank"
OUT_DIR.mkdir(parents=True, exist_ok=True)

def main():
    print(f"Scanning question files in {ITEMS_DIR}...")
    files = glob.glob(str(ITEMS_DIR / "**" / "*.json"), recursive=True)
    print(f"Found {len(files)} items.")

    domain_items = defaultdict(list)
    index_entries = []

    for i, file_path in enumerate(files):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                item = json.load(f)
        except Exception as e:
            print(f"Error reading {file_path}: {e}")
            continue

        item_id = item.get("item_id")
        domain_id = item.get("domain_id")
        subskill_id = item.get("target_subskill_id")
        depth = item.get("cognitive_depth", "APPLY")
        transfer = item.get("transfer_level", "LEVEL_1_SURFACE")

        cleaned_item = {
            "item_id": item_id,
            "target_subskill_id": subskill_id,
            "domain_id": domain_id,
            "evidence_archetype": item.get("evidence_archetype", "CONCEPTUAL"),
            "language_load_class": item.get("language_load_class", "PURE_REASONING"),
            "challenge_type": item.get("challenge_type", "MULTIPLE_CHOICE"),
            "cognitive_depth": depth,
            "transfer_level": transfer,
            "representation_type": item.get("representation_type", "VISUAL"),
            "primary_modality": item.get("primary_modality", "TAP_SELECT"),
            "prompt_structure": item.get("prompt_structure", {}),
            "scaffolding_protocol": item.get("scaffolding_protocol", {}),
            "rubric": item.get("rubric", {}),
            "interaction_model": item.get("interaction_model", {}),
            "options": item.get("options", [])
        }

        domain_items[domain_id].append(cleaned_item)
        index_entries.append({
            "id": item_id,
            "domain": domain_id,
            "subskill": subskill_id,
            "depth": depth,
            "transfer": transfer
        })

        if (i + 1) % 3000 == 0:
            print(f"Processed {i + 1}/{len(files)} items...")

    print(f"Total processed: {len(index_entries)} items across {len(domain_items)} domains.")

    # Write domain bundles
    domain_stats = {}
    for dom, items in domain_items.items():
        out_file = OUT_DIR / f"items_{dom}.json"
        with open(out_file, "w", encoding="utf-8") as f:
            json.dump(items, f, separators=(',', ':'))
        size_kb = os.path.getsize(out_file) / 1024
        domain_stats[dom] = {
            "count": len(items),
            "size_kb": round(size_kb, 1),
            "file": f"items_{dom}.json"
        }
        print(f"Saved {dom}: {len(items)} items ({size_kb:.1f} KB) -> {out_file.name}")

    # Write manifest
    manifest = {
        "total_items": len(index_entries),
        "domains": domain_stats,
        "index": index_entries
    }
    manifest_file = OUT_DIR / "manifest.json"
    with open(manifest_file, "w", encoding="utf-8") as f:
        json.dump(manifest, f, separators=(',', ':'))
    manifest_size_kb = os.path.getsize(manifest_file) / 1024
    print(f"Saved manifest: {len(index_entries)} entries ({manifest_size_kb:.1f} KB) -> {manifest_file.name}")
    print("Done! Question bank compiled successfully.")

if __name__ == "__main__":
    main()
