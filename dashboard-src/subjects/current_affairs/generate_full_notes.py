import json
import re
import os
import html

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))

def generate_full_notes():
    with open(os.path.join(HERE, "structured_all_chapters.json"), "r", encoding="utf-8") as f:
        chapters = json.load(f)

    with open(os.path.join(HERE, "parsed_uppsc_questions.json"), "r", encoding="utf-8") as f:
        qs = json.load(f)

    with open(os.path.join(HERE, "repeated_facts.json"), "r", encoding="utf-8") as f:
        repeats = json.load(f)

    with open(os.path.join(HERE, "template_full_style.css"), "r", encoding="utf-8") as f:
        css = f.read()

    with open(os.path.join(HERE, "template_full_js.html"), "r", encoding="utf-8") as f:
        js = f.read()

    # Question count per chapter matching pqd
    ch_q_count = {}
    for qid, q in qs.items():
        ch_n = int(q["ch"][1:])
        ch_q_count[ch_n] = ch_q_count.get(ch_n, 0) + 1

    total_uppsc_q = sum(ch_q_count.values())
    total_pts = sum(len(t["points"]) for c in chapters for t in c["topics"])

    out = []
    out.append('<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">')
    out.append('<title>Current Affairs Full Notes</title>')
    out.append('<meta name="description" content="Ghatna Chakra Drishti Current Affairs 2026 for UPPCS Prelims: complete comprehensive study notes covering all 10 chapters with practice PYQ bank.">')
    out.append(f'<style>{css}</style></head><body>')
    
    # Header
    out.append('<header class="top" id="top">')
    out.append('<button id="menu" aria-label="Open contents">☰</button>')
    out.append('<a class="brand" href="#home">Current Affairs · Drishti 2026</a>')
    out.append('<input id="q" type="search" placeholder="Search full notes…" aria-label="Search notes" autocomplete="off">')
    out.append('<label class="tog"><input id="only" type="checkbox"> Important</label>')
    out.append('<label class="tog"><input id="dark" type="checkbox"> Dark</label>')
    out.append('</header>')
    
    out.append('<div class="wrap">')
    
    # Sidebar
    out.append('<nav class="side" id="side" aria-label="Chapters">')
    out.append('<a href="#home" data-v="home" class="plain on">Start</a>')
    out.append(f'<a href="#repeated" data-v="repeated" class="plain hl">Most repeated ({len(repeats)})</a>')
    out.append('<a href="#latest" data-v="latest" class="plain">Latest Drishti 2026</a>')
    out.append(f'<a href="#practice" data-v="practice" class="plain">PYQ practice ({total_uppsc_q})</a>')
    out.append('<div class="lb">Chapters</div>')
    for c in chapters:
        num = c["num"]
        out.append(f'<a href="#c{num}" data-v="c{num}"><span>{num}</span>{html.escape(c["title"])}</a>')
    out.append('</nav>')
    
    out.append('<main>')
    
    # Home view
    out.append('<section class="view" id="home"><h1>Current Affairs Full Notes</h1>')
    out.append('<p class="gist">Complete point-wise study notes from Ghatna Chakra Drishti Current Affairs 2026 for UPPCS Prelims.</p>')
    out.append('<p class="legend"><span class="key"></span>Repeated theme <span class="p up">UPPSC ×3</span> asked in 3 papers <span class="p up">UPPSC</span> high frequency</p>')
    out.append(f'<a class="cta" href="#repeated">Start with the {len(repeats)} most repeated facts →</a>')
    out.append('<ol class="toc">')
    for c in chapters:
        num = c["num"]
        title = html.escape(c["title"])
        k = ch_q_count.get(num, 0)
        hot_badge = '<span class="p up">Most asked</span>' if k >= 50 else ''
        out.append(f'<li><a href="#c{num}"><span class="no">{num}</span><span class="nm">{title}</span>{hot_badge}<span class="q">{k} UPPSC PYQs</span></a></li>')
    out.append('</ol>')
    out.append(f'<p class="foot">{total_pts} points and {total_uppsc_q} UPPSC practice questions (PCS Pre and Mains, RO/ARO, Lower Subordinate, UDA/LDA, GIC, BEO, RI; up to 2026) from Ghatna Chakra Drishti Current Affairs 2026. Facts and answers are as in the book; Check lines mark doubtful keys. Past repeats guide revision and do not predict a paper.</p>')
    out.append('</section>')
    
    # Repeated view
    out.append('<section class="view" id="repeated" data-title="UPPSC most repeated">')
    out.append('<h2>UPPSC most repeated</h2>')
    out.append('<p class="gist">Facts asked in multiple UPPSC papers and recurring high-yield themes. Tap a row to see exams.</p>')
    out.append(f'<h3>{len(repeats)} facts asked in two or more UPPSC papers</h3>')
    out.append('<ol class="rows">')
    for r in repeats:
        f_esc = r["fact"]
        p_esc = html.escape(r["papers"])
        anc = r["anchor"]
        cnt = r["count"]
        link_t = html.escape(r.get("link_text", "Open in chapter →"))
        out.append(f'<li><details><summary><span class="t">{f_esc}</span><span class="ps"><span class="p up">×{cnt}</span></span></summary><div class="yrs"><div>{p_esc}</div><a href="#{anc}">{link_t}</a></div></details></li>')
    out.append('</ol>')
    out.append('</section>')
    
    # Latest view
    out.append('<section class="view" id="latest" data-title="Latest Drishti 2026">')
    out.append('<h2>Latest Drishti Current Affairs 2026</h2>')
    out.append('<p class="gist">High-yield recent developments from late 2025 and 2026 compiled for UPPCS Prelims.</p>')
    out.append('<ol class="rows">')
    for r in repeats[:30]:
        out.append(f'<li><details><summary><span class="t">{r["fact"]}</span><span class="ps-lat"><span class="p up">Latest</span></span></summary><div class="yrs"><div>Drishti 2026 Official Record</div><a href="#{r["anchor"]}">Open in chapter →</a></div></details></li>')
    out.append('</ol>')
    out.append('</section>')
    
    # Practice view
    out.append('<section class="view" id="practice" data-title="UPPSC PYQ practice">')
    out.append('<h2>UPPSC PYQ Practice</h2>')
    out.append('<p class="gist">Practice all 500 questions chapter by chapter with instant feedback and explanations.</p>')
    out.append('<div class="pbar"><div id="pb" class="pbf"></div></div>')
    out.append('<div id="pq-box"></div>')
    out.append('</section>')
    
    # Chapters c1 to c10
    for idx, c in enumerate(chapters):
        num = c["num"]
        title = html.escape(c["title"])
        gist = c["gist"]
        prev_href = f"#c{num - 1}" if num > 1 else "#home"
        prev_txt = f"← {html.escape(chapters[idx - 1]['title'])}" if num > 1 else "← Start"
        next_href = f"#c{num + 1}" if num < len(chapters) else "#home"
        next_txt = f"{html.escape(chapters[idx + 1]['title'])} →" if num < len(chapters) else "Start →"
        
        out.append(f'<section class="view ch" id="c{num}" data-title="{title}">')
        out.append(f'<p class="eyebrow">Chapter {num}</p>')
        out.append(f'<h2>{title}</h2>')
        out.append(f'<p class="gist">{gist}</p>')
        
        for top in c["topics"]:
            t_id = top["id"]
            t_title = top["title"]
            out.append(f'<article class="topic" id="{t_id}">')
            out.append(f'<h3>{t_title}</h3>')
            out.append('<ul>')
            for pt in top["points"]:
                cls = "pt"
                if pt.get("asked"): cls += " asked"
                if pt.get("hot"): cls += " hot"
                out.append(f'<li class="{cls}">{pt["html"]}</li>')
            out.append('</ul></article>')
            
        out.append(f'<nav class="pn"><a href="{prev_href}">{prev_txt}</a><a class="nx" href="{next_href}">{next_txt}</a></nav>')
        out.append('</section>')
        
    # Results view
    out.append('<section class="view" id="results" data-title="Search">')
    out.append('<h2 id="rt">Search</h2>')
    out.append('<ul id="rl" class="res"></ul>')
    out.append('</section>')
    
    out.append('</main></div>')
    out.append('<div id="scrim"></div>')
    
    # Practice data script
    out.append(f'<script id="pqd" type="application/json">{json.dumps(qs, ensure_ascii=False)}</script>')
    
    # JavaScript
    out.append(js)
    out.append('</body></html>')
    
    full_html = "\n".join(out)
    out_path = os.path.join(ROOT, "Drishti-current affairs", "current-uppsc-full-notes.html")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(full_html)
        
    print(f"Generated {out_path} ({len(full_html):,} chars, {os.path.getsize(out_path):,} bytes)")

if __name__ == "__main__":
    generate_full_notes()
