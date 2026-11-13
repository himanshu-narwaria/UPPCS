"""Build study-dashboard.html: one UPPSC dashboard holding every subject separately.

Usage (from any folder):
    python build_dashboard.py
This also runs sitenav.py (global menu, breadcrumbs, related links) and security.py
(writes vercel.json with the security headers). sitenav.py adds the global menu, breadcrumbs and Related/Previous/Next
links to every page in the project.

For each subject folder listed in SUBJECTS it finds, by file name:
    full notes   *-uppsc-notes.html or *-full-notes.html
    quick notes  *quick-notes.html  (optional; the dashboard says so when missing)
    72-hour plan *-in-72h.html
It reads only these HTML files (never a PDF) and writes ../study-dashboard.html.
Every number on the page is parsed from them, so re-run this script after any notes file
changes. If a file's layout changes, the script stops with a clear error instead of
showing wrong numbers. Standard library only. Re-running on unchanged files gives an identical page; the
"Updated" dates come from the files' modified dates.
"""
import datetime
import glob
import html
import json
import os
import re
import sys
from collections import Counter, OrderedDict

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUT = os.path.join(ROOT, "study-dashboard.html")
E = html.escape

# Order here is the order of the tabs. Add a subject by adding a line.
SUBJECTS = [
    {"key": "history", "name": "Indian History", "hindi": "भारतीय इतिहास", "folder": "Indian_History_Part_2"},
    {"key": "environment", "name": "Environment & Ecology", "hindi": "पर्यावरण एवं पारिस्थितिकी", "folder": "Environment_2025"},
    {"key": "polity", "name": "Indian Polity", "hindi": "भारतीय राजव्यवस्था", "folder": "Indian_Polity_and_Governance"},
    {"key": "economy", "name": "Economy", "hindi": "अर्थव्यवस्था", "folder": "Economy 2024"},
    {"key": "geography", "name": "General Geography", "hindi": "सामान्य भूगोल", "folder": "General_Geography_Part_3"},
    {"key": "science", "name": "General Science", "hindi": "सामान्य विज्ञान", "folder": "General_Science_Part_7"},
    {"key": "current", "name": "Current Affairs", "hindi": "दृष्टि समसामयिकी", "folder": "Drishti-current affairs"},
]


# ------------------------------------------------------------------ helpers
def fail(msg):
    sys.exit("build_dashboard: " + msg)


def need(pattern, text, what, flags=re.S):
    m = re.search(pattern, text, flags)
    if not m:
        fail(f"could not find {what}; the file layout may have changed.")
    return m


def strip_tags(s):
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", "", s))).strip()


def norm(t):
    t = re.sub(r"\band\b", " ", t.lower().replace("&", " "))
    return re.sub(r"[^a-z0-9]", "", t)


def find_one(folder, patterns, required=True):
    hits = []
    for p in patterns:
        hits += sorted(glob.glob(os.path.join(ROOT, folder, p)))
    hits = list(OrderedDict.fromkeys(hits))
    if not hits:
        if required:
            fail(f"no file matching {patterns} in {folder}")
        return None
    if len(hits) > 1:
        fail(f"more than one file matches {patterns} in {folder}: {[os.path.basename(h) for h in hits]}")
    return hits[0]


def rel(path):
    return os.path.relpath(path, ROOT).replace(os.sep, "/")


def href(path, anchor=""):
    url = "/".join(part.replace(" ", "%20") for part in rel(path).split("/"))
    return url + ("#" + anchor if anchor else "")


def modified(path):
    return datetime.date.fromtimestamp(os.stat(path).st_mtime)


def fmt_date(d):
    return f"{d.day} {d:%b %Y}"


# ------------------------------------------------------------------ full notes, "views" layout (Polity, Economy)
def study_metadata(s):
    """Optional provenance contract for source practice rather than past exam papers."""
    m = re.search(r'<script[^>]*id=[\"\']study-meta[\"\'][^>]*>(.*?)</script>', s, re.S)
    return json.loads(m.group(1)) if m else {}


def parse_views_notes(s, label):
    meta = study_metadata(s)
    source_practice = meta.get("question_kind") == "source-practice"
    home = need(r'<section class="view" id="home".*?</section>', s, f"home view in {label}").group(0)
    toc = re.findall(r'<a href="#c(\d+)"><span class="no">\d+</span><span class="nm">([^<]+)</span>(?:<span class="p up">[^<]*</span>)?'
                     r'<span class="q">(\d+) (?:UPPSC PYQs|practice questions|past-paper questions)</span>', home)
    if not toc:
        fail(f"no chapter list in {label}")
    chapters = OrderedDict((int(n), {"title": html.unescape(t), "asked": int(q)}) for n, t, q in toc)
    data = json.loads(need(r'<script[^>]*id="pqd"[^>]*>(.*?)</script>', s, f"practice data in {label}").group(1))
    qs = list(data.values()) if isinstance(data, dict) else data
    bank_ch = Counter(int(q["ch"][1:]) for q in qs)
    for n, c in chapters.items():
        if bank_ch.get(n, 0) != c["asked"]:
            fail(f"{label}: chapter {n} lists {c['asked']} PYQs but its practice data holds {bank_ch.get(n, 0)}")
    rep = need(r'<section class="view" id="repeated".*?</section>', s, f"most repeated view in {label}").group(0)
    repeats = []
    for fact, cnt, papers, anchor in re.findall(
            r'<summary><span class="t">(.*?)</span><span class="ps"><span class="p up">×(\d+)</span></span></summary>'
            r'<div class="yrs"><div>(.*?)</div>(?:<p>.*?</p>\s*)*<a href="#([^"]+)"', rep, re.S):
        m = re.match(r"c(\d+)", anchor)
        repeats.append({"fact": strip_tags(fact), "count": int(cnt), "papers": strip_tags(papers), "anchor": anchor,
                        "ch": int(m.group(1)) if m else 0})
    stated = 0 if source_practice else int(need(r"(\d+) facts asked in two or more", rep, f"repeated-fact count in {label}").group(1))
    if stated != len(repeats):
        fail(f"{label}: parsed {len(repeats)} repeated facts, file states {stated}")
    if source_practice:
        if meta.get("practice_questions") != len(qs):
            fail(f"{label}: source-practice metadata disagrees with its question bank")
        priority_count = int(need(r"(\d+) priority facts from the source", rep, f"priority-fact count in {label}").group(1))
        if priority_count != meta.get("priority_facts") or len(re.findall(r"<summary>", rep)) != priority_count:
            fail(f"{label}: priority-fact count disagrees with the revision list")
        expected_counts = {f"c{n}": c["asked"] for n, c in chapters.items()}
        if meta.get("chapter_practice_counts") != expected_counts:
            fail(f"{label}: source-practice metadata disagrees with chapter counts")
        if meta.get("verified_uppsc_pyqs") != 0 or meta.get("verified_repeated_facts") != 0:
            fail(f"{label}: source-practice material must not claim verified exam provenance")
        if any(q.get("kind") != "source-practice" for q in qs):
            fail(f"{label}: source-practice questions must carry an explicit kind")
    foot = [strip_tags(x) for x in re.findall(r'<p class="foot">(.*?)</p>', home, re.S)]
    return {"layout": "views", "chapters": chapters, "years": Counter(q["y"] for q in qs), "after_years": [],
            "bank": len(qs), "bank_new": 0, "repeats": sorted(repeats, key=lambda r: -r["count"]),
            "latest_anchor": lambda y: "latest", "basis": foot[0] if foot else "", "extras": [],
            "source_practice": source_practice, "metadata": meta}


