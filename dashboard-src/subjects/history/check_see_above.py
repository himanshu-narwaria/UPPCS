import json, re

with open("dashboard-src/subjects/history/parsed_uppsc_questions.json", encoding="utf-8") as f:
    qs = json.load(f)

mod_qs = {qid: q for qid, q in qs.items() if 41 <= int(q["ch"][1:]) <= 95}
print("Total modern questions:", len(mod_qs))

see_above_cnt = 0
for qid, q in mod_qs.items():
    if "see the explanation" in q["f"].lower():
        see_above_cnt += 1

print(f"Questions with 'See the explanation': {see_above_cnt} out of {len(mod_qs)}")
