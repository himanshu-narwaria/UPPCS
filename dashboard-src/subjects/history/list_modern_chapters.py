import json

with open("dashboard-src/subjects/history/parsed_chapter_stats.json", encoding="utf-8") as f:
    stats = json.load(f)

for s in stats:
    if 41 <= s["num"] <= 95:
        print(f"{s['num']:2d} | {s['title'][:50]:50} | pp. {s['pages']:9} | {s['uppsc_count']} Qs | intro len: {len(s['intro'])}")
