"""フェーズ2：計算で決まる値を366日分まとめる → work/data/base_366.json（キー MMDD、0229を含む）
決めたこと（work/knowledge/01・03・08 に追記済み）:
- 基準期間 1930〜2027年（生まれ年パネルの対象 1930〜2020年＋2027年）
- 太陽の度数：基準期間の各年の、その日 12:00 JST の視黄経の平均（2/29 はうるう年だけ）
- 星座の境目フラグ：基準期間のどれか1年で、その日 0:00〜24:00 JST に太陽が星座の0度を通る
- 七十二候・二十四節気：2027年の暦で決める（その日までに始まった最後の候）。2/29 は2028年の暦。
  基準期間で別の候になる年があれば kou_alt に入れる（境目フラグ）
- 2/29 生まれの2027年の誕生日当日は 2/28（年齢計算ニ関スル法律：前日の終了時に年をとる）
"""
import json, os, datetime as dt, collections
import swisseph as swe
from common import jd_from_jst, jst_from_jd, lon, SIGNS, JST
from calc_sekki import crossings, SEKKI, KOU, SEKKI_BY_DEG
from calc_kanshi_kyusei import kanshi, day_index
from calc_maya_num_bio import birthday_number, personal_year, personal_month, personal_day

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "data", "base_366.json")
Y0, Y1 = 1930, 2027
ELEMENT = ["火", "地", "風", "水"] * 3
MODE = ["活動", "不動", "柔軟"] * 4
RULER = ["火星", "金星", "水星", "月", "太陽", "水星", "金星", "冥王星", "木星", "土星", "天王星", "海王星"]
RULER_CLASSIC = ["火星", "金星", "水星", "月", "太陽", "水星", "金星", "火星", "木星", "土星", "土星", "木星"]
WEEK = "月火水木金土日"
SIGN_RANGE_EN = ["aries", "taurus", "gemini", "cancer", "leo", "virgo", "libra", "scorpio",
                 "sagittarius", "capricorn", "aquarius", "pisces"]


def all_dates():
    d = dt.date(2028, 1, 1)  # うるう年で 366日を並べる
    while d.year == 2028:
        yield d.strftime("%m%d"), d.month, d.day
        d += dt.timedelta(days=1)


def kou_info(deg):
    base = (deg - (deg - 315) % 15) % 360
    s = SEKKI_BY_DEG[base]
    idx = ((deg - base) % 360) // 5
    name, yomi = KOU[s[1]][idx]
    return {"kou": name, "kou_yomi": yomi, "kou_no": idx + 1, "kou_serial": ((deg - 315) % 360) // 5 + 1,
            "sekki": s[1], "sekki_yomi": s[2]}


