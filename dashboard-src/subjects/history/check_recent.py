import json
from collections import Counter

with open("dashboard-src/subjects/history/parsed_uppsc_questions.json", encoding="utf-8") as f:
    qs = json.load(f)

recent_qs = [q for q in qs.values() if q["y"] >= 2021]
print(f"Total recent UPPSC questions (2021-2025): {len(recent_qs)}")

by_year = Counter(q["y"] for q in recent_qs)
for yr in sorted(by_year.keys(), reverse=True):
    print(f"  {yr}: {by_year[yr]} questions")

print("\nSample recent questions:")
for q in recent_qs[:8]:
    print(f"  [{q['y']} {q['e']}] ({q['ch']}) {q['s'][:80]}...")
