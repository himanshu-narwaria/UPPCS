import json, re

with open("dashboard-src/subjects/history/accurate_ranges.json", encoding="utf-8") as f:
    ranges = json.load(f)

with open("dashboard-src/subjects/history/raw_pages.json", encoding="utf-8") as f:
    pages = json.load(f)

with open("dashboard-src/subjects/history/parsed_uppsc_questions.json", encoding="utf-8") as f:
    qs = json.load(f)

# Let's inspect where chapters 41-95 start in raw_pages
for entry in ranges:
    if 41 <= entry["num"] <= 95:
        num = entry["num"]
        title = entry["title"]
        start_p = entry["start"]
        nom_start = entry["nominal_start"]
        nom_end = entry["nominal_end"]
        # Count questions in parsed_uppsc_questions
        c_qs = [q for q in qs.values() if q["ch"] == f"c{num}"]
        print(f"Ch {num:2d} | {title[:38]:38} | start: {start_p:3d} (nom {nom_start}-{nom_end}) | {len(c_qs):2d} UPPSC Qs")
