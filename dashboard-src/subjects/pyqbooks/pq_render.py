"""Step 4: build a book's three study pages from source.json, clusters.json and memory/.

    python pq_render.py polity|history|economy [--draft]

  * full notes  - every past-paper question of the book with its options, answer (highlighted),
                  exam tags, the book's explanation and a one-line "Remember" card; each chapter
                  opens with the book's key facts; practice with spaced repetition; facts asked in
                  2+ papers; latest UP papers; Hindi terms
  * quick notes - one recall line per fact cluster (grey boxes in Test mode), Must-know first marks
  * 72h plan    - 54 learn hours, 12 revise hours, 6 timed mocks; spaced review at 1/3/7/15/30 hours
--draft renders even when some memory cards are missing (the question itself is shown).
"""
import html
import json
import random
import re
import sys
import hashlib
from collections import Counter, OrderedDict, defaultdict

from pq_books import BOOKS, HERE, book_dir

E = html.escape
EXAM = "6 December 2026"
LEARN_HOURS, REVISE_HOURS, TEST_HOURS = 54, 12, 6
REVIEW_GAPS = (1, 3, 7, 15, 30)


def seed(*parts):
    return int(hashlib.md5("|".join(parts).encode()).hexdigest()[:8], 16)


def text(runs):
    return "".join(t for t, _ in runs).strip()


def short(t, n):
    if len(t) <= n:
        return t
    return t[:n].rsplit(" ", 1)[0].rstrip(",;:–-") + "…"


# ------------------------------------------------------------------ html helpers
def runs_html(runs, mask=True):
    """Bold text: key facts (grey boxes in Test mode) in theory and explanations; plain bold in
    questions and options, which must stay readable in Test mode."""
    tag = '<b class="k">' if mask else "<b>"
    return "".join(f'{tag}{E(t)}</b>' if b and t.strip() else E(t) for t, b in runs)


def table_html(b, mask=True):
    rows = "".join("<tr>" + "".join(f"<td>{runs_html(c, mask)}</td>" for c in row) + "</tr>" for row in b["rows"])
    return f'<div class="table-scroll"><table>{rows}</table></div>'


def blocks_html(blocks, cls="pt", mask=True):
    out, in_ul = [], False
    for b in blocks:
        if b["kind"] == "li":
            if not in_ul:
                out.append("<ul>")
                in_ul = True
            out.append(f'<li class="{cls}">{runs_html(b["runs"], mask)}</li>')
            continue
        if in_ul:
            out.append("</ul>")
            in_ul = False
        if b["kind"] == "table":
            out.append(table_html(b, mask))
        elif b["kind"] == "h":
            out.append(f'<h4 class="{cls}">{runs_html(b["runs"], mask)}</h4>')
        else:
            out.append(f'<p class="{cls}">{runs_html(b["runs"], mask)}</p>')
    if in_ul:
        out.append("</ul>")
    return "".join(out)


def blocks_plain(blocks):
    out = []
    for b in blocks:
        if b["kind"] == "table":
            out += [" | ".join(text(c) for c in row) for row in b["rows"]]
        else:
            out.append(text(b["runs"]))
    return [x for x in out if x]


# one masked answer per number, with its clause brackets and range kept whole:
# "66(3)(c)", "11 am-12 noon", "1947-48", "42nd"
_NUM = r"₹?\d[\d,.]*(?:\([0-9a-z]{1,4}\))*(?:\s?%|\s?(?:per cent|crore|lakh|million|billion|km|kg|th|st|nd|rd|am|pm|noon)\b)?"
NUM_MASK = re.compile(_NUM + r"(?:\s?[-–]\s?" + _NUM + r")?")


def recall_html(t):
    """A Remember line with its answer part in grey test-mode boxes: what follows the first
    "→", "=" or ": " in each "; "-separated part, or else its numbers and years."""
    out = []
    for seg in re.split(r"(;\s+)", t):
        if re.fullmatch(r";\s+", seg):
            out.append(E(seg))
            continue
        m = re.search(r"\s(?:→|=)\s|:\s|\s–\s", seg)
        if m and m.end() < len(seg):
            out.append(E(seg[:m.end()]) + f'<b class="k">{E(seg[m.end():])}</b>')
            continue
        pos = 0
        for n in NUM_MASK.finditer(seg):
            out.append(E(seg[pos:n.start()]) + f'<b class="k">{E(n.group(0))}</b>')
            pos = n.end()
        out.append(E(seg[pos:]))
    return "".join(out)


UP_RE = re.compile(r"^\W*(?:\d+\w*\s*(?:to\s*\d+\w*)?\s*)?(?:U\.\s?P(?!\.?\s?S\.?\s?C)|UP\b|UPP(?:CS|SC)\b|Uttar Pradesh)")


def tag_html(t):
    return f'<span class="tag{" upp" if UP_RE.match(t) else ""}">{E(t)}</span>'


