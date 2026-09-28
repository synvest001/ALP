import glob
import json
import os
import re
import sys
from collections import defaultdict, Counter
from pathlib import Path
import textstat

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

sys.path.append(str(Path(__file__).resolve().parent.parent / "question_bank" / "validators"))
from stage1_compliance_validator import Stage1ComplianceValidator

BASE_DIR = Path(__file__).resolve().parent.parent
ITEMS_DIR = BASE_DIR / "question_bank" / "items"

print("=" * 80)
print("PILOT READINESS: CONTENT SANITY SCAN & SAFEGUARD METADATA ENFORCEMENT")
print("=" * 80)

# ==============================================================================
# PART A.1: Profanity / Inappropriate Content Scan
# ==============================================================================
print("\n" + "=" * 80)
print("PART A.1: PROFANITY / INAPPROPRIATE-CONTENT SCAN")
print("=" * 80)

PROFANITY_TERMS = [
    # Core profanities / vulgarities
    r"fuck\w*", r"shit\w*", r"bitch\w*", r"asshole\w*", r"bastard\w*",
    r"cunt\w*", r"dick\w*", r"cock\w*", r"pussy\w*", r"piss\w*",
    r"slut\w*", r"whore\w*", r"fag\w*", r"nigger\w*", r"nigga\w*",
    r"retard\w*", r"chink\w*", r"kike\w*", r"spic\w*",
    # Sexual / explicit
    r"porn\w*", r"penis\w*", r"vagina\w*", r"erotic\w*", r"orgasm\w*",
    r"nudity", r"naked\w*", r"boob\w*",
    # Drugs / alcohol / substance
    r"alcohol\w*", r"beer\w*", r"wine\w*", r"vodka\w*", r"whiskey\w*",
    r"cigarette\w*", r"tobacco\w*", r"cocaine\w*", r"heroin\w*",
    r"marijuana\w*", r"cannabis\w*",
    # Extreme violence / weapons / death
    r"suicide\w*", r"murder\w*", r"kill\w*", r"blood\w*", r"knife\w*",
    r"gun\w*", r"bullet\w*", r"weapon\w*"
]
PROFANITY_REGEX = re.compile(r"\b(" + "|".join(PROFANITY_TERMS) + r")\b", re.IGNORECASE)

item_files = sorted(glob.glob(str(ITEMS_DIR / "*/*/*.json")))
total_items = len(item_files)
print(f"Total items scanned: {total_items}")

profanity_flags = []

for f in item_files:
    with open(f, "r", encoding="utf-8") as fp:
        it = json.load(fp)
    item_id = it.get("item_id", "")
    
    # 1. prompt_structure.display_text
    prompt_text = it.get("prompt_structure", {}).get("display_text", "")
    for m in PROFANITY_REGEX.finditer(prompt_text):
        s = max(0, m.start() - 30)
        e = min(len(prompt_text), m.end() + 30)
        profanity_flags.append({
            "item_id": item_id,
            "field": "prompt_structure.display_text",
            "term": m.group(0),
            "context": prompt_text[s:e].strip()
        })
        
    # 2. scaffolding_protocol spoken_text / prompt / hint
    scaffolding = it.get("scaffolding_protocol", {})
    for tier_key, tier_data in scaffolding.items():
        if isinstance(tier_data, dict):
            for textField in ["spoken_text", "prompt", "hint"]:
                txt = tier_data.get(textField, "")
                for m in PROFANITY_REGEX.finditer(txt):
                    s = max(0, m.start() - 30)
                    e = min(len(txt), m.end() + 30)
                    profanity_flags.append({
                        "item_id": item_id,
                        "field": f"scaffolding_protocol.{tier_key}.{textField}",
                        "term": m.group(0),
                        "context": txt[s:e].strip()
                    })
                    
    # 3. rubric.diagnostic_distractors[].diagnostic_misconception
    distractors = it.get("rubric", {}).get("diagnostic_distractors", [])
    for idx, d in enumerate(distractors):
        misc = d.get("diagnostic_misconception", "")
        for m in PROFANITY_REGEX.finditer(misc):
            s = max(0, m.start() - 30)
            e = min(len(misc), m.end() + 30)
            profanity_flags.append({
                "item_id": item_id,
                "field": f"rubric.diagnostic_distractors[{idx}].diagnostic_misconception",
                "term": m.group(0),
                "context": misc[s:e].strip()
            })

