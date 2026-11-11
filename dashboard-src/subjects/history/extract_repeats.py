import json, re

with open("dashboard-src/subjects/history/parsed_uppsc_questions.json", encoding="utf-8") as f:
    qs = json.load(f)

print(f"Total questions: {len(qs)}")
repeats_from_n = [q for q in qs.values() if q["n"] >= 2]
print(f"Questions with multiple UPPSC exam tags (n >= 2): {len(repeats_from_n)}")

# Sample repeats
print("\nSample 10 repeats from multi-exam tags:")
for q in repeats_from_n[:10]:
    print(f"[{q['ch']}] ×{q['n']} ({q['e']}) {q['s'][:75]}...")
