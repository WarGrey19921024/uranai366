"""干支（年柱・月柱・日柱）と九星（本命星・年盤・月盤）の計算。
年の区切り＝立春の瞬間、月の区切り＝各月の節入り（calc_sekki.py の setsuiri_1900_2100.json）。
日柱の基準：1900-01-01 = 甲戌（六十干支の11番目、0始まりで10）。
"""
import json, os, datetime as dt

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "data")
KAN = "甲乙丙丁戊己庚辛壬癸"
SHI = "子丑寅卯辰巳午未申酉戌亥"
KAN_YOMI = ["きのえ", "きのと", "ひのえ", "ひのと", "つちのえ", "つちのと", "かのえ", "かのと", "みずのえ", "みずのと"]
SHI_YOMI = ["ね", "うし", "とら", "う", "たつ", "み", "うま", "ひつじ", "さる", "とり", "いぬ", "い"]
KYUSEI = ["", "一白水星", "二黒土星", "三碧木星", "四緑木星", "五黄土星", "六白金星", "七赤金星", "八白土星", "九紫火星"]
# 後天定位盤の飛泊順（中宮→乾→兌→艮→離→坎→坤→震→巽）
HOUI = ["中央", "北西", "西", "北東", "南", "北", "南西", "東", "南東"]
SETSU_ORDER = ["小寒", "立春", "啓蟄", "清明", "立夏", "芒種", "小暑", "立秋", "白露", "寒露", "立冬", "大雪"]
SETSU_BRANCH = {"立春": 2, "啓蟄": 3, "清明": 4, "立夏": 5, "芒種": 6, "小暑": 7,
                "立秋": 8, "白露": 9, "寒露": 10, "立冬": 11, "大雪": 0, "小寒": 1}  # 十二支の番号

_SETSU = None


def setsu():
    global _SETSU
    if _SETSU is None:
        _SETSU = json.load(open(os.path.join(DATA, "setsuiri_1900_2100.json"), encoding="utf-8"))
    return _SETSU


def kanshi(n: int) -> str:
    return KAN[n % 10] + SHI[n % 12]


def day_index(d: dt.date) -> int:
    return (10 + (d - dt.date(1900, 1, 1)).days) % 60


def risshun(year: int) -> dt.datetime:
    return dt.datetime.strptime(setsu()[str(year)]["立春"], "%Y-%m-%d %H:%M")


def eto_year(t: dt.datetime) -> int:
    """立春で切り替わる干支の年（西暦）"""
    return t.year if t >= risshun(t.year) else t.year - 1


def year_index(t: dt.datetime) -> int:
    return (eto_year(t) - 4) % 60  # 西暦4年＝甲子


def month_branch(t: dt.datetime) -> int:
    """直近の節入りから月の十二支の番号を決める"""
    cand = []
    for y in (t.year - 1, t.year):
        for name, s in setsu()[str(y)].items():
            st = dt.datetime.strptime(s, "%Y-%m-%d %H:%M")
            if st <= t:
                cand.append((st, name))
    return SETSU_BRANCH[max(cand)[1]]


def month_index(t: dt.datetime) -> int:
    yk = year_index(t) % 10
    b = month_branch(t)
    tora_kan = {0: 2, 5: 2, 1: 4, 6: 4, 2: 6, 7: 6, 3: 8, 8: 8, 4: 0, 9: 0}[yk]  # 寅月の天干（五虎遁）
    k = (tora_kan + (b - 2) % 12) % 10
    # 天干k・地支bを満たす六十干支の番号
    return next(n for n in range(60) if n % 10 == k and n % 12 == b)


def honmei(t: dt.datetime) -> int:
    """本命星（年の九星）：立春で切替"""
    y = eto_year(t)
    return (11 - y % 9) % 9 or 9


def month_star(t: dt.datetime) -> int:
    """月の九星（月盤の中宮）：節入りで切替"""
    ys = honmei(t)
    tora = {1: 8, 4: 8, 7: 8, 3: 5, 6: 5, 9: 5, 2: 2, 5: 2, 8: 2}[ys]
    b = month_branch(t)
    return ((tora - 1 - (b - 2) % 12) % 9) + 1


def ban(center: int) -> dict:
    """中宮の星から、各方位の星（飛泊）"""
    return {HOUI[i]: KYUSEI[((center - 1 + i) % 9) + 1] for i in range(9)}


if __name__ == "__main__":
    T = lambda s: dt.datetime.strptime(s, "%Y-%m-%d %H:%M")
    for s in ["2027-01-01 12:00", "2027-02-04 10:45", "2027-02-04 10:47", "2027-12-31 12:00"]:
        t = T(s)
        print(s, "年", kanshi(year_index(t)), "月", kanshi(month_index(t)), "日", kanshi(day_index(t.date())),
              "年の九星", KYUSEI[honmei(t)], "月の九星", KYUSEI[month_star(t)])
    print("2027年盤", ban(9))
