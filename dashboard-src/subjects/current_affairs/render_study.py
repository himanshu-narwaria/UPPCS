"""Shared renderer for full notes, concise revision and a real 72-session plan."""
import html
import json
import math
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OUT = ROOT / "Drishti-current affairs"
FULL = "current-uppsc-full-notes.html"
QUICK = "current-uppsc-quick-notes.html"
PLAN = "current-in-72h.html"
E = html.escape
CONTEXT = "These notes follow the supplied Drishti 2026 (2) issue. Events, rankings, results and figures retain that issue's dates; this is not a live news feed. Page references mean PDF file pages, one higher than the printed number."

def load(name):
    return json.loads((HERE / name).read_text(encoding="utf-8"))

def refs(pages):
    return '<span class="src">PDF p. '+', '.join(str(p) for p in pages)+'</span>'

def metadata(chapters, questions, priority):
    return dict(question_kind="source-practice", practice_questions=len(questions), verified_uppsc_pyqs=0,
        verified_repeated_facts=0, priority_facts=len(priority), source_pdf_pages=241, source_content_pages=238,
        guided_facts=sum(len(c["learning"]["points"]) for c in chapters),
        recall_questions=sum(len(c["learning"]["recall"]) for c in chapters),
        source_blocks=sum(len(t["points"]) for c in chapters for t in c["topics"]),
        chapter_practice_counts={f"c{c['num']}":sum(q["ch"]==f"c{c['num']}" for q in questions.values()) for c in chapters},
        context="Supplied 2026 (2) PDF; no verified UPPSC papers or live updates added")

def assets():
    return ((HERE / "fonts_embedded.css").read_text(encoding="utf-8")+'\n'+
            (HERE / "study_styles.css").read_text(encoding="utf-8"),
            (HERE / "study_runtime.js").read_text(encoding="utf-8"))

def shell_start(title, mode="full"):
    css, _ = assets()
    search = '<input id="q" type="search" aria-label="Search notes" placeholder="Search a name, place or idea" autocomplete="off">' if mode != "plan" else '<span id="prog" class="prog">0 of 72 hours done</span>'
    only = '<label class="tog"><input id="only" type="checkbox"> Guide only</label>' if mode=="full" else ''
    return [f'<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{E(title)}</title><meta name="description" content="Page-referenced Drishti 2026 study notes, explained recall and honest source practice for UPPSC revision."><style>{css}</style></head><body>',
        '<header class="top" id="top"><button id="menu" type="button" aria-label="Open contents" aria-expanded="false" aria-controls="side">☰</button><a class="brand" href="#home">Drishti · Learn &amp; recall</a>'+search+only+'<label class="tog"><input id="dark" type="checkbox"> Dark</label></header>',
        '<div class="progress-track"><i id="bar"></i></div>' if mode=="plan" else '', '<div class="wrap">']

def close(out, meta, questions=None):
    _, js=assets()
    out += ['</main></div><div id="scrim"></div>', '<script id="study-meta" type="application/json">'+json.dumps(meta,ensure_ascii=False).replace('</',r'<\/')+'</script>']
    if questions is not None:
        out.append('<script id="pqd" type="application/json">'+json.dumps(questions,ensure_ascii=False).replace('</',r'<\/')+'</script>')
    out += ['<script>'+js+'</script></body></html>']
    return '\n'.join(out)

def chapter_nav(chapters, mode):
    out=['<nav class="side" id="side" aria-label="Contents"><a href="#home" data-v="home">Start here</a><a href="#repeated" data-v="repeated">Priority revision</a>']
    if mode=="full":
        out += ['<a href="#latest" data-v="latest">Source context &amp; checks</a><a href="#practice" data-v="practice">Source practice · 40</a>']
    out.append('<div class="lb">Chapters</div>')
    out += [f'<a href="#c{c["num"]}" data-v="c{c["num"]}"><span>{c["num"]}</span>{E(c["title"])}</a>' for c in chapters]
    out.append('</nav><main>')
    return out

