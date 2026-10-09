"""work/data/planets_2027.json から work/knowledge/02_2027年の天体.md の表部分を作る"""
import json, os
HERE = os.path.dirname(os.path.abspath(__file__))
d = json.load(open(os.path.join(HERE, "..", "data", "planets_2027.json"), encoding="utf-8"))
L = []
L.append("### 2027年1月1日 0時（日本時間）の位置\n\n| 天体 | 位置 |\n|---|---|")
for k, v in d["start_positions"].items():
    L.append(f"| {k} | {v} |")
for name in ["太陽", "水星", "金星", "火星", "木星", "土星", "天王星", "海王星", "冥王星"]:
    rows = [r for r in d["ingress"] if r["planet"] == name]
    L.append(f"\n### {name}の星座移動（{len(rows)}回）\n")
    if not rows:
        L.append("2027年中の星座移動なし（1年を通して同じ星座）。")
        continue
    L.append("| 日時（JST） | 入る星座 | 備考 |\n|---|---|---|")
    for r in rows:
        L.append(f"| {r['jst']} | {r['to']} | {'逆行で前の星座に戻る' if r['retrograde'] else ''} |")
L.append("\n### 逆行（留＝向きが変わる日時）\n\n| 天体 | 日時（JST） | できごと | 位置 |\n|---|---|---|---|")
for r in d["stations"]:
    L.append(f"| {r['planet']} | {r['jst']} | {r['kind']} | {r['sign']} {r['deg']:.1f}度 |")
L.append("\n### 日食・月食\n\n| 種類 | 食の最大（JST） | 位置 | 日本（東京）で |\n|---|---|---|---|")
for r in d["eclipses"]:
    L.append(f"| {r['type']} | {r['jst_max']} | {r['sign']} {r['deg']:.1f}度 | {r['japan']} |")
print("\n".join(L))
