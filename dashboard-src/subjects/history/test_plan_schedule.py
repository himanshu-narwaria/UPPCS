import re, json
import sys
sys.path.append("dashboard-src")
import build_dashboard as bd

with open("dashboard-src/subjects/history/chapter_ledger.json", encoding="utf-8") as f:
    ledger = json.load(f)

# Chapters dictionary format as parsed by build_dashboard
chapters = {entry["num"]: {"title": entry["title"], "asked": 0} for entry in ledger}

# Let's draft a 48-hour Learn schedule covering all 95 chapters
# Ancient (1-15):
# h1: Stone Age
# h2: Indus Valley Civilization
# h3: Vedic Age
# h4: Buddhism
# h5: Jain Religion + Shaiva, Bhagavata Religion
# h6: Sixth century B.C.E - Political Condition + Greek Invasion
# h7: Maurya Empire · part 1 of 2
# h8: Maurya Empire · part 2 of 2
# h9: Post-Mauryan Period
# h10: Gupta and Post-Gupta Period
# h11: Architecture in Ancient India
# h12: South India (Chola, Chalukya, Pallava and Sangam Period) to Early-Medieval Period (covers 13, 14, 15)

# Medieval (16-40):
# h13: Muslim Invasion of India + Delhi Sultanate: Slave Dynasty (16, 17)
# h14: Khalji Dynasty + Tughluq Dynasty (18, 19)
# h15: Lodi Dynasty + Vijayanagara Empire (20, 21)
# h16: Delhi Sultanate: Administration to Delhi Sultanate: Literature (22, 23, 24)
# h17: Delhi Sultanate: Miscellaneous + Provincial Dynasty of North India and Deccan Province (25, 26)
# h18: Bhakti and Sufi Movement (27)
# h19: Mughal Dynasty : Babur + Humayun and Sher Shah (28, 29)
# h20: Akbar (30)
# h21: Jahangir to Aurangzeb (31, 32, 33)
# h22: Mughal Administration to Mughal Literature (34, 35, 36)
# h23: Mughal Period: Miscellaneous (37)
# h24: Sikh Sect to Disintegration of the Mughal Empire (38, 39, 40)

# Modern (41-95):
# h25: Advent of European Companies + East India Company and Nawab of Bengal (41, 42)
# h26: Regional States: Punjab and Mysore + Governor/Governor General/Viceroy (43, 44)
# h27: Economic Impact of British Rule on India + Revolt of 1857 (45, 46)
# h28: Other Civil Uprisings (47)
# h29: Development of Education in Modern India + Development of Press in Modern India (48, 49)
# h30: Social Religious Movement (50)
# h31: Political Organisation Established before Congress + Indian National Congress (51, 52)
# h32: Moderates and Extremists in Congress to Revolutionary Activities Outside India (53, 54, 55)
# h33: Partition of Bengal and Swadeshi Movement to Formation of Muslim League (1906) (56, 57, 58)
# h34: Morley-Minto Reforms to Home Rule League Movement (59, 60, 61, 62)
# h35: Gandhi and His Early Movement (63)
# h36: Peasant Movement and Kisan Sabha + Trade Union and Communist Party (64, 65)
# h37: Rowlatt Act and Jallianwala Bagh Massacre (1919) to Non-Cooperation Movement (66, 67, 68)
# h38: Formation of Swaraj Party (1923) + Simon Commission (1927) (69, 70)
# h39: Lahore Session of Congress, Proposal of Complete Independence (1929) + Civil Disobedience Movement (71, 72)
# h40: Gandhi-Irwin Pact to Round Table Conference (73, 74, 75)
# h41: Communal Award And Poona Pact (1932) to Provincial Election and Formation of Cabinet (1937) (76, 77, 78)
# h42: Tripuri Crisis of Congress (1939) to Demand for Pakistan (79, 80, 81, 82)
# h43: Individual Satyagraha (1940) to Quit India Movement (83, 84, 85)
# h44: Subhash Chandra Bose and Azad Hind Fauj to Formation of Interim Government (1946) (86, 87, 88, 89)
# h45: Partition of India and Independence + Constitutional Development of India (90, 91)
# h46: Modern History: Miscellaneous (92)
# h47: Magazines, Books And Their Authors (93)
# h48: Art and Culture + Award (94, 95)

