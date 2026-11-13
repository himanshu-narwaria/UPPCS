"""Build Polity-UPPCS-Plus.html: the same fact lists as Polity-UPPCS.html with recall, flashcards, quiz, progress, focus mode and timelines.
Heat levels count UPPSC papers only. Run: python -I build_plus.py"""
import re, json, html, os, collections
W = os.path.dirname(os.path.abspath(__file__)); os.chdir(W)
src = open('build.py', encoding='utf-8').read()
exec(src[:src.index('ORDER = sorted(CH)')])          # parsing: A, QI, TITLE, CH, allf, esc, inline, errors
OUT = os.path.join(W, '..', '..', '..', 'Indian_Polity_and_Governance', 'Polity-UPPCS-Plus.html')
ORDER = sorted(CH)
GROUPS = [(range(1, 11), 'Making and basics of the Constitution', '#0f766e'), (range(11, 16), 'States, citizens and rights', '#4338ca'),
          (range(16, 27), 'Union: executive, Parliament, Supreme Court', '#c2410c'), (range(27, 32), 'States and Centre-State relations', '#15803d'),
          (range(32, 43), 'Bodies, elections, local government and more', '#7e22ce')]
def group(ch): return next(i for i, (r, _, _) in enumerate(GROUPS) if ch in r)
KEY = re.compile(r'Articles? \d+[A-Z]?(?:\(\d+\))?(?:\([a-z]\))?|\b\d+(?:st|nd|rd|th) (?:Amendment|Schedule)|\b(?:1[6-9]\d\d|20[0-2]\d)\b|\b\d+(?:\.\d+)?%?')
def fact_html(text):
    h = inline(text)
    if '<b>' not in h:
        h = KEY.sub(lambda m: '<b>' + m.group(0) + '</b>', h, count=1)
    return h
YEAR = re.compile(r'\b(1[6-9]\d\d|20[0-2]\d)\b')
for n, f in enumerate(allf): f['id'] = f'f{n}'; f['u'] = len(f['up'])
heat = lambda f: ' h3' if f['u'] >= 6 else ' h2' if f['u'] >= 4 else ' h1' if f['u'] >= 2 else ''
def cls(f): return 'f' + (' a' if f['u'] else '') + heat(f)
def pill(f):
    if not f['u']: return ''
    return f'<span class="p u{heat(f)}" title="{esc("; ".join(f["up"]))}">UPPSC{" ×" + str(f["u"]) if f["u"] > 1 else ""}</span>'
TK = '<button class="tk" type="button" aria-label="Mark as known"></button>'
tl_count = 0
def render(ch):
    global tl_count
    fs = [f for f in allf if f['ch'] == ch]; g = group(ch)
    o = [f'<section class="view ch g{g}" id="c{ch}" data-title="{esc(TITLE[ch])}" data-n="{len(fs)}"><p class="eyebrow">Chapter {ch} · {esc(GROUPS[g][1])}</p><h2>{esc(TITLE[ch])}</h2>'
         f'<p class="gist"><span class="ring" data-ch="{ch}"></span> {len(fs)} facts · {sum(1 for f in fs if f["u"] >= 2)} repeated by UPPSC</p>']
    top = sorted([f for f in fs if f['u'] >= 2], key=lambda f: -f['u'])[:5]
    if top:
        o.append('<div class="topf"><h3>UPPSC asks these most</h3><ol>' + ''.join(f'<li><span>{fact_html(f["text"])}</span><span class="cnt">×{f["u"]}</span></li>' for f in top) + '</ol></div>')
    nq = sum(1 for (c, i), q in QI.items() if c == ch and q['uppsc_exams'] and q['k'] and not q['review'])
    o.append(f'<div class="acts"><a class="btn" href="#quiz" data-quiz="{ch}">Quick quiz: 10 of {nq} UPPSC questions</a></div>' if nq >= 4 else '')
    for ti, t in enumerate(CH[ch], 1):
        tid = f'c{ch}-t{ti}'
        dated = [(int(YEAR.search(v['text']).group(1)), v) for k, v in t['items'] if k == 'pt' and YEAR.search(v['text'])]
        npt = sum(1 for k, v in t['items'] if k == 'pt')
        has_tl = len(dated) >= 6 and len(dated) >= 0.5 * npt
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
# flashcard deck: facts repeated by UPPSC, most-asked first
deck = [dict(i=f['id'], h=fact_html(f['text']), c=f['ch'], n=f['u'], t=f.get('tid', f'c{f["ch"]}')) for f in sorted([f for f in allf if f['u'] >= 2], key=lambda f: (-f['u'], f['ch']))]
# quiz: UPPSC questions with a clear key
fact_of = {(f['ch'], i): f for f in allf for i in f['ids']}
quiz = collections.defaultdict(list)
for (ch, i), q in sorted(QI.items()):
    if not (q['uppsc_exams'] and q['k'] and not q['review'] and len(q['o']) >= 4): continue
    f = fact_of.get((ch, i))
    quiz[ch].append(dict(s=esc(re.sub(r'\s+', ' ', q['s'])), o=[esc(x) for x in q['o']], k=q['k'], e=esc('; '.join(re.sub(r'\s+', ' ', e) for e in q['uppsc_exams'])), f=fact_html(f['text']) if f else '', t=f.get('tid', '') if f else ''))
