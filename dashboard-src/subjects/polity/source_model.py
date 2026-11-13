"""Page-aware evidence model. Never manufacture options, keys, or official status."""
from collections import Counter
import html
import json
from pathlib import Path
import re
import unicodedata
from build_polity_data import CHAPTER_SPECS, format_uppsc_exam

HERE = Path(__file__).resolve().parent
PAGE = re.compile(r"\[\[PDF_PAGE:(\d+)\]\]")
ANSWER = re.compile(r"(?m)^\s*Ans\s*\.\s*\(([^)]*)\)")
QUESTION = re.compile(r"(?m)^\s*(\d{1,3})(?:\s*[.．]\s*|\s+(?=[A-Z‘“]))")
OPTION = re.compile(r"\(\s*([a-e])\s*\)")
EXAM = re.compile(r"^\s*(?:U\s*\.?\s*P\s*\.?|M\s*\.?\s*P\s*\.?|I\s*\.?\s*A\s*\.?\s*S\s*\.?|R\s*\.?\s*A\s*\.?\s*S\s*\.?|Chh?attisgarh|Chh?atisgarh|Jharkhand|Utt?arakhand|Uttrakhand|(?:\d+(?:st|nd|rd|th)?\s*(?:to\s*\d+(?:st|nd|rd|th)?)?\s*)?B\s*\.?\s*P\s*\.?\s*(?:S\s*\.?\s*C|C\s*\.?\s*S))", re.I)
UP = re.compile(r"\bU\s*\.?\s*P\s*\.?\s*(?:P\s*\.?\s*C\s*\.?\s*S|P\s*\.?\s*S\s*\.?\s*C|Lower|R\s*\.?\s*O|A\s*\.?\s*R\s*\.?\s*O|U\s*\.?\s*D\s*\.?\s*A|L\s*\.?\s*D\s*\.?\s*A|G\s*\.?\s*I\s*\.?\s*C|G\s*\.?\s*D\s*\.?\s*C|B\s*\.?\s*E\s*\.?\s*O|R\s*\.?\s*I)", re.I)


def clean(text):
    text = PAGE.sub("", text)
    text = unicodedata.normalize("NFKC", text).replace("\x02", "")
    text = re.sub(r"(?im)^.*(?:search on TG|click here|@freepdfhall|@PdfTaskari).*$", "", text)
    text = re.sub(r"(?im)^.*General Studies.*$", "", text)
    text = re.sub(r"(?im)^D[–-]\s*\d+\s*$", "", text)
    return text.strip()


def plain(text):
    return re.sub(r"\s+", " ", clean(text)).strip()


def source_pages(text, start, end):
    prior = [int(m.group(1)) for m in PAGE.finditer(text[:start])]
    inside = [int(m.group(1)) for m in PAGE.finditer(text[start:end])]
    return sorted(set((prior[-1:] or inside[:1]) + inside))


def chapter_texts(pages):
    unique_pages, seen = [], set()
    for page in pages:
        fingerprint = re.sub(r"\s+", " ", page["text"])
        if fingerprint in seen:
            continue
        seen.add(fingerprint)
        unique_pages.append(page)
    stream = "\n".join(f"\n[[PDF_PAGE:{p['page_num']}]]\n{p['text']}" for p in unique_pages)
    starts = []
    for num, title, start_page, pattern in CHAPTER_SPECS:
        marker = stream.index(f"[[PDF_PAGE:{start_page}]]")
        next_marker = stream.find("[[PDF_PAGE:", marker + 1)
        stop = next_marker if next_marker >= 0 else len(stream)
        match = re.search(pattern, stream[marker:stop], re.I)
        if not match:
            raise ValueError(f"Chapter {num}: heading missing on PDF p{start_page}: {pattern}")
        starts.append(marker + match.start())
    return {n: f"[[PDF_PAGE:{p}]]\n" + stream[starts[i]:starts[i + 1] if i + 1 < len(starts) else len(stream)]
            for i, (n, title, p, pattern) in enumerate(CHAPTER_SPECS)}


def split_options(text):
    matches = list(OPTION.finditer(text))
    # Matching questions sometimes label the two lists (a)-(d) before the
    # actual answer-code options. Use the final complete option run.
    for first in reversed([m for m in matches if m.group(1) == "a"]):
        chosen = [first]
        for letter in "bcd":
            nxt = next((m for m in matches if m.start() > chosen[-1].start() and m.group(1) == letter), None)
            if nxt is None:
                break
            chosen.append(nxt)
        if len(chosen) == 4:
            fifth = next((m for m in matches if m.start() > chosen[-1].start() and m.group(1) == "e"), None)
            if fifth:
                chosen.append(fifth)
            options = [plain(text[m.end():chosen[i + 1].start() if i + 1 < len(chosen) else len(text)]) for i, m in enumerate(chosen)]
            if all(options):
                return plain(text[:first.start()]), options
    return plain(text), []


