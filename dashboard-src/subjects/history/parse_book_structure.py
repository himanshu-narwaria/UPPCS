import os, re, pypdf

pdf_path = os.path.join("Indian_History_Part_2", "Preview_Indian_History_Part_2_2026_26116_C_E_Book_Merged_1.pdf")
reader = pypdf.PdfReader(pdf_path)
n_pages = len(reader.pages)
print(f"Total pages: {n_pages}")

# Let's extract text for all pages and analyze headings
# In Ghatna Chakra books, chapter headings usually appear right after notes begin, or at the top of a page.
# Let's see what appears on page 9, 17, 32, 48, 71, etc.
sample_pages = [9, 17, 32, 48, 71, 81, 87, 96, 98, 119, 130, 156, 170, 183, 195, 204]
for p in sample_pages:
    txt = reader.pages[p-1].extract_text() or ""
    lines = [l.strip() for l in txt.split('\n') if l.strip()]
    print(f"\n--- Page {p} (first 6 lines) ---")
    for l in lines[:6]:
        print("  ", l)
