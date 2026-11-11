import json
import re

with open("dashboard-src/subjects/geography/raw_pages.json", encoding="utf-8") as f:
    pages = json.load(f)

def is_uppsc_new(line):
    if re.search(r'\b(Uttarakhand|U\.?K\.?)\b', line, re.I):
        return False
    # Pattern 1: UP followed by PCS / PSC / etc.
    if re.search(r'\bU\.?\s*P\.?\s*(P\.?C\.?S|P\.?S\.?C|Lower|R\.?O|A\.?R\.?O|U\.?D\.?A|L\.?D\.?A|G\.?I\.?C|G\.?D\.?C|B\.?E\.?O|R\.?I)\b', line, re.I):
        return True
    # Pattern 2: UPPCS / UPPSC / etc.
    if re.search(r'\b(UPPCS|UPPSC|U\.?P\.?P\.?C\.?S|U\.?P\.?P\.?S\.?C)\b', line, re.I):
        return True
    return False

all_tags = []
for p in pages:
    txt = p["text"]
    # Join split UP
    txt_norm = re.sub(r'U\.?\s*P\.?\s*\n\s*\.?', 'U.P.', txt)
    for line in txt_norm.split("\n"):
        line_clean = line.strip()
        if is_uppsc_new(line_clean) and re.search(r'19\d\d|20[0-2]\d', line_clean):
            all_tags.append(line_clean)

print(f"Total UPPSC exam tags with new regex: {len(all_tags)}")
