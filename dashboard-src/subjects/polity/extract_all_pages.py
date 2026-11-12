import pypdf
import json
import time
import os

pdf_path = os.path.join("Indian_Polity_and_Governance", "Preview_Indian_Polity_and_Governance_Part_4_2026_26118_C_E_Book.pdf")
out_path = os.path.join("dashboard-src", "subjects", "polity", "raw_pages.json")

print(f"Reading {pdf_path}...")
t0 = time.time()
reader = pypdf.PdfReader(pdf_path)
total = len(reader.pages)
print(f"Total pages to extract: {total}")

pages = []
for idx, page in enumerate(reader.pages):
    txt = page.extract_text() or ""
    pages.append({
        "page_index": idx,
        "page_num": idx + 1,
        "text": txt
    })
    if (idx + 1) % 100 == 0 or (idx + 1) == total:
        print(f"Extracted {idx + 1}/{total} pages ({(idx + 1)/total*100:.1f}%) in {time.time() - t0:.1f}s")

with open(out_path, "w", encoding="utf-8") as f:
    json.dump(pages, f, ensure_ascii=False)

print(f"Successfully saved {out_path} ({os.path.getsize(out_path):,} bytes) in {time.time() - t0:.1f}s")
