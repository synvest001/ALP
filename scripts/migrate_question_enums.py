import glob
import json
import os
import subprocess
import sys
from collections import defaultdict

def main():
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    items_glob = os.path.join(root_dir, "question_bank", "items", "**", "*.json")
    files = glob.glob(items_glob, recursive=True)

    print("=" * 80)
    print(f"QUESTION BANK ENUM MIGRATION: {len(files):,} raw files found")
    print("=" * 80)

    mod_challenge_type = 0
    mod_creation_stage = 0
    mod_language_load = 0
    files_modified = 0

    creation_stage_distribution = defaultdict(int)
    challenge_type_distribution = defaultdict(int)
    language_load_distribution = defaultdict(int)

    for fpath in files:
        with open(fpath, "r", encoding="utf-8") as f:
            item = json.load(f)

        dirty = False

        # 1. challenge_type: "MULTIPLE_CHOICE" -> "STANDARD"
        if item.get("challenge_type") == "MULTIPLE_CHOICE":
            item["challenge_type"] = "STANDARD"
            mod_challenge_type += 1
            dirty = True

        # 2. creation_stage: "DRAFT" -> "ANSWERING"
        if item.get("creation_stage") in ("DRAFT", "NONE", None):
            item["creation_stage"] = "ANSWERING"
            mod_creation_stage += 1
            dirty = True

        # 3. language_load_class: "MINIMAL_INSTRUCTIONAL" -> "INTEGRATED_LANGUAGE_AND_REASONING"
        if item.get("language_load_class") == "MINIMAL_INSTRUCTIONAL":
            item["language_load_class"] = "INTEGRATED_LANGUAGE_AND_REASONING"
            mod_language_load += 1
            dirty = True

        creation_stage_distribution[item.get("creation_stage")] += 1
        challenge_type_distribution[item.get("challenge_type")] += 1
        language_load_distribution[item.get("language_load_class")] += 1

        if dirty:
            files_modified += 1
            with open(fpath, "w", encoding="utf-8") as f:
                json.dump(item, f, indent=2)
                f.write("\n")

    print("\nMIGRATION SUMMARY:")
    print(f"  - Total files scanned:                       {len(files):,}")
    print(f"  - Files updated and saved:                   {files_modified:,}")
    print(f"  - challenge_type -> 'STANDARD' updates:      {mod_challenge_type:,}")
    print(f"  - creation_stage -> 'ANSWERING' updates:     {mod_creation_stage:,}")
    print(f"  - language_load_class -> INTEGRATED updates: {mod_language_load:,}")

    print("\nPOST-MIGRATION ENUM VERIFICATION (Raw Question Bank):")
    print(f"  creation_stage distribution:")
    for k, v in sorted(creation_stage_distribution.items()):
        pct = (v / len(files)) * 100
        print(f"    - {repr(k)}: {v:,} ({pct:.1f}%)")

    print(f"  challenge_type distribution:")
    for k, v in sorted(challenge_type_distribution.items()):
        pct = (v / len(files)) * 100
        print(f"    - {repr(k)}: {v:,} ({pct:.1f}%)")

    print(f"  language_load_class distribution:")
    for k, v in sorted(language_load_distribution.items()):
        pct = (v / len(files)) * 100
        print(f"    - {repr(k)}: {v:,} ({pct:.1f}%)")

    print("\n" + "-" * 80)
    print("NOTE: EXPLAINING/MODIFYING/GENERATING/CREATING have zero items and are a content-authoring gap, not something this script can fix.")
    print("-" * 80)

    # Recompile question bank for frontend
    print("\nRecompiling question bank bundles for frontend...")
    compile_script = os.path.join(root_dir, "scripts", "compile_question_bank.py")
    subprocess.run([sys.executable, compile_script], check=True)

    # Re-run validation script
    print("\nRunning validation script to verify 100% schema enum compliance...")
    validate_script = os.path.join(root_dir, "scripts", "validate_question_enums.py")
    subprocess.run([sys.executable, validate_script], check=True)

if __name__ == "__main__":
    main()
