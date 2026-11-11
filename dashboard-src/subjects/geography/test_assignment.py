import sys, json, re, os
sys.path.insert(0, 'dashboard-src/subjects/geography')
from chapter_definitions_1_31 import CHAPTER_DATA

with open("dashboard-src/subjects/geography/accurate_chapter_ranges.json", encoding="utf-8") as f:
    ranges = json.load(f)

with open("dashboard-src/subjects/geography/parsed_uppsc_questions.json", encoding="utf-8") as f:
    qs = json.load(f)

qs_by_ch = {}
for qid, q in qs.items():
    ch_num = int(q["ch"][1:])
    if ch_num not in qs_by_ch:
        qs_by_ch[ch_num] = []
    q["qid"] = qid
    qs_by_ch[ch_num].append(q)

print("Testing question assignment across topics...")
for num in range(1, 32):
    ch_def = CHAPTER_DATA[num]
    ch_qs = qs_by_ch.get(num, [])
    topics = ch_def["topics"]
    
    assigned = {t["id"]: 0 for t in topics}
    for q in ch_qs:
        text = (q["s"] + " " + q.get("f", "")).lower()
        best_t = topics[0]["id"]
        best_score = 0
        for t in topics:
            score = sum(1 for kw in t.get("keywords", []) if kw in text)
            if score > best_score:
                best_score = score
                best_t = t["id"]
        # If no score, distribute evenly
        if best_score == 0:
            # Pick topic with fewest assigned
            best_t = min(assigned.keys(), key=lambda k: assigned[k])
        assigned[best_t] += 1
    print(f"Ch {num:2d} ({len(ch_qs):3d} Qs): {assigned}")
