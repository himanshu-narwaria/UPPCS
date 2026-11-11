import json
import re

with open('dashboard-src/subjects/history/structured_all_chapters.json', 'r', encoding='utf-8') as f:
    struct = json.load(f)

with open('Indian_History_Part_2/history-uppsc-full-notes.html', 'r', encoding='utf-8') as f:
    full = f.read()

with open('Indian_History_Part_2/history-uppsc-quick-notes.html', 'r', encoding='utf-8') as f:
    quick = f.read()

with open('Indian_History_Part_2/history-in-72h.html', 'r', encoding='utf-8') as f:
    h72 = f.read()

with open('dashboard-src/subjects/history/parsed_uppsc_questions.json', 'r', encoding='utf-8') as f:
    questions = json.load(f)

with open('dashboard-src/subjects/history/repeated_facts.json', 'r', encoding='utf-8') as f:
    repeated = json.load(f)

print(f"Total chapters in structured_all_chapters.json: {len(struct)}")
expected_ch_ids = [f"c{i}" for i in range(1, 96)]
struct_ids = [f"c{c['num']}" for c in struct]
assert struct_ids == expected_ch_ids, f"Mismatch in chapter ids: {set(expected_ch_ids) ^ set(struct_ids)}"

# Check full notes chapters
full_ch_ids = re.findall(r'<section\s+class="view\s+ch"\s+id="(c\d+)"', full)
assert full_ch_ids == expected_ch_ids, f"Mismatch in full notes chapters: {len(full_ch_ids)}"

# Check quick notes chapters
quick_ch_ids = re.findall(r'<section\s+class="view\s+ch"\s+id="(c\d+)"', quick)
assert quick_ch_ids == expected_ch_ids, f"Mismatch in quick notes chapters: {len(quick_ch_ids)}"

# Check questions count
print(f"Total questions in parsed_uppsc_questions.json: {len(questions)}")
assert len(questions) == 2164, f"Questions count is {len(questions)}, expected 2164"

# Check repeated facts count
print(f"Total repeated facts in repeated_facts.json: {len(repeated)}")
assert len(repeated) == 198, f"Repeated facts count is {len(repeated)}, expected 198"

# Check question keys in HTML
full_pqd = json.loads(re.search(r'<script\s+id="pqd"\s+type="application/json">(.*?)</script>', full, re.S).group(1))
assert len(full_pqd) == 2164, f"Full notes pqd has {len(full_pqd)} questions"

h72_pqd = json.loads(re.search(r'<script\s+id="pqd"\s+type="application/json">(.*?)</script>', h72, re.S).group(1))
assert len(h72_pqd) == 2164, f"72h pqd has {len(h72_pqd)} questions"

# Check exam date
assert "72 hours before 6 December 2026" in h72, "Missing exam date string in 72h plan"
with open('study-dashboard.html', 'r', encoding='utf-8') as f:
    dash = f.read()
assert "6 December 2026" in dash, "Missing exam date string in dashboard"

# Check progress key
assert 'localStorage.getItem("his72-done")' in h72, "Missing his72-done in 72h plan"
assert 'localStorage.setItem("his72-done"' in h72, "Missing his72-done setter in 72h plan"
assert 'data-key="his72-done"' in dash, "Missing his72-done data-key in dashboard"

print("ALL NUMBER CHECKS PASSED PERFECTLY!")
