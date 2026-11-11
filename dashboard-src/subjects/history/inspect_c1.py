with open("Indian_Polity_2026/polity-uppsc-full-notes.html", encoding="utf-8") as f:
    s = f.read()

import re
m = re.search(r'(<section class="view ch" id="c1".*?</section>)', s, re.S)
if m:
    ch1 = m.group(1)
    print("Length of c1:", len(ch1))
    print(ch1[:2500])
