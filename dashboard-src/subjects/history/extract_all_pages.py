import os, json, time, pypdf

start = time.time()
pdf_path = os.path.join("Indian_History_Part_2", "Preview_Indian_History_Part_2_2026_26116_C_E_Book_Merged_1.pdf")
reader = pypdf.PdfReader(pdf_path)
n_pages = len(reader.pages)

pages_data = []
for i in range(n_pages):
    txt = reader.pages[i].extract_text() or ""
    pages_data.append({
        "page_index": i,
        "pdf_page": i + 1,
        "text": txt
    })

out_path = os.path.join("dashboard-src", "subjects", "history", "raw_pages.json")
with open(out_path, "w", encoding="utf-8") as f:
    json.dump(pages_data, f, ensure_ascii=False)

print(f"Extracted all {n_pages} pages in {time.time() - start:.2f}s to {out_path}")
