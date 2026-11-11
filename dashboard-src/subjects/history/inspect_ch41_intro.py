import json

with open("dashboard-src/subjects/history/parsed_chapter_stats.json", encoding="utf-8") as f:
    stats = json.load(f)

for s in stats:
    if s["num"] == 41:
        print("Chapter 41 intro preview:")
        print(s["intro"][:1000])
        print("Length of intro:", len(s["intro"]))
        break
