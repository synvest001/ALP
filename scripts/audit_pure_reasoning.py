import glob
import json
import os
from collections import defaultdict

def audit_pure_reasoning():
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    files = glob.glob(os.path.join(root_dir, "question_bank", "items", "**", "*.json"), recursive=True)

    domain_total = defaultdict(int)
    domain_over_8 = defaultdict(int)
    domain_empty_audio = defaultdict(int)
    word_count_examples = defaultdict(list)

    for f in files:
        with open(f, "r", encoding="utf-8") as fp:
            d = json.load(fp)
        if d.get("language_load_class") == "PURE_REASONING":
            dom = d.get("domain_id", "UNKNOWN")
            domain_total[dom] += 1
            ps = d.get("prompt_structure", {})
            text = ps.get("display_text", "").strip()
            words = text.split()
            if len(words) > 8:
                domain_over_8[dom] += 1
                if len(word_count_examples[dom]) < 3:
                    word_count_examples[dom].append((d.get("item_id"), len(words), text))
            audio = ps.get("spoken_audio_uri", "")
            if not audio or not audio.strip():
                domain_empty_audio[dom] += 1

    total_pure = sum(domain_total.values())
    total_over_8 = sum(domain_over_8.values())
    total_empty_audio = sum(domain_empty_audio.values())

    print("=" * 80)
    print("PURE_REASONING CONSTRUCT-LOAD AUDIT REPORT")
    print("=" * 80)
    print(f"Total PURE_REASONING items across question bank: {total_pure:,}")
    print(f"Exceeding 8-word display text ceiling:           {total_over_8:,} / {total_pure:,} ({(total_over_8/total_pure*100):.1f}%)")
    print(f"Empty or whitespace-only spoken_audio_uri:       {total_empty_audio:,} / {total_pure:,} ({(total_empty_audio/total_pure*100):.1f}%)")
    print("=" * 80)

    for dom in sorted(domain_total.keys()):
        tot = domain_total[dom]
        o8 = domain_over_8[dom]
        ea = domain_empty_audio[dom]
        pct = (o8 / tot * 100) if tot else 0.0
        print(f"\n[DOMAIN] {dom}")
        print(f"  Total PURE_REASONING items:       {tot:,}")
        print(f"  Exceeding 8 words in prompt text: {o8:,} ({pct:.1f}%)")
        print(f"  Empty/whitespace audio URI:       {ea:,} ({(ea/tot*100):.1f}%)")
        print("  Sample items exceeding 8 words:")
        for iid, wc, sample in word_count_examples[dom]:
            print(f"    - {iid} ({wc} words): \"{sample}\"")
    print("=" * 80)

if __name__ == "__main__":
    audit_pure_reasoning()
