"""フェーズ3 点検：birthday_items_366.json → work/reports/items_check.md"""
import json, os, collections
HERE = os.path.dirname(os.path.abspath(__file__))
O = json.load(open(os.path.join(HERE, "..", "data", "birthday_items_366.json"), encoding="utf-8"))
keys = list(O)
get = lambda k, name: [i for i in O[k] if i["項目"].startswith(name)]
L = ["# フェーズ3 点検：誕生日もの・記念日（birthday_items_366.csv）\n", "`python work/scripts/build_items.py && python work/scripts/check_items.py` で再生成。\n",
     "| 項目 | 入っている日 | 確認済み | 未確認 | 備考 |", "|---|---|---|---|---|"]
for name in ["誕生石（月）", "誕生色", "誕生日石", "誕生花", "記念日"]:
    its = [(k, i) for k in keys for i in get(k, name) if i["値"]]
    days = len({k for k, _ in its})
    ok = sum(1 for _, i in its if i["確認済み"])
    note = ""
    if name == "誕生色":
        vals = [get(k, name)[0]["値"] for k in keys if get(k, name)]
        adj = sum(1 for a, b in zip(keys, keys[1:]) if get(a, name) and get(b, name) and get(a, name)[0]["値"] == get(b, name)[0]["値"])
        note = f"色の種類 {len(set(vals))}／隣の日と同じ色 {adj} 組／未確認＝色見本の値（HEX）が出典で未確認"
    if name == "誕生日石":
        vals = [get(k, name)[0]["値"] for k in keys if get(k, name)]
        adj = sum(1 for a, b in zip(keys, keys[1:]) if get(a, name) and get(b, name) and get(a, name)[0]["値"] == get(b, name)[0]["値"])
        c = collections.Counter(vals)
        note = f"石の種類 {len(c)}・最多 {c.most_common(1)[0][1]} 日／隣の日と同じ石 {adj} 組／未確認＝販売ページが未確認"
    if name == "記念日":
        per = collections.Counter(k for k, _ in its)
        few = [k for k in keys if per[k] < 2 and k != "0229"]
        note = f"1日あたり {min(per.values())}〜{max(per.values())} 件／2件未満の日 {len(few)}（{' '.join(few[:15])}）"
    if name == "誕生花":
        note = "PDF（source/birthday/hanakotoba.pdf）待ち"
    L.append(f"| {name} | {days} | {ok} | {len(its) - ok} | {note} |")
titles = collections.Counter(i["値"] for k in keys for i in get(k, "記念日"))
L.append(f"\n- 記念日の同じ題名が複数の日に：{[t for t, n in titles.items() if n > 1] or 'なし'}")
L.append("- **未確認のものはページに使わない**（確認し直すまで保留。検索回数の上限で確認が途中になったため）。")
open(os.path.join(HERE, "..", "reports", "items_check.md"), "w", encoding="utf-8").write("\n".join(L) + "\n")
print("\n".join(L))
