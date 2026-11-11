with open("Indian_Polity_2026/polity-uppsc-full-notes.html", encoding="utf-8") as f:
    s = f.read()

import re
m = re.search(r'(<section class="view[^"]*" id="practice".*?</section>)', s, re.S)
if m:
    print(m.group(1)[:2000])
