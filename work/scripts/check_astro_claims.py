"""12か月の運勢の文に出てくる「〇〇座の金星」「火星が〇〇座」などが、その月の実際の星の位置と合うかを確かめる（2026-10-22 点検の指摘から）。
その月のどの日にもその星座にいなければ「合わない」。結果：reports/astro_claims.md と reports/astro_claims.json"""
import calendar, datetime as dt, glob, json, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import SIGNS, PLANETS, JST, jd_from_jst, lon

W = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
PL = ["太陽", "水星", "金星", "火星", "木星", "土星"]
SG = "|".join(SIGNS)
PLR = "|".join(PL)
SEQ = rf"(?:{PLR})(?:[、と](?:{PLR}))*"
PAT = [re.compile(rf"({SG})の({SEQ})"),
       re.compile(rf"({SEQ})(?:が|は)({SG})(?:に|を|で|へ|入り|に入)")]
OWN = re.compile(rf"({SEQ})が(?:あなたの)?(?:太陽|星座)(?:に|と)重な")
OPP = re.compile(rf"(?:({SG})の)?({SEQ})が(?:向かい|向こう正面)")
_cache = {}


def signs_in_month(p, m):
    k = (p, m)
    if k not in _cache:
        s = set()
        for d in range(1, calendar.monthrange(2027, m)[1] + 1):
            for h in (0, 12):
                s.add(SIGNS[int(lon(jd_from_jst(dt.datetime(2027, m, d, h, tzinfo=JST)), PLANETS[p]) // 30)])
        _cache[k] = s
    return _cache[k]


def main():
    bad = []
    for f in sorted(glob.glob(os.path.join(W, "text", "*", "[0-9][0-9][0-9][0-9].json"))):
        mmdd = os.path.basename(f)[:4]
        months = (json.load(open(f, encoding="utf-8")).get("y2027") or {}).get("months") or []
        for i, t in enumerate(months):
            t = t if isinstance(t, str) else json.dumps(t, ensure_ascii=False)
            for pat in PAT:
                for mm in pat.finditer(t):
                    a, b = mm.group(1), mm.group(2)
                    sign, pls = (a, b) if a in SIGNS else (b, a)
                    for p in re.split(r"[、と]", pls):
                        if sign not in signs_in_month(p, i + 1):
                            bad.append({"mmdd": mmdd, "month": i + 1, "claim": mm.group(0), "planet": p, "sign": sign,
                                        "actual": sorted(signs_in_month(p, i + 1), key=SIGNS.index), "text": t})
            own = SIGNS[int(lon(jd_from_jst(dt.datetime(2027, int(mmdd[:2]), min(int(mmdd[2:]), 28 if mmdd[:2] == "02" else 31), 12, tzinfo=JST))) // 30)]
            opp = SIGNS[(SIGNS.index(own) + 6) % 12]
            for rx, need, kind in ((OWN, own, "あなたの星座"), (OPP, opp, "向かい側")):
                for mm in rx.finditer(t):
                    gs = mm.groups()
                    sign = gs[0] if kind == "向かい側" else None
                    pls = gs[-1]
                    if sign and sign != need:
                        bad.append({"mmdd": mmdd, "month": i + 1, "claim": mm.group(0), "planet": "-", "sign": sign,
                                    "actual": [f"{kind}は{need}"], "text": t})
                        continue
                    for p in re.split(r"[、と]", pls):
                        if need not in signs_in_month(p, i + 1):
                            bad.append({"mmdd": mmdd, "month": i + 1, "claim": mm.group(0), "planet": p, "sign": f"{kind}（{need}）",
                                        "actual": sorted(signs_in_month(p, i + 1), key=SIGNS.index), "text": t})
    json.dump(bad, open(os.path.join(W, "reports", "astro_claims.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    L = ["# 12か月の運勢の星の位置の点検", "", f"合わない：{len(bad)}件（{len({b['mmdd'] for b in bad})}日）", "",
         "| 日 | 月 | 文の言い方 | 実際のその月 |", "|---|---|---|---|"]
    L += [f"| {b['mmdd']} | {b['month']}月 | {b['claim']} | {b['planet']}は{'・'.join(b['actual'])} |" for b in bad]
    open(os.path.join(W, "reports", "astro_claims.md"), "w", encoding="utf-8").write("\n".join(L) + "\n")
    print(f"合わない：{len(bad)}件（{len({b['mmdd'] for b in bad})}日）")


if __name__ == "__main__":
    main()
