import re

with open('Indian_History_Part_2/history-uppsc-full-notes.html', 'r', encoding='utf-8') as f:
    full = f.read()

m = re.search(r'<section\s+class="view"\s+id="repeated"[^>]*>(.*?)</section>', full, re.S)
if m:
    content = m.group(1)
    # Check articles or items
    articles = re.findall(r'<article\b[^>]*>(.*?)</article>', content, re.S)
    print("Full notes repeated articles count:", len(articles))
    lis = re.findall(r'<li>', content)
    print("Full notes repeated <li> inside #repeated:", len(lis))
    print("Full notes repeated sample snippet:\n", content[:500])

with open('Indian_History_Part_2/history-uppsc-quick-notes.html', 'r', encoding='utf-8') as f:
    quick = f.read()

mq = re.search(r'<section\s+class="view"\s+id="repeated"[^>]*>(.*?)</section>', quick, re.S)
if mq:
    content_q = mq.group(1)
    articles_q = re.findall(r'<article\b[^>]*>(.*?)</article>', content_q, re.S)
    print("Quick notes repeated articles count:", len(articles_q))
    lis_q = re.findall(r'<li>', content_q)
    print("Quick notes repeated <li> inside #repeated:", len(lis_q))
    print("Quick notes repeated sample snippet:\n", content_q[:500])
