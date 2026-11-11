import json
import re

with open("dashboard-src/subjects/geography/raw_pages.json", encoding="utf-8") as f:
    pages = json.load(f)

# Normalize line breaks inside exam tags
# Replace things like:
# 'U.P\n.P.C.S.' -> 'U.P.P.C.S.'
# 'U.P.\n.P.C.S.' -> 'U.P.P.C.S.'
# 'M.P\n.P.C.S.' -> 'M.P.P.C.S.'

all_tags = []
for p in pages:
    txt = p["text"]
    # Join split UP
    txt_norm = re.sub(r'U\.?\s*P\.?\s*\n\s*\.?', 'U.P.', txt)
    txt_norm = re.sub(r'M\.?\s*P\.?\s*\n\s*\.?', 'M.P.', txt_norm)
    txt_norm = re.sub(r'B\.?\s*P\.?\s*\n\s*\.?', 'B.P.', txt_norm)
    
    for line in txt_norm.split("\n"):
        line_clean = line.strip()
        if re.search(r'\b(U\.?P\.?P?\.?C\.?S|U\.?P\.?\s*P\.?S\.?C|U\.?P\.?\s*Lower|U\.?P\.?\s*R\.?O|U\.?P\.?\s*A\.?R\.?O|U\.?P\.?\s*U\.?D\.?A|U\.?P\.?\s*L\.?D\.?A|U\.?P\.?\s*G\.?I\.?C|U\.?P\.?\s*G\.?D\.?C|U\.?P\.?\s*B\.?E\.?O|U\.?P\.?\s*R\.?I)\b', line_clean, re.I):
            if not re.search(r'Uttarakhand|U\.?K', line_clean, re.I):
                if re.search(r'19\d\d|20[0-2]\d', line_clean):
                    all_tags.append(line_clean)

print(f"Total normalized UPPSC exam tags found: {len(all_tags)}")