def parse_chapter(text, chapter):
    answers = list(ANSWER.finditer(text))
    records = []
    previous_number = 0
    for index, answer in enumerate(answers):
        previous_end = answers[index - 1].end() if index else 0
        segment = text[previous_end:answer.start()]
        headings = list(QUESTION.finditer(segment))
        expected = [m for m in headings if int(m.group(1)) == previous_number + 1]
        # Numbered statements are ordinarily <= 5; prefer the next source
        # question number, with the first question after the chapter heading.
        heading = expected[0] if expected else (headings[0] if headings else None)
        if chapter == 38 and index == 0:
            heading = expected[-1]  # introductory list "1. Simple majority" is not Q1
        start = previous_end + heading.start() if heading else previous_end
        number = int(heading.group(1)) if heading else previous_number + 1
        previous_number = number
        body = text[start:answer.start()]
        lines = clean(body).splitlines()
        exam_at = [i for i, line in enumerate(lines) if EXAM.search(line) and re.search(r"\b(?:19|20)\d{2}\b", line)]
        # Exam metadata follows all options. A question stem can itself name
        # an exam or a commission, so take the final contiguous metadata area.
        exam_start = exam_at[0] if exam_at else len(lines)
        exam_lines = [plain(lines[i]) for i in exam_at]
        content = "\n".join(lines[:exam_start])
        content = re.sub(rf"^\s*{number}(?:\s*[.．]\s*|\s+)", "", content)
        stem, options = split_options(content)
        key_text = answer.group(1).strip()
        keys = [ord(letter) - 97 for letter in re.findall(r"\b[a-e]\b", key_text.lower())] if re.fullmatch(r"[a-e, /&+orand]+", key_text.lower()) else []
        keys = sorted(set(k for k in keys if k < len(options)))
        records.append({"chapter": chapter, "source_no": number, "s": stem,
                        "o": options, "k": keys, "source_key": key_text,
                        "exams": exam_lines, "uppsc_exams": [x for x in exam_lines if UP.search(x)],
                        "pages": source_pages(text, start, answer.end()), "start": start,
                        "answer_end": answer.end(), "body": plain(body)})
    first_start = records[0]["start"] if records else len(text)
    previous_explanation = ""
    previous_explanation_pages = []
    for index, record in enumerate(records):
        end = records[index + 1]["start"] if index + 1 < len(records) else len(text)
        explanation = plain(text[record["answer_end"]:end])
        exp_pages = source_pages(text, record["answer_end"], end)
        if re.search(r"See\s+(?:the\s+)?explanations?\s+(?:of\s+)?(?:the\s+)?(?:above|previous)\s+question", explanation, re.I):
            record["cross_reference"] = explanation
            record["f"] = previous_explanation or "Source check: the book refers to an earlier explanation; consult the PDF before using this answer."
            record["explanation_pages"] = previous_explanation_pages
        else:
            record["f"] = explanation or "The source prints this answer key without an explanation."
            record["explanation_pages"] = exp_pages
            if explanation:
                previous_explanation = explanation
                previous_explanation_pages = exp_pages
        record["pages"] = sorted(set(record["pages"] + exp_pages))
        record["review"] = []
        if not record["s"] or not record["o"] or not record["k"]:
            record["review"].append("Printed key/options need manual review; retained as an unscored source question.")
        if "*" in record["source_key"]:
            record["review"].append("The book marks the key with an asterisk; do not infer an answer option.")
        for field in ["start", "answer_end"]:
            del record[field]
    intro = text[:first_start]
    return records, intro


def build():
    pages = json.loads((HERE / "raw_pages.json").read_text(encoding="utf-8"))
    texts = chapter_texts(pages)
    all_source = []
    bank = {}
    pending = []
    intros = {}
    stats = {}
    for number, title, first_page, pattern in CHAPTER_SPECS:
        text = texts[number]
        records, intro = parse_chapter(text, number)
        intros[str(number)] = {"text": intro, "pages": source_pages(text, 0, len(intro))}
        chapter_dir = HERE / "chapter_texts"
        chapter_dir.mkdir(exist_ok=True)
        export_text = "\n".join(line.rstrip() for line in text.splitlines()).rstrip() + "\n"
        (chapter_dir / f"ch{number}.txt").write_text(export_text, encoding="utf-8")
        stats[number] = 0
        for ordinal, record in enumerate(records, 1):
            record["id"] = f"src-c{number}-item{ordinal}"
            all_source.append(record)
            exams = list(dict.fromkeys(record["uppsc_exams"]))
            if not exams:
                continue
            if record["review"]:
                pending.append(record)
                continue
            labels = [format_uppsc_exam(x) for x in exams]
            year = max(x[1] for x in labels)
            qid = f"q{len(bank) + 1:04d}"
            bank[qid] = {"ch": f"c{number}", "y": year, "e": "; ".join(x[0] for x in labels),
                         "s": html.escape(record["s"]), "o": [html.escape(x) for x in record["o"]],
                         "k": record["k"], "f": html.escape(record["f"]), "n": len(exams),
                         "h": f"c{number}-t1", "p": record["pages"][0], "pages": record["pages"],
                         "exams": exams, "source_no": record["source_no"], "source_id": record["id"],
                         "key_status": "book key; not independently verified as official"}
            stats[number] += 1
    for filename, data in [("all_source_questions.json", all_source), ("parsed_uppsc_questions.json", bank),
                           ("review_questions.json", pending), ("source_intros.json", intros),
                           ("parsed_chapter_stats.json", stats)]:
        (HERE / filename).write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Parsed {len(all_source)} source questions; {len(bank)} scorable UPPSC items; {len(pending)} UPPSC items retained for review.")
    print("Scorable questions by chapter:", stats)


if __name__ == "__main__":
    build()
