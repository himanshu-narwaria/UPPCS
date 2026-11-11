import json
from collections import Counter

with open("Indian_Polity_2026/polity-uppsc-full-notes.html", encoding="utf-8") as f:
    s = f.read()

import re
m = re.search(r'<script id="pqd"[^>]*>(.*?)</script>', s, re.S)
data = json.loads(m.group(1))
exams = sorted(set(q["e"] for q in (data.values() if isinstance(data, dict) else data)))
print(f"Total unique exam labels in Polity: {len(exams)}")
print("Sample 40 labels:")
for e in exams[:40]:
    print(" ", repr(e))
