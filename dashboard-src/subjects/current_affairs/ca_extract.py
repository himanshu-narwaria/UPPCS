"""Step 1: read the Drishti PDF by font and layout, and write ca_source.json.

What the fonts mean in this issue (checked page by page):
  * Points to Remember (chapter 1): each bullet is one question in regular weight followed by
    its answer in bold. Question and answer are separated by weight, not by position, because
    the PDF sometimes places the answer in the middle of the question's lines.
    Light text inside the bold answer's brackets belongs to the answer ("Vivek Aggarwal (July 2026
    to June 2027)"); light text ending in "?" is the end of the question.
  * Articles (chapters 2-10): BookmanOldStyle-Bold 13 = article title; Garamond-Bold 11-14 =
    sub-heading; TimesNewRomanPS-BoldMT 19 = section heading; MonotypeSorts glyph = bullet;
    small Wingdings glyph = sub-bullet; bold words inside text = the answer-worthy facts.
    Bold body-size text after a heading-box glyph is a minor heading; a centred bold one-line
    caption ("Finnie", "Result –") is its own paragraph.
  * Tables have drawn cell borders (inside nested form objects), so cells are rebuilt from them.
    A cell with no rule under it spans the next row (rowspan). Body text the table was printed
    over (a rule cutting through a word) is taken out of the table. Text struck through by a row
    rule belongs to the row above. Six tables that drift against their borders are kept line by
    line (DRIFTED_TABLE_PAGES).
  * Reading order is by bands: full-width banners, headings and tables split a page into bands;
    a line that merely overflows its column (printing over the next column) does not.
  * pdfium marks every line-end hyphen as soft (\\x02); most are real compounds ("high-speed"),
    so the hyphen is kept unless only the joined word occurs elsewhere in the book.
  * Watermarks (Lato, Times-Roman, LiberationSerif) and the running header are dropped.

Run:  python ca_extract.py
"""
import ctypes
import json
import re
from collections import Counter
from pathlib import Path

import pypdfium2 as pdfium
import pypdfium2.raw as raw

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
PDF = ROOT / "Drishti-current affairs" / "Drishti (2) English 2026 (2615-M).pdf"
OUT = HERE / "ca_source.json"

# File-page ranges of the ten chapters (checked against the chapter opening pages).
CHAPTERS = [
    (1, "Points to Remember", "याद रखने योग्य बिंदु", 4, 17),
    (2, "National Affairs", "राष्ट्रीय परिदृश्य", 18, 52),
    (3, "International Affairs", "अंतरराष्ट्रीय परिदृश्य", 53, 86),
    (4, "Economic Affairs", "आर्थिक परिदृश्य", 87, 120),
    (5, "Science & Technology Affairs", "वैज्ञानिक परिदृश्य", 121, 143),
    (6, "Environmental Affairs", "पर्यावरण परिदृश्य", 144, 156),
    (7, "Uttar Pradesh Current Affairs", "उत्तर प्रदेश परिदृश्य", 157, 168),
    (8, "Bihar Current Affairs", "बिहार परिदृश्य", 169, 177),
    (9, "Short News, Awards and Persons", "संक्षिप्त समाचार, पुरस्कार एवं व्यक्ति", 178, 220),
    (10, "Sports News", "खेल परिदृश्य", 221, 241),
]
SKIP_FONTS = ("Lato", "Times-Roman", "LiberationSerif")
LIGATURE = {0x6600: "f", 0x6900: "i", 0x6C00: "l"}


def chapter_of(page):
    for num, _, _, a, b in CHAPTERS:
        if a <= page <= b:
            return num
    return None


def clean_font(name):
    return re.sub(r"^[A-Z]{6}\+", "", name)


# ------------------------------------------------------------------ low level: characters and table grids
def page_chars(doc, index):
    tp = doc[index].get_textpage()
    buf = ctypes.create_string_buffer(256)
    flags = ctypes.c_int()
    out = []
    for i in range(tp.count_chars()):
        u = raw.FPDFText_GetUnicode(tp.raw, i)
        raw.FPDFText_GetFontInfo(tp.raw, i, buf, 256, ctypes.byref(flags))
        font = clean_font(buf.value.decode(errors="ignore"))
        if any(font.startswith(s) for s in SKIP_FONTS):
            continue
        size = round(raw.FPDFText_GetFontSize(tp.raw, i), 1)
        l, r_, b, t = (ctypes.c_double() for _ in range(4))
        raw.FPDFText_GetCharBox(tp.raw, i, ctypes.byref(l), ctypes.byref(r_), ctypes.byref(b), ctypes.byref(t))
        ch = chr(u)
        if font == "Rupee":
            ch = "₹"
        elif u in LIGATURE:
            ch = LIGATURE[u]
        elif 0x3000 <= u < 0xF000:
            raise SystemExit(f"Unknown glyph U+{u:04X} on file page {index + 1}; add it to LIGATURE")
        ox, oy = ctypes.c_double(), ctypes.c_double()
        raw.FPDFText_GetCharOrigin(tp.raw, i, ctypes.byref(ox), ctypes.byref(oy))
        out.append({"c": ch, "u": u, "font": font, "size": size, "x": (l.value + r_.value) / 2,
                    "l": l.value, "r": r_.value, "base": oy.value,
                    "y": (b.value + t.value) / 2, "top": t.value, "bot": b.value, "bold": "Bold" in font})
    return out


def _walk(obj, acc):
    if raw.FPDFPageObj_GetType(obj) == raw.FPDF_PAGEOBJ_FORM:
        for i in range(raw.FPDFFormObj_CountObjects(obj)):
            _walk(raw.FPDFFormObj_GetObject(obj, i), acc)
    elif raw.FPDFPageObj_GetType(obj) == raw.FPDF_PAGEOBJ_PATH:
        l, b, r_, t = (ctypes.c_float() for _ in range(4))
        raw.FPDFPageObj_GetBounds(obj, ctypes.byref(l), ctypes.byref(b), ctypes.byref(r_), ctypes.byref(t))
        acc.append((l.value, b.value, r_.value, t.value))


def _cluster(values, gap=3.0):
    out = []
    for v in sorted(values):
        if not out or v - out[-1][-1] > gap:
            out.append([v])
        else:
            out[-1].append(v)
    return [sum(c) / len(c) for c in out]


