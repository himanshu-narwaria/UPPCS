import os, pypdf

pdf_path = os.path.join("Indian_History_Part_2", "Preview_Indian_History_Part_2_2026_26116_C_E_Book_Merged_1.pdf")
reader = pypdf.PdfReader(pdf_path)

for p in range(2, 8):
    print(f"================ PAGE {p+1} ================")
    print(reader.pages[p].extract_text())
