"""Build History-UPPCS-Plus.html from out/chN.md (fact lists tagged with question numbers) and pyqbooks/history/source.json.
Heat levels count UPPSC papers only. Run: python -I build_plus.py"""
import re, json, html, os, collections
W = os.path.dirname(os.path.abspath(__file__)); os.chdir(W)
OUT = os.path.join(W, '..', '..', '..', 'Indian_History_Part_2', 'History-UPPCS-Plus.html')
esc = lambda s: html.escape(s, quote=False)
inline = lambda s: re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', esc(s))
S = json.load(open('../pyqbooks/history/source.json', encoding='utf-8'))
runs = lambda r: r if isinstance(r, str) else ''.join(x[0] for x in (r or []))
TITLE = {c['num']: re.sub(r'\s+', ' ', c['title']).replace('andPaintingsof', 'and Paintings of') for c in S['chapters']}
UPRE = re.compile(r'\W*(U\.\s?P\b|UP(?!SC)|R\.?O\.?/A\.?R\.?O)')   # "U.P.P.C.S.", "U.P P.C.S.", "[UPPCS ...]", "U.P. Lower Sub.", "R.O./A.R.O."
norm = lambda e: re.sub(r'\s+', ' ', e).strip()
QI = {}
for q in S['questions']:
    letters = [k for k in re.findall(r'[a-e]', q['ans'].lower()) if k in q['options']]
    order = list(q['options'])
    QI[(q['ch'], q['num'])] = dict(q=q, exams=[norm(t) for t in q['tags']], up=[norm(t) for t in q['tags'] if UPRE.match(t)], k=[order.index(k) for k in letters], order=order)
errors = []
def split_tag(s, ch, where):
    m = re.search(r'\s*\{([^{}]*)\}\s*$', s)
    if not m: return s.rstrip(), []
    ids = []
    for x in re.split(r'[,\s]+', m.group(1).strip()):
        if x.isdigit() and (ch, int(x)) in QI: ids.append(int(x))
        elif x: errors.append(f'{where}: bad tag {x}')
    return s[:m.start()].rstrip(), ids
def meta(ch, ids):
    up = []
    for i in ids:
        for e in QI[(ch, i)]['up']:
            if e not in up: up.append(e)
    return up
CH = {}; allf = []
for ch in sorted(TITLE):
    p = f'out/ch{ch}.md'
    if not os.path.exists(p): continue
    topics = []; topic = None; table = None
    for ln, raw in enumerate(open(p, encoding='utf-8').read().splitlines(), 1):
        l = raw.strip()
        if not l: table = None; continue
        if l.startswith('|'):
            cells = [c.strip() for c in l.strip('|').split('|')]
            if all(re.fullmatch(r':?-{2,}:?', c) for c in cells): continue
            if topic is None: topic = dict(title=TITLE[ch], items=[]); topics.append(topic)
            if table is None:
                table = dict(head=cells, rows=[]); topic['items'].append(('table', table))
            else:
                cells[-1], ids = split_tag(cells[-1], ch, f'ch{ch}:{ln}')
                f = dict(ch=ch, cells=cells, text=' · '.join(c for c in cells if c), ids=ids, up=meta(ch, ids)); table['rows'].append(f); allf.append(f)
            continue
        table = None
        if l.startswith('@'): continue
        if l.startswith('## '): topic = dict(title=l[3:].strip(), items=[]); topics.append(topic)
        elif l.startswith('- '):
            if topic is None: topic = dict(title=TITLE[ch], items=[]); topics.append(topic)
            txt, ids = split_tag(l[2:].strip(), ch, f'ch{ch}:{ln}')
            f = dict(ch=ch, text=txt, ids=ids, up=meta(ch, ids)); topic['items'].append(('pt', f)); allf.append(f)
        elif l.startswith('! '):
            if topic is not None: topic['items'].append(('warn', l[2:].strip()))
        else: errors.append(f'ch{ch}:{ln}: unknown line {l[:50]}')
    CH[ch] = topics
ORDER = sorted(CH)
GROUPS = [(range(1, 15), 'Ancient India', '#0f766e'), (range(15, 41), 'Medieval India', '#4338ca'), (range(41, 52), 'British rule, revolts and reform', '#c2410c'),
          (range(52, 92), 'Freedom struggle', '#15803d'), (range(92, 96), 'Miscellaneous, books, art and culture', '#7e22ce')]
