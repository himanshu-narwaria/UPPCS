"""Build Polity-UPPCS.html from out/chN.md (fact lists tagged with question item numbers). Run: python -I build.py"""
import re, json, html, os, collections
W = os.path.dirname(os.path.abspath(__file__)); os.chdir(W)
OUT = os.path.join(W, '..', '..', '..', 'Indian_Polity_and_Governance', 'Polity-UPPCS.html')
esc = lambda s: html.escape(s, quote=False)
inline = lambda s: re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', esc(s))
A = json.load(open('../polity/all_source_questions.json', encoding='utf-8'))
QI = {(q['chapter'], int(re.search(r'item(\d+)$', q['id']).group(1))): q for q in A}
BOUNDS = json.load(open('../polity/chapter_boundaries.json', encoding='utf-8'))
TITLE = {b['chapter_no']: re.sub(r'\s+', ' ', b['title']) for b in BOUNDS}
norm_exam = lambda e: re.sub(r'\s+', ' ', e).strip()
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
    exams = []; up = []
    for i in ids:
        q = QI[(ch, i)]
        for e in q['exams']:
            e = norm_exam(e)
            if e not in exams: exams.append(e)
        for e in q['uppsc_exams']:
            e = norm_exam(e)
            if e not in up: up.append(e)
    return exams, up
CH = {}; allf = []
for ch in range(1, 43):
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
                ex, up = meta(ch, ids); f = dict(ch=ch, cells=cells, text=' · '.join(c for c in cells if c), ids=ids, exams=ex, up=up); table['rows'].append(f); allf.append(f)
            continue
        table = None
        if l.startswith('@'): continue
        if l.startswith('## '):
            topic = dict(title=l[3:].strip(), items=[]); topics.append(topic)
        elif l.startswith('- '):
            if topic is None: topic = dict(title=TITLE[ch], items=[]); topics.append(topic)
            txt, ids = split_tag(l[2:].strip(), ch, f'ch{ch}:{ln}')
            ex, up = meta(ch, ids); f = dict(ch=ch, text=txt, ids=ids, exams=ex, up=up); topic['items'].append(('pt', f)); allf.append(f)
        elif l.startswith('! '):
            if topic is not None: topic['items'].append(('warn', l[2:].strip()))
        else: errors.append(f'ch{ch}:{ln}: unknown line {l[:50]}')
    CH[ch] = topics
ORDER = sorted(CH)
def pills(f):
    n = len(f['exams'])
    if not n: return ''
    o = f'<span class="p n" title="{esc("; ".join(f["exams"]))}">asked ×{n}</span>' if n > 1 else f'<span class="p o" title="{esc(f["exams"][0])}">asked</span>'
    if f['up']: o += f'<span class="p u" title="{esc("; ".join(f["up"]))}">UPPSC{" ×" + str(len(f["up"])) if len(f["up"]) > 1 else ""}</span>'
    return f'<span class="ps">{o}</span>'