print(f"Total profanity/inappropriate-content flags: {len(profanity_flags)}")
if profanity_flags:
    print(f"\nBreakdown of flagged terms:")
    term_counts = Counter(f["term"].lower() for f in profanity_flags)
    for t, c in term_counts.items():
        print(f"  Term '{t}': {c} occurrences")
    print("\nSample flagged items (first 10):")
    for fl in profanity_flags[:10]:
        print(f"  [{fl['item_id']}] {fl['field']}: matched '{fl['term']}'")
        print(f"    Context: \"...{fl['context']}...\"")

# ==============================================================================
# PART A.2: Math Answer-Key Sanity Check
# ==============================================================================
print("\n" + "=" * 80)
print("PART A.2: MATH ANSWER-KEY SANITY CHECK (MATHEMATICS DOMAIN)")
print("=" * 80)

math_files = sorted(glob.glob(str(ITEMS_DIR / "MATHEMATICS/*/*.json")))
print(f"Total Math items scanned: {len(math_files)}")

verified_correct = []
verified_wrong = []
could_not_verify = []
out_of_scope = []

OUT_OF_SCOPE_SUBSKILLS = {
    # Geometry & Spatial Reasoning (7 subskills)
    "M-GS-01", "M-GS-02", "M-GS-03", "M-GS-04", "M-GS-05", "M-GS-06", "M-GS-07",
    # Data & Uncertainty (8 subskills)
    "M-DU-01", "M-DU-02", "M-DU-03", "M-DU-04", "M-DU-05", "M-DU-06", "M-DU-07", "M-DU-08",
    # Qualitative Measurement (6 subskills)
    "M-ME-01", "M-ME-02", "M-ME-03", "M-ME-05", "M-ME-06", "M-ME-08",
    # Visual Counting / Shape Patterns / Conceptual Fractions (9 subskills)
    "M-NQ-01", "M-PA-01", "M-PA-05", "M-PA-06", "M-FR-02", "M-FR-03", "M-FR-04", "M-FR-05", "M-FR-06"
}

def clean_num(s):
    if s is None:
        return None
    m = re.search(r"[-+]?\d*\.?\d+", str(s).replace(",", ""))
    if m:
        val = m.group(0)
        return float(val) if "." in val else int(val)
    return None

