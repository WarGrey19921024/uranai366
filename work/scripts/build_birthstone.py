"""誕生石のページ（新規の固定ページ /birthstone/）を作る（2026-10-16。検索「誕生石」1万〜10万／月）。
作る前の確認：WordPress の固定ページ・投稿、静的ページ（sitemap-static.xml）に誕生石のページは無い（/stone/ /birthstone/ 等は404）。

中身
- 誕生日を選ぶと「あなたの宝石箱」（月の誕生石・誕生日石・誕生色）が開く
- 1月〜12月の誕生石の早見表、月ごとの石と意味（全29石）、2021年の改定で増えた10石、色から選ぶ誕生石
- 366日の誕生日石の一覧（当サイト独自の選び方。366日の誕生日ページと同じ値）
- 選び方・贈り方・お手入れ、FAQ
データ
- 月の誕生石：全国宝石卸商協同組合 2021年12月改定（全29石）＝ work/knowledge/10_誕生日もの.md の確定表
- 石の別名・色・言い伝え：work/data/src_stones.json（言い伝えは自分の言葉で要約したもの）
- 誕生日石・誕生色：work/data/materials_366.json（誕生日ページと同じ値）
使い方: python work/scripts/build_birthstone.py [最終更新日]
出力: work/out/birthstone.html（投入用）、work/out/sample/birthstone.html（確認用）
"""
import collections, datetime as dt, html, json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from build_hub import OUT, WORK, DATA, shell  # noqa: E402
import aff_extra
STD = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "bday_standard_366.json"), encoding="utf-8"))["days"]  # noqa: E402

URL = "/birthstone/"
DAYS = {1: 31, 2: 29, 3: 31, 4: 30, 5: 31, 6: 30, 7: 31, 8: 31, 9: 30, 10: 31, 11: 30, 12: 31}
# 2021年改定（全国宝石卸商協同組合）。knowledge/10_誕生日もの.md の確定表と同じ
MONTHS = {1: ["ガーネット"], 2: ["アメシスト", "クリソベリル・キャッツアイ"],
          3: ["アクアマリン", "サンゴ", "ブラッドストーン", "アイオライト"], 4: ["ダイヤモンド", "モルガナイト"],
          5: ["エメラルド", "ヒスイ"], 6: ["真珠", "ムーンストーン", "アレキサンドライト"], 7: ["ルビー", "スフェーン"],
          8: ["サードオニックス", "ペリドット", "スピネル"], 9: ["サファイア", "クンツァイト"], 10: ["オパール", "トルマリン"],
          11: ["トパーズ", "シトリン"], 12: ["ターコイズ", "ラピスラズリ", "タンザナイト", "ジルコン"]}
ADDED_2021 = {"クリソベリル・キャッツアイ", "ブラッドストーン", "アイオライト", "モルガナイト", "アレキサンドライト",
              "スフェーン", "スピネル", "クンツァイト", "タンザナイト", "ジルコン"}
# 石ごとのひとこと（キーワード）。言い伝え（src_stones.json の meaning）から自分の言葉で短くしたもの
KEY = {"ガーネット": "実り・友情・努力", "アメシスト": "誠実・心の平静", "クリソベリル・キャッツアイ": "魔よけ・見通し",
       "アクアマリン": "航海の守り・幸せな結婚", "サンゴ": "魔よけ・長寿", "ブラッドストーン": "勇気・粘り強さ",
       "アイオライト": "道しるべ・方向", "ダイヤモンド": "永遠の絆・意志", "モルガナイト": "優しさ・愛情",
       "エメラルド": "再生・希望", "ヒスイ": "徳・長寿", "真珠": "純粋・円満", "ムーンストーン": "恋人の石・旅の守り",
       "アレキサンドライト": "二面性の調和", "ルビー": "情熱・勇気", "スフェーン": "ひらめき・知恵",
       "サードオニックス": "夫婦の幸せ・家庭円満", "ペリドット": "太陽の石・明るさ", "スピネル": "秘めた力",
       "サファイア": "誠実・慈愛", "クンツァイト": "無償の愛・穏やかさ", "オパール": "希望・美しさ",
       "トルマリン": "才能・個性", "トパーズ": "希望・友情", "シトリン": "明るさ・豊かさ", "ターコイズ": "旅の安全・守り",
       "ラピスラズリ": "聖なる石・瑠璃", "タンザナイト": "冷静さ・決断", "ジルコン": "安らぎ・知恵"}
