"""Step 1: read a chapterwise solved-paper book by font and position; write <book>/source.json.

    python pq_extract.py polity|history|economy

What the print means in these books (checked page by page):
  * question: bold, starting with its number ("77. Ashokaram monastery was situated at -")
  * options (a)-(d), numbered statements and List-I/List-II rows: regular ("Code :" and list
    headers bold)
  * exam tag lines: bold, with a year ("U.P.P.C.S. (Mains) 2015"); a question can carry several
  * answer: bold "Ans. (b)"
  * explanation: regular text after the answer, key words bold; "See the explanation of the
    above question." points back to an earlier question
  * a chapter opens with its title (bold, 15pt or more) and a theory section of short facts
    separated by "*", key terms bold, sub-headings bold and a little larger
Page furniture is dropped: watermark fonts (Helvetica, Lato), footers below y = 86, Hindi set in
legacy-encoded fonts. The Economy PDF stores every character 29 code points low, often has no
space characters between words, and uses private codes for dashes, quotes and bullets.
"""
import ctypes
import json
import re
import sys
from collections import Counter

import pypdfium2 as pdfium
import pypdfium2.raw as raw

from pq_books import BOOKS, book_dir

DROP_FONTS = ("Helvetica", "Lato", "APS-DV", "Kruti", "DevLys", "Walkman", "F5", "F6")
FOOTER_Y = 86
ECON_MAP = {"±": "–", "¶": "’", "µ": "‘", "³": "“", "´": "”", "²": "—", "\x87": "•", "\x8a": "•", "¼": "•"}
LIGATURE = {0xFB01: "fi", 0xFB02: "fl", 0xFB00: "ff", 0xFB03: "ffi", 0xFB04: "ffl"}
TITLE_SIZE = 14.5
HEAD_SIZE = 10.6
# "Ans. (b)", "Ans. (a & c)", and two answers printed as "Ans. (a) & (c)"
# (one stray character may stand for the full stop: the Economy PDF decodes "Ans." as "Ansm" twice)
ANS_RE = re.compile(r"\bAns\s*[.m]?\s*[:\-]?\s*\(\s*([a-eA-E*](?:\s*(?:,|&|and|or)\s*[a-eA-E])*)\s*(?:\)|(?=\s+[A-Z])|$)"
                    r"(?:\s*(?:&|and|,|or)\s*\(\s*[a-eA-E]\s*\))*")
QNUM_RE = re.compile(r"^(\d{1,4})\s*\.(?:\s*(?=\S)|\s*$)")     # "77. Ashokaram ..." or a lone "1." above a map
YEAR_RE = re.compile(r"(?:19|20)\d\d")
EXAM_WORDS = re.compile(r"P\.?\s*C\.?\s*S|I\.?\s*A\.?\s*S|U\.?\s*P|B\.?\s*P\.?\s*S\.?\s*C|R\.?\s*A\.?\s*S|"
                        r"Pre|Mains|Exam|S\.?\s*S\.?\s*C|C\.?\s*D\.?\s*S|N\.?\s*D\.?\s*A|R\.?\s*O|U\.?\s*D\.?\s*A|"
                        r"Lower|Sub\.?|J\.?\s*P\.?\s*S\.?\s*C|Uttarakhand|Chhattisgarh|Jharkhand|Haryana|Punjab|"
                        r"Gujarat|Rajasthan|Himachal|Bihar|M\.?\s*P|C\.?\s*G|U\.?\s*K|Spl|Re-?Exam|P\.?\s*S\.?\s*C|"
                        r"Teacher|T\.?\s*G\.?\s*T|L\.?\s*T|Asst|B\.?\s*E\.?\s*O|G\.?\s*I\.?\s*C|Police|Forest|"
                        r"A\.?\s*P\.?\s*O|Commission|Services|Selection|Officer", re.I)


# ------------------------------------------------------------------ characters
def page_chars(doc, index, shift):
    page = doc[index]
    tp = page.get_textpage()
    buf = ctypes.create_string_buffer(256)
    flags = ctypes.c_int()
    m = raw.FS_MATRIX()
    out = []
    for i in range(tp.count_chars()):
        u = raw.FPDFText_GetUnicode(tp.raw, i)
        raw.FPDFText_GetFontInfo(tp.raw, i, buf, 256, ctypes.byref(flags))
        font = buf.value.decode(errors="ignore").split("+")[-1]
        if font.startswith(DROP_FONTS):
            continue
        raw.FPDFText_GetMatrix(tp.raw, i, ctypes.byref(m))
        size = abs(m.d) * raw.FPDFText_GetFontSize(tp.raw, i)
        if size < 2:                       # line-break pseudo characters
            continue
        ox, oy = ctypes.c_double(), ctypes.c_double()
        raw.FPDFText_GetCharOrigin(tp.raw, i, ctypes.byref(ox), ctypes.byref(oy))
        if oy.value < FOOTER_Y:
            continue
        coded = shift and re.fullmatch(r"F\d", font)
        if coded:
            # code 0x20 is both "=" and the PDF's own word space; only "=" has ink
            # (spaces are set near 12pt, some at 11.99, so size alone cannot tell them apart)
            if u == 0x20 and (size >= 12 or tp.get_charbox(i)[2] - tp.get_charbox(i)[0] < 0.5):
                ch = " "
            elif 3 <= u <= 0x5F:
                ch = chr(u + shift)
            else:
                ch = chr(u)
            ch = ECON_MAP.get(ch, ch)
            if not (ch.isascii() or ch in "–’‘“”—•₹×"):
                continue
        elif font.startswith("Wingdings") and u == 0x6C:
            ch = "•"                        # Wingdings "l" is a round bullet
        else:
            ch = LIGATURE.get(u, chr(u))
        if ch in "\r\n\x02\x00":
            continue
        # the loose box spans the glyph's whole advance width, so letters of one word touch and
        # a word gap stays visible even where the PDF has no space character (Economy)
        lb = raw.FS_RECTF()
        raw.FPDFText_GetLooseCharBox(tp.raw, i, ctypes.byref(lb))
        bold = "Bold" in font or font == "F1"
        l_, r2 = (lb.left, lb.right) if lb.right > lb.left else (ox.value, ox.value)
        out.append({"c": ch, "size": round(size, 1), "x": ox.value, "base": oy.value, "l": l_, "r": r2,
                    "bold": bold, "italic": "Italic" in font})
    return out, page.get_width()