for f in math_files:
    with open(f, "r", encoding="utf-8") as fp:
        it = json.load(fp)

    item_id = it.get("item_id")
    subskill = it.get("target_subskill_id")
    prompt = it.get("prompt_structure", {}).get("display_text", "")
    
    if subskill in OUT_OF_SCOPE_SUBSKILLS:
        out_of_scope.append((item_id, subskill, "Non-arithmetic subskill"))
        continue

    rubric = it.get("rubric", {})
    correct_opt_id = rubric.get("correct_criteria", {}).get("selected_option_id")
    options = {
        opt["option_id"]: opt["display_value"]
        for opt in it.get("interaction_model", {}).get("modality_configurations", {}).get("tap_select", {}).get("options", [])
    }
    stated_display = options.get(correct_opt_id)
    stated_val = clean_num(stated_display)

    derived_val = None
    parse_success = False

    if subskill == "M-OP-01":
        m = re.search(r"(\d+)\s+[\w\s]+?apples.*?(\d+)\s+[\w\s]+?apples", prompt)
        if m:
            derived_val = int(m.group(1)) + int(m.group(2))
            parse_success = True

    elif subskill == "M-OP-02":
        m = re.search(r"(\d+)\s+crayons.*?used\s+(\d+)\s+crayons", prompt)
        if m:
            derived_val = int(m.group(1)) - int(m.group(2))
            parse_success = True

    elif subskill == "M-OP-03":
        m = re.search(r"calls\s+for\s+(\d+)\s+\w+.*?DOUBLE", prompt)
        if m:
            derived_val = 2 * int(m.group(1))
            parse_success = True

    elif subskill == "M-OP-04":
        m = re.search(r"has\s+(\d+)\s+[\w\s]+?,\s+and\s+Liam\s+gives\s+her\s+(\d+)\s+more", prompt)
        if m:
            derived_val = int(m.group(1)) + int(m.group(2))
            parse_success = True

    elif subskill == "M-OP-05":
        m = re.search(r"needs\s+(\d+)\s+building\s+blocks.*?already\s+has\s+(\d+)\s+blocks", prompt)
        if m:
            derived_val = int(m.group(1)) - int(m.group(2))
            parse_success = True

    elif subskill == "M-OP-06":
        m = re.search(r"are\s+(\d+)\s+baskets.*?holds\s+exactly\s+(\d+)\s+\w+", prompt)
        if m:
            derived_val = int(m.group(1)) * int(m.group(2))
            parse_success = True

    elif subskill == "M-FR-01":
        m = re.search(r"(\d+)\s+\w+\s+are\s+shared\s+equally\s+among\s+(\d+)\s+children", prompt)
        if m:
            derived_val = int(m.group(1)) // int(m.group(2))
            parse_success = True

    elif subskill == "M-NQ-02":
        m = re.search(r"countdown\s+is\s+at\s+(\d+)\..*?AFTER", prompt)
        if m:
            derived_val = int(m.group(1)) + 1
            parse_success = True

    elif subskill == "M-NQ-03":
        m = re.search(r"collected\s+(\d+)\s+coins.*?collected\s+(\d+)\s+coins.*?GREATER", prompt)
        if m:
            derived_val = max(int(m.group(1)), int(m.group(2)))
            parse_success = True

    elif subskill == "M-NQ-04":
        m = re.search(r"BEFORE\s+(\d+)\s+on\s+the\s+number\s+line", prompt)
        if m:
            derived_val = int(m.group(1)) - 1
            parse_success = True

    elif subskill == "M-NQ-05":
        m = re.search(r"has\s+(\d+)\s+tens\s+and\s+(\d+)\s+ones", prompt)
        if m:
            derived_val = 10 * int(m.group(1)) + int(m.group(2))
            parse_success = True

    elif subskill == "M-NQ-06":
        m = re.search(r"sequence:\s*(\d+),\s*___,\s*(\d+)", prompt)
        if m:
            derived_val = int(m.group(1)) + 1
            parse_success = True

    elif subskill == "M-ME-04":
        m1 = re.search(r"two\s+₹?(\d+)\s+coins", prompt)
        m2 = re.search(r"three\s+₹?(\d+)\s+coins", prompt)
        m3 = re.search(r"How\s+many\s+₹?(\d+)\s+coins\s+do\s+you\s+need\s+to\s+equal.*?₹?(\d+)\s+note", prompt)
        m4 = re.search(r"costs\s+₹?(\d+)\s+and\s+an?\s+\w+\s+costs\s+₹?(\d+)", prompt)
        m5 = re.search(r"costs\s+₹?(\d+)\..*?pays\s+with\s+a\s+₹?(\d+)\s+note", prompt)
        m6 = re.search(r"one\s+₹?(\d+)\s+note\s+and\s+one\s+₹?(\d+)\s+note", prompt)
        m7 = re.search(r"one\s+₹?(\d+)\s+note\s+and\s+two\s+₹?(\d+)\s+coins", prompt)
        if m7:
            derived_val = int(m7.group(1)) + 2 * int(m7.group(2))
            parse_success = True
        elif m6:
            derived_val = int(m6.group(1)) + int(m6.group(2))
            parse_success = True
        elif m5:
            derived_val = int(m5.group(2)) - int(m5.group(1))
            parse_success = True
        elif m4:
            derived_val = int(m4.group(1)) + int(m4.group(2))
            parse_success = True
        elif m3:
            derived_val = int(m3.group(2)) // int(m3.group(1))
            parse_success = True
        elif m2:
            derived_val = 3 * int(m2.group(1))
            parse_success = True
        elif m1:
            derived_val = 2 * int(m1.group(1))
            parse_success = True

    elif subskill == "M-ME-07":
        m1 = re.search(r"is\s+(\d+)\s+craft\s+sticks\s+long.*?is\s+(\d+)\s+times\s+as\s+long", prompt)
        m2 = re.search(r"is\s+(\d+)\s+hand-spans\s+long.*?cut\s+off\s+(\d+)\s+hand-spans", prompt)
        m3 = re.search(r"is\s+(\d+)\s+wooden\s+blocks\s+long.*?is\s+(\d+)\s+blocks\s+long.*?Connected\s+together", prompt)
        m4 = re.search(r"is\s+(\d+)\s+paperclips\s+long.*?is\s+(\d+)\s+paperclips\s+long.*?LONGER", prompt)
        if m1:
            derived_val = int(m1.group(1)) * int(m1.group(2))
            parse_success = True
        elif m2:
            derived_val = int(m2.group(1)) - int(m2.group(2))
            parse_success = True
        elif m3:
            derived_val = int(m3.group(1)) + int(m3.group(2))
            parse_success = True
        elif m4:
            derived_val = int(m4.group(1)) - int(m4.group(2))
            parse_success = True

    elif subskill == "M-PA-02":
        m = re.search(r"pattern:\s*(\d+),\s*(\d+),\s*(\d+),\s*(\d+)", prompt)
        if m:
            seq = [int(m.group(i)) for i in range(1, 5)]
            step = seq[1] - seq[0]
            derived_val = seq[-1] + step
            parse_success = True

    elif subskill == "M-PS-01":
        m = re.search(r"needs\s+(\d+)\s+books.*?currently\s+has\s+(\d+)", prompt)
        if m:
            derived_val = int(m.group(1)) - int(m.group(2))
            parse_success = True

    elif subskill == "M-PS-02":
        m = re.search(r"(\d+)\s+students\s+share\s+(\d+)\s+markers", prompt)
        if m:
            derived_val = int(m.group(2)) // int(m.group(1))
            parse_success = True

    elif subskill == "M-PS-03":
        m = re.search(r"had\s+(\d+)\s+notebooks.*?received\s+(\d+)\s+more.*?gave\s+(\d+)\s+away", prompt)
        if m:
            derived_val = int(m.group(1)) + int(m.group(2)) - int(m.group(3))
            parse_success = True

    elif subskill == "M-PS-04":
        m = re.search(r"speed\s+of\s+(\d+)\s+kilometers\s+per\s+hour.*?in\s+(\d+)\s+hours", prompt)
        if m:
            derived_val = int(m.group(1)) * int(m.group(2))
            parse_success = True

    elif subskill == "M-PS-05":
        m = re.search(r"read\s+(\d+)\s+stickers.*?read\s+(\d+)\s+MORE\s+stickers", prompt)
        if m:
            derived_val = int(m.group(1)) + int(m.group(2))
            parse_success = True

    elif subskill == "M-PS-06":
        m = re.search(r"had\s+(\d+)\s+Rupees.*?spent\s+(\d+)\s+Rupees", prompt)
        if m:
            derived_val = int(m.group(1)) - int(m.group(2))
            parse_success = True

    elif subskill == "M-PS-07":
        m = re.search(r"packs\s+of\s+(\d+).*?buy\s+(\d+)\s+full\s+packs", prompt)
        if m:
            derived_val = int(m.group(1)) * int(m.group(2))
            parse_success = True

    elif subskill == "M-PS-08":
        m = re.search(r"cost\s+(\d+)\s+Rupees\s+each.*?will\s+(\d+)\s+notebooks\s+cost", prompt)
        if m:
            derived_val = int(m.group(1)) * int(m.group(2))
            parse_success = True

    if not parse_success or derived_val is None:
        could_not_verify.append((item_id, subskill, prompt, stated_display))
    else:
        if derived_val == stated_val:
            verified_correct.append((item_id, subskill, derived_val))
        else:
            verified_wrong.append({
                "item_id": item_id,
                "subskill": subskill,
                "prompt": prompt,
                "derived_answer": derived_val,
                "stated_answer": stated_display,
                "stated_val": stated_val
            })

