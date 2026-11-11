import json, re, os
from collections import Counter, defaultdict

def load_base():
    with open("dashboard-src/subjects/history/raw_pages.json", encoding="utf-8") as f:
        pages = json.load(f)
    with open("dashboard-src/subjects/history/accurate_ranges.json", encoding="utf-8") as f:
        ranges = json.load(f)
    with open("dashboard-src/subjects/history/parsed_uppsc_questions.json", encoding="utf-8") as f:
        qs = json.load(f)
    return pages, ranges, qs

def clean_text(t):
    t = re.sub(r'B–\d+ General Studies Indian History', '', t)
    t = re.sub(r'Indian History General Studies B–\d+', '', t)
    t = re.sub(r'Indian HistoryB–\d+', '', t)
    t = re.sub(r'click here -@freepdfhall', '', t)
    t = re.sub(r'search on TG-@freepdfhall', '', t)
    t = re.sub(r'\s+', ' ', t).strip()
    return t

# Hindi glossary mapping for key historical terms
HINDI_TERMS = {
    "Palaeolithic": "पुरापाषाण काल [Palaeolithic]",
    "Mesolithic": "मध्यपाषाण काल [Mesolithic]",
    "Neolithic": "नवपाषाण काल [Neolithic]",
    "Chalcolithic": "ताम्रपाषाण काल [Chalcolithic]",
    "Harappan": "हड़प्पा सभ्यता [Harappan]",
    "Indus Valley": "सिंधु घाटी सभ्यता [Indus Valley]",
    "Great Bath": "विशाल स्नानागार [Great Bath]",
    "Granary": "अन्नागार [Granary]",
    "Vedic": "वैदिक काल [Vedic period]",
    "Rigveda": "ऋग्वेद [Rigveda]",
    "Upanishad": "उपनिषद [Upanishad]",
    "Buddhism": "बौद्ध धर्म [Buddhism]",
    "Four Noble Truths": "चार आर्य सत्य [Four Noble Truths]",
    "Eightfold Path": "अष्टांगिक मार्ग [Eightfold Path]",
    "Jainism": "जैन धर्म [Jainism]",
    "Tirthankara": "तीर्थंकर [Tirthankara]",
    "Triratna": "त्रिरत्न [Three Jewels]",
    "Mahajanapadas": "महाजनपद [Mahajanapadas]",
    "Magadha": "मगध [Magadha]",
    "Maurya": "मौर्य साम्राज्य [Maurya Empire]",
    "Ashoka": "सम्राट अशोक [Ashoka]",
    "Dhamma": "धम्म [Dhamma]",
    "Rock Edicts": "शिलालेख [Rock Edicts]",
    "Gupta": "गुप्त साम्राज्य [Gupta Empire]",
    "Navaratna": "नवरत्न [Nine Jewels]",
    "Sangam": "संगम काल [Sangam Period]",
    "Delhi Sultanate": "दिल्ली सल्तनत [Delhi Sultanate]",
    "Slave Dynasty": "गुलाम वंश [Slave Dynasty]",
    "Khalji": "खिलजी वंश [Khalji Dynasty]",
    "Market Control": "बाजार नियंत्रण प्रणाली [Market Control]",
    "Tughluq": "तुगलक वंश [Tughluq Dynasty]",
    "Vijayanagara": "विजयनगर साम्राज्य [Vijayanagara Empire]",
    "Bhakti": "भक्ति आंदोलन [Bhakti Movement]",
    "Sufi": "सूफी आंदोलन [Sufi Movement]",
    "Mughal": "मुगल साम्राज्य [Mughal Empire]",
    "Mansabdari": "मनसबदारी व्यवस्था [Mansabdari System]",
    "Zabt": "ज़ब्ती प्रणाली [Zabt System]",
    "Din-i-Ilahi": "दीन-ए-इलाही [Din-i-Ilahi]",
    "Maratha": "मराठा साम्राज्य [Maratha Empire]",
    "Ashtapradhan": "अष्टप्रधान [Ashtapradhan]",
    "Chauth": "चौथ [Chauth]",
    "Sardeshmukhi": "सरदेशमुखी [Sardeshmukhi]",
    "East India Company": "ईस्ट इंडिया कंपनी [East India Company]",
    "Permanent Settlement": "स्थायी बंदोबस्त [Permanent Settlement]",
    "Ryotwari": "रैयतवाड़ी [Ryotwari]",
    "Mahalwari": "महलवाड़ी [Mahalwari]",
    "Drain of Wealth": "धन का निष्कासन [Drain of Wealth]",
    "Revolt of 1857": "1857 का विद्रोह [Revolt of 1857]",
    "Indian National Congress": "भारतीय राष्ट्रीय कांग्रेस [Indian National Congress]",
    "Swadeshi": "स्वदेशी आंदोलन [Swadeshi Movement]",
    "Home Rule": "होम रूल आंदोलन [Home Rule Movement]",
    "Rowlatt Act": "रॉलेट एक्ट [Rowlatt Act]",
    "Jallianwala Bagh": "जलियांवाला बाग हत्याकांड [Jallianwala Bagh Massacre]",
    "Non-Cooperation": "असहयोग आंदोलन [Non-Cooperation Movement]",
    "Civil Disobedience": "सविनय अवज्ञा आंदोलन [Civil Disobedience Movement]",
    "Dandi March": "दांडी मार्च [Dandi March]",
    "Quit India": "भारत छोड़ो आंदोलन [Quit India Movement]",
    "Cabinet Mission": "कैबिनेट मिशन [Cabinet Mission]",
    "Constituent Assembly": "संविधान सभा [Constituent Assembly]",
    "Partition": "भारत का विभाजन [Partition of India]"
}

