import json
import re
import os
from collections import Counter, defaultdict

def load_data():
    base_dir = os.path.join("dashboard-src", "subjects", "science")
    with open(os.path.join(base_dir, "raw_pages.json"), encoding="utf-8") as f:
        pages = json.load(f)
    with open(os.path.join(base_dir, "chapter_boundaries.json"), encoding="utf-8") as f:
        ranges = json.load(f)
    return pages, ranges

def clean_noise(text):
    text = re.sub(r'General Science\s+General Studies\s+G[–-]\d+', '', text)
    text = re.sub(r'G[–-]\d+\s+General Studies\s+General Science', '', text)
    text = re.sub(r'search on TG-@freepdfhall', '', text)
    text = re.sub(r'click here -@freepdfhall', '', text)
    text = re.sub(r'click here -@PdfTaskari', '', text)
    # Normalize broken exam tags
    text = re.sub(r'U\.?\s*P\.?\s*\n\s*\.?', 'U.P.', text)
    text = re.sub(r'M\.?\s*P\.?\s*\n\s*\.?', 'M.P.', text)
    text = re.sub(r'B\.?\s*P\.?\s*\n\s*\.?', 'B.P.', text)
    return text

def is_uppsc(line):
    if re.search(r'\b(Uttarakhand|U\.?K\.?|M\.?P|B\.?P|R\.?A|Jharkhand|Chhattisgarh|I\.?A\.?S)\b', line, re.I):
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
        
        # Explanation range
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
            
        # Question body before Ans.
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
        
        for idx, l in enumerate(lines):
            l_str = l.strip()
            if is_uppsc(l_str):
                uppsc_lines.append(l_str)
                exam_line_indices.append(idx)
            elif re.search(r'\b(P\.?C\.?S|R\.?O|A\.?R\.?O|Lower|UDA|LDA|GIC|BEO|RI|B\.P\.S\.C|M\.P\.P\.C\.S|I\.A\.S|R\.A\.S|Chhattisgarh|Jharkhand|Uttarakhand)\b', l_str, re.I):
                exam_line_indices.append(idx)
                
        # Only keep UPPSC questions
        if not uppsc_lines:
            if expl_text and not re.search(r'See the explanation of above question', expl_text, re.I):
                last_seen_expl = expl_text
            continue
            
        # Parse exam label and year
        primary_exam = uppsc_lines[0]
        exam_lbl, exam_yr = format_uppsc_exam(primary_exam)
        total_uppsc_papers = len(uppsc_lines)
        
        # Clean lines before exam lines
        min_exam_idx = min(exam_line_indices) if exam_line_indices else len(lines)
        content_lines = lines[:min_exam_idx]
        full_content = "\n".join(content_lines).strip()
        
        # Extract question number and stem
        num_m = re.match(r'^(\d{1,3})\.\s*(.*)', full_content, re.S)
        if num_m:
            raw_stem_and_opts = num_m.group(2).strip()
        else:
            raw_stem_and_opts = full_content
            
        # Extract options (a), (b), (c), (d)
        opt_matches = list(re.finditer(r'(?:^|\s)\(([a-e])\)\s*', raw_stem_and_opts))
        options = []
        stem = ""
        
        if len(opt_matches) >= 2:
            stem = raw_stem_and_opts[:opt_matches[0].start()].strip()
            for opt_i in range(len(opt_matches)):
                o_start = opt_matches[opt_i].end()
                o_end = opt_matches[opt_i+1].start() if opt_i < len(opt_matches) - 1 else len(raw_stem_and_opts)
                opt_str = raw_stem_and_opts[o_start:o_end].strip()
                options.append(opt_str)
        else:
            stem = raw_stem_and_opts
            options = ["True", "False", "Partially correct", "None of the above"]
            
        # Normalize key
        key_indices = []
        for char in ['a', 'b', 'c', 'd', 'e']:
            if char in ans_val:
                idx = ord(char) - ord('a')
                if idx < len(options):
                    key_indices.append(idx)
        if not key_indices:
            key_indices = [0]
            
        # Clean explanation
        clean_expl = re.sub(r'\s+', ' ', expl_text).strip()
        if re.search(r'See the explanation of above question', clean_expl, re.I) and last_seen_expl:
            clean_expl = re.sub(r'\s+', ' ', last_seen_expl).strip()
        elif clean_expl and not re.search(r'See the explanation of above question', clean_expl, re.I):
            last_seen_expl = clean_expl
            
        if not clean_expl:
            clean_expl = f"According to UPPSC official answer key, option ({chr(ord('a') + key_indices[0])}) is the correct answer."
            
        stem = re.sub(r'\s+', ' ', stem).strip()
        options = [re.sub(r'\s+', ' ', o).strip() for o in options]
        
        questions.append({
            "ch": f"c{ch_num}",
            "y": exam_yr,
            "e": exam_lbl,
            "s": stem,
            "o": options,
            "k": key_indices,
            "f": clean_expl[:500],
            "n": total_uppsc_papers,
            "h": f"c{ch_num}-t1"
        })
        
    return questions, last_seen_expl

def main():
    pages, ranges = load_data()
    all_qs = []
    ch_q_counts = {}
    last_expl = None
    
    for r in ranges:
        num = r["num"]
        sp = r["start_page"]
        ep = r["end_page"]
        
        ch_text = ""
        for p in range(sp, ep + 1):
            ch_text += "\n" + pages[p - 1]["text"]
            
        qs, last_expl = parse_questions_from_chapter(ch_text, num, last_expl)
        ch_q_counts[num] = len(qs)
        all_qs.extend(qs)
        
    print(f"Total parsed UPPSC questions: {len(all_qs)}")
    for num, cnt in ch_q_counts.items():
        if cnt == 0:
            print(f"WARNING: Ch {num} has 0 questions!")
            
    # Assign IDs
    pqd = {}
    for i, q in enumerate(all_qs, 1):
        qid = f"q{i:04d}"
        pqd[qid] = q
        
    out_dir = os.path.join("dashboard-src", "subjects", "science")
    with open(os.path.join(out_dir, "parsed_uppsc_questions.json"), "w", encoding="utf-8") as f:
        json.dump(pqd, f, indent=2, ensure_ascii=False)
        
    print(f"Saved {len(pqd)} UPPSC questions to parsed_uppsc_questions.json")
    
    with open(os.path.join(out_dir, "parsed_chapter_stats.json"), "w", encoding="utf-8") as f:
        json.dump(ch_q_counts, f, indent=2)

if __name__ == "__main__":
    main()