# ------------------------------------------------------------------ full notes, "sections" layout (Environment)
def parse_sections_notes(s, label):
    chapters = OrderedDict()
    for m in re.finditer(r'<section class="chapter" id="c(\d+)" data-title="([^"]*)" data-pages="([^"]*)"', s):
        chapters[int(m.group(1))] = {"title": html.unescape(m.group(2)), "pages": m.group(3)}
    if not chapters:
        fail(f"no chapters in {label}")
    data = json.loads(need(r'<script id="pq-data" type="application/json">(.*?)</script>', s, f"practice data in {label}").group(1))
    bank_ch = Counter(q["c"] for q in data)
    for n, c in chapters.items():
        c["asked"] = bank_ch.get(n, 0)
    after = [q for q in data if q.get("p") == "after the book"]
    block = need(r'id="dash-repeats".*?<tbody>(.*?)</tbody>', s, f"most repeated table in {label}").group(1)
    repeats = []
    for row in re.findall(r"<tr[^>]*>(.*?)</tr>", block, re.S):
        tds = re.findall(r"<td[^>]*>(.*?)</td>", row, re.S)
        if len(tds) < 6:
            fail(f"{label}: a most-repeated row has {len(tds)} cells, expected 6")
        link = re.search(r'href="#([^"]+)"', tds[1])
        repeats.append({"fact": strip_tags(tds[1]), "anchor": link.group(1) if link else "", "papers": strip_tags(tds[2]),
                        "count": int(strip_tags(tds[3])), "ch": int(re.search(r"\d+", strip_tags(tds[5])).group(0))})
    stated = int(need(r"(\d+) facts qualify", s, f"repeated-fact count in {label}").group(1))
    if stated != len(repeats):
        fail(f"{label}: parsed {len(repeats)} repeated facts, file states {stated}")

    # Extra sections that only this file has
    extras = []
    th = need(r'id="dash-themes".*?<tbody>(.*?)</tbody>', s, f"themes table in {label}").group(1)
    n_themes = len(re.findall(r"<tr[\s>]", th))
    extras.append(("Recurring themes", n_themes, "themes asked in 3 or more UPPSC papers", "dash-themes"))
    up = need(r'id="dash-up".*?(?=<section class="chapter")', s, f"UP Special in {label}").group(0)
    extras.append(("UP Special", up.count('class="tag upp"'), "Uttar Pradesh facts UPPSC has asked", "dash-up"))
    mains = re.findall(r"<tr[^>]*>\s*<td[^>]*>(\d{4})</td>\s*<td[^>]*>([^<]+)</td>",
                       need(r'id="mains-q".*?<tbody>(.*?)</tbody>', s, f"Mains table in {label}").group(1))
    extras.append(("UPPCS Mains", len(mains), f"real Mains questions, {min(y for y, _ in mains)}–{max(y for y, _ in mains)}", "mains-q"))
    new_title = html.unescape(need(r'<section class="chapter" id="add-new" data-title="([^"]*)"', s, "recent developments").group(1))
    extras.append((new_title, len(re.findall(r'<article class="topic" id="add-new-\d+"', s)), "topics added from current sources", "add-new"))
    gl = need(r'id="glossary".*?<tbody>(.*?)</tbody>', s, f"glossary in {label}").group(1)
    extras.append(("Hindi glossary", len(re.findall(r"<tr[\s>]", gl)), "English terms with their Hindi", "glossary"))
    for name, value, _, _ in extras:
        if not value:
            fail(f"{label}: found nothing for {name}")
    after_years = sorted({q["y"] for q in after})
    book_last = max(q["y"] for q in data if q.get("p") != "after the book")
    prov = " Their answers rest on UPPSC provisional keys." if after and "provisional" in after[0].get("v", "") else ""
    basis = (f"{len(data)} practice MCQs: {len(data) - len(after)} from the book (to {book_last}) and {len(after)} from "
             f"{', '.join(map(str, after_years))} papers added later, not from the book.{prov}")
    return {"layout": "sections", "chapters": chapters, "years": Counter(q["y"] for q in data), "after_years": after_years,
            "bank": len(data), "bank_new": len(after), "repeats": sorted(repeats, key=lambda r: -r["count"]),
            "latest_anchor": lambda y: f"dash-upp{y}", "basis": basis, "extras": extras}


def parse_full(path):
    s = open(path, encoding="utf-8").read()
    label = os.path.basename(path)
    if 'id="pqd"' in s:
        return parse_views_notes(s, label)
    if 'id="pq-data"' in s:
        return parse_sections_notes(s, label)
    fail(f"{label}: unknown notes layout")