# ------------------------------------------------------------------ lines
def build_line(chars, page, col):
    chars = sorted(chars, key=lambda c: c["l"])
    main = [c for c in chars if c["size"] >= 7.5] or chars
    size = Counter(c["size"] for c in main).most_common(1)[0][0]
    runs = []

    def add(t, bold):
        if runs and runs[-1][1] == bold:
            runs[-1][0] += t
        else:
            runs.append([t, bold])
    prev, saw_space = None, False
    for c in chars:
        if c["c"] == " ":       # word spaces come from the gaps; the PDFs' own space characters
            saw_space = True    # also sit inside words ("b y the", "p opulation") ...
            continue
        # ... but where bold and regular meet, the glyph boxes can touch: trust the space there
        switch = prev is not None and saw_space and prev["bold"] != c["bold"]
        saw_space = False
        if prev is not None and prev["c"] != " " and (switch or c["l"] - prev["r"] > max(1.0, 0.1 * size)):
            if not (runs and runs[-1][0].endswith(" ")):
                add(" ", c["bold"] and prev["bold"])
        add(c["c"], c["bold"])
        prev = c
    text = "".join(t for t, _ in runs).strip()
    # a wide gap inside a line separates table cells ("Researcher      Timeline")
    cells, cur, last = [], [], None
    for c in chars:
        if not c["c"].strip():
            if cur:
                cur.append(dict(c, space=True))
            continue
        if last is not None and c["l"] - last["r"] > max(9, 1.1 * size):
            cells.append(cur)
            cur = []
        cur.append(c)
        last = c
    if cur:
        cells.append(cur)
    cell_runs = []
    if len(cells) > 1:
        for cs in cells:
            cr, p_, sp = [], None, False
            for c in cs:
                if c.get("space"):
                    sp = True
                    continue
                switch = p_ is not None and sp and p_["bold"] != c["bold"]
                sp = False
                if p_ is not None and (switch or c["l"] - p_["r"] > max(1.0, 0.1 * size)) and not (cr and cr[-1][0].endswith(" ")):
                    cr.append([" ", c["bold"]])
                if cr and cr[-1][1] == c["bold"]:
                    cr[-1][0] += c["c"]
                else:
                    cr.append([c["c"], c["bold"]])
                p_ = c
            cell_runs.append(cr)
    letters = [c for c in main if c["c"].strip()]
    bold_frac = sum(1 for c in letters if c["bold"]) / len(letters) if letters else 0
    return {"page": page, "col": col, "base": max(c["base"] for c in main), "x0": min(c["l"] for c in chars),
            "x1": max(c["r"] for c in chars), "size": size, "runs": runs, "text": text, "bold": bold_frac,
            "cells": cell_runs}


def page_lines(chars, width, page):
    mid = width / 2
    main = sorted((c for c in chars if c["size"] >= 7.5), key=lambda c: -c["base"])
    small = [c for c in chars if c["size"] < 7.5]
    groups = []
    for c in main:
        if groups and abs(groups[-1][0] - c["base"]) <= 2.2:
            groups[-1][1].append(c)
        else:
            groups.append([c["base"], [c]])
    for c in small:                            # superscripts ("42nd") join the nearest line of their column
        side = c["x"] < mid
        mine = [g for g in groups if any((m_["x"] < mid) == side for m_ in g[1])]
        best = min(mine, key=lambda g: abs(g[0] - c["base"])) if mine else None
        if best is not None and -1.5 <= c["base"] - best[0] <= 7:
            best[1].append(c)
    lines = []
    for base, cs in groups:
        cs.sort(key=lambda c: c["l"])
        # a line crossing the column gap with ordinary letter spacing is full width
        wide = any(a["x"] < mid <= b["x"] and b["l"] - a["r"] < 6 and a["c"] != " " and b["c"] != " "
                   for a, b in zip(cs, cs[1:]))
        if wide:
            lines.append(build_line(cs, page, 2))
            continue
        for col in (0, 1):
            part = [c for c in cs if (c["x"] < mid) == (col == 0)]
            if any(c["c"].strip() for c in part):
                lines.append(build_line(part, page, col))
    # reading order: full-width lines split the page into bands; in a band, left column first
    wides = sorted((ln["base"] for ln in lines if ln["col"] == 2), reverse=True)

    def key(ln):
        band = sum(1 for w in wides if w > ln["base"] + 0.5)
        return (band, 1 if ln["col"] == 2 else (0 if ln["col"] == 0 else 2), -ln["base"])
    for ln in lines:
        if ln["col"] == 2:
            band = sum(1 for w in wides if w > ln["base"] + 0.5)
            ln["_k"] = (band, 1, -ln["base"])
        else:
            ln["_k"] = key(ln)
    # a band = everything between two full-width lines: [left col][right col] then the wide line
    def order(ln):
        band = sum(1 for w in wides if w > ln["base"] + 0.5)
        if ln["col"] == 2:
            return (band, 0, -ln["base"])
        return (band + (0 if True else 0), 1 + ln["col"], -ln["base"])
    out = sorted(lines, key=lambda ln: (sum(1 for w in wides if w >= ln["base"] - 0.5) if ln["col"] != 2
                                        else sum(1 for w in wides if w > ln["base"] + 0.5),
                                        0 if ln["col"] == 2 else 1 + ln["col"], -ln["base"]))
    for ln in out:
        ln.pop("_k", None)
    return out


# ------------------------------------------------------------------ classification helpers
def is_title(ln):
    return TITLE_SIZE <= ln["size"] < 30 and ln["bold"] > 0.7 and len(ln["text"]) > 2 and not ln["text"].isdigit()


def is_tag(ln):
    """An exam tag line: short, bold, ending with a year, naming an exam by its dotted initials
    ("U.P.P.C.S. (Pre) 2014", "48 to 52 B.P.S.C. (Pre) 2008") or by (Pre)/(Mains)."""
    t = ln["text"]
    # the year may be printed "1997-98" or "2002,03"; one UP paper is named with no year at all
    year_end = re.search(r"(?:19|20)\d\d(?:\s*[-–,/]\s*\d{2,4})*\W{0,12}$", t) \
        or re.fullmatch(r"U\.\s?P\.\s?[A-Z][A-Z./()\s-]*", t)
    return bool(ln["bold"] > 0.6 and len(t) < 100 and year_end
                and (re.search(r"\b[A-Z]\.\s?[A-Z]\.", t) or re.search(r"\((?:Pre|Mains?|Re)", t))
                and not t.lower().startswith(("ans", "see")) and not QNUM_RE.match(t)
                # a bold match-list row ending in a year is not a tag ("B. N. Sanjiva Reddy 2. 1974-1977")
                and not re.match(r"^[A-H]\.\s", t) and not re.search(r"\s\d{1,2}\.\s+(?:19|20)\d\d", t))


