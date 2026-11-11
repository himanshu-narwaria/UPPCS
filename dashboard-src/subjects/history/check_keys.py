import json

with open('dashboard-src/subjects/history/structured_all_chapters.json', 'r', encoding='utf-8') as f:
    struct = json.load(f)

print("First chapter structure:", struct[0].keys(), struct[0].get("ch_id"), struct[0].get("id"), struct[0].get("title"))