def group(ch): return next(i for i, (r, _, _) in enumerate(GROUPS) if ch in r)
KEY = re.compile(r'\b\d{1,4}(?:[-–]\d{1,4})?\s?(?:B\.?C\.?E?\.?|A\.?D\.?|C\.?E\.?)|\b\d+(?:st|nd|rd|th) century|\b(?:1[0-9]\d\d)\b|\b\d+(?:\.\d+)?%?')
def fact_html(text):
    h = inline(text)
    return h if '<b>' in h else KEY.sub(lambda m: '<b>' + m.group(0) + '</b>', h, count=1)
YEAR = re.compile(r'(?<![\d-])(1[0-9]\d\d)\b(?!\s?B)')
for n, f in enumerate(allf): f['id'] = f'f{n}'; f['u'] = len(f['up'])
heat = lambda f: ' h3' if f['u'] >= 6 else ' h2' if f['u'] >= 4 else ' h1' if f['u'] >= 2 else ''
cls = lambda f: 'f' + (' a' if f['u'] else '') + heat(f)
def pill(f):
    return f'<span class="p u{heat(f)}" title="{esc("; ".join(f["up"]))}">UPPSC{" ×" + str(f["u"]) if f["u"] > 1 else ""}</span>' if f['u'] else ''
TK = '<button class="tk" type="button" aria-label="Mark as known"></button>'
tl_count = 0
def quiz_ok(v): return v['up'] and v['k'] and len(v['order']) >= 4
def render(ch):
    global tl_count
    fs = [f for f in allf if f['ch'] == ch]; g = group(ch)
    o = [f'<section class="view ch g{g}" id="c{ch}" data-title="{esc(TITLE[ch])}" data-n="{len(fs)}"><p class="eyebrow">Chapter {ch} · {esc(GROUPS[g][1])}</p><h2>{esc(TITLE[ch])}</h2>'
         f'<p class="gist"><span class="ring" data-ch="{ch}"></span> {len(fs)} facts · {sum(1 for f in fs if f["u"] >= 2)} repeated by UPPSC</p>']
    top = sorted([f for f in fs if f['u'] >= 2], key=lambda f: -f['u'])[:5]
    if top: o.append('<div class="topf"><h3>UPPSC asks these most</h3><ol>' + ''.join(f'<li><span>{fact_html(f["text"])}</span><span class="cnt">×{f["u"]}</span></li>' for f in top) + '</ol></div>')
    nq = sum(1 for (c, i), v in QI.items() if c == ch and quiz_ok(v))
    if nq >= 4: o.append(f'<div class="acts"><a class="btn" href="#quiz" data-quiz="{ch}">Quick quiz: {min(10, nq)} of {nq} UPPSC questions</a></div>')
    for ti, t in enumerate(CH[ch], 1):
        tid = f'c{ch}-t{ti}'
        dated = [(int(YEAR.search(v['text']).group(1)), v) for k, v in t['items'] if k == 'pt' and YEAR.search(v['text'])]
        npt = sum(1 for k, v in t['items'] if k == 'pt'); has_tl = len(dated) >= 6 and len(dated) >= 0.5 * npt
        o.append(f'<article class="topic" id="{tid}"><h3>{esc(t["title"])}' + ('<button class="tlb" type="button" aria-pressed="false">Timeline</button>' if has_tl else '') + '</h3>')
        if has_tl:
            tl_count += 1
            o.append('<ol class="tl" hidden>' + ''.join(f'<li><span class="yr">{y}</span><span>{fact_html(v["text"])}{pill(v)}</span></li>' for y, v in sorted(dated, key=lambda x: x[0])) + '</ol>')
        buf = []
        def flush():
            if buf: o.append('<ul class="fl">' + ''.join(buf) + '</ul>'); buf.clear()
        for k, v in t['items']:
            if k == 'table':
                flush(); w = len(v['head']); rows = ''
                for f in v['rows']:
                    f['tid'] = tid; cells = (f['cells'] + [''] * w)[:w]
                    rows += f'<tr class="{cls(f)}" id="{f["id"]}"><td class="tkc">{TK}</td>' + ''.join(f'<td>{inline(c)}</td>' for c in cells[:-1]) + f'<td>{inline(cells[-1])}{pill(f)}</td></tr>'
                o.append(f'<div class="tw"><table><thead><tr><th></th>{"".join("<th>" + inline(c) + "</th>" for c in v["head"])}</tr></thead><tbody>{rows}</tbody></table></div>')
            elif k == 'warn':
                flush(); o.append(f'<p class="warn"><b>Note from the book</b> {inline(v)}</p>')
            else:
                v['tid'] = tid; buf.append(f'<li class="{cls(v)}" id="{v["id"]}">{TK}<span class="tx">{fact_html(v["text"])}</span>{pill(v)}</li>')
        flush(); o.append('</article>')
    i = ORDER.index(ch)
    o.append('<nav class="pn">' + (f'<a href="#c{ORDER[i-1]}">← {esc(TITLE[ORDER[i-1]])}</a>' if i else '<a href="#home">← Start</a>') + (f'<a class="nx" href="#c{ORDER[i+1]}">{esc(TITLE[ORDER[i+1]])} →</a>' if i < len(ORDER) - 1 else '<a class="nx" href="#cards">Flashcards →</a>') + '</nav></section>')
    return ''.join(o)
