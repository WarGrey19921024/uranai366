"""一覧ページ（既存の固定ページ /366uranai/・ID 2743「366日生年月日占い」）の本文を作る。

使い方:
  python work/scripts/build_hub.py

出力:
  work/out/hub_366uranai.html   投入用。<!-- fh-b27:start --> 〜 <!-- fh-b27:end --> の中身（[no_toc] ＋ カスタムHTMLブロック）を
                                固定ページ ID 2743 の本文と差し替える（コードエディターに貼る）
  work/out/sample/hub.html      確認用（共通CSSを ../assets/ から読む）

中身:
  366日へのリンク（月ごと・星座つき。リンク先は /366uranai/MM-DD/）、星座12ページへのリンク、
  このページ群の作り方（使った占い・計算のしかた・出典の考え方。work/knowledge/ と work/reports/knowledge_check.md をやさしく短く）、
  ほかの占いへのリンク。デザインは誕生日ページと同じ J 夜の手帳（共通の fh-b27.css。JS は使わない）。
  見出しH1：このページだけ本文先頭の題を H1 にする（改善第2弾：このページはテーマがタイトルを出さないため）。誕生日ページ・まるごと診断は H1 なしのまま。
データ: work/data/materials_366.json（各日の星座・星座の境目の日）
"""
import datetime as dt, html, json, os, sys
import hub_extra
import aff_extra

HERE = os.path.dirname(os.path.abspath(__file__))
WORK = os.path.normpath(os.path.join(HERE, ".."))
DATA = os.path.join(WORK, "data")
OUT = os.path.join(WORK, "out")

SITE = "https://www.uranai.epoch-compass.com"
HUB = "/366uranai/"
WP_ASSET = "/wp-content/uploads/fh-b27/"
ASSET_VER = "20261012"  # build_html.py の ASSET_VER と同じにする
FONTS = ("https://fonts.googleapis.com/css2?family=Klee+One:wght@400;600&family=Shippori+Mincho:wght@600;800"
         "&family=Zen+Kaku+Gothic+New:wght@400;500;700&display=swap")
SIGNS = ["牡羊座", "牡牛座", "双子座", "蟹座", "獅子座", "乙女座", "天秤座", "蠍座", "射手座", "山羊座", "水瓶座", "魚座"]
SIGN_EN = dict(zip(SIGNS, ["aries", "taurus", "gemini", "cancer", "leo", "virgo", "libra", "scorpio", "sagittarius",
                           "capricorn", "aquarius", "pisces"]))
SIGN_HIRA = dict(zip(SIGNS, ["おひつじ座", "おうし座", "ふたご座", "かに座", "しし座", "おとめ座", "てんびん座", "さそり座",
                             "いて座", "やぎ座", "みずがめ座", "うお座"]))


def ic(name, extra=""):
    """共通CSSのイラスト（icons.py → fh-b27-icons.css）"""
    return f'<i class="fh-b27-ic fh-b27-ic-{name}{(" " + extra) if extra else ""}" aria-hidden="true"></i>'


def h2(n, icon, text):
    return f'<h2><span class="fh-b27-n">{n}</span>{ic(icon, "fh-b27-h2ic")}<span>{text}</span></h2>'


USED_IC = {"西洋占星術": "stars", "デーカン": "stars", "二十四節気・七十二候": "koyomi", "数秘術": "suhi", "干支・九星": "kyusei",
           "生まれ年でわかること": "year", "誕生花": "flower", "誕生石": "stone", "誕生日石・誕生色": "mono", "守護石・ラッキーカラー": "mono",
           "相性の良い誕生日": "compat", "2027年の月別スコア": "graph"}