def table_grids(doc, index):
    """Tables = bordered areas with internal vertical rules. This PDF draws cell borders row by
    row, so a row whose internal rule is missing has merged (spanning) cells."""
    page = doc[index]
    paths = []
    for i in range(raw.FPDFPage_CountObjects(page.raw)):
        _walk(raw.FPDFPage_GetObject(page.raw, i), paths)
    verts = [((l + r_) / 2, b, t) for l, b, r_, t in paths if r_ - l < 3 and t - b > 5]
    hors = [((b + t) / 2, l, r_) for l, b, r_, t in paths if t - b < 3 and r_ - l > 5]
    rects = [(l, b, r_, t) for l, b, r_, t in paths if r_ - l > 40 and t - b > 10]
    grids = []
    for l, b, r_, t in rects:
        if not [x for x, vb, vt in verts if l + 4 < x < r_ - 4 and vb >= b - 2 and vt <= t + 2]:
            continue
        # grow the area to every border segment that touches it
        changed = True
        while changed:
            changed = False
            for x, vb, vt in verts:
                if l - 2 <= x <= r_ + 2 and vt >= b - 3 and vb <= t + 3 and (vb < b - 0.5 or vt > t + 0.5):
                    b, t, changed = min(b, vb), max(t, vt), True
        if any(abs(g["box"][0] - l) < 2 and abs(g["box"][1] - b) < 2 and abs(g["box"][2] - r_) < 2
               and abs(g["box"][3] - t) < 2 for g in grids):
            continue
        mine = [(x, vb, vt) for x, vb, vt in verts if l - 2 <= x <= r_ + 2 and vb >= b - 3 and vt <= t + 3]
        cols = _cluster([l, r_] + [x for x, _, _ in mine])
        cols[0], cols[-1] = l, r_
        ys = _cluster([y for y, hl, hr in hors if b - 2 <= y <= t + 2 and hl >= l - 2 and hr <= r_ + 2])
        rows = sorted(set([b] + [y for y in ys if b + 4 < y < t - 4] + [t]), reverse=True)
        hsegs = [(y, hl, hr) for y, hl, hr in hors if b - 2 <= y <= t + 2 and hl >= l - 2 and hr <= r_ + 2]
        grids.append({"box": (l, b, r_, t), "cols": cols, "rows": rows, "verts": mine, "hsegs": hsegs})
    grids = [g for g in grids if not any(o is not g and o["box"][0] >= g["box"][0] - 1 and o["box"][2] <= g["box"][2] + 1
                                         and o["box"][1] >= g["box"][1] - 1 and o["box"][3] <= g["box"][3] + 1
                                         and o["box"] != g["box"] for o in grids)]
    return grids


def in_grid(ch, g):
    l, b, r_, t = g["box"]
    # a table that reaches the right margin keeps text that overflows its last column
    # ("Microeconomic foundations of macroeconomic stabilisation" runs off the page on p61)
    right = 1e9 if r_ > 495 else r_ + 1
    if id(ch) in g.get("not_table", ()):
        return False
    # the last row's text sometimes sits on the bottom border ("Pvt. Ltd., Dholera" on p102)
    return l - 1 <= ch["x"] <= right and b - 3 <= ch["y"] <= t + 1


def mark_overprinted_text(chars, grids):
    """Text inside a table's box that a drawn column rule cuts through mid-word is not table text:
    it is body text the table was printed over (the NFHS-6 bullets under the CRS table on p95,
    "The pe|rcentage ..."). Real cell text never crosses its own column rules. The whole run of
    text around the cut is taken out of the table."""
    for g in grids:
        l, b, r_, t = g["box"]
        g["not_table"] = set()
        lines = {}
        for c in chars:
            # body-size text only: small chart labels inside a boxed figure stay with the figure
            if c["c"].strip() and c["size"] >= 8 and l - 1 <= c["x"] <= r_ + 1 and b - 4 <= c["y"] <= t + 1:
                lines.setdefault(round(c["base"]), []).append(c)
        for line in lines.values():
            line.sort(key=lambda c: c["x"])
            row = cell_of(line[0], g)[0]
            rules = row_bounds(g, row)
            segs, cur = [], [line[0]]
            for a, z in zip(line, line[1:]):
                if z["l"] - a["r"] < 6:
                    cur.append(z)
                else:
                    segs.append(cur)
                    cur = [z]
            segs.append(cur)
            for seg in segs:
                cut = any(a["x"] < x < z["x"] and z["l"] - a["r"] < 3 for a, z in zip(seg, seg[1:]) for x in rules) \
                    or any(c["l"] + 0.3 < x < c["r"] - 0.3 for c in seg for x in rules)
                if cut:
                    g["not_table"].update(id(c) for c in seg)


def row_bounds(g, row):
    """Internal column rules actually drawn across this row."""
    hi, lo = g["rows"][row], g["rows"][row + 1]
    mid = (hi + lo) / 2
    return [x for x in g["cols"][1:-1]
            if any(abs(vx - x) < 2.5 and vb - 1 <= mid <= vt + 1 for vx, vb, vt in g["verts"])]


def cell_of(ch, g):
    row = max(0, min(len(g["rows"]) - 2, sum(1 for y in g["rows"][1:-1] if ch["y"] < y - 2.5)))
    col = sum(1 for x in row_bounds(g, row) if ch["x"] > x)
    return row, col


def row_spans(g, row):
    """How many base columns each drawn cell in this row covers."""
    present = row_bounds(g, row)
    edges = [g["cols"][0]] + present + [g["cols"][-1]]
    spans = []
    for a, b in zip(edges, edges[1:]):
        spans.append(max(1, sum(1 for x in g["cols"][1:-1] if a + 1 < x < b - 1) + 1))
    return spans


INDIAN_NUM = re.compile(r"\b\d{1,3}(?:, \d{2})+, ?\d{2},\d{3}\b|\b\d{1,3}(?:, \d{2})+,\d{3}\b")
NUM_SPACE = re.compile(r"(\d) ?, ?(?=\d{3}\b)(\d{3})")
NUM_SPACE_STRICT = re.compile(r"(\d) ,\s?(\d{3})\b|(\d)\s,(\d{3})\b")
ORD_FIX = re.compile(r"(\d)\s+(st|nd|rd|th)\b")
ORD_LEAD = re.compile(r"^(st|nd|rd|th)\s+(\d{1,3})\b")


