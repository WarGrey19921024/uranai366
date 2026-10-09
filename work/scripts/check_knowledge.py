"""知識ベースの計算を、外部の既知の値と照合する。結果は work/reports/knowledge_check_calc.md
外部の値は、この環境で確認できた出典（検索結果）から転記したもの。出典は各行に記す。"""
import json, os, datetime as dt
from calc_sekki import kou_list
from calc_kanshi_kyusei import kanshi, day_index, year_index, month_index, honmei, ban, KYUSEI
from calc_maya_num_bio import kin
HERE = os.path.dirname(os.path.abspath(__file__))
REP = os.path.join(HERE, "..", "reports")
NAOJ = "国立天文台 令和9年(2027)暦要項 https://eco.mtk.nao.ac.jp/koyomi/yoko/2027/rekiyou272.html"
SEKKI_NAOJ = {"小寒": "01-05 23:10", "大寒": "01-20 16:30", "立春": "02-04 10:46", "雨水": "02-19 06:33",
              "啓蟄": "03-06 04:40", "春分": "03-21 05:25", "清明": "04-05 09:17", "穀雨": "04-20 16:18",
              "立夏": "05-06 02:25", "小満": "05-21 15:18", "芒種": "06-06 06:26", "夏至": "06-21 23:11",
              "小暑": "07-07 16:37", "大暑": "07-23 10:05", "立秋": "08-08 02:27", "処暑": "08-23 17:14",
              "白露": "09-08 05:28", "秋分": "09-23 15:02", "寒露": "10-08 21:17", "霜降": "10-24 00:33",
              "立冬": "11-08 00:39", "小雪": "11-22 22:16", "大雪": "12-07 17:38", "冬至": "12-22 11:42"}
rows, ok, ng = [], 0, 0


def add(item, calc, ref, src, judge=None):
    global ok, ng
    j = (calc == ref) if judge is None else judge
    ok += j; ng += (not j)
    rows.append(f"| {item} | {calc} | {ref} | {'✅' if j else '⚠'} | {src} |")


# 1) 二十四節気
for r in kou_list(2027):
    if r["sekki"]:
        calc = r["jst"][5:]
        ref = SEKKI_NAOJ[r["sekki"]]
        same_day = calc[:5] == ref[:5]
        tm = lambda s: int(s[6:8]) * 60 + int(s[9:11])
        add(f"節気 {r['sekki']}", calc, ref, NAOJ, same_day and abs(tm(calc) - tm(ref)) <= 1)
# 2) 日食・月食
p = json.load(open(os.path.join(HERE, "..", "data", "planets_2027.json"), encoding="utf-8"))
ECL = {"金環日食": "2027-02-07 01:00", "半影月食": None, "皆既日食": "2027-08-02"}
NASA = "NASA Eclipses During 2027 https://eclipse.gsfc.nasa.gov/OH/OH2027.html"
refs = [("金環日食", "2027-02-07 01:00", "2/6 16:00 UT"), ("半影月食", "2027-02-21 08:13", "2/20 23:13 UT"),
        ("半影月食", "2027-07-19", "7/18 (UT)"), ("皆既日食", "2027-08-02", "8/2 (UT)"), ("半影月食", "2027-08-17", "8/17 (UT)")]
for (typ, ref, note), e in zip(refs, p["eclipses"]):
    add(f"{typ}（{note}）", f"{e['type']} {e['jst_max']}", ref, NASA,
        e["type"] == typ and e["jst_max"].startswith(ref))
# 3) 干支・九星
T = dt.datetime(2027, 1, 1, 12)
add("2027-01-01 の日柱", kanshi(day_index(T.date())), "庚辰", "datedb.net https://datedb.net/calendar/day/20270101/ ・万年暦 wannianli.tianqi.com")
add("2027-01-01 の年柱・月柱", kanshi(year_index(T)) + "・" + kanshi(month_index(T)), "丙午・庚子", "同上（立春基準）")
T2 = dt.datetime(2027, 3, 1, 12)
add("2027年（立春後）の年柱", kanshi(year_index(T2)), "丁未", "同上・一般的な暦")
add("2027年の年の九星", KYUSEI[honmei(T2)], "九紫火星", "KADOKAWA 2027年手帳告知 https://www.kadokawa.co.jp/topics/17669/")
add("2027年盤 北の星（五黄殺）", ban(9)["北"], "五黄土星", "masterseanchan.com fengshui 2027 flying star chart（検索結果）")
# 4) 旧暦
k = json.load(open(os.path.join(HERE, "..", "data", "kyureki_1900_2030.json"), encoding="utf-8"))
for d, ref in [("2024-02-10", "旧正月"), ("2025-01-29", "旧正月"), ("2026-02-17", "旧正月"), ("2027-02-07", "旧正月")]:
    v = k[d]
    add(f"{d} の旧暦", f"{v[0]}年{v[1]}月{v[3]}日", f"{d[:4]}年1月1日", "国立天文台 暦要項の朔（日本時間）による旧正月", v[1] == 1 and v[3] == 1 and not v[2])
for d in ["2024-09-17", "2025-10-06", "2026-09-25", "2027-09-15"]:
    v = k[d]
    add(f"{d}（中秋の名月）の旧暦", f"{v[1]}月{v[3]}日", "8月15日", "国立天文台 暦要項「中秋の名月」", v[1] == 8 and v[3] == 15)
v = k["2025-07-25"]
add("2025年の閏月", f"{'閏' if v[2] else ''}{v[1]}月1日", "閏6月1日", "2025年は閏六月（一般的な暦）", v[2] and v[1] == 6 and v[3] == 1)
# 5) マヤ暦
for d, ref, src in [("2013-07-26", 164, "基準日（試作と同じ）"), ("2012-12-21", 207, "ドリームスペル暦で広く知られる値（青い手・音12）"),
                    ("1987-07-26", 34, "ドリームスペル暦で広く知られる値（白い魔法使い・音8）")]:
    add(f"{d} のKIN", kin(dt.date.fromisoformat(d)), ref, src)

os.makedirs(REP, exist_ok=True)
with open(os.path.join(REP, "knowledge_check_calc.md"), "w", encoding="utf-8") as f:
    f.write(f"# 計算の照合結果（自動）\n\n`python work/scripts/check_knowledge.py` で再生成。一致 {ok} 件／要確認 {ng} 件。\n"
            "節気は「日付が同じ・時刻の差1分以内」を一致とする。\n\n| 項目 | 計算 | 外部の値 | 判定 | 出典 |\n|---|---|---|---|---|\n")
    f.write("\n".join(rows) + "\n")
print(ok, ng)
