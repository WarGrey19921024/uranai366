"""静的ページ（FTPで置いているページ：/dice/ /trump/ /rune/ /number-fortune/ /mbti-compatibility/ とその下）に入れる広告の部品。2026-10-18 本人「静的ページにしよう」。
ページごとに「よくある質問」の見出しの直前に、商品ボックスと電話占いの案内を入れる（入れるのはローカルの Code。手順は work/Code依頼_20261018_静的ページの広告.md）。
出力：out/static_ads/<group>.html（そのまま貼る1かたまり。<!-- st-ad:start --> 〜 <!-- st-ad:end -->）"""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import aff_extra as AX
from build_sign_ads import card, esc, OM_CSS

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "out", "static_ads")
GROUPS = {
    "dice": ("サイコロ占いを手もとで", "画面のサイコロのかわりに、手もとで振ってみたい人へ。楽天・Yahoo!ショッピングの商品ページへ移ります。",
             "出た目の意味を、人と話してみたいときは", "サイコロは「今の流れ」を短く教えてくれます。迷いが大きいときは、占い師に直接たずねてみるのもひとつの方法です。"),
    "trump": ("トランプ占いに使うトランプ", "手もとのトランプで占うなら、丈夫で切りやすいものを。楽天・Yahoo!ショッピングの商品ページへ移ります。",
              "カードの答えを、人と話してみたいときは", "同じカードでも、読み手が変わると見えてくるものがあります。気になる結果が出たら、占い師に直接たずねてみるのもひとつの方法です。"),
    "rune": ("ルーン占いを手もとで", "石のルーンは、袋から1つずつ引いて使えます。楽天・Yahoo!ショッピングの商品ページへ移ります。",
             "ルーンの答えを、人と話してみたいときは", "5つのルーンの並びは、読み手によって受け取り方が変わります。気になる結果が出たら、占い師に直接たずねてみるのもひとつの方法です。"),
    "num": ("数秘術をもっと知る本", "数字の意味をくわしく知りたい人へ。楽天・Yahoo!ショッピングの商品ページへ移ります。",
            "数字が表す流れを、人と話してみたいときは", "同じ数字でも、生年月日の組み合わせで読み方が変わります。くわしく見てもらいたいときは、占い師に直接たずねてみるのもひとつの方法です。"),
    "mbti": ("16タイプをもっと知る本", "タイプごとの性格や付き合い方を、もっとくわしく知りたい人へ。楽天・Yahoo!ショッピングの商品ページへ移ります。",
             "二人の関係を、人に相談したいときは", "相性はタイプだけでなく、出会い方やその時の状況でも変わります。気になる相手がいるなら、占い師に直接たずねてみるのもひとつの方法です。"),
}


def main():
    os.makedirs(OUT, exist_ok=True)
    rows = {}
    for line in open(os.path.join(HERE, "..", "data", "goods_static.tsv"), encoding="utf-8"):
        g, q, label, img, url, price, rev, shop, name = line.rstrip("\n").split("\t")
        rows.setdefault(g, []).append((label, q, dict(at="2026-10-18", img="https://thumbnail.image.rakuten.co.jp/@0_" + img + "?_ex=300x300",
                                                     url="https://item.rakuten.co.jp/" + url, price=int(price), name=name)))
    t = AX.tpl()
    css = (AX.CSS + OM_CSS + "<style>.om-ad{margin:20px auto}.om-ad .fh-b27-adphone{background:#F3EEFA;border:1px solid #D9CCEB;border-radius:14px;padding:14px 16px;font-size:14px;line-height:1.7;margin-top:12px;color:#2E2A26}"
           ".om-ad .fh-b27-adphone small{display:block;font-weight:700;color:#5B3C88;font-size:14px}.om-ad .fh-b27-adphone p{margin:4px 0 10px;color:#2E2A26}"
           ".om-ad .fh-b27-adphone a.fh-b27-btn{display:inline-block;background:#5B3C88;color:#fff;border-radius:999px;padding:8px 18px;font-weight:700;text-decoration:none}"
           ".om-ad .fh-b27-adphone a img{display:none}.om-ad .fh-b27-adphone .fh-b27-pr{margin-left:8px}.om-ad .fh-b27-shops{grid-template-columns:repeat(2,minmax(0,1fr))}"
           ".om-ad .fh-b27-adgoods-h span,.om-ad .fh-b27-adgoods-l,.om-ad .fh-b27-shop-name{color:#2E2A26}@media(max-width:600px){.om-ad .fh-b27-shops{grid-template-columns:minmax(0,1fr)}}</style>")
    for g, (title, lead, ph_t, ph_p) in GROUPS.items():
        cards = [card(label, q, it) for label, q, it in rows[g]]
        goods = (f'<aside class="fh-b27-adgoods"><p class="fh-b27-adgoods-h"><span>{esc(title)}</span><span class="fh-b27-pr">PR（広告）</span></p>'
                 f'<p class="fh-b27-adgoods-l">{esc(lead)}</p><div class="fh-b27-shops">{"".join(cards)}</div></aside>')
        phone = (f'<div class="fh-b27-ad fh-b27-adphone"><small>{esc(ph_t)}</small><p>{esc(ph_p)}</p>'
                 f'<a class="fh-b27-btn" href="{esc(AX.href("phone"))}" rel="nofollow sponsored" data-aff="phone">電話占いで相談してみる</a>{t["phone"]["impression"]}<span class="fh-b27-pr">広告</span></div>')
        block = f'<!-- st-ad:start 2026-10-18 -->\n<div class="fh-b27 om-ad">{css}{goods}{phone}</div>\n<!-- st-ad:end -->\n'
        open(os.path.join(OUT, f"{g}.html"), "w", encoding="utf-8").write(block)
        print(g, len(block))


if __name__ == "__main__":
    main()
