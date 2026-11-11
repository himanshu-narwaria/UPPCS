import os, re, pypdf

pdf_path = os.path.join("Indian_History_Part_2", "Preview_Indian_History_Part_2_2026_26116_C_E_Book_Merged_1.pdf")
reader = pypdf.PdfReader(pdf_path)

# Let's inspect pages around B9 (page index 8 or 9)
for p in [7, 8, 9, 15, 16, 17, 31, 32, 33, 47, 48, 49]:
    txt = reader.pages[p].extract_text()
    first_line = txt.split('\n')[0] if txt else ''
    last_line = txt.split('\n')[-1] if txt else ''
    print(f"PDF page {p+1}: first_line='{first_line[:50]}' | last_line='{last_line[:50]}'")
