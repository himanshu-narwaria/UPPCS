import json
import re

with open("dashboard-src/subjects/geography/raw_pages.json", encoding="utf-8") as f:
    pages = json.load(f)

page_map = []
for p in pages:
    txt = p["text"]
    # Look for CA or CB in first 100 chars
    m = re.search(r'\b(CA|CB)[\s–-]+(\d+)\b', txt[:150], re.IGNORECASE)
    printed = f"{m.group(1).upper()}-{int(m.group(2))}" if m else None
    page_map.append({
        "pdf_page": p["pdf_page"],
        "printed": printed,
        "sample": txt[:80].replace("\n", " ")
    })

# Check coverage
found_printed = [x for x in page_map if x["printed"]]
print(f"Total PDF pages: {len(page_map)}")
print(f"Pages with detected printed number: {len(found_printed)}")

# Sample missing ones
missing = [x for x in page_map if not x["printed"]]
print(f"Pages missing printed number: {len(missing)}")
for m in missing[:10]:
    print(f"PDF {m['pdf_page']}: {m['sample']}")
