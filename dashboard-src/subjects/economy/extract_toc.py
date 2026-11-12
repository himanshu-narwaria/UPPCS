import re
import json

with open("Economy 2024/economy-uppsc-full-notes.html", "r", encoding="utf-8") as f:
    fc = f.read()

home_m = re.search(r'<section class="view" id="home">(.*?)</section>', fc, re.S).group(1)
toc_items = re.findall(
    r'<li><a href="#c(\d+)"><span class="no">(\d+)</span><span class="nm">([^<]+)</span>(?:<span class="p up">([^<]+)</span>)?<span class="q">(\d+) UPPSC PYQs</span></a></li>',
    home_m
)

print(f"Matched {len(toc_items)} TOC items.")
toc_data = []
for ch_n, no, nm, badge, q_cnt in toc_items:
    toc_data.append({
        "num": int(ch_n),
        "title": nm.strip(),
        "badge": badge.strip() if badge else None,
        "questions": int(q_cnt)
    })
    print(f"  Ch {ch_n:2s}: {nm:40s} | badge: {str(badge):15s} | questions: {q_cnt}")

total_q = sum(item["questions"] for item in toc_data)
print(f"Total questions in TOC: {total_q}")

with open("dashboard-src/subjects/economy/extracted_toc_data.json", "w", encoding="utf-8") as f:
    json.dump(toc_data, f, ensure_ascii=False, indent=2)

print("Saved to dashboard-src/subjects/economy/extracted_toc_data.json")
