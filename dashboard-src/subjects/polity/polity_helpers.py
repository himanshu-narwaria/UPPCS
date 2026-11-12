import re
import json

HINDI_TERMS = [
    ("Constitutional Development", "संवैधानिक विकास"),
    ("Constituent Assembly", "संविधान सभा"),
    ("Drafting Committee", "प्रारूप समिति"),
    ("Preamble", "प्रस्तावना"),
    ("Sovereign", "संपूर्ण प्रभुत्व संपन्न"),
    ("Socialist", "समाजवादी"),
    ("Secular", "पंथनिरपेक्ष"),
    ("Democratic", "लोकतंत्रात्मक"),
    ("Republic", "गणराज्य"),
    ("Justice", "न्याय"),
    ("Liberty", "स्वतंत्रता"),
    ("Equality", "समता"),
    ("Fraternity", "बंधुत्व"),
    ("Fundamental Rights", "मौलिक अधिकार"),
    ("Right to Equality", "समता का अधिकार"),
    ("Right to Freedom", "स्वतंत्रता का अधिकार"),
    ("Preventive Detention", "निवारक निरोध"),
    ("Right against Exploitation", "शोषण के विरुद्ध अधिकार"),
    ("Freedom of Religion", "धर्म की स्वतंत्रता"),
    ("Constitutional Remedies", "संवैधानिक उपचार"),
    ("Habeas Corpus", "बंदी प्रत्यक्षीकरण"),
    ("Mandamus", "परमादेश"),
    ("Prohibition", "प्रतिषेध"),
    ("Certiorari", "उत्प्रेषण"),
    ("Quo-Warranto", "अधिकार पृच्छा"),
    ("Directive Principles of State Policy", "राज्य के नीति निदेशक तत्व"),
    ("Directive Principles", "नीति निदेशक तत्व"),
    ("Uniform Civil Code", "समान नागरिक संहिता"),
    ("Fundamental Duties", "मौलिक कर्तव्य"),
    ("President", "राष्ट्रपति"),
    ("Electoral College", "निर्वाचक मंडल"),
    ("Impeachment", "महाभियोग"),
    ("Ordinance", "अध्यादेश"),
    ("Pardon", "क्षमादान"),
    ("Vice-President", "उपराष्ट्रपति"),
    ("Council of Ministers", "मंत्रिपरिषद"),
    ("Cabinet", "मंत्रिमंडल"),
    ("Prime Minister", "प्रधानमंत्री"),
    ("Collective Responsibility", "सामूहिक उत्तरदायित्व"),
    ("Attorney General", "महान्यायवादी"),
    ("Advocate General", "महाधिवक्ता"),
    ("Solicitor General", "सॉलिसिटर जनरल"),
    ("Comptroller and Auditor General", "नियंत्रक एवं महालेखापरीक्षक"),
    ("Order of Precedence", "वरीयता अनुक्रम"),
    ("Parliament", "संसद"),
    ("Lok Sabha", "लोकसभा"),
    ("Rajya Sabha", "राज्यसभा"),
    ("Speaker", "अध्यक्ष"),
    ("Deputy Speaker", "उपाध्यक्ष"),
    ("Chairman", "सभापति"),
    ("Deputy Chairman", "उपसभापति"),
    ("Money Bill", "धन विधेयक"),
    ("Financial Bill", "वित्त विधेयक"),
    ("Ordinary Bill", "साधारण विधेयक"),
    ("Joint Sitting", "संयुक्त बैठक"),
    ("Prorogation", "सत्रावसान"),
    ("Dissolution", "विघटन"),
    ("Adjournment", "स्थगन"),
    ("Quorum", "गणपूर्ति"),
    ("Question Hour", "प्रश्नकाल"),
    ("Zero Hour", "शून्यकाल"),
    ("No-Confidence Motion", "अविश्वास प्रस्ताव"),
    ("Parliamentary Committees", "संसदीय समितियां"),
    ("Public Accounts Committee", "लोक लेखा समिति"),
    ("Estimates Committee", "प्राक्कलन समिति"),
    ("Committee on Public Undertakings", "सार्वजनिक उपक्रम समिति"),
    ("Supreme Court", "सर्वोच्च न्यायालय"),
    ("Judicial Review", "न्यायिक पुनरावलोकन"),
    ("Original Jurisdiction", "मूल क्षेत्राधिकार"),
    ("Appellate Jurisdiction", "अपीलीय क्षेत्राधिकार"),
    ("Advisory Jurisdiction", "परामर्शदात्री क्षेत्राधिकार"),
    ("Court of Record", "अभिलेख न्यायालय"),
    ("Public Interest Litigation", "जनहित याचिका"),
    ("Basic Structure", "मूल संरचना"),
    ("High Court", "उच्च न्यायालय"),
    ("Subordinate Courts", "अधीनस्थ न्यायालय"),
    ("Governor", "राज्यपाल"),
    ("State Legislature", "राज्य विधानमंडल"),
    ("Legislative Assembly", "विधानसभा"),
    ("Legislative Council", "विधान परिषद"),
    ("Chief Minister", "मुख्यमंत्री"),
    ("Centre-State Relations", "केंद्र-राज्य संबंध"),
    ("Inter-State Council", "अंतर-राज्य परिषद"),
    ("Finance Commission", "वित्त आयोग"),
    ("Emergency Provisions", "आपातकालीन उपबंध"),
    ("National Emergency", "राष्ट्रीय आपातकाल"),
    ("President's Rule", "राष्ट्रपति शासन"),
    ("Financial Emergency", "वित्तीय आपातकाल"),
    ("Election Commission", "निर्वाचन आयोग"),
    ("Chief Election Commissioner", "मुख्य निर्वाचन आयुक्त"),
    ("Delimitation Commission", "परिसीमन आयोग"),
    ("Model Code of Conduct", "आदर्श आचार संहिता"),
    ("Political Parties", "राजनीतिक दल"),
    ("National Party", "राष्ट्रीय दल"),
    ("Anti-Defection Law", "दल-बदल विरोधी कानून"),
    ("Official Language", "राजभाषा"),
    ("Eighth Schedule", "आठवीं अनुसूची"),
    ("Panchayati Raj", "पंचायती राज"),
    ("Democratic Decentralization", "लोकतांत्रिक विकेंद्रीकरण"),
    ("Gram Sabha", "ग्राम सभा"),
    ("Gram Panchayat", "ग्राम पंचायत"),
    ("Panchayat Samiti", "पंचायत समिति"),
    ("Zila Parishad", "जिला परिषद"),
    ("Municipality", "नगरपालिका"),
    ("Municipal Corporation", "नगर निगम"),
    ("State Election Commission", "राज्य निर्वाचन आयोग"),
    ("State Finance Commission", "राज्य वित्त आयोग"),
    ("Constitutional Amendment", "संविधान संशोधन"),
    ("Scheduled Castes", "अनुसूचित जातियां"),
    ("Scheduled Tribes", "अनुसूचित जनजातियां"),
    ("Backward Classes", "पिछड़ा वर्ग"),
    ("Lokpal", "लोकपाल"),
    ("Lokayukta", "लोकायुक्त"),
    ("Central Vigilance Commission", "केंद्रीय सतर्कता आयोग"),
    ("Central Information Commission", "केंद्रीय सूचना आयोग"),
    ("National Human Rights Commission", "राष्ट्रीय मानवाधिकार आयोग"),
    ("NITI Aayog", "नीति आयोग"),
    ("Planning Commission", "योजना आयोग"),
    ("Schedules", "अनुसूचियां"),
    ("Citizenship", "नागरिकता"),
    ("Single Citizenship", "एकल नागरिकता"),
    ("Bicameral", "द्विसदनीय"),
    ("Rule of Law", "विधि का शासन"),
    ("Procedure Established by Law", "विधि द्वारा स्थापित प्रक्रिया"),
    ("Due Process of Law", "विधि की सम्यक प्रक्रिया")
]

def clean_fact(text):
    if not text:
        return ""
    text = re.sub(r'D[–-]\d+\s+General Studies.*?\n', ' ', text)
    text = re.sub(r'General Studies\s+Indian Polity and Governance.*?\n', ' ', text)
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
        if f"({hin})" in text or f"[{hin}]" in text or f"/{hin}" in text:
            continue
        pat = rf'\b{re.escape(eng)}\b'
        m = re.search(pat, text, re.I)
        if m:
            matched_eng = m.group(0)
            text = text[:m.start()] + f"{matched_eng} ({hin})" + text[m.end():]
            break
    return text
