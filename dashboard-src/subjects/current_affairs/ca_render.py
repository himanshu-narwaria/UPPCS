"""Step 3: build the three Current Affairs pages.

Inputs : ca_source.json (step 1), ca_units.json (step 2), memory/*.part*.json (writer agents),
         ca_styles.css, ca_runtime.js, fonts_embedded.css
Outputs: Drishti-current affairs/current-uppsc-full-notes.html
         Drishti-current affairs/current-uppsc-quick-notes.html
         Drishti-current affairs/current-in-72h.html
Run:  python ca_render.py            (fails if any unit lacks its memory entry)
      python ca_render.py --draft    (renders with gaps, for previewing)
"""
import hashlib
import html
import json
import random
import re
import sys
from collections import Counter, OrderedDict, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OUT = ROOT / "Drishti-current affairs"
FULL, QUICK, PLAN = "current-uppsc-full-notes.html", "current-uppsc-quick-notes.html", "current-in-72h.html"
E = html.escape
EXAM = "6 December 2026"
ISSUE = "Drishti Current Affairs 2026 (2)"
CONTEXT = (f"Everything here comes from the supplied {ISSUE} PDF (241 pages). Dates, ranks and figures are as that "
           "issue printed them; this is not a live news feed. Page references are PDF file pages. Practice questions "
           "are built from the issue's own facts: they are not UPPSC previous-year questions.")
LEARN_HOURS, REVISE_HOURS, TEST_HOURS = 54, 12, 6
WEIGHT = {1: 2.6, 7: 1.5, 8: 0.5}          # Q&A bank is dense and exam-like; UP counts more; Bihar less (optional)
REVIEW_GAPS = (1, 3, 7, 15, 30)            # spaced review: hours back


# ------------------------------------------------------------------ data
def load(draft):
    src = json.loads((HERE / "ca_source.json").read_text(encoding="utf-8"))
    units = json.loads((HERE / "ca_units.json").read_text(encoding="utf-8"))
    memory = {}
    for p in sorted((HERE / "memory").glob("*.part*.json")):
        memory.update(json.loads(p.read_text(encoding="utf-8")))
    missing = [u["id"] for u in units if u["id"] not in memory]
    if missing and not draft:
        raise SystemExit(f"{len(missing)} units have no memory entry (e.g. {missing[:8]}); run the writers or use --draft")
    return src, units, memory


def seed(*parts):
    return int(hashlib.md5("|".join(parts).encode()).hexdigest()[:8], 16)


# ------------------------------------------------------------------ MCQs from the book's own Q&A answers
ADJ = r"(?:[a-z-]+ ){0,2}"      # "which aerospace company", "which Union minister"
QCLASS = [
    ("theme", r"\b(theme|slogan|motto|tagline|mascot)\b"),
    ("sport", r"\bwhich sport\b|\bwhich game\b"),
    ("when", r"^when\b|^until when|\b(which|what) (year|date|month|day)\b"),
    ("num", r"^how (many|much|long)\b|\b(rank|percentage|per cent|value|outlay|amount|number|share|cost|size|"
            r"length|distance|capacity|score|position)\b"),
    ("place", rf"^where\b|\bwhich {ADJ}(city|cities|state|states|country|countries|district|place|venue|port|location|"
              rf"town|village|island|region|nation|union territory|ut|continent|river|lake|mountain|airport)\b"),
    ("org", rf"\bwhich {ADJ}(organisation|organization|agency|ministry|company|institute|institution|bank|body|"
            rf"department|university|committee|commission|firm|startup|think tank|council|board|party|"
            rf"team|club|group|corporation|authority|force|regiment|navy|army)\b"),
    ("who", rf"^(who|whom|whose)\b|\bwhich {ADJ}(minister|person|leader|official|officer|actor|actress|athlete|"
            rf"player|cricketer|author|writer|poet|scientist|economist|journalist|singer|judge|justice|president|"
            rf"governor|ceo|chairman|chairperson|captain|coach|boxer|wrestler|shooter|grandmaster|filmmaker|"
            rf"director|astronaut|personality|woman|man|chess player|footballer|archer|lawyer|diplomat|artist)\b"),
]
MONTHS = r"(january|february|march|april|may|june|july|august|september|october|november|december)"


def qclass(q):
    s = q.lower()
    if re.search(r"\bwho (?:will |would |is to )?host", s):     # a host is a place
        return "place"
    for name, pat in QCLASS:
        if re.search(pat, s):
            return name
    return "other"


def qnoun(q):
    """The thing asked for: "Which mission…" -> mission, "What was the theme…" -> theme."""
    m = re.search(r"\b(?:which|what) (?:is |was |are |were |will be |has been )?(?:the )?"
                  r"(?:new |first |major |main |indian |international |union |official |current )*([a-z-]+)", q.lower())
    return m.group(1) if m and m.group(1) not in ("is", "was", "are", "were", "the", "did", "does", "do", "has") else ""


SPORTS = ["Cricket", "Hockey", "Football", "Badminton", "Tennis", "Kabaddi", "Wrestling", "Boxing", "Athletics",
          "Shooting", "Chess", "Archery", "Table Tennis", "Weightlifting"]


def bare(a):
    """Option text without a leading "At/In/On/The/Its", so no option stands out by its first word."""
    a = re.sub(r"^(?:(?:at|in|on|the|its)\s+)+(?=\S)", "", a, flags=re.I)
    return a[:1].upper() + a[1:]


ORDINALS = r"(first|second|third|fourth|fifth|sixth|seventh|eighth|ninth|tenth|\d+(st|nd|rd|th))"
ORG_END = r"\b(inc|ltd|limited|corporation|corp|company|holdings|group|bank|llp|plc|foundation|trust)\.?$"


APPROX = r"(?:about |around |approximately |approx\.? |over |more than |nearly |almost |up to |below |above |" \
         r"less than |only |rank |the |a total of |total )?"
UNIT = r"(crore|lakh|million|billion|km|kilomet\w*|metres?|kg|tonnes?|mw|gw|years?|days?|months?|medals?|hectares?|" \
       r"countries|nations|states|districts|members|teams|athletes|sites)"


