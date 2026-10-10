"""フェーズ8の直し用：指定した星座のページが関わる「同じ文（4ページ以上）」と「同じセクションの類似度0.40以上」を全件出す
使い方: python list_dups.py capricorn"""
import sys, os, json, glob, re, collections, itertools
HERE = os.path.dirname(os.path.abspath(__file__))
T = os.path.join(HERE, "..", "text")
SIGN = sys.argv[1]
pages = {}
for f in glob.glob(os.path.join(T, "*.json")):
    s = os.path.basename(f)[:-5]
    if s.startswith("_"): continue
    for k, v in json.load(open(f, encoding="utf-8")).items(): pages[k] = (s, v)
sys.argv = [sys.argv[0]]
import check_dup as C
secs = {k: C.sections(v) for k, (s, v) in pages.items()}
where = collections.defaultdict(set)
for k, x in secs.items():
    for t in x.values():
        for s_ in C.sents(t): where[s_].add(k)
mine = {k for k, (s, v) in pages.items() if s == SIGN}
print(f"# {SIGN}：同じ文（4ページ以上）で自分の星座の日が入っているもの")
for s_, p in sorted(where.items(), key=lambda x: -len(x[1])):
    if len(p) >= 4 and p & mine:
        print(f"- {len(p)}ページ：{s_}　自分の日：{' '.join(sorted(p & mine))}　（ほか：{' '.join(sorted(p - mine)[:6])}）")
print(f"\n# {SIGN}：同じセクションの類似度0.40以上（相手は全星座）")
names = sorted({n for x in secs.values() for n in x})
for n in names:
    have = {k: C.grams(secs[k][n]) for k in pages if n in secs[k] and len(secs[k][n]) >= 30}
    for a in sorted(mine & set(have)):
        for b, gb in have.items():
            if b == a or (b in mine and b < a): continue
            j = C.jac(have[a], gb)
            if j >= .40: print(f"- {j:.2f} {n} {a}–{b}")