MONTH_TEXT = {  # 月ごとの紹介（手書き）
    1: "1月の誕生石はガーネットひとつだけ。深い赤は、寒さの中で新しい年を始める力強さにも重なります。石の名は、粒が実のように集まるザクロにちなむと言われ、実りや努力が報われることの象徴とされてきました。",
    2: "2月は紫のアメシストと、光の筋が浮かぶクリソベリル・キャッツアイ。落ち着いた紫は心を静める石、猫の目のような光は見通しのよさの石とされ、どちらも「冷静に見きわめる」という共通点があります。",
    3: "3月は4つの石が選ばれた月です。海の色のアクアマリン、海から生まれるサンゴ、緑に赤い斑点のブラッドストーン、見る向きで色が変わるアイオライト。海と旅にまつわる言い伝えが多く、旅立ちの季節らしい顔ぶれです。",
    4: "4月はダイヤモンドと、やわらかな桃色のモルガナイト。いちばん硬い宝石と、春の花のような色の石の組み合わせで、変わらない意志と、人を思いやる優しさの両方を表します。",
    5: "5月は新緑の色の石がそろう月。エメラルドは若葉のような緑で再生の象徴、ヒスイは日本で縄文時代から勾玉に使われてきた石です。同じ緑でも、華やかさと素朴さの違いがあります。",
    6: "6月は真珠、ムーンストーン、アレキサンドライト。貝の中で育つ真珠と、月の光を思わせるムーンストーンは、どちらも月にたとえられてきた石です。灯りで色が変わるアレキサンドライトが2021年に加わりました。",
    7: "7月は真っ赤なルビーと、七色にきらめくスフェーン。ルビーは「宝石の王」と呼ばれた情熱の石、スフェーンはダイヤモンドを上回るきらめきを持つ石です。夏の日差しのような、まぶしさのある組み合わせです。",
    8: "8月は縞模様のサードオニックス、明るい緑のペリドット、ルビーと間違われてきたスピネル。家庭円満、太陽の明るさ、内に秘めた力と、暮らしを支える言い伝えが並びます。",
    9: "9月は青のサファイアと、淡い桃紫色のクンツァイト。サファイアは天の青を映す誠実の石、クンツァイトは20世紀に名づけられた新しい石で、穏やかな愛情を表すとされます。",
    10: "10月は色の豊かな2つの石。虹のような遊色のオパールと、1つの石の中に何色もあることがあるトルマリンです。どちらも「同じものが2つとない」個性の石と言えます。",
    11: "11月は黄色から橙色の石が並ぶ月。トパーズとシトリンは、秋の実りや夕日のような温かい色で、希望や豊かさを表す石とされています。",
    12: "12月は4つの石。青緑のターコイズ、瑠璃色のラピスラズリ、夕暮れの空のようなタンザナイト、強い輝きのジルコン。冬の夜空のような青の石がそろい、旅の守りや知恵の言い伝えが目立ちます。",
}
COLOR_ORDER = ["赤", "桃", "橙", "黄", "緑", "青", "藍", "紫", "白", "透明", "茶", "多色"]
COLOR_TEXT = {"赤": "情熱や勇気の色", "桃": "優しさや愛情の色", "橙": "温かさの色", "黄": "明るさや豊かさの色",
              "緑": "再生や希望の色", "青": "誠実さや冷静さの色", "藍": "深い知恵の色", "紫": "心の静けさの色",
              "白": "純粋さの色", "透明": "まっすぐな意志の色", "茶": "落ち着きの色", "多色": "個性の色"}
CARE = [("水・汗・薬品に弱い石", "真珠・サンゴ・オパール・ターコイズ・ラピスラズリ",
         "汗や化粧品、洗剤がつくと、つやが落ちたり色が変わったりすることがあります。身につけたあとは柔らかい布でふき、香水やクリームは石をつける前に。"),
        ("ぶつけると割れやすい石", "トパーズ・クンツァイト・タンザナイト・スフェーン・アイオライト",
         "ある方向に割れやすい性質（へき開）があります。硬い場所にぶつけないようにし、指輪なら家事のときは外すと安心です。"),
        ("光で色があせることがある石", "クンツァイト・アメシスト",
         "強い日光に長く当てると、色が薄くなることがあります。しまうときは暗い場所に。"),
        ("毎日使いやすい硬い石", "ダイヤモンド・ルビー・サファイア・アレキサンドライト・スピネル",
         "硬くて傷がつきにくく、婚約指輪や毎日つける指輪にも選ばれます。ただし硬い石同士がこすれると傷がつくので、しまうときは別々に。")]
USE = [("贈り物に", "相手の誕生月の石を選ぶのが基本です。誕生石が2つ以上ある月は、相手の好きな色や、言い伝えで選べます。誕生日石を添えると、その人だけの石になります。"),
       ("婚約指輪・記念日に", "二人の誕生石を並べたり、結婚記念日の月の石を選んだりする方法があります。毎日つける指輪なら、硬い石を選ぶと長く楽しめます。"),
       ("赤ちゃんの誕生に", "生まれた月の石を、出産祝いや記念品にする人もいます。小さいうちは口に入れないよう、飾って楽しむのが安心です。"),
       ("自分のお守りに", "自分の誕生石や誕生日石を、言い伝えを思い出すきっかけとして身につけます。石の力を信じるかどうかより、気持ちを整える目印として使うのがおすすめです。")]
FAQ = [
    ("誕生石は誰が決めているのですか。",
     "日本では、全国宝石卸商協同組合が1958年に初めて定め、2021年12月に63年ぶりに改定しました。改定には一般社団法人日本ジュエリー協会と山梨県水晶宝飾協同組合が賛同しています。このページは2021年の改定（全29石）に沿っています。"),
    ("2021年の改定で何が変わったのですか。",
     "10の石が加わり、19石から29石になりました。加わったのは、クリソベリル・キャッツアイ（2月）、ブラッドストーン・アイオライト（3月）、モルガナイト（4月）、アレキサンドライト（6月）、スフェーン（7月）、スピネル（8月）、クンツァイト（9月）、タンザナイト・ジルコン（12月）です。"),
    ("誕生石が2つ以上ある月は、どれを選べばいいですか。",
     "どれも同じ月の誕生石なので、好きなものを選んでかまいません。色の好み、言い伝え、予算、毎日つけるかどうか（硬さ）で選ぶ人が多いです。"),
    ("誕生石と誕生日石は何が違いますか。",
     "誕生石は月ごとに業界団体が定めた石、誕生日石は1日ごとに石を割り当てたものです。誕生日石には公式な決まりがありませんが、多くのサイトやお店で同じ系統の一覧が使われています。このページの誕生日石は、複数の一覧を突き合わせて2つ以上で一致した石です。"),
    ("守護石とは何ですか。誕生日石とどう違いますか。",
     "守護石は、このサイトが独自に選んだ1日ごとの石です。その日の星（太陽がいる星座の区切り＝デーカンの支配星）に対応する石や、その日のラッキーカラーに近い石の中から、実際に販売されている石を選んでいます。一般的な一覧に沿った誕生日石とは別のもので、誕生日ページの運勢やお守りで使っています。"),
    ("海外の誕生石と違うのはなぜですか。",
     "誕生石は国ごとに業界団体が定めていて、アメリカやイギリスのリストとは一部が違います。たとえば日本の3月にはサンゴがあり、5月にはヒスイがあるなど、日本で親しまれてきた石が入っています。"),
    ("誕生石に本当に効果はありますか。",
     "石ごとの意味は、昔からの言い伝えや文化の中で語られてきたものです。科学的に効果が確かめられているわけではありません。お守りや記念として、気持ちを込めて楽しむものと考えてください。"),
    ("誕生日のほかの占いも見られますか。",
     "見られます。誕生日を選んだあとに出る「誕生日のページへ」から、性格、相性の良い誕生日、誕生花、2027年の運勢まで読めます。"),
]


