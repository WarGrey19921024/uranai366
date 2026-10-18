"""トップページ（ID 896）の下のほうに置く、控えめな広告の1かたまり。2026-10-18 本人「先に終わらせて」（提案：下のほうに控えめに）。
出力：out/static_ads/top.html（<!-- top-ad:start --> 〜 <!-- top-ad:end -->）。本文の最後に足す。"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import aff_extra as AX
from build_sign_ads import OM_CSS

HERE = os.path.dirname(os.path.abspath(__file__))
ITEMS = [("令和9年 運勢暦", "2027年の運勢暦", "吉日・吉方位・六曜まで1冊で確かめられる暦です。", "book"),
         ("ひとり用の手帳", "2027年の手帳", "占いで見たいい月・いい日を書き込んでおくと、1年の計画が立てやすくなります。", "book"),
         ("月齢カレンダー 2027", "月の満ち欠けカレンダー", "新月・満月の日がひと目でわかる壁掛けカレンダーです。", "moon"),
         ("タロットカード ウェイト版", "タロットカード", "画面だけでなく、手もとのカードでも占ってみたい人へ。", "star")]


def main():
    t = AX.tpl()
    goods = AX.goods_box("2027年の準備に", ITEMS, lead="来年の運勢や暦を手もとに置いておきたい人へ。楽天・Yahoo!ショッピングの商品ページへ移ります。")
    phone = (f'<div class="fh-b27-ad fh-b27-adphone"><small>占いの結果を、人と話してみたいときは</small>'
             f'<p>このサイトの占いで気になる結果が出たら、占い師に直接たずねてみるのもひとつの方法です。</p>'
             f'<a class="fh-b27-btn" href="{AX.esc(AX.href("phone"))}" rel="nofollow sponsored" data-aff="phone">電話占いで相談してみる</a>'
             f'{t["phone"]["impression"]}<span class="fh-b27-pr">広告</span></div>')
    css = (AX.CSS + OM_CSS + "<style>.om-ad{margin:32px auto 8px;max-width:880px}.om-ad .fh-b27-adphone{background:#F3EEFA;border:1px solid #D9CCEB;border-radius:14px;padding:14px 16px;font-size:14px;line-height:1.7;margin-top:12px;color:#2E2A26}"
           ".om-ad .fh-b27-adphone small{display:block;font-weight:700;color:#5B3C88;font-size:14px}.om-ad .fh-b27-adphone p{margin:4px 0 10px;color:#2E2A26}"
           ".om-ad .fh-b27-adphone a.fh-b27-btn{display:inline-block;background:#5B3C88;color:#fff;border-radius:999px;padding:8px 18px;font-weight:700;text-decoration:none}"
           ".om-ad .fh-b27-adphone a img{display:none}.om-ad .fh-b27-adphone .fh-b27-pr{margin-left:8px}.om-ad .fh-b27-shops{display:grid;gap:10px;grid-template-columns:repeat(2,minmax(0,1fr))}"
           ".om-ad .fh-b27-shop{display:grid;grid-template-columns:56px minmax(0,1fr);gap:10px;align-items:center;background:#fff;border:1px solid #E6DCCB;border-radius:12px;padding:10px}"
           ".om-ad .fh-b27-shop-btns{display:flex;gap:6px;flex-wrap:wrap}.om-ad a.fh-b27-shopbtn{display:inline-flex;align-items:center;justify-content:center;border-radius:999px;padding:6px 12px;font-size:13px;font-weight:700;text-decoration:none;background:#BF0000;color:#fff}"
           ".om-ad a.fh-b27-shop-yahoo{background:#FF0033}.om-ad .fh-b27-shop small{display:block;font-size:11px;color:#7A6E5C}.om-ad .fh-b27-shop-name{display:block;font-size:15px}.om-ad .fh-b27-shop-why{display:block;font-size:13px;line-height:1.6;color:#4A3F30}"
           ".om-ad .fh-b27-adgoods-h span,.om-ad .fh-b27-adgoods-l,.om-ad .fh-b27-shop-name{color:#2E2A26}@media(max-width:600px){.om-ad .fh-b27-shops{grid-template-columns:minmax(0,1fr)}}</style>")
    block = f'<!-- top-ad:start 2026-10-18 -->\n<div class="fh-b27 om-ad" style="position:relative;z-index:2">{css}{goods}{phone}</div>\n<!-- top-ad:end -->\n'
    assert goods and "<img" in goods
    open(os.path.join(HERE, "..", "out", "static_ads", "top.html"), "w", encoding="utf-8").write(block)
    print(len(block), goods.count("fh-b27-shop\""), goods.count("<img"))


main()
