"""生年月日まるごと診断（新しい固定ページ /seinengappi/）を作る。

使い方:
  python work/scripts/build_html.py --sample 0101   # 共通CSS/JS（fh-b27.css・fh-b27.js ほか）を先に作る
  python work/scripts/build_seinengappi.py

出力:
  work/out/seinengappi.html          投入用。<!-- fh-b27:start --> 〜 <!-- fh-b27:end --> の中身（[no_toc] ＋ カスタムHTMLブロック）を
                                     新しい固定ページ（スラッグ seinengappi・親なし）の本文に貼る
  work/out/sample/seinengappi.html   確認用（共通CSS/JSを ../assets/ から読む）
  work/out/assets/fh-b27-sign.js     太陽が星座を移る日時（日本時間）1930〜2030年。各年12個 × "DDhhmm"（1月＝水瓶座入り … 12月＝山羊座入り）。
                                     calc_sekki.py の crossings（太陽の視黄経が30度の倍数を通る時刻）で計算

しくみ:
  生年月日（1930〜2030年＝節入り・旧暦の表の範囲）を選ぶと、共通JS fh-b27.js の計算（FHB27Calc：honmei・pillars・shuku・kin・
  lifePath・animal・sunSign）で、星座・九星・干支・四柱推命・宿曜・マヤ暦・数秘・動物×色を1枚のカードに出す。
  表示の処理も fh-b27.js の bootSeinen（<div class="fh-b27" data-fh-page="seinengappi"> のときだけ動く）。計算をこのページで書き直さない。
  生年月日は送信・保存しない（ページの中だけで計算）。
読み込むJS（この順）: fh-b27-setsuiri.js → fh-b27-kyureki.js → fh-b27-sign.js → fh-b27.js
"""
import datetime as dt, json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from build_hub import OUT, WORK, esc, shell  # noqa: E402
from calc_sekki import crossings  # noqa: E402
from common import jst_from_jd  # noqa: E402

URL = "/seinengappi/"
Y0, Y1 = 1930, 2030
SCRIPTS = ("fh-b27-setsuiri.js", "fh-b27-kyureki.js", "fh-b27-sign.js", "fh-b27.js")
# 黄経（度）→ その星座に入る月（30度＝牡牛座入りは4月 …）
SIGN_MONTH = {300: 1, 330: 2, 0: 3, 30: 4, 60: 5, 90: 6, 120: 7, 150: 8, 180: 9, 210: 10, 240: 11, 270: 12}


def sign_table():
    rows = {}
    for deg, jd in crossings(Y0, Y1, step_deg=30):
        t = jst_from_jd(jd)
        m = SIGN_MONTH[deg]
        assert t.month == m, (deg, t)
        rows.setdefault(t.year, {})[m] = t.strftime("%d%H%M")
    out = []
    for y in range(Y0, Y1 + 1):
        r = rows[y]
        assert sorted(r) == list(range(1, 13)), (y, sorted(r))
        out.append("".join(r[m] for m in range(1, 13)))
    return out


def write_sign_js(rows):
    path = os.path.join(OUT, "assets", "fh-b27-sign.js")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(f"/* 太陽が星座を移る日時（日本時間）{Y0}〜{Y1}年。各年 1月（水瓶座入り）〜12月（山羊座入り）の順に DDhhmm。"
                "生年月日まるごと診断（/seinengappi/）用。出典: 天文計算（work/scripts/calc_sekki.py の crossings、build_seinengappi.py が出力）*/\n")
        f.write("window.FH_B27_SIGN=" + json.dumps({"y0": Y0, "d": rows}, separators=(",", ":")) + ";\n")
    return path


def res_box(key, label, link=None, wide=False):
    a = f'<a id="fh-b27-sg-{key}-a" href="{link[0]}">{esc(link[1])}</a>' if link else ""
    cls = ' class="fh-b27-wide"' if wide else ""
    return (f'    <div{cls}><small>{esc(label)}</small><b id="fh-b27-sg-{key}">—</b>'
            f'<span id="fh-b27-sg-{key}-n"></span>{a}</div>')


CARD_ROWS = [("sign", "星座"), ("star", "九星"), ("eto", "干支"), ("pillars", "四柱推命"), ("nikkan", "日干"),
             ("shuku", "宿曜"), ("kin", "マヤ暦"), ("seal", "紋章・音"), ("lp", "ライフパス"), ("animal", "動物×色")]


