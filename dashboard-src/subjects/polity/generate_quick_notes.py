import json
import re
import os
import html

def generate_quick_notes():
    base_dir = os.path.join("dashboard-src", "subjects", "polity")
    with open(os.path.join(base_dir, "structured_all_chapters.json"), encoding="utf-8") as f:
        chapters = json.load(f)
    with open(os.path.join(base_dir, "parsed_uppsc_questions.json"), encoding="utf-8") as f:
        qs = json.load(f)
    with open(os.path.join(base_dir, "repeated_facts.json"), encoding="utf-8") as f:
        repeats = json.load(f)
    with open(os.path.join(base_dir, "template_quick_style.css"), encoding="utf-8") as f:
        css = f.read()
    with open(os.path.join(base_dir, "template_quick_js.html"), encoding="utf-8") as f:
        js = f.read()

    # Question count per chapter matching full notes
    ch_q_count = {}
    for qid, q in qs.items():
        ch_n = int(q["ch"][1:])
        ch_q_count[ch_n] = ch_q_count.get(ch_n, 0) + 1

    total_uppsc_q = sum(ch_q_count.values())

    out = []
    out.append('<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">')
    out.append('<title>Indian Polity Quick Revision Notes</title>')
    out.append('<meta name="description" content="Indian Polity and Governance for UPPCS Prelims: rapid revision notes covering all 42 chapters with key facts and repeated PYQs.">')
    out.append(f'<style>{css}</style></head><body>')
    
    # Header
    out.append('<header class="top" id="top">')
    out.append('<button id="menu" aria-label="Open contents">☰</button>')
    out.append('<a class="brand" href="#home">Indian Polity · Quick Revision</a>')
    out.append('<input id="q" type="search" placeholder="Search revision notes…" aria-label="Search quick notes" autocomplete="off">')
    out.append('<label class="tog"><input id="only" type="checkbox"> Important</label>')
    out.append('<label class="tog"><input id="dark" type="checkbox"> Dark</label>')
    out.append('</header>')
    
    out.append('<div class="wrap">')
    
    # Sidebar
    out.append('<nav class="side" id="side" aria-label="Chapters">')
    out.append('<a href="#home" class="on"><span></span>Contents</a>')
    out.append(f'<a href="#repeated" class="hl"><span>★</span>Repeated ({len(repeats)})</a>')
    out.append('<div class="lb">Part I · Constitutional Framework</div>')
    for c in chapters:
        num = c["num"]
        if num == 9:
            out.append('<div class="lb">Part II · Governance System & Territories</div>')
        elif num == 13:
            out.append('<div class="lb">Part III · Rights, Duties & Directives</div>')
        elif num == 16:
            out.append('<div class="lb">Part IV · Union Executive & Precedence</div>')
        elif num == 21:
            out.append('<div class="lb">Part V · Parliament of India</div>')
        elif num == 26:
            out.append('<div class="lb">Part VI · The Judiciary & State Governments</div>')
        elif num == 30:
            out.append('<div class="lb">Part VII · Federal Relations & Emergency</div>')
        elif num == 32:
            out.append('<div class="lb">Part VIII · Constitutional & Statutory Bodies</div>')
        elif num == 37:
            out.append('<div class="lb">Part IX · Elections, Language & Amendments</div>')
        elif num == 40:
            out.append('<div class="lb">Part X · Local Governance & Special Provisions</div>')
        out.append(f'<a href="#c{num}"><span>{num}</span>{html.escape(c["title"])}</a>')
    out.append('</nav>')
    
    out.append('<main>')
    
    # Home view
    out.append('<section class="view" id="home"><h1>Indian Polity Quick Revision</h1>')
    out.append('<p class="gist">Condensed revision points and high-yield facts for UPPSC Prelims 2026.</p>')
    out.append('<p class="legend"><span class="key"></span>Repeated fact <span class="p up">UPPSC ×3</span> asked in 3 papers <span class="p up">UPPSC</span> asked once</p>')
    out.append(f'<a class="cta" href="#repeated">Start with the {len(repeats)} most repeated facts →</a>')
    out.append('<ol class="toc">')
    for c in chapters:
        num = c["num"]
        title = html.escape(c["title"])
        k = ch_q_count.get(num, 0)
        hot_badge = '<span class="p up">High weightage</span>' if k >= 35 else ''
        out.append(f'<li><a href="#c{num}"><span class="no">{num}</span><span class="nm">{title}</span>{hot_badge}<span class="q">{k} UPPSC PYQs</span></a></li>')
    out.append('</ol>')
    out.append(f'<p class="foot">Based on {total_uppsc_q} UPPSC questions (PCS Pre and Mains, RO/ARO, Lower Subordinate, UDA/LDA, GIC, BEO, RI; up to 2025) from Ghatna Chakra Preview Indian Polity and Governance 2026. Every fact is verified against official answer keys.</p>')
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
        out.append(f'<li><details><summary><span class="t">{f_esc}</span><span class="ps"><span class="p up">×{cnt}</span></span></summary><div class="yrs"><div>{p_esc}</div><a href="#{anc}">Open in chapter →</a></div></details></li>')
    out.append('</ol>')
    out.append('</section>')
    
    # Chapters c1 to c42
    for idx, c in enumerate(chapters):
        num = c["num"]
        title = html.escape(c["title"])
        gist = html.escape(c.get("gist", f"Quick revision points for {c['title']}."))
        prev_href = f"#c{num - 1}" if num > 1 else "#home"
        prev_txt = f"← Chapter {num - 1}" if num > 1 else "← Start"
        next_href = f"#c{num + 1}" if num < len(chapters) else "#home"
        next_txt = f"{html.escape(chapters[idx + 1]['title'])} →" if num < len(chapters) else "Start →"
        
        out.append(f'<section class="view ch" id="c{num}" data-title="{title}">')
        out.append(f'<p class="eyebrow">Chapter {num}</p>')
        out.append(f'<h2>{title}</h2>')
        out.append(f'<p class="gist">{gist}</p>')
        
        for top in c.get("topics", []):
            t_id = top["id"]
            t_title = html.escape(top["title"])
            pts = top.get("points", [])
            # Quick notes filters for asked or high yield points
            quick_pts = [p for p in pts if p.get("asked") or p.get("hot")]
            if not quick_pts:
                quick_pts = pts[:4]
                
            out.append(f'<article class="topic" id="{t_id}">')
            out.append(f'<h3>{t_title}</h3><ul>')
            for pt in quick_pts:
                cls = "pt"
                if pt.get("asked"):
                    cls += " asked"
                if pt.get("hot"):
                    cls += " hot"
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
    
    # JavaScript
    out.append(js)
    out.append('</body></html>')
    
    full_html = "\n".join(out)
    out_path = os.path.join("Indian_Polity_and_Governance", "polity-uppsc-quick-notes.html")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(full_html)
        
    print(f"Generated {out_path} ({len(full_html):,} chars, {os.path.getsize(out_path):,} bytes)")

if __name__ == "__main__":
    generate_quick_notes()
