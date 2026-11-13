"""Check one chapter file: python -I check.py N"""
import re, sys, collections
n = sys.argv[1]
want = set(); review = set()
for l in open(f'qlist/ch{n}.txt', encoding='utf-8'):
    if not l.strip(): continue
    i = int(l.split('|')[0])
    (review if 'REVIEW:' in l else want).add(i)
seen = collections.Counter(); bad = []; table = None; facts = 0
lines = open(f'out/ch{n}.md', encoding='utf-8').read().splitlines()
if not lines or not lines[0].startswith('@'): bad.append('first line must start with @')
for no, raw in enumerate(lines, 1):
    l = raw.strip()
    if not l: table = None; continue
    if l.startswith('|'):
        cells = l.strip('|').split('|')
        if table is None: table = len(cells)
        else:
            facts += 1
            if len(cells) != table: bad.append(f'line {no}: table row has {len(cells)} cells, header has {table}')
    else:
        table = None
        if l.startswith('- '): facts += 1
        elif not (l.startswith('@') or l.startswith('## ') or l.startswith('! ')): bad.append(f'line {no}: unknown line type: {l[:50]}')
    m = re.search(r'\{([^{}]*)\}\s*\|?\s*$', l)
    if m:
        for x in re.split(r'[,\s]+', m.group(1).strip()):
            if x.isdigit(): seen[int(x)] += 1
            elif x: bad.append(f'line {no}: bad tag {x!r}')
missing = sorted(want - set(seen)); dup = sorted(i for i, c in seen.items() if c > 1); unknown = sorted(set(seen) - want - review)
print(f'chapter {n}: {facts} fact lines, {len(set(seen) & want)} of {len(want)} items tagged')
if missing: print('MISSING items:', missing)
if dup: print('DUPLICATE items:', dup)
if unknown: print('UNKNOWN items:', unknown)
if sorted(set(seen) & review): print('REVIEW items tagged (remove):', sorted(set(seen) & review))
for b in bad[:30]: print('FORMAT:', b)
print('OK' if not (missing or dup or unknown or bad or (set(seen) & review)) else 'NOT OK')
