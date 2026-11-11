import json, re

with open("dashboard-src/subjects/history/raw_pages.json", encoding="utf-8") as f:
    pages = json.load(f)

with open("dashboard-src/subjects/history/chapter_ledger.json", encoding="utf-8") as f:
    ledger = json.load(f)

print(f"{'No':2} | {'Title':42} | {'TOC p':5} | {'Heading found on p.'}")
print("-" * 75)

accurate_ranges = []
for entry in ledger:
    ch_num = entry["num"]
    title = entry["title"]
    nominal_start = entry["nominal_start"]
    nominal_end = entry["nominal_end"]
    
    # Check lines on nominal_start - 1, nominal_start, nominal_start + 1
    found_p = None
    title_words = [w.lower() for w in re.sub(r'[^a-zA-Z0-9\s]', ' ', title).split() if len(w) > 3]
    
    for p in [nominal_start, nominal_start - 1, nominal_start + 1]:
        if 1 <= p <= len(pages):
            txt = pages[p-1]["text"]
            lines = [l.strip() for l in txt.split("\n")[:15]]
            for l in lines:
                l_low = l.lower()
                if title.lower() in l_low or (title_words and sum(1 for w in title_words if w in l_low) >= max(1, len(title_words) * 0.7)):
                    found_p = p
                    break
        if found_p:
            break
            
    p_use = found_p if found_p else nominal_start
    accurate_ranges.append({
        "num": ch_num,
        "title": title,
        "start": p_use,
        "nominal_start": nominal_start,
        "nominal_end": nominal_end
    })
    print(f"{ch_num:2d} | {title[:42]:42} | {nominal_start:5d} | {p_use}")

with open("dashboard-src/subjects/history/accurate_ranges.json", "w", encoding="utf-8") as f:
    json.dump(accurate_ranges, f, indent=2)
