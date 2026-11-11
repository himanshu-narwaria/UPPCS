import json

with open("dashboard-src/subjects/history/parsed_chapter_stats.json", encoding="utf-8") as f:
    stats = json.load(f)

for ch_num in [1, 2, 9, 16, 30, 41, 46, 52, 63, 85]:
    st = next(s for s in stats if s["num"] == ch_num)
    print(f"\n================ CHAPTER {ch_num}: {st['title']} ================")
    print(f"Pages: {st['pages']}, UPPSC PYQs: {st['uppsc_count']}")
    intro = st["intro"]
    print("Intro length:", len(intro))
    print("Intro first 500 chars:\n", intro[:500])
