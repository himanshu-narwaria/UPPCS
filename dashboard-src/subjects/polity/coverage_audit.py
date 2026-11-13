"""Reproducible source-retention ledger; does not certify every legal fact."""
from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path
import re

from build_polity_data import CHAPTER_SPECS
from source_model import ANSWER, chapter_texts, clean

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
FOLDER = ROOT / "Indian_Polity_and_Governance"
PDF_NAME = "Preview_Indian_Polity_and_Governance_Part_4_2026_26118_C_E_Book.pdf"


def read(name):
    return json.loads((HERE / name).read_text(encoding="utf-8"))


def words(text):
    return Counter(re.findall(r"\w+", clean(text).casefold()))


def characters(text):
    # Space and ligature differences in the two engines are irrelevant to
    # this order-insensitive content check. It is not a semantic comparison.
    return Counter(re.sub(r"[^a-z0-9]", "", clean(text).casefold()))


def build_ledger():
    pages, source, bank, review, intros = (read(name) for name in
        ("raw_pages.json", "all_source_questions.json", "parsed_uppsc_questions.json", "review_questions.json", "source_intros.json"))
    identity = read("source_identity.json")
    actual_hash = hashlib.sha256((FOLDER / PDF_NAME).read_bytes()).hexdigest()
    assert actual_hash == identity["sha256"], "Source PDF changed; regenerate extraction first"
    assert len(pages) == identity["pages"]
    texts = chapter_texts(pages)
    by_chapter = defaultdict(list)
    bank_by_source = {q["source_id"]: qid for qid, q in bank.items()}
    review_ids = {item["id"] for item in review}
    for item in source:
        by_chapter[item["chapter"]].append(item)
    fingerprints, duplicates, page_rows = {}, [], []
    for page in pages:
        num = page["page_num"]
        fingerprint = re.sub(r"\s+", " ", page["text"])
        duplicate_of = fingerprints.get(fingerprint)
        if duplicate_of:
            duplicates.append([duplicate_of, num])
        else:
            fingerprints[fingerprint] = num
        missing = characters(page["stream_text"]) - characters(page["text"])
        page_rows.append({"pdf_page": num, "role": "front matter" if num <= 6 else "content",
                          "duplicate_of": duplicate_of,
                          "independent_character_count_missing": sum(missing.values()),
                          "missing_character_counts": dict(missing)})
    chapter_rows = []
    for index, (num, title, start, _) in enumerate(CHAPTER_SPECS):
        records = by_chapter[num]
        reconstruction = intros[str(num)]["text"] + " " + " ".join(
            r["body"] + " Ans " + r["source_key"] + " " + r["f"] + " " + r.get("cross_reference", "") for r in records)
        missing = words(texts[num]) - words(reconstruction)
        answer_count = len(ANSWER.findall(texts[num]))
        assert answer_count == len(records), f"Chapter {num}: answer-marker mismatch"
        assert not missing, f"Chapter {num}: parser dropped source tokens: {missing}"
        chapter_rows.append({"chapter": num, "title": title,
            "pdf_range": [start, CHAPTER_SPECS[index + 1][2] if index + 1 < len(CHAPTER_SPECS) else len(pages)],
            "source_questions": len(records), "answer_markers": answer_count,
            "scorable_uppsc": sum(r["id"] in bank_by_source for r in records),
            "uppsc_unscored": sum(r["id"] in review_ids for r in records),
            "source_reconstruction_missing_word_tokens": sum(missing.values()),
            "guide_points": 4, "recall_prompts": 3,
            "evidence_anchor": f"polity-uppsc-full-notes.html#c{num}-source"})
    record_rows = [{"source_id": r["id"], "chapter": r["chapter"], "printed_number": r["source_no"],
        "pages": r["pages"], "explanation_pages": r["explanation_pages"],
        "printed_key": r["source_key"], "bank_id": bank_by_source.get(r["id"]),
        "uppsc_review": r["id"] in review_ids, "review_reasons": r["review"],
        "has_printed_cross_reference": "cross_reference" in r,
        "evidence_anchor": f'polity-uppsc-full-notes.html#{r["id"]}'} for r in source]
    result = {"audit_date": "2026-11-13", "source": identity, "verified_pdf_sha256": actual_hash,
        "scope": "Structural source retention and selected learning guides; not a complete independent fact or current-law certification.",
        "counts": {"chapters": len(chapter_rows), "file_pages": len(pages),
            "source_questions_all_exams": len(source), "scorable_uppsc": len(bank),
            "uppsc_review": len(review), "uppsc_source_items": len(bank) + len(review),
            "repeated_uppsc_items": sum(q["n"] >= 2 for q in bank.values()),
            "recall_prompts": len(chapter_rows) * 3},
        "exact_duplicate_content_pages": duplicates, "pages": page_rows,
        "chapters": chapter_rows, "source_items": record_rows,
        "checks": {"source_answer_marker_coverage": "all retained",
            "chapter_reconstruction": "zero missing normalized word-token counts in every chapter",
            "independent_extraction": "zero missing normalized a-z/0-9 character counts on every content page; ignores order and whitespace",
            "current_law": "not comprehensively checked",
            "official_exam_keys": "not independently verified",
            "browser_visual_review": "not available in this session; static/contract checks only"},
        "known_source_corrections": [{"chapter": 41, "printed_label": "Article 300 A for women's Lok Sabha reservation",
            "correction": "330A concerns women's Lok Sabha representation; 300A concerns property",
            "verified_on": "2026-11-13", "official_sources": [
                "https://www.legislative.gov.in/static/uploads/2025/08/cb1b190ea633a1746368ed1fac35fb30.pdf",
                "https://www.legislative.gov.in/static/uploads/2025/07/359f70a69695affb9d72f8393102bd2e.pdf"]}]}
    assert not any(row["independent_character_count_missing"] for row in page_rows if row["role"] == "content")
    (HERE / "coverage_ledger.json").write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    return result


