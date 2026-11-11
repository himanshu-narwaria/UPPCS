import json
import re

with open("dashboard-src/subjects/geography/raw_pages.json", encoding="utf-8") as f:
    pages = json.load(f)

with open("dashboard-src/subjects/geography/accurate_chapter_ranges.json", encoding="utf-8") as f:
    chapters = json.load(f)

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

def parse_questions_from_text(raw_text):
    text = clean_noise(raw_text)
    
    # We find all "Ans. (...)" positions
    ans_matches = list(re.finditer(r'\nAns\.\s*\((.*?)\)', text))
    if not ans_matches:
        return []
        
    questions = []
    
    for i in range(len(ans_matches)):
        ans_m = ans_matches[i]
        ans_val = ans_m.group(1).lower().strip()
        ans_start = ans_m.start()
        ans_end = ans_m.end()
        
        # The explanation runs from ans_end until the start of the next question
        # Next question starts somewhere before the next Ans (or at end of text)
        if i < len(ans_matches) - 1:
            next_ans_start = ans_matches[i+1].start()
            between_text = text[ans_end:next_ans_start]
            
            # The next question begins where a line like "\n\d+\." occurs
            # Look for the last or most prominent "\n\d+\." before next_ans
            q_starts = list(re.finditer(r'\n(\d{1,3})\.\s+', between_text))
            if q_starts:
                # The first q_start is the start of the next question!
                expl_text = between_text[:q_starts[0].start()].strip()
                # But wait, what if there are multiple \n\d+\. in between?
                # Actually, the start of question i+1 is between_text[q_starts[0].start():]
                # And question i's pre-ans text was before ans_start!
            else:
                expl_text = between_text.strip()
        else:
            expl_text = text[ans_end:].strip()
            
        # Now find the start of question i (before ans_start)
        # Search backwards from ans_start for "\n\d+\."
        prev_bound = 0
        if i > 0:
            # cannot start before previous ans_end
            prev_bound = ans_matches[i-1].end()
            
        pre_ans_text = text[prev_bound:ans_start]
        q_starts = list(re.finditer(r'\n(\d{1,3})\.\s+', pre_ans_text))
        if q_starts:
            # The question start is q_starts[0] (or if there was intro, q_starts[0])
            q_num = int(q_starts[0].group(1))
            q_body = pre_ans_text[q_starts[0].start():].strip()
        else:
            q_num = 0
            q_body = pre_ans_text.strip()
            
        # Check exams in q_body
        lines = q_body.split('\n')
        uppsc_lines = []
        exam_line_indices = []
        for l_idx, l in enumerate(lines):
            l_str = l.strip()
            if is_uppsc(l_str):
                uppsc_lines.append(l_str)
                exam_line_indices.append(l_idx)
                
        if not uppsc_lines:
            continue # not a UPPSC question
            
        # Parse stem, options
        # Remove exam lines from stem/options
        first_exam_idx = exam_line_indices[0]
        content_lines = lines[:first_exam_idx]
        content_text = "\n".join(content_lines).strip()
        
        # Remove question number prefix
        content_text = re.sub(r'^\d+\.\s*', '', content_text)
        
        # Parse options (a), (b), (c), (d)
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
        expl = re.sub(r'\s+', ' ', expl_text).strip()
        
        # Format key k
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
            
        questions.append({
            "q_num": q_num,
            "stem": stem,
            "options": options,
            "k": k,
            "ans_raw": ans_val,
            "feedback": expl[:220] + ("..." if len(expl) > 220 else ""),
            "full_expl": expl,
            "labels": labels,
            "year": max(years),
            "primary_label": "; ".join(labels),
            "n": len(labels)
        })
        
    return questions

# Test on Ch 1
ch1 = chapters[0]
ch1_text = "\n".join(pages[p-1]["text"] for p in range(ch1['pdf_start'], ch1['calc_end_page'] + 1))
qs = parse_questions_from_text(ch1_text)
print(f"Ch 1 parsed UPPSC questions: {len(qs)}")
for q in qs[:5]:
    print(f"Q{q['q_num']}: {q['primary_label']} ({q['year']}) | Key={q['k']}")
    print(f"   Stem: {q['stem'][:90]}")
    print(f"   Opts: {q['options']}")
    print(f"   Fb:   {q['feedback'][:90]}")
