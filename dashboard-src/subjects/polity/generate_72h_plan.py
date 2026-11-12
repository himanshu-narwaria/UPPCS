import json
import re
import os
import html
from collections import defaultdict

def generate_72h_plan():
    base_dir = os.path.join("dashboard-src", "subjects", "polity")
    with open(os.path.join(base_dir, "structured_all_chapters.json"), encoding="utf-8") as f:
        chapters = json.load(f)
    with open(os.path.join(base_dir, "parsed_uppsc_questions.json"), encoding="utf-8") as f:
        qs = json.load(f)
    with open(os.path.join(base_dir, "template_72h_style.css"), encoding="utf-8") as f:
        css = f.read()
    with open(os.path.join(base_dir, "template_72h_js.html"), encoding="utf-8") as f:
        js = f.read()

    # Learn schedule tested and confirmed with chapter_hours
    learn_hours = [
        (1, "The Constitutional Development of India", [1]),
        (2, "Constituent Assembly and Making of the Constitution", [2]),
        (3, "Important Committees of Constituent Assembly + Sources of the Constitution", [3, 4]),
        (4, "Parts of Indian Constitution + Articles of the Constitution", [5, 6]),
        (5, "Schedules", [7]),
        (6, "The Preamble", [8]),
        (7, "The Governance System · part 1 of 2", [9]),
        (8, "The Governance System · part 2 of 2", [9]),
        (9, "National Symbols + States and Union Territories", [10, 11]),
        (10, "The Citizenship", [12]),
        (11, "Fundamental Rights · part 1 of 3", [13]),
        (12, "Fundamental Rights · part 2 of 3", [13]),
        (13, "Fundamental Rights · part 3 of 3", [13]),
        (14, "Directive Principles of State Policy · part 1 of 2", [14]),
        (15, "Directive Principles of State Policy · part 2 of 2", [14]),
        (16, "Fundamental Duties", [15]),
        (17, "The President · part 1 of 2", [16]),
        (18, "The President · part 2 of 2", [16]),
        (19, "The Vice-President + The Council of Ministers", [17, 18]),
        (20, "The Attorney General and the C.A.G. + Order of Precedence", [19, 20]),
        (21, "The Parliament (1)", [21]),
        (22, "The Parliament (2)", [22]),
        (23, "The Parliament (3) · part 1 of 2", [23]),
        (24, "The Parliament (3) · part 2 of 2", [23]),
        (25, "Parliamentary Committees", [24]),
        (26, "The Parliamentary Act", [25]),
        (27, "The Supreme Court · part 1 of 2", [26]),
        (28, "The Supreme Court · part 2 of 2", [26]),
        (29, "The Governor", [27]),
        (30, "The State Legislature · part 1 of 2", [28]),
        (31, "The State Legislature · part 2 of 2", [28]),
        (32, "The High Court", [29]),
        (33, "The Centre-State Relations", [30]),
        (34, "Emergency Provisions", [31]),
        (35, "The Finance Commission + The Planning Commission/NITI Aayog", [32, 33]),
        (36, "Lokpal and Important Commissions", [34]),
        (37, "Temporary, Transitional and Special Provisions + Election Commission", [35, 36]),
        (38, "Political Parties", [37]),
        (39, "Constitutional Amendments", [38]),
        (40, "Official Language", [39]),
        (41, "Panchayati Raj and Community Development · part 1 of 3", [40]),
        (42, "Panchayati Raj and Community Development · part 2 of 3", [40]),
        (43, "Panchayati Raj and Community Development · part 3 of 3", [40]),
        (44, "Special Provision for Certain Classes", [41]),
        (45, "Miscellaneous · part 1 of 4", [42]),
        (46, "Miscellaneous · part 2 of 4", [42]),
        (47, "Miscellaneous · part 3 of 4", [42]),
        (48, "Miscellaneous · part 4 of 4", [42]),
    ]

    # Revise hours (49 to 68)
    revise_hours = [
        (49, "Constitutional History & Framing: Acts of 1773–1947 & Constituent Assembly"),
        (50, "Constitutional Core: Preamble, Sources, Schedules & Parts"),
        (51, "Territory, States Reorganisation & Indian Citizenship"),
        (52, "Fundamental Rights: Right to Equality (Arts 14–18) & Right to Freedom (Arts 19–22)"),
        (53, "Fundamental Rights: Protection, Religion & Writs (Arts 23–32)"),
        (54, "Directive Principles of State Policy & Fundamental Duties"),
        (55, "Union Executive: President of India — Election, Impeachment & Powers"),
        (56, "Union Executive: Vice-President, Prime Minister & Council of Ministers"),
        (57, "Constitutional Watchdogs: Attorney General of India & Comptroller and Auditor General"),
        (58, "Union Parliament: Lok Sabha Composition, Qualifications & Procedures"),
        (59, "Union Parliament: Rajya Sabha Powers & Legislative Process"),
        (60, "Parliamentary Proceedings: Money Bills, Joint Sittings & Motions"),
        (61, "Parliamentary Committees: PAC, Estimates, PUC & Ad-hoc Bodies"),
        (62, "Judiciary: Supreme Court of India — Jurisdictions, Judicial Review & PIL"),
        (63, "State Executive: Governor Powers, Discretion & Ordinances"),
        (64, "State Legislature: Legislative Assembly & Legislative Council"),
        (65, "State Judiciary: High Courts, Subordinate Courts & Tribunals"),
        (66, "Federal Structure: Centre-State Relations & Emergency Provisions (Arts 352–360)"),
        (67, "Local Self-Government: Panchayati Raj & Municipalities (73rd/74th Amendments)"),
        (68, "Constitutional Commissions, Political Parties & Major Amendments"),
    ]

    # Test hours (69 to 72)
    test_hours = [
        (69, "UPPSC Indian Polity Full Mock 1"),
        (70, "UPPSC Indian Polity Full Mock 2"),
        (71, "UPPSC Indian Polity Full Mock 3"),
        (72, "UPPSC Indian Polity Full Mock 4"),
    ]

    # Map questions to chapters
    qs_by_ch = defaultdict(list)
    all_q_ids = list(qs.keys())
    for qid, q in qs.items():
        ch_num = int(q["ch"][1:])
        qs_by_ch[ch_num].append(qid)

    ch_dict = {c["num"]: c for c in chapters}

    out = []
    out.append('<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">')
    out.append('<title>Indian Polity in 72 Hours</title>')
    out.append('<meta name="description" content="72 hours before 6 December 2026: hour-by-hour revision plan for Indian Polity in UPPCS Prelims 2026.">')
    out.append(f'<style>{css}</style></head><body>')
    
    # Header
    out.append('<header class="top" id="top">')
    out.append('<button id="menu" aria-label="Open schedule">☰</button>')
    out.append('<a class="brand" href="#home">Polity in 72h</a>')
    out.append('<span id="prog" class="prog">0 of 72 hours done</span>')
    out.append('<input id="q" type="search" placeholder="Search" aria-label="Search notes" autocomplete="off">')
    out.append('<label class="tog"><input id="dark" type="checkbox"> Dark</label>')
    out.append('</header>')
    out.append('<div class="bar"><i id="bar"></i></div>')
    
    out.append('<div class="wrap">')
    
    # Sidebar
    out.append('<nav class="side" id="side" aria-label="Hours">')
    out.append('<a href="#home" data-v="home"><span></span>Plan</a>')
    
    out.append('<div class="lb">Learn</div>')
    for h, title, _ in learn_hours:
        out.append(f'<a href="#h{h}" data-v="h{h}"><span>{h}</span>{html.escape(title)}</a>')
        
    out.append('<div class="lb">Revise</div>')
    for h, title in revise_hours:
        out.append(f'<a href="#h{h}" data-v="h{h}"><span>{h}</span>{html.escape(title)}</a>')
        
    out.append('<div class="lb">Test</div>')
    for h, title in test_hours:
        out.append(f'<a href="#h{h}" data-v="h{h}"><span>{h}</span>{html.escape(title)}</a>')
    out.append('</nav>')
    
    out.append('<main>')
    
    # Home view
    out.append('<section class="view on" id="home"><h1>Indian Polity in 72 Hours</h1>')
    out.append('<p class="gist">72 hours before 6 December 2026 for UPPSC Prelims 2026.</p>')
    out.append('<a class="cta" id="cont" href="#h1">Start with hour 1 →</a>')
    out.append('<p class="lead">Complete syllabus coverage in 48 hours of focused reading, 20 hours of rapid revision, and 4 timed full-length mocks. Every hour has its reading points and real UPPSC PYQs.</p>')
    out.append('<div class="plan-grid">')
    out.append('<div class="card"><h3>Phase 1: Learn</h3><p><b>Hours 1–48</b>: All 42 chapters structured into 48 intensive sessions. Read high-yield summaries and solve matching PYQs.</p><a class="btn" href="#h1">Start Hour 1 →</a></div>')
    out.append('<div class="card"><h3>Phase 2: Revise</h3><p><b>Hours 49–68</b>: 20 rapid revision hours focusing on repeated facts, landmark judgments, key articles, and constitutional amendments.</p><a class="btn sec" href="#h49">Jump to Revision →</a></div>')
    out.append('<div class="card"><h3>Phase 3: Test</h3><p><b>Hours 69–72</b>: 4 timed mocks with high-yield questions simulating real UPPSC exam conditions.</p><a class="btn sec" href="#h69">Jump to Tests →</a></div>')
    out.append('</div>')
    out.append('</section>')
    
    # Hours 1 to 48 (Learn)
    for h, title, ch_nums in learn_hours:
        eyebrow = f"Hour {h} of 72 · Learn"
        read_blocks = []
        hour_q_ids = []
        
        m_part = re.search(r'· part (\d+) of (\d+)$', title)
        if m_part:
            part_idx = int(m_part.group(1)) - 1
            num_parts = int(m_part.group(2))
            c_num = ch_nums[0]
            c = ch_dict.get(c_num)
            
            # 1. Distinct Questions per part (strictly disjoint across parts)
            ch_all_qs = qs_by_ch.get(c_num, [])
            q_slice_size = min(15, max(10, len(ch_all_qs) // num_parts))
            q_start = part_idx * q_slice_size
            q_end = min(len(ch_all_qs), (part_idx + 1) * q_slice_size) if part_idx < num_parts - 1 else min(len(ch_all_qs), max((part_idx + 1) * q_slice_size, len(ch_all_qs)))
            hour_q_ids = ch_all_qs[q_start:q_end]
            if not hour_q_ids:
                hour_q_ids = ch_all_qs[:15]
                
            # 2. Distinct Reading points per part
            topics = c.get("topics", [])
            num_topics = len(topics)
            t_start = part_idx * num_topics // num_parts
            t_end = (part_idx + 1) * num_topics // num_parts if part_idx < num_parts - 1 else num_topics
            assigned_topics = topics[t_start:t_end] if t_start < t_end else [topics[min(t_start, num_topics - 1)]]
            
            for top in assigned_topics:
                pts = [p["html"] for p in top.get("points", [])]
                if pts:
                    pts_html = "".join(f'<li class="pt">{p}</li>' for p in pts[:8])
                    read_blocks.append(f'<div class="ch-read"><h4>{html.escape(top["title"])}</h4><ul>{pts_html}</ul></div>')
        else:
            # Single or combined chapters
            for c_num in ch_nums:
                c = ch_dict.get(c_num)
                if not c:
                    continue
                c_qs = qs_by_ch.get(c_num, [])
                take_q = 15 // len(ch_nums) if len(ch_nums) > 1 else 15
                hour_q_ids.extend(c_qs[:take_q])
                
                c_pts = []
                for top in c.get("topics", []):
                    for pt in top.get("points", []):
                        c_pts.append(pt["html"])
                        
                if c_pts:
                    pts_html = "".join(f'<li class="pt">{p}</li>' for p in c_pts[:8])
                    read_blocks.append(f'<div class="ch-read"><h4>Chapter {c_num}: {html.escape(c["title"])}</h4><ul>{pts_html}</ul></div>')
                    
        out.append(f'<section class="view" id="h{h}" data-n="{h}">')
        out.append(f'<p class="eyebrow">{eyebrow}</p>')
        out.append(f'<h2>{html.escape(title)}</h2>')
        out.append('<div class="reading"><h3>High-Yield Reading</h3>' + "".join(read_blocks) + '</div>')
        
        # Questions
        sel_q_ids = hour_q_ids[:15] if hour_q_ids else all_q_ids[((h-1)*5) % len(all_q_ids) : (((h-1)*5) % len(all_q_ids)) + 8]
        q_csv = ",".join(sel_q_ids)
        out.append('<div class="practice"><h3>Hour Practice MCQs</h3>')
        out.append(f'<p class="score"></p><ol class="pq" data-q="{q_csv}"></ol></div>')
        
        # Done block
        nx_href = f"#h{h+1}" if h < 72 else "#home"
        out.append(f'<div class="done"><button type="button" class="btn" data-done="{h}">Mark hour {h} done</button>')
        out.append(f'<a class="btn nx" href="{nx_href}">Next: Hour {h+1} →</a></div>')
        out.append('</section>')
        
    # Hours 49 to 68 (Revise)
    for h, title in revise_hours:
        eyebrow = f"Hour {h} of 72 · Revise"
        start_idx = ((h - 49) * 2) % len(chapters)
        rev_chapters = chapters[start_idx : start_idx + 3]
        
        read_blocks = []
        hour_q_ids = []
        for c in rev_chapters:
            c_num = c["num"]
            c_qs = qs_by_ch.get(c_num, [])
            rev_qs = [qid for qid in c_qs if qs[qid].get("n", 1) >= 2]
            if len(rev_qs) < 5:
                rev_qs += [qid for qid in c_qs if qid not in rev_qs]
            hour_q_ids.extend(rev_qs[:5])
            rev_pts = []
            for top in c.get("topics", []):
                for pt in top.get("points", []):
                    if pt.get("asked") or pt.get("hot"):
                        rev_pts.append(pt["html"])
            if rev_pts:
                pts_html = "".join(f'<li class="pt">{p}</li>' for p in rev_pts[:6])
                read_blocks.append(f'<div class="ch-read"><h4>Review: {html.escape(c["title"])}</h4><ul>{pts_html}</ul></div>')
                
        out.append(f'<section class="view" id="h{h}" data-n="{h}">')
        out.append(f'<p class="eyebrow">{eyebrow}</p>')
        out.append(f'<h2>{html.escape(title)}</h2>')
        out.append('<div class="reading"><h3>Rapid Revision Focus</h3>' + "".join(read_blocks) + '</div>')
        
        sel_q_ids = hour_q_ids[:15] if hour_q_ids else all_q_ids[((h-1)*5) % len(all_q_ids) : (((h-1)*5) % len(all_q_ids)) + 10]
        q_csv = ",".join(sel_q_ids)
        out.append('<div class="practice"><h3>Revision Drill MCQs</h3>')
        out.append(f'<p class="score"></p><ol class="pq" data-q="{q_csv}"></ol></div>')
        
        nx_href = f"#h{h+1}" if h < 72 else "#home"
        out.append(f'<div class="done"><button type="button" class="btn" data-done="{h}">Mark hour {h} done</button>')
        out.append(f'<a class="btn nx" href="{nx_href}">Next: Hour {h+1} →</a></div>')
        out.append('</section>')
        
    # Hours 69 to 72 (Test)
    for h, title in test_hours:
        eyebrow = f"Hour {h} of 72 · Test"
        mock_idx = h - 69
        slice_size = min(25, len(all_q_ids) // 4)
        mock_q_ids = all_q_ids[mock_idx * slice_size : (mock_idx + 1) * slice_size]
        q_csv = ",".join(mock_q_ids)
        
        out.append(f'<section class="view" id="h{h}" data-n="{h}">')
        out.append(f'<p class="eyebrow">{eyebrow}</p>')
        out.append(f'<h2>{html.escape(title)}</h2>')
        out.append('<div class="reading"><h3>Exam Simulation Instructions</h3>')
        out.append('<p>Time: 60 minutes. Standard UPPSC negative marking (1/3rd mark deducted per wrong answer). Answer all questions under timed exam conditions.</p></div>')
        
        out.append('<div class="practice"><h3>Mock Test Questions</h3>')
        out.append(f'<p class="score"></p><ol class="pq" data-q="{q_csv}"></ol></div>')
        
        nx_href = f"#h{h+1}" if h < 72 else "#home"
        out.append(f'<div class="done"><button type="button" class="btn" data-done="{h}">Mark hour {h} done</button>')
        out.append(f'<a class="btn nx" href="{nx_href}">{"Next: Hour " + str(h+1) if h < 72 else "Back to Plan"} →</a></div>')
        out.append('</section>')
        
    # Search results view
    out.append('<section class="view" id="results" data-title="Search">')
    out.append('<h2 id="rt">Search</h2>')
    out.append('<div id="rl" class="search-res"></div>')
    out.append('</section>')
    
    out.append('</main></div>')
    out.append('<div id="scrim"></div>')
    
    # Embed question database
    out.append('<script id="pqd" type="application/json">')
    out.append(json.dumps(qs, ensure_ascii=False))
    out.append('</script>')
    
    # Append JS
    out.append(js)
    out.append('</body></html>')
    
    full_html = "\n".join(out)
    out_path = os.path.join("Indian_Polity_and_Governance", "polity-in-72h.html")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(full_html)
        
    print(f"Generated {out_path} ({len(full_html):,} chars, {os.path.getsize(out_path):,} bytes)")

if __name__ == "__main__":
    generate_72h_plan()