# ------------------------------------------------------------------ runs (text with bold flags)
class Runs:
    def __init__(self):
        self.runs = []

    def add(self, text, bold):
        if not text:
            return
        if self.runs and self.runs[-1][1] == bold:
            self.runs[-1][0] += text
        else:
            self.runs.append([text, bold])

    def finish(self):
        """Normalise spaces, drop soft hyphens, keep bold boundaries."""
        out = []
        for text, bold in self.runs:
            text = re.sub(r"\x02[\r\n\t ]*", "\x02", text).replace("\x01", "")
            text = re.sub(r"[\r\n\t ]+", " ", text)
            text = re.sub(r" {2,}", " ", text)
            text = ORD_FIX.sub(r"\1\2", text)
            text = NUM_SPACE.sub(r"\1,\2", text)
            text = INDIAN_NUM.sub(lambda m: m.group(0) if re.search(r"(Articles?|Sections?|Rules?)\s*$", m.string[:m.start()])
                                  else m.group(0).replace(" ", ""), text)
            if out and out[-1][1] == bold:
                out[-1][0] += text
            else:
                out.append([text, bold])
        # move outer spaces of bold runs into the neighbouring plain text
        fixed = []
        for text, bold in out:
            if bold:
                lead = text[: len(text) - len(text.lstrip())]
                trail = text[len(text.rstrip()):]
                core = text.strip()
                if lead:
                    fixed.append([lead, False])
                if core:
                    fixed.append([core, True])
                if trail:
                    fixed.append([trail, False])
            else:
                fixed.append([text, False])
        merged = []
        for text, bold in fixed:
            if merged and merged[-1][1] == bold:
                merged[-1][0] += text
            else:
                merged.append([text, bold])
        if merged:
            merged[0][0] = merged[0][0].lstrip()
            merged[-1][0] = merged[-1][0].rstrip()
        merged = [[re.sub(r" {2,}", " ", t), b] for t, b in merged if t]
        return tidy_runs(merged)

    @staticmethod
    def text(runs):
        return "".join(t for t, _ in runs).strip()


# spaces the PDF's justified text puts before punctuation: "January 14 , 1949", "(U.S. A .)",
# "India ’ s", "( Haryana)". Every group in a pattern is deleted.
TIDY = [re.compile(p) for p in (r"\S( +)[,;)]", r"\S( +):(?=\s|$)", r"\S( +)\.(?=\s|$|\))",
                                r"\w( ?)[’']( )s\b", r"\(( +)", r"[\w.!?]( +)”")]


def tidy_runs(runs):
    s = "".join(t for t, _ in runs)
    flags = [b for t, b in runs for _ in t]
    keep = [True] * len(s)
    for pat in TIDY:
        for m in pat.finditer(s):
            for gi in range(1, (pat.groups or 0) + 1):
                for k in range(m.start(gi), m.end(gi)):
                    keep[k] = False
    out = []
    for ch, b, k in zip(s, flags, keep):
        if not k:
            continue
        if out and out[-1][1] == b:
            out[-1][0] += ch
        else:
            out.append([ch, b])
    return out


# ------------------------------------------------------------------ stream to blocks
def classify(ch):
    f, s = ch["font"], ch["size"]
    if "Sorts" in f:
        return "bullet"
    if f.startswith("Wingdings"):
        return "subbullet" if s < 10 else "icon"
    if f.startswith("BookmanOldStyle"):
        return "title"
    if f.startswith("TimesNewRomanPS-Bold") and s >= 15:
        return "section"
    if f.startswith("Garamond-Bold-SC"):
        return "header" if ch["y"] < 60 or ch["y"] > 780 else "title"
    if f.startswith("Garamond") and s == 10.0 and ch["y"] < 50:
        return "header"
    if f.startswith("Garamond-Bold") and s >= 11:
        return "heading"
    return "text"


# Tables whose printed text drifts a whole line against their own borders (checked against the page
# images: Nobel 2026, BRICS guests, international rankings, TOP500 systems, Ig Nobel, conferences
# and summits, exercises).
# A grid would pair the wrong items, so they are shown line by line as printed.
DRIFTED_TABLE_PAGES = {61, 75, 86, 127, 201, 210, 211, 213}


def straddles(t):
    """True when a printed line of text sits across one of the table's own row rules,
    i.e. the PDF's text and borders disagree."""
    g = t["grid"]
    inner = g["rows"][1:-1]
    lines = {}
    for ch in t.get("chars", []):
        if not ch["c"].strip():
            continue
        k = (round(ch["bot"]), sum(1 for x in g["cols"][1:-1] if ch["x"] > x))
        lo, hi = lines.get(k, (1e9, -1e9))
        lines[k] = (min(lo, ch["bot"]), max(hi, ch["top"]))
    return any(lo + 1.5 < y < hi - 1.5 for lo, hi in lines.values() for y in inner)


