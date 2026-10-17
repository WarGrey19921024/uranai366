"""商品ボックスの「商品の写真」と「商品ページへのリンク」（fetch_goods.py が集めた work/data/goods_*.json を使う）。
データの無い検索語は、これまでどおり自前の絵と検索ページへのボタンになる（ページは壊れない）。
写真は楽天・Yahoo!の画像サーバーのものをそのまま表示する（両社の商品検索APIの結果。商品ページへのリンクとセットで使う）。"""
import html, json, os, re, urllib.parse

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "data")
_D = {}


_NG = None


def _ng():
    global _NG
    if _NG is None:
        p = os.path.join(DATA, "goods_ng.json")
        _NG = set(json.load(open(p, encoding="utf-8"))["ng"]) if os.path.exists(p) else set()
    return _NG


def _load(shop):
    if shop not in _D:
        p = os.path.join(DATA, f"goods_{shop}.json")
        _D[shop] = json.load(open(p, encoding="utf-8")) if os.path.exists(p) else {}
    return _D[shop]


_SEEN = set()


def item(shop, q):
    """検索語 q の代表商品（楽天 or Yahoo!）。無ければ None"""
    _SEEN.add(q)
    if os.environ.get("FH_GOODS_LOG"):  # 使っている検索語を書き出す（写真集めの一覧づくり用）
        with open(os.environ["FH_GOODS_LOG"], "a", encoding="utf-8") as fp:
            fp.write(q + "\n")
    if shop == "rakuten" and q in _ng():  # 品物が合わない商品は使わない（goods_ng.json）
        return None
    return (_load(shop).get(q) or None) if shop in ("rakuten", "yahoo") else None


def photo(q):
    """商品の写真（楽天 → Yahoo! の順）。無ければ None"""
    for sh in ("rakuten", "yahoo"):
        it = item(sh, q)
        if it and it.get("img"):
            return it
    return None


def img_tag(q, alt, cls="fh-b27-shop-img"):
    it = photo(q)
    if not it:
        return ""
    return (f'<img class="{cls}" src="{html.escape(it["img"], quote=True)}" alt="{html.escape(alt, quote=True)}" '
            f'width="128" height="128" loading="lazy" decoding="async" referrerpolicy="no-referrer">')


def moshimo_item_href(tpl_href, item_url):
    """もしもの「どこでもリンク」の url= に商品ページを入れる"""
    return tpl_href.replace("{url}", urllib.parse.quote(item_url, safe=""))


def price_html(q, short=False):
    """写真のある商品の値段（○月○日時点）と商品名。無ければ空"""
    it = item("rakuten", q)
    shop = "楽天"
    if not it or not it.get("price"):
        it, shop = item("yahoo", q), "Yahoo!"
    if not it or not it.get("price"):
        return ""
    at = it.get("at", "")
    when = f"{int(at[5:7])}月{int(at[8:10])}日時点" if len(at) >= 10 else ""
    name = re.sub(r"[！!【】★☆＼／◆◇■□♪]+", " ", it.get("name") or "").strip()
    name = re.sub(r"\s+", " ", name)
    name = name if len(name) <= 30 else name[:30] + "…"
    prod = "" if short else f'<span class="fh-b27-shop-prod">{html.escape(name)}</span>'
    return (f'{prod}<span class="fh-b27-shop-price">{shop} <b>{int(it["price"]):,}円</b>'
            f'<small>（{when}）</small></span>')
