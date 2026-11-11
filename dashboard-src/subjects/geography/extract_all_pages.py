import os
import json
import time
import pypdf

PDF_PATH = os.path.join("General_Geography_Part_3", "Preview_General_Geography_Part_3_2026_26117_C_E_Book_combined.pdf")
OUT_PATH = os.path.join("dashboard-src", "subjects", "geography", "raw_pages.json")

def main():
    t0 = time.time()
    print(f"Opening {PDF_PATH}...")
    reader = pypdf.PdfReader(PDF_PATH)
    total = len(reader.pages)
    print(f"Total pages: {total}")
    
    pages = []
    for idx, page in enumerate(reader.pages):
        txt = page.extract_text() or ""
        pages.append({
            "pdf_page": idx + 1,
            "text": txt
        })
        if (idx + 1) % 100 == 0 or idx + 1 == total:
            print(f"Extracted {idx + 1}/{total} pages ({time.time() - t0:.1f}s)...")
            
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(pages, f, ensure_ascii=False)
        
    print(f"Saved {len(pages)} pages to {OUT_PATH} in {time.time() - t0:.1f}s.")

if __name__ == "__main__":
    main()
