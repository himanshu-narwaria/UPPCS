"""Evidence-derived invariants for the active Polity study files."""
from collections import Counter, defaultdict
from html.parser import HTMLParser
import html
import json
from pathlib import Path
import re
import subprocess

from build_polity_data import CHAPTER_SPECS
from coverage_audit import build_ledger, read, write_report
from source_model import UP

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
FOLDER = ROOT / "Indian_Polity_and_Governance"
FILENAMES = ["polity-uppsc-full-notes.html", "polity-uppsc-quick-notes.html", "polity-in-72h.html"]


class Markup(HTMLParser):
    def __init__(self, text):
        super().__init__(convert_charrefs=True)
        self.ids, self.anchors, self.handlers, self.external_loads, self.target_blank, self.details = [], [], [], [], [], []
        self.feed(text)

    def handle_starttag(self, tag, attributes):
        data = dict(attributes)
        if "id" in data:
            self.ids.append(data["id"])
        if tag == "a" and data.get("href"):
            self.anchors.append(data["href"])
            if data.get("target") == "_blank":
                self.target_blank.append(data)
        if tag == "details":
            self.details.append(data)
        self.handlers.extend(name for name in data if re.fullmatch(r"on[a-z]+", name))
        if tag in ("script", "img", "iframe", "link"):
            self.external_loads.extend(value for name,value in data.items() if name in ("src", "href") and re.match(r"https?://", value or ""))


