import json

with open("dashboard-src/subjects/history/parsed_uppsc_questions.json", encoding="utf-8") as f:
    questions = json.load(f)

mod_qs = [q for qid, q in questions.items() if 41 <= int(q["ch"][1:]) <= 95]
print(f"Total modern UPPSC questions: {len(mod_qs)}")
if mod_qs:
    print("Sample question:", json.dumps(mod_qs[0], indent=2))
