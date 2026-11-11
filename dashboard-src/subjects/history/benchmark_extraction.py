import time, os, pypdf

start = time.time()
pdf_path = os.path.join("Indian_History_Part_2", "Preview_Indian_History_Part_2_2026_26116_C_E_Book_Merged_1.pdf")
reader = pypdf.PdfReader(pdf_path)
n_pages = len(reader.pages)
print(f"Reader loaded in {time.time() - start:.2f}s, pages: {n_pages}")

# Test extracting 50 pages
t0 = time.time()
total_chars = 0
for i in range(50):
    txt = reader.pages[i].extract_text() or ""
    total_chars += len(txt)
t1 = time.time()
print(f"Extracted 50 pages in {t1 - t0:.2f}s, total chars: {total_chars}")
