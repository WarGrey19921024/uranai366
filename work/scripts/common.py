"""共通：天文計算の土台（pyswisseph・暦ファイル不要のMoshier方式）。
環境づくり（Debian系でpipのビルドが失敗する場合は仮想環境で）:
  python3 -m venv .venv && .venv/bin/pip install -U pip setuptools wheel && .venv/bin/pip install -r work/scripts/requirements.txt
"""
import datetime as dt
import swisseph as swe

FLAG = swe.FLG_MOSEPH | swe.FLG_SPEED
JST = dt.timezone(dt.timedelta(hours=9))
SIGNS = ["牡羊座", "牡牛座", "双子座", "蟹座", "獅子座", "乙女座",
         "天秤座", "蠍座", "射手座", "山羊座", "水瓶座", "魚座"]
PLANETS = {"太陽": swe.SUN, "月": swe.MOON, "水星": swe.MERCURY, "金星": swe.VENUS,
           "火星": swe.MARS, "木星": swe.JUPITER, "土星": swe.SATURN,
           "天王星": swe.URANUS, "海王星": swe.NEPTUNE, "冥王星": swe.PLUTO}


def jd_from_jst(d: dt.datetime) -> float:
    u = d.astimezone(dt.timezone.utc)
    return swe.julday(u.year, u.month, u.day, u.hour + u.minute / 60 + u.second / 3600)


def jst_from_jd(jd: float, round_min: bool = True) -> dt.datetime:
    """JDをJSTに。round_min=True で分に四捨五入（国立天文台の暦要項と同じ表示）"""
    y, m, d, h = swe.revjul(jd)
    base = dt.datetime(y, m, d, tzinfo=dt.timezone.utc) + dt.timedelta(hours=h)
    if round_min:
        base = (base + dt.timedelta(seconds=30)).replace(second=0, microsecond=0)
    return base.astimezone(JST)


def lon(jd: float, body=swe.SUN) -> float:
    """視黄経（真の春分点・光行差込み＝暦の標準）"""
    return swe.calc_ut(jd, body, FLAG)[0][0]


def speed(jd: float, body) -> float:
    return swe.calc_ut(jd, body, FLAG)[0][3]


def _angdiff(a, b):
    return (a - b + 180) % 360 - 180


def find_lon(target: float, jd0: float, jd1: float, body=swe.SUN, step=0.5):
    """[jd0,jd1)で天体の黄経がtargetを（順行方向に）通過する時刻をすべて返す"""
    out = []
    jd = jd0
    prev = _angdiff(lon(jd, body), target)
    while jd < jd1:
        nj = min(jd + step, jd1)
        cur = _angdiff(lon(nj, body), target)
        if prev < 0 <= cur and abs(cur - prev) < 90:
            a, b = jd, nj
            for _ in range(60):
                mid = (a + b) / 2
                if _angdiff(lon(mid, body), target) < 0:
                    a = mid
                else:
                    b = mid
            out.append((a + b) / 2)
        elif prev >= 0 > cur and abs(cur - prev) < 90:  # 逆行で戻る通過
            a, b = jd, nj
            for _ in range(60):
                mid = (a + b) / 2
                if _angdiff(lon(mid, body), target) >= 0:
                    a = mid
                else:
                    b = mid
            out.append(-(a + b) / 2)  # 負号で「逆行での通過」を示す
        prev, jd = cur, nj
    return out


def new_moons(jd0: float, jd1: float):
    """朔（太陽と月の黄経差0）の時刻"""
    res = []
    jd = jd0
    f = lambda t: _angdiff(lon(t, swe.MOON), lon(t, swe.SUN))
    prev = f(jd)
    while jd < jd1:
        nj = jd + 1
        cur = f(nj)
        if prev < 0 <= cur:
            a, b = jd, nj
            for _ in range(50):
                m = (a + b) / 2
                if f(m) < 0:
                    a = m
                else:
                    b = m
            res.append((a + b) / 2)
        prev, jd = cur, nj
    return res
