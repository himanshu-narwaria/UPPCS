import re

with open('Environment_2025/environment-2025-uppsc-quick-notes.html', 'r', encoding='utf-8') as f:
    text = f.read()

views = re.findall(r'<section class="view[^"]*" id="([^"]+)"', text)
print('Views found:', views)

c1_match = re.search(r'(<section class="view ch" id="c1".*?)(?=<section class="view ch" id="c2"|</main>)', text, re.S)
if c1_match:
    print('--- c1 structure (first 1500 chars) ---')
    print(c1_match.group(1)[:1500])
    print('--- c1 structure (last 500 chars) ---')
    print(c1_match.group(1)[-500:])
