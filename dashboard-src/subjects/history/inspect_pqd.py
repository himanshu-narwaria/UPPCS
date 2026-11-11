import json, re
from collections import Counter

with open("Indian_Polity_2026/polity-uppsc-full-notes.html", encoding="utf-8") as f:
    s = f.read()

m = re.search(r'<script id="pqd"[^>]*>(.*?)</script>', s, re.S)
if m:
    data = json.loads(m.group(1))
    print(f"Polity questions count: {len(data)}")
    first_q = list(data.values())[0] if isinstance(data, dict) else data[0]
    print("Sample question:", json.dumps(first_q, indent=2))
    
    # Check all unique 'e' (exam) strings
    exams = Counter(q["e"] for q in (data.values() if isinstance(data, dict) else data))
    print("\nTotal distinct exams:", len(exams))
    print("Top 20 exam strings:")
    for e, c in exams.most_common(20):
        print(f"  {e}: {c}")

with open("Economy 2024/economy-uppsc-full-notes.html", encoding="utf-8") as f:
    s_ec = f.read()

m_ec = re.search(r'<script id="pqd"[^>]*>(.*?)</script>', s_ec, re.S)
if m_ec:
    data_ec = json.loads(m_ec.group(1))
    print(f"\nEconomy questions count: {len(data_ec)}")
    exams_ec = Counter(q["e"] for q in (data_ec.values() if isinstance(data_ec, dict) else data_ec))
    print("Top 15 Economy exam strings:")
    for e, c in exams_ec.most_common(15):
        print(f"  {e}: {c}")
