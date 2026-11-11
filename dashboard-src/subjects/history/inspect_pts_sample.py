import json

with open("dashboard-src/subjects/history/structured_all_chapters.json", encoding="utf-8") as f:
    data = json.load(f)

for ch in data[:3]:
    print(f"Chapter {ch['num']}: {ch['title']}")
    for top in ch["topics"]:
        print(f"  Topic: {top['id']} - {top['title']}")
        for pt in top["points"][:3]:
            print(f"    Point: hot={pt.get('hot')} asked={pt.get('asked')}")
            print(f"    html: {pt.get('html')[:120]}")
