"""History-UPPCS: write per-chapter source text and question lists from pyqbooks/history/source.json."""
import json, re, collections
S = json.load(open('../pyqbooks/history/source.json', encoding='utf-8'))
def runs(r):
    if isinstance(r, str): return r
    return ''.join(x[0] if isinstance(x, (list, tuple)) else str(x) for x in (r or []))
def block(b):
    if isinstance(b, str): return b
    if 'runs' in b: return ('* ' if b.get('kind') == 'li' else '') + runs(b['runs'])
    if 'rows' in b: return '\n'.join(' | '.join(runs(c) if not isinstance(c, str) else c for c in row) for row in b['rows'])
    return ' '.join(block(v) if isinstance(v, dict) else runs(v) if isinstance(v, list) else str(v) for k, v in b.items() if k != 'kind')
def blocks(L):
    if isinstance(L, str): return L
    return '\n'.join(block(b) for b in (L or []))
by = collections.defaultdict(list)
for q in S['questions']: by[q['ch']].append(q)
kinds = collections.Counter(); sizes = {}
for c in S['chapters']:
    n = c['num']; qs = by[n]
    nums = [q['num'] for q in qs]; assert len(nums) == len(set(nums)), (n, 'dup nums')
    t = [f"CHAPTER {n}: {c['title']}", '', 'EXPLANATION SECTION', blocks(c['theory'])]
    for s in c.get('sections') or []: t.append(blocks(s) if not isinstance(s, dict) else block(s))
    t += ['', 'QUESTIONS']
    ql = []
    for q in qs:
        for b in (q['expl'] or []):
            if isinstance(b, dict): kinds[b.get('kind')] += 1
        opts = '\n'.join(f"({k}) {runs(v)}" for k, v in q['options'].items())
        mid = blocks(q['mid']) if q['mid'] else ''
        ex = blocks(q['expl']) if q['expl'] else ''
        if q.get('see'): ex = (f"[See the explanation of question {q['see']}] " + ex).strip()
        t.append(f"{q['num']}. {runs(q['stem'])}\n{mid}\n{opts}\n{'; '.join(q['tags'])}\nAns. ({q['ans']})\n{ex}\n")
        key = ' & '.join(runs(q['options'][k]) for k in re.findall(r'[a-e]', q['ans'].lower()) if k in q['options'])
        flag = '' if key else ' | REVIEW: key or options unclear, do not tag'
        ql.append(f"{q['num']} | {'; '.join(q['tags']) or 'no exam label'} | Q: {re.sub(chr(10), ' ', runs(q['stem']))[:300]} | KEY: {key[:160]}{flag}")
    txt = re.sub(r'\n{3,}', '\n\n', '\n'.join(t))
    open(f'texts/ch{n}.txt', 'w', encoding='utf-8').write(txt); open(f'qlist/ch{n}.txt', 'w', encoding='utf-8').write('\n'.join(ql) + '\n')
    sizes[n] = len(txt)
print('kinds', kinds, 'total chars', sum(sizes.values()))
print('review', sum(1 for n in sizes for l in open(f'qlist/ch{n}.txt', encoding='utf-8') if 'REVIEW' in l))
acc = 0
for c in S['chapters']: print(c['num'], c['title'][:44], sizes[c['num']], len(by[c['num']]))
json.dump(sizes, open('sizes.json', 'w'))
