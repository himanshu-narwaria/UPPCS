import json

with open("dashboard-src/subjects/geography/raw_pages.json", encoding="utf-8") as f:
    pages = json.load(f)

with open("dashboard-src/subjects/geography/accurate_chapter_ranges.json", encoding="utf-8") as f:
    ranges = json.load(f)

for ch_idx in [28, 30, 79, 82]:
    c = ranges[ch_idx]
    print(f"=== Ch {c['num']}: {c['title']} (PDF P.{c['pdf_start']}) ===")
    txt = pages[c['pdf_start'] - 1]['text'][:400]
    for line in txt.split("\n")[:10]:
        print("  ", line)
