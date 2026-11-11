import json
import re
import os
from collections import defaultdict

HINDI_TERMS = {
    # Indian Geography
    "Tropic of Cancer": "कर्क रेखा [Tropic of Cancer]",
    "Standard Time": "मानक समय [Standard Time]",
    "Equator": "भूमध्य रेखा [Equator]",
    "Passes": "दर्रे [Passes]",
    "Pass": "दर्रा [Pass]",
    "Glaciers": "हिमनद [Glaciers]",
    "Glacier": "हिमनद [Glacier]",
    "Peninsular Plateau": "प्रायद्वीपीय पठार [Peninsular Plateau]",
    "Plateau": "पठार [Plateau]",
    "Drainage System": "अपवाह तंत्र [Drainage System]",
    "Monsoon": "मानसून [Monsoon]",
    "Western Disturbances": "पश्चिमी विक्षोभ [Western Disturbances]",
    "Alluvial": "जलोढ़ [Alluvial]",
    "Black Soil": "काली मिट्टी [Regur / Black Soil]",
    "Red Soil": "लाल मिट्टी [Red Soil]",
    "Laterite": "लैटेराइट [Laterite]",
    "Multi-Purpose": "बहुउद्देशीय परियोजना [Multi-Purpose Project]",
    "Green Revolution": "हरित क्रांति [Green Revolution]",
    "Kharif": "खरीफ फसलें [Kharif crops]",
    "Rabi": "रबी फसलें [Rabi crops]",
    "Zaid": "जायद फसलें [Zaid crops]",
    "Jhuming": "झूम कृषि [Shifting / Jhum Cultivation]",
    "Bauxite": "बॉक्साइट [Bauxite]",
    "Iron Ore": "लौह अयस्क [Iron Ore]",
    "Manganese": "मैंगनीज [Manganese]",
    "Mica": "अभ्रक [Mica]",
    "Coal": "कोयला [Coal]",
    "Petroleum": "पेट्रोलियम [Petroleum]",
    "Hydroelectric": "जलविद्युत [Hydroelectric Power]",
    "Thermal Power": "ताप विद्युत [Thermal Power]",
    "Nuclear Power": "परमाणु ऊर्जा [Nuclear Power]",
    "National Highway": "राष्ट्रीय राजमार्ग [National Highway]",
    
    # World Geography
    "Solar System": "सौर मंडल [Solar System]",
    "Milky Way": "मंदाकिनी / आकाशगंगा [Milky Way]",
    "Black Hole": "ब्लैक होल / कृष्ण विवर [Black Hole]",
    "Latitude": "अक्षांश [Latitude]",
    "Longitude": "देशांतर [Longitude]",
    "Continental Drift": "महाद्वीपीय विस्थापन सिद्धांत [Continental Drift Theory]",
    "Plate Tectonics": "प्लेट विवर्तनिकी [Plate Tectonics]",
    "Igneous": "आग्नेय चट्टानें [Igneous Rocks]",
    "Sedimentary": "अवसादी चट्टानें [Sedimentary Rocks]",
    "Metamorphic": "रूपांतरित / कायांतरित चट्टानें [Metamorphic Rocks]",
    "Volcano": "ज्वालामुखी [Volcano]",
    "Earthquake": "भूकंप [Earthquake]",
    "Seismic": "भूकंपीय तरंगें [Seismic Waves]",
    "Tsunami": "सुनामी [Tsunami]",
    "Mountain": "पर्वत [Mountain]",
    "Desert": "मरुस्थल [Desert]",
    "Grasslands": "घास के मैदान [Grasslands]",
    "Savanna": "सवाना [Savanna]",
    "Steppe": "स्टेपी [Steppe]",
    "Prairies": "प्रेयरी [Prairies]",
    "Pampas": "पम्पास [Pampas]",
    "Veld": "वेल्ड [Veld]",
    "Downs": "डाउन्स [Downs]",
    "Land-locked": "स्थल-रुद्ध देश [Land-locked Countries]",
    "Ocean Currents": "महासागरीय जलधाराएं [Ocean Currents]",
    "Gulf Stream": "गल्फ स्ट्रीम [Gulf Stream]",
    "Kuroshio": "क्यूरोशियो जलधारा [Kuroshio Current]",
    "Oyashio": "ओयाशियो जलधारा [Oyashio Current]",
    "Canary": "कनारी जलधारा [Canary Current]",
    "Benguela": "बेंगुएला जलधारा [Benguela Current]",
    "Salinity": "लवणता [Salinity]",
    "Tides": "ज्वार-भाटा [Tides]",
    "Strait": "जलडमरूमध्य [Strait]",
    "Atmosphere": "वायुमंडल [Atmosphere]",
    "Troposphere": "क्षोभमंडल [Troposphere]",
    "Stratosphere": "समतापमंडल [Stratosphere]",
    "Ozone": "ओजोन परत [Ozone Layer]",
    "Ionosphere": "आयनमंडल [Ionosphere]",
    "Cyclone": "चक्रवात [Cyclone]",
    "Anticyclone": "प्रतिचक्रवात [Anticyclone]",
    "Chinook": "चिनूक पवन [Chinook Wind]",
    "Foehn": "फॉह्न पवन [Foehn Wind]",
    "Sirocco": "सिरोको पवन [Sirocco Wind]",
    "Mistral": "मिस्ट्रल पवन [Mistral Wind]",
    "Taiga": "टैगा वन [Taiga / Boreal Forest]",
    "Tundra": "टुंड्रा [Tundra]"
}

