"""誕生日相性占い（既存の固定ページ /compatibility/ の本文を作り直す）を作る。

使い方:
  python work/scripts/build_html.py --sample 0101     # 共通CSS/JS（fh-b27.css・fh-b27.js ほか）を先に作る
  python work/scripts/build_compatibility.py [2026-10-11]   # 引数は最終更新日（省略で今日）
  python work/scripts/test_compatibility.py           # JS の計算が build_compat.scores() と一致するかのテスト

出力:
  work/out/compatibility.html          投入用。<!-- fh-b27:start --> 〜 <!-- fh-b27:end --> の中身（[no_toc] ＋ カスタムHTMLブロック）を
                                       既存の固定ページ /compatibility/ の本文と差し替える（差し替え前の本文は本人が控える）
  work/out/sample/compatibility.html   確認用（共通CSS/JSを ../assets/ から読む）
  work/out/assets/fh-b27-compat.js     templates/fh-b27-compat.js に366日の小さな表を埋め込んだもの

しくみ:
  2人の誕生日（月日は必須・生まれ年は任意）を選ぶと、366日の誕生日ページと同じ相性の決め方
  （build_compat.py の scores()：太陽の位置どうしの角度＋誕生日の数のグループ）で、2人の関係の型・5段階の目安・
  場面の文・うまくいくコツを出し、2人それぞれの /366uranai/MM-DD/ に案内する。
  2人とも生まれ年を選んだときだけ、九星気学の本命星どうしの相性（knowledge/04_九星気学.md 3-3 の表）を足す。
  計算と文の組み立ては fh-b27-compat.js（<div class="fh-b27" data-fh-page="compatibility"> のときだけ動く）。
  生年月日は送信・保存しない（ページの中だけで計算）。
埋め込む表（366日・暦の順。2月29日を含む）:
  [太陽の位置×1000（base_366.json の sun_lon と同じ値）, 誕生日の数, 星座の番号（牡羊座=0）, エレメント（火地風水=0〜3）,
   相性の良い誕生日5つの番号, 気をつけたい誕生日3つの番号]（compat_366.json の順）
  ＋ 九星どうしの相性の表（knowledge/04_九星気学.md 3-3 をそのまま読む）
読み込むJS（この順）: fh-b27-setsuiri.js → fh-b27-kyureki.js → fh-b27.js → fh-b27-compat.js
"""
import datetime as dt, json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from build_hub import OUT, WORK, shell  # noqa: E402

DATA = os.path.join(WORK, "data")
TPL = os.path.join(HERE, "templates")
URL = "/compatibility/"
SCRIPTS = ("fh-b27-setsuiri.js", "fh-b27-kyureki.js", "fh-b27.js", "fh-b27-compat.js")
SIGNS = ["牡羊座", "牡牛座", "双子座", "蟹座", "獅子座", "乙女座", "天秤座", "蠍座", "射手座", "山羊座", "水瓶座", "魚座"]
ELEM = "火地風水"


def kyusei_table():
    """knowledge/04_九星気学.md の 3-3（本人＼相手）の表を 9行 × 9文字 で読む"""
    md = open(os.path.join(WORK, "knowledge", "04_九星気学.md"), encoding="utf-8").read()
    sec = md[md.index("### 3-3."):]
    sec = sec[:sec.index("### 3-4.")]
    rows = []
    for line in sec.splitlines():
        m = re.match(r"^\|([一二三四五六七八九][白黒碧緑黄赤紫].星)\|(.*)\|$", line)
        if m:
            cells = m.group(2).split("|")
            assert len(cells) == 9 and all(c in "◎○◇△×" for c in cells), line
            rows.append("".join(cells))
    assert len(rows) == 9, rows
    return rows


def table():
    base = json.load(open(os.path.join(DATA, "base_366.json"), encoding="utf-8"))
    comp = json.load(open(os.path.join(DATA, "compat_366.json"), encoding="utf-8"))
    keys = list(base)
    assert len(keys) == 366 and keys == sorted(keys) and keys[59] == "0229"
    idx = {k: i for i, k in enumerate(keys)}
    rows = []
    for k in keys:
        b = base[k]
        lon = round(b["sun_lon"] * 1000)
        assert abs(lon / 1000 - b["sun_lon"]) < 1e-9, (k, b["sun_lon"])  # 小数3けたまで＝そのまま戻せる
        rows.append([lon, b["birthday_number"], SIGNS.index(b["sign"]), ELEM.index(b["element"]),
                     [idx[g["mmdd"]] for g in comp[k]["good"]], [idx[g["mmdd"]] for g in comp[k]["bad"]]])
    return rows


