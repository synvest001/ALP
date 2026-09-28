import json

MAP_PATH = "frontend/public/data/curriculum_map.json"

def verify_counts():
    with open(MAP_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    expected = {
        "1": ("Mathematics & Mathematical Thinking", 55),
        "2": ("English Language, Reading & Reasoning", 53),
        "3": ("Science / EVS & Scientific Inquiry", 35),
        "4": ("Logical Reasoning", 24),
        "5": ("World Knowledge & Understanding", 20)
    }

    print("=" * 80)
    print("CURRICULUM MAP SKILL COUNT & PER-DOMAIN BREAKDOWN VERIFICATION")
    print("=" * 80)

    total_skills = 0
    all_matched = True

    for domain in data["domains"]:
        d_id = domain["id"]
        d_title = domain["title"]
        strands = domain["strands"]
        skill_count = sum(len(s.get("skills", [])) for s in strands)
        total_skills += skill_count

        exp_title, exp_count = expected.get(d_id, ("Unknown", -1))
        match = (skill_count == exp_count)
        if not match:
            all_matched = False

        print(f"Domain {d_id} ({d_title}):")
        print(f"  Strands: {len(strands)}")
        print(f"  Skills:  {skill_count} (Expected: {exp_count}) -> {'MATCH' if match else 'MISMATCH'}")

    print("-" * 80)
    print(f"Total Skill Entries: {total_skills} (Expected: 187) -> {'MATCH' if total_skills == 187 else 'MISMATCH'}")
    print(f"Per-Domain Match (55/53/35/24/20): {'CONFIRMED' if all_matched else 'FAILED'}")
    print("=" * 80)

if __name__ == "__main__":
    verify_counts()
