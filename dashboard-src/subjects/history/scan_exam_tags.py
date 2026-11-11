import json, re
from collections import Counter

with open("dashboard-src/subjects/history/raw_pages.json", encoding="utf-8") as f:
    pages = json.load(f)

# Let's inspect how exam lines appear.
# In Ghatna Chakra, exam tags usually look like:
# U.P.P.C.S. (Pre) 2018
# U.P. Lower Sub. (Pre) 2004
# U.P. R.O./A.R.O. (Pre) 2017
# 44th B.P.S.C. (Pre) 2000
# I.A.S. (Pre) 1993
# etc.

# Let's look for lines containing U.P., UPPCS, PCS, RO/ARO, etc.
uppsc_patterns = [
    r'U\.?P\.?P?\.?C\.?S\.?',
    r'U\.?P\.?\s*R\.?O\.?',
    r'U\.?P\.?\s*A\.?R\.?O\.?',
    r'U\.?P\.?\s*Lower',
    r'U\.?P\.?\s*UDA',
    r'U\.?P\.?\s*LDA',
    r'U\.?P\.?\s*GIC',
    r'U\.?P\.?\s*BEO',
    r'U\.?P\.?\s*RI',
    r'UPPCS',
]

exam_lines = []
for p in pages:
    txt = p["text"]
    lines = txt.split("\n")
    for l in lines:
        l_str = l.strip()
        if any(re.search(pat, l_str, re.I) for pat in uppsc_patterns):
            exam_lines.append((p["pdf_page"], l_str))

print(f"Total matching lines: {len(exam_lines)}")
print("Sample 30 lines:")
for p, l in exam_lines[:30]:
    print(f"  p.{p}: {l}")

counts = Counter(l for _, l in exam_lines)
print("\nTop 30 unique UPPSC exam lines:")
for l, c in counts.most_common(30):
    print(f"  {c:3d}: {l}")
