import sys, json, re, os
sys.path.insert(0, 'dashboard-src/subjects/geography')
from chapter_definitions_1_31 import CHAPTER_DATA

with open("dashboard-src/subjects/geography/accurate_chapter_ranges.json", encoding="utf-8") as f:
    ranges = json.load(f)

with open("dashboard-src/subjects/geography/parsed_uppsc_questions.json", encoding="utf-8") as f:
    qs = json.load(f)

# Group questions by chapter
qs_by_ch = {}
for qid, q in qs.items():
    ch_num = int(q["ch"][1:])
    if ch_num not in qs_by_ch:
        qs_by_ch[ch_num] = []
    q["qid"] = qid
    qs_by_ch[ch_num].append(q)

HINDI_TERMS = {
    "Tropic of Cancer": "कर्क रेखा [Tropic of Cancer]",
    "Standard Time": "मानक समय [Standard Time]",
    "Indian Standard Time": "भारतीय मानक समय [Indian Standard Time]",
    "Passes": "दर्रे [Mountain Passes]",
    "Pass": "दर्रा [Mountain Pass]",
    "Glaciers": "हिमनद [Glaciers]",
    "Glacier": "हिमनद [Glacier]",
    "Peninsular Plateau": "प्रायद्वीपीय पठार [Peninsular Plateau]",
    "Drainage System": "अपवाह तंत्र [Drainage System]",
    "Multi-Purpose River Valley Project": "बहुउद्देशीय नदी घाटी परियोजना [Multi-Purpose River Valley Project]",
    "Multi-purpose River Valley Project": "बहुउद्देशीय नदी घाटी परियोजना [Multi-Purpose River Valley Project]",
    "Cyclone": "चक्रवात [Cyclone]",
    "Cyclones": "चक्रवात [Cyclones]",
    "Bhabhar": "भाबर [Bhabhar]",
    "Terai": "तराई [Terai]",
    "Alluvial Soil": "जलोढ़ मिट्टी [Alluvial Soil]",
    "Alluvial plain": "जलोढ़ मैदान [Alluvial Plain]",
    "Alluvial": "जलोढ़ [Alluvial]",
    "Khadar": "खादर [Khadar]",
    "Bangar": "बांगर [Bangar]",
    "Black Cotton Soil": "काली मिट्टी [Black Cotton Soil]",
    "Black Soil": "काली मिट्टी [Black Soil]",
    "Regur": "रेगुर [Regur]",
    "Red Soil": "लाल मिट्टी [Red Soil]",
    "Laterite Soil": "लैटेराइट मिट्टी [Laterite Soil]",
    "Western Disturbances": "पश्चिमी विक्षोभ [Western Disturbances]",
    "Western Disturbance": "पश्चिमी विक्षोभ [Western Disturbance]",
    "South-West Monsoon": "दक्षिण-पश्चिम मानसून [South-West Monsoon]",
    "North-East Monsoon": "उत्तर-पूर्वी मानसून [North-East Monsoon]",
    "Retreating Monsoon": "लौटता मानसून [Retreating Monsoon]",
    "Green Revolution": "हरित क्रांति [Green Revolution]",
    "Shifting Cultivation": "झूम कृषि [Shifting Cultivation]",
    "Jhum Cultivation": "झूम कृषि [Jhum Cultivation]",
    "Jhuming": "झूम कृषि [Jhuming]",
    "Kharif": "खरीफ [Kharif]",
    "Rabi": "रबी [Rabi]",
    "Zaid": "जायद [Zaid]",
    "Silk": "रेशम [Silk]",
    "Sericulture": "रेशम कीट पालन [Sericulture]",
    "Plantation Crops": "रोपण फसलें [Plantation Crops]",
    "Cash Crops": "नकदी फसलें [Cash Crops]",
    "Pulses": "दलहन [Pulses]",
    "Oilseeds": "तिलहन [Oilseeds]",
    "Oilseed": "तिलहन [Oilseed]",
    "Animal Husbandry": "पशुपालन [Animal Husbandry]",
    "Livestock": "पशुधन [Livestock]",
    "Mineral Resources": "खनिज संसाधन [Mineral Resources]",
    "Coal": "कोयला [Coal]",
    "Iron Ore": "लौह अयस्क [Iron Ore]",
    "Bauxite": "बॉक्साइट [Bauxite]",
    "Mica": "अभ्रक [Mica]",
    "Limestone": "चूना पत्थर [Limestone]",
    "Nuclear Energy": "परमाणु ऊर्जा [Nuclear Energy]",
    "Nuclear Power": "परमाणु ऊर्जा [Nuclear Power]",
    "Thermal Power": "ताप विद्युत [Thermal Power]",
    "Hydroelectric Power": "जल विद्युत [Hydroelectric Power]",
    "National Waterways": "राष्ट्रीय जलमार्ग [National Waterways]",
    "National Waterway": "राष्ट्रीय जलमार्ग [National Waterway]",
    "Golden Quadrilateral": "स्वर्णिम चतुर्भुज [Golden Quadrilateral]",
    "Wildlife Sanctuary": "वन्यजीव अभयारण्य [Wildlife Sanctuary]",
    "National Park": "राष्ट्रीय उद्यान [National Park]",
    "Biosphere Reserve": "जैवमंडल आरक्षित क्षेत्र [Biosphere Reserve]",
    "Mangrove": "मैंग्रोव [Mangrove]",
    "Mangroves": "मैंग्रोव वन [Mangrove Forests]"
}

SORTED_TERMS = sorted(HINDI_TERMS.keys(), key=lambda x: -len(x))

def inject_hindi(text):
    for en in SORTED_TERMS:
        hi = HINDI_TERMS[en]
        pattern = r'\b' + re.escape(en) + r'\b'
        if re.search(pattern, text, re.I):
            if f"[{en}" not in text and hi not in text:
                text = re.sub(pattern, hi, text, count=1, flags=re.I)
    return text

def clean_fact(text):
    text = re.sub(r'CA–\d+\s+General Studies\s+Indian Geography', '', text)
    text = re.sub(r'CB–\d+\s+General Studies\s+World Geography', '', text)
    text = re.sub(r'search on TG-@freepdfhall', '', text)
    text = re.sub(r'click here -@PdfTaskari', '', text)
    text = re.sub(r'click here -@freepdfhall', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

print("Modules initialized successfully.")