def qnum(ln):
    """The question number at the start of a line whose number is bold: "77. Ashokaram ...",
    also "44 Consider ..." (no full stop, p304) and "44. Assertion (A): ..." (only the number bold)."""
    if not ln["runs"] or not ln["runs"][0][1] or ln["bold"] < 0.2:
        return None
    m = QNUM_RE.match(ln["text"])
    if not m and ln["bold"] > 0.8 and not re.search(r"(?:19|20)\d\d\W{0,12}$", ln["text"]):
        m = re.match(r"^(\d{1,4})\s+(?=[A-Z‘'“])", ln["text"])   # not "47 B.P.S.C. (Pre) 2005"
    return int(m.group(1)) if m else None


def runs_text(runs):
    return "".join(t for t, _ in runs).strip()


def strip_runs(runs, n):
    """Drop the first n characters of a run list."""
    out = []
    for t, b in runs:
        if n >= len(t):
            n -= len(t)
            continue
        out.append([t[n:], b])
        n = 0
    return out


# ------------------------------------------------------------------ book
def read_lines(book):
    doc = pdfium.PdfDocument(str(book["pdf"]))
    if len(doc) != book["pages"]:
        raise SystemExit(f"{book['pdf'].name}: expected {book['pages']} pages, found {len(doc)}")
    lines, seen, dup = [], {}, []
    for i in range(len(doc)):
        chars, width = page_chars(doc, i, book["shift"])
        text = "".join(c["c"] for c in chars)
        if len(text) > 200 and text in seen:      # the PDF prints some pages twice
            dup.append((i + 1, seen[text]))
            continue
        seen[text] = i + 1
        lines += page_lines(chars, width, i + 1)
    if dup:
        print("pages printed twice (skipped):", ", ".join(f"p{a} = p{b}" for a, b in dup))
    return lines


def find_chapters(lines):
    """Chapter titles: bold lines at 15pt or more; a title may run over two lines."""
    chapters = []
    i = 0
    while i < len(lines):
        ln = lines[i]
        if is_title(ln):
            j = i
            text = ln["text"]
            while j + 1 < len(lines) and is_title(lines[j + 1]) and lines[j + 1]["page"] == ln["page"] \
                    and abs(lines[j + 1]["size"] - ln["size"]) < 1.5:
                j += 1
                text += " " + lines[j]["text"]
            chapters.append({"line": i, "end_line": j, "title": re.sub(r"\s+", " ", text).strip(), "page": ln["page"],
                             "size": ln["size"]})
            i = j + 1
            continue
        i += 1
    return chapters


def split_ans(lines):
    """A line holding "Ans. (b)" after other text (a tag line) is split in two."""
    out = []
    for ln in lines:
        m = ANS_RE.search(ln["text"])
        if m and m.start() > 0 and not ln["text"][:m.start()].strip().endswith(("(", "See")):
            head_len = len(ln["text"][:m.start()].rstrip())
            # cut runs at the character position of "Ans"
            full = "".join(t for t, _ in ln["runs"])
            lead = len(full) - len(full.lstrip())
            cut = lead + m.start()
            a, b, n = [], [], 0
            for t, bold in ln["runs"]:
                if n + len(t) <= cut:
                    a.append([t, bold])
                elif n >= cut:
                    b.append([t, bold])
                else:
                    a.append([t[:cut - n], bold])
                    b.append([t[cut - n:], bold])
                n += len(t)
            first = dict(ln, runs=a, text=runs_text(a))
            second = dict(ln, runs=b, text=runs_text(b))
            if first["text"]:
                out.append(first)
            out.append(second)
            continue
        out.append(ln)
    return out