def main():
    # 1) 5度ごとの通過時刻（候・節気・星座の境目）を基準期間＋2028年ぶん
    cross = crossings(Y0, 2028, 5)
    by_year = collections.defaultdict(list)  # 年 → [(JST datetime, deg)]
    for deg, jd in cross:
        t = jst_from_jd(jd, round_min=False)
        by_year[t.year].append((t, deg))
    # 前年末の状態も必要なので、年をまたいで並べたリスト
    seq = sorted((t, deg) for y in by_year for t, deg in by_year[y])

    def kou_on(date: dt.date):
        """その日（の終わりまで）に始まった最後の候の度数"""
        end = dt.datetime(date.year, date.month, date.day, tzinfo=JST) + dt.timedelta(days=1)
        last = None
        for t, deg in seq:
            if t < end:
                last = deg
            else:
                break
        return last

    # 高速化：日付→候 を前計算
    kou_by_date = {}
    i = 0
    d = dt.date(Y0, 1, 1)
    cur = None
    while d <= dt.date(2028, 12, 31):
        end = dt.datetime(d.year, d.month, d.day, tzinfo=JST) + dt.timedelta(days=1)
        while i < len(seq) and seq[i][0] < end:
            cur = seq[i][1]
            i += 1
        kou_by_date[d] = cur
        d += dt.timedelta(days=1)
    sign_cross = [(t, deg) for t, deg in seq if deg % 30 == 0]
    sekki_day = {(t.date()): deg for t, deg in seq if deg % 15 == 0}

    out = {}
    for key, m, dd in all_dates():
        years = [y for y in range(Y0, Y1 + 1) if not (m == 2 and dd == 29) or (y % 4 == 0 and (y % 100 != 0 or y % 400 == 0))]
        # 太陽の度数（12:00 JST の平均。基準値からのずれで平均）
        ls = [lon(jd_from_jst(dt.datetime(y, m, dd, 12, tzinfo=JST))) for y in years]
        ref = ls[0]
        mean = (ref + sum(((x - ref + 180) % 360 - 180) for x in ls) / len(ls)) % 360
        s = int(mean // 30)
        deg_in = mean % 30
        decan = int(deg_in // 10) + 1
        decan_sign = (s + 4 * (decan - 1)) % 12
        # 星座の境目：その日の 0〜24時に 30度の倍数を通過した年
        border_years, other = [], set()
        for t, deg in sign_cross:
            if t.year in years and t.month == m and t.day == dd:
                border_years.append(t.year)
                other.update({SIGNS[int(deg // 30)], SIGNS[(int(deg // 30) - 1) % 12]})
        other.discard(SIGNS[s])
        # 12:00 の星座が平均と違う年
        noon_other = sorted({SIGNS[int(x // 30)] for x in ls} - {SIGNS[s]})
        # 七十二候：2027年（2/29は2028年）
        yref = 2028 if key == "0229" else 2027
        kd = kou_by_date[dt.date(yref, m, dd)]
        kinfo = kou_info(kd)
        alt = collections.Counter(kou_info(kou_by_date[dt.date(y, m, dd)])["kou"] for y in years)
        sd = sekki_day.get(dt.date(yref, m, dd))
        # 2027年の誕生日当日
        bday = dt.date(2027, 2, 28) if key == "0229" else dt.date(2027, m, dd)
        py = personal_year(m, dd, 2027)
        pms = {str(mm): personal_month(py, mm) for mm in range(1, 13)}
        rec = {
            "mmdd": key, "month": m, "day": dd,
            "sun_lon": round(mean, 3), "sun_deg_in_sign": round(deg_in, 2),
            "sun_lon_range": [round(min(ls, key=lambda x: (x - mean + 180) % 360 - 180), 3),
                              round(max(ls, key=lambda x: (x - mean + 180) % 360 - 180), 3)],
            "sign": SIGNS[s], "sign_en": SIGN_RANGE_EN[s], "sign_index": s,
            "element": ELEMENT[s], "mode": MODE[s], "ruler": RULER[s], "ruler_classic": RULER_CLASSIC[s],
            "decan": decan, "decan_ruler": RULER[decan_sign], "decan_ruler_classic": RULER_CLASSIC[decan_sign],
            "decan_sign": SIGNS[decan_sign],
            "decan_border": len({int(((x % 30)) // 10) for x in ls}) > 1 or len({int(x // 30) for x in ls}) > 1,
            "sign_border": bool(border_years) or bool(noon_other),
            "sign_border_other": sorted(other | set(noon_other)),
            "sign_border_years": len(border_years),
            "sekki": kinfo["sekki"], "sekki_yomi": kinfo["sekki_yomi"],
            "sekki_day": SEKKI_BY_DEG[sd][1] if sd is not None else None,
            "kou": kinfo["kou"], "kou_yomi": kinfo["kou_yomi"], "kou_no": kinfo["kou_no"],
            "kou_serial": kinfo["kou_serial"], "kou_ref_year": yref,
            "kou_border": len(alt) > 1,
            "kou_alt": [k for k, _ in alt.most_common() if k != kinfo["kou"]],
            "birthday_number": birthday_number(dd),
            "py2027": py, "pm2027": pms,
            "bday2027": {"date": bday.isoformat(), "weekday": WEEK[bday.weekday()],
                         "day_kanshi": kanshi(day_index(bday)),
                         "personal_day": personal_day(pms[str(bday.month)], bday.day)},
        }
        out[key] = rec
    keys = list(out)
    for i, k in enumerate(keys):
        out[k]["prev"] = keys[i - 1]
        out[k]["next"] = keys[(i + 1) % len(keys)]
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    return out


if __name__ == "__main__":
    o = main()
    print(len(o), "日")
    for k in ["0101", "0120", "0229", "0321", "1222", "1231"]:
        r = o[k]
        print(k, r["sign"], r["sun_deg_in_sign"], "第%dデーカン" % r["decan"], r["decan_ruler"],
              "境目" if r["sign_border"] else "", r["sign_border_other"], r["sekki"], r["kou"], r["kou_alt"],
              "誕生日数", r["birthday_number"], "PY", r["py2027"], r["bday2027"])
