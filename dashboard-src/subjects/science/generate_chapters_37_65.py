import json
import re
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from science_helpers import clean_fact, inject_hindi

base_dir = os.path.dirname(os.path.abspath(__file__))

with open(os.path.join(base_dir, "raw_pages.json"), encoding="utf-8") as f:
    pages = json.load(f)

with open(os.path.join(base_dir, "chapter_boundaries.json"), encoding="utf-8") as f:
    boundaries = json.load(f)

with open(os.path.join(base_dir, "parsed_uppsc_questions.json"), encoding="utf-8") as f:
    qs = json.load(f)

qs_by_ch = {}
for qid, q in qs.items():
    ch_num = int(q["ch"][1:])
    if ch_num not in qs_by_ch:
        qs_by_ch[ch_num] = []
    q["qid"] = qid
    qs_by_ch[ch_num].append(q)

def extract_notes_text(sp, ep):
    notes_lines = []
    in_notes = False
    for p in range(sp, ep + 1):
        txt = pages[p - 1]["text"]
        lines = [l.strip() for l in txt.split("\n") if l.strip()]
        for l in lines:
            if re.match(r'^(?:Question Bank|\d{1,3}\.\s+)', l, re.I):
                in_notes = False
            elif re.match(r'^Notes\b', l, re.I):
                in_notes = True
                continue
            if in_notes:
                notes_lines.append(l)
    return notes_lines

def generate_chapter(ch_num):
    b = boundaries[ch_num - 1]
    title = b["title"]
    part = b["part"]
    sp = b["start_page"]
    ep = b["end_page"]
    ch_qs = qs_by_ch.get(ch_num, [])
    
    gist = f"Comprehensive short notes on {title} ({part}) with key concepts, definitions, and real UPPSC previous year questions."
    
    # Focus
    focus = []
    seen_focus = set()
    sorted_qs = sorted(ch_qs, key=lambda q: (-q.get("n", 1), -q.get("y", 2000)))
    for q in sorted_qs:
        f_text = clean_fact(q.get("f", ""))
        if not f_text or "See the explanation" in f_text or len(f_text) < 15:
            ans_opts = [q["o"][k_idx] for k_idx in q["k"] if k_idx < len(q["o"])]
            ans_txt = ", ".join(ans_opts) if ans_opts else ""
            f_text = f"{q['s']} → <b>{ans_txt}</b>."
        norm = re.sub(r'[^a-zA-Z0-9]', '', f_text.lower())[:45]
        if norm in seen_focus:
            continue
        seen_focus.add(norm)
        n_p = q.get("n", 1)
        focus.append({
            "fact": f_text[:140] + ("..." if len(f_text) > 140 else ""),
            "exam": q["e"],
            "cnt": f"{n_p} paper{'s' if n_p > 1 else ''}"
        })
        if len(focus) >= 5:
            break
            
    # Extract book bullets
    notes_raw = extract_notes_text(sp, ep)
    bullet_items = []
    cur_bullet = []
    for l in notes_raw:
        if l.startswith("•") or l.startswith("-") or re.match(r'^\d+\.\s+', l):
            if cur_bullet:
                bullet_items.append(" ".join(cur_bullet))
                cur_bullet = []
            cur_bullet.append(re.sub(r'^[•\-\d\.]+\s*', '', l))
        elif cur_bullet:
            cur_bullet.append(l)
        elif len(l) > 20 and not re.search(r'General Studies|General Science', l):
            bullet_items.append(l)
    if cur_bullet:
        bullet_items.append(" ".join(cur_bullet))
        
    num_topics = max(2, min(4, len(ch_qs) // 6 + 1))
    topic_size = max(1, len(ch_qs) // num_topics) if ch_qs else 1
    
    topics = []
    for t_i in range(num_topics):
        t_id = f"c{ch_num}-t{t_i+1}"
        p_sub_start = sp + t_i * max(1, (ep - sp + 1) // num_topics)
        p_sub_end = min(ep, sp + (t_i + 1) * max(1, (ep - sp + 1) // num_topics) - 1) if t_i < num_topics - 1 else ep
        pg_str = f"pp. {p_sub_start}–{p_sub_end}" if p_sub_start != p_sub_end else f"p. {p_sub_start}"
        
        if num_topics == 1:
            t_title = f"{title}: Core Concepts & Biological Systems"
        elif t_i == 0:
            t_title = f"{title}: Structure, Anatomy & Functions"
        elif t_i == 1:
            t_title = f"{title}: Physiological Processes & Mechanisms"
        elif t_i == 2:
            t_title = f"{title}: Pathology, Traps & High-Yield PYQs"
        else:
            t_title = f"{title}: Advanced Classifications & Observations"
            
        t_title = inject_hindi(t_title)
        
        pts = []
        seen_pts = set()
        
        b_slice = bullet_items[t_i * (len(bullet_items)//num_topics) : (t_i + 1) * (len(bullet_items)//num_topics)] if bullet_items else []
        for b_text in b_slice[:8]:
            clean_b = inject_hindi(clean_fact(b_text))
            if len(clean_b) > 20:
                norm = re.sub(r'[^a-zA-Z0-9]', '', clean_b.lower())[:40]
                if norm not in seen_pts:
                    seen_pts.add(norm)
                    pts.append({"html": clean_b, "asked": False, "hot": False})
                    
        q_slice = ch_qs[t_i * topic_size : (t_i + 1) * topic_size] if t_i < num_topics - 1 else ch_qs[t_i * topic_size :]
        for q in q_slice:
            q["h"] = t_id
            f_text = clean_fact(q.get("f", ""))
            if not f_text or "See the explanation" in f_text or len(f_text) < 15:
                ans_opts = [q["o"][k_idx] for k_idx in q["k"] if k_idx < len(q["o"])]
                ans_txt = ", ".join(ans_opts) if ans_opts else ""
                f_text = f"<b>{q['s']}</b> → {ans_txt}."
            else:
                f_text = re.sub(r'\s+', ' ', f_text).strip()
                if len(f_text) > 350:
                    f_text = f_text[:350] + "..."
            
            f_text = inject_hindi(f_text)
            norm = re.sub(r'[^a-zA-Z0-9]', '', f_text.lower())[:40]
            if norm not in seen_pts:
                seen_pts.add(norm)
                pts.append({
                    "html": f_text,
                    "asked": True,
                    "hot": q.get("n", 1) >= 2
                })
                
        topics.append({
            "id": t_id,
            "title": t_title,
            "pg": pg_str,
            "points": pts
        })
        
    return {
        "num": ch_num,
        "title": title,
        "part": part,
        "gist": gist,
        "focus": focus,
        "topics": topics
    }

def main():
    print("Generating Chapters 37 to 65 (Biology)...")
    chapters = []
    for c_num in range(37, 66):
        ch = generate_chapter(c_num)
        chapters.append(ch)
        print(f"  Ch {c_num:02d}: {ch['title']} ({len(ch['topics'])} topics, {sum(len(t['points']) for t in ch['topics'])} pts)")
        
    out_file = os.path.join(base_dir, "chapters_37_65.json")
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(chapters, f, indent=2, ensure_ascii=False)
    print(f"Successfully saved {out_file} ({os.path.getsize(out_file):,} bytes)")

if __name__ == "__main__":
    main()
