"""誕生日ページ以外のページ（タロット・九星・宿曜・マヤ・誕生花・相性・一覧・まるごと診断）に入れる広告。
AdSense 不合格（2026-10-16）を受けて、本人の指示でアフィリエイトを貼る。

- 電話占い（A8・電話占いセラ）：占いの結果を見た直後に、小さな案内を1か所
- 物販（もしも・楽天／Yahoo!ショッピング。Amazon は審査が通るまで出さない）：FAQ の前に、ページの内容に合う商品ボックスを2つ
- 実リンクは work/out/affiliate_templates.json（build_html.py と同じひな形）。無ければ何も入れない（仮リンクは作らない）
- 広告であることを「広告」「PR」と明記する。リンクは rel="nofollow sponsored"
build_hub.shell() から呼ぶ（URL でページを見分ける）。"""
import html, json, os, re, urllib.parse
import goods_media as GM

HERE = os.path.dirname(os.path.abspath(__file__))
TPL_PATH = os.path.join(HERE, "..", "out", "affiliate_templates.json")
GOODS_SHOPS = [("rakuten", "楽天"), ("yahoo", "Yahoo!"), ("amazon", "Amazon")]
HOSTS = ("af.moshimo.com", "px.a8.net")
_TPL = None


def tpl():
    global _TPL
    if _TPL is None:
        _TPL = {}
        if os.path.exists(TPL_PATH):
            for k, v in json.load(open(TPL_PATH, encoding="utf-8")).items():
                if isinstance(v, dict) and v.get("href") and v.get("impression") \
                        and urllib.parse.urlsplit(v["href"]).hostname in HOSTS:
                    _TPL[k] = v
    return _TPL


def esc(s):
    return html.escape(str(s), quote=True)


def href(shop, q=""):
    t = tpl().get(shop)
    if not t:
        return None
    h = t["href"]
    it = GM.item(shop, q) if q else None
    if it and it.get("url") and "{url}" in h:  # 商品データがあれば、その商品のページへ
        return GM.moshimo_item_href(h, it["url"])
    if "{url}" in h:
        if "{q}" not in (t.get("target") or ""):
            return None
        dest = t["target"].replace("{q}", urllib.parse.quote_plus(q))
        h = h.replace("{url}", urllib.parse.quote(dest, safe=""))
    return h


def ic(name):
    return f'<i class="fh-b27-ic fh-b27-ic-{name}" aria-hidden="true"></i>'


