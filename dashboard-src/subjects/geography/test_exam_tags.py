import json
import re

with open("dashboard-src/subjects/geography/raw_pages.json", encoding="utf-8") as f:
    pages = json.load(f)

# Concatenate text with normalized spaces where appropriate, or inspect lines
sample_matches = []
all_tags = []

for p in pages:
    txt = p["text"]
    # Look for UPPSC lines
    # Match lines containing UP or PCS or GIC or BEO or RO/ARO or UDA/LDA
    for line in txt.split("\n"):
        line_clean = line.strip()
        if re.search(r'\b(U\.?P|U\.?P\.?P?\.?C\.?S|RO/?ARO|UDA/?LDA|Lower|GIC|BEO|RI)\b', line_clean, re.I):
            # Check if Uttarakhand
            if not re.search(r'Uttarakhand|U\.?K', line_clean, re.I):
                if re.search(r'19\d\d|20[0-2]\d', line_clean):
                    all_tags.append(line_clean)

print(f"Total potential UPPSC exam tags found: {len(all_tags)}")
print("Sample 25 tags:")
for t in all_tags[:25]:
    print("  ", t)