LINK_IC = {"/seinengappi/": ("card", "yellow"), "/compatibility/": ("compat", "rose"), "/enmusubi/pair/": ("love", "rose"),
           "/animal-color/": ("animal", "yellow"), "/tarot/": ("stars", "lav"), "/kyusei/": ("kyusei", "sage"), "/shukuyo/": ("shuku", "blue"), "/maya/": ("maya", "yellow"), "/flower/": ("flower", "rose"), "/birthstone/": ("stone", "lav"), "/angel-number/": ("suhi", "rose"), "/blood/": ("love", "rose"), "/mbti/": ("mbti", "blue"), "/mbti-compatibility/": ("people", "blue"),
           "/kokoro/": ("kokoro", "lav"), "/kaiun/compass/": ("compass", "sage"), "/dream/": ("dream", "lav"), "/about/": ("about", "cream")}
SEASON_OF_MONTH = {12: "winter", 1: "winter", 2: "winter", 3: "spring", 4: "spring", 5: "spring",
                   6: "summer", 7: "summer", 8: "summer", 9: "autumn", 10: "autumn", 11: "autumn"}


def esc(s):
    return html.escape(str(s), quote=True)


def day_url(mmdd):
    """各日のページ：/366uranai/MM-DD/（WordPress は数字だけのスラッグを使えないため MM-DD）"""
    return f"{HUB}{mmdd[:2]}-{mmdd[2:]}/"


FX = {"/flower/": "petal", "/birthstone/": "spark", "/blood/": "heart"}  # それ以外は流れ星


def fx_layer(body, url):
    """ページ上部の飾りの動き（流れ星・花びら・きらめき・ハート）。CSSだけ・押せない・動きを減らす設定なら止める（2026-10-16 本人の要望）"""
    kind = FX.get(url, "star")
    if kind == "star":
        items = "".join(f'<i style="--x:{x}%;--y:{y}px;--d:{d}s;--t:{t}s"></i>' for x, y, d, t in ((78, 10, 0, 7), (55, 40, 2.6, 9), (92, 90, 5.1, 8), (35, 0, 7.4, 11)))
        css = (".fh-b27-fx i{position:absolute;left:var(--x);top:var(--y);width:120px;height:2px;border-radius:2px;background:linear-gradient(90deg,rgba(255,255,255,0),rgba(255,255,255,.9));"
               "transform:rotate(-35deg);opacity:0;animation:fh-b27-fx-star var(--t) linear var(--d) infinite}"
               "@keyframes fh-b27-fx-star{0%{opacity:0;transform:rotate(-35deg) translateX(0)}3%{opacity:1}10%{opacity:0;transform:rotate(-35deg) translateX(-260px)}100%{opacity:0;transform:rotate(-35deg) translateX(-260px)}}")
    elif kind == "petal":
        items = "".join(f'<i style="--x:{x}%;--d:{d}s;--t:{t}s;--s:{sz}px"></i>' for x, d, t, sz in ((10, 0, 9, 12), (30, 3, 11, 9), (52, 1.5, 10, 14), (70, 5, 12, 10), (88, 2.2, 9.5, 12), (42, 7, 13, 8)))
        css = (".fh-b27-fx i{position:absolute;left:var(--x);top:-20px;width:var(--s);height:calc(var(--s)*.8);border-radius:80% 0 80% 0;background:linear-gradient(135deg,#FFD3DB,#F29BB0);opacity:0;"
               "animation:fh-b27-fx-fall var(--t) linear var(--d) infinite}"
               "@keyframes fh-b27-fx-fall{0%{opacity:0;transform:translate(0,0) rotate(0)}10%{opacity:.85}90%{opacity:.7}100%{opacity:0;transform:translate(-60px,420px) rotate(320deg)}}")
    elif kind == "spark":
        items = "".join(f'<i style="--x:{x}%;--y:{y}px;--d:{d}s"></i>' for x, y, d in ((12, 30, 0), (40, 12, 1.2), (66, 60, .6), (86, 20, 1.8), (24, 140, 2.4), (74, 170, 3), (52, 110, .3)))
        css = (".fh-b27-fx i{position:absolute;left:var(--x);top:var(--y);width:12px;height:12px;background:#fff;clip-path:polygon(50% 0,60% 40%,100% 50%,60% 60%,50% 100%,40% 60%,0 50%,40% 40%);"
               "opacity:0;animation:fh-b27-fx-tw 3.2s ease-in-out var(--d) infinite}"
               "@keyframes fh-b27-fx-tw{0%,100%{opacity:0;transform:scale(.3) rotate(0)}50%{opacity:.95;transform:scale(1) rotate(45deg)}}")
    else:  # heart
        items = "".join(f'<i style="--x:{x}%;--d:{d}s;--t:{t}s">♡︎</i>' for x, d, t in ((8, 0, 8), (26, 2.4, 10), (48, 1, 9), (68, 3.6, 11), (88, 1.8, 8.5)))
        css = (".fh-b27-fx i{position:absolute;left:var(--x);bottom:-20px;font-style:normal;font-size:20px;color:rgba(255,183,195,.8);opacity:0;animation:fh-b27-fx-up var(--t) ease-in var(--d) infinite}"
               "@keyframes fh-b27-fx-up{0%{opacity:0;transform:translateY(0) scale(.6)}15%{opacity:.9}100%{opacity:0;transform:translateY(-360px) scale(1.2)}}")
    layer = (f'<style>.fh-b27 .fh-b27-note{{position:relative}}.fh-b27-fx{{position:absolute;left:0;right:0;top:0;height:420px;overflow:hidden;pointer-events:none;z-index:0}}'
             f'.fh-b27 .fh-b27-note>*:not(.fh-b27-fx){{position:relative;z-index:1}}{css}'
             f'@media (prefers-reduced-motion:reduce){{.fh-b27-fx{{display:none}}}}</style>'
             f'<div class="fh-b27-fx" aria-hidden="true">{items}</div>')
    mk = '<div class="fh-b27-note">'
    return body.replace(mk, mk + layer, 1) if mk in body else body


