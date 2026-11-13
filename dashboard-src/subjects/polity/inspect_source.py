"""Read-only diagnostics for the polity PDF extraction and old practice bank."""
import json
import re
from pathlib import Path
from build_polity_data import CHAPTER_SPECS, extract_chapter_texts

HERE = Path(__file__).resolve().parent
pages = json.loads((HERE / "raw_pages.json").read_text(encoding="utf-8"))
chapters = extract_chapter_texts(pages)
for n, title, start, _ in CHAPTER_SPECS:
    text = chapters[n]
    first = re.search(r"(?m)^\s*1\.\s+", text)
    intro = text[:first.start()] if first else text
    print(f"\n{'=' * 12} {n}. {title} | PDF {start} | {len(intro)} intro characters {'=' * 12}\n{intro}")
