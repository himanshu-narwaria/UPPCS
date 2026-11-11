import os, pypdf

pdf_path = os.path.join("General_Geography_Part_3", "Preview_General_Geography_Part_3_2026_26117_C_E_Book_combined.pdf")
reader = pypdf.PdfReader(pdf_path)
n_pages = len(reader.pages)
print(f"Total pages: {n_pages}")

for i in range(min(12, n_pages)):
    txt = reader.pages[i].extract_text() or ""
    lines = [l.strip() for l in txt.split("\n") if l.strip()]
    header = " | ".join(lines[:3]) if lines else "(empty)"
    print(f"Page {i+1}: lines={len(lines)}, header: {header[:120]}")
    if any(k in txt.lower() for k in ["contents", "index", "geography", "universe", "solar"]):
        print(f"--- Page {i+1} sample lines ---")
        for line in lines[:20]:
            print("  ", line)