def shell(title, desc, url, body, sample, scripts=()):
    """ページ全体（確認用の <html> つき）。WordPress に貼るのは fh-b27:start 〜 fh-b27:end の中身。
    先頭に [no_toc]（Table of Contents Plus の目次を出さない）、本文はカスタムHTMLブロックで包む。
    <!--OffDef--> で WP QUADS の自動挿入を止める（広告の位置は本文の <!--Ads1--> などで決める）。"""
    body = aff_extra.inject(body, url)  # 広告（アフィリエイト。2026-10-16〜）
    pre = "../assets/" if sample else WP_ASSET
    v = "" if sample else f"?v={ASSET_VER}"  # 共通CSS/JSの版（build_html.py と同じ）
    tail = "".join(f'\n<script src="{pre}{s}{v}"></script>' for s in scripts)
    # 2026-10-16 テーマ（Diver）の表の白い背景＋こちらの淡い文字で読めなくなるのを、全ページで防ぐ
    fix = ("<style>.fh-b27 .fh-b27-note table th,.fh-b27 .fh-b27-note table td{background-color:transparent;color:inherit}"
           ".fh-b27 .fh-b27-note table thead th{background-color:rgba(255,255,255,.08)}"
           ".fh-b27 .fh-b27-note table tbody th{background-color:rgba(255,255,255,.05)}</style>")
    body = fix + "\n" + fx_layer(body, url)
    inner = f'''<!--OffDef-->
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="{FONTS}" rel="stylesheet">
<link rel="stylesheet" href="{pre}fh-b27.css{v}">
{body}{tail}'''
    wp = inner if sample else f"[no_toc]\n<!-- wp:html -->\n{inner}\n<!-- /wp:html -->"
    note = "確認用（WordPress には out/ の同名ページの中身を貼る）" if sample else f"WordPress の本文に貼るのはここから（URL: {url}）"
    return f'''<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
<link rel="canonical" href="{SITE}{url}">
<style>/* 確認用（WordPressでは不要） */body{{margin:0;background:#141824}}</style>
</head>
<body>
<!-- fh-b27:start  {note} -->
{wp}
<!-- fh-b27:end -->
</body>
</html>
'''


