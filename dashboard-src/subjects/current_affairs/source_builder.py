"""Build dated learning notes without fabricated paper provenance.

Short answer lines remain with their questions. No content block is discarded for
being short. Only obvious scan ligatures are normalised; event claims stay dated.
"""
import hashlib
import html
import json
import re
from pathlib import Path
from pypdf import PdfReader
from learning_content import LEARNING

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
PDF = ROOT / "Drishti-current affairs/Drishti (2) English 2026 (2615-M).pdf"
CHAPTERS = [
    (1, "Points to Remember", "याद रखने योग्य बिंदु", 4, 17),
    (2, "National Affairs", "राष्ट्रीय परिदृश्य", 18, 52),
    (3, "International Affairs", "अंतरराष्ट्रीय परिदृश्य", 53, 86),
    (4, "Economic Affairs", "आर्थिक परिदृश्य", 87, 120),
    (5, "Science & Technology Affairs", "वैज्ञानिक परिदृश्य", 121, 143),
    (6, "Environmental Affairs", "पर्यावरण परिदृश्य", 144, 156),
    (7, "Uttar Pradesh Current Affairs", "उत्तर प्रदेश परिदृश्य", 157, 168),
    (8, "Bihar Current Affairs", "बिहार परिदृश्य", 169, 177),
    (9, "Short News, Awards and Persons", "संक्षिप्तियाँ, पुरस्कार एवं चर्चित व्यक्ति", 178, 220),
    (10, "Sports News", "खेल परिदृश्य", 221, 241),
]

def write(name, data):
    (HERE / name).write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

def normalise(text):
    for old, new in {"昀椀": "fi", "昀氀": "fl", "昀昀": "ff", "ﬁ": "fi", "ﬂ": "fl", "ﬀ": "ff", "\u00ad": ""}.items():
        text = text.replace(old, new)
    return re.sub(r"\s+", " ", text).strip()

def clean_page(text):
    lines = []
    for line in text.splitlines():
        s = line.strip()
        if not s or s == "JRLib" or "search on TG" in s or "Click here" in s:
            continue
        if "DRISHTI" in s and re.search(r"20\d\d", s):
            continue
        lines.append(re.sub(r"^l\s+", "\uf0e8 ", s))
    return "\n".join(lines)

def heading_runs(page):
    spans = []
    def visitor(t, cm, tm, font, size):
        if not t.strip() or float(tm[5]) <= 45 or "search on" in t or "Click here" in t:
            return
        f = str(font.get("/BaseFont", "")) if font else ""
        heading = ("BookmanOldStyle-Bold" in f and size > 11) or (
            "Garamond-Bold" in f and (11.4 <= size <= 11.7 or 13.8 <= size <= 14.2))
        if size >= 30 or t.strip() == "JRLib":
            heading = False
        spans.append((t, heading, size))
    page.extract_text(visitor_text=visitor)
    runs, pending = [], []
    for i, (t, is_heading, size) in enumerate(spans):
        superscript = bool(pending and size < 8 and i + 1 < len(spans) and spans[i+1][1])
        if is_heading or superscript:
            pending.append(t.strip())
        else:
            if pending:
                title = normalise(" ".join(pending))
                if len(title) >= 3:
                    runs.append(title)
                pending = []
    if pending:
        runs.append(normalise(" ".join(pending)))
    return runs

def blocks(text):
    # En-dash answers are deliberately NOT delimiters.
    parts = re.split(r"[\uf0e8\uf0dc]|(?=[\x80-\x8f])", text)
    return [s for part in parts if (s := normalise(re.sub(r"[\x00-\x1f\x7f-\x9f]", " ", part)))]

def build_boundaries():
    data = [dict(num=n, title=t, hindi=h, start_page=a, end_page=b,
                 weightage="Editorial selection; no verified exam frequency", gist=LEARNING[n]["intro"])
            for n, t, h, a, b in CHAPTERS]
    write("chapter_boundaries.json", data)
    print("10 verified contiguous chapter ranges; PDF pp. 4-241 (238 content pages).")

