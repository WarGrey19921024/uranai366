"""商品ボックスに「商品の写真」を出すための商品データを、楽天市場（とYahoo!ショッピング）の公式APIから集める（2026-10-16）。
本人の要望：「探す」ボタンだけではどんな物かわからず、買うイメージがわかない → 写真つきの商品カード（Rinker・ポチップ型）にする。

仕組み
- work/out/ の全ページから、楽天のボタンに入っている検索語（4,000語ほど）を集める
- 1語ずつ楽天市場商品検索API（新API・2026年版）で検索し、写真のある・在庫のある商品の上位から1つ選ぶ
  （レビューのある商品を優先。なければ1件目）
- 結果を work/data/goods_rakuten.json に保存（検索語 → 写真URL・商品ページURL・商品名・価格・店名・取得日）
- 途中で止めても、次に動かすと続きから集める。1語ごとに1.6秒あける（楽天の注意：短い間に大量に送ると止められる）
- YAHOO_APP_ID があれば、Yahoo!ショッピングの商品検索API（V3）でも同じように集める → work/data/goods_yahoo.json

使い方（本人のパソコン＝楽天のアプリ登録で許可したIPアドレスから。クラウドからは届かない）
  set RAKUTEN_APP_ID=（アプリID）
  set RAKUTEN_ACCESS_KEY=（pk_ で始まるアクセスキー）
  set YAHOO_APP_ID=（任意：Yahoo!デベロッパーのClient ID）
  .venv\\Scripts\\python -X utf8 work\\scripts\\fetch_goods.py            # 全部（続きから）
  .venv\\Scripts\\python -X utf8 work\\scripts\\fetch_goods.py --limit 20 # 試しに20語
  .venv\\Scripts\\python -X utf8 work\\scripts\\fetch_goods.py --refresh 60 # 60日より古いものを取り直す
キー（アプリID・アクセスキー）はファイルに書かない・コミットしない（環境変数だけで渡す）。
集めたJSON（写真のURL・商品ページのURL・商品名）は公開されている情報なので、コミットしてよい。
"""
import argparse, datetime as dt, glob, json, os, re, sys, time, urllib.parse, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
WORK = os.path.normpath(os.path.join(HERE, ".."))
SITE = "https://www.uranai.epoch-compass.com/"
R_URL = "https://openapi.rakuten.co.jp/ichibams/api/IchibaItem/Search/20260701"
Y_URL = "https://shopping.yahooapis.jp/ShoppingWebService/V3/itemSearch"
OUT_R = os.path.join(WORK, "data", "goods_rakuten.json")
OUT_Y = os.path.join(WORK, "data", "goods_yahoo.json")
WAIT = 1.6


def queries():
    """全ページの楽天ボタンから検索語を集める（もしもの url= の中の楽天検索URL /search/mall/{語}/）"""
    qs = []
    seen = set()
    for p in sorted(glob.glob(os.path.join(WORK, "out", "**", "*.html"), recursive=True)):
        if os.sep + "sample" + os.sep in p:
            continue
        t = open(p, encoding="utf-8").read()
        for m in re.finditer(r'https://af\.moshimo\.com/af/c/click\?[^"\']*?url=([^"\'&]+)', t):
            u = urllib.parse.unquote(m.group(1))
            q = re.search(r"search\.rakuten\.co\.jp/search/mall/([^/]+)/", u)
            if q:
                w = urllib.parse.unquote_plus(q.group(1))
                if w not in seen:
                    seen.add(w)
                    qs.append(w)
    return qs


def get_json(url, headers):
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.loads(r.read().decode("utf-8"))


