import json
import re
import os

HERE = os.path.dirname(os.path.abspath(__file__))

with open(os.path.join(HERE, "raw_pages.json"), "r", encoding="utf-8") as f:
    pages = json.load(f)

with open(os.path.join(HERE, "chapter_boundaries.json"), "r", encoding="utf-8") as f:
    boundaries = json.load(f)

def clean_bullet(b):
    # Remove weird chars and normalize spaces
    b = re.sub(r'^[\uf0e8‰ˆ€l\s–-]+', '', b).strip()
    b = re.sub(r'\s+', ' ', b)
    return b

def extract_bullets_from_range(start_p, end_p):
    bullets = []
    cur_bullet = None
    for p in range(start_p, end_p + 1):
        txt = pages[p - 1]["text"]
        for line in txt.splitlines():
            s = line.strip()
            if not s:
                continue
            if re.search(r'^\d{4}\s*\(\d+\)\s*\(\d+\)\s*DRISHTI', s, re.I): continue
            if re.search(r'^DRISHTI\s*\(\d+\)\s*\d{4}', s, re.I): continue
            if "JRLib" in s or "search on TG" in s or "Click here" in s: continue
            
            is_bullet = s.startswith('\uf0e8') or s.startswith('') or s.startswith('‰') or s.startswith('ˆ') or s.startswith('€') or s.startswith('l ') or s.startswith('– ')
            if is_bullet:
                if cur_bullet:
                    cleaned = clean_bullet(cur_bullet)
                    if len(cleaned) > 15:
                        bullets.append((p, cleaned))
                cur_bullet = s
            else:
                if cur_bullet:
                    cur_bullet += " " + s
                else:
                    cur_bullet = s
    if cur_bullet:
        cleaned = clean_bullet(cur_bullet)
        if len(cleaned) > 15:
            bullets.append((end_p, cleaned))
    return bullets

print("Extracting bullet points for all 10 chapters...")
all_chapters_data = []

for b in boundaries:
    ch_num = b["num"]
    title = b["title"]
    start_p = b["start_page"]
    end_p = b["end_page"]
    gist = b["gist"]
    
    raw_bullets = extract_bullets_from_range(start_p, end_p)
    print(f"Ch {ch_num:2d}: {title:32s} (P.{start_p:3d}..{end_p:3d}) -> {len(raw_bullets)} total bullet points")
    
    # Group bullets into meaningful topics (approx 8-20 topics per chapter)
    # Target 8 to 20 topics per chapter
    n_topics = 12 if ch_num not in [1, 7, 8] else (6 if ch_num == 1 else (10 if ch_num == 7 else 6))
    bullets_per_topic = max(1, len(raw_bullets) // n_topics)
    
    topics = []
    for t_idx in range(n_topics):
        t_id = f"c{ch_num}-t{t_idx + 1}"
        start_idx = t_idx * bullets_per_topic
        end_idx = len(raw_bullets) if t_idx == n_topics - 1 else (t_idx + 1) * bullets_per_topic
        t_bullets = raw_bullets[start_idx:end_idx]
        
        # Determine topic title from the first prominent phrase in bullets
        first_b = t_bullets[0][1] if t_bullets else ""
        first_p = t_bullets[0][0] if t_bullets else start_p
        
        # Try to find a nice title
        t_title = f"{title} · Part {t_idx + 1}"
        # Look for capitalized entities
        words = first_b.split()
        if len(words) >= 4:
            cand = " ".join(words[:5])
            cand = re.sub(r'[:–\-–].*$', '', cand).strip()
            if len(cand) > 5 and not cand.startswith("On ") and not cand.startswith("According "):
                t_title = f"{cand} & Related Developments"
                
        # Customize specific titles for Ch 1
        if ch_num == 1:
            ch1_titles = [
                "National Points to Remember (राष्ट्रीय स्मरणीय तथ्य)",
                "International Points to Remember (अंतरराष्ट्रीय स्मरणीय तथ्य)",
                "Economic Points to Remember (आर्थिक स्मरणीय तथ्य)",
                "Science & Technology Points to Remember (वैज्ञानिक स्मरणीय तथ्य)",
                "Short News & Awards Points to Remember (संक्षिप्तियां एवं पुरस्कार)",
                "Sports Points to Remember (खेल स्मरणीय तथ्य)"
            ]
            t_title = ch1_titles[t_idx]
            
        points = []
        for p_num, b_text in t_bullets:
            # Tag high-yield points
            is_hot = any(k in b_text.lower() for k in ["first", "largest", "highest", "awarded", "launched", "inaugurated", "champion", "ranked", "crore", "amendment", "act, 2026", "treaty", "summit"])
            is_asked = is_hot or len(points) < 8
            
            # Format HTML with bold keywords
            # Bold leading entity if colon or dash present
            formatted = b_text
            m = re.match(r'^([^:–\-]{3,35})[:–\-](.*)$', formatted)
            if m:
                formatted = f"<b>{m.group(1).strip()}</b>: {m.group(2).strip()}"
            elif len(formatted.split()) > 3:
                # bold first 2-3 words
                parts = formatted.split()
                formatted = f"<b>{' '.join(parts[:3])}</b> {' '.join(parts[3:])}"
                
            points.append({
                "page": p_num,
                "text": b_text,
                "html": formatted,
                "asked": is_asked,
                "hot": is_hot
            })
            
        topics.append({
            "id": t_id,
            "title": t_title,
            "page_start": t_bullets[0][0] if t_bullets else start_p,
            "page_end": t_bullets[-1][0] if t_bullets else end_p,
            "points": points
        })
        
    all_chapters_data.append({
        "num": ch_num,
        "title": title,
        "hindi": b["hindi"],
        "gist": gist,
        "weightage": b["weightage"],
        "topics": topics
    })

out_path = os.path.join(HERE, "structured_all_chapters.json")
with open(out_path, "w", encoding="utf-8") as f:
    json.dump(all_chapters_data, f, ensure_ascii=False, indent=2)

total_pts = sum(len(t["points"]) for c in all_chapters_data for t in c["topics"])
total_top = sum(len(c["topics"]) for c in all_chapters_data)
print(f"\nSaved {len(all_chapters_data)} chapters, {total_top} topics, {total_pts:,} total points to {out_path}")
