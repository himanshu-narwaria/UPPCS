import json

with open("dashboard-src/subjects/geography/structured_all_chapters.json", encoding="utf-8") as f:
    chapters = json.load(f)

print(f"Total structured chapters: {len(chapters)}")
for c in chapters[:3]:
    print(f"\n=== Ch {c['num']}: {c['title']} ({c['section']}) ===")
    print(f"Gist: {c['gist']}")
    print(f"Focus items: {len(c.get('focus', []))}")
    for fc in c.get('focus', [])[:2]:
        print(f"  * {fc['cnt']}: {fc['fact'][:70]} [{fc['exam']}]")
    print(f"Topics: {len(c.get('topics', []))}")
    for t in c.get('topics', []):
        print(f"  Topic {t['id']}: {t['title']} ({len(t['points'])} points)")
        for pt in t['points'][:2]:
            print(f"    - (hot={pt['hot']}, asked={pt['asked']}): {pt['html'][:80]}...")

print("\nSample World Geography:")
for c in chapters[31:33]:
    print(f"\n=== Ch {c['num']}: {c['title']} ({c['section']}) ===")
    print(f"Gist: {c['gist']}")
    print(f"Focus items: {len(c.get('focus', []))}")
    print(f"Topics: {len(c.get('topics', []))}")
    for t in c.get('topics', []):
        print(f"  Topic {t['id']}: {t['title']} ({len(t['points'])} points)")
        for pt in t['points'][:2]:
            print(f"    - (hot={pt['hot']}, asked={pt['asked']}): {pt['html'][:80]}...")