def shape(a):
    """What kind of thing an answer is; wrong options must be the same kind, or they give the answer away."""
    s = a.lower().strip()
    if s[:1] in "“‘\"'":
        return "quote"
    if re.search(MONTHS, s) and re.search(r"\d", s) and len(s) < 45:
        return "date"
    if re.fullmatch(r"(in |by |from |since |until )?(19|20)\d\d", s):
        return "year"
    if re.search(ORG_END, s):
        return "org"
    if re.match(APPROX + r"(₹|rs\.? ?|us\$|\$)", s) or re.match(APPROX + r"[\d,.]+ ?(crore|lakh|million|billion)? ?(rupees|dollars?|usd|euros?)", s):
        return "money"
    if re.match(APPROX + r"[\d,.]+ ?(%|per ?cent)", s):
        return "pct"
    if re.fullmatch(rf"(the )?{ORDINALS}( \w+)?", s):
        return "ordinal"
    if re.match(APPROX + r"(one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|thirteen|fourteen|"
                r"fifteen|twenty|thirty|forty|fifty|hundred|thousand)\b", s):
        return "num:"
    m = re.match(APPROX + r"[\d,.]+ ?" + UNIT + "?", s)
    if m:
        return "num:" + (m.group(1) or "")
    if len(a.split()) <= 5:
        return "name" if a[:1].isupper() else "words"
    return "long"


def family(sh):
    if sh.startswith("num:") or sh in ("money", "pct", "ordinal"):
        return "qty"
    return {"date": "time", "year": "time", "org": "entity", "name": "entity", "words": "entity"}.get(sh, "text")


TITLE_WORDS = {"the", "of", "and", "for", "in", "on", "at", "a", "an", "pm", "prime", "minister", "president",
               "chief", "union", "dr", "shri", "smt", "mr", "ms", "air", "marshal", "general", "vice", "deputy",
               "secretary", "chairman", "ministry", "department", "government", "india", "indian", "national",
               "(", ")", "&"}


def core(a):
    """Content words of an answer plus the acronym of its capitalised words, for spotting two
    options that name the same thing ("PM Narendra Modi" / "Prime Minister Narendra Modi",
    "DRDO" / "Defence Research and Development Organisation")."""
    words = re.findall(r"[a-z0-9]+", a.lower())
    toks = {w for w in words if w not in TITLE_WORDS}
    caps = [w[0] for w in re.findall(r"\b[A-Z][A-Za-z]+", a) if w.lower() not in ("and", "of", "the", "for")]
    acr = "".join(caps).lower() if len(caps) >= 3 else ""
    return toks, acr


def same_thing(a, b):
    (ta, aa), (tb, ab) = core(a), core(b)
    if not ta or not tb:
        return False
    if (aa and aa in tb) or (ab and ab in ta):
        return True
    small, big = sorted((ta, tb), key=len)
    return len(small & big) / len(small) >= 0.6


def head_word(a):
    """Last capitalised word: 'Digital Agriculture Mission' -> 'mission', 'Fairfax Financial Holdings' -> 'holdings'."""
    caps = re.findall(r"\b[A-Z][A-Za-z-]+", a)
    return caps[-1].lower() if caps else ""


def lead_word(a):
    w = a.split()[0].lower() if a.split() else ""
    return w if w in {"to", "by", "for", "in", "it", "the", "a", "an", "under", "through", "with"} else ""


def clean_answer(a):
    a = a.strip()
    if re.search(r"\b(Inc|Ltd|Co|Corp|Jr|Sr|St|etc|U\.S\.A|U\.K|Dr|No)\.$", a):
        return a
    return a.rstrip(".").strip()


def norm_ans(a):
    return re.sub(r"[^a-z0-9]", "", a.lower())


def qa_mcqs(src):
    qa = src["qa"]
    feats = [(q, qclass(q["q"]), qnoun(q["q"]), shape(q["a"]), bare(clean_answer(q["a"]))) for q in qa]
    extra = {q["id"]: (head_word(clean_answer(q["a"])), lead_word(q["a"])) for q in qa}
    out = {}
    for q, qc, qn, sh, ans in feats:
        na = norm_ans(ans)
        hw, lw = extra[q["id"]]
        cands = []
        for q2, qc2, qn2, sh2, ans2 in feats:
            n2 = norm_ans(ans2)
            if q2["story"] == q["story"] or not n2 or n2 == na or n2 in na or na in n2:
                continue
            hw2, lw2 = extra[q2["id"]]
            # what the question asks for decides first (a city for a city, a minister for a
            # minister), then the answer's form (a date for a date, ₹ for ₹)
            score = (100 if qc == qc2 and qc != "other" else 0) + (100 if qn and qn == qn2 else 0) \
                + (60 if sh == sh2 else 30 if family(sh) == family(sh2) else 0) \
                + (3 if hw and hw == hw2 else 0) + (2 if lw and lw == lw2 else 0) \
                + (1 if q["category"] == q2["category"] else 0) - abs(len(ans) - len(ans2)) / 40
            cands.append((-score, seed(q["id"], q2["id"]), ans2, n2))
        if qc == "sport":    # only two questions ask for a sport: use real sport names
            cands = [(-1000, seed(q["id"], sp), sp, norm_ans(sp)) for sp in SPORTS] + cands
        cands.sort()
        picked, seen = [], {na}
        for _, _, ans2, n2 in cands:
            if n2 in seen or any(n2 in s or s in n2 for s in seen):
                continue
            if same_thing(ans2, ans) or any(same_thing(ans2, p) for p in picked):
                continue
            picked.append(ans2)
            seen.add(n2)
            if len(picked) == 3:
                break
        opts = picked + [ans]
        random.Random(seed("opt", q["id"])).shuffle(opts)
        out[q["id"]] = {"o": opts, "k": [opts.index(ans)]}
    return out


