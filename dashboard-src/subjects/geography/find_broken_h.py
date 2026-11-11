import re

with open("General_Geography_Part_3/geography-in-72h.html", encoding="utf-8") as f:
    text = f.read()

for m in re.finditer(r'.{0,60}href=["\']#h["\'].{0,60}', text):
    print("Match:", m.group(0))
