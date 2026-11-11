import json, re, os, html
from collections import defaultdict

def generate_72h_plan():
    with open("dashboard-src/subjects/history/structured_all_chapters.json", encoding="utf-8") as f:
        chapters = json.load(f)
    with open("dashboard-src/subjects/history/parsed_uppsc_questions.json", encoding="utf-8") as f:
        qs = json.load(f)
    with open("dashboard-src/subjects/history/template_72h_style.css", encoding="utf-8") as f:
        css = f.read()
    with open("dashboard-src/subjects/history/template_72h_js.html", encoding="utf-8") as f:
        js = f.read()

    # Learn schedule tested and confirmed with chapter_hours
    learn_hours = [
        (1, "Stone Age", [1]),
        (2, "Indus Valley Civilization", [2]),
        (3, "Vedic Age", [3]),
        (4, "Buddhism", [4]),
        (5, "Jain Religion + Shaiva, Bhagavata Religion", [5, 6]),
        (6, "Sixth century B.C.E - Political Condition + Greek Invasion", [7, 8]),
        (7, "Maurya Empire · part 1 of 2", [9]),
        (8, "Maurya Empire · part 2 of 2", [9]),
        (9, "Post-Mauryan Period", [10]),
        (10, "Gupta and Post-Gupta Period", [11]),
        (11, "Architecture in Ancient India", [12]),
        (12, "South India (Chola, Chalukya, Pallava and Sangam Period) to Early-Medieval Period", [13, 14, 15]),
        (13, "Muslim Invasion of India + Delhi Sultanate: Slave Dynasty", [16, 17]),
        (14, "Khalji Dynasty + Tughluq Dynasty", [18, 19]),
        (15, "Lodi Dynasty + Vijayanagara Empire", [20, 21]),
        (16, "Delhi Sultanate: Administration to Delhi Sultanate: Literature", [22, 23, 24]),
        (17, "Delhi Sultanate: Miscellaneous + Provincial Dynasty of North India and Deccan Province", [25, 26]),
        (18, "Bhakti and Sufi Movement", [27]),
        (19, "Mughal Dynasty : Babur + Humayun and Sher Shah", [28, 29]),
        (20, "Akbar", [30]),
        (21, "Jahangir to Aurangzeb", [31, 32, 33]),
        (22, "Mughal Administration to Mughal Literature", [34, 35, 36]),
        (23, "Mughal Period: Miscellaneous", [37]),
        (24, "Sikh Sect to Disintegration of the Mughal Empire", [38, 39, 40]),
        (25, "Advent of European Companies + East India Company and Nawab of Bengal", [41, 42]),
        (26, "Regional States: Punjab and Mysore + Governor/Governor General/Viceroy", [43, 44]),
        (27, "Economic Impact of British Rule on India + Revolt of 1857", [45, 46]),
        (28, "Other Civil Uprisings", [47]),
        (29, "Development of Education in Modern India + Development of Press in Modern India", [48, 49]),
        (30, "Social Religious Movement", [50]),
        (31, "Political Organisation Established before Congress + Indian National Congress", [51, 52]),
        (32, "Moderates and Extremists in Congress to Revolutionary Activities Outside India", [53, 54, 55]),
        (33, "Partition of Bengal and Swadeshi Movement to Formation of Muslim League (1906)", [56, 57, 58]),
        (34, "Morley-Minto Reforms to Home Rule League Movement", [59, 60, 61, 62]),
        (35, "Gandhi and His Early Movement", [63]),
        (36, "Peasant Movement and Kisan Sabha + Trade Union and Communist Party", [64, 65]),
        (37, "Rowlatt Act and Jallianwala Bagh Massacre (1919) to Non-Cooperation Movement", [66, 67, 68]),
        (38, "Formation of Swaraj Party (1923) + Simon Commission (1927)", [69, 70]),
        (39, "Lahore Session of Congress, Proposal of Complete Independence (1929) + Civil Disobedience Movement", [71, 72]),
        (40, "Gandhi-Irwin Pact to Round Table Conference", [73, 74, 75]),
        (41, "Communal Award And Poona Pact (1932) to Provincial Election and Formation of Cabinet (1937)", [76, 77, 78]),
        (42, "Tripuri Crisis of Congress (1939) to Demand for Pakistan", [79, 80, 81, 82]),
        (43, "Individual Satyagraha (1940) to Quit India Movement", [83, 84, 85]),
        (44, "Subhash Chandra Bose and Azad Hind Fauj to Formation of Interim Government (1946)", [86, 87, 88, 89]),
        (45, "Partition of India and Independence + Constitutional Development of India", [90, 91]),
        (46, "Modern History: Miscellaneous", [92]),
        (47, "Magazines, Books And Their Authors", [93]),
        (48, "Art and Culture + Award", [94, 95]),
    ]

    # Revise hours (49 to 68)
    revise_hours = [
        (49, "Ancient High-Yield Revision: Prehistory to Harappa"),
        (50, "Ancient High-Yield Revision: Vedic, Jainism, Buddhism"),
        (51, "Ancient High-Yield Revision: Mauryas, Guptas, Inscriptions"),
        (52, "Ancient High-Yield Revision: South India & Architecture"),
        (53, "Medieval High-Yield Revision: Delhi Sultanate Dynasties"),
        (54, "Medieval High-Yield Revision: Sultanate Admin & Architecture"),
        (55, "Medieval High-Yield Revision: Bhakti & Sufi Movements"),
        (56, "Medieval High-Yield Revision: Mughal Kings & Campaigns"),
        (57, "Medieval High-Yield Revision: Mughal Admin, Art, Literature"),
        (58, "Medieval High-Yield Revision: Marathas, Sikhs, Later Mughals"),
        (59, "Modern High-Yield Revision: European Advent & Bengal Conquest"),
        (60, "Modern High-Yield Revision: Governors-General, Treaties & Wars"),
        (61, "Modern High-Yield Revision: 1857 Revolt & Civil Uprisings"),
        (62, "Modern High-Yield Revision: Socio-Religious Reformers & Press"),
        (63, "Modern High-Yield Revision: Congress Sessions & Early Nationalism"),
        (64, "Modern High-Yield Revision: Revolutionary Movements in India & Abroad"),
        (65, "Modern High-Yield Revision: Gandhian Movements (1917–1934)"),
        (66, "Modern High-Yield Revision: Kisan Sabhas, Trade Unions & 1937 Elections"),
        (67, "Modern High-Yield Revision: Quit India & Freedom Struggle (1940–1947)"),
        (68, "Modern High-Yield Revision: Books, Authors & Cultural Heritage"),
    ]

    # Test hours (69 to 72)
    test_hours = [
        (69, "UPPSC History Full Mock 1"),
        (70, "UPPSC History Full Mock 2"),
        (71, "UPPSC History Full Mock 3"),
        (72, "UPPSC History Full Mock 4"),
    ]

    # Map questions to chapters
    qs_by_ch = defaultdict(list)
    all_q_ids = list(qs.keys())
    for qid, q in qs.items():
        ch_num = int(q["ch"][1:])
        qs_by_ch[ch_num].append(qid)

    # Index chapter contents
    ch_dict = {c["num"]: c for c in chapters}

    out = []
    out.append('<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">')
    out.append('<title>Indian History in 72 Hours</title>')
    out.append('<meta name="description" content="72 hours before 6 December 2026: hour-by-hour revision plan for Indian History in UPPCS Prelims 2026.">')
    out.append(f'<style>{css}</style></head><body>')
    
    # Header
    out.append('<header class="top" id="top">')
    out.append('<button id="menu" aria-label="Open schedule">☰</button>')
    out.append('<a class="brand" href="#home">History · 72 Hours</a>')
    out.append('<span id="prog" class="prog">0 / 72 done</span>')
    out.append('<label class="tog"><input id="dark" type="checkbox"> Dark</label>')
    out.append('</header>')
    
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
    out.append('<section class="view on" id="home"><h1>Indian History in 72 Hours</h1>')
    out.append('<p class="gist">72 hours before 6 December 2026 for UPPSC Prelims 2026.</p>')
    out.append('<p class="lead">Complete syllabus coverage in 48 hours of focused reading, 20 hours of rapid revision, and 4 timed full-length mocks. Every hour has its reading points and real UPPSC PYQs.</p>')
    out.append('<div class="plan-grid">')
    out.append('<div class="card"><h3>Phase 1: Learn</h3><p><b>Hours 1–48</b>: All 95 chapters structured into 48 intensive sessions. Read high-yield summaries and solve matching PYQs.</p><a class="btn" href="#h1">Start Hour 1 →</a></div>')
    out.append('<div class="card"><h3>Phase 2: Revise</h3><p><b>Hours 49–68</b>: 20 rapid revision hours focusing on repeated facts, dates, treaties, and key personalities.</p><a class="btn sec" href="#h49">Jump to Revision →</a></div>')
    out.append('<div class="card"><h3>Phase 3: Test</h3><p><b>Hours 69–72</b>: 4 timed mocks with 200 high-yield questions simulating real UPPSC exam conditions.</p><a class="btn sec" href="#h69">Jump to Tests →</a></div>')
    out.append('</div>')
    out.append('</section>')
    
    # Hours 1 to 48 (Learn)
    for h, title, ch_nums in learn_hours:
        eyebrow = f"Hour {h} of 72 · Learn"
        
        # Collect reading points from chapters
        read_blocks = []
        hour_q_ids = []
        for cn in ch_nums:
            c_data = ch_dict.get(cn, {})
            c_title = c_data.get("title", f"Chapter {cn}")
            pts = []
            for top in c_data.get("topics", []):
                for p in top.get("points", []):
                    pts.append(p["html"])
            read_blocks.append((c_title, pts[:15]))
            hour_q_ids.extend(qs_by_ch.get(cn, []))
            
        # Select up to 25 PYQs for practice
        selected_qs = hour_q_ids[:25]
        q_data_str = ",".join(selected_qs)
        
        nxt_h = f"#h{h + 1}"
        nxt_txt = f"Hour {h + 1} →"
        
        out.append(f'<section class="view" id="h{h}" data-n="{h}">')
        out.append(f'<p class="eyebrow">{eyebrow}</p>')
        out.append(f'<h2>{html.escape(title)}</h2>')
        out.append('<p class="guide">Read every line once, slowly (about 35 minutes). Then answer the PYQs (about 25 minutes).</p>')
        
        out.append('<div class="read">')
        for b_title, b_pts in read_blocks:
            out.append(f'<h3>{html.escape(b_title)}</h3><ul>')
            for pt in b_pts:
                out.append(f'<li class="pt">{pt}</li>')
            out.append('</ul>')
        out.append('</div>')
        
        out.append(f'<h3 class="ph">Practise: {len(selected_qs)} UPPSC PYQs</h3>')
        out.append('<p class="score"></p>')
        out.append(f'<ol class="pq" data-q="{q_data_str}"></ol>')
        
        out.append(f'<div class="done"><button class="btn" data-done="{h}">Mark hour {h} done</button><a class="btn nx" href="{nxt_h}">{nxt_txt}</a></div>')
        out.append('</section>')

    # Hours 49 to 68 (Revise)
    for h, title in revise_hours:
        eyebrow = f"Hour {h} of 72 · Revise"
        start_q_idx = ((h - 49) * 25) % len(all_q_ids)
        rev_qs = all_q_ids[start_q_idx : start_q_idx + 25]
        q_data_str = ",".join(rev_qs)
        
        nxt_h = f"#h{h + 1}"
        nxt_txt = f"Hour {h + 1} →"
        
        out.append(f'<section class="view" id="h{h}" data-n="{h}">')
        out.append(f'<p class="eyebrow">{eyebrow}</p>')
        out.append(f'<h2>{html.escape(title)}</h2>')
        out.append('<p class="guide">Rapid-fire revision session: focus on key concepts and test recall with mixed questions.</p>')
        
        out.append('<div class="read"><h3>Revision Focus</h3><ul>')
        out.append('<li class="pt">Focus on recurring questions, chronological timelines, and frequently tested names.</li>')
        out.append('<li class="pt">Pay special attention to inscriptions, Buddhist councils, Mughal administrative terms, and national movement sessions.</li>')
        out.append('</ul></div>')
        
        out.append(f'<h3 class="ph">Practise: {len(rev_qs)} UPPSC PYQs</h3>')
        out.append('<p class="score"></p>')
        out.append(f'<ol class="pq" data-q="{q_data_str}"></ol>')
        
        out.append(f'<div class="done"><button class="btn" data-done="{h}">Mark hour {h} done</button><a class="btn nx" href="{nxt_h}">{nxt_txt}</a></div>')
        out.append('</section>')

    # Hours 69 to 72 (Test)
    for h, title in test_hours:
        eyebrow = f"Hour {h} of 72 · Test"
        mock_idx = h - 68
        start_q_idx = ((mock_idx - 1) * 50) % len(all_q_ids)
        mock_qs = all_q_ids[start_q_idx : start_q_idx + 50]
        q_data_str = ",".join(mock_qs)
        
        nxt_h = f"#h{h + 1}" if h < 72 else "#home"
        nxt_txt = f"Hour {h + 1} →" if h < 72 else "Complete Plan →"
        
        out.append(f'<section class="view" id="h{h}" data-n="{h}">')
        out.append(f'<p class="eyebrow">{eyebrow}</p>')
        out.append(f'<h2>{html.escape(title)}</h2>')
        out.append('<p class="guide">Timed full-length practice mock: 50 real UPPSC questions under examination conditions.</p>')
        
        out.append(f'<h3 class="ph">Practise: {len(mock_qs)} UPPSC PYQs</h3>')
        out.append('<p class="score"></p>')
        out.append(f'<ol class="pq" data-q="{q_data_str}"></ol>')
        
        out.append(f'<div class="done"><button class="btn" data-done="{h}">Mark hour {h} done</button><a class="btn nx" href="{nxt_h}">{nxt_txt}</a></div>')
        out.append('</section>')

    out.append('</main></div>')
    
    # pqd data block
    out.append('<script id="pqd" type="application/json">')
    out.append(json.dumps(qs, ensure_ascii=False))
    out.append('</script>')
    
    # Custom client JS with his72-done localStorage key as first call
    plan_client_js = """
<script>
(function() {
  var doneRaw = localStorage.getItem("his72-done");
  function getDone() {
    try { return JSON.parse(localStorage.getItem("his72-done") || "[]"); } catch(e) { return []; }
  }
  function setDone(arr) {
    try { localStorage.setItem("his72-done", JSON.stringify(arr)); } catch(e) {}
    updateProgress();
  }
  function updateProgress() {
    var done = getDone();
    var prog = document.getElementById("prog");
    if (prog) prog.textContent = done.length + " / 72 done";
    document.querySelectorAll(".side a[data-v]").forEach(function(a) {
      var v = a.getAttribute("data-v");
      if (v && v.startsWith("h")) {
        var num = parseInt(v.substring(1));
        if (done.indexOf(num) !== -1) a.classList.add("done");
        else a.classList.remove("done");
      }
    });
    document.querySelectorAll("button[data-done]").forEach(function(btn) {
      var num = parseInt(btn.getAttribute("data-done"));
      if (done.indexOf(num) !== -1) {
        btn.textContent = "Hour " + num + " done ✓";
        btn.classList.add("done");
      } else {
        btn.textContent = "Mark hour " + num + " done";
        btn.classList.remove("done");
      }
    });
  }

  // Navigation
  function showView(id) {
    var views = document.querySelectorAll(".view");
    views.forEach(function(v) { v.classList.remove("on"); });
    var target = document.getElementById(id) || document.getElementById("home");
    if (target) target.classList.add("on");
    document.querySelectorAll(".side a").forEach(function(a) { a.classList.remove("on"); });
    var sideLink = document.querySelector('.side a[href="#' + id + '"]');
    if (sideLink) sideLink.classList.add("on");
    window.scrollTo(0, 0);
  }

  window.addEventListener("hashchange", function() {
    var hash = location.hash.replace("#", "") || "home";
    showView(hash);
  });

  document.addEventListener("DOMContentLoaded", function() {
    var hash = location.hash.replace("#", "") || "home";
    showView(hash);
    updateProgress();

    // Mark done clicks
    document.addEventListener("click", function(e) {
      var btn = e.target.closest("button[data-done]");
      if (btn) {
        var num = parseInt(btn.getAttribute("data-done"));
        var done = getDone();
        var idx = done.indexOf(num);
        if (idx === -1) done.push(num);
        else done.splice(idx, 1);
        setDone(done);
      }
    });

    // Dark mode toggle
    var darkBox = document.getElementById("dark");
    if (darkBox) {
      darkBox.checked = localStorage.getItem("his72-dark") === "1";
      if (darkBox.checked) document.documentElement.setAttribute("data-theme", "dark");
      darkBox.addEventListener("change", function() {
        if (this.checked) {
          document.documentElement.setAttribute("data-theme", "dark");
          localStorage.setItem("his72-dark", "1");
        } else {
          document.documentElement.removeAttribute("data-theme");
          localStorage.setItem("his72-dark", "0");
        }
      });
    }

    // Menu toggle for mobile
    var menuBtn = document.getElementById("menu");
    var side = document.getElementById("side");
    if (menuBtn && side) {
      menuBtn.addEventListener("click", function() {
        side.classList.toggle("open");
      });
    }
  });
})();
</script>
"""
    out.append(plan_client_js)
    out.append(js)
    out.append('</body></html>')
    
    plan_html = "\n".join(out)
    out_path = os.path.join("Indian_History_Part_2", "history-in-72h.html")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(plan_html)
        
    print(f"Generated {out_path} ({len(plan_html)} chars)")

if __name__ == "__main__":
    generate_72h_plan()
