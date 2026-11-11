import os, re, pypdf

pdf_path = os.path.join("Indian_History_Part_2", "Preview_Indian_History_Part_2_2026_26116_C_E_Book_Merged_1.pdf")
reader = pypdf.PdfReader(pdf_path)

# Let's read page 3 (TOC) carefully and parse the chapters listed
toc_text = reader.pages[2].extract_text()
print("=== TOC TEXT ===")
print(toc_text)