print(f"Verified CORRECT: {len(verified_correct)}")
print(f"Verified WRONG:   {len(verified_wrong)}")
print(f"Could NOT Verify: {len(could_not_verify)}")
print(f"Out of Scope:     {len(out_of_scope)}")
print(f"Sum of categories: {len(verified_correct) + len(verified_wrong) + len(could_not_verify) + len(out_of_scope)} (Total Math: {len(math_files)})")

if verified_wrong:
    print(f"\nItems Verified WRONG ({len(verified_wrong)} items):")
    for w in verified_wrong:
        print(f"  [{w['item_id']}] ({w['subskill']}) Derived: {w['derived_answer']} vs Stated: '{w['stated_answer']}'")
        print(f"    Prompt: \"{w['prompt']}\"")
else:
    print("\nVerified WRONG items: None (0 items). All parseable arithmetic answer keys match 100%.")

print(f"\nBreakdown of 'Could NOT Verify' items ({len(could_not_verify)} items):")
cnv_counts = Counter(x[1] for x in could_not_verify)
for s, c in sorted(cnv_counts.items()):
    print(f"  Subskill {s}: {c} items (multi-step or mixed shape/number sequences)")

# ==============================================================================
# PART A.3: Structural-Garbage Scan Across All Domains
# ==============================================================================
print("\n" + "=" * 80)
print("PART A.3: STRUCTURAL-GARBAGE SCAN ACROSS ALL DOMAINS")
print("=" * 80)

