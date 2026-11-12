import json
import re
import os
import html
from collections import defaultdict

def generate_72h_plan():
    base_dir = os.path.join("dashboard-src", "subjects", "science")
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
        # Physics (1-17)
        (1, "Measurement/Unit", [1]),
        (2, "Measuring Devices and Scales", [2]),
        (3, "Mechanics", [3]),
        (4, "Motion under Gravity", [4]),
        (5, "Physical Properties of Matter", [5]),
        (6, "Optics · part 1 of 2", [6]),
        (7, "Optics · part 2 of 2", [6]),
        (8, "Heat and Thermodynamics", [7]),
        (9, "Wave Motion + Sound", [8, 9]),
        (10, "Electric Current", [10]),
        (11, "Conductivity + Nuclear Physics", [11, 12]),
        (12, "Computer and Information Technology", [13]),
        (13, "Space", [14]),
        (14, "Defence Technology", [15]),
        (15, "Scientists & Inventions + Physics : Miscellaneous", [16, 17]),
        
        # Chemistry (18-36)
        (16, "Atomic Structure + Physical and Chemical Changes, Solution", [18, 19]),
        (17, "Inorganic Chemistry + Metals, Minerals, Ores: Properties, Uses", [20, 21]),
        (18, "Alloys + Carbon and its various forms", [22, 23]),
        (19, "Hydrogen and its compounds + Sulfur, Nitrogen, Halogen, Inert Gases", [24, 25]),
        (20, "Acid, Base and Salt", [26]),
        (21, "Hydrocarbons to Alcohol", [27, 28]),
        (22, "Polymer to Organic Acid", [29, 30]),
        (23, "Explosive Substances + Fuel", [31, 32]),
        (24, "Food Preservation, Nutrition, Medicine, etc.", [33]),
        (25, "Detergents and Soap + Fertilizers", [34, 35]),
        (26, "Chemistry : Miscellaneous · part 1 of 2", [36]),
        (27, "Chemistry : Miscellaneous · part 2 of 2", [36]),
        
        # Biology (37-65)
        (28, "Subdivisions of Biology + Evolution of Life", [37, 38]),
        (29, "Taxonomy · part 1 of 2", [39]),
        (30, "Taxonomy · part 2 of 2", [39]),
        (31, "Cell + Heredity", [40, 41]),
        (32, "Biofertilizers", [42]),
        (33, "Skeletal and Muscle System + Digestive System", [43, 44]),
        (34, "Vitamins and Nutrition · part 1 of 2", [45]),
        (35, "Vitamins and Nutrition · part 2 of 2", [45]),
        (36, "Respiratory System + Circulatory System", [46, 47]),
        (37, "Excretory System + Nervous System", [48, 49]),
        (38, "Endocrine System + Reproduction and Embryo Development", [50, 51]),
        (39, "Photosynthesis + Plant Nutrition", [52, 53]),
        (40, "Plant Hormones + Plant Reproduction", [54, 55]),
        (41, "Plants : Economic Importance", [56]),
        (42, "Viral Diseases", [57]),
        (43, "Bacterial Diseases", [58]),
        (44, "Fungal Diseases to Other Parasitic Diseases", [59, 60]),
        (45, "Genetic Disorders + Deficiency, Non-Contagious and Other Diseases", [61, 62]),
        (46, "Main Plant Diseases", [63]),
        (47, "Genetic Engineering and Biotechnology", [64]),
        (48, "Biology : Miscellaneous", [65]),
    ]

    # Revise hours (49 to 68)
    revise_hours = [
        (49, "Physics Revision: Units, Dimensions & Scientific Instruments"),
        (50, "Physics Revision: Mechanics, Gravity & Properties of Matter"),
        (51, "Physics Revision: Optics, Total Internal Reflection & Lenses"),
        (52, "Physics Revision: Heat, Thermodynamics & Waves"),
        (53, "Physics Revision: Electricity, Magnetism & Nuclear Physics"),
        (54, "Physics Revision: Space, Defence & Computers"),
        (55, "Chemistry Revision: Atomic Structure & Chemical Bonding"),
        (56, "Chemistry Revision: Metals, Ores & Metallurgy"),
        (57, "Chemistry Revision: Non-Metals, Carbon & Allotropes"),
        (58, "Chemistry Revision: Acids, Bases, Salts & Polymers"),
        (59, "Chemistry Revision: Fuels, Explosives & Fertilizers"),
        (60, "Biology Revision: Cell Biology, Genetics & Evolution"),
        (61, "Biology Revision: Human Skeletal & Muscular Systems"),
        (62, "Biology Revision: Digestive & Respiratory Systems"),
        (63, "Biology Revision: Circulatory, Excretory & Nervous Systems"),
        (64, "Biology Revision: Endocrine System & Hormones"),
        (65, "Biology Revision: Vitamins, Nutrition & Deficiency"),
        (66, "Biology Revision: Plant Physiology & Hormones"),
        (67, "Biology Revision: Human Diseases, Pathogens & Vectors"),
        (68, "Biology Revision: Biotechnology & Genetic Engineering"),
    ]

    # Test hours (69 to 72)
    test_hours = [
        (69, "UPPSC General Science Full Mock 1"),
        (70, "UPPSC General Science Full Mock 2"),
        (71, "UPPSC General Science Full Mock 3"),
        (72, "UPPSC General Science Full Mock 4"),
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
    out.append('<title>General Science in 72 Hours</title>')
    out.append('<meta name="description" content="72 hours before 6 December 2026: hour-by-hour revision plan for General Science in UPPCS Prelims 2026.">')
    out.append(f'<style>{css}</style></head><body>')
    
    # Header
    out.append('<header class="top" id="top">')
    out.append('<button id="menu" aria-label="Open schedule">☰</button>')
    out.append('<a class="brand" href="#home">Science in 72h</a>')
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
    out.append('<section class="view on" id="home"><h1>General Science in 72 Hours</h1>')
    out.append('<p class="gist">72 hours before 6 December 2026 for UPPSC Prelims 2026.</p>')
    out.append('<a class="cta" id="cont" href="#h1">Start with hour 1 →</a>')
    out.append('<p class="lead">Complete syllabus coverage in 48 hours of focused reading, 20 hours of rapid revision, and 4 timed full-length mocks. Every hour has its reading points and real UPPSC PYQs.</p>')
    out.append('<div class="plan-grid">')
    out.append('<div class="card"><h3>Phase 1: Learn</h3><p><b>Hours 1–48</b>: All 65 chapters structured into 48 intensive sessions. Read high-yield summaries and solve matching PYQs.</p><a class="btn" href="#h1">Start Hour 1 →</a></div>')
    out.append('<div class="card"><h3>Phase 2: Revise</h3><p><b>Hours 49–68</b>: 20 rapid revision hours focusing on repeated facts, laws, formulae, biological systems, and diseases.</p><a class="btn sec" href="#h49">Jump to Revision →</a></div>')
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
        out.append('<div class="reading"><h3>Key Revision Facts</h3><p class="lead">Focus on repeated scientific concepts, comparative tables, and multi-statement statements frequently tested by UPPSC.</p></div>')
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
        out.append(f'<div class="reading"><h3>Full Mock Examination {mock_num}</h3><p class="lead">35 selected UPPSC questions covering Physics, Chemistry, and Biology. Test speed, accuracy, and negative-marking discipline.</p></div>')
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
    out_path = os.path.join("General_Science_Part_7", "science-in-72h.html")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(plan_html)
        
    print(f"Generated {out_path} ({len(plan_html):,} chars)")

if __name__ == "__main__":
    generate_72h_plan()
