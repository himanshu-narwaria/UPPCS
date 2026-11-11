import re

with open("Economy 2024/economy-in-72h.html", encoding="utf-8") as f:
    text = f.read()

nav = re.search(r'<nav class="side" id="side"[^>]*>(.*?)</nav>', text, re.S).group(1)
for m in re.finditer(r'<div class="lb">([^<]+)</div>|<a href="#h(\d+)" data-v="h\d+"><span>\d+</span>([^<]+)</a>', nav):
    if m.group(1):
        print(f"--- PHASE: {m.group(1)} ---")
    else:
        print(f"h{m.group(2)}: {m.group(3)}")
