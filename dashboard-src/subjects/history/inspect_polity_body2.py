with open("Indian_Polity_2026/polity-in-72h.html", encoding="utf-8") as f:
    text = f.read()

import re
m = re.search(r'</style></head><body>(.*?)<main class="main">', text, re.S)
if m:
    print("BODY TO MAIN:")
    print(m.group(1)[:1000])
    print("...")
    print(m.group(1)[-500:])