def parse(lines):
    """Questions are anchored on their bold "Ans. (x)" lines. A chapter starts where question
    numbering restarts at 1; its title is the first big bold heading after the previous answer.
    Other big headings inside a chapter name sections."""
    lines = split_ans(lines)
    titles = find_chapters(lines)
    title_lines = {i for t in titles for i in range(t["line"], t["end_line"] + 1)}
    # "Ans. (x)" anchors a question whatever its weight (a few are printed regular, e.g. p293)
    ans_idx = [i for i, ln in enumerate(lines) if ANS_RE.match(ln["text"])]
    chapters, questions, problems = [], [], []
    last, lo = 0, 0
    section = None
    for ai in ans_idx:
        cands = [i for i in range(lo, ai) if i not in title_lines and qnum(lines[i]) is not None]
        heads = [t for t in titles if lo <= t["line"] < ai]
        start = next((i for i in cands if qnum(lines[i]) == last + 1), None)
        if start is None and (heads or not chapters):     # a new chapter always has a title
            start = next((i for i in cands if qnum(lines[i]) == 1 and (not heads or i > heads[0]["line"])), None)
        if start is None:                                  # a number was skipped or misprinted
            later = [i for i in cands if qnum(lines[i]) > last]
            if later:
                start = min(later, key=lambda i: qnum(lines[i]))
                problems.append(f"p{lines[start]['page']}: expected question {last + 1}, found {qnum(lines[start])}")
        if start is None:
            problems.append(f"p{lines[ai]['page']}: answer without a question: {lines[ai]['text'][:60]!r}")
            if questions:
                questions[-1]["expl_lines"] += lines[lo:ai + 1]
            lo = ai + 1
            continue
        n = qnum(lines[start])
        between = lines[lo:start]
        heads = [t for t in titles if lo <= t["line"] < start]
        heads = [t for t in heads if t["line"] < start]
        if not chapters or (n == 1 and n != last + 1 and heads):
            part = None
            if not chapters:      # the first chapter: the title nearest its questions (not the front matter)
                t = max((t for t in titles if t["line"] < start), key=lambda t: t["line"], default=None)
                lo = t["line"] if t else lo
                heads = [t] if t else []
            else:
                # a part banner ("B. Social Development") may come before the chapter title
                named = [h for h in heads if not re.match(r"^[A-H]\.\s", h["title"])]
                t = named[0] if named else heads[0]
                if named and named[0] is not heads[0]:
                    part = heads[0]["title"]
            if t is None:
                raise SystemExit("no chapter title before the first question")
            first = min(t["line"], heads[0]["line"]) if heads else t["line"]
            if questions and first >= lo:
                questions[-1]["expl_lines"] += lines[lo:first]
            sub = [{"title": h["title"], "page": h["page"]} for h in heads if h is not t and h["title"] != part]
            chapters.append({"num": len(chapters) + 1, "title": t["title"], "page": t["page"], "part": part,
                             "theory_lines": [dict(ln, head=(i in title_lines)) for i, ln in
                                              enumerate(lines[t["end_line"] + 1:start], t["end_line"] + 1)],
                             "sections": sub})
            section = None
            last = 0
        elif heads:
            first = heads[0]["line"]
            if questions:
                questions[-1]["expl_lines"] += lines[lo:first]
            section = heads[-1]["title"]
            chapters[-1]["sections"].append({"title": section, "page": heads[-1]["page"],
                                             "intro_lines": lines[heads[-1]["end_line"] + 1:start]})
        elif questions:
            questions[-1]["expl_lines"] += between
        if n != last + 1 and not (n == 1 and last == 0):
            problems.append(f"ch{len(chapters)} p{lines[start]['page']}: question {n} follows {last}")
        # a question printed without its "Ans." line runs straight into the next number
        # (Economy Q71 on p49): split there once the first question's options are complete
        cuts = [start]
        for i in range(start + 1, ai):
            if qnum(lines[i]) == n + len(cuts) and any(re.search(r"\(d\)|\(c\)", ln["text"]) for ln in lines[cuts[-1]:i]):
                cuts.append(i)
        for j, s_ in enumerate(cuts):
            e_ = cuts[j + 1] if j + 1 < len(cuts) else ai
            body = lines[s_:e_]
            tags = [ln for ln in body[1:] if is_tag(ln)]
            qlines = body[:1] + [ln for ln in body[1:] if not is_tag(ln)]
            if j + 1 < len(cuts):
                problems.append(f"ch{len(chapters)} p{lines[s_]['page']}: question {n + j} is printed without an answer")
                ans, tail = "", ""
            else:
                m = ANS_RE.match(lines[ai]["text"])
                # group(1) is the first bracket's letters (its ")" can be missing: "Ans. (c");
                # later "& (c)" groups add more
                letters = list(dict.fromkeys(
                    [x.lower() for x in re.findall(r"[a-eA-E*]", re.sub(r"\b(?:and|or)\b", " ", m.group(1)))]
                    + [x.lower() for x in re.findall(r"\(\s*([a-eA-E])\s*\)", m.group(0)[m.end(1):])]))
                ans, tail = ",".join(letters), lines[ai]["text"][m.end():].strip()
            questions.append({"ch": len(chapters), "num": n + j, "section": section, "page": lines[s_]["page"],
                              "qlines": qlines, "tags": tags, "ans": ans, "ans_tail": tail, "expl_lines": [],
                              "ans_page": lines[ai]["page"]})
        n += len(cuts) - 1
        last = n
        lo = ai + 1
    if questions:
        questions[-1]["expl_lines"] += lines[lo:]
    return chapters, questions, problems, ans_idx


# ------------------------------------------------------------------ structure: blocks, questions
BULLET = re.compile(r"^(?:\*|•|–|—|\((?:i{1,3}|iv|vi{0,3}|ix|x)\)|\d{1,2}\s*\.|\(\d{1,2}\)|\([a-e]\)|[ivx]{1,4}\.|"
                    r"(?:Assertion|Reason)\s*\(?[AR]?\)?\s*:)\s*")
OPT_START = re.compile(r"^\(\s*a\s*\)")
CODE_LINE = re.compile(r"^Codes?\s*(?:[:\-–—]|$|A\s+B\s+C)", re.I)
# an instruction line starts its own paragraph, not the tail of the last statement
INSTR = re.compile(r"^(?:Select|Choose|Which|Use the code|Mark the|Find the|Give the|Answer using|In the light of)\b")
SEE_RE = re.compile(r"^see (?:the )?(?:explanation|answer) of (?:the )?(?:above|previous|preceding)", re.I)
# "U.P.P.C.S.", "[U.P.P.C.S. (Pre)-2018]", "UPPCS", "U.P. Lower Sub." -- not "U.P.S.C." (the national exam)
UP_TAG = re.compile(r"^\W*(?:[\w\s]*?\s)?(?:U\.\s?P\.(?!\s?S\.?\s?C)|UP\b|UPP(?:CS|SC)\b|U\.P\b|Uttar Pradesh)")
# function words that may be pieces of a glued line ("had", "under", "one", "be" are left out:
# they sit inside real words: "Mantriparis|had", "under|written", "some|one")
FUNCTION_WORDS = {"the", "of", "and", "to", "in", "is", "was", "are", "were", "which", "who", "whom", "whose",
                  "what", "among", "following", "by", "for", "with", "on", "at", "from", "as"}
EDGE_WORDS = {"the", "of", "and", "which", "who", "whose", "from", "with", "are", "was", "were", "by", "for"}
REAL_COMPOUNDS = {"notwithstanding", "nevertheless", "nonetheless", "whatsoever", "inasmuch", "insofar",
                  "thereafter", "hereinafter", "whereabouts", "heretofore", "henceforth", "furthermore"}
JOIN_NEVER = {"inspite", "chiefofthe", "setup"}     # pairs the book prints both ways; keep them apart
TIDY = [re.compile(p) for p in (r"\S( +)[,;:)?.](?=\s|$)", r"\(( +)", r"( ) ")]


def tidy(runs):
    """Merge runs, collapse spaces, drop spaces before punctuation; keep bold boundaries."""
    s = "".join(t for t, _ in runs)
    flags = [b for t, b in runs for _ in t]
    keep = [True] * len(s)
    for pat in TIDY:
        for m in pat.finditer(s):
            for k in range(m.start(1), m.end(1)):
                keep[k] = False
    res = []
    for ch, b, k in zip(s, flags, keep):
        if not k:
            continue
        if res and res[-1][1] == b:
            res[-1][0] += ch
        else:
            res.append([ch, b])
    # "Con|st|itution": a ligature glyph set in the regular font inside a bold word stays bold
    if any(not b and 0 < k < len(res) - 1 and re.fullmatch(r"[a-z]{1,3}", t) for k, (t, b) in enumerate(res)):
        for k in range(1, len(res) - 1):
            if not res[k][1] and res[k - 1][1] and res[k + 1][1] and re.fullmatch(r"[a-z]{1,3}", res[k][0]) \
                    and res[k - 1][0][-1:].isalpha() and res[k + 1][0][:1].isalpha():
                res[k][1] = True
        merged = []
        for t, b in res:
            if merged and merged[-1][1] == b:
                merged[-1][0] += t
            else:
                merged.append([t, b])
        res = merged
    if res:
        res[0][0] = res[0][0].lstrip()
        res[-1][0] = res[-1][0].rstrip()
    return [r for r in res if r[0]]


