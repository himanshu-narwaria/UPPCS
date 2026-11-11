import json
import re

with open("dashboard-src/subjects/geography/raw_pages.json", encoding="utf-8") as f:
    pages = json.load(f)

print(f"Loaded {len(pages)} pages.")

# Let's inspect headers on pages 1 to 15
print("=== First 15 pages headers ===")
for p in pages[:15]:
    lines = [l.strip() for l in p["text"].split("\n") if l.strip()]
    header = lines[0] if lines else "(empty)"
    print(f"PDF P.{p['pdf_page']}: {header[:60]}")

# Let's find where Section II starts
print("\n=== Finding Section II / World Geography / CB-01 ===")
for p in pages:
    lines = [l.strip() for l in p["text"].split("\n") if l.strip()]
    header = " | ".join(lines[:3]) if lines else ""
    if "World Geography" in header or "CB–01" in header or "CB-01" in header or "CB 01" in header or "CB–1" in header:
        print(f"PDF P.{p['pdf_page']}: {header[:100]}")
