import json

with open("dashboard-src/subjects/history/accurate_ranges.json", encoding="utf-8") as f:
    ranges = json.load(f)

with open("dashboard-src/subjects/history/parsed_uppsc_questions.json", encoding="utf-8") as f:
    qs = json.load(f)

for r in ranges:
    if 41 <= r["num"] <= 95:
        num = r["num"]
        c_qs = [q for q in qs.values() if q["ch"] == f"c{num}"]
        years = [q["y"] for q in c_qs]
        hot_qs = [q for q in c_qs if q.get("n", 1) >= 2]
        print(f"Ch {num:2d}: {r['title'][:40]:40} | Qs: {len(c_qs):2d} | Hot: {len(hot_qs):2d} | Range: {r['start']}-{r['nominal_end']}")
