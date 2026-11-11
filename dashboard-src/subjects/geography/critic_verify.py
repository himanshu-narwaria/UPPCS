import os
import sys
import re
import json

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
folder = os.path.join(ROOT, "General_Geography_Part_3")
full_file = os.path.join(folder, "geography-uppsc-full-notes.html")
quick_file = os.path.join(folder, "geography-uppsc-quick-notes.html")
plan_file = os.path.join(folder, "geography-in-72h.html")

fc = open(full_file, encoding="utf-8").read()
qc = open(quick_file, encoding="utf-8").read()
pc = open(plan_file, encoding="utf-8").read()

# 1. Chapters in full notes
f_ch_links = re.findall(r'<a href="#(c\d+)"><span class="no">(\d+)</span><span class="nm">([^<]+)</span>.*?<span class="q">(\d+)\s+UPPSC PYQs</span></a>', fc)
f_ch_sections = re.findall(r'<section class="view ch" id="(c\d+)" data-title="([^"]+)">', fc)

# 2. Chapters in quick notes
q_ch_links = re.findall(r'<a href="#(c\d+)"><span class="no">(\d+)</span><span class="nm">([^<]+)</span>', qc)
q_ch_sections = re.findall(r'<section class="view ch" id="(c\d+)" data-title="([^"]+)">', qc)

# 3. Chapters in 72h plan
p_hours = re.findall(r'<section class="view" id="h(\d+)" data-n="(\d+)">', pc)

# 4. Full notes practice bank
pqd_match = re.search(r'<script id="pqd" type="application/json">(.*?)</script>', fc, re.S)
pqd_data = json.loads(pqd_match.group(1)) if pqd_match else []

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

print("=== DEEP CRITIC VERIFICATION RESULTS ===")
print(f"Full notes chapter links in TOC: {len(f_ch_links)}")
print(f"Full notes chapter views: {len(f_ch_sections)}")
print(f"Quick notes chapter links in TOC: {len(q_ch_links)}")
print(f"Quick notes chapter views: {len(q_ch_sections)}")
print(f"Full notes MCQ bank (pqd): {len(pqd_data)}")
sum_f_qs = sum(int(x[3]) for x in f_ch_links)
print(f"Full notes sum of chapter question counts: {sum_f_qs}")
print(f"Full notes repeated facts count: {len(f_rep_facts)}, Header: {f_rep_header.group(1) if f_rep_header else 'None'}")
print(f"Quick notes repeated facts count: {len(q_rep_facts)}, Header: {q_rep_header.group(1) if q_rep_header else 'None'}")
print(f"Quick notes foot line questions count: {q_foot.group(1) if q_foot else 'None'}")
print(f"72h plan total hours: {len(p_hours)}")
print(f"72h plan first localStorage call: {p_ls_first.group(0) if p_ls_first else 'None'}")

# Assertions
assert len(f_ch_links) == 83, f"Expected 83 chapters in full notes TOC, got {len(f_ch_links)}"
assert len(f_ch_sections) == 83, f"Expected 83 chapter views in full notes, got {len(f_ch_sections)}"
assert len(q_ch_links) == 83, f"Expected 83 chapters in quick notes TOC, got {len(q_ch_links)}"
assert len(q_ch_sections) == 83, f"Expected 83 chapter views in quick notes, got {len(q_ch_sections)}"
assert len(pqd_data) == 1795, f"Expected 1795 MCQs in pqd, got {len(pqd_data)}"
assert sum_f_qs == 1795, f"Expected 1795 total MCQs in TOC, got {sum_f_qs}"
assert q_foot.group(1) == "1795", f"Expected 1795 in quick foot line, got {q_foot.group(1)}"
assert len(f_rep_facts) == 128, f"Expected 128 repeated facts in full notes, got {len(f_rep_facts)}"
assert f_rep_header.group(1) == "128", f"Expected header 128 in full notes, got {f_rep_header.group(1)}"
assert len(q_rep_facts) == 128, f"Expected 128 repeated facts in quick notes, got {len(q_rep_facts)}"
assert q_rep_header.group(1) == "128", f"Expected header 128 in quick notes, got {q_rep_header.group(1)}"
assert len(p_hours) == 72, f"Expected 72 hours in 72h plan, got {len(p_hours)}"
assert 'localStorage.getItem("geo72-done")' in p_ls_first.group(0), f"Expected first localStorage call geo72-done, got {p_ls_first.group(0)}"

# Verify chapter titles match between full notes and quick notes
for i in range(83):
    f_title = f_ch_sections[i][1]
    q_title = q_ch_sections[i][1]
    assert f_title == q_title, f"Chapter {i+1} title mismatch: Full='{f_title}' vs Quick='{q_title}'"

print("\nALL ASSERTIONS PASSED: Chapter titles, counts, headers, footers, keys 100% matched!")