def validate():
    ledger = build_ledger()
    source, bank, review, chapters, repeats, latest = (read(name) for name in
        ("all_source_questions.json", "parsed_uppsc_questions.json", "review_questions.json", "structured_all_chapters.json", "repeated_facts.json", "latest_facts.json"))
    source_by_id = {q["id"]: q for q in source}
    assert len(source_by_id) == len(source)
    review_ids = {q["id"] for q in review}
    source_up = {q["id"] for q in source if q["uppsc_exams"]}
    bank_source_ids = {q["source_id"] for q in bank.values()}
    assert not bank_source_ids & review_ids
    assert bank_source_ids | review_ids == source_up
    assert {c["num"] for c in chapters} == {c[0] for c in CHAPTER_SPECS}
    for ch in chapters:
        assert len(ch["topics"][0]["points"]) == 4 and len(ch["recall"]) == 3
        assert ch["comparison"] and ch["confusion"]
    for qid, q in bank.items():
        original = source_by_id[q["source_id"]]
        assert not original["review"] and q["s"].strip()
        assert len(q["o"]) == 4 and all(q["o"]) and q["k"]
        assert all(0 <= k < len(q["o"]) for k in q["k"])
        assert html.unescape(q["s"]) == original["s"]
        assert [html.unescape(x) for x in q["o"]] == original["o"]
        assert q["k"] == original["k"] and html.unescape(q["f"]) == original["f"]
        assert q["n"] == len(set(q["exams"])) and all(UP.search(exam) for exam in q["exams"])
        assert q["y"] == max(int(re.search(r"\b(?:19|20)\d{2}\b", exam).group(0)) for exam in q["exams"])
        assert q["pages"] == original["pages"] and all(1 <= p <= ledger["counts"]["file_pages"] for p in q["pages"])
        assert q["key_status"] == "book key; not independently verified as official"
    assert {r["question_id"] for r in repeats} == {qid for qid,q in bank.items() if q["n"] >= 2}
    assert {r["question_id"] for records in latest.values() for r in records} == {qid for qid,q in bank.items() if q["y"] >= 2021}
    for r in repeats + [item for records in latest.values() for item in records]:
        q = bank[r["question_id"]]
        assert q["s"] in r["fact"] and q["f"] == r["explanation"]
        assert r["count"] == q["n"]
    # Real extraction regressions: resets, absent punctuation, and no space.
    assert source_by_id["src-c1-item9"]["source_no"] == 1
    assert source_by_id["src-c26-item44"]["s"].startswith("Consider the following statements")
    assert "BHARATPOL" in source_by_id["src-c42-item113"]["s"]
    assert source_by_id["src-c42-item113"]["source_no"] == 113
    # The two match-list questions must preserve list labels in the stem.
    for sid in ("src-c25-item87", "src-c42-item121"):
        assert "(a)" in source_by_id[sid]["s"] and len(source_by_id[sid]["o"]) == 4
    rendered = {name: (FOLDER / name).read_text(encoding="utf-8") for name in FILENAMES}
    doms = {name: Markup(text) for name,text in rendered.items()}
    for name, markup in doms.items():
        text = rendered[name]
        assert len(markup.ids) == len(set(markup.ids)), f"Duplicate id in {name}"
        assert not markup.handlers and not markup.external_loads
        assert not re.search(r'href\s*=\s*["\']javascript:', text, re.I)
        assert all({"noopener", "noreferrer"} <= set(link.get("rel", "").split()) for link in markup.target_blank)
        for href in markup.anchors:
            if re.match(r"(?:https?:|mailto:|tel:)", href):
                continue
            path, sep, anchor = href.partition("#")
            target_path = (FOLDER / path).resolve() if path else FOLDER / name
            assert target_path.exists(), f"Missing file: {name} -> {href}"
            if sep and anchor and target_path.suffix == ".html":
                target_dom = doms.get(target_path.name) or Markup(target_path.read_text(encoding="utf-8"))
                assert anchor in target_dom.ids, f"Broken anchor: {name} -> {href}"
        for attributes, code in re.findall(r"<script\b([^>]*)>(.*?)</script>", text, re.S):
            if "application/json" in attributes:
                continue
            check = subprocess.run(["node", "--check"], input=code, text=True, capture_output=True, encoding="utf-8")
            assert check.returncode == 0, f"JavaScript syntax in {name}: {check.stderr}"
        if name != FILENAMES[1]:
            embedded = json.loads(re.search(r'<script id="pqd" type="application/json">(.*?)</script>', text, re.S).group(1))
            assert embedded == bank
        else:
            assert f"Based on {len(bank)} UPPSC questions" in text
    for name in FILENAMES[:2]:
        text = rendered[name]
        assert len(re.findall(r'<section class="view ch" id="c\d+"', text)) == len(chapters)
        assert text.count('class="recall"') == sum(len(c["recall"]) for c in chapters)
        assert len(re.findall(r'<summary><span class="t">', text)) == len(repeats)
    full = rendered[FILENAMES[0]]
    assert sum(f'id="{sid}"' in full for sid in source_by_id) == len(source)
    source_details = [d for d in doms[FILENAMES[0]].details if d.get("id", "").endswith("-source")]
    assert len(source_details) == len(chapters) and not any("open" in d for d in source_details)
    assert sum(f'id="{sid}-review"' in full for sid in review_ids) == len(review)
    plan = rendered[FILENAMES[2]]
    hours = re.findall(r'<section class="view" id="h(\d+)"[^>]*>(.*?)(?=<section class="view"|$)', plan, re.S)
    assert [int(n) for n,body in hours] == list(range(1,73))
    multipart, mocks = defaultdict(list), []
    for num, body in hours:
        number = int(num)
        question_ids = re.search(r'data-q="([^"]*)"', body).group(1).split(",")
        assert question_ids and len(question_ids) == len(set(question_ids)) and all(qid in bank for qid in question_ids)
        if number <= 48:
            title = re.search(r"<h2>(.*?)</h2>", body).group(1)
            if "· part" in title:
                base = title.split("· part")[0]
                points = re.findall(r'<li class="pt">(.*?)</li>', body, re.S)
                assert points
                multipart[base].append((set(question_ids), set(points)))
        if number >= 69:
            assert len(question_ids) == 25
            mocks.append(set(question_ids))
    for parts in multipart.values():
        seen_q, seen_p = set(), set()
        for qs, points in parts:
            assert not qs & seen_q and not points & seen_p
            seen_q.update(qs)
            seen_p.update(points)
    assert sum(map(len, mocks)) == len(set.union(*mocks))
    runtime = subprocess.run(["node", str(HERE / "runtime_verify.js")], text=True, capture_output=True, encoding="utf-8")
    assert runtime.returncode == 0, f"Plan storage/navigation regression: {runtime.stderr}"
    print(runtime.stdout.strip())
    write_report(ledger)
    print("PASS: source identity/retention, scored-review provenance, 42 learning guides, complete anchors, JavaScript syntax, 72 hours, multipart separation and 100 disjoint mock questions.")
    print(json.dumps(ledger["counts"]))
    return True


if __name__ == "__main__":
    validate()
