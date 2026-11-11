import json

with open("dashboard-src/subjects/geography/parsed_uppsc_questions.json", encoding="utf-8") as f:
    qs = json.load(f)
print(f"Total parsed UPPSC questions: {len(qs)}")
sample_q = next(iter(qs.items()))
print(f"Sample Q: {sample_q[0]} -> keys: {list(sample_q[1].keys())}")
print(f"Sample content: {sample_q[1]}")

# Count questions per chapter for ch 1-31
ch_counts = {}
for qid, q in qs.items():
    ch_id = q.get("ch") # e.g. "c1", "c2"
    ch_counts[ch_id] = ch_counts.get(ch_id, 0) + 1

print("\nQuestion counts for ch 1 to 31:")
for i in range(1, 32):
    cid = f"c{i}"
    print(f"{cid}: {ch_counts.get(cid, 0)} questions", end=" | " if i % 5 != 0 else "\n")
print()

with open("dashboard-src/subjects/geography/repeated_facts.json", encoding="utf-8") as f:
    rep = json.load(f)
print(f"Total repeated facts entries: {len(rep)}")
if rep:
    print(f"Sample repeated fact: {rep[0]}")