def sign_ranges(mats):
    """星座ごとの「M/D〜M/D」（materials_366.json の星座＝1930〜2027年の平均の太陽の位置）"""
    order = sorted(mats)
    out = {}
    for s in SIGNS:
        ks = [k for k in order if mats[k]["sign"] == s]
        if s == "山羊座":  # 年をまたぐ
            ks = [k for k in ks if k >= "0601"] + [k for k in ks if k < "0601"]
        a, b = ks[0], ks[-1]
        out[s] = f"{int(a[:2])}/{int(a[2:])}〜{int(b[:2])}/{int(b[2:])}"
    return out


def month_heading(mats, m):
    ks = [k for k in sorted(mats) if int(k[:2]) == m]
    parts, cur = [], None
    for k in ks:
        s = mats[k]["sign"]
        if s != cur:
            parts.append([s, k, k])
            cur = s
        else:
            parts[-1][2] = k
    return "／".join(f"{int(a[2:])}〜{int(b[2:])}日 {s}" for s, a, b in parts)


LINKS = [
    ("/seinengappi/", "生年月日まるごと診断", "星座・九星・干支・四柱推命・宿曜・マヤ暦・数秘・動物×色を1枚に"),
    ("/compatibility/", "誕生日相性占い", "2人の生年月日で相性を見る"),
    ("/enmusubi/pair/", "ご縁の相性診断", "縁結び診断室"),
    ("/tarot/", "タロット占い", "78枚の意味と1枚引き・3枚引き・Yes/No"),
    ("/kyusei/", "九星気学", "本命星と2027年の運勢・年盤"),
    ("/shukuyo/", "宿曜占星術", "本命宿と三九の秘法の相性"),
    ("/maya/", "マヤ暦占い", "KIN・太陽の紋章・銀河の音"),
    ("/blood/", "血液型相性占い", "A・B・O・AB型の恋愛・友達・仕事の相性"),
    ("/angel-number/", "エンジェルナンバー", "111・1111・1234など、よく見る数字の意味"),
    ("/flower/", "誕生花一覧", "366日の誕生花と花言葉"),
    ("/birthstone/", "誕生石一覧", "1月〜12月の誕生石と366日の誕生日石"),
    ("/animal-color/", "動物×色占い", "生年月日で60タイプ"),
    ("/mbti/", "MBTI占い", "性格タイプで見る2027年"),
    ("/mbti-compatibility/", "MBTI相性占い", "性格タイプどうしの相性"),
    ("/kokoro/", "心コンパス", "エニアグラム・ビッグファイブで性格を深く知る"),
    ("/kaiun/compass/", "8方位の読み方", "開運ライフ｜本命星の吉方位に"),
    ("/dream/", "夢解き図鑑", "気になる夢の意味を調べる"),
    ("/about/", "このサイトについて", "作成方針・運営者"),
]

