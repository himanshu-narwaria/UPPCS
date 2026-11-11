import json

with open("dashboard-src/subjects/geography/parsed_uppsc_questions.json", encoding="utf-8") as f:
    qs = json.load(f)

# Group questions by chapter
qs_by_ch = {}
for qid, q in qs.items():
    ch_num = int(q["ch"][1:])
    if ch_num not in qs_by_ch:
        qs_by_ch[ch_num] = []
    qs_by_ch[ch_num].append(q)

print("Parsed UPPSC questions successfully loaded.")
for i in range(1, 32):
    print(f"Ch {i}: {len(qs_by_ch.get(i, []))} questions")