def comparison(data):
    out=['<div class="table-scroll"><table><caption>'+E(data['title'])+'</caption><thead><tr>']
    out += ['<th scope="col">'+E(x)+'</th>' for x in data['headers']]
    out.append('</tr></thead><tbody>')
    for row in data['rows']:
        out.append('<tr>'+''.join('<td>'+E(x)+'</td>' for x in row)+'</tr>')
    out.append('</tbody></table></div>'+refs(data['pages']))
    return ''.join(out)

def recall(data, indexes=None):
    rows = data['recall'] if indexes is None else [data['recall'][i] for i in indexes]
    return ''.join('<details class="recall"><summary>'+E(q)+'</summary><div class="answer"><p>'+E(a)+refs(p)+'</p></div></details>' for q,a,p in rows)

def guide(c, quick=False):
    n=c['num']; d=c['learning']
    out=[f'<article class="topic guided" id="c{n}-t1"><h3>Build the chapter in eight anchors</h3><div class="guide-grid">']
    for label,text,pages in d['points']:
        out.append('<div class="fact pt asked"><b>'+E(label)+'</b><p>'+E(text)+'</p>'+refs(pages)+'</div>')
    out += ['</div>',comparison(d['comparison']),'<div class="note"><b>Learning aid - not from source</b>'+E(d['aid'])+'</div>', '<h4>Close the notes. Explain it back.</h4>',recall(d),'</article>']
    for flag in d['checks']:
        out.append('<div class="warn"><b>Source check.</b> '+E(flag['text'])+refs(flag['pages'])+'</div>')
    if quick:
        out.append(f'<a class="btn" href="{FULL}#c{n}">Read the chapter and source evidence →</a>')
    else:
        out.append(f'<a class="btn" href="#practice" data-practice-ch="c{n}">Try this chapter’s four source MCQs →</a>')
    return out

def source_evidence(c):
    out=['<details class="source-wrap"><summary>Explore all source topics · PDF pp. '+str(c['start_page'])+'-'+str(c['end_page'])+'</summary>',
         '<p class="context">This supporting layer retains extracted source text under its actual headings. Short answers and table text are retained. Complex maps and tables still need the original PDF for visual relationships; this layer is not a certification of every diagram or source claim.</p><ul class="source-index">']
    for t in c['topics']:
        out.append('<li><a href="#'+t['id']+'">'+E(t['title'])+' <small>p. '+str(t['page_start'])+'</small></a></li>')
    out.append('</ul>')
    for t in c['topics']:
        out.append('<article class="topic source-topic" id="'+t['id']+'" data-pages="'+str(t['page_start'])+'-'+str(t['page_end'])+'"><h3>'+E(t['title'])+refs(range(t['page_start'],t['page_end']+1))+'</h3><ul>')
        for p in t['points']:
            out.append('<li class="pt" data-page="'+str(p['page'])+'">'+E(p['text'])+refs(p['pages'])+'</li>')
        out.append('</ul></article>')
    out.append('</details>')
    return out

def questions_block(ids, bank=False, mock=None):
    return '<div class="question-set"><p class="score" aria-live="polite"></p><ol class="pq"'+(' id="pqList"' if bank else '')+(f' data-mock="{mock}"' if mock else '')+' data-q="'+','.join(ids)+'"></ol>'+('<div class="pq-controls"><button type="button" data-submit-mock>Submit mock and review</button><button type="button" data-reset-mock>Start a fresh attempt</button></div>' if mock else '')+'</div>'

