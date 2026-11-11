import json

with open("dashboard-src/subjects/history/raw_pages.json", encoding="utf-8") as f:
    pages = json.load(f)

for p in range(523, 528):
    print(f"=== PAGE {p} ===")
    lines = [l.strip() for l in pages[p-1]["text"].split("\n") if l.strip()]
    for l in lines[:8]:
        print(" ", l)