def build_data():
    raw = json.loads((HERE / "raw_pages.json").read_text(encoding="utf-8"))
    bounds = json.loads((HERE / "chapter_boundaries.json").read_text(encoding="utf-8"))
    reader = PdfReader(PDF)
    assert len(reader.pages) == len(raw) == 241
    mismatches = [n+1 for n, page in enumerate(reader.pages) if (page.extract_text() or "") != raw[n]["text"]]
    if mismatches:
        raise ValueError(f"Cached extraction differs from source PDF: {mismatches}")
    chapters = []
    ledger = [dict(page=n, type="cover/watermark" if n == 1 else "index/editorial", chapter=None) for n in range(1, 4)]
    for boundary in bounds:
        c = dict(boundary)
        n = c["num"]
        c["learning"] = LEARNING[n]
        c["topics"] = []
        def new_topic(title, page):
            item = dict(id=f"c{n}-t{len(c['topics'])+2}", title=title, page_start=page,
                        page_end=page, heading_pages=[page], points=[])
            c["topics"].append(item)
            return item
        current = new_topic(f"{c['title']}: source reading", c["start_page"])
        for page_num in range(c["start_page"], c["end_page"] + 1):
            body = normalise(clean_page(raw[page_num-1]["text"]))
            retained = []
            positions, cursor = [], 0
            for title in heading_runs(reader.pages[page_num-1]):
                pos = body.find(title, cursor)
                if pos >= 0:
                    positions.append((pos, pos+len(title), title))
                    cursor = pos + len(title)
            cursor = 0
            for start, end, title in positions + [(len(body), len(body), None)]:
                for value in blocks(body[cursor:start]):
                    retained.append(value)
                    current["points"].append(dict(page=page_num, pages=[page_num], text=value,
                                                 html=html.escape(value), asked=False, hot=False))
                    current["page_end"] = page_num
                if title:
                    retained.append(title)
                    if not current["points"] and current["title"].endswith(": source reading"):
                        current["title"] = title
                        current["heading_pages"] = [page_num]
                    else:
                        current = new_topic(title, page_num)
                cursor = end
            canonical = lambda value: re.sub(r"[\s\uf0e8\uf0dc\x00-\x1f\x7f-\x9f]", "", value)
            if canonical(body) != canonical(" ".join(retained)):
                raise ValueError(f"Source text lost while splitting PDF page {page_num}")
            ledger.append(dict(page=page_num, type="content", chapter=n,
                               topics=[t["id"] for t in c["topics"] if page_num in t["heading_pages"] or any(x["page"] == page_num for x in t["points"])],
                               source_blocks=sum(x["page"] == page_num for t in c["topics"] for x in t["points"]),
                               retained_characters=len(canonical(body)),
                               text_preserved_after_documented_normalisation=True,
                               cleaned_text_sha256=hashlib.sha256(body.encode("utf-8")).hexdigest()))
        chapters.append(c)
    write("structured_all_chapters.json", chapters)
    write("page_ledger.json", ledger)
    write("source_manifest.json", dict(pdf=PDF.name, sha256=hashlib.sha256(PDF.read_bytes()).hexdigest(),
        total_pages=241, content_pages=238, cached_text_matches_all_pages=True,
        normalization={"昀椀": "fi", "昀氀": "fl", "昀昀": "ff", "soft_hyphen": "removed"},
        context="Supplied Drishti 2026 (2) issue; no live updates or official key verification"))
    print(f"Built {len(chapters)} guided chapters, {sum(len(c['topics']) for c in chapters)} source topics, "
          f"{sum(len(t['points']) for c in chapters for t in c['topics'])} source blocks; 241 cached pages match PDF.")

def build_practice():
    questions, priority = {}, []
    for n, data in LEARNING.items():
        for label, text, pages in data["points"]:
            priority.append(dict(ch=n, fact=text, label=label, pages=pages, anchor=f"c{n}-t1", kind="editorial-priority"))
        for stem, options, key, explanation, page in data["practice"]:
            qid = f"q{len(questions)+1:04d}"
            assert len(options) == len(set(options)) == 4 and 0 <= key < 4
            assert options[key] and len(explanation) > 80
            questions[qid] = dict(ch=f"c{n}", y=2026, e=f"Source practice · PDF p. {page}",
                                 s=stem, o=options, k=[key], f=f"{explanation} (PDF p. {page}; issue context.)",
                                 n=1, h=f"c{n}-t1", page=page, kind="source-practice")
    write("parsed_uppsc_questions.json", questions)
    write("repeated_facts.json", [])
    write("priority_facts.json", priority)
    print(f"{len(questions)} source-practice MCQs; {len(priority)} editorial priority facts; 0 verified UPPSC PYQs/repeats.")
