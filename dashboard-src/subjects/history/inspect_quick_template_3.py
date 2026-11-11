import re

with open('Environment_2025/environment-2025-uppsc-quick-notes.html', 'r', encoding='utf-8') as f:
    text = f.read()

# Inspect sidebar
side_m = re.search(r'(<nav class="side".*?</nav>)', text, re.S)
if side_m:
    print('--- Sidebar (first 500 chars) ---')
    print(side_m.group(1)[:500])
    print('--- Sidebar (last 300 chars) ---')
    print(side_m.group(1)[-300:])

# Inspect #home
home_m = re.search(r'(<section class="view" id="home".*?</section>)', text, re.S)
if home_m:
    print('--- Home (first 500 chars) ---')
    print(home_m.group(1)[:500])
    print('--- Home (last 500 chars) ---')
    print(home_m.group(1)[-500:])

# Inspect c1 topics
c1_m = re.search(r'<section class="view ch" id="c1".*?</section>', text, re.S)
if c1_m:
    articles = re.findall(r'<article class="topic".*?</article>', c1_m.group(0), re.S)
    print(f'c1 has {len(articles)} topics')
    if articles:
        print('--- Sample Topic 1 ---')
        print(articles[0])
        print('--- Sample Topic 2 ---')
        print(articles[1])