# ページごとの中身：phone=(電話占いの案内を置く直後のセクションid, 見出し, 文)、goods=(見出し, [(検索語, 表示名, ひとこと, 絵)])、before=商品を置く前のセクションid
PAGES = {
    "/tarot/": dict(
        phone=("b27-tr-play", "カードの答えを、人と話したいときは",
               "同じカードでも、読み手が変わると見えてくるものがあります。気になる1枚が出たら、占い師に直接たずねてみるのもひとつの方法です。"),
        before="b27-tr-faq",
        goods=("手もとでカードを引くなら", [
            ("タロットカード ウェイト版", "タロットカード（ウェイト版）", "このページと同じ78枚の構成。自分の手でシャッフルすると、画面とはちがう集中が生まれます。", "card"),
            ("タロット 入門 本", "タロットの入門書", "大アルカナから小アルカナまで、1枚ずつ意味をじっくり覚えたい人に。", "book")])),
    "/tarot/hexagram/": dict(
        phone=("b27-tr-play", "7枚の読みを、人と話したいときは",
               "相手の気持ちや本心のカードは、事情を話すと読み方が深まります。気になるカードが出たら、占い師にたずねてみるのもひとつの方法です。"),
        before="b27-sp-faq",
        goods=("手もとで7枚を並べるなら", [
            ("タロットカード ウェイト版", "タロットカード（ウェイト版）", "このページと同じ78枚の構成。六芒星に並べると、画面とはちがう実感があります。", "card"),
            ("タロットクロス", "タロットクロス", "カードを並べる布。7枚・10枚を広げても場所が決まり、気持ちが落ち着きます。", "card")])),
    "/tarot/celtic/": dict(
        phone=("b27-tr-play", "10枚の読みを、人と話したいときは",
               "ケルト十字は事情がからむ悩みほど読みごたえがあります。結末が気になったら、占い師に一緒に読んでもらうのもひとつの方法です。"),
        before="b27-sp-faq",
        goods=("手もとで10枚を並べるなら", [
            ("タロットカード ウェイト版", "タロットカード（ウェイト版）", "このページと同じ78枚の構成。自分の手で十字に並べると、読みが身近になります。", "card"),
            ("タロット 入門 本", "タロットの入門書", "位置ごとの読み方や組み合わせを、じっくり学びたい人に。", "book")])),
    "/kyusei/": dict(
        phone=("b27-ky-calc", "2027年の方位や転機で迷ったら",
               "引っ越し・転職・旅行の時期など、自分の星だけでは決めきれないこともあります。占い師に事情を話して一緒に考えてもらうのもひとつの方法です。"),
        before="b27-ky-faq",
        goods=("2027年の暦と方位を手もとに", [
            ("令和9年 運勢暦", "令和9年（2027年）の運勢暦", "毎日の九星・吉方位・六曜が一冊にまとまった暦。家族の分の星も引けます。", "koyomi"),
            ("方位磁石 コンパス", "方位磁石（コンパス）", "吉方位へ出かけるときや、家の中心から方角を確かめるときに。", "compass")])),
    "/shukuyo/": dict(
        phone=("b27-sk-aisho", "あの人との関係を、もっと深く知りたいときは",
               "宿の相性は関係の「形」を教えてくれますが、実際の二人の事情は人それぞれです。気になる相手がいるなら、占い師に直接相談してみる方法もあります。"),
        before="b27-sk-faq",
        goods=("月の暦をもっと身近に", [
            ("宿曜占星術 本", "宿曜占星術の本", "27宿の性格や相性を、くわしい解説で読みたい人に。", "book"),
            ("月齢カレンダー 2027", "2027年の月齢カレンダー", "宿曜は月の暦。毎日の月の形を眺めると、その日の宿の流れを感じやすくなります。", "koyomi")])),
    "/maya/": dict(
        phone=("b27-my-calc", "自分のKINの意味を、人と話したいときは",
               "紋章や音の意味は、今の暮らしに当てはめてこそ生きてきます。迷っていることがあるなら、占い師に聞いてみるのもひとつの方法です。"),
        before="b27-my-faq",
        goods=("毎日のKINを手もとで", [
            ("マヤ暦 手帳 2027", "マヤ暦の手帳（2027年）", "毎日のKINと紋章が書かれた手帳。予定と一緒にその日のエネルギーを確かめられます。", "stationery"),
            ("マヤ暦 本", "マヤ暦の本", "20の紋章・13の音・ウェイブスペルを、じっくり読み解きたい人に。", "book")])),
    "/flower/": dict(
        before="b27-fl-faq",
        goods=("誕生花を贈るなら", [
            ("誕生花 フラワーギフト", "誕生花のフラワーギフト", "誕生日の花を、そのまま花束やアレンジメントにして贈れます。", "flower"),
            ("プリザーブドフラワー 誕生日", "プリザーブドフラワー", "水やりがいらず、長く飾れる花。遠くに住む人への贈り物に。", "flower")])),
    "/compatibility/": dict(
        phone=("b27-cp-result", "相性が気になる相手がいるなら",
               "誕生日の相性は二人の「くせ」を知る手がかりです。具体的な悩みがあるときは、占い師に二人の事情を話して相談してみる方法もあります。"),
        before="b27-cp-faq",
        goods=("二人の記念日の贈り物に", [
            ("ペアネックレス 誕生石", "誕生石のペアネックレス", "二人それぞれの誕生石を選べるペアのアクセサリー。", "accessory"),
            ("ペアマグカップ 名入れ", "名入れのペアマグカップ", "名前や記念日を入れられるペアのマグ。毎日使える贈り物に。", "tableware")])),
    "/birthstone/": dict(
        before="b27-bs-faq",
        goods=("誕生石のアクセサリーを探すなら", [
            ("誕生石 ネックレス", "誕生石のネックレス", "生まれ月の石を毎日身につけられるネックレス。贈り物にも選ばれています。", "stone"),
            ("誕生石 ブレスレット 天然石", "天然石のブレスレット", "誕生日石や好きな色の石を組み合わせて、自分だけのお守りに。", "accessory")])),
    "/angel-number/": dict(
        phone=("b27-an-pick", "数字のメッセージを、人と話したいときは",
               "同じ数字を何度も見るときは、心が何かに気づいているときかもしれません。気になっていることがあるなら、占い師に直接相談してみるのもひとつの方法です。"),
        before="b27-an-faq",
        goods=("数字を書きとめておくなら", [
            ("天使 モチーフ ネックレス", "天使モチーフのネックレス", "エンジェルナンバーを思い出す小さなお守りに。羽や天使のモチーフは贈り物にも選ばれています。", "accessory"),
            ("手帳 2027 マンスリー", "2027年の手帳", "見かけた数字と、そのとき考えていたことを書きとめておくと、あとで流れを振り返れます。", "stationery")])),
    "/blood/": dict(
        phone=("b27-bl-pick", "二人のこと、もっと深く知りたいときは",
               "血液型の相性はひとつの目安です。今の二人の関係について具体的に悩んでいるなら、占い師に直接相談してみるのもひとつの方法です。"),
        before="b27-bl-faq",
        goods=("二人の記念日の贈り物に", [
            ("ペアリング シルバー", "シルバーのペアリング", "記念日やおそろいの思い出に。サイズ直しができるものを選ぶと安心です。", "accessory"),
            ("カップル ペア ギフト 名入れ", "名入れのペアギフト", "二人の名前や記念日を入れられる贈り物。毎日使う物だと、目にするたびに思い出せます。", "gift")])),
    "/omikuji/": dict(
        phone=("b27-om-draw", "おみくじの言葉が気になったら",
               "おみくじは、今日の過ごし方のヒントです。恋愛や仕事などで具体的に迷っていることがあるときは、占い師に直接相談してみるのもひとつの方法です。"),
        before="b27-om-faq",
        goods=("おみくじと一緒に持ちたい開運アイテム", [
            ("御朱印帳", "御朱印帳", "おみくじを引きに神社へ行くなら、お参りの記録に。", "omamori"),
            ("神社のお守り袋", "お守り袋", "引いたおみくじを入れて、持ち歩くのにちょうどいい大きさ。", "omamori")])),
    "/hoshi/": dict(
        phone=("b27-hs-soon", "星の動きを、自分のことに当てはめたいときは",
               "新月や逆行の日付がわかっても、自分の場合どうなるかは人それぞれです。気になる時期があるときは、占い師に直接相談してみるのもひとつの方法です。"),
        before="b27-hs-faq",
        goods=("星を見るアイテム", [
            ("星座早見盤", "星座早見盤", "新月の夜は星がよく見えます。今夜見える星座を、くるっと回して探せます。", "star"),
            ("プラネタリウム 家庭用", "家庭用プラネタリウム", "部屋の天井に星空を映して、満月や新月の夜をゆっくり過ごせます。", "star")])),
    "/hoshi/mercury-retrograde/": dict(
        phone=("b27-mr-when", "逆行中の迷いごとを、人に相談したいときは",
               "水星逆行は見直しの時期とされます。決めかねていることがあるときは、占い師に直接相談してみるのもひとつの方法です。"),
        before="b27-mr-faq",
        goods=("逆行中の「見直し」に", [
            ("手帳 2027", "2027年の手帳", "逆行と注意期間を書き込んでおくと、大事な予定をずらす目安になります。", "stationery"),
            ("星座早見盤", "星座早見盤", "空の星の動きを、自分の目で確かめてみたい人に。", "star")])),
    "/animal-color/": dict(
        phone=("b27-ac-calc", "タイプの結果を、今の悩みに生かしたいときは",
               "60タイプは性格の傾向を知る手がかりです。人間関係や恋愛で具体的に迷っているときは、占い師に直接相談してみるのもひとつの方法です。"),
        before="b27-ac-faq",
        goods=("色の力を、毎日の暮らしに", [
            ("色彩心理 本", "色の力がわかる本", "色が気持ちや印象にどう働くかを、図でわかりやすく知りたい人へ。", "book"),
            ("パワーストーン ブレスレット 選べる", "色で選べるパワーストーン", "あなたのタイプの色の石を選んで、身につけるお守りに。", "stone")])),
    "/trump/": dict(
        phone=("b27-tp-draw", "カードの答えを、人に相談したいときは",
               "トランプは気軽に答えをくれる占いです。出たカードを今の悩みにどう当てはめるか迷うときは、占い師に直接相談してみるのもひとつの方法です。"),
        before="b27-tp-faq",
        goods=("手もとのトランプで占うなら", [
            ("トランプ バイスクル", "バイスクルのトランプ", "手品にも使われる定番のトランプ。カードがすべりやすく、よく混ぜられます。", "game"),
            ("トランプ タリホー", "タリホーのトランプ", "落ち着いた裏面の模様が人気のトランプ。占い用に1組持っておくのにも。", "game")])),
    "/rune/": dict(
        phone=("b27-rn-draw", "ルーンの答えを、もっとくわしく聞きたいときは",
               "ルーンは短い言葉で答えをくれる占いです。出た答えを今の悩みにどう当てはめるか迷うときは、占い師に直接相談してみるのもひとつの方法です。"),
        before="b27-rn-faq",
        goods=("ルーン占いを手もとで", [
            ("ルーンストーン ローズクォーツ", "ルーンストーン（ローズクォーツ）", "25のルーンが刻まれた天然石のセット。袋から1つずつ引いて使えます。", "stone"),
            ("ルーンストーン アベンチュリン", "ルーンストーン（アベンチュリン）", "落ち着いた緑の石のルーン。手に取って引くと、画面とはまた違う感覚で占えます。", "stone")])),
    "/suhijutsu/": dict(
        phone=("b27-sh-calc", "数の結果を、自分の悩みに当てはめたいときは",
               "ライフパスや2027年の数は、大きな傾向を知る手がかりです。今の仕事や恋愛にどう生かすか迷うときは、占い師に直接相談してみるのもひとつの方法です。"),
        before="b27-sh-faq",
        goods=("数を書きとめて、一年を過ごすなら", [
            ("手帳 2027", "2027年の手帳", "2027年の数と月ごとの流れを書き込んでおくと、節目の月を意識しながら過ごせます。", "stationery"),
            ("数秘術 本", "数秘術の本", "12の数の意味や名前の数の出し方まで、くわしく知りたい人へ。", "book")])),
    "/366uranai/": dict(
        phone=("b27-2027", "2027年の流れを、人に相談したいときは",
               "誕生日占いでわかるのは大きな流れです。今かかえている悩みに当てはめて考えたいときは、占い師に直接相談してみるのもひとつの方法です。"),
        before="b27-faq",
        goods=("誕生日の贈り物さがしに", [
            ("誕生日プレゼント 名入れ", "名入れの誕生日プレゼント", "名前や誕生日を刻めるギフト。366日それぞれのページのラッキーアイテムと合わせて選べます。", "gift"),
            ("誕生石 ネックレス", "誕生石のネックレス", "生まれ月の石を身につけるお守りに。誕生日ページの「誕生石」と合わせてどうぞ。", "stone")])),
    "/seinengappi/": dict(
        phone=("b27-detail", "結果をもっと深く聞きたいときは",
               "いくつもの占いを並べると、当てはまるところと迷うところが出てきます。気になるところは、占い師に直接たずねてみるのもひとつの方法です。"),
        before="b27-more",
        goods=("2027年の暦と手帳", [
            ("令和9年 運勢暦", "令和9年（2027年）の運勢暦", "九星・干支・六曜が毎日わかる暦。家族の星も一冊で引けます。", "koyomi"),
            ("手帳 2027", "2027年の手帳", "このページで見た「いい月」「気をつけたい月」を書き込んでおくと、1年の計画が立てやすくなります。", "stationery")])),
}