cls = lambda f: 'f' + (' a' if f['exams'] else '') + (' hot' if len(f['exams']) >= 2 else '')
def render(ch, n):
    o = [f'<section class="view" id="c{ch}" data-title="{esc(TITLE[ch])}"><p class="eyebrow">Chapter {ch}</p><h2>{esc(TITLE[ch])}</h2>']
    fs = [f for f in allf if f['ch'] == ch]
    o.append(f'<p class="gist">{len(fs)} facts · {sum(1 for f in fs if len(f["exams"]) >= 2)} asked again and again · {sum(1 for f in fs if f["exams"])} asked at least once</p>')
    for ti, t in enumerate(CH[ch], 1):
        tid = f'c{ch}-t{ti}'
        o.append(f'<article class="topic" id="{tid}"><h3>{esc(t["title"])}</h3>'); buf = []
        def flush():
            if buf: o.append('<ul>' + ''.join(buf) + '</ul>'); buf.clear()
        for k, v in t['items']:
            if k == 'table':
                flush(); w = len(v['head']); rows = ''
                for f in v['rows']:
                    f['tid'] = tid; cells = (f['cells'] + [''] * w)[:w]
                    rows += f'<tr class="{cls(f)}">' + ''.join(f'<td>{inline(c)}</td>' for c in cells[:-1]) + f'<td>{inline(cells[-1])}{pills(f)}</td></tr>'
                o.append(f'<div class="tw"><table><thead><tr>{"".join("<th>" + inline(c) + "</th>" for c in v["head"])}</tr></thead><tbody>{rows}</tbody></table></div>')
            elif k == 'warn':
                flush(); o.append(f'<p class="warn"><b>Note from the book</b> {inline(v)}</p>')
            else:
                v['tid'] = tid; buf.append(f'<li class="{cls(v)}">{inline(v["text"])}{pills(v)}</li>')
        flush(); o.append('</article>')
    i = ORDER.index(ch)
    o.append('<nav class="pn">' + (f'<a href="#c{ORDER[i-1]}">← {esc(TITLE[ORDER[i-1]])}</a>' if i else '<a href="#home">← Start</a>') + (f'<a class="nx" href="#c{ORDER[i+1]}">{esc(TITLE[ORDER[i+1]])} →</a>' if i < len(ORDER) - 1 else '<a class="nx" href="#repeated">Most repeated →</a>') + '</nav></section>')
    return ''.join(o)
