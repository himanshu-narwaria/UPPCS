import json

with open("dashboard-src/subjects/geography/accurate_chapter_ranges.json", encoding="utf-8") as f:
    ranges = json.load(f)

print(f"Total entries in ranges: {len(ranges)}")
for r in ranges:
    if r["num"] <= 35:
        print(f"Ch {r['num']:2d} | Sec: {r.get('section')} | Pages: {r.get('pdf_start')}-{r.get('pdf_end')} | Title: {r['title']}")
