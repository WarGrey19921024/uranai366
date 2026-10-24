"""2027年の吉日（暦注）を計算する（2026-10-25）。
- 日の干支：calc_kanshi_kyusei.day_index（1900-01-01=甲戌）
- 節月：節入りの日から新しい月（暦注の一般的な扱い）。setsuiri_1900_2100.json
- 一粒万倍日：節月ごとの十二支（寅月=丑・午、卯月=酉・寅、辰月=子・卯、巳月=卯・辰、午月=巳・午、未月=酉・午、
  申月=子・未、酉月=卯・申、戌月=午・酉、亥月=酉・戌、子月=亥・子、丑月=卯・子）
- 天赦日：春（立春〜立夏の前日）戊寅、夏（立夏〜）甲午、秋（立秋〜）戊申、冬（立冬〜）甲子
- 六曜：旧暦の（月＋日）% 6 → 0大安 1赤口 2先勝 3友引 4先負 5仏滅（閏月は同じ月の数で数える）
- 不成就日：旧暦の月ごとの日（1・7月=3,11,19,27／2・8月=2,10,18,26／3・9月=1,9,17,25／4・10月=4,12,20,28／5・11月=5,13,21,29／6・12月=6,14,22,30）
- 寅の日・巳の日・己巳の日・甲子の日：日の干支から
出力：data/kichijitsu_2027.json"""
import json, os, sys, datetime as dt
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import calc_kanshi_kyusei as K
DATA = os.path.join(HERE, "..", "data")
SET = json.load(open(os.path.join(DATA, "setsuiri_1900_2100.json"), encoding="utf-8"))
KYU = json.load(open(os.path.join(DATA, "kyureki_1900_2030.json"), encoding="utf-8"))
MANBAI = {2: "丑午", 3: "酉寅", 4: "子卯", 5: "卯辰", 6: "巳午", 7: "酉午", 8: "子未", 9: "卯申", 10: "午酉", 11: "酉戌", 0: "亥子", 1: "卯子"}
ROKUYO = ["大安", "赤口", "先勝", "友引", "先負", "仏滅"]
FUJOJU = {1: (3, 11, 19, 27), 2: (2, 10, 18, 26), 3: (1, 9, 17, 25), 4: (4, 12, 20, 28), 5: (5, 13, 21, 29), 6: (6, 14, 22, 30)}

def setsu_list(y):
    out = []
    for yy in (y - 1, y):
        for name, t in SET[str(yy)].items():
            out.append((dt.date.fromisoformat(t[:10]), name))
    return sorted(out)

def main(y=2027):
    sl = setsu_list(y); res = []
    d = dt.date(y, 1, 1)
    while d.year == y:
        cur = [n for (sd, n) in sl if sd <= d][-1]
        br = K.SETSU_BRANCH[cur]
        kan = K.kanshi(K.day_index(d))
        season = {"立春": "春", "啓蟄": "春", "清明": "春", "立夏": "夏", "芒種": "夏", "小暑": "夏", "立秋": "秋", "白露": "秋", "寒露": "秋", "立冬": "冬", "大雪": "冬", "小寒": "冬"}[cur]
        ly, lm, leap, ld = KYU[d.isoformat()]
        tags = []
        if kan[1] in MANBAI[br]: tags.append("一粒万倍日")
        if kan == {"春": "戊寅", "夏": "甲午", "秋": "戊申", "冬": "甲子"}[season]: tags.append("天赦日")
        if kan[1] == "寅": tags.append("寅の日")
        if kan[1] == "巳": tags.append("巳の日")
        if kan == "己巳": tags.append("己巳の日")
        if kan == "甲子": tags.append("甲子の日")
        rk = ROKUYO[(lm + ld) % 6]
        if rk == "大安": tags.append("大安")
        if ld in FUJOJU[(lm - 1) % 6 + 1]: tags.append("不成就日")
        res.append({"date": d.isoformat(), "wd": "月火水木金土日"[d.weekday()], "kanshi": kan, "rokuyo": rk, "lunar": f"{'閏' if leap else ''}{lm}/{ld}", "setsu": cur, "tags": tags})
        d += dt.timedelta(days=1)
    json.dump(res, open(os.path.join(DATA, f"kichijitsu_{y}.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=0)
    return res

if __name__ == "__main__":
    r = main()
    for t in ["天赦日", "一粒万倍日", "寅の日", "巳の日", "己巳の日", "甲子の日", "大安", "不成就日"]:
        print(t, sum(t in x["tags"] for x in r))
    print("天赦日:", [x["date"] for x in r if "天赦日" in x["tags"]])
    print("天赦日+万倍:", [x["date"] for x in r if "天赦日" in x["tags"] and "一粒万倍日" in x["tags"]])
    print("一粒万倍日 1月:", [x["date"][5:] for x in r if "一粒万倍日" in x["tags"] and x["date"][5:7]=="01"])
