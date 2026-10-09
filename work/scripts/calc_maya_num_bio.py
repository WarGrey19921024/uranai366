"""マヤ暦（ドリームスペル方式）・数秘術・バイオリズムの計算。
マヤ暦：基準 2013-07-26 = KIN164。2/29 は数えない（前日と同じKIN）。
数秘：けたを足して1けたに（11・22・33は残す）。
バイオリズム：sin(2π・経過日数/周期)。身体23・感情28・知性33日。
"""
import math, datetime as dt

SEAL = ["赤い龍", "白い風", "青い夜", "黄色い種", "赤い蛇", "白い世界の橋渡し", "青い手", "黄色い星",
        "赤い月", "白い犬", "青い猿", "黄色い人", "赤い空歩く人", "白い魔法使い", "青い鷲", "黄色い戦士",
        "赤い地球", "白い鏡", "青い嵐", "黄色い太陽"]
TONE = ["磁気", "月", "電気", "自己存在", "倍音", "律動", "共振", "銀河", "太陽", "惑星", "スペクトル", "水晶", "宇宙"]
REF = dt.date(2013, 7, 26)


def _leaps_between(a: dt.date, b: dt.date) -> int:
    """a<d<=b の範囲にある 2/29 の数"""
    n = 0
    for y in range(a.year, b.year + 1):
        try:
            d = dt.date(y, 2, 29)
        except ValueError:
            continue
        if a < d <= b:
            n += 1
    return n


def kin(d: dt.date) -> int:
    if d >= REF:
        days = (d - REF).days - _leaps_between(REF, d)
    else:
        # d 自身が 2/29 のときは (d, REF] に含まれないので数えられ、結果は 2/28 と同じになる
        days = -((REF - d).days - _leaps_between(d, REF))
    return (163 + days) % 260 + 1


def kin_info(d):
    k = kin(d)
    return {"kin": k, "seal": SEAL[(k - 1) % 20], "tone_no": (k - 1) % 13 + 1, "tone": TONE[(k - 1) % 13]}


def reduce(n: int, keep_master=True) -> int:
    while n > 9 and not (keep_master and n in (11, 22, 33)):
        n = sum(int(c) for c in str(n))
    return n


def life_path(d: dt.date) -> int:
    return reduce(sum(int(c) for c in d.strftime("%Y%m%d")))


def birthday_number(day: int) -> int:
    return reduce(day)


def personal_year(month: int, day: int, year: int) -> int:
    return reduce(sum(int(c) for c in f"{year}{month}{day}"), keep_master=False)


def personal_month(py: int, month: int) -> int:
    return reduce(py + month, keep_master=False)


def personal_day(pm: int, day: int) -> int:
    return reduce(pm + day, keep_master=False)


def bio(birth: dt.date, d: dt.date):
    n = (d - birth).days
    return {k: math.sin(2 * math.pi * n / p) for k, p in (("身体", 23), ("感情", 28), ("知性", 33))}


def mark(v: float) -> str:
    return "★" if v >= 0.8 else "◎" if v >= 0.4 else "〇" if v >= -0.2 else "△" if v >= -0.6 else "▽"


if __name__ == "__main__":
    for s in ["2013-07-26", "2012-12-21", "1987-07-26", "2000-01-01", "2027-01-01"]:
        print(s, kin_info(dt.date.fromisoformat(s)))
    print("2027 PY 1/1:", personal_year(1, 1, 2027), "LP 1990-01-01:", life_path(dt.date(1990, 1, 1)))
