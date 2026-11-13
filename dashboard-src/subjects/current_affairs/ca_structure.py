"""Step 2: turn ca_source.json into study units and write agent input packs.

Units
  * Chapter 1 (Points to Remember): one unit per story = a dated question plus its follow-ups.
  * Chapters 2-6: one unit per article (BookmanOldStyle title).
  * Chapters 7-10: one unit per news item = each sub-heading inside an article; ALL-CAPS headings
    (NATIONAL, INTERNATIONAL, INDIA, WORLD) are categories, and a heading that is only a date in
    brackets belongs to the heading before it.

Writes ca_units.json and packs/<agent>.txt (the text the writer agents read).
Run:  python ca_structure.py
"""
import json
import re
from collections import Counter, OrderedDict
from pathlib import Path

HERE = Path(__file__).resolve().parent
SRC = HERE / "ca_source.json"
OUT = HERE / "ca_units.json"
PACKS = HERE / "packs"
REGISTRY = HERE / "unit_ids.json"   # signature -> unit id, so ids survive extraction fixes

# Which writer agent handles which chapters (balanced by text volume).
AGENTS = OrderedDict([
    ("w1", [1, 6, 8]),
    ("w2", [2]),
    ("w3", [3]),
    ("w4", [4, 7]),
    ("w5", [5, 10]),
    ("w6", [9]),
])


def text_of(runs, mark=False):
    if mark:
        return "".join(f"**{t}**" if b and t.strip() else t for t, b in runs).strip()
    return "".join(t for t, _ in runs).strip()


def block_text(b, mark=False):
    if b["kind"] == "table":
        return "\n".join("| " + " | ".join(text_of(c, mark) for c, *_ in row) + " |" for row in b["rows"])
    return text_of(b["runs"], mark)


def is_category(h):
    letters = re.sub(r"[^A-Za-z]", "", h)
    return len(letters) >= 4 and letters.isupper() and h.strip().upper() in {
        "NATIONAL", "INTERNATIONAL", "INDIA", "WORLD", "STATE", "STATES"}


def split_items(article):
    """Chapters 7-10: one unit per sub-heading."""
    units, category, cur = [], None, None
    for b in article["blocks"]:
        if b["kind"] == "heading":
            h = text_of(b["runs"])
            if is_category(h):
                category = h.title()
                cur = None
                continue
            if re.fullmatch(r"\(.*\)", h) and cur is not None:
                cur["subtitle"] = h.strip("()")
                continue
            if cur is not None and not cur["blocks"] and cur.get("from_heading"):
                cur["title"] += " " + h        # two stacked headings name one item
                continue
            cur = {"title": h, "category": category, "blocks": [], "pages": [b["page"]], "from_heading": True}
            units.append(cur)
            continue
        if cur is None:
            cur = {"title": article["title"], "category": category, "blocks": [], "pages": [b["page"]]}
            units.append(cur)
        cur["blocks"].append(b)
        if b["page"] not in cur["pages"]:
            cur["pages"].append(b["page"])
    return [u for u in units if u["blocks"]]


def signature(u):
    """What a unit is, independent of its position: chapter, kind, parent article, title."""
    parent = u.get("group") if u["kind"] == "item" else ""
    return f"{u['ch']}|{u['kind']}|{parent or ''}|{u['title']}"


def signatures(units):
    seen = Counter()
    out = []
    for u in units:
        base = signature(u)
        out.append(f"{base}|{seen[base]}")
        seen[base] += 1
    return out


def assign_stable_ids(units):
    """Keep each unit's id across rebuilds; new units get the next free number."""
    reg = json.loads(REGISTRY.read_text(encoding="utf-8")) if REGISTRY.exists() else {}
    used = set(reg.values())
    nxt = max([int(v[1:]) for v in used] + [0]) + 1
    sigs = signatures(units)
    taken = {reg[s] for s in sigs if s in reg}
    # a cosmetic fix to a title ("LineShine : World's" -> "LineShine: World's", "EcoSensitive" ->
    # "Eco-Sensitive") keeps the unit's id
    def squash(x):
        return re.sub(r"[\s\-‐]+", "", x)
    loose = {}
    for s, v in reg.items():
        loose.setdefault(squash(s), v)
    for u, sig in zip(units, sigs):
        if sig not in reg and loose.get(squash(sig)) not in taken | {None}:
            reg[sig] = loose[squash(sig)]
            taken.add(reg[sig])
        if sig not in reg:
            while f"u{nxt:04d}" in used:
                nxt += 1
            reg[sig] = f"u{nxt:04d}"
            used.add(reg[sig])
        u["id"] = reg[sig]
    ids = [u["id"] for u in units]
    if len(set(ids)) != len(ids):
        raise SystemExit("unit id registry produced duplicate ids")
    REGISTRY.write_text(json.dumps(reg, ensure_ascii=False, indent=0), encoding="utf-8")