# ------------------------------------------------------------------ model
class Model:
    def __init__(self, key, draft):
        self.key, self.book = key, BOOKS[key]
        d = book_dir(key)
        self.src = json.loads((d / "source.json").read_text(encoding="utf-8"))
        self.clusters = json.loads((d / "clusters.json").read_text(encoding="utf-8"))
        self.mem = {}
        for p in sorted((d / "memory").glob("w*.part*.json")):
            try:
                self.mem.update(json.loads(p.read_text(encoding="utf-8")))
            except ValueError:
                if not draft:
                    raise
                print(f"  (draft) skipped unreadable {p.name}")
        missing = [c["id"] for c in self.clusters if c["id"] not in self.mem]
        if missing and not draft:
            raise SystemExit(f"{len(missing)} clusters have no memory card (e.g. {missing[:8]}); run the writers or use --draft")
        self.missing = len(missing)
        self.qs = self.src["questions"]
        self.q_by = {q["id"]: q for q in self.qs}
        self.chapters = self.src["chapters"]
        self.cl_of = {qid: c for c in self.clusters for qid in c["qids"]}
        self.by_ch = OrderedDict((c["num"], [x for x in self.clusters if x["ch"] == c["num"]]) for c in self.chapters)
        self.anchor = {q["id"]: f'c{q["ch"]}-t{q["num"]}' for q in self.qs}
        self.full, self.quick, self.plan = self.book["files"]
        self.build_questions()

    def card(self, cl):
        m = clean_card(self.mem.get(cl["id"], {}))
        if m.get("c") and self.q_by[cl["head"]]["ans"] == "*":
            # the book prints "Ans. (*)": say so in the page's own words, not "answer not printed"
            m["c"] = STAR_NOTE.sub("The book gives no single answer (*)", m["c"])
        return m

    def head(self, cl):
        return self.q_by[cl["head"]]

    def remember(self, cl):
        r = self.card(cl).get("r")
        if r:
            return r
        h = self.head(cl)
        ans = "; ".join(text(h["options"].get(a, [])) for a in re.findall(r"[a-e]", h["ans"]))
        return f'{text(h["stem"])} → {ans}' if ans else text(h["stem"])

    def build_questions(self):
        self.pq = OrderedDict()
        self.q_pid = {}
        for q in self.qs:
            letters = re.findall(r"[a-e]", q["ans"])
            keys = sorted(q["options"])
            if len(keys) < 2 or not letters or any(l not in q["options"] for l in letters):
                continue
            # options that are pictures (blank) or read the same as the answer cannot be scored
            texts = {k: re.sub(r"\s+", " ", text(v)).strip().lower() for k, v in q["options"].items()}
            if any(not t for t in texts.values()) or any(texts[k] == texts[a] for a in letters for k in keys if k not in letters):
                continue
            cl = self.cl_of[q["id"]]
            pid = f"p{len(self.pq) + 1:05d}"
            ch = self.chapters[q["ch"] - 1]
            years = q["years"] or cl["years"]
            ans_txt = "; ".join(f"({a}) {text(q['options'][a])}" for a in letters)
            fb = f"Answer: {ans_txt}."
            r = self.card(cl).get("r")
            if r:
                fb += f" Remember: {r}"
            self.pq[pid] = {"e": f"Ch {q['ch']} · {ch['title']}" + (f" · {q['tags'][0]}" if q["tags"] else ""),
                            "s": text(q["stem"]), "m": blocks_plain(q["mid"])[:8],
                            "o": [text(q["options"][k]) for k in keys], "k": [keys.index(a) for a in letters],
                            "f": fb, "h": self.anchor[q["id"]], "ch": f"c{q['ch']}",
                            "y": years[-1] if years else 0, "p": cl["priority"], "up": 1 if q["up"] else 0,
                            "kind": "book-pyq"}
            self.q_pid[q["id"]] = pid
        known = [x["y"] for x in self.pq.values() if x["y"]]
        fallback = Counter(known).most_common(1)[0][0] if known else 2020
        for x in self.pq.values():
            if not x["y"]:
                x["y"] = fallback
        self.ch_count = Counter(x["ch"] for x in self.pq.values())

    def repeated(self):
        rows = [c for c in self.clusters if c["papers"] >= 2]
        return sorted(rows, key=lambda c: (-c["papers"], c["priority"], c["ch"], c["id"]))

    def meta(self):
        up_q = sum(1 for q in self.qs if q["up"])
        return {"question_kind": "book-pyq", "book_questions": len(self.qs), "practice_questions": len(self.pq),
                "uppsc_questions": up_q, "fact_clusters": len(self.clusters),
                "must_know": sum(1 for c in self.clusters if c["priority"] == 1),
                "repeated_facts": len(self.repeated()), "source_pdf_pages": self.src["pages"],
                "chapter_practice_counts": {f"c{c['num']}": self.ch_count.get(f"c{c['num']}", 0) for c in self.chapters},
                "context": f"{self.book['pdf'].name}; every question of the book from every exam, read by font "
                           "(question bold, options regular, answer and exam tags bold)"}


# ------------------------------------------------------------------ page parts
def assets(model):
    css = (HERE / "fonts_embedded.css").read_text(encoding="utf-8") + "\n" + (HERE / "pq_styles.css").read_text(encoding="utf-8")
    js = (HERE / "pq_runtime.js").read_text(encoding="utf-8")
    js = js.replace("__FULL__", model.full).replace("__P__", model.book["prefix"] + "2").replace("__PLAN__", model.book["plan_key"])
    return css, js


def head(model, title, desc, mode):
    css, _ = assets(model)
    if mode == "plan":
        tools = '<span class="prog" id="prog">0 of 72 hours done</span>'
    else:
        tools = ('<input id="q" type="search" placeholder="Search a word, name or Article…" aria-label="Search notes" autocomplete="off">'
                 '<label class="tog"><input id="test" type="checkbox"> Test mode</label>')
    return (f'<!DOCTYPE html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n'
            f'<meta name="viewport" content="width=device-width, initial-scale=1">\n<title>{E(title)}</title>\n'
            f'<meta name="description" content="{E(desc)}">\n<style>\n{css}\n</style>\n</head>\n<body data-mode="{mode}">\n'
            f'<header class="top"><button id="menu" type="button" aria-label="Open contents" aria-expanded="false" aria-controls="side">☰</button>'
            f'<a class="brand" href="#home">{E(model.book["name"])} · UPPCS</a>{tools}</header>\n'
            + ('<div class="progress-track"><i id="bar"></i></div>\n' if mode == "plan" else "")
            + '<div class="wrap">\n')