# ------------------------------------------------------------------ html helpers
def runs_html(runs):
    return "".join(f'<b class="k">{E(t)}</b>' if b and t.strip() else E(t) for t, b in runs)


def table_html(b):
    rows = []
    for row in b["rows"]:
        cells = "".join(f'<td{f" colspan={span}" if span > 1 else ""}{f" rowspan={rs[0]}" if rs else ""}>{runs_html(c)}</td>' for c, span, *rs in row)
        rows.append(f"<tr class=\"pt\">{cells}</tr>")
    note = ('<p class="vnote">Shown line by line as printed: in the PDF this table\'s text and borders do not line up, '
            'so read each line across.</p>') if b.get("as_printed") else ""
    return '<div class="table-scroll"><table>' + "".join(rows) + "</table></div>" + note


def blocks_html(blocks):
    out, stack = [], []          # one entry per open <ul>: is an <li> open in it?

    def close_to(depth):
        while len(stack) > depth:
            if stack[-1]:
                out.append("</li>")
            out.append("</ul>")
            stack.pop()

    for b in blocks:
        if b["kind"] == "li":
            want = 1 if b.get("level", 1) == 1 else 2
            close_to(want)
            while len(stack) < want:
                if stack and not stack[-1]:          # a sub-list needs a parent item to sit in
                    out.append('<li class="nb">')
                    stack[-1] = True
                out.append("<ul>")
                stack.append(False)
            if stack[-1]:
                out.append("</li>")
            out.append(f'<li class="pt">{runs_html(b["runs"])}')
            stack[-1] = True
            continue
        close_to(0)
        if b["kind"] == "table":
            out.append(table_html(b))
        elif b["kind"] == "heading":
            out.append(f'<h4 class="pt">{runs_html(b["runs"])}</h4>')
        else:
            cls = "pt box" if b.get("box") else "pt"
            out.append(f'<p class="{cls}">{runs_html(b["runs"])}</p>')
    close_to(0)
    return "".join(out)


def pages_label(pages):
    pages = sorted(set(pages))
    if len(pages) == 1:
        return f"PDF p. {pages[0]}"
    return f"PDF pp. {pages[0]}–{pages[-1]}"


def mem_html(m, story=False):
    if not m:
        return ""
    parts = []
    if story and m.get("line"):
        parts.append(f'<p class="line"><b>Remember:</b> {E(m["line"])}</p>')
    if not story and m.get("facts"):
        parts.append("<ul>" + "".join(f'<li class="pt">{E(f)}</li>' for f in m["facts"]) + "</ul>")
    if m.get("hook"):
        parts.append(f'<p class="hook"><b>Memory aid</b> {E(m["hook"])}</p>')
    if m.get("trap"):
        parts.append(f'<p class="trap"><b>Don\'t confuse</b> {E(m["trap"])}</p>')
    if m.get("check"):
        parts.append(f'<p class="check"><b>Check</b> {E(m["check"])}</p>')
    if m.get("hindi"):
        parts.append(f'<p class="hi">हिंदी: {E(" · ".join(m["hindi"]))}</p>')
    if not parts:
        return ""
    if story:
        return '<div class="mem story">' + "".join(parts) + "</div>"
    return '<div class="mem">' + "".join(parts) + "</div>"


# ------------------------------------------------------------------ model: chapters, topics, questions
class Model:
    def __init__(self, src, units, memory):
        self.src, self.units, self.mem = src, units, memory
        self.qa = {q["id"]: q for q in src["qa"]}
        self.arts = {a["id"]: a for a in src["articles"]}
        self.chapters = src["chapters"]
        self.by_ch = OrderedDict((c["num"], [u for u in units if u["ch"] == c["num"]]) for c in self.chapters)
        self.anchor = {}
        for n, us in self.by_ch.items():
            for k, u in enumerate(us, 1):
                self.anchor[u["id"]] = f"c{n}-t{k}"
        self.build_questions()

    def m(self, u):
        return self.mem.get(u["id"], {})

    def priority(self, u):
        return self.m(u).get("priority", 2)

    def build_questions(self):
        self.q = OrderedDict()
        self.unit_q = defaultdict(list)
        mcq = qa_mcqs(self.src)
        n = 0
        for u in self.units:
            if u["kind"] == "story":
                prev = None
                for qid in u["qa"]:
                    q = self.qa[qid]
                    n += 1
                    pid = f"p{n:04d}"
                    ctx = f" · follows: {prev['q']}" if prev else ""
                    prev = q
                    self.q[pid] = {"e": f"Points to Remember · {q['category']}{ctx}",
                                   "s": q["q"] + (f" ({q['date']})" if q["date"] else ""),
                                   "o": mcq[qid]["o"], "k": mcq[qid]["k"],
                                   "f": f"Answer: {clean_answer(q['a'])}. (PDF p. {q['page']})",
                                   "h": f"c1-{qid}", "ch": "c1", "y": 2026, "kind": "source-practice",
                                   "p": self.priority(u), "u": u["id"]}
                    self.unit_q[u["id"]].append(pid)
            else:
                for m in self.m(u).get("mcq", []):
                    n += 1
                    pid = f"p{n:04d}"
                    self.q[pid] = {"e": f"Ch {u['ch']} · {u['title']}", "s": m["q"], "o": m["o"], "k": [m["k"]],
                                   "f": f"{m.get('why', '').strip()} ({pages_label(u['pages'])})".strip(),
                                   "h": self.anchor[u["id"]], "ch": f"c{u['ch']}", "y": 2026,
                                   "kind": "source-practice", "p": self.priority(u), "u": u["id"]}
                    self.unit_q[u["id"]].append(pid)
        self.ch_count = Counter(q["ch"] for q in self.q.values())

    def priority_units(self):
        return [u for u in self.units if self.priority(u) == 1]

    def bold_count(self):
        n = 0
        for a in self.src["articles"]:
            for b in a["blocks"]:
                if b["kind"] == "table":
                    n += sum(1 for row in b["rows"] for c, *_ in row for _, bb in c if bb)
                else:
                    n += sum(1 for t, bb in b["runs"] if bb and t.strip())
        return n

    def meta(self):
        return {"question_kind": "source-practice", "practice_questions": len(self.q), "verified_uppsc_pyqs": 0,
                "verified_repeated_facts": 0, "priority_facts": len(self.priority_units()), "source_pdf_pages": 241,
                "source_qa_items": len(self.qa), "study_units": len(self.units), "bold_key_facts": self.bold_count(),
                "chapter_practice_counts": {f"c{c['num']}": self.ch_count.get(f"c{c['num']}", 0) for c in self.chapters},
                "context": f"{ISSUE}; built from the PDF by font (questions light, answers bold); no live updates"}


