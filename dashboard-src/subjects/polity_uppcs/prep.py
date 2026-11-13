"""Polity-UPPCS: write one question list per chapter (all exams) for the fact-extraction agents."""
import json, re, os
A = json.load(open('../polity/all_source_questions.json', encoding='utf-8'))
by = {}
for q in A:
    n = int(re.search(r'item(\d+)$', q['id']).group(1))
    by.setdefault(q['chapter'], []).append((n, q))
for ch, L in by.items():
    nums = [n for n, _ in L]; assert len(nums) == len(set(nums)), ch
    out = []
    for n, q in sorted(L):
        key = ' & '.join(q['o'][k] for k in q['k'] if k < len(q['o'])) if q['k'] else ''
        flag = ' | REVIEW: key or options unclear, do not tag' if (q['review'] or not q['k']) else ''
        out.append(f"{n} | {'; '.join(q['exams']) or 'no exam label'} | Q: {re.sub(r'\s+', ' ', q['s'])[:300]} | KEY: {key[:160]}{flag}")
    open(f'qlist/ch{ch}.txt', 'w', encoding='utf-8').write('\n'.join(out) + '\n')
print({ch: len(L) for ch, L in sorted(by.items())})
