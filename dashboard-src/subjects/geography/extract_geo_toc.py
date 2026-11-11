import os, pypdf

pdf_path = os.path.join("General_Geography_Part_3", "Preview_General_Geography_Part_3_2026_26117_C_E_Book_combined.pdf")
reader = pypdf.PdfReader(pdf_path)

print("=== PDF Page 3 text ===")
print(reader.pages[2].extract_text())

# Check page 4, 5, 6
for p in [3, 4, 5]:
    txt = reader.pages[p].extract_text()
    if "index" in txt.lower() or "world geography" in txt.lower():
        print(f"\n=== PDF Page {p+1} text ===")
        print(txt)
