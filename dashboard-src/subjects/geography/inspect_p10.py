import json
import re

with open("dashboard-src/subjects/geography/raw_pages.json", encoding="utf-8") as f:
    pages = json.load(f)

# Let's inspect page 10 where Q3 and Q4 are
p10 = pages[9]["text"]
print("=== Page 10 raw text ===")
print(p10[:1000])
