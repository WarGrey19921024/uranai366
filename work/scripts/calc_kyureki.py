"""旧暦（太陰太陽暦・天保暦の決まりを現代の天文計算で適用＝国立天文台方式の「旧暦」）と宿曜の本命宿。
決まり:
  1) 朔（新月）の瞬間を含む日（JST）を月の1日とする
  2) 中気を含む月に、その中気で月の番号をつける（雨水=1月 … 冬至=11月 … 大寒=12月）
  3) 冬至を含む月から次の冬至を含む月までが13か月なら、中気を含まない最初の月を閏月とする
  ※いわゆる「2033年問題」の年は対象外（このサイトの範囲 1900〜2030年には生じない）
宿曜：宿曜経の「各月1日の宿」から日数ぶん進める（27宿・牛宿を除く）。閏月はもとの月と同じ。
出力: work/data/kyureki_1900_2030.json （新暦の日付 → [旧暦年, 月, 閏, 日]）
"""
import json, os, datetime as dt
import swisseph as swe
from common import jd_from_jst, jst_from_jd, lon, new_moons, JST

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "data")

SHUKU27 = ["昴", "畢", "觜", "参", "井", "鬼", "柳", "星", "張", "翼", "軫", "角", "亢",
           "氐", "房", "心", "尾", "箕", "斗", "女", "虚", "危", "室", "壁", "奎", "婁", "胃"]
# 宿曜経：旧暦の各月1日の宿
MONTH_START = {1: "室", 2: "奎", 3: "胃", 4: "畢", 5: "参", 6: "鬼",
               7: "張", 8: "角", 9: "氐", 10: "心", 11: "斗", 12: "虚"}


def jst_date(jd):
    return jst_from_jd(jd, round_min=False).date()


def chuki_dates(y0, y1):
    """中気（太陽黄経30度の倍数）のJST日付 → 月番号"""
    jd = jd_from_jst(dt.datetime(y0, 1, 1, tzinfo=JST))
    end = jd_from_jst(dt.datetime(y1, 1, 1, tzinfo=JST))
    out, prev = [], lon(jd)
    while jd < end:
        nj = jd + 1
        cur = lon(nj)
        if int(prev // 30) != int(cur // 30):
            t = (int(cur // 30) * 30) % 360
            a, b = jd, nj
            for _ in range(45):
                m = (a + b) / 2
                if (lon(m) - t + 180) % 360 - 180 < 0:
                    a = m
                else:
                    b = m
            month = ((t - 330) % 360) // 30 + 1  # 雨水330度=1月, 冬至270度=11月
            out.append((jst_date((a + b) / 2), month))
        prev, jd = cur, nj
    return out


def build(y0=1899, y1=2034):
    nms = [jst_date(j) for j in new_moons(jd_from_jst(dt.datetime(y0, 1, 1, tzinfo=JST)),
                                          jd_from_jst(dt.datetime(y1, 1, 1, tzinfo=JST)))]
    chu = chuki_dates(y0, y1)
    months = []  # [start_date, end_date(excl), [中気の月番号...]]
    ci = 0
    for i in range(len(nms) - 1):
        s, e = nms[i], nms[i + 1]
        cs = [m for d, m in chu if s <= d < e]
        months.append({"start": s, "end": e, "chuki": cs})
    # 番号づけ
    win = [i for i, m in enumerate(months) if 11 in m["chuki"]]  # 冬至を含む月
    for a, b in zip(win, win[1:]):
        leap_needed = (b - a) == 13
        leap_done = False
        months[a]["no"], months[a]["leap"] = 11, False
        num = 11
        for k in range(a + 1, b):
            m = months[k]
            if leap_needed and not leap_done and not m["chuki"]:
                m["no"], m["leap"] = num, True
                leap_done = True
                continue
            num = num % 12 + 1
            m["no"], m["leap"] = num, False
    # 旧暦の年：1月（閏でない）から始まる
    table = {}
    year = None
    for m in months:
        if "no" not in m:
            continue
        if m["no"] == 1 and not m["leap"]:
            year = m["start"].year
        if year is None:
            continue
        d = m["start"]
        while d < m["end"]:
            table[d.isoformat()] = [year, m["no"], m["leap"], (d - m["start"]).days + 1]
            d += dt.timedelta(days=1)
    return table


def shuku(month: int, day: int) -> str:
    i = SHUKU27.index(MONTH_START[month])
    return SHUKU27[(i + day - 1) % 27]


if __name__ == "__main__":
    t = build()
    t = {k: v for k, v in t.items() if "1900-01-01" <= k <= "2030-12-31"}
    os.makedirs(DATA, exist_ok=True)
    with open(os.path.join(DATA, "kyureki_1900_2030.json"), "w", encoding="utf-8") as f:
        json.dump(t, f, ensure_ascii=False, separators=(",", ":"))
    print(len(t), "日分", min(t), "〜", max(t))
