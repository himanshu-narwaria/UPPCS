"""Check the writer agents' memory layer against the source.

Usage:  python ca_validate_memory.py            (all agents)
        python ca_validate_memory.py w3         (one agent)

Reads memory/<agent>.partNN.json files (each a JSON object: unit id -> entry) and checks:
  * every unit of the agent's chapters has exactly one entry, and no foreign ids;
  * the entry has the right fields for its kind (story units vs article/item units);
  * every number of two or more digits written in gist, facts, line, why and the correct MCQ
    option appears in that unit's source text (numbers cannot be invented);
  * MCQs have 4 distinct options, a valid answer index and a stem of reasonable length.
Exit code 1 on any error. Warnings (single-digit numbers not found) do not fail.
"""
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from ca_structure import AGENTS, block_text  # noqa: E402

NUM = re.compile(r"\d[\d,]*(?:\.\d+)?")
HINDI = re.compile(r"[ऀ-ॿ]")


def norm_num(n):
    return n.replace(",", "").rstrip(".")


def source_text(unit, src, arts, qa):
    if unit["kind"] == "story":
        return " ".join(qa[q]["q"] + " " + qa[q]["a"] + " " + (qa[q]["date"] or "") for q in unit["qa"]) + " " + unit["title"]
    a = arts[unit["article"]]
    return unit["title"] + " " + (unit.get("subtitle") or "") + " " + (unit.get("group") or "") + " " + \
        " ".join(block_text(a["blocks"][i]) for i in unit["blocks"])


def load_parts(agent):
    merged, errors = {}, []
    for p in sorted((HERE / "memory").glob(f"{agent}.part*.json")):
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
        except ValueError as e:
            errors.append(f"{p.name}: invalid JSON: {e}")
            continue
        for k, v in data.items():
            if k in merged:
                errors.append(f"{p.name}: duplicate unit {k}")
            merged[k] = v
    return merged, errors


def check(agent, units, src):
    arts = {a["id"]: a for a in src["articles"]}
    qa = {q["id"]: q for q in src["qa"]}
    mine = {u["id"]: u for u in units if u["ch"] in AGENTS[agent]}
    mem, errors = load_parts(agent)
    warnings = []
    missing = sorted(set(mine) - set(mem))
    extra = sorted(set(mem) - set(mine))
    if missing:
        errors.append(f"missing {len(missing)} units: {missing[:15]}")
    if extra:
        errors.append(f"foreign ids: {extra[:15]}")
    for uid, e in mem.items():
        u = mine.get(uid)
        if not u or not isinstance(e, dict):
            continue
        src_txt = source_text(u, src, arts, qa)
        src_nums = {norm_num(n) for n in NUM.findall(src_txt)}
        story = u["kind"] == "story"
        need = ["line", "priority"] if story else ["gist", "facts", "priority", "mcq"]
        for f in need:
            if f not in e:
                errors.append(f"{uid}: missing field '{f}'")
        if e.get("priority") not in (1, 2, 3):
            errors.append(f"{uid}: priority must be 1, 2 or 3")
        for f in ("hook", "trap"):
            if f in e and not isinstance(e[f], str):
                errors.append(f"{uid}: {f} must be a string")
        if not isinstance(e.get("hindi", []), list) or any(not HINDI.search(h) for h in e.get("hindi", [])):
            errors.append(f"{uid}: hindi must be a list of 'English (हिंदी)' strings")
        texts = []
        if story:
            texts.append(("line", e.get("line", "")))
        else:
            texts.append(("gist", e.get("gist", "")))
            facts = e.get("facts", [])
            if not isinstance(facts, list) or not 1 <= len(facts) <= 7:
                errors.append(f"{uid}: facts must be a list of 1-7 lines")
            texts += [("fact", f) for f in facts if isinstance(f, str)]
            mcqs = e.get("mcq", [])
            if not isinstance(mcqs, list) or len(mcqs) > 3:
                errors.append(f"{uid}: mcq must be a list of at most 3 questions")
                mcqs = []
            for i, m in enumerate(mcqs):
                o = m.get("o", [])
                if len(o) != 4 or len({x.strip().lower() for x in o}) != 4:
                    errors.append(f"{uid}: mcq {i + 1} needs 4 distinct options")
                    continue
                if m.get("k") not in (0, 1, 2, 3):
                    errors.append(f"{uid}: mcq {i + 1} answer index must be 0-3")
                    continue
                if len(m.get("q", "")) < 20:
                    errors.append(f"{uid}: mcq {i + 1} stem too short")
                texts.append(("mcq answer", o[m["k"]]))
                texts.append(("why", m.get("why", "")))
        for label, t in texts:
            for n in NUM.findall(t or ""):
                nn = norm_num(n)
                if nn in src_nums or nn.lstrip("0") in src_nums:
                    continue
                if len(nn.replace(".", "")) >= 2:
                    errors.append(f"{uid}: {label} has number {n} not in the source")
                else:
                    warnings.append(f"{uid}: {label} has number {n} not in the source")
    return errors, warnings, len(mine), len(mem)


def main():
    units = json.loads((HERE / "ca_units.json").read_text(encoding="utf-8"))
    src = json.loads((HERE / "ca_source.json").read_text(encoding="utf-8"))
    agents = sys.argv[1:] or list(AGENTS)
    failed = False
    for a in agents:
        errors, warnings, n_units, n_mem = check(a, units, src)
        print(f"{a}: {n_mem}/{n_units} units, {len(errors)} errors, {len(warnings)} warnings")
        for e in errors[:60]:
            print("  ERROR", e)
        for w in warnings[:15]:
            print("  warn ", w)
        failed |= bool(errors)
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
