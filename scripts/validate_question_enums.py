import os
import glob
import json
from collections import defaultdict
from typing import Dict, List, Set, Any

SCHEMA_PATH = os.path.join(os.path.dirname(__file__), "..", "question_bank", "schema", "question_specification_v1_3_0.json")

def load_documented_enums(schema_path: str) -> Dict[str, Set[str]]:
    with open(schema_path, "r", encoding="utf-8") as f:
        schema = json.load(f)

    props = schema.get("properties", {})
    enums: Dict[str, Set[str]] = {}

    # Top-level fields
    for field in [
        "domain_id",
        "evidence_archetype",
        "cognitive_depth",
        "transfer_level",
        "primary_modality",
        "language_load_class",
        "representation_type",
        "challenge_type",
        "creation_stage",
    ]:
        if field in props and "enum" in props[field]:
            enums[field] = set(props[field]["enum"])

    # Array of strings
    if "supported_alternative_modalities" in props:
        items_schema = props["supported_alternative_modalities"].get("items", {})
        if "enum" in items_schema:
            enums["supported_alternative_modalities"] = set(items_schema["enum"])

    # Nested fields
    if "interaction_model" in props:
        im_props = props["interaction_model"].get("properties", {})
        if "input_mechanic" in im_props and "enum" in im_props["input_mechanic"]:
            enums["interaction_model.input_mechanic"] = set(im_props["input_mechanic"]["enum"])

    if "prompt_structure" in props:
        va_items = props["prompt_structure"].get("properties", {}).get("visual_assets", {}).get("items", {})
        va_props = va_items.get("properties", {})
        if "asset_type" in va_props and "enum" in va_props["asset_type"]:
            enums["prompt_structure.visual_assets[].asset_type"] = set(va_props["asset_type"]["enum"])

    if "scaffolding_protocol" in props:
        sp_props = props["scaffolding_protocol"].get("properties", {})
        l2_props = sp_props.get("level_2_representation_shift", {}).get("properties", {})
        if "target_representation" in l2_props and "enum" in l2_props["target_representation"]:
            enums["scaffolding_protocol.level_2_representation_shift.target_representation"] = set(l2_props["target_representation"]["enum"])

    if "rubric" in props:
        r_props = props["rubric"].get("properties", {})
        if "evaluation_mode" in r_props and "enum" in r_props["evaluation_mode"]:
            enums["rubric.evaluation_mode"] = set(r_props["evaluation_mode"]["enum"])
        dd_items = r_props.get("diagnostic_distractors", {}).get("items", {})
        dd_props = dd_items.get("properties", {})
        if "recommended_ws3_branch" in dd_props and "enum" in dd_props["recommended_ws3_branch"]:
            enums["rubric.diagnostic_distractors[].recommended_ws3_branch"] = set(dd_props["recommended_ws3_branch"]["enum"])

    return enums

def validate_item_enums(item: Dict[str, Any], item_id: str, enums: Dict[str, Set[str]], source_tag: str, violations: Dict[str, Dict[Any, List[str]]]):
    # Check top-level enums
    for field in [
        "domain_id",
        "evidence_archetype",
        "cognitive_depth",
        "transfer_level",
        "primary_modality",
        "language_load_class",
        "representation_type",
        "challenge_type",
        "creation_stage",
    ]:
        val = item.get(field)
        if val is None or val not in enums[field]:
            violations[f"{source_tag} -> {field}"][val].append(item_id)

    # Check supported_alternative_modalities (list)
    mods = item.get("supported_alternative_modalities")
    if not isinstance(mods, list):
        violations[f"{source_tag} -> supported_alternative_modalities"][str(type(mods))].append(item_id)
    else:
        for m in mods:
            if m not in enums["supported_alternative_modalities"]:
                violations[f"{source_tag} -> supported_alternative_modalities[]"][m].append(item_id)

    # Check interaction_model.input_mechanic
    im = item.get("interaction_model")
    if isinstance(im, dict):
        mech = im.get("input_mechanic")
        if mech is not None and mech not in enums["interaction_model.input_mechanic"]:
            violations[f"{source_tag} -> interaction_model.input_mechanic"][mech].append(item_id)

    # Check prompt_structure.visual_assets[].asset_type
    ps = item.get("prompt_structure")
    if isinstance(ps, dict):
        assets = ps.get("visual_assets")
        if isinstance(assets, list):
            for a in assets:
                if isinstance(a, dict):
                    atype = a.get("asset_type")
                    if atype is not None and atype not in enums["prompt_structure.visual_assets[].asset_type"]:
                        violations[f"{source_tag} -> prompt_structure.visual_assets[].asset_type"][atype].append(item_id)

    # Check scaffolding_protocol target_representation
    sp = item.get("scaffolding_protocol")
    if isinstance(sp, dict):
        l2 = sp.get("level_2_representation_shift")
        if isinstance(l2, dict):
            tr = l2.get("target_representation")
            if tr is not None and tr not in enums["scaffolding_protocol.level_2_representation_shift.target_representation"]:
                violations[f"{source_tag} -> scaffolding_protocol.level_2_representation_shift.target_representation"][tr].append(item_id)

    # Check rubric.evaluation_mode
    rubric = item.get("rubric")
    if isinstance(rubric, dict):
        em = rubric.get("evaluation_mode")
        if em is not None and em not in enums["rubric.evaluation_mode"]:
            violations[f"{source_tag} -> rubric.evaluation_mode"][em].append(item_id)
        dd = rubric.get("diagnostic_distractors")
        if isinstance(dd, list):
            for d in dd:
                if isinstance(d, dict):
                    branch = d.get("recommended_ws3_branch")
                    if branch is not None and branch not in enums["rubric.diagnostic_distractors[].recommended_ws3_branch"]:
                        violations[f"{source_tag} -> rubric.diagnostic_distractors[].recommended_ws3_branch"][branch].append(item_id)

