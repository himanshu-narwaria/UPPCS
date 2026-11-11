import os, json, re

# Chapter list from TOC (page 3)
# We will define the 95 chapters with their nominal B-page ranges from the TOC
# and then verify the exact start page for each in raw_pages.json

TOC_ENTRIES = [
    # I. Ancient History of India
    (1, "Stone Age", "B9-B16"),
    (2, "Indus Valley Civilization", "B17-B32"),
    (3, "Vedic Age", "B32-B48"),
    (4, "Buddhism", "B48-B70"),
    (5, "Jain Religion", "B71-B81"),
    (6, "Shaiva, Bhagavata Religion", "B81-B87"),
    (7, "Sixth century B.C.E - Political Condition", "B87-B96"),
    (8, "Greek Invasion", "B96-B98"),
    (9, "Maurya Empire", "B98-B119"),
    (10, "Post-Mauryan Period", "B119-B129"),
    (11, "Gupta and Post-Gupta Period", "B130-B156"),
    (12, "Architecture in Ancient India", "B156-B169"),
    (13, "South India (Chola, Chalukya, Pallava and Sangam Period)", "B170-B183"),
    (14, "Ancient Literature and Litterateur", "B183-B195"),
    (15, "Early-Medieval Period", "B195-B203"),

    # II. Medieval History of India
    (16, "Muslim Invasion of India", "B204-B210"),
    (17, "Delhi Sultanate: Slave Dynasty", "B210-B217"),
    (18, "Khalji Dynasty", "B217-B223"),
    (19, "Tughluq Dynasty", "B223-B230"),
    (20, "Lodi Dynasty", "B230-B232"),
    (21, "Vijayanagara Empire", "B232-B239"),
    (22, "Delhi Sultanate: Administration", "B239-B244"),
    (23, "Delhi Sultanate: Art and Architecture", "B244-B247"),
    (24, "Delhi Sultanate: Literature", "B247-B253"),
    (25, "Delhi Sultanate: Miscellaneous", "B253-B257"),
    (26, "Provincial Dynasty of North India and Deccan Province", "B257-B263"),
    (27, "Bhakti and Sufi Movement", "B263-B278"),
    (28, "Mughal Dynasty : Babur", "B278-B283"),
    (29, "Humayun and Sher Shah", "B283-B288"),
    (30, "Akbar", "B288-B300"),
    (31, "Jahangir", "B300-B305"),
    (32, "Shah Jahan", "B305-B309"),
    (33, "Aurangzeb", "B309-B313"),
    (34, "Mughal Administration", "B313-B319"),
    (35, "Music and Paintings of Mughal Period", "B319-B322"),
    (36, "Mughal Literature", "B322-B326"),
    (37, "Mughal Period: Miscellaneous", "B326-B334"),
    (38, "Sikh Sect", "B334-B337"),
    (39, "Maratha State and Confederacy", "B337-B343"),
    (40, "Disintegration of the Mughal Empire", "B343-B347"),

    # III. Modern History of India
    (41, "Advent of European Companies", "B348-B358"),
    (42, "East India Company and Nawab of Bengal", "B358-B363"),
    (43, "Regional States: Punjab and Mysore", "B363-B368"),
    (44, "Governor/Governor General/Viceroy", "B368-B389"),
    (45, "Economic Impact of British Rule on India", "B389-B397"),
    (46, "Revolt of 1857", "B397-B412"),
    (47, "Other Civil Uprisings", "B412-B427"),
    (48, "Development of Education in Modern India", "B427-B434"),
    (49, "Development of Press in Modern India", "B435-B446"),
    (50, "Social Religious Movement", "B446-B469"),
    (51, "Political Organisation Established before Congress", "B469-B474"),
    (52, "Indian National Congress", "B474-B486"),
    (53, "Moderates and Extremists in Congress", "B486-B492"),
    (54, "Revolutionary Movement in India", "B492-B505"),
    (55, "Revolutionary Activities Outside India", "B505-B511"),
    (56, "Partition of Bengal and Swadeshi Movement", "B511-B517"),
    (57, "Congress: Banaras, Calcutta, and Surat Session", "B517-B520"),
    (58, "Formation of Muslim League (1906)", "B520-B522"),
    (59, "Morley-Minto Reforms", "B522-B524"),
    (60, "Delhi Durbar and Change of Capital", "B524-B525"),
    (61, "Lucknow Session of Congress (The Lucknow Pact)", "B525-B527"),
    (62, "Home Rule League Movement", "B527-B529"),
    (63, "Gandhi and His Early Movement", "B529-B545"),
    (64, "Peasant Movement and Kisan Sabha", "B545-B550"),
    (65, "Trade Union and Communist Party", "B551-B553"),
    (66, "Rowlatt Act and Jallianwala Bagh Massacre (1919)", "B553-B559"),
    (67, "Khilafat Movement", "B559-B562"),
    (68, "Non-Cooperation Movement", "B562-B570"),
    (69, "Formation of Swaraj Party (1923)", "B571-B574"),
    (70, "Simon Commission (1927)", "B575-B578"),
    (71, "Lahore Session of Congress, Proposal of Complete Independence (1929)", "B578-B581"),
    (72, "Civil Disobedience Movement", "B581-B587"),
    (73, "Gandhi-Irwin Pact", "B587-B589"),
    (74, "Karachi Session of Congress (1931)", "B589-B590"),
    (75, "Round Table Conference", "B590-B593"),
    (76, "Communal Award And Poona Pact (1932)", "B593-B597"),
    (77, "Congress Socialist Party (1934)", "B597-B599"),
    (78, "Provincial Election and Formation of Cabinet (1937)", "B600-B602"),
    (79, "Tripuri Crisis of Congress (1939)", "B602-B604"),
    (80, "Indian Princely States", "B604-B605"),
    (81, "Second World War", "B605-B607"),
    (82, "Demand for Pakistan", "B607-B609"),
    (83, "Individual Satyagraha (1940)", "B610-B611"),
    (84, "Cripps Mission (1942)", "B611-B612"),
    (85, "Quit India Movement", "B612-B623"),
    (86, "Subhash Chandra Bose and Azad Hind Fauj", "B623-B629"),
    (87, "Cabinet Mission Plan (1946)", "B630-B633"),
    (88, "Constituent Assembly (1946)", "B633-B635"),
    (89, "Formation of Interim Government (1946)", "B635-B637"),
    (90, "Partition of India and Independence", "B637-B645"),
    (91, "Constitutional Development of India", "B645-B657"),
    (92, "Modern History: Miscellaneous", "B658-B707"),
    (93, "Magazines, Books And Their Authors", "B707-B734"),
    (94, "Art and Culture", "B734-B756"),
    (95, "Award", "B756-B760"),
]

