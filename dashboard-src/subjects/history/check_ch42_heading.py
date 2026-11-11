import json, re

with open("dashboard-src/subjects/history/raw_pages.json", encoding="utf-8") as f:
    pages = json.load(f)

for p in range(355, 365):
    text = pages[p-1]["text"]
    if re.search(r'East India Company and|Nawab of Bengal', text, re.I):
        print(f"Found heading on page {p}:")
        for line in text.split('\n')[:15]:
            print("  ", line)
