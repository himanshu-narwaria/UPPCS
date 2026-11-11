import re

with open('Indian_History_Part_2/history-in-72h.html', 'r', encoding='utf-8') as f:
    h72 = f.read()

# Let's see all occurrences of repeated or rep in h72
for m in re.finditer(r'repeated', h72, re.I):
    pos = m.start()
    print("Match in 72h:", h72[pos-30:pos+100].replace('\n', ' '))
