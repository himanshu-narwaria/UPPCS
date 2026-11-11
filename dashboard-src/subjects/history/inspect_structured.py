import json

with open("dashboard-src/subjects/history/structured_all_chapters.json", encoding="utf-8") as f:
    data = json.load(f)

print(f"Total chapters in structured_all_chapters: {len(data)}")
for ch in data:
    if ch["num"] in [1, 41, 46, 52]:
        print(f"\n--- Chapter {ch['num']}: {ch['title']} ---")
        print("Gist:", ch.get("gist"))
        print("Focus items count:", len(ch.get("focus", [])))
        if ch.get("focus"):
            print("Focus sample:", ch["focus"][0])
        print("Topics count:", len(ch.get("topics", [])))
        if ch.get("topics"):
            top = ch["topics"][0]
            print("Topic 1:", top["id"], top["title"], top.get("pg"))
            print("Points count:", len(top.get("points", [])))
            if top.get("points"):
                print("Point 1:", top["points"][0])
