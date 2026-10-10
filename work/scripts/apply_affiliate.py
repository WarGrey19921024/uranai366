"""アフィリエイトの仮リンク（#affiliate-TODO-…）を実リンクに置き換える。
2つの方法（両方使える。個別指定が優先）：
 1) 店ごとの「検索リンクのひな形」：work/out/affiliate_templates.json に
    {"rakuten": "https://hb.afl.rakuten.co.jp/hgc/あなたのID/?pc=https%3A%2F%2Fsearch.rakuten.co.jp%2Fsearch%2Fmall%2F{q}%2F",
     "rakuten-amazon": "（同上 または Amazon の検索リンク {q}）",
     "phone": "電話占いの案内ページの実リンク（{q} は使わない）"}
    のように書く。{q} には商品名（URLエンコード済み）が入る。
 2) 個別指定：work/out/affiliate_placeholders.csv の「実リンク（ここに記入）」列に書いた行だけ、その URL にする。
使い方: python apply_affiliate.py  → work/out/html/ を書き換え、build_import.py で投入用CSVを作り直す
"""
import os, re, csv, json, glob, urllib.parse
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "out")
tpl_p = os.path.join(OUT, "affiliate_templates.json")
tpl = json.load(open(tpl_p, encoding="utf-8")) if os.path.exists(tpl_p) else {}
manual = {}
for r in csv.DictReader(open(os.path.join(OUT, "affiliate_placeholders.csv"), encoding="utf-8-sig")):
    if r.get("実リンク（ここに記入）", "").strip():
        manual[r["仮リンク（置換前）"]] = r["実リンク（ここに記入）"].strip()
left, done = 0, 0
for f in sorted(glob.glob(os.path.join(OUT, "html", "*.html"))):
    s = open(f, encoding="utf-8").read()
    def rep(m):
        global left, done
        key, label = m.group(1), m.group(2)
        shop = key.split("-")[2] if key.count("-") >= 3 else "other"
        shop = "rakuten-amazon" if "rakuten-amazon" in key else shop
        url = manual.get(key)
        if not url and shop in tpl:
            q = label.split(":", 1)[-1].replace(" 小物", "").replace(" ギフト", "")
            url = tpl[shop].replace("{q}", urllib.parse.quote(q))
        if not url:
            left += 1
            return m.group(0)
        done += 1
        return m.group(0).replace(f'href="{key}"', f'href="{url}"')
    s2 = re.sub(r'href="(#affiliate-TODO-[^"]+)" rel="nofollow sponsored" data-aff="\[([^\]]*)\]"', rep, s)
    if s2 != s: open(f, "w", encoding="utf-8").write(s2)
print(f"置き換え {done} か所・残り（仮のまま）{left} か所")
