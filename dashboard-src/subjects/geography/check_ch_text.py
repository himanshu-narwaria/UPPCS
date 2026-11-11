import json

with open("dashboard-src/subjects/geography/accurate_chapter_ranges.json", encoding="utf-8") as f:
    ranges = json.load(f)

with open("dashboard-src/subjects/geography/raw_pages.json", encoding="utf-8") as f:
    pages = json.load(f)

for r in ranges[:31]:
    num = r["num"]
    title = r["title"]
    p_start = r["pdf_start"]
    p_end = r["pdf_end"]
    # Check text length
    ch_text = "\n".join(pages[p-1]["text"] for p in range(p_start, min(p_end + 1, len(pages))))
    print(f"Ch {num:2d}: {title:35s} | Pages {p_start:3d}-{p_end:3d} (len {len(ch_text):6d})")
