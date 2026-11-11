import re

def check_economy():
    with open('Economy 2024/economy-uppsc-full-notes.html', encoding='utf-8') as f:
        text = f.read()
    ch = re.findall(r'<a href="#c(\d+)"><span class="no">(\d+)</span><span class="nm">([^<]+)</span>', text)
    print(f'Economy has {len(ch)} chapters:')
    for c in ch[:10]:
        print(c)
    print('...')
    for c in ch[-5:]:
        print(c)

def check_polity():
    with open('Indian_Polity_2026/polity-uppsc-full-notes.html', encoding='utf-8') as f:
        text = f.read()
    ch = re.findall(r'<a href="#c(\d+)"><span class="no">(\d+)</span><span class="nm">([^<]+)</span>', text)
    print(f'Polity has {len(ch)} chapters:')
    for c in ch[:10]:
        print(c)
    print('...')
    for c in ch[-5:]:
        print(c)

if __name__ == '__main__':
    check_economy()
    check_polity()
