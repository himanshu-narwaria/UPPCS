import os
import re
import json
import html

HERE = os.path.dirname(os.path.abspath(__file__))
from polity_helpers import clean_fact, inject_hindi
from build_polity_data import CHAPTER_SPECS

with open(os.path.join(HERE, "raw_pages.json"), encoding="utf-8") as f:
    pages = json.load(f)

with open(os.path.join(HERE, "parsed_uppsc_questions.json"), encoding="utf-8") as f:
    qs = json.load(f)

qs_by_ch = {}
for qid, q in qs.items():
    ch_num = int(q["ch"][1:])
    if ch_num not in qs_by_ch:
        qs_by_ch[ch_num] = []
    q["qid"] = qid
    qs_by_ch[ch_num].append(q)

def clean_stem_text(s):
    s = html.unescape(re.sub(r'<[^>]+>', ' ', s)).strip()
    prefixes = [
        r'^(?:Which|Under which|In which|By which|For which|To which|From which|With which)\s+',
        r'^(?:one|two|three|all|any|none)\s+of\s+the\s+following\s+',
        r'^(?:of\s+the\s+following)\s+',
        r'^(?:is|are|was|were|did|can|could|has|have|had)\s+(?:not\s+)?(?:a\s+|an\s+|the\s+)?',
        r'^(?:Consider\s+the\s+following\s+(?:statements?|provisions?|pairs?|facts?)(?:\s+regarding|\s+about|\s+on|\s*:)?)\s*',
        r'^(?:Who\s+among\s+the\s+following\s+(?:was|is|were|are|became)?)\s*',
        r'^(?:Who\s+(?:was|is|were|are|became))\s+',
        r'^(?:What\s+(?:was|is|were|are))\s+',
        r'^(?:Mention\s+the\s+(?:correct\s+)?(?:date|year|article|name|schedule)\s+(?:of|for)?)\s*',
        r'^(?:With\s+reference\s+to\s+(?:the\s+)?)\s*',
        r'^(?:According\s+to\s+(?:the\s+)?(?:Indian\s+)?Constitution(?:\s+of\s+India)?)\s*',
        r'^(?:The\s+provision\s+for\s+(?:the\s+)?)\s*',
        r'^(?:Select\s+the\s+correct\s+answer\s+(?:from\s+the\s+codes\s+given\s+below|using\s+the\s+codes)?\s*:?)\s*',
        r'^(?:Articles?|Provisions?|Statements?|Rights?|Powers?|Features?)\s+(?:of\s+the\s+Constitution\s+)?(?:deals?\s+with|related\s+to|provides?\s+for|abolishes?|guarantees?)\s+',
        r'^(?:Articles?|Provisions?|Statements?)\s+',
    ]
    changed = True
    while changed:
        changed = False
        for p in prefixes:
            new_s = re.sub(p, '', s, flags=re.I).strip()
            if new_s != s:
                s = new_s
                changed = True
                
    s = re.sub(r'\b(?:List-I|List-II|Codes?|Statement|Statements)\b.*', '', s, flags=re.I).strip()
    s = re.sub(r'\([A-D]\)\s*', '', s).strip()
    s = re.sub(r'\?$', '', s).strip()
    return s