def write_js():
    src = open(os.path.join(TPL, "fh-b27-compat.js"), encoding="utf-8").read()
    data = {"d": table(), "ky": kyusei_table()}
    js = src.replace("/*@CPDATA@*/", "var CP=" + json.dumps(data, ensure_ascii=False, separators=(",", ":")) + ";")
    assert "/*@CPDATA@*/" in src and "var CP=" in js
    path = os.path.join(OUT, "assets", "fh-b27-compat.js")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    open(path, "w", encoding="utf-8").write(js)
    return path


def person(key, who, icon):
    return f'''    <fieldset class="fh-b27-cp-person fh-b27-cp-person-{key}">
      <legend><i class="fh-b27-ic fh-b27-ic-{icon}" aria-hidden="true"></i>{who}の誕生日</legend>
      <div class="fh-b27-cp-sel">
        <label for="fh-b27-cp-{key}m">月<select id="fh-b27-cp-{key}m" data-fh-cp="{key}m"></select></label>
        <label for="fh-b27-cp-{key}d">日<select id="fh-b27-cp-{key}d" data-fh-cp="{key}d"></select></label>
        <label class="fh-b27-cp-yl" for="fh-b27-cp-{key}y">生まれた年（なくてもOK）<select id="fh-b27-cp-{key}y" data-fh-cp="{key}y"></select></label>
      </div>
    </fieldset>'''


