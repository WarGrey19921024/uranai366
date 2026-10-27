"""干支（十二支）別 2027年の運勢ページの数値 → data/eto_2027.json
- 2027年の年支＝未（立春 2027-02-04 から）。関係は knowledge/05 3-7 の3つだけ（支合・三合・冲。刑・害・破は扱わない）
- 五行の関係：年支「未」（土）から見た、本人の支の五行（knowledge/05 3-1）
- 月ごと：2027年2月（寅月）〜2028年1月（丑月）の月支と、本人の支との関係（支合・三合＝追い風、冲＝注意、同じ支＝自分の月）
- 生まれ年：1930〜2026年（立春前生まれは前の年の支）、2027年に年男・年女になる年齢
"""
import json, os, sys, datetime as dt

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import calc_kanshi_kyusei as C  # noqa: E402

SHI = C.SHI
GOGYO = ["水", "土", "木", "木", "土", "火", "火", "土", "金", "金", "土", "水"]
ANIMAL = ["ねずみ", "うし", "とら", "うさぎ", "たつ", "へび", "うま", "ひつじ", "さる", "とり", "いぬ", "いのしし"]
SHIGOU = {0: 1, 1: 0, 2: 11, 11: 2, 3: 10, 10: 3, 4: 9, 9: 4, 5: 8, 8: 5, 6: 7, 7: 6}
SANGOU = [{8, 0, 4}, {11, 3, 7}, {2, 6, 10}, {5, 9, 1}]
CHU = {i: (i + 6) % 12 for i in range(12)}
SEI = {"木": "火", "火": "土", "土": "金", "金": "水", "水": "木"}  # 生む
KOKU = {"木": "土", "土": "水", "水": "火", "火": "金", "金": "木"}  # 剋す


def rel(a, b):
    """支aから見た支bとの関係（このサイトで扱う3つ＋同じ支）"""
    if a == b:
        return "同じ支"
    if SHIGOU[a] == b:
        return "支合"
    if any(a in g and b in g for g in SANGOU):
        return "三合"
    if CHU[a] == b:
        return "冲"
    return None


def gogyo_rel(me, year):
    """本人の五行 me から見た年の五行 year"""
    if me == year:
        return "比和"
    if SEI[year] == me:
        return "年に生じられる"
    if SEI[me] == year:
        return "年を生む"
    if KOKU[year] == me:
        return "年に剋される"
    return "年を剋す"


def main():
    Y = 7  # 未
    T = lambda s: dt.datetime.strptime(s, "%Y-%m-%d %H:%M")  # noqa: E731
    S27, S28 = C.setsu()["2027"], C.setsu()["2028"]
    starts = [(n, T(S27[n])) for n in C.SETSU_ORDER[1:]] + [("小寒", T(S28["小寒"]))]
    months = []
    for i, (name, t0) in enumerate(starts):
        t1 = starts[i + 1][1] if i + 1 < len(starts) else T(S28["立春"])
        b = C.month_branch(t0 + dt.timedelta(minutes=1))
        months.append({"setsu": name, "start": t0.strftime("%Y-%m-%d"), "end": (t1 - dt.timedelta(days=1)).strftime("%Y-%m-%d"),
                       "branch": SHI[b], "kanshi": C.kanshi(C.month_index(t0 + dt.timedelta(minutes=1))), "b": b})
    assert [m["branch"] for m in months] == list("寅卯辰巳午未申酉戌亥子丑")
    out = {"year": {"kanshi": "丁未", "branch": "未", "gogyo": "土", "start": S27["立春"], "end": S28["立春"]}, "months": [], "eto": {}}
    for m in months:
        out["months"].append({k: v for k, v in m.items() if k != "b"})
    for s in range(12):
        years = [y for y in range(1930, 2027) if C.year_index(T(f"{y}-06-01 00:00")) % 12 == s]
        ages = sorted(2027 - y for y in years) if s == Y else []
        ms = []
        for m in months:
            r = rel(s, m["b"])
            ms.append(r)
        out["eto"][SHI[s]] = {"animal": ANIMAL[s], "gogyo": GOGYO[s], "rel": rel(s, Y), "gogyo_rel": gogyo_rel(GOGYO[s], "土"),
                              "years": sorted(years, reverse=True), "toshi_otoko_ages": ages, "month_rel": ms}
    path = os.path.join(HERE, "..", "data", "eto_2027.json")
    json.dump(out, open(path, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    for s in range(12):
        e = out["eto"][SHI[s]]
        print(SHI[s], e["gogyo"], e["rel"], e["gogyo_rel"], e["years"][:2], " ".join(f'{m["start"][5:7]}{r[0] if r else "・"}' for m, r in zip(months, e["month_rel"])))
    print("年男年女の年齢", out["eto"]["未"]["toshi_otoko_ages"])


if __name__ == "__main__":
    main()