chapters = ''.join(render(ch) for ch in ORDER)
deck = [dict(i=f['id'], h=fact_html(f['text']), c=f['ch'], n=f['u']) for f in sorted([f for f in allf if f['u'] >= 2], key=lambda f: (-f['u'], f['ch']))]
fact_of = {(f['ch'], i): f for f in allf for i in f['ids']}
quiz = collections.defaultdict(list)
for (ch, i), v in sorted(QI.items()):
    if ch not in CH or not quiz_ok(v): continue
    q = v['q']; f = fact_of.get((ch, i))
    stem = esc(re.sub(r'\s+', ' ', runs(q['stem'])))
    if q['mid']:
        mid = [runs(b['runs']) if isinstance(b, dict) and 'runs' in b else ' | '.join(runs(c) for c in row) if False else (runs(b) if not isinstance(b, dict) else '<br>'.join(' · '.join(runs(c) if not isinstance(c, str) else c for c in row) for row in b.get('rows', []))) for b in q['mid']]
        stem += '<br>' + '<br>'.join(esc(m) if '<br>' not in m else m for m in mid if m)
    quiz[ch].append(dict(s=stem, o=[esc(re.sub(r'\s+', ' ', runs(q['options'][k]))) for k in v['order']], k=v['k'], e=esc('; '.join(v['up'])), f=fact_html(f['text']) if f else '', t=f.get('tid', '') if f else ''))
home = ''
for gi, (r, name, col) in enumerate(GROUPS):
    home += f'<h3 class="gh g{gi}">{esc(name)}</h3><ol class="toc">' + ''.join(f'<li><a href="#c{ch}" class="g{gi}"><span class="no">{ch}</span><span class="nm">{esc(TITLE[ch])}</span><span class="ring" data-ch="{ch}"></span></a></li>' for ch in ORDER if ch in r) + '</ol>'
