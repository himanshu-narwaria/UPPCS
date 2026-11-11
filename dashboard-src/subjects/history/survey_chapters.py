import json, re

with open("dashboard-src/subjects/history/accurate_ranges.json", encoding="utf-8") as f:
    ranges = json.load(f)

with open("dashboard-src/subjects/history/raw_pages.json", encoding="utf-8") as f:
    pages = json.load(f)

with open("dashboard-src/subjects/history/parsed_uppsc_questions.json", encoding="utf-8") as f:
    qs = json.load(f)

def clean_text(t):
    t = re.sub(r'B–\d+ General Studies Indian History', '', t)
    t = re.sub(r'Indian History General Studies B–\d+', '', t)
    t = re.sub(r'Indian HistoryB–\d+', '', t)
    t = re.sub(r'click here -@freepdfhall', '', t)
    t = re.sub(r'search on TG-@freepdfhall', '', t)
    t = re.sub(r'\s+', ' ', t).strip()
    return t

print("Checking raw chapter notes for all modern chapters:")
for r in ranges:
    if 41 <= r["num"] <= 95:
        num = r["num"]
        title = r["title"]
        start_p = r["start"]
        next_idx = ranges.index(r) + 1
        end_p = ranges[next_idx]["start"] - 1 if next_idx < len(ranges) else len(pages)
        
        # text for this page range
        txt = "\n".join(pages[p-1]["text"] for p in range(start_p, end_p + 1))
        # Look for chapter title in text
        pos = txt.find(title)
        if pos == -1:
            # try fuzzy or first word
            first_w = title.split()[0]
            pos = txt.find(first_w)
            
        print(f"Ch {num:2d} ({start_p}-{end_p}): title '{title}' pos={pos}, total len={len(txt)}")
