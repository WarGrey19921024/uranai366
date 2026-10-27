"""マヤ暦（ドリームスペル）2027年の運勢ページ（/unsei-2027/maya/）の数値 → data/maya_2027.json
- ドリームスペルの1年は7月26日に始まる。「2027年のエネルギー」＝2027-07-26のKIN（〜2028-07-25）。あわせて2027年1月1日〜7月25日の前の年（2026-07-26のKIN）も記録
- 20の紋章ごと：年の紋章との関係（同じ紋章・類似＝番号の和19/39・反対＝10離れ・神秘＝番号の和21・同じ色＝ガイドの仲間）※knowledge/07 3の追記と同じ決まり
- 2027年（1/1〜12/31）に、その紋章がめぐってくる日（紋章の日＝20日ごと）
"""
import json, os, sys, datetime as dt

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from calc_maya_num_bio import kin, kin_info  # noqa: E402
from build_maya import load  # noqa: E402

COLORS = ["赤", "白", "青", "黄"]


def seal_no(k):
    return (k - 1) % 20 + 1


def rel(s, y):
    """紋章 s（1〜20）から見た年の紋章 y との関係"""
    if s == y:
        return "同じ紋章"
    if s + y in (19, 39):
        return "類似"
    if (s - y) % 20 == 10:
        return "反対"
    if s + y == 21:
        return "神秘"
    if (s - 1) % 4 == (y - 1) % 4:
        return "同じ色"
    return None


def main():
    seals, tones = load()
    names = [x["name"] for x in seals]
    y27 = kin_info(dt.date(2027, 7, 26))
    y26 = kin_info(dt.date(2026, 7, 26))
    assert kin(dt.date(2013, 7, 26)) == 164
    ys27, ys26 = seal_no(y27["kin"]), seal_no(y26["kin"])
    out = {"year": {"start": "2027-07-26", "end": "2028-07-25", "kin": y27["kin"], "seal_no": ys27, "seal": names[ys27 - 1],
                    "tone_no": y27["tone_no"], "tone": tones[y27["tone_no"] - 1]["name"]},
           "prev": {"start": "2026-07-26", "end": "2027-07-25", "kin": y26["kin"], "seal_no": ys26, "seal": names[ys26 - 1],
                    "tone_no": y26["tone_no"], "tone": tones[y26["tone_no"] - 1]["name"]},
           "seals": {}}
    days = {}
    d = dt.date(2027, 1, 1)
    while d.year == 2027:
        days.setdefault(seal_no(kin(d)), []).append(d.isoformat())
        d += dt.timedelta(days=1)
    for s in range(1, 21):
        out["seals"][s] = {"name": names[s - 1], "color": COLORS[(s - 1) % 4], "kw": seals[s - 1]["kw"],
                           "rel27": rel(s, ys27), "rel26": rel(s, ys26), "days2027": days[s]}
    json.dump(out, open(os.path.join(HERE, "..", "data", "maya_2027.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("2027-07-26:", out["year"], "\n2026-07-26:", out["prev"])
    for s in range(1, 21):
        e = out["seals"][s]
        print(s, e["name"], e["color"], e["rel27"], e["rel26"], len(e["days2027"]), e["days2027"][:2])


if __name__ == "__main__":
    main()
