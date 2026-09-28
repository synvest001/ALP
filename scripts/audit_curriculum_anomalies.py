import json
import re
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

MAP_PATH = Path("frontend/public/data/curriculum_map.json")

def audit_curriculum_map(filepath):
    print("=" * 80)
    print(f"COMPREHENSIVE AUDIT OF CURRICULUM MAP: {filepath}")
    print("=" * 80)

    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)

    CODE_REGEX = re.compile(r"^[MESLW]-[A-Z]{2}-[0-9]{2}$")

    total_domains = len(data.get("domains", []))
    total_strands = 0
    total_skills = 0

    non_matching_codes = []
    empty_subskills = []
    empty_priority = []
    empty_progression = []
    anomalous_strands = []

    for d_idx, domain in enumerate(data.get("domains", [])):
        d_id = domain.get("id")
        d_title = domain.get("title")
        strands = domain.get("strands", [])
        total_strands += len(strands)

        for s_idx, strand in enumerate(strands):
            st_id = strand.get("id", "")
            st_title = strand.get("title", "")
            skills = strand.get("skills", [])
            total_skills += len(skills)

            # Check if strand is anomalous (non-curriculum sections 11.x, 16.x, or empty)
            if st_id.startswith("11.") or st_id.startswith("16.") or len(skills) == 0:
                anomalous_strands.append({
                    "domain_id": d_id,
                    "domain_title": d_title,
                    "strand_id": st_id,
                    "strand_title": st_title,
                    "skill_count": len(skills)
                })

            for sk_idx, skill in enumerate(skills):
                code = skill.get("code", "")
                title = skill.get("title", "")
                subskills = skill.get("subskills", [])
                priority = skill.get("priority", "")
                progression = skill.get("progression", [])

                loc = f"Domain '{d_title}' -> Strand '{st_id} {st_title}' -> Skill [{sk_idx}]"

                if not CODE_REGEX.match(code):
                    non_matching_codes.append({
                        "location": loc,
                        "code": code,
                        "title": title,
                        "subskills_len": len(subskills),
                        "priority": priority,
                        "progression": progression
                    })

                if not subskills:
                    empty_subskills.append({"location": loc, "code": code, "title": title})

                if not priority:
                    empty_priority.append({"location": loc, "code": code, "title": title})

                if not progression:
                    empty_progression.append({"location": loc, "code": code, "title": title})

    print(f"\n[SUMMARY STATS]")
    print(f"  Domains: {total_domains}")
    print(f"  Strands: {total_strands}")
    print(f"  Total Skill Entries in Map: {total_skills}")

    print(f"\n[CHECK 1] Skills with code NOT matching ^[MESLW]-[A-Z]{{2}}-[0-9]{{2}}$:")
    print(f"  Found: {len(non_matching_codes)}")
    for item in non_matching_codes:
        print(f"    - {item['location']}")
        print(f"      code: '{item['code']}', title: '{item['title']}', subskills: {item['subskills_len']}, priority: '{item['priority']}'")

    print(f"\n[CHECK 2] Strands with anomalous numbering (e.g. section numbers):")
    print(f"  Found: {len(anomalous_strands)}")
    for item in anomalous_strands:
        print(f"    - Domain '{item['domain_title']}': Strand '{item['strand_id']} {item['strand_title']}' ({item['skill_count']} skills)")

    print(f"\n[CHECK 3] Skills with empty 'subskills':")
    print(f"  Found: {len(empty_subskills)}")
    for item in empty_subskills:
        print(f"    - [{item['code']}] '{item['title']}' at {item['location']}")

    print(f"\n[CHECK 4] Skills with empty 'priority':")
    print(f"  Found: {len(empty_priority)}")
    for item in empty_priority:
        print(f"    - [{item['code']}] '{item['title']}' at {item['location']}")

    print(f"\n[CHECK 5] Skills with empty 'progression':")
    print(f"  Found: {len(empty_progression)}")
    for item in empty_progression:
        print(f"    - [{item['code']}] '{item['title']}' at {item['location']}")

    print("\n" + "=" * 80)
    print("AUDIT COMPLETE")
    print("=" * 80)

if __name__ == "__main__":
    audit_curriculum_map(MAP_PATH)
