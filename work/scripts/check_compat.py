"""フェーズ4-1 検査：compat_366.json → work/reports/compat_check.md"""
import json, os, collections, re
HERE = os.path.dirname(os.path.abspath(__file__))
C = json.load(open(os.path.join(HERE, "..", "data", "compat_366.json"), encoding="utf-8"))
B = json.load(open(os.path.join(HERE, "..", "data", "base_366.json"), encoding="utf-8"))
keys = list(B); idx = {k: i for i, k in enumerate(keys)}
md = lambda k: f"{int(k[:2])}/{int(k[2:])}"
ng = collections.defaultdict(list)
appear = collections.Counter()
sent = collections.defaultdict(set)
for a, v in C.items():
    g = [x["mmdd"] for x in v["good"]]; b = [x["mmdd"] for x in v["bad"]]
    if len(g) != 5: ng["良い相性が5日でない"].append(f"{a}({len(g)})")
    if len(b) != 3: ng["ぶつかる相手が3日でない"].append(f"{a}({len(b)})")
    for x in g:
        if a not in [y["mmdd"] for y in C[x]["good"]]: ng["良いの対称性"].append(f"{a}-{x}")
    for x in b:
        if a not in [y["mmdd"] for y in C[x]["bad"]]: ng["ぶつかるの対称性"].append(f"{a}-{x}")
    if set(g) & set(b): ng["良いとぶつかるの両方"].append(a)
    for x in g + b:
        appear[x] += 1
        if x == a or min((idx[a] - idx[x]) % 366, (idx[x] - idx[a]) % 366) <= 1: ng["自分・前後1日"].append(f"{a}-{x}")
    for y in v["good"] + v["bad"]:
        for s in re.split(r"(?<=。)", y["text"]):
            if s.strip(): sent[s.strip()].add(a)
dup = {s: p for s, p in sent.items() if len(p) > 3}
mx = max(appear.values())
L = [f"""# フェーズ4 検査：相性（compat_366.json）

`python work/scripts/build_compat.py && python work/scripts/check_compat.py` で再生成。規則は `work/knowledge/12_スコアと相性の規則.md`。

| 検査 | 結果 |
|---|---|
| 全ページに良い5日・ぶつかる3日 | {'✅' if not ng['良いが5日でない'] and not ng['良い相性が5日でない'] and not ng['ぶつかる相手が3日でない'] else '⚠ ' + ' '.join(ng['良い相性が5日でない'] + ng['ぶつかる相手が3日でない'])} |
| 対称性（AがBを選べばBもAを選ぶ） | {'✅ すべて対称' if not ng['良いの対称性'] and not ng['ぶつかるの対称性'] else '⚠ ' + str(len(ng['良いの対称性']) + len(ng['ぶつかるの対称性'])) + '組'} |
| 同じ組が「良い」と「ぶつかる」の両方 | {'✅ なし' if not ng['良いとぶつかるの両方'] else '⚠ ' + ' '.join(ng['良いとぶつかるの両方'])} |
| 1つの日付が他ページに登場する回数 | 最大 {mx} 回・最小 {min(appear[k] for k in keys)} 回（上限15回）{'✅' if mx <= 15 else '⚠'} |
| 自分自身・前後1日を選んでいない | {'✅' if not ng['自分・前後1日'] else '⚠ ' + ' '.join(ng['自分・前後1日'][:10])} |
| 一言説明の同じ文が4ページ以上 | {'✅ なし（最大 ' + str(max(len(p) for p in sent.values())) + 'ページ）' if not dup else '⚠ ' + str(len(dup)) + '文'} |

- 宿曜は使っていない（月日だけでは本命宿が決まらないため。生まれ年パネル専用）。
- 対称にしたので、どの日付も「良い」に5回・「ぶつかる」に3回ずつ、ちょうど8回登場する（偏りなし）。
"""]
cnt = collections.Counter()
for a, v in C.items():
    for y in v["good"]:
        d = abs((B[a]["sun_lon"] - B[y["mmdd"]]["sun_lon"] + 180) % 360 - 180)
        cnt["120度" if abs(d - 120) <= 8 else "60度" if abs(d - 60) <= 6 else "同じ星座"] += 1
L.append("## 良い相性の根拠の内訳（延べ）\n\n" + "・".join(f"{k} {v}" for k, v in cnt.most_common()) + "\n")
L.append("## 例\n")
for k in ["0101", "0229", "0715", "1231"]:
    L.append(f"### {md(k)}（{B[k]['sign']}・誕生日の数{B[k]['birthday_number']}）\n")
    for y in C[k]["good"]: L.append(f"- 良い {md(y['mmdd'])}：{y['text']}")
    for y in C[k]["bad"]: L.append(f"- ぶつかる {md(y['mmdd'])}：{y['text']}")
    L.append("")
open(os.path.join(HERE, "..", "reports", "compat_check.md"), "w", encoding="utf-8").write("\n".join(L) + "\n")
print("\n".join(L)[:3500])
