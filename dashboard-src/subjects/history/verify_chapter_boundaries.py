import json, re

with open("dashboard-src/subjects/history/raw_pages.json", encoding="utf-8") as f:
    pages = json.load(f)

with open("dashboard-src/subjects/history/chapter_ledger.json", encoding="utf-8") as f:
    ledger = json.load(f)

# Let's inspect where the exact chapter title appears in the pages
corrected_ledger = []
for entry in ledger:
    ch_num = entry["num"]
    title = entry["title"]
    nominal_start = entry["nominal_start"]
    
    # search around nominal_start (-5 to +5)
    best_p = None
    # Look for exact or fuzzy title match
    clean_title = re.sub(r'[^a-zA-Z0-9\s]', ' ', title).strip().lower()
    words = [w for w in clean_title.split() if len(w) > 3]
    
    for p in range(max(1, nominal_start - 4), min(len(pages), nominal_start + 5) + 1):
        txt = pages[p-1]["text"]
        lines = [l.strip() for l in txt.split("\n")[:15]]
        for l in lines:
            l_clean = re.sub(r'[^a-zA-Z0-9\s]', ' ', l).strip().lower()
            if clean_title in l_clean:
                best_p = p
                break
            if words and sum(1 for w in words if w in l_clean) >= max(1, len(words) * 0.7):
                best_p = p
                break
        if best_p:
            break
            
    # If not found with header, use nominal_start
    final_start = best_p if best_p else nominal_start
    corrected_ledger.append({
        "num": ch_num,
        "title": title,
        "nominal": entry["nominal"],
        "nominal_start": nominal_start,
        "start": final_start
    })

# Check for monotonicity: each chapter start must be >= previous start
for i in range(1, len(corrected_ledger)):
    prev = corrected_ledger[i-1]
    curr = corrected_ledger[i]
    if curr["start"] <= prev["start"]:
        print(f"WARNING: Ch {curr['num']} ({curr['title']}) start {curr['start']} <= Ch {prev['num']} ({prev['title']}) start {prev['start']}")

with open("dashboard-src/subjects/history/corrected_ledger.json", "w", encoding="utf-8") as f:
    json.dump(corrected_ledger, f, indent=2)
print("Saved corrected_ledger.json")
