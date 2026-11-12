import re

with open("Economy 2024/economy-uppsc-full-notes.html", "r", encoding="utf-8") as f:
    fc = f.read()

style_m = re.search(r'<style>(.*?)</style>', fc, re.S)
if style_m:
    style = style_m.group(1)
    fonts = re.findall(r'(@font-face\s*\{.*?\})', style, re.S)
    print(f"Extracted {len(fonts)} @font-face blocks.")
    total_font_len = sum(len(f) for f in fonts)
    print(f"Total fonts length: {total_font_len:,} chars")
    
    # Save the fonts to a dedicated file
    with open("dashboard-src/subjects/economy/fonts_embedded.css", "w", encoding="utf-8") as out_f:
        out_f.write("\n".join(fonts))
    print("Saved fonts to dashboard-src/subjects/economy/fonts_embedded.css")