# ------------------------------------------------------------------ quick notes
def parse_quick(path):
    s = open(path, encoding="utf-8").read()
    label = os.path.basename(path)
    meta = study_metadata(s)
    source_practice = meta.get("question_kind") == "source-practice"
    home = need(r'<section class="view" id="home".*?</section>', s, f"home view in {label}").group(0)
    toc = re.findall(r'<a href="#c(\d+)"><span class="no">\d+</span><span class="nm">([^<]+)</span>(?:<span class="p up">[^<]*</span>)?'
                     r'<span class="q">(\d+) (?:UPPSC PYQs|practice questions|past-paper questions)</span>', home)
    if not toc:
        fail(f"no chapter list in {label}")
    topics = Counter(int(c) for c in re.findall(r'<article class="topic" id="c(\d+)-t\d+"', s))
    chapters = OrderedDict((int(n), {"title": html.unescape(t), "asked": int(q), "topics": topics.get(int(n), 0)}) for n, t, q in toc)
    rep = need(r'<section class="view" id="repeated".*?</section>', s, f"most repeated view in {label}").group(0)
    facts_head = need(r'<h3 id="rep-facts"[^>]*>(\d+) (?:facts asked in two or more|priority facts from the source)', rep, f"revision-facts heading in {label}")
    facts_part = need(r'<h3 id="rep-facts".*?<ol class="rows">(.*?)</ol>', rep, f"repeated-facts list in {label}").group(1)
    n_rep = len(re.findall(r"<summary>", facts_part))
    if n_rep != int(facts_head.group(1)):
        fail(f"{label}: heading says {facts_head.group(1)} repeated facts but the list has {n_rep}")
    foot = [strip_tags(x) for x in re.findall(r'<p class="foot">(.*?)</p>', home, re.S)]
    basis = foot[0] if foot else ""
    m = re.search(r"Based on (\d+) (?:UPPSC|source practice|past-paper) questions", basis)
    if m and int(m.group(1)) != sum(c["asked"] for c in chapters.values()):
        fail(f"{label}: states {m.group(1)} questions but chapters add to {sum(c['asked'] for c in chapters.values())}")
    if not m:
        fail(f"{label}: no 'Based on N UPPSC questions' line to confirm the chapter counts")
    if source_practice and meta.get("priority_facts") != n_rep:
        fail(f"{label}: priority-fact metadata disagrees with the displayed list")
    return {"chapters": chapters, "repeats": 0 if source_practice else n_rep, "basis": basis,
            "source_practice": source_practice, "metadata": meta}


# ------------------------------------------------------------------ 72-hour plan
def parse_72h(path):
    s = open(path, encoding="utf-8").read()
    label = os.path.basename(path)
    exam = datetime.datetime.strptime(need(r"72 hours before (\d{1,2} [A-Z][a-z]+ \d{4})", s, f"exam date in {label}").group(1),
                                      "%d %B %Y").date()
    key = need(r'localStorage\.getItem\("([^"]+)"\)', s, f"progress key in {label}").group(1)
    nav = need(r'<nav class="side" id="side"[^>]*>(.*?)</nav>', s, f"side menu in {label}").group(1)
    phases = OrderedDict()
    cur = None
    for tok in re.finditer(r'<div class="lb">([^<]+)</div>|<a href="#h(\d+)" data-v="h\d+"><span>\d+</span>([^<]+)</a>', nav):
        if tok.group(1):
            cur = html.unescape(tok.group(1))
            phases[cur] = []
        elif cur:
            phases[cur].append((int(tok.group(2)), html.unescape(tok.group(3))))
    hours = [h for v in phases.values() for h in v]
    if [n for n, _ in hours] != list(range(1, 73)):
        fail(f"{label}: expected hours 1–72 in order, found {len(hours)}")
    return {"exam": exam, "key": key, "phases": phases, "hours": hours}


def chapter_hours(chapters, plan, label):
    """Learn-phase hours for each chapter. Hour titles name one chapter, join two with ' + ',
    or give a range 'A to B' that covers every chapter from A to B."""
    order = list(chapters)
    index = {norm(c["title"]): n for n, c in chapters.items()}
    out = {n: [] for n in order}
    for h, title in plan["phases"].get("Learn", []):
        base = re.sub(r" · part \d+ of \d+$", "", title)
        covered = []
        for part in base.split(" + "):
            if " to " in part and norm(part) not in index:
                a, b = (x.strip() for x in part.split(" to ", 1))
                if norm(a) not in index or norm(b) not in index:
                    fail(f"{label}: hour {h} names a range I can't match: {part!r}")
                i, j = order.index(index[norm(a)]), order.index(index[norm(b)])
                covered += order[i:j + 1]
            elif norm(part) in index:
                covered.append(index[norm(part)])
            else:
                fail(f"{label}: hour {h} names a chapter I can't match: {part!r}")
        for n in covered:
            out[n].append(h)
    missing = [chapters[n]["title"] for n in order if not out[n]]
    if missing:
        fail(f"{label}: no Learn hour found for {missing}")
    return out


