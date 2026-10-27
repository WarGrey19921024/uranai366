"""数秘術 2027年の運勢ページ（/unsei-2027/suhi/）の数値 → data/suhi_2027.json
- 2027年の数（パーソナルイヤー PY）＝1けた化（2+0+2+7＋誕生月の各けた＋誕生日の各けた）。マスターは残さない（knowledge/08・build_suhi.py の py2027 と同じ）
- 月の数（パーソナルマンス PM）＝1けた化（PY＋その月）。1月1日切り替え・カレンダーの月（knowledge/08）
- 早見表：誕生日（2/29を含む366日）→ PY
"""
import json, os, sys, datetime as dt

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from build_suhi import py2027  # noqa: E402


def red(n):
    while n > 9:
        n = sum(int(c) for c in str(n))
    return n


def main():
    table = {}
    d = dt.date(2024, 1, 1)
    while d.year == 2024:
        table[f"{d.month:02d}-{d.day:02d}"] = py2027(d.month, d.day)
        d += dt.timedelta(days=1)
    assert table["01-01"] == 4 and table["12-31"] == 9 and table["02-29"] == 6
    out = {"year_sum": 2 + 0 + 2 + 7, "py": {}, "table": table}
    for p in range(1, 10):
        pm = [red(p + m) for m in range(1, 13)]
        days = [k for k, v in table.items() if v == p]
        out["py"][p] = {"pm": pm, "count": len(days)}
        print(p, len(days), pm)
    json.dump(out, open(os.path.join(HERE, "..", "data", "suhi_2027.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main()
