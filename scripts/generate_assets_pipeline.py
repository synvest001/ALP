import os
import json
import glob
from pathlib import Path
from datetime import datetime

# Paths
BASE_DIR = Path(__file__).resolve().parent.parent
ITEMS_DIR = BASE_DIR / "question_bank" / "items"
PUBLIC_DIR = BASE_DIR / "frontend" / "public"
LEDGER_DIR = BASE_DIR / "question_bank" / "ledger"
LEDGER_FILE = LEDGER_DIR / "asset_generation_log.txt"

# Ensure directories exist
LEDGER_DIR.mkdir(parents=True, exist_ok=True)
(PUBLIC_DIR / "art").mkdir(parents=True, exist_ok=True)
(PUBLIC_DIR / "audio").mkdir(parents=True, exist_ok=True)

stats = {
    "items_processed": 0,
    "images_generated": 0,
    "audio_generated": 0,
    "jsons_updated": 0
}

log_lines = []
log_lines.append(f"--- ASSET GENERATION PIPELINE RUN: {datetime.now().isoformat()} ---")

def generate_svg(filepath, text):
    """Generates a highly compressed, solid color placeholder SVG."""
    filepath.parent.mkdir(parents=True, exist_ok=True)
    svg_content = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 300" width="100%" height="100%">
  <rect width="400" height="300" fill="#3498db" rx="15" ry="15"/>
  <text x="50%" y="50%" font-family="sans-serif" font-size="24" fill="white" text-anchor="middle" dominant-baseline="middle">
    {text}
  </text>
  <text x="50%" y="65%" font-family="sans-serif" font-size="14" fill="#ecf0f1" text-anchor="middle" dominant-baseline="middle">
    (Automated Placeholder)
  </text>
</svg>'''
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(svg_content)

def generate_mp3(filepath):
    """Generates a tiny empty/silent file just to satisfy the browser's audio loader."""
    filepath.parent.mkdir(parents=True, exist_ok=True)
    # A few bytes of generic mp3 header/empty frames is enough to not throw a hard 404, 
    # but an empty file is often fine for basic Audio() constructor fallbacks.
    with open(filepath, 'wb') as f:
        f.write(b'\x00' * 128)

def process_dict(d, json_filepath):
    """Recursively search for asset dicts and fix them."""
    modified = False
    
    if isinstance(d, dict):
        if "asset_type" in d and "uri" in d:
            original_uri = d["uri"]
            # Remove leading slash for local path resolution
            relative_path = original_uri.lstrip('/')
            physical_path = PUBLIC_DIR / relative_path
            
            if not physical_path.exists():
                if d["asset_type"] in ["STATIC_IMAGE", "ANIMATION"]:
                    # Change to SVG
                    new_uri = str(Path(original_uri).with_suffix('.svg')).replace('\\', '/')
                    d["uri"] = new_uri
                    
                    new_relative = new_uri.lstrip('/')
                    new_physical_path = PUBLIC_DIR / new_relative
                    
                    if not new_physical_path.exists():
                        asset_id = d.get("asset_id", "Unknown Asset")
                        generate_svg(new_physical_path, asset_id)
                        stats["images_generated"] += 1
                        log_lines.append(f"[GEN:IMAGE] {new_uri} for item {json_filepath.name}")
                    modified = True
                    
                elif d["asset_type"] == "AUDIO":
                    new_uri = str(Path(original_uri).with_suffix('.mp3')).replace('\\', '/')
                    d["uri"] = new_uri
                    
                    new_relative = new_uri.lstrip('/')
                    new_physical_path = PUBLIC_DIR / new_relative
                    
                    if not new_physical_path.exists():
                        generate_mp3(new_physical_path)
                        stats["audio_generated"] += 1
                        log_lines.append(f"[GEN:AUDIO] {new_uri} for item {json_filepath.name}")
                    modified = True

        for k, v in d.items():
            if process_dict(v, json_filepath):
                modified = True
                
    elif isinstance(d, list):
        for item in d:
            if process_dict(item, json_filepath):
                modified = True
                
    return modified

# Find all JSONs
json_files = glob.glob(str(ITEMS_DIR / "**" / "*.json"), recursive=True)

for json_file in json_files:
    json_path = Path(json_file)
    stats["items_processed"] += 1
    
    with open(json_path, 'r', encoding='utf-8') as f:
        try:
            data = json.load(f)
        except Exception as e:
            log_lines.append(f"[ERROR] Failed to parse {json_path.name}: {e}")
            continue
            
    was_modified = process_dict(data, json_path)
    
    if was_modified:
        stats["jsons_updated"] += 1
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)

log_lines.append("--- SUMMARY ---")
log_lines.append(f"Items Processed: {stats['items_processed']}")
log_lines.append(f"Images Generated: {stats['images_generated']}")
log_lines.append(f"Audio Generated: {stats['audio_generated']}")
log_lines.append(f"JSONs Updated: {stats['jsons_updated']}")

# Write to ledger
with open(LEDGER_FILE, 'a', encoding='utf-8') as f:
    f.write("\n".join(log_lines) + "\n\n")

print(f"Pipeline complete! Processed {stats['items_processed']} items.")
print(f"Generated {stats['images_generated']} SVGs and {stats['audio_generated']} MP3s.")
print(f"Ledger updated at {LEDGER_FILE}")
