import json
import re
import os
import html

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))

def generate_72h_plan():
    with open(os.path.join(HERE, "structured_all_chapters.json"), "r", encoding="utf-8") as f:
        chapters = json.load(f)

    with open(os.path.join(HERE, "parsed_uppsc_questions.json"), "r", encoding="utf-8") as f:
        qs = json.load(f)

    with open(os.path.join(HERE, "template_72h_style.css"), "r", encoding="utf-8") as f:
        css = f.read()

    with open(os.path.join(HERE, "template_72h_js.html"), "r", encoding="utf-8") as f:
        js = f.read()

    # Plan schedule definitions (72 hours)
    # Phase 1: Learn (Hours 1 to 54)
    # Covering all 10 chapters
    learn_hours = [
        # Ch 1: Points to Remember (4 hours)
        (1, "Points to Remember · part 1 of 4", 1, "National & International One-Liners"),
        (2, "Points to Remember · part 2 of 4", 1, "Economy & Financial Indicators"),
        (3, "Points to Remember · part 3 of 4", 1, "Science, Defence & Space Q&As"),
        (4, "Points to Remember · part 4 of 4", 1, "Short News, Awards & Sports Highlights"),
        
        # Ch 2: National Affairs (6 hours)
        (5, "National Affairs · part 1 of 6", 2, "Major National Summits, Anniversaries & Conclaves"),
        (6, "National Affairs · part 2 of 6", 2, "New Acts, Statutory Amendments & Judicial Rulings"),
        (7, "National Affairs · part 3 of 6", 2, "Central Welfare Schemes & Infrastructure Projects"),
        (8, "National Affairs · part 4 of 6", 2, "Education, Health & Digital Initiatives"),
        (9, "National Affairs · part 5 of 6", 2, "Social Justice, Reports & Governance Indices"),
        (10, "National Affairs · part 6 of 6", 2, "Elections, Census 2027 Approval & Counter-Terrorism Policy"),
        
        # Ch 3: International Affairs (6 hours)
        (11, "International Affairs · part 1 of 6", 3, "Bilateral Relations: India with European Nations"),
        (12, "International Affairs · part 2 of 6", 3, "Bilateral Relations: Asian & Central Asian Partners"),
        (13, "International Affairs · part 3 of 6", 3, "Presidential & Prime Ministerial State Visits"),
        (14, "International Affairs · part 4 of 6", 3, "Nobel Prizes 2026 & Global Hunger / Gender Indices"),
        (15, "International Affairs · part 5 of 6", 3, "International Reports & Academic/Rule of Law Rankings"),
        (16, "International Affairs · part 6 of 6", 3, "Multilateral Summits: SCO, G7, BRICS & UNGA 81st"),
        
        # Ch 4: Economic Affairs (6 hours)
        (17, "Economic Affairs · part 1 of 6", 4, "Fiscal & Monetary Policy, Banking Restructuring & ULI"),
        (18, "Economic Affairs · part 2 of 6", 4, "Agriculture Schemes, MSPs & Edible Oil/Cotton Missions"),
        (19, "Economic Affairs · part 3 of 6", 4, "MSME Development Act, Semiconductor Units & Startup India"),
        (20, "Economic Affairs · part 4 of 6", 4, "National & Global Economic Indices (EPI, WEF, MPI)"),
        (21, "Economic Affairs · part 5 of 6", 4, "Union Budget 2026–27 Analysis & Fiscal Deficits"),
        (22, "Economic Affairs · part 6 of 6", 4, "Economic Survey 2025–26 Highlights & Rich Lists"),
        
        # Ch 5: Science & Technology Affairs (6 hours)
        (23, "Science & Technology Affairs · part 1 of 6", 5, "Space Missions: JAXA MMX, Artemis II, ISRO LVM3"),
        (24, "Science & Technology Affairs · part 2 of 6", 5, "New Telescopes, Earth Observation Satellites & Spacecraft"),
        (25, "Science & Technology Affairs · part 3 of 6", 5, "Supercomputing, AI Summits & Green Hydrogen Portals"),
        (26, "Science & Technology Affairs · part 4 of 6", 5, "Health Innovations, Vaccines (Dengue, TB, HPV, Malaria)"),
        (27, "Science & Technology Affairs · part 5 of 6", 5, "Indigenous Defence: Drones, Engines & GaN Technology"),
        (28, "Science & Technology Affairs · part 6 of 6", 5, "Naval Warships, Submarines & Ballistic Missiles (Agni, Oreshnik)"),
        
        # Ch 6: Environmental Affairs (5 hours)
        (29, "Environmental Affairs · part 1 of 5", 6, "UNEP Emissions Gap Report & Net Zero Dashboards"),
        (30, "Environmental Affairs · part 2 of 5", 6, "Ramsar Sites Tally (103) & Wetland Conservation"),
        (31, "Environmental Affairs · part 3 of 5", 6, "Wildlife Projects, Petroglyph Parks & Night Safaris"),
        (32, "Environmental Affairs · part 4 of 5", 6, "Renewable Energy Capacity (Solar, Wind, E85 Fuel)"),
        (33, "Environmental Affairs · part 5 of 5", 6, "COP30 Climate Summit Belém & World Air Quality Report"),
        
        # Ch 7: Uttar Pradesh Current Affairs (8 hours)
        (34, "Uttar Pradesh Current Affairs · part 1 of 8", 7, "IAF Varanasi Air Show & Bhadohi Carpet Expo"),
        (35, "Uttar Pradesh Current Affairs · part 2 of 8", 7, "Noida International Airport Jewar Operations"),
        (36, "Uttar Pradesh Current Affairs · part 3 of 8", 7, "Kashi Tamil Sangamam 4.0 & Cultural Projects"),
        (37, "Uttar Pradesh Current Affairs · part 4 of 8", 7, "UP Expressway Extensions & Industrial Corridors"),
        (38, "Uttar Pradesh Current Affairs · part 5 of 8", 7, "Swachh Vayu Survekshan: Lucknow & UP Rankings"),
        (39, "Uttar Pradesh Current Affairs · part 6 of 8", 7, "Ayodhya Solar City & Renewable Energy Initiatives"),
        (40, "Uttar Pradesh Current Affairs · part 7 of 8", 7, "Paddy Procurement Policy, Agriculture & ODOP GI Tags"),
        (41, "Uttar Pradesh Current Affairs · part 8 of 8", 7, "UP State Budget, Metro Projects & Welfare Schemes"),
        
        # Ch 8: Bihar Current Affairs (4 hours)
        (42, "Bihar Current Affairs · part 1 of 4", 8, "Bihar AI-Ready Data Center & Bodh Gaya AI Factory"),
        (43, "Bihar Current Affairs · part 2 of 4", 8, "Sankalp Dashboard, Samanvay Portal & Tech Parks"),
        (44, "Bihar Current Affairs · part 3 of 4", 8, "Bihar MSME Policy 2026 & Sector Incentives"),
        (45, "Bihar Current Affairs · part 4 of 4", 8, "Bihar Agriculture Growth, Horticulture & GSVA Indicators"),
        
        # Ch 9: Short News, Awards and Persons (5 hours)
        (46, "Short News, Awards and Persons · part 1 of 5", 9, "Persons in News: National Leaders & Appointments"),
        (47, "Short News, Awards and Persons · part 2 of 5", 9, "Persons in News: International Leaders & Heads of State"),
        (48, "Short News, Awards and Persons · part 3 of 5", 9, "Awards & Honours: Nobel, Dadasaheb Phalke, Magsaysay"),
        (49, "Short News, Awards and Persons · part 4 of 5", 9, "Books, Authors & Distinguished Memoirs"),
        (50, "Short News, Awards and Persons · part 5 of 5", 9, "Joint Military Exercises, Operations, Days & Themes"),
        
        # Ch 10: Sports News (4 hours)
        (51, "Sports News · part 1 of 4", 10, "Cricket Championships: Women's T20 Asia Cup & World Cups"),
        (52, "Sports News · part 2 of 4", 10, "Tennis Grand Slams: US Open, Wimbledon, Roland Garros"),
        (53, "Sports News · part 3 of 4", 10, "Olympic/Paralympic Highlights & Athletics Records"),
        (54, "Sports News · part 4 of 4", 10, "National Sports Awards: Khel Ratna, Arjuna Awards, Chess & Badminton")
    ]

    # Phase 2: Revise (Hours 55 to 64)
    revise_hours = [
        (55, "Rapid Revision: Points to Remember & One-Liners", 1, "Quick revision of all high-yield Q&As"),
        (56, "Rapid Revision: National Affairs & Central Schemes", 2, "Consolidated review of bills and policies"),
        (57, "Rapid Revision: International Summits & Global Indices", 3, "Review of bilateral pacts and India's rankings"),
        (58, "Rapid Revision: Union Budget & Economic Indicators", 4, "Review of fiscal targets, slabs, and schemes"),
        (59, "Rapid Revision: Science, Defence & Space Breakthroughs", 5, "Review of space missions and missile systems"),
        (60, "Rapid Revision: Environment, Ramsar Sites & COP30", 6, "Review of wetlands, emissions, and wildlife"),
        (61, "Rapid Revision: UP Special Core Current Affairs", 7, "High-weightage UP schemes and infrastructure"),
        (62, "Rapid Revision: Bihar Current Events & MSME Policy", 8, "Review of Bihar state indicators"),
        (63, "Rapid Revision: Awards, Honours, Books & Exercises", 9, "Review of major awards and military drills"),
        (64, "Rapid Revision: Sports Tournaments & Arjuna Awards", 10, "Review of trophies, medals, and champions")
    ]

    # Phase 3: Test (Hours 65 to 72)
    test_hours = [
        (65, "Thematic Practice Drill: National & International", 2, "50 curated MCQs with instant feedback"),
        (66, "Thematic Practice Drill: Economy & Environment", 4, "50 curated MCQs with instant feedback"),
        (67, "Thematic Practice Drill: Sci-Tech & UP Special", 7, "50 curated MCQs with instant feedback"),
        (68, "Thematic Practice Drill: Short News, Awards & Sports", 9, "50 curated MCQs with instant feedback"),
        (69, "Full-Length Mock 1: Comprehensive Current Affairs 2026", 1, "Timed 100-MCQ test covering entire syllabus"),
        (70, "Full-Length Mock 2: High-Yield Expected Questions", 2, "Timed 100-MCQ test covering high-frequency topics"),
        (71, "Full-Length Mock 3: UP Special & National Priority Mock", 7, "Timed 100-MCQ test emphasizing UP facts"),
        (72, "Final Score Booster Mock 4: Complete Drishti 2026 Simulation", 1, "Final comprehensive readiness assessment")
    ]

    all_hours = learn_hours + revise_hours + test_hours
    assert len(all_hours) == 72, f"Expected 72 hours, got {len(all_hours)}"

    out = []
    out.append('<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">')
    out.append('<title>Current Affairs in 72h</title>')
    out.append('<meta name="description" content="72-hour revision plan for Ghatna Chakra Drishti Current Affairs 2026 before UPPCS Prelims on 6 December 2026.">')
    out.append(f'<style>{css}</style></head><body>')
    
    # Header
    out.append('<header class="top" id="top">')
    out.append('<button id="menu" aria-label="Open schedule">☰</button>')
    out.append('<a class="brand" href="#home">Current Affairs · in 72h</a>')
    out.append('<span id="prog" class="prog">0 of 72 hours done</span>')
    out.append('<label class="tog"><input id="dark" type="checkbox"> Dark</label>')
    out.append('</header>')
    out.append('<div class="bar"><i id="bar"></i></div>')
    
    out.append('<div class="wrap">')
    
    # Sidebar
    out.append('<nav class="side" id="side" aria-label="Schedule">')
    out.append('<a href="#home" data-v="home" class="plain on">Start</a>')
    
    out.append('<div class="lb">Learn</div>')
    for h_num, h_title, _, _ in learn_hours:
        out.append(f'<a href="#h{h_num}" data-v="h{h_num}"><span>{h_num}</span>{html.escape(h_title)}</a>')
        
    out.append('<div class="lb">Revise</div>')
    for h_num, h_title, _, _ in revise_hours:
        out.append(f'<a href="#h{h_num}" data-v="h{h_num}"><span>{h_num}</span>{html.escape(h_title)}</a>')
        
    out.append('<div class="lb">Test</div>')
    for h_num, h_title, _, _ in test_hours:
        out.append(f'<a href="#h{h_num}" data-v="h{h_num}"><span>{h_num}</span>{html.escape(h_title)}</a>')
        
    out.append('</nav>')
    
    out.append('<main>')
    
    # Home view
    out.append('<section class="view" id="home"><h1>Current Affairs in 72h</h1>')
    out.append('<p class="gist">72 hours before 6 December 2026 — Master Ghatna Chakra Drishti Current Affairs 2026 with targeted one-hour sessions.</p>')
    out.append('<div class="prog-box"><div class="pb-lbl"><span>Progress</span><span id="prog-txt">0 / 72 hours (0%)</span></div><div class="pbar"><div id="pb" class="pbf"></div></div></div>')
    out.append('<a class="cta" id="cont" href="#h1">Begin Hour 1: Points to Remember →</a>')
    out.append('<ol class="toc">')
    for h_num, h_title, _, h_desc in all_hours:
        out.append(f'<li><a href="#h{h_num}"><span class="no">{h_num}</span><span class="nm">{html.escape(h_title)}</span><span class="q">{html.escape(h_desc)}</span></a></li>')
    out.append('</ol>')
    out.append('</section>')
    
    # Hours 1 to 72
    for idx, (h_num, h_title, ch_ref, h_desc) in enumerate(all_hours):
        prev_href = f"#h{h_num - 1}" if h_num > 1 else "#home"
        prev_txt = f"← Hour {h_num - 1}" if h_num > 1 else "← Start"
        next_href = f"#h{h_num + 1}" if h_num < 72 else "#home"
        next_txt = f"Hour {h_num + 1} →" if h_num < 72 else "Start →"
        
        matching_ch = next((c for c in chapters if c["num"] == ch_ref), chapters[0])
        sample_pts = [p for t in matching_ch["topics"] for p in t["points"][:3]][:6]
        
        out.append(f'<section class="view" id="h{h_num}" data-n="{h_num}" data-title="Hour {h_num}: {html.escape(h_title)}">')
        out.append(f'<p class="eyebrow">Session {h_num} of 72</p>')
        out.append(f'<h2>{html.escape(h_title)}</h2>')
        out.append(f'<p class="gist">{html.escape(h_desc)}</p>')
        
        out.append('<div class="session-content">')
        out.append('<h3>High-Yield Reading Focus</h3><ul>')
        for pt in sample_pts:
            out.append(f'<li class="pt asked">{pt["html"]}</li>')
        out.append('</ul></div>')
        
        out.append('<div class="done">')
        out.append(f'<button type="button" class="btn btn-tick" data-done="{h_num}" data-h="{h_num}">Mark hour {h_num} done</button>')
        out.append(f'<a class="btn nx" href="{next_href}">{next_txt}</a>')
        out.append('</div>')
        
        out.append(f'<nav class="pn"><a href="{prev_href}">{prev_txt}</a><a class="nx" href="{next_href}">{next_txt}</a></nav>')
        out.append('</section>')
        
    out.append('</main></div>')
    out.append('<div id="scrim"></div>')
    
    # JavaScript
    out.append(js)
    out.append('</body></html>')
    
    full_html = "\n".join(out)
    out_path = os.path.join(ROOT, "Drishti-current affairs", "current-in-72h.html")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(full_html)
        
    print(f"Generated {out_path} ({len(full_html):,} chars, {os.path.getsize(out_path):,} bytes)")

if __name__ == "__main__":
    generate_72h_plan()
