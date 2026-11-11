import json
import re

with open("dashboard-src/subjects/geography/raw_pages.json", encoding="utf-8") as f:
    pages = json.load(f)

with open("dashboard-src/subjects/geography/chapter_ledger.json", encoding="utf-8") as f:
    chapters = json.load(f)

# Build a lookup from printed (e.g. CA-9 or CB-1) to PDF page
printed_to_pdf = {}
for p in pages:
    txt = p["text"]
    m = re.search(r'\b(CA|CB)[\s–-]+(\d+)', txt[:150], re.IGNORECASE)
    if m:
        key = f"{m.group(1).upper()}-{int(m.group(2))}"
        if key not in printed_to_pdf:
            printed_to_pdf[key] = p["pdf_page"]

print(f"Mapped {len(printed_to_pdf)} unique printed page numbers.")

# Now verify each chapter start
updated_chapters = []
for idx, ch in enumerate(chapters):
    sec = "CA" if ch["section"] == "Indian Geography" else "CB"
    nom_start = ch["nominal_start"]
    nom_end = ch["nominal_end"]
    
    # get pdf page for nom_start
    start_key = f"{sec}-{nom_start}"
    pdf_start = printed_to_pdf.get(start_key, ch["pdf_est_start"])
    
    # get pdf page for nom_end
    end_key = f"{sec}-{nom_end}"
    pdf_end = printed_to_pdf.get(end_key, ch["pdf_est_end"])
    
    # Check if heading appears around pdf_start
    ch["pdf_start"] = pdf_start
    ch["pdf_end"] = pdf_end
    
    # sample text on pdf_start
    sample = pages[pdf_start - 1]["text"][:250].replace("\n", " ")
    ch["first_page_sample"] = sample
    updated_chapters.append(ch)

# Fix chapter ranges so that chapter N's end page is chapter N+1's start page (or last page)
for i in range(len(updated_chapters)):
    cur = updated_chapters[i]
    if i < len(updated_chapters) - 1:
        nxt = updated_chapters[i + 1]
        if cur["section"] == nxt["section"]:
            cur["calc_end_page"] = nxt["pdf_start"] - 1 if nxt["pdf_start"] > cur["pdf_start"] else cur["pdf_start"]
        else:
            # cur is last chapter of Section I (Indian Geography)
            # CB-1 starts at PDF 418, so Section I ends at PDF 417
            cur["calc_end_page"] = 417
    else:
        # last chapter of Section II
        cur["calc_end_page"] = 708

with open("dashboard-src/subjects/geography/accurate_chapter_ranges.json", "w", encoding="utf-8") as f:
    json.dump(updated_chapters, f, indent=2, ensure_ascii=False)

print("Saved accurate_chapter_ranges.json")
for c in updated_chapters[:10]:
    print(f"Ch {c['num']:2d}: {c['title'][:30]:30s} | Nom: {c['nominal']:12s} | PDF: {c['pdf_start']:3d} - {c['calc_end_page']:3d}")
print("...")
for c in updated_chapters[30:40]:
    print(f"Ch {c['num']:2d}: {c['title'][:30]:30s} | Nom: {c['nominal']:12s} | PDF: {c['pdf_start']:3d} - {c['calc_end_page']:3d}")
print("...")
for c in updated_chapters[-5:]:
    print(f"Ch {c['num']:2d}: {c['title'][:30]:30s} | Nom: {c['nominal']:12s} | PDF: {c['pdf_start']:3d} - {c['calc_end_page']:3d}")