def join_line(runs, ln):
    """Append a printed line to a paragraph. A word broken at the line end keeps a marker that is
    resolved against the book's vocabulary later ("Gov-|ernment" joins, "high-|speed" keeps)."""
    text = runs_text(runs)
    if re.search(r"[A-Za-z]-$", text) and ln["text"][:1].isalpha():
        runs = [list(r) for r in runs]
        for r in reversed(runs):
            if r[0].rstrip():
                r[0] = r[0].rstrip()[:-1] + "\x02"
                break
        return runs + [list(r) for r in ln["runs"]]
    both_bold = bool(runs and runs[-1][1] and ln["runs"] and ln["runs"][0][1])
    return runs + [[" ", both_bold]] + [list(r) for r in ln["runs"]]


def split_runs(runs, sep):
    parts, cur = [], []
    for t, b in runs:
        pieces = t.split(sep)
        for i, piece in enumerate(pieces):
            if i:
                parts.append(cur)
                cur = []
            if piece:
                cur.append([piece, b])
    parts.append(cur)
    return parts


def blocks_from_lines(lines, facts=False):
    """Printed lines -> blocks: headings, paragraphs, list items, tables (rows of cells).
    facts=True splits theory paragraphs at the book's "*" markers into one fact per item."""
    blocks, para, prev = [], None, None
    right = {}
    for ln in lines:
        k = (ln["page"], ln["col"])
        right[k] = max(right.get(k, 0), ln["x1"])
    for ln in lines:
        if not ln["text"]:
            continue
        if ln.get("head") or (ln["bold"] > 0.85 and ln["size"] >= HEAD_SIZE and len(ln["text"]) < 120):
            blocks.append({"kind": "h", "runs": [list(r) for r in ln["runs"]]})
            para, prev = None, None
            continue
        if len(ln["cells"]) >= 2:
            if blocks and blocks[-1]["kind"] == "table" and prev is not None and prev.get("cells"):
                blocks[-1]["rows"].append(ln["cells"])
            else:
                blocks.append({"kind": "table", "rows": [ln["cells"]]})
            para, prev = None, ln
            continue
        starts_own = BULLET.match(ln["text"]) or INSTR.match(ln["text"]) or CODE_LINE.match(ln["text"])
        # "Reason (R):   Britain had become weak during the" / "second World War.": the label's gap
        # made the first line look like a one-row table; the indented next line continues it
        if prev is not None and prev.get("cells") and not starts_own and blocks and blocks[-1]["kind"] == "table" \
                and len(blocks[-1]["rows"]) == 1 and ln["x0"] > prev["x0"] + 8 and ln["page"] == prev["page"]:
            merged = []
            for c in blocks[-1]["rows"][0]:
                merged += ([[" ", False]] if merged else []) + [list(r) for r in c]
            para = {"kind": "p", "runs": join_line(merged, ln)}
            blocks[-1] = para
            prev = ln
            continue
        prev_short = prev is not None and (prev["x1"] < right[(prev["page"], prev["col"])] - 30
                                           or prev["text"].endswith(":"))
        if para is None or starts_own or prev_short or (prev is not None and prev.get("cells")):
            para = {"kind": "p", "runs": [list(r) for r in ln["runs"]]}
            blocks.append(para)
        else:
            para["runs"] = join_line(para["runs"], ln)
        prev = ln
    out = []
    for b in blocks:
        if b["kind"] == "table":
            rows = [[tidy(c) for c in row] for row in b["rows"]]
            if len(rows) == 1:
                # a single gapped line is a spaced-out line, not a table
                merged = []
                for c in rows[0]:
                    merged += ([[" ", False]] if merged else []) + c
                out.append({"kind": "p", "runs": tidy(merged)})
                continue
            out.append({"kind": "table", "rows": rows})
            continue
        runs = tidy(b["runs"])
        if not runs:
            continue
        text = runs_text(runs)
        if facts and b["kind"] == "p" and "*" in text:
            for part in split_runs(runs, "*"):
                part = tidy(part)
                if runs_text(part):
                    out.append({"kind": "li", "runs": part})
            continue
        lead = re.match(r"^[*•]\s*", text)
        if b["kind"] == "p" and lead:
            out.append({"kind": "li", "runs": tidy(strip_runs(runs, lead.end()))})
            continue
        out.append({"kind": b["kind"], "runs": runs})
    return fix_match_rows(out)


ROW_RE = re.compile(r"^(\(?[A-Da-d][.)]\s*\S.*?)\s+((?:\d{1,2}\s*\.|\((?:i{1,3}|iv|vi?)\)|(?:i{1,3}|iv|vi?)\.)\s*\S.*)$")
LABEL_RE = re.compile(r"^\(?[A-Da-d][.)]")


def cut_runs(runs, at):
    a, b, n = [], [], 0
    for t, bold in runs:
        if n + len(t) <= at:
            a.append([t, bold])
        elif n >= at:
            b.append([t, bold])
        else:
            a.append([t[:at - n], bold])
            b.append([t[at - n:], bold])
        n += len(t)
    return tidy(a), tidy(b)