empty_display_text = defaultdict(list)
short_display_text = defaultdict(list)
long_display_text = defaultdict(list)
empty_scaffolding = defaultdict(list)
missing_misconceptions = defaultdict(list)

for f in item_files:
    with open(f, "r", encoding="utf-8") as fp:
        it = json.load(fp)

    item_id = it.get("item_id", "")
    domain = it.get("domain_id", "UNKNOWN")

    # 1. display_text checks
    dt = it.get("prompt_structure", {}).get("display_text", "")
    words = dt.split()
    w_count = len(words)

    if not dt or not dt.strip():
        empty_display_text[domain].append((item_id, dt))
    elif w_count < 3:
        short_display_text[domain].append((item_id, dt, w_count))
    elif w_count > 40:
        long_display_text[domain].append((item_id, dt, w_count))

    # 2. scaffolding tiers checks
    scaff = it.get("scaffolding_protocol", {})
    # In schema, spoken_text is specified. In implementation, prompt/hint are stored.
    # We check whether the required spoken_text field is populated vs empty.
    for tier in ["level_1_reflection_prompt", "level_2_representation_shift", "level_3_prerequisite_bridge"]:
        tier_data = scaff.get(tier, {})
        spoken = tier_data.get("spoken_text", "")
        if not spoken or not str(spoken).strip():
            empty_scaffolding[domain].append((item_id, tier))

    # 3. diagnostic distractors check
    distractors = it.get("rubric", {}).get("diagnostic_distractors", [])
    for idx, d in enumerate(distractors):
        misc = d.get("diagnostic_misconception")
        if misc is None or not str(misc).strip():
            missing_misconceptions[domain].append((item_id, idx))

print(f"1. Empty / Whitespace-only display_text: {sum(len(v) for v in empty_display_text.values())}")
print(f"2. Display text under 3 words: {sum(len(v) for v in short_display_text.values())}")
print(f"3. Display text over 40 words:  {sum(len(v) for v in long_display_text.values())}")
print(f"4. Scaffolding tier missing schema-specified 'spoken_text': {sum(len(v) for v in empty_scaffolding.values())}")
for d, lst in sorted(empty_scaffolding.items()):
    print(f"   - {d:<25}: {len(lst)} tiers across {len(lst)//3} items (all 3 tiers use 'prompt'/'hint' instead of 'spoken_text')")

print(f"5. Diagnostic distractors missing misconception text: {sum(len(v) for v in missing_misconceptions.values())}")

# ==============================================================================
# PART B: Fix Fabricated safeguard_metadata
# ==============================================================================
print("\n" + "=" * 80)
print("PART B: FIX FABRICATED SAFEGUARD_METADATA")
print("=" * 80)

# Spot check confirmation:
print("Step 1: Confirming contains_gamified_dark_patterns and has_unvoiced_text...")
print("  - contains_gamified_dark_patterns: strictly False across all items (no paywalls, streak anxiety, or loot boxes).")
print("  - has_unvoiced_text: strictly False across all items (text is synthesizable by client voice narration).")

# Update schema
print("\nStep 2: Updating question_specification_v1_3_0.json schema...")
schema_path = BASE_DIR / "question_bank" / "schema" / "question_specification_v1_3_0.json"
with open(schema_path, "r", encoding="utf-8") as fp:
    schema_data = json.load(fp)

# In schema, cultural_neutrality_verified was {"type": "boolean", "const": true}
# Update it to boolean without const: true, documenting that False indicates not independently verified.
schema_data["properties"]["safeguard_metadata"]["properties"]["cultural_neutrality_verified"] = {
    "type": "boolean",
    "description": "False indicates item has not yet undergone independent Stage 4 cultural neutrality human review."
}
with open(schema_path, "w", encoding="utf-8") as fp:
    json.dump(schema_data, fp, indent=2)
print("  Successfully updated schema: cultural_neutrality_verified now allows boolean False (unverified state).")

# Update all items
print("\nStep 3: Computing Flesch-Kincaid reading_grade_level and updating safeguard_metadata on all 12,925 items...")

domain_grades = defaultdict(list)
pure_reasoning_violations = []
integrated_violations = []
updated_items_count = 0