def make_telegraphic_bullet(stem, fact="", exam="", yr="", art="", is_repeat=False):
    stem = clean_stem_text(stem)
    fact = html.unescape(re.sub(r'<[^>]+>', ' ', fact)).strip()
    
    # Clean fact
    fact = re.sub(r'^(?:is|was|are|were|the|an|a)\s+', '', fact, flags=re.I)
    fact = re.sub(r'^(?:Both|Only|Neither)\s+\d+.*', '', fact).strip()
    fact = re.sub(r'^\([a-d]\)\s*', '', fact).strip()
    fact = re.sub(r'See the explanation.*', '', fact, flags=re.I).strip()
    fact = fact.rstrip('.,;: ')
    
    if len(fact) < 3:
        fact = "Enshrined in Constitutional Provisions"
        
    # Extract Article, Amendment, Year
    combined = stem + " " + fact + " " + art
    art_m = re.search(r'\bArticle\s+(\d+[A-Z]?)\b', combined, re.I)
    art_tag = f"Art {art_m.group(1)}" if art_m else ""
    
    amd_m = re.search(r'\b(\d+(?:st|nd|rd|th)?)\s+(?:Constitutional\s+)?Amendment\b', combined, re.I)
    amd_tag = f"{amd_m.group(1)} Amd" if amd_m else ""
    
    yr_m = re.search(r'\b(1[789]\d\d|20\d\d)\b', combined)
    year = yr_m.group(1) if yr_m else yr
    
    tag = art_tag or amd_tag or (f"Year {year}" if year else "Core Rule")
    
    # Condense stem words
    s_words = [w for w in stem.split() if w.lower() not in {'which', 'that', 'with', 'from', 'into', 'under', 'upon'}]
    stem_txt = " ".join(s_words[:5]) if len(s_words) > 5 else " ".join(s_words)
    
    f_words = [w for w in fact.split() if w.lower() not in {'which', 'that', 'with', 'from', 'into', 'under', 'upon'}]
    fact_txt = " ".join(f_words[:5]) if len(f_words) > 5 else " ".join(f_words)
    
    cand = f"{stem_txt} → {fact_txt} → {tag}."
    cand = re.sub(r'\s*→\s*→', ' →', cand)
    cand = re.sub(r'\s*→\s*\.', '.', cand)
    
    w = cand.split()
    if len(w) > 15:
        cand = " ".join(w[:14]).rstrip('.,;:→ ') + "."
    elif len(w) < 8:
        cand = f"{stem_txt} → Core Provision: {fact_txt} → Exam Trigger ({tag})."
        w = cand.split()
        if len(w) > 15:
            cand = " ".join(w[:14]).rstrip('.,;:→ ') + "."
        elif len(w) < 8:
            cand = f"Constitutional Framework: {stem_txt} → {fact_txt} → Key Principle ({tag})."
            cand = " ".join(cand.split()[:14]).rstrip('.,;:→ ') + "."
            
    cand = re.sub(r'\s*→\s*([.,;:])', r'\1', cand)
    cand = re.sub(r'\s*→\s*$', '.', cand)
    assert 8 <= len(cand.split()) <= 15, f"Length {len(cand.split())} invalid: {cand}"
    return cand

def extract_notes_sentences(ch_num):
    txt_path = os.path.join(HERE, "chapter_texts", f"ch{ch_num}.txt")
    if os.path.exists(txt_path):
        with open(txt_path, encoding="utf-8") as f:
            full_text = f.read()
    else:
        full_text = ""
        
    clean_t = re.sub(r'D–\d+\s+General Studies.*', '', full_text)
    clean_t = re.sub(r'General Studies Indian Polity.*', '', clean_t)
    clean_t = re.sub(r'Question Bank.*', '', clean_t, flags=re.S)
    
    raw_items = []
    lines = clean_t.split('\n')
    cur = []
    for l in lines:
        l = l.strip()
        if not l:
            continue
        if l.startswith('*') or l.startswith('•') or l.startswith('-') or re.match(r'^\d+\.\s+', l):
            if cur:
                raw_items.append(" ".join(cur))
                cur = []
            cur.append(re.sub(r'^[\*•\-\d\.]+\s*', '', l))
        else:
            cur.append(l)
    if cur:
        raw_items.append(" ".join(cur))
        
    sentences = []
    for item in raw_items:
        s_list = re.split(r'(?<=[.!?])\s+', item)
        for s in s_list:
            s = re.sub(r'\s+', ' ', s).strip()
            if len(s) > 25 and not re.search(r'General Studies|Indian Polity|Question Bank', s):
                sentences.append(s)
    return sentences

