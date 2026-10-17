"""12星座ページの文章の点検：
1. 文中の「M月D日」が、天体の出来事（星座入り・逆行/順行・食）か星座の期間の日付のどれかと合うか
2. 星座どうしで同じ言い回し（14文字以上の一致）がないか
3. 「！」が無いか・字数のめやす"""
import glob, json, os, re, sys, itertools
W = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
P = json.load(open(os.path.join(W, "data", "planets_2027.json"), encoding="utf-8"))
ok = set()
for x in P["ingress"] + P["stations"]:
    ok.add((int(x["jst"][5:7]), int(x["jst"][8:10])))
for e in P["eclipses"]:
    ok.add((int(e["jst_max"][5:7]), int(e["jst_max"][8:10])))
S = json.load(open(os.path.join(W, "data", "signs_2027.json"), encoding="utf-8"))
for p in S["phases"]:
    ok.add((int(p["date"][5:7]), int(p["date"][8:10])))
PERIOD_OK = {(3, 20), (3, 21), (4, 19), (4, 20), (5, 20), (5, 21), (6, 21), (6, 22), (7, 22), (7, 23), (8, 22), (8, 23), (9, 22), (9, 23), (10, 23), (10, 24),
             (11, 22), (11, 23), (12, 21), (12, 22), (1, 19), (1, 20), (2, 18), (2, 19), (1, 1), (12, 31)}


def texts(d):
    out = [d["catch"], d["lead"], d["year"], d["jupiter"], d["saturn"], d["personality"]]
    out += [v for _, v in d["keywords"]] + list(d["months"].values()) + list(d["fields"].values())
    out += [v for _, v in d["compat"]["good"]] + [v for _, v in d["compat"]["care"]] + [v for _, v in d["tips"]] + [a for _, a in d["faq"]]
    return out


def main():
    files = sorted(glob.glob(os.path.join(W, "text", "signs", "*.json")))
    T = {os.path.basename(f)[:-5]: json.load(open(f, encoding="utf-8")) for f in files}
    bad = 0
    for en, d in T.items():
        alltxt = "\n".join(texts(d))
        if "！" in alltxt:
            print(en, "！がある"); bad += 1
        # 月の文：その月のどちらかの日付も含めて
        for m, t in d["months"].items():
            for mm, dd in re.findall(r"(\d{1,2})月(\d{1,2})日", t):
                if (int(mm), int(dd)) not in ok | PERIOD_OK:
                    print(en, f"{m}月の文", f"{mm}月{dd}日 は天体の出来事に無い"); bad += 1
            for dd in re.findall(r"(?<![月\d])(\d{1,2})日", t):
                if (int(m), int(dd)) not in ok | PERIOD_OK:
                    print(en, f"{m}月の文", f"{dd}日 は天体の出来事に無い"); bad += 1
        for mm, dd in re.findall(r"(\d{1,2})月(\d{1,2})日", alltxt):
            if (int(mm), int(dd)) not in ok | PERIOD_OK:
                print(en, f"{mm}月{dd}日 は天体の出来事に無い"); bad += 1
    # 14字一致
    N = 14
    grams = {}
    for en, d in T.items():
        s = re.sub(r"(牡羊|牡牛|双子|蟹|獅子|乙女|天秤|蠍|射手|山羊|水瓶|魚)座", "〇座", "".join(texts(d)))
        s = re.sub(r"\d+", "#", s)
        for i in range(len(s) - N):
            grams.setdefault(s[i:i + N], set()).add(en)
    dup = [(g, sorted(v)) for g, v in grams.items() if len(v) > 1 and not re.search(r"[（）「」]", g)]
    print("14字の一致：", len(dup))
    for g, v in dup[:40]:
        print("  ", g, v)
    print("点検終わり。問題", bad, "件")


if __name__ == "__main__":
    main()
