import json

with open("dashboard-src/subjects/history/chapter_ledger.json", encoding="utf-8") as f:
    ledger = json.load(f)
ledger.sort(key=lambda x: x["found_start"])

with open("dashboard-src/subjects/history/parsed_chapter_stats.json", encoding="utf-8") as f:
    stats = json.load(f)

print(f"Total ledger entries: {len(ledger)}")
print(f"Total stats entries: {len(stats)}")

modern_stats = [s for s in stats if 41 <= s['num'] <= 95]
print(f"Modern chapters count: {len(modern_stats)}")

for s in modern_stats:
    print(f"Ch {s['num']:2d}: {s['title'][:45]:45} | pp. {s['pages']:9} | {s['uppsc_count']} UPPSC Qs")