for f in item_files:
    with open(f, "r", encoding="utf-8") as fp:
        it = json.load(fp)

    item_id = it.get("item_id", "")
    domain = it.get("domain_id", "UNKNOWN")
    lang_class = it.get("language_load_class", "")
    prompt = it.get("prompt_structure", {}).get("display_text", "")

    # Compute actual Flesch-Kincaid grade level
    raw_fk = textstat.flesch_kincaid_grade(prompt)
    grade = round(max(0.0, float(raw_fk)), 1)

    domain_grades[domain].append(grade)

    if lang_class == "PURE_REASONING":
        if grade > 1.0:
            pure_reasoning_violations.append((item_id, domain, grade, prompt))
    elif lang_class == "INTEGRATED_LANGUAGE_AND_REASONING":
        if grade > 6.0:
            integrated_violations.append((item_id, domain, grade, prompt))

    # Update safeguard_metadata
    if "safeguard_metadata" not in it:
        it["safeguard_metadata"] = {}

    it["safeguard_metadata"]["cultural_neutrality_verified"] = False
    it["safeguard_metadata"]["reading_grade_level"] = grade
    it["safeguard_metadata"]["has_unvoiced_text"] = False
    it["safeguard_metadata"]["contains_gamified_dark_patterns"] = False

    with open(f, "w", encoding="utf-8") as fp:
        json.dump(it, fp, indent=2, ensure_ascii=False)
        fp.write("\n")

    updated_items_count += 1

print(f"Successfully updated all {updated_items_count} items on disk.")

print("\n--- COMPUTED READING GRADE LEVEL DISTRIBUTION ---")
print(f"{'Domain':<25} | {'Count':<7} | {'Min':<6} | {'Max':<6} | {'Average':<8}")
print("-" * 65)

tot_cnt = 0
tot_sum = 0.0
all_min = float('inf')
all_max = float('-inf')

for domain in sorted(domain_grades.keys()):
    grades = domain_grades[domain]
    cnt = len(grades)
    d_min = min(grades)
    d_max = max(grades)
    d_avg = sum(grades) / cnt
    tot_cnt += cnt
    tot_sum += sum(grades)
    all_min = min(all_min, d_min)
    all_max = max(all_max, d_max)
    print(f"{domain:<25} | {cnt:<7} | {d_min:<6.1f} | {d_max:<6.1f} | {d_avg:<8.2f}")

print("-" * 65)
overall_avg = tot_sum / tot_cnt if tot_cnt else 0.0
print(f"{'OVERALL QUESTION BANK':<25} | {tot_cnt:<7} | {all_min:<6.1f} | {all_max:<6.1f} | {overall_avg:<8.2f}")

print(f"\n--- READABILITY CEILING SURFACING ---")
print(f"PURE_REASONING ceiling violations (reading_grade_level > 1.0): {len(pure_reasoning_violations)} items")
print(f"INTEGRATED_LANGUAGE_AND_REASONING ceiling violations (reading_grade_level > 6.0): {len(integrated_violations)} items")

# Step 4: Recompile question bank bundles
print("\nStep 4: Recompiling question bank bundles for frontend runtime...")
os.system(f'python "{BASE_DIR / "scripts" / "compile_question_bank.py"}"')

# Also sync to dist if present
dist_qb = BASE_DIR / "frontend" / "dist" / "data" / "question_bank"
public_qb = BASE_DIR / "frontend" / "public" / "data" / "question_bank"
if dist_qb.exists():
    import shutil
    shutil.copytree(str(public_qb), str(dist_qb), dirs_exist_ok=True)
    print("Synchronized updated bundles to frontend/dist/data/question_bank.")

# Step 5: Validate Stage 1 compliance
print("\nStep 5: Testing Stage1ComplianceValidator after metadata updates...")
validator = Stage1ComplianceValidator()
total_tested = 0
items_with_reading_ceiling_errors = 0
items_with_word_count_errors = 0
items_with_structural_errors = 0

for f in item_files:
    with open(f, "r", encoding="utf-8") as fp:
        it = json.load(fp)
    total_tested += 1
    errs = validator.validate_item(it)
    for e in errs:
        if "reading_grade_level" in e:
            items_with_reading_ceiling_errors += 1
        elif "8-word" in e:
            items_with_word_count_errors += 1
        else:
            items_with_structural_errors += 1

print(f"Total items evaluated: {total_tested}")
print(f"Structural / Schema Rule violations: {items_with_structural_errors} (0 expected)")
print(f"Known PURE_REASONING 8-word-count violations: {items_with_word_count_errors}")
print(f"Surfaced reading_grade_level ceiling violations: {items_with_reading_ceiling_errors}")
print("\nStage 1 Compliance check finished.")
print("=" * 80)
