import json

with open("dashboard-src/subjects/geography/raw_pages.json", encoding="utf-8") as f:
    pages = json.load(f)

for p_idx in [8, 9, 10, 22, 23, 420, 421]:
    print(f"==================== PDF Page {p_idx} ====================")
    text = pages[p_idx - 1]["text"]
    lines = text.split("\n")
    for i, line in enumerate(lines[:35]):
        print(f"{i+1:2d}: {line}")