def cells_by_position(t):
    """Rebuild a table's cells from where its text is printed instead of the PDF's stream order,
    which is scrambled in tables whose text crosses their rules. Whole printed lines are placed in
    a row by the line's middle, so a descender ("g" in "Singles") cannot slip into the next row."""
    g = t["grid"]
    chars = [c for c in t.get("chars", []) if c["c"].strip()]
    spaces = [c for c in t.get("chars", []) if c["c"] == " " and c["r"] - c["l"] > 0.5]
    if not chars:
        return {}
    body = sorted(c["size"] for c in chars)[len(chars) // 2]
    lines = []
    for c in sorted((c for c in chars if c["size"] >= body * 0.8), key=lambda c: -c["base"]):
        if lines and abs(lines[-1][0] - c["base"]) <= 1.5:
            lines[-1][1].append(c)
        else:
            lines.append([c["base"], [c]])
    for c in (c for c in chars if c["size"] < body * 0.8):        # superscripts join the nearest line
        best = min(lines, key=lambda ln: abs(ln[0] - c["base"])) if lines else None
        if best is not None and abs(best[0] - c["base"]) < 7:
            best[1].append(c)
    per = {}
    for base, members in lines:
        mid = sorted(c["y"] for c in members)[len(members) // 2]
        for c in members:
            key = cell_of({"x": c["x"], "y": mid}, g)
            per.setdefault(key, {}).setdefault(base, []).append(c)
    out = {}
    for key, by_line in per.items():
        r = Runs()
        for i, base in enumerate(sorted(by_line, reverse=True)):
            if i and r.runs and not r.runs[-1][0].endswith(("-", "–", "/", "\x02")):
                r.add(" ", False)
            prev = None
            gaps = [sp for sp in spaces if abs(sp["base"] - base) <= 1.5]
            for c in sorted(by_line[base], key=lambda c: c["l"]):
                if prev is not None and (c["l"] - prev["r"] > min(prev["size"], c["size"]) * 0.2
                                         or any(prev["r"] - 0.5 <= sp["x"] <= c["l"] + 0.5 for sp in gaps)):
                    r.add(" ", c["bold"])
                r.add(c["c"], c["bold"])
                prev = c
        out[key] = r
    return out


def line_rows(t):
    """Rebuild a misaligned table one printed line at a time (columns kept, rows = lines).
    Lines are grouped by baseline; small raised characters (superscripts) join the nearest line."""
    g = t["grid"]
    chars = [c for c in t.get("chars", []) if c["c"].strip()]
    if not chars:
        return []
    body = sorted(c["size"] for c in chars)[len(chars) // 2]
    lines = []
    for c in sorted((c for c in chars if c["size"] >= body * 0.8), key=lambda c: -c["base"]):
        if lines and abs(lines[-1][0] - c["base"]) <= 1.5:
            lines[-1][1].append(c)
        else:
            lines.append([c["base"], [c]])
    for c in (c for c in chars if c["size"] < body * 0.8):
        best = min(lines, key=lambda ln: abs(ln[0] - c["base"])) if lines else None
        if best is not None and abs(best[0] - c["base"]) < 7:
            best[1].append(c)
    spaces = {}
    for sp in (c for c in t.get("chars", []) if c["c"] == " " and c["r"] - c["l"] > 0.5):   # skip zero-width spaces
        best = min(lines, key=lambda ln: abs(ln[0] - sp["base"])) if lines else None
        if best is not None and abs(best[0] - sp["base"]) <= 1.5:
            spaces.setdefault(id(best[1]), []).append(sp)
    ncols = len(g["cols"]) - 1
    rows = []
    for base, members in lines:
        # split this line only where a column rule is actually drawn at its height
        drawn = [x for x in g["cols"][1:-1]
                 if any(abs(vx - x) < 2.5 and vb - 2 <= base <= vt + 2 for vx, vb, vt in g["verts"])]
        edges = [g["cols"][0]] + drawn + [g["cols"][-1]]
        row = []
        for a, b in zip(edges, edges[1:]):
            r = Runs()
            prev = None
            mine = sorted((c for c in members if a <= c["x"] < b or (b == edges[-1] and c["x"] >= b)), key=lambda c: c["l"])
            for c in mine:
                gap = prev is not None and (c["l"] - prev["r"] > min(prev["size"], c["size"]) * 0.2
                                            or any(prev["r"] - 0.5 <= sp["x"] <= c["l"] + 0.5 for sp in spaces.get(id(members), ())))
                if gap:
                    r.add(" ", c["bold"])
                r.add(c["c"], c["bold"])
                prev = c
            span = max(1, sum(1 for x in g["cols"][1:-1] if a + 1 < x < b - 1) + 1)
            row.append([r.finish(), span])
        if any(Runs.text(x) for x, _ in row):
            rows.append(row)
    return rows


def grid_rows(t):
    """Rows of a bordered table as [[runs, colspan(, rowspan)], ...].

    The PDF draws every cell's border separately, so a cell with no rule under it continues
    into the next row (e.g. "Men's Singles" beside both the Winner and the Runner-up rows):
    such cells are merged and get a rowspan."""
    cells, g = t["cells"], t["grid"]
    nrows = max(r for r, _ in cells) + 1 if cells else 0
    grid = []
    for r in range(nrows):
        spans = row_spans(g, r)
        edges = [g["cols"][0]] + row_bounds(g, r) + [g["cols"][-1]]
        n = max(len(spans), max([c for rr, c in cells if rr == r] + [0]) + 1)
        grid.append([{"runs": cells[(r, c)].finish() if (r, c) in cells else [],
                      "span": spans[c] if c < len(spans) else 1, "rowspan": 1, "into": None,
                      "x": (edges[c], edges[c + 1]) if c + 1 < len(edges) else None} for c in range(n)])
    keep = [any(Runs.text(c["runs"]) for c in row) for row in grid]

    def ruled(y, x):
        return any(abs(hy - y) < 2.5 and hl - 2 <= x <= hr + 2 for hy, hl, hr in g.get("hsegs", []))

    for r in range(1, nrows):
        if not (keep[r] and keep[r - 1]):
            continue
        for cell in grid[r]:
            if cell["x"] is None:
                continue
            above = next((a for a in grid[r - 1] if a["x"] and abs(a["x"][0] - cell["x"][0]) < 2
                          and abs(a["x"][1] - cell["x"][1]) < 2), None)
            if above is None or ruled(g["rows"][r], (cell["x"][0] + cell["x"][1]) / 2):
                continue
            target = above["into"] or above
            if Runs.text(cell["runs"]):
                if Runs.text(target["runs"]):
                    target["runs"] = target["runs"] + [[" ", False]] + cell["runs"]
                else:
                    target["runs"] = cell["runs"]
            target["rowspan"] += 1
            cell["into"] = target
    out = []
    for r, row in enumerate(grid):
        if keep[r]:
            out.append([[c["runs"], c["span"]] + ([c["rowspan"]] if c["rowspan"] > 1 else [])
                        for c in row if c["into"] is None])
    return out


def caption_line_starts(chars, grids):
    """First characters of centred bold one-line captions ("Finnie" under the mascot picture on
    p237, "Total Oilseeds – 429.89 lakh tonnes" on p99). Without this they are glued onto the end
    of the bullet above them. They become their own paragraph (not a heading, so they never split
    a study unit)."""
    lines = {}
    for c in chars:
        if (c["c"].strip() and c["size"] >= 7.6 and classify(c) == "text"
                and not any(in_grid(c, g) for g in grids)):
            lines.setdefault((round(c["base"]), 0 if c["x"] < 270 else 1), []).append(c)
    found = []
    for (base, col), cs in lines.items():
        cs.sort(key=lambda c: c["l"])
        lo, hi = cs[0]["l"], cs[-1]["r"]
        cl, cr = (36, 260) if col == 0 else (280, 504)
        if cs[0]["bold"] and lo > cl + 25 and abs((lo + hi) / 2 - (cl + cr) / 2) < 12 and hi - lo < 0.8 * (cr - cl):
            found.append((base, col, cs[0]))
    # a caption printed on two lines is one paragraph
    return {id(c) for base, col, c in found
            if not any(col2 == col and 0 < base2 - base < 16 for base2, col2, _ in found)}


def list_lines(b):
    """Split a paragraph into its printed lines when it is really a list: at least three lines and
    most of them "Name - Place" pairs (Upcoming Sports Events on p239). Returns None otherwise."""
    lines, cur = [], []
    for t, bold in b["runs"].runs:
        parts = re.split(r"\r\n|\n", t)
        for i, part in enumerate(parts):
            if i:
                lines.append(cur)
                cur = []
            if part:
                cur.append([part, bold])
    lines.append(cur)
    lines = [ln for ln in lines if "".join(t for t, _ in ln).strip()]
    if len(lines) < 3:
        return None

    def txt(ln):
        return "".join(t for t, _ in ln).strip()

    # an item that wraps onto a second printed line: "UCI Road World Championship 2032 / - Pune"
    numbered = sum(1 for ln in lines if re.match(r"\d+\.", txt(ln))) >= 0.6 * len(lines)
    joined = []
    for ln in lines:
        t, prev = txt(ln), txt(joined[-1]) if joined else ""
        is_pair = re.search(r"\S\s[–-]\s\S", t)
        wraps = joined and (t[:1] in "-–(" or t[:1].islower() or prev[-1:] in ",&("
                            or (prev.count("(") > prev.count(")") and not is_pair)
                            or (numbered and not re.match(r"\d+\.", t)))
        if wraps:
            joined[-1] = joined[-1] + [[" ", False]] + ln
        else:
            joined.append(ln)
    lines = joined
    if len(lines) < 3:
        return None
    pairs = sum(1 for ln in lines if re.search(r"\S\s[\u2013-]\s\S", "".join(t for t, _ in ln)))
    ends = sum(1 for ln in lines if "".join(t for t, _ in ln).rstrip()[-1:] in ".;,")
    return lines if pairs >= 0.7 * len(lines) and ends <= len(lines) // 3 else None


def is_separator(b, blocks):
    """Does this block split the page into bands (full-width banner, heading, paragraph or table)?

    A text line that crosses the column gap is full-width only when nothing else is printed beside
    it. Some lines in the source overflow their column and print over the right column's text
    ("...1.56 lakh installations, retaining its leading position." on p161; the heading
    "Chemistry: Understanding Molecular Handedness" on p62); those are ordinary left-column lines."""
    if b["kind"] == "table":
        return bool(b.get("wide"))
    head = b["kind"] in ("section", "title", "heading")
    for k, (lo, hi) in b.get("lines", {}).items():
        if not ((lo < 268 and hi > 285) if head else (lo < 200 and hi > 330)):
            continue
        beside = False
        for o in blocks:
            if o is b:
                continue
            if o["kind"] == "table":
                beside = any(abs(c["y"] / 3 - k) <= 2 and 285 < c["x"] < hi for c in o.get("chars", []) if c["c"].strip())
            else:
                beside = any(abs(k2 - k) <= 2 and lo2 < hi and hi2 > 285 for k2, (lo2, hi2) in o.get("lines", {}).items())
            if beside:
                break
        if not beside:
            return True
    return False


def page_blocks(doc, index):
    chars = page_chars(doc, index)
    grids = table_grids(doc, index)
    mark_overprinted_text(chars, grids)
    captions = caption_line_starts(chars, grids)
    blocks = []
    cur = None
    tables = {}
    last_target = None
    icon_at = None

    def grow(b, ch):
        """Remember how far a block reaches, for band-aware reading order."""
        if ch["c"].strip():
            b["x0"] = min(b.get("x0", 1e9), ch["x"])
            b["x1"] = max(b.get("x1", -1e9), ch["x"])
            b["ytop"] = max(b.get("ytop", -1e9), ch["y"])
            line = b.setdefault("lines", {}).setdefault(round(ch["y"] / 3), [1e9, -1e9])
            line[0], line[1] = min(line[0], ch["x"]), max(line[1], ch["x"])
            if line[0] < 200 and line[1] > 330:
                b["wide"] = True     # one line of this block crosses the column gap

    def start(kind, **kw):
        nonlocal cur, last_target
        cur = dict(kind=kind, runs=Runs(), page=index + 1, pos=None, last=None, **kw)
        blocks.append(cur)
        last_target = cur["runs"]

    for ch in chars:
        kind = classify(ch)
        if kind == "header":
            continue
        # line breaks and superscripts ("46th", "72nd") belong to whatever block is open
        if not ch["c"].strip() or (ch["size"] < 7.6 and kind == "text"):
            # a superscript inside a table belongs to its printed line; a space glyph marks a word gap
            if ch["c"].strip() or ch["c"] == " ":
                tg = next((g for g in grids if in_grid(ch, g)), None)
                if tg is not None and id(tg) in tables:
                    tables[id(tg)].setdefault("chars", []).append(ch)
            if last_target is not None and cur is not None and last_target is not cur["runs"]:
                last_target.add(ch["c"], ch["bold"])
            elif cur is not None and cur["kind"] != "table":
                cur["runs"].add(ch["c"], cur["kind"] in ("title", "section", "heading") or ch["bold"])
            elif last_target is not None:
                last_target.add(ch["c"], ch["bold"])
            continue
        # a symbol or superscript on the same line as an open title/heading (e.g. "₹10", "46th") stays in it
        if (cur is not None and cur["kind"] in ("title", "section", "heading") and kind == "text" and cur["last"]
                and abs(ch["y"] - cur["last"][1]) < 7 and 0 <= ch["x"] - cur["last"][0] < 25):
            cur["runs"].add(ch["c"], True)
            cur["last"] = (ch["x"], ch["y"])
            grow(cur, ch)
            continue
        # bold body-size text right after a heading box glyph is a (minor) heading: "Lionel Messi" on
        # p239, "CVC Annual Report 2025" on p25 are printed at 10.5pt instead of the usual 11.5pt
        if kind == "text" and ch["bold"] and icon_at and abs(ch["y"] - icon_at[1]) < 5 and 0 < ch["x"] - icon_at[0] < 30:
            start("heading", size=ch["size"], minor=True)
            cur["runs"].add(ch["c"], True)
            cur["pos"] = cur["last"] = (ch["x"], ch["y"])
            grow(cur, ch)
            icon_at = None
            continue
        # ... and may wrap onto a second line
        if (kind == "text" and ch["bold"] and cur is not None and cur.get("minor") and cur["last"]
                and 5 < cur["last"][1] - ch["y"] < 16 and abs(ch["x"] - cur["pos"][0]) < 8):
            cur["runs"].add(ch["c"], True)
            cur["last"] = (ch["x"], ch["y"])
            grow(cur, ch)
            continue
        after_icon = icon_at is not None and abs(ch["y"] - icon_at[1]) < 5 and 0 < ch["x"] - icon_at[0] < 30
        if kind != "icon":
            icon_at = None
        g = next((g for g in grids if in_grid(ch, g)), None)
        # a line that runs on past its column into a table stays with its own paragraph
        # ("... and finis|hed 27th" overflows into the IAU table on p232)
        if (g is not None and cur is not None and cur["kind"] in ("p", "li") and cur.get("lastc")
                and abs(ch["base"] - cur["lastc"][2]) < 1.5 and 0 <= ch["x"] - cur["lastc"][0] < 12
                and (not g["box"][0] - 1 <= cur["lastc"][0] <= g["box"][2] + 1 or cur.get("ovf") == id(g))
                and not in_grid({"x": cur["pos"][0], "y": cur["pos"][1]}, g)):
            cur["ovf"] = id(g)
            g = None
        if g is not None and kind == "text" and ch["size"] <= 10.5:
            key = id(g)
            if key not in tables:
                tables[key] = {"kind": "table", "page": index + 1, "cells": {}, "grid": g,
                               "pos": (g["box"][0], -1e9)}
                blocks.append(tables[key])
                cur = None
            cell = tables[key]["cells"].setdefault(cell_of(ch, g), Runs())
            # a new line inside a cell needs a space when the PDF did not supply one
            prev = getattr(cell, "last_ch", None)
            if prev and cell.runs and not cell.runs[-1][0][-1:].isspace():
                if abs(ch["y"] - prev["y"]) > 3:
                    if not cell.runs[-1][0].endswith(("-", "–", "/", "\x02")):
                        cell.add(" ", ch["bold"])
                elif ch["l"] - prev["r"] > min(prev["size"], ch["size"]) * 0.25 and prev["c"] != "₹" \
                        and ch["c"] not in ",.;:)%" and prev["c"] not in "(":
                    cell.add(" ", ch["bold"])
            cell.last_ch = ch
            if ch["c"].strip():  # a table sits where its topmost text is, not where its border starts
                tables[key]["pos"] = (g["box"][0], max(tables[key]["pos"][1], ch["y"]))
            cell.add(ch["c"], ch["bold"])
            tables[key].setdefault("chars", []).append(ch)
            last_target = cell
            continue
        if kind == "bullet":
            start("li", level=1)
            cur["pos"] = (ch["x"], ch["y"])
            grow(cur, ch)
            continue
        if kind == "subbullet":
            start("li", level=2)
            cur["pos"] = (ch["x"], ch["y"])
            grow(cur, ch)
            continue
        if kind == "icon":
            if ch["c"] == "":      # the arrow sub-bullet, sometimes printed at body size (p126, p197)
                start("li", level=2)
                cur["pos"] = (ch["x"], ch["y"])
                grow(cur, ch)
            else:
                icon_at = (ch["x"], ch["y"])
            continue
        if kind in ("title", "section", "heading"):
            smallcaps = ch["font"].startswith("Garamond-Bold-SC")
            same_line = (cur is not None and cur["kind"] == kind and cur["last"]
                         and abs(ch["y"] - cur["last"][1]) < 9 and ch["x"] > cur["last"][0] - 2)
            new_heading = after_icon and cur is not None and cur["last"] and abs(ch["y"] - cur["last"][1]) > 5
            if cur is None or cur["kind"] != kind or new_heading or (cur.get("size") != ch["size"] and not same_line):
                start(kind, size=ch["size"])
            cur["runs"].add(ch["c"], True)
            last_target = cur["runs"]
            if smallcaps:
                cur["smallcaps"] = True
            if cur["pos"] is None:
                cur["pos"] = (ch["x"], ch["y"])
            cur["last"] = (ch["x"], ch["y"])
            grow(cur, ch)
            continue
        # body text
        small = ch["size"] < 7.6 and ch["c"].strip()
        if id(ch) in captions:
            start("p", level=0, box=False, caption=True)
        if cur is None or cur["kind"] in ("title", "section", "heading"):
            start("p", level=0, box=ch["size"] <= 9.5)
        cur["runs"].add(ch["c"], ch["bold"])
        last_target = cur["runs"]
        if cur["pos"] is None:
            cur["pos"] = (ch["x"], ch["y"])
        cur["lastc"] = (ch["x"], ch["y"], ch["base"])
        grow(cur, ch)
        if small:
            cur["sup"] = True
    # Reading order. Blocks that cross the column gap (section headings, wide tables) split the
    # page into horizontal bands; inside a band read the left column top to bottom, then the
    # right column. (The PDF's own stream order sometimes puts a title after the text below it.)
    for b in blocks:
        if b["kind"] == "table":
            b["x0"], b["x1"], b["ytop"] = b["grid"]["box"][0], b["grid"]["box"][2], b["pos"][1]
            b["wide"] = b["x0"] < 200 and b["x1"] > 330
        elif "x0" not in b:
            b["x0"], b["x1"], b["ytop"] = 0, 0, -1e9
    # A block is placed where it STARTS (a paragraph may run on into the next column).
    for b in blocks:
        if b["kind"] != "table":
            b["sx"], b["sy"] = b.get("pos") or (b["x0"], b["ytop"])
        else:
            b["sx"], b["sy"] = b["x0"], b["ytop"]
    seps = sorted([b for b in blocks if is_separator(b, blocks)], key=lambda b: -b["sy"])
    sep_rank = {id(b): j for j, b in enumerate(seps, 1)}
    # a heading printed just above a full-width table is that table's caption ("Population and
    # Household Profile" on p96): read it with the table, not with the column beside it
    caption_of = {}
    for t in seps:
        if t["kind"] != "table":
            continue
        for h in blocks:
            if (h["kind"] in ("heading", "title") and id(h) not in sep_rank and 0 < h["sy"] - t["sy"] < 30
                    and t["x0"] - 5 <= h["x0"] <= t["x1"]):
                caption_of[id(h)] = sep_rank[id(t)]

    def key(b):
        if id(b) in caption_of:
            return (2 * caption_of[id(b)] - 1, -1, -b["sy"])
        if id(b) in sep_rank:
            return (2 * sep_rank[id(b)] - 1, 0, -b["sy"])
        band = sum(1 for sp in seps if sp["sy"] > b["sy"])
        return (2 * band, 0 if b["sx"] < 270 else 1, -b["sy"])
    blocks = sorted(blocks, key=key)
    out = []
    for b in blocks:
        crossed = b["kind"] == "table" and straddles(b)
        if crossed and b["page"] in DRIFTED_TABLE_PAGES:
            rows = line_rows(b)
            if rows:
                out.append({"kind": "table", "page": b["page"], "cols": len(b["grid"]["cols"]) - 1, "rows": rows,
                            "as_printed": True})
            continue
        if b["kind"] == "table":
            sizes = sorted(c["size"] for c in b.get("chars", []) if c["c"].strip())
            # text printed across a rule (usually struck through by it): place by position; small
            # print is a boxed figure's labels (the UP budget pie chart), whose stream order reads best
            if crossed and sizes and sizes[len(sizes) // 2] >= 8:
                b["cells"] = cells_by_position(b)
            rows = grid_rows(b)
            if rows:
                out.append({"kind": "table", "page": b["page"], "cols": len(b["grid"]["cols"]) - 1, "rows": rows})
        else:
            items = list_lines(b) if b["kind"] == "p" else None
            if items:       # an "Event – Host" list printed one item per line, without bullets
                for line in items:
                    lr = Runs()
                    for t, bold in line:
                        lr.add(t, bold)
                    if Runs.text(lr.finish()):
                        out.append({"kind": "li", "level": 1, "page": b["page"], "runs": lr.finish()})
                continue
            runs = b["runs"].finish()
            if b["kind"] in ("title", "section", "heading") and runs:
                runs = [[ORD_LEAD.sub(r"\2\1", Runs.text(runs)), True]]
            if Runs.text(runs):
                out.append({k: v for k, v in b.items() if k not in ("runs", "size", "pos", "last", "lastc", "ovf", "x0", "x1", "ytop", "lines", "wide", "sx", "sy")} | {"runs": runs})
    return out


# ------------------------------------------------------------------ chapter 1: question / answer bank
DATE_RE = re.compile(r"\(\s*([^()]*?\b(?:19|20)\d\d)\s*\)")
MONTH_WORD = r"\b(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\b"


def qa_from_blocks(blocks):
    items, category = [], None
    for b in blocks:
        if b["kind"] in ("heading", "section", "title"):
            category = Runs.text(b["runs"]).title()
            continue
        if b["kind"] == "table":
            raise SystemExit(f"Unexpected table in Points to Remember on page {b['page']}")
        if b["kind"] == "p" and items and not any(bold for _, bold in b["runs"]):
            # a question that wrapped onto the next column without a new bullet
            items[-1]["q_runs"] += [[" ", False]] + b["runs"]
            continue
        if b["kind"] == "p" and items:
            items[-1]["q_runs"] += [[" ", False]] + b["runs"]
            continue
        items.append({"page": b["page"], "category": category, "q_runs": list(b["runs"])})
    qa = []
    for it in items:
        runs = it["q_runs"]
        first = next((i for i, (t, bold) in enumerate(runs) if bold and t.strip()), len(runs))
        q_runs, a_runs = list(runs[:first]), []
        # light text after the answer starts is part of the answer ("Vivek Aggarwal (July 2026 to
        # June 2027)", “Unnat Bihar, Ujjwal Bihar”) unless it is the end of the question, which
        # the PDF sometimes streams after the answer's first line ("... study the Sun?")
        for t, bold in runs[first:]:
            if not bold and t.strip().endswith("?"):
                q_runs.append([" " + t, bold])
                a_runs.append([" ", False])
            else:
                a_runs.append([t, bold])
        q = re.sub(r"\s+", " ", "".join(t for t, _ in q_runs)).strip()
        a = re.sub(r"\s+", " ", "".join(t for t, _ in a_runs)).strip()
        a = re.sub(r"^[–—-]\s*", "", a).strip()
        a = re.sub(r"\s+([.,;:])", r"\1", a)
        # the story date is the last bracket holding a month or a day range: "(6–9 January 2026)",
        # not "(CES 2026)"
        dates = [m for m in DATE_RE.finditer(q) if re.search(MONTH_WORD, m.group(1), re.I)
                 or re.fullmatch(r"[\d\s,/–-]+", m.group(1))]
        m = dates[-1] if dates else None
        date = m.group(1).strip() if m else None
        if m:
            q = (q[: m.start()] + q[m.end():]).strip()
        q = re.sub(r"\s+([?.,;:])", r"\1", q)
        qa.append({"page": it["page"], "category": it["category"], "q": q, "a": a, "date": date})
    return qa


# ------------------------------------------------------------------ chapters 2-10: articles
def articles_from_blocks(blocks, chapter):
    arts, section = [], None
    cur = None
    for b in blocks:
        if b["kind"] == "section":
            section = Runs.text(b["runs"])
            continue
        if b["kind"] == "title":
            if cur and not cur["blocks"] and cur["page_last"] == b["page"] and cur["title_open"]:
                cur["title"] += " " + Runs.text(b["runs"])
                continue
            title = Runs.text(b["runs"])
            if b.get("smallcaps"):      # small-caps banners read "NewS IN SHoRTS", "IRan–ISRael ConflICT"
                title = smallcaps_title(title)
            cur = {"ch": chapter, "section": section, "title": title, "pages": [b["page"]],
                   "blocks": [], "page_last": b["page"], "title_open": True}
            arts.append(cur)
            continue
        if cur is None:
            cur = {"ch": chapter, "section": section, "title": "Introduction", "pages": [b["page"]],
                   "blocks": [], "page_last": b["page"], "title_open": False}
            arts.append(cur)
        cur["title_open"] = False
        if b["page"] not in cur["pages"]:
            cur["pages"].append(b["page"])
        cur["page_last"] = b["page"]
        blk = {k: v for k, v in b.items() if k not in ("page",)}
        blk["page"] = b["page"]
        cur["blocks"].append(blk)
    for a in arts:
        a.pop("page_last", None)
        a.pop("title_open", None)
        a["title"] = ORD_LEAD.sub(r"\2\1", re.sub(r"\s+", " ", a["title"]).strip())
    return [a for a in arts if a["blocks"] or a["title"] != "Introduction"]


def resolve_line_hyphens(data):
    """pdfium reports every hyphen that ends a line as a soft hyphen (\x02). In this magazine most
    are real compounds ("high-speed", "women-owned", "Indo-Tibetan"); a few split one word
    ("recommenda-tions", "Ben-gal"). Decide from the book's own vocabulary: keep the hyphen if the
    hyphenated form occurs elsewhere, join if only the joined word occurs, otherwise keep it."""
    strings = []

    def walk(o):
        if isinstance(o, dict):
            for v in o.values():
                walk(v)
        elif isinstance(o, list):
            if len(o) == 2 and isinstance(o[0], str) and isinstance(o[1], bool):
                strings.append(o)
            else:
                for v in o:
                    walk(v)

    walk(data)
    full = " ".join(o[0] for o in strings) + " " + " ".join(
        q[k] for q in data["qa"] for k in ("q", "a") if isinstance(q.get(k), str))
    clean = re.sub(r"\w*\x02\w*", " ", full)
    vocab = set(w.lower() for w in re.findall(r"[A-Za-z]+", clean))
    hyph = set(w.lower() for w in re.findall(r"[A-Za-z]+-[A-Za-z]+", clean))

    def fix(text):
        def one(m):
            a, b = m.group(1), m.group(2)
            if f"{a}-{b}".lower() in hyph:
                return f"{a}-{b}"
            if (a + b).lower() in vocab and b[:1].islower():
                return a + b
            return f"{a}-{b}"
        text = re.sub(r"([A-Za-z]+)\x02([A-Za-z]+)", one, text)
        return text.replace("\x02", "-")

    for o in strings:
        o[0] = fix(o[0])
    for q in data["qa"]:
        for k in ("q", "a"):
            if isinstance(q.get(k), str):
                q[k] = fix(q[k])
    for a in data["articles"]:
        a["title"] = fix(a["title"])


EVENT_NOUNS = (
    "conference|summit|event|meeting|scheme|mission|programme|program|policy|project|report|index|award|"
    "awards|prize|festival|exercise|operation|tournament|championship|cup|games|fair|expo|conclave|initiative|"
    "campaign|platform|portal|agreement|treaty|act|bill|law|company|bank|organisation|organization|body|"
    "institute|university|ministry|committee|commission|plan|survey|study|ceremony|session|forum|dialogue|"
    "ranking|rankings|list|edition|visit|deal|mou|pact|centre|center|facility|plant|corridor|station|airport|"
    "port|bridge|museum|park|ship|vessel|satellite|rocket|aircraft|missile|system|technology|vaccine|species|"
    "site|sanctuary|reserve|team|film|book|novel|album|spacecraft|probe|telescope|state|city|country|nation|"
    "leader|minister|player|winner|laureate|recipient|athlete|declaration|framework|guidelines|rules|code|"
    "theme|mascot|slogan|venue|host|app|tool|model|network|grid|dam|temple|monument|trophy|title|medal|"
    "record|match|final|league|series|budget|census|election|court|verdict|judgment|case|order|ban|tax|"
    "tariff|fund|loan|bond|currency|coin|stamp|campus|lab|laboratory|hospital|unit|force|position|positions|"
    "rank|place|spot|top|agency|firm|group|corporation|startup|bureau|department|ministers|countries|nations")
BACKREF = re.compile(rf"\b(this|these|that|those|it|its|they|their|them|he|his|him|she|her|such|"
                     rf"the (?:\w+ ){{0,2}}(?:{EVENT_NOUNS}))\b", re.I)


def _story_tokens(text):
    toks = {t.lower() for t in re.findall(r"[A-Z][A-Za-z-]{2,}|[A-Z]{2,}|\d{2,}[\w.,]*", text)}
    for run in re.findall(r"(?:\b[A-Z][a-z]+\b[ -]?){2,}", text):     # "Indian Space Congress" -> "isc"
        words = [w for w in re.findall(r"[A-Z][a-z]+", run)]
        if len(words) >= 2:
            toks.add("".join(w[0] for w in words).lower())
    return toks


def story_of(qa):
    """Group the Q&A bank into stories. The magazine prints a date only on the first question of a
    day's block, and several unrelated news items can share that block, so a question also starts
    a new story when it neither points back to the story so far nor shares a distinctive word
    (a name, acronym or number that is rare in the whole bank) with it."""
    df = Counter()
    for q in qa:
        df.update(_story_tokens(q["q"] + " " + q["a"]))
    common = {t for t, n in df.items() if n > len(qa) * 0.02}
    # boundaries a reviewer checked where the rule below guesses wrong (story_overrides.json)
    over = json.loads((HERE / "story_overrides.json").read_text(encoding="utf-8"))
    story, toks = 0, set()
    for q in qa:
        if q["id"] in over["start_new"] or q["id"] in over["continue"]:
            if q["id"] in over["start_new"] or story == 0:
                story += 1
                toks = set()
            toks |= _story_tokens(q["q"] + " " + q["a"]) - common
            q["story"] = f"s{story:03d}"
            continue
        mine = _story_tokens(q["q"]) - common
        # a question with no name, acronym or rare number of its own ("Which team became the
        # champion?") cannot open a new topic: it follows the story before it
        if q["date"] or story == 0 or not (BACKREF.search(q["q"]) or mine & toks or not mine):
            story += 1
            toks = set()
        toks |= _story_tokens(q["q"] + " " + q["a"]) - common
        q["story"] = f"s{story:03d}"


SMALL_WORDS = {"in", "of", "and", "the", "for", "on", "at", "to", "a", "an", "with", "by"}


def smallcaps_title(t):
    """A small-caps banner is printed all in capitals; give it ordinary title case."""
    words = re.split(r"(\s+|[–-])", t.lower())
    out = [w if i and w in SMALL_WORDS else w[:1].upper() + w[1:] for i, w in enumerate(words)]
    return "".join(out)


def join_broken_sentences(blocks):
    """"... tailored to Ladakh's" (end of p25) + "circumstances." (top of p26) is one sentence."""
    out = []
    for b in blocks:
        prev = out[-1] if out else None
        if (prev is not None and b["kind"] == "p" and prev["kind"] in ("p", "li") and not b.get("caption")
                and b["runs"] and prev["runs"]):
            tail = Runs.text(prev["runs"])
            head = Runs.text(b["runs"])
            if tail and head and tail[-1] not in ".!?:;”\"’)" and (head[0].islower() or b["page"] != prev["page"]):
                prev["runs"] = prev["runs"] + [[" ", False]] + b["runs"]
                continue
        out.append(b)
    return out


def main():
    doc = pdfium.PdfDocument(str(PDF))
    if len(doc) != 241:
        raise SystemExit(f"Expected 241 pages, found {len(doc)}")
    by_ch = {n: [] for n, *_ in CHAPTERS}
    starts = {a: n for n, _, _, a, _ in CHAPTERS}
    for index in range(len(doc)):
        ch = chapter_of(index + 1)
        if ch is None:
            continue
        blocks = page_blocks(doc, index)
        # text at the top of a chapter's first page, before any title or heading, is the end of
        # the previous chapter's last article (chapters 3 onwards; chapter 2 follows the Q&A bank)
        if starts.get(index + 1) == ch and ch >= 3:
            k = 0
            while k < len(blocks) and blocks[k]["kind"] in ("p", "li", "table"):
                k += 1
            by_ch[ch - 1] += blocks[:k]
            blocks = blocks[k:]
        by_ch[ch] += blocks
    qa = qa_from_blocks(by_ch[1])
    articles = []
    for n, *_ in CHAPTERS[1:]:
        articles += articles_from_blocks(by_ch[n], n)
    for i, q in enumerate(qa, 1):
        q["id"] = f"q{i:03d}"
    story_of(qa)
    story = len({q["story"] for q in qa})
    for i, a in enumerate(articles, 1):
        a["id"] = f"a{i:03d}"
        a["blocks"] = join_broken_sentences(a["blocks"])
    data = {
        "pdf": PDF.name, "pdf_pages": len(doc),
        "chapters": [{"num": n, "title": t, "hindi": h, "start": a, "end": b} for n, t, h, a, b in CHAPTERS],
        "qa": qa, "articles": articles,
    }
    resolve_line_hyphens(data)
    OUT.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
    # report
    missing_a = [q["id"] for q in qa if not q["a"]]
    missing_q = [q["id"] for q in qa if len(q["q"]) < 8]
    print(f"Q&A: {len(qa)} items in {story} stories; missing answer: {missing_a[:20]}; short question: {missing_q[:20]}")
    per = Counter(a["ch"] for a in articles)
    chars = Counter()
    bold = Counter()
    tables = Counter()
    for a in articles:
        for b in a["blocks"]:
            if b["kind"] == "table":
                tables[a["ch"]] += 1
                cells = [c for row in b["rows"] for c, *_ in row]
                chars[a["ch"]] += sum(len(Runs.text(c)) for c in cells)
                bold[a["ch"]] += sum(1 for c in cells for _, bb in c if bb)
            else:
                chars[a["ch"]] += len(Runs.text(b["runs"]))
                bold[a["ch"]] += sum(1 for _, bb in b["runs"] if bb)
    for n, t, *_ in CHAPTERS[1:]:
        print(f"ch{n} {t}: {per[n]} articles, {tables[n]} tables, {bold[n]} bold phrases, {chars[n]:,} chars")
    print(f"Wrote {OUT}")


if __name__ == "__main__":
    main()
