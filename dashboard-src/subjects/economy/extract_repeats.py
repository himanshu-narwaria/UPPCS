import re
import json

with open("Economy 2024/economy-uppsc-full-notes.html", "r", encoding="utf-8") as f:
    fc = f.read()

rep_sec = re.search(r'<section class="view" id="repeated"[^>]*>(.*?)</section>', fc, re.S).group(1)

# Each repeated fact item:
matches = re.findall(
    r'<li><details><summary><span class="t">(.*?)</span><span class="ps"><span class="p up">×(\d+)</span></span></summary><div class="yrs"><div>(.*?)</div><a href="#([^"]+)">([^<]+)</a></div></details></li>',
    rep_sec,
    re.S
)

print(f"Matched {len(matches)} repeated items.")

repeats_data = []
for fact, cnt, papers, anc, link_txt in matches:
    repeats_data.append({
        "fact": fact.strip(),
        "count": int(cnt),
        "papers": papers.strip(),
        "anchor": anc.strip(),
        "link_text": link_txt.strip()
    })

with open("dashboard-src/subjects/economy/extracted_repeated_facts.json", "w", encoding="utf-8") as f:
    json.dump(repeats_data, f, ensure_ascii=False, indent=2)

print("Saved to dashboard-src/subjects/economy/extracted_repeated_facts.json")
