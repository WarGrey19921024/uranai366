"""12星座ページ（2027年版）の数字 → work/data/signs_2027.json
誕生日占い（366日・build_scores.py）とは考え方を分ける：
  366日 … 誕生日の太陽の「度数」に、天体が作る角度（アスペクト）で見る＝その日生まれの人の運勢
  12星座 … 天体が自分の星座から数えて「何番目の部屋（ハウス）」にいるか、星座どうしの角度で見る＝星座全体の運勢
           （太陽星座を1番目の部屋とする「ソーラーサイン・ハウス」。雑誌の星座占いと同じ考え方）
計算は pyswisseph（Moshier）。2027年の毎日12:00（日本時間）の天体の星座で見る。手で数字を直さない。
規則は work/knowledge/13_12星座ページの規則.md に同じ内容を書く。"""
import json, os, datetime as dt, statistics as st
import swisseph as swe
from common import jd_from_jst, lon, speed, JST, SIGNS

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "data")
P = {"太陽": swe.SUN, "水星": swe.MERCURY, "金星": swe.VENUS, "火星": swe.MARS, "木星": swe.JUPITER, "土星": swe.SATURN}
# 星座どうしの角度（星座の数で0〜6つ離れ）ごとの点
SEP_PT = {0: 1.0, 1: -0.15, 2: 0.5, 3: -0.7, 4: 1.0, 5: -0.25, 6: -0.6}
W = {"太陽": 1.0, "水星": 0.4, "金星": 0.8, "火星": 0.8, "木星": 0.9, "土星": 0.7}
SAT_FLIP = {0: -0.5, 4: 0.5, 2: 0.4, 3: -0.9, 6: -0.7}  # 土星は重なりが試練寄り
# 部屋（1〜12）ごとの分野の加点：天体がその部屋にいると追い風
FIELD = {
    "恋愛": {"金星": {5: .9, 7: .8, 1: .5, 11: .3}, "太陽": {5: .5, 7: .3}, "火星": {5: .4, 7: -.2}, "木星": {5: .7, 7: .6}},
    "仕事": {"太陽": {10: .7, 6: .4}, "火星": {10: .6, 6: .5}, "木星": {10: .9, 6: .5}, "土星": {10: .3, 6: .2}, "水星": {3: .3, 6: .3, 10: .3}},
    "金運": {"金星": {2: .8, 8: .5}, "木星": {2: 1.0, 8: .7}, "太陽": {2: .4}, "土星": {2: -.4, 8: -.3}},
    "健康": {"太陽": {1: .4, 6: .3}, "火星": {1: .3, 6: .2, 12: -.4}, "土星": {6: -.4, 12: -.4, 1: -.3}, "木星": {1: .4, 6: .3}},
}
MOON_MARK = {0: "◎", 4: "◎", 2: "○", 1: "・", 5: "・", 3: "△", 6: "△"}
MOON_WHY = {0: "月があなたの星座に", 4: "月が同じエレメントの星座に", 2: "月が相性のいい星座に", 1: "月がとなりの星座に",
            5: "月が少し遠い星座に", 3: "月が直角の星座に", 6: "月が向かい側の星座に"}
HOUSE_NAME = {1: "自分自身", 2: "お金・持ち物", 3: "学び・会話", 4: "家・家族", 5: "恋愛・楽しみ", 6: "仕事の進め方・健康",
              7: "パートナー・対人関係", 8: "深い縁・受け継ぐもの", 9: "旅・学問", 10: "仕事・評価", 11: "仲間・夢", 12: "休息・心の奥"}