def tail(model, with_q):
    _, js = assets(model)
    out = ['</main></div><div id="scrim"></div>',
           '<script id="study-meta" type="application/json">' + json.dumps(model.meta(), ensure_ascii=False).replace("</", "<\\/") + "</script>"]
    if with_q:
        out.append('<script id="pqd" type="application/json">' + json.dumps(model.pq, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/") + "</script>")
    out.append("<script>" + js + "</script>\n</body>\n</html>\n")
    return "\n".join(out)


def grouping(model):
    """For each chapter: (book part heading to show before it, main-chapter heading to show before
    it, short title inside its group). Geography and Science split a main chapter into sub-topic
    units ("Climate · Rainfall"); the menus show "Climate" once and the units under it."""
    # a main chapter counts within its book part: "Miscellaneous" in Physics is not the one in Biology
    size = Counter((c.get("book_part"), c.get("group")) for c in model.chapters if c.get("group"))
    part = grp = None
    out = []
    for c in model.chapters:
        p_head = c["book_part"] if c.get("book_part") and c["book_part"] != part else None
        part = c.get("book_part") or part
        g = c.get("group")
        multi = bool(g) and size[(c.get("book_part"), g)] > 1
        g_head = g if multi and (g != grp or p_head) else None
        grp = g
        short = c["title"][len(g) + 3:] if multi and c["title"].startswith(g + " · ") else c["title"]
        out.append((p_head, g_head, short if multi else None))
    return out


def toc(model):
    items = []
    for c, (p_head, g_head, _) in zip(model.chapters, grouping(model)):
        n = c["num"]
        if p_head:
            items.append(f'<li class="tpart">{E(p_head)}</li>')
        if g_head:
            items.append(f'<li class="tgrp">{E(g_head)}</li>')
        up = sum(1 for q in model.qs if q["ch"] == n and q["up"])
        # the full title stays here: the dashboard matches plan hours to these names
        items.append(f'<li><a href="#c{n}"><span class="no">{n}</span><span class="nm">{E(c["title"])}</span>'
                     f'<span class="p up">{up} from UP papers</span>'
                     f'<span class="q">{model.ch_count.get(f"c{n}", 0)} past-paper questions</span></a></li>')
    return '<ol class="toc">' + "".join(items) + "</ol>"


def side_nav(model, extra):
    out = ['<nav class="side" id="side" aria-label="Contents"><a href="#home" data-v="home">Start here</a>']
    out += [f'<a href="#{v}" data-v="{v}">{E(t)}</a>' for v, t in extra]
    groups = grouping(model)
    if not any(p for p, _, _ in groups):
        out.append('<div class="lb">Chapters</div>')
    for c, (p_head, g_head, short) in zip(model.chapters, groups):
        if p_head:
            out.append(f'<div class="lb">{E(p_head)}</div>')
        if g_head:
            out.append(f'<div class="gp">{E(g_head)}</div>')
        cls = ' class="in"' if short else ""
        out.append(f'<a href="#c{c["num"]}" data-v="c{c["num"]}"{cls}><span>{c["num"]}</span>{E(short or c["title"])}</a>')
    out.append("</nav><main>")
    return "".join(out)


STAR_NOTE = re.compile(r"^(?:Answer not printed|No answer printed|Book prints answer '\*'|Book prints no answer|"
                       r"No single answer printed|No single answer|No answer)(?:\s*\(\*\))?", re.I)


def clean_card(m):
    m = dict(m)
    for k, lab in (("t", r"don'?t confuse"), ("h", r"memory aid"), ("r", r"remember")):
        if m.get(k):
            m[k] = re.sub(rf"^\s*{lab}\s*[:\-–]?\s*", "", m[k], flags=re.I).strip()
            # capitalise an ordinary first word only: "g = GM/R²", "pH", "mRNA" stay as written
            first = m[k].split(" ", 1)[0]
            if len(first) > 1 and first.isalpha() and first.islower():
                m[k] = m[k][:1].upper() + m[k][1:]
    return m


def card_html(model, cl, story=False):
    m = model.card(cl)
    parts = [f'<p class="line"><b>Remember:</b> {E(model.remember(cl))}</p>']
    if m.get("h"):
        parts.append(f'<p class="hook"><b>Memory aid</b> {E(m["h"])}</p>')
    if m.get("t"):
        parts.append(f'<p class="trap"><b>Don\'t confuse</b> {E(m["t"])}</p>')
    if m.get("c"):
        parts.append(f'<p class="check"><b>Check</b> {E(m["c"])}</p>')
    if m.get("hi"):
        parts.append(f'<p class="hi">हिंदी: {E(" · ".join(m["hi"]))}</p>')
    return '<div class="mem">' + "".join(parts) + "</div>"


def question_html(model, q, with_ids=True):
    cl = model.cl_of[q["id"]]
    aid = model.anchor[q["id"]]
    idattr = f' id="{aid}"' if with_ids else ""
    must = '<span class="must">Must know</span>' if cl["priority"] == 1 and cl["head"] == q["id"] else ""
    tags = "".join(tag_html(t) for t in q["tags"])
    letters = re.findall(r"[a-e]", q["ans"])
    opts = "".join(f'<li class="pt{" ok" if k in letters else ""}"><span class="ol">({k})</span>{runs_html(v, False)}</li>'
                   for k, v in q["options"].items())
    if letters:
        ans = "; ".join(f"({a}) {text(q['options'].get(a, []))}".strip() for a in letters)
    elif q["ans"] == "*":
        ans = "The book marks this question as having no single correct option (*)."
    else:
        ans = "Not printed in the book."
    out = [f'<article class="topic qcard"{idattr} data-u="{cl["id"]}" data-title="Q{q["num"]}">',
           f'<div class="qh"><span class="qn">Q{q["num"]}</span>{tags}{must}<span class="pg">PDF p. {q["page"]}</span></div>',
           f'<p class="qs pt">{runs_html(q["stem"], False)}</p>']
    if q["mid"]:
        out.append(f'<div class="qmid">{blocks_html(q["mid"], mask=False)}</div>')
    if opts:
        out.append(f'<ol class="opts">{opts}</ol>')
    if q.get("opt_note"):
        out.append(f'<p class="same">{E(q["opt_note"])}</p>')
    shown = [re.sub(r"\s+", " ", text(v)).strip().lower() for v in q["options"].values()]
    if letters and (not q["options"] or any(not t for t in shown)):
        out.append(f'<p class="same">The options of this question are pictures or diagrams in the book; see PDF p. {q["page"]}.</p>')
    elif len(set(shown)) < len(shown):
        out.append(f'<p class="same">Two options read the same here: either they are formulas the page text cannot show, '
                   f'or the book repeats an option. See PDF p. {q["page"]}.</p>')
    if q.get("printed_num"):
        out.append(f'<p class="same">The book prints this question’s number as {q["printed_num"]}, the same as the one before; '
                   f'it is numbered {q["num"]} here.</p>')
    out.append(f'<p class="ans pt">Answer: <span class="a">{E(ans)}</span></p>')
    if cl["head"] == q["id"]:
        out.append(card_html(model, cl))
    else:
        h = model.head(cl)
        out.append(f'<p class="same">Same fact as <a href="#{model.anchor[h["id"]]}">Q{h["num"]}</a>: {E(short(model.remember(cl), 160))}</p>')
    if q["expl"]:
        see = q.get("see")
        if see and see in model.q_by and len(q["expl"]) == 1:
            out.append(f'<p class="same">{runs_html(q["expl"][0]["runs"])} <a href="#{model.anchor[see]}">Go to it</a></p>')
        else:
            out.append(f'<details class="ex" open><summary>Explanation</summary>{blocks_html(q["expl"])}</details>')
    out.append("</article>")
    return "".join(out)


HOW = """<div class="how">
<div><b>1. Read the chapter's key facts first.</b> Each chapter opens with the book's own summary. Then go through the questions: the question is in bold, the options below it, the correct option is highlighted in green, and the exam that asked it is shown as a tag (green tag = an Uttar Pradesh paper).</div>
<div><b>2. Learn the green "Remember" line.</b> It is the one fact the question tests, in a single line. Questions that test the same fact point back to the first one, so you learn each fact once.</div>
<div><b>3. Turn on Test mode and recall.</b> Answers, the green highlights and the Remember lines are hidden. Answer from memory, then tap the grey box to check. Recalling fixes facts far better than re-reading.</div>
<div><b>4. Practise with spaced repetition.</b> Every question is in Practice with its real options. Mistakes come back in "Only my mistakes" until you get them right twice. Purple "Memory aid" lines and red "Don't confuse" lines help with tricky facts.</div>
</div>"""


def chapter_view(model, c):
    n = c["num"]
    qs = [q for q in model.qs if q["ch"] == n]
    cls = model.by_ch[n]
    up = sum(1 for q in qs if q["up"])
    must = sum(1 for x in cls if x["priority"] == 1)
    out = [f'<section class="view ch" id="c{n}" data-title="{E(c["title"])}"><p class="eyebrow">Chapter {n} · PDF p. {c["page"]}'
           + (f' · {E(c["part"])}' if c.get("part") else "") + "</p>"
           f'<h2>{E(c["title"])}</h2>'
           f'<p class="gist">{len(qs)} questions ({up} from UP papers) · {len(cls)} facts to learn · {must} marked Must know</p>',
           '<p class="context testnote">Test mode is on: tap a grey box to reveal the answer.</p>',
           f'<a class="btn" href="#practice" data-practice-ch="c{n}">Practise this chapter’s {model.ch_count.get(f"c{n}", 0)} questions →</a>']
    if c["theory"]:
        out.append(f'<details class="theory" open><summary>Key facts from the book ({len(c["theory"])} points)</summary>'
                   f'{blocks_html(c["theory"])}</details>')
    section = None
    for q in qs:
        if q.get("section") and q["section"] != section:
            section = q["section"]
            out.append(f'<h3 class="sec">{E(section)}</h3>')
            intro = next((s["intro"] for s in c["sections"] if s["title"] == section and s.get("intro")), None)
            if intro:
                out.append(blocks_html(intro))
        out.append(question_html(model, q))
    prev_c = model.chapters[n - 2] if n > 1 else None
    next_c = model.chapters[n] if n < len(model.chapters) else None
    out.append('<nav class="pn">' + (f'<a href="#c{n - 1}">← {E(prev_c["title"])}</a>' if prev_c else '<a href="#home">← Start</a>')
               + (f'<a class="nx" href="#c{n + 1}">{E(next_c["title"])} →</a>' if next_c else "") + "</nav></section>")
    return "".join(out)


def repeated_rows(model, link_prefix=""):
    rows = []
    for cl in model.repeated():
        papers = "; ".join(dict.fromkeys(cl["tags"]))
        h = model.head(cl)
        rows.append(f'<li><details><summary><span class="t"><b>Ch {cl["ch"]}</b> {E(model.remember(cl))}</span>'
                    f'<span class="ps"><span class="p up">×{cl["papers"]}</span></span></summary>'
                    f'<div class="yrs"><div>{E(papers)}</div><p>Q: {E(text(h["stem"]))}</p>'
                    f'<a href="{link_prefix}#{model.anchor[h["id"]]}">Open the question →</a></div></details></li>')
    return rows


def glossary(model):
    seen = OrderedDict()
    for cl in model.clusters:
        for h in model.card(cl).get("hi", []):
            k = h.strip()
            if k and k not in seen:
                seen[k] = (cl["ch"], model.anchor[cl["head"]])
    rows = []
    for h, (ch, aid) in sorted(seen.items(), key=lambda kv: kv[0].lower()):
        m = re.match(r"^(.*?)\s*\((.*)\)\s*$", h)
        en, hi = (m.group(1), m.group(2)) if m else (h, "")
        rows.append(f'<tr><td>{E(en)}</td><td lang="hi">{E(hi)}</td><td><a href="#{aid}">Ch {ch}</a></td></tr>')
    return rows


def latest_view(model):
    up = [q for q in model.qs if q["up"] and q["years"]]
    years = sorted({max(q["years"]) for q in up}, reverse=True)[:3]
    out = ['<section class="view" id="latest" data-title="Latest UP papers"><h2>Latest Uttar Pradesh papers</h2>',
           f'<p class="gist">Questions from the {len(years)} most recent years of Uttar Pradesh papers in this book. Recent papers show what UPPCS asks now.</p>']
    for y in years:
        qy = [q for q in up if max(q["years"]) == y]
        out.append(f'<h3 class="sec">{y} · {len(qy)} questions</h3><ol class="rows">')
        for q in qy:
            ans = "; ".join(text(q["options"].get(a, [])) for a in re.findall(r"[a-e]", q["ans"]))
            out.append(f'<li><a href="#{model.anchor[q["id"]]}">{E(short(text(q["stem"]), 160))}</a> <span class="qa"><span class="a">{E(ans)}</span></span>'
                       f' <small>{E("; ".join(t for t in q["tags"] if UP_RE.match(t)))}</small></li>')
        out.append("</ol>")
    out.append("</section>")
    return "".join(out)


def foot_line(model):
    m = model.meta()
    return (f'Based on {m["practice_questions"]} past-paper questions in practice ({m["uppsc_questions"]} of the book\'s '
            f'{m["book_questions"]} questions are from Uttar Pradesh papers), grouped into {m["fact_clusters"]} facts to learn; '
            f'{m["repeated_facts"]} facts asked in two or more papers. Source: {model.book["pdf"].name} ({m["source_pdf_pages"]} pages).')


# ------------------------------------------------------------------ the three pages
def build_full(model):
    name = model.book["name"]
    rows = repeated_rows(model)
    out = [head(model, f"{name} Full Notes · UPPCS", f"Every past-paper question of the {name} book with answers, explanations and memory cards for UPPCS.", "full"),
           side_nav(model, [("repeated", "Asked again and again"), ("latest", "Latest UP papers"),
                            ("practice", f"Practice · {len(model.pq):,}"), ("glossary", "Hindi terms (शब्दावली)")])]
    out.append(f'<section class="view" id="home" data-title="Start"><p class="eyebrow">{E(model.book["pdf"].name)}</p>'
               f'<h1>{E(name)} for UPPCS <span class="pg">({E(model.book["hindi"])})</span></h1>'
               f'<p class="gist">All {len(model.qs):,} past-paper questions of the book, chapter by chapter, each with its answer, the exams that asked it, '
               'the book\'s explanation and a one-line fact to remember.</p>'
               f'{HOW}{toc(model)}<p class="foot">{E(foot_line(model))}</p></section>')
    out.append(f'<section class="view" id="repeated" data-title="Asked again and again"><h2>Asked again and again</h2>'
               f'<p class="gist">{len(rows)} facts asked in two or more papers, most-asked first. Learn these before anything else.</p>'
               f'<ol class="rows">{"".join(rows)}</ol></section>')
    out.append(latest_view(model))
    opts = "".join(f'<option value="c{c["num"]}">{c["num"]}. {E(c["title"])} ({model.ch_count.get(f"c{c["num"]}", 0)})</option>' for c in model.chapters)
    out.append(f'<section class="view" id="practice" data-title="Practice"><h2>Practice</h2>'
               f'<p class="gist">{len(model.pq):,} real past-paper questions with their own options. Your answers and mistakes are saved on this device.</p>'
               f'<div class="pq-bar"><label>Chapter <select id="pqCh"><option value="">All chapters</option>{opts}</select></label>'
               '<label><input id="pqUp" type="checkbox"> UP papers only</label><label><input id="pqPri" type="checkbox"> Must-know only</label>'
               '<label><input id="pqMiss" type="checkbox"> Only my mistakes</label>'
               '<button id="pqShuf" type="button">Shuffle</button><button id="pqReset" type="button">Clear my answers</button></div>'
               '<p class="score"></p><ol class="pq" id="pqList"></ol><button id="pqMore" class="btn" type="button">Show 15 more</button></section>')
    g = glossary(model)
    out.append(f'<section class="view" id="glossary" data-title="Hindi terms"><h2>Hindi terms <span class="pg">(शब्दावली)</span></h2>'
               f'<p class="gist">{len(g)} standard Hindi terms used in these notes, for the bilingual paper.</p>'
               f'<div class="table-scroll"><table class="gl"><tr><td>English</td><td>हिंदी</td><td>Where</td></tr>{"".join(g)}</table></div></section>')
    for c in model.chapters:
        out.append(chapter_view(model, c))
    out.append('<section class="view" id="results" data-title="Search"><h2>Search</h2><p class="score" id="rt"></p><ol id="rl"></ol></section>')
    out.append(tail(model, True))
    return "\n".join(out)


def quick_cluster(model, cl, full_link=True):
    m = model.card(cl)
    h = model.head(cl)
    must = '<span class="must">Must know</span>' if cl["priority"] == 1 else ""
    papers = f'<span class="tag">{cl["papers"]} paper{"s" if cl["papers"] != 1 else ""}</span>'
    up = '<span class="tag upp">UP</span>' if cl["up"] else ""
    hook = f'<p class="hook"><b>Memory aid</b> {E(m["h"])}</p>' if m.get("h") else ""
    trap = f'<p class="trap"><b>Don\'t confuse</b> {E(m["t"])}</p>' if m.get("t") else ""
    aid_html = f'<div class="aid">{hook}{trap}</div>' if hook or trap else ""
    link = f'<a href="{model.full}#{model.anchor[h["id"]]}">question</a>' if full_link else ""
    return (f'<article class="topic" id="{model.anchor[h["id"]]}" data-title="Q{h["num"]}"><p class="pt line">{recall_html(model.remember(cl))} {must}</p>'
            f'{aid_html}<p class="date">{up}{papers} {link}</p></article>')


def build_quick(model):
    name = model.book["name"]
    out = [head(model, f"{name} Quick Notes · UPPCS", f"One-line recall notes for every fact the {name} past papers test.", "quick"),
           side_nav(model, [("repeated", "Asked again and again")])]
    out.append(f'<section class="view" id="home" data-title="Start"><p class="eyebrow">{E(model.book["pdf"].name)}</p>'
               f'<h1>{E(name)} · Quick Notes</h1>'
               '<p class="gist">One line per fact the exams test, chapter by chapter, with memory aids and look-alike traps. '
               'Turn on Test mode: the answer part of every line becomes a grey box to recall. Each line links to its full question.</p>'
               f'{toc(model)}<p class="foot">{E(foot_line(model))}</p></section>')
    rows = repeated_rows(model, model.full)
    out.append(f'<section class="view" id="repeated" data-title="Asked again and again"><h2>Asked again and again</h2>'
               f'<h3 id="rep-facts">{len(rows)} facts asked in two or more papers</h3>'
               f'<ol class="rows">{"".join(rows)}</ol></section>')
    for c in model.chapters:
        n = c["num"]
        cls = model.by_ch[n]
        part = [f'<section class="view ch" id="c{n}" data-title="{E(c["title"])}"><p class="eyebrow">Chapter {n}</p><h2>{E(c["title"])}</h2>'
                f'<p class="gist">{len(cls)} facts · {sum(1 for x in cls if x["priority"] == 1)} Must know</p>'
                '<p class="context testnote">Test mode is on: tap a grey box to reveal the answer.</p>']
        if c["theory"]:
            part.append(f'<details class="theory"><summary>Key facts from the book ({len(c["theory"])} points)</summary>{blocks_html(c["theory"])}</details>')
        section = None
        for cl in cls:
            sec = model.head(cl).get("section")
            if sec and sec != section:
                section = sec
                part.append(f'<h3 class="sec">{E(sec)}</h3>')
            part.append(quick_cluster(model, cl))
        part.append("</section>")
        out.append("".join(part))
    out.append('<section class="view" id="results" data-title="Search"><h2>Search</h2><p class="score" id="rt"></p><ol id="rl"></ol></section>')
    out.append(tail(model, False))
    return "\n".join(out)


# ------------------------------------------------------------------ 72-hour plan
def cluster_weight(model, cl):
    return sum(1 + (1 if model.q_by[q]["up"] else 0) for q in cl["qids"]) + (2 if cl["priority"] == 1 else 0)


def split_hours(model):
    """54 learn hours: big chapters split into parts, small neighbours share an hour."""
    w = {n: sum(cluster_weight(model, x) for x in cls) for n, cls in model.by_ch.items()}
    target = sum(w.values()) / LEARN_HOURS
    pieces = []
    for n, cls in model.by_ch.items():
        k = max(1, round(w[n] / target))
        if k == 1:
            pieces.append({"chs": [n], "cls": cls, "part": None})
            continue
        size = w[n] / k
        cur, acc, made = [], 0, []
        for x in cls:
            cur.append(x)
            acc += cluster_weight(model, x)
            if acc >= size * (len(made) + 1) and len(made) < k - 1:
                made.append(cur)
                cur = []
        made.append(cur)
        made = [m for m in made if m]
        for i, m in enumerate(made, 1):
            pieces.append({"chs": [n], "cls": m, "part": (i, len(made))})
    hours = []
    for p in pieces:
        if (p["part"] is None and hours and hours[-1]["part"] is None
                and sum(cluster_weight(model, x) for x in hours[-1]["cls"]) + sum(cluster_weight(model, x) for x in p["cls"]) <= target * 1.05):
            hours[-1]["chs"] += p["chs"]
            hours[-1]["cls"] += p["cls"]
        else:
            hours.append({"chs": list(p["chs"]), "cls": list(p["cls"]), "part": p["part"]})

    def weight(h):
        return sum(cluster_weight(model, x) for x in h["cls"])
    while len(hours) > LEARN_HOURS:
        # merge the lightest neighbours: two whole-chapter hours, or two parts of one chapter
        pairs = [i for i in range(len(hours) - 1)
                 if (hours[i]["part"] is None and hours[i + 1]["part"] is None)
                 or (hours[i]["part"] and hours[i + 1]["part"] and hours[i]["chs"] == hours[i + 1]["chs"])]
        best = min(pairs, key=lambda i: weight(hours[i]) + weight(hours[i + 1]), default=None)
        if best is None:
            raise SystemExit(f"cannot fit {len(hours)} learn hours into {LEARN_HOURS}")
        hours[best]["chs"] += hours[best + 1]["chs"]
        hours[best]["cls"] += hours[best + 1]["cls"]
        del hours[best + 1]
    while len(hours) < LEARN_HOURS:          # split the heaviest single-chapter hour in two
        i = max((i for i in range(len(hours)) if len(hours[i]["chs"]) == 1 and len(hours[i]["cls"]) > 1),
                key=lambda i: weight(hours[i]))
        h = hours[i]
        half = len(h["cls"]) // 2
        n = h["chs"][0]
        a = {"chs": [n], "cls": h["cls"][:half], "part": True}
        b = {"chs": [n], "cls": h["cls"][half:], "part": True}
        hours[i:i + 1] = [a, b]
    # titles (the dashboard maps Learn hours back to chapters from these)
    title_of = {c["num"]: c["title"] for c in model.chapters}
    parts_of = Counter(h["chs"][0] for h in hours if len(h["chs"]) == 1)
    seen = Counter()
    for h in hours:
        chs = h["chs"]
        if len(chs) == 1:
            seen[chs[0]] += 1
            k = parts_of[chs[0]]
            h["title"] = title_of[chs[0]] + (f" · part {seen[chs[0]]} of {k}" if k > 1 else "")
        elif len(chs) == 2:
            h["title"] = f"{title_of[chs[0]]} + {title_of[chs[1]]}"
        else:
            h["title"] = f"{title_of[chs[0]]} to {title_of[chs[-1]]}"
    return hours


def hour_shell(n, phase, title, gist, guide):
    return (f'<section class="view" id="h{n}" data-n="{n}" data-title="Hour {n}"><p class="eyebrow">Hour {n} of 72 · {phase}</p>'
            f'<h2>{E(title)}</h2><p class="gist">{E(gist)}</p><div class="guide">{guide}</div>')


def done_html(n):
    nxt = f'<a class="btn nx" href="#h{n + 1}">Hour {n + 1} →</a>' if n < 72 else '<a class="btn nx" href="#home">Back to the plan →</a>'
    return f'<div class="done"><button class="btn" type="button" data-done="{n}">Mark hour {n} done</button>{nxt}</div></section>'


def plan_cluster(model, cl):
    """A fact to learn in the plan: the question, its answer, the Remember line and aids."""
    h = model.head(cl)
    letters = re.findall(r"[a-e]", h["ans"])
    ans = "; ".join(text(h["options"].get(a, [])) for a in letters) or "—"
    m = model.card(cl)
    must = '<span class="must">Must know</span>' if cl["priority"] == 1 else ""
    extra = "".join(f'<p class="{c}"><b>{lab}</b> {E(m[k])}</p>' for k, c, lab in (("h", "hook", "Memory aid"), ("t", "trap", "Don't confuse")) if m.get(k))
    return (f'<article class="topic"><ul class="qa"><li class="pt"><span class="q">{E(text(h["stem"]))}</span>'
            f'<span class="a">{E(ans)}</span></li></ul><p class="pt line">{recall_html(model.remember(cl))} {must}</p>{extra}'
            f'<p class="date"><a href="{model.full}#{model.anchor[h["id"]]}">Full question and explanation</a> · {cl["papers"]} paper(s)</p></article>')


def build_plan(model):
    name = model.book["name"]
    learn = split_hours(model)
    assert len(learn) == LEARN_HOURS, len(learn)
    out = [head(model, f"{name} in 72h · UPPCS", f"72 one-hour sessions to learn the {name} past papers before UPPCS Prelims.", "plan")]
    nav = ['<nav class="side" id="side" aria-label="Hours"><a href="#home" data-v="home"><span></span>Plan</a><div class="lb">Learn</div>']
    for i, h in enumerate(learn, 1):
        nav.append(f'<a href="#h{i}" data-v="h{i}"><span>{i}</span>{E(h["title"])}</a>')
    must = [c for c in model.clusters if c["priority"] == 1]
    per = -(-len(must) // 10)
    revise = [must[i:i + per] for i in range(0, len(must), per)][:10]
    while len(revise) < 10:
        revise.append([])
    title_of = {c["num"]: c["title"] for c in model.chapters}
    revise_titles = []
    for chunk in revise:
        chs = sorted({x["ch"] for x in chunk})
        revise_titles.append("Revise: " + (f"{title_of[chs[0]]} to {title_of[chs[-1]]}" if len(chs) > 1 else title_of[chs[0]] if chs else "mixed"))
    revise_titles += ["Revise: your weak questions", "Revise: traps and look-alike facts"]
    nav.append('<div class="lb">Revise</div>')
    for j, t in enumerate(revise_titles):
        n = LEARN_HOURS + 1 + j
        nav.append(f'<a href="#h{n}" data-v="h{n}"><span>{n}</span>{E(t)}</a>')
    nav.append('<div class="lb">Test</div>')
    for j in range(TEST_HOURS):
        n = LEARN_HOURS + REVISE_HOURS + 1 + j
        nav.append(f'<a href="#h{n}" data-v="h{n}"><span>{n}</span>Mock test {j + 1}: 30 UP-paper questions</a>')
    nav.append("</nav><main>")
    out.append("".join(nav))
    hrs_by_ch = Counter(c for h in learn for c in h["chs"])
    rows = "".join(f'<tr><td>{c["num"]}. {E(c["title"])}</td><td>{hrs_by_ch[c["num"]]}</td></tr>' for c in model.chapters)
    out.append(f'<section class="view" id="home" data-title="72-hour plan"><p class="eyebrow">{LEARN_HOURS} learn · {REVISE_HOURS} revise · {TEST_HOURS} mock tests</p>'
               f'<h1>{E(name)} in 72 hours</h1><p class="gist">Learn every fact the {E(name)} past papers test in 72 hours before {EXAM}: '
               'one hour at a time, in order. Every hour mixes learning, recall and questions from earlier hours, so facts come back just as you start to forget them.</p>'
               '<div class="how"><div><b>Each learn hour (60 min):</b> read the key facts and the hour\'s questions with their answers (30) · '
               'cover the answers and recall the grey boxes (10) · answer this hour\'s questions (10) · answer the spaced-review questions from 1, 3, 7, 15 and 30 hours ago and your weak questions (10).</div>'
               '<div><b>Revise hours:</b> every Must-know fact, then your weak questions, then look-alike traps.</div>'
               '<div><b>Mock tests:</b> 30 real Uttar Pradesh paper questions in 25 minutes. Review every mistake afterwards.</div></div>'
               '<a class="cta" id="cont" href="#h1">Start with hour 1 →</a>'
               f'<h3 class="sec">Learn hours per chapter</h3><div class="table-scroll"><table><tr><td>Chapter</td><td>Learn hours</td></tr>{rows}</table></div>'
               f'<p class="foot">72 hours before {EXAM}. Chapters with more questions, especially from UP papers, get more time. Progress is saved on this device.</p></section>')
    hour_q = {}
    first_hour_of = {}
    for i, h in enumerate(learn, 1):
        for n in h["chs"]:
            first_hour_of.setdefault(n, i)
    for i, h in enumerate(learn, 1):
        cls = h["cls"]
        qids = [model.q_pid[q] for x in cls for q in x["qids"] if q in model.q_pid]
        hour_q[i] = qids
        review = []
        for gap in REVIEW_GAPS:
            j = i - gap
            if j >= 1 and hour_q.get(j):
                pool = list(hour_q[j])
                random.Random(seed("rev", str(i), str(j))).shuffle(pool)
                review += pool[:3]
        gist = f"{len(cls)} facts · {len(qids)} questions · {sum(1 for x in cls if x['priority'] == 1)} Must know"
        guide = (f'Read the key facts and each question with its answer (30 min), then cover the answers and recall (10 min). '
                 f'<a href="{model.full}#c{h["chs"][0]}">Open the chapter in the full notes</a> for explanations.')
        part = [hour_shell(i, "Learn", h["title"], gist, guide), '<div class="read">']
        for n in h["chs"]:
            c = model.chapters[n - 1]
            if first_hour_of[n] == i and c["theory"]:
                part.append(f'<details class="theory" open><summary>{E(c["title"])}: key facts from the book</summary>{blocks_html(c["theory"])}</details>')
        for x in cls:
            part.append(plan_cluster(model, x))
        part.append("</div>")
        if qids:
            take = qids[:40]
            part.append(f'<h3 class="ph">Practise this hour: {len(take)} questions</h3><p class="score"></p><ol class="pq" data-q="{",".join(take)}"></ol>')
        if review:
            part.append(f'<h3 class="ph">Spaced review: {len(review)} questions from earlier hours</h3><p class="score"></p><ol class="pq" data-q="{",".join(review)}"></ol>')
        if i > 1:
            part.append('<h3 class="ph">Your weak questions</h3><p class="score"></p><ol class="pq" data-review="10"></ol>')
        part.append(done_html(i))
        out.append("".join(part))
    for j, chunk in enumerate(revise):
        n = LEARN_HOURS + 1 + j
        qids = [model.q_pid[x["head"]] for x in chunk if x["head"] in model.q_pid][:40]
        part = [hour_shell(n, "Revise", revise_titles[j], f"{len(chunk)} Must-know facts. Say each one aloud before you read it.",
                           "Cover each line, recall it, then check. Answer the questions below.")]
        part += [plan_cluster(model, x) for x in chunk]
        part.append(f'<h3 class="ph">Must-know questions: {len(qids)}</h3><p class="score"></p><ol class="pq" data-q="{",".join(qids)}"></ol>')
        part.append(done_html(n))
        out.append("".join(part))
    n = LEARN_HOURS + 11
    out.append(hour_shell(n, "Revise", revise_titles[10], "Every question you have answered wrongly so far, hardest first.",
                          "Answer each one again. A question leaves this list once you get it right twice.")
               + '<p class="score"></p><ol class="pq" data-review="60"></ol>' + done_html(n))
    traps = [(x, model.card(x)["t"]) for x in model.clusters if model.card(x).get("t")]
    n = LEARN_HOURS + 12
    trap_html = "".join(f'<li class="pt"><b>Ch {x["ch"]}</b> {E(t)} <a href="{model.full}#{model.anchor[x["head"]]}">question</a></li>' for x, t in traps)
    out.append(hour_shell(n, "Revise", revise_titles[11], f"{len(traps)} look-alike facts that are easy to mix up.",
                          "Read each pair and say the difference in your own words.")
               + f'<ul class="read">{trap_html}</ul>' + done_html(n))
    rng = random.Random(seed("mocks", model.key))
    up = [p for p, x in model.pq.items() if x["up"]]
    up_must = [p for p in up if model.pq[p]["p"] == 1]
    up_rest = [p for p in up if model.pq[p]["p"] != 1]
    rng.shuffle(up_must)
    rng.shuffle(up_rest)
    for j in range(TEST_HOURS):
        n = LEARN_HOURS + REVISE_HOURS + 1 + j
        picked = up_must[j * 18:(j + 1) * 18] + up_rest[j * 12:(j + 1) * 12]
        rng.shuffle(picked)
        part = [hour_shell(n, "Test", f"Mock test {j + 1}: 30 UP-paper questions", "Real Uttar Pradesh paper questions from every chapter, more than half Must know.",
                           "Press Start, answer all 30 in 25 minutes, then Submit. Spend the rest of the hour reading the explanation of every mistake."),
                f'<div class="mock" data-min="25"><div class="mock-bar"><button class="btn" type="button" data-mock-start="m{j + 1}">Start 25-minute timer</button>'
                f'<span class="timer">25:00</span><button class="btn" type="button" data-mock-submit="m{j + 1}">Submit</button></div>'
                f'<p class="score"></p><ol class="pq" data-mock="m{j + 1}" data-q="{",".join(picked)}"></ol></div>', done_html(n)]
        out.append("".join(part))
    out.append(tail(model, True))
    return "\n".join(out), learn


def main():
    key = sys.argv[1]
    draft = "--draft" in sys.argv
    model = Model(key, draft)
    out_dir = model.book["out"]
    pages = ((model.full, build_full(model)), (model.quick, build_quick(model)))
    plan, learn = build_plan(model)
    for name, t in pages + ((model.plan, plan),):
        (out_dir / name).write_text(t, encoding="utf-8", newline="\n")
        print(f"wrote {name}: {len(t):,} chars")
    (book_dir(key) / "plan.json").write_text(json.dumps([{"hour": i, "title": h["title"], "clusters": [x["id"] for x in h["cls"]]}
                                                          for i, h in enumerate(learn, 1)], ensure_ascii=False, indent=0), encoding="utf-8")
    print(f"{key}: {len(model.qs)} questions, {len(model.pq)} in practice, {len(model.clusters)} facts, "
          f"{model.missing} cards missing{' (draft)' if draft else ''}; learn hours by chapter: {len(learn)} hours")


if __name__ == "__main__":
    main()