def fix_match_rows(blocks):
    """List-I / List-II rows printed with a narrow gap come out as paragraphs ("(b) Poona Sarvjanik
    Sabha 2. Surendra Nath Banerji"). Next to a table (or another such row) they are split at the
    List-II marker into a two-cell row; a table row with no label right after a labelled row
    continues it ("Association | Ranade" under "(c) Bombay Presidency | 3. Mahadev Govind")."""
    rows = [i for i, b in enumerate(blocks) if b["kind"] == "p" and ROW_RE.match(runs_text(b["runs"]))]
    near = lambda i: any(0 <= j < len(blocks) and (j in rows or (blocks[j]["kind"] == "table" and
                         len(blocks[j]["rows"][0]) == 2)) for j in (i - 1, i + 1))
    for i in [i for i in rows if near(i)]:
        runs = blocks[i]["runs"]
        s = "".join(t for t, _ in runs)
        m = ROW_RE.match(s.strip())
        blocks[i] = {"kind": "table", "rows": [list(cut_runs(runs, len(s) - len(s.lstrip()) + m.start(2)))]}
    out = []
    for b in blocks:
        if b["kind"] == "table" and out and out[-1]["kind"] == "table" \
                and len(b["rows"][0]) == len(out[-1]["rows"][0]) == 2:
            out[-1] = {"kind": "table", "rows": out[-1]["rows"] + b["rows"]}
        else:
            out.append(b)
    for b in out:
        if b["kind"] != "table":
            continue
        rows_ = []
        for row in b["rows"]:
            prev = rows_[-1] if rows_ else None
            if prev and len(row) == len(prev) and LABEL_RE.match(runs_text(prev[0])) \
                    and not LABEL_RE.match(runs_text(row[0])) and runs_text(row[0])[:1].isalpha() \
                    and not re.match(r"(?:List|Codes?)\b", runs_text(row[0])):
                rows_[-1] = [tidy(p + [[" ", False]] + c) if runs_text(c) else p for p, c in zip(prev, row)]
            else:
                rows_.append(row)
        b["rows"] = rows_
    return out


def strip_tail(runs, n):
    """Drop the last n characters of a run list."""
    out, total = [], sum(len(t) for t, _ in runs)
    keep = total - n
    for t, b in runs:
        if keep <= 0:
            break
        out.append([t[:keep], b])
        keep -= len(t)
    return out


def option_text(lines):
    """The option lines as one run list, plus the positions where a printed line or a table cell
    (a wide gap: "(a) Both (a) and (b)      (b) Only (b)") begins. A line broken at a hyphen keeps
    the \\x02 marker that resolve_breaks joins ("Deprecia-|tion")."""
    runs, anchors = [], set()

    def at():
        return sum(len(t) for t, _ in runs)
    for ln in lines:
        if runs:
            prev = "".join(t for t, _ in runs).rstrip()
            if re.search(r"[A-Za-z]-$", prev) and ln["text"][:1].isalpha():
                for r in reversed(runs):
                    if r[0].rstrip():
                        r[0] = r[0].rstrip()[:-1] + "\x02"
                        break
            else:
                runs.append([" ", False])
        for k, cell in enumerate(ln["cells"] or [ln["runs"]]):
            if k:
                runs.append([" ", False])
            lead = len("".join(t for t, _ in cell)) - len("".join(t for t, _ in cell).lstrip())
            anchors.add(at() + lead)
            runs += [list(r) for r in cell]
    return runs, anchors


def split_options(lines):
    """'(a) IX (b) VI' or one option per line -> {'a': runs, ...}. Markers at the start of a line
    or cell come first, so an option that names others ("Both (a) and (b)", "Article 102 (1) (b)")
    stays whole; markers anywhere in the text are the fallback ("(a) IX (b) VI (c) ...")."""
    runs, anchors = option_text(lines)
    s = "".join(t for t, _ in runs)
    flags = [b for t, b in runs for _ in t]

    def scan(anchored):
        seq, want = [], "abcde"
        for m in re.finditer(r"\(\s*([a-e])\s*\)\s*", s):
            if want and m.group(1) == want[0] and (not anchored or m.start() in anchors):
                seq.append((m.start(), m.end(), m.group(1)))
                want = want[1:]
        return seq
    seq = scan(True)
    if len(seq) < 4:
        seq = scan(False)
    opts = {}
    for j, (st, en, letter) in enumerate(seq):
        stop = seq[j + 1][0] if j + 1 < len(seq) else len(s)
        piece = tidy([[c, b] for c, b in zip(s[en:stop], flags[en:stop])])
        txt = runs_text(piece)
        # the answer letter printed after the last option ("(d) Akbar (d)"), but not a letter the
        # option itself names ("Neither (a) nor (b)", "Article 102 (1) (a)")
        tail = re.search(r"\s*\(\s*[a-e]\s*\)\s*$", txt)
        if tail and letter == seq[-1][2] and tail.start() > 0 \
                and not re.search(r"(?:\band|\bnor|\bor|&|,|\)|\bboth)\s*$", txt[:tail.start()], re.I):
            piece = tidy(strip_tail(piece, len(txt) - tail.start()))
        opts[letter] = piece
    return opts


# a loose option marker: "(a)", "(C)", "b)" (its "(" printed in a dropped Hindi font), "(h)" for (b)
LOOSE_OPT = re.compile(r"(?:^|(?<=\s))\(?\s*([a-hA-H])\s*\)\s*")
LOOSE_OPT_START = re.compile(r"^\(?\s*[a-hA-H]\s*\)")


def split_options_loose(lines):
    """Options whose printed letters are wrong. Used only when the strict a->b->c->d scan fails.
    When the first marker is (a) and the letters are one each of a..d (or a..e), the printed
    letters are right and only the layout is odd ("(a) (b) / (d) (c)"). Otherwise the book
    misprinted the letters ("(a) (b) (b) (d)", "(c) (b) (c) (d)", "(b) (c) (d) (a)") and position
    is the only reliable guide: the n-th option is letter n. Returns (options, note)."""
    runs, _ = option_text(lines)
    s = "".join(t for t, _ in runs)
    flags = [b for t, b in runs for _ in t]
    marks = [(m.start(), m.end(), m.group(1).lower()) for m in LOOSE_OPT.finditer(s)]
    if marks and not s[marks[-1][1]:].strip():
        marks = marks[:-1]          # the answer letter printed after the last option
    printed = "".join(x[2] for x in marks)
    if len(marks) not in (4, 5):
        return None, None
    if printed[0] == "a" and sorted(printed) == list("abcde"[:len(marks)]):
        letters, note = printed, None
    else:
        letters = "abcde"[:len(marks)]
        note = (f"The book prints these option letters as ({'), ('.join(printed)}); "
                "they are lettered here by position.")
    opts = {}
    for j, (st, en, _) in enumerate(marks):
        stop = marks[j + 1][0] if j + 1 < len(marks) else len(s)
        opts[letters[j]] = tidy([[c, b] for c, b in zip(s[en:stop], flags[en:stop])])
    if any(not runs_text(v) for v in opts.values()):
        return None, None
    return dict(sorted(opts.items())), note