def build(sample, updated):
    H = []
    a = H.append
    a('<div class="fh-b27" data-fh-page="compatibility">\n<div class="fh-b27-note">')
    a('''<header class="fh-b27-hero">
  <div class="fh-b27-kou" aria-hidden="true">相性</div>
  <div class="fh-b27-hero-body">
    <span class="fh-b27-tape">人生予報 誕生日相性占い</span>
    <p class="fh-b27-title">誕生日相性占い<br>2人の誕生日で相性を診断</p>
    <p class="fh-b27-lead">あなたとお相手の誕生日を選ぶだけで、2人がどんな関係になりやすいかと、うまくいくコツがわかります。決め方は<a class="fh-b27-cp-link" href="/366uranai/">366日の誕生日占い</a>の「相性の良い誕生日」と同じ。恋人・友人・職場の人・家族、どんな相手でも占えます。</p>
  </div>
</header>''')
    a(f'''<section class="fh-b27-sec" id="b27-cp-input">
  <h2><span class="fh-b27-n">1</span>2人の誕生日を選ぶ</h2>
  <div class="fh-b27-cp-form">
{person("a", "あなた", "people")}
{person("b", "お相手", "love")}
    <div class="fh-b27-cp-act">
      <button type="button" class="fh-b27-btn fh-b27-cp-go" id="fh-b27-cp-go">相性を診断する →</button>
      <p class="fh-b27-cp-msg" id="fh-b27-cp-msg" role="alert" hidden></p>
    </div>
    <p class="fh-b27-small">月と日だけで占えます。2人とも生まれた年を選ぶと、九星気学の本命星どうしの相性も表示します（選べるのは1930〜2030年）。<b>生年月日は送信も保存もしません</b>（このページの中だけで計算します）。</p>
  </div>
  <noscript><p class="fh-b27-small">この診断はJavaScriptで計算します。ブラウザの設定でJavaScriptを有効にしてください。</p></noscript>
</section>''')
    a('''<section class="fh-b27-sec fh-b27-cp-out" id="b27-cp-result" hidden>
  <h2><span class="fh-b27-n">2</span>2人の相性</h2>
  <div class="fh-b27-cp-paper">
    <div class="fh-b27-cp-top"><span class="fh-b27-hand">2人の相性メモ</span><span>人生予報</span></div>
    <p class="fh-b27-cp-pair" id="fh-b27-cp-pair">—</p>
    <p class="fh-b27-cp-type"><i class="fh-b27-ic fh-b27-ic-compat" aria-hidden="true"></i><span id="fh-b27-cp-type">—</span></p>
    <div class="fh-b27-cp-meter" id="fh-b27-cp-meter">
      <span class="fh-b27-cp-mk" id="fh-b27-cp-mk">—</span>
      <span class="fh-b27-cp-mcol"><small>息の合いやすさ（5段階）</small><span class="fh-b27-cp-lv" id="fh-b27-cp-lv">—</span>
      <span class="fh-b27-cp-bar" id="fh-b27-cp-bar" aria-hidden="true"><i></i><i></i><i></i><i></i><i></i></span></span>
    </div>
    <p class="fh-b27-cp-lead" id="fh-b27-cp-lead">—</p>
    <dl class="fh-b27-cp-rows">
      <div><dt>誕生日の数</dt><dd id="fh-b27-cp-num">—</dd></div>
      <div><dt>星座の性質</dt><dd id="fh-b27-cp-elem">—</dd></div>
    </dl>
    <p class="fh-b27-cp-list" id="fh-b27-cp-list">—</p>
  </div>
  <div class="fh-b27-cp-tips">
    <h3><i class="fh-b27-ic fh-b27-ic-kokoro" aria-hidden="true"></i>うまくいくコツ</h3>
    <ul id="fh-b27-cp-tips"></ul>
  </div>
  <div class="fh-b27-cp-who" id="fh-b27-cp-who"></div>
  <div class="fh-b27-cp-kyusei" id="fh-b27-cp-kyusei"></div>
  <div class="fh-b27-cp-days">
    <a class="fh-b27-cp-day" id="fh-b27-cp-da" href="/366uranai/"><small>あなたの誕生日のページ</small><b id="fh-b27-cp-dat">誕生日占い →</b><span>性格・相性の良い誕生日・2027年の運勢</span></a>
    <a class="fh-b27-cp-day" id="fh-b27-cp-db" href="/366uranai/"><small>お相手の誕生日のページ</small><b id="fh-b27-cp-dbt">誕生日占い →</b><span>性格・相性の良い誕生日・2027年の運勢</span></a>
  </div>
  <div class="fh-b27-cp-btns">
    <button type="button" class="fh-b27-btn fh-b27-ghost" id="fh-b27-cp-swap">あなたとお相手を入れ替える</button>
    <button type="button" class="fh-b27-btn fh-b27-ghost" id="fh-b27-cp-again">誕生日を選び直す</button>
  </div>
</section>''')
    a("<!--Ads1-->")
    a('''<section class="fh-b27-sec" id="b27-cp-how">
  <h2><span class="fh-b27-n">3</span>相性の決め方</h2>
  <p>この診断は、2つの占いを重ねて2人の関係を読みます。<a class="fh-b27-cp-link" href="/366uranai/">366日の誕生日占い</a>の各ページにある「相性の良い誕生日」「気をつけたい誕生日」と同じ決め方なので、2人のページを読み比べるとさらに楽しめます。</p>
  <div class="fh-b27-cp-how">
    <div class="fh-b27-sticky fh-b27-y">
      <strong><i class="fh-b27-ic fh-b27-ic-compass" aria-hidden="true"></i>太陽の位置どうし</strong>
      <span>生まれた日に太陽が星座のどのあたりにいたかを比べます。<b>自然に調和しやすい位置</b>か、<b>刺激し合う位置</b>かで、関係の型が決まります。</span>
    </div>
    <div class="fh-b27-sticky fh-b27-b">
      <strong><i class="fh-b27-ic fh-b27-ic-card" aria-hidden="true"></i>誕生日の数のグループ</strong>
      <span>生まれた日の数字を1けたにした数を、<b>行動派</b>（1・5・7）、<b>堅実派</b>（2・4・8）、<b>表現派</b>（3・6・9）に分けて、組み合わせを見ます。</span>
    </div>
    <div class="fh-b27-sticky fh-b27-cp-c">
      <strong><i class="fh-b27-ic fh-b27-ic-calendar-next" aria-hidden="true"></i>生まれ年（なくてもOK）</strong>
      <span>2人とも生まれた年がわかると、<b>九星気学の本命星</b>どうしの相性も加わります。立春より前に生まれた人は前の年の星になります。</span>
    </div>
  </div>
</section>''')
    a('''<section class="fh-b27-sec" id="b27-cp-more">
  <h2><span class="fh-b27-n">4</span>あわせて占う</h2>
  <div class="fh-b27-links">
    <a href="/366uranai/"><b>366日の誕生日占い →</b><small>誕生日から性格と2027年の運勢を見る</small></a>
    <a href="/seinengappi/"><b>生年月日まるごと診断 →</b><small>8つの占いを1枚のカードに</small></a>
    <a href="/enmusubi/pair/"><b>ご縁の相性診断 →</b><small>縁結び診断室</small></a>
    <a href="/mbti-compatibility/"><b>MBTI相性占い →</b><small>性格タイプどうしの相性</small></a>
    <a href="/animal-color/"><b>動物×色占い →</b><small>生年月日で60タイプ</small></a>
  </div>
</section>''')
    a('''<section class="fh-b27-about" id="b27-cp-about">
  <h3>この診断について</h3>
  <ul>
    <li><b>決め方：</b>366日の誕生日占いの「相性の良い誕生日」と同じ規則です。2人の生まれた日の太陽の位置がつくる角度が120度前後（前後8度まで）なら「調和」、60度前後（6度まで）なら「協力」、0度前後（8度まで）なら「似た者どうし」、90度前後（8度まで）なら「刺激し合う」、180度前後（8度まで）なら「向かい合う」、どれにも当たらなければ「おだやか」とします。</li>
    <li><b>点数と5段階：</b>角度がぴったりに近いほど点が高く、誕生日の数のグループ（行動派1・5・7／堅実派2・4・8／表現派3・6・9。11は2、22は4として扱う）が同じなら良い相性の点を、行動派と堅実派の組み合わせならぶつかりやすさの点を足します。良い相性の点が1.0以上で◎、それより低ければ○、角度の関係がなければ◇、ぶつかりやすさの点が0.9未満で△、0.9以上で▽です。</li>
    <li><b>誕生日ページの相性リスト：</b>各ページの「相性の良い誕生日」5つと「気をつけたい誕生日」3つは、366日の中から点の高い組を「お互いに」選んだものです。リストに入らなくても相性が悪いという意味ではありません。どうしても5つ（3つ）に届かない日だけ角度の幅を4度ずつ広げて選んでいるため、その組は広げた幅で関係の型を表示します。</li>
    <li><b>太陽の位置：</b>各誕生日の太陽の位置は、1930〜2027年のその日の正午（日本時間）の平均です。生まれた年によって1度ほど前後しますが、誕生日ページと結果をそろえるため、生まれ年を選んでも同じ値を使います。</li>
    <li><b>九星の相性：</b>本命星は立春で年が切り替わる、日本で一般的な決まりで計算し、相性は九星の五行（木・火・土・金・水）が生み合う・抑え合う関係で見ます。</li>
    <li><b>生年月日は送信も保存もしません。</b>結果は占いとして、2人の関係を考えるきっかけにお使いください。</li>
  </ul>
</section>''')
    up = dt.date.fromisoformat(updated)
    a(f'<p class="fh-b27-foot">この診断は、西洋占星術（太陽の位置）と数秘術（誕生日の数）、生まれ年があるときは九星気学を組み合わせた、当サイトの決め方によるものです。楽しみと気づきのためにお読みください。<br>'
      f'最終更新日：{up.year}年{up.month}月{up.day}日／<a href="/about/">この記事の作成方針について</a></p>')
    a("</div>\n</div>")
    title = "誕生日相性占い｜2人の誕生日で相性を診断【2027年版】"
    desc = ("2人の誕生日を選ぶだけで相性を診断。366日の誕生日占いと同じ決め方（太陽の位置と誕生日の数のグループ）で、"
            "2人の関係の型とうまくいくコツを表示します。生まれ年を入れると九星の相性も。生年月日は送信・保存しません。")
    out = shell(title, desc, URL, "\n".join(H), sample, SCRIPTS)
    assert "\\" not in out and "動物占い" not in out and "六星" not in out and out.count("！") <= 1
    return out


def main():
    updated = sys.argv[1] if len(sys.argv) > 1 else dt.date.today().isoformat()
    p = write_js()
    print("→", os.path.relpath(p, WORK), os.path.getsize(p), "bytes")
    if not os.path.exists(os.path.join(OUT, "assets", "fh-b27.js")):
        print("注意: out/assets/fh-b27.js が無い。先に build_html.py を実行してください。")
    for sample, path in ((False, os.path.join(OUT, "compatibility.html")),
                         (True, os.path.join(OUT, "sample", "compatibility.html"))):
        with open(path, "w", encoding="utf-8") as f:
            f.write(build(sample, updated))
        print("→", os.path.relpath(path, WORK))


if __name__ == "__main__":
    main()
