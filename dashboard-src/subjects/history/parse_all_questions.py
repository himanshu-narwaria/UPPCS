import json, re

with open("dashboard-src/subjects/history/raw_pages.json", encoding="utf-8") as f:
    pages = json.load(f)

with open("dashboard-src/subjects/history/chapter_ledger.json", encoding="utf-8") as f:
    ledger = json.load(f)

# Sort ledger by found_start
ledger.sort(key=lambda x: x["found_start"])

# Assign each page to a chapter
# Pages before ledger[0]["found_start"] are front matter (p. 1-8)
page_to_ch = {}
for i, entry in enumerate(ledger):
    ch_num = entry["num"]
    start_p = entry["found_start"]
    end_p = ledger[i + 1]["found_start"] - 1 if i + 1 < len(ledger) else len(pages)
    for p in range(start_p, end_p + 1):
        page_to_ch[p] = ch_num

print(f"Total pages mapped: {len(page_to_ch)} of {len(pages)}")

# Let's inspect how questions are structured across all pages
# Each page may have text. In Ghatna Chakra, header is "B-XX ...", then question numbers "1. ", "2. ", etc.
# Some pages start with explanation of previous question.

def is_uppsc(line):
    if re.search(r'\b(Uttarakhand|U\.?K\.?)\b', line, re.I):
        return False
    return bool(re.search(r'\b(U\.?P\.?P?\.?C\.?S|U\.?P\.?\s*P\.?S\.?C|U\.?P\.?\s*Lower|U\.?P\.?\s*R\.?O|U\.?P\.?\s*A\.?R\.?O|U\.?P\.?\s*U\.?D\.?A|U\.?P\.?\s*L\.?D\.?A|U\.?P\.?\s*G\.?I\.?C|U\.?P\.?\s*G\.?D\.?C|U\.?P\.?\s*B\.?E\.?O|U\.?P\.?\s*R\.?I)\b', line, re.I))

# Let's count questions per chapter
all_qs = []
uppsc_qs = []

# Let's concatenate text by chapter
for entry in ledger:
    ch_num = entry["num"]
    start_p = entry["found_start"]
    next_idx = ledger.index(entry) + 1
    end_p = ledger[next_idx]["found_start"] - 1 if next_idx < len(ledger) else len(pages)
    
    ch_text = "\n".join(pages[p-1]["text"] for p in range(start_p, end_p + 1))
    
    # Split into questions by pattern `\n(\d{1,3})\.\s+`
    # Note: Question numbers restart at 1 in each chapter!
    q_splits = re.split(r'\n\s*(\d{1,3})\.\s+', '\n' + ch_text)
    # q_splits[0] is the introductory notes before Q1!
    intro_notes = q_splits[0].strip()
    
    q_list = []
    for j in range(1, len(q_splits), 2):
        q_no = int(q_splits[j])
        q_raw = q_splits[j+1]
        
        # Check if this question has UPPSC exam tag
        has_uppsc = False
        exam_lines = []
        for l in q_raw.split('\n')[:15]: # exam tags are usually before or right at Ans.
            l_str = l.strip()
            if is_uppsc(l_str):
                has_uppsc = True
                exam_lines.append(l_str)
            elif re.search(r'Ans\.', l_str):
                break
                
        all_qs.append((ch_num, q_no))
        if has_uppsc:
            uppsc_qs.append((ch_num, q_no, exam_lines))

print(f"Total MCQs detected in book: {len(all_qs)}")
print(f"Total UPPSC MCQs detected: {len(uppsc_qs)}")
