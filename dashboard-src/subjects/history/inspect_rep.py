import re

with open('Environment_2025/environment-2025-uppsc-quick-notes.html', 'r', encoding='utf-8') as f:
    text = f.read()

rep_m = re.search(r'<section class="view" id="repeated".*?</section>', text, re.S)
if rep_m:
    rep_html = rep_m.group(0)
    print("rep_html length:", len(rep_html))
    print(rep_html[:1200])
    rows = re.findall(r'<li><details>.*?</details></li>', rep_html, re.S)
    print("Total rows:", len(rows))
    print("Sample row 1:", rows[0])
    print("Sample row 2:", rows[1])
    print("Sample row 3:", rows[2])