side = ''.join(f'<a href="#c{ch}" data-v="c{ch}" class="g{group(ch)}"><span>{ch}</span>{esc(TITLE[ch])}</a>' for ch in ORDER)
fonts = ''.join(re.findall(r'@font-face\s*\{[^}]*\}', open('../pyqbooks/fonts_embedded.css', encoding='utf-8').read()))
assert 'Atkinson' in fonts and 'Lexend' in fonts
css = fonts + ''.join(f'.g{i}{{--g:{c}}}' for i, (_, _, c) in enumerate(GROUPS)) + open('../polity_uppcs/plus.css', encoding='utf-8').read()
js = open('../polity_uppcs/plus.js', encoding='utf-8').read().replace("'polity-uppcs-plus'", "'history-uppcs-plus'").replace('Polity-UPPCS Plus', 'History-UPPCS Plus')
assert "'history-uppcs-plus'" in js
total_u = sum(1 for f in allf if f['u'])
page = f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>History-UPPCS Plus</title><meta name="description" content="Indian History for UPPCS: every fact of every chapter, with recall mode, flashcards, quizzes and progress.">
<style>{css}</style></head><body>
<header class="top"><button id="menu" aria-label="Open chapter list">☰</button><a class="brand" href="#home">History-UPPCS <i>Plus</i></a>
<input id="q" type="search" placeholder="Search facts" aria-label="Search facts" autocomplete="off"><span class="tot" id="tot"></span></header>
<div class="tools" id="tools"><label><input type="checkbox" id="tRecall"> Recall mode</label><label><input type="checkbox" id="tRep"> Repeated only</label><label><input type="checkbox" id="tWeak"> Hide known</label><label><input type="checkbox" id="tFocus"> Focus mode</label></div>
<div class="wrap"><nav class="side" id="side" aria-label="Chapters"><a href="#home" data-v="home"><span></span>Start</a><a href="#cards" data-v="cards" class="hl"><span></span>Flashcards</a><a href="#quiz" data-v="quiz" class="hl"><span></span>Quiz</a><div class="lb">Chapters</div>{side}</nav>
<main>
<section class="view" id="home"><h1>History-UPPCS <i>Plus</i></h1>
<p class="gist">Every fact of every chapter, with self-testing and progress. Tap the circle beside a fact when you know it.</p>
<div class="stats"><div><b id="sKnown">0</b><span>of {len(allf)} facts known</span></div><div><b>{len(deck)}</b><span>repeated by UPPSC</span></div><div><b>{total_u}</b><span>asked by UPPSC</span></div></div>
<div class="bar"><i id="bar"></i></div>
<p class="legend"><span class="k h1"></span>UPPSC ×2–3 <span class="k h2"></span>×4–5 <span class="k h3"></span>×6 or more <span class="p u">UPPSC</span> asked once</p>
<div class="acts"><a class="btn pri" href="#cards">Flashcards: {len(deck)} repeated facts</a><a class="btn" href="#quiz">Quiz from UPPSC questions</a><a class="btn" id="cont" href="#c1">Continue reading</a></div>
<ul class="how"><li><b>Recall mode</b> hides the key term in each fact; tap it to check yourself.</li><li><b>Repeated only</b> shows facts UPPSC asked two or more times.</li><li><b>Hide known</b> leaves only what you have not ticked.</li><li><b>Focus mode</b> shows one topic at a time.</li></ul>
{home}
<p class="foot">{len(allf)} facts from all {len(ORDER)} chapters of Ghatna Chakra Preview Indian History 2026: its explanation sections, its {len(S["questions"])} solved questions and their explanations. Nothing from outside the book is added. Heat colours count UPPSC papers only (PCS Pre and Mains, RO/ARO, Lower Subordinate, UDA/LDA and other UPPSC exams). Quiz answers follow the book's keys. Ticks are saved in this browser only.</p></section>
<section class="view" id="cards" data-title="Flashcards"><h2>Flashcards</h2><p class="gist">Facts UPPSC repeated, most-asked first. Say the hidden part, then reveal.</p>
<div class="acts"><label class="chk"><input type="checkbox" id="fcWeak" checked> Skip known</label><button class="btn" id="fcShuf" type="button">Shuffle</button><span class="gist" id="fcPos"></span></div>
<div class="card" id="fc" tabindex="0"><p class="cm" id="fcMeta"></p><p class="cf" id="fcFact"></p></div>
<div class="acts"><button class="btn" id="fcPrev" type="button">← Back</button><button class="btn pri" id="fcShow" type="button">Reveal</button><button class="btn ok" id="fcKnow" type="button">Got it ✓</button><button class="btn" id="fcNext" type="button">Again later →</button></div>
<p class="gist"><a id="fcOpen" href="#home">Open in chapter →</a></p></section>
<section class="view" id="quiz" data-title="Quiz"><h2>Quiz</h2><p class="gist">Ten real UPPSC questions from one chapter, with the book's answers.</p>
<div class="acts"><label class="chk">Chapter <select id="qzCh">{''.join(f'<option value="{ch}">{ch}. {esc(TITLE[ch])} ({len(quiz[ch])})</option>' for ch in ORDER if len(quiz[ch]) >= 4)}</select></label><button class="btn" id="qzNew" type="button">New 10</button><span class="gist" id="qzScore"></span></div>
<ol class="qz" id="qzList"></ol></section>
{chapters}
<section class="view" id="results" data-title="Search"><h2 id="rt">Search</h2><div id="rl" class="res"></div></section>
</main></div>
<div class="fbar" id="fbar" hidden><button class="btn" id="fPrev" type="button">← Back</button><span id="fPos"></span><button class="btn pri" id="fNext" type="button">Next →</button></div>
<div id="scrim"></div>
<script id="deck" type="application/json">{json.dumps(deck, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/')}</script>
<script id="quizd" type="application/json">{json.dumps(quiz, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/')}</script>
<script>{js}</script></body></html>'''
open(OUT, 'w', encoding='utf-8').write(page)
tagged = {(f['ch'], i) for f in allf for i in f['ids']}
scor = {k for k, v in QI.items() if v['k'] and k[0] in CH}
print('chapters', len(ORDER), 'facts', len(allf), 'uppsc asked', total_u, 'deck', len(deck), 'heat', dict(collections.Counter(heat(f).strip() or '-' for f in allf)))
print('quiz q', sum(len(v) for v in quiz.values()), 'timelines', tl_count, 'questions tagged', len(tagged & scor), 'of', len(scor), 'size', os.path.getsize(OUT), 'errors', len(errors), errors[:5])
print('uppsc flag agreement', sum(bool(v['up']) == bool(v['q']['up']) for v in QI.values()), 'of', len(QI))
