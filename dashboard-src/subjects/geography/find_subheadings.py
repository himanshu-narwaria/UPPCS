import json
import re

with open("dashboard-src/subjects/geography/accurate_chapter_ranges.json", encoding="utf-8") as f:
    ranges = json.load(f)

with open("dashboard-src/subjects/geography/raw_pages.json", encoding="utf-8") as f:
    pages = json.load(f)

for r in ranges[:31]:
    num = r["num"]
    title = r["title"]
    p_start = r["pdf_start"]
    p_end = r["pdf_end"]
    # Look for chapter title or roman numerals in pages
    found_lines = []
    for p in range(p_start, min(p_end + 1, len(pages))):
        text = pages[p-1]["text"]
        for line in text.split("\n"):
            line_s = line.strip()
            # check for subheadings or roman numerals e.g. "I.", "II.", "i.", "ii.", or "*"
            if re.match(r'^(?:[0-9]{1,2}\.|\([a-z]\)|[I|V|X]+\.|\*[A-Z])', line_s) and len(line_s) < 80:
                found_lines.append(f"p.{p}: {line_s}")
    print(f"=== Ch {num}: {title} ===")
    for fl in found_lines[:8]:
        print("  ", fl)
