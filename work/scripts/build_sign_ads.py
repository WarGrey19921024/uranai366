"""12星座の記事（/aries/ など、投稿 2396〜2409・既存の手書き記事）に入れる広告の部品を作る。2026-10-17 本人「次へいこう」（星座・MBTI）。
記事の本文は書き換えず、次の3か所に足すだけ（反映はブラウザから REST）：
1. 「ラッキーカラー」の色の下：色の系統ごとのマグカップ（data/goods_family.json。366日ページと同じ使いまわしの部品）
2. 「ラッキーアイテム」の一覧の下：記事に書かれたアイテムに合う楽天の商品3つ（data/goods_signs.tsv。写真を見て選んだ）
3. 「他の誕星座との相性」の前：電話占いの案内
商品データは goods_rakuten.json と分けて持つ（366日ページで使っている検索語の商品を変えないため）。
出力：out/sign_ads.json（星座ごとに {colors, items, phone} の HTML）"""
import html, json, os, sys, urllib.parse
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import goods_media as GM
import aff_extra as AX
from build_omikuji_ads import OM_CSS

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "data")
OUT = os.path.join(HERE, "..", "out", "sign_ads.json")
AT = "2026-10-17"
FAM = json.load(open(os.path.join(DATA, "goods_family.json"), encoding="utf-8"))

# 記事に書かれたラッキーカラー → 色の系統
COLOR_FAM = {"レッド": "赤", "ターコイズブルー": "水色", "グリーン": "緑", "アイボリー": "白", "イエロー": "黄", "ライトブルー": "水色",
             "シルバー": "銀", "パステルブルー": "水色", "ゴールド": "金", "オレンジ": "オレンジ", "ラベンダー": "紫", "ミントグリーン": "黄緑",
             "ペールピンク": "ピンク", "ディープレッド": "赤", "マリンブルー": "青", "パープル": "紫", "ディープグリーン": "緑", "グレー": "グレー",
             "エレクトリックブルー": "青", "アクアブルー": "水色"}
SIGN_COLORS = {"aries": "レッド、ターコイズブルー", "taurus": "グリーン、アイボリー", "gemini": "イエロー、ライトブルー",
               "cancer": "シルバー、パステルブルー", "leo": "ゴールド、オレンジ", "virgo": "ラベンダー、ミントグリーン",
               "libra": "ペールピンク、シルバー", "scorpio": "ディープレッド、マリンブルー", "sagittarius": "ターコイズブルー、パープル",
               "capricorn": "ディープグリーン、グレー", "aquarius": "エレクトリックブルー、シルバー", "pisces": "アクアブルー、ラベンダー"}
# 記事のラッキーアイテム①〜⑤の順に並べるための目印（記事の5つすべてに商品を出す。2026-10-17 本人「アイテム数分あったほうがいい」）
ORDER = {"aries": ["財布", "腕時計", "スポーツ", "日記", "赤い"], "taurus": ["マグ", "観葉", "スカーフ", "天然石", "木製"],
         "gemini": ["イヤホン", "本や雑誌", "メモ", "ボールペン", "旅"], "cancer": ["シーグラス", "クッション", "キャンドル", "写真", "ガラス"],
         "leo": ["ライオン", "サングラス", "ゴールド", "ボディ", "スケジュール"], "virgo": ["ノート", "ハーブ", "文房具", "時計", "クリスタル"],
         "libra": ["ミラー", "アロマ", "アクセサリー", "ノート", "ハンカチ"], "scorpio": ["ブレスレット", "本革", "アンティーク", "日記", "キャンドル"],
         "sagittarius": ["パスポート", "帽子", "バッグ", "語学", "地図"], "capricorn": ["手帳", "ビジネス", "時計", "マグ", "登山"],
         "aquarius": ["イヤホン", "ウォッチ", "水筒", "講座", "未来"], "pisces": ["シェル", "キャンドル", "ディフューザー", "ノート", "音楽"]}
SIGN_JA = {"aries": "おひつじ座", "taurus": "おうし座", "gemini": "ふたご座", "cancer": "かに座", "leo": "しし座", "virgo": "おとめ座",
           "libra": "てんびん座", "scorpio": "さそり座", "sagittarius": "いて座", "capricorn": "やぎ座", "aquarius": "みずがめ座", "pisces": "うお座"}


def esc(s):
    return html.escape(str(s), quote=True)


def links(q, url):
    t = AX.tpl()
    rk = GM.moshimo_item_href(t["rakuten"]["href"], url)
    yh = t["yahoo"]["href"].replace("{url}", urllib.parse.quote(t["yahoo"]["target"].replace("{q}", urllib.parse.quote_plus(q)), safe=""))
    return rk, yh


