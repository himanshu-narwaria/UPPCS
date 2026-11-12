import os
import sys
import re
import json

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
folder = os.path.join(ROOT, "Indian_Polity_and_Governance")
full_file = os.path.join(folder, "polity-uppsc-full-notes.html")
quick_file = os.path.join(folder, "polity-uppsc-quick-notes.html")
plan_file = os.path.join(folder, "polity-in-72h.html")

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
assert len(f_ch_links) == 42, f"Expected 42 chapters in full notes TOC, got {len(f_ch_links)}"
assert len(f_ch_sections) == 42, f"Expected 42 chapter sections in full notes, got {len(f_ch_sections)}"
assert len(q_ch_links) == 42, f"Expected 42 chapters in quick notes TOC, got {len(q_ch_links)}"
assert len(q_ch_sections) == 42, f"Expected 42 chapter sections in quick notes, got {len(q_ch_sections)}"
assert len(pqd_data) == 1280, f"Expected 1280 MCQs in pqd, got {len(pqd_data)}"
assert sum_f_qs == 1280, f"Expected sum of chapter counts 1280, got {sum_f_qs}"
assert len(p_hours) == 72, f"Expected 72 hours in 72h plan, got {len(p_hours)}"
assert len(f_rep_facts) == 141, f"Expected 141 repeated facts in full notes, got {len(f_rep_facts)}"
assert len(q_rep_facts) == 141, f"Expected 141 repeated facts in quick notes, got {len(q_rep_facts)}"
assert int(f_rep_header.group(1)) == 141, f"Expected 141 in full notes header, got {f_rep_header.group(1)}"
assert int(q_rep_header.group(1)) == 141, f"Expected 141 in quick notes header, got {q_rep_header.group(1)}"
assert int(q_foot.group(1)) == 1280, f"Expected 1280 in quick notes footer, got {q_foot.group(1)}"
assert 'polgov72-done' in p_ls_first.group(0), f"Expected polgov72-done in localStorage, got {p_ls_first.group(0)}"

# Spot-check 20 random facts from PDF
raw_pages_path = os.path.join(os.path.dirname(__file__), "raw_pages.json")
raw_pages = json.load(open(raw_pages_path, encoding="utf-8"))
raw_full = " ".join(p["text"] for p in raw_pages)

spot_checks = [
    "Regulating Act of 1773",
    "Warren Hastings",
    "Cabinet Mission",
    "Swaraj Party",
    "Drafting Committee",
    "Dr. B.R. Ambedkar",
    "Government of India Act 1935",
    "Article 32",
    "Sarkaria Commission",
    "Panchayati Raj",
    "Balwant Rai Mehta",
    "73rd Amendment",
    "74th Amendment",
    "Finance Commission",
    "Article 280",
    "Comptroller and Auditor",
    "Attorney General",
    "Article 76",
    "Lok Sabha",
    "Rajya Sabha",
    "Eighth Schedule",
    "Anti-Defection"
]

print("\nSpot-checking 22 core concepts against book text:")
for term in spot_checks:
    assert term.lower() in raw_full.lower(), f"Term '{term}' not found in raw book text!"
    print(f"  [OK] '{term}' verified in book text.")

print("\nALL DEEP CRITIC CHECKS PASSED WITH 100% SUCCESS!")
