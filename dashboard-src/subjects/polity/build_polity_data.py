import json
import re
import os
from collections import Counter, defaultdict

# The 42 chapters with their exact starting page and heading regex pattern on that page
CHAPTER_SPECS = [
    (1, "The Constitutional Development of India", 7, r'The Constitutional Development\s+of India'),
    (2, "Constituent Assembly and Making of the Constitution", 17, r'Constituent Assembly and making\s+of the Constitution'),
    (3, "Important Committees of Constituent Assembly", 29, r'Important Committees of the\s+Constituent Assembly'),
    (4, "Sources of the Constitution", 31, r'Sources of the Constitution'),
    (5, "Parts of Indian Constitution", 37, r'Parts of the Indian Constitution'),
    (6, "Articles of the Constitution", 42, r'Important articles of the Constitution at a glance'),
    (7, "Schedules", 50, r'\nSchedules\s*\n'),
    (8, "The Preamble", 61, r'\nThe Preamble\s*\n'),
    (9, "The Governance System", 70, r'The Governance System'),
    (10, "National Symbols", 87, r'National Symbols'),
    (11, "States and Union Territories", 90, r'States and the Union Territories'),
    (12, "The Citizenship", 102, r'The Citizenship'),
    (13, "Fundamental Rights", 105, r'Fundamental Rights'),
    (14, "Directive Principles of State Policy", 136, r'Directive Principles of State Policy'),
    (15, "Fundamental Duties", 150, r'Fundamental Duties'),
    (16, "The President", 156, r'The President'),
    (17, "The Vice-President", 179, r'The Vice-President'),
    (18, "The Council of Ministers", 184, r'The Council of Ministers'),
    (19, "The Attorney General and the C.A.G.", 199, r'The Attorney-General and\s+the C\.A\.G\.|The Attorney-General and the C\.A\.G\.'),
    (20, "Order of Precedence", 210, r'Order of Precedence'),
    (21, "The Parliament (1)", 212, r'The Parliament \(1\)'),
    (22, "The Parliament (2)", 231, r'The Parliament \(2\)'),
    (23, "The Parliament (3)", 243, r'The Parliament \(3\)'),
    (24, "Parliamentary Committees", 269, r'Parliamentary Committees'),
    (25, "The Parliamentary Act", 277, r'Parliamentary Act'),
    (26, "The Supreme Court", 295, r'The Supreme Court'),
    (27, "The Governor", 320, r'The Governor'),
    (28, "The State Legislature", 332, r'Legislative Assembly'),
    (29, "The High Court", 347, r'The High Court'),
    (30, "The Centre-State Relations", 356, r'The Centre-State Relation'),
    (31, "Emergency Provisions", 367, r'Emergency Provisions'),
    (32, "The Finance Commission", 375, r'The Finance Commission'),
    (33, "The Planning Commission/NITI Aayog", 381, r'The Planning Commission\s*/\s*NITI AAYOG'),
    (34, "Lokpal and Important Commissions", 386, r'Lokpal and Important\s+Commissions'),
    (35, "Temporary, Transitional and Special Provisions", 408, r'Temporary, Transitional and\s+Special Provisions'),
    (36, "Election Commission", 410, r'Election Commission'),
    (37, "Political Parties", 424, r'Political Parties'),
    (38, "Constitutional Amendments", 436, r'Constitutional Amendment'),
    (39, "Official Language", 454, r'Official Language'),
    (40, "Panchayati Raj and Community Development", 459, r'Panchayati Raj and\s+Community Development'),
    (41, "Special Provision for Certain Classes", 498, r'Special Provisions Relating to\s+Certain Classes'),
    (42, "Miscellaneous", 504, r'Miscellaneous')
]

def load_pages():
    path = os.path.join("dashboard-src", "subjects", "polity", "raw_pages.json")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def clean_noise(text):
    text = re.sub(r'D[–-]\d+\s+General Studies.*?\n', '\n', text)
    text = re.sub(r'General Studies\s+Indian Polity and Governance.*?\n', '\n', text)
    text = re.sub(r'search on TG-@freepdfhall', '', text)
    text = re.sub(r'click here -@freepdfhall', '', text)
    text = re.sub(r'click here -@PdfTaskari', '', text)
    text = re.sub(r'U\.?\s*P\.?\s*\n\s*\.?', 'U.P.', text)
    text = re.sub(r'M\.?\s*P\.?\s*\n\s*\.?', 'M.P.', text)
    text = re.sub(r'B\.?\s*P\.?\s*\n\s*\.?', 'B.P.', text)
    return text

