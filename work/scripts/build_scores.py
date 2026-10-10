"""フェーズ4-2：月別スコア（2027年・12か月）→ work/data/scores_366.json
規則は work/knowledge/12_スコアと相性の規則.md（このスクリプトと同じ内容）。手で数字を直さない。
3本：
  星座 … 2027年の各日12:00 JSTの 太陽・金星・火星・木星・土星 が、その誕生日の太陽の度数に作るアスペクト（01_西洋占星術 3-7）
  数秘 … 2027年のパーソナルマンスの点（PM_SCORE）＋誕生日の数と同じ数の月は+5
  暦の五行 … その月（15日時点）の月柱の天干・地支の五行と、星座のエレメントの五行（火→火・地→土・風→木・水→水）の関係
総合 … 3本の平均。分野別（仕事・恋愛・金・健康・人間関係）も同じ材料の組み合わせで出す
"""
import json, os, math, datetime as dt, statistics as st
import swisseph as swe
from common import jd_from_jst, lon, JST
from calc_kanshi_kyusei import month_index, KAN, SHI

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "data")
P = {"太陽": swe.SUN, "金星": swe.VENUS, "火星": swe.MARS, "木星": swe.JUPITER, "土星": swe.SATURN}
ASPECTS = [0, 60, 90, 120, 180]
ORB = {"太陽": (6, 4), "金星": (6, 4), "火星": (6, 4), "木星": (4, 3), "土星": (4, 3)}  # (主要, 60度)
PT = {"太陽": {0: .8, 60: .5, 90: -.5, 120: .8, 180: -.4},
      "金星": {0: 1.0, 60: .6, 90: -.3, 120: 1.0, 180: -.3},
      "火星": {0: .2, 60: .5, 90: -.8, 120: .7, 180: -.7},
      "木星": {0: 1.0, 60: .7, 90: -.3, 120: 1.0, 180: -.2},
      "土星": {0: -.6, 60: .4, 90: -1.0, 120: .5, 180: -.8}}
W = {"太陽": 1.0, "金星": .8, "火星": .8, "木星": .7, "土星": .7}
PM_SCORE = {1: 70, 2: 55, 3: 80, 4: 50, 5: 65, 6: 70, 7: 40, 8: 85, 9: 45}
ELEM5 = {"火": "火", "地": "土", "風": "木", "水": "水"}
KAN5 = "木木火火土土金金水水"
SHI5 = {"子": "水", "丑": "土", "寅": "木", "卯": "木", "辰": "土", "巳": "火", "午": "火", "未": "土", "申": "金", "酉": "金", "戌": "土", "亥": "水"}
GEN = {"木": "火", "火": "土", "土": "金", "金": "水", "水": "木"}   # 相生：A が B を生む
KOKU = {"木": "土", "土": "水", "水": "火", "火": "金", "金": "木"}  # 相剋：A が B を剋す
REL_SCORE = {"生じられる": 85, "比和": 75, "剋す": 60, "生じる": 50, "剋される": 30}
# 分野別：天体ごとの寄与の重み（星座側）と、数秘で追い風になる月の数
FIELD_PLANET = {"仕事": {"太陽": 1, "火星": 1, "土星": 1.2, "木星": .6},
                "恋愛": {"金星": 1.5, "太陽": .5, "火星": .5},
                "金運": {"木星": 1.3, "金星": 1, "土星": .5},
                "健康": {"太陽": 1.2, "火星": 1, "土星": .6},
                "人間関係": {"金星": 1, "木星": 1, "太陽": .6}}
FIELD_PM = {"仕事": {8: 12, 4: 8, 1: 6, 7: -6}, "恋愛": {2: 10, 3: 8, 6: 10, 7: -6},
            "金運": {8: 12, 4: 6, 6: 4, 9: -6}, "健康": {4: 8, 6: 6, 7: 4, 5: -6},
            "人間関係": {2: 12, 6: 10, 3: 6, 1: -4}}


def astro_scale(x):
    """星座の生の値（S で割ったもの）→ 点数。60＋40·tanh(1.2x)：端で張り付かず 20〜100 に収まる"""
    return 60 + 40 * math.tanh(1.2 * x)


def relation(me, other):
    if me == other: return "比和"
    if GEN[other] == me: return "生じられる"
    if GEN[me] == other: return "生じる"
    if KOKU[me] == other: return "剋す"
    return "剋される"


def planet_table():
    """2027年の各日12:00 JST の黄経"""
    d, out = dt.date(2027, 1, 1), []
    while d.year == 2027:
        jd = jd_from_jst(dt.datetime(d.year, d.month, d.day, 12, tzinfo=JST))
        out.append((d, {n: lon(jd, b) for n, b in P.items()}))
        d += dt.timedelta(days=1)
    return out


def aspect_contrib(pl, plon, natal):
    diff = abs((plon - natal + 180) % 360 - 180)
    for a in ASPECTS:
        orb = ORB[pl][1] if a == 60 else ORB[pl][0]
        dev = abs(diff - a)
        if dev <= orb:
            return a, PT[pl][a] * W[pl] * (1 - dev / orb)
    return None, 0.0