def build_notes(mode):
    chapters=load('structured_all_chapters.json'); questions=load('parsed_uppsc_questions.json');priority=load('priority_facts.json')
    quick=mode=='quick'; title='Current Affairs Quick Revision' if quick else 'Current Affairs Full Notes'
    meta=metadata(chapters,questions,priority);out=shell_start(title,mode)+chapter_nav(chapters,mode)
    out += [f'<section class="view" id="home" data-title="{title}"><p class="eyebrow">Read → connect → recall</p><h1>{title}</h1>',
        '<p class="gist">Learn the idea behind the headline, attach the right date and unit, then test your memory. Ten chapters follow the source book’s order.</p>',
        '<div class="context">'+E(CONTEXT)+'</div><div class="stats"><span>80 guided facts</span><span>50 explained recall prompts</span><span>40 source-practice MCQs</span><span>238 content pages mapped</span></div>',
        '<p>Use each chapter’s eight anchors and comparison first. Reveal the recall answers only after explaining them aloud.'+(' The full notes hold the supporting source evidence for every content page.' if quick else ' Open the supporting source topics when you need detail, a list or a date check.')+'</p>',
        '<a class="cta" href="#c1">Begin with Points to Remember →</a><ol class="toc">']
    for c in chapters:
        n=c['num']; k=meta['chapter_practice_counts'][f'c{n}']
        out.append(f'<li><a href="#c{n}"><span class="no">{n}</span><span class="nm">{E(c["title"])}</span><span class="q">{k} practice questions</span></a></li>')
    out += ['</ol><p class="foot">Based on 40 source practice questions and 80 editorial priority facts from the supplied Drishti 2026 (2) PDF. No verified UPPSC PYQs or exam-repeat counts are claimed. The full notes retain page-referenced source evidence; the quick view is a selective learning and revision guide.</p>',
        f'<p><a href="{FULL if quick else QUICK}#home">'+('Open full notes' if quick else 'Open quick revision')+f'</a> · <a href="{PLAN}#home">Open the 72-hour plan</a></p></section>',
        '<section class="view" id="repeated" data-title="Priority revision"><h2>Priority revision</h2><p class="gist">A balanced editorial selection for learning. These are not verified repeats from past UPPSC papers.</p><h3 id="rep-facts" class="sec">80 priority facts from the source</h3><ol class="rows">']
    for p in priority:
        out.append('<li><details><summary><span class="t">'+E(p['label'])+': '+E(p['fact'])+'</span></summary><div class="yrs">'+refs(p['pages'])+'<a href="#'+p['anchor']+'">Connect this with the chapter →</a></div></details></li>')
    out.append('</ol></section>')
    if not quick:
        out += ['<section class="view" id="latest" data-title="Source context and checks"><h2>Source context &amp; checks</h2><p class="gist">The issue’s own context is preserved. No live 2026 update or official UPPSC key has been added.</p><div class="context">'+E(CONTEXT)+'</div>',
            '<p>The source is a 241-page PDF: page 1 is a cover/watermark; pages 2-3 are index/editorial matter; pages 4-241 are mapped to ten chapters. Its original file is left unchanged. Source evidence preserves text; maps, illustrations and overlapping table cells may still require the original file.</p>']
        for c in chapters:
            for flag in c['learning']['checks']:
                out.append('<div class="warn"><b>'+E(c['title'])+'.</b> '+E(flag['text'])+refs(flag['pages'])+'</div>')
        out += ['</section><section class="view" id="practice" data-title="Source practice"><h2>Source practice</h2><p class="gist">40 editorial MCQs based on cited PDF pages. These are not past UPPSC questions, and the answers are not official exam keys. Explanations tell you which distinction matters.</p><div class="pq-controls"><label for="pqCh">Chapter</label><select id="pqCh"><option value="">All chapters</option>']
        out += [f'<option value="c{c["num"]}">{E(c["title"])}</option>' for c in chapters]
        out += ['</select><button type="button" id="pqReset">Reset practice</button></div>',questions_block(list(questions),bank=True),'</section>']
    for i,c in enumerate(chapters):
        n=c['num'];d=c['learning']
        out += [f'<section class="view ch" id="c{n}" data-title="{E(c["title"],quote=True)}"><p class="eyebrow">Chapter {n} · PDF pp. {c["start_page"]}-{c["end_page"]}</p><h2>{E(c["title"])}</h2><p class="gist">{E(d["intro"])}</p><ol class="reading-route">']
        out += ['<li>'+E(x)+'</li>' for x in d['route']]
        out += ['</ol>']+guide(c,quick)
        if not quick:out += source_evidence(c)
        prev='#c'+str(n-1) if n>1 else '#home';nx='#c'+str(n+1) if n<10 else '#home'
        out += [f'<nav class="pn"><a href="{prev}">← '+(E(chapters[i-1]['title']) if n>1 else 'Start')+f'</a><a href="{nx}">'+(E(chapters[i+1]['title']) if n<10 else 'Start')+' →</a></nav></section>']
    out.append('<section class="view" id="results" data-title="Search"><h2 id="rt">Search</h2><ul class="res" id="rl"></ul></section>')
    target=OUT/(QUICK if quick else FULL);target.write_text(close(out,meta,None if quick else questions),encoding='utf-8')
    print(f'Generated {target.name}: 10 chapters, 80 guided facts, 50 recalls, '+('source evidence + 40 MCQs' if not quick else 'selective revision'))