def esc(s):
    return html.escape(str(s), quote=True)


def day_url(k):
    return f"/366uranai/{k[:2]}-{k[2:]}/"


def load():
    stones = {x["name"]: x for x in json.load(open(os.path.join(DATA, "src_stones.json"), encoding="utf-8"))["stones"]}
    mats = json.load(open(os.path.join(DATA, "materials_366.json"), encoding="utf-8"))
    assert sum(len(v) for v in MONTHS.values()) == 29 and len(ADDED_2021) == 10
    for m, names in MONTHS.items():
        for n in names:
            assert n in stones and stones[n]["birth_month"] == [m], n
            assert n in KEY
    for k, v in mats.items():  # 誕生日ページと同じ月の誕生石・誕生日石がカタログにあること
        assert v["birthstone_month"] == "・".join(MONTHS[v["month"]]), k
        assert v["birthday_stone"]["name"] in stones and v["birthday_stone"]["name"] not in MONTHS[v["month"]], k
    return stones, mats


def gem(hexc, size=""):
    """宝石の絵（CSS。ブリリアントカット風の多角形）"""
    return f'<i class="fh-b27-bs-gem{(" " + size) if size else ""}" style="--g:{hexc}" aria-hidden="true"></i>'


CSS = """<style id="fh-b27-bs-css">
.fh-b27[data-fh-page="birthstone"]{--ink:#F1EEF6;--sub:#D6D0E2;--mute:#ABA3BD;--paper:#17141F;--deep:#120F19;--line:#4A4060;--gold:#E9C977;--gem2:#B9A6F0;--cream:#FBF7EF;--cream-ink:#2B2633}
.fh-b27[data-fh-page="birthstone"] a:hover{color:#FFE7A8}
.fh-b27[data-fh-page="birthstone"] .fh-b27-note{border-left:0;border-radius:22px;background-color:var(--paper);
  background-image:radial-gradient(circle at 88% 6%,rgba(185,166,240,.20),transparent 34%),radial-gradient(circle at 6% 36%,rgba(233,201,119,.10),transparent 32%),
  radial-gradient(rgba(255,255,255,.55) .7px,transparent 1.2px),radial-gradient(rgba(255,255,255,.25) .6px,transparent 1px);
  background-size:auto,auto,90px 90px,37px 37px;background-position:0 0,0 0,13px 21px,0 0;box-shadow:0 14px 40px rgba(0,0,0,.5),inset 0 0 0 1px rgba(233,201,119,.18)}
.fh-b27[data-fh-page="birthstone"] .fh-b27-hero{align-items:center}
.fh-b27-bs-emb{position:relative;flex:0 0 120px;height:120px;display:flex;align-items:center;justify-content:center}
.fh-b27-bs-gem{display:inline-block;width:34px;height:30px;flex:0 0 auto;position:relative;
  clip-path:polygon(22% 0,78% 0,100% 32%,50% 100%,0 32%);
  background:linear-gradient(115deg,rgba(255,255,255,.75) 0 14%,transparent 15%),linear-gradient(245deg,rgba(255,255,255,.35) 0 22%,transparent 23%),
  linear-gradient(180deg,transparent 31%,rgba(0,0,0,.18) 32% 33%,transparent 34%),
  conic-gradient(from 200deg at 50% 32%,var(--g),color-mix(in srgb,var(--g) 55%,#fff),var(--g),color-mix(in srgb,var(--g) 60%,#000),var(--g))}
.fh-b27-bs-gem.fh-b27-bs-l{width:96px;height:84px}
.fh-b27-bs-gem.fh-b27-bs-m{width:52px;height:46px}
.fh-b27-bs-emb .fh-b27-bs-gem{animation:fh-b27-bs-float 5s ease-in-out infinite}
.fh-b27-bs-emb::before,.fh-b27-bs-emb::after{content:"";position:absolute;width:10px;height:10px;background:#fff;clip-path:polygon(50% 0,60% 40%,100% 50%,60% 60%,50% 100%,40% 60%,0 50%,40% 40%);animation:fh-b27-bs-tw 2.4s ease-in-out infinite}
.fh-b27-bs-emb::before{left:14px;top:16px}.fh-b27-bs-emb::after{right:10px;bottom:22px;animation-delay:1.2s}
@keyframes fh-b27-bs-float{50%{transform:translateY(-6px) rotate(-3deg)}}
@keyframes fh-b27-bs-tw{0%,100%{opacity:0;transform:scale(.4)}50%{opacity:1;transform:scale(1)}}
.fh-b27[data-fh-page="birthstone"] .fh-b27-tape{transform:none;border-radius:999px;background:linear-gradient(90deg,var(--gold),var(--gem2));color:#17141F}
.fh-b27[data-fh-page="birthstone"] .fh-b27-title{font-family:'Shippori Mincho',serif;font-weight:800;font-size:30px}
.fh-b27[data-fh-page="birthstone"] h2{font-family:'Shippori Mincho',serif;font-weight:800;font-size:24px}
.fh-b27[data-fh-page="birthstone"] h2 .fh-b27-n{border:0;background:linear-gradient(135deg,var(--gold),var(--gem2));color:#17141F;font-weight:800;border-radius:4px;transform:rotate(45deg)}
.fh-b27[data-fh-page="birthstone"] h2 .fh-b27-n span{display:inline-block;transform:rotate(-45deg)}
.fh-b27[data-fh-page="birthstone"] h3{border-bottom:0;background:linear-gradient(90deg,var(--gold),var(--gem2)) left bottom/100% 2px no-repeat}
.fh-b27[data-fh-page="birthstone"] .fh-b27-toc{border-style:solid;border-color:rgba(233,201,119,.25);border-radius:16px}
.fh-b27[data-fh-page="birthstone"] .fh-b27-toc ol{columns:2;column-gap:28px;list-style:none;padding-left:0}
/* 宝石箱 */
.fh-b27-bs-pick{border:1.5px solid rgba(233,201,119,.35);border-radius:18px;background:var(--deep);padding:16px;display:flex;flex-direction:column;gap:14px}
.fh-b27-bs-pick form{display:flex;flex-wrap:wrap;gap:8px;align-items:center}
.fh-b27-bs-pick select{min-height:44px;border-radius:10px;border:1.5px solid var(--line);background:var(--paper);color:var(--ink);font:inherit;padding:0 10px}
.fh-b27-bs-pick button{min-height:44px;border:0;border-radius:999px;background:linear-gradient(90deg,#E9C977,#D7B25A);color:#17141F;font:inherit;font-weight:700;padding:0 18px;cursor:pointer}
.fh-b27-bs-pick button.fh-b27-bs-sub{background:transparent;border:1.5px solid var(--gem2);color:var(--gem2)}
.fh-b27-bs-box{perspective:900px}
.fh-b27-bs-lid{height:30px;border-radius:14px 14px 0 0;background:linear-gradient(180deg,#5B3A6E,#3B2549);box-shadow:inset 0 -3px 0 rgba(233,201,119,.55);transform-origin:50% 0;transition:transform .7s cubic-bezier(.3,1.4,.5,1)}
.fh-b27-bs-box.fh-b27-bs-open .fh-b27-bs-lid{transform:rotateX(-75deg)}
.fh-b27-bs-in{background:radial-gradient(circle at 50% 0,rgba(185,166,240,.25),transparent 60%),linear-gradient(180deg,#2A1E36,#1C1426);border-radius:0 0 16px 16px;padding:18px;border:1px solid rgba(233,201,119,.3);border-top:0}
.fh-b27-bs-date{display:block;text-align:center;font-family:'Shippori Mincho',serif;font-size:20px;color:var(--gold);margin-bottom:10px}
.fh-b27-bs-trio{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:10px}
.fh-b27-bs-slot{background:var(--cream);color:var(--cream-ink);border-radius:14px;padding:12px 10px;text-align:center;display:flex;flex-direction:column;align-items:center;gap:6px;line-height:1.6;
  opacity:0;transform:translateY(14px) scale(.96)}
.fh-b27-bs-open .fh-b27-bs-slot{animation:fh-b27-bs-pop .6s ease forwards}
.fh-b27-bs-open .fh-b27-bs-slot:nth-child(2){animation-delay:.18s}.fh-b27-bs-open .fh-b27-bs-slot:nth-child(3){animation-delay:.36s}
@keyframes fh-b27-bs-pop{to{opacity:1;transform:none}}
.fh-b27-bs-slot small{font-size:12px;color:#7A6F84}
.fh-b27 .fh-b27-bs-slot b{font-family:'Shippori Mincho',serif;font-size:17px;color:var(--cream-ink)}
.fh-b27 .fh-b27-bs-slot p{font-size:12.5px;color:#4A4255;margin:0;text-align:left}
.fh-b27-bs-gems{display:flex;gap:4px;justify-content:center;flex-wrap:wrap;min-height:46px;align-items:center}
.fh-b27-bs-sw{display:inline-block;width:46px;height:46px;border-radius:50%;box-shadow:inset 0 0 0 3px rgba(255,255,255,.6),0 2px 6px rgba(0,0,0,.2)}
.fh-b27-bs-msg{margin-top:14px;background:rgba(255,255,255,.05);border:1px dashed rgba(233,201,119,.4);border-radius:12px;padding:12px 14px;font-size:14.5px;line-height:1.85}
.fh-b27 .fh-b27-bs-msg b{color:var(--gold)}
.fh-b27-bs-acts{display:flex;flex-wrap:wrap;gap:8px;margin-top:12px;align-items:center}
.fh-b27[data-fh-page="birthstone"] a.fh-b27-bs-go,.fh-b27[data-fh-page="birthstone"] a.fh-b27-bs-go:hover{color:#17141F}
.fh-b27 a.fh-b27-bs-go{display:inline-flex;align-items:center;min-height:44px;padding:0 16px;border-radius:999px;background:var(--gold);color:#17141F;font-weight:700;text-decoration:none}
.fh-b27-bs-acts .fh-b27-shopbtn{min-height:44px}
.fh-b27-bs-acts small{font-size:11px;color:var(--mute)}
@media (prefers-reduced-motion:reduce){.fh-b27-bs-emb .fh-b27-bs-gem,.fh-b27-bs-emb::before,.fh-b27-bs-emb::after{animation:none}.fh-b27-bs-slot{opacity:1;transform:none}.fh-b27-bs-open .fh-b27-bs-slot{animation:none}.fh-b27-bs-lid{transition:none}}
/* 早見表・月カード */
.fh-b27-bs-t{width:100%;border-collapse:collapse;font-size:14px;line-height:1.65}
.fh-b27-bs-t caption{position:absolute;left:-9999px}
.fh-b27-bs-t th,.fh-b27-bs-t td{border-bottom:1px dashed var(--line);padding:7px 6px;text-align:left;vertical-align:middle}
.fh-b27-bs-t thead th{color:var(--gold);font-size:12.5px}
.fh-b27-bs-t td.own{color:var(--mute);font-size:13px}.fh-b27-bs-t thead small{font-weight:400;font-size:10.5px}
.fh-b27-bs-t tbody th{white-space:nowrap;font-family:'Shippori Mincho',serif}
.fh-b27-bs-t .fh-b27-bs-gem{width:18px;height:16px;margin-right:3px;vertical-align:-2px}
.fh-b27-bs-months{display:flex;flex-direction:column;gap:14px}
.fh-b27-bs-month{border:1px solid rgba(233,201,119,.22);border-radius:18px;background:var(--deep);padding:14px 16px}
.fh-b27-bs-month h3{display:flex;align-items:center;gap:10px;margin:0 0 6px}
.fh-b27-bs-month>p{font-size:14.5px;color:var(--sub)}
.fh-b27-bs-stones{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:10px;margin-top:8px}
.fh-b27-bs-stone{background:var(--cream);color:var(--cream-ink);border-radius:12px;padding:10px 12px;display:grid;grid-template-columns:52px minmax(0,1fr);gap:10px;align-items:start;line-height:1.65}
.fh-b27 .fh-b27-bs-stone b{font-family:'Shippori Mincho',serif;font-size:16px;color:var(--cream-ink)}
.fh-b27 .fh-b27-bs-stone p{font-size:13px;color:#4A4255;margin:2px 0 0}
.fh-b27-bs-stone small{font-size:11.5px;color:#7A6F84}
.fh-b27-bs-new{display:inline-block;font-size:10.5px;font-weight:700;border-radius:999px;padding:0 7px;margin-left:6px;background:#5B3A6E;color:#FBF7EF;vertical-align:2px}
.fh-b27-bs-kw{display:inline-block;font-size:12px;color:#7B4F12;background:#F6E7C1;border-radius:6px;padding:0 6px;margin-top:3px}
.fh-b27-bs-colors{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:10px}
.fh-b27-bs-colors div{border:1px solid rgba(185,166,240,.25);border-radius:14px;background:var(--deep);padding:10px 14px;font-size:14px;line-height:1.8}
.fh-b27-bs-colors .fh-b27-bs-gem{width:16px;height:14px;vertical-align:-1px;margin-right:2px}
.fh-b27-bs-colors span{white-space:nowrap}
.fh-b27-bs-colors b{font-family:'Shippori Mincho',serif;color:var(--gem2);font-size:16px}
.fh-b27-bs-list{display:flex;flex-direction:column;gap:8px}
.fh-b27-bs-list details{border:1px solid rgba(233,201,119,.22);border-radius:14px;background:var(--deep);padding:6px 12px}
.fh-b27-bs-list summary{cursor:pointer;font-family:'Shippori Mincho',serif;font-weight:700;font-size:16px;color:var(--gold)}
.fh-b27-bs-list summary small{color:var(--mute);font-family:inherit;font-weight:400;font-size:12.5px;margin-left:8px}
.fh-b27-bs-src{border-left:3px solid var(--gold);padding:8px 14px;background:rgba(233,201,119,.06);border-radius:0 10px 10px 0;font-size:14.5px}
.fh-b27-bs-care,.fh-b27-bs-use{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:10px;list-style:none;margin:0;padding:0}
.fh-b27 .fh-b27-bs-care li,.fh-b27 .fh-b27-bs-use li{margin:0;border:1px dashed var(--line);border-radius:12px;padding:10px 14px;font-size:14.5px;line-height:1.8}
.fh-b27-bs-care li::before,.fh-b27-bs-use li::before{content:none}
.fh-b27-bs-care b,.fh-b27-bs-use b{display:block;color:var(--gold);font-family:'Shippori Mincho',serif}
.fh-b27-bs-care em{display:block;font-style:normal;color:var(--gem2);font-size:13px}
.fh-b27-bs-qa details{border-bottom:1px dashed var(--line);padding:8px 2px}
.fh-b27-bs-qa summary{cursor:pointer;font-weight:700}
.fh-b27-bs-qa p{margin-top:6px;font-size:14.5px}
@media (max-width:640px){.fh-b27-bs-t .fh-b27-bs-kwc{display:none}.fh-b27-bs-stones,.fh-b27-bs-colors,.fh-b27-bs-care,.fh-b27-bs-use{grid-template-columns:1fr}.fh-b27-bs-trio{grid-template-columns:1fr}
  .fh-b27[data-fh-page="birthstone"] .fh-b27-toc ol{columns:1}.fh-b27-bs-emb{flex-basis:96px;height:96px}.fh-b27[data-fh-page="birthstone"] .fh-b27-title{font-size:25px}
  .fh-b27-bs-slot{display:grid;grid-template-columns:56px minmax(0,1fr);text-align:left;align-items:center}.fh-b27-bs-slot .fh-b27-bs-gems{grid-row:span 3;justify-content:flex-start}}
</style>"""


