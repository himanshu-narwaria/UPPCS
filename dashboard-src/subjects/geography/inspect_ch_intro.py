import json
import re

with open("dashboard-src/subjects/geography/accurate_chapter_ranges.json", encoding="utf-8") as f:
    ranges = json.load(f)

with open("dashboard-src/subjects/geography/raw_pages.json", encoding="utf-8") as f:
    pages = json.load(f)

for r in ranges[:10]:
    num = r["num"]
    title = r["title"]
    p_start = r["pdf_start"]
    text = pages[p_start - 1]["text"]
    # Look for bullet points or sections
    print(f"=== Ch {num}: {title} (Page {p_start}) ===")
    lines = [l.strip() for l in text.split("\n") if l.strip()]
    for l in lines[:15]:
        print("  ", l[:90])