def rakuten(q, app, key):
    p = {"applicationId": app, "accessKey": key, "keyword": q, "hits": 10, "imageFlag": 1, "availability": 1,
         "formatVersion": 2, "elements": "itemName,itemPrice,itemUrl,mediumImageUrls,reviewCount,reviewAverage,shopName"}
    d = get_json(R_URL + "?" + urllib.parse.urlencode(p), {"Referer": SITE, "Origin": SITE.rstrip("/"), "User-Agent": "jinsei-yoho-goods/1.0"})
    items = d.get("items") or d.get("Items") or []
    items = [x.get("item", x) for x in items]
    items = [x for x in items if x.get("mediumImageUrls")]
    if not items:
        return None
    best = next((x for x in items if (x.get("reviewCount") or 0) >= 3), items[0])
    img = best["mediumImageUrls"][0]
    img = img.get("imageUrl", img) if isinstance(img, dict) else img
    img = re.sub(r"\?_ex=\d+x\d+", "?_ex=300x300", img)
    return {"img": img, "url": best["itemUrl"], "name": best["itemName"][:80], "price": best.get("itemPrice"),
            "shop": best.get("shopName", ""), "reviews": best.get("reviewCount", 0), "at": dt.date.today().isoformat()}


def yahoo(q, app):
    p = {"appid": app, "query": q, "results": 10, "image_size": 300, "in_stock": "true"}
    d = get_json(Y_URL + "?" + urllib.parse.urlencode(p), {"User-Agent": "jinsei-yoho-goods/1.0"})
    hits = [h for h in d.get("hits", []) if (h.get("exImage") or h.get("image") or {}).get("url")]
    if not hits:
        return None
    best = next((h for h in hits if ((h.get("review") or {}).get("count") or 0) >= 3), hits[0])
    img = (best.get("exImage") or best.get("image"))["url"]
    return {"img": img, "url": best["url"], "name": best["name"][:80], "price": best.get("price"),
            "shop": (best.get("seller") or {}).get("name", ""), "reviews": (best.get("review") or {}).get("count", 0), "at": dt.date.today().isoformat()}


def load(p):
    return json.load(open(p, encoding="utf-8")) if os.path.exists(p) else {}


def save(p, d):
    tmp = p + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(d, f, ensure_ascii=False, indent=0, sort_keys=True)
    os.replace(tmp, p)


def run(name, path, fn, qs, limit, refresh):
    data = load(path)
    old = (dt.date.today() - dt.timedelta(days=refresh)).isoformat() if refresh else None
    todo = [q for q in qs if q not in data or (old and (data[q] or {}).get("at", "0") < old)]
    if limit:
        todo = todo[:limit]
    print(f"{name}: 全{len(qs)}語のうち、これから {len(todo)} 語（約{len(todo) * WAIT / 60:.0f}分）")
    for i, q in enumerate(todo, 1):
        for attempt in range(3):
            try:
                data[q] = fn(q)
                break
            except urllib.error.HTTPError as e:
                if e.code == 429:
                    time.sleep(10 * (attempt + 1))
                    continue
                print(f"  {q}: HTTP {e.code} {e.read()[:200]!r}")
                if e.code in (401, 403):
                    sys.exit("キーまたは許可IPアドレスの設定を確認してください（楽天ウェブサービスのアプリ設定）")
                data[q] = None
                break
            except Exception as e:  # 通信の一時的な失敗
                print(f"  {q}: {e}")
                time.sleep(5)
        if i % 25 == 0:
            save(path, data)
            print(f"  {i}/{len(todo)}")
        time.sleep(WAIT)
    save(path, data)
    ok = sum(1 for v in data.values() if v)
    print(f"{name}: 写真あり {ok} 語／{len(data)} 語 → {os.path.relpath(path, WORK)}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--refresh", type=int, default=0, help="この日数より古いものを取り直す")
    a = ap.parse_args()
    qs = queries()
    for pth in (OUT_R, OUT_Y):  # 作り直したページは商品ページへのリンクになるので、集めたことのある語も足す
        qs += [q for q in load(pth) if q not in qs]
    app, key = os.environ.get("RAKUTEN_APP_ID"), os.environ.get("RAKUTEN_ACCESS_KEY")
    if app and key:
        run("楽天", OUT_R, lambda q: rakuten(q, app, key), qs, a.limit, a.refresh)
    else:
        print("RAKUTEN_APP_ID と RAKUTEN_ACCESS_KEY が無いので、楽天は飛ばします")
    yid = os.environ.get("YAHOO_APP_ID")
    if yid:
        run("Yahoo!", OUT_Y, lambda q: yahoo(q, yid), qs, a.limit, a.refresh)


if __name__ == "__main__":
    main()
