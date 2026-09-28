import json
import glob
from pathlib import Path
from collections import Counter, defaultdict
import textstat

BASE_DIR = Path(r"c:\Users\Asus\ALP")
files = sorted(glob.glob(str(BASE_DIR / "question_bank" / "items" / "*" / "*" / "*.json")))

print(f"Total items on disk: {len(files)}")

# 1. language_load_class counts by domain
lang_by_domain = defaultdict(Counter)
subskill_counts_by_domain = defaultdict(Counter)

# 2. PURE_REASONING metrics
pure_total = 0
pure_fk_textstat_gt_1 = 0
pure_fk_meta_gt_1 = 0
pure_words_gt_8 = 0
pure_both_gt = 0

# 3. INTEGRATED metrics
integrated_total = 0
integrated_fk_textstat_gt_6 = 0
integrated_fk_meta_gt_6 = 0

# 4. Genuinely pure reasoning list
pure_items = []

for f in files:
    with open(f, "r", encoding="utf-8") as fp:
        it = json.load(fp)
    
    dom = it.get("domain_id")
    sub = it.get("target_subskill_id")
    lang = it.get("language_load_class")
    prompt = it.get("prompt_structure", {}).get("display_text", "")
    words = len(prompt.split())
    meta_fk = it.get("safeguard_metadata", {}).get("reading_grade_level", 0.0)
    
    try:
        calc_fk = textstat.flesch_kincaid_grade(prompt)
    except Exception:
        calc_fk = 0.0

    lang_by_domain[dom][lang] += 1
    subskill_counts_by_domain[dom][sub] += 1

    if lang == "PURE_REASONING":
        pure_total += 1
        pure_items.append(it)
        if calc_fk > 1.0:
            pure_fk_textstat_gt_1 += 1
        if meta_fk > 1.0:
            pure_fk_meta_gt_1 += 1
        if words > 8:
            pure_words_gt_8 += 1
        if calc_fk > 1.0 and words > 8:
            pure_both_gt += 1
    elif lang == "INTEGRATED_LANGUAGE_AND_REASONING":
        integrated_total += 1
        if calc_fk > 6.0:
            integrated_fk_textstat_gt_6 += 1
        if meta_fk > 6.0:
            integrated_fk_meta_gt_6 += 1

print("\n--- 1. LANGUAGE_LOAD_CLASS COUNTS BY DOMAIN ---")
for dom in sorted(lang_by_domain.keys()):
    print(f"Domain: {dom}")
    for l_class, cnt in sorted(lang_by_domain[dom].items()):
        print(f"  {l_class}: {cnt}")

print("\n--- 2. PURE_REASONING METRICS ---")
print(f"Total PURE_REASONING items: {pure_total}")
print(f"PURE_REASONING with textstat FK > 1.0: {pure_fk_textstat_gt_1}")
print(f"PURE_REASONING with safeguard_metadata FK > 1.0: {pure_fk_meta_gt_1}")
print(f"PURE_REASONING with display_text > 8 words: {pure_words_gt_8}")
print(f"PURE_REASONING with textstat FK > 1.0 AND words > 8: {pure_both_gt}")

print("\n--- 3. INTEGRATED_LANGUAGE_AND_REASONING METRICS ---")
print(f"Total INTEGRATED items: {integrated_total}")
print(f"INTEGRATED with textstat FK > 6.0: {integrated_fk_textstat_gt_6}")
print(f"INTEGRATED with safeguard_metadata FK > 6.0: {integrated_fk_meta_gt_6}")

print(f"\n--- 4. PER-SUBSKILL COUNTS FOR PURE_REASONING ITEMS ---")
pure_subskills = Counter(it.get("target_subskill_id") for it in pure_items)
for sub, cnt in sorted(pure_subskills.items()):
    print(f"  {sub}: {cnt}")
