"""Step 5: prove a book's three pages are complete and fit the dashboard.

    python pq_verify.py polity|history|economy

  * Full notes: every question of the book (all exams) has its card (by anchor), its question text,
    every option and the book's answer.
  * Quick notes: one line per fact cluster; Plan: every cluster in exactly one Learn hour.
  * Practice bank: valid options and keys; the key is the book's answer.
  * The dashboard's own parsers accept all three files.
Exit code 1 on any failure.
"""
import html
import json
import re
import sys
from collections import Counter

from pq_books import BOOKS, ROOT, book_dir

sys.path.insert(0, str(ROOT / "dashboard-src"))
import build_dashboard as dash  # noqa: E402

errors = []


def fail(msg):
    errors.append(msg)


def squash(s):
    return re.sub(r"\s+", " ", s).strip()


def plain(s):
    return squash(html.unescape(re.sub(r"<[^>]+>", "", s)))


def text(runs):
    return "".join(t for t, _ in runs).strip()


def main():
    key = sys.argv[1]
    book = BOOKS[key]
    d = book_dir(key)
    src = json.loads((d / "source.json").read_text(encoding="utf-8"))
    clusters = json.loads((d / "clusters.json").read_text(encoding="utf-8"))
    full_name, quick_name, plan_name = book["files"]
    full = (book["out"] / full_name).read_text(encoding="utf-8")
    quick = (book["out"] / quick_name).read_text(encoding="utf-8")
    plan_json = json.loads((d / "plan.json").read_text(encoding="utf-8"))

    # full notes: each question card holds its text, options and answer
    cards = dict(re.findall(r'<article class="topic qcard" id="(c\d+-t\d+)"[^>]*>(.*?)</article>', full, re.S))
    for q in src["questions"]:
        aid = f'c{q["ch"]}-t{q["num"]}'
        body = cards.get(aid)
        if body is None:
            fail(f"{q['id']} ({aid}): no card in the full notes")
            continue
        flat = plain(body)
        if squash(text(q["stem"]))[:120] not in flat:
            fail(f"{q['id']}: question text missing")
        for k, v in q["options"].items():
            if squash(text(v)) and squash(text(v)) not in flat:
                fail(f"{q['id']}: option ({k}) missing")
        for a in re.findall(r"[a-e]", q["ans"]):
            if f"({a})" not in flat.split("Answer:", 1)[-1][:400]:
                fail(f"{q['id']}: answer ({a}) not shown")
    if len(cards) != len(src["questions"]):
        fail(f"full notes have {len(cards)} question cards, the book has {len(src['questions'])}")

    # quick notes: one line per cluster
    heads = {c["head"] for c in clusters}
    anchors = set(re.findall(r'<article class="topic" id="(c\d+-t\d+)"', quick))
    want = {f'c{q["ch"]}-t{q["num"]}' for q in src["questions"] if q["id"] in heads}
    if want - anchors:
        fail(f"quick notes miss {len(want - anchors)} facts, e.g. {sorted(want - anchors)[:5]}")

    # plan: every cluster in exactly one learn hour
    seen = Counter(c for h in plan_json for c in h["clusters"])
    if set(seen) != {c["id"] for c in clusters} or any(v != 1 for v in seen.values()):
        fail("the 72h plan does not hold every fact exactly once")

    # practice bank
    pq = json.loads(re.search(r'<script id="pqd" type="application/json">(.*?)</script>', full, re.S).group(1))
    by_anchor = {f'c{q["ch"]}-t{q["num"]}': q for q in src["questions"]}
    for pid, item in pq.items():
        q = by_anchor[item["h"]]
        book_dupes = len({squash(text(v)).lower() for v in q["options"].values()}) != len(q["options"])
        if len(item["o"]) < 2 or (len({o.strip().lower() for o in item["o"]}) != len(item["o"]) and not book_dupes):
            fail(f"{pid}: options are not distinct")     # (a misprint in the book itself is kept, e.g. p117)
        if not item["k"] or any(k not in range(len(item["o"])) for k in item["k"]):
            fail(f"{pid}: bad key")
        keys = sorted(q["options"])
        if sorted(keys[k] for k in item["k"]) != sorted(re.findall(r"[a-e]", q["ans"])):
            fail(f"{pid}: key is not the book's answer")

    # the dashboard's parsers
    try:
        F = dash.parse_full(str(book["out"] / full_name))
        Q = dash.parse_quick(str(book["out"] / quick_name))
        P = dash.parse_72h(str(book["out"] / plan_name))
        dash.chapter_hours(F["chapters"], P, plan_name)
        print(f"dashboard: {len(F['chapters'])} chapters, {F['bank']} questions, {len(F['repeats'])} repeated facts, "
              f"quick chapters {len(Q['chapters'])}, plan key {P['key']}, exam {P['exam']}")
    except SystemExit as e:
        fail(f"dashboard parser: {e}")
    print(f"{key}: {len(src['questions'])} questions checked in the full notes, {len(pq)} practice questions, "
          f"{len(clusters)} facts in quick notes and plan")
    if errors:
        for e in errors[:40]:
            print("ERROR", e)
        print(f"{len(errors)} errors")
        sys.exit(1)
    print("OK")


if __name__ == "__main__":
    main()