def inject_hindi(text):
    for en, hi in HINDI_TERMS.items():
        if en in text and f"[{en}" not in text:
            # Replace first occurrence
            text = text.replace(en, hi, 1)
    return text

def build_all_structured_chapters():
    pages, ranges, qs = load_base()
    
    # Check if Agent 1 and Agent 2 outputs exist
    ch_1_40 = {}
    if os.path.exists("dashboard-src/subjects/history/chapters_1_40.json"):
        with open("dashboard-src/subjects/history/chapters_1_40.json", encoding="utf-8") as f:
            for c in json.load(f):
                ch_1_40[c["num"]] = c
                
    ch_41_95 = {}
    if os.path.exists("dashboard-src/subjects/history/chapters_41_95.json"):
        with open("dashboard-src/subjects/history/chapters_41_95.json", encoding="utf-8") as f:
            for c in json.load(f):
                ch_41_95[c["num"]] = c

    # Index questions by chapter
    qs_by_ch = defaultdict(list)
    for qid, q in qs.items():
        ch_num = int(q["ch"][1:])
        q["qid"] = qid
        qs_by_ch[ch_num].append(q)

    all_chapters = []

    for entry in ranges:
        num = entry["num"]
        title = entry["title"]
        start_p = entry["start"]
        next_idx = ranges.index(entry) + 1
        end_p = ranges[next_idx]["start"] - 1 if next_idx < len(ranges) else len(pages)
        ch_qs = qs_by_ch.get(num, [])

        # If subagent provided a rich chapter, use it as baseline
        existing = ch_1_40.get(num) or ch_41_95.get(num)
        if existing and existing.get("topics") and len(existing.get("topics")) >= 1:
            # ensure valid formatting
            all_chapters.append(existing)
            continue

        # Otherwise build high-yield structured chapter from raw text & questions
        ch_text = "\n".join(pages[p-1]["text"] for p in range(start_p, end_p + 1))
        q_splits = re.split(r'\n\s*(\d{1,3})\.\s+', '\n' + ch_text)
        intro_raw = clean_text(q_splits[0].strip()) if q_splits else ""

        # Gist
        gist = f"Key historical facts, chronology, and UPPSC questions on {title}."
        
        # Focus: top repeated or most important questions in this chapter
        focus = []
        # Sort questions by repeat count descending
        sorted_qs = sorted(ch_qs, key=lambda q: -q.get("n", 1))
        for q in sorted_qs[:5]:
            n_papers = q.get("n", 1)
            f_text = q.get("f", q["s"])
            f_text = re.sub(r'See the explanation.*', '', f_text).strip()
            if not f_text:
                f_text = q["s"]
            focus.append({
                "fact": f_text[:140] + ("..." if len(f_text) > 140 else ""),
                "exam": q["e"],
                "cnt": f"{n_papers} paper{'s' if n_papers > 1 else ''}"
            })

        # Split into topics
        # Default 2-4 topics based on pages and questions
        topics = []
        t1_id = f"c{num}-t1"
        t1_title = f"{title}: Core Facts and Sources"
        t1_points = []
        
        # Extract points from intro notes (prefixed with * in Ghatna Chakra)
        intro_bullets = [b.strip() for b in intro_raw.split('*') if len(b.strip()) > 20]
        for b in intro_bullets[:15]:
            clean_b = inject_hindi(clean_text(b))
            t1_points.append({
                "html": clean_b,
                "hot": False,
                "asked": False
            })

        # Add questions as high-yield asked points
        t2_id = f"c{num}-t2"
        t2_title = f"{title}: Exam Focus and Inscriptions/Details"
        t2_points = []
        
        for q in ch_qs[:30]:
            is_hot = q.get("n", 1) >= 2
            cnt_str = f" ×{q['n']}" if is_hot else ""
            badge = f'<span class="ps"><span class="p up" title="{q["e"]}">UPPSC{cnt_str}</span></span>'
            
            # Use concise feedback or stem
            core_fact = q.get("f", "")
            if not core_fact or "See the explanation" in core_fact or len(core_fact) < 15:
                # build fact from stem + correct option
                ans_opts = [q["o"][k_idx] for k_idx in q["k"] if k_idx < len(q["o"])]
                ans_txt = ", ".join(ans_opts) if ans_opts else ""
                core_fact = f"{q['s']} → <b>{ans_txt}</b>."
            else:
                core_fact = re.sub(r'\s+', ' ', core_fact).strip()
                
            pt_html = f"{inject_hindi(core_fact)} {badge}"
            target_pts = t2_points if len(t1_points) > 10 else t1_points
            target_pts.append({
                "html": pt_html,
                "hot": is_hot,
                "asked": True
            })

        if t1_points:
            topics.append({
                "id": t1_id,
                "title": t1_title,
                "pg": f"pp. {start_p}–{min(start_p + 2, end_p)}",
                "points": t1_points
            })
            
        if t2_points:
            topics.append({
                "id": t2_id,
                "title": t2_title,
                "pg": f"pp. {min(start_p + 2, end_p)}–{end_p}",
                "points": t2_points
            })

        # If no intro bullets and no questions, create at least 1 topic with key overview
        if not topics:
            topics.append({
                "id": t1_id,
                "title": title,
                "pg": f"pp. {start_p}–{end_p}",
                "points": [{
                    "html": f"Key historical developments regarding {title}.",
                    "hot": False,
                    "asked": False
                }]
            })

        all_chapters.append({
            "num": num,
            "title": title,
            "gist": gist,
            "focus": focus,
            "topics": topics
        })

    with open("dashboard-src/subjects/history/structured_all_chapters.json", "w", encoding="utf-8") as f:
        json.dump(all_chapters, f, indent=2, ensure_ascii=False)
        
    print(f"Generated structured data for all {len(all_chapters)} chapters.")

if __name__ == "__main__":
    build_all_structured_chapters()
