import json
import re
import os
import html
from collections import defaultdict

def generate_72h_plan():
    base_dir = os.path.join("dashboard-src", "subjects", "geography")
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
        # Indian Geography (Hours 1-24)
        (1, "General Introduction", [1]),
        (2, "Physical Division · part 1 of 2", [2]),
        (3, "Physical Division · part 2 of 2", [2]),
        (4, "States and Union Territories of India + Species/Tribes", [3, 4]),
        (5, "Languages of India", [5]),
        (6, "Drainage System · part 1 of 2", [6]),
        (7, "Drainage System · part 2 of 2", [6]),
        (8, "Climate + Natural Disasters", [7, 8]),
        (9, "Soils + Natural Vegetation", [9, 10]),
        (10, "Irrigation and Canals + Multi-Purpose River Valley Project", [11, 12]),
        (11, "Agriculture + Green Revolution", [13, 14]),
        (12, "Food Crops", [15]),
        (13, "Cash Crops + Oilseed", [16, 17]),
        (14, "Pulses to Silk", [18, 19]),
        (15, "Plantation Crops + Jhuming Agriculture", [20, 21]),
        (16, "Agriculture : Miscellaneous + Animal Husbandry", [22, 23]),
        (17, "Mineral Resources", [24]),
        (18, "Miscellaneous : Minerals + Electrical Energy", [25, 26]),
        (19, "Industry", [27]),
        (20, "Research Centres in India", [28]),
        (21, "Transport in India · part 1 of 2", [29]),
        (22, "Transport in India · part 2 of 2", [29]),
        (23, "Tourism", [30]),
        (24, "Indian Geography : Miscellaneous", [31]),

        # World Geography (Hours 25-48)
        (25, "Universe · part 1 of 2", [32]),
        (26, "Universe · part 2 of 2", [32]),
        (27, "Earth", [33]),
        (28, "Rocks to Volcano", [34, 35]),
        (29, "The Earthquake to The Continents", [36, 37]),
        (30, "The World Mountain Ranges", [38]),
        (31, "The Plateaus to Arid Region / Desert", [39, 40, 41]),
        (32, "The Grasslands to Countries and their Borders", [42, 43]),
        (33, "Dependent Territory to International Border Lines", [44, 45, 46, 47]),
        (34, "Capital Cities of the World to Geographical Sobriquets", [48, 49, 50]),
        (35, "Hydrosphere to Ocean Currents", [51, 52, 53]),
        (36, "Salinity of the Ocean to Oceanic Trenches", [54, 55, 56]),
        (37, "Rivers of the World to Landforms by River", [57, 58, 59]),
        (38, "The Island to Lakes and Water Falls", [60, 61]),
        (39, "Straits to The Coral Reefs", [62, 63, 64, 65]),
        (40, "The Atmosphere to Cyclone", [66, 67, 68]),
        (41, "Humidity to Winds", [69, 70, 71, 72]),
        (42, "Local Winds + The Forest", [73, 74]),
        (43, "World Climate to The Soil", [75, 76]),
        (44, "The Major Tribes of the World + Major Languages of the World", [77, 78]),
        (45, "Economic Geography · part 1 of 2", [79]),
        (46, "Economic Geography · part 2 of 2", [79]),
        (47, "World Transport to The Ports and Harbours", [80, 81]),
        (48, "Mapping to World Geography : Miscellaneous", [82, 83]),
    ]

    # Revise hours (49 to 68)
    revise_hours = [
        (49, "Indian High-Yield Revision: Physical Divisions, Passes & Glaciers"),
        (50, "Indian High-Yield Revision: Ganga, Brahmaputra & Peninsular Rivers"),
        (51, "Indian High-Yield Revision: Waterfalls, Lakes & Riverbank Cities"),
        (52, "Indian High-Yield Revision: Monsoon, Rainfall & Winter Rains"),
        (53, "Indian High-Yield Revision: Soils, Vegetation & Forests"),
        (54, "Indian High-Yield Revision: Multipurpose Projects & Canals"),
        (55, "Indian High-Yield Revision: Agriculture, Green Revolution & Cash Crops"),
        (56, "Indian High-Yield Revision: Mineral Belts, Coal & Petroleum"),
        (57, "Indian High-Yield Revision: Nuclear, Thermal & Renewable Energy"),
        (58, "Indian High-Yield Revision: Transport, Highways & Research Centres"),
        (59, "World High-Yield Revision: Universe, Solar System & Planets"),
        (60, "World High-Yield Revision: Latitudes, Longitudes & Earth's Movements"),
        (61, "World High-Yield Revision: Mountain Ranges, Plateaus & Valleys"),
        (62, "World High-Yield Revision: Major Deserts & Global Grasslands"),
        (63, "World High-Yield Revision: Landlocked Countries & Border Lines"),
        (64, "World High-Yield Revision: Ocean Currents, Tides & Salinity"),
        (65, "World High-Yield Revision: World Rivers, Waterfalls & Straits"),
        (66, "World High-Yield Revision: Atmospheric Layers & Pressure Belts"),
        (67, "World High-Yield Revision: Planetary Winds & Local Winds"),
        (68, "World High-Yield Revision: Global Mineral Belts & Industrial Regions"),
    ]

    # Test hours (69 to 72)
    test_hours = [
        (69, "UPPSC Geography Full Mock 1"),
        (70, "UPPSC Geography Full Mock 2"),
        (71, "UPPSC Geography Full Mock 3"),
        (72, "UPPSC Geography Full Mock 4"),
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
    out.append('<title>General Geography in 72 Hours</title>')
    out.append('<meta name="description" content="72 hours before 6 December 2026: hour-by-hour revision plan for General Geography in UPPCS Prelims 2026.">')
    out.append(f'<style>{css}</style></head><body>')
    
    # Header
    out.append('<header class="top" id="top">')
    out.append('<button id="menu" aria-label="Open schedule">☰</button>')
    out.append('<a class="brand" href="#home">Geography in 72h</a>')
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
    out.append('<section class="view on" id="home"><h1>General Geography in 72 Hours</h1>')
    out.append('<p class="gist">72 hours before 6 December 2026 for UPPSC Prelims 2026.</p>')
    out.append('<a class="cta" id="cont" href="#h1">Start with hour 1 →</a>')
    out.append('<p class="lead">Complete syllabus coverage in 48 hours of focused reading, 20 hours of rapid revision, and 4 timed full-length mocks. Every hour has its reading points and real UPPSC PYQs.</p>')
    out.append('<div class="plan-grid">')
    out.append('<div class="card"><h3>Phase 1: Learn</h3><p><b>Hours 1–48</b>: All 83 chapters structured into 48 intensive sessions. Read high-yield summaries and solve matching PYQs.</p><a class="btn" href="#h1">Start Hour 1 →</a></div>')
    out.append('<div class="card"><h3>Phase 2: Revise</h3><p><b>Hours 49–68</b>: 20 rapid revision hours focusing on repeated facts, physical maps, rivers, climate, and mineral belts.</p><a class="btn sec" href="#h49">Jump to Revision →</a></div>')
    out.append('<div class="card"><h3>Phase 3: Test</h3><p><b>Hours 69–72</b>: 4 timed mocks with high-yield questions simulating real UPPSC exam conditions.</p><a class="btn sec" href="#h69">Jump to Tests →</a></div>')
    out.append('</div>')
    out.append('</section>')
    
    # Hours 1 to 48 (Learn)
    for h, title, ch_nums in learn_hours:
        eyebrow = f"Hour {h} of 72 · Learn"
        read_blocks = []
        hour_q_ids = []
        
        for c_num in ch_nums:
            c = ch_dict.get(c_num)
            if not c:
                continue
            hour_q_ids.extend(qs_by_ch.get(c_num, []))
            
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
        rev_idx = (h - 49) * 15
        rev_q_ids = all_q_ids[rev_idx % len(all_q_ids) : (rev_idx % len(all_q_ids)) + 15]
        q_csv = ",".join(rev_q_ids)
        
        out.append(f'<section class="view" id="h{h}" data-n="{h}">')
        out.append(f'<p class="eyebrow">{eyebrow}</p>')
        out.append(f'<h2>{html.escape(title)}</h2>')
        out.append('<div class="reading"><h3>Key Revision Facts</h3><p class="lead">Focus on repeated concepts, comparative tables, and multi-statement statements frequently tested by UPPSC.</p></div>')
        out.append('<div class="practice"><h3>Rapid-Fire Practice</h3>')
        out.append(f'<p class="score"></p><ol class="pq" data-q="{q_csv}"></ol></div>')
        nx_href = f"#h{h+1}" if h < 72 else "#home"
        out.append(f'<div class="done"><button type="button" class="btn" data-done="{h}">Mark hour {h} done</button>')
        out.append(f'<a class="btn nx" href="{nx_href}">Next: Hour {h+1} →</a></div>')
        out.append('</section>')

    # Hours 69 to 72 (Test)
    for h, title in test_hours:
        eyebrow = f"Hour {h} of 72 · Test"
        mock_num = h - 68
        mock_idx = (mock_num - 1) * 35
        mock_q_ids = all_q_ids[mock_idx % len(all_q_ids) : (mock_idx % len(all_q_ids)) + 35]
        q_csv = ",".join(mock_q_ids)
        
        out.append(f'<section class="view" id="h{h}" data-n="{h}">')
        out.append(f'<p class="eyebrow">{eyebrow}</p>')
        out.append(f'<h2>{html.escape(title)}</h2>')
        out.append(f'<div class="reading"><h3>Full Mock Examination {mock_num}</h3><p class="lead">35 selected UPPSC questions covering Indian and World Geography. Test speed, accuracy, and negative-marking discipline.</p></div>')
        out.append('<div class="practice"><h3>Exam Paper</h3>')
        out.append(f'<p class="score"></p><ol class="pq" data-q="{q_csv}"></ol></div>')
        nx_href = f"#h{h+1}" if h < 72 else "#home"
        out.append(f'<div class="done"><button type="button" class="btn" data-done="{h}">Mark hour {h} done</button>')
        out.append(f'<a class="btn nx" href="{nx_href}">Next: Hour {h+1} →</a></div>')
        out.append('</section>')

    # Results view
    out.append('<section class="view" id="results">')
    out.append('<h2 id="rt">Search</h2>')
    out.append('<div id="rl" class="res"></div>')
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
    
    plan_html = "\n".join(out)
    out_path = os.path.join("General_Geography_Part_3", "geography-in-72h.html")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(plan_html)
        
    print(f"Generated {out_path} ({len(plan_html):,} chars)")

if __name__ == "__main__":
    generate_72h_plan()
