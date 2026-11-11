import json

with open("dashboard-src/subjects/history/raw_pages.json", encoding="utf-8") as f:
    pages = json.load(f)

for p in [358, 359]:
    print(f"=== PAGE {p} ===")
    print(pages[p-1]["text"])
