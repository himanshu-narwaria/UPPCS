import json
import re
import html
import sys

# Load chapters from accurate_chapter_ranges.json
with open("dashboard-src/subjects/geography/accurate_chapter_ranges.json", encoding="utf-8") as f:
    ranges = json.load(f)

# Update the titles for disambiguation
for c in ranges:
    if c["num"] == 29:
        c["title"] = "Transport in India"
    elif c["num"] == 31:
        c["title"] = "Indian Geography : Miscellaneous"
    elif c["num"] == 80:
        c["title"] = "World Transport"
    elif c["num"] == 83:
        c["title"] = "World Geography : Miscellaneous"
    elif c["num"] == 5:
        c["title"] = "Languages of India"
    elif c["num"] == 78:
        c["title"] = "Major Languages of the World"

chapters = {c["num"]: {"title": c["title"], "asked": 0} for c in ranges}

def norm(t):
    t = re.sub(r"\band\b", " ", t.lower().replace("&", " "))
    return re.sub(r"[^a-z0-9]", "", t)

def chapter_hours(chapters, plan, label="test"):
    order = list(chapters)
    index = {norm(c["title"]): n for n, c in chapters.items()}
    out = {n: [] for n in order}
    for h, title in plan["phases"].get("Learn", []):
        base = re.sub(r" · part \d+ of \d+$", "", title)
        covered = []
        for part in base.split(" + "):
            if " to " in part and norm(part) not in index:
                a, b = (x.strip() for x in part.split(" to ", 1))
                if norm(a) not in index:
                    sys.exit(f"Hour {h} start chapter unknown: {a!r}")
                if norm(b) not in index:
                    sys.exit(f"Hour {h} end chapter unknown: {b!r}")
                i, j = order.index(index[norm(a)]), order.index(index[norm(b)])
                covered += order[i:j + 1]
            elif norm(part) in index:
                covered.append(index[norm(part)])
            else:
                sys.exit(f"Hour {h} names a chapter I can't match: {part!r}")
        for n in covered:
            out[n].append(h)
    missing = [chapters[n]["title"] for n in order if not out[n]]
    if missing:
        sys.exit(f"Missing Learn hours for: {missing}")
    print(f"SUCCESS! All {len(order)} chapters covered across {len(plan['phases']['Learn'])} Learn hours.")
    return out

learn_hours = [
    # Indian Geography (Hours 1-24)
    (1, "General Introduction", [1]),
    (2, "Physical Division · part 1 of 2", [2]),
    (3, "Physical Division · part 2 of 2", [2]),
    (4, "States and Union Territories of India + Species/Tribes", [3, 4]),
    (5, "Languages of India", [5]),
    (6, "Drainage System · part 1 of 2", [6]),
    (7, "Drainage System · part 2 of 2", [6]),
    (8, "Climate + Natural Disasters", [7, 8]),
    (9, "Soils + Natural Vegetation", [9, 10]),
    (10, "Irrigation and Canals + Multi-Purpose River Valley Project", [11, 12]),
    (11, "Agriculture + Green Revolution", [13, 14]),
    (12, "Food Crops", [15]),
    (13, "Cash Crops + Oilseed", [16, 17]),
    (14, "Pulses to Silk", [18, 19]),
    (15, "Plantation Crops + Jhuming Agriculture", [20, 21]),
    (16, "Agriculture : Miscellaneous + Animal Husbandry", [22, 23]),
    (17, "Mineral Resources", [24]),
    (18, "Miscellaneous : Minerals + Electrical Energy", [25, 26]),
    (19, "Industry", [27]),
    (20, "Research Centres in India", [28]),
    (21, "Transport in India · part 1 of 2", [29]),
    (22, "Transport in India · part 2 of 2", [29]),
    (23, "Tourism", [30]),
    (24, "Indian Geography : Miscellaneous", [31]),

    # World Geography (Hours 25-48)
    (25, "Universe · part 1 of 2", [32]),
    (26, "Universe · part 2 of 2", [32]),
    (27, "Earth", [33]),
    (28, "Rocks to Volcano", [34, 35]),
    (29, "The Earthquake to The Continents", [36, 37]),
    (30, "The World Mountain Ranges", [38]),
    (31, "The Plateaus to Arid Region / Desert", [39, 40, 41]),
    (32, "The Grasslands to Countries and their Borders", [42, 43]),
    (33, "Dependent Territory to International Border Lines", [44, 45, 46, 47]),
    (34, "Capital Cities of the World to Geographical Sobriquets", [48, 49, 50]),
    (35, "Hydrosphere to Ocean Currents", [51, 52, 53]),
    (36, "Salinity of the Ocean to Oceanic Trenches", [54, 55, 56]),
    (37, "Rivers of the World to Landforms by River", [57, 58, 59]),
    (38, "The Island to Lakes and Water Falls", [60, 61]),
    (39, "Straits to The Coral Reefs", [62, 63, 64, 65]),
    (40, "The Atmosphere to Cyclone", [66, 67, 68]),
    (41, "Humidity to Winds", [69, 70, 71, 72]),
    (42, "Local Winds + The Forest", [73, 74]),
    (43, "World Climate to The Soil", [75, 76]),
    (44, "The Major Tribes of the World + Major Languages of the World", [77, 78]),
    (45, "Economic Geography · part 1 of 2", [79]),
    (46, "Economic Geography · part 2 of 2", [79]),
    (47, "World Transport to The Ports and Harbours", [80, 81]),
    (48, "Mapping to World Geography : Miscellaneous", [82, 83]),
]

print(f"Total Learn hours: {len(learn_hours)}")
plan = {
    "phases": {
        "Learn": [(h, t) for h, t, _ in learn_hours]
    }
}

res = chapter_hours(chapters, plan)
