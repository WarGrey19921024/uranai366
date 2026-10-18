"""誕生日ページ366本の横断チェック（2026-10-18 本人の改善依頼書 2-2〜2-4・3-1・4-2）。
1) 「誕生色（X）」の X が、その日の一般的な誕生色と違う（ラッキーカラーと取り違え）
2) 生まれ持ちのラッキーカラーの表示が、その日のラッキーカラーと違う
3) 品名と合わないと判定した商品（goods_ng.json）の写真が出ている
4) 商品枠が12を超える／同じ商品へのリンクが2回出る
5) 値段の表示が残っている／PR が枠の頭にない広告の注記が残っている
使い方: python work/scripts/check_birthday_facts.py（out/html/*.html を読む）"""
import glob, json, os, re, collections
W = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
M = json.load(open(os.path.join(W, "data", "materials_366.json"), encoding="utf-8"))
STD = json.load(open(os.path.join(W, "data", "bday_standard_366.json"), encoding="utf-8"))["days"]
G = json.load(open(os.path.join(W, "data", "goods_rakuten.json"), encoding="utf-8"))
NG = set(json.load(open(os.path.join(W, "data", "goods_ng.json"), encoding="utf-8"))["ng"])
ng_imgs = {G[q]["img"] for q in NG if G.get(q) and G[q].get("img")}
err = collections.defaultdict(list)
for p in sorted(glob.glob(os.path.join(W, "out", "html", "*.html"))):
    k = os.path.basename(p)[:4]
    s = open(p, encoding="utf-8").read()
    e, std = M[k], STD[f"{k[:2]}-{k[2:]}"]
    for m in re.finditer(r"誕生色（(?!\d+月\d+日)([^）]{1,15})）", s):
        if m.group(1) != std["color"]:
            err["1 誕生色の取り違え"].append(f"{k}: 誕生色（{m.group(1)}）")
    if f'生まれ持ちのラッキーカラー（当サイト独自）</small><b>{e["birthday_color"]["name"]}' not in s:
        err["2 ラッキーカラーの表示"].append(k)
    for nm in re.finditer(r'<b class="fh-b27-shop-name">([^<]+)</b>', s):
        st = max(s.rfind('<div class="fh-b27-shop"', 0, nm.start()), s.rfind('<div class="fh-b27-shop fh-b27-gift"', 0, nm.start()))
        if nm.group(1) in NG and "<img" in s[st:nm.start()]:
            err["3 合わない商品の写真"].append(f"{k}: {nm.group(1)}")
    hrefs = re.findall(r'class="fh-b27-shopbtn fh-b27-shop-rakuten" href="([^"]+)"', s)
    if len(hrefs) > 12:
        err["4 商品枠が12超"].append(f"{k}: {len(hrefs)}")
    dup = [h for h, c in collections.Counter(hrefs).items() if c > 1]
    if dup:
        err["4 同じ商品が2回"].append(f"{k}: {len(dup)}")
    if re.search(r"\d円</b>", s) or "広告を含みます" in s or "アフィリエイトリンク）を含みます" in s:
        err["5 値段・古い広告注記"].append(k)
n = len(glob.glob(os.path.join(W, "out", "html", "*.html")))
print(f"{n}ページを確認")
for t, v in sorted(err.items()):
    print(f"{t}: {len(v)}件 例 {v[:5]}")
print("問題なし" if not err else "")
