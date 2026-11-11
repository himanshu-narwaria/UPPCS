import json

with open("dashboard-src/subjects/geography/parsed_uppsc_questions.json", encoding="utf-8") as f:
    qs = json.load(f)

# Inspect c1 questions
c1_qs = [q for q in qs.values() if q["ch"] == "c1"]
print(f"c1 total qs: {len(c1_qs)}")
for q in c1_qs[:3]:
    print("Stem:", q["s"][:80])
    print("Exam:", q["e"])
    print("Count:", q["n"])
    print("Feedback:", q["f"][:80])
    print("---")