def inject_hindi(text):
    for en, hi in HINDI_TERMS.items():
        if en in text and f"[{en}" not in text and hi not in text:
            text = text.replace(en, hi, 1)
    return text

def build_structured_all():
    base_dir = os.path.join("dashboard-src", "subjects", "geography")
    with open(os.path.join(base_dir, "raw_pages.json"), encoding="utf-8") as f:
        pages = json.load(f)
    with open(os.path.join(base_dir, "accurate_chapter_ranges.json"), encoding="utf-8") as f:
        ranges = json.load(f)
    with open(os.path.join(base_dir, "parsed_uppsc_questions.json"), encoding="utf-8") as f:
        qs = json.load(f)

    # Check for subagent outputs
    p_1_31 = os.path.join(base_dir, "chapters_1_31.json")
    p_32_83 = os.path.join(base_dir, "chapters_32_83.json")
    
    agent_data = {}
    if os.path.exists(p_1_31):
        try:
            with open(p_1_31, encoding="utf-8") as f:
                for c in json.load(f):
                    agent_data[c["num"]] = c
            print(f"Loaded {len(agent_data)} chapters from chapters_1_31.json")
        except Exception as e:
            print(f"Error reading chapters_1_31.json: {e}")
            
    if os.path.exists(p_32_83):
        try:
            with open(p_32_83, encoding="utf-8") as f:
                for c in json.load(f):
                    agent_data[c["num"]] = c
            print(f"Loaded chapters from chapters_32_83.json (total now {len(agent_data)})")
        except Exception as e:
            print(f"Error reading chapters_32_83.json: {e}")

    # Map questions to chapters
    qs_by_ch = defaultdict(list)
    for qid, q in qs.items():
        ch_num = int(q["ch"][1:])
        q["qid"] = qid
        qs_by_ch[ch_num].append(q)

    all_chapters = []
    for entry in ranges:
        num = entry["num"]
        title = entry["title"]
        start_p = entry["pdf_start"]
        end_p = entry["calc_end_page"]
        ch_qs = qs_by_ch.get(num, [])

        if num in agent_data and agent_data[num].get("topics") and len(agent_data[num]["topics"]) >= 1:
            ch_obj = agent_data[num]
            ch_obj["title"] = title # ensure title matches updated disambiguated title
            all_chapters.append(ch_obj)
            continue

        # Fallback generator
        ch_text = "\n".join(pages[p-1]["text"] for p in range(start_p, end_p + 1))
        ch_text_clean = re.sub(r'CA–\d+\s+General Studies\s+Indian Geography', '', ch_text)
        ch_text_clean = re.sub(r'CB–\d+\s+General Studies\s+World Geography', '', ch_text_clean)
        ch_text_clean = re.sub(r'search on TG-@freepdfhall', '', ch_text_clean)
        ch_text_clean = re.sub(r'click here -@PdfTaskari', '', ch_text_clean)

        intro_splits = re.split(r'\n\s*1\.\s+', ch_text_clean)
        intro_raw = intro_splits[0].strip() if intro_splits else ""

        gist = f"Comprehensive revision points and UPPSC questions on {title}."

        # Focus
        focus = []
        sorted_qs = sorted(ch_qs, key=lambda q: -q.get("n", 1))
        for q in sorted_qs[:5]:
            f_text = q.get("f", q["s"])
            f_text = re.sub(r'See the explanation.*', '', f_text).strip()
            if not f_text or len(f_text) < 15:
                ans_opts = [q["o"][k_idx] for k_idx in q["k"] if k_idx < len(q["o"])]
                ans_txt = ", ".join(ans_opts) if ans_opts else ""
                f_text = f"{q['s']} → {ans_txt}"
            focus.append({
                "fact": f_text[:140] + ("..." if len(f_text) > 140 else ""),
                "exam": q["e"],
                "cnt": f"{q['n']} paper{'s' if q['n'] > 1 else ''}"
            })

        # Topics
        topics = []
        t1_id = f"c{num}-t1"
        t1_title = f"{title}: Key Concepts & Overview"
        t1_points = []

        intro_bullets = [b.strip() for b in intro_raw.split('*') if len(b.strip()) > 20]
        for b in intro_bullets[:12]:
            clean_b = inject_hindi(re.sub(r'\s+', ' ', b))
            t1_points.append({
                "html": clean_b,
                "hot": False,
                "asked": False
            })

        t2_id = f"c{num}-t2"
        t2_title = f"{title}: UPPSC Exam Focus & Questions"
        t2_points = []
        for q in ch_qs[:25]:
            is_hot = q.get("n", 1) >= 2
            ans_opts = [q["o"][k_idx] for k_idx in q["k"] if k_idx < len(q["o"])]
            ans_txt = ", ".join(ans_opts) if ans_opts else ""
            f_body = q.get("f", "")
            if not f_body or "See the explanation" in f_body or len(f_body) < 15:
                pt_html = f"<b>{q['s']}</b>: Answer is <b>{ans_txt}</b>."
            else:
                pt_html = f"<b>{q['s']}</b>: {f_body}"
            pt_html = inject_hindi(re.sub(r'\s+', ' ', pt_html))
            t2_points.append({
                "html": pt_html,
                "hot": is_hot,
                "asked": True
            })

        topics.append({
            "id": t1_id,
            "title": t1_title,
            "points": t1_points if t1_points else [{"html": f"Core revision concepts for {title}.", "hot": False, "asked": False}]
        })
        topics.append({
            "id": t2_id,
            "title": t2_title,
            "points": t2_points if t2_points else [{"html": f"Key facts tested by UPPSC on {title}.", "hot": False, "asked": False}]
        })

        all_chapters.append({
            "num": num,
            "title": title,
            "section": entry["section"],
            "gist": gist,
            "focus": focus,
            "topics": topics
        })

    out_file = os.path.join(base_dir, "structured_all_chapters.json")
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(all_chapters, f, indent=2, ensure_ascii=False)

    print(f"Saved {len(all_chapters)} structured chapters to {out_file}")

if __name__ == "__main__":
    build_structured_all()