def finish_question(q):
    ql = q["qlines"]
    first = ql[0]
    full = "".join(t for t, _ in first["runs"])
    num = QNUM_RE.match(first["text"]) or re.match(r"^(\d{1,4})\s+", first["text"])
    cut = (len(full) - len(full.lstrip())) + (num.end() if num else 0)
    stem_lines = [dict(first, runs=strip_runs(first["runs"], cut), text=first["text"][num.end() if num else 0:])]
    i = 1
    # the bold stem ends where statements, Assertion/Reason or a list begin
    while i < len(ql) and ql[i]["bold"] > 0.6 and not OPT_START.match(ql[i]["text"]) and not ql[i]["cells"] \
            and not BULLET.match(ql[i]["text"]) and not re.match(r"List\s*[-–]?\s*I\b", ql[i]["text"]):
        stem_lines.append(ql[i])
        i += 1
    rest = ql[i:]
    # Options start at the first regular-weight "(a)" line after a "Code(s):" line. Before it, lines
    # starting "(a)".."(d)" are list rows (printed "(A) Atul Kohli", read "(a)" from the text layer).
    codes = [k for k, ln in enumerate(rest) if CODE_LINE.match(ln["text"])]
    starts = [k for k, ln in enumerate(rest) if OPT_START.match(ln["text"])]
    after = [k for k in starts if not codes or k > codes[-1]]
    plain = [k for k in after if rest[k]["bold"] < 0.5]
    oi = (plain or after or starts or [None])[0]
    mid, opt_lines = (rest[:oi], rest[oi:]) if oi is not None else (rest, [])
    options, opt_note = split_options(opt_lines), None
    if "".join(sorted(options)) not in ("abcd", "abcde"):
        # misprinted letters, or options set out with no line starting "(a)": then the options
        # are the trailing lines of the question that each start with an option marker
        cand = opt_lines
        if oi is None:
            k = len(rest)
            while k > 0 and LOOSE_OPT_START.match(rest[k - 1]["text"]):
                k -= 1
            cand = rest[k:]
        loose, note = split_options_loose(cand) if cand else (None, None)
        if loose:
            options, opt_note = loose, note
            if oi is None:
                mid = rest[:len(rest) - len(cand)]
    stem_runs = []
    for ln in stem_lines:
        stem_runs = join_line(stem_runs, ln) if stem_runs else [list(r) for r in ln["runs"]]
    tags = [re.sub(r"\s+", " ", ln["text"]).strip() for ln in q["tags"]]
    expl_lines = list(q["expl_lines"])
    if q["ans_tail"]:
        expl_lines = [{"page": q["ans_page"], "col": 0, "base": 0, "x0": 0, "x1": 0, "size": 10,
                       "runs": [[q["ans_tail"], False]], "text": q["ans_tail"], "bold": 0, "cells": []}] + expl_lines
    return {"ch": q["ch"], "num": q["num"], "page": q["page"], "section": q["section"],
            "stem": tidy(stem_runs), "mid": blocks_from_lines(mid), "options": options, "opt_note": opt_note,
            "tags": tags, "up": any(UP_TAG.match(t) for t in tags),
            "years": sorted({int(y) for t in tags for y in re.findall(r"(?:19|20)\d\d", t)}),
            "ans": q["ans"], "expl": blocks_from_lines(expl_lines)}


