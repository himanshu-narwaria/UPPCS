import json, re

with open("dashboard-src/subjects/history/raw_pages.json", encoding="utf-8") as f:
    pages = json.load(f)

# Let's inspect Stone Age (pages 9 to 16)
stone_age_text = "\n".join(pages[p-1]["text"] for p in range(9, 17))

# Let's test parsing questions
# Questions start with number followed by dot, e.g. "1.  According to..." or "13.  The first..."
# And options (a), (b), (c), (d)
# Exam tag: e.g. "U.P.P.C.S. (Pre) 1997"
# Ans: e.g. "Ans. (c)"
# Followed by explanation

# Let's find all question blocks
q_pattern = re.compile(r'(?:^|\n)\s*(\d{1,3})\.\s+(.*?)(?=(?:\n\s*\d{1,3}\.\s+)|\Z)', re.S)
matches = list(q_pattern.finditer(stone_age_text))
print(f"Total questions found in Stone Age: {len(matches)}")

for i, m in enumerate(matches[:5]):
    q_num = m.group(1)
    q_body = m.group(2).strip()
    print(f"\n--- Q {q_num} ---")
    # Let's see if we can find Ans, exam tag, etc.
    ans_m = re.search(r'Ans\.\s*\(([a-d\*])\)', q_body)
    ans = ans_m.group(1) if ans_m else "NOT FOUND"
    print(f"Ans: {ans}")
    print(f"Body snippet:\n{q_body[:300]}...")