with open("dashboard-src/subjects/history/raw_pages.json", encoding="utf-8") as f:
    pages = json.load(f)

print(f"Total entries: {len(TOC_ENTRIES)}")

# Check each entry in raw_pages to verify exact page where heading appears
results = []
for n, title, nominal in TOC_ENTRIES:
    # nominal e.g. "B9-B16"
    m = re.match(r'B(\d+)-B(\d+)', nominal)
    start_p, end_p = int(m.group(1)), int(m.group(2))
    
    # Let's search around start_p in pages (start_p-2 to start_p+2)
    found_page = None
    # simplify title for search
    key_words = [w for w in re.sub(r'[^a-zA-Z0-9\s]', ' ', title).split() if len(w) > 3]
    for p_num in range(max(1, start_p - 2), min(len(pages), start_p + 3) + 1):
        txt = pages[p_num - 1]["text"]
        # Check if title appears near top of page (first 10 lines)
        lines = [l.strip() for l in txt.split('\n')[:12]]
        for l in lines:
            matches = sum(1 for w in key_words if w.lower() in l.lower())
            if len(key_words) > 0 and matches >= max(1, len(key_words) // 2):
                found_page = p_num
                break
        if found_page:
            break
            
    results.append({
        "num": n,
        "title": title,
        "nominal": nominal,
        "nominal_start": start_p,
        "nominal_end": end_p,
        "found_start": found_page or start_p
    })

print(f"{'No':3} | {'Title':45} | {'Nominal':9} | {'Found':5} | {'Diff'}")
print("-" * 75)
for r in results:
    diff = r["found_start"] - r["nominal_start"]
    diff_str = f"{diff:+d}" if diff != 0 else "OK"
    print(f"{r['num']:3d} | {r['title'][:45]:45} | {r['nominal']:9} | {r['found_start']:5d} | {diff_str}")

with open("dashboard-src/subjects/history/chapter_ledger.json", "w", encoding="utf-8") as f:
    json.dump(results, f, indent=2)
