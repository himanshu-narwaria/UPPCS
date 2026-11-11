import json
import re

with open("dashboard-src/subjects/geography/raw_pages.json", encoding="utf-8") as f:
    pages = json.load(f)

for ch_name, p_start, p_end in [("Ch 5 Languages", 97, 98), ("Ch 34 Rocks", 470, 473), ("Ch 78 Languages (World)", 642, 643)]:
    print(f"==================== {ch_name} (pp. {p_start}-{p_end}) ====================")
    for p in range(p_start, p_end + 1):
        txt = pages[p-1]["text"]
        print(f"--- Page {p} ---")
        for line in txt.split("\n"):
            line_str = line.strip()
            if any(term in line_str for term in ["P.C.S.", "P.S.C.", "B.P.S.C", "M.P.", "I.A.S.", "U.P"]):
                print("   Exam line:", line_str)
