import json
import re

with open("dashboard-src/subjects/geography/raw_pages.json", encoding="utf-8") as f:
    pages = json.load(f)

# 20 specific facts across Indian and World Geography to spot check against the PDF text
check_items = [
    # 1. Ch 1: Latitudinal / Longitudinal extent of India
    (1, "8°4", "Indian mainland southern extent 8°4' N"),
    # 2. Ch 1: Tropic of cancer passing through states
    (1, "Tropic of Cancer", "Tropic of Cancer passing through Indian states"),
    # 3. Ch 1: Standard Meridian 82°30' E
    (1, "82°30", "Indian Standard Meridian 82°30' E"),
    # 4. Ch 2: Oldest mountain range Aravalli
    (2, "Aravalli", "Aravalli range antiquity"),
    # 5. Ch 2: Highest peak K2 / Godwin Austen
    (2, "Godwin Austen", "K2 / Godwin Austen highest peak"),
    # 6. Ch 2: Nathu La pass in Sikkim
    (2, "Nathu La", "Nathu La pass location"),
    # 7. Ch 6: Longest river Ganga 2525 km
    (6, "2525", "Ganga river length 2525 km"),
    # 8. Ch 6: Origin of Bhagirathi from Gaumukh
    (6, "Gaumukh", "Gaumukh / Gangotri source"),
    # 9. Ch 9: Regur / Black soil for cotton
    (9, "Regur", "Regur soil characteristic"),
    # 10. Ch 11: Sharda Canal in UP
    (11, "Sharda", "Sharda canal irrigation in UP"),
    # 11. Ch 12: Bhakra Nangal Dam on Sutlej
    (12, "Sutlej", "Bhakra Nangal dam on Sutlej"),
    # 12. Ch 24: Kolar and Hutti gold mines
    (24, "Kolar", "Kolar gold fields"),
    # 13. Ch 24: Jharia coalfield in Jharkhand
    (24, "Jharia", "Jharia coal field"),
    # 14. Ch 26: Narora nuclear power plant in UP (Bulandshahr)
    (26, "Narora", "Narora atomic power station in UP"),
    # 15. Ch 32: Big Bang Theory Georges Lemaitre
    (32, "Lemaitre", "Big Bang theory propounded by Lemaitre"),
    # 16. Ch 32: Chandrasekhar Limit 1.44 solar mass
    (32, "1.44", "Chandrasekhar limit 1.44 solar mass"),
    # 17. Ch 34: Metamorphic form of Limestone is Marble
    (34, "Marble", "Limestone metamorphism to marble"),
    # 18. Ch 45: Landlocked countries (e.g. Bolivia, Paraguay, Laos)
    (45, "Bolivia", "Landlocked status of Bolivia"),
    # 19. Ch 53: Gulf stream warm ocean current
    (53, "Gulf Stream", "Gulf Stream warm current"),
    # 20. Ch 73: Chinook local wind (Snow-eater)
    (73, "Chinook", "Chinook warm local wind in Rockies"),
]

with open("dashboard-src/subjects/geography/accurate_chapter_ranges.json", encoding="utf-8") as f:
    ranges = json.load(f)

print("=== SPOT CHECKING 20 GEOGRAPHY FACTS AGAINST PDF TEXT ===")
passed = 0
for ch_num, term, desc in check_items:
    r_entry = ranges[ch_num - 1]
    p_start = r_entry["pdf_start"]
    p_end = r_entry["calc_end_page"]
    
    ch_text = "\n".join(pages[p-1]["text"] for p in range(p_start, p_end + 1))
    found = term.lower() in ch_text.lower()
    if found:
        passed += 1
        print(f" [PASS] Ch {ch_num:2d} ({desc}): Found '{term}' in pp. {p_start}–{p_end}")
    else:
        found_any = any(term.lower() in p["text"].lower() for p in pages)
        print(f" [WARN] Ch {ch_num:2d} ({desc}): Not in chapter pp. {p_start}–{p_end}, found elsewhere={found_any}")

print(f"\nTotal spot-checks passed: {passed}/{len(check_items)}")
assert passed == 20, f"Expected 20/20, got {passed}"
print("ALL 20 SPOT-CHECKS 100% CONFIRMED IN EXACT CHAPTER PAGES!")
