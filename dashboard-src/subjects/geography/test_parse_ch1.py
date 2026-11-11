import json
import re

with open("dashboard-src/subjects/geography/raw_pages.json", encoding="utf-8") as f:
    pages = json.load(f)

with open("dashboard-src/subjects/geography/accurate_chapter_ranges.json", encoding="utf-8") as f:
    chapters = json.load(f)

ch1 = chapters[0]
print(f"Testing Chapter 1: {ch1['title']}, PDF pages {ch1['pdf_start']} to {ch1['calc_end_page']}")

ch1_text = "\n".join(pages[p-1]["text"] for p in range(ch1['pdf_start'], ch1['calc_end_page'] + 1))

# Normalize line splits like 'U.P\n.P.C.S.'
ch1_text = re.sub(r'U\.?\s*P\.?\s*\n\s*\.?', 'U.P.', ch1_text)
ch1_text = re.sub(r'M\.?\s*P\.?\s*\n\s*\.?', 'M.P.', ch1_text)
ch1_text = re.sub(r'B\.?\s*P\.?\s*\n\s*\.?', 'B.P.', ch1_text)

# Strip headers
ch1_text = re.sub(r'CA–\d+\s+General Studies\s+Indian Geography', '', ch1_text)
ch1_text = re.sub(r'search on TG-@freepdfhall', '', ch1_text)
ch1_text = re.sub(r'click here -@PdfTaskari', '', ch1_text)

# Split by question numbers
q_splits = re.split(r'\n\s*(\d{1,3})\.\s+', '\n' + ch1_text)
print(f"Total question splits found: {len(q_splits)//2}")

def is_uppsc(line):
    if re.search(r'\b(Uttarakhand|U\.?K\.?)\b', line, re.I):
        return False
    return bool(re.search(r'\b(U\.?P\.?P?\.?C\.?S|U\.?P\.?\s*P\.?S\.?C|U\.?P\.?\s*Lower|U\.?P\.?\s*R\.?O|U\.?P\.?\s*A\.?R\.?O|U\.?P\.?\s*U\.?D\.?A|U\.?P\.?\s*L\.?D\.?A|U\.?P\.?\s*G\.?I\.?C|U\.?P\.?\s*G\.?D\.?C|U\.?P\.?\s*B\.?E\.?O|U\.?P\.?\s*R\.?I)\b', line, re.I))

uppsc_qs = []
for j in range(1, len(q_splits), 2):
    q_no = int(q_splits[j])
    body = q_splits[j+1]
    
    lines = body.split('\n')
    ans_idx = None
    uppsc_lines = []
    for idx, l in enumerate(lines):
        if re.search(r'Ans\.', l):
            ans_idx = idx
            break
        if is_uppsc(l.strip()):
            uppsc_lines.append(l.strip())
            
    if uppsc_lines:
        ans_m = re.search(r'Ans\.\s*\((.*?)\)', body)
        ans_str = ans_m.group(1).lower() if ans_m else ""
        uppsc_qs.append({
            "q_no": q_no,
            "exams": uppsc_lines,
            "ans": ans_str,
            "sample_stem": lines[0][:80]
        })

print(f"UPPSC questions in Ch 1: {len(uppsc_qs)}")
for q in uppsc_qs[:10]:
    print(f"  Q{q['q_no']}: Ans={q['ans']} | Exams={q['exams']} | Stem={q['sample_stem']}")
