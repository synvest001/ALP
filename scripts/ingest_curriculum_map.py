import re
import json
import os

def parse_curriculum_map(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        
    domains = []
    current_domain = None
    current_strand = None
    current_skill = None
    current_section = None
    
    domain_pattern = re.compile(r'^# \d+\.\s+(Domain.*?)\s+—\s+(.*)')
    strand_pattern = re.compile(r'^## (\d+\.\d+)\s+(.*)')
    skill_pattern = re.compile(r'^\*\*(.*?)\s+(.*)\*\*')
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        domain_match = domain_pattern.match(line)
        if domain_match:
            current_domain = {
                "id": domain_match.group(1).replace("Domain ", "").strip(),
                "title": domain_match.group(2).strip(),
                "strands": []
            }
            domains.append(current_domain)
            current_strand = None
            current_skill = None
            continue
            
        strand_match = strand_pattern.match(line)
        if strand_match and current_domain:
            current_strand = {
                "id": strand_match.group(1).strip(),
                "title": strand_match.group(2).strip(),
                "skills": []
            }
            current_domain["strands"].append(current_strand)
            current_skill = None
            continue
            
        skill_match = skill_pattern.match(line)
        if skill_match and current_strand:
            current_skill = {
                "code": skill_match.group(1).strip(),
                "title": skill_match.group(2).strip(),
                "subskills": [],
                "priority": "",
                "progression": [],
                "prerequisites": {
                    "required": [],
                    "strongly_supportive": [],
                    "useful_background": []
                }
            }
            current_strand["skills"].append(current_skill)
            continue
            
        if line.startswith("Subskills:"):
            current_section = "subskills"
            continue
        elif line.startswith("Priority:"):
            current_section = "priority"
            continue
        elif line.startswith("Normal progression:"):
            current_section = "progression"
            continue
        elif line.startswith("Prerequisites:"):
            current_section = "prerequisites"
            continue
            
        if line.startswith("-") and current_skill:
            content = line[1:].strip()
            if current_section == "subskills":
                current_skill["subskills"].append(content)
            elif current_section == "priority":
                current_skill["priority"] = content
            elif current_section == "progression":
                current_skill["progression"] = [p.strip() for p in content.split("→")]
            elif current_section == "prerequisites":
                if content.startswith("Required:"):
                    current_skill["prerequisites"]["required"].append(content.replace("Required:", "").strip())
                elif content.startswith("Strongly Supportive:"):
                    current_skill["prerequisites"]["strongly_supportive"].append(content.replace("Strongly Supportive:", "").strip())
                elif content.startswith("Useful Background:"):
                    current_skill["prerequisites"]["useful_background"].append(content.replace("Useful Background:", "").strip())

    return {"domains": domains}

if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    input_file = os.path.join(base_dir, "Workstreams", "WS1_CURRICULUM_MAP___VERSION_1_0.md")
    output_file = os.path.join(base_dir, "frontend", "public", "data", "curriculum_map.json")
    
    parsed_data = parse_curriculum_map(input_file)
    
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(parsed_data, f, indent=2)
    
    print(f"Successfully generated {output_file}")