CSS = ("<style>.fh-b27 a.fh-b27-shopbtn,.fh-b27 a.fh-b27-shopbtn:visited{color:#fff}.fh-b27 .fh-b27-shop>.fh-b27-shop-btns{grid-column:1/-1;margin-top:0}.fh-b27 .fh-b27-shop>.fh-b27-shop-btns a.fh-b27-shopbtn{flex:1 1 0;min-height:42px;font-size:14px}.fh-b27 .fh-b27-shop-prod{display:block;font-size:12px;line-height:1.5;color:#5E5546;margin-top:4px}.fh-b27 .fh-b27-shop-price{display:block;font-size:12.5px;color:#4A3F30;margin-top:2px}.fh-b27 .fh-b27-shop-price b{font-size:16px;color:#B3261E;margin:0 2px}.fh-b27 .fh-b27-shop-price small{font-size:11px;color:#7A6E5C}.fh-b27 .fh-b27-mono-btns .fh-b27-shop-price{flex-basis:100%;margin:0}.fh-b27 .fh-b27-adgoods{display:flex;flex-direction:column;gap:12px;margin:8px 0 24px}"
       ".fh-b27 .fh-b27-adgoods-h{display:flex;justify-content:space-between;align-items:baseline;gap:8px;margin:0;"
       "font-family:'Klee One',cursive;font-size:17px}"
       ".fh-b27 .fh-b27-adgoods .fh-b27-pr,.fh-b27 .fh-b27-adphone .fh-b27-pr{font-family:inherit;font-size:11px;opacity:.8}"
       ".fh-b27 .fh-b27-adphone{margin:8px 0 24px}.fh-b27 .fh-b27-adgoods-l{margin:-4px 0 0;font-size:13.5px;opacity:.9}"
       ".fh-b27 .fh-b27-shop:has(.fh-b27-shop-photo){grid-template-columns:112px minmax(0,1fr)}"
       ".fh-b27 .fh-b27-shop-pic:has(img){width:112px;height:112px;background:#fff;padding:4px;overflow:hidden;border-radius:10px}"
       ".fh-b27 .fh-b27-shop-pic a.fh-b27-shop-photo{display:block;width:100%;height:100%}"
       ".fh-b27 img[data-fh=fh-b27-shop-img]{display:block;width:100%;height:100%;object-fit:contain;background:#fff;border-radius:8px;margin:0}"
       "@media(max-width:560px){.fh-b27 .fh-b27-adgoods .fh-b27-shops{grid-template-columns:minmax(0,1fr)}}</style>")


