"""2027年の運勢ページ（/kyusei/unsei-2027/）の数値を計算して data/kyusei_nenun_2027.json に書く。
- 期間：2027年の立春（2027-02-04）〜2028年の立春前。月は節入りで区切る（立春〜小寒の12か月）
- 各月：月盤の中宮・月の干支・五黄殺／暗剣殺／月破の方位・本命星ごとの宮（位置）と注意の印・月の吉方位
- 年：年盤（九紫中宮）での本命星の宮・年の吉方位
- 本命星の早見表：1930〜2026年生まれ（立春前生まれは前年の星）
吉方位の決め方は knowledge/04_九星気学.md 3-7 と同じ（相生・比和の星の方位から、五黄殺・暗剣殺・破・本命殺・本命的殺を除く。月は年盤の凶方位も除く）。
"""
import datetime as dt, json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import calc_kanshi_kyusei as C  # noqa: E402
from build_kyusei import load, STARS  # noqa: E402

HOUI = C.HOUI  # 0中央 1北西 2西 3北東 4南 5北 6南西 7東 8南東
OPP = {1: 8, 8: 1, 2: 7, 7: 2, 3: 6, 6: 3, 4: 5, 5: 4}
# 十二支の方位（破の計算用）：子=北 丑=北東 寅=北東 卯=東 辰=南東 巳=南東 午=南 未=南西 申=南西 酉=西 戌=北西 亥=北西
SHI_POS = {0: 5, 1: 3, 2: 3, 3: 7, 4: 8, 5: 8, 6: 4, 7: 6, 8: 6, 9: 2, 10: 1, 11: 1}
at = lambda c, p: ((c - 1 + p) % 9) + 1  # noqa: E731  中宮cの盤で宮pにいる星
pal = lambda c, s: (s - c) % 9  # noqa: E731  中宮cの盤で星sがいる宮


def bads(c, branch):
    """盤（中宮c）の五黄殺・暗剣殺と、十二支branchの破（いずれも宮番号。中宮なら None）"""
    p5 = pal(c, 5)
    gohou = p5 or None
    anken = OPP[p5] if p5 else None
    ha = OPP[SHI_POS[branch]]
    return gohou, anken, ha


def lucky(aisho, c, st, bad):
    ps = pal(c, st)
    b = set(x for x in bad if x)
    if ps:
        b |= {ps, OPP[ps]}
    return [p for p in range(1, 9) if p not in b and aisho[STARS[st - 1]][at(c, p) - 1] in "◎○◇"]


def main():
    _, _, aisho, _ = load()
    T = lambda s: dt.datetime.strptime(s, "%Y-%m-%d %H:%M")  # noqa: E731
    S27, S28 = C.setsu()["2027"], C.setsu()["2028"]
    starts = [(n, T(S27[n])) for n in C.SETSU_ORDER[1:]] + [("小寒", T(S28["小寒"]))]
    end = T(S28["立春"])
    yc = 9
    yg, ya, yh = bads(yc, 7)  # 2027年＝未年
    assert C.honmei(T(S27["立春"]) + dt.timedelta(minutes=1)) == 9 and (HOUI[yg], HOUI[ya], HOUI[yh]) == ("北", "南", "北東")
    months = []
    for i, (name, t0) in enumerate(starts):
        t = t0 + dt.timedelta(minutes=1)
        t1 = starts[i + 1][1] if i + 1 < len(starts) else end
        c = C.month_star(t)
        br = C.month_branch(t)
        g, a, h = bads(c, br)
        m = {"setsu": name, "start": t0.strftime("%Y-%m-%d %H:%M"), "end": t1.strftime("%Y-%m-%d %H:%M"),
             "kanshi": C.kanshi(C.month_index(t)), "center": c,
             "gohou": HOUI[g] if g else None, "anken": HOUI[a] if a else None, "ha": HOUI[h], "stars": {}}
        for st in range(1, 10):
            p = pal(c, st)
            marks = []
            if p == 0:
                marks.append("中央")
            if a is not None and p == a:
                marks.append("暗剣殺")
            if p == h:
                marks.append("月破")
            m["stars"][st] = {"palace": HOUI[p], "marks": marks,
                              "lucky": [HOUI[x] for x in lucky(aisho, c, st, [g, a, h, yg, ya, yh])]}
        months.append(m)
    year = {}
    for st in range(1, 10):
        p = pal(yc, st)
        marks = (["中央"] if p == 0 else []) + (["暗剣殺"] if p == ya else []) + (["歳破"] if p == yh else [])
        year[st] = {"palace": HOUI[p], "marks": marks, "lucky": [HOUI[x] for x in lucky(aisho, yc, st, [yg, ya, yh])],
                    "rel9": aisho[STARS[st - 1]][8]}
    hayami = {}
    for y in range(1930, 2027):
        hayami[y] = C.honmei(T(f"{y}-06-01 00:00"))
    out = {"year": {"kanshi": C.kanshi(C.year_index(T(S27["立春"]) + dt.timedelta(minutes=1))), "center": yc,
                    "gohou": HOUI[yg], "anken": HOUI[ya], "ha": HOUI[yh], "start": S27["立春"], "end": S28["立春"], "stars": year},
           "months": months, "hayami": hayami,
           "risshun": {y: C.setsu()[str(y)]["立春"] for y in range(1930, 2028)}}
    path = os.path.join(HERE, "..", "data", "kyusei_nenun_2027.json")
    json.dump(out, open(path, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    for m in months:
        print(m["start"][:10], m["setsu"], m["kanshi"], STARS[m["center"] - 1], m["gohou"], m["anken"], m["ha"])
    for st in range(1, 10):
        print(STARS[st - 1], year[st]["palace"], year[st]["marks"], year[st]["lucky"], " / ", " ".join(m["stars"][st]["palace"] + ("*" + "*".join(m["stars"][st]["marks"]) if m["stars"][st]["marks"] else "") for m in months))


if __name__ == "__main__":
    main()
