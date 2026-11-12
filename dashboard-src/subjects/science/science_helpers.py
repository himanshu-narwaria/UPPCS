import re
import json

HINDI_TERMS = [
    ("Measurement", "मापन"),
    ("Unit", "मात्रक"),
    ("Work", "कार्य"),
    ("Energy", "ऊर्जा"),
    ("Power", "शक्ति"),
    ("Force", "बल"),
    ("Gravity", "गुरुत्वाकर्षण"),
    ("Gravitational", "गुरुत्वाकर्षण"),
    ("Acceleration", "त्वरण"),
    ("Velocity", "वेग"),
    ("Speed", "चाल"),
    ("Mass", "द्रव्यमान"),
    ("Weight", "भार"),
    ("Pressure", "दाब"),
    ("Atmospheric Pressure", "वायुमंडलीय दाब"),
    ("Density", "घनत्व"),
    ("Surface Tension", "पृष्ठ तनाव"),
    ("Capillarity", "केशिकत्व"),
    ("Viscosity", "श्यानता"),
    ("Light", "प्रकाश"),
    ("Reflection", "परावर्तन"),
    ("Refraction", "अपवर्तन"),
    ("Total Internal Reflection", "पूर्ण आंतरिक परावर्तन"),
    ("Dispersion", "विक्षेपण"),
    ("Scattering", "प्रकीर्णन"),
    ("Diffraction", "विवर्तन"),
    ("Interference", "व्यतिकरण"),
    ("Heat", "ऊष्मा"),
    ("Temperature", "तापमान"),
    ("Conduction", "चालन"),
    ("Convection", "संवहन"),
    ("Radiation", "विकिरण"),
    ("Sound", "ध्वनि"),
    ("Frequency", "आवृत्ति"),
    ("Wavelength", "तरंगदैर्ध्य"),
    ("Amplitude", "आयाम"),
    ("Resonance", "अनुनाद"),
    ("Echo", "प्रतिध्वनि"),
    ("Electric Current", "विद्युत धारा"),
    ("Resistance", "प्रतिरोध"),
    ("Conductivity", "चालकता"),
    ("Superconductivity", "अतिचालकता"),
    ("Semiconductor", "अर्धचालक"),
    ("Insulator", "विद्युतरोधी"),
    ("Nuclear Fission", "नाभिकीय विखंडन"),
    ("Nuclear Fusion", "नाभिकीय संलयन"),
    ("Radioactivity", "रेडियोधर्मिता"),
    ("Half-life", "अर्ध-आयु"),
    ("Atom", "परमाणु"),
    ("Molecule", "अणु"),
    ("Electron", "इलेक्ट्रॉन"),
    ("Proton", "प्रोटॉन"),
    ("Neutron", "न्यूट्रॉन"),
    ("Element", "तत्व"),
    ("Compound", "यौगिक"),
    ("Mixture", "मिश्रण"),
    ("Isotopes", "समस्थानिक"),
    ("Isobars", "समभारिक"),
    ("Acid", "अम्ल"),
    ("Base", "क्षार"),
    ("Salt", "लवण"),
    ("Polymer", "बहुलक"),
    ("Polymerization", "बहुलकीकरण"),
    ("Catalyst", "उत्प्रेरक"),
    ("Oxidation", "ऑक्सीकरण"),
    ("Reduction", "अपचयन"),
    ("Corrosion", "संक्षारण"),
    ("Galvanization", "यशदीकरण"),
    ("Alloy", "मिश्र धातु"),
    ("Hydrocarbon", "हाइड्रोकार्बन"),
    ("Fertilizer", "उर्वरक"),
    ("Biofertilizer", "जैव उर्वरक"),
    ("Photosynthesis", "प्रकाश संश्लेषण"),
    ("Respiration", "श्वसन"),
    ("Digestion", "पाचन"),
    ("Circulation", "परिसंचरण"),
    ("Excretion", "उत्सर्जन"),
    ("Hormone", "हार्मोन"),
    ("Enzyme", "एंजाइम"),
    ("Vitamin", "विटामिन"),
    ("Cell", "कोशिका"),
    ("Chromosome", "गुणसूत्र"),
    ("Gene", "जीन"),
    ("Heredity", "आनुवंशिकता"),
    ("Mutation", "उत्परिवर्तन"),
    ("Evolution", "जैव विकास"),
    ("Taxonomy", "वर्गिकी"),
    ("Vaccine", "टीका"),
    ("Antibiotic", "प्रतिजैविक"),
    ("Antibody", "प्रतिरक्षी"),
    ("Antigen", "प्रतिजन"),
    ("Immunity", "प्रतिरक्षा"),
    ("Pathogen", "रोगजनक"),
    ("Parasite", "परजीवी"),
    ("Vector", "वाहक"),
    ("Fungus", "कवक"),
    ("Bacteria", "जीवाणु"),
    ("Virus", "विषाणु"),
    ("Protozoa", "प्रोटोजोआ"),
    ("Algae", "शैवाल"),
    ("Lichen", "लाइकेन"),
    ("Symbiosis", "सहजीविता"),
    ("Endocrine", "अंतःस्रावी"),
    ("Exocrine", "बहिःस्रावी"),
    ("Nervous System", "तंत्रिका तंत्र"),
    ("Brain", "मस्तिष्क"),
    ("Spinal Cord", "मेरुरज्जु"),
    ("Heart", "हृदय"),
    ("Kidney", "वृक्क/गुर्दा"),
    ("Liver", "यकृत"),
    ("Pancreas", "अग्न्याशय"),
    ("Lungs", "फेफड़े"),
    ("Stomach", "आमाशय"),
    ("Intestine", "आंत"),
    ("Hemoglobin", "हीमोग्लोबिन"),
    ("Platelets", "प्लेटलेट्स/पट्टिकाणु"),
    ("Plasma", "प्लाज्मा"),
    ("Blood Group", "रक्त समूह"),
    ("Blood Pressure", "रक्तचाप"),
]

def clean_fact(text):
    if not text:
        return ""
    text = re.sub(r'General Science\s+General Studies\s+G[–-]\d+', '', text)
    text = re.sub(r'G[–-]\d+\s+General Studies\s+General Science', '', text)
    text = re.sub(r'search on TG-@freepdfhall', '', text)
    text = re.sub(r'click here -@freepdfhall', '', text)
    text = re.sub(r'click here -@PdfTaskari', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def inject_hindi(text):
    if not text:
        return ""
    # Inject standard Hindi term at first occurrence
    for eng, hin in HINDI_TERMS:
        # Avoid double injection
        if f"({hin})" in text or f"/{hin}" in text:
            continue
        pat = rf'\b{re.escape(eng)}\b'
        # Check if match exists and replace first occurrence only
        m = re.search(pat, text, re.I)
        if m:
            matched_eng = m.group(0)
            text = text[:m.start()] + f"{matched_eng} ({hin})" + text[m.end():]
    return text
