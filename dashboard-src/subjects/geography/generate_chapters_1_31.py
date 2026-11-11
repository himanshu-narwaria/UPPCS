import sys, json, re, os
sys.path.insert(0, 'dashboard-src/subjects/geography')
from chapter_definitions_1_31 import CHAPTER_DATA
from test_helpers import inject_hindi, clean_fact

with open("dashboard-src/subjects/geography/accurate_chapter_ranges.json", encoding="utf-8") as f:
    ranges = json.load(f)

with open("dashboard-src/subjects/geography/parsed_uppsc_questions.json", encoding="utf-8") as f:
    qs = json.load(f)

qs_by_ch = {}
for qid, q in qs.items():
    ch_num = int(q["ch"][1:])
    if ch_num not in qs_by_ch:
        qs_by_ch[ch_num] = []
    q["qid"] = qid
    qs_by_ch[ch_num].append(q)

def build_chapter(ch_num):
    r_entry = ranges[ch_num - 1]
    title = r_entry["title"]
    section = "Indian Geography"
    ch_def = CHAPTER_DATA[ch_num]
    gist = ch_def["gist"]
    ch_qs = qs_by_ch.get(ch_num, [])
    
    # Focus
    focus = []
    seen_focus = set()
    sorted_qs = sorted(ch_qs, key=lambda q: (-q.get("n", 1), -q.get("y", 2000)))
    for q in sorted_qs:
        f_text = clean_fact(q.get("f", ""))
        if not f_text or "See the explanation" in f_text or len(f_text) < 15:
            ans_opts = [q["o"][k_idx] for k_idx in q["k"] if k_idx < len(q["o"])]
            ans_txt = ", ".join(ans_opts) if ans_opts else ""
            f_text = f"{q['s']} → {ans_txt}."
        f_text = re.sub(r'\s+', ' ', f_text).strip()
        norm_key = re.sub(r'[^a-zA-Z0-9]', '', f_text.lower())[:45]
        if norm_key in seen_focus:
            continue
        seen_focus.add(norm_key)
        
        n_papers = q.get("n", 1)
        focus.append({
            "fact": f_text[:140] + ("..." if len(f_text) > 140 else ""),
            "exam": q["e"],
            "cnt": f"{n_papers} paper{'s' if n_papers > 1 else ''}"
        })
        if len(focus) >= 5:
            break
            
    # Topics
    topics_out = []
    p_start = r_entry["pdf_start"]
    p_end = r_entry["pdf_end"]
    num_topics = len(ch_def["topics"])
    p_step = max(1, (p_end - p_start + 1) // num_topics)
    
    assigned = {t["id"]: [] for t in ch_def["topics"]}
    for q in ch_qs:
        text = (q["s"] + " " + q.get("f", "")).lower()
        best_t = ch_def["topics"][0]["id"]
        best_score = 0
        for t in ch_def["topics"]:
            score = sum(1 for kw in t.get("keywords", []) if kw in text)
            if score > best_score:
                best_score = score
                best_t = t["id"]
        if best_score == 0:
            best_t = min(assigned.keys(), key=lambda k: len(assigned[k]))
        assigned[best_t].append(q)
        
    for t_idx, t in enumerate(ch_def["topics"]):
        t_id = t["id"]
        t_title = t["title"]
        t_start = p_start + t_idx * p_step
        t_end = min(p_end, p_start + (t_idx + 1) * p_step - 1) if t_idx < num_topics - 1 else p_end
        t_pg = f"pp. {t_start}–{t_end}"
        
        pts = []
        seen_pts = set()
        # Curated points
        for cp in t.get("points", []):
            cp_clean = inject_hindi(clean_fact(cp))
            norm = re.sub(r'[^a-zA-Z0-9]', '', cp_clean.lower())[:40]
            if norm not in seen_pts:
                seen_pts.add(norm)
                pts.append({"html": cp_clean, "hot": False, "asked": False})
                
        # Asked points from UPPSC
        for q in assigned[t_id]:
            f_text = clean_fact(q.get("f", ""))
            if not f_text or "See the explanation" in f_text or len(f_text) < 15:
                ans_opts = [q["o"][k_idx] for k_idx in q["k"] if k_idx < len(q["o"])]
                ans_txt = ", ".join(ans_opts) if ans_opts else ""
                f_text = f"{q['s']} → <b>{ans_txt}</b>."
            else:
                f_text = re.sub(r'\s+', ' ', f_text).strip()
                if len(f_text) > 320:
                    f_text = f_text[:317] + "..."
            
            norm = re.sub(r'[^a-zA-Z0-9]', '', f_text.lower())[:45]
            if norm in seen_pts:
                continue
            seen_pts.add(norm)
            
            is_hot = q.get("n", 1) >= 2
            cnt_str = f" ×{q['n']}" if is_hot else ""
            badge = f'<span class="ps"><span class="p up" title="{q["e"]}">UPPSC{cnt_str}</span></span>'
            pt_html = f"{inject_hindi(f_text)} {badge}"
            pts.append({"html": pt_html, "hot": is_hot, "asked": True})
            
        topics_out.append({
            "id": t_id,
            "title": t_title,
            "pg": t_pg,
            "points": pts
        })
        
    return {
        "num": ch_num,
        "title": title,
        "section": section,
        "gist": gist,
        "focus": focus,
        "topics": topics_out
    }

def main():
    all_ch1_31 = []
    for c_num in range(1, 32):
        ch_data = build_chapter(c_num)
        all_ch1_31.append(ch_data)
        
    out_file = "dashboard-src/subjects/geography/chapters_1_31.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(all_ch1_31, f, indent=2, ensure_ascii=False)
        
    print(f"Successfully generated {len(all_ch1_31)} chapters at {out_file}")

if __name__ == "__main__":
    main()
