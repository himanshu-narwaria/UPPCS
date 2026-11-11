import json
import re
import os
from collections import Counter, defaultdict

def load_data():
    with open("dashboard-src/subjects/geography/raw_pages.json", encoding="utf-8") as f:
        pages = json.load(f)
    with open("dashboard-src/subjects/geography/accurate_chapter_ranges.json", encoding="utf-8") as f:
        ranges = json.load(f)
    return pages, ranges

def clean_noise(text):
    text = re.sub(r'CA–\d+\s+General Studies\s+Indian Geography', '', text)
    text = re.sub(r'CB–\d+\s+General Studies\s+World Geography', '', text)
    text = re.sub(r'search on TG-@freepdfhall', '', text)
    text = re.sub(r'click here -@PdfTaskari', '', text)
    text = re.sub(r'click here -@freepdfhall', '', text)
    # Normalize broken exam tags
    text = re.sub(r'U\.?\s*P\.?\s*\n\s*\.?', 'U.P.', text)
    text = re.sub(r'M\.?\s*P\.?\s*\n\s*\.?', 'M.P.', text)
    text = re.sub(r'B\.?\s*P\.?\s*\n\s*\.?', 'B.P.', text)
    return text

def is_uppsc(line):
    if re.search(r'\b(Uttarakhand|U\.?K\.?)\b', line, re.I):
        return False
    # Pattern 1: UP followed by PCS / PSC / etc.
    if re.search(r'\bU\.?\s*P\.?\s*(P\.?C\.?S|P\.?S\.?C|Lower|R\.?O|A\.?R\.?O|U\.?D\.?A|L\.?D\.?A|G\.?I\.?C|G\.?D\.?C|B\.?E\.?O|R\.?I)\b', line, re.I):
        return True
    # Pattern 2: UPPCS / UPPSC / etc.
    if re.search(r'\b(UPPCS|UPPSC|U\.?P\.?P\.?C\.?S|U\.?P\.?P\.?S\.?C)\b', line, re.I):
        return True
    return False

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

def parse_questions_from_chapter(text, ch_num, last_seen_expl=None):
    text = clean_noise(text)
    ans_matches = list(re.finditer(r'\nAns\.\s*\((.*?)\)', text))
    if not ans_matches:
        return [], last_seen_expl
        
    questions = []
    
    for i in range(len(ans_matches)):
        ans_m = ans_matches[i]
        ans_val = ans_m.group(1).lower().strip()
        ans_start = ans_m.start()
        ans_end = ans_m.end()
        
        # Determine explanation range
        if i < len(ans_matches) - 1:
            next_ans_start = ans_matches[i+1].start()
            between_text = text[ans_end:next_ans_start]
            q_starts = list(re.finditer(r'\n(\d{1,3})\.\s+', between_text))
            if q_starts:
                expl_text = between_text[:q_starts[0].start()].strip()
            else:
                expl_text = between_text.strip()
        else:
            expl_text = text[ans_end:].strip()
            
        # Determine question body before ans_start
        prev_bound = ans_matches[i-1].end() if i > 0 else 0
        pre_ans_text = text[prev_bound:ans_start]
        q_starts = list(re.finditer(r'\n(\d{1,3})\.\s+', pre_ans_text))
        if q_starts:
            q_body = pre_ans_text[q_starts[0].start():].strip()
        else:
            q_body = pre_ans_text.strip()
            
        lines = q_body.split('\n')
        uppsc_lines = []
        exam_line_indices = []
        for l_idx, l in enumerate(lines):
            l_str = l.strip()
            if is_uppsc(l_str):
                uppsc_lines.append(l_str)
                exam_line_indices.append(l_idx)
                
        # Clean expl text
        expl = re.sub(r'\s+', ' ', expl_text).strip()
        if re.search(r'See the explanation of the above question', expl, re.I):
            if last_seen_expl:
                expl = last_seen_expl
        elif len(expl) > 20:
            last_seen_expl = expl
            
        if not uppsc_lines:
            continue
            
        first_exam_idx = exam_line_indices[0] if exam_line_indices else len(lines)
        content_lines = lines[:first_exam_idx]
        content_text = "\n".join(content_lines).strip()
        content_text = re.sub(r'^\d+\.\s*', '', content_text)
        
        opt_matches = list(re.finditer(r'\(([a-e])\)', content_text))
        if len(opt_matches) >= 4:
            stem = content_text[:opt_matches[0].start()].strip()
            options = [
                content_text[opt_matches[0].end():opt_matches[1].start()].strip(),
                content_text[opt_matches[1].end():opt_matches[2].start()].strip(),
                content_text[opt_matches[2].end():opt_matches[3].start()].strip(),
                content_text[opt_matches[3].end():(opt_matches[4].start() if len(opt_matches) > 4 else len(content_text))].strip()
            ]
        else:
            stem = content_text
            options = ["Option A", "Option B", "Option C", "Option D"]
            
        stem = re.sub(r'\s+', ' ', stem).strip()
        options = [re.sub(r'\s+', ' ', opt).strip() for opt in options]
        
        k = []
        for letter in ['a', 'b', 'c', 'd']:
            if letter in ans_val:
                k.append(ord(letter) - ord('a'))
        if not k:
            k = [0]
            
        labels = []
        years = []
        for l in uppsc_lines:
            lbl, yr = format_uppsc_exam(l)
            labels.append(lbl)
            years.append(yr)
            
        feedback = expl[:220] + ("..." if len(expl) > 220 else "")
        if not feedback:
            feedback = f"Official UPPSC answer: Option {chr(ord('A') + k[0])}."
            
        questions.append({
            "ch": f"c{ch_num}",
            "y": max(years),
            "e": "; ".join(labels),
            "s": stem if stem else f"Question regarding {ranges[ch_num-1]['title']}",
            "o": options,
            "k": k,
            "f": feedback,
            "n": len(labels),
            "h": f"c{ch_num}-t1"
        })
        
    return questions, last_seen_expl

