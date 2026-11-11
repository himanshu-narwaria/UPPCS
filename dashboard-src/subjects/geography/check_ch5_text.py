import json

with open("dashboard-src/subjects/geography/raw_pages.json", encoding="utf-8") as f:
    pages = json.load(f)

for p in range(97, 99):
    print(f"--- PAGE {p} ---")
    print(pages[p-1]["text"][:1500])
