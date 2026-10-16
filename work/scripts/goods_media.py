"""商品ボックスの「商品の写真」と「商品ページへのリンク」（fetch_goods.py が集めた work/data/goods_*.json を使う）。
データの無い検索語は、これまでどおり自前の絵と検索ページへのボタンになる（ページは壊れない）。
写真は楽天・Yahoo!の画像サーバーのものをそのまま表示する（両社の商品検索APIの結果。商品ページへのリンクとセットで使う）。"""
import html, json, os, urllib.parse

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "data")
_D = {}


def _load(shop):
    if shop not in _D:
        p = os.path.join(DATA, f"goods_{shop}.json")
        _D[shop] = json.load(open(p, encoding="utf-8")) if os.path.exists(p) else {}
    return _D[shop]


def item(shop, q):
    """検索語 q の代表商品（楽天 or Yahoo!）。無ければ None"""
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
