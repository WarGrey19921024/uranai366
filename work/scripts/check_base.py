"""base_366.json の集計と点検 → work/reports/base_check.md"""
import json, os, collections
HERE = os.path.dirname(os.path.abspath(__file__))
b = json.load(open(os.path.join(HERE, "..", "data", "base_366.json"), encoding="utf-8"))
R = []
ng = []
assert len(b) == 366 and "0229" in b
md = lambda k: f"{int(k[:2])}/{int(k[2:])}"
# 星座ごとの期間
R.append("## 星座ごとの期間（平均の太陽の度数で決めた「主な星座」）\n\n| 星座 | 最初の日 | 最後の日 | 日数 | 境目の日（年によって星座が変わる） |\n|---|---|---|---|---|")
by = collections.OrderedDict()
for k, r in b.items():
    by.setdefault(r["sign"], []).append(k)
for s, ks in by.items():
    # 山羊座は年をまたぐ
    if s == "山羊座":
        ks = [k for k in ks if k >= "1201"] + [k for k in ks if k < "1201"]
    borders = [md(k) for k in ks if b[k]["sign_border"]]
    R.append(f"| {s} | {md(ks[0])} | {md(ks[-1])} | {len(ks)} | {'・'.join(borders)} |")
# 点検
for k, r in b.items():
    if r["decan"] not in (1, 2, 3): ng.append(f"{k} デーカン異常")
    if not (0 <= r["sun_deg_in_sign"] < 30): ng.append(f"{k} 度数異常")
    if b[r["next"]]["birthday_number"] == r["birthday_number"] and r["next"] != "0101" and k != "1231":
        ng.append(f"{k} 隣の日と誕生日の数が同じ")
keys = list(b)
for a, c in zip(keys, keys[1:]):
    if b[a]["sun_lon"] == b[c]["sun_lon"]: ng.append(f"{a}/{c} 度数が同じ")
cnt = lambda f: sum(1 for r in b.values() if f(r))
R.insert(0, f"""# フェーズ2 点検：base_366.json

`python work/scripts/check_base.py` で再生成。

| 項目 | 結果 |
|---|---|
| 日数 | {len(b)}（0229を含む） |
| 星座の境目の日 | {cnt(lambda r: r['sign_border'])} 日 |
| デーカンの境目の日 | {cnt(lambda r: r['decan_border'])} 日 |
| 七十二候の境目の日（1930〜2027年で候が変わる） | {cnt(lambda r: r['kou_border'])} 日 |
| 七十二候の種類 | {len({r['kou'] for r in b.values()})} |
| 節気の当日（2027年） | {cnt(lambda r: r['sekki_day'])} 日 |
| 2027年のパーソナルイヤー | {dict(sorted(collections.Counter(r['py2027'] for r in b.values()).items()))} |
| 誕生日の数 | {dict(sorted(collections.Counter(r['birthday_number'] for r in b.values()).items()))} |
| 2027年の誕生日の曜日 | {dict(collections.Counter(r['bday2027']['weekday'] for r in b.values()))} |
| 点検での異常 | {len(ng)} 件 {'・'.join(ng[:10])} |

決めたこと：基準期間は1930〜2027年。太陽の度数＝各年のその日12時（日本時間）の平均。七十二候は2027年の暦（2/29は2028年）。2/29生まれの2027年の誕生日当日は2/28。
""")
open(os.path.join(HERE, "..", "reports", "base_check.md"), "w", encoding="utf-8").write("\n".join(R) + "\n")
print("\n".join(R[:1])[:1500]); print(len(ng))