def card(label, q, it, small="おすすめ"):
    rk, yh = links(q, it["url"])
    t = AX.tpl()
    when = f"{int(it['at'][5:7])}月{int(it['at'][8:10])}日時点"
    return (f'<div class="fh-b27-shop"><div class="fh-b27-shop-pic"><a class="fh-b27-shop-photo" href="{esc(rk)}" rel="nofollow sponsored" tabindex="-1" aria-hidden="true">'
            f'<img class="fh-b27-shop-img" src="{esc(it["img"])}" alt="{esc(label)}" width="128" height="128" loading="lazy" decoding="async" referrerpolicy="no-referrer"></a></div>'
            f'<div class="fh-b27-shop-body"><small>{esc(small)}</small><b class="fh-b27-shop-name">{esc(label)}</b>'
            f'<span class="fh-b27-shop-price">楽天 <b>{int(it["price"]):,}円</b><small>（{when}）</small></span></div>'
            f'<div class="fh-b27-shop-btns"><a class="fh-b27-shopbtn fh-b27-shop-rakuten" href="{esc(rk)}" rel="nofollow sponsored" data-aff="rakuten">楽天で見る</a>{t["rakuten"]["impression"]}'
            f'<a class="fh-b27-shopbtn fh-b27-shop-yahoo" href="{esc(yh)}" rel="nofollow sponsored" data-aff="yahoo">Yahoo!で探す</a>{t["yahoo"]["impression"]}</div></div>')


def wrap(title, lead, cards, mark):
    return (f'<!-- sign-ad:{mark} 2026-10-17 --><div class="fh-b27 om-ad"><aside class="fh-b27-adgoods"><p class="fh-b27-adgoods-h"><span>{esc(title)}</span>'
            f'<span class="fh-b27-pr">PR（広告）</span></p><p class="fh-b27-adgoods-l">{esc(lead)}</p><div class="fh-b27-shops">{"".join(cards)}</div></aside></div><!-- /sign-ad:{mark} -->')


def main():
    rows = {}
    for line in open(os.path.join(DATA, "goods_signs.tsv"), encoding="utf-8"):
        sl, q, label, img, url, price, rev, shop, name = line.rstrip("\n").split("\t")
        rows.setdefault(sl, []).append((label, q, dict(at=AT, img="https://thumbnail.image.rakuten.co.jp/@0_" + img + "?_ex=300x300",
                                                       url="https://item.rakuten.co.jp/" + url, price=int(price), name=name)))
    gr = json.load(open(os.path.join(DATA, "goods_rakuten.json"), encoding="utf-8"))
    t = AX.tpl()
    out = {"css": AX.CSS + OM_CSS + "<style>.om-ad{margin:16px 0}.om-ad .fh-b27-adphone{background:#F3EEFA;border:1px solid #D9CCEB;border-radius:14px;padding:14px 16px;font-size:14px;line-height:1.7}"
                  ".om-ad .fh-b27-adphone small{display:block;font-weight:700;color:#5B3C88;font-size:14px}.om-ad .fh-b27-adphone p{margin:4px 0 10px}"
                  ".om-ad .fh-b27-adphone a.fh-b27-btn{display:inline-block;background:#5B3C88;color:#fff;border-radius:999px;padding:8px 18px;font-weight:700;text-decoration:none}"
                  ".om-ad .fh-b27-adphone a.fh-b27-btn img{display:none}.om-ad .fh-b27-adphone .fh-b27-pr{margin-left:8px}</style>", "signs": {}}
    for sl, ja in SIGN_JA.items():
        cols = [c.strip() for c in SIGN_COLORS[sl].split("、")]
        ccards = []
        for c in cols:
            q = FAM["color"][COLOR_FAM[c]]
            ccards.append(card(f"{c}系のマグカップ", q, gr[q], small=f"ラッキーカラー {c}"))
        order = ORDER[sl]
        rs = sorted(rows[sl], key=lambda r: next((i for i, k in enumerate(order) if k in r[0]), 9))
        items = [card(label, q, it, small=f"{ja}のラッキーアイテム") for label, q, it in rs]
        phone = (f'<!-- sign-ad:phone 2026-10-17 --><div class="fh-b27 om-ad"><div class="fh-b27-ad fh-b27-adphone"><small>{esc(ja)}の相性や今年の流れを、人に相談したいときは</small>'
                 f'<p>星座の相性は、生まれた日や時間まで見るとさらにくわしくわかります。気になる相手がいるなら、占い師に直接たずねてみるのもひとつの方法です。</p>'
                 f'<a class="fh-b27-btn" href="{esc(AX.href("phone"))}" rel="nofollow sponsored" data-aff="phone">電話占いで相談してみる</a>{t["phone"]["impression"]}'
                 f'<span class="fh-b27-pr">広告</span></div></div><!-- /sign-ad:phone -->')
        out["signs"][sl] = dict(
            colors=wrap(f"{ja}のラッキーカラーの小物", "毎日使うマグカップなら、ラッキーカラーを無理なく取り入れられます。楽天・Yahoo!ショッピングの商品ページへ移ります。", ccards, "colors"),
            items=wrap(f"{ja}のラッキーアイテムを探す", "上のラッキーアイテムに合う商品です。楽天・Yahoo!ショッピングの商品ページへ移ります。", items, "items"),
            phone=phone)
    # /star/（一覧ページ）：FAQ の前に商品3つ、ほかの占いとの組み合わせの前に電話占い
    out["star"] = dict(
        items=wrap("星座をもっと楽しむアイテム", "自分の星座を身につけたり、夜空で探したり。楽天・Yahoo!ショッピングの商品ページへ移ります。",
                   [card(label, q, it, small="おすすめ") for label, q, it in rows["star"]], "items"),
        phone=out["signs"]["aries"]["phone"].replace("おひつじ座の相性や今年の流れを、人に相談したいときは", "星座の相性や今年の流れを、人に相談したいときは"))
    json.dump(out, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("ok", len(out["signs"]))


if __name__ == "__main__":
    main()