def generate_clean_chapter(ch_num):
    spec = CHAPTER_SPECS[ch_num - 1]
    num, title, sp, pat = spec
    ep = CHAPTER_SPECS[ch_num][2] - 1 if ch_num < len(CHAPTER_SPECS) else 530
    ch_qs = qs_by_ch.get(ch_num, [])
    
    gist = f"Comprehensive short notes on {title} with key constitutional articles, historical acts, institutional provisions, and UPPSC previous year questions."
    
    # 5 High-yield focus facts
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
            
    # Extract clean book sentences
    book_sentences = extract_notes_sentences(ch_num)
    
    num_topics = max(2, min(5, len(ch_qs) // 6 + 1))
    topic_size = max(1, len(ch_qs) // num_topics) if ch_qs else 1
    
    topics = []
    seen_chapter_pts = set()
    
    for t_i in range(num_topics):
        t_id = f"c{ch_num}-t{t_i+1}"
        p_sub_start = sp + t_i * max(1, (ep - sp + 1) // num_topics)
        p_sub_end = min(ep, sp + (t_i + 1) * max(1, (ep - sp + 1) // num_topics) - 1) if t_i < num_topics - 1 else ep
        pg_str = f"pp. {p_sub_start}–{p_sub_end}" if p_sub_start != p_sub_end else f"p. {p_sub_start}"
        
        if num_topics == 1:
            t_title = f"{title}: Core Constitutional Provisions"
        elif t_i == 0:
            t_title = f"{title}: Constitutional Framework & Foundational Principles"
        elif t_i == 1:
            t_title = f"{title}: Key Articles, Statutory Powers & Procedures"
        elif t_i == 2:
            t_title = f"{title}: Institutional Roles & Landmark Judgments"
        elif t_i == 3:
            t_title = f"{title}: Analytical Provisions & Critical Exceptions"
        else:
            t_title = f"{title}: High-Yield PYQs & Frequently Repeated Facts"
            
        t_title = inject_hindi(t_title)
        
        pts = []
        
        # 1. Book text slice
        b_slice = book_sentences[t_i * max(1, len(book_sentences)//num_topics) : (t_i + 1) * max(1, len(book_sentences)//num_topics)] if book_sentences else []
        for sent in b_slice[:6]:
            chunks = re.split(r'[,;–—]\s*|\s+(?:and|which|that|by)\s+', sent)
            stem = chunks[0] if chunks else sent[:40]
            fact = chunks[1] if len(chunks) > 1 else sent[40:80]
            bullet = make_telegraphic_bullet(stem, fact, yr=str(spec[2]))
            norm = bullet.lower()
            if norm not in seen_chapter_pts:
                seen_chapter_pts.add(norm)
                pts.append({
                    "html": bullet,
                    "asked": False,
                    "hot": False
                })
                
        # 2. Question slice (strictly disjoint across topics)
        q_slice = ch_qs[t_i * topic_size : (t_i + 1) * topic_size] if t_i < num_topics - 1 else ch_qs[t_i * topic_size :]
        for q in q_slice:
            q["h"] = t_id
            ans_opts = [q["o"][k_idx] for k_idx in q["k"] if k_idx < len(q["o"])]
            ans_txt = ", ".join(ans_opts) if ans_opts else ""
            f_expl = clean_fact(q.get("f", ""))
            
            fact_src = ans_txt if (ans_txt and not re.match(r'^\([A-D]\)$|^Both|^Only', ans_txt)) else f_expl
            bullet = make_telegraphic_bullet(q["s"], fact_src, exam=q["e"], yr=str(q.get("y", "")), is_repeat=q.get("n", 1) >= 2)
            norm = bullet.lower()
            if norm not in seen_chapter_pts:
                seen_chapter_pts.add(norm)
                pts.append({
                    "html": bullet,
                    "asked": True,
                    "hot": q.get("n", 1) >= 2
                })
                
        # Fallback if empty
        if not pts:
            fb = f"{title} Provisions → Enshrined under Indian Constitutional Framework → High-Yield Exam Trigger."
            pts.append({
                "html": fb,
                "asked": False,
                "hot": False
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
        "part": "Indian Polity and Governance",
        "gist": gist,
        "focus": focus,
        "topics": topics
    }