USED = [
    ("西洋占星術", "12星座",
     "太陽の通り道（黄道）を春分点から30度ずつ12に分けた、季節を基準にした星座（トロピカル方式）です。"
     "各誕生日の太陽の位置は、1930〜2027年のその日の正午（日本時間）の位置の平均から求めました。"
     "太陽が星座を移る時刻は年によって違うので、境目の日のページには「生まれた年と時刻で星座が変わる」と書いています。"),
    ("デーカン", "星座を3つに分ける",
     "1つの星座を10度ずつ3つに分け、それぞれに支配星を当てます。日本の誕生日占いで広く使われている"
     "「トリプリシティ方式」（同じエレメントの星座の味が加わる、と説明できる方式）を選びました。"),
    ("二十四節気・七十二候", "暦の季節",
     "太陽が15度進むごとの節気、5度ごとの候です。名前は明治以降の暦（略本暦）のもの。"
     "その日がどの候に当たるかは年によって1日ほど動くため、境目の日はそのことも書いています。"),
    ("数秘術", "誕生日の数・2027年の数",
     "誕生日の「日」の数字から出す誕生日の数と、生年月日から出す2027年の数（パーソナルイヤー）を使います。"
     "ライフパスは生年月日の数字をすべて足す方式です（流派によって11・22・33の出方が変わります）。"),
    ("干支・九星", "2027年は丁未・九紫火星",
     "2027年は丁未（ひのと・ひつじ）、九星は九紫火星が中央に入る年です。"
     "暦の月は節入り（立春・啓蟄など）で、年は立春で切り替わる、日本で一般的な決まりで計算しています。"),
    ("生まれ年でわかること", "四柱推命・宿曜・マヤ暦ほか",
     "各ページで生まれ年を選ぶと、本命星・四柱推命（年柱・月柱・日柱）・宿曜（旧暦の月日から出す本命宿）・"
     "マヤ暦（ドリームスペル方式。古代マヤの暦そのものとは別物）・ライフパス・バイオリズム・動物×色占い（当サイト独自の60タイプ）が出ます。"
     "生まれ年は送信も保存もしません。"),
    ("誕生花", "日本花普及センター",
     "日本花普及センターの「誕生花」一覧によります。花言葉も同じ一覧からとっています。"),
    ("誕生石", "全国宝石卸商協同組合（2021年）",
     "月ごとの誕生石は、全国宝石卸商協同組合が2021年に改定した一覧（全29石）によります。"),
    ("誕生日石・誕生色", "広く使われている一覧",
     "公式の決まりはありませんが、多くのサイトやお店で同じ系統の一覧が使われています（もとは斉藤貴子『366日誕生石の本』、野村順一『誕生色事典』とされます）。"
     "宝石店・メディアなど複数の一覧を突き合わせ、2つ以上で一致したものを載せています。"),
    ("守護石・ラッキーカラー", "当サイト独自の選び方",
     "ラッキーカラーは日本の伝統色から、その日の七十二候や誕生花にちなんで選び、隣の日とは必ず変えています。"
     "守護石は、その月の誕生石とは別の石を、デーカンの支配星に対応する石やラッキーカラーに近い石の中から、実際に販売されている石だけで選んでいます。"),
    ("相性の良い誕生日", "当サイト独自の決め方",
     "2人の太陽の位置がつくる角度（調和しやすい角度・ぶつかりやすい角度）と、誕生日の数のグループ"
     "（行動派1・5・7／堅実派2・4・8／表現派3・6・9）の組み合わせで選びます。"
     "366日の中から「お互いに」選んでいるので、AのページにBが出ていれば、BのページにもAが出ています。"),
    ("2027年の月別スコア", "当サイト独自の決め方",
     "星座（2027年の太陽・金星・火星・木星・土星の動き）・数秘（その月の数）・暦の五行（その月の干支）の3つを"
     "20〜100点にそろえて平均しました。◎は366日×12か月の中で上位4分の1、△は下位4分の1です。"
     "生まれ年を選ぶと、九星とバイオリズムの線もグラフに加わります。"),
]


YC_CSS = """<style>
.fh-b27-yc{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:14px}
.fh-b27-yc-m{border:1.5px solid var(--line);border-radius:12px;background:var(--deep);padding:10px 12px;scroll-margin-top:80px}
.fh-b27 .fh-b27-yc-m h3{margin:0 0 6px;font-size:18px;display:flex;flex-direction:column;gap:2px}
.fh-b27 .fh-b27-yc-m h3 small{font-family:'Zen Kaku Gothic New',sans-serif;font-size:11.5px;font-weight:400;color:var(--mute);line-height:1.5}
.fh-b27-yc-d{display:grid;grid-template-columns:repeat(7,minmax(0,1fr));gap:4px}
.fh-b27 .fh-b27-yc-d a{display:flex;align-items:center;justify-content:center;min-height:36px;border-radius:6px;background:rgba(255,255,255,.04);border:1px solid var(--line);
 text-decoration:none;color:var(--ink);font-family:'Klee One',cursive;font-size:15px;font-weight:600}
.fh-b27 .fh-b27-yc-d a:hover,.fh-b27 .fh-b27-yc-d a:focus-visible{border-color:var(--gold);color:var(--gold);outline:none}
.fh-b27 .fh-b27-yc-d a.fh-b27-bd{border-style:dashed;border-color:var(--gold)}
.fh-b27 .fh-b27-yc-d a.is-today{background:var(--gold);color:var(--paper);border-color:var(--gold)}
@media (max-width:900px){.fh-b27-yc{grid-template-columns:repeat(2,minmax(0,1fr))}}
.fh-b27 .fh-b27-hx-go label{width:100%;font-size:14px;color:var(--sub)}
@media (max-width:560px){.fh-b27-yc{grid-template-columns:1fr}.fh-b27 .fh-b27-yc-d a{min-height:40px}.fh-b27-hero .fh-b27-kou{display:none}}
</style>"""


