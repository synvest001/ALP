import json
import os
from pathlib import Path

BASE_DIR = Path(r"c:\Users\Asus\ALP")
QUESTION_BANK_DIR = BASE_DIR / "question_bank" / "items"
PUBLIC_SVG_DIR = BASE_DIR / "frontend" / "public" / "assets" / "svg"
DIST_SVG_DIR = BASE_DIR / "frontend" / "dist" / "assets" / "svg"

GEMS_SVG = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 200" width="100%" height="100%">
  <rect width="400" height="200" rx="16" fill="#f8fafc"/>
  <!-- Left group (6 gems) -->
  <g transform="translate(40, 30)">
    <rect width="140" height="140" rx="12" fill="#ecfeff" stroke="#14b8a6" stroke-width="3" stroke-dasharray="8,4"/>
    <g fill="#0ea5e9" stroke="#0284c7" stroke-width="2">
      <!-- Top Row -->
      <polygon points="40,25 55,40 40,55 25,40" />
      <polygon points="70,25 85,40 70,55 55,40" />
      <polygon points="100,25 115,40 100,55 85,40" />
      <!-- Bottom Row -->
      <polygon points="40,85 55,100 40,115 25,100" />
      <polygon points="70,85 85,100 70,115 55,100" />
      <polygon points="100,85 115,100 100,115 85,100" />
    </g>
  </g>
  <!-- Right group (2 gems) -->
  <g transform="translate(220, 30)">
    <rect width="140" height="140" rx="12" fill="#fff1f2" stroke="#f43f5e" stroke-width="3" stroke-dasharray="8,4"/>
    <g fill="#ec4899" stroke="#be185d" stroke-width="2">
      <polygon points="50,60 70,80 50,100 30,80" />
      <polygon points="90,60 110,80 90,100 70,80" />
    </g>
  </g>
</svg>'''

count = 0
for root, _, files in os.walk(QUESTION_BANK_DIR):
    for file in files:
        if file.endswith(".json"):
            filepath = Path(root) / file
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    item = json.load(f)
                display_text = item.get("prompt_structure", {}).get("display_text", "").lower()
                if "gems" in display_text and "more jewels" in display_text:
                    # Overwrite SVG
                    item_id = item.get("item_id", "").lower()
                    if item_id:
                        svg_filename = f"{item_id}_visual.svg"
                        for target_dir in [PUBLIC_SVG_DIR, DIST_SVG_DIR]:
                            target_path = target_dir / svg_filename
                            if target_path.exists():
                                with open(target_path, "w", encoding="utf-8") as svg_file:
                                    svg_file.write(GEMS_SVG)
                        count += 1
            except Exception as e:
                print(f"Error on {file}: {e}")

print(f"Fixed {count} gems SVGs.")
