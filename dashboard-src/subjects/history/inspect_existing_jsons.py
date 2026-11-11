import json, os

for fn in ['accurate_ranges.json', 'latest_facts.json', 'repeated_facts.json', 'structured_all_chapters.json']:
    path = f"dashboard-src/subjects/history/{fn}"
    if os.path.exists(path):
        size = os.path.getsize(path)
        print(f"{fn}: size = {size} bytes")
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, list):
                print(f"  Type list, len = {len(data)}")
                if len(data) > 0:
                    print("  Sample item keys/data:", list(data[0].keys()) if isinstance(data[0], dict) else data[0])
            elif isinstance(data, dict):
                print(f"  Type dict, keys len = {len(data)}, first 5 keys: {list(data.keys())[:5]}")
