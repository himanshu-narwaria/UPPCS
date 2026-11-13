"""Write the bounded coverage report and machine-readable reference ledger."""
import json
from collections import Counter
from pathlib import Path
from source_builder import PDF

HERE = Path(__file__).resolve().parent

def load(name):
    return json.loads((HERE/name).read_text(encoding="utf-8"))

def main():
    chapters = load("structured_all_chapters.json")
    manifest = load("source_manifest.json")
    bank = load("parsed_uppsc_questions.json")
    pages = load("page_ledger.json")
    guided = [dict(id=f"c{c['num']}-f{i}",chapter=c["num"],label=label,pages=ps,
                   reference_check="page exists; editorial selection, not exhaustive")
              for c in chapters for i,(label,text,ps) in enumerate(c["learning"]["points"],1)]
    counts = Counter(q["ch"] for q in bank.values())
    chapter_rows = [dict(chapter=c["num"],title=c["title"],start_page=c["start_page"],end_page=c["end_page"],
        content_pages=c["end_page"]-c["start_page"]+1,source_topics=len(c["topics"]),
        source_blocks=sum(len(t["points"]) for t in c["topics"]),guided_facts=len(c["learning"]["points"]),
        recall_prompts=len(c["learning"]["recall"]),practice_questions=counts[f"c{c['num']}"])
        for c in chapters]
    recoveries = [
        dict(pages=[5],item="Kalinganagar",reason="Short answer for the below-3-lakh Swachh Vayu category"),
        dict(pages=[5,6],item="Mission for Cotton Productivity: ₹5,659.22 crore",reason="Question and answer cross a PDF page boundary"),
        dict(pages=[6],item="Pragati and Vikas",reason="Keep both Census mascot names and enumerator roles"),
        dict(pages=[10,93],item="Pradhan Mantri Samajik Sahayata Yojana: ₹53,428 crore",reason="Keep the short amount with its programme and detailed period"),
        dict(pages=[17],item="Neeraj Chopra: 88.05 metres",reason="Keep the short distance with Lausanne 2026 and reported second place"),
        dict(pages=[220],item="Himanshu Roy: PMO",reason="Keep the short author line with its full title"),
    ]
    flags = [dict(chapter=c["num"],**flag) for c in chapters for flag in c["learning"]["checks"]]
    ledger = dict(scope="PDF-to-notes coverage and reference audit; not independent live fact or official exam-key verification",
        source=manifest,chapter_coverage=chapter_rows,guided_fact_references=guided,
        recall_references=[dict(chapter=c["num"],prompt=q,pages=p) for c in chapters for q,a,p in c["learning"]["recall"]],
        practice_references=[dict(id=i,chapter=q["ch"],page=q["page"],kind=q["kind"],note_anchor=q["h"]) for i,q in bank.items()],
        recovered_examples=recoveries,source_cautions=flags,
        source_visual_review_pages=[28,38,49,182,203,213],
        source_visual_scope="Focused page inspection of newly broadened national/news selections; not every PDF layout",
        automated_checks=dict(cached_text_matches_pdf_pages=241,content_pages_mapped=238,
            canonical_source_text_preserved_pages=sum(p.get("text_preserved_after_documented_normalisation",False) for p in pages),
            source_topics=sum(c["source_topics"] for c in chapter_rows),source_blocks=sum(c["source_blocks"] for c in chapter_rows),
            guided_facts=len(guided),comparisons=10,recall_prompts=50,source_practice_questions=len(bank),
            verified_uppsc_pyqs=0,verified_repeated_facts=0),
        limitations=["A retained text block is not proof that an extracted table preserves its visual row/column relationships.",
            "The 80 guided facts and quick notes are selective; all content-page text is in the full source evidence layer.",
            "Current figures, appointments, results, rankings and legal developments are the supplied issue's claims and dates, not verified live updates.",
            "No browser was available for visual HTML or end-to-end browser testing; static structure, links, script syntax and state-focused runtime checks are used."])
    (HERE/"coverage_ledger.json").write_text(json.dumps(ledger,ensure_ascii=False,indent=2),encoding="utf-8")
    lines = ["# Drishti current-affairs coverage audit", "",
        "The study files now use a guided learning layer, explained recall and explicitly labelled source practice. The audit distinguishes physical PDF coverage from semantic verification; it does not certify every source claim or every table cell.", "",
        f"Source: `{PDF.name}`. SHA-256: `{manifest['sha256']}`.", "",
        "The 241 cached pages match a fresh pypdf extraction page by page. PDF page 1 is the cover/watermark; pages 2-3 are index/editorial matter. All 238 content pages, PDF pp. 4-241, are mapped to ten contiguous chapters. Original PDF bytes are read only by the generators.", "",
        "For each content page, a character-preservation assertion compares cleaned source text with its split heading and text fragments. It ignores whitespace, bullet/control glyphs and documented scan ligature normalization; running page headers, Telegram footers and empty lines are excluded. All 238 pages pass. This confirms text retention after those transformations, not semantic correctness or faithful table geometry.", "",
        "| Chapter | PDF pages | Source topics | Source blocks | Guided / recall / MCQ |", "|---|---|---:|---:|---:|"]
    for c in chapter_rows:
        lines.append(f"| {c['chapter']}. {c['title']} | {c['start_page']}-{c['end_page']} | {c['source_topics']} | {c['source_blocks']} | {c['guided_facts']} / {c['recall_prompts']} / {c['practice_questions']} |")
    lines += ["", f"There are {sum(c['source_topics'] for c in chapter_rows):,} retained source topics and {sum(c['source_blocks'] for c in chapter_rows):,} source text blocks, 80 guided facts, ten comparisons, 50 explained recall prompts and 40 authored source-practice MCQs. The quick notes are a selective learning guide; the full notes contain the supporting source evidence. All guided, recall and MCQ references point to valid PDF file pages. File-page numbers are one higher than the printed page numbers.", "",
        "## Recovered omissions and broader selections", ""]
    lines += [f"- PDF pp. {', '.join(map(str,r['pages']))}: {r['item']}. {r['reason']}." for r in recoveries]
    lines += ["", "National Affairs now spans UDAN and rights, SEMICON (p. 28), Ken-Betwa (p. 38) and Census phases (pp. 49-50). The news chapter includes books, ambassador/CJI appointments, environmental and peace awards, and naval exercise partners. Newly selected details were checked against extracted source text; PDF pp. 28, 38, 49, 182, 203 and 213 were also visually inspected. The clearly readable SIMBEX, VARUNA and SLINEX rows were used from p. 213; its overlapping rows remain flagged.", "",
        "## Provenance and study behavior", "",
        "The former claims of 500 UPPSC questions and 120 repeated facts were not supported by verified papers. They are replaced by 40 editorial source-practice questions and 80 editorial priority facts, with zero verified UPPSC PYQs and zero verified repeat counts. No official exam keys or exam predictions are asserted. Both full and quick TOCs and the dashboard metadata agree on those counts.", "",
        "The 72-hour plan maps all 238 content pages once across 54 distinct learning ranges, then adds ten revision sessions, four drills and four timed mocks. Each mock has ten questions; the four mocks partition the 40-question bank. Mocks use fresh independent answer sheets and reveal keys only after submission; learning-bank answers remain separate. Feedback links from the plan open the matching full-note anchor. Malformed/null saved answers are discarded safely.", "",
        "## Source cautions retained", ""]
    lines += [f"- Chapter {f['chapter']}, PDF pp. {', '.join(map(str,f['pages']))}: {f['text']}" for f in flags]
    lines += ["", "## Verification and limits", "",
        "`rebuild_all_current_affairs.py` rebuilds the three study pages and runs source-retention, metadata/count, chapter-range, omission-regression, security, anchor and dashboard-contract checks. `critic_verify.py` is a deterministic regression script; it is not the separately requested fresh critic review. `coverage_ledger.json` records the reference-level scope and cautions; `page_ledger.json` records all 241 pages and per-content-page preservation checks.", "",
        "No browser was available for visual HTML or end-to-end interaction testing. JavaScript syntax and focused state/feedback behavior checks supplement the static HTML audits. Source PDF visual inspection is a sample, not certification of all figures, maps or tables. The guide follows the supplied 2026 (2) issue; it does not claim that the issue's later dates, office-holders, results, rankings or legal statements were independently verified against current primary sources.", ""]
    (HERE/"coverage_audit.md").write_text("\n".join(lines),encoding="utf-8")
    print("Wrote coverage_audit.md and coverage_ledger.json with bounded reference/retention scope.")

if __name__ == "__main__":
    main()