# ------------------------------------------------------------------ page parts
def assets():
    css = (HERE / "fonts_embedded.css").read_text(encoding="utf-8") + "\n" + (HERE / "ca_styles.css").read_text(encoding="utf-8")
    js = (HERE / "ca_runtime.js").read_text(encoding="utf-8")
    return css, js


def head(title, desc, mode):
    css, _ = assets()
    if mode == "plan":
        tools = '<span class="prog" id="prog">0 of 72 hours done</span>'
    else:
        tools = ('<input id="q" type="search" placeholder="Search a name, place, scheme…" aria-label="Search notes" autocomplete="off">'
                 '<label class="tog"><input id="test" type="checkbox"> Test mode</label>')
    return (f'<!DOCTYPE html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n'
            f'<meta name="viewport" content="width=device-width, initial-scale=1">\n<title>{E(title)}</title>\n'
            f'<meta name="description" content="{E(desc)}">\n<style>\n{css}\n</style>\n</head>\n<body data-mode="{mode}">\n'
            f'<header class="top"><button id="menu" type="button" aria-label="Open contents" aria-expanded="false" aria-controls="side">☰</button>'
            f'<a class="brand" href="#home">Current Affairs · UPPCS</a>{tools}</header>\n'
            + ('<div class="progress-track"><i id="bar"></i></div>\n' if mode == "plan" else "")
            + '<div class="wrap">\n')