def build(sample, updated):
    H = []
    a = H.append
    a('<div class="fh-b27" data-fh-page="seinengappi">\n<div class="fh-b27-note">')
    a('''<header class="fh-b27-hero">
  <div class="fh-b27-kou" aria-hidden="true">生年月日</div>
  <div class="fh-b27-hero-body">
    <span class="fh-b27-tape">人生予報 まるごと診断</span>
    <p class="fh-b27-title">生年月日まるごと診断<br>8つの占いを1枚のカードに</p>
    <p class="fh-b27-lead">生年月日を選ぶだけで、星座・九星・干支・四柱推命・宿曜・マヤ暦・数秘・動物×色の8つの占いの結果を、1枚のカードにまとめて表示します。気になった占いは、それぞれのページでくわしく読めます。</p>
  </div>
</header>''')
    a(f'''<section class="fh-b27-sec" id="b27-input">
  <h2><span class="fh-b27-n">1</span>生年月日を選ぶ</h2>
  <div class="fh-b27-yearbar">
    <div class="fh-b27-sg-form">
      <label class="fh-b27-sg-yl" for="fh-b27-sg-y">生まれた年<select id="fh-b27-sg-y" data-fh-sg="y"></select></label>
      <label for="fh-b27-sg-m">月<select id="fh-b27-sg-m" data-fh-sg="m"></select></label>
      <label for="fh-b27-sg-d">日<select id="fh-b27-sg-d" data-fh-sg="d"></select></label>
      <button type="button" class="fh-b27-btn" id="fh-b27-sg-go">診断する</button>
    </div>
    <p class="fh-b27-small">選べるのは{Y0}〜{Y1}年です。<b>生年月日は送信も保存もしません</b>（このページの中だけで計算します）。生まれた時刻はわからないものとして、正午（日本時間）に生まれたとして計算します。</p>
  </div>
  <noscript><p class="fh-b27-small">この診断はJavaScriptで計算します。ブラウザの設定でJavaScriptを有効にしてください。</p></noscript>
</section>''')
    a('<div class="fh-b27-sg-out" id="fh-b27-sg-out" hidden>')
    a('''<div class="fh-b27-cardwrap fh-b27-sg-cardwrap">
  <div class="fh-b27-card-outer">
    <div class="fh-b27-card fh-b27-sg-card">
      <div class="fh-b27-card-top"><span class="fh-b27-hand">生年月日まるごとカード</span><span>人生予報</span></div>
      <div class="fh-b27-card-name"><span class="fh-b27-d" id="fh-b27-sg-date">—</span></div>
      <span class="fh-b27-sub" id="fh-b27-sg-sub"></span>
      <dl>''')
    for k, lab in CARD_ROWS:
        a(f'        <div><dt>{lab}</dt><dd id="fh-b27-sg-c-{k}">—</dd></div>')
    a('''      </dl>
      <button type="button" class="fh-b27-btn" data-fh-action="save-sg">カードを画像で保存</button>
    </div>
  </div>
</div>''')
    a('''<a class="fh-b27-promo" id="fh-b27-sg-day" href="/366uranai/">
  <small>この誕生日のページへ</small>
  <b id="fh-b27-sg-day-t">誕生日占い（2027年版）</b>
  <span>性格・相性・誕生花と誕生石、2027年の月ごとの運勢とグラフ、バイオリズムまで。</span>
</a>''')
    a('''<section class="fh-b27-sec" id="b27-detail">
  <h2><span class="fh-b27-n">2</span>ひとつずつ、くわしく</h2>
  <div class="fh-b27-res">''')
    a(res_box("sign", "星座（西洋占星術）", ("/366uranai/", "星座のページを見る →")))
    a(res_box("star", "本命星（九星気学）", ("/kaiun/compass/", "本命星の吉方位を8方位の読み方で見る →")))
    a(res_box("eto", "生まれ年の干支"))
    a(res_box("pillars", "四柱推命（年柱・月柱・日柱）"))
    a(res_box("shuku", "宿曜（本命宿）"))
    a(res_box("kin", "マヤ暦（ドリームスペル）"))
    a(res_box("lp", "数秘術（ライフパス）"))
    a('''    <div><small>動物×色占い</small><b id="fh-b27-sg-animal">—</b><span>12の動物×5つの色＝60タイプの、このサイト独自の占いです。</span><a href="/animal-color/">60タイプの性格を見る →</a></div>''')
    a('''    <div class="fh-b27-wide"><small>もっと知りたい人へ</small><span>干支・四柱推命・宿曜・マヤ暦・数秘の意味と、2027年のあなたの運勢は、誕生日のページで生まれ年を選ぶと読めます。</span><a id="fh-b27-sg-day-a" href="/366uranai/">誕生日のページを見る →</a></div>''')
    a('''  </div>
</section>''')
    a('</div>')
    a("<!--Ads1-->")
    a('''<section class="fh-b27-sec" id="b27-more">
  <h2><span class="fh-b27-n">3</span>あわせて占う</h2>
  <div class="fh-b27-links">
    <a href="/366uranai/"><b>366日の誕生日占い</b><small>誕生日から性格と2027年の運勢を見る</small></a>
    <a href="/compatibility/"><b>誕生日相性占い</b><small>2人の生年月日で相性を見る</small></a>
    <a href="/enmusubi/pair/"><b>ご縁の相性診断</b><small>縁結び診断室</small></a>
    <a href="/animal-color/"><b>動物×色占い</b><small>生年月日で60タイプ</small></a>
    <a href="/mbti/"><b>MBTI占い</b><small>性格タイプで見る2027年</small></a>
    <a href="/mbti-compatibility/"><b>MBTI相性占い</b><small>性格タイプどうしの相性</small></a>
    <a href="/kokoro/"><b>心コンパス</b><small>エニアグラム・ビッグファイブで性格を深く知る</small></a>
    <a href="/kaiun/compass/"><b>8方位の読み方</b><small>開運ライフ｜本命星の吉方位に</small></a>
    <a href="/dream/"><b>夢解き図鑑</b><small>気になる夢の意味を調べる</small></a>
  </div>
</section>''')
    a(f'''<section class="fh-b27-about" id="b27-about">
  <h3>この診断について</h3>
  <ul>
    <li><b>計算のしかた：</b>星座・節入り・旧暦は、天文計算で求めた日時（日本時間）をもとにしています。生まれた時刻はわからないので、正午に生まれたとして計算します。</li>
    <li><b>星座：</b>太陽が星座を移る日は年によって違うため、生まれた年の実際の日時で判定します。移る日に生まれた人は、時刻によって隣の星座になることがあります。</li>
    <li><b>九星・干支・四柱推命：</b>九星気学と四柱推命は立春で年が、節入り（立春・啓蟄など）で月が切り替わります。立春より前に生まれた人は前年の星・干支になります。ふだんの干支は1月1日で切り替えて表示しています。</li>
    <li><b>宿曜：</b>旧暦の月日と『宿曜経』の「各月1日の宿」の表から本命宿を出しています。</li>
    <li><b>マヤ暦：</b>ドリームスペル方式（2013年7月26日＝KIN164を基準に、2月29日は数えない）です。古代マヤの暦そのものとは別物です。</li>
    <li><b>数秘術：</b>ライフパスは生年月日の数字をすべて足して1けたにする方式です（11・22・33は残します）。流派によって数が違うことがあります。</li>
    <li><b>動物×色占い：</b>当サイト独自の60タイプです。</li>
    <li><b>選べる年：</b>{Y0}〜{Y1}年（節入りと旧暦の表を用意している範囲）です。生年月日は送信も保存もしません。</li>
  </ul>
</section>''')
    up = dt.date.fromisoformat(updated)
    a(f'<p class="fh-b27-foot">この診断は、西洋占星術・九星気学・干支・四柱推命・宿曜・マヤ暦・数秘術と、当サイト独自の動物×色占いの計算をまとめたものです。占いの結果として、楽しみと気づきのためにお読みください。<br>'
      f'最終更新日：{up.year}年{up.month}月{up.day}日／<a href="/about/">この記事の作成方針について</a></p>')
    a("</div>\n</div>")
    title = "生年月日まるごと診断｜星座・九星・干支・四柱推命・宿曜・マヤ暦・数秘を1枚に"
    desc = ("生年月日を選ぶだけで、星座・九星（本命星）・干支・四柱推命・宿曜・マヤ暦・数秘（ライフパス）・動物×色の8つの占いを"
            "1枚のカードにまとめて表示。画像で保存もできます。生年月日は送信・保存しません。")
    return shell(title, desc, URL, "\n".join(H), sample, SCRIPTS)


def main():
    updated = sys.argv[1] if len(sys.argv) > 1 else dt.date.today().isoformat()
    p = write_sign_js(sign_table())
    print("→", os.path.relpath(p, WORK))
    js = os.path.join(OUT, "assets", "fh-b27.js")
    if not os.path.exists(js) or "bootSeinen" not in open(js, encoding="utf-8").read():
        print("注意: out/assets/fh-b27.js が古い（まるごと診断の処理 bootSeinen が無い）。先に build_html.py を実行してください。")
    for sample, path in ((False, os.path.join(OUT, "seinengappi.html")), (True, os.path.join(OUT, "sample", "seinengappi.html"))):
        with open(path, "w", encoding="utf-8") as f:
            f.write(build(sample, updated))
        print("→", os.path.relpath(path, WORK))


if __name__ == "__main__":
    main()
