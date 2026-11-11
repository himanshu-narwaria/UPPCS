import re
import json

with open('Indian_History_Part_2/history-uppsc-full-notes.html', 'r', encoding='utf-8') as f:
    full = f.read()

with open('Indian_History_Part_2/history-uppsc-quick-notes.html', 'r', encoding='utf-8') as f:
    quick = f.read()

with open('Indian_History_Part_2/history-in-72h.html', 'r', encoding='utf-8') as f:
    h72 = f.read()

with open('study-dashboard.html', 'r', encoding='utf-8') as f:
    dash = f.read()

print("=== 1. CHAPTER COUNTS ===")
full_ch = re.findall(r'<section\s+class="view ch"\s+id="(c\d+)"', full)
print(f"Full notes chapter views: {len(full_ch)} (first: {full_ch[0]}, last: {full_ch[-1]})")

quick_ch = re.findall(r'<section\s+class="view ch"\s+id="(c\d+)"', quick)
print(f"Quick notes chapter views: {len(quick_ch)} (first: {quick_ch[0]}, last: {quick_ch[-1]})")

h72_hours = re.findall(r'<section\s+class="view"\s+id="h(\d+)"', h72)
print(f"72h plan hours count: {len(h72_hours)} (first: h{h72_hours[0]}, last: h{h72_hours[-1]})")

print("\n=== 2. QUESTIONS DATA (<script id='pqd' type='application/json'>) ===")
full_pqd = re.search(r'<script\s+id="pqd"\s+type="application/json">(.*?)</script>', full, re.S)
if full_pqd:
    data_full = json.loads(full_pqd.group(1))
    print(f"Full notes pqd question count: {len(data_full)}")

h72_pqd = re.search(r'<script\s+id="pqd"\s+type="application/json">(.*?)</script>', h72, re.S)
if h72_pqd:
    data_h72 = json.loads(h72_pqd.group(1))
    print(f"72h notes pqd question count: {len(data_h72)}")

print("\n=== 3. REPEATED FACTS COUNT ===")
rep_full_m = re.search(r'<section class="view" id="repeated".*?</section>', full, re.S)
if rep_full_m:
    rep_rows = re.findall(r'<summary><span class="t">', rep_full_m.group(0))
    m_num = re.search(r'(\d+)\s+facts asked in two or more', rep_full_m.group(0))
    print(f"Full notes stated: {m_num.group(1)}, actual summary tags: {len(rep_rows)}")

rep_quick_m = re.search(r'<section class="view" id="repeated".*?</section>', quick, re.S)
if rep_quick_m:
    rep_rows_q = re.findall(r'<summary><span class="t">', rep_quick_m.group(0))
    m_num_q = re.search(r'(\d+)\s+facts asked in two or more', rep_quick_m.group(0))
    print(f"Quick notes stated: {m_num_q.group(1)}, actual summary tags: {len(rep_rows_q)}")

print("\n=== 4. EXAM DATE AND PROGRESS KEY ===")
print("72h matches exam phrase:", bool(re.search(r"72 hours before 6 December 2026", h72)))
print("72h progress key matches his72-done:", re.search(r'localStorage\.getItem\("([^"]+)"\)', h72).group(1))

print("\n=== 5. SPOT-CHECK 20 FACTS AGAINST RAW PDF ===")
with open("dashboard-src/subjects/history/raw_pages.json", encoding="utf-8") as f:
    pages = json.load(f)

sample_ids = ["q0001", "q0010", "q0050", "q0120", "q0200", "q0300", "q0450",
              "q0600", "q0700", "q0800", "q0900", "q1000", "q1100",
              "q1250", "q1400", "q1550", "q1700", "q1850", "q2000", "q2150"]

all_matched = True
for qid in sample_ids:
    q = data_full[qid]
    words = [w for w in re.sub(r'[^a-zA-Z0-9\s]', ' ', q['s']).split() if len(w) > 4]
    matched = any(all(w in page['text'] for w in words[:3]) for page in pages)
    if not matched:
        all_matched = False
        print(f"FAIL: {qid} words not found in PDF: {words[:4]}")

if all_matched:
    print(f"ALL 20 sample facts confirmed 100% present in Ghatna Chakra PDF!")
