import json
import os
from build_polity_data import load_pages, extract_chapter_texts, CHAPTER_SPECS

pages = load_pages()
ch_texts = extract_chapter_texts(pages)

out_dir = os.path.join("dashboard-src", "subjects", "polity", "chapter_texts")
os.makedirs(out_dir, exist_ok=True)

for ch_num, title, st_page, _ in CHAPTER_SPECS:
    txt = ch_texts[ch_num]
    out_file = os.path.join(out_dir, f"ch{ch_num}.txt")
    with open(out_file, "w", encoding="utf-8") as f:
        f.write(txt)

print(f"Dumped all 42 chapter texts to {out_dir}")
