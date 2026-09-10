import glob
import re
import os

print("Starting SVG patch...")
count = 0
for folder in ['frontend/public/assets/svg', 'frontend/dist/assets/svg']:
    for f in glob.glob(folder + '/*.svg'):
        with open(f, 'r', encoding='utf-8') as file:
            content = file.read()
        
        # Remove width="100%" height="100%" to prevent flex collapse
        new_content = re.sub(r'\s+width=[\"\']100%[\"\']\s+height=[\"\']100%[\"\']', '', content)
        
        if new_content != content:
            with open(f, 'w', encoding='utf-8') as file:
                file.write(new_content)
            count += 1

print(f'Fixed SVG intrinsic heights in {count} files!')
