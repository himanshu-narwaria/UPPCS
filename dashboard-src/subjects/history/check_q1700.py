import json

with open("dashboard-src/subjects/history/parsed_uppsc_questions.json", encoding="utf-8") as f:
    qs = json.load(f)

with open("dashboard-src/subjects/history/raw_pages.json", encoding="utf-8") as f:
    pages = json.load(f)

for qid in ["q1700", "q2000"]:
    q = qs[qid]
    print(f"\n{qid}: ch={q['ch']}, exam={q['e']}, page={q['pdf_page']}")
    print(f"Stem: {q['s'][:100]}")
    p = pages[q['pdf_page'] - 1]
    # Check words
    words = [w for w in q['s'].split() if len(w) > 4]
    found = any(all(w in page['text'] for w in words[:3]) for page in pages)
    print("Found words in book?", found)
