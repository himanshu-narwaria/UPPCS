import json, re

with open("Indian_Polity_2026/polity-in-72h.html", encoding="utf-8") as f:
    text = f.read()

m = re.search(r'<script id="pqd" type="application/json">(.*?)</script>', text, re.S)
pqd = json.loads(m.group(1))
print("Questions in polity 72h pqd:", len(pqd))

# Find all data-q references in ol.pq
all_referenced_qs = set()
for q_str in re.findall(r'<ol class="pq" data-q="([^"]+)"', text):
    all_referenced_qs.update(q_str.split(","))

print("Total unique question references in 72h:", len(all_referenced_qs))
print("Are all referenced questions in pqd?", all_referenced_qs.issubset(set(pqd.keys())))
print("Are all pqd questions referenced in 72h?", set(pqd.keys()).issubset(all_referenced_qs))