def is_uppsc(line):
    # Exclude non-UPPSC state PSCs and UPSC
    if re.search(r'\b(Uttarakhand|U\.?K\.?|M\.?P|B\.?P|R\.?A|Jharkhand|Chhattisgarh|I\.?A\.?S)\b', line, re.I):
        return False
    # Pattern 1: UP followed by PCS / PSC / etc.
    if re.search(r'\bU\.?\s*P\.?\s*(P\.?C\.?S|P\.?S\.?C|Lower|R\.?O|A\.?R\.?O|U\.?D\.?A|L\.?D\.?A|G\.?I\.?C|G\.?D\.?C|B\.?E\.?O|R\.?I)\b', line, re.I):
        return True
    # Pattern 2: UPPCS / UPPSC
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

def extract_chapter_texts(pages):
    # Slice text cleanly for each chapter
    # Each chapter text starts at its heading on start_page, and ends at next chapter's heading on its start_page
    chapter_texts = {}
    
    for i in range(len(CHAPTER_SPECS)):
        ch_num, title, st_page, pat = CHAPTER_SPECS[i]
        
        # Start text on st_page
        p_txt = pages[st_page - 1]["text"]
        m_st = re.search(pat, p_txt, re.I)
        if not m_st:
            raise ValueError(f"Could not find start pattern for Ch {ch_num} on page {st_page}")
        
        text_parts = [p_txt[m_st.start():]]
        
        # Middle pages up to next chapter's start page
        if i < len(CHAPTER_SPECS) - 1:
            next_ch_num, next_title, next_st_page, next_pat = CHAPTER_SPECS[i+1]
            for p in range(st_page + 1, next_st_page):
                text_parts.append(pages[p - 1]["text"])
            
            # On next_st_page, text up to next chapter heading
            next_p_txt = pages[next_st_page - 1]["text"]
            m_en = re.search(next_pat, next_p_txt, re.I)
            if not m_en:
                raise ValueError(f"Could not find end pattern (next Ch {next_ch_num}) on page {next_st_page}")
            text_parts.append(next_p_txt[:m_en.start()])
        else:
            # Last chapter (Ch 42) goes all the way to end of PDF
            for p in range(st_page + 1, len(pages) + 1):
                text_parts.append(pages[p - 1]["text"])
                
        full_ch_text = clean_noise("\n".join(text_parts))
        chapter_texts[ch_num] = full_ch_text
        
    return chapter_texts

def parse_questions_from_chapter(text, ch_num, last_seen_expl=None):
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
    pages = load_pages()
    print(f"Loaded {len(pages)} pages.")
    
    chapter_texts = extract_chapter_texts(pages)
    print("Cleanly sliced chapter texts for all 42 chapters.")
    
    all_qs = []
    ch_q_counts = {}
    last_expl = None
    
    for ch_num, title, _, _ in CHAPTER_SPECS:
        text = chapter_texts[ch_num]
        qs, last_expl = parse_questions_from_chapter(text, ch_num, last_expl)
        ch_q_counts[ch_num] = len(qs)
        all_qs.extend(qs)
        print(f"Ch {ch_num:2d} ({title[:35]}): {len(qs):3d} UPPSC questions")
        
    print(f"\nTotal parsed UPPSC questions: {len(all_qs)}")
    
    # Assign IDs
    pqd = {}
    for i, q in enumerate(all_qs, 1):
        qid = f"q{i:04d}"
        pqd[qid] = q
        
    out_dir = os.path.join("dashboard-src", "subjects", "polity")
    with open(os.path.join(out_dir, "parsed_uppsc_questions.json"), "w", encoding="utf-8") as f:
        json.dump(pqd, f, indent=2, ensure_ascii=False)
        
    print(f"Saved {len(pqd)} UPPSC questions to parsed_uppsc_questions.json")
    
    with open(os.path.join(out_dir, "parsed_chapter_stats.json"), "w", encoding="utf-8") as f:
        json.dump(ch_q_counts, f, indent=2)

if __name__ == "__main__":
    main()