def build_plan():
    chapters=load('structured_all_chapters.json');questions=load('parsed_uppsc_questions.json');priority=load('priority_facts.json');meta=metadata(chapters,questions,priority)
    counts=[3,8,8,8,5,3,3,2,9,5]
    sessions=[]
    for c,parts in zip(chapters,counts):
        pages=list(range(c['start_page'],c['end_page']+1))
        for part in range(parts):
            chunk=pages[part*len(pages)//parts:(part+1)*len(pages)//parts]
            sessions.append(dict(n=len(sessions)+1,phase='Learn',title=c['title']+f' · part {part+1} of {parts}',chapter=c,pages=chunk,part=part,parts=parts))
    assert len(sessions)==54
    for c in chapters:
        sessions.append(dict(n=len(sessions)+1,phase='Revise',title='Revise: '+c['title'],chapter=c,pages=[],part=0,parts=1))
    groups=[([1,2,3],'National and international connections'),([4,6],'Economic measures and environment'),([5,7,8],'Technology and State comparisons'),([9,10],'Names, books, events and sports')]
    for nums,title in groups:
        sessions.append(dict(n=len(sessions)+1,phase='Test',title='Practice drill: '+title,chapters=nums))
    keys=list(questions)
    for j in range(4):
        # Interleave chapters so all four mocks are mixed, with no duplicate within the four mocks.
        ids=[keys[k] for k in range(j,len(keys),4)]
        sessions.append(dict(n=len(sessions)+1,phase='Test',title=f'Timed mock {j+1}: ten mixed source questions',ids=ids))
    assert len(sessions)==72
    meta['learn_hours']=54;meta['revise_hours']=10;meta['drill_hours']=4;meta['timed_mocks']=4
    out=shell_start('Current Affairs in 72h','plan')
    out.append('<nav class="side" id="side" aria-label="72-hour schedule"><a href="#home" data-v="home">Start here</a>')
    phase=None
    for s in sessions:
        if s['phase']!=phase:
            phase=s['phase'];out.append('<div class="lb">'+phase+'</div>')
        out.append(f'<a href="#h{s["n"]}" data-v="h{s["n"]}"><span>{s["n"]}</span>{E(s["title"])}</a>')
    out += ['</nav><main><section class="view" id="home" data-title="72-hour plan"><p class="eyebrow">54 learn · 10 revise · 4 drills · 4 timed mocks</p><h1>Current Affairs in 72h</h1><p class="gist">72 hours before 6 December 2026: work through the supplied issue with distinct reading ranges, retrieval practice and review.</p><div class="context">'+E(CONTEXT)+'</div><p>Each learn hour has its own source pages and topics. Spend 10 minutes orienting, 25 reading, 15 recalling without the notes and 10 checking mistakes. Mocks contain ten source-practice questions each: 12 minutes to answer, then use the rest of the hour to explain errors.</p><a class="cta" id="cont" href="#h1">Begin hour 1 →</a><ol class="toc">']
    for s in sessions:
        out.append(f'<li><a href="#h{s["n"]}"><span class="no">{s["n"]}</span><span class="nm">{E(s["title"])}</span><span class="q">'+(f'PDF pp. {s["pages"][0]}-{s["pages"][-1]}' if s.get('pages') else s['phase'])+'</span></a></li>')
    out.append('</ol><p class="foot">40 original source-practice MCQs, reused in learning and drills; four mixed mocks partition those 40 questions without duplication between mocks. No verified UPPSC PYQs, official keys or exam predictions are claimed.</p></section>')
    for s in sessions:
        n=s['n'];out += [f'<section class="view" id="h{n}" data-n="{n}" data-title="{E(s["title"],quote=True)}"><p class="eyebrow">Hour {n} of 72 · {s["phase"]}</p><h2>{E(s["title"])}</h2>']
        if s['phase']=='Learn':
            c=s['chapter'];pages=s['pages'];topics=[t for t in c['topics'] if any(p['page'] in pages for p in t['points']) or any(p in pages for p in t['heading_pages'])]
            out += [f'<p class="gist">Read PDF pp. {pages[0]}-{pages[-1]}. Link each headline to its purpose, place, date and source qualification.</p>',f'<p><a class="btn" href="{FULL}#c{c["num"]}">Open chapter guide</a></p><h3>This hour’s source topics</h3><ul class="session-topics">']
            for t in topics:out.append(f'<li><a href="{FULL}#{t["id"]}">{E(t["title"])}</a> <small>PDF p. {t["page_start"]}</small></li>')
            out.append('</ul><h3>Read, then reconstruct</h3>')
            pts=[(t,p) for t in topics for p in t['points'] if p['page'] in pages]
            # Distinct starting excerpts for this actual page range, not a repeated chapter sample.
            for t,p in pts[::max(1,len(pts)//4)][:4]:
                out.append('<div class="fact pt"><b>'+E(t['title'])+'</b><p>'+E(p['text'])+'</p>'+refs(p['pages'])+'</div>')
            out.append('<div class="note"><b>Retrieve before checking</b>Choose three of the named topics above. For each, write the central development and one precise date, place or number from this reading range. Reopen its page reference and correct any missing qualification.</div>')
            ids=[i for i,q in questions.items() if q['ch']==f'c{c["num"]}' and q['page'] in pages]
            if ids:out += ['<h3>Source practice for these pages</h3>',questions_block(ids)]
        elif s['phase']=='Revise':
            c=s['chapter'];out += ['<p class="gist">Use 15 minutes to recreate the comparison, 25 to answer these prompts without looking and 20 to correct your weak links.</p>',comparison(c['learning']['comparison']),recall(c['learning']),f'<p><a class="btn" href="{QUICK}#c{c["num"]}">Check the eight revision anchors →</a></p>']
        else:
            ids=s.get('ids') or [i for i,q in questions.items() if int(q['ch'][1:]) in s['chapters']]
            if 'ids' in s:out.append('<p class="gist">Ten mixed source questions. Answer for 12 minutes, then submit to review every explanation. Each mock starts with a fresh answer sheet; your learning-bank answers are kept separately. These are editorial practice, not a past UPPSC paper.</p><div class="timebox" data-seconds="720"><button type="button" data-start-timer>Start 12-minute timer</button><output class="timer-readout" aria-live="polite">12:00</output></div>')
            else:out.append('<p class="gist">Spend 20 minutes answering and 40 minutes explaining why the other options do not match the cited source. Questions are reused from the 40-question learning bank.</p>')
            out.append(questions_block(ids,mock=f'h{n}' if 'ids' in s else None))
        nx=f'#h{n+1}' if n<72 else '#home';prev=f'#h{n-1}' if n>1 else '#home'
        out.append(f'<div class="done"><button type="button" class="btn" data-done="{n}" aria-pressed="false">Mark hour {n} done</button><a class="btn nx" href="{nx}">'+(f'Hour {n+1} →' if n<72 else 'Finish and review →')+f'</a></div><nav class="pn"><a href="{prev}">← Previous</a><a class="nx" href="{nx}">Next →</a></nav></section>')
    (OUT/PLAN).write_text(close(out,meta,questions),encoding='utf-8')
    (HERE/'session_plan.json').write_text(json.dumps([dict(hour=s['n'],title=s['title'],phase=s['phase'],pages=s.get('pages',[]),question_ids=s.get('ids',[])) for s in sessions],ensure_ascii=False,indent=2),encoding='utf-8')
    print('Generated current-in-72h.html: 54 distinct learn ranges, 10 revision hours, 4 drills and 4 timed ten-question mocks.')
