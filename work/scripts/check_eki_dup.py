"""易64卦の文章で、別の卦と同じ言い回し（句読点を除いて連続16字以上）がないかを調べる。書き下し文は除く。"""
import json, pathlib, re, collections
W = pathlib.Path(__file__).resolve().parent.parent
N = 16
seen = collections.defaultdict(set)
for p in sorted((W / 'data/eki_texts').glob('*.json')):
    d = json.load(open(p, encoding='utf-8'))
    parts = [d[k] for k in ('catch', 'gua_mean', 'shape', 'overall', 'now', 'advice')] + list(d['themes'].values()) + [y[k] for y in d['yao'] for k in ('mean', 'read')] + [q['a'] for q in d['faq']]
    for s in parts:
        s = re.sub(r'[、。「」（）・\s]', '', s)
        for i in range(len(s) - N + 1):
            seen[s[i:i + N]].add(d['n'])
dups = {k: v for k, v in seen.items() if len(v) > 1}
print(f'重複 {len(dups)} 件')
for k, v in list(dups.items())[:40]:
    print(sorted(v), k)