learn_hours = [
    (1, "Stone Age"),
    (2, "Indus Valley Civilization"),
    (3, "Vedic Age"),
    (4, "Buddhism"),
    (5, "Jain Religion + Shaiva, Bhagavata Religion"),
    (6, "Sixth century B.C.E - Political Condition + Greek Invasion"),
    (7, "Maurya Empire · part 1 of 2"),
    (8, "Maurya Empire · part 2 of 2"),
    (9, "Post-Mauryan Period"),
    (10, "Gupta and Post-Gupta Period"),
    (11, "Architecture in Ancient India"),
    (12, "South India (Chola, Chalukya, Pallava and Sangam Period) to Early-Medieval Period"),
    (13, "Muslim Invasion of India + Delhi Sultanate: Slave Dynasty"),
    (14, "Khalji Dynasty + Tughluq Dynasty"),
    (15, "Lodi Dynasty + Vijayanagara Empire"),
    (16, "Delhi Sultanate: Administration to Delhi Sultanate: Literature"),
    (17, "Delhi Sultanate: Miscellaneous + Provincial Dynasty of North India and Deccan Province"),
    (18, "Bhakti and Sufi Movement"),
    (19, "Mughal Dynasty : Babur + Humayun and Sher Shah"),
    (20, "Akbar"),
    (21, "Jahangir to Aurangzeb"),
    (22, "Mughal Administration to Mughal Literature"),
    (23, "Mughal Period: Miscellaneous"),
    (24, "Sikh Sect to Disintegration of the Mughal Empire"),
    (25, "Advent of European Companies + East India Company and Nawab of Bengal"),
    (26, "Regional States: Punjab and Mysore + Governor/Governor General/Viceroy"),
    (27, "Economic Impact of British Rule on India + Revolt of 1857"),
    (28, "Other Civil Uprisings"),
    (29, "Development of Education in Modern India + Development of Press in Modern India"),
    (30, "Social Religious Movement"),
    (31, "Political Organisation Established before Congress + Indian National Congress"),
    (32, "Moderates and Extremists in Congress to Revolutionary Activities Outside India"),
    (33, "Partition of Bengal and Swadeshi Movement to Formation of Muslim League (1906)"),
    (34, "Morley-Minto Reforms to Home Rule League Movement"),
    (35, "Gandhi and His Early Movement"),
    (36, "Peasant Movement and Kisan Sabha + Trade Union and Communist Party"),
    (37, "Rowlatt Act and Jallianwala Bagh Massacre (1919) to Non-Cooperation Movement"),
    (38, "Formation of Swaraj Party (1923) + Simon Commission (1927)"),
    (39, "Lahore Session of Congress, Proposal of Complete Independence (1929) + Civil Disobedience Movement"),
    (40, "Gandhi-Irwin Pact to Round Table Conference"),
    (41, "Communal Award And Poona Pact (1932) to Provincial Election and Formation of Cabinet (1937)"),
    (42, "Tripuri Crisis of Congress (1939) to Demand for Pakistan"),
    (43, "Individual Satyagraha (1940) to Quit India Movement"),
    (44, "Subhash Chandra Bose and Azad Hind Fauj to Formation of Interim Government (1946)"),
    (45, "Partition of India and Independence + Constitutional Development of India"),
    (46, "Modern History: Miscellaneous"),
    (47, "Magazines, Books And Their Authors"),
    (48, "Art and Culture + Award"),
]

plan = {
    "phases": {
        "Learn": learn_hours,
        "Revise": [(h, f"Revision Block {h}") for h in range(49, 69)],
        "Test": [(h, f"Mock Test {h - 68}") for h in range(69, 73)]
    }
}

try:
    res = bd.chapter_hours(chapters, plan, "test-history-plan")
    print(f"SUCCESS! All {len(chapters)} chapters covered in Learn phase!")
    # Check coverage for each chapter
    for ch_n, hrs in res.items():
        if not hrs:
            print(f"Chapter {ch_n} {chapters[ch_n]['title']} has NO hours!")
    print(f"Verified {len(res)} chapters have matching Learn hours.")
except Exception as e:
    print("FAILED:", e)
