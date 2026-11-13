"""Step 4: prove the three pages are complete and fit the dashboard.

Checks
  * Full notes: all 656 Q&As (question and answer, word for word), every source block's text,
    and every bold key fact (as a highlighted <b class="k">) appear.
  * Quick notes: one topic per study unit; Plan: every unit in exactly one Learn hour.
  * Practice bank: 4 distinct options, valid key; Q&A questions keep the book's answer as the key.
  * The dashboard's own parsers accept all three files.
Exit code 1 on any failure.
"""
import html
import json
import re
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "dashboard-src"))
sys.path.insert(0, str(HERE))
import build_dashboard as dash  # noqa: E402
from ca_render import FULL, QUICK, PLAN, OUT, bare, clean_answer  # noqa: E402

errors = []


def fail(msg):
    errors.append(msg)


def plain(s):
    s = re.sub(r"<script.*?</script>", " ", s, flags=re.S)
    s = re.sub(r"<style.*?</style>", " ", s, flags=re.S)
    s = html.unescape(re.sub(r"<[^>]+>", "", s))
    return re.sub(r"\s+", " ", s)


def squash(s):
    return re.sub(r"\s+", " ", s).strip()


def main():
    src = json.loads((HERE / "ca_source.json").read_text(encoding="utf-8"))
    units = json.loads((HERE / "ca_units.json").read_text(encoding="utf-8"))
    full = (OUT / FULL).read_text(encoding="utf-8")
    quick = (OUT / QUICK).read_text(encoding="utf-8")
    plan = (OUT / PLAN).read_text(encoding="utf-8")
    full_plain = plain(full)

    # 1. Q&A bank
    for q in src["qa"]:
        m = re.search(rf'<li class="pt" id="c1-{q["id"]}"><span class="q">(.*?)</span><span class="a">(.*?)</span></li>', full)
        if not m:
            fail(f"Q&A {q['id']} missing from full notes")
            continue
        if html.unescape(m.group(1)) != q["q"] or html.unescape(m.group(2)) != clean_answer(q["a"]):
            fail(f"Q&A {q['id']} text differs from the source")

    # 2. every block's text and every bold phrase
    bold_src = Counter()
    for a in src["articles"]:
        for b in a["blocks"]:
            if b["kind"] == "table":
                pieces = [squash("".join(t for t, _ in c)) for row in b["rows"] for c, *_ in row]
                bold_src.update(squash(t) for row in b["rows"] for c, *_ in row for t, bb in c if bb and t.strip())
            elif b["kind"] == "heading":
                # sub-headings become topic titles or group labels: check the words, any case
                h = squash("".join(t for t, _ in b["runs"]))
                if re.fullmatch(r"\(.*\)", h):
                    h = h[1:-1]          # a bracketed date line is shown as the item's subtitle
                if h.lower() not in full_plain.lower():
                    fail(f"{a['id']} p.{b['page']}: heading not found in full notes: {h[:70]!r}")
                pieces = []
            else:
                pieces = [squash("".join(t for t, _ in b["runs"]))]
                bold_src.update(squash(t) for t, bb in b["runs"] if bb and t.strip())
            for p in pieces:
                if p and p not in full_plain:
                    fail(f"{a['id']} p.{b['page']}: text not found in full notes: {p[:70]!r}")
    bold_full = Counter(squash(html.unescape(x)) for x in re.findall(r'<b class="k">(.*?)</b>', full))
    for t, n in bold_src.items():
        if bold_full[t] < n:
            fail(f"bold key fact shown {bold_full[t]} times, source has {n}: {t[:60]!r}")
    print(f"full notes: {len(src['qa'])} Q&As, {sum(bold_src.values())} bold key facts checked")

    # 3. quick notes and plan coverage
    anchors = re.findall(r'<article class="topic[^"]*" id="(c\d+-t\d+)"', quick)
    if len(anchors) != len(units) or len(set(anchors)) != len(units):
        fail(f"quick notes have {len(anchors)} topics for {len(units)} units")
    learn_part = plan.split('<p class="eyebrow">Hour ')
    seen = Counter()
    for part in learn_part[1:]:
        if "· Learn</p>" not in part[:40]:
            continue
        seen.update(re.findall(r'data-u="(u\d+)"', part))
    missing = [u["id"] for u in units if seen[u["id"]] != 1]
    if missing:
        fail(f"{len(missing)} units not in exactly one Learn hour: {missing[:10]}")

    # 4. practice bank
    q = json.loads(re.search(r'<script id="pqd" type="application/json">(.*?)</script>', full, re.S).group(1))
    qa = {x["id"]: x for x in src["qa"]}
    for pid, item in q.items():
        if len(item["o"]) != 4 or len({o.strip().lower() for o in item["o"]}) != 4:
            fail(f"{pid}: needs 4 distinct options")
        if not item["k"] or any(k not in range(4) for k in item["k"]):
            fail(f"{pid}: bad answer key")
        if item["h"].startswith("c1-q"):
            book = bare(clean_answer(qa[item["h"][3:]]["a"]))     # options drop a leading "At/In/The"
            if item["o"][item["k"][0]] != book:
                fail(f"{pid}: key is not the book's answer")
        if f'id="{item["h"]}"' not in full:
            fail(f"{pid}: note anchor {item['h']} missing")
    print(f"practice bank: {len(q)} questions checked")

    # 5. dashboard contract
    try:
        F = dash.parse_full(str(OUT / FULL))
        Q = dash.parse_quick(str(OUT / QUICK))
        P = dash.parse_72h(str(OUT / PLAN))
        dash.chapter_hours(F["chapters"], P, PLAN)
        print(f"dashboard: {len(F['chapters'])} chapters, {F['bank']} questions, {F['metadata']['priority_facts']} priority facts, "
              f"quick topics {sum(c['topics'] for c in Q['chapters'].values())}, plan key {P['key']}, exam {P['exam']}")
    except SystemExit as e:
        fail(f"dashboard parser rejected the files: {e}")

    for e in errors[:80]:
        print("ERROR", e)
    print("OK" if not errors else f"{len(errors)} errors")
    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
