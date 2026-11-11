import json, re

with open("dashboard-src/subjects/history/raw_pages.json", encoding="utf-8") as f:
    pages = json.load(f)

with open("dashboard-src/subjects/history/chapter_ledger.json", encoding="utf-8") as f:
    ledger = json.load(f)

ledger.sort(key=lambda x: x["found_start"])

def is_uppsc(line):
    if re.search(r'\b(Uttarakhand|U\.?K\.?)\b', line, re.I):
        return False
    return bool(re.search(r'\b(U\.?P\.?P?\.?C\.?S|U\.?P\.?\s*P\.?S\.?C|U\.?P\.?\s*Lower|U\.?P\.?\s*R\.?O|U\.?P\.?\s*A\.?R\.?O|U\.?P\.?\s*U\.?D\.?A|U\.?P\.?\s*L\.?D\.?A|U\.?P\.?\s*G\.?I\.?C|U\.?P\.?\s*G\.?D\.?C|U\.?P\.?\s*B\.?E\.?O|U\.?P\.?\s*R\.?I)\b', line, re.I))

def format_uppsc_exam(line):
    # Normalize e.g. "U.P.P.C.S. (Pre) 2018" -> "PCS Pre ’18"
    # "U.P. Lower Sub. (Pre) 2004" -> "Lower Sub ’04"
    # "U.P.R.O./A.R.O. (Mains) 2014" -> "RO/ARO Mains ’14"
    # "U.P.P.S.C. (GIC) 2010" -> "GIC ’10"
    # "U.P. B.E.O. (Pre) 2019" -> "BEO ’19"
    # "UPPCS (RI) Pre Exam 2014" -> "RI ’14"
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
    else: # Default PCS
        mains = bool(re.search(r'Mains', line, re.I))
        lbl = f"PCS{' Mains' if mains else ' Pre'}{spl_str} {y_short}"
    return lbl, year

# Let's test on Chapter 1 (Stone Age)
ch1_start = ledger[0]["found_start"]
ch1_end = ledger[1]["found_start"] - 1
text = "\n".join(pages[p-1]["text"] for p in range(ch1_start, ch1_end + 1))

q_splits = re.split(r'\n\s*(\d{1,3})\.\s+', '\n' + text)
parsed_qs = []

for j in range(1, len(q_splits), 2):
    q_no = int(q_splits[j])
    body = q_splits[j+1]
    
    # Check if UPPSC
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
        
    # Stem & options are before ans_idx
    pre_ans = "\n".join(lines[:ans_idx]) if ans_idx is not None else body
    post_ans = "\n".join(lines[ans_idx:]) if ans_idx is not None else ""
    
    # Answer key
    ans_m = re.search(r'Ans\.\s*\((.*?)\)', post_ans)
    ans_str = ans_m.group(1).lower() if ans_m else ""
    k = []
    for letter in ['a', 'b', 'c', 'd']:
        if letter in ans_str:
            k.append(ord(letter) - ord('a'))
    if not k:
        k = [0] # default if not found or canceled
        
    # Feedback
    expl = re.sub(r'Ans\.\s*\(.*?\)', '', post_ans).strip()
    # clean header footers
    expl = re.sub(r'B–\d+ General Studies Indian History', '', expl)
    expl = re.sub(r'Indian History General Studies B–\d+', '', expl)
    expl = re.sub(r'click here -@freepdfhall', '', expl)
    expl = re.sub(r'search on TG-@freepdfhall', '', expl)
    expl = re.sub(r'\s+', ' ', expl).strip()
    feedback = expl[:160] + ("..." if len(expl) > 160 else "")
    
    # Options
    # Check for (a), (b), (c), (d)
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
        # clean options
        for oi in range(4):
            options[oi] = re.sub(r'U\.?P\.?.*', '', options[oi]).strip()
            options[oi] = re.sub(r'\s+', ' ', options[oi])
            
    # Exam labels and year
    labels = []
    years = []
    for l in uppsc_lines:
        lbl, yr = format_uppsc_exam(l)
        labels.append(lbl)
        years.append(yr)
        
    primary_label = "; ".join(labels)
    primary_year = max(years)
    
    stem = re.sub(r'\s+', ' ', stem).strip()
    
    parsed_qs.append({
        "q_no": q_no,
        "s": stem,
        "o": options,
        "k": k,
        "f": feedback,
        "e": primary_label,
        "y": primary_year,
        "n": len(labels)
    })

print(f"Chapter 1 UPPSC questions parsed: {len(parsed_qs)}")
for q in parsed_qs[:5]:
    print("\n", json.dumps(q, indent=2))
