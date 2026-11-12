import json
import re

with open("dashboard-src/subjects/science/raw_pages.json", encoding="utf-8") as f:
    pages = json.load(f)

# The 65 canonical chapters
chapter_defs = [
    # Physics
    (1, "Physics", "Measurement/Unit", 9),
    (2, "Physics", "Measuring Devices and Scales", 19),
    (3, "Physics", "Mechanics", 28),
    (4, "Physics", "Motion under Gravity", 38),
    (5, "Physics", "Physical Properties of Matter", 47),
    (6, "Physics", "Optics", 58),
    (7, "Physics", "Heat and Thermodynamics", 83),
    (8, "Physics", "Wave Motion", 100),
    (9, "Physics", "Sound", 108),
    (10, "Physics", "Electric Current", 120),
    (11, "Physics", "Conductivity", 139),
    (12, "Physics", "Nuclear Physics", 143),
    (13, "Physics", "Computer and Information Technology", 162),
    (14, "Physics", "Space", 223),
    (15, "Physics", "Defence Technology", 268),
    (16, "Physics", "Scientists & Inventions", 295),
    (17, "Physics", "Physics : Miscellaneous", 305),

    # Chemistry
    (18, "Chemistry", "Atomic Structure", 324),
    (19, "Chemistry", "Physical and Chemical Changes, Solution", 332),
    (20, "Chemistry", "Inorganic Chemistry", 341),
    (21, "Chemistry", "Metals, Minerals, Ores: Properties, Uses", 346),
    (22, "Chemistry", "Alloys", 358),
    (23, "Chemistry", "Carbon and its various forms", 363),
    (24, "Chemistry", "Hydrogen and its compounds", 370),
    (25, "Chemistry", "Sulfur, Nitrogen, Halogen, Inert Gases", 375),
    (26, "Chemistry", "Acid, Base and Salt", 381),
    (27, "Chemistry", "Hydrocarbons", 391),
    (28, "Chemistry", "Alcohol", 395),
    (29, "Chemistry", "Polymer", 398),
    (30, "Chemistry", "Organic Acid", 403),
    (31, "Chemistry", "Explosive Substances", 410),
    (32, "Chemistry", "Fuel", 412),
    (33, "Chemistry", "Food Preservation, Nutrition, Medicine, etc.", 424),
    (34, "Chemistry", "Detergents and Soap", 430),
    (35, "Chemistry", "Fertilizers", 432),
    (36, "Chemistry", "Chemistry : Miscellaneous", 436),

    # Biology
    (37, "Biology", "Subdivisions of Biology", 458),
    (38, "Biology", "Evolution of Life", 463),
    (39, "Biology", "Taxonomy", 470),
    (40, "Biology", "Cell", 503),
    (41, "Biology", "Heredity", 509),
    (42, "Biology", "Biofertilizers", 516),
    (43, "Biology", "Skeletal and Muscle System", 521),
    (44, "Biology", "Digestive System", 528),
    (45, "Biology", "Vitamins and Nutrition", 538),
    (46, "Biology", "Respiratory System", 563),
    (47, "Biology", "Circulatory System", 567),
    (48, "Biology", "Excretory System", 585),
    (49, "Biology", "Nervous System", 588),
    (50, "Biology", "Endocrine System", 592),
    (51, "Biology", "Reproduction and Embryo Development", 605),
    (52, "Biology", "Photosynthesis", 608),
    (53, "Biology", "Plant Nutrition", 615),
    (54, "Biology", "Plant Hormones", 621),
    (55, "Biology", "Plant Reproduction", 624),
    (56, "Biology", "Plants : Economic Importance", 631),
    (57, "Biology", "Viral Diseases", 643),
    (58, "Biology", "Bacterial Diseases", 657),
    (59, "Biology", "Fungal Diseases", 667),
    (60, "Biology", "Other Parasitic Diseases", 669),
    (61, "Biology", "Genetic Disorders", 675),
    (62, "Biology", "Deficiency, Non-Contagious and Other Diseases", 680),
    (63, "Biology", "Main Plant Diseases", 701),
    (64, "Biology", "Genetic Engineering and Biotechnology", 705),
    (65, "Biology", "Biology : Miscellaneous", 727),
]

# Build accurate start and end pages
accurate = []
for i, (num, part, title, est_p) in enumerate(chapter_defs):
    # End page is start page of next chapter, or 760 for the last chapter
    if i < len(chapter_defs) - 1:
        next_start = chapter_defs[i + 1][3]
        end_p = next_start # chapters often share boundary page
    else:
        end_p = 760
    
    accurate.append({
        "num": num,
        "part": part,
        "title": title,
        "start_page": est_p,
        "end_page": end_p
    })

print(f"Total accurately bounded chapters: {len(accurate)}")
for c in accurate[:5]:
    print(c)
print("...")
for c in accurate[-5:]:
    print(c)

with open("dashboard-src/subjects/science/chapter_boundaries.json", "w", encoding="utf-8") as f:
    json.dump(accurate, f, indent=2, ensure_ascii=False)