def build(mats, sample, updated):
    rng = sign_ranges(mats)
    H = []
    a = H.append
    a('<div class="fh-b27">\n<div class="fh-b27-note">')
    a('''<header class="fh-b27-hero">
  <div class="fh-b27-kou" aria-hidden="true">三百六十六日</div>
  <div class="fh-b27-hero-body">
    <span class="fh-b27-tape">2027年版 誕生日占い</span>
    <h1 class="fh-b27-title">誕生日占い 366日<br>あなたの誕生日のページを探す</h1>
    <p class="fh-b27-lead">ここは、366日の誕生日占い（2027年版）の入口です。誕生日を選ぶと、その日生まれの人だけのページ（性格・相性の良い誕生日・誕生花・同じ誕生日の有名人・2027年の月ごとの運勢）が開きます。すべて無料です。</p>
    ''' + hub_extra.picker(mats) + '''
  </div>
</header>''')
    PROMO = '''<a class="fh-b27-promo" href="/seinengappi/">
  <i class="fh-b27-ic fh-b27-ic-card fh-b27-promoic" aria-hidden="true"></i><small>生まれた年までわかる人は</small>
  <b>生年月日まるごと診断 →</b>
  <span>星座・九星・干支・四柱推命・宿曜・マヤ暦・数秘・動物×色を、1枚のカードにまとめて表示します。</span>
</a>'''
    a('''<nav class="fh-b27-toc" aria-label="目次">
  <strong>目次</strong>
  <ol>
    <li><a href="#b27-days">誕生日から探す（366日のカレンダー）</a></li>
    <li><a href="#b27-signs">星座から探す</a></li>
    <li><a href="#b27-know">誕生日のページで読めること</a></li>
    <li><a href="#b27-2027">2027年はどんな年？</a></li>
    <li><a href="#b27-month">誕生月ごとの特徴</a></li>
    <li><a href="#b27-table">366日の早見表（星座・誕生花・七十二候）</a></li>
    <li><a href="#b27-faq">よくある質問</a></li>
    <li><a href="#b27-how">この占いの作り方と出典</a></li>
  </ol>
</nav>''')

    # 1 誕生日から選ぶ
    a(YC_CSS)
    a(f'''<section class="fh-b27-sec" id="b27-days">
  {h2(1, "cake", "誕生日から探す")}
  <p>366日のカレンダーです。誕生日の数字を押すと、その日のページが開きます。今日の日付には印がつきます。</p>
  <div class="fh-b27-yc">''')
    for m in range(1, 13):
        ks = [k for k in sorted(mats) if int(k[:2]) == m]
        a(f'''  <div class="fh-b27-yc-m" id="b27-m{m:02d}">
    <h3>{m}月<small>{esc(month_heading(mats, m))}</small></h3>
    <div class="fh-b27-yc-d">''')
        for k in ks:
            e = mats[k]
            d = int(k[2:])
            s = e["sign"]
            if e["sign_border"]:
                other = "・".join(e["sign_border_other"])
                lab = f"{m}月{d}日生まれ（{s}。年と時刻によっては{other}）"
                a(f'      <a class="fh-b27-bd" data-md="{k}" href="{day_url(k)}" aria-label="{esc(lab)}" title="{esc(lab)}">{d}</a>')
            else:
                lab = f"{m}月{d}日生まれ（{s}）"
                a(f'      <a data-md="{k}" href="{day_url(k)}" aria-label="{esc(lab)}" title="{esc(lab)}">{d}</a>')
        a('    </div>\n  </div>')
    a('''  </div>
  <p class="fh-b27-small">点線の日は星座の境目の日です。太陽が星座を移る時刻は年によって違うので、生まれた年と時刻によっては隣の星座になります（くわしくは各ページに書いています）。</p>
</section>''')
    a("<script>(function(){var n=new Date(),k=('0'+(n.getMonth()+1)).slice(-2)+('0'+n.getDate()).slice(-2),e=document.querySelector('.fh-b27-yc [data-md=\\''+k+'\\']');if(e){e.classList.add('is-today');e.setAttribute('aria-current','date');}})();</script>")
    a("<!--Ads1-->")

    # 2 星座から選ぶ
    a(f'''<section class="fh-b27-sec" id="b27-signs">
  {h2(2, "stars", "星座から探す")}
  <p>星座ごとの性格と2027年の運勢は、星座のページにまとめています。</p>
  <div class="fh-b27-signs">''')
    for s in SIGNS:
        a(f'    <a href="/{SIGN_EN[s]}/">{ic(SIGN_EN[s], "fh-b27-signic")}<span><b>{SIGN_HIRA[s]} →</b><small>{rng[s]}生まれ</small></span></a>')
    a('''  </div>
  <p class="fh-b27-small">日付は、1930〜2027年の太陽の位置の平均から決めたものです。境目の日は年によって前後します。</p>
</section>''')
    a(PROMO)

    def HOW(k):
        o = []
        a2 = o.append
        a2(f'''<section class="fh-b27-sec" id="b27-how">
  {h2(k, "links", "この占いの作り方と出典")}
  <p>366日のページを、どんな材料と決め方で作っているかをまとめました。押すと開きます。</p>
  <div class="fh-b27-hx-list"><details><summary>このページ群の作り方</summary>
  <p>366日のページは、日ごとに<b>その日にしかない材料</b>を集めてから書いています。太陽の星座とデーカン、七十二候、誕生花、誕生日の数、その日の記念日、同じ誕生日の有名人などです。</p>
  <p>はじめに366日分の材料を1つの表にまとめ、どの日も必ずその日の材料を使って文章を書きました。書いたあとは、<b>別の日と同じような文章になっていないかを機械で調べ</b>、似すぎているところは書き直しています。</p>
  <p>1ページは2部に分かれています。第1部は<b>ずっと変わらない本質</b>（性格・暦と星・誕生花と誕生石・相性・有名人）、第2部は<b>2027年の運勢</b>（分野別の運勢・月別のグラフ・12か月の運勢・ラッキーカラーなど）です。生まれ年を選ぶと、あなた専用の結果も加わります。</p>
</details>''')
        a2('''<details><summary>使った占いと出典</summary>
  <dl class="fh-b27-koyomi fh-b27-kcards">''')
        for name, sub, text in USED:
            a2(f'    <div>{ic(USED_IC.get(name, "stars"), "fh-b27-kcic")}<dt><b>{esc(name)}</b>{esc(sub)}</dt><dd>{esc(text)}</dd></div>')
        a2('''  </dl>
  <p class="fh-b27-small">同じ誕生日の有名人は、運営者がまとめた一覧から載せています。文章はすべてこのサイトで書いたものです。</p>
</details><details><summary>計算のしかた</summary>
  <p>太陽や月、惑星の位置は、天文計算のプログラム（Swiss Ephemeris）で求めています。二十四節気・七十二候・干支・九星・旧暦・宿曜は、その計算で出した日時（日本時間）から決めました。<b>手で書き写した日付や、記憶にたよった値は使っていません。</b></p>
  <p>計算の結果は、外の資料とも突き合わせています。2027年の二十四節気は国立天文台の暦要項と24件すべて日付が一致し、日食・月食はNASAの一覧と、干支・九星・旧正月・マヤ暦も公開されている値と一致することを確かめました。</p>
  <p>生まれた時刻はわからないので、<b>正午（日本時間）に生まれたとして計算</b>しています。節入りの日（月や年の干支が切り替わる日）や星座の境目の日は、生まれた時刻で結果が変わることがあるため、各ページにそのことを書いています。</p>
</details><details><summary>出典の考え方</summary>
  <ul class="fh-b27-acts">
    <li><span><b>計算で出せるものは計算で</b>天体・節気・干支・九星・旧暦・宿曜・マヤ暦・数秘は、決まった式で計算して出しています。</span></li>
    <li><span><b>計算できないものは、出典を1つに決める</b>誕生花は日本花普及センター、誕生石は全国宝石卸商協同組合（2021年）の一覧だけを使い、ほかのサイトの値と混ぜていません。</span></li>
    <li><span><b>流派が分かれるものは、日本で一般的な方式を1つ</b>デーカンはトリプリシティ方式、ライフパスは全部の数字を足す方式、宿曜は旧暦の月日から出す方式、マヤ暦はドリームスペル方式です。</span></li>
    <li><span><b>決まった出典がないものは「当サイト独自」と書く</b>守護石・ラッキーカラー・相性の選び方・月別スコア・動物×色占いは、このサイトで作った決め方です。各ページにもそう書いています。</span></li>
  </ul>
  <p class="fh-b27-small">占いは、自分を振り返るきっかけや、毎日の楽しみとしてお読みください。バイオリズムは科学的な根拠が認められていない読み物として扱っています。</p>
</details></div>
</section>''')
        return "\n".join(o)


    # 2026-10-15 検索向けの解説を追加（hub_extra.py）
    extra, n = hub_extra.sections(mats, 3, h2)
    a(extra)
    a(hub_extra.faq(n, h2))
    a(HOW(n + 1))
    # ほかの占い
    a(f'''<section class="fh-b27-sec" id="b27-more">
  {h2(n + 2, "omikuji", "ほかの占い")}
  <div class="fh-b27-lcards">''')
    for href, b, small in LINKS:
        icn, tone = LINK_IC.get(href, ("goods", "cream"))
        a(f'    <a class="fh-b27-lcard" href="{href}"><span class="fh-b27-eye fh-b27-eye-{tone}">{ic(icn)}</span>'
          f'<span class="fh-b27-lbody"><b>{esc(b)} →</b><small>{esc(small)}</small></span></a>')
    a('''  </div>
</section>''')
    up = dt.date.fromisoformat(updated)
    a(f'<p class="fh-b27-foot">366日の誕生日占い（2027年版）は、西洋占星術・七十二候・数秘術・干支と九星・誕生花・誕生石をもとに、計算で出した暦の値を使って作っています。<br>'
      f'最終更新日：{up.year}年{up.month}月{up.day}日／<a href="/about/">この記事の作成方針について</a></p>')
    a("</div>\n</div>")
    body = "\n".join(H)
    title = "誕生日占い｜366日の生年月日占いで性格・相性・2027年の運勢【無料】"
    desc = ("366日の誕生日占い（2027年版）。誕生日・生年月日から性格、相性の良い誕生日、誕生花と誕生石、同じ誕生日の有名人、"
            "2027年の月別の運勢まで無料でわかります。366日の星座・誕生花・七十二候の早見表と、誕生月ごとの特徴も。")
    return shell(title, desc, HUB, body, sample)


def main():
    updated = sys.argv[1] if len(sys.argv) > 1 else dt.date.today().isoformat()
    mats = json.load(open(os.path.join(DATA, "materials_366.json"), encoding="utf-8"))
    assert len(mats) == 366, len(mats)
    os.makedirs(os.path.join(OUT, "sample"), exist_ok=True)
    for sample, path in ((False, os.path.join(OUT, "hub_366uranai.html")), (True, os.path.join(OUT, "sample", "hub.html"))):
        page = build(mats, sample, updated)
        with open(path, "w", encoding="utf-8") as f:
            f.write(page)
        print("→", os.path.relpath(path, WORK), f"（日へのリンク {page.count('href=\"/366uranai/')}本）")


if __name__ == "__main__":
    main()
