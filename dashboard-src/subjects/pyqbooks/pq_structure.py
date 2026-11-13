"""Step 2: group each book's questions into fact clusters and write the writer packs.

    python pq_structure.py polity|history|economy [writers]

A cluster is one fact the exams keep asking: a question plus every later question whose
explanation says "See the explanation of the above question", plus same-worded questions of the
same chapter. Each cluster gets one memory card (written by a writer agent from packs/wNN.txt).
Priority comes from the papers that asked it:
  1 = asked in a UP paper and in 2+ papers overall, or in 3+ papers   ("Must know")
  2 = asked in a UP paper, or in 2+ papers
  3 = asked once, outside UP
Writes <book>/clusters.json and <book>/packs/wNN.txt.
"""
import json
import re
import sys
from collections import OrderedDict

from pq_books import BOOKS, book_dir


def text(runs):
    return "".join(t for t, _ in runs).strip()


def blocks_text(blocks, limit=None):
    out = []
    for b in blocks:
        if b["kind"] == "table":
            out += ["| " + " | ".join(text(c) for c in row) + " |" for row in b["rows"]]
        else:
            out.append(text(b["runs"]))
    s = "\n".join(x for x in out if x)
    # say plainly that the brief, not the book, is shortened (writers read a bare "…" as a cut-off book)
    return s if limit is None or len(s) <= limit else s[:limit].rsplit(" ", 1)[0] + " … [shortened in this brief; the book continues]"


def norm(s):
    return re.sub(r"[^a-z0-9]", "", s.lower())


def paper(tag):
    """'U.P.P.C.S. (Pre) 2016' -> a key for one exam paper (spacing and dots ignored)."""
    return re.sub(r"[^A-Z0-9]", "", tag.upper())


def clusters_for(src):
    qs = src["questions"]
    by_id = {q["id"]: q for q in qs}
    parent = {q["id"]: q["id"] for q in qs}

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(a, b):
        ra, rb = find(a), find(b)
        if ra != rb:
            # the earlier question (the one with the explanation) stays the head
            if ra > rb:
                ra, rb = rb, ra
            parent[rb] = ra
    for q in qs:
        if q.get("see") and q["see"] in by_id:
            union(q["see"], q["id"])
    seen = {}
    for q in qs:
        # the statements count too: "Consider the following statements" + "1 and 2 only" alone
        # would join unrelated questions
        key = (q["ch"], norm(text(q["stem"]) + blocks_text(q["mid"])) + "|"
               + norm(text(q["options"].get(q["ans"][:1], []))))
        if len(key[1]) > 25:
            if key in seen:
                union(seen[key], q["id"])
            else:
                seen[key] = q["id"]
    groups = OrderedDict()
    for q in qs:
        groups.setdefault(find(q["id"]), []).append(q)
    out = []
    for head, members in groups.items():
        h = by_id[head]
        tags = [t for q in members for t in q["tags"]]
        papers = sorted({paper(t) for t in tags})
        up_papers = sorted({paper(t) for q in members for t in q["tags"] if q["up"] and re.match(r"^\W*(?:\d+\w*\s*(?:to\s*\d+\w*)?\s*)?U\.?\s?P(?!\.?\s?S\.?\s?C)", t)})
        n, nu = len(papers), len(up_papers) or (1 if any(q["up"] for q in members) else 0)
        pri = 1 if (nu and n >= 2) or n >= 3 else 2 if (nu or n >= 2) else 3
        years = sorted({y for q in members for y in q["years"]})
        out.append({"id": f"{h['ch']:02d}-{h['num']:03d}", "ch": h["ch"], "head": head, "qids": [q["id"] for q in members],
                    "papers": n, "up": nu, "priority": pri, "years": years, "page": h["page"],
                    "tags": tags})
    return out


def pack_entry(src_q, cl, chapters):
    h = src_q[cl["head"]]
    ch = chapters[cl["ch"] - 1]["title"]
    opts = " ".join(f"({k}) {text(v)}" for k, v in h["options"].items())
    ans = h["ans"]
    ans_txt = "; ".join(f"({a}) {text(h['options'].get(a, []))}" for a in re.findall(r"[a-e]", ans)) or ans
    lines = [f"[{cl['id']}] Ch{cl['ch']} · {ch} · asked in {cl['papers']} paper(s): " + "; ".join(cl["tags"][:6])
             + (" …" if len(cl["tags"]) > 6 else "")]
    lines.append("Q: " + text(h["stem"]))
    mid = blocks_text(h["mid"], 600)
    if mid:
        lines.append("   " + mid.replace("\n", "\n   "))
    if opts:
        lines.append("Options: " + opts)
    lines.append("Answer: " + (ans_txt if ans else "not printed in the book"))
    for qid in cl["qids"][1:4]:
        o = src_q[qid]
        a2 = "; ".join(text(o["options"].get(a, [])) for a in re.findall(r"[a-e]", o["ans"])) or o["ans"]
        lines.append(f"Also asked: {text(o['stem'])[:120]} -> {a2[:70]}")
    ex = blocks_text(h["expl"], 420)
    if ex:
        lines.append("Explanation: " + ex.replace("\n", " / "))
    return "\n".join(lines)


def main():
    key = sys.argv[1]
    # the cards in memory/ were written per pack, so the pack split must stay the same
    writers = int(sys.argv[2]) if len(sys.argv) > 2 else BOOKS[key]["writers"]
    d = book_dir(key)
    src = json.loads((d / "source.json").read_text(encoding="utf-8"))
    cls = clusters_for(src)
    (d / "clusters.json").write_text(json.dumps(cls, ensure_ascii=False, indent=0), encoding="utf-8")
    src_q = {q["id"]: q for q in src["questions"]}
    entries = [(cl, pack_entry(src_q, cl, src["chapters"])) for cl in cls]
    total = sum(len(e) for _, e in entries)
    packs = d / "packs"
    packs.mkdir(exist_ok=True)
    for f in packs.glob("w*.txt"):
        f.unlink()
    # split by size, never inside a chapter boundary's middle more than needed: consecutive runs
    per = total / writers
    k, acc, cur = 1, 0, []
    out = []
    for cl, e in entries:
        if acc > per * k and k < writers:
            out.append(cur)
            cur, k = [], k + 1
        cur.append(e)
        acc += len(e)
    out.append(cur)
    for i, chunk in enumerate(out, 1):
        (packs / f"w{i:02d}.txt").write_text("\n\n".join(chunk) + "\n", encoding="utf-8")
    pri = [c["priority"] for c in cls]
    print(f"{key}: {len(src['questions'])} questions -> {len(cls)} clusters "
          f"(must know {pri.count(1)}, useful {pri.count(2)}, other {pri.count(3)}); "
          f"repeated (2+ papers) {sum(1 for c in cls if c['papers'] >= 2)}")
    print("packs:", {f"w{i:02d}": (len(c), sum(len(x) for x in c)) for i, c in enumerate(out, 1)})


if __name__ == "__main__":
    main()