LEADS = {'/tarot/': 'カードの意味を覚えたくなったら、手もとに1組あると便利です。楽天・Yahoo!ショッピングの商品ページへ移ります。', '/tarot/hexagram/': '画面だけでなく、手もとのカードでも並べてみたい人へ。楽天・Yahoo!ショッピングの商品ページへ移ります。', '/tarot/celtic/': '本格的な10枚引きを、手もとのカードでも試したい人へ。楽天・Yahoo!ショッピングの商品ページへ移ります。', '/kyusei/': '吉方位や月ごとの流れを、手もとの暦で毎日確かめたい人へ。楽天・Yahoo!ショッピングの商品ページへ移ります。', '/shukuyo/': '27宿や月の巡りを、もっとくわしく知りたい人へ。楽天・Yahoo!ショッピングの商品ページへ移ります。', '/maya/': '毎日のKINを手帳で確かめたい人へ。楽天・Yahoo!ショッピングの商品ページへ移ります。', '/flower/': '誕生日の花を、そのまま贈り物にしたいときに。楽天・Yahoo!ショッピングの商品ページへ移ります。', '/compatibility/': '二人の記念日に、誕生日にちなんだ贈り物を選ぶなら。楽天・Yahoo!ショッピングの商品ページへ移ります。', '/366uranai/': '誕生日の贈り物を探すときに。楽天・Yahoo!ショッピングの商品ページへ移ります。', '/seinengappi/': '診断で見た2027年の「いい月」「気をつけたい月」を、暦や手帳に書き込んでおくと1年の計画が立てやすくなります。楽天・Yahoo!ショッピングの商品ページへ移ります。', '/birthstone/': '生まれ月の石を身につけたい人・贈りたい人へ。楽天・Yahoo!ショッピングの商品ページへ移ります。', '/angel-number/': '気になる数字を書きとめたり、お守りにしたりしたい人へ。楽天・Yahoo!ショッピングの商品ページへ移ります。', '/blood/': '二人の記念日の贈り物を探すなら。楽天・Yahoo!ショッピングの商品ページへ移ります。', '/omikuji/': '神社でおみくじを引くときや、引いたあとに。楽天・Yahoo!ショッピングの商品ページへ移ります。', '/hoshi/': '新月・満月や星の動きを、実際の夜空や部屋で楽しみたい人へ。楽天・Yahoo!ショッピングの商品ページへ移ります。', '/hoshi/mercury-retrograde/': '逆行の期間を手帳に書き込んでおきたい人へ。楽天・Yahoo!ショッピングの商品ページへ移ります。', '/animal-color/': '自分のタイプの色を、身の回りに取り入れたい人へ。楽天・Yahoo!ショッピングの商品ページへ移ります。', '/trump/': '占い用に、手もとに1組あると便利です。楽天・Yahoo!ショッピングの商品ページへ移ります。', '/rune/': '画面だけでなく、手もとの石でも引いてみたい人へ。楽天・Yahoo!ショッピングの商品ページへ移ります。', '/suhijutsu/': '数のことをもっと知りたい人・一年の計画を立てたい人へ。楽天・Yahoo!ショッピングの商品ページへ移ります。'}


