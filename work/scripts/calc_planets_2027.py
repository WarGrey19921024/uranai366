"""2027年の天体イベントを計算する（pyswisseph・Moshier）。
- 太陽〜冥王星の星座移動（逆行で戻る移動も含む）
- 水星・金星・火星・木星・土星などの逆行期間（留の日時）
- 日食・月食（世界のどこかで起きるもの＋日本で見えるか）
出力: work/data/planets_2027.json
"""
import json, os, datetime as dt
import swisseph as swe
from common import (jd_from_jst, jst_from_jd, lon, speed, find_lon, SIGNS, PLANETS, JST, FLAG)

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "data")
Y0 = jd_from_jst(dt.datetime(2027, 1, 1, tzinfo=JST))
Y1 = jd_from_jst(dt.datetime(2028, 1, 1, tzinfo=JST))
fmt = lambda jd: jst_from_jd(jd).strftime("%Y-%m-%d %H:%M")


def ingresses(name, body):
    res = []
    for i in range(12):
        for j in find_lon(i * 30, Y0, Y1, body, step=0.25 if body == swe.MOON else 1.0):
            retro = j < 0
            jd = abs(j)
            to = SIGNS[i] if not retro else SIGNS[(i - 1) % 12]
            res.append({"planet": name, "jst": fmt(jd), "jd": jd, "to": to, "retrograde": retro})
    return sorted(res, key=lambda r: r["jd"])


def stations(name, body):
    res = []
    jd, prev = Y0 - 1, speed(Y0 - 1, body)
    while jd < Y1 + 1:
        nj = jd + 0.5
        cur = speed(nj, body)
        if (prev > 0) != (cur > 0):
            a, b = jd, nj
            for _ in range(50):
                m = (a + b) / 2
                if (speed(m, body) > 0) == (prev > 0):
                    a = m
                else:
                    b = m
            t = (a + b) / 2
            L = lon(t, body)
            res.append({"planet": name, "jst": fmt(t), "jd": t,
                        "kind": "逆行開始" if prev > 0 else "順行に戻る",
                        "sign": SIGNS[int(L // 30)], "deg": round(L % 30, 2)})
        prev, jd = cur, nj
    return res


def eclipses():
    res = []
    t = Y0
    while True:
        r, tret = swe.sol_eclipse_when_glob(t, swe.FLG_MOSEPH, 0)
        if tret[0] >= Y1:
            break
        kind = ("皆既" if r & swe.ECL_TOTAL else "金環" if r & swe.ECL_ANNULAR else
                "金環皆既" if r & swe.ECL_ANNULAR_TOTAL else "部分")
        L = lon(tret[0])
        res.append({"type": f"{kind}日食", "jst_max": fmt(tret[0]), "sign": SIGNS[int(L // 30)],
                    "deg": round(L % 30, 2), "japan": japan_solar(tret[0])})
        t = tret[0] + 20
    t = Y0
    while True:
        r, tret = swe.lun_eclipse_when(t, swe.FLG_MOSEPH, 0)
        if tret[0] >= Y1:
            break
        kind = "皆既" if r & swe.ECL_TOTAL else "部分" if r & swe.ECL_PARTIAL else "半影"
        L = lon(tret[0], swe.MOON)
        res.append({"type": f"{kind}月食", "jst_max": fmt(tret[0]), "sign": SIGNS[int(L // 30)],
                    "deg": round(L % 30, 2), "japan": japan_lunar(tret)})
        t = tret[0] + 20
    return sorted(res, key=lambda r: r["jst_max"])


TOKYO = (139.7414, 35.6581, 0)


def japan_solar(jd_max):
    try:
        r, tret, attr = swe.sol_eclipse_when_loc(jd_max - 2, TOKYO, swe.FLG_MOSEPH)
        if abs(tret[0] - jd_max) < 1 and r:
            return f"東京で見える（食分{attr[0]:.2f}・最大{fmt(tret[0])}）"
    except Exception as e:
        return f"判定不可({e})"
    return "東京では見えない"


def japan_lunar(tret):
    # 東京で月が地平線より上にあるかを、食の最大時刻で判定
    jd = tret[0]
    az = swe.azalt(jd, swe.ECL2HOR, TOKYO, 0, 0, swe.calc_ut(jd, swe.MOON, FLAG)[0][:3])
    return "東京で見える（最大時に月が地平線上）" if az[1] > 0 else "東京では最大時に月が地平線下"


if __name__ == "__main__":
    out = {"ingress": [], "stations": [], "eclipses": eclipses(),
           "start_positions": {}}
    for n, b in PLANETS.items():
        if n == "月":
            continue
        L = lon(Y0, b)
        out["start_positions"][n] = f"{SIGNS[int(L//30)]} {L%30:.1f}度"
        out["ingress"] += ingresses(n, b)
        if n != "太陽":
            out["stations"] += stations(n, b)
    for k in ("ingress", "stations"):
        for r in out[k]:
            r.pop("jd", None)
    os.makedirs(DATA, exist_ok=True)
    with open(os.path.join(DATA, "planets_2027.json"), "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    print("2027-01-01 0時JSTの位置:", out["start_positions"])
    for r in out["ingress"]:
        if r["planet"] != "太陽":
            print(r["jst"], r["planet"], "→", r["to"], "(逆行で戻る)" if r["retrograde"] else "")
    for r in out["stations"]:
        print(r["jst"], r["planet"], r["kind"], r["sign"], r["deg"])
    for r in out["eclipses"]:
        print(r)
