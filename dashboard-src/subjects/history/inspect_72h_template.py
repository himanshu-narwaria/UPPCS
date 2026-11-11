import re

with open("Indian_Polity_2026/polity-in-72h.html", encoding="utf-8") as f:
    text = f.read()

m_h1 = re.search(r'<section class="view" id="h1"[^>]*>.*?</section>', text, re.S)
if m_h1:
    content = m_h1.group(0)
    print("END OF HOUR 1:")
    print(content[-1500:])

m_h72 = re.search(r'<section class="view" id="h72"[^>]*>.*?</section>', text, re.S)
if m_h72:
    print("\nHOUR 72:")
    print(m_h72.group(0)[:800])
    print(m_h72.group(0)[-800:])

# Check how questions are embedded in pqd script tag or similar
m_pqd = re.search(r'<script id="pqd"[^>]*>(.*?)</script>', text, re.S)
if m_pqd:
    print("\nPQD script tag length:", len(m_pqd.group(1)))
    print("Sample PQD (first 300 chars):", m_pqd.group(1)[:300])
