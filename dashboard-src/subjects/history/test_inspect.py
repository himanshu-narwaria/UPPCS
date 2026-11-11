import re

with open('Environment_2025/environment-2025-uppsc-quick-notes.html', 'r', encoding='utf-8') as f:
    text = f.read()

m = re.search(r'<section class="view"[^>]*id="results".*?</section>', text, re.S)
if m:
    print(m.group(0))
