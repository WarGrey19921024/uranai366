"""星のこよみ（/hoshi/・/hoshi/mercury-retrograde/）用の天文データ（2026-10-01〜2027-12-31）を計算する（2026-10-18）。
新月・満月（日本時・分に四捨五入）、月のある星座、満月の地心距離（大きく見える満月の判定）、水星・金星・火星の逆行の始まりと終わり（留）。
日食・月食と星座の入れ替わりは planets_2027.json（calc_planets_2027 系の計算結果）を使う。
出力: work/data/hoshi_2027.json"""
import datetime as dt, json, os, sys
import swisseph as swe
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import jd_from_jst, jst_from_jd, lon, speed, JST, SIGNS, new_moons, FLAG, _angdiff  # noqa: E402

WORK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
J0 = jd_from_jst(dt.datetime(2026, 10, 1, tzinfo=JST))
J1 = jd_from_jst(dt.datetime(2028, 1, 1, tzinfo=JST))


def elong(jd):
    return _angdiff(lon(jd, swe.MOON), lon(jd, swe.SUN))


def full_moons(a, b):
    out, jd = [], a
    prev = (elong(jd) % 360)
    while jd < b:
        nj = jd + 0.25
        cur = (elong(nj) % 360)
        if prev < 180 <= cur:
            x, y = jd, nj
            for _ in range(60):
                m = (x + y) / 2
                if (elong(m) % 360) < 180:
                    x = m
                else:
                    y = m
            out.append((x + y) / 2)
        prev, jd = cur, nj
    return out


def sign_deg(l):
    return SIGNS[int(l // 30)], round(l % 30, 2)


def stations(body, a, b):
    out, jd = [], a
    prev = speed(jd, body)
    while jd < b:
        nj = jd + 0.5
        cur = speed(nj, body)
        if (prev > 0) != (cur > 0):
            x, y = jd, nj
            for _ in range(60):
                m = (x + y) / 2
                if (speed(m, body) > 0) == (prev > 0):
                    x = m
                else:
                    y = m
            t = (x + y) / 2
            s, d = sign_deg(lon(t, body))
            out.append({"jst": jst_from_jd(t).strftime("%Y-%m-%d %H:%M"), "kind": "逆行開始" if prev > 0 else "順行に戻る", "sign": s, "deg": d})
        prev, jd = cur, nj
    return out


def main():
    moons = []
    for t in new_moons(J0, J1):
        s, _ = sign_deg(lon(t, swe.MOON))
        moons.append({"kind": "新月", "jst": jst_from_jd(t).strftime("%Y-%m-%d %H:%M"), "sign": s})
    for t in full_moons(J0, J1):
        s, _ = sign_deg(lon(t, swe.MOON))
        dist = swe.calc_ut(t, swe.MOON, FLAG)[0][2] * 149597870.7
        moons.append({"kind": "満月", "jst": jst_from_jd(t).strftime("%Y-%m-%d %H:%M"), "sign": s, "km": round(dist)})
    moons.sort(key=lambda x: x["jst"])
    st = {n: stations(b, J0, J1) for n, b in (("水星", swe.MERCURY), ("金星", swe.VENUS), ("火星", swe.MARS))}
    # 水星逆行の前後の「影の期間」：逆行で戻る範囲（順行に戻る度数〜逆行を始める度数）を、逆行の前に通り始める日と、逆行の後に通り終える日
    from common import find_lon
    ms = st["水星"]
    shadows = []
    for i in range(0, len(ms) - 1, 2):
        r, d = ms[i], ms[i + 1]
        jr = jd_from_jst(dt.datetime.strptime(r["jst"], "%Y-%m-%d %H:%M").replace(tzinfo=JST))
        jdd = jd_from_jst(dt.datetime.strptime(d["jst"], "%Y-%m-%d %H:%M").replace(tzinfo=JST))
        lr, ld = lon(jr, swe.MERCURY), lon(jdd, swe.MERCURY)
        pre = [t for t in find_lon(ld, jr - 60, jr, swe.MERCURY, 0.25) if t > 0]
        post = [t for t in find_lon(lr, jdd, jdd + 60, swe.MERCURY, 0.25) if t > 0]
        shadows.append({"retro": r["jst"], "direct": d["jst"], "pre_start": jst_from_jd(pre[-1]).strftime("%Y-%m-%d") if pre else None,
                        "post_end": jst_from_jd(post[0]).strftime("%Y-%m-%d") if post else None, "from_sign": r["sign"], "to_sign": d["sign"]})
    # 2026年10〜12月の二十四節気（太陽黄経 210°〜270° の15°ごと）
    names = {210: "霜降", 225: "立冬", 240: "小雪", 255: "大雪", 270: "冬至"}
    sk26 = []
    for deg, nm in names.items():
        ts = [t for t in find_lon(deg, J0, jd_from_jst(dt.datetime(2027, 1, 1, tzinfo=JST)), swe.SUN, 1) if t > 0]
        if ts:
            sk26.append({"name": nm, "jst": jst_from_jd(ts[0]).strftime("%Y-%m-%d %H:%M")})
    p27 = json.load(open(os.path.join(WORK, "data", "planets_2027.json"), encoding="utf-8"))
    out = {"note": "calc_hoshi.py（Swiss Ephemeris・Moshier方式）。時刻は日本時で分に四捨五入", "moons": moons, "stations": st,
           "eclipses_2027": p27["eclipses"], "shadows": shadows, "sekki_2026q4": sk26, "ingress_2027": [x for x in p27["ingress"] if x["planet"] in ("木星", "土星", "天王星", "海王星", "冥王星")]}
    json.dump(out, open(os.path.join(WORK, "data", "hoshi_2027.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(shadows, sk26)
    for m in moons[:8]:
        print(m)
    print(st["水星"])
    f27 = [m for m in moons if m["kind"] == "満月" and m["jst"].startswith("2027")]
    print("2027 full moons", len(f27), "min km", min(f27, key=lambda x: x["km"]), "max", max(f27, key=lambda x: x["km"]))


if __name__ == "__main__":
    main()
