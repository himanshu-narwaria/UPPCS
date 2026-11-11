import re

with open('Environment_2025/environment-2025-uppsc-quick-notes.html', 'r', encoding='utf-8') as f:
    text = f.read()

# Let's inspect everything before <main>
main_start = text.find('<main')
print('--- Before <main> ---')
print(text[:main_start])

# Let's inspect #home
home_match = re.search(r'(<section class="view" id="home".*?</section>)', text, re.S)
if home_match:
    print('--- #home (first 800 chars) ---')
    print(home_match.group(1)[:800])
    print('--- #home (last 600 chars) ---')
    print(home_match.group(1)[-600:])

# Let's inspect #repeated
rep_match = re.search(r'(<section class="view" id="repeated".*?</section>)', text, re.S)
if rep_match:
    print('--- #repeated (first 800 chars) ---')
    print(rep_match.group(1)[:800])
    print('--- #repeated (sample row) ---')
    sample_li = re.search(r'<li><details>.*?</details></li>', rep_match.group(1), re.S)
    if sample_li:
        print(sample_li.group(0))

# Let's inspect views after chapters
for vid in ['upx', 'newx', 'results']:
    v_match = re.search(rf'(<section class="view[^"]*" id="{vid}".*?</section>)', text, re.S)
    if v_match:
        print(f'--- #{vid} ---')
        print(v_match.group(1)[:400])

# Let's inspect after </main>
main_end = text.find('</main>')
print('--- After </main> ---')
print(text[main_end:])
