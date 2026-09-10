import json, glob
from collections import defaultdict
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent.parent
QB_DIR = BASE / 'frontend' / 'public' / 'data' / 'question_bank'

prompts = defaultdict(list)
domains = ['MATHEMATICS', 'ENGLISH_LANGUAGE', 'SCIENCE_EVS', 'LOGICAL_REASONING', 'WORLD_KNOWLEDGE']

total = 0
for dom in domains:
    p = QB_DIR / f'items_{dom}.json'
    if p.exists():
        with open(p, 'r', encoding='utf-8') as f:
            items = json.load(f)
            total += len(items)
            for it in items:
                text = it.get('prompt_structure', {}).get('display_text', '').strip()
                prompts[text].append(it.get('item_id'))

duplicates = {k: v for k, v in prompts.items() if len(v) > 1}
print(f'Total items: {total}')
print(f'Total unique prompts: {len(prompts)}')
print(f'Prompts with duplicate text across multiple items: {len(duplicates)}')
for i, (k, v) in enumerate(sorted(duplicates.items(), key=lambda x: len(x[1]), reverse=True)[:25]):
    print(f'{i+1}. "{k}" ({len(v)} items): {v[:4]}')