def resolve_breaks(data):
    """A word broken at a line end: keep the hyphen if the hyphenated form occurs elsewhere in the
    book, join if the joined word occurs (or the second part starts in lower case), else keep it."""
    runs_all = []

    def walk(o):
        if isinstance(o, dict):
            for v in o.values():
                walk(v)
        elif isinstance(o, list):
            if len(o) == 2 and isinstance(o[0], str) and isinstance(o[1], bool):
                runs_all.append(o)
            else:
                for v in o:
                    walk(v)
    walk(data)
    full = " ".join(r[0] for r in runs_all)
    clean = re.sub(r"\w*\x02\w*", " ", full)
    vocab = set(w.lower() for w in re.findall(r"[A-Za-z]+", clean))
    hyph = set(w.lower() for w in re.findall(r"[A-Za-z]+-[A-Za-z]+", clean))

    def one(m):
        a, b = m.group(1), m.group(2)
        if f"{a}-{b}".lower() in hyph:
            return f"{a}-{b}"
        if (a + b).lower() in vocab:
            return a + b
        return f"{a}-{b}" if b[:1].isupper() else a + b
    for r in runs_all:
        if "\x02" in r[0]:
            r[0] = re.sub(r"([A-Za-z]+)\x02([A-Za-z]+)", one, r[0]).replace("\x02", "-")

    # a stray letter split off a word by the PDF's own spacing ("p opulation", "b e"): join it
    # when the joined word occurs elsewhere in the book
    def glue(m):
        a, b = m.group(1), m.group(2)
        return a + b if (a + b).lower() in vocab and (a + b).lower() not in ("ab", "ah") else m.group(0)
    for r in runs_all:
        r[0] = re.sub(r"\b([b-hj-zB-HJ-Z]) ([a-z]{2,})\b", glue, r[0])

    # "ofIndia", "ofthe", "toArticle": the PDFs set a short word tight against the next one, so no
    # gap shows. Real words that begin with "of" are off... and often...; for the other short
    # words only a following capital ("inApril") is taken as a glue.
    counts = Counter(w.lower() for w in re.findall(r"[A-Za-z]+", clean))

    def unglue(m):
        rest = m.group(1)
        return "of " + rest if rest[0].isupper() or counts[rest.lower()] >= 3 else m.group(0)

    # "estab lished", "Mega sthenes": a word split in two where neither half occurs on its own
    # (2 times at most, the split itself included) and the whole word occurs elsewhere; or
    # "As sertion", "an swer", "st atements": the same glitch repeated, so the fragment is not rare,
    # but it never occurs outside this pair, and the whole word is common ("set up" stays: "set"
    # occurs alone too)
    pairs = Counter((a.lower(), b.lower()) for a, b in re.findall(r"\b([A-Za-z]{2,}) (?=([a-z]{2,})\b)", clean))

    def join_split(m):
        # the second word is only looked at, not consumed, so every adjacent pair gets a turn
        # ("correct an swer": "correct an" is checked, then "an swer")
        a, b = m.group(1), m.group(2)
        whole, ca, cb = counts[(a + b).lower()], counts[a.lower()], counts[b.lower()]
        n = pairs[(a.lower(), b.lower())]
        if (whole >= 2 and ca <= 2 and cb <= 2) or \
                (whole >= 5 and whole >= 3 * n and n in (ca, cb) and (a + b).lower() not in JOIN_NEVER):
            return a
        return m.group(0)
    for r in runs_all:
        r[0] = re.sub(r"\bof(?!f|ten)([A-Za-z]+)", unglue, r[0])
        r[0] = re.sub(r"\b(in|and|the|to|by|for|from|with|at|on|is|was|as)(?=[A-Z][a-z]{2,})", r"\1 ", r[0])
        r[0] = re.sub(r"\b([A-Za-z]{2,}) (?=([a-z]{2,})\b)", join_split, r[0])

    # Bold lines set so tight that no gap shows: "WhoamongthefollowingkingshadfoundedPataliputra",
    # "UndertheNationalRural HealthMission". Only bold runs; a token is split into words the book
    # prints at least 5 times, and only when the split has two or more function words (a long
    # real word such as "Dharmachakrapravartana" has none). Two common words glued by case
    # ("HealthMission") are split too.
    common = {w for w, n in counts.items() if n >= 5}

    def segment(tok):
        low = tok.lower()
        best = [None] * (len(low) + 1)
        best[0] = []
        for i in range(len(low)):
            if best[i] is None:
                continue
            for j in range(i + 1, min(len(low), i + 20) + 1):
                w = low[i:j]
                # no one- or two-letter pieces except real function words ("national|is|a|tion")
                if w in common and (len(w) >= 3 or w in FUNCTION_WORDS) \
                        and (best[j] is None or len(best[i]) + 1 < len(best[j])):
                    best[j] = best[i] + [w]
        return best[-1]

    def unglue_long(m):
        tok = m.group(0)
        if counts[tok.lower()] > 1 or tok.lower() in REAL_COMPOUNDS:
            return tok
        seg = segment(tok)
        if not seg or len(seg) < 2:
            return tok
        nf = sum(w in FUNCTION_WORDS for w in seg)
        content = [w for w in seg if w not in FUNCTION_WORDS]
        ok = (
            # "who among the following kings had founded Pataliputra"
            (nf >= 2 and len(seg) >= 3)
            # "United States of America": capitals inside the token show the glue
            or (nf >= 1 and len(seg) >= 3 and any(ch.isupper() for ch in tok[1:]) and all(len(w) >= 4 for w in content))
            # "consider the", "with reference", "developed by": a function word that rarely begins
            # a real word ("in", "to", "is" do: "in|formation", "in|equality")
            or (len(seg) == 2 and any(w in EDGE_WORDS for w in seg) and all(len(w) >= 5 for w in content))
            # "advisory jurisdiction": two long lower-case words (names are capitalised:
            # "Hemchandraacharya", "Adityavardhana" stay whole)
            or (len(seg) == 2 and tok.islower() and all(len(w) >= 6 for w in seg)))
        if not ok:
            return tok
        out, k = [], 0
        for w in seg:
            out.append(tok[k:k + len(w)])
            k += len(w)
        return " ".join(out)

    # "ChiefJustice", "RigVeda", "SaudiArabia": two common words glued by case (in these books every
    # such pair is a glue; checked against all three)
    def camel(m):
        a, b = m.group(1), m.group(2)
        if len(a) > 2 and a.lower() in common and b.lower() in common:
            return a + " " + b
        return m.group(0)
    for r in runs_all:
        # tight-set bold lines glue at 10 letters; in regular text only long tokens are suspects
        r[0] = re.sub(r"[A-Za-z]{10,}" if r[1] else r"[A-Za-z]{14,}", unglue_long, r[0])
        r[0] = re.sub(r"\b([A-Za-z]*[a-z])([A-Z][a-z]{2,})\b", camel, r[0])


def main():
    key = sys.argv[1]
    book = BOOKS[key]
    lines = read_lines(book)
    chapters, questions, problems, ans_idx = parse(lines)
    print(f"{key}: {len(lines)} lines, {len(ans_idx)} answers, {len(questions)} questions, {len(chapters)} chapters")
    qs = [finish_question(q) for q in questions]
    for i, q in enumerate(qs, 1):
        q["id"] = f"q{i:05d}"
    # print the text layer cannot carry (stacked fractions), read from the page image: pq_books.py
    fixes = book.get("corrections", {})
    for q in qs:
        fx = fixes.get(f"{q['ch']:02d}-{q['num']:03d}")
        if fx:
            if "mid" in fx:
                q["mid"] = fx["mid"]
            if "options" in fx:
                q["options"] = {k: [[v, False]] for k, v in fx["options"].items()}
    unused = set(fixes) - {f"{q['ch']:02d}-{q['num']:03d}" for q in qs}
    if unused:
        raise SystemExit(f"corrections for questions that do not exist: {sorted(unused)}")
    # "See the explanation of the above question" -> the nearest earlier question with an explanation
    last_real = {}
    for q in qs:
        text = " ".join(runs_text(b.get("runs", [])) for b in q["expl"] if b["kind"] != "table").strip()
        if q["expl"] and SEE_RE.match(text) and len(text) < 120:
            q["see"] = last_real.get(q["ch"])
        elif q["expl"]:
            last_real[q["ch"]] = q["id"]
    chs = []
    for c in chapters:
        chs.append({"num": c["num"], "title": re.sub(r"^[A-H]\.\s+", "", c["title"]), "part": c.get("part"),
                    "page": c["page"], "theory": blocks_from_lines(c["theory_lines"], facts=True),
                    "sections": [{"title": s_["title"], "page": s_["page"],
                                  "intro": blocks_from_lines(s_.get("intro_lines", []), facts=True)}
                                 for s_ in c["sections"]]})
    data = {"book": key, "name": book["name"], "pdf": book["pdf"].name, "pages": book["pages"],
            "chapters": chs, "questions": qs, "problems": problems}
    resolve_breaks(data)
    out = book_dir(key) / "source.json"
    out.write_text(json.dumps(data, ensure_ascii=False, indent=0), encoding="utf-8")
    print(f"  {sum(1 for q in qs if q['up'])} from UP exams; {sum(1 for q in qs if len(q['options']) >= 4)} with 4+ options; "
          f"{sum(1 for q in qs if not q['ans'])} without a printed answer; {sum(1 for q in qs if q.get('see'))} 'see above'")
    for c in chs:
        n = sum(1 for q in qs if q["ch"] == c["num"])
        print(f"  {c['num']:3d} p{c['page']:4d} {n:4d} q  theory {len(c['theory']):3d} blocks  {c['title'][:60]}")
    print("problems:", len(problems))
    for p_ in problems[:40]:
        print("  ", p_)
    print("wrote", out)


if __name__ == "__main__":
    main()
