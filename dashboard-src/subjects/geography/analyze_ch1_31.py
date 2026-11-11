import json

with open("dashboard-src/subjects/geography/accurate_chapter_ranges.json", encoding="utf-8") as f:
    ranges = json.load(f)

with open("dashboard-src/subjects/geography/parsed_uppsc_questions.json", encoding="utf-8") as f:
    qs = json.load(f)

with open("dashboard-src/subjects/geography/repeated_facts.json", encoding="utf-8") as f:
    rep = json.load(f)

# Group questions by chapter
qs_by_ch = {}
for qid, q in qs.items():
    ch_num = int(q["ch"][1:])
    if ch_num not in qs_by_ch:
        qs_by_ch[ch_num] = []
    qs_by_ch[ch_num].append(q)

# Group repeated facts by chapter
rep_by_ch = {}
for r in rep:
    ch_num = r.get("ch")
    if ch_num not in rep_by_ch:
        rep_by_ch[ch_num] = []
    rep_by_ch[ch_num].append(r)

for r in ranges[:31]:
    num = r["num"]
    title = r["title"]
    ch_qs = qs_by_ch.get(num, [])
    ch_rep = rep_by_ch.get(num, [])
    hot_qs = [q for q in ch_qs if q.get("n", 1) >= 2]
    print(f"Ch {num:2d}: {title:35s} | {len(ch_qs):3d} UPPSC Qs | {len(hot_qs):2d} Hot Qs | {len(ch_rep):2d} Rep Facts")
