import glob
import re

files = glob.glob('frontend/public/assets/svg/*.svg')
print(f"Total SVGs: {len(files)}")

white_on_white_count = 0
sample_invisible = []

for f in files:
    with open(f, 'r', encoding='utf-8') as fp:
        content = fp.read()
    
    fills = re.findall(r'fill=["\']([^"\']+)["\']', content)
    strokes = re.findall(r'stroke=["\']([^"\']+)["\']', content)
    
    unique_colors = set(fills + strokes)
    non_bg_colors = [c for c in unique_colors if c.lower() not in ['#f8fafc', '#fff', '#ffffff', 'none', 'transparent']]
    
    if len(non_bg_colors) == 0:
        white_on_white_count += 1
        if len(sample_invisible) < 10:
            sample_invisible.append((f, content))

print(f"Completely white/invisible SVGs: {white_on_white_count}")
for s in sample_invisible[:5]:
    print('---', s[0])
    print(s[1])
