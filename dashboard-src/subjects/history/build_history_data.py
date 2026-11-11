import json, re, os
from collections import Counter, defaultdict

def load_data():
    with open("dashboard-src/subjects/history/raw_pages.json", encoding="utf-8") as f:
        pages = json.load(f)
    with open("dashboard-src/subjects/history/accurate_ranges.json", encoding="utf-8") as f:
        ranges = json.load(f)
    return pages, ranges

def is_uppsc(line):
    if re.search(r'\b(Uttarakhand|U\.?K\.?)\b', line, re.I):
        return False
    return bool(re.search(r'\b(U\.?P\.?P?\.?C\.?S|U\.?P\.?\s*P\.?S\.?C|U\.?P\.?\s*Lower|U\.?P\.?\s*R\.?O|U\.?P\.?\s*A\.?R\.?O|U\.?P\.?\s*U\.?D\.?A|U\.?P\.?\s*L\.?D\.?A|U\.?P\.?\s*G\.?I\.?C|U\.?P\.?\s*G\.?D\.?C|U\.?P\.?\s*B\.?E\.?O|U\.?P\.?\s*R\.?I)\b', line, re.I))

def format_uppsc_exam(line):
    y_m = re.search(r'\b(19\d\d|20[0-2]\d)\b', line)
    year = int(y_m.group(1)) if y_m else 2000
    y_short = f"’{str(year)[-2:]}"
    is_spl = bool(re.search(r'\b(Spl|Special)\b', line, re.I))
    spl_str = " (Spl)" if is_spl else ""
    
    if re.search(r'GIC', line, re.I):
        lbl = f"GIC{spl_str} {y_short}"
    elif re.search(r'BEO|B\.E\.O', line, re.I):
        lbl = f"BEO{spl_str} {y_short}"
    elif re.search(r'\bRI\b', line, re.I):
        lbl = f"RI{spl_str} {y_short}"
    elif re.search(r'R\.?O|A\.?R\.?O', line, re.I):
        mains = bool(re.search(r'Mains', line, re.I))
        lbl = f"RO/ARO{' Mains' if mains else ' Pre'}{spl_str} {y_short}"
    elif re.search(r'U\.?D\.?A|L\.?D\.?A', line, re.I):
        mains = bool(re.search(r'Mains', line, re.I))
        lbl = f"UDA/LDA{' Mains' if mains else ' Pre'}{spl_str} {y_short}"
    elif re.search(r'Lower', line, re.I):
        mains = bool(re.search(r'Mains', line, re.I))
        lbl = f"Lower Sub{' Mains' if mains else ''}{spl_str} {y_short}"
    else:
        mains = bool(re.search(r'Mains', line, re.I))
        lbl = f"PCS{' Mains' if mains else ' Pre'}{spl_str} {y_short}"
    return lbl, year

def clean_text(t):
    t = re.sub(r'B–\d+ General Studies Indian History', '', t)
    t = re.sub(r'Indian History General Studies B–\d+', '', t)
    t = re.sub(r'Indian HistoryB–\d+', '', t)
    t = re.sub(r'click here -@freepdfhall', '', t)
    t = re.sub(r'search on TG-@freepdfhall', '', t)
    t = re.sub(r'\s+', ' ', t).strip()
    return t

def parse_all_chapters():
    pages, ranges = load_data()
    q_global_id = 1
    all_qs = {}
    chapter_stats = []

    for i, entry in enumerate(ranges):
        ch_num = entry["num"]
        ch_title = entry["title"]
        start_p = entry["start"]
        end_p = ranges[i + 1]["start"] - 1 if i + 1 < len(ranges) else len(pages)
        ch_text = "\n".join(pages[p-1]["text"] for p in range(start_p, end_p + 1))
        
        q_splits = re.split(r'\n\s*(\d{1,3})\.\s+', '\n' + ch_text)
        intro_raw = q_splits[0].strip()
        intro = clean_text(intro_raw)
        
        ch_qs = []
        for j in range(1, len(q_splits), 2):
            q_no = int(q_splits[j])
            body = q_splits[j+1]
            
            uppsc_lines = []
            lines = body.split('\n')
            ans_idx = None
            for idx, l in enumerate(lines):
                if re.search(r'Ans\.', l):
                    ans_idx = idx
                    break
                if is_uppsc(l.strip()):
                    uppsc_lines.append(l.strip())
                    
            if not uppsc_lines:
                continue
                
            pre_ans = "\n".join(lines[:ans_idx]) if ans_idx is not None else body
            post_ans = "\n".join(lines[ans_idx:]) if ans_idx is not None else ""
            
            ans_m = re.search(r'Ans\.\s*\((.*?)\)', post_ans)
            ans_str = ans_m.group(1).lower() if ans_m else ""
            k = []
            for letter in ['a', 'b', 'c', 'd']:
                if letter in ans_str:
                    k.append(ord(letter) - ord('a'))
            if not k:
                k = [0]
                
            expl = re.sub(r'Ans\.\s*\(.*?\)', '', post_ans).strip()
            expl = clean_text(expl)
            feedback = expl[:200] + ("..." if len(expl) > 200 else "")
            
            opt_matches = list(re.finditer(r'\(([a-d])\)', pre_ans))
            options = []
            stem = pre_ans
            if len(opt_matches) == 4:
                stem = pre_ans[:opt_matches[0].start()].strip()
                options = [
                    pre_ans[opt_matches[0].end():opt_matches[1].start()].strip(),
                    pre_ans[opt_matches[1].end():opt_matches[2].start()].strip(),
                    pre_ans[opt_matches[2].end():opt_matches[3].start()].strip(),
                    pre_ans[opt_matches[3].end():].strip()
                ]
                for oi in range(4):
                    options[oi] = re.sub(r'U\.?P\.?.*', '', options[oi]).strip()
                    options[oi] = clean_text(options[oi])
            else:
                stem = clean_text(stem)
                options = ["Option A", "Option B", "Option C", "Option D"]
                
            stem = clean_text(stem)
            
            labels = []
            years = []
            for l in uppsc_lines:
                lbl, yr = format_uppsc_exam(l)
                labels.append(lbl)
                years.append(yr)
                
            primary_label = "; ".join(labels)
            primary_year = max(years)
            
            qid = f"q{q_global_id:04d}"
            q_global_id += 1
            
            q_item = {
                "ch": f"c{ch_num}",
                "y": primary_year,
                "e": primary_label,
                "s": stem,
                "o": options,
                "k": k,
                "f": feedback,
                "n": len(labels),
                "h": f"c{ch_num}-t1",
                "pdf_page": start_p
            }
            all_qs[qid] = q_item
            ch_qs.append(q_item)

        chapter_stats.append({
            "num": ch_num,
            "title": ch_title,
            "pages": f"{start_p}–{end_p}",
            "uppsc_count": len(ch_qs),
            "intro": intro
        })

    with open("dashboard-src/subjects/history/parsed_uppsc_questions.json", "w", encoding="utf-8") as f:
        json.dump(all_qs, f, indent=2, ensure_ascii=False)
        
    with open("dashboard-src/subjects/history/parsed_chapter_stats.json", "w", encoding="utf-8") as f:
        json.dump(chapter_stats, f, indent=2, ensure_ascii=False)

    print(f"Total UPPSC questions parsed: {len(all_qs)} across {len(ranges)} chapters.")

if __name__ == "__main__":
    parse_all_chapters()
