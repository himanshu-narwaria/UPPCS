"""Extract the book in visual reading order, retaining source-page provenance.

The old pypdf stream order repeated headings before the left-hand questions on
several chapter boundaries. PDFium's bounded extraction reads the left column,
then the right. The full text stream is retained for an independent token audit.
"""
import hashlib
import json
from pathlib import Path
import re
import pypdfium2
from pypdf import PdfReader

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
PDF = ROOT / "Indian_Polity_and_Governance" / "Preview_Indian_Polity_and_Governance_Part_4_2026_26118_C_E_Book.pdf"


def tidy(text):
    return re.sub(r"\n{3,}", "\n\n", text.replace("\r\n", "\n").replace("\r", "\n")).strip()


def main():
    doc = pypdfium2.PdfDocument(str(PDF))
    reader = PdfReader(PDF)
    pages = []
    for index in range(len(doc)):
        page = doc[index]
        text = page.get_textpage()
        width, height = page.get_size()
        if index < 6:
            columns = [tidy(text.get_text_range())]
        else:
            columns = [tidy(text.get_text_bounded(left=30, bottom=96, right=width / 2, top=height - 58)),
                       tidy(text.get_text_bounded(left=width / 2, bottom=96, right=width - 25, top=height - 58))]
        pages.append({"page_index": index, "page_num": index + 1,
                      "text": "\n".join(columns), "columns": columns,
                      "stream_text": reader.pages[index].extract_text() or "",
                      "extraction": "PDFium bounded columns, left then right; file-page numbers"})
    (HERE / "raw_pages.json").write_text(json.dumps(pages, ensure_ascii=False), encoding="utf-8")
    (HERE / "source_identity.json").write_text(json.dumps({
        "pdf": PDF.name, "sha256": hashlib.sha256(PDF.read_bytes()).hexdigest(),
        "pages": len(doc), "extracted_on": "2026-11-12", "method": "pypdf independent stream + PDFium column order",
        "visual_samples": [7, 11, 41, 69, 105, 331, 367, 436, 459]}, indent=2), encoding="utf-8")
    print(f"Extracted {len(pages)} actual PDF pages in column order; kept independent stream text.")


if __name__ == "__main__":
    main()