def main():
    src = json.loads(SRC.read_text(encoding="utf-8"))
    units = []
    # chapter 1 stories
    stories = OrderedDict()
    for q in src["qa"]:
        stories.setdefault(q["story"], []).append(q)
    last_date = None
    for sid, qs in stories.items():
        last_date = qs[0]["date"] or last_date     # undated stories belong to the last printed date
        units.append({"id": f"u{len(units) + 1:04d}", "ch": 1, "kind": "story", "group": qs[0]["category"],
                      "title": qs[0]["q"], "date": last_date, "pages": sorted({q["page"] for q in qs}),
                      "qa": [q["id"] for q in qs]})
    # chapters 2-10
    for a in src["articles"]:
        if a["ch"] <= 6:
            units.append({"id": f"u{len(units) + 1:04d}", "ch": a["ch"], "kind": "article", "group": a["section"],
                          "title": a["title"], "pages": a["pages"], "article": a["id"],
                          "blocks": list(range(len(a["blocks"])))})
        else:
            idx = {id(b): i for i, b in enumerate(a["blocks"])}
            for it in split_items(a):
                units.append({"id": f"u{len(units) + 1:04d}", "ch": a["ch"], "kind": "item",
                              "group": a["title"] if a["title"] != "Introduction" else None,
                              "category": it["category"], "title": it["title"], "subtitle": it.get("subtitle"),
                              "pages": it["pages"], "article": a["id"],
                              "blocks": [idx[id(b)] for b in it["blocks"]]})
    # every block of every article must belong to exactly one unit
    used = Counter()
    for u in units:
        for i in u.get("blocks", []):
            used[(u["article"], i)] += 1
    arts = {a["id"]: a for a in src["articles"]}
    lost = []
    for a in src["articles"]:
        for i, b in enumerate(a["blocks"]):
            if b["kind"] == "heading":
                continue
            if used[(a["id"], i)] != 1:
                lost.append((a["id"], i, used[(a["id"], i)]))
    if lost:
        raise SystemExit(f"{len(lost)} blocks are not in exactly one unit: {lost[:10]}")
    assign_stable_ids(units)
    OUT.write_text(json.dumps(units, ensure_ascii=False, indent=1), encoding="utf-8")

    # agent packs
    qa = {q["id"]: q for q in src["qa"]}
    PACKS.mkdir(exist_ok=True)
    for agent, chapters in AGENTS.items():
        lines = []
        for u in units:
            if u["ch"] not in chapters:
                continue
            head = f"[{u['id']}] Ch{u['ch']} · {u['title']}"
            if u.get("subtitle"):
                head += f" ({u['subtitle']})"
            meta = [x for x in (u.get("group"), u.get("category"), u.get("date")) if x]
            lines.append(f"\n{head}\n  context: {' · '.join(meta) or '-'} · PDF p. {', '.join(map(str, u['pages']))}")
            if u["kind"] == "story":
                for qid in u["qa"]:
                    q = qa[qid]
                    lines.append(f"  Q{qid[1:]}: {q['q']}  =>  A: {q['a']}")
            else:
                a = arts[u["article"]]
                for i in u["blocks"]:
                    b = a["blocks"][i]
                    prefix = "  - " if b["kind"] == "li" and b.get("level") == 1 else ("    · " if b["kind"] == "li" else "  ")
                    lines.append(prefix + block_text(b, mark=True).replace("\n", "\n  "))
        (PACKS / f"{agent}.txt").write_text("\n".join(lines).strip() + "\n", encoding="utf-8")
    per = Counter(u["ch"] for u in units)
    sizes = {a: (PACKS / f"{a}.txt").stat().st_size for a in AGENTS}
    print("units per chapter:", dict(sorted(per.items())), "total", len(units))
    print("pack sizes (bytes):", sizes)


if __name__ == "__main__":
    main()
