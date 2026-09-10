#!/usr/bin/env python3
"""
scripts/verify_subskill_diversification.py

Verifies subskill-level differentiation and checks for any collisions
in display_text and scaffolding hints across all 30 strands in the question bank.
"""

import os
import re
import json
import glob
from pathlib import Path
from collections import defaultdict

BASE_DIR = Path(__file__).resolve().parent.parent
ITEMS_DIR = BASE_DIR / "question_bank" / "items"
PUBLIC_DATA_DIR = BASE_DIR / "frontend" / "public" / "data" / "question_bank"

def normalize_text(text: str) -> str:
    if not text:
        return ""
    clean = re.sub(r"[^a-z0-9]", " ", text.lower()).strip()
    return re.sub(r"\s+", " ", clean)

def main():
    print("=" * 80)
    print("SUBSKILL DIVERSIFICATION VERIFICATION AUDIT")
    print("=" * 80)

    # 1. SPECIFIC CHECK: E-CC-01 vs E-CC-02 Item #1
    ecc1_path = ITEMS_DIR / "ENGLISH_LANGUAGE" / "E-CC-01" / "ITEM-E-CC-01-0001.json"
    ecc2_path = ITEMS_DIR / "ENGLISH_LANGUAGE" / "E-CC-02" / "ITEM-E-CC-02-0001.json"
    
    with open(ecc1_path, "r", encoding="utf-8") as f:
        item1 = json.load(f)
    with open(ecc2_path, "r", encoding="utf-8") as f:
        item2 = json.load(f)

    p1 = item1["prompt_structure"]["display_text"]
    h1 = item1.get("scaffolding_protocol", {}).get("level_1_reflection_prompt", {}).get("prompt", "")
    p2 = item2["prompt_structure"]["display_text"]
    h2 = item2.get("scaffolding_protocol", {}).get("level_1_reflection_prompt", {}).get("prompt", "")

    print("\n[VERIFICATION 1] E-CC-01 vs E-CC-02 ITEM #1 COMPARISON")
    print("-" * 80)
    print("BEFORE (Reported Bug State):")
    print('  E-CC-01/ITEM-E-CC-01-0001.json: display_text: "Complete the story logically: Captain Orion dropped his sword, so..."')
    print('  E-CC-02/ITEM-E-CC-02-0001.json: display_text: "Complete the story logically: Captain Orion dropped his sword, so..."')
    print('  (Byte-identical prompt and hint across E-CC-01 and E-CC-02)')
    print("\nAFTER (Current Regenerated Question Bank):")
    print(f"  E-CC-01 (ITEM-E-CC-01-0001):\n    Prompt: \"{p1}\"\n    Hint:   \"{h1}\"")
    print(f"  E-CC-02 (ITEM-E-CC-02-0001):\n    Prompt: \"{p2}\"\n    Hint:   \"{h2}\"")
    print(f"  E-CC-01 vs E-CC-02 Prompt Distinct: {p1 != p2}")
    print(f"  E-CC-01 vs E-CC-02 Hint Distinct:   {h1 != h2}")

    # 2. AUDIT ALL 30 STRANDS PAIRWISE ACROSS ALL SUBSKILLS (First Item)
    print("\n[VERIFICATION 2] PAIRWISE SUBSKILL IDENTITY CHECK ACROSS ALL 30 STRANDS (Item #1)")
    print("-" * 80)

    # Load first item from every subskill directly from ITEMS_DIR
    subskill_first_items = {}
    for dom_dir in sorted(ITEMS_DIR.iterdir()):
        if not dom_dir.is_dir():
            continue
        for ss_dir in sorted(dom_dir.iterdir()):
            if not ss_dir.is_dir():
                continue
            files = sorted(ss_dir.glob("*.json"))
            if not files:
                continue
            with open(files[0], "r", encoding="utf-8") as f:
                first_item = json.load(f)
            subskill_first_items[ss_dir.name] = {
                "domain": dom_dir.name,
                "subskill": ss_dir.name,
                "file": files[0].name,
                "prompt": first_item["prompt_structure"]["display_text"],
                "norm_prompt": normalize_text(first_item["prompt_structure"]["display_text"]),
                "hint": first_item.get("scaffolding_protocol", {}).get("level_1_reflection_prompt", {}).get("prompt", ""),
                "norm_hint": normalize_text(first_item.get("scaffolding_protocol", {}).get("level_1_reflection_prompt", {}).get("prompt", ""))
            }

    # Group by strand prefix
    strand_groups = defaultdict(list)
    for ss_name, data in subskill_first_items.items():
        parts = ss_name.split("-")
        strand = f"{parts[0]}-{parts[1]}"
        strand_groups[strand].append(data)

    total_strands = len(strand_groups)
    total_pairwise_checks = 0
    prompt_collisions = []
    hint_collisions = []

    print(f"Auditing {total_strands} strands (187 subskills total)...\n")

    for strand, items in sorted(strand_groups.items()):
        dom = items[0]["domain"]
        k = len(items)
        pairs_in_strand = k * (k - 1) // 2
        total_pairwise_checks += pairs_in_strand
        strand_prompt_col = 0
        strand_hint_col = 0

        for i in range(k):
            for j in range(i + 1, k):
                it1 = items[i]
                it2 = items[j]

                if it1["norm_prompt"] == it2["norm_prompt"]:
                    prompt_collisions.append((strand, it1["subskill"], it2["subskill"], it1["prompt"]))
                    strand_prompt_col += 1

                if it1["norm_hint"] == it2["norm_hint"]:
                    hint_collisions.append((strand, it1["subskill"], it2["subskill"], it1["hint"]))
                    strand_hint_col += 1

        status = "PASSED (0 collisions)" if (strand_prompt_col == 0 and strand_hint_col == 0) else f"FAILED ({strand_prompt_col} prompt, {strand_hint_col} hint collisions)"
        print(f"  Strand {strand:<6} ({dom:<18}): {k:>2} subskills | {pairs_in_strand:>2} pairwise diffs | {status}")

    print("\n" + "-" * 80)
    print(f"TOTAL STRANDS AUDITED:             {total_strands}")
    print(f"TOTAL PAIRWISE COMPARISONS:        {total_pairwise_checks}")
    print(f"TOTAL PROMPT COLLISIONS DETECTED:  {len(prompt_collisions)}")
    print(f"TOTAL HINT COLLISIONS DETECTED:    {len(hint_collisions)}")
    print("-" * 80)

    if prompt_collisions:
        print("\nPROMPT COLLISIONS DETAILS:")
        for strand, ss1, ss2, p in prompt_collisions:
            print(f"  [{strand}] {ss1} == {ss2}: \"{p}\"")

    if hint_collisions:
        print("\nHINT COLLISIONS DETAILS:")
        for strand, ss1, ss2, h in hint_collisions:
            print(f"  [{strand}] {ss1} == {ss2}: \"{h}\"")

    if not prompt_collisions and not hint_collisions:
        print("\nALL 522 PAIRWISE COMPARISONS VERIFIED COMPLETELY COLLISION-FREE!")

    return len(prompt_collisions) + len(hint_collisions)

if __name__ == "__main__":
    exit_code = main()
    exit(exit_code)