def main():
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    schema_path = os.path.join(root_dir, "question_bank", "schema", "question_specification_v1_3_0.json")

    enums = load_documented_enums(schema_path)

    # Violations tracking
    # violations[dataset][field][value] = list of item IDs
    raw_violations = defaultdict(lambda: defaultdict(list))
    compiled_violations = defaultdict(lambda: defaultdict(list))
    compiled_omitted = defaultdict(list)

    raw_files = glob.glob(os.path.join(root_dir, "question_bank", "items", "**", "*.json"), recursive=True)
    total_raw_files = len(raw_files)

    # Track domain breakdowns for violations
    raw_domain_counts = defaultdict(int)
    raw_field_domain_map = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))

    for fpath in raw_files:
        try:
            with open(fpath, "r", encoding="utf-8") as f:
                item = json.load(f)
            item_id = item.get("item_id", os.path.basename(fpath))
            domain = item.get("domain_id", "UNKNOWN")
            raw_domain_counts[domain] += 1

            # Check all top-level enums
            for field in [
                "domain_id", "evidence_archetype", "cognitive_depth",
                "transfer_level", "primary_modality", "language_load_class",
                "representation_type", "challenge_type", "creation_stage"
            ]:
                val = item.get(field)
                if val not in enums.get(field, set()):
                    raw_violations[field][val].append(item_id)
                    raw_field_domain_map[field][val][domain] += 1

            # Check array items
            mods = item.get("supported_alternative_modalities")
            if isinstance(mods, list):
                for m in mods:
                    if m not in enums["supported_alternative_modalities"]:
                        raw_violations["supported_alternative_modalities[]"][m].append(item_id)
            else:
                raw_violations["supported_alternative_modalities"][type(mods).__name__].append(item_id)

            # Check nested enums
            im = item.get("interaction_model", {})
            if isinstance(im, dict):
                mech = im.get("input_mechanic")
                if mech and mech not in enums["interaction_model.input_mechanic"]:
                    raw_violations["interaction_model.input_mechanic"][mech].append(item_id)

            ps = item.get("prompt_structure", {})
            if isinstance(ps, dict):
                for va in ps.get("visual_assets", []):
                    if isinstance(va, dict):
                        at = va.get("asset_type")
                        if at and at not in enums["prompt_structure.visual_assets[].asset_type"]:
                            raw_violations["prompt_structure.visual_assets[].asset_type"][at].append(item_id)

            sp = item.get("scaffolding_protocol", {})
            if isinstance(sp, dict):
                l2 = sp.get("level_2_representation_shift", {})
                if isinstance(l2, dict):
                    tr = l2.get("target_representation")
                    if tr and tr not in enums["scaffolding_protocol.level_2_representation_shift.target_representation"]:
                        raw_violations["scaffolding_protocol.level_2_representation_shift.target_representation"][tr].append(item_id)

            rubric = item.get("rubric", {})
            if isinstance(rubric, dict):
                em = rubric.get("evaluation_mode")
                if em and em not in enums["rubric.evaluation_mode"]:
                    raw_violations["rubric.evaluation_mode"][em].append(item_id)
                for dd in rubric.get("diagnostic_distractors", []):
                    if isinstance(dd, dict):
                        b = dd.get("recommended_ws3_branch")
                        if b and b not in enums["rubric.diagnostic_distractors[].recommended_ws3_branch"]:
                            raw_violations["rubric.diagnostic_distractors[].recommended_ws3_branch"][b].append(item_id)

        except Exception as e:
            raw_violations["JSON_PARSE_ERROR"][str(e)].append(fpath)

    # Scan compiled files
    compiled_files = glob.glob(os.path.join(root_dir, "frontend", "public", "data", "question_bank", "items_*.json"))
    total_compiled_items = 0

    for fpath in compiled_files:
        fname = os.path.basename(fpath)
        try:
            with open(fpath, "r", encoding="utf-8") as f:
                items = json.load(f)
            if isinstance(items, list):
                total_compiled_items += len(items)
                for item in items:
                    item_id = item.get("item_id", "UNKNOWN")
                    # Check fields present in compiled format
                    for field in [
                        "domain_id", "evidence_archetype", "cognitive_depth",
                        "transfer_level", "primary_modality", "language_load_class",
                        "representation_type", "challenge_type"
                    ]:
                        if field in item:
                            val = item.get(field)
                            if val not in enums.get(field, set()):
                                compiled_violations[field][val].append(item_id)
                        else:
                            compiled_omitted[field].append(item_id)
        except Exception as e:
            compiled_violations["JSON_PARSE_ERROR"][str(e)].append(fpath)

    # Print Report
    print("=" * 80)
    print("QUESTION BANK SCHEMA ENUM AUDIT REPORT")
    print("=" * 80)
    print(f"Documented Schema Reference: question_bank/schema/question_specification_v1_3_0.json")
    print(f"Total Raw Items Scanned:    {total_raw_files:,} across {len(raw_domain_counts)} domains")
    for dom, count in sorted(raw_domain_counts.items()):
        print(f"  - {dom:<22}: {count:>6,} items")
    print(f"Total Compiled Items:       {total_compiled_items:,} across {len(compiled_files)} bundle files")
    print("=" * 80)

    print("\n" + "#" * 80)
    print("1. RAW QUESTION BANK AUDIT (question_bank/items/**/*.json)")
    print("#" * 80)

    if not raw_violations:
        print("No enum violations found in raw question bank.")
    else:
        for field, val_dict in sorted(raw_violations.items()):
            valid_vals = enums.get(field, set())
            print(f"\n[FIELD] {field}")
            if valid_vals:
                print(f"  Documented Valid Enum Values: {sorted(list(valid_vals))}")
            for val, ids in sorted(val_dict.items(), key=lambda x: len(x[1]), reverse=True):
                pct = (len(ids) / total_raw_files) * 100
                print(f"  -> Offending Value:  {repr(val)}")
                print(f"     Affected Items:   {len(ids):,} / {total_raw_files:,} ({pct:.1f}%)")
                # Domain breakdown
                dom_breakdown = raw_field_domain_map[field][val]
                breakdown_str = ", ".join(f"{d}: {c:,}" for d, c in sorted(dom_breakdown.items()))
                print(f"     Domain Breakdown: {breakdown_str}")
                print(f"     Sample Item IDs:  {', '.join(ids[:5])}")

    print("\n" + "#" * 80)
    print("2. COMPILED CLIENT BUNDLE AUDIT (frontend/public/data/question_bank/items_*.json)")
    print("#" * 80)

    if not compiled_violations:
        print("No enum violations found in compiled bundle items.")
    else:
        for field, val_dict in sorted(compiled_violations.items()):
            valid_vals = enums.get(field, set())
            print(f"\n[FIELD] {field}")
            if valid_vals:
                print(f"  Documented Valid Enum Values: {sorted(list(valid_vals))}")
            for val, ids in sorted(val_dict.items(), key=lambda x: len(x[1]), reverse=True):
                pct = (len(ids) / total_compiled_items) * 100
                print(f"  -> Offending Value:  {repr(val)}")
                print(f"     Affected Items:   {len(ids):,} / {total_compiled_items:,} ({pct:.1f}%)")
                print(f"     Sample Item IDs:  {', '.join(ids[:5])}")

    print("\n" + "=" * 80)
    print("AUDIT COMPLETE - NO AUTOMATED EDITS PERFORMED.")
    print("=" * 80)

if __name__ == "__main__":
    main()
