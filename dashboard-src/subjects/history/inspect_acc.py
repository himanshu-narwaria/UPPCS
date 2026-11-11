import json

with open("dashboard-src/subjects/history/accurate_ranges.json", encoding="utf-8") as f:
    acc = json.load(f)

for item in acc:
    if 41 <= item["num"] <= 95:
        print(f"Ch {item['num']:2d}: {item['title'][:40]:40} | start: {item['start']} | nom: {item['nominal_start']} - {item['nominal_end']}")