def phone_box(title, text):
    h = href("phone")
    if not h:
        return ""
    return (f'<div class="fh-b27-ad fh-b27-adphone"><small>{esc(title)}</small><p>{esc(text)}</p>'
            f'<a class="fh-b27-btn fh-b27-ghost" href="{esc(h)}" rel="nofollow sponsored" data-aff="phone">電話占いで相談してみる</a>'
            f'{tpl()["phone"]["impression"]}<span class="fh-b27-pr">広告を含みます</span></div>')


def goods_box(title, items, lead=""):
    boxes = []
    for q, name, why, icon in items:
        btns = "".join(
            f'<a class="fh-b27-shopbtn fh-b27-shop-{sh}" href="{esc(href(sh, q))}" rel="nofollow sponsored" data-aff="{sh}">'
            f'{lab}{"で見る" if GM.item(sh, q) else "で探す"}</a>{tpl()[sh]["impression"]}' for sh, lab in GOODS_SHOPS if href(sh, q))
        ph = GM.img_tag(q, name)
        hp = href("rakuten", q) if GM.item("rakuten", q) else (href("yahoo", q) if GM.item("yahoo", q) else None)
        pic = (f'<a class="fh-b27-shop-photo" href="{esc(hp)}" rel="nofollow sponsored" tabindex="-1" aria-hidden="true">{ph}</a>'
               if ph and hp else ic(icon))
        if not btns:
            continue
        boxes.append(f'<div class="fh-b27-shop"><div class="fh-b27-shop-pic">{pic}</div>'
                     f'<div class="fh-b27-shop-body"><small>おすすめ</small><b class="fh-b27-shop-name">{esc(name)}</b>'
                     f'<span class="fh-b27-shop-why">{esc(why)}</span>{GM.price_html(q)}</div><div class="fh-b27-shop-btns">{btns}</div></div>')
    if not boxes:
        return ""
    return (f'<aside class="fh-b27-adgoods"><p class="fh-b27-adgoods-h"><span>{esc(title)}</span>'
            f'<span class="fh-b27-pr">PR（広告）</span></p>' + (f'<p class="fh-b27-adgoods-l">{esc(lead)}</p>' if lead else "") + f'<div class="fh-b27-shops">{"".join(boxes)}</div></aside>')