chapters = ''.join(render(ch, n) for n, ch in enumerate(ORDER))
rep = sorted([f for f in allf if len(f['exams']) >= 2], key=lambda f: (-len(f['exams']), -len(f['up']), f['ch']))
rep_html = ''.join(f'<li><details><summary><span class="t">{inline(f["text"])}</span>{pills(f)}</summary><div class="yrs">{esc("; ".join(f["exams"]))}<br><a href="#{f["tid"]}">Open in Chapter {f["ch"]}: {esc(TITLE[f["ch"]])} →</a></div></details></li>' for f in rep)
cnt = {ch: (sum(1 for f in allf if f['ch'] == ch), sum(1 for f in allf if f['ch'] == ch and len(f['exams']) >= 2)) for ch in ORDER}
home = ''.join(f'<li><a href="#c{ch}"><span class="no">{ch}</span><span class="nm">{esc(TITLE[ch])}</span><span class="q">{cnt[ch][0]} facts · {cnt[ch][1]} repeated</span></a></li>' for ch in ORDER)
side = ''.join(f'<a href="#c{ch}" data-v="c{ch}"><span>{ch}</span>{esc(TITLE[ch])}</a>' for ch in ORDER)
fonts = ''.join(re.findall(r'@font-face\{[^}]*\}', open('../polity/template_full_style.css', encoding='utf-8').read()))
css = fonts + ''':root{--ink:#1d1d1b;--mute:#666;--line:#e6e6e6;--soft:#f5f5f3;--acc:#1b6b4a;--hot:#fff3c4;--hotb:#e0a800;--up:#9a3412;--upbg:#fde9dc;--n:#7a5600;--nbg:#fbe6a8;--warn:#a2401c;--warnbg:#fdf0ea}
*{box-sizing:border-box}html{-webkit-text-size-adjust:100%;scroll-padding-top:70px}
body{margin:0;background:#fff;color:var(--ink);font:17px/1.55 "Atkinson Hyperlegible Next","Segoe UI",system-ui,Arial,"Nirmala UI",sans-serif}
a{color:inherit;text-decoration:none}button,input{font:inherit;color:inherit}:focus-visible{outline:2px solid var(--acc);outline-offset:2px}
h1,h2,h3,.brand{font-family:"Lexend","Segoe UI",system-ui,sans-serif;font-weight:600;letter-spacing:-.01em;line-height:1.25}
.top{position:sticky;top:0;z-index:20;display:flex;align-items:center;gap:12px;height:56px;padding:0 16px;background:#fff;border-bottom:1px solid var(--line)}
.brand{white-space:nowrap}#menu{display:none;width:40px;height:40px;background:none;border:1px solid var(--line);border-radius:8px;cursor:pointer;flex:none}
#q{flex:1;max-width:400px;margin-left:auto;height:38px;padding:0 12px;background:var(--soft);border:1px solid transparent;border-radius:8px;min-width:0}
.tog{display:flex;align-items:center;gap:7px;font-size:14px;white-space:nowrap;cursor:pointer;min-height:40px}.tog input{width:17px;height:17px;accent-color:var(--acc);margin:0}
.wrap{display:flex;max-width:1140px;margin:0 auto}
.side{position:sticky;top:56px;align-self:flex-start;flex:0 0 280px;height:calc(100vh - 56px);overflow-y:auto;padding:14px 10px 30px 14px;font-size:14.5px}
.side a{display:flex;gap:9px;padding:6px 10px;border-radius:7px;line-height:1.3}.side a span{color:var(--mute);min-width:18px;text-align:right}
.side a:hover{background:var(--soft)}.side a.on{background:var(--soft);font-weight:600;color:var(--acc)}.side .hl{color:var(--n);font-weight:600}
.side .lb{margin:14px 10px 4px;font-size:12px;color:var(--mute);font-weight:600}
main{flex:1;min-width:0;max-width:790px;padding:28px 24px 90px}.view{display:none}.view.on{display:block}
h1,h2{font-size:28px;margin:0 0 6px}h3{font-size:18px;margin:24px 0 6px}.eyebrow{margin:0 0 4px;font-size:13px;color:var(--mute)}.gist{margin:0 0 14px;color:var(--mute)}
ul,ol.rows,ol.toc{margin:0;padding:0;list-style:none}
li.f,td,th,.warn,.rows .t,h2,h3{overflow-wrap:anywhere}
li.f{position:relative;padding:4px 8px 4px 22px;border-radius:6px;line-height:1.45}
li.f::before{content:"";position:absolute;left:9px;top:14px;width:5px;height:5px;border-radius:50%;background:#999}
li.hot,tr.hot td{background:var(--hot)}li.hot{margin:2px 0}li.hot::before{background:var(--hotb)}
.ps{display:inline-flex;gap:4px;margin-left:7px;vertical-align:1px}
.p{display:inline-block;padding:0 6px;border-radius:5px;font-size:11.5px;line-height:18px;font-weight:600;white-space:nowrap}
.p.n{background:var(--nbg);color:var(--n)}.p.o{background:var(--soft);color:var(--mute)}.p.u{background:var(--upbg);color:var(--up)}
.warn{margin:6px 0;padding:7px 11px;background:var(--warnbg);color:var(--warn);border-radius:6px;font-size:14.5px;line-height:1.4}
.tw{overflow-x:auto;margin:8px 0;border:1px solid var(--line);border-radius:8px}table{width:100%;border-collapse:collapse;font-size:14.5px;line-height:1.35}
th{text-align:left;font-size:12.5px;color:var(--mute);background:var(--soft)}th,td{padding:7px 10px;border-top:1px solid var(--line);vertical-align:top}tr:first-child th{border-top:0}
.legend{display:flex;flex-wrap:wrap;align-items:center;gap:6px 10px;margin:0 0 18px;font-size:14px;color:var(--mute)}.key{display:inline-block;width:18px;height:14px;background:var(--hot);border:1px solid var(--hotb);border-radius:3px}
.cta{display:block;margin:0 0 20px;padding:13px 15px;background:var(--nbg);color:var(--n);border-radius:10px;font-weight:600}
.toc{border-top:1px solid var(--line)}.toc a{display:flex;align-items:center;gap:10px;padding:11px 4px;border-bottom:1px solid var(--line)}.toc .no{width:22px;color:var(--mute);font-size:14px}.toc .nm{flex:1;font-weight:600}.toc .q{font-size:13px;color:var(--mute);white-space:nowrap}
.rows{counter-reset:r;border-top:1px solid var(--line)}.rows li{counter-increment:r;border-bottom:1px solid var(--line)}
.rows summary{display:flex;flex-wrap:wrap;align-items:baseline;gap:6px 10px;padding:9px 2px;cursor:pointer;list-style:none;line-height:1.4}.rows summary::-webkit-details-marker{display:none}
.rows summary::before{content:counter(r);min-width:24px;color:var(--mute);font-size:13px}.rows .t{flex:1;min-width:200px}.rows .ps{margin:0}
.yrs{padding:0 0 11px 34px;font-size:13.5px;color:var(--mute);line-height:1.5}.yrs a{color:var(--acc);font-weight:600}
.pn{display:flex;justify-content:space-between;gap:16px;margin-top:34px;padding-top:16px;border-top:1px solid var(--line);font-size:14.5px;color:var(--acc);font-weight:600}.pn .nx{text-align:right}
.foot{margin-top:20px;font-size:13.5px;color:var(--mute)}.res a{display:block;padding:9px 2px;border-bottom:1px solid var(--line)}.res small{display:block;color:var(--mute);font-size:12.5px}mark{background:var(--hotb)}
.flash{animation:fl 1.8s ease-out}@keyframes fl{0%,40%{box-shadow:0 0 0 2px var(--acc)}100%{box-shadow:0 0 0 2px transparent}}
body.rep li.f:not(.hot),body.rep tr.f:not(.hot),body.rep .warn{display:none}body.rep .topic.empty{display:none}body.rep .tw.empty{display:none}
#scrim{display:none}
@media (max-width:860px){#menu{display:inline-flex;align-items:center;justify-content:center}.brand{display:none}#q{margin-left:0}
.side{position:fixed;z-index:40;left:0;top:0;width:285px;height:100%;background:#fff;border-right:1px solid var(--line);transform:translateX(-100%);transition:transform .18s}.side.open{transform:none}
#scrim.on{display:block;position:fixed;inset:0;z-index:30;background:rgba(0,0,0,.4)}main{padding:20px 16px 80px}h1,h2{font-size:24px}.toc .q{display:none}}
@media print{.top,.side,.pn,#scrim{display:none!important}.view{display:block!important;break-before:page}main{max-width:none;padding:0}}'''
js = r'''(function(){var $=function(s,r){return(r||document).querySelector(s)},$$=function(s,r){return[].slice.call((r||document).querySelectorAll(s))};
var side=$("#side"),scrim=$("#scrim"),q=$("#q"),only=$("#only"),last="home",idx=null;
function drawer(o){side.classList.toggle("open",o);scrim.classList.toggle("on",o)}
function show(id){$$(".view").forEach(function(v){v.classList.toggle("on",v.id===id)});$$(".side a").forEach(function(a){a.classList.toggle("on",a.dataset.v===id)});if(id!=="results")last=id;
 var v=$("#"+id);document.title=(v&&v.dataset.title?v.dataset.title+" · ":"")+"Polity-UPPCS"}
function mark(){$$(".topic").forEach(function(t){t.classList.toggle("empty",!$(".f.hot",t))});$$(".tw").forEach(function(t){t.classList.toggle("empty",!$("tr.hot",t))})}
function apply(){document.body.classList.toggle("rep",only.checked);try{localStorage.setItem("polity-uppcs-rep",only.checked?"1":"0")}catch(e){}}
function route(){var h=decodeURIComponent(location.hash.slice(1))||"home",el=document.getElementById(h);if(!el){h="home";el=document.getElementById(h)}
 var v=el.classList.contains("view")?el:el.closest(".view");q.value="";show(v.id);drawer(false);
 if(el===v)window.scrollTo(0,0);else{el.scrollIntoView();el.classList.add("flash");setTimeout(function(){el.classList.remove("flash")},1900)}}
q.addEventListener("input",function(){var s=q.value.trim().toLowerCase();if(s.length<2){show(last);return}
 if(!idx){idx=[];$$(".view[id^=c]").forEach(function(v){$$(".f",v).forEach(function(p){var c=p.cloneNode(true);$$(".ps",c).forEach(function(x){x.remove()});
  var t=(p.tagName==="TR"?$$("td",c).map(function(d){return d.textContent}).join(" · "):c.textContent).replace(/\s+/g," ").trim();idx.push({el:p,t:t,l:t.toLowerCase(),w:v.dataset.title,hot:p.classList.contains("hot")})})})}
 var w=s.split(/\s+/),hits=idx.filter(function(x){return w.every(function(k){return x.l.indexOf(k)>=0})});hits.sort(function(a,b){return(b.hot?1:0)-(a.hot?1:0)});hits=hits.slice(0,80);
 $("#rt").textContent=hits.length+(hits.length===80?"+":"")+" results";var L=$("#rl");L._h=hits;
 L.innerHTML=hits.map(function(x,i){return'<a href="#" data-i="'+i+'">'+x.t.replace(/[&<>]/g,function(c){return{"&":"&amp;","<":"&lt;",">":"&gt;"}[c]})+"<small>"+x.w+"</small></a>"}).join("")||"<p>Nothing found. Try one word.</p>";show("results");window.scrollTo(0,0)});
$("#rl").addEventListener("click",function(e){var a=e.target.closest("a");if(!a)return;e.preventDefault();var x=this._h[+a.dataset.i];if(only.checked&&!x.hot){only.checked=false;apply()}
 q.value="";var v=x.el.closest(".view");show(v.id);history.replaceState(null,"","#"+v.id);x.el.scrollIntoView({block:"center"});x.el.classList.add("flash");setTimeout(function(){x.el.classList.remove("flash")},1900)});
$("#menu").onclick=function(){drawer(!side.classList.contains("open"))};scrim.onclick=function(){drawer(false)};only.onchange=apply;
window.addEventListener("hashchange",route);try{only.checked=localStorage.getItem("polity-uppcs-rep")==="1"}catch(e){}mark();apply();route()})();'''
page = f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Polity-UPPCS</title><meta name="description" content="Indian Polity for UPPCS: every fact of every chapter in one list, with repeatedly asked facts highlighted.">
<style>{css}</style></head><body>
<header class="top"><button id="menu" aria-label="Open chapter list">☰</button><a class="brand" href="#home">Polity-UPPCS</a>
<input id="q" type="search" placeholder="Search facts" aria-label="Search facts" autocomplete="off"><label class="tog"><input id="only" type="checkbox"><span>Repeated only</span></label></header>
<div class="wrap"><nav class="side" id="side" aria-label="Chapters"><a href="#home" data-v="home"><span></span>Start</a><a href="#repeated" data-v="repeated" class="hl"><span></span>Most repeated</a><div class="lb">Chapters</div>{side}</nav>
<main>
<section class="view" id="home"><h1>Polity-UPPCS</h1>
<p class="gist">Every fact of every chapter in one list, for one-pass revision. Facts asked again and again are highlighted.</p>
<p class="legend"><span class="key"></span>asked in 2 or more papers <span class="p n">asked ×4</span> number of papers <span class="p u">UPPSC ×2</span> of which UPPSC papers <span class="p o">asked</span> asked once</p>
<a class="cta" href="#repeated">Start with the {len(rep)} facts asked again and again →</a>
<ol class="toc">{home}</ol>
<p class="foot">{len(allf)} facts from all {len(ORDER)} chapters of Ghatna Chakra Preview Indian Polity and Governance 2026: its explanation paragraphs, its {len(A)} solved questions and their explanations. Nothing from outside the book is added; "Note from the book" lines repeat the book's own remarks on doubtful or dated keys. Hover or long-press a tag to see the exams and years.</p></section>
<section class="view" id="repeated" data-title="Most repeated"><h2>Most repeated</h2><p class="gist">{len(rep)} facts asked in two or more papers, most-asked first. Tap a row for exams and years.</p><ol class="rows">{rep_html}</ol></section>
{chapters}
<section class="view" id="results" data-title="Search"><h2 id="rt">Search</h2><div id="rl" class="res"></div></section>
</main></div><div id="scrim"></div><script>{js}</script></body></html>'''
open(OUT, 'w', encoding='utf-8').write(page)
tagged = {(f['ch'], i) for f in allf for i in f['ids']}
scorable = {k for k, q in QI.items() if q['k'] and not q['review'] and k[0] in CH}
print('chapters', len(ORDER), 'facts', len(allf), 'asked', sum(bool(f['exams']) for f in allf), 'repeated', len(rep), 'size', os.path.getsize(OUT))
print('questions tagged', len(tagged & scorable), 'of', len(scorable), 'errors', len(errors), errors[:6])
