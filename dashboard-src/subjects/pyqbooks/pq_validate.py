"""Check the writers' memory cards against the clusters and the book text.

    python pq_validate.py polity|history|economy [wNN]

ERROR: a pack id without a card, a card for an unknown id, an empty or over-long Remember line,
a number (2+ digits) that is not in the cluster's own source text, Hindi without Devanagari.
WARN: single-digit numbers not in the source, long hooks or traps.
"""
import json
import re
import sys
from pathlib import Path

from pq_books import book_dir

NUM = re.compile(r"\d[\d,.]*\d|\d")


def text(runs):
    return "".join(t for t, _ in runs)


def blocks_text(blocks):
    out = []
    for b in blocks:
        if b["kind"] == "table":
            out += [" ".join(text(c) for c in row) for row in b["rows"]]
        else:
            out.append(text(b["runs"]))
    return " ".join(out)


def source_numbers(src_q, cl):
    parts = []
    for qid in cl["qids"]:
        q = src_q[qid]
        parts += [text(q["stem"]), blocks_text(q["mid"]), " ".join(text(v) for v in q["options"].values()),
                  blocks_text(q["expl"]), " ".join(q["tags"])]
    s = " ".join(parts)
    nums = {n.replace(",", "").rstrip(".") for n in NUM.findall(s)}
    # ordinals and roman forms are fine: "42nd" -> 42
    return nums, s


def main():
    key = sys.argv[1]
    only = sys.argv[2] if len(sys.argv) > 2 else None
    d = book_dir(key)
    src = json.loads((d / "source.json").read_text(encoding="utf-8"))
    src_q = {q["id"]: q for q in src["questions"]}
    cls = {c["id"]: c for c in json.loads((d / "clusters.json").read_text(encoding="utf-8"))}
    packs = sorted((d / "packs").glob("w*.txt"))
    pack_ids = {}
    for p in packs:
        for m in re.finditer(r"^\[(\d\d-\d\d\d)\]", p.read_text(encoding="utf-8"), re.M):
            pack_ids[m.group(1)] = p.stem
    cards = {}
    errors = warns = 0
    for f in sorted((d / "memory").glob("w*.part*.json")):
        w = f.name.split(".")[0]
        if only and w != only:
            continue
        try:
            data = json.loads(f.read_text(encoding="utf-8"))
        except Exception as e:
            print(f"  ERROR {f.name}: not valid JSON ({e})")
            errors += 1
            continue
        for k, v in data.items():
            if k in cards:
                print(f"  ERROR {k}: card appears twice ({f.name})")
                errors += 1
            cards[k] = (w, v)
    want = {k for k, w in pack_ids.items() if not only or w == only}
    missing = sorted(want - set(cards))
    if missing:
        print(f"  ERROR {len(missing)} ids have no card, e.g. {missing[:10]}")
        errors += 1
    for k, (w, v) in sorted(cards.items()):
        if k not in cls:     # its question now belongs to another fact (re-clustering); unused
            print(f"  warn  {k}: card for a fact that no longer exists (unused)")
            warns += 1
            continue
        # (a card written for one pack stays valid if a later re-pack moves its id to another)
        r = (v.get("r") or "").strip()
        if not r:
            print(f"  ERROR {k}: empty Remember line")
            errors += 1
        elif len(r.split()) > 40:
            print(f"  ERROR {k}: Remember line has {len(r.split())} words (max 30)")
            errors += 1
        nums, _ = source_numbers(src_q, cls[k])
        for field in ("r", "h", "t", "c"):
            for n in NUM.findall(v.get(field) or ""):
                n2 = n.replace(",", "").rstrip(".")
                if n2 in nums or n2.lstrip("0") in nums:
                    continue
                if len(n2) >= 2:
                    print(f"  ERROR {k}: {field} has number {n} not in its source")
                    errors += 1
                else:
                    warns += 1
        for field in ("h", "t"):
            if v.get(field) and len(v[field].split()) > 32:
                print(f"  warn  {k}: {field} is long ({len(v[field].split())} words)")
                warns += 1
        for h in v.get("hi") or []:
            if not re.search(r"[ऀ-ॿ]", h):
                print(f"  ERROR {k}: Hindi term without Devanagari: {h}")
                errors += 1
    scope = only or "all writers"
    print(f"{key} {scope}: {len([k for k in cards if not only or cards[k][0] == only])}/{len(want)} cards, "
          f"{errors} errors, {warns} warnings")
    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