def write_report(ledger):
    counts = ledger["counts"]
    rows = ["# Indian Polity: source coverage and learning audit", "", "Audit date: 13 November 2026.", "",
        f"The supplied PDF has {counts['file_pages']} file pages. The active study files now provide {counts['chapters']} readable chapter guides, four complete points per guide, comparisons, a confusion check and {counts['recall_prompts']} hidden-answer recall prompts. The full notes retain the extracted chapter openings and all {counts['source_questions_all_exams']:,} source question/explanation cards behind closed evidence panels.", "",
        f"Practice contains {counts['scorable_uppsc']:,} scorable UPPSC-labelled questions. A further {counts['uppsc_review']} UPPSC items retain a printed asterisk or malformed options and remain explicitly unscored: {counts['uppsc_source_items']:,} UPPSC source items in total. Four options are present on every scored item. All-exam evidence can have five options. There are {counts['repeated_uppsc_items']} repeated UPPSC items; counts use distinct printed exam labels, not estimates or other exams.", "",
        "## What the cross-check establishes", "",
        "- All 42 source chapter headings were located in visual column order. The correct starts include Articles on file page 41, Governance System on 69, and State Legislature on 331.",
        "- Every printed answer marker in the unique chapter stream has a retained source record. Reconstructing each chapter from its opening, raw question bodies, keys, explanations and printed cross-references leaves zero missing normalized word-token counts in all 42 chapters.",
        "- Independent pypdf stream extraction and PDFium column extraction have zero missing cleaned a-z/0-9 character counts on all 524 content pages. This check ignores order, spaces and punctuation; it detects omitted character content, not incorrect meaning.",
        "- Four duplicate PDF page pairs are retained in the original file and deduplicated in the study stream: " + ", ".join(f"{a}/{b}" for a,b in ledger["exact_duplicate_content_pages"]) + ".",
        "- Questions preserve their actual printed options and keys. No True/False questions, default A keys, invented years, or cut-off explanations are added. Matching-list questions use the final answer-code option run. Printed 'see above' references retain their original text and the resolved explanation/page provenance.",
        "- Chapter 1 restarts printed numbering after its historical subsection. Q113 about BHARATPOL in Miscellaneous and Q44 in Supreme Court have their complete stems. These cases are checked by the validator.", "",
        "## Important source error", "",
        "The source's chapter 41 labels women's Lok Sabha reservation as Article 300 A. The learning layer corrects this to Article 330A and explains that Article 300A concerns property. Primary Legislative Department PDFs were checked on 13 November 2026:", "",
        "- [Women's representation: Article 330A](https://www.legislative.gov.in/static/uploads/2025/08/cb1b190ea633a1746368ed1fac35fb30.pdf)",
        "- [Constitution: Article 300A and property](https://www.legislative.gov.in/static/uploads/2025/07/359f70a69695affb9d72f8393102bd2e.pdf)", "",
        "The Federal Court question on PDF page 11 prints options for 1861, 1909 and 1919, then None of the above. Its book key (d) is consistent with its explanation of the Government of India Act, 1935; it must not be rewritten as option C or 1905.", "",
        "## Limits and verification", "",
        "This is a full structural retention audit plus selective teaching synthesis. It does not establish that every explanation, legal proposition, statistic, office-holder or original exam key is correct. Source-era claims stay explicitly labelled. The book's keys are not described as independently verified official keys. The guide is selective; additional important detail remains in the evidence panels and original PDF.", "",
        "Static checks validate data provenance, scored/review separation, chapter and repeat totals, all local anchors, complete 72-hour scheduling, distinct multipart reading/questions, four disjoint 25-question practice mocks, embedded JavaScript syntax, and absence of inline event attributes or external loaded resources. Live browser visual/interaction review was unavailable in this session; it is not claimed as completed.", "",
        "Rebuild with `python dashboard-src/subjects/polity/rebuild_all_polity.py`. The original source PDF is checked against its recorded SHA-256 and remains unchanged. The active folder is `Indian_Polity_and_Governance`; legacy `Indian_Polity_2026` is outside this rebuild.", "",
        "Machine evidence: [coverage_ledger.json](coverage_ledger.json), including every page, chapter and source item. Counts in the validator are derived from source evidence rather than frozen to the previous erroneous 1,280-item bank.", "",
        "## Chapter ledger", "", "| Chapter | PDF file pages | All-exam cards | Scored UPPSC | UPPSC review |", "|---|---:|---:|---:|---:|"]
    for row in ledger["chapters"]:
        a,b = row["pdf_range"]
        rows.append(f'| {row["chapter"]}. {row["title"]} | {a}-{b} | {row["source_questions"]} | {row["scorable_uppsc"]} | {row["uppsc_unscored"]} |')
    (HERE / "coverage_audit.md").write_text("\n".join(rows) + "\n", encoding="utf-8")


if __name__ == "__main__":
    ledger = build_ledger()
    write_report(ledger)
    print(json.dumps(ledger["counts"]))