# ------------------------------------------------------------------ rendering pieces
def year_svg(counts, highlight, label):
    years = list(range(min(counts), max(counts) + 1))
    vmax = max(counts.values())
    step = next(s for s in (5, 10, 20, 25, 50, 100, 200, 250, 500, 1000, 2000, 2500, 5000, 10 ** 9) if vmax / s <= 8)
    top = -(-vmax // step) * step
    W, H, L, B, T = 640, 220, 38, 30, 12
    pw, ph = W - L - 8, H - B - T
    bw = pw / len(years)
    every = 1 if len(years) <= 12 else 5
    out = [f'<svg viewBox="0 0 {W} {H}" role="img" aria-label="{E(label)}"><title>{E(label)}</title>']
    for v in range(0, top + 1, step):
        y = T + ph - ph * v / top
        out.append(f'<line x1="{L}" x2="{W - 8}" y1="{y:.1f}" y2="{y:.1f}" class="gl"/><text x="{L - 6}" y="{y + 4:.1f}" class="ax" text-anchor="end">{v}</text>')
    for i, yr in enumerate(years):
        v = counts.get(yr, 0)
        h = ph * v / top
        x = L + i * bw
        out.append(f'<rect x="{x + bw * .15:.1f}" y="{T + ph - h:.1f}" width="{bw * .7:.1f}" height="{h:.1f}" class="{"bar new" if yr in highlight else "bar"}">'
                   f'<title>{yr}: {v}</title></rect>')
        if yr % every == 0 or yr == years[-1] or len(years) <= 12:
            out.append(f'<text x="{x + bw / 2:.1f}" y="{H - B + 16}" class="ax" text-anchor="middle">{yr if len(years) <= 12 else yr}</text>')
    out.append(f'<line x1="{L}" x2="{W - 8}" y1="{T + ph}" y2="{T + ph}" class="base"/></svg>')
    return "".join(out)


def top_with_ties(rows, n=12):
    if not rows:
        return [], 0
    cut = rows[min(n, len(rows)) - 1]["count"]
    return [r for r in rows if r["count"] >= cut], cut


def render_source_practice(sub, F, Q, files):
    """Present authored recall separately from independently verified exam evidence."""
    k, full_h, meta = sub["key"], files["full"], F["metadata"]
    rows = "".join(
        f'<tr><td class="n">{n}</td><td><a href="{href(full_h, f"c{n}")}">{E(c["title"])}</a></td>'
        f'<td class="num">{c["asked"]}</td></tr>' for n, c in F["chapters"].items())
    full = f'''
<section class="blk" id="{k}-full" aria-labelledby="{k}-full-h">
<div class="bh"><div><p class="kind">Full notes</p><h3 id="{k}-full-h">Read, connect, recall</h3></div>
<a class="open" href="{href(full_h)}">Open full notes</a></div>
<p class="basis">{E(F["basis"])} Updated {fmt_date(modified(full_h))}.</p>
<div class="kpis"><div><b>{len(F["chapters"])}</b><span>chapters</span></div>
<div><b>{F["bank"]:,}</b><span>source practice questions</span></div>
<div><b>{meta.get("priority_facts", 0)}</b><span>priority revision facts</span></div>
<div><b>{meta.get("source_pdf_pages", 0)}</b><span>pages in the source PDF</span></div></div>
<p class="lead">Practice questions are learning exercises based on this PDF. No verified UPPSC PYQs or exam-repeat counts are claimed. Dates and rankings retain the issue's time context.</p>
<div class="tw"><table><thead><tr><th>#</th><th>Chapter</th><th class="num">Practice questions</th></tr></thead><tbody>{rows}</tbody></table></div>
<div class="extras"><a class="ex" href="{href(full_h, "repeated")}"><b>Revise</b><span>Priority facts selected from the source</span></a>
<a class="ex" href="{href(full_h, "practice")}"><b>Recall</b><span>Test yourself, then read the explanation</span></a></div></section>'''
    quick = ""
    if Q:
        qh = files["quick"]
        qrows = "".join(
            f'<li><a href="{href(qh, f"c{n}")}"><span class="qn">{n}</span><span class="qt">{E(c["title"])}</span>'
            f'<span class="qm">{c["topics"]} topics</span></a></li>' for n, c in Q["chapters"].items())
        quick = f'''
<section class="blk" id="{k}-quick" aria-labelledby="{k}-quick-h">
<div class="bh"><div><p class="kind">Quick notes</p><h3 id="{k}-quick-h">Recall the essentials</h3></div>
<a class="open" href="{href(qh)}">Open quick notes</a></div>
<p class="basis">{E(Q["basis"])} Updated {fmt_date(modified(qh))}.</p>
<div class="kpis"><div><b>{len(Q["chapters"])}</b><span>chapters</span></div>
<div><b>{sum(c["topics"] for c in Q["chapters"].values())}</b><span>short topics</span></div>
<div><b>{Q["metadata"].get("priority_facts", 0)}</b><span>priority revision facts</span></div></div>
<ul class="qlist">{qrows}</ul><a href="{href(qh, "repeated")}">Open priority revision</a></section>'''
    return full, quick


def render_subject(sub, F, Q, P, files, exam_txt):
    k = sub["key"]
    book = F.get("metadata", {}).get("question_kind") == "book-pyq"
    qlabel = "past-paper MCQs" if book else "UPPSC MCQs"
    qshort = "past-paper" if book else "UPPSC"
    ch = F["chapters"]
    max_q = max(1, max(c["asked"] for c in ch.values()))
    rep_by_ch = Counter(r["ch"] for r in F["repeats"])
    top3 = sorted(sorted(ch, key=lambda n: -ch[n]["asked"])[:3])
    full_h = files["full"]

    # --- Full notes block
    rows = []
    for n, c in ch.items():
        pages = f'<small>PDF pp. {E(c["pages"])}</small>' if c.get("pages") else ""
        rows.append(f'<tr><td class="n">{n}</td><td class="cn"><a href="{href(full_h, f"c{n}")}">{E(c["title"])}</a>{pages}</td>'
                    f'<td class="num"><span class="mini"><span style="width:{100 * c["asked"] / max_q:.1f}%"></span></span>{c["asked"]}</td>'
                    f'<td class="num">{rep_by_ch.get(n, 0) or "—"}</td></tr>')
    top_rep, cut = top_with_ties(F["repeats"])
    rep_rows = "".join(
        f'<tr><td class="n">{i}</td><td><a href="{href(full_h, r["anchor"])}">{E(r["fact"])}</a><small>{E(r["papers"])}</small></td>'
        f'<td class="num"><b class="pill">×{r["count"]}</b></td><td class="chc">{"Ch " + str(r["ch"]) if r["ch"] else ""}</td></tr>'
        for i, r in enumerate(top_rep, 1))
    years = F["years"]
    recent_years = sorted(years)[-5:][::-1]
    latest = "".join(f'<li><a href="{href(full_h, F["latest_anchor"](y))}"><b>{y}</b><span>{years[y]} questions</span></a></li>' for y in recent_years)
    key_html = ""
    if F["after_years"]:
        key_html = (f'<div class="key"><span><i class="kb"></i>From the book</span><span><i class="kn"></i>{", ".join(map(str, F["after_years"]))}: '
                    f'added later, not from the book</span></div>')
    extras = ""
    if F["extras"]:
        extras = '<h4>Also in these notes</h4><div class="extras">' + "".join(
            f'<a class="ex" href="{href(full_h, a)}"><b>{v}</b><span class="et">{E(t)}</span><span>{E(d)}</span></a>' for t, v, d, a in F["extras"]) + "</div>"
    full_block = f"""
<section class="blk" id="{k}-full" aria-labelledby="{k}-full-h">
<div class="bh"><div><p class="kind">Full notes</p><h3 id="{k}-full-h">{E(os.path.basename(full_h))}</h3></div>
<a class="open" href="{href(full_h)}">Open full notes</a></div>
<p class="basis">{E(F["basis"])} Updated {fmt_date(modified(full_h))}.</p>
<div class="kpis"><div><b>{len(ch)}</b><span>chapters</span></div><div><b>{F["bank"]:,}</b><span>{qlabel} to practise</span></div>
<div><b>{len(F["repeats"])}</b><span>facts asked in 2+ papers</span></div><div><b>{min(years)}–{max(years)}</b><span>years of papers</span></div></div>
<h4>Chapters <span class="hi">(अध्याय)</span></h4>
<p class="lead">Chapters {top3[0]}, {top3[1]} and {top3[2]} carry the most {qshort} questions. Click a chapter to open it.</p>
<div class="tw"><table><thead><tr><th>#</th><th>Chapter</th><th class="num">{qlabel}</th><th class="num">Repeated facts</th></tr></thead><tbody>{"".join(rows)}</tbody></table></div>
<div class="two">
<div class="col"><h4>Most repeated facts <span class="hi">(बार-बार पूछे गए तथ्य)</span></h4>
<p class="lead">The {len(top_rep)} facts asked in {cut} or more UPPSC papers. Learn these first.</p>
<div class="tw"><table><thead><tr><th>#</th><th>Fact and papers</th><th class="num">Papers</th><th>Ch</th></tr></thead><tbody>{rep_rows}</tbody></table></div>
<a href="{href(full_h, "repeated" if F["layout"] == "views" else "dash-repeats")}">All {len(F["repeats"])} repeated facts →</a></div>
<div class="col"><h4>Questions by year <span class="hi">(वर्षवार प्रश्न)</span></h4>
<p class="lead">{qlabel} in the practice bank, by the year of the paper.</p>
<div class="chart">{year_svg(years, F["after_years"], f"{sub['name']}: {qlabel} per year")}</div>{key_html}
<h4>Latest papers</h4><ul class="latest">{latest}</ul></div>
</div>
{extras}
</section>"""

    # --- Quick notes block
    if Q:
        qh = files["quick"]
        qrows = "".join(
            f'<li><a href="{href(qh, f"c{n}")}"><span class="qn">{n}</span><span class="qt">{E(c["title"])}</span>'
            f'<span class="qm">{c["topics"]} topics · {c["asked"]} PYQs</span></a></li>' for n, c in Q["chapters"].items())
        quick_block = f"""
<section class="blk" id="{k}-quick" aria-labelledby="{k}-quick-h">
<div class="bh"><div><p class="kind">Quick notes</p><h3 id="{k}-quick-h">{E(os.path.basename(qh))}</h3></div>
<a class="open" href="{href(qh)}">Open quick notes</a></div>
<p class="basis">{E(Q["basis"])} These counts are the quick notes’ own tagging of the book’s questions, so they differ a little from the full notes’ practice bank. Updated {fmt_date(modified(qh))}.</p>
<div class="kpis"><div><b>{sum(c["topics"] for c in Q["chapters"].values())}</b><span>short topics</span></div>
<div><b>{sum(c["asked"] for c in Q["chapters"].values())}</b><span>UPPSC PYQs tagged</span></div><div><b>{Q["repeats"]}</b><span>repeated facts</span></div></div>
<ul class="qlist">{qrows}</ul>
<a href="{href(qh, "repeated")}">Start with the facts UPPSC repeats →</a>
</section>"""
    else:
        quick_block = f"""
<section class="blk empty" id="{k}-quick" aria-labelledby="{k}-quick-h">
<div class="bh"><div><p class="kind">Quick notes</p><h3 id="{k}-quick-h">Not made yet</h3></div></div>
<p class="basis">There is no quick-notes file in <b>{E(sub["folder"])}</b> yet. When one is added (a file whose name ends in <code>quick-notes.html</code>), run the script again and it will appear here.</p>
</section>"""

    if F.get("source_practice"):
        full_block, quick_block = render_source_practice(sub, F, Q, files)

    # --- 72-hour plan block
    ph = files["h72"]
    phase_rows = "".join(
        f'<li data-a="{v[0][0]}" data-b="{v[-1][0]}"><div class="pn"><b>{E(p)}</b><span>Hours {v[0][0]}–{v[-1][0]}</span></div>'
        f'<div class="pt"><span></span></div><span class="pc">0 of {len(v)} done</span><a class="pl" href="{href(ph, f"h{v[0][0]}")}">Open hour {v[0][0]}</a></li>'
        for p, v in P["phases"].items())
    ch_h = chapter_hours(ch, P, os.path.basename(ph))
    hour_rows = "".join(
        f'<li><span class="qt">{E(c["title"])}</span>' + (
            f'<a href="{href(ph, f"h{ch_h[n][0]}")}">{"Hour " + str(ch_h[n][0]) if len(ch_h[n]) == 1 else "Hours " + str(ch_h[n][0]) + "–" + str(ch_h[n][-1])}</a>'
            if ch_h[n] else "") + "</li>"
        for n, c in ch.items())
    plan_block = f"""
<section class="blk" id="{k}-plan" aria-labelledby="{k}-plan-h" data-key="{E(P["key"])}">
<div class="bh"><div><p class="kind">72-hour plan</p><h3 id="{k}-plan-h">{E(os.path.basename(ph))}</h3></div>
<a class="open" href="{href(ph)}">Open the plan</a></div>
<p class="basis">72 one-hour sessions before {exam_txt}. Updated {fmt_date(modified(ph))}. <span class="prog">Progress shows here after you tick hours in the plan (Chrome and Edge share this between local files; Firefox may not).</span></p>
<ol class="plan">{phase_rows}</ol>
<details><summary>Where each chapter is in the plan</summary><ul class="hlist">{hour_rows}</ul></details>
</section>"""

    return f"""
<section class="subject" id="{k}" aria-labelledby="{k}-h">
<h2 id="{k}-h">{E(sub["name"])} <span class="hi">({E(sub["hindi"])})</span></h2>
<nav class="jump" aria-label="{E(sub["name"])} sections"><a href="#{k}-full">Full notes</a><a href="#{k}-quick">Quick notes{"" if Q else " (not yet)"}</a><a href="#{k}-plan">72-hour plan</a></nav>
{full_block}{quick_block}{plan_block}
</section>"""


def overview_card(sub, F, Q, P):
    k = sub["key"]
    bank_label = "source practice questions" if F.get("source_practice") else "MCQs"
    revision_count = F["metadata"].get("priority_facts", 0) if F.get("source_practice") else len(F["repeats"])
    revision_label = "priority facts" if F.get("source_practice") else "repeated facts"
    return (f'<a class="sc" href="#{k}" data-tab="{k}" data-key="{E(P["key"])}"><span class="sn">{E(sub["name"])}</span>'
            f'<span class="sh">{E(sub["hindi"])}</span>'
            f'<span class="sm"><b>{len(F["chapters"])}</b> chapters · <b>{F["bank"]:,}</b> {bank_label} · <b>{revision_count}</b> {revision_label}</span>'
            f'<span class="sf"><i class="on">Full</i><i class="{"on" if Q else "off"}">Quick</i><i class="on">72h</i></span>'
            f'<span class="sp"><span class="pt"><span></span></span><span class="spt">0 of 72 hours</span></span></a>')


# ------------------------------------------------------------------ page
CSS = r"""
:root{--bg:#ffffff;--ink:#16202e;--soft:#4b5566;--line:#e3e7ee;--wash:#f4f6fa;--accent:#1f5f8b;--up:#b8462e;--up-wash:#fbeae5;--ok:#2e7d4f;
--body:"Atkinson Hyperlegible Next","Atkinson Hyperlegible",system-ui,"Segoe UI",Arial,sans-serif;--head:"Lexend",system-ui,"Segoe UI",Arial,sans-serif;color-scheme:light}
*{box-sizing:border-box}
html{-webkit-text-size-adjust:100%;scroll-padding-top:70px}
body{margin:0;background:var(--bg);color:var(--ink);font-family:var(--body);font-size:16px;line-height:1.55}
a{color:var(--accent);text-underline-offset:2px}
a:focus-visible,summary:focus-visible{outline:2px solid var(--accent);outline-offset:2px}
.wrap{max-width:1120px;margin:0 auto;padding-block:24px 60px;padding-left:max(16px,env(safe-area-inset-left,0px));padding-right:max(16px,env(safe-area-inset-right,0px));display:grid;gap:24px}
h1,h2,h3,h4{font-family:var(--head);font-weight:600;line-height:1.2;margin:0;text-wrap:balance}
h1{font-size:28px}
h2{font-size:24px}
h3{font-size:17px;word-break:break-word}
h4{font-size:16px;margin-top:6px}
.hi{font-family:var(--body);font-weight:400;color:var(--soft);font-size:.8em}
.top{display:flex;flex-wrap:wrap;align-items:flex-end;justify-content:space-between;gap:12px 24px;border-bottom:2px solid var(--ink);padding-bottom:14px}
.top p{margin:6px 0 0;color:var(--soft);max-width:64ch}
.exam{font-family:var(--head);font-size:15px;border:1.5px solid var(--up);color:var(--up);background:var(--up-wash);border-radius:999px;padding:6px 14px;white-space:nowrap}
.exam b{font-size:20px}
.cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(250px,1fr));gap:14px}
.sc{display:grid;gap:6px;border:1.5px solid var(--line);border-radius:10px;padding:14px 16px;text-decoration:none;color:var(--ink);background:var(--bg)}
.sc:hover{background:var(--wash)}
.sc.cur{border-color:var(--accent);box-shadow:inset 0 3px 0 var(--accent)}
.sn{font-family:var(--head);font-weight:600;font-size:19px;color:var(--accent)}
.sh{color:var(--soft);font-size:14px}
.sm{font-size:14px;color:var(--soft)}
.sm b{color:var(--ink)}
.sf{display:flex;gap:6px}
.sf i{font-style:normal;font-size:12px;font-weight:700;border-radius:4px;padding:1px 7px;border:1px solid}
.sf i.on{color:var(--ok);border-color:var(--ok)}
.sf i.off{color:var(--soft);border-color:var(--line);text-decoration:line-through}
.sp{display:grid;grid-template-columns:1fr auto;gap:8px;align-items:center;font-size:13px;color:var(--soft)}
.pt{height:9px;background:var(--wash);border-radius:5px;overflow:hidden}
.pt>span{display:block;height:100%;width:0;background:var(--ok)}
.subject{display:grid;gap:18px;scroll-margin-top:16px}
.js .subject{display:none}
.js .subject.cur{display:grid}
.jump{display:flex;flex-wrap:wrap;gap:8px}
.jump a{font-size:14px;border:1.5px solid var(--line);border-radius:999px;padding:4px 12px;text-decoration:none}
.jump a:hover{background:var(--wash)}
.blk{border:1.5px solid var(--line);border-radius:12px;padding:18px;display:grid;gap:14px;min-width:0}
.blk.empty{background:var(--wash)}
.bh{display:flex;flex-wrap:wrap;justify-content:space-between;align-items:center;gap:10px}
.kind{margin:0 0 2px;font-size:12.5px;font-weight:700;letter-spacing:.08em;text-transform:uppercase;color:var(--up)}
.open{font-family:var(--head);font-size:14px;background:var(--accent);color:#fff;text-decoration:none;border-radius:8px;padding:7px 14px}
.open:hover{background:#174a6d}
.basis{margin:0;color:var(--soft);font-size:14px;max-width:90ch}
.kpis{display:grid;grid-template-columns:repeat(auto-fit,minmax(140px,1fr));border:1px solid var(--line);border-radius:8px}
.kpis div{padding:10px 14px;border-right:1px solid var(--line);display:grid}
.kpis div:last-child{border-right:0}
.kpis b{font-family:var(--head);font-size:24px;font-weight:600;font-variant-numeric:tabular-nums}
.kpis span{font-size:13.5px;color:var(--soft)}
.lead{margin:0;color:var(--soft);font-size:14.5px}
.two{display:grid;grid-template-columns:minmax(0,1.15fr) minmax(0,.85fr);gap:24px;align-items:start}
.col{display:grid;gap:10px;min-width:0}
.tw{overflow-x:auto;border:1px solid var(--line);border-radius:8px;max-height:560px;overflow-y:auto}
table{border-collapse:collapse;width:100%;font-size:14.5px}
th{position:sticky;top:0;font-family:var(--head);font-weight:500;font-size:12.5px;text-align:left;color:var(--soft);background:var(--wash);padding:8px 10px;border-bottom:1px solid var(--line)}
td{padding:7px 10px;border-bottom:1px solid var(--line);vertical-align:top}
tr:last-child td{border-bottom:0}
td small{display:block;color:var(--soft);font-size:12.5px}
td.n{color:var(--soft);font-variant-numeric:tabular-nums;width:2.2em}
td.num,th.num{text-align:right;font-variant-numeric:tabular-nums;white-space:nowrap}
td.chc{white-space:nowrap;color:var(--soft)}
td.cn a{font-weight:700;text-decoration:none}
td.cn a:hover{text-decoration:underline}
.mini{display:inline-block;width:64px;height:8px;background:var(--wash);border-radius:4px;margin-right:8px;vertical-align:middle;overflow:hidden}
.mini span{display:block;height:100%;background:var(--up)}
.pill{display:inline-block;font-family:var(--head);font-weight:600;font-size:13.5px;color:var(--up);background:var(--up-wash);border-radius:999px;padding:0 9px}
.chart svg{width:100%;height:auto;display:block}
.chart .gl{stroke:var(--line);stroke-width:1}
.chart .base{stroke:var(--ink);stroke-width:1.2}
.chart .ax{fill:var(--soft);font:12px var(--body)}
.chart .bar{fill:var(--accent)}
.chart .bar.new{fill:var(--up)}
.key{display:flex;flex-wrap:wrap;gap:6px 16px;font-size:12.5px;color:var(--soft)}
.key i{display:inline-block;width:11px;height:11px;border-radius:2px;margin-right:5px;vertical-align:-1px}
.key .kb{background:var(--accent)}
.key .kn{background:var(--up)}
.latest{list-style:none;margin:0;padding:0;display:grid;grid-template-columns:repeat(auto-fit,minmax(96px,1fr));gap:8px}
.latest a{display:grid;border:1px solid var(--line);border-radius:8px;padding:6px 10px;text-decoration:none}
.latest a:hover{background:var(--wash)}
.latest b{font-family:var(--head);color:var(--ink)}
.latest span{font-size:12.5px;color:var(--soft)}
.extras{display:grid;grid-template-columns:repeat(auto-fit,minmax(170px,1fr));gap:10px}
.ex{display:grid;border:1px solid var(--line);border-radius:8px;padding:10px 12px;text-decoration:none;color:var(--ink)}
.ex:hover{background:var(--wash)}
.ex b{font-family:var(--head);font-size:22px}
.ex .et{font-weight:700;color:var(--accent)}
.ex span{font-size:13px;color:var(--soft)}
.qlist,.hlist{list-style:none;margin:0;padding:0;display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:6px 14px}
.qlist a{display:grid;grid-template-columns:2em 1fr;gap:0 6px;text-decoration:none;padding:6px 8px;border-radius:6px}
.qlist a:hover{background:var(--wash)}
.qn{color:var(--soft);font-variant-numeric:tabular-nums;grid-row:span 2}
.qt{font-weight:700;color:var(--ink)}
.qm{font-size:12.5px;color:var(--soft)}
.hlist li{display:flex;justify-content:space-between;gap:10px;border-bottom:1px dashed var(--line);padding:4px 0;font-size:14px}
.hlist .qt{font-weight:400}
.hlist a{white-space:nowrap}
.muted{color:var(--soft);font-size:13px;white-space:nowrap}
.plan{list-style:none;margin:0;padding:0;display:grid;gap:8px}
.plan li{display:grid;grid-template-columns:minmax(130px,1fr) minmax(80px,2fr) 7.5em auto;gap:6px 14px;align-items:center;border:1px solid var(--line);border-radius:8px;padding:9px 14px}
.pn b{display:block;font-family:var(--head);font-weight:600}
.pn span,.pc{font-size:13px;color:var(--soft);font-variant-numeric:tabular-nums}
.pl{font-size:14px;white-space:nowrap}
details summary{cursor:pointer;font-weight:700;color:var(--accent)}
details[open] summary{margin-bottom:8px}
code{font-size:.92em;background:var(--wash);padding:0 4px;border-radius:3px}
.spn{display:flex;justify-content:space-between;gap:10px;border-top:1.5px solid var(--line);padding-top:12px}
.spn a{font-family:var(--head);font-weight:600;text-decoration:none}
.spn a:hover{text-decoration:underline}
.others{display:grid;gap:10px}
.olist{list-style:none;margin:0;padding:0;display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:8px}
.olist li{border:1px solid var(--line);border-radius:8px;padding:8px 12px;display:grid}
.olist a{font-weight:700;text-decoration:none}
.olist small{color:var(--soft);font-size:12.5px}
.foot{font-size:13px;color:var(--soft);margin:0;border-top:1.5px solid var(--line);padding-top:14px}
@media (max-width:820px){.two{grid-template-columns:minmax(0,1fr)}
.kpis div{border-right:0;border-bottom:1px solid var(--line)}
.kpis div:last-child{border-bottom:0}}
@media (max-width:520px){h1{font-size:24px}.plan li{grid-template-columns:1fr}.qlist,.hlist{grid-template-columns:1fr}.blk{padding:14px}}
@media print{.js .subject{display:grid}.blk,.sc{break-inside:avoid}.tw{max-height:none;overflow:visible}}
"""

JS = r"""
(function(){
document.documentElement.classList.add("js");
var exam=new Date("__EXAM__T00:00:00"),now=new Date();now.setHours(0,0,0,0);
var d=Math.round((exam-now)/864e5),el=document.getElementById("days");
if(el)el.innerHTML=d>0?"<b>"+d+"</b> days to UPPCS Prelims · __EXAMTXT__":(d===0?"UPPCS Prelims is today":"UPPCS Prelims was on __EXAMTXT__");
function done(key){var a=[];try{a=JSON.parse(localStorage.getItem(key)||"[]")}catch(e){a=[]}return Array.isArray(a)?a:[]}
document.querySelectorAll(".sc").forEach(function(c){var n=done(c.dataset.key).length;c.querySelector(".pt>span").style.width=(100*n/72)+"%";c.querySelector(".spt").textContent=n+" of 72 hours"});
document.querySelectorAll("section[data-key]").forEach(function(s){var a=done(s.dataset.key);
 if(a.length)s.querySelector(".prog").textContent=a.length+" of 72 hours ticked.";
 s.querySelectorAll(".plan li").forEach(function(li){var x=+li.dataset.a,y=+li.dataset.b,n=0;a.forEach(function(h){if(h>=x&&h<=y)n++});
  li.querySelector(".pt>span").style.width=(100*n/(y-x+1))+"%";li.querySelector(".pc").textContent=n+" of "+(y-x+1)+" done";
  var l=li.querySelector(".pl"),nx=x;while(a.indexOf(nx)>=0&&nx<y)nx++;
  if(n===y-x+1)l.textContent="Phase done ✓";else{l.setAttribute("href",l.getAttribute("href").replace(/#h\d+$/,"#h"+nx));l.textContent=(n?"Continue at hour ":"Open hour ")+nx}})});
var subs=[].slice.call(document.querySelectorAll(".subject")),keys=subs.map(function(s){return s.id});
function show(){var h=location.hash.slice(1),t=null;
 subs.forEach(function(s){if(s.id===h||(h&&h.indexOf(s.id+"-")===0))t=s.id});
 if(!t){try{t=localStorage.getItem("dash-tab")}catch(e){}}
 if(keys.indexOf(t)<0)t=keys[0];
 subs.forEach(function(s){s.classList.toggle("cur",s.id===t)});
 document.querySelectorAll(".sc").forEach(function(c){var on=c.dataset.tab===t;c.classList.toggle("cur",on);if(on)c.setAttribute("aria-current","true");else c.removeAttribute("aria-current")});
 try{localStorage.setItem("dash-tab",t)}catch(e){}
 if(h&&h!==t){var x=document.getElementById(h);if(x)x.scrollIntoView()}}
window.addEventListener("hashchange",show);show();
})();
"""


def fonts_css():
    for sub in SUBJECTS:
        for path in sorted(glob.glob(os.path.join(ROOT, sub["folder"], "*.html"))):
            s = open(path, encoding="utf-8").read()
            faces = re.findall(r"@font-face\{.*?\}", s, re.S)
            fams = {re.search(r"font-family:\s*\"?([^\";]+)", f).group(1) for f in faces}
            if {"Atkinson Hyperlegible Next", "Lexend"} <= fams:
                return "\n".join(faces)
    print("Warning: no file embeds both Atkinson Hyperlegible Next and Lexend; using fallback fonts.")
    return ""


def build():
    blocks, cards, exams, inputs = [], [], set(), []
    for sub in SUBJECTS:
        folder = sub["folder"]
        if not os.path.isdir(os.path.join(ROOT, folder)):
            fail(f"folder not found: {folder}")
        files = {
            "full": find_one(folder, ["*-uppsc-notes.html", "*-full-notes.html"]),
            "quick": find_one(folder, ["*quick-notes.html"], required=False),
            "h72": find_one(folder, ["*-in-72h.html"]),
        }
        # a quick-notes file must not be mistaken for the full notes
        if files["quick"] and files["quick"] == files["full"]:
            fail(f"{folder}: the same file matched full and quick notes")
        F = parse_full(files["full"])
        Q = parse_quick(files["quick"]) if files["quick"] else None
        if Q and [norm(c["title"]) for c in Q["chapters"].values()] != [norm(c["title"]) for c in F["chapters"].values()]:
            if len(Q["chapters"]) != len(F["chapters"]):
                fail(f"{folder}: quick notes have {len(Q['chapters'])} chapters, full notes {len(F['chapters'])}")
        P = parse_72h(files["h72"])
        exams.add(P["exam"])
        inputs += [p for p in files.values() if p]
        cards.append(overview_card(sub, F, Q, P))
        blocks.append((sub, F, Q, P, files))
        print(f"{sub['name']}: {len(F['chapters'])} chapters, {F['bank']} MCQs, {len(F['repeats'])} repeated, "
              f"quick={'yes' if Q else 'no'}, 72h key {P['key']}")
    if len(exams) != 1:
        fail(f"the 72-hour plans give different exam dates: {sorted(exams)}")
    exam = exams.pop()
    exam_txt = f"{exam.day} {exam:%B %Y}"
    built = max(modified(p) for p in inputs)
    rendered = [render_subject(sub, F, Q, P, files, exam_txt) for sub, F, Q, P, files in blocks]
    names = [(b[0]["key"], b[0]["name"]) for b in blocks]
    for i, part in enumerate(rendered):
        prev = f'<a href="#{names[i - 1][0]}">← {E(names[i - 1][1])}</a>' if i > 0 else "<span></span>"
        nxt = f'<a class="nx" href="#{names[i + 1][0]}">{E(names[i + 1][1])} →</a>' if i < len(names) - 1 else '<a class="nx" href="#others">Other notes →</a>'
        k = part.rindex("</section>")
        rendered[i] = part[:k] + f'<nav class="spn" aria-label="Previous and next subject">{prev}{nxt}</nav>\n' + part[k:]
    panels = "".join(rendered)
    import sitenav
    archive = sitenav.site_map()["archive"]
    others = ""
    if archive:
        others = ('<section class="others" id="others" aria-labelledby="others-h"><h2 id="others-h">Other notes <span class="hi">(अन्य नोट्स)</span></h2>'
                  '<p class="lead">Older or general notes kept in the project. They open with the same menu and breadcrumbs.</p><ul class="olist">'
                  + "".join(f'<li><a href="{E(sitenav.enc(a["path"]))}">{E(a["t"])}</a><small>{E(a["dir"])}</small></li>' for a in archive)
                  + "</ul></section>")
    js = JS.replace("__EXAM__", exam.isoformat()).replace("__EXAMTXT__", f"{exam.day} {exam:%b %Y}")
    page = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>UPPSC Study Dashboard</title>
<meta name="description" content="Environment, Polity and Economy notes for UPPSC in one place: full notes, quick notes and 72-hour plans, each shown separately.">
<style>
{fonts_css()}
{CSS.strip()}
</style>
</head>
<body>
<main class="wrap">
<header class="top">
<div><h1>UPPSC Study Dashboard <span class="hi">(अध्ययन डैशबोर्ड)</span></h1>
<p>Pick a subject. Each one keeps its full notes, quick notes and 72-hour plan separate, with links straight into the right chapter.</p></div>
<div class="exam" id="days">UPPCS Prelims · {exam_txt}</div>
</header>
<nav class="cards" aria-label="Subjects">{"".join(cards)}</nav>
{panels}
{others}
<p class="foot">Built from files dated up to {fmt_date(built)} by <b>dashboard-src/build_dashboard.py</b>. It reads only the notes and plan HTML files, never the PDFs. Run it again after any notes file changes. Counts come from each file’s own practice bank, so they cover different years for each subject.</p>
</main>
<script>{js.strip()}</script>
</body>
</html>
"""
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(page)
    print(f"Wrote {OUT} ({len(page):,} chars)")


def main():
    import sitenav
    sitenav.inject_all(only=None)   # every notes page (the dashboard is rebuilt next)
    build()
    sitenav.inject_all(only={"study-dashboard.html"})
    import security
    security.write_vercel_json()   # CSP script hashes must match the pages just written


if __name__ == "__main__":
    main()