def result_boxes(prefix, groups, lead="結果に合わせて選んだアイテムです。楽天・Yahoo!ショッピングの商品ページへ移ります。"):
    """占いの結果ごとの商品の箱（2026-10-18）。groups = {key: (見出し, [(検索語, 商品名, ひとこと, アイコン), ...])}。
    すべて hidden で出し、ページの JS が結果に合う id（prefix-key）だけを表示する（JS に画像タグを書かないため）"""
    return "".join(f'<div id="{prefix}-{k}" hidden>' + goods_box(t, items, lead=lead) + "</div>" for k, (t, items) in groups.items())

def inject(body, url):
    """本文に広告を入れる。目印のセクションが無いときは、その広告は入れない"""
    cfg = PAGES.get(url)
    if not cfg or not tpl():
        return body
    used = False
    if cfg.get("phone"):
        sid, title, text = cfg["phone"]
        m = re.search(rf'<section[^>]*id="{re.escape(sid)}"', body)
        box = phone_box(title, text)
        if m and box:
            end = body.find("</section>", m.end())
            if end > 0:
                end += len("</section>")
                body = body[:end] + "\n" + box + body[end:]
                used = True
    if cfg.get("goods"):
        m = re.search(rf'<section[^>]*id="{re.escape(cfg["before"])}"', body)
        box = goods_box(*cfg["goods"], lead=LEADS.get(url, ""))
        if m and box:
            body = body[:m.start()] + box + "\n" + body[m.start():]
            used = True
    return (CSS + "\n" + body) if used else body
