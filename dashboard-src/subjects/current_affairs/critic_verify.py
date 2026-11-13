"""Deterministic source/learning regressions, not an independent content review."""
import hashlib
import json
from collections import Counter
from pathlib import Path
from bs4 import BeautifulSoup
from source_builder import CHAPTERS, PDF, normalise

HERE = Path(__file__).resolve().parent
OUT = HERE.parents[2] / "Drishti-current affairs"

def load(name):
    return json.loads((HERE/name).read_text(encoding="utf-8"))

def main():
    chapters, bank, priority = (load(n) for n in ["structured_all_chapters.json", "parsed_uppsc_questions.json", "priority_facts.json"])
    pages, manifest, sessions, raw = (load(n) for n in ["page_ledger.json", "source_manifest.json", "session_plan.json", "raw_pages.json"])
    assert hashlib.sha256(PDF.read_bytes()).hexdigest() == manifest["sha256"]
    assert len(raw) == len(pages) == 241
    assert [p["page"] for p in pages] == list(range(1, 242))
    content = [p for p in pages if p["type"] == "content"]
    assert len(content) == 238
    assert all(p["source_blocks"] > 0 and p["text_preserved_after_documented_normalisation"] for p in content)
    assert [p["page"] for p in content] == list(range(4, 242))
    assert len(chapters) == 10 and len(bank) == 40 and len(priority) == 80
    counts = Counter(q["ch"] for q in bank.values())
    assert counts == Counter({f"c{n}": 4 for n in range(1, 11)})
    assert load("repeated_facts.json") == []
    for n, c in enumerate(chapters, 1):
        assert c["num"] == n and (c["start_page"], c["end_page"]) == CHAPTERS[n-1][-2:]
        assert len(c["learning"]["points"]) == 8 and len(c["learning"]["recall"]) == 5
        for point in c["learning"]["points"] + c["learning"]["recall"]:
            assert point[2] and all(1 <= p <= 241 for p in point[2])
        for t in c["topics"]:
            assert c["start_page"] <= t["page_start"] <= t["page_end"] <= c["end_page"]
            assert all(c["start_page"] <= p["page"] <= c["end_page"] for p in t["points"])
    for q in bank.values():
        c = chapters[int(q["ch"][1:])-1]
        assert q["kind"] == "source-practice" and len(q["o"]) == len(set(q["o"])) == 4
        assert len(q["k"]) == 1 and 0 <= q["k"][0] < 4 and len(q["f"]) > 80
        assert c["start_page"] <= q["page"] <= c["end_page"]
    for page, value in [(5,"Kalinganagar"),(6,"5,659.22"),(6,"Pragati"),(10,"53,428"),(17,"88.05"),(220,"Himanshu Roy")]:
        assert value.casefold() in normalise(raw[page-1]["text"]).casefold(), (page,value)
        retained = " ".join(p["text"] for c in chapters for t in c["topics"] for p in t["points"] if p["page"] == page)
        retained += " " + " ".join(t["title"] for c in chapters for t in c["topics"] if page in t["heading_pages"])
        assert value.casefold() in retained.casefold(), (page,value,"absent from evidence")
    soups = {}
    for name in ["current-uppsc-full-notes.html","current-uppsc-quick-notes.html","current-in-72h.html"]:
        soup = soups[name] = BeautifulSoup((OUT/name).read_text(encoding="utf-8"),"html.parser")
        meta = json.loads(soup.select_one("#study-meta").string)
        assert meta["question_kind"] == "source-practice"
        assert meta["practice_questions"] == 40 and meta["priority_facts"] == 80
        assert meta["verified_uppsc_pyqs"] == meta["verified_repeated_facts"] == 0
        assert meta["chapter_practice_counts"] == dict(counts)
        assert meta["source_pdf_pages"] == 241 and meta["source_content_pages"] == 238
        assert "500 UPPSC" not in soup.get_text() and "120 facts asked" not in soup.get_text()
    full, quick, plan = (soups[n] for n in ["current-uppsc-full-notes.html","current-uppsc-quick-notes.html","current-in-72h.html"])
    for soup in [full,quick]:
        assert len(soup.select("section.ch")) == len(soup.select("#home .toc a")) == 10
        assert len(soup.select(".guided .fact")) == 80 and len(soup.select(".recall")) == 50
        assert len(soup.select(".guided table")) == 10 and len(soup.select("#repeated .rows > li")) == 80
        assert "80 priority facts from the source" in soup.select_one("#rep-facts").get_text()
        assert "Based on 40 source practice questions" in soup.select_one(".foot").get_text()
    assert sum(len(t["points"]) for c in chapters for t in c["topics"]) == len(full.select(".source-topic li[data-page]"))
    assert {int(p["data-page"]) for p in full.select(".source-topic li[data-page]")} == set(range(4,242))
    assert json.loads(full.select_one("#pqd").string) == json.loads(plan.select_one("#pqd").string) == bank
    assert [int(s["data-n"]) for s in plan.select("section[data-n]")] == list(range(1,73))
    assert Counter(s["phase"] for s in sessions) == Counter({"Learn":54,"Revise":10,"Test":8})
    assert [p for s in sessions if s["phase"] == "Learn" for p in s["pages"]] == list(range(4,242))
    mocks = plan.select("ol[data-mock]")
    assert len(mocks) == len(plan.select("[data-submit-mock]")) == len(plan.select("[data-reset-mock]")) == 4
    mock_ids = [q for mock in mocks for q in mock["data-q"].split(",")]
    assert len(mock_ids) == len(set(mock_ids)) == 40 and set(mock_ids) == set(bank)
    assert all(len(mock["data-q"].split(",")) == 10 for mock in mocks)
    assert len(plan.select(".timebox[data-seconds='720']")) == 4
    for ol in plan.select("ol.pq"):
        assert all(q in bank for q in ol["data-q"].split(","))
    print("Verified source hash; 238 retained content pages; 10 chapters; 80 guided facts; 50 recalls; 40 source-practice MCQs; 72 sessions; four isolated ten-question mocks.")
    print("Scope: structural/source-retention checks and six omission regressions; not certification of every table, source claim or live fact.")

if __name__ == "__main__":
    main()