def sign_of(l):
    return int(l // 30) % 12


def sep(a, b):
    d = (a - b) % 12
    return min(d, 12 - d)


def day_positions(d):
    jd = jd_from_jst(dt.datetime(d.year, d.month, d.day, 12, 0, tzinfo=JST))
    pos = {n: sign_of(lon(jd, b)) for n, b in P.items()}
    retro = {n: speed(jd, b) < 0 for n, b in P.items() if n not in ("太陽",)}
    moon = lon(jd, swe.MOON)
    sun = lon(jd, swe.SUN)
    return pos, retro, sign_of(moon), (moon - sun) % 360


def score_day(s, pos, retro):
    tot = 0
    for n, ps in pos.items():
        k = sep(ps, s)
        pt = SAT_FLIP.get(k, SEP_PT[k]) if n == "土星" else SEP_PT[k]
        tot += W[n] * pt
    if retro.get("水星"):
        tot -= 0.25
    fields = {}
    for f, rule in FIELD.items():
        v = tot * 0.5
        for n, hs in rule.items():
            h = (pos[n] - s) % 12 + 1
            v += hs.get(h, 0)
        fields[f] = v
    return tot, fields


def to100(vals):
    """順位で 35〜95 に並べる（144個＝12星座×12か月の中での位置）"""
    srt = sorted(vals)
    n = len(srt) - 1
    return [round(35 + 60 * srt.index(v) / n) for v in vals]


def main():
    days = [dt.date(2027, 1, 1) + dt.timedelta(i) for i in range(365)]
    P_DAY = [day_positions(d) for d in days]
    raw = {s: {m: {"総合": [], "恋愛": [], "仕事": [], "金運": [], "健康": []} for m in range(1, 13)} for s in range(12)}
    for d, (pos, retro, ms, el) in zip(days, P_DAY):
        for s in range(12):
            t, f = score_day(s, pos, retro)
            r = raw[s][d.month]
            r["総合"].append(t)
            for k, v in f.items():
                r[k].append(v)
    out = {"note": "calc_signs_2027.py で計算。毎日12:00（日本時間）の天体の星座で見る。点は12星座×12か月の中での順位を35〜95に並べたもの（手で直さない）", "signs": {}}
    for key in ["総合", "恋愛", "仕事", "金運", "健康"]:
        flat = [(s, m, st.mean(raw[s][m][key])) for s in range(12) for m in range(1, 13)]
        sc = to100([x[2] for x in flat])
        for (s, m, _), v in zip(flat, sc):
            out["signs"].setdefault(SIGNS[s], {"months": {mm: {} for mm in range(1, 13)}})["months"][m][key] = v
    # 月ごとの12星座の順位（総合）
    rank = {}
    for m in range(1, 13):
        order = sorted(range(12), key=lambda s: -st.mean(raw[s][m]["総合"]))
        rank[m] = [SIGNS[s] for s in order]
    out["rank"] = rank
    # 毎日の月（ラッキーデーのカレンダー）と、外側の天体の部屋の移り変わり
    for s in range(12):
        sg = out["signs"][SIGNS[s]]
        cal = []
        for d, (pos, retro, ms, el) in zip(days, P_DAY):
            k = sep(ms, s)
            ph = ""
            cal.append([d.isoformat(), MOON_MARK[k], SIGNS[ms], k])
        sg["moon"] = cal
        periods = {}
        for n in ("木星", "土星", "火星", "金星"):
            seq, cur, start = [], None, None
            for d, (pos, retro, ms, el) in zip(days, P_DAY):
                h = (pos[n] - s) % 12 + 1
                if h != cur:
                    if cur is not None:
                        seq.append({"from": start, "to": (d - dt.timedelta(1)).isoformat(), "house": cur, "sign": SIGNS[(s + cur - 1) % 12], "theme": HOUSE_NAME[cur]})
                    cur, start = h, d.isoformat()
            seq.append({"from": start, "to": days[-1].isoformat(), "house": cur, "sign": SIGNS[(s + cur - 1) % 12], "theme": HOUSE_NAME[cur]})
            periods[n] = seq
        sg["houses"] = periods
        good = [d for d, mk, _, k in cal if k in (0, 4)]
        sg["moon_good_days"] = len(good)
    # 新月・満月（ラッキーデーのカレンダーの印）
    phases = []
    for d, (pos, retro, ms, el) in zip(days, P_DAY):
        pass
    jd0 = jd_from_jst(dt.datetime(2027, 1, 1, 0, 0, tzinfo=JST))
    for target, name in ((0, "新月"), (180, "満月")):
        from common import find_lon  # noqa
        jd = jd0
        while jd < jd0 + 366:
            el0 = (lon(jd, swe.MOON) - lon(jd, swe.SUN)) % 360
            el1 = (lon(jd + 1, swe.MOON) - lon(jd + 1, swe.SUN)) % 360
            a = (el0 - target) % 360
            b = (el1 - target) % 360
            if a > 300 and b < 60:
                lo, hi = jd, jd + 1
                for _ in range(40):
                    mid = (lo + hi) / 2
                    if (lon(mid, swe.MOON) - lon(mid, swe.SUN) - target) % 360 > 180:
                        lo = mid
                    else:
                        hi = mid
                y, mo, dd, h = swe.revjul(lo)
                t = (dt.datetime(y, mo, dd, tzinfo=dt.timezone.utc) + dt.timedelta(hours=h)).astimezone(JST)
                if t.year == 2027:
                    phases.append({"date": t.date().isoformat(), "kind": name, "sign": SIGNS[sign_of(lon(lo, swe.MOON))]})
            jd += 1
    out["phases"] = sorted(phases, key=lambda x: x["date"])
    json.dump(out, open(os.path.join(DATA, "signs_2027.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("ok", len(out["phases"]))
    for sg in SIGNS[:3]:
        print(sg, [out["signs"][sg]["months"][m]["総合"] for m in range(1, 13)])
        print(" 木星", [(x["from"], x["house"]) for x in out["signs"][sg]["houses"]["木星"]], "土星", [(x["from"], x["house"]) for x in out["signs"][sg]["houses"]["土星"]])


if __name__ == "__main__":
    main()