def month_kanshi(m):
    i = month_index(dt.datetime(2027, m, 15, 12))
    return KAN[i % 10] + SHI[i % 12]


def main():
    base = json.load(open(os.path.join(DATA, "base_366.json"), encoding="utf-8"))
    table = planet_table()
    raw = {}
    for k, r in base.items():
        natal = r["sun_lon"]
        months = {m: {"all": 0.0, **{n: 0.0 for n in P}, "hits": {}} for m in range(1, 13)}
        ndays = {m: 0 for m in range(1, 13)}
        for d, pos in table:
            ndays[d.month] += 1
            for n, L in pos.items():
                a, c = aspect_contrib(n, L, natal)
                if a is not None:
                    months[d.month]["all"] += c
                    months[d.month][n] += c
                    months[d.month]["hits"].setdefault(f"{n}{a}", 0)
                    months[d.month]["hits"][f"{n}{a}"] += 1
        for m in months:
            for key in ["all", *P]:
                months[m][key] /= ndays[m]
        raw[k] = months
    # 正規化の基準 S：366日×12か月の |raw| の99パーセンタイル（1回だけ決める）
    vals = sorted(abs(raw[k][m]["all"]) for k in raw for m in range(1, 13))
    S = vals[int(len(vals) * .99) - 1]
    clamp = lambda x: max(0, min(100, round(x)))
    mk = {m: month_kanshi(m) for m in range(1, 13)}
    out = {"_meta": {"S": S, "month_kanshi": mk}}
    for k, r in base.items():
        me5 = ELEM5[r["element"]]
        rec = {"astro": [], "num": [], "gogyo": [], "total": [], "fields": {f: [] for f in FIELD_PLANET},
               "astro_hits": [], "gogyo_rel": []}
        for m in range(1, 13):
            a = clamp(astro_scale(raw[k][m]["all"] / S))
            pm = r["pm2027"][str(m)]
            n = PM_SCORE[pm] + (5 if pm == r["birthday_number"] or (r["birthday_number"] in (11, 22) and pm == r["birthday_number"] % 9) else 0)
            ks = mk[m]
            rk, rs = relation(me5, KAN5[KAN.index(ks[0])]), relation(me5, SHI5[ks[1]])
            g = round((REL_SCORE[rk] + REL_SCORE[rs]) / 2)
            rec["astro"].append(a); rec["num"].append(n); rec["gogyo"].append(g)
            rec["total"].append(round((a + n + g) / 3))
            rec["astro_hits"].append(sorted(raw[k][m]["hits"], key=lambda h: -raw[k][m]["hits"][h]))
            rec["gogyo_rel"].append([ks, rk, rs])
            for f, wp in FIELD_PLANET.items():
                s = sum(raw[k][m][p] * w for p, w in wp.items()) / sum(wp.values()) * 3  # 天体を絞った分、総和より小さくなるので3倍で総合と同じ程度の幅に
                v = astro_scale(s / S + FIELD_PM[f].get(pm, 0) / 40)  # 数秘の追い風も tanh の中で足す
                if f in ("健康", "人間関係"):
                    v = v * .8 + g * .2
                rec["fields"][f].append(clamp(v))
        out[k] = rec
    # ◎○△：総合の全体分布（366×12）の上位25%＝◎、下位25%＝△
    allt = sorted(t for k, v in out.items() if k != "_meta" for t in v["total"])
    q75, q25 = allt[int(len(allt) * .75)], allt[int(len(allt) * .25)]
    out["_meta"].update({"q_top": q75, "q_bottom": q25})
    for k, v in out.items():
        if k == "_meta": continue
        marks = ["◎" if t >= q75 else "△" if t < q25 else "○" for t in v["total"]]
        # ページ内に◎2つ・△1つを保証する規則：足りなければその人の中で上位2か月を◎、最下位を△にする
        order = sorted(range(12), key=lambda i: (-v["total"][i], i))
        if marks.count("◎") < 2:
            for i in order[:2]: marks[i] = "◎"
        if marks.count("△") < 1:
            marks[order[-1]] = "△"
        v["marks"] = marks
        v["peak_months"] = [i + 1 for i in order[:3]]
        v["low_months"] = [i + 1 for i in order[-3:][::-1]]
        v["field_peak"] = {f: max(range(12), key=lambda i: (s[i], -i)) + 1 for f, s in v["fields"].items()}
        v["field_low"] = {f: min(range(12), key=lambda i: (s[i], i)) + 1 for f, s in v["fields"].items()}
    json.dump(out, open(os.path.join(DATA, "scores_366.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=0)
    return out


if __name__ == "__main__":
    o = main()
    print(o["_meta"])
    for k in ["0101", "0102", "0120", "0715"]:
        v = o[k]
        print(k, "総合", v["total"], v["marks"], "山", v["peak_months"], "谷", v["low_months"])
        print("   星", v["astro"], "数", v["num"], "五", v["gogyo"])