def main():
    pages, ranges = load_data()
    all_qs = {}
    chapter_stats = []
    q_global_id = 1
    last_expl = None
    
    print(f"Parsing UPPSC questions across {len(ranges)} chapters...")
    for entry in ranges:
        ch_num = entry["num"]
        ch_title = entry["title"]
        start_p = entry["pdf_start"]
        end_p = entry["calc_end_page"]
        
        ch_text = "\n".join(pages[p-1]["text"] for p in range(start_p, end_p + 1))
        qs, last_expl = parse_questions_from_chapter(ch_text, ch_num, last_expl)
        
        # Assign unique IDs
        for q in qs:
            qid = f"q{q_global_id:04d}"
            q_global_id += 1
            all_qs[qid] = q
            
        # Extract introductory notes
        intro_splits = re.split(r'\n\s*1\.\s+', clean_noise(ch_text))
        intro = re.sub(r'\s+', ' ', intro_splits[0]).strip()[:300] if intro_splits else ""
        
        chapter_stats.append({
            "num": ch_num,
            "title": ch_title,
            "section": entry["section"],
            "pages": f"{start_p}–{end_p}",
            "uppsc_count": len(qs),
            "intro": intro
        })
        
    out_dir = os.path.join("dashboard-src", "subjects", "geography")
    with open(os.path.join(out_dir, "parsed_uppsc_questions.json"), "w", encoding="utf-8") as f:
        json.dump(all_qs, f, indent=2, ensure_ascii=False)
        
    with open(os.path.join(out_dir, "parsed_chapter_stats.json"), "w", encoding="utf-8") as f:
        json.dump(chapter_stats, f, indent=2, ensure_ascii=False)
        
    total_qs = len(all_qs)
    year_counts = Counter(q["y"] for q in all_qs.values())
    print(f"\nSuccessfully parsed {total_qs} UPPSC questions across {len(chapter_stats)} chapters!")
    print(f"Year range: {min(year_counts.keys())} to {max(year_counts.keys())}")
    
    # Print top 5 chapters by question count
    top5 = sorted(chapter_stats, key=lambda x: -x["uppsc_count"])[:5]
    print("\nTop 5 chapters by UPPSC question count:")
    for c in top5:
        print(f"  Ch {c['num']:2d} ({c['section']}): {c['title']} -> {c['uppsc_count']} questions")
        
    # Check if any chapter has 0 questions
    zero_q = [c for c in chapter_stats if c["uppsc_count"] == 0]
    print(f"\nChapters with 0 UPPSC questions: {len(zero_q)}")
    if zero_q:
        for c in zero_q:
            print(f"  Ch {c['num']:2d}: {c['title']} (PDF pp. {c['pages']})")

if __name__ == "__main__":
    main()