home = ''
for gi, (r, name, col) in enumerate(GROUPS):
    home += f'<h3 class="gh g{gi}">{esc(name)}</h3><ol class="toc">' + ''.join(f'<li><a href="#c{ch}" class="g{gi}"><span class="no">{ch}</span><span class="nm">{esc(TITLE[ch])}</span><span class="ring" data-ch="{ch}"></span></a></li>' for ch in ORDER if ch in r) + '</ol>'
side = ''.join(f'<a href="#c{ch}" data-v="c{ch}" class="g{group(ch)}"><span>{ch}</span>{esc(TITLE[ch])}</a>' for ch in ORDER)
fonts = ''.join(re.findall(r'@font-face\{[^}]*\}', open('../polity/template_full_style.css', encoding='utf-8').read()))
gcss = ''.join(f'.g{i}{{--g:{c}}}' for i, (_, _, c) in enumerate(GROUPS))
css = fonts + gcss + open('plus.css', encoding='utf-8').read()
js = open('plus.js', encoding='utf-8').read()
total_u = sum(1 for f in allf if f['u'])
page = f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Polity-UPPCS Plus</title><meta name="description" content="Indian Polity for UPPCS: every fact of every chapter, with recall mode, flashcards, quizzes and progress.">
<style>{css}</style></head><body>
<header class="top"><button id="menu" aria-label="Open chapter list">☰</button><a class="brand" href="#home">Polity-UPPCS <i>Plus</i></a>
<input id="q" type="search" placeholder="Search facts" aria-label="Search facts" autocomplete="off"><span class="tot" id="tot"></span></header>
<div class="tools" id="tools"><label><input type="checkbox" id="tRecall"> Recall mode</label><label><input type="checkbox" id="tRep"> Repeated only</label><label><input type="checkbox" id="tWeak"> Hide known</label><label><input type="checkbox" id="tFocus"> Focus mode</label></div>
<div class="wrap"><nav class="side" id="side" aria-label="Chapters"><a href="#home" data-v="home"><span></span>Start</a><a href="#cards" data-v="cards" class="hl"><span></span>Flashcards</a><a href="#quiz" data-v="quiz" class="hl"><span></span>Quiz</a><div class="lb">Chapters</div>{side}</nav>
<main>
<section class="view" id="home"><h1>Polity-UPPCS <i>Plus</i></h1>
<p class="gist">Every fact of every chapter, now with self-testing and progress. Tap the circle beside a fact when you know it.</p>
<div class="stats"><div><b id="sKnown">0</b><span>of {len(allf)} facts known</span></div><div><b>{len(deck)}</b><span>repeated by UPPSC</span></div><div><b>{total_u}</b><span>asked by UPPSC</span></div></div>
<div class="bar"><i id="bar"></i></div>
<p class="legend"><span class="k h1"></span>UPPSC ×2–3 <span class="k h2"></span>×4–5 <span class="k h3"></span>×6 or more <span class="p u">UPPSC</span> asked once</p>
<div class="acts"><a class="btn pri" href="#cards">Flashcards: {len(deck)} repeated facts</a><a class="btn" href="#quiz">Quiz from UPPSC questions</a><a class="btn" id="cont" href="#c1">Continue reading</a></div>
<ul class="how"><li><b>Recall mode</b> hides the key term in each fact; tap it to check yourself.</li><li><b>Repeated only</b> shows facts UPPSC asked two or more times.</li><li><b>Hide known</b> leaves only what you have not ticked.</li><li><b>Focus mode</b> shows one topic at a time.</li></ul>
{home}
<p class="foot">{len(allf)} facts from all {len(ORDER)} chapters of Ghatna Chakra Preview Indian Polity and Governance 2026. Nothing from outside the book is added. Heat colours count UPPSC papers only (PCS Pre and Mains, RO/ARO, Lower Subordinate, UDA/LDA and other UPPSC exams). Quiz answers follow the book's keys. Ticks are saved in this browser only.</p></section>
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
print('facts', len(allf), 'uppsc asked', total_u, 'deck', len(deck), 'heat', collections.Counter(heat(f).strip() or '-' for f in allf), 'quiz q', sum(len(v) for v in quiz.values()), 'timelines', tl_count, 'bold', sum('**' in f['text'] for f in allf), 'size', os.path.getsize(OUT), 'errors', len(errors))
