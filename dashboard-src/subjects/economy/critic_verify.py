import os
import sys
import re
import json

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
folder = os.path.join(ROOT, "Economy 2024")
full_file = os.path.join(folder, "economy-uppsc-full-notes.html")
quick_file = os.path.join(folder, "economy-uppsc-quick-notes.html")
plan_file = os.path.join(folder, "economy-in-72h.html")

fc = open(full_file, encoding="utf-8").read()
qc = open(quick_file, encoding="utf-8").read()
pc = open(plan_file, encoding="utf-8").read()

# 1. Chapters in full notes
f_ch_links = re.findall(r'<a href="#(c\d+)"><span class="no">(\d+)</span><span class="nm">([^<]+)</span>.*?<span class="q">(\d+)\s+UPPSC PYQs</span></a>', fc)
f_ch_sections = re.findall(r'<section class="view ch" id="(c\d+)" data-title="([^"]+)">', fc)

# 2. Chapters in quick notes
q_ch_links = re.findall(r'<a href="#(c\d+)"><span class="no">(\d+)</span><span class="nm">([^<]+)</span>.*?<span class="q">(\d+)\s+UPPSC PYQs</span></a>', qc)
q_ch_sections = re.findall(r'<section class="view ch" id="(c\d+)" data-title="([^"]+)">', qc)

# 3. Chapters in 72h plan
p_hours = re.findall(r'<section class="view" id="h(\d+)" data-n="(\d+)">', pc)

# 4. Full notes practice bank
pqd_match = re.search(r'<script id="pqd" type="application/json">(.*?)</script>', fc, re.S)
pqd_data = json.loads(pqd_match.group(1)) if pqd_match else {}

# 5. Full notes repeated facts
f_rep_facts = re.findall(r'<summary><span class="t">(.*?)</span><span class="ps">', fc)
f_rep_header = re.search(r'(\d+)\s+facts asked in two or more UPPSC papers', fc)

# 6. Quick notes repeated facts
q_rep_facts = re.findall(r'<summary><span class="t">(.*?)</span><span class="ps">', qc)
q_rep_header = re.search(r'(\d+)\s+facts asked in two or more UPPSC papers', qc)

# 7. Quick notes foot line
q_foot = re.search(r'Based on (\d+) UPPSC questions', qc)

# 8. 72h plan first localStorage call
p_ls_first = re.search(r'localStorage\.[gs]etItem\(([^)]+)\)', pc)

print("=== DEEP CRITIC VERIFICATION RESULTS (ECONOMY) ===")
print(f"Full notes chapter links in TOC: {len(f_ch_links)}")
print(f"Full notes chapter views: {len(f_ch_sections)}")
print(f"Quick notes chapter links in TOC: {len(q_ch_links)}")
print(f"Quick notes chapter views: {len(q_ch_sections)}")
print(f"Full notes MCQ bank (pqd): {len(pqd_data)}")
sum_f_qs = sum(int(x[3]) for x in f_ch_links)
sum_q_qs = sum(int(x[3]) for x in q_ch_links)
print(f"Full notes sum of chapter question counts: {sum_f_qs}")
print(f"Quick notes sum of chapter question counts: {sum_q_qs}")
print(f"Full notes repeated facts count: {len(f_rep_facts)}, Header: {f_rep_header.group(1) if f_rep_header else 'None'}")
print(f"Quick notes repeated facts count: {len(q_rep_facts)}, Header: {q_rep_header.group(1) if q_rep_header else 'None'}")
print(f"Quick notes foot line questions count: {q_foot.group(1) if q_foot else 'None'}")
print(f"72h plan total hours: {len(p_hours)}")
print(f"72h plan first localStorage call: {p_ls_first.group(0) if p_ls_first else 'None'}")

# Assertions
assert len(f_ch_links) == 19, f"Expected 19 chapters in full notes TOC, got {len(f_ch_links)}"
assert len(f_ch_sections) == 19, f"Expected 19 chapter sections in full notes, got {len(f_ch_sections)}"
assert len(q_ch_links) == 19, f"Expected 19 chapters in quick notes TOC, got {len(q_ch_links)}"
assert len(q_ch_sections) == 19, f"Expected 19 chapter sections in quick notes, got {len(q_ch_sections)}"
assert len(pqd_data) == 1757, f"Expected 1757 MCQs in pqd, got {len(pqd_data)}"
assert sum_f_qs == 1757, f"Expected sum of full notes chapter counts 1757, got {sum_f_qs}"
assert sum_q_qs == 1757, f"Expected sum of quick notes chapter counts 1757, got {sum_q_qs}"
assert len(p_hours) == 72, f"Expected 72 hours in 72h plan, got {len(p_hours)}"
assert len(f_rep_facts) == 280, f"Expected 280 repeated facts in full notes, got {len(f_rep_facts)}"
assert len(q_rep_facts) == 280, f"Expected 280 repeated facts in quick notes, got {len(q_rep_facts)}"
assert int(f_rep_header.group(1)) == 280, f"Expected 280 in full notes header, got {f_rep_header.group(1)}"
assert int(q_rep_header.group(1)) == 280, f"Expected 280 in quick notes header, got {q_rep_header.group(1)}"
assert int(q_foot.group(1)) == 1757, f"Expected 1757 in quick notes footer, got {q_foot.group(1)}"
assert 'eco72-done' in p_ls_first.group(0), f"Expected eco72-done in localStorage, got {p_ls_first.group(0)}"

# Chapter titles match exactly between full and quick notes
for (f_id, f_no, f_title, f_q), (q_id, q_no, q_title, q_q) in zip(f_ch_links, q_ch_links):
    assert f_id == q_id, f"ID mismatch: {f_id} vs {q_id}"
    assert f_no == q_no, f"Number mismatch: {f_no} vs {q_no}"
    assert f_title == q_title, f"Title mismatch: '{f_title}' vs '{q_title}'"
    assert f_q == q_q, f"Question count mismatch in Ch {f_no}: {f_q} vs {q_q}"

print("All 19 chapter IDs, titles, numbers, and PYQ counts match 100% between full and quick notes!")

# Spot-check 20 key economy concepts & facts in quick notes
spot_checks = [
    "Mixed economy",
    "National Income",
    "Sustainable Development",
    "NITI Aayog",
    "Green Revolution",
    "Maharatna",
    "Goods and Services Tax",
    "Vijay Kelkar",
    "FRBM",
    "Finance Commission",
    "Five Year Plan",
    "RBI",
    "NABARD",
    "SEBI",
    "Human Development Index",
    "MGNREGA",
    "Census 2011",
    "Decadal growth",
    "Sex ratio",
    "Urbanization"
]

found_checks = 0
for term in spot_checks:
    found = term.lower() in qc.lower()
    if found:
        found_checks += 1
    print(f"  [{'PASS' if found else 'FAIL'}] Spot-check term: '{term}'")

assert found_checks == len(spot_checks), f"Expected all {len(spot_checks)} spot-check terms to be found, got {found_checks}"
print(f"ALL {found_checks}/{len(spot_checks)} SPOT-CHECK TERMS VERIFIED IN QUICK NOTES!")
print("ALL CRITIC VERIFICATION ASSERTIONS PASSED!")

if __name__ == "__main__":
    pass