def tail(model, with_q):
    _, js = assets()
    out = ['</main></div><div id="scrim"></div>',
           '<script id="study-meta" type="application/json">' + json.dumps(model.meta(), ensure_ascii=False).replace("</", "<\\/") + "</script>"]
    if with_q:
        out.append('<script id="pqd" type="application/json">' + json.dumps(model.q, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/") + "</script>")
    out.append("<script>" + js + "</script>\n</body>\n</html>\n")
    return "\n".join(out)


def toc(model, quick=False):
    items = []
    for c in model.chapters:
        n = c["num"]
        flag = ""
        if n == 7:
            flag = '<span class="p up">Top priority for UPPCS</span>'
        elif n == 8:
            flag = '<span class="p up">Optional for UPPCS</span>'
        items.append(f'<li><a href="#c{n}"><span class="no">{n}</span><span class="nm">{E(c["title"])}</span>{flag}'
                     f'<span class="q">{model.ch_count.get(f"c{n}", 0)} practice questions</span></a></li>')
    return '<ol class="toc">' + "".join(items) + "</ol>"


def side_nav(model, extra):
    out = ['<nav class="side" id="side" aria-label="Contents"><a href="#home" data-v="home">Start here</a>']
    out += [f'<a href="#{v}" data-v="{v}">{E(t)}</a>' for v, t in extra]
    out.append('<div class="lb">Chapters</div>')
    out += [f'<a href="#c{c["num"]}" data-v="c{c["num"]}"><span>{c["num"]}</span>{E(c["title"])}</a>' for c in model.chapters]
    out.append("</nav><main>")
    return "".join(out)


HOW = """<div class="how">
<div><b>1. Read once, with the answers showing.</b> Questions are in normal text, answers are green; key facts the magazine printed in bold are highlighted. The green box above each article is the short version to memorise.</div>
<div><b>2. Turn on Test mode and recall.</b> Answers and highlighted facts turn into grey boxes. Say the answer out loud, then tap the box to check. Retrieving from memory fixes facts far better than re-reading.</div>
<div><b>3. Practise.</b> Each chapter has multiple-choice practice built from the issue's own facts. Wrong answers are remembered and come back in "Your weak questions" until you get them right twice (spaced repetition).</div>
<div><b>4. Use the memory aids.</b> Purple "Memory aid" lines link a fact to a picture, pattern or number; red "Don't confuse" lines separate look-alike facts. They are learning aids, not extra facts.</div>
</div>"""


def topic_html(model, u, with_ids=True, compact=False):
    m = model.m(u)
    aid = model.anchor[u["id"]]
    idattr = f' id="{aid}"' if with_ids else ""
    must = '<span class="must">Must know</span>' if model.priority(u) == 1 else ""
    if u["kind"] == "story":
        qs = []
        for qid in u["qa"]:
            q = model.qa[qid]
            qid_attr = f' id="c1-{qid}"' if with_ids else ""
            qs.append(f'<li class="pt"{qid_attr}><span class="q">{E(q["q"])}</span><span class="a">{E(clean_answer(q["a"]))}</span></li>')
        date = f'{E(u["date"])} · ' if u.get("date") else ""
        return (f'<article class="topic story"{idattr} data-u="{u["id"]}" data-title="{E(u["title"][:80])}">'
                f'<p class="date">{date}{E(u["group"] or "")} · {pages_label(u["pages"])} {must}</p>'
                f'<ol class="qa">{"".join(qs)}</ol>{mem_html(m, story=True)}</article>')
    sub = f'<span class="sub">{E(u["subtitle"])}</span>' if u.get("subtitle") else ""
    gist = f'<p class="gist">{E(m["gist"])}</p>' if m.get("gist") else ""
    body = ""
    if not compact:
        a = model.arts[u["article"]]
        body = '<p class="src-h">From the magazine</p><div class="src">' + blocks_html([a["blocks"][i] for i in u["blocks"]]) + "</div>"
    return (f'<article class="topic"{idattr} data-u="{u["id"]}" data-title="{E(u["title"])}">'
            f'<h3>{E(u["title"])} {sub}{must}<span class="pg">{pages_label(u["pages"])}</span></h3>'
            f'{gist}{mem_html(m)}{body}</article>')


def group_label(u):
    if u["kind"] == "story":
        return u.get("group") or ""
    bits = [x for x in (u.get("group"), u.get("category")) if x]
    return " · ".join(bits)


def chapter_view(model, c, quick=False):
    n = c["num"]
    us = model.by_ch[n]
    count = model.ch_count.get(f"c{n}", 0)
    must = sum(1 for u in us if model.priority(u) == 1)
    out = [f'<section class="view ch" id="c{n}" data-title="{E(c["title"])}"><p class="eyebrow">Chapter {n} · {pages_label([c["start"], c["end"]])}</p>'
           f'<h2>{E(c["title"])} <span class="pg">({E(c["hindi"])})</span></h2>'
           f'<p class="gist">{len(us)} {"stories" if n == 1 else "topics"} · {must} marked Must know · {count} practice questions</p>']
    if n == 8:
        out.append('<p class="optional">Optional for UPPCS: this chapter is about Bihar. Read it once; the 72-hour plan gives it less time.</p>')
    if n == 7:
        out.append('<p class="optional">Top priority for UPPCS: Uttar Pradesh facts are asked often. Learn every line.</p>')
    out.append('<p class="context testnote">Test mode is on: tap a grey box to reveal the answer.</p>')
    if not quick:
        out.append(f'<a class="btn" href="#practice" data-practice-ch="c{n}">Practise this chapter’s {count} questions →</a>')
    group = None
    for u in us:
        g = group_label(u)
        if g and g != group:
            out.append(f'<h3 class="cat">{E(g)}</h3>')
            group = g
        if quick:
            out.append(quick_topic(model, u))
        else:
            out.append(topic_html(model, u))
    prev_c = model.chapters[n - 2] if n > 1 else None
    next_c = model.chapters[n] if n < len(model.chapters) else None
    pn = '<nav class="pn">' + (f'<a href="#c{n - 1}">← {E(prev_c["title"])}</a>' if prev_c else '<a href="#home">← Start</a>') \
        + (f'<a class="nx" href="#c{n + 1}">{E(next_c["title"])} →</a>' if next_c else "") + "</nav>"
    out.append(pn + "</section>")
    return "".join(out)


NUM_MASK = re.compile(r"₹?\d[\d,.]*(?:\s?(?:%|per cent|crore|lakh|million|billion|km|kg|MW|GW|GWh|tonnes|"
                      r"th|st|nd|rd))?")


def recall_html(text):
    """Quick-notes line with its answer part in grey test-mode boxes: what follows the first
    "→", "=" or ": " in each "; "-separated part, or else its numbers."""
    out = []
    for seg in re.split(r"(;\s+)", text):
        if re.fullmatch(r";\s+", seg):
            out.append(E(seg))
            continue
        m = re.search(r"\s(?:→|=)\s|:\s", seg)
        if m and m.end() < len(seg):
            out.append(E(seg[:m.end()]) + f'<b class="k">{E(seg[m.end():])}</b>')
            continue
        pos = 0
        for n in NUM_MASK.finditer(seg):
            out.append(E(seg[pos:n.start()]) + f'<b class="k">{E(n.group(0))}</b>')
            pos = n.end()
        out.append(E(seg[pos:]))
    return "".join(out)


def short(t, n):
    """Cut at a word boundary, not mid-word."""
    if len(t) <= n:
        return t
    return t[:n].rsplit(" ", 1)[0].rstrip(",;:–-") + "…"


def quick_topic(model, u):
    m = model.m(u)
    aid = model.anchor[u["id"]]
    must = '<span class="must">Must know</span>' if model.priority(u) == 1 else ""
    if u["kind"] == "story":
        line = m.get("line") or "; ".join(f'{model.qa[q]["q"]} → {clean_answer(model.qa[q]["a"])}' for q in u["qa"])
        hook = f'<p class="hook"><b>Memory aid</b> {E(m["hook"])}</p>' if m.get("hook") else ""
        trap = f'<p class="trap"><b>Don\'t confuse</b> {E(m["trap"])}</p>' if m.get("trap") else ""
        aid_html = f'<div class="aid">{hook}{trap}</div>' if hook or trap else ""
        return (f'<article class="topic" id="{aid}" data-title="{E(u["title"][:80])}"><p class="pt line">{recall_html(line)} {must}</p>'
                f'{aid_html}<p class="date"><a href="{FULL}#{aid}">Full questions</a> · {pages_label(u["pages"])}</p></article>')
    facts = "".join(f'<li class="pt">{recall_html(f)}</li>' for f in m.get("facts", []))
    hook = f'<p class="hook"><b>Memory aid</b> {E(m["hook"])}</p>' if m.get("hook") else ""
    trap = f'<p class="trap"><b>Don\'t confuse</b> {E(m["trap"])}</p>' if m.get("trap") else ""
    aid_html = f'<div class="aid">{hook}{trap}</div>' if hook or trap else ""
    return (f'<article class="topic" id="{aid}" data-title="{E(u["title"])}"><h3>{E(u["title"])} {must}'
            f'<span class="pg"><a href="{FULL}#{aid}">full text</a></span></h3>'
            f'<div class="mem"><ul>{facts}</ul>{aid_html}</div></article>')


def priority_rows(model, link_prefix=""):
    rows = []
    for u in model.priority_units():
        m = model.m(u)
        aid = model.anchor[u["id"]]
        if u["kind"] == "story":
            head_txt = m.get("line") or model.qa[u["qa"][0]]["q"]
            body = "<ul>" + "".join(f'<li>{E(model.qa[q]["q"])} <b>{E(clean_answer(model.qa[q]["a"]))}</b></li>' for q in u["qa"]) + "</ul>"
        else:
            head_txt = f'{u["title"]}: {m.get("gist", "")}'.strip(": ")
            body = "<ul>" + "".join(f"<li>{E(f)}</li>" for f in m.get("facts", [])) + "</ul>"
        rows.append(f'<li><details><summary><span class="t"><b>Ch {u["ch"]}</b> {E(head_txt)}</span></summary>'
                    f'<div class="yrs">{body}<a href="{link_prefix}#{aid}">Open in chapter →</a></div></details></li>')
    return rows


def glossary(model):
    seen = OrderedDict()
    for u in model.units:
        for h in model.m(u).get("hindi", []):
            key = h.strip()
            if key and key not in seen:
                seen[key] = (u["ch"], model.anchor[u["id"]])
    rows = []
    for h, (ch, aid) in seen.items():
        m = re.match(r"^(.*?)\s*\((.*)\)\s*$", h)
        en, hi = (m.group(1), m.group(2)) if m else (h, "")
        rows.append(f'<tr><td>{E(en)}</td><td lang="hi">{E(hi)}</td><td><a href="#{aid}">Ch {ch}</a></td></tr>')
    return rows


# ------------------------------------------------------------------ the three pages
def build_full(model):
    meta = model.meta()
    out = [head("Current Affairs Full Notes · UPPCS", f"Every question, answer and key fact of {ISSUE}, made easy to memorise for UPPCS.", "full"),
           side_nav(model, [("repeated", "Must-know revision"), ("practice", f"Practice · {len(model.q)}"),
                            ("glossary", "Hindi terms (शब्दावली)")])]
    out.append(f'<section class="view" id="home" data-title="Start"><p class="eyebrow">{E(ISSUE)}</p><h1>Current Affairs for UPPCS</h1>'
               f'<p class="gist">All {meta["source_qa_items"]} one-line questions with their answers, and every article, news item and table of the issue, '
               'with a short memory card on top of each.</p>'
               f'<div class="context">{E(CONTEXT)}</div>{HOW}{toc(model)}'
               f'<p class="foot">Based on {meta["source_qa_items"]} question–answer pairs and {meta["study_units"] - 249} articles and news items '
               f'({meta["bold_key_facts"]:,} bold key facts) from {ISSUE}; {meta["practice_questions"]:,} source practice questions. '
               'No UPPSC previous-year questions are claimed.</p></section>')
    rows = priority_rows(model)
    out.append(f'<section class="view" id="repeated" data-title="Must-know revision"><h2>Must-know revision</h2>'
               f'<p class="gist">{len(rows)} priority facts from the source, chosen for UPPCS: Uttar Pradesh, central schemes and laws, '
               'indices and India\'s rank, firsts, summits, appointments and awards. Tap one to see the details.</p>'
               f'<ol class="rows">{"".join(rows)}</ol></section>')
    opts = "".join(f'<option value="c{c["num"]}">{c["num"]}. {E(c["title"])} ({model.ch_count.get(f"c{c["num"]}", 0)})</option>' for c in model.chapters)
    out.append(f'<section class="view" id="practice" data-title="Practice"><h2>Practice</h2>'
               f'<p class="gist">{len(model.q):,} multiple-choice questions built from the issue: every Points to Remember question, and one or two per article. '
               'Your answers and mistakes are saved on this device.</p>'
               f'<div class="pq-bar"><label>Chapter <select id="pqCh"><option value="">All chapters</option>{opts}</select></label>'
               '<label><input id="pqPri" type="checkbox"> Must-know only</label><label><input id="pqMiss" type="checkbox"> Only my mistakes</label>'
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


def build_quick(model):
    meta = model.meta()
    out = [head("Current Affairs Quick Notes · UPPCS", f"One-line recall notes for {ISSUE}, for fast UPPCS revision.", "quick"),
           side_nav(model, [("repeated", "Must-know revision")])]
    out.append(f'<section class="view" id="home" data-title="Start"><p class="eyebrow">{E(ISSUE)}</p><h1>Current Affairs · Quick Notes</h1>'
               '<p class="gist">Only what to memorise: one line per story, the key facts of every article, memory aids and traps. '
               'Each topic links to its full text.</p>'
               f'<div class="context">{E(CONTEXT)}</div>{toc(model, quick=True)}'
               f'<p class="foot">Based on {meta["practice_questions"]} source practice questions and {meta["study_units"]} study units of {ISSUE}. '
               'No UPPSC previous-year questions are claimed.</p></section>')
    rows = priority_rows(model, FULL)
    out.append(f'<section class="view" id="repeated" data-title="Must-know revision"><h2>Must-know revision</h2>'
               '<p class="gist">The facts to revise first.</p>'
               f'<h3 id="rep-facts" class="sec">{len(rows)} priority facts from the source</h3><ol class="rows">{"".join(rows)}</ol></section>')
    for c in model.chapters:
        out.append(chapter_view(model, c, quick=True))
    out.append('<section class="view" id="results" data-title="Search"><h2>Search</h2><p class="score" id="rt"></p><ol id="rl"></ol></section>')
    out.append(tail(model, False))
    return "\n".join(out)


# ------------------------------------------------------------------ 72-hour plan
def unit_weight(model, u):
    if u["kind"] == "story":
        return sum(len(model.qa[q]["q"]) + len(model.qa[q]["a"]) for q in u["qa"])
    a = model.arts[u["article"]]
    total = 0
    for i in u["blocks"]:
        b = a["blocks"][i]
        if b["kind"] == "table":
            total += sum(len(t) for row in b["rows"] for c, *_ in row for t, _ in c)
        else:
            total += sum(len(t) for t, _ in b["runs"])
    return total


def split_hours(model):
    w = {n: sum(unit_weight(model, u) for u in us) * WEIGHT.get(n, 1.0) for n, us in model.by_ch.items()}
    total = sum(w.values())
    raw = {n: LEARN_HOURS * w[n] / total for n in w}
    hrs = {n: max(1, int(raw[n])) for n in w}
    while sum(hrs.values()) < LEARN_HOURS:
        n = max(w, key=lambda k: raw[k] - hrs[k])
        hrs[n] += 1
    while sum(hrs.values()) > LEARN_HOURS:
        n = max((k for k in w if hrs[k] > 1), key=lambda k: hrs[k] - raw[k])
        hrs[n] -= 1
    learn = []
    for n, us in model.by_ch.items():
        k = hrs[n]
        weights = [unit_weight(model, u) for u in us]
        target = sum(weights) / k
        chunks, cur, acc = [], [], 0
        for u, wt in zip(us, weights):
            if cur and acc + wt / 2 > target * (len(chunks) + 1) and len(chunks) < k - 1:
                chunks.append(cur)
                cur = []
            cur.append(u)
            acc += wt
        chunks.append(cur)
        while len(chunks) < k:      # very uneven units: split the largest chunk
            big = max(range(len(chunks)), key=lambda i: len(chunks[i]))
            half = len(chunks[big]) // 2
            chunks[big:big + 1] = [chunks[big][:half], chunks[big][half:]]
        title = next(c["title"] for c in model.chapters if c["num"] == n)
        for i, ch in enumerate(chunks, 1):
            learn.append({"ch": n, "title": title if k == 1 else f"{title} · part {i} of {k}", "units": ch})
    return learn


def hour_shell(n, phase, title, gist, guide):
    return (f'<section class="view" id="h{n}" data-n="{n}" data-title="Hour {n}"><p class="eyebrow">Hour {n} of 72 · {phase}</p>'
            f'<h2>{E(title)}</h2><p class="gist">{E(gist)}</p><div class="guide">{guide}</div>')


def done_html(n):
    nxt = f'<a class="btn nx" href="#h{n + 1}">Hour {n + 1} →</a>' if n < 72 else '<a class="btn nx" href="#home">Back to the plan →</a>'
    return f'<div class="done"><button class="btn" type="button" data-done="{n}">Mark hour {n} done</button>{nxt}</div></section>'


def build_plan(model):
    learn = split_hours(model)
    assert len(learn) == LEARN_HOURS, len(learn)
    hour_q = {}
    out = [head("Current Affairs in 72h · UPPCS", f"72 one-hour sessions to learn and memorise {ISSUE} before UPPCS Prelims.", "plan")]
    # navigation
    nav = ['<nav class="side" id="side" aria-label="Hours"><a href="#home" data-v="home"><span></span>Plan</a><div class="lb">Learn</div>']
    for i, h in enumerate(learn, 1):
        nav.append(f'<a href="#h{i}" data-v="h{i}"><span>{i}</span>{E(h["title"])}</a>')
    pri = model.priority_units()
    per = -(-len(pri) // 10)
    revise = [pri[i:i + per] for i in range(0, len(pri), per)][:10]
    while len(revise) < 10:
        revise.append([])
    revise_titles = []
    for chunk in revise:
        chs = sorted({u["ch"] for u in chunk})
        names = [next(c["title"] for c in model.chapters if c["num"] == x) for x in chs]
        revise_titles.append("Revise: " + (", ".join(names) if names else "mixed"))
    revise_titles += ["Revise: your weak questions", "Revise: traps and look-alike facts"]
    nav.append('<div class="lb">Revise</div>')
    for j, t in enumerate(revise_titles):
        n = LEARN_HOURS + 1 + j
        nav.append(f'<a href="#h{n}" data-v="h{n}"><span>{n}</span>{E(t)}</a>')
    nav.append('<div class="lb">Test</div>')
    for j in range(TEST_HOURS):
        n = LEARN_HOURS + REVISE_HOURS + 1 + j
        nav.append(f'<a href="#h{n}" data-v="h{n}"><span>{n}</span>Mock test {j + 1}: 25 mixed questions</a>')
    nav.append("</nav><main>")
    out.append("".join(nav))
    # home
    hrs_by_ch = Counter(h["ch"] for h in learn)
    rows = "".join(f'<tr><td>{c["num"]}. {E(c["title"])}</td><td>{hrs_by_ch[c["num"]]}</td></tr>' for c in model.chapters)
    out.append(f'<section class="view" id="home" data-title="72-hour plan"><p class="eyebrow">{LEARN_HOURS} learn · {REVISE_HOURS} revise · {TEST_HOURS} mock tests</p>'
               f'<h1>Current Affairs in 72 hours</h1><p class="gist">Learn the whole {E(ISSUE)} issue in 72 hours before {EXAM}: one hour a day or several, in order. '
               'Every hour mixes reading, recall and questions from earlier hours, so facts come back just as you start to forget them.</p>'
               f'<div class="context">{E(CONTEXT)}</div>'
               '<div class="how"><div><b>Each learn hour (60 min):</b> read the hour\'s topics (30) · switch on Test mode in the full notes and recall the grey boxes (10) · '
               'answer this hour\'s questions (10) · answer the spaced-review questions from 1, 3, 7, 15 and 30 hours ago, plus your weak questions (10).</div>'
               '<div><b>Revise hours:</b> must-know facts by chapter, then your weak questions, then traps.</div>'
               '<div><b>Mock tests:</b> 25 mixed questions in 20 minutes, like the real paper\'s pace. Review every mistake afterwards.</div></div>'
               f'<a class="cta" id="cont" href="#h1">Start with hour 1 →</a>'
               f'<h3 class="sec">Learn hours per chapter</h3><div class="table-scroll"><table><tr><td>Chapter</td><td>Learn hours</td></tr>{rows}</table></div>'
               f'<p class="foot">72 hours before {EXAM}. Uttar Pradesh gets extra time; Bihar (optional for UPPCS) gets less. Progress is saved on this device.</p></section>')
    # learn hours
    for i, h in enumerate(learn, 1):
        us = h["units"]
        qids = [q for u in us for q in model.unit_q[u["id"]]]
        hour_q[i] = qids
        review = []
        for gap in REVIEW_GAPS:
            j = i - gap
            if j >= 1 and hour_q.get(j):
                pool = list(hour_q[j])
                random.Random(seed("rev", str(i), str(j))).shuffle(pool)
                review += pool[:3]
        gist = ", ".join(short(u["title"], 60) for u in us[:6]) + (f" and {len(us) - 6} more" if len(us) > 6 else "")
        guide = ('Read every topic once (30 min), then cover the answers and recall (10 min). Use '
                 f'<a href="{FULL}#c{h["ch"]}">Test mode in the full notes</a> for the grey-box check.')
        if h["ch"] == 8:
            guide += " This chapter is optional for UPPCS: a single careful read is enough."
        part = [hour_shell(i, "Learn", h["title"], gist, guide), '<div class="read">']
        group = None
        for u in us:
            g = group_label(u)
            if g and g != group:
                part.append(f'<h3 class="cat">{E(g)}</h3>')
                group = g
            part.append(topic_html(model, u))
        part.append("</div>")
        if qids:
            part.append(f'<h3 class="ph">Practise this hour: {len(qids)} questions</h3><p class="score"></p><ol class="pq" data-q="{",".join(qids)}"></ol>')
        if review:
            part.append(f'<h3 class="ph">Spaced review: {len(review)} questions from earlier hours</h3><p class="score"></p><ol class="pq" data-q="{",".join(review)}"></ol>')
        if i > 1:
            part.append('<h3 class="ph">Your weak questions</h3><p class="score"></p><ol class="pq" data-review="10"></ol>')
        part.append(done_html(i))
        out.append("".join(part))
    # revise hours
    for j, chunk in enumerate(revise):
        n = LEARN_HOURS + 1 + j
        qids = [q for u in chunk for q in model.unit_q[u["id"]] if model.q[q]["p"] == 1][:40]
        part = [hour_shell(n, "Revise", revise_titles[j], f"{len(chunk)} must-know topics. Say each fact aloud before you read it.",
                           "Cover each card, recall it, then check. Mark any you missed and answer the questions below.")]
        part += [quick_topic_plain(model, u) for u in chunk]
        part.append(f'<h3 class="ph">Must-know questions: {len(qids)}</h3><p class="score"></p><ol class="pq" data-q="{",".join(qids)}"></ol>')
        part.append(done_html(n))
        out.append("".join(part))
    n = LEARN_HOURS + 11
    out.append(hour_shell(n, "Revise", revise_titles[10], "Every question you have answered wrongly so far, hardest first.",
                          "Answer each one again. A question leaves this list once you get it right twice.")
               + '<p class="score"></p><ol class="pq" data-review="60"></ol>' + done_html(n))
    traps = [(u, model.m(u)["trap"]) for u in model.units if model.m(u).get("trap")]
    n = LEARN_HOURS + 12
    trap_html = "".join(f'<li class="pt"><b>{E(short(u["title"], 70))}</b>: {E(t)} <a href="{FULL}#{model.anchor[u["id"]]}">note</a></li>' for u, t in traps)
    out.append(hour_shell(n, "Revise", revise_titles[11], f"{len(traps)} look-alike facts that are easy to mix up.",
                          "Read each pair and say the difference in your own words.")
               + f'<ul class="read">{trap_html}</ul>' + done_html(n))
    # mocks: interleaved, weighted to must-know, no repeats
    all_q = list(model.q)
    rng = random.Random(seed("mocks"))
    must = [q for q in all_q if model.q[q]["p"] == 1]
    rest = [q for q in all_q if model.q[q]["p"] != 1]
    rng.shuffle(must)
    rng.shuffle(rest)
    for j in range(TEST_HOURS):
        n = LEARN_HOURS + REVISE_HOURS + 1 + j
        picked = must[j * 17:(j + 1) * 17] + rest[j * 8:(j + 1) * 8]
        rng.shuffle(picked)
        part = [hour_shell(n, "Test", f"Mock test {j + 1}: 25 mixed questions", "Questions from every chapter, about two-thirds must-know.",
                           "Press Start, answer all 25 in 20 minutes, then Submit. Spend the rest of the hour reading the note for every mistake."),
                f'<div class="mock" data-min="20"><div class="mock-bar"><button class="btn" type="button" data-mock-start="m{j + 1}">Start 20-minute timer</button>'
                f'<span class="timer">20:00</span><button class="btn" type="button" data-mock-submit="m{j + 1}">Submit</button></div>'
                f'<p class="score"></p><ol class="pq" data-mock="m{j + 1}" data-q="{",".join(picked)}"></ol></div>', done_html(n)]
        out.append("".join(part))
    out.append(tail(model, True))
    return "\n".join(out), learn


def quick_topic_plain(model, u):
    m = model.m(u)
    if u["kind"] == "story":
        body = "<ul>" + "".join(f'<li class="pt">{E(model.qa[q]["q"])} <span class="qa"><span class="a">{E(clean_answer(model.qa[q]["a"]))}</span></span></li>' for q in u["qa"]) + "</ul>"
        return f'<article class="topic"><p class="date">Ch 1 · {E(u["group"] or "")}</p>{body}{mem_html(m, story=True)}</article>'
    return (f'<article class="topic"><h3>{E(u["title"])} <span class="pg">Ch {u["ch"]} · <a href="{FULL}#{model.anchor[u["id"]]}">full text</a></span></h3>'
            f'{mem_html(m)}</article>')


def main():
    draft = "--draft" in sys.argv
    src, units, memory = load(draft)
    model = Model(src, units, memory)
    OUT.mkdir(exist_ok=True)
    full = build_full(model)
    quick = build_quick(model)
    plan, learn = build_plan(model)
    for name, text in ((FULL, full), (QUICK, quick), (PLAN, plan)):
        (OUT / name).write_text(text, encoding="utf-8", newline="\n")
        print(f"wrote {name}: {len(text):,} chars")
    (HERE / "ca_plan.json").write_text(json.dumps([{"hour": i, "title": h["title"], "units": [u["id"] for u in h["units"]]}
                                                   for i, h in enumerate(learn, 1)], ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"practice questions {len(model.q)}, priority facts {len(model.priority_units())}, learn hours by chapter "
          f"{dict(Counter(h['ch'] for h in learn))}")


if __name__ == "__main__":
    main()
