import json
import re
import os
import html

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))

def generate_quick_notes():
    full_notes_path = os.path.join(ROOT, "Economy 2024", "economy-uppsc-full-notes.html")
    with open(full_notes_path, "r", encoding="utf-8") as f:
        fc = f.read()

    css_path = os.path.join(HERE, "template_quick_style.css")
    with open(css_path, "r", encoding="utf-8") as f:
        css = f.read()

    js_path = os.path.join(HERE, "template_quick_js.html")
    with open(js_path, "r", encoding="utf-8") as f:
        js = f.read()

    toc_path = os.path.join(HERE, "extracted_toc_data.json")
    with open(toc_path, "r", encoding="utf-8") as f:
        toc = json.load(f)

    repeats_path = os.path.join(HERE, "extracted_repeated_facts.json")
    with open(repeats_path, "r", encoding="utf-8") as f:
        repeats = json.load(f)

    # Question count per chapter matching full notes
    ch_q_count = {item["num"]: item["questions"] for item in toc}
    total_uppsc_q = sum(ch_q_count.values())
    assert total_uppsc_q == 1757, f"Expected 1757 questions, got {total_uppsc_q}"

    # Extract 19 chapters
    chapters = []
    for i in range(1, 20):
        pos_cur = fc.find(f'<section class="view ch" id="c{i}"')
        if i < 19:
            pos_nxt = fc.find(f'<section class="view ch" id="c{i+1}"')
        else:
            pos_nxt = fc.find('<section class="view" id="results"')
            if pos_nxt == -1:
                pos_nxt = fc.find('</main>')
                
        ch_str = fc[pos_cur:pos_nxt]
        title_m = re.search(r'data-title="([^"]+)"', ch_str)
        title = title_m.group(1) if title_m else f"Chapter {i}"
        gist_m = re.search(r'<p class="gist">(.*?)</p>', ch_str, re.S)
        gist = gist_m.group(1).strip() if gist_m else f"Condensed revision points for {title}."
        
        # Extract articles
        articles = re.findall(r'<article class="topic" id="([^"]+)">(.*?)</article>', ch_str, re.S)
        
        topic_list = []
        for tid, tbody in articles:
            h3_m = re.search(r'<h3>(.*?)</h3>', tbody, re.S)
            h3 = h3_m.group(1) if h3_m else ""
            
            has_repeat = any(r["anchor"] == tid for r in repeats)
            
            # Extract list items
            li_matches = re.findall(r'<li class="([^"]+)">(.*?)</li>', tbody, re.S)
            
            # Filter for quick notes: asked or hot points
            quick_lis = [p for p in li_matches if 'asked' in p[0] or 'hot' in p[0]]
            if not quick_lis:
                quick_lis = [('pt keep', p[1]) for p in li_matches[:4]]
                
            # Extract tables if any
            tables = re.findall(r'(<div class="tw">.*?</div>|<table.*?</table>)', tbody, re.S)
            quick_tables = []
            for tbl in tables:
                if 'asked' in tbl or 'hot' in tbl or has_repeat or len(li_matches) < 4:
                    quick_tables.append(tbl)
                    
            topic_list.append({
                "id": tid,
                "title": h3,
                "points": quick_lis,
                "tables": quick_tables
            })
            
        chapters.append({
            "num": i,
            "title": title,
            "gist": gist,
            "topics": topic_list
        })

    out = []
    out.append('<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">')
    out.append('<title>Economy Quick Revision Notes</title>')
    out.append('<meta name="description" content="Indian Economy and Social Development for UPPCS Prelims: rapid revision notes covering all 19 chapters with key facts and repeated PYQs.">')
    out.append(f'<style>{css}</style></head><body>')
    
    # Header
    out.append('<header class="top" id="top">')
    out.append('<button id="menu" aria-label="Open contents">☰</button>')
    out.append('<a class="brand" href="#home">Economy · Quick Revision</a>')
    out.append('<input id="q" type="search" placeholder="Search revision notes…" aria-label="Search quick notes" autocomplete="off">')
    out.append('<label class="tog"><input id="only" type="checkbox"> Important</label>')
    out.append('<label class="tog"><input id="dark" type="checkbox"> Dark</label>')
    out.append('</header>')
    
    out.append('<div class="wrap">')
    
    # Sidebar
    out.append('<nav class="side" id="side" aria-label="Chapters">')
    out.append('<a href="#home" class="on"><span></span>Contents</a>')
    out.append(f'<a href="#repeated" class="hl"><span>★</span>Repeated ({len(repeats)})</a>')
    out.append('<div class="lb">Chapters</div>')
    for c in chapters:
        num = c["num"]
        out.append(f'<a href="#c{num}"><span>{num}</span>{html.escape(c["title"])}</a>')
    out.append('</nav>')
    
    out.append('<main>')
    
    # Home view
    out.append('<section class="view" id="home"><h1>Economy Quick Revision</h1>')
    out.append('<p class="gist">Condensed revision points and high-yield facts for UPPSC Prelims 2026.</p>')
    out.append('<p class="legend"><span class="key"></span>Repeated fact <span class="p up">UPPSC ×3</span> asked in 3 papers <span class="p up">UPPSC</span> asked once</p>')
    out.append(f'<a class="cta" href="#repeated">Start with the {len(repeats)} most repeated facts →</a>')
    out.append('<ol class="toc">')
    for c in chapters:
        num = c["num"]
        title = html.escape(c["title"])
        k = ch_q_count.get(num, 0)
        hot_badge = '<span class="p up">Most asked</span>' if k >= 130 else ''
        out.append(f'<li><a href="#c{num}"><span class="no">{num}</span><span class="nm">{title}</span>{hot_badge}<span class="q">{k} UPPSC PYQs</span></a></li>')
    out.append('</ol>')
    out.append(f'<p class="foot">Based on {total_uppsc_q} UPPSC questions (PCS Pre and Mains, RO/ARO, Lower Subordinate, UDA/LDA, GIC, BEO, RI; up to 2023) from Ghatna Chakra Economic and Social Development 2024. Facts and answers are as in the book; Check lines mark doubtful keys. Past repeats guide revision and do not predict a paper.</p>')
    out.append('</section>')
    
    # Repeated view
    out.append('<section class="view" id="repeated" data-title="UPPSC most repeated">')
    out.append('<h2>UPPSC most repeated</h2>')
    out.append('<p class="gist">Facts asked in multiple UPPSC papers. Tap a row to see exams.</p>')
    out.append(f'<h3 id="rep-facts" class="sec">{len(repeats)} facts asked in two or more UPPSC papers</h3>')
    out.append('<ol class="rows">')
    for r in repeats:
        f_esc = r["fact"]
        p_esc = html.escape(r["papers"])
        anc = r["anchor"]
        cnt = r["count"]
        link_t = html.escape(r["link_text"])
        out.append(f'<li><details><summary><span class="t">{f_esc}</span><span class="ps"><span class="p up">×{cnt}</span></span></summary><div class="yrs"><div>{p_esc}</div><a href="#{anc}">{link_t}</a></div></details></li>')
    out.append('</ol>')
    out.append('</section>')
    
    # Chapters c1 to c19
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
            if top["points"]:
                out.append('<ul>')
                for cls, p_html in top["points"]:
                    out.append(f'<li class="{cls}">{p_html}</li>')
                out.append('</ul>')
            for tbl in top["tables"]:
                out.append(tbl)
            out.append('</article>')
            
        out.append(f'<nav class="pn"><a href="{prev_href}">{prev_txt}</a><a class="nx" href="{next_href}">{next_txt}</a></nav>')
        out.append('</section>')
        
    # Results view
    out.append('<section class="view" id="results" data-title="Search">')
    out.append('<h2 id="rt">Search</h2>')
    out.append('<ul id="rl" class="res"></ul>')
    out.append('</section>')
    
    out.append('</main></div>')
    out.append('<div id="scrim"></div>')
    
    # JavaScript
    out.append(js)
    out.append('</body></html>')
    
    full_html = "\n".join(out)
    out_path = os.path.join(ROOT, "Economy 2024", "economy-uppsc-quick-notes.html")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(full_html)
        
    print(f"Generated {out_path} ({len(full_html):,} chars, {os.path.getsize(out_path):,} bytes)")

if __name__ == "__main__":
    generate_quick_notes()
