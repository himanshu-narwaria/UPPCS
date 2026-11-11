import json
import re

with open("dashboard-src/subjects/geography/raw_pages.json", encoding="utf-8") as f:
    pages = json.load(f)

# Chapters definition with nominal printed pages
# Section I: CA-9 to CA-416. Offset is approx PDF = CA - 2.
# Section II: CB-01 to CB-288. Offset is approx PDF = CB + 417.

sec1_toc = [
    (1, "General Introduction", 9, 23),
    (2, "Physical Division", 23, 71),
    (3, "States and Union Territories of India", 71, 82),
    (4, "Species/Tribes", 82, 97),
    (5, "Languages", 97, 98),
    (6, "Drainage System", 99, 142),
    (7, "Climate", 142, 158),
    (8, "Natural Disasters", 158, 165),
    (9, "Soils", 165, 179),
    (10, "Natural Vegetation", 179, 187),
    (11, "Irrigation and Canals", 187, 194),
    (12, "Multi-Purpose River Valley Project", 194, 214),
    (13, "Agriculture", 214, 223),
    (14, "Green Revolution", 223, 228),
    (15, "Food Crops", 228, 240),
    (16, "Cash Crops", 240, 246),
    (17, "Oilseed", 246, 249),
    (18, "Pulses", 249, 252),
    (19, "Silk", 252, 253),
    (20, "Plantation Crops", 253, 261),
    (21, "Jhuming Agriculture", 261, 263),
    (22, "Agriculture : Miscellaneous", 263, 281),
    (23, "Animal Husbandry", 281, 284),
    (24, "Mineral Resources", 284, 316),
    (25, "Miscellaneous : Minerals", 316, 328),
    (26, "Electrical Energy", 328, 344),
    (27, "Industry", 344, 364),
    (28, "Research Centres in India", 364, 377),
    (29, "Transport", 377, 406),
    (30, "Tourism", 406, 411),
    (31, "Miscellaneous", 411, 416),
]

sec2_toc = [
    (1, "Universe", 1, 33),
    (2, "Earth", 33, 52),
    (3, "Rocks", 52, 55),
    (4, "Volcano", 55, 60),
    (5, "The Earthquake", 60, 63),
    (6, "The Continents", 63, 67),
    (7, "The World Mountain Ranges", 67, 76),
    (8, "The Plateaus", 76, 78),
    (9, "Valleys", 78, 80),
    (10, "Arid Region / Desert", 81, 86),
    (11, "The Grasslands", 87, 90),
    (12, "Countries and their Borders", 90, 97),
    (13, "Dependent Territory", 97, 99),
    (14, "The Land-locked Countries", 100, 102),
    (15, "Old Names of Countries", 102, 103),
    (16, "International Border Lines", 103, 105),
    (17, "Capital Cities of the World", 105, 113),
    (18, "World Towns", 113, 117),
    (19, "Geographical Sobriquets", 118, 121),
    (20, "Hydrosphere", 121, 125),
    (21, "Important Seas of the World", 125, 129),
    (22, "Ocean Currents", 129, 135),
    (23, "Salinity of the Ocean", 135, 137),
    (24, "High Tide, Low Tide", 137, 139),
    (25, "Oceanic Trenches", 139, 140),
    (26, "Rivers of the World", 141, 147),
    (27, "Towns and Cities along the Banks of Rivers", 148, 152),
    (28, "Landforms by River", 152, 154),
    (29, "The Island", 154, 160),
    (30, "Lakes and Water Falls", 160, 166),
    (31, "Straits", 166, 169),
    (32, "Canals", 169, 171),
    (33, "The Important Dams of the World", 172, 173),
    (34, "The Coral Reefs", 173, 174),
    (35, "The Atmosphere", 174, 179),
    (36, "The Insolation", 179, 182),
    (37, "Cyclone", 182, 185),
    (38, "Humidity", 185, 186),
    (39, "The Atmospheric Pressure", 186, 187),
    (40, "Clouds", 187, 189),
    (41, "Winds", 189, 192),
    (42, "Local Winds", 193, 195),
    (43, "The Forest", 195, 201),
    (44, "World Climate", 201, 212),
    (45, "The Soil", 212, 216),
    (46, "The Major Tribes of the World", 216, 223),
    (47, "The Languages", 223, 225),
    (48, "Economic Geography", 225, 269),
    (49, "Transport", 269, 273),
    (50, "The Ports and Harbours", 273, 275),
    (51, "Mapping", 276, 277),
    (52, "Miscellaneous", 277, 288),
]

all_chapters = []
for n, title, s, e in sec1_toc:
    all_chapters.append({
        "num": n,
        "section": "Indian Geography",
        "title": title,
        "nominal": f"CA {s}-CA {e}",
        "nominal_start": s,
        "nominal_end": e,
        "pdf_est_start": s - 2,
        "pdf_est_end": e - 2
    })

for n, title, s, e in sec2_toc:
    all_chapters.append({
        "num": n + 31,
        "section": "World Geography",
        "title": title,
        "nominal": f"CB {s:02d}-CB {e:02d}",
        "nominal_start": s,
        "nominal_end": e,
        "pdf_est_start": s + 417,
        "pdf_est_end": e + 417
    })

print(f"Total unified chapters: {len(all_chapters)}")

# Now let's check text around each chapter's pdf_est_start to find the exact heading and start page
for ch in all_chapters:
    est = ch["pdf_est_start"]
    # search window: est-3 to est+3
    found_page = None
    target_words = [w.lower() for w in ch["title"].replace(":", " ").replace("/", " ").split() if len(w) > 3]
    for p in range(max(1, est - 3), min(len(pages) + 1, est + 4)):
        ptxt = pages[p - 1]["text"]
        # look for title words in the top 300 characters
        top = ptxt[:400].lower()
        if any(w in top for w in target_words):
            found_page = p
            break
    ch["found_start"] = found_page or est

# Save preliminary chapter ledger
with open("dashboard-src/subjects/geography/chapter_ledger.json", "w", encoding="utf-8") as f:
    json.dump(all_chapters, f, indent=2, ensure_ascii=False)

print("Saved chapter_ledger.json")
for c in all_chapters[:5]:
    print(c["num"], c["section"], c["title"], f"Nominal: {c['nominal']}", f"PDF Est: {c['pdf_est_start']}", f"Found: {c['found_start']}")
print("...")
for c in all_chapters[31:36]:
    print(c["num"], c["section"], c["title"], f"Nominal: {c['nominal']}", f"PDF Est: {c['pdf_est_start']}", f"Found: {c['found_start']}")
