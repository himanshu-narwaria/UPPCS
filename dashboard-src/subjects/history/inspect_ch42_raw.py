import json

with open("dashboard-src/subjects/history/raw_pages.json", encoding="utf-8") as f:
    pages = json.load(f)

# Inspect Chapter 42 (pp. 358-362)
ch42_text = "\n".join(pages[p-1]["text"] for p in range(358, 363))
print("Ch 42 first 1500 chars:")
print(ch42_text[:1500])
