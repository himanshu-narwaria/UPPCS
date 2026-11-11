import json

def update_titles(path):
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    for c in data:
        if c["num"] == 29:
            c["title"] = "Transport in India"
        elif c["num"] == 31:
            c["title"] = "Indian Geography : Miscellaneous"
        elif c["num"] == 80:
            c["title"] = "World Transport"
        elif c["num"] == 83:
            c["title"] = "World Geography : Miscellaneous"
        elif c["num"] == 5:
            c["title"] = "Languages of India"
        elif c["num"] == 78:
            c["title"] = "Major Languages of the World"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"Updated titles in {path}")

update_titles("dashboard-src/subjects/geography/accurate_chapter_ranges.json")
update_titles("dashboard-src/subjects/geography/parsed_chapter_stats.json")
