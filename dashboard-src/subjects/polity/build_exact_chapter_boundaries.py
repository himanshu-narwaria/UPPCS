import json
import re

with open("dashboard-src/subjects/polity/raw_pages.json", "r", encoding="utf-8") as f:
    pages = json.load(f)

# Candidate start pages based on book headings found
# (ch_num, title, start_page)
candidates = [
    (1, "The Constitutional Development of India", 7),
    (2, "Constituent Assembly and Making of the Constitution", 17),
    (3, "Important Committees of Constituent Assembly", 29),
    (4, "Sources of the Constitution", 31),
    (5, "Parts of Indian Constitution", 37),
    (6, "Articles of the Constitution", 41),
    (7, "Schedules", 50),
    (8, "The Preamble", 61),
    (9, "The Governance System", 69),
    (10, "National Symbols", 87),
    (11, "States and Union Territories", 90),
    (12, "The Citizenship", 102),
    (13, "Fundamental Rights", 105),
    (14, "Directive Principles of State Policy", 136),
    (15, "Fundamental Duties", 150),
    (16, "The President", 156),
    (17, "The Vice-President", 179),
    (18, "The Council of Ministers", 184),
    (19, "The Attorney General and the C.A.G.", 199),
    (20, "Order of Precedence", 210),
    (21, "The Parliament (1)", 212),
    (22, "The Parliament (2)", 231),
    (23, "The Parliament (3)", 243),
    (24, "Parliamentary Committees", 269),
    (25, "The Parliamentary Act", 277),
    (26, "The Supreme Court", 295),
    (27, "The Governor", 320),
    (28, "The State Legislature", 331),
    (29, "The High Court", 347),
    (30, "The Centre-State Relations", 356),
    (31, "Emergency Provisions", 367),
    (32, "The Finance Commission", 375),
    (33, "The Planning Commission/NITI Aayog", 381),
    (34, "Lokpal and Important Commissions", 386),
    (35, "Temporary, Transitional and Special Provisions", 408),
    (36, "Election Commission", 410),
    (37, "Political Parties", 424),
    (38, "Constitutional Amendments", 436),
    (39, "Official Language", 454),
    (40, "Panchayati Raj and Community Development", 459),
    (41, "Special Provision for Certain Classes", 498),
    (42, "Miscellaneous", 504)
]

boundaries = []
for i in range(len(candidates)):
    ch_num, title, st = candidates[i]
    if i < len(candidates) - 1:
        en = candidates[i+1][2] # page where next chapter starts
    else:
        en = 530
    boundaries.append({
        "chapter_no": ch_num,
        "title": title,
        "start_page": st,
        "end_page": en
    })

print(f"Total chapters: {len(boundaries)}")
for b in boundaries:
    print(f"Ch {b['chapter_no']:2d}: {b['title']:45s} -> Pages {b['start_page']:3d} to {b['end_page']:3d} ({b['end_page'] - b['start_page'] + 1} pages)")

with open("dashboard-src/subjects/polity/chapter_boundaries.json", "w", encoding="utf-8") as f:
    json.dump(boundaries, f, indent=2)
print("Saved chapter_boundaries.json")
