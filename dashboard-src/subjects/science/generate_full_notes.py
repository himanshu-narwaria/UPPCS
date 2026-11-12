import json
import re
import os
import html

def generate_full_notes():
    base_dir = os.path.join("dashboard-src", "subjects", "science")
    with open(os.path.join(base_dir, "structured_all_chapters.json"), encoding="utf-8") as f:
        chapters = json.load(f)
    with open(os.path.join(base_dir, "parsed_uppsc_questions.json"), encoding="utf-8") as f:
        qs = json.load(f)
    with open(os.path.join(base_dir, "repeated_facts.json"), encoding="utf-8") as f:
        repeats = json.load(f)
    with open(os.path.join(base_dir, "latest_facts.json"), encoding="utf-8") as f:
        latest = json.load(f)
    with open(os.path.join(base_dir, "template_full_style.css"), encoding="utf-8") as f:
        css = f.read()
    with open(os.path.join(base_dir, "template_full_js.html"), encoding="utf-8") as f:
        js = f.read()

    # Question count per chapter
    ch_q_count = {}
    for qid, q in qs.items():
        ch_n = int(q["ch"][1:])
        ch_q_count[ch_n] = ch_q_count.get(ch_n, 0) + 1

    out = []
    out.append('<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">')
    out.append('<title>General Science Full Notes</title>')
    out.append('<meta name="description" content="General Science for UPPCS: all 65 chapters in short points, tagged by UPPSC previous-year papers.">')
    out.append(f'<style>{css}</style></head><body>')
    
    # Header
    out.append('<header class="top" id="top">')
    out.append('<button id="menu" aria-label="Open contents">☰</button>')
    out.append('<a class="brand" href="#home">General Science</a>')
    out.append(f'<input id="q" type="search" placeholder="Search 65 chapters, {len(qs)} UPPSC questions…" aria-label="Search notes" autocomplete="off">')
    out.append('<label class="tog"><input id="only" type="checkbox"> Important</label>')
    out.append('<label class="tog"><input id="dark" type="checkbox"> Dark</label>')
    out.append('</header>')
    
    out.append('<div class="wrap">')
    
    # Sidebar
    out.append('<nav class="side" id="side" aria-label="Chapters">')
    out.append('<a href="#home" class="on"><span></span>Contents</a>')
    out.append(f'<a href="#repeated" class="hl"><span>★</span>Most repeated ({len(repeats)})</a>')
    out.append('<a href="#latest" class="hl"><span>⚡</span>Latest UPPSC (2021–25)</a>')
    out.append(f'<a href="#practice" class="hl"><span>✎</span>Practice ({len(qs)} MCQs)</a>')
    out.append('<div class="lb">Part I · Physics</div>')
    for c in chapters:
        num = c["num"]
        if num == 18:
            out.append('<div class="lb">Part II · Chemistry</div>')
        elif num == 37:
            out.append('<div class="lb">Part III · Biology</div>')
        out.append(f'<a href="#c{num}"><span>{num}</span>{html.escape(c["title"])}</a>')
    out.append('</nav>')
    
    out.append('<main>')
    
    # Home view
    out.append('<section class="view" id="home"><h1>General Science for UPPSC</h1>')
    out.append('<p class="gist">All 65 chapters in short points, tagged by what UPPSC has actually asked.</p>')
    out.append('<p class="legend"><span class="key"></span>Asked in 2 or more UPPSC papers <span class="p up">UPPSC ×3</span> asked in 3 UPPSC papers <span class="p up">UPPSC</span> asked once</p>')
    out.append(f'<a class="cta" href="#repeated">Short on time? Start with the {len(repeats)} facts UPPSC repeats →</a>')
    out.append('<ol class="toc">')
    for c in chapters:
        num = c["num"]
        title = html.escape(c["title"])
        k = ch_q_count.get(num, 0)
        hot_badge = '<span class="p up">Most asked</span>' if k >= 40 else ''
        out.append(f'<li><a href="#c{num}"><span class="no">{num}</span><span class="nm">{title}</span>{hot_badge}<span class="q">{k} UPPSC PYQs</span></a></li>')
    out.append('</ol>')
    out.append(f'<p class="foot">{len(chapters)} chapters and {len(qs)} UPPSC questions (PCS Pre and Mains, RO/ARO, Lower Subordinate, UDA/LDA, GIC, BEO, RI; up to 2025) from Ghatna Chakra Preview General Science 2026. Facts and answers are as in the book; Check lines mark doubtful keys. Past repeats guide revision and do not predict a paper.</p>')
    out.append('</section>')
    
    # Repeated view
    out.append('<section class="view" id="repeated" data-title="Most repeated">')
    out.append('<h2>Most repeated</h2>')
    out.append(f'<p class="gist">{len(repeats)} facts asked in two or more UPPSC papers, most-asked first. Tap a row to see exams and years.</p>')
    out.append('<ol class="rows">')
    for r in repeats:
        f_esc = r["fact"]
        p_esc = html.escape(r["papers"])
        anc = r["anchor"]
        cnt = r["count"]
        out.append(f'<li><details><summary><span class="t">{f_esc}</span><span class="ps"><span class="p up">×{cnt}</span></span></summary><div class="yrs"><div>{p_esc}</div><a href="#{anc}">Open in chapter →</a></div></details></li>')
    out.append('</ol>')
    out.append('</section>')
    
    # Latest view
    out.append('<section class="view" id="latest" data-title="Latest UPPSC">')
    out.append('<h2>Latest UPPSC, 2021–25</h2>')
    out.append('<p class="gist">Facts asked in the newest UPPSC papers, newest year first.</p>')
    out.append('<div class="new">')
    for yr in sorted(latest.keys(), reverse=True):
        out.append(f'<h4>UPPSC {yr}</h4><ul>')
        for item in latest[yr]:
            f_esc = item["fact"]
            cnt_str = f' <span class="p up">×{item["count"]}</span>' if item["count"] > 1 else ''
            anc = item["anchor"]
            out.append(f'<li>{f_esc}{cnt_str} <a class="to" href="#{anc}" aria-label="Open in chapter">→</a></li>')
        out.append('</ul>')
    out.append('</div>')
    out.append('</section>')
    
    # Practice view
    out.append('<section class="view" id="practice" data-title="UPPSC PYQ practice">')
    out.append('<h2>UPPSC PYQ practice</h2>')
    out.append(f'<p class="gist">{len(qs)} real UPPSC questions with the book\'s answer key. Pick an option to check it; each answer shows the fact tested and a link to its note.</p>')
    out.append('<div class="pq-bar"><label>Chapter <select id="pqCh">')
    out.append(f'<option value="">All chapters ({len(qs)})</option>')
    for c in chapters:
        num = c["num"]
        out.append(f'<option value="c{num}">{num}. {html.escape(c["title"])} ({ch_q_count.get(num, 0)})</option>')
    out.append('</select></label>')
    out.append('<label>Years <select id="pqYr"><option value="0">All years</option><option value="2015">2015 onwards</option><option value="2020">2020 onwards</option></select></label>')
    out.append('<label class="pq-chk"><input type="checkbox" id="pqRep"> Repeated facts only</label>')
    out.append('<button class="pqb" id="pqShuf">Shuffle</button>')
    out.append('<button class="pqb" id="pqReset">Reset</button></div>')
    out.append('<p class="pq-score" id="pqScore" aria-live="polite"></p>')
    out.append('<ol class="pq-list" id="pqList"></ol>')
    out.append('<button class="pqb" id="pqMore">Show 10 more</button>')
    out.append('</section>')
    
    # Chapters c1 to c65
    for idx, c in enumerate(chapters):
        num = c["num"]
        title = html.escape(c["title"])
        gist = html.escape(c.get("gist", f"Key facts and UPPSC questions on {c['title']}."))
        k = ch_q_count.get(num, 0)
        prev_href = f"#c{num - 1}" if num > 1 else "#home"
        prev_txt = f"← Chapter {num - 1}" if num > 1 else "← Start"
        next_href = f"#c{num + 1}" if num < len(chapters) else "#home"
        next_txt = f"{html.escape(chapters[idx + 1]['title'])} →" if num < len(chapters) else "Start →"
        
        out.append(f'<section class="view ch" id="c{num}" data-title="{title}">')
        out.append(f'<p class="eyebrow">Chapter {num}</p>')
        out.append(f'<h2>{title}</h2>')
        out.append(f'<p class="gist">{gist}</p>')
        
        # Focus
        if c.get("focus"):
            out.append('<div class="focus"><h3>UPPSC asks most here</h3><ol>')
            for f_item in c["focus"]:
                f_esc = f_item["fact"]
                e_esc = html.escape(f_item["exam"])
                c_esc = html.escape(f_item["cnt"])
                out.append(f'<li><b>{f_esc}</b><span class="know">{e_esc}</span><span class="cnt">{c_esc}</span></li>')
            out.append('</ol></div>')
            
        # Topics
        for top in c.get("topics", []):
            t_id = top["id"]
            t_title = html.escape(top["title"])
            t_pg = html.escape(top.get("pg", ""))
            pg_span = f'<span class="pg">{t_pg}</span>' if t_pg else ''
            out.append(f'<article class="topic" id="{t_id}">')
            out.append(f'<h3>{t_title}{pg_span}</h3><ul>')
            for pt in top.get("points", []):
                cls = "pt"
                if pt.get("asked"):
                    cls += " asked"
                if pt.get("hot"):
                    cls += " hot"
                out.append(f'<li class="{cls}">{pt["html"]}</li>')
            out.append('</ul></article>')
            
        out.append(f'<a class="cta" href="#practice" data-pq-ch="c{num}">Practise this chapter’s {k} UPPSC PYQs →</a>')
        out.append(f'<nav class="pn"><a href="{prev_href}">{prev_txt}</a><a class="nx" href="{next_href}">{next_txt}</a></nav>')
        out.append('</section>')
        
    # Results view
    out.append('<section class="view" id="results" data-title="Search">')
    out.append('<h2 id="rt">Search</h2>')
    out.append('<ul id="rl" class="res"></ul>')
    out.append('</section>')
    
    out.append('</main></div>')
    out.append('<div id="scrim"></div>')
    
    # pqd data block
    out.append('<script id="pqd" type="application/json">')
    out.append(json.dumps(qs, ensure_ascii=False))
    out.append('</script>')
    
    # JavaScript
    out.append(js)
    out.append('</body></html>')
    
    full_html = "\n".join(out)
    out_path = os.path.join("General_Science_Part_7", "science-uppsc-full-notes.html")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(full_html)
        
    print(f"Generated {out_path} ({len(full_html):,} chars)")

if __name__ == "__main__":
    generate_full_notes()
