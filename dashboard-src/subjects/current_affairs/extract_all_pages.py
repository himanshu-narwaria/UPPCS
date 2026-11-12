from pypdf import PdfReader
import json
import time

t0 = time.time()
reader = PdfReader("Drishti-current affairs/Drishti (2) English 2026 (2615-M).pdf")
print(f"Total pages: {len(reader.pages)}")

pages_data = []
empty_pages = []

for i, page in enumerate(reader.pages):
    txt = page.extract_text() or ""
    pages_data.append({
        "page_num": i + 1,
        "char_count": len(txt),
        "text": txt
    })
    if len(txt.strip()) < 50:
        empty_pages.append(i + 1)

print(f"Extracted {len(pages_data)} pages in {time.time() - t0:.2f}s")
print(f"Empty or very short pages (<50 chars): {empty_pages}")

total_chars = sum(p["char_count"] for p in pages_data)
print(f"Total extracted characters: {total_chars:,}")

# Save raw extracted pages to json
with open("dashboard-src/subjects/current_affairs/raw_pages.json", "w", encoding="utf-8") as f:
    json.dump(pages_data, f, ensure_ascii=False, indent=2)

print("Saved to dashboard-src/subjects/current_affairs/raw_pages.json")
