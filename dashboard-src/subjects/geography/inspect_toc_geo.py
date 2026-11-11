import os, pypdf

pdf_path = os.path.join("General_Geography_Part_3", "Preview_General_Geography_Part_3_2026_26117_C_E_Book_combined.pdf")
reader = pypdf.PdfReader(pdf_path)

for p in range(1, 8):
    print(f"================ PDF PAGE {p+1} ================")
    print(reader.pages[p].extract_text())
