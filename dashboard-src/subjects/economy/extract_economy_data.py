import re
import json

with open("Economy 2024/economy-uppsc-full-notes.html", "r", encoding="utf-8") as f:
    fc = f.read()

chapters_data = []
for i in range(1, 20):
    ch_m = re.search(rf'<section class="view ch" id="c{i}" data-title="([^"]+)">(.*?)</section>', fc, re.S)
    if not ch_m:
        print(f"Ch {i} missing!")
        continue
    title = ch_m.group(1)
    body = ch_m.group(2)
    gist_m = re.search(r'<p class="gist">(.*?)</p>', body, re.S)
    gist = gist_m.group(1) if gist_m else ""
    
    topics = []
    t_matches = re.findall(r'<article class="topic" id="([^"]+)">\s*<h3>(.*?)</h3>\s*<ul>(.*?)</ul>\s*</article>', body, re.S)
    for tid, ttitle, tul in t_matches:
        pts = re.findall(r'<li class="([^"]+)">(.*?)</li>', tul, re.S)
        topics.append({
            "id": tid,
            "title": ttitle,
            "points": [{"cls": cls, "html": pthtml} for cls, pthtml in pts]
        })
    chapters_data.append({
        "num": i,
        "title": title,
        "gist": gist,
        "topics": topics
    })

print(f"Extracted {len(chapters_data)} chapters.")
total_pts = sum(len(t["points"]) for c in chapters_data for t in c["topics"])
asked_pts = sum(1 for c in chapters_data for t in c["topics"] for p in t["points"] if "asked" in p["cls"])
print(f"Total points: {total_pts}, asked/hot points: {asked_pts}")

# Save extracted chapters
with open("dashboard-src/subjects/economy/extracted_economy_chapters.json", "w", encoding="utf-8") as f:
    json.dump(chapters_data, f, ensure_ascii=False, indent=2)

print("Saved to dashboard-src/subjects/economy/extracted_economy_chapters.json")
