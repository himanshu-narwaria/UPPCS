import os
import pypdf

pdf_path = os.path.join("Indian_History_Part_2", "Preview_Indian_History_Part_2_2026_26116_C_E_Book_Merged_1.pdf")
reader = pypdf.PdfReader(pdf_path)
n_pages = len(reader.pages)
print(f"Total pages: {n_pages}")

# Let's inspect first 15 pages to find the Index / Table of Contents
for i in range(min(15, n_pages)):
    txt = reader.pages[i].extract_text() or ""
    lines = [l.strip() for l in txt.split("\n") if l.strip()]
    header = " | ".join(lines[:3]) if lines else "(empty)"
    print(f"Page {i+1}: lines={len(lines)}, header: {header[:120]}")
    if any(k in txt.lower() for k in ["contents", "index", "ancient", "medieval", "modern"]):
        print(f"--- Page {i+1} might be TOC ---")
        for line in lines[:25]:
            print("  ", line)
