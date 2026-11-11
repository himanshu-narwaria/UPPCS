import os, pypdf

pdf_path = os.path.join("Indian_History_Part_2", "Preview_Indian_History_Part_2_2026_26116_C_E_Book_Merged_1.pdf")
reader = pypdf.PdfReader(pdf_path)

for p in [203, 204, 347, 348, 758, 759]:
    txt = reader.pages[p].extract_text()
    first_line = txt.split('\n')[0] if txt else ''
    print(f"PDF page {p+1}: first_line='{first_line[:50]}'")
