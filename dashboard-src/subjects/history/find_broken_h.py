with open("Indian_History_Part_2/history-in-72h.html", encoding="utf-8") as f:
    text = f.read()

import re
matches = [m.start() for m in re.finditer(r'href=["\']#h["\']', text)]
print(f"Found {len(matches)} matches of href='#h':")
for idx in matches:
    print(text[max(0, idx - 80):min(len(text), idx + 80)])