def build(sample, updated):
    stones, mats = load()
    H = []
    a = H.append
    a(CSS)
    a('<div class="fh-b27" data-fh-page="birthstone">\n<div class="fh-b27-note">')
    a(f'''<header class="fh-b27-hero">
  <div class="fh-b27-bs-emb" aria-hidden="true">{gem("#9B7BE0", "fh-b27-bs-l")}</div>
  <div class="fh-b27-hero-body">
    <span class="fh-b27-tape">人生予報 誕生石</span>
    <h1 class="fh-b27-title">誕生石一覧<br>1月〜12月の石の意味と色</h1>
    <p class="fh-b27-lead">1月から12月の誕生石29石の意味と色、2021年の改定で増えた石、366日の誕生日石までまとめました。誕生日を選ぶと、あなたの誕生石・誕生日石・誕生色が入った「宝石箱」が開きます。月の誕生石は、全国宝石卸商協同組合の2021年改定のリストに沿っています。</p>
  </div>
</header>''')
    items = [("b27-bs-pick", "あなたの宝石箱を開く"), ("b27-bs-table", "誕生石の早見表（1月〜12月）"), ("b27-bs-months", "月ごとの誕生石と意味"),
             ("b27-bs-2021", "2021年の改定で増えた10石"), ("b27-bs-color", "色から選ぶ誕生石"), ("b27-bs-days", "366日の誕生日石の一覧"),
             ("b27-bs-use", "誕生石の選び方・贈り方"), ("b27-bs-care", "長く使うためのお手入れ"), ("b27-bs-faq", "よくある質問")]
    a('<nav class="fh-b27-toc" aria-label="目次"><strong>このページの内容</strong><ol>' +
      "".join(f'<li><a href="#{i}">{t}</a></li>' for i, t in items) + "</ol></nav>")
    n = [0]

    def h2(t):
        n[0] += 1
        return f'<h2><span class="fh-b27-n"><span>{n[0]}</span></span><span>{t}</span></h2>'

    # 1 宝石箱
    S = {nm: [stones[nm]["color_hex"], KEY.get(nm, ""), stones[nm]["meaning"]] for nm in stones}
    D = {}
    for k, v in mats.items():
        sd = STD[f"{k[:2]}-{k[2:]}"]
        own = v["birthday_stone"]["name"]
        D[k] = [sd["stone"], sd["color"], sd["color_hex"], own, v["birthday_stone"]["note"], stones[own]["color_hex"]]
    shop = {}
    for m in range(1, 13):
        q = f"誕生石 {m}月 ネックレス"
        shop[m] = [aff_extra.href("rakuten", q), aff_extra.href("yahoo", q)]
    imp = "".join(aff_extra.tpl()[s]["impression"] for s in ("rakuten", "yahoo") if s in aff_extra.tpl())
    mo = "".join(f'<option value="{m:02d}">{m}月</option>' for m in range(1, 13))
    do = "".join(f'<option value="{d:02d}">{d}日</option>' for d in range(1, 32))
    a(f'''<section class="fh-b27-sec" id="b27-bs-pick">
  {h2("あなたの宝石箱を開く")}
  <p>誕生日を選んで「宝石箱を開く」を押すと、生まれた月の誕生石、その日の誕生日石、その日の誕生色が出てきます。</p>
  <div class="fh-b27-bs-pick">
    <form id="fh-b27-bs-form" aria-label="誕生日を選ぶ"><select name="m" aria-label="月">{mo}</select><select name="d" aria-label="日">{do}</select><button type="submit">宝石箱を開く</button>
      <button type="button" class="fh-b27-bs-sub" id="fh-b27-bs-today">今日の誕生石</button></form>
    <div class="fh-b27-bs-box" id="fh-b27-bs-box" aria-live="polite">
      <div class="fh-b27-bs-lid"></div>
      <div class="fh-b27-bs-in">
        <span class="fh-b27-bs-date" id="fh-b27-bs-date">誕生日を選んでください</span>
        <div class="fh-b27-bs-trio">
          <div class="fh-b27-bs-slot"><div class="fh-b27-bs-gems" id="fh-b27-bs-mg"></div><small>誕生石（月）</small><b id="fh-b27-bs-mn">―</b></div>
          <div class="fh-b27-bs-slot"><div class="fh-b27-bs-gems" id="fh-b27-bs-dg"></div><small>誕生日石</small><b id="fh-b27-bs-dn">―</b></div>
          <div class="fh-b27-bs-slot"><div class="fh-b27-bs-gems"><i class="fh-b27-bs-sw" id="fh-b27-bs-cs" style="background:#888"></i></div><small>誕生色</small><b id="fh-b27-bs-cn">―</b></div>
        </div>
        <div class="fh-b27-bs-msg" id="fh-b27-bs-msg">誕生石・誕生日石の言い伝えが、ここに出てきます。</div>
        <div class="fh-b27-bs-acts"><a class="fh-b27-bs-go" id="fh-b27-bs-link" href="/366uranai/">誕生日の性格・2027年の運勢へ →</a>
          <span id="fh-b27-bs-shop"></span>{imp}</div>
      </div>
    </div>
  </div>
  <noscript><p class="fh-b27-small">宝石箱を開くにはJavaScriptを有効にしてください。下の早見表と一覧からも探せます。</p></noscript>
</section>''')
    js = ("(function(){var S=" + json.dumps(S, separators=(",", ":")) + ",D=" + json.dumps(D, separators=(",", ":")) +
          ",M=" + json.dumps({str(m): v for m, v in MONTHS.items()}, separators=(",", ":")) +
          ",P=" + json.dumps({str(m): v for m, v in shop.items()}, separators=(",", ":")) + ";"
          "var f=document.getElementById('fh-b27-bs-form');if(!f)return;var Ms=f.querySelector('[name=m]'),Ds=f.querySelector('[name=d]'),"
          "N={1:31,2:29,3:31,4:30,5:31,6:30,7:31,8:31,9:30,10:31,11:30,12:31};function $(i){return document.getElementById(i)}"
          "function g(c,s){var e=document.createElement('i');e.className='fh-b27-bs-gem'+(s?' '+s:'');e.style.setProperty('--g',c);e.setAttribute('aria-hidden','true');return e}"
          "function fit(){var n=N[+Ms.value];for(var i=0;i<Ds.options.length;i++){Ds.options[i].disabled=i>=n;}if(+Ds.value>n)Ds.value=String(n).padStart(2,'0');}"
          "function show(m,d){var k=m+d,x=D[k],ms=M[String(+m)];if(!x)return;var b=$('fh-b27-bs-box');b.classList.remove('fh-b27-bs-open');void b.offsetWidth;"
          "var t=(+m)+'月'+(+d)+'日';$('fh-b27-bs-date').textContent=t+'生まれの宝石箱';"
          "var mg=$('fh-b27-bs-mg');mg.innerHTML='';ms.forEach(function(n){mg.appendChild(g(S[n][0],ms.length>2?'':'fh-b27-bs-m'))});"
          "$('fh-b27-bs-mn').textContent=ms.join('・');var dg=$('fh-b27-bs-dg');dg.innerHTML='';dg.appendChild(g(S[x[0]]?S[x[0]][0]:x[2],'fh-b27-bs-m'));"
          "$('fh-b27-bs-dn').textContent=x[0];$('fh-b27-bs-cs').style.background=x[2];$('fh-b27-bs-cn').textContent=x[1];"
          "var h='';ms.forEach(function(n){h+='<b>'+n+'</b>：'+S[n][2]+'<br>'});h+='<b>'+x[0]+'（誕生日石）</b>：'+t+'の誕生日石として、多くの一覧で紹介されている石です。<br><b>'+x[3]+'（このサイトの守護石）</b>：'+x[4]+'<br><small>※誕生日石・誕生色は、広く使われている一覧に合わせています（公式の決まりはありません）。守護石は、その日の星などからこのサイトが独自に選んだ石です。</small>';$('fh-b27-bs-msg').innerHTML=h;"
          "var l=$('fh-b27-bs-link');l.href='/366uranai/'+m+'-'+d+'/';l.textContent=t+'生まれの性格・2027年の運勢へ →';"
          "var p=P[String(+m)],s='',L=['楽天','Yahoo!'],C=['rakuten','yahoo'];for(var i=0;i<2;i++){if(p[i])s+='<a class=\"fh-b27-shopbtn fh-b27-shop-'+C[i]+'\" href=\"'+p[i]+'\" rel=\"nofollow sponsored\" data-aff=\"'+C[i]+'\">'+(+m)+'月の誕生石を'+L[i]+'で探す</a> '}"
          "if(s)s+='<small>PR（広告）</small>';$('fh-b27-bs-shop').innerHTML=s;"
          "requestAnimationFrame(function(){b.classList.add('fh-b27-bs-open')});}"
          "Ms.addEventListener('change',fit);f.addEventListener('submit',function(e){e.preventDefault();show(Ms.value,Ds.value);});"
          "$('fh-b27-bs-today').addEventListener('click',function(){var n=new Date(),m=String(n.getMonth()+1).padStart(2,'0'),d=String(n.getDate()).padStart(2,'0');Ms.value=m;fit();Ds.value=d;show(m,d);});"
          "})();")
    a(f"<script>{js}</script>")

    # 2 早見表
    rows = ""
    for m in range(1, 13):
        ss = "".join(f'<span style="white-space:nowrap">{gem(stones[x]["color_hex"])}{esc(x)}</span>{"" if i == len(MONTHS[m]) - 1 else "、"}'
                     for i, x in enumerate(MONTHS[m]))
        kw = "／".join(KEY[x] for x in MONTHS[m])
        rows += f'<tr><th scope="row"><a href="#b27-bs-m{m:02d}">{m}月</a></th><td>{ss}</td><td class="fh-b27-bs-kwc">{esc(kw)}</td></tr>'
    a(f'''<section class="fh-b27-sec" id="b27-bs-table">
  {h2("誕生石の早見表（1月〜12月）")}
  <p>月ごとの誕生石と、言い伝えのキーワードです。月の名前を押すと、くわしい説明に進みます。</p>
  <table class="fh-b27-bs-t"><caption>1月〜12月の誕生石</caption><thead><tr><th scope="col">月</th><th scope="col">誕生石</th><th scope="col" class="fh-b27-bs-kwc">キーワード</th></tr></thead><tbody>{rows}</tbody></table>
  <p class="fh-b27-small">全国宝石卸商協同組合が2021年12月に改定したリスト（全29石）です。</p>
</section>''')

    # 3 月ごと
    cards = ""
    for m in range(1, 13):
        st = ""
        for x in MONTHS[m]:
            s = stones[x]
            aka = "・".join(s.get("aka") or [])
            st += (f'<div class="fh-b27-bs-stone">{gem(s["color_hex"], "fh-b27-bs-m")}<div><b>{esc(x)}</b>'
                   f'{"<span class=\"fh-b27-bs-new\">2021年に追加</span>" if x in ADDED_2021 else ""}'
                   f'<br><small>{("別名：" + esc(aka) + "／") if aka else ""}色：{esc("・".join(s["color_family"]))}</small>'
                   f'<p>{esc(s["meaning"])}</p><span class="fh-b27-bs-kw">{esc(KEY[x])}</span></div></div>')
        mg = "".join(gem(stones[x]["color_hex"]) for x in MONTHS[m])
        cards += (f'<div class="fh-b27-bs-month" id="b27-bs-m{m:02d}"><h3>{mg}{m}月の誕生石</h3>'
                  f'<p>{esc(MONTH_TEXT[m])}</p><div class="fh-b27-bs-stones">{st}</div></div>')
    a(f'''<section class="fh-b27-sec" id="b27-bs-months">
  {h2("月ごとの誕生石と意味")}
  <p>それぞれの石の別名・色と、昔から語られてきた言い伝えです。言い伝えは国や時代によって違いがあり、ここではよく知られているものを短くまとめています。</p>
  <div class="fh-b27-bs-months">{cards}</div>
</section>''')

    # 4 2021年
    add = "".join(f'<li><b>{m}月：{esc(x)}</b>{esc(KEY[x])}</li>' for m in range(1, 13) for x in MONTHS[m] if x in ADDED_2021)
    a(f'''<section class="fh-b27-sec" id="b27-bs-2021">
  {h2("2021年の改定で増えた10石")}
  <p>日本の誕生石は、全国宝石卸商協同組合が1958年に定めたものが長く使われてきました。2021年12月、63年ぶりに改定され、10の石が加わって全29石になりました。改定には一般社団法人日本ジュエリー協会と山梨県水晶宝飾協同組合が賛同しています。</p>
  <p>理由は、国内で複数のリストが混ざって使われ、選ぶ人が迷ってしまうため、業界として1つにまとめることでした。新しく加わったのは、比較的新しく見つかった石や、色の選択肢を広げる石です。</p>
  <ul class="fh-b27-bs-use">{add}</ul>
  <div class="fh-b27-bs-src"><b>このページの出典</b><br>月の誕生石は2021年の改定リストに沿い、山梨県の報道資料・新聞報道・辞書の3つで内容が一致することを確かめています。それより前のリストや海外のリストとは、一部が違います。</div>
</section>''')

    # 5 色から
    by = collections.OrderedDict((c, []) for c in COLOR_ORDER)
    for m in range(1, 13):
        for x in MONTHS[m]:
            for c in stones[x]["color_family"]:
                if c in by:
                    by[c].append((m, x))
    cc = ""
    for c, lst in by.items():
        if not lst:
            continue
        cc += (f'<div><b>{esc(c)}</b>　<small>{esc(COLOR_TEXT[c])}</small><br>' +
               "、".join(f'<span>{gem(stones[x]["color_hex"])}{esc(x)}（{m}月）</span>' for m, x in lst) + "</div>")
    a(f'''<section class="fh-b27-sec" id="b27-bs-color">
  {h2("色から選ぶ誕生石")}
  <p>好きな色や、贈る相手に似合う色から誕生石を探すこともできます。1つの石が何色もある場合は、それぞれの色に入れています。</p>
  <div class="fh-b27-bs-colors">{cc}</div>
</section>''')

    # 6 誕生日石366
    det = ""
    for m in range(1, 13):
        rows = ""
        for d in range(1, DAYS[m] + 1):
            k = f"{m:02d}{d:02d}"
            v = mats[k]
            bs = v["birthday_stone"]["name"]
            sd = STD[f"{m:02d}-{d:02d}"]
            rows += (f'<tr><th scope="row"><a href="{day_url(k)}">{m}月{d}日</a></th><td>{esc(sd["stone"])}</td>'
                     f'<td>{gem(sd["color_hex"])}{esc(sd["color"])}</td><td class="own">{esc(bs)}</td></tr>')
        det += (f'<details{" open" if m == 1 else ""}><summary>{m}月の誕生日石<small>{DAYS[m]}日分</small></summary>'
                f'<table class="fh-b27-bs-t"><caption>{m}月の誕生日石と誕生色</caption><thead><tr><th scope="col">誕生日</th><th scope="col">誕生日石</th><th scope="col">誕生色</th><th scope="col">守護石<small>（当サイト）</small></th></tr></thead><tbody>{rows}</tbody></table></details>')
    used = len({v["birthday_stone"]["name"] for v in mats.values()})
    a(f'''<section class="fh-b27-sec" id="b27-bs-days">
  {h2("366日の誕生日石の一覧")}
  <p>誕生日石は、1日ごとに石を割り当てたものです。誕生石と違って公式な決まりはありませんが、もとになった本（斉藤貴子『366日誕生石の本』とされます）から広まった一覧が、多くのサイトやお店で使われています。このページでは、宝石店・メディアなど複数の一覧を突き合わせ、2つ以上で一致した石を載せています。誕生色も同じように、野村順一『誕生色事典』がもととされる一覧に合わせています。</p>
  <p>右の「守護石」は、その日の星（デーカンの支配星）に対応する石などから、このサイトが独自に選んだ石です。誕生日ページの運勢やお守りで使っています。日付を押すと、その誕生日の性格や2027年の運勢のページが開きます。</p>
  <div class="fh-b27-bs-list">{det}</div>
</section>''')

    # 7 選び方
    lis = "".join(f"<li><b>{esc(x)}</b>{esc(y)}</li>" for x, y in USE)
    a(f'''<section class="fh-b27-sec" id="b27-bs-use">
  {h2("誕生石の選び方・贈り方")}
  <ul class="fh-b27-bs-use">{lis}</ul>
</section>''')
    # 8 お手入れ
    lis = "".join(f"<li><b>{esc(x)}</b><em>{esc(y)}</em>{esc(z)}</li>" for x, y, z in CARE)
    a(f'''<section class="fh-b27-sec" id="b27-bs-care">
  {h2("長く使うためのお手入れ")}
  <p>誕生石の中には、硬くて丈夫な石もあれば、水や衝撃に弱い石もあります。毎日身につけるものを選ぶときや、しまうときの参考にしてください。</p>
  <ul class="fh-b27-bs-care">{lis}</ul>
  <p class="fh-b27-small">石の状態や加工によって扱い方は変わります。くわしくは購入したお店に確認してください。</p>
</section>''')
    # 9 FAQ
    qa = "".join(f'<details{" open" if i == 0 else ""}><summary>Q. {q}</summary><p>A. {x}</p></details>' for i, (q, x) in enumerate(FAQ))
    ld = {"@context": "https://schema.org", "@type": "FAQPage",
          "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": x}} for q, x in FAQ]}
    a(f'''<section class="fh-b27-sec" id="b27-bs-faq">
  {h2("よくある質問")}
  <div class="fh-b27-bs-qa">{qa}</div>
</section>
<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>''')
    a('''<section class="fh-b27-sec" id="b27-bs-more">
  <div class="fh-b27-links">
    <a href="/366uranai/"><b>366日の誕生日占い →</b><small>誕生日から性格・相性・2027年の運勢</small></a>
    <a href="/flower/"><b>誕生花一覧 →</b><small>366日の誕生花と花言葉</small></a>
    <a href="/seinengappi/"><b>生年月日まるごと診断 →</b><small>8つの占いを1枚のカードに</small></a>
  </div>
</section>''')
    up = dt.date.fromisoformat(updated)
    a(f'<p class="fh-b27-foot">月の誕生石は全国宝石卸商協同組合の2021年改定のリストによります。誕生日石・誕生色は、広く使われている一覧を複数突き合わせたものです。守護石は当サイト独自の選び方です。石の言い伝えは一般に知られているものを短くまとめたもので、効果を保証するものではありません。<br>'
      f'最終更新日：{up.year}年{up.month}月{up.day}日／<a href="/about/">この記事の作成方針について</a></p>')
    a("</div>\n</div>")
    title = "誕生石一覧｜1月〜12月の誕生石の意味と色・366日の誕生日石【2021年改定・全29石】"
    desc = ("1月〜12月の誕生石29石の意味・色・言い伝えを一覧で紹介。2021年の改定で増えた10石、色から選ぶ誕生石、"
            "366日の誕生日石、選び方とお手入れも。誕生日を選ぶと誕生石・誕生日石・誕生色がわかります。")
    out = shell(title, desc, URL, "\n".join(H), sample)
    assert "動物占い" not in out and "！" not in out
    return out


def main():
    updated = sys.argv[1] if len(sys.argv) > 1 else dt.date.today().isoformat()
    for sample, path in ((False, os.path.join(OUT, "birthstone.html")), (True, os.path.join(OUT, "sample", "birthstone.html"))):
        with open(path, "w", encoding="utf-8") as fp:
            fp.write(build(sample, updated))
        print("→", os.path.relpath(path, WORK))


if __name__ == "__main__":
    main()
